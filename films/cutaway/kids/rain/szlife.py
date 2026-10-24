"""Where does rain come from? Everything alive on the slice, and the easter eggs (bpy + numpy). Every pose is a pure function of t.
Each piece has a job (CRAFT section 1):
  meadow grass, flowers and trees          the happy hillside the rain falls on
  birds and butterflies, a rabbit          a busy world in the sun; they leave while it rains and come back after
  the child in a yellow raincoat and red boots, a yellow umbrella and a puddle     everyone knows this one: the rain arrives, she runs in,
                                           the umbrella pops open, she jumps in the puddle; after the rain it closes; at the end one more splash
  the snail                                the series mascot: it LOVES the rain (the visual joke): stretches up, rocks its shell, wiggles its eyes
  a rubber duck on the lake, a paper boat (szstory), a watering can that fills up, a lost red ball and a toy car in the soil, a kite (szback)
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


def lumpy_ball(c, r, seed, sub=2, amp=0.18):
    V, F = cw._icosphere(sub); V = cw._lumpy(V, seed, amp, 2.6, 0.06, 7.0); return V * np.asarray(r, float) + np.asarray(c, float), F


def calm(t):
    """1 when it is dry (before the cloud darkens, and after the rain): the birds, butterflies and the rabbit are out."""
    return 1.0 - max(W.sm(W.B.dark0 + 1.5, W.B.dark1, t) * (1 - W.sm(W.B.drop1, W.B.sunback0 + 1.5, t)), 0.0)


def world_pts(rng, step, rmax, rmin=0.0):
    """Jittered points on the land around the block (not on it, not in the viewing trench), from rmin to rmax metres away."""
    xs = np.arange(-W.HX - rmax, W.HX + rmax, step); ys = np.arange(-W.HY - rmax, W.HY + rmax, step)
    X, Y = np.meshgrid(xs, ys); P = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.5, 0.5, (X.size, 2)) * step
    d = np.hypot(np.maximum(np.abs(P[:, 0]) - W.HX, 0), np.maximum(np.abs(P[:, 1]) - W.HY, 0))
    ok = ~W.in_hole(P[:, 0], P[:, 1]) & (d <= rmax) & (d >= rmin)
    ok &= rng.uniform(0, 1, len(P)) < np.clip(1.15 - d / rmax, 0.15, 1.0)
    return P[ok]


def behind(P, margin=-0.6):
    """Keep points that are not between the camera and the block (tall things there would wall off the view)."""
    return P[W.depth_s(P[:, 0], P[:, 1]) > float(min(W.depth_s(np.array([-W.HX, W.HX]), np.array([-W.HY, -W.HY])))) - margin]


def _set_pts(ob, P, z, sc):
    me = ob.data; co = np.column_stack([P, z]).astype(np.float32)
    me.vertices.foreach_set('co', co.ravel()); me.attributes['scale'].data.foreach_set('value', np.asarray(sc, np.float32)); me.update()


# ============================================================================== plants
def build_plants(kit, L, D, rng):
    """Grass and flowers (the kit's scatter, wind sway), their heights rewritten every frame (they follow the lifted top)."""
    out = {}
    pal = dict(cw.SEASONS['summer'])
    gm = M.varied(kit, D, 'sz_grass', [(0.44, 0.70, 0.30), (0.56, 0.78, 0.34), (0.38, 0.64, 0.28), (0.62, 0.80, 0.38)], tip=(0.90, 0.94, 0.56), height=0.07)
    tufts = cw.proto_tufts(kit, pal, 6, 0.06, 7, (8, 13))
    for o in tufts: o.data.materials[0] = gm
    xs = np.arange(-W.HX + 0.02, W.HX - 0.01, 0.034); X, Y = np.meshgrid(xs, np.arange(-W.HY + 0.02, W.HY - 0.01, 0.034))
    Q = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.016, 0.016, (X.size, 2))
    rd = W.river_d(Q[:, 0], Q[:, 1])
    pud = np.hypot((Q[:, 0] - W.PUDDLE[0]) / (W.PUDDLE[2] + 0.1), (Q[:, 1] - W.PUDDLE[1]) / (W.PUDDLE[3] + 0.1)) > 1.0
    Q = Q[(rd > 0.19) & pud & (np.abs(Q) < [W.HX - 0.006, W.HY - 0.006]).all(1)]
    Qw = world_pts(rng, 0.05, 1.8); Qw = Qw[W.river_d(Qw[:, 0], Qw[:, 1]) > 0.19]; Q = np.vstack([Q, Qw]); n = len(Q)
    sc = rng.uniform(0.7, 1.3, n)
    ob = L.scatter('sz_grass', tufts, Q, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 6, n), sway=0.22, speed=0.9, z=0.0)
    out['grass'] = (ob, Q, sc, rng.uniform(0, 0.4, n))
    fl = cw.proto_flowers(kit, 5, 7)
    R = rng.uniform([-W.HX + 0.05, -W.HY + 0.05], [W.HX - 0.05, W.HY - 0.05], (260, 2))
    pud = np.hypot((R[:, 0] - W.PUDDLE[0]) / (W.PUDDLE[2] + 0.1), (R[:, 1] - W.PUDDLE[1]) / (W.PUDDLE[3] + 0.1)) > 1.0
    R = R[(W.river_d(R[:, 0], R[:, 1]) > 0.22) & pud]
    Rw = world_pts(rng, 0.16, 2.2); Rw = Rw[W.river_d(Rw[:, 0], Rw[:, 1]) > 0.22]; R = np.vstack([R, Rw]); n = len(R)
    sc = rng.uniform(0.9, 1.5, n)
    ob = L.scatter('sz_flowers', fl, R, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 5, n), sway=0.18, speed=0.9, z=0.0)
    out['flowers'] = (ob, R, sc, rng.uniform(0.2, 0.7, n))
    return out


def plants_pose(pl, t):
    for key in ('grass', 'flowers'):
        ob, Q, sc, d = pl[key]
        # the flowers lift their heads a little after the rain (they drink)
        k = 1.0 + (0.18 * W.sm(W.B.soak0, W.B.gw1, t) * (key == 'flowers'))
        _set_pts(ob, Q, TOP(Q[:, 0], Q[:, 1], t) - 0.004, sc * k)


# ============================================================================== trees
def _tree(base, H, crown_r, seed, kind='round'):
    """A storybook tree: a list of (V, F, which) with which 0 = trunk, 1 = crown."""
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


TODAY_TREES = [(-1.50, 0.78, 0.66, 0.20, 'round'), (-0.65, 0.90, 0.56, 0.17, 'round'), (0.95, 0.80, 0.70, 0.21, 'round'),
               (1.62, -0.30, 0.62, 0.13, 'fir'), (0.20, 0.95, 0.50, 0.11, 'fir')]


def world_trees(rng):
    pts = behind(world_pts(rng, 1.25, 5.0, 0.35), -1.4); pts = pts[W.river_d(pts[:, 0], pts[:, 1]) > 0.45]
    out = []
    for i, (x, y) in enumerate(pts):
        h = rng.uniform(0.40, 0.62); out.append((x, y, h, h * 0.30, 'round' if rng.uniform() < 0.7 else 'fir'))
    return out


def build_trees(kit, D):
    pr = Parts('fs_trees')
    mats = [M.paint(kit, D, 'sz_trunk', (0.46, 0.30, 0.24)), M.varied(kit, D, 'sz_crown', [(0.26, 0.62, 0.36), (0.40, 0.70, 0.36), (0.18, 0.52, 0.38)]),
            M.paint(kit, D, 'sz_fir', (0.14, 0.44, 0.40))]
    items = []
    allt = TODAY_TREES + world_trees(np.random.default_rng(17))
    for i, (x, y, H, r, kind) in enumerate(allt):
        ids = [pr.add(v, f, m, pivot=(x, y, 0)) for v, f, m in _tree((x, y), H, r, 100 + i, kind)]
        items.append((ids, x, y, i * 1.7))
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'items': items}


def trees_pose(T, t):
    pr = T['parts']
    # the trees sway a little more in the rain wind and shiver when it falls hard
    wind = 1.0 + 1.4 * W.rain_k(t)
    for ids, x, y, ph in T['items']:
        z = gz(x, y, t) - 0.01
        R = euler(0.015 * wind * math.sin(0.9 * t + ph), 0.012 * wind * math.cos(0.7 * t + ph), 0.0)
        for j in ids: pr.set(j, (x, y, z), R, 1.0)
    pr.commit()


# ============================================================================== creatures
def _ell(c, r, sub=1): return sphere(c, r, sub)


def build_birds(kit, D, rng, n=4):
    pr = Parts('fs_birds'); m = M.paint(kit, D, 'sz_bird', (0.18, 0.20, 0.30), noise=0.0); out = []
    for k in range(n):
        s = 0.045
        b = pr.add(*tube([(-s * 0.5, 0, 0), (0, 0, 0), (s * 0.45, 0, 0.004)], [s * 0.09, s * 0.14, s * 0.06], 6))
        w = [pr.add([(-s * 0.18, 0, 0), (s * 0.18, 0, 0), (0.0, sd * s * 0.95, 0), (-s * 0.32, sd * s * 0.7, 0)], [(0, 1, 2, 3)]) for sd in (-1, 1)]
        out.append((b, w, rng.uniform(2.0, 2.6), rng.uniform(0.95, 1.35), rng.uniform(0, 6.28), rng.uniform(2.6, 3.6)))
    pr.build(kit.bpy, [m], kit.coll, smooth=False)
    return {'parts': pr, 'birds': out, 'n': n}


def birds_pose(Bd, t):
    pr = Bd['parts']; pres = calm(t)
    for i, (b, wings, r, h, a0, flap) in enumerate(Bd['birds']):
        a = a0 + 0.42 * t; rr = r + (1 - pres) * 7.0
        P = (rr * math.cos(a), rr * math.sin(a) * 0.7 + 0.3, h + W.lift(t) + (1 - pres) * 2.0 + 0.06 * math.sin(0.8 * t + a0)); yaw = a + math.pi / 2
        amp = math.radians(12 + 30 * (0.5 + 0.5 * math.sin(0.5 * t + a0))) * math.sin(2 * math.pi * flap * t)
        if pres < 0.02:
            pr.hide(b); [pr.hide(w) for w in wings]; continue
        R = rz(yaw); pr.set(b, P, R)
        for w, sd in zip(wings, (-1, 1)): pr.set(w, P, R @ rx(sd * amp))
    pr.commit()


def build_flutter(kit, D, rng, n_fly=5):
    """Butterflies: bodies and flapping wings."""
    pr = Parts('fs_flutter'); out = []
    cols = [(0.97, 0.52, 0.36), (0.99, 0.80, 0.30), (0.70, 0.84, 0.98), (0.92, 0.62, 0.86), (1.0, 0.66, 0.22)]
    mats = [M.paint(kit, D, 'sz_bug', (0.12, 0.10, 0.16), noise=0.0)] + [M.paint(kit, D, f'sz_wing{k}', c, noise=0.0) for k, c in enumerate(cols)]
    for k in range(n_fly):
        b = pr.add(*tube([(-0.008, 0, 0), (0.008, 0, 0)], [0.0025, 0.0025], 6), m=0)
        ws = []
        for sd in (-1, 1):
            V = [(0, 0, 0)] + [(0.020 * math.cos(a) * (1 + 0.3 * math.sin(2 * a)) - 0.002, sd * 0.024 * abs(math.sin(a)) + sd * 0.002, 0) for a in np.linspace(-0.3, math.pi + 0.3, 10)]
            ws.append(pr.add(V, [(0, i, i + 1) for i in range(1, 10)], m=1 + k % 5))
        out.append((b, ws, rng.uniform(-1.4, 1.4), rng.uniform(-0.7, 0.8), rng.uniform(0, 6.28)))
    pr.build(kit.bpy, mats, kit.coll, smooth=False)
    return {'parts': pr, 'bugs': out}


def flutter_pose(Fl, t):
    pr = Fl['parts']; pres = calm(t)
    for b, ws, hx, hy, ph in Fl['bugs']:
        x = hx + 0.35 * math.sin(0.55 * t + ph) + 0.12 * math.sin(1.7 * t + 2 * ph); y = hy + 0.22 * math.sin(0.43 * t + 1.3 * ph)
        z = gz(x, y, t) + 0.12 + 0.06 * math.sin(1.3 * t + ph) + 0.03 * abs(math.sin(5.0 * t + ph))
        yaw = math.atan2(0.22 * 0.43 * math.cos(0.43 * t + 1.3 * ph), 0.35 * 0.55 * math.cos(0.55 * t + ph)); amp = 0.15 + 1.0 * abs(math.sin(2 * math.pi * 4.5 * t + ph))
        if pres < 0.5 or abs(x) > W.HX - 0.02 or abs(y) > W.HY - 0.02 or W.lake_r(x, y) < 1.0:
            pr.hide(b); [pr.hide(w) for w in ws]; continue
        R = rz(yaw); pr.set(b, (x, y, z), R, 1.6)
        for i, w in enumerate(ws): pr.set(w, (x, y, z), R @ rx((-1 if i == 0 else 1) * amp), 1.6)
    pr.commit()


def build_critters(kit, D, rng):
    """The rabbit (about 9 cm long), facing +x."""
    pr = Parts('fs_critters')
    mats = [M.paint(kit, D, 'sz_rabbit', (0.80, 0.70, 0.60)), M.paint(kit, D, 'sz_rabbitw', (0.99, 0.96, 0.92), noise=0.0)]
    rb = [pr.add(*_ell((0, 0, 0.032), (0.042, 0.030, 0.030), 2), m=0), pr.add(*_ell((0.036, 0, 0.056), (0.020, 0.018, 0.019), 2), m=0),
          pr.add(*_ell((0.030, 0.008, 0.088), (0.006, 0.004, 0.022), 1), m=0), pr.add(*_ell((0.030, -0.008, 0.088), (0.006, 0.004, 0.022), 1), m=0),
          pr.add(*_ell((-0.044, 0, 0.040), (0.011, 0.011, 0.011), 1), m=1)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'rabbit': rb}


RK = 1.6
RABBIT_PATH = [(-1.30, -0.20), (-1.05, 0.05), (-1.45, 0.25), (-0.80, 0.20), (-0.60, -0.10), (-1.00, -0.35), (-1.30, -0.20)]


def critters_pose(C, t):
    pr = C['parts']; rb = C['rabbit']
    if calm(t) > 0.95:
        cyc = 0.77; hopn = int(t // cyc); f = (t % cyc) / 0.32
        u0 = (hopn * 0.035) % 1.0; u1 = ((hopn + 1) * 0.035) % 1.0
        p0, hd = path_at(RABBIT_PATH, u0); p1, _ = path_at(RABBIT_PATH, u1)
        if f < 1: p = p0 + (p1 - p0) * W.sm(0, 1, f); hop = 0.045 * math.sin(math.pi * f)
        else: p = p1; hop = 0.0
        z = gz(p[0], p[1], t) + hop * RK; R = rz(hd); sit = 1.0 if f >= 1 else 0.0
        for j in rb: pr.set(j, (p[0], p[1], z), R @ ry(-0.25 * sit), RK)
    else:
        for j in rb: pr.hide(j)
    pr.commit()


# ============================================================================== the child in the yellow raincoat
def build_girl(kit, D):
    pr = Parts('fs_girl')
    mats = [M.paint(kit, D, 'sz_coat', (1.0, 0.82, 0.16)), M.paint(kit, D, 'sz_skin', (0.66, 0.44, 0.32), noise=0.0),
            M.paint(kit, D, 'sz_hair', (0.20, 0.12, 0.10), noise=0.0), M.paint(kit, D, 'sz_hood', (1.0, 0.76, 0.12)),
            M.paint(kit, D, 'sz_boots', (0.90, 0.16, 0.14), noise=0.0), M.paint(kit, D, 'sz_umb', (1.0, 0.85, 0.12), noise=0.0),
            M.paint(kit, D, 'sz_umb2', (0.98, 0.62, 0.10), noise=0.0), M.paint(kit, D, 'sz_umbstick', (0.30, 0.20, 0.18), noise=0.0)]
    g = {}
    g['legL'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.10)], [0.012, 0.011], 8), m=1)
    g['legR'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.10)], [0.012, 0.011], 8), m=1)
    g['bootL'] = pr.add(*_ell((0.008, 0, -0.100), (0.024, 0.015, 0.020), 1), m=4)
    g['bootR'] = pr.add(*_ell((0.008, 0, -0.100), (0.024, 0.015, 0.020), 1), m=4)
    g['dress'] = pr.add(*cone((0, 0, 0.0), 0.066, 0.13, 16, 0.032), m=0)
    g['torso'] = pr.add(*_ell((0, 0, 0.14), (0.036, 0.042, 0.042), 2), m=0)
    g['head'] = pr.add(*_ell((0, 0, 0.215), (0.040, 0.040, 0.042), 2), m=1)
    g['hair'] = pr.add(*_ell((-0.014, 0, 0.222), (0.040, 0.043, 0.040), 2), m=2)
    g['plait'] = pr.add(*tube([(-0.03, 0, 0.21), (-0.05, 0, 0.17), (-0.052, 0, 0.14)], [0.010, 0.009, 0.007], 6), m=2)
    g['hood'] = pr.add(*_ell((-0.012, 0, 0.226), (0.047, 0.047, 0.044), 2), m=3)
    g['armL'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.085)], [0.010, 0.009], 6), m=0)
    g['armR'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.085)], [0.010, 0.009], 6), m=0)
    # the yellow umbrella: a shaft up from her right hand, a round canopy of two yellows, a tip and a hooked handle
    g['shaft'] = pr.add(*tube([(0, 0, -0.04), (0, 0, 0.30)], [0.006, 0.006], 6), m=7)
    g['hook'] = pr.add(*tube([(0, 0, -0.04), (0.012, 0, -0.058), (0.024, 0, -0.045)], [0.0045, 0.0045, 0.0045], 6), m=7)
    g['canopy'] = pr.add(*cone((0, 0, 0.0), 0.135, 0.062, 18, 0.012), m=5)
    g['canopy2'] = pr.add(*cone((0, 0, 0.0), 0.138, 0.012, 18, 0.1385), m=6)
    g['tip'] = pr.add(*_ell((0, 0, 0.066), (0.006, 0.006, 0.008), 1), m=7)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'g': g}


GK = 1.7
CHILD_PATH = [np.array([-1.76, -0.84]), np.array([-1.30, -0.80]), np.array([W.PUDDLE[0] - 0.40, W.PUDDLE[1] + 0.02])]


def umbrella_open(t):
    """0 shut, 1 open: it pops open when she has run in (a small overshoot), shuts when the rain has stopped, opens again to dance at the end? no: stays shut."""
    B = W.B; o = W.sm(B.umbrella0, B.umbrella1, t) * (1 - W.sm(B.drop1 + 0.2, B.drop1 + 1.0, t))
    u = min(1.0, max(0.0, (t - B.umbrella0) / (B.umbrella1 - B.umbrella0)))
    return o * (1.0 + 0.10 * math.sin(math.pi * u) * (t < B.umbrella1 + 0.4))


def girl_pose(G_, t):
    """She runs in from the left when the first drops fall, pops her umbrella open, jumps in the puddle (the landings are the
    splashes), shuts the umbrella when the sun is back, looks at the rainbow, and jumps once more at the very end."""
    B = W.B; pr = G_['parts']; g = G_['g']; k_ = GK
    if t < B.child0:
        for v in g.values(): pr.hide(v)
        pr.commit(); return None
    run_end = B.child0 + 1.9
    u = W.sm(B.child0, run_end, t); p, hd = path_at(CHILD_PATH, u)
    running = B.child0 < t < run_end
    face_cam = math.atan2(-0.88, 0.47)
    def turn_to(a0, a1, f): return a0 + ((((a1 - a0) + math.pi) % (2 * math.pi)) - math.pi) * f
    yaw = turn_to(hd, face_cam + 0.5, W.sm(run_end - 0.3, run_end + 0.2, t))
    sw = math.sin(2 * math.pi * 2.8 * t) if running else 0.0
    k, ph = W.jump_phase(t); jump = 0.075 * max(0.0, math.sin(2 * math.pi * ph)) if k >= 0 else 0.0
    # the happy jump at the end: lands on chord2 (landings()[-1])
    jf = (t - (B.chord2 - 0.8)) / W.JUMP_T
    if 0 <= jf < 0.5: jump = max(jump, 0.075 * math.sin(2 * math.pi * jf))
    z0 = gz(p[0], p[1], t) + (0.112 + jump) * k_
    root = np.array([p[0], p[1], z0]); R0 = rz(yaw); lean = 0.12 * W.win(t, B.child0, run_end, 0.3)
    Rb = R0 @ ry(lean)
    sl = 1.0 if (k >= 0 or jf > 0) else 0.0
    for kk, sd, phs in (('legL', 1, 0.0), ('legR', -1, math.pi)):
        a = 0.5 * sw * (1 if phs == 0 else -1) - 0.5 * min(1.0, jump / 0.075) * (1 if phs == 0 else -1) * 0.0 + 0.35 * min(1.0, jump / 0.075)
        Rl = R0 @ ry(a); hip = root + R0 @ np.array([0, sd * 0.018 * k_, 0.0])
        pr.set(g[kk], hip, Rl, k_); pr.set(g['boot' + kk[-1]], hip, Rl, k_)
    for kk in ('dress', 'torso', 'head', 'hair', 'plait', 'hood'): pr.set(g[kk], root, Rb, k_)
    sh = lambda sd: root + Rb @ (np.array([0.0, sd * 0.042, 0.168]) * k_)
    op = umbrella_open(t)
    wave = W.win(t, B.drop1 + 1.5, B.drop1 + 4.5, 0.4) * math.sin(2 * math.pi * 2.0 * t)
    cheer = W.win(t, B.chord2 - 0.8, B.chord2 + 0.8, 0.2)
    aL = ry(-0.45 * sw) if running else I3
    aL = aL @ ry(-2.6 * wave * 0.0) if False else aL
    if t > B.drop1 + 1.5 and not running:
        aL = ry(-2.5) @ rx(0.35 * math.sin(2 * math.pi * 1.8 * t)) * 1.0 if W.win(t, B.drop1 + 1.5, B.drop1 + 4.5, 0.4) > 0.5 else aL     # she waves at the rainbow
    if cheer > 0.01: aL = rx(2.5 * cheer) @ ry(-0.2 * cheer)
    aR = ry(-2.9)                                                    # the umbrella arm straight up (hand at the shaft)
    if op < 0.02 and cheer < 0.01 and not running: aR = I3
    if running and op < 0.02: aR = ry(0.45 * sw)
    if cheer > 0.01: aR = rx(-2.5 * cheer) @ ry(-0.2 * cheer)
    pr.set(g['armL'], sh(1), Rb @ aL, k_); pr.set(g['armR'], sh(-1), Rb @ aR, k_)
    # the umbrella: carried shut on the shoulder while she runs, open over her head in the rain, shut and held down after
    hold = sh(-1) + Rb @ aR @ np.array([0.0, 0.0, -0.09]) * k_ if False else sh(-1) + Rb @ aR @ (np.array([0, 0, -0.085]) * k_)
    shut_down = ry(-0.7)
    up = 1.0 if (op > 0.02) else 0.0
    Ru = Rb @ (ry(-0.0) if up else ry(1.25))                          # shut: tilted forward, shaft pointing along her arm
    if up:
        pr.set(g['shaft'], hold + Rb @ np.array([0, 0, 0.0]), Rb, k_); pr.set(g['hook'], hold, Rb, k_)
        top = hold + Rb @ np.array([0, 0, 0.26 * k_])
        sx = max(0.12, op); pr.set(g['canopy'], top, Rb, (sx * k_, sx * k_, (0.5 + 0.5 * op) * k_)); pr.set(g['canopy2'], top, Rb, (sx * k_, sx * k_, k_))
        pr.set(g['tip'], top + Rb @ np.array([0, 0, 0.0]), Rb, (sx * k_, sx * k_, op * k_))
    else:
        pr.set(g['shaft'], hold, Ru, k_); pr.set(g['hook'], hold, Ru, k_)
        for nm in ('canopy', 'canopy2', 'tip'): pr.set(g[nm], hold + Ru @ np.array([0, 0, 0.26 * k_]), Ru, (0.14 * k_, 0.14 * k_, 0.9 * k_))
    pr.commit()
    return root


# ============================================================================== easter eggs
def build_eggs(kit, D):
    pr = Parts('fs_eggs')
    mats = [M.paint(kit, D, 'sz_ball', (0.92, 0.18, 0.16), noise=0.0), M.paint(kit, D, 'sz_ballw', (0.99, 0.96, 0.90), noise=0.0),
            M.paint(kit, D, 'sz_car', (0.20, 0.46, 0.86), noise=0.0), M.paint(kit, D, 'sz_wheel', (0.12, 0.12, 0.16), noise=0.0),
            M.paint(kit, D, 'sz_duck', (1.0, 0.84, 0.16), noise=0.0), M.paint(kit, D, 'sz_beak', (1.0, 0.52, 0.12), noise=0.0),
            M.paint(kit, D, 'sz_can', (0.22, 0.62, 0.42)), M.paint(kit, D, 'sz_canwater', (0.40, 0.76, 1.0), noise=0.0)]
    e = {}
    e['ball'] = pr.add(*sphere((0, 0, 0), (0.040, 0.040, 0.040), 2), m=0)
    e['band'] = pr.add(*cone((0, 0, -0.006), 0.0412, 0.012, 20, 0.0412), m=1)
    e['car'] = [pr.add(*box((0, 0, 0.012), (0.075, 0.036, 0.020)), m=2), pr.add(*box((-0.006, 0, 0.030), (0.036, 0.032, 0.018)), m=2)] + \
               [pr.add(*tube([(wx, -0.021, 0.004), (wx, 0.021, 0.004)], [0.009, 0.009], 10), m=3) for wx in (-0.024, 0.024)]
    e['duck'] = [pr.add(*_ell((0, 0, 0.012), (0.030, 0.022, 0.018), 2), m=4), pr.add(*_ell((0.020, 0, 0.038), (0.014, 0.014, 0.014), 2), m=4),
                 pr.add(*_ell((0.036, 0, 0.036), (0.009, 0.006, 0.004), 1), m=5), pr.add(*_ell((-0.030, 0, 0.022), (0.008, 0.010, 0.006), 1), m=4)]
    # a green watering can on the meadow: its water rises while it rains (the rain fills it)
    e['can'] = [pr.add(*tube([(0, 0, 0), (0, 0, 0.075)], [0.042, 0.038], 14), m=6), pr.add(*tube([(0.034, 0, 0.035), (0.075, 0, 0.075), (0.105, 0, 0.098)], [0.009, 0.007, 0.006], 8), m=6),
                pr.add(*tube([(-0.040, 0, 0.068), (-0.078, 0, 0.056), (-0.072, 0, 0.026), (-0.040, 0, 0.014)], [0.006, 0.006, 0.006, 0.006], 6), m=6)]
    e['canwater'] = pr.add(*disc((0, 0, 0), 0.036, 14), m=7)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'e': e}


BALL = (-1.00, -W.HY - 0.004, -0.115)          # a lost red ball in the soil of the front face (obvious)
CAR = (W.HX - 0.012, 0.28, -0.075)              # a toy car in the soil of the right face (hidden)
CAN = (0.02, -0.80)                            # the watering can on the meadow
DUCK_C = (W.LAKE[0] - 0.06, W.LAKE[1] + 0.02)
CK = 1.7


def eggs_pose(E, t):
    B = W.B; pr = E['parts']; e = E['e']; L = W.lift(t)
    pr.set(e['ball'], (BALL[0], BALL[1], BALL[2] + L), I3, 1.0); pr.set(e['band'], (BALL[0], BALL[1], BALL[2] + L), rx(math.pi / 2), 1.0)
    for j in e['car']: pr.set(j, (CAR[0], CAR[1], CAR[2] + L), I3)
    # the rubber duck bobs round the lake, turning slowly; the rain makes it bob harder
    a = 0.30 * t + 1.0; r = 0.5 + 0.15 * W.rain_k(t); x = DUCK_C[0] + 0.32 * math.cos(a) * 0.9; y = DUCK_C[1] + 0.17 * math.sin(a)
    lv = W.lake_level(t) + L; bob = 0.004 * math.sin(2 * math.pi * (0.9 + 0.8 * W.rain_k(t)) * t)
    Rd = rz(a + math.pi / 2) @ rx(0.08 * math.sin(2 * math.pi * 0.9 * t))
    for j in e['duck']: pr.set(j, (x, y, lv - 0.006 + bob), Rd, 1.5)
    # the watering can fills up
    cz = gz(CAN[0], CAN[1], t) - 0.003; R = rz(2.2)
    for j in e['can']: pr.set(j, (CAN[0], CAN[1], cz), R, CK)
    fill = W.keys(t, [(B.drop0 + 2.0, 0.0), (B.drop1, 1.0)])
    pr.set(e['canwater'], (CAN[0], CAN[1], cz + (0.030 + 0.036 * fill) * CK), R, CK * (fill > 0.02))
    pr.commit()


# ============================================================================== the series mascot: a little snail
SNAIL_HOME = (1.42, -W.HY + 0.07)
SK = 4.6     # the mascot: bigger than the fossil film (it is this film's joke), about 24 cm long


def build_snail(kit, D):
    """The series' silent recurring creature: a little snail with a coral and gold shell on the front right corner. In this
    film it is the visual joke: while the people run for cover, the snail LOVES the rain (snails do): out of its shell, tall,
    rocking happily, eyes wiggling."""
    pr = Parts('fs_snail')
    mats = [M.paint(kit, D, 'sz_snailshell', (0.96, 0.52, 0.40), noise=0.0), M.paint(kit, D, 'sz_snailband', (0.99, 0.82, 0.38), noise=0.0),
            M.paint(kit, D, 'sz_snailbody', (0.86, 0.84, 0.66), noise=0.0), M.paint(kit, D, 'sz_snaileye', (0.10, 0.10, 0.18), noise=0.0)]
    s = {'shell': pr.add(*sphere((0, 0, 0.030), (0.026, 0.017, 0.028), 2), m=0), 'band': pr.add(*sphere((0.0, 0, 0.030), (0.016, 0.0185, 0.018), 2), m=1),
         'body': pr.add(*sphere((0.012, 0, 0.007), (0.040, 0.012, 0.008), 2), m=2)}
    s['stalks'] = [pr.add(*tube([(0, 0, 0), (0.004, sd * 0.004, 0.022)], [0.0025, 0.0018], 5), m=2) for sd in (-1, 1)]
    s['eyes'] = [pr.add(*sphere((0.004, sd * 0.004, 0.024), (0.0035, 0.0035, 0.0035), 1), m=3) for sd in (-1, 1)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 's': s}


def snail_pose(Sn, t):
    B = W.B; pr = Sn['parts']; s = Sn['s']
    x, y = SNAIL_HOME; x = x - 0.06 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 30.0)); p = np.array([x, y, gz(x, y, t) - 0.002]); hdg = -math.pi / 2 + 0.5
    joy = W.win(t, B.snail0, B.drop1 + 5.0, 0.8)                     # it loves the rain
    look = W.win(t, 0.6, B.sun1, 0.6)                                 # at the start it looks up at the sky
    rock = 0.30 * joy * math.sin(2 * math.pi * 1.1 * t)               # rocking its shell side to side
    wave = W.sm(B.chord1 - 0.3, B.chord1 + 0.4, t) * 0.7 * math.sin(2 * math.pi * 1.6 * t) * (1 - W.sm(B.chord1 + 3.0, B.chord1 + 3.6, t))
    up = 1.0 + 0.9 * joy + 0.5 * look + 0.5 * wave
    R = rz(hdg) @ ry(-0.30 * look - 0.25 * joy) @ rx(rock)
    pr.set(s['shell'], p, R, SK); pr.set(s['band'], p, R, SK)
    pr.set(s['body'], p, R, (SK, SK, SK))
    head = p + R @ (np.array([0.040, 0, 0.010]) * SK)
    for j, ph in zip(s['stalks'] + s['eyes'], (0, 1, 0, 1)):
        wob = rx(0.25 * math.sin(2 * math.pi * 0.5 * t + ph) + (0.55 * joy * math.sin(2 * math.pi * 1.7 * t + 2 * ph) + wave * (1 if ph == 0 else -1)))
        pr.set(j, head, R @ wob, (SK, SK, up * SK))
    pr.commit()
