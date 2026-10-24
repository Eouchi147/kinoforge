#!/usr/bin/env python3
"""Sound of Little Big Questions, film 1 (fossil): a REAL orchestral recording and REAL recorded sound effects (65.0 s).

    python3 films/cutaway/kids/fossil/audio/make_audio.py     # writes audio/mix.m4a, audio/mix.json and ../SOUND.md

What it makes (all deterministic; audio never goes into git, see .gitignore):
  MUSIC   Grieg, Morning Mood, Musopen Symphony (public domain), cut exactly as beats.json says: recording 0:00 to 0:54.5,
          a triangular (linear) cross-fade of 1.5 s (film 53.0 to 54.5) into 3:37.0 to 3:49.0; 65.0 s. The music is the
          voice of the film: foreground. A slow, smooth level rider (no pumping, 1 s smoothing) lifts the whispering opening
          and eases the sunrise climax so the film sits near -16 LUFS; it never touches the notes' shape.
  EFFECTS real CC0 recordings (the studio bank, release sfx-bank of Eouchi147/rc-render, BigSoundBank) placed on the
          picture's events. Event times are READ from films/cutaway/kids/fossil/blender.py (the EVENTS table) and beats.json
          at build time, so a re-timed picture re-times the sound. Soft attacks everywhere, nothing sudden or scary.
  TONAL   the few pitched sounds (bowl, chimes, toy squeak, glock) are tuned by resampling to the pitch classes
          the orchestra plays at that moment (read from the recording; E major, the climax sits on B), so they ring with it.
  MASTER  about -16 LUFS integrated, true peak under -1.5 dBTP (measured on the decoded AAC), 48 kHz stereo AAC 256k.

Needs: numpy, scipy, soundfile, ffmpeg, and the bank (audio_kit finds or downloads it) with the added recordings (bank run of
24 Oct 2026, see SOUND.md). The recording of the music: $MUSIC_FLAC, else ~/.cache/kinoforge/music/, else the public release.
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
FOSSIL = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(FOSSIL, '..', '..', '..', '..'))
SERIES = os.path.join(ROOT, 'films', 'cutaway', 'series')
os.environ['KF_SOUND_DUR'] = '65.0'                      # before audio_kit is imported
sys.path.insert(0, SERIES)
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy.ndimage import gaussian_filter1d  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
import audio_kit as K  # noqa: E402

dsp = K.dsp
SR, N, DUR = K.SR, K.N, K.DUR
db = K.db
MUSIC_URL = 'https://github.com/Eouchi147/rc-render/releases/download/music/grieg-morning-mood-musopen.flac'
MUSIC_CACHE = os.path.expanduser('~/.cache/kinoforge/music/grieg-morning-mood-musopen.flac')


# ==================================================================================================================
# 1. EVENT TIMES: read from the picture's own table (blender.py EVENTS) and beats.json; nothing is typed twice
# ==================================================================================================================
def _num(node):
    return eval(compile(ast.Expression(node), 'events', 'eval'), {'__builtins__': {}})      # numbers and + - * / only


def read_events():
    """{event: seconds} from blender.py's EVENTS table (beat name, fraction of the beat) and beats.json; beats; eras."""
    bj = json.load(open(os.path.join(FOSSIL, 'beats.json')))
    tree = ast.parse(open(os.path.join(FOSSIL, 'blender.py')).read())
    tab = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') in ('EVENTS', 'BEAT_NAMES'):
            tab[n.targets[0].id] = n.value
    names = ast.literal_eval(tab['BEAT_NAMES'])
    beats = {b['name']: (float(b['t'][0]), float(b['t'][1])) for b in bj['beats']}
    ev = {}
    for k, v in zip(tab['EVENTS'].keys, tab['EVENTS'].values):
        beat, u = ast.literal_eval(k), (ast.literal_eval(v.elts[0]), _num(v.elts[1]))
        a, b = beats[names[u[0]]]
        ev[beat] = a + u[1] * (b - a)
    eras = None
    for n in ast.parse(open(os.path.join(FOSSIL, 'szworld.py')).read()).body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'SLOT_ERAS':
            eras = ast.literal_eval(n.value)
    words = [(b['words'].strip(), b['t'][0]) for b in bj['beats'] if b.get('words', '').strip()]
    return ev, beats, eras or ['forest', 'ice', 'mammoth', 'grass', 'forest'], bj, words


# ==================================================================================================================
# 2. THE BANK: make sure the recordings this film needs are there (the bank was extended on 24 Oct 2026)
# ==================================================================================================================
def ensure_bank(names):
    d = K.bank_dir()
    miss = [n for n in names if not os.path.exists(os.path.join(d, n + '.flac'))]
    if miss:
        print('the cached bank lacks', miss[:6], 'so: downloading the current sfx-bank.tar')
        tar = os.path.join(K.CACHE, 'sfx-bank.tar')
        if os.path.exists(tar): os.remove(tar)
        urllib.request.urlretrieve(K.URL, tar + '.part'); os.replace(tar + '.part', tar)
        with tarfile.open(tar) as t: t.extractall(K.CACHE, filter='data')
        K._C.clear()
        miss = [n for n in names if not os.path.exists(os.path.join(K.bank_dir(), n + '.flac'))]
        if miss: raise SystemExit('still missing from the bank: %s' % miss)
    return K.bank_dir()


def bank_csv():
    """name -> source page, from the bank's csv if it sits next to the bank, else from the release."""
    rows = {}
    for p in (os.path.join(K.CACHE, 'sfx-bank.csv'), os.path.join(os.path.dirname(K.bank_dir()), 'sfx-bank.csv')):
        if os.path.exists(p):
            import csv
            for r in csv.DictReader(open(p)): rows[r['name']] = r
            break
    return rows


# ==================================================================================================================
# 3. THE MUSIC: the edit of beats.json, then a slow level rider
# ==================================================================================================================
def music_file():
    p = os.environ.get('MUSIC_FLAC') or MUSIC_CACHE
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        print('downloading the recording (once):', MUSIC_URL)
        urllib.request.urlretrieve(MUSIC_URL, p + '.part'); os.replace(p + '.part', p)
    return p


EDIT = dict(a0=0.0, a1=54.5, b0=217.0, b1=229.0, xf=1.5)          # recording seconds; beats.json music.edit


def music_edit():
    x, sr = sf.read(music_file(), dtype='float32', always_2d=True)
    assert sr == SR, sr
    A = x[int(EDIT['a0'] * SR):int(EDIT['a1'] * SR)]; Bm = x[int(EDIT['b0'] * SR):int(EDIT['b1'] * SR)]
    L = int(EDIT['xf'] * SR); ramp = np.linspace(0, 1, L, dtype=np.float32)[:, None]      # triangular = linear in, linear out
    y = np.concatenate([A[:-L], A[-L:] * (1 - ramp) + Bm[:L] * ramp, Bm[L:]])
    assert abs(len(y) - N) <= 1, (len(y), N)
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
def design(F, T, B, ERAS, WORDS):
    """Every level is `rel`: the clip's peak in dB against the music's RMS around the event (rmsrel / bed rel for steady sounds)."""
    rng = np.random.default_rng(65)
    HY = 1.1                                             # half the block's depth (szworld.SY = 2.2)
    DINO_Y = -HY + 0.50; DINO_LIE_X = 0.20
    DIG = (DINO_LIE_X - 0.10, DINO_Y + 0.02)             # where she brushes (szworld.DIG)
    pan_dino = lambda x: pan_of(x, DINO_Y)
    pan_dig = pan_of(*DIG)
    AUTO = 'auto'                                        # tuned to what the orchestra plays at that moment
    # the places: today's meadow (0 to 5 and from the meadow's return), the fern river, the rain, the cave of the lens
    today = [(0, 0), (5.0, 0), (5.9, -40), (T['green0'] - 0.4, -40), (T['green1'] + 0.8, 0)]
    F.bed('birds_waking_3', 0, 65, rel=-16, start=40, hp=500, env=today, fi=1.5, fo=2.0, label='meadow birds (today)')
    F.bed('wind_plain', 0, 65, rel=-25, start=20, hp=120, lp=3500, env=today, fi=1.5, fo=2.0, label='a soft breeze (today)')
    stp = lambda i: onsets('steps_short_grass')[i % len(onsets('steps_short_grass'))]
    grass = lambda t, rel, p, i, label, length=0.24, lp=3500: F.spot('steps_short_grass', t, rel=rel, at_peak=True, lead=0.015, start=max(0.0, stp(i) - 0.06), length=length,
                                                                    lp=lp, hp=200, fi=0.01, fo=0.12, trim=False, p=p, label=label)

    # ---- hook 0 to 5: the fossil glints (every 1.6 s), the red ball rolls in and stops with a little bounce
    for k, tg in enumerate([0.8, 2.4, 4.0]):
        F.spot('chimes_butterfly_1', tg, rel=-13 - 2 * k, p=-0.15, notes=AUTO, send=-3, fo=0.5, length=1.6, label='the fossil glints')
    b0, b1 = T['ball0'], T['ball1']
    cl = pieces('cloth')
    cl_long = max(cl, key=lambda a: a[1] - a[0])                                    # the longest stretch of rubbing cloth
    F.spot('strong_wind_village', b0, rel=-17, start=69.6, length=b1 - b0, lp=3200, hp=500, fi=0.7, fo=0.8, trim=False, sweep=(-0.55, -0.1), swell=True,
           label='the red ball rolls in on the grass (a soft swish of air stands in)')
    for dt, rl in ((0.0, -8), (0.26, -14)):
        F.spot('boing_2', b1 + dt, rel=rl, p=-0.15, notes=AUTO, lp=3500, fi=0.02, fo=0.25, length=0.6, label='the ball stops with a little bounce')

    # ---- rewind 5 to 10: reversed whooshes scrub back through time, a wind of years, a rising shimmer, the clock spinning back
    for nm, te, rl in (('whoosh_8', T['rw0'] + 0.6, -9), ('whoosh_3', 6.55, -7), ('whoosh_7', 7.35, -5), ('whoosh_4', 8.15, -4), ('whoosh_5', T['peel1'], -2)):
        F.spot(nm, te, rel=rl, rev=True, p=0.1 * (te % 2 - 1), lp=7500, fi=0.04, fo=0.08, swell=True, label='time runs backwards (a reversed whoosh)')
    F.bed('wind_whistle_2', T['rw0'] + 0.1, T['rw1'] + 0.3, rel=-14, start=3, hp=300, lp=4500, env=[(5.0, -30), (7.5, -3), (9.4, 0), (10.3, -30)], fi=0.3, fo=0.5,
          label='a wind of passing years')
    for te, rl, pn in ((7.5, -9, -0.3), (8.7, -7, 0.3), (T['rw1'] - 0.2, -5, 0.0)):
        F.spot('chimes_butterfly_3', te, rel=rl, rev=True, notes=AUTO, send=-3, fi=0.3, fo=0.25, p=pn, swell=True, label='a rising shimmer as time runs back (reversed chimes)')
    F.spot('winder_1', T['rw1'] - 0.2, rel=-8, rev=True, hp=500, lp=5000, length=4.2, fi=0.8, fo=0.4, p=0.35, swell=True, label='the clock spins backwards (a music-box winder, reversed)')
    F.bed('steps_leaves', T['fern0'], T['fern1'] + 0.5, rel=-24, hp=800, lp=5000, p=0.2, fi=1.2, fo=0.8, label='ferns unfurl (leaf rustle)')

    # ---- the living world 10 to 21: the river, the long-neck's heavy gentle steps, munching, baby splashes, far life
    F.bed('watercourse_1', T['rw1'] - 1.5, 26.0, rel=-15, start=12, hp=150, lp=7000, p=-0.1, fi=2.5, fo=2.0,
          env=[(8.5, -30), (10.5, 0), (21.0, 0), (22.5, -9), (25.0, -9), (26.0, -24)], label='the river')
    foot_times = lambda a, b: [(0.25 + 0.5 * k) / 1.1 for k in range(0, 400) if a <= (0.25 + 0.5 * k) / 1.1 < b]     # szlife.dino_pose: walk = 2 pi 1.1 t

    def dino_steps(a, b, rel, label):
        ow, om = onsets('steps_wood_floor'), onsets('steps_mud')
        for j, tf in enumerate(foot_times(a, b)):
            xw = -1.7 + 0.9 * min(1.0, max(0.0, (tf - a) / (b - a))); pn = pan_dino(xw); r_ = rel - 1.0 * (j % 2)
            F.spot('steps_wood_floor', tf, rel=r_, at_peak=True, lead=0.025, start=max(0.0, ow[j % len(ow)] - 0.06), length=0.7, speed=0.55, lp=420, hp=40, fi=0.02, fo=0.3,
                   p=pn, trim=False, label=label)
            F.spot('steps_mud', tf, rel=r_ - 6, at_peak=True, lead=0.02, start=max(0.0, om[(j * 3) % len(om)] - 0.06), length=0.5, speed=0.7, lp=1800, hp=100, fi=0.02, fo=0.25,
                   p=pn, trim=False, label=label + ' (wet leaf and mud)')

    dino_steps(T['walk0'] + 0.1, T['walk1'], -3, 'the long-neck walks to the ferns')
    # munching: a bite when the neck is lowest in the ferns, then three slow chews while it lifts (szlife: every 2.2 s)
    pm = pan_dino(-0.8); k = 0; tb = T['munch0'] + 1.1
    while tb < T['munch1'] - 0.2:
        for j, (dt, rl) in enumerate(((0.0, -4), (0.42, -9), (0.80, -9), (1.18, -11))):
            nm = ('carrot_crunch', 'apple_crunch_1', 'apple_crunch_2')[(k + j) % 3]; on = onsets(nm)
            F.spot(nm, tb + dt, rel=rl, at_peak=True, lead=0.02, start=max(0.0, on[(k * 4 + j) % len(on)] - 0.06), length=0.6, speed=0.62, lp=3200, hp=90, fi=0.015, fo=0.2,
                   p=pm, trim=False, label='munching the ferns' if j == 0 else 'chew')
        k += 1; tb += 2.2
    # two babies splash, a hop every 1.6 s; the landing is the splash (szstory.babies_pose: both land together)
    for n, ts in enumerate([0.26 + 1.6 * q for q in range(0, 30) if T['fern1'] - 1.5 < 0.26 + 1.6 * q < T['leave0']]):
        for b, (xw, yw) in enumerate(((0.95, -0.17), (0.55, -0.24))):
            nm = ('splash_small_1', 'splash_small_2', 'splash_small_3', 'splash_small_4', 'splash_small_5', 'splash_small_6')[(2 * n + b) % 6]
            F.spot(nm, ts + 0.05 * b, rel=-7 - 3 * b, at_peak=True, lead=0.015, p=pan_of(xw, yw), length=1.1, speed=1.15 if b else 1.0, hp=300, lp=9000, fi=0.01, fo=0.5,
                   label='a baby splashes')
    for tt, p_ in ((13.5, -0.5), (16.9, 0.45)):
        F.spot('bumblebee_2', tt, rel=-17, p=p_, start=3.0, length=2.4, hp=400, lp=4500, speed=1.3, fi=0.8, fo=0.8, trim=False, swell=True, label='a dragonfly hums past')
    F.spot('flight_bird_2', 14.6, rel=-15, sweep=(-0.7, 0.5), length=2.2, lp=5000, speed=0.8, fo=0.6, swell=True, label='a pterosaur glides over the hills')
    F.spot('goat_bleat_1', 17.2, rel=-19, p=0.55, speed=0.45, lp=1600, hp=150, fi=0.15, fo=0.8, send=-3, swell=True, label='a far soft call (a slowed goat stands in)')
    for j in range(8):
        grass(T['turtle0'] + 0.6 + 1.5 * j, -17, 0.4, 3 * j + 1, 'the turtle plods (tiny steps)', length=0.3, lp=2500)

    # ---- the old dinosaur rests 21 to 25: the world goes hushed
    dino_steps(T['towater0'], T['towater1'] - 0.2, -5, 'the old one walks to the bank')
    ow = onsets('steps_wood_floor')
    F.spot('steps_wood_floor', T['lie0'] + 0.75, rel=-3, at_peak=True, lead=0.03, start=ow[2] - 0.06, length=1.0, speed=0.42, lp=300, hp=30, fi=0.04, fo=0.45, p=pan_dino(0.2),
           trim=False, label='the long-neck lies down')
    F.spot('body_fall_1', T['lie0'] + 0.8, rel=-9, at_peak=True, lead=0.03, speed=0.55, lp=700, hp=60, fi=0.03, fo=0.4, p=pan_dino(0.2), trim=False, label='it settles on the bank')
    F.spot('wind_inside_1', T['curl0'] - 0.2, rel=-14, start=10, length=3.4, hp=100, lp=2500, fi=1.3, fo=1.4, trim=False, swell=True,
           label='a long soft exhale of wind, the world hushes')
    F.spot('robin_1', 22.0, rel=-18, p=0.6, lp=6000, fi=0.05, fo=0.5, send=-4, label='one bird')
    for j in range(6):
        grass(T['leave0'] + 0.2 + 0.5 * j, -13 - j, -0.3 - 0.05 * j, 5 + j, 'the babies walk off')
    F.spot('paper', T['leaf1'] - 0.25, rel=-22, start=3.0, length=0.45, hp=1500, lp=7000, fi=0.1, fo=0.2, p=0.1, trim=False, swell=True, label='one leaf lands')

    # ---- mud covers the bones 25 to 30: rain begins, a gentle flood, a wet squelch as each mud wave settles
    F.bed('rain_puddle', T['rainA0'], T['stack0'], rel=-14, start=8, hp=200, lp=9000, env=[(25.0, -30), (26.0, 0), (29.0, 0), (30.0, -30)], fi=0.5, fo=0.8, label='rain begins')
    F.bed('small_cascade', T['flood0'], T['stack0'] + 0.5, rel=-19, start=4, hp=120, lp=3200, p=-0.1,
          env=[(25.4, -30), (26.6, 0), (27.6, -3), (28.5, 0), (29.75, -6), (30.5, -30)], fi=0.8, fo=0.8, label='the flood spreads')
    om = onsets('steps_mud')
    for k, tm in enumerate([T['flood1'], T['skel1'], T['mud0'] + 0.9, T['mud1'], T['flood3']]):
        pn = (-0.2, 0.15, -0.1, 0.2, 0.0)[k]
        F.spot('water_over_soil', tm - 0.25, rel=-15, start=1.2 * k, length=1.2, lp=2600, hp=100, fi=0.25, fo=0.5, p=pn, trim=False, swell=True, label='a wave of mud spreads')
        F.spot('steps_mud', tm, rel=-7, at_peak=True, lead=0.02, start=om[(4 * k + 1) % len(om)] - 0.06, length=0.6, speed=0.7, lp=1500, hp=100, fi=0.02, fo=0.35, p=pn,
               trim=False, label='a wet squelch as the mud settles')

    # ---- layer on layer 30 to 38: each layer is brought by a short flood and lands with a soft thud, then its era races by
    d5 = (T['stack1'] - T['stack0']) / 5
    SL = [(T['stack0'] + d5 * (i + 0.08), T['stack0'] + d5 * (i + 0.30)) for i in range(5)]          # szworld.set_events: the slots
    for i, (sa, sb) in enumerate(SL):
        F.spot('swirl_water', sa, rel=-15, start=0.9 * i + 0.2, length=sb - sa + 0.12, lp=3000, hp=150, fi=0.12, fo=0.12, trim=False, p=-0.15, swell=True,
               label='a short flood brings a layer')
        F.spot('steps_wood_floor', sb, rel=-2 - 0.3 * i, at_peak=True, lead=0.03, start=ow[(3 * i + 1) % len(ow)] - 0.06, length=0.9, speed=0.5, lp=380, hp=35, fi=0.03, fo=0.35,
               trim=False, p=-0.1, label='a layer lands (soft thud)')
        F.spot('steps_mud', sb, rel=-9, at_peak=True, lead=0.02, start=om[(5 * i + 2) % len(om)] - 0.06, length=0.5, speed=0.8, lp=1500, hp=90, fi=0.02, fo=0.3, trim=False, p=-0.1,
               label='a layer lands (damp settle)')
        e0 = sb + 0.12; e1 = (T['stack0'] + d5 * (i + 1) + 0.05) if i < 4 else T['stack1']
        era = ERAS[i]
        if era == 'forest':
            F.bed('forest', e0, e1, rel=-14, start=5 * i, hp=300, lp=6000, fi=0.25, fo=0.25, xf=0.2, p=0.1, label='a forest era races by (leaves and birds)')
        elif era == 'ice':
            F.bed('wind_whistle_2', e0, e1, rel=-15, start=5, hp=250, lp=5000, fi=0.25, fo=0.25, xf=0.2, label='an ice era races by (cold wind)')
            osn = onsets('steps_snow_1')
            for j in range(3):
                F.spot('steps_snow_1', e0 + 0.2 + 0.4 * j, rel=-13, at_peak=True, lead=0.015, start=max(0.0, osn[(j * 2) % len(osn)] - 0.06), length=0.3, lp=4500, fi=0.01, fo=0.12,
                       trim=False, p=-0.3 + 0.3 * j, label='snow crunch')
        elif era == 'mammoth':
            for j, tm in enumerate((e0 + 0.15, e0 + 0.75, e0 + 1.3)):
                F.spot('steps_wood_floor', tm, rel=-8 - j, at_peak=True, lead=0.03, start=ow[(2 * j) % len(ow)] - 0.06, length=0.9, speed=0.42, lp=300, hp=30, fi=0.04, fo=0.4,
                       p=-0.45 + 0.45 * j, trim=False, send=-6, label='mammoths cross the steppe (far soft footfalls)')
            F.spot('goat_bleat_2', e0 + 0.4, rel=-16, p=0.3, speed=0.4, lp=1300, hp=120, fi=0.12, fo=0.7, send=-4, swell=True, label='a far mammoth call (a slowed goat stands in)')
        else:   # grass
            F.bed('strong_wind_village', e0, e1, rel=-15, start=20, hp=200, lp=3500, fi=0.25, fo=0.25, xf=0.2, label='grassland era races by (grass in the wind)')

    # ---- bone to stone 38 to 44: a round window opens, slow drips and tiny crystal tinkles, a glow swells to the hit on 43.0
    F.bed('cave_1', T['stack1'], T['lens3'] + 0.6, rel=-20, start=10, hp=120, lp=7000, fi=0.6, fo=0.9, send=-6, label='a cave-like hush inside the window')
    F.spot('water_bubble_2', T['lens0'] + 0.1, rel=-10, at_peak=True, lead=0.01, length=0.5, p=0.0, lp=5000, fo=0.3, send=-4, trim=False,
           label='the round window opens (a soft bubble)')
    drip_t = []; tt = T['seep0'] + 0.3
    while tt < T['seep1'] + 0.3:
        drip_t.append(tt); tt += float(rng.uniform(0.62, 1.05))
    for j, tt in enumerate(drip_t):
        nm = ('drops_1', 'drops_2', 'drops_4', 'drops_3')[j % 4]; pc = pieces(nm); pa = pc[(2 * j) % min(8, len(pc))]
        F.spot(nm, tt, rel=-6, at_peak=True, lead=0.01, start=max(0.0, pa[0] - 0.03), length=0.5, hp=500, lp=7000, fi=0.01, fo=0.3, p=float(rng.uniform(-0.25, 0.25)), send=-2,
               trim=False, label='a drop seeps in')
        F.spot('chimes_dream_1', tt + 0.22, rel=-11, length=1.5, notes=AUTO, lp=9000, hp=700, fi=0.01, fo=0.9, p=float(rng.uniform(-0.3, 0.3)), send=-2,
               label='a crystal sparkle where a drop lands')
    th = T['hit']
    F.spot('tibetan_bowl_1', th, rel=-6, at_peak=True, lead=0.0, notes=F.auto_notes(40.0, dur=6.0, kmax=2), lp=5500, fi=0.05, fo=3.5, length=46.5 - 37.7, trim=False, send=-2, swell=True,
           label='THE HIT: the stone glows (a singing bowl swells to the hit)')
    F.spot('hammer_concrete', th, rel=-7, at_peak=True, lead=0.01, speed=0.6, lp=900, hp=60, fi=0.015, fo=0.25, length=0.5, trim=False, label='THE HIT: a soft stone tok')
    cw = loud_windows('cluster_chimes', 2.5, 1, hop=0.5, start=0.0, stop=120.0)[0]
    F.spot('cluster_chimes', th + 0.03, rel=-9, start=cw, length=2.6, notes=AUTO, lp=10000, fi=0.08, fo=1.4, send=-2, trim=False, swell=True, label='THE HIT: a burst of gold stars')
    F.spot('water_bubble_2', T['lens2'] + 0.35, rel=-12, rev=True, start=0.0, length=0.5, lp=5000, fo=0.2, send=-4, swell=True, label='the window closes (a soft bubble, reversed)')

    # ---- the land wears away 44 to 47: wind gusts, rain, small grit trickles; the meadow returns
    F.bed('rain_concrete', T['rain0'], T['rain1'] + 0.4, rel=-16, start=10, hp=300, lp=9000, fi=0.4, fo=0.8, label='rain wears the land')
    F.bed('strong_wind_1', T['rain0'] - 0.2, T['erode1'] + 0.5, rel=-18, start=10, hp=120, lp=4200, p=0.1,
          env=[(43.8, -20), (44.6, 0), (45.1, -6), (45.8, 0), (46.5, -8), (46.9, -30)], fi=0.4, fo=0.6, label='wind gusts')
    of = onsets('fall_of_stone')
    for k, tm in enumerate((44.5, 45.1, 45.7, 46.2)):
        F.spot('fall_of_stone', tm, rel=-16, at_peak=True, lead=0.01, start=of[(2 * k + 1) % len(of)] - 0.04, length=0.7, hp=500, lp=4500, fi=0.02, fo=0.3, p=(-0.4, 0.3, -0.2, 0.4)[k],
               trim=False, label='a small trickle of grit')

    # ---- the find 47 to 54.5: she runs in, kneels, brush brush; the bone appears with FOSSIL! on 49.5; she jumps for joy
    g0, g1 = T['girl0'], T['girl1']
    pth = [(-2.60, -0.55), (-1.40, -0.60), (-0.75, -0.66), (DIG[0] - 0.24, DIG[1] - 0.15)]      # szlife.girl_pose
    nstep = int((g1 - g0) / 0.21)
    for j in range(nstep):
        tf = g0 + 0.10 + 0.21 * j; u = j / max(1, nstep - 1); q = u * (len(pth) - 1); a = int(min(len(pth) - 2, q)); f = q - a
        px = pth[a][0] + (pth[a + 1][0] - pth[a][0]) * f; py = pth[a][1] + (pth[a + 1][1] - pth[a][1]) * f
        grass(tf, -9 + 3 * float(np.sin(np.pi * u)) - 4, pan_of(px, py), 11 + j, 'she runs in over the grass', length=0.22)
    F.spot('cloth', T['kneel0'] + 0.1, rel=-17, start=cl_long[0] + 1.0, length=0.55, hp=400, lp=4500, fi=0.15, fo=0.25, p=pan_dig, trim=False, swell=True, label='she kneels (cloth rustle)')
    F.bed('dogs_breathing', g0 + 0.3, T['cheer0'] + 0.5, rel=-24, start=2.0, hp=500, lp=4000, p=0.5, fi=0.8, fo=0.6, label='the dog pants as it runs about')
    # brush, brush: one stroke at every turn of her wrist (szlife.girl_pose: the brush swings at 2.2 Hz, a stroke every 1/4.4 s)
    b0, b1 = T['brush0'], T['brush1']
    strokes = [k / 4.4 for k in range(int(b0 * 4.4), int(b1 * 4.4) + 2) if b0 - 0.05 <= k / 4.4 <= b1 + 0.02]
    wins = loud_windows('brush_concrete', 0.30, len(strokes) + 2, hop=0.3, start=0.5)
    for j, ts in enumerate(strokes):
        u = (ts - b0) / max(0.1, b1 - b0)
        F.spot('brush_concrete', ts, rel=-6 + 4 * u, at_peak=True, lead=0.0, start=wins[j % len(wins)], length=0.30, hp=350, lp=7500, fi=0.07, fo=0.12, trim=False, p=pan_dig + 0.05,
               label='brush stroke')
    # FOSSIL! on the full-orchestra climax at 49.5: the bone appears, a bright soft ta-da made of real chimes, a triangle and a glock
    tf0 = T['pit1']
    F.spot('chimes_butterfly_1', tf0, rel=-3, notes=AUTO, lp=10000, fi=0.03, fo=1.4, send=-2, p=0.1, label='FOSSIL! the bone appears (chimes)')
    F.spot('glockenspiel', tf0 + 0.06, rel=-6, start=0.0, speed=2 ** (4 / 12), lp=9000, fi=0.02, fo=1.8, length=2.8, send=-3, p=-0.1, label='FOSSIL! sparkle (a struck glockenspiel chord, raised to B7)')
    F.spot('triangle_2', tf0 + 0.02, rel=-9, notes=AUTO, lp=9000, fi=0.03, fo=1.8, length=3.0, send=-3, p=0.15, label='FOSSIL! a soft triangle')
    c0 = T['cheer0']
    for k_, tl in enumerate((c0 + 0.30, c0 + 0.90)):
        grass(tl, -15, pan_dig, 17 + k_, 'she lands, jumping for joy', length=0.25)
    F.spot('cloth', c0, rel=-18, start=cl_long[0] + 1.5, length=1.2, hp=400, lp=4500, fi=0.1, fo=0.3, trim=False, p=pan_dig, swell=True, label='arms up (cloth)')
    for k_, tb in enumerate((T['flyup0'], T['flyup0'] + 0.12, T['flyup0'] + 0.3)):
        F.spot(('flight_bird_1', 'flight_pigeon', 'flight_bird_2')[k_], tb, rel=-14 - k_, sweep=(0.2, 0.9), length=1.6, lp=7000, hp=250, fo=0.5, swell=True, label='birds fly up from the big tree')
    bk = onsets('old_dog_bark_3')
    for k_, (tb, rl, sp) in enumerate(((c0 + 0.18, -6, 1.25), (c0 + 0.80, -8, 1.3), (c0 + 1.9, -12, 1.2))):
        F.spot('old_dog_bark_3', tb, rel=rl, at_peak=True, lead=0.02, start=max(0.0, bk[(2 * k_) % len(bk)] - 0.06), length=0.3, speed=sp, lp=3800, hp=250, fi=0.015, fo=0.12,
               p=0.55 - 0.15 * k_, trim=False, label='the dog barks happily')

    # ---- the send-off 54.5 to 65: the ball rolls back, the toy is lifted on the final swell, the snail waves
    r0, r1 = T['ballback0'], T['ballback1']
    F.spot('strong_wind_village', r0, rel=-17, start=69.0, length=r1 - r0, lp=3200, hp=500, fi=0.7, fo=0.8, trim=False, sweep=(-0.5, -0.05), swell=True,
           label='the red ball rolls back (a soft swish of air stands in)')
    for dt, rl in ((0.0, -8), (0.26, -14)):
        F.spot('boing_2', r1 + dt, rel=rl, p=-0.1, notes=AUTO, lp=3500, fi=0.02, fo=0.25, length=0.6, label='the ball stops with a little bounce')
    h0, h1 = T['hold0'], T['hold1']
    F.spot('cloth', h0 + 0.2, rel=-18, start=cl_long[0] + 2.0, length=2.2, hp=400, lp=4500, fi=0.4, fo=0.5, trim=False, p=pan_dig, swell=True, label='she lifts her arm (cloth)')
    F.spot('toy_duck', h0 + 1.5, rel=-10, start=1.45, notes=AUTO, lp=6000, fi=0.03, fo=0.35, length=0.6, p=pan_dig, label='the toy dinosaur squeaks as it is lifted')
    F.spot('chimes_dream_3', h1 - 0.5, rel=-11, notes=AUTO, lp=9000, fi=0.04, fo=1.8, length=3.0, send=-3, p=0.1, label='the toy reaches the top: a small twinkle')
    F.spot('boing_4', T['wave0'], rel=-12, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.7, p=0.55, label='the snail waves')
    F.spot('robin_1', 62.6, rel=-18, p=-0.4, lp=6000, fi=0.05, fo=0.6, send=-4, label='a bird calls over the last chord')

    # ---- words in with a soft pop (every word set in code); FOSSIL! has its own sparkle above
    for w, tw in WORDS:
        if w.startswith('FOSSIL'): continue
        tw_in = T['words_send'] if w.startswith('WHAT') else tw + 0.35
        F.spot('wine_stopper_3', tw_in, rel=-15, notes=None, lp=4500, hp=300, fi=0.01, fo=0.2, p=0.0, label='words pop in: ' + w.lower())
    return dict(climax=tf0, hit=th, brush=(b0, b1), strokes=strokes)


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
    'The red ball rolls on a soft swish of air (a band-passed village wind): the bank has no rolling ball. Its stop is two soft harp "boings", tuned to the music.',
    'The long-neck\'s footfalls are a slowed, low-passed wooden step with a slowed mud step on top: there is no recording of a giant. It will read as a heavy soft footfall, not as a dinosaur.',
    'Munching is a slowed raw carrot and apple crunch (a plant eater\'s mouth made large by slowing).',
    'Lying down is a slowed low-passed wooden step and a slowed body fall; the "exhale" is a swell of real wind inside a hall (no breath, on purpose: nothing to read as a sigh of death).',
    'The far soft call (17 s) and the far mammoth call (34 s) are slowed goat bleats, low-passed, far away and very quiet: there is no dinosaur or mammoth in any recording.',
    'Dragonflies are a bumblebee\'s hum passing; the pterosaur is a small bird\'s wings, slowed.',
    'The dog is an old dog\'s real barks, played a little faster so it sounds younger and happier: the nearest recording the bank has.',
    'The stone hit is a singing bowl that swells to the hit, a slowed low-passed hammer on concrete and a burst of real chimes: a blend for a magic moment, not a real stone.',
    'The rewind is real whooshes, chimes and a music-box winder played backwards, with a wind of years.',
    'The glockenspiel is a struck G7 chord raised a major third to B7 (the dominant of the key, over the climax); it is a real recording shifted, not played on a glockenspiel in B.',
    'Words pop in with a wine stopper\'s pop.',
]


def write_sound_md(F, meas, bj, csvrows, edit_info, chk):
    use = {}
    for r in F.rows:
        d = use.setdefault(r['name'], {})
        key = r['what']; d.setdefault(key, []).append(r['t'])
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
    md = f"""# Sound of the fossil film (Little Big Questions, film 1)

A SILENT 65 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
Audio never goes into git: `audio/mix.m4a` and `audio/mix.wav` are ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** {m['credit']}

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- {meas['seconds']:.2f} s, 48 kHz stereo AAC 256k, {meas['lufs']:.1f} LUFS integrated (target {TARGET_LUFS:.0f}), true peak {meas['true_peak']:.2f} dBTP (limit {TP_LIMIT} dBTP), loudness range {meas['lra']:.1f} LU.
- The loudest limiter dip is {meas['limiter_max_reduction_db']:.1f} dB at {meas['limiter_max_reduction_at_s']:.1f} s (the sunrise climax); the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; the loudest instant of a footfall, bite or splash sits 10 to 35 ms after the event
  frame, a brush stroke on its turn). On the rendered effects bus alone, {chk['landed']} of {chk['checked']} percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under the river, rain or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
{m['piece']}, {m['recording']}, {m['licence']}. Source: {m['source']}. Asset: {m['asset']}.
Recording 0:00 to 0:54.5, a triangular (linear in, linear out) cross-fade of 1.5 s (film 53.0 to 54.5) into recording
3:37.0 to 3:49.0; 65.0 s. The music leads. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio {edit_info['ratio']},
gain between {edit_info['gain_min']:+.1f} and {edit_info['gain_max']:+.1f} dB) lifts the whispering opening and eases the sunrise climax so the film can sit near
-16 LUFS; the notes keep their own shape. The music is lowered by at most {edit_info['duck_db']:.1f} dB under the brush strokes, the FOSSIL! sparkle and the stone hit.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). The bank was extended for this film with 64 more BigSoundBank ids from
`docs/research/KIDS_MUSIC_2026-10.md` section 5.1 (soft boings, chimes, bowls, soft steps, crunches, brushes, splashes):
{BANK_RUN}. Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowl, chimes, glock, toy squeak, boings) are tuned by resampling to the
pitch classes the orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
""" + "\n".join(lines) + f"""

## Stand-ins (honest)
""" + "\n".join('- ' + s for s in STANDINS) + """

## Rebuild
`python3 films/cutaway/kids/fossil/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
"""
    open(os.path.join(FOSSIL, 'SOUND.md'), 'w').write(md)


# ==================================================================================================================
# 9. MAIN
# ==================================================================================================================
KEY_EVENTS = [('ball stops (hook)', 'ball1'), ('rewind', 'rw0'), ('peel ends', 'peel1'), ('first footstep', 'walk0'), ('first bite', 'munch0'),
              ('lies down', 'lie0'), ('flood', 'flood1'), ('mud settles', 'mud1'), ('layer 3 lands', None), ('the hit', 'hit'),
              ('brush starts', 'brush0'), ('FOSSIL!', 'pit1'), ('ball back', 'ballback1'), ('toy lift', 'hold0'), ('toy top', 'hold1'), ('last words', 'words_send')]


def main():
    T, B, ERAS, bj, WORDS = read_events()
    need = ['birds_waking_3', 'wind_plain', 'chimes_butterfly_1', 'chimes_butterfly_3', 'chimes_dream_1', 'chimes_dream_3', 'cluster_chimes', 'glockenspiel',
            'triangle_2', 'tibetan_bowl_1', 'boing_2', 'boing_4', 'toy_duck', 'water_bubble_2', 'wine_stopper_3', 'brush_concrete', 'carrot_crunch',
            'apple_crunch_1', 'apple_crunch_2', 'steps_short_grass', 'running_tall_grass', 'steps_snow_1', 'steps_leaves', 'steps_leaves_2',
            'splash_small_2', 'splash_small_3', 'splash_small_4', 'splash_small_5', 'splash_small_6', 'swirl_water', 'water_over_soil', 'whoosh_long_1']
    bank = ensure_bank(need)
    csvp = os.path.join(K.CACHE, 'sfx-bank.csv')
    if not os.path.exists(csvp):
        urllib.request.urlretrieve('https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.csv', csvp)
    mus_raw = music_edit()
    mus, gcur = level_rider(mus_raw, target=-21.0, ratio=2.3)
    F = Film(); F.mus = mus
    info = design(F, T, B, ERAS, WORDS)
    brush0, brush1 = info['brush']; climax = info['climax']; hit = info['hit']
    duck_db = -1.5
    duck = [(0, 0), (hit - 0.15, 0), (hit + 0.05, -1.0), (hit + 1.2, 0), (brush0 - 0.25, 0), (brush0 + 0.15, duck_db), (brush1, duck_db), (climax + 0.12, -0.8),
            (climax + 2.0, -1.0), (climax + 3.0, 0), (65, 0)]
    os.makedirs(HERE, exist_ok=True)
    print('mastering')
    y, musd, fx, res = master(F, mus, duck, fx_trim=FX_TRIM, out_dir=HERE)
    if os.environ.get('KF_STEMS'):                       # for inspection only (never in git): the music and the effects as the mix has them
        os.makedirs(os.environ['KF_STEMS'], exist_ok=True)
        sf.write(os.path.join(os.environ['KF_STEMS'], 'music.wav'), musd, SR, subtype='PCM_24'); sf.write(os.path.join(os.environ['KF_STEMS'], 'fx.wav'), fx, SR, subtype='PCM_24')
    # the checks: every spot lands on its event (the clip speaks within a few ms of t), loudness, a 0.5 s RMS timeline
    for r in F.rows:
        if 'bed_to' not in r and r.get('peak_db') is not None:
            r['peak_above_music_rms_db'] = round(r['peak_db'] + res['gain_db'] - rms_line(musd, max(0.0, r['t'] - 0.25), min(DUR, r['t'] + 0.5)), 1)
    if '--table' in sys.argv:
        for r in sorted(F.rows, key=lambda r: r['t']):
            print(f"{r['t']:7.2f} {r['name']:<20} {r.get('peak_above_music_rms_db', ''):>6} {r['what'][:60]}")
    lr_all, lr_good = landing_report(F, fx)
    land = [dict(t=r['t'], what=r['what'], onset_ms=r['onset_ms']) for r in F.rows if r.get('onset_ms') is not None and 'bed_to' not in r and not r.get('swell')]
    late = [l for l in land if l['onset_ms'] > 60]
    ev_list = []
    for nm, k in KEY_EVENTS:
        ev_list.append((nm, T[k] if k else T['stack0'] + 2 * (T['stack1'] - T['stack0']) / 5 + 0.3))
    tl = timeline(y, musd, fx, ev_list)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(HERE, 'mix.m4a')],
                               capture_output=True, text=True).stdout.strip())
    res['seconds'] = round(dur, 3)
    csvrows = bank_csv()
    edit_info = dict(ratio=2.3, gain_min=float(gcur.min()), gain_max=float(gcur.max()), duck_db=abs(duck_db))
    meas = dict(res, codec='aac 256k stereo 48 kHz', target_lufs=TARGET_LUFS, true_peak_limit_dbtp=TP_LIMIT)
    out = dict(
        film='kids-fossil', duration_s=meas['seconds'], measurements=meas,
        music=dict(bj['music'], cut=dict(first=[EDIT['a0'], EDIT['a1']], second=[EDIT['b0'], EDIT['b1']], crossfade_s=EDIT['xf'], crossfade_film_s=[53.0, 54.5],
                                          curve='triangular (linear)'), rider=dict(target_lufs=-21.0, ratio=2.3, smoothing_s=1.0, gain_db_range=[round(edit_info['gain_min'], 1), round(edit_info['gain_max'], 1)]),
                   duck_points_db=duck, music_only_lufs=round(dsp.loudness(musd), 2)),
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
    print('landing (on the rendered effects bus): %d checked, %d peak within -30..+150 ms of the event and 3 dB over the 300 ms before' % (len(lr_all), len(lr_good)))
    for o in lr_all:
        if o not in lr_good: print('   not clear:', o)
    if '--full' in sys.argv:
        print('per second (mix, music, effects RMS dBFS, and the loudest effect peak dB over the music RMS):')
        for t in range(0, 65):
            pk = max([r['peak_above_music_rms_db'] for r in F.rows if 'peak_above_music_rms_db' in r and t <= r['t'] < t + 1] or [None], key=lambda v: -99 if v is None else v)
            print(f'  {t:2d}-{t + 1:2d}  mix {rms_line(y, t, t + 1):6.1f}  music {rms_line(musd, t, t + 1):6.1f}  fx {rms_line(fx, t, t + 1):6.1f}   gap {rms_line(musd, t, t + 1) - rms_line(fx, t, t + 1):5.1f} dB   top spot {pk}')
    print('timeline (t, mix, music, effects; dBFS per 0.5 s):')
    for r in tl:
        print(f"  {r['event']:<20} @{r['t']:6.2f}:", ' | '.join(f"{a:5.1f}: {m_:5.1f} {mu:5.1f} {e:5.1f}" for a, m_, mu, e in r['windows']))
    return out


if __name__ == '__main__':
    main()
