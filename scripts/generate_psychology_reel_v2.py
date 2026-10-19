#!/usr/bin/env python3
"""
generate_psychology_reel_v2.py
==============================
HIGH-END 1-MINUTE PSYCHOLOGY STICKMAN REEL GENERATOR.
Features authentic hand-drawn chalk animation with complete dynamic motion:
- Staggered entrances & write-on animations for all diagrams
- Animated checkmarks that draw in with progressive strokes
- Physics-based swinging & tilting for the balance scale
- Sliding cards & progressively drawn U-curve graph
- Animated red strikethrough lines & stamp effect
- Smooth crossfades (12-frame opacity blends) between scenes
- Character micro-movements: walking, breathing, arm folding, blinking
- Deep resonant baritone voiceover & ambient piano music
- Kinetic Patrick Hand handwriting subtitles with golden yellow active-word highlight
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


def ease_out_cubic(t):
    return 1.0 - math.pow(1.0 - max(0.0, min(1.0, t)), 3)


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def draw_progressive_line(draw, p1, p2, progress, fill, width=4):
    if progress <= 0:
        return
    progress = min(1.0, progress)
    x1, y1 = p1
    x2, y2 = p2
    cur_x = x1 + (x2 - x1) * progress
    cur_y = y1 + (y2 - y1) * progress
    draw.line([(x1, y1), (cur_x, cur_y)], fill=fill, width=width)


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


def draw_animated_stickman(draw, x, y, pose="stand", emotion="serious", is_female=False, is_shadow=False, t=0.0):
    """
    Renders expressive stickman with subtle breathing bob and blinking eyes.
    """
    white = (245, 245, 245) if not is_shadow else (140, 140, 140)
    w = 4 if not is_shadow else 3

    # Breathing micro-bob
    bob = math.sin(t * 3.5) * 2.0
    hx = x
    hy = y - 180 + bob
    head_r = 34

    if is_shadow:
        for a in range(0, 360, 24):
            draw.arc([hx - head_r, hy - head_r, hx + head_r, hy + head_r], start=a, end=a+14, fill=white, width=w)
    else:
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], outline=white, width=w)

    # Hair for female
    if is_female:
        draw.arc([hx - 46, hy - 20, hx - 16, hy + 50], start=80, end=270, fill=white, width=w)
        draw.arc([hx + 16, hy - 20, hx + 46, hy + 50], start=270, end=100, fill=white, width=w)

    # Blinking logic (blink every 3.6s for 0.12s)
    blink_cycle = (t % 3.6)
    is_blinking = (blink_cycle < 0.12) and not is_shadow

    # Face Expressions
    if not is_shadow:
        if is_blinking:
            draw.line([(hx - 16, hy - 4), (hx - 8, hy - 4)], fill=white, width=3)
            draw.line([(hx + 8, hy - 4), (hx + 16, hy - 4)], fill=white, width=3)
            draw.arc([hx - 10, hy + 8, hx + 10, hy + 20], start=0, end=180, fill=white, width=3)
        elif emotion == "peaceful" or is_female:
            draw.arc([hx - 20, hy - 14, hx - 6, hy + 2], start=180, end=360, fill=white, width=3)
            draw.arc([hx + 6, hy - 14, hx + 20, hy + 2], start=180, end=360, fill=white, width=3)
            draw.arc([hx - 12, hy + 8, hx + 12, hy + 22], start=0, end=180, fill=white, width=3)
        else:
            # Serious / observing
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
    elif pose == "arms_open":
        # Questioning gesture
        draw.line([(hx, shoulder_y), (hx - 35, shoulder_y + 30)], fill=white, width=w)
        draw.line([(hx - 35, shoulder_y + 30), (hx - 55, shoulder_y + 15)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 35, shoulder_y + 30)], fill=white, width=w)
        draw.line([(hx + 35, shoulder_y + 30), (hx + 55, shoulder_y + 15)], fill=white, width=w)
    elif pose == "walking":
        walk_swing = math.sin(t * 7.0) * 22
        if is_shadow:
            draw_dashed_line(draw, (hx, shoulder_y), (hx - 25 - walk_swing, shoulder_y + 50), fill=white, width=w)
            draw_dashed_line(draw, (hx, shoulder_y), (hx + 25 + walk_swing, shoulder_y + 50), fill=white, width=w)
        else:
            draw.line([(hx, shoulder_y), (hx - 25 - walk_swing, shoulder_y + 50)], fill=white, width=w)
            draw.line([(hx, shoulder_y), (hx + 25 + walk_swing, shoulder_y + 50)], fill=white, width=w)
    else:
        # Normal standing
        draw.line([(hx, shoulder_y), (hx - 22, shoulder_y + 60)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 22, shoulder_y + 60)], fill=white, width=w)

    # Legs
    if pose == "walking":
        walk_leg = math.sin(t * 7.0) * 24
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


def render_scene_1(draw, cur_t, font_chalk):
    """
    Scene 1: Staggered entrance of Decision boxes, Question marks, Red Strikethrough lines.
    """
    white = (240, 240, 240)
    red = (235, 60, 60)

    # Box 1 drops in at 3.0s
    if cur_t >= 3.0:
        anim_progress = ease_out_cubic((cur_t - 3.0) / 0.5)
        box1_y = int(50 + 60 * anim_progress)
        draw.rounded_rectangle([160, box1_y, 560, box1_y + 60], radius=8, outline=white, width=3)
        draw.text((210, box1_y + 12), "DOESN'T CARE?", font=font_chalk, fill=white)

    # Question mark 1 pops in at 4.5s
    if cur_t >= 4.5:
        draw.text((120, 290), "?", font=font_chalk, fill=(160, 160, 170))

    # Box 2 drops in at 6.0s
    if cur_t >= 6.0:
        anim_progress = ease_out_cubic((cur_t - 6.0) / 0.5)
        box2_y = int(120 + 70 * anim_progress)
        draw.rounded_rectangle([140, box2_y, 580, box2_y + 60], radius=8, outline=white, width=3)
        draw.text((180, box2_y + 12), "NOT ATTRACTED?", font=font_chalk, fill=white)

    # Question mark 2 pops in at 7.0s
    if cur_t >= 7.0:
        draw.text((350, 340), "?", font=font_chalk, fill=(180, 180, 190))

    # Question mark 3 pops in at 8.0s
    if cur_t >= 8.0:
        draw.text((580, 280), "?", font=font_chalk, fill=(160, 160, 170))

    # Red Strikethrough & Banner at 9.2s
    if cur_t >= 9.2:
        strike_prog = ease_out_cubic((cur_t - 9.2) / 0.4)
        # Red X across Box 1
        draw_progressive_line(draw, (170, 115), (550, 165), strike_prog, fill=red, width=5)
        draw_progressive_line(draw, (550, 115), (170, 165), strike_prog, fill=red, width=5)
        # Red X across Box 2
        draw_progressive_line(draw, (150, 195), (570, 245), strike_prog, fill=red, width=5)
        draw_progressive_line(draw, (570, 195), (150, 245), strike_prog, fill=red, width=5)
        # Red banner: COMPLETELY WRONG
        banner_prog = ease_out_cubic((cur_t - 9.5) / 0.3)
        if banner_prog > 0:
            draw.rounded_rectangle([120, 35, 600, 95], radius=10, outline=red, width=3)
            draw.text((180, 47), "COMPLETELY WRONG", font=font_chalk, fill=red)

    # Characters
    pose = "arms_crossed" if cur_t >= 6.5 else "arms_open"
    draw_animated_stickman(draw, 180, 780, pose=pose, emotion="serious", t=cur_t)
    shadow_x = 320 + int(math.sin(cur_t * 3.0) * 50)
    draw_animated_stickman(draw, shadow_x, 780, pose="walking", is_shadow=True, t=cur_t)
    draw_animated_stickman(draw, 580, 780, pose="stand", is_female=True, t=cur_t)


def render_scene_2(draw, cur_t, font_chalk):
    """
    Scene 2: Staggered Checklist entrances with write-on checkmarks and magnifying glass.
    """
    white = (240, 240, 240)
    green = (80, 215, 120)

    # Magnifying glass slides in at 12.5s
    mg_prog = ease_out_cubic((cur_t - 12.2) / 0.6)
    mx = 590
    my = int(80 + 80 * mg_prog)
    mr = 42
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=white, width=4)
    draw.line([(mx + 30, my + 30), (mx + 70, my + 70)], fill=(190, 160, 120), width=7)

    items = [
        {"text": "she shows interest", "appear_t": 13.0, "check_t": 14.0},
        {"text": "effort is mutual", "appear_t": 15.0, "check_t": 16.0},
        {"text": "it feels genuine", "appear_t": 17.0, "check_t": 18.0}
    ]

    start_y = 190
    for idx, item in enumerate(items):
        item_y = start_y + idx * 115
        if cur_t >= item["appear_t"]:
            box_prog = ease_out_cubic((cur_t - item["appear_t"]) / 0.3)
            draw.rounded_rectangle([70, item_y, 130, item_y + 55], radius=8, outline=white, width=4)
            draw.text((160, item_y + 8), item["text"], font=font_chalk, fill=white)

            # Draw green checkmark with progressive stroke
            if cur_t >= item["check_t"]:
                chk_prog = (cur_t - item["check_t"]) / 0.25
                # First stroke down-right
                p1_prog = min(1.0, chk_prog * 2.0)
                draw_progressive_line(draw, (85, item_y + 26), (98, item_y + 40), p1_prog, fill=green, width=5)
                # Second stroke up-right
                if chk_prog > 0.5:
                    p2_prog = min(1.0, (chk_prog - 0.5) * 2.0)
                    draw_progressive_line(draw, (98, item_y + 40), (120, item_y + 16), p2_prog, fill=green, width=5)

            # Accent line under effort is mutual
            if idx == 1 and cur_t >= 16.5:
                line_prog = ease_out_cubic((cur_t - 16.5) / 0.4)
                draw_progressive_line(draw, (165, item_y + 58), (250, item_y + 58), line_prog, fill=(235, 140, 170), width=4)
                draw_progressive_line(draw, (280, item_y + 58), (370, item_y + 58), line_prog, fill=(110, 160, 230), width=4)

    # Character observing with arms folded
    draw_animated_stickman(draw, 490, 780, pose="arms_crossed", emotion="observing", t=cur_t)


def render_scene_3(draw, cur_t, font_chalk):
    """
    Scene 3: Balance Scale with physics swinging & tilting.
    """
    white = (240, 240, 240)
    yellow = (255, 215, 80)
    pink = (245, 120, 130)

    bx, by = 420, 780
    draw.polygon([(bx - 35, by), (bx + 35, by), (bx, by - 30)], fill=(80, 85, 95))
    draw.line([(bx, by - 30), (bx, 310)], fill=white, width=5)

    # Physics swinging tilt: tips left (EQ heavier)
    scale_elapsed = max(0.0, cur_t - 21.0)
    # Pendulum damping equation
    osc = math.exp(-scale_elapsed * 0.4) * math.sin(scale_elapsed * 4.0) * 14.0
    final_tilt = 10.0
    tilt = final_tilt + osc

    x1, y1 = 250, int(310 - tilt)
    x2, y2 = 590, int(310 + tilt)
    draw.line([(x1, y1), (x2, y2)], fill=white, width=5)

    # Left tray (EQ)
    draw.line([(x1, y1), (x1 - 50, y1 + 80)], fill=white, width=3)
    draw.line([(x1, y1), (x1 + 50, y1 + 80)], fill=white, width=3)
    draw.line([(x1 - 60, y1 + 80), (x1 + 60, y1 + 80)], fill=white, width=4)
    cx, cy = x1, y1 + 45
    # Pulsing brain glow
    brain_glow = 1.0 + math.sin(cur_t * 4.0) * 0.08
    draw.arc([cx - int(35 * brain_glow), cy - int(25 * brain_glow), cx + int(35 * brain_glow), cy + int(20 * brain_glow)], start=0, end=360, fill=(200, 100, 150), width=5)
    draw.line([(cx, cy - 20), (cx, cy + 20)], fill=(200, 100, 150), width=4)
    draw.text((x1 - 70, y1 + 95), "emotional", font=font_chalk, fill=yellow)
    draw.text((x1 - 75, y1 + 125), "intelligence", font=font_chalk, fill=yellow)

    # Right tray (Impulse)
    draw.line([(x2, y2), (x2 - 50, y2 + 80)], fill=white, width=3)
    draw.line([(x2, y2), (x2 + 50, y2 + 80)], fill=white, width=3)
    draw.line([(x2 - 60, y2 + 80), (x2 + 60, y2 + 80)], fill=white, width=4)
    px, py = x2, y2 + 48
    draw.polygon([(px, py - 30), (px - 22, py + 18), (px + 22, py + 18)], outline=white, fill=(230, 80, 80))
    draw.polygon([(px, py - 16), (px - 14, py + 5), (px + 14, py + 5)], fill=(245, 170, 60))
    draw.text((x2 - 40, y2 + 100), "impulse", font=font_chalk, fill=pink)

    # Contemplating stick figure
    draw_animated_stickman(draw, 140, 780, pose="hand_on_chin", emotion="serious", t=cur_t)


def render_scene_4(draw, cur_t, font_chalk):
    """
    Scene 4: Sliding pastel cards and progressively drawn U-Curve.
    """
    white = (240, 240, 240)
    pink = (235, 140, 170)
    yellow = (255, 215, 80)

    # Pink card slides down at 35.0s
    card1_prog = ease_out_cubic((cur_t - 35.0) / 0.5)
    c1_y = int(80 + 60 * card1_prog)
    draw.rounded_rectangle([200, c1_y, 520, c1_y + 65], radius=10, outline=pink, width=3)
    draw.text((250, c1_y + 15), "do I like her?", font=font_chalk, fill=white)
    draw.arc([520, c1_y + 10, 560, c1_y + 50], start=270, end=90, fill=pink, width=3)

    # Yellow card drops down at 37.0s
    if cur_t >= 37.0:
        card2_prog = ease_out_cubic((cur_t - 37.0) / 0.5)
        c2_y = int(160 + 65 * card2_prog)
        draw.rounded_rectangle([180, c2_y, 540, c2_y + 65], radius=10, outline=yellow, width=3)
        draw.text((210, c2_y + 15), "is it worth investing?", font=font_chalk, fill=white)
        draw.rectangle([460, c2_y + 65, 480, c2_y + 87], fill=(120, 210, 130))

    # Progressive drawing of U-Curve starting at 38.5s
    if cur_t >= 38.5:
        curve_prog = min(1.0, (cur_t - 38.5) / 1.5)
        all_points = []
        for px in range(410, 590, 5):
            t = (px - 500) / 90.0
            py = 520 + (t ** 2) * 150
            all_points.append((px, py))
        
        num_pts = int(len(all_points) * curve_prog)
        for i in range(num_pts - 1):
            draw.line([all_points[i], all_points[i + 1]], fill=white, width=4)

        if curve_prog > 0.6:
            draw.text((410, 690), "time & energy", font=font_chalk, fill=(130, 135, 150))

    draw_animated_stickman(draw, 220, 780, pose="hand_on_chin", emotion="serious", t=cur_t)


def render_scene_5(draw, cur_t, font_chalk):
    """
    Scene 5: Mutual respect finale. Male and female step in together and smile.
    """
    # Characters walk in smoothly
    walk_prog = min(1.0, (cur_t - 47.0) / 2.0)
    male_x = int(160 + (270 - 160) * ease_out_cubic(walk_prog))
    female_x = int(560 - (560 - 450) * ease_out_cubic(walk_prog))

    pose = "walking" if walk_prog < 0.95 else "stand"
    emotion = "serious" if walk_prog < 0.95 else "peaceful"

    # Blue aura over male, pink aura over female
    if walk_prog >= 0.8:
        aura_prog = ease_out_cubic((cur_t - 48.6) / 0.5)
        draw_progressive_line(draw, (220, 520), (320, 520), aura_prog, fill=(110, 160, 230), width=4)
        draw_progressive_line(draw, (400, 520), (500, 520), aura_prog, fill=(235, 140, 170), width=4)

    draw_animated_stickman(draw, male_x, 780, pose=pose, emotion=emotion, t=cur_t)
    draw_animated_stickman(draw, female_x, 780, pose=pose, emotion=emotion, is_female=True, t=cur_t)


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


def render_scene_at_time(cur_t, w, h, font_chalk):
    img = Image.new("RGB", (w, h), color=(11, 12, 15))
    draw = ImageDraw.Draw(img)

    # Ground line
    draw.line([(40, 780), (680, 780)], fill=(240, 240, 240), width=4)

    if cur_t < 12.0:
        render_scene_1(draw, cur_t, font_chalk)
    elif cur_t < 20.0:
        render_scene_2(draw, cur_t, font_chalk)
    elif cur_t < 35.0:
        render_scene_3(draw, cur_t, font_chalk)
    elif cur_t < 47.0:
        render_scene_4(draw, cur_t, font_chalk)
    else:
        render_scene_5(draw, cur_t, font_chalk)

    return img


def render_psychology_reel(output_path="output/reels/psychology_reel_01.mp4"):
    os.makedirs("output/reels", exist_ok=True)
    temp_dir = Path("output/temp/psychology_reel")
    temp_frames = temp_dir / "frames"
    temp_frames.mkdir(parents=True, exist_ok=True)

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
    print("🎬 RENDERING HIGH-MOTION 1-MINUTE PSYCHOLOGY STICKMAN REEL (v2)")
    print("Style: Fluid Hand-drawn Chalk Animation with Scene Crossfades")
    print("Voice: Deep Philosophical Baritone (en-US-ChristopherNeural)")
    print("=" * 70)

    vo_mp3 = temp_dir / "voice.mp3"
    vo_vtt = temp_dir / "voice.vtt"
    print("\n[1/4] Generating deep resonant voiceover and timestamps...")
    generate_deep_voiceover(script_text, vo_mp3, vo_vtt)
    total_dur = get_audio_duration(vo_mp3)
    print(f"      Voiceover generated: {total_dur:.2f} seconds")

    subtitles = parse_vtt_timestamps(vo_vtt)

    font_path = "assets/fonts/PatrickHand-Regular.ttf"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
    font_chalk = ImageFont.truetype(font_path, 34)
    font_sub = ImageFont.truetype(font_path, 44)

    w, h = 720, 1280
    fps = 30
    total_frames = int(total_dur * fps)
    print(f"\n[2/4] Rendering {total_frames} animated frames with crossfades & motion...")

    # Transition points in seconds:
    transitions = [
        (11.6, 12.0),
        (19.6, 20.0),
        (34.6, 35.0),
        (46.6, 47.0)
    ]

    for f_idx in range(total_frames):
        cur_t = f_idx / fps

        # Check if in a crossfade transition window
        in_transition = False
        trans_alpha = 0.0
        t_before, t_after = 0.0, 0.0

        for t_start, t_end in transitions:
            if t_start <= cur_t <= t_end:
                in_transition = True
                trans_alpha = (cur_t - t_start) / (t_end - t_start)
                t_before = t_start - 0.05
                t_after = t_end + 0.05
                break

        if in_transition:
            img_from = render_scene_at_time(t_before, w, h, font_chalk)
            img_to = render_scene_at_time(t_after, w, h, font_chalk)
            # Smooth cosine blend
            blend_w = ease_in_out(trans_alpha)
            img = Image.blend(img_from, img_to, blend_w)
        else:
            img = render_scene_at_time(cur_t, w, h, font_chalk)

        # Draw kinetic subtitles on top
        draw = ImageDraw.Draw(img)
        draw_reference_subtitles(draw, cur_t, subtitles, w, h, font_sub)

        # Save frame
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
    print("🎉 1-MINUTE HIGH-MOTION PSYCHOLOGY REEL (v2) READY!")
    print(f"📁 Video:    {output_path}")
    print(f"⏱️ Duration: {total_dur:.1f} seconds | Resolution: 720x1280 (9:16)")
    print("=" * 70)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate High-Motion 1-Minute Psychology Stickman Reel.")
    parser.add_argument("--output", default="output/reels/psychology_reel_01.mp4", help="Output file path")
    args = parser.parse_args()

    render_psychology_reel(output_path=args.output)


if __name__ == "__main__":
    main()
