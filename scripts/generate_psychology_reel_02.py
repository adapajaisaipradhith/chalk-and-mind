import os
import sys
import math
import subprocess
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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
    random.seed(84)
    for i in range(16):
        base_x = random.uniform(30, width - 30)
        base_y = random.uniform(60, height - 120)
        speed = random.uniform(10, 26)
        radius = random.uniform(1.5, 3.0)
        y = (base_y - t * speed) % (height - 80) + 40
        x = base_x + math.sin(t * 1.3 + i) * 14
        alpha = int(40 + math.sin(t * 2.2 + i) * 22)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(225, 230, 240, alpha))

def draw_clean_stickman(draw, x, y, pose="stand", emotion="serious", is_female=False, t=0.0):
    """
    Renders clean, perfectly proportioned white chalk stick figure.
    x, y: Ground contact point (feet level at y=800)
    Height: 214px total (Head top at y-214)
    """
    white = (245, 245, 245)
    w = 4

    bob = math.sin(t * 3.5) * 2.0
    hx = x
    hy = y - 180 + bob
    head_r = 34

    # Head
    draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], outline=white, width=w)

    # Hair sway physics for female
    if is_female:
        hair_sway = math.sin(t * 3.0) * 3.0
        draw.arc([hx - 44 + hair_sway, hy - 20, hx - 16 + hair_sway, hy + 46], start=80, end=270, fill=white, width=w)
        draw.arc([hx + 16 + hair_sway, hy - 20, hx + 44 + hair_sway, hy + 46], start=270, end=100, fill=white, width=w)

    # Blinking logic (blink every 3.8s for 0.12s)
    blink_cycle = (t % 3.8)
    is_blinking = (blink_cycle < 0.12)

    if is_blinking:
        draw.line([(hx - 16, hy - 4), (hx - 8, hy - 4)], fill=white, width=3)
        draw.line([(hx + 8, hy - 4), (hx + 16, hy - 4)], fill=white, width=3)
        draw.arc([hx - 10, hy + 8, hx + 10, hy + 18], start=0, end=180, fill=white, width=3)
    elif emotion == "peaceful" or is_female:
        draw.arc([hx - 18, hy - 14, hx - 6, hy + 2], start=180, end=360, fill=white, width=3)
        draw.arc([hx + 6, hy - 14, hx + 18, hy + 2], start=180, end=360, fill=white, width=3)
        draw.arc([hx - 12, hy + 8, hx + 12, hy + 20], start=0, end=180, fill=white, width=3)
    else:
        # Reflective / thoughtful
        draw.line([(hx - 18, hy - 14), (hx - 6, hy - 8)], fill=white, width=3)
        draw.line([(hx + 6, hy - 8), (hx + 18, hy - 14)], fill=white, width=3)
        draw.ellipse([hx - 14, hy - 4, hx - 10, hy], fill=white)
        draw.ellipse([hx + 10, hy - 4, hx + 14, hy], fill=white)
        draw.line([(hx - 8, hy + 14), (hx + 8, hy + 14)], fill=white, width=3)

    # Spine
    neck_y = hy + head_r
    hip_y = neck_y + 115
    draw.line([(hx, neck_y), (hx, hip_y)], fill=white, width=w)

    # Arms
    shoulder_y = neck_y + 20
    if pose == "arms_crossed":
        draw.line([(hx, shoulder_y), (hx - 26, shoulder_y + 25)], fill=white, width=w)
        draw.line([(hx - 26, shoulder_y + 25), (hx + 18, shoulder_y + 25)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 26, shoulder_y + 25)], fill=white, width=w)
        draw.line([(hx + 26, shoulder_y + 25), (hx - 18, shoulder_y + 25)], fill=white, width=w)
    elif pose == "hand_on_chin":
        draw.line([(hx, shoulder_y), (hx - 22, shoulder_y + 45)], fill=white, width=w)
        draw.line([(hx - 22, shoulder_y + 45), (hx - 4, hip_y)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 26, shoulder_y + 35)], fill=white, width=w)
        draw.line([(hx + 26, shoulder_y + 35), (hx + 12, hy + 18)], fill=white, width=w)
    elif pose == "holding_inner":
        # Gently reach toward partner
        reach_dir = -1 if hx > 360 else 1
        draw.line([(hx, shoulder_y), (hx + reach_dir * 35, shoulder_y + 40)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx - reach_dir * 20, shoulder_y + 50)], fill=white, width=w)
    elif pose == "walking":
        walk_swing = math.sin(t * 7.0) * 20
        draw.line([(hx, shoulder_y), (hx - 22 - walk_swing, shoulder_y + 48)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 22 + walk_swing, shoulder_y + 48)], fill=white, width=w)
    else:
        # Relaxed standing
        draw.line([(hx, shoulder_y), (hx - 22, shoulder_y + 55)], fill=white, width=w)
        draw.line([(hx, shoulder_y), (hx + 22, shoulder_y + 55)], fill=white, width=w)

    # Legs
    if pose == "walking":
        walk_leg = math.sin(t * 7.0) * 22
        draw.line([(hx, hip_y), (hx - 16 + walk_leg, y)], fill=white, width=w)
        draw.line([(hx, hip_y), (hx + 16 - walk_leg, y)], fill=white, width=w)
    else:
        draw.line([(hx, hip_y), (hx - 16, y)], fill=white, width=w)
        draw.line([(hx, hip_y), (hx + 16, y)], fill=white, width=w)

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
# SCENE 1 (0.0s - 8.4s): SPLIT SCREEN CONTRAST HOOK (ZERO OVERLAP)
# -----------------------------------------------------------------------------
def render_scene_1(draw, cur_t, font_chalk, font_small):
    pink = (235, 140, 170)
    blue = (110, 160, 230)
    dim = (160, 165, 175)

    # Center vertical dividing line (strict boundaries)
    div_prog = min(1.0, cur_t / 0.5)
    draw_dashed_line(draw, (360, 120), (360, int(120 + 660 * div_prog)), fill=dim, width=3)

    # Left: Female Card in Zone A (x: 40 to 330, y: 150)
    if cur_t >= 0.4:
        p_scale = spring(cur_t - 0.4, start=0.4, target=1.0, stiffness=140.0, damping=13.0)
        bw, bh = int(280 * p_scale), int(55 * p_scale)
        bx = 180 - bw // 2
        by = 160 - bh // 2
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, outline=pink, width=3)
        if p_scale > 0.7:
            draw.text((bx + 20, by + 12), "A WOMAN'S PAIN", font=font_small, fill=pink)
            draw.text((bx + 15, by + 65), "Loud until total silence", font=font_small, fill=dim)

    # Right: Male Card in Zone A (x: 390 to 680, y: 160)
    if cur_t >= 4.7:
        m_scale = spring(cur_t - 4.7, start=0.4, target=1.0, stiffness=140.0, damping=13.0)
        bw, bh = int(280 * m_scale), int(55 * m_scale)
        bx = 540 - bw // 2
        by = 160 - bh // 2
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, outline=blue, width=3)
        if m_scale > 0.7:
            draw.text((bx + 25, by + 12), "A MAN'S PAIN", font=font_small, fill=blue)
            draw.text((bx + 20, by + 65), "Silent from day one", font=font_small, fill=dim)

    # Characters in Zone B (ground y=800)
    draw_clean_stickman(draw, 180, 800, pose="stand", emotion="serious", is_female=True, t=cur_t)
    draw_clean_stickman(draw, 540, 800, pose="arms_crossed", emotion="serious", t=cur_t)

# -----------------------------------------------------------------------------
# SCENE 2 (8.4s - 27.9s): THE PSYCHOLOGY OF HER SILENCE (SPACIOUS LAYOUT)
# -----------------------------------------------------------------------------
def render_scene_2(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    pink = (235, 140, 170)
    red = (235, 75, 75)
    green = (80, 215, 120)
    dim = (160, 165, 175)

    # Female stick figure on left (x=180, y=800)
    draw_clean_stickman(draw, 180, 800, pose="stand", emotion="serious", is_female=True, t=cur_t)

    # Part 1 (8.4s to 20.0s): Questions & Fighting to save connection
    if cur_t < 20.0:
        draw.text((120, 120), "WHEN A GIRL IS HURT:", font=font_small, fill=dim)
        draw.text((120, 155), "SHE QUESTIONS • TALKS • FIGHTS", font=font_chalk, fill=pink)

        # 3 Clean Speech Cards (Zone A, x: 300 to 650)
        if cur_t >= 9.2:
            s1 = spring(cur_t - 9.2, start=0.2, target=1.0, stiffness=150.0, damping=13.0)
            if s1 > 0.6:
                draw.rounded_rectangle([300, 230, 640, 285], radius=10, fill=(28, 30, 38), outline=white, width=2)
                draw.text((320, 242), "Why don't we talk anymore?", font=font_small, fill=white)

        if cur_t >= 11.5:
            s2 = spring(cur_t - 11.5, start=0.2, target=1.0, stiffness=150.0, damping=13.0)
            if s2 > 0.6:
                draw.rounded_rectangle([300, 305, 640, 360], radius=10, fill=(28, 30, 38), outline=white, width=2)
                draw.text((320, 317), "Do you even care about us?", font=font_small, fill=white)

        if cur_t >= 14.5:
            draw.text((300, 395), "NOT DRAMATIC:", font=font_small, fill=dim)
            draw.text((300, 425), "SAVING THE CONNECTION", font=font_chalk, fill=green)

    # Part 2 (20.0s to 27.9s): The Battery Drain & Checking Out
    if cur_t >= 20.0:
        draw.text((120, 120), "THE DAY SHE STOPS ARGUING:", font=font_small, fill=dim)
        draw.text((120, 155), "SHE DIDN'T BECOME PEACEFUL.", font=font_chalk, fill=white)

        # Battery in Zone A (x: 280 to 620, y: 240)
        bx, by = 450, 250
        draw.rounded_rectangle([bx - 140, by, bx + 140, by + 55], radius=8, outline=white, width=3)
        draw.rectangle([bx + 140, by + 16, bx + 152, by + 38], fill=white)

        # Drain equation from 20.5s to 24.0s
        bat_prog = min(1.0, max(0.0, 1.0 - (cur_t - 20.5) / 3.5))
        fill_w = int(274 * bat_prog)
        bat_color = green if bat_prog > 0.5 else (red if bat_prog < 0.25 else (255, 215, 80))
        if fill_w > 0:
            draw.rounded_rectangle([bx - 137, by + 3, bx - 137 + fill_w, by + 52], radius=6, fill=bat_color)

        draw.text((bx - 80, by + 68), f"EMOTIONAL CAPACITY: {int(bat_prog * 100)}%", font=font_small, fill=bat_color)

        if cur_t >= 24.5:
            stamp_scale = spring(cur_t - 24.5, start=0.5, target=1.0, stiffness=150.0, damping=13.0)
            if stamp_scale > 0.6:
                draw.rounded_rectangle([280, 370, 660, 435], radius=10, outline=red, width=3)
                draw.text((305, 385), "EMOTIONALLY CHECKED OUT", font=font_chalk, fill=red)

# -----------------------------------------------------------------------------
# SCENE 3 (27.9s - 43.8s): THE BOY'S BURDEN & 2:00 AM CEILING (CLEAN GAP)
# -----------------------------------------------------------------------------
def render_scene_3(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    gold = (255, 215, 80)
    red = (235, 75, 75)
    dim = (160, 165, 175)

    # Titles in Zone A (well above character head)
    draw.text((120, 120), "FOR MEN, SUFFERING OUT LOUD", font=font_small, fill=dim)
    draw.text((120, 155), "WAS LABELED AS 'WEAKNESS'", font=font_chalk, fill=red)

    # Burden Card in Zone A (y: 230 to 320) - DOES NOT TOUCH CHARACTER
    if cur_t >= 29.5:
        b_y = int(spring(cur_t - 29.5, start=160.0, target=240.0, stiffness=120.0, damping=14.0))
        draw.rounded_rectangle([180, b_y, 540, b_y + 70], radius=10, fill=(35, 38, 48), outline=white, width=3)
        draw.text((220, b_y + 18), "HEAVY EXPECTATIONS", font=font_chalk, fill=white)
        # Downward pressure arrows pointing to character
        draw_progressive_line(draw, (360, b_y + 75), (360, b_y + 115), 1.0, fill=dim, width=3)
        draw.line([(350, b_y + 105), (360, b_y + 115)], fill=dim, width=3)
        draw.line([(370, b_y + 105), (360, b_y + 115)], fill=dim, width=3)

    # 2:00 AM Ceiling & Clock (y: 380 to 480)
    if cur_t >= 37.5:
        # Subtle wall clock in top-right area of Zone A
        cx, cy, cr = 580, 390, 36
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=dim, width=3)
        # Hour hand pointing to 2, minute hand to 12
        draw.line([(cx, cy), (cx + 18, cy - 10)], fill=white, width=3)
        draw.line([(cx, cy), (cx, cy - 25)], fill=white, width=3)

        draw.text((100, 380), "SMILES AT WORK ALL DAY...", font=font_small, fill=dim)
        draw.text((100, 415), "2:00 AM: 'WHERE DID I GO WRONG?'", font=font_chalk, fill=gold)
        underline_prog = spring(cur_t - 38.5, start=0.0, target=1.0, stiffness=140.0, damping=14.0)
        draw_progressive_line(draw, (95, 460), (620, 460), underline_prog, fill=gold, width=4)

    # Character stands at x=360, y=800 (Head top is at y=586, perfectly clear of y=460)
    draw_clean_stickman(draw, 360, 800, pose="hand_on_chin", emotion="serious", t=cur_t)

# -----------------------------------------------------------------------------
# SCENE 4 (43.8s - 49.2s): PAIN HAS NO GENDER (NO ACCIDENTAL CIRCLES!)
# -----------------------------------------------------------------------------
def render_scene_4(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    gold = (255, 215, 80)
    dim = (160, 165, 175)

    # Clean titles in Zone A
    draw.text((140, 140), "PAIN DOESN'T CARE ABOUT GENDER", font=font_small, fill=dim)
    draw.text((140, 180), "IT ONLY ASKS TO BE HEARD.", font=font_chalk, fill=gold)
    p = spring(cur_t - 44.5, start=0.0, target=1.0, stiffness=130.0, damping=14.0)
    draw_progressive_line(draw, (130, 225), (590, 225), p, fill=gold, width=4)

    # Gentle golden heart between them (NO HUGE CIRCLE IN THE MIDDLE)
    if cur_t >= 45.0:
        h_scale = spring(cur_t - 45.0, start=0.2, target=1.0, stiffness=140.0, damping=13.0)
        if h_scale > 0.5:
            draw.text((345, 620), "💛", font=font_chalk, fill=gold)

    # Both figures step closer together cleanly without merging
    step = min(1.0, (cur_t - 44.0) / 1.8)
    mx = int(220 + 70 * step)  # 220 -> 290
    fx = int(500 - 70 * step)  # 500 -> 430 (clean 140px gap between them!)

    draw_clean_stickman(draw, mx, 800, pose="stand", emotion="peaceful", t=cur_t)
    draw_clean_stickman(draw, fx, 800, pose="stand", emotion="peaceful", is_female=True, t=cur_t)

# -----------------------------------------------------------------------------
# SCENE 5 (49.2s - 56.1s): ASK THEM WHAT BROKE (CLEAN RESOLUTION & LOOP)
# -----------------------------------------------------------------------------
def render_scene_5(draw, cur_t, font_chalk, font_small):
    white = (245, 245, 245)
    gold = (255, 215, 80)
    red = (235, 75, 75)
    dim = (160, 165, 175)

    draw.text((120, 120), "IF SOMEONE YOU LOVE HAS GONE QUIET:", font=font_small, fill=dim)

    # Strikethrough on peace
    draw.text((120, 160), "DON'T CELEBRATE THE PEACE", font=font_chalk, fill=red)
    if cur_t >= 50.4:
        strike = min(1.0, (cur_t - 50.4) / 0.3)
        draw_progressive_line(draw, (110, 185), (570, 185), strike, fill=red, width=5)

    # Climax reveal in gold
    if cur_t >= 52.2:
        draw.text((160, 240), "ASK THEM WHAT BROKE.", font=font_chalk, fill=gold)
        prog = spring(cur_t - 52.5, start=0.0, target=1.0, stiffness=140.0, damping=14.0)
        draw_progressive_line(draw, (150, 285), (550, 285), prog, fill=gold, width=4)

    if cur_t >= 53.8:
        draw.text((150, 340), "✨ Send this to someone who needs to be heard", font=font_small, fill=white)

    # Characters stand side-by-side with 120px gap (mx=300, fx=420)
    # Reaching gently toward each other without collision
    draw_clean_stickman(draw, 300, 800, pose="holding_inner", emotion="peaceful", t=cur_t)
    draw_clean_stickman(draw, 420, 800, pose="holding_inner", emotion="peaceful", is_female=True, t=cur_t)

# -----------------------------------------------------------------------------
# SUBTITLE RENDERER
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
    start_y = 870 - ((len(lines) - 1) * line_h) // 2

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

    draw_floating_motes(draw, cur_t, w, h)
    draw.line([(40, 800), (680, 800)], fill=(245, 245, 245), width=4)

    if cur_t < 8.4:
        render_scene_1(draw, cur_t, font_chalk, font_small)
    elif cur_t < 27.9:
        render_scene_2(draw, cur_t, font_chalk, font_small)
    elif cur_t < 43.8:
        render_scene_3(draw, cur_t, font_chalk, font_small)
    elif cur_t < 49.2:
        render_scene_4(draw, cur_t, font_chalk, font_small)
    else:
        render_scene_5(draw, cur_t, font_chalk, font_small)

    # Pin circular brand logo in top-right
    badge_path = "assets/branding/chalk_mind_badge.png"
    if os.path.exists(badge_path):
        badge = Image.open(badge_path).convert("RGBA")
        img.paste(badge, (w - badge.width - 25, 35), badge)

    return img

def render_reel_02():
    os.makedirs("output/reels", exist_ok=True)
    temp_dir = Path("output/temp/reel_02")
    temp_frames = temp_dir / "frames"
    temp_frames.mkdir(parents=True, exist_ok=True)

    vo_mp3 = temp_dir / "voice.mp3"
    vo_vtt = temp_dir / "voice.vtt"

    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(vo_mp3)]
    total_dur = float(subprocess.check_output(dur_cmd).decode().strip())
    subtitles = parse_vtt_timestamps(vo_vtt)

    font_path = "assets/fonts/PatrickHand-Regular.ttf"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

    font_chalk = ImageFont.truetype(font_path, 34)
    font_small = ImageFont.truetype(font_path, 24)
    font_sub = ImageFont.truetype(font_path, 42)

    w, h = 720, 1280
    fps = 30
    total_frames = int(total_dur * fps)

    print(f"🎬 RENDERING REEL #2 WITH STRICT ZERO-COLLISION ZONES ({total_frames} frames)...")

    transitions = [
        (8.1, 8.4),
        (27.5, 27.9),
        (43.4, 43.8),
        (48.8, 49.2)
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

        if f_idx % 200 == 0:
            print(f"   Rendered frame {f_idx}/{total_frames} ({cur_t:.1f}s / {total_dur:.1f}s)...")

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
    ], "Encoding video frames")

    print("🎵 Mixing voiceover and soundtrack with tactical ducking...")
    bgm_path = Path("assets/audio/bgm/bgm_psychology.wav")
    final_output = Path("output/reels/psychology_reel_02.mp4")

    filter_complex = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]volume=0.12,atrim=0:{total_dur},afade=t=out:st={total_dur-3}:d=3[bgm];"
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
    ], "Exporting final Reel #2")

    print(f"\n🎉 REEL #2 COMPLETED: {final_output}")

if __name__ == "__main__":
    render_reel_02()
