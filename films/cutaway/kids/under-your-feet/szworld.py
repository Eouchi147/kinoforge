"""Who lives under your feet? The park lawn, the clock of beats and the seasons (pure numpy, no bpy).

One block, one fixed view: a slice of a park lawn with a big tree, lifted out of the land (the Cutaway lifted slice).
The top never changes height; what changes is the SEASON on top (the years passing, the seasons-loop grammar Sam loves)
and the life under it. Every height, colour and amount is a pure function of t (seconds), so any frame renders alone.

Times: beats.json (Sam 23 Oct: a silent film; 10 beats timed to Mozart, The Marriage of Figaro, overture). blender.py holds the
one event table (beat, fraction) and calls set_events(); everything here reads the resulting B.<event> seconds.

Fable (films/styles/cutaway/art/fable.py) reads this module by its name `szworld`: weights(t) sets the painted sky card,
the hills and the sun (spring, summer, autumn, winter); cv(name, t) answers its 'snow' and 'dens' questions.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24

# ------------------------------------------------------------------ the block and its heights (metres)
SX, SY = 3.6, 2.2          # block width (x, the front face) and depth (y)
HX, HY = SX / 2, SY / 2
ZB = -1.05                 # bottom of the block
Z_NOW = 0.0                # the lawn
Z_MAX = 0.0                # the soil record starts at the lawn
STACK = [('topsoil', 0.24, (0.34, 0.20, 0.14), 0.04), ('loam', 0.22, (0.50, 0.30, 0.20), 0.08), ('clay', 0.22, (0.74, 0.46, 0.30), 0.10),
         ('sand', 0.18, (0.86, 0.66, 0.40), 0.14)]
BELOW = [('rock', 1.0, (0.24, 0.36, 0.44), 0.30)]
STRATA = STACK + BELOW


# ------------------------------------------------------------------ small maths
def smooth(a, b, x):
    u = np.clip((np.asarray(x, float) - a) / (b - a + 1e-12), 0.0, 1.0); return u * u * (3 - 2 * u)

def sm(a, b, x):
    """Scalar smoothstep (float)."""
    return float(smooth(a, b, x))

def _h2(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + (seed * 2654435761 & 0xffffffff)) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffffff) / float(0xffffff)

def vnoise(x, y, seed=0):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ix = np.floor(x).astype(np.int64); iy = np.floor(y).astype(np.int64); fx = x - ix; fy = y - iy
    u = fx * fx * (3 - 2 * fx); v = fy * fy * (3 - 2 * fy)
    a = _h2(ix, iy, seed); b = _h2(ix + 1, iy, seed); c = _h2(ix, iy + 1, seed); d = _h2(ix + 1, iy + 1, seed)
    return ((a + (b - a) * u) * (1 - v) + (c + (d - c) * u) * v) * 2 - 1

def fbm(x, y, seed=0, octaves=3, freq=1.0):
    s = 0.0; a = 1.0; n = 0.0
    for o in range(octaves):
        s = s + a * vnoise(x * freq * 2 ** o + 17.1 * o, y * freq * 2 ** o - 9.3 * o, seed + o * 101); n += a; a *= 0.5
    return s / n

def keys(t, ks):
    """Keyframes [(time, value)] with smoothstep easing, held flat before the first and after the last (not periodic)."""
    ks = sorted(ks, key=lambda k: k[0]); t = float(t)
    if t <= ks[0][0]: return ks[0][1]
    for (a, va), (b, vb) in zip(ks, ks[1:]):
        if t < b:
            u = (t - a) / max(b - a, 1e-9); u = u * u * (3 - 2 * u)
            if isinstance(va, (tuple, list)): return tuple(p + (q - p) * u for p, q in zip(va, vb))
            return va + (vb - va) * u
    return ks[-1][1]

def win(t, a, b, r=0.3):
    """1 inside [a, b] with eased edges of r seconds, 0 outside."""
    return sm(a, a + r, t) * (1 - sm(b - r, b, t))


# ------------------------------------------------------------------ the story clock: beats.json + the event table
BEATS_JSON = json.load(open(os.path.join(HERE, 'beats.json')))
BEATS = [dict(name=b['name'], t0=float(b['t'][0]), t1=float(b['t'][1]), words=b.get('words', '')) for b in BEATS_JSON['beats']]
BEAT = {b['name']: b for b in BEATS}
DURATION = float(BEATS_JSON.get('duration', BEATS[-1]['t1']))
KEY_WORD = BEATS_JSON.get('key_word', 'CICADA')
TIMING_SOURCE = 'beats.json'


def bt(name, u=0.0):
    """Time u of the way through the beat called `name` (u below 0 or above 1 reaches before or after it)."""
    b = BEAT[name]; return b['t0'] + u * (b['t1'] - b['t0'])


class Beats:
    pass


B = Beats()


def set_events(table):
    """table: {event: (beat name, u)} -> B.<event> in seconds."""
    for k, (name, u) in table.items(): setattr(B, k, bt(name, u))


WORD_IN = {}     # beat name -> start time of its words, when the music wants them later than the beat (set by blender.py)


def word_windows():
    """(text, t_in, t_out) for each beat that has words: in with a soft pop after the beat starts (or at WORD_IN), out
    before it ends, never under 2.5 s on screen. The key word (CICADA) is the label on the nymph, the rest are captions."""
    out = []
    for b in BEATS:
        w = b['words'].strip()
        if not w: continue
        a = WORD_IN.get(b['name'], b['t0'] + 0.35); z = max(b['t1'] - 0.25, a + 2.5)
        out.append((w, a, min(z, DURATION)))
    return out


# ------------------------------------------------------------------ the years: seasons on top
# y(t) in years: the hook and the first beat of the story stand in high summer; then the years run (one slow year, then a
# race that eases to a stop in a warm spring-summer for the emergence). One whole turn of y is one year.
Y_SUMMER = 0.375
N_YEARS = 7


_YT = {}


def _years_table():
    """Years elapsed against t: a slow first year (the seasons turn once, gently), then a race that eases to a stop. The speed
    is a ramped curve integrated once (pure function of the events), scaled so exactly N_YEARS years pass."""
    key = (B.yr0, B.yr1, B.stack0)
    if _YT.get('key') == key: return _YT
    ts = np.arange(B.yr0 - 0.5, B.yr1 + 1.0, 1.0 / 240.0); y0 = B.yr0; y1 = B.yr1; r0 = B.stack0 - 0.6
    v = np.interp(ts, [y0, y0 + 0.9, r0 - 0.4, r0 + 0.5, y1 - 2.3, y1], [0.0, 0.136, 0.136, 1.4, 1.4, 0.0], left=0.0, right=0.0)
    e = np.concatenate([[0.0], np.cumsum((v[1:] + v[:-1]) * 0.5 / 240.0)]); e = e * (N_YEARS / e[-1])
    _YT.update(key=key, ts=ts, e=e); return _YT


def years(t):
    """Year phase y(t): high summer until the first year starts, then N_YEARS whole turns (the seasons loop)."""
    T_ = _years_table(); return Y_SUMMER + float(np.interp(float(t), T_['ts'], T_['e']))


def season_w(y):
    """(spring, summer, autumn, winter) weights at year phase y (circular, linear between the four season centres)."""
    p = (float(y) % 1.0) * 4.0 - 0.5; i = int(math.floor(p)); a = p - i
    w = np.zeros(4); w[i % 4] += 1 - a; w[(i + 1) % 4] += a; return w


def weights(t):
    """Fable's four moods: (spring, summer, autumn, winter)."""
    return season_w(years(t))


def cv(name, t):
    """Curves Fable asks for by name on a kit scene: snow on the evergreens in winter; canopies full."""
    if name == 'snow': return float(weights(t)[3])
    if name == 'dens': return 1.0
    raise KeyError(name)


# ------------------------------------------------------------------ places shared by the lawn and the cut face
TX, TY = -0.80, -0.68          # the big tree's trunk on the lawn
ROOT_X = -0.58                 # where its roots meet the top of the cut face (seen from the camera, right under the trunk)
HOLE_XY = (-0.22, -0.98)       # the nymph's hole in the lawn, near the front edge (the shaft starts right below it on the cut face)
SHAFT_X = HOLE_XY[0]

# ------------------------------------------------------------------ the world around the slice
# The slice was lifted out of a continuous park: the land carries on all round at its natural level and far behind; beyond
# the slice's far corner it curves gently away so a horizon shows.
VIEW_AZ = -62.0            # the camera's azimuth (blender.py uses it): the land curves away from the viewer beyond the block
DROP_R = 6.0               # radius of that curve (m): a little storybook world, so the horizon, the hills and the sky show
_FH = np.array([-math.cos(math.radians(VIEW_AZ)), -math.sin(math.radians(VIEW_AZ))])
_S0 = float(max(np.array([(x, y) for x in (-HX, HX) for y in (-HY, HY)]) @ _FH))


def depth_s(x, y):
    """How far a point lies along the view (horizontal), measured like the block's corners."""
    return np.asarray(x, float) * _FH[0] + np.asarray(y, float) * _FH[1]


def drop(x, y):
    """How far the land has curved down at (x, y): nothing on the block and just beyond it, then a gentle curve."""
    s = np.maximum(depth_s(x, y) - _S0, 0.0); return s * s / (2 * DROP_R)


def in_block(x, y):
    return (np.abs(np.asarray(x)) < HX) & (np.abs(np.asarray(y)) < HY)


# ------------------------------------------------------------------ the lifted slice
GAP = 0.32                 # underside to land
HM = 0.10                  # the hole is this much wider than the slice on every side
HOLE_FLOOR = Z_NOW - 1.05  # the hole is as deep as the slice


def lift(t):
    """How high the slice floats: its full depth plus the gap, bobbing a few centimetres on a slow sine."""
    return -ZB + GAP + 0.025 * math.sin(2 * math.pi * float(t) / 7.5)


def in_slice(x, y):
    return (np.abs(np.asarray(x, float)) <= HX + 1e-6) & (np.abs(np.asarray(y, float)) <= HY + 1e-6)


def in_hole(x, y):
    return (np.abs(np.asarray(x, float)) < HX + HM - 1e-6) & (np.abs(np.asarray(y, float)) < HY + HM - 1e-6)


def far(x, y):
    """0 on the block; a small step down just outside it (the cut-out reads as the hero), then more haze with distance."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    d = np.hypot(np.maximum(np.abs(x) - HX, 0), np.maximum(np.abs(y) - HY, 0))
    return np.where(in_block(x, y), 0.0, 0.18 + 0.62 * smooth(0.0, 9.0, d))


def relief(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return 0.016 * fbm(x, y, 5, 3, 0.9) + 0.022 * smooth(-0.2, 1.1, y) * (0.6 + 0.4 * fbm(x, y, 9, 2, 0.6))


def top_h(x, y, t):
    """Height of the ground at (x, y): on the slice (its footprint, edges included) the lawn lifted by lift(t); around it
    the land at its natural level, curving away beyond the far corner."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return np.where(in_slice(x, y), slice_h(x, y, t) + lift(t), land_h(x, y, t))


def land_h(x, y, t):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return Z_NOW + relief(x, y) - drop(x, y)


def slice_h(x, y, t):
    """The slice's own top in its own frame (before the lift): the lawn."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return Z_NOW + relief(x, y)
