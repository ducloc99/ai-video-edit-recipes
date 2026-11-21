import fs from "fs";
const P = "D:/Test/Edit-video-1/videos/kho/cap-phu-de/";
const words = JSON.parse(fs.readFileSync(P + "work/words.json", "utf8")).filter(w => /[a-z0-9]/i.test(w.t));
const FPS = 30, f = x => Math.round(x * FPS) / FPS, r3 = x => Math.round(x * 1000) / 1000;
// source segments (frame-snapped) -> output timeline
const SEG = [[0.2, 6.6], [293 / 30, 19.0], [745 / 30, 871 / 30]];
let off = 0; const segs = SEG.map(([a, b]) => { const s = { a, b, out: off, dur: r3(b - a) }; off = r3(off + b - a); return s; });
const TOTAL = off;
const map = t => { for (const s of segs) if (t >= s.a - 0.05 && t < s.b) return r3(s.out + Math.max(0, t - s.a)); return null; };
const W = []; for (const w of words) { const seg = segs.find(g => w.e > g.a + 0.05 && w.s < g.b - 0.05); if (!seg) continue;
  const s = r3(seg.out + Math.max(0, w.s - seg.a));
  W.push({ text: w.t, s, e: r3(Math.min(seg.out + seg.dur, seg.out + (w.e - seg.a))), seg: segs.indexOf(seg) }); }
// groups: phrase breaks chosen by meaning (2-4 words each)
const SIZES = [3,3,4,3,3,2,2, 3,2,2,2,2,3,2,3,2,2,3,3, 3,2,3,3,2,2];
const WC = W.map(w => ({ ...w, clean: w.text.replace(/[.,!?]/g, "") }));
if (SIZES.reduce((a, b) => a + b) !== WC.length) throw new Error("word count " + WC.length);
const G = []; let k = 0; for (const n of SIZES) { G.push(WC.slice(k, k + n)); k += n; }
const EMPH = new Set(["phone", "simple", "noon", "hand", "finished", "seven", "time", "back"]);
let html = "", js = "";
G.forEach((g, gi) => {
  const start = r3(Math.max(0, g[0].s - 0.08)), next = G[gi + 1];
  let end = r3(next ? Math.min(next[0].s - 0.08, g.at(-1).e + 0.6) : TOTAL - 0.05);
  const chars = g.map(w => w.clean).join(" ").length;
  const fs_ = Math.min(84, Math.floor(880 / (chars * 0.72)));
  html += `      <div id="g${gi}" class="grp" data-layout-allow-overlap style="font-size:${fs_}px">` + g.map((w, wi) =>
    `<span class="w" id="g${gi}w${wi}"><span class="base">${w.clean}</span><span class="hi${EMPH.has(w.clean.toLowerCase()) ? " em" : ""}" id="g${gi}h${wi}">${w.clean}</span></span>`).join(" ") + `</div>\n`;
  js += `  tl.fromTo("#g${gi}", { opacity: 0, y: 26, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.2, ease: "power3.out" }, ${start});\n`;
  g.forEach((w, wi) => {
    const ws = r3(Math.max(start, w.s - 0.03)), we = r3(Math.max(ws + 0.11, wi < g.length - 1 ? g[wi + 1].s - 0.03 : end - 0.12));
    js += `  tl.fromTo("#g${gi}h${wi}", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.1, ease: "power2.out" }, ${ws});\n`;
    js += `  tl.set("#g${gi}h${wi}", { opacity: 0 }, ${we});\n`;
  });
  js += `  tl.to("#g${gi}", { opacity: 0, duration: 0.12, ease: "power2.in" }, ${r3(end - 0.12)});\n  tl.set("#g${gi}", { opacity: 0, visibility: "hidden" }, ${end});\n`;
});
const cap = `<template id="captions-template">
  <div id="root" data-composition-id="captions" data-start="0" data-duration="${TOTAL}" data-width="1080" data-height="1920">
    <style>
      #root { position: absolute; inset: 0; width: 1080px; height: 1920px; pointer-events: none; }
      .grp { position: absolute; left: 0; right: 0; top: 1236px; text-align: center; white-space: nowrap; opacity: 0;
        font-family: "Montserrat", sans-serif; font-weight: 900; text-transform: uppercase; letter-spacing: -0.01em; line-height: 1.2;
        color: #fff; overflow: visible; }
      .w { position: relative; display: inline-block; margin: 0 0.06em; }
      .base { position: relative; text-shadow: 0 3px 0 rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.6), 0 6px 18px rgba(0,0,0,0.45); -webkit-text-stroke: 0.11em rgba(10,10,10,0.92); paint-order: stroke fill; }
      .hi { position: absolute; left: -0.16em; right: -0.16em; top: 0.02em; bottom: 0.02em; padding: 0 0.16em; text-align: center;
        background: #FFD23F; color: #111; border-radius: 0.14em; opacity: 0; }
      .hi.em { background: #FFD23F; }
    </style>
${html}    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
${js}      window.__timelines["captions"] = tl;
    </script>
  </div>
</template>
`;
fs.writeFileSync(P + "compositions/captions.html", cap);
// punch-ins: [time, scale]; resets at every scene cut
const SRCCUTS = [3.7667, 13.5333, 15.4, 17.0667, 26.4];
const cuts = [...SRCCUTS.map(map), ...segs.slice(1).map(s => s.out)].sort((a, b) => a - b);
const findW = (txt, n = 0) => W.filter(w => w.text.toLowerCase().replace(/[.,]/g, "") === txt)[n];
const PUNCH = [["phone", 0, 1.1], ["simple", 0, 1.06], ["noon", 0, 1.12], ["hand", 0, 1.08], ["finished", 0, 1.1], ["seven", 0, 1.1], ["one", 1, 1.12]];
let pjs = "";
for (const c of cuts) pjs += `  tl.set("#cam", { scale: 1 }, ${c});\n`;
for (const [t, n, sc] of PUNCH) { const w = findW(t, n); if (!w) { console.error("miss", t); continue; }
  pjs += `  tl.to("#cam", { scale: ${sc}, duration: 0.32, ease: "power3.out" }, ${r3(w.s - 0.04)});\n`; }
const vids = segs.map((s, i) => `      <video id="v${i + 1}" class="clip" src="assets/video-tho.mp4" data-start="${s.out}" data-duration="${s.dur}" data-media-start="${s.a.toFixed(4)}" data-track-index="0" data-has-audio="true" playsinline></video>`).join("\n");
const index = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
      #cam { position: absolute; inset: 0; transform-origin: 50% 34%; }
      #cam video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #captions-host { position: absolute; inset: 0; z-index: 5; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${TOTAL}" data-width="1080" data-height="1920">
      <div id="cam">
${vids}
      </div>
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="${TOTAL}" data-media-start="8.5" data-volume="0.09" data-fade-in="0.5" data-fade-out="1.4" data-track-index="2"></audio>
      <div id="captions-host" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="${TOTAL}" data-track-index="1" data-track-kind="captions"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      tl.set("#cam", { scale: 1 }, 0);
${pjs}      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;
fs.writeFileSync(P + "index.html", index);
console.log("TOTAL", TOTAL, "cuts", cuts); G.forEach(g => console.log(g[0].s, g.map(w => w.clean).join(" ")));
