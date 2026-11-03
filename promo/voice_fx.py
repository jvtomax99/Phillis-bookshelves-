# Voice treatments for the promo narration. Used by build_audio.py.
import subprocess
import numpy as np

SR = 48000
_V = 'highpass=f=70,lowshelf=f=200:g=3,equalizer=f=3200:t=q:w=1.2:g=-2.5,highshelf=f=9000:g=2.5,deesser=i=0.4,' \
     'acompressor=threshold=-26dB:ratio=4:attack=8:release=120:makeup=4'
# breath/air layer: the voice's own top end, squashed hard and tucked under
_AIR = 'asplit[d][w];[w]highpass=f=4500,acompressor=threshold=-45dB:ratio=12:attack=1:release=80:makeup=14,volume={air}[a];' \
       '[d][a]amix=inputs=2:normalize=0'
VOICES = {
    'A': {'fx': None, 'pause': 1.0},
    'B': {'fx': 'rubberband=pitch=0.92:tempo=0.93:formant=preserved:pitchq=quality,' + _V + ',aecho=0.8:0.5:38|61:0.18|0.10',
          'pause': 1.0},
    # B2: Velvet, breathier. A little lower and slower than B, warmer, with air and longer pauses
    'B2': {'fx': 'rubberband=pitch=0.90:tempo=0.91:formant=preserved:pitchq=quality,' + _AIR.format(air=0.38) + ',' +
                 'highpass=f=65,lowshelf=f=180:g=4,equalizer=f=3000:t=q:w=1.1:g=-2.5,highshelf=f=8500:g=3.5,deesser=i=0.55,'
                 'acompressor=threshold=-30dB:ratio=5:attack=6:release=140:makeup=6,volume=2dB,asoftclip=type=tanh,'
                 'lowpass=f=14500,aecho=0.8:0.55:42|71|113:0.20|0.12|0.07',
           'pause': 1.5},
    # B3: Velvet, after dark. Same voice as B2 with more air, darker top and pauses held twice as long
    'B3': {'fx': 'rubberband=pitch=0.89:tempo=0.90:formant=preserved:pitchq=quality,' + _AIR.format(air=0.55) + ',' +
                 'highpass=f=60,lowshelf=f=170:g=5,equalizer=f=2900:t=q:w=1.0:g=-3,highshelf=f=8500:g=3.5,deesser=i=0.6,'
                 'acompressor=threshold=-32dB:ratio=6:attack=5:release=160:makeup=7,volume=3dB,asoftclip=type=tanh,'
                 'lowpass=f=14000,aecho=0.8:0.6:47|79|127:0.24|0.15|0.09',
           'pause': 2.0},
    'C': {'fx': 'rubberband=pitch=0.86:tempo=0.86:formant=preserved:pitchq=quality,highpass=f=60,lowshelf=f=160:g=5,'
                'equalizer=f=2800:t=q:w=1.0:g=-4,highshelf=f=10000:g=3.5,deesser=i=0.5,'
                'acompressor=threshold=-30dB:ratio=6:attack=5:release=150:makeup=6,aecho=0.8:0.55:45|83:0.22|0.12',
          'pause': 1.0},
}

def stretch_pauses(x, factor):
    """Hold the gaps inside a line longer (not the edges), padding with the gap's own room tone."""
    if factor <= 1: return x
    hop = int(.02 * SR)
    db = np.array([20 * np.log10(np.sqrt((x[i:i+hop]**2).mean()) + 1e-9) for i in range(0, len(x) - hop, hop)])
    quiet = db < -38
    out, last, i = [], 0, 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            inner = i > 3 and j < len(quiet) - 3
            if inner and (j - i) >= 5:                       # a real pause of 100 ms or more
                a, b = i * hop, j * hop
                out.append(x[last:b])
                gap = x[a:b]
                extra = int(len(gap) * (factor - 1))
                tone = np.resize(gap[len(gap)//4: 3*len(gap)//4] if len(gap) > 8 else gap, extra) * .7
                out.append(tone); last = b
            i = j
        else:
            i += 1
    out.append(x[last:])
    return np.concatenate(out).astype(np.float32)

def treat(x, name):
    v = VOICES[name]
    x = stretch_pauses(x, v['pause'])
    if not v['fx']: return x
    tail = np.zeros(int(.35 * SR), np.float32)                # room for the reverb tail
    raw = (np.clip(np.concatenate([x, tail]), -1, 1) * 32767).astype(np.int16).tobytes()
    out = subprocess.run(['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                          '-af', v['fx'], '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         input=raw, capture_output=True, check=True).stdout
    y = np.frombuffer(out, np.int16).astype(np.float32) / 32768
    # trim trailing near-silence beyond the tail we added
    hop = int(.01 * SR); k = len(y)
    while k > hop and np.sqrt((y[k-hop:k]**2).mean()) < 10 ** (-50 / 20): k -= hop
    return y[:k]
