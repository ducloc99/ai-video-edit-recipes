# cutout.py: cut a person or product out of a clip, frame by frame, into a transparent webm (for text behind the subject).
#   python cutout.py <in.mp4> <out.webm> [--model isnet-general-use | u2net_human_seg]
# Needs: pip install rembg onnxruntime pillow numpy. Use u2net_human_seg for people, isnet-general-use for products.
import argparse, subprocess, json
import numpy as np
from PIL import Image
from rembg import remove, new_session
a = argparse.ArgumentParser(); a.add_argument("inp"); a.add_argument("out"); a.add_argument("--model", default="isnet-general-use")
o = a.parse_args()
pr = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "json", o.inp]))["streams"][0]
W, H = pr["width"], pr["height"]
s = new_session(o.model)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", o.inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "5M", "-auto-alt-ref", "0", o.out], stdin=subprocess.PIPE)
prev = None
for f in fr:
    small = Image.fromarray(f).resize((W // 2, H // 2))
    m = np.array(remove(small, session=s, only_mask=True).resize((W, H), Image.BILINEAR)).astype(np.float32)
    if prev is not None: m = 0.6 * m + 0.4 * prev   # smooth the edge from frame to frame
    prev = m
    enc.stdin.write(np.dstack([f, np.clip(m, 0, 255).astype(np.uint8)]).tobytes())
enc.stdin.close(); enc.wait()
print(o.out, len(fr), "frames")
