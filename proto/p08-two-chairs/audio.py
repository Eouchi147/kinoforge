"""P08 TWO CHAIRS — sound (12 s). Run: python3 proto/p08-two-chairs/audio.py out/p08-two-chairs/audio.wav

Reads the SAME cue file as the picture (lines/cues.json, written by build_lines.py) and the dialogue stems (lines/*.wav),
so every line lands on the frame the mouth track was built for (start_frame x 2000 samples @ 48 kHz).
Plan: room tone (low-passed noise, -40 dB RMS) under everything | warm pad (-34 dB RMS) from the top, dipped 6 dB through the
18-frame beat (R-3-06: the pause sits >=20 dB under the punchline), CUT on the S6 picture cut -> silence under the reaction,
room tone only to the end | two low chair creaks (-30 dB) on Remi's visible weight shifts | dialogue: each line gated-RMS
normalised to -16 dB, peak-limited at -2 dBFS, placed at 0 dB gain, centred. No music sting (deadpan, R-8-08)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness', 'audio'))
import numpy as np
import soundfile as sf
from sfx import seed, noise, lowpass, highpass, bandpass, pluck, fade, SR

seed(808)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
C = json.load(open(os.path.join(HERE, 'lines', 'cues.json')))
FPS = C['fps']; N = int(round(C['total_frames'] / FPS * SR)); SPF = SR // FPS          # 2000 samples per frame
L = np.zeros(N, dtype=np.float64); R = np.zeros(N, dtype=np.float64); cues = []
db = lambda x: 10 ** (x / 20)
rms_db = lambda x: 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


def put(x, at_sample, gain_db=0.0, pan=0.0, name=''):
    """Sample-exact placement. pan -1..1 as a balance (0 = dual mono at unity, i.e. '0 dB gain')."""
    x = np.asarray(x, dtype=np.float64) * db(gain_db); i = int(at_sample); j = min(N, i + len(x)); x = x[:j - i]
    L[i:j] += x * min(1.0, 1.0 - pan); R[i:j] += x * min(1.0, 1.0 + pan)
    cues.append((i / SR, name, len(x) / SR, rms_db(x[np.abs(x) > 1e-6]) if np.any(np.abs(x) > 1e-6) else -120))


def gated_rms_db(x, win=0.02, rel=-30.0):
    n = int(win * SR); fr = x[:len(x) // n * n].reshape(-1, n); e = np.sqrt(np.mean(fr ** 2, axis=1) + 1e-12)
    keep = 20 * np.log10(e) > 20 * np.log10(e.max()) + rel
    return 20 * np.log10(np.sqrt(np.mean(fr[keep] ** 2)) + 1e-12)


def limit(x, ceiling_db=-2.0, look=0.003, release=0.06):
    """Look-ahead peak limiter: per-sample gain floor, spread over the look-ahead window, exponential release."""
    c = db(ceiling_db); need = np.minimum(1.0, c / (np.abs(x) + 1e-12))
    k = int(look * SR); pad = np.concatenate([need, np.ones(k)])
    from numpy.lib.stride_tricks import sliding_window_view
    g = sliding_window_view(pad, k + 1).min(axis=1)[:len(x)]
    a = np.exp(-1.0 / (release * SR)); y = np.empty_like(g); cur = 1.0
    for i in range(len(g)):                      # fast attack (look-ahead already covers it), smooth release
        cur = g[i] if g[i] < cur else a * cur + (1 - a) * g[i]; y[i] = cur
    return x * y, 20 * np.log10(y.min())


def shaped_noise(dur, lp, s):
    seed(s); x = lowpass(noise(dur, 'pink'), lp, order=3); return x / (np.sqrt(np.mean(x ** 2)) + 1e-12)


ev = C['events']; shots = C['shots']
cut = lambda k: shots[k]['start_frame'] * SPF
dur = N / SR; t = np.arange(N) / SR

# ---- room tone: decorrelated L/R low-passed pink noise, slow +/-1.5 dB drift (no loop), -40 dB RMS
drift = db(1.5 * np.sin(2 * np.pi * t / 5.3 + 0.7) * np.sin(2 * np.pi * t / 2.9 + 0.2))
rt_l = shaped_noise(dur, 520, 11) * drift; rt_r = shaped_noise(dur, 520, 12) * drift
rt_l = fade(rt_l.astype(np.float32), 0.25, 0.03) * db(-40); rt_r = fade(rt_r.astype(np.float32), 0.25, 0.03) * db(-40)
L += rt_l; R += rt_r; cues.append((0.0, 'room tone (L/R decorrelated)', dur, rms_db(rt_l)))

# ---- warm pad: Cmaj7 (C3 E3 G3 B3), slow vibrato, low-passed; -34 dB RMS; 6 dB dip through the beat; hard cut on S6
freqs = (130.81, 164.81, 196.0, 246.94); pcut = cut(5); pdur = pcut / SR
tp = np.arange(pcut) / SR; pad = np.zeros(pcut)
for k, f0 in enumerate(freqs):
    ph = 2 * np.pi * f0 * tp + 0.18 * np.sin(2 * np.pi * (0.21 + 0.05 * k) * tp + k)
    pad += (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)) * (1 + 0.15 * np.sin(2 * np.pi * (0.13 + 0.04 * k) * tp + 2 * k))
pad = lowpass(pad, 900, order=2); pad = pad / np.sqrt(np.mean(pad ** 2)) * db(-34)
pad *= np.minimum(1, tp / 1.4) ** 2                                                     # slow fade-in from the top
b0, b1 = C['lines'][3]['off'], C['lines'][4]['on']                                      # the beat: end of "And?" -> punchline
dip = np.ones(pcut); r = int(0.08 * SR); i0, i1 = int(b0 * SR), int(b1 * SR) - r
dip[i0:i1] = db(-6); dip[i0 - r:i0] = np.linspace(1, db(-6), r); dip[i1:i1 + r] = np.linspace(db(-6), 1, r); pad *= dip
pad[-int(0.012 * SR):] *= np.linspace(1, 0, int(0.012 * SR))                            # 12 ms declick: silent by S6 frame 1
put(pad, 0, 0, 0, f'warm pad (cut at S6 {pdur:.3f}s)')


# ---- chair creaks: low Karplus-Strong plucks + a stick-slip wood rasp, -30 dB RMS, panned to Remi's side of the stage
def creak(var):
    seed(300 + var); d = 0.55; n = int(d * SR); tt = np.arange(n) / SR
    body = pluck(96 + 9 * var, d, 0.25)[:n] + 0.6 * np.concatenate([np.zeros(int(0.028 * SR)), pluck(131 + 7 * var, d, 0.2)])[:n]
    seed(310 + var); rasp = bandpass(noise(d), 280, 1400) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (23 + 4 * var) * tt))) * np.exp(-tt / 0.09)
    x = lowpass(body * 0.8 + rasp * 0.35, 2600); x = fade(x.astype(np.float32), 0.004, 0.2)
    act = x[: int(0.3 * SR)]; return x / (np.sqrt(np.mean(act ** 2)) + 1e-12) * db(-30)
put(creak(0), int(round(ev['creak1'] * SR)), 0, -0.3, 'chair creak 1 (Remi launches the list)')
put(creak(1), int(round(ev['creak2'] * SR)), 0, -0.35, 'chair creak 2 (Remi leans in, punchline cut)')

# ---- dialogue: gated-RMS -16 dB, peak-limited, 0 dB gain, centred, at the picture cue frame
for ln in C['lines']:
    x, sr = sf.read(os.path.join(HERE, ln['wav']), dtype='float64')
    assert sr == SR, f"{ln['wav']}: {sr} Hz"
    if x.ndim > 1: x = x.mean(axis=1)
    g0 = gated_rms_db(x); x = x * db(-16.0 - g0); x, gr = limit(x, -2.0)
    put(x, ln['start_frame'] * SPF, 0.0, 0.0, f"{ln['id']} {ln['who'].upper():4s} \"{ln['text']}\" (norm {-16 - g0:+.1f} dB, limiter {gr:.1f} dB)")

st = np.stack([L, R], axis=1).astype(np.float32)
pk = 20 * np.log10(np.max(np.abs(st)) + 1e-12)
assert st.shape[0] == N
sf.write(out, st, SR, subtype='PCM_24')
print('wrote', out, f'{st.shape[0] / SR:.4f} s ({st.shape[0]} samples = {st.shape[0] // SPF} frames), peak {pk:.2f} dBFS, mix RMS {rms_db(st):.1f} dB')
print('cue sheet:')
for a, n, d, lv in sorted(cues, key=lambda c: c[0]): print(f'  {a:7.3f}s  f{a * FPS:6.1f}  {d:5.2f}s  {lv:6.1f} dB  {n}')
