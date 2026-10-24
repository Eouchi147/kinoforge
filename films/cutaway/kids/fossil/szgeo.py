"""How does a dinosaur turn into stone? Geometry helpers (numpy + bpy): rigid parts in one mesh, primitives, the dinosaur.

Parts: many small rigid pieces (a bird's body and wings, a butterfly, a tree, a sheep) in ONE mesh; every frame each piece
gets a position, a rotation and a scale and the vertices are rewritten with numpy (cheap, deterministic, any frame alone).
A piece with scale 0 is parked far below the world (it does not render).
The dinosaur is one swept tube along a spine that blends three poses (standing, munching, lying curled up), plus legs and
eyes, rebuilt every frame from t: storybook proportions, round and soft, no teeth.
"""
import math

import numpy as np

import cutaway as cw


# ------------------------------------------------------------------ rotations
def rz(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])

def ry(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def rx(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def euler(x=0.0, y=0.0, z=0.0):
    return rz(z) @ ry(y) @ rx(x)

I3 = np.eye(3)


# ------------------------------------------------------------------ primitives (V, F)
_ICO = {}

def sphere(c=(0, 0, 0), r=(1, 1, 1), sub=2):
    if sub not in _ICO: _ICO[sub] = cw._icosphere(sub)
    V, F = _ICO[sub]; return V * np.asarray(r, float) + np.asarray(c, float), F

def tube(pts, radii, ring=8, cap=True):
    V, F = cw._tube(pts, radii, ring, cap); return np.asarray(V, float), F

def cone(c, r, h, ring=12, r_top=0.0):
    c = np.asarray(c, float); V = []; F = []
    for k in range(ring):
        a = 2 * math.pi * k / ring; V.append(c + (r * math.cos(a), r * math.sin(a), 0)); V.append(c + (r_top * math.cos(a), r_top * math.sin(a), h))
    for k in range(ring):
        a, b = 2 * k, 2 * ((k + 1) % ring); F.append((a, b, b + 1, a + 1))
    V.append(c); V.append(c + (0, 0, h)); n = len(V)
    for k in range(ring):
        F.append((n - 2, 2 * ((k + 1) % ring), 2 * k)); F.append((n - 1, 2 * k + 1, 2 * ((k + 1) % ring) + 1))
    return np.array(V), F

def box(c, s):
    c = np.asarray(c, float); s = np.asarray(s, float) / 2
    V = [c + s * np.array(p) for p in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))]
    F = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return np.array(V), F

def disc(c, r, ring=16, axis='z'):
    c = np.asarray(c, float); V = [c]
    for k in range(ring):
        a = 2 * math.pi * k / ring; p = (r * math.cos(a), r * math.sin(a), 0) if axis == 'z' else (r * math.cos(a), 0, r * math.sin(a)) if axis == 'y' else (0, r * math.cos(a), r * math.sin(a))
        V.append(c + p)
    F = [(0, 1 + k, 1 + (k + 1) % ring) for k in range(ring)]
    return np.array(V), F

def quad(pts):
    return np.asarray(pts, float), [(0, 1, 2, 3)]


class Parts:
    """Rigid pieces in one mesh. add() returns a piece index; build(); then pose(P, R, S) each frame."""
    def __init__(self, name):
        self.name = name; self.V = []; self.F = []; self.M = []; self.it = []; self.n = 0; self.ob = None
    def add(self, V, F, m=0, pivot=(0, 0, 0)):
        V = np.asarray(V, float) - np.asarray(pivot, float); o = len(self.V)
        self.V += [tuple(v) for v in V]; self.F += [tuple(i + o for i in f) for f in F]; self.M += [m] * len(F)
        self.it += [self.n] * len(V); self.n += 1; return self.n - 1
    def build(self, bpy, mats, coll, smooth=True, attrs=None):
        self.L = np.array(self.V, float); self.idx = np.array(self.it, int)
        self.ob = cw.mk_mesh(bpy, self.name, self.L, self.F, mats, self.M, smooth, coll, attrs)
        self.P = np.zeros((self.n, 3)); self.R = np.repeat(I3[None], self.n, 0); self.S = np.zeros((self.n, 3))
        return self.ob
    def set(self, k, p, R=None, s=1.0):
        self.P[k] = p; self.R[k] = I3 if R is None else R; self.S[k] = s if np.ndim(s) else (s, s, s)
    def hide(self, k): self.S[k] = 0.0
    def commit(self):
        i = self.idx; Ls = self.L * self.S[i]
        V = np.einsum('nij,nj->ni', self.R[i], Ls) + self.P[i]
        V[np.all(self.S[i] <= 1e-5, axis=1)] = (0.0, 0.0, -50.0)
        me = self.ob.data; me.vertices.foreach_set('co', V.astype(np.float32).ravel()); me.update()


# ------------------------------------------------------------------ the dinosaur (a gentle long-neck, storybook shapes)
# spine control points, tail tip to head, in the dinosaur's own frame (x forward, z up, origin on the ground under the hips)
STAND = [(-1.05, 0, 0.20), (-0.76, 0, 0.32), (-0.44, 0, 0.44), (-0.18, 0, 0.50), (0.05, 0, 0.52), (0.26, 0, 0.52), (0.42, 0, 0.60),
         (0.53, 0, 0.80), (0.59, 0, 0.98), (0.68, 0, 1.06)]
MUNCH = [(-1.05, 0, 0.20), (-0.76, 0, 0.32), (-0.44, 0, 0.44), (-0.18, 0, 0.50), (0.05, 0, 0.51), (0.26, 0, 0.50), (0.44, 0, 0.52),
         (0.62, 0, 0.48), (0.78, 0, 0.36), (0.90, 0, 0.26)]
LIE = [(-0.95, -0.16, 0.05), (-0.64, -0.06, 0.08), (-0.32, 0, 0.13), (-0.12, 0, 0.16), (0.08, 0, 0.17), (0.28, 0, 0.15), (0.44, -0.03, 0.12),
       (0.60, -0.10, 0.09), (0.74, -0.17, 0.07), (0.86, -0.19, 0.07)]
RAD = [(0.0, 0.012), (0.15, 0.045), (0.30, 0.10), (0.42, 0.17), (0.55, 0.19), (0.66, 0.16), (0.74, 0.085), (0.86, 0.056),
       (0.945, 0.05), (0.972, 0.068), (1.0, 0.034)]
NS, RING = 56, 14
HIP_S, SHO_S = 0.47, 0.64


def _resample(C, n):
    C = np.asarray(C, float); D = cw.catmull([tuple(c) for c in C], 200) if hasattr(cw, 'catmull') else C
    D = np.asarray(D, float); seg = np.linalg.norm(np.diff(D, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); s /= s[-1]
    u = np.linspace(0, 1, n); return np.column_stack([np.interp(u, s, D[:, k]) for k in range(3)])


class Dino:
    """Build once (topology), pose every frame: pose(root(x, y, z), yaw, w_munch, w_lie, walk_phase, walk_amt, tail, eyes,
    scale, alpha handled by the material)."""
    def __init__(self, bpy, name, mats, coll, scale=1.0):
        self.k = scale; self.name = name
        u = np.linspace(0, 1, NS); self.r = np.interp(u, [a for a, _ in RAD], [b for _, b in RAD]) * scale
        F = []
        for i in range(NS - 1):
            for j in range(RING):
                a = i * RING + j; b = i * RING + (j + 1) % RING; F.append((a, b, b + RING, a + RING))
        nb = NS * RING; V0 = np.zeros((nb + 2, 3)); F += [(nb, (j + 1) % RING, j) for j in range(RING)]
        F += [(nb + 1, (NS - 1) * RING + j, (NS - 1) * RING + (j + 1) % RING) for j in range(RING)]
        M = [0] * len(F)
        self.nbody = nb + 2
        # legs: 4 tubes of 3 points, ring 8
        self.leg_v0 = []; o = self.nbody; LV = []
        for _ in range(4):
            v, f = tube([(0, 0, 0), (0, 0, 0.5), (0, 0, 1)], [1, 1, 1], 8, True)
            F += [tuple(i + o for i in ff) for ff in f]; M += [0] * len(f); self.leg_v0.append(o); o += len(v); LV.append(v)
        self.nleg = len(LV[0])
        # eyes: two small spheres
        self.eye_v, self.eye_f = sphere((0, 0, 0), (1, 1, 1), 1); self.eye_o = []
        for _ in range(2):
            F += [tuple(i + o for i in ff) for ff in self.eye_f]; M += [1] * len(self.eye_f); self.eye_o.append(o); o += len(self.eye_v)
        self.nv = o
        self.ob = cw.mk_mesh(bpy, name, np.zeros((o, 3)), F, mats, M, True, coll)

    def spine(self, w_munch, w_lie, tail_sway, curl):
        S = np.asarray(STAND, float); Mu = np.asarray(MUNCH, float); Li = np.asarray(LIE, float)
        C = S + (Mu - S) * w_munch; C = C + (Li - C) * w_lie
        # the tail sways gently from side to side (more at the tip)
        for i in range(4): C[i, 1] += tail_sway * (1 - i / 4) ** 2 * 0.18 * (1 - 0.7 * w_lie)
        # curling up: the tail and the neck bend round towards the viewer a little more
        C[0, 1] -= 0.10 * curl; C[1, 1] -= 0.04 * curl; C[-1, 1] -= 0.10 * curl; C[-2, 1] -= 0.06 * curl
        return _resample(C * self.k, NS)

    def pose(self, root, yaw, w_munch=0.0, w_lie=0.0, walk=0.0, walk_amt=0.0, tail=0.0, curl=0.0, eyes=1.0, breathe=0.0, bob=0.0):
        P = self.spine(w_munch, w_lie, tail, curl)
        P[:, 2] += bob * (1 - w_lie)
        T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
        r = self.r * (1 + breathe * np.exp(-((np.linspace(0, 1, NS) - 0.55) / 0.12) ** 2))
        out = np.zeros((self.nv, 3)); up = np.array([0, 0, 1.0])
        ph = 2 * math.pi * np.arange(RING) / RING; cph, sph = np.cos(ph), np.sin(ph)
        for i in range(NS):
            a = up if abs(T[i] @ up) < 0.95 else np.array([1.0, 0, 0])
            N = np.cross(a, T[i]); N /= np.linalg.norm(N); Bv = np.cross(T[i], N)
            # a little flatter on the belly, rounder on the back
            out[i * RING:(i + 1) * RING] = P[i] + r[i] * (cph[:, None] * N + sph[:, None] * Bv * 1.0)
        out[NS * RING] = P[0]; out[NS * RING + 1] = P[-1]
        # legs (hips and shoulders): standing columns, a walking swing, folded under when lying
        si = lambda s: P[int(round(s * (NS - 1)))]
        k = self.k
        for li, (s, side, phs) in enumerate(((HIP_S, -1, 0.0), (HIP_S, 1, math.pi), (SHO_S, -1, math.pi), (SHO_S, 1, 0.0))):
            top = si(s) + np.array([0, side * 0.09 * k, -0.04 * k])
            sw = walk_amt * math.sin(walk + phs); lift = walk_amt * max(0.0, math.cos(walk + phs)) * 0.05 * k
            foot_st = np.array([top[0] + 0.10 * sw * k, top[1] + side * 0.02 * k, lift])
            knee_st = (top + foot_st) / 2 + np.array([0.02 * k, 0, 0])
            foot_ly = np.array([top[0] + 0.16 * k, top[1] + side * 0.10 * k, 0.03 * k]); knee_ly = np.array([top[0] - 0.06 * k, top[1] + side * 0.15 * k, 0.06 * k])
            foot = foot_st + (foot_ly - foot_st) * w_lie; knee = knee_st + (knee_ly - knee_st) * w_lie
            v, _ = tube([top, knee, foot], [0.062 * k, 0.052 * k, 0.058 * k], 8, True)
            out[self.leg_v0[li]:self.leg_v0[li] + self.nleg] = v
        # eyes on the head, a little forward; they close (flatten) when it sleeps
        hd = P[-4]; tg = T[-4]; side_v = np.cross(up, tg); side_v /= np.linalg.norm(side_v) + 1e-9
        for e, sd in zip(self.eye_o, (-1, 1)):
            c = hd + side_v * sd * 0.055 * k + np.array([0, 0, 0.018 * k]) + tg * 0.012 * k
            sc = np.array([0.013, 0.013, 0.013 * max(0.12, eyes)]) * k
            out[e:e + len(self.eye_v)] = self.eye_v * sc + c
        R = rz(yaw); out = out @ R.T + np.asarray(root, float)
        me = self.ob.data; me.vertices.foreach_set('co', out.astype(np.float32).ravel()); me.update()
        return P

    def rigid(self, w_munch=0.0, w_lie=0.0):
        """(V, F) of a fixed pose (for the far herd and the toy): pose once at the origin and read the mesh back."""
        self.pose((0, 0, 0), 0.0, w_munch, w_lie)
        me = self.ob.data; V = np.array([v.co[:] for v in me.vertices]); F = [tuple(p.vertices) for p in me.polygons]
        M = [p.material_index for p in me.polygons]
        return V, F, M


def dino_fossil_2d(k=1.0):
    """The lying skeleton seen side on (the cut face): the LIE spine's (x, z), resampled. Returns (pts (NS, 2), radii)."""
    P = _resample(np.asarray(LIE, float) * k, NS); u = np.linspace(0, 1, NS)
    return P[:, [0, 2]], np.interp(u, [a for a, _ in RAD], [b for _, b in RAD]) * k
