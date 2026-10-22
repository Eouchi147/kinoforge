"""Venetian props for "Why Venice Sinks", built in code on top of the Cutaway kit (films/styles/cutaway/cutaway.py).

Simplified, charming architecture at about 1:100 (a 4 m block is a few hundred metres of city): palazzi with arched
windows and funnel chimneys, a campanile, the domed church of Santa Maria della Salute, gondolas and boats that move,
small figures, raised walkways, the MOSE gates, a pile driver, pole sections on the cut faces. Everything is a pure
function of time through kit.on_frame callbacks, so any frame renders the same anywhere.
Local frame of every building: the main facade faces local -Y; yaw rotates it about Z.
"""
import math
import numpy as np
import cutaway as cw

PASTELS = [(0.86, 0.62, 0.48), (0.90, 0.78, 0.60), (0.80, 0.48, 0.40), (0.93, 0.86, 0.74), (0.84, 0.70, 0.52),
           (0.74, 0.44, 0.36), (0.90, 0.70, 0.62), (0.82, 0.76, 0.66)]
STONE = (0.93, 0.91, 0.86)          # Istrian stone: white trim, cornices, the Salute
ROOF = (0.66, 0.34, 0.24)
BRICK = (0.62, 0.32, 0.24)
WOOD = (0.46, 0.32, 0.20)


class Mats:
    """Shared materials, with a few values the film animates (window glow at dusk)."""
    def __init__(self, kit):
        self.kit = kit; self.c = {}
        self.glow = None

    def get(self, key, color, rough=0.75, noise=0.12, bump=0.2):
        k = (key, tuple(round(c, 3) for c in color))
        if k not in self.c: self.c[k] = cw.mat_simple(self.kit, 'vz_' + key, color, rough, noise_amt=noise, bump=bump)
        return self.c[k]

    def window(self):
        """Dark glass by day; glows warm at dusk (the film sets the emission strength)."""
        if self.glow is None:
            bpy = self.kit.bpy; m = cw._new_mat(bpy, 'vz_window'); g = cw.G(m.node_tree, self.kit)
            p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': cw.srgb((0.10, 0.11, 0.13)), 'Roughness': 0.25})
            g.put(p, 'Emission Color', cw.srgb((1.0, 0.70, 0.36))); g.put(p, 'Emission Strength', 0.0)
            cw._finish(g, p); self.glow = m; self.glow_socket = cw._sock(p.inputs, 'Emission Strength')
        return self.glow


def _rot(V, yaw):
    c, s = math.cos(yaw), math.sin(yaw); V = np.asarray(V, float)
    return np.column_stack([V[:, 0] * c - V[:, 1] * s, V[:, 0] * s + V[:, 1] * c, V[:, 2]])


def _arch_poly(cx, z0, w, h, n=7):
    """An arched opening outline in the facade plane: (u, z) points, rectangle with a round top."""
    r = w / 2; pts = [(cx - r, z0), (cx + r, z0), (cx + r, z0 + h - r)]
    for k in range(1, n):
        a = math.pi * k / n; pts.append((cx + r * math.cos(a), z0 + h - r + r * math.sin(a)))
    pts.append((cx - r, z0 + h - r)); return pts


def _facade_shapes(A, polys, plane, mat):
    """Flat polygons on a facade plane. plane = (origin, u axis, normal) in local coords; polys in (u, z)."""
    o, u, n = (np.asarray(x, float) for x in plane)
    for P in polys:
        V = [o + u * a + np.array([0, 0, z]) + n * 0.0009 for a, z in P]
        F = [tuple(range(len(V)))] if np.cross(u, [0, 0, 1]) @ n > 0 else [tuple(range(len(V)))[::-1]]
        A.add(V, F, mat)


def palazzo(kit, M, x, y, z, w=0.22, d=0.16, h=0.16, yaw=0.0, wall=None, floors=None, roof='hip', seed=0, water_door=True,
            balcony=True, chimneys=2, name='vz_palazzo'):
    """A Venetian palazzo: body, white cornice and string courses, rows of arched windows on the front and the sides,
    a piano nobile with a grouped arcade and balcony, a water door, a low tiled hip roof and funnel chimneys."""
    rng = np.random.default_rng(seed); wall = wall or PASTELS[seed % len(PASTELS)]
    A = cw._Acc(); mats = [M.get('wall', wall, 0.85, 0.10, 0.25), M.get('stone', STONE, 0.6, 0.05, 0.1), M.window(), M.get('roof', ROOF, 0.7, 0.25, 0.4),
                           M.get('door', (0.20, 0.13, 0.08), 0.6)]
    v, f = cw._box(-w / 2, -d / 2, -0.02, w / 2, d / 2, h); A.add(v, f, 0)
    v, f = cw._box(-w / 2 - 0.004, -d / 2 - 0.004, h - 0.006, w / 2 + 0.004, d / 2 + 0.004, h + 0.002); A.add(v, f, 1)   # cornice
    nf = floors or max(2, int(round(h / 0.045))); fh = h / nf
    for k in range(1, nf):
        v, f = cw._box(-w / 2 - 0.0015, -d / 2 - 0.0015, k * fh - 0.0012, w / 2 + 0.0015, d / 2 + 0.0015, k * fh + 0.0006); A.add(v, f, 1)
    noble = 1 if nf >= 2 else 0
    faces = [((-w / 2, -d / 2, 0), (1, 0, 0), (0, -1, 0), w), ((w / 2, -d / 2, 0), (0, 1, 0), (1, 0, 0), d),
             ((-w / 2, d / 2, 0), (0, -1, 0), (-1, 0, 0), d), ((w / 2, d / 2, 0), (-1, 0, 0), (0, 1, 0), w)]
    faces[2] = ((-w / 2, d / 2, 0), (0, -1, 0), (-1, 0, 0), d)
    for fi, (o, u, n, L) in enumerate(faces):
        polys = []; o = np.asarray(o, float); u = np.asarray(u, float)
        if fi == 2: o = np.array([-w / 2, d / 2, 0.0])
        nw = max(2, int(L / 0.034)); sp = L / nw
        for k in range(nf):
            z0 = k * fh + fh * 0.28; wh = fh * 0.52
            if k == 0 and fi == 0 and water_door:
                polys.append(_arch_poly(L / 2, 0.004, min(0.036, L * 0.2), fh * 0.78)); continue
            if k == noble and fi == 0 and L > 0.12:
                c = L / 2; m = 4 if L > 0.18 else 3; ww = 0.011
                for j in range(m): polys.append(_arch_poly(c + (j - (m - 1) / 2) * (ww + 0.003), z0 - fh * 0.04, ww, wh * 1.15))
                for side in (-1, 1): polys.append(_arch_poly(c + side * L * 0.36, z0, 0.012, wh))
                continue
            for j in range(nw): polys.append(_arch_poly(sp * (j + 0.5), z0, min(0.012, sp * 0.45), wh))
        _facade_shapes(A, polys, (o, u, n), 2)
    if balcony and nf >= 2:
        v, f = cw._box(-w * 0.2, -d / 2 - 0.009, fh * 1.02, w * 0.2, -d / 2, fh * 1.08); A.add(v, f, 1)
    if roof == 'hip':
        o = 0.006; r = min(w, d) * 0.28
        V = [(-w / 2 - o, -d / 2 - o, h + 0.002), (w / 2 + o, -d / 2 - o, h + 0.002), (w / 2 + o, d / 2 + o, h + 0.002), (-w / 2 - o, d / 2 + o, h + 0.002),
             (-w / 2 + r, -d / 2 + r, h + r * 0.55), (w / 2 - r, -d / 2 + r, h + r * 0.55), (w / 2 - r, d / 2 - r, h + r * 0.55), (-w / 2 + r, d / 2 - r, h + r * 0.55)]
        A.add(V, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)], 3)
    for k in range(chimneys):   # Venetian funnel chimneys
        cx = rng.uniform(-w * 0.35, w * 0.35); cy = rng.uniform(-d * 0.3, d * 0.3); zb = h + 0.004
        v, f = cw._tube([(cx, cy, zb), (cx, cy, zb + 0.022), (cx, cy, zb + 0.030), (cx, cy, zb + 0.036)], [0.0035, 0.0035, 0.0075, 0.0085], 8); A.add(v, f, 0)
    ob = A.build(kit.bpy, name, mats, False, kit.coll); ob.location = (x, y, z); ob.rotation_euler = (0, 0, yaw)
    return ob


def campanile(kit, M, x, y, z, h=0.52, w=0.07, name='vz_campanile'):
    """A bell tower: brick shaft with pilaster strips, a white belfry with open arches, an attic and a green copper spire."""
    A = cw._Acc(); mats = [M.get('brick', BRICK, 0.85, 0.2, 0.3), M.get('stone', STONE, 0.6, 0.05, 0.1), M.get('dark', (0.06, 0.06, 0.07), 0.9, 0, 0),
                           M.get('copper', (0.42, 0.62, 0.54), 0.5, 0.15, 0.2), M.get('gold', (0.95, 0.75, 0.30), 0.3, 0, 0)]
    hs = h * 0.62
    v, f = cw._box(-w / 2, -w / 2, -0.02, w / 2, w / 2, hs); A.add(v, f, 0)
    for sx in (-1, 0, 1):
        for side in range(4):
            yaw = side * math.pi / 2; c, s = math.cos(yaw), math.sin(yaw)
            V, F = cw._box(sx * w * 0.36 - 0.004, -w / 2 - 0.003, 0.0, sx * w * 0.36 + 0.004, -w / 2 + 0.001, hs - 0.01)
            A.add(_rot(V, yaw), F, 0)
    v, f = cw._box(-w / 2 - 0.004, -w / 2 - 0.004, hs, w / 2 + 0.004, w / 2 + 0.004, hs + 0.008); A.add(v, f, 1)
    bh = h * 0.12; v, f = cw._box(-w / 2, -w / 2, hs + 0.008, w / 2, w / 2, hs + 0.008 + bh); A.add(v, f, 1)
    for side in range(4):
        yaw = side * math.pi / 2
        for j in range(3):
            P = _arch_poly(-w / 2 + w * (j + 0.5) / 3, hs + 0.014, w / 3 * 0.62, bh * 0.78)
            V = [(a, -w / 2 - 0.0012, zz) for a, zz in P]; A.add(_rot(V, yaw), [tuple(range(len(V)))[::-1]], 2)
    z1 = hs + 0.008 + bh; v, f = cw._box(-w / 2 - 0.004, -w / 2 - 0.004, z1, w / 2 + 0.004, w / 2 + 0.004, z1 + 0.008); A.add(v, f, 1)
    v, f = cw._box(-w * 0.44, -w * 0.44, z1 + 0.008, w * 0.44, w * 0.44, z1 + 0.008 + h * 0.07); A.add(v, f, 0)
    z2 = z1 + 0.008 + h * 0.07; tip = z2 + h * 0.20; r = w * 0.46
    A.add([(-r, -r, z2), (r, -r, z2), (r, r, z2), (-r, r, z2), (0, 0, tip)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], 3)
    V0, F0 = cw._icosphere(1); A.add(V0 * 0.006 + np.array([0, 0, tip + 0.004]), F0, 4)
    ob = A.build(kit.bpy, name, mats, False, kit.coll); ob.location = (x, y, z); return ob


def _revolve(profile, n=24, z0=0.0, sides=None):
    """A solid of revolution from (r, z) pairs; sides=8 makes an octagonal one."""
    n = sides or n; V = []; F = []
    for r, zz in profile:
        for k in range(n):
            a = 2 * math.pi * k / n + (math.pi / n if sides else 0); V.append((r * math.cos(a), r * math.sin(a), zz + z0))
    m = len(profile)
    for i in range(m - 1):
        for k in range(n):
            a = i * n + k; b = i * n + (k + 1) % n; F.append((a, b, b + n, a + n))
    V.append((0, 0, profile[-1][1] + z0)); c = len(V) - 1; base = (m - 1) * n
    F += [(base + k, base + (k + 1) % n, c) for k in range(n)]
    return V, F


def salute(kit, M, x, y, z, s=1.0, yaw=0.0, name='vz_salute'):
    """Santa Maria della Salute, simplified: an octagonal white body, a ring of scroll buttresses, a tall drum, the great
    lead dome with its lantern, a smaller second dome with two little bell towers behind, a temple front with steps."""
    A = cw._Acc(); mats = [M.get('stone', STONE, 0.6, 0.05, 0.1), M.get('lead', (0.70, 0.73, 0.76), 0.45, 0.06, 0.15), M.window(),
                           M.get('stone2', (0.84, 0.82, 0.77), 0.7, 0.05, 0.1)]
    R = 0.15 * s
    v, f = _revolve([(R * 1.05, -0.02), (R * 1.05, 0.0), (R, 0.004), (R, 0.13 * s), (R * 1.04, 0.135 * s), (R * 1.04, 0.145 * s), (R * 0.8, 0.15 * s)], sides=8); A.add(v, f, 0)
    v, f = _revolve([(R * 0.74, 0.14 * s), (R * 0.74, 0.215 * s), (R * 0.78, 0.22 * s), (R * 0.72, 0.226 * s)], sides=16); A.add(v, f, 3)
    prof = [(R * 0.74 * math.cos(a), 0.226 * s + R * 0.86 * math.sin(a)) for a in np.linspace(0, math.pi / 2 * 0.93, 10)]
    v, f = _revolve(prof, 28); A.add(v, f, 1)
    tz = 0.226 * s + R * 0.86
    v, f = _revolve([(R * 0.13, tz - 0.01 * s), (R * 0.13, tz + 0.03 * s), (R * 0.15, tz + 0.033 * s), (R * 0.08, tz + 0.05 * s), (0.002, tz + 0.07 * s)], 12); A.add(v, f, 0)
    for k in range(8):   # scroll buttresses (orecchioni): a ring of small rolls on the octagon's top
        a = 2 * math.pi * (k + 0.5) / 8; c, sn = math.cos(a), math.sin(a)
        p0 = np.array([c * R * 0.95, sn * R * 0.95, 0.15 * s]); p1 = np.array([c * R * 0.78, sn * R * 0.78, 0.19 * s])
        v, f = cw._tube([p0, (p0 + p1) / 2 + [0, 0, 0.012 * s], p1], [0.012 * s, 0.010 * s, 0.008 * s], 8); A.add(v, f, 3)
    for k in range(8):   # tall windows on the drum and arches on the octagon
        a = 2 * math.pi * (k + 0.5) / 16 * 2; u = np.array([-math.sin(a), math.cos(a), 0]); n = np.array([math.cos(a), math.sin(a), 0])
        o = n * R * 0.74 * 0.981 - u * 0.006 * s; _facade_shapes(A, [_arch_poly(0.006 * s, 0.155 * s, 0.009 * s, 0.045 * s)], (o, u, n), 2)
        a2 = 2 * math.pi * k / 8; n2 = np.array([math.cos(a2), math.sin(a2), 0])      # octagon face normals (apothem 0.924 R)
        u2 = np.array([-math.sin(a2), math.cos(a2), 0]); o2 = n2 * R * 0.924 - u2 * 0.012 * s
        _facade_shapes(A, [_arch_poly(0.012 * s, 0.02 * s, 0.016 * s, 0.07 * s)], (o2, u2, n2), 2)
    # second, smaller dome behind (+Y local) with two little bell towers
    off = np.array([0, R * 1.55, 0])
    v, f = _revolve([(R * 0.5, -0.02), (R * 0.5, 0.11 * s), (R * 0.42, 0.115 * s)], sides=8); A.add(np.array(v) + off, f, 0)
    v, f = _revolve([(R * 0.42 * math.cos(a), 0.115 * s + R * 0.5 * math.sin(a)) for a in np.linspace(0, math.pi / 2 * 0.9, 8)], 20); A.add(np.array(v) + off, f, 1)
    for side in (-1, 1):
        p = off + np.array([side * R * 0.62, R * 0.25, 0])
        v, f = cw._box(p[0] - 0.012 * s, p[1] - 0.012 * s, -0.02, p[0] + 0.012 * s, p[1] + 0.012 * s, 0.2 * s); A.add(v, f, 0)
        v, f = _revolve([(0.012 * s, 0.2 * s), (0.004 * s, 0.235 * s)], 8); A.add(np.array(v) + [p[0], p[1], 0], f, 1)
    # temple front with steps down to the water (local -Y)
    fw = R * 0.62; fy = -R * 0.98
    v, f = cw._box(-fw, fy - 0.02 * s, -0.02, fw, fy + 0.02, 0.12 * s); A.add(v, f, 0)
    A.add([(-fw, fy - 0.02 * s, 0.12 * s), (fw, fy - 0.02 * s, 0.12 * s), (0, fy - 0.02 * s, 0.16 * s), (-fw, fy + 0.02, 0.12 * s), (fw, fy + 0.02, 0.12 * s), (0, fy + 0.02, 0.16 * s)],
          [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], 0)
    _facade_shapes(A, [_arch_poly(fw, 0.0, 0.05 * s, 0.085 * s)], (np.array([-fw, fy - 0.02 * s, 0]), np.array([1.0, 0, 0]), np.array([0, -1.0, 0])), 2)
    for k in range(4):
        v, f = cw._box(-fw * 1.3, fy - 0.02 * s - 0.012 * (k + 1), -0.02, fw * 1.3, fy - 0.02 * s - 0.012 * k, 0.012 * (3 - k) * 0.5); A.add(v, f, 3)
    ob = A.build(kit.bpy, name, mats, False, kit.coll); ob.location = (x, y, z); ob.rotation_euler = (0, 0, yaw); return ob


def church(kit, M, x, y, z, w=0.14, d=0.26, h=0.15, yaw=0.0, name='vz_church'):
    """A simple parish church: a nave with a gable roof, a white temple front, a rose window."""
    A = cw._Acc(); mats = [M.get('wall', (0.88, 0.80, 0.70), 0.85, 0.1, 0.25), M.get('stone', STONE, 0.6, 0.05, 0.1), M.get('roof', ROOF, 0.7, 0.25, 0.4), M.window()]
    v, f = cw._box(-w / 2, -d / 2, -0.02, w / 2, d / 2, h); A.add(v, f, 0)
    o = 0.006; r = 0.06
    A.add([(-w / 2 - o, -d / 2, h), (w / 2 + o, -d / 2, h), (0, -d / 2, h + r), (-w / 2 - o, d / 2, h), (w / 2 + o, d / 2, h), (0, d / 2, h + r)],
          [(0, 2, 5, 3), (1, 4, 5, 2), (0, 1, 2), (3, 5, 4)], 2)
    v, f = cw._box(-w / 2 - 0.004, -d / 2 - 0.006, -0.02, w / 2 + 0.004, -d / 2, h + 0.004); A.add(v, f, 1)
    A.add([(-w / 2 - 0.006, -d / 2 - 0.007, h + 0.004), (w / 2 + 0.006, -d / 2 - 0.007, h + 0.004), (0, -d / 2 - 0.007, h + r + 0.008)], [(0, 1, 2)], 1)
    o3 = np.array([-w / 2, -d / 2 - 0.006, 0]); u = np.array([1.0, 0, 0]); n = np.array([0, -1.0, 0])
    _facade_shapes(A, [_arch_poly(w / 2, 0.0, 0.03, 0.06)] + [[(w / 2 + 0.014 * math.cos(a), h * 0.72 + 0.014 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14)[:-1]]], (o3, u, n), 3)
    for side in (-1, 1):
        oo = np.array([side * w / 2, -d / 2, 0]); uu = np.array([0, 1.0, 0]) * (1 if side > 0 else 1); nn = np.array([side * 1.0, 0, 0])
        _facade_shapes(A, [_arch_poly(d * (k + 0.5) / 5, h * 0.35, 0.014, h * 0.45) for k in range(5)], (oo if side > 0 else oo + [0, d, 0], uu if side > 0 else -uu, nn), 3)
    ob = A.build(kit.bpy, name, mats, False, kit.coll); ob.location = (x, y, z); ob.rotation_euler = (0, 0, yaw); return ob


def figure(kit, M, color=(0.3, 0.3, 0.5), h=0.032, name='vz_fig'):
    """A small person: a tapered body and a head. Returned unplaced (the caller animates it)."""
    A = cw._Acc(); mats = [M.get('cloth', color, 0.8, 0.1, 0), M.get('skin', (0.86, 0.66, 0.52), 0.6, 0, 0), M.get('legs', (0.16, 0.16, 0.20), 0.8, 0, 0)]
    v, f = cw._tube([(0, 0, 0), (0, 0, h * 0.45)], [h * 0.07, h * 0.09], 8); A.add(v, f, 2)
    v, f = cw._tube([(0, 0, h * 0.42), (0, 0, h * 0.62), (0, 0, h * 0.80)], [h * 0.13, h * 0.13, h * 0.10], 10); A.add(v, f, 0)
    V0, F0 = cw._icosphere(2); A.add(V0 * h * 0.11 + np.array([0, 0, h * 0.91]), F0, 1)
    return A.build(kit.bpy, name, mats, True, kit.coll)


def gondola(kit, M, name='vz_gondola', rower=True):
    """A black gondola with a silver prow and a gondolier rowing at the stern (the oar rocks). Local: bow along +X."""
    A = cw._Acc(); L = 0.11
    xs = np.linspace(-L / 2, L / 2, 14); pts = [(x, 0, 0.004 + 0.018 * (abs(x) / (L / 2)) ** 3) for x in xs]
    rad = [0.002 + 0.008 * math.sin(math.pi * (k + 0.5) / 14) for k in range(14)]
    v, f = cw._tube(pts, rad, 10); A.add([(a, b * 1.0, c) for a, b, c in v], f, 0)
    v, f = cw._box(L / 2 - 0.004, -0.0006, 0.014, L / 2 + 0.004, 0.0006, 0.026); A.add(v, f, 1)
    ob = A.build(kit.bpy, name, [M.get('black', (0.04, 0.04, 0.05), 0.35, 0, 0), M.get('silver', (0.85, 0.85, 0.85), 0.25, 0, 0)], True, kit.coll)
    ob.scale = (1, 0.7, 1)
    parts = [ob]
    if rower:
        fg = figure(kit, M, (0.94, 0.94, 0.94), 0.028, name + '_g'); fg.parent = ob; fg.location = (-L * 0.36, 0, 0.008)
        oar = cw.mk_mesh(kit.bpy, name + '_oar', *cw._tube([(0, 0, 0), (0.05, 0, -0.03)], [0.0008, 0.0008], 5), [M.get('wood', WOOD, 0.7, 0.2, 0)], None, True, kit.coll)
        oar.parent = ob; oar.location = (-L * 0.32, 0.006, 0.028)
        parts += [fg, oar]
        ob['oar'] = oar.name
    return ob, parts


def boat(kit, M, color=WOOD, L=0.09, people=2, name='vz_boat', seed=0):
    """A small open wooden boat (early lagoon settlers), with people sitting in it."""
    rng = np.random.default_rng(seed); A = cw._Acc()
    xs = np.linspace(-L / 2, L / 2, 12); pts = [(x, 0, 0.004 + 0.008 * (abs(x) / (L / 2)) ** 2) for x in xs]
    rad = [0.003 + 0.010 * math.sin(math.pi * (k + 0.5) / 12) for k in range(12)]
    v, f = cw._tube(pts, rad, 10); A.add(v, f, 0)
    ob = A.build(kit.bpy, name, [M.get('boat', color, 0.75, 0.25, 0.2)], True, kit.coll); ob.scale = (1, 0.9, 0.7)
    parts = [ob]
    for k in range(people):
        c = PASTELS[int(rng.integers(0, len(PASTELS)))]; c = (c[0] * 0.6, c[1] * 0.55, c[2] * 0.5)
        fg = figure(kit, M, c, 0.024, f'{name}_p{k}'); fg.parent = ob; fg.location = ((k - (people - 1) / 2) * L * 0.32, 0, 0.004); parts.append(fg)
    return ob, parts


def walkway(kit, M, a, b, z, width=0.03, h=0.03, name='vz_walk'):
    """Raised wooden walkways for high water: planks on trestles from point a to b (x, y), top at z + h."""
    a = np.array(a, float); b = np.array(b, float); d = b - a; L = np.linalg.norm(d); t = d / L; n = np.array([-t[1], t[0]]); A = cw._Acc()
    for k in range(int(L / 0.09) + 1):
        p = a + t * min(L, k * 0.09)
        for side in (-1, 1):
            q = p + n * side * width * 0.4; v, f = cw._tube([(q[0], q[1], z - 0.01), (q[0], q[1], z + h)], [0.0016, 0.0016], 5); A.add(v, f, 1)
    c = [a - n * width / 2, b - n * width / 2, b + n * width / 2, a + n * width / 2]
    V = [(p[0], p[1], z + h) for p in c] + [(p[0], p[1], z + h + 0.004) for p in c]
    A.add(V, [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 0)
    return A.build(kit.bpy, name, [M.get('plank', (0.62, 0.48, 0.32), 0.8, 0.3, 0.3), M.get('iron', (0.15, 0.15, 0.16), 0.5, 0, 0)], False, kit.coll)


def gate(kit, M, length=0.30, width=0.075, thick=0.03, name='vz_gate'):
    """One MOSE gate: a hollow yellow steel box hinged on the seabed along local Y; rotation about Y raises it."""
    A = cw._Acc(); v, f = cw._box(0, -width / 2 + 0.002, 0, length, width / 2 - 0.002, thick); A.add(v, f, 0)
    for k in range(3):
        x = length * (0.25 + 0.25 * k); v, f = cw._box(x - 0.002, -width / 2 + 0.002, thick, x + 0.002, width / 2 - 0.002, thick + 0.0015); A.add(v, f, 1)
    v, f = cw._tube([(0, -width / 2, 0.0), (0, width / 2, 0.0)], [0.006, 0.006], 10); A.add(v, f, 1)
    return A.build(kit.bpy, name, [M.get('yellow', (0.96, 0.74, 0.12), 0.45, 0.08, 0.1), M.get('steel', (0.30, 0.31, 0.33), 0.4, 0, 0)], False, kit.coll)


def pile_driver(kit, M, x, y, z, name='vz_driver'):
    """A wooden tripod with a heavy weight hauled up and dropped on the pole head. Returns (rig, weight)."""
    A = cw._Acc(); H = 0.20
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3; v, f = cw._tube([(0.07 * math.cos(a), 0.07 * math.sin(a), 0), (0, 0, H)], [0.003, 0.0025], 6); A.add(v, f, 0)
    v, f = cw._tube([(0, 0, H - 0.004), (0, 0, H + 0.004)], [0.008, 0.008], 8); A.add(v, f, 0)
    rig = A.build(kit.bpy, name, [M.get('wood', WOOD, 0.75, 0.25, 0.2)], False, kit.coll); rig.location = (x, y, z)
    W = cw._Acc(); v, f = cw._box(-0.016, -0.016, 0, 0.016, 0.016, 0.03); W.add(v, f, 0)
    v, f = cw._tube([(0, 0, 0.03), (0, 0, H)], [0.0007, 0.0007], 4); W.add(v, f, 1)
    wt = W.build(kit.bpy, name + '_w', [M.get('ironw', (0.22, 0.20, 0.18), 0.6, 0.2, 0.2), M.get('rope', (0.70, 0.62, 0.45), 0.9, 0, 0)], False, kit.coll)
    return rig, wt


def section_mesh(kit, name, mat, n_items):
    """One mesh holding n flat quads on the cut faces (pole sections and the like); update with set_quads()."""
    V = np.zeros((n_items * 4, 3)); F = [(4 * k, 4 * k + 1, 4 * k + 2, 4 * k + 3) for k in range(n_items)]
    ob = cw.mk_mesh(kit.bpy, name, V, F, [mat], None, False, kit.coll)
    return ob


def set_quads(ob, quads):
    """quads: array (n, 4, 3) of corner points (counter-clockwise seen from outside)."""
    q = np.asarray(quads, np.float32).reshape(-1)
    ob.data.vertices.foreach_set('co', q); ob.data.update()


def face_quad(face, s, zb, zt, half, sx, sy, out=0.0012):
    """A vertical quad on a cut face: face '-Y' (s = x) or '+X' (s = y), from zb to zt, half-width half."""
    if face == '-Y':
        y = -sy / 2 - out; return [(s - half, y, zb), (s + half, y, zb), (s + half, y, zt), (s - half, y, zt)]
    x = sx / 2 + out; return [(x, s - half, zb), (x, s + half, zb), (x, s + half, zt), (x, s - half, zt)]


def mat_pole_section(kit, name='vz_polecut', wood=(0.50, 0.36, 0.22), stone=(0.58, 0.58, 0.56)):
    """Wood seen along its length on the cut: grain streaks; a 'stone' value (0..1) turns it mineral grey (the film sets it)."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    hz = g.math('ADD', sx[0], sx[1])
    streak = g.noise(g.comb(g.math('MULTIPLY', hz, 260.0), g.math('MULTIPLY', sx[2], 6.0), 0.0), 1.0, 3.0, 0.6)
    col = g.mix(streak.outputs['Fac'], cw.srgb(tuple(c * 0.75 for c in wood)), cw.srgb(tuple(min(1, c * 1.18) for c in wood)))
    st = g.value(0.0, 'stone'); speck = g.voronoi(pos, 400.0, 'F1')
    scol = g.mix(g.sep(speck.outputs['Color'])[0], cw.srgb(stone), cw.srgb(tuple(c * 0.8 for c in stone)))
    col = g.mix(st, col, scol)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.8})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.3, 'Height': streak.outputs['Fac'], 'Distance': 0.002}); g.put(p, 'Normal', b)
    cw._finish(g, p); st.node.label = 'stone'
    return m


def mat_band(kit, name, color, grain=0.35, pebbles=0.0, wet=0.0, alt=None):
    """A flat strata band for the hand-drawn sections (same feel as the kit's strata: grain, a few pebbles). With alt, a
    Value node labelled 'mix' blends the base colour towards alt (the film animates it)."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']
    n1 = g.noise(pos, 60.0, 5.0, 0.6); n2 = g.noise(pos, 4.0, 3.0)
    base = cw.srgb(color)
    if alt is not None:
        mv = g.value(0.0, 'mix'); base = g.mix(mv, cw.srgb(color), cw.srgb(alt))
    col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], grain), base, g.mix(0.55, base, (0, 0, 0), 'MULTIPLY'))
    col = g.mix(g.math('MULTIPLY', n2.outputs['Fac'], 0.2), col, g.mix(0.5, col, (1, 1, 1), 'SCREEN'))
    if pebbles > 0:
        vp = g.voronoi(pos, 34.0, 'F1'); rr = g.sep(vp.outputs['Color'])
        peb = g.math('MULTIPLY', g.math('SUBTRACT', g.math('MULTIPLY', rr[0], 0.3 * pebbles), vp.outputs['Distance']), 25.0, clamp=True)
        col = g.mix(peb, col, cw.srgb((0.70, 0.66, 0.58)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.9 - 0.4 * wet})
    cw._finish(g, p); return m
