# DESIGN.md: Phillis Brown Books

The look of the site, written down from the code on 2026-11-15 (Jose's choice:
record the site as it is; no template, no reference sites). The site is fixed
to the **walnut** look. Take values from here or from `index.html`, never from
memory, and change this file in the same commit when a value changes.

## The idea

A private library at night: a dark walnut wall, one warm light from above,
books on a plank, gold lettering. Quiet and grown-up (the readers are 18+).
Nothing bright, nothing rounded and friendly, no drop shadows that look like
an app.

## Colours (walnut, `:root[data-style="walnut"]`)

| Name | Value | Used for |
|---|---|---|
| `--wall` | `#24160F` | page background, top |
| `--wall-2` | `#110A06` | page background, deep |
| `--ink` | `#F6ECDF` | text |
| `--muted` | `#CDB9A4` | secondary text, small labels |
| `--caramel`, `--gold` | `#C9A25B` | gold: hairlines, accents, lettering |
| `--wood-hi` | `#8C5D38` | plank highlight |
| `--wood` | `#5A3820` | plank |
| `--wood-lo` | `#22130A` | plank shadow, dark surfaces |
| `--crimson` | `#B0142F` | the one strong accent, used sparingly |

A book page takes its own three colours from its entry in `BOOKS`
(`--dbg` background, `--dink` text, `--dacc` accent); buttons there use those.
The other looks (lounge, red, library, gallery) redefine the same names and
must keep working.

## Type

| Name | Faces | Used for |
|---|---|---|
| `--display` | Bodoni Moda, then Bodoni 72, Didot, Georgia | titles, the author's name |
| `--body` | Instrument Sans, then Helvetica Neue, Arial | everything read or tapped |
| `--script` | Pinyon Script, then Snell Roundhand | the signature touch only |

- Small labels: `600 10px` to `13px`, capitals, letter spacing `.12em` to
  `.14em`, in `--muted`.
- Running text: 13 to 16 px, line height about 1.4.
- Titles: `clamp(30px, 3.4vw, 40px)` to `clamp(34px, 4vw, 46px)`.
- The fonts come from Google Fonts.

## Spacing, corners, shadows, motion

- Side gutters: 16 px, more where the phone's safe area asks for it.
- Corners: pills are `99px`; covers and book edges `2px` or less; cards `14px`.
  Nothing in between.
- Shadows are warm and brown, never grey or black: a gold hairline
  (`inset 0 0 0 1px #C9A25B`) with `0 14px 24px -12px rgba(40,20,10,.6)` under
  a raised piece. Outlined pieces use a 1 px inset line and no drop shadow.
- Motion: fades of `.3s` to `.35s`; larger moves `.85s` to `.9s` with
  `cubic-bezier(.2,.75,.2,1)`. Reduced motion turns loops and moves off.

## Parts

- **Shelf** (`#stage`): the wall, the light, the plank, books that scroll
  without end; dots under it.
- **Footer** (`.foot`): three small labels in one row: the copyright, a hint
  (swipe or drag), the counter.
- **Buttons** (`.buy`): a pill, `15px 24px`, `600 13px` capitals with `.12em`
  spacing. Filled in the book's accent, or outlined (`.is-soon`) with a 1 px
  inset line. Focus: a 2 px outline, 3 px off.
- **Book and author page** (`#detail`): unfolds over the shelf in the book's
  own colours; on a phone its buttons stick to the bottom.
- **Install line** (`.d-install`, on a book page under the description): a
  card-cornered box (`14px`) with a 1 px inset line in the book's text colour
  at 22%, `400 13px/1.45` text, Share and Add to Home Screen in `600`. Shown
  only in Safari on an iPhone or iPad, when the site is not on the Home
  Screen and the reader has started that story.
- **Offline notes**: shown only when the narration or trailer can't load.
  In a reader, `.offline-note` above the player meta row: the reader's own
  small-label style (label face, `0.66rem`, capitals, `.16em`, muted), centred.
  In the trailer, `.tr-off` over the video: a `14px` card on `rgba(10,6,7,.82)`
  with a gold hairline, `600 12px` capitals with `.12em`.
- **18+ note** (`#ag`): over the whole page on `rgba(17,10,6,.86)` with a 6px
  blur. A `14px` card in `--wall` with a gold hairline, a small-label "Phillis
  Brown", the title in `500 34px` display face with "18+" in gold italic, a
  `400 15px` line in `--muted`, a filled gold pill (`.buy` size), and "Leave" as
  an underlined small label. Fixed walnut colours, so it looks the same in the
  readers.
- **Share pictures** (`share/`, 1200x630): the wall gradient, a gold hairline
  inset 22px, the cover(s) on the left, kicker, title with the gold italic word,
  the pull line, and the script signature. Made by `tools/share-cards.cjs`.
- **Start screen** (`#start`): see `.claude/rules/start-screen.md`.
- **Trailer** (`#trailer`): see `.claude/rules/trailer-and-icons.md`.
