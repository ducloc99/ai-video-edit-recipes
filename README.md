# Claude Edit Agent: AI Video Edit Recipes

**A skill that makes Claude edit videos for you**, plus a gallery of 41 videos it made, each with the prompt, what you hand the AI, the tools, the cost and, for most of them, the full editable project.

[![Watch the 2-minute trailer](gallery/intro-preview.gif)](https://github.com/ducloc99/ai-video-edit-recipes/releases/download/v1/intro.mp4)

**[▶ Watch the 2-minute trailer](https://github.com/ducloc99/ai-video-edit-recipes/releases/download/v1/intro.mp4)** · **[Install the skill](#install-the-skill)** · [Open the gallery](index.html) · [Tiếng Việt](README.vi.md)

## Install the skill

In Claude Code:

```text
/plugin marketplace add ducloc99/ai-video-edit-recipes
/plugin install edit-agent@ai-video-edit-recipes
```

Or just tell Claude Code: *"Install the skill from https://github.com/ducloc99/ai-video-edit-recipes following INSTALL.md"*. Full steps, requirements and the manual install are in [INSTALL.md](INSTALL.md).

Then open a folder with your clips or photos and say what you want, e.g. *"Turn these clips into a 15-second ad, giant word behind the product, music only."* The skill picks the closest recipe, prepares your footage, builds the edit, checks its own frames and renders an MP4. How it works: [skills/edit-agent/SKILL.md](skills/edit-agent/SKILL.md).

## The gallery

| Section | What you'll find |
|---|---|
| Real estate | sketch → real home, map → 3D massing → footage, floor-plan tours, aerial location pins, editorial listings |
| Product ads | perfume, gimbal, headphones, drone, car, sports gear, 3D exploded view, carousel |
| Education | split-screen expert talk, vocabulary boards, cartoon explainers, space and nature facts |
| Everyday edits & news | word-by-word captions, cut-to-the-beat montage, news explainer, map storytelling |
| 3D & code | voxel and low-poly scenes, tiny rooms, pixel art, kinetic type |

Every recipe lives in [`recipes/<id>/`](recipes/): a README with the prompt and, where available, `source/` — a [HyperFrames](https://hyperframes.heygen.com) project (HTML + GSAP rendered to MP4).

## Using a recipe by hand

Paste a prompt from the gallery into Claude Code (with the skill installed) and change the names, text and length to yours. To re-render a published project: copy `recipes/<id>/source/`, add the media listed in its `MEDIA.md`, then run `npx hyperframes render`.

## What it costs

| Tool | Cost | Used for |
|---|---|---|
| Claude Code | your Claude plan | writing and checking every edit |
| HyperFrames, ffmpeg, OpenCV, rembg, faster-whisper, librosa | free, local | rendering, line drawings, cut-outs, captions, beat detection |
| Pexels | free | stock footage |
| HeyGen, Vbee, other TTS | paid credits | avatars and voices (only the recipes marked so) |

Most recipes are **free** apart from your Claude plan.

## Running the gallery locally

```bash
node tools/serve.mjs 4340   # then open http://localhost:4340
```

The finished MP4s are not in git (they are large). They are attached to the GitHub Release `v1`; fetch them next to the page with `gh release download v1 -D videos`. `VIDEO_BASE` at the top of `index.html` points the page at them. `tools/build.py` rebuilds `gallery/data.js`, the posters and `recipes/` from `recipes.json`.

## Credits and licence

- Stock footage: [Pexels](https://www.pexels.com) creators (Alef Morais, TR Studio, cottonbro studio, Taryn Elliott, Tima Miroshnichenko, Sergei Starostin, Michael Burrows and others), used under the Pexels licence. Footage is not redistributed in this repo.
- Brand names in the videos (NOIR, AXIS, HUSH, ACE, SKYLINE MINI, VANTA GT, Tropical Villa…) are fictional.
- Code and prompts: MIT (see [LICENSE](LICENSE)).
