"""KINOFORGE procedural sound kit — synthesised drones, risers, hits, ambiences, tones and a cue-sheet mixer.
No samples needed. 48 kHz float32 mono/stereo numpy. Deterministic (seeded).

    from sfx import *
    m = Mix(duration=10.0)
    m.put(drone(10, f0=55, detune=0.3, lp=400), at=0, db=-18, fade_in=2, fade_out=2)
    m.put(riser(3.0, 200, 2400), at=5.5, db=-14)
    m.put(hit(2.5, sub=45), at=8.5, db=-6)
    m.put(silence_marker(), at=8.0)       # purely documentary
    m.write('audio.wav')                  # normalises to ~-1 dBTP, mixes to stereo

Design rules baked in (R-3-06 / R-9-11): leave a real silence before the biggest hit; hits land on picture cuts;
no loop repeats; everything has a tail.
"""
import numpy as np
from scipy import signal
import soundfile as sf

SR = 48000
_rng = np.random.default_rng(7)

def seed(s):
    global _rng; _rng = np.random.default_rng(s)

def t_axis(dur): return np.arange(int(dur * SR)) / SR
def db(x): return 10 ** (x / 20)
def env_adsr(n, a=0.01, d=0.1, s=0.8, r=0.3):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR); s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([np.linspace(0, 1, a_n, endpoint=False), np.linspace(1, s, d_n, endpoint=False), np.full(s_n, s), np.linspace(s, 0, r_n)])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))
def fade(x, fin=0.0, fout=0.0):
    x = x.copy(); n = len(x); i, o = int(fin * SR), int(fout * SR)
    if i > 0: x[:i] *= np.linspace(0, 1, i) ** 2
    if o > 0: x[-o:] *= np.linspace(1, 0, o) ** 2
    return x
def lowpass(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR / 2 - 100) / (SR / 2)); return signal.lfilter(b, a, x)
def highpass(x, fc, order=2):
    b, a = signal.butter(order, max(fc, 10) / (SR / 2), btype='high'); return signal.lfilter(b, a, x)
def bandpass(x, lo, hi, order=2):
    b, a = signal.butter(order, [max(lo, 10) / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], btype='band'); return signal.lfilter(b, a, x)
def saturate(x, drive=2.0): return np.tanh(x * drive) / np.tanh(drive)
def noise(dur, kind='white'):
    n = int(dur * SR); w = _rng.standard_normal(n).astype(np.float32)
    if kind == 'pink':  # Voss-ish via filter
        b, a = signal.butter(1, 200 / (SR / 2)); w = signal.lfilter(b, a, w) * 6
    if kind == 'brown': w = np.cumsum(w) / 200; w -= np.linspace(w[0], w[-1], n)
    return w
def reverb(x, size=0.6, decay=2.5, mix=0.3, predelay=0.02):
    """Cheap Schroeder-style reverb (4 combs + 2 allpass). size 0..1, decay seconds."""
    n = len(x); out = np.zeros(n + int(decay * SR) + int(predelay * SR), dtype=np.float32); out[int(predelay * SR):int(predelay * SR) + n] += x
    wet = np.zeros_like(out)
    for i, d in enumerate([0.0297, 0.0371, 0.0411, 0.0437]):
        dl = int(d * (0.5 + size) * SR); g = 10 ** (-3 * dl / SR / decay); buf = np.zeros_like(out)
        for k in range(dl, len(out)): buf[k] = out[k] + g * buf[k - dl]
        wet += buf * 0.25
    for d in [0.005, 0.0017]:
        dl = int(d * SR); g = 0.7; y = np.zeros_like(wet)
        for k in range(dl, len(wet)): y[k] = -g * wet[k] + wet[k - dl] + g * y[k - dl]
        wet = y
    return out * (1 - mix) + wet * mix

# ------------------------------------------------------------------ generators (all return float32 arrays)
def drone(dur, f0=55.0, detune=0.4, lp=500.0, voices=5, motion=0.05, shape='saw'):
    """Dark cinematic drone: detuned stack with slow filter motion."""
    t = t_axis(dur); out = np.zeros_like(t)
    for v in range(voices):
        f = f0 * (1 + detune / 100 * (v - voices / 2)) * (1 if v % 2 == 0 else 1.005)
        ph = 2 * np.pi * f * t + 2 * np.pi * _rng.random()
        w = signal.sawtooth(ph) if shape == 'saw' else np.sin(ph) + 0.3 * np.sin(2 * ph)
        out += w / voices
    out = lowpass(out, float(lp))
    lfo = 1 + motion * np.sin(2 * np.pi * 0.05 * t); out = out * lfo
    return fade(out.astype(np.float32), 0.5, 0.5)
def pad(dur, freqs=(110, 164.8, 220), lp=1200, vib=0.15):
    t = t_axis(dur); out = np.zeros_like(t)
    for f in freqs:
        for k, g in [(1, 1), (2, 0.4), (3, 0.2)]:
            out += g * np.sin(2 * np.pi * f * k * t + vib * np.sin(2 * np.pi * 0.3 * t + _rng.random() * 6)) / (len(freqs) * 1.6)
    return fade(lowpass(out, lp), 1.0, 1.0).astype(np.float32)
def riser(dur, f_start=150, f_end=3000, noise_mix=0.5, curve=2.0):
    """Tension riser: pitch sweep + filtered noise, swelling. Ends at its peak (land a hit there)."""
    t = t_axis(dur); u = (t / dur) ** curve
    f = f_start * (f_end / f_start) ** u; ph = 2 * np.pi * np.cumsum(f) / SR
    tone = signal.sawtooth(ph) * 0.5 + np.sin(ph * 0.5) * 0.5
    nz = bandpass(noise(dur), 200, 6000) * 0.5
    sw = u ** 1.5
    out = (tone * (1 - noise_mix) + nz * noise_mix) * sw
    return fade(out, 0.2, 0.01).astype(np.float32)
def shepard(dur, base=55, octaves=6, rate=0.12):
    """Endless-rise Shepard tone for dread (R-6-07)."""
    t = t_axis(dur); out = np.zeros_like(t)
    for i in range(octaves):
        phase = (i / octaves + rate * t) % 1.0; f = base * 2 ** (phase * octaves)
        amp = np.sin(np.pi * phase) ** 2; ph = 2 * np.pi * np.cumsum(f) / SR; out += amp * np.sin(ph) / octaves
    return fade(lowpass(out, 2500), 0.5, 0.5).astype(np.float32)
def hit(dur=2.5, sub=45.0, click=True, tail=True, crunch=0.6):
    """Trailer hit: sub thump + noise crack + tail."""
    t = t_axis(dur)
    pitch = sub * (1 + 3 * np.exp(-t * 18)); ph = 2 * np.pi * np.cumsum(pitch) / SR
    s = np.sin(ph) * np.exp(-t * 2.2)
    nz = lowpass(noise(dur), 1800) * np.exp(-t * 14) * crunch
    out = s + nz
    if click: out += highpass(noise(dur), 2000) * np.exp(-t * 120) * 0.6
    out = saturate(out, 1.8)
    if tail: out = reverb(out, size=0.9, decay=2.0, mix=0.35)[:len(t)]
    return out.astype(np.float32)
def braam(dur=3.0, f0=41.2):
    """Brass-like blast (use ≤2 per piece, R-6-07)."""
    t = t_axis(dur); out = np.zeros_like(t)
    for k, g in [(1, 1), (2, 0.6), (3, 0.35), (4, 0.2), (5, 0.1)]:
        out += g * signal.sawtooth(2 * np.pi * f0 * k * t * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)))
    e = env_adsr(len(t), 0.05, 0.4, 0.5, 1.5); out = lowpass(out * e, 900 + 2500 * np.exp(-t * 3)) if False else lowpass(out * e, 1800)
    return saturate(reverb(out, 0.8, 2.5, 0.3)[:len(t)], 1.5).astype(np.float32)
def sub_drop(dur=2.0, f_start=70, f_end=30):
    t = t_axis(dur); f = f_start * (f_end / f_start) ** (t / dur); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 1.2)).astype(np.float32)
def whoosh(dur=0.8, lo=300, hi=4000, direction=1):
    t = t_axis(dur); u = t / dur; u = u if direction > 0 else 1 - u
    nz = noise(dur); env = np.sin(np.pi * u) ** 2
    out = np.zeros_like(nz);
    # moving band-pass by chunks
    N = 16; step = len(nz) // N
    for i in range(N):
        fc = lo * (hi / lo) ** (i / (N - 1)); seg = nz[i * step:(i + 1) * step]
        out[i * step:(i + 1) * step] = bandpass(np.concatenate([nz[max(0, i * step - 2000):i * step], seg]), fc / 1.6, fc * 1.6)[-len(seg):]
    return fade(out * env, 0.01, 0.05).astype(np.float32)
def wind(dur, strength=0.5, gust=0.3):
    t = t_axis(dur); g = 1 + gust * (0.6 * np.sin(2 * np.pi * 0.09 * t) + 0.4 * np.sin(2 * np.pi * 0.23 * t + 1))
    return fade(lowpass(noise(dur, 'pink'), 600 + 900 * strength) * g * strength, 1.0, 1.0).astype(np.float32)
def rain(dur, intensity=0.6):
    base = highpass(lowpass(noise(dur), 9000), 800) * 0.25 * intensity
    n = int(dur * SR); drops = np.zeros(n, dtype=np.float32); k = int(dur * 60 * intensity)
    idx = _rng.integers(0, n - 200, k)
    for i in idx: drops[i:i + 120] += np.sin(np.linspace(0, np.pi, 120)) * _rng.random() * 0.4
    return fade(base + bandpass(drops, 1500, 7000) * 0.4, 0.5, 0.5).astype(np.float32)
def hum(dur, f=60.0, level=0.3):
    t = t_axis(dur); return fade((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3 * f * t)) * level, 0.2, 0.2).astype(np.float32)
def tape_hiss(dur, level=0.15): return fade(highpass(noise(dur), 3000) * level, 0.1, 0.1).astype(np.float32)
def crackle(dur, density=30.0, level=0.5):
    n = int(dur * SR); out = np.zeros(n, dtype=np.float32); k = int(dur * density)
    for i in _rng.integers(0, n - 400, k):
        L = _rng.integers(20, 300); out[i:i + L] += (_rng.standard_normal(L) * np.exp(-np.linspace(0, 6, L))) * _rng.random() * level
    return bandpass(out, 300, 8000).astype(np.float32)
def fire(dur, level=0.5): return (lowpass(noise(dur, 'brown'), 300) * 2.0 * level + crackle(dur, 25, 0.4 * level)).astype(np.float32)
def heartbeat(dur, bpm=60, level=0.8):
    n = int(dur * SR); out = np.zeros(n, dtype=np.float32); period = 60 / bpm; t = t_axis(0.25)
    beat = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 20); beat2 = np.sin(2 * np.pi * 48 * t) * np.exp(-t * 24) * 0.7
    k = 0.0
    while k < dur - 0.4:
        i = int(k * SR); out[i:i + len(beat)] += beat; j = int((k + period * 0.3) * SR); out[j:j + len(beat2)] += beat2; k += period
    return (out * level).astype(np.float32)
def tick(dur, bpm=120, level=0.4, f=3000):
    n = int(dur * SR); out = np.zeros(n, dtype=np.float32); t = t_axis(0.03); tk = np.sin(2 * np.pi * f * t) * np.exp(-t * 300)
    k = 0.0
    while k < dur - 0.05: i = int(k * SR); out[i:i + len(tk)] += tk; k += 60 / bpm
    return (out * level).astype(np.float32)
def tone(freq, dur, wave='sine', a=0.01, d=0.1, s=0.7, r=0.3):
    t = t_axis(dur); ph = 2 * np.pi * freq * t
    w = {'sine': np.sin(ph), 'tri': signal.sawtooth(ph, 0.5), 'saw': signal.sawtooth(ph), 'square': signal.square(ph)}[wave]
    return (w * env_adsr(len(t), a, d, s, r)).astype(np.float32)
def pluck(freq, dur=2.0, bright=0.5):
    """Karplus-Strong string (piano/harp-ish)."""
    n = int(dur * SR); N = int(SR / freq); buf = _rng.uniform(-1, 1, N).astype(np.float32); buf = lowpass(buf, 2000 + 6000 * bright)
    out = np.zeros(n, dtype=np.float32);
    for i in range(n):
        out[i] = buf[i % N]; buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N]) * 0.996
    return (out * np.exp(-t_axis(dur) * 0.8)).astype(np.float32)
def piano(freq, dur=3.0):
    """Felt-piano-ish: inharmonic partials with fast decay."""
    t = t_axis(dur); out = np.zeros_like(t)
    for k, g in [(1, 1), (2, 0.5), (3, 0.25), (4, 0.12), (5, 0.06)]:
        out += g * np.sin(2 * np.pi * freq * k * (1 + 0.0006 * k * k) * t) * np.exp(-t * (1.2 + k * 0.9))
    out += highpass(noise(dur), 2000) * np.exp(-t * 80) * 0.05
    return lowpass(out * 0.4, 5000).astype(np.float32)
def choir(dur, freqs=(130.8, 196, 261.6), breath=0.3):
    t = t_axis(dur); out = np.zeros_like(t)
    for f in freqs:
        v = np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 5.2 * t)) + 0.4 * np.sin(2 * np.pi * 2 * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t)
        out += bandpass(v, 200, 2500) / len(freqs)
    out += bandpass(noise(dur), 1500, 4000) * breath * 0.3
    return fade(out, 1.5, 1.5).astype(np.float32)
NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def note(name, octave=4): return NOTE[name] * 2 ** (octave - 4)

# ------------------------------------------------------------------ mixer
class Mix:
    def __init__(self, duration, sr=SR):
        self.sr = sr; self.n = int(duration * sr); self.L = np.zeros(self.n, dtype=np.float32); self.R = np.zeros(self.n, dtype=np.float32); self.cues = []
    def put(self, x, at=0.0, db_=None, db=0.0, pan=0.0, fade_in=0.0, fade_out=0.0, name=''):
        """Place a mono signal at time `at` (s). pan -1..1. Trims to the mix length."""
        g = 10 ** ((db if db_ is None else db_) / 20); x = fade(np.asarray(x, dtype=np.float32), fade_in, fade_out) * g
        i = int(at * self.sr); j = min(self.n, i + len(x)); x = x[:max(0, j - i)]
        if len(x) == 0: return self
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.L[i:j] += x * l; self.R[i:j] += x * r; self.cues.append((at, name or 'cue', len(x) / self.sr)); return self
    def duck(self, start, end, depth_db=-12, ramp=0.15):
        """Pull the whole mix down between start and end (e.g. under dialogue or for a pre-hit silence)."""
        g = np.ones(self.n, dtype=np.float32); i, j = int(start * self.sr), int(end * self.sr); k = int(ramp * self.sr); d = 10 ** (depth_db / 20)
        g[i:j] = d; g[max(0, i - k):i] = np.linspace(1, d, min(k, i)); g[j:j + k] = np.linspace(d, 1, min(k, self.n - j))
        self.L *= g; self.R *= g; return self
    def write(self, path, peak_db=-1.0, target_rms_db=-18.0):
        st = np.stack([self.L, self.R], axis=1)
        rms = np.sqrt(np.mean(st ** 2) + 1e-12); st *= 10 ** (target_rms_db / 20) / rms
        pk = np.max(np.abs(st)) + 1e-9; lim = 10 ** (peak_db / 20)
        if pk > lim: st = np.tanh(st / lim * 0.9) * lim  # soft limit
        sf.write(path, st.astype(np.float32), self.sr, subtype='PCM_24'); return path
def silence_marker(): return np.zeros(1, dtype=np.float32)
