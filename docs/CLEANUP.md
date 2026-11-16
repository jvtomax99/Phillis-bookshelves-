# Cleanup list

Last audit: 2026-11-15, after phase 6.

Report from `docs/cleanup-audit.md`.
Each item was found by a scan and then checked by hand with grep. Line numbers
are as of the audit. Run the items with `docs/refactor.md` ("Refactor:
CLEANUP.md items ...").

1. **The two readers are 95% the same code** (`read/*/index.html`, about 580 matching lines each).
   - What: apart from the story text, chapters, `KEY`, the audio file, the
     title, the cover sizing, the Part Two divider (Ebony) and the closing
     note (Reign), the two pages are copies.
   - Why it matters: every fix has to be made twice. The listening-place
     fix on 2026-11-15 was. One shared reader script, with each book's
     page holding only its data, would make one fix cover both, and a third
     book cheaper to add.
   - Risk: **medium**. It changes how both readers load. It needs the full
     site check and offline check, plus a phone test of both readers.
     The 18+ note block (2026-11-16) is a third shared copy: it's in
     `index.html` and both readers, so the merge should make it one file.
     Rules to keep: `KEY` per book, the readers not linking the manifest,
     and the offline file list (the shared script goes into
     `tools/offline.cjs`).

Done on 2026-11-15 (removed from this list): the shelf props and filler-book
code that never ran (SPEC corrected), the old text-drawn cover styles in both
readers, three leftover Ebony reader styles, the unused `savedStyle` read, the
unused `MID` constant, and the `ssMenu` and `shelfCount` ids. Before and after
screenshots of every page matched pixel for pixel.

Kept on purpose (not cleanup): the other looks (lounge, red, library,
gallery) and their JavaScript branches, the hidden `#styles` switcher
(CLAUDE.md), and `window.__offline`, which `.github/offline-check.cjs` uses.
Every file in the repo is referenced somewhere; there are no orphan files.
