import os
import sys
import math
import subprocess
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))
from character_hoodie import draw_hoodie_guy

def run_cmd(cmd, desc):
    print(f"--> {desc}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Error in {desc}:")
        print(res.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return res.stdout

def spring(t_elapsed, start=0.0, target=1.0, stiffness=130.0, damping=14.0):
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
    vx, vy = dx / dist, dy / dist
    cur = 0
    while cur < dist:
        start_d = cur
        end_d = min(cur + dash_len, dist)
        draw.line([(x1 + vx * start_d, y1 + vy * start_d), (x1 + vx * end_d, y1 + vy * end_d)], fill=fill, width=width)
        cur += dash_len + gap_len

def draw_floating_motes(draw, t, width=720, height=1280):
    random.seed(42)
    for i in range(18):
        base_x = random.uniform(30, width - 30)
        base_y = random.uniform(60, height - 120)
        speed = random.uniform(10, 26)
        radius = random.uniform(1.5, 3.2)
        y = (base_y - t * speed) % (height - 80) + 40
        x = base_x + math.sin(t * 1.3 + i) * 14
        alpha = int(40 + math.sin(t * 2.2 + i) * 22)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(225, 230, 240, alpha))

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

# -----------------------------------------------------------------------------
# SCENE 1 (0.0s - 8.5s): PURSUING vs CHASING & REACHING OUT
# -----------------------------------------------------------------------------
def render_scene_1(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    green = (80, 215, 120)
    red = (235, 75, 75)
    dim = (160, 165, 175)

    # 1. Top Contrast Cards (Pursuing vs Chasing)
    # Green Card: PURSUING (pops at 0.3s)
    if cur_t >= 0.3:
        p_scale = spring(cur_t - 0.3, start=0.4, target=1.0, stiffness=140.0, damping=13.0)
        bw, bh = int(220 * p_scale), int(55 * p_scale)
        bx = 170 - bw // 2
        by = 130 - bh // 2
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, outline=green, width=3)
        if p_scale > 0.7:
            draw.text((bx + 25, by + 10), "PURSUING", font=font_chalk, fill=green)

    # "vs" in center (pops at 1.0s)
    if cur_t >= 1.0:
        draw.text((345, 115), "vs", font=font_chalk, fill=dim)

    # Red Card: CHASING (pops at 1.5s)
    if cur_t >= 1.5:
        c_scale = spring(cur_t - 1.5, start=0.4, target=1.0, stiffness=140.0, damping=13.0)
        bw, bh = int(220 * c_scale), int(55 * c_scale)
        bx = 550 - bw // 2
        by = 130 - bh // 2
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, outline=red, width=3)
        if c_scale > 0.7:
            draw.text((bx + 35, by + 10), "CHASING", font=font_chalk, fill=red)

    # 2. Reaching Out Animation (3.5s to 8.5s)
    pose = "hands_in_pockets"
    look = (0.2, -0.4)
    char_x = 240

    if cur_t >= 3.5:
        pose = "pointing"
        look = (0.7, -0.2)

        # Message 1 pops at 4.0s
        if cur_t >= 4.0:
            m1_prog = spring(cur_t - 4.0, start=0.2, target=1.0, stiffness=150.0, damping=14.0)
            if m1_prog > 0.6:
                draw.rounded_rectangle([320, 260, 520, 315], radius=10, fill=(28, 32, 42), outline=white, width=2)
                draw.text((340, 272), "Hey, are you free?", font=font_small, fill=white)

        # Message 2 pops at 5.4s
        if cur_t >= 5.4:
            m2_prog = spring(cur_t - 5.4, start=0.2, target=1.0, stiffness=150.0, damping=14.0)
            if m2_prog > 0.6:
                draw.rounded_rectangle([330, 335, 540, 390], radius=10, fill=(28, 32, 42), outline=white, width=2)
                draw.text((350, 347), "Did you see this?", font=font_small, fill=white)

        # "Zero Interest" stamp drops on right at 6.8s
        if cur_t >= 6.8:
            stamp_y = int(spring(cur_t - 6.8, start=380.0, target=450.0, stiffness=160.0, damping=13.0))
            draw.rounded_rectangle([360, stamp_y, 630, stamp_y + 60], radius=8, outline=red, width=3)
            draw.text((385, stamp_y + 12), "[ 0% INTEREST ]", font=font_chalk, fill=red)
            draw.text((410, stamp_y + 70), "Read 11:42 PM • No reply", font=font_small, fill=dim)

    # Draw our signature Bald Hoodie Guy
    draw_hoodie_guy(draw, char_x, 740, pose=pose, emotion="thoughtful", look_dir=look, t=cur_t, scale=1.3)

# -----------------------------------------------------------------------------
# SCENE 2 (8.5s - 20.0s): EMOTIONALLY INTELLIGENT OBSERVE & CARRY WEIGHT
# -----------------------------------------------------------------------------
def render_scene_2(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    gold = (255, 215, 80)
    red = (235, 75, 75)
    dim = (160, 165, 175)

    # 1. "Don't Chase" X Mark at 8.8s
    if cur_t < 14.0:
        draw.text((120, 110), "EMOTIONALLY INTELLIGENT:", font=font_small, fill=dim)
        draw.text((120, 145), "DON'T CHASE", font=font_chalk, fill=red)
        if cur_t >= 9.2:
            x_prog = min(1.0, (cur_t - 9.2) / 0.3)
            draw_progressive_line(draw, (110, 150), (320, 185), x_prog, fill=red, width=5)
            draw_progressive_line(draw, (320, 150), (110, 185), x_prog, fill=red, width=5)

    # 2. "They Observe" Golden Reveal at 12.0s
    if 12.0 <= cur_t < 14.5:
        eye_y = int(spring(cur_t - 12.0, start=180.0, target=230.0, stiffness=150.0, damping=13.0))
        draw.ellipse([340, eye_y - 20, 380, eye_y + 20], outline=gold, width=3)
        draw.ellipse([355, eye_y - 8, 365, eye_y + 8], fill=gold)
        draw.text((280, eye_y + 35), "THEY OBSERVE", font=font_chalk, fill=gold)
        underline_prog = spring(cur_t - 12.3, start=0.0, target=1.0, stiffness=140.0, damping=15.0)
        draw_progressive_line(draw, (260, eye_y + 75), (460, eye_y + 75), underline_prog, fill=gold, width=4)

    # 3. "Carry All The Weight" Imbalanced Scale at 14.5s
    if cur_t >= 14.2:
        draw.text((180, 100), "A GENUINE CONNECTION", font=font_chalk, fill=white)
        draw.text((150, 140), "Doesn't require one person to carry all weight", font=font_small, fill=dim)

        bx, by = 420, 740
        draw.polygon([(bx - 30, by), (bx + 30, by), (bx, by - 30)], fill=(70, 75, 85))
        draw.line([(bx, by - 30), (bx, 360)], fill=white, width=5)

        # Scale rocking equation with severe tilt to left (heavy burden)
        tilt = spring(cur_t - 14.8, start=0.0, target=22.0, stiffness=70.0, damping=8.0)
        x1, y1 = 250, int(360 + tilt * 2)  # Left heavy
        x2, y2 = 590, int(360 - tilt * 2)  # Right light

        draw.line([(x1, y1), (x2, y2)], fill=white, width=5)

        # Left tray: YOUR EFFORT (Heavy 100%)
        draw.line([(x1, y1), (x1 - 45, y1 + 75)], fill=white, width=3)
        draw.line([(x1, y1), (x1 + 45, y1 + 75)], fill=white, width=3)
        draw.line([(x1 - 55, y1 + 75), (x1 + 55, y1 + 75)], fill=white, width=4)
        draw.rounded_rectangle([x1 - 40, y1 + 25, x1 + 40, y1 + 75], radius=6, fill=red, outline=white, width=2)
        draw.text((x1 - 32, y1 + 38), "100%", font=font_chalk, fill=white)
        draw.text((x1 - 55, y1 + 90), "YOUR EFFORT", font=font_small, fill=red)

        # Right tray: THEIR EFFORT (Empty 0%)
        draw.line([(x2, y2), (x2 - 45, y2 + 75)], fill=white, width=3)
        draw.line([(x2, y2), (x2 + 45, y2 + 75)], fill=white, width=3)
        draw.line([(x2 - 55, y2 + 75), (x2 + 55, y2 + 75)], fill=white, width=4)
        draw.text((x2 - 15, y2 + 35), "0%", font=font_chalk, fill=dim)
        draw.text((x2 - 60, y2 + 90), "THEIR EFFORT", font=font_small, fill=dim)

    # Bald Hoodie Guy: thoughtful observing pose
    char_pose = "thoughtful_chin" if cur_t < 14.5 else "hands_in_pockets"
    look = (0.4, -0.3)
    draw_hoodie_guy(draw, 170, 740, pose=char_pose, emotion="thoughtful", look_dir=look, t=cur_t, scale=1.2)

# -----------------------------------------------------------------------------
# SCENE 3 (20.0s - 30.7s): THE TWO QUESTIONS & PEACE / ENERGY
# -----------------------------------------------------------------------------
def render_scene_3(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    gold = (255, 215, 80)
    red = (235, 75, 75)
    cyan = (110, 180, 245)
    dim = (160, 165, 175)

    # 1. Question 1: "Do they like me?" (pops at 20.2s, crossed out at 21.6s)
    if cur_t >= 20.2:
        q1_y = int(spring(cur_t - 20.2, start=80.0, target=140.0, stiffness=140.0, damping=13.0))
        draw.rounded_rectangle([100, q1_y, 620, q1_y + 70], radius=10, outline=red, width=3)
        draw.text((130, q1_y + 16), "❌ Instead of: 'Do they like me?'", font=font_chalk, fill=red)
        if cur_t >= 21.6:
            strike = min(1.0, (cur_t - 21.6) / 0.3)
            draw_progressive_line(draw, (90, q1_y + 35), (630, q1_y + 35), strike, fill=red, width=5)

    # 2. Question 2: "Do I actually like them?" (pops with gold at 23.5s)
    if cur_t >= 23.5:
        q2_y = int(spring(cur_t - 23.5, start=180.0, target=240.0, stiffness=140.0, damping=13.0))
        draw.rounded_rectangle([100, q2_y, 620, q2_y + 70], radius=10, outline=gold, width=3)
        draw.text((130, q2_y + 16), "✨ Step back: 'Do I actually like them?'", font=font_chalk, fill=gold)

    # 3. Peace & Energy Gauges (slide in at 27.2s)
    if cur_t >= 27.2:
        draw.text((140, 360), "IS THIS CONNECTION WORTHY OF:", font=font_small, fill=dim)

        # Peace Gauge
        draw.text((140, 400), "MY PEACE", font=font_chalk, fill=cyan)
        p_w = int(spring(cur_t - 27.2, start=0.0, target=320.0, stiffness=120.0, damping=14.0))
        draw.rounded_rectangle([290, 405, 610, 435], radius=6, outline=cyan, width=2)
        if p_w > 0:
            draw.rounded_rectangle([292, 407, 290 + min(318, p_w), 433], radius=4, fill=cyan)

        # Energy Gauge
        if cur_t >= 28.2:
            draw.text((140, 460), "MY ENERGY", font=font_chalk, fill=gold)
            e_w = int(spring(cur_t - 28.2, start=0.0, target=320.0, stiffness=120.0, damping=14.0))
            draw.rounded_rectangle([290, 465, 610, 495], radius=6, outline=gold, width=2)
            if e_w > 0:
                draw.rounded_rectangle([292, 467, 290 + min(318, e_w), 493], radius=4, fill=gold)

    # Bald Hoodie Guy: serene, thoughtful smile
    draw_hoodie_guy(draw, 360, 740, pose="hands_in_pockets", emotion="thoughtful", look_dir=(0.2, -0.4), t=cur_t, scale=1.35)

# -----------------------------------------------------------------------------
# SCENE 4 (30.7s - 40.2s): VALUE YOURSELF & WALK AWAY WITH SILENT RESPECT
# -----------------------------------------------------------------------------
def render_scene_4(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    gold = (255, 215, 80)
    red = (235, 75, 75)
    green = (80, 215, 120)
    dim = (160, 165, 175)

    # 1. Stop Fighting For Attention (30.7s)
    if cur_t < 35.5:
        draw.text((160, 120), "WHEN YOU TRULY VALUE YOURSELF", font=font_small, fill=dim)
        draw.text((140, 160), "STOP FIGHTING FOR ATTENTION", font=font_chalk, fill=red)
        if cur_t >= 32.0:
            strike = min(1.0, (cur_t - 32.0) / 0.3)
            draw_progressive_line(draw, (130, 185), (590, 185), strike, fill=red, width=5)
            draw.text((250, 215), "CHOOSE SELF-RESPECT", font=font_chalk, fill=gold)

    # 2. Match Effort with Effort & Silent Respect (35.4s - 40.2s)
    char_x = 360
    char_pose = "hands_in_pockets"

    if cur_t >= 35.4:
        draw.text((180, 130), "MATCH EFFORT WITH EFFORT", font=font_chalk, fill=green)
        
        # Two balanced meeting arrows
        arrow_prog = spring(cur_t - 35.6, start=0.0, target=1.0, stiffness=130.0, damping=14.0)
        draw_progressive_line(draw, (180, 190), (320, 190), arrow_prog, fill=green, width=4)
        draw_progressive_line(draw, (320, 190), (305, 180), arrow_prog, fill=green, width=4)
        draw_progressive_line(draw, (320, 190), (305, 200), arrow_prog, fill=green, width=4)

        draw_progressive_line(draw, (540, 190), (400, 190), arrow_prog, fill=green, width=4)
        draw_progressive_line(draw, (400, 190), (415, 180), arrow_prog, fill=green, width=4)
        draw_progressive_line(draw, (400, 190), (415, 200), arrow_prog, fill=green, width=4)

        draw.text((335, 175), "⚖️", font=font_chalk, fill=white)

        if cur_t >= 37.0:
            draw.text((160, 245), "WALK AWAY WITH SILENT RESPECT", font=font_chalk, fill=white)
            underline_prog = spring(cur_t - 37.3, start=0.0, target=1.0, stiffness=140.0, damping=14.0)
            draw_progressive_line(draw, (150, 285), (570, 285), underline_prog, fill=gold, width=4)
            # Character walks calmly to right
            char_pose = "walking"
            walk_drift = (cur_t - 37.0) * 45
            char_x = 360 + int(walk_drift)

    draw_hoodie_guy(draw, char_x, 740, pose=char_pose, emotion="thoughtful", look_dir=(0.5, -0.2), t=cur_t, scale=1.3)

# -----------------------------------------------------------------------------
# SCENE 5 (40.2s - 57.5s): TWO-WAY STREET & CHOSEN EVERY DAY (INFINITE LOOP)
# -----------------------------------------------------------------------------
def render_scene_5(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    gold = (255, 215, 80)
    red = (235, 75, 75)
    dim = (160, 165, 175)

    # 1. Two-Way Street (40.2s - 46.5s)
    if cur_t < 46.5:
        draw.text((160, 100), "REAL CONNECTION IS A TWO-WAY STREET", font=font_small, fill=dim)
        
        # Road outline
        draw.line([(100, 170), (620, 170)], fill=white, width=4)
        draw.line([(100, 270), (620, 270)], fill=white, width=4)
        draw_dashed_line(draw, (100, 220), (620, 220), fill=dim, width=3)

        # Arrows: GIVING vs RECEIVING
        draw.text((140, 180), "GIVING  → → →", font=font_chalk, fill=white)
        draw.text((380, 230), "← ← ←  RECEIVING", font=font_chalk, fill=white)

        if cur_t >= 43.0:
            stamp_scale = spring(cur_t - 43.0, start=0.5, target=1.0, stiffness=150.0, damping=13.0)
            if stamp_scale > 0.6:
                draw.rounded_rectangle([180, 310, 540, 370], radius=8, outline=red, width=3)
                draw.text((220, 322), "NEVER BEG FOR LOVE", font=font_chalk, fill=red)

    # 2. Chosen Every Single Day (46.5s - 57.5s)
    if cur_t >= 46.5:
        draw.text((120, 110), "RESPECT YOURSELF ENOUGH", font=font_small, fill=dim)
        draw.text((120, 145), "NEVER SETTLE FOR ONE-SIDED EFFORT", font=font_chalk, fill=white)

        if cur_t >= 50.8:
            # Golden aura blooming behind character
            aura_scale = spring(cur_t - 50.8, start=0.0, target=1.0, stiffness=110.0, damping=15.0)
            aura_r = int(140 * aura_scale)
            if aura_r > 0:
                draw.ellipse([360 - aura_r, 470 - aura_r, 360 + aura_r, 470 + aura_r], outline=gold, width=3)

        if cur_t >= 53.5:
            draw.text((160, 230), "A HEALTHY CONNECTION IS NEVER CHASED", font=font_small, fill=dim)
            draw.text((150, 265), "IT IS CHOSEN, EVERY SINGLE DAY.", font=font_chalk, fill=gold)
            prog = spring(cur_t - 53.8, start=0.0, target=1.0, stiffness=140.0, damping=14.0)
            draw_progressive_line(draw, (140, 310), (580, 310), prog, fill=gold, width=4)

        if cur_t >= 55.0:
            draw.text((180, 340), "✨ Send this to someone who needs this", font=font_small, fill=white)

    # Bald Hoodie Guy standing centered, calm, dignified
    draw_hoodie_guy(draw, 360, 740, pose="hands_in_pockets", emotion="thoughtful", look_dir=(0.0, -0.3), t=cur_t, scale=1.35)

# -----------------------------------------------------------------------------
# SUBTITLE RENDERER (WORD-BY-WORD KINETIC GOLDEN HIGHLIGHT)
# -----------------------------------------------------------------------------
def draw_subtitles(draw, cur_t, subtitles, width, height, font_sub):
    active = None
    for sub in subtitles:
        if sub["start"] <= cur_t <= sub["end"]:
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
    elapsed = cur_t - active["start"]
    active_idx = min(len(words) - 1, int((elapsed / sub_dur) * len(words)))

    white = (245, 245, 245)
    yellow = (255, 215, 75)
    space_w = font_sub.getbbox(" ")[2] - font_sub.getbbox(" ")[0]
    line_h = 52
    start_y = 860 - ((len(lines) - 1) * line_h) // 2

    word_idx = 0
    for l_idx, line_words in enumerate(lines):
        total_w = sum(font_sub.getbbox(w)[2] - font_sub.getbbox(w)[0] for w in line_words) + (len(line_words) - 1) * space_w
        pos_x = (width - total_w) // 2
        pos_y = start_y + l_idx * line_h
        cur_x = pos_x

        for w in line_words:
            w_w = font_sub.getbbox(w)[2] - font_sub.getbbox(w)[0]
            is_active = (word_idx == active_idx) or (word_idx == len(words) - 1 and elapsed > sub_dur * 0.75)
            color = yellow if is_active else white
            draw.text((cur_x, pos_y), w, font=font_sub, fill=color)
            if is_active:
                underline_y = pos_y + 45
                draw.line([(cur_x - 2, underline_y), (cur_x + w_w + 2, underline_y)], fill=yellow, width=4)
            cur_x += w_w + space_w
            word_idx += 1

def render_scene_at_time(cur_t, w, h, font_chalk, font_small):
    img = Image.new("RGB", (w, h), color=(11, 12, 14))
    draw = ImageDraw.Draw(img)

    # Ambient floating dust motes
    draw_floating_motes(draw, cur_t, w, h)

    # Chalk ground baseline
    draw.line([(40, 780), (680, 780)], fill=(245, 245, 245), width=4)

    if cur_t < 8.5:
        render_scene_1(draw, cur_t, font_chalk, font_small)
    elif cur_t < 20.0:
        render_scene_2(draw, cur_t, font_chalk, font_small)
    elif cur_t < 30.7:
        render_scene_3(draw, cur_t, font_chalk, font_small)
    elif cur_t < 40.2:
        render_scene_4(draw, cur_t, font_chalk, font_small)
    else:
        render_scene_5(draw, cur_t, font_chalk, font_small)

    return img

def render_remastered_reel():
    os.makedirs("output/reels", exist_ok=True)
    temp_dir = Path("output/temp/psychology_reel")
    temp_frames = temp_dir / "frames_remastered"
    temp_frames.mkdir(parents=True, exist_ok=True)

    vo_mp3 = temp_dir / "voice.mp3"
    vo_vtt = temp_dir / "voice.vtt"

    if not vo_mp3.exists() or not vo_vtt.exists():
        raise FileNotFoundError("voice.mp3 or voice.vtt not found in temp dir")

    # Get duration
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(vo_mp3)]
    total_dur = float(subprocess.check_output(dur_cmd).decode().strip())
    subtitles = parse_vtt_timestamps(vo_vtt)

    font_path = "assets/fonts/PatrickHand-Regular.ttf"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

    font_chalk = ImageFont.truetype(font_path, 36)
    font_small = ImageFont.truetype(font_path, 26)
    font_sub = ImageFont.truetype(font_path, 42)

    w, h = 720, 1280
    fps = 30
    total_frames = int(total_dur * fps)

    print(f"🎬 RENDERING REMASTERED REEL 1 WITH HOODIE GUY & MILLISECOND VOICE-SYNC ({total_frames} frames)...")

    transitions = [
        (8.2, 8.5),
        (19.6, 20.0),
        (30.3, 30.7),
        (39.8, 40.2)
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
            img_from = render_scene_at_time(t_before, w, h, font_chalk, font_small)
            img_to = render_scene_at_time(t_after, w, h, font_chalk, font_small)
            blend_w = ease_in_out(trans_alpha)
            img = Image.blend(img_from, img_to, blend_w)
        else:
            img = render_scene_at_time(cur_t, w, h, font_chalk, font_small)

        draw = ImageDraw.Draw(img)
        draw_subtitles(draw, cur_t, subtitles, w, h, font_sub)

        frame_file = temp_frames / f"frame_{f_idx:05d}.png"
        img.save(frame_file)

        if f_idx % 150 == 0:
            print(f"   Rendered frame {f_idx}/{total_frames} ({cur_t:.1f}s / {total_dur:.1f}s)...")

    raw_video = temp_dir / "raw_video_remastered.mp4"
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

    print("🎵 Mixing voiceover and soundtrack with tactical ducking...")
    bgm_path = Path("assets/audio/bgm/bgm_psychology.wav")
    final_output = Path("output/reels/psychology_reel_01_remastered.mp4")

    filter_complex = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]volume=0.13,atrim=0:{total_dur},afade=t=out:st={total_dur-3}:d=3[bgm];"
        f"[voice][bgm]amix=inputs=2:duration=first[aout]"
    )

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
        "-shortest",
        str(final_output)
    ], "Exporting final remastered reel")

    print(f"\n🎉 MASTER REEL COMPLETED: {final_output}")

if __name__ == "__main__":
    render_remastered_reel()
