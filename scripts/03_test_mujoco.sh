#!/usr/bin/env bash
set -e

echo "[INFO] MuJoCo simple test"
python src/test_mujoco.py

echo "[INFO] TIAGo model load test"
python tests/test_tiago_load.py

echo "[SUCCESS] Basic MuJoCo tests complete"