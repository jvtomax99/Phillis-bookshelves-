// Writes the offline copy's file list (offline-files.json) and its fingerprint
// (version.json). sw.js keeps these files on the phone; how it works is at its top.
// This site has no build step, so this stands in for one.
//
// Run from the repo root after changing ANY file the site loads, and commit
// what it writes:   node tools/offline.cjs
// CI only compares (and fails if they are stale):   node tools/offline.cjs --check
//
// version.json's "build" is a fingerprint of every kept file, so it changes
// whenever anything kept changes and never has to be bumped by hand.
// "sw": false in version.json is the off switch; this script keeps it as it was.
//
// Kept ("app"): index.html, the manifest, icons/ (not source.png, 2 MB and not
// loaded), covers/, img/, the start screen's stills, the trailer's poster,
// each reader's page and cover, and each book's share-link page in book/. Kept unless data saver is on ("start"): the
// start screen's clips and music. Never kept: the narration (.mp3) and the
// trailer (video/*.mp4), which stay online-only, and share/ (the pictures link
// apps fetch for a card; no page loads them). A new kind of file, or a file
// in a new folder, must be added to the rules below.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const root = path.resolve(__dirname, '..');

const ls = (dir, test) => {
  const full = path.join(root, dir);
  if (!fs.existsSync(full)) return [];
  return fs.readdirSync(full).filter(f => fs.statSync(path.join(full, f)).isFile() && test(f))
    .map(f => (dir ? dir + '/' : '') + f).sort();
};
const books = fs.readdirSync(path.join(root, 'read'))
  .filter(d => fs.statSync(path.join(root, 'read', d)).isDirectory()).sort();

const keep = {
  app: ['index.html', 'manifest.webmanifest']
    .concat(ls('icons', f => f !== 'source.png'))
    .concat(ls('covers', () => true))
    .concat(ls('img', () => true))
    .concat(ls('start', f => f.endsWith('.webp')))
    .concat(['video/trailer-poster.jpg'])
    .concat(books.flatMap(b => ls('read/' + b, f => f === 'index.html' || f === 'cover.jpg')))
    .concat(books.flatMap(b => ls('book/' + b, f => f === 'index.html'))),
  start: ls('start', f => /\.(mp4|webm|m4a)$/.test(f)),
};

const all = [...keep.app, ...keep.start];
for (const f of all) if (/\.mp3$/i.test(f) || /^video\/.*\.mp4$/i.test(f)) throw new Error('never keep ' + f);
const sha1 = {};
for (const f of all) sha1[f] = crypto.createHash('sha1').update(fs.readFileSync(path.join(root, f))).digest('hex');
const mark = crypto.createHash('sha1').update(all.map(f => f + '\0' + sha1[f] + '\n').join('')).digest('hex').slice(0, 12);

const lpath = path.join(root, 'offline-files.json'), vpath = path.join(root, 'version.json');
let was = {};
try { was = JSON.parse(fs.readFileSync(vpath, 'utf8')); } catch (e) {}
const on = was.sw !== false;
const listing = JSON.stringify({build: mark, ...keep, sha1}, null, 1) + '\n';
const version = JSON.stringify({build: mark, sw: on}) + '\n';

if (process.argv.includes('--check')) {
  let same = false;
  try { same = fs.readFileSync(lpath, 'utf8') === listing && was.build === mark; } catch (e) {}
  if (!same) { console.error('FAIL: offline-files.json or version.json does not match the files in the repo. Run: node tools/offline.cjs, and commit what it writes.'); process.exit(1); }
  console.log(`offline copy: the list and version.json match the repo (${all.length} files, build ${mark})`);
  if (!on) console.log('::warning::Offline is switched OFF for everyone: version.json says "sw": false. Set it to true to switch it back on.');
  process.exit(0);
}
fs.writeFileSync(lpath, listing);
fs.writeFileSync(vpath, version);
const size = all.reduce((n, f) => n + fs.statSync(path.join(root, f)).size, 0);
const appSize = keep.app.reduce((n, f) => n + fs.statSync(path.join(root, f)).size, 0);
console.log(`offline copy: ${all.length} files, ${(size / 1e6).toFixed(1)} MB (${(appSize / 1e6).toFixed(1)} MB without the start screen's clips and music), build ${mark}` + (on ? '' : '  (switched OFF: "sw": false in version.json)'));
