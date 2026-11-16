// Makes the share pictures in share/ (1200x630), the picture a link shows when it
// is texted or posted. Run from the repo root after a cover or a title changes:
//   node tools/share-cards.cjs
// then run node tools/offline.cjs and commit both. Needs the installed Playwright
// and internet for the Google fonts (without them the lettering falls back).
// The words here speak for Phillis: show Jose before changing them.
const fs = require('fs'), path = require('path'), { pathToFileURL } = require('url');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const cover = id => pathToFileURL(path.join(root, 'covers', id + '.jpg')).href;

const CARDS = {
  'shelf': { covers: ['reign-is-mine', 'ebony-the-club'], kicker: 'Short stories', title: 'Phillis<br><em>Brown</em>',
    pull: 'Steamy short reads for grown readers.<br>Read them, or listen.', sign: false },
  'reign-is-mine': { covers: ['reign-is-mine'], kicker: 'A short story', title: 'Reign<br>Is <em>Mine</em>',
    pull: 'He chose her.<br>She chose him anyway.', sign: true },
  'ebony-the-club': { covers: ['ebony-the-club'], kicker: 'A short story', title: 'Ebony<br><em>The Club</em>',
    pull: 'He never showed.<br>She showed him the door.', sign: true },
};

// Walnut colours from DESIGN.md.
const page = c => `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..700&family=Instrument+Sans:wght@400;600&family=Pinyon+Script&display=swap">
<style>
html,body{margin:0}
.c{width:1200px;height:630px;position:relative;overflow:hidden;display:flex;align-items:center;gap:56px;padding:0 80px;box-sizing:border-box;
  background:radial-gradient(ellipse 70% 90% at 30% 0%,#3a2416 0%,#24160F 45%,#110A06 100%);color:#F6ECDF;font-family:"Instrument Sans",Helvetica,Arial,sans-serif}
.c:after{content:"";position:absolute;inset:22px;box-shadow:inset 0 0 0 1px rgba(201,162,91,.55)}
.covers{display:flex;gap:26px;flex:none}
.covers img{height:${c.covers.length > 1 ? 420 : 470}px;border-radius:2px;box-shadow:inset 0 0 0 1px #C9A25B,0 24px 40px -14px rgba(40,20,10,.8)}
.t{flex:1;min-width:0}
.k{font-weight:600;font-size:20px;letter-spacing:.14em;text-transform:uppercase;color:#CDB9A4}
h1{font-family:"Bodoni Moda",Georgia,serif;font-weight:500;font-size:76px;line-height:1.02;margin:18px 0 8px}
h1 em{color:#C9A25B}
.rule{width:80px;height:1px;background:#C9A25B;margin:14px 0}
.pull{font-family:"Bodoni Moda",Georgia,serif;font-style:italic;font-size:32px;line-height:1.25;margin:18px 0 26px}
.by{font-family:"Pinyon Script",cursive;font-size:52px;color:#C9A25B}
.age{position:absolute;right:56px;bottom:46px;font-weight:600;font-size:18px;letter-spacing:.14em;color:#CDB9A4}
</style></head><body><div class="c">
<div class="covers">${c.covers.map(id => `<img src="${cover(id)}" alt="">`).join('')}</div>
<div class="t"><div class="k">${c.kicker}</div><h1>${c.title}</h1><div class="rule"></div><div class="pull">${c.pull}</div>${c.sign ? '<div class="by">Phillis Brown</div>' : ''}</div>
<div class="age">ADULTS 18+</div></div></body></html>`;

(async () => {
  const out = path.join(root, 'share');
  fs.mkdirSync(out, { recursive: true });
  const tmp = path.join(out, '.card.html');
  const browser = await chromium.launch();
  const p = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  try {
    for (const [name, c] of Object.entries(CARDS)) {
      fs.writeFileSync(tmp, page(c));
      await p.goto(pathToFileURL(tmp).href, { waitUntil: 'load' });
      await p.evaluate(() => document.fonts.ready);
      await p.waitForTimeout(300);
      await p.screenshot({ path: path.join(out, name + '.jpg'), type: 'jpeg', quality: 86 });
      console.log('share/' + name + '.jpg');
    }
  } finally {
    fs.rmSync(tmp, { force: true });
    await browser.close();
  }
})();
