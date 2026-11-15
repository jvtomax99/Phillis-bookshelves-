// Offline check: run on every pull request (.github/workflows/site-check.yml).
// Proves the offline copy (sw.js) does what SPEC.md says, in a real browser:
//  1. After one visit with signal, the worker holds a complete copy.
//  2. With the site unreachable: the shelf, both book pages, About, the start
//     screen and both readers open from the copy; the readers and the trailer
//     say they need internet.
//  3. With a slow site, a page falls back to the copy after about 4 seconds.
//  4. With signal, pages come from the site, not the copy (internet first).
//  5. Both off switches ("sw": false in version.json, ?sw=off) remove the
//     worker and this site's caches.
//  6. Other apps' caches on the same address, and the saved reading places,
//     are untouched throughout.
// Usage, from the repo root: node .github/offline-check.cjs
const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium } = require('playwright');

const ROOT = process.cwd();
const SUB = '/' + path.basename(ROOT) + '/';
const problems = [];
const fail = m => { problems.push(m); console.log('  FAIL ' + m); };
const ok = m => console.log('  ok   ' + m);
const expect = (cond, m) => (cond ? ok(m) : fail(m));

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.webp': 'image/webp',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon', '.mp4': 'video/mp4', '.webm': 'video/webm',
  '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.webmanifest': 'application/manifest+json' };
// The test's switches for the "internet": down (unreachable), slow (10 s), fresh (index.html changed), off ("sw": false).
const net = { down: false, slow: false, fresh: false, off: false };
const server = http.createServer(async (req, res) => {
  if (net.down) return req.socket.destroy();
  if (net.slow) await new Promise(r => setTimeout(r, 10000));
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (!p.startsWith(SUB)) { res.writeHead(404); return res.end(); }
  const rel = p.slice(SUB.length);
  p = path.join(ROOT, rel);
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  const type = TYPES[path.extname(p).toLowerCase()] || 'application/octet-stream';
  if (rel === 'version.json' && net.off) { res.writeHead(200, { 'Content-Type': type }); return res.end('{"build":"x","sw":false}'); }
  if ((rel === 'index.html' || rel === '') && net.fresh) {
    res.writeHead(200, { 'Content-Type': type });
    return res.end(fs.readFileSync(p, 'utf8').replace('</body>', '<p id="freshMark">fresh</p></body>'));
  }
  res.writeHead(200, { 'Content-Type': type });
  fs.createReadStream(p).pipe(res);
});

const SAVED = { 'book2-pos': '123.4', 'book-ebony-club-pos': '55.5', 'book2-pos-view': '0', 'book-ebony-club-pos-view': '0', 'pb-style': 'walnut' };
const DECOYS = ['atl:/CPA-study-app/:build:test', 'pk:test', 'pbb:/someone-else/:build:x'];

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const origin = `http://127.0.0.1:${server.address().port}`, base = origin + SUB;
  const list = JSON.parse(fs.readFileSync(path.join(ROOT, 'offline-files.json'), 'utf8'));
  const kept = new Set([...list.app, ...list.start].map(f => base + f));
  const browser = await chromium.launch();

  async function visit(page, url, wait = 2500) {
    try { await page.goto(url, { waitUntil: 'load', timeout: 30000 }); }
    catch (e) { fail(`did not open: ${url.slice(origin.length)}: ${e.message.split('\n')[0]}`); return false; }
    await page.waitForTimeout(wait);
    return true;
  }
  async function waitForCopy(page) {
    for (let i = 0; i < 60; i++) {
      const s = await page.evaluate(() => window.__offline ? window.__offline() : null).catch(() => null);
      if (s && s.current) return s.current;
      await page.waitForTimeout(1000);
    }
    return null;
  }
  const cacheNames = page => page.evaluate(() => caches.keys());
  const saved = page => page.evaluate(keys => Object.fromEntries(keys.map(k => [k, localStorage.getItem(k)])), Object.keys(SAVED));

  // ---------- 1. A visit with signal ----------
  console.log('1. A visit with signal leaves a complete copy');
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  page.on('pageerror', e => fail(`script error on ${page.url().slice(origin.length)}: ${String(e.message || e).split('\n')[0]}`));
  let offlinePhase = false;
  page.on('requestfailed', r => { if (offlinePhase && kept.has(r.url().split(/[?#]/)[0])) fail(`kept file failed offline: ${r.url().slice(origin.length)}`); });
  await visit(page, base + 'index.html?start=0', 500);
  await page.evaluate(async ({ saved, decoys }) => {
    for (const [k, v] of Object.entries(saved)) localStorage.setItem(k, v);
    for (const d of decoys) await (await caches.open(d)).put('/decoy', new Response('decoy'));
  }, { saved: SAVED, decoys: DECOYS });
  await visit(page, base + 'index.html?start=0', 500);
  const build = await waitForCopy(page);
  expect(build === list.build, `the worker holds build ${list.build} (got ${build})`);
  const names = await cacheNames(page);
  expect(names.includes(`pbb:${SUB}:build:${list.build}`), 'the copy is in its own pbb: cache');

  // ---------- 2. No signal ----------
  console.log('2. No signal: everything kept opens from the copy');
  net.down = true; offlinePhase = true;
  if (await visit(page, base + 'index.html?start=0')) {
    expect(await page.locator('#stage').isVisible(), 'the shelf opens');
    await page.locator('[data-trailer]').first().click().catch(() => {});
    await page.waitForTimeout(2000);
    expect(await page.locator('#trOff').isVisible(), 'the trailer says it needs internet');
  }
  for (const [hash, what] of [['#reign-is-mine', 'Reign Is Mine'], ['#ebony-the-club', 'Ebony'], ['#about', 'About']]) {
    if (await visit(page, base + 'index.html' + hash)) expect(await page.locator('#detail').isVisible(), `the ${what} page opens`);
  }
  if (await visit(page, base + 'index.html?start=1', 3000)) expect(await page.locator('#start').isVisible(), 'the start screen opens');
  for (const b of ['reign-is-mine', 'ebony-the-club']) {
    if (await visit(page, base + `read/${b}/index.html`, 3000)) {
      const words = await page.evaluate(() => document.body.textContent.length);
      expect(words > 20000, `the ${b} reader shows its text`);
      await page.locator('#play').click().catch(() => {});
      await page.waitForTimeout(1500);
      expect(await page.locator('#offlineNote').isVisible(), `the ${b} reader says the narration needs internet`);
    }
  }
  offlinePhase = false;

  // ---------- 3. A slow signal ----------
  console.log('3. A slow signal: the page falls back to the copy');
  net.down = false; net.slow = true;
  const t0 = Date.now();
  await visit(page, base + 'index.html?start=0', 0);
  const took = Date.now() - t0;
  expect(took < 8000, `the shelf opened in ${(took / 1000).toFixed(1)} s, not the server's 10 s`);
  net.slow = false;
  await page.waitForTimeout(10500);         // let the slow requests finish

  // ---------- 4. With signal ----------
  console.log('4. With signal: pages come from the site');
  net.fresh = true;
  await visit(page, base + 'index.html?start=0', 500);
  expect(await page.locator('#freshMark').count() === 1, 'a change on the site shows on the next visit');
  net.fresh = false;

  // ---------- 5. Off switches ----------
  console.log('5. Off switches remove the worker and only this site\'s caches');
  net.off = true;
  await visit(page, base + 'index.html?start=0', 3000);
  let regs = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).length);
  let mine = (await cacheNames(page)).filter(k => k.startsWith(`pbb:${SUB}:`));
  expect(regs === 0 && mine.length === 0, `"sw": false removes the worker and the copy (${regs} workers, ${mine.length} caches left)`);
  net.off = false;
  await visit(page, base + 'index.html?start=0', 500);
  await waitForCopy(page);
  await visit(page, base + 'index.html?start=0&sw=off', 3000);
  regs = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).length);
  mine = (await cacheNames(page)).filter(k => k.startsWith(`pbb:${SUB}:`));
  expect(regs === 0 && mine.length === 0, `?sw=off removes the worker and the copy (${regs} workers, ${mine.length} caches left)`);

  // ---------- 6. Untouched ----------
  console.log('6. Other apps\' caches and the saved reading places are untouched');
  const left = await cacheNames(page);
  expect(DECOYS.every(d => left.includes(d)), 'other apps\' caches are still there');
  const now = await saved(page);
  expect(Object.entries(SAVED).every(([k, v]) => now[k] === v), 'the saved reading places are unchanged: ' + JSON.stringify(now));

  await ctx.close();
  await browser.close();
  server.close();
  if (problems.length) { console.log(`Offline check found ${problems.length} problem(s).`); process.exit(1); }
  console.log('Offline check passed.');
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
