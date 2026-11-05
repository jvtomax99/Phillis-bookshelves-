# Start screen source

The source of the site's start screen (`start/` on `main`): a candlelit nightstand rendered with Blender's Cycles from Python. This branch is never deployed.

- `scene.py`: builds the whole scene (book with a hinged cover, gold lettering in the site's fonts, walnut nightstand, velvet curtain, wine glass, lights, cameras) and renders it. Needs Blender as a Python module (`pip install bpy`).
- `make_textures.py`: draws the signed first page (`tex/flyleaf.png`) and the endpaper. **The inscription is a placeholder** until Phillis approves her own words; change it here, re-run, re-render.
- `meshy_gen.py`: how the props in `meshy/` were made (Meshy text-to-3D, meshy-7.1, preview then refine with PBR; 30 credits each). Only re-run it to make new props.
- `render_all.sh`: renders the two opening clips (32 frames at 24 fps) and their sharp last frames.
- `tex/`: leather `leather_red_02`, wood `black_walnut_veneer_01` and velvet `velour_velvet` from Poly Haven (CC0), 2K.
- `fonts/`: Bodoni Moda, Pinyon Script, Instrument Sans (SIL Open Font License, licences beside them).

## Re-render

```
python3 make_textures.py
python3 scene.py --out closed-phone.png --res 780x1690 --samples 96            # waiting screen, phone
python3 scene.py --out closed-desk.png --res 1920x1200 --samples 96 --cam desk # waiting screen, desktop
python3 scene.py --res 780x1690 --flames flames-phone.json --samples 1 --out /tmp/x.png   # flame positions for FLAMES in index.html
bash render_all.sh
```

Then on `main`: convert the PNGs to `start/*.webp` (quality 84), and encode each clip folder twice:

```
ffmpeg -framerate 24 -i f%04d.png -c:v libx264 -profile:v main -pix_fmt yuv420p -crf 21 -preset slow -movflags +faststart -an open-phone.mp4
ffmpeg -framerate 24 -i f%04d.png -c:v libvpx-vp9 -b:v 0 -crf 34 -pix_fmt yuv420p -row-mt 1 -an open-phone.webm
```

On 4 CPU cores a phone still takes about 3 minutes and each clip about 20.
