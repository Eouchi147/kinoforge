"""What lives in the deep sea? Geometry helpers (numpy + bpy): rigid parts in one mesh and primitives.

Parts: many small rigid pieces (a fish and its tail, a jellyfish bell and tentacles, the submarine) in ONE mesh; every frame each
piece gets a position, a rotation and a scale and the vertices are rewritten with numpy (cheap, deterministic, any frame alone).
A piece with scale 0 is parked far below the world (it does not render).
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
