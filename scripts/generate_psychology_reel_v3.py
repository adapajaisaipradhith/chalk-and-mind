#!/usr/bin/env python3
"""
generate_psychology_reel_v3.py
==============================
FRAMER MOTION MASTER EDITION — 1-Minute Deep Psychological Stickman Reel.
Implements true spring physics (stiffness/damping), staggered organic entrances,
ambient floating motes, smooth progressive stroke drawing, and emotional audio:
- Damped harmonic oscillator (spring physics) on all diagram entrances
- Progressive chalk stroke drawing with rounded caps
- Drifting ambient light motes in deep matte dark (#0b0c0e) void
- Hair sway & breathing idle physics
- Rich emotional acoustic piano & sub-bass heartbeat BGM
- Kinetic Patrick Hand handwriting subtitles with glowing golden yellow active word & underline
"""

import argparse
import math
import os
import random
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


def spring(t_elapsed, start=0.0, target=1.0, stiffness=130.0, damping=14.0):
    """
    Framer Motion spring physics (Damped harmonic oscillator).
    Gives realistic, organic settlement with subtle elastic overshoot.
    """
    if t_elapsed <= 0.0:
        return start
    gamma = damping / 2.0
    omega_sq = stiffness - (gamma * gamma)
    if omega_sq > 0:
        omega = math.sqrt(omega_sq)
        decay = math.exp(-gamma * t_elapsed)
        return target + (start - target) * decay * (math.cos(omega * t_elapsed) + (gamma / omega) * math.sin(omega * t_elapsed))
    else:
        return target + (start - target) * math.exp(-gamma * t_elapsed)


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


def draw_floating_motes(draw, t, width=720, height=1280):
    """
    Renders soft, floating ambient dust / light motes giving organic depth to the dark canvas.
    """
    random.seed(42)
    for i in range(16):
        base_x = random.uniform(40, width - 40)
        base_y = random.uniform(80, height - 150)
        speed = random.uniform(12, 28)
        radius = random.uniform(1.5, 3.5)
        # Drifting wave
        y = (base_y - t * speed) % (height - 100) + 50
        x = base_x + math.sin(t * 1.2 + i) * 15
        alpha = int(45 + math.sin(t * 2.0 + i) * 25)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(220, 225, 235, alpha))


def draw_animated_stickman(draw, x, y, pose="stand", emotion="serious", is_female=False, is_shadow=False, t=0.0):
    white = (245, 245, 245) if not is_shadow else (140, 140, 140)
    w = 4 if not is_shadow else 3

    # Breathing micro-bob
    bob = math.sin(t * 3.5) * 2.2
    hx = x
    hy = y - 180 + bob
    head_r = 34

    if is_shadow:
        for a in range(0, 360, 24):
            draw.arc([hx - head_r, hy - head_r, hx + head_r, hy + head_r], start=a, end=a+14, fill=white, width=w)
    else:
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], outline=white, width=w)

    # Hair sway physics for female
    if is_female:
        hair_sway = math.sin(t * 3.0) * 3.0
        draw.arc([hx - 46 + hair_sway, hy - 20, hx - 16 + hair_sway, hy + 50], start=80, end=270, fill=white, width=w)
        draw.arc([hx + 16 + hair_sway, hy - 20, hx + 46 + hair_sway, hy + 50], start=270, end=100, fill=white, width=w)

    # Blinking logic (blink every 3.8s for 0.12s)
    blink_cycle = (t % 3.8)
    is_blinking = (blink_cycle < 0.12) and not is_shadow

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

    neck_y = hy + head_r
    hip_y = neck_y + 115
    if is_shadow:
        draw_dashed_line(draw, (hx, neck_y), (hx, hip_y), fill=white, width=w)
    else:
        draw.line([(hx, neck_y), (hx, hip_y)], fill=white, width=w)

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
        draw.line([(hx, shoulder_y), (hx - 22, shoulder_y + 60)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 22, shoulder_y + 60)], fill=white, width=w)

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
    white = (240, 240, 240)
    red = (235, 60, 60)
    green = (80, 215, 120)

    # Box 1 drops with Framer Motion spring physics at 2.5s
    # Voice: "Most people confuse pursuing with chasing"
    if cur_t >= 2.5:
        box1_y = int(spring(cur_t - 2.5, start=40.0, target=110.0, stiffness=120.0, damping=13.0))
        draw.rounded_rectangle([140, box1_y, 580, box1_y + 60], radius=8, outline=green, width=3)
        draw.text((180, box1_y + 12), "PURSUING vs CHASING", font=font_chalk, fill=green)

    # Question mark 1 pops in at 4.5s
    if cur_t >= 4.5:
        q_scale = spring(cur_t - 4.5, start=0.2, target=1.0, stiffness=180.0, damping=12.0)
        if q_scale > 0.5:
            draw.text((120, 290), "?", font=font_chalk, fill=(160, 160, 170))

    # Box 2 drops with spring at 5.8s
    # Voice: "even when the other person shows zero interest"
    if cur_t >= 5.8:
        box2_y = int(spring(cur_t - 5.8, start=120.0, target=190.0, stiffness=120.0, damping=13.0))
        draw.rounded_rectangle([150, box2_y, 570, box2_y + 60], radius=8, outline=red, width=3)
        draw.text((220, box2_y + 12), "ZERO INTEREST", font=font_chalk, fill=red)

    if cur_t >= 7.0:
        draw.text((350, 340), "?", font=font_chalk, fill=(180, 180, 190))
    if cur_t >= 8.0:
        draw.text((580, 280), "?", font=font_chalk, fill=(160, 160, 170))

    # Red Strikethrough & Banner at 9.0s
    # Voice: "But emotionally intelligent people don't chase. They observe."
    if cur_t >= 9.0:
        strike_prog = spring(cur_t - 9.0, start=0.0, target=1.0, stiffness=160.0, damping=16.0)
        draw_progressive_line(draw, (140, 115), (580, 165), strike_prog, fill=red, width=5)
        draw_progressive_line(draw, (580, 115), (140, 165), strike_prog, fill=red, width=5)
        draw_progressive_line(draw, (150, 195), (570, 245), strike_prog, fill=red, width=5)
        draw_progressive_line(draw, (570, 195), (150, 245), strike_prog, fill=red, width=5)
        if cur_t >= 9.5:
            banner_scale = spring(cur_t - 9.5, start=0.6, target=1.0, stiffness=140.0, damping=12.0)
            if banner_scale > 0.7:
                draw.rounded_rectangle([120, 35, 600, 95], radius=10, outline=(255, 215, 80), width=3)
                draw.text((160, 47), "DON'T CHASE • OBSERVE", font=font_chalk, fill=(255, 215, 80))

    pose = "arms_crossed" if cur_t >= 6.5 else "arms_open"
    draw_animated_stickman(draw, 180, 780, pose=pose, emotion="serious", t=cur_t)
    shadow_x = 320 + int(math.sin(cur_t * 3.0) * 50)
    draw_animated_stickman(draw, shadow_x, 780, pose="walking", is_shadow=True, t=cur_t)
    draw_animated_stickman(draw, 580, 780, pose="stand", is_female=True, t=cur_t)


def render_scene_2(draw, cur_t, font_chalk):
    white = (240, 240, 240)
    green = (80, 215, 120)

    # Magnifying glass slides in with spring
    # Voice: "They understand that a genuine connection doesn't require one person to carry all the weight"
    my = int(spring(cur_t - 12.2, start=60.0, target=160.0, stiffness=110.0, damping=14.0))
    mx = 590
    mr = 42
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=white, width=4)
    draw.line([(mx + 30, my + 30), (mx + 70, my + 70)], fill=(190, 160, 120), width=7)

    items = [
        {"text": "genuine connection", "appear_t": 12.8, "check_t": 14.2},
        {"text": "effort is mutual", "appear_t": 15.0, "check_t": 16.5},
        {"text": "never carry all weight", "appear_t": 17.2, "check_t": 18.5}
    ]

    start_y = 190
    for idx, item in enumerate(items):
        item_y = start_y + idx * 115
        if cur_t >= item["appear_t"]:
            draw.rounded_rectangle([70, item_y, 130, item_y + 55], radius=8, outline=white, width=4)
            draw.text((160, item_y + 8), item["text"], font=font_chalk, fill=white)

            if cur_t >= item["check_t"]:
                chk_prog = (cur_t - item["check_t"]) / 0.25
                p1_prog = min(1.0, chk_prog * 2.0)
                draw_progressive_line(draw, (85, item_y + 26), (98, item_y + 40), p1_prog, fill=green, width=5)
                if chk_prog > 0.5:
                    p2_prog = min(1.0, (chk_prog - 0.5) * 2.0)
                    draw_progressive_line(draw, (98, item_y + 40), (120, item_y + 16), p2_prog, fill=green, width=5)

            if idx == 1 and cur_t >= 16.5:
                line_prog = spring(cur_t - 16.5, start=0.0, target=1.0, stiffness=140.0, damping=15.0)
                draw_progressive_line(draw, (165, item_y + 58), (250, item_y + 58), line_prog, fill=(235, 140, 170), width=4)
                draw_progressive_line(draw, (280, item_y + 58), (370, item_y + 58), line_prog, fill=(110, 160, 230), width=4)

    draw_animated_stickman(draw, 490, 780, pose="arms_crossed", emotion="observing", t=cur_t)


def render_scene_3(draw, cur_t, font_chalk):
    white = (240, 240, 240)
    yellow = (255, 215, 80)
    pink = (245, 120, 130)

    bx, by = 420, 780
    draw.polygon([(bx - 35, by), (bx + 35, by), (bx, by - 30)], fill=(80, 85, 95))
    draw.line([(bx, by - 30), (bx, 310)], fill=white, width=5)

    # Scale tilt rocking equation with damping
    tilt = spring(cur_t - 21.0, start=0.0, target=12.0, stiffness=75.0, damping=8.0)

    x1, y1 = 250, int(310 - tilt)
    x2, y2 = 590, int(310 + tilt)
    draw.line([(x1, y1), (x2, y2)], fill=white, width=5)

    # Left tray (Peace & Energy)
    draw.line([(x1, y1), (x1 - 50, y1 + 80)], fill=white, width=3)
    draw.line([(x1, y1), (x1 + 50, y1 + 80)], fill=white, width=3)
    draw.line([(x1 - 60, y1 + 80), (x1 + 60, y1 + 80)], fill=white, width=4)
    cx, cy = x1, y1 + 45
    brain_glow = 1.0 + math.sin(cur_t * 4.0) * 0.08
    draw.arc([cx - int(35 * brain_glow), cy - int(25 * brain_glow), cx + int(35 * brain_glow), cy + int(20 * brain_glow)], start=0, end=360, fill=(200, 100, 150), width=5)
    draw.line([(cx, cy - 20), (cx, cy + 20)], fill=(200, 100, 150), width=4)
    draw.text((x1 - 60, y1 + 95), "peace &", font=font_chalk, fill=yellow)
    draw.text((x1 - 60, y1 + 125), "energy", font=font_chalk, fill=yellow)

    # Right tray (Asking 'Do they like me?')
    draw.line([(x2, y2), (x2 - 50, y2 + 80)], fill=white, width=3)
    draw.line([(x2, y2), (x2 + 50, y2 + 80)], fill=white, width=3)
    draw.line([(x2 - 60, y2 + 80), (x2 + 60, y2 + 80)], fill=white, width=4)
    px, py = x2, y2 + 48
    draw.polygon([(px, py - 30), (px - 22, py + 18), (px + 22, py + 18)], outline=white, fill=(230, 80, 80))
    draw.polygon([(px, py - 16), (px - 14, py + 5), (px + 14, py + 5)], fill=(245, 170, 60))
    draw.text((x2 - 75, y2 + 100), "do they like me?", font=font_chalk, fill=pink)

    draw_animated_stickman(draw, 140, 780, pose="hand_on_chin", emotion="serious", t=cur_t)


def render_scene_4(draw, cur_t, font_chalk):
    white = (240, 240, 240)
    pink = (235, 140, 170)
    yellow = (255, 215, 80)

    # Pink card spring drop: "stop fighting for attention"
    c1_y = int(spring(cur_t - 35.0, start=60.0, target=140.0, stiffness=120.0, damping=14.0))
    draw.rounded_rectangle([150, c1_y, 570, c1_y + 65], radius=10, outline=pink, width=3)
    draw.text((170, c1_y + 15), "stop fighting for attention", font=font_chalk, fill=white)
    draw.arc([570, c1_y + 10, 610, c1_y + 50], start=270, end=90, fill=pink, width=3)

    # Yellow card: "match effort with effort"
    if cur_t >= 37.0:
        c2_y = int(spring(cur_t - 37.0, start=150.0, target=225.0, stiffness=120.0, damping=14.0))
        draw.rounded_rectangle([160, c2_y, 560, c2_y + 65], radius=10, outline=yellow, width=3)
        draw.text((180, c2_y + 15), "match effort with effort", font=font_chalk, fill=white)
        draw.rectangle([510, c2_y + 65, 530, c2_y + 87], fill=(120, 210, 130))

    if cur_t >= 38.5:
        curve_prog = min(1.0, (cur_t - 38.5) / 1.5)
        all_points = []
        for px in range(390, 610, 5):
            t = (px - 500) / 100.0
            py = 520 + (t ** 2) * 150
            all_points.append((px, py))
        
        num_pts = int(len(all_points) * curve_prog)
        for i in range(num_pts - 1):
            draw.line([all_points[i], all_points[i + 1]], fill=white, width=4)

        if curve_prog > 0.6:
            draw.text((410, 690), "silent respect", font=font_chalk, fill=yellow)

    draw_animated_stickman(draw, 220, 780, pose="hand_on_chin", emotion="serious", t=cur_t)


def render_scene_5(draw, cur_t, font_chalk):
    walk_prog = min(1.0, (cur_t - 47.0) / 2.0)
    male_x = int(160 + (270 - 160) * spring(walk_prog, start=0.0, target=1.0, stiffness=80.0, damping=14.0))
    female_x = int(560 - (560 - 450) * spring(walk_prog, start=0.0, target=1.0, stiffness=80.0, damping=14.0))

    pose = "walking" if walk_prog < 0.95 else "stand"
    emotion = "serious" if walk_prog < 0.95 else "peaceful"

    if walk_prog >= 0.8:
        aura_prog = spring(cur_t - 48.6, start=0.0, target=1.0, stiffness=140.0, damping=14.0)
        draw_progressive_line(draw, (220, 520), (320, 520), aura_prog, fill=(110, 160, 230), width=4)
        draw_progressive_line(draw, (400, 520), (500, 520), aura_prog, fill=(235, 140, 170), width=4)

    if cur_t >= 53.0:
        draw.text((150, 120), "CHOSEN, EVERY SINGLE DAY.", font=font_chalk, fill=(255, 215, 80))
        p = spring(cur_t - 53.2, start=0.0, target=1.0, stiffness=130.0, damping=14.0)
        draw_progressive_line(draw, (140, 165), (580, 165), p, fill=(255, 215, 80), width=4)

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

    # Ambient drifting motes in dark atmosphere
    draw_floating_motes(draw, cur_t, w, h)

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

    # Circular brand logo badge in top right corner
    badge_path = "assets/branding/chalk_mind_badge.png"
    if os.path.exists(badge_path):
        badge = Image.open(badge_path).convert("RGBA")
        img.paste(badge, (w - badge.width - 30, 40), badge)

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
    print("🎬 RENDERING FRAMER-MOTION PSYCHOLOGY STICKMAN REEL (v3)")
    print("Features: Spring Physics, Progressive Chalk Drawing, Floating Motes")
    print("Audio: Deep Christopher Baritone + Emotional Piano/Heartbeat BGM")
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
    print(f"\n[2/4] Rendering {total_frames} frames with spring physics & ambient motes...")

    transitions = [
        (11.6, 12.0),
        (19.6, 20.0),
        (34.6, 35.0),
        (46.6, 47.0)
    ]

    for f_idx in range(total_frames):
        cur_t = f_idx / fps
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
            blend_w = ease_in_out(trans_alpha)
            img = Image.blend(img_from, img_to, blend_w)
        else:
            img = render_scene_at_time(cur_t, w, h, font_chalk)

        draw = ImageDraw.Draw(img)
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

    print("\n[3/4] Mixing deep voiceover with emotional piano & heartbeat BGM...")
    bgm_path = Path("assets/audio/bgm/bgm_psychology.wav")

    filter_complex = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]volume=0.12,atrim=0:{total_dur},afade=t=out:st={total_dur-3}:d=3[bgm];"
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
    print("🎉 1-MINUTE FRAMER-MOTION PSYCHOLOGY REEL (v3) READY!")
    print(f"📁 Video:    {output_path}")
    print(f"⏱️ Duration: {total_dur:.1f} seconds | Resolution: 720x1280 (9:16)")
    print("=" * 70)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate Framer-Motion 1-Minute Psychology Stickman Reel.")
    parser.add_argument("--output", default="output/reels/psychology_reel_01.mp4", help="Output file path")
    args = parser.parse_args()

    render_psychology_reel(output_path=args.output)


if __name__ == "__main__":
    main()
