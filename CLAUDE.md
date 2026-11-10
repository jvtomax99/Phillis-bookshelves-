# Phillis Brown Books

Static author site for Phillis Brown, published with GitHub Pages from `main` (root folder). No build step, no package manager, no tests. What is on `main` is what is live at https://jvtomax99.github.io/Phillis-bookshelves-/ a minute or two after a push (the path is case-sensitive: the lowercase `phillis-bookshelves-` returns 404).

All books are for adult readers (18+).

## Layout

- `index.html`: the whole shelf site in one file (bookshelf, book pages, About the author). CSS and JS are inline. Several looks live side by side as `:root[data-style="..."]` blocks (lounge, red, library, gallery, walnut); keep them working when changing shared styles.
- `read/<book>/index.html`: one self-contained read-along reader per book, with its narration `.mp3` and `cover.jpg` next to it. Readers save listening position and view in `localStorage`, always inside try/catch.
- `covers/`: full size and `-sm` shelf versions of each cover.
- `img/`: author portrait and face crop.
- `video/`: the promo trailer for the site (`trailer.mp4`, a 720x1280 web copy, about 3.7 MB, plus `trailer-poster.jpg`). It plays in the player opened by "Watch the trailer" on the shelf and "Trailer" on each book page. Its source lives in `promo/` on the `promo-video` branch; rebuild there with `promo/make.sh`, then re-encode the web copy at 720x1280 (crf 25, max 2.5 Mbps, faststart).
- `start/`: the start screen, a candlelit nightstand rendered in Blender (Cycles) with props from Meshy (candles, rose, lace mask). `closed-phone.webp` / `closed-desk.webp` are the waiting screen, `loop-*.mp4`/`.webm` a seamless 2 s candle-flicker loop of it (its first frame is the still; skipped under reduced motion and data saver, and when autoplay is refused, e.g. iPhone Low Power Mode), `open-*.mp4` the cover opening (flickering on from the loop's first frame) as the camera pushes in on the signed first page, `open-*.webp` that clip's sharp last frame. Phone files are portrait 780x1690, desktop files 1920x1200 (chosen by aspect ratio, landscape gets desktop). The flame glow positions in `index.html` (`FLAMES`) come from the render; re-render, re-measure. It opens on a start menu ("Enter with sound" / "Enter quietly"; a tap anywhere but Enter quietly counts as with sound), because browsers play sound only after a tap; the second tap opens the book. `start/music.m4a` (AAC, for Safari) / `music.webm` (Opus) is an original late-night lounge piece in D minor, a 58.18 s seamless loop played through Web Audio (`LOOP` in `index.html`; change both together), with a mute button while it plays and a fade-out into the shelf. Its source (`compose.py`, rendered with FluidSynth and the FluidR3 GM soundfont, MIT) is on the `start-screen-source` branch. It shows once per visit (`sessionStorage` key `pb-start-seen`), never on a `#book` link; `?start=1` forces it, `?start=0` skips it. The flyleaf line "For the ones who read after dark" is a placeholder until Phillis approves her own words.
- `icons/` and `manifest.webmanifest`: the PB monogram app icon. `icons/source.png` is the master art. Home-screen icons are full squares (the phone rounds them), tab favicons keep the rounded shape with transparent corners, and `icon-maskable-512.png` has the art shrunk to about 78% for Android's circle crop. If the art changes, regenerate every size from the new source the same way.
- `.nojekyll`: keeps GitHub Pages from running Jekyll. Do not delete.
- `SPEC.md`: what the site does, "Done when" per feature, Not in v1, Later, Phases (the open ideas once listed here moved there). `docs/ARCHITECTURE.md`: the short map of files and how data moves. Read it at the start of a session.

## Rules for this repo

- Paths must be relative. The site is served from the `/phillis-bookshelves-/` subfolder, so a link starting with `/` breaks on Pages.
- Reader pages link the icons but not the manifest, so a home-screen shortcut to a reader opens that reader instead of the shelf.
- Audio files are large (11 to 15 MB). Don't re-encode, rename or duplicate them without asking.
- After a change, serve the repo from a parent folder so the URL includes `/phillis-bookshelves-/`, and check the page in Playwright before calling it done.
- Mockups: both `index.html` and the readers put their main `<style>` in the body, after `</head>`. When injecting draft CSS for a mock, insert it before `</body>`, or the page's own rules override it and the mock lies.
- The look is fixed to walnut: `index.html` calls `applyStyle("walnut")` at start-up (line 1366) and the style switcher (`#styles`) is `hidden`. The `pb-style` key is written, and read into `savedStyle` but never used, so the other looks only show if that line changes.
- Each book's `progressKey` in `BOOKS` (`index.html`) must match `KEY` in its reader, or the shelf's progress and "Continue" lose track.

## This project: how the general rules apply here

- **Hosting.** GitHub Pages, from `main`, root folder. There are no branch previews: pushing to `main` is going live. So a "preview" here is Playwright screenshots at phone width (390 px) and desktop, taken from a local server run from the parent folder, plus a short "try this" list Jose can follow on the live site after the merge. Say plainly that the live site changes the moment the pull request is merged.
- **Real user.** Not Jose. The site is for Phillis Brown (the author) and her adult readers (18+). Jose builds it for her. Remind Jose to check plans, and any words that speak for Phillis (About text, blurbs, the flyleaf line), with Phillis before building.
- **Plan and phases.** In `SPEC.md` ("Phases"). It was drafted from the code on 2026-11-10; lines marked TO FILL wait for Jose.
- **Handoffs.** New handoffs go in `HANDOFF.md` at the repo root. There is no older handoff or notes file. `README.md` is the short public readme for the repo, not session notes; leave it as it is.
- **Not set up yet.** `DESIGN.md` and `docs/CLEANUP.md` do not exist. `docs/design-rules.md`, `docs/assets.md`, `docs/cleanup-audit.md` and `docs/refactor.md` were added on 2026-11-10; follow `docs/design-rules.md` to make `DESIGN.md` before the first design work.
- **Packages.** None. The site has no package list and no install step. Tools used only to check it (Playwright) are not project packages.

### Extras kept from the old rules (Jose, 2026-11-10)

These came from the old CLAUDE.md and go further than the general rules below. Follow them too. The old "never commit or push without asking" rule is gone: the general rules' branch, pull request and "push" flow replaced it.

- **Clickable choices, always.** Whenever there are options, a suggestion or a next step, show them as clickable buttons, recommended pick first and marked "(Recommended)", with one line on why it's the pick. (Wider than the general rules, which ask for buttons only in named cases.)
- **Show a mock of every suggestion.** Before asking the owner to choose, show what each option would look like. For anything visual, render a draft in Playwright and send the screenshot (phone width and desktop when layout differs), one per option, side by side when there are several. For text or code changes, show a short before and after in the button's preview. Build the real change only after the owner picks. (Stricter: the general rules ask for proof after building, not a mock of every option before.)
- **Notify when action is needed.** Send a phone notification every time the owner has to do something: approve a push, answer a question, check something on their phone, change a setting. Name the change and what they need to do, even if they seem to be in the chat. (Wider: the general rules ask for a notification only when a change needs Jose's "push".)

- **Public repo, paid assets.** The repo is public (checked 2026-11-10) and GitHub Pages on a free plan needs it public, so paid raw files (fonts, models) can't be committed here (docs/assets.md, section 9). Before any purchase, ask Jose: keep to free assets, or GitHub Pro / a move to Vercel so the repo can go private.
- **Taste skill.** Saved in `.claude/skills/taste/` (Senlin's, MIT; `SOURCE.md` there says where from). It asks for the Playwright MCP server; in a cloud session use the Playwright already installed instead (run its `references/extract.js` with `page.evaluate`).
- **Refactor prompt.** docs/refactor.md, run when Jose asks for "Refactor: CLEANUP.md items ...".
- **Site check.** Every pull request runs `.github/site-check.cjs` on GitHub ("Site check": missing files, links starting with "/", script errors at phone and desktop width). It must be green before asking Jose to push. Run it locally with `node .github/site-check.cjs` and the pages listed in `.github/workflows/site-check.yml`. A new page goes into that list.

# General rules (all of Jose's website projects)

Same in every project. Where the "This project" section above differs, it wins.

## Planning

- **Challenge me.** Question my ideas; no sugarcoating. Say plainly when a plan is bad, why, and what's better; name the biggest risk I'm missing. Skip small stuff. Once I've decided after hearing you out, build it my way.
- **SPEC.md** (repo root): what it does and who for (if not me, who and what they need); one or two "Done when" lines per feature; "Not in v1"; "Later"; "Phases" (build order, a checkbox list per phase, each phase one or two sessions; check it off when done and verified). New project: write it with me before any code. Existing project without one: draft it from the code, then ask me to fill the gaps and "Not in v1". Keep it current. If I ask for something not in it or on "Not in v1", say so and ask: now, or "Later"?
- **Cleanup check.** After a phase is checked off, read "Last audit" at the top of docs/CLEANUP.md. If 3 phases have been completed since then, or it's been over 30 days, or the file is missing, offer docs/cleanup-audit.md with buttons: "Run it now" (recommended), "Next session", "Skip this time". If cleanup-audit.md is missing, ask me for the prompt and save it there.
- **docs/ARCHITECTURE.md**: short and current (main folders, key files, how data moves). Read it at session start instead of exploring; update it when the structure changes.
- **Big feature** = a new page or screen, a new kind of stored data, or a new outside service. Everything else is small.
- **Big features and new projects:** first look at 2 or 3 similar tools and tell me in a few lines how they do it and where mine can be better (new ideas go to "Later" unless I approve). Before any coding, use plan mode: what you'll build and how, in plain words, with assumptions listed separately; wait for my OK. Whenever I correct you, update SPEC.md. In a scheduled or background run, do small changes only and leave the plan. If the real user isn't me, remind me to check the plan with them.

## Proof and reporting

- **Show me it works.** I can't check code, so every feature ends with proof I can see. Never say "fixed", "works" or "done" without running or testing it; say what you checked, or "not verified" and why. Small change: a screenshot or a short "try this" list. Big feature: check its "Done when" line and give me the link to a preview I can open on my phone (what a preview is here: "This project").
- **Review before the pull request.** After a phase or big feature, and before opening its pull request, a separate reviewer subagent checks the changes for bugs, broken behavior and mismatches with SPEC.md, without seeing how the code was written. Fix what it finds; tell me in 2 or 3 lines what it caught.
- **Reports:** status updates extremely concise, fragments fine. Explanations in plain full sentences. After a meaningful change, 2 or 3 plain sentences on what changed and why.
- **Ask first** before: deleting data or files I may need, changing logins or accounts, pushing to main, deploying to the live site, anything that costs money.

## Usage

- **Keep the session light.** Read only the parts of files you need. Show me only the lines of logs and test output that matter. Big searches and many-file reads go to a subagent so only its summary comes back.
- **Helpers.** Haiku subagents for repetitive work (searching, test results, summaries, checklists). Planning, decisions and code changes stay on the main model; check helpers' results before relying on them.
- **New session triggers** (tokens or share of context, whichever first; a new session costs 20k to 40k to catch up): under 150k or 50%, keep going. 150k to 300k or 50% to 75%, finish the step, then hand off. Over 300k or 75%, hand off now, even mid-task. Over 100k and the next task is unrelated: hand off. Over 100k and I tell you I've been away over an hour: hand off. Ask once with buttons, "Start a new session" (recommended) and "Keep going"; if I keep going, don't ask again until the next trigger. If I say keep going past 75%, warn me once and write HANDOFF.md anyway (auto-compact is off, so a full session just stops).
- **HANDOFF.md** (repo root, short, pointing to what exists): the goal and exact next step; what's done (commits) and what's left; this session's decisions (also added to SPEC.md); files to look at first. Overwrite it each time; in a cloud session commit and push it on the current branch. At session start, if it exists, read it first and confirm the next step with me. Delete it once its work is done (phase checked off, pull request opened).
- **Effort.** No ultracode or max effort unless I ask.
- **Keep CLAUDE.md lean.** Suggest a one-line addition for a lasting decision; remove lines that no longer apply. Keep it short: it loads every session.

## Environment and installs

- **Settings to save** (API key, environment variable, setup step): one copy-and-paste block in the format that place expects, plus one line saying exactly where to paste it. Secrets I hold: YOUR_VALUE_HERE. Never put secrets in code or commit them.
- **Ask first, with buttons** (recommended first, plus Skip), before installing anything that changes my computer, costs money, needs an account or connects to my apps (plugins, MCP servers, connectors, system programs). Say what it is and why it helps. On yes, install it yourself and check it works. Don't ask about what's installed already. In a scheduled or background run, skip it and tell me what you skipped and why.
- **Project packages:** install without asking, mention them, and add them to the package list (package.json, requirements.txt) so one command restores everything.
- **Making installs stick:** the environment's setup script runs the project's install command; for system tools outside the project, give me the copy-and-paste line to add to it.

## Git and GitHub

- **Branches.** Never commit to main. One branch per feature or fix with a plain name (add-quiz-scores). Pull the latest main and check for uncommitted work first. (A cloud session handed a branch name uses it.)
- **Commits.** Small steps, plain-English messages ("Add score screen after practice quiz"). Never commit secrets, keys or .env files; keep them in .gitignore.
- **Pushing.** A feature branch: push freely. Into main: (1) a pull request with a short plain summary, the "Done when" check and the preview link (or screenshots where there are no previews); (2) a phone notification naming the change and saying it needs my "push" (if you can't notify, put that at the very top of your message); (3) wait for my OK before merging.
- **Never without asking** (if I ask for one, first explain what it will do and what can't be undone): force push; deleting a branch with work not in main; rewriting or resetting history (git reset --hard, rebase on main); changing repo settings (like making a repo public).
- **Big files.** GitHub rejects files over 100 MB: warn me before committing one and suggest compressing it or Git LFS.
- **Undo.** After a merge, one line on how to undo it if it breaks the live site.

## Assets and design

- **Assets** (models, textures, icons, fonts, images, sounds, templates): read docs/assets.md first and follow it. If it's missing, stop, ask me to paste my asset rules, and create it before starting.
- **Design** (any page or UI): read docs/design-rules.md and DESIGN.md first and follow them. If design-rules.md is missing, stop, ask me to paste my design rules, and create it before starting.
