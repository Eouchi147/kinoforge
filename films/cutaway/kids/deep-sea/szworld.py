"""What lives in the deep sea? The clock of beats, the column's measures and the submarine's path (pure numpy, no bpy).

One lifted slice: a tall column of ocean (sunlight zone, twilight zone, midnight zone, the seafloor with a hot vent) floating
a little above the hole it was lifted from in a sunny sea that carries on to the horizon. The little submarine's descent is
the thread of the film. Every height, colour and amount is a pure function of t (seconds), so any frame renders alone.

Times: beats.json (a silent film, 11 beats over 70.5 s, timed to the Hebrides edit). blender.py holds the one event table
(beat, fraction) and calls set_events(); everything here reads the resulting B.<event> seconds.

Fable (films/styles/cutaway/art/fable.py) reads this module by its name `szworld`: weights(t) sets the painted sky card
(spring weight = bright day, autumn weight = golden evening) and cv(name, t) answers its 'snow' and 'dens' questions.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24

# ------------------------------------------------------------------ the slice (metres)
SX, SY = 2.4, 1.3          # the slice's width (x, the long front face) and depth (y)
HX, HY = SX / 2, SY / 2
DEEP = 2.9                 # the water: from the sea surface (z = 0 in the slice's frame) down to the seafloor's top
BASE = 0.46                # the seafloor's strata under it (the cut faces)
ZB = -(DEEP + BASE)        # bottom of the slice
GAP = 0.34                 # the slice floats this far above the sea it was lifted from
HM = 0.10                  # the hole is this much wider than the slice on every side
LIFT0 = -ZB + GAP          # slice frame -> world
HOLE_FLOOR = -(DEEP + BASE)
# zone tops (depth below the surface, m): sunlight, twilight, midnight, then the seafloor
ZONES = [0.0, 0.84, 1.70, DEEP]
ZONE_NAMES = ['sunlight', 'twilight', 'midnight']
VIEW_AZ = -62.0            # the camera's azimuth; screen-right is (0.883, 0.469) on the ground, away is (-0.469, 0.883)
_a = math.radians(VIEW_AZ)
RIGHT = np.array([-math.sin(_a), math.cos(_a)])      # screen right on the ground
AWAY = np.array([-math.cos(_a), -math.sin(_a)])      # away from the camera on the ground


def world_xy(a, b):
    """Ground point a metres to the screen right and b metres away from the camera, from the slice's centre."""
    return RIGHT * a + AWAY * b


# ------------------------------------------------------------------ small maths
def smooth(a, b, x):
    u = np.clip((np.asarray(x, float) - a) / (b - a + 1e-12), 0.0, 1.0); return u * u * (3 - 2 * u)

def sm(a, b, x):
    """Scalar smoothstep (float)."""
    return float(smooth(a, b, x))

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

def lin_keys(t, ks):
    """Keyframes with straight lines between them (for paths that must not stop at every key)."""
    ks = sorted(ks, key=lambda k: k[0]); t = float(t)
    if t <= ks[0][0]: return ks[0][1]
    for (a, va), (b, vb) in zip(ks, ks[1:]):
        if t < b:
            u = (t - a) / max(b - a, 1e-9); return va + (vb - va) * u
    return ks[-1][1]

def spline_keys(t, ks):
    """Smooth path through keys (Catmull-Rom on values), continuous speed: for the submarine and the creatures."""
    ks = sorted(ks, key=lambda k: k[0]); T = [k[0] for k in ks]; V = [np.asarray(k[1], float) for k in ks]; t = float(t)
    if t <= T[0]: return V[0]
    if t >= T[-1]: return V[-1]
    i = max(0, min(len(T) - 2, int(np.searchsorted(T, t, 'right') - 1)))
    u = (t - T[i]) / (T[i + 1] - T[i])
    p0 = V[max(0, i - 1)]; p1 = V[i]; p2 = V[i + 1]; p3 = V[min(len(V) - 1, i + 2)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)

def win(t, a, b, r=0.3):
    """1 inside [a, b] with eased edges of r seconds, 0 outside."""
    return sm(a, a + r, t) * (1 - sm(b - r, b, t))

def pulse(t, a, b):
    """0 outside [a, b], a smooth bump (sine) inside."""
    return math.sin(math.pi * min(1.0, max(0.0, (t - a) / max(b - a, 1e-9)))) ** 1.0

# ------------------------------------------------------------------ the story clock: beats.json + the event table
BEATS_JSON = json.load(open(os.path.join(HERE, 'beats.json')))
BEATS = [dict(name=b['name'], t0=float(b['t'][0]), t1=float(b['t'][1]), words=b.get('words', '')) for b in BEATS_JSON['beats']]
BEAT = {b['name']: b for b in BEATS}
DURATION = float(BEATS_JSON.get('duration', BEATS[-1]['t1']))
KEY_WORD = BEATS_JSON.get('key_word', 'GLOW')
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
    before it ends, never under 2.5 s on screen. The key word (GLOW!) is the label on the first jellyfish, the rest are captions."""
    out = []
    for b in BEATS:
        w = b['words'].strip()
        if not w: continue
        a = WORD_IN.get(b['name'], b['t0'] + 0.35); z = max(b['t1'] - 0.25, a + 2.5)
        out.append((w, a, min(z, DURATION)))
    return out


# ------------------------------------------------------------------ the slice floats and bobs
def lift(t):
    """Slice frame -> world height: a slow bob (2.5 cm on a 7.5 s sine, as on the other films)."""
    return LIFT0 + 0.025 * math.sin(2 * math.pi * t / 7.5)


def zone_of(d):
    return 0 if d < ZONES[1] else 1 if d < ZONES[2] else 2


# ------------------------------------------------------------------ the thread: the little submarine's path
# depth below the surface (m) at the keys; the path is eased, with the dwell times the story wants.
def sub_depth(t):
    return keys(t, [(0.0, 0.12), (4.9, 0.12), (6.1, 0.34), (9.0, 0.52), (13.0, 0.80), (16.0, 1.00), (19.0, 1.30), (22.0, 1.78),
                    (26.0, 1.92), (33.0, 2.06), (39.0, 2.12), (45.5, 2.12), (49.0, 2.40), (52.5, 2.60), (55.5, 2.60),
                    (59.4, 2.60), (61.0, 2.40), (63.0, 1.55), (64.8, 0.72), (65.9, -0.02), (70.5, -0.04)])


def sub_x(t):
    """Left-right in the slice (m): from the middle to the left, a gentle slalom, the vent, then the rise on the right."""
    return keys(t, [(0.0, 0.05), (5.0, 0.05), (9.0, -0.30), (14.0, 0.10), (20.0, -0.35), (26.0, -0.20), (33.0, 0.20), (39.0, 0.0),
                    (41.5, -0.10), (46.0, -0.10), (50.0, -0.30), (52.5, -0.50), (54.0, -0.52), (60.0, -0.52), (63.0, 0.30), (66.0, 0.30), (70.5, 0.30)])


def sub_y(t):
    return keys(t, [(0.0, -0.05), (20.0, -0.12), (40.0, -0.16), (55.0, -0.10), (66.0, -0.05)])


def sub_pitch(t):
    """Nose pitch (rad, positive = nose down): tips in to dive, level in the zones, nose up to leave."""
    return (0.38 * win(t, 5.0, 7.4, 0.7) + 0.10 * win(t, 7.4, 22.0, 2.5) + 0.20 * win(t, 47.0, 53.0, 1.2)
            - 0.34 * win(t, 60.0, 65.0, 1.0) - 0.0 * t)


# ------------------------------------------------------------------ the sky's weights for Fable's painted card
def weights(t):
    """(spring, summer, autumn, winter): bright day, then the golden evening of the calm ending."""
    e = sm(64.0, 70.0, t)
    if os.environ.get('KF_WT'):
        a, b, c, d = [float(v) for v in os.environ['KF_WT'].split(',')]; return (1.0 - e + e * a, e * b, e * c, e * d)
    return (1.0 - e, 0.0, e, 0.0)


def cv(name, t):
    return 0.0 if name == 'snow' else 1.0
