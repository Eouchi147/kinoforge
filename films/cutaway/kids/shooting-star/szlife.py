"""What is a shooting star? Everything alive on the hilltop, and the easter eggs (bpy + numpy).

Every pose is a pure function of t. Each piece has a job (CRAFT section 1):
  the family   dad toasts marshmallows, mum holds a hot mug, the girl stands at the telescope, her little brother holds a toy
               rocket: when the streak comes they all look up, point, gasp; they close their eyes for the wish; they cuddle
  the camp     a tent with a paper star hanging from it and a glowing doorway, a campfire (flames, sparks, a warm glow on the grass
               and a flickering light), two log seats, a telescope on a tripod that follows the sky, a flashlight with its beam
  the animals  an owl on the tree (its head turns to the streak, it blinks), a sleeping cat, fireflies, the snail mascot with a
               tiny telescope, whose wish is a lettuce leaf (the visual joke)
  the land     grass and a few flowers on the hilltop, round trees and firs all round (dark storybook shapes)
Easter eggs (Sam 23 Oct 19:43: generic everyday things kids know, some obvious, one or two hidden, animated where possible;
never a brand or a character): a teddy bear by the tent, marshmallows on a stick that brown in the fire, a flashlight, a paper
star on the tent, a toy rocket in the little brother's hand, a sleeping cat in a blanket, the snail looking up through a tiny
telescope.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, disc, quad, rz, ry, rx, euler, I3

gz = lambda x, y, t: float(W.top_h(np.array([x]), np.array([y]), t)[0])
K = W.keys


def path_at(P, u):
    P = np.asarray(P, float); seg = np.linalg.norm(np.diff(P, axis=0), axis=1); c = np.concatenate([[0], np.cumsum(seg)])
    s = float(np.clip(u, 0, 1)) * c[-1]; i = min(int(np.searchsorted(c, s, 'right')) - 1, len(seg) - 1); f = (s - c[i]) / max(seg[i], 1e-9)
    p = P[i] + (P[i + 1] - P[i]) * f; d = P[i + 1] - P[i]
    return p, math.atan2(d[1], d[0])


def lumpy_ball(c, r, seed, sub=2, amp=0.18):
    V, F = cw._icosphere(sub); V = cw._lumpy(V, seed, amp, 2.6, 0.06, 7.0); return V * np.asarray(r, float) + np.asarray(c, float), F


def _ell(c, r, sub=1): return sphere(c, r, sub)


def hide_all(pr, ids):
    for v in ids:
        if isinstance(v, (list, tuple)): hide_all(pr, v)
        elif isinstance(v, dict): hide_all(pr, list(v.values()))
        else: pr.hide(v)


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


# ============================================================================== grass, flowers
def build_plants(kit, L, D, rng):
    out = {}
    pal = dict(cw.SEASONS['summer'])
    gm = M.varied(kit, D, 'sz_grass', [(0.30, 0.58, 0.28), (0.40, 0.66, 0.30), (0.26, 0.52, 0.26), (0.46, 0.68, 0.34)], tip=(0.80, 0.90, 0.52), height=0.07)
    tufts = cw.proto_tufts(kit, pal, 6, 0.06, 7, (8, 13))
    for o in tufts: o.data.materials[0] = gm
    xs = np.arange(-W.HX + 0.02, W.HX - 0.01, 0.034); X, Y = np.meshgrid(xs, np.arange(-W.HY + 0.02, W.HY - 0.01, 0.034))
    Q = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.016, 0.016, (X.size, 2))
    rf = np.hypot(Q[:, 0] - W.FIRE[0], Q[:, 1] - W.FIRE[1])
    Q = Q[(rf > 0.50) & (np.abs(Q) < [W.HX - 0.006, W.HY - 0.006]).all(1)]
    Qw = world_pts(rng, 0.05, 1.8); Q = np.vstack([Q, Qw]); n = len(Q)
    sc = rng.uniform(0.7, 1.3, n)
    ob = L.scatter('sz_grass', tufts, Q, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 6, n), sway=0.22, speed=0.9, z=0.0)
    out['grass'] = (ob, Q, sc)
    fl = cw.proto_flowers(kit, 5, 7)
    R = rng.uniform([-W.HX + 0.05, -W.HY + 0.05], [W.HX - 0.05, W.HY - 0.05], (140, 2))
    R = R[np.hypot(R[:, 0] - W.FIRE[0], R[:, 1] - W.FIRE[1]) > 0.55]
    Rw = world_pts(rng, 0.2, 2.2); R = np.vstack([R, Rw]); n = len(R)
    sc = rng.uniform(0.9, 1.5, n)
    ob = L.scatter('sz_flowers', fl, R, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 5, n), sway=0.18, speed=0.9, z=0.0)
    out['flowers'] = (ob, R, sc)
    return out


def _set_pts(ob, P, z, sc):
    me = ob.data; co = np.column_stack([P, z]).astype(np.float32)
    me.vertices.foreach_set('co', co.ravel()); me.attributes['scale'].data.foreach_set('value', np.asarray(sc, np.float32)); me.update()


def plants_pose(pl, t):
    for key in ('grass', 'flowers'):
        ob, Q, sc = pl[key]; _set_pts(ob, Q, W.top_h(Q[:, 0], Q[:, 1], t) - 0.004, sc)


# ============================================================================== trees
def _tree(base, H, crown_r, seed, kind='round'):
    rng = np.random.default_rng(seed); x, y = base; parts = []
    if kind == 'round':
        v, f = tube([(x, y, -0.02), (x + 0.01, y, H * 0.45), (x, y + 0.01, H * 0.62)], [0.028 * H / 0.6, 0.022 * H / 0.6, 0.016 * H / 0.6], 8); parts.append((v, f, 0))
        for c in [(0, 0, 0.78), (-0.45, 0.1, 0.62), (0.45, -0.1, 0.64), (0.1, 0.42, 0.66), (-0.1, -0.42, 0.62), (0.0, 0.0, 1.0)]:
            r = crown_r * rng.uniform(0.6, 0.85); v, f = lumpy_ball((x + c[0] * crown_r, y + c[1] * crown_r, H * c[2]), (r, r, r * 0.85), seed + len(parts)); parts.append((v, f, 1))
    else:
        v, f = tube([(x, y, -0.02), (x, y, H * 0.25)], [0.02, 0.016], 8); parts.append((v, f, 0))
        for i in range(4):
            z0 = H * (0.18 + 0.2 * i); v, f = cone((x, y, z0), crown_r * (1 - 0.2 * i), H * 0.36, 14); parts.append((v, f, 2))
    return parts


# on the slice: the owl tree is TREE (built apart); round trees and firs on the hilltop; many more round the land
SLICE_TREES = [(-1.62, -0.55, 0.62, 0.17, 'round'), (-1.55, 0.88, 0.70, 0.19, 'round'), (-0.35, 0.95, 0.52, 0.12, 'fir'), (0.55, 0.92, 0.66, 0.18, 'round'),
               (1.65, -0.45, 0.60, 0.12, 'fir')]


def build_trees(kit, D):
    pr = Parts('fs_trees')
    mats = [M.paint(kit, D, 'sz_trunk', (0.46, 0.30, 0.24)), M.varied(kit, D, 'sz_crown', [(0.20, 0.52, 0.34), (0.30, 0.60, 0.34), (0.14, 0.44, 0.34)]),
            M.paint(kit, D, 'sz_fir', (0.10, 0.38, 0.36))]
    rng = np.random.default_rng(17); items = []
    pts = behind(world_pts(rng, 1.15, 5.0, 0.35), -1.4); pts = pts[np.hypot((pts[:, 0] - W.LAKE_C[0]) / W.LAKE_R[0], (pts[:, 1] - W.LAKE_C[1]) / W.LAKE_R[1]) > 1.45]
    world = []
    for (x, y) in pts:
        h = rng.uniform(0.40, 0.62); world.append((x, y, h, h * 0.30, 'round' if rng.uniform() < 0.7 else 'fir'))
    for i, (x, y, H, r, kind) in enumerate(SLICE_TREES + world):
        ids = [pr.add(v, f, m, pivot=(x, y, 0)) for v, f, m in _tree((x, y), H, r, 100 + i, kind)]
        items.append((ids, x, y, i * 1.7))
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'items': items}


def trees_pose(T, t):
    pr = T['parts']
    for ids, x, y, ph in T['items']:
        z = gz(x, y, t) - 0.01; R = euler(0.015 * math.sin(0.9 * t + ph), 0.012 * math.cos(0.7 * t + ph), 0.0)
        for j in ids: pr.set(j, (x, y, z), R, 1.0)
    pr.commit()


# ============================================================================== the people
class PersonSpec:
    def __init__(self, name, pos, yaw, k, seat, shirt, pants, skin, hair, hair_kind, hat=None, delay=0.0):
        self.name = name; self.pos = pos; self.yaw = yaw; self.k = k; self.seat = seat
        self.shirt, self.pants, self.skin, self.hair, self.hair_kind, self.hat, self.delay = shirt, pants, skin, hair, hair_kind, hat, delay


def _face(a, b): return math.atan2(b[1] - a[1], b[0] - a[0])


PEOPLE = [
    PersonSpec('dad', W.LOG_A, _face(W.LOG_A, W.FIRE), 2.0, 0.15, (0.80, 0.26, 0.22), (0.26, 0.34, 0.52), (0.78, 0.56, 0.42), (0.18, 0.12, 0.10), 'short', None),
    PersonSpec('mum', (W.LOG_A[0] - 0.36, W.LOG_A[1] + 0.12), _face((W.LOG_A[0] - 0.36, W.LOG_A[1] + 0.12), W.FIRE), 1.85, 0.15, (0.30, 0.62, 0.62), (0.34, 0.30, 0.46), (0.72, 0.50, 0.38), (0.30, 0.16, 0.10), 'bun', None),
    PersonSpec('girl', (W.TELE[0] - 0.34, W.TELE[1] - 0.12), 0.9, 1.55, 0.0, (0.96, 0.78, 0.26), (0.30, 0.34, 0.60), (0.66, 0.44, 0.32), (0.16, 0.10, 0.10), 'plait', (0.90, 0.30, 0.34)),
    PersonSpec('boy', W.LOG_B, _face(W.LOG_B, W.FIRE), 1.30, 0.15, (0.34, 0.70, 0.46), (0.70, 0.46, 0.30), (0.66, 0.44, 0.32), (0.20, 0.12, 0.08), 'tuft', None),
]
LOG_H = 0.085


def build_person(kit, D, sp):
    pr = Parts('fs_p_' + sp.name)
    mats = [M.paint(kit, D, f'sz_{sp.name}_shirt', sp.shirt, noise=0.05), M.paint(kit, D, f'sz_{sp.name}_pants', sp.pants, noise=0.05), M.paint(kit, D, f'sz_{sp.name}_skin', sp.skin, noise=0.0),
            M.paint(kit, D, f'sz_{sp.name}_hair', sp.hair, noise=0.0), M.paint(kit, D, f'sz_{sp.name}_boot', (0.30, 0.22, 0.20), noise=0.0),
            M.paint(kit, D, f'sz_{sp.name}_eye', (0.07, 0.06, 0.10), noise=0.0), M.paint(kit, D, f'sz_{sp.name}_hat', sp.hat or (0.9, 0.3, 0.3), noise=0.05)]
    p = {}
    for s in (-1, 1):
        p['thigh%d' % s] = pr.add(*tube([(0, 0, 0), (0, 0, -0.09)], [0.026, 0.023], 8), m=1)
        p['shin%d' % s] = pr.add(*tube([(0, 0, 0), (0, 0, -0.09)], [0.023, 0.020], 8), m=1)
        p['boot%d' % s] = pr.add(*_ell((0.014, 0, -0.095), (0.036, 0.022, 0.016), 1), m=4)
        p['arm%d' % s] = pr.add(*tube([(0, 0, 0), (0, 0, -0.118)], [0.021, 0.017], 7), m=0)
        p['hand%d' % s] = pr.add(*_ell((0, 0, -0.122), (0.019, 0.019, 0.019), 1), m=2)
        p['eye%d' % s] = pr.add(*_ell((0, 0, 0), (0.0085, 0.0085, 0.0085), 1), m=5)
    p['torso'] = pr.add(*_ell((0, 0, 0.098), (0.050, 0.062, 0.078), 2), m=0)
    p['hips'] = pr.add(*_ell((0, 0, 0.010), (0.046, 0.056, 0.036), 1), m=1)
    p['head'] = pr.add(*_ell((0.0, 0, 0.0), (0.050, 0.050, 0.054), 2), m=2)
    hk = sp.hair_kind
    if sp.hat: p['hair'] = pr.add(*_ell((-0.006, 0, 0.018), (0.052, 0.054, 0.040), 2), m=6)
    else: p['hair'] = pr.add(*_ell((-0.010, 0, 0.012), (0.053, 0.055, 0.050), 2), m=3)
    p['extra'] = []
    if hk == 'plait': p['extra'] += [pr.add(*tube([(-0.04, 0.03, 0.0), (-0.055, 0.04, -0.05), (-0.055, 0.04, -0.10)], [0.014, 0.012, 0.008], 6), m=3)]
    if hk == 'bun': p['extra'] += [pr.add(*_ell((-0.045, 0, 0.055), (0.026, 0.026, 0.026), 1), m=3)]
    if hk == 'tuft': p['extra'] += [pr.add(*_ell((0.0, 0, 0.060), (0.018, 0.018, 0.026), 1), m=3)]
    if sp.hat: p['extra'] += [pr.add(*_ell((-0.006, 0, 0.066), (0.016, 0.016, 0.016), 1), m=3)]
    if sp.name == 'dad': p['extra'] += [pr.add(*_ell((0.028, 0, -0.030), (0.034, 0.040, 0.030), 1), m=3)]      # a beard
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'p': p, 'spec': sp}


def person_params(name, t):
    """(look up 0..1, eyes 0..1, aL, aR, lean, cuddle) for the story: each arm (rx, ry) swing angles."""
    B = W.B
    look = W.sm(B.point0 - 0.15, B.point0 + 0.35, t) * (1 - 0.0)
    eyes = 1.0 - W.win(t, B.wish0, B.wish1, 0.35)
    gasp = W.win(t, B.gasp, B.gasp + 2.2, 0.35)
    if name == 'girl':
        look = max(look * (1 - 0.8 * W.win(t, B.pebble0, B.pebble2, 0.5)), 0.2 * W.win(t, B.pebble0, B.pebble2, 0.5))
    return look, eyes, gasp


def person_pose(Pn, t):
    B = W.B; pr = Pn['parts']; p = Pn['p']; sp = Pn['spec']; k = sp.k
    look, eyes, gasp = person_params(sp.name, t)
    seat = sp.seat > 0
    x, y = sp.pos; yaw = sp.yaw
    cud = W.sm(B.cuddle0, B.cuddle0 + 1.2, t)
    # arms (rx sideways, ry forward/back)
    aL = (0.0, 0.0); aR = (0.0, 0.0)
    pit = 0.55 * look                     # the head tilts up
    lean = -0.14 * look - 0.10 * gasp + 0.10 * cud
    if sp.name == 'dad':
        toast = W.win(t, B.toast0, B.point0 + 0.3, 0.5)
        stick = (0.0, -1.35 + 0.06 * math.sin(1.1 * t))
        aR = stick if toast > 0.5 else (0.0, -0.5)
        up = W.win(t, B.point0, B.point1, 0.4); aR = tuple(np.array(aR) * (1 - up) + np.array((0.0, -2.5)) * up)
        aR = tuple(np.array(aR) * (1 - cud) + np.array((0.0, -0.9)) * cud)
        aL = (0.0, -0.3 * (1 - cud) - 1.0 * cud)
    elif sp.name == 'mum':
        aR = (0.0, -1.15 + 0.03 * math.sin(0.8 * t))          # the mug held in front
        aL = (0.0, -1.0)
        up = W.win(t, B.point0, B.point0 + 1.6, 0.4); aR = tuple(np.array(aR) * (1 - up) + np.array((0.0, -2.4)) * up)
        aR = tuple(np.array(aR) * (1 - cud) + np.array((0.0, -1.0)) * cud)
    elif sp.name == 'girl':
        tele = W.win(t, B.tele0, B.hold0 + 3.0, 0.5)
        aR = (0.0, -1.3 * tele); aL = (0.2 * tele, -0.3 * tele)
        pb = W.sm(B.pebble0, B.pebble0 + 0.8, t) * (1 - W.sm(B.pebble2, B.pebble2 + 0.7, t))
        aL = tuple(np.array(aL) * (1 - pb) + np.array((0.0, -2.5)) * pb)       # the pebble held high against the sky
        pt = W.win(t, B.point0, B.point1, 0.4); aR = tuple(np.array(aR) * (1 - pt) + np.array((0.2, -2.6)) * pt)
    else:      # the little brother holds the toy rocket
        aR = (0.0, -1.0)
        aR = tuple(np.array(aR) + np.array((0.0, -1.5)) * W.win(t, B.point0, B.point1, 0.4))
        aL = (0.0, -0.4)
    if gasp > 0.05: aL = tuple(np.array(aL) * (1 - gasp) + np.array((0.6, -2.7)) * gasp); aR = tuple(np.array(aR) * (1 - gasp) + np.array((-0.6, -2.7)) * gasp)
    # the wish: hands together in front of the chest, head tipped up, eyes closed
    wi = W.win(t, B.wish0, B.wish1, 0.5)
    if wi > 0.02:
        aL = tuple(np.array(aL) * (1 - wi) + np.array((0.5, -1.0)) * wi); aR = tuple(np.array(aR) * (1 - wi) + np.array((-0.5, -1.0)) * wi); pit = pit * (1 - wi) + 0.40 * wi
    bob = 0.004 * math.sin(2 * math.pi * 0.28 * t + sp.delay * 3)
    zg = gz(x, y, t)
    hip = (LOG_H + 0.09 * 0 + 0.085 * k) if seat else 0.18 * k
    if seat: hip = LOG_H * 1.05 + 0.040 * k + 0.0
    root = np.array([x, y, zg + hip + bob])
    R0 = rz(yaw)
    Rt = R0 @ ry(lean)
    # legs
    for s in (-1, 1):
        a_t = -1.45 if seat else 0.0; a_s = 1.45 if seat else 0.0
        if sp.name == 'girl':
            sw = 0.0
        hipp = root + R0 @ np.array([0, s * 0.026 * k, -0.01 * k])
        Rth = R0 @ ry(a_t); knee = hipp + Rth @ np.array([0, 0, -0.09 * k]); Rsh = R0 @ ry(a_t + a_s)
        pr.set(p['thigh%d' % s], hipp, Rth, k); pr.set(p['shin%d' % s], knee, Rsh, k)
        foot = knee + Rsh @ np.array([0, 0, 0.0]); pr.set(p['boot%d' % s], foot, Rsh, k)
    pr.set(p['hips'], root, R0, k)
    pr.set(p['torso'], root, Rt, k)
    sh = lambda s: root + Rt @ (np.array([0.0, s * 0.066, 0.152]) * k)
    for s, a in ((-1, aR), (1, aL)):
        Ra = Rt @ rx(a[0] * s) @ ry(a[1])
        pr.set(p['arm%d' % s], sh(s), Ra, k); pr.set(p['hand%d' % s], sh(s), Ra, k)
    # head
    hb = root + Rt @ (np.array([0.0, 0.0, 0.235]) * k); Rh = Rt @ ry(-pit)
    pr.set(p['head'], hb, Rh, k); pr.set(p['hair'], hb, Rh, k)
    for q in p['extra']: pr.set(q, hb, Rh, k)
    for s in (-1, 1):
        ey = max(0.12, eyes) * (1.0 - 0.9 * (1 - eyes))
        pr.set(p['eye%d' % s], hb + Rh @ (np.array([0.044, s * 0.021, 0.008]) * k), Rh, (k, k, k * max(0.12, eyes)))
    pr.commit()
    return {'hand_R': sh(-1) + Rt @ rx(aR[0] * -1) @ ry(aR[1]) @ (np.array([0, 0, -0.13]) * k), 'hand_L': sh(1) + Rt @ rx(aL[0]) @ ry(aL[1]) @ (np.array([0, 0, -0.13]) * k), 'head': hb, 'Rh': Rh, 'yaw': yaw}


# ============================================================================== the camp
def build_camp(kit, D):
    pr = Parts('fs_camp')
    mats = [M.paint(kit, D, 'sz_tent', (0.96, 0.52, 0.30), noise=0.05), M.paint(kit, D, 'sz_tentstripe', (0.99, 0.90, 0.70), noise=0.0),
            M.mat_drive_glow(kit, D, 'fs_tentin', 'tentglow', 1.0), M.paint(kit, D, 'sz_rope', (0.92, 0.88, 0.76), noise=0.0),
            M.paint(kit, D, 'sz_peg', (0.50, 0.36, 0.26), noise=0.0), M.paint(kit, D, 'sz_log', (0.50, 0.34, 0.24)),
            M.paint(kit, D, 'sz_logend', (0.78, 0.62, 0.44), noise=0.0), M.paint(kit, D, 'sz_stone', (0.60, 0.60, 0.66)),
            M.paint(kit, D, 'sz_brass', (0.92, 0.72, 0.30), rough=0.35, noise=0.0), M.paint(kit, D, 'sz_scope', (0.28, 0.36, 0.62), noise=0.0),
            M.paint(kit, D, 'sz_tripod', (0.40, 0.30, 0.24), noise=0.0), M.mat_glow(kit, D, 'fs_pstar', (1.0, 0.80, 0.28), 1.1),
            M.paint(kit, D, 'sz_pole', (0.60, 0.50, 0.40), noise=0.0), M.paint(kit, D, 'sz_blanket', (0.80, 0.34, 0.34), noise=0.05)]
    c = {}
    # ---- the tent: a prism (ridge along y), local frame at its centre on the ground; entrance on the -y face, turned to the viewer
    w, d, h = 0.60, 0.50, 0.80      # half width, half depth, height
    def tri(a, b, cc, m): return ([a, b, cc], [(0, 1, 2)], m)
    V = [(-w, -d, 0), (w, -d, 0), (0, -d, h), (-w, d, 0), (w, d, 0), (0, d, h)]
    pr_ = lambda V_, F_, m: pr.add(np.array(V_, float), F_, m)
    c['panL'] = pr_(V, [(0, 3, 5, 2)], 0); c['panR'] = pr_(V, [(1, 2, 5, 4)], 0); c['back'] = pr_(V, [(3, 4, 5)], 0)
    # the front triangle: the doorway is a smaller glowing triangle; frame in cream
    c['front'] = pr_(V, [(0, 1, 2)], 1)
    dw = 0.32; dh = 0.52; ze = -d - 0.004
    c['door'] = pr_([(-dw, ze, 0.0), (dw, ze, 0.0), (0, ze, dh)], [(0, 1, 2)], 2)
    c['flapL'] = pr_([(-dw, ze - 0.004, 0.0), (-dw * 0.22, ze - 0.004, 0.0), (0, ze - 0.004, dh), (-dw * 0.5, ze - 0.004, dh * 0.5)], [(0, 1, 2, 3)], 0)
    c['stripe'] = [pr_([(-w * (1 - s), -d - 0.002, h * s), (w * (1 - s), -d - 0.002, h * s), (w * (1 - s - 0.07), -d - 0.002, h * (s + 0.07)), (-w * (1 - s - 0.07), -d - 0.002, h * (s + 0.07))], [(0, 1, 2, 3)], 1) for s in (0.60,)]
    c['pole'] = pr_(*tube([(0, -d - 0.05, h), (0, -d - 0.05, h + 0.12)], [0.008, 0.005], 6), 12) if False else pr.add(*tube([(0, -d - 0.02, h - 0.02), (0, -d - 0.02, h + 0.10)], [0.008, 0.005], 6), 12)
    c['ropes'] = [pr.add(*tube([(sx * w * 0.5, -d * 1.0, h * 0.5), (sx * (w + 0.30), -d - 0.30, 0.01)], [0.004, 0.004], 5), 3) for sx in (-1, 1)]
    c['pegs'] = [pr.add(*cone((sx * (w + 0.30), -d - 0.30, 0.0), 0.012, 0.04, 6), 4) for sx in (-1, 1)]
    # ---- two log seats
    for nm in ('logA', 'logB'):
        c[nm] = [pr.add(*tube([(-0.26, 0, 0), (0.26, 0, 0)], [0.075, 0.075], 12), 5), pr.add(*disc((0.262, 0, 0), 0.07, 12, 'y'), 6) if False else pr.add(*_ell((0.262, 0, 0), (0.006, 0.07, 0.07), 1), 6)]
    # ---- the fire ring: stones, and three crossed logs
    c['stones'] = [pr.add(*_ell((0.34 * math.cos(2 * math.pi * k / 9 + 0.2), 0.30 * math.sin(2 * math.pi * k / 9 + 0.2), 0.02), (0.050, 0.044, 0.034), 1), 7) for k in range(9)]
    c['flogs'] = [pr.add(*tube([(-0.17, 0, 0.0), (0.17, 0, 0.0)], [0.026, 0.026], 8), 5) for _ in range(3)]
    # ---- the telescope: tripod legs, a brass-banded blue tube and an eyepiece (posed to aim each frame)
    c['legs'] = [pr.add(*tube([(0, 0, 0.0), (0, 0, -0.5)], [0.017, 0.012], 6), 10) for _ in range(3)]
    c['tube'] = pr.add(*tube([(-0.30, 0, 0), (0.34, 0, 0)], [0.036, 0.042], 12), 9)
    c['band'] = [pr.add(*tube([(x0, 0, 0), (x0 + 0.04, 0, 0)], [0.044, 0.044], 12), 8) for x0 in (-0.30, 0.10, 0.30)]
    c['eyep'] = pr.add(*tube([(-0.40, 0, 0), (-0.30, 0, 0)], [0.016, 0.022], 8), 8)
    c['head'] = pr.add(*_ell((0, 0, 0), (0.03, 0.03, 0.03), 1), 8)
    ring = [(0.075 * (1 if k % 2 == 0 else 0.42) * math.sin(math.pi * k / 5), 0.0, -0.10 + 0.075 * (1 if k % 2 == 0 else 0.42) * math.cos(math.pi * k / 5)) for k in range(10)]
    c['pstar'] = [pr.add(np.array([(0, 0, -0.10)] + ring), [(0, 1 + k, 1 + (k + 1) % 10) for k in range(10)], 11), pr.add(*tube([(0, 0, 0), (0, 0, -0.06)], [0.002, 0.002], 4), 3)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'c': c}


TENT_YAW = 0.62
LOG_A_YAW = W.FIRE[1] - W.LOG_A[1]


def camp_pose(Cp, t):
    B = W.B; pr = Cp['parts']; c = Cp['c']
    Rt = rz(TENT_YAW); tx, ty = W.TENT; zt = gz(tx, ty, t) - 0.01
    for k in ('panL', 'panR', 'back', 'front', 'door', 'flapL', 'pole'): pr.set(c[k], (tx, ty, zt), Rt)
    for k in ('stripe', 'ropes', 'pegs'):
        for j in c[k]: pr.set(j, (tx, ty, zt), Rt)
    for nm, pos in (('logA', W.LOG_A), ('logB', W.LOG_B)):
        yaw = math.atan2(W.FIRE[1] - pos[1], W.FIRE[0] - pos[0]) + math.pi / 2
        for j in c[nm]: pr.set(j, (pos[0], pos[1], gz(pos[0], pos[1], t) + 0.07), rz(yaw))
    fx, fy = W.FIRE; zf = gz(fx, fy, t)
    for j in c['stones']: pr.set(j, (fx, fy, zf), I3)
    for i, j in enumerate(c['flogs']): pr.set(j, (fx, fy, zf + 0.035 + 0.02 * i), rz(i * 2.1 + 0.4) @ ry(0.10 * (i - 1)))
    # the telescope: a tripod standing on the grass, the tube aimed at the star, then following the sky
    ex, ey = W.TELE; zg = gz(ex, ey, t); ph = 0.0
    a = math.radians(W.VIEW_AZ); right = np.array([-math.sin(a), math.cos(a), 0.0]); fwd = np.array([-math.cos(a), -math.sin(a), 0.0])
    el = math.radians(K(t, [(0.0, 28.0), (B.tele0, 28.0), (B.tele1, 52.0), (B.streak0 - 0.4, 52.0), (B.peak, 68.0), (B.peak + 1.6, 56.0), (B.cuddle1, 40.0)]))
    hz = fwd * 0.92 - right * 0.38; hz /= np.linalg.norm(hz)
    d = np.array([hz[0] * math.cos(el), hz[1] * math.cos(el), math.sin(el)])
    ax = np.cross([1, 0, 0], d); n = np.linalg.norm(ax)
    if n < 1e-6: Rd = I3
    else:
        ax /= n; ang = math.acos(np.clip(d[0], -1, 1)); Kx = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]]); Rd = I3 + math.sin(ang) * Kx + (1 - math.cos(ang)) * Kx @ Kx
    hd = np.array([ex, ey, zg + 0.52])
    sway = 0.01 * math.sin(0.9 * t)
    for i, j in enumerate(c['legs']):
        an = 2 * math.pi * i / 3 + 0.5; out = np.array([math.cos(an), math.sin(an), 0.0]) * 0.17
        top = hd + np.array([0, 0, -0.01]); foot = np.array([ex, ey, zg]) + out
        v = foot - top; L_ = np.linalg.norm(v); zax = v / L_; xax = np.cross([0, 1, 0], zax); xax /= np.linalg.norm(xax) + 1e-9; yax = np.cross(zax, xax)
        pr.set(j, top, np.column_stack([xax, yax, zax]), (1.0, 1.0, L_ / 0.5))
    pr.set(c['head'], hd, I3)
    for nm in ('tube', 'eyep'): pr.set(c[nm], hd + Rd @ np.array([0.0, 0, 0.04]), Rd)
    for j in c['band']: pr.set(j, hd + Rd @ np.array([0.0, 0, 0.04]), Rd)
    # the paper star hangs by its string from the tent's front pole, swinging a little
    sw = 0.12 * math.sin(1.7 * t) + 0.05 * math.sin(4.1 * t + 1.0)
    Rp = Rt @ rx(sw)
    for j in c['pstar']: pr.set(j, np.array([tx, ty, zt]) + Rt @ np.array([0.50, -0.60, 0.30]), Rp, 1.5)
    pr.commit()
    tip = hd + Rd @ np.array([0.34, 0, 0.04]); eye = hd + Rd @ np.array([-0.40, 0, 0.04])
    return {'tip': tip, 'eye': eye, 'tent': (tx, ty, zt), 'tent_yaw': TENT_YAW}


# ============================================================================== the fire, the lantern, the glow
def build_fire(kit, D):
    pr = Parts('fs_fire')
    mats = [M.mat_glow(kit, D, 'fs_flame1', (1.0, 0.46, 0.12), 2.2), M.mat_glow(kit, D, 'fs_flame2', (1.0, 0.78, 0.26), 2.6), M.mat_glow(kit, D, 'fs_flame3', (1.0, 0.96, 0.72), 3.0),
            M.mat_glow(kit, D, 'fs_ember', (1.0, 0.55, 0.20), 2.0), M.mat_glow(kit, D, 'fs_spark', (1.0, 0.86, 0.45), 3.0),
            M.paint(kit, D, 'sz_fsmoke', (0.80, 0.80, 0.86), noise=0.0, lit=False)]
    def flame(h, w, m):
        pts = [(0, 0, 0), (w, 0, h * 0.25), (w * 0.55, 0, h * 0.7), (0, 0, h), (-w * 0.55, 0, h * 0.7), (-w, 0, h * 0.25)]
        V = [p for p in pts] + [(p[0] * 0.0, 0.0, p[2]) for p in pts]
        return pts, [(0, 1, 2, 5), (5, 2, 3, 4)]
    f = {'flames': []}
    for k, (h, w, m) in enumerate(((0.36, 0.10, 0), (0.28, 0.08, 1), (0.18, 0.06, 2), (0.30, 0.08, 0), (0.22, 0.07, 1))):
        a, ff = flame(h, w, m); f['flames'].append((pr.add(a, ff, m), pr.add(*[(np.array(a) * (1, 1, 1) + (0, 0.001, 0)), [(0, 5, 4, 3), (0, 3, 2, 1)]], m), k))
    f['embers'] = [pr.add(*_ell((0.12 * math.cos(k * 2.3), 0.10 * math.sin(k * 2.3), 0.03), (0.020, 0.020, 0.012), 1), 3) for k in range(5)]
    f['sparks'] = [(pr.add(*sphere((0, 0, 0), (0.010, 0.010, 0.010), 1), 4), k) for k in range(14)]
    f['smoke'] = [pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), 5) for _ in range(6)]
    pr.build(kit.bpy, mats, kit.coll)
    # the glow on the grass: a flat disc with a radial falloff, warm; and the point light
    bpy = kit.bpy; n = 40; V = [(0, 0, 0)] + [(math.cos(a), math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    F = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    m = cw._new_mat(bpy, 'fs_fireglow'); g = cw.G(m.node_tree, kit); rr = g.attr('rr').outputs['Fac']
    fall = g.math('POWER', g.math('SUBTRACT', 1.0, rr, clamp=True), 1.6)
    e = g.node('ShaderNodeEmission', ins={'Color': cw.srgb((1.0, 0.56, 0.20)), 'Strength': 1.0})
    M._alpha_out(g, e, g.math('MULTIPLY', fall, D.val(g, 'fireglow', 0.0)))
    glow = cw.mk_mesh(bpy, 'fs_fireglowdisc', V, F, [m], None, False, kit.coll, {'rr': ('FLOAT', [0.0] + [1.0] * n)}); glow.visible_shadow = False
    ld = bpy.data.lights.new('fs_firelight', 'POINT'); ld.color = (1.0, 0.58, 0.28); ld.energy = 0.0; ld.shadow_soft_size = 0.25
    lo = bpy.data.objects.new('fs_firelight', ld); kit.coll.objects.link(lo)
    return {'parts': pr, 'f': f, 'glow': glow, 'light': lo}


def fire_pose(Fr, D, t):
    pr = Fr['parts']; f = Fr['f']; fx, fy = W.FIRE; zf = gz(fx, fy, t) + 0.03
    nt = W.night(t); lit = W.sm(0.0, 1.5, t)
    fl = 0.85 + 0.15 * math.sin(11.0 * t) * math.sin(7.3 * t + 1.0) + 0.06 * math.sin(23.0 * t)
    for a, b, k in f['flames']:
        ph = k * 1.7; s = lit * (0.85 + 0.25 * math.sin(2 * math.pi * (1.3 + 0.2 * k) * t + ph)) * fl
        x = fx + 0.05 * math.cos(1.9 * k + 0.7); y = fy + 0.05 * math.sin(1.9 * k + 0.7)
        sway = 0.12 * math.sin(3.1 * t + ph)
        R = rz(0.8 * k) @ ry(sway); R2 = rz(0.8 * k + math.pi / 2) @ ry(sway)
        pr.set(a, (x, y, zf), R, (s, s, s * (1.0 + 0.3 * math.sin(5.0 * t + ph)))); pr.set(b, (x, y, zf), R2, (s, s, s * (1.0 + 0.3 * math.sin(5.0 * t + ph))))
    for j in f['embers']: pr.set(j, (fx, fy, zf - 0.02), I3, lit * (0.8 + 0.2 * math.sin(3 * t + j)))
    for j, k in f['sparks']:
        T = 2.4; age = ((t / T + k * 0.137) % 1.0); ang = 2.4 * k + 0.3; r = 0.08 + 0.22 * age
        x = fx + r * math.cos(ang) * 0.5 + 0.03 * math.sin(7 * age + k); y = fy + r * math.sin(ang) * 0.5; z = zf + 0.2 + 0.95 * age
        s = (1 - age) ** 1.3 * lit
        if k % 3 == 0 and s > 0: pr.set(j, (x, y, z), I3, s * 1.2)
        else: pr.hide(j)
    for i, j in enumerate(f['smoke']):
        age = ((t / 5.0 + i / 6.0) % 1.0); x = fx + 0.05 * math.sin(3 * age + i) + 0.15 * age; y = fy + 0.15 * age * math.cos(i); z = zf + 0.30 + 1.0 * age
        r = (0.03 + 0.07 * age) * (1 - W.sm(0.6, 1.0, age)) * lit * 0.8
        if r < 1e-3: pr.hide(j)
        else: pr.set(j, (x, y, z), I3, r)
    pr.commit()
    D.set('fireglow', lit * (0.35 + 0.45 * nt) * fl)
    g = Fr['glow']; g.location = (fx, fy, gz(fx, fy, t) + 0.010); g.scale = (1.25, 1.05, 1.0); g.rotation_euler = (0, 0, 0.0)
    lo = Fr['light']; lo.location = (fx, fy, zf + 0.35); lo.data.energy = 90.0 * lit * fl * (0.4 + 0.6 * nt)
    D.setc('tentglow', tuple(c * (0.55 + 0.45 * nt) for c in (1.0, 0.74, 0.40)) if lit > 0 else (0.2, 0.15, 0.1)); return fl


# ============================================================================== easter eggs and small animals
def build_eggs(kit, D):
    pr = Parts('fs_eggs')
    mats = [M.paint(kit, D, 'sz_teddy', (0.78, 0.52, 0.28)), M.paint(kit, D, 'sz_teddy2', (0.96, 0.84, 0.66), noise=0.0), M.paint(kit, D, 'sz_teddybow', (0.90, 0.20, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_stickw', (0.50, 0.34, 0.22), noise=0.0), M.paint(kit, D, 'sz_marsh', (0.98, 0.95, 0.90), noise=0.0), M.mat_drive_glow(kit, D, 'fs_marshhot', 'marsh', 1.2),
            M.paint(kit, D, 'sz_flashbody', (0.90, 0.24, 0.20), rough=0.4, noise=0.0), M.mat_glow(kit, D, 'fs_flashlens', (1.0, 0.96, 0.70), 2.6),
            M.mat_glow(kit, D, 'fs_flashbeam', (1.0, 0.95, 0.65), 1.0, alpha='beam_a'),
            M.paint(kit, D, 'sz_rocketbody', (0.92, 0.92, 0.96), noise=0.0), M.paint(kit, D, 'sz_rocketred', (0.90, 0.22, 0.22), noise=0.0), M.paint(kit, D, 'sz_rocketwin', (0.40, 0.70, 0.90), noise=0.0),
            M.paint(kit, D, 'sz_cat', (0.88, 0.62, 0.36)), M.paint(kit, D, 'sz_catw', (0.99, 0.96, 0.92), noise=0.0), M.paint(kit, D, 'sz_catear', (0.96, 0.62, 0.62), noise=0.0),
            M.paint(kit, D, 'sz_pebble', (0.62, 0.52, 0.44)), M.paint(kit, D, 'sz_pebblec', (0.44, 0.34, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_lettuce', (0.50, 0.86, 0.30), lit=False), M.paint(kit, D, 'sz_lettuce2', (0.84, 0.96, 0.52), noise=0.0, lit=False), M.mat_glow(kit, D, 'fs_wishstar', (1.0, 0.88, 0.40), 2.4)]
    e = {}
    # a teddy bear sitting by the tent
    e['teddy'] = [pr.add(*_ell((0, 0, 0.034), (0.030, 0.028, 0.034), 2), 0), pr.add(*_ell((0.004, 0, 0.082), (0.024, 0.024, 0.022), 2), 0),
                  pr.add(*_ell((0.002, 0.020, 0.100), (0.009, 0.004, 0.009), 1), 0), pr.add(*_ell((0.002, -0.020, 0.100), (0.009, 0.004, 0.009), 1), 0),
                  pr.add(*_ell((0.022, 0, 0.078), (0.010, 0.012, 0.009), 1), 1), pr.add(*_ell((0.018, 0, 0.036), (0.014, 0.020, 0.020), 1), 1),
                  pr.add(*_ell((0.022, 0.024, 0.008), (0.018, 0.010, 0.010), 1), 0), pr.add(*_ell((0.022, -0.024, 0.008), (0.018, 0.010, 0.010), 1), 0),
                  pr.add(*_ell((0.0, 0.032, 0.046), (0.010, 0.010, 0.020), 1), 0), pr.add(*_ell((0.0, -0.032, 0.046), (0.010, 0.010, 0.020), 1), 0),
                  pr.add(*_ell((0.014, 0, 0.060), (0.012, 0.016, 0.006), 1), 2)]
    # dad's stick with two marshmallows (they brown as they near the flames); drawn along +x from the hand
    e['stick'] = pr.add(*tube([(0, 0, 0), (0.30, 0, 0)], [0.004, 0.003], 5), 3)
    e['marsh'] = [pr.add(*_ell((0.27 + 0.025 * i, 0, 0), (0.014, 0.014, 0.014), 1), 4) for i in range(2)]
    e['marsh_hot'] = [pr.add(*_ell((0.27 + 0.025 * i, 0, 0), (0.0145, 0.0145, 0.0145), 1), 5) for i in range(2)]
    # the flashlight on the ground and its beam
    e['flash'] = [pr.add(*tube([(0, 0, 0), (0.09, 0, 0)], [0.012, 0.012], 8), 6), pr.add(*tube([(0.09, 0, 0), (0.11, 0, 0)], [0.018, 0.020], 8), 6), pr.add(*_ell((0.112, 0, 0), (0.002, 0.016, 0.016), 1), 7)]
    e['beam'] = pr.add(*cone((0.115, 0, 0), 0.016, 0.45, 12, 0.11), 8) if False else pr.add(np.array([(0.115, -0.016, 0.0), (0.115, 0.016, 0.0), (0.60, 0.11, 0.0), (0.60, -0.11, 0.0)]), [(0, 1, 2, 3)], 8)
    # the toy rocket (the little brother's)
    e['rocket'] = [pr.add(*tube([(0, 0, -0.045), (0, 0, 0.04)], [0.016, 0.016], 10), 9), pr.add(*cone((0, 0, 0.04), 0.016, 0.034, 10), 10),
                   pr.add(*_ell((0.013, 0, 0.0), (0.006, 0.006, 0.006), 1), 11)] + \
                  [pr.add(*quad([(0, 0.016 * s, -0.045), (0, 0.040 * s, -0.060), (0, 0.040 * s, -0.020), (0, 0.016 * s, -0.005)]), 10) for s in (-1, 1)]
    # a sleeping cat curled on a blanket
    e['cat'] = [pr.add(*quad([(-0.12, -0.10, 0.004), (0.12, -0.10, 0.004), (0.12, 0.10, 0.004), (-0.12, 0.10, 0.004)]), 10 if False else 2),
                pr.add(*_ell((0, 0, 0.040), (0.062, 0.050, 0.036), 2), 12), pr.add(*_ell((0.050, 0.020, 0.034), (0.030, 0.028, 0.026), 2), 12),
                pr.add(*_ell((0.066, 0.034, 0.052), (0.008, 0.006, 0.012), 1), 14), pr.add(*_ell((0.050, 0.044, 0.056), (0.008, 0.006, 0.012), 1), 14),
                pr.add(*tube([(-0.03, -0.04, 0.020), (-0.07, -0.01, 0.018), (-0.02, 0.05, 0.016), (0.04, 0.05, 0.016)], [0.011, 0.010, 0.009, 0.006], 6), 12),
                pr.add(*_ell((0.0, 0.0, 0.052), (0.040, 0.030, 0.014), 1), 13)]
    # the pebble the girl picks up: on the grass, then in her hand
    e['pebble'] = [pr.add(*lumpy_ball((0, 0, 0), (0.026, 0.022, 0.016), 5, 1, 0.25), 15), pr.add(*_ell((0.008, 0.006, 0.010), (0.006, 0.006, 0.003), 1), 16)]
    # the lettuce leaf: a ruffled strip of green with a pale rib, floating (the snail's wish)
    n = 9; Vl = []; Fl = []
    for i in range(n):
        u = i / (n - 1); wd = 0.060 * math.sin(math.pi * (0.12 + 0.88 * u)) ** 0.7 * (1 + 0.16 * math.sin(14 * u))
        Vl += [(u * 0.17 - 0.085, -wd, 0.012 * math.sin(10 * u)), (u * 0.17 - 0.085, 0.0, 0.0), (u * 0.17 - 0.085, wd, 0.012 * math.cos(9 * u))]
    for i in range(n - 1): o = 3 * i; Fl += [(o, o + 3, o + 4, o + 1), (o + 1, o + 4, o + 5, o + 2)]
    e['leaf'] = pr.add(Vl, Fl, 17); e['rib'] = pr.add(*tube([(-0.085, 0, 0.003), (0.08, 0, 0.003)], [0.004, 0.002], 5), 18)
    e['wish'] = [[pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), 19) for _ in range(3)] for _ in range(5)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'e': e}


def owl_tree_parts(kit, D):
    """The owl tree on the hilltop: a trunk, one long branch and a crown; the owl sits on the branch."""
    pr = Parts('fs_owltree')
    mats = [M.paint(kit, D, 'sz_otrunk', (0.42, 0.28, 0.22)), M.varied(kit, D, 'sz_ocrown', [(0.20, 0.50, 0.34), (0.28, 0.58, 0.34), (0.14, 0.42, 0.32)]),
            M.paint(kit, D, 'sz_owlbody', (0.62, 0.46, 0.32)), M.paint(kit, D, 'sz_owlbelly', (0.96, 0.86, 0.70), noise=0.0), M.paint(kit, D, 'sz_owleyew', (0.99, 0.95, 0.72), noise=0.0),
            M.mat_glow(kit, D, 'fs_owleye', (1.0, 0.84, 0.24), 1.6), M.paint(kit, D, 'sz_owlpupil', (0.06, 0.05, 0.08), noise=0.0), M.paint(kit, D, 'sz_owlbeak', (1.0, 0.62, 0.18), noise=0.0)]
    o = {}
    H = 0.78; v, f = tube([(0, 0, -0.03), (0.02, 0, H * 0.45), (0.0, 0.02, H * 0.72)], [0.050, 0.038, 0.028], 10); o['trunk'] = pr.add(v, f, 0)
    o['branch'] = pr.add(*tube([(0.0, 0, 0.46), (-0.18, -0.08, 0.50), (-0.40, -0.12, 0.52)], [0.026, 0.020, 0.012], 8), 0)
    for i, c in enumerate([(0, 0, 0.88), (-0.18, 0.06, 0.74), (0.18, -0.04, 0.76), (0.04, 0.2, 0.78), (0.02, -0.2, 0.74), (0.0, 0.0, 1.0)]):
        o['crown%d' % i] = pr.add(*lumpy_ball(c, (0.20, 0.20, 0.17), 31 + i), 1)
    # the owl, local frame: at the origin (the branch's end), facing +x; head separate so it can turn
    o['body'] = pr.add(*_ell((0, 0, 0.060), (0.046, 0.040, 0.066), 2), 2); o['belly'] = pr.add(*_ell((0.016, 0, 0.052), (0.032, 0.030, 0.050), 2), 3)
    o['wingL'] = pr.add(*_ell((-0.006, 0.040, 0.058), (0.026, 0.010, 0.048), 1), 2); o['wingR'] = pr.add(*_ell((-0.006, -0.040, 0.058), (0.026, 0.010, 0.048), 1), 2)
    o['tail'] = pr.add(*_ell((-0.036, 0, 0.020), (0.020, 0.014, 0.036), 1), 2)
    o['head'] = pr.add(*_ell((0, 0, 0), (0.048, 0.050, 0.044), 2), 2)
    o['tuft'] = [pr.add(*cone((0.0, sd * 0.032, 0.030), 0.012, 0.030, 6), 2) for sd in (-1, 1)]
    o['disc'] = [pr.add(*_ell((0.034, sd * 0.021, 0.004), (0.016, 0.019, 0.019), 1), 4) for sd in (-1, 1)]
    o['eye'] = [pr.add(*_ell((0.044, sd * 0.021, 0.004), (0.012, 0.0125, 0.0125), 1), 5) for sd in (-1, 1)]
    o['pupil'] = [pr.add(*_ell((0.054, sd * 0.021, 0.004), (0.006, 0.006, 0.006), 1), 6) for sd in (-1, 1)]
    o['beak'] = pr.add(*cone((0.044, 0, -0.008), 0.010, 0.020, 6), 7)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'o': o}


OWL_AT = (W.TREE[0] - 0.40, W.TREE[1] - 0.12, 0.52 + 0.015)     # the branch's end, relative to the tree (rotated by the tree's yaw)


def owl_pose(Ow, t, streak_dir):
    B = W.B; pr = Ow['parts']; o = Ow['o']; tx, ty = W.TREE; zg = gz(tx, ty, t) - 0.01
    Rt = rz(0.6)
    for k, j in o.items():
        if k in ('trunk', 'branch') or k.startswith('crown'): pr.set(j, (tx, ty, zg), Rt, 1.0)
    base = np.array([tx, ty, zg]) + Rt @ np.array([-0.40, -0.12, 0.52 + 0.02]); k = 1.7
    # the owl faces the camp (turned to the viewer) and turns its head to follow the sky
    yaw0 = -1.0; look = W.sm(B.owl0, B.owl1, t) * (1 - W.sm(B.cuddle0, B.cuddle1, t)); bl = W.keys(t, [(0, 0.0)])
    head_yaw = 0.7 * look * math.sin(0.5 * math.pi * min(1.0, (t - B.owl0) / 0.7)) if t > B.owl0 else 0.0
    head_yaw += 0.35 * W.win(t, B.streak0, B.peak + 1.5, 0.4) - 0.3 * W.win(t, B.air_in, B.enter + 3, 0.6) * 0.0
    pitch = -0.35 * W.win(t, B.air_in, B.cuddle1, 0.8)
    wide = 1.0 + 0.35 * W.win(t, B.gasp, B.gasp + 2.0, 0.3)
    blink = max(0.0, 1 - abs(((t + 1.3) % 4.7) - 0.1) / 0.1)
    R0 = rz(yaw0 + 0.15 * math.sin(0.25 * t))
    for kk in ('body', 'belly', 'wingL', 'wingR', 'tail'): pr.set(o[kk], base, R0, k)
    hp = base + R0 @ np.array([0.0, 0, 0.116 * k]); Rh = R0 @ rz(head_yaw) @ ry(pitch)
    pr.set(o['head'], hp, Rh, k)
    for j in o['tuft']: pr.set(j, hp, Rh, k)
    for j in o['disc']: pr.set(j, hp, Rh, k)
    for j in o['eye']: pr.set(j, hp, Rh, (k, k * wide, k * wide * (1 - 0.92 * blink)))
    for j in o['pupil']: pr.set(j, hp, Rh, (k, k * wide, k * wide * (1 - 0.92 * blink)))
    pr.set(o['beak'], hp, Rh, k)
    pr.commit()
    return hp


def eggs_pose(E, D, t, hands):
    B = W.B; pr = E['parts']; e = E['e']
    D.setc('marsh', (0.74, 0.46, 0.20)); D.set('beam_a', 0.30 * W.night(t))
    # teddy by the tent
    tx, ty = W.TEDDY; tz = gz(tx, ty, t) - 0.004
    for j in e['teddy']: pr.set(j, (tx, ty, tz), rz(0.35), 2.4)
    # dad's stick with the marshmallows
    hd = hands['dad']['hand_R']; yaw = hands['dad']['yaw']
    toast = W.win(t, B.toast0, B.point0 + 0.3, 0.5)
    up = W.win(t, B.point0, B.point1, 0.4)
    Rs = rz(yaw) @ ry(-0.08 - 1.0 * up) @ rz(0.0)
    brown = W.sm(B.toast0 + 0.5, B.point0, t)
    pr.set(e['stick'], hd, Rs, 1.4)
    for j in e['marsh']: pr.set(j, hd, Rs, 1.4)
    for j in e['marsh_hot']: pr.set(j, hd, Rs, (1.4 * (1.0 + 0.04) if brown > 0.55 else 0.0))
    # flashlight with a beam lying on the grass near the tent
    fx, fy = W.FLASH; fz = gz(fx, fy, t) + 0.014
    for j in e['flash']: pr.set(j, (fx, fy, fz), rz(1.0), 3.0)
    pr.set(e['beam'], (fx, fy, fz + 0.004), rz(1.0), 3.0)
    # the toy rocket in the little brother's hand (it rises when he points)
    hb = hands['boy']['hand_R']; zb = 1.0 + 0.0
    for j in e['rocket']: pr.set(j, hb + np.array([0, 0, 0.05]), rz(hands['boy']['yaw']) @ ry(-0.2 - 0.5 * W.win(t, B.point0, B.point1, 0.4)), 2.3)
    # the sleeping cat
    cx, cy = W.CAT; cz = gz(cx, cy, t) + 0.03; br = 1.0 + 0.04 * math.sin(2 * math.pi * 0.35 * t)
    for i, j in enumerate(e['cat']): pr.set(j, (cx, cy, cz), rz(0.5), (2.2, 2.2, 2.2 * (br if i in (1, 6) else 1.0)))
    # the pebble: on the grass, then in the girl's raised hand, then back on the grass
    px, py = W.PEBBLE; pz = gz(px, py, t) + 0.012
    pb = W.sm(B.pebble0 + 0.8, B.pebble1, t) * (1 - W.sm(B.pebble2, B.pebble2 + 0.8, t))
    hand = hands['girl']['hand_L']
    pos = np.array([px, py, pz]) * (1 - pb) + (hand + np.array([0, 0, 0.012])) * pb
    for j in e['pebble']: pr.set(j, pos, rz(0.4), 1.6 if pb > 0.5 else 1.4)
    # the lettuce leaf floats in from the upper right, rocking, and lands by the snail
    lu = W.sm(B.leaf0, B.leaf1, t)
    if t < B.leaf0 or t > B.munch1 + 0.2: pr.hide(e['leaf']); pr.hide(e['rib'])
    else:
        sx, sy = W.SNAIL_HOME
        p0 = np.array([sx + 1.7, sy + 1.2, gz(sx, sy, t) + 2.2]); p1 = np.array([sx - 0.16, sy - 0.04, gz(sx, sy, t) + 0.07])
        p = p0 + (p1 - p0) * lu + np.array([0.18 * math.sin(7.0 * lu) * (1 - lu), 0.1 * math.cos(5.0 * lu) * (1 - lu), 0.12 * math.sin(4.0 * lu) * (1 - lu)])
        eaten = W.sm(B.munch0, B.munch1, t)
        rot = euler(0.55 * (1 - lu) * math.sin(6 * lu) + 0.35 * lu, 0.4 * (1 - lu) * math.cos(5 * lu), 0.2 + 3.0 * (1 - lu))
        sc = 2.2 * (1 - 0.85 * eaten)
        pr.set(e['leaf'], p, rot, sc); pr.set(e['rib'], p, rot, sc)
    # wish stars lift from each head during the wish
    names = ['dad', 'mum', 'girl', 'boy']
    for i, grp in enumerate(e['wish']):
        wi = W.win(t, B.wish0, B.wish1, 0.4)
        for q, j in enumerate(grp):
            if wi < 0.02 or i >= 4: pr.hide(j); continue
            ph = ((t - B.wish0) * 0.35 + q / 3.0 + 0.2 * i) % 1.0; hp = hands[names[i]]['head']
            pr.set(j, hp + np.array([0.08 * math.sin(5 * ph + i) * 1.0, 0.0, 0.10 + 0.55 * ph]), I3, 0.012 * wi * (1 - ph) ** 0.7)
    pr.commit()


# ============================================================================== fireflies
def build_fireflies(kit, D, rng, n=22):
    pr = Parts('fs_flies'); m = M.mat_glow(kit, D, 'fs_firefly', (0.86, 1.0, 0.40), 3.0); items = []
    for k in range(n): items.append((pr.add(*sphere((0, 0, 0), (0.012, 0.012, 0.012), 1), 0), rng.uniform(-1.9, 1.9), rng.uniform(-1.1, 1.1), rng.uniform(0.15, 0.9), rng.uniform(0, 6.28), rng.uniform(0.15, 0.4), k >= 14))
    pr.build(kit.bpy, [m], kit.coll)
    return {'parts': pr, 'items': items}


def flies_pose(Fl, t):
    pr = Fl['parts']; nt = W.sm(6.0, 14.0, t)
    for j, hx, hy, hz, ph, sp, outer in Fl['items']:
        x = hx + 0.35 * math.sin(sp * 2.1 * t + ph) + 0.12 * math.sin(1.7 * t + 2 * ph); y = hy + 0.25 * math.sin(sp * 1.7 * t + 1.3 * ph)
        if outer: x = hx * 2.6 + 0.8 * math.sin(sp * t + ph); y = hy * 3.0 + 1.0 * math.cos(0.8 * sp * t + ph)
        z = gz(x, y, t) + hz + 0.08 * math.sin(1.3 * t + ph)
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * (0.35 + 0.1 * (j % 4)) * t + ph * 3); s = nt * (0.15 + 0.85 * pulse ** 2) * (1.5 if t > W.B.chord and t < W.B.chord + 2 else 1.0)
        if s < 1e-3: pr.hide(j)
        else: pr.set(j, (x, y, z), I3, s)
    pr.commit()


# ============================================================================== the series mascot: a little snail with a tiny telescope
SK = 4.2


def build_snail(kit, D):
    pr = Parts('fs_snail')
    mats = [M.paint(kit, D, 'sz_snailshell', (0.93, 0.50, 0.42), noise=0.0, lit=False), M.paint(kit, D, 'sz_snailband', (0.99, 0.84, 0.40), noise=0.0, lit=False),
            M.paint(kit, D, 'sz_snailbody', (0.86, 0.80, 0.60), noise=0.0, lit=False), M.paint(kit, D, 'sz_snaileye', (0.10, 0.10, 0.18), noise=0.0, lit=False),
            M.paint(kit, D, 'sz_snailscope', (0.34, 0.46, 0.86), noise=0.0, lit=False), M.paint(kit, D, 'sz_snailbrass', (0.96, 0.78, 0.34), rough=0.35, noise=0.0, lit=False)]
    s = {'shell': pr.add(*sphere((0, 0, 0.032), (0.028, 0.018, 0.030), 2), m=0), 'band': pr.add(*sphere((0.0, 0, 0.032), (0.018, 0.0205, 0.019), 2), m=1),
         'body': pr.add(*sphere((0.012, 0, 0.007), (0.040, 0.012, 0.008), 2), m=2)}
    s['stalks'] = [pr.add(*tube([(0, 0, 0), (0.004, sd * 0.004, 0.022)], [0.0025, 0.0018], 5), m=2) for sd in (-1, 1)]
    s['eyes'] = [pr.add(*sphere((0.004, sd * 0.004, 0.024), (0.0035, 0.0035, 0.0035), 1), m=3) for sd in (-1, 1)]
    s['scope'] = pr.add(*tube([(0, 0, 0), (0.05, 0, 0)], [0.0045, 0.0055], 8), m=4); s['scopeband'] = pr.add(*tube([(0.046, 0, 0), (0.052, 0, 0)], [0.0062, 0.0062], 8), m=5)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 's': s}


def snail_pose(Sn, t):
    """It sits on the front right corner and looks up at the sky through its tiny telescope (one eye stalk to the glass); the
    telescope follows the streak; at the wish it closes its eyes; the lettuce leaf lands beside it and it munches; it waves at the
    end."""
    B = W.B; pr = Sn['parts']; s = Sn['s']
    x, y = W.SNAIL_HOME; p = np.array([x, y, gz(x, y, t) - 0.002]); hdg = -2.45
    up = W.sm(B.snail_up0, B.snail_up1, t)
    follow = W.win(t, B.streak0, B.peak + 1.6, 0.4)
    wishing = W.win(t, B.wish0, B.wish1, 0.5)
    chew = W.win(t, B.munch0, B.munch1, 0.3) * (0.5 + 0.5 * math.sin(2 * math.pi * 2.2 * t))
    R = rz(hdg + 0.1 * math.sin(0.5 * t))
    pr.set(s['shell'], p, R, SK); pr.set(s['band'], p, R, SK)
    pr.set(s['body'], p, R, (SK, SK, SK * (1 - 0.1 * chew)))
    head = p + R @ (np.array([0.040, 0, 0.010]) * SK)
    for j, ph in zip(s['stalks'] + s['eyes'], (0, 1, 0, 1)):
        wob = rx(0.15 * math.sin(2 * math.pi * 0.5 * t + ph)) @ ry(0.0)
        if wishing > 0.5: wob = rx(0.0) @ ry(0.9)     # eyes lowered, shut
        pr.set(j, head, R @ wob, SK)
    # the tiny telescope held to the front eye, pointing up and to the left of the sky (it swings with the streak)
    aim = ry(-(0.9 + 0.5 * up) + 0.0) @ rz(0.0)
    tilt = 1.15 + 0.35 * follow
    on = (up > 0.02) * (1 - wishing) * (1 - W.sm(B.leaf0 + 2.0, B.leaf1, t) * 0.0)
    Rs = R @ ry(-tilt) @ rz(0.5 * follow * 0.0)
    eyep = head + R @ np.array([0.004, 0.004, 0.024]) * SK
    if on < 0.02: pr.hide(s['scope']); pr.hide(s['scopeband'])
    else: pr.set(s['scope'], eyep, Rs, (SK * on, SK * on, SK * on)); pr.set(s['scopeband'], eyep, Rs, (SK * on, SK * on, SK * on))
    pr.commit()
    return head
