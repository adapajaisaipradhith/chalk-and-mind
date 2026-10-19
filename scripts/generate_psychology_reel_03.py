import os
import sys
import math
import subprocess
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# =============================================================================
# CHALK & MIND — REEL #3: PURE 2D CARTOON NARRATIVE (STYLE 4 COZY STORY)
# Topic: "The Psychology of The 'Strong One' (Why Hyper-Independence is Trauma)"
# Brand: Chalk & Mind (@chalk.mind)
# Focus: ZERO top text clutter, 100% Rich 2D Animated Action, Props & Deep Audio
# =============================================================================

def run_cmd(cmd, desc):
    print(f"--> {desc}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Error in {desc}:")
        print(res.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return res.stdout

def spring(t_elapsed, start=0.0, target=1.0, stiffness=140.0, damping=14.0):
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

# -----------------------------------------------------------------------------
# GRAPHICS & ATMOSPHERIC ENVIRONMENT RENDERING
# -----------------------------------------------------------------------------
def draw_gradient_vertical(draw, w, h, top_color, bot_color, y_start=0, y_end=1280):
    span = max(1, y_end - y_start)
    for y in range(y_start, y_end, 2):
        t = (y - y_start) / span
        r = int(top_color[0] * (1 - t) + bot_color[0] * t)
        g = int(top_color[1] * (1 - t) + bot_color[1] * t)
        b = int(top_color[2] * (1 - t) + bot_color[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b), width=2)

def draw_light_cone(draw, apex_x, apex_y, base_y, left_x, right_x, color=(255, 210, 110, 45)):
    draw.polygon([(apex_x, apex_y), (left_x, base_y), (right_x, base_y)], fill=color)

def draw_rain_window(draw, cur_t, box=(60, 180, 320, 560)):
    x1, y1, x2, y2 = box
    draw.rectangle([x1, y1, x2, y2], fill=(12, 18, 30), outline=(60, 75, 95), width=4)
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2
    draw.line([(mid_x, y1), (mid_x, y2)], fill=(50, 65, 85), width=3)
    draw.line([(x1, mid_y), (x2, mid_y)], fill=(50, 65, 85), width=3)
    
    random.seed(42)
    for i in range(28):
        rx = random.uniform(x1 + 6, x2 - 6)
        ry_base = random.uniform(y1 + 6, y2 - 6)
        drop_y = (ry_base + cur_t * 95.0 + i * 14.0) % (y2 - y1 - 12) + y1 + 6
        drop_len = random.uniform(8, 16)
        draw.line([(rx, drop_y), (rx - 2, drop_y + drop_len)], fill=(160, 190, 225, 140), width=2)

# -----------------------------------------------------------------------------
# 2D CARTOON CHARACTER SYSTEM (HERO SCALE: 1.6x LARGER & HIGHLY EXPRESSIVE)
# -----------------------------------------------------------------------------
def draw_cartoon_character(draw, x, y, pose="stand", emotion="serious", t=0.0, is_companion=False, scale=1.45):
    white = (252, 252, 255)
    black = (24, 26, 32)
    amber = (255, 170, 50)
    sweater_color = (205, 185, 160) if is_companion else (42, 52, 46)  # Warm beige for companion, charcoal-olive for protagonist

    # Breathing micro-movement
    breath_bob = math.sin(t * 3.4 + (1.2 if is_companion else 0.0)) * (2.5 * scale)
    head_y = y - int(255 * scale) + breath_bob
    head_r = int(28 * scale)

    # 1. Solid White-Filled Head
    draw.ellipse([(x - head_r, head_y - head_r), (x + head_r, head_y + head_r)], fill=white, outline=black, width=int(3 * scale))

    # 2. Sketched Cartoon Hair
    if is_companion:
        draw.arc([(x - head_r - 2, head_y - head_r - 4), (x + head_r + 2, head_y + 4)], start=160, end=380, fill=black, width=int(5 * scale))
        draw.line([(x - head_r, head_y - 8), (x - head_r - 8, head_y + 16)], fill=black, width=int(4 * scale))
        draw.line([(x + head_r, head_y - 8), (x + head_r + 8, head_y + 16)], fill=black, width=int(4 * scale))
    else:
        draw.arc([(x - head_r - 2, head_y - head_r - 4), (x + head_r + 2, head_y + 2)], start=170, end=370, fill=black, width=int(5 * scale))
        draw.line([(x - head_r + 2, head_y - 14), (x - head_r - 6, head_y + 8)], fill=black, width=int(4 * scale))

    # 3. Expressive Eyes & Brows with Blinking Cycle (every 3.8s)
    blink_cycle = (t + (0.5 if is_companion else 0.0)) % 3.8
    is_blinking = blink_cycle < 0.12

    eye_offset_x = int(10 * scale)
    eye_offset_y = int(2 * scale)
    eye_lx, eye_rx = x - eye_offset_x, x + eye_offset_x
    eye_y = head_y - eye_offset_y

    if is_blinking:
        draw.line([(eye_lx - int(5 * scale), eye_y), (eye_lx + int(5 * scale), eye_y)], fill=black, width=int(2 * scale))
        draw.line([(eye_rx - int(5 * scale), eye_y), (eye_rx + int(5 * scale), eye_y)], fill=black, width=int(2 * scale))
    else:
        if emotion == "peaceful":
            draw.arc([(eye_lx - int(5 * scale), eye_y - int(5 * scale)), (eye_lx + int(5 * scale), eye_y + int(2 * scale))], start=180, end=360, fill=black, width=int(3 * scale))
            draw.arc([(eye_rx - int(5 * scale), eye_y - int(5 * scale)), (eye_rx + int(5 * scale), eye_y + int(2 * scale))], start=180, end=360, fill=black, width=int(3 * scale))
            draw.arc([(x - int(8 * scale), head_y + int(8 * scale)), (x + int(8 * scale), head_y + int(18 * scale))], start=0, end=180, fill=black, width=int(2 * scale))
        elif emotion == "straining":
            # Gritted teeth and determined furrowed brows under heavy load
            draw.line([(eye_lx - int(5 * scale), eye_y - int(3 * scale)), (eye_lx + int(5 * scale), eye_y + int(1 * scale))], fill=black, width=int(3 * scale))
            draw.line([(eye_rx - int(5 * scale), eye_y + int(1 * scale)), (eye_rx + int(5 * scale), eye_y - int(3 * scale))], fill=black, width=int(3 * scale))
            # Gritted teeth smile
            draw.rounded_rectangle([x - int(9 * scale), head_y + int(9 * scale), x + int(9 * scale), head_y + int(17 * scale)], radius=int(3 * scale), fill=white, outline=black, width=2)
            # Sweat drop flying off forehead
            sw_y = head_y - int(10 * scale) + int((t * 20) % 20)
            draw.ellipse([(x - head_r - int(6 * scale), sw_y), (x - head_r - int(1 * scale), sw_y + int(8 * scale))], fill=(160, 210, 255))
        else:
            # Thoughtful introspective almond eyes
            draw.ellipse([(eye_lx - int(3 * scale), eye_y - int(3 * scale)), (eye_lx + int(3 * scale), eye_y + int(3 * scale))], fill=black)
            draw.ellipse([(eye_rx - int(3 * scale), eye_y - int(3 * scale)), (eye_rx + int(3 * scale), eye_y + int(3 * scale))], fill=black)
            draw.line([(eye_lx - int(5 * scale), eye_y - int(7 * scale)), (eye_lx + int(5 * scale), eye_y - int(6 * scale))], fill=black, width=int(2 * scale))
            draw.line([(eye_rx - int(5 * scale), eye_y - int(6 * scale)), (eye_rx + int(5 * scale), eye_y - int(7 * scale))], fill=black, width=int(2 * scale))
            draw.line([(x - int(6 * scale), head_y + int(14 * scale)), (x + int(6 * scale), head_y + int(14 * scale))], fill=black, width=int(2 * scale))

    # 4. Clothed Torso
    neck_y = head_y + head_r
    shoulder_y = neck_y + int(12 * scale)
    hip_y = shoulder_y + int(75 * scale)

    sweater_points = [
        (x - int(20 * scale), shoulder_y),
        (x + int(20 * scale), shoulder_y),
        (x + int(24 * scale), hip_y),
        (x - int(24 * scale), hip_y)
    ]
    draw.polygon(sweater_points, fill=sweater_color, outline=black, width=int(2 * scale))
    draw.polygon([(x - int(9 * scale), shoulder_y), (x + int(9 * scale), shoulder_y), (x, shoulder_y + int(12 * scale))], fill=white, outline=black, width=int(2 * scale))

    # Glowing heart core
    if not is_companion:
        pulse = 0.5 * (1.0 + math.sin(t * 4.2))
        core_r = int((6 + 2 * pulse) * scale)
        draw.ellipse([(x - core_r, shoulder_y + int(28 * scale) - core_r), (x + core_r, shoulder_y + int(28 * scale) + core_r)], fill=(amber[0], amber[1], amber[2], 220))

    # 5. Arms, Hands & Poses
    arm_w = int(4 * scale)
    if pose == "sitting_bench":
        draw.line([(x - int(18 * scale), shoulder_y + 4), (x - int(20 * scale), shoulder_y + int(50 * scale))], fill=black, width=arm_w)
        draw.line([(x - int(20 * scale), shoulder_y + int(50 * scale)), (x - int(4 * scale), hip_y)], fill=black, width=arm_w)
        draw.line([(x + int(18 * scale), shoulder_y + 4), (x + int(20 * scale), shoulder_y + int(50 * scale))], fill=black, width=arm_w)
        draw.line([(x + int(20 * scale), shoulder_y + int(50 * scale)), (x + int(4 * scale), hip_y)], fill=black, width=arm_w)
        draw.ellipse([(x - int(10 * scale), hip_y - int(6 * scale)), (x - int(2 * scale), hip_y + int(2 * scale))], fill=white, outline=black)
        draw.ellipse([(x + int(2 * scale), hip_y - int(6 * scale)), (x + int(10 * scale), hip_y + int(2 * scale))], fill=white, outline=black)

        # Sitting legs
        knee_x_l, knee_x_r = x - int(28 * scale), x + int(28 * scale)
        knee_y = hip_y + int(22 * scale)
        draw.line([(x - int(16 * scale), hip_y), (knee_x_l, knee_y)], fill=black, width=arm_w)
        draw.line([(x + int(16 * scale), hip_y), (knee_x_r, knee_y)], fill=black, width=arm_w)
        draw.line([(knee_x_l, knee_y), (knee_x_l, y)], fill=black, width=arm_w)
        draw.line([(knee_x_r, knee_y), (knee_x_r, y)], fill=black, width=arm_w)
        draw.rounded_rectangle([knee_x_l - int(8 * scale), y - int(6 * scale), knee_x_l + int(12 * scale), y + int(2 * scale)], radius=3, fill=black)
        draw.rounded_rectangle([knee_x_r - int(8 * scale), y - int(6 * scale), knee_x_r + int(12 * scale), y + int(2 * scale)], radius=3, fill=black)

    elif pose == "holding_boulders":
        # Arms bent upward in U-shape physically carrying the heavy stack
        shiver = math.sin(t * 18.0) * int(2.5 * scale)
        draw.line([(x - int(20 * scale), shoulder_y + 4), (x - int(50 * scale) + shiver, shoulder_y + int(30 * scale))], fill=black, width=arm_w)
        draw.line([(x - int(50 * scale) + shiver, shoulder_y + int(30 * scale)), (x - int(35 * scale) + shiver, shoulder_y - int(20 * scale))], fill=black, width=arm_w)
        draw.line([(x + int(20 * scale), shoulder_y + 4), (x + int(50 * scale) - shiver, shoulder_y + int(30 * scale))], fill=black, width=arm_w)
        draw.line([(x + int(50 * scale) - shiver, shoulder_y + int(30 * scale)), (x + int(35 * scale) - shiver, shoulder_y - int(20 * scale))], fill=black, width=arm_w)
        draw.ellipse([(x - int(42 * scale), shoulder_y - int(26 * scale)), (x - int(28 * scale), shoulder_y - int(14 * scale))], fill=white, outline=black)
        draw.ellipse([(x + int(28 * scale), shoulder_y - int(26 * scale)), (x + int(42 * scale), shoulder_y - int(14 * scale))], fill=white, outline=black)

        # Knees bent and shaking slightly under weight
        knee_wobble = math.sin(t * 16.0) * int(2 * scale)
        knee_x_l, knee_x_r = x - int(22 * scale) + knee_wobble, x + int(22 * scale) - knee_wobble
        knee_y = hip_y + int(40 * scale)
        draw.line([(x - int(16 * scale), hip_y), (knee_x_l, knee_y)], fill=black, width=arm_w)
        draw.line([(x + int(16 * scale), hip_y), (knee_x_r, knee_y)], fill=black, width=arm_w)
        draw.line([(knee_x_l, knee_y), (x - int(24 * scale), y)], fill=black, width=arm_w)
        draw.line([(knee_x_r, knee_y), (x + int(24 * scale), y)], fill=black, width=arm_w)
        draw.rounded_rectangle([x - int(34 * scale), y - int(6 * scale), x - int(14 * scale), y + int(2 * scale)], radius=3, fill=black)
        draw.rounded_rectangle([x + int(14 * scale), y - int(6 * scale), x + int(34 * scale), y + int(2 * scale)], radius=3, fill=black)

    elif pose == "head_bowed":
        draw.line([(x - int(20 * scale), shoulder_y + 4), (x - int(38 * scale), shoulder_y + int(30 * scale))], fill=black, width=arm_w)
        draw.line([(x - int(38 * scale), shoulder_y + int(30 * scale)), (x - int(14 * scale), head_y + int(12 * scale))], fill=black, width=arm_w)
        draw.ellipse([(x - int(18 * scale), head_y + int(4 * scale)), (x - int(8 * scale), head_y + int(16 * scale))], fill=white, outline=black)
        draw.line([(x + int(20 * scale), shoulder_y + 4), (x + int(18 * scale), hip_y - 2)], fill=black, width=arm_w)
        draw.ellipse([(x + int(14 * scale), hip_y - 6), (x + int(24 * scale), hip_y + 4)], fill=white, outline=black)

        knee_x_l, knee_x_r = x - int(28 * scale), x + int(28 * scale)
        knee_y = hip_y + int(22 * scale)
        draw.line([(x - int(16 * scale), hip_y), (knee_x_l, knee_y)], fill=black, width=arm_w)
        draw.line([(x + int(16 * scale), hip_y), (knee_x_r, knee_y)], fill=black, width=arm_w)
        draw.line([(knee_x_l, knee_y), (knee_x_l, y)], fill=black, width=arm_w)
        draw.line([(knee_x_r, knee_y), (knee_x_r, y)], fill=black, width=arm_w)

    elif pose == "slumped_knees":
        # Slumped on knees on the ground (Scene 5)
        knee_y = y - int(15 * scale)
        draw.line([(x - int(16 * scale), hip_y), (x - int(24 * scale), knee_y)], fill=black, width=arm_w)
        draw.line([(x + int(16 * scale), hip_y), (x + int(24 * scale), knee_y)], fill=black, width=arm_w)
        draw.line([(x - int(24 * scale), knee_y), (x - int(45 * scale), y)], fill=black, width=arm_w)
        draw.line([(x + int(24 * scale), knee_y), (x + int(45 * scale), y)], fill=black, width=arm_w)
        # Arms resting exhausted down to knees
        draw.line([(x - int(20 * scale), shoulder_y + 4), (x - int(26 * scale), knee_y - int(10 * scale))], fill=black, width=arm_w)
        draw.line([(x + int(20 * scale), shoulder_y + 4), (x + int(26 * scale), knee_y - int(10 * scale))], fill=black, width=arm_w)

    elif pose == "support_shoulder":
        # Companion's comforting arm resting gently on protagonist's shoulder
        draw.line([(x - int(20 * scale), shoulder_y + 4), (x - int(56 * scale), shoulder_y + int(14 * scale))], fill=black, width=arm_w)
        draw.ellipse([(x - int(64 * scale), shoulder_y + int(6 * scale)), (x - int(50 * scale), shoulder_y + int(20 * scale))], fill=white, outline=black)
        draw.line([(x + int(20 * scale), shoulder_y + 4), (x + int(18 * scale), hip_y + 10)], fill=black, width=arm_w)
        draw.line([(x - int(14 * scale), hip_y), (x - int(18 * scale), y)], fill=black, width=arm_w)
        draw.line([(x + int(14 * scale), hip_y), (x + int(18 * scale), y)], fill=black, width=arm_w)

    else:
        # Standard balanced standing
        draw.line([(x - int(20 * scale), shoulder_y + 4), (x - int(24 * scale), shoulder_y + int(60 * scale))], fill=black, width=arm_w)
        draw.line([(x + int(20 * scale), shoulder_y + 4), (x + int(24 * scale), shoulder_y + int(60 * scale))], fill=black, width=arm_w)
        draw.line([(x - int(14 * scale), hip_y), (x - int(18 * scale), y)], fill=black, width=arm_w)
        draw.line([(x + int(14 * scale), hip_y), (x + int(18 * scale), y)], fill=black, width=arm_w)

# -----------------------------------------------------------------------------
# SUBTITLE PARSER
# -----------------------------------------------------------------------------
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
# SCENE 1 (0.0s - 10.3s): DUSK PARK BENCH UNDER STREETLIGHT
# Zero top text. Pure 2D visual storytelling.
# -----------------------------------------------------------------------------
def render_scene_1(draw, cur_t):
    # Deep twilight to indigo gradient
    draw_gradient_vertical(draw, 720, 1280, (11, 15, 28), (24, 32, 54), y_start=0, y_end=880)

    # Distant city skyline with soft lit windows
    for cx in range(40, 700, 75):
        h_bldg = 110 + (cx % 80)
        draw.rectangle([cx - 30, 880 - h_bldg, cx + 30, 880], fill=(16, 22, 38))
        for wy in range(880 - h_bldg + 15, 860, 22):
            draw.point((cx - 10, wy), fill=(255, 215, 130, 140))
            draw.point((cx + 10, wy), fill=(255, 215, 130, 140))

    # Streetlamp at x=200
    draw.line([(200, 220), (200, 880)], fill=(40, 48, 65), width=10)
    draw.polygon([(170, 220), (230, 220), (215, 180), (185, 180)], fill=(30, 38, 52))
    draw.ellipse([(185, 215), (215, 245)], fill=(255, 220, 120))
    # Wide volumetric light cone
    draw_light_cone(draw, 200, 240, 880, 40, 580, color=(255, 210, 110, 38))

    # Park Bench at x=360, y=830
    draw.rectangle([220, 825, 500, 850], fill=(75, 52, 38), outline=(35, 25, 18), width=3)
    draw.line([(245, 850), (240, 880)], fill=(40, 48, 65), width=8)
    draw.line([(475, 850), (480, 880)], fill=(40, 48, 65), width=8)

    # Character sitting on bench holding warm coffee cup
    draw_cartoon_character(draw, 360, 880, pose="sitting_bench", emotion="serious", t=cur_t)

    # Warm coffee cup held in hands
    draw.rounded_rectangle([348, 715, 372, 740], radius=4, fill=(240, 240, 245), outline=(40, 40, 40), width=2)
    # Animated steam curls rising from cup
    st_p = (cur_t * 2.2) % 2.5
    draw.arc([(352, 690 - int(st_p * 18)), (368, 712 - int(st_p * 18))], start=180, end=360, fill=(245, 245, 255, 140), width=2)

    # Exhaled breath mist from cold air
    mist_t = (cur_t * 1.4) % 3.2
    if mist_t < 2.0:
        mx = 378 + mist_t * 26
        my = 575 - mist_t * 15
        mr = int(5 + mist_t * 8)
        draw.ellipse([(mx - mr, my - mr), (mx + mr, my + mr)], fill=(225, 238, 255, int(85 * (1 - mist_t / 2.0))))

    # Cold wind gusts with autumn leaves blowing past in foreground
    random.seed(55)
    for i in range(12):
        lx = (random.uniform(50, 700) + cur_t * 80.0 + i * 50) % 720
        ly = (random.uniform(300, 850) + math.sin(cur_t * 2.0 + i) * 30) % 850
        leaf_color = (210, 110, 50) if i % 2 == 0 else (180, 75, 40)
        draw.ellipse([(lx - 6, ly - 3), (lx + 6, ly + 3)], fill=leaf_color)

# -----------------------------------------------------------------------------
# SCENE 2 (10.3s - 23.9s): COZY CAFÉ & BEARING HEAVY PROBLEM BOULDERS
# Zero top text. Visible strain, physical cartoon burdens stacking up!
# -----------------------------------------------------------------------------
def render_scene_2(draw, cur_t):
    # Warm mahogany coffee shop background
    draw_gradient_vertical(draw, 720, 1280, (38, 26, 20), (58, 40, 30), y_start=0, y_end=880)

    # Industrial Edison bulb hanging pendants
    for lx in [120, 600]:
        draw.line([(lx, 0), (lx, 260)], fill=(30, 20, 15), width=3)
        draw.ellipse([(lx - 14, 260), (lx + 14, 290)], fill=(255, 195, 95, 220), outline=(255, 225, 140))
        draw.ellipse([(lx - 60, 225), (lx + 60, 325)], fill=(255, 185, 80, 28))

    # Character in center holding heavy stack
    draw_cartoon_character(draw, 360, 880, pose="holding_boulders", emotion="straining", t=cur_t)

    # Stack of heavy cartoon problem boulders accumulating:
    # 1st Boulder arrives at 13.2s
    if cur_t >= 13.2:
        b1_prog = spring(cur_t - 13.2, start=0.2, target=1.0, stiffness=160.0, damping=13.0)
        b1_w, b1_h = int(140 * b1_prog), int(60 * b1_prog)
        draw.rounded_rectangle([360 - b1_w // 2, 600 - b1_h // 2, 360 + b1_w // 2, 600 + b1_h // 2], radius=14, fill=(80, 90, 105), outline=(30, 35, 45), width=3)
        # Cracks on boulder
        draw.line([(340, 585), (355, 605), (370, 595)], fill=(50, 60, 75), width=2)

    # 2nd Boulder drops onto the stack at 16.0s
    if cur_t >= 16.0:
        b2_prog = spring(cur_t - 16.0, start=0.2, target=1.0, stiffness=160.0, damping=13.0)
        b2_w, b2_h = int(120 * b2_prog), int(55 * b2_prog)
        draw.rounded_rectangle([360 - b2_w // 2, 535 - b2_h // 2, 360 + b2_w // 2, 535 + b2_h // 2], radius=12, fill=(110, 95, 85), outline=(40, 35, 30), width=3)

    # 3rd Heavy Boulder drops at 19.2s
    if cur_t >= 19.2:
        b3_prog = spring(cur_t - 19.2, start=0.2, target=1.0, stiffness=160.0, damping=13.0)
        b3_w, b3_h = int(105 * b3_prog), int(50 * b3_prog)
        draw.rounded_rectangle([360 - b3_w // 2, 475 - b3_h // 2, 360 + b3_w // 2, 475 + b3_h // 2], radius=10, fill=(135, 80, 80), outline=(50, 25, 25), width=3)

# -----------------------------------------------------------------------------
# SCENE 3 (23.9s - 29.8s): MIDNIGHT BEDROOM, RAINY WINDOW & BLANK PHONE
# Zero top text. Moody, poignant, quiet vulnerability.
# -----------------------------------------------------------------------------
def render_scene_3(draw, cur_t):
    # Deep midnight navy room gradient
    draw_gradient_vertical(draw, 720, 1280, (10, 14, 24), (18, 24, 40), y_start=0, y_end=880)

    # Rainy Window on left (x: 60 to 320, y: 180 to 560)
    draw_rain_window(draw, cur_t, box=(60, 180, 320, 560))

    # Bed / Mattress on right
    draw.rectangle([260, 810, 700, 880], fill=(32, 42, 60), outline=(50, 62, 85), width=3)
    # Pillow
    draw.rounded_rectangle([580, 785, 680, 825], radius=10, fill=(60, 75, 100))

    # Character sitting on bed edge, head bowed in hands
    draw_cartoon_character(draw, 360, 880, pose="head_bowed", emotion="serious", t=cur_t)

    # Smartphone resting on mattress next to him
    phone_x, phone_y = 500, 815
    draw.rounded_rectangle([phone_x, phone_y, phone_x + 65, phone_y + 40], radius=8, fill=(15, 20, 30), outline=(60, 70, 90), width=2)
    # Phone screen illuminated with faint cold blue light (blank lockscreen)
    draw.rounded_rectangle([phone_x + 5, phone_y + 5, phone_x + 60, phone_y + 35], radius=4, fill=(28, 38, 55))
    # Clock icon / zero notifications
    draw.point((phone_x + 32, phone_y + 20), fill=(180, 200, 230))

# -----------------------------------------------------------------------------
# SCENE 4 (29.8s - 48.0s): TWILIGHT CLIFF & HEAVY STONE FORTRESS
# Heavy masonry blocks encase the character, heavy iron padlock over heart!
# -----------------------------------------------------------------------------
def render_scene_4(draw, cur_t):
    amber = (255, 170, 50)
    # Twilight violet sky
    draw_gradient_vertical(draw, 720, 1280, (20, 14, 32), (45, 30, 60), y_start=0, y_end=880)

    # Jagged cliff silhouette below
    draw.polygon([(0, 880), (720, 880), (720, 940), (0, 940)], fill=(32, 25, 42))

    # Character stands firm at center
    draw_cartoon_character(draw, 360, 880, pose="stand", emotion="serious", t=cur_t)

    # Heavy Stone Fortress Blocks rising around the character at 38s
    if cur_t >= 38.0:
        fort_prog = spring(cur_t - 38.0, start=0.0, target=1.0, stiffness=120.0, damping=14.0)
        sw = int(120 * fort_prog)
        if sw > 0:
            fx1, fy1, fx2, fy2 = 360 - sw, 520, 360 + sw, 875
            # Stone wall texture
            draw.rounded_rectangle([fx1, fy1, fx2, fy2], radius=18, fill=(40, 48, 62, 180), outline=(130, 140, 160), width=5)
            # Brick mortar lines
            for by in range(580, 870, 55):
                draw.line([(fx1, by), (fx2, by)], fill=(90, 100, 120), width=3)
            # Battlements at top
            draw.rectangle([fx1 - 8, fy1 - 18, fx1 + 25, fy1], fill=(130, 140, 160))
            draw.rectangle([fx2 - 25, fy1 - 18, fx2 + 8, fy1], fill=(130, 140, 160))
            draw.rectangle([345, fy1 - 18, 375, fy1], fill=(130, 140, 160))

    # Massive Golden Padlock locks shut over heart at 42s
    if cur_t >= 42.0:
        p_prog = spring(cur_t - 42.0, start=0.1, target=1.0, stiffness=150.0, damping=13.0)
        pw = int(48 * p_prog)
        draw.rounded_rectangle([360 - pw // 2, 650, 360 + pw // 2, 700], radius=8, fill=(55, 62, 78), outline=amber, width=3)
        draw.arc([(348, 628), (372, 655)], start=180, end=360, fill=amber, width=4)

# -----------------------------------------------------------------------------
# SCENE 5 (48.0s - 54.8s): CRACKING STONE & THE ZERO-VOLUME DROP
# Stones shatter into floating golden stardust. Absolute acoustic dead silence.
# -----------------------------------------------------------------------------
def render_scene_5(draw, cur_t):
    amber = (255, 170, 50)
    draw_gradient_vertical(draw, 720, 1280, (18, 14, 26), (36, 26, 48), y_start=0, y_end=880)

    # Cracking fissures
    dissolve_prog = min(1.0, max(0.0, (cur_t - 48.0) / 4.5))
    # Glowing cracks
    draw.line([(310, 530), (335, 610), (320, 710), (345, 820)], fill=(255, 215, 110), width=4)
    draw.line([(410, 540), (385, 620), (400, 720), (375, 830)], fill=(255, 215, 110), width=4)

    # Shattered golden stardust motes floating gently up
    random.seed(88)
    for i in range(45):
        sx = random.uniform(250, 470)
        sy_base = random.uniform(520, 850)
        sy = sy_base - dissolve_prog * 150.0
        sr = random.choice([2, 3, 4, 5])
        draw.ellipse([(sx - sr, sy - sr), (sx + sr, sy + sr)], fill=(amber[0], amber[1], amber[2], int(200 * dissolve_prog)))

    # Character drops to slumped knees, exhaling
    draw_cartoon_character(draw, 360, 880, pose="slumped_knees", emotion="serious", t=cur_t)

# -----------------------------------------------------------------------------
# SCENE 6 (54.8s - 63.8s): GOLDEN DAWN HORIZON & THE SAFE HARBOR COMPANION
# Radiant sunrise, companion's hand on shoulder, peaceful smiling eyes!
# -----------------------------------------------------------------------------
def render_scene_6(draw, cur_t):
    # Radiant sunrise horizon: morning indigo to warm coral, gold and amber
    draw_gradient_vertical(draw, 720, 1280, (25, 40, 70), (255, 155, 85), y_start=0, y_end=880)

    # Soft glowing morning clouds
    draw.ellipse([(40, 740), (340, 840)], fill=(255, 200, 150, 95))
    draw.ellipse([(360, 720), (680, 830)], fill=(255, 210, 160, 95))

    # Balcony Railing at y=850
    draw.line([(40, 850), (680, 850)], fill=(45, 35, 30), width=8)
    for rx in range(80, 660, 65):
        draw.line([(rx, 850), (rx, 880)], fill=(45, 35, 30), width=5)

    # Warm radiant halo around both characters
    draw.ellipse([(180, 500), (540, 860)], fill=(255, 220, 130, 30))

    # Two figures side-by-side:
    # 1. The Strong One at x=300 (peaceful curved smile)
    draw_cartoon_character(draw, 300, 880, pose="stand", emotion="peaceful", t=cur_t, is_companion=False)
    # 2. The Safe Harbor Companion at x=420 (warm hand on shoulder, curved smile)
    draw_cartoon_character(draw, 420, 880, pose="support_shoulder", emotion="peaceful", t=cur_t, is_companion=True)

# -----------------------------------------------------------------------------
# SUBTITLE RENDERER (LOWER THIRD: y=920 to 1060)
# Clean, bold, with radiant amber active-word karaoke lighting
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
        if (bbox[2] - bbox[0]) > 540:
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

    white = (252, 252, 255)
    amber = (255, 175, 50)
    space_w = font_sub.getbbox(" ")[2] - font_sub.getbbox(" ")[0]
    line_h = 54
    start_y = 960 - ((len(lines) - 1) * line_h) // 2

    # Draw subtle dark soft pill behind subtitle for crisp contrast against any background
    sub_box_top = start_y - 12
    sub_box_bot = start_y + len(lines) * line_h + 8
    draw.rounded_rectangle([40, sub_box_top, width - 40, sub_box_bot], radius=16, fill=(10, 12, 18, 180))

    word_idx = 0
    for l_idx, line_words in enumerate(lines):
        total_w = sum(font_sub.getbbox(w)[2] - font_sub.getbbox(w)[0] for w in line_words) + (len(line_words) - 1) * space_w
        pos_x = (width - total_w) // 2
        pos_y = start_y + l_idx * line_h
        cur_x = pos_x

        for w in line_words:
            w_w = font_sub.getbbox(w)[2] - font_sub.getbbox(w)[0]
            is_active = (word_idx == active_idx) or (word_idx == len(words) - 1 and elapsed > sub_dur * 0.75)
            color = amber if is_active else white
            draw.text((cur_x, pos_y), w, font=font_sub, fill=color)
            if is_active:
                underline_y = pos_y + 48
                draw.line([(cur_x - 2, underline_y), (cur_x + w_w + 2, underline_y)], fill=amber, width=4)
            cur_x += w_w + space_w
            word_idx += 1

# -----------------------------------------------------------------------------
# MAIN COMPOSITOR
# -----------------------------------------------------------------------------
def render_scene_at_time(cur_t, w, h):
    img = Image.new("RGB", (w, h), color=(14, 18, 28))
    draw = ImageDraw.Draw(img)

    # 1. Render Active 2D Cartoon Scene
    if cur_t < 10.3:
        render_scene_1(draw, cur_t)
    elif cur_t < 23.9:
        render_scene_2(draw, cur_t)
    elif cur_t < 29.8:
        render_scene_3(draw, cur_t)
    elif cur_t < 48.0:
        render_scene_4(draw, cur_t)
    elif cur_t < 54.8:
        render_scene_5(draw, cur_t)
    else:
        render_scene_6(draw, cur_t)

    # Official Brand Watermark Emblem in Top-Right Corner
    badge_path = "assets/branding/chalk_mind_badge.png"
    if os.path.exists(badge_path):
        badge = Image.open(badge_path).convert("RGBA")
        img.paste(badge, (w - badge.width - 25, 35), badge)

    return img

# -----------------------------------------------------------------------------
# FULL RENDER & EXPORT PIPELINE
# -----------------------------------------------------------------------------
def render_reel_03():
    os.makedirs("output/reels", exist_ok=True)
    temp_dir = Path("output/temp/reel_03")
    temp_frames = temp_dir / "frames"
    temp_frames.mkdir(parents=True, exist_ok=True)

    vo_vtt = temp_dir / "voice.vtt"
    mastered_audio = temp_dir / "mastered_cinematic_audio.aac"

    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(mastered_audio)]
    total_dur = float(subprocess.check_output(dur_cmd).decode().strip())
    subtitles = parse_vtt_timestamps(vo_vtt)

    font_path = "assets/online_vault/fonts/Kalam-Bold.ttf"
    if not os.path.exists(font_path):
        font_path = "assets/fonts/PatrickHand-Regular.ttf"
    font_sub = ImageFont.truetype(font_path, 44)

    fps = 30
    total_frames = int(total_dur * fps)
    w, h = 720, 1280

    print(f"🎬 RENDERING REEL #3 (PURE 2D ANIMATION — ZERO TOP TEXT — {total_frames} frames)...")

    for f_idx in range(total_frames):
        cur_t = f_idx / fps
        frame_img = render_scene_at_time(cur_t, w, h)
        
        # Lower-third viral subtitles
        draw_sub = ImageDraw.Draw(frame_img)
        draw_subtitles(draw_sub, cur_t, subtitles, w, h, font_sub)

        frame_path = temp_frames / f"frame_{f_idx:05d}.png"
        frame_img.save(frame_path)

        if f_idx % 250 == 0:
            print(f"   Rendered frame {f_idx}/{total_frames} ({cur_t:.1f}s / {total_dur:.1f}s)...")

    raw_video = temp_dir / "raw_video.mp4"
    print("--> Encoding video frames...")
    enc_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(temp_frames / "frame_%05d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "fast",
        str(raw_video)
    ]
    run_cmd(enc_cmd, "Encoding video frames")

    # Mux with the mastered multi-track audio mix (voice + Moonlight Sonata + SFX)
    final_reel = Path("output/reels/psychology_reel_03.mp4")
    print("--> Exporting final Reel #3 with mastered audio...")
    export_cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(mastered_audio),
        "-c:v", "copy",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(final_reel)
    ]
    run_cmd(export_cmd, "Muxing final video and audio")

    print(f"\n🎉 REEL #3 COMPLETED: {final_reel}")

if __name__ == "__main__":
    render_reel_03()
