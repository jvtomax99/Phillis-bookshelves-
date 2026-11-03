// Renders frames [a, b) of promo.html to build/frames. Run via make.sh.
const {chromium} = require('playwright');
const [a, b, port] = process.argv.slice(2, 5).map(Number);
const repoDir = process.argv[5];
(async () => {
  const br = await chromium.launch();
  const p = await br.newPage({viewport: {width: 1080, height: 1920}});
  p.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
  const res = await p.goto(`http://127.0.0.1:${port}/${repoDir}/promo/promo.html`);
  if (!res.ok()) throw new Error('promo.html not found: HTTP ' + res.status());
  await p.evaluate(() => window.ready);
  for (let f = a; f < b; f++) {
    await p.evaluate(t => render(t), f / 30);
    await p.screenshot({path: `${__dirname}/build/frames/f${String(f).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93});
  }
  await br.close();
})();
