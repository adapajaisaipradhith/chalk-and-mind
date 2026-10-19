#!/usr/bin/env bash
set -e

# =============================================================================
# CHALK & MIND — AUTOMATED PRODUCTION PIPELINE SETUP
# =============================================================================

echo "======================================================================"
echo "🎬 Setting up Chalk & Mind Video Production Studio..."
echo "======================================================================"

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi
echo "✅ Python 3 detected: $(python3 --version)"

# 2. Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo "   On macOS: run 'brew install ffmpeg'"
    echo "   On Ubuntu/Debian: run 'sudo apt install ffmpeg'"
    exit 1
fi
echo "✅ FFmpeg detected: $(ffmpeg -version | head -n 1)"

# 3. Create Virtual Environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# 4. Activate & Install Dependencies
echo "⬇️  Installing required production dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install edge-tts pillow numpy scipy

# 5. Ensure Output Directories
mkdir -p output/reels output/temp output/branding

echo ""
echo "======================================================================"
echo "🎉 Setup Complete! You are ready to produce Chalk & Mind videos."
echo "======================================================================"
echo ""
echo "Quick Commands:"
echo "  • Render Reel #1 (Minimalist Line Art):  .venv/bin/python scripts/generate_psychology_reel_remastered.py"
echo "  • Render Reel #2 (Kinetic Blueprint):   .venv/bin/python scripts/generate_psychology_reel_02.py"
echo "  • Render Reel #3 (Pure 2D Cartoon):     .venv/bin/python scripts/generate_psychology_reel_03.py"
echo "  • Assemble Multi-Clip Shorts:           .venv/bin/python scripts/assemble_short.py"
echo "======================================================================"
