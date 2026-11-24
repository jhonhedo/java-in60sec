# Java.in60sec — Production Kit

## What's here
- `PROJECT_INSTRUCTIONS.md`: paste into the claude.ai Project's Instructions field.
- `episodes.md`: episode log, scripts, captions and topic backlog. Add it to Project files.
- `engine/`: the animation engine.
  - `anim.py`: Ep 1 (String Pool). Also holds the shared helpers: fonts, colours, easing, arrows, background.
  - `hm.py`: Ep 2 (HashMap). `al.py`: Ep 3 (ArrayList vs LinkedList).
  - `sound.py`: synthesizes SFX and the music bed from each module's `SFX` event list.
  - `render.py`: renders a time range of a module to MP4.
  - `align.py`: word timestamps from voiceover MP3 + script.
  - `make_episode.sh`: renders, mixes and outputs the final reel.

## Setup
`./setup.sh` installs skia-python, numpy, pocketsphinx, pillow and ffmpeg. Fonts are already in `fonts/`.

## Automation
A daily scheduled task reads `state.json`, makes the next backlog topic, commits the episode to `episodes/epNN_<slug>/` (module, script, caption, final MP4), and queues the reel in Buffer as a draft for John's approval.

## Making an episode
1. Copy the closest module (e.g. `cp al.py gc.py`) and build the new scenes in its `T` timeline.
2. Preview stills: `python3 -c "import gc_ as m; ..."` (see how stills were checked in each module).
3. Generate the voice with Om (`8hVYjlyENdV7qi07KoIk`, `eleven_v4`) and download the MP3.
4. `python3 align.py voice.mp3 script.txt`, then write the `WARP` anchors and `DUR` in the module.
5. `./make_episode.sh gc_ 45 voice.mp3 java_gc_om.mp4`
