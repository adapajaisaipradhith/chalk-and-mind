#!/usr/bin/env bash
# ==============================================================================
# One-Click Daily Stickman Reel Generator
# Usage: ./run_day.sh [DAY_NUMBER]
# Example: ./run_day.sh 1
# ==============================================================================

DAY=${1:-1}

echo "=========================================================="
echo "🚀 GENERATING INSTAGRAM REEL FOR DAY: $DAY (30-DAY PLAN)"
echo "=========================================================="

python3 scripts/generate_full_reel.py --day "$DAY"

echo ""
echo "✅ Video generation finished! Check the output directory."
