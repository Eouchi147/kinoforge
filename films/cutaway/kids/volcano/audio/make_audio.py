#!/usr/bin/env python3
"""Sound of Little Big Questions, HOW IS A VOLCANO BORN? (volcano): a REAL orchestral recording and REAL recorded sound effects (72.3 s).

    python3 films/cutaway/kids/volcano/audio/make_audio.py     # writes audio/mix.m4a, audio/mix.json and ../SOUND.md

What it makes (all deterministic):
  MUSIC   Grieg, In the Hall of the Mountain King, Musopen Symphony (public domain), cut exactly as beats.json says (four
          pieces on rests of the music, triangular cross-fades of 0.5, 1.0 and 1.0 s; 72.3 s). The music is the voice of the
          film: foreground. A slow, smooth level rider (no pumping, 1 s smoothing) lifts the whispering opening and eases the
          tutti so the film sits near -16 LUFS; it never touches the notes' shape.
  EFFECTS real CC0 recordings (the studio bank, release sfx-bank of Eouchi147/rc-render, BigSoundBank) placed on the
          picture's events. Event times are READ from films/cutaway/kids/volcano/blender.py (the EVENTS table) and beats.json
          at build time, so a re-timed picture re-times the sound. Soft attacks everywhere, nothing sudden or scary.
  TONAL   the pitched sounds (bowl, chimes, boings, bubbles, plant pops) are tuned by resampling to the pitch classes
          the orchestra plays at that moment (read from the recording), so they ring with it.
  MASTER  about -16 LUFS integrated, true peak under -1.5 dBTP (measured on the decoded AAC), 48 kHz stereo AAC 256k.

Needs: numpy, scipy, soundfile, ffmpeg, and the bank (audio_kit finds or downloads it). The recording of the music:
$MUSIC_FLAC, else ~/.cache/kinoforge/music/, else the public release.
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
os.environ['KF_SOUND_DUR'] = '72.3'                      # before audio_kit is imported
sys.path.insert(0, SERIES)
sys.path.insert(0, FILM)
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy.ndimage import gaussian_filter1d  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
import audio_kit as K  # noqa: E402
import szworld as W  # noqa: E402   (pure numpy: the world's own numbers, so the stereo positions are the picture's)

dsp = K.dsp
SR, N, DUR = K.SR, K.N, K.DUR
db = K.db
MUSIC_URL = 'https://github.com/Eouchi147/rc-render/releases/download/music/grieg-mountain-king-musopen.flac'
MUSIC_CACHE = os.path.expanduser('~/.cache/kinoforge/music/grieg-mountain-king-musopen.flac')


# ==================================================================================================================
# 1. EVENT TIMES: read from the picture's own table (blender.py EVENTS) and beats.json; nothing is typed twice
# ==================================================================================================================
def _num(node):
    return eval(compile(ast.Expression(node), 'events', 'eval'), {'__builtins__': {}})      # numbers and + - * / only


def read_events():
    """{event: seconds} from blender.py's EVENTS table (beat name, fraction of the beat) and beats.json; beats; words; dolphins."""
    bj = json.load(open(os.path.join(FILM, 'beats.json')))
    tree = ast.parse(open(os.path.join(FILM, 'blender.py')).read())
    tab = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'EVENTS':
            tab['EVENTS'] = n.value
    beats = {b['name']: (float(b['t'][0]), float(b['t'][1])) for b in bj['beats']}
    ev = {}
    for k, v in zip(tab['EVENTS'].keys, tab['EVENTS'].values):
        beat, u = ast.literal_eval(k), (ast.literal_eval(v.elts[0]), _num(v.elts[1]))
        a, b = beats[u[0]]                                     # BEAT_NAMES maps every beat to itself
        ev[beat] = a + u[1] * (b - a)
    dolph = None
    for n in ast.parse(open(os.path.join(FILM, 'szlife.py')).read()).body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'DOLPH':
            dolph = ast.literal_eval(n.value)
    words = [(b['words'].strip(), b['t'][0]) for b in bj['beats'] if b.get('words', '').strip()]
    return ev, beats, dolph, bj, words


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


def music_edit(bj):
    """The four cuts of beats.json music.segments (recording seconds -> film second), each cross-faded triangularly (linear in, linear out)."""
    x, sr = sf.read(music_file(), dtype='float32', always_2d=True)
    assert sr == SR, sr
    segs = bj['music']['segments']; y = np.zeros((N, 2), np.float32)
    for k, s in enumerate(segs):
        a, b = s['src']; clip = x[int(round(a * SR)):int(round(b * SR))].copy(); i0 = int(round(s['film'] * SR))
        xf_in = int(round(s.get('xf', 0.0) * SR)); xf_out = int(round(segs[k + 1].get('xf', 0.0) * SR)) if k + 1 < len(segs) else 0
        if xf_in: clip[:xf_in] *= np.linspace(0, 1, xf_in, dtype=np.float32)[:, None]
        if xf_out: clip[-xf_out:] *= np.linspace(1, 0, xf_out, dtype=np.float32)[:, None]
        m = min(len(clip), N - i0); y[i0:i0 + m] += clip[:m]
    return y


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


# ==================================================================================================================
# 6. THE SOUND OF THE FILM: every event of the picture, in time order
# ==================================================================================================================
def design(F, T, B, DOLPH, WORDS):
    """Every level is `rel`: the clip's peak in dB against the music's RMS around the event (rmsrel / follow-beds for steady sounds)."""
    rng = np.random.default_rng(72)
    AUTO = 'auto'                                        # tuned to what the orchestra plays at that moment
    E = [T['e%d' % k] for k in range(9)]
    STR = W.STRENGTH
    BOTTLE, CASTLE, BALL, BOARD = (0.80, -0.72), (0.56, -0.50), (-0.98, -0.52), (1.46, -0.52)      # szvolc.BOTTLE, szvolc.CASTLE, szlife.BALL_TO, szlife.BOARD
    p_bottle, p_castle, p_ball, p_board = pan_of(*BOTTLE), pan_of(*CASTLE), pan_of(*BALL), pan_of(*BOARD)
    p_vent = pan_of(W.XC, W.YC)
    p_dol = lambda s, d: pan_of(*W.at_screen(s, d), half=4.0)

    def fbed(name, t0, t1, off, extra=None, label='', **kw):
        """A bed that follows the music: its level is the music's own (smoothed) RMS plus `off` dB, plus an optional [(t, dB)] shape."""
        ts = np.arange(t0, t1 + 0.01, 0.5); lv = np.array([F.mr(t - 0.75, t + 0.75) for t in ts]); lv = gaussian_filter1d(lv, 3.0, mode='nearest')
        ex = np.interp(ts, [p[0] for p in extra], [p[1] for p in extra]) if extra else 0.0
        F.bed(name, t0, t1, rms=0.0, env=list(zip(ts.tolist(), (lv + off + ex).tolist())), label=label, **kw)

    # ---- the sea and the birds all film long: gulls in the hook and in the calm, the sea always (it follows the music, a little under)
    fbed('small_waves_ocean', 0, DUR, -17, start=30, hp=120, lp=5500, fi=1.0, fo=1.5, label='the sea laps the beach', extra=[(0, 2), (9, 0), (31, -3), (58, -2), (62, 2)])
    fbed('gulls_harbor', 0, 5.8, -15, start=20, hp=700, lp=7500, p=-0.2, fi=0.8, fo=1.5, label='gulls over the beach (the hook)', extra=[(0, 0), (4.9, -1), (5.8, -10)])
    fbed('gulls_harbor', 59.0, DUR, -15, start=60, hp=700, lp=7500, p=0.15, fi=2.0, fo=1.5, label='gulls over the calm', extra=[(59, -6), (62, 0), (72, -2)])
    fbed('birds_waking_3', 59.4, DUR, -16, start=40, hp=500, lp=9000, p=-0.1, fi=2.5, fo=1.5, label='small birds find the green island', extra=[(59.4, -8), (63, 0), (72, 0)])
    fbed('wind_plain', 58.8, DUR, -23, start=20, hp=120, lp=3500, fi=2.5, fo=1.5, label='a soft breeze in the new leaves')
    F.spot('sea_tern', 1.15, rel=-16, p=-0.45, start=2.0, length=2.0, hp=600, lp=7500, fi=0.05, fo=0.5, send=-5, label='a tern calls over the sea', trim=False)

    # ---- hook 0 to 4.9: the beach ball rolls in and stops with a little bounce; a dolphin hops
    b0, b1 = T['ball0'], T['ball1']
    F.spot('strong_wind_village', b0, rel=-17, start=69.6, length=b1 - b0, lp=3200, hp=500, fi=0.7, fo=0.8, trim=False, sweep=(-0.35, p_ball), swell=True,
           label='the beach ball rolls in on the sand (a soft swish of air stands in)')
    for dt, rl in ((0.0, -8), (0.26, -14)):
        F.spot('boing_2', b1 + dt, rel=rl, p=p_ball, notes=AUTO, lp=3500, fi=0.02, fo=0.25, length=0.6, label='the beach ball stops with a little bounce')

    # ---- the dolphins: a splash at the take-off, a bigger one at the landing (1.5 s later), a happy squeak on the way
    for n, (tj, who, s, dd) in enumerate(DOLPH):
        pn = p_dol(s, dd); nm = ('splash_small_1', 'splash_small_2', 'splash_small_3', 'splash_small_4', 'splash_small_5', 'splash_small_6')
        F.spot(nm[n % 6], tj + 0.03, rel=-9, at_peak=True, lead=0.02, p=pn, hp=300, lp=9000, length=1.1, fi=0.01, fo=0.5, label='a dolphin leaps from the sea')
        F.spot(nm[(n + 3) % 6], tj + 1.5, rel=-7, at_peak=True, lead=0.02, p=pn, hp=250, lp=9000, length=1.3, speed=0.9, fi=0.01, fo=0.6, label='the dolphin dives back in')
        if n in (0, 3, 5, 6): F.spot('toy_squeal_3', tj + 0.55, rel=-15, p=pn, notes=AUTO, lp=7000, length=0.7, fi=0.04, fo=0.35, label='a happy squeak (a toy squeal stands in for a dolphin)')

    # ---- magma 4.9 to 8.5: the chamber glows: a warm bowl, a deep rumble that never stops until the eruption
    F.spot('tibetan_bowl_1', T['glow0'] + 0.1, rel=-12, notes=AUTO, lp=5000, fi=0.25, fo=2.0, length=4.0, send=-4, label='the chamber begins to glow (a warm bowl)')
    fbed('thunder_8', T['glow0'], E[0] + 1.2, -14, lp=220, hp=25, start=6, fi=2.0, fo=2.5, label='the deep rumble of the magma far below',
         extra=[(4.9, -28), (8.5, -22), (20.5, -10), (26.0, -4), (31.0, 0), (32.6, -6)])
    fbed('big_broth', T['glow0'] + 0.3, E[0], -12, lp=1500, hp=80, start=1, fi=1.5, fo=1.0, label='thick magma bubbles slowly',
         extra=[(5.2, -22), (8.6, -16), (20.5, -8), (26, -3), (31.0, 0)], p=p_vent)

    # ---- rises 8.5 to 20.5: blobs of magma lift off the chamber (soft bubbles tuned to the orchestra), the rock creaks as it opens
    k = 0
    for tb in np.arange(T['rise0'] + 0.5, T['rise1'] - 0.3, 1.45):
        F.spot('water_bubble_2', float(tb), rel=-15, start=float(rng.uniform(0.5, 15.0)), length=0.55, notes=AUTO, lp=4500, fi=0.02, fo=0.3, p=float(rng.uniform(-0.15, 0.15)) + p_vent,
               label='a blob of magma lifts off the chamber'); k += 1
    F.spot('creak_barn_door', 12.4, rel=-24, start=2.0, length=2.8, speed=0.5, lp=900, hp=60, fi=0.8, fo=1.2, trim=False, swell=True, p=p_vent, label='the rock creaks open (a slowed door stands in)')

    # ---- gas 20.5 to 31.39: bubbles in the magma swell and pop, faster and bigger like a shaken fizzy drink; the bottle trembles
    bp = onsets('bubbles_burst')
    n_b = 42
    for i in range(n_b):
        u = (i + 0.5) / n_b; tb = T['gas0'] + (T['gas1'] - T['gas0']) * u ** 0.75 + float(rng.uniform(-0.12, 0.12))
        on = bp[int(rng.integers(0, len(bp)))]
        F.spot('bubbles_burst', tb, rel=-17 + 8 * u, at_peak=True, lead=0.02, start=max(0.0, on - 0.05), length=0.4, speed=1.25 - 0.45 * u, hp=250, lp=6500, fi=0.01, fo=0.18,
               p=float(rng.uniform(-0.35, 0.35)) + 0.4 * p_vent, trim=False, label='a gas bubble pops in the magma')
    fbed('water_bubble_2', T['gas0'], E[0] - 0.1, -12, start=2, hp=300, lp=4000, fi=1.0, fo=0.6, label='the gas fizzes in the crack', p=p_vent,
         extra=[(21, -14), (26, -6), (31.2, 0)])
    fbed('sparkling_water', T['bottle0'], E[0] - 0.05, -13, start=1, hp=2200, fi=1.0, fo=0.08, p=p_bottle, label='the shaken bottle fizzes',
         extra=[(23, -18), (27, -8), (31.3, 0)])
    fbed('swirl_water', T['bottle0'], E[0], -22, start=3, hp=200, lp=2200, fi=1.0, fo=0.1, p=p_bottle, label='the drink sloshes as it is shaken', extra=[(23, -10), (31.3, 0)])

    # ---- 31.39: THE ERUPTION: a cork pop, a whoosh, a fountain of lava, fizz and foam, steam, a rumble, gulls cheer, the cap lands on the sandcastle
    e0 = E[0]
    F.spot('wine_stopper_3', e0, rel=1, at_peak=True, lead=0.01, speed=0.8, hp=180, lp=6500, fi=0.004, fo=0.25, p=p_bottle, trim=False, label='the bottle pops its cap')
    F.spot('whoosh_long_1', e0 - 0.12, rel=-2, start=0.0, length=3.4, hp=250, lp=4500, fi=0.12, fo=1.7, p=p_vent, trim=False, swell=True, label='WHOOSH: lava leaps out of the top')
    F.spot('whoosh_9', e0 + 0.08, rel=-9, hp=500, lp=6000, fi=0.01, fo=0.15, sweep=(p_bottle, p_castle), label='the cap whooshes over to the sandcastle')
    F.spot('boing_4', e0 + 1.15, rel=-10, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.7, p=p_castle, label='the cap lands on the sandcastle')
    F.spot('thunder_3', e0 - 0.05, rel=-2, at_peak=True, lead=0.05, length=5.5, lp=240, hp=25, fi=0.04, fo=2.5, p=p_vent, trim=False, label='the big happy rumble of the eruption')
    F.spot('sparkling_water', e0 + 0.02, rel=-4, start=3.0, length=3.6, hp=1800, fi=0.02, fo=2.2, p=p_bottle, trim=False, label='fizz and foam burst from the bottle')
    F.spot('steam_hiss_1', e0 + 0.5, rel=-9, start=0.2, length=3.6, hp=1600, fi=0.15, fo=1.6, p=p_vent, trim=False, swell=True, label='a puff of steam')
    F.spot('gulls_harbor', e0 + 0.9, rel=-11, start=float(loud_windows('gulls_harbor', 3.0, 1)[0]), length=3.0, hp=600, lp=7500, fi=0.3, fo=1.3, p=-0.3, swell=True, trim=False,
           label='the gulls cheer from a safe distance')
    F.spot('suction_cup_plastic', e0 - 0.35, rel=-17, length=0.5, hp=400, lp=6000, fo=0.2, p=p_board, label='the snail pops into its shell')
    F.spot('plant_cartoon_4', e0 + 2.2, rel=-19, notes=AUTO, length=0.8, lp=5000, fo=0.3, p=p_board, label='the snail peeks out again')
    fbed('fire_branching_1', e0 + 0.6, B['layers'][0] + 1.0, -22, start=8, hp=500, lp=7000, fi=1.0, fo=1.5, p=0.1, label='the lava crackles as it flows',
         extra=[(32, 2), (36, 0), (41, -4), (43.3, -12)])
    fbed('steam_hiss_3', e0 + 2.4, B['flows'][0] + 3.0, -26, start=0.2, hp=1800, fi=1.0, fo=1.5, p=0.35, label='steam where the lava meets the sea', extra=[(34, 0), (38, 0), (42, -6)])

    # ---- every eruption: a ball hop, a thud as the new layer lands, a puff of steam, a short fizz, lava hissing into the sea; cooling rock ticks
    ob = onsets('bubbles_burst')
    for kk, e in enumerate(E):
        S = STR[kk]
        if kk > 0:
            F.spot('whoosh_9', e - 0.10, rel=-10 + 3 * (S - 0.55), hp=450, lp=6000, fi=0.01, fo=0.12, p=p_vent, label='a little jet leaps from the top')
            F.spot('body_fall_1', e + 0.02, rel=-6 + 5 * (S - 0.55), at_peak=True, lead=0.02, speed=0.5, lp=280, hp=30, fi=0.02, fo=0.5, p=p_vent, trim=False,
                   label='a new layer settles (soft thud)')
            F.spot('sparkling_water', e + 0.02, rel=-10 + 3 * (S - 0.55), start=3.0 + 0.1 * kk, length=1.7, hp=1800, fi=0.02, fo=1.0, p=p_vent, trim=False, label='a short fizz of the small fountain')
            F.spot('steam_hiss_3', e + 0.5, rel=-14, start=0.1, length=2.0, hp=1700, fi=0.1, fo=1.0, p=p_vent, trim=False, swell=True, label='a puff of steam')
            F.spot('steam_hiss_1', e + 1.9, rel=-15, start=0.4, length=2.4, hp=1700, fi=0.3, fo=1.3, p=0.3, trim=False, swell=True, label='lava hisses where it meets the sea')
        F.spot('boing_6', e + 0.7, rel=-9, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.6, p=p_ball, label='the beach ball lands after its hop')
        if kk < 8:
            F.spot(('ice_crack_1', 'ice_crack_2', 'ice_crack_3', 'ice_crack_4')[kk % 4], e + 2.7, rel=-16, speed=1.35, lp=6000, hp=500, fi=0.01, fo=0.3, p=0.2 - 0.05 * kk, label='the cooling rock ticks')
    for tt in (37.4, 39.0, 40.6, 41.5):
        F.spot(('ice_crack_1', 'ice_crack_2', 'ice_crack_3', 'ice_crack_4')[int(tt * 3) % 4], tt, rel=-17, speed=1.3, lp=6000, hp=500, fi=0.01, fo=0.3, p=0.25, label='the first lava cools into new rock (ticks)')

    # ---- the last, biggest eruption on the final crash
    e8 = E[8]
    F.spot('thunder_2', e8 - 0.05, rel=-1, at_peak=True, lead=0.05, length=5.0, lp=260, hp=25, fi=0.03, fo=2.4, p=p_vent, trim=False, label='the biggest rumble on the final crash')
    F.spot('splash_big_3', e8 + 1.5, rel=-9, at_peak=True, lead=0.03, length=2.4, hp=300, lp=8000, fi=0.01, fo=1.0, p=0.25, label='a big happy splash as the lava slides into the sea')
    F.spot('glockenspiel', e8 + 0.04, rel=-9, notes=AUTO, lp=9000, fi=0.01, fo=1.8, length=2.8, send=-4, p=0.0, label='sparkles on the final crash')
    F.spot('gulls_harbor', e8 + 1.2, rel=-15, start=float(loud_windows('gulls_harbor', 3.0, 2)[1]), length=3.2, hp=600, lp=7500, fi=0.3, fo=1.5, p=0.3, swell=True, trim=False,
           label='the gulls cheer again')

    # ---- layers: the clock spins while the layers pile up
    F.spot('winder_1', T['stack0'], rel=-16, start=0.0, length=9.9, hp=500, lp=5000, fi=0.4, fo=0.6, p=0.35, trim=False, swell=True, label='the clock spins (a music-box winder)')
    F.spot('winder_2', T['stack0'] + 9.9, rel=-16, start=0.0, length=T['stack1'] - T['stack0'] - 9.9 + 0.2, hp=500, lp=5000, fi=0.2, fo=0.5, p=0.35, trim=False, swell=True,
           label='the clock spins on (a music-box winder)')

    # ---- rest 58.5 to 66: plants find a home on the new rock (soft growing pops tuned to the quiet theme), the soil forms
    for i, tp in enumerate((T['rest0'] + 0.5, T['rest0'] + 2.0, T['rest0'] + 3.4, T['rest0'] + 4.8, T['rest0'] + 6.1)):
        F.spot(('plant_cartoon_1', 'plant_cartoon_4')[i % 2], tp, rel=-13, notes=AUTO, lp=5500, length=0.9, fi=0.02, fo=0.35, p=-0.3 + 0.15 * i, send=-5, label='a plant finds a home on the new rock')
    F.spot('water_over_soil', T['soil0'], rel=-23, start=1.0, length=3.0, lp=1800, hp=100, fi=0.5, fo=1.2, p=0.1, trim=False, swell=True, label='the soil forms')
    F.spot('robin_1', 62.6, rel=-18, p=-0.4, lp=6000, fi=0.05, fo=0.5, send=-4, label='a bird sings in the new green')

    # ---- islands 66 to 69: a gold ring round each island: a chime each, tuned to the quiet theme
    rings = [(W.NEAR_C[0][0], W.NEAR_C[0][1]), (W.NEAR_C[2][0], W.NEAR_C[2][1]), (W.NEAR_C[1][0], W.NEAR_C[1][1]), (W.XC, W.YC)]
    for j, (rx_, ry_) in enumerate(rings):
        tr = T['ring%d' % j]
        F.spot(('chimes_butterfly_1', 'chimes_butterfly_3', 'chimes_dream_1', 'chimes_dream_3')[j], tr, rel=-9 + (1 if j == 3 else 0), notes=AUTO, lp=9000, fi=0.01, fo=1.6, length=2.4, send=-3,
               p=pan_of(rx_, ry_, half=4.0), label='a chime for each old island' if j < 3 else 'a chime for our new island')
    F.spot('triangle_2', T['ring3'] + 0.05, rel=-14, notes=AUTO, lp=9000, fi=0.01, fo=1.8, length=3.0, send=-3, p=p_vent, label='a ping on our own island')

    # ---- send-off 69 to 72.3: the snail waves; the question
    F.spot('boing_4', T['wave0'], rel=-11, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.7, p=p_board, label='the snail waves')
    F.spot('toy_squeal_1', T['wave0'] + 0.35, rel=-17, notes=AUTO, lp=6500, fi=0.02, fo=0.3, length=0.5, p=p_board, label='a happy squeak from the snail')
    F.spot('chimes_dream_3', 70.5, rel=-13, notes=AUTO, lp=9000, fi=0.04, fo=1.4, length=2.3, send=-3, p=0.1, label='a last twinkle for the question')

    # ---- words in with a soft pop (every word set in code)
    for w, tw in WORDS:
        F.spot('wine_stopper_3', tw + 0.35, rel=-16, speed=1.3, notes=None, lp=4500, hp=300, fi=0.01, fo=0.2, p=0.0, label='words pop in: ' + w.lower())
    return dict(eruption=e0, last=e8)


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
    red[:int(0.1 * SR)] = 0; red[-int(0.5 * SR):] = 0                                      # the fade-in and fade-out are not the limiter
    res.update(limiter_max_reduction_db=round(float(red.max()), 2), limiter_max_reduction_at_s=round(float(np.argmax(red) / SR), 2),
               limiter_samples_over_1db=int((red > 1.0).sum()), limiter_seconds_over_3db=round(float((red > 3.0).sum() / SR), 2), limiter_seconds_over_1db=round(float((red > 1.0).sum() / SR), 2))
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


# ==================================================================================================================
# 8. SOUND.md (written from the same data as mix.json, so the two never disagree)
# ==================================================================================================================
STANDINS = [
    'The beach ball rolls on a soft swish of air (a band-passed village wind): the bank has no rolling ball. Its stop and every hop are soft harp "boings", tuned to the music.',
    'Dolphins are real splashes with a toy squeal tuned to the music for a happy squeak: there is no dolphin in the bank.',
    'The deep rumble of the magma is real thunder, low-passed to the floor of hearing; thick bubbling magma is a real pot of broth, slowed and low-passed; the cracking rock is a slowed barn door.',
    'Gas bubbles popping in the magma are real bubbles bursting in water, slowed and lowered as they grow; the glowing chamber is a singing bowl.',
    'The shaken bottle is real sparkling water (fizz) and a swirl of water; the cap pop is a wine-stopper pop slowed a little; the cap flying is a short whoosh.',
    'The lava fountain is a long real whoosh plus a thunder rumble and real fizz; lava crackle is a real fire in branches; steam is a real steam hiss; cooling rock ticks are real ice cracks sped up and filtered. There is no lava in any recording.',
    'The gulls cheer is a real gull recording from a harbour, placed on the eruption.',
    'The snail popping into its shell is a suction-cup pop; peeking out and waving are a plant-pop and a boing; its happy squeak is a toy squeal.',
    'Plants finding a home are cartoon plant pops tuned to the music; the soil forming is water over soil, soft.',
    'The clock spinning is a music-box winder.',
    'Words pop in with a wine stopper\'s pop, sped up.',
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
    md = f"""# Sound of the volcano film (Little Big Questions: how is a volcano born?)

A SILENT 72.3 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
`audio/mix.m4a` is committed (force-added); `audio/mix.wav` is ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** {m['credit']}

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- {meas['seconds']:.2f} s, 48 kHz stereo AAC 256k, {meas['lufs']:.1f} LUFS integrated (target {TARGET_LUFS:.0f}), true peak {meas['true_peak']:.2f} dBTP (limit {TP_LIMIT} dBTP), loudness range {meas['lra']:.1f} LU.
- The loudest limiter dip is {meas['limiter_max_reduction_db']:.1f} dB at {meas['limiter_max_reduction_at_s']:.1f} s; the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; a thud's or a bubble's loudest instant sits 10 to 35 ms after the event
  frame). On the rendered effects bus alone, {chk['landed']} of {chk['checked']} percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under a bed or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
{m['piece']}, {m['recording']}, {m['licence']}. Source: {m['source']}. Asset: {m['asset']}.
{m['edit']}
Every cut sits on a rest of the music; the cross-fades are triangular (linear in, linear out). The music leads. A slow level rider
(zero-phase, 1 s Gaussian smoothing, ratio {edit_info['ratio']}, gain between {edit_info['gain_min']:+.1f} and {edit_info['gain_max']:+.1f} dB) lifts the whispering opening
and eases the tutti so the film can sit near -16 LUFS; the notes keep their own shape.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow): {BANK_RUN}. Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowl, chimes, boings, bubbles, plant pops, squeaks) are tuned by resampling to the pitch classes the orchestra is playing at that moment
(read from the recording, mostly B minor), so they ring with the chord and never against it. Steady beds (sea, rumble, fizz, crackle, birds) follow the music's own
smoothed level, a fixed number of dB under it, so they are felt more than heard.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
""" + "\n".join(lines) + f"""

## Stand-ins (honest)
""" + "\n".join('- ' + s for s in STANDINS) + """

## Rebuild
`python3 films/cutaway/kids/volcano/audio/make_audio.py` (a few minutes; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
"""
    open(os.path.join(FILM, 'SOUND.md'), 'w').write(md)


# ==================================================================================================================
# 9. MAIN
# ==================================================================================================================
KEY_EVENTS = [('beach ball stops (hook)', 'ball1'), ('chamber glows', 'glow0'), ('bottle shaken', 'bottle0'), ('ERUPTION: cork pop', 'e0'), ('first lava flows', 'flows_0'),
              ('layer hit e1', 'e1'), ('layer hit e3', 'e3'), ('final crash e8', 'e8'), ('rest begins', 'rest0'), ('ring: first island', 'ring0'), ('ring: our island', 'ring3'),
              ('snail waves', 'wave0')]


def main():
    T, B, DOLPH, bj, WORDS = read_events()
    T['flows_0'] = B['flows'][0] + 0.6
    need = ['small_waves_ocean', 'gulls_harbor', 'birds_waking_3', 'wind_plain', 'sea_tern', 'strong_wind_village', 'boing_2', 'boing_4', 'boing_6', 'splash_small_1', 'splash_small_2',
            'splash_small_3', 'splash_small_4', 'splash_small_5', 'splash_small_6', 'splash_big_3', 'toy_squeal_1', 'toy_squeal_3', 'tibetan_bowl_1', 'thunder_8', 'thunder_3', 'thunder_2', 'big_broth',
            'water_bubble_2', 'creak_barn_door', 'bubbles_burst', 'sparkling_water', 'swirl_water', 'wine_stopper_3', 'whoosh_long_1', 'whoosh_9', 'steam_hiss_1', 'steam_hiss_3',
            'suction_cup_plastic', 'plant_cartoon_1', 'plant_cartoon_4', 'fire_branching_1', 'body_fall_1', 'ice_crack_1', 'ice_crack_2', 'ice_crack_3', 'ice_crack_4', 'glockenspiel',
            'winder_1', 'winder_2', 'water_over_soil', 'robin_1', 'chimes_butterfly_1', 'chimes_butterfly_3', 'chimes_dream_1', 'chimes_dream_3', 'triangle_2']
    ensure_bank(need)
    csvp = os.path.join(K.CACHE, 'sfx-bank.csv')
    if not os.path.exists(csvp):
        urllib.request.urlretrieve('https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.csv', csvp)
    mus_raw = music_edit(bj)
    RIDER = dict(target=-21.0, ratio=2.6, maxg=14.0)
    mus, gcur = level_rider(mus_raw, **RIDER)
    F = Film(); F.mus = mus
    info = design(F, T, B, DOLPH, WORDS)
    duck = [(0, 0), (DUR, 0)]
    os.makedirs(HERE, exist_ok=True)
    print('mastering')
    y, musd, fx, res = master(F, mus, duck, fx_trim=FX_TRIM, out_dir=HERE)
    if os.environ.get('KF_STEMS'):                       # for inspection only (never in git): the music and the effects as the mix has them
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
    ev_list = [(nm, T[k]) for nm, k in KEY_EVENTS]
    tl = timeline(y, musd, fx, ev_list)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(HERE, 'mix.m4a')],
                               capture_output=True, text=True).stdout.strip())
    res['seconds'] = round(dur, 3)
    csvrows = bank_csv()
    edit_info = dict(ratio=RIDER['ratio'], gain_min=float(gcur.min()), gain_max=float(gcur.max()))
    meas = dict(res, codec='aac 256k stereo 48 kHz', target_lufs=TARGET_LUFS, true_peak_limit_dbtp=TP_LIMIT)
    out = dict(
        film='kids-volcano', duration_s=meas['seconds'], measurements=meas,
        music=dict(bj['music'], rider=dict(target_lufs=RIDER['target'], ratio=RIDER['ratio'], max_gain_db=RIDER['maxg'], smoothing_s=1.0,
                                           gain_db_range=[round(edit_info['gain_min'], 1), round(edit_info['gain_max'], 1)]), music_only_lufs=round(dsp.loudness(musd), 2)),
        events={k: round(float(v), 3) for k, v in sorted(T.items(), key=lambda x: x[1]) if v > 0},
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
        for t in range(0, 72):
            pk = max([r['peak_above_music_rms_db'] for r in F.rows if 'peak_above_music_rms_db' in r and t <= r['t'] < t + 1] or [None], key=lambda v: -99 if v is None else v)
            print(f'  {t:2d}-{t + 1:2d}  mix {rms_line(y, t, t + 1):6.1f}  music {rms_line(musd, t, t + 1):6.1f}  fx {rms_line(fx, t, t + 1):6.1f}   gap {rms_line(musd, t, t + 1) - rms_line(fx, t, t + 1):5.1f} dB   top spot {pk}')
    print('timeline (t, mix, music, effects; dBFS per 0.5 s):')
    for r in tl:
        print(f"  {r['event']:<22} @{r['t']:6.2f}:", ' | '.join(f"{a:5.1f}: {m_:5.1f} {mu:5.1f} {e:5.1f}" for a, m_, mu, e in r['windows']))
    return out


if __name__ == '__main__':
    main()
