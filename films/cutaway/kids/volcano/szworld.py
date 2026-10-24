"""How is a volcano born? The island, the clock of beats and the moods (pure numpy, no bpy).

One block, one fixed view: a slice of a young volcano island lifted out of a sunny sea. The slice is cut through the
volcano's axis, so its front face is a textbook cross-section: layers of old lava, the dark crack (the vent's pipe), the
magma chamber glowing deep down. Magma rises in the crack (it is lighter than the rock), gas bubbles grow in it (a shaken
fizzy drink), it bursts out of the top and is lava, cools into new rock; each eruption adds a layer and the mountain grows;
plants find a home on the new rock and it slowly turns to soil; the islands of Hawaii were built this way.

The island's shape is ONE function of time, `h_now`: the island of the last eruption (`h_final`, a cone on a flat beach)
minus the layers that have not yet been laid, `off(t) * w` (thick under the summit, thin at the shore, nothing at the
beach). Each eruption (the first on the music's big entrance, the next eight on its eight orchestral hits) lays one layer
(`TH` thick at the summit) in 0.8 s. The cut face's colour bands follow the same shells (`sd_wall`), so every new layer is
a new band exactly where the new rock appears.

Times: beats.json (Sam 23 Oct 2026, a silent film; 11 beats over 72.3 s, timed to the music edit). blender.py holds the
one event table (beat, fraction) and calls set_events(); everything here reads the resulting B.<event> seconds.

Fable (films/styles/cutaway/art/fable.py) reads this module by its name `szworld`: weights(t) sets the painted sky card and
the sun, cv(name, t) answers its 'snow' and 'dens' questions.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24

# ------------------------------------------------------------------ the block (metres; z = 0 is the sea's surface)
SX, SY = 3.6, 2.2
HX, HY = SX / 2, SY / 2
ZB = -1.20                 # bottom of the block
Z_SEA = 0.0
SEABED = -0.30             # the sea floor beside the island
GAP = 0.32                 # underside to the sea: about a quarter of the slice's height
HM = 0.10                  # the hole (a column of sea) is this much wider than the slice on every side
HOLE_FLOOR = ZB

# ------------------------------------------------------------------ the island
XC, YC = -0.12, -HY        # the summit's axis lies ON the front face: the cut passes through the vent
KY = 0.62                  # the island is longer front to back than wide
RS = 1.10                  # shore radius
PEAK = 0.98                # summit height after the last layer
INIT = 0.40                # summit height before the first layer (a low young cone)
BEACH = 0.035              # the flat beach ring
CR_R, CR_D = 0.17, 0.075   # crater radius (on the axis' scale) and depth
N_LAYERS = 9               # nine layers (the first eruption and the eight hits)
OFF0 = PEAK - INIT         # what the nine layers add under the summit
TH = OFF0 / N_LAYERS       # each layer is TH thick at the summit


def smooth(a, b, x):
    u = np.clip((np.asarray(x, float) - a) / (b - a + 1e-12), 0.0, 1.0); return u * u * (3 - 2 * u)


def sm(a, b, x):
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
    """Keyframes [(time, value)] with smoothstep easing, held flat before the first and after the last."""
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
KEY_WORD = BEATS_JSON.get('key_word', 'MAGMA')
TIMING_SOURCE = 'beats.json'


def bt(name, u=0.0):
    b = BEAT[name]; return b['t0'] + u * (b['t1'] - b['t0'])


class Beats:
    pass


B = Beats()
ERUPT = []        # the nine eruption times (the first big one, then the eight hits)
STRENGTH = (1.0, 0.55, 0.55, 0.6, 0.6, 0.65, 0.65, 0.7, 1.3)     # fountain size of each eruption


def set_events(table):
    """table: {event: (beat name, u)} -> B.<event> in seconds; then the derived times (the nine eruptions)."""
    global ERUPT
    for k, (name, u) in table.items(): setattr(B, k, bt(name, u))
    ERUPT = [B.e0, B.e1, B.e2, B.e3, B.e4, B.e5, B.e6, B.e7, B.e8]


WORD_IN = {}


def word_windows():
    """(text, t_in, t_out) for each beat that has words: in with a soft pop after the beat starts (or at WORD_IN), out
    before it ends, never under 2.5 s on screen. The key word (MAGMA) is the label on the chamber, the rest are captions."""
    out = []
    for b in BEATS:
        w = b['words'].strip()
        if not w: continue
        a = WORD_IN.get(b['name'], b['t0'] + 0.35); z = max(b['t1'] - 0.25, a + 2.5)
        out.append((w, a, min(z, DURATION)))
    return out


# ------------------------------------------------------------------ the island's shape in time
def rr(x, y):
    return np.hypot(np.asarray(x, float) - XC, (np.asarray(y, float) - YC) * KY)


def h_final(x, y):
    """The island after the ninth layer: a cone (a little concave) on a flat beach ring, a crater, then the sea floor."""
    r = rr(x, y); u = np.clip(1 - r / RS, 0, 1)
    cone = BEACH + (PEAK - BEACH) * u ** 1.7
    cone = cone + 0.018 * fbm(x * 3.0, y * 3.0, 4, 2, 1.0) * u              # a little roughness on the flanks
    bowl = smooth(CR_R, CR_R * 0.25, r)                                      # 1 in the crater's middle, 0 at its rim
    cone = cone - CR_D * bowl + 0.02 * smooth(CR_R * 0.7, CR_R * 1.15, r) * smooth(CR_R * 2.2, CR_R * 1.15, r)    # a low rim
    sea = BEACH + (SEABED - BEACH) * smooth(0.0, 0.42, r - RS)
    return np.where(r <= RS, cone, sea)


def wgt(x, y):
    """How much of a layer's thickness a point gets: all of it under the summit, none at the shore. It is the share of
    the island's growth (the final cone minus the first, low cone) at that point, so the first island is a low cone."""
    u = np.clip(1 - rr(x, y) / RS, 0, 1)
    return ((PEAK - BEACH) * u ** 1.7 - (INIT - BEACH) * u ** 2.2) / OFF0


def inside(x, y):
    return smooth(RS + 0.03, RS - 0.03, rr(x, y))


def progress(t):
    """Layers laid by time t (0 to 9), each in 0.8 s from its eruption."""
    return sum(sm(e, e + 0.8, t) for e in ERUPT)


def off(t):
    return TH * (N_LAYERS - progress(t))


def h_now(x, y, t):
    """The island's own top in its own frame (before the lift): the final cone minus the layers not yet laid, never below the beach."""
    hf = h_final(x, y); ins = inside(x, y)
    return np.where(ins > 0.001, np.maximum(hf - off(t) * wgt(x, y) * ins, np.minimum(hf, BEACH)), hf)


def crater_floor(t):
    return float(h_now(np.array([XC]), np.array([YC + 0.001]), t)[0])


def sd_wall(x, y, z):
    """Depth in 'layers' below the surface for the cut face's colour bands (Fable's `sd`): shells of the final island,
    stretched by the layer weight, so a new layer is a new band exactly where the new rock appears."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    hf = h_final(x, y); w = np.maximum(wgt(x, y), 0.12); zc = hf - OFF0 * w
    return np.where(z >= zc, (hf - z) / w, OFF0 + (zc - z))


# the colour bands, newest first: nine lava and ash layers (Fable paints these names), then the old sea-floor rock
STRATA = [('rust', TH, (0.72, 0.26, 0.27), 0.0), ('topsoil', TH, (0.34, 0.14, 0.26), 0.0), ('ochre', TH, (0.96, 0.74, 0.30), 0.0),
          ('topsoil', TH, (0.34, 0.14, 0.26), 0.0), ('rust', TH, (0.72, 0.26, 0.27), 0.0), ('topsoil', TH, (0.34, 0.14, 0.26), 0.0),
          ('ochre', TH, (0.96, 0.74, 0.30), 0.0), ('topsoil', TH, (0.34, 0.14, 0.26), 0.0), ('rust', TH, (0.72, 0.26, 0.27), 0.0),
          ('loam', 0.10, (0.72, 0.26, 0.27), 0.0), ('topsoil', 0.12, (0.34, 0.14, 0.26), 0.0), ('clay', 0.08, (0.95, 0.47, 0.38), 0.0),
          ('topsoil', 0.16, (0.34, 0.14, 0.26), 0.0), ('rock', 0.30, (0.12, 0.30, 0.40), 0.10), ('deep', 1.0, (0.07, 0.10, 0.25), 0.05)]

# ------------------------------------------------------------------ the lifted slice
def shake(t):
    """A gentle rumble of the whole slice: rising with the gas, a little jolt at each eruption (a few millimetres)."""
    t = float(t); a = 0.0
    a = max(a, 0.0075 * sm(B.rumble0, B.rumble1, t) * (1 - sm(B.e0, B.e0 + 0.3, t)))
    for e, s in zip(ERUPT, STRENGTH):
        if e <= t < e + 1.1: a = max(a, 0.009 * s * (1 - (t - e) / 1.1))
    return a * math.sin(2 * math.pi * 13.0 * t) + 0.4 * a * math.sin(2 * math.pi * 7.3 * t + 1.0)


def lift(t):
    """How high the slice floats: its full depth plus the gap, bobbing a few centimetres on a slow sine, rumbling."""
    return -ZB + GAP + 0.022 * math.sin(2 * math.pi * float(t) / 7.5) + shake(t)


def in_slice(x, y):
    return (np.abs(np.asarray(x, float)) <= HX + 1e-6) & (np.abs(np.asarray(y, float)) <= HY + 1e-6)


def in_hole(x, y):
    return (np.abs(np.asarray(x, float)) < HX + HM - 1e-6) & (np.abs(np.asarray(y, float)) < HY + HM - 1e-6)


def in_block(x, y):
    return (np.abs(np.asarray(x)) < HX) & (np.abs(np.asarray(y)) < HY)


# ------------------------------------------------------------------ the world around: sea, curve away, other islands
VIEW_AZ = -62.0
DROP_R = 6.0
_FH = np.array([-math.cos(math.radians(VIEW_AZ)), -math.sin(math.radians(VIEW_AZ))])
_S0 = float(max(np.array([(x, y) for x in (-HX, HX) for y in (-HY, HY)]) @ _FH))
RIGHT = np.array([-math.sin(math.radians(VIEW_AZ)), math.cos(math.radians(VIEW_AZ))])


def depth_s(x, y):
    return np.asarray(x, float) * _FH[0] + np.asarray(y, float) * _FH[1]


def drop(x, y):
    s = np.maximum(depth_s(x, y) - _S0, 0.0); return s * s / (2 * DROP_R)


def at_screen(s, d):
    """World (x, y) of the point s to the right of the block's centre on screen and d behind it."""
    return RIGHT * s + _FH * d


# the older islands around (screen offset s, depth d, radius, height, kind): green, rounder and lower than the young one
NEAR_ISLANDS = [(-3.5, 1.6, 1.35, 0.55, 'hill'), (3.6, 2.4, 1.5, 0.70, 'hill'), (0.8, 4.4, 2.1, 1.00, 'volcano')]
NEAR_C = [(*at_screen(s, d), r, h, k) for s, d, r, h, k in NEAR_ISLANDS]


def island_bump(x, y):
    """Heights above the sea of the near older islands (a rounded, green hill with a sandy beach ring)."""
    h = np.zeros(np.shape(x))
    for cx, cy, r, ht, kind in NEAR_C:
        d = np.hypot(np.asarray(x, float) - cx, np.asarray(y, float) - cy) / r
        d = d + 0.10 * fbm(np.asarray(x, float) * 1.2, np.asarray(y, float) * 1.2, 31, 2, 1.0)
        u = np.clip(1 - d, 0, 1); b = BEACH + ht * u ** 1.6
        if kind == 'volcano': b = b - 0.10 * smooth(0.16, 0.04, d)          # an old, sleeping crater
        sea = BEACH + (SEABED - BEACH) * smooth(0.0, 0.30, d - 1.0)
        h = np.maximum(h, np.where(d <= 1.0, b, sea))
    return np.where(np.abs(h) < 1e-9, SEABED, h)


def land_h(x, y, t=0.0):
    """The world's solid ground around the slice (sea floor and the older islands), standing on the curved sea."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return island_bump(x, y) - drop(x, y)


def sea_h(x, y, t):
    """The sea's surface around the slice: flat, curving away, a slow swell."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return Z_SEA - drop(x, y) + 0.006 * np.sin(1.3 * x + 0.9 * y + 0.8 * t)


def top_h(x, y, t):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return np.where(in_slice(x, y), h_now(x, y, t) + lift(t), land_h(x, y, t))


# ------------------------------------------------------------------ the pipe, the chamber (cut face, slice frame)
CH_Z, CH_A, CH_B = -0.80, 0.56, 0.17      # the magma chamber: centre height, half width, half height
PIPE_W = 0.052                             # half width of the crack
PIPE_Z0 = CH_Z + CH_B * 0.80


def pipe_x(z):
    """The crack's path up from the chamber (a gentle zig-zag, a crack not a pipe)."""
    z = np.asarray(z, float); return XC + 0.050 * np.sin(8.5 * z + 0.6) * smooth(-0.9, -0.55, z) + 0.022 * np.sin(23.0 * z)


def pipe_top(t):
    return crater_floor(t) - 0.004


def magma_level(t):
    """The magma front in the crack (z, slice frame): sinks back to the chamber's top in the very start, rises (it is lighter
    than the rock round it) through the 'rises' beat, climbs on in the 'gas' beat to the crater, spills at the eruption and
    drains back to the vent as the lava flows away."""
    t = float(t); lo, hi = PIPE_Z0 + 0.02, pipe_top(t)
    u = keys(t, [(B.rise0, 0.0), (B.rise1, 0.52), (B.gas1, 1.0)])
    drain = keys(t, [(B.e0 + 0.4, 0.0), (B.e0 + 3.5, 0.30)])
    if t > B.e0: u = 1.0 - drain
    if t > B.e0 + 3.5:       # each later eruption refills the pipe quickly and falls back again
        u = 0.70
        for e in ERUPT[1:]:
            u = max(u, 0.70 + 0.30 * sm(e - 0.5, e + 0.1, t) * (1 - sm(e + 0.9, e + 2.4, t)))
        u = u - 0.40 * sm(ERUPT[-1] + 2.5, ERUPT[-1] + 7.0, t)      # the last eruption is over: the magma sinks, the pipe cools
    return lo + (hi - lo) * u


def gas_amount(t):
    """0 to 1: how much gas has come out of the magma (the bubbles grow as the magma rises, like a shaken drink)."""
    return keys(t, [(B.gas0, 0.0), (B.gas1, 1.0)]) * (1 - sm(B.e0 + 0.1, B.e0 + 1.2, t))


# ------------------------------------------------------------------ lava flows (paths on the island, in the slice frame)
# angle (degrees from +x, counter-clockwise seen from above), length in the island's own metric, wiggle phase
FLOWS = [(172, 1.10, 0.0), (6, 1.10, 1.3), (128, 1.05, 2.1), (50, 1.05, 0.7), (186, 1.05, 3.0), (352, 1.05, 4.1), (150, 1.00, 5.2), (28, 1.00, 2.6), (8, 1.1, 0.4)]
FLOW_OF = (0, 1, 2, 3, 4, 5, 6, 7, 8)         # eruption j sends flow FLOW_OF[j]; the first and the last also send a second one
FLOW_EXTRA = {0: 1, 8: 3}
FLOW_DUR = 5.0                                  # seconds for a flow to reach the shore
FLOW_COOL = 4.5


def flow_path(k, n=40):
    """Points (x, y) of flow k from the crater's lip to the shore: straight down the slope with a lazy meander."""
    ang, ln, ph = FLOWS[k]; a = math.radians(ang); u = np.linspace(0, 1, n)
    r = CR_R * 0.9 + u * (RS * 0.98 - CR_R * 0.9)
    wig = 0.07 * np.sin(5.0 * u + ph) * np.sin(math.pi * u)
    ca, sa = np.cos(a + wig), np.sin(a + wig)
    x = XC + r * ca; y = YC + np.abs(r * sa) / KY * 0.999 + 0.02       # y reaches the elliptical shore; stays behind the face
    return np.column_stack([x, y])


# ------------------------------------------------------------------ light and sky
P_DAY, P_BRIGHT, P_WARM, P_SOFT = (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)


def weights(t):
    """(spring, summer, autumn, winter) for Fable's sky card, the hills and the sun: a bright day, the sky warms with each
    eruption (peach and gold), clears in the calm and ends in a soft clear light."""
    t = float(t)
    w = np.array(P_DAY, float) * 0.55 + np.array(P_BRIGHT, float) * 0.45
    warm = 0.0
    for e, s in zip(ERUPT, STRENGTH):
        warm = max(warm, 0.55 * s * sm(e - 0.2, e + 0.6, t) * (1 - sm(e + 1.6, e + 5.0, t)))
    warm = max(warm, 0.18 * sm(B.gas0, B.gas1, t) * (1 - sm(B.e0, B.e0 + 1.0, t)))
    w = w * (1 - warm) + np.array(P_WARM, float) * warm
    calm = sm(B.rest0, B.rest0 + 4.0, t)
    w = w * (1 - 0.35 * calm) + np.array(P_SOFT, float) * 0.35 * calm
    return w / max(w.sum(), 1e-6)


def cv(name, t):
    if name == 'snow': return 0.0
    if name == 'dens': return 1.0
    raise KeyError(name)
