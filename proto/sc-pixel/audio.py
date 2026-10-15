"""P13 PIXEL VIGIL — sound cue sheet (10 s, 24 fps). Run: python3 audio.py out.wav
Phase map (frames @24): S1 0-86 wide city pan (rain + hum + buzz + slow chip pulse) | cut 87 (3.625 s) | S2 87-172 MS behind the watcher
| 116-129 HELD BREATH (everything pulled to -50 dB, 14 f) | 130 (5.417 s) window lights: sine chime + soft 3-note arpeggio enters
| cut 173 (7.208 s) | S3 173-239 footfalls at f186 / f194, window pulse period 1.7 s, wind gust ramps f212->239, tail to 10.0 s.
The neon buzz drops out on the SAME frames the picture flickers: the FLICK tables are parsed from world.js (single source of truth)."""
import sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness', 'audio'))
from sfx import *
seed(1313)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
DUR, FPS = 10.0, 24
F = lambda f: f / FPS                                  # frame -> seconds
CUT2, CUT3, LIGHT, STEP1, STEP2, GUST0, GUST1 = 87, 173, 130, 186, 194, 212, 239
SIL0, SIL1 = 116, 130                                  # held-breath window: frames 116..129 (14 f) before the chime
T = t_axis(DUR)

def curve(pts):                                        # [(seconds, dB)] -> linear gain over the whole mix (piecewise-linear in dB)
    ts, gs = zip(*pts); return db(np.interp(T, ts, gs)).astype(np.float32)

# ---- picture-locked flicker tables (parsed from world.js so audio and picture cannot drift apart)
src = open(os.path.join(HERE, 'world.js')).read()
def tab(txt): return [(int(a), int(b), float(c)) for a, b, c in re.findall(r'\[(\d+),\s*(\d+),\s*([\d.]+)\]', txt)]
FL = {}
blk = re.search(r'export const FLICK = \{(.*?)\n\};', src, re.S).group(1)
for k in ('ring', 'zig', 'eq', 'stack'): FL[k] = tab(re.search(k + r':\s*(\[\[.*?\]\]),', blk, re.S).group(1))
FL['far'] = sum((tab(m) for m in re.findall(r"neon\.sign\(b3,.*?flick:\s*(\[\[.*?\]\])", src)), [])

def mask(events):                                      # 1 = buzz on, 0 = dropout, .35 = dim; 2 ms smoothing so dropouts never click
    g = np.ones(len(T), dtype=np.float32)
    for a, n, lv in events: g[int(F(a) * SR):int(F(a + n) * SR)] = 0.0 if lv <= 0 else 0.35
    k = int(0.003 * SR); return np.convolve(g, np.ones(k) / k, mode='same').astype(np.float32)
def relight_ticks(events, level_db=-38):               # a tiny electric tick each time a tube relights
    x = np.zeros(len(T), dtype=np.float32); tk = (np.sin(2 * np.pi * 2100 * t_axis(0.02)) + 0.5 * highpass(noise(0.02), 2500)) * np.exp(-t_axis(0.02) * 260)
    for a, n, lv in events:
        i = int(F(a + n) * SR); x[i:i + len(tk)] += tk[:len(x) - i] * (1.0 if lv <= 0 else 0.5)
    return (x * db(level_db)).astype(np.float32)

m = Mix(DUR)
# ================= BEDS (all full-length; slow gain movement so no bed is a flat loop)
# rain 0.7: two decorrelated stereo layers; wider/softer in the wide shot, closer from the cut to S2, a little more present in S3
for side, pan in ((1, -0.65), (2, 0.65)):
    m.put(rain(DUR, 0.7) * curve([(0, -4), (F(CUT2) - 0.125, -4), (F(CUT2) + 0.075, 0), (F(CUT3) - 0.06, 0), (F(CUT3) + 0.09, 1.0), (10, -1.5)]), at=0, db=-17, pan=pan, name=f'rain 0.7 ({"L" if side == 1 else "R"})')
# city hum: hum 50 + drone lp 200, breathing +-1.5 dB; sinks toward the held breath, opens again once the window lights
breath = 1.5 * np.sin(2 * np.pi * 0.11 * T + 0.6)
cityg = curve([(0, -3), (F(CUT2), -3), (4.4, -6), (F(SIL0), -9), (F(SIL1), -9), (6.4, -3), (10, -4)]) * db(breath)
m.put(hum(DUR, 50.0, 0.4) * cityg, at=0, db=-24, name='city hum 50 Hz')
m.put(drone(DUR, f0=50.0, detune=0.35, lp=200, voices=4, motion=0.06) * cityg, at=0, db=-24, name='city drone lp200')
# neon buzz: hum 120 per sign (slightly detuned so they beat), each dropping out on its own flicker frames; recedes in S2/S3 (signs leave frame)
bz = curve([(0, 0), (F(CUT2), 0), (F(CUT2) + 0.1, -3), (F(CUT3), -3), (F(CUT3) + 0.1, -9), (10, -9)])
for kind, f0, pan, lvl in (('ring', 120.0, -0.45, -33), ('zig', 120.9, 0.5, -34), ('eq', 119.2, -0.85, -35), ('stack', 121.4, 0.8, -35), ('far', 118.1, 0.0, -43)):
    x = (hum(DUR, f0, 0.5) + 0.45 * hum(DUR, 2 * f0 + 0.3, 0.5) + 0.2 * lowpass(noise(DUR), 3000) * 0.05) * mask(FL[kind]) * bz
    m.put(x, at=0, db=lvl, pan=pan, name=f'neon buzz {kind}')
    m.put(relight_ticks(FL[kind]), at=0, pan=pan, name=f'relight ticks {kind}')
# wind: a low bed from the window onward + the gust that follows the coat (picture gust ramps f212 -> f239)
wbed = wind(DUR + 1.2, 0.5, 0.3)[:len(T)]                  # generated long so its own 1 s fade-out falls after the end
wg = curve([(0, -60), (F(SIL1), -60), (6.2, -30), (8.4, -26), (F(GUST0), -17), (9.75, -4), (10, -7)])
m.put(wbed * wg, at=0, db=-8, pan=-0.1, fade_out=0.2, name='wind bed -> gust (f212-239)')
# ================= CHIP PULSE: slow 2-note square pulse (A2 / E3, lowpassed), -28 dB; one note per 0.725 s so a downbeat lands on each cut
def chip(freq, dur, lp=750):
    return lowpass(tone(freq, dur, 'square', a=0.006, d=0.16, s=0.5, r=0.35), lp)
P = 0.725                                              # 5 notes = cut 1 (3.625 s) exactly; the post-light notes re-lock to cut 2 (f173)
PULSE = [(k * P, k % 2) for k in range(7)] + [(5.8, 0), (6.525, 1), (F(CUT3), 0), (8.7, 0), (9.425, 1)]   # (time, 0=A2 1=E3); nothing inside the held breath, nothing between the footfalls
for t0, n in PULSE:
    m.put(chip(note('A', 2) if n == 0 else note('E', 3), 0.62), at=t0, db=-28 if t0 < SIL0 / FPS else -29, name=f'chip pulse {"A2" if n == 0 else "E3"}')
# ================= CUT ACCENTS (soft: the cuts are punctuation, not events)
m.put(hit(0.6, sub=50, click=False, tail=False, crunch=0.15), at=F(CUT2), db=-27, fade_out=0.3, name='cut 1 thump (S1->S2)')
m.put(whoosh(0.55, 250, 2400, 1), at=F(CUT2) - 0.275, db=-33, name='cut 1 air push (peaks on the cut)')
m.put(hit(0.6, sub=46, click=False, tail=False, crunch=0.15), at=F(CUT3), db=-26, fade_out=0.3, name='cut 2 thump (S2->S3)')
# ================= HELD BREATH: pull everything to -50 dB for frames 116-129 (>=12 f of near-silence before the chime)
m.duck(F(SIL0), F(SIL1), -50, 0.05)
m.duck(F(SIL1) - 0.01, F(SIL1), -14, 0.5)                 # beds come back up over half a second under the chime (the world re-opens)
# ================= THE SIGNAL (placed AFTER the duck so it is not ducked): sine chime on the lighting frame + soft arpeggio only from here on
def bell(f, dur=2.6):
    t = t_axis(dur); x = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2) + 0.28 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 3.5) + 0.1 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
    return (x * np.minimum(1, t / 0.004)).astype(np.float32)
m.put(reverb(bell(note('A', 5), 2.6), size=0.8, decay=2.0, mix=0.38)[:int(2.6 * SR)], at=F(LIGHT), db=-20, fade_out=0.9, name='CHIME (sine) = window lights f130')
def arp(notes, step, at, level, name, tail=0.9):       # 3 soft square notes, lowpassed + a little echo
    for i, (nm, o) in enumerate(notes):
        x = lowpass(tone(note(nm, o), 0.42, 'square', a=0.004, d=0.1, s=0.35, r=0.22), 1900); x = x + 0.35 * np.roll(x, int(0.19 * SR)) * (np.arange(len(x)) > int(0.19 * SR))
        m.put(x, at=at + i * step, db=level - (0 if i < 2 else 1), pan=0.15 * (i - 1), name=f'{name} {nm}{o}')
ARP = [('A', 4), ('C#', 5), ('E', 5)]
arp(ARP, 0.17, F(LIGHT) + 0.42, -30, 'arpeggio 1 (after light)')
arp(ARP, 0.2, F(CUT3) + 0.03, -31, 'arpeggio 2 (S3 start, E5 on glow peak 7.64)')
arp(ARP, 0.2, F(CUT3) + 1.7 * 1 + 0.03, -31, 'arpeggio 3 (final hold, E5 on glow peak 9.34)')
m.put(reverb(bell(note('E', 6), 1.8), size=0.8, decay=2.2, mix=0.45)[:int(1.8 * SR)], at=F(CUT3) + 0.425 + 1.7, db=-30, fade_out=0.6, name='soft bell tail (glow peak, end)')
# ================= FOOTFALLS: two planted steps, hit sub 60, very short, -22 dB, locked to the plant frames (+ a wet puddle slap)
for fr, pan in ((STEP1, 0.25), (STEP2, 0.3)):
    m.put(hit(0.32, sub=60, click=True, tail=False, crunch=0.25), at=F(fr), db=-22, pan=pan, fade_out=0.1, name=f'FOOTFALL thud f{fr}')
    sp = bandpass(noise(0.16), 1500, 6000) * np.exp(-t_axis(0.16) * 32)
    m.put(sp, at=F(fr), db=-33, pan=pan, name=f'puddle slap f{fr}')
m.write(out)
print('wrote', out)
for a, n, d in sorted(m.cues): print(f'  {a:6.3f}s  f{a * FPS:6.1f}  {n:48s} {d:4.2f}s')
