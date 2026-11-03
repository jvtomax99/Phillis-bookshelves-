#!/usr/bin/env bash
# Builds build/phillis-promo.mp4 from the covers and narration in this repo.
# Needs python3 + numpy, ffmpeg, node with playwright, and network for Google Fonts.
set -euo pipefail
cd "$(dirname "$0")"
PORT=${PORT:-8811}
REPO_DIR=$(basename "$(cd .. && pwd)")
mkdir -p build && rm -rf build/frames && mkdir build/frames
python3 clean.py
python3 build_audio.py
ffmpeg -v error -y -i build/mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 build/mix.wav
# serve from the folder above the repo so the URL has /phillis-bookshelves-/ like Pages
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory ../.. >/dev/null 2>&1 & SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
for _ in $(seq 50); do curl -sf -o /dev/null "http://127.0.0.1:$PORT/" && break; sleep .2; done
N=$(python3 -c "import json,math;print(math.ceil(json.load(open('build/timeline.json'))['T']*30))")
Q=$(( (N + 3) / 4 )); PIDS=()
for i in 0 1 2 3; do
  A=$(( i * Q )); B=$(( (i + 1) * Q )); (( B > N )) && B=$N
  node render.js $A $B "$PORT" "$REPO_DIR" & PIDS+=($!)
done
for p in "${PIDS[@]}"; do wait "$p"; done
ffmpeg -v error -y -framerate 30 -i build/frames/f%05d.jpg -i build/mix.wav \
  -c:v libx264 -preset slow -crf 21 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -profile:v high \
  -movflags +faststart -c:a aac -b:a 192k -ac 2 -shortest build/phillis-promo.mp4
echo "done: promo/build/phillis-promo.mp4 ($N frames)"
