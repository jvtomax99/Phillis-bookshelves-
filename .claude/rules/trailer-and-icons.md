---
paths:
  - "video/**"
  - "icons/**"
  - "manifest.webmanifest"
---

# Trailer and app icons

- **Trailer.** `video/trailer.mp4` is a 720x1280 web copy, about 4 MB,
  with `trailer-poster.jpg`. It plays in the player opened by "Watch the
  trailer" on the shelf and "Trailer" on each book page. Its source lives
  in `promo/` on the `promo-video` branch: rebuild there with
  `promo/make.sh`, then re-encode the web copy at 720x1280 (crf 25, max
  2.5 Mbps, faststart).
- **Icons.** The PB monogram; `icons/source.png` is the master art.
  Home-screen icons are full squares (the phone rounds them), tab favicons
  keep the rounded shape with transparent corners, and
  `icon-maskable-512.png` has the art shrunk to about 78% for Android's
  circle crop. If the art changes, regenerate every size from the new
  source the same way.
