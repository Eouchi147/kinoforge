"""How does a dinosaur turn into stone? The land, the clock of beats and the moods (pure numpy, no bpy).

One block, one fixed view. The top of the block moves in time, which is the story: today's meadow at Z_NOW; time rewinds
and the ground above the old one peels away, leaving the ancient river plain at Z_ANC (the dinosaur's world); a flood lays
the mud over the skeleton (the first band, marl, whose top is today's ground); five more layers stack up to Z_MAX while the
eras race by above (forest, ice, mammoth steppe, grassland, forest); wind and rain wear the land back down to Z_NOW, right
to the fossil's own band, where a little rock face holds the bone the girl finds. Every height, colour and amount is a pure
function of t (seconds), so any frame renders alone.

Times: beats.json (Sam 23 Oct 20:09, a silent film; 10 beats over 60 s, to be re-timed to the music). blender.py holds the
one event table (beat, fraction) and calls set_events(); everything here reads the resulting B.<event> seconds.

Fable (films/styles/cutaway/art/fable.py) reads this module by its name `szworld` (as on the seasons loop): weights(t)
sets the painted sky card and cv(name, t) answers its 'snow' and 'dens' questions.
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
Z_ANC = -0.30              # the dinosaur's ground, long ago
Z_NOW = 0.0                # today's meadow
# the rock record, from the top of the full stack down: (name, thickness m, sRGB, pebbles). Names pick Fable's band paint.
STACK = [('clay', 0.07, (0.80, 0.46, 0.36), 0.05), ('ochre', 0.09, (0.86, 0.66, 0.34), 0.10), ('sand', 0.09, (0.90, 0.74, 0.46), 0.12),
         ('silt', 0.10, (0.46, 0.56, 0.52), 0.04), ('loam', 0.09, (0.62, 0.34, 0.30), 0.10), ('marl', 0.30, (0.40, 0.58, 0.52), 0.03)]
# the first band (marl) is the mud blanket with the bones; its top is exactly today's ground, so the wearing away stops
# at the fossil's own rock and the bone can poke out of it
BELOW = [('chalk', 0.16, (0.72, 0.82, 0.72), 0.06), ('pale', 0.10, (0.96, 0.86, 0.60), 0.10), ('red', 0.16, (0.90, 0.50, 0.40), 0.20),
         ('rock', 1.0, (0.24, 0.36, 0.44), 0.30)]
STRATA = STACK + BELOW
Z_MAX = Z_ANC + sum(l[1] for l in STACK)     # 0.44: the top at the end of the millions of years
# deposit tops from the first (the mud blanket) to the last, absolute z
DEPOSITS = list(np.cumsum([l[1] for l in STACK[::-1]]) + Z_ANC)

# the dinosaur's place: it lies along the front face, a little behind it, so its bones show in the cut face
DINO_K = 1.15             # the dinosaur's storybook size (about 2 m long, 1.2 m tall standing)
DINO_Y = -HY + 0.50
DINO_LIE_X = 0.20          # where its hips are when it lies down (facing +x)
DIG = (DINO_LIE_X - 0.10, DINO_Y + 0.02)   # where the girl brushes today: above the hips of the skeleton
DIG_R = 0.12

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
# Sam, 23 Oct 20:09: a silent story (no narration), music and sound effects carry it; beats.json (10 beats over 60 s) is
# the source of truth and will be re-timed to the phrases of the chosen recording. blender.py holds the ONE table that
# anchors every event to a beat (beat name, fraction u of the way through it); set_events() turns it into seconds here.
BEATS_JSON = json.load(open(os.path.join(HERE, 'beats.json')))
BEATS = [dict(name=b['name'], t0=float(b['t'][0]), t1=float(b['t'][1]), words=b.get('words', '')) for b in BEATS_JSON['beats']]
BEAT = {b['name']: b for b in BEATS}
DURATION = float(BEATS_JSON.get('duration', BEATS[-1]['t1']))
KEY_WORD = BEATS_JSON.get('key_word', 'FOSSIL')
TIMING_SOURCE = 'beats.json'


def bt(name, u=0.0):
    """Time u of the way through the beat called `name` (u below 0 or above 1 reaches before or after it)."""
    b = BEAT[name]; return b['t0'] + u * (b['t1'] - b['t0'])


class Beats:
    pass


B = Beats()
SLOTS = []
SLOT_ERAS = ['forest', 'ice', 'mammoth', 'grass', 'forest']     # what the world above looks like on each new layer


def set_events(table):
    """table: {event: (beat name, u)} -> B.<event> in seconds; then the derived times (the five layer slots)."""
    global SLOTS
    for k, (name, u) in table.items(): setattr(B, k, bt(name, u))
    a, b = B.stack0, B.stack1; n = 5; d = (b - a) / n
    SLOTS = [(a + i * d + 0.08 * d, a + i * d + 0.30 * d) for i in range(n)]      # water and mud in the first third, then the era shows


def slot_at(t):
    """Index of the layer slot whose stretch contains t (-1 before the first, 4 after the last)."""
    if not SLOTS or t < B.stack0: return -1
    d = (B.stack1 - B.stack0) / 5; return int(min(4, max(0, (t - B.stack0) // d)))


WORD_IN = {}     # beat name -> start time of its words, when the music wants them later than the beat (set by blender.py)


def word_windows():
    """(text, t_in, t_out) for each beat that has words: in with a soft pop after the beat starts (or at WORD_IN), out
    before it ends, never under 2.5 s on screen. The key word (FOSSIL!) is the label on the bone, the rest are captions."""
    out = []
    for b in BEATS:
        w = b['words'].strip()
        if not w: continue
        a = WORD_IN.get(b['name'], b['t0'] + 0.35); z = max(b['t1'] - 0.25, a + 2.5)
        out.append((w, a, min(z, DURATION)))
    return out


# ------------------------------------------------------------------ the top of the block in time
def base(t):
    """The level of the top (before the relief): today, the rewind (the ground above the old one peels away upward), the
    blanket and the layers up, then the wearing down to today."""
    t = float(t)
    if t < B.flood0:
        return Z_NOW if t < B.peel0 else Z_ANC
    if t < B.stack0:
        return keys(t, [(B.mud0, Z_ANC), (B.mud1, DEPOSITS[0])])
    if t < B.erode0:
        z = DEPOSITS[0]
        for i, (a, b) in enumerate(SLOTS):
            if t >= a: z = DEPOSITS[i] + (DEPOSITS[i + 1] - DEPOSITS[i]) * sm(a, b, t)
        return z
    return keys(t, [(B.erode0, Z_MAX), (B.erode1, Z_NOW)])

def era(t):
    """1 = today, 0 = the fern era and deep time (drives the background, the life and the colours)."""
    return keys(t, [(B.rw0, 1.0), (B.rw1, 0.0), (B.green0 - 0.4, 0.0), (B.green1, 1.0)])

def ancient(t):
    """1 while the fern forest stands (from the rewind until the mud covers it)."""
    return sm(B.fern0, B.fern1, t) * (1 - sm(B.mud0, B.mud0 + 0.6, t))


def today(t):
    """1 in today's world (the hook, and from the meadow's return to the end)."""
    return 1.0 - sm(B.rw0, B.peel0, t) if t < B.green0 else sm(B.green0, B.green1, t)

def flood_level(t):
    """Height of the flood water above the top's base (negative = no flood): line 4 and the five pulses of line 5."""
    lv = -1.0
    lv = max(lv, keys(t, [(B.flood0, -0.06), (B.flood1, 0.05), (B.flood2, 0.05), (B.flood3, -0.06)]) if B.flood0 - 0.5 < t < B.flood3 + 0.5 else -1.0)
    for a, b in SLOTS:
        if a - 0.3 < t < b + 0.3: lv = max(lv, keys(t, [(a - 0.12, -0.06), (a, 0.045), (b, 0.045), (b + 0.15, -0.06)]))
    return lv

# the river (ancient) and the brook (today) share one bed along the back, out through the right (+X) face
RIVER = np.array([(-10.0, 5.5), (-5.5, 2.6), (-2.6, 0.9), (-1.2, 0.30), (-0.3, -0.08), (0.5, -0.20), (1.15, -0.02), (1.45, 0.55),
                  (1.55, 1.3), (2.2, 2.6), (4.5, 4.5), (9.0, 6.5)])
# the river comes from far behind on the left, loops past the front of the block (where the dinosaur rests by it) and
# leaves through the back, on into the land behind

# ------------------------------------------------------------------ the world around the slice
# The slice was lifted out of a continuous land: the land carries on all round at its natural level and far behind (same
# relief, same ground colours, same eras); beyond the slice's far corner it curves gently away so a horizon shows.
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


# ------------------------------------------------------------------ the lifted slice (Sam 23 Oct: v3 framing)
# The block is a slice of land lifted out of the living world: its underside floats GAP above the land, directly over the
# hole it came from (the hole is HM wider than the slice all round, so its dark walls show). Everything on the slice is
# at slice height (top_h adds lift(t) inside the slice's footprint); the land around stays at its natural level.
GAP = 0.32                 # underside to land: about 0.3 of the slice's own height (1.05 m today)
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

def _seg_dist(P, x, y):
    d = np.full(np.shape(x), 1e9)
    for a, b in zip(P[:-1], P[1:]):
        ab = b - a; L2 = ab @ ab + 1e-12
        t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / L2, 0, 1)
        d = np.minimum(d, np.hypot(x - a[0] - t * ab[0], y - a[1] - t * ab[1]))
    return d

def river_d(x, y):
    return _seg_dist(RIVER, np.asarray(x, float), np.asarray(y, float))

def channel(t):
    """Width and depth of the water course: a wide river long ago, filled in by the layers, a brook today."""
    w = keys(t, [(B.rw0, 0.13), (B.rw1, 0.26), (B.mud0, 0.26), (B.mud1, 0.0), (B.green0, 0.0), (B.green1, 0.13)])
    d = keys(t, [(B.rw0, 0.045), (B.rw1, 0.075), (B.mud0, 0.075), (B.mud1, 0.0), (B.green0, 0.0), (B.green1, 0.045)])
    return w, d

def relief(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return 0.022 * fbm(x, y, 5, 3, 0.9) + 0.035 * smooth(-0.2, 1.1, y) * (0.6 + 0.4 * fbm(x, y, 9, 2, 0.6))

def hump(x, y):
    """The blanket over the sleeping dinosaur: a soft long mound along its body."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return np.exp(-(((x - DINO_LIE_X) / 0.60) ** 2) - (((y - DINO_Y + 0.04) / 0.24) ** 2))

ROCK_R = 0.42              # today: bare rock round the girl's find, where the land wore away down to the fossil's band


def rock_patch(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); r = np.hypot((x - DIG[0]) / 1.35, (y - DIG[1] + 0.16) / 1.0)
    return smooth(ROCK_R, ROCK_R * 0.65, r + 0.04 * fbm(x, y, 77, 2, 6.0))


def dent(t):
    """How far her brushing has cleared the rock face round the bone (0 to 1)."""
    return keys(t, [(B.pit0, 0.0), (B.pit1, 1.0)]) if t > B.pit0 else 0.0


def hollow(x, y, t):
    """Today: a small hollow in the meadow with a low rock face at its back, facing the viewer; the bone is in that face.
    Brushing pushes the face back round the bone (the bone appears out of the rock)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    yc = DIG[1] + 0.075 * dent(t) * np.exp(-((x - DIG[0]) / 0.13) ** 2)
    wx = smooth(0.44, 0.30, np.abs(x - DIG[0]))
    return wx * smooth(yc + 0.006, yc - 0.020, y) * smooth(DIG[1] - 0.46, DIG[1] - 0.30, y)


HOLLOW_D = 0.13


def top_h(x, y, t):
    """Height of the ground at (x, y) at time t. On the slice (its footprint, edges included): the story's top (base +
    relief + water course + blanket hump - today's hollow) lifted by lift(t). Around it: the land at its natural level
    (today's ground, the same relief and water course), curving away beyond the far corner."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    sl = in_slice(x, y)
    h = np.where(sl, slice_h(x, y, t) + lift(t), land_h(x, y, t))
    return h


def land_h(x, y, t):
    x = np.asarray(x, float); y = np.asarray(y, float); w, d = channel(t)
    h = Z_NOW + relief(x, y)
    if d > 1e-4: h = h - d * smooth(w + 0.06, max(w - 0.05, 0.0), river_d(x, y))
    return h - drop(x, y)


def slice_h(x, y, t):
    """The slice's own top in its own frame (before the lift)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    w, d = channel(t)
    h = base(t) + relief(x, y)
    if d > 1e-4:
        rd = river_d(x, y); h = h - d * smooth(w + 0.06, max(w - 0.05, 0.0), rd)
    hp = keys(t, [(B.mud0 + 0.15, 0.0), (B.mud1, 0.07), (B.hump1, 0.0)]) if B.mud0 < t < B.hump1 + 0.1 else 0.0
    if hp > 1e-4: h = h + hp * hump(x, y)
    td = today(t) if base(t) < Z_NOW + 0.02 else 0.0
    if td > 1e-3: h = h - HOLLOW_D * td * hollow(x, y, t)
    return h


def water_level(t):
    """The water surface on the slice (absolute z, lift included): the river or brook in its bed; the flood above it."""
    w, d = channel(t); f = flood_level(t)
    lv = base(t) - 0.012 - 0.5 * d if d > 1e-4 else -9.0
    if f > -0.9: lv = max(lv, base(t) + f + 0.02)
    return lv + lift(t)


def land_water(t):
    """The river's surface on the land around (before the curve away), or -9 when the layers have filled it."""
    w, d = channel(t)
    return Z_NOW - 0.012 - 0.5 * d if d > 1e-4 else -9.0

# ------------------------------------------------------------------ colours in time (the painted sky card and the light)
P_TODAY, P_FERN, P_EVE, P_DEEP = (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)
SLOT_MOOD = {'forest': P_FERN, 'ice': P_DEEP, 'mammoth': P_EVE, 'grass': P_TODAY}


def weights(t):
    """(spring, summer, autumn, winter) for Fable's sky card, the hills and the sun: spring = today, summer = the fern
    era, autumn = the evening of the rest (and the mammoth steppe), winter = rain, ice and the hush of deep time. In the
    rewind the sky runs back through days and seasons (soft blends, about two changes a second, no flashing)."""
    t = float(t)
    if B.rw0 < t < B.rw1:
        order = [P_TODAY, P_DEEP, P_EVE, P_FERN]; ph = (t - B.rw0) / (B.rw1 - B.rw0) * 6.0
        k = int(ph); f = ph - k; f = f * f * (3 - 2 * f)
        a = np.array(order[k % 4], float); b = np.array(order[(k + 1) % 4], float) if k < 5 else np.array(P_FERN, float)
        if k >= 6: return np.array(P_FERN, float)
        w = a + (b - a) * f; return w / w.sum()
    ks = [(0.0, P_TODAY), (B.rw0, P_TODAY), (B.rw1, P_FERN), (B.soft0, P_FERN), (B.soft1, P_EVE), (B.rainA0, P_EVE),
          (B.flood1, (0, 0, 0.35, 0.65))]
    d = (B.stack1 - B.stack0) / 5
    for i, e in enumerate(SLOT_ERAS): ks.append((B.stack0 + (i + 0.45) * d, SLOT_MOOD[e]))
    ks += [(B.lens0, P_DEEP), (B.rain1 - 0.6, P_DEEP), (B.green1, P_TODAY), (DURATION + 1, P_TODAY)]
    w = np.array(keys(t, [(a, tuple(float(x) for x in v)) for a, v in ks]), float)
    return w / max(w.sum(), 1e-6)


CURVES = {}

def cv(name, t):
    """Curves Fable asks for by name on a kit scene: no snow; canopies full."""
    if name == 'snow': return 0.0
    if name == 'dens': return 1.0
    raise KeyError(name)
