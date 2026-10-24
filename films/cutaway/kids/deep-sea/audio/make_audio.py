#!/usr/bin/env python3
"""Sound of Little Big Questions, film (deep-sea): a REAL orchestral recording and REAL recorded sound effects (70.5 s).

    python3 films/cutaway/kids/deep-sea/audio/make_audio.py     # writes audio/mix.m4a, audio/mix.json and ../SOUND.md

What it makes (all deterministic; numpy, scipy, soundfile, ffmpeg):
  MUSIC   Mendelssohn, The Hebrides Overture, Musopen Symphony (public domain on Commons), cut exactly as beats.json says
          (recording 0:00.5 to 0:26.0, a 2 s triangular cross-fade into 1:05.0 to 1:42.0, a 2 s cross-fade into 11:07.5 to
          11:20.0; 70.5 s). The music is the voice of the film: foreground. A slow, smooth level rider lifts the quiet
          passages and eases the climax so the film sits near -16 LUFS; it never touches the notes' shape.
  EFFECTS real CC0 recordings (the studio bank, release sfx-bank of Eouchi147/rc-render, BigSoundBank) placed on the
          picture's events. Event times are READ from blender.py (the EVENTS table: beat, seconds into it) and beats.json
          at build time, so a re-timed picture re-times the sound. Soft attacks everywhere, nothing sudden or scary.
  TONAL   the few pitched sounds (chimes, bowl, boings, the duck's squeak) are tuned by resampling to the pitch classes
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
FOSSIL = os.path.dirname(HERE)          # this film's folder (kept under the old name the helpers use)
ROOT = os.path.abspath(os.path.join(FOSSIL, '..', '..', '..', '..'))
SERIES = os.path.join(ROOT, 'films', 'cutaway', 'series')
os.environ['KF_SOUND_DUR'] = '70.5'                      # before audio_kit is imported
sys.path.insert(0, SERIES)
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy.ndimage import gaussian_filter1d  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
import audio_kit as K  # noqa: E402

dsp = K.dsp
SR, N, DUR = K.SR, K.N, K.DUR
db = K.db
MUSIC_URL = 'https://github.com/Eouchi147/rc-render/releases/download/music/mendelssohn-hebrides-musopen.flac'
MUSIC_CACHE = os.path.expanduser('~/.cache/kinoforge/music/mendelssohn-hebrides-musopen.flac')


# ==================================================================================================================
# 1. EVENT TIMES: read from the picture's own table (blender.py EVENTS) and beats.json; nothing is typed twice
# ==================================================================================================================
def _num(node):
    return eval(compile(ast.Expression(node), 'events', 'eval'), {'__builtins__': {}})      # numbers and + - * / only


def read_events():
    """{event: seconds} from blender.py's EVENTS table (beat key, seconds after the beat starts) and beats.json."""
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
        beat, sec = ast.literal_eval(k), (ast.literal_eval(v.elts[0]), _num(v.elts[1]))
        ev[beat] = beats[names[sec[0]]][0] + sec[1]
    words = [(b['words'].strip(), b['t'][0]) for b in bj['beats'] if b.get('words', '').strip()]
    return ev, beats, None, bj, words


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


RIDER = dict(target=-22.0, ratio=3.2, maxg=10.0)
EDIT = dict(a0=0.5, a1=26.0, b0=65.0, b1=102.0, c0=667.5, c1=680.0, xf1=2.0, xf2=2.0)          # recording seconds; beats.json music.edit


def music_edit():
    x, sr = sf.read(music_file(), dtype='float32', always_2d=True)
    assert sr == SR, sr
    A = x[int(EDIT['a0'] * SR):int(EDIT['a1'] * SR)]; Bm = x[int(EDIT['b0'] * SR):int(EDIT['b1'] * SR)]; C = x[int(EDIT['c0'] * SR):int(EDIT['c1'] * SR)]
    L1 = int(EDIT['xf1'] * SR); L2 = int(EDIT['xf2'] * SR)
    r1 = np.linspace(0, 1, L1, dtype=np.float32)[:, None]; r2 = np.linspace(0, 1, L2, dtype=np.float32)[:, None]          # triangular = linear in, linear out
    y = np.concatenate([A[:-L1], A[-L1:] * (1 - r1) + Bm[:L1] * r1, Bm[L1:-L2], Bm[-L2:] * (1 - r2) + C[:L2] * r2, C[L2:]])
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
    rng = np.random.default_rng(23)
    AUTO = 'auto'                                        # tuned to what the orchestra plays at that moment
    px = lambda x: float(np.clip(x / 2.4 * 0.88, -0.6, 0.6))      # the slice's x across the picture (the column is the middle third)
    far = lambda a: float(np.clip(a / 5.5, -0.9, 0.9))            # the world round the slice (a metres to the right of the column)
    DIVE, SURF = T['dive'], T['surf']
    # whale spouts: szworld.B.spouts as blender.py computes them (fractions of beats)
    spouts = [B['hook'][0] + 1.2, B['sunlight zone'][0] + 5.0, B['they glow'][0] + 0.2 * (B['they glow'][1] - B['they glow'][0]),
              B['only a tiny piece'][0] + 0.5, B['back to the surface'][0] + 4.5]

    # ---- the sunny sea above (0 to 5.6 and again from the surfacing): waves, gulls, a ship's bell far away
    above = [(0, 0), (DIVE - 0.2, 0), (DIVE + 1.3, -26), (SURF - 1.0, -26), (SURF + 0.2, 0), (SURF + 2.0, -6)]
    F.bed('small_waves_ocean', 0, 70.5, rel=-17, start=10, hp=100, lp=6000, env=above, fi=1.0, fo=2.5, label='gentle waves on the sunny sea')
    F.bed('gulls_harbor', 0, 70.5, rel=-24, start=30, hp=500, lp=7000, p=0.3, env=[(0, 0), (DIVE - 0.2, 0), (DIVE + 1.0, -30), (SURF + 0.4, -30), (SURF + 1.4, -4), (SURF + 3.0, -10)], fi=1.0, fo=2.5,
          label='gulls over the sea')
    F.spot('sea_tern', 4.0, rel=-18, p=-0.45, lp=6000, hp=400, length=1.6, fi=0.05, fo=0.5, send=-4, label='a tern calls')
    F.spot('bell_1oclock', 3.7, rel=-22, p=far(5.0), lp=4000, hp=350, length=2.0, fi=0.02, fo=0.9, send=-5, label='the boat rings a far soft bell')
    for te in spouts:
        F.spot('blow_1', te + 0.15, rel=-17, p=far(4.9), lp=2800, hp=150, length=1.6, speed=0.8, fi=0.2, fo=0.9, send=-5, trim=False, swell=True, label='the whale blows a far soft spout')
    # the duck squeaks as it bobs; the snail's porthole
    for k, tt in enumerate((T['duck_hop0'], T['duck_hop1'])):
        F.spot('toy_duck', tt, rel=-9 - 2 * k, notes=AUTO, lp=6500, fi=0.02, fo=0.3, length=0.7, p=px(-0.62), label='the rubber duck squeaks as it hops')

    # ---- the dive 5.6: splash, a ring of bubbles; the fish school, the turtle
    F.spot('splash_big_1', DIVE + 0.1, rel=-7, at_peak=True, lead=0.03, p=px(0.05), lp=8000, hp=150, length=2.4, fi=0.01, fo=1.2, label='the submarine dives in: a splash')
    F.spot('water_bubbles', DIVE + 0.25, rel=-12, p=px(0.0), length=2.6, hp=300, lp=7000, fi=0.05, fo=1.0, trim=False, label='a ring of bubbles')
    F.bed('underwater', DIVE + 0.8, SURF - 0.6, rel=-22, start=5, hp=60, lp=5000, env=[(DIVE + 0.8, -20), (DIVE + 2.0, 0), (20.0, 0), (24.0, -8), (60.0, -8), (63.0, -4), (SURF - 0.6, -20)],
          fi=1.2, fo=1.0, label='under the water (a soft hum)')
    for j, tt in enumerate((7.4, 9.1, 11.0, 12.3)):
        F.spot(('water_bubble_2', 'drops_1', 'water_bubble_2', 'drops_2')[j], tt, rel=-17, p=px(0.45 - 0.2 * j), lp=6500, hp=300, length=0.5, fi=0.01, fo=0.25, label='the fish school flutters past')
    F.spot('swirl_water', 8.2, rel=-23, p=px(-0.1), length=2.8, lp=2800, hp=120, fi=0.6, fo=0.9, trim=False, swell=True, label='the turtle paddles by (a slow swirl)')

    # ---- twilight 13.5: the sun rays run out; the lanterns light on the swell at 16.9; the next swell at 20.4
    F.spot('whoosh_long_1', T['twi0'] - 0.2, rel=-22, p=-0.2, lp=1800, hp=100, length=3.0, fi=1.0, fo=1.0, trim=False, swell=True, label='the water hums lower as the sun fades')
    for j, (dt, nm, rl) in enumerate(((0.0, 'chimes_dream_1', -9), (0.30, 'chimes_butterfly_1', -12), (0.62, 'chimes_dream_3', -14), (0.95, 'chimes_butterfly_3', -16))):
        F.spot(nm, T['lant0'] + dt, rel=rl, notes=AUTO, lp=9500, hp=500, length=1.8, fi=0.02, fo=1.0, p=px(0.3 - 0.25 * j), send=-3, label='the lantern fish switch on (tiny chimes)')
    F.bed('sparkling_water', T['lant0'], T['lant1'], rel=-27, start=3, hp=1500, lp=9000, p=0.1, fi=0.8, fo=1.2, env=[(T['lant0'], -6), (T['lant0'] + 1.5, 0), (T['lant1'] - 1.5, 0), (T['lant1'], -20)],
          label='a shimmer of tiny lights')
    F.spot('chimes_dream_3', T['B_j3'], rel=-12, notes=AUTO, lp=9000, hp=500, length=1.8, fi=0.02, fo=1.0, p=px(0.4), send=-3, label='a pale jellyfish lights up in the twilight')

    # ---- midnight 20.5: the headlamp clicks on, a bubble, deep quiet
    F.spot('lock', 21.0, rel=-9, at_peak=True, lead=0.01, length=0.4, hp=500, lp=4500, fi=0.005, fo=0.15, p=px(0.05), label='the submarine\'s headlamp clicks on')
    F.spot('chimes_dream_1', 21.1, rel=-17, notes=AUTO, lp=8000, length=1.5, fi=0.03, fo=0.9, p=px(0.05), send=-3, label='the lamp\'s soft glow')
    F.bed('cave_soundscape_1', 20.4, 63.0, rel=-25, start=20, hp=80, lp=1800, p=0.0, send=-8, env=[(20.4, -20), (22.5, 0), (60.0, 0), (63.0, -10)], fi=1.5, fo=2.0, label='the deep quiet of the midnight zone')
    F.spot('water_bubble_2', 24.0, rel=-17, p=px(-0.3), lp=4500, length=0.6, fi=0.01, fo=0.3, label='one slow bubble')

    # ---- they glow 26.5: a chime for each jellyfish as its light blooms
    for tt, nm, pn, rl in ((T['B_j0'], 'chimes_butterfly_1', px(-0.56), -8), (T['B_j1'], 'chimes_dream_1', px(0.62), -9), (T['B_j2'], 'chimes_butterfly_3', px(-0.05), -9)):
        F.spot(nm, tt, rel=rl, notes=AUTO, lp=10000, hp=400, length=2.0, fi=0.03, fo=1.2, p=pn, send=-2, label='a jellyfish lights up (a glass chime)')
        F.spot('water_bubbles', tt + 0.1, rel=-20, p=pn, length=1.2, lp=5000, hp=400, fi=0.05, fo=0.6, trim=False, label='a burble as it glows')
    for j, tt in enumerate((27.9, 29.0, 30.9, 31.9, 32.6)):
        F.spot('candle_sparkle_1' if j % 2 == 0 else 'candle_sparkle_2', tt, rel=-19, p=px(float(rng.uniform(-0.8, 0.8))), lp=9000, hp=900, length=1.2, fi=0.02, fo=0.6, send=-3,
               label='tiny sparkles twinkle round the jellyfish')

    # ---- the squid 33.7, the bottle, the snail waves
    F.spot('whoosh_5', T['sq0'] - 0.1, rel=-15, sweep=(0.6, 0.2), lp=4500, hp=300, length=1.4, fi=0.2, fo=0.5, trim=False, swell=True, label='the squid zips in')
    F.spot('toy_squeal_1', T['sq0'] + 0.5, rel=-13, notes=AUTO, lp=6000, length=0.5, fi=0.01, fo=0.2, p=px(0.5), label='the squid squeaks')
    F.spot('water_bubble_2', T['sq0'] + 1.8, rel=-14, p=px(0.1), length=0.5, lp=5500, fo=0.2, label='a bubble pop as it blinks its spots')
    F.spot('whoosh_4', T['sq1'] - 0.3, rel=-16, sweep=(-0.2, -0.7), lp=4500, hp=300, length=1.4, fi=0.2, fo=0.5, trim=False, swell=True, label='the squid zips away')
    for j, tt in enumerate((T['bot0'], T['bot1'])):
        F.spot('wine_stopper_3', tt + 0.4, rel=-17, speed=0.75, lp=3500, hp=250, length=0.5, fi=0.01, fo=0.25, p=px(0.6 - 1.2 * j), label='the bottle\'s cork bobs')
        F.spot('drops_3', tt + 1.6, rel=-18, p=px(0.4 - 0.9 * j), lp=6000, hp=400, length=0.6, fi=0.01, fo=0.3, label='the bottle bobs by')
    for j, nm in enumerate(('snwave0', 'snwave1', 'snwave2', 'snwave3')):
        F.spot('boing_4' if j % 2 == 0 else 'boing_2', T[nm], rel=-13, notes=AUTO, lp=3800, hp=200, length=0.7, fi=0.02, fo=0.3, p=px(-0.1), label='the snail waves')

    # ---- the lantern 40: the anglerfish slides out; the lamp blinks off; the lure lights the submarine like a torch
    F.spot('boing_6', T['an0'] + 0.5, rel=-12, notes=AUTO, lp=3800, length=0.8, fi=0.02, fo=0.3, p=px(-0.85), label='a cheerful boing: the friendly anglerfish swims out')
    F.spot('whoosh_10', T['an0'] - 0.2, rel=-23, p=px(-0.9), lp=2500, hp=120, length=2.0, fi=0.5, fo=0.8, trim=False, swell=True, label='it glides out of the dark')
    F.spot('lock', T['lamp_off'], rel=-11, at_peak=True, lead=0.01, length=0.4, hp=500, lp=4500, fi=0.005, fo=0.15, p=px(-0.1), label='the headlamp blinks off')
    F.spot('tibetan_bowl_2', T['lure0'] - 0.1, rel=-11, notes=F.auto_notes(T['lure0'], dur=4.0, kmax=2), lp=5500, hp=100, length=5.0, fi=0.4, fo=2.2, trim=False, p=px(-0.5), send=-2, swell=True,
           label='the lure lights up (a warm bowl)')
    F.spot('chimes_dream_3', T['lure0'] + 0.2, rel=-10, notes=AUTO, lp=9500, hp=500, length=2.0, fi=0.02, fo=1.2, p=px(-0.4), send=-3, label='the torch lights the submarine (a chime)')
    F.spot('water_bubbles', T['lure0'] + 1.0, rel=-18, p=px(-0.3), length=1.4, lp=5000, hp=400, fi=0.05, fo=0.6, trim=False, label='a bubble giggle')
    F.spot('lock', T['lamp_on'], rel=-11, at_peak=True, lead=0.01, length=0.4, hp=500, lp=4500, fi=0.005, fo=0.15, p=px(-0.1), label='the headlamp clicks back on')
    F.spot('water_bubble_2', T['lure1'] + 0.1, rel=-14, p=px(-0.6), length=0.5, lp=5500, fo=0.2, label='the lure dims with a bubble pop')

    # ---- hot vents 47: a warm low rumble, bubbling, the submarine settles on the sand, the chest sparkles
    F.bed('boiling_water', T['vent0'] + 0.5, T['bloom0'] + 3.0, rel=-23, start=15, hp=120, lp=1600, p=px(0.5), send=-6, env=[(T['vent0'] + 0.5, -20), (T['vent0'] + 2.5, 0), (T['bloom0'], 0), (T['bloom0'] + 3.0, -18)],
          fi=1.0, fo=1.5, label='the hot vent bubbles')
    F.spot('thunder_8', T['vent0'] + 0.1, rel=-19, p=px(0.5), lp=170, hp=25, length=4.0, fi=1.0, fo=1.8, trim=False, swell=True, label='a low warm rumble from the vent')
    F.spot('steam_hiss_1', T['vent0'] + 0.9, rel=-26, p=px(0.5), lp=3200, hp=600, length=3.0, fi=0.7, fo=1.2, trim=False, swell=True, label='warm steam')
    om = onsets('steps_mud')
    F.spot('steps_mud', 52.4, rel=-8, at_peak=True, lead=0.02, start=max(0.0, om[1] - 0.06), length=0.6, speed=0.75, lp=900, hp=60, fi=0.02, fo=0.35, p=px(-0.16), trim=False,
           label='the submarine settles on the sand (soft thump)')
    F.spot('body_fall_1', 52.45, rel=-13, at_peak=True, lead=0.03, speed=0.6, lp=500, hp=40, fi=0.03, fo=0.4, p=px(-0.16), trim=False, label='a soft settle')
    F.spot('chimes_butterfly_1', T['chest0'], rel=-12, notes=AUTO, lp=9500, hp=500, length=1.8, fi=0.02, fo=1.0, p=px(-0.3), send=-3, label='the treasure chest sparkles')
    F.spot('creaking_door_1', T['chest0'] - 0.1, rel=-24, speed=1.3, lp=3000, hp=300, length=0.7, fi=0.1, fo=0.3, p=px(-0.3), trim=False, swell=True, label='a toy chest lid creaks')

    # ---- the climax 55: every light at once, a cascade of chimes
    tcl = T['bloom0']
    F.spot('chimes_butterfly_1', tcl, rel=-4, notes=AUTO, lp=10000, fi=0.03, fo=1.5, send=-2, p=0.0, label='ALL THE LIGHTS: the chime that starts the cascade')
    cw = loud_windows('cluster_chimes', 2.5, 1, hop=0.5, start=0.0, stop=120.0)[0]
    F.spot('cluster_chimes', tcl + 0.04, rel=-8, start=cw, length=2.6, notes=AUTO, lp=10000, fi=0.08, fo=1.5, send=-2, trim=False, swell=True, label='ALL THE LIGHTS: a burst of gold stars')
    F.spot('glockenspiel', tcl + 0.08, rel=-8, start=0.0, lp=9000, fi=0.02, fo=1.8, length=2.8, send=-3, p=-0.1, notes=F.auto_notes(tcl, dur=1.2, kmax=2), label='ALL THE LIGHTS: sparkle (a struck glockenspiel chord, tuned)')
    F.spot('tibetan_bowl_1', tcl, rel=-10, at_peak=True, lead=0.0, notes=F.auto_notes(tcl, dur=3.0, kmax=2), lp=5500, fi=0.05, fo=3.0, length=5.5, trim=False, send=-2, swell=True,
           label='ALL THE LIGHTS: a singing bowl swells')
    for j in range(9):
        tt = tcl + 0.45 + 0.42 * j
        F.spot(('chimes_dream_1', 'chimes_butterfly_3', 'chimes_dream_3')[j % 3], tt, rel=-12 - 0.5 * j, notes=AUTO, lp=9500, hp=500, length=1.6, fi=0.02, fo=1.0,
               p=float(np.clip(rng.uniform(-0.6, 0.6), -0.6, 0.6)), send=-3, label='another light twinkles on')

    # ---- only a tiny piece 59.5: the lights go out one by one, a small torch-patch of seafloor, a question
    for j, (dt, rl) in enumerate(((0.3, -13), (0.95, -15), (1.7, -17), (2.4, -19))):
        F.spot('chimes_dream_3', T['unseen0'] + dt, rel=rl, notes=AUTO, lp=8500, hp=500, length=1.5, fi=0.02, fo=0.9, p=0.45 - 0.3 * j, send=-3, label='a light goes out (a falling chime)')
    F.spot('water_bubble_2', T['unseen0'] + 3.4, rel=-15, p=px(0.3), lp=5000, length=0.6, fi=0.01, fo=0.3, label='a questioning bubble')
    F.spot('tibetan_bowl_3', 63.0, rel=-10, at_peak=True, lead=0.0, notes=F.auto_notes(63.0, dur=2.5, kmax=2), lp=5000, fi=0.05, fo=3.0, length=5.0, trim=False, send=-2, swell=True,
           label='the first closing chord: the torch shows only a little')
    F.spot('whoosh_long_2', 63.8, rel=-24, p=px(0.3), lp=1800, hp=100, length=2.4, fi=0.6, fo=0.8, trim=False, swell=True, label='the submarine rises')

    # ---- back to the surface 64.5: the pop out of the water on the last chord, the snail waves, the duck, the sunset
    F.spot('splash_big_2', SURF, rel=-6, at_peak=True, lead=0.03, p=px(0.3), lp=8500, hp=150, length=2.6, fi=0.01, fo=1.3, label='the submarine pops out of the sea')
    F.spot('chimes_butterfly_3', SURF - 0.1, rel=-9, notes=AUTO, lp=9500, fi=0.03, fo=1.8, send=-3, p=0.2, label='the surface: a warm chime on the last chord')
    for k, tt in enumerate((T['end_duck0'], T['end_duck1'])):
        F.spot('toy_duck', tt, rel=-12 - 2 * k, notes=AUTO, lp=6500, fi=0.02, fo=0.3, length=0.7, p=px(-0.62), label='the rubber duck greets the submarine')
    F.spot('sea_tern', SURF + 0.6, rel=-19, p=0.4, lp=6000, hp=400, length=1.6, fi=0.05, fo=0.6, send=-4, label='a gull calls at sunset')
    for tt in (T['end_wave0'], T['end_wave1']):
        F.spot('boing_4', tt, rel=-14, notes=AUTO, lp=3800, hp=200, length=0.7, fi=0.02, fo=0.3, p=px(0.3), label='the snail waves goodbye')

    # ---- words in with a soft pop (every word set in code)
    for w, tw in WORDS:
        tw_in = T['words_send'] if w.startswith('WHAT ELSE') else (0.35 if w.startswith('WHAT LIVES') else tw + 0.35)
        F.spot('wine_stopper_3', tw_in, rel=-16, notes=None, lp=4500, hp=300, fi=0.01, fo=0.2, p=0.0, label='words pop in: ' + w.lower())
    return dict(climax=tcl)


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
        pre = mix * db(gain); y0 = dsp.limiter(pre, ceil)
        y = K.fades(y0, 0.06, 0.35)
        sf.write(wav, y, SR, subtype='PCM_24')
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'aac', '-b:a', '256k', '-ar', str(SR), '-ac', '2',
                        '-movflags', '+faststart', m4a], check=True)
        res = ebur128(m4a)
        eI = TARGET_LUFS - res['lufs']; eP = res['true_peak'] - (TP_LIMIT - 0.05)
        print(f'  pass {it}: {res["lufs"]:.2f} LUFS, true peak {res["true_peak"]:.2f} dBTP, gain {gain:.2f} dB, ceiling {ceil:.2f}')
        if abs(eI) <= 0.2 and eP <= 0: break
        gain += 0.85 * eI
        if eP > 0: ceil -= eP + 0.05
    a_ = np.abs(pre).max(1); b_ = np.abs(y0).max(1); ok_ = a_ > 0.02; red = np.where(ok_, 20 * np.log10((a_ + 1e-9) / (b_ + 1e-9)), 0.0)
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
    'The submarine\'s headlamp click is the click of a real lock, shortened: there is no recording of a little submarine.',
    'The whale\'s spout is a real soft blow (an exhale), slowed and low-passed, far away: there is no recording of a whale.',
    'The squid\'s squeak is a small toy squeal; its zip is a real whoosh. No recording of a squid exists in the bank.',
    'The anglerfish\'s cheerful boing is a real soft boing, tuned to the music; the lure\'s glow is a singing bowl swell with real chimes.',
    'The hot vent is boiling water, low-passed, a very low rolling thunder and a breath of steam: there is no recording of a hydrothermal vent.',
    'The sub settling on the sand is a slowed soft mud step and a slowed body fall (no recording of a small submarine landing).',
    'The turtle\'s paddle is a slow swirl of real water; the fish school is real water drops and bubbles; the bottle\'s cork is a wine stopper slowed.',
    'The boat\'s far bell is a real church bell striking once, low-passed and far away; gulls and the tern are real recordings.',
    'The glockenspiel is a real struck chord tuned to the orchestra\'s pitch classes at the climax (a recording shifted, not played in the key).',
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
    md = f"""# Sound of the deep-sea film (Little Big Questions)

A SILENT 70.5 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
Audio never goes into git: `audio/mix.m4a` and `audio/mix.wav` are ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** {m['credit']}

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- {meas['seconds']:.2f} s, 48 kHz stereo AAC 256k, {meas['lufs']:.1f} LUFS integrated (target {TARGET_LUFS:.0f}), true peak {meas['true_peak']:.2f} dBTP (limit {TP_LIMIT} dBTP), loudness range {meas['lra']:.1f} LU.
- The loudest limiter dip is {meas['limiter_max_reduction_db']:.1f} dB at {meas['limiter_max_reduction_at_s']:.1f} s (the climax of the Hebrides, where every light comes on); the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; the loudest instant of a splash or a thump sits 10 to 35 ms after the event
  frame). On the rendered effects bus alone, {chk['landed']} of {chk['checked']} percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under the river, rain or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
{m['piece']}, {m['recording']}, {m['licence']}. Source: {m['source']}. Asset: {m['asset']}.
Recording 0:00.5 to 0:26.0, a triangular (linear in, linear out) cross-fade of 2.0 s (film 23.5 to 25.5) into recording 1:05.0 to 1:42.0,
then a 2.0 s cross-fade (film 58.5 to 60.5) into recording 11:07.5 to 11:20.0; 70.5 s. The music leads. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio {edit_info['ratio']},
gain between {edit_info['gain_min']:+.1f} and {edit_info['gain_max']:+.1f} dB) lifts the whispering opening and the hush of the midnight zone and eases the climax so the film can sit near
-16 LUFS; the notes keep their own shape. The music is lowered by at most {edit_info['duck_db']:.1f} dB under the climax cascade of chimes.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). The bank is the one extended on 24 Oct 2026 with the BigSoundBank ids of
`docs/research/KIDS_MUSIC_2026-10.md` section 5.1 (soft boings, chimes, bowls, soft steps, splashes):
{BANK_RUN}. Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowls, chimes, glock, toy squeaks, boings) are tuned by resampling to the
pitch classes the orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
""" + "\n".join(lines) + f"""

## Stand-ins (honest)
""" + "\n".join('- ' + s for s in STANDINS) + """

## Rebuild
`python3 films/cutaway/kids/deep-sea/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
"""
    open(os.path.join(FOSSIL, 'SOUND.md'), 'w').write(md)


# ==================================================================================================================
# 9. MAIN
# ==================================================================================================================
KEY_EVENTS = [('title', None), ('dive', 'dive'), ('lanterns light', 'lant0'), ('lamp on', None), ('first jellyfish', 'B_j0'), ('squid', 'sq0'), ('lure lights', 'lure0'),
              ('vent', 'vent0'), ('sub settles', None), ('ALL THE LIGHTS', 'bloom0'), ('lights go out', 'unseen0'), ('first closing chord', None), ('surfacing', 'surf'), ('last words', 'words_send')]
KEY_AT = {'title': 0.35, 'lamp on': 21.0, 'sub settles': 52.4, 'first closing chord': 63.0}


def main():
    T, B, ERAS, bj, WORDS = read_events()
    need = ['small_waves_ocean', 'gulls_harbor', 'sea_tern', 'bell_1oclock', 'blow_1', 'toy_duck', 'splash_big_1', 'splash_big_2', 'water_bubbles', 'underwater', 'water_bubble_2',
            'drops_1', 'drops_2', 'drops_3', 'swirl_water', 'whoosh_long_1', 'whoosh_long_2', 'whoosh_4', 'whoosh_5', 'whoosh_10', 'chimes_dream_1', 'chimes_dream_3',
            'chimes_butterfly_1', 'chimes_butterfly_3', 'sparkling_water', 'lock', 'cave_soundscape_1', 'candle_sparkle_1', 'candle_sparkle_2', 'toy_squeal_1', 'wine_stopper_3',
            'boing_2', 'boing_4', 'boing_6', 'tibetan_bowl_1', 'tibetan_bowl_2', 'tibetan_bowl_3', 'boiling_water', 'thunder_8', 'steam_hiss_1', 'steps_mud', 'body_fall_1',
            'creaking_door_1', 'cluster_chimes', 'glockenspiel']
    bank = ensure_bank(need)
    csvp = os.path.join(K.CACHE, 'sfx-bank.csv')
    if not os.path.exists(csvp):
        urllib.request.urlretrieve('https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.csv', csvp)
    mus_raw = music_edit()
    mus, gcur = level_rider(mus_raw, target=RIDER['target'], ratio=RIDER['ratio'], maxg=RIDER['maxg'])
    F = Film(); F.mus = mus
    info = design(F, T, B, ERAS, WORDS)
    climax = info['climax']
    duck_db = -1.5
    duck = [(0, 0), (climax - 0.05, 0), (climax + 0.15, duck_db), (climax + 1.8, -1.0), (climax + 3.2, 0), (70.5, 0)]
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
        ev_list.append((nm, T[k] if k else KEY_AT[nm]))
    tl = timeline(y, musd, fx, ev_list)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(HERE, 'mix.m4a')],
                               capture_output=True, text=True).stdout.strip())
    res['seconds'] = round(dur, 3)
    csvrows = bank_csv()
    edit_info = dict(ratio=RIDER['ratio'], gain_min=float(gcur.min()), gain_max=float(gcur.max()), duck_db=abs(duck_db))
    meas = dict(res, codec='aac 256k stereo 48 kHz', target_lufs=TARGET_LUFS, true_peak_limit_dbtp=TP_LIMIT)
    out = dict(
        film='kids-deep-sea', duration_s=meas['seconds'], measurements=meas,
        music=dict(bj['music'], cut=dict(first=[EDIT['a0'], EDIT['a1']], second=[EDIT['b0'], EDIT['b1']], crossfade_s=[EDIT['xf1'], EDIT['xf2']], crossfade_film_s=[[23.5, 25.5], [58.5, 60.5]],
                                          third=[EDIT['c0'], EDIT['c1']], curve='triangular (linear)'), rider=dict(target_lufs=RIDER['target'], ratio=RIDER['ratio'], smoothing_s=1.0, gain_db_range=[round(edit_info['gain_min'], 1), round(edit_info['gain_max'], 1)]),
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
        for t in range(0, 70):
            pk = max([r['peak_above_music_rms_db'] for r in F.rows if 'peak_above_music_rms_db' in r and t <= r['t'] < t + 1] or [None], key=lambda v: -99 if v is None else v)
            print(f'  {t:2d}-{t + 1:2d}  mix {rms_line(y, t, t + 1):6.1f}  music {rms_line(musd, t, t + 1):6.1f}  fx {rms_line(fx, t, t + 1):6.1f}   gap {rms_line(musd, t, t + 1) - rms_line(fx, t, t + 1):5.1f} dB   top spot {pk}')
    print('timeline (t, mix, music, effects; dBFS per 0.5 s):')
    for r in tl:
        print(f"  {r['event']:<20} @{r['t']:6.2f}:", ' | '.join(f"{a:5.1f}: {m_:5.1f} {mu:5.1f} {e:5.1f}" for a, m_, mu, e in r['windows']))
    return out


if __name__ == '__main__':
    main()
