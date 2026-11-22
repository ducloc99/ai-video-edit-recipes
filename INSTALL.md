# Installing the Claude Edit Agent skill

These steps are written so that **Claude Code can follow them for you**. Open Claude Code and say:

> Cài skill từ https://github.com/ducloc99/ai-video-edit-recipes theo file INSTALL.md
> (or: Install the skill from https://github.com/ducloc99/ai-video-edit-recipes following INSTALL.md)

## Option A: as a Claude Code plugin (recommended)

In Claude Code, type:

```text
/plugin marketplace add ducloc99/ai-video-edit-recipes
/plugin install edit-agent@ai-video-edit-recipes
```

Then start a new session. The whole repo (skill, scripts and every recipe) is installed together.
While the repo is private, your machine must be signed in to a GitHub account that has access (`gh auth login`).

## Option B: by hand (what Claude does when you ask it to install)

1. **Clone the repo** to a fixed place:
   - Windows: `git clone https://github.com/ducloc99/ai-video-edit-recipes "$HOME/.claude/ai-video-edit-recipes"`
   - macOS / Linux: `git clone https://github.com/ducloc99/ai-video-edit-recipes ~/.claude/ai-video-edit-recipes`
2. **Link the skill** into the skills folder (a link, so `git pull` updates it and the skill can find the recipes):
   - Windows (PowerShell): `New-Item -ItemType Junction -Path "$HOME/.claude/skills/edit-agent" -Target "$HOME/.claude/ai-video-edit-recipes/skills/edit-agent"`
   - macOS / Linux: `ln -s ~/.claude/ai-video-edit-recipes/skills/edit-agent ~/.claude/skills/edit-agent`
3. **Check the tools** (install only what is missing, after asking):
   - Node.js 22+ (`node --version`), ffmpeg (`ffmpeg -version`), Python 3.10+ (`python --version`)
   - HyperFrames: `npx --yes hyperframes@0.9.74 --version`, then `npx hyperframes skills update` for the HyperFrames skills
   - Python packages, only for the features that need them: `pip install librosa` (cut to the beat), `pip install rembg onnxruntime pillow numpy` (text behind a person or product), `pip install faster-whisper` (captions)
4. **Test it**: `python ~/.claude/skills/edit-agent/scripts/recipes.py product ad` should list recipes with their paths.
5. Start a new Claude Code session so the skill is loaded.

## Optional: the gallery videos on your machine

```bash
cd ~/.claude/ai-video-edit-recipes
gh release download v1 -D videos
node tools/serve.mjs 4340     # open http://localhost:4340
```

## Using it

Put your clips or photos in a folder, open it in Claude Code and just say what you want, for example:

> Dựng mấy clip này thành quảng cáo 15 giây, chữ thật to nằm sau sản phẩm, chỉ có nhạc.

or copy a prompt from the gallery and change the names and text to yours.

## Updating

Plugin: `/plugin marketplace update ai-video-edit-recipes`. By hand: `git -C ~/.claude/ai-video-edit-recipes pull`.
