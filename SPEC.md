# SPEC: Phillis Brown Books

Drafted from the code on 2026-11-10. Gaps marked TO FILL for Jose.

## What it does

A static author site for Phillis Brown. Visitors land on a candlelit start screen, then a wood bookshelf. Each book turns to show its cover and opens into its own page with a blurb, a content note and a button to read or listen. Each book has its own read-along reader: the story's text on turning pages, with Phillis's narration playing and the text following it.

Live: https://jvtomax99.github.io/Phillis-bookshelves-/ (GitHub Pages, from `main`).

## Who it's for

- **Phillis Brown**, the author. She needs a site that looks like her books (steamy, late-night, elegant), shows her stories and lets people hear them. Words that speak for her (About text, blurbs, the flyleaf line) need her OK.
- **Her readers**, adults 18+, mostly on phones. They need to find a story, see what it is about and what it contains, then read or listen, and pick up where they left off.
- Jose builds and runs the site for her.
- TO FILL: does Phillis want anything from the site beyond showing the books (sales, a mailing list, news)?

## Features

### Start screen
A rendered nightstand with flickering candles. A start menu says the site is for adults 18+ and offers "Enter with sound" or "Enter quietly". A tap opens the book onto a signed first page, then the shelf. Music loops until the shelf appears, with a mute button. A "Continue" link jumps back into the story with the most listening saved. Shown once per visit, never on a book link.
- Done when: a first-time visitor on a phone sees the menu, taps in with sound, hears the music, watches the book open and lands on the shelf; reloading in the same visit skips it.
- Done when: with reduced motion, data saver or Low Power Mode, the still image shows and the screen still opens to the shelf.

### Bookshelf
An endless wood shelf of the two books with props (wine glass, rose, bookends). The picked book turns to show its cover, with its title, details, "Open the book" and "Watch the trailer" below. Move by swipe, wheel, arrow keys or the dots. Each spine shows how far the reader has listened.
- Done when: a visitor can move between both books on a phone and a laptop and open either one.

### Book page
The page unfolds from the book in the book's own colours: cover, title, details, blurb, a folded "Content note", then "Read or listen" (or "Continue" with minutes in), "Trailer", and "Kindle edition coming soon" or "Buy on Amazon" once a link is set. If listening is saved, a progress bar and "Start over" show. Each book has its own link (`#reign-is-mine`, `#ebony-the-club`).
- Done when: a visitor opens a book, reads the content note, taps "Read or listen" and reaches that book's reader; a shared `#book` link opens straight to that page.

### About the author
Opened from the name at the top (`#about`). Photo, a short bio and a button for each book.
- Done when: a visitor opens About, then jumps from it to either book's page.
- TO FILL: Phillis to confirm the bio text.

### Trailer
A video player over the page with the promo for both books (`video/trailer.mp4`, captioned "Adults 18+, Sound on").
- Done when: the trailer plays from the shelf and from each book page, and closes with the X, a tap outside or Escape.

### Read-along readers
One page per book (`read/<book>/`): a black satin hardcover that opens to a two-page spread on wide screens and one page on phones. Play the narration and the text follows it sentence by sentence, marking his voice and hers. Chapters, page turns, back and forward 15 s, a seek bar, playback speed, and "Back to the narration" after reading ahead. A button returns to the shelf. Position and page are saved on the device; finishing the story clears the position.
- Done when: a reader starts a story on a phone, closes it partway, comes back and continues from the same spot; the shelf shows the same progress.

### App icon
The PB monogram as the tab icon and home-screen icon (`manifest.webmanifest`).
- Done when: "Add to Home Screen" on iPhone and Android shows the monogram and opens the shelf.

### Access for everyone
Keyboard use (arrow keys, Enter, Escape, visible focus), screen reader labels, and calmer motion under reduced motion.
- Done when: the whole site can be used with the keyboard alone, and nothing big moves under reduced motion.

## Not in v1

- "Buy on Amazon" links: the code is ready (`amazon:""` in `BOOKS`), waiting for the Kindle editions. TO FILL: the links, when live.
- An age check on direct book links and on the readers: the 18+ note only shows on the start screen, which a `#book` link or a reader link skips. (drafted from code, Jose to confirm)
- Style picker for visitors: five other looks exist in the code, but the site is fixed to walnut and the picker is hidden. (drafted from code, Jose to confirm)
- TO FILL: Jose's own list.

## Later

- Reader auto-open: when arriving from "Read or listen", open the cover by itself instead of asking for a second tap. Trade-off: loses the open-it-yourself moment. (mocked, not built; from the old CLAUDE.md, Jose to confirm)
- Phone landscape shelf: a compact header helps but "Open the book" is still partly cut off at 390 px tall; a real fix puts the caption beside the books. (mocked, not built; from the old CLAUDE.md, Jose to confirm)
- The flyleaf line "For the ones who read after dark" is a placeholder until Phillis approves her own words. (drafted from code, Jose to confirm)
- More books on the shelf. TO FILL: is a third book coming?

## Phases

Grouped from the git history (21 commits on `main`).


- [x] Phase 1: the shelf site. Bookshelf, book pages, About, both readers with narration, GitHub Pages.
- [x] Phase 2: app icon. PB monogram, home-screen and tab icons.
- [x] Phase 3: polish. Reader header and player, spine lettering, "Read or listen" in view on phones and laptops, ragged-right reader text, keyboard focus, bigger books on tall screens, Ebony's full description and content note.
- [x] Phase 4: trailer. Promo video on the shelf and each book page.
- [x] Phase 5: start screen. Rendered nightstand, candle-flicker loop, opening clip, start menu with music.
- [ ] Phase next: to decide with Jose.
