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

# General rules (all of Jose's website projects)

These are the same in every project. Where this project works differently
(hosting, file names, who the real user is), the "This project" section above
says so, and it wins.

## Planning and working with me

**Challenge me.** Question my ideas. Don't sugarcoat problems. If a plan is bad, say so and why, then give me a better option. Point out the biggest risk I'm not seeing. Don't argue over small stuff, and once I've decided after hearing you out, build it my way.

**Spec.** Every project has a SPEC.md in the repo root with:
- What it does and who it's for. If the real user isn't me, say who it is and what they need.
- A "Done when" line or two for each feature (example: "A user can finish a practice quiz and see their score").
- A "Not in v1" list of things we're deliberately not building yet.
- A "Later" list for ideas we're saving.

New project with no SPEC.md: help me write it before any code.
Existing project with no SPEC.md: write one from the current code, then ask me to fill the gaps and the "Not in v1" list.
Keep SPEC.md updated when decisions change. If I ask for something on the "Not in v1" list or not in the spec, point it out and ask whether to add it now or move it to "Later."

**Phases.** SPEC.md has a "Phases" section: the build order, each phase as a short list of features with a checkbox. Each phase should fit in one or two sessions. When a phase is done and verified, check it off.

**Cleanup check.** After a phase is checked off, look at the "Last audit" line at the top of docs/CLEANUP.md. If 3 phases have been completed since then, or it's been more than 30 days, or the file doesn't exist yet, offer to run the cleanup audit in docs/cleanup-audit.md, with buttons: "Run it now" (recommended), "Next session," or "Skip this time." If docs/cleanup-audit.md doesn't exist, ask me to paste my cleanup audit prompt and save it there first.

**Architecture doc.** Keep docs/ARCHITECTURE.md short and current: the main folders, the key files and what each does, and how data moves through the app. Read it at the start of a session instead of exploring the code. Update it whenever the structure changes.

**Big vs small.** A big feature adds a new page or screen, stores new kinds of data, or connects to an outside service. Everything else is a small change.

**Research before big features.** For a new project or a big feature, look at 2 or 3 similar tools or sites first. Tell me in a few lines how they do it and where mine can be better. New ideas from research go into "Later" unless I approve them for now. Skip this for small changes.

**Explain it back.** Before coding a new project or big feature, use plan mode. Explain in plain words what you'll build and how it works, then list your assumptions separately (example: "progress saves across devices"). Wait for my OK. If I correct you, update SPEC.md.
If I'm not around to approve, like in a scheduled or background run, don't start big features. Do small changes only and leave me the plan to review.
If the real user isn't me, remind me to check the plan with them before building.

**Show me it works.** I can't read code well enough to check it, so every feature ends with proof I can see. Never say "fixed," "works," or "done" without actually running or testing it, and say what you checked. If you couldn't check it, say "not verified" and why.
- Small changes: a screenshot or a short "try this" list of steps.
- Big features: check against the "Done when" line, put up a preview I can open on my phone (see "This project" for what a preview is here), and give me the link.

**Review before the pull request.** When a phase or big feature is done, have a separate reviewer subagent check the changes before opening the pull request. It looks for bugs, broken behavior, and anything that doesn't match SPEC.md, without seeing how the code was written. Fix what it finds, then tell me in two or three lines what it caught.

**Status updates.** When reporting progress or what you did, be extremely concise: short fragments are fine. This is for updates only; explanations stay in plain, full sentences.

**Help me learn.** After a meaningful change, explain in 2 or 3 plain sentences what you changed and why.

**Ask before anything risky.** Explain it and get my OK before you:
- Delete data or files I may need.
- Change how logins or accounts work.
- Push to the main branch.
- Deploy to the live site.
- Do anything that costs money.

## Usage

**Keep the session light.** Every step re-sends the whole session, so a heavy session burns usage on everything after it. Prevent bloat first:
- Read only the parts of files you need, not whole files.
- Don't paste full logs or test output. Show me only the lines that matter.
- For big searches or reading many files, use a subagent so only its summary lands in this session.

**Helpers.** Use Haiku subagents for repetitive work (searching, reading test results, summaries, checking lists). Keep planning, decisions, and code changes on the main model, and check the helpers' results before relying on them.

**When to start a new session.** A new session costs about 20k to 40k tokens to get back up to speed, so only switch when it saves more than that. Triggers (token count or share of the context window, whichever comes first):
- Under 150k or 50%: keep going.
- 150k to 300k or 50% to 75%: finish the current step, then hand off.
- Over 300k or 75%: hand off now, even mid-task.
- Next task is unrelated and the session is over 100k: hand off.
- I tell you I've been away more than an hour and the session is over 100k: hand off.

When a trigger hits, ask me once with buttons: "Start a new session" (recommended) and "Keep going." If I say keep going, don't ask again until the next trigger.
Auto-compact is off, so a full session just stops and leaves no room for a handoff. If I say keep going past 75%, warn me once, and write HANDOFF.md anyway so it's ready.

**Handoffs.** Write HANDOFF.md in the repo root, short and pointing to what already exists:
- The goal and the exact next step.
- What's done (point to commits) and what's left.
- Decisions made this session that aren't in SPEC.md yet. Add them to SPEC.md too.
- Files I'll need to look at first.

Overwrite it each time. In a cloud session, commit and push it on the current branch so the next session can see it.
At the start of a session, if HANDOFF.md exists, read it first and confirm the next step with me.
When the work it describes is done (phase checked off, pull request opened), delete HANDOFF.md so the next session doesn't follow stale instructions.

**Effort.** Don't use ultracode or max effort unless I ask.

**Keep CLAUDE.md lean.** When we make a decision that should last, suggest a one-line addition to CLAUDE.md. Remove lines that no longer apply. Keep it short, since it loads every session.

## Environment and installs

**Saving settings.** When something needs to be saved outside this session, like an API key, password, environment variable, or setup step, give it to me as one copy-and-paste block. Tell me in one line exactly where to paste it. Use the format that place expects. If it's a secret only I have, write YOUR_VALUE_HERE instead of the real value. Never put secrets in code files or commit them to the repo.

**Installing tools.** Ask me first, with clickable buttons, before installing anything that changes my computer, costs money, needs an account, or connects to my apps (plugins, MCP servers, connectors, system programs). Tell me what it is and why it helps, put your recommended choice first, and include a Skip option. If I say yes, install it yourself and check that it works. Don't ask about things already installed. If you can't ask me, like in a scheduled or background run, skip the install and tell me what you skipped and why.

**Project packages.** Normal packages this project needs, install without asking and mention them. Always add them to the project's package list (package.json, requirements.txt, or whatever this project uses) so one install command brings everything back.

**Making installs stick.** Cloud sessions erase installs when they end. My environment's setup script should run the project's install command (like npm install). For system tools that live outside the project, give me the copy-and-paste line to add to the setup script so they install automatically next time.

## Git and GitHub

**Branches.** Never commit directly to main. For each feature or fix, make a new branch with a plain name (like add-quiz-scores or fix-login-button). Before starting, pull the latest main and check for uncommitted work so nothing gets overwritten. (A cloud session that was handed a branch name uses that branch.)

**Commits.** Commit in small steps, each with a plain-English message that says what changed (like "Add score screen after practice quiz"). Never commit secrets, API keys, or .env files. Make sure they're in .gitignore.

**Pushing.** Pushing a feature branch is fine without asking (previews need it, where the project has them).
Getting work into main always needs my OK:
1. Open a pull request with a short plain summary, the "Done when" check from SPEC.md, and the preview link (or the screenshots, where the project has no previews).
2. Send me a phone notification saying which change it is and that it needs my "push." If you can't send a notification, put that at the very top of your message instead.
3. Wait for my OK before merging.

**Never without asking:**
- Force push.
- Delete branches that have work not yet in main.
- Rewrite or reset history (git reset --hard, rebase on main, and similar).
- Change repo settings, like making a repo public.

If I ask you to do one of these, explain what it will do and what can't be undone first.

**Big files.** GitHub rejects files over 100 MB. If an asset is that big, warn me before committing and suggest compressing it or using Git LFS.

**Undo.** When you merge something, tell me in one line how to undo it if it breaks the live site.

## Assets

Before any asset work (3D models, textures, icons, fonts, images, sounds, templates), read docs/assets.md and follow it. If docs/assets.md doesn't exist yet, stop and ask me to paste my asset rules, then create it before starting.

## Design

Before building or changing any page or UI, read docs/design-rules.md and DESIGN.md and follow them. If docs/design-rules.md doesn't exist yet, stop and ask me to paste my design rules, then create it before starting.
