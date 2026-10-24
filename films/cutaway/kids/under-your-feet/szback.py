"""Who lives under your feet? The world behind the block (the park, its hills and the sky) (bpy + numpy).

Sam, 23 Oct 2026 19:43: the background must not be a flat static painted card; it is a lively extension of the world on
the block, real 3D layers with depth (parallax even with the small sway), hills and forests of the same era, life far
away, clouds drifting, light changing with the story, and it changes when time passes. Fable's painted sky card stays
only as the sky at the very back.

Three hill layers stand behind the block at 2.6, 5.0 and 7.8 m (multiplane, like painted animation backgrounds but in
depth): each is a curtain of land whose crest rolls back in a quarter cylinder, so the low sun lights its top and the
paint reads as round hills. Their colours follow the story (today, the fern era, the soft evening, deep time and rain)
through the same four weights as Fable's sky. On them, by era (each piece grows up out of its hill or sinks back, staggered
left to right, when time rewinds and again when today returns):
  long ago   a smoking volcano far off, a herd of small long-necks walking along a ridge, pterosaurs circling,
             tree ferns and monkey-puzzle conifers on the crests
  today      a village with chimney smoke, a train crossing a viaduct, a red tractor, grazing sheep, two kites,
             round trees and poplars on the crests
  always     clouds drifting across, painted cream, greyer in deep time and the rain
Every motion is a pure function of t.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, Dino, sphere, tube, cone, box, rz, rx, ry, I3

# per layer: distance behind the block centre, crest height (z), roll, rounding radius, sRGB (today, fern era, evening, deep)
# v: where the crest sits on screen (fraction of the half height above the centre), so the sky keeps the top of the frame
LAYERS = [
    dict(d=3.8, v=0.44, amp=0.16, f=0.55, R=0.9, seed=3, cols=((0.58, 0.76, 0.46), (0.40, 0.70, 0.42), (0.80, 0.62, 0.32), (0.84, 0.88, 0.90))),
    dict(d=5.8, v=0.50, amp=0.26, f=0.40, R=1.3, seed=7, cols=((0.52, 0.72, 0.56), (0.34, 0.62, 0.48), (0.74, 0.54, 0.38), (0.80, 0.86, 0.92))),
    dict(d=7.8, v=0.56, amp=0.36, f=0.28, R=1.8, seed=11, cols=((0.66, 0.78, 0.84), (0.50, 0.68, 0.76), (0.80, 0.64, 0.58), (0.84, 0.88, 0.94))),
]


def ridge(L, s):
    s = np.asarray(s, float)
    return L['z'] + L['amp'] * (0.65 * W.fbm(s * L['f'], 0.0 * s + L['seed'], L['seed'], 3, 1.0) + 0.35 * np.sin(s * L['f'] * 1.3 + L['seed']))


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
    # crests: trees of both eras along all three layers
    for li, L in enumerate(LAYERS):
        hw = (F3.dist + L['d']) * hf * 1.25; n = (12, 16, 22)[li]; H = (0.26, 0.34, 0.42)[li]
        for s in np.sort(rng.uniform(-hw, hw, n)):
            dz = rng.uniform(0.0, 0.25 * L['R']); h = H * rng.uniform(0.7, 1.3)
            put(L, s, 1, 'tree', lollipop(h, 0.22 * h) if rng.uniform() < 0.7 else poplar(h * 1.2), dz)
    Lf, Lm, Ln = LAYERS
    # today: the village (houses with chimneys), the viaduct and the train, the tractor, sheep, kites
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
        for k in range(n): smoke.append((src, k, pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), 4 if src == 'vent' else 3)))
    out['smoke'] = smoke
    # clouds: soft clusters drifting across the sky between the far hills and the painted sky
    clouds = []
    for k in range(7):
        parts = []
        for j in range(5):
            c = (rng.uniform(-0.5, 0.5), rng.uniform(-0.15, 0.15), rng.uniform(-0.05, 0.12)); r = rng.uniform(0.22, 0.38)
            parts.append(pr.add(*sphere(c, (r * 1.3, r * 0.8, r * 0.7), 2), 15))
        clouds.append((parts, rng.uniform(-6, 6), rng.uniform(2.6, 4.2), rng.uniform(6.0, 8.2), rng.uniform(0.04, 0.08)))
    out['clouds'] = clouds
    pr.build(bpy, mats, kit.coll)
    out['parts'] = pr; out['items'] = items
    return out


def _grow(era_k, it, t):
    """Trees on the crests thin out in winter (bare in the snow); everything else stands all year."""
    if it['kind'] == 'tree': return 1.0 - 0.5 * float(W.weights(t)[3])
    return 1.0


def pose(Bk, D, t):
    pr = Bk['parts']; F3 = Bk['F3']; R = Bk['R']; e = 1.0
    w = W.weights(t)
    for i, L in enumerate(LAYERS): D.setc(f'hill{i}', _rgbmix(t, L['cols']))
    D.set('era', e)
    D.setc('cloud', tuple(sum(wi * c[j] for wi, c in zip(w, ((1.0, 0.98, 0.94), (1.0, 0.99, 0.95), (1.0, 0.86, 0.78), (0.86, 0.88, 0.94)))) for j in range(3)))
    # the hills rise while the layers stack (deep time) and shrink again as the land wears away
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
        if today < 0.5: pr.hide(kp); pr.hide(st); continue
        anchor = F3.at(Ln, s, float(ridge(Ln, s)) - 0.1, 0.3)
        kpos = anchor + np.array([0, 0, 1.25]) + F3.right * (0.25 * math.sin(0.6 * t + ph)) + np.array([0, 0, 0.1 * math.sin(1.1 * t + ph)])
        pr.set(kp, kpos, R @ ry(0.3 * math.sin(1.4 * t + ph)))
        d = kpos - anchor; L_ = np.linalg.norm(d); zax = d / L_; xax = np.cross([0, 1, 0], zax); xax /= np.linalg.norm(xax) + 1e-9; yax = np.cross(zax, xax)
        pr.set(st, kpos, np.column_stack([xax, yax, zax]), (1.0, 1.0, L_))      # the string's local -z runs down to its anchor
    # smoke: rising, growing, then gone (looping, so it never stops)
    ch = Bk['chimneys']
    for src, k, j in Bk['smoke']:
        if src == 'chim':
            if today < 0.5: pr.hide(j); continue
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
    pr.commit()
