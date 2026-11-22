# recipes.py: find the gallery recipes closest to a request.
#   python recipes.py                 -> every recipe, by section
#   python recipes.py perfume ad      -> recipes matching the words, best first, with their README and source paths
# The repo root is found from this file's place (skills/edit-agent/scripts -> repo root).
import sys, os, json, re
ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", ".."))
R = json.load(open(os.path.join(ROOT, "recipes.json"), encoding="utf-8"))
# Vietnamese requests: map common words to the English used in the recipes
VI = {"bất động sản": "real estate", "nhà": "house home", "căn hộ": "apartment", "biệt thự": "villa", "sản phẩm": "product", "quảng cáo": "ad",
      "nước hoa": "perfume", "tai nghe": "headphones", "xe": "car", "giày": "sneaker", "đồng hồ": "watch", "giáo dục": "education",
      "hoạt hình": "cartoon", "vũ trụ": "space sun", "từ vựng": "vocabulary", "phụ đề": "captions", "nhịp": "beat", "tin tức": "news",
      "bản đồ": "map", "thể thao": "sports tennis basketball", "chữ": "type text", "người nói": "talking speaker"}
q = " ".join(sys.argv[1:]).lower()
for vi, en in VI.items(): q = q.replace(vi, en)
words = q.split()
sec = {s["id"]: s["name"] for s in R["sections"]}
def score(it):
    text = " ".join([it["title"], it["prompt"], it["input"], " ".join(it["tools"]), sec.get(it["section"], "")]).lower()
    return sum(len(re.findall(r"\b" + re.escape(w), text)) for w in words)
items = sorted(R["items"], key=lambda i: -score(i)) if words else R["items"]
if words: items = [i for i in items if score(i) > 0][:6] or R["items"][:6]
for it in items:
    src = os.path.join(ROOT, "recipes", it["id"], "source")
    print(f"[{sec.get(it['section'], it['section'])}] {it['id']}: {it['title']}  ({it['input']}; {', '.join(it['tools'])})")
    print(f"    recipe: {os.path.join(ROOT, 'recipes', it['id'], 'README.md')}")
    if os.path.isdir(src): print(f"    source: {src}")
