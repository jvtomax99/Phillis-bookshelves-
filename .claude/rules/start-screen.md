---
paths:
  - "start/**"
---

# Start screen (`start/` and its code in `index.html`)

A candlelit nightstand rendered in Blender (Cycles) with props from Meshy
(candles, rose, lace mask).

- **Files.** `closed-phone.webp` and `closed-desk.webp` are the waiting
  screen. `loop-*.mp4`/`.webm` is a seamless 2 s candle-flicker loop of it
  (its first frame is the still). `open-*.mp4` is the cover opening,
  flickering on from the loop's first frame, as the camera pushes in on the
  signed first page. `open-*.webp` is that clip's sharp last frame.
- **Sizes.** Phone files are portrait 780x1690, desktop files 1920x1200,
  chosen by aspect ratio (landscape gets desktop).
- **The loop is skipped** under reduced motion and data saver, and when
  autoplay is refused (for example iPhone Low Power Mode).
- **Flame glow positions** (`FLAMES` in `index.html`) come from the render.
  Re-render, then re-measure.
- **Start menu.** "Enter with sound" or "Enter quietly"; a tap anywhere but
  Enter quietly counts as with sound, because browsers play sound only
  after a tap. The second tap opens the book.
- **Music.** `start/music.m4a` (AAC, for Safari) and `music.webm` (Opus):
  an original late-night lounge piece in D minor, a 58.18 s seamless loop
  played through Web Audio. The length is `LOOP` in `index.html`; change
  both together. A mute button shows while it plays and it fades out into
  the shelf. Its source (`compose.py`, rendered with FluidSynth and the
  FluidR3 GM soundfont, MIT) is on the `start-screen-source` branch.
- **When it shows.** Once per visit (`sessionStorage` key `pb-start-seen`),
  never on a `#book` link. `?start=1` forces it, `?start=0` skips it.
- **Flyleaf line.** "For the ones who read after dark" is a placeholder
  until Phillis approves her own words.
