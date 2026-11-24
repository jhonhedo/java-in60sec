#!/usr/bin/env bash
# One-time environment setup for a fresh machine/session
set -e
pip install --break-system-packages -q skia-python numpy pocketsphinx pillow 2>/dev/null || pip install -q skia-python numpy pocketsphinx pillow
command -v ffmpeg >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg)
echo "setup ok"
