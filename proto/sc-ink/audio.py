"""P02 INK & EMBER — sound cue sheet (10 s, 24 fps). Run: python3 audio.py out.wav
All picture times are integer frames (cut = frame/24): S1 0-2.583 | S2 2.583-5.417 | S3 5.417-7.792 | S4 7.792-8.292 (SILENCE)
| S5 8.292-10.0. Picture sync points: lightning main stroke f26 (1.083-1.125 s, crack at 1.100 s lands inside it; restrike f28 =
+0.083 s), breath puffs f72 / f110, drop on the seal f168 = 7.000 s, chapter card f199 = 8.292 s.
Lantern swing extremes (= creaks) are 2.9 s and 4.1 s, the same constants scene.js uses (lanternAng)."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
seed(1022)
R = np.random.default_rng(1022)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
FPS = 24
T = dict(s2=62 / FPS, s3=130 / FPS, s4=187 / FPS, s5=199 / FPS, flash=26 / FPS, drop=168 / FPS)

# ------------------------------------------------------------------ scene-specific voices built from kit primitives
def rumble(dur, f=170):
    """Rolling thunder body: low-passed brown noise with an uneven, rolling envelope (no repeats)."""
    x = lowpass(noise(dur, 'brown'), f); x /= np.max(np.abs(x)) + 1e-9; t = t_axis(dur)
    env = (1 - np.exp(-t * 14)) * np.exp(-t * 1.05) * (0.62 + 0.38 * np.sin(2 * np.pi * 0.85 * t + 0.4) * np.sin(2 * np.pi * 2.1 * t + 1.3))
    return (x * env).astype(np.float32)
def crack(dur=0.9, restrike=2 / FPS):
    """Close lightning crack: bright noise burst + a second strike on the picture's restrike frame."""
    t = t_axis(dur); out = highpass(noise(dur), 1400) * np.exp(-t * 11)
    k = int(restrike * SR); tail = highpass(noise(dur), 900)[:len(t) - k] * np.exp(-t[:len(t) - k] * 16) * 0.7
    out[k:] += tail
    return saturate(out * 0.8, 1.6).astype(np.float32)
def creak(dur=0.75, f0=60.0, glide=1.45, body=note('D', 2)):
    """Iron bracket under a swinging lantern: stick-slip friction clicks (gliding rate) + a dull low pluck body, in reverb."""
    n = int(dur * SR); fr = np.zeros(n, dtype=np.float32); t = 0.0
    while t < dur - 0.012:
        i = int(t * SR); L = 70
        fr[i:i + L] += (np.exp(-np.linspace(0, 5, L)) * np.sin(np.linspace(0, np.pi * 7, L)) * (0.5 + 0.5 * R.random())).astype(np.float32)
        t += (1.0 / (f0 * (1 + (glide - 1) * t / dur))) * (0.8 + 0.4 * R.random())
    env = np.sin(np.pi * np.arange(n) / n) ** 0.8
    x = bandpass(fr, 450, 2600) * env * 0.9 + pluck(body, dur, bright=0.12) * 0.55
    return reverb(x.astype(np.float32), size=0.75, decay=1.6, mix=0.35)
def breath(dur=1.2, bright=1.0):
    """Exhale: band-passed noise swell (fricative 'h' attack, soft decay) with a little low body."""
    t = t_axis(dur); env = np.clip(t / 0.14, 0, 1) ** 1.4 * np.exp(-np.maximum(t - 0.14, 0) * 2.6)
    x = bandpass(noise(dur), 380, 2300 * bright) * 0.8 + lowpass(noise(dur), 300) * 0.35
    return (x * env).astype(np.float32)
def brush(dur=0.4):
    """Brush ink dragged on paper (the panel border drawing itself): dry hiss that follows the stroke speed."""
    t = t_axis(dur); env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.2 * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t))
    return (bandpass(noise(dur), 1800, 7000) * env).astype(np.float32)

m = Mix(10.0)
# ------------------------------------------------------------------ beds (slow movement, no loops)
m.put(rain(7.9, 0.6), at=0.0, db=-21, fade_in=0.8, name='rain bed (0.6)')
m.put(wind(7.9, 0.45, 0.45), at=0.0, db=-27, fade_in=1.2, name='wind layer (gusting)')
m.put(drone(7.9, f0=65.0, detune=0.35, lp=500.0, voices=4, motion=0.08), at=0.0, db=-23, fade_in=1.4, fade_out=2.4, name='cello drone f0 65 (fading)')
m.put(brush(0.38), at=0.04, db=-31, name='brush: border draws itself')
# ------------------------------------------------------------------ S1: thunder exactly with the flash (frame 26 = 1.083-1.125 s)
m.put(crack(), at=1.100, db=-17, name='THUNDER crack (+restrike f28)')
m.put(hit(2.6, sub=40.0, crunch=0.75), at=1.100, db=-13, name='thunder hit (sub 40)')
m.put(rumble(3.4), at=1.115, db=-11, pan=-0.15, name='thunder rumble tail')
# ------------------------------------------------------------------ S2: lantern, breath, piano A3 on the cut
m.put(piano(note('A', 3), 3.2), at=T['s2'], db=-17, name='piano A3 (cut S2)')
m.put(creak(0.75, 58, 1.5, note('D', 2)), at=2.90 - 0.12, db=-24, pan=0.45, name='lantern creak 1 (swing extreme 2.9 s)')
m.put(breath(1.15, 1.0), at=3.00 - 0.03, db=-27, pan=0.1, name='breath 1 (f72)')
m.put(creak(0.8, 52, 1.35, note('C#', 2)), at=4.10 - 0.12, db=-25, pan=0.45, name='lantern creak 2 (swing extreme 4.1 s)')
m.put(breath(1.3, 0.85), at=110 / FPS - 0.03, db=-26, pan=0.1, name='breath 2 (f110, after the glance)')
m.put(rain(2.9, 0.75), at=T['s2'], db=-27, pan=0.3, fade_in=0.05, fade_out=0.3, name='rain closer (hood, S2)')
# ------------------------------------------------------------------ S3: temptation
m.put(piano(note('E', 4), 3.0), at=T['s3'], db=-18, name='piano E4 (cut S3)')
m.put(piano(note('F', 4), 2.4), at=6.800, db=-19, name='piano F4 (minor second: the pull)')
m.put(riser(T['s4'] - 6.6, f_start=180, f_end=2200, noise_mix=0.55, curve=2.2), at=6.600, db=-20, name='riser -20 dB -> S4 cut')
drip = reverb(pluck(note('A', 5), 0.7, bright=0.85), size=0.7, decay=1.8, mix=0.5)
m.put(drip, at=T['drop'], db=-15, pan=0.2, name='DRIP on the seal (f168)')
m.put(highpass(noise(0.05), 3000) * np.exp(-t_axis(0.05) * 90), at=T['drop'], db=-24, pan=0.2, name='drip splash transient')
# ------------------------------------------------------------------ S4: real silence, 12 frames (R-3-06), cut clean (no ramp into the hit)
m.duck(T['s4'], 10.0, -120, 0.012)   # everything before S4 (incl. reverb tails) is gone for good; S5 cues are added after the duck
# ------------------------------------------------------------------ S5: the chapter card
m.put(hit(1.708, sub=44.0, crunch=0.35), at=T['s5'], db=-8, name='CARD HIT (low, -8 dB) f199')
m.put(sub_drop(1.7, 62, 30), at=T['s5'], db=-15, name='card sub drop')
m.put(choir(1.708, freqs=(110.0, 164.8, 220.0), breath=0.22), at=T['s5'] + 0.05, db=-25, fade_in=0.3, fade_out=0.5, name='tail pad (A2 E3 A3)')
m.put(rain(1.4, 0.35), at=8.6, db=-41, fade_in=0.9, fade_out=0.2, name='distant rain returns (room tone)')
m.write(out)
print('wrote', out); [print(f'  {a:6.3f}s  f{a * FPS:6.2f}  {n:44s} {d:4.2f}s') for a, n, d in sorted(m.cues)]
