"""P04 WITNESS - sound cue sheet (6.0 s). Run: python3 audio.py out.wav
Phase map (cut on frame 63 = 2.625 s):
  S1 0-2.625  room tone + candle fire; quill scratching locked to the nib's strokes (word A 0-0.70, lift, word B 0.84-1.90,
              faltering from 1.45); THE STOP at 1.90: the scratch dies and everything but the room tone drops 8 dB within one
              frame and stays down to the cut (17 f of near-silence, >= 12 f rule) - the writer is listening.
  S2 2.625-6  HIT ON THE CUT: first distant boot/drum (70 bpm, grows -36 -> -20 dB) + low thump; drone (f0 49, lp 300) rises
              from the cut; window rattle 4.60 (crackle burst + thump, the lattice judders on screen); distant horn 5.00
              (saw, lowpassed, far reverb, no voices); ends on the drone at full (the cut to black is the next scene's job)."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
seed(1628)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
FPS = 24
DUR = 6.0
T_CUT = 63 / FPS          # 2.625
T_STOP = 1.90
T_RATTLE, T_HORN = 4.60, 5.00


def _smooth(a, b, x):
    u = np.clip((x - a) / (b - a), 0.0, 1.0); return u * u * (3 - 2 * u)


def nib_speed(t):
    """Relative nib speed, identical in shape to blender.py nib_state (word A, lift, word B faltering, stop)."""
    t = np.asarray(t, dtype=np.float64)
    a = (t < 0.70).astype(np.float64)
    g = (1.0 - 0.72 * _smooth(1.45, 1.68, t)) * (1.0 - _smooth(1.76, T_STOP, t))
    b = ((t >= 0.84) & (t < T_STOP)).astype(np.float64) * g
    return a + b


def quill_scratch(dur, loops_per_s=4.6):
    n = int(dur * SR); t = np.arange(n) / SR
    sp = nib_speed(t)
    phase = np.cumsum(sp * loops_per_s) / SR                       # loops written so far
    stroke = 0.35 + 0.65 * np.abs(np.sin(2 * np.pi * phase)) ** 0.8  # up- and down-strokes: two swells per loop
    hiss = highpass(noise(dur), 2600) * 0.55 + bandpass(noise(dur), 1100, 4200) * 0.45
    grit = highpass(crackle(dur, 320, 0.9), 1800)                   # fibres catching the split nib
    sig = (hiss * 0.45 + grit) * sp * stroke
    return sig.astype(np.float32)


def tick(dur=0.05, f=3200.0):
    t = t_axis(dur); return (bandpass(noise(dur), f * 0.6, f * 1.6) * np.exp(-t * 140)).astype(np.float32)


def gain_ramp(x, db0, db1, curve=1.6):
    u = np.linspace(0.0, 1.0, len(x)) ** curve
    return (x * (10 ** ((db0 + (db1 - db0) * u) / 20))).astype(np.float32)


def horn(dur=1.1, f=146.8):
    t = t_axis(dur)
    bend = 1.0 - 0.035 * np.exp(-t * 9) + 0.004 * np.sin(2 * np.pi * 5.2 * t) * _smooth(0.15, 0.4, t)
    ph = 2 * np.pi * np.cumsum(f * bend) / SR
    x = sum(g * np.sin(k * ph) for k, g in [(1, 1.0), (2, 0.55), (3, 0.35), (4, 0.2), (5, 0.12)])
    x = x * 0.6 + 0.4 * tone(f, dur, 'saw', a=0.06, d=0.2, s=0.8, r=0.35)
    x = lowpass(x * env_adsr(len(t), 0.07, 0.25, 0.75, 0.45), 700)
    return reverb(x, size=0.95, decay=2.2, mix=0.55)[:len(t) + int(0.9 * SR)].astype(np.float32)


def norm(x):
    """Peak-normalise a generator so a placement level means 'peak at N dBFS' (the kit's raw levels differ by ~15 dB)."""
    x = np.asarray(x, dtype=np.float32); return x / (np.max(np.abs(x)) + 1e-9)


m = Mix(DUR)            # everything that ducks at the STOP
# --- beds
m.put(norm(fire(DUR, 0.4)), at=0.0, db=-26, fade_in=0.05, name='candle fire 0.4 (bed)')
# --- S1: the quill, locked to the strokes
m.put(norm(quill_scratch(T_STOP + 0.05)), at=0.0, db=-17, name='quill scratch (word A, word B)')
m.put(norm(tick(0.05, 2600)), at=0.84, db=-24, name='nib touches down (word B)')
m.put(norm(tick(0.08, 1800)), at=T_STOP - 0.02, db=-28, name='nib comes to rest')
# --- THE STOP: everything placed so far drops 8 dB within a frame and stays down to the cut (17 f)
m.duck(T_STOP, T_CUT - 0.01, depth_db=-8.0, ramp=1.0 / FPS)
# --- S2: the threat (placed after the duck, so not ducked)
m.put(gain_ramp(norm(drone(DUR - T_CUT, f0=49.0, detune=0.45, lp=300, voices=6)), -30, -12, 1.3), at=T_CUT, db=0, fade_in=0.08,
      name='drone f0 49, lp 300 (rises -30 -> -12 dB)')
m.put(gain_ramp(norm(drone(DUR - T_CUT - 0.8, f0=73.4, detune=0.6, lp=420, voices=4)), -36, -20, 1.2), at=T_CUT + 0.8, db=0,
      fade_in=0.3, name='drone fifth (swell)')
boots = norm(lowpass(heartbeat(DUR - T_CUT + 0.2, bpm=70, level=1.0), 180))
m.put(gain_ramp(boots[:int((DUR - T_CUT) * SR)], -36, -20, 1.4), at=T_CUT, db=0, name='distant boots/drum 70 bpm (-36 -> -20 dB)')
m.put(norm(sub_drop(0.7, 52, 34)), at=T_CUT, db=-17, name='HIT ON THE CUT: low thump')
m.put(gain_ramp(norm(wind(DUR - T_CUT, 0.25, 0.5)), -34, -26), at=T_CUT, db=0, fade_in=0.5, name='night air through the glass')
rat = highpass(crackle(0.42, 420, 1.0), 900) * np.exp(-t_axis(0.42) * 7)
m.put(norm(rat), at=T_RATTLE, db=-18, name='window rattle (crackle burst)')
m.put(norm(hit(0.9, sub=58, click=False, tail=True, crunch=0.2)), at=T_RATTLE, db=-21, name='window rattle (low thump)')
m.put(norm(horn(1.0, 146.8)), at=T_HORN, db=-30, pan=-0.35, name='distant horn (saw, lowpassed, far)')
# --- room tone: never ducked (added after the duck)
rt = norm(lowpass(noise(DUR, 'pink'), 380)) * (1 + 0.15 * np.sin(2 * np.pi * 0.11 * t_axis(DUR)))
m.put(rt, at=0.0, db=-40, name='room tone (never ducked)')
m.write(out)

# --- report
import soundfile as sf
x, sr = sf.read(out)
pk = 20 * np.log10(np.max(np.abs(x)) + 1e-12)
print('wrote', out, f'{len(x) / sr:.3f} s', f'peak {pk:.2f} dBFS')
for a, n, d in sorted(m.cues): print(f'  {a:5.2f}s  {n:44s} {d:4.2f}s')
mono = x.mean(axis=1)
def rms_db(a, b): s = mono[int(a * sr):int(b * sr)]; return 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-12)
def pk_db(a, b): s = mono[int(a * sr):int(b * sr)]; return 20 * np.log10(np.max(np.abs(s)) + 1e-12)
print(f'  silence {T_STOP:.2f}-{T_CUT:.3f}s ({(T_CUT - T_STOP) * FPS:.0f} f): rms {rms_db(T_STOP + 0.05, T_CUT - 0.01):.1f} dB'
      f' | hit window peak {pk_db(T_CUT, T_CUT + 0.25):.1f} dB | gap {pk_db(T_CUT, T_CUT + 0.25) - rms_db(T_STOP + 0.05, T_CUT - 0.01):.1f} dB')
