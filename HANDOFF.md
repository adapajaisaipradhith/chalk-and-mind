# 🎬 Chalk & Mind — Engineering & Production Handoff Guide

Welcome to **Chalk & Mind** (`@chalk.mind`). This guide is written for you (our collaborator and friend) to clone this repository, get running in under 2 minutes, understand the codebase architecture, and immediately continue producing world-class animated psychology reels and documentaries.

---

## 1. Quick Start (Get Running in 2 Minutes)

### Step 1: System Prerequisites
Ensure your machine has **Python 3.10+** and **FFmpeg** installed:
```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg

# Windows (Command Prompt with Scoop or Chocolatey)
choco install ffmpeg
```

Verify in terminal:
```bash
ffmpeg -version
python3 --version
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/adapajaisaipradhith/chalk-and-mind.git
cd chalk-and-mind
```

### Step 3: Run the 1-Click Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

`setup.sh` will:
1. Create a Python virtual environment in `.venv/`.
2. Install all core Python packages: `edge-tts`, `pillow`, `numpy`, `scipy`.
3. Verify that all 1,899 Lucide vector icons, 698 UnDraw SVGs, fonts, and sound effects are present and intact.
4. Confirm FFmpeg audio filtering and rendering capabilities.

---

## 2. Testing Existing Videos

To verify everything works correctly on your system, render the completed reels:

```bash
# Reel #1: Pursuing vs. Chasing & Mutual Effort (Classic Minimalist Line Art)
.venv/bin/python scripts/generate_psychology_reel_remastered.py

# Reel #2: When He Goes Quiet vs. When She Stops Complaining (Kinetic Blueprint Slate)
.venv/bin/python scripts/generate_psychology_reel_02.py

# Reel #3: The Psychology of The "Strong One" (Pure 2D Cartoon Narrative - Style 4)
.venv/bin/python scripts/generate_psychology_reel_03.py
```

All final videos are exported directly to:
📁 **`output/reels/`**

---

## 3. Repository Architecture & File Map

```
chalk-and-mind/
├── .agents/skills/directing-stickman-videos/  # Master prompt schemas & storyboard specifications
├── assets/
│   ├── branding/               # Watermark badges (chalk_mind_badge.png)
│   ├── editing_toolkit/
│   │   ├── sfx/                # 14+ sound effects (whoosh, boulder thud, braam, chimes, clock tick)
│   │   └── textures/           # Blueprint grid, stardust, paper grunge textures
│   ├── fonts/                  # Patrick Hand, Kalam, Caveat, Outfit, Architects Daughter
│   ├── online_vault/
│   │   ├── audio/              # 320kbps Beethoven Moonlight Sonata score, stems, rain ambience
│   │   └── lucide_icons/       # 1,899 clean vector stroke icons (brain, heart, scale, battery, etc.)
│   └── packages/               # 698 UnDraw SVGs, 127 GL transitions, RoughJS, Popmotion
├── output/
│   ├── branding/               # Official 1024x1024 profile picture and transparent badges
│   └── reels/                  # Exported final MP4 videos (Reel 1, Reel 2, Reel 3)
├── scripts/
│   ├── generate_psychology_reel_03.py  # Pure 2D narrative cartoon engine (Hero-scale characters & props)
│   ├── generate_psychology_reel_02.py  # Kinetic blueprint diagrams & balance scales engine
│   ├── generate_psychology_reel_remastered.py # Classic minimalist line art engine
│   ├── assemble_short.py       # General FFmpeg subtitle and scene stitcher
│   └── download_online_assets_vault.py # Asset downloader utility
├── AGENTS.md                   # Brand identity, system rules, and 6 retention laws
├── HANDOFF.md                  # This collaborator handoff document
├── README.md                   # Repository overview
└── setup.sh                    # Automated 1-click installer
```

---

## 4. The 3 Supported Animation Styles

| Style | Key Identifier | Description & Composition | Script Reference |
| :--- | :--- | :--- | :--- |
| **Style 1** | Classic Minimalist | Pure dark chalkboard slate (`#0B0C0E`), fine chalk lines, living eye blinks, breathing physics, golden-amber text reveals. | [`scripts/generate_psychology_reel_remastered.py`](file:///Users/ajsp/stick-guy/scripts/generate_psychology_reel_remastered.py) |
| **Style 2** | Kinetic Blueprint | Coordinate grid background, glowing cyan and amber glassmorphism cards, dynamic physical balance scales tipping, battery meters draining. | [`scripts/generate_psychology_reel_02.py`](file:///Users/ajsp/stick-guy/scripts/generate_psychology_reel_02.py) |
| **Style 4** | Pure 2D Narrative Cartoon | Full 2D illustrated environments (bedroom window with animated rain, night streetlight bench, stone fortress, golden sunrise). Hero-scale characters (1.45x) interacting with physical cartoon props (problem boulders, padlocks, companion). Zero top text clutter; lower-third karaoke subtitles only. | [`scripts/generate_psychology_reel_03.py`](file:///Users/ajsp/stick-guy/scripts/generate_psychology_reel_03.py) |

---

## 5. The 6 Zero-Skip Retention Rules (MANDATORY)

Every script and animation sequence **must strictly adhere to these 6 laws**:

1. **Rule 1: The 1.2-Second Negative Contrast Hook**
   - Hook the viewer instantly with an unsaid emotional contradiction:
     - *“The people who give the warmest advice... are usually the coldest inside.”*
     - *“A woman’s pain is loud until it turns into total silence. A man’s pain is silent from the very beginning.”*
   - Frame 0 must move immediately (progressive chalk stroke, spring pop, boulder drop). Never open with greetings or slow logos.

2. **Rule 2: The Relatability Mirror**
   - Viscerally describe private moments that make the viewer say: *“How do they know my exact life right now?”*
   - E.g.: Staring at the ceiling at 2:00 AM, holding everyone else's problems while having nobody to call.

3. **Rule 3: Visual Novelty Every 2.5 Seconds**
   - No frame remains static for $> 2.5$ seconds.
   - Use micro-actions: Character breathing bobs, eye blinking cycle (0.12s every 3.8s), rain falling, leaves drifting, boulders stacking.

4. **Rule 4: Tactical Audio Ducking & The Zero-Volume Drop**
   - **The 0.8s Dead Silence Drop**: Absolute acoustic silence right before delivering the hardest-hitting emotional truth.
   - **Narration**: Deep baritone via `edge-tts`:
     - Voice: `en-US-ChristopherNeural`
     - Rate: `-7%`
     - Pitch: `-10Hz`
     - FFmpeg EQ: `equalizer=f=85:t=q:w=1.2:g=7,bass=g=7:f=110,volume=1.25`
   - **Tactile SFX**: Boulder thuds, padlock snaps, rain ASMR, whooshes, and 528Hz crystal chimes synced precisely with visual actions.

5. **Rule 5: The Seamless Infinite Loop**
   - The final sentence must grammatically and tonally connect back into the opening hook line:
     - End: *“Because when you build walls so thick that nobody can hurt you... you also ensure that nobody can see...”*
     - Hook: *“...the strong one.”*
   - Triggers Instagram / TikTok algorithm rewatch multipliers (>100% completion rate).

6. **Rule 6: The Story Repost & Share Trigger**
   - Close with an articulate emotional realization that viewers want to post on their own Instagram Story (e.g., *"Send this to the strong one in your life"*).

---

## 6. How to Build a New Reel (Step-by-Step Guide)

To create **Reel #4** (e.g., *The Anxious-Avoidant Loop: Why You Crave People Who Pull Away*):

1. **Copy the Template:**
   ```bash
   cp scripts/generate_psychology_reel_03.py scripts/generate_psychology_reel_04.py
   ```

2. **Define the 6 Storyboard Scenes in `generate_psychology_reel_04.py`:**
   - **Scene 1 (0.0s – 7.5s):** The Hook (Negative contrast + sudden motion).
   - **Scene 2 (7.5s – 17.0s):** The Relatability Mirror (The chase begins).
   - **Scene 3 (17.0s – 27.5s):** The Escalation (The withdrawal & cold wall).
   - **Scene 4 (27.5s – 39.5s):** The Silent Drop (0.8s total silence before the breakthrough).
   - **Scene 5 (39.5s – 50.0s):** The Healing & Solution (Breaking the pattern).
   - **Scene 6 (50.0s – 60.0s):** The Share Trigger & Infinite Loop.

3. **Keep Visuals Clean (The 2D Narrative Golden Rule):**
   - Do **NOT** put large diagnostic cards or quotes at the top of the screen.
   - Draw hero-scale characters (head radius 24–28px, body length 55–65px, total height ~200px).
   - Let the animation act out the emotions: walking toward someone who turns away, an invisible elastic string snapping, an open hand closing.
   - Use lower-third subtitles with golden active-word karaoke highlighting (`#FACC15`).

4. **Render and Inspect:**
   ```bash
   .venv/bin/python scripts/generate_psychology_reel_04.py
   ```

5. **Verify Frame Quality:**
   Check snapshot frames at scene transitions:
   ```bash
   ffmpeg -ss 00:00:03 -i output/reels/psychology_reel_04.mp4 -vframes 1 output/temp/check_01.png -y
   ffmpeg -ss 00:00:15 -i output/reels/psychology_reel_04.mp4 -vframes 1 output/temp/check_02.png -y
   ```

---

## 7. Branding & Asset Specifications

- **Brand Name:** Chalk & Mind
- **Instagram:** `@chalk.mind`
- **Watermark Badge:** Must appear in the **top-right corner** (`x = width - 110`, `y = 80`) on every single frame inside a clean circular chalk ring (`assets/branding/chalk_mind_badge.png`).
- **Color Palette:**
  - Dark Slate Background: `#0B0C0E`
  - Night Charcoal / Interior: `#14161B`
  - Clean Chalk White: `#FFFFFF` / `#E2E8F0`
  - Golden Highlight / Amber: `#F59E0B` / `#FACC15`
  - Muted Chalk Gray: `#94A3B8` / `#64748B`
  - Atmospheric Cyan: `#38BDF8`
- **Typography:** Patrick Hand (`assets/fonts/PatrickHand-Regular.ttf`) or Kalam Bold (`assets/fonts/Kalam-Bold.ttf`).

---

## 8. Production Schedule & Roadmap

- **Daily Instagram:** 1 to 2 Reels (60s Vertical 9:16).
  - Morning (9:00 AM): Raw relationship truths & unspoken emotional pain.
  - Evening (7:30 PM): Psychological healing & self-worth models.
- **Weekly YouTube:** 1 Episode (5–6 min Narrative Case Study 16:9).
- **Milestone Tracker:**
  - [x] **Reel #1:** *Pursuing vs. Chasing & Mutual Effort*
  - [x] **Reel #2:** *When He Goes Quiet vs. When She Stops Complaining*
  - [x] **Reel #3:** *The Psychology of The "Strong One"*
  - [ ] **Reel #4:** *The Anxious-Avoidant Loop: Why You Crave People Who Pull Away*
  - [ ] **Reel #5:** *When You Miss the Memories, Not the Person (Dopamine vs. Reality)*

---

*Chalk & Mind Studio Pipeline — Crafted with obsessive care for storytelling and retention.*
