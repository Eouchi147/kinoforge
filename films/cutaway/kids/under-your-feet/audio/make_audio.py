#!/usr/bin/env python3
"""Sound of Little Big Questions, film "Who lives under your feet?" (under-your-feet): a REAL orchestral recording and REAL
recorded sound effects (74.0 s).

    python3 films/cutaway/kids/under-your-feet/audio/make_audio.py     # writes audio/mix.m4a, audio/mix.json and ../SOUND.md

What it makes (deterministic):
  MUSIC   Mozart, The Marriage of Figaro, overture (Czech National Symphony Orchestra, Musopen; the Wikimedia Commons file
          page records CC0 1.0), cut as beats.json says: recording 0:00 to 0:27.6 (film 0 to 27.6), a linear 1.5 s cross-fade
          (film 26.1 to 27.6) into recording 3:15.0 on, played straight to the piece's own final cadence (film 68.05) and its
          decay. A slow, smooth level rider (no pumping) evens the hushed start against the tuttis; it never reshapes the notes.
  EFFECTS real CC0 recordings (the studio bank, BigSoundBank) placed on the picture's events. Event times are READ from
          blender.py (the T(**seconds) calls) and beats.json at build time. Soft attacks everywhere, nothing sudden or scary.
  TONAL   the pitched sounds (chimes, boings, bowl, glock) are tuned by resampling to the pitch classes the orchestra plays
          at that moment (read from the recording), so they ring with it.
  MASTER  about -16 LUFS integrated, true peak under -1.5 dBTP (measured on the decoded AAC), 48 kHz stereo AAC 256k.

Needs: numpy, scipy, soundfile, ffmpeg and the bank (audio_kit finds or downloads it). The recording of the music:
$MUSIC_FILE, else ~/.cache/kinoforge/music/mozart-figaro-overture.ogg, else the public release `music` of rc-render.
"""
import ast
import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(FILM, '..', '..', '..', '..'))
SERIES = os.path.join(ROOT, 'films', 'cutaway', 'series')
os.environ['KF_SOUND_DUR'] = '74.0'                      # before audio_kit is imported
sys.path.insert(0, SERIES)
sys.path.insert(0, FILM)
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy.ndimage import gaussian_filter1d  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
import audio_kit as K  # noqa: E402
import szworld as W  # noqa: E402   (pure numpy: the clock of beats and the years)

dsp = K.dsp
SR, N, DUR = K.SR, K.N, K.DUR
db = K.db
MUSIC_URL = 'https://github.com/Eouchi147/rc-render/releases/download/music/mozart-figaro-overture.ogg'
MUSIC_CACHE = os.path.expanduser('~/.cache/kinoforge/music/mozart-figaro-overture.ogg')


# ==================================================================================================================
# 1. EVENT TIMES: read from the picture's own table (the T(**seconds) calls of blender.py) and beats.json; nothing is typed twice
# ==================================================================================================================
def read_events():
    """{event: seconds} from blender.py's T(**seconds) calls (film seconds, each anchored to its beat) and the szworld clock."""
    tree = ast.parse(open(os.path.join(FILM, 'blender.py')).read())
    ev = {}
    for n in tree.body:
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and getattr(n.value.func, 'id', '') == 'T':
            for kw in n.value.keywords: ev[kw.arg] = float(ast.literal_eval(kw.value))
    tab = {}
    for k, s in ev.items():                                   # the same anchoring blender.py does: (beat, fraction)
        for b in W.BEATS:
            if b['t0'] - 1e-6 <= s < b['t1'] - 1e-6: tab[k] = (b['name'], (s - b['t0']) / (b['t1'] - b['t0'])); break
        else: tab[k] = (W.BEATS[-1]['name'], (s - W.BEATS[-1]['t0']) / (W.BEATS[-1]['t1'] - W.BEATS[-1]['t0']))
    W.set_events(tab)
    W.WORD_IN['stir'] = W.B.gather0 - 0.2; W.WORD_IN['send'] = W.B.final
    bj = json.load(open(os.path.join(FILM, 'beats.json')))
    return {k: getattr(W.B, k) for k in ev}, bj, W.word_windows()


def ensure_bank(names):
    d = K.bank_dir()
    miss = [n for n in names if not os.path.exists(os.path.join(d, n + '.flac'))]
    if miss: raise SystemExit('the bank lacks %s' % miss)
    return d


def bank_csv():
    """name -> source page, from the bank's csv."""
    rows = {}
    for p in (os.path.join(K.CACHE, 'sfx-bank.csv'), os.path.join(os.path.dirname(K.bank_dir()), 'sfx-bank.csv')):
        if os.path.exists(p):
            import csv
            for r in csv.DictReader(open(p)): rows[r['name']] = r
            break
    return rows


# ==================================================================================================================
# 2. THE MUSIC: the edit of beats.json, then a slow level rider
# ==================================================================================================================
def music_file():
    p = os.environ.get('MUSIC_FILE') or MUSIC_CACHE
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        print('downloading the recording (once):', MUSIC_URL)
        urllib.request.urlretrieve(MUSIC_URL, p + '.part'); os.replace(p + '.part', p)
    return p


EDIT = dict(a0=0.0, a1=27.6, b0=195.0, b1=239.9, xf=1.5)          # recording seconds; beats.json music.edit (B starts at film 26.1)


def music_edit():
    x, sr = sf.read(music_file(), dtype='float32', always_2d=True)
    if sr != SR: x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
    A = x[int(EDIT['a0'] * SR):int(EDIT['a1'] * SR)]; Bm = x[int(EDIT['b0'] * SR):int(EDIT['b1'] * SR)]
    L = int(EDIT['xf'] * SR); ramp = np.linspace(0, 1, L, dtype=np.float32)[:, None]      # triangular = linear in, linear out
    y = np.concatenate([A[:-L], A[-L:] * (1 - ramp) + Bm[:L] * ramp, Bm[L:]])
    y = y[:N] if len(y) >= N else np.vstack([y, np.zeros((N - len(y), 2), np.float32)])
    return y.astype(np.float32)


def lufs_curve(y, win=0.4, hop=0.1):
    """momentary loudness (K-weighted, LUFS) every hop s."""
    k = dsp._kweight(y.astype(np.float64), SR); sq = (k ** 2).sum(1); c = np.concatenate([[0], np.cumsum(sq)])
    w, h = int(win * SR), int(hop * SR); st = np.arange(0, len(sq) - w + 1, h)
    return -0.691 + 10 * np.log10(np.maximum((c[st + w] - c[st]) / w, 1e-12))


def level_rider(y, target=-22.0, ratio=1.7, sigma=1.0, maxg=7.0):
    """Zero-phase, slow gain riding: out = target + (level - target) / ratio on a 1 s Gaussian-smoothed level. Smooth,
    no attack or release artefacts, no change to the notes' shape; returns (y, gain_db_curve_at_hop)."""
    lv = lufs_curve(y); sm = gaussian_filter1d(np.maximum(lv, -60.0), sigma / 0.1, mode='nearest')
    g = np.clip((target - sm) * (1 - 1 / ratio), -maxg, maxg)
    tt = (np.arange(len(g)) * 0.1 + 0.2)
    gi = np.interp(np.arange(len(y)) / SR, tt, g)
    return (y * db(gi)[:, None]).astype(np.float32), g


# ==================================================================================================================
# 4. THE MIXER: spots and beds on K.Mix, each set by its own level (peak or RMS) so the table below reads in dB
# ==================================================================================================================
def rms_db(x, floor=-50.0):
    """RMS of the parts of x within 30 dB of its loudest 0.1 s block (so silence inside a clip does not skew it)."""
    m = x.mean(1); h = SR // 10; n = len(m) // h
    if n < 1: return float(20 * np.log10(np.sqrt((m ** 2).mean()) + 1e-9))
    e = np.array([(m[i * h:(i + 1) * h] ** 2).mean() for i in range(n)]); keep = e > e.max() * 1e-3
    return float(10 * np.log10(e[keep].mean() + 1e-12))


def f0_of(x, lo=300.0, hi=9000.0):
    """The strongest partial of a clip, Hz, measured on its loudest 0.6 s."""
    m = x.mean(1); h = SR // 10
    e = np.array([(m[i:i + h] ** 2).sum() for i in range(0, max(1, len(m) - h), h // 2)]); a = int(np.argmax(e)) * (h // 2)
    s = m[max(0, a - h // 2):max(0, a - h // 2) + int(0.6 * SR)]; n = 1 << 16
    S = np.abs(np.fft.rfft(np.pad(s * np.hanning(len(s)), (0, n - len(s))))); f = np.fft.rfftfreq(n, 1 / SR); band = (f > lo) & (f < hi)
    return float(f[band][np.argmax(S[band])])


PC = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def tune_speed(x, notes, lo_st=-5.0, hi_st=7.0):
    """Resampling ratio that moves the clip's strongest partial to the nearest of the pitch classes `notes`."""
    p = 69 + 12 * np.log2(f0_of(x) / 440.0); best = None
    for n in notes:
        s = ((PC[n] - p + 6) % 12) - 6                       # nearest shift in semitones, -6..+6
        if lo_st <= s <= hi_st and (best is None or abs(s) < abs(best)): best = s
    if best is None: best = 0.0
    return float(2 ** (best / 12.0)), float(best)


class Film:
    def __init__(self):
        self.m = K.Mix(seed=65)
        self.rows = []                     # every placement: dict(t, event, name, gain_db, peak_db)
        self.mus = None                    # the leveled music (pre-master): spot levels are set against it
        self.cache = {}

    def mr(self, a, b):
        """RMS (dBFS) of the music between a and b s: what an effect has to sit under."""
        a = max(0.0, a); b = min(DUR, max(b, a + 0.1))
        return max(-60.0, rms_line(self.mus, a, b))

    def auto_notes(self, t, dur=1.5, thr=0.14, kmax=3):
        """The pitch classes the orchestra is playing from t for `dur` s (strongest first, each above `thr` of the energy):
        a tuned sound is moved to the nearest of them, so it rings with the chord and never against it."""
        key = (round(t, 2), dur)
        if key not in self.cache:
            m = self.mus.mean(1); a = int(max(0.0, t) * SR); n = 1 << 16
            seg = m[a:a + min(n, int(dur * SR))]; seg = np.pad(seg * np.hanning(len(seg)), (0, n - len(seg)))
            S = np.abs(np.fft.rfft(seg)) ** 2; f = np.fft.rfftfreq(n, 1 / SR); c = np.zeros(12)
            ok = (f > 100) & (f < 2500); pit = 12 * np.log2(np.maximum(f[ok], 1) / 440.0) + 69; near = np.abs(pit - np.round(pit)) < 0.3
            np.add.at(c, np.round(pit[near]).astype(int) % 12, S[ok][near]); c = c / c.sum()
            names = list(PC); top = [names[i] for i in np.argsort(c)[::-1][:kmax] if c[i] >= thr]
            self.cache[key] = top or [names[int(np.argmax(c))]]
        return self.cache[key]

    # -- one recording placed on one event
    def spot(self, name, t, peak=None, rms=None, p=0.0, start=0.0, length=None, hp=None, lp=None, speed=1.0, fi=0.008, fo=0.08,
             rev=False, at_peak=False, lead=0.02, swell=False, rel=None, rmsrel=None, trim=True, width=1.0, send=None, notes=None, label='', sweep=None, gain=0.0):
        """Place `name` so its onset (or, reversed, its end; with at_peak its loudest moment) lands on t. Level: `rel` = the
        clip's peak in dB against the music's RMS around t (the way a mixer thinks: 'a splash 6 dB under the music'), or
        `rmsrel` = its RMS against the music's, or `peak` / `rms` in dBFS, else `gain` dB on the raw file. notes=[pitch
        classes]: tuned to the music's key by resampling."""
        t_ev = t
        if rel is not None: peak = self.mr(t - 0.25, t + 0.5) + rel
        if rmsrel is not None: rms = self.mr(t - 0.25, t + 0.5) + rmsrel
        x = K.load(name)[int(start * SR):]
        if length is not None: x = x[:int(length * SR * speed)]
        if rev: x = x[::-1].copy()
        elif trim: x = K.onset(x)
        tuned = None
        if notes == 'auto': notes = self.auto_notes(t_ev)
        x = K.shape(x, hp, lp, speed, width)
        if notes:                                                     # tune what is left after the filters (its strongest partial) to the chord
            sp, tuned = tune_speed(x if not rev else x[::-1], notes); tuned = round(tuned, 2); x = K.shape(x, speed=sp)
        x = K.fades(x, fi, fo)
        pc_out = None
        if notes and not rev:                                         # check the tuning: which pitch class does the result sit on, and how far off (cents)?
            pm_ = 69 + 12 * np.log2(f0_of(x) / 440.0); k_ = int(round(pm_)); pc_out = '%s %+d cents' % (list(PC)[k_ % 12], round(100 * (pm_ - k_)))
        env_ = np.abs(x).max(1); onset_ms = None
        if not rev and len(x) and env_.max() > 0: onset_ms = round(1000.0 * int(np.argmax(env_ > 0.1 * env_.max())) / SR, 1)     # where it speaks, from t
        if p: x = K.pan(x, p)
        if sweep is not None:
            a = (np.clip(np.linspace(sweep[0], sweep[1], len(x)), -1, 1) + 1) * np.pi / 4
            x = x * np.stack([np.cos(a), np.sin(a)], 1).astype(np.float32) * 1.414
        if peak is not None: g = peak - float(20 * np.log10(np.abs(x).max() + 1e-9))
        elif rms is not None: g = rms - rms_db(x)
        else: g = gain
        x = x * db(g)
        if at_peak:           # a hit or a swell: its loudest moment (30 ms envelope) lands on t (+ lead), not its first noise
            e50 = np.convolve(np.abs(x).max(1), np.ones(SR // 33) / (SR // 33), 'same'); t = t + lead - float(np.argmax(e50)) / SR; onset_ms = round(1000 * lead, 1)
        i = int(round((t - len(x) / SR if rev else t) * SR))
        if i < 0: x = x[-i:]; i = 0
        mm = min(len(x), N - i)
        if mm > 0:
            self.m.bus[i:i + mm] += x[:mm]
            if send is not None: self.m.send[i:i + mm] += x[:mm] * db(send)
        self.m._note(name, f'{label or "spot"} at {t_ev:.2f} s')
        self.rows.append(dict(t=round(float(t_ev), 3), what=label, name=name, gain_db=round(float(g), 1),
                              peak_db=round(float(20 * np.log10(np.abs(x[:max(mm, 1)]).max() + 1e-9)), 1), tuned_st=tuned, notes=list(notes) if notes else None, pitch_out=pc_out,
                              pan=round(float(p), 2), onset_ms=(None if swell else onset_ms), swell=bool(swell), rev=bool(rev), tail_s=round(len(x) / SR, 2)))
        return self

    # -- a looped bed, level by RMS, with a dB envelope over the film (absolute times)
    def bed(self, name, t0, t1, rms=None, rel=None, start=0.0, hp=None, lp=None, speed=1.0, p=0.0, env=None, fi=1.0, fo=1.0, xf=1.0, send=None,
            width=1.0, smooth=True, label=''):
        if rel is not None: rms = self.mr(t0, t1) + rel
        x = K.load(name); start = smooth_start(x, start, min(20.0, t1 - t0)) if smooth else start
        x = x[int(start * SR) % len(x):] if start < len(x) / SR else x
        x = K.shape(x, hp, lp, speed, width)
        n = int((t1 - t0) * SR)
        y = K.fades(K.loop(x, n, xf), fi, fo); g = rms - rms_db(y[:min(len(y), 20 * SR)])
        y = y * db(g)
        if p: y = K.pan(y, p)
        i = int(t0 * SR); mm = min(n, N - i); seg = y[:mm]
        if env is not None: seg = seg * K.envelope(env)[i:i + mm, None]
        self.m.bus[i:i + mm] += seg
        if send is not None: self.m.send[i:i + mm] += seg * db(send)
        self.m._note(name, f'bed {t0:.1f}-{t1:.1f} s')
        self.rows.append(dict(t=round(float(t0), 3), what=label or 'bed', name=name, gain_db=round(float(g), 1), bed_to=round(float(t1), 3)))
        return self


def pan_of(x, y, az=-62.0, half=2.4):
    """Stereo position -1..1 of a world point (metres) from the fixed camera of blender.py (screen right = 0.88 x + 0.47 y)."""
    a = np.radians(az); cx, cy = np.cos(a), np.sin(a); rx, ry = -cy, cx          # right vector of the camera (see szlife.face_cam)
    return float(np.clip((x * rx + y * ry) / half, -0.9, 0.9))


# ==================================================================================================================
# 5. HELPERS TO PICK PIECES OF RECORDINGS (no ears needed: onsets and energy are found in the file itself)
# ==================================================================================================================
_ON = {}


def onsets(name, gap=0.15, rise=9.0, floor_db=-45.0):
    """Onset times (s) of a recording: where the 10 ms envelope jumps `rise` dB above the previous 60 ms and is not buried."""
    if name in _ON: return _ON[name]
    x = K.load(name).mean(1); h = SR // 100; n = len(x) // h
    e = 10 * np.log10(np.array([(x[i * h:(i + 1) * h] ** 2).mean() for i in range(n)]) + 1e-12)
    top = e.max(); out = []
    for i in range(6, n):
        if e[i] > top + floor_db and e[i] - e[i - 6:i].min() > rise and (not out or (i - out[-1]) * 0.01 > gap): out.append(i)
    _ON[name] = [round(i * 0.01, 2) for i in out]
    return _ON[name]


def loud_windows(name, length, k, hop=None, start=0.0, stop=None):
    """The k loudest non-overlapping windows (start times, s) of `length` s: energetic pieces of a continuous recording."""
    x = K.load(name).mean(1); w = int(length * SR); hop = int((hop or length) * SR)
    a = int(start * SR); z = len(x) if stop is None else int(stop * SR)
    cand = [(float((x[i:i + w] ** 2).mean()), i / SR) for i in range(a, z - w, hop)]
    cand.sort(key=lambda c: -c[0]); pick = sorted(c[1] for c in cand[:k])
    return pick


def smooth_start(x, start, length, span=90.0, step=1.0):
    """Where, from `start` on (within `span` s), a stretch of `length` s of a long recording has the lowest crest factor: a bed
    set by its RMS must not carry a stray loud drop or knock (rain on a puddle has drops 30 dB over its level)."""
    m = x.mean(1); w = int(length * SR); best = (1e9, start)
    for a in np.arange(start, min(len(m) / SR - length, start + span), step):
        seg = m[int(a * SR):int(a * SR) + w]
        if len(seg) < w: break
        c = np.abs(seg).max() / (np.sqrt((seg ** 2).mean()) + 1e-9)
        if c < best[0]: best = (c, float(a))
    return best[1]


def pieces(name, floor=-50.0, gap=0.06):
    """(start, end) of every stretch of a recording that is not (nearly) silent, in s: whooshes and drops come in series."""
    x = K.load(name).mean(1); h = SR // 100; n = len(x) // h
    e = 10 * np.log10(np.array([(x[i * h:(i + 1) * h] ** 2).mean() for i in range(n)]) + 1e-12); on = e > e.max() + floor; out = []; i = 0
    while i < n:
        if on[i]:
            j = i
            while j < n and (on[j] or on[j:j + int(gap * 100) + 1].any()): j += 1
            out.append((round(i * 0.01, 2), round(j * 0.01, 2))); i = j
        else: i += 1
    return out



# ==================================================================================================================
# 6. THE SOUND OF THE FILM: every event of the picture, in time order
# ==================================================================================================================
def year_times(frac, a, b):
    """Times in [a, b] where the year phase passes `frac` (a season's centre) going up (szworld.years)."""
    ts = np.arange(a, b, 1.0 / 48.0); y = np.array([W.years(t) for t in ts]) - frac; k = np.floor(y)
    return [float(ts[i]) for i in range(1, len(ts)) if k[i] > k[i - 1]]


def design(F, T, WORDS):
    """Every level is `rel`: the clip's peak in dB against the music's RMS around the event (bed rel for steady sounds)."""
    rng = np.random.default_rng(74)
    AUTO = 'auto'                                        # tuned to what the orchestra plays at that moment
    FY = -1.1                                            # the cut face (szworld.HY = 1.1)
    face = lambda x: pan_of(x, FY, half=2.0)             # pan of a point on the cut face
    park = lambda x, y: pan_of(x, y, half=2.0)           # pan of a point on the lawn
    HOLE = park(*W.HOLE_XY); TREE = park(W.TX, W.TY)
    stp = lambda nm, i: onsets(nm)[i % len(onsets(nm))]
    cl = pieces('cloth'); cl_long = max(cl, key=lambda a: a[1] - a[0])

    def grass(t, rel, p, i, label, length=0.24, lp=3500, nm='steps_short_grass', speed=1.0, hp=200):
        F.spot(nm, t, rel=rel, at_peak=True, lead=0.015, start=max(0.0, stp(nm, i) - 0.06), length=length, lp=lp, hp=hp, speed=speed, fi=0.01, fo=0.12, trim=False, p=p, label=label)

    # ---- the seasons on top: birds in spring and summer, wind in autumn and winter (read from the picture's own season weights)
    tt = np.arange(0.0, 74.01, 0.25); wts = np.array([W.weights(t) for t in tt])
    bird_env = [(float(t), float(-26.0 + 26.0 * (w[0] + w[1]))) for t, w in zip(tt, wts)]
    wind_env = [(float(t), float(-24.0 + 24.0 * (w[2] + w[3]))) for t, w in zip(tt, wts)]
    F.bed('birds_waking_3', 0, 74, rel=-17, start=40, hp=500, env=bird_env, fi=1.5, fo=2.5, label='park birds (spring and summer)')
    F.bed('wind_plain', 0, 74, rel=-24, start=20, hp=120, lp=3500, env=wind_env, fi=1.5, fo=2.5, label='a soft breeze (autumn and winter swell it)')
    F.bed('cave_soundscape_1', T['reveal0'] - 0.1, T['pop0'] - 0.3, rel=-26, start=12, hp=100, lp=2800, fi=0.8, fo=1.2, send=-6,
          env=[(8.6, -30), (9.6, 0), (33.0, 0), (33.9, -30)], label='the hush of the soil (the hidden world)')

    # ---- hook 0 to 5.2: the glinting egg, and little feet passing on the lawn above
    for k, tg in enumerate([T['egg_glint0'], T['egg_glint0'] + 1.7, T['egg_glint0'] + 3.4]):
        F.spot('chimes_butterfly_1', tg, rel=-14 - 2 * k, p=0.0, notes=AUTO, send=-3, fo=0.5, length=1.6, label='the egg glints')
    for j in range(8):                                   # shoes of the passers-by (the girl and the boy cross the lawn)
        grass(0.7 + 0.5 * j, -16 + 2 * float(np.sin(np.pi * j / 7)), 0.45 - 0.1 * j, 2 * j, 'shoes pass on the lawn above', length=0.22, lp=3000)
    # ---- scurry 5.2 to 8.7: the egg cracks, the nymph tumbles, a tiny plop, tiny feet, a dive into the hole
    F.spot('candle_sparkle_1', T['crack0'], rel=-12, start=8.0, length=0.7, hp=1200, lp=9000, fi=0.01, fo=0.3, p=0.0, trim=False, label='the egg cracks (a tiny crackle)')
    F.spot('ice_crack_2', T['crack1'], rel=-14, at_peak=True, lead=0.01, speed=1.3, hp=900, lp=7000, fi=0.01, fo=0.25, length=0.5, trim=False, p=0.0, label='the shell splits')
    F.spot('boing_6', T['fall1'], rel=-9, p=-0.05, notes=AUTO, lp=3500, fi=0.02, fo=0.25, length=0.6, label='a tiny plop as the nymph lands')
    n_w = int((T['walk1'] - T['walk0']) / 0.17)
    for j in range(n_w):
        tf = T['walk0'] + 0.08 + 0.17 * j; u = j / max(1, n_w - 1)
        grass(tf, -17 + 2 * float(np.sin(np.pi * u)), pan_of(0.0 + (W.HOLE_XY[0]) * u, -0.7 + (W.HOLE_XY[1] + 0.7) * u, half=2.0), 3 * j + 1, 'tiny feet scurry to the hole', length=0.16, lp=6000, nm='steps_twigs', speed=1.25, hp=900)
    F.spot('water_bubble_2', T['dive0'] + 0.05, rel=-10, at_peak=True, lead=0.01, speed=1.4, length=0.4, lp=5000, fo=0.2, p=HOLE, trim=False, label='a dive into the hole (a soft bubble)')
    F.spot('water_over_soil', T['dive0'] + 0.1, rel=-15, start=1.0, length=0.8, lp=3000, hp=200, fi=0.1, fo=0.4, p=HOLE, trim=False, swell=True, label='soil trickles in')
    for j in range(8):                                   # digging down the shaft: little scratches, a crumb of soil each time
        ts = T['shaft0'] + 0.25 + 0.5 * j
        if ts > T['shaft1'] - 0.4: break
        F.spot('brush_wood', ts, rel=-13 + 0.6 * j, at_peak=True, lead=0.0, start=1.0 + 1.3 * j, length=0.34, speed=1.4, hp=500, lp=6500, fi=0.06, fo=0.14, p=face(W.SHAFT_X), trim=False, label='the nymph digs down the shaft')

    # ---- reveal 8.75 (the first tutti burst): the hidden world lights up, the neighbours pop in one by one
    t0 = T['reveal0']
    F.spot('cluster_chimes', t0, rel=-8, start=loud_windows('cluster_chimes', 2.5, 1, hop=0.5, start=0.0, stop=120.0)[0], length=2.6, notes=AUTO, lp=10000, fi=0.06, fo=1.4, send=-2, trim=False, swell=True,
           label='THE HIDDEN WORLD: tunnels glow open (a burst of chimes on the tutti)')
    F.spot('glockenspiel', t0 + 0.04, rel=-9, speed=2 ** (4 / 12), lp=9000, fi=0.02, fo=1.6, length=2.4, send=-3, p=0.1, label='THE HIDDEN WORLD: sparkle')
    for nm, te, xw, rl, lab in (('boing_2', T['pop_worm'], -0.75, -9, 'the worms pop in'), ('boing_4', T['pop_ant'], 0.9, -9, 'the ants pop in'),
                                 ('boing_8', T['pop_mole'], 0.3, -8, 'the mole pops in'), ('boing_6', T['pop_grub'], -1.3, -9, 'the grubs pop in')):
        F.spot(nm, te, rel=rl, p=face(xw), notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.6, label=lab)
    for te, xw in ((T['roots_on0'] + 0.1, -0.7), (T['roots_on0'] + 0.5, -0.4), (T['roots_on1'] - 0.2, -0.1)):    # roots drink
        F.spot('chimes_dream_1', te, rel=-14, notes=AUTO, length=1.4, lp=9000, hp=700, fi=0.01, fo=0.9, p=face(xw), send=-2, label='the roots wake and drink (a sparkle)')

    # ---- meet 14.25 to 22.15: busy neighbours, the nymph sips, the label, the sandwich joke
    drip = T['settle0'] + 0.3; j = 0
    while drip < T['unhook0'] - 0.5:
        nm = ('drops_1', 'drops_2', 'drops_4', 'drops_3')[j % 4]; pc = pieces(nm); pa = pc[(2 * j) % min(8, len(pc))]
        F.spot(nm, drip, rel=-9, at_peak=True, lead=0.01, start=max(0.0, pa[0] - 0.03), length=0.5, hp=600, lp=7500, speed=1.15, fi=0.01, fo=0.3, p=face(-0.19), send=-2, trim=False,
               label='the nymph sips root juice (a drop)')
        drip += float(rng.uniform(1.3, 1.9)); j += 1
    F.spot('wine_stopper_3', T['label0'] + 0.05, rel=-12, lp=4500, hp=300, fi=0.01, fo=0.2, p=face(-0.19), label='the label pops: CICADA!')
    F.spot('chimes_butterfly_3', T['label0'] + 0.1, rel=-13, notes=AUTO, length=1.6, lp=9000, fi=0.02, fo=1.0, p=face(-0.19), send=-3, label='a sparkle on the label')
    for k in range(6):                                   # worms slide: slow soft squelches, a head each 11 s and 8 s
        F.spot('steps_mud', T['pop_worm'] + 2.0 + 3.1 * k, rel=-14, at_peak=True, lead=0.02, start=max(0.0, stp('steps_mud', 2 * k + 1) - 0.06), length=0.55, speed=0.8, lp=1500, hp=120,
               fi=0.02, fo=0.3, p=face(-0.9 + 0.3 * (k % 3)), trim=False, label='a worm slides along its tunnel')
    for k in range(10):                                  # ants skitter along the passages
        grass(T['pop_ant'] + 1.0 + 2.2 * k, -19, face(0.4 + 0.15 * (k % 4)), 5 * k + 2, 'ants skitter in the tunnels', length=0.3, lp=6500, nm='steps_pebbles', speed=1.4, hp=1200)
    T0 = T['pop_ant'] + 2.5; cyc = 14.0
    for c in range(0, 6):                                # the visual joke: the ant hauls a sandwich crumb bigger than itself, down and into the pantry
        ta = T0 + cyc * c; tdrop = ta + 0.62 * cyc
        if ta < T['pop_ant'] or tdrop > 72.0: continue
        for q in range(5):
            grass(ta + 0.8 + 1.5 * q, -15, face(0.9 - 0.12 * q), 7 * q + c, 'the ant hauls its crumb', length=0.28, lp=5000, nm='steps_pebbles', speed=1.2, hp=900)
        F.spot('squeaker_toy_2', tdrop, rel=-14, start=2.0, length=0.35, notes=AUTO, lp=5500, fi=0.02, fo=0.2, p=face(0.58), label='the crumb is home (a tiny squeak: the joke)')
        F.spot('boing_6', tdrop + 0.12, rel=-17, notes=AUTO, lp=3500, fi=0.02, fo=0.25, length=0.5, p=face(0.58), label='the crumb lands in the pantry')
    for k in range(7):                                   # the mole digs: soft muffled crunches and soil
        te = T['pop_mole'] + 2.2 + 3.6 * k
        if te > 31.0: break
        mx = 1.2 - 2.0 * min(1.0, (te - T['pop_mole']) / 21.0)
        F.spot('dig_shovel', te, rel=-12, at_peak=True, lead=0.02, start=3.0 + 3.1 * k, length=0.8, speed=0.7, lp=1100, hp=60, fi=0.03, fo=0.35, p=face(mx), trim=False, label='the mole digs (soft)')
    for k in range(9):                                   # the grubs munch roots
        F.spot('rusk_crunch', T['pop_grub'] + 1.5 + 2.3 * k, rel=-17, at_peak=True, lead=0.02, start=max(0.0, stp('rusk_crunch', 3 * k) - 0.06), length=0.4, speed=1.2, lp=3000, hp=250, fi=0.01, fo=0.15,
               p=face(-1.3), trim=False, label='a grub munches a root')

    # ---- years 22.15 to 27.6: the seasons race, the clock spins, a soft tick for each spring
    a, b = T['yr0'], T['yr1']
    for k, ts in enumerate(year_times(0.125, T['stack0'] - 0.5, T['yr1'])):
        F.spot('metallophone', ts, rel=-12 - 0.3 * k, notes=AUTO, length=1.2, lp=9000, fi=0.01, fo=0.8, p=0.35, send=-3, label='a year turns (a soft tick)')
    F.spot('winder_1', T['stack0'] - 0.2, rel=-10, length=5.7, hp=500, lp=5000, fi=0.6, fo=1.0, p=0.35, swell=True, label='the clock winds (a music-box winder)')
    F.spot('wind_whistle_2', T['stack0'] - 0.3, rel=-18, start=3, length=5.6, hp=300, lp=4500, fi=0.8, fo=1.2, swell=True, label='a wind of years')
    F.bed('steps_leaves', T['stack0'] + 0.5, T['yr1'] - 1.5, rel=-24, hp=700, lp=5500, p=-0.2, fi=1.0, fo=1.0, label='leaves of the years')

    # ---- stir 27.6 to 34.0: the soil warms, the nymphs unhook and gather, everything leans toward the shaft
    F.bed('sun_heat_1', T['warm0'] - 0.3, T['pop0'] + 0.2, rel=-23, start=5, hp=120, lp=4500, env=[(27.5, -30), (29.5, -6), (33.0, 0), (34.1, -30)], fi=0.6, fo=0.6, label='the soil warms (a warm hush)')
    F.bed('heartbeat_5', T['unhook0'] - 0.4, T['pop0'] - 0.2, rel=-25, start=6, hp=50, lp=900, p=face(-0.1), env=[(28.0, -30), (29.0, -8), (33.0, 0), (33.6, -30)], fi=0.5, fo=0.5, label='many small hearts wake')
    for i in range(5):
        F.spot('suction_cup_plastic', T['unhook0'] + 0.12 * i, rel=-13, start=0.2 + 0.7 * i, length=0.45, notes=None, speed=1.2, hp=300, lp=4500, fi=0.01, fo=0.2, p=face(-0.6 + 0.15 * i), trim=False,
               label='a nymph lets go of the root (a tiny pop)')
    for j in range(10):
        grass(T['unhook0'] + 0.8 + 0.45 * j, -17, face(-0.5 + 0.1 * j), 4 * j + 3, 'little feet crawl to the shaft', length=0.2, lp=5500, nm='steps_pebbles', speed=1.3, hp=1000)
    for te, rl in ((T['up0'] - 0.6, -8), (T['up0'] + 0.3, -6), (T['pop0'] - 0.5, -4)):
        F.spot('chimes_butterfly_3', te, rel=rl, rev=True, notes=AUTO, send=-3, fi=0.3, fo=0.25, p=HOLE, swell=True, label='a rising shimmer up the shaft (reversed chimes)')
    F.spot('wind_inside_2', T['up0'] - 0.3, rel=-14, start=8, length=2.2, hp=100, lp=3000, fi=0.8, fo=0.8, trim=False, swell=True, label='a breath of air up the shaft')

    # ---- emerge (the finale tutti at 34.0): they pop out of the lawn, the birds fly up, the dog barks, they march to the tree
    th = T['pop0']
    F.spot('cluster_chimes', th, rel=-8, start=loud_windows('cluster_chimes', 2.5, 2, hop=0.5, start=0.0, stop=120.0)[-1], length=2.6, notes=AUTO, lp=10000, fi=0.06, fo=1.4, send=-2, trim=False, swell=True,
           label='THEY ARE OUT: a burst of chimes on the finale tutti')
    for i, nm in enumerate(('boing_2', 'boing_4', 'boing_6', 'boing_8', 'boing_2')):
        F.spot(nm, th + 0.16 * i, rel=-8 - i, p=HOLE + 0.04 * (i - 2), notes=AUTO, lp=3500, fi=0.02, fo=0.25, length=0.5, label='a cicada pops out of the lawn')
    F.spot('water_over_soil', th - 0.05, rel=-15, start=2.0, length=1.2, lp=3500, hp=200, fi=0.05, fo=0.6, p=HOLE, trim=False, swell=True, label='soil crumbs fall away')
    for k_, tb in enumerate((T['bird_up'], T['bird_up'] + 0.12, T['bird_up'] + 0.3)):
        F.spot(('flight_bird_1', 'flight_pigeon', 'flight_bird_2')[k_], tb, rel=-14 - k_, sweep=(0.2, 0.9), length=1.6, lp=7000, hp=250, fo=0.5, swell=True, label='birds fly up from the big tree')
    bk = onsets('old_dog_bark_3')
    for k_, (tb, rl) in enumerate(((T['look0'] + 0.3, -7), (T['look0'] + 1.0, -9), (T['look0'] + 2.7, -11))):
        F.spot('old_dog_bark_3', tb, rel=rl, at_peak=True, lead=0.02, start=max(0.0, bk[(2 * k_) % len(bk)] - 0.06), length=0.3, speed=1.25, lp=3800, hp=250, fi=0.015, fo=0.12,
               p=0.5 - 0.1 * k_, trim=False, label='the dog barks happily')
    F.spot('toy_squeal_1', T['look0'] + 0.1, rel=-15, start=0.3, length=0.5, notes=AUTO, lp=6000, fi=0.02, fo=0.25, p=-0.2, label='the kids gasp (a toy squeal stands in)')
    nm_ = int((T['march1'] - T['march0']) / 0.24)
    for j in range(nm_):                                 # five small cicadas march from the hole to the tree
        u = j / max(1, nm_ - 1)
        grass(T['march0'] + 0.24 * j, -18 + 2 * float(np.sin(np.pi * u)), HOLE + (TREE - HOLE) * u, 6 * j + 1, 'the cicadas march to the tree', length=0.18, lp=6000, nm='steps_twigs', speed=1.3, hp=900)

    # ---- climb 43.6 to 55.55: scratch, scratch up the trunk; a robin, the wind in the leaves
    for k in range(18):
        ts = T['climb0'] + 0.3 + 0.62 * k
        if ts > T['crack_shell0'] - 1.6: break
        F.spot('brush_wood', ts, rel=-14 + 0.4 * k / 3, at_peak=True, lead=0.0, start=(1.0 + 0.7 * k) % 11.0, length=0.3, speed=1.35, hp=500, lp=6500, fi=0.05, fo=0.12, p=TREE, trim=False, label='scritch, they climb the trunk')
    F.spot('robin_1', 47.0, rel=-18, p=-0.35, lp=6000, fi=0.05, fo=0.5, send=-4, label='a robin in the tree')
    F.bed('wind_tree_squeaks', T['climb0'], T['crack_shell0'] + 0.5, rel=-26, start=30, hp=300, lp=4500, p=TREE, fi=1.5, fo=1.0, label='the big tree creaks in the breeze')

    # ---- split 55.55 to 59.7: the old skin splits, the wings unfold, then they snap open on the coda (59.7)
    F.spot('ice_crack_2', T['crack_shell0'], rel=-9, at_peak=True, lead=0.01, speed=1.1, hp=700, lp=7500, fi=0.01, fo=0.3, length=0.7, trim=False, p=TREE, label='the old skin splits (a soft crack on the accent)')
    F.spot('candle_sparkle_2', T['crack_shell0'] + 0.1, rel=-14, start=5.0, length=1.5, hp=1000, lp=9000, fi=0.05, fo=0.5, p=TREE, trim=False, swell=True, label='a crackle of the skin')
    F.spot('cloth', T['ease0'], rel=-17, start=cl_long[0] + 1.0, length=2.6, hp=500, lp=5000, fi=0.4, fo=0.6, p=TREE, trim=False, swell=True, label='the wings unfold (soft cloth)')
    F.spot('chimes_dream_1', T['ease0'] + 0.5, rel=-12, notes=AUTO, length=2.8, lp=9000, hp=500, fi=0.3, fo=1.6, p=TREE, send=-3, swell=True, label='the wings grow, glowing')
    F.spot('dreamcatcher', T['ease1'] - 0.3, rel=-16, start=0.2, length=1.6, notes=AUTO, lp=9000, fi=0.1, fo=0.8, p=TREE, send=-3, swell=True, label='a held breath before the song')

    # ---- sing 59.7 to 68.05: the wings snap open on the coda, they sing; the kids dance
    to = T['open0']
    F.spot('chimes_butterfly_1', to, rel=-3, notes=AUTO, lp=10000, fi=0.03, fo=1.4, send=-2, p=TREE, label='THE WINGS OPEN: chimes on the coda')
    F.spot('glockenspiel', to + 0.05, rel=-6, speed=2 ** (4 / 12), lp=9000, fi=0.02, fo=1.8, length=2.8, send=-3, p=TREE + 0.1, label='THE WINGS OPEN: a bright sparkle')
    F.spot('triangle_2', to + 0.02, rel=-9, notes=AUTO, lp=9000, fi=0.03, fo=1.8, length=3.0, send=-3, p=TREE - 0.1, label='THE WINGS OPEN: a soft triangle')
    F.bed('field_cricket', T['song0'], T['final'] + 3.5, rel=-17, start=6, hp=2500, lp=9500, speed=1.0, p=TREE, env=[(60.0, -30), (61.5, 0), (67.0, 0), (68.6, -4), (71.5, -9), (73.0, -20)], fi=0.8, fo=1.5,
          label='the cicada song (a field cricket chorus stands in; see SOUND.md)')
    F.bed('solitary_bees', T['song0'] + 0.5, T['final'] + 2.0, rel=-30, start=0.0, hp=1500, lp=7000, p=TREE + 0.15, env=[(60.4, -30), (62.0, 0), (66.5, 0), (68.5, -20)], fi=0.8, fo=1.2, label='a shimmer around the song')
    for k_, tb in enumerate((T['song0'] + 0.4, T['song0'] + 1.3, T['song0'] + 3.1, T['song0'] + 5.6)):
        F.spot('old_dog_bark_3', tb, rel=-8 - k_, at_peak=True, lead=0.02, start=max(0.0, bk[(2 * k_ + 1) % len(bk)] - 0.06), length=0.3, speed=1.25, lp=3800, hp=250, fi=0.015, fo=0.12,
               p=0.5 - 0.1 * k_, trim=False, label='the dog barks and dances')
    for k_, ts in enumerate((T['song0'] + 0.6, T['song0'] + 2.4, T['song0'] + 4.8)):
        F.spot('flight_bird_3' if k_ else 'flight_bird_4', ts, rel=-17, sweep=(-0.3, 0.8), length=1.8, lp=7000, hp=300, fo=0.5, swell=True, label='birds join the song')
    for k_ in range(6):
        grass(T['open0'] + 0.35 + 0.3 * k_, -15 - k_, -0.25 + 0.1 * k_, 11 + k_, 'the kids dance on the grass', length=0.22)

    # ---- send 68.05 to 74: the final chord, the sun gold, the girl lies down to listen, the snail waves, the question
    tf = T['final']
    F.spot('tibetan_bowl_1', tf, rel=-8, at_peak=True, lead=0.0, notes=F.auto_notes(tf - 0.3, dur=1.0, kmax=2), lp=5500, fi=0.05, fo=3.5, length=5.9, trim=False, send=-2, swell=True, label='the final chord: a singing bowl swells in')
    F.spot('chimes_dream_3', tf + 0.05, rel=-8, notes=AUTO, lp=9000, fi=0.04, fo=2.0, length=3.4, send=-3, p=0.1, label='the final chord: a twinkle')
    F.spot('triangle_2', tf + 0.1, rel=-11, notes=AUTO, lp=9000, fi=0.03, fo=2.0, length=3.4, send=-3, p=-0.1, label='the final chord: a soft triangle')
    F.spot('cloth', T['lie0'], rel=-17, start=cl_long[0] + 2.0, length=1.6, hp=400, lp=4500, fi=0.2, fo=0.4, p=park(0.9, -0.5), trim=False, swell=True, label='the girl lies down, ear to the grass (cloth)')
    F.spot('body_fall_1', T['lie0'] + 0.9, rel=-16, at_peak=True, lead=0.03, speed=0.7, lp=700, hp=60, fi=0.03, fo=0.4, p=park(0.9, -0.5), trim=False, label='she settles on the lawn')
    F.spot('boing_4', T['wave0'], rel=-12, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.7, p=park(1.38, -1.0), label='the snail waves')
    F.spot('robin_1', 71.2, rel=-18, p=-0.4, lp=6000, fi=0.05, fo=0.6, send=-4, label='a bird calls in the quiet')

    # ---- words in with a soft pop (every word is set in code)
    for w, tw_in, tw_out in WORDS:
        F.spot('wine_stopper_3', tw_in, rel=-15, lp=4500, hp=300, fi=0.01, fo=0.2, p=0.0, label='words pop in: ' + w.lower())
    return dict(reveal=T['reveal0'], emerge=T['pop0'], open=T['open0'], final=T['final'])
# ==================================================================================================================
# 7. MASTER AND MEASURE
# ==================================================================================================================
BANK_RUN = 'rc-render sfx-bank.yml run 40049538821 (24 Oct 2026)'
TARGET_LUFS, TP_LIMIT = -16.0, -1.5
FX_TRIM = 3.0              # the whole effects bus, dB (set by measurement: effects read, the music still leads)


def ebur128(path):
    """Integrated loudness, loudness range and true peak of a file, from ffmpeg's EBU R128 meter."""
    r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = r[r.rfind('Summary:'):]
    g = lambda pat: float(re.search(pat, s).group(1))
    return dict(lufs=g(r'I:\s+(-?[\d.]+) LUFS'), lra=g(r'LRA:\s+(-?[\d.]+) LU'), true_peak=g(r'Peak:\s+(-?[\d.]+) dBFS'))


def dbfs(x):
    return float(20 * np.log10(np.abs(x).max() + 1e-9))


def rms_line(y, t0, t1):
    a, b = int(t0 * SR), int(t1 * SR)
    return float(10 * np.log10((y[a:b] ** 2).mean() + 1e-12))


def master(F, mus, duck, fx_trim, out_dir):
    F.m.room(rt60=2.2, wet=0.55, seed=7, predelay=0.02)                      # the sends (cave, far calls, sparkles) bloom a little
    fx = dsp.highpass(F.m.bus, 40, 2).astype(np.float32) * db(fx_trim)
    musd = (mus * K.envelope(duck)[:, None]).astype(np.float32)
    mix = musd + fx
    gain = TARGET_LUFS - dsp.loudness(mix); ceil = -2.0
    wav = os.path.join(out_dir, 'mix.wav'); m4a = os.path.join(out_dir, 'mix.m4a'); res = {}
    for it in range(6):
        pre = mix * db(gain); y = dsp.limiter(pre, ceil)
        y = K.fades(y, 0.06, 0.35)
        sf.write(wav, y, SR, subtype='PCM_24')
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'aac', '-b:a', '256k', '-ar', str(SR), '-ac', '2',
                        '-movflags', '+faststart', m4a], check=True)
        res = ebur128(m4a)
        eI = TARGET_LUFS - res['lufs']; eP = res['true_peak'] - (TP_LIMIT - 0.05)
        print(f'  pass {it}: {res["lufs"]:.2f} LUFS, true peak {res["true_peak"]:.2f} dBTP, gain {gain:.2f} dB, ceiling {ceil:.2f}')
        if abs(eI) <= 0.2 and eP <= 0: break
        gain += 0.85 * eI
        if eP > 0: ceil -= eP + 0.05
    a_ = np.abs(pre).max(1); b_ = np.abs(y).max(1); ok_ = a_ > 0.02; red = np.where(ok_, 20 * np.log10((a_ + 1e-9) / (b_ + 1e-9)), 0.0)
    res.update(limiter_max_reduction_db=round(float(red.max()), 2), limiter_max_reduction_at_s=round(float(np.argmax(red) / SR), 2),
               limiter_samples_over_1db=int((red > 1.0).sum()))
    res.update(gain_db=round(gain, 2), ceiling_dbfs=round(ceil, 2), wav_sample_peak_dbfs=round(dbfs(y), 2),
               wav_lufs_bs1770=round(dsp.loudness(y), 2))
    return y, musd * db(gain), fx * db(gain), res


def landing_report(F, fx):
    """Independent check on the rendered effects bus (no music): for every percussive spot, where does the effects bus peak
    around its event (10 ms envelope above 150 Hz, window -30 ms to +150 ms) and does it rise 3 dB over the 300 ms before?"""
    h = dsp.highpass(fx, 150, 2).max(1) if fx.ndim == 2 else fx
    env = np.sqrt(np.convolve(np.asarray(h, np.float64) ** 2, np.ones(SR // 100) / (SR // 100), 'same'))
    out = []
    for r in F.rows:
        if 'bed_to' in r or r.get('swell') or r.get('rev') or r.get('onset_ms') is None: continue
        t = r['t']; a, b = int((t - 0.03) * SR), int((t + 0.15) * SR)
        if a < 0 or b > len(env): continue
        pk = a + int(np.argmax(env[a:b])); pre = env[max(0, int((t - 0.33) * SR)):int((t - 0.03) * SR)]
        rise = 20 * np.log10(env[pk] / (np.sqrt((pre ** 2).mean()) + 1e-9))
        out.append(dict(t=t, what=r['what'], peak_offset_ms=round(1000 * (pk / SR - t), 1), rise_db=round(float(rise), 1)))
    good = [o for o in out if -30 <= o['peak_offset_ms'] <= 150 and o['rise_db'] >= 3.0]
    return out, good


def timeline(y, musd, fx, ev_list):
    """0.5 s RMS (dBFS) of the mix, the music alone and the effects alone, around the key events."""
    rows = []
    for name, t in ev_list:
        t0 = max(0.0, t - 1.0)
        pts = []
        for k in range(6):
            a = t0 + 0.5 * k
            if a + 0.5 > DUR: break
            pts.append((round(a, 2), round(rms_line(y, a, a + 0.5), 1), round(rms_line(musd, a, a + 0.5), 1), round(rms_line(fx, a, a + 0.5), 1)))
        rows.append(dict(event=name, t=round(float(t), 2), windows=pts))
    return rows




# ==================================================================================================================
# 8. SOUND.md (written from the same data as mix.json, so the two never disagree)
# ==================================================================================================================
STANDINS = [
    'The cicada song (60 to 74 s) is a field recording of crickets, filtered and kept soft, with a bee shimmer: the bank has no cicada. It reads as a bright insect chorus, not as a real periodical cicada.',
    'Tiny feet (the hatchling, the ants, the marching cicadas) are a twig or pebble step, sped up and high-passed: there is no recording of an insect walking.',
    'Digging and climbing scratches are a wooden brush stroke and a shovel in soil, slowed or sped up and filtered. The mole is a muffled shovel crunch.',
    'Worms are a slowed, low-passed mud step. Grubs munching is a sped-up rusk crunch.',
    'The egg crack is a soft ice crack and a candle crackle: there is no recording of an egg.',
    'The nymph\'s sips are real water drops. Pops of the neighbours and of the cicadas coming out are soft harp "boings", tuned to the music.',
    'The dog is an old dog\'s real barks, played a little faster so it sounds younger and happier: the nearest recording the bank has.',
    'The kids\' gasp is a toy squeal (no children\'s voices in the bank, on purpose: the film has no voices).',
    'The wings opening are real chimes, a triangle and a glockenspiel chord raised a major third; the unfolding is soft cloth.',
    'Words pop in with a wine stopper\'s pop.',
]


def write_sound_md(F, meas, bj, csvrows, edit_info, chk):
    use = {}
    for r in F.rows:
        d = use.setdefault(r['name'], {})
        d.setdefault(r['what'], []).append(r['t'])
    lines = []
    for name in sorted(use):
        parts = []
        for what, ts in use[name].items():
            ts = sorted(ts)
            parts.append(f'{what} ({ts[0]:.1f} s)' if len(ts) == 1 else f'{what} ({len(ts)}x, {ts[0]:.1f} to {ts[-1]:.1f} s)')
        page = csvrows.get(name, {}).get('source', 'bank csv')
        lic = csvrows.get(name, {}).get('licence', 'CC0')
        lines.append(f'| `{name}` | {"; ".join(parts)} | {page} | {lic} |')
    m = bj['music']
    md = f"""# Sound of "Who lives under your feet?" (Little Big Questions)

A SILENT 74 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on screen
has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg). Audio
never goes into git by default (`audio/mix.m4a` is committed here with `git add -f` because the render needs it; `audio/mix.wav`
is ignored); `audio/mix.json` (measurements, every recording and where it is used, the music edit, the event table, the
timelines) is kept.

**Music credit (for the description of the video):** {m['credit']}

## Music licence (read from the asset's `licence.json`)
{m['licence']}. Source page: {m['source_page']}. Asset: {m['asset']}. The Wikimedia Commons file page records the licence as
CC0 1.0 Universal and quotes Musopen's rule that uploaders "represent and warrant that content uploaded to the site is in the
public domain"; attribution is not required and is given anyway. The recording is Czech National Symphony Orchestra via
Musopen; the composition (Mozart, 1786) is long out of copyright.

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- {meas['seconds']:.2f} s, 48 kHz stereo AAC 256k, {meas['lufs']:.1f} LUFS integrated (target {TARGET_LUFS:.0f}), true peak {meas['true_peak']:.2f} dBTP (limit {TP_LIMIT} dBTP), loudness range {meas['lra']:.1f} LU.
- The loudest limiter dip is {meas['limiter_max_reduction_db']:.1f} dB at {meas['limiter_max_reduction_at_s']:.1f} s; the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction). On the rendered effects bus alone, {chk['landed']} of {chk['checked']} percussive spots stand out by 3 dB or more
  within 30 ms before to 150 ms after their event; the rest are quiet details sitting under a bed or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement and by rules, and must be checked by ear on a phone
  speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
Recording 0:00 to 0:27.6 (film 0 to 27.6), a triangular (linear in, linear out) cross-fade of 1.5 s (film 26.1 to 27.6) into recording
3:15.0 to 3:59.9 (film 26.1 to 71.0, played straight through the piece's own final cadence at film 68.05 and its decay), then a quiet
tail to 74.0 s. The hushed scurrying opening (pizzicato strings and whispering woodwinds) is the many small feet; the first tutti burst
at film 8.75 is the hidden world revealed; the tutti at 22.15 is the years racing; the finale tutti at film 34.0 (recording 202.9) is the
cicadas coming out; accents at 43.6 and 55.55 carry the climb and the splitting skin; the coda at 59.7 carries the wings opening and the song;
the final chord at 68.05 closes it. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio {edit_info['ratio']}, gain between
{edit_info['gain_min']:+.1f} and {edit_info['gain_max']:+.1f} dB) lifts the whispering opening and eases the tuttis so the film can sit near -16 LUFS; the notes keep their own shape.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was checked to say
CC0 by the bank workflow), {BANK_RUN}. Event times are read from `blender.py` (its `T(**seconds)` calls) and `beats.json` at build time. Tonal sounds
(chimes, boings, bowl, glock, triangle) are tuned by resampling to the pitch classes the orchestra is playing at that moment (read from the
recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
""" + "\n".join(lines) + """

## Stand-ins (honest)
""" + "\n".join('- ' + s for s in STANDINS) + """

## Rebuild
`python3 films/cutaway/kids/under-your-feet/audio/make_audio.py` (about a minute; it needs the bank and the recording once).
`$MUSIC_FILE` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
"""
    open(os.path.join(FILM, 'SOUND.md'), 'w').write(md)


# ==================================================================================================================
# 9. MAIN
# ==================================================================================================================
KEY_EVENTS = [('egg cracks', 'crack0'), ('reveal burst', 'reveal0'), ('label CICADA!', 'label0'), ('years race', 'stack0'), ('unhook', 'unhook0'),
              ('finale tutti: out', 'pop0'), ('climb', 'climb0'), ('skin splits', 'crack_shell0'), ('wings open', 'open0'), ('final chord', 'final')]


def main():
    T, bj, WORDS = read_events()
    need = ['birds_waking_3', 'wind_plain', 'cave_soundscape_1', 'chimes_butterfly_1', 'chimes_butterfly_3', 'chimes_dream_1', 'chimes_dream_3', 'cluster_chimes', 'glockenspiel',
            'triangle_2', 'tibetan_bowl_1', 'boing_2', 'boing_4', 'boing_6', 'boing_8', 'toy_squeal_1', 'squeaker_toy_2', 'water_bubble_2', 'wine_stopper_3', 'brush_wood',
            'steps_short_grass', 'steps_twigs', 'steps_pebbles', 'steps_mud', 'steps_leaves', 'candle_sparkle_1', 'candle_sparkle_2', 'ice_crack_2', 'water_over_soil',
            'drops_1', 'drops_2', 'drops_3', 'drops_4', 'metallophone', 'winder_1', 'wind_whistle_2', 'wind_inside_2', 'sun_heat_1', 'heartbeat_5', 'suction_cup_plastic',
            'dig_shovel', 'rusk_crunch', 'cloth', 'dreamcatcher', 'field_cricket', 'solitary_bees', 'old_dog_bark_3', 'flight_bird_1', 'flight_bird_2', 'flight_bird_3',
            'flight_bird_4', 'flight_pigeon', 'robin_1', 'wind_tree_squeaks', 'body_fall_1']
    ensure_bank(need)
    csvp = os.path.join(K.CACHE, 'sfx-bank.csv')
    if not os.path.exists(csvp):
        urllib.request.urlretrieve('https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.csv', csvp)
    mus_raw = music_edit()
    mus, gcur = level_rider(mus_raw, target=-21.0, ratio=2.3)
    F = Film(); F.mus = mus
    design(F, T, WORDS)
    duck = [(0, 0), (74, 0)]
    os.makedirs(HERE, exist_ok=True)
    print('mastering')
    y, musd, fx, res = master(F, mus, duck, fx_trim=FX_TRIM, out_dir=HERE)
    if os.environ.get('KF_STEMS'):                       # for inspection only (never in git)
        os.makedirs(os.environ['KF_STEMS'], exist_ok=True)
        sf.write(os.path.join(os.environ['KF_STEMS'], 'music.wav'), musd, SR, subtype='PCM_24'); sf.write(os.path.join(os.environ['KF_STEMS'], 'fx.wav'), fx, SR, subtype='PCM_24')
    for r in F.rows:
        if 'bed_to' not in r and r.get('peak_db') is not None:
            r['peak_above_music_rms_db'] = round(r['peak_db'] + res['gain_db'] - rms_line(musd, max(0.0, r['t'] - 0.25), min(DUR, r['t'] + 0.5)), 1)
    if '--table' in sys.argv:
        for r in sorted(F.rows, key=lambda r: r['t']):
            print(f"{r['t']:7.2f} {r['name']:<20} {r.get('peak_above_music_rms_db', ''):>6} {r['what'][:60]}")
    lr_all, lr_good = landing_report(F, fx)
    land = [dict(t=r['t'], what=r['what'], onset_ms=r['onset_ms']) for r in F.rows if r.get('onset_ms') is not None and 'bed_to' not in r and not r.get('swell')]
    late = [l for l in land if l['onset_ms'] > 60]
    tl = timeline(y, musd, fx, [(nm, T[k]) for nm, k in KEY_EVENTS])
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(HERE, 'mix.m4a')],
                               capture_output=True, text=True).stdout.strip())
    res['seconds'] = round(dur, 3)
    csvrows = bank_csv()
    edit_info = dict(ratio=2.3, gain_min=float(gcur.min()), gain_max=float(gcur.max()))
    meas = dict(res, codec='aac 256k stereo 48 kHz', target_lufs=TARGET_LUFS, true_peak_limit_dbtp=TP_LIMIT)
    out = dict(
        film='kids-under-your-feet', duration_s=meas['seconds'], measurements=meas,
        music=dict(bj['music'], cut=dict(first=[EDIT['a0'], EDIT['a1']], second=[EDIT['b0'], EDIT['b1']], crossfade_s=EDIT['xf'], crossfade_film_s=[26.1, 27.6], curve='triangular (linear)'),
                   rider=dict(target_lufs=-21.0, ratio=2.3, smoothing_s=1.0, gain_db_range=[round(edit_info['gain_min'], 1), round(edit_info['gain_max'], 1)]), music_only_lufs=round(dsp.loudness(musd), 2)),
        events={k: round(float(v), 3) for k, v in sorted(T.items(), key=lambda x: x[1])},
        recordings={n: dict(uses=u, source=csvrows.get(n, {}).get('source'), licence=csvrows.get(n, {}).get('licence')) for n, u in sorted(F.m.used.items())},
        placements=F.rows, landing_check=dict(by_construction=dict(spots=len(land), latest_onset_ms=max(l['onset_ms'] for l in land), over_60ms=late),
                                              on_the_rendered_effects_bus=dict(checked=len(lr_all), landed=len(lr_good), not_clear=[o for o in lr_all if o not in lr_good])),
        timeline_rms_dbfs=tl, stand_ins=STANDINS, bank_run=BANK_RUN,
        listened=False, note='Built and measured only: nobody has listened to this mix yet.')
    json.dump(out, open(os.path.join(HERE, 'mix.json'), 'w'), indent=1)
    write_sound_md(F, meas, bj, csvrows, edit_info, out['landing_check']['on_the_rendered_effects_bus'])
    print(json.dumps({k: v for k, v in meas.items()}))
    print('landing (by construction): %d spots, latest onset %.1f ms, over 60 ms: %d' % (len(land), max(l['onset_ms'] for l in land), len(late)))
    print('landing (on the rendered effects bus): %d checked, %d within -30..+150 ms and 3 dB over the 300 ms before' % (len(lr_all), len(lr_good)))
    print('timeline (t, mix, music, effects; dBFS per 0.5 s):')
    for r in tl:
        print(f"  {r['event']:<20} @{r['t']:6.2f}:", ' | '.join(f"{a:5.1f}: {m_:5.1f} {mu:5.1f} {e:5.1f}" for a, m_, mu, e in r['windows']))
    return out


if __name__ == '__main__':
    main()
