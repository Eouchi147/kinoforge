"""Where does rain come from? The set pieces of single beats (bpy + numpy). Every pose is a pure function of t.

  cloud       the cloud forms right above the slice from tiny drops, grows, turns grey and heavy, thins out and drifts away; a
              small new one starts at the end (round and around)
  vapour      invisible water rising from the lake: pale wavy ribbons that thin out as they climb; tiny white dots at their tips
              gather into the cloud (the drops that make it)
  soil        the cut faces: the wet front sinks through the soil, little drops sink with it, the water table rises in the sand
  lake        the lake, the rain's ripples on it, the puddle and the splashes when the child lands in it
  boat        a paper boat sails down the brook into the lake
  lens        a magnifier window on the cloud: tiny drops bump and stick into bigger and bigger drops until one fat raindrop falls
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
import szui as UI
from szgeo import Parts, sphere, tube, cone, box, disc, rz, ry, rx, I3

gz = lambda x, y, t: float(W.top_h(np.array([x]), np.array([y]), t)[0])


def h01(i, c, salt=0):
    """A repeatable pseudo-random number in 0..1 for (i, c)."""
    h = (int(i) * 374761393 + int(c) * 668265263 + salt * 2246822519) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffffff) / float(0xffffff)


# ============================================================================== the cloud
CLOUD_P = np.array([0.25, 0.05, 2.75])     # where it forms: right above the slice (absolute z; the slice floats at about 1.4)


def _lumpy(c, r, seed, sub=2, amp=0.07):
    V, F = cw._icosphere(sub); V = cw._lumpy(V, seed, amp, 2.6, 0.06, 7.0); return V * np.asarray(r, float) + np.asarray(c, float), F


def build_cloud(kit, D, name, seed, rows, drive):
    """A storybook cumulus: flat-bottomed, a few rows of overlapping puffs. rows: [(z, [x...], radius)]; each puff has a delay."""
    rng = np.random.default_rng(seed); pr = Parts(name); m = M.paint(kit, D, name + 'm', (1.0, 0.98, 0.94), rough=0.95, noise=0.0, drive=drive)
    puffs = []
    for z, xs, r in rows:
        for x in xs:
            rr = r * rng.uniform(0.85, 1.12); i = pr.add(*_lumpy((0, 0, 0), (rr * 1.15, rr * 0.9, rr * 0.8), seed + len(puffs)), 0)
            puffs.append((i, x + rng.uniform(-0.04, 0.04), rng.uniform(-0.12, 0.12), z, rr, rng.uniform(0.0, 1.0)))
    pr.build(kit.bpy, [m], kit.coll)
    return {'parts': pr, 'puffs': puffs}


def cloud_pose(Cl, t, grow, center, ph=0.0):
    pr = Cl['parts']
    for i, x, y, z, r, d in Cl['puffs']:
        k = W.sm(d * 0.65, d * 0.65 + 0.35, grow) if grow > 0.001 else 0.0
        if k < 0.01: pr.hide(i); continue
        bob = 0.02 * math.sin(0.7 * t + 3 * d + ph)
        pr.set(i, center + np.array([x * (0.35 + 0.65 * grow), y, z * (0.5 + 0.5 * grow) + bob]), I3, k * (0.55 + 0.45 * grow))
    pr.commit()


def cloud_state(t):
    """(grow1, center1, grow2, center2) of the big cloud and of the small new one; the big one drifts right as it thins."""
    B = W.B
    g1 = W.sm(B.cloud0, B.cloud1, t) * (1 - 0.92 * W.sm(B.cshrink0, B.cshrink1, t))
    drift = W.sm(B.cshrink0, B.cshrink1 + 4, t)
    c1 = CLOUD_P + np.array([2.4 * drift, 0.6 * drift, 0.15 * drift])
    g2 = 0.62 * W.sm(B.cloud2a, B.cloud2b, t)
    c2 = CLOUD_P + np.array([-0.2, 0.0, -0.2])
    return g1, c1, g2, c2


# ============================================================================== invisible water
NR, NSEG = 7, 28
VAP_TOP = 2.55


def _rib_base(j):
    a = 2 * math.pi * j / NR + 0.4
    return W.LAKE[0] + 0.62 * W.LAKE[2] * math.cos(a), W.LAKE[1] + 0.62 * W.LAKE[3] * math.sin(a)


def rib_pt(j, s, t, h):
    """A point on ribbon j at fraction s of its length (height h reached): rises from the lake, wavers, leans toward the cloud."""
    x0, y0 = _rib_base(j); z0 = W.lake_level(t) + W.lift(t) + 0.02
    z = z0 + (VAP_TOP - z0) * h * s
    sway = 0.07 * math.sin(2 * math.pi * (1.3 * s - 0.28 * t) + 1.7 * j) * (0.3 + s) + 0.04 * math.sin(2 * math.pi * (2.6 * s - 0.5 * t) + j)
    x = x0 + (CLOUD_P[0] - 0.1 - x0) * 0.30 * s * s + sway
    y = y0 + (CLOUD_P[1] - y0) * 0.30 * s * s + 0.5 * sway * math.cos(j)
    return np.array([x, y, z])


def vap_amount(t):
    B = W.B; return max(W.win(t, B.vap0, B.vap1, 1.4), W.win(t, B.vap2a, B.vap2b, 1.4))


def vap_height(t):
    B = W.B
    if t > B.vap2a - 1.5: return W.sm(B.vap2a, B.vap2a + 4.5, t) * 0.78
    return W.sm(B.vapup0, B.vapup0 + 5.5, t)


def build_vapour(kit, D, rng):
    mat = M.mat_vapor(kit, D); V = []; F = []; FA = []; FE = []
    for j in range(NR):
        o = len(V)
        for k in range(NSEG + 1):
            s = k / NSEG; fa = W.sm(0.0, 0.10, s) * (1 - 0.72 * W.sm(0.45, 1.0, s))
            for side in (0, 1): V.append((0, 0, 0)); FA.append(fa); FE.append(0.0 if True else 1.0)
        for k in range(NSEG): a = o + 2 * k; F.append((a, a + 1, a + 3, a + 2))
    ob = cw.mk_mesh(kit.bpy, 'fs_vapour', V, F, [mat], None, False, kit.coll, {'fa': ('FLOAT', FA), 'fe': ('FLOAT', [1.0] * len(V))}); ob.visible_shadow = False
    # mist: tiny white dots that leave the ribbons' tips and gather into the cloud
    pr = Parts('fs_mist'); m = M.paint(kit, D, 'fs_mistm', (1.0, 0.99, 0.95), noise=0.0)
    dots = [(pr.add(*sphere((0, 0, 0), (0.024, 0.024, 0.024), 1), 0), i % NR, rng.uniform(0, 1), rng.uniform(-0.45, 0.45, 3)) for i in range(90)]
    pr.build(kit.bpy, [m], kit.coll)
    return {'ob': ob, 'mist': pr, 'dots': dots}


def vapour_pose(Vp, D, t):
    D.set('a_vap', vap_amount(t))
    ob = Vp['ob']; a = vap_amount(t)
    if a < 0.01: ob.hide_render = True
    else:
        ob.hide_render = False; h = vap_height(t); co = np.zeros((NR * (NSEG + 1) * 2, 3), np.float32); n = 0
        for j in range(NR):
            hj = min(1.0, h * (1.0 + 0.1 * math.sin(j * 2.3)))
            for k in range(NSEG + 1):
                s = k / NSEG; p = rib_pt(j, s, t, hj); q = rib_pt(j, min(1.0, s + 0.03), t, hj) - rib_pt(j, max(0.0, s - 0.03), t, hj)
                w = 0.028 + 0.030 * s; side = np.array([-q[1], q[0], 0.0]); side = side / (np.linalg.norm(side) + 1e-9) * w
                co[n] = p - side; co[n + 1] = p + side; n += 2
        ob.data.vertices.foreach_set('co', co.ravel()); ob.data.update()
    B = W.B; pr = Vp['mist']
    for i, j, d, off in Vp['dots']:
        t0 = B.cool0 + d * (B.cool1 - B.cool0 - 4.5); arrive = t0 + 4.2
        if not (t0 < t < arrive + 0.6): pr.hide(i); continue
        top = rib_pt(j, 1.0, t, 1.0); tgt = CLOUD_P + off * np.array([0.9, 0.45, 0.28]) + np.array([0, 0, -0.1])
        u = W.sm(t0 + 0.4, arrive, t); p = top + (tgt - top) * u + np.array([0.04 * math.sin(3 * t + d * 9), 0.0, 0.03 * math.cos(2.4 * t + d * 7)])
        k = W.sm(t0, t0 + 0.7, t) * (1 - W.sm(arrive - 0.2, arrive + 0.6, t))
        pr.set(i, p, I3, k)
    pr.commit()


# ============================================================================== water in the soil
def build_soil(kit, D, rng):
    """Overlays on the front and the right cut faces (just in front of them): wet soil, the water table; and little drops sinking."""
    mat = M.mat_soilwater(kit, D); obs = []
    def face(name, pts_fn, n=130, rows=44):
        V = []; F = []; DEP = []; ZS = []; UX = []
        for i in range(n + 1):
            u = i / n; x, y, ztop = pts_fn(u)
            for r in range(rows + 1):
                v = r / rows; z = ztop + (W.ZB - ztop) * v
                V.append((x, y, z)); DEP.append(ztop - z); ZS.append(z); UX.append(u * 3.6)
        for i in range(n):
            for r in range(rows):
                a = i * (rows + 1) + r; c = (i + 1) * (rows + 1) + r; F.append((a, c, c + 1, a + 1))
        ob = cw.mk_mesh(kit.bpy, name, V, F, [mat], None, False, kit.coll, {'dep': ('FLOAT', DEP), 'zs': ('FLOAT', ZS), 'ux': ('FLOAT', UX)})
        ob.visible_shadow = False; return ob
    def front(u):
        x = -W.HX + 2 * W.HX * u; y = -W.HY - 0.0035
        return x, y, float(W.slice_h(np.array([x]), np.array([-W.HY]), 0.0)[0])
    def right(u):
        y = -W.HY + 2 * W.HY * u; x = W.HX + 0.0035
        return x, y, float(W.slice_h(np.array([W.HX]), np.array([y]), 0.0)[0])
    obs = [face('fs_soil_front', front), face('fs_soil_right', right)]
    # sinking drops on the front face
    pr = Parts('fs_sinkers'); m = M.mat_glow(kit, D, 'fs_sinkm', (0.46, 0.80, 1.0), 1.5)
    drop = [(0, 0.020, 0), (0.0085, 0.0, 0), (0, -0.008, 0), (-0.0085, 0.0, 0)]
    items = [(pr.add(drop, [(0, 1, 2, 3)], 0), rng.uniform(-W.HX + 0.1, W.HX - 0.1), rng.uniform(0, 1), rng.uniform(0.6, 1.2)) for _ in range(34)]
    pr.build(kit.bpy, [m], kit.coll, smooth=False); pr.ob.visible_shadow = False
    return {'obs': obs, 'sink': pr, 'items': items}


def soil_pose(S, D, t):
    B = W.B
    fr = W.front(t) if t > B.drop0 + 0.8 else 0.0
    D.set('wfront', fr); D.set('gwl', W.gw(t))
    L = W.lift(t)
    for ob in S['obs']: ob.location = (0, 0, L)
    pr = S['sink']; act = W.sm(B.drop0 + 1.0, B.drop0 + 2.5, t) * (1 - W.sm(B.soak1 + 1.0, B.soak1 + 3.0, t))
    for i, x, ph, sp in S['items']:
        if act < 0.02: pr.hide(i); continue
        top = float(W.slice_h(np.array([x]), np.array([-W.HY]), 0.0)[0]); depth_max = max(0.06, min(0.5, fr + 0.05))
        age = (0.16 * sp * (t - B.drop0) + ph) % 1.0
        pr.set(i, (x, -W.HY - 0.0052, top - age * depth_max + L), I3, act * W.sm(0.0, 0.08, age) * (1 - W.sm(0.85, 1.0, age)))
    pr.commit()


# ============================================================================== lake, ripples, puddle, splashes
def disc_mesh(kit, name, cx, cy, rx_, ry_, mat, n=48):
    V = [(0, 0, 0)] + [(rx_ * math.cos(a), ry_ * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, n + 1)[:-1]]
    ob = cw.mk_mesh(kit.bpy, name, V, [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)], [mat], None, False, kit.coll); ob.visible_shadow = False
    return ob


def build_lake(kit, D, rng):
    mat = M.mat_water(kit, D)
    lake = disc_mesh(kit, 'fs_lake', 0, 0, W.LAKE[2] * 0.97, W.LAKE[3] * 0.97, mat)
    pud = disc_mesh(kit, 'fs_puddle', 0, 0, 1.0, 1.0, mat, 32)
    # ripple rings and splash droplets
    pr = Parts('fs_ripples'); rm = M.mat_glow(kit, D, 'fs_ripplem', (0.92, 0.98, 1.0), 1.1)
    def ring(r0, r1, n=24):
        V = []; F = []
        for k in range(n): a = 2 * math.pi * k / n; V += [(r0 * math.cos(a), r0 * math.sin(a), 0), (r1 * math.cos(a), r1 * math.sin(a), 0)]
        for k in range(n): a_ = 2 * k; b_ = (2 * ((k + 1) % n)); F.append((a_, a_ + 1, b_ + 1, b_))
        return V, F
    rings = [pr.add(*ring(0.84, 1.0), 0) for _ in range(26)]
    spl = Parts('fs_splash'); sm_ = M.mat_glow(kit, D, 'fs_splashm', (0.80, 0.94, 1.0), 1.4)
    drops = [spl.add(*sphere((0, 0, 0), (0.012, 0.012, 0.016), 1), 0) for _ in range(12)]
    pr.build(kit.bpy, [rm], kit.coll, smooth=False); spl.build(kit.bpy, [sm_], kit.coll)
    pr.ob.visible_shadow = False; spl.ob.visible_shadow = False
    return {'lake': lake, 'pud': pud, 'rp': pr, 'rings': rings, 'sp': spl, 'drops': drops}


def lake_pose(Lk, t):
    B = W.B; L = W.lift(t)
    Lk['lake'].location = (W.LAKE[0], W.LAKE[1], W.lake_level(t) + L)
    ps = W.puddle_size(t); px, py, prx, pry = W.PUDDLE
    Lk['pud'].location = (px, py, gz(px, py, t) + 0.004); Lk['pud'].scale = (prx * max(ps, 1e-3), pry * max(ps, 1e-3), 1.0); Lk['pud'].hide_render = ps < 0.02
    pr = Lk['rp']; rk = W.rain_k(t); zl = W.lake_level(t) + L + 0.003; zp = gz(px, py, t) + 0.008
    n = len(Lk['rings']); used = 0
    # raindrop rings on the lake and the puddle: each ring lives 1.2 s, then a new place
    for i in range(n - 6):
        T = 1.25 + 0.5 * h01(i, 0); age = (t * 1.0 + T * h01(i, 1)) % T; c = int((t + T * h01(i, 1)) // T)
        if rk < 0.04 or h01(i, c, 2) > rk * 1.6: pr.hide(Lk['rings'][i]); continue
        a = 2 * math.pi * h01(i, c, 3); rr = math.sqrt(h01(i, c, 4)) * 0.88
        on_lake = i % 3 != 0
        if on_lake: x = W.LAKE[0] + W.LAKE[2] * rr * math.cos(a); y = W.LAKE[1] + W.LAKE[3] * rr * math.sin(a); z = zl
        else:
            x = px + prx * ps * rr * math.cos(a); y = py + pry * ps * rr * math.sin(a); z = zp
            if ps < 0.2: pr.hide(Lk['rings'][i]); continue
        u = age / T; rad = 0.012 + 0.085 * u; pr.set(Lk['rings'][i], (x, y, z), I3, rad * (1 - W.sm(0.7, 1.0, u)))
    # the child's landings: three big rings and a crown of droplets
    sp = Lk['sp']; lands = W.landings()
    for q in range(6):
        i = Lk['rings'][n - 6 + q]; tl = lands[min(len(lands) - 1, q * max(1, len(lands) // 6))] if q < len(lands) else -9
        # ring q follows the q-th landing
        if q >= len(lands): pr.hide(i); continue
        tl = lands[q]; u = (t - tl) / 1.3
        if 0 <= u < 1: pr.set(i, (px, py, zp + 0.002), I3, (0.05 + 0.28 * u) * (1 - W.sm(0.75, 1.0, u)) * max(ps, 0.5))
        else: pr.hide(i)
    pr.commit()
    for k, j in enumerate(Lk['drops']):
        pr_ = None
        best = None
        for tl in lands:
            if -0.02 < t - tl < 0.7: best = tl
        if best is None: sp.hide(j); continue
        u = t - best; a = 2 * math.pi * k / len(Lk['drops']) + 0.4; v = 0.35 + 0.1 * (k % 3)
        sp.set(j, (px + v * u * math.cos(a) * 0.5 * 1.0, py + v * u * math.sin(a) * 0.5, zp + 0.012 + 0.55 * u - 1.5 * u * u), I3, 1.0 if (0.55 * u - 1.5 * u * u) > -0.01 else 0.0)
    sp.commit()


# ============================================================================== the paper boat
def build_boat(kit, D):
    pr = Parts('fs_boat'); mats = [M.paint(kit, D, 'sz_boathull', (0.96, 0.40, 0.30), noise=0.0), M.paint(kit, D, 'sz_boatsail', (0.99, 0.97, 0.92), noise=0.0)]
    hull = pr.add([(-0.045, -0.018, 0.028), (0.045, -0.018, 0.028), (0.030, -0.008, 0.0), (-0.030, -0.008, 0.0), (-0.045, 0.018, 0.028), (0.045, 0.018, 0.028), (0.030, 0.008, 0.0), (-0.030, 0.008, 0.0)],
                   [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)], 0)
    sail = pr.add([(-0.026, 0, 0.026), (0.030, 0, 0.026), (0.0, 0, 0.082)], [(0, 1, 2), (0, 2, 1)], 1)
    pr.build(kit.bpy, mats, kit.coll)
    P = np.array([tuple(p) for p in cw.catmull([tuple(q) for q in W.RIVER], 400)])
    P = P[(np.abs(P[:, 0]) < W.HX - 0.06) & (np.abs(P[:, 1]) < W.HY - 0.06)]
    return {'parts': pr, 'ids': (hull, sail), 'path': P[:, :2]}


def boat_pose(Bt, t):
    B = W.B; pr = Bt['parts']; hull, sail = Bt['ids']
    if t < B.boat0:
        pr.hide(hull); pr.hide(sail); pr.commit(); return
    u = min(1.0, (t - B.boat0) * 0.14 / (np.sum(np.linalg.norm(np.diff(Bt['path'], axis=0), axis=1))))
    from szlife import path_at
    p, hd = path_at(Bt['path'], u)
    w, d = W.channel(t); on_lake = W.lake_r(p[0], p[1]) < 1.0
    z = (W.lake_level(t) - 0.004 if on_lake else float(W.slice_h(np.array([p[0]]), np.array([p[1]]), t)[0]) - 0.5 * d) + W.lift(t) + 0.004 * math.sin(2 * math.pi * 0.8 * t)
    R = rz(hd) @ rx(0.10 * math.sin(2 * math.pi * 0.7 * t)); sc = 1.8 * W.sm(B.boat0, B.boat0 + 0.5, t)
    pr.set(hull, (p[0], p[1], z), R, sc); pr.set(sail, (p[0], p[1], z), R, sc); pr.commit()


# ============================================================================== the magnifier window (a million tiny drops join)
DL = 4.5     # the window hangs 4.5 m in front of the camera (in front of the block), in the picture layer
NLEAF = 32


class Lens:
    def __init__(self, kit, D, cam, target_world):
        bpy = kit.bpy; self.kit = kit; self.D = D; self.cam = cam; self.target = np.asarray(target_world, float)
        hw = DL * 18.0 / cam.ob.data.lens; hh = hw * 9 / 16; self.hh = hh
        self.R = 0.47 * hh
        Rl = self.R; self.obs = []
        def own(ob, z):
            ob.parent = cam.ob; ob.matrix_parent_inverse.identity(); ob.location = (0, 0, -DL + z); self.obs.append(ob)
            for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
            return ob
        # inside the cloud: soft blue-grey, lighter in the middle, a few faint swirls
        m = cw._new_mat(bpy, 'fs_lensrock'); g = cw.G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; s = g.sep(P)
        r = g.vmath('LENGTH', g.comb(s[0], s[1], 0.0)); f = g.math('MULTIPLY', r, 1.0 / Rl, clamp=True)
        col = g.mix(f, cw.srgb((0.70, 0.82, 0.93)), cw.srgb((0.40, 0.55, 0.74)))
        col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', g.noise(P, 5.0 / Rl, 3.0).outputs['Fac'], 0.5), 0.3), col, cw.srgb((0.95, 0.98, 1.0)), 'OVERLAY')
        cw._finish(g, g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}))
        V = [(0, 0, 0)] + [(Rl * math.cos(a), Rl * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 65)[:-1]]
        self.disc = own(cw.mk_mesh(bpy, 'fs_lensdisc', V, [(0, 1 + i, 1 + (i + 1) % 64) for i in range(64)], [m], None, False, kit.coll), 0.0)
        # the drops: a tree of merges. Leaves wander in the window; pairs approach, touch and become one drop of twice the volume.
        rng = np.random.default_rng(41)
        homes = []
        while len(homes) < NLEAF:
            p = rng.uniform(-0.74, 0.74, 2) * Rl
            if np.hypot(*p) < 0.72 * Rl and all(np.hypot(*(p - q)) > 0.20 * Rl for q in homes): homes.append(p)
        homes = sorted(homes, key=lambda p: (round(p[1] / (0.5 * Rl)), p[0]))
        self.levels = []                       # per level: list of (centre, members)
        cur = [(np.array(h), [i]) for i, h in enumerate(homes)]
        self.levels.append(cur)
        while len(cur) > 1:
            nxt = []
            for a in range(0, len(cur), 2):
                mem = cur[a][1] + cur[a + 1][1]; nxt.append((np.mean([homes[i] for i in mem], axis=0), mem))
            self.levels.append(nxt); cur = nxt
        self.r0 = 0.060 * Rl
        pr = Parts('fs_lensfx'); self.ent = []
        for L, lv in enumerate(self.levels):
            for g, (c, mem) in enumerate(lv):
                rad = self.r0 * (len(mem) ** (1 / 3.0)) * 1.12
                V = [(0, 0, 0)] + [(math.cos(a), math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 21)[:-1]]
                Fc = [(0, 1 + i, 1 + (i + 1) % 20) for i in range(20)]
                rim = pr.add(V, Fc, 0); body = pr.add(V, Fc, 1); hl = pr.add([(0.30 * math.cos(a) - 0.30, 0.20 * math.sin(a) + 0.34, 0) for a in np.linspace(0, 2 * math.pi, 9)[:-1]] + [(-0.30, 0.34, 0)],
                                                                         [(8, i, (i + 1) % 8) for i in range(8)], 2)
                self.ent.append((L, g, c, rad, rim, body, hl, rng.uniform(0, 6.28, 2)))
        pr.build(bpy, [M.mat_glow(kit, D, 'fs_drimm', (0.30, 0.52, 0.86), 1.0), M.mat_glow(kit, D, 'fs_drbody', (0.70, 0.89, 1.0), 1.15), M.mat_glow(kit, D, 'fs_drhl', (1.0, 1.0, 1.0), 1.4)], kit.coll, smooth=False)
        self.fx = own(pr.ob, 0.004); self.pr = pr
        self.center = None
        self._build_frame(kit, D, own, Rl)

    def tm(self, L, g):
        """When level L group g exists from (the merge time), staggered a little per group."""
        B = W.B
        if L == 0: return -1e9
        base = [B.lensj1, B.lensj2, B.lensj3, B.lensj4, B.lensj5][L - 1]
        return base + 0.35 * (h01(g, L) - 0.5) * (1 if L < 5 else 0)

    def _build_frame(self, kit, D, own, Rl):
        """The storybook lens frame (Sam 24 Oct: improve the frame): a rich gold ring with a bevel, a studded rim, a glass glint,
        a short plum grip, and the small gold ring at the bone with two fine gold connector lines. Crisp pieces in the words'
        layer (`crisp`, handed to the art adapter by blender.py): they stay sharp over the brushwork."""
        bpy = kit.bpy; self.crisp = []; al = 'a_lens'
        def mats3(tag): return [UI.mat_shadow(kit, D, f'fs_lf{tag}s', al, 0.40), UI.mat_gold(kit, D, f'fs_lf{tag}g', al),
                                UI.mat_flat(kit, D, f'fs_lf{tag}c', al, (1.0, 0.98, 0.90), taper=True),
                                UI.mat_gold(kit, D, f'fs_lf{tag}p', al, ((0.16, 0.07, 0.20), (0.36, 0.17, 0.36), (0.62, 0.38, 0.52)))]
        fl = UI.Flat(); rc = Rl + 0.014; Pc, Nc = UI.circle_loop(rc, 120); Pw, Nw = UI.circle_loop(Rl, 120)
        fl.band(Pc, Nc, [(0.085, 1.0, 0.0), (0.040, 0.55, 0.0), (-0.020, 0.0, 0.0)], 0, 0.0, at=(0.012, -0.034))
        fl.band(Pc, Nc, [(0.043, 0.0, 0.08), (0.032, 1.0, 0.08)], 1, 0.0006)                    # a dark gold line round the outside
        fl.tube(Pc, Nc, 0.060, 1, 0.0012, grow=0.008)                                            # the bevelled gold ring
        fl.band(Pw, Nw, [(0.0, 0.0, 0.10), (-0.009, 1.0, 0.10)], 1, 0.0006)                     # a shadow line where the glass sinks in
        fl.band(Pc, Nc, [(0.0045, 0.0, 0.55), (0.0, 0.5, 0.92), (-0.0045, 1.0, 0.55)], 1, 0.0020)  # the fine bright line down the ring
        for q in range(12):                                                                       # studs
            a = 2 * math.pi * q / 12 + 0.26; c = np.array([rc * math.cos(a), rc * math.sin(a)]); Ps, Ns = UI.circle_loop(0.0125, 14)
            fl.fan(Ps, Ns, 0.0, 0.5, 0.40, 1, 0.0026, at=tuple(c)); fl.band(Ps, Ns, [(0.0, 0.0, 0.20), (-0.0045, 1.0, 0.95)], 1, 0.0028, at=tuple(c))
        # a glass glint: a slim bright crescent in the upper left and a small round one
        n = 18; ang = np.linspace(math.radians(112), math.radians(170), n); wd = 0.036 * np.sin(np.linspace(0, math.pi, n)) ** 0.8
        A = np.column_stack([(Rl * 0.84 + wd) * np.cos(ang), (Rl * 0.84 + wd) * np.sin(ang)]); Bq = np.column_stack([(Rl * 0.84 - wd) * np.cos(ang), (Rl * 0.84 - wd) * np.sin(ang)])
        fl.strip(A, Bq, 2, 0.0040, es=np.sin(np.linspace(0, math.pi, n)) * 0.62, ss=0.5)
        Pd, Nd = UI.circle_loop(0.022, 16); fl.fan(Pd, Nd, 0.0, 0.5, 0.5, 2, 0.0040, at=(-Rl * 0.70 * 0.86, Rl * 0.70 * 0.55 + 0.02))
        self.frame = own(fl.build(bpy, 'fs_lensframe', mats3('f'), kit.coll), 0.006)
        # the handle: a gold collar and a short plum grip (rotated about the window each frame, drawn under the ring)
        h = UI.Flat(); x0, x1, x2 = Rl + 0.00, Rl + 0.13, Rl + 0.33
        def bar(xa, xb, wa, wb, mat, z, rows=(0.45, 0.95, 0.30)):
            m = 8; xs = np.linspace(xa, xb, m); ws = np.linspace(wa, wb, m)
            top = np.column_stack([xs, ws]); mid = np.column_stack([xs, ws * 0.35]); bot = np.column_stack([xs, -ws])
            h.strip(top, mid, mat, z, es=0.0, ss=rows[0]); h.strip(mid, bot, mat, z, es=1.0, ss=rows[2])
        bar(x0, x0 + 0.075, 0.030, 0.036, 1, 0.0010)
        bar(x0 + 0.075, x2, 0.040, 0.046, 3, 0.0014)
        Pe, Ne = UI.circle_loop(0.046, 24); h.fan(Pe, Ne, 0.0, 0.5, 0.45, 3, 0.0014, at=(x2, 0.0))
        h.band(*UI.circle_loop(0.046, 24), [(0.003, 0.0, 0.2), (-0.006, 1.0, 0.8)], 1, 0.0020, at=(x2, 0.0))
        h.poly([(x0 + 0.075, 0.048), (x0 + 0.075 + 0.020, 0.048), (x0 + 0.075 + 0.020, -0.048), (x0 + 0.075, -0.048)], 1, 0.0018, ss=[0.8] * 4)
        h.strip(np.column_stack([np.linspace(x0 + 0.12, x2 - 0.01, 6), np.full(6, 0.022)]), np.column_stack([np.linspace(x0 + 0.12, x2 - 0.01, 6), np.full(6, 0.016)]), 2, 0.0024, es=0.5, ss=0.5)
        self.handle = own(h.build(bpy, 'fs_lenshandle', mats3('h'), kit.coll), 0.004)
        # the small ring on the fossil and two fine connector lines (rewritten each frame)
        rs = 0.075; r = UI.Flat(); Pr, Nr = UI.circle_loop(rs, 48)
        r.band(Pr, Nr, [(0.030, 1.0, 0.0), (0.012, 0.55, 0.0), (-0.004, 0.0, 0.0)], 0, 0.0, at=(0.006, -0.016))
        r.tube(Pr, Nr, 0.020, 1, 0.0010, grow=0.004); r.star((rs * 0.72, rs * 0.72), 0.034, 1, 0.0020)
        self.ring = own(r.build(bpy, 'fs_lensring', mats3('r'), kit.coll), 0.006)
        V = [(0, 0, 0)] * 12; F = []; E = []; S = []
        for q in range(4):
            for row, (e, sv) in enumerate(((0.0, 0.56), (0.5, 0.80), (1.0, 0.28))): E.append(e); S.append(sv)
        for k in range(2):
            for row in range(2): a_ = 6 * k + row; F.append((a_, a_ + 3, a_ + 4, a_ + 1))
        self.lines = own(cw.mk_mesh(bpy, 'fs_lenslines', V, F, [UI.mat_gold(kit, D, 'fs_lflg', al)], None, False, kit.coll, {'e': ('FLOAT', E), 'sh': ('FLOAT', S)}), 0.005)
        self.crisp = [self.frame, self.handle, self.ring, self.lines]


    def pose(self, t):
        B = W.B; D = self.D
        o = W.sm(B.lens0, B.lens1, t) * (1 - W.sm(B.lens2 + 0.4, B.lens3, t))
        show = o > 0.01
        for ob in self.obs: ob.hide_render = not show
        if not show: return
        from mathutils import Vector
        p = self.cam.ob.matrix_basis.inverted() @ Vector(tuple(self.target)); k = DL / max(-p.z, 1e-3); bx, by = p.x * k, p.y * k   # this frame's camera
        cx, cy = bx + self.R + 0.45, min(by + self.R + 0.18, self.hh * 0.50 - self.R)
        pop = o * (1.0 + 0.06 * math.sin(math.pi * min(1.0, W.sm(B.lens0, B.lens1, t))))
        self.disc.location = (cx, cy, self.disc.location.z); self.disc.scale = (pop, pop, 1)
        pr = self.pr; Rl = self.R * pop
        fall = W.sm(B.lens2, B.lens3, t)
        for L, g, c, rad, rim, body, hl, ph in self.ent:
            t0 = self.tm(L, g)
            t1 = self.tm(L + 1, g // 2) if L < len(self.levels) - 1 else 1e9
            if not (t0 <= t < t1) or (L == 0 and t < B.lens0):
                pr.hide(rim); pr.hide(body); pr.hide(hl); continue
            pc = self.levels[L + 1][g // 2][0] if L < len(self.levels) - 1 else c
            pos = c + (pc - c) * W.sm(t1 - 1.0, t1, t) if L < len(self.levels) - 1 else c.copy()
            amp = 0.05 * (1.0 if L < 3 else 0.5) * (1 - W.sm(t1 - 1.0, t1, t) if L < len(self.levels) - 1 else 1.0)
            pos = pos + Rl / self.R * amp * self.R * np.array([math.sin(1.2 * t + ph[0]), math.cos(1.0 * t + ph[1])])
            s = rad * (1 + 0.30 * math.sin(math.pi * min(1.0, max(0.0, (t - t0) / 0.35))) if L > 0 else 1.0) * (1 + 0.10 * math.sin(2.2 * t + ph[0]))
            if L == len(self.levels) - 1:
                s *= 1.0 + 0.9 * W.sm(B.lensj5, B.lensj5 + 1.0, t)
                pos = pos + np.array([0.0, -fall * fall * 2.6 * self.R]) - np.array([0.0, 0.0])
            pz = np.array([cx + pos[0] * pop, cy + pos[1] * pop, 0.0]); sc = s * pop
            pr.set(rim, pz, I3, sc); pr.set(body, pz + np.array([0, 0, 0.001]), I3, sc * 0.82); pr.set(hl, pz + np.array([0, 0, 0.002]), I3, sc * 0.82)
        pr.commit()
        D.set('a_lens', min(1.0, o * 1.6))
        v = np.array([cx - bx, cy - by]); dist = np.linalg.norm(v) + 1e-9; u = v / dist; nrm = np.array([-u[1], u[0]])
        self.frame.location = (cx, cy, self.frame.location.z); self.frame.scale = (pop, pop, 1)
        ah = math.atan2(v[1], v[0]) + 0.50
        self.handle.location = (cx, cy, self.handle.location.z); self.handle.scale = (pop, pop, 1); self.handle.rotation_euler = (0, 0, ah)
        self.ring.location = (bx, by, self.ring.location.z); self.ring.scale = (o, o, 1)
        co = np.zeros((12, 3), np.float32)
        for k, sd in enumerate((-1, 1)):
            a = np.array([bx, by]) + nrm * sd * 0.078 * o; b = np.array([cx, cy]) + nrm * sd * Rl
            tg = (b - a) / (np.linalg.norm(b - a) + 1e-9); nn = np.array([-tg[1], tg[0]])
            if nn @ UI.LIGHT < 0: nn = -nn
            for q, (pt, hw) in enumerate(((a, 0.0055 * o), (b, 0.0075 * pop))):
                for row, off in enumerate((1.0, 0.0, -1.0)): co[6 * k + 3 * q + row] = (*(pt + nn * off * hw), 0.0)
        me = self.lines.data; me.vertices.foreach_set('co', co.ravel()); me.update()
