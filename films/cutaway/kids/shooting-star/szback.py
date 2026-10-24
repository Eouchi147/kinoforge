"""What is a shooting star? The world behind the block (bpy + numpy): hills with a sleepy village, a far shore, clouds.

Sam 23 Oct 2026 19:43: the background must not be a flat static painted card; it is a lively extension of the world on the
block, real 3D layers with depth (parallax even with the small sway), life far away, clouds drifting, light changing with
the story. Fable's painted sky card is replaced by this film's own night sky (szstory.py); these are the land layers.

Three hill layers stand behind the block at 3.8, 5.8 and 7.8 m (multiplane, like painted animation backgrounds but in depth):
each is a curtain of land whose crest rolls back in a quarter cylinder. Their colours follow the light of the moment (dusk,
twilight, night, deep night) through the same four weights as the sky. On them:
  the middle hills   a little village across the lake: houses whose windows light up one by one as the sunset fades, chimney
                     smoke rising; a church tower with a clock face glowing
  the far hills      two sleepy farm lights, a windmill turning slowly
  the crests         round trees and poplars as dark storybook silhouettes
  always             a few clouds drifting across, silver in the moonlight
Every motion is a pure function of t.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, rz, rx, ry, I3

# per layer: distance behind the block centre, crest height (z), roll, rounding radius, sRGB (dusk, twilight, night, deep night)
# v: where the crest sits on screen (fraction of the half height above the centre), so the sky keeps the top of the frame
LAYERS = [
    dict(d=5.6, v=0.10, amp=0.16, f=0.55, R=0.9, seed=3, cols=((0.46, 0.34, 0.40), (0.24, 0.24, 0.42), (0.12, 0.22, 0.32), (0.09, 0.17, 0.29))),
    dict(d=7.4, v=0.16, amp=0.26, f=0.40, R=1.3, seed=7, cols=((0.58, 0.40, 0.48), (0.30, 0.28, 0.48), (0.12, 0.20, 0.38), (0.10, 0.17, 0.34))),
    dict(d=9.2, v=0.23, amp=0.36, f=0.28, R=1.8, seed=11, cols=((0.74, 0.52, 0.56), (0.40, 0.36, 0.58), (0.17, 0.26, 0.46), (0.14, 0.22, 0.42))),
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
        S = np.linspace(-hw, hw, ns); top = ridge(L, S); p0 = F3.at(L, 0.0, 0.0); zb = -float(W.drop(p0[0], p0[1])) - 0.9
        V = []
        for j in range(nv):
            v = j / (nv - 1)
            for k, s in enumerate(S):
                zz = zb + (top[k] - zb) * v; dz = top[k] - zz; w = min(1.0, dz / L['R'])
                off = L['R'] * math.sqrt(max(0.0, 1 - (1 - w) ** 2))
                V.append(F3.at(L, s, zz, off))
        Fc = [(j * ns + k, j * ns + k + 1, (j + 1) * ns + k + 1, (j + 1) * ns + k) for j in range(nv - 1) for k in range(ns - 1)]
        m = cw._new_mat(bpy, f'fs_hill{i}'); g = cw.G(m.node_tree, kit)
        tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']
        base = D.rgb(g, f'hill{i}', L['cols'][0])
        n1 = g.noise(P, 1.2 / (1 + i), 3.0)
        col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], 0.35), base, g.mix(0.7, base, (0.0, 0.0, 0.1, 1), 'MULTIPLY'))
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.9}); cw._finish(g, p)
        ob = cw.mk_mesh(bpy, f'fs_hill{i}', V, Fc, [m], None, True, kit.coll)
        out['layers'].append(ob)
    # ---------------------------------------------------------------- things on the hills
    pr = Parts('fs_far')
    mats = [M.paint(kit, D, 'sz_fartree', (0.12, 0.30, 0.26)), M.paint(kit, D, 'sz_farpop', (0.10, 0.26, 0.28)),
            M.paint(kit, D, 'sz_smoke', (0.96, 0.94, 0.90), noise=0.0),
            M.paint(kit, D, 'sz_wall', (0.98, 0.92, 0.80), noise=0.0), M.paint(kit, D, 'sz_roof', (0.80, 0.34, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_cloud', (1.0, 0.97, 0.92), noise=0.0, drive='cloud', lit=False),
            M.mat_glow(kit, D, 'fs_window', (1.0, 0.74, 0.32), 2.6), M.paint(kit, D, 'sz_mill', (0.90, 0.84, 0.74), noise=0.0),
            M.paint(kit, D, 'sz_millsail', (0.60, 0.40, 0.30), noise=0.0), M.mat_glow(kit, D, 'fs_clockface', (1.0, 0.92, 0.62), 2.2),
            M.mat_glow(kit, D, 'fs_farlight', (1.0, 0.80, 0.45), 2.0)]
    rng = np.random.default_rng(23); items = []
    def put(L, s, kind, parts, dz=0.0, scale=1.0, order=None):
        """parts: list of (V, F, m) in local coords (x along the layer, y toward the viewer, z up), placed on the crest."""
        z = float(ridge(L, s)) - dz; w = min(1.0, dz / L['R']); off = L['R'] * math.sqrt(max(0.0, 1 - (1 - w) ** 2))
        p = F3.at(L, s, z, off)
        ids = [pr.add(v, f, m) for v, f, m in parts]
        items.append(dict(ids=ids, p=p, kind=kind, s=s, L=L, li=[id(x) for x in LAYERS].index(id(L)), scale=scale))
        return len(items) - 1
    R = np.column_stack([F3.right, F3.dv, [0, 0, 1]])      # local (x along, y toward camera, z up) -> world
    out['R'] = R
    def lollipop(H, r, m=0): return [(*tube([(0, 0, -0.05), (0, 0, H * 0.55)], [0.03 * H, 0.02 * H], 6), m)] + [(*sphere((0, 0, H * 0.7), (r, r, r * 1.05), 1), m)]
    def poplar(H, m=1): return [(*sphere((0, 0, H * 0.5), (H * 0.13, H * 0.13, H * 0.5), 1), m)]
    for li, L in enumerate(LAYERS):
        hw = (F3.dist + L['d']) * hf * 1.25; n = (14, 18, 24)[li]; H = (0.26, 0.34, 0.42)[li]
        for s in np.sort(rng.uniform(-hw, hw, n)):
            dz = rng.uniform(0.0, 0.25 * L['R']); h = H * rng.uniform(0.7, 1.3)
            put(L, s, 'tree', lollipop(h, 0.22 * h) if rng.uniform() < 0.65 else poplar(h * 1.2), dz)
    Lf, Lm, Ln = LAYERS[2], LAYERS[1], LAYERS[0]
    # the village on the middle hills, to the left (across the lake), its windows lighting up one by one
    win = []; chim = []
    hs = (-4.2, -3.75, -3.3, -2.85, -2.4, -1.95, -1.5)
    for k, s in enumerate(hs):
        h = 0.20 + 0.06 * (k % 2); w_ = 0.26 + 0.04 * (k % 3)
        parts = [(*box((0, 0, h / 2), (w_, 0.24, h)), 3), (*cone((0, 0, h), 0.19, 0.16, 4), 4), (*box((0.07, 0, h + 0.10), (0.04, 0.04, 0.12)), 4)]
        idx = put(Lm, s, 'house', parts, 0.15)
        for q, (wx, wz) in enumerate(((-0.07, 0.65), (0.07, 0.65), (0.0, 0.28))):
            if q == 2 and k % 2: continue
            v, fc = box((wx * w_ / 0.3, 0.123, h * wz), (0.045, 0.006, 0.06)); wid = pr.add(v, fc, 6)
            win.append((wid, idx, 2.2 + 0.55 * k + 0.37 * q + rng.uniform(0, 0.6)))
        chim.append((idx, h))
    out['win'] = win
    # the church tower with a glowing clock face, and a few farm lights on the far hills; a windmill that turns slowly
    parts = [(*box((0, 0, 0.30), (0.20, 0.20, 0.60)), 3), (*cone((0, 0, 0.60), 0.15, 0.30, 4), 4)]
    ci = put(Lm, -1.05, 'church', parts, 0.15)
    v, fc = box((0.0, 0.103, 0.45), (0.09, 0.006, 0.09)); out['clockface'] = (pr.add(v, fc, 9), ci)
    farl = []
    for s in (-2.6, -0.8, 1.9, 3.1):
        v, fc = box((0, 0.0, 0.0), (0.05, 0.02, 0.04)); farl.append((put(Lf, s, 'farm', [(v, fc, 10)], 0.05), rng.uniform(5.0, 14.0)))
    out['farl'] = farl
    mi = put(Lf, 1.0, 'mill', [(*cone((0, 0, 0.0), 0.10, 0.34, 8, 0.06), 7)], 0.1)
    sails = [pr.add(*box((0, 0.0, 0.0), (0.03, 0.01, 0.30)), 8) for _ in range(2)]
    out['mill'] = (mi, sails)
    out['chimneys'] = [(F3.at(Lm, s, float(ridge(Lm, s)) - 0.15 + 0.20 + 0.06 * (k % 2) + 0.18, 0.05) + F3.right * 0.07) for k, s in enumerate(hs)]
    # smoke puffs from three chimneys
    smoke = []
    for hk in (0, 2, 5):
        for k in range(5): smoke.append((hk, k, pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), 2)))
    out['smoke'] = smoke
    # clouds: soft clusters drifting across the sky between the far hills and the painted sky
    clouds = []
    for k in range(6):
        parts = []
        for j in range(5):
            c = (rng.uniform(-0.5, 0.5), rng.uniform(-0.15, 0.15), rng.uniform(-0.05, 0.12)); r = rng.uniform(0.22, 0.38)
            parts.append(pr.add(*sphere(c, (r * 1.3, r * 0.8, r * 0.7), 2), 5))
        clouds.append((parts, rng.uniform(-6, 6), rng.uniform(1.4, 2.6), rng.uniform(6.0, 8.2), rng.uniform(0.04, 0.08)))
    out['clouds'] = clouds
    pr.build(bpy, mats, kit.coll)
    out['parts'] = pr; out['items'] = items
    return out


def pose(Bk, D, t):
    pr = Bk['parts']; F3 = Bk['F3']; R = Bk['R']
    for i, L in enumerate(LAYERS): D.setc(f'hill{i}', _rgbmix(t, L['cols']))
    w = W.weights(t)
    D.setc('cloud', tuple(sum(wi * c[j] for wi, c in zip(w, ((1.0, 0.78, 0.66), (0.70, 0.64, 0.80), (0.58, 0.62, 0.78), (0.52, 0.56, 0.74)))) for j in range(3)))
    for it in Bk['items']:
        for j in it['ids']: pr.set(j, it['p'], R, it['scale'])
    # the windows light up one by one (they pop in from a point), the clock face and the farm lights follow; a farm light winks
    items = Bk['items']
    for wid, idx, t_on in Bk['win']:
        k = W.sm(t_on, t_on + 0.5, t) * (1.0 + 0.0 * math.sin(t))
        if k < 1e-3: pr.hide(wid)
        else: pr.set(wid, items[idx]['p'], R, k)
    cf, ci = Bk['clockface']; k = W.sm(5.0, 5.6, t)
    if k < 1e-3: pr.hide(cf)
    else: pr.set(cf, items[ci]['p'], R, k)
    for idx, ph in Bk['farl']:
        k = W.sm(ph - 4.0, ph - 3.5, t) * (0.75 + 0.25 * math.sin(0.9 * t + ph))
        pr.set(items[idx]['ids'][0], items[idx]['p'], R, max(k, 0.0)) if k > 1e-3 else pr.hide(items[idx]['ids'][0])
    mi, sails = Bk['mill']; mp = items[mi]['p'] + R @ np.array([0.0, 0.07, 0.30])
    for q, j in enumerate(sails): pr.set(j, mp, R @ rx(0) @ ry(0.0) @ _rot_y(0.35 * t + q * math.pi / 2))
    # smoke: rising, growing, then gone (looping, so it never stops)
    ch = Bk['chimneys']
    for hk, k, j in Bk['smoke']:
        T = 4.5; age = ((t + k * T / 5 + hk * 0.9) % T) / T
        c = ch[hk] + np.array([0, 0, 0.45 * age]) + F3.right * (0.15 * age); r = (0.02 + 0.06 * age) * (1 - W.sm(0.75, 1.0, age)) * W.sm(1.0, 3.0, t)
        if r < 1e-3: pr.hide(j)
        else: pr.set(j, c, I3, r)
    # clouds drift (a few, thin, silver)
    for parts, s0, z, d, v in Bk['clouds']:
        s = ((s0 + v * t + 7.0) % 14.0) - 7.0; c = F3.t0 - F3.dv * d + F3.right * s + np.array([0, 0, z])
        for j in parts: pr.set(j, c, R)
    pr.commit()


def _rot_y(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
