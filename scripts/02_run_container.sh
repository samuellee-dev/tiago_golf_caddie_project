#!/usr/bin/env bash
set -e

echo "[INFO] Docker container start"
docker compose up -d

echo "[INFO] Enter container"
docker compose exec tiago-golf-caddie bash