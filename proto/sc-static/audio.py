"""P01 STATIC — sound cue sheet (10 s, 24 fps). Run: python3 audio.py out.wav
Every time is a frame index / 24 and mirrors scene.js (CUT, EV, FLICKER). No music.
S1 f0-76   room tone of a tape: 60 Hz hum, hiss, failing tube's 120 Hz buzz (drops out on every P5 flicker + ballast ticks),
           sub drone enters. The clock stutter (f31-33) is deliberately SILENT: the clock is wrong, the tape is not.
S2 f77-138 tracking error f87-104 = hiss burst + low rumble; quiet thump on f104 when the band clears (door revealed).
S3 f139-208 Shepard rises -32 -> -20 dB with the zoom; 2 frames of true silence at the dropout (f173-174), a click on f175
           when the picture comes back with the figure in it; P5 dies again f183-186 (buzz gone, ticks).
S4 f209-222 SILENCE (everything -60 dB, 14 f) — the tape stops.
S5 f223-239 one 110 Hz sine, -30 dB, slow fade: the card."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
seed(214)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
FPS = 24
fr = lambda f: f / FPS                                   # frame -> seconds
CUT = [0, 77, 139, 209, 223, 240]
EV = dict(band=(87, 104), drop=(173, 175), figure=175)
FLICKER = [(14, 16, 0.06), (17, 18, 0.4), (54, 58, 0.04), (60, 61, 0.45), (120, 123, 0.05), (146, 148, 0.3), (183, 187, 0.03), (199, 200, 0.25)]
TAPE_END = fr(CUT[3])                                    # 8.7083 s: hard stop into black
m = Mix(10.0)

def trim(x, dur, fade_out=0.005):
    """cut a (longer) generated bed to exactly dur seconds with a click-free 5 ms tail, so it is at full level at the cut"""
    y = np.asarray(x[:int(dur * SR)], dtype=np.float32).copy(); k = int(fade_out * SR); y[-k:] *= np.linspace(1, 0, k); return y
def ramp_db(n, a_db, b_db, curve=1.0):
    u = np.linspace(0, 1, n) ** curve; return (10 ** ((a_db + (b_db - a_db) * u) / 20)).astype(np.float32)
def slow(n, depth=0.12, rate=0.13, ph=0.0):              # slow movement for beds (no loops: generated noise underneath)
    t = np.arange(n) / SR; return (1 + depth * np.sin(2 * np.pi * rate * t + ph) + 0.5 * depth * np.sin(2 * np.pi * rate * 2.7 * t + 1.3 * ph)).astype(np.float32)
def flicker_gain(n):
    g = np.ones(n, dtype=np.float32)
    for a, b, lv in FLICKER: g[int(fr(a) * SR):int(fr(b) * SR)] = lv
    k = int(0.003 * SR); return np.convolve(g, np.ones(k) / k, mode='same').astype(np.float32)  # 3 ms edges, no clicks
def click(dur=0.03, body=180.0):
    t = t_axis(dur); return (highpass(noise(dur), 1500) * np.exp(-t * 380) * 0.8 + np.sin(2 * np.pi * body * t) * np.exp(-t * 110) * 0.5).astype(np.float32)

n_tape = int(TAPE_END * SR)
# --- beds (S1-S3), all stopping dead on the cut to black
m.put(trim(hum(9.5, f=60.0, level=0.6), TAPE_END) * slow(n_tape, 0.06, 0.07), at=0, db=-28, fade_in=0.02, name='60 Hz ground hum (VCR)')
m.put(trim(tape_hiss(9.5, level=0.5), TAPE_END) * slow(n_tape, 0.15, 0.11, 2.0), at=0, db=-34, fade_in=0.02, name='tape hiss bed')
buzz = saturate(hum(9.5, f=120.0, level=0.8), 3.0); buzz = highpass(buzz, 100)
m.put(trim(buzz, TAPE_END) * flicker_gain(n_tape) * slow(n_tape, 0.05, 0.9), at=0, db=-36, fade_in=0.05, name='P5 tube buzz 120 Hz (flicker-synced)')
m.put(trim(drone(9.5, f0=36.7, detune=0.4, lp=150, voices=5), TAPE_END) * ramp_db(n_tape, -40, -26, 1.6), at=0, db=0, fade_in=0.8, name='sub drone building (lp 150)')
for a, b, lv in FLICKER:                                  # ballast ticks: the tube striking out and back
    m.put(highpass(noise(0.012), 3000) * np.exp(-t_axis(0.012) * 500), at=fr(a), db=-36, name=f'ballast tick f{a}')
    m.put(highpass(noise(0.012), 3000) * np.exp(-t_axis(0.012) * 500), at=fr(b), db=-40, name=f'ballast tick f{b}')
# --- S2: the tracking error, exactly f87-f104, then the reveal thump
b0, b1 = fr(EV['band'][0]), fr(EV['band'][1]); bd = b1 - b0; t = t_axis(bd)
env = np.minimum(1, t / 0.012) * np.minimum(1, (bd - t) / 0.04)
chop = 0.65 + 0.35 * np.sign(np.sin(2 * np.pi * 29 * t + 3 * np.sin(2 * np.pi * 3.1 * t)))   # head chatter
m.put(highpass(noise(bd), 1500) * env * chop, at=b0, db=-27, name='TRACKING ERROR hiss burst')
m.put(lowpass(noise(bd, 'brown'), 120) * env * 3.0, at=b0, db=-26, name='tracking rumble (lp 120)')
m.put(crackle(bd, 70, 0.7) * env, at=b0, db=-32, name='tracking crackle')
m.put(hit(2.2, sub=38, click=False, crunch=0.15), at=b1, db=-18, name='door-reveal thump (sub 38)')
# --- S3: the Shepard rise under the zoom, up to the hard cut
s0 = fr(CUT[2]); sd = TAPE_END - s0
m.put(trim(shepard(sd + 0.8, base=55, octaves=5, rate=0.12), sd) * ramp_db(int(sd * SR), -32, -20, 1.3), at=s0, db=0, fade_in=0.4, name='Shepard rise (-32 -> -20 dB)')
# --- silences: the 2-frame dropout, then the long black (R-3-06: 14 f at -60 dB before the card)
m.duck(fr(EV['drop'][0]), fr(EV['drop'][1]), -60, 0.003)
m.put(click(), at=fr(EV['figure']), db=-22, name='signal re-lock click (figure)')
m.duck(TAPE_END, fr(CUT[4]), -60, 0.004)
# --- S5: the card tone
cd = fr(CUT[5] - CUT[4])
m.put(np.sin(2 * np.pi * 110 * t_axis(cd)).astype(np.float32), at=fr(CUT[4]), db=-30, fade_in=0.25, fade_out=0.35, name='card tone 110 Hz')
m.write(out)
print('wrote', out)
for a, nme, d in sorted(m.cues): print(f'  {a:6.3f}s  f{a * FPS:6.1f}  {nme:40s} {d:5.2f}s')
