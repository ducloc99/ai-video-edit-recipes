import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("small.en",device="cpu",compute_type="int8")
segs,_=m.transcribe(sys.argv[1],language="en",word_timestamps=True,vad_filter=False)
out=[]
for s in segs:
    for w in s.words: out.append({"t":w.word.strip(),"s":round(w.start,3),"e":round(w.end,3)})
json.dump(out,open("words.json","w"),indent=0)
for w in out: print(w["s"],w["e"],w["t"])
