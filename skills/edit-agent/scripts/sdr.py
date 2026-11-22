# sdr.py: make footage safe for HyperFrames: SDR bt709, 30 fps, sized and cropped to the frame, no audio, a keyframe every 0.5 s.
# Phone and stock clips are often HDR; HyperFrames then drops overlays silently, so always run footage through this first.
#   python sdr.py <in.mp4> <out.mp4> [--w 1080 --h 1920] [--ss 0 --t 0]
import argparse, subprocess
a = argparse.ArgumentParser()
a.add_argument("inp"); a.add_argument("out")
a.add_argument("--w", type=int, default=1080); a.add_argument("--h", type=int, default=1920)
a.add_argument("--ss", type=float, default=0); a.add_argument("--t", type=float, default=0)
o = a.parse_args()
vf = (f"scale={o.w}:{o.h}:force_original_aspect_ratio=increase,crop={o.w}:{o.h},fps=30,format=yuv420p,"
      "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
cmd = ["ffmpeg", "-v", "error", "-y"] + (["-ss", str(o.ss)] if o.ss else []) + (["-t", str(o.t)] if o.t else []) + \
      ["-i", o.inp, "-an", "-vf", vf, "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-g", "15", "-movflags", "+faststart", o.out]
subprocess.run(cmd, check=True)
print(o.out)
