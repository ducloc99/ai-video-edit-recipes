# frames.py: a contact sheet of a video (one frame every N seconds) so you can LOOK at what you made.
#   python frames.py <video.mp4> <sheet.jpg> [everySeconds=2]
import sys, subprocess, math
v, out = sys.argv[1], sys.argv[2]
every = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v]))
n = max(1, int(dur / every)); cols = min(8, n); rows = math.ceil(n / cols)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", f"fps=1/{every},scale=320:-2,tile={cols}x{rows}", "-frames:v", "1", out], check=True)
print(out, f"{n} frames, every {every}s")
