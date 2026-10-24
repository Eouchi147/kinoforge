#!/usr/bin/env python3
"""Sound of Little Big Questions, film 5 (shooting star): a REAL orchestral recording and REAL recorded sound effects (68.4 s).

    python3 films/cutaway/kids/shooting-star/audio/make_audio.py     # writes audio/mix.m4a, audio/mix.json and ../SOUND.md

What it makes (all deterministic; audio never goes into git except mix.m4a, see SOUND.md):
  MUSIC   Grieg, Anitra's Dance (Peer Gynt Suite No. 1), Musopen Symphony (public domain), cut on its bar lines (one bar =
          1.3065 s) into four pieces and joined by triangular (linear in, linear out) cross-fades: the introduction, the theme,
          the plucked build and its full-orchestra peak, and the dance's own ending (the mapping is in szevents.py and beats.json).
          The music is the voice of the film: foreground. A slow, smooth level rider (no pumping, 1 s smoothing) lifts the
          whispering parts and eases the peak so the film sits near -16 LUFS; it never touches the notes' shape.
  EFFECTS real CC0 recordings (the studio bank, release sfx-bank of Eouchi147/rc-render, BigSoundBank) placed on the
          picture's events. Event times are READ from szevents.py (the one events table the picture uses too) and beats.json at
          build time, so a re-timed picture re-times the sound. Soft attacks everywhere, nothing sudden or scary.
  TONAL   the pitched sounds (chimes, triangle, glockenspiel, bowl, boings) are tuned by resampling to the pitch classes the
          orchestra plays at that moment (read from the recording), so they ring with it and never against it.
  BEDS    chosen by low crest factor (a stretch without a stray knock) and set by RMS against the music.
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
os.environ['KF_SOUND_DUR'] = '68.4'                      # before audio_kit is imported
sys.path.insert(0, SERIES)
sys.path.insert(0, FILM)
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from scipy.ndimage import gaussian_filter1d  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402
import audio_kit as K  # noqa: E402
import szevents as EV  # noqa: E402       (pure python: the one events table of the picture)

dsp = K.dsp
SR, N, DUR = K.SR, K.N, K.DUR
db = K.db
MUSIC_URL = 'https://github.com/Eouchi147/rc-render/releases/download/music/grieg-anitra-musopen.flac'
MUSIC_CACHE = os.path.expanduser('~/.cache/kinoforge/music/grieg-anitra-musopen.flac')


# ==================================================================================================================
# 1. EVENT TIMES: the picture's own table (szevents.py: beat name + seconds after the beat starts) and beats.json
# ==================================================================================================================
def read_events():
    """({event: film seconds}, {beat: (t0, t1)}, beats.json, [(words, t_in)])."""
    bj = json.load(open(os.path.join(FILM, 'beats.json')))
    beats = {b['name']: (float(b['t'][0]), float(b['t'][1])) for b in bj['beats']}
    ev = {k: beats[b][0] + float(s) for k, (b, s) in EV.EVENTS.items()}
    t_in = {'streak': ev['peak'], 'send': ev['words_send']}
    words = [(b['words'].strip(), t_in.get(b['name'], float(b['t'][0]) + 0.35)) for b in bj['beats'] if b.get('words', '').strip()]
    return ev, beats, bj, words



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
# 3. THE MUSIC: the edit of beats.json (cut on bar lines, one-bar cross-fades), then a slow level rider
# ==================================================================================================================
def music_file():
    p = os.environ.get('MUSIC_FLAC') or MUSIC_CACHE
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        print('downloading the recording (once):', MUSIC_URL)
        urllib.request.urlretrieve(MUSIC_URL, p + '.part'); os.replace(p + '.part', p)
    return p


BAR = EV.BAR
# the pieces: (recording start, recording end, film start); the next piece's cross-fade window is where they overlap
EDIT = dict(
    pieces=[(0.00, 3.60 + 0.25, 0.00), (5.18 - 0.25, 30.05, 3.60 - 0.25), (88.84, 120.19, 27.16), (226.06, 237.30 + 0.5, 57.20)],
    fades=[(3.60 - 0.25, 3.60 + 0.25), (27.16, 27.16 + BAR), (57.20, 57.20 + BAR)],
)


def music_edit():
    x, sr = sf.read(music_file(), dtype='float32', always_2d=True)
    assert sr == SR, sr
    y = np.zeros((N, 2), np.float32)
    for k, (r0, r1, f0) in enumerate(EDIT['pieces']):
        seg = x[int(round(r0 * SR)):int(round(r1 * SR))].copy(); n = len(seg); t = np.arange(n) / SR + f0
        g = np.ones(n, np.float32)
        if k > 0:                                    # fade in over the window that joins it to the piece before
            a, b = EDIT['fades'][k - 1]; g *= np.clip((t - a) / (b - a), 0, 1).astype(np.float32)
        if k < len(EDIT['fades']):                   # fade out over the window that joins it to the next
            a, b = EDIT['fades'][k]; g *= np.clip(1 - (t - a) / (b - a), 0, 1).astype(np.float32)
        i = int(round(f0 * SR)); m = min(n, N - i)
        if m > 0: y[i:i + m] += seg[:m] * g[:m, None]
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




def nth(name, i):
    """The i-th onset (s, wrapping round) of a recording: a way to pick a different hit each time without listening."""
    o = onsets(name)
    return o[i % len(o)]



# ==================================================================================================================
# 6. THE SOUND OF THE FILM: every event of the picture, in time order
# ==================================================================================================================
def design(F, T, B, WORDS):
    """Every level is `rel`: the clip's peak in dB against the music's RMS around the event (rmsrel / bed rel for steady sounds).
    Positions (metres, szworld): fire (0.05, -0.12), tent (-1.05, 0.42), telescope (1.10, -0.28), owl tree (1.42, 0.72), snail (1.38, -0.98)."""
    rng = np.random.default_rng(68)
    AUTO = 'auto'                                        # tuned to what the orchestra plays at that moment
    FIRE, TENT, TELE, TREE, SNAIL = (0.05, -0.12), (-1.05, 0.42), (1.10, -0.28), (1.42, 0.72), (1.38, -0.98)
    pf, pt, pe, po, ps = (pan_of(*q) for q in (FIRE, TENT, TELE, TREE, SNAIL))
    pk = T['peak']

    # ---- beds: the fire all film long, crickets as the dusk turns to night, a few last evening birds, a breath of night air
    F.bed('fireplace_1', 0, DUR, rel=-17, start=6, hp=120, lp=7500, p=pf, env=[(0, -30), (1.5, 0), (pk, 0), (pk + 3, -2), (DUR, -2)], fi=1.5, fo=2.0, label='the campfire crackles all film')
    F.bed('evening_birds', 0, 9.5, rel=-19, start=30, hp=500, lp=9000, env=[(0, 0), (4.0, -2), (8.0, -30)], fi=0.4, fo=1.5, label='the last evening birds')
    F.bed('field_cricket', 3.0, DUR, rel=-21, start=5, hp=1200, lp=9000, p=-0.25,
          env=[(3.0, -30), (10.0, -6), (16.0, 0), (T['gasp'] - 0.3, 0), (T['gasp'] + 0.1, -6), (T['gasp'] + 3.5, -2), (T['hush0'], 0), (T['hush0'] + 0.6, 4), (T['hush1'], 4), (T['hush1'] + 1.0, 0), (DUR, -3)],
          fi=1.5, fo=1.5, label='crickets as the night comes (louder in the breath of stillness)')
    F.bed('wind_plain', 14.0, DUR, rel=-27, start=20, hp=150, lp=2600, p=0.2, env=[(14, -30), (20, 0), (DUR, 0)], fi=2.0, fo=2.0, label='a soft night breeze')
    for k, tc in enumerate((2.2, 5.6, 11.4, 17.0, 23.3, 31.5, 37.0, 47.4, 52.8, 60.3, 64.2)):
        F.spot('fire_branching_1', tc, rel=-16 - (k % 3), at_peak=True, lead=0.02, start=max(0.0, nth('fire_branching_1', 3 * k + 1) - 0.06), length=0.5, hp=300, lp=6500, fi=0.01, fo=0.2,
               p=pf + 0.05 * (k % 3 - 1), trim=False, label='a crackle from the fire')

    # ---- hook 0 to 4.9: the snail looks up through its tiny telescope; dad lifts a marshmallow on a stick
    F.spot('boing_6', T['snail_up0'] + 0.3, rel=-17, notes=AUTO, lp=4000, fi=0.02, fo=0.3, length=0.6, p=ps, label='the snail lifts its tiny telescope (a little boing)')
    for k, ts in enumerate((1.0, 2.2, 3.2)):
        F.spot('candle_sparkle_1', ts, rel=-24, start=2.0 + 5.0 * k, length=0.8, hp=2500, lp=9000, fi=0.1, fo=0.4, p=-0.5 + 0.5 * k, trim=False, swell=True, label='the first stars wink on')
    F.spot('brush_wood', T['toast0'], rel=-19, start=loud_windows('brush_wood', 0.5, 1, hop=0.25)[0], length=0.5, hp=500, lp=5500, fi=0.08, fo=0.2, p=pf - 0.25, trim=False, swell=True,
           label='dad holds a marshmallow on a stick to the fire (a soft swish)')

    # ---- look 4.9 to 8.8: the dance begins; a small streak zips by on the bar line; everyone looks up
    z0 = T['streak1_0']
    F.spot('whoosh_10', z0 + 0.35, rel=-13, at_peak=True, lead=0.0, hp=900, lp=9000, fi=0.01, fo=0.25, sweep=(0.5, -0.8), trim=False, label='a small streak zips across the sky')
    F.spot('chimes_dream_1', z0 + 0.05, rel=-11, notes=AUTO, lp=9000, fi=0.02, fo=0.9, length=1.6, p=0.1, send=-3, label='the little streak sings (chimes tuned to the music)')
    F.spot('candle_sparkle_2', z0 + 0.2, rel=-20, start=4.0, length=1.0, hp=2500, lp=9500, fi=0.05, fo=0.5, p=-0.2, trim=False, swell=True, label='sparkle in its wake')
    F.spot('cloth', T['point0'], rel=-20, start=pieces('cloth')[0][0] + 0.2, length=0.7, hp=400, lp=4500, fi=0.1, fo=0.25, p=-0.1, trim=False, swell=True, label='everyone looks up (cloth rustle)')
    F.spot('toy_squeal_1', T['point0'] + 0.1, rel=-19, notes=AUTO, lp=6500, fi=0.01, fo=0.2, p=pf + 0.2, label='the little brother squeals with delight')
    F.spot('owl_tawny', T['owl0'], rel=-19, start=max(0.0, nth('owl_tawny', 1) - 0.08), length=2.2, hp=250, lp=2500, fi=0.04, fo=0.5, p=po, send=-4, trim=False,
           label='the owl turns its head (a soft hoot)')

    # ---- not a star 8.8 to 12.7: the window opens on one bright star, a ring and two gold lines tie it to the sky
    F.spot('water_bubble_2', T['win0'], rel=-11, at_peak=True, lead=0.01, length=0.5, p=0.35, lp=5000, fo=0.3, send=-4, trim=False, label='the round window opens (a soft bubble)')
    F.spot('chimes_butterfly_1', T['win0'] + 0.15, rel=-12, notes=AUTO, lp=9500, fi=0.03, fo=1.4, send=-3, p=0.3, length=2.0, label='the window opens (chimes)')
    F.spot('triangle_2', T['lens_star'], rel=-10, notes=AUTO, lp=9500, fi=0.03, fo=1.8, length=3.0, send=-3, p=0.3, label='the star glints in the window (a triangle)')
    F.spot('metallophone', T['tele0'] + 0.3, rel=-17, notes=AUTO, lp=7000, fi=0.03, fo=0.6, length=1.2, p=pe, label='she aims the telescope (a tiny ring)')

    # ---- far away 12.7 to 18: the star is a giant calm ball of fire; the window closes; she picks up a pebble
    F.spot('chimes_dream_3', T['star_pulse'], rel=-12, notes=AUTO, lp=9000, fi=0.05, fo=2.2, length=3.2, send=-3, p=0.2, label='the star is a giant, calm ball of fire (a slow glow of chimes)')
    F.spot('water_bubble_2', T['win_close0'] + 0.4, rel=-12, rev=True, length=0.5, p=0.35, lp=5000, fo=0.2, send=-4, swell=True, label='the window closes (a soft bubble, reversed)')
    F.spot('steps_pebbles', T['pebble0'], rel=-14, at_peak=True, lead=0.02, start=max(0.0, nth('steps_pebbles', 1) - 0.06), length=0.5, hp=400, lp=5500, fi=0.01, fo=0.2, p=pe - 0.2, trim=False, label='she picks up a pebble')
    F.spot('chimes_butterfly_3', T['pebble1'], rel=-15, notes=AUTO, lp=9000, fi=0.04, fo=1.0, length=1.6, send=-3, p=pe - 0.2, label='she holds the pebble up to the sky (a small chime)')
    F.spot('steps_pebbles', T['pebble2'], rel=-15, at_peak=True, lead=0.02, start=max(0.0, nth('steps_pebbles', 4) - 0.06), length=0.4, hp=400, lp=5500, fi=0.01, fo=0.2, p=pe - 0.2, trim=False, label='she sets the pebble back')

    # ---- tiny rock 18 to 21.9: the window opens on a small brown rock tumbling in space, beside a matching pebble
    F.spot('water_bubble_2', T['win2'], rel=-11, at_peak=True, lead=0.01, length=0.5, p=0.35, lp=5000, fo=0.3, send=-4, trim=False, label='the round window opens again (a soft bubble)')
    F.spot('chimes_butterfly_1', T['win2'] + 0.2, rel=-13, notes=AUTO, lp=9500, fi=0.03, fo=1.4, send=-3, p=0.3, length=2.0, label='the window opens on the rock (chimes)')
    for k, (dt, p_) in enumerate(((0.05, 0.4), (0.62, 0.3), (1.15, 0.45), (1.7, 0.35))):
        F.spot('steps_pebbles', T['lens_rock'] + dt, rel=-18 - 0.7 * k, at_peak=True, lead=0.02, start=max(0.0, nth('steps_pebbles', 2 * k + 6) - 0.06), length=0.35, hp=600, lp=6000, fi=0.01, fo=0.15, p=p_,
               trim=False, label='the rock tumbles (a tiny tick)')
    F.spot('candle_sparkle_1', T['pebble_in'], rel=-16, start=9.0, length=1.2, hp=2000, lp=9500, fi=0.05, fo=0.6, p=0.3, trim=False, swell=True, label='the pebble and the rock glint together')
    F.spot('triangle_2', T['pebble_in'] + 0.05, rel=-12, notes=AUTO, lp=9500, fi=0.03, fo=1.6, length=2.6, send=-3, p=0.25, label='the twin glint (a triangle)')

    # ---- drifting 21.9 to 27.2: the rock drifts closer; three accents on the bar lines
    for k, (te, rl) in enumerate(((T['acc0'], -14), (T['acc1'], -12), (T['acc2'], -10))):
        F.spot('metallophone', te, rel=rl, notes=AUTO, lp=8000, fi=0.02, fo=0.8, length=1.6, send=-3, p=0.3 - 0.1 * k, label='the rock drifts closer (accent %d of 3 on the bar line)' % (k + 1))
    F.spot('wind_inside_1', T['acc0'] + 0.2, rel=-21, start=8, length=5.0, hp=120, lp=2200, fi=1.2, fo=1.4, p=0.3, trim=False, swell=True, label='a long breath of air as it nears')
    F.spot('water_bubble_2', T['air_in'], rel=-11, at_peak=True, lead=0.01, length=0.5, p=0.35, lp=5000, fo=0.3, send=-4, trim=False, label='the window shows the layers of the air (a soft bubble)')

    # ---- the air 27.2 to 40.2: the rock enters the air and begins to glow: orange, yellow, white
    F.spot('whoosh_long_2', T['enter'] - 0.4, rel=-16, length=5.5, hp=250, lp=5500, fi=1.2, fo=1.0, p=0.35, trim=False, swell=True, label='it enters the air (a long, rising rush)')
    F.bed('wind_whistle_1', T['enter'], T['burn'] + 1.0, rel=-23, start=15, hp=500, lp=6500, p=0.3,
          env=[(T['enter'], -30), (T['glow0'], -9), (T['glow1'], -2), (T['burn'] - 0.3, 2), (T['burn'] + 0.6, -30)], fi=0.5, fo=0.6, label='the air sings past as it glows hotter')
    F.spot('chimes_dream_3', T['ring0'], rel=-14, notes=AUTO, lp=9000, fi=0.04, fo=1.4, length=2.2, send=-3, p=0.2, label='the ring appears in the sky (a small chime)')
    F.spot('triangle_2', T['sky_ring'], rel=-12, notes=AUTO, lp=9500, fi=0.03, fo=1.8, length=3.0, send=-3, p=0.1, label='the ring in the sky (a triangle)')

    # ---- the streak 40.2 to 44.1: the rock rushes in on the full orchestra: the long streak across the sky
    s0 = T['streak0']
    F.spot('whoosh_8', pk, rel=-8, rev=True, length=1.5, hp=250, lp=9000, fi=0.04, fo=0.06, sweep=(0.55, -0.8), swell=True, label='the rock rushes in (a reversed whoosh crossing the sky)')
    F.spot('wind_whistle_2', pk - 0.1, rel=-15, rev=True, start=3, length=1.8, hp=700, lp=8000, fi=0.4, fo=0.1, sweep=(0.5, -0.7), swell=True, label='the air screams past, gently (a reversed whistle)')
    F.spot('cluster_chimes', pk + 0.03, rel=-8, start=loud_windows('cluster_chimes', 2.5, 1, hop=0.5, start=0.0, stop=120.0)[0], length=2.8, notes=AUTO, lp=10500, fi=0.08, fo=1.6, send=-2,
           trim=False, swell=True, label='METEOR! a burst of gold stars (chimes, tuned)')
    F.spot('glockenspiel', pk + 0.05, rel=-9, speed=2 ** (4 / 12), notes=AUTO, lp=9500, fi=0.02, fo=2.0, length=3.0, send=-3, p=-0.1, label='METEOR! sparkle (a struck glockenspiel chord, tuned)')
    F.spot('triangle_2', pk + 0.02, rel=-9, notes=AUTO, lp=9500, fi=0.03, fo=2.2, length=3.4, send=-3, p=0.15, label='METEOR! a soft triangle')
    F.spot('tibetan_bowl_2', pk, rel=-12, at_peak=True, lead=0.0, notes=F.auto_notes(pk - 0.3, dur=4.0, kmax=2), lp=5500, fi=0.05, fo=3.5, length=7.0, trim=False, send=-2, swell=True,
           label='METEOR! a singing bowl blooms with the climax')
    F.spot('sigh_nose', T['gasp'], rel=-19, start=0.3, length=1.6, speed=1.2, hp=300, lp=4500, fi=0.12, fo=0.6, p=pf - 0.2, trim=False, swell=True, label='everyone gasps: oh (a soft breath)')
    F.spot('toy_squeal_1', T['gasp'] + 0.35, rel=-17, speed=1.15, notes=AUTO, lp=6500, fi=0.01, fo=0.25, p=pf + 0.25, label='the little brother cheers')
    for k, ts in enumerate(np.sort(rng.uniform(pk + 0.2, T['streak1'] + 0.6, 7))):
        F.spot('candle_sparkle_2', float(ts), rel=-17 - (k % 3), start=3.0 + 4.0 * k, length=0.9, hp=2500, lp=9500, fi=0.04, fo=0.5, p=float(rng.uniform(-0.6, 0.3)), trim=False, swell=True,
               label='sparks shed from the streak')
    for k, ts in enumerate((pk + 0.9, pk + 1.5, pk + 2.2, pk + 2.9)):
        F.spot('chimes_dream_1', ts, rel=-13 - 1.3 * k, notes=AUTO, lp=9000, fi=0.03, fo=1.2, length=1.8, send=-3, p=-0.3 + 0.15 * k, label='sparkles drift down and melt (chimes)')
    F.spot('chimes_butterfly_3', T['streak1'], rel=-14, notes=AUTO, lp=9000, fi=0.05, fo=2.4, length=3.2, send=-3, p=-0.4, label='the trail fades away (a long soft chime)')

    # ---- gone 44.1 to 49.4: the window closes; specks of dust glint
    F.spot('water_bubble_2', T['win_close2'] + 0.4, rel=-12, rev=True, length=0.5, p=0.35, lp=5000, fo=0.2, send=-4, swell=True, label='the window closes (a soft bubble, reversed)')
    for k, ts in enumerate((T['dust0'] + 0.5, T['dust0'] + 1.8, T['dust0'] + 3.1, T['dust0'] + 4.3)):
        F.spot('candle_sparkle_1', ts, rel=-20, start=12.0 + 6.0 * k, length=0.8, hp=2800, lp=9500, fi=0.05, fo=0.5, p=-0.5 + 0.35 * k, trim=False, swell=True,
               label='a speck of space dust glints (tiny dust falls every day)')

    # ---- the wish 49.4 to 57.2: everyone closes their eyes; the snail's wish, a lettuce leaf, floats in and lands; it munches
    F.spot('chimes_dream_3', T['wish0'], rel=-14, notes=AUTO, lp=9000, fi=0.05, fo=2.2, length=3.2, send=-3, p=0.0, label='everyone makes a wish (a hushed chime)')
    F.spot('dreamcatcher', T['wish0'] + 0.9, rel=-22, start=0.2, length=3.0, hp=1500, lp=9000, fi=0.4, fo=1.2, p=0.15, trim=False, send=-3, swell=True, label='wish stars lift from their heads (a faint shimmer)')
    F.spot('paper', T['leaf0'] + 1.3, rel=-23, start=pieces('paper')[0][0] + 1.0, length=2.2, hp=1200, lp=7500, fi=0.5, fo=0.6, p=ps - 0.3, trim=False, swell=True, label='a lettuce leaf floats in, rocking (paper-light rustle)')
    F.spot('plant_cartoon_1', T['leaf1'], rel=-12, at_peak=True, lead=0.02, speed=1.1, length=0.7, hp=300, lp=5000, fi=0.01, fo=0.3, p=ps, trim=False, label='the leaf lands beside the snail')
    for k in range(6):
        F.spot(('carrot_crunch', 'rusk_crunch')[k % 2], T['munch0'] + 0.35 + 0.455 * k, rel=-11 - (k % 2) * 2, at_peak=True, lead=0.02,
               start=max(0.0, nth(('carrot_crunch', 'rusk_crunch')[k % 2], 3 * k + 1) - 0.06), length=0.4, speed=1.0, hp=350, lp=7000,
               fi=0.01, fo=0.15, p=ps, trim=False, label='the snail munches its wish (a lettuce crunch)')

    # ---- the send-off 57.2 to 68.4: a cuddle; the dance's last bright chord; a breath of stillness; the last streak
    F.spot('cloth', T['cuddle0'], rel=-21, start=pieces('cloth')[0][0] + 1.5, length=1.5, hp=400, lp=4500, fi=0.2, fo=0.4, p=pf - 0.1, trim=False, swell=True, label='they cuddle close (cloth)')
    F.spot('sigh_nose', T['cuddle0'] + 0.5, rel=-23, start=1.8, length=2.0, speed=0.9, hp=250, lp=3500, fi=0.3, fo=0.8, p=pf + 0.1, trim=False, swell=True, label='a happy sigh')
    ch = T['chord']
    F.spot('triangle_2', ch, rel=-9, notes=AUTO, lp=9500, fi=0.03, fo=2.4, length=3.6, send=-3, p=0.1, label='the dance\'s last bright chord (a triangle)')
    F.spot('chimes_butterfly_1', ch + 0.02, rel=-11, notes=AUTO, lp=10000, fi=0.03, fo=2.0, length=3.0, send=-3, p=-0.1, label='the last bright chord (chimes)')
    F.spot('owl_tawny', T['cuddle1'] + 1.6, rel=-20, start=max(0.0, nth('owl_tawny', 3) - 0.08), length=2.2, hp=250, lp=2500, fi=0.04, fo=0.6, p=po, send=-4, trim=False,
           label='the owl hoots softly goodnight')
    l0 = T['last0']
    F.spot('whoosh_4', l0 + 0.3, rel=-16, at_peak=True, lead=0.0, hp=900, lp=9000, fi=0.01, fo=0.25, sweep=(0.2, -0.7), trim=False, label='one last small streak')
    F.spot('chimes_dream_1', l0 + 0.05, rel=-13, notes=AUTO, lp=9000, fi=0.03, fo=1.6, length=2.4, send=-3, p=-0.2, label='the last streak sings (a soft chime)')

    # ---- words in with a soft pop (every word set in code)
    for w, tw in WORDS:
        F.spot('wine_stopper_3', tw, rel=-16, notes=None, lp=4500, hp=300, fi=0.01, fo=0.2, p=0.0, label='words pop in: ' + w.lower())
    return dict(peak=pk, chord=ch, last=l0)



# ==================================================================================================================
# 7. MASTER AND MEASURE
# ==================================================================================================================
BANK_RUN = 'rc-render sfx-bank.yml (the studio bank of BigSoundBank CC0 recordings)'
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
    a_ = np.abs(pre).max(1); b_ = np.abs(y).max(1); ok_ = a_ > 0.02; red = np.where(ok_, 20 * np.log10((a_ + 1e-9) / (b_ + 1e-9)), 0.0); red[int((DUR - 0.5) * SR):] = 0.0      # the closing fade is not the limiter
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
    'The streaks are real whooshes (reversed so they build to the bright instant) with real chimes, a triangle and a glockenspiel chord tuned to the music: the bank has no recording of a meteor, and there is none to make (it is silent in space and far away).',
    'The pebble, the rock tumbling and the marshmallow stick are a pebble-walking recording, a few of its ticks, and a soft wooden brush: stand-ins for small things.',
    'The sparks from the fire and the streak are tiny recorded sparkles from a candle, faint and short.',
    'The lettuce crunch is a raw carrot and a rusk crunch, a little higher and small: there is no recording of a snail, and a snail would not be heard.',
    'The owl is a real tawny owl\'s hoots (cut to short soft ones, low-passed, a little way off).',
    'The family\'s gasp and happy sigh are a soft breath through the nose; the little brother\'s squeal is a squeaky toy (no recorded children).',
    'The window opening is a soft water bubble, closing is the same reversed; the shimmer of the wish stars is a dreamcatcher\'s faint jingle.',
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
    md = f"""# Sound of the shooting star film (Little Big Questions)

A SILENT 68.4 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
`audio/mix.m4a` is committed (the render needs it); `audio/mix.wav` is ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** {m['credit']}

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- {meas['seconds']:.2f} s, 48 kHz stereo AAC 256k, {meas['lufs']:.1f} LUFS integrated (target {TARGET_LUFS:.0f}), true peak {meas['true_peak']:.2f} dBTP (limit {TP_LIMIT} dBTP), loudness range {meas['lra']:.1f} LU.
- The loudest limiter dip is {meas['limiter_max_reduction_db']:.1f} dB at {meas['limiter_max_reduction_at_s']:.1f} s; the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (`szevents.py`, zero offset by construction). On the rendered effects bus alone, {chk['landed']} of {chk['checked']} percussive spots
  stand out by 3 dB or more within 30 ms before to 150 ms after their event; the rest are quiet details sitting under the fire or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
{m['piece']}, {m['recording']}, {m['licence']}. Source: {m['source']}. Asset: {m['asset']}.
Cut on the bar lines (one bar = {BAR} s) into four pieces, joined by triangular (linear in, linear out) cross-fades:
recording 0:00 to 0:03.6 (the introduction, film 0 to 3.6), 0:05.18 to 0:30.05 (the theme, film 3.6 to 28.47, a 0.5 s fade at 3.6),
1:28.84 to 2:00.19 (the plucked build and its full-orchestra peak, film 27.16 to 58.51, a one-bar fade from 27.16), 3:46.06 to the end
(the dance's own ending, film 57.2 to 68.4, a one-bar fade from 57.2; its bright chord is at film 59.55). The big reveal lands on the loud
hit of the peak (film 41.9). A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio {edit_info['ratio']}, gain between {edit_info['gain_min']:+.1f}
and {edit_info['gain_max']:+.1f} dB) lifts the whispering parts and eases the peak so the film sits near -16 LUFS; the notes keep their own shape.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). Event times are read from `szevents.py` and `beats.json` at build time: a re-timed picture
re-times the sound. Tonal sounds (chimes, triangle, glockenspiel, bowl, boings, metallophone) are tuned by resampling to the pitch classes the
orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it. Beds (fire, crickets, evening birds,
air) are chosen by low crest factor (no stray knock) and set by RMS against the music; every spot is set by its peak in dB against the music's local RMS.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
""" + "\n".join(lines) + f"""

## Stand-ins (honest)
""" + "\n".join('- ' + s for s in STANDINS) + """

## Rebuild
`python3 films/cutaway/kids/shooting-star/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
"""
    open(os.path.join(FILM, 'SOUND.md'), 'w').write(md)


# ==================================================================================================================
# 9. MAIN
# ==================================================================================================================
KEY_EVENTS = [('first stars', 'snail_up1'), ('zip streak', 'streak1_0'), ('window: star', 'win0'), ('window: rock', 'win2'), ('enters the air', 'enter'),
              ('the streak starts', 'streak0'), ('METEOR!', 'peak'), ('gone', 'win_close2'), ('the wish', 'wish0'), ('the lettuce lands', 'leaf1'),
              ('the last chord', 'chord'), ('the stillness', 'hush0'), ('the last streak', 'last0')]


def main():
    T, B, bj, WORDS = read_events()
    need = ['fireplace_1', 'evening_birds', 'field_cricket', 'wind_plain', 'fire_branching_1', 'boing_6', 'candle_sparkle_1', 'candle_sparkle_2', 'brush_wood', 'whoosh_10',
            'chimes_dream_1', 'chimes_dream_3', 'chimes_butterfly_1', 'chimes_butterfly_3', 'cloth', 'toy_squeal_1', 'owl_tawny', 'water_bubble_2', 'triangle_2', 'metallophone',
            'steps_pebbles', 'wind_inside_1', 'whoosh_long_2', 'wind_whistle_1', 'wind_whistle_2', 'whoosh_8', 'cluster_chimes', 'glockenspiel', 'tibetan_bowl_2', 'sigh_nose',
            'dreamcatcher', 'paper', 'plant_cartoon_1', 'carrot_crunch', 'rusk_crunch', 'whoosh_4', 'wine_stopper_3']
    ensure_bank(need)
    csvp = os.path.join(K.CACHE, 'sfx-bank.csv')
    if not os.path.exists(csvp):
        urllib.request.urlretrieve('https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.csv', csvp)
    mus_raw = music_edit()
    mus, gcur = level_rider(mus_raw, target=-21.0, ratio=3.0, maxg=9.0)
    F = Film(); F.mus = mus
    info = design(F, T, B, WORDS)
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
    tl = timeline(y, musd, fx, [(nm, T[k]) for nm, k in KEY_EVENTS])
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(HERE, 'mix.m4a')],
                               capture_output=True, text=True).stdout.strip())
    res['seconds'] = round(dur, 3)
    csvrows = bank_csv()
    edit_info = dict(ratio=3.0, gain_min=float(gcur.min()), gain_max=float(gcur.max()))
    meas = dict(res, codec='aac 256k stereo 48 kHz', target_lufs=TARGET_LUFS, true_peak_limit_dbtp=TP_LIMIT)
    out = dict(
        film='kids-shooting-star', duration_s=meas['seconds'], measurements=meas,
        music=dict(bj['music'], cut=dict(pieces_recording_to_film=[list(p) for p in EDIT['pieces']], crossfade_windows_film_s=[list(f) for f in EDIT['fades']], bar_s=BAR,
                                         curve='triangular (linear)'), rider=dict(target_lufs=-21.0, ratio=3.0, smoothing_s=1.0, gain_db_range=[round(edit_info['gain_min'], 1), round(edit_info['gain_max'], 1)]),
                   music_only_lufs=round(dsp.loudness(musd), 2)),
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
        for t in range(0, 68):
            pk = max([r['peak_above_music_rms_db'] for r in F.rows if 'peak_above_music_rms_db' in r and t <= r['t'] < t + 1] or [None], key=lambda v: -99 if v is None else v)
            print(f'  {t:2d}-{t + 1:2d}  mix {rms_line(y, t, t + 1):6.1f}  music {rms_line(musd, t, t + 1):6.1f}  fx {rms_line(fx, t, t + 1):6.1f}   gap {rms_line(musd, t, t + 1) - rms_line(fx, t, t + 1):5.1f} dB   top spot {pk}')
    print('timeline (t, mix, music, effects; dBFS per 0.5 s):')
    for r in tl:
        print(f"  {r['event']:<20} @{r['t']:6.2f}:", ' | '.join(f"{a:5.1f}: {m_:5.1f} {mu:5.1f} {e:5.1f}" for a, m_, mu, e in r['windows']))
    return out


if __name__ == '__main__':
    main()
