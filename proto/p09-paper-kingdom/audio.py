"""P09 PAPER KINGDOM — sound cue sheet (10 s). Run: python3 audio.py out.wav
All times come from the scene's integer frames (24 fps):
S1 0-71 (0.000-2.958) king's dip f6 / raise f12, army steps off on beat 1 = 0.778 s, toy march 108 bpm (tick every beat,
   low drum on 1 and 3); the 5th beat (a drum) lands ON the S2 cut at f72 = 3.000 s, then the march stops dead.
S2 72-143 (3.000-5.958) quiet low riser 3.000 -> ends ON the S3 cut at 6.000; rumbling paper flutter as the dragon surfaces
   (head breaks the hillock ~f90); spears level f86-104; wings unfold f96-122; head rears f108-118; FIRE f120 = 5.000 s.
S3 144-201 (6.000-8.375) hands enter f144, grasp f156-160, presses f162/f172/f182, SNAPS f166 = 6.917, f176 = 7.333,
   f186 = 7.750; 12 frames of silence f190-201 (7.917-8.417) under -60 dB.
S4 202-239 (8.417-10.000) soft gong + wooden flute G4 B4 D5 G5 + warm pad ON the cut, bird flutters, spears lower."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
seed(909)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
FPS = 24
F = lambda f: f / FPS                                  # frame -> seconds (cuts and cues share exact frame times)
BEAT, T0 = 60 / 108, 3.0 - 4 * 60 / 108
m = Mix(10.0)

def rustle(dur=0.3, dens=180, level=0.7, hp=1400, lp=9000):
    """paper rustle: crackle, high-passed, with a soft swell/decay envelope (every burst is freshly generated)."""
    x = crackle(dur, dens, level); x = highpass(lowpass(x, lp), hp)
    t = t_axis(dur); e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    return (x[:len(e)] * e).astype(np.float32)
def snap(level=1.0):
    """sharp paper crease: a hard click + a very short dense crackle burst."""
    t = t_axis(0.16); click = highpass(noise(0.16), 1500) * np.exp(-t * 95)
    return (click * 0.9 + crackle(0.16, 420, 1.0) * np.exp(-t * 30) * 1.4).astype(np.float32) * level
def tom(f0=96.0, dur=0.42):
    """low toy drum: pitched membrane thump with a short skin noise."""
    t = t_axis(dur); f = f0 * (1 + 0.45 * np.exp(-t * 26)); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 9) + lowpass(noise(dur), 900) * np.exp(-t * 40) * 0.35).astype(np.float32)
def woodtick(f=2900.0):
    t = t_axis(0.07); return (np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + highpass(noise(0.07), 3000) * np.exp(-t * 220) * 0.25).astype(np.float32)
def flute(freq, dur, vib=4.8):
    """wooden flute: soft triangle with breath noise and a delayed vibrato, slow attack."""
    t = t_axis(dur); v = 1 + 0.006 * np.sin(2 * np.pi * vib * t) * np.clip((t - 0.18) / 0.3, 0, 1)
    ph = 2 * np.pi * np.cumsum(freq * v) / SR; body = signal.sawtooth(ph, 0.5) * 0.8 + np.sin(ph) * 0.4
    breath = bandpass(noise(dur), freq * 1.5, min(freq * 6, 12000)) * 0.12
    return ((body + breath) * env_adsr(len(t), 0.14, 0.12, 0.8, 0.25)).astype(np.float32)

# ---- room tone under S1-S3: the theatre lamp's faint hum + air (ducked to silence before the bird)
m.put(hum(10.0, f=55.0, level=0.25), at=0.0, db=-38, fade_in=0.4, name='lamp hum (room tone)')
m.put(wind(10.0, 0.18, 0.5), at=0.0, db=-40, fade_in=0.6, name='room air')

# ---- S1: the king commands, the toy march
m.put(rustle(0.22, 160, 0.6), at=F(6), db=-24, name='king dip (rustle)')
m.put(rustle(0.4, 220, 0.8), at=F(12), db=-24, pan=-0.3, name='king raise (rustle)')
m.put(rustle(0.2, 140, 0.5), at=F(14), db=-30, pan=0.1, name='army crouch (rustle)')
for k in range(5):                                   # beats 0..4: tick every beat, low drum on 1 and 3 (beats 0, 2, 4)
    tb = T0 + k * BEAT
    m.put(woodtick(2900 + 37 * ((k * 7) % 5)), at=tb, db=-20 - 0.6 * (k % 2), pan=0.15, name=f'march tick {k + 1}')
    if k % 2 == 0: m.put(tom(96.0 - 3 * (k // 2)), at=tb, db=-20, name=f'march drum {k // 2 + 1}' + (' (ON the S2 cut)' if k == 4 else ''))
    if k < 4: m.put(rustle(0.16, 120, 0.4, hp=2000), at=tb + 0.02, db=-31, pan=0.2, name=f'step rustle {k + 1}')

# ---- S2: the dragon rises (march has stopped dead at 3.000)
m.put(riser(3.0, 48, 260, noise_mix=0.3, curve=1.5), at=3.0, db=-22, name='low riser -> ends ON the S3 cut')
m.put(drone(3.0, f0=41.2, detune=0.6, lp=260, voices=5), at=3.0, db=-26, fade_in=1.6, fade_out=0.02, name='low drone swell')
tf = t_axis(1.6); flap = lowpass(crackle(1.6, 520, 0.9), 1700) * (0.55 + 0.45 * np.sin(2 * np.pi * 11 * tf)) + lowpass(noise(1.6, 'brown'), 140) * 1.6
m.put(flap.astype(np.float32), at=F(86), db=-22, fade_in=0.5, fade_out=0.4, name='rumbling paper flutter (rise)')
for k, f in enumerate([86, 90, 94, 98]): m.put(rustle(0.18, 160, 0.5), at=F(f), db=-27, pan=-0.4 + 0.1 * k, name=f'spear level {k + 1}')
m.put(rustle(0.9, 300, 0.9, hp=700), at=F(96), db=-22, pan=0.4, fade_in=0.2, name='wings unfold (paper)')
m.put(rustle(0.3, 200, 0.7), at=F(108), db=-25, pan=0.3, name='head rears (anticipation)')
m.put(whoosh(0.8, 300, 4200, 1), at=F(120), db=-16, pan=-0.2, name='FIRE whoosh')
m.put(fire(0.95, 0.7), at=F(120), db=-22, fade_out=0.35, name='paper fire crackle')
m.put(rustle(0.9, 90, 0.5, hp=2500), at=F(122), db=-29, pan=-0.3, fade_out=0.3, name='spears tremble')

# ---- S3: the hands, three creases, then silence
m.put(rustle(0.45, 110, 0.6, hp=500, lp=4000), at=F(144), db=-26, name='hands enter (sleeve) ON the cut')
m.put(rustle(0.25, 240, 0.8), at=F(156), db=-24, name='grasp (paper)')
for k, (fp, fs) in enumerate([(162, 166), (172, 176), (182, 186)]):
    m.put(rustle(0.08, 300, 0.7, hp=2500), at=F(fp), db=-28, name=f'press {k + 1}')
    m.put(snap(), at=F(fs), db=-10, name=f'SNAP {k + 1} (crease)')
m.duck(F(190) - 0.0, F(202), -60, 0.05)              # 12 frames of real silence before the bird lifts (R-3-06)

# ---- S4: the bird into the light (placed after the duck, so nothing here is attenuated)
tg = t_axis(1.6); gong = pluck(note('G', 2), 1.6, 0.25) * 0.7
for k, r_ in enumerate([1.0, 1.47, 2.09, 2.76]): gong = gong + np.sin(2 * np.pi * 98.0 * r_ * tg + k) * np.exp(-tg * (1.2 + 0.6 * k)) * (0.35 / (k + 1))
m.put(reverb(gong.astype(np.float32), size=0.95, decay=3.2, mix=0.5)[:len(tg)], at=F(202), db=-14, fade_out=0.3, name='soft gong ON the cut')
for k, (nm, o) in enumerate([('G', 4), ('B', 4), ('D', 5), ('G', 5)]):
    st = F(202) + k * 0.3333; d = 10.0 - st
    m.put(reverb(flute(note(nm, o), d), size=0.7, decay=1.6, mix=0.3)[:int(d * SR)], at=st, db=-14 - 1.0 * (k == 3), fade_out=0.35, name=f'flute {nm}{o}')
m.put(pad(10.0 - F(202), freqs=(196.0, 246.9, 293.7), lp=1300), at=F(202), db=-22, fade_in=0.35, fade_out=0.45, name='warm pad G')
m.put(hum(10.0 - F(202), f=55.0, level=0.3), at=F(202), db=-36, fade_in=0.5, fade_out=0.3, name='lamp hum swells (brighter)')
for k, f in enumerate([206, 218]): m.put(lowpass(rustle(0.2, 260, 0.6, hp=600), 3500), at=F(f), db=-28, pan=0.15, name=f'wing flutter {k + 1}')
m.put(rustle(0.5, 120, 0.5), at=F(204), db=-30, pan=-0.2, fade_out=0.2, name='spears lower')
m.put(rustle(0.3, 140, 0.5), at=F(204), db=-29, pan=-0.5, name='king arm falls')
m.write(out)
print('wrote', out); [print(f'  {a:6.3f}s  f{a * FPS:6.1f}  {n:34s} {d:5.2f}s') for a, n, d in sorted(m.cues)]
