"""dsp.py: the small signal toolkit of the score engine (numpy and scipy only, nothing else to install).

Reverb (synthesised room, no impulse-response files), filters, a BS.1770 loudness meter, a look-ahead peak limiter,
a band-limited wavetable oscillator and a Karplus-Strong string. Everything is deterministic given the rng passed in.
"""
import numpy as np
from scipy import signal as sg
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 48000


# ---------------------------------------------------------------- small helpers
def db(x):
    return 10 ** (x / 20.0)


def lin2db(x):
    return 20 * np.log10(np.maximum(x, 1e-12))


def smoothstep(x, a, b):
    t = np.clip((x - a) / max(b - a, 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def pan_gains(p):
    """equal-power pan, p in -1..1 -> (left, right)"""
    a = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return float(np.cos(a)), float(np.sin(a))


def env_ar(n, attack, release, curve=2.0, sr=SR):
    """cosine-shaped attack and release over n samples (no clicks, no harsh onsets)"""
    e = np.ones(n, np.float32)
    na = min(n, max(1, int(attack * sr))); nr = min(n, max(1, int(release * sr)))
    e[:na] *= (np.sin(np.linspace(0, np.pi / 2, na)) ** curve).astype(np.float32)
    e[n - nr:] *= (np.cos(np.linspace(0, np.pi / 2, nr)) ** 1.5).astype(np.float32)
    return e


def smooth_noise(n, rate_hz, rng, sr=SR):
    """slow random drift in -1..1 (cubic interpolation of a few random points); n samples"""
    k = max(4, int(n / sr * rate_hz) + 3)
    pts = rng.uniform(-1, 1, k)
    xs = np.linspace(0, n - 1, k)
    from scipy.interpolate import CubicSpline
    return np.clip(CubicSpline(xs, pts)(np.arange(n)), -1, 1).astype(np.float32)


# ---------------------------------------------------------------- filters
def lowpass(x, fc, order=2, sr=SR, axis=0):
    return sg.sosfilt(sg.butter(order, fc, 'low', fs=sr, output='sos'), x, axis=axis).astype(np.float32)


def highpass(x, fc, order=2, sr=SR, axis=0):
    return sg.sosfilt(sg.butter(order, fc, 'high', fs=sr, output='sos'), x, axis=axis).astype(np.float32)


def bandpass(x, lo, hi, order=2, sr=SR, axis=0):
    return sg.sosfilt(sg.butter(order, [lo, hi], 'band', fs=sr, output='sos'), x, axis=axis).astype(np.float32)


def peaking_sos(f0, gain_db, q, sr=SR):
    """RBJ peaking biquad as a 1-section sos"""
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / sr; al = np.sin(w) / (2 * q); c = np.cos(w)
    b = np.array([1 + al * A, -2 * c, 1 - al * A]); a = np.array([1 + al / A, -2 * c, 1 - al / A])
    return np.concatenate([b / a[0], a / a[0]])[None, :]


def high_shelf_sos(f0, gain_db, sr=SR, slope=0.7):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / sr; c = np.cos(w); s = np.sin(w)
    al = s / 2 * np.sqrt((A + 1 / A) * (1 / slope - 1) + 2); sq = 2 * np.sqrt(A) * al
    b = np.array([A * ((A + 1) + (A - 1) * c + sq), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sq)])
    a = np.array([(A + 1) - (A - 1) * c + sq, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sq])
    return np.concatenate([b / a[0], a / a[0]])[None, :]


def eq(x, sos_list, axis=0):
    for s in sos_list:
        x = sg.sosfilt(s, x, axis=axis)
    return x.astype(np.float32)


# ---------------------------------------------------------------- reverb (synthesised room)
def make_ir(rt60, rng, sr=SR, predelay=0.018, damp=0.55, width=1.0):
    """Stereo impulse response of a warm, soft room/hall: decorrelated noise tails, bands decay at different speeds
    (lows linger, highs die fast), a few early reflections, a pre-delay, and a gentle fade in so nothing clicks."""
    n = int(rt60 * 1.15 * sr)
    t = np.arange(n) / sr
    out = np.zeros((n, 2), np.float32)
    for ch in range(2):
        noise = rng.standard_normal(n).astype(np.float32)
        lo = lowpass(noise, 400, 1, sr) * np.exp(-6.9 * t / (rt60 * 1.25))
        mid = bandpass(noise, 400, 3200, 1, sr) * np.exp(-6.9 * t / rt60)
        hi = highpass(noise, 3200, 1, sr) * np.exp(-6.9 * t / (rt60 * (1 - damp) + 0.15))
        out[:, ch] = lo * 0.9 + mid * 1.0 + hi * 0.55
    # gentle onset (diffusion build-up)
    ramp = np.minimum(1, t / 0.035) ** 1.5
    out *= ramp[:, None]
    # early reflections
    for tap, g in ((0.011, .5), (0.019, .42), (0.027, .36), (0.041, .3), (0.053, .24), (0.067, .2)):
        for ch in range(2):
            i = int((tap + rng.uniform(-0.003, 0.003) + ch * 0.0017) * sr)
            if i < n: out[i, ch] += g * (1 if rng.random() > .5 else -1)
    if width < 1:                                         # narrow the tail towards mono
        m = out.mean(axis=1, keepdims=True); out = m + (out - m) * width
    pd = int(predelay * sr)
    out = np.concatenate([np.zeros((pd, 2), np.float32), out])
    out /= np.sqrt((out ** 2).sum() / 2) + 1e-9           # unit energy per channel
    return out.astype(np.float32)


def convolve(x, ir):
    """x: (n,2) or (n,) float32 -> (n,2) wet signal, same length"""
    if x.ndim == 1: x = np.stack([x, x], 1)
    n = len(x)
    L = sg.oaconvolve(x[:, 0], ir[:, 0])[:n]
    R = sg.oaconvolve(x[:, 1], ir[:, 1])[:n]
    # cross-feed a little so a hard-panned source still blooms into both sides
    return np.stack([L + 0.25 * R, R + 0.25 * L], 1).astype(np.float32) * 0.8


# ---------------------------------------------------------------- dynamics
def limiter(x, ceiling_db=-3.5, hold=0.03, sr=SR):
    """transparent peak limiter: the gain dips smoothly (about 30 ms each side) around any peak above the ceiling,
    with the dip held by a minimum filter and rounded by a short smoothing window, so no click and no pumping"""
    ceil = db(ceiling_db)
    pk = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
    need = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    h = max(1, int(hold * sr))
    g = minimum_filter1d(need, size=2 * h + 1, mode='nearest')
    g = uniform_filter1d(g, size=h + 1, mode='nearest')
    y = x * g[:, None] if x.ndim == 2 else x * g
    peak = np.abs(y).max()
    if peak > ceil: y = y * (ceil / peak)                 # exact safety net
    return y.astype(np.float32)


# ---------------------------------------------------------------- loudness (ITU-R BS.1770-4, as used by EBU R128)
_KS_B1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]; _KS_A1 = [1.0, -1.69065929318241, 0.73248077421585]
_KS_B2 = [1.0, -2.0, 1.0]; _KS_A2 = [1.0, -1.99004745483398, 0.99007225036621]


def _kweight(x, sr):
    if sr != 48000:
        x = sg.resample_poly(x, 48000, sr, axis=0)
    y = sg.lfilter(_KS_B1, _KS_A1, x, axis=0)
    return sg.lfilter(_KS_B2, _KS_A2, y, axis=0)


def loudness(x, sr=SR):
    """integrated loudness in LUFS (stereo or mono array)"""
    if x.ndim == 1: x = x[:, None]
    y = _kweight(x.astype(np.float64), sr); sr = 48000
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    if len(y) < blk: return -70.0
    sq = (y ** 2).sum(axis=1) if y.shape[1] <= 2 else (y ** 2).sum(axis=1)
    c = np.concatenate([[0], np.cumsum(sq)])
    starts = np.arange(0, len(y) - blk + 1, hop)
    ms = (c[starts + blk] - c[starts]) / blk
    lk = -0.691 + 10 * np.log10(np.maximum(ms, 1e-12))
    keep = lk > -70
    if not keep.any(): return -70.0
    rel = -0.691 + 10 * np.log10(ms[keep].mean()) - 10
    keep = lk > max(-70, rel)
    return float(-0.691 + 10 * np.log10(ms[keep].mean())) if keep.any() else -70.0


def short_term(x, sr=SR, win=3.0, hop=1.0):
    """short-term loudness (LUFS) every hop seconds"""
    if x.ndim == 1: x = x[:, None]
    y = _kweight(x.astype(np.float64), sr); sq = (y ** 2).sum(axis=1)
    c = np.concatenate([[0], np.cumsum(sq)]); w, h = int(win * 48000), int(hop * 48000)
    out = []
    for s in range(0, max(1, len(sq) - w + 1), h):
        out.append(-0.691 + 10 * np.log10(max((c[s + w] - c[s]) / w, 1e-12)))
    return np.array(out)


# ---------------------------------------------------------------- oscillators and strings
_TABLES = {}


def wavetable(n_harm, shape='saw', size=4096):
    """band-limited single-cycle table (built by additive synthesis, cached)"""
    key = (n_harm, shape)
    if key in _TABLES: return _TABLES[key]
    ph = np.arange(size) / size * 2 * np.pi; tab = np.zeros(size)
    for h in range(1, n_harm + 1):
        if shape == 'saw': a = 1.0 / h ** 1.15                 # a little softer than a true saw: strings, not buzz
        elif shape == 'tri': a = (1.0 / h ** 2) if h % 2 else 0.0
        elif shape == 'odd': a = (1.0 / h ** 1.3) if h % 2 else 0.0   # clarinet / reed colour
        else: a = 1.0 if h == 1 else 0.0
        tab += a * np.sin(h * ph + (0.0 if shape != 'saw' else 0.3 * h))
    tab /= np.abs(tab).max() + 1e-9
    tab = np.concatenate([tab, tab[:2]]).astype(np.float32)
    _TABLES[key] = tab
    return tab


def osc(freq, shape='saw', max_hz=9000, phase0=0.0, sr=SR):
    """oscillator following a per-sample frequency array (Hz); band-limited, linear-interpolated"""
    f = np.asarray(freq, np.float64)
    nh = int(max(1, min(40, max_hz / max(float(f.mean()), 20.0))))
    tab = wavetable(nh, shape); size = len(tab) - 2
    ph = (phase0 + np.cumsum(f / sr)) % 1.0
    idx = ph * size; i0 = idx.astype(np.int64); fr = (idx - i0).astype(np.float32)
    return tab[i0] * (1 - fr) + tab[i0 + 1] * fr


def midi_hz(m):
    return 440.0 * 2 ** ((np.asarray(m, np.float64) - 69) / 12)


def karplus(freq, dur, rng, brightness=0.5, decay=0.9985, pick=0.18, sr=SR):
    """Karplus-Strong plucked string (lute, oud, lyre) as one IIR: a delay loop with a two-tap average (loses highs
    as it rings, like a real string) and an all-pass for exact tuning. brightness 0..1 sets the excitation colour."""
    total = sr / freq
    N = int(np.floor(total - 1.0))                         # 0.5 sample from the averager, ~0.5..1.5 from the all-pass
    d = np.clip(total - 0.5 - N, 0.4, 1.6); c = (1 - d) / (1 + d)
    g = min(float(decay) ** max(1.0, 440.0 / freq), 0.9995)  # low strings ring longer per round trip
    # den(z) = (1 + c z^-1) - g z^-N * 0.5 (1 + z^-1) (c + z^-1)
    den = np.zeros(N + 3); den[0] = 1.0; den[1] = c
    den[N] -= g * 0.5 * c; den[N + 1] -= g * 0.5 * (1 + c); den[N + 2] -= g * 0.5
    n = int(dur * sr)
    L = int(total) + 2
    nz = rng.uniform(-1, 1, L).astype(np.float32)
    nz = lowpass(nz, min(900 + 5200 * brightness, sr * 0.45), 2, sr)
    m = max(1, int(L * pick))
    nz[m:] = nz[m:] - 0.7 * nz[:-m]                        # pick position comb: woody, not a plain noise burst
    exc = np.zeros(n, np.float32); exc[:L] = nz
    y = sg.lfilter([1.0, c], den, exc).astype(np.float32)
    y /= np.abs(y).max() + 1e-9
    return y
