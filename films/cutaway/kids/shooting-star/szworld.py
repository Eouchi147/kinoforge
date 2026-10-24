"""What is a shooting star? The land, the clock of beats and the moods (pure numpy, no bpy).

One lifted slice, one fixed view. The slice is a hilltop at dusk turning to night with a family camping on it (a tent, a
campfire, a telescope); the sky above is the stage (the streak, the magnifier window). The ground does not change: the
story is in the sky and in the light. Every height, colour and amount is a pure function of t (seconds), so any frame
renders alone.

Times: beats.json (Sam 23 Oct 2026: a silent film, 68.4 s, timed on the bars of Grieg's Anitra's Dance, Musopen). blender.py
holds the one event table (beat, fraction) and calls set_events(); everything here reads the resulting B.<event> seconds.

Fable (films/styles/cutaway/art/fable.py) reads this module by its name `szworld`: weights(t) is the mood of the sky and the
light (dusk, twilight, night, deep night; this film drives its OWN night sky card from them) and cv(name, t).
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
Z_NOW = 0.0                # the hilltop meadow
# the ground below the hill, from the top: (name, thickness m, sRGB, pebbles). Names pick Fable's band paint.
STRATA = [('topsoil', 0.10, (0.40, 0.26, 0.20), 0.05), ('clay', 0.14, (0.80, 0.46, 0.36), 0.10), ('sand', 0.15, (0.90, 0.74, 0.46), 0.12),
          ('gravel', 0.16, (0.46, 0.56, 0.52), 0.30), ('limestone', 0.22, (0.40, 0.58, 0.52), 0.10), ('bedrock', 1.0, (0.24, 0.36, 0.44), 0.20)]
Z_MAX = 0.0

# the camp, on the slice (x along the front face, y away from the viewer)
TENT = (-1.05, 0.42)
FIRE = (0.05, -0.12)
TELE = (1.10, -0.28)         # the tripod's centre
LOG_A = (-0.52, -0.58)      # dad's log
LOG_B = (0.62, -0.52)       # the little brother's log
TEDDY = (-0.50, 0.02)
CAT = (0.50, 0.55)
TREE = (1.42, 0.72)          # the owl tree
ROCKET = (0.82, 0.14)
SNAIL_HOME = (1.38, -HY + 0.12)
PEBBLE = (0.86, -0.78)       # the pebble the girl picks up
FLASH = (-0.30, -0.84)       # the flashlight


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
KEY_WORD = BEATS_JSON.get('key_word', 'METEOR')
TIMING_SOURCE = 'beats.json'
BAR = 1.3065            # one bar of the dance, seconds


def bt(name, u=0.0):
    """Time u of the way through the beat called `name` (u below 0 or above 1 reaches before or after it)."""
    b = BEAT[name]; return b['t0'] + u * (b['t1'] - b['t0'])


class Beats:
    pass


B = Beats()
SLOTS = []


def set_events(table):
    """table: {event: (beat name, seconds after the beat starts)} -> B.<event> in film seconds."""
    for k, (name, sec) in table.items(): setattr(B, k, BEAT[name]['t0'] + float(sec))


WORD_IN = {}     # beat name -> start time of its words, when the music wants them later than the beat (set by blender.py)


def word_windows():
    """(text, t_in, t_out) for each beat that has words: in with a soft pop after the beat starts (or at WORD_IN), out
    before it ends, never under 2.5 s on screen. The key word (METEOR!) is the label on the streak, the rest are captions."""
    out = []
    for b in BEATS:
        w = b['words'].strip()
        if not w: continue
        a = WORD_IN.get(b['name'], b['t0'] + 0.35); z = max(b['t1'] - 0.25, a + 2.5)
        out.append((w, a, min(z, DURATION)))
    return out


# ------------------------------------------------------------------ the moods: dusk, twilight, night, deep night
P_DUSK, P_TWI, P_NIGHT, P_DEEP = (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)


def weights(t):
    """(dusk, twilight, night, deep night): the sunset fades through twilight to night in the first 14 s, deep night after
    the streak. Soft blends, never a flash. Fable's season slots are used as these four moods by this film's own sky."""
    t = float(t)
    ks = [(0.0, P_DUSK), (3.0, P_DUSK), (9.0, P_TWI), (16.0, P_NIGHT), (38.0, P_NIGHT), (48.0, P_DEEP), (DURATION + 1, P_DEEP)]
    w = np.array(keys(t, [(a, tuple(float(x) for x in v)) for a, v in ks]), float)
    return w / max(w.sum(), 1e-6)


def night(t):
    """0 in the sunset, 1 in the dark (drives the paint tint, the stars, the windows, the fire's glow)."""
    return float(keys(t, [(0.0, 0.0), (2.0, 0.04), (8.0, 0.45), (15.0, 0.92), (24.0, 1.0)]))


def cv(name, t):
    """Curves Fable asks for by name on a kit scene: no snow; canopies full."""
    if name == 'snow': return 0.0
    if name == 'dens': return 1.0
    raise KeyError(name)


# ------------------------------------------------------------------ the world around the slice
VIEW_AZ = -62.0            # the camera's azimuth (blender.py uses it): the land curves away from the viewer beyond the block
DROP_R = 16.0              # radius of that curve (m): a little storybook world, so the horizon, the hills and the sky show
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
    dome = 0.075 * (1.0 - np.clip((x / HX) ** 2 * 0.5 + (y / HY) ** 2 * 0.5, 0, 1))      # the hilltop: a gentle dome
    return dome + 0.014 * fbm(x, y, 5, 3, 1.1)


# the lake: a basin in the land far behind on the left, with its water level (the land around is higher)
LAKE_C = (-5.2, 1.3)
LAKE_R = (2.5, 1.7)


def lake_z(x, y):
    """The water's surface: the land's own curve (the world curves away), a little below the unbasined ground."""
    return Z_NOW - 0.10 - drop(x, y)


def basin(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    r = np.hypot((x - LAKE_C[0]) / LAKE_R[0], (y - LAKE_C[1]) / LAKE_R[1])
    return 0.34 * smooth(1.2, 0.6, r)


def land_h(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return Z_NOW + relief(x, y) * 0.5 - basin(x, y) - drop(x, y)


def slice_h(x, y, t=0.0):
    """The slice's own top in its own frame (before the lift)."""
    return Z_NOW + relief(x, y)


def top_h(x, y, t):
    """Height of the ground at (x, y). On the slice (its footprint, edges included): the hilltop lifted by lift(t). Around
    it: the land at its natural level (the same relief, the lake's basin), curving away beyond the far corner."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return np.where(in_slice(x, y), slice_h(x, y, t) + lift(t), land_h(x, y))
