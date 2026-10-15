"""P10 CLAY - sound cue sheet (6.0 s). Run: python3 audio.py out.wav
Picture is animated on 2s, so every cue sits on the even frame of the pose it belongs to (t = f/24 s):
  f4/f14/f24  pluck motif C5 E5 G5 (pride, rule of three) | f34 varied repeat C5 -> Eb5 (the turn: eyes dart up)
  f37.6-f52   falling whistle + descending wind whoosh, ending on the impact pose
  f52 2.167s  IMPACT: soft clay splat (sub 70 Hz + short low-passed noise, no reverb tail) + table thump
  f52-f60     8 frames of silence (room tone dipped) | f62 tiny squeak (pupils pin) | f64-f96 the apple rolls off (soft)
  f82/f94/f106 three ascending boings (re-inflation: small, medium, overshoot) | f110 shell pops back (soft plop)
  f124        resolving pluck chord (dignified look) | f132 blink click (very quiet) | chord tail to the end
Brief deviations: cue times are snapped to the pose frames (2.2 -> 2.167, 2.6 -> 2.583, 3.4/3.9/4.4 -> 3.417/3.917/4.417,
5.2 -> 5.167 s) so sound never leads picture by more than a frame (R-9-14)."""
import os
import sys

import numpy as np
from scipy import signal as sps

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *  # noqa: F401,F403  (SR, Mix, pluck, tone, whoosh, hit, noise, lowpass, highpass, bandpass, env_adsr, fade, t_axis, note, seed)

seed(1010)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
F = lambda f: f / 24.0
DUR = 6.0
m = Mix(DUR)

# ------------------------------------------------------------------ local instruments
def uke(freq, dur=1.2, bright=0.62):
    """Ukulele-ish: Karplus-Strong pluck, faster decay than the kit default, a small nylon body resonance."""
    x = pluck(freq, dur, bright) * np.exp(-t_axis(dur) * 2.6)
    body = bandpass(x, 180, 2600) * 0.6 + x * 0.4
    return fade(body.astype(np.float32), 0.002, 0.08)

def glide(f0, f1, dur, wave='tri', curve=0.55, wobble=0.0, a=0.004, d=0.06, s=0.65, r=0.14):
    """Pitch-glide tone (the kit's tone() is fixed-pitch). Optional decaying spring wobble for boings."""
    t = t_axis(dur); u = (t / dur) ** curve
    f = f0 * (f1 / f0) ** u * (1 + wobble * np.sin(2 * np.pi * 17 * t) * np.exp(-t * 7))
    ph = 2 * np.pi * np.cumsum(f) / SR
    w = sps.sawtooth(ph, 0.5) if wave == 'tri' else np.sin(ph)
    return (w * env_adsr(len(t), a, d, s, r)).astype(np.float32)

def splat(dur=0.24):
    """Soft clay splat: sub thump at 70 Hz + a short burst of low-passed noise; no reverb tail, dead after ~0.15 s
    (the kit hit() keeps a slow sub decay even with tail=False, so it is re-enveloped here)."""
    t = t_axis(dur)
    body = hit(dur, sub=70.0, click=True, tail=False, crunch=0.9) * np.exp(-t * 14)
    wet = lowpass(noise(dur), 1100, 3) * np.exp(-t * 30) * 1.4          # the squelch
    smack = bandpass(noise(dur), 500, 3200) * np.exp(-t * 90) * 0.5       # first contact
    return fade((body + wet + smack).astype(np.float32), 0.0, 0.05)

def thump(dur=0.20, f0=52.0):
    """Table thump: the set takes the hit (low, short)."""
    t = t_axis(dur); ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.6 * np.exp(-t * 30))) / SR
    return fade((np.sin(ph) * np.exp(-t * 22) + lowpass(noise(dur), 300) * np.exp(-t * 40) * 0.5).astype(np.float32), 0.0, 0.05)

def tok(dur=0.12, f0=420.0):
    """Small hollow knock (apple drops off the pancake onto paper)."""
    t = t_axis(dur)
    return fade((np.sin(2 * np.pi * f0 * t) * np.exp(-t * 60) + bandpass(noise(dur), 300, 2500) * np.exp(-t * 120) * 0.6).astype(np.float32), 0.0, 0.02)

def click(dur=0.03):
    t = t_axis(dur)
    return fade((highpass(noise(dur), 3000) * np.exp(-t * 400) * 0.6 + np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 220) * 0.5).astype(np.float32), 0.0, 0.005)

# ------------------------------------------------------------------ bed: quiet room tone with slow movement (no loops)
t6 = t_axis(DUR)
room = lowpass(noise(DUR, 'pink'), 900) * (1 + 0.22 * np.sin(2 * np.pi * 0.11 * t6) + 0.12 * np.sin(2 * np.pi * 0.29 * t6 + 1.3))
room = room + highpass(noise(DUR), 5000) * 0.05
m.put(room.astype(np.float32), at=0.0, db=-36, fade_in=0.4, fade_out=0.3, name='room tone')

# ------------------------------------------------------------------ the pride motif (rule of three) and its turn
m.put(uke(note('C', 5)), at=F(4), db=-8, pan=-0.12, name='pluck C5 (stalks dip)')
m.put(uke(note('E', 5)), at=F(14), db=-8, pan=0.0, name='pluck E5 (admires shell)')
m.put(uke(note('G', 5)), at=F(24), db=-7, pan=0.12, name='pluck G5 (proud wiggle)')
m.put(uke(note('C', 5), 0.6), at=F(34), db=-9, pan=-0.08, name='varied: C5 (eyes dart up)')
m.put(uke(note('D#', 5), 0.9, 0.5), at=F(36), db=-9, pan=0.08, name='varied: Eb5 (uh-oh)')

# ------------------------------------------------------------------ the drop: descending wind whoosh + whistle, ends on the impact
drop_at = F(52) - 0.6
m.put(whoosh(0.6, lo=3200, hi=500), at=drop_at, db=-18, fade_out=0.14, name='wind drop (whoosh 3.2k->500)')   # lo>hi: kit whoosh only sweeps lo->hi
wh = glide(2300, 760, 0.6, wave='sine', curve=1.6) * (1 + 0.04 * np.sin(2 * np.pi * 6 * t_axis(0.6)))
m.put(fade(wh.astype(np.float32), 0.10, 0.12), at=drop_at, db=-27, name='falling whistle 2.3k->760')

# ------------------------------------------------------------------ IMPACT (f52) then 8 frames of silence
m.put(splat(), at=F(52), db=-6, name='IMPACT splat (sub 70)')
m.put(thump(), at=F(52), db=-11, name='set thump')
m.duck(F(52) + 0.16, F(61), -9, 0.04)              # dead air after the splat (room tone dips, nothing else plays)
m.put(fade(glide(1760, 1840, 0.06, wave='sine', a=0.004, d=0.02, s=0.8, r=0.02), 0.0, 0.01), at=F(62), db=-24, name='squeak (pupils pin)')

# ------------------------------------------------------------------ the apple rolls off (soft foley)
roll_d = F(90) - F(64)
tr = t_axis(roll_d); spd = np.interp(tr, [0, F(66) - F(64), F(74) - F(64), F(88) - F(64), roll_d], [0.0, 0.1, 1.0, 0.2, 0.0])
roll = lowpass(noise(roll_d, 'brown'), 260) * 3.0 * spd + bandpass(noise(roll_d), 600, 2000) * 0.08 * spd
m.put(fade(roll.astype(np.float32), 0.05, 0.1), at=F(64), db=-27, pan=0.35, name='apple roll')
m.put(tok(), at=F(76), db=-23, pan=0.4, name='apple drops off the pancake')
m.put(tok(0.08, 520), at=F(80), db=-31, pan=0.45, name='apple bounce')

# ------------------------------------------------------------------ re-inflation: three ascending boings, then the shell pops last
m.put(glide(180, 260, 0.34, wobble=0.035), at=F(82), db=-14, pan=-0.05, name='boing 1 180->260 (small)')
m.put(glide(220, 330, 0.36, wobble=0.035), at=F(94), db=-14, pan=0.0, name='boing 2 220->330 (medium)')
m.put(glide(260, 420, 0.42, wobble=0.045), at=F(106), db=-14, pan=0.05, name='boing 3 260->420 (overshoot)')
m.put(fade(glide(620, 210, 0.07, wave='sine', curve=0.4, a=0.002, d=0.02, s=0.6, r=0.03), 0.0, 0.01), at=F(110), db=-25, name='shell pops back (plop)')

# ------------------------------------------------------------------ dignity: resolving chord, one slow blink
for k, (n, o) in enumerate([('C', 4), ('E', 4), ('G', 4), ('C', 5)]):
    m.put(uke(note(n, o), 0.84, 0.55), at=F(124) + 0.012 * k, db=-10, pan=-0.15 + 0.1 * k, fade_out=0.25, name=f'chord {n}{o}')
m.put(click(), at=F(132), db=-32, name='blink click')

m.write(out, peak_db=-1.0, target_rms_db=-21.0)
print('wrote', out)
for a, nme, dd in sorted(m.cues):
    print(f'  {a:5.3f}s  f{a * 24:6.1f}  {nme:34s} {dd:4.2f}s')
