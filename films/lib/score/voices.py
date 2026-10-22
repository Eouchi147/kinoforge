"""voices.py: the instruments of the score engine.

Two families, same interface (each returns a float32 stereo array for one note or hit):
  * sampled: real recordings from VSCO-2 CE (CC0: strings, harp, flute, clarinet, bassoon, solo violin) found in a
    sample folder (see README.md); re-pitched a few semitones at most, sustained with equal-power cross-fades of
    different takes, so no loop point is ever audible;
  * synthesised: warm wavetable strings, breathy flute/ney, reed, bowed fiddle, Karplus-Strong lute/oud/lyre,
    synthesised hand drums. These need no files at all and are also the fallback for any missing sample.
"""
import os, re, glob, functools
import numpy as np
import soundfile as sf
from fractions import Fraction
from scipy.signal import resample_poly
import dsp
from dsp import SR, db

# ---------------------------------------------------------------- sample library
_PAT = re.compile(r'(?<![A-Za-z])([A-G](?:#|b)?)(-?\d)(?![\d])')
_NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
         'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def sample_root():
    """where the VSCO-2 CE samples live: $SCORE_SAMPLES, then ./samples/vsco next to this package, then known places"""
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.environ.get('SCORE_SAMPLES'), os.path.join(here, 'samples', 'vsco'), os.path.join(here, '..', '..', '..', '.cache', 'vsco'),
              '/home/claude/vp/lib/vsco', os.path.expanduser('~/vsco')):
        if p and os.path.isdir(os.path.join(p, 'Strings')): return os.path.abspath(p)
    return None


def _midi(name):
    m = _PAT.findall(os.path.basename(name).replace('.wav', ''))
    return None if not m else 12 * (int(m[0][1]) + 1) + _NOTE[m[0][0]]


@functools.lru_cache(maxsize=None)
def _load(path):
    x, sr = sf.read(path, dtype='float32', always_2d=True)
    x = np.repeat(x, 2, axis=1) if x.shape[1] == 1 else x[:, :2]
    if sr != SR: x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
    env = np.abs(x).max(axis=1); on = int(np.argmax(env > env.max() * 0.02))
    return x[max(0, on - SR // 250):]


def _yin(x, sr=SR, fmin=40, fmax=2000):
    x = x.mean(axis=1); a = int(0.3 * sr); seg = x[a:a + sr // 2] if len(x) > a + sr // 2 + 4096 else x[:sr // 2]
    seg = seg - seg.mean(); W = len(seg) // 2; tmin, tmax = int(sr / fmax), min(int(sr / fmin), W - 1)
    # difference function by FFT (fast)
    n = len(seg); f = np.fft.rfft(seg, 2 * n); ac = np.fft.irfft(f * np.conj(f))[:W + tmax + 1]
    cs = np.concatenate([[0], np.cumsum(seg ** 2)])
    d = np.array([cs[W] + (cs[t + W] - cs[t]) - 2 * ac[t] for t in range(tmax + 1)])
    c = d.copy(); c[0] = 1; c[1:] = d[1:] * np.arange(1, tmax + 1) / np.maximum(np.cumsum(d[1:]), 1e-12)
    cand = np.where(c[tmin:] < 0.15)[0]
    t = (cand[0] + tmin) if len(cand) else (np.argmin(c[tmin:]) + tmin)
    return sr / t


class Sampled:
    """one instrument from a sample folder (or several: velocity layers are all collected)"""

    def __init__(self, folders, name, target_db=-24.0, max_shift=3.2):
        root = sample_root(); self.items = []; self.name = name; self.target = target_db; self.max_shift = max_shift
        self.ok = False
        if not root: return
        files = []
        for f in folders: files += sorted(glob.glob(os.path.join(root, f, '*.wav')))
        items = [(_midi(f), f) for f in files]; items = [(m, f) for m, f in items if m is not None]
        if not items: return
        mids = sorted(items); probe = mids[len(mids) // 2]                    # verify the octave label against the audio
        try:
            m = 69 + 12 * np.log2(_yin(_load(probe[1])) / 440); shift = int(round((m - probe[0]) / 12)) * 12
        except Exception:
            shift = 0
        self.items = [(m + shift, f) for m, f in items]; self.ok = True
        self.lo = min(m for m, _ in self.items); self.hi = max(m for m, _ in self.items)
        self._gain = {}

    def has(self, midi):
        return self.ok and self.lo - self.max_shift <= midi <= self.hi + self.max_shift

    def _pick(self, midi, rng):
        best = min(abs(m - midi) for m, _ in self.items)
        near = [it for it in self.items if abs(it[0] - midi) == best]
        return near[int(rng.integers(len(near)))]

    def _norm(self, f):
        if f not in self._gain:
            x = _load(f); a = int(0.5 * SR); seg = x[a:a + 3 * SR] if len(x) > a + SR else x
            self._gain[f] = db(self.target) / (np.sqrt((seg ** 2).mean()) + 1e-9)
        return self._gain[f]

    def _shifted(self, f, semis):
        return _repitch(f, int(round(semis * 100)))

    def note(self, midi, dur, rng, vel=0.6, attack=0.05, release=0.5, xfade=1.6, pluck=False):
        """a note of `dur` seconds (plus release). Long notes chain takes (different files where possible) with
        equal-power cross-fades; plucked samples simply ring out."""
        m, f = self._pick(midi, rng)
        x = self._shifted(f, midi - m)
        need = int((dur + release) * SR)
        if len(x) < need and not pluck:
            # chain takes: each is used up to just before its recorded tail (the natural release would dip the level)
            trim = int(1.5 * SR); xf = int(xfade * SR)
            out = (x * self._norm(f))[:max(len(x) - trim, len(x) // 2)]
            guard = 0
            while len(out) < need and guard < 40:
                guard += 1
                m2, f2 = self._pick(midi, rng); y = self._shifted(f2, midi - m2) * self._norm(f2)
                skip = int(0.35 * SR) if len(y) > 2 * SR else 0
                last = len(out) + len(y) - skip - trim >= need
                y = y[skip:] if last else y[skip:max(len(y) - trim, skip + len(y) // 2)]
                k = min(xf, len(out) // 3, len(y) // 3)
                a = np.cos(np.linspace(0, np.pi / 2, k))[:, None]; b = np.sin(np.linspace(0, np.pi / 2, k))[:, None]
                out = np.concatenate([out[:-k], out[-k:] * a + y[:k] * b, y[k:]])
            x = out
        else:
            x = x * self._norm(f)
        x = x[:need].copy()
        x *= dsp.env_ar(len(x), attack, release)[:, None]
        return x * (0.25 + 0.75 * vel) * 1.0


@functools.lru_cache(maxsize=512)
def _repitch(path, cents):
    x = _load(path)
    if cents == 0: return x
    r = Fraction(2 ** (-cents / 1200.0)).limit_denominator(600)
    return resample_poly(x, r.numerator, r.denominator, axis=0).astype(np.float32)


# ---------------------------------------------------------------- synthesised voices
def synth_pad_note(midi, dur, rng, attack=2.5, release=3.5, shape='saw', voices=5, bright=1.0, vel=0.6):
    """warm string-like pad note: several detuned, slowly drifting band-limited oscillators, spread across the stereo
    field, with a soft sub-octave. Brightness is set on the bus afterwards, so the note itself stays dark."""
    n = int((dur + release) * SR); f0 = float(dsp.midi_hz(midi)); out = np.zeros((n, 2), np.float32)
    for v in range(voices):
        det = (v - (voices - 1) / 2) * 5.5 + rng.uniform(-2, 2)               # cents
        drift = dsp.smooth_noise(n, 0.35, rng) * 3.5                           # slow pitch wander
        vib = np.sin(2 * np.pi * rng.uniform(4.6, 5.4) * np.arange(n) / SR + rng.uniform(0, 6)) * 1.8 * np.minimum(1, np.arange(n) / (SR * 3.0))
        f = f0 * 2 ** ((det + drift + vib) / 1200)
        y = dsp.osc(f, shape, max_hz=7000, phase0=rng.random()) * (1.0 / np.sqrt(voices))
        L, R = dsp.pan_gains((v - (voices - 1) / 2) / max(1, voices - 1) * 1.7)
        out[:, 0] += y * L * 1.4; out[:, 1] += y * R * 1.4
    if midi >= 40:
        sub = dsp.osc(np.full(n, f0 / 2), 'sine') * 0.22; out += sub[:, None]
    amp = dsp.env_ar(n, attack, release, curve=1.6)
    breath = 1 + 0.06 * dsp.smooth_noise(n, 0.25, rng)                         # slow swells inside the note
    return out * (amp * breath)[:, None] * (0.25 + 0.75 * vel)


def synth_bass_note(midi, dur, rng, attack=1.8, release=3.0, vel=0.6):
    n = int((dur + release) * SR); f0 = float(dsp.midi_hz(midi))
    drift = dsp.smooth_noise(n, 0.3, rng) * 2.0; f = f0 * 2 ** (drift / 1200)
    y = dsp.osc(f, 'tri', max_hz=1500) * 0.7 + dsp.osc(f, 'sine') * 0.5 + dsp.osc(f * 2, 'sine') * 0.12
    y = y * dsp.env_ar(n, attack, release, curve=1.4) * (0.25 + 0.75 * vel)
    return np.stack([y, y], 1).astype(np.float32)


def synth_wind_note(midi, dur, rng, kind='flute', vel=0.6, attack=0.12, release=0.6, glide=0.0, vibrato=0.35):
    """breathy flute / ney (kind='flute'), reedy clarinet-like (kind='reed'), bowed fiddle (kind='bowed').
    Pitch starts a touch flat and settles (a real player's attack), vibrato starts late, breath noise rides the note."""
    n = int((dur + release) * SR); t = np.arange(n) / SR; f0 = float(dsp.midi_hz(midi))
    vd = vibrato * np.minimum(1, np.maximum(0, t - 0.35) / 0.8) * (1 + 0.25 * dsp.smooth_noise(n, 1.0, rng))
    vr = rng.uniform(4.6, 5.6) if kind != 'bowed' else rng.uniform(5.2, 6.0)
    cents = vd * 22 * np.sin(2 * np.pi * vr * t + rng.uniform(0, 6)) + dsp.smooth_noise(n, 0.7, rng) * 3
    cents += -28 * np.exp(-t / 0.07)                                          # settle in from slightly flat
    if glide: cents += -glide * 100 * np.exp(-t / 0.18)                       # scoop up into the note
    f = f0 * 2 ** (cents / 1200)
    if kind == 'flute':
        y = osc_sum(f, [1.0, 0.30, 0.10, 0.04, 0.02]); y *= 1 + 0.25 * np.sin(2 * np.pi * vr * t) * vd * 0.4
        nz = dsp.bandpass(rng.standard_normal(n).astype(np.float32), 1800, 5200, 2) * (0.020 + 0.018 * (1 - vel))
        nz *= (0.6 + 0.4 * np.exp(-t / 0.4)); y = y + nz * 2.0
        y = dsp.lowpass(y, 5200 if midi < 80 else 7000, 2)
    elif kind == 'reed':
        y = dsp.osc(f, 'odd', max_hz=4500); y = dsp.lowpass(y, 1900 + 1600 * vel, 2) + dsp.bandpass(rng.standard_normal(n).astype(np.float32), 1500, 3500, 1) * 0.01
    else:
        y = dsp.osc(f, 'saw', max_hz=5000); y = dsp.lowpass(y, 1500 + 1500 * vel, 2) * (1 + 0.1 * np.sin(2 * np.pi * 0.3 * t))
        y = y + dsp.bandpass(rng.standard_normal(n).astype(np.float32), 2200, 5000, 1) * 0.012 * np.exp(-t / 0.5)
    y = y * dsp.env_ar(n, attack, release, curve=1.3) * (0.25 + 0.75 * vel) * 0.55
    return np.stack([y, y], 1).astype(np.float32)


def osc_sum(f, amps):
    ph = np.cumsum(np.asarray(f, np.float64) / SR) * 2 * np.pi; y = np.zeros(len(ph), np.float32)
    for h, a in enumerate(amps, 1):
        y += (a * np.sin(h * ph)).astype(np.float32)
    return y


def synth_pluck(midi, dur, rng, kind='lute', vel=0.6):
    """lute / oud / lyre by Karplus-Strong; oud is darker and rounder, lyre brighter and shorter"""
    f = float(dsp.midi_hz(midi))
    br = {'lute': 0.45, 'oud': 0.3, 'lyre': 0.62, 'harp': 0.5}.get(kind, 0.45) * (0.6 + 0.6 * vel)
    dec = {'lute': 0.9988, 'oud': 0.9984, 'lyre': 0.9978, 'harp': 0.9992}.get(kind, 0.9988)
    y = dsp.karplus(f, dur, rng, brightness=br, decay=dec, pick={'oud': 0.22, 'lyre': 0.12}.get(kind, 0.17))
    y = dsp.highpass(y, 70, 1)
    y *= dsp.env_ar(len(y), 0.004, min(0.8, dur * 0.4), curve=1.0) * (0.25 + 0.75 * vel) * 0.9
    return np.stack([y, y], 1).astype(np.float32)


# ---------------------------------------------------------------- hand drums
def _decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR)).astype(np.float32)


def drum(kind, rng, vel=0.6, pitch=1.0):
    """soft hand drums. 'doum' deep hand hit, 'tek' edge tap, 'tabor' dry medium drum, 'tom' round low drum,
    'boom' deep soft hit for the turn, 'brush' muted snare tap. Every hit has a 3 to 8 ms rounded attack: no clicks."""
    if kind == 'doum': n = int(0.9 * SR); f_end, f_start, tau, body = 78 * pitch, 135 * pitch, 0.20, 1.0
    elif kind == 'tom': n = int(1.1 * SR); f_end, f_start, tau, body = 98 * pitch, 160 * pitch, 0.26, 1.0
    elif kind == 'tabor': n = int(0.5 * SR); f_end, f_start, tau, body = 150 * pitch, 230 * pitch, 0.10, 0.9
    elif kind == 'boom': n = int(3.2 * SR); f_end, f_start, tau, body = 44 * pitch, 95 * pitch, 0.9, 1.2
    elif kind == 'tek': n = int(0.25 * SR); f_end, f_start, tau, body = 330 * pitch, 390 * pitch, 0.045, 0.35
    else: n = int(0.3 * SR); f_end, f_start, tau, body = 190 * pitch, 240 * pitch, 0.05, 0.3
    t = np.arange(n) / SR
    f = f_end + (f_start - f_end) * np.exp(-t / 0.045)
    ph = np.cumsum(f) / SR * 2 * np.pi
    y = np.sin(ph) * _decay(n, tau) * body
    y += 0.25 * np.sin(2 * ph * 1.58) * _decay(n, tau * 0.5) * body             # membrane overtone
    nz = rng.standard_normal(n).astype(np.float32)
    if kind in ('tek', 'brush'):
        y += dsp.bandpass(nz, 1100, 3600, 2) * _decay(n, 0.03 if kind == 'tek' else 0.07) * (0.5 if kind == 'tek' else 0.7)
    else:
        y += dsp.bandpass(nz, 220, 1400, 2) * _decay(n, 0.025) * 0.35            # the palm slap
    if kind == 'boom': y += dsp.lowpass(nz, 220, 2) * _decay(n, 0.12) * 0.25
    y *= dsp.env_ar(n, 0.004 if kind != 'boom' else 0.009, 0.05, curve=1.0)
    y = dsp.highpass(y, 32, 1) * (0.2 + 0.8 * vel)
    return np.stack([y, y], 1).astype(np.float32)


def air_swell(dur, rng, f_lo=250.0, f_hi=3200.0, tail=0.0):
    """breathy filtered-noise riser used under a swell: opens slowly, no hiss (band-limited, rounded)"""
    n = int((dur + tail) * SR); nz = rng.standard_normal((n, 2)).astype(np.float32)
    out = np.zeros_like(nz)
    k = 6
    edges = np.geomspace(f_lo, f_hi, k + 1)
    t = np.arange(n) / SR
    for i in range(k):
        band = dsp.bandpass(nz, edges[i], edges[i + 1] * 1.05, 2, axis=0)
        c = (i + 0.5) / k                                                      # which band is open, as time goes on
        g = np.clip((t / dur) * (k + 1) - i, 0, 1) ** 1.2                       # band i opens later in the swell
        out += band * (g * (1 - 0.35 * c))[:, None]
    env = np.where(t < dur, (t / dur) ** 2.2, np.exp(-(t - dur) / 0.8)) if tail else (t / dur) ** 2.2
    return (out * env[:, None] * 0.55).astype(np.float32)
