#!/usr/bin/env bash
set -e

echo "[INFO] Docker image build start"
docker compose build
echo "[SUCCESS] Docker image build complete"