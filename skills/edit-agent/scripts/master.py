# master.py: final delivery. Loudness to -14 LUFS (video copied), a poster frame, and a one-line spec.
#   python master.py <rendered.mp4> <final.mp4> [posterSecond]
import sys, subprocess, re, os
inp, out = sys.argv[1], sys.argv[2]
poster_at = sys.argv[3] if len(sys.argv) > 3 else "1"
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
ff = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
ff("-i", inp, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out)
poster = out[:-4] + ".jpg"
ff("-ss", poster_at, "-i", out, "-frames:v", "1", "-vf", "scale=960:-2", "-q:v", "3", poster)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
wh = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", out]).decode().strip()
r = subprocess.run(["ffmpeg", "-nostats", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
lufs = (re.findall(r"I:\s+(-?[\d.]+) LUFS", r) or ["?"])[-1]
print(f"{out}  |  {dur:.1f}s  |  {wh}  |  {lufs} LUFS  |  {os.path.getsize(out) / 1e6:.1f} MB  |  poster {poster}")
