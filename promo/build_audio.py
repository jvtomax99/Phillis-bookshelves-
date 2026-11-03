# Builds timeline.json (scenes, narration clips with word times, hits) and mix.wav.
import json, subprocess, wave, os
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, '..', 'read')
OUT = os.path.join(HERE, 'build')
os.makedirs(OUT, exist_ok=True)
SRC = {'reign': ('reign-is-mine', 'story3.mp3'), 'club': ('ebony-the-club', 'club.mp3')}

def sentences(book):
    d = SRC[book][0]
    for line in open(f'{REPO}/{d}/index.html', encoding='utf-8'):
        if line.startswith('const PARAS'):
            P = json.loads(line[len('const PARAS = '):].rstrip().rstrip(';'))
            return [s for p in P for s in p['sents']]

def find(book, t):
    for s in sentences(book):
        if abs(s['t'] - t) < .02:
            return s
    raise KeyError(t)

def load_clip(book, s):
    d, f = SRC[book]
    a, b = s['t'] - .03, s['e'] + .08
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-i', f'{REPO}/{d}/{f}',
                          '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(out, np.int16).astype(np.float32) / 32768
    n = int(.012 * SR); x[:n] *= np.linspace(0, 1, n); x[-n*3:] *= np.linspace(1, 0, n*3)
    return x

def word_times(x, text):
    """Spread words over voiced time only, so pauses in the reading are not counted."""
    hop = int(.02 * SR)
    rms = np.array([np.sqrt((x[i:i+hop]**2).mean() + 1e-12) for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(rms)
    voiced = db > -42
    # fill tiny gaps (<120ms) so only real pauses are skipped
    v = voiced.copy(); run = 0
    for i in range(len(v)):
        if not voiced[i]: run += 1
        else:
            if 0 < run <= 6: v[i-run:i] = True
            run = 0
    idx = np.nonzero(v)[0]
    if len(idx) == 0: idx = np.arange(len(db))
    vt = idx * hop / SR                      # voiced frame times
    words = text.replace('’', "'").split()
    w = np.array([len(wd.strip('.,!?"')) + 1.5 for wd in words], float)
    cum = np.concatenate([[0], np.cumsum(w)]) / w.sum()
    starts = [float(vt[min(int(c * (len(vt) - 1)), len(vt) - 1)]) for c in cum[:-1]]
    return [{'w': wd, 't': round(t, 3)} for wd, t in zip(words, starts)]

# ---------- script ----------
# Each scene: (id, [narration (book, sentence start, speaker label)], extra hold)
SCRIPT = [
    ('open',  [], 3.0),
    ('coat',  [('reign', 563.077, 'Ebony')], .35),
    ('wine',  [('reign', 681.972, 'Ebony')], .3),
    ('dare',  [('reign', 812.684, 'Ebony'), ('reign', 814.263, 'Ebony')], .35),
    ('reign', [], 2.5),
    ('calls', [('club', 179.103, ''), ('club', 190.05, '')], .3),
    ('woman', [('club', 221.615, 'Raven')], .3),
    ('slam',  [('club', 718.757, '')], .55),
    ('want',  [('club', 737.086, 'Ebony')], .45),
    ('end',   [], 5.2),
]
LEAD = .28   # silence at the start of a narrated scene
GAP = .18    # between two lines in one scene

scenes, vos, cursor = [], [], 0.0
clips = []
for sid, lines, hold in SCRIPT:
    start = cursor
    if not lines:
        cursor += hold
    else:
        t = cursor + LEAD
        for i, (book, st, who) in enumerate(lines):
            s = find(book, st); x = load_clip(book, s)
            words = word_times(x, s['text'].strip())
            vos.append({'scene': sid, 'at': round(t, 3), 'dur': round(len(x) / SR, 3), 'who': who, 'book': book,
                        'text': s['text'].strip(), 'words': [{'w': w['w'], 't': round(t + w['t'], 3)} for w in words]})
            clips.append((t, x))
            t += len(x) / SR + (GAP if i < len(lines) - 1 else 0)
        cursor = t + hold
    scenes.append({'id': sid, 'a': round(start, 3), 'b': round(cursor, 3)})
T = round(cursor, 3)

S = {s['id']: s for s in scenes}
def word_at(sid, needle, k=0):
    hits = [w['t'] for v in vos if v['scene'] == sid for w in v['words'] if needle.lower() in w['w'].lower()]
    return hits[k]

# hits: (time, kind) kind: big | mid | tick | slam | glitch
hits = [(0.35, 'mid'), (1.55, 'mid')]
for s in scenes[1:]:
    hits.append((s['a'], 'tick'))
hits += [(word_at('dare', 'dare'), 'mid'), (word_at('dare', 'Scarlett'), 'glitch'),
         (S['reign']['a'], 'big'), (word_at('slam', 'slammed'), 'slam'), (word_at('want', 'him!'), 'mid'),
         (S['end']['a'], 'big'), (S['end']['a'] + 1.55, 'mid')]
hits = sorted({(round(t, 3), k) for t, k in hits if not (k == 'tick' and any(abs(t - u) < .05 and kk != 'tick' for u, kk in hits))})
risers = [S['reign']['a'], S['end']['a']]

json.dump({'T': T, 'fps': 30, 'scenes': scenes, 'vo': vos, 'hits': [{'t': t, 'k': k} for t, k in hits], 'risers': risers},
          open(f'{OUT}/timeline.json', 'w'), indent=1)

# ---------- sound design ----------
N = int((T + .1) * SR)
tt = np.arange(N) / SR
rng = np.random.default_rng(11)

def fft_filter(x, lo=0, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * m, len(x))

def env(n, dec):
    return np.exp(-np.arange(n) / SR / dec)

def kick(dur=.45, f0=95, f1=42, dec=.22, amp=1.):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / .045)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, dec)

def add(buf, x, t, g=1.):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i+len(x)] += g * x

bed = np.zeros(N); fx = np.zeros(N); vo = np.zeros(N)

# drone: low A with a fifth, slow swell; brighter in the Club half
drone = .09 * np.sin(2*np.pi*55*tt) + .05 * np.sin(2*np.pi*82.4*tt + 1) + .03 * np.sin(2*np.pi*110.2*tt)
drone *= .6 + .4 * np.sin(2*np.pi*tt/7.3) ** 2
noise = fft_filter(rng.standard_normal(N), 200, 1400) * .012
bed += drone + noise

# heartbeat pulse, 84 bpm (lub-dub), starts after the first title hit, stops for the end card tail
beat = 60 / 84
t = 0.35
while t < S['end']['a'] + 3.6:
    bed_g = .55 if t < S['reign']['a'] else .7
    add(bed, kick(amp=bed_g), t); add(bed, kick(amp=bed_g*.55, f0=80), t + .2)
    t += beat

# hits
def boom(heavy=False):
    n = int(2.2 * SR); t = np.arange(n) / SR
    k = kick(2.2, 70, 31, .9 if heavy else .55, 1.2)
    nz = fft_filter(rng.standard_normal(n), 0, 2500) * env(n, .12) * .5
    saw = sum(((t * f) % 1 * 2 - 1) for f in (55, 82.4, 110)) / 3
    braam = fft_filter(saw * env(n, .7 if heavy else .4), 0, 600) * (.9 if heavy else .5)
    return k + nz + braam

def tick():
    n = int(.25 * SR)
    return fft_filter(rng.standard_normal(n), 2000, 9000) * env(n, .03) * .35 + kick(.25, 120, 60, .06, .4)

def glitch():
    n = int(.6 * SR); x = np.zeros(n)
    for j in range(6):
        seg = fft_filter(rng.standard_normal(int(.04 * SR)), 300, 5000) * .6
        x[int(j * .07 * SR):int(j * .07 * SR) + len(seg)] += seg
    return x + kick(.6, 90, 40, .25, .9)

for h in hits:
    t, k = h
    if k == 'tick': add(fx, tick(), t)
    elif k == 'mid': add(fx, boom(False), t, .8 if not any(v['at'] < t < v['at'] + v['dur'] for v in vos) else .5)
    elif k == 'big': add(fx, boom(True), t, 1.)
    elif k == 'slam': add(fx, boom(False), t, .8); add(fx, tick(), t, 1.6)
    elif k == 'glitch': add(fx, glitch(), t, .6)

# risers into the two title slams
for r in risers:
    d = 1.4; n = int(d * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    X = np.fft.rfft(nz)  # crude rising brightness: crossfade three bands
    lo_, mid_, hi_ = (fft_filter(nz, 100, 800), fft_filter(nz, 800, 3000), fft_filter(nz, 3000, 10000))
    p = t / d
    sweep = lo_ * (1 - p) + mid_ * np.sin(np.pi * p) + hi_ * p
    tone = np.sin(2 * np.pi * np.cumsum(110 + 330 * p ** 2) / SR) * .15
    add(fx, (sweep * .35 + tone) * p ** 1.6, r - d)

# simple reverb on fx
ir_n = int(1.8 * SR); ir = rng.standard_normal(ir_n) * env(ir_n, .45); ir[0] = 0
ir = fft_filter(ir, 150, 4000); ir /= np.abs(ir).sum() / 6
L = 1 << int(np.ceil(np.log2(N + ir_n)))
wet = np.fft.irfft(np.fft.rfft(fx, L) * np.fft.rfft(ir, L), L)[:N]
fx = fx + .3 * wet

# narration, level matched
for t0, x in clips:
    r = np.sqrt((x ** 2).mean()); add(vo, x * (.12 / r), t0)

# duck the bed under the voice
duck = np.ones(N)
for v in vos:
    a, b = int((v['at'] - .1) * SR), int((v['at'] + v['dur'] + .15) * SR)
    duck[a:b] = .38
k = int(.08 * SR); duck = np.convolve(duck, np.ones(k) / k, 'same')
mix = bed * duck * .8 + fx * (.3 + .7 * duck) * .9 + vo * 1.25
fade = int(.6 * SR); mix[-fade:] *= np.linspace(1, 0, fade) ** 2
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.abs(mix).max() / .95
with wave.open(f'{OUT}/mix_raw.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('T =', T)
for s in scenes: print(s)
for h in hits: print(h)
