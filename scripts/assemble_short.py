#!/usr/bin/env python3
"""
assemble_short.py
=================
Automated assembly tool for 20-second portrait (9:16) stickman videos.
Stitches generated clips, rescales to 1080x1920, burns stylized subtitles,
and mixes background music & voiceover for TikTok, YouTube Shorts, and Reels.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, desc="Running command"):
    print(f"[*] {desc}: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error during {desc}:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout


def check_ffmpeg():
    if not subprocess.run(["which", "ffmpeg"], capture_output=True).stdout:
        print("[!] FFmpeg is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)


def create_ass_subtitles(dialogues, output_ass_path):
    """
    Generate an Advanced SubStation Alpha (.ass) file with high-retention viral styling:
    Bold Outfit/Arial, Yellow primary with black outline, centered near bottom.
    """
    ass_header = """[Script Info]
Title: Stickman Short Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
Timer: 100.0000
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,68,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,0,2,80,80,380,1
Style: Punchline,Arial Black,78,&H000055FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,3,0,1,8,0,2,80,80,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for start_t, end_t, text, is_punchline in dialogues:
        style = "Punchline" if is_punchline else "Default"
        events.append(f"Dialogue: 0,{start_t},{end_t},{style},,0,0,0,,{text.upper()}")

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
    print(f"[+] Subtitles generated: {output_ass_path}")


def assemble_video(clips, output_path, subtitles_ass=None, bgm_path=None, voice_path=None):
    """
    Converts and concatenates clips into 1080x1920 (9:16) format,
    applies subtitles, and mixes audio.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    temp_dir = Path("output/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    formatted_clips = []
    for i, clip in enumerate(clips):
        temp_clip = temp_dir / f"clip_{i}_9x16.mp4"
        # Scale & pad to 1080x1920 portrait (or center crop if already 9:16)
        scale_filter = (
            "scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(clip),
            "-vf", scale_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-r", "30",
            "-c:a", "aac",
            "-ar", "44100",
            str(temp_clip)
        ]
        run_cmd(cmd, f"Formatting clip {i+1} to 9:16")
        formatted_clips.append(temp_clip)

    # Concat file list
    concat_list = temp_dir / "concat_list.txt"
    with open(concat_list, "w") as f:
        for c in formatted_clips:
            f.write(f"file '{c.resolve()}'\n")

    raw_concat = temp_dir / "raw_concat.mp4"
    run_cmd([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(raw_concat)
    ], "Concatenating clips")

    # Final pass: audio mixing and subtitle burn
    vf_chain = []
    if subtitles_ass and os.path.exists(subtitles_ass):
        # Escape path for ffmpeg filter
        escaped_ass = str(Path(subtitles_ass).resolve()).replace(":", "\\:").replace("\\", "/")
        vf_chain.append(f"ass='{escaped_ass}'")

    final_cmd = ["ffmpeg", "-y", "-i", str(raw_concat)]

    if bgm_path and os.path.exists(bgm_path):
        final_cmd.extend(["-i", str(bgm_path)])
        # Duck BGM under voice: volume 0.15 for BGM
        audio_filter = "[0:a]volume=1.0[v];[1:a]volume=0.18[bg];[v][bg]amix=inputs=2:duration=first[aout]"
        final_cmd.extend(["-filter_complex", audio_filter, "-map", "0:v", "-map", "[aout]"])
    else:
        final_cmd.extend(["-map", "0:v", "-map", "0:a?"])

    if vf_chain:
        final_cmd.extend(["-vf", ",".join(vf_chain)])

    final_cmd.extend([
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ])

    run_cmd(final_cmd, "Rendering final 9:16 short")
    print(f"\n[🎉 SUCCESS] 9:16 Short produced: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Assemble 20-second 9:16 stickman videos for TikTok/Shorts.")
    parser.add_argument("--clips", nargs="+", required=True, help="Paths to 10s clip files (e.g. clip1.mp4 clip2.mp4)")
    parser.add_argument("--output", default="output/daily_short_9x16.mp4", help="Output video path")
    parser.add_argument("--subtitles", help="Path to .ass subtitles file")
    parser.add_argument("--bgm", help="Path to background music mp3/wav")
    args = parser.parse_args()

    check_ffmpeg()
    assemble_video(args.clips, args.output, subtitles_ass=args.subtitles, bgm_path=args.bgm)


if __name__ == "__main__":
    main()
