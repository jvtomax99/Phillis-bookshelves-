# Start screen music

`compose.py` writes three original sketches as MIDI (late-night lounge, candlelight piano, slow R&B); the site uses **lounge** (D minor, 66 BPM, 16 bars = 58.18 s).

```
python3 compose.py
fluidsynth -ni -q -g 0.7 -r 44100 -o synth.reverb.room-size=0.75 -o synth.reverb.damp=0.35 -o synth.reverb.width=0.9 -o synth.reverb.level=0.55 -o synth.chorus.active=0 -F raw-lounge.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 lounge.mid
```

The MIDI plays the form twice; cut the second pass (58.1818 s to 116.3636 s) so the loop carries its own reverb tail and loops without a seam, then warm it and set a quiet level:

```
ffmpeg -i raw-lounge.wav -ss 58.1818 -t 58.1818 -af "equalizer=f=4500:t=q:w=1:g=-2.5,equalizer=f=180:t=q:w=1:g=1.5,loudnorm=I=-20:TP=-2:LRA=11" loop.wav
ffmpeg -i loop.wav -c:a aac -b:a 96k -movflags +faststart music.m4a
ffmpeg -i loop.wav -c:a libopus -b:a 80k music.webm
```

FluidSynth and the FluidR3 GM soundfont (MIT): `apt-get install fluidsynth fluid-soundfont-gm`. If the loop length changes, change `LOOP` in `index.html` on main.
