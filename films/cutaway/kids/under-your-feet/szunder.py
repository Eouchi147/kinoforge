"""Who lives under your feet? The cut face: tunnels, roots, the neighbours and what is buried (bpy + numpy).

The front cut face (y = -HY) of the lifted slice is the stage. Flat painted shapes lie a hair in front of it (tunnels, rooms,
an ink edge: emission, so Fable leaves their colours alone); the creatures are small 3D figures a few centimetres in front of
the face; the tree's roots are tubes. All of it rides the slice's lift. Every pose is a pure function of t.

  roots and rootlets   the big tree's roots, with bright drops rising up them (the roots are drinking)
  the cicada thread    the shaft the nymph digs, its root, the side tunnels the others crawl through (bodies: szcic.py)
  earthworms           two, wriggling along winding tunnels; one chases a marble
  ants                 a town: an entrance shaft, a nursery (eggs, larvae, the queen, nurses), a pantry; ants walk the
                       tunnels; ONE ANT HAULS A SANDWICH CRUMB FAR BIGGER THAN ITSELF into the pantry (the visual joke)
  the mole             digs a long tunnel with big paws, throws soil, makes a molehill; never hunts (no predator is shown)
  beetle grubs         three round cream grubs in a room beside a root, nibbling
  easter eggs          a marble, a coin, a key, a toy treasure chest, a stone figure with a pointed hat, a toy car in the
                       right face
  warmth               in the stir the soil warms: a golden glow creeps down the face (the cue that it is time)
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, disc, quad, rz, ry, rx, euler, I3

FY = -W.HY
Y_T = FY - 0.0030           # tunnels
Y_INK = FY - 0.0024
Y_C = FY - 0.030            # the creatures' centre line (a few cm in front of the face)


def sm(a, b, t): return W.sm(a, b, t)


def pop_k(t, t0, d=0.45):
    """0 before t0, then a springy pop to 1 (a little overshoot)."""
    if t <= t0: return 0.0
    u = min(1.0, (t - t0) / d); return 1.0 + 1.7 * (u - 1) ** 3 + 0.7 * (u - 1) ** 2 if u < 1.0 else 1.0


class Path:
    """A polyline in the face's (x, z) with arc length."""
    def __init__(self, pts):
        self.P = np.asarray(pts, float); seg = np.linalg.norm(np.diff(self.P, axis=0), axis=1); self.c = np.concatenate([[0], np.cumsum(seg)]); self.L = float(self.c[-1])
    def at(self, s):
        s = float(np.clip(s, 0.0, self.L)); i = min(int(np.searchsorted(self.c, s, 'right')) - 1, len(self.P) - 2); f = (s - self.c[i]) / max(self.c[i + 1] - self.c[i], 1e-9)
        d = self.P[i + 1] - self.P[i]; d = d / (np.linalg.norm(d) + 1e-9); return self.P[i] + (self.P[i + 1] - self.P[i]) * f, d
    def ext(self, s):
        """Like at(), but beyond either end the path goes on straight (a worm's tail trailing out of a tunnel)."""
        if 0.0 <= s <= self.L: return self.at(s)
        p, d = self.at(0.0 if s < 0 else self.L); return p + d * (s if s < 0 else s - self.L), d


def catmull(pts, n=60):
    return np.array(cw.catmull([(p[0], p[1], 0.0) for p in pts], n))[:, :2]


# ------------------------------------------------------------------ the layout of the cut face (x, z)
ROOTS = {      # name: points (a gentle curve); radius from base to tip
    'R1': ([(W.ROOT_X, 0.0), (-0.72, -0.18), (-1.0, -0.34), (-1.35, -0.46), (-1.66, -0.60)], 0.052, 0.012),
    'R2': ([(W.ROOT_X, 0.0), (-0.60, -0.30), (-0.55, -0.58), (-0.62, -0.82), (-0.60, -1.0)], 0.046, 0.010),
    'R3': ([(W.ROOT_X, 0.0), (-0.50, -0.14), (-0.30, -0.28), (-0.12, -0.46), (0.06, -0.60)], 0.052, 0.012),
}
RootletsList = [      # (parent, u, direction angle degrees, length)
    ('R1', 0.30, 255, 0.20), ('R1', 0.55, 70, 0.14), ('R1', 0.72, 250, 0.22), ('R2', 0.35, 190, 0.18), ('R2', 0.55, 350, 0.16), ('R2', 0.80, 170, 0.12),
    ('R3', 0.35, 70, 0.12), ('R3', 0.60, 280, 0.16), ('R1', 0.90, 280, 0.12)]
PATH_ROOT = {k: Path(catmull(v[0])) for k, v in ROOTS.items()}

NYMPH_POST = (-0.19, -0.385)           # where the main nymph sips: on root R3, right beside the shaft
SIB = {   # name: (post on a root, route to the shaft a list of (x, z) points ending on the shaft x)
    'S1': ((-1.00, -0.335), [(-1.00, -0.335), (-0.80, -0.30), (-0.52, -0.285), (W.SHAFT_X, -0.27)]),
    'S2': ((-0.575, -0.62), [(-0.575, -0.62), (-0.42, -0.62), (W.SHAFT_X, -0.60)]),
    'S3': ((0.02, -0.575), [(0.02, -0.575), (-0.10, -0.62), (W.SHAFT_X, -0.64)]),
    'S4': ((-1.50, -0.545), [(-1.50, -0.545), (-1.20, -0.62), (-0.80, -0.70), (-0.45, -0.72), (W.SHAFT_X, -0.68)]),
}
SHAFT_TOP = (W.SHAFT_X, 0.02)
SHAFT_BOT = (W.SHAFT_X, -0.70)
TUNNELS = {
    # name: (points, width, draw start, draw end) ; pure shapes grown along their length with t
    'shaft': ([SHAFT_TOP, (W.SHAFT_X, -0.28), NYMPH_POST], 0.150, 'nymph', None),
    'shaft2': ([NYMPH_POST, (W.SHAFT_X, -0.50), SHAFT_BOT], 0.140, 'gather', None),
    'worm1': ([(0.10, 0.02), (0.14, -0.14), (0.03, -0.30), (0.14, -0.46), (0.30, -0.54), (0.46, -0.58), (0.70, -0.585), (0.95, -0.60)], 0.130, 'tun_worm', None),
    'worm2': ([(-1.45, 0.02), (-1.40, -0.12), (-1.50, -0.26)], 0.115, 'tun_worm', None),
    'ant0': ([(1.30, 0.02), (1.30, -0.22)], 0.140, 'tun_ant', None),
    'ant1': ([(1.05, -0.34), (0.80, -0.34)], 0.130, 'tun_ant', None),
    'mole': ([(W.HX + 0.05, -0.86), (1.40, -0.84), (1.0, -0.88), (0.6, -0.84), (0.25, -0.88), (0.05, -0.86)], 0.26, 'mole', None),
    'moleup': ([(1.62, -0.78), (1.62, 0.02)], 0.110, 'moleup', None),
    'grubs': ([(-1.40, -0.60), (-1.40, -0.68)], 0.09, 'tun_grub', None),
}
CHAMBERS = {   # name: (centre, rx, rz, reveal event)
    'nursery': ((1.30, -0.34), 0.40, 0.19, 'tun_ant'), 'pantry': ((0.58, -0.34), 0.28, 0.165, 'tun_ant'),
    'grubroom': ((-1.30, -0.78), 0.36, 0.15, 'tun_grub'),
}
for nm, (pts, w, ev, _) in list(TUNNELS.items()):
    pass
# the sibling tunnels (dug by the crawling nymphs; each grows with its own nymph)
for nm, (post, route) in SIB.items():
    TUNNELS['t' + nm] = (route[::-1] if False else route, 0.085, 'sib' + nm, None)

ANT_ROUTE = Path([(1.30, 0.0), (1.30, -0.20), (1.30, -0.34), (1.02, -0.34), (0.58, -0.34)])        # entrance to the pantry
ANT_LOOP = Path([(1.30, -0.34), (1.0, -0.34), (0.58, -0.34)])
WORM_A = Path(catmull(TUNNELS['worm1'][0], 40))
WORM_B = Path(catmull(TUNNELS['worm2'][0], 20))
MOLE_PATH = Path(catmull(TUNNELS['mole'][0], 50))


def mole_hill_k(t):
    """The molehill on the lawn grows when the mole passes below it (about 10.2 s) and stays."""
    return W.sm(W.B.tun_mole0 + 0.9, W.B.tun_mole0 + 2.0, t) * 1.0


def tunnel_progress(name, t, B=None):
    """0..1 how much of the tunnel is open."""
    B = W.B; ev = TUNNELS[name][2] if name in TUNNELS else None
    if ev == 'nymph': return float(np.clip(nymph_descent(t), 0, 1))
    if ev == 'gather': return W.sm(B.unhook0 - 0.2, B.gather0, t)
    if ev == 'tun_worm': return W.sm(B.tun_worm0, B.tun_worm1, t)
    if ev == 'tun_ant': return W.sm(B.tun_ant0, B.tun_ant1, t)
    if ev == 'tun_grub': return W.sm(B.tun_grub0, B.tun_grub1, t)
    if ev == 'moleup': return W.sm(B.tun_mole0 + 0.8, B.tun_mole0 + 1.5, t)
    if ev == 'mole':
        x = mole_x(t); s = MOLE_PATH.L * 0.0
        # open as far as the mole has dug (plus its snout)
        head = mole_s(t); return float(np.clip((head + 0.14) / MOLE_PATH.L, 0.0, 1.0)) if t > B.pop_mole else 0.0
    if isinstance(ev, str) and ev.startswith('sib'):
        return float(np.clip(sib_s(ev[3:], t) / SIB_PATHS[ev[3:]].L, 0.0, 1.0)) if t > B.unhook0 else 0.0
    return 0.0


# ------------------------------------------------------------------ the cicada thread's routes on the face
SHAFT_PATH = Path([SHAFT_TOP, (W.SHAFT_X, -0.28), NYMPH_POST])


def nymph_descent(t):
    """Progress 0..1 down the shaft (8.1 s to 12.3 s)."""
    B = W.B; return W.sm(B.shaft0 + 0.1, B.shaft1, t) if t < B.unhook0 else 1.0


SIB_PATHS = {k: Path(r) for k, (post, r) in SIB.items()}
# up the shaft (from the junction to the lawn): the nymphs climb in a queue
UP = {'M': Path([NYMPH_POST, (W.SHAFT_X, -0.30), (W.SHAFT_X, -0.12), SHAFT_TOP])}
for k, (post, r) in SIB.items():
    junc = r[-1]; UP[k] = Path([junc, (W.SHAFT_X, -0.30), (W.SHAFT_X, -0.12), SHAFT_TOP])


def sib_s(k, t):
    """Arc length along the sibling's crawl route (post to the shaft)."""
    B = W.B; idx = list(SIB).index(k); a = B.unhook0 + 0.12 * idx; b = B.gather1 - 0.5 + 0.1 * idx
    return SIB_PATHS[k].L * W.sm(a, b, t)


def nymph_state(who, t):
    """Where a nymph is on the face / lawn: ('hidden'|'face'|'lawn', (x, z) or None, tangent angle, mode, climb u).
    who is 'M' (the main nymph) or 'S1'..'S4'."""
    B = W.B
    idx = 0 if who == 'M' else 1 + list(SIB).index(who)
    pop = B.pop0 + 0.16 * idx                      # when it leaves the shaft at the top (staggered)
    up_a = B.up0 + 0.0 * idx - 0.0                 # the climb begins together
    if who == 'M':
        if t < B.shaft0: return 'hidden', None, 0.0, 'none', 0.0
        if t < B.unhook0:
            s = nymph_descent(t) * SHAFT_PATH.L; p, d = SHAFT_PATH.at(s)
            return 'face', p, math.atan2(d[1], d[0]), 'dig' if nymph_descent(t) < 0.995 else 'sip', nymph_descent(t)
        if t < B.up0: return 'face', np.array(NYMPH_POST), math.pi, 'unhook', 0.0
    else:
        post, route = SIB[who]
        if t < B.unhook0: return 'face', np.array(post), 0.0, 'sip', 0.0
        P = SIB_PATHS[who]
        if t < B.gather1 - 0.5 + 0.1 * (idx - 1):
            p, d = P.at(sib_s(who, t)); return 'face', p, math.atan2(d[1], d[0]), 'crawl', 0.0
        if t < B.up0 + 0.0: return 'face', np.array(route[-1]), math.pi / 2, 'wait', 0.0
    # up the shaft to the lawn: 4 s climb, main nymph first
    U = UP[who]; a = B.up0 + 0.14 * idx; b = pop - 0.02
    if t < b:
        s = U.L * W.sm(a, b, t); p, d = U.at(s)
        return 'face', p, math.atan2(d[1], d[0]), 'climb', W.sm(a, b, t)
    return 'lawn', None, 0.0, 'out', 1.0


# ------------------------------------------------------------------ a swept tube that is re-posed every frame
class Sweep:
    """A tube along n stations (any 3D path), ring points each; radii per station; caps at both ends."""
    def __init__(self, kit, name, mats, n, ring=8, mat_idx=0):
        self.n, self.ring = n, ring; F = []
        for i in range(n - 1):
            for j in range(ring):
                a = i * ring + j; b = i * ring + (j + 1) % ring; F.append((a, b, b + ring, a + ring))
        nb = n * ring; F += [(nb, (j + 1) % ring, j) for j in range(ring)]
        F += [(nb + 1, (n - 1) * ring + j, (n - 1) * ring + (j + 1) % ring) for j in range(ring)]
        self.ob = cw.mk_mesh(kit.bpy, name, np.zeros((nb + 2, 3)), F, mats, [mat_idx] * len(F), True, kit.coll)
        self.cph, self.sph = np.cos(2 * math.pi * np.arange(ring) / ring), np.sin(2 * math.pi * np.arange(ring) / ring)
    def set(self, P, R, e1=(0.0, -1.0, 0.0)):
        P = np.asarray(P, float); n = self.n; T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
        e1 = np.asarray(e1, float); E2 = np.cross(T, e1); E2 /= np.linalg.norm(E2, axis=1)[:, None] + 1e-9
        out = np.zeros((n * self.ring + 2, 3)); R = np.broadcast_to(np.asarray(R, float), (n,))
        for i in range(n):
            out[i * self.ring:(i + 1) * self.ring] = P[i] + R[i] * (self.cph[:, None] * e1 + self.sph[:, None] * E2[i])
        out[n * self.ring] = P[0] - T[0] * R[0] * 0.5; out[n * self.ring + 1] = P[-1] + T[-1] * R[-1] * 0.5
        me = self.ob.data; me.vertices.foreach_set('co', out.astype(np.float32).ravel()); me.update()
    def hide(self, h): self.ob.hide_render = h


# ------------------------------------------------------------------ flat shapes: tunnels, rooms and their ink edge
class Flat:
    """Tunnel ribbons that grow along their path with a progress value, and room blobs, as flat painted meshes on the face.
    Vertex attribute `e` = 1 at the centre line and 0 at the rim (a darker middle and a lit lip); `g` = glow."""
    def __init__(self, kit, D, rng):
        bpy = kit.bpy; self.tun = {}; V = []; Fc = []; E = []; self.ranges = {}
        NS = 36
        for nm, (pts, w, ev, _) in TUNNELS.items():
            C = catmull(pts, NS) if len(pts) > 2 else np.linspace(pts[0], pts[-1], NS)
            seg = np.linalg.norm(np.diff(C, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)]); cum /= cum[-1]
            T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9; N = np.column_stack([-T[:, 1], T[:, 0]])
            o = len(V); self.ranges[nm] = (o, NS, C, cum, N, w)
            for i in range(NS):
                for e_, off in ((0.0, -1.0), (1.0, 0.0), (0.0, 1.0)): V.append((0.0, Y_T, 0.0)); E.append(e_)
            for i in range(NS - 1):
                a = o + 3 * i
                Fc += [(a, a + 3, a + 4, a + 1), (a + 1, a + 4, a + 5, a + 2)]
        self.nt = len(V)
        # rooms: wobbly ellipses (fan), static
        self.rooms = {}
        for nm, (c, rx_, rz_, ev) in CHAMBERS.items():
            o = len(V); V.append((c[0], Y_T, c[1])); E.append(1.0); n = 28
            for k in range(n):
                a = 2 * math.pi * k / n; wob = 1 + 0.06 * math.sin(3 * a + len(nm)) + 0.04 * math.sin(5 * a + 1)
                V.append((c[0] + rx_ * wob * math.cos(a), Y_T, c[1] + rz_ * wob * math.sin(a))); E.append(0.0)
            Fc += [(o, o + 1 + k, o + 1 + (k + 1) % n) for k in range(n)]; self.rooms[nm] = (o, n, c, rx_, rz_, ev)
        self.E = np.array(E, float); self.V0 = np.array(V, float); self.F = Fc
        m = cw._new_mat(bpy, 'fs_tunnel'); g = cw.G(m.node_tree, kit)
        e = g.attr('e').outputs['Fac']
        col = g.mix(g.math('MULTIPLY', e, 1.0, clamp=True), cw.srgb((0.62, 0.40, 0.30)), cw.srgb((0.14, 0.07, 0.09)))        # lit lip to a deep warm dark
        glow = D.val(g, 'tglow', 0.0); col = g.mix(g.math('MULTIPLY', glow, 0.55), col, cw.srgb((1.0, 0.78, 0.42)))
        em = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}); M._alpha_out(g, em, D.val(g, 'talpha', 1.0))
        self.ob = cw.mk_mesh(bpy, 'fs_tunnels', self.V0, Fc, [m], None, True, kit.coll, {'e': ('FLOAT', list(self.E))})
        for a in ('visible_shadow',): setattr(self.ob, a, False)
        # an ink outline behind (a wider, darker copy: the tunnels' edge)
        self.V_ink = None
    def pose(self, t, lift):
        V = self.V0.copy(); B = W.B
        for nm, (o, NS, C, cum, N, w) in self.ranges.items():
            pg = tunnel_progress(nm, t)
            if pg <= 1e-3:
                V[o:o + 3 * NS] = (0.0, 0.0, -50.0); continue
            for i in range(NS):
                u = min(cum[i], pg); k = np.searchsorted(cum, u, 'right') - 1; k = min(max(k, 0), NS - 2); f = (u - cum[k]) / max(cum[k + 1] - cum[k], 1e-9)
                c = C[k] + (C[k + 1] - C[k]) * f; nn = N[k]
                # the width swells in at the head (rounded end) and tapers out at the very start
                cap = 1.0 if i == 0 or cum[i] <= pg - 1e-9 else 1.0
                ww = w * 0.5 * (0.75 + 0.25 * min(1.0, pg / 0.1)) if True else w * 0.5
                if cum[i] > pg: ww = 0.0
                for j, off in enumerate((-1.0, 0.0, 1.0)):
                    q = c + nn * off * ww; V[o + 3 * i + j] = (q[0], Y_T, q[1])
        # rooms grow with their reveal
        for nm, (o, n, c, rx_, rz_, ev) in self.rooms.items():
            k = {'tun_ant': W.sm(B.tun_ant0 + 0.2, B.tun_ant1, t), 'tun_grub': W.sm(B.tun_grub0, B.tun_grub1, t)}[ev]
            for q in range(n + 1):
                p = self.V0[o + q]; V[o + q] = (c[0] + (p[0] - c[0]) * k, Y_T, c[1] + (p[2] - c[1]) * k) if q else (c[0], Y_T, c[1])
        V[:, 2] = np.where(V[:, 2] < -40, V[:, 2], V[:, 2] + lift)
        self.ob.data.vertices.foreach_set('co', V.astype(np.float32).ravel()); self.ob.data.update()


# ------------------------------------------------------------------ the worms
class Worm:
    def __init__(self, kit, D, name, path, color, band, seed, seg=0.020):
        self.path = path; self.seg = seg; self.sw = Sweep(kit, name, [M.paint(kit, D, name + 'm', color, noise=0.0), M.paint(kit, D, name + 'b', band, noise=0.0)], 26, 8)
        self.sw.ob.data.materials.clear(); self.sw.ob.data.materials.append(M.paint(kit, D, name + 'm', color, noise=0.0))
        pr = Parts(name + '_eyes'); m = [M.paint(kit, D, name + 'e', (0.08, 0.06, 0.10), noise=0.0), M.paint(kit, D, name + 'w', (1.0, 0.98, 0.95), noise=0.0)]
        self.eyes = [pr.add(*sphere((0, 0, 0), (0.0085, 0.0085, 0.0085), 1), m=0) for _ in range(2)] + [pr.add(*sphere((0, 0, 0), (0.0125, 0.0105, 0.0125), 1), m=1) for _ in range(2)]
        pr.build(kit.bpy, m, kit.coll); self.pr = pr; self.seed = seed
    def pose(self, t, s_head, k, lift, wave=0.026, rad=0.040):
        """s_head: arc length of the head on the path; k: size (0 hides it)."""
        if k < 0.02: self.sw.hide(True); [self.pr.hide(j) for j in self.eyes]; self.pr.commit(); return
        self.sw.hide(False); n = self.sw.n; seg = self.seg * k
        S = s_head - seg * np.arange(n)           # head first
        P = np.zeros((n, 3)); dirv = None
        for i, s in enumerate(S):
            p, d = self.path.ext(s); nrm = np.array([-d[1], d[0]]); ph = 2 * math.pi * (1.6 * i / n - 0.9 * t) + self.seed
            off = wave * k * math.sin(ph) * (0.35 + 0.65 * i / n)
            P[i] = (p[0] + nrm[0] * off, Y_C, p[1] + nrm[1] * off + lift)
        r = rad * k * (0.78 + 0.22 * np.sin(np.pi * np.linspace(0.0, 1.0, n) ** 0.8)) * np.where(np.arange(n) < 2, 0.8, 1.0)
        r[-1] *= 0.5; r[-2] *= 0.8
        # the pinker band (the saddle) is painted by radius: a small swelling
        r = r * (1 + 0.07 * np.exp(-((np.arange(n) - 0.28 * n) / 1.3) ** 2))
        self.sw.set(P, r)
        hd = P[0] - P[1]; hd /= np.linalg.norm(hd) + 1e-9; side = np.cross(hd, (0, 1, 0)); side /= np.linalg.norm(side) + 1e-9
        for q, sd in enumerate((1, -1)):
            c = P[0] + hd * 0.004 + side * sd * 0.011 * k + np.array([0, -0.017, 0.009]) * k
            self.pr.set(self.eyes[2 + q], c, I3, k); self.pr.set(self.eyes[q], c + np.array([0, -0.007, 0.001]) + hd * 0.004 * k, I3, k)
        self.pr.commit()


# ------------------------------------------------------------------ ants
def face_frame(tx, tz):
    """Orientation of a creature that walks along (tx, tz) in the face plane, upright when it can be."""
    if tx >= 0: return ry(-math.atan2(tz, max(tx, 1e-6)))
    return ry(math.atan2(tz, max(-tx, 1e-6))) @ rz(math.pi)


AS = 1.55      # storybook scale of the ants


class Ants:
    """Seven ants and a queen: three parts of body, a pair of eyes, two antennae, six legs each."""
    def __init__(self, kit, D, rng):
        pr = Parts('fs_ants'); self.pr = pr
        mats = [M.paint(kit, D, 'sz_antbody', (0.20, 0.12, 0.14), noise=0.0), M.paint(kit, D, 'sz_anteye', (0.99, 0.99, 0.96), noise=0.0), M.paint(kit, D, 'sz_antpupil', (0.04, 0.04, 0.06), noise=0.0),
                M.paint(kit, D, 'sz_queen', (0.50, 0.20, 0.26), noise=0.0), M.paint(kit, D, 'sz_crown', (1.0, 0.82, 0.22), noise=0.0),
                M.paint(kit, D, 'sz_egg', (0.99, 0.95, 0.84), noise=0.0), M.paint(kit, D, 'sz_larva', (0.96, 0.88, 0.62), noise=0.0),
                M.paint(kit, D, 'sz_bread', (0.96, 0.78, 0.46), noise=0.0), M.paint(kit, D, 'sz_filling', (0.56, 0.78, 0.28), noise=0.0), M.paint(kit, D, 'sz_cheese', (1.0, 0.84, 0.22), noise=0.0),
                M.paint(kit, D, 'sz_seed', (0.62, 0.40, 0.20), noise=0.0)]
        self.ants = []
        for k in range(8):
            queen = k == 7; m = 3 if queen else 0
            a = {'abd': pr.add(*sphere((-0.040, 0, 0.0), (0.040, 0.030, 0.032), 2), m=m), 'thx': pr.add(*sphere((0.000, 0, 0.004), (0.024, 0.020, 0.022), 2), m=m),
                 'head': pr.add(*sphere((0.040, 0, 0.012), (0.030, 0.026, 0.028), 2), m=m),
                 'eyeL': pr.add(*sphere((0.054, 0.020, 0.020), (0.011, 0.007, 0.011), 1), m=1), 'eyeR': pr.add(*sphere((0.054, -0.020, 0.020), (0.011, 0.007, 0.011), 1), m=1),
                 'pupL': pr.add(*sphere((0.060, 0.0235, 0.020), (0.0055, 0.004, 0.0065), 1), m=2), 'pupR': pr.add(*sphere((0.060, -0.0235, 0.020), (0.0055, 0.004, 0.0065), 1), m=2),
                 'antL': pr.add(*tube([(0.050, 0.010, 0.034), (0.070, 0.016, 0.062), (0.082, 0.020, 0.068)], [0.0035, 0.003, 0.0035], 5), m=m),
                 'antR': pr.add(*tube([(0.050, -0.010, 0.034), (0.070, -0.016, 0.062), (0.082, -0.020, 0.068)], [0.0035, 0.003, 0.0035], 5), m=m)}
            a['legs'] = [pr.add(*tube([(0, 0, 0), (0.012 * (i % 3 - 1), 0.0, -0.032)], [0.0045, 0.003], 5), m=m) for i in range(6)]
            if queen: a['crown'] = pr.add(*cone((0.038, 0, 0.040), 0.020, 0.024, 6, 0.006), m=4)
            self.ants.append(a)
        # eggs and larvae in the nursery, crumbs, seeds, the big sandwich crumb (a triangle sandwich: two bread slices around a green filling and cheese)
        self.eggs = [(pr.add(*sphere((0, 0, 0), (0.021, 0.018, 0.027), 2), m=5), (1.04 + 0.075 * (k % 4) + 0.02 * (k // 4), -0.42 + 0.05 * (k // 4) + 0.012 * (k % 2))) for k in range(10)]
        self.larvae = [(pr.add(*sphere((0, 0, 0), (0.026, 0.020, 0.020), 2), m=6), (1.12 + 0.10 * k, -0.27 + 0.01 * k)) for k in range(3)]
        self.crumbs = [(pr.add(*sphere((0, 0, 0), (0.014, 0.011, 0.011), 1), m=7), (0.40 + 0.10 * k, -0.43 + 0.035 * (k % 2))) for k in range(5)] + \
                      [(pr.add(*sphere((0, 0, 0), (0.010, 0.014, 0.010), 1), m=10), (0.46 + 0.11 * k, -0.40 + 0.03 * (k % 3))) for k in range(4)]
        tri = [(-0.10, 0, 0.0), (0.10, 0, 0.0), (0.0, 0, 0.14)]
        self.sand = [pr.add(*[(np.array(v) + (0, o, 0)) for v in [tri]][0:1], [(0, 1, 2)], m=mm) if False else pr.add(np.array([(-0.10, o, 0.0), (0.10, o, 0.0), (0.0, o, 0.14)]), [(0, 1, 2)], m=mm) for o, mm in ((-0.036, 7), (-0.020, 8), (-0.006, 9), (0.012, 7))]
        self.sand += [pr.add(np.array([(-0.10, 0.012, 0.0), (0.10, 0.012, 0.0), (0.0, 0.012, 0.14)]), [(0, 2, 1)], m=7)]
        # thicken the sandwich: boxes for the slices (so it has side faces)
        self.slab = [pr.add(*box((0, o, 0.045), (0.150, th, 0.095)), m=mm) for o, th, mm in ((-0.030, 0.014, 7), (-0.016, 0.012, 8), (-0.004, 0.008, 9), (0.012, 0.016, 7))]
        for j in self.sand: pass
        pr.build(kit.bpy, mats, kit.coll); self.mats = mats
    def place(self, a, p, d, k, t, ph, lift, nod=0.0, lean=0.0):
        pr = self.pr; R = face_frame(d[0], d[1]); stride = 2 * math.pi * 3.0 * t + ph
        k = k * AS; base = np.array([p[0], Y_C + 0.004, p[1] + lift + 0.026 * k]); Rb = R @ ry(lean)
        for nm in ('abd', 'thx', 'head', 'eyeL', 'eyeR', 'pupL', 'pupR', 'antL', 'antR'):
            wob = rx(0.12 * math.sin(2 * math.pi * 1.7 * t + ph)) if nm.startswith('ant') else I3
            pr.set(a[nm], base, Rb @ wob @ (ry(nod) if nm in ('head', 'eyeL', 'eyeR', 'pupL', 'pupR', 'antL', 'antR') else I3), k)
        for i, j in enumerate(a['legs']):
            side = 1 if i % 2 == 0 else -1; row = i // 2; foot = 0.012 * math.sin(stride + (math.pi if (row + (i % 2)) % 2 else 0.0))
            pr.set(j, base + Rb @ np.array([0.022 * (row - 1) * k, side * 0.012 * k, -0.006 * k]), Rb @ rz(side * 0.35) @ ry(foot / 0.03), k)
        if 'crown' in a: pr.set(a['crown'], base, Rb, k)
    def hide(self, a):
        for nm, j in a.items():
            if nm == 'legs': [self.pr.hide(q) for q in j]
            else: self.pr.hide(j)


# ------------------------------------------------------------------ the mole
class Mole:
    def __init__(self, kit, D):
        pr = Parts('fs_mole'); self.pr = pr
        mats = [M.paint(kit, D, 'sz_mole', (0.34, 0.34, 0.50), noise=0.0), M.paint(kit, D, 'sz_molepink', (0.98, 0.62, 0.66), noise=0.0), M.paint(kit, D, 'sz_moleeye', (0.04, 0.04, 0.06), noise=0.0),
                M.paint(kit, D, 'sz_soilball', (0.46, 0.30, 0.20), noise=0.0), M.paint(kit, D, 'sz_moleclaw', (0.99, 0.92, 0.80), noise=0.0)]
        self.body = pr.add(*sphere((0, 0, 0), (0.165, 0.100, 0.105), 2), m=0)
        self.head = pr.add(*sphere((0.150, 0, 0.015), (0.092, 0.075, 0.075), 2), m=0)
        self.snout = pr.add(*sphere((0.232, 0, 0.012), (0.050, 0.034, 0.034), 2), m=1)
        self.nose = pr.add(*sphere((0.278, 0, 0.016), (0.016, 0.016, 0.016), 1), m=1)
        self.eyes = [pr.add(*sphere((0.178, sd * 0.050, 0.050), (0.0075, 0.0075, 0.0075), 1), m=2) for sd in (1, -1)]
        self.paws = [pr.add(*sphere((0, 0, 0), (0.088, 0.016, 0.062), 2), m=1) for _ in range(2)]
        self.claws = [pr.add(*sphere((0.06, 0, 0.0), (0.020, 0.010, 0.016), 1), m=4) for _ in range(6)]
        self.tail = pr.add(*tube([(-0.150, 0, 0.0), (-0.200, 0, 0.020), (-0.230, 0, 0.012)], [0.014, 0.010, 0.006], 6), m=1)
        self.soil = [pr.add(*sphere((0, 0, 0), (0.016, 0.016, 0.016), 1), m=3) for _ in range(10)]
        pr.build(kit.bpy, mats, kit.coll)


def mole_s(t):
    """Arc length of the mole's nose along its tunnel (right to left, with a rest and a turn back)."""
    B = W.B; L = MOLE_PATH.L
    return L * float(W.keys(t, [(B.pop_mole, 0.12), (B.pop_mole + 4.0, 0.34), (14.25, 0.44), (22.15, 0.66), (27.6, 0.86), (30.0, 0.96), (30.4, 0.96)]))


def mole_x(t): return MOLE_PATH.at(mole_s(t))[0][0]


# ------------------------------------------------------------------ beetle grubs
class Grubs:
    def __init__(self, kit, D):
        mat = M.paint(kit, D, 'sz_grub', (0.99, 0.92, 0.70), noise=0.0)
        self.sw = [Sweep(kit, f'fs_grub{k}', [mat], 16, 8) for k in range(3)]
        pr = Parts('fs_grubheads'); m = [M.paint(kit, D, 'sz_grubhead', (0.74, 0.40, 0.18), noise=0.0), M.paint(kit, D, 'sz_grubeye', (0.06, 0.05, 0.08), noise=0.0)]
        self.heads = [pr.add(*sphere((0, 0, 0), (0.026, 0.024, 0.024), 2), m=0) for _ in range(3)]
        self.eyes = [[pr.add(*sphere((0, 0, 0), (0.0045, 0.0045, 0.0045), 1), m=1) for _ in range(2)] for _ in range(3)]
        pr.build(kit.bpy, m, kit.coll); self.pr = pr
        self.at = [(-1.50, -0.78, 0.0), (-1.30, -0.80, math.pi), (-1.10, -0.77, 0.4)]
    def pose(self, t, lift):
        B = W.B; show = pop_k(t, B.pop_grub) if t > B.pop_grub else 0.0
        for k in range(3):
            cx, cz, ph = self.at[k]; n = 16
            if show < 0.02: self.sw[k].hide(True); self.pr.hide(self.heads[k]); [self.pr.hide(e) for e in self.eyes[k]]; continue
            self.sw[k].hide(False); sc = show
            curl = 0.80 + 0.06 * math.sin(2 * math.pi * 0.5 * t + ph)
            ang = np.linspace(0.55 * math.pi, 0.55 * math.pi + 1.45 * math.pi * curl / 0.80, n); rc = 0.075 * sc
            P = np.array([(cx + rc * math.cos(a), Y_C, cz + rc * math.sin(a) + lift) for a in ang]); r = 0.042 * sc * (0.55 + 0.45 * np.sin(np.linspace(0.15, 3.1, n))) * (1 + 0.10 * np.cos(np.arange(n) * 2.4))
            r[0] *= 0.55; self.sw[k].set(P, r)
            tipd = P[-1] - P[-2]; tipd /= np.linalg.norm(tipd) + 1e-9
            bite = 0.012 * sc * abs(math.sin(2 * math.pi * 1.4 * t + ph))
            hp = P[-1] + tipd * 0.012 * sc + np.array([0, 0, 0.0]) + tipd * bite
            self.pr.set(self.heads[k], hp, I3, sc)
            for q, sd in enumerate((1, -1)): self.pr.set(self.eyes[k][q], hp + np.array([0.008 * sd, -0.019, 0.008]) * sc + tipd * 0.01 * sc, I3, sc)
        self.pr.commit()


# ------------------------------------------------------------------ build / pose
def build(kit, D, rng):
    S = {}
    S['flat'] = Flat(kit, D, rng)
    # ---- static things: roots, rootlets, rooms' eggs are in Ants; easter eggs
    pr = Parts('fs_ugstatic'); mats = [M.paint(kit, D, 'sz_root', (0.42, 0.28, 0.20), noise=0.0), M.paint(kit, D, 'sz_rootlet', (0.62, 0.46, 0.34), noise=0.0),
                                      M.paint(kit, D, 'sz_marble', (0.30, 0.55, 0.95), noise=0.0), M.paint(kit, D, 'sz_marble2', (0.96, 0.96, 0.99), noise=0.0),
                                      M.paint(kit, D, 'sz_coin', (1.0, 0.82, 0.24), noise=0.0), M.paint(kit, D, 'sz_coin2', (0.96, 0.66, 0.16), noise=0.0),
                                      M.paint(kit, D, 'sz_key', (0.92, 0.72, 0.22), noise=0.0), M.paint(kit, D, 'sz_chest', (0.64, 0.38, 0.22)), M.paint(kit, D, 'sz_chestband', (0.98, 0.78, 0.22), noise=0.0),
                                      M.paint(kit, D, 'sz_gnomebody', (0.72, 0.74, 0.78)), M.paint(kit, D, 'sz_gnomehat', (0.90, 0.22, 0.22), noise=0.0), M.paint(kit, D, 'sz_gnomebeard', (0.96, 0.96, 0.94), noise=0.0),
                                      M.paint(kit, D, 'sz_pebbleug', (0.62, 0.56, 0.52)), M.paint(kit, D, 'sz_carb', (0.20, 0.46, 0.86), noise=0.0), M.paint(kit, D, 'sz_wheel', (0.12, 0.12, 0.16), noise=0.0)]
    yR = FY - 0.012
    for nm, (pts, r0, r1) in ROOTS.items():
        C = PATH_ROOT[nm]; n = 12; ss = np.linspace(0, C.L, n); P3 = [(C.at(s)[0][0], yR, C.at(s)[0][1]) for s in ss]
        rad = [r0 + (r1 - r0) * (i / (n - 1)) ** 0.8 for i in range(n)]; v, f = tube(P3, rad, 8); S.setdefault('fixed', []).append(pr.add(v, f, 0))
    S['rootlets'] = []
    for (parent, u, ang, ln) in RootletsList:
        C = PATH_ROOT[parent]; p, d = C.at(u * C.L); a = math.radians(ang); dd = np.array([math.cos(a), math.sin(a)])
        pts = [(p[0] + dd[0] * ln * s + 0.02 * math.sin(6 * s), yR, p[1] + dd[1] * ln * s) for s in (0.0, 0.33, 0.66, 1.0)]
        v, f = tube(pts, [0.014, 0.011, 0.008, 0.004], 6); S['fixed'].append(pr.add(v, f, 1))
        S['rootlets'].append((p, dd, ln))
    # a rootlet down into the grubs' room
    v, f = tube([(-1.42, yR, -0.50), (-1.43, yR, -0.58), (-1.40, yR, -0.66)], [0.013, 0.011, 0.008], 6); S['fixed'].append(pr.add(v, f, 1))
    # easter eggs: marble (placed by pose), coin, key, chest, gnome, pebbles
    S['marble'] = [pr.add(*sphere((0, 0, 0), (0.034, 0.034, 0.034), 2), m=2), pr.add(*cone((0, 0, -0.004), 0.0345, 0.010, 20, 0.0345), m=3)]
    S['coin'] = [pr.add(*tube([(0, -0.002, 0), (0, 0.004, 0)], [0.052, 0.052], 18), m=4), pr.add(*tube([(0, -0.012, 0), (0, -0.004, 0)], [0.036, 0.036], 18), m=5)]
    # a key: ring, shaft, teeth
    ring = [(0.05 * math.cos(a), 0.0, 0.05 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 17)]
    S['key'] = [pr.add(*tube(ring, [0.011] * 17, 6, False), m=6), pr.add(*tube([(0.05, 0, 0), (0.24, 0, 0)], [0.012, 0.012], 6), m=6), pr.add(*box((0.20, 0, -0.025), (0.020, 0.012, 0.05)), m=6), pr.add(*box((0.23, 0, -0.020), (0.020, 0.012, 0.040)), m=6)]
    S['chest'] = [pr.add(*box((0, 0, 0.040), (0.220, 0.130, 0.080)), m=7), pr.add(*tube([(-0.11, 0, 0.080), (-0.055, 0, 0.125), (0.055, 0, 0.125), (0.11, 0, 0.080)], [0.058, 0.060, 0.060, 0.058], 10), m=7),
                  pr.add(*box((-0.06, -0.066, 0.045), (0.022, 0.008, 0.100)), m=8), pr.add(*box((0.06, -0.066, 0.045), (0.022, 0.008, 0.100)), m=8), pr.add(*box((0, -0.068, 0.062), (0.030, 0.010, 0.036)), m=8)]
    S['gnome'] = [pr.add(*sphere((0, 0, 0.065), (0.058, 0.050, 0.070), 2), m=9), pr.add(*sphere((0, -0.012, 0.145), (0.044, 0.042, 0.044), 2), m=9),
                  pr.add(*cone((0, -0.012, 0.165), 0.052, 0.140, 12, 0.0), m=10), pr.add(*sphere((0, -0.040, 0.118), (0.040, 0.020, 0.046), 2), m=11),
                  pr.add(*sphere((0.018, -0.052, 0.150), (0.007, 0.006, 0.007), 1), m=14), pr.add(*sphere((-0.018, -0.052, 0.150), (0.007, 0.006, 0.007), 1), m=14)]
    S['pebbles'] = [pr.add(*sphere((0, 0, 0), (0.05 * (1 + 0.3 * (k % 3)), 0.02, 0.035 * (1 + 0.2 * (k % 2))), 1), m=12) for k in range(10)]
    S['car'] = [pr.add(*box((0, 0, 0.012), (0.075, 0.036, 0.020)), m=13), pr.add(*box((-0.006, 0, 0.030), (0.036, 0.032, 0.018)), m=13)] + [pr.add(*tube([(wx, -0.021, 0.004), (wx, 0.021, 0.004)], [0.009, 0.009], 10), m=14) for wx in (-0.024, 0.024)]
    pr.build(kit.bpy, mats, kit.coll); S['static'] = pr
    # water drops rising in the roots (emission, with alpha)
    pd = Parts('fs_rootdrops'); S['drops'] = []
    drop = [(0, 0, 0.022), (0.010, 0, 0.0), (0, 0, -0.012), (-0.010, 0, 0.0)]
    for rn in ROOTS:
        for k in range(5): S['drops'].append((rn, pd.add(drop, [(0, 1, 2, 3)], 0), k / 5.0 + 0.02 * len(S['drops'])))
    for k in range(6): S['drops'].append(('puff', pd.add(drop, [(0, 1, 2, 3)], 0), 0.0))
    pd.build(kit.bpy, [M.mat_glow(kit, D, 'fs_dropm', (0.50, 0.86, 1.0), 2.4)], kit.coll, smooth=False)
    pd.ob.visible_shadow = False; S['dropparts'] = pd
    # warmth: a gold glow creeping down the face
    nx, nz = 24, 12; Vw = []; Ew = []
    for j in range(nz + 1):
        for i in range(nx + 1): Vw.append((-W.HX + W.SX * i / nx, FY - 0.0045, -1.05 * j / nz)); Ew.append(j / nz)
    Fw = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(nz) for i in range(nx)]
    m = cw._new_mat(kit.bpy, 'fs_warm'); g = cw.G(m.node_tree, kit)
    dz = g.attr('dz').outputs['Fac']; wf = D.val(g, 'warmf', -1.0); wa = D.val(g, 'warma', 0.0)
    a = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', dz, wf), 0.0), 5.0, clamp=True)), g.math('MULTIPLY', wa, 0.42))
    a = g.math('MULTIPLY', a, g.math('GREATER_THAN', wf, 0.0))
    em = g.node('ShaderNodeEmission', ins={'Color': cw.srgb((1.0, 0.80, 0.42)), 'Strength': 1.4}); M._alpha_out(g, em, g.math('MULTIPLY', a, g.math('GREATER_THAN', a, 0.0)))
    S['warm'] = cw.mk_mesh(kit.bpy, 'fs_warm', Vw, Fw, [m], None, False, kit.coll, {'dz': ('FLOAT', Ew)}); S['warm'].visible_shadow = False
    # inhabitants
    S['wormA'] = Worm(kit, D, 'fs_wormA', WORM_A, (0.98, 0.58, 0.62), (0.96, 0.46, 0.52), 0.0, 0.022)
    S['wormB'] = Worm(kit, D, 'fs_wormB', WORM_B, (0.96, 0.66, 0.50), (0.94, 0.50, 0.40), 2.0, 0.0125)
    S['ants'] = Ants(kit, D, rng); S['mole'] = Mole(kit, D); S['grubs'] = Grubs(kit, D)
    return S


def pose(S, D, t):
    B = W.B; lift = W.lift(t)
    S['flat'].pose(t, lift)
    D.set('tglow', W.keys(t, [(B.reveal0 - 0.05, 0.0), (B.reveal0 + 0.05, 1.0), (B.reveal0 + 1.4, 0.0)]) if B.reveal0 - 0.1 < t < B.reveal0 + 1.6 else 0.0)
    D.set('talpha', 1.0)
    # roots, easter eggs ride the lift
    pr = S['static']
    for ob in (pr.ob,): ob.location = (0.0, 0.0, lift)
    S['warm'].location = (0.0, 0.0, lift)
    S['dropparts'].ob.location = (0.0, 0.0, lift)
    # ---- the easter eggs (static parts positioned each frame)
    rt = sm(B.roots_on0, B.roots_on1, t)
    # marble rolls slowly in the worm's tunnel (left and right, slope), glints
    mx = 0.88 + 0.10 * math.sin(2 * math.pi * t / 9.0); mz = -0.665 + 0.0 + 0.02
    mk = pop_k(t, B.tun_worm1 + 0.4); R = ry(2 * math.pi * (mx / 0.21))
    pr.set(S['marble'][0], (mx, Y_C, mz), R, mk); pr.set(S['marble'][1], (mx, Y_C, mz), R @ rx(math.pi / 2), mk)
    ck = pop_k(t, B.tun_ant0 + 1.0, 0.5)
    for j in S['coin']: pr.set(j, (1.62, FY - 0.010, -0.605), rx(math.pi / 2) @ rz(0.0), ck * 1.35)
    for j in S['key']: pr.set(j, (-1.00, FY - 0.010, -0.955), ry(0.25) @ rz(0.0), pop_k(t, B.pop_grub + 0.8, 0.5) * 1.0)
    for j in S['chest']: pr.set(j, (-0.22, FY - 0.050, -0.96), rz(0.0) @ ry(0.12), pop_k(t, B.pop_grub + 0.4, 0.5) * 1.0)
    for j in S['fixed']: pr.set(j, (0.0, 0.0, 0.0), I3, 1.0)
    for j in S['gnome']: pr.set(j, (1.25, 0.45, 0.02), rz(0.5), 1.25)         # on the lawn: a stone garden figure with a pointed hat
    for k, j in enumerate(S['pebbles']):
        pk = [(-0.35, -0.90), (0.15, -0.94), (0.95, -0.92), (1.70, -0.40), (-1.70, -0.90), (-0.05, -0.20), (0.90, -0.15), (0.50, -0.10), (-1.0, -0.62), (1.62, -0.98)][k]
        pr.set(j, (pk[0], FY - 0.010, pk[1]), ry(0.4 * k), 1.0)
    for j in S['car']: pr.set(j, (W.HX - 0.012, 0.30, -0.046), I3, 1.0)
    pr.commit()
    # the key and coin glint: handled by a bright flicker through the drops parts? (a tiny gold star in dropparts is cheaper than another mesh)
    # ---- drops rising in the roots to the tree
    pd = S['dropparts']; sparks = 0
    for rn, j, ph in S['drops']:
        if rn == 'puff': pd.hide(j); continue
        C = PATH_ROOT[rn]; u = (ph + t * 0.20) % 1.0; s = C.L * (1 - u)       # from the tip up to the trunk
        p, d = C.at(s); a = rt * min(1.0, u * 6) * min(1.0, (1 - u) * 5)
        if a < 0.03: pd.hide(j); continue
        pd.set(j, (p[0], FY - 0.026, p[1]), I3, 1.1 * a)
    pd.commit()
    # ---- warmth down the face in the stir
    D.set('warmf', W.keys(t, [(B.warm0, 0.02), (B.warm1, 1.12)]) if B.warm0 <= t else -1.0); D.set('warma', W.win(t, B.warm0, B.up0 + 1.2, 0.8))
    # ---- worms
    lenA = 0.022 * 25 + 0.05; sA = lenA + (WORM_A.L - lenA) * (0.5 + 0.5 * math.sin(2 * math.pi * (t - B.pop_worm) / 11.0)); kA = pop_k(t, B.pop_worm)
    S['wormA'].pose(t, sA, kA, lift)
    lenB = 0.0125 * 25 + 0.05; sB = lenB + (WORM_B.L - lenB) * (0.5 + 0.5 * math.sin(2 * math.pi * (t - B.pop_worm - 1.0) / 8.0 + 1.0)); kB = pop_k(t, B.pop_worm + 0.35)
    S['wormB'].pose(t, sB, kB, lift)
    # ---- ants
    an = S['ants']; pr = an.pr; kk = lambda t0: pop_k(t, t0, 0.5)
    ants = an.ants
    # (0) the sandwich hauler: from the top, down the shaft, along the passage, into the pantry (the visual joke), repeats every 14 s
    T0 = B.pop_ant + 2.5; cyc = 14.0
    hauler = ants[0]; tt_ = (t - T0)
    if tt_ >= 0:
        ph = (tt_ % cyc) / cyc; walk_u = W.sm(0.0, 0.62, ph); L = ANT_ROUTE.L
        if ph < 0.62:
            p, d = ANT_ROUTE.at(L * walk_u); carrying = 1.0
        else:                                    # drops it in the pantry, then trots off back (left over the loop and up)
            p, d = ANT_ROUTE.at(L); carrying = 0.0
            back = W.sm(0.70, 0.98, ph); p2, d2 = ANT_ROUTE.at(L * (1 - back)); p = p2; d = -d2 if back > 0.01 else d
        on = 1.0 if ph < 0.99 else 0.0
        an.place(hauler, p, d, 1.0 * on * kk(T0 - 0.2), t, 0.0, lift, nod=0.15 if carrying else 0.0, lean=0.0)
        # the crumb: carried above its back (three times the ant's length), then lies in the pantry
        if ph < 0.62:
            R = face_frame(d[0], d[1]) @ ry(-0.12)
            up = np.array([0.0, 0.0, 0.085 * 1.0]); base = np.array([p[0], Y_C + 0.005, p[1] + lift + 0.030]) + R @ np.array([0.06, 0.0, 0.11])
            cr = 1.0
        else:
            base = np.array([0.56, Y_C + 0.005, -0.34 + lift - 0.085]); R = rz(0.0); cr = 1.0
    else:
        an.hide(hauler); base = np.array([0.0, 0.0, -50.0]); R = I3; cr = 0.0
    for j in an.sand + an.slab: pr.hide(j) if cr == 0.0 else None
    if cr:
        for j in an.sand: pr.hide(j)
        for j in an.slab: pr.set(j, base, R, 1.5)
    # (1..3) walkers pacing the passages in turns; (4,5) nurses by the eggs; (6) a worker with a seed; (7) the queen
    def pace(a, k, route, period, phase, t0, off=0.0, size=1.0):
        u = (((t - phase) / period) % 1.0); w = 0.5 - 0.5 * math.cos(2 * math.pi * u)         # there and back, easing at the turns
        p, d = route.at(route.L * w); sgn = 1.0 if (u < 0.5) else -1.0
        d = d * (sgn if True else 1.0) * (1 if abs(math.sin(2 * math.pi * u)) > 0.0 else 1)
        an.place(a, p + np.array([0.0, off]), d, size * kk(t0), t, phase, lift)
    pace(ants[1], 1, ANT_LOOP, 9.0, 0.0, B.pop_ant + 0.2, 0.012); pace(ants[2], 2, ANT_LOOP, 11.0, 5.0, B.pop_ant + 0.4, -0.012)
    pace(ants[3], 3, ANT_LOOP, 7.0, 2.5, B.pop_ant + 0.6, 0.0)
    # nurses: tend the eggs (bob toward the eggs)
    for q, (a, cx) in enumerate(((ants[4], 1.10), (ants[5], 1.50))):
        k_ = kk(B.pop_ant + 0.8 + 0.2 * q); fx = 1 if q == 0 else -1; bob = 0.014 * math.sin(2 * math.pi * 0.8 * t + q)
        an.place(a, np.array([cx, -0.405 + bob]), np.array([fx, 0.0]), k_, t, 1.0 + q, lift, nod=0.25 * math.sin(2 * math.pi * 0.8 * t + q))
    # a worker rolling a seed along the pantry floor
    p, d = Path([(0.34, -0.44), (0.78, -0.44)]).at(0.32 * (0.5 - 0.5 * math.cos(2 * math.pi * (t - 3.0) / 10.0))); an.place(ants[6], p, np.array([1.0, 0.0]), kk(B.pop_ant + 1.0), t, 3.0, lift)
    # the queen
    an.place(ants[7], np.array([1.30, -0.40]), np.array([-1.0, 0.0]), 1.5 * kk(B.pop_ant + 0.1), t, 0.0, lift, nod=0.04 * math.sin(2 * math.pi * 0.4 * t))
    for j, (cx, cz) in an.eggs: pr.set(j, (cx, Y_C + 0.004, cz + lift), I3, 1.5 * kk(B.pop_ant + 0.3))
    for k_, (j, (cx, cz)) in enumerate(an.larvae): pr.set(j, (cx, Y_C + 0.004, cz + lift + 0.004 * math.sin(2 * math.pi * 0.7 * t + k_)), rz(0.3 * math.sin(t + k_)), 1.5 * kk(B.pop_ant + 0.4))
    for j, (cx, cz) in an.crumbs: pr.set(j, (cx, Y_C + 0.004, cz + lift), I3, 1.5 * kk(B.pop_ant + 0.9))
    pr.commit()
    # ---- the mole
    ml = S['mole']; mp = ml.pr; ms = mole_s(t)
    if t < B.pop_mole: [mp.hide(j) for j in [ml.body, ml.head, ml.snout, ml.nose, ml.tail] + ml.eyes + ml.paws + ml.claws + ml.soil]
    else:
        k = 1.0; p, d = MOLE_PATH.at(ms); back = W.sm(30.0, 30.9, t) > 0.5 and False
        head_dir = np.array([-1.0, 0.0]); R = face_frame(d[0], d[1]) if False else rz(math.pi) @ ry(math.atan2(-d[1], -d[0]) * 0 + (0.0))
        slope = math.atan2(d[1], -d[0]) if d[0] < 0 else 0.0
        R = rz(math.pi) @ ry(0.0)
        base = np.array([p[0] + 0.20, Y_C - 0.02, p[1] + lift]) ; k = pop_k(t, B.pop_mole, 0.5) * 1.25
        dig = 2 * math.pi * 2.3 * t; moving = 1.0 if t < 30.2 else 0.0
        mp.set(ml.body, base, R, k); mp.set(ml.head, base, R, k); mp.set(ml.snout, base, R, k); mp.set(ml.nose, base, R, k); mp.set(ml.tail, base, R, k)
        for j in ml.eyes: mp.set(j, base, R, k)
        for q, j in enumerate(ml.paws):
            ang = 0.9 * math.sin(dig + q * math.pi) * moving
            pp = base + R @ (np.array([0.20, -0.075 + 0.0, -0.035 + 0.02 * (1 - q)]) * k)
            mp.set(j, pp, R @ ry(-0.35 + ang) @ rz(0.25 * (1 if q else -1)), k)
            for c in range(3): mp.set(ml.claws[3 * q + c], pp + R @ ry(-0.35 + ang) @ np.array([0.07 * k, -0.01 * k, (c - 1) * 0.028 * k]), R @ ry(-0.35 + ang), k)
        # soil thrown behind in arcs
        for q, j in enumerate(ml.soil):
            T_ = 1.1; age = ((t / T_ + q / 10.0) % 1.0); x0 = base[0] + 0.05; vx = 0.36 + 0.04 * (q % 3); z0 = base[2] + 0.02
            if not moving or age > 0.9: mp.hide(j); continue
            mp.set(j, (x0 + vx * age * 0.9, Y_C - 0.01, z0 + 0.20 * age - 0.30 * age * age), I3, 0.9 * (1 - age) * k)
    mp.commit()
    S['grubs'].pose(t, lift)
