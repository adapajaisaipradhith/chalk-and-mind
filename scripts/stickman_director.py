#!/usr/bin/env python3
"""
stickman_director.py
====================
AI Stickman Video Director CLI & Daily Content Engine.
Tailored for 20-second portrait (9:16) high-retention shorts.
Follows the repository's 5-Stage Heartbeat Engine & prompt contracts.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Built-in bank of 10 viral entertainment episodes for quick daily production
VIRAL_EPISODES = [
    {
        "id": 1,
        "title": "Why Humans Never Sleep on Time",
        "style": "Style 1 (Classic Minimalist Dark)",
        "hook": "Ever notice your brain only gets motivated at 1:47 AM?",
        "clip1_vo": "Your brain at 2 PM: completely dead, zero energy. Your brain at 1:47 AM: 'Let's research the entire history of the Byzantine Empire.'",
        "clip2_vo": "Congratulations. You traded 8 hours of peaceful sleep for useless trivia. And tomorrow at 7 AM? You will regret everything.",
        "clip1_beats": {
            "0-3s": "Stick figure slumped like a deflated balloon over a desk under a harsh white spotlight, eyes drooping.",
            "3-7s": "Sudden snap to night bedroom. Clock reads 01:47. Stick figure's head jolts upright with electric gold lightning sparks radiating outward.",
            "7-10s": "Dozens of holographic books, charts, and ancient maps spin wildly around the bed as the figure maniacally takes notes with glowing pen."
        },
        "clip2_beats": {
            "0-3s": "Camera pulls back to show the figure proudly holding a giant golden trophy of knowledge while standing on a mountain of glowing trivia scrolls.",
            "3-7s": "Violent match cut to 7:00 AM alarm ringing. A massive digital anvil labeled 7:00 AM slams down onto the bed with comedic screen shake.",
            "7-10s": "Stick figure crawls on the floor looking directly at the camera with hollow dead eyes, dragging a single pillow behind him into darkness."
        }
    },
    {
        "id": 2,
        "title": "How Humans Invented Overthinking",
        "style": "Style 3 (Prehistoric Dark Comedy)",
        "hook": "Ten thousand years ago, survival was simple. Then someone invented 'What if?'",
        "clip1_vo": "A prehistoric caveman hears a tiny twig snap. Tiger? No. Falling leaf. But his brain decides: 'What if that leaf was holding a spear?'",
        "clip2_vo": "Ten thousand years later, the tiger is gone, but we still lie awake wondering what our coworker meant by that emoji. Evolution is funny.",
        "clip1_beats": {
            "0-3s": "Chubby caveman in rough leopard pelt sitting happily by campfire roasting a meat bone, smiling peacefully under starry sky.",
            "3-7s": "A tiny leaf drops behind him with a gentle rustle. The caveman's eyes widen cartoonishly to twice their size, campfire freezes.",
            "7-10s": "Dark prehistoric thought cloud erupts overhead with a giant saber-toothed beast wearing armor and holding three clubs, glaring menacingly."
        },
        "clip2_beats": {
            "0-3s": "Seamless match cut to modern bedroom ceiling. White-filled caveman face now in bed, staring unblinkingly upward.",
            "3-7s": "A giant floating thumbs-up emoji with a yellow smiley hovers above the bed, pulsing with ominous red question marks.",
            "7-10s": "He pulls rough animal skin blanket completely over his head as three giant question marks drop onto his pillow like rocks."
        }
    },
    {
        "id": 3,
        "title": "The Gym Motivation Trap",
        "style": "Style 2A (Modern Studio Tech)",
        "hook": "Buying a gym membership burns 0 calories, but your brain thinks you won.",
        "clip1_vo": "You swipe your credit card for a luxury gym pass. Dopamine floods your nervous system. You feel ripped, healthy, unstoppable.",
        "clip2_vo": "Then comes 6 AM Monday. The bed is warm. The floor is cold. And suddenly, rest day becomes rest year.",
        "clip1_beats": {
            "0-3s": "Red-beanie stickman in yellow shirt stands in sleek white studio. He taps a glowing cyan card on a floating glass biometric kiosk.",
            "3-7s": "Electric blue energy rings pulse out from the terminal. His stick biceps inflate cartoonishly with golden victory aura, flexing proudly.",
            "7-10s": "He puts on glowing neon sunglasses, celebrating in zero gravity as confetti particles burst across the high-key white space."
        },
        "clip2_beats": {
            "0-3s": "Instant match cut into bedroom setting. Stickman is wrapped like a burrito in thick blankets, beanie peeking out.",
            "3-7s": "Alarm clock sounds. He sticks one bare black stick leg out. Frost crystals rapidly freeze across his foot, accompanied by comedy shivering.",
            "7-10s": "Leg snaps back under the duvet instantly. Blanket pulls over head. A floating glowing calendar flips from 'Mon' to '2027'."
        }
    },
    {
        "id": 4,
        "title": "The Procrastination Cleaning Loop",
        "style": "Style 1 (Classic Minimalist Dark)",
        "hook": "Why does a 5-minute task make your whole house sparkling clean?",
        "clip1_vo": "You sit down to do one single email. Five minutes of work. But suddenly, your baseboards haven't been deep cleaned since 2019.",
        "clip2_vo": "Three hours later, the windows shine, the pantry is alphabetical, and that email? Still sitting there, judging you.",
        "clip1_beats": {
            "0-3s": "Monochrome white stick figure sitting at desk staring at a glowing white laptop screen displaying a single envelope icon.",
            "3-7s": "Figure spots a microscopic white dot of dust on the table. Eyes zoom in with crosshairs. He pulls out a giant mop with speed lines.",
            "7-10s": "Figure transforms into a cyclone of cleaning energy, wiping walls, dusting shelves, and scrubbing floorboards at hyper speed."
        },
        "clip2_beats": {
            "0-3s": "Camera dollies across a pristine, mirror-like sparkling room reflecting starburst sparkles from every corner.",
            "3-7s": "Figure stands proudly with hands on hips holding golden sponge, admiring the squeaky clean paradise.",
            "7-10s": "Slow dolly into the laptop screen on the desk. The single unopened envelope icon slowly raises one eyebrow and blinks."
        }
    },
    {
        "id": 5,
        "title": "The Screen Time Dilemma",
        "style": "Style 4 (Cozy Storytelling)",
        "hook": "Just five minutes before sleep. What could possibly go wrong?",
        "clip1_vo": "Tucked into warm blankets, lights out. You open your phone for just 'one quick check.' Just two minutes, right?",
        "clip2_vo": "Thirty short videos later, the birds are chirping outside, your retina is scorched, and you have learned zero new life skills.",
        "clip1_beats": {
            "0-3s": "Cozy dimly lit bedroom in soft blue hues. Minimalist white-filled stick figure lies in bed, glowing phone illuminating face.",
            "3-7s": "Thumb scrolls up rapidly. Colorful glowing holographic icons (dancing cats, cooking pans, cars) shoot out of screen in high arc.",
            "7-10s": "Camera orbits around bed as the stream of floating video cards wraps around the bedroom like a glowing neon vortex."
        },
        "clip2_beats": {
            "0-3s": "Exterior window cut: gentle golden morning sunlight spills into the room as small cartoon birds land on windowsill, singing notes.",
            "3-7s": "Cut inside: Stick figure is frozen in identical pose, eyes now glowing bright red like lasers, still scrolling without breathing.",
            "7-10s": "Figure slowly turns face to camera. A large textless battery icon above head flashes red at 1% with a soft beep."
        }
    }
]


def print_daily_plan(episodes):
    print("=" * 70)
    print("   AI STICKMAN DIRECTOR — 20-SECOND DAILY VIRAL SHORTS ENGINE")
    print("=" * 70)
    print(f"Loaded {len(episodes)} Ready-to-Produce Episodes:\n")
    for ep in episodes:
        print(f"[{ep['id']}] {ep['title']}")
        print(f"    Style: {ep['style']}")
        print(f"    Hook: \"{ep['hook']}\"")
        print(f"    Clip 1 (0-10s): {ep['clip1_vo']}")
        print(f"    Clip 2 (10-20s): {ep['clip2_vo']}")
        print("-" * 70)


def generate_prompts(ep_id):
    ep = next((e for e in VIRAL_EPISODES if e["id"] == ep_id), None)
    if not ep:
        print(f"[!] Episode ID {ep_id} not found.", file=sys.stderr)
        return

    print("=" * 70)
    print(f"PROMPT PACKAGE: Episode {ep['id']} - {ep['title']}")
    print("Ratio: 9:16 Portrait (1080x1920) | Duration: 20s (2x10s clips)")
    print("=" * 70)

    # CLIP 1 PROMPT
    print("\n" + "=" * 30 + " CLIP 1 (0–10s) " + "=" * 30)
    c1 = f"""Output specification: approximately ten seconds, portrait aspect ratio 9:16, 720p/1080p target, 24/30 FPS, synchronized audio.

Visual Style & Environment:
Flat, uniform, high-contrast canvas tailored for portrait 9:16 mobile feeds. Safe margins around top and bottom for UI overlay.

Character DNA Lock:
Use minimalist two-dimensional line animation. Show consistent stick figure with round head, no clothing or stylized simple clothing, stable proportions, connected line limbs, and uniform line weight. Exactly two arms and two legs visible. Raising or lowering a limb replaces the previous line, never leaving double limbs.

Timed Synchronized Visual Beats:
- [0-3s]: {ep['clip1_beats']['0-3s']}
- [3-7s]: {ep['clip1_beats']['3-7s']}
- [7-10s]: {ep['clip1_beats']['7-10s']}

Audio & Voiceover Contract:
Audio voiceover only, strictly no speech bubbles, no dialogue boxes.
Dialogue: "{ep['clip1_vo']}"

Narrator Lock:
One off-screen adult male narrator throughout. General American accent, warm clean baritone, medium-low pitch, gentle chest resonance, no raspiness or breathiness. Calm conversational delivery, restrained pitch variation, steady speaking pace, and close, dry studio sound. Keep the same vocal timbre, register, accent, pace, and recording quality throughout.

BGM & SFX:
Audio: Voiceover clearly audible over subtle playful rhythm and soft ambient bass, building punchy narrative momentum. Synchronized crisp comedy SFX on physical actions.

Final Transition State:
Ends on high-energy pose creating seamless motion match for clip 2 opening.

Negative Constraints:
Negative constraints: no photorealistic human skin or faces, no 3D humanoid CGI models, no extra limbs, no speech bubbles, no dialogue text boxes, no chaotic line glitches, no watermarks, no subtitles in raw video."""
    print(c1)

    # CLIP 2 PROMPT
    print("\n" + "=" * 30 + " CLIP 2 (10–20s) " + "=" * 30)
    c2 = f"""Output specification: approximately ten seconds, portrait aspect ratio 9:16, 720p/1080p target, 24/30 FPS, synchronized audio.

Visual Style & Environment:
Flat, uniform, high-contrast canvas tailored for portrait 9:16 mobile feeds. Continuing identical visual style and color palette from clip 1.

Character DNA Lock:
The identical minimalist two-dimensional stick figure from clip 1 with identical proportions, head shape, line weight, and drawing grammar.

First-Frame State:
Inherits the energetic final position and trajectory from clip 1.

Timed Synchronized Visual Beats:
- [0-3s]: {ep['clip2_beats']['0-3s']}
- [3-7s]: {ep['clip2_beats']['3-7s']}
- [7-10s]: {ep['clip2_beats']['7-10s']}

Audio & Voiceover Contract:
Audio voiceover only, strictly no speech bubbles, no dialogue boxes.
Dialogue: "{ep['clip2_vo']}"

Narrator Lock:
One off-screen adult male narrator throughout. General American accent, warm clean baritone, medium-low pitch, gentle chest resonance, no raspiness or breathiness. Calm conversational delivery, restrained pitch variation, steady speaking pace, and close, dry studio sound. Keep the same vocal timbre, register, accent, pace, and recording quality throughout.

BGM & SFX:
Audio: Voiceover seamlessly continues the identical musical rhythm and tempo from clip 1, culminating in a crisp deadpan comedy beat at 9s. Synchronized crisp SFX on impacts and camera moves.

Negative Constraints:
Negative constraints: no photorealistic human skin or faces, no 3D humanoid CGI models, no extra limbs, no speech bubbles, no dialogue text boxes, no chaotic line glitches, no watermarks, no subtitles in raw video."""
    print(c2)

    # Generate subtitles file
    os.makedirs("output/subtitles", exist_ok=True)
    ass_path = f"output/subtitles/ep_{ep['id']}_subtitles.ass"
    from assemble_short import create_ass_subtitles
    dialogues = [
        ("00:00:00.50", "00:00:04.50", ep['clip1_vo'].split('.')[0], False),
        ("00:00:05.00", "00:00:09.50", ep['clip1_vo'].split('.')[1] if '.' in ep['clip1_vo'] else ep['clip1_vo'], False),
        ("00:00:10.50", "00:00:15.00", ep['clip2_vo'].split('.')[0], False),
        ("00:00:15.50", "00:00:19.50", ep['clip2_vo'].split('.')[1] if '.' in ep['clip2_vo'] else ep['clip2_vo'], True),
    ]
    create_ass_subtitles(dialogues, ass_path)

    print("\n" + "=" * 70)
    print(f"[+] Subtitles file prepared: {ass_path}")
    print(f"[+] When Clip 1 & Clip 2 are generated, run:")
    print(f"    python3 scripts/assemble_short.py --clips clip1.mp4 clip2.mp4 --subtitles {ass_path} --output output/ep_{ep['id']}_final.mp4")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="AI Stickman Video Director Engine.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List ready-made viral episodes for daily upload")
    
    gen_parser = subparsers.add_parser("generate", help="Generate production prompts for an episode")
    gen_parser.add_argument("--id", type=int, default=1, help="Episode ID (1-5)")

    args = parser.parse_args()
    if args.command == "list" or not args.command:
        print_daily_plan(VIRAL_EPISODES)
    elif args.command == "generate":
        generate_prompts(args.id)


if __name__ == "__main__":
    main()
