#!/usr/bin/env python3
"""score.py: a free, deterministic procedural score engine for KINOFORGE films.

    python3 films/lib/score/score.py plan.json -o score.wav [--engine auto|synth|samples] [--seed N]

Makes a stereo 48 kHz WAV of any length from a short score plan. The feel is Age of Empires and Anno: ambient, warm,
living; long evolving chords, plucked and bowed strings, a solo instrument for the place and era, soft hand drums that
enter with tension, one swell into the turn of the battle, a settling after it, a resolve at the end.

Nothing is paid and nothing is downloaded at run time. Two sound sources, same score:
  * samples (engine auto/samples): CC0 recordings from VSCO-2 CE when a sample folder exists (see README.md);
  * synthesis (engine synth, and the fallback for any missing sample): wavetable strings, Karplus-Strong plucks,
    breathy winds and hand drums built from scratch.
Same plan + same seed + same engine = the same audio, sample for sample.

Score plan (JSON):
  {"palette": "ancient_med" | "medieval_europe" | "middle_east_central_asia" | "early_modern_europe",
   "key": "D", "mode": "dorian",          optional: key and mode default to the palette's
   "tempo": 62,                           optional: hand-drum pulse in BPM (free time otherwise: the palette's tempo)
   "duration": 157.6, "seed": 1,
   "sections": [{"t": 0, "mood": "calm"}, {"t": 17.4, "mood": "curious"}, ..., {"t": 98.8, "mood": "turn"}, ...],
        moods: calm, curious, tension, turn, triumph, aftermath; optional "intensity": 0..1 replaces a section's level
   "hits": [{"t": 98.8, "kind": "low" | "drum" | "swell" | "chime", "level": 0..1}],     optional
   "voice": [[start, end], ...],          optional narration spans: solo phrases then prefer the gaps between them
   "solo": "flute"|"clarinet"|"bassoon"|"solo_violin"  optional, forces the solo instrument
   "swell_len": 8, "settle": 10, "end_fade": 3.5}
"""
import os, sys, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp, voices, palettes as P
from dsp import SR, db

CR = 50  # control-curve rate in Hz


# ---------------------------------------------------------------- plan
def normalise_plan(plan):
    p = dict(plan)
    name = P.ALIASES.get(p.get('palette', ''), p.get('palette', ''))
    if name not in P.PALETTES: raise ValueError(f'unknown palette {p.get("palette")!r}; use one of {sorted(P.PALETTES)}')
    pal = P.PALETTES[name]; p['palette'] = name
    p.setdefault('key', pal['key']); p.setdefault('mode', pal['mode']); p['tempo'] = p.get('tempo') or pal['tempo']
    if p['key'] not in P.TONIC_PC: raise ValueError(f'unknown key {p["key"]!r}')
    if p['mode'] not in P.MODES: raise ValueError(f'unknown mode {p["mode"]!r}; use one of {sorted(P.MODES)}')
    p.setdefault('seed', 1); p.setdefault('swell_len', 8.0); p.setdefault('settle', 10.0); p.setdefault('end_fade', 3.5)
    p['duration'] = float(p['duration'])
    secs = sorted(({'t': float(s['t']), 'mood': s['mood'], **({'intensity': float(s['intensity'])} if 'intensity' in s else {})} for s in p['sections']), key=lambda s: s['t'])
    for s in secs:
        if s['mood'] not in P.MOODS: raise ValueError(f'unknown mood {s["mood"]!r}; use one of {sorted(P.MOODS)}')
    if not secs or secs[0]['t'] > 0: secs.insert(0, {'t': 0.0, 'mood': 'calm'})
    secs[0]['t'] = 0.0
    secs = [s for s in secs if s['t'] < p['duration'] - 6]
    for i, s in enumerate(secs): s['t1'] = secs[i + 1]['t'] if i + 1 < len(secs) else p['duration']
    p['sections'] = secs
    p['hits'] = sorted(p.get('hits', []), key=lambda h: h['t'])
    p['voice'] = [[float(a), float(b)] for a, b in p.get('voice', [])]
    return p


# ---------------------------------------------------------------- helpers
class Bus:
    def __init__(self, n):
        self.n = n; self.buf = np.zeros((n, 2), np.float32)

    def add(self, x, t, gain=1.0, pan=0.0):
        i = int(round(t * SR))
        if i < 0: x = x[-i:]; i = 0
        if i >= self.n or len(x) == 0: return
        m = min(len(x), self.n - i); L, R = dsp.pan_gains(pan)
        self.buf[i:i + m, 0] += x[:m, 0] * gain * L * 1.414
        self.buf[i:i + m, 1] += x[:m, 1] * gain * R * 1.414


def rms_ref(x, target_db):
    """scale a sustained note so its body sits at target_db RMS (so notes of different instruments balance)"""
    a = np.abs(x).max(axis=1); act = a > 0.15 * a.max()
    r = np.sqrt((x[act] ** 2).mean()) if act.any() else 1.0
    return x * (db(target_db) / (r + 1e-9))


def peak_ref(x, target_db):
    return x * (db(target_db) / (np.abs(x).max() + 1e-9))


def cur(curve, t):
    return float(np.interp(t * CR, np.arange(len(curve)), curve))


# ---------------------------------------------------------------- the composer
class Composer:
    def __init__(self, plan, engine='auto', log=lambda *a: None):
        self.plan = normalise_plan(plan); p = self.plan; self.log = log
        self.pal = P.PALETTES[p['palette']]; self.D = p['duration']; self.n = int(self.D * SR) + SR
        self.tonic = P.TONIC_PC[p['key']]; self.scale = P.MODES[p['mode']]; self.menu = P.MENUS[p['mode']]
        self.scale_pcs = {(self.tonic + s) % 12 for s in self.scale}
        self.rngs = {k: np.random.default_rng([int(p['seed']), i]) for i, k in
                     enumerate(['chords', 'pad', 'solo', 'pluck', 'drums', 'hits', 'motif', 'swell'])}
        self.engine = engine
        self.inst = {}
        if engine != 'synth':
            for name, (fol, _, _) in P.INSTRUMENTS.items():
                s = voices.Sampled(fol, name)
                if s.ok: self.inst[name] = s
            if engine == 'samples' and not self.inst: raise RuntimeError('engine=samples but no sample folder found (set SCORE_SAMPLES)')
        self.use_samples = bool(self.inst)
        self.log(f'engine: {"samples+synth" if self.use_samples else "synth"} ({len(self.inst)} sampled instruments found)')
        self.info = {'chords': [], 'hits': [], 'solo': [], 'beats': []}
        self.turn_t = next((s['t'] for s in p['sections'] if s['mood'] == 'turn'), None)

    # ---- curves
    def build_curves(self):
        p = self.plan; D = self.D; n = int(D * CR) + 2
        self.curves = {}
        for key in ('I', 'perc', 'bright'):
            pts = []; last = [-1.0]

            def add(t, v):
                t = max(t, last[0] + 0.02); pts.append((t, v)); last[0] = t
            prev = None; hold_until = 0.0
            for i, s in enumerate(p['sections']):
                M = P.MOODS[s['mood']]; v0, v1 = M[key]
                if key == 'I' and 'intensity' in s: v0 = v1 = s['intensity']
                if i == 0:
                    end_t = s['t1'] - 2
                    if len(p['sections']) > 1 and p['sections'][1]['mood'] == 'turn': end_t = min(end_t, s['t1'] - p['swell_len'] - 0.3)
                    add(0.0, v0); add(max(end_t, 0.1), v1); prev = v1; continue
                if s['mood'] == 'turn':
                    sl = p['swell_len']; ts = max(last[0] + 0.1, s['t'] - sl)
                    add(ts, prev); add(ts + sl * 0.5, prev + (v0 - prev) * 0.22); add(ts + sl * 0.82, prev + (v0 - prev) * 0.62)
                    add(s['t'] + 0.6, v0); hold = min(s['t1'] - 0.5, s['t'] + 3.0); add(hold, v0); hold_until = hold
                    if s['t1'] - hold > 6: add(min(hold + 8.0, s['t1'] - 1.0), v1)           # the peak is brief: it settles within ~8 s
                else:
                    r = p['settle'] if p['sections'][i - 1]['mood'] == 'turn' else 4.0
                    a = max(s['t'] - r / 2 if p['sections'][i - 1]['mood'] != 'turn' else s['t'], hold_until)
                    add(a, prev); add(a + r, v0)
                end_t = s['t1'] - 1.5
                if i + 1 < len(p['sections']) and p['sections'][i + 1]['mood'] == 'turn':      # the swell has to start before the turn
                    end_t = min(end_t, s['t1'] - p['swell_len'] - 0.3)
                add(max(end_t, last[0] + 0.05), v1); prev = v1
            add(D, pts[-1][1]); add(D + 1, pts[-1][1])
            tt = np.array([a for a, _ in pts]); vv = np.array([b for _, b in pts])
            c = np.interp(np.arange(n) / CR, tt, vv)
            from scipy.ndimage import gaussian_filter1d
            self.curves[key] = gaussian_filter1d(c, 0.7 * CR).astype(np.float32)

    # ---- harmony
    def section_at(self, t):
        for s in self.plan['sections']:
            if s['t'] <= t < s['t1']: return s
        return self.plan['sections'][-1]

    def chord_pcs(self, root, ctype):
        T = self.tonic; S = {(T + s) % 12 for s in self.scale}
        r = (T + root) % 12; o = lambda i: (r + i) % 12
        fifth = 7 if o(7) in S else (6 if o(6) in S else 7)
        third = 4 if (o(4) in S and o(3) not in S) else (3 if o(3) in S else (4 if o(4) in S else None))
        fourth = 5 if o(5) in S else None
        ninth = 2 if o(2) in S else (1 if o(1) in S else None)
        if ctype == 'open': tones = [0, fifth, ninth] if ninth is not None else [0, fifth]
        elif ctype == 'sus': tones = [0, fourth if fourth is not None else (ninth or fifth), fifth]
        elif ctype == 'major': tones = [0, 4, 7]                                          # the lift: a major third on the tonic
        elif ctype == 'add9': tones = [0, third or fifth, fifth] + ([ninth] if ninth is not None else [])
        else: tones = [0, third if third is not None else fifth, fifth]
        return r, [(r + i) % 12 for i in tones]

    def voice_chord(self, root_pc, pcs, prev):
        """bass note in 36..47; two or three upper voices in 52..76 chosen to move as little as possible"""
        import itertools
        bass = 36 + ((root_pc - 36) % 12)
        ups = [pc for pc in pcs]
        cands = [[m for m in range(50, 77) if m % 12 == pc] for pc in ups]
        best, bs = None, 1e9
        pv = prev[1:] if prev else None
        for combo in itertools.product(*cands):
            c = sorted(combo)
            if any(b - a < 3 for a, b in zip(c, c[1:])) or c[-1] - c[0] > 19: continue
            score = 0.0
            if pv:
                for a, b in zip(sorted(pv), c): score += abs(a - b)
                score += 0.8 * abs(len(pv) - len(c))
            else: score = abs(np.mean(c) - 60) * 0.6
            score += max(0, c[0] - 64) * 0.5 + 0.1 * abs(c[-1] - c[0] - 12)
            if score < bs: bs, best = score, c
        if best is None: best = sorted([next(m for m in range(53, 65) if m % 12 == pc) for pc in ups])[:3]
        return [bass] + best

    def plan_chords(self):
        p = self.plan; rng = self.rngs['chords']; D = self.D; M = P.MOODS; menu = self.menu; chords = []
        prev_root = None

        def pick(roles, avoid):
            pool = [r for role in roles for r in menu[role]]
            for _ in range(8):
                r = int(rng.choice(pool))
                if r != avoid: return r
            return pool[0]

        def push(t, mood, root=None, ctype=None, role=None):
            nonlocal prev_root
            if root is None: root = pick(role, prev_root)
            if ctype is None:
                ctype = {'calm': 'open', 'curious': 'sus' if rng.random() < .5 else 'add9', 'tension': 'sus' if rng.random() < .6 else 'open',
                         'turn': 'triad', 'triumph': 'add9', 'aftermath': 'open'}[mood]
            rpc, pcs = self.chord_pcs(root, ctype)
            prev = chords[-1]['voicing'] if chords else None
            chords.append(dict(t=float(t), mood=mood, root=int(root), type=ctype, pcs=pcs, root_pc=int(rpc), voicing=self.voice_chord(rpc, pcs, prev)))
            prev_root = root

        for i, s in enumerate(p['sections']):
            m = s['mood']; lo, hi = M[m]['chord']; t = s['t']
            role = {'calm': ['stable'], 'curious': ['curious', 'stable'], 'tension': ['tense'], 'turn': ['peak'], 'triumph': ['lift', 'stable'], 'aftermath': ['stable']}[m]
            if m == 'turn':
                ts = max(t - p['swell_len'], (chords[-1]['t'] + 3.0) if chords else 0)
                push(ts, 'tension', role=['pre'], ctype='sus')
                push(max(t - 1.6, ts + 2.0), 'turn', role=['peak'], ctype='triad'); t0 = max(t - 1.6, ts + 2.0)
            elif m == 'triumph':
                push(t, m, root=0, ctype='major' if self.mode_lifts() else 'add9'); t0 = t
            elif i == 0:
                push(t, m, root=0, ctype='open'); t0 = t
            else:
                if chords and chords[-1]['t'] > t - 2.0:                               # a chord has just begun: let it breathe
                    t = chords[-1]['t'] + 2.0
                push(t, m, role=role); t0 = t
            t = t0 + float(rng.uniform(lo, hi))
            while t < s['t1'] - 5.0:
                push(t, m, role=role); t += float(rng.uniform(lo, hi))
        # the resolve: the tonic, held to the end
        end_t = D - 11.0
        while chords and chords[-1]['t'] > end_t - 3.0: chords.pop()
        push(end_t, 'aftermath', root=0, ctype='major' if (self.mode_lifts() and p['sections'][-1]['mood'] in ('triumph',)) else 'open')
        self.chords = chords
        self.info['chords'] = [(round(c['t'], 2), c['mood'], c['root'], c['type']) for c in chords]

    def mode_lifts(self):
        return self.plan['mode'] in ('dorian', 'aeolian', 'phrygian', 'hijaz')

    def chord_at(self, t):
        c = self.chords[0]
        for x in self.chords:
            if x['t'] <= t: c = x
            else: break
        return c

    # ---- helpers for notes
    def gap_shift(self, t, window=2.6):
        for a, b in self.plan['voice']:
            if a <= t < b and b - t <= window: return b + 0.12
        return t

    # ---- pads: bowed strings (long, evolving)
    def render_pad(self):
        p = self.plan; rng = self.rngs['pad']; pal = self.pal; D = self.D
        strings = Bus(self.n); synth_pad = Bus(self.n)
        use_s = self.use_samples
        for k, c in enumerate(self.chords):
            t0 = c['t']; t1 = self.chords[k + 1]['t'] if k + 1 < len(self.chords) else D + 4
            span = t1 - t0 + 1.8; I = cur(self.curves['I'], t0 + 1)
            att = float(np.clip(span * 0.22, 2.2, 4.2)); rel = 3.8
            v = c['voicing']; bass, ups = v[0], v[1:]
            # bass voice: cello (or synthesised) on the chord root; a fifth above in the palette's drone style
            jit = lambda: float(rng.normal(0, 0.18))
            self.add_pad_note(strings, synth_pad, pal['bass'], bass, t0 - 0.7 + jit(), span, att, rel, 0.62, -3.0, 'bass', rng, use_s)
            if pal['fifth_drone'] and c['type'] != 'major':
                fifth = bass + 7 if bass + 7 < 56 else bass - 5
                self.add_pad_note(strings, synth_pad, 'cello', fifth + 12 if fifth < 45 else fifth, t0 - 0.4 + jit(), span, att, rel, 0.4, -9.0, 'bass', rng, use_s)
            for j, m in enumerate(ups):
                name = pal['mids'][j % len(pal['mids'])] if m < 66 else pal['highs'][0]
                if m >= 66 and I < 0.32 and k % 2 == 0: continue                      # keep the calm sections dark: fewer high voices
                self.add_pad_note(strings, synth_pad, name, m, t0 - 0.5 + jit() + 0.12 * j, span, att, rel, 0.50 + 0.2 * I, -3.5 - 0.5 * j, 'mid', rng, use_s)
        # the swell into the turn: extra upper strings enter one by one, bowed crescendo, peak at the turn
        if self.turn_t is not None:
            t_sw = self.turn_t; sl = p['swell_len']; peak = None
            for c in self.chords:
                if c['mood'] == 'turn' and c['t'] <= t_sw + 0.5: peak = c
            if peak:
                notes = [peak['voicing'][0] + 12] + [m + 12 if m < 62 else m for m in peak['voicing'][1:]]
                for j, m in enumerate(notes):
                    ts = t_sw - sl + 0.8 * j
                    dur = (t_sw + 4.5) - ts
                    name = 'violin' if m >= 62 else 'viola'
                    self.add_pad_note(strings, synth_pad, name, m, ts, dur, max(2.0, sl * 0.85 - 0.8 * j), 4.0, 0.62, -5.0 - 0.8 * j, 'mid', self.rngs['swell'], use_s)
        self.strings, self.synth_pad = strings, synth_pad

    def add_pad_note(self, strings, synth_pad, name, midi, t, dur, att, rel, vel, gain_db, role, rng, use_s):
        """one sustained string note: the sampled instrument when we have it, plus a synthesised cushion underneath
        (quiet when the samples are there, the whole sound when they are not) so the pad never thins or pulses"""
        inst = self.inst.get(name) if use_s else None
        sampled = inst is not None and inst.has(midi)
        if sampled:
            x = inst.note(midi, dur, rng, vel=vel, attack=att, release=rel, xfade=2.0)
            strings.add(x, t, db(gain_db), pan=float(rng.uniform(-0.35, 0.35)))
        under = db(gain_db - (8.5 if sampled else 0.0))
        if role == 'bass': y = voices.synth_bass_note(midi, dur, rng, attack=att, release=rel, vel=vel)
        else: y = voices.synth_pad_note(midi, dur, rng, attack=att, release=rel, vel=vel, voices=4 if use_s else 5)
        y = rms_ref(y, -24.0) * (0.25 + 0.75 * vel) * (1.0 if role == 'mid' else 0.9)
        synth_pad.add(y, t, under, pan=0.0)

    # ---- the solo voice
    def scale_notes(self, lo, hi):
        return [m for m in range(lo, hi + 1) if m % 12 in self.scale_pcs]

    def solo_choose(self, rng, mood):
        sol = self.plan.get('solo')
        if sol: return sol
        names = [n for n, _ in self.pal['solo']]; w = np.array([w for _, w in self.pal['solo']], float)
        if mood == 'tension' and 'bassoon' in names: return 'bassoon'
        return str(rng.choice(names, p=w / w.sum()))

    def make_motif(self):
        rng = self.rngs['motif']
        templ = [[0, 1, 2, 1, 0], [0, 2, 1, 3, 2, 0], [2, 1, 0, -1, 0], [0, 1, 0, -1, 0, 2, 1], [4, 3, 2, 1, 2, 0], [0, 2, 4, 3, 1, 0]]
        steps = list(templ[int(rng.integers(len(templ)))])
        rhy = [1.1, 0.8, 1.6, 1.0, 1.2, 2.6, 1.0]
        self.motif = (steps, rhy)

    def scale_idx_walk(self, centre):
        lo, hi = centre - 14, centre + 16
        notes = self.scale_notes(lo, hi)
        ton = [i for i, m in enumerate(notes) if m % 12 == self.tonic]
        base = min(ton, key=lambda i: abs(notes[i] - centre))
        return notes, base

    def render_solo(self):
        p = self.plan; rng = self.rngs['solo']; D = self.D; pal = self.pal
        bus = Bus(self.n); events = []                                             # (t, midi, dur, vel, inst, glide)
        t = 3.0 + float(rng.uniform(0, 2)); first = True; last_idx = None
        end_solo = D - 25.0
        pending_apex = self.turn_t
        while t < end_solo:
            s = self.section_at(t); mood = s['mood']; M = P.MOODS[mood]
            inst_name = self.solo_choose(rng, mood)
            lo_i, hi_i = P.INSTRUMENTS[inst_name][2]
            centre = int(np.clip(pal['centre'] + M['reg'] + (4 if inst_name == 'bassoon' else 0) - (12 if inst_name == 'bassoon' else 0), lo_i + 4, hi_i - 5))
            notes, base = self.scale_idx_walk(centre)
            ch = self.chord_at(t); ctones = [i for i, m in enumerate(notes) if m % 12 in ch['pcs']]
            steps, rhy = self.motif
            use_motif = first or (mood in ('curious', 'calm', 'triumph', 'aftermath') and rng.random() < 0.42) or (mood == 'turn' and rng.random() < .6)
            # build the phrase
            if pending_apex is not None and t >= pending_apex - 3.5:
                cA = int(np.clip(pal['centre'] + P.MOODS['turn']['reg'] - (12 if inst_name == 'bassoon' else 0), lo_i + 4, hi_i - 5))
                nA, _ = self.scale_idx_walk(cA); chA = self.chord_at(pending_apex)
                top = [i for i, m in enumerate(nA) if m % 12 in chA['pcs'] and m >= cA + 2]
                m_apex = nA[top[0]] if top else nA[-1]
                seq = [(0.0, m_apex, p['swell_len'] * 0.55 + 4.0, 0.62)]
                pending_apex = None
                plen = seq[0][2]
            elif use_motif:
                shift = 0 if first else int(rng.choice([0, 0, 1, -1, 2]))
                if mood == 'aftermath': steps_ = steps[: max(3, len(steps) - 2)]
                else: steps_ = steps
                seq = []; tt = 0.0; durscale = float(np.mean(M['dur'])) / 1.6
                for j, st in enumerate(steps_):
                    i = int(np.clip(base + st + shift, 0, len(notes) - 1)); d = rhy[j % len(rhy)] * durscale
                    if j == len(steps_) - 1: d *= 1.8
                    seq.append((tt, notes[i], d, 0.0)); tt += d
                plen = tt
            else:
                n_notes = int(rng.integers(M['notes'][0], M['notes'][1] + 1))
                idx = int(last_idx if last_idx is not None and abs(last_idx - base) < 6 else base)
                cand = [i for i in ctones if abs(i - idx) <= 3] or ctones
                idx = int(min(cand, key=lambda i: abs(i - idx)))
                seq = []; tt = 0.0; direction = 1 if rng.random() < .55 else -1
                for j in range(n_notes):
                    last = j == n_notes - 1
                    d = float(rng.choice(M['dur'])) * (1.6 if last else 1.0)
                    seq.append((tt, notes[int(np.clip(idx, 0, len(notes) - 1))], d, 0.0)); tt += d * (0.92 if not last else 1)
                    if j == n_notes - 2:                                          # land on a chord tone
                        idx = int(min(ctones, key=lambda i: abs(i - idx)))
                    else:
                        step = int(rng.choice([1, 1, 1, 2, 2, 3])) * direction
                        if rng.random() < .25: direction = -direction
                        idx = int(np.clip(idx + step, base - 6, base + 7))
                plen = tt
                last_idx = idx
            # place it, preferring a gap between narration lines in the quiet moods
            ts = self.gap_shift(t) if mood in ('calm', 'curious', 'aftermath', 'triumph') else t
            ts += float(rng.normal(0, 0.03))
            I = cur(self.curves['I'], ts)
            for k, (o, m, d, v) in enumerate(seq):
                vel = float(np.clip(0.28 + 0.38 * I + rng.normal(0, 0.04) + (0.06 if k == len(seq) // 2 else 0), 0.2, 0.9)) if v == 0.0 else v
                glide = pal['glide'] if (k == 0 and rng.random() < 0.45) else 0.0
                events.append((ts + o + float(rng.normal(0, 0.025)), int(m), float(d), vel, inst_name, glide))
            first = False
            t = ts + plen + float(rng.uniform(*M['rest'])) * (1 + (0.8 if mood == 'turn' else 0) * (1 - cur(self.curves['I'], ts)))
            if pending_apex is not None and t > pending_apex - 3.0 and ts + plen < pending_apex - 1.0:
                t = max(ts + plen + 0.8, pending_apex - 3.0)                                 # be ready for the swell: the high held note enters at the turn
        # the last phrase: falls home to the tonic and rests there
        notes, base = self.scale_idx_walk(int(np.clip(pal['centre'] - 2, 56, 80)))
        fin = [base + 3, base + 2, base + 1, base]
        tt = D - 25.0 + 2.0; inst_name = self.solo_choose(rng, 'aftermath')
        lo_i, hi_i = P.INSTRUMENTS[inst_name][2]
        for k, i in enumerate(fin):
            m = notes[i]; m = int(np.clip(m, lo_i + 2, hi_i - 2)); d = [2.2, 2.2, 3.0, D - 4.2 - (tt + 7.4)][k]
            events.append((tt, m, d, 0.42, inst_name, 0.0)); tt += [2.2, 2.2, 3.0, 0][k]
        events.sort()
        for (t, m, d, vel, name, glide) in events:
            if t >= D - 0.5: continue
            x = self.solo_note(name, m, d, vel, rng, glide)
            bus.add(x, t, 1.0, pan=pal['solo_pan'] + float(rng.normal(0, 0.03)))
        self.solo = bus
        self.info['solo'] = [(round(e[0], 2), e[1], round(e[2], 2), e[4]) for e in events]

    def solo_note(self, name, m, d, vel, rng, glide):
        inst = self.inst.get(name) if self.use_samples else None
        kind = P.INSTRUMENTS[name][1]
        if inst is not None and inst.has(m):
            x = inst.note(m, d, rng, vel=vel, attack=0.10 + 0.05 * (1 - vel), release=0.45, xfade=1.0)
            if glide:                                                                  # a short scoop into the note, like a ney or a fiddle
                x = self.scoop(x, glide)
        else:
            x = voices.synth_wind_note(m, d, rng, kind=kind, vel=vel, attack=0.12, release=0.5, glide=glide, vibrato=0.4)
            x = rms_ref(x, -24.0) * (0.25 + 0.75 * vel)
        return x

    @staticmethod
    def scoop(x, glide):
        """pitch rises a fraction of a semitone-step into the note over 0.15 s (simple resample of the head)"""
        n0 = int(0.16 * SR)
        if len(x) < 2 * n0: return x
        from scipy.signal import resample_poly
        head = x[:n0]; ratio = 1 + 0.06 * glide                                       # up to ~0.45 semitone below the target
        rate = np.linspace(1 - 0.05 * glide * 2, 1, n0)
        pos = np.cumsum(rate); pos = pos / pos[-1] * (n0 - 1)
        out = np.stack([np.interp(pos, np.arange(n0), head[:, c]) for c in (0, 1)], 1).astype(np.float32)
        return np.concatenate([out, x[n0:]])

    # ---- plucked strings
    def pluck_note(self, midi, ring, vel, rng, which):
        if which.startswith('synth:'):
            kind = which.split(':')[1]; y = voices.synth_pluck(midi, ring, rng, kind, vel)
            return peak_ref(y, -9.0) * (0.25 + 0.75 * vel)
        inst = self.inst.get(which) if self.use_samples else None
        if inst is not None and inst.has(midi):
            x = inst.note(midi, ring, rng, vel=vel, attack=0.002, release=min(1.2, ring * 0.5), pluck=True)
            return peak_ref(x, -9.0) * (0.25 + 0.75 * vel)
        y = voices.synth_pluck(midi, ring, rng, 'lyre' if which in ('harp',) else 'lute', vel)
        return peak_ref(y, -9.0) * (0.25 + 0.75 * vel)

    def render_pluck(self):
        p = self.plan; rng = self.rngs['pluck']; D = self.D; pal = self.pal
        bus = Bus(self.n); ev = []
        names = pal['pluck']; wts = np.array(pal['pluck_weights'], float)
        beat = 60.0 / p['tempo']
        t = 2.0 + float(rng.uniform(0, 1.5)); idx_state = 0; dirn = 1; rolled = False
        on = np.where(self.curves['perc'] > 0.05)[0]; grid0 = max(0.0, on[0] / CR - 1.0) if len(on) else 0.0
        end = D - 12.0
        def tones(ch, lo, hi):
            return sorted(m for m in range(lo, hi + 1) if m % 12 in ch['pcs'])
        while t < end:
            s = self.section_at(t); mood = s['mood']; M = P.MOODS[mood]; ch = self.chord_at(t); I = cur(self.curves['I'], t)
            which = str(rng.choice(names, p=wts / wts.sum()))
            if mood in ('calm', 'aftermath'):
                tn = tones(ch, 52, 79); idx_state = int(np.clip(idx_state + dirn * int(rng.integers(1, 3)), 0, len(tn) - 1))
                if idx_state in (0, len(tn) - 1): dirn = -dirn
                ts = self.gap_shift(t) + float(rng.normal(0, 0.02))
                ev.append((ts, tn[idx_state], 4.5, 0.38 + 0.12 * rng.random(), which))
                if mood == 'calm' and rng.random() < 0.3:
                    ev.append((ts + float(rng.uniform(0.38, 0.6)), tn[min(len(tn) - 1, idx_state + 1)], 4.0, 0.3, which))
                t += float(rng.uniform(*M['pluck']))
            elif mood == 'curious':
                tn = tones(ch, 50, 81); k = int(rng.integers(3, 5)); sp = float(rng.uniform(0.34, 0.55)); i0 = int(rng.integers(0, max(1, len(tn) - 4)))
                ts = self.gap_shift(t)
                for j in range(k):
                    ev.append((ts + j * sp + float(rng.normal(0, 0.015)), tn[min(len(tn) - 1, i0 + (j if dirn > 0 else k - 1 - j) % len(tn))], 3.5, 0.34 + 0.12 * rng.random() + 0.04 * (j == 0), which))
                dirn = -dirn; t = ts + k * sp + float(rng.uniform(*M['pluck']))
            elif mood == 'tension':
                tn_low = tones(ch, 43, 57); tn_mid = tones(ch, 55, 72)
                bar = 4 * beat; ev_t = grid0 + np.ceil((t - grid0) / bar - 1e-6) * bar; vel_b = 0.26 + 0.16 * I   # on the drums' bar line
                for q in range(4):                                                      # one bar: the ostinato rides the drum pulse
                    tq = ev_t + q * beat
                    root = tn_low[0] if q % 2 == 0 else tn_low[min(len(tn_low) - 1, 2)]
                    ev.append((tq + float(rng.normal(0, 0.012)), root, 1.8, vel_b * (1.0 if q == 0 else .8), which))
                    if q == 3 or (q == 1 and rng.random() < .4): ev.append((tq + beat * 0.5 + float(rng.normal(0, 0.012)), tn_mid[int(rng.integers(len(tn_mid)))], 1.5, 0.28 + 0.1 * I, which))
                t = ev_t + 4 * beat
            elif mood == 'turn':
                tn = tones(ch, 48, 84)
                if not rolled:
                    rolled = True; k = 9; sp = 0.085
                    for j in range(k): ev.append((max(s['t'] - 0.1, 0) + j * sp, tn[min(len(tn) - 1, 2 + j)], 4.5, 0.42 + 0.05 * j / k, which))
                    t = max(t, s['t'] + 0.9)
                for j in range(3): ev.append((t + j * beat * .5 + float(rng.normal(0, 0.012)), tn[min(len(tn) - 1, 3 + int(rng.integers(0, 6)))], 3.5, 0.34 + 0.12 * rng.random(), which))
                t += (float(rng.uniform(1.0, 1.6)) + beat) * (1 + 1.5 * (1 - I))                 # thins out as the peak passes
            else:  # triumph: flowing arpeggios
                tn = tones(ch, 52, 84); k = int(rng.integers(4, 7)); sp = float(rng.uniform(0.28, 0.42)); i0 = int(rng.integers(0, max(1, len(tn) - 6)))
                for j in range(k):
                    ev.append((t + j * sp + float(rng.normal(0, 0.012)), tn[min(len(tn) - 1, i0 + j)], 3.5, 0.32 + 0.10 * rng.random(), which))
                t += k * sp + float(rng.uniform(1.2, 2.6))
        # final resolve: tonic and fifth, plucked softly, left to ring
        which = names[0]
        ev.append((D - 11.0 + 0.3, 48 + (self.tonic % 12) + (12 if self.tonic < 3 else 0), 7.0, 0.36, which))
        ev.append((D - 11.0 + 1.6, 60 + ((self.tonic + 7) % 12) - (12 if (self.tonic + 7) % 12 > 6 else 0) + 0, 6.0, 0.30, which))
        pan0 = pal['pluck_pan']
        for (t, m, ring, vel, which) in sorted(ev):
            if t < 0 or t > D - 0.5: continue
            x = self.pluck_note(int(m), ring, float(vel) * (0.6 + 0.4 * cur(self.curves['I'], t)), rng, which)
            vel_h = 1 + float(rng.normal(0, 0.05))
            bus.add(x, t, vel_h, pan=pan0 + 0.35 * np.sin(t * 0.21))
        self.pluck = bus

    # ---- hand drums and hits
    def render_drums(self):
        p = self.plan; rng = self.rngs['drums']; D = self.D; pal = self.pal
        bus = Bus(self.n); pat = P.PATTERNS[p.get('drums') or pal['drums']]; beat = 60.0 / p['tempo']; step = beat / 2
        perc = self.curves['perc']; on = np.where(perc > 0.05)[0]
        pitch = float(dsp.midi_hz(self.tonic + 36) / 78.0)
        while pitch > 1.35: pitch /= 2
        while pitch < 0.7: pitch *= 2
        self.beats = []
        if len(on):
            t0 = max(0.0, on[0] / CR - 1.0); k = 0
            self.beats = []
            t = t0; stop = D - 6.0
            while t < stop:
                pv = cur(perc, t); slot = pat[k % 8]
                if k % 2 == 0: self.beats.append(round(t, 3))
                if slot is not None and pv > 0.05:
                    kind, imp = slot
                    if pv >= (1 - imp) * 0.8 and not (imp < 0.5 and rng.random() < 0.25):
                        vel = float(np.clip((0.30 + 0.55 * pv) * (1 if imp > 0.7 else 0.7) * (1 + rng.normal(0, 0.12)), 0.1, 0.95))
                        x = voices.drum(kind, rng, vel, pitch * float(rng.uniform(0.97, 1.03)))
                        x = peak_ref(x, -10.0) * (0.2 + 0.8 * vel)
                        drift = 0.012 * np.sin(k * 0.37)
                        bus.add(x, t + float(rng.normal(0, 0.007)) + drift, 1.0, pan=0.18 + float(rng.normal(0, 0.04)) if kind in ('tek', 'brush') else -0.05)
                t += step; k += 1
        self.drums = bus

    def render_hits(self):
        p = self.plan; rng = self.rngs['hits']; D = self.D
        self.hitbus = Bus(self.n); self.hit_air = Bus(self.n)
        hits = list(p['hits'])
        f_boom = float(dsp.midi_hz(self.tonic + 24))                               # the tonic, in the 62 to 124 Hz octave
        while f_boom < 62: f_boom *= 2
        while f_boom >= 124: f_boom /= 2
        pitch = f_boom / 44.0
        for h in hits:
            t = float(h['t']); lv = float(h.get('level', 0.8)); kind = h.get('kind', 'low')
            if t >= D - 3: continue
            if kind == 'low':
                x = peak_ref(voices.drum('boom', rng, 0.8, pitch), -8.0) * (0.2 + 0.8 * lv)
                self.hitbus.add(x, t, 1.0, pan=0.0)
                air = voices.air_swell(min(4.0, 2.0 + 2 * lv), rng, tail=1.2); self.hit_air.add(peak_ref(air, -26.0) * lv, t - min(4.0, 2.0 + 2 * lv), 1.0)
            elif kind == 'drum':
                x = peak_ref(voices.drum('tom', rng, 0.7, pitch * 1.6), -9.0) * (0.2 + 0.8 * lv); self.hitbus.add(x, t, 1.0)
            elif kind == 'swell':
                air = voices.air_swell(4.5, rng, tail=1.0); self.hit_air.add(peak_ref(air, -24.0) * lv, t - 4.5, 1.0)
            elif kind == 'chime':
                m = 72 + self.tonic % 12 - (12 if self.tonic > 5 else 0)
                for j, mm in enumerate([m, m + 7 if (m + 7) % 12 in self.scale_pcs else m + 5]):
                    self.hitbus.add(self.pluck_note(mm, 5.0, 0.4 * lv + 0.1, rng, self.pal['pluck'][0]), t + 0.12 * j, 0.8, pan=0.2)
            self.info['hits'].append((round(t, 2), kind, lv))

    # ---- mix
    def render(self):
        t00 = time.time(); self.build_curves(); self.plan_chords(); self.make_motif()
        self.render_pad(); self.log(f'pads {time.time() - t00:.1f}s')
        self.render_solo(); self.log(f'solo {time.time() - t00:.1f}s')
        self.render_pluck(); self.render_drums(); self.render_hits(); self.log(f'plucks/drums {time.time() - t00:.1f}s')
        n = self.n; I = self.curves['I']; B = self.curves['bright']
        tt = np.arange(n) / SR
        I_s = np.interp(tt * CR, np.arange(len(I)), I).astype(np.float32); B_s = np.interp(tt * CR, np.arange(len(B)), B).astype(np.float32)
        # strings: gain follows intensity (about 14 dB between calm and the peak of the swell); brightness opens with it
        g = 10 ** ((-15.0 * (1 - I_s) ** 1.1 + 2.0 * dsp.smoothstep(I_s, 0.8, 1.0)) / 20.0)
        body = (self.strings.buf + self.synth_pad.buf)
        dark = dsp.lowpass(body, 1500, 2, axis=0); mid = dsp.lowpass(body, 3600, 2, axis=0); bright = dsp.lowpass(body, 9500, 2, axis=0)
        w_d = np.clip(1 - 2 * B_s, 0, 1); w_b = np.clip(2 * B_s - 1, 0, 1); w_m = 1 - w_d - w_b
        pad = (dark * w_d[:, None] + mid * w_m[:, None] + bright * w_b[:, None]) * g[:, None]
        del dark, mid, bright, body
        solo = self.solo.buf * (10 ** (-5.0 / 20)) * (10 ** (-3.0 * (1 - I_s) / 20)).astype(np.float32)[:, None]
        pluck = dsp.lowpass(self.pluck.buf, 5200, 2, axis=0) * (10 ** (-5.5 / 20))                  # no sharp pick or pizzicato edge above ~5 kHz
        drums = dsp.lowpass(self.drums.buf, 5500, 2, axis=0) * (10 ** (-6.0 / 20)); hitbus = self.hitbus.buf * (10 ** (-3.0 / 20)); air = self.hit_air.buf
        # balance report: RMS of each bus in each section, before the room (what the arrangement is doing)
        self.balance = []
        for s in self.plan['sections']:
            a, b = int(s['t'] * SR), int(min(s['t1'], self.D) * SR)
            if b - a < SR: continue
            r = lambda x: round(float(10 * np.log10((x[a:b] ** 2).mean() + 1e-12)), 1)
            self.balance.append({'t': round(s['t'], 1), 'mood': s['mood'], 'pad': r(pad), 'solo': r(solo), 'pluck': r(pluck), 'drums': r(drums), 'hits': r(hitbus)})
        rt = self.pal['rt60']
        hall = dsp.make_ir(rt, np.random.default_rng(self.plan['seed'] + 101)); room = dsp.make_ir(0.8, np.random.default_rng(self.plan['seed'] + 202), predelay=0.008)
        send_hall = pad * 0.30 + solo * 0.50 + pluck * 0.38 + hitbus * 0.30 + air * 0.5
        send_room = drums * 0.22 + pluck * 0.12
        wet = dsp.convolve(send_hall, hall) * 1.0 + dsp.convolve(send_room, room) * 1.0
        # a pitch-quiet dry bleed: wet is what makes it warm, so keep the dry part moderate
        mix = pad + solo * 0.85 + pluck * 0.9 + drums * 0.85 + hitbus * 0.9 + air * 0.4 + wet * 0.9
        del wet, send_hall, send_room
        # master EQ: tidy the lows, a gentle scoop where the voice lives, soften the top
        mix = dsp.highpass(mix, 38, 2, axis=0)
        mix = dsp.eq(mix, [dsp.peaking_sos(2300, -2.5, 0.7), dsp.peaking_sos(220, 1.2, 0.8), dsp.high_shelf_sos(7000, -1.0)], axis=0)
        mix = dsp.lowpass(mix, 13500, 1, axis=0)
        # fades: in at the start, the end fade
        D = self.D; ef = self.plan['end_fade']
        mix = mix[: int(D * SR)]
        nin = int(2.5 * SR); mix[:nin] *= (np.sin(np.linspace(0, np.pi / 2, nin)) ** 2)[:, None]
        nout = int(ef * SR); mix[-nout:] *= (np.cos(np.linspace(0, np.pi / 2, nout)) ** 2)[:, None]
        return mix.astype(np.float32)


def finalise(mix, target_lufs=-23.0, ceiling_db=-3.5):
    """loudness-normalise (integrated, BS.1770) and peak-limit; returns the audio and its measurements"""
    lu = dsp.loudness(mix); y = mix * db(target_lufs - lu)
    y = dsp.limiter(y, ceiling_db)
    return y, {'lufs': round(dsp.loudness(y), 2), 'peak_dbfs': round(float(dsp.lin2db(np.abs(y).max())), 2)}


def render_plan(plan, engine='auto', target_lufs=-23.0, log=lambda *a: None):
    c = Composer(plan, engine, log); mix = c.render()
    y, meas = finalise(mix, target_lufs)
    info = {'plan': c.plan, 'engine': 'samples+synth' if c.use_samples else 'synth', **meas, 'chords': c.info['chords'], 'hits': c.info['hits'],
            'beats': c.beats[:2000], 'curves': {k: [round(float(v), 3) for v in c.curves[k][::CR // 5]] for k in c.curves}, 'curve_hz': 5,
            'solo_events': len(c.info['solo']), 'balance_db': c.balance, 'tonic': plan.get('key', c.pal['key']), 'mode': c.plan['mode']}
    return y, info


def main():
    ap = argparse.ArgumentParser(description='free procedural score engine')
    ap.add_argument('plan'); ap.add_argument('-o', '--out', default='score.wav')
    ap.add_argument('--engine', default='auto', choices=['auto', 'synth', 'samples']); ap.add_argument('--seed', type=int)
    ap.add_argument('--lufs', type=float, default=-23.0); ap.add_argument('--info', help='write the render info (chords, hits, curves) as JSON')
    ap.add_argument('--excerpt', nargs=2, type=float, metavar=('START', 'LEN'), help='write only this part of the render')
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    if a.seed is not None: plan['seed'] = a.seed
    t0 = time.time()
    y, info = render_plan(plan, a.engine, a.lufs, log=lambda *x: print('  ', *x, flush=True))
    import soundfile as sf
    if a.excerpt:
        s, l = int(a.excerpt[0] * SR), int(a.excerpt[1] * SR); y = y[s:s + l].copy()
        nf = int(0.4 * SR); y[:nf] *= np.linspace(0, 1, nf)[:, None]; y[-nf:] *= np.linspace(1, 0, nf)[:, None]
    sf.write(a.out, y, SR, subtype='PCM_16')
    if a.info: json.dump(info, open(a.info, 'w'), indent=1)
    print(f'{a.out}: {len(y) / SR:.1f} s, {info["engine"]}, {info["lufs"]} LUFS, peak {info["peak_dbfs"]} dBFS, {time.time() - t0:.1f} s')


if __name__ == '__main__':
    main()
