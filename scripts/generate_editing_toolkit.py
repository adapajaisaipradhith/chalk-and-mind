import os
import math
import wave
import struct
import random
from pathlib import Path
from PIL import Image, ImageDraw

def create_sine_tone(filename, freq=440.0, duration=1.0, sample_rate=44100, volume=0.5, fade=True):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            val = math.sin(2 * math.pi * freq * t) * volume
            if fade:
                if i < int(num_samples * 0.1):
                    val *= (i / (num_samples * 0.1))
                elif i > int(num_samples * 0.8):
                    val *= ((num_samples - i) / (num_samples * 0.2))
            sample = int(val * 32767)
            wav.writeframes(struct.pack("<h", max(-32768, min(32767, sample))))

def create_sub_drop(filename, start_freq=90.0, end_freq=35.0, duration=1.8, sample_rate=44100, volume=0.85):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        phase = 0.0
        for i in range(num_samples):
            t = i / sample_rate
            cur_freq = start_freq + (end_freq - start_freq) * (t / duration) ** 1.5
            phase += 2 * math.pi * cur_freq / sample_rate
            decay = math.exp(-2.2 * (t / duration))
            val = math.sin(phase) * volume * decay
            sample = int(val * 32767)
            wav.writeframes(struct.pack("<h", max(-32768, min(32767, sample))))

def create_whoosh(filename, duration=0.8, sample_rate=44100, volume=0.6):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        random.seed(42)
        for i in range(num_samples):
            t = i / sample_rate
            env = math.sin(math.pi * (t / duration)) ** 2
            noise = random.uniform(-1.0, 1.0)
            tone = math.sin(2 * math.pi * (200 + 400 * (t / duration)) * t) * 0.3
            val = (noise * 0.7 + tone) * volume * env
            sample = int(val * 32767)
            wav.writeframes(struct.pack("<h", max(-32768, min(32767, sample))))

def create_chalk_scratch(filename, duration=0.45, sample_rate=44100, volume=0.55):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        random.seed(99)
        last_val = 0.0
        for i in range(num_samples):
            t = i / sample_rate
            env = math.sin(math.pi * (t / duration)) ** 1.2
            noise = random.uniform(-1.0, 1.0)
            friction = (noise - last_val * 0.4)
            last_val = noise
            harmonic = math.sin(2 * math.pi * 1850 * t) * 0.25
            val = (friction * 0.75 + harmonic) * volume * env
            sample = int(val * 32767)
            wav.writeframes(struct.pack("<h", max(-32768, min(32767, sample))))

def create_heartbeat(filename, duration=2.5, sample_rate=44100, volume=0.8):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        pulse_intervals = [0.0, 0.22, 1.05, 1.27, 2.10, 2.32]
        for i in range(num_samples):
            t = i / sample_rate
            val = 0.0
            for pt in pulse_intervals:
                dt = t - pt
                if 0 <= dt < 0.16:
                    freq = 60.0 - 25.0 * (dt / 0.16)
                    env = math.sin(math.pi * (dt / 0.16)) ** 2
                    val += math.sin(2 * math.pi * freq * dt) * env * volume
            sample = int(max(-1.0, min(1.0, val)) * 32767)
            wav.writeframes(struct.pack("<h", sample))

def create_cinematic_riser(filename, duration=3.0, sample_rate=44100, volume=0.7):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        phase = 0.0
        for i in range(num_samples):
            t = i / sample_rate
            cur_freq = 65.0 + 380.0 * (t / duration) ** 2.2
            phase += 2 * math.pi * cur_freq / sample_rate
            env = (t / duration) ** 1.8
            val = math.sin(phase) * volume * env
            sample = int(val * 32767)
            wav.writeframes(struct.pack("<h", max(-32768, min(32767, sample))))

def create_clock_tick(filename, duration=0.15, sample_rate=44100, volume=0.5):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            decay = math.exp(-35.0 * t)
            click = math.sin(2 * math.pi * 1200 * t) * decay * volume
            sample = int(click * 32767)
            wav.writeframes(struct.pack("<h", max(-32768, min(32767, sample))))

def build_texture_assets(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    w, h = 720, 1280

    # 1. Blueprint Grid Overlay
    grid_img = Image.new("RGBA", (w, h), (7, 8, 10, 255))
    draw_grid = ImageDraw.Draw(grid_img)
    spacing = 40
    for x in range(0, w, spacing):
        for y in range(0, h, spacing):
            draw_grid.point((x, y), fill=(35, 42, 54, 180))
            if (x % 160 == 0) and (y % 160 == 0):
                draw_grid.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(60, 75, 95, 200))
    grid_img.save(os.path.join(out_dir, "blueprint_grid.png"))

    # 2. Dark Slate Vignette
    slate_img = Image.new("RGBA", (w, h), (8, 9, 12, 255))
    draw_slate = ImageDraw.Draw(slate_img)
    random.seed(101)
    for _ in range(800):
        rx = random.randint(0, w)
        ry = random.randint(0, h)
        rad = random.uniform(1.0, 2.5)
        alpha = random.randint(15, 65)
        draw_slate.ellipse([rx - rad, ry - rad, rx + rad, ry + rad], fill=(210, 220, 235, alpha))
    slate_img.save(os.path.join(out_dir, "slate_stardust.png"))

def build_full_toolkit():
    base = Path("assets/editing_toolkit")
    sfx_dir = base / "sfx"
    tex_dir = base / "textures"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    tex_dir.mkdir(parents=True, exist_ok=True)

    print("🛠️ Generating Audio & SFX Assets...")
    create_sub_drop(str(sfx_dir / "sub_bass_impact.wav"))
    create_whoosh(str(sfx_dir / "cinematic_whoosh.wav"))
    create_chalk_scratch(str(sfx_dir / "chalk_draw_fast.wav"))
    create_chalk_scratch(str(sfx_dir / "chalk_draw_gentle.wav"), duration=0.6, volume=0.4)
    create_heartbeat(str(sfx_dir / "heartbeat_58bpm.wav"))
    create_cinematic_riser(str(sfx_dir / "tension_riser.wav"))
    create_clock_tick(str(sfx_dir / "clock_tick.wav"))
    create_sine_tone(str(sfx_dir / "harmonic_chime_528hz.wav"), freq=528.0, duration=1.5, volume=0.45)
    create_sine_tone(str(sfx_dir / "deep_bell_128hz.wav"), freq=128.0, duration=2.2, volume=0.6)

    print("🎨 Generating Textures & Blueprint Overlays...")
    build_texture_assets(str(tex_dir))
    print(f"✅ Toolkit built successfully in {base}")

if __name__ == "__main__":
    build_full_toolkit()
