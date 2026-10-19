import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def download_file(url, target_path, desc):
    print(f"--> Downloading {desc}...")
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists() and target_path.stat().st_size > 1000:
        print(f"    Already exists: {target_path} ({target_path.stat().st_size / 1024:.1f} KB)")
        return
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response, open(target_path, "wb") as out_file:
            data = response.read()
            out_file.write(data)
        print(f"    Saved: {target_path} ({len(data) / 1024:.1f} KB)")
    except Exception as e:
        print(f"    Failed to download {url}: {e}")

def clone_repo(repo_url, target_dir, desc):
    print(f"--> Cloning {desc}...")
    target_dir = Path(target_dir)
    if target_dir.exists() and any(target_dir.iterdir()):
        print(f"    Already cloned: {target_dir}")
        return
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--depth=1", repo_url, str(target_dir)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"    Successfully cloned to {target_dir}")
    else:
        print(f"    Git clone notice: {res.stderr.strip()}")

def main():
    base_dir = Path("assets/online_vault")
    base_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🌐 DOWNLOADING ONLINE ASSET VAULT FOR CHALK & MIND")
    print("Fonts, Icons, Background Music, Ambience, and Textures")
    print("=" * 70)

    # 1. FONTS (Handwriting & Modern Editorial Displays)
    font_dir = base_dir / "fonts"
    fonts = [
        ("https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf", font_dir / "Caveat.ttf", "Caveat Handwriting Font"),
        ("https://raw.githubusercontent.com/google/fonts/main/ofl/kalam/Kalam-Bold.ttf", font_dir / "Kalam-Bold.ttf", "Kalam Bold Handwriting Font"),
        ("https://raw.githubusercontent.com/google/fonts/main/ofl/kalam/Kalam-Regular.ttf", font_dir / "Kalam-Regular.ttf", "Kalam Regular Handwriting Font"),
        ("https://raw.githubusercontent.com/google/fonts/main/ofl/shadowsintolight/ShadowsIntoLight.ttf", font_dir / "ShadowsIntoLight.ttf", "Shadows Into Light Font"),
        ("https://raw.githubusercontent.com/google/fonts/main/ofl/outfit/Outfit%5Bwght%5D.ttf", font_dir / "Outfit.ttf", "Outfit Modern Display Font"),
        ("https://raw.githubusercontent.com/google/fonts/main/ofl/syne/Syne%5Bwght%5D.ttf", font_dir / "Syne.ttf", "Syne Geometric Display Font")
    ]
    for url, path, name in fonts:
        download_file(url, path, name)

    # 2. VECTOR ICONS (Lucide 1400+ clean line icons)
    icons_dir = base_dir / "lucide_icons"
    clone_repo("https://github.com/lucide-icons/lucide.git", icons_dir, "Lucide Vector Stroke Icons Suite")

    # 3. BACKGROUND MUSIC & AMBIENCE (CC0 / Public Domain Wikimedia Classical)
    audio_dir = base_dir / "audio"
    audio_tracks = [
        # Moonlight Sonata 1st Movement (Melancholic emotional piano)
        ("https://upload.wikimedia.org/wikipedia/commons/e/eb/Beethoven_Moonlight_1st_movement.ogg", audio_dir / "bgm_moonlight_sonata.ogg", "Moonlight Sonata Piano"),
        # Gymnopédie No. 1 (Erik Satie - Deep reflective introspective piano)
        ("https://upload.wikimedia.org/wikipedia/commons/0/07/Erik_Satie_-_Gymnop%C3%A9die_No._1.ogg", audio_dir / "bgm_gymnopedie_no1.ogg", "Satie Gymnopedie No 1"),
        # Rain & Ambient Thunder Storm (Atmospheric depth)
        ("https://upload.wikimedia.org/wikipedia/commons/4/41/Thunder_in_the_rain.ogg", audio_dir / "ambience_rain_thunder.ogg", "Rain & Thunder Ambience"),
        # Vintage Vinyl Crackle Loop
        ("https://upload.wikimedia.org/wikipedia/commons/a/af/Phonograph_cylinder_noise.ogg", audio_dir / "vinyl_crackle.ogg", "Vinyl Cylinder Crackle")
    ]
    for url, path, name in audio_tracks:
        download_file(url, path, name)

    # 4. TEXTURES & FILM OVERLAYS
    tex_dir = base_dir / "textures"
    tex_urls = [
        # Dark Slate Texture
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Blackboard_green.jpg/800px-Blackboard_green.jpg", tex_dir / "blackboard_texture.jpg", "Chalkboard Surface Texture"),
        # High-res Grunge / Stardust Paper
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Paper_texture_01.jpg/800px-Paper_texture_01.jpg", tex_dir / "grunge_paper.jpg", "Grunge Paper Texture")
    ]
    for url, path, name in tex_urls:
        download_file(url, path, name)

    print("\n✅ ASSET VAULT DOWNLOAD COMPLETED!")

if __name__ == "__main__":
    main()
