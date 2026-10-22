#!/usr/bin/env python3
"""Sound for the four seasons loop: an exact 12 s loop (no crossfade at the seam), free and deterministic.

    python3 films/cutaway/loops/seasons/audio/make_audio.py        # writes audio/mix.m4a (+ mix.json); mix.wav is a local check

How the loop is exact: every note and sound event starts inside [0, 12) and is rendered on a 36 s buffer with its full
tail and reverb; the buffer is then folded (0-12 + 12-24 + 24-36), which is exactly what you hear when the loop plays
over and over. Noise beds (wind, rustle) are made periodic in the frequency domain. The limiter runs on three copies and
the middle one is kept, so even its gain is periodic.

Score: the free engine films/lib/score (Composer voices: synthesised string pad and a harp-like pluck, its hall reverb),
D major, four chords, one per season: spring D(add9), summer G(add9), autumn Bm, winter A(sus4), back to D at the seam.
Ambience (synthesised here, sounds only for what we see): wind all year (a whistle in winter), leaves rustling in
spring and summer, birds in spring and summer and when they return with the thaw, a few frogs in spring, leaves
dropping onto the pond in autumn, a soft creak of ice in winter. The score sits under the ambience.
"""
import os, sys, json, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(FILM, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'films', 'lib', 'score')); sys.path.insert(0, FILM)
import dsp, voices  # noqa: E402
from score import Composer, peak_ref  # noqa: E402
import szworld as W  # noqa: E402
SR = dsp.SR; LOOP = W.LOOP; N = int(LOOP * SR); T = 3 * N


class Buf:
    def __init__(self): self.x = np.zeros((T, 2), np.float32)
    def add(self, y, t, gain=1.0, pan=0.0):
        if y.ndim == 1: y = np.stack([y, y], 1)
        i = int(round((t % LOOP) * SR)); m = min(len(y), T - i); L, R = dsp.pan_gains(pan)
        self.x[i:i + m, 0] += y[:m, 0] * gain * L * 1.414; self.x[i:i + m, 1] += y[:m, 1] * gain * R * 1.414


def fold(x):
    return x[:N] + x[N:2 * N] + x[2 * N:3 * N]


def pnoise(rng, lo, hi, tilt=1.0, n=N):
    """Noise that repeats exactly every n samples, band-limited to lo..hi Hz with a 1/f^tilt slope. RMS 1."""
    f = np.fft.rfftfreq(n, 1 / SR); f[0] = 1.0
    shape = 1 / (1 + (lo / f) ** 4) / (1 + (f / hi) ** 4) * f ** (-tilt / 2)
    out = np.zeros((n, 2), np.float32)
    for c in range(2):
        sp = (rng.standard_normal(len(f)) + 1j * rng.standard_normal(len(f))) * shape; sp[0] = 0
        y = np.fft.irfft(sp, n); out[:, c] = y / (np.sqrt((y ** 2).mean()) + 1e-12)
    return out


def curve(fn):
    """A control curve over one loop at sample rate (fn evaluated at 200 Hz, then interpolated)."""
    tt = np.arange(0, LOOP + 0.005, 0.005); v = np.array([fn(t) for t in tt])
    return np.interp(np.arange(N) / SR, tt, v).astype(np.float32)


# ------------------------------------------------------------------ score
def make_score(rng):
    plan = {'palette': 'ancient_med', 'key': 'D', 'mode': 'ionian', 'duration': 3 * LOOP, 'seed': 3, 'sections': [{'t': 0, 'mood': 'calm'}]}
    engine = 'auto' if voices.sample_root() else 'synth'
    c = Composer(plan, engine); pad_s = Buf(); pad = Buf(); pl = Buf()

    class _B:                      # the Composer writes into objects with .add(x, t, gain, pan)
        def __init__(self, b): self.b = b
        def add(self, x, t, gain=1.0, pan=0.0): self.b.add(x, t, gain, pan)
    chords = [(0.0, 0, 'add9'), (3.0, 5, 'add9'), (6.0, 9, 'triad'), (9.0, 7, 'sus')]; prev = None; info = []
    for k, (t0, root, ct) in enumerate(chords):
        rpc, pcs = c.chord_pcs(root, ct); v = c.voice_chord(rpc, pcs, prev); prev = v; info.append((t0, root, ct, v))
        ts = t0 - 0.55
        c.add_pad_note(_B(pad_s), _B(pad), 'cello', v[0], ts, 3.9, 1.5, 2.8, 0.50, -4.0, 'bass', rng, c.use_samples)
        for j, m in enumerate(v[1:]):
            c.add_pad_note(_B(pad_s), _B(pad), 'viola' if m < 66 else 'violin', m, ts + 0.15 * j, 3.9, 1.6, 2.8, 0.46, -4.0 - 0.6 * j, 'mid', rng, c.use_samples)
        tones = sorted(m for m in range(60, 82) if m % 12 in pcs)
        start = [0, 1, 2, 1][k]; seq = [tones[min(len(tones) - 1, start + i)] for i in (0, 1, 2, 3, 2)]
        for i, (dt, m) in enumerate(zip((0.30, 0.78, 1.24, 1.72, 2.40), seq)):
            x = c.pluck_note(int(m), 3.2, 0.40 - 0.03 * i, rng, 'harp' if c.use_samples else 'synth:harp')
            pl.add(x, t0 + dt + float(rng.normal(0, 0.012)), 1.0, pan=-0.25 + 0.12 * i)
    body = pad_s.x + pad.x
    body = dsp.lowpass(body, 2300, 2) * dsp.db(-9.0)
    pluck = pl.x * dsp.db(-7.0)
    hall = dsp.make_ir(3.2, np.random.default_rng(101))
    wet = dsp.convolve(body * 0.30 + pluck * 0.42, hall)
    mix = body + pluck * 0.9 + wet * 0.9
    mix = dsp.highpass(mix, 45, 2)
    return fold(mix), info, engine


# ------------------------------------------------------------------ ambience events
def chirp(rng, f0, dur):
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    f = f0 * (1 + 0.45 * u + 0.06 * np.sin(2 * np.pi * rng.uniform(25, 45) * t))
    ph = 2 * np.pi * np.cumsum(f) / SR; y = np.sin(ph) + 0.12 * np.sin(2 * ph)
    return (y * np.sin(np.pi * u) ** 1.5).astype(np.float32)


def bird_song(rng):
    f0 = rng.uniform(2600, 4200); parts = []; t = 0.0; out = np.zeros(int(1.2 * SR), np.float32)
    for k in range(int(rng.integers(2, 6))):
        d = rng.uniform(0.05, 0.12); y = chirp(rng, f0 * rng.uniform(0.9, 1.15), d); i = int(t * SR)
        out[i:i + len(y)] += y[: len(out) - i] * rng.uniform(0.6, 1.0); t += d + rng.uniform(0.04, 0.14)
    return dsp.highpass(out, 1500, 2)


def croak(rng):
    """A frog: two bursts of a buzzy low voice, pulsed about 30 times a second ('rib-bit')."""
    out = []
    for dur, f0 in ((0.13, rng.uniform(190, 230)), (0.09, rng.uniform(240, 280))):
        n = int(dur * SR); t = np.arange(n) / SR
        ph = 2 * np.pi * f0 * t; y = sum(np.sin(h * ph) / h ** 0.6 for h in range(1, 9))
        pulse = (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(26, 34) * t)) ** 3
        out.append(y * pulse * np.sin(np.pi * t / dur) ** 0.7); out.append(np.zeros(int(0.06 * SR)))
    y = np.concatenate(out).astype(np.float32)
    return dsp.bandpass(y, 250, 2400, 2)


def plip(rng):
    n = int(0.09 * SR); t = np.arange(n) / SR; f = rng.uniform(900, 1300) * (1 + 1.2 * t / 0.09)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.018) * np.minimum(1, t / 0.002)
    return y.astype(np.float32)


def creak(rng):
    n = int(0.5 * SR); t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for k in range(int(rng.integers(3, 6))):
        i = int(rng.uniform(0, 0.35) * SR); m = int(rng.uniform(0.02, 0.06) * SR)
        y[i:i + m] += rng.standard_normal(m).astype(np.float32) * np.hanning(m).astype(np.float32)
    y = dsp.bandpass(y, 300, 1400, 2) + dsp.lowpass(y, 160, 2) * 2.0
    return y * np.minimum(1, t / 0.01)


def make_ambience(rng):
    b = Buf(); room = dsp.make_ir(1.2, np.random.default_rng(202), predelay=0.01)
    for _ in range(11):                                                    # birds while they are here
        t = rng.uniform(0.2, 6.0); b.add(bird_song(rng) * dsp.db(rng.uniform(-24, -17)), t, 1.0, rng.uniform(-0.8, 0.8))
    for t in (11.45, 11.8): b.add(bird_song(rng) * dsp.db(-22), t, 1.0, rng.uniform(-0.6, 0.6))
    for t, lv in ((1.95, -18), (2.45, -21), (3.05, -19), (3.9, -23), (4.8, -25)):   # frogs at the surface in spring
        b.add(croak(rng) * dsp.db(lv), t + rng.normal(0, 0.05), 1.0, rng.uniform(-0.5, 0.5))
    for t in np.sort(rng.uniform(7.2, 9.3, 7)): b.add(plip(rng) * dsp.db(rng.uniform(-34, -28)), t, 1.0, rng.uniform(-0.6, 0.6))
    for t in (9.9, 10.35): b.add(creak(rng) * dsp.db(-33), t, 1.0, rng.uniform(-0.4, 0.4))
    wet = dsp.convolve(b.x, room)
    ev = fold(b.x * 0.85 + wet * 0.35)
    # wind all year (strongest in autumn and winter), a whistle in winter, leaves rustling in spring and summer
    gust = curve(lambda t: 0.62 + 0.24 * np.sin(2 * np.pi * 2 * t / LOOP + 0.7) + 0.14 * np.sin(2 * np.pi * 5 * t / LOOP + 2.1))
    wl = curve(lambda t: W.blend(t, (0.42, 0.30, 0.70, 0.85)))
    whl = curve(lambda t: W.blend(t, (0.05, 0.02, 0.30, 1.0)) * (1 - W.cv('wet', t) * 0.3))
    rl = curve(lambda t: W.blend(t, (0.55, 0.75, 0.55, 0.05)))
    wind = pnoise(rng, 70, 700, 1.0) * dsp.db(-25) * (wl * gust)[:, None]
    whistle = pnoise(rng, 900, 2200, 0.5) * dsp.db(-38) * (whl * gust ** 2)[:, None]
    rustle = pnoise(rng, 2500, 9000, 0.0) * dsp.db(-40) * (rl * gust)[:, None]
    return ev + wind + whistle + rustle


def main():
    rng = np.random.default_rng(11)
    score, info, engine = make_score(np.random.default_rng(5))
    amb = make_ambience(rng)
    s_lu = dsp.loudness(np.tile(score, (3, 1))); a_lu = dsp.loudness(np.tile(amb, (3, 1)))
    mix = amb * dsp.db(-21.0 - a_lu) + score * dsp.db(-25.0 - s_lu)          # score about 4 LU under the ambience
    x3 = np.tile(mix, (3, 1)); lu = dsp.loudness(x3); x3 = dsp.limiter(x3 * dsp.db(-18.0 - lu), -2.0)
    y = x3[N:2 * N]
    seam = float(np.abs(y[0] - y[-1]).max()); step = float(np.percentile(np.abs(np.diff(y, axis=0)), 99.9))
    import soundfile as sf
    wav = os.path.join(HERE, 'mix.wav'); sf.write(wav, y, SR, subtype='PCM_24')
    m4a = os.path.join(HERE, 'mix.m4a')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), m4a], check=True)
    meas = {'seconds': len(y) / SR, 'lufs': round(dsp.loudness(np.tile(y, (3, 1))), 2), 'peak_dbfs': round(float(dsp.lin2db(np.abs(y).max())), 2),
            'seam_jump': round(seam, 5), 'p99_9_step': round(step, 5), 'engine': engine,
            'score_lufs_before_mix': round(s_lu, 1), 'ambience_lufs_before_mix': round(a_lu, 1),
            'chords': [(t0, root, ct, v) for t0, root, ct, v in info]}
    json.dump(meas, open(os.path.join(HERE, 'mix.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in meas.items() if k != 'chords'}))


if __name__ == '__main__':
    main()
