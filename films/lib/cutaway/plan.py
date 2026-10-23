"""The Cutaway line's plan: spec.json + cues.json -> sets (Layouts), a timeline of shots, overlays, all in seconds.

Pure Python (numpy). The validator (tools/validate.py) checks the plan; the engine (engine.py) builds and renders it.
Problems are collected, never raised one at a time, so a model gets every error in one round:
plan.errors (the film cannot be made like this) and plan.warnings (it can, but it breaks a house rule softly).
"""
import json
import os
import re

import presets as P
from camera import pose, CAMERAS_OK
from layout import Layout, LayoutError
from timeref import Times, TimeRefError

DASH = re.compile(r'[–—]|\.\.\.|…')
EMOJI = re.compile('[\U0001F000-\U0001FAFF☀-➿️]')


def load(film_dir, spec_path=None):
    """(spec, cues) of a film folder; spec_path (relative to the folder) picks a candidate spec."""
    sp = os.path.join(film_dir, spec_path or os.environ.get('KF_SPEC') or 'spec.json')
    spec = json.load(open(sp)); cues = json.load(open(os.path.join(film_dir, 'cues.json')))
    return spec, cues


class Plan:
    def __init__(self, spec, cues):
        self.spec = spec; self.cues = cues; self.errors = []; self.warnings = []
        self.fmt = spec.get('format', '16:9')
        if self.fmt not in P.REF: self.errors.append('format must be "16:9" or "9:16"'); self.fmt = '16:9'
        self.T = Times(cues, spec.get('marks')); self.duration = self.T.duration
        self.sets = {}; self.shots = []; self.scenes = []
        self._text_rules(spec)
        self._sets(); self._timeline(); self._cards()

    # ---------------------------------------------------------------- helpers
    def t(self, ref, where):
        try: return self.T.t(ref)
        except TimeRefError as e: self.errors.append(f'{where}: {e}'); return None

    def _text_rules(self, spec):
        def walk(o, path):
            if isinstance(o, dict):
                for k, v in o.items(): walk(v, f'{path}.{k}')
            elif isinstance(o, list):
                for i, v in enumerate(o): walk(v, f'{path}[{i}]')
            elif isinstance(o, str):
                if EMOJI.search(o): self.errors.append(f'{path}: no emoji anywhere (CRAFT.md 6)')
        walk(spec, 'spec')

    def _onscreen(self, text, where, max_words=5, max_chars=34):
        if not isinstance(text, str) or not text.strip(): self.errors.append(f'{where}: text is empty'); return ''
        if DASH.search(text): self.errors.append(f'{where}: no em or en dashes and no "..." on screen ("{text}")')
        if len(text.split()) > max_words or len(text) > max_chars:
            self.warnings.append(f'{where}: "{text}" is long for the screen (at most {max_words} words, {max_chars} characters)')
        return text.strip()

    # ---------------------------------------------------------------- sets
    def _sets(self):
        sets = self.spec.get('sets')
        if not isinstance(sets, dict) or not sets: self.errors.append('sets: at least one set is needed ({"name": {...presets}})'); return
        for name, s in sets.items():
            if not re.match(r'^[a-z][a-z0-9_]{0,23}$', name): self.errors.append(f'sets.{name}: set names are lowercase letters, digits and _ (start with a letter)')
            if not isinstance(s, dict): self.errors.append(f'sets.{name}: must be an object'); continue
            if s.get('like'):
                base = sets.get(s['like'])
                if not isinstance(base, dict): self.errors.append(f'sets.{name}: like {s["like"]!r} is not a set'); continue
                s = {**{k: v for k, v in base.items() if k != 'like'}, **{k: v for k, v in s.items() if k != 'like'}}
            try: self.sets[name] = Layout(name, s, self.fmt)
            except LayoutError as e: self.errors.append(str(e))
            except Exception as e: self.errors.append(f'sets.{name}: {type(e).__name__}: {e}')

    # ---------------------------------------------------------------- scenes and shots
    def _timeline(self):
        scenes = self.spec.get('scenes')
        if not isinstance(scenes, list) or not scenes: self.errors.append('scenes: write the scene list first (each scene: name, job, set, begin, middle, end, shots)'); return
        t0 = 0.0; allshots = [(si, sh) for si, sc in enumerate(scenes) for sh in (sc.get('shots') or [])]
        for si, sc in enumerate(scenes):
            w = f'scenes[{si}]'
            if not isinstance(sc, dict): self.errors.append(f'{w}: must be an object'); continue
            for k in ('name', 'job'):
                if not str(sc.get(k) or '').strip(): self.errors.append(f'{w}: needs "{k}" (CRAFT.md 2: the scene\'s dramatic question)')
            if not all(str(sc.get(k) or '').strip() for k in ('begin', 'middle', 'end')):
                self.warnings.append(f'{w} ({sc.get("name")}): write begin, middle and end (what we see arrive, change, and end)')
            if sc.get('set') not in self.sets and not all(isinstance(x, dict) and x.get('set') in self.sets for x in (sc.get('shots') or [])):
                self.errors.append(f'{w}: set {sc.get("set")!r} is not in sets ({", ".join(self.sets) or "none"})')
            if not sc.get('shots'): self.errors.append(f'{w}: no shots'); continue
            self.scenes.append({'i': si, 'name': sc.get('name'), 'job': sc.get('job'), 'set': sc.get('set'), 'shots': []})
        n = len(allshots)
        for j, (si, sh) in enumerate(allshots):
            w = f'scenes[{si}].shots[{[x for x in allshots[:j] if x[0] == si].__len__()}]'
            if not isinstance(sh, dict): self.errors.append(f'{w}: must be an object'); continue
            last = j == n - 1
            if last:
                t1 = self.duration
                if sh.get('until') is not None:
                    u = self.t(sh['until'], f'{w}.until')
                    if u is not None and u < self.duration - 0.05: self.warnings.append(f'{w}: the last shot runs to the end of the film (its until {u:.2f} s is ignored)')
            else:
                if sh.get('until') is None: self.errors.append(f'{w}: needs "until" (only the last shot runs to the end)'); t1 = None
                else: t1 = self.t(sh['until'], f'{w}.until')
            cam = sh.get('camera')
            if cam not in CAMERAS_OK: self.errors.append(f'{w}: camera must be one of {", ".join(CAMERAS_OK)} (got {cam!r})')
            if not str(sh.get('why') or '').strip(): self.errors.append(f'{w}: every cut needs "why" (new information, place, time, reaction or scale; CRAFT.md 3)')
            setn = sh.get('set') or scenes[si].get('set')
            if t1 is None: continue
            if t1 <= t0 + 1e-6: self.errors.append(f'{w}: until {t1:.2f} s is not after the shot start {t0:.2f} s (shots run in order, each ends where the next starts)'); continue
            rec = dict(sh); rec.update(i=len(self.shots), scene=si, set=setn, t0=t0, t1=t1, where=w, transition=sh.get('transition', 'cut'))
            if rec['transition'] not in ('cut', 'dip'): self.errors.append(f'{w}: transition is "cut" or "dip"')
            L = self.sets.get(setn)
            if L is not None and cam in CAMERAS_OK: self._shot_targets(rec, L, w)
            rec['labels'] = self._labels(sh.get('labels') or [], rec, L, w)
            rec['caption'] = self._caption(sh.get('caption'), rec, w)
            rec['counter'] = self._counter(sh.get('counter'), rec, w)
            self.shots.append(rec)
            if self.scenes and any(s['i'] == si for s in self.scenes): next(s for s in self.scenes if s['i'] == si)['shots'].append(rec)
            t0 = t1

    def _shot_targets(self, rec, L, w):
        cam = rec['camera']
        if cam == 'macro':
            tg = rec.get('target')
            if not isinstance(tg, str) or L.egg(tg[4:] if tg.startswith('egg:') else tg) is None:
                self.errors.append(f'{w}: macro needs "target": an egg of set {L.name} ({", ".join(e["id"] for e in L.eggs) or "it has none"})')
        if cam in ('push', 'pull') and rec.get('target') is not None:
            from camera import target_point
            if target_point(L, rec['target']) is None: self.errors.append(f'{w}: target {rec["target"]!r} is not an egg of {L.name}, "water", "mill", "house" or [x, y, z]')
        if cam == 'crane':
            if rec.get('face', '-Y') not in P.FACES: self.errors.append(f'{w}: crane face must be "-Y" or "+X"')
            to = rec.get('to')
            if isinstance(to, str):
                eg = L.egg(to[4:] if to.startswith('egg:') else to)
                if eg is None: self.errors.append(f'{w}: crane "to" {to!r} is not an egg of {L.name}')
                elif eg['face'] != rec.get('face', '-Y'): self.errors.append(f'{w}: crane "to" {to!r} is on face {eg["face"]}; set "face": "{eg["face"]}"')
            elif isinstance(to, (int, float)) and not 0.05 < to < L.depth: self.errors.append(f'{w}: crane "to" {to} m is outside the block (0 to {L.depth} m deep)')
        try: pose(rec, L, 0.5, self.fmt)
        except Exception as e: self.errors.append(f'{w}: the camera cannot be placed: {e}')

    def _slot(self, slot, w):
        if isinstance(slot, (list, tuple)) and len(slot) == 2: return (float(slot[0]), float(slot[1]))
        S = P.SLOTS[self.fmt]
        if slot not in S: self.errors.append(f'{w}: slot must be one of {", ".join(S)} or [x, y] pixels'); return S['upper-left']
        return S[slot]

    def _labels(self, labels, rec, L, w):
        out = []
        for k, lb in enumerate(labels):
            ww = f'{w}.labels[{k}]'
            if not isinstance(lb, dict): self.errors.append(f'{ww}: must be an object'); continue
            text = self._onscreen(lb.get('text'), ww)
            a = self.t(lb.get('at', rec['t0']), f'{ww}.at'); b = self.t(lb.get('until', rec['t1']), f'{ww}.until')
            if a is None or b is None: continue
            if b <= a: self.errors.append(f'{ww}: until is not after at'); continue
            if b < rec['t0'] or a > rec['t1']: self.errors.append(f'{ww}: shown {a:.2f} to {b:.2f} s, outside its shot ({rec["t0"]:.2f} to {rec["t1"]:.2f} s)'); continue
            if a < rec['t0'] - 0.01 or b > rec['t1'] + 0.01: self.warnings.append(f'{ww}: "{text}" is clipped to its shot ({rec["t0"]:.2f} to {rec["t1"]:.2f} s)')
            point = lb.get('point')
            anchor = None
            if point is not None and L is not None:
                from camera import target_point
                p = target_point(L, point)
                if p is None: self.errors.append(f'{ww}: point {point!r} is not an egg of {L.name}, "water", "mill", "house" or [x, y, z]')
                else: anchor = tuple(float(v) for v in p)
            out.append({'text': text.upper(), 'at': max(a, rec['t0']), 'until': min(b, rec['t1']), 'anchor': anchor,
                        'pos': self._slot(lb.get('slot', 'upper-left'), ww), 'slot': lb.get('slot', 'upper-left')})
        return out

    def _caption(self, c, rec, w):
        if not c: return None
        text = self._onscreen(c.get('text'), f'{w}.caption')
        a = self.t(c.get('at', rec['t0']), f'{w}.caption.at'); b = self.t(c.get('until', rec['t1']), f'{w}.caption.until')
        if a is None or b is None or b <= a: return None
        return {'text': text.upper(), 'at': max(a, rec['t0']), 'until': min(b, rec['t1'])}

    def _counter(self, c, rec, w):
        if not c: return None
        try: to = float(c['to']); fr = float(c.get('from', 0))
        except (KeyError, TypeError, ValueError): self.errors.append(f'{w}.counter: needs a number "to"'); return None
        a = self.t(c.get('at', rec['t0']), f'{w}.counter.at'); b = self.t(c.get('until', rec['t1']), f'{w}.counter.until')
        done = self.t(c.get('done', c.get('until', rec['t1'])), f'{w}.counter.done')
        if None in (a, b, done) or b <= a: return None
        cap = self._onscreen(c.get('caption', ''), f'{w}.counter.caption', 6, 40) if c.get('caption') else ''
        return {'from': fr, 'to': to, 'at': max(a, rec['t0']), 'until': min(b, rec['t1']), 'done': min(max(done, a + 0.3), b), 'caption': cap.upper(),
                'suffix': str(c.get('suffix', ''))[:3], 'pos': self._slot(c.get('slot', 'upper-right'), f'{w}.counter')}

    def _cards(self):
        ti = self.spec.get('title')
        self.title = None; self.end = None
        if not isinstance(ti, dict) or not ti.get('text'): self.warnings.append('title: no title card (the film title over the title line, set in code)')
        else:
            text = self._onscreen(ti['text'], 'title.text', 7, 40)
            tl = self.cues.get('title_line')
            a = self.t(ti.get('at', tl if tl else 1.0), 'title.at'); b = self.t(ti.get('until', (tl + '>+2.0') if tl else 5.0), 'title.until')
            if a is not None and b is not None and b > a:
                self.title = {'text': text, 'kicker': (self._onscreen(ti['kicker'], 'title.kicker', 5, 34).upper() if ti.get('kicker') else ''), 'at': a, 'until': b}
        en = self.spec.get('end')
        if isinstance(en, dict) and en.get('text'):
            self.end = {'text': self._onscreen(en['text'], 'end.text', 5, 34).upper(), 'sub': self._onscreen(en['sub'], 'end.sub', 7, 40) if en.get('sub') else '',
                        'at': self.duration - self.T.outro_s, 'until': self.duration}
        else: self.warnings.append('end: no end card over the outro (the series name and the film title)')

    # ---------------------------------------------------------------- queries
    def shot_at(self, t):
        for s in self.shots:
            if t < s['t1']: return s
        return self.shots[-1] if self.shots else None

    def sets_between(self, a, b):
        return sorted({s['set'] for s in self.shots if s['t1'] > a and s['t0'] < b + 1e-6 and s['set'] in self.sets})
