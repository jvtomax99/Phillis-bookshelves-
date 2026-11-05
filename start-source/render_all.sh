set -e
cd "$(dirname "$0")"
t=$(date +%s); python3 scene.py --res 600x1300 --samples 28 --anim rend/clip-phone 2>&1 | grep -i "error\|Trace\|rendered anim"; echo "clip-phone $(( $(date +%s)-t ))s"
t=$(date +%s); python3 scene.py --res 1280x800 --samples 28 --cam desk --anim rend/clip-desk 2>&1 | grep -i "error\|Trace\|rendered anim"; echo "clip-desk $(( $(date +%s)-t ))s"
python3 scene.py --res 780x1690 --samples 96 --endstill --out rend/final-end.png 2>&1 | grep -i "error\|rendered anim"
python3 scene.py --res 1920x1200 --samples 96 --cam desk --endstill --out rend/final-end-desk.png 2>&1 | grep -i "error\|rendered anim"
echo ALL_RENDERS_DONE
