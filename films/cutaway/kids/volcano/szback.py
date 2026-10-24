"""How is a volcano born? The world behind the block (bpy + numpy).

Sam, 23 Oct 2026 19:43: the background is a lively extension of the world on the block, real 3D layers with depth, life
far away, clouds drifting, light that follows the story. Here it is the sea to the horizon: three sea terraces behind the
near water (7, 9.4 and 12 m behind the block; each a curtain whose crest rolls back, so the low sun lights its top and
the paint reads as round swells), with older green islands standing on them (some with a sleeping crater and a little
smoke), sailing boats, drifting clouds. At the end a gold ring pops round each of the islands in turn (the islands of
Hawaii were built the same way). Every motion is a pure function of t.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, rz, rx, ry, I3

LAYERS = [
    dict(d=7.0, v=0.40, amp=0.03, f=0.55, R=0.7, seed=3, cols=((0.14, 0.60, 0.70), (0.16, 0.62, 0.70), (0.30, 0.58, 0.66))),
    dict(d=9.4, v=0.47, amp=0.04, f=0.40, R=0.9, seed=7, cols=((0.26, 0.66, 0.78), (0.28, 0.66, 0.78), (0.44, 0.66, 0.78))),
    dict(d=12.0, v=0.54, amp=0.05, f=0.28, R=1.2, seed=11, cols=((0.52, 0.80, 0.90), (0.54, 0.80, 0.90), (0.66, 0.80, 0.90))),
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
    w = W.weights(t); c = (cols[0], cols[1], cols[2], cols[2]); return tuple(sum(wi * ci[j] for wi, ci in zip(w, c)) for j in range(3))


def build(kit, D, cam, ctx):
    bpy = kit.bpy; F3 = Frame3(cam); out = {'F3': F3, 'layers': []}
    hf = 18.0 / cam.ob.data.lens; tanv = hf * min(ctx['W'], ctx['H']) / max(ctx['W'], ctx['H'])
    a, e = math.radians(cam.az), math.radians(cam.el); dvec = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    C = np.asarray(cam.target, float) + cam.dist * dvec; f = -dvec; rgt = np.cross(f, (0, 0, 1)); rgt /= np.linalg.norm(rgt); up = np.cross(rgt, f)
    for L in LAYERS:
        A = F3.at(L, 0.0, 0.0) - C; y = L['v'] * tanv
        L['z'] = float((A @ up - y * (A @ f)) / (y * f[2] - up[2]))
    for i, L in enumerate(LAYERS):
        hw = (F3.dist + L['d']) * hf * 1.35; ns = 120; nv = 26
        S = np.linspace(-hw, hw, ns); top = ridge(L, S); zb = -7.0
        V = []
        for j in range(nv):
            v = j / (nv - 1)
            for k, s in enumerate(S):
                zz = zb + (top[k] - zb) * v; dz = top[k] - zz; w = min(1.0, dz / L['R'])
                off = L['R'] * math.sqrt(max(0.0, 1 - (1 - w) ** 2))
                V.append(F3.at(L, s, zz, off))
        Fc = [(j * ns + k, j * ns + k + 1, (j + 1) * ns + k + 1, (j + 1) * ns + k) for j in range(nv - 1) for k in range(ns - 1)]
        m = cw._new_mat(bpy, f'fs_sea{i}'); g = cw.G(m.node_tree, kit)
        tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; sx = g.sep(P)
        base = D.rgb(g, f'hill{i}', L['cols'][0])
        zoff, w = g.phase(0.25)
        st = g.noise(g.comb(g.math('MULTIPLY', sx[0], 0.7 + 0.3 * i), g.math('MULTIPLY', sx[2], 7.0 / (1 + 0.5 * i)), zoff), 1.0, 3.0, 0.5, '4D', w)
        strokes = g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.56), 7.0, clamp=True)
        col = g.mix(g.math('MULTIPLY', strokes, 0.5), base, g.mix(0.6, base, (1.0, 1.0, 0.95, 1), 'SCREEN'))
        em = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}); cw._finish(g, em)
        out['layers'].append(cw.mk_mesh(bpy, f'fs_seaterrace{i}', V, Fc, [m], None, True, kit.coll))
    # ---------------------------------------------------------------- islands on the terraces
    pr = Parts('fs_far')
    mats = [M.paint(kit, D, 'sz_isle', (0.22, 0.58, 0.34)), M.paint(kit, D, 'sz_isleb', (0.94, 0.82, 0.58), noise=0.0), M.paint(kit, D, 'sz_isleold', (0.44, 0.36, 0.34)),
            M.paint(kit, D, 'sz_puff', (1.0, 0.99, 0.97), noise=0.0), M.paint(kit, D, 'sz_cloud', (1.0, 0.97, 0.92), noise=0.0, drive='cloud'),
            M.paint(kit, D, 'sz_isleg2', (0.30, 0.68, 0.32)), M.paint(kit, D, 'sz_palmfar', (0.14, 0.50, 0.30), noise=0.0), M.paint(kit, D, 'sz_sailfar', (1.0, 0.98, 0.94), noise=0.0),
            M.paint(kit, D, 'sz_sailfar2', (0.96, 0.34, 0.30), noise=0.0), M.paint(kit, D, 'sz_hullfar', (0.30, 0.34, 0.52), noise=0.0)]
    rng = np.random.default_rng(29); out['isl'] = []
    def island(L, s, size, kind):
        z = float(ridge(L, s)); p = F3.at(L, s, z, 0.0)
        parts = [(*sphere((0, 0, 0.0), (0.36 * size, 0.30 * size, 0.045 * size), 1), 1)]
        if kind == 'hill':
            parts += [(*sphere((0, 0, 0.0), (0.30 * size, 0.24 * size, 0.20 * size), 2), 0), (*sphere((-0.14 * size, 0.02, 0.0), (0.18 * size, 0.15 * size, 0.13 * size), 2), 5)]
            for q in range(3):
                a_ = rng.uniform(0, 6.28); r_ = rng.uniform(0.1, 0.22) * size; parts.append((*tube([(r_ * math.cos(a_), r_ * math.sin(a_), 0.1 * size), (r_ * math.cos(a_), r_ * math.sin(a_), 0.30 * size)], [0.012 * size, 0.008 * size], 5), 2))
                parts.append((*sphere((r_ * math.cos(a_), r_ * math.sin(a_), 0.32 * size), (0.07 * size, 0.07 * size, 0.04 * size), 1), 6))
        else:
            parts += [(*cone((0, 0, 0.0), 0.30 * size, 0.40 * size, 20, 0.05 * size), 2), (*sphere((0, 0, 0.0), (0.33 * size, 0.27 * size, 0.07 * size), 1), 5)]
        ids = [pr.add(v, f_, m) for v, f_, m in parts]
        out['isl'].append(dict(ids=ids, p=p, kind=kind, size=size, s=s, L=L, ph=rng.uniform(0, 6.28)))
        return len(out['isl']) - 1
    L0, L1, L2 = LAYERS
    for s, sz, kd in ((-3.4, 1.1, 'hill'), (2.4, 0.9, 'hill'), (6.0, 1.3, 'volcano'), (-7.0, 1.2, 'hill')): island(L0, s, sz, kd)
    for s, sz, kd in ((-1.0, 1.6, 'hill'), (4.6, 1.5, 'volcano'), (-6.0, 1.7, 'hill'), (8.8, 1.8, 'hill')): island(L1, s, sz, kd)
    for s, sz, kd in ((0.8, 2.3, 'hill'), (-4.0, 2.4, 'volcano'), (6.6, 2.4, 'hill'), (-9.0, 2.6, 'hill')): island(L2, s, sz, kd)
    out['R'] = np.column_stack([F3.right, F3.dv, [0, 0, 1]])
    # smoke from the sleeping craters (a few soft puffs, rising and fading)
    out['smoke'] = [(i, k, pr.add(*sphere((0, 0, 0), (1, 1, 0.9), 1), 3)) for i, it in enumerate(out['isl']) if it['kind'] == 'volcano' for k in range(5)]
    # sailing boats far away
    out['sails'] = []
    for k, (L, s0, v) in enumerate(((L0, -2.0, 0.07), (L1, 3.0, -0.05), (L2, -6.0, 0.04))):
        hull = pr.add(*box((0, 0, 0.0), (0.22, 0.07, 0.06)), 9); sa = pr.add([(0.01, 0, 0.03), (0.01, 0, 0.34), (0.15, 0, 0.03)], [(0, 1, 2), (0, 2, 1)], 7)
        sb = pr.add([(-0.01, 0, 0.03), (-0.01, 0, 0.26), (-0.12, 0, 0.03)], [(0, 1, 2), (0, 2, 1)], 8)
        out['sails'].append((hull, sa, sb, L, s0, v))
    # clouds
    clouds = []
    for k in range(7):
        parts = []
        for j in range(5):
            c = (rng.uniform(-0.5, 0.5), rng.uniform(-0.15, 0.15), rng.uniform(-0.05, 0.12)); r = rng.uniform(0.22, 0.38)
            parts.append(pr.add(*sphere(c, (r * 1.3, r * 0.8, r * 0.7), 2), 4))
        clouds.append((parts, rng.uniform(-6, 6), rng.uniform(2.6, 4.2), rng.uniform(6.0, 8.2), rng.uniform(0.04, 0.08)))
    out['clouds'] = clouds
    # the gold rings of the end: one round each older island, then ours
    ring = lambda n: tube([(math.cos(a), math.sin(a), 0.0) for a in np.linspace(0, 2 * math.pi, n + 1)], [0.012] * (n + 1), 6, False)
    rm = M.mat_glow(kit, D, 'fs_ring', (1.0, 0.82, 0.30), 2.4)
    out['rings'] = [pr.add(*ring(48), m=10) for _ in range(4)]
    pr.build(bpy, mats + [rm], kit.coll)
    out['parts'] = pr
    return out


def pose(Bk, D, t):
    pr = Bk['parts']; F3 = Bk['F3']; R = Bk['R']; B = W.B
    for i, L in enumerate(LAYERS): D.setc(f'hill{i}', _rgbmix(t, L['cols']))
    w = W.weights(t)
    D.setc('cloud', tuple(sum(wi * c[j] for wi, c in zip(w, ((1.0, 0.98, 0.94), (1.0, 0.98, 0.92), (1.0, 0.86, 0.78), (0.98, 0.98, 1.0)))) for j in range(3)))
    for it in Bk['isl']:
        p = it['p'] + np.array([0, 0, 0.01 * math.sin(0.7 * t + it['ph'])])
        for j in it['ids']: pr.set(j, p, R, 1.0)
    for i, k, j in Bk['smoke']:
        it = Bk['isl'][i]; T = 7.0; age = ((t + k * T / 5 + i) % T) / T
        c = it['p'] + np.array([0, 0, 0.42 * it['size'] + 0.5 * age * it['size']]) + F3.right * (0.16 * age * it['size'])
        r = (0.03 + 0.09 * age) * it['size'] * (1 - W.sm(0.7, 1.0, age)) * W.sm(0.0, 0.1, age)
        if r < 1e-3: pr.hide(j)
        else: pr.set(j, c, I3, r)
    for hull, sa, sb, L, s0, v in Bk['sails']:
        s = ((s0 + v * t + 9.0) % 18.0) - 9.0; z = float(ridge(L, s)) + 0.03
        p = F3.at(L, s, z, 0.12); Rs = R @ rz(0.0 if v > 0 else math.pi) @ rx(0.04 * math.sin(1.2 * t + s0))
        for j in (hull, sa, sb): pr.set(j, p, Rs, 1.6)
    for parts, s0, z, d, v in Bk['clouds']:
        s = ((s0 + v * t + 7.0) % 14.0) - 7.0; c = F3.t0 - F3.dv * d + F3.right * s + np.array([0, 0, z])
        for j in parts: pr.set(j, c, R)
    # the gold rings
    targets = [(W.NEAR_C[0][0], W.NEAR_C[0][1], W.NEAR_C[0][2] * 1.02, 1.0), (W.NEAR_C[2][0], W.NEAR_C[2][1], W.NEAR_C[2][2] * 1.02, 1.0),
               (W.NEAR_C[1][0], W.NEAR_C[1][1], W.NEAR_C[1][2] * 1.02, 1.0), (W.XC, W.YC, W.RS + 0.08, 1.0 / W.KY)]
    for (cx, cy, r, ey), j, t0 in zip(targets, Bk['rings'], (B.ring0, B.ring1, B.ring2, B.ring3)):
        a = t - t0
        if a < 0 or a > 2.7: pr.hide(j); continue
        grow = W.sm(0, 0.5, a) * (1 + 0.12 * math.sin(math.pi * min(1.0, a / 0.5))) * (1 - W.sm(2.2, 2.7, a))
        z = float(W.sea_h(np.array([cx]), np.array([cy]), t)[0]) + 0.012 if j != Bk['rings'][3] else W.Z_SEA + W.lift(t) + 0.016
        pr.set(j, (cx, cy, z), I3, (r * grow, r * ey * grow if ey != 1.0 else r * grow, grow))
    pr.commit()
