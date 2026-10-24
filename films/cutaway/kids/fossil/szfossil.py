"""How does a dinosaur turn into stone? The skeleton in the front cut face, and the water and gold that change it.

The bones are flat painted shapes laid on the front (-Y) face, a hair in front of it, under the dinosaur's lying place:
vertebrae along the spine (long in the neck, small in the tail), ribs over the body, folded leg bones, the hips and the
shoulder blade, a rounded skull. Each shape is a fan from its centre line (attribute sh: 1 at the centre, 0 at the rim,
so the paint is rounder in the middle) and carries bi, its place along the skeleton (0 tail tip, 1 skull). An ink
outline sits just behind. Emission only, so Fable leaves the colours as set here.
  hook               stone bones with a glint travelling over them (a glinting fossil in the rock)
  rewind             the stone fades (we go back to when it was alive)
  mud                fresh cream bones appear in the new mud band once the mud covers the skeleton
  bone to stone      blue drops creep down through the layers into the bones, the bones darken with water
  bone to stone      a front moves along the skeleton, cream to blue-grey stone with gold flecks; on the music hit a burst
                     of gold sparkles over the whole fossil (the reveal)
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, dino_fossil_2d, sphere, I3, rx

Y_FACE = -W.HY - 0.0018


class Shapes:
    def __init__(self): self.V = []; self.F = []; self.sh = []; self.bi = []
    def fan(self, center, rim, bi):
        o = len(self.V); self.V.append(center); self.sh.append(1.0); self.bi.append(bi)
        for p in rim: self.V.append(p); self.sh.append(0.0); self.bi.append(bi)
        n = len(rim); self.F += [(o, o + 1 + k, o + 1 + (k + 1) % n) for k in range(n)]
    def strip(self, pts, widths, bi):
        """A curved bone (a rib): three rows (edge, centre, edge)."""
        P = np.asarray(pts, float); T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9; N = np.column_stack([-T[:, 1], T[:, 0]])
        o = len(self.V); n = len(P)
        for i in range(n):
            for s, shv in ((-1, 0.0), (0, 1.0), (1, 0.0)):
                q = P[i] + N[i] * widths[i] * s; self.V.append(q); self.sh.append(shv); self.bi.append(bi)
        for i in range(n - 1):
            a = o + 3 * i; self.F += [(a, a + 3, a + 4, a + 1), (a + 1, a + 4, a + 5, a + 2)]


def _ellipse(c, rx_, rz_, ang=0.0, n=16):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0] + rx_ * math.cos(a) * ca - rz_ * math.sin(a) * sa, c[1] + rx_ * math.cos(a) * sa + rz_ * math.sin(a) * ca) for a in np.linspace(0, 2 * math.pi, n + 1)[:-1]]


def _capsule(a, b, r, n=6):
    a = np.asarray(a, float); b = np.asarray(b, float); d = b - a; L = np.linalg.norm(d) + 1e-9; u = d / L; ang = math.atan2(u[1], u[0])
    pts = [tuple(b + r * np.array([math.cos(ang - math.pi / 2 + math.pi * k / n), math.sin(ang - math.pi / 2 + math.pi * k / n)])) for k in range(n + 1)]
    pts += [tuple(a + r * np.array([math.cos(ang + math.pi / 2 + math.pi * k / n), math.sin(ang + math.pi / 2 + math.pi * k / n)])) for k in range(n + 1)]
    return pts


def skeleton(grow=0.0):
    """2D skeleton in face coordinates (x, z), placed under the lying dinosaur. grow = outline dilation (m)."""
    P, R = dino_fossil_2d(W.DINO_K); P = P + np.array([W.DINO_LIE_X, W.Z_ANC]); n = len(P); u = np.linspace(0, 1, n)
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; Nn = np.column_stack([-T[:, 1], T[:, 0]])
    S = Shapes(); g = grow
    # vertebrae: a bead every few samples, long in the neck, round in the back, tiny in the tail
    for i in range(1, n - 3):
        if 0.35 <= u[i] <= 0.72 and i % 2: continue           # the back: a bead every other sample; neck and tail: every sample
        r = 0.55 * R[i] + 0.018
        if u[i] > 0.72: S.fan(tuple(P[i]), _capsule(P[i] - T[i] * 0.020, P[i] + T[i] * 0.020, 0.80 * r + g), u[i])
        else: S.fan(tuple(P[i]), _ellipse(P[i], 0.58 * r + 0.004 + g, 0.80 * r + g, math.atan2(T[i, 1], T[i, 0])), u[i])
    # ribs: curved bones from the spine down over the belly
    for i in range(int(0.42 * n), int(0.67 * n), 2):
        a = P[i]; L = 0.85 * R[i]; d = -Nn[i]
        if d[1] > 0: d = -d
        pts = [a + d * L * s + T[i] * (-0.05 * L * s * s) for s in np.linspace(0.12, 1.0, 6)]
        S.strip(pts, [0.013 + g, 0.014 + g, 0.014 + g, 0.013 + g, 0.011 + g, 0.008 + g], u[i])
    # hips and shoulder blade
    ih, isd = int(0.47 * (n - 1)), int(0.64 * (n - 1))
    S.fan(tuple(P[ih] - Nn[ih] * 0.03), _ellipse(P[ih] - Nn[ih] * 0.03, 0.085 + g, 0.050 + g, 0.2), u[ih])
    S.fan(tuple(P[isd] - Nn[isd] * 0.03), _ellipse(P[isd] - Nn[isd] * 0.03, 0.070 + g, 0.040 + g, -0.5), u[isd])
    # folded legs: thigh and shin bones with knobbly ends, a foot
    for i0, sgn in ((ih, 1.0), (isd, 1.0)):
        top = P[i0] - Nn[i0] * 0.06; knee = np.array([top[0] - 0.10, W.Z_ANC + 0.045]); foot = np.array([top[0] + 0.11, W.Z_ANC + 0.020])
        for a, b in ((top, knee), (knee, foot)):
            S.fan(tuple((a + b) / 2), _capsule(a, b, 0.017 + g), u[i0])
            for c in (a, b): S.fan(tuple(c), _ellipse(c, 0.026 + g, 0.023 + g), u[i0])
        S.fan(tuple(foot + (0.03, 0)), _ellipse(foot + np.array([0.03, 0.0]), 0.034 + g, 0.012 + g), u[i0])
    # the skull: a rounded cranium and a blunt snout, resting on the ground at the end of the neck
    h = P[-1] + T[-1] * 0.03; ang = math.atan2(T[-1, 1], T[-1, 0]) * 0.5
    S.fan(tuple(h), _ellipse(h, 0.098 + g, 0.060 + g, ang, 20), 1.0)
    sn = h + np.array([math.cos(ang), math.sin(ang)]) * 0.085
    S.fan(tuple(sn), _ellipse(sn, 0.060 + g, 0.036 + g, ang, 16), 1.0)
    return S


def build(kit, D):
    bpy = kit.bpy
    S = skeleton(0.0)
    V = [(x, Y_FACE, z) for x, z in S.V]
    bones = cw.mk_mesh(bpy, 'fs_bones', V, S.F, [M.mat_bones(kit, D)], None, False, kit.coll, {'sh': ('FLOAT', S.sh), 'bi': ('FLOAT', S.bi)})
    O = skeleton(0.007)
    ink = M.mat_glow(kit, D, 'fs_bone_ink', (0.10, 0.10, 0.20), 1.0, 'balpha')
    outline = cw.mk_mesh(bpy, 'fs_bones_ink', [(x, Y_FACE + 0.0008, z) for x, z in O.V], O.F, [ink], None, False, kit.coll)
    # the eye socket of the skull (a darker hollow)
    P, R = dino_fossil_2d(W.DINO_K); P = P + np.array([W.DINO_LIE_X, W.Z_ANC]); T = P[-1] - P[-2]; T /= np.linalg.norm(T)
    c = P[-1] + T * 0.040 + np.array([0, 0.014]); V, F = [], []
    V.append((c[0], Y_FACE - 0.0006, c[1])); V += [(c[0] + 0.017 * math.cos(a), Y_FACE - 0.0006, c[1] + 0.015 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 13)[:-1]]
    F = [(0, 1 + k, 1 + (k + 1) % 12) for k in range(12)]
    sock = cw.mk_mesh(bpy, 'fs_socket', V, F, [ink], None, False, kit.coll)
    # sparkles (gold, four-pointed stars) and drops (blue diamonds), facing out of the face
    pr = Parts('fs_sparkle')
    star = [(0, 0, 0)] + [((0.03 if k % 2 == 0 else 0.008) * math.cos(math.pi * k / 4), 0, (0.03 if k % 2 == 0 else 0.008) * math.sin(math.pi * k / 4)) for k in range(8)]
    sf = [(0, 1 + k, 1 + (k + 1) % 8) for k in range(8)]
    drop = [(0, 0, 0.022), (0.010, 0, 0.0), (0, 0, -0.012), (-0.010, 0, 0.0)]
    rng = np.random.default_rng(31)
    Pb = np.array(S.V); bi = np.array(S.bi)
    sp = []
    for k in range(46):
        j = rng.integers(0, len(Pb)); sp.append((pr.add(star, sf, 0), Pb[j], bi[j], rng.uniform(0, 1), rng.uniform(0.6, 1.3)))
    dr = []
    xs = np.linspace(Pb[:, 0].min() + 0.05, Pb[:, 0].max() - 0.05, 30)
    for k, x in enumerate(xs):
        zt = float(np.interp(x, Pb[:, 0], Pb[:, 1]))
        tgt = Pb[np.argmin(np.abs(Pb[:, 0] - x) + 5 * np.abs(Pb[:, 1] - zt))]
        dr.append((pr.add(drop, [(0, 1, 2, 3)], 1), x + rng.uniform(-0.02, 0.02), tgt[1] + rng.uniform(0.0, 0.03), rng.uniform(0, 1)))
    glint = pr.add(star, sf, 2)
    pr.build(bpy, [M.mat_glow(kit, D, 'fs_gold', (1.0, 0.84, 0.36), 2.4), M.mat_glow(kit, D, 'fs_drop', (0.40, 0.80, 1.0), 1.8),
                   M.mat_glow(kit, D, 'fs_glint', (1.0, 0.97, 0.86), 2.6)], kit.coll, smooth=False)
    for ob in (bones, outline, sock, pr.ob):
        for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission'): setattr(ob, a, False)
    return {'bones': bones, 'outline': outline, 'sock': sock, 'parts': pr, 'sp': sp, 'dr': dr, 'glint': glint, 'P': Pb}


def pose(Fo, D, t):
    B = W.B; pr = Fo['parts']
    for k in ('bones', 'outline', 'sock'): Fo[k].location = (0.0, 0.0, W.lift(t))     # the fossil rides the lifted slice
    pr.ob.location = (0.0, 0.0, W.lift(t))
    today_a = 1 - W.sm(B.rw0 - 0.1, B.rw0 + 0.9, t)                      # the stone fossil of today, fading in the rewind
    later_a = W.sm(B.bones_in0, B.bones_in1, t)                          # the bones tucked in by the blanket, and after
    a = today_a if t < B.bones_in0 else later_a
    D.set('balpha', a)
    for k in ('bones', 'outline', 'sock'): Fo[k].hide_render = a < 0.01
    front = 1.25 if t < B.bones_in0 else W.keys(t, [(B.stone0, -0.15), (B.hit, 1.15)])
    D.set('front', front)
    wet = W.keys(t, [(B.seep0 + 0.6, 0.0), (B.seep1, 1.0), (B.hit + 0.6, 0.0)]) if B.seep0 < t < B.hit + 1.0 else 0.0
    D.set('wet', wet)
    burst = W.keys(t, [(B.hit - 0.05, 0.0), (B.hit + 0.15, 1.0), (B.hit + 1.8, 0.0)]) if B.hit - 0.1 < t < B.hit + 2.0 else 0.0
    D.set('bglow', burst + 0.25 * today_a * (t < B.rw0))
    # gold sparkles: a burst on the hit, then a few twinkles while the stone settles; a few on today's fossil too
    for j, p, bi, ph, sz in Fo['sp']:
        tw = 0.5 + 0.5 * math.sin(2 * math.pi * (1.3 * t + ph))
        s = burst * (0.6 + 0.6 * tw) * sz
        if t < B.hit and B.stone0 < t:     # sparkle where the stone front passes
            s = max(s, 0.8 * sz * max(0.0, 1 - abs(front - bi) / 0.08))
        if t > B.hit + 1.5 and t < B.rain0: s = max(s, 0.5 * sz * max(0.0, math.sin(2 * math.pi * (0.5 * t + ph))) ** 8)
        if t < B.rw0 or t > B.green1: s = max(s, 0.55 * sz * max(0.0, math.sin(2 * math.pi * (0.35 * t + ph))) ** 12 * (today_a if t < B.rw0 else 1.0))
        if t > B.green1: s *= W.era(t)
        if s < 0.02 or a < 0.05: pr.hide(j)
        else: pr.set(j, (p[0], Y_FACE - 0.003, p[1]), rx(0.0) @ np.array([[math.cos(t * 1.5 + ph * 6), 0, -math.sin(t * 1.5 + ph * 6)], [0, 1, 0], [math.sin(t * 1.5 + ph * 6), 0, math.cos(t * 1.5 + ph * 6)]]), s)
    # blue drops creep down from the top of the face into the bones (bone to stone, alongside the magnifier window)
    top = W.base(t)
    for j, x, zt, ph in Fo['dr']:
        if not (B.seep0 < t < B.seep1 + 0.8): pr.hide(j); continue
        T = 1.9; age = ((t - B.seep0 + ph * T) % T) / T
        z = top - 0.02 - (top - 0.02 - zt) * age; s = 1.2 * min(1.0, age * 6) * (1 - W.sm(0.85, 1.0, age)) * W.win(t, B.seep0, B.seep1 + 0.8, 0.5)
        if s < 0.02: pr.hide(j)
        else: pr.set(j, (x, Y_FACE - 0.003, z), I3, s)
    # the hook's glint: one bright star sliding along the bones, every 1.6 s (today, before the rewind and at the end)
    if (t < B.rw0 or t > B.green1 + 1.0) and a > 0.3:
        u = (t % 1.6) / 1.6; P = Fo['P']; xs = P[:, 0]; x = xs.min() + (xs.max() - xs.min()) * u
        k = np.argmin(np.abs(xs - x) - 0.5 * P[:, 1]); s = 1.4 * math.sin(math.pi * u)
        pr.set(Fo['glint'], (P[k, 0], Y_FACE - 0.004, P[k, 1]), I3, s)
    else:
        pr.hide(Fo['glint'])
    pr.commit()
