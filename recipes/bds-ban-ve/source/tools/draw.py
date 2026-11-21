# draw.py: turn one real frame into an architect's drawing that draws itself, then washes into colour.
# usage: python draw.py <video> <time> <out.mp4> <draw_s> <wash_s> <hold_s>
# Output 1920x1080 30 fps: paper + blue construction lines -> graphite lines drawn in a sweep -> a clean diagonal
# watercolour wash that ends on the exact real frame, so the real clip can take over without a jump.
# Architecture (long straight edges) is inked strongly; busy texture such as leaves is kept faint.
import sys, subprocess, numpy as np, cv2
src, t, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
DRAW, WASH, HOLD = map(float, sys.argv[4:7]); FPS, W, H = 30, 1920, 1080
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
real = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
u8 = (real * 255).astype(np.uint8)
sm = u8
for _ in range(3): sm = cv2.bilateralFilter(sm, 9, 40, 9)           # flatten textures, keep edges
g = cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
# soft pencil lines (difference of Gaussians on the flattened image)
d = cv2.GaussianBlur(g, (0, 0), 1.1) - cv2.GaussianBlur(g, (0, 0), 2.2)
soft = np.clip(-d * 22, 0, 1)
# texture density: where edges are dense (foliage, stone), keep lines faint
e_full = cv2.Canny(cv2.cvtColor(u8, cv2.COLOR_BGR2GRAY), 50, 140).astype(np.float32) / 255
dens = cv2.blur(e_full, (31, 31))
calm = np.clip(1.0 - (dens - 0.06) * 6, 0.18, 1.0)
# architecture: long straight segments inked crisp and dark
e = cv2.Canny(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY), 40, 120)
hl = cv2.HoughLinesP(e, 1, np.pi / 180, 70, minLineLength=90, maxLineGap=8)
arch = np.zeros((H, W), np.float32); cons = np.zeros((H, W), np.float32)
if hl is not None:
    segs = hl.reshape(-1, 4)
    for x1, y1, x2, y2 in segs[:400]:
        cv2.line(arch, (int(x1), int(y1)), (int(x2), int(y2)), 1.0, 2, cv2.LINE_AA)
    longest = sorted(segs, key=lambda s: -((s[2] - s[0]) ** 2 + (s[3] - s[1]) ** 2))[:28]
    for x1, y1, x2, y2 in longest:                                    # construction lines run past the edges
        dx, dy = x2 - x1, y2 - y1; ex = 0.6
        cv2.line(cons, (int(x1 - dx * ex), int(y1 - dy * ex)), (int(x2 + dx * ex), int(y2 + dy * ex)), 1.0, 1, cv2.LINE_AA)
lines = np.clip(np.maximum(arch * 0.95, soft * calm * 0.85), 0, 1)
lines = cv2.GaussianBlur(lines, (0, 0), 0.5)
# drawing order: left-to-right sweep broken up by smooth noise
rng = np.random.default_rng(7)
noise = cv2.GaussianBlur(rng.random((H // 8, W // 8)).astype(np.float32), (0, 0), 3)
noise = cv2.resize((noise - noise.min()) / (np.ptp(noise) + 1e-6), (W, H))
xs = np.arange(W)[None, :] / W; ys = np.arange(H)[:, None] / H
order = 0.7 * xs + 0.3 * noise
diag = (0.75 * xs + 0.25 * ys)                                        # the wash travels as a clean diagonal
paper = np.ones((H, W, 3), np.float32) * np.array([0.918, 0.945, 0.957], np.float32)   # warm paper (BGR)
grid = np.zeros((H, W), np.float32); grid[::48, :] = 1; grid[:, ::48] = 1
paper -= grid[..., None] * 0.03
ink = np.array([0.15, 0.15, 0.17], np.float32); blue = np.array([0.74, 0.56, 0.36], np.float32)   # BGR
gray = cv2.cvtColor(real, cv2.COLOR_BGR2GRAY)[..., None]
tint = paper * 0.35 + (gray + (real - gray) * 0.55) * 0.65             # watercolour tint on paper
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p", "-g", "15", out], stdin=subprocess.PIPE)
N = int(round((DRAW + WASH + HOLD) * FPS))
ease = lambda x: x * x * (3 - 2 * x)
for i in range(N):
    tt = i / FPS
    pc = np.clip(tt / (DRAW * 0.4), 0, 1)
    pl = ease(np.clip((tt - DRAW * 0.12) / (DRAW * 0.88), 0, 1))
    m_cons = cons * np.clip((pc * 1.1 - order) * 10, 0, 1) * 0.5
    m_ink = lines * np.clip((pl * 1.1 - order) * 12, 0, 1)
    img = paper * (1 - m_cons[..., None]) + blue * m_cons[..., None]
    img = img * (1 - m_ink[..., None]) + ink * m_ink[..., None]
    w = np.clip((tt - DRAW) / max(WASH, 1e-3), 0, 1)
    if w > 0:
        a = np.clip((ease(w) * 1.35 - diag) * 6, 0, 1)[..., None]      # tint arrives first
        b = np.clip((ease(w) * 1.35 - 0.3 - diag) * 6, 0, 1)[..., None]  # real colour follows behind it
        layer = tint * (1 - m_ink[..., None] * 0.6) + ink * m_ink[..., None] * 0.6
        img = img * (1 - a) + layer * a
        img = img * (1 - b) + real * b
    if tt >= DRAW + WASH: img = real
    enc.stdin.write((np.clip(img, 0, 1) * 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print("ok", out, N, "frames")
