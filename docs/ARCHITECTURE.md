# Architecture

A static site: plain HTML, CSS and JS, no build step, no server code, no packages. GitHub Pages serves `main` from the root folder.

## Folders and key files

- `index.html` (1,518 lines): the whole shelf site. Inline CSS, then the markup (start screen `#start`, shelf `#stage`, trailer `#trailer`, book and author page `#detail`), then one script. Script sections, by banner comment:
  - Content: `BOOKS` (one object per book: title, colours, cover, reader path, `progressKey`, `duration`, blurb, content note, Amazon link) and `AUTHOR`.
  - Shelf build, Sizing and endless wrap: draws the shelf (`buildShelf`) in copies so it scrolls without end.
  - Where each reader left off: `posOf`, `refreshProgress`.
  - Selection; Pointer, wheel, keys; trailer player (`openTrailer`).
  - The page that unfolds: `fillBook`, `fillAuthor`, `openBook`, `closePage`.
  - Start: `routeFromHash`, dots, `applyStyle` (fixed to walnut).
  - Start screen: menu, candle loop, opening clip, music.
- `read/<book>/index.html` (about 610 lines each): a self-contained reader. `PARAS` holds the text with each sentence's start and end time in the audio and its voice; `CHAPTERS` the chapter starts; `KEY` the storage key. The `.mp3` and `cover.jpg` sit beside it.
- `covers/`: shelf covers, full and `-sm`. `img/`: author photo.
- `start/`: start screen stills, loops, opening clips (phone and desk), music.
- `video/`: the trailer and its poster.
- `icons/`, `manifest.webmanifest`: app icon and install info (shelf only).
- `SPEC.md`: what it does and the phases. `CLAUDE.md`: project facts and rules.
- `docs/`: this file, plus Jose's working rules (`design-rules.md`, `assets.md`, `cleanup-audit.md`, `refactor.md`).

## How data moves

Nothing leaves the visitor's device. There is no account, database or server.

- **Book data** is the `BOOKS` list in `index.html`. Adding a book means a new entry there, its covers, and a new `read/<book>/` folder.
- **Listening position** (`localStorage`):
  - `book2-pos` (Reign Is Mine) and `book-ebony-club-pos` (Ebony): seconds into the audio. The reader saves it every 5 s while playing and on pause, restores it on load, and removes it when the story ends.
  - `<key>-view`: the page the reader was on.
  - The shelf reads the same keys (`progressKey` in `BOOKS`) to show progress on the spines, "Continue" on the book page and start screen, and "Start over" (which removes the key, then opens the reader). It refreshes on `pageshow`, when the tab comes back, and on `storage` events.
- **Look**: `pb-style` in `localStorage`, written by `applyStyle`; the site always applies walnut.
- **Start screen flow**:
  1. A tiny script in `<head>` decides to show it: `?start=1` forces it, `?start=0` skips it; otherwise it shows unless the URL has a `#book` link or `sessionStorage` has `pb-start-seen`.
  2. The still shows; the 2 s candle loop plays over it unless reduced motion, data saver or a refused autoplay. Phone or desk files are picked by aspect ratio.
  3. The menu (18+ note): "Enter with sound" or "Enter quietly". Music (`start/music.m4a` or `.webm`) is fetched and played through Web Audio as a 58.182 s loop.
  4. "Tap to open" plays `start/open-*.mp4`, holds its last frame, then fades into the shelf; the music fades out and `pb-start-seen` is set. A second tap or Escape skips ahead.
  5. "Continue" (when listening is saved) goes straight to that reader.
- **Links**: `#reign-is-mine`, `#ebony-the-club` and `#about` open those pages directly. Readers link back with `../../index.html#<book>`.
- **Trailer**: `video/trailer.mp4` loads only when the player first opens.
