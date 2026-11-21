# Claude Edit Agent: the 2-minute trailer

![poster](../gallery/intro.jpg)

**You give the AI:** the finished gallery videos, a few raw clips, and a music brief  
**Tools:** Claude Code, HyperFrames, Suno (music), librosa (beats)  
**Cost:** about 12 Suno credits for the music; everything else is free  
**Length:** 2:04, 1920x1080, Vietnamese on-screen text

## Prompt

```text
Make a 2-minute 16:9 cinematic trailer for "Claude Edit Agent" in Vietnamese, fast and powerful, no voice-over.
Black, letterboxed, hard cuts on every beat of a new hybrid-trailer track (phonk/trap drums, braams, ~130 bpm,
a drop near 27 s, a near-silent breakdown near 81 s, a second drop near 87 s). Cold open: raw clips flicker
three-up on the beat. One sentence is typed into a terminal, then the edit timeline cuts itself on the beat,
and a strobe of raw vs finished frames speeds up into the drop: the name slams in. Prove the editing: for each
industry show the raw clip turning into the finished edit as an orange scan line crosses it (headphones, villa
footage to sketch, talking clip to captions, loose basketball clips to a beat cut), then hard-cut montages with
the industry word slammed between. Breakdown: three lines on black. Second drop: one cut per beat, then two,
into the final name. No counters, dots or glow.
```

## How it was built

`source/tools/gen.py` writes `index.html` from the beat grid in `tools/beats.json`.
To render: add the media listed in `source/MEDIA.md` (short proxies of the gallery videos in `assets/c/`), then run `python tools/gen.py` and `npx hyperframes render`.
