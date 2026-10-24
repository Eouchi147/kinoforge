"""Where does rain come from? The land, the clock of beats and the moods (pure numpy, no bpy).

One lifted slice of a hillside (topsoil, subsoil, a sandy water-bearing layer, clay, rock) with a brook that runs down into
a little lake, floating above the hole it came from; the living world carries on all round (hills, a village, a river that
runs on to the sea at the horizon). The sky above carries the story: the sun warms the water, invisible vapour rises,
cools into tiny drops that make a cloud, about a million drops join into one raindrop, the rain falls, soaks into the
ground, runs into the brook, the lake and the river, and the sun comes out for a rainbow. Every height, colour and amount
is a pure function of t (seconds), so any frame renders alone.

Times: beats.json; blender.py holds the one event table (beat, fraction) and calls set_events(); everything here reads the
resulting B.<event> seconds. Fable (films/styles/cutaway/art/fable.py) reads this module by its name `szworld`: weights(t)
sets the painted sky card, the hills and the sun; cv(name, t) answers its 'snow' and 'dens' questions.
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
Z_NOW = 0.0                # the meadow's level
Z_MAX = 0.14               # top of the topsoil band (the hill's crest stays inside it)
# the soil record, from the top down: (name, thickness m, sRGB, pebbles). Names pick Fable's band paint (topsoil plum, loam
# deep coral, sand pale orange, clay coral, rock midnight). The sand is the water-bearing layer (the groundwater).
STRATA = [('topsoil', 0.14, (0.34, 0.20, 0.16), 0.04), ('loam', 0.16, (0.56, 0.34, 0.22), 0.10), ('sand', 0.28, (0.92, 0.72, 0.42), 0.14),
          ('clay', 0.14, (0.72, 0.42, 0.34), 0.03), ('chalk', 0.14, (0.70, 0.78, 0.70), 0.06), ('rock', 1.0, (0.20, 0.34, 0.42), 0.30)]
SAND_TOP = Z_MAX - 0.30      # the sand layer, absolute z of its top and bottom
SAND_BOT = SAND_TOP - 0.28
GW_LO, GW_HI = SAND_BOT + 0.07, SAND_TOP - 0.05      # the water table before and after the rain

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
# Sam, 23 Oct 20:09: a silent story (no narration), music and sound effects carry it; beats.json is the source of truth,
# timed to the phrases of the chosen recording. blender.py holds the ONE table that
# anchors every event to a beat (beat name, fraction u of the way through it); set_events() turns it into seconds here.
BEATS_JSON = json.load(open(os.path.join(HERE, 'beats.json')))
BEATS = [dict(name=b['name'], t0=float(b['t'][0]), t1=float(b['t'][1]), words=b.get('words', '')) for b in BEATS_JSON['beats']]
BEAT = {b['name']: b for b in BEATS}
DURATION = float(BEATS_JSON.get('duration', BEATS[-1]['t1']))
KEY_WORD = BEATS_JSON.get('key_word', 'CLOUD')
TIMING_SOURCE = 'beats.json'


def bt(name, u=0.0):
    """Time u of the way through the beat called `name` (u below 0 or above 1 reaches before or after it)."""
    b = BEAT[name]; return b['t0'] + u * (b['t1'] - b['t0'])


class Beats:
    pass


B = Beats()
SLOTS = []
COMPAT = ['rw0', 'rw1', 'stack0', 'stack1', 'rain0', 'erode1', 'label0', 'label1', 'hold0', 'hold1']


def set_events(table):
    """table: {event: (beat name, u)} -> B.<event> in seconds; then the derived times (the five layer slots)."""
    for k, (name, u) in table.items(): setattr(B, k, bt(name, u))
    for k in COMPAT:          # events of the pilot that a drop-in szwords.py may still read: never inside this film
        if not hasattr(B, k): setattr(B, k, DURATION + 50.0 + COMPAT.index(k))


WORD_IN = {}     # beat name -> start time of its words, when the music wants them later than the beat (set by blender.py)


def word_windows():
    """(text, t_in, t_out) for each beat that has words: in with a soft pop after the beat starts (or at WORD_IN), out
    before it ends, never under 2.5 s on screen. The key word (if a beat carries it with a ! mark) is the label, the rest are captions."""
    out = []
    for b in BEATS:
        w = b['words'].strip()
        if not w: continue
        a = WORD_IN.get(b['name'], b['t0'] + 0.35); z = max(b['t1'] - 0.25, a + 2.5)
        out.append((w, a, min(z, DURATION)))
    return out



# ------------------------------------------------------------------ the story in time
def sunny(t):
    """1 = warm bright morning sun (the hook and the sun warming the water), eased down as the cloud darkens."""
    return keys(t, [(0.0, 0.7), (B.sun0, 0.7), (B.sun1, 1.0), (B.dark0, 1.0), (B.dark1, 0.0), (B.sunback0, 0.0), (B.sunback1, 1.0)])

def wet(t):
    """How wet the ground and air are: rain wets the top and the stream, the sun dries them slowly."""
    return keys(t, [(B.drop0, 0.0), (B.drop0 + 4.0, 1.0), (B.drop1, 1.0), (B.drop1 + 8.0, 0.35)])

def rain_k(t):
    """Rain amount 0..1 (first drops, soft rain, easing off): drives the streaks, the cloud's dark and the splashes."""
    first = keys(t, [(B.drop0, 0.0), (B.drop0 + 0.4, 0.06), (B.drop0 + 2.6, 0.22), (B.rainsoft, 0.55), (B.drop1 - 2.0, 0.55), (B.drop1 + 0.8, 0.0)])
    return first if B.drop0 - 0.1 < t < B.drop1 + 1.0 else 0.0

def front(t):
    """Depth (m) the wet front has sunk below the surface (the soil darkens from the top down)."""
    return keys(t, [(B.drop0 + 0.8, 0.0), (B.soak1, 0.46)])

def gw(t):
    """The water table (slice z) in the sand: it rises once the rain has sunk in."""
    return keys(t, [(B.soak0, GW_LO), (B.gw1, GW_HI)])

def channel(t):
    """Width and depth of the brook: a thin trickle before the rain, swollen after it, easing back."""
    sw = keys(t, [(B.drop0 + 1.0, 0.0), (B.swell1, 1.0), (B.sunback1 + 6.0, 0.35)])
    return 0.105 + 0.075 * sw, 0.040 + 0.012 * sw

def stream_flow(t):
    return keys(t, [(0.0, 0.4), (B.drop0, 0.4), (B.swell1, 1.0), (DURATION, 0.7)])

def era(t): return 1.0
def today(t): return 1.0
def ancient(t): return 0.0
def base(t): return Z_NOW
def flood_level(t): return -1.0

# ------------------------------------------------------------------ the world around the slice
VIEW_AZ = -62.0
DROP_R = 6.0
_FH = np.array([-math.cos(math.radians(VIEW_AZ)), -math.sin(math.radians(VIEW_AZ))])
_S0 = float(max(np.array([(x, y) for x in (-HX, HX) for y in (-HY, HY)]) @ _FH))

def depth_s(x, y):
    return np.asarray(x, float) * _FH[0] + np.asarray(y, float) * _FH[1]

def drop(x, y):
    s = np.maximum(depth_s(x, y) - _S0, 0.0); return s * s / (2 * DROP_R)

def in_block(x, y):
    return (np.abs(np.asarray(x)) < HX) & (np.abs(np.asarray(y)) < HY)

GAP = 0.32
HM = 0.10
HOLE_FLOOR = Z_NOW - 1.05

def lift(t):
    return -ZB + GAP + 0.025 * math.sin(2 * math.pi * float(t) / 7.5)

def in_slice(x, y):
    return (np.abs(np.asarray(x, float)) <= HX + 1e-6) & (np.abs(np.asarray(y, float)) <= HY + 1e-6)

def in_hole(x, y):
    return (np.abs(np.asarray(x, float)) < HX + HM - 1e-6) & (np.abs(np.asarray(y, float)) < HY + HM - 1e-6)

def far(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    d = np.hypot(np.maximum(np.abs(x) - HX, 0), np.maximum(np.abs(y) - HY, 0))
    return np.where(in_block(x, y), 0.0, 0.18 + 0.62 * smooth(0.0, 9.0, d))

# the brook comes from far behind on the left, runs down the hillside past the front of the slice into the lake, and goes
# on out through the back into the land behind: the river that runs to the sea at the horizon
RIVER = np.array([(-10.0, 5.5), (-5.5, 2.6), (-2.6, 0.9), (-1.2, 0.30), (-0.3, -0.08), (0.5, -0.20), (1.15, -0.02), (1.45, 0.55),
                  (1.55, 1.3), (2.2, 2.6), (4.5, 4.5), (9.0, 6.5)])
LAKE = (0.50, -0.30, 0.62, 0.36)        # centre x, y, radii x, y (in the slice's own frame: the lake sits in the slice)
LAKE_D = 0.060                          # how deep the lake's bed lies below the meadow

def _seg_dist(P, x, y):
    d = np.full(np.shape(x), 1e9)
    for a, b in zip(P[:-1], P[1:]):
        ab = b - a; L2 = ab @ ab + 1e-12
        t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / L2, 0, 1)
        d = np.minimum(d, np.hypot(x - a[0] - t * ab[0], y - a[1] - t * ab[1]))
    return d

def lake_r(x, y):
    """Normalised elliptical radius from the lake's centre (1 at the shore)."""
    return np.hypot((np.asarray(x, float) - LAKE[0]) / LAKE[2], (np.asarray(y, float) - LAKE[1]) / LAKE[3])

def river_d(x, y):
    """Distance to the water course; the lake counts as a wide part of it (inside the lake: small)."""
    d = _seg_dist(RIVER, np.asarray(x, float), np.asarray(y, float))
    return np.minimum(d, np.maximum(0.0, lake_r(x, y) - 1.0) * 0.42 + 0.02)

def hill(x, y):
    """A gentle hillside: higher toward the far left corner, flattening toward the front right."""
    return 0.17 * smooth(-1.3, 1.5, depth_s(x, y))

def relief(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return 0.016 * fbm(x, y, 5, 3, 0.9) + hill(x, y)

def carve(x, y, t):
    """How far the brook and the lake cut into the ground."""
    w, d = channel(t)
    c = d * smooth(w + 0.06, max(w - 0.05, 0.0), _seg_dist(RIVER, np.asarray(x, float), np.asarray(y, float)))
    lk = LAKE_D * smooth(1.0, 0.82, lake_r(x, y))
    return np.maximum(c, lk)

def top_h(x, y, t):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return np.where(in_slice(x, y), slice_h(x, y, t) + lift(t), land_h(x, y, t))

def land_h(x, y, t):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return Z_NOW + relief(x, y) - carve(x, y, t) * (1.0 - 0.0) - drop(x, y)

def slice_h(x, y, t):
    """The slice's own top in its own frame (before the lift)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return Z_NOW + relief(x, y) - carve(x, y, t)

LAKE_Z0 = Z_NOW + float(hill(np.array([LAKE[0]]), np.array([LAKE[1]]))[0]) - LAKE_D * 0.75      # lake level, slice frame (before rain)

def lake_level(t):
    """The lake surface in the slice's own frame (it rises a little with the rain) -- absolute z needs + lift(t)."""
    return LAKE_Z0 + 0.012 * keys(t, [(B.drop0 + 3.0, 0.0), (B.swell1 + 2.0, 1.0), (B.sunback1 + 8.0, 0.4)])

def water_level(t):
    """The brook's surface on the slice (absolute z, lift included) at its mid height (used for floating things)."""
    w, d = channel(t)
    return Z_NOW - 0.012 - 0.5 * d + lift(t)

def land_water(t):
    w, d = channel(t)
    return Z_NOW - 0.012 - 0.5 * d

# ------------------------------------------------------------------ colours in time (the painted sky card and the light)
P_SUN, P_WARM, P_EVE, P_RAIN = (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)


def weights(t):
    """(spring, summer, autumn, winter) for Fable's sky card, the hills and the sun: spring = the fresh morning, summer =
    the warm sun, winter = the grey of rain, autumn = a golden clearing after the rain."""
    t = float(t)
    ks = [(0.0, P_SUN), (B.sun0, P_SUN), (B.sun1, (0.25, 0.75, 0, 0)), (B.cool1, (0.55, 0.2, 0, 0.25)), (B.dark1, (0.1, 0, 0, 0.9)),
          (B.drop0 + 3.0, P_RAIN), (B.drop1 - 1.0, (0, 0, 0.1, 0.9)), (B.sunback0, (0.1, 0.1, 0.5, 0.3)), (B.sunback1, (0.5, 0.2, 0.3, 0.0)),
          (B.rainbow1, P_SUN), (DURATION + 1, P_SUN)]
    w = np.array(keys(t, [(a, tuple(float(x) for x in v)) for a, v in ks]), float)
    return w / max(w.sum(), 1e-6)


CURVES = {}

def cv(name, t):
    """Curves Fable asks for by name on a kit scene: no snow; canopies full."""
    if name == 'snow': return 0.0
    if name == 'dens': return 1.0
    raise KeyError(name)

# ------------------------------------------------------------------ the child, the puddle, the jumps
PUDDLE = (-0.72, -0.74, 0.34, 0.20)      # centre x, y (slice frame), radii x, y
JUMP_T = 1.6                             # one jump in the puddle takes 1.6 s: up for the first half, the landing splash at 0.8 s


def jump_phase(t):
    """(k, u): which jump (0,1,2... from B.jump0 to B.jump1) and how far (0..1) through it; k = -1 outside the jumping."""
    if t < B.jump0 or t > B.jump1 + 0.8: return -1, 0.0
    x = (t - B.jump0) / JUMP_T; return int(x), x - int(x)


def landings():
    """Seconds at which the child lands in the puddle (a splash): the jumps of the downpour and the happy jump at the end."""
    out = []; k = 0
    while B.jump0 + (k + 0.5) * JUMP_T <= B.jump1 + 0.01: out.append(B.jump0 + (k + 0.5) * JUMP_T); k += 1
    out.append(B.chord2); return out


def puddle_size(t):
    return keys(t, [(B.drop0 + 1.5, 0.0), (B.jump0 - 1.0, 0.8), (B.jump1, 1.0), (B.sunback1 + 4, 0.8), (DURATION, 0.55)])


def calm(t):
    """1 when it is dry (before the cloud darkens, and after the rain): birds, butterflies, kites and the rabbit are out."""
    return 1.0 - sm(B.dark0 + 1.5, B.dark1, t) * (1 - sm(B.drop1, B.sunback0 + 1.5, t))


def rock_patch(x, y):
    return np.zeros_like(np.asarray(x, float))
