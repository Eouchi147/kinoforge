"""Props of the Arabia film: lettering (title, labels, tiles, verse), scroll, bowls, thorn bush, footprint stamps, houses, lamp fields."""
import math
import numpy as np
from kit import *
from kit import _mat
from actors import pivot, mk, torus, D

def cream_letters(bpy, name, col=(0.96, 0.90, 0.74), emit=0.55, seed=1):
    m = clay(bpy, name, col, tuple(x * 0.86 for x in col), rough=0.55, seed=seed, var_scale=14.0)
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Emission Color'].default_value = srgb(col); n.inputs['Emission Strength'].default_value = emit
    return m

class Lettering:
    """Letters/words as separate clay objects under one pivot; each has an x offset (centred), so they can pop in one by one."""
    def __init__(self, bpy, name, coll, text, size, mat, per='letter', extrude=0.006, bevel=0.0016, plane='XZ', spacing=1.0, seed=1):
        self.root = pivot(bpy, name + '_root', coll); self.items = []; self.text = text
        def width(s):
            if not s.strip(): return 0.0
            o = text_mesh(bpy, name + '_m', s + '|', size, None, coll, extrude=extrude, bevel=bevel, align='LEFT', plane=plane, spacing=spacing)
            w = max(v.co.x for v in o.data.vertices); o2 = text_mesh(bpy, name + '_m2', '|', size, None, coll, extrude=extrude, bevel=bevel, align='LEFT', plane=plane, spacing=spacing)
            w2 = max(v.co.x for v in o2.data.vertices)
            for ob in (o, o2): bpy.data.objects.remove(ob); 
            return w - w2
        units = list(text) if per == 'letter' else text.split(' ')
        pos = []; acc = 0.0
        if per == 'letter':
            for k, ch in enumerate(units): pos.append(width(text[:k])); 
            total = width(text)
        else:
            for k, w_ in enumerate(units): pos.append(width(' '.join(units[:k]) + (' ' if k else ''))); 
            total = width(text)
        for k, u in enumerate(units):
            if not u.strip(): continue
            o = text_mesh(bpy, f'{name}_{k}', u, size, mat, coll, extrude=extrude, bevel=bevel, align='LEFT', plane=plane, spacing=spacing)
            o.parent = self.root; o.location = (pos[k] - total / 2, 0, 0); set_vis(o, False); self.items.append((o, pos[k] - total / 2, u))
        self.width = total

    def show(self, n=None, pops=None, t=0.0, times=None, pop_s=0.35):
        """Show items whose time <= t (times = list per item); item pops: scale 0.7 -> 1.08 -> 1 over pop_s seconds."""
        for k, (o, x, u) in enumerate(self.items):
            tk = times[k] if times else 0.0
            if t < tk: o.hide_render = True; continue
            o.hide_render = False; a = clamp((t - tk) / pop_s)
            sc = 1.0 if a >= 1 else (0.55 + 0.6 * smoothstep3(a / 0.6) if a < 0.6 else 1.15 - 0.15 * smoothstep3((a - 0.6) / 0.4))
            o.scale = (sc, sc, sc)

def thorn_bush(bpy, coll, mat, seed=3, n=14, h=0.07):
    rs = np.random.RandomState(seed); root = pivot(bpy, 'thorn', coll)
    for k in range(n):
        a = rs.uniform(0, 2 * math.pi); lean = rs.uniform(0.25, 0.9); hh = h * rs.uniform(0.55, 1.0); L = []
        p0 = np.zeros(3); d = np.array([math.cos(a) * lean, math.sin(a) * lean, 1.0]); d /= np.linalg.norm(d)
        pts = [p0 + d * hh * t + np.array([rs.uniform(-1, 1) * 0.004 * t, rs.uniform(-1, 1) * 0.004 * t, 0]) for t in (0.0, 0.35, 0.7, 1.0)]
        o = tube(bpy, f'thorn_{k}', [tuple(p) for p in pts], [0.0017, 0.0013, 0.0009, 0.0003], mat, coll, n=10, ring=6, lateral=(0, 1, 0)); o.parent = root
        for q in range(2):
            t = rs.uniform(0.4, 0.8); b = pts[1] if q == 0 else pts[2]; a2 = a + rs.uniform(-1.2, 1.2)
            tp = b + np.array([math.cos(a2) * 0.014, math.sin(a2) * 0.014, 0.012])
            o2 = tube(bpy, f'thorn_{k}_{q}', [tuple(b), tuple((b + tp) / 2 + np.array([0, 0, 0.003])), tuple(tp)], [0.0010, 0.0007, 0.0002], mat, coll, n=8, ring=5, lateral=(0, 1, 0)); o2.parent = root
    return root

def stamp_mesh(bpy, name, mat_rim, mat_in, coll, a=0.0075, b=0.0135, shoe=True):
    """A footprint pressed into the sand: dark floor + raised rim, built to sit on the terrain (z = 0 at the surface)."""
    v, f = torus(1.0, 0.16, 20, 6, 0.6)
    V = [(x * a * 1.12, y * b * 1.1, z * 0.006 + 0.0003) for x, y, z in v]
    rim = mesh_obj(bpy, name + '_rim', V, f, mat_rim, coll, noise_amp=0.0002, noise_freq=140.0)
    fl = ellipsoid(bpy, name + '_in', (a * 0.95, b * 0.95, 0.0016), mat_in, coll, seg=18, rings=6); fl.location = (0, 0, 0.0000); fl.parent = rim
    # toe/heel notch: a second smaller lobe
    ball = ellipsoid(bpy, name + '_ball', (a * 0.9, b * 0.55, 0.0016), mat_in, coll, seg=14, rings=6); ball.parent = rim; ball.location = (0, b * 0.52, 0.0)
    return rim

def build_house(bpy, name, coll, mats, w=0.14, d=0.12, h=0.12, seed=1, door=True, windows=1, glow=None):
    """Rounded clay house with a flat roof, parapet, door recess and glowing windows."""
    root = pivot(bpy, name + '_root', coll)
    rings = []
    for z, r in ((0.0, 1.0), (0.01, 1.0), (h * 0.5, 0.995), (h - 0.004, 0.985), (h, 0.93)): rings.append((z, w * r, d * r))
    # superellipse rings
    seg = 40; V, F = [], []
    for (z, rx, ry) in rings:
        for j in range(seg):
            ph = 2 * math.pi * j / seg; c, s_ = math.cos(ph), math.sin(ph); e = 2.0 / 8.0
            V.append((rx * np.sign(c) * abs(c) ** e, ry * np.sign(s_) * abs(s_) ** e, z))
    n = len(rings)
    for k in range(n - 1):
        for j in range(seg): a = k * seg + j; b = k * seg + (j + 1) % seg; F.append((a, a + seg, b + seg, b))
    V.append((0, 0, rings[-1][0])); c1 = len(V) - 1; base = (n - 1) * seg; F += [(c1, base + j, base + (j + 1) % seg) for j in range(seg)]
    V.append((0, 0, 0)); c0 = len(V) - 1; F += [(c0, (j + 1) % seg, j) for j in range(seg)]
    mk(bpy, name + '_wall', V, F, mats['wall'], coll, root, noise_amp=0.0007, noise_freq=40.0, seed=seed)
    # parapet slab
    rg = [(h, w * 0.94, d * 0.94), (h + 0.008, w * 0.94, d * 0.94), (h + 0.008, w * 0.80, d * 0.80)]
    V2, F2 = [], []
    for (z, rx, ry) in rg:
        for j in range(seg):
            ph = 2 * math.pi * j / seg; c, s_ = math.cos(ph), math.sin(ph); e = 2.0 / 8.0; V2.append((rx * np.sign(c) * abs(c) ** e, ry * np.sign(s_) * abs(s_) ** e, z))
    for k in range(2):
        for j in range(seg): a = k * seg + j; b = k * seg + (j + 1) % seg; F2.append((a, a + seg, b + seg, b))
    mk(bpy, name + '_par', V2, F2, mats['wall2'], coll, root, noise_amp=0.0005, seed=seed + 1)
    # glowing windows and a door on the front (-Y) face
    items = []
    for k in range(windows):
        x = (k - (windows - 1) / 2) * w * 0.9 * (1 if windows > 1 else 0) + (0.045 if door and windows == 1 else 0.0)
        o = ellipsoid(bpy, f'{name}_win{k}', (0.0125, 0.0035, 0.017), mats['glowwin'], coll, seg=14, rings=8); o.parent = root; o.location = (x, -d * 0.985, h * 0.62); set_vis(o, False); items.append(o)
        fr = ellipsoid(bpy, f'{name}_winfr{k}', (0.0160, 0.0030, 0.0205), mats['wall2'], coll, seg=14, rings=8); fr.parent = root; fr.location = (x, -d * 0.975, h * 0.62)
    dr = None
    if door:
        dr = ellipsoid(bpy, name + '_door', (0.017, 0.004, 0.034), mats['glowdoor'], coll, seg=16, rings=10, shape=lambda x, y, z: (x, y, z if z > 0 else z * 0.9)); dr.parent = root; dr.location = (-0.03, -d * 0.985, 0.032); set_vis(dr, False)
        fd = ellipsoid(bpy, name + '_doorfr', (0.0205, 0.0030, 0.0375), mats['wall2'], coll, seg=16, rings=10); fd.parent = root; fd.location = (-0.03, -d * 0.975, 0.031)
    return root, dr


def stamp_data(bpy, name, a=0.0075, b=0.0135):
    """One mesh (2 material slots: rim, floor) for a footprint; objects share it."""
    v, f = torus(1.0, 0.16, 20, 6, 0.6)
    V = [(x * a * 1.12, y * b * 1.1, z * 0.006 + 0.0003) for x, y, z in v]; F = list(f); MI = [0] * len(F)
    for sc_, dy, zz in ((0.95, 0.0, 0.0), (0.9, b * 0.52, 0.0)):
        seg, rings = 16, 5; base = len(V)
        rx, ry = a * sc_, (b * 0.95 if dy == 0 else b * 0.55)
        for r in range(rings + 1):
            ph = (math.pi / 2) * r / rings
            for j in range(seg):
                th = 2 * math.pi * j / seg; V.append((rx * math.sin(ph) * math.cos(th), dy + ry * math.sin(ph) * math.sin(th), 0.0004 + 0.0012 * math.cos(ph) * 0.5))
        for r in range(rings):
            for j in range(seg):
                p0 = base + r * seg + j; p1 = base + r * seg + (j + 1) % seg; F.append((p0, p1, p1 + seg, p0 + seg)); MI.append(1)
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.polygons.foreach_set('material_index', MI)
    return me

class LampField:
    """~400 tiny clay lamps with emissive flames, joined into chunks so they can light up in waves."""
    def __init__(self, bpy, coll, mat_clay, mat_flame, positions_fn, groups, seed=11):
        rs = np.random.RandomState(seed); self.chunks = []
        dish_v, dish_f = [], []
        def build_chunk(pts, tag):
            Vd, Fd, Vf, Ff = [], [], [], []
            for (x, y, z) in pts:
                s = rs.uniform(0.85, 1.2); yaw = rs.uniform(0, 6.28)
                bd = len(Vd)
                for r in range(5):
                    ph = (math.pi / 2) * r / 4
                    for j in range(10):
                        th = 2 * math.pi * j / 10 + yaw; Vd.append((x + 0.0125 * s * math.sin(ph) * math.cos(th), y + 0.0125 * s * math.sin(ph) * math.sin(th), z + 0.0012 + 0.0052 * s * math.cos(ph)))
                for r in range(4):
                    for j in range(10): a = bd + r * 10 + j; b = bd + r * 10 + (j + 1) % 10; Fd.append((a + 10, b + 10, b, a))
                bf = len(Vf)
                for r in range(5):
                    t = r / 4; rad = 0.0032 * s * (1 - 0.75 * t) * (1 if r < 4 else 0.2); 
                    for j in range(6):
                        th = 2 * math.pi * j / 6; Vf.append((x + rad * math.cos(th), y + 0.0075 * s + rad * math.sin(th), z + 0.0072 + 0.0085 * s * (t ** 0.9)))
                for r in range(4):
                    for j in range(6): a = bf + r * 6 + j; b = bf + r * 6 + (j + 1) % 6; Ff.append((a, b, b + 6, a + 6))
            out = []
            for tg, V, F, m in (('d', Vd, Fd, mat_clay), ('f', Vf, Ff, mat_flame)):
                me = bpy.data.meshes.new(f'lf_{tag}_{tg}'); me.from_pydata(V, [], F); me.update(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.materials.append(m)
                o = bpy.data.objects.new(f'lf_{tag}_{tg}', me); coll.objects.link(o); o.hide_render = True
                if tg == 'f': set_vis(o, False)
                out.append(o)
            return out
        pts = positions_fn(sum(groups))
        k = 0; self.order = []
        for gi, g in enumerate(groups):
            n_chunks = max(1, int(round(g / 14.0))); sizes = [g // n_chunks + (1 if q < g % n_chunks else 0) for q in range(n_chunks)]
            ch = []
            for sz in sizes:
                ch.append(build_chunk(pts[k:k + sz], f'{gi}_{len(self.chunks)}')); self.chunks.append(ch[-1]); k += sz
            self.order.append(ch)
        self.groups = groups; self.pts = pts

    def show(self, t, starts, dt=0.0833):
        """Group g's chunks pop in one after another from starts[g] (dt apart)."""
        for g, ch in enumerate(self.order):
            for q, objs in enumerate(ch):
                vis = t >= starts[g] + q * dt
                for o in objs: o.hide_render = not vis

    def hide_all(self):
        for ch in self.order:
            for objs in ch:
                for o in objs: o.hide_render = True
