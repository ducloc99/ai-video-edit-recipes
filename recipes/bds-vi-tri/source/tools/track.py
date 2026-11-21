# Point tracker: median LK flow of features around each seed point, forward and backward from its seed frame.
# usage: python track.py video.mp4 seeds.json out.json [sheet.jpg]
# seeds.json: [{"id":"tower","t":2.5,"x":380,"y":850,"r":70}, ...]  (pixel coords in the video frame)
import sys, json
import cv2
import numpy as np

vid, seedf, outf = sys.argv[1:4]
sheet = sys.argv[4] if len(sys.argv) > 4 else None
cap = cv2.VideoCapture(vid)
fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(f)
grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
n = len(frames)
H, W = grays[0].shape
seeds = json.load(open(seedf))
lk = dict(winSize=(31, 31), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))


def step(g0, g1, p, r):
    x, y = p
    mask = np.zeros_like(g0)
    cv2.circle(mask, (int(x), int(y)), int(r), 255, -1)
    pts = cv2.goodFeaturesToTrack(g0, 80, 0.01, 6, mask=mask)
    if pts is None or len(pts) < 4:
        return p
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, pts, None, **lk)
    back, st2, _ = cv2.calcOpticalFlowPyrLK(g1, g0, nxt, None, **lk)
    fb = np.linalg.norm((back - pts).reshape(-1, 2), axis=1)
    good = (st.reshape(-1) == 1) & (st2.reshape(-1) == 1) & (fb < 1.0)
    if good.sum() < 3:
        return p
    d = (nxt - pts).reshape(-1, 2)[good]
    dx, dy = np.median(d[:, 0]), np.median(d[:, 1])
    return (x + float(dx), y + float(dy))


out = {"fps": fps, "n": n, "tracks": {}}
for s in seeds:
    r = s.get("r", 60)
    f0 = min(n - 1, int(round(s["t"] * fps)))
    pos = [None] * n
    pos[f0] = (s["x"], s["y"])
    for i in range(f0, n - 1):
        pos[i + 1] = step(grays[i], grays[i + 1], pos[i], r)
    for i in range(f0, 0, -1):
        pos[i - 1] = step(grays[i], grays[i - 1], pos[i], r)
    out["tracks"][s["id"]] = [[round(p[0], 1), round(p[1], 1)] for p in pos]
json.dump(out, open(outf, "w"))

if sheet:
    cols = []
    for k in range(6):
        i = int(k * (n - 1) / 5)
        im = frames[i].copy()
        for sid, tr in out["tracks"].items():
            x, y = tr[i]
            cv2.circle(im, (int(x), int(y)), 14, (0, 0, 255), 4)
            cv2.putText(im, sid, (int(x) + 18, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3)
        cv2.putText(im, "%.2fs" % (i / fps), (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 255), 5)
        cols.append(cv2.resize(im, (W // 3, H // 3)))
    cv2.imwrite(sheet, np.hstack(cols))
