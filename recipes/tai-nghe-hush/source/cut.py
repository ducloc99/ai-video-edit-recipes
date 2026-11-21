# cut.py: the product cut out of h10.mp4 frame by frame (rembg isnet), written as an alpha webm for text-behind-object.
import subprocess, numpy as np
from PIL import Image
from rembg import remove, new_session
s = new_session("isnet-general-use"); W, H = 1080, 1920
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "assets/h10.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "5M", "-auto-alt-ref", "0", "assets/h10-cut.webm"], stdin=subprocess.PIPE)
prev = None
for i, f in enumerate(fr):
    m = np.array(remove(Image.fromarray(f).resize((540, 960)), session=s, only_mask=True).resize((W, H), Image.BILINEAR)).astype(np.float32)
    if prev is not None: m = 0.6 * m + 0.4 * prev
    prev = m
    enc.stdin.write(np.dstack([f, np.clip(m, 0, 255).astype(np.uint8)]).tobytes())
enc.stdin.close(); enc.wait(); print("ok", len(fr))
