# Phillis Brown Books

Static author site for Phillis Brown, published with GitHub Pages from `main` (root folder). No build step, no package manager, no tests. What is on `main` is what is live at https://jvtomax99.github.io/Phillis-bookshelves-/ a minute or two after a push (the path is case-sensitive: the lowercase `phillis-bookshelves-` returns 404).

All books are for adult readers (18+).

## Layout

- `index.html`: the whole shelf site in one file (bookshelf, book pages, About the author). CSS and JS are inline. Several looks live side by side as `:root[data-style="..."]` blocks (lounge, red, library, gallery, walnut); keep them working when changing shared styles.
- `read/<book>/index.html`: one self-contained read-along reader per book, with its narration `.mp3` and `cover.jpg` next to it. Readers save listening position and view in `localStorage`, always inside try/catch.
- `covers/`: full size and `-sm` shelf versions of each cover.
- `img/`: author portrait and face crop.
- `video/`: the promo trailer for the site (`trailer.mp4`, a 720x1280 web copy, about 3.7 MB, plus `trailer-poster.jpg`). It plays in the player opened by "Watch the trailer" on the shelf and "Trailer" on each book page. Its source lives in `promo/` on the `promo-video` branch; rebuild there with `promo/make.sh`, then re-encode the web copy at 720x1280 (crf 25, max 2.5 Mbps, faststart).
- `start/`: the start screen, a candlelit nightstand rendered in Blender (Cycles) with props from Meshy (candles, rose, lace mask). `closed-phone.webp` / `closed-desk.webp` are the waiting screen, `loop-*.mp4`/`.webm` a seamless 2 s candle-flicker loop of it (its first frame is the still; skipped under reduced motion and data saver, and when autoplay is refused, e.g. iPhone Low Power Mode), `open-*.mp4` the cover opening (flickering on from the loop's first frame) as the camera pushes in on the signed first page, `open-*.webp` that clip's sharp last frame. Phone files are portrait 780x1690, desktop files 1920x1200 (chosen by aspect ratio, landscape gets desktop). The flame glow positions in `index.html` (`FLAMES`) come from the render; re-render, re-measure. It shows once per visit (`sessionStorage` key `pb-start-seen`), never on a `#book` link; `?start=1` forces it, `?start=0` skips it. The flyleaf line "For the ones who read after dark" is a placeholder until Phillis approves her own words.
- `icons/` and `manifest.webmanifest`: the PB monogram app icon. `icons/source.png` is the master art. Home-screen icons are full squares (the phone rounds them), tab favicons keep the rounded shape with transparent corners, and `icon-maskable-512.png` has the art shrunk to about 78% for Android's circle crop. If the art changes, regenerate every size from the new source the same way.
- `.nojekyll`: keeps GitHub Pages from running Jekyll. Do not delete.

## Rules for this repo

- Paths must be relative. The site is served from the `/phillis-bookshelves-/` subfolder, so a link starting with `/` breaks on Pages.
- Reader pages link the icons but not the manifest, so a home-screen shortcut to a reader opens that reader instead of the shelf.
- Audio files are large (11 to 15 MB). Don't re-encode, rename or duplicate them without asking.
- After a change, serve the repo from a parent folder so the URL includes `/phillis-bookshelves-/`, and check the page in Playwright before calling it done.

- Mockups: both `index.html` and the readers put their main `<style>` in the body, after `</head>`. When injecting draft CSS for a mock, insert it before `</body>`, or the page's own rules override it and the mock lies.

## Open ideas (mocked, not built)

- Reader auto-open: when arriving from "Read or listen", open the cover by itself instead of asking for a second tap. Trade-off: loses the open-it-yourself moment.
- Phone landscape shelf: a compact header helps but "Open the book" is still partly cut off at 390px tall; a real fix puts the caption beside the books.

## Working with the owner

- **Clickable choices, always.** Whenever there are options, a suggestion or a next step, show them as clickable buttons, recommended pick first and marked "(Recommended)", with one line on why it's the pick.
- **Show a mock of every suggestion.** Before asking the owner to choose, show what each option would look like. For anything visual, render a draft in Playwright and send the screenshot (phone width and desktop when layout differs), one per option, side by side when there are several. For text or code changes, show a short before and after in the button's preview. Build the real change only after the owner picks.
- **Pushing is the owner's call.** Never commit or push without asking. When a change is ready, ask with buttons (for example "Push to main", "Branch + PR", "Hold off"). Pushing to `main` makes it live right away.
- **Notify when action is needed.** Send a phone notification every time the owner has to do something: approve a push, answer a question, check something on their phone, change a setting. Name the change and what they need to do, even if they seem to be in the chat.
- **Be honest.** Say plainly what was checked and what wasn't, what failed and what's a guess. Don't call something done without verifying it. If an idea is weak, say so and say why.
