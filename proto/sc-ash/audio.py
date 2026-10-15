"""P07 ASH ASCENT — sound cue sheet (6.0 s). Run: python3 audio.py out.wav
Phase map: 0-3.79 s quiet build (wind at altitude, sub rumble, one horn note swelling toward the crest, faint hooves)
| 3.79 s the sun's limb breaks the volcano (frame 91): the horn peaks, the high shimmer pad enters
| 3.9-4.95 s light reaches the rider, he halts and lifts his staff (hooves stop) | 5.417 s (frame 130) HARD CUT: the black is silent.
Hoof thuds are read from the scene's own gait (blender.hoof_plants), so they land on the plants."""
import sys, os, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness', 'audio'))
from sfx import *
spec = importlib.util.spec_from_file_location('p07_scene', os.path.join(HERE, 'blender.py')); scene = importlib.util.module_from_spec(spec); spec.loader.exec_module(scene)

seed(707)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
DUR = scene.TOTAL / scene.FPS                       # 6.0 s
CUT = scene.CUT / scene.FPS                          # 5.4167 s: picture and sound cut to black together
CREST = scene.T_CREST                                # 3.7917 s (frame 91): first frame the limb is visible (SUN_ROT is verified for it)
m = Mix(DUR)

# --- beds: wind at altitude (two decorrelated gusty layers, slow L/R drift) + sub rumble
m.put(wind(CUT, 0.5, 0.45), at=0.0, db=-22, pan=-0.35, fade_in=0.5, name='wind at altitude L')
m.put(wind(CUT, 0.5, 0.35), at=0.0, db=-24, pan=0.40, fade_in=0.9, name='wind at altitude R')
m.put(drone(CUT, f0=30.0, detune=0.35, lp=120, voices=4, motion=0.08), at=0.0, db=-24, fade_in=0.8, name='sub rumble (30 Hz)')

# --- one long horn note: saw 110 Hz, lowpassed 600, 2 s attack, swelling toward the crest, then holding to the cut
n = int((CUT - 0.35) * SR); tt = np.arange(n) / SR + 0.35
horn = lowpass(tone(110.0, CUT - 0.35, 'saw', a=2.0, d=0.1, s=1.0, r=0.05), 600.0)
swell = np.interp(tt, [0.35, 2.4, CREST, CUT], [db(-9), db(-5), db(0), db(-1.5)])
vib = 1.0 + 0.012 * np.sin(2 * np.pi * 4.6 * tt) * np.clip((tt - 1.5) / 2.0, 0, 1)   # breath of vibrato as it swells
m.put((horn * swell * vib).astype(np.float32), at=0.35, db=-18, name='horn A2 (saw 110, lp 600)')

# --- hooves: very short sub thumps on every plant until the halt (front plants a touch louder), panned to the rider
plants = scene.hoof_plants()
thud = hit(0.16, sub=70.0, click=False, tail=False, crunch=0.15)
for k, (tp, leg) in enumerate(plants):
    fade = 1.0 if tp < scene.T_REACT else max(0.0, 1.0 - (tp - scene.T_REACT) / 0.6)
    lvl = -30.0 + (1.5 if leg.endswith('F') else 0.0) + 20 * np.log10(max(fade, 1e-3))
    m.put(thud, at=tp, db=lvl, pan=-0.28, name=f'hoof {leg}' if k < 3 else '')
m.cues = [c for c in m.cues if c[1] != 'cue'] + [(plants[0][0], f'hooves x{len(plants)} (on plants)', 0.16)]

# --- the crest: high shimmer pad (C5 E5 G5) enters on the frame the limb breaks
m.put(choir(CUT - CREST, freqs=(523.25, 659.25, 783.99), breath=0.35), at=CREST, db=-30, fade_in=0.35, name='shimmer pad (sun crest)')

# --- hard cut to silence with the picture (4 ms anti-click ramp before the cut, then digital silence)
k = int(CUT * SR); r = int(0.004 * SR)
for ch in (m.L, m.R):
    ch[k - r:k] *= np.linspace(1.0, 0.0, r); ch[k:] = 0.0
m.cues.append((CUT, 'CUT TO BLACK: silence', DUR - CUT))
m.write(out)
print('wrote', out); [print(f'  {a:5.2f}s  {nm:34s} {d:4.2f}s') for a, nm, d in sorted(m.cues)]
