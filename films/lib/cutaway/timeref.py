"""Cue-time references for the Cutaway line (the same forms as the Battle Map engine, films/lib/battlemap/SPEC.md).

    12.5                 seconds
    "l08" / "l08>"       start / end of cue line l08
    "l08.charged"        start of the word "charged" in line l08 (case and punctuation ignored; exact match first, then prefix)
    "l08.charged>"       end of that word
    "l08.step#1"         the second "step" in the line (0-based)
    "l05.bigger+0.25"    an offset in seconds, + or -
    "start", "end"       0 and the film's end
    "outro"              the start of the end card (duration - cues.outro_s)
    "myMark"             an entry of spec.marks ({"myMark": "l03.commanders"})

Pure Python: used by the validator (no Blender) and the engine.
"""
import re

OFF = re.compile(r'^(?P<base>.+?)(?P<off>[+-]\d+(?:\.\d+)?)$')
REF = re.compile(r'^(?P<line>l\d\d)(?:\.(?P<word>[^>#]+?)(?:#(?P<nth>\d+))?)?(?P<edge>>)?$')


class TimeRefError(ValueError):
    pass


def norm(w):
    return re.sub(r'[^a-z0-9]', '', str(w).lower())


class Times:
    def __init__(self, cues, marks=None):
        self.cues = cues; self.marks = dict(marks or {})
        self.lines = {l['id']: l for l in cues.get('lines', [])}
        self.duration = float(cues['duration']); self.outro_s = float(cues.get('outro_s', 4.0))

    def t(self, ref, _depth=0):
        """Seconds for a reference; raises TimeRefError with a plain message when it does not resolve."""
        if isinstance(ref, bool) or ref is None: raise TimeRefError(f'not a time: {ref!r}')
        if isinstance(ref, (int, float)): return float(ref)
        if not isinstance(ref, str) or not ref.strip(): raise TimeRefError(f'not a time: {ref!r}')
        s = ref.strip(); off = 0.0
        m = OFF.match(s)          # a trailing +n or -n is always an offset (a word like "covid-19": write "l03.covid")
        if m: s, off = m.group('base'), float(m.group('off'))
        if s == 'start': return 0.0 + off
        if s == 'end': return self.duration + off
        if s == 'outro': return self.duration - self.outro_s + off
        if s in self.marks:
            if _depth > 4: raise TimeRefError(f'mark loop at {ref!r}')
            return self.t(self.marks[s], _depth + 1) + off
        r = REF.match(s)
        if not r: raise TimeRefError(f'unknown time reference {ref!r} (use seconds, "l03", "l03>", "l03.word", "l03.word>", offsets like "+0.5", "start", "end", "outro" or a mark)')
        ln = self.lines.get(r.group('line'))
        if ln is None: raise TimeRefError(f'{ref!r}: no cue line {r.group("line")} (lines run {min(self.lines) if self.lines else "-"} to {max(self.lines) if self.lines else "-"})')
        edge = bool(r.group('edge'))
        if not r.group('word'): return float(ln['end'] if edge else ln['start']) + off
        key = norm(r.group('word')); nth = int(r.group('nth') or 0)
        words = ln.get('words') or []
        if not key: raise TimeRefError(f'{ref!r}: empty word')
        hits = [w for w in words if norm(w[0]) == key] or [w for w in words if norm(w[0]).startswith(key)]
        if len(hits) <= nth:
            have = ' '.join(w[0] for w in words)[:200]
            raise TimeRefError(f'{ref!r}: the word "{r.group("word")}"' + (f' #{nth}' if nth else '') + f' is not in {r.group("line")} (its words: {have})')
        w = hits[nth]
        return float(w[2] if edge else w[1]) + off

    def ok(self, ref):
        try: self.t(ref); return None
        except TimeRefError as e: return str(e)
