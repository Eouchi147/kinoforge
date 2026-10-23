"""Sound kit of the Cutaway showcase series: real recordings only (BigSoundBank CC0, release `sfx-bank` of
Eouchi147/rc-render), no music, no voice, no synthesis. Ideas taken from the Dark Corners mix kit
(rc-render/dark/film/mix_kit.py): beds looped with crossfades, spot sounds placed on the picture's events, levels
in dB, a master to a loudness target with a peak ceiling. numpy, scipy, soundfile and ffmpeg; free and deterministic.

Where the bank is: $SFX_BANK (a folder of <name>.flac), else ~/.cache/kinoforge/sfx-bank; if neither holds it,
the kit downloads sfx-bank.tar (about 1 GB, public release, no key) and unpacks it into the cache.

A film's make_audio.py:
    import audio_kit as K
    m = K.Mix()
    m.bed('forest', start=12, gain=-6, hp=120)            # the place, looped to 20 s
    m.spot('splash_small_1', t=7.4, gain=-12, pan=0.3)    # an event we see
    m.master(HERE)                                        # mix.m4a (20.0 s, 48 kHz stereo AAC 256k) + mix.json
"""
import os, sys, json, subprocess, tarfile, urllib.request
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'films', 'lib', 'score'))
import dsp  # noqa: E402  (filters, room, BS.1770 loudness, limiter)

SR = 48000
DUR = 20.0
N = int(DUR * SR)
URL = 'https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.tar'
CACHE = os.path.expanduser('~/.cache/kinoforge')
_C = {}


def bank_dir():
    d = os.environ.get('SFX_BANK') or os.path.join(CACHE, 'sfx-bank')
    if os.path.isdir(d) and any(f.endswith('.flac') for f in os.listdir(d)):
        return d
    os.makedirs(CACHE, exist_ok=True)
    tar = os.path.join(CACHE, 'sfx-bank.tar')
    if not os.path.exists(tar):
        print('downloading the sound bank (once):', URL)
        urllib.request.urlretrieve(URL, tar + '.part'); os.replace(tar + '.part', tar)
    with tarfile.open(tar) as t:
        t.extractall(CACHE, filter='data')
    return os.path.join(CACHE, 'sfx-bank')


def load(name):
    """A bank recording as float32 (n, 2) at 48 kHz."""
    if name not in _C:
        x, sr = sf.read(os.path.join(bank_dir(), name + '.flac'), dtype='float32', always_2d=True)
        if x.shape[1] == 1: x = np.repeat(x, 2, 1)
        if sr != SR: x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
        _C[name] = x[:, :2]
    return _C[name]


def db(v):
    return 10 ** (v / 20.0)


def envelope(points, n=N):
    """Piecewise-linear gain in dB over time: [(t, dB), (t, dB)] -> per-sample linear gain (n,)."""
    ts = np.array([p[0] for p in points], float); vs = np.array([p[1] for p in points], float)
    return db(np.interp(np.arange(n) / SR, ts, vs)).astype(np.float32)


def shape(x, hp=None, lp=None, speed=1.0, width=1.0):
    """Filter, slow down (speed < 1: lower and longer, as heard through rock or water) and narrow a clip."""
    if speed != 1.0:
        up, down = int(round(1000 / speed)), 1000
        x = resample_poly(x, up, down, axis=0).astype(np.float32)
    if hp: x = dsp.highpass(x, hp, 2)
    if lp: x = dsp.lowpass(x, lp, 2)
    if width != 1.0:
        m = x.mean(1, keepdims=True); x = m + (x - m) * width
    return x.astype(np.float32)


def loop(x, n, xf=0.8):
    """Repeat x to n samples with equal-power crossfades of xf seconds."""
    if len(x) >= n: return x[:n].copy()
    L = int(xf * SR); out = x.copy()
    a = np.sqrt(np.linspace(0, 1, L))[:, None]; b = np.sqrt(np.linspace(1, 0, L))[:, None]
    while len(out) < n:
        out[-L:] = out[-L:] * b + x[:L] * a
        out = np.concatenate([out, x[L:]])
    return out[:n].copy()


def pan(x, p):
    """Equal-power balance of a stereo clip, p in -1..1."""
    l, r = dsp.pan_gains(p)
    return (x * np.array([l, r], np.float32) * 1.414).astype(np.float32)


def fades(x, fi=0.0, fo=0.0):
    x = x.copy()
    if fi > 0:
        k = min(len(x), int(fi * SR)); x[:k] *= (np.sin(np.linspace(0, np.pi / 2, k)) ** 2)[:, None]
    if fo > 0:
        k = min(len(x), int(fo * SR)); x[-k:] *= (np.cos(np.linspace(0, np.pi / 2, k)) ** 2)[:, None]
    return x


def onset(x, thr=0.1):
    """Trim the silence before a one-shot so it lands on its frame."""
    e = np.abs(x).max(1); i = int(np.argmax(e > thr * e.max()))
    return x[max(0, i - int(0.004 * SR)):]


class Mix:
    def __init__(self, seed=1):
        self.bus = np.zeros((N, 2), np.float32)
        self.rng = np.random.default_rng(seed)
        self.used = {}                       # name -> how it is used, for mix.json and SOUND.md

    def _note(self, name, how):
        self.used.setdefault(name, []).append(how)

    def bed(self, name, start=0.0, gain=0.0, env=None, hp=None, lp=None, speed=1.0, width=1.0, p=0.0, t0=0.0, t1=DUR,
            fi=1.0, fo=1.0, xf=0.8):
        """A looped bed from `start` s into the recording, heard t0..t1 (with fades), level `gain` dB, optional dB
        envelope [(t, dB)] over the film (absolute times)."""
        x = load(name); x = x[int(start * SR) % len(x):] if start < len(x) / SR else x
        x = shape(x, hp, lp, speed, width)
        n = int((t1 - t0) * SR)
        y = fades(loop(x, n, xf), fi, fo) * db(gain)
        if p: y = pan(y, p)
        i = int(t0 * SR); m = min(n, N - i)
        seg = y[:m]
        if env is not None: seg = seg * envelope(env)[i:i + m, None]
        self.bus[i:i + m] += seg
        self._note(name, f'bed {t0:.1f}-{t1:.1f} s')
        return self

    def spot(self, name, t, gain=0.0, p=0.0, start=0.0, length=None, hp=None, lp=None, speed=1.0, fi=0.005, fo=0.05,
             trim=True, width=1.0, label='', sweep=None):
        """One recording placed so its onset lands at t (seconds); `length` is the heard length (after any slowing);
        sweep=(p0, p1) moves it across the frame (a bus or a train passing)."""
        x = load(name)[int(start * SR):]
        if length is not None: x = x[:int(length * SR * speed)]
        if trim: x = onset(x)
        x = shape(x, hp, lp, speed, width)
        x = fades(x, fi, fo) * db(gain)
        if p: x = pan(x, p)
        if sweep is not None:
            a = (np.clip(np.linspace(sweep[0], sweep[1], len(x)), -1, 1) + 1) * np.pi / 4
            x = x * np.stack([np.cos(a), np.sin(a)], 1).astype(np.float32) * 1.414
        i = int(round(t * SR))
        if i < 0: x = x[-i:]; i = 0
        m = min(len(x), N - i)
        if m > 0: self.bus[i:i + m] += x[:m]
        self._note(name, f'{label or "spot"} at {t:.2f} s')
        return self

    def room(self, rt60=1.5, wet=0.25, seed=7, predelay=0.02):
        """Send the whole bus through a synthetic room (the cave, the tunnel): wet adds to dry."""
        ir = dsp.make_ir(rt60, np.random.default_rng(seed), predelay=predelay)
        self.bus = self.bus + dsp.convolve(self.bus, ir) * wet
        return self

    def master(self, out_dir, lufs=-18.0, ceiling=-2.0, fi=0.8, fo=1.2, notes=None):
        x = dsp.highpass(self.bus, 28, 2)
        x = x * db(lufs - dsp.loudness(x))
        x = dsp.limiter(x, ceiling)
        x = fades(x, fi, fo)
        x = x * db(lufs - dsp.loudness(x))                  # the fades and limiter moved it a little
        x = dsp.limiter(x, ceiling)
        x = x[:N]
        os.makedirs(out_dir, exist_ok=True)
        wav = os.path.join(out_dir, 'mix.wav'); m4a = os.path.join(out_dir, 'mix.m4a')
        sf.write(wav, x, SR, subtype='PCM_24')
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'aac', '-b:a', '256k',
                        '-ar', str(SR), '-ac', '2', '-movflags', '+faststart', m4a], check=True)
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', m4a],
                                   capture_output=True, text=True).stdout.strip())
        y, _ = sf.read(wav, dtype='float32')
        dec = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', m4a, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                             capture_output=True, check=True).stdout
        z = np.frombuffer(dec, np.float32).reshape(-1, 2)
        meas = {'seconds_wav': len(y) / SR, 'seconds_m4a': round(dur, 3), 'lufs': round(dsp.loudness(y), 2),
                'peak_dbfs': round(float(dsp.lin2db(np.abs(y).max())), 2),
                'm4a_decoded_lufs': round(dsp.loudness(z), 2), 'm4a_decoded_peak_dbfs': round(float(dsp.lin2db(np.abs(z).max())), 2),
                'sample_rate': SR, 'codec': 'aac 256k stereo',
                'fade_in_s': fi, 'fade_out_s': fo, 'sources': {k: v for k, v in sorted(self.used.items())},
                'licence': 'all CC0 (BigSoundBank), see films/cutaway/series/SOUND.md'}
        if notes: meas['notes'] = notes
        json.dump(meas, open(os.path.join(out_dir, 'mix.json'), 'w'), indent=1)
        print(json.dumps({k: v for k, v in meas.items() if k not in ('sources',)}))
        return meas
