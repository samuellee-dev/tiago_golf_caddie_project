#!/usr/bin/env bash
set -e

echo "[INFO] Render single frame"
python src/render_single_frame.py

echo "[INFO] Inspect cameras"
python src/inspect_cameras.py

echo "[SUCCESS] Rendering test complete"