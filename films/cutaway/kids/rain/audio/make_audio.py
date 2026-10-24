#!/usr/bin/env python3
"""Sound of Little Big Questions, film 3 (rain): a REAL orchestral recording and REAL recorded sound effects (73.0 s).

    python3 films/cutaway/kids/rain/audio/make_audio.py     # writes audio/mix.m4a, audio/mix.json and ../SOUND.md

What it makes (all deterministic):
  MUSIC   Smetana, Vltava (The Moldau), Musopen Symphony (public domain), cut as beats.json says (EDIT below): the two
          springs, the river theme entering on the first fat raindrop, the broad major river theme for the rainbow, and the
          piece's own two final chords. Cross-fades 1.5, 1.0 and 2.0 s on joints found by chroma and pulse matching. The
          recording is very quiet at the start and loud at the end (about 30 dB), so a strong slow level rider evens it out.
  EFFECTS real CC0 recordings (the studio bank, release sfx-bank of Eouchi147/rc-render, BigSoundBank) placed on the picture's
          events. Event times are READ from blender.py (the EVENTS table) and beats.json at build time, so a re-timed
          picture re-times the sound. Soft attacks everywhere, nothing sudden or scary (no thunder).
  TONAL   the few pitched sounds are tuned by resampling to the pitch classes the orchestra plays at that moment.
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
FOSSIL = os.path.dirname(HERE)      # this film's folder (the name is kept from the template)
ROOT = os.path.abspath(os.path.join(FOSSIL, '..', '..', '..', '..'))
SERIES = os.path.join(ROOT, 'films', 'cutaway', 'series')
os.environ['KF_SOUND_DUR'] = '73.0'                      # before audio_kit is imported
sys.path.insert(0, SERIES)
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy.ndimage import gaussian_filter1d  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
import audio_kit as K  # noqa: E402

dsp = K.dsp
SR, N, DUR = K.SR, K.N, K.DUR
db = K.db
MUSIC_URL = 'https://github.com/Eouchi147/rc-render/releases/download/music/smetana-vltava-musopen.flac'
MUSIC_CACHE = os.path.expanduser('~/.cache/kinoforge/music/smetana-vltava-musopen.flac')


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
    words = [(b['words'].strip(), b['t'][0]) for b in bj['beats'] if b.get('words', '').strip()]
    return ev, beats, eras, bj, words


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


# the edit, in recording seconds: (start, end) of each piece and the cross-fade into the next (s). Joints: A 16.2 = B 44.4 (flutes, chroma 0.95),
# river theme 77.0 = 712.2 (the E-minor theme's dominant into the broad E-major theme), 728.0 = 761.0 (E major afterglow into the quiet tail)
EDIT = dict(pieces=[(0.0, 16.95), (43.65, 77.5), (711.7, 729.0), (760.8, 770.2)], xf=[1.5, 1.0, 2.0], fade_out=0.6, tail_trim_db=-3.0)


def music_edit():
    x, sr = sf.read(music_file(), dtype='float32', always_2d=True)
    assert sr == SR, sr
    out = None
    for k, (a, b) in enumerate(EDIT['pieces']):
        seg = x[int(round(a * SR)):int(round(b * SR))].copy()
        if k == len(EDIT['pieces']) - 1:                                       # the piece's own two final chords: a little softer, fade-out of the last decay
            seg *= db(EDIT['tail_trim_db']); n = int(EDIT['fade_out'] * SR); seg[-n:] *= np.linspace(1, 0, n, dtype=np.float32)[:, None]
        if out is None: out = seg; continue
        L = int(EDIT['xf'][k - 1] * SR); ramp = np.linspace(0, 1, L, dtype=np.float32)[:, None]
        out = np.concatenate([out[:-L], out[-L:] * (1 - ramp) + seg[:L] * ramp, seg[L:]])
    y = out
    assert abs(len(y) - N) <= 2, (len(y) / SR, N / SR)
    y = y[:N] if len(y) >= N else np.vstack([y, np.zeros((N - len(y), 2), np.float32)])
    return y.astype(np.float32)


def lufs_curve(y, win=0.4, hop=0.1):
    """momentary loudness (K-weighted, LUFS) every hop s."""
    k = dsp._kweight(y.astype(np.float64), SR); sq = (k ** 2).sum(1); c = np.concatenate([[0], np.cumsum(sq)])
    w, h = int(win * SR), int(hop * SR); st = np.arange(0, len(sq) - w + 1, h)
    return -0.691 + 10 * np.log10(np.maximum((c[st + w] - c[st]) / w, 1e-12))


def level_rider(y, target=-22.0, ratio=1.7, sigma=1.0, maxg=7.0, ming=None):
    """Zero-phase, slow gain riding: out = target + (level - target) / ratio on a 1 s Gaussian-smoothed level. Smooth,
    no attack or release artefacts, no change to the notes' shape; returns (y, gain_db_curve_at_hop)."""
    lv = lufs_curve(y); sm = gaussian_filter1d(np.maximum(lv, -60.0), sigma / 0.1, mode='nearest')
    g = np.clip((target - sm) * (1 - 1 / ratio), -(ming if ming is not None else maxg), maxg)
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
        cap = 10 ** ((rms + 11.0) / 20.0); y = (cap * np.tanh(y / cap)).astype(np.float32)          # a bed is a bed: no stray bang or drop more than 11 dB over its level
        y = y * db(rms - rms_db(y[:min(len(y), 20 * SR)]))
        if p: y = K.pan(y, p)
        i = int(t0 * SR); mm = min(n, N - i); seg = y[:mm]
        if env is not None: seg = seg * K.envelope(env)[i:i + mm, None]
        self.m.bus[i:i + mm] += seg
        if send is not None: self.m.send[i:i + mm] += seg * db(send)
        self.m._note(name, f'bed {t0:.1f}-{t1:.1f} s')
        self.rows.append(dict(t=round(float(t0), 3), what=label or 'bed', name=name, gain_db=round(float(g), 1), bed_to=round(float(t1), 3), bed_peak_db=round(float(20 * np.log10(np.abs(seg).max() + 1e-9)), 1), bed_rms_db=round(float(rms_db(seg)), 1)))
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
def h01(i, c, salt=0):
    """The same pseudo-random hash as szstory.h01 (the picture's merge times are staggered with it)."""
    h = (int(i) * 374761393 + int(c) * 668265263 + salt * 2246822519) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffffff) / float(0xffffff)


def design(F, T, B, ERAS, WORDS):
    """Every level is `rel`: the clip's peak in dB against the music's RMS around the event (rmsrel / bed rel for steady sounds)."""
    rng = np.random.default_rng(73)
    AUTO = 'auto'                                        # tuned to what the orchestra plays at that moment
    HX, HY = 1.8, 1.1
    pan_xy = lambda x, y: pan_of(x, y)
    PUD = (-0.72, -0.74); LAKE = (0.50, -0.30)
    landings = []; k = 0
    while T['jump0'] + (k + 0.5) * 1.6 <= T['jump1'] + 0.01: landings.append(T['jump0'] + (k + 0.5) * 1.6); k += 1
    landings.append(T['chord2'])
    rain_end = T['drop1']
    # ---- the world: morning birds and a brook until the cloud darkens, the same again after the rain; wind; the brook swells
    dry = [(0, 0), (T['dark0'] + 1.0, 0), (T['dark1'] + 1.5, -40), (rain_end, -40), (T['sunback0'] + 2.5, -3), (T['sunback1'], 0)]
    F.bed('birds_waking_3', 0, 73, rel=-17, start=40, hp=500, env=dry, fi=1.5, fo=2.0, label='morning birds (and again when the sun is back)')
    F.bed('wind_plain', 0, 73, rel=-25, start=20, hp=120, lp=3500, fi=1.5, fo=2.0, label='a soft breeze')
    F.bed('forest_stream_1', 0, 73, rel=-17, start=10, hp=200, lp=7500, p=-0.15, env=[(0, 0), (T['drop0'], 0), (T['swell1'], 5), (T['sunback1'], 5), (73, 2)], fi=1.5, fo=2.0,
          label='the brook (it swells in the rain)')
    # ---- the sun warms 6.5 to 12.5: a warm swell, sparkling water, the glitter of the lake and the sea
    F.bed('sun_heat_1', T['sun0'] - 0.5, T['sun1'] + 2.5, rel=-20, start=3, hp=150, lp=5000, env=[(T['sun0'] - 0.5, -30), (T['sun0'] + 2, 0), (T['sun1'], 0), (T['sun1'] + 2.5, -30)], fi=0.6, fo=0.8, label='the sun warms (a warm hum)')
    F.bed('sparkling_water', T['sun0'] + 1.0, T['vap1'], rel=-22, start=5, hp=800, lp=9000, p=0.2, env=[(T['sun0'] + 1.0, -30), (T['sun0'] + 3.5, 0), (T['vap1'] - 2, 0), (T['vap1'], -30)], fi=0.8, fo=1.2,
          label='the water glitters in the warm sun')
    for k_, tg in enumerate([T['sun0'] + 1.2, T['sun0'] + 3.1, T['sun0'] + 4.6, T['sun1'] - 0.2]):
        F.spot('chimes_butterfly_1', tg, rel=-14 - k_ * 0.5, p=0.25, notes=AUTO, send=-3, fo=0.6, length=1.6, label='a glint on the lake')
    # ---- invisible water 12.5 to 19: a rising shimmer of glassy chimes, the ribbons climb
    for k_, tt in enumerate((T['vapup0'], T['vapup0'] + 1.7, T['vapup0'] + 3.4, T['vapup0'] + 5.0)):
        F.spot('chimes_dream_1', tt, rel=-12 - k_ * 0.7, rev=True, notes=AUTO, send=-3, fi=0.4, fo=0.3, p=0.15 * (k_ - 1.5), swell=True, label='the water rises as an invisible shimmer (reversed chimes)')
    F.bed('wind_inside_1', T['vapup0'], T['cloud1'], rel=-26, start=8, hp=200, lp=3000, env=[(T['vapup0'], -30), (T['vapup0'] + 3, 0), (T['cloud1'] - 3, 0), (T['cloud1'], -30)], fi=0.8, fo=1.0,
          label='high up the air is cold and still (a soft wind)')
    # ---- tiny drops 19 to 25.5: tiny tinks as the dots gather into the cloud
    nd = 0
    for tt in np.linspace(T['cool0'] + 0.4, T['cool1'] - 0.2, 14):
        F.spot('candle_sparkle_1', tt, rel=-16 - (nd % 3), p=float(rng.uniform(-0.2, 0.3)), lp=9000, hp=1200, fi=0.01, fo=0.2, length=0.5, label='a tiny drop joins the cloud'); nd += 1
    for k_, tt in enumerate((T['cloud0'] + 0.3, T['cloud0'] + 3.0, T['cloud0'] + 6.0)):
        F.spot('cluster_chimes', tt, rel=-15, start=2.0 * k_, length=2.2, notes=AUTO, lp=9000, fi=0.3, fo=1.2, send=-3, swell=True, p=0.1, label='the cloud puffs up (a soft shimmer)')
    # ---- a million 25.5 to 33.86: the window opens, drops bump and stick (a soft blip each), one fat drop falls
    F.spot('water_bubble_2', T['lens0'] + 0.1, rel=-11, at_peak=True, lead=0.01, length=0.5, lp=5000, fo=0.3, send=-4, trim=False, label='the round window opens (a soft bubble)')
    pops = []
    for L_, base in enumerate((T['lensj1'], T['lensj2'], T['lensj3'], T['lensj4'], T['lensj5']), start=1):
        for g in range(NLEAF >> L_):
            pops.append((base + 0.35 * (h01(g, L_) - 0.5) * (1 if L_ < 5 else 0), L_))
    used = []
    for tp, L_ in sorted(pops):
        if any(abs(tp - u) < 0.12 for u in used) and L_ < 5: continue          # thin out the crowd: one pop per 0.12 s
        used.append(tp)
        nm = ('water_bubble_2', 'bubbles_burst', 'water_bubble_2', 'drops_3', 'splash_small_3')[L_ - 1]
        F.spot(nm, tp, rel=-16 + 2.0 * L_, at_peak=True, lead=0.01, length=0.4 + 0.1 * L_, speed=1.5 - 0.15 * L_, lp=6000, hp=250, fi=0.01, fo=0.18, notes=AUTO if L_ < 4 else None,
               p=0.15 * (L_ - 3), send=-4, trim=False, label='two drops bump and stick (a soft blip)')
    F.spot('boing_2', T['lensj5'] + 0.05, rel=-10, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.7, p=0.0, label='the last two join: one plump drop')
    F.spot('whoosh_3', T['lens2'] + 0.1, rel=-17, lp=4000, fi=0.1, fo=0.2, length=0.8, swell=True, p=0.2, label='the fat drop falls out of the window')
    F.bed('rain_puddle', T['dark0'], T['drop0'] + 1.0, rel=-35, start=8, hp=300, lp=6000, env=[(T['dark0'], -30), (T['dark1'], -12), (T['drop0'] + 1.0, 0)], fi=1.0, fo=0.5, label='the cloud grows heavy (a far hush of rain)')
    # ---- first drops 33.86 to 40.5: single plinks, then soft rain; the child runs in, the umbrella pops open
    t0d = T['drop0']
    first = [0.0, 0.85, 1.5, 1.95, 2.35, 2.65, 2.9, 3.1, 3.3, 3.5]
    for k_, dt in enumerate(first):
        nm = ('drops_1', 'drops_2', 'drops_4', 'drops_3')[k_ % 4]; pc = pieces(nm); pa = pc[(2 * k_) % min(8, len(pc))]
        F.spot(nm, t0d + dt, rel=-8 + 0.4 * k_, at_peak=True, lead=0.01, start=max(0.0, pa[0] - 0.03), length=0.6, hp=400, lp=8000, fi=0.01, fo=0.3, p=float(rng.uniform(-0.5, 0.5)),
               send=-3, trim=False, label='the first raindrops fall' if k_ == 0 else 'a raindrop')
    F.bed('rain_puddle', t0d + 2.0, rain_end + 2.5, rel=-10, start=20, hp=200, lp=9000, env=[(t0d + 2.0, -30), (T['rainsoft'], -3), (T['rainsoft'] + 4, 0), (rain_end - 2.5, 0), (rain_end, -12), (rain_end + 2.5, -40)],
          fi=0.6, fo=1.0, label='soft rain')
    F.bed('rain_concrete', t0d + 3.0, rain_end + 1.5, rel=-23, start=10, hp=800, lp=9000, p=0.2, env=[(t0d + 3.0, -30), (T['rainsoft'], -4), (rain_end - 3, 0), (rain_end + 1.5, -40)], fi=0.8, fo=1.0,
          label='rain on leaves')
    cdir = pan_xy(-1.2, -0.8)
    for j in range(8):
        F.spot('steps_short_grass', T['child0'] + 0.2 + 0.22 * j, rel=-10 - 0.4 * j, at_peak=True, lead=0.015, start=max(0.0, onsets('steps_short_grass')[(3 * j) % len(onsets('steps_short_grass'))] - 0.06),
               length=0.24, lp=3500, hp=200, fi=0.01, fo=0.12, trim=False, p=cdir - 0.1 + 0.02 * j, label='she runs in over the wet grass')
    cl = pieces('cloth'); cl_long = max(cl, key=lambda a: a[1] - a[0])
    F.spot('cloth', T['umbrella0'] - 0.2, rel=-15, start=cl_long[0] + 1.0, length=0.8, hp=400, lp=4500, fi=0.1, fo=0.2, p=cdir, trim=False, swell=True, label='the umbrella unfurls (cloth)')
    F.spot('wine_stopper_3', T['umbrella1'] - 0.1, rel=-9, at_peak=True, lead=0.01, lp=5000, hp=250, fi=0.01, fo=0.2, p=cdir, trim=False, label='POP: the yellow umbrella opens')
    F.spot('boing_4', T['umbrella1'] - 0.02, rel=-12, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.6, p=cdir, label='the umbrella bounces open (a soft boing)')
    F.spot('rain_puddle', T['umbrella1'] + 0.2, rel=-18, start=30, length=2.2, hp=800, lp=6000, fi=0.3, fo=0.8, p=cdir, trim=False, swell=True, label='rain drums on the umbrella')
    # the snail loves it: a happy squeak and little boings as it wiggles
    for k_, tt in enumerate((T['snail0'] + 0.3, T['snail0'] + 1.9, T['snail0'] + 3.4, T['snail0'] + 5.2)):
        F.spot(('toy_squeal_1', 'boing_4', 'toy_squeal_3', 'boing_4')[k_], tt, rel=-17 + (k_ % 2), notes=AUTO, lp=5000, fi=0.03, fo=0.3, length=0.5, p=0.65, label='the snail wiggles happily in the rain')
    # the watering can fills up (plinks of rain in a metal can)
    pm = pieces('drops_metal_pan'); tt = T['drop0'] + 2.6; q = 0
    while tt < rain_end - 0.5:
        a = pm[q % min(10, len(pm))]
        F.spot('drops_metal_pan', tt, rel=-17, at_peak=True, lead=0.01, start=max(0.0, a[0] - 0.03), length=0.5, hp=500, lp=7000, fi=0.01, fo=0.25, p=0.0, send=-3, trim=False,
               label='a raindrop plinks in the watering can')
        tt += float(rng.uniform(0.9, 1.5)); q += 1
    # ---- soaking in 40.5 to 48.8: the rain sinks into the hill, the brook swells, a paper boat sails, splashes
    F.bed('water_over_soil', T['soak0'] - 3.0, T['gw1'] + 1.0, rel=-23, start=1.0, hp=100, lp=2800, p=-0.3, env=[(T['soak0'] - 3.0, -30), (T['soak0'], 0), (T['soak1'], 0), (T['gw1'] + 1.0, -30)], fi=0.5, fo=1.0,
          label='the water sinks into the soil')
    tt = T['soak0'] - 2.0; q = 0
    while tt < T['gw1']:
        nm = ('drops_2', 'drops_1', 'drops_4')[q % 3]; pc = pieces(nm); pa = pc[(q * 2 + 1) % min(8, len(pc))]
        F.spot(nm, tt, rel=-15, at_peak=True, lead=0.01, start=max(0.0, pa[0] - 0.03), length=0.5, hp=500, lp=6000, fi=0.01, fo=0.3, p=-0.35 + 0.12 * (q % 4), send=-3, trim=False,
               label='a drop sinks down to the water in the sand')
        tt += float(rng.uniform(0.7, 1.15)); q += 1
    F.spot('swirl_water', T['gw1'] - 3.5, rel=-17, start=1.4, length=3.0, lp=3000, hp=150, fi=0.5, fo=0.8, p=-0.35, trim=False, swell=True, label='the water table rises in the sand')
    F.spot('small_cascade', T['swell1'] - 1.5, rel=-18, start=4, length=3.4, lp=3500, hp=150, fi=0.6, fo=0.8, p=-0.1, trim=False, swell=True, label='the brook swells')
    F.spot('water_bubble_2', T['boat0'], rel=-12, at_peak=True, lead=0.01, length=0.5, lp=5000, fo=0.3, send=-4, trim=False, p=-0.4, label='the paper boat is set on the brook')
    F.spot('paper', T['boat0'] - 0.3, rel=-19, start=3.0, length=0.45, hp=1500, lp=7000, fi=0.1, fo=0.2, p=-0.4, trim=False, swell=True, label='paper rustle (the boat)')
    for q, tt in enumerate(landings):
        nm = ('splash_small_2', 'splash_small_4', 'splash_small_5', 'splash_small_6', 'splash_small_3')[q % 5]
        big = tt > T['chord1']
        F.spot('splash_big_1' if big else nm, tt, rel=-9 if not big else -7, at_peak=True, lead=0.015, length=1.1, speed=1.0, hp=300, lp=9000, fi=0.01, fo=0.5,
               p=pan_xy(*PUD), send=-3, trim=False, label='she lands in the puddle: SPLASH')
        F.spot('boing_2', tt - 0.78, rel=-17, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.5, p=pan_xy(*PUD), label='a hop (a soft boing)')
    # ---- the sun again 48.8 to 57: the rain stops, birds, the cloud thins, the rainbow on the big phrase
    F.spot('night_after_rain', T['sunback0'] + 0.5, rel=-24, start=5, length=5.0, hp=300, lp=7000, fi=0.8, fo=1.5, trim=False, swell=True, p=0.2, label='drip, drip: after the rain')
    for k_, tt in enumerate((T['drop1'] + 0.5, T['drop1'] + 1.4, T['drop1'] + 2.5)):
        F.spot(('robin_1', 'blackbird_30', 'robin_1')[k_], tt, rel=-19, p=(-0.5, 0.5, -0.2)[k_], lp=6000, fi=0.05, fo=0.6, send=-4, label='a bird sings again')
    F.spot('cloth', T['drop1'] + 0.3, rel=-19, start=cl_long[0] + 1.5, length=0.9, hp=400, lp=4500, fi=0.1, fo=0.3, p=cdir, trim=False, swell=True, label='the umbrella is shut (cloth)')
    tr = T['rainbow0']
    for k_, tt in enumerate((tr - 0.1, tr + 0.8, tr + 1.6, tr + 2.4)):
        F.spot('chimes_dream_3', tt, rel=-10 - 0.6 * k_, notes=AUTO, lp=9000, fi=0.04, fo=1.6, length=2.6, send=-3, p=-0.6 + 0.4 * k_, label='the rainbow paints itself across the sky (chimes)')
    F.spot('glockenspiel', tr, rel=-9, start=0.0, notes=AUTO, lp=9000, fi=0.02, fo=1.8, length=2.8, send=-3, p=0.0, label='the rainbow arrives (a struck glockenspiel chord, tuned)')
    F.spot('triangle_2', tr + 0.05, rel=-12, notes=AUTO, lp=9000, fi=0.03, fo=1.8, length=3.0, send=-3, p=0.15, label='a soft triangle on the rainbow')
    # ---- around and around 57 to 64.4: the sea glitters, new shimmer rises, a small new cloud
    F.bed('small_waves_ocean', T['sea0'] - 1.0, 73, rel=-24, start=6, hp=150, lp=4500, p=0.55, env=[(T['sea0'] - 1.0, -30), (T['sea0'] + 2, 0), (73, -3)], fi=1.0, fo=2.0, label='the far sea')
    for k_, tt in enumerate((T['vap2a'] + 0.2, T['vap2a'] + 1.9, T['vap2a'] + 3.6)):
        F.spot('chimes_dream_1', tt, rel=-14 - k_, rev=True, notes=AUTO, send=-3, fi=0.4, fo=0.3, p=0.2 * (k_ - 1), swell=True, label='new shimmer rises again (reversed chimes)')
    F.spot('toy_duck', T['sea0'] + 2.5, rel=-14, start=1.45, notes=AUTO, lp=6000, fi=0.03, fo=0.35, length=0.6, p=pan_xy(*LAKE), label='the rubber duck squeaks on the lake')
    F.spot('toy_duck', T['sunback1'] + 6.5, rel=-15, start=1.45, notes=AUTO, lp=6000, fi=0.03, fo=0.35, length=0.6, p=pan_xy(*LAKE), label='the rubber duck squeaks again')
    # ---- your rain 64.4 to 73: the snail waves on the first chord, she jumps on the second
    F.spot('boing_4', T['chord1'] - 0.1, rel=-11, notes=AUTO, lp=3500, fi=0.02, fo=0.3, length=0.7, p=0.65, label='the snail waves')
    F.spot('chimes_butterfly_3', T['chord1'] + 0.1, rel=-14, notes=AUTO, lp=9000, fi=0.04, fo=1.6, length=2.6, send=-3, p=0.2, label='a last twinkle')
    F.spot('robin_1', T['chord2'] + 1.0, rel=-19, p=-0.4, lp=6000, fi=0.05, fo=0.6, send=-4, label='a bird calls over the last chord')
    # ---- words in with a soft pop (every word set in code)
    for w, tw in WORDS:
        tw_in = T['words_end'] + 0.35 if w.startswith('WHERE HAS') else tw + 0.35
        F.spot('wine_stopper_3', tw_in, rel=-16, notes=None, lp=4500, hp=300, fi=0.01, fo=0.2, p=0.0, label='words pop in: ' + w.lower())
    return dict(rain=(t0d, rain_end), rainbow=tr, chords=(T['chord1'], T['chord2']), landings=landings)


# ==================================================================================================================
# 7. MASTER AND MEASURE
# ==================================================================================================================
BANK_RUN = 'rc-render sfx-bank.yml run 40049538821 (24 Oct 2026)'
TARGET_LUFS, TP_LIMIT = -16.0, -1.5
FX_TRIM = 6.0
NLEAF = 32              # the whole effects bus, dB (set by measurement: effects read, the music still leads)


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
    'The umbrella pop is a wine stopper\'s pop plus a soft harp boing tuned to the music: the bank has no umbrella.',
    'The child\'s running is a real soft footstep on short grass (the bank has no wet grass or rubber boots); the puddle splashes are real small splashes.',
    'The snail\'s happy wiggle is a toy squeal and soft boings, panned right: there is no recording of a snail.',
    'The drops that bump and stick in the magnifier are soft water bubbles and bubble bursts (the bank has no cloud droplets); the last join is a soft boing.',
    'The invisible water rising is reversed chimes tuned to the music (a shimmer, not a real sound of vapour).',
    'The tiny drops gathering are a candle sparkle (tiny tinks).',
    'The paper boat is a rustle of paper and a bubble where it touches the water.',
    'The rainbow is a struck glockenspiel, chimes and a triangle, tuned to the orchestra; a rainbow has no sound.',
    'No thunder anywhere (it would frighten the very young); the rain is a soft puddle-rain bed and rain on leaves.',
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
    md = f"""# Sound of the rain film (Little Big Questions, film 3)

A SILENT 73 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
`audio/mix.wav` is ignored; `audio/mix.m4a` is committed with `git add -f` (the runners need it) together with `audio/mix.json`
(measurements, every recording and where it is used, the music edit, the event table, the timelines).

**Music credit (for the description of the video):** {m['credit']}

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- {meas['seconds']:.2f} s, 48 kHz stereo AAC 256k, {meas['lufs']:.1f} LUFS integrated (target {TARGET_LUFS:.0f}), true peak {meas['true_peak']:.2f} dBTP (limit {TP_LIMIT} dBTP), loudness range {meas['lra']:.1f} LU.
- The loudest limiter dip is {meas['limiter_max_reduction_db']:.1f} dB at {meas['limiter_max_reduction_at_s']:.1f} s (the loud river theme); the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; the loudest instant of a footstep or splash sits 10 to 35 ms after the event
  frame, a pop on its frame). On the rendered effects bus alone, {chk['landed']} of {chk['checked']} percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under the river, rain or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
{m['piece']}, {m['recording']}, {m['licence']}. Source: {m['source']}. Asset: {m['asset']}.
{m['edit']}
The music leads. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio {edit_info['ratio']},
gain between {edit_info['gain_min']:+.1f} and {edit_info['gain_max']:+.1f} dB) lifts the whispering opening and eases the sunrise climax so the film can sit near
-16 LUFS; the notes keep their own shape. The music is lowered by at most {edit_info['duck_db']:.1f} dB under the rain and the rainbow.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). The bank is the one extended on 24 Oct 2026 for the kids series: {BANK_RUN}. Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowl, chimes, glock, toy squeak, boings) are tuned by resampling to the
pitch classes the orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
""" + "\n".join(lines) + f"""

## Stand-ins (honest)
""" + "\n".join('- ' + s for s in STANDINS) + """

## Rebuild
`python3 films/cutaway/kids/rain/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
"""
    open(os.path.join(FOSSIL, 'SOUND.md'), 'w').write(md)


# ==================================================================================================================
# 9. MAIN
# ==================================================================================================================
KEY_EVENTS = [('first flutes', None), ('sun warms', 'sun0'), ('vapour rises', 'vapup0'), ('cloud forms', 'cloud0'), ('window opens', 'lens0'), ('last drops join', 'lensj5'),
              ('FIRST RAINDROP', 'drop0'), ('umbrella pops', 'umbrella1'), ('soaking in', 'soak0'), ('rain stops', 'drop1'), ('RAINBOW', 'rainbow0'), ('sea', 'sea0'),
              ('chord 1', 'chord1'), ('chord 2', 'chord2')]

def main():
    T, B, ERAS, bj, WORDS = read_events()
    need = ['birds_waking_3', 'wind_plain', 'forest_stream_1', 'sun_heat_1', 'sparkling_water', 'chimes_butterfly_1', 'chimes_butterfly_3', 'chimes_dream_1', 'chimes_dream_3', 'wind_inside_1',
            'candle_sparkle_1', 'cluster_chimes', 'water_bubble_2', 'bubbles_burst', 'drops_1', 'drops_2', 'drops_3', 'drops_4', 'drops_metal_pan', 'splash_small_2', 'splash_small_3',
            'splash_small_4', 'splash_small_5', 'splash_small_6', 'splash_big_1', 'boing_2', 'boing_4', 'whoosh_3', 'rain_puddle', 'rain_concrete', 'steps_short_grass', 'cloth',
            'wine_stopper_3', 'toy_squeal_1', 'toy_squeal_3', 'toy_duck', 'water_over_soil', 'swirl_water', 'small_cascade', 'paper', 'night_after_rain', 'robin_1', 'blackbird_30',
            'glockenspiel', 'triangle_2', 'small_waves_ocean']
    bank = ensure_bank(need)
    csvp = os.path.join(K.CACHE, 'sfx-bank.csv')
    if not os.path.exists(csvp):
        urllib.request.urlretrieve('https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.csv', csvp)
    mus_raw = music_edit()
    RIDER = dict(target=-27.0, ratio=3.4, sigma=1.4, maxg=17.0, ming=9.0)
    mus, gcur = level_rider(mus_raw, **RIDER)
    mus = (mus * K.envelope([(0, 0), (T['chord1'] - 0.6, 0), (T['chord1'] - 0.25, -10.0), (73, -10.0)])[:, None]).astype(np.float32)      # the piece's two final chords: softer than the rainbow phrase
    F = Film(); F.mus = mus
    info = design(F, T, B, ERAS, WORDS)
    duck_db = -1.5
    t_r = T['drop0']; tb = T['rainbow0']
    duck = [(0, 0), (t_r - 0.3, 0), (t_r + 0.5, duck_db), (T['drop1'] - 1.0, duck_db), (T['drop1'] + 1.5, 0), (tb - 0.2, 0), (tb + 0.3, -1.0), (tb + 3.0, 0), (80, 0)]
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
        ev_list.append((nm, T[k] if k else 0.5))
    tl = timeline(y, musd, fx, ev_list)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(HERE, 'mix.m4a')],
                               capture_output=True, text=True).stdout.strip())
    res['seconds'] = round(dur, 3)
    csvrows = bank_csv()
    edit_info = dict(ratio=RIDER['ratio'], gain_min=float(gcur.min()), gain_max=float(gcur.max()), duck_db=abs(duck_db))
    meas = dict(res, codec='aac 256k stereo 48 kHz', target_lufs=TARGET_LUFS, true_peak_limit_dbtp=TP_LIMIT)
    out = dict(
        film='kids-rain', duration_s=meas['seconds'], measurements=meas,
        music=dict(bj['music'], cut=dict(pieces_rec_s=EDIT['pieces'], crossfades_s=EDIT['xf'], curve='triangular (linear)', fade_out_s=EDIT['fade_out'], tail_trim_db=EDIT['tail_trim_db']),
                   rider=dict(RIDER, gain_db_range=[round(edit_info['gain_min'], 1), round(edit_info['gain_max'], 1)]), duck_points_db=duck, music_only_lufs=round(dsp.loudness(musd), 2)),
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
        for t in range(0, 73):
            pk = max([r['peak_above_music_rms_db'] for r in F.rows if 'peak_above_music_rms_db' in r and t <= r['t'] < t + 1] or [None], key=lambda v: -99 if v is None else v)
            print(f'  {t:2d}-{t + 1:2d}  mix {rms_line(y, t, t + 1):6.1f}  music {rms_line(musd, t, t + 1):6.1f}  fx {rms_line(fx, t, t + 1):6.1f}   gap {rms_line(musd, t, t + 1) - rms_line(fx, t, t + 1):5.1f} dB   top spot {pk}')
    print('timeline (t, mix, music, effects; dBFS per 0.5 s):')
    for r in tl:
        print(f"  {r['event']:<20} @{r['t']:6.2f}:", ' | '.join(f"{a:5.1f}: {m_:5.1f} {mu:5.1f} {e:5.1f}" for a, m_, mu, e in r['windows']))
    return out


if __name__ == '__main__':
    main()
