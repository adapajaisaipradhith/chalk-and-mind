#!/usr/bin/env python3
"""
generate_full_reel.py
=====================
Complete broadcast-ready Instagram Reel / Shorts video generator.
Renders smooth 2D stickman animations, synthesizes Indian voiceover,
mixes background music + whoosh/pop/boom sound effects, and burns
high-retention viral yellow subtitles in 1080x1920 (9:16).
"""

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def run_cmd(cmd, desc="Running"):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error in {desc}:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout


def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    out = run_cmd(cmd, "Getting audio duration")
    return float(out.strip())


def generate_voiceover(text, voice, output_m4a):
    temp_aiff = Path(output_m4a).with_suffix(".aiff")
    cmd = ["say", "-v", voice, text, "-o", str(temp_aiff)]
    run_cmd(cmd, "Synthesizing voiceover")
    
    cmd = [
        "ffmpeg", "-y", "-i", str(temp_aiff),
        "-c:a", "aac", "-b:a", "192k",
        str(output_m4a)
    ]
    run_cmd(cmd, "Encoding voiceover to AAC")
    if temp_aiff.exists():
        temp_aiff.unlink()
    return output_m4a


def time_to_seconds(t_str):
    parts = t_str.split(":")
    hours = float(parts[0])
    mins = float(parts[1])
    secs = float(parts[2])
    return hours * 3600 + mins * 60 + secs


def draw_stickman(draw, center_x, center_y, pose="normal", emotion="normal", prop=None, progress=0.0):
    white = (255, 255, 255)
    yellow = (255, 225, 50)
    cyan = (50, 220, 255)
    red = (255, 60, 60)
    line_w = 12

    head_r = 75
    hx, hy = center_x, center_y - 200
    draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], outline=white, width=line_w)

    neck_y = hy + head_r
    hip_y = neck_y + 250
    draw.line([hx, neck_y, hx, hip_y], fill=white, width=line_w)

    # Eyes & Expressions
    if emotion == "shocked":
        draw.ellipse([hx - 35, hy - 25, hx - 5, hy + 15], outline=white, width=6)
        draw.ellipse([hx + 5, hy - 25, hx + 35, hy + 15], outline=white, width=6)
        draw.ellipse([hx - 22, hy - 10, hx - 14, hy - 2], fill=white)
        draw.ellipse([hx + 18, hy - 10, hx + 26, hy - 2], fill=white)
        draw.ellipse([hx - 15, hy + 25, hx + 15, hy + 50], outline=white, width=6)
    elif emotion in ("super_focus", "motivated"):
        draw.line([hx - 40, hy - 10, hx - 10, hy - 5], fill=cyan, width=10)
        draw.line([hx + 10, hy - 5, hx + 40, hy - 10], fill=cyan, width=10)
        draw.arc([hx - 30, hy + 15, hx + 30, hy + 45], start=0, end=180, fill=white, width=6)
    elif emotion in ("sleepy", "bored"):
        draw.line([hx - 35, hy - 5, hx - 10, hy - 5], fill=white, width=8)
        draw.line([hx + 10, hy - 5, hx + 35, hy - 5], fill=white, width=8)
        draw.line([hx - 20, hy + 35, hx + 20, hy + 35], fill=white, width=6)
    else:
        draw.ellipse([hx - 28, hy - 15, hx - 16, hy - 3], fill=white)
        draw.ellipse([hx + 16, hy - 15, hx + 28, hy - 3], fill=white)
        draw.arc([hx - 25, hy + 10, hx + 25, hy + 40], start=10, end=170, fill=white, width=6)

    shoulder_y = neck_y + 40
    bob = math.sin(progress * math.pi * 4) * 15

    if pose == "celebrating":
        draw.line([hx, shoulder_y, hx - 120, shoulder_y - 140 + bob], fill=white, width=line_w)
        draw.line([hx, shoulder_y, hx + 120, shoulder_y - 140 - bob], fill=white, width=line_w)
        draw.line([hx, hip_y, hx - 90, hip_y + 240], fill=white, width=line_w)
        draw.line([hx, hip_y, hx + 90, hip_y + 240], fill=white, width=line_w)

    elif pose == "facepalm":
        draw.line([hx, shoulder_y, hx - 100, shoulder_y + 60], fill=white, width=line_w)
        draw.line([hx - 100, shoulder_y + 60, hx - 30, hy], fill=white, width=line_w)
        draw.line([hx, shoulder_y, hx + 90, shoulder_y + 80], fill=white, width=line_w)
        draw.line([hx + 90, shoulder_y + 80, hx + 30, hip_y], fill=white, width=line_w)
        draw.line([hx, hip_y, hx - 60, hip_y + 260], fill=white, width=line_w)
        draw.line([hx, hip_y, hx + 60, hip_y + 260], fill=white, width=line_w)

    elif pose == "typing":
        draw.line([hx, shoulder_y, hx - 60, shoulder_y + 110 + bob], fill=white, width=line_w)
        draw.line([hx - 60, shoulder_y + 110 + bob, hx - 10, shoulder_y + 130], fill=white, width=line_w)
        draw.line([hx, shoulder_y, hx + 60, shoulder_y + 110 - bob], fill=white, width=line_w)
        draw.line([hx + 60, shoulder_y + 110 - bob, hx + 10, shoulder_y + 130], fill=white, width=line_w)
        draw.line([hx, hip_y, hx - 100, hip_y + 120], fill=white, width=line_w)
        draw.line([hx - 100, hip_y + 120, hx - 100, hip_y + 260], fill=white, width=line_w)
        draw.line([hx, hip_y, hx + 100, hip_y + 120], fill=white, width=line_w)
        draw.line([hx + 100, hip_y + 120, hx + 100, hip_y + 260], fill=white, width=line_w)

    elif pose == "drinking_chai":
        draw.line([hx, shoulder_y, hx + 90, shoulder_y + 60], fill=white, width=line_w)
        draw.line([hx + 90, shoulder_y + 60, hx + 35, hy + 30], fill=white, width=line_w)
        draw.line([hx, shoulder_y, hx - 80, shoulder_y + 140], fill=white, width=line_w)
        draw.line([hx, hip_y, hx - 70, hip_y + 260], fill=white, width=line_w)
        draw.line([hx, hip_y, hx + 70, hip_y + 260], fill=white, width=line_w)

    else:
        draw.line([hx, shoulder_y, hx - 110, shoulder_y + 120 + bob], fill=white, width=line_w)
        draw.line([hx, shoulder_y, hx + 110, shoulder_y + 80 - bob], fill=white, width=line_w)
        draw.line([hx, hip_y, hx - 60, hip_y + 260], fill=white, width=line_w)
        draw.line([hx, hip_y, hx + 60, hip_y + 260], fill=white, width=line_w)

    # Props
    if prop in ("chai_cup", "chai_glass"):
        gx, gy = hx + 160, center_y - 30
        draw.polygon([(gx - 30, gy - 40), (gx + 30, gy - 40), (gx + 20, gy + 40), (gx - 20, gy + 40)], outline=white, fill=(180, 95, 35))
        steam_offset = math.sin(progress * math.pi * 6) * 10
        draw.arc([gx - 20 + steam_offset, gy - 90, gx + steam_offset, gy - 50], start=180, end=360, fill=yellow, width=5)
        draw.arc([gx + steam_offset, gy - 120, gx + 20 + steam_offset, gy - 80], start=0, end=180, fill=yellow, width=5)

    elif prop == "laptop":
        lx, ly = hx, hip_y - 20
        draw.line([lx - 90, ly, lx + 90, ly], fill=cyan, width=12)
        draw.polygon([(lx - 70, ly - 70), (lx + 70, ly - 70), (lx + 60, ly), (lx - 60, ly)], outline=cyan, fill=(20, 40, 60))

    elif prop in ("flying_papers", "question_marks"):
        for idx, offset in enumerate([-120, 0, 120]):
            qx = hx + offset
            qy = hy - 140 + math.sin((progress * 4 + idx) * math.pi) * 20
            draw.arc([qx - 20, qy - 40, qx + 20, qy], start=180, end=360, fill=yellow, width=8)
            draw.line([qx + 20, qy - 20, qx, qy + 15], fill=yellow, width=8)
            draw.ellipse([qx - 5, qy + 28, qx + 5, qy + 38], fill=yellow)

    elif prop == "degree":
        dx, dy = hx - 140, center_y - 40
        draw.rectangle([dx - 30, dy - 60, dx + 30, dy + 60], outline=white, fill=(240, 240, 240))
        draw.rectangle([dx - 30, dy - 10, dx + 30, dy + 10], fill=red)


def draw_burned_subtitles(draw, current_time, subtitles, width, height, font):
    """
    Renders dynamic, high-retention viral yellow captions with thick black borders.
    """
    active_sub = None
    is_punchline = False
    for idx, sub in enumerate(subtitles):
        st = time_to_seconds(sub["start"])
        et = time_to_seconds(sub["end"])
        if st <= current_time <= et:
            active_sub = sub["text"].upper()
            is_punchline = (idx == len(subtitles) - 1)
            break

    if not active_sub:
        return

    # Wrap text if long
    words = active_sub.split()
    lines = []
    cur_line = []
    for w in words:
        cur_line.append(w)
        if len(" ".join(cur_line)) > 24:
            lines.append(" ".join(cur_line[:-1]))
            cur_line = [w]
    if cur_line:
        lines.append(" ".join(cur_line))

    # Calculate positioning
    text_color = (255, 80, 50) if is_punchline else (255, 235, 40)
    stroke_color = (0, 0, 0)
    stroke_w = 9

    total_text_h = len(lines) * 85
    start_y = 1380 - (total_text_h // 2)

    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        line_w = bbox[2] - bbox[0]
        pos_x = (width - line_w) // 2
        pos_y = start_y + i * 85

        # Draw dark pill background for readability
        pad_x, pad_y = 25, 10
        draw.rounded_rectangle(
            [pos_x - pad_x, pos_y - pad_y, pos_x + line_w + pad_x, pos_y + 70 + pad_y],
            radius=15,
            fill=(0, 0, 0, 160)
        )

        draw.text(
            (pos_x, pos_y),
            line,
            font=font,
            fill=text_color,
            stroke_width=stroke_w,
            stroke_fill=stroke_color
        )


def render_scene_frames(frame_indices, total_frames, scene_info, temp_frames_dir, subtitles, fps, font):
    w, h = 1080, 1920
    action = scene_info.get("action", "normal")
    emotion = scene_info.get("emotion", "normal")
    prop = scene_info.get("prop", None)

    pose_map = {
        "proud_parent": "celebrating",
        "studying_books": "typing",
        "typing_laptop": "typing",
        "facepalm": "facepalm",
        "drinking_chai": "drinking_chai",
        "fist_pump": "celebrating",
        "celebrating_jumping": "celebrating",
        "walking_out": "normal",
        "relaxing_gaming": "typing",
        "slapping_remote": "facepalm"
    }
    pose = pose_map.get(action, "normal")

    for f_idx in frame_indices:
        progress = f_idx / total_frames
        current_time = f_idx / fps

        img = Image.new("RGB", (w, h), color=(14, 18, 26))
        draw = ImageDraw.Draw(img)

        # Background grid
        for gy in range(0, h, 120):
            draw.line([0, gy, w, gy], fill=(22, 28, 40), width=1)
        for gx in range(0, w, 120):
            draw.line([gx, 0, gx, h], fill=(22, 28, 40), width=1)

        center_x = int(w / 2)
        center_y = int(h / 2 - 100 + math.sin(progress * math.pi * 2) * 15)

        # Draw animated stickman
        draw_stickman(draw, center_x, center_y, pose=pose, emotion=emotion, prop=prop, progress=progress)

        # Draw kinetic subtitles directly on frame
        draw_burned_subtitles(draw, current_time, subtitles, w, h, font)

        # Save frame
        frame_path = temp_frames_dir / f"frame_{f_idx:05d}.png"
        img.save(frame_path)


def render_full_reel(day_num, voice="Rishi", output_path=None):
    schedule_file = Path("data/thirty_days_schedule.json")
    with open(schedule_file, "r", encoding="utf-8") as f:
        schedule = json.load(f)

    day_data = next((d for d in schedule if d["day"] == day_num), None)
    if not day_data:
        print(f"[!] Day {day_num} not found in schedule.", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print(f"🎬 RENDERING REEL: Day {day_data['day']} - {day_data['title']}")
    print(f"Category: {day_data['category']} | Hook: \"{day_data['hook']}\"")
    print("=" * 70)

    safe_title = day_data['title'].lower().replace(" ", "_").replace("'", "").replace(":", "")
    output_dir = Path("output/reels")
    output_dir.mkdir(parents=True, exist_ok=True)
    if not output_path:
        output_path = output_dir / f"day_{day_num:02d}_{safe_title}.mp4"

    temp_dir = Path("output/temp") / f"day_{day_num:02d}"
    temp_frames = temp_dir / "frames"
    temp_frames.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize Voiceover
    vo_path = temp_dir / "voiceover.m4a"
    print("\n[1/4] Synthesizing Indian English Voiceover...")
    generate_voiceover(day_data["narration"], voice, vo_path)
    total_dur = get_audio_duration(vo_path)
    print(f"      Voiceover ready: {total_dur:.2f} seconds")

    # Font setup for subtitles
    font_path = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/Helvetica.ttc"
    font = ImageFont.truetype(font_path, 60)

    # 2. Render Animation Frames with Burned Subtitles
    fps = 30
    total_frames = int(total_dur * fps)
    print(f"\n[2/4] Rendering {total_frames} frames with stickman & kinetic subtitles...")

    scenes = day_data.get("animation_scenes", [
        {"action": "normal", "prop": None, "emotion": "normal"}
    ])
    frames_per_scene = total_frames // len(scenes)

    # Adjust last subtitle duration to match audio length
    subs = day_data["subtitles"]
    if subs:
        subs[-1]["end"] = f"00:00:{total_dur:05.2f}"

    for s_idx, scene in enumerate(scenes):
        start_f = s_idx * frames_per_scene
        end_f = total_frames if s_idx == len(scenes) - 1 else (s_idx + 1) * frames_per_scene
        indices = range(start_f, end_f)
        render_scene_frames(indices, total_frames, scene, temp_frames, subs, fps, font)

    # Assemble video from frames
    raw_video = temp_dir / "raw_animation.mp4"
    run_cmd([
        "ffmpeg", "-y",
        "-r", str(fps),
        "-i", str(temp_frames / "frame_%05d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(raw_video)
    ], "Encoding video frames")

    # 3. Mix Audio (Voice + BGM + SFX Whooshes + Boom)
    print("\n[3/4] Mixing Audio: Voiceover, Chill BGM, Whooshes & Boom SFX...")
    sfx_whoosh = Path("assets/audio/sfx/whoosh.wav")
    sfx_boom = Path("assets/audio/sfx/boom.wav")
    bgm_path = Path("assets/audio/bgm/bgm_chill.wav")

    cut_1 = frames_per_scene / fps
    cut_2 = (frames_per_scene * 2) / fps
    cut_3 = (frames_per_scene * 3) / fps
    punchline_t = max(0, total_dur - 4.5)

    filter_complex = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]volume=0.14,atrim=0:{total_dur},afade=t=out:st={total_dur-2}:d=2[bgm];"
        f"[3:a]adelay={int(cut_1*1000)}|{int(cut_1*1000)},volume=0.6[sfx1];"
        f"[3:a]adelay={int(cut_2*1000)}|{int(cut_2*1000)},volume=0.6[sfx2];"
        f"[4:a]adelay={int(punchline_t*1000)}|{int(punchline_t*1000)},volume=0.85[boom];"
        f"[voice][bgm][sfx1][sfx2][boom]amix=inputs=5:duration=first[aout]"
    )

    print("\n[4/4] Producing final broadcast MP4...")
    run_cmd([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(vo_path),
        "-i", str(bgm_path),
        "-i", str(sfx_whoosh),
        "-i", str(sfx_boom),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ], "Final MP4 export")

    # Clean up temp frames to save space
    for f in temp_frames.glob("*.png"):
        f.unlink()

    print("\n" + "=" * 70)
    print(f"🎉 SUCCESS! REEL FOR DAY {day_num} IS COMPLETE:")
    print(f"📁 File:      {output_path}")
    print(f"⏱️ Duration:  {total_dur:.1f}s | Resolution: 1080x1920 (9:16)")
    print(f"💬 Caption:   {day_data['caption']}")
    print(f"🏷️ Hashtags:  {day_data['hashtags']}")
    print("=" * 70)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate full broadcast-ready stickman reel for any day.")
    parser.add_argument("--day", type=int, default=1, help="Day number (1-30)")
    parser.add_argument("--voice", default="Rishi", help="macOS voice name (Rishi, Aman, Tara, Samantha)")
    parser.add_argument("--output", help="Optional custom output path")
    args = parser.parse_args()

    render_full_reel(args.day, voice=args.voice, output_path=args.output)


if __name__ == "__main__":
    main()
