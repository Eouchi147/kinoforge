"""Where does rain come from? The world behind the slice (bpy + numpy).

Three hill layers stand behind the block (3.8, 5.8 and 7.8 m): curtains of land whose crests roll back in a quarter
cylinder. On them: a village with chimney smoke, a train on a viaduct, a tractor, sheep, kites, trees. Far right, the
hills open onto the SEA (a painted band with sun glitter) where the river ends. Clouds drift. The colours follow the
weather through the four weights of szworld.weights (fresh morning, warm sun, golden clearing, grey rain). A RAINBOW
arcs over the slice after the rain, painting itself across the sky from left to right. Every motion is a pure function of t.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, rz, rx, ry, I3

# per layer: distance behind the block centre, crest height (z), roll, rounding radius, sRGB (today, fern era, evening, deep)
# v: where the crest sits on screen (fraction of the half height above the centre), so the sky keeps the top of the frame
LAYERS = [
    dict(d=3.8, v=0.44, amp=0.16, f=0.55, R=0.9, seed=3, cols=((0.54, 0.72, 0.46), (0.50, 0.74, 0.40), (0.66, 0.66, 0.44), (0.40, 0.54, 0.52))),
    dict(d=5.8, v=0.50, amp=0.26, f=0.40, R=1.3, seed=7, cols=((0.50, 0.68, 0.58), (0.46, 0.70, 0.50), (0.68, 0.62, 0.50), (0.44, 0.54, 0.60))),
    dict(d=7.8, v=0.56, amp=0.36, f=0.28, R=1.8, seed=11, cols=((0.68, 0.78, 0.84), (0.62, 0.78, 0.80), (0.80, 0.70, 0.64), (0.58, 0.66, 0.76))),
]
SEA_S = (1.0, 4.6)         # where the far hills open onto the sea (position along the far layer)
SEA_DIP = 0.55
RB_S, RB_DZ, RB_R, RB_W = 0.85, -0.55, 3.0, 0.55

def ridge(L, s):
    s = np.asarray(s, float)
    z = L['z'] + L['amp'] * (0.65 * W.fbm(s * L['f'], 0.0 * s + L['seed'], L['seed'], 3, 1.0) + 0.35 * np.sin(s * L['f'] * 1.3 + L['seed']))
    if L['seed'] == 11: z = z - SEA_DIP * W.smooth(SEA_S[0] - 0.6, SEA_S[0] + 0.3, s) * (1 - W.smooth(SEA_S[1] - 0.3, SEA_S[1] + 0.6, s))
    return z


class Frame3:
    def __init__(self, cam):
        a = math.radians(cam.az); self.dv = np.array([math.cos(a), math.sin(a), 0.0]); self.right = np.array([-math.sin(a), math.cos(a), 0.0])
        self.t0 = np.array([cam.target[0], cam.target[1], 0.0]); self.dist = cam.dist
    def at(self, L, s, z, off=0.0):
        return self.t0 - self.dv * L['d'] + self.right * s + np.array([0, 0, z]) + self.dv * off


def _rgbmix(t, cols):
    w = W.weights(t); return tuple(sum(wi * c[j] for wi, c in zip(w, cols)) for j in range(3))


def build(kit, D, cam, ctx):
    bpy = kit.bpy; F3 = Frame3(cam); out = {'F3': F3, 'layers': []}
    hf = 18.0 / cam.ob.data.lens; tanv = hf * min(ctx['W'], ctx['H']) / max(ctx['W'], ctx['H'])
    a, e = math.radians(cam.az), math.radians(cam.el); dvec = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    C = np.asarray(cam.target, float) + cam.dist * dvec; f = -dvec; rgt = np.cross(f, (0, 0, 1)); rgt /= np.linalg.norm(rgt); up = np.cross(rgt, f)
    for L in LAYERS:      # solve the crest height that lands at screen height v (perspective: y = (A.up + z up_z) / (A.f + z f_z))
        A = F3.at(L, 0.0, 0.0) - C; y = L['v'] * tanv
        L['z'] = float((A @ up - y * (A @ f)) / (y * f[2] - up[2]))
    for i, L in enumerate(LAYERS):
        hw = (F3.dist + L['d']) * hf * 1.35; ns = 120; nv = 26
        S = np.linspace(-hw, hw, ns); top = ridge(L, S); zb = -7.0
        V = []
        for j in range(nv):
            v = j / (nv - 1)
            for k, s in enumerate(S):
                # from the bottom up to the crest; the last stretch rolls back in a quarter circle of radius R
                zz = zb + (top[k] - zb) * v; dz = top[k] - zz; w = min(1.0, dz / L['R'])
                off = L['R'] * math.sqrt(max(0.0, 1 - (1 - w) ** 2))
                V.append(F3.at(L, s, zz, off))
        Fc = [(j * ns + k, j * ns + k + 1, (j + 1) * ns + k + 1, (j + 1) * ns + k) for j in range(nv - 1) for k in range(ns - 1)]
        m = cw._new_mat(bpy, f'fs_hill{i}'); g = cw.G(m.node_tree, kit)
        tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; sx = g.sep(P)
        base = D.rgb(g, f'hill{i}', L['cols'][0])
        n1 = g.noise(P, 1.2 / (1 + i), 3.0); n2 = g.noise(P, 6.0 / (1 + i), 3.0)
        col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], 0.35), base, g.mix(0.7, base, (0.0, 0.0, 0.1, 1), 'MULTIPLY'))
        # field rows (today) or fern clumps (long ago): soft stripes across the slope, by the 'era' value
        rows = g.math('ABSOLUTE', g.math('SINE', g.math('ADD', g.math('MULTIPLY', sx[2], 14.0 / (1 + i)), g.math('MULTIPLY', n2.outputs['Fac'], 3.0))))
        rows = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', rows, 0.8), 4.0, clamp=True), D.val(g, 'era', 1.0))
        col = g.mix(g.math('MULTIPLY', rows, 0.22), col, g.mix(1.0, col, (1.25, 1.2, 0.85, 1), 'MULTIPLY'))
        clumps = g.math('MULTIPLY', g.math('LESS_THAN', g.voronoi(P, 3.0 / (1 + i), 'F1').outputs['Distance'], 0.32), g.math('SUBTRACT', 1.0, D.val(g, 'era', 1.0)))
        col = g.mix(g.math('MULTIPLY', clumps, 0.3), col, g.mix(1.0, col, (0.7, 0.85, 0.75, 1), 'MULTIPLY'))
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.9}); cw._finish(g, p)
        ob = cw.mk_mesh(bpy, f'fs_hill{i}', V, Fc, [m], None, True, kit.coll)
        out['layers'].append(ob)
    # ---------------------------------------------------------------- things on the hills
    pr = Parts('fs_far')
    mats = [M.paint(kit, D, 'sz_fartree', (0.20, 0.52, 0.36)), M.paint(kit, D, 'sz_farold', (0.10, 0.40, 0.36)), M.paint(kit, D, 'sz_volcano', (0.40, 0.30, 0.36)),
            M.paint(kit, D, 'sz_smoke', (0.96, 0.94, 0.90), noise=0.0), M.paint(kit, D, 'sz_ash', (0.62, 0.58, 0.64), noise=0.0),
            M.paint(kit, D, 'sz_herd', (0.36, 0.56, 0.52), noise=0.0), M.paint(kit, D, 'sz_ptero', (0.50, 0.30, 0.34), noise=0.0),
            M.paint(kit, D, 'sz_wall', (0.98, 0.92, 0.80), noise=0.0), M.paint(kit, D, 'sz_roof', (0.80, 0.34, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_train', (0.18, 0.40, 0.62), noise=0.0), M.paint(kit, D, 'sz_viaduct', (0.80, 0.70, 0.62)),
            M.paint(kit, D, 'sz_tractor', (0.90, 0.24, 0.20), noise=0.0), M.paint(kit, D, 'sz_tyre', (0.12, 0.12, 0.16), noise=0.0),
            M.paint(kit, D, 'sz_sheep', (0.99, 0.97, 0.92), noise=0.0), M.paint(kit, D, 'sz_kitefar', (0.99, 0.80, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_cloud', (1.0, 0.97, 0.92), noise=0.0, drive='cloud'), M.paint(kit, D, 'sz_lava', (1.0, 0.56, 0.24), noise=0.0)]
    rng = np.random.default_rng(23); items = []
    def put(L, s, era, kind, parts, dz=0.0, scale=1.0, order=None):
        """parts: list of (V, F, m) in local coords (x along the layer, y toward the viewer, z up), placed on the crest."""
        z = float(ridge(L, s)) - dz; w = min(1.0, dz / L['R']); off = L['R'] * math.sqrt(max(0.0, 1 - (1 - w) ** 2))
        p = F3.at(L, s, z, off)
        ids = [pr.add(v, f, m) for v, f, m in parts]
        items.append(dict(ids=ids, p=p, era=era, kind=kind, s=s, L=L, li=[id(x) for x in LAYERS].index(id(L)), scale=scale, order=(s / 12.0 + 0.5) if order is None else order))
    R = np.column_stack([F3.right, F3.dv, [0, 0, 1]])      # local (x along, y toward camera, z up) -> world
    out['R'] = R
    def lollipop(H, r, m=0): return [(*tube([(0, 0, -0.05), (0, 0, H * 0.55)], [0.03 * H, 0.02 * H], 6), m)] + [(*sphere((0, 0, H * 0.7), (r, r, r * 1.05), 1), m)]
    def poplar(H, m=0): return [(*sphere((0, 0, H * 0.5), (H * 0.13, H * 0.13, H * 0.5), 1), m)]
    def spire(H, m=1): return [(*tube([(0, 0, -0.05), (0, 0, H * 0.3)], [0.02 * H, 0.015 * H], 6), m), (*cone((0, 0, H * 0.18), H * 0.16, H * 0.85, 10), m)]
    def treefern(H, m=1):
        out_ = [(*tube([(0, 0, -0.05), (0.02 * H, 0, H * 0.9)], [0.025 * H, 0.02 * H], 6), m)]
        for k in range(6):
            a = 2 * math.pi * k / 6; d = np.array([math.cos(a), math.sin(a), 0]); top = np.array([0.02 * H, 0, H * 0.9])
            out_.append((*tube([top, top + d * 0.25 * H + (0, 0, 0.05 * H), top + d * 0.42 * H - (0, 0, 0.12 * H)], [0.03 * H, 0.025 * H, 0.008 * H], 5), m))
        return out_
    # crests: trees along all three layers
    for li, L in enumerate(LAYERS):
        hw = (F3.dist + L['d']) * hf * 1.25; n = (12, 16, 22)[li]; H = (0.26, 0.34, 0.42)[li]
        for s in np.sort(rng.uniform(-hw, hw, n)):
            dz = rng.uniform(0.0, 0.25 * L['R']); h = H * rng.uniform(0.7, 1.3)
            put(L, s, 1, 'tree', lollipop(h, 0.22 * h) if rng.uniform() < 0.7 else poplar(h * 1.2), dz)
    Lf, Lm, Ln = LAYERS
    # the village (houses with chimneys), the viaduct and the train, the tractor, sheep, kites
    for k, s in enumerate((1.5, 1.95, 2.35, 2.9, 3.3)):
        h = 0.20 + 0.06 * (k % 2); w_ = 0.26 + 0.04 * (k % 3)
        parts = [(*box((0, 0, h / 2), (w_, 0.24, h)), 7), (*cone((0, 0, h), 0.19, 0.16, 4), 8), (*box((0.07, 0, h + 0.10), (0.04, 0.04, 0.12)), 8)]
        put(Lm, s, 1, 'house', parts, 0.15)
    out['chimneys'] = [F3.at(Lm, s, float(ridge(Lm, s)) - 0.15 + (0.20 + 0.06 * (k % 2)) + 0.18, 0.05) + F3.right * 0.07 for k, s in enumerate((1.5, 1.95, 2.35, 2.9, 3.3))]
    via_s0, via_s1 = -1.6, 1.1; via_z = float(min(ridge(Lm, np.linspace(via_s0, via_s1, 30)))) + 0.05
    vparts = [(*box(((via_s0 + via_s1) / 2, 0, 0.0), (via_s1 - via_s0, 0.14, 0.06)), 10)]
    for s in np.linspace(via_s0 + 0.2, via_s1 - 0.2, 6): vparts.append((*box((s, 0, -0.45), (0.10, 0.12, 0.9)), 10))
    p_via = F3.at(Lm, 0.0, via_z, 0.35)
    ids = [pr.add(v, f, m) for v, f, m in vparts]; items.append(dict(ids=ids, p=p_via, era=1, kind='viaduct', s=0.0, L=Lm, li=1, scale=1.0, order=0.6))
    out['via'] = (p_via, via_s0, via_s1)
    train = []
    for k in range(4):
        L_ = 0.20 if k else 0.17
        parts = [(*box((0, 0, 0.05), (L_, 0.10, 0.08)), 9 if k == 0 else (8 if k % 2 else 7))]
        if k == 0: parts += [(*box((-0.04, 0, 0.11), (0.07, 0.09, 0.06)), 9), (*tube([(0.05, 0, 0.09), (0.05, 0, 0.14)], [0.015, 0.015], 6), 12)]
        train.append(([pr.add(v, f, m) for v, f, m in parts], k))
    out['train'] = train
    tr_parts = [(*box((0, 0, 0.06), (0.16, 0.09, 0.06)), 11), (*box((-0.03, 0, 0.12), (0.07, 0.08, 0.08)), 11),
                (*tube([(-0.05, -0.055, 0.045), (-0.05, 0.055, 0.045)], [0.045, 0.045], 10), 12), (*tube([(0.06, -0.05, 0.025), (0.06, 0.05, 0.025)], [0.025, 0.025], 10), 12)]
    out['tractor'] = [pr.add(v, f, m) for v, f, m in tr_parts]
    sheep = []
    for k in range(7):
        s = -2.6 + 0.32 * k + rng.uniform(-0.1, 0.1); dz = rng.uniform(0.25, 0.55)
        body = (*sphere((0, 0, 0.05), (0.07, 0.045, 0.045), 1), 13); head = (*sphere((0.07, 0, 0.05), (0.022, 0.018, 0.02), 1), 12)
        put(Ln, s, 1, 'sheep', [body, head], dz, order=0.3 + 0.03 * k)
        sheep.append(len(items) - 1)
    out['sheep'] = sheep
    kites = []
    for k in range(2):
        kp = pr.add([(0, 0, 0.14), (0.08, 0, 0.0), (0, 0, -0.10), (-0.08, 0, 0.0)], [(0, 1, 2, 3)], 14 if k else 8)
        st = pr.add(*tube([(0, 0, 0), (0, 0, -1.0)], [0.004, 0.004], 4), 13)
        kites.append((kp, st, (-1.9, 2.6)[k], rng.uniform(0, 6.28)))
    out['kites'] = kites
    # smoke puffs: the volcano (6), each chimney (4), the engine (4)
    smoke = []
    for src, n in (('chim', 4 * 5), ('train', 4)):
        for k in range(n): smoke.append((src, k, pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), 3)))
    out['smoke'] = smoke
    # clouds: soft clusters drifting across the sky between the far hills and the painted sky
    clouds = []
    for k in range(5):
        parts = []
        for j in range(5):
            c = (rng.uniform(-0.5, 0.5), rng.uniform(-0.15, 0.15), rng.uniform(-0.05, 0.12)); r = rng.uniform(0.22, 0.38)
            parts.append(pr.add(*sphere(c, (r * 1.3, r * 0.8, r * 0.7), 2), 15))
        clouds.append((parts, rng.uniform(-6, 6), rng.uniform(2.6, 4.2), rng.uniform(6.0, 8.2), rng.uniform(0.04, 0.08)))
    out['clouds'] = clouds
    # ---------------------------------------------------------------- the sea at the horizon, where the river ends
    Ls = LAYERS[2]; sa, sb = SEA_S; zh = float(ridge(Ls, np.array([(sa + sb) / 2]))[0]) + 0.34
    ms = cw._new_mat(bpy, 'fs_sea'); gs = cw.G(ms.node_tree, kit)
    P_ = gs.node('ShaderNodeTexCoord').outputs['Object']; zf = gs.math('MULTIPLY', gs.math('SUBTRACT', gs.sep(P_)[2], 0.0), 1.0)
    f_ = gs.math('MULTIPLY', gs.math('SUBTRACT', gs.sep(P_)[2], zh - 0.9), 1.0 / 0.9, clamp=True)
    strokes = gs.math('MULTIPLY', gs.math('SUBTRACT', gs.noise(gs.comb(gs.math('MULTIPLY', gs.sep(P_)[0], 1.2), gs.math('MULTIPLY', gs.sep(P_)[2], 26.0), 0.0), 1.0, 2.0, 0.5).outputs['Fac'], 0.55), 0.35)
    colS = gs.mix(f_, D.rgb(gs, 'seabot', (0.10, 0.40, 0.62)), D.rgb(gs, 'seatop', (0.52, 0.80, 0.90)))
    colS = gs.mix(1.0, colS, gs.math('ADD', 1.0, strokes), 'MULTIPLY')
    cw._finish(gs, gs.node('ShaderNodeEmission', ins={'Color': colS, 'Strength': 1.0}))
    qs = [F3.at(Ls, sa - 0.9, zh - 0.9, -1.1), F3.at(Ls, sb + 1.2, zh - 0.9, -1.1), F3.at(Ls, sb + 1.2, zh, -1.1), F3.at(Ls, sa - 0.9, zh, -1.1)]
    # the card's object coordinates: put z relative to the horizon (0 at the horizon, -0.9 at the bottom)
    c0 = (qs[0] + qs[2]) / 2
    sea = cw.mk_mesh(bpy, 'fs_sea', [tuple(q - np.array([0, 0, zh]) * 0) for q in qs], [(0, 1, 2, 3)], [ms], None, False, kit.coll); sea.visible_shadow = False
    out['sea'] = (sea, Ls, zh)
    # sun glitter on the sea: small four-pointed stars that twinkle
    gl = Parts('fs_glitter'); gm = M.mat_glow(kit, D, 'fs_glitm', (1.0, 0.98, 0.85), 1.6)
    star = [(0, 0.05, 0), (0.012, 0.012, 0), (0.05, 0, 0), (0.012, -0.012, 0), (0, -0.05, 0), (-0.012, -0.012, 0), (-0.05, 0, 0), (-0.012, 0.012, 0)]
    out['glit'] = [(gl.add([(0, 0, 0)] + star, [(0, 1 + i, 1 + (i + 1) % 8) for i in range(8)], 0), rng.uniform(sa - 0.5, sb + 0.8), rng.uniform(zh - 0.75, zh - 0.05), rng.uniform(0, 6.28)) for _ in range(46)]
    gl.build(bpy, [gm], kit.coll, smooth=False); gl.ob.visible_shadow = False; out['gl'] = gl
    # ---------------------------------------------------------------- the rainbow: seven soft bands that paint themselves across the sky
    NRW, NC = 15, 72; Lr = LAYERS[1]
    mr = M.mat_rainbow(kit, D)
    FA = []; RB = []
    for r in range(NRW + 1):
        for j in range(NC + 1): RB.append(r / NRW)
    FE = [min(1.0, 7.0 * min(v, 1 - v) + 0.02) for v in RB]
    Fr = [(r * (NC + 1) + j, r * (NC + 1) + j + 1, (r + 1) * (NC + 1) + j + 1, (r + 1) * (NC + 1) + j) for r in range(NRW) for j in range(NC)]
    rbw = cw.mk_mesh(bpy, 'fs_rainbow', np.zeros(((NRW + 1) * (NC + 1), 3)), Fr, [mr], None, False, kit.coll, {'rb': ('FLOAT', RB), 'fe': ('FLOAT', FE)}); rbw.visible_shadow = False
    out['rainbow'] = dict(ob=rbw, NRW=NRW, NC=NC, L=Lr)
    pr.build(bpy, mats, kit.coll)
    out['parts'] = pr; out['items'] = items
    return out


def _grow(era_k, it, t):
    return 1.0


def pose(Bk, D, t):
    pr = Bk['parts']; F3 = Bk['F3']; R = Bk['R']; e = W.era(t)
    w = W.weights(t)
    for i, L in enumerate(LAYERS): D.setc(f'hill{i}', _rgbmix(t, L['cols']))
    D.set('era', e)
    D.setc('cloud', tuple(sum(wi * c[j] for wi, c in zip(w, ((1.0, 0.98, 0.94), (0.98, 0.96, 0.88), (1.0, 0.82, 0.76), (0.80, 0.82, 0.90)))) for j in range(3)))
    dz = [0.0, 0.0, 0.0]
    for i, ob in enumerate(Bk['layers']): ob.location = (0.0, 0.0, dz[i])
    for it in Bk['items']:
        k = _grow(None, it, t); li = it.get('li', 0)
        for j in it['ids']:
            if k < 1e-3: pr.hide(j)
            else: pr.set(j, it['p'] + np.array([0, 0, dz[li]]), R @ np.diag([1.0, 1.0, k]), it['scale'] * np.array([1.0, 1.0, 1.0]))
    Lf, Lm, Ln = LAYERS
    # the train crosses the viaduct every 14 s (today)
    p_via, s0, s1 = Bk['via']; today = 1.0
    ph = ((t + 3.0) % 14.0) / 9.0
    for ids, k in Bk['train']:
        s = s0 - 0.8 + (s1 - s0 + 1.6) * ph - 0.22 * k
        vis = today > 0.5 and ph < 1.0 and s0 - 0.6 < s < s1 + 0.6
        for j in ids:
            if vis: pr.set(j, p_via + F3.right * s + np.array([0, 0, 0.03]), R)
            else: pr.hide(j)
    # the tractor creeps along the near hill
    s = -3.2 + 0.05 * t; z = float(ridge(Ln, s)) - 0.18
    for j in Bk['tractor']:
        if today > 0.5: pr.set(j, F3.at(Ln, s, z, 0.30), R @ ry(0.02 * math.sin(9 * t)))
        else: pr.hide(j)
    # sheep graze (heads dip)
    for idx in Bk['sheep']:
        it = Bk['items'][idx]
        if _grow(None, it, t) > 1e-3: pr.set(it['ids'][1], it['p'], R @ ry(0.25 * max(0.0, math.sin(0.9 * t + it['s'] * 5))), 1.0)
    # kites dance on their strings (today)
    for kp, st, s, ph in Bk['kites']:
        if W.calm(t) < 0.5: pr.hide(kp); pr.hide(st); continue
        anchor = F3.at(Ln, s, float(ridge(Ln, s)) - 0.1, 0.3)
        kpos = anchor + np.array([0, 0, 1.25]) + F3.right * (0.25 * math.sin(0.6 * t + ph)) + np.array([0, 0, 0.1 * math.sin(1.1 * t + ph)])
        pr.set(kp, kpos, R @ ry(0.3 * math.sin(1.4 * t + ph)))
        d = kpos - anchor; L_ = np.linalg.norm(d); zax = d / L_; xax = np.cross([0, 1, 0], zax); xax /= np.linalg.norm(xax) + 1e-9; yax = np.cross(zax, xax)
        pr.set(st, kpos, np.column_stack([xax, yax, zax]), (1.0, 1.0, L_))      # the string's local -z runs down to its anchor
    # smoke: rising, growing, then gone (looping, so it never stops)
    ch = Bk['chimneys']
    for src, k, j in Bk['smoke']:
        if src == 'chim':
            hk, kk = divmod(k, 4); T = 4.0; age = ((t + kk * T / 4 + hk * 0.7) % T) / T
            c = ch[hk] + np.array([0, 0, 0.45 * age]) + F3.right * (0.15 * age); r = (0.02 + 0.06 * age) * (1 - W.sm(0.75, 1.0, age))
        else:
            ids, _ = Bk['train'][0]; T = 1.6; age = ((t + k * T / 4) % T) / T
            if today < 0.5 or ph >= 1.0: pr.hide(j); continue
            s = s0 - 0.8 + (s1 - s0 + 1.6) * ph - 0.6 * age * 0.0
            c = p_via + F3.right * (s + 0.05 - 0.25 * age) + np.array([0, 0, 0.18 + 0.25 * age]); r = (0.02 + 0.05 * age) * (1 - W.sm(0.7, 1.0, age))
        if r < 1e-3: pr.hide(j)
        else: pr.set(j, c, I3, r)
    # clouds drift
    for parts, s0, z, d, v in Bk['clouds']:
        s = ((s0 + v * t + 7.0) % 14.0) - 7.0; c = F3.t0 - F3.dv * d + F3.right * s + np.array([0, 0, z])
        for j in parts: pr.set(j, c, R)
    # the sea: colour with the weather, glitter with the sun
    w = W.weights(t)
    D.setc('seatop', tuple(sum(wi * c[j] for wi, c in zip(w, ((0.52, 0.80, 0.90), (0.50, 0.82, 0.90), (0.80, 0.78, 0.74), (0.52, 0.60, 0.68)))) for j in range(3)))
    D.setc('seabot', tuple(sum(wi * c[j] for wi, c in zip(w, ((0.10, 0.40, 0.62), (0.10, 0.44, 0.64), (0.40, 0.42, 0.52), (0.20, 0.30, 0.42)))) for j in range(3)))
    sun = W.sunny(t) * (1.0 - W.rain_k(t))
    for j, s_, z_, ph in Bk['glit']:
        k = max(0.0, math.sin(2 * math.pi * 0.45 * t + ph)) ** 2 * sun
        if k < 0.02: Bk['gl'].hide(j)
        else: Bk['gl'].set(j, F3.at(LAYERS[2], s_, z_, -1.05), R, 0.5 + 1.1 * k)
    Bk['gl'].commit()
    rb = Bk['rainbow']; u = W.sm(W.B.rainbow0, W.B.rainbow1, t)
    D.set('a_rb', W.sm(W.B.rainbow0 - 0.1, W.B.rainbow0 + 0.6, t))
    rbw = rb['ob']; rbw.hide_render = u < 0.003
    if u >= 0.003:
        NRW, NC = rb['NRW'], rb['NC']; Lr = rb['L']
        c0 = F3.at(Lr, RB_S, Lr['z'] + RB_DZ, 0.4)
        co = np.zeros(((NRW + 1) * (NC + 1), 3), np.float32)
        for r in range(NRW + 1):
            rad = RB_R - RB_W * r / NRW
            for j in range(NC + 1):
                th = math.pi * (1 - min(j / NC, u * 1.0)); co[r * (NC + 1) + j] = c0 + F3.right * (rad * math.cos(th)) + np.array([0, 0, rad * math.sin(th)])
        rbw.data.vertices.foreach_set('co', co.ravel()); rbw.data.update()
    pr.commit()
