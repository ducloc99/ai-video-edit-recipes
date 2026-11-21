# gen.py: the Vietnamese cinematic trailer for Claude Edit Agent (index.html).
# Black, letterboxed, hard cuts on the beat of assets/music.mp3 (130 bpm): raw footage -> one typed sentence -> DROP: the name
# -> industries in fast montage -> silent breakdown with three lines -> DROP 2 -> hyper montage -> the name.
import json, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BT = json.load(open("tools/beats.json"))
P = (BT[-1] - BT[0]) / (len(BT) - 1)
def nb(t): return min(range(len(BT)), key=lambda i: abs(BT[i] - t))   # index of the beat nearest t
def b(i): return BT[i] if i < len(BT) else BT[-1] + (i - len(BT) + 1) * P
DUR = 124.0
D1, BRK, D2, FIN = nb(27.0), nb(80.6), nb(87.4), nb(117.6)
H, J = [], []
def js(s): J.append(s)

CLAWD = ["000111111111111000", "000110111111011000", "011111111111111110", "000111111111111000", "000010100000010100"]
CELLS = [(x, y) for y, row in enumerate(CLAWD) for x, c in enumerate(row) if c == "1"]
def clawd(id, px, x, y):
    return (f'<div class="clawd" id="{id}" style="left:{x}px;top:{y}px;width:{18 * px}px;height:{5 * px}px">'
            + "".join(f'<i style="left:{cx * px}px;top:{cy * px}px;width:{px + 1}px;height:{px + 1}px"></i>' for cx, cy in CELLS) + "</div>")

NV = [0]
def video(key, start, dur, media):
    NV[0] += 1
    return (f'<video id="v{NV[0]}" class="clip" src="assets/c/{key}.mp4" data-start="{max(0, start):.3f}" data-duration="{dur:.3f}" '
            f'data-media-start="{media:.2f}" data-track-index="{1 + NV[0] % 8}" muted playsinline></video>')

NS = [0]
def shot(spec, t0, t1, enter="cut"):
    """one full-frame shot from t0 to t1. spec = ("h", key, media) full bleed, or ("t", (key, media), (key, media), (key, media)) three panels"""
    NS[0] += 1; i = f"s{NS[0]}"
    pre, post = 0.35, 0.05
    if spec[0] == "h":
        inner = video(spec[1], t0 - pre, t1 - t0 + pre + post, spec[2])
    else:
        inner = "".join(f'<div class="pn" id="{i}p{n}" style="left:{n * 644}px">{video(k, t0 - pre, t1 - t0 + pre + post, m)}</div>' for n, (k, m) in enumerate(spec[1:]))
    H.append(f'<div class="sh" id="{i}"><div class="in" id="{i}i">{inner}</div></div>')
    js(f'tl.set("#{i}", {{ opacity: 1 }}, {t0:.3f}); tl.set("#{i}", {{ opacity: 0 }}, {t1:.3f});')
    js(f'tl.fromTo("#{i}i", {{ scale: 1.0 }}, {{ scale: 1.06, duration: {t1 - t0:.3f}, ease: "none", immediateRender: false }}, {t0:.3f});')
    if spec[0] == "h" and enter == "punch":
        js(f'tl.fromTo("#{i}", {{ scale: 1.18 }}, {{ scale: 1, duration: 0.32, ease: "expo.out", immediateRender: false }}, {t0:.3f});')
    if spec[0] == "t":
        for n in range(3):
            d = -1 if n % 2 == 0 else 1
            js(f'tl.fromTo("#{i}p{n}", {{ y: {d * 1080} }}, {{ y: 0, duration: 0.34, ease: "expo.out", immediateRender: false }}, {t0 + n * 0.05:.3f});')
    return i

def shake(t, amp=18, dur=0.35):
    js(f'tl.fromTo("#cam", {{ x: 0, y: 0 }}, {{ keyframes: {{ x: [{amp}, {-amp}, {amp * .6:.0f}, {-amp * .4:.0f}, 0], y: [{-amp * .7:.0f}, {amp * .5:.0f}, {-amp * .3:.0f}, {amp * .2:.0f}, 0] }}, duration: {dur}, ease: "none", immediateRender: false }}, {t:.3f});')

NW = [0]
def slam(text, t0, t1, cls=""):
    """a big Vietnamese word slammed onto black on the beat"""
    NW[0] += 1; i = f"w{NW[0]}"
    H.append(f'<div class="slam {cls}" id="{i}">{text}</div>')
    js(f'tl.fromTo("#{i}", {{ opacity: 0, scale: 1.55, filter: "blur(18px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out", immediateRender: false }}, {t0:.3f});')
    js(f'tl.to("#{i}", {{ scale: 1.05, duration: {t1 - t0 - 0.2:.3f}, ease: "none" }}, {t0 + 0.2:.3f}); tl.set("#{i}", {{ opacity: 0 }}, {t1:.3f});')
    shake(t0, 14, 0.3)

NL = [0]
def line(html, t0, t1, top=480, fade=0.5):
    NL[0] += 1; i = f"l{NL[0]}"
    H.append(f'<div class="line" id="{i}" style="top:{top}px{";opacity:1" if t0 <= 0 else ""}">{html}</div>')
    if t0 <= 0:
        js(f'tl.to("#{i}", {{ opacity: 0, duration: 0.3 }}, {t1 - 0.3:.3f});'); return
    js(f'tl.fromTo("#{i}", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: {fade}, ease: "power2.out", immediateRender: false }}, {t0:.3f}); tl.to("#{i}", {{ opacity: 0, duration: 0.3 }}, {t1 - 0.3:.3f});')


NP = [0]
def wipe(raw, rm, edit, em, t0, t1, vertical, rawlab="Video thô", edlab="AI edit"):
    """the raw clip turns into the finished edit as an orange scan line crosses it"""
    NP[0] += 1; i = f"p{NP[0]}"
    x, w = (656, 608) if vertical else (0, 1920)
    sweep0, sweep1 = t0 + (t1 - t0) * 0.28, t0 + (t1 - t0) * 0.62
    side = ""
    if vertical:
        side = (f'<div class="side" id="{i}a" style="left:80px;width:520px">{rawlab}</div>'
                f'<div class="side r" id="{i}b" style="right:80px;width:520px">{edlab}</div>')
    tags = "" if vertical else (f'<div class="tagw" id="{i}a" style="left:90px">{rawlab}</div><div class="tagw o" id="{i}b" style="right:90px">{edlab}</div>')
    H.append(f'<div class="sh" id="{i}">{side}<div class="wp" id="{i}w" style="left:{x}px;width:{w}px">{video(raw, t0 - 0.35, t1 - t0 + 0.4, rm)}'
             f'<div class="ed" id="{i}e">{video(edit, t0 - 0.35, t1 - t0 + 0.4, em)}</div><div class="sc" id="{i}s"></div></div>{tags}</div>')
    js(f'tl.set("#{i}", {{ opacity: 1 }}, {t0:.3f}); tl.set("#{i}", {{ opacity: 0 }}, {t1:.3f});')
    js(f'tl.fromTo("#{i}w", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.4, ease: "expo.out", immediateRender: false }}, {t0:.3f});')
    js(f'tl.fromTo("#{i}e", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: {sweep1 - sweep0:.3f}, ease: "power2.inOut", immediateRender: false }}, {sweep0:.3f});')
    js(f'tl.fromTo("#{i}s", {{ x: 0, opacity: 1 }}, {{ x: {w}, duration: {sweep1 - sweep0:.3f}, ease: "power2.inOut", immediateRender: false }}, {sweep0:.3f}); tl.set("#{i}s", {{ opacity: 0 }}, {sweep1:.3f});')
    if vertical:
        js(f'tl.to("#{i}a", {{ color: "#F4EFE8", duration: 0.2 }}, {t0 + 0.1:.3f}); tl.to("#{i}a", {{ color: "#3A3A3F", duration: 0.2 }}, {sweep1:.3f}); tl.to("#{i}b", {{ color: "#E8774F", duration: 0.2 }}, {sweep1:.3f});')
    else:
        js(f'tl.fromTo("#{i}a", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, {t0 + 0.15:.3f}); tl.to("#{i}a", {{ opacity: 0, duration: 0.2 }}, {sweep1:.3f}); tl.fromTo("#{i}b", {{ opacity: 0, x: 30 }}, {{ opacity: 1, x: 0, duration: 0.3, immediateRender: false }}, {sweep1:.3f});')
    shake(sweep1, 12, 0.3)

def timeline_cut(t0, t1):
    """the edit timeline cuts itself on the beat: frames drop out, the rest close up, the playhead races"""
    FW, G = 160, 20
    frames = "".join(f'<div class="fr" id="tf{n}" style="left:{n * (FW + G)}px"><img src="assets/strip/f{n + 1}.jpg"></div>' for n in range(9))
    ruler = "".join(f'<span style="position:absolute;left:{n * 180}px">00:{n * 2:02d}</span>' for n in range(9))
    H.append(f'<div id="tlw"><div class="ruler" data-layout-ignore>{ruler}</div>{frames}<div class="ph" id="tph"></div><div class="lab2" id="tlab">Claude đang cắt theo nhịp nhạc</div></div>')
    js(f'tl.fromTo("#tlw", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, {t0:.3f}); tl.set("#tlw", {{ opacity: 0 }}, {t1:.3f});')
    js(f'tl.fromTo("#tlw .fr", {{ y: 90, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, stagger: 0.03, ease: "expo.out", immediateRender: false }}, {t0:.3f});')
    js(f'tl.to("#tlab", {{ opacity: 1, duration: 0.3 }}, {t0 + 0.3:.3f});')
    js(f'tl.fromTo("#tph", {{ x: 0 }}, {{ x: 1600, duration: {t1 - t0 - 0.3:.3f}, ease: "none", immediateRender: false }}, {t0:.3f});')
    cuts = [1, 3, 5, 7]; shift = {n: 0 for n in range(9)}
    for j, c in enumerate(cuts):
        tc = t0 + 0.5 + j * (t1 - t0 - 1.0) / len(cuts)
        js(f'tl.to("#tf{c}", {{ y: 220, rotation: 14, opacity: 0, duration: 0.28, ease: "power2.in" }}, {tc:.3f});')
        for n in range(c + 1, 9):
            shift[n] -= FW + G
            js(f'tl.to("#tf{n}", {{ x: {shift[n]}, duration: 0.25, ease: "power3.inOut" }}, {tc + 0.22:.3f});')
        shake(tc, 8, 0.2)

# ---------- 0: cold open, raw footage flickers on the beat ----------
line("Ổ cứng đầy <b>video thô.</b>", 0.0, b(nb(3.5)), 470, 0.8)
raw = [("raw-h01", 0.2), ("raw-h06", 0.4), ("raw-h10", 0.3), ("raw-h01", 1.6), ("raw-h06", 1.8), ("raw-h10", 2.0)]
k = nb(3.5)
for n in range(8):   # 2 beats each: a raw shot, three-up, so it feels like a pile of files
    a, z = b(k + 2 * n), b(k + 2 * n + 2)
    r = [raw[(n + j) % 6] for j in range(3)]
    shot(("t", r[0], r[1], r[2]) if n % 2 == 0 else ("t", (r[2][0], r[2][1] + 0.7), (r[0][0], r[0][1] + 0.9), (r[1][0], r[1][1] + 0.5)), a, z)
k += 16
slam("Không có thời gian dựng.", b(k), b(k + 4), "s2")
k += 4

# ---------- the sentence ----------
T0 = b(k)
line("Chỉ cần <b>nói một câu.</b>", T0, b(k + 4), 470)
k += 4
text = "Dựng thành quảng cáo 15 giây. Chữ thật to sau tai nghe. Nhạc mạnh."
chars = "".join(f"<s>{ch}</s>" for ch in text)
H.append(f'<div class="term" id="term"><div class="hd">{clawd("tk", 4, 0, 0).replace("position:absolute", "")}<span style="margin-left:86px">Claude Edit Agent</span></div><div class="tx"><b>&gt;</b> {chars}<span class="cur"></span></div></div>')
tt = b(k)
js(f'tl.fromTo("#term", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out", immediateRender: false }}, {tt:.3f});')
js(f'tl.to("#term .tx s", {{ display: "inline", duration: 0.001, stagger: {1 / 30:.4f} }}, {tt + 0.3:.3f});')
te = b(k + 8)
js(f'tl.to("#term", {{ scale: 1.08, duration: {te - tt:.2f}, ease: "power1.in" }}, {tt:.3f}); tl.set("#term", {{ opacity: 0 }}, {te:.3f});')
k += 8
timeline_cut(b(k), b(k + 12)); k += 12
# riser: raw and finished frames strobe faster and faster into the drop
n = 0; t = b(k)
while t < b(D1) - 0.05:
    step = max(P / 4, P * (1 - (t - b(k)) / (b(D1) - b(k))))
    shot(("t", ("raw-h01", 0.5 + n * 0.08), ("raw-h10", 0.6 + n * 0.08), ("raw-h06", 0.4 + n * 0.08)) if n % 2 == 0 else ("t", ("tai-nghe-hush", 2 + n * 0.15), ("tai-nghe-hush", 4.5 + n * 0.1), ("tai-nghe-hush", 7 + n * 0.1)), t, min(t + step, b(D1)))
    t += step; n += 1

# ---------- DROP 1: the name ----------
t0 = b(D1)
H.append(f'<div class="sh" id="nm1">{clawd("nk", 20, 780, 250)}<div class="name" id="nm1t" style="top:420px">Claude <b>Edit Agent</b></div></div>')
js(f'tl.set("#nm1", {{ opacity: 1 }}, {t0:.3f}); tl.set("#nm1", {{ opacity: 0 }}, {b(D1 + 8):.3f});')
js(f'tl.fromTo("#nk i", {{ x: (i) => ((i * 137) % 1500) - 750, y: (i) => ((i * 89) % 900) - 450, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.45, stagger: 0.002, ease: "expo.out", immediateRender: false }}, {t0:.3f});')
js(f'tl.fromTo("#nm1t", {{ scale: 1.5, opacity: 0, filter: "blur(20px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out", immediateRender: false }}, {t0 + 0.05:.3f}); tl.to("#nm1t", {{ scale: 1.06, duration: 3.4, ease: "none" }}, {t0 + 0.3:.3f});')
shake(t0, 26, 0.5)
k = D1 + 8
wipe("raw-h10", 0.2, "tai-nghe-hush", 1.0, b(k), b(k + 8), True); k += 8

# ---------- industries ----------
def sector(word, shots, k, w=None):
    slam(word, b(k), b(k + 3)); k += 3
    if w:
        wipe(*w[:4], b(k), b(k + 8), *w[4:]); k += 8
    for spec, n in shots:
        shot(spec, b(k), b(k + n), "punch" if spec[0] == "h" else "cut"); k += n
    return k
k = sector("Bất động sản", [
    (("h", "bds-dung-3d", 2.5), 4), (("t", ("bds-vi-tri", 0.5), ("bds-noi-that", 1), ("bds-vi-tri", 4)), 4),
    (("h", "bds-tour-map", 3), 4), (("h", "bds-ban-ve", 5), 2), (("h", "bds-dung-3d", 5.5), 2), (("t", ("bds-noi-that", 4), ("bds-vi-tri", 2), ("bds-noi-that", 6)), 4)], k, ("raw-villa", 0.2, "bds-ban-ve", 6.0, False, "Clip quay nhà", "Bản vẽ thành nhà thật"))
k = sector("Sản phẩm", [
    (("t", ("nuoc-hoa-noir", 1), ("gimbal-axis", 1), ("tennis-ace", 2)), 4), (("h", "xe-vanta", 2), 4), (("t", ("tai-nghe-hush", 2), ("drone-skyline", 1), ("tennis-ace", 4)), 4),
    (("h", "dong-ho-3d", 1), 2), (("h", "xe-vanta", 5), 2), (("t", ("gimbal-axis", 4), ("nuoc-hoa-noir", 4), ("drone-skyline", 4)), 4)], k)
k = sector("Giáo dục", [
    (("t", ("gd-hoat-hinh", 2), ("gd-vu-tru", 1), ("gd-thuc-te", 2)), 4), (("t", ("viet-chu-han", 2), ("ve-phan-bang-den", 2), ("tu-long-gen-z", 2)), 4),
    (("t", ("tu-vung-anh", 1), ("hoat-hinh-phu-de", 2), ("ca-phe-hay-tra", 2)), 4), (("t", ("gd-vu-tru", 4), ("gd-thuc-te", 5), ("gd-hoat-hinh", 5)), 4)], k)
# fill up to the breakdown with fast two-beat cuts
fill = [("h", "bds-tour-map", 6), ("t", ("tennis-ace", 6), ("nuoc-hoa-noir", 6), ("gimbal-axis", 6)), ("h", "xe-vanta", 6.5), ("t", ("gd-thuc-te", 6), ("tai-nghe-hush", 6), ("gd-vu-tru", 6))]
n = 0
while k + 2 <= BRK:
    shot(fill[n % len(fill)], b(k), b(k + 2), "punch"); k += 2; n += 1
if k < BRK: k = BRK

# ---------- breakdown: three lines on black ----------
t0 = b(BRK)
line("Không cần biết <b>dựng phim.</b>", t0 + 0.1, t0 + 2.0, 470, 0.4)
line("Không cần phần mềm <b>đắt tiền.</b>", t0 + 2.05, t0 + 3.95, 470, 0.4)
line("Chỉ cần biết <b>mình muốn gì.</b>", t0 + 4.0, b(D2) - 0.15, 470, 0.6)

# ---------- DROP 2 ----------
k = D2
k = sector("Edit hằng ngày", [], k, ("raw-talk", 0.2, "cap-phu-de", 0.8, True, "Video nói", "Phụ đề"))
wipe("raw-ball", 0.2, "nhip-bong-ro", 5.0, b(k), b(k + 8), True, "Clip rời", "Cắt theo nhịp"); k += 8
shot(("h", "tin-indonesia", 1), b(k), b(k + 4), "punch"); k += 4
k = sector("3D & code", [
    (("t", ("3d-phong", 1), ("3d-dao", 1), ("3d-hinh-khoi", 1)), 4), (("t", ("code-hat", 2), ("code-chu", 1), ("voxel", 1)), 4),
    (("t", ("3d-dao", 5), ("code-hat", 5.5), ("3d-phong", 5)), 4), (("t", ("pixel-art", 2), ("3d-hinh-khoi", 5), ("code-chu", 5)), 4)], k)
# hyper montage: one cut per beat, then two per beat into the final hit
best = [("h", "bds-ban-ve", 6.5), ("t", ("tai-nghe-hush", 7), ("tennis-ace", 7), ("drone-skyline", 6)), ("h", "xe-vanta", 7), ("t", ("3d-dao", 6), ("gd-hoat-hinh", 6), ("code-chu", 6)),
        ("h", "bds-dung-3d", 7), ("t", ("nuoc-hoa-noir", 7), ("gd-thuc-te", 7), ("nhip-bong-ro", 7)), ("h", "tin-indonesia", 6), ("t", ("3d-phong", 6), ("code-hat", 7), ("gd-vu-tru", 7))]
n = 0
while k + 1 <= FIN - 8:
    shot(best[n % len(best)], b(k), b(k + 1), "punch"); k += 1; n += 1
half = 0
while k < FIN:
    a = b(k) + half * P / 2
    shot(best[(n + half) % len(best)], a, a + P / 2, "punch")
    half += 1
    if half == 2: half = 0; k += 1
    n += 1

# ---------- the name, and where to get the prompts ----------
t0 = b(FIN)
H.append(f'<div class="sh" id="nm2">{clawd("nk2", 20, 780, 230)}<div class="name" id="nm2t" style="top:400px">Claude <b>Edit Agent</b></div>'
         '<div class="sub" id="nm2s" style="top:650px">Mọi câu lệnh và mã nguồn: miễn phí trên GitHub</div></div>')
js(f'tl.set("#nm2", {{ opacity: 1 }}, {t0:.3f});')
js(f'tl.fromTo("#nk2 i", {{ x: (i) => ((i * 137) % 1500) - 750, y: (i) => ((i * 89) % 900) - 450, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.45, stagger: 0.002, ease: "expo.out", immediateRender: false }}, {t0:.3f});')
js(f'tl.fromTo("#nm2t", {{ scale: 1.5, opacity: 0, filter: "blur(20px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out", immediateRender: false }}, {t0 + 0.05:.3f}); tl.to("#nm2t", {{ scale: 1.05, duration: {DUR - t0 - 0.3:.2f}, ease: "none" }}, {t0 + 0.3:.3f});')
js(f'tl.fromTo("#nm2s", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.6, immediateRender: false }}, {t0 + 1.2:.3f});')
js(f'tl.to("#nm2", {{ opacity: 0, duration: 0.8 }}, {DUR - 0.9:.3f});')
shake(t0, 30, 0.55)

js('tl.fromTo("#grain", { x: 0, y: 0 }, { keyframes: { x: [0, -40, 30, -20, 50, -30, 10, 0], y: [0, 20, -30, 40, -10, 30, -20, 0] }, duration: 0.5, ease: "steps(8)", repeat: 247 }, 0);')

CSS = open("tools/style.css", encoding="utf-8").read()
html = f'''<!doctype html>
<html lang="vi"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
/*FONTS*/
{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1920" data-height="1080">
<div id="cam">
{chr(10).join(H)}
</div>
<div id="vig"></div><div id="grain"></div><div id="bars"><i></i><i></i></div>
<audio id="music" src="assets/music.mp3" data-start="0" data-duration="{DUR}" data-track-index="9" data-volume="1"></audio>
</div>
<script>
(function () {{
  const tl = gsap.timeline({{ paused: true }});
  {chr(10).join("  " + l for l in J)}
  tl.to({{}}, {{ duration: 0.01 }}, {DUR - 0.01});
  window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
}})();
</script></body></html>'''
open("index.html", "w", encoding="utf-8", newline="\n").write(html)
print("ok", len(J), "js,", NV[0], "videos; drop1", round(b(D1), 2), "brk", round(b(BRK), 2), "drop2", round(b(D2), 2), "final", round(b(FIN), 2))
