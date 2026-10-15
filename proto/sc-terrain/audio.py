"""P12 TERRAIN — sound cue sheet (10 s). Run: python3 audio.py out.wav   (timings come from timing.json, written by tools/timing.mjs from timing.js, the same module scene.js uses)
Phase map: S1 0-3.625 the pen is set down (wind, drone, one paper tap on CAMP II, quill) | S2 3.625-7.625 the tilt-down (choir swell, a clock ticking at 90 bpm, paper taps on THE BLACK TARN / THE SADDLE)
| S3 7.625-10 the cut to the low oblique, then 12 frames of near-silence (7.875-8.375, the quill thinning out as the ink runs dry) | 8.375 the route stops: low hit + 880 Hz marker ring, drone to the end."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
seed(1212)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
DUR = 10.0
TJ = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing.json')))
FPS, CUT2, CUT3, T = TJ['fps'], TJ['cutS2'], TJ['cutS3'], TJ['times']
PEN = np.array(TJ['penSpeed']); PEN_T, PEN_V = PEN[:, 0], PEN[:, 1] / TJ['penPeak']   # pen speed 0..1 (200 Hz), the same curve that drives the ink on screen
STOP, SIL0 = T['stop'], T['silenceFrom']                                               # 8.375 s (frame 201) / 7.875 s (frame 189)
m = Mix(DUR)
sheet = []                                                                              # (time, name, dur, dB, sync note) for the printed cue sheet
def cue(x, at, db, name, sync='', **kw):
    m.put(x, at=at, db=db, name=name, **kw)
    sheet.append((at, name, len(x) / SR, db, sync, 20 * np.log10(np.sqrt(np.mean(x ** 2)) * 10 ** (db / 20) + 1e-9), 20 * np.log10(np.max(np.abs(x)) * 10 ** (db / 20) + 1e-9)))
ss = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))

# ---- local sound design from kit primitives
def paper_hit(pitch=1.0, bright=1.0, dur=0.42):
    """A flat palm on a sheet of heavy paper: a soft low body, a mid slap, a few dry fibres. Re-rolled for each label (no repeats)."""
    t = t_axis(dur)
    body = np.sin(2 * np.pi * np.cumsum(118 * pitch * (1 + 1.3 * np.exp(-t * 55))) / SR) * np.exp(-t * 26)
    slap = bandpass(noise(dur), 650 * bright, 4300 * bright) * np.exp(-t * 36)
    fibre = highpass(noise(dur), 4800) * np.exp(-t * 100) * 0.35
    x = saturate(0.8 * body + 1.2 * slap + fibre + lowpass(noise(dur), 800) * np.exp(-t * 18) * 0.35, 1.2)
    x = reverb(x, size=0.3, decay=0.45, mix=0.18)[:len(t)]
    return fade((x / (np.max(np.abs(x)) + 1e-9) * 0.6).astype(np.float32), 0.0, 0.06)   # a tap on the sheet, not a slam: peak 0.6 before the -14 dB cue gain

def quill_scratch(t0, t1):
    """Crackle, highpassed, gated by the pen's own speed curve (same envelope that inks the route): the hand's wobble is audible, the scratch thins as the ink runs dry."""
    dur = t1 - t0; t = t_axis(dur) + t0; env = np.interp(t, PEN_T, PEN_V)
    x = highpass(crackle(dur, 150, 1.0), 2300) * env ** 0.85 + highpass(noise(dur), 3600) * 0.02 * env
    # ride the level up in the silent window so the dying pen is the last thing the ear holds (the global duck takes it back down)
    x *= 1 + 2.2 * ss(SIL0 - 0.30, SIL0 + 0.05, t)
    return fade(x.astype(np.float32), 0.04, 0.012)

def ring_tone(dur, f=880.0, ripples=(0.35, 0.80)):
    """tone(sine 880) with a slow exponential decay; it is re-excited softly on the frames where the two ink ripples leave the marker (age 0.35 s and 0.80 s)."""
    t = t_axis(dur); x = tone(f, dur, 'sine', a=0.004, d=0.05, s=1.0, r=0.5) * np.exp(-t / 0.8)
    lift = 1 + sum(g * np.where(t >= r0, np.exp(-(t - r0) / 0.2) * (1 - np.exp(-(t - r0) / 0.02)), 0) for r0, g in zip(ripples, (0.45, 0.30)))
    return (x * lift).astype(np.float32)

# ---- beds: wind 0.4 (stereo pair, decorrelated), the drone to the end
wt = t_axis(DUR); expo = 1 + 0.55 * ss(6.8, 9.2, wt)            # the wind opens up a little when the peaks stand against the sky (S3)
for side, pan in (('L', -0.6), ('R', 0.6)):
    cue((wind(DUR, 0.4, 0.4) * expo).astype(np.float32), 0.0, -30, f'wind 0.4 ({side})', 'bed, S3 opens up', pan=pan, fade_in=0.9, fade_out=0.5)
cue(drone(DUR, f0=55.0, detune=0.4, lp=400, voices=5, motion=0.10), 0.0, -24, 'drone A1 55 Hz lp400', 'to the end', fade_in=1.6, fade_out=0.5)

# ---- the quill: exactly while the route draws (pen down 0.60 s -> route complete 8.375 s)
cue(quill_scratch(T['draw0'], STOP), T['draw0'], -22, 'quill (crackle, highpassed)', f"pen down {T['draw0']:.2f} -> stop {STOP:.3f}")

# ---- one paper hit on every label pop (re-rolled, panned to where the label sits)
cue(paper_hit(1.00, 1.05), T['campPop'], -14, 'paper hit: CAMP II', 'label pop', pan=-0.35)
cue(paper_hit(0.82, 0.90), T['tarnPop'], -14, 'paper hit: THE BLACK TARN', 'label pop', pan=0.25)
cue(paper_hit(0.92, 0.97), T['saddlePop'], -14, 'paper hit: THE SADDLE', 'label pop', pan=0.10)

# ---- S2 only: the swell across the tilt-down, the clock
cue(choir(CUT3 + 0.12 - CUT2, freqs=(110.0, 164.8, 220.0), breath=0.25), CUT2, -26, 'choir swell (A2 E3 A3)', 'S2: across the tilt-down', fade_in=3.0, fade_out=0.45)
tk = tick(CUT3 - CUT2, bpm=90, level=0.9, f=2600)
beat = int(60 / 90 * SR); gains = np.random.default_rng(90).uniform(0.75, 1.0, 8)           # a hand-wound clock: each tick a hair different
for k in range(int((CUT3 - CUT2) / (60 / 90)) + 1): tk[k * beat:(k + 1) * beat] *= gains[k]
cue(tk, CUT2, -30, 'tick 90 bpm', 'S2 only: stops on the cut', fade_out=0.02)

# ---- 12 frames of near-silence before the route stops (7.875-8.375), everything pulled down; the next beat that would have landed on the cut never comes
m.duck(SIL0, STOP, -30, 0.12)
sheet.append((SIL0, 'NEAR-SILENCE (duck -30 dB)', STOP - SIL0, -30, f'{round((STOP - SIL0) * FPS)} frames, frame {round(SIL0 * FPS)}-{round(STOP * FPS) - 1}', float('nan'), float('nan')))

# ---- the route stops, the marker appears (frame 201): low hit + the ringing marker tone
cue(hit(2.4, sub=38, click=False, crunch=0.28), STOP, -12, 'LOW HIT', 'marker appears (frame 201)')
cue(ring_tone(10.0 - STOP), STOP, -22, 'marker ring sine 880 Hz', 'ripples at +0.35 / +0.80 s', fade_out=0.5)

m.write(out)
print('wrote', out)
print('  time    frame  cue                           dur    dB   rms/peak(pre-norm)  sync')
for a, n, d, g, s, r, p in sorted(sheet): print(f'  {a:6.3f}s f{round(a * FPS):3d}   {n:28s} {d:5.2f}s {g:4d}   {r:6.1f}/{p:6.1f}      {s}')
