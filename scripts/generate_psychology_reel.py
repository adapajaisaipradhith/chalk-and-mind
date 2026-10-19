#!/usr/bin/env python3
"""
generate_psychology_reel.py
===========================
1-Minute Deep Psychological & Emotional Maturity Stickman Video Generator.
Faithfully recreates the visual style, voice depth, diagrams, motion frames,
and kinetic handwriting subtitles from the reference reel:
- Background: Matte dark gradient (#0c0c0e) with subtle radial spotlight
- Hand-drawn chalk aesthetic with smooth rounded lines
- Diagrams: Balance scale (EQ vs Impulse), Checklists with green checkmarks,
  Magnifying glass, U-curve graph, pastel dialogue cards
- Voice: Deep, resonant, philosophical baritone (en-US-ChristopherNeural)
- Kinetic Subtitles: Patrick Hand font with glowing golden yellow highlights
  and active word underline.
"""

import argparse
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


def generate_deep_voiceover(text, output_mp3, output_vtt):
    cmd = [
        ".venv/bin/edge-tts",
        "--voice", "en-US-ChristopherNeural",
        "--rate", "-7%",
        "--pitch", "-4Hz",
        "--text", text,
        "--write-media", str(output_mp3),
        "--write-subtitles", str(output_vtt)
    ]
    run_cmd(cmd, "Synthesizing deep voiceover with Edge-TTS")


def parse_vtt_timestamps(vtt_file):
    entries = []
    if not os.path.exists(vtt_file):
        return entries

    with open(vtt_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "-->" in line:
            parts = line.split("-->")
            start_str = parts[0].strip().replace(",", ".")
            end_str = parts[1].strip().split()[0].replace(",", ".")

            def to_secs(s):
                p = s.split(":")
                if len(p) == 3:
                    return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
                elif len(p) == 2:
                    return float(p[0]) * 60 + float(p[1])
                return float(s)

            st = to_secs(start_str)
            et = to_secs(end_str)
            txt_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit() and "-->" not in lines[i]:
                txt_lines.append(lines[i].strip())
                i += 1
            txt = " ".join(txt_lines)
            if txt:
                entries.append({"start": st, "end": et, "text": txt})
            continue
        i += 1
    return entries


def draw_dashed_line(draw, p1, p2, fill=(170, 170, 170), width=3, dash_len=8, gap_len=6):
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    vx = dx / dist
    vy = dy / dist
    cur = 0
    while cur < dist:
        start_d = cur
        end_d = min(cur + dash_len, dist)
        draw.line([(x1 + vx * start_d, y1 + vy * start_d), (x1 + vx * end_d, y1 + vy * end_d)], fill=fill, width=width)
        cur += dash_len + gap_len


def draw_ref_stickman(draw, x, y, pose="stand", emotion="serious", is_female=False, is_shadow=False, progress=0.0):
    white = (245, 245, 245) if not is_shadow else (140, 140, 140)
    w = 4 if not is_shadow else 3

    hx = x
    hy = y - 180
    head_r = 34

    if is_shadow:
        for a in range(0, 360, 24):
            draw.arc([hx - head_r, hy - head_r, hx + head_r, hy + head_r], start=a, end=a+14, fill=white, width=w)
    else:
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], outline=white, width=w)

    # Female Hair
    if is_female:
        draw.arc([hx - 46, hy - 20, hx - 16, hy + 50], start=80, end=270, fill=white, width=w)
        draw.arc([hx + 16, hy - 20, hx + 46, hy + 50], start=270, end=100, fill=white, width=w)

    # Face Expressions
    if not is_shadow:
        if emotion == "peaceful" or is_female:
            draw.arc([hx - 20, hy - 14, hx - 6, hy + 2], start=180, end=360, fill=white, width=3)
            draw.arc([hx + 6, hy - 14, hx + 20, hy + 2], start=180, end=360, fill=white, width=3)
            draw.arc([hx - 12, hy + 8, hx + 12, hy + 22], start=0, end=180, fill=white, width=3)
        elif emotion in ("serious", "observing"):
            draw.line([(hx - 18, hy - 14), (hx - 6, hy - 8)], fill=white, width=3)
            draw.line([(hx + 6, hy - 8), (hx + 18, hy - 14)], fill=white, width=3)
            draw.ellipse([hx - 14, hy - 4, hx - 10, hy], fill=white)
            draw.ellipse([hx + 10, hy - 4, hx + 14, hy], fill=white)
            draw.line([(hx - 8, hy + 14), (hx + 8, hy + 14)], fill=white, width=3)

    # Torso
    neck_y = hy + head_r
    hip_y = neck_y + 115
    if is_shadow:
        draw_dashed_line(draw, (hx, neck_y), (hx, hip_y), fill=white, width=w)
    else:
        draw.line([(hx, neck_y), (hx, hip_y)], fill=white, width=w)

    # Arms
    shoulder_y = neck_y + 20
    if pose == "arms_crossed":
        draw.line([(hx, shoulder_y), (hx - 28, shoulder_y + 25)], fill=white, width=w)
        draw.line([(hx - 28, shoulder_y + 25), (hx + 20, shoulder_y + 25)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 28, shoulder_y + 25)], fill=white, width=w)
        draw.line([(hx + 28, shoulder_y + 25), (hx - 20, shoulder_y + 25)], fill=white, width=w)
    elif pose == "hand_on_chin":
        draw.line([(hx, shoulder_y), (hx - 24, shoulder_y + 40)], fill=white, width=w)
        draw.line([(hx - 24, shoulder_y + 40), (hx - 4, hip_y)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 28, shoulder_y + 35)], fill=white, width=w)
        draw.line([(hx + 28, shoulder_y + 35), (hx + 14, hy + 20)], fill=white, width=w)
    elif pose == "walking":
        walk_swing = math.sin(progress * math.pi * 6) * 20
        if is_shadow:
            draw_dashed_line(draw, (hx, shoulder_y), (hx - 25 - walk_swing, shoulder_y + 50), fill=white, width=w)
            draw_dashed_line(draw, (hx, shoulder_y), (hx + 25 + walk_swing, shoulder_y + 50), fill=white, width=w)
        else:
            draw.line([(hx, shoulder_y), (hx - 25 - walk_swing, shoulder_y + 50)], fill=white, width=w)
            draw.line([(hx, shoulder_y), (hx + 25 + walk_swing, shoulder_y + 50)], fill=white, width=w)
    else:
        draw.line([(hx, shoulder_y), (hx - 22, shoulder_y + 60)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 22, shoulder_y + 60)], fill=white, width=w)

    # Legs
    if pose == "walking":
        walk_leg = math.sin(progress * math.pi * 6) * 22
        if is_shadow:
            draw_dashed_line(draw, (hx, hip_y), (hx - 18 + walk_leg, y), fill=white, width=w)
            draw_dashed_line(draw, (hx, hip_y), (hx + 18 - walk_leg, y), fill=white, width=w)
        else:
            draw.line([(hx, hip_y), (hx - 18 + walk_leg, y)], fill=white, width=w)
            draw.line([(hx, hip_y), (hx + 18 - walk_leg, y)], fill=white, width=w)
    else:
        if is_shadow:
            draw_dashed_line(draw, (hx, hip_y), (hx - 18, y), fill=white, width=w)
            draw_dashed_line(draw, (hx, hip_y), (hx + 18, y), fill=white, width=w)
        else:
            draw.line([(hx, hip_y), (hx - 18, y)], fill=white, width=w)
            draw.line([(hx, hip_y), (hx + 18, y)], fill=white, width=w)


def draw_diagram_checklist(draw, font_chalk, progress=0.0):
    white = (240, 240, 240)
    green = (80, 215, 120)

    # Magnifying glass in top right
    mx, my = 590, 160
    mr = 42
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=white, width=4)
    draw.line([(mx + 30, my + 30), (mx + 70, my + 70)], fill=(190, 160, 120), width=7)

    items = [
        "she shows interest",
        "effort is mutual",
        "it feels genuine"
    ]
    start_y = 190
    for idx, item in enumerate(items):
        item_y = start_y + idx * 115
        draw.rounded_rectangle([70, item_y, 130, item_y + 55], radius=8, outline=white, width=4)
        draw.line([(85, item_y + 26), (98, item_y + 40)], fill=green, width=5)
        draw.line([(98, item_y + 40), (120, item_y + 16)], fill=green, width=5)
        draw.text((160, item_y + 8), item, font=font_chalk, fill=white)
        if idx == 1:
            draw.line([(165, item_y + 58), (250, item_y + 58)], fill=(235, 140, 170), width=4)
            draw.line([(280, item_y + 58), (370, item_y + 58)], fill=(110, 160, 230), width=4)


def draw_diagram_balance_scale(draw, font_chalk, progress=0.0):
    white = (240, 240, 240)
    yellow = (255, 215, 80)
    pink = (245, 120, 130)

    bx, by = 420, 780
    draw.polygon([(bx - 35, by), (bx + 35, by), (bx, by - 30)], fill=(80, 85, 95))
    draw.line([(bx, by - 30), (bx, 310)], fill=white, width=5)

    tilt = math.sin(progress * math.pi) * 8 - 4
    x1, y1 = 250, 310 - tilt
    x2, y2 = 590, 310 + tilt
    draw.line([(x1, y1), (x2, y2)], fill=white, width=5)

    # Left tray
    draw.line([(x1, y1), (x1 - 50, y1 + 80)], fill=white, width=3)
    draw.line([(x1, y1), (x1 + 50, y1 + 80)], fill=white, width=3)
    draw.line([(x1 - 60, y1 + 80), (x1 + 60, y1 + 80)], fill=white, width=4)
    cx, cy = x1, y1 + 45
    draw.arc([cx - 35, cy - 25, cx + 35, cy + 20], start=0, end=360, fill=(200, 100, 150), width=5)
    draw.line([(cx, cy - 20), (cx, cy + 20)], fill=(200, 100, 150), width=4)
    draw.text((x1 - 70, y1 + 95), "emotional", font=font_chalk, fill=yellow)
    draw.text((x1 - 75, y1 + 125), "intelligence", font=font_chalk, fill=yellow)

    # Right tray
    draw.line([(x2, y2), (x2 - 50, y2 + 80)], fill=white, width=3)
    draw.line([(x2, y2), (x2 + 50, y2 + 80)], fill=white, width=3)
    draw.line([(x2 - 60, y2 + 80), (x2 + 60, y2 + 80)], fill=white, width=4)
    px, py = x2, y2 + 48
    draw.polygon([(px, py - 30), (px - 22, py + 18), (px + 22, py + 18)], outline=white, fill=(230, 80, 80))
    draw.polygon([(px, py - 16), (px - 14, py + 5), (px + 14, py + 5)], fill=(245, 170, 60))
    draw.text((x2 - 40, y2 + 100), "impulse", font=font_chalk, fill=pink)


def draw_diagram_ucurve_and_cards(draw, font_chalk, progress=0.0):
    white = (240, 240, 240)
    pink = (235, 140, 170)
    yellow = (255, 215, 80)

    draw.rounded_rectangle([200, 140, 520, 205], radius=10, outline=pink, width=3)
    draw.text((250, 155), "do I like her?", font=font_chalk, fill=white)
    draw.arc([520, 150, 560, 190], start=270, end=90, fill=pink, width=3)

    draw.rounded_rectangle([180, 225, 540, 290], radius=10, outline=yellow, width=3)
    draw.text((210, 240), "is it worth investing?", font=font_chalk, fill=white)
    draw.rectangle([460, 290, 480, 312], fill=(120, 210, 130))

    u_points = []
    for px in range(410, 590, 5):
        t = (px - 500) / 90.0
        py = 520 + (t ** 2) * 150
        u_points.append((px, py))
    for i in range(len(u_points) - 1):
        draw.line([u_points[i], u_points[i + 1]], fill=white, width=4)
    draw.text((410, 690), "time & energy", font=font_chalk, fill=(120, 125, 140))


def draw_decision_boxes(draw, font_chalk, progress=0.0):
    white = (240, 240, 240)
    draw.rounded_rectangle([160, 110, 560, 170], radius=8, outline=white, width=3)
    draw.text((210, 122), "DOESN'T CARE?", font=font_chalk, fill=white)

    draw.rounded_rectangle([140, 190, 580, 250], radius=8, outline=white, width=3)
    draw.text((180, 202), "NOT ATTRACTED?", font=font_chalk, fill=white)

    draw.text((120, 290), "?", font=font_chalk, fill=(150, 150, 160))
    draw.text((350, 340), "?", font=font_chalk, fill=(180, 180, 190))
    draw.text((580, 280), "?", font=font_chalk, fill=(150, 150, 160))


def draw_reference_subtitles(draw, current_time, subtitles, width, height, font_sub):
    active = None
    for sub in subtitles:
        if sub["start"] <= current_time <= sub["end"]:
            active = sub
            break

    if not active:
        return

    text = active["text"].strip()
    words = text.split()
    if not words:
        return

    # Wrap into lines of max 6 words or max 580px width
    lines = []
    cur_line = []
    for w in words:
        cur_line.append(w)
        line_str = " ".join(cur_line)
        bbox = font_sub.getbbox(line_str)
        if (bbox[2] - bbox[0]) > 600:
            if len(cur_line) > 1:
                lines.append(cur_line[:-1])
                cur_line = [w]
            else:
                lines.append(cur_line)
                cur_line = []
    if cur_line:
        lines.append(cur_line)

    sub_dur = max(0.1, active["end"] - active["start"])
    elapsed = current_time - active["start"]
    active_global_idx = min(len(words) - 1, int((elapsed / sub_dur) * len(words)))

    white = (240, 240, 240)
    yellow = (255, 215, 75)
    space_w = font_sub.getbbox(" ")[2] - font_sub.getbbox(" ")[0]

    line_h = 56
    start_y = 860 - ((len(lines) - 1) * line_h) // 2

    word_count_so_far = 0
    for line_idx, line_words in enumerate(lines):
        line_str = " ".join(line_words)
        total_w = sum(font_sub.getbbox(w)[2] - font_sub.getbbox(w)[0] for w in line_words) + (len(line_words) - 1) * space_w
        pos_x = (width - total_w) // 2
        pos_y = start_y + line_idx * line_h

        cur_x = pos_x
        for w in line_words:
            w_w = font_sub.getbbox(w)[2] - font_sub.getbbox(w)[0]
            is_active = (word_count_so_far == active_global_idx) or (word_count_so_far == len(words) - 1 and elapsed > sub_dur * 0.7)
            color = yellow if is_active else white

            draw.text((cur_x, pos_y), w, font=font_sub, fill=color)
            if is_active:
                underline_y = pos_y + 48
                draw.line([(cur_x - 2, underline_y), (cur_x + w_w + 2, underline_y)], fill=yellow, width=4)

            cur_x += w_w + space_w
            word_count_so_far += 1


def render_psychology_reel(output_path="output/reels/psychology_reel_01.mp4"):
    os.makedirs("output/reels", exist_ok=True)
    temp_dir = Path("output/temp/psychology_reel")
    temp_frames = temp_dir / "frames"
    temp_frames.mkdir(parents=True, exist_ok=True)

    # Master Script: ~58 seconds at -7% rate
    script_text = (
        "Most people confuse pursuing with chasing. "
        "They keep reaching out, even when the other person shows zero interest. "
        "But emotionally intelligent people don't chase. "
        "They observe. "
        "They understand that a genuine connection doesn't require one person to carry all the weight. "
        "Instead of constantly asking, 'Do they like me?', they step back and ask: "
        "'Do I actually like them? Is this connection worthy of my peace and energy?' "
        "When you truly value yourself, you stop fighting for attention. "
        "You match effort with effort, and you walk away with silent respect. "
        "Real connection is a two-way street. "
        "Never beg for what should be given freely. "
        "Respect yourself enough to never settle for one-sided effort. "
        "Because a healthy connection is never chased. "
        "It is chosen, every single day."
    )

    print("=" * 70)
    print("🎬 RENDERING 1-MINUTE PSYCHOLOGY STICKMAN REEL")
    print("Style: Psychological Explainer (Faithful to Reference Video)")
    print("Voice: Deep Philosophical Baritone (en-US-ChristopherNeural)")
    print("=" * 70)

    vo_mp3 = temp_dir / "voice.mp3"
    vo_vtt = temp_dir / "voice.vtt"
    print("\n[1/4] Generating deep resonant voiceover and timestamps...")
    generate_deep_voiceover(script_text, vo_mp3, vo_vtt)
    total_dur = get_audio_duration(vo_mp3)
    print(f"      Voiceover generated: {total_dur:.2f} seconds")

    subtitles = parse_vtt_timestamps(vo_vtt)
    print(f"      Parsed {len(subtitles)} synchronized subtitle segments")

    font_path = "assets/fonts/PatrickHand-Regular.ttf"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
    font_chalk = ImageFont.truetype(font_path, 34)
    font_sub = ImageFont.truetype(font_path, 44)

    w, h = 720, 1280
    fps = 30
    total_frames = int(total_dur * fps)
    print(f"\n[2/4] Rendering {total_frames} frames (720x1280 @ {fps} FPS)...")

    for f_idx in range(total_frames):
        cur_t = f_idx / fps
        progress = f_idx / total_frames

        img = Image.new("RGB", (w, h), color=(11, 12, 15))
        draw = ImageDraw.Draw(img)

        # Ground line at y = 780
        draw.line([(40, 780), (680, 780)], fill=(240, 240, 240), width=4)

        if progress < 0.18:
            # Scene 1: Male standing, ghost shadow walking towards female
            draw_decision_boxes(draw, font_chalk, progress=progress)
            draw_ref_stickman(draw, 180, 780, pose="stand", emotion="serious", progress=progress)
            shadow_x = 360 + int(math.sin(progress * 15) * 30)
            draw_ref_stickman(draw, shadow_x, 780, pose="walking", is_shadow=True, progress=progress)
            draw_ref_stickman(draw, 580, 780, pose="stand", is_female=True, progress=progress)

        elif progress < 0.40:
            # Scene 2: The Checklist + Magnifying glass + Character to the right
            draw_diagram_checklist(draw, font_chalk, progress=progress)
            draw_ref_stickman(draw, 490, 780, pose="arms_crossed", emotion="observing", progress=progress)

        elif progress < 0.65:
            # Scene 3: The Balance Scale of Emotional Intelligence vs Impulse
            draw_diagram_balance_scale(draw, font_chalk, progress=progress)
            draw_ref_stickman(draw, 140, 780, pose="hand_on_chin", emotion="serious", progress=progress)

        elif progress < 0.85:
            # Scene 4: U-Curve + Pastel Decision Cards
            draw_diagram_ucurve_and_cards(draw, font_chalk, progress=progress)
            draw_ref_stickman(draw, 220, 780, pose="hand_on_chin", emotion="serious", progress=progress)

        else:
            # Scene 5: Male & Female standing peacefully side by side with mutual respect
            draw.line([(220, 520), (320, 520)], fill=(110, 160, 230), width=4)
            draw.line([(400, 520), (500, 520)], fill=(235, 140, 170), width=4)
            draw_ref_stickman(draw, 270, 780, pose="stand", emotion="peaceful", progress=progress)
            draw_ref_stickman(draw, 450, 780, pose="stand", emotion="peaceful", is_female=True, progress=progress)

        draw_reference_subtitles(draw, cur_t, subtitles, w, h, font_sub)

        frame_file = temp_frames / f"frame_{f_idx:05d}.png"
        img.save(frame_file)

    raw_video = temp_dir / "raw_video.mp4"
    run_cmd([
        "ffmpeg", "-y",
        "-r", str(fps),
        "-i", str(temp_frames / "frame_%05d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(raw_video)
    ], "Encoding animation video")

    # Audio Mixing: Voice + Soft Ambient Background Music
    print("\n[3/4] Mixing deep voiceover with ambient piano background music...")
    bgm_path = Path("assets/audio/bgm/bgm_chill.wav")

    filter_complex = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]volume=0.10,atrim=0:{total_dur},afade=t=out:st={total_dur-3}:d=3[bgm];"
        f"[voice][bgm]amix=inputs=2:duration=first[aout]"
    )

    print("\n[4/4] Exporting broadcast-ready 1-minute Reel...")
    run_cmd([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(vo_mp3),
        "-i", str(bgm_path),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ], "Final video export")

    for f in temp_frames.glob("*.png"):
        f.unlink()

    print("\n" + "=" * 70)
    print("🎉 1-MINUTE PSYCHOLOGY STICKMAN REEL GENERATED SUCCESSFULLY!")
    print(f"📁 Video:    {output_path}")
    print(f"⏱️ Duration: {total_dur:.1f} seconds | Resolution: 720x1280 (9:16)")
    print("=" * 70)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate 1-Minute Psychology Stickman Reel.")
    parser.add_argument("--output", default="output/reels/psychology_reel_01.mp4", help="Output file path")
    args = parser.parse_args()

    render_psychology_reel(output_path=args.output)


if __name__ == "__main__":
    main()
