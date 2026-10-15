"""P05 RELIC — sound cue sheet (10 s). Run: python3 audio.py out.wav
Phase map: S1 0-2.2 cold open (cavern air, drip, drone enters) | S2 2.2-5.2 reveal (drone swells, shepard, wind)
| S3 5.2-7.6 wake (riser, pulse, ember crackle) | S4 7.6-8.1 BLACK SILENCE (R-3-06) | S5 8.1-10 title: hit + sub + one braam + tail."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
seed(1105)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
m = Mix(10.0)
# beds
m.put(wind(10, 0.35, 0.4), at=0, db=-30, fade_in=1.0, name='cavern air')
m.put(drone(8.0, f0=36.7, detune=0.5, lp=320, voices=6), at=0.0, db=-20, fade_in=1.6, fade_out=0.3, name='drone D1')
m.put(drone(5.6, f0=55.0, detune=0.6, lp=600, voices=4), at=2.2, db=-24, fade_in=1.2, fade_out=0.2, name='drone swell A1')
m.put(shepard(5.4, base=55, octaves=5, rate=0.1), at=2.2, db=-30, fade_in=1.5, fade_out=0.2, name='shepard dread')
# S1 details: a single drip (high pluck w/ reverb) and dust
drip = reverb(pluck(note('E', 6), 0.6, 0.3), size=0.9, decay=2.4, mix=0.6)
m.put(drip, at=0.9, db=-26, name='drip')
m.put(drip, at=4.1, db=-30, pan=0.4, name='drip 2')
# S2 reveal: low choir pad under the crane
m.put(choir(3.4, freqs=(73.4, 110, 146.8), breath=0.25), at=2.3, db=-26, fade_in=1.2, fade_out=0.4, name='choir pad')
m.put(whoosh(0.9, 200, 2500, 1), at=2.2, db=-24, name='cut whoosh (crane)')
# S3 wake: riser to the cut, crackle, heartbeat pulse, the relic's hum
m.put(riser(2.4, 120, 2600, noise_mix=0.55, curve=2.2), at=5.2, db=-14, name='riser -> black')
m.put(crackle(2.4, 40, 0.6), at=5.2, db=-22, fade_in=0.8, name='ember crackle')
m.put(heartbeat(2.4, bpm=78, level=0.8), at=5.2, db=-18, fade_in=0.5, name='pulse')
m.put(hum(2.4, f=48, level=0.5), at=5.2, db=-20, fade_in=1.0, name='relic hum')
# S4: silence. Everything is pulled to -60 dB from 7.58 to 8.1 (12+ frames of near-silence before the hit)
m.duck(7.58, 8.1, -60, 0.04)
# S5: the title hit lands on frame 1 of S5 (8.1 s): hit + sub drop + one braam, tail rings out
m.put(hit(1.9, sub=42, crunch=0.7), at=8.1, db=-3, name='TITLE HIT')
m.put(sub_drop(1.9, 65, 28), at=8.1, db=-7, name='sub drop')
m.put(braam(1.9, f0=36.7), at=8.12, db=-12, name='braam (1 of 1)')
m.put(choir(1.9, freqs=(73.4, 92.5, 110), breath=0.2), at=8.3, db=-24, fade_in=0.4, fade_out=0.6, name='tail pad')
m.put(crackle(1.9, 25, 0.4), at=8.1, db=-26, fade_out=0.6, name='ember tail')
m.write(out)
print('wrote', out); [print(f'  {a:5.2f}s  {n:22s} {d:4.1f}s') for a, n, d in sorted(m.cues)]
