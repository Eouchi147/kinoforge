"""The storybook graphics kit of the fossil film: flat painted pieces set in code (cards, gold bands, ribbons, stars).

Everything here is a flat mesh in the picture layer ('type' layer of the Fable look: crisp, over the brushwork). Each
piece carries two point attributes the materials read: `e` (0 on the outside of a band or card, 1 on the inside; also the
soft-edge amount of a shadow) and `sh` (a painted shading value, 0 dark to 1 bright). The gold is shaded like a rounded
tube lit from the upper left, so a thin line reads as a real gold rim. Materials are emission whose colour is a node
chain (never a plain default), so Fable's word recolouring (ink and paper) leaves them alone.
No fonts here: the font file is Fredoka Bold (OFL), in fonts/, loaded by szwords.py.
"""
import math

import numpy as np

import cutaway as cw
from cutaway import G, srgb
import szmats as M

LIGHT = np.array([-0.52, 0.85])          # the painted light comes from the upper left
GOLD = ((0.46, 0.25, 0.04), (0.88, 0.60, 0.11), (1.0, 0.85, 0.40))     # dark, base, bright
PLUM = (0.21, 0.10, 0.27)                # the ink of the words: deep warm plum, never black
PAPER = ((0.995, 0.945, 0.80), (0.965, 0.865, 0.64), (0.90, 0.72, 0.46))   # light, mottle, edge tan


# ---------------------------------------------------------------------------------------------- outlines
def rrect_loop(w, h, r, seed=0, amp=0.0, step=0.045, narc=7):
    """A rounded rectangle outline, counter-clockwise: (points (m,2), outward normals (m,2)). `amp` roughens the edge
    along its normal with two slow sines (a hand-cut edge); the same wobble for every inset of the same shape."""
    pts = []; nr = []
    cs = [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]
    for ci, (cx, cy, a0) in enumerate(cs):
        for k in range(narc + 1):
            a = math.radians(a0 + 90.0 * k / narc); pts.append((cx + r * math.cos(a), cy + r * math.sin(a))); nr.append((math.cos(a), math.sin(a)))
        nx = cs[(ci + 1) % 4]; a1 = math.radians(nx[2])
        p0 = pts[-1]; p1 = (nx[0] + r * math.cos(a1), nx[1] + r * math.sin(a1)); L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        m = int(L / step)
        for j in range(1, m):
            u = j / m; pts.append((p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)); nr.append((math.cos(a1), math.sin(a1)))
    P = np.array(pts); N = np.array(nr)
    if amp:
        rng = np.random.default_rng(seed); s = np.arange(len(P)) / len(P); ph = rng.uniform(0, 6.28, 3)
        d = amp * (np.sin(2 * math.pi * 3 * s + ph[0]) + 0.55 * np.sin(2 * math.pi * 7 * s + ph[1]) + 0.3 * np.sin(2 * math.pi * 13 * s + ph[2]))
        P = P + N * d[:, None]
    return P, N


def circle_loop(r, n=48):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False); N = np.column_stack([np.cos(a), np.sin(a)]); return N * r, N


class Flat:
    """Accumulates flat pieces (z per piece, a material slot each) into one mesh with the e / sh point attributes."""
    def __init__(self): self.V = []; self.F = []; self.M = []; self.E = []; self.S = []

    def _loop(self, P, N, off, e, sh, z, at=(0.0, 0.0)):
        sh = np.broadcast_to(np.asarray(sh, float), (len(P),)); Q = P + N * off + np.asarray(at)[None, :]; o = len(self.V)
        for i, (x, y) in enumerate(Q): self.V.append((x, y, z)); self.E.append(e); self.S.append(float(sh[i]))
        return list(range(o, o + len(P)))

    def band(self, P, N, rows, mat, z, at=(0.0, 0.0)):
        """rows: [(offset along the normal, e, sh)], outermost first; quads between consecutive rows."""
        ids = [self._loop(P, N, off, e, sh, z, at) for off, e, sh in rows]; m = len(P)
        for a, b in zip(ids, ids[1:]):
            for i in range(m): j = (i + 1) % m; self.F.append((a[i], a[j], b[j], b[i])); self.M.append(mat)
        return ids[-1]

    def fan(self, P, N, off, e, sh, mat, z, at=(0.0, 0.0), centre_sh=None):
        ids = self._loop(P, N, off, e, sh, z, at); c = len(self.V); cxy = P.mean(axis=0) + np.asarray(at)
        self.V.append((cxy[0], cxy[1], z)); self.E.append(e); self.S.append(float(np.mean(sh) if centre_sh is None else centre_sh))
        for i in range(len(ids)): self.F.append((c, ids[i], ids[(i + 1) % len(ids)])); self.M.append(mat)

    def tube(self, P, N, width, mat, z, grow=0.0, at=(0.0, 0.0)):
        """A gold band of `width` centred on the loop, shaded as a rounded tube lit from the upper left (outer half turns to
        the light on its upper-left side, the inner half on its lower-right side, a bright crest down the middle)."""
        d = (N @ LIGHT) / np.linalg.norm(LIGHT)
        so = np.clip(0.46 + 0.34 * d, 0, 1); si = np.clip(0.40 - 0.30 * d, 0, 1); sm = np.clip(0.66 + 0.16 * d, 0, 1)
        self.band(P, N, [(width / 2 + grow, 0.0, so), (grow * 0.5, 0.5, sm), (-width / 2, 1.0, si)], mat, z, at)

    def star(self, c, s, mat, z, sh=0.9):
        pts = []
        for q in range(8):
            r = s if q % 2 == 0 else s * 0.26; a = math.pi * q / 4 + math.pi / 2; pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
        o = len(self.V); self.V.append((c[0], c[1], z)); self.E.append(0.5); self.S.append(1.0)
        for p in pts: self.V.append((p[0], p[1], z)); self.E.append(0.5); self.S.append(sh * 0.45)
        for q in range(8): self.F.append((o, o + 1 + q, o + 1 + (q + 1) % 8)); self.M.append(mat)

    def poly(self, pts, mat, z, e=0.5, sh=0.7, es=None, ss=None):
        o = len(self.V)
        for k, p in enumerate(pts): self.V.append((p[0], p[1], z)); self.E.append(e if es is None else es[k]); self.S.append(sh if ss is None else ss[k])
        for k in range(1, len(pts) - 1): self.F.append((o, o + k, o + k + 1)); self.M.append(mat)

    def strip(self, A, B, mat, z, es=0.5, ss=0.7):
        """Quads between two matching point lists (the two sides of a curved band); es / ss: value or one per point pair."""
        n = len(A); es = np.broadcast_to(np.asarray(es, float), (n,)); ss = np.broadcast_to(np.asarray(ss, float), (n,)); o = len(self.V)
        for i in range(n): self.V.append((A[i][0], A[i][1], z)); self.E.append(float(es[i])); self.S.append(float(ss[i]))
        for i in range(n): self.V.append((B[i][0], B[i][1], z)); self.E.append(float(es[i])); self.S.append(float(ss[i]) * 0.6)
        for i in range(n - 1): self.F.append((o + i, o + i + 1, o + n + i + 1, o + n + i)); self.M.append(mat)

    def build(self, bpy, name, mats, coll):
        return cw.mk_mesh(bpy, name, self.V, self.F, mats, self.M, False, coll, {'e': ('FLOAT', self.E), 'sh': ('FLOAT', self.S)})


# ---------------------------------------------------------------------------------------------- materials
def _mat(kit, D, name, alpha, colour, amul=None):
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    c = colour(g)
    if isinstance(c, (tuple, list)): n = g.node('ShaderNodeRGB'); n.outputs[0].default_value = tuple(c); c = n.outputs[0]     # a node, so Fable's recolour cannot reach it
    e = g.node('ShaderNodeEmission', ins={'Color': c, 'Strength': 1.0})
    a = D.val(g, alpha, 1.0)
    if amul is not None: a = g.math('MULTIPLY', a, amul(g))
    M._alpha_out(g, e, a); return m


def _attr(g, name): return g.attr(name).outputs['Fac']


def mat_gold(kit, D, name, alpha, palette=None):
    """Painted gold (or any 3-colour palette: dark, base, bright): by the shading value, a little brush-noise so it is not plastic."""
    pal = palette or GOLD
    def col(g):
        P = g.node('ShaderNodeTexCoord').outputs['Object']; n = g.noise(P, 38.0, 3.0).outputs['Fac']
        s = g.math('ADD', _attr(g, 'sh'), g.math('MULTIPLY', g.math('SUBTRACT', n, 0.5), 0.14), clamp=True)
        c = g.mix(g.math('MULTIPLY', s, 2.0, clamp=True), srgb(pal[0]), srgb(pal[1]))
        return g.mix(g.math('SUBTRACT', g.math('MULTIPLY', s, 2.0), 1.0, clamp=True), c, srgb(pal[2]))
    return _mat(kit, D, name, alpha, col)


def mat_paper(kit, D, name, alpha):
    """Warm parchment: cream with soft mottle, fibres, a tan toned edge (e = 0 outside) and a lighter top (sh)."""
    def col(g):
        P = g.node('ShaderNodeTexCoord').outputs['Object']; x = g.sep(P)
        mot = g.noise(P, 7.0, 4.0, 0.6).outputs['Fac']; fib = g.noise(g.comb(g.math('MULTIPLY', x[0], 1.0), g.math('MULTIPLY', x[1], 9.0), 0.0), 40.0, 2.0).outputs['Fac']
        c = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', mot, 0.30), 1.6, clamp=True), srgb(PAPER[0]), srgb(PAPER[1]))
        c = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', fib, 0.58), 1.1, clamp=True), c, srgb((0.93, 0.80, 0.58)))
        c = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', _attr(g, 'sh'), 0.5), 0.5), c, srgb((1.0, 0.98, 0.90)), 'MIX', clamp=True)
        edge = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', _attr(g, 'e'), 1.6, clamp=True)), 0.75)
        return g.mix(edge, c, srgb(PAPER[2]))
    return _mat(kit, D, name, alpha, col)


def mat_face(kit, D, name, alpha):
    """The watch face: cream, brighter in the middle, a faint warm rim shade (e = 1 in the middle)."""
    def col(g):
        c = g.mix(g.math('SUBTRACT', 1.0, _attr(g, 'e')), srgb((1.0, 0.975, 0.88)), srgb((0.96, 0.86, 0.66)))
        P = g.node('ShaderNodeTexCoord').outputs['Object']
        return g.mix(g.math('MULTIPLY', g.math('SUBTRACT', g.noise(P, 30.0, 3.0).outputs['Fac'], 0.5), 0.10), c, srgb((0.90, 0.78, 0.56)))
    return _mat(kit, D, name, alpha, col)


def mat_flat(kit, D, name, alpha, colour, taper=False):
    """One colour (a node, so Fable never recolours it); `taper` fades the alpha by e (soft shadows and glints)."""
    return _mat(kit, D, name, alpha, lambda g: srgb(colour), (lambda g: _attr(g, 'e')) if taper else None)


def mat_shadow(kit, D, name, alpha, strength=0.34):
    return _mat(kit, D, name, alpha, lambda g: srgb((0.30, 0.15, 0.10)), lambda g: g.math('MULTIPLY', g.math('SUBTRACT', 1.0, _attr(g, 'e')), strength))


# ---------------------------------------------------------------------------------------------- the card
def card(fl, w, h, r, seed, mats, z=0.0):
    """A storybook label: warm shadow, gold rim, parchment with a toned edge, a thin gold inner line, two gold sparkles.
    mats = (shadow, gold, paper). One mesh, drawn back to front by z."""
    P, N = rrect_loop(w, h, r, seed, 0.0030)
    # shadow: soft, warm, offset down and a little right so the card floats
    fl.band(P, N, [(0.045, 1.0, 0.0), (0.020, 0.55, 0.0), (-0.004, 0.0, 0.0)], mats[0], z, at=(0.010, -0.030))
    fl.fan(P, N, -0.004, 0.0, 0.0, mats[0], z, at=(0.010, -0.030))
    # parchment (a toned edge that lightens inward), then the gold rim on top of its border
    top = np.clip(0.55 + 0.45 * P[:, 1] / (h / 2), 0, 1)
    fl.band(P, N, [(-0.002, 0.0, top), (-0.020, 0.45, top), (-0.060, 1.0, top)], mats[2], z + 0.0008)
    fl.fan(P, N, -0.060, 1.0, top, mats[2], z + 0.0008)
    fl.tube(P, N, 0.020, mats[1], z + 0.0016, grow=0.006)
    # a thin inner gold line, like a printed picture-book frame
    fl.band(P, N, [(-0.034, 0.0, 0.52), (-0.0375, 0.5, 0.80), (-0.041, 1.0, 0.52)], mats[1], z + 0.0020)
    # two gold sparkles on opposite corners
    fl.star((-w / 2 + 0.012, h / 2 - 0.006), 0.060, mats[1], z + 0.0030); fl.star((w / 2 - 0.016, -h / 2 + 0.010), 0.045, mats[1], z + 0.0030)
    fl.star((w / 2 - 0.070, h / 2 + 0.002), 0.026, mats[1], z + 0.0030)
