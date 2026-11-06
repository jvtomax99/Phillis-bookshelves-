"""Three original sketches for Phillis Brown's start screen, written as MIDI and rendered with FluidSynth (FluidR3 GM).
python3 compose.py  ->  lounge.mid, piano.mid, rnb.mid (render with render.sh)"""
import pretty_midi as pm, random, os
random.seed(11)
HERE = os.path.dirname(os.path.abspath(__file__))

# D minor, 4-bar phrases. (bass root, upper voicing)
A_SECTION = [(38, [53, 57, 60, 64]),   # Dm9
             (43, [58, 62, 65, 69]),   # Gm9
             (46, [50, 53, 57, 60]),   # Bbmaj9
             (45, [55, 61, 65, 70])]   # A7b9
B_SECTION = [(38, [53, 57, 60, 64]),   # Dm9
             (43, [58, 62, 65, 69]),   # Gm9
             (39, [55, 58, 62, 69]),   # Ebmaj7#11
             (45, [55, 62, 64, 67])]   # A7sus4 (resolves to the loop start)
FORM = A_SECTION + B_SECTION + A_SECTION + B_SECTION   # 16 bars, loops back to Dm9

def hum(t, amt=0.012): return t + random.uniform(-amt, amt)
def vel(v, spread=8): return max(1, min(127, int(v + random.uniform(-spread, spread))))

def note(inst, p, t0, t1, v):
    inst.notes.append(pm.Note(velocity=vel(v), pitch=p, start=max(0, hum(t0)), end=hum(t1)))

def song(bpm):
    m = pm.PrettyMIDI(initial_tempo=bpm); return m, 60.0 / bpm

def lounge():
    """Late-night lounge: Rhodes comping, walking upright bass, brushes and a soft ride, a lazy vibraphone line."""
    m, b = song(66)
    keys = pm.Instrument(4, name="Rhodes"); bass = pm.Instrument(32, name="Upright"); vib = pm.Instrument(11, name="Vibes")
    dr = pm.Instrument(40, is_drum=True, name="Brushes")
    sw = 0.62  # swing: the off-beat 8th lands at 62% of the beat
    for bar, (root, ch) in enumerate(FORM):
        t = bar * 4 * b
        for p in ch: note(keys, p, t, t + 1.4 * b, 52)                      # long chord on 1
        for p in ch[1:]: note(keys, p + 0, t + (1 + sw) * b, t + 2.6 * b, 40)  # push on the and of 2
        nxt = FORM[(bar + 1) % len(FORM)][0]
        walk = [root, root + 7, root + 12 if bar % 2 else root + 10, nxt + (1 if nxt < root else -1)]
        for i, p in enumerate(walk): note(bass, p, t + i * b, t + (i + 0.92) * b, 70 if i == 0 else 60)
        for i in range(4):                                                    # brushes: soft swish 8ths, ride on 2 and 4
            note(dr, 38, t + i * b, t + i * b + 0.2, 22); note(dr, 38, t + (i + sw) * b, t + (i + sw) * b + 0.2, 16)
            if i in (1, 3): note(dr, 51, t + i * b, t + i * b + 0.3, 34); note(dr, 42, t + i * b, t + i * b + 0.1, 26)
        note(dr, 36, t, t + 0.2, 28)
    # vibraphone: two answering phrases per 8 bars, D dorian
    phr = [(0, 69, 1.5), (1.5, 72, .5), (2.0, 74, 1), (3.0, 72, .7), (3.7, 69, 2.3), (8, 65, 1), (9, 67, .5), (9.6, 69, 1.4), (11, 64, 1), (12, 62, 3)]
    for rep in (0, 32):
        for s, p, d in phr:
            if rep and s >= 8: p += 2
            note(vib, p, (rep + 4 + s) * b, (rep + 4 + s + d) * b, 58)
    m.instruments += [keys, bass, vib, dr]; return m

def piano():
    """Candlelight piano: rolled chords and a slow melody on grand piano, a warm string bed underneath."""
    m, b = song(60)
    pno = pm.Instrument(0, name="Grand"); strings = pm.Instrument(49, name="Strings")
    mel = [76, 74, 72, 69, 72, 74, 77, 76, 74, 72, 70, 69, 74, 72, 69, 67]
    for bar, (root, ch) in enumerate(FORM):
        t = bar * 4 * b
        note(pno, root - 12 if root > 40 else root, t, t + 3.8 * b, 50)
        arp = [root, ch[0], ch[1], ch[2], ch[3], ch[2], ch[1], ch[0]]
        for i, p in enumerate(arp): note(pno, p + (12 if i else 0), t + i * 0.5 * b, t + 3.9 * b, 34 + (6 if i == 4 else 0))
        top = mel[bar % len(mel)]
        note(pno, top, t + 0.02, t + 2.5 * b, 60); note(pno, top - (2 if bar % 2 else 3), t + 2.5 * b, t + 3.9 * b, 50)
        for p in ch: note(strings, p, t, t + 4 * b, 30)
    m.instruments += [pno, strings]; return m

def rnb():
    """Velvet groove: slow R&B. Rhodes, round bass, side-stick, soft swung hats, a warm pad."""
    m, b = song(72)
    keys = pm.Instrument(4, name="Rhodes"); bass = pm.Instrument(33, name="Bass"); pad = pm.Instrument(89, name="Warm pad")
    dr = pm.Instrument(0, is_drum=True, name="Kit")
    for bar, (root, ch) in enumerate(FORM):
        t = bar * 4 * b
        for p in ch: note(keys, p, t + 0.03, t + 1.8 * b, 50)
        for p in ch[1:]: note(keys, p, t + 2.5 * b, t + 3.7 * b, 42)
        for p in ch: note(pad, p - 12, t, t + 4 * b, 26)
        note(bass, root, t, t + 1.4 * b, 80); note(bass, root, t + 1.75 * b, t + 2.2 * b, 58)
        note(bass, root + 7, t + 2.5 * b, t + 3.2 * b, 66); note(bass, root + 10, t + 3.5 * b, t + 3.95 * b, 56)
        note(dr, 36, t, t + .2, 74); note(dr, 36, t + 2.5 * b, t + 2.7 * b, 60); note(dr, 36, t + 2.75 * b, t + 2.9 * b, 44)
        note(dr, 37, t + b, t + b + .1, 62); note(dr, 37, t + 3 * b, t + 3 * b + .1, 66)
        for i in range(8):
            off = (i * 0.5 + (0.08 if i % 2 else 0)) * b
            note(dr, 42, t + off, t + off + .05, 34 if i % 2 else 44)
        if bar % 4 == 3: note(dr, 46, t + 3.5 * b, t + 3.9 * b, 36)
    m.instruments += [keys, bass, pad, dr]; return m

for name, fn in (("lounge", lounge), ("piano", piano), ("rnb", rnb)):
    m = fn()
    # play the form twice: the second pass carries the first one's reverb tail, so it can be cut out as a seamless loop
    loop_len = m.get_end_time()
    one = m.instruments
    for inst in one:
        extra = [pm.Note(n.velocity, n.pitch, n.start + 0, n.end) for n in []]
    bar_len = 4 * 60.0 / m.get_tempo_changes()[1][0]
    L = 16 * bar_len
    for inst in m.instruments:
        inst.notes += [pm.Note(n.velocity, n.pitch, n.start + L, n.end + L) for n in list(inst.notes)]
    m.write(os.path.join(HERE, name + ".mid"))
    print(name, "loop seconds", round(L, 2))
