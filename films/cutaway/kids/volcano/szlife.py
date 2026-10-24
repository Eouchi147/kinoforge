"""How is a volcano born? Everything alive on and round the island, and the easter eggs (bpy + numpy).

Every pose is a pure function of t. Each piece has a job (CRAFT section 1):
  grass, flowers, palms   plants find a home on the new rock: green from the shore up, then the palms (the calm); the older
                          islands round it are green all the time, because they were built the same way, long ago
  gulls                   a happy world: they circle the island, lift off to the old island when the rumbling grows, and
                          watch from there (nobody is in danger), come home in the calm
  dolphins                leap for joy (one at the very first second, one right on the eruption), a sailing boat
  easter eggs             a beach ball (it rolls in, hops at every eruption), flip-flops, a snorkel and mask, a sandcastle with a
                          bucket and spade (szvolc), the fizzy drink bottle (szvolc), the snail on its surfboard (the mascot)
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, disc, rz, ry, rx, euler, I3
from szvolc import gh


# ============================================================================== plants
def island_pts(rng, n, rmin=0.12, rmax=0.97):
    out = []
    while len(out) < n:
        x = rng.uniform(W.XC - W.RS, W.XC + W.RS); y = rng.uniform(W.YC + 0.02, W.YC + W.RS / W.KY)
        r = float(W.rr(x, y))
        if r / W.RS < rmin or r / W.RS > rmax or abs(x) > W.HX - 0.05 or y > W.HY - 0.05: continue
        out.append((x, y))
    return np.array(out)


def world_island_pts(rng, per):
    out = []
    for cx, cy, r, ht, kind in W.NEAR_C:
        k = 0
        while k < per:
            a = rng.uniform(0, 2 * math.pi); d = r * 0.85 * math.sqrt(rng.uniform(0.02, 1.0))
            x, y = cx + d * math.cos(a), cy + d * math.sin(a)
            if W.in_hole(x, y): continue
            out.append((x, y)); k += 1
    return np.array(out)


def _set_pts(ob, P, z, sc):
    me = ob.data; co = np.column_stack([P, z]).astype(np.float32)
    me.vertices.foreach_set('co', co.ravel()); me.attributes['scale'].data.foreach_set('value', np.asarray(sc, np.float32)); me.update()


def build_plants(kit, L, D, rng):
    out = {}
    pal = dict(cw.SEASONS['summer'])
    gm = M.varied(kit, D, 'sz_grass', [(0.30, 0.70, 0.30), (0.46, 0.78, 0.30), (0.22, 0.60, 0.30), (0.56, 0.80, 0.34)], tip=(0.86, 0.96, 0.50), height=0.07)
    tufts = cw.proto_tufts(kit, pal, 6, 0.06, 7, (8, 13))
    for o in tufts: o.data.materials[0] = gm
    fl = cw.proto_flowers(kit, 5, 7)
    P = island_pts(rng, 520); n = len(P); gq = W.rr(P[:, 0], P[:, 1]) / W.RS; sc = rng.uniform(0.8, 1.5, n)
    ob = L.scatter('sz_grass', tufts, P, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 6, n), sway=0.22, speed=0.9, z=0.0)
    out['grass'] = (ob, P, sc, gq, rng.uniform(0, 0.5, n))
    P2 = island_pts(rng, 70, 0.35, 0.92); n2 = len(P2); gq2 = W.rr(P2[:, 0], P2[:, 1]) / W.RS; sc2 = rng.uniform(1.1, 1.7, n2)
    ob2 = L.scatter('sz_flowers', fl, P2, yaw=rng.uniform(0, 6.28, n2), scale=sc2, variant=rng.integers(0, 5, n2), sway=0.18, speed=0.9, z=0.0)
    out['flowers'] = (ob2, P2, sc2, gq2, rng.uniform(0.3, 0.9, n2))
    # the older islands: green all the time (static)
    Pw = world_island_pts(rng, 260); nw = len(Pw); scw = rng.uniform(1.6, 3.0, nw)
    obw = L.scatter('sz_wgrass', tufts, Pw, yaw=rng.uniform(0, 6.28, nw), scale=scw, variant=rng.integers(0, 6, nw), sway=0.18, speed=0.8, z=0.0)
    _set_pts(obw, Pw, W.land_h(Pw[:, 0], Pw[:, 1]) - 0.004, scw)
    out['world'] = obw
    return out


def plants_pose(pl, t):
    B = W.B; lf = W.lift(t)
    front = W.keys(t, [(B.rest0, 0.0), (B.green1, 1.12)])
    for key in ('grass', 'flowers'):
        ob, P, sc, gq, d = pl[key]
        tg = (1 - gq) * 0.9 + d * 0.15                     # the shore greens first
        k = np.clip((front - tg) / 0.14, 0, 1); k = k * k * (3 - 2 * k)
        on = float(k.max()) > 1e-3; ob.hide_render = not on
        if on: _set_pts(ob, P, W.h_now(P[:, 0], P[:, 1], t) + lf - 0.004, sc * k)


# ============================================================================== palms
def _palm(rng, H, lean):
    parts = []
    pts = [(0.0, 0.0, 0.0), (lean * 0.3, 0.0, H * 0.35), (lean * 0.8, 0.0, H * 0.70), (lean, 0.0, H)]
    v, f = tube(pts, [0.026, 0.020, 0.016, 0.014], 8, True); parts.append((v, f, 0))
    top = np.array(pts[-1]); n = 8
    for k in range(n):
        a = 2 * math.pi * k / n + rng.uniform(-0.2, 0.2); L = H * rng.uniform(0.55, 0.72)
        d = np.array([math.cos(a), math.sin(a), 0.0]); sd = np.array([-math.sin(a), math.cos(a), 0.0])
        Vv = []; Fc = []
        for i, u in enumerate(np.linspace(0, 1, 7)):
            p = top + d * L * u + np.array([0, 0, L * (0.40 * u - 0.78 * u * u)]); w = L * 0.17 * math.sin(math.pi * min(1.0, (u + 0.12))) * (1 - 0.35 * u)
            Vv += [tuple(p - sd * w), tuple(p), tuple(p + sd * w)]
        for i in range(6): o = 3 * i; Fc += [(o, o + 3, o + 4, o + 1), (o + 1, o + 4, o + 5, o + 2)]
        parts.append((np.array(Vv), Fc, 1))
    for q in range(3):
        a = 2 * math.pi * q / 3; v, f = sphere(top + np.array([0.025 * math.cos(a), 0.025 * math.sin(a), -0.02]), (0.020, 0.020, 0.020), 1); parts.append((v, f, 2))
    return parts


def build_palms(kit, D, rng):
    pr = Parts('fs_palms')
    mats = [M.paint(kit, D, 'sz_palmtrunk', (0.52, 0.34, 0.22)), M.varied(kit, D, 'sz_palmleaf', [(0.18, 0.60, 0.28), (0.32, 0.72, 0.30), (0.12, 0.52, 0.34)]), M.paint(kit, D, 'sz_coco', (0.40, 0.26, 0.16), noise=0.0)]
    items = []
    # on our island: along the beach and the lower slopes, in front of nothing (staggered, in the order of the calm)
    spots = []
    for a in np.linspace(math.radians(8), math.radians(172), 11):
        r = W.RS * rng.uniform(0.74, 0.90); x = W.XC + r * math.cos(a); y = W.YC + r * math.sin(a) / W.KY
        if abs(x) < W.HX - 0.08 and y < W.HY - 0.1 and not (abs(x - 0.72) < 0.2 and abs(y + 0.60) < 0.2) and not (abs(x - 0.44) < 0.16 and abs(y + 0.40) < 0.18) and y > W.YC + 0.18: spots.append((x, y))
    for i, (x, y) in enumerate(spots):
        H = rng.uniform(0.34, 0.50); lean = rng.uniform(-0.09, 0.09)
        ids = [pr.add(v, f, m, pivot=(0, 0, 0)) for v, f, m in _palm(rng, H, lean)]
        items.append((ids, x, y, False, i / max(len(spots) - 1, 1), rng.uniform(0, 6.28)))
    # on the older islands (always there, bigger)
    for cx, cy, r, ht, kind in W.NEAR_C:
        for q in range(7):
            a = rng.uniform(0, 2 * math.pi); d = r * rng.uniform(0.2, 0.75); x, y = cx + d * math.cos(a), cy + d * math.sin(a)
            if W.in_hole(x, y): continue
            H = rng.uniform(0.40, 0.62); ids = [pr.add(v, f, m) for v, f, m in _palm(rng, H, rng.uniform(-0.1, 0.1))]
            items.append((ids, x, y, True, 0.0, rng.uniform(0, 6.28)))
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'items': items}


def palms_pose(Pm, t):
    B = W.B; pr = Pm['parts']; lf = W.lift(t)
    for ids, x, y, old, d, ph in Pm['items']:
        if old: k = 1.0; z = float(W.land_h(np.array([x]), np.array([y]))[0]) - 0.01
        else:
            k = W.sm(B.rest0 + 1.0 + d * 4.0, B.rest0 + 3.2 + d * 4.0, t); z = gh(x, y, t) + lf - 0.01
        R = euler(0.02 * math.sin(0.9 * t + ph), 0.02 * math.cos(0.7 * t + ph), 0.08 * math.sin(0.6 * t + ph))
        for j in ids:
            if k < 1e-3: pr.hide(j)
            else: pr.set(j, (x, y, z), R, k)
    pr.commit()


# ============================================================================== gulls, dolphins, the boat
def build_gulls(kit, D, rng, n=6):
    pr = Parts('fs_gulls'); m = M.paint(kit, D, 'sz_gull', (0.98, 0.98, 0.96), noise=0.0); tipm = M.paint(kit, D, 'sz_gulltip', (0.22, 0.24, 0.30), noise=0.0); out = []
    for k in range(n):
        s = 0.052
        b = pr.add(*tube([(-s * 0.5, 0, 0), (0, 0, 0), (s * 0.45, 0, 0.004)], [s * 0.10, s * 0.15, s * 0.07], 6), m=0)
        w = [pr.add([(-s * 0.18, 0, 0), (s * 0.18, 0, 0), (0.0, sd * s * 1.0, 0), (-s * 0.34, sd * s * 0.74, 0)], [(0, 1, 2, 3)], 0) for sd in (-1, 1)]
        out.append((b, w, rng.uniform(1.5, 2.3), rng.uniform(0.9, 1.5), rng.uniform(0, 6.28), rng.uniform(2.4, 3.4), rng.choice([-1, 1])))
    pr.build(kit.bpy, [m, tipm], kit.coll, smooth=False)
    return {'parts': pr, 'g': out}


def gulls_pose(Gl, t):
    B = W.B; pr = Gl['parts']; lf = W.lift(t)
    away = W.sm(B.fly0, B.fly0 + 3.5, t) * (1 - W.sm(B.rest0 + 2.0, B.rest0 + 6.0, t))
    ac = W.NEAR_C[1]            # the old island on the right: they watch from there
    for i, (b, wings, r, h, a0, flap, dr) in enumerate(Gl['g']):
        a = a0 + dr * (0.40 + 0.1 * (i % 3)) * t
        home = np.array([W.XC + r * math.cos(a) * 1.15, r * math.sin(a) * 0.8 + 0.1, h + 0.05 * math.sin(0.8 * t + a0) + lf])
        r2 = 0.5 + 0.1 * i; far = np.array([ac[0] + r2 * math.cos(a * 1.5), ac[1] + r2 * math.sin(a * 1.5), float(W.land_h(np.array([ac[0]]), np.array([ac[1]]))[0]) + 1.0 + 0.1 * i])
        P = home * (1 - away) + far * away; yaw = a + dr * math.pi / 2
        amp = math.radians(14 + 28 * (0.5 + 0.5 * math.sin(0.5 * t + a0))) * math.sin(2 * math.pi * flap * t) * (1.0 + 0.4 * away)
        R = rz(yaw); pr.set(b, P, R)
        for w, sd in zip(wings, (-1, 1)): pr.set(w, P, R @ rx(sd * amp))
    pr.commit()


DOLPH = [(2.4, 0, 3.2, -1.6), (12.6, 1, 4.4, 0.6), (24.6, 0, 3.0, -0.8), (31.55, 1, 3.6, -0.5), (40.0, 0, 4.2, 0.2), (50.5, 1, 3.3, -1.3), (60.2, 0, 3.4, -0.4), (63.4, 1, 4.1, 0.5), (68.2, 0, 3.7, -0.9)]


def build_dolphins(kit, D):
    pr = Parts('fs_dolphins'); m = M.paint(kit, D, 'sz_dolphin', (0.42, 0.60, 0.78), noise=0.0); belly = M.paint(kit, D, 'sz_dolphinb', (0.92, 0.95, 0.98), noise=0.0); out = []
    for k in range(2):
        pts = [(-0.26, 0, 0.0), (-0.12, 0, 0.0), (0.04, 0, 0.0), (0.16, 0, 0.0), (0.26, 0, -0.005), (0.32, 0, -0.01)]
        v, f = tube(pts, [0.012, 0.040, 0.052, 0.044, 0.020, 0.010], 10, True); body = pr.add(v, f, 0)
        bl = pr.add(*sphere((0.05, 0, -0.022), (0.17, 0.040, 0.026), 1), m=1)
        fin = pr.add([(0.0, 0, 0.04), (-0.06, 0, 0.04), (-0.025, 0, 0.115)], [(0, 1, 2), (0, 2, 1)], 0)
        fluke = pr.add([(-0.25, 0, 0), (-0.34, 0.065, 0.02), (-0.30, 0.0, 0.0), (-0.34, -0.065, 0.02)], [(0, 1, 2), (0, 2, 3), (0, 2, 1), (0, 3, 2)], 0)
        snout = pr.add(*sphere((0.33, 0, -0.012), (0.04, 0.012, 0.011), 1), m=0)
        pf = pr.add([(0.12, 0.03, -0.02), (0.07, 0.09, -0.05), (0.05, 0.03, -0.02)], [(0, 1, 2), (0, 2, 1)], 0)
        splash = [pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), m=1) for _ in range(6)]
        out.append((body, bl, fin, fluke, snout, pf, splash))
    pr.build(kit.bpy, [m, belly], kit.coll)
    return {'parts': pr, 'd': out}


def dolphins_pose(Dl, t):
    pr = Dl['parts']; K = 1.5
    for k, d in enumerate(Dl['d']):
        parts = d[:6]; splash = d[6]; active = None
        for (tj, who, s, dd) in DOLPH:
            if who == k and tj - 0.2 <= t <= tj + 2.4: active = (tj, s, dd)
        if active is None:
            for j in parts: pr.hide(j)
            for j in splash: pr.hide(j)
            continue
        tj, s, dd = active; a = t - tj; T = 1.5
        x0, y0 = W.at_screen(s, dd); head = math.atan2(-0.35, 0.9) if k == 0 else math.atan2(0.25, -0.9)
        hx, hy = math.cos(head), math.sin(head)
        # screen-left to right (+s) is along RIGHT; head along the screen
        hv = (W.RIGHT * (1 if k == 0 else -1)); head = math.atan2(hv[1], hv[0]); hx, hy = hv
        u = 1.25; vz = 1.9; g = 2 * vz / T
        base = float(W.sea_h(np.array([x0]), np.array([y0]), t)[0])
        if 0 <= a <= T:
            z = base - 0.05 + vz * a - 0.5 * g * a * a; vzn = vz - g * a
            pitch = math.atan2(vzn, u); R = rz(head) @ ry(-pitch)
            p = (x0 + hx * u * a * 0.55 - hx * 0.4, y0 + hy * u * a * 0.55 - hy * 0.4, z)
            for j in parts: pr.set(j, p, R, K)
        else:
            for j in parts: pr.hide(j)
        # splashes at the take-off (a = 0) and the landing (a = T)
        for q, j in enumerate(splash):
            for ta, off in ((0.0, 0.0), (T, 1.0)):
                sa = (t - tj - ta)
                if 0 <= sa < 0.9 and (q % 2) == int(off):
                    ang = 2 * math.pi * q / 6; r = 0.05 + 0.10 * sa
                    pr.set(j, (x0 + hx * u * 0.55 * ta - hx * 0.4 + r * math.cos(ang), y0 + hy * u * 0.55 * ta - hy * 0.4 + r * math.sin(ang), base + 0.06 * math.sin(math.pi * sa / 0.9) + 0.02), I3, 0.022 * (1 - sa / 0.9))
                    break
            else: pr.hide(j)
    pr.commit()


def build_boat(kit, D):
    pr = Parts('fs_boat'); mats = [M.paint(kit, D, 'sz_hull', (0.92, 0.28, 0.26), noise=0.0), M.paint(kit, D, 'sz_sail', (0.99, 0.97, 0.92), noise=0.0), M.paint(kit, D, 'sz_sail2', (0.98, 0.78, 0.22), noise=0.0), M.paint(kit, D, 'sz_mast', (0.55, 0.38, 0.26), noise=0.0)]
    hull = pr.add([(-0.17, -0.05, 0.0), (0.17, -0.05, 0.0), (0.24, 0.0, 0.07), (-0.24, 0.0, 0.07), (-0.17, 0.05, 0.0), (0.17, 0.05, 0.0), (0.24, 0.0, 0.07)], [(0, 1, 2, 3), (4, 5, 6, 3)], 0)
    hull2 = pr.add([(-0.24, -0.08, 0.07), (0.24, -0.08, 0.07), (0.24, 0.08, 0.07), (-0.24, 0.08, 0.07), (-0.17, -0.05, 0.0), (0.17, -0.05, 0.0), (0.17, 0.05, 0.0), (-0.17, 0.05, 0.0)],
                   [(0, 1, 2, 3), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0), (4, 7, 6, 5)], 0)
    v, f = tube([(0, 0, 0.07), (0, 0, 0.42)], [0.008, 0.005], 6, True); mast = pr.add(v, f, 3)
    s1 = pr.add([(0.012, 0, 0.12), (0.012, 0, 0.40), (0.20, 0, 0.12)], [(0, 1, 2), (0, 2, 1)], 1)
    s2 = pr.add([(-0.012, 0, 0.12), (-0.012, 0, 0.34), (-0.16, 0, 0.12)], [(0, 1, 2), (0, 2, 1)], 2)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'ids': [hull, hull2, mast, s1, s2]}


def boat_pose(Bo, t):
    pr = Bo['parts']; s = 3.9 + 0.35 * math.sin(0.12 * t); d = -0.55 + 0.25 * math.sin(0.09 * t + 1.0)
    x, y = W.at_screen(s, d); z = float(W.sea_h(np.array([x]), np.array([y]), t)[0]) + 0.012
    R = rz(math.atan2(W.RIGHT[1], W.RIGHT[0]) + (math.pi if math.cos(0.12 * t) > 0 else 0)) @ rx(0.07 * math.sin(1.1 * t)) @ ry(0.05 * math.sin(0.8 * t + 1.0))
    for j in Bo['ids']: pr.set(j, (x, y, z + 0.015 * math.sin(1.3 * t)), R, 1.3)
    pr.commit()


# ============================================================================== easter eggs: the ball, flip-flops, snorkel; the surfing snail
def build_eggs(kit, D):
    pr = Parts('fs_eggs')
    m = cw._new_mat(kit.bpy, 'sz_ball'); g = cw.G(m.node_tree, kit); P = g.node('ShaderNodeTexCoord').outputs['Object']; s = g.sep(P)
    ang = g.math('DIVIDE', g.math('ARCTAN2', s[1], s[0]), 2 * math.pi)
    col = g.ramp(g.math('FRACT', g.math('ADD', ang, 1.0)), [(0.0, (0.95, 0.22, 0.22)), (0.16, (0.99, 0.96, 0.90)), (0.33, (0.98, 0.78, 0.20)), (0.50, (0.99, 0.96, 0.90)), (0.66, (0.20, 0.52, 0.92)), (0.83, (0.99, 0.96, 0.90))], 'CONSTANT')
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', g.math('MULTIPLY', g.math('ABSOLUTE', s[2]), 20.0), 0.85), 8.0, clamp=True), col, cw.srgb((0.99, 0.96, 0.90)))
    cw._finish(g, g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.5}))
    mats = [m, M.paint(kit, D, 'sz_ff1', (1.0, 0.45, 0.62), noise=0.0), M.paint(kit, D, 'sz_ff2', (0.22, 0.82, 0.78), noise=0.0), M.paint(kit, D, 'sz_strap', (0.98, 0.92, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_mask', (0.20, 0.30, 0.82), noise=0.0), M.paint(kit, D, 'sz_maskglass', (0.70, 0.92, 1.0), noise=0.0), M.paint(kit, D, 'sz_snork', (1.0, 0.66, 0.12), noise=0.0)]
    e = {'ball': pr.add(*sphere((0, 0, 0), (0.05, 0.05, 0.05), 2), m=0)}
    e['ff'] = []
    for k, (mm, ox) in enumerate(((1, -0.03), (2, 0.03))):
        sole = pr.add(*sphere((ox, 0, 0.006), (0.052, 0.020, 0.0065), 1), m=mm)
        v, f = tube([(ox + 0.018, 0.0, 0.008), (ox + 0.026, 0.0, 0.013)], [0.004, 0.003], 5, True); post = pr.add(v, f, 3)
        a1 = pr.add(*tube([(ox + 0.026, 0, 0.013), (ox - 0.008, 0.020, 0.008)], [0.003, 0.003], 5, True), m=3)
        a2 = pr.add(*tube([(ox + 0.026, 0, 0.013), (ox - 0.008, -0.020, 0.008)], [0.003, 0.003], 5, True), m=3)
        e['ff'] += [sole, post, a1, a2]
    ring_pts = [(0.05 * math.cos(a), 0.0, 0.05 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14)]
    e['mask'] = [pr.add(*tube(ring_pts + [ring_pts[0]], [0.006] * 15, 6, False), m=4), pr.add(*disc((0, 0.001, 0), 0.046, 14, 'y'), m=5)]
    e['snork'] = [pr.add(*tube([(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)], [0.001, 0.001], 4, True), m=6)]
    v, f = tube([(0.05, 0, 0.0), (0.09, 0.0, 0.04), (0.10, 0.0, 0.12), (0.095, 0.0, 0.17)], [0.008, 0.008, 0.008, 0.009], 7, True); e['snork'] = [pr.add(v, f, 6)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'e': e}


BALL_R = 0.05 * 1.8
BALL_FROM, BALL_TO = (-0.55, -0.20), (-0.98, -0.52)
FF = (-0.80, -0.14); MASK = (-1.02, -0.80)


def eggs_pose(E, t):
    B = W.B; pr = E['parts']; e = E['e']; lf = W.lift(t)
    u = W.sm(B.ball0, B.ball1, t); x = BALL_FROM[0] + (BALL_TO[0] - BALL_FROM[0]) * u; y = BALL_FROM[1] + (BALL_TO[1] - BALL_FROM[1]) * u
    hop = 0.0
    for ee in W.ERUPT:
        if ee <= t < ee + 0.7: hop = max(hop, 0.07 * math.sin(math.pi * (t - ee) / 0.7) * (0.5 + 0.5 * W.STRENGTH[W.ERUPT.index(ee)]))
    bounce = 0.05 * abs(math.sin(math.pi * (t - B.ball0) / 0.55)) * (1 - u) if t < B.ball1 else 0.0
    gz = gh(x, y, t) + lf
    spin = (u * math.hypot(BALL_TO[0] - BALL_FROM[0], BALL_TO[1] - BALL_FROM[1])) / BALL_R
    pr.set(e['ball'], (x, y, gz + BALL_R + hop + bounce), rz(math.atan2(BALL_TO[1] - BALL_FROM[1], BALL_TO[0] - BALL_FROM[0])) @ ry(spin) @ rx(0.25 * math.sin(t)), 1.8)
    fx, fy = FF; fz = gh(fx, fy, t) + lf
    for i, j in enumerate(e['ff']):
        k = i // 4; pr.set(j, (fx + 0.07 * k, fy - 0.03 * k, fz), rz(0.7 + 0.15 * k), 1.8)
    mx, my = MASK; mz = gh(mx, my, t) + lf
    pr.set(e['mask'][0], (mx, my, mz + 0.06), rx(-1.15) @ rz(0.5) , 1.8); pr.set(e['mask'][1], (mx, my, mz + 0.06), rx(-1.15) @ rz(0.5), 1.8)
    pr.set(e['snork'][0], (mx + 0.01, my, mz + 0.05), rx(-1.15) @ rz(0.5) @ ry(0.9), 1.6)
    pr.commit()


BOARD = (1.46, -0.52)


def build_snail(kit, D):
    pr = Parts('fs_snail')
    mats = [M.paint(kit, D, 'sz_snailshell', (0.96, 0.52, 0.40), noise=0.0), M.paint(kit, D, 'sz_snailband', (0.99, 0.82, 0.38), noise=0.0),
            M.paint(kit, D, 'sz_snailbody', (0.86, 0.84, 0.66), noise=0.0), M.paint(kit, D, 'sz_snaileye', (0.10, 0.10, 0.18), noise=0.0),
            M.paint(kit, D, 'sz_board', (0.98, 0.84, 0.22), noise=0.0), M.paint(kit, D, 'sz_boardstripe', (0.92, 0.22, 0.40), noise=0.0)]
    s = {'shell': pr.add(*sphere((0, 0, 0.030), (0.026, 0.017, 0.028), 2), m=0), 'band': pr.add(*sphere((0.0, 0, 0.030), (0.016, 0.0185, 0.018), 2), m=1),
         'body': pr.add(*sphere((0.012, 0, 0.007), (0.040, 0.012, 0.008), 2), m=2)}
    s['stalks'] = [pr.add(*tube([(0, 0, 0), (0.004, sd * 0.004, 0.022)], [0.0025, 0.0018], 5), m=2) for sd in (-1, 1)]
    s['eyes'] = [pr.add(*sphere((0.004, sd * 0.004, 0.024), (0.0035, 0.0035, 0.0035), 1), m=3) for sd in (-1, 1)]
    s['board'] = pr.add(*sphere((0, 0, 0.0), (0.17, 0.045, 0.009), 2), m=4)
    s['stripe'] = pr.add(*sphere((0, 0, 0.002), (0.14, 0.012, 0.010), 1), m=5)
    s['fin'] = pr.add([(-0.15, 0, -0.005), (-0.19, 0, -0.04), (-0.10, 0, -0.005)], [(0, 1, 2), (0, 2, 1)], 5)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 's': s}


SK = 2.6


def snail_pose(Sn, t):
    B = W.B; pr = Sn['parts']; s = Sn['s']; lf = W.lift(t)
    x0, y0 = BOARD; sea = W.Z_SEA + lf + 0.004
    sw = math.sin(2 * math.pi * t / 4.1); bob = 0.012 * sw
    x = x0 + 0.05 * math.sin(2 * math.pi * t / 9.0); y = y0 + 0.03 * math.sin(2 * math.pi * t / 7.0)
    Rb = rz(0.35 + 0.1 * math.sin(0.4 * t)) @ rx(0.10 * math.sin(2 * math.pi * t / 3.3)) @ ry(0.07 * sw)
    pr.set(s['board'], (x, y, sea + 0.004 + bob), Rb, 1.0); pr.set(s['stripe'], (x, y, sea + 0.004 + bob), Rb, 1.0); pr.set(s['fin'], (x, y, sea + 0.004 + bob), Rb, 1.0)
    p = np.array([x, y, sea + 0.004 + bob]) + Rb @ np.array([0.03, 0, 0.012])
    hide = max(W.win(t, B.e0 - 0.4, B.e0 + 2.2, 0.3), 0.0)                    # it tucks in for the whoosh, then peeks out
    for e in W.ERUPT[1:]: hide = max(hide, 0.6 * W.win(t, e - 0.1, e + 0.6, 0.15))
    out = 1 - hide
    up = 1 + 0.6 * W.win(t, B.wave0 - 0.5, B.wave0 + 2.6, 0.3)
    wave = W.sm(B.wave0, B.wave0 + 0.4, t) * 0.8 * math.sin(2 * math.pi * 1.6 * t)
    R = Rb
    pr.set(s['shell'], p, R, SK); pr.set(s['band'], p, R, SK)
    if out < 0.02: pr.hide(s['body']); [pr.hide(j) for j in s['stalks'] + s['eyes']]
    else:
        pr.set(s['body'], p, R, (out * SK, SK, SK)); head = p + R @ (np.array([0.040 * out, 0, 0.010]) * SK)
        for j, ph in zip(s['stalks'] + s['eyes'], (0, 1, 0, 1)):
            wob = rx(0.25 * math.sin(2 * math.pi * 0.5 * t + ph) + wave * (1 if ph == 0 else -1))
            pr.set(j, head, R @ wob, (out * SK, out * SK, out * up * SK))
    pr.commit()
    return p
