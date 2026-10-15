"""P03 THE LANTERN ROAD — sound cue sheet (12 s). Run: python3 audio.py out.wav
All times come from timing.json (shared with scene.js); footsteps use the same gait formula as the picture:
plants at phase0 + k*T, drawn on 2s -> the landing is heard on the first even frame at/after the plant.
Phase map: S1 0-4.625 dusk road (wind, D2 drone, steps, bell, 3 lantern chimes) | S2 4.625-8.833 the village wakes
(choir swell, ascending pentatonic chain of 9 chimes, distant steps) | S3 8.833-12 the gate (bell, two last steps,
SILENCE 9.60-10.20, gentle low hit + chime as the great lantern catches, flame bed, motif resolves, tail)."""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness', 'audio'))
from sfx import *
seed(303)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
TM = json.load(open(os.path.join(HERE, 'timing.json')))
FPS = TM['fps']; DUR = sum(s['dur'] for s in TM['shots'])
cut1 = math.ceil(TM['shots'][0]['dur'] * FPS) / FPS                              # first frame of S2 (4.625)
cut2 = math.ceil((TM['shots'][0]['dur'] + TM['shots'][1]['dur']) * FPS) / FPS   # first frame of S3 (8.833)
on1 = lambda t: math.ceil(t * FPS - 1e-9) / FPS                                  # first frame at/after t (lights: on 1s)
on2 = lambda t: 2 * math.ceil(t * FPS / 2 - 1e-9) / FPS                           # first even frame at/after t (character on 2s)
m = Mix(DUR)

# ---------------------------------------------------------------- beds (slow movement, no loops)
m.put(wind(DUR, strength=0.35, gust=0.5), at=0, db=-24, fade_in=1.2, name='mountain wind (gusty)')
m.put(highpass(wind(DUR, strength=0.6, gust=0.8), 900), at=0, db=-36, pan=0.3, fade_in=2.0, name='wind whistle (high gusts)')
m.put(drone(DUR, f0=73.4, detune=0.3, lp=700, voices=4, shape='sine'), at=0, db=-21, fade_in=1.8, fade_out=0.6, name='warm drone D2 (sine, lp 700)')
m.put(drone(DUR - cut1, f0=110.0, detune=0.25, lp=900, voices=3, shape='sine'), at=cut1, db=-30, fade_in=2.0, fade_out=1.0, name='drone fifth A2 joins (S2+)')

# ---------------------------------------------------------------- footsteps on gravel (+ staff tap with the far foot)
def step(level=1.0):
    crunch = bandpass(crackle(0.16, 1400, 0.7), 900, 7000) * np.exp(-t_axis(0.16) * 18)
    thump = np.sin(2 * np.pi * 85 * t_axis(0.16)) * np.exp(-t_axis(0.16) * 40) * 0.6
    return ((crunch + thump) * level).astype(np.float32)
def tap():
    tt = t_axis(0.09); return (highpass(noise(0.09), 1200) * np.exp(-tt * 70) * 0.5 + np.sin(2 * np.pi * 620 * tt) * np.exp(-tt * 55) * 0.4).astype(np.float32)
W = TM['walk']; T = W['T']; ph = W['phase0']
for k in range(0, 16):
    tc = ph + k * T; ta = on2(tc)
    if ta >= cut2: break
    s1 = ta < cut1; pan = -0.32 if s1 else -0.42
    m.put(step(), at=ta, db=-27 if s1 else -31, pan=pan, name=f'step {"S1" if s1 else "S2 (distant)"}')
    if k % 2 == 1: m.put(tap(), at=ta + 0.02, db=-33 if s1 else -37, pan=pan, name='staff tap')
S3 = TM['s3']
m.put(step(1.1), at=on2(S3['plantBrake']), db=-23, pan=-0.1, name='step S3 (braking)')
m.put(step(1.25), at=on2(S3['plantStop']), db=-22, pan=-0.1, name='step S3 (STOP, closing foot)')
m.put(tap(), at=on2(S3['plantStop']) + 0.02, db=-27, pan=-0.05, name='staff plants')

# ---------------------------------------------------------------- distant bell (low pluck, long reverb)
def bell(f):
    b = pluck(f, 3.5, bright=0.35) + 0.35 * pluck(f * 2.01, 3.5, bright=0.2)
    return lowpass(reverb(b, size=0.95, decay=4.0, mix=0.55)[:int(3.5 * SR)], 2600).astype(np.float32)
m.put(bell(note('D', 3)), at=TM['bells'][0], db=-21, pan=0.35, name='distant bell 1')
m.put(bell(note('D', 3)), at=TM['bells'][1], db=-19, pan=0.25, name='village bell 2')

# ---------------------------------------------------------------- lantern chimes (soft sine, pentatonic)
def chime(f, dur=0.9):
    c = tone(f, dur, 'sine', a=0.004, d=0.12, s=0.25, r=0.55) + 0.25 * tone(f * 2.0, dur, 'sine', a=0.003, d=0.08, s=0.1, r=0.4) + 0.08 * tone(f * 3.01, dur, 'sine', a=0.002, d=0.05, s=0.0, r=0.2)
    return reverb(c * 0.6, size=0.6, decay=1.6, mix=0.32)[:int((dur + 0.6) * SR)].astype(np.float32)
for t0, n_, o in zip(TM['s1']['ropeLanterns'], ['A', 'C', 'D'], [5, 6, 6]):
    m.put(chime(note(n_, o)), at=on1(t0), db=-24, pan=-0.25, name=f'chime rope lantern {n_}{o}')
chain_notes = [('D', 5), ('F', 5), ('G', 5), ('A', 5), ('C', 6), ('D', 6), ('F', 6), ('G', 6), ('A', 6)]
chain_x = [366, 560, 760, 1010, 640, 470, 905, 640, 790]                         # screen x of each chain lantern (pan)
for t0, (n_, o), x in zip(TM['s2']['chain'], chain_notes, chain_x):
    m.put(chime(note(n_, o), 0.8), at=on1(t0), db=-25 - (2 if o >= 6 else 0), pan=(x - 640) / 640 * 0.7, name=f'chain chime {n_}{o}')

# ---------------------------------------------------------------- choir swell across the S2 reveal
m.put(choir(cut2 - cut1 + 0.6, freqs=(146.8, 220.0, 293.7), breath=0.2), at=cut1 + 0.1, db=-27, fade_in=1.6, fade_out=1.2, name='choir swell (D3 A3 D4)')

# ---------------------------------------------------------------- plucked pentatonic motif (sparse, on cuts)
mot = [(0.50, 'D', 4), (3.20, 'F', 4), (cut1, 'A', 4), (cut2, 'G', 4)]
for t0, n_, o in mot: m.put(reverb(pluck(note(n_, o), 2.4, bright=0.45), size=0.7, decay=2.2, mix=0.3)[:int(2.6 * SR)], at=t0, db=-21, pan=0.1, name=f'motif {n_}{o}')

# ---------------------------------------------------------------- SILENCE before the great lantern (R-3-06): >= 12 f, >= 20 dB under the hit
sil = TM['silence']; m.duck(sil[0], sil[1], -42, 0.1)
# ---------------------------------------------------------------- the great lantern catches (frame 245) — hit, chime, flame, resolution
tg = on1(S3['ignite'])
m.put(hit(2.2, sub=46, click=False, tail=True, crunch=0.12), at=tg, db=-16, name='GENTLE LOW HIT (great lantern)')
m.put(chime(note('D', 5), 1.6) + chime(note('A', 5), 1.6) * 0.6, at=tg, db=-21, pan=0.45, name='chime D5+A5 (great lantern)')
m.put(fire(DUR - tg, level=0.3), at=tg + 0.05, db=-33, pan=0.45, fade_in=0.4, name='lantern flame bed')
m.put(pad(DUR - tg, freqs=(146.8, 185.0, 220.0), lp=1400), at=tg, db=-30, fade_in=0.8, fade_out=0.8, name='warm pad (D major colour) under the title')
for t0, n_, o in [(TM['s3']['title'], 'C', 5), (11.25, 'D', 4)]: m.put(reverb(pluck(note(n_, o), 2.0, bright=0.4), size=0.7, decay=2.2, mix=0.32)[:int(2.2 * SR)], at=t0, db=-22, pan=0.1, name=f'motif {n_}{o} (resolve)')
m.write(out)
print('wrote', out); [print(f'  {a:6.3f}s  {n:44s} {d:4.2f}s') for a, n, d in sorted(m.cues)]
