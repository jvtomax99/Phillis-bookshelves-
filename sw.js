// The offline copy. Keeps one whole copy of the site on the phone (shelf, book
// pages, About, both readers' text) and uses it ONLY when the internet does not
// answer. With signal, every page and file comes from the live site as before.
// Adapted from the CPA app's worker (jvtomax99/CPA-study-app, sw.js).
//
// How a copy gets here:
//   - "check": this worker reads version.json from the network (8 s after a
//     page opens with signal, and when the page asks). A build it does not
//     hold is staged. `"sw": false` there removes this worker and its caches.
//   - "stage": every file in offline-files.json is fetched into a cache of its
//     own, named after the build, and compared with the fingerprint (SHA-1)
//     the list gives for it. One wrong or missing file and the whole cache is
//     thrown away; the next check tries again. So a stale file from GitHub
//     Pages' 10-minute cache can never get into the copy.
//   - A finished copy is used at once: it only ever serves when offline.
//
// Shared address: several of Jose's apps live on jvtomax99.github.io and share
// cache storage. This worker only ever opens or deletes caches whose name
// starts with PREFIX. Never delete any other cache.
//
// Never served or touched here: the narration (.mp3), the trailer (video/*.mp4),
// other sites (Google Fonts), version.json, offline-files.json and this file.
// Saved progress lives in localStorage, which a worker cannot reach.
// Off switches: `?sw=off` on the shelf, or `"sw": false` in version.json.
// tools/offline.cjs writes offline-files.json and version.json.
const SCOPE = new URL(self.registration.scope).pathname;
const PREFIX = `pbb:${SCOPE}:`;
const META = PREFIX + 'meta', META_URL = SCOPE + '__offline-state';
const cacheOf = build => PREFIX + 'build:' + build;
const NONE = {current: null};
const WAIT = 4000;                         // a request waits this long for the internet, then uses the copy

let state = null;                          // {current} (a build name)
let gone = false;                          // set by the off switch
async function readState() {
  if (state) return state;
  // (Looked up without opening, so a worker on its way out leaves no empty cache behind.)
  const r = await caches.match(META_URL, {cacheName: META});
  return state = r ? await r.json() : NONE;
}
async function writeState(s) {
  if (gone) return;                        // switched off: write nothing back
  await (await caches.open(META)).put(META_URL, new Response(JSON.stringify(s), {headers: {'content-type': 'application/json'}}));
  state = s;                               // only once it is really saved
}
// Remove this site's caches of builds that are neither served nor being staged.
async function tidy() {
  const s = await readState(), keep = new Set([META, s.current && cacheOf(s.current), staging && cacheOf(staging.build)]);
  for (const k of await caches.keys()) if (k.startsWith(PREFIX) && !keep.has(k)) await caches.delete(k);
}

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

const held = async build => !!(await caches.match(SCOPE + 'index.html', {cacheName: cacheOf(build)}));
const hex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');

// Fetch a whole build into its own cache. All or nothing.
let staging = null;                        // {build, done: Promise<boolean>}
function stage(build, kinds) {
  if (staging) return staging.build === build ? staging.done : Promise.resolve(false);   // one at a time
  const done = (async () => {
    const s = await readState();
    // (Held already? Only if its cache is really there: the browser may have cleared it.)
    if (s.current === build && await held(build)) return true;
    const name = cacheOf(build);
    let failed = false;
    try {
      const list = await (await fetch(SCOPE + 'offline-files.json', {cache: 'no-store'})).json();
      // (The list and version.json can come from different moments: only a list made for this build will do.)
      if (list.build !== build || !list.sha1) throw new Error('list is for another build');
      const files = [...list.app, ...kinds.flatMap(k => list[k] || [])];
      await caches.delete(name);
      const cache = await caches.open(name);
      // (Six at a time. `no-cache` asks the server whether the phone's own
      // copy is still right, so a file already here is not sent twice.)
      let i = 0;
      const next = async () => {
        while (i < files.length && !failed) {
          const f = files[i++];
          try {
            const r = await fetch(SCOPE + f, {cache: 'no-cache'});
            if (!r.ok || r.status !== 200) throw new Error(f + ' ' + r.status);
            const body = await r.arrayBuffer();
            if (hex(await crypto.subtle.digest('SHA-1', body)) !== list.sha1[f]) throw new Error(f + ' is not this build\'s');
            const headers = {'content-type': r.headers.get('content-type') || 'application/octet-stream'};
            await cache.put(SCOPE + f, new Response(body, {status: 200, headers}));
          } catch (err) { failed = true; throw err; }
        }
      };
      await Promise.all(Array.from({length: 6}, next));
      if (gone) throw new Error('switched off');
      await writeState({current: build});
      await tidy();
      return true;
    } catch (err) {
      await caches.delete(name);
      return false;
    }
  })();
  const mine = staging = {build, done};
  done.finally(() => { if (staging === mine) staging = null; });
  return done;
}

// Remove the copy and this worker (the off switch). Only this site's caches.
async function off() {
  gone = true;
  for (const k of await caches.keys()) if (k.startsWith(PREFIX)) await caches.delete(k);
  state = NONE;
  await self.registration.unregister();
}

// Read version.json from the network and act on it.
async function check(wait) {
  if (wait) await new Promise(r => setTimeout(r, wait));
  if (gone) return;
  let v;
  try { v = await (await fetch(SCOPE + 'version.json', {cache: 'no-store'})).json(); } catch (err) { return; }   // no signal
  if (!v || typeof v !== 'object') return;
  if (v.sw === false) return off();
  if (typeof v.build !== 'string') return;
  // (With data saver on, the start screen's clips and music are left out; it shows its still instead.)
  const saver = self.navigator.connection && self.navigator.connection.saveData;
  await stage(v.build, saver ? [] : ['start']);
}

self.addEventListener('message', e => {
  const m = e.data || {}, reply = x => e.ports[0] && e.ports[0].postMessage(x);
  if (m.cmd === 'off') e.waitUntil(off().catch(() => {}));
  else if (m.cmd === 'check') e.waitUntil(check(0).catch(() => {}));
  else if (m.cmd === 'state') e.waitUntil(readState().catch(() => NONE).then(s => reply({current: s.current, busy: !!staging})));
});

// A piece of a kept file (videos are asked for in pieces).
async function slice(res, range) {
  const m = /^bytes=(\d*)-(\d*)$/.exec(range), buf = await res.arrayBuffer(), size = buf.byteLength;
  if (!m || (m[1] === '' && m[2] === '')) return new Response(buf, {status: 200, headers: res.headers});
  let from = m[1] === '' ? size - +m[2] : +m[1], to = m[1] === '' || m[2] === '' ? size - 1 : Math.min(+m[2], size - 1);
  from = Math.max(0, from);
  if (from > to || from >= size) return new Response(null, {status: 416, headers: {'content-range': `bytes */${size}`}});
  const headers = new Headers(res.headers);
  headers.set('content-range', `bytes ${from}-${to}/${size}`);
  headers.set('content-length', String(to - from + 1));
  headers.set('accept-ranges', 'bytes');
  return new Response(buf.slice(from, to + 1), {status: 206, headers});
}

// The kept file for a request, or nothing.
async function fromCopy(path, req) {
  const s = await readState();
  if (!s.current) return null;
  // (Matched by path alone, so index.html?start=0 finds its file.)
  const hit = await caches.match(SCOPE + path, {cacheName: cacheOf(s.current)});
  if (!hit) return null;
  return req.headers.has('range') ? slice(hit, req.headers.get('range')) : hit;
}

// The network, unless it fails or has not answered within WAIT (a weak signal) and the
// copy has the file; then the copy. Not kept: wait for the network, as without this worker.
let slowAt = 0;                            // when the internet last failed to answer in time
async function networkFirst(req, path) {
  // (Just found slow: for the next half minute a page's pictures and clips come from the
  // copy straight away, so a visit waits once, not once for the page and again for every
  // picture on it. Pages themselves always ask the internet first.)
  const page = req.mode === 'navigate';
  if (!page && Date.now() - slowAt < 30000) { const hit = await fromCopy(path, req).catch(() => null); if (hit) return hit; }
  const net = fetch(req);
  net.catch(() => {});                     // (if the copy wins, a late failure is nobody's business)
  const first = await Promise.race([net.then(r => r, () => 'fail'), new Promise(r => setTimeout(r, WAIT, 'slow'))]);
  if (first !== 'slow' && first !== 'fail') { if (page) slowAt = 0; return first; }
  if (first === 'slow') slowAt = Date.now();
  const hit = await fromCopy(path, req).catch(() => null);
  return hit || net;                       // not kept: as it would have been without this worker
}

self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin || !url.pathname.startsWith(SCOPE)) return;
  let path = url.pathname.slice(SCOPE.length);
  // Left entirely alone: the build's fingerprint, this script, the list, the narration and the trailer.
  if (/^(version\.json|sw\.js|offline-files\.json)$/.test(path) || /\.mp3$/i.test(path) || /^video\/.*\.mp4$/i.test(path)) return;
  const page = req.mode === 'navigate';
  if (page && (path === '' || path.endsWith('/'))) path += 'index.html';
  else if (page && !/\.[a-z0-9]+$/i.test(path)) path += '/index.html';   // read/<book> without its last slash
  // Each time a page opens with signal, look for a newer copy (or the off switch) once it has had time to start.
  if (page) e.waitUntil(check(8000).catch(() => {}));
  e.respondWith(networkFirst(req, path));
});
