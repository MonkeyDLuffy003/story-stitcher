# Story-stitcher

Automatically stitches AI-generated video clips into one smooth story — no manual video editing required.

## Why this exists

AI video tools (like YouTube Create) generate short clips one at a time — usually ~10 seconds each. Joining them manually in an editing app is repetitive and slow. This repo does it automatically: push your clips, and GitHub Actions hands you back one finished video with smooth crossfade transitions and background music.

## How to use it

1. Add your clips to the `clips/` folder, named in play order:
   - `clip1.mp4`
   - `clip2.mp4`
   - `clip3.mp4`
   - ...and so on
2. (Optional) Add a music track to the repo root named `music.mp3`
3. Commit your changes
4. Go to the **Actions** tab → open the latest run → scroll to **Artifacts** → download `final-video`

That's your finished, stitched video — ready to post.

## How it works

- `stitch.py` uses `ffmpeg` to crossfade between each clip and lay music underneath
- `.github/workflows/stitch-video.yml` runs that script automatically every time new clips are pushed

## Adjusting the transition speed

Open `stitch.py` and change this line near the top:

```python
CROSSFADE_SECONDS = 0.4
```

Lower = snappier cuts. Higher = slower, dreamier blends between scenes.
