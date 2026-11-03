# Promo video

A 38 second vertical (1080x1920) promo for Reels, TikTok and Shorts, built from the covers and the narration already in this repo. Nothing here is served by the site: this folder lives on the `promo-video` branch, not `main`.

Run `./make.sh`. It writes `build/phillis-promo.mp4` (about 30 MB, ignored by git).

- `build_audio.py`: the script. `SCRIPT` lists the scenes and which narrated sentence each one uses (book + sentence start time from the reader's `PARAS` data). It cuts those lines from the MP3s without changing them, works out word timings, synthesizes the pulse, hits and risers, and writes `build/timeline.json` and the mix.
- `voice_fx.py`: voice treatments. The promo uses `B2` ("Velvet, breathier"): about 1.8 semitones lower, 9% slower, warmer, a breath layer from the voice's own top end, and pauses inside a line held 1.5x. `A` is the narration as recorded.
- `clean.py`: copies of the two covers with the printed title and taglines painted out, for the close-up shots. The end card uses the real covers.
- `promo.html`: the animation. `render(t)` draws the frame at time `t`, so every frame is exact. Open `promo.html?t=12.3` on a local server to look at one moment.
- `render.js`: screenshots each frame with Playwright.

Options: `VOICE=A|B|B2|B3|C` and `MUSIC=remix1|remix2|groove|pulse`. The default `remix1` plays Reign Is Mine over the first version's heartbeat and drone, speeds the heartbeat up into the "Reign is MINE" slam and drops the groove there for the Ebony half. `groove` is v2 (beat from the open), `remix2` is the groove over the drone with a heartbeat open and outro, `pulse` is the first version's heartbeat bed without the beat grid, e.g. `VOICE=A MUSIC=pulse ./make.sh` for the first version exactly, or `VOICE=B2 MUSIC=pulse ./make.sh` for the first version's edit with the breathier voice. `pulse` keeps the Red Wine beat and the other modes cut it; `RED_WINE=1` or `RED_WINE=0` overrides that. `./test.sh NAME MUSIC VOICE SCENE` renders only up to the end of one scene, for quick comparisons.

The music is synthesized in `build_audio.py`: a heartbeat locked to the beat grid, a low drone, and a 140 BPM half-time beat (808 on A, A, F, G, claps, hats with rolls), and drops out for one beat before each title slam. Scene cuts snap to a two-beat grid, the picture pulses on kicks, and long shots punch in on a bar line.

To change a line: edit `SCRIPT` in `build_audio.py` (scene timings follow automatically), then adjust that scene's look in `R.<scene>` in `promo.html` if needed.

Adults 18+. The chosen lines stay away from the drugging and assault content and from the ending twist.
