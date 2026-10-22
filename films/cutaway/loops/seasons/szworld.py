"""Four seasons loop: the land, the pond and the timeline (pure numpy, no bpy).

The loop closes because the year closes: every season curve is periodic over 12 s (spring at the seam on both sides),
every motion repeats on the loop (kit.Kit(loop=12)), and the camera only sways a few degrees on a 12 s sine. So the
world can be natural and asymmetric: one pond cut open on the front (-Y) face, a stream feeding it from the back, mounds.
"""
import math
import numpy as np

LOOP = 12.0
S = 3.2                  # block size (m)
H = S / 2
DEPTH = 1.25
LV = -0.05               # water level
FPS = 24

# ------------------------------------------------------------------ small maths
def smooth(a, b, x):
    u = np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0); return u * u * (3 - 2 * u)

def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0); return b * (1 - h) + a * h - k * h * (1 - h)

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

# ------------------------------------------------------------------ pond and land
POND_C, POND_R = (0.22, -1.32), (0.88, 0.68)          # centre past nothing: the -Y face (y = -1.5) cuts it open
STREAM = [(-0.95, 2.2), (-0.85, 1.25), (-0.30, 0.55), (-0.32, -0.15), (0.05, -0.75)]

def _seg_dist(P, x, y):
    d = np.full(np.shape(x), 1e9)
    for a, b in zip(P[:-1], P[1:]):
        ab = b - a; L2 = ab @ ab + 1e-12
        t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / L2, 0, 1)
        d = np.minimum(d, np.hypot(x - a[0] - t * ab[0], y - a[1] - t * ab[1]))
    return d

def _catmull(points, n):
    P = np.asarray(points, float); m = len(P); P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]]); out = []
    for k in range(n):
        s = k / (n - 1) * (m - 1); i = min(int(s), m - 2); u = s - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out.append(0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    return np.array(out)

_SP = _catmull(STREAM, 60)

def pond_sd(x, y):
    """Signed distance to the water (negative inside): an oval pond against the front face, a stream from the back."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    q = np.hypot((x - POND_C[0]) / POND_R[0], (y - POND_C[1]) / POND_R[1]); ang = np.arctan2(y - POND_C[1], x - POND_C[0])
    dp = (q - 1 + 0.06 * np.sin(3 * ang + 1.0) + 0.04 * np.sin(5 * ang + 2.0)) * min(POND_R)
    t = np.clip((y + 0.8) / 2.8, 0, 1); w = 0.13 + 0.05 * np.sin(4 * t)              # the stream narrows upstream
    ds = _seg_dist(_SP, x, y) - w
    return smin(dp, ds, 0.18) + 0.03 * fbm(x, y, 21, 3, 2.2)

def land_h(x, y):
    """Dry land: a hill in the back right, a low rise back left, gentle rolling."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    hill = 0.20 * np.exp(-((x - 1.0) ** 2 + (y - 0.95) ** 2) / 0.55) + 0.10 * np.exp(-((x + 1.05) ** 2 + (y - 0.6) ** 2) / 0.35)
    return 0.035 + hill + 0.035 * fbm(x, y, 5, 3, 1.4)

def field(x, y):
    """h (top height), sd (signed distance to the water), wg (grass), ws (sand), depth below the water level."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    h = land_h(x, y); sd = pond_sd(x, y)
    r = np.hypot((x - POND_C[0]) / POND_R[0], (y - POND_C[1]) / POND_R[1])
    D = 0.16 + 0.24 * smooth(1.6, 0.4, r)          # the stream is shallow, the pond deep
    bed = LV - 0.02 - D * smooth(0, 0.30, -sd) * (0.93 + 0.07 * fbm(x, y, 9, 3, 3.0))
    bank = LV + 0.012 + 0.55 * np.maximum(sd, 0)
    target = np.where(sd < 0, bed, bank)
    k2 = 0.03; hmin = np.minimum(h, target); hh = h - target
    h = np.where(np.abs(hh) < k2, hmin - (k2 - np.abs(hh)) ** 2 / (4 * k2), hmin)
    depth = LV - h
    near = smooth(0.09, 0.0, sd)
    ws = np.where(depth > 0, 1.0, near)
    dry = 0.5 + 0.5 * fbm(x, y, 41, 3, 1.3)
    wg = np.clip(1 - ws, 0, 1) * smooth(0.12, 0.3, dry + 0.25)
    return {'h': h, 'sd': sd, 'wg': wg, 'ws': ws, 'depth': depth}

def H_at(x, y):
    return field(np.asarray([x], float), np.asarray([y], float))['h'][0]

# ------------------------------------------------------------------ the year (t in seconds, periodic over LOOP)
def kc(t, keys):
    """Periodic keyframes [(time, value)] with smoothstep easing between neighbours (wraps from the last to the first)."""
    t = float(t) % LOOP; ks = sorted(keys)
    ext = [(a - LOOP, v) for a, v in ks] + ks + [(a + LOOP, v) for a, v in ks]
    for (a, va), (b, vb) in zip(ext, ext[1:]):
        if a <= t < b:
            u = (t - a) / (b - a); u = u * u * (3 - 2 * u)
            if isinstance(va, (tuple, list)): return tuple(p + (q - p) * u for p, q in zip(va, vb))
            return va + (vb - va) * u
    return ks[0][1]

def weights(t):
    """Colour weights of spring, summer, autumn, winter (they sum to 1)."""
    w = np.array([kc(t, [(0.6, 1), (2.6, 1), (3.6, 0), (11.2, 0)]), kc(t, [(2.6, 0), (3.6, 1), (5.8, 1), (6.6, 0)]),
                  kc(t, [(5.8, 0), (6.6, 1), (8.8, 1), (9.6, 0)]), kc(t, [(0.6, 0), (8.8, 0), (9.6, 1), (11.2, 1)])])
    return w / w.sum()

def blend(t, vals):
    """vals = (spring, summer, autumn, winter): numbers or tuples; returns the weighted mix at t."""
    w = weights(t); a = [np.asarray(v, float) for v in vals]
    out = sum(wi * ai for wi, ai in zip(w, a))
    return tuple(float(v) for v in np.atleast_1d(out)) if np.ndim(out) else float(out)

def win(t, a, b, r=0.4):
    """Periodic window: 0 outside [a, b] (mod LOOP), easing up over r after a and down over r before b. Vectorised."""
    t = np.asarray(t, float); a = np.asarray(a, float); b = np.asarray(b, float)
    L = (b - a) % LOOP; u = (t - a) % LOOP
    v = smooth(0, r, u) * (1 - smooth(L - r, L, u))
    return np.where(u <= L, v, 0.0)

CURVES = {
    'snow':   [(9.3, 0.0), (10.5, 1.0), (11.15, 1.0), (11.85, 0.0)],          # snow cover on the ground
    'ice':    [(9.5, 0.0), (10.65, 1.0), (11.2, 1.0), (11.9, 0.0)],          # freeze front from the edges inwards
    'wet':    [(11.1, 0.0), (11.8, 1.0), (0.8, 1.0), (1.9, 0.0)],            # meltwater darkening
    'dens':   [(11.5, 0.10), (2.3, 1.0), (6.3, 1.0), (8.7, 0.10)],           # deciduous canopy density
    'bloss':  [(11.7, 0.0), (0.7, 1.0), (2.3, 1.0), (3.3, 0.0)],             # blossom on the trees
    'grassh': [(11.4, 0.55), (2.2, 1.0), (6.6, 1.0), (9.2, 0.82), (10.2, 0.55)],
    'litter': [(6.6, 0.0), (8.8, 1.0), (9.6, 1.0), (10.4, 0.0)],             # leaf litter on the grass (snow covers it)
    'roots':  [(11.8, 0.80), (2.6, 1.0), (8.0, 1.0), (10.6, 0.80)],          # fine roots grow in spring, die back in winter
    'caus':   [(0.0, 0.8), (4.5, 1.15), (7.5, 0.7), (9.6, 0.5), (10.6, 0.15), (11.6, 0.35)],
    'burrow': [(7.95, 0.0), (8.5, 1.0), (0.45, 1.0), (1.25, 0.0)],           # the frog's chamber in the cut face
    'tunnel': [(7.75, 0.0), (8.0, 1.0), (8.75, 1.0), (9.0, 0.0), (11.55, 0.0), (11.75, 1.0), (0.5, 1.0), (0.75, 0.0)],
    'birds':  [(6.2, 1.0), (8.0, 0.0), (10.7, 0.0), (11.95, 1.0)],          # birds leave in autumn, return with the thaw
}

def cv(name, t): return kc(t, CURVES[name])
