# CLAUDE.md: Phillis Brown Books

Static author site for Phillis Brown, for adult readers (18+): a bookshelf,
book pages, About the author, and a read-along reader per book. Live at
https://jvtomax99.github.io/Phillis-bookshelves-/ (the path is
case-sensitive; lowercase returns 404). Plain files on GitHub Pages from
`main`: no build step, no packages, no tests.

Read first: `SPEC.md` (what, "Done when", phases; TO FILL lines wait for
Jose) and `docs/ARCHITECTURE.md` (map of files and how data moves). The
rules shared by all of Jose's projects are in `.claude/rules/general.md`;
where this file differs, this file wins.

## Rules for this repo

- **Real user.** Not Jose: Phillis Brown and her readers. Remind Jose to
  check plans, and any words that speak for Phillis (About text, blurbs,
  the flyleaf line), with Phillis before building.
- **Relative paths only.** The site is served from a subfolder, so a link
  starting with `/` breaks on Pages.
- **Looks.** `index.html` holds several looks as
  `:root[data-style="..."]` blocks (lounge, red, library, gallery, walnut).
  The site is fixed to walnut (`applyStyle("walnut")` at start-up, the
  `#styles` switcher is `hidden`), but keep the others working when
  changing shared styles.
- **Progress keys.** Each book's `progressKey` in `BOOKS` (`index.html`)
  must match `KEY` in its reader, or the shelf's progress and "Continue"
  lose track. Readers use `localStorage` only inside try/catch.
- **Audio files are large** (11 to 15 MB). Don't re-encode, rename or
  duplicate them without asking.
- **Readers link the icons but not the manifest,** so a home-screen
  shortcut to a reader opens that reader instead of the shelf.
- **`.nojekyll`** keeps Pages from running Jekyll. Do not delete.
- **Start screen** (`start/` and its code in `index.html`): read
  `.claude/rules/start-screen.md` before changing it. **Trailer and app
  icons:** `.claude/rules/trailer-and-icons.md`.
- **Public repo.** Paid raw files (fonts, models) can't be committed
  (`docs/assets.md`, section 9). Before any purchase ask Jose: free assets,
  or GitHub Pro or a move to Vercel so the repo can go private.

## Preview and going live

- **Preview.** There are no branch previews: the live site changes the
  moment a pull request is merged, so say that plainly. Serve the repo from
  a parent folder so the URL includes `/phillis-bookshelves-/`, check the
  page in Playwright, and send screenshots at 390 px and desktop plus a
  "try this" list Jose can follow on the live site after the merge.
- **Mockups.** `index.html` and the readers put their main `<style>` in the
  body, after `</head>`. Insert draft CSS before `</body>`, or the page's
  own rules override it and the mock lies.
- **Site check.** `node .github/site-check.cjs` with the pages listed in
  `.github/workflows/site-check.yml`; it also runs on every pull request and
  must be green before asking Jose to push. A new page goes into that list.
- **Not made yet:** `DESIGN.md` and `docs/CLEANUP.md`. Follow
  `docs/design-rules.md` to make `DESIGN.md` before the first design work.
- `README.md` is the public readme, not session notes; leave it as it is.

## Extras Jose asked for here

- **Show a mock of every suggestion** before asking him to choose. Visual:
  a Playwright draft per option (phone and desktop when layout differs),
  side by side. Text or code: a short before and after in the button's
  preview. Build the real change only after he picks.
- **Buttons carry one line on why the recommended pick is the pick.**
- **Notify when action is needed.** A phone notification every time he has
  to do something (approve a push, answer a question, check his phone,
  change a setting), naming the change and what he needs to do, even if he
  seems to be in the chat.

## Tools

- **Taste skill** (`.claude/skills/taste/`): it asks for the Playwright MCP
  server. In a cloud session use the installed Playwright instead and run
  its `references/extract.js` with `page.evaluate`.
- **Refactor.** `docs/refactor.md`, run when Jose asks for "Refactor:
  CLEANUP.md items ...".
