"""P06 CEL — sound cue sheet (10 s). Run: python3 audio.py out.wav
Picture map (frames @ 24 fps, mirrored from scene.js):
  S1 f0-71   (0.000-3.000 s) exterior storm, locked low; lightning flashes f21-22 / f55-56 -> thunder at 0.9 s / 2.3 s exactly;
             wave crashes (spray) f30, f58
  S2 f72-139 (3.000-5.833 s) inside the tower: look up, crouch f78, launch f84, iron-stair contacts f92 f100 f108 f116 f124 f132
  S3 f140-191 (5.833-8.000 s) lantern room: wind-up f144, push f150, CLUNK f154, near-silence f156-167 (-30 dB, 12 f),
             IGNITION f168, lamp hum + riser into the S4 cut
  S4 f192-239 (8.000-10.000 s) from the sea: the beam passes over the lens f206 (whoosh peak), choir peaks, storm continues
Rules kept: hits on picture frames, riser ends on the cut it motivates, >=12 f of real silence before the biggest hit (ignition),
beds move slowly (gusts, swells), nothing is a repeated loop, tails bridge the cuts (L-cuts on the storm beds)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
import numpy as np

seed(606)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
FPS = 24.0
F = lambda f: f / FPS
DUR = 10.0
T2, T3, T4 = F(72), F(140), F(192)                 # cut times: 3.000, 5.833, 8.000
m = Mix(DUR)

def trim_head(x, sec):                             # the kit beds fade in over ~1 s: start them already "in" the storm
    return x[int(sec * SR):]

def env(n, pts):                                   # piecewise-linear gain envelope over n samples; pts = [(sec, gain), ...]
    t = np.arange(n) / SR; xs, ys = zip(*pts); return np.interp(t, xs, ys).astype(np.float32)

def surf(dur, swell=2.6):                          # low surge of the sea: brown noise, slow swells
    x = lowpass(noise(dur, 'brown'), 420) * 2.2
    t = t_axis(dur); g = 0.55 + 0.45 * np.sin(2 * np.pi * t / swell + 0.7) ** 2
    return (x * g).astype(np.float32)

def crash(dur=1.6):                                # a wave breaking on rock: noise burst + low body
    t = t_axis(dur); a = np.minimum(1, t / 0.03) * np.exp(-t * 2.4)
    x = lowpass(noise(dur), 2600) * a * 0.9 + lowpass(noise(dur, 'brown'), 300) * a * 2.0
    return (x + hit(dur, sub=52, click=False, tail=False, crunch=0.2) * 0.5).astype(np.float32)

def breath(dur, kind='in'):                        # noise swells (no voice)
    t = t_axis(dur); u = t / dur
    e = np.sin(np.pi * u) ** (1.5 if kind == 'in' else 0.8) * (1 - 0.5 * u if kind == 'out' else 0.6 + 0.4 * u)
    return (bandpass(noise(dur), 700 if kind == 'in' else 450, 3600) * e).astype(np.float32)

def clunk(dur=0.11):                               # iron ratchet locking: click + short low thunk, gone within ~3 frames
    t = t_axis(dur); body = np.sin(2 * np.pi * 118 * t) * np.exp(-t * 42) + 0.5 * np.sin(2 * np.pi * 236 * t + 0.4) * np.exp(-t * 60)
    clk = highpass(noise(dur), 1800) * np.exp(-t * 160) * 0.8 + bandpass(noise(dur), 900, 2600) * np.exp(-t * 55) * 0.5
    return fade(saturate((body + clk).astype(np.float32), 1.6), 0.0, 0.03)

def step(f0):                                      # iron stair: very short square ping, low-passed, plus a dull thud
    ping = lowpass(tone(f0, 0.07, 'square', a=0.001, d=0.02, s=0.15, r=0.03), 2200) * 0.55
    t = t_axis(0.12); thud = (np.sin(2 * np.pi * 95 * t) * np.exp(-t * 38) + lowpass(noise(0.12), 700) * np.exp(-t * 60) * 0.6)
    x = np.zeros(int(0.12 * SR), np.float32); x[:len(ping)] += ping; x += thud.astype(np.float32) * 0.7
    return x

# ------------------------------------------------------------------ S1 exterior storm (0 - 3.0 s, L-cut tails into S2)
m.put(trim_head(wind(4.6, 0.8, 0.6), 1.0), at=0.0, db=-15, fade_out=0.35, name='storm wind 0.8 gusty (ext)')
m.put(trim_head(rain(3.9, 0.8), 0.5), at=0.0, db=-14, fade_out=0.3, name='rain 0.8 (ext)')
m.put(surf(3.4), at=0.0, db=-17, fade_out=0.3, name='sea surge')
for at, name in [(0.9, 'THUNDER 1 (flash f21)'), (2.3, 'THUNDER 2 (flash f55)')]:
    m.put(hit(1.9, sub=45, crunch=0.8), at=at, db=-7, name=name)
    m.put(drone(2.2, f0=31, detune=0.8, lp=170, voices=4), at=at + 0.04, db=-12, fade_in=0.05, fade_out=0.9, name='  rumble')
m.put(crash(1.7), at=F(30), db=-11, pan=0.35, name='wave crash (spray f30)')
m.put(crash(1.3), at=F(58), db=-15, pan=-0.3, name='wave crash 2 (spray f58)')

# ------------------------------------------------------------------ S2 + S3 interior (storm muffled by stone and glass)
m.put(lowpass(trim_head(wind(6.6, 0.8, 0.7), 1.0), 380) * 1.6, at=T2, db=-17, fade_in=0.05, fade_out=0.25, name='wind through stone (muffled)')
t = t_axis(2.95); moan = bandpass(noise(2.95), 320, 760) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t) ** 2)
m.put(moan, at=T2, db=-24, fade_in=0.3, fade_out=0.3, name='slit-window moan')
m.put(lowpass(trim_head(rain(3.4, 0.7), 0.5), 1400), at=T2, db=-19, fade_out=0.15, name='rain on the tower (muffled)')
m.put(drone(3.2, f0=55, detune=0.3, lp=220, voices=3), at=T2 - 0.1, db=-27, fade_in=0.3, fade_out=0.3, name='tower resonance')
m.put(highpass(trim_head(rain(2.9, 0.9), 0.5), 1800), at=T3, db=-21, fade_in=0.03, fade_out=0.2, name='rain on the lantern glass')
m.put(lowpass(trim_head(wind(3.4, 0.7, 0.5), 1.0), 700), at=T3, db=-21, fade_out=0.2, name='wind round the lantern')

# S2 action: look-up, crouch inhale, launch, iron footsteps on her contacts (on 2s), panting
m.put(breath(0.32, 'in'), at=F(78), db=-21, name='inhale (crouch, anticipation)')
m.put(step(1150) * 0.5, at=F(80), db=-20, name='scuff (crouch)')
m.put(step(1210), at=F(84), db=-17, name='push-off (launch)')
steps = np.zeros(int((T3 - T2 + 1.5) * SR), np.float32)
for k, f in enumerate([92, 100, 108, 116, 124, 132]):
    s_ = step(1200 + (k % 3 - 1) * 40 + k * 6) * (0.85 + 0.15 * ((k * 7) % 3) / 2); i0 = int((F(f) - T2) * SR); steps[i0:i0 + len(s_)] += s_
m.put(reverb(steps, size=0.75, decay=1.1, mix=0.32)[:len(steps)], at=T2, db=-6, name='iron stair contacts f92..f132 (stairwell verb)')
for at in [F(96), F(112), F(128)]:
    m.put(breath(0.26, 'out'), at=at, db=-24, name='pant')

# ------------------------------------------------------------------ S3 lever: hold, wind-up, push, CLUNK, silence, IGNITION
m.put(breath(0.3, 'out'), at=T3 + 0.02, db=-23, name='pant (arrives)')
creak = pluck(note('E', 2), 0.5, bright=0.15) * 0.9 + bandpass(noise(0.5), 500, 1600) * np.exp(-t_axis(0.5) * 5) * 0.25
m.put(creak, at=F(144), db=-15, name='lever wind-up creak (pluck low) f144')
m.put(breath(0.24, 'in'), at=F(145), db=-21, name='inhale (wind-up)')
m.put(breath(0.22, 'out'), at=F(150), db=-18, name='effort (push) f150')
choir_full = choir(DUR - T3, freqs=(220.0, 277.18, 329.63), breath=0.22)       # A3 C#4 E4, bright key
cg = env(len(choir_full), [(0, 0.0), (0.35, 0.12), (F(156) - T3, 0.2), (F(168) - T3, 0.2), (F(168) - T3 + 0.4, 0.55), (T4 - T3, 0.75), (T4 - T3 + 0.8, 1.0), (DUR - T3, 0.9)])
m.put(choir_full * cg, at=T3, db=-14, name='choir A3 C#4 E4 (rises from S3, peaks in S4)')
# the world holds its breath: everything placed so far is pulled -30 dB for 12 frames (f156-f167)
m.duck(F(156), F(168), -30, 0.02)
m.put(clunk(), at=F(154), db=-5, name='CLUNK f154 (short, no tail)')
m.put(hit(1.6, sub=55, click=False, tail=True, crunch=0.35), at=F(168), db=-4, name='IGNITION f168 (whumpf)')
m.put(sub_drop(1.2, 70, 34), at=F(168), db=-9, name='  ignition sub')
m.put(highpass(noise(0.9), 3500) * np.exp(-t_axis(0.9) * 4), at=F(168), db=-22, name='  flare shimmer')
m.put(hum(3.0, f=110, level=0.6), at=F(168), db=-21, fade_in=0.5, name='lamp hum 110 Hz (rising, holds into S4)')
m.put(riser(T4 - F(168), 220, 1760, noise_mix=0.35, curve=1.8), at=F(168), db=-20, name='lamp riser -> ends on the S4 cut')

# ------------------------------------------------------------------ S4 exterior again: the beam passes, choir peaks, storm continues
m.put(trim_head(wind(3.0, 0.8, 0.6), 1.0), at=T4, db=-16, fade_in=0.03, name='storm wind (ext)')
m.put(trim_head(rain(2.5, 0.8), 0.5), at=T4, db=-15, fade_in=0.03, name='rain (ext)')
m.put(surf(2.0, 3.1), at=T4, db=-16, name='sea surge')
m.put(whoosh(1.2, 220, 3600), at=T4, db=-11, name='beam whoosh 1.2 s (peak f206 = 8.58 s)')
m.put(choir(DUR - T4 + 0.6, freqs=(440.0, 554.37, 659.26), breath=0.1)[int(0.6 * SR):], at=T4, db=-24, name='choir octave (peak)')
m.put(drone(2.4, f0=55, detune=0.2, lp=300, voices=4, shape='sine'), at=T4, db=-24, fade_in=0.2, name='low pad under the hold')

m.write(out)
print('wrote', out)
for a, n, d in sorted(m.cues):
    print(f'  {a:6.3f}s  f{a * FPS:6.1f}  {n:52s} {d:4.2f}s')
