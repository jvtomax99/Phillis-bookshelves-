# Promo video

A 37 second vertical (1080x1920) promo for Reels, TikTok and Shorts, built from the covers and the narration already in this repo. Nothing here is served by the site: this folder lives on the `promo-video` branch, not `main`.

Run `./make.sh`. It writes `build/phillis-promo.mp4` (about 30 MB, ignored by git).

- `build_audio.py`: the script. `SCRIPT` lists the scenes and which narrated sentence each one uses (book + sentence start time from the reader's `PARAS` data). It cuts those lines from the MP3s without changing them, works out word timings, synthesizes the pulse, hits and risers, and writes `build/timeline.json` and the mix.
- `clean.py`: copies of the two covers with the printed title and taglines painted out, for the close-up shots. The end card uses the real covers.
- `promo.html`: the animation. `render(t)` draws the frame at time `t`, so every frame is exact. Open `promo.html?t=12.3` on a local server to look at one moment.
- `render.js`: screenshots each frame with Playwright.

To change a line: edit `SCRIPT` in `build_audio.py` (scene timings follow automatically), then adjust that scene's look in `R.<scene>` in `promo.html` if needed.

Adults 18+. The chosen lines stay away from the drugging and assault content and from the ending twist.
