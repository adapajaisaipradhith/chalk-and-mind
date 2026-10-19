import math
import os
import random
from PIL import Image, ImageDraw

def draw_chalk_stroke(draw, points, fill=(245, 245, 245), width=4, jitter=1.2):
    """
    Draws a smooth line with micro chalk jitter for that authentic blackboard texture.
    """
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        draw.line([(x1, y1), (x2, y2)], fill=fill, width=width)
        # Subtle chalk edge roughness
        if jitter > 0:
            mid_x = (x1 + x2) / 2 + random.uniform(-jitter, jitter)
            mid_y = (y1 + y2) / 2 + random.uniform(-jitter, jitter)
            draw.line([(x1, y1), (mid_x, mid_y)], fill=(fill[0], fill[1], fill[2], 120), width=max(1, width - 1))

def draw_hoodie_guy(draw, x, y, pose="hands_in_pockets", emotion="thoughtful", look_dir=(0.5, -0.4), t=0.0, scale=1.35):
    """
    Programmatic renderer perfectly matching Option 2:
    - Smooth rounded bald head with high expressive forehead.
    - Soulful arched eyebrows, large reflective eyes with pupils looking up-right.
    - Gentle thoughtful half-smile and nose curve.
    - Softly sloping chalk hoodie shoulders, curved neckline, hanging drawstrings, and kangaroo pouch.
    """
    random.seed(int(t * 10) + 100)
    white = (248, 248, 250)
    dim_white = (190, 195, 205, 160)
    w = max(3, int(4.5 * scale))
    fine_w = max(2, int(2.5 * scale))

    # Breathing micro-bob & tilt
    bob_y = math.sin(t * 3.0) * (3.0 * scale)
    tilt = math.sin(t * 1.5) * 0.03  # slight head tilt angle

    head_cx = x
    head_cy = y - int(175 * scale) + bob_y
    rx = int(52 * scale)
    ry = int(58 * scale)

    # -------------------------------------------------------------
    # 1. SOFT HOODIE SHOULDERS & BODY
    # -------------------------------------------------------------
    neck_cx = head_cx
    neck_top = head_cy + ry - int(12 * scale)
    neck_bot = neck_top + int(38 * scale)
    neck_half_w = int(18 * scale)

    # Neck
    draw.line([(neck_cx - neck_half_w, neck_top), (neck_cx - neck_half_w, neck_bot)], fill=white, width=w)
    draw.line([(neck_cx + neck_half_w, neck_top), (neck_cx + neck_half_w, neck_bot)], fill=white, width=w)

    # Curved natural shoulders
    shoulder_left = (neck_cx - int(105 * scale), neck_bot + int(48 * scale))
    shoulder_right = (neck_cx + int(105 * scale), neck_bot + int(48 * scale))
    bottom_left = (neck_cx - int(80 * scale), y + int(85 * scale))
    bottom_right = (neck_cx + int(80 * scale), y + int(85 * scale))

    # Natural shoulder slopes
    left_slope = [
        (neck_cx - neck_half_w - int(8 * scale), neck_bot + int(10 * scale)),
        (neck_cx - int(55 * scale), neck_bot + int(24 * scale)),
        shoulder_left
    ]
    right_slope = [
        (neck_cx + neck_half_w + int(8 * scale), neck_bot + int(10 * scale)),
        (neck_cx + int(55 * scale), neck_bot + int(24 * scale)),
        shoulder_right
    ]
    draw.line(left_slope, fill=white, width=w)
    draw.line(right_slope, fill=white, width=w)

    # Torso sides
    draw.line([shoulder_left, bottom_left], fill=white, width=w)
    draw.line([shoulder_right, bottom_right], fill=white, width=w)

    # Chalk cross-hatch shading on hoodie (soft texture like Option 2)
    for hy in range(int(neck_bot + 45 * scale), int(y + 70 * scale), int(12 * scale)):
        cur_w = int(72 * scale)
        draw.line([(neck_cx - cur_w + (hy % 8), hy), 
                   (neck_cx + cur_w - (hy % 8), hy + int(6 * scale))], fill=dim_white, width=fine_w)

    # Relaxed hoodie collar
    collar_pts = [
        (neck_cx - neck_half_w - int(12 * scale), neck_bot + int(4 * scale)),
        (neck_cx - int(18 * scale), neck_bot + int(35 * scale)),
        (neck_cx, neck_bot + int(42 * scale)),
        (neck_cx + int(18 * scale), neck_bot + int(35 * scale)),
        (neck_cx + neck_half_w + int(12 * scale), neck_bot + int(4 * scale)),
        (neck_cx, neck_bot + int(18 * scale))
    ]
    draw.polygon(collar_pts, fill=(16, 18, 22), outline=white)
    draw.line([(neck_cx - neck_half_w - int(12 * scale), neck_bot + int(4 * scale)),
               (neck_cx, neck_bot + int(42 * scale)),
               (neck_cx + neck_half_w + int(12 * scale), neck_bot + int(4 * scale))], fill=white, width=w)

    # Drawstrings with physics swing
    sway = math.sin(t * 2.6) * (3.5 * scale)
    ds_start_y = neck_bot + int(30 * scale)
    ds_len = int(50 * scale)
    
    # Left string
    draw.line([(neck_cx - int(10 * scale), ds_start_y), 
               (neck_cx - int(12 * scale) + sway, ds_start_y + ds_len)], fill=white, width=fine_w)
    draw.ellipse([neck_cx - int(15 * scale) + sway, ds_start_y + ds_len - int(2 * scale),
                  neck_cx - int(9 * scale) + sway, ds_start_y + ds_len + int(4 * scale)], fill=white)

    # Right string
    draw.line([(neck_cx + int(10 * scale), ds_start_y), 
               (neck_cx + int(8 * scale) + sway * 0.8, ds_start_y + ds_len - int(6 * scale))], fill=white, width=fine_w)
    draw.ellipse([neck_cx + int(5 * scale) + sway * 0.8, ds_start_y + ds_len - int(8 * scale),
                  neck_cx + int(11 * scale) + sway * 0.8, ds_start_y + ds_len - int(2 * scale)], fill=white)

    # Kangaroo Pouch
    pouch_top = y + int(10 * scale)
    pouch_w = int(55 * scale)
    draw.line([(neck_cx - pouch_w + int(16 * scale), pouch_top), 
               (neck_cx + pouch_w - int(16 * scale), pouch_top)], fill=white, width=w)
    draw.line([(neck_cx - pouch_w, pouch_top + int(36 * scale)), 
               (neck_cx - pouch_w + int(16 * scale), pouch_top)], fill=white, width=w)
    draw.line([(neck_cx + pouch_w, pouch_top + int(36 * scale)), 
               (neck_cx + pouch_w - int(16 * scale), pouch_top)], fill=white, width=w)

    # Arms
    if pose == "hands_in_pockets":
        draw.line([shoulder_left, (neck_cx - pouch_w + int(6 * scale), pouch_top + int(24 * scale))], fill=white, width=w)
        draw.line([shoulder_right, (neck_cx + pouch_w - int(6 * scale), pouch_top + int(24 * scale))], fill=white, width=w)
    elif pose == "thoughtful_chin":
        draw.line([shoulder_left, (neck_cx - int(35 * scale), y + int(30 * scale))], fill=white, width=w)
        draw.line([shoulder_right, (neck_cx + int(26 * scale), head_cy + ry - int(4 * scale))], fill=white, width=w)
        draw.ellipse([neck_cx + int(20 * scale), head_cy + ry - int(12 * scale),
                      neck_cx + int(32 * scale), head_cy + ry], outline=white, width=fine_w)
    elif pose == "pointing":
        draw.line([shoulder_left, (neck_cx - pouch_w + int(6 * scale), pouch_top + int(24 * scale))], fill=white, width=w)
        elbow = (shoulder_right[0] + int(35 * scale), shoulder_right[1] - int(10 * scale))
        hand = (elbow[0] + int(50 * scale), elbow[1] - int(25 * scale))
        draw.line([shoulder_right, elbow], fill=white, width=w)
        draw.line([elbow, hand], fill=white, width=w)
        draw.line([hand, (hand[0] + int(14 * scale), hand[1] - int(4 * scale))], fill=white, width=fine_w)
    elif pose == "walking":
        arm_swing = math.sin(t * 6.5) * (18 * scale)
        draw.line([shoulder_left, (shoulder_left[0] - int(5 * scale) - int(arm_swing), bottom_left[1] - int(15 * scale))], fill=white, width=w)
        draw.line([shoulder_right, (shoulder_right[0] + int(5 * scale) + int(arm_swing), bottom_right[1] - int(15 * scale))], fill=white, width=w)
    else:
        draw.line([shoulder_left, (shoulder_left[0] - int(4 * scale), bottom_left[1] - int(15 * scale))], fill=white, width=w)
        draw.line([shoulder_right, (shoulder_right[0] + int(4 * scale), bottom_right[1] - int(15 * scale))], fill=white, width=w)

    # -------------------------------------------------------------
    # 2. BALD HEAD & FACIAL EXPRESSIONS (OPTION 2 TWIN)
    # -------------------------------------------------------------
    # Egg-shaped smooth bald head
    draw.ellipse([head_cx - rx, head_cy - ry, head_cx + rx, head_cy + ry], outline=white, width=w)

    # Cute rounded ears at eye line
    ear_r = int(12 * scale)
    draw.arc([head_cx - rx - ear_r + int(2 * scale), head_cy - int(8 * scale),
              head_cx - rx + ear_r, head_cy + int(18 * scale)], start=90, end=270, fill=white, width=w)
    draw.arc([head_cx + rx - ear_r, head_cy - int(8 * scale),
              head_cx + rx + ear_r - int(2 * scale), head_cy + int(18 * scale)], start=270, end=90, fill=white, width=w)

    # Arched, expressive eyebrows (soulful & contemplative like Option 2)
    brow_y = head_cy - int(18 * scale)
    # Left brow (arched up toward center)
    draw.arc([head_cx - int(34 * scale), brow_y - int(16 * scale),
              head_cx - int(8 * scale), brow_y + int(6 * scale)], start=190, end=340, fill=white, width=w)
    # Right brow (higher arch reflecting curiosity/deep thought)
    draw.arc([head_cx + int(8 * scale), brow_y - int(18 * scale),
              head_cx + int(36 * scale), brow_y + int(4 * scale)], start=190, end=345, fill=white, width=w)

    # Blinking logic (blink every 3.8s for 0.12s)
    blink_cycle = (t % 3.8)
    is_blinking = (blink_cycle < 0.12)

    eye_y = head_cy + int(2 * scale)
    eye_lx = head_cx - int(18 * scale)
    eye_rx = head_cx + int(20 * scale)
    eye_r_x = int(11 * scale)
    eye_r_y = int(13 * scale)

    if is_blinking:
        # Smooth closed eyelid curve
        draw.arc([eye_lx - eye_r_x, eye_y - int(4 * scale), eye_lx + eye_r_x, eye_y + int(8 * scale)], start=10, end=170, fill=white, width=fine_w)
        draw.arc([eye_rx - eye_r_x, eye_y - int(4 * scale), eye_rx + eye_r_x, eye_y + int(8 * scale)], start=10, end=170, fill=white, width=fine_w)
    else:
        # Large expressive eyes
        draw.ellipse([eye_lx - eye_r_x, eye_y - eye_r_y, eye_lx + eye_r_x, eye_y + eye_r_y], outline=white, width=fine_w)
        draw.ellipse([eye_rx - eye_r_x, eye_y - eye_r_y, eye_rx + eye_r_x, eye_y + eye_r_y], outline=white, width=fine_w)

        # Pupils looking up-right into deep thought (Option 2 pose)
        p_dx = int(look_dir[0] * (5 * scale))
        p_dy = int(look_dir[1] * (5 * scale))
        pupil_r = int(5.5 * scale)

        draw.ellipse([eye_lx + p_dx - pupil_r, eye_y + p_dy - pupil_r,
                      eye_lx + p_dx + pupil_r, eye_y + p_dy + pupil_r], fill=white)
        draw.ellipse([eye_rx + p_dx - pupil_r, eye_y + p_dy - pupil_r,
                      eye_rx + p_dx + pupil_r, eye_y + p_dy + pupil_r], fill=white)

        # Catchlight spark (alive spark)
        draw.ellipse([eye_lx + p_dx - int(1 * scale), eye_y + p_dy - int(4 * scale),
                      eye_lx + p_dx + int(2 * scale), eye_y + p_dy - int(1 * scale)], fill=(255, 255, 255))
        draw.ellipse([eye_rx + p_dx - int(1 * scale), eye_y + p_dy - int(4 * scale),
                      eye_rx + p_dx + int(2 * scale), eye_y + p_dy - int(1 * scale)], fill=(255, 255, 255))

    # Gentle curved nose
    nose_x = head_cx + int(4 * scale)
    nose_y = head_cy + int(14 * scale)
    draw.arc([nose_x - int(7 * scale), nose_y - int(8 * scale),
              nose_x + int(7 * scale), nose_y + int(8 * scale)], start=270, end=90, fill=white, width=fine_w)

    # Thoughtful half-smile (Option 2 reflective expression)
    mouth_y = head_cy + int(32 * scale)
    draw.arc([head_cx - int(14 * scale), mouth_y - int(10 * scale),
              head_cx + int(18 * scale), mouth_y + int(12 * scale)], start=15, end=165, fill=white, width=w)

if __name__ == "__main__":
    os.makedirs("/Users/ajsp/stick-guy/output/temp", exist_ok=True)
    img = Image.new("RGBA", (720, 1280), (11, 12, 14, 255))
    draw = ImageDraw.Draw(img)
    
    # Test render the updated character
    draw_hoodie_guy(draw, 360, 680, pose="hands_in_pockets", emotion="thoughtful", look_dir=(0.55, -0.4), t=0.5, scale=1.45)
    
    out_path = "/Users/ajsp/stick-guy/output/temp/test_character_hoodie_v2.png"
    img.save(out_path)
    print(f"Saved refined test render to {out_path}")
