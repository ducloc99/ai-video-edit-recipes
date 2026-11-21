# build.py: builds the gallery from recipes.json.
# - copies each finished video into videos/ (not committed; upload them as a GitHub Release, see README)
# - makes a poster in gallery/posters/
# - copies the editable source of each project into recipes/<id>/ (big media left out, listed in MEDIA.md)
# - writes recipes/<id>/README.md and gallery/data.js
# Local paths below are the author's machine; edit SRC to point at your own renders.
import os, sys, json, shutil, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
E1 = "D:/Test/Edit-video-1"; PC = f"{E1}/phong-cach/v"; K = f"{E1}/videos/kho"; RD = f"{E1}/renders"
# id: (finished video, project folder or None)
SRC = {
 "bds-ban-ve": (f"{K}/bds-ban-ve/deliverables/ban-ve-thanh-nha-that.mp4", f"{K}/bds-ban-ve"),
 "bds-dung-3d": (f"{K}/bds-dung-3d/deliverables/ban-do-dung-3d-thanh-nha-that.mp4", f"{K}/bds-dung-3d"),
 "bds-tour-map": (f"{K}/bds-tour-map/deliverables/tour-map.mp4", f"{K}/bds-tour-map"),
 "bds-vi-tri": (f"{K}/bds-vi-tri/deliverables/vi-tri.mp4", f"{K}/bds-vi-tri"),
 "bds-noi-that": (f"{K}/bds-noi-that/deliverables/noi-that.mp4", f"{K}/bds-noi-that"),
 "nuoc-hoa-noir": (f"{K}/sp-nuoc-hoa/deliverables/nuoc-hoa-noir.mp4", f"{K}/sp-nuoc-hoa"),
 "gimbal-axis": (f"{K}/sp-gimbal/deliverables/gimbal-axis.mp4", f"{K}/sp-gimbal"),
 "tai-nghe-hush": (f"{K}/sp-tai-nghe/deliverables/tai-nghe-hush.mp4", f"{K}/sp-tai-nghe"),
 "tennis-ace": (f"{K}/sp-tennis/deliverables/tennis-ace.mp4", f"{K}/sp-tennis"),
 "drone-skyline": (f"{K}/sp-drone/deliverables/drone-skyline.mp4", f"{K}/sp-drone"),
 "xe-vanta": (f"{K}/sp-xe/deliverables/xe-vanta.mp4", f"{K}/sp-xe"),
 "gd-vu-tru": (f"{K}/gd-vu-tru/deliverables/vu-tru.mp4", f"{K}/gd-vu-tru"),
 "gd-hoat-hinh": (f"{K}/gd-hoat-hinh/deliverables/hoat-hinh.mp4", f"{K}/gd-hoat-hinh"),
 "gd-thuc-te": (f"{K}/gd-thuc-te/deliverables/thuc-te.mp4", f"{K}/gd-thuc-te"),
 "cap-phu-de": (f"{K}/cap-phu-de/deliverables/phu-de.mp4", f"{K}/cap-phu-de"),
 "nhip-bong-ro": (f"{K}/nhip-bong-ro/deliverables/nhip.mp4", f"{K}/nhip-bong-ro"),
 "3d-dao": (f"{K}/3d-dao/deliverables/dao.mp4", f"{K}/3d-dao"),
 "3d-phong": (f"{K}/3d-phong/deliverables/phong.mp4", f"{K}/3d-phong"),
 "code-chu": (f"{K}/code-chu/deliverables/chu.mp4", f"{K}/code-chu"),
 "3d-hinh-khoi": (f"{K}/3d-hinh-khoi/deliverables/hinh-khoi.mp4", f"{K}/3d-hinh-khoi"),
 "code-hat": (f"{K}/code-hat/deliverables/hat.mp4", f"{K}/code-hat"),
 "dong-ho-3d": (f"{PC}/dong-ho-3d.mp4", None), "tai-nghe": (f"{PC}/tai-nghe.mp4", None),
 "giay-xoay-3d": (f"{PC}/giay-xoay-3d.mp4", None), "review-3d": (f"{PC}/review-3d.mp4", None),
 "ngu-du-van-met": (f"{PC}/ngu-du-van-met.mp4", None), "heygen-tren-duoi": (f"{PC}/heygen-be-may-anh-tren-nguoi-duoi.mp4", None),
 "noi-sang-hon": (f"{PC}/noi-sang-hon.mp4", None), "tu-vung-quan-ca-phe": (f"{PC}/tu-vung-quan-ca-phe.mp4", None),
 "tu-long-gen-z": (f"{PC}/tu-long-gen-z.mp4", None), "luyen-noi-theo-phim": (f"{PC}/luyen-noi-theo-phim.mp4", None),
 "tu-vung-anh": (f"{PC}/tu-vung-anh.mp4", None), "hoat-hinh-phu-de": (f"{PC}/hoat-hinh-phu-de.mp4", None),
 "ca-phe-hay-tra": (f"{PC}/ca-phe-hay-tra.mp4", None), "ve-phan-bang-den": (f"{PC}/ve-phan-bang-den.mp4", None),
 "viet-chu-han": (f"{PC}/viet-chu-han.mp4", None), "tin-indonesia": (f"{PC}/tin-indonesia-tai-nguyen.mp4", None),
 "alaska": (f"{RD}/01-alaska.mp4", None), "voxel": (f"{PC}/voxel.mp4", None),
 "pixel-art": (f"{PC}/pixel-art.mp4", None), "nhan-vat-3d": (f"{PC}/nhan-vat-3d.mp4", None),
}
SKIP_DIRS = {"renders", "deliverables", "snapshots", "node_modules", ".thumbnails", "raw", "chk", ".hyperframes", "snapshots", "snaps", "snap", "frames", "tmp"}
SKIP_FILES = {"CLAUDE.md", "AGENTS.md"}
BIG = (".mp4", ".webm", ".mov", ".mp3", ".wav", ".m4a")
def probe(p, what):
    return subprocess.check_output(["ffprobe", "-v", "error"] + what + ["-of", "csv=p=0", p]).decode().strip().strip(",")
def copy_source(src, dst):
    media = []
    for d, ds, fs in os.walk(src):
        ds[:] = [x for x in ds if x not in SKIP_DIRS]
        for f in fs:
            a = os.path.join(d, f); rel = os.path.relpath(a, src).replace("\\", "/")
            if f in SKIP_FILES: continue
            if f.lower().endswith(BIG) or os.path.getsize(a) > 1_500_000:
                media.append((rel, os.path.getsize(a))); continue
            os.makedirs(os.path.join(dst, os.path.dirname(rel)), exist_ok=True); shutil.copy2(a, os.path.join(dst, rel))
    return media
R = json.load(open("recipes.json", encoding="utf-8"))
os.makedirs("videos", exist_ok=True); os.makedirs("gallery/posters", exist_ok=True)
out = {"sections": [], "items": []}; missing = []
for it in R["items"]:
    k = it["id"]; v, proj = SRC[k]
    if not os.path.exists(v): missing.append(k); continue
    dst = f"videos/{k}.mp4"
    if not os.path.exists(dst) or os.path.getmtime(v) > os.path.getmtime(dst): shutil.copy2(v, dst)
    w, h = map(int, probe(v, ["-select_streams", "v", "-show_entries", "stream=width,height"]).split(",")[:2])
    d = float(probe(v, ["-show_entries", "format=duration"]))
    post = f"gallery/posters/{k}.jpg"
    if not os.path.exists(post) or os.path.getmtime(v) > os.path.getmtime(post):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, min(d * 0.45, d - 0.5)):.2f}", "-i", v, "-frames:v", "1", "-vf", "scale=-2:540", "-q:v", "4", post], check=True)
    rd = f"recipes/{k}"; os.makedirs(rd, exist_ok=True)
    has_src = False
    if proj and os.path.isdir(proj):
        media = copy_source(proj, rd + "/source"); has_src = True
        with open(rd + "/source/MEDIA.md", "w", encoding="utf-8", newline="\n") as f:
            f.write("# Media not in the repo\n\nFootage, music and renders are left out to keep the repo small. Put your own files at these paths (or download the Pexels clips named in the recipe) before rendering.\n\n")
            f.writelines(f"- `{p}` ({s / 1e6:.1f} MB)\n" for p, s in sorted(media))
    with open(rd + "/README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {it['title']}\n\n![poster](../../{post})\n\n")
        f.write(f"**You give the AI:** {it['input']}  \n**Tools:** {', '.join(it['tools'])}  \n**Cost:** {it['cost']}  \n**Length:** {round(d)}s, {w}x{h}\n\n")
        f.write(f"## Prompt\n\n```text\n{it['prompt']}\n```\n\n")
        if it.get("credits"): f.write(f"## Credits\n\n{it['credits']}\n\n")
        if has_src: f.write("## Source\n\n`source/` is the HyperFrames project. Add the media listed in `source/MEDIA.md`, then run `npx hyperframes render`.\n")
        else: f.write("## Source\n\nMade with an earlier pipeline; only the prompt is published.\n")
    out["items"].append({**it, "w": round(300 * w / h), "d": round(d), "poster": post, "src": has_src})
used = {i["section"] for i in out["items"]}
out["sections"] = [s for s in R["sections"] if s["id"] in used]
open("gallery/data.js", "w", encoding="utf-8", newline="\n").write("window.GALLERY = " + json.dumps(out, ensure_ascii=False) + ";\n")
print(len(out["items"]), "videos;", "missing:", ", ".join(missing) or "none")
# the 2-minute intro: video next to the others, its HyperFrames source in intro/
PROMO = f"{K}/promo-vi"
pv = f"{PROMO}/deliverables/claude-edit-agent-trailer.mp4"
if os.path.exists(pv):
    if not os.path.exists("videos/intro.mp4") or os.path.getmtime(pv) > os.path.getmtime("videos/intro.mp4"): shutil.copy2(pv, "videos/intro.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "27.6", "-i", pv, "-frames:v", "1", "-vf", "scale=-2:540", "-q:v", "4", "gallery/intro.jpg"], check=True)
    media = copy_source(PROMO, "intro/source")
    with open("intro/source/MEDIA.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("# Media not in the repo\n\nThe intro is cut from the gallery videos. `tools/prep.py` makes the short clips in `assets/c/` from them; the music is an original Suno trailer track (130 bpm).\n\n")
        f.writelines(f"- `{p}` ({s / 1e6:.1f} MB)\n" for p, s in sorted(media))
    print("intro copied")
