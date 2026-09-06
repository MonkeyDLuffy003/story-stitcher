#!/usr/bin/env python3
"""
stitch.py — joins numbered video clips into one video with crossfade transitions.

HOW TO USE:
1. Put your clips in a folder called "clips" named clip1.mp4, clip2.mp4, clip3.mp4, etc.
   (they MUST be numbered in the order you want them to play)
2. (Optional) put one music file at "music.mp3" in the same folder as this script.
3. Run: python3 stitch.py
4. Find your finished video at output/final.mp4

That's it — no manual editing needed.
"""

import subprocess
import os
import glob

CROSSFADE_SECONDS = 0.4   # how long each transition blends between clips
CLIPS_FOLDER = "clips"
MUSIC_FILE = "music.mp3"  # optional — skipped if it doesn't exist
OUTPUT_FILE = "output/final.mp4"


def get_duration(filepath):
    """Ask ffprobe how long a clip is, in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", filepath],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def build_stitch_command(clips, output_path):
    """
    Builds one big ffmpeg command that:
      - takes all clips
      - crossfades between each pair
      - outputs a single continuous video
    """
    inputs = []
    for clip in clips:
        inputs += ["-i", clip]

    # Build the filter chain: xfade between clip[0]+clip[1], then that result + clip[2], etc.
    filter_parts = []
    current_label = "0:v"
    running_offset = 0.0

    durations = [get_duration(c) for c in clips]

    for i in range(1, len(clips)):
        next_label = f"v{i}"
        # offset = when the fade should START, relative to the running combined stream
        running_offset += durations[i - 1] - CROSSFADE_SECONDS
        filter_parts.append(
            f"[{current_label}][{i}:v]xfade=transition=fade:"
            f"duration={CROSSFADE_SECONDS}:offset={running_offset:.2f}[{next_label}]"
        )
        current_label = next_label

    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", f"[{current_label}]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        output_path
    ]
    return cmd


def add_music(video_path, music_path, final_path):
    """Lays background music under the finished video, trimmed to match video length."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music_path,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        final_path
    ]
    subprocess.run(cmd, check=True)


def main():
    os.makedirs("output", exist_ok=True)

    clips = sorted(
        glob.glob(os.path.join(CLIPS_FOLDER, "clip*.mp4")),
        key=lambda p: int("".join(filter(str.isdigit, os.path.basename(p))))
    )

    if len(clips) < 2:
        print(f"Need at least 2 clips in the '{CLIPS_FOLDER}' folder. Found: {clips}")
        return

    print(f"Found {len(clips)} clips: {clips}")
    print("Stitching with crossfades...")

    stitched_path = "output/stitched_no_music.mp4"
    cmd = build_stitch_command(clips, stitched_path)
    subprocess.run(cmd, check=True)

    if os.path.exists(MUSIC_FILE):
        print("Adding background music...")
        add_music(stitched_path, MUSIC_FILE, OUTPUT_FILE)
        os.remove(stitched_path)
    else:
        os.rename(stitched_path, OUTPUT_FILE)
        print("(No music.mp3 found — skipped music step.)")

    print(f"Done! Final video: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
