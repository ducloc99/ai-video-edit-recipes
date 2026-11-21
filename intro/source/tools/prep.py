# prep.py: cut a short SDR proxy of each gallery video for the promo (no audio, keyframe every 0.5 s so seeks are exact)
import subprocess, os, sys
V = "D:/Test/edit-video/thu-vien/v"
# key: (start second, length)
C = {"bds-ban-ve": (3, 9), "bds-dung-3d": (4, 9), "bds-tour-map": (3, 9), "bds-vi-tri": (1, 8), "bds-noi-that": (1, 8),
     "nuoc-hoa-noir": (2, 8), "gimbal-axis": (2, 8), "tai-nghe-hush": (1, 10), "tennis-ace": (3, 8), "drone-skyline": (3, 8),
     "xe-vanta": (3, 9), "dong-ho-3d": (8, 8), "gd-vu-tru": (5, 8), "gd-hoat-hinh": (4, 8), "gd-thuc-te": (3, 8),
     "viet-chu-han": (2, 8), "ve-phan-bang-den": (6, 8), "tu-long-gen-z": (4, 8), "cap-phu-de": (1, 8), "nhip-bong-ro": (6, 8),
     "tin-indonesia": (8, 8), "alaska": (6, 8), "voxel": (1, 8), "pixel-art": (1, 8), "noi-sang-hon": (8, 8),
     "3d-phong": (8, 8), "3d-dao": (7, 8), "3d-hinh-khoi": (2, 8), "code-hat": (3, 8), "code-chu": (1, 8),
     "tu-vung-anh": (3, 8), "hoat-hinh-phu-de": (3, 8), "ca-phe-hay-tra": (4, 8)}
for k, (s, n) in C.items():
    src = f"{V}/{k}.mp4"; out = f"assets/c/{k}.mp4"
    if os.path.exists(out) and len(sys.argv) < 2: continue
    w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", src]).decode().strip().split(",")[:2])
    sc = "scale=1920:1080" if w > h else "scale=608:1080"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-t", str(n), "-i", src, "-an", "-vf",
                    f"{sc},fps=30,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv",
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-g", "15", "-movflags", "+faststart", out], check=True)
    print(k)
