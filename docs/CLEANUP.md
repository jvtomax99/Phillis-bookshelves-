# Cleanup list

Last audit: 2026-11-15, after phase 6.

Report only, from `docs/cleanup-audit.md`. Nothing here has been changed yet.
Each item was found by a scan and then checked by hand with grep. Line numbers
are as of the audit. Run the items with `docs/refactor.md` ("Refactor:
CLEANUP.md items ...").

1. **Shelf props and filler books that never appear** (`index.html`, about 105 lines).
   - What: the code for the wine glass, rose, candle, book stacks, bookends,
     framed photo and plain filler spines. That is `FILL`, `PROPS`, the three
     prop SVGs, `propHTML`, `rng`, the prop and filler branches of
     `buildShelf`, the `.prop-frame` click handler, and the CSS for
     `.prop-*`, `.spine.fill` and `.band`, with the `flick` and `glow`
     animations.
   - Why it isn't needed: `SET_LAYOUT` is `["B1","B0"]`, so `buildShelf`
     only ever draws the two books. The props have not shown since the
     shelf was cut down to two books. SPEC.md still says the shelf has
     "props (wine glass, rose, bookends)", which is wrong today.
   - Removing it: about 8 KB less in the page every visitor loads, and the
     shelf code reads as what it does. SPEC.md gets corrected either way.
   - Risk: **medium**. Removing it is safe in code terms, but it is a design
     question: if Jose wants the props back, the right change is to put them
     in `SET_LAYOUT`, not to delete them.

2. **Old text-drawn cover styles in both readers** (`read/*/index.html`, about 14 lines each).
   - What: `.cover .art`, `.lbl`, `.mid`, `.ttl` (and its spans), `.line`,
     `.foot`, `.tap` and `.sheen-text`.
   - Why it isn't needed: the cover is now the picture (`.cover-img`), and
     no markup or script uses those classes.
   - Removing it: shorter readers, with no leftover styling to puzzle over
     the next time the cover changes.
   - Risk: **low**.

3. **Leftover styles in the Ebony reader only** (`read/ebony-the-club/index.html`, about 4 lines).
   - What: `.coda` (Ebony puts `id="coda"` on the end mark instead),
     `.titlepage h1 .r`, `.titlepage h1 .and` and `.cover .ttl .and`.
   - Why it isn't needed: Ebony's title markup has none of those classes.
     Reign Is Mine does use them, so they stay in that reader.
   - Risk: **low**.

4. **The two readers are 95% the same code** (`read/*/index.html`, about 590 matching lines each).
   - What: apart from the story text, chapters, `KEY`, the audio file, the
     title, the cover sizing, the Part Two divider (Ebony) and the closing
     note (Reign), the two pages are copies.
   - Why it matters: every fix has to be made twice. The listening-place
     fix on 2026-11-15 was. One shared reader script, with each book's
     page holding only its data, would make one fix cover both, and a third
     book cheaper to add.
   - Risk: **medium**. It changes how both readers load. It needs the full
     site check and offline check, plus a phone test of both readers.
     Rules to keep: `KEY` per book, the readers not linking the manifest,
     and the offline file list (the shared script goes into
     `tools/offline.cjs`).

5. **Unused saved-look variable** (`index.html` lines 1391 to 1392).
   - What: `savedStyle` is read from `pb-style` and never used, because the
     site always applies walnut.
   - Removing it: one fewer read of saved data at start-up. `pb-style`
     itself is still written by `applyStyle` and stays.
   - Risk: **low**.

6. **Unused constant `MID`** (`index.html` line 905, in `const SETS = 1, MID = 0, JUMP = 3`).
   - Risk: **low**.

7. **Ids nothing refers to** (`index.html`: `id="shelfCount"` line 746, `id="ssMenu"` line 707).
   - Why it isn't needed: no style or script uses either id. The classes on
     the same elements are used and stay.
   - Risk: **low**. Tiny gain; do these only alongside other items.

Kept on purpose (not cleanup): the other looks (lounge, red, library,
gallery) and their JavaScript branches, the hidden `#styles` switcher
(CLAUDE.md), and `window.__offline`, which `.github/offline-check.cjs` uses.
Every file in the repo is referenced somewhere; there are no orphan files.
