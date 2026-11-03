#!/usr/bin/env bash
# test.sh NAME MUSIC VOICE UNTIL_SCENE  -> ../NAME.mp4 (from 0 to the end of UNTIL_SCENE)
set -euo pipefail
cd "$(dirname "$0")"
NAME=$1; export MUSIC=$2 VOICE=$3; UNTIL=$4; PORT=8812
python3 clean.py; python3 build_audio.py >/dev/null
ffmpeg -v error -y -i build/mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 build/mix.wav
rm -rf build/frames; mkdir -p build/frames
python3 -m http.server $PORT --bind 127.0.0.1 --directory ../.. >/dev/null 2>&1 & SRV=$!; trap 'kill $SRV 2>/dev/null' EXIT
for _ in $(seq 50); do curl -sf -o /dev/null "http://127.0.0.1:$PORT/" && break; sleep .2; done
END=$(python3 -c "import json;d=json.load(open('build/timeline.json'));print(int([s['b'] for s in d['scenes'] if s['id']=='$UNTIL'][0]*30)+12)")
Q=$(( (END + 3) / 4 )); PIDS=()
for i in 0 1 2 3; do A=$((i*Q)); B=$(((i+1)*Q)); ((B>END)) && B=$END; node render.js $A $B $PORT "$(basename "$(cd .. && pwd)")" & PIDS+=($!); done
for p in "${PIDS[@]}"; do wait "$p"; done
ffmpeg -v error -y -framerate 30 -i build/frames/f%05d.jpg -i build/mix.wav -c:v libx264 -preset medium -crf 21 -maxrate 6M -bufsize 12M \
  -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -ac 2 -shortest -af "afade=t=out:st=$(python3 -c "print($END/30-.4)"):d=0.4" ../$NAME.mp4
echo "$NAME: $(python3 -c "print(round($END/30,1))")s"
