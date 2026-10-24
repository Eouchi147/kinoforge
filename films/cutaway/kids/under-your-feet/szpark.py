"""Who lives under your feet? Everything alive on top of the lawn: the park (bpy + numpy). Every pose is a pure function of t.

  lawn            grass and daisies that follow the seasons (green, gold, thin frost, green again)
  the big tree    a trunk, bare branches and a crown that leafs out in spring, turns gold in autumn, falls in winter; leaves
                  drift down in autumn; a kite is stuck in it; a bike leans on it; the cicadas climb it
  the people      a girl in red shoes and a boy dribbling a red ball cross the lawn (their steps are why the first beat reads
                  "feet"), a dog follows; they look, point, dance and one lies with an ear to the grass at the end
  the picnic      a gingham blanket, a basket, sandwiches, an apple, a teddy bear
  easter eggs     (on top) the red ball, a bike, a kite in the tree, a teddy on the blanket; the snail mascot on a leaf at the
                  front right corner (series mascot, hidden in every film), who waves at the end
  the playground  a swing swinging and a slide, on the land beside the lifted slice
Generic everyday things only: no brand, no character.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, disc, quad, rz, ry, rx, euler, I3

TOP = W.top_h


def gz(x, y, t):
    return float(TOP(np.array([x]), np.array([y]), t)[0])


def path_at(P, u):
    P = np.asarray(P, float); seg = np.linalg.norm(np.diff(P, axis=0), axis=1); c = np.concatenate([[0], np.cumsum(seg)])
    s = float(np.clip(u, 0, 1)) * c[-1]; i = min(int(np.searchsorted(c, s, 'right')) - 1, len(seg) - 1); f = (s - c[i]) / max(seg[i], 1e-9)
    p = P[i] + (P[i + 1] - P[i]) * f; d = P[i + 1] - P[i]
    return p, math.atan2(d[1], d[0])


def _ell(c, r, sub=1): return sphere(c, r, sub)


def lumpy_ball(c, r, seed, sub=2, amp=0.18):
    V, F = cw._icosphere(sub); V = cw._lumpy(V, seed, amp, 2.6, 0.06, 7.0); return V * np.asarray(r, float) + np.asarray(c, float), F


def tau(t):
    """The people's clock: it runs ahead of the film's during the years, so they zip past while the seasons whirl."""
    return float(t) + 4.0 * (W.years(t) - W.Y_SUMMER)


# ------------------------------------------------------------------ the big tree
TX, TY = W.TX, W.TY            # where the trunk stands on the lawn
TREE_H = 0.62                  # trunk height to the crown
CROWN = (0.0, 0.0, 0.84)       # crown centre, relative to the trunk base
CROWN_R = 0.40
BRANCHES = [(0.22, 0.0, 0.50), (-0.20, 0.05, 0.56), (0.02, 0.26, 0.60), (0.04, -0.24, 0.58)]        # tips (x, y, z) relative to the base


def trunk_r(z):
    return 0.075 - 0.030 * min(1.0, max(0.0, z) / 0.70)


# ------------------------------------------------------------------ lawn
def world_pts(rng, step, rmax, rmin=0.0):
    """Jittered points on the land around the block (not on it), from rmin to rmax metres away."""
    xs = np.arange(-W.HX - rmax, W.HX + rmax, step); ys = np.arange(-W.HY - rmax, W.HY + rmax, step)
    X, Y = np.meshgrid(xs, ys); P = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.5, 0.5, (X.size, 2)) * step
    d = np.hypot(np.maximum(np.abs(P[:, 0]) - W.HX, 0), np.maximum(np.abs(P[:, 1]) - W.HY, 0))
    ok = ~W.in_hole(P[:, 0], P[:, 1]) & (d <= rmax) & (d >= rmin)
    ok &= rng.uniform(0, 1, len(P)) < np.clip(1.15 - d / rmax, 0.15, 1.0)
    return P[ok]


def behind(P, margin=-0.6):
    """Keep points that are not between the camera and the block (tall things there would wall off the view)."""
    return P[W.depth_s(P[:, 0], P[:, 1]) > float(min(W.depth_s(np.array([-W.HX, W.HX]), np.array([-W.HY, -W.HY])))) - margin]


def build_lawn(kit, L, D, rng):
    out = {}
    pal = dict(cw.SEASONS['summer'])
    gm = M.paint(kit, D, 'sz_grass', (0.44, 0.70, 0.30), noise=0.0, drive='grasscol')
    tufts = cw.proto_tufts(kit, pal, 6, 0.06, 7, (8, 13))
    for o in tufts: o.data.materials[0] = gm
    xs = np.arange(-W.HX + 0.02, W.HX - 0.01, 0.034); X, Y = np.meshgrid(xs, np.arange(-W.HY + 0.02, W.HY - 0.01, 0.034))
    Q = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.016, 0.016, (X.size, 2))
    Q = Q[(np.abs(Q) < [W.HX - 0.006, W.HY - 0.006]).all(1)]
    # keep the mat of the picnic blanket and the nymph's hole clear
    Q = Q[~((np.abs(Q[:, 0] - BLANKET[0]) < 0.36) & (np.abs(Q[:, 1] - BLANKET[1]) < 0.29))]
    Q = Q[np.hypot(Q[:, 0] - HOLE_XY[0], Q[:, 1] - HOLE_XY[1]) > 0.075]
    Qw = world_pts(rng, 0.05, 1.8); Q = np.vstack([Q, Qw]); n = len(Q)
    sc = rng.uniform(0.7, 1.3, n)
    ob = L.scatter('sz_grass', tufts, Q, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 6, n), sway=0.22, speed=0.9, z=0.0)
    out['grass'] = (ob, Q, sc, rng.uniform(0, 0.4, n))
    fl = cw.proto_flowers(kit, 5, 7)
    R = rng.uniform([-W.HX + 0.05, -W.HY + 0.05], [W.HX - 0.05, W.HY - 0.05], (240, 2))
    R = R[~((np.abs(R[:, 0] - BLANKET[0]) < 0.38) & (np.abs(R[:, 1] - BLANKET[1]) < 0.31))]
    Rw = world_pts(rng, 0.16, 2.2); R = np.vstack([R, Rw]); n = len(R)
    sc = rng.uniform(0.9, 1.5, n)
    ob = L.scatter('sz_flowers', fl, R, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 5, n), sway=0.18, speed=0.9, z=0.0)
    out['flowers'] = (ob, R, sc, rng.uniform(0.2, 0.7, n))
    return out


def _set_pts(ob, P, z, sc):
    me = ob.data; co = np.column_stack([P, z]).astype(np.float32)
    me.vertices.foreach_set('co', co.ravel()); me.attributes['scale'].data.foreach_set('value', np.asarray(sc, np.float32)); me.update()


def lawn_pose(lw, D, t):
    w = W.weights(t); wi = float(w[3])
    D.setc('grasscol', tuple(float(sum(wi_ * np.asarray(c, float) for wi_, c in zip(w, ((0.50, 0.82, 0.32), (0.40, 0.72, 0.28), (0.78, 0.68, 0.24), (0.84, 0.92, 0.95))))[j]) for j in range(3)))
    for key, rate in (('grass', 1.0), ('flowers', 1.0)):
        ob, Q, sc, d = lw[key]
        k = 1.0 - (0.78 if key == 'grass' else 0.97) * wi - 0.25 * float(w[2]) * (key == 'flowers')      # frosted stubble in winter; the daisies sleep
        _set_pts(ob, Q, TOP(Q[:, 0], Q[:, 1], t) - 0.004, sc * max(k, 0.0))


# ------------------------------------------------------------------ the tree
def build_tree(kit, D):
    pr = Parts('fs_bigtree')
    mats = [M.paint(kit, D, 'sz_bark', (0.46, 0.30, 0.24), noise=0.0), M.paint(kit, D, 'sz_leaf', (0.30, 0.64, 0.30), noise=0.0, drive='leafcol'),
            M.paint(kit, D, 'sz_leaf2', (0.40, 0.72, 0.34), noise=0.0, drive='leafcol2'), M.paint(kit, D, 'sz_fall', (0.90, 0.46, 0.16), noise=0.0)]
    ids = {}
    z = np.linspace(0, TREE_H + 0.10, 6)
    v, f = tube([(0, 0, -0.02)] + [(0.012 * math.sin(2 * zi), 0.008 * math.cos(3 * zi), zi) for zi in z[1:]], [trunk_r(0)] + [trunk_r(zi) for zi in z[1:]], 12)
    ids['trunk'] = pr.add(v, f, 0)
    ids['br'] = []
    for k, (bx, by, bz) in enumerate(BRANCHES):
        p0 = (0.0, 0.0, 0.34 + 0.05 * k); p1 = (bx * 0.5, by * 0.5, (0.34 + 0.05 * k + bz) / 2 + 0.03); p2 = (bx, by, bz)
        v, f = tube([p0, p1, p2], [0.030, 0.022, 0.010], 8); ids['br'].append(pr.add(v, f, 0))
    ids['crown'] = []
    rng = np.random.default_rng(41)
    for k, c in enumerate([(0, 0, 0.0), (-0.28, 0.10, -0.08), (0.28, -0.10, -0.06), (0.08, 0.30, -0.04), (-0.08, -0.30, -0.06), (0.0, 0.0, 0.24), (-0.22, -0.12, 0.14), (0.22, 0.14, 0.12)]):
        r = CROWN_R * rng.uniform(0.62, 0.86); cc = (CROWN[0] + c[0], CROWN[1] + c[1], CROWN[2] + c[2])
        v, f = lumpy_ball(cc, (r, r, r * 0.86), 200 + k); ids['crown'].append((pr.add(v, f, 1 + k % 2), cc))
    ids['leaves'] = []
    for k in range(16):
        v = [(-0.02, 0, 0), (0.0, 0.02, 0), (0.02, 0, 0), (0.0, -0.02, 0), (0, 0, 0.0)]; ids['leaves'].append((pr.add(v, [(0, 1, 2, 3)], 3), rng.uniform(0, 1), rng.uniform(0, 6.28), rng.uniform(-0.45, 0.45, 2)))
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'ids': ids}


def tree_pose(Tr, D, t):
    w = W.weights(t); pr = Tr['parts']; ids = Tr['ids']
    sp, su, au, wi = [float(x) for x in w]
    la = 1.0 * (sp * 0.88 + su + au * 0.80) + 0.0 * wi       # how much crown there is (none in winter)
    if wi > 0.02: la = la * (1 - wi)
    D.setc('leafcol', tuple(float(sum(wk * np.asarray(c, float) for wk, c in zip(w, ((0.46, 0.78, 0.38), (0.24, 0.62, 0.28), (0.92, 0.50, 0.14), (0.60, 0.70, 0.60))))[j]) for j in range(3)))
    D.setc('leafcol2', tuple(float(sum(wk * np.asarray(c, float) for wk, c in zip(w, ((0.62, 0.86, 0.40), (0.38, 0.72, 0.30), (0.98, 0.70, 0.18), (0.70, 0.78, 0.70))))[j]) for j in range(3)))
    base = np.array([TX, TY, gz(TX, TY, t) - 0.01]); sway = euler(0.012 * math.sin(0.9 * t), 0.010 * math.cos(0.7 * t), 0.0)
    pr.set(ids['trunk'], base, I3)
    for j in ids['br']: pr.set(j, base, I3)
    for j, cc in ids['crown']:
        if la < 0.02: pr.hide(j)
        else: pr.set(j, base + np.array(cc) * (1 - la) * 0.0 + (np.array(cc) - np.array(cc)) , sway, la)
    # the crown shrinks about its own centre: set with pivot offset (parts were built around the origin of the tree base)
    for j, cc in ids['crown']:
        if la >= 0.02:
            c = np.array(cc); pr.set(j, base + c * (1 - la), sway, la)
    # leaves drift down in autumn from the crown, and lie on the lawn
    for j, ph, spin, dxy in ids['leaves']:
        a = float(au) * (1 - 0.0)
        if a < 0.25 or la < 0.1: pr.hide(j); continue
        T_ = 3.4; age = ((t / T_ + ph) % 1.0); z0 = base[2] + 0.60; z1 = base[2] + 0.01
        x = base[0] + dxy[0] * 1.6 * (0.4 + age) + 0.06 * math.sin(2.1 * t + spin); y = base[1] + dxy[1] * 1.6 * (0.4 + age)
        z = z0 + (z1 - z0) * age
        if abs(x) > W.HX - 0.03 or abs(y) > W.HY - 0.03: pr.hide(j); continue
        pr.set(j, (x, y, z), euler(1.0 * math.sin(3 * t + spin), 0.8 * math.cos(2 * t + spin), spin + t), a)
    pr.commit()


# ------------------------------------------------------------------ props: picnic, bike, kite, teddy, ball, the snail
BLANKET = (0.62, 0.20)         # centre of the picnic blanket
HOLE_XY = W.HOLE_XY
BIKE = (-1.52, -0.22)
KITE_P = (TX + 0.10, TY - 0.20, 0.64)
SNAIL_HOME = (1.38, -W.HY + 0.10)
SK = 2.8


def build_props(kit, D):
    pr = Parts('fs_props')
    mats = [M.paint(kit, D, 'sz_blanket', (0.92, 0.30, 0.28), noise=0.0), M.paint(kit, D, 'sz_blanket2', (0.99, 0.96, 0.90), noise=0.0),
            M.paint(kit, D, 'sz_basket', (0.80, 0.56, 0.30)), M.paint(kit, D, 'sz_bread', (0.96, 0.80, 0.50), noise=0.0),
            M.paint(kit, D, 'sz_filling', (0.60, 0.80, 0.30), noise=0.0), M.paint(kit, D, 'sz_cheese', (1.0, 0.84, 0.20), noise=0.0),
            M.paint(kit, D, 'sz_apple', (0.90, 0.16, 0.14), noise=0.0), M.paint(kit, D, 'sz_teddy', (0.78, 0.52, 0.28)),
            M.paint(kit, D, 'sz_teddy2', (0.96, 0.84, 0.66), noise=0.0), M.paint(kit, D, 'sz_bikeframe', (0.20, 0.50, 0.90), noise=0.0),
            M.paint(kit, D, 'sz_biketyre', (0.14, 0.14, 0.18), noise=0.0), M.paint(kit, D, 'sz_bikeseat', (0.96, 0.62, 0.16), noise=0.0),
            M.paint(kit, D, 'sz_kite', (0.98, 0.42, 0.40), noise=0.0), M.paint(kit, D, 'sz_kite2', (0.99, 0.82, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_dockleaf', (0.30, 0.64, 0.26), noise=0.0), M.paint(kit, D, 'sz_bottle', (0.50, 0.86, 0.96), noise=0.0),
            M.paint(kit, D, 'sz_hole2', (0.10, 0.06, 0.06), noise=0.0), M.paint(kit, D, 'sz_hill', (0.40, 0.28, 0.20))]
    e = {}
    # blanket: red and white squares (a 5 by 4 chequer)
    e['blanket'] = []
    for i in range(5):
        for j in range(4):
            e['blanket'].append(pr.add(*box(((i - 2) * 0.14, (j - 1.5) * 0.14, 0.0), (0.139, 0.139, 0.006)), m=(i + j) % 2))
    # basket with a handle, two sandwiches (bread, green filling, cheese), an apple, a bottle, and a teddy sitting on the blanket
    e['basket'] = [pr.add(*box((0, 0, 0.040), (0.17, 0.12, 0.08)), m=2), pr.add(*tube([(-0.075, 0, 0.08), (-0.05, 0, 0.15), (0.0, 0, 0.17), (0.05, 0, 0.15), (0.075, 0, 0.08)], [0.007] * 5, 6), m=2)]
    e['sand'] = []
    for k in range(2):
        e['sand'] += [pr.add(*box((0, 0, 0.000), (0.10, 0.10, 0.012)), m=3), pr.add(*box((0, 0, 0.010), (0.098, 0.098, 0.008)), m=4), pr.add(*box((0, 0, 0.018), (0.09, 0.09, 0.006)), m=5),
                      pr.add(*box((0, 0, 0.026), (0.10, 0.10, 0.012)), m=3)]
    e['apple'] = [pr.add(*_ell((0, 0, 0.025), (0.026, 0.026, 0.026), 2), m=6)]
    e['bottle'] = [pr.add(*tube([(0, 0, 0), (0, 0, 0.12)], [0.026, 0.026], 10), m=15), pr.add(*tube([(0, 0, 0.12), (0, 0, 0.17)], [0.012, 0.010], 8), m=15)]
    e['teddy'] = [pr.add(*_ell((0, 0, 0.034), (0.030, 0.028, 0.034), 2), m=7), pr.add(*_ell((0.004, 0, 0.082), (0.024, 0.024, 0.022), 2), m=7),
                  pr.add(*_ell((0.002, 0.020, 0.100), (0.009, 0.004, 0.009), 1), m=7), pr.add(*_ell((0.002, -0.020, 0.100), (0.009, 0.004, 0.009), 1), m=7),
                  pr.add(*_ell((0.022, 0, 0.078), (0.010, 0.012, 0.009), 1), m=8), pr.add(*_ell((0.018, 0, 0.036), (0.014, 0.020, 0.020), 1), m=8),
                  pr.add(*_ell((0.022, 0.024, 0.008), (0.018, 0.010, 0.010), 1), m=7), pr.add(*_ell((0.022, -0.024, 0.008), (0.018, 0.010, 0.010), 1), m=7),
                  pr.add(*_ell((0.0, 0.032, 0.046), (0.010, 0.010, 0.020), 1), m=7), pr.add(*_ell((0.0, -0.032, 0.046), (0.010, 0.010, 0.020), 1), m=7)]
    # the bike: two wheels, a frame, handlebars, a seat (leaning on the big tree's side)
    def wheel(cx):
        pts = [(cx + 0.15 * math.cos(a), 0.0, 0.15 + 0.15 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)]
        return pr.add(*tube(pts, [0.011] * 25, 6, False), m=10)
    e['bike'] = [wheel(-0.26), wheel(0.26),
                 pr.add(*tube([(-0.26, 0, 0.15), (-0.06, 0, 0.17), (0.12, 0, 0.30)], [0.009] * 3, 6), m=9), pr.add(*tube([(0.26, 0, 0.15), (0.14, 0, 0.30), (0.12, 0, 0.30), (-0.06, 0, 0.17)], [0.009] * 4, 6), m=9),
                 pr.add(*tube([(0.14, 0, 0.30), (0.20, 0, 0.36), (0.23, 0.07, 0.38)], [0.008] * 3, 6), m=9), pr.add(*tube([(0.20, 0, 0.36), (0.23, -0.07, 0.38)], [0.008] * 2, 6), m=9),
                 pr.add(*box((-0.08, 0, 0.30), (0.09, 0.04, 0.02)), m=11), pr.add(*tube([(-0.06, 0, 0.17), (-0.08, 0, 0.29)], [0.008] * 2, 6), m=9)]
    # kite stuck in the tree
    k1 = pr.add([(0, 0, 0.09), (0.05, 0, 0.0), (0, 0, -0.05), (0, 0.0005, 0.0)], [(0, 1, 2), (0, 2, 3)], m=12)
    k2 = pr.add([(0, -0.0005, 0.09), (-0.05, -0.0005, 0.0), (0, -0.0005, -0.05)], [(0, 1, 2)], m=13)
    tail = [pr.add([(-0.012, 0, 0.0), (0.012, 0, 0.008), (0.012, 0, -0.008), (-0.012, 0, 0.0)], [(0, 1, 2)], m=13 - i % 2) for i in range(5)]
    e['kite'] = (k1, k2, tail)
    # the nymph's hole in the lawn (a dark oval with a rim of crumbs) and a molehill (grows when the mole pushes up)
    e['hole'] = [pr.add(*disc((0, 0, 0.0), 0.058, 20), m=16), pr.add(*cone((0, 0, 0.0), 0.085, 0.006, 18, 0.062), m=17)]
    e['molehill'] = pr.add(*cone((0, 0, 0.0), 0.16, 0.10, 16, 0.02), m=17)
    # the snail's big leaf
    e['dock'] = pr.add(*_ell((0, 0, 0.006), (0.11, 0.075, 0.008), 2), m=14)
    pr.build(kit.bpy, mats, kit.coll)
    # the snail (series mascot)
    sn = Parts('fs_snail')
    smats = [M.paint(kit, D, 'sz_snailshell', (0.96, 0.52, 0.40), noise=0.0), M.paint(kit, D, 'sz_snailband', (0.99, 0.82, 0.38), noise=0.0),
             M.paint(kit, D, 'sz_snailbody', (0.86, 0.84, 0.66), noise=0.0), M.paint(kit, D, 'sz_snaileye', (0.10, 0.10, 0.18), noise=0.0)]
    s = {'shell': sn.add(*sphere((0, 0, 0.030), (0.026, 0.017, 0.028), 2), m=0), 'band': sn.add(*sphere((0.0, 0, 0.030), (0.016, 0.0185, 0.018), 2), m=1),
         'body': sn.add(*sphere((0.012, 0, 0.007), (0.040, 0.012, 0.008), 2), m=2)}
    s['stalks'] = [sn.add(*tube([(0, 0, 0), (0.004, sd * 0.004, 0.022)], [0.0025, 0.0018], 5), m=2) for sd in (-1, 1)]
    s['eyes'] = [sn.add(*sphere((0.004, sd * 0.004, 0.024), (0.0035, 0.0035, 0.0035), 1), m=3) for sd in (-1, 1)]
    sn.build(kit.bpy, smats, kit.coll)
    return {'parts': pr, 'e': e, 'snail': sn, 's': s}


def props_pose(Pp, D, t):
    pr = Pp['parts']; e = Pp['e']; B = W.B; lf = W.lift(t)
    # blanket and picnic
    bz = gz(BLANKET[0], BLANKET[1], t) + 0.004
    for k, j in enumerate(e['blanket']):
        i, jj = divmod(k, 4); pr.set(j, (BLANKET[0] + (i - 2) * 0.14, BLANKET[1] + (jj - 1.5) * 0.14, bz), I3)
    def put(j, p, R=None, s=1.0): pr.set(j, p, R, s)
    bx, by = BLANKET
    for j in e['basket']: put(j, (bx - 0.18, by + 0.10, bz + 0.003), rz(0.3), 1.2)
    for k in range(2):
        for q, j in enumerate(e['sand'][4 * k:4 * k + 4]): put(j, (bx + 0.06 + 0.10 * k, by - 0.12 + 0.04 * k, bz + 0.006), rz(0.2 + 0.7 * k), 1.0)
    put(e['apple'][0], (bx + 0.14, by + 0.12, bz + 0.003), I3, 1.2)
    for j in e['bottle']: put(j, (bx + 0.28, by + 0.02, bz + 0.003), I3, 1.0)
    # the teddy sits on the blanket, and takes a little bow at the end
    bow = 0.35 * W.win(t, B.final, B.final + 3.5, 0.5) * math.sin(2 * math.pi * 0.7 * (t - B.final))
    for j in e['teddy']: put(j, (bx - 0.02, by + 0.02, bz + 0.003), rz(-1.2) @ ry(bow), 1.6)
    # the bike leans against the big tree's neighbour: parked on the lawn at an angle
    gzb = gz(BIKE[0], BIKE[1], t)
    for j in e['bike']: put(j, (BIKE[0], BIKE[1], gzb + 0.002), rz(0.4) @ rx(-0.20), 1.0)
    # kite in the tree, tugging in the wind (lives in the crown while it is there)
    k1, k2, tail = e['kite']; tug = 0.22 * math.sin(2 * math.pi * 0.7 * t) + 0.08 * math.sin(2 * math.pi * 1.9 * t)
    Rk = rz(-1.0) @ rx(0.35 + tug) @ ry(0.3); la = float(W.weights(t)[3]); vis = 1.0
    kp = (KITE_P[0], KITE_P[1], KITE_P[2] + gz(TX, TY, t)); put(k1, kp, Rk, 1.5); put(k2, kp, Rk, 1.5)
    base = np.array(kp) + Rk @ np.array([0, 0, -0.075])
    for i, j in enumerate(tail):
        sw = 0.03 * math.sin(2 * math.pi * 0.7 * t - 0.6 * i) * (i + 1) / 5
        put(j, base + np.array([sw, 0.0, -0.05 * (i + 1)]), rz(-1.0) @ rx(tug * 0.5), 1.5)
    # the nymph's hole (dark oval) on the lawn; the molehill rises when the mole pushes up (UG sets it through Pp['mole_k'])
    hz = gz(HOLE_XY[0], HOLE_XY[1], t)
    put(e['hole'][0], (HOLE_XY[0], HOLE_XY[1], hz + 0.0035), I3, 1.0); put(e['hole'][1], (HOLE_XY[0], HOLE_XY[1], hz + 0.0005), I3, 1.0)
    import szunder as UG
    mk = UG.mole_hill_k(t)
    MH = (1.62, -0.70)
    if mk > 0.01: put(e['molehill'], (MH[0], MH[1], gz(MH[0], MH[1], t)), I3, (mk, mk, mk))
    else: pr.hide(e['molehill'])
    pr.hide(e['dock']) if False else put(e['dock'], (SNAIL_HOME[0], SNAIL_HOME[1], gz(SNAIL_HOME[0], SNAIL_HOME[1], t) + 0.001), rz(0.4), 1.5)
    pr.commit()
    # the snail waves
    sn = Pp['snail']; s = Pp['s']
    x, y = SNAIL_HOME; p = np.array([x, y, gz(x, y, t) + 0.016]); hdg = -math.pi / 2 + 0.55
    hide = max(W.win(t, B.pop0 - 0.1, B.pop0 + 1.2, 0.3), 0.0)
    up = 1 + 0.6 * W.win(t, B.open0, B.open0 + 3.0, 0.3) + 0.6 * W.win(t, B.pop0, B.pop0 + 1.5, 0.3)
    wave = W.sm(B.wave0, B.wave0 + 0.4, t) * 0.7 * math.sin(2 * math.pi * 1.6 * t)
    out = 1 - 0.0 * hide; R = rz(hdg)
    sn.set(s['shell'], p, R, SK); sn.set(s['band'], p, R, SK); sn.set(s['body'], p, R, (SK, SK, SK))
    head = p + R @ (np.array([0.040, 0, 0.010]) * SK)
    for j, ph in zip(s['stalks'] + s['eyes'], (0, 1, 0, 1)):
        wob = rx(0.25 * math.sin(2 * math.pi * 0.5 * t + ph) + wave * (1 if ph == 0 else -1))
        sn.set(j, head, R @ wob, (SK, SK, up * SK))
    sn.commit()


# ------------------------------------------------------------------ the people: a girl, a boy, a ball, a dog
KID = {'girl': dict(dress=(0.98, 0.78, 0.18), shoe=(0.92, 0.14, 0.14), skin=(0.62, 0.42, 0.30), hair=(0.20, 0.12, 0.10), top=(0.30, 0.66, 0.78)),
       'boy': dict(dress=(0.28, 0.46, 0.86), shoe=(0.98, 0.84, 0.12), skin=(0.86, 0.66, 0.50), hair=(0.62, 0.34, 0.14), top=(0.92, 0.36, 0.30))}
GK = 1.8


def build_kids(kit, D):
    pr = Parts('fs_kids'); out = {}
    for name, c in KID.items():
        mats = [M.paint(kit, D, f'sz_{name}_dress', c['dress'], noise=0.0), M.paint(kit, D, f'sz_{name}_shoe', c['shoe'], noise=0.0), M.paint(kit, D, f'sz_{name}_skin', c['skin'], noise=0.0),
                M.paint(kit, D, f'sz_{name}_hair', c['hair'], noise=0.0), M.paint(kit, D, f'sz_{name}_top', c['top'], noise=0.0), M.paint(kit, D, f'sz_{name}_sock', (0.99, 0.97, 0.92), noise=0.0)]
        o = len(pr.V)
        g = {}
        # the kit's materials are per Parts; give each kid its own set of material slots by an offset (pieces carry m = 6 * k + i)
        out[name] = g; g['mats'] = mats
    # one Parts mesh with 12 materials
    pr = Parts('fs_kids'); allm = []; g2 = {}
    for ki, (name, c) in enumerate(KID.items()):
        mats = out[name]['mats']; allm += mats; off = 6 * ki; g = {}
        g['legL'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.085)], [0.013, 0.012], 8), m=off + 5); g['legR'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.085)], [0.013, 0.012], 8), m=off + 5)
        g['shoeL'] = pr.add(*_ell((0.014, 0, -0.098), (0.030, 0.017, 0.016), 1), m=off + 1); g['shoeR'] = pr.add(*_ell((0.014, 0, -0.098), (0.030, 0.017, 0.016), 1), m=off + 1)
        g['skirt'] = pr.add(*cone((0, 0, 0.0), 0.056 if ki == 0 else 0.046, 0.10, 16, 0.032), m=off + 0)
        g['torso'] = pr.add(*_ell((0, 0, 0.125), (0.034, 0.040, 0.040), 2), m=off + 4)
        g['head'] = pr.add(*_ell((0, 0, 0.200), (0.042, 0.042, 0.044), 2), m=off + 2)
        g['hair'] = pr.add(*_ell((-0.010, 0, 0.208), (0.042, 0.045, 0.042), 2), m=off + 3)
        g['armL'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.08)], [0.011, 0.010], 6), m=off + 2); g['armR'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.08)], [0.011, 0.010], 6), m=off + 2)
        g2[name] = g
    pr.build(kit.bpy, allm, kit.coll)
    # the red ball with a white band and the dog
    pb = Parts('fs_ball'); mb = [M.paint(kit, D, 'sz_ball', (0.92, 0.18, 0.16), noise=0.0), M.paint(kit, D, 'sz_ballw', (0.99, 0.96, 0.90), noise=0.0)]
    ball = [pb.add(*sphere((0, 0, 0), (0.036, 0.036, 0.036), 2), m=0), pb.add(*cone((0, 0, -0.006), 0.0372, 0.012, 20, 0.0372), m=1)]
    pb.build(kit.bpy, mb, kit.coll)
    pd = Parts('fs_dog')
    dm = [M.paint(kit, D, 'sz_dog', (0.86, 0.60, 0.32)), M.paint(kit, D, 'sz_dogdark', (0.36, 0.22, 0.16), noise=0.0), M.paint(kit, D, 'sz_stick', (0.56, 0.40, 0.26), noise=0.0)]
    dg = {'body': pd.add(*_ell((0, 0, 0.060), (0.062, 0.030, 0.030), 2), m=0), 'head': pd.add(*_ell((0.0, 0, 0.0), (0.026, 0.022, 0.022), 2), m=0),
          'snout': pd.add(*_ell((0.026, 0, -0.006), (0.016, 0.012, 0.011), 1), m=0), 'nose': pd.add(*_ell((0.042, 0, -0.004), (0.005, 0.005, 0.005), 1), m=1),
          'earL': pd.add(*_ell((-0.006, 0.020, 0.004), (0.010, 0.005, 0.016), 1), m=1), 'earR': pd.add(*_ell((-0.006, -0.020, 0.004), (0.010, 0.005, 0.016), 1), m=1),
          'tail': pd.add(*tube([(0, 0, 0), (-0.02, 0, 0.02), (-0.03, 0, 0.04)], [0.006, 0.005, 0.003], 6), m=0),
          'legs': [pd.add(*tube([(0, 0, 0), (0, 0, -0.045)], [0.008, 0.007], 6), m=0) for _ in range(4)]}
    pd.build(kit.bpy, dm, kit.coll)
    return {'parts': pr, 'g': g2, 'ball': pb, 'ball_ids': ball, 'dog': pd, 'dg': dg}


GIRL_PATH = [(-1.62, 0.32), (-1.0, 0.55), (-0.2, 0.62), (0.7, 0.70), (1.45, 0.30), (1.62, -0.30), (1.1, -0.70), (0.3, -0.62), (-0.40, -0.40), (-0.9, 0.0), (-1.62, 0.32)]
BOY_PATH = [(1.55, 0.45), (0.9, 0.25), (0.15, -0.20), (-0.35, -0.75), (-0.05, -0.25), (0.6, 0.5), (1.55, 0.45)]
BALL_R = 0.036 * 1.6


def _kid_pose(pr, g, p, yaw, walk_amt, ph, t, lift_z, arms=None, k=GK, tilt=None, pop=1.0, lying=0.0):
    """A child: root at the feet. `arms` = (angL, angR) raise (0 down, pi up) or None for swinging with the steps."""
    R0 = rz(yaw)
    if lying > 0.0: R0 = R0 @ ry(-lying * 1.50)
    sw = math.sin(ph) * walk_amt; bob = 0.012 * abs(math.sin(ph)) * walk_amt
    root = np.array([p[0], p[1], p[2] + (0.090 + bob) * k * pop])
    if lying > 0.0: root = np.array([p[0], p[1], p[2] + (0.045 + 0.050 * (1 - lying)) * k])
    lean = 0.0 if tilt is None else tilt
    Rb = R0 @ ry(lean)
    for kk, sd, sg in (('legL', 1, 1.0), ('legR', -1, -1.0)):
        hip = root + R0 @ np.array([0, sd * 0.020 * k, 0.0]); Rl = R0 @ ry(0.55 * sw * sg)
        pr.set(g[kk], hip, Rl, k); pr.set(g['shoe' + kk[-1]], hip, Rl, k)
    for kk in ('skirt', 'torso', 'head', 'hair'): pr.set(g[kk], root, Rb, k)
    sh = lambda sd: root + Rb @ (np.array([0.0, sd * 0.042, 0.140]) * k)
    aL = ry(-0.55 * sw) if arms is None else ry(-arms[0]); aR = ry(0.55 * sw) if arms is None else ry(-arms[1])
    pr.set(g['armL'], sh(1), Rb @ aL, k); pr.set(g['armR'], sh(-1), Rb @ aR, k)


def kids_pose(Kd, D, t):
    pr = Kd['parts']; B = W.B; tt = tau(t)
    w = W.weights(t); winter = float(w[3])
    look = W.sm(B.look0, B.look0 + 0.6, t) * (1 - W.sm(B.open0 - 0.4, B.open0, t)) * 0.0 + W.win(t, B.look0, B.final, 0.6)
    dance = W.win(t, B.open0, B.final + 2.0, 0.4)
    # ---- the girl in red shoes
    g = Kd['g']['girl']; u = (tt * 0.045 + 0.1) % 1.0; p, hd = path_at(GIRL_PATH, u); walking = 1.0
    face = math.atan2(TY - p[1], TX - p[0])
    face_cam = math.atan2(-0.88, 0.47)
    end_lie = W.sm(B.lie0, B.lie1, t)
    stand_pt = np.array([0.05, -0.30])
    if t >= B.look0:
        # walks to a spot in front of the tree and stops to look up, then dances; at the end lies with an ear to the grass
        up = W.sm(B.look0, B.look0 + 2.5, t); path0 = tau(B.look0) * 0.045 + 0.1
        p0, _ = path_at(GIRL_PATH, path0 % 1.0); p = p0 + (stand_pt - p0) * up; walking = 1.0 if up < 0.98 else 0.0
        hd = math.atan2(stand_pt[1] - p0[1], stand_pt[0] - p0[0]) if up < 0.98 else face
        hd = hd + (face - hd) * W.sm(B.look0 + 2.0, B.look0 + 2.8, t) * (0.0 if up < 0.98 else 1.0)
        if up >= 0.98: hd = face
    pz = gz(p[0], p[1], t); ph = 2 * math.pi * 1.2 * tt
    arms = None; jump = 0.0
    if t >= B.look0 and walking == 0.0:
        arms = (0.2, 0.2)
        if t > B.open0 - 0.5: arms = (2.6 + 0.3 * math.sin(6 * t), 2.6 - 0.3 * math.sin(6 * t)); jump = 0.04 * abs(math.sin(2 * math.pi * 1.7 * t)) * dance
        elif t > B.climb0: arms = (2.4, 0.2)
    if end_lie > 0.0:
        pe = np.array([-0.45, -0.98]); p = p + (pe - p) * end_lie; hd = hd + (math.pi / 2 - hd) * end_lie * 0.0
        _kid_pose(pr, g, (p[0], p[1], gz(p[0], p[1], t)), 0.0 if end_lie < 0.5 else 0.0, 0.0, ph, t, 0.0, arms=(0.3, 0.3), lying=end_lie)
    else:
        _kid_pose(pr, g, (p[0], p[1], pz + jump), hd, walking, ph, t, 0.0, arms=arms)
    # ---- the boy dribbling the ball
    g = Kd['g']['boy']; u = (tt * 0.06 + 0.35) % 1.0; q, hq = path_at(BOY_PATH, u); walking = 1.0; arms = None; jump = 0.0
    pball = None
    ball_pos = q + np.array([math.cos(hq), math.sin(hq)]) * 0.20
    if t >= B.look0:
        up = W.sm(B.look0, B.look0 + 2.2, t); u0 = (tau(B.look0) * 0.06 + 0.35) % 1.0; q0, hq0 = path_at(BOY_PATH, u0)
        stand_b = np.array([0.55, -0.55]); q = q0 + (stand_b - q0) * up; walking = 1.0 if up < 0.98 else 0.0
        hq = math.atan2(stand_b[1] - q0[1], stand_b[0] - q0[0]) if up < 0.98 else math.atan2(TY - stand_b[1], TX - stand_b[0])
        ball_pos = q + np.array([0.18, -0.05])
        if walking == 0.0:
            arms = (0.2, 2.5) if t < B.open0 - 0.5 else (2.7 + 0.3 * math.sin(6 * t + 1), 2.7 - 0.3 * math.sin(6 * t))       # points at the tree, then cheers
            if t > B.open0 - 0.5: jump = 0.045 * abs(math.sin(2 * math.pi * 1.9 * t + 1.0)) * dance
    _kid_pose(pr, g, (q[0], q[1], gz(q[0], q[1], t) + jump), hq, walking, 2 * math.pi * 1.4 * tt, t, 0.0, arms=arms)
    pr.commit()
    # the ball: bounces ahead of the boy while he walks, then rests
    pb = Kd['ball']; bi = Kd['ball_ids']
    bounce = abs(math.sin(math.pi * 1.4 * tt)) * 0.06 if walking else 0.0
    bz = gz(ball_pos[0], ball_pos[1], t) + BALL_R + bounce
    sp = 1.6; R = rz(0.3) @ ry(2 * math.pi * 0.7 * tt if walking else 0.0)
    pb.set(bi[0], (ball_pos[0], ball_pos[1], bz), R, sp); pb.set(bi[1], (ball_pos[0], ball_pos[1], bz), R @ rx(math.pi / 2), sp); pb.commit()
    # ---- the dog trots after them, sits and barks at the pop, then dances
    pd = Kd['dog']; dg = Kd['dg']; DK = 1.6
    pth = [(1.2, 0.0), (0.4, 0.45), (-0.5, 0.30), (-0.2, -0.5), (0.7, -0.75), (1.3, -0.40), (1.2, 0.0)]
    u = (tt * 0.055 + 0.2) % 1.0; d, hd = path_at(pth, u); run = 2 * math.pi * 3.0 * tt; amt = 1.0; jump = 0.0; sit = 0.0
    if t >= B.look0:
        up = W.sm(B.look0, B.look0 + 1.5, t); u0 = (tau(B.look0) * 0.055 + 0.2) % 1.0; d0, hd0 = path_at(pth, u0); seat = np.array([0.15, -0.85])
        d = d0 + (seat - d0) * up; hd = math.atan2(seat[1] - d0[1], seat[0] - d0[0]) if up < 0.98 else math.atan2(TY - seat[1], TX - seat[0])
        amt = 1.0 if up < 0.98 else 0.0; sit = W.sm(B.look0 + 1.3, B.look0 + 1.8, t) if up >= 0.98 else 0.0
        if amt == 0.0:
            run = 0.0; jump = 0.05 * max(0.0, math.sin(2 * math.pi * 2.2 * t)) * (1.0 if (t % 1.0) < 0.5 else 0.0) if t > B.open0 - 0.5 else 0.0
    z = gz(d[0], d[1], t) + (0.045 + 0.008 * abs(math.sin(run)) + jump) * DK; R = rz(hd)
    root = np.array([d[0], d[1], z - 0.06 * DK]); Rs = R @ ry(-0.45 * sit)
    pd.set(dg['body'], root, Rs, DK)
    hp = root + Rs @ (np.array([0.062, 0, 0.088]) * DK); tilt = rx(0.0)
    pd.set(dg['head'], hp, R @ tilt, DK)
    for k in ('snout', 'nose', 'earL', 'earR'): pd.set(dg[k], hp, R @ tilt @ (rx(0.25 * math.sin(run)) if k.startswith('ear') else I3), DK)
    wag = 4.0 if t < B.look0 else 9.0
    pd.set(dg['tail'], root + Rs @ (np.array([-0.058, 0, 0.07]) * DK), Rs @ rz(0.6 * math.sin(2 * math.pi * wag * t)), DK)
    for i, (lx, ly, phs) in enumerate(((0.04, 0.018, 0), (0.04, -0.018, math.pi), (-0.04, 0.018, math.pi), (-0.04, -0.018, 0))):
        pd.set(dg['legs'][i], root + R @ (np.array([lx, ly, 0.045]) * DK), R @ ry(0.6 * math.sin(run + phs)), DK)
    pd.commit()


# ------------------------------------------------------------------ the playground (on the land beside the slice)
SWING = (1.6, 2.9)
SLIDE = (2.6, 2.1)


def build_playground(kit, D):
    pr = Parts('fs_play')
    mats = [M.paint(kit, D, 'sz_frame', (0.90, 0.26, 0.24), noise=0.0), M.paint(kit, D, 'sz_seat', (0.98, 0.78, 0.18), noise=0.0), M.paint(kit, D, 'sz_chain', (0.60, 0.62, 0.66), noise=0.0),
            M.paint(kit, D, 'sz_slide', (0.30, 0.62, 0.90), noise=0.0), M.paint(kit, D, 'sz_ladder', (0.96, 0.66, 0.20), noise=0.0)]
    e = {}
    h = 0.62
    e['frame'] = [pr.add(*tube([(-0.30, -0.22, 0), (-0.02, 0, h)], [0.020, 0.020], 8), m=0), pr.add(*tube([(-0.30, 0.22, 0), (-0.02, 0, h)], [0.020, 0.020], 8), m=0),
                  pr.add(*tube([(0.30, -0.22, 0), (0.02, 0, h)], [0.020, 0.020], 8), m=0), pr.add(*tube([(0.30, 0.22, 0), (0.02, 0, h)], [0.020, 0.020], 8), m=0),
                  pr.add(*tube([(-0.03, 0, h), (0.03, 0, h)], [0.0, 0.0], 3), m=0)]
    e['frame'][-1] = pr.add(*tube([(-0.02, 0, h), (-0.02, 0, h)], [0.0, 0.0], 3), m=0)
    e['bar'] = pr.add(*tube([(0, -0.28, h), (0, 0.28, h)], [0.016, 0.016], 8), m=0)
    e['swing'] = [pr.add(*tube([(0, -0.07, 0), (0, -0.07, -0.34)], [0.003, 0.003], 4), m=2), pr.add(*tube([(0, 0.07, 0), (0, 0.07, -0.34)], [0.003, 0.003], 4), m=2),
                  pr.add(*box((0, 0, -0.355), (0.10, 0.18, 0.016)), m=1)]
    # a slide: ladder, platform, and a curved blue slide
    e['slide'] = [pr.add(*box((0, 0, 0.30), (0.20, 0.20, 0.016)), m=4), pr.add(*tube([(0.0, -0.09, 0.0), (0.0, -0.09, 0.30)], [0.012, 0.012], 8), m=4),
                  pr.add(*tube([(0.0, 0.09, 0.0), (0.0, 0.09, 0.30)], [0.012, 0.012], 8), m=4)]
    pts = [(0.10 + 0.30 * u, 0, 0.30 - 0.30 * u ** 1.6) for u in np.linspace(0, 1, 9)]
    V, F = [], []
    for i, (x, y, z) in enumerate(pts): V += [(x, -0.07, z), (x, 0.07, z)]
    for i in range(len(pts) - 1): F.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    e['slide'].append(pr.add(V, F, m=3))
    for k in range(3): e['slide'].append(pr.add(*tube([(0.0, -0.09, 0.06 + 0.09 * k), (0.0, 0.09, 0.06 + 0.09 * k)], [0.006, 0.006], 6), m=4))
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'e': e, 'h': h}


def playground_pose(Pg, D, t):
    pr = Pg['parts']; e = Pg['e']; h = Pg['h']
    def land(x, y): return float(W.land_h(np.array([x]), np.array([y]), t)[0])
    sx, sy = SWING; z0 = land(sx, sy)
    for j in e['frame']: pr.set(j, (sx, sy, z0), I3, 1.0)
    pr.set(e['bar'], (sx, sy, z0), I3, 1.0)
    swing = (0.60 * math.sin(2 * math.pi * 0.42 * t)) * (0.6 + 0.4 * W.win(t, 0.0, 100.0, 1.0))
    for j in e['swing']: pr.set(j, (sx, sy, z0 + h), ry(swing), 1.0)
    px, py = SLIDE; z1 = land(px, py)
    for j in e['slide']: pr.set(j, (px, py, z1), rz(-0.4), 1.0)
    pr.commit()


# ------------------------------------------------------------------ everything
def build(kit, L, D, rng):
    return {'lawn': build_lawn(kit, L, D, rng), 'tree': build_tree(kit, D), 'props': build_props(kit, D), 'kids': build_kids(kit, D), 'play': build_playground(kit, D)}


def pose(Pk, D, t):
    lawn_pose(Pk['lawn'], D, t); tree_pose(Pk['tree'], D, t); props_pose(Pk['props'], D, t); kids_pose(Pk['kids'], D, t); playground_pose(Pk['play'], D, t)
