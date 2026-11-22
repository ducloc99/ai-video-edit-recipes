# beats.py: beat times of a music file, for cutting on the beat. Writes a JSON list of seconds and prints tempo,
# the first beats and where the music gets loud or quiet (drops and breakdowns).
#   python beats.py <music.mp3> <beats.json>
# Needs: pip install librosa
import sys, json
import numpy as np, librosa
y, sr = librosa.load(sys.argv[1], sr=22050)
tempo, bt = librosa.beat.beat_track(y=y, sr=sr, units="time")
json.dump([round(float(t), 3) for t in bt], open(sys.argv[2], "w"))
rms = librosa.feature.rms(y=y)[0]; tt = librosa.times_like(rms, sr=sr)
loud = [round(float(rms[(tt >= s) & (tt < s + 1)].mean()), 3) for s in range(int(len(y) / sr))]
print(f"tempo {float(np.atleast_1d(tempo)[0]):.1f} bpm, {len(bt)} beats, length {len(y) / sr:.1f}s")
print("first beats", [round(float(t), 2) for t in bt[:8]])
print("loudness per second", loud)
