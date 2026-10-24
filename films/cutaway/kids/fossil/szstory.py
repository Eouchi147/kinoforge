"""How does a dinosaur turn into stone? The set pieces of single beats (bpy + numpy). Every pose is a pure function of t.

  peel        rewind: the ground above the old one lifts away upward and fades (time running backwards)
  babies      the living world: two small long-necks splash in the river; while the old one rests they grow and walk off
  turtle      the living world: a turtle plods along the front with the mascot snail riding on its shell
  leaf        the rest: one frond drifts down beside the old dinosaur
  skeleton    mud: the body fades and what remains is the skeleton, which the mud then covers (gentle, museum-like)
  mammoths    layer on layer: two woolly mammoths cross the third new layer (the eras racing by above)
  saplings    layer on layer: little trees on the forest layers
  lens        bone to stone: a round magnifier window on the bone in the rock; drops seep in and leave crystal sparkles,
              the bone turns from ivory to stone grey with mineral glints, from one end to the other; a small ring on
              the fossil and two gold lines tie the window to the place it shows
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
import szui as UI
from szgeo import Parts, Dino, sphere, tube, cone, box, rz, ry, rx, I3

gz = lambda x, y, t: float(W.top_h(np.array([x]), np.array([y]), t)[0])


# ============================================================================== peel: the ground lifts away (rewind)
def build_peel(kit, D):
    m = cw._new_mat(kit.bpy, 'sz_peel'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); z = g.sep(tc.outputs['Object'])[2]; geo = g.node('ShaderNodeNewGeometry')
    top = g.math('GREATER_THAN', g.sep(geo.outputs['Normal'])[2], 0.5)
    band = g.ramp(g.math('DIVIDE', g.math('SUBTRACT', z, W.Z_ANC), W.Z_NOW - W.Z_ANC), [(0.0, (0.40, 0.58, 0.52)), (0.85, (0.46, 0.64, 0.56)), (0.92, (0.30, 0.22, 0.20)), (1.0, (0.30, 0.22, 0.20))])
    col = g.mix(top, band, cw.srgb((0.44, 0.70, 0.32)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.8})
    M._alpha_out(g, p, D.val(g, 'peel_a', 0.0))
    e = 0.004; V, F = box((0, 0, (W.Z_ANC + W.Z_NOW + 0.02) / 2), (W.SX - 2 * e, W.SY - 2 * e, W.Z_NOW + 0.02 - W.Z_ANC))
    ob = cw.mk_mesh(kit.bpy, 'fs_peel', V, F, [m], None, False, kit.coll); ob.hide_render = True
    return ob


def peel_pose(ob, D, t):
    B = W.B
    if not (B.peel0 <= t < B.peel1): ob.hide_render = True; D.set('peel_a', 0.0); return
    u = (t - B.peel0) / (B.peel1 - B.peel0); ob.hide_render = False
    ob.location = (0.0, 0.0, W.lift(t) + 1.5 * u ** 1.4); s = 1.0 + 0.06 * u; ob.scale = (s, s, 1.0)
    D.set('peel_a', 1.0 - W.sm(0.35, 1.0, u))


# ============================================================================== babies, turtle, leaf
def build_babies(kit, D, dino_mats):
    pr = Parts('fs_babies')
    tmp = Dino(kit.bpy, 'fs_babytmp', dino_mats, None, 0.36); V, F, Mi = tmp.rigid(0.0, 0.0); kit.bpy.data.objects.remove(tmp.ob, do_unlink=True)
    babies = [pr.add(V, F, 0) for _ in range(2)]
    pr.F_mi = None
    splash = [[pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), 1) for _ in range(6)] for _ in range(2)]
    mats = [M.paint(kit, D, 'sz_baby', (0.50, 0.80, 0.60), alpha='baby_a', noise=0.0), M.mat_glow(kit, D, 'fs_splash', (0.92, 0.98, 1.0), 1.3)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'babies': babies, 'splash': splash}


def babies_pose(Bb, D, t):
    B = W.B; pr = Bb['parts']; anc = W.ancient(t)
    a = W.sm(B.fern0, B.fern1, t) * (1 - W.sm(B.leave1 - 0.5, B.leave1, t)); D.set('baby_a', a)
    homes = [(0.95, -0.17, 0.3), (0.55, -0.24, 1.9)]
    for k, (b, sp) in enumerate(zip(Bb['babies'], Bb['splash'])):
        x0, y0, ph = homes[k]
        if a < 0.01:
            pr.hide(b); [pr.hide(j) for j in sp]; continue
        grow = 1.0 + 0.6 * W.sm(B.grow0, B.grow1, t)
        lv = W.water_level(t)
        if t < B.leave0:
            # paddling and splashing in the river: a hop every 1.6 s
            f = ((t + ph) % 1.6) / 1.6; hop = max(0.0, math.sin(math.pi * min(1.0, f / 0.35))) * 0.05
            x = x0 + 0.10 * math.sin(0.5 * t + ph); y = y0; z = lv - 0.06 + hop; yaw = math.pi * 0.85 + 0.4 * math.sin(0.4 * t + ph)
            for i, j in enumerate(sp):
                sf = (f - 0.30) / 0.35
                if 0 < sf < 1:
                    ang = 2 * math.pi * i / 6 + ph; r = 0.07 * sf
                    pr.set(j, (x + r * math.cos(ang), y + r * math.sin(ang), lv + 0.07 * math.sin(math.pi * sf)), I3, 0.014 * (1 - sf))
                else: pr.hide(j)
        else:
            u = W.sm(B.leave0, B.leave1, t); x = x0 + (-1.55 - x0) * u * (1 + 0.1 * k); y = y0 + (0.95 - y0) * u
            z = gz(x, y, t) - 0.01 + 0.01 * abs(math.sin(6 * t + ph)); yaw = math.atan2(0.95 - y0, -1.55 - x0)
            [pr.hide(j) for j in sp]
        pr.set(b, (x, y, z), rz(yaw), grow)
    pr.commit()


def build_turtle(kit, D):
    pr = Parts('fs_turtle')
    mats = [M.paint(kit, D, 'sz_shell', (0.46, 0.56, 0.30)), M.paint(kit, D, 'sz_turtle', (0.62, 0.70, 0.44), noise=0.0)]
    t = {'shell': pr.add(*sphere((0, 0, 0.030), (0.075, 0.060, 0.040), 2), 0), 'rim': pr.add(*cone((0, 0, 0.022), 0.078, 0.008, 20, 0.074), 0),
         'head': pr.add(*sphere((0.085, 0, 0.032), (0.024, 0.020, 0.018), 2), 1)}
    t['legs'] = [pr.add(*sphere((0, 0, 0.012), (0.020, 0.013, 0.012), 1), 1) for _ in range(4)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 't': t}


TURTLE_K = 1.5


def turtle_pos(t):
    B = W.B; u = W.sm(B.turtle0, B.turtle1, t); x = 1.55 + (0.80 - 1.55) * u; y = -0.95
    return np.array([x, y, gz(x, y, t)]), math.pi


def turtle_pose(Tt, t):
    B = W.B; pr = Tt['parts']; T = Tt['t']; k = TURTLE_K
    show = W.ancient(t) > 0.5 and t < B.flood0
    if not show:
        for v in T.values():
            if isinstance(v, list): [pr.hide(j) for j in v]
            else: pr.hide(v)
        pr.commit(); return
    p, yaw = turtle_pos(t); R = rz(yaw); step = 2 * math.pi * 1.2 * t
    bob = 0.004 * abs(math.sin(step))
    pr.set(T['shell'], p + (0, 0, bob), R, k); pr.set(T['rim'], p + (0, 0, bob), R, k)
    pr.set(T['head'], p + (0, 0, bob), R @ rz(0.2 * math.sin(0.7 * t)), k)
    for i, (lx, ly) in enumerate(((0.05, 0.05), (0.05, -0.05), (-0.05, 0.05), (-0.05, -0.05))):
        sw = 0.012 * math.sin(step + (0 if i in (0, 3) else math.pi))
        pr.set(T['legs'][i], p + R @ (np.array([lx + sw, ly, 0.0]) * k), R, k)
    pr.commit()


def build_leaf(kit, D):
    m = M.paint(kit, D, 'sz_fallleaf', (0.86, 0.72, 0.30), noise=0.0)
    V = [(0, 0, 0)] + [(0.045 * math.cos(a), 0.016 * math.sin(a) * (1 - 0.3 * math.cos(a)), 0) for a in np.linspace(0, 2 * math.pi, 13)[:-1]]
    F = [(0, 1 + i, 1 + (i + 1) % 12) for i in range(12)]
    ob = cw.mk_mesh(kit.bpy, 'fs_leaf', V, F, [m], None, False, kit.coll); ob.hide_render = True; return ob


def leaf_pose(ob, t):
    B = W.B
    if not (B.leaf0 < t < B.mud0): ob.hide_render = True; return
    u = W.sm(B.leaf0, B.leaf1, t); x0, y0, z0 = 1.40, -0.72, W.Z_ANC + 0.62 + W.lift(t); x1, y1 = 1.05, -0.80
    x = x0 + (x1 - x0) * u + 0.06 * math.sin(5.0 * u) * (1 - u); y = y0 + (y1 - y0) * u; z = z0 + (gz(x1, y1, t) + 0.004 - z0) * u
    ob.hide_render = False; ob.location = (x, y, z); ob.rotation_euler = (0.6 * math.sin(7 * u) * (1 - u), 0.4 * math.cos(6 * u) * (1 - u), 3.0 * u)


# ============================================================================== the skeleton that remains (mud beat)
def build_skeleton(kit, D, dn):
    """Cream bones in 3D along the lying pose: vertebrae, ribs round the body, folded leg bones, the skull."""
    P = dn.spine(0.0, 1.0, 0.0, 1.0); n = len(P); k = W.DINO_K; r = dn.r
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
    A = cw._Acc()
    for i in range(1, n - 3, 2):
        rr = 0.30 * r[i] + 0.008; v, f = sphere(P[i], (rr * 1.1, rr * 0.8, rr * 0.8), 1); A.add(v, f)
    for i in range(int(0.42 * n), int(0.67 * n), 2):
        side = np.cross((0, 0, 1), T[i]); side /= np.linalg.norm(side)
        for sd in (-1, 1):
            pts = [P[i] + side * sd * r[i] * math.sin(a) * 0.95 + np.array([0, 0, -r[i] * (1 - math.cos(a)) * 0.95]) for a in np.linspace(0.2, 2.2, 6)]
            v, f = tube(pts, [0.010 * k] * 6, 6); A.add(v, f)
    hd = P[-1] + T[-1] * 0.02 * k; v, f = sphere(hd, (0.075 * k, 0.045 * k, 0.040 * k), 2); A.add(v, f)
    for s in (0.47, 0.64):
        top = P[int(round(s * (n - 1)))]
        for sd in (-1, 1):
            knee = top + np.array([-0.06 * k, sd * 0.15 * k, -top[2] + 0.06 * k]); foot = top + np.array([0.16 * k, sd * 0.10 * k, -top[2] + 0.03 * k])
            v, f = tube([top, knee, foot], [0.018 * k, 0.016 * k, 0.016 * k], 8); A.add(v, f)
    m = M.paint(kit, D, 'sz_skel', (0.98, 0.94, 0.84), alpha='skel_a', noise=0.08)
    ob = A.build(kit.bpy, 'fs_skeleton', [m], True, kit.coll)
    return ob


def skeleton_pose(ob, D, t):
    B = W.B; a = W.sm(B.skel0 + 0.2, B.skel1, t) * (1 - W.sm(B.mud1 - 0.4, B.mud1 + 0.3, t))
    D.set('skel_a', a); ob.hide_render = a < 0.01
    ob.location = (W.DINO_LIE_X, W.DINO_Y, W.Z_ANC - 0.012 + W.lift(t)); ob.rotation_euler = (0, 0, 0)


# ============================================================================== mammoths and saplings (layer on layer)
def build_mammoths(kit, D):
    pr = Parts('fs_mammoths')
    mats = [M.paint(kit, D, 'sz_mammoth', (0.62, 0.38, 0.24)), M.paint(kit, D, 'sz_tusk', (0.98, 0.94, 0.84), noise=0.0), M.paint(kit, D, 'sz_mameye', (0.10, 0.08, 0.12), noise=0.0)]
    out = []
    for k in range(2):
        b = {'body': pr.add(*sphere((0, 0, 0.20), (0.17, 0.11, 0.12), 2), 0), 'hump': pr.add(*sphere((0.06, 0, 0.29), (0.09, 0.08, 0.07), 2), 0),
             'head': pr.add(*sphere((0.17, 0, 0.27), (0.07, 0.065, 0.075), 2), 0),
             'trunk': pr.add(*tube([(0.22, 0, 0.26), (0.26, 0, 0.18), (0.25, 0, 0.10), (0.27, 0, 0.06)], [0.026, 0.020, 0.015, 0.012], 8), 0),
             'eyes': [pr.add(*sphere((0.21, sd * 0.045, 0.29), (0.008, 0.008, 0.008), 1), 2) for sd in (-1, 1)],
             'tusks': [pr.add(*tube([(0.21, sd * 0.03, 0.22), (0.28, sd * 0.05, 0.16), (0.33, sd * 0.04, 0.17), (0.34, sd * 0.02, 0.21)], [0.010, 0.009, 0.007, 0.004], 6), 1) for sd in (-1, 1)],
             'legs': [pr.add(*tube([(0, 0, 0.0), (0, 0, -0.16)], [0.034, 0.032], 8), 0) for _ in range(4)]}
        out.append(b)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'm': out}


def mammoths_pose(Mm, t):
    pr = Mm['parts']; i = 2
    a0, b0 = W.SLOTS[i][1] + 0.12, (W.SLOTS[i + 1][0] - 0.10)
    for k, b in enumerate(Mm['m']):
        show = a0 < t < b0
        if not show:
            for v in b.values():
                if isinstance(v, list): [pr.hide(j) for j in v]
                else: pr.hide(v)
            continue
        u = (t - a0) / (b0 - a0); x = (-1.0 if k == 0 else 0.35) + 0.55 * u; y = 0.30 - 0.55 * k
        sc = (1.15 - 0.2 * k) * W.sm(0.0, 0.15, u) * (1 - W.sm(0.85, 1.0, u))      # they come and go with their era
        if sc < 0.02:
            for v in b.values():
                if isinstance(v, list): [pr.hide(j) for j in v]
                else: pr.hide(v)
            continue
        z = gz(x, y, t); step = 2 * math.pi * 1.4 * t + k; R = rz(0.0); p = np.array([x, y, z + 0.16 * sc + 0.006 * abs(math.sin(step))])
        for key in ('body', 'hump', 'head', 'trunk'): pr.set(b[key], p - (0, 0, 0.16 * sc), R @ (rx(0.0)), sc)
        for j in b['eyes'] + b['tusks']: pr.set(j, p - (0, 0, 0.16 * sc), R, sc)
        for li, (lx, ly) in enumerate(((0.10, 0.06), (0.10, -0.06), (-0.10, 0.06), (-0.10, -0.06))):
            pr.set(b['legs'][li], p + R @ (np.array([lx, ly, 0.0]) * sc), R @ ry(0.35 * math.sin(step + (0 if li in (0, 3) else math.pi))), sc)
    pr.commit()


def build_saplings(kit, D, rng, n=14):
    pr = Parts('fs_saplings')
    mats = [M.paint(kit, D, 'sz_sapling', (0.30, 0.62, 0.36)), M.paint(kit, D, 'sz_saptrunk', (0.46, 0.32, 0.24), noise=0.0)]
    spots = rng.uniform([-W.HX + 0.15, -W.HY + 0.15], [W.HX - 0.15, W.HY - 0.15], (n, 2)); items = []
    for k, (x, y) in enumerate(spots):
        H = rng.uniform(0.34, 0.56); ids = [pr.add(*tube([(0, 0, -0.02), (0, 0, H * 0.6)], [0.012, 0.008], 6), 1)]
        if k % 3 == 0: ids.append(pr.add(*cone((0, 0, H * 0.25), H * 0.22, H * 0.8, 10), 0))
        else: ids.append(pr.add(*sphere((0, 0, H * 0.72), (H * 0.28, H * 0.28, H * 0.30), 2), 0))
        items.append((ids, x, y, rng.uniform(0, 0.3)))
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'items': items}


def saplings_pose(Sp, t):
    pr = Sp['parts']
    for ids, x, y, d in Sp['items']:
        k = 0.0
        for i, e in enumerate(W.SLOT_ERAS):
            if e != 'forest': continue
            a = W.SLOTS[i][1] + 0.1 + d; b = (W.SLOTS[i + 1][0] - 0.05) if i < 4 else W.B.erode0 + 0.6
            k = max(k, W.sm(a, a + 0.45, t) * (1 - W.sm(b - 0.3, b, t)))
        for j in ids:
            if k < 1e-3: pr.hide(j)
            else: pr.set(j, (x, y, gz(x, y, t) - 0.01), I3, k)
    pr.commit()


# ============================================================================== the magnifier window (bone to stone)
DL = 4.5     # the window hangs 4.5 m in front of the camera (in front of the block), in the picture layer


class Lens:
    def __init__(self, kit, D, cam, target_world):
        bpy = kit.bpy; self.kit = kit; self.D = D; self.cam = cam; self.target = np.asarray(target_world, float)
        hw = DL * 18.0 / cam.ob.data.lens; hh = hw * 9 / 16; self.hh = hh
        self.R = 0.47 * hh       # window radius (camera units): about half the half height
        Rl = self.R; self.obs = []
        def own(ob, z):
            ob.parent = cam.ob; ob.matrix_parent_inverse.identity(); ob.location = (0, 0, -DL + z); self.obs.append(ob)
            for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
            return ob
        # the rock inside the window: the bone's own band, with strata stripes and grain
        m = cw._new_mat(bpy, 'fs_lensrock'); g = cw.G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; s = g.sep(P)
        st = g.math('ABSOLUTE', g.math('SINE', g.math('ADD', g.math('MULTIPLY', s[1], 26.0), g.math('MULTIPLY', g.noise(P, 3.0, 2.0).outputs['Fac'], 4.0))))
        col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', st, 0.85), 6.0, clamp=True), 0.5), cw.srgb((0.36, 0.56, 0.52)), cw.srgb((0.52, 0.70, 0.62)))
        col = g.mix(g.math('MULTIPLY', g.noise(P, 30.0, 3.0).outputs['Fac'], 0.3), col, cw.srgb((0.20, 0.34, 0.34)))
        r = g.vmath('LENGTH', g.comb(s[0], s[1], 0.0)); vig = g.math('MULTIPLY', g.math('SUBTRACT', r, Rl * 0.7), 1.0 / (Rl * 0.3), clamp=True)
        col = g.mix(g.math('MULTIPLY', vig, 0.35), col, cw.srgb((0.10, 0.18, 0.22)))
        cw._finish(g, g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}))
        V = [(0, 0, 0)] + [(Rl * math.cos(a), Rl * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 65)[:-1]]
        self.disc = own(cw.mk_mesh(bpy, 'fs_lensdisc', V, [(0, 1 + i, 1 + (i + 1) % 64) for i in range(64)], [m], None, False, kit.coll), 0.0)
        # the big bone: a long shaft with knobbly ends; attribute u runs along it (the stone front), sh for roundness
        V = []; F = []; U = []; SH = []
        def fan(c, pts, u):
            o = len(V); V.append((c[0], c[1], 0)); U.append(u); SH.append(1.0)
            for p in pts: V.append((p[0], p[1], 0)); U.append(u); SH.append(0.0)
            F.extend([(o, o + 1 + i, o + 1 + (i + 1) % len(pts)) for i in range(len(pts))])
        L = Rl * 0.68; w = Rl * 0.17
        for i in range(12):
            x0 = -L + 2 * L * i / 12; x1 = -L + 2 * L * (i + 1) / 12; u = (i + 0.5) / 12
            fan(((x0 + x1) / 2, 0), [(x0, -w), (x1, -w), (x1, w), (x0, w)], u)
        for sx in (-1, 1):
            for sy in (-1, 1):
                c = (sx * L, sy * w * 0.9); fan(c, [(c[0] + w * 1.25 * math.cos(a), c[1] + w * 1.15 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 17)[:-1]], 0.0 if sx < 0 else 1.0)
        m = cw._new_mat(bpy, 'fs_lensbone'); g = cw.G(m.node_tree, kit)
        u = g.attr('u').outputs['Fac']; sh = g.attr('sh').outputs['Fac']; P = g.node('ShaderNodeTexCoord').outputs['Object']
        stone = g.math('MULTIPLY', g.math('SUBTRACT', D.val(g, 'lfront', -0.2), u), 8.0, clamp=True)
        ivory = cw.srgb((0.99, 0.94, 0.80)); grey = g.mix(g.noise(P, 18.0, 3.0).outputs['Fac'], cw.srgb((0.56, 0.60, 0.66)), cw.srgb((0.74, 0.76, 0.78)))
        fl = g.math('LESS_THAN', g.voronoi(P, 30.0 / Rl, 'F1').outputs['Distance'], 0.17)
        grey = g.mix(g.math('MULTIPLY', fl, 0.9), grey, cw.srgb((1.0, 0.82, 0.38)))
        col = g.mix(stone, ivory, grey); col = g.mix(1.0, col, g.math('ADD', 0.70, g.math('MULTIPLY', sh, 0.36)), 'MULTIPLY')
        cw._finish(g, g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}))
        self.bone = own(cw.mk_mesh(bpy, 'fs_lensbone', V, F, [m], None, False, kit.coll, {'u': ('FLOAT', U), 'sh': ('FLOAT', SH)}), 0.002)
        self.L, self.w = L, w
        # pores on the bone (where the water goes in), drops, crystal sparkles
        pr = Parts('fs_lensfx'); rng = np.random.default_rng(41)
        self.pores = []
        for k in range(14):
            x = rng.uniform(-L * 0.9, L * 0.9); y = rng.uniform(-w * 0.55, w * 0.55)
            V = [(0, 0, 0)] + [(0.010 * math.cos(a), 0.008 * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
            self.pores.append((pr.add(V, [(0, 1 + i, 1 + (i + 1) % 8) for i in range(8)], 0), x, y))
        drop = [(0, 0.030, 0), (0.013, 0.0, 0), (0, -0.012, 0), (-0.013, 0.0, 0)]
        star = [(0, 0, 0)] + [((0.034 if q % 2 == 0 else 0.009) * math.cos(math.pi * q / 4), (0.034 if q % 2 == 0 else 0.009) * math.sin(math.pi * q / 4), 0) for q in range(8)]
        self.drops = []
        for k, (j, x, y) in enumerate(self.pores):
            d = pr.add(drop, [(0, 1, 2, 3)], 1); sp = pr.add(star, [(0, 1 + q, 1 + (q + 1) % 8) for q in range(8)], 2)
            self.drops.append((d, sp, x, y, k / len(self.pores) + rng.uniform(-0.03, 0.03)))
        pr.build(bpy, [M.mat_glow(kit, D, 'fs_pore', (0.20, 0.26, 0.30), 1.0), M.mat_glow(kit, D, 'fs_ldrop', (0.42, 0.80, 1.0), 1.6),
                       M.mat_glow(kit, D, 'fs_crystal', (0.90, 1.0, 1.0), 2.2)], kit.coll, smooth=False)
        self.fx = own(pr.ob, 0.004); self.pr = pr
        self.center = None
        self._build_frame(kit, D, own, Rl)

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
        o = W.sm(B.lens0, B.lens1, t) * (1 - W.sm(B.lens2, B.lens3, t))
        show = o > 0.01
        for ob in self.obs: ob.hide_render = not show
        if not show: return
        from mathutils import Vector
        p = self.cam.ob.matrix_basis.inverted() @ Vector(tuple(self.target + np.array([0.0, 0.0, W.lift(t)]))); k = DL / max(-p.z, 1e-3); bx, by = p.x * k, p.y * k   # this frame's camera
        cx, cy = bx + self.R + 0.45, min(by + self.R + 0.18, self.hh * 0.50 - self.R)     # up and to the right of the bone, clear of the caption
        pop = o * (1.0 + 0.06 * math.sin(math.pi * min(1.0, W.sm(B.lens0, B.lens1, t))))
        for ob in (self.disc, self.bone): ob.location = (cx, cy, ob.location.z); ob.scale = (pop, pop, 1)
        front = W.keys(t, [(B.stone0, -0.15), (B.hit, 1.15)]); D.set('lfront', front)
        pr = self.pr; Rl = self.R * pop
        def at(x, y): return np.array([cx + x * pop, cy + y * pop, 0.0])
        for j, x, y in self.pores: pr.set(j, at(x, y), I3, pop * (1 - W.sm(-0.05, 0.05, front - (x / self.L + 1) / 2)))
        for d, sp, x, y, ph in self.drops:
            t_land = B.seep0 + (B.hit - 0.3 - B.seep0) * ph
            f = (t - (t_land - 0.9)) / 0.9
            if 0 < f < 1:
                pr.set(d, at(x, y + (Rl * 0.95 - y) * (1 - f) * (1 - f * 0.2)), I3, pop);
            else: pr.hide(d)
            g = t - t_land
            if g > 0: pr.set(sp, at(x, y), rz(0.8 * t + ph * 6), pop * (0.55 + 0.45 * math.sin(2 * math.pi * (0.8 * t + ph))) * min(1.0, g / 0.15) * (1 + 0.8 * W.win(t, B.hit - 0.05, B.hit + 0.9, 0.25)))
            else: pr.hide(sp)
        D.set('a_lens', min(1.0, o * 1.6))
        v = np.array([cx - bx, cy - by]); dist = np.linalg.norm(v) + 1e-9; u = v / dist; nrm = np.array([-u[1], u[0]])
        self.frame.location = (cx, cy, self.frame.location.z); self.frame.scale = (pop, pop, 1)
        ah = math.atan2(v[1], v[0]) + 0.50                                  # the grip points away from the fossil, a little up
        self.handle.location = (cx, cy, self.handle.location.z); self.handle.scale = (pop, pop, 1); self.handle.rotation_euler = (0, 0, ah)
        self.ring.location = (bx, by, self.ring.location.z); self.ring.scale = (o, o, 1)
        # two fine gold lines from the small ring's sides to the window's sides (a zoom callout)
        co = np.zeros((12, 3), np.float32)
        for k, sd in enumerate((-1, 1)):
            a = np.array([bx, by]) + nrm * sd * 0.078 * o; b = np.array([cx, cy]) + nrm * sd * Rl
            tg = (b - a) / (np.linalg.norm(b - a) + 1e-9); nn = np.array([-tg[1], tg[0]])
            if nn @ UI.LIGHT < 0: nn = -nn
            for q, (pt, hw) in enumerate(((a, 0.0055 * o), (b, 0.0075 * pop))):
                for row, off in enumerate((1.0, 0.0, -1.0)): co[6 * k + 3 * q + row] = (*(pt + nn * off * hw), 0.0)
        me = self.lines.data; me.vertices.foreach_set('co', co.ravel()); me.update()
        pr.commit()
