# gen.py: writes index.html for the 2-minute Claude Edit Agent promo.
# Light editorial look: you type what you want -> the edit plays. Every cut sits on a beat of assets/music.mp3 (tools/beats.json).
# Story: raw clips -> the request -> Claude edits -> the result -> name -> five chapters (prompt, then results) -> wall of every video -> name.
import json, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BT = json.load(open("tools/beats.json"))
P = (BT[-1] - BT[0]) / (len(BT) - 1)
def b(i): return BT[i] if i < len(BT) else BT[-1] + (i - len(BT) + 1) * P
DUR = 122.6
H, J = [], []
def js(s): J.append(s)

CLAWD = ["000111111111111000", "000110111111011000", "011111111111111110", "000111111111111000", "000010100000010100"]
CELLS = [(x, y) for y, row in enumerate(CLAWD) for x, c in enumerate(row) if c == "1"]
def clawd(id, px, style=""):
    return (f'<div class="clawd" id="{id}" style="width:{18 * px}px;height:{5 * px}px;{style}">'
            + "".join(f'<i style="left:{x * px}px;top:{y * px}px;width:{px + 1}px;height:{px + 1}px"></i>' for x, y in CELLS) + "</div>")

NV = [0]
def video(src, start, dur, media=0.0):
    NV[0] += 1
    return (f'<video id="v{NV[0]}" class="clip" src="{src}" data-start="{max(0, start):.3f}" data-duration="{dur:.3f}" '
            f'data-media-start="{media:.2f}" data-track-index="{1 + NV[0] % 8}" muted playsinline></video>')

NC = [0]
def card(src, x, y, w, h, t0, t1, media=0.0, delay=0.0, rot=0, enter=True, exit=True, parent=None):
    NC[0] += 1; i = f"c{NC[0]}"
    pre = 0.5
    el = f'<div class="card" id="{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{video(src, t0 - pre, t1 - t0 + pre + 0.6, media)}</div>'
    (parent if parent is not None else H).append(el)
    if rot: js(f'tl.set("#{i}", {{ rotation: {rot} }}, 0);')
    if enter:
        js(f'tl.fromTo("#{i}", {{ x: 260, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.6, ease: "expo.out", immediateRender: false }}, {t0 + delay:.3f});')
    else:
        js(f'tl.set("#{i}", {{ opacity: 1 }}, {t0:.3f});')
    js(f'tl.fromTo("#{i}", {{ scale: 1 }}, {{ scale: 1.03, duration: {t1 - t0:.2f}, ease: "none", immediateRender: false }}, {t0:.3f});')
    if exit:
        js(f'tl.to("#{i}", {{ x: -260, opacity: 0, duration: 0.35, ease: "power2.in" }}, {t1 - 0.35 + delay * 0.5:.3f});')
    return i

def single(k, t0, t1): card(f"assets/c/{k}.mp4", 200, 150, 1520, 855, t0, t1)
def trip(ks, t0, t1):
    for n, k in enumerate(ks): card(f"assets/c/{k}.mp4", 186 + n * 532, 150, 484, 860, t0, t1, delay=n * 0.09)
def duo(hk, vk, t0, t1):
    card(f"assets/c/{hk}.mp4", 110, 258, 1180, 664, t0, t1)
    card(f"assets/c/{vk}.mp4", 1326, 150, 484, 860, t0, t1, delay=0.09)

NS = [0]
def typed(text, t, cps=34):
    """a prompt card; returns (html, js-time when typing ends)"""
    NS[0] += 1; i = f"pc{NS[0]}"
    chars = "".join(f"<s>{ch}</s>" for ch in text)
    html = (f'<div class="pc" id="{i}"><div class="hd">{clawd(i + "k", 4)}<span>Claude Edit Agent</span></div>'
            f'<div class="tx"><b>&gt;</b> {chars}<span class="cur"></span></div></div>')
    dt = 1 / cps
    js(f'tl.set("#{i} .cur", {{ opacity: 1 }}, {t:.3f});')
    js(f'tl.to("#{i} .tx s", {{ display: "inline", duration: 0.001, stagger: {dt:.4f} }}, {t:.3f});')
    return i, html, t + len(text) * dt

def words(id, html, t, stagger=0.08):
    js(f'tl.fromTo("#{id} .mask > span", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.7, ease: "expo.out", stagger: {stagger}, immediateRender: false }}, {t:.3f});')

def scene(id, t0, t1, inner, out="up"):
    H.append(f'<div class="scene" id="{id}"{' style="opacity:1"' if t0 < 0.2 else ''}>{inner}</div>')
    js(f'tl.set("#{id}", {{ opacity: 1 }}, {max(0, t0 - 0.05):.3f});')
    if out == "up":
        js(f'tl.to("#{id}", {{ y: -70, opacity: 0, duration: 0.35, ease: "power2.in" }}, {t1 - 0.35:.3f});')
    else:
        js(f'tl.set("#{id}", {{ opacity: 0 }}, {t1:.3f});')

# ---------- 0: you shot the footage ----------
t0, t1 = b(0), b(8)
raws = [("raw-h01", 1000, 210, -5), ("raw-h06", 1250, 250, 3), ("raw-h10", 1500, 190, -2)]
inner = '<div class="big serif" id="o1t" style="left:130px;top:330px"><span class="mask"><span>You shot</span></span><span class="mask"><span>the <i>footage.</i></span></span></div>'
sub = []
for n, (k, x, y, r) in enumerate(raws):
    card(f"assets/c/{k}.mp4", x, y, 340, 604, t0 + 0.15 + n * 0.2, t1, rot=r, delay=0, exit=False, parent=sub)
    sub.append(f'<div class="lab" id="rl{n}" style="left:{x + 10}px;top:{y + 630}px">{k[4:]}.mp4</div>')
    js(f'tl.to("#rl{n}", {{ opacity: 1, duration: 0.4 }}, {t0 + 0.6 + n * 0.25:.3f});')
scene("o1", t0, t1, inner + "".join(sub))
# title already on screen at 0 s (thumbnail)

# ---------- 4.9: now say what you want ----------
t0, t1 = b(8), b(16)
pid, phtml, tend = typed("Turn these clips into a 15-second ad. Giant word behind the headphones, music only.", t0 + 0.9)
inner = ('<div class="big serif" id="o2t" style="left:360px;top:150px;font-size:110px"><span class="mask"><span>Now just say <i>what you want.</i></span></span></div>'
         + phtml.replace('class="pc"', 'class="pc" style="top:470px"'))
scene("o2", t0, t1, inner)
words("o2t", "", t0 + 0.1)
js(f'tl.fromTo("#{pid}", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: "expo.out", immediateRender: false }}, {t0 + 0.4:.3f});')

# ---------- 9.7: Claude edits (frames are cut and close up) ----------
t0, t1 = b(16), b(24)
FW, GAP, X0, Y0 = 160, 20, 160, 380
frames = "".join(f'<div class="fr" id="fr{n}" style="left:{X0 + n * (FW + GAP)}px;top:{Y0}px"><img src="assets/strip/f{n + 1}.jpg"></div>' for n in range(9))
inner = (f'<div class="strip">{frames}</div>{clawd("cw", 10, f"position:absolute;left:{X0}px;top:{Y0 - 90}px")}'
         f'<div class="lab" id="edl" style="left:0;right:0;text-align:center;top:{Y0 + 340}px;font-size:30px;color:#16140F">Claude is editing</div>')
scene("o3", t0, t1, inner)
js(f'tl.fromTo("#o3 .fr", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, stagger: 0.05, ease: "expo.out", immediateRender: false }}, {t0:.3f});')
js(f'tl.to("#edl", {{ opacity: 1, duration: 0.4 }}, {t0 + 0.4:.3f});')
# Clawd walks along the strip, hopping on every beat
span = 8 * (FW + GAP)
js(f'tl.fromTo("#cw", {{ x: 0 }}, {{ x: {span}, duration: {b(23) - b(16):.2f}, ease: "none", immediateRender: false }}, {b(16):.3f});')
for k in range(16, 23):
    js(f'tl.to("#cw", {{ y: -26, duration: {P / 2 - 0.01:.3f}, ease: "power2.out", yoyo: true, repeat: 1 }}, {b(k):.3f});')
# three frames are cut out on beats, the rest close the gap
for cutn, bb in ((1, 18), (4, 20), (7, 22)):
    js(f'tl.to("#fr{cutn}", {{ y: 160, rotation: 12, opacity: 0, duration: 0.4, ease: "power2.in" }}, {b(bb):.3f});')
shift = {n: 0 for n in range(9)}
for cutn, bb in ((1, 18), (4, 20), (7, 22)):
    for n in range(cutn + 1, 9):
        shift[n] -= FW + GAP
        js(f'tl.to("#fr{n}", {{ x: {shift[n]}, duration: 0.35, ease: "power3.inOut" }}, {b(bb) + 0.3:.3f});')

# ---------- 14.5: the result ----------
t0, t1 = b(24), b(32)
sub = []
card("assets/c/raw-h10.mp4", 330, 260, 330, 586, t0, t1, exit=False, parent=sub)
card("assets/c/tai-nghe-hush.mp4", 860, 80, 520, 924, t0, t1, media=0.0, delay=0.1, exit=False, parent=sub)
sub.append('<div class="lab" id="l1" style="left:340px;top:870px">your clip</div><div class="lab" id="l2" style="left:1420px;top:480px;color:#16140F;font-size:30px">the edit</div>')
scene("o4", t0, t1, "".join(sub))
js(f'tl.to("#l1, #l2", {{ opacity: 1, duration: 0.4, stagger: 0.2 }}, {t0 + 0.6:.3f});')

# ---------- 19.3: the name ----------
def name_scene(id, t0, t1, subline, last=False):
    inner = (clawd(id + "k", 22, "position:absolute;left:762px;top:250px")
             + f'<div id="{id}n" style="position:absolute;left:0;right:0;top:430px;text-align:center;font:800 132px/1.2 \'Inter Tight\',sans-serif;letter-spacing:-4px">'
             + '<span class="mask"><span>Claude <b style="color:#D97757;font-weight:800">Edit Agent</b></span></span></div>'
             + f'<div class="lab" id="{id}s" style="left:0;right:0;text-align:center;top:650px;font-size:34px">{subline}</div>')
    scene(id, t0, t1, inner, out="cut" if last else "up")
    js(f'tl.fromTo("#{id}k i", {{ x: (i) => ((i * 137) % 1500) - 750, y: (i) => ((i * 89) % 900) - 450, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.7, stagger: 0.004, ease: "expo.out", immediateRender: false }}, {t0:.3f});')
    words(id + "n", "", t0 + P * 2)
    js(f'tl.to("#{id}s", {{ opacity: 1, duration: 0.5 }}, {t0 + P * 4:.3f});')
name_scene("nm1", b(32), b(40), "Edit videos by describing them.")

# ---------- chapters: the request, then what came out ----------
CH = [
    ("Real estate", "Draw the floor plan, then turn it into the real house.",
     [("single", "bds-ban-ve"), ("duo", "bds-tour-map", "bds-noi-that"), ("duo", "bds-dung-3d", "bds-vi-tri")]),
    ("Product ads", "Make a 15-second ad. Big type, music only.",
     [("trip", "nuoc-hoa-noir", "gimbal-axis", "tennis-ace"), ("single", "xe-vanta"), ("duo", "dong-ho-3d", "drone-skyline")]),
    ("Education", "Explain how rain is made, as a cartoon.",
     [("trip", "gd-hoat-hinh", "gd-vu-tru", "gd-thuc-te"), ("trip", "viet-chu-han", "ve-phan-bang-den", "tu-long-gen-z"), ("trip", "tu-vung-anh", "hoat-hinh-phu-de", "ca-phe-hay-tra")]),
    ("Everyday edits", "Add captions word by word. Then cut it to the beat.",
     [("trip", "cap-phu-de", "nhip-bong-ro", "alaska"), ("duo", "tin-indonesia", "noi-sang-hon")]),
    ("3D & code", "Build a tiny 3D room that turns from day to night.", json.load(open("tools/ch3d.json"))),
]
bi = 40
for ci, (name, prompt, lays) in enumerate(CH):
    t0, t1 = b(bi), b(bi + 6)
    pid, phtml, tend = typed(prompt, t0 + 0.5, cps=40)
    inner = (f'<div class="big serif" id="ch{ci}t" style="left:360px;top:200px;font-size:120px"><span class="mask"><span>{name}</span></span></div>'
             + phtml.replace('class="pc"', 'class="pc" style="top:450px"'))
    scene(f"ch{ci}", t0, t1, inner)
    words(f"ch{ci}t", "", t0)
    js(f'tl.fromTo("#{pid}", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "expo.out", immediateRender: false }}, {t0 + 0.2:.3f});')
    bi += 6
    end = bi + 8 * len(lays)
    H.append(f'<div class="tag" id="tg{ci}">{name}</div>')
    js(f'tl.fromTo("#tg{ci}", {{ y: -20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "expo.out", immediateRender: false }}, {b(bi):.3f}); tl.to("#tg{ci}", {{ opacity: 0, duration: 0.3 }}, {b(end) - 0.3:.3f});')
    for lay in lays:
        a, z = b(bi), b(bi + 8)
        if lay[0] == "single": single(lay[1], a, z)
        elif lay[0] == "trip": trip(lay[1:], a, z)
        else: duo(lay[1], lay[2], a, z)
        bi += 8
CH_END = bi

# ---------- wall of every video ----------
t0, t1 = b(CH_END), b(196)
P_ = sorted(f for f in os.listdir("assets/posters") if f.endswith(".jpg"))
tiles = []
for n, f in enumerate(P_ * 2):
    if n >= 42: break
    c, r = n % 7, n // 7
    tiles.append(f'<div class="wt" style="left:{c * 370}px;top:{r * 626 + (c % 2) * 220}px"><img src="assets/posters/{f}"></div>')
inner = (f'<div id="wall">{"".join(tiles)}</div>'
         '<div class="plate" id="pl1"><div class="big serif"><span class="mask"><span>Every video here</span></span><span class="mask"><span>comes with its <i>prompt.</i></span></span></div></div>'
         '<div class="plate" id="pl2"><div class="big serif"><span class="mask"><span>Copy it. Change it.</span></span><span class="mask"><span><i>Make yours.</i></span></span></div></div>')
scene("wl", t0, t1, inner, out="cut")
js(f'tl.set("#wall", {{ rotationX: 28, rotationZ: -10 }}, 0);')
js(f'tl.fromTo("#wall", {{ y: 900 }}, {{ y: -700, duration: {t1 - t0:.2f}, ease: "none", immediateRender: false }}, {t0:.3f});')
js(f'tl.fromTo("#wl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out", immediateRender: false }}, {t0:.3f});')
mid = b(CH_END + (196 - CH_END) // 2)
for pl, a, z in (("pl1", b(CH_END + 2), mid), ("pl2", mid, t1)):
    js(f'tl.fromTo("#{pl}", {{ scale: 0.94, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "expo.out", immediateRender: false }}, {a:.3f});')
    words(pl, "", a + 0.1, 0.1)
    js(f'tl.to("#{pl}", {{ opacity: 0, duration: 0.25 }}, {z - 0.25:.3f});')

# ---------- 118: the name, prompts and source ----------
name_scene("nm2", b(196), DUR, "Prompts and source, free on GitHub.", last=True)

js('tl.fromTo("#grain", { x: 0, y: 0 }, { keyframes: { x: [0, -40, 30, -20, 50, -30, 10, 0], y: [0, 20, -30, 40, -10, 30, -20, 0] }, duration: 0.8, ease: "steps(8)", repeat: 152 }, 0);')

CSS = open("tools/style.css", encoding="utf-8").read()
html = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
/*FONTS*/
{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1920" data-height="1080">
<div id="bg"></div>
{chr(10).join(H)}
<div id="grain"></div>
<audio id="music" src="assets/music.mp3" data-start="0" data-duration="{DUR}" data-track-index="9" data-volume="0.95"></audio>
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
print("ok", len(J), "js lines,", NV[0], "videos, chapters end", round(b(CH_END), 1), "wall", round(t0, 1), "->", round(t1, 1))
