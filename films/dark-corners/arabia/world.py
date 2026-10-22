"""World of the Arabia film: sand-clay terrain (analytic height field, coarse + fine tiles), painted card sky with pin-hole stars,
a clay moon, cut-card far dunes, lights. Metres, +Y away from the main camera, +Z up."""
import math
import numpy as np
from kit import *

# ----------------------------------------------------------------------------------------------- places (world coords)
TENT1 = (1.30, 1.55)         # the old man's tent (open front, lamp inside)
TENT2 = (2.50, 1.80)         # the woman's tent (closed, glowing cloth)
PADS = [  # (x, y, inner radius, outer radius): flattened clay where puppets and props stand
    (TENT1[0], TENT1[1], 0.30, 0.62), (TENT2[0], TENT2[1], 0.30, 0.62), (1.7, 0.85, 0.32, 0.66), (0.35, 0.85, 0.30, 0.6),
    (-1.0, 2.3, 0.22, 0.5), (-2.1, 1.1, 0.35, 0.8), (0.0, 0.0, 0.35, 0.8), (0.9, 0.25, 0.35, 0.8),
]
TRACK_PTS = [(-3.9, 3.05), (-3.0, 2.75), (-2.2, 2.55), (-1.4, 2.10), (-0.6, 2.05), (0.2, 1.65), (0.75, 1.15), (1.1, 0.95)]
MECCA_X = 9.0

def _sines(seed, n, kmin, kmax, amp0):
    rs = np.random.RandomState(seed); out = []
    for i in range(n):
        k = rs.uniform(kmin, kmax); a = rs.uniform(0, 2 * math.pi)
        out.append((amp0 * rs.uniform(0.5, 1.0) / (1 + 0.3 * i), k * math.cos(a), k * math.sin(a), rs.uniform(0, 2 * math.pi)))
    return out
_LOW = _sines(5, 7, 1.2, 3.8, 0.02)

def base_h(x, y):
    w = 0.30 * np.sin(1.1 * x + 0.8 * y + 0.7) + 0.16 * np.sin(2.7 * x - 1.9 * y + 2.1)
    a = math.radians(-18); k = 2 * math.pi / 1.45
    u = (x * math.cos(a) + y * math.sin(a)) * k + w * 2.0
    s = np.sin(u) + 0.32 * np.sin(2 * u + 0.9)
    h = 0.040 * s
    for (am, kx, ky, ph) in _LOW: h = h + am * np.sin(kx * x + ky * y + ph)
    # the far edge rises into a big dune wall that hides the foot of the sky card
    h = h + 0.30 * smoothv(3.5, 4.6, y) * (0.75 + 0.25 * np.sin(1.3 * x + 0.4))
    # front edge drops a little so the camera can sit low
    return h

def smoothv(a, b, x):
    u = np.clip((x - a) / (b - a), 0.0, 1.0); return u * u * (3 - 2 * u)

def terrain_h(x, y):
    h = base_h(x, y)
    for (px, py, r0, r1) in PADS:
        d = np.sqrt((x - px) ** 2 + ((y - py) * 1.15) ** 2); w = 1.0 - smoothv(r0, r1, d)
        hc = float(base_h(np.array(px), np.array(py)))
        h = h * (1 - w) + (hc * 0.5) * w
    return h

# ----------------------------------------------------------------------------------------------- tracks
def spline_pts(pts, step):
    P = np.array(pts, float); n = max(4, int(sum(np.linalg.norm(P[1:] - P[:-1], axis=1)) / step * 3))
    C = catmull(P, n); seg = np.linalg.norm(C[1:] - C[:-1], axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    return C, s

def camel_prints(pts, lateral, stride, phase=0.0, a=0.013, b=0.010):
    """Alternating left/right pad prints along a path -> [(x, y, dir_x, dir_y, a, b)]."""
    C, s = spline_pts(pts, 0.01); out = []
    for side in (-1, 1):
        d = phase + (0.0 if side < 0 else stride / 2)
        while d < s[-1] - 0.05:
            i = int(np.searchsorted(s, d)); i = min(i, len(C) - 2)
            t = C[i + 1] - C[i]; t /= np.linalg.norm(t); n = np.array([-t[1], t[0]])
            p = C[i] + n * lateral * side
            out.append((p[0], p[1], t[0], t[1], a, b)); d += stride
    return out

def build_prints():
    pr = []
    pr += camel_prints([(x, y - 0.00) for x, y in TRACK_PTS], 0.020, 0.085, 0.0)
    pr += camel_prints([(x + 0.0, y + 0.075) for x, y in TRACK_PTS], 0.019, 0.083, 0.03)
    return pr
PRINTS = build_prints()

def apply_prints(X, Y, H):
    """Add the dents to a regular grid (X, Y 1-D axes); slices a local window per print."""
    x0, y0 = X[0], Y[0]; dx = X[1] - X[0]; dy = Y[1] - Y[0]
    for (px, py, tx, ty, a, b) in PRINTS:
        R = 1.5 * max(a, b) + 0.01
        i0 = int(math.floor((px - R - x0) / dx)); i1 = int(math.ceil((px + R - x0) / dx)); j0 = int(math.floor((py - R - y0) / dy)); j1 = int(math.ceil((py + R - y0) / dy))
        if i1 < 0 or j1 < 0 or i0 >= len(X) or j0 >= len(Y): continue
        i0, j0 = max(i0, 0), max(j0, 0); i1, j1 = min(i1, len(X) - 1), min(j1, len(Y) - 1)
        gx, gy = np.meshgrid(X[i0:i1 + 1], Y[j0:j1 + 1], indexing='ij')
        u = (gx - px) * tx + (gy - py) * ty; v = -(gx - px) * ty + (gy - py) * tx
        r2 = (u / a) ** 2 + (v / b) ** 2
        dent = np.where(r2 < 1.0, (1 - r2) ** 1.5, 0.0) * -0.0042 + 0.0011 * np.exp(-((np.sqrt(r2) - 1.25) / 0.3) ** 2)
        H[i0:i1 + 1, j0:j1 + 1] += dent

def grid_mesh(X, Y, H, cell_mask=None):
    nx, ny = len(X), len(Y)
    gx, gy = np.meshgrid(X, Y, indexing='ij')
    V = np.stack([gx, gy, H], -1).reshape(-1, 3)
    idx = np.arange(nx * ny).reshape(nx, ny)
    a = idx[:-1, :-1]; b = idx[1:, :-1]; c = idx[1:, 1:]; d = idx[:-1, 1:]
    F = np.stack([a, b, c, d], -1)
    if cell_mask is not None: F = F[cell_mask]
    F = F.reshape(-1, 4)
    used = np.unique(F); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used))
    return V[used], remap[F]

def make_mesh(bpy, name, V, F, mat, coll):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V)); me.vertices.foreach_set('co', np.asarray(V, np.float32).ravel())
    me.loops.add(F.size); me.loops.foreach_set('vertex_index', F.ravel().astype(np.int32))
    me.polygons.add(len(F)); me.polygons.foreach_set('loop_start', np.arange(0, F.size, 4, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(len(F), 4, np.int32))
    me.polygons.foreach_set('use_smooth', np.ones(len(F), bool)); me.update(); me.validate()
    if mat is not None: me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

def snap(v, lo, step): return lo + step * round((v - lo) / step)

def build_terrain(bpy, mat, coll, region=(-4.2, 4.2, -1.5, 4.6), cs=0.024, fs=0.006, fine=None, fn=terrain_h, prints=True, name='sand'):
    x0, x1, y0, y1 = region
    nx = int(round((x1 - x0) / cs)); ny = int(round((y1 - y0) / cs))
    X = x0 + cs * np.arange(nx + 1); Y = y0 + cs * np.arange(ny + 1)
    rects = []
    for (a, b, c, d) in (fine or []):
        rects.append((snap(a, x0, cs), snap(b, x0, cs), snap(c, y0, cs), snap(d, y0, cs)))
    gx, gy = np.meshgrid(X, Y, indexing='ij'); H = fn(gx, gy)
    if prints: apply_prints(X, Y, H)
    cm = np.ones((nx, ny), bool)
    cx = (X[:-1] + X[1:]) / 2; cy = (Y[:-1] + Y[1:]) / 2
    for (a, b, c, d) in rects: cm &= ~(((cx[:, None] > a) & (cx[:, None] < b)) & ((cy[None, :] > c) & (cy[None, :] < d)))
    V, F = grid_mesh(X, Y, H, cm); objs = [make_mesh(bpy, name, V, F, mat, coll)]
    for k, (a, b, c, d) in enumerate(rects):
        fx = np.arange(int(round((b - a) / fs)) + 1) * fs + a; fy = np.arange(int(round((d - c) / fs)) + 1) * fs + c
        gx, gy = np.meshgrid(fx, fy, indexing='ij'); Hf = fn(gx, gy)
        if prints: apply_prints(fx, fy, Hf)
        V, F = grid_mesh(fx, fy, Hf); objs.append(make_mesh(bpy, f'{name}_fine{k}', V, F, mat, coll))
    return objs
