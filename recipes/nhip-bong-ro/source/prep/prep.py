"""Prepare footage for nhip-bong-ro: SDR bt709 1080x1920 30fps shots, baked speed ramps,
freeze still + player cutout + white outline, and the music cut.
Run: python prep/prep.py  (from the project folder)"""
import json, subprocess, os, sys
import numpy as np, cv2

SRC = "D:/Test/huong-dan-edit-video-ai/video-tho-the-thao/bong-ro-khoi"
MUSIC = "D:/Test/videos/06-vanta/assets/music-d.mp3"  # earlier Suno take, dark trap/trailer 143.6 bpm
MUSIC_IN = 31.788   # a downbeat; window runs to the track's final hit and tail
DUR = 16.6
A = "assets"
FILES = {n: f"{SRC}/{f}" for n, f in [(f[:2], f) for f in os.listdir(SRC)]}
SDR = "format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
ENC = ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
       "-movflags", "+faststart", "-an"]

def fit(cx):
    # cx=None: portrait source -> fill width; else landscape -> fill height and crop around cx (0..1)
    if cx is None:
        return "scale=1080:-2:flags=lanczos,crop=1080:1920:0:(ih-1920)/2"
    return f"scale=-2:1920:flags=lanczos,crop=1080:1920:'min(max(iw*{cx}-540,0),iw-1080)':0"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:]); sys.exit(1)

# id, clip, src start, timeline in, timeline out, rate, crop centre (None = portrait)
SHOTS = [
    ("s01", "02", 12.0, 0.000, 0.826, 1.0, None),
    ("s02", "07", 0.2, 0.826, 1.685, 1.0, 0.42),
    ("s03", "08", 4.0, 1.685, 2.115, 1.2, None),
    ("s05", "01", 9.0, 2.962, 3.810, 1.0, 0.50),
    ("s06", "06", 5.0, 3.810, 4.251, 1.2, 0.62),
    ("s07", "13", 0.25, 4.251, 5.110, 1.0, None),
    ("s08", "10", 4.0, 5.110, 6.399, 1.0, None),
    ("s09", "09", 0.5, 6.399, 7.258, 1.0, 0.50),
    ("s10", "03", 3.0, 7.258, 9.000, 1.0, None),
    ("s14", "02", 1.0, 11.111, 11.761, 1.2, None),
    ("s15", "11", 3.0, 11.761, 12.399, 1.2, 0.50),
    ("s16", "08", 9.5, 12.399, 13.038, 1.2, None),
    ("s17", "14", 10.5, 13.038, 14.293, 1.0, 0.60),
]

def plain(sid, clip, ss, t0, t1, rate, cx):
    need = (t1 - t0) * rate + 0.25
    vf = f"{fit(cx)},setpts=PTS/{rate},fps=30,{SDR}"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{need:.3f}", "-i", FILES[clip],
         "-vf", vf, *ENC, f"{A}/{sid}.mp4"])

def dense(clip, ss, span, cx, fps=100):
    """Motion-interpolated frames of a source span, returned as an array list at `fps`."""
    tmp = f"prep/_dense_{clip}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{span:.3f}", "-i", FILES[clip],
         "-vf", f"{fit(cx)},minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
         "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-an", tmp])
    cap = cv2.VideoCapture(tmp); frames = []
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(f)
    return frames

def write(frames, out):
    h, w = frames[0].shape[:2]
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                          "-r", "30", "-i", "-", "-vf", SDR, *ENC, out], stdin=subprocess.PIPE)
    for f in frames: p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

def ramp(out, frames, fps, src0, mapping, dur):
    n = int(round(dur * 30)) + 3
    picked = []
    for i in range(n):
        s = mapping(min(i / 30, dur) / dur) - src0
        picked.append(frames[min(len(frames) - 1, max(0, int(round(s * fps))))])
    write(picked, out)

if __name__ == "__main__":
    os.makedirs(A, exist_ok=True)
    for s in SHOTS:
        if not os.path.exists(f"{A}/{s[0]}.mp4"): plain(*s)
        print("ok", s[0])

    # s04: clip 12, slow-mo 0.3x for 60% then snap to 2.2x into the hit at 2.962
    d4 = 2.962 - 2.115; a, k = 1.5, 0.6
    f12 = dense("12", a, 1.0, None)
    def m4(u):
        t = u * d4; t1 = k * d4
        return a + (0.3 * t if t <= t1 else 0.3 * t1 + 2.2 * (t - t1))
    ramp(f"{A}/s04.mp4", f12, 100, a, m4, d4); print("ok s04")

    # s11: clip 05, decelerate into the spin on the finger, stop at 3.70 (the freeze)
    d11 = 10.043 - 9.0; a5, peak = 3.15, 3.70
    f05 = dense("05", a5, 1.95, None)
    ramp(f"{A}/s11.mp4", f05, 100, a5, lambda u: a5 + (peak - a5) * (1 - (1 - u) ** 2), d11); print("ok s11")
    # s13: snap out of the freeze at 1.8x
    d13 = 11.111 - 10.461
    ramp(f"{A}/s13.mp4", f05, 100, a5, lambda u: peak + 1.8 * d13 * u, d13); print("ok s13")

    # freeze still at the peak, player cutout and outline ring
    still = f05[int(round((peak - a5) * 100))]
    from rembg import remove
    from PIL import Image
    rgba = np.array(remove(Image.fromarray(cv2.cvtColor(still, cv2.COLOR_BGR2RGB))))
    m = (rgba[:, :, 3] > 128).astype(np.uint8) * 255
    n_, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = [i for i in range(1, n_) if st[i, cv2.CC_STAT_AREA] > 4000]
    m = np.isin(lab, keep).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cv2.imwrite(f"{A}/freeze.png", still)
    dim = (still.astype(np.float32) * 0.42).astype(np.uint8)
    cv2.imwrite(f"{A}/freeze-dim.png", dim)
    cut = np.dstack([still, cv2.GaussianBlur(m, (3, 3), 0)])
    cv2.imwrite(f"{A}/freeze-cut.png", cut)
    outer = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    inner = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    ring = cv2.GaussianBlur(cv2.subtract(outer, inner), (3, 3), 0)
    white = np.full_like(still, 255)
    cv2.imwrite(f"{A}/outline.png", np.dstack([white, ring]))
    ys, xs = np.where(m > 0)
    json.dump({"bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]}, open("prep/freeze.json", "w"))
    print("ok freeze", xs.min(), ys.min(), xs.max(), ys.max())

    # music: the track's last phrase, ending on its final hit and tail
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(MUSIC_IN), "-t", str(DUR), "-i", MUSIC,
         "-af", f"afade=t=in:st=0:d=0.01,afade=t=out:st={DUR-1.0}:d=1.0", "-ar", "48000", "-b:a", "256k", f"{A}/bgm.mp3"])
    for f in os.listdir("prep"):
        if f.startswith("_dense"): os.remove(f"prep/{f}")
    print("done")
