"""KINOFORGE Cutaway kit: a block of land cut out of the world (Blender bpy 5.2, Cycles, fully procedural, free).

A floating block: the top is a living landscape (terrain, grass, trees, rocks, flowers, water), the four sides are a clean
cross-section (strata, pebbles, roots), water is a clear glassy volume you can see into. Everything that moves is a pure
function of time t (seconds), driven by Kit.update(t), so any frame renders the same on any machine.

Quick start (inside a harness scene: DURATION, SETTINGS, build(bpy, ctx), frame(bpy, ctx, state, i, t)):

    import cutaway as cw
    kit  = cw.Kit(bpy, seed=3, loop=8.0)                       # loop: seconds after which every motion repeats exactly
    land = cw.block(kit, size=(4, 4), depth=1.4, strata=cw.STRATA['meadow'],
                    top=cw.rolling(amp=0.12), water=[cw.river([(-2.2, -0.4), (0, 0.2), (2.2, 0.9)], width=0.7)],
                    season='summer')
    cw.studio(kit, color=(0.93, 0.92, 0.90))                   # or cw.sky(kit), cw.dusk(kit)
    cam = cw.camera(kit, land, aspect='16:9', az=-38, el=31)   # or aspect='9:16'
    ...
    def frame(bpy, ctx, S, i, t): S['kit'].update(t); S['cam'].orbit(t, deg_per_s=2)

The full API, parameters and costs are in README.md next to this file. Coordinates: metres, block centred on the origin,
top surface near z = 0, bottom at z = -depth. The camera-facing "front" faces are -Y (left) and +X (right).
"""
import math
import zlib

import numpy as np

__all__ = ['Kit', 'block', 'river', 'pond', 'basin', 'rolling', 'STRATA', 'SEASONS', 'studio', 'sky', 'dusk', 'camera',
           'pile', 'pipe', 'house', 'mill', 'bridge', 'lamp', 'tunnel_mouth', 'birds', 'falling_stones', 'hanging_roots', 'render_settings']

# =============================================================================================== numeric helpers
def smooth(a, b, x):
    u = np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0); return u * u * (3 - 2 * u)

def _h2(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + (seed * 2654435761 & 0xffffffff)) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffffff) / float(0xffffff)

def vnoise(x, y, seed=0):
    """Smooth value noise in [-1, 1] (numpy, vectorised, deterministic)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    ix = np.floor(x).astype(np.int64); iy = np.floor(y).astype(np.int64); fx = x - ix; fy = y - iy
    u = fx * fx * (3 - 2 * fx); v = fy * fy * (3 - 2 * fy)
    a = _h2(ix, iy, seed); b = _h2(ix + 1, iy, seed); c = _h2(ix, iy + 1, seed); d = _h2(ix + 1, iy + 1, seed)
    return ((a + (b - a) * u) * (1 - v) + (c + (d - c) * u) * v) * 2 - 1

def fbm(x, y, seed=0, octaves=4, freq=1.0, gain=0.5):
    s = 0.0; a = 1.0; n = 0.0
    for o in range(octaves):
        s = s + a * vnoise(x * freq * 2 ** o + 17.1 * o, y * freq * 2 ** o - 9.3 * o, seed + o * 101); n += a; a *= gain
    return s / n

def rnd(seed, tag):
    return (zlib.crc32(f'{seed}|{tag}'.encode()) & 0xffffffff) / 4294967295.0

def catmull(points, n):
    P = np.asarray(points, float); m = len(P)
    if m < 2: return P
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]]); out = []
    for k in range(n):
        s = k / (n - 1) * (m - 1); i = min(int(s), m - 2); u = s - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out.append(0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    return np.array(out)

def srgb(c):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (f(c[0]), f(c[1]), f(c[2]), 1.0)

# =============================================================================================== palettes
# Strata: list of layers from the top down: (name, thickness m, sRGB colour, pebble density 0..1). The last layer fills the rest.
STRATA = {
    'meadow': [('topsoil', 0.07, (0.32, 0.21, 0.12), 0.05), ('sand', 0.13, (0.78, 0.62, 0.42), 0.10), ('pale', 0.04, (0.86, 0.74, 0.56), 0.02),
               ('clay', 0.17, (0.62, 0.52, 0.42), 0.03), ('loam', 0.24, (0.50, 0.32, 0.19), 0.25), ('ochre', 0.05, (0.66, 0.46, 0.26), 0.15),
               ('gravel', 0.14, (0.56, 0.46, 0.36), 0.85), ('deep', 1.0, (0.34, 0.24, 0.16), 0.30)],
    'red': [('topsoil', 0.06, (0.22, 0.14, 0.09), 0.05), ('ochre', 0.18, (0.66, 0.42, 0.26), 0.12), ('pale', 0.08, (0.80, 0.66, 0.50), 0.05),
            ('rust', 0.28, (0.52, 0.30, 0.19), 0.30), ('band', 0.06, (0.70, 0.52, 0.36), 0.10), ('deep', 1.0, (0.40, 0.25, 0.17), 0.25)],
    'limestone': [('topsoil', 0.05, (0.24, 0.17, 0.11), 0.05), ('chalk', 0.22, (0.86, 0.82, 0.72), 0.06), ('marl', 0.18, (0.66, 0.58, 0.46), 0.15),
                  ('clay', 0.22, (0.52, 0.40, 0.30), 0.20), ('rock', 1.0, (0.56, 0.52, 0.46), 0.50)],
    'lagoon': [('sand', 0.10, (0.84, 0.76, 0.60), 0.08), ('loam', 0.14, (0.55, 0.38, 0.25), 0.20), ('red', 0.28, (0.56, 0.34, 0.22), 0.30),
               ('band', 0.05, (0.72, 0.55, 0.40), 0.10), ('deep', 1.0, (0.42, 0.27, 0.18), 0.25)],
    'mud': [('topsoil', 0.05, (0.20, 0.15, 0.10), 0.02), ('silt', 0.20, (0.45, 0.40, 0.33), 0.02), ('mud', 0.35, (0.30, 0.26, 0.21), 0.05),
            ('clay', 0.25, (0.50, 0.47, 0.42), 0.02), ('sand', 1.0, (0.62, 0.55, 0.42), 0.20)],
}
# Seasons: sRGB colours for the living top. Pass season='autumn' or a dict to block() (any missing key falls back to summer).
SEASONS = {
    'summer': {'grass': (0.30, 0.56, 0.15), 'grass_tip': (0.66, 0.80, 0.30), 'grass_dry': (0.55, 0.55, 0.22), 'ground': (0.22, 0.32, 0.11),
               'leaf': [(0.20, 0.42, 0.13), (0.28, 0.50, 0.15), (0.16, 0.34, 0.12), (0.36, 0.52, 0.18)], 'flowers': 1.0, 'snow': 0.0, 'leaf_density': 1.0},
    'spring': {'grass': (0.38, 0.62, 0.20), 'grass_tip': (0.72, 0.82, 0.36), 'grass_dry': (0.50, 0.60, 0.24), 'ground': (0.26, 0.38, 0.13),
               'leaf': [(0.42, 0.66, 0.22), (0.55, 0.72, 0.28), (0.92, 0.72, 0.80), (0.36, 0.60, 0.20)], 'flowers': 1.6, 'snow': 0.0, 'leaf_density': 0.9},
    'autumn': {'grass': (0.42, 0.46, 0.18), 'grass_tip': (0.70, 0.62, 0.30), 'grass_dry': (0.62, 0.48, 0.22), 'ground': (0.30, 0.28, 0.13),
               'leaf': [(0.80, 0.40, 0.10), (0.86, 0.60, 0.16), (0.62, 0.22, 0.08), (0.52, 0.48, 0.16)], 'flowers': 0.2, 'snow': 0.0, 'leaf_density': 0.85},
    'winter': {'grass': (0.48, 0.48, 0.36), 'grass_tip': (0.70, 0.68, 0.56), 'grass_dry': (0.60, 0.56, 0.44), 'ground': (0.40, 0.38, 0.32),
               'leaf': [(0.22, 0.30, 0.20), (0.26, 0.34, 0.22), (0.20, 0.26, 0.18), (0.30, 0.36, 0.24)], 'flowers': 0.0, 'snow': 0.85, 'leaf_density': 0.35},
}

# =============================================================================================== node builder
def _sock(coll, key):
    if isinstance(key, int): return coll[key]
    for s in coll:
        if s.identifier == key and getattr(s, 'enabled', True): return s
    for s in coll:
        if s.name == key and getattr(s, 'enabled', True): return s
    for s in coll:
        if s.identifier == key or s.name == key: return s
    raise KeyError(key)

class G:
    """Tiny node-graph builder for shader and geometry node trees. Values or sockets (or nodes: first output) go in ins."""
    def __init__(self, tree, kit=None):
        self.t = tree; self.N = tree.nodes; self.L = tree.links; self.kit = kit; self._k = 0; self._phase = None
    def node(self, kind, ins=None, **attrs):
        n = self.N.new(kind); self._k += 1; n.location = ((self._k % 30) * 220, -(self._k // 30) * 400)
        for a, v in attrs.items(): setattr(n, a, v)
        for key, v in (ins or {}).items(): self.put(n, key, v)
        return n
    def put(self, n, key, v):
        s = _sock(n.inputs, key)
        if hasattr(v, 'outputs') and not hasattr(v, 'is_output'): v = v.outputs[0]
        if hasattr(v, 'is_output'): self.L.new(v, s); return
        dv = s.default_value
        if isinstance(v, (tuple, list)) and hasattr(dv, '__len__') and len(dv) == 4 and len(v) == 3: v = tuple(v) + (1.0,)
        s.default_value = v
    def link(self, a, b):
        if hasattr(a, 'outputs') and not hasattr(a, 'is_output'): a = a.outputs[0]
        self.L.new(a, b)
    def out(self, n, key=0): return _sock(n.outputs, key)
    def math(self, op, a, b=0.0, c=0.0, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.put(n, 0, a); self.put(n, 1, b); self.put(n, 2, c); return n.outputs[0]
    def vmath(self, op, a, b=(0, 0, 0), scale=None):
        n = self.node('ShaderNodeVectorMath', operation=op); self.put(n, 0, a); self.put(n, 1, b)
        if scale is not None: self.put(n, 'Scale', scale)
        return self.out(n, 'Value' if op in ('DOT_PRODUCT', 'LENGTH', 'DISTANCE') else 'Vector')
    def mix(self, fac, a, b, blend='MIX', dtype='RGBA', clamp=False):
        n = self.node('ShaderNodeMix', data_type=dtype, blend_type=blend, clamp_result=clamp)
        suf = {'RGBA': 'Color', 'FLOAT': 'Float', 'VECTOR': 'Vector'}[dtype]
        self.put(n, 'Factor_Float', fac); self.put(n, 'A_' + suf, a); self.put(n, 'B_' + suf, b)
        return self.out(n, 'Result_' + suf)
    def ramp(self, fac, stops, interp='LINEAR'):
        n = self.node('ShaderNodeValToRGB'); cr = n.color_ramp; cr.interpolation = interp
        while len(cr.elements) < len(stops): cr.elements.new(0.5)
        for el, (p, c) in zip(cr.elements, stops):
            el.position = p; el.color = srgb(c) if len(c) == 3 else c
        self.put(n, 'Fac', fac); return n.outputs['Color']
    def sep(self, v):
        n = self.node('ShaderNodeSeparateXYZ'); self.put(n, 0, v); return n.outputs
    def comb(self, x=0.0, y=0.0, z=0.0):
        n = self.node('ShaderNodeCombineXYZ'); self.put(n, 0, x); self.put(n, 1, y); self.put(n, 2, z); return n.outputs[0]
    def value(self, v=0.0, name=None):
        n = self.node('ShaderNodeValue'); n.outputs[0].default_value = v
        if name: n.label = name
        return n.outputs[0]
    def noise(self, vec, scale=1.0, detail=2.0, rough=0.5, dims='3D', w=None, distortion=0.0):
        n = self.node('ShaderNodeTexNoise', noise_dimensions=dims, ins={'Scale': scale, 'Detail': detail, 'Roughness': rough, 'Distortion': distortion})
        if vec is not None: self.put(n, 'Vector', vec)
        if w is not None: self.put(n, 'W', w)
        return n
    def voronoi(self, vec, scale=5.0, feature='F1', dims='3D', w=None, rand=1.0):
        n = self.node('ShaderNodeTexVoronoi', voronoi_dimensions=dims, feature=feature, ins={'Scale': scale, 'Randomness': rand})
        if vec is not None: self.put(n, 'Vector', vec)
        if w is not None: self.put(n, 'W', w)
        return n
    def attr(self, name, kind='GEOMETRY'):
        return self.node('ShaderNodeAttribute', attribute_name=name, attribute_type=kind)
    def phase(self, speed):
        """Looping time for noise: returns (z_offset, w) sockets that travel at `speed` noise-units per second around a circle
        that closes exactly after kit.loop seconds (so a loop render is seamless)."""
        if self._phase is None:
            c = self.value(1.0, 'kf_cos'); s = self.value(0.0, 'kf_sin'); self._phase = (c, s)
            if self.kit is not None: self.kit._register_phase(c, s)
        c, s = self._phase; R = speed * (self.kit.loop if self.kit else 60.0) / (2 * math.pi)
        return self.math('MULTIPLY', c, R), self.math('MULTIPLY', s, R)

# =============================================================================================== kit (time registry)
class Kit:
    """Owns the scene-wide registries: every time-driven socket, modifier input and per-frame callback.
    loop: seconds after which every motion repeats exactly (seamless loops); 0 means a long 240 s cycle (no visible repeat)."""
    def __init__(self, bpy, seed=1, loop=0.0):
        self.bpy = bpy; self.seed = seed; self.loop = float(loop) if loop else 240.0
        self._phases = []; self._gn = []; self._cb = []; self.t = 0.0
        self.coll = bpy.context.scene.collection
        self.protos = bpy.data.collections.new('cw_protos')   # instance prototypes: never linked to the scene
        self.mats = {}
    def _register_phase(self, c, s): self._phases.append((c, s))
    def on_frame(self, fn): self._cb.append(fn); return fn
    def update(self, t):
        """Pose everything for time t (seconds). Deterministic."""
        self.t = t; th = 2 * math.pi * (t / self.loop)
        c, s = math.cos(th), math.sin(th)
        for a, b in self._phases: a.default_value = c; b.default_value = s
        for ob, mod, ids in self._gn:
            gn_set(mod, ids[0], c); gn_set(mod, ids[1], s)
            ob.update_tag()
        for fn in self._cb: fn(t)
    def cycles(self, t, per_loop_hint):
        """Phase (radians) for a periodic motion that repeats an integer number of times per loop (keeps loops seamless)."""
        n = max(1, round(per_loop_hint * self.loop)); return 2 * math.pi * n * t / self.loop

# =============================================================================================== mesh helpers
def mk_mesh(bpy, name, verts, faces, mats=(), mat_idx=None, smooth_shade=True, coll=None, attrs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, v)) for v in verts], [], [tuple(int(i) for i in f) for f in faces])
    for m in mats: me.materials.append(m)
    if mat_idx is not None and len(faces): me.polygons.foreach_set('material_index', np.asarray(mat_idx, np.int32))
    if len(faces): me.polygons.foreach_set('use_smooth', np.full(len(faces), bool(smooth_shade)))
    for an, (kind, arr) in (attrs or {}).items():
        a = me.attributes.new(an, kind, 'POINT'); a.data.foreach_set('value', np.asarray(arr, np.float32 if kind == 'FLOAT' else np.int32))
    me.update()
    ob = bpy.data.objects.new(name, me)
    if coll is not None: coll.objects.link(ob)
    return ob

def _icosphere(sub=3):
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    V = np.array([v.co[:] for v in bm.verts]); F = [tuple(v.index for v in f.verts) for f in bm.faces]; bm.free(); return V, F

def _lumpy(V, seed, amp=0.18, freq=2.2, amp2=0.07, freq2=6.0):
    from mathutils import noise, Vector
    o = Vector((seed * 3.1, seed * 1.7, seed * 2.3)); out = []
    for v in V:
        p = Vector(v); r = 1 + amp * noise.noise(p * freq + o) + amp2 * noise.noise(p * freq2 + o * 2)
        out.append(np.asarray(v) * r)
    return np.array(out)

def _tube(pts, radii, ring=8, cap=True):
    """Swept tube through pts with radii; returns verts, faces."""
    C = np.asarray(pts, float); n = len(C); R = np.asarray(radii, float)
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
    up = np.array([0, 0, 1.0]); verts = []; faces = []
    for k in range(n):
        a = up if abs(T[k] @ up) < 0.95 else np.array([1.0, 0, 0])
        N = np.cross(a, T[k]); N /= np.linalg.norm(N); B = np.cross(T[k], N)
        for j in range(ring):
            ph = 2 * math.pi * j / ring; verts.append(C[k] + R[k] * (math.cos(ph) * N + math.sin(ph) * B))
    for k in range(n - 1):
        for j in range(ring):
            a = k * ring + j; b = k * ring + (j + 1) % ring; faces.append((a, b, b + ring, a + ring))
    if cap:
        verts.append(C[0]); c0 = len(verts) - 1; faces += [(c0, (j + 1) % ring, j) for j in range(ring)]
        verts.append(C[-1]); c1 = len(verts) - 1; base = (n - 1) * ring; faces += [(c1, base + j, base + (j + 1) % ring) for j in range(ring)]
    return verts, faces

class _Acc:
    """Accumulates parts (verts, faces, material index) into one mesh."""
    def __init__(self): self.V = []; self.F = []; self.M = []
    def add(self, V, F, m=0):
        o = len(self.V); self.V += [tuple(v) for v in V]; self.F += [tuple(i + o for i in f) for f in F]; self.M += [m] * len(F)
    def build(self, bpy, name, mats, smooth_shade=True, coll=None):
        return mk_mesh(bpy, name, self.V, self.F, mats, self.M, smooth_shade, coll)

# =============================================================================================== materials
def _new_mat(bpy, name):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    m.node_tree.nodes.clear(); return m

def _finish(g, shader, volume=None, displacement=None):
    o = g.node('ShaderNodeOutputMaterial', target='ALL'); g.link(shader, o.inputs['Surface'])
    if volume is not None: g.link(volume, o.inputs['Volume'])
    return o

def mat_simple(kit, name, color, rough=0.6, emission=None, strength=0.0, sss=0.0, metallic=0.0, noise_amt=0.0, bump=0.0):
    bpy = kit.bpy; m = _new_mat(bpy, name); g = G(m.node_tree, kit)
    col = color
    if noise_amt > 0:
        tc = g.node('ShaderNodeTexCoord'); n = g.noise(tc.outputs['Object'], 18.0, 3.0)
        c2 = tuple(x * (1 - noise_amt) for x in color)
        col = g.mix(n.outputs['Fac'], c2, tuple(min(1, x * (1 + noise_amt)) for x in color))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb(color) if col is color else col, 'Roughness': rough, 'Metallic': metallic})
    if sss: g.put(p, 'Subsurface Weight', sss)
    if emission is not None: g.put(p, 'Emission Color', srgb(emission)); g.put(p, 'Emission Strength', strength)
    if bump > 0:
        tc = g.node('ShaderNodeTexCoord'); n = g.noise(tc.outputs['Object'], 40.0, 4.0)
        b = g.node('ShaderNodeBump', ins={'Strength': bump, 'Height': n.outputs['Fac'], 'Distance': 0.01}); g.put(p, 'Normal', b)
    _finish(g, p); return m

def mat_glow(kit, name, color, strength):
    """Pure emission (windows, lamps)."""
    m = _new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': strength}); _finish(g, e); return m

def mat_varied(kit, name, colors, rough=0.7, translucent=0.0, bump=0.3, bump_scale=60.0, tip=None):
    """Per-instance colour variation (Object Info Random) for grass, leaves, flowers; optional root-to-tip gradient."""
    m = _new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    oi = g.node('ShaderNodeObjectInfo'); stops = [(i / max(1, len(colors) - 1), c) for i, c in enumerate(colors)]
    col = g.ramp(oi.outputs['Random'], stops)
    tc = g.node('ShaderNodeTexCoord')
    if tip is not None:
        z = g.sep(tc.outputs['Object'])[2]; f = g.math('MULTIPLY', z, tip[1], clamp=True)
        col = g.mix(g.math('POWER', f, 1.6), g.mix(0.55, col, (0.02, 0.05, 0.01), 'MULTIPLY'), g.mix(0.5, col, srgb(tip[0])))
    n = g.noise(tc.outputs['Object'], bump_scale, 3.0)
    col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.35), col, g.mix(0.6, col, (0, 0, 0), 'MULTIPLY'))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': rough})
    if bump: b = g.node('ShaderNodeBump', ins={'Strength': bump, 'Height': n.outputs['Fac'], 'Distance': 0.005}); g.put(p, 'Normal', b)
    sh = p
    if translucent:
        tr = g.node('ShaderNodeBsdfTranslucent', ins={'Color': col}); mx = g.node('ShaderNodeMixShader')
        g.put(mx, 0, translucent); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2]); sh = mx
    _finish(g, sh); return m

def mat_leaf(kit, name, colors, snow=0.0):
    """Leaf masses: per-instance colour, leafy voronoi breakup and bump, translucency, optional snow on top."""
    m = _new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    oi = g.node('ShaderNodeObjectInfo'); tc = g.node('ShaderNodeTexCoord')
    col = g.ramp(oi.outputs['Random'], [(i / max(1, len(colors) - 1), c) for i, c in enumerate(colors)])
    vo = g.voronoi(tc.outputs['Object'], 70.0, 'F1'); nn = g.noise(tc.outputs['Object'], 9.0, 3.0)
    shade = g.math('MULTIPLY_ADD', vo.outputs['Distance'], 0.9, 0.35)
    col = g.mix(g.math('SUBTRACT', 1.0, shade, clamp=True), col, g.mix(0.7, col, (0, 0, 0), 'MULTIPLY'))
    col = g.mix(g.math('MULTIPLY', nn.outputs['Fac'], 0.5), col, g.mix(0.4, col, srgb((0.9, 0.95, 0.5)), 'MIX'))
    geo = g.node('ShaderNodeNewGeometry')
    if snow > 0:
        nz = g.sep(geo.outputs['Normal'])[2]; sm = g.math('MULTIPLY', g.math('SUBTRACT', nz, 1 - snow, clamp=False), 4.0, clamp=True)
        col = g.mix(sm, col, (0.92, 0.94, 0.97))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.65})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.6, 'Height': vo.outputs['Distance'], 'Distance': 0.01}); g.put(p, 'Normal', b)
    tr = g.node('ShaderNodeBsdfTranslucent', ins={'Color': col}); mx = g.node('ShaderNodeMixShader')
    g.put(mx, 0, 0.22); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2]); _finish(g, mx); return m

def mat_rock(kit, name, color=(0.62, 0.60, 0.56), moss=0.0, moss_color=(0.28, 0.40, 0.14), snow=0.0, wet_below=None):
    m = _new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); oi = g.node('ShaderNodeObjectInfo'); geo = g.node('ShaderNodeNewGeometry')
    n1 = g.noise(tc.outputs['Object'], 6.0, 6.0, 0.6); n2 = g.noise(tc.outputs['Object'], 30.0, 4.0)
    base = g.mix(oi.outputs['Random'], srgb(tuple(c * 0.8 for c in color)), srgb(tuple(min(1, c * 1.12) for c in color)))
    col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], 0.8), g.mix(0.3, base, (0, 0, 0), 'MULTIPLY'), base)
    nz = g.sep(geo.outputs['Normal'])[2]
    if moss > 0:
        mm = g.math('MULTIPLY', g.math('ADD', g.math('SUBTRACT', nz, 0.55), g.math('MULTIPLY', n1.outputs['Fac'], 0.5)), 4.0 * moss, clamp=True)
        col = g.mix(mm, col, srgb(moss_color))
    if snow > 0:
        sm = g.math('MULTIPLY', g.math('SUBTRACT', nz, 1 - snow), 5.0, clamp=True); col = g.mix(sm, col, (0.92, 0.94, 0.97))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.8})
    h = g.math('ADD', n1.outputs['Fac'], g.math('MULTIPLY', n2.outputs['Fac'], 0.4))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.5, 'Height': h, 'Distance': 0.02}); g.put(p, 'Normal', b)
    _finish(g, p); return m

def _caustics(g, pos, level, depth_scale=0.5, strength=1.6):
    """Animated caustic web (two voronoi edge layers), fading with depth below `level`. Returns a 0..k scalar socket."""
    zoff, w = g.phase(0.25)
    sx = g.sep(pos); p2 = g.comb(sx[0], sx[1], zoff)
    v1 = g.voronoi(p2, 7.0, 'DISTANCE_TO_EDGE', '4D', w); v2 = g.voronoi(g.vmath('SCALE', p2, scale=1.37), 9.0, 'DISTANCE_TO_EDGE', '4D', g.math('MULTIPLY', w, 1.3))
    c1 = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', v1.outputs['Distance'], 9.0), clamp=True)
    c2 = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', v2.outputs['Distance'], 11.0), clamp=True)
    c = g.math('POWER', g.math('MAXIMUM', c1, c2), 2.0)
    d = g.math('SUBTRACT', level, sx[2])                       # depth below the surface
    under = g.math('MULTIPLY', d, 60.0, clamp=True)             # 0 at the surface line, 1 below 1.7 cm
    fade = g.math('EXPONENT', g.math('MULTIPLY', d, -1.0 / max(1e-3, depth_scale)))
    return g.math('MULTIPLY', g.math('MULTIPLY', c, g.math('MULTIPLY', under, fade)), strength)

def mat_top(kit, land):
    """The top surface: grass ground, dirt, sand, pale cracked rock, path; wet near water; caustics underwater; snow."""
    pal = land.pal; m = _new_mat(kit.bpy, 'cw_top'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; geo = g.node('ShaderNodeNewGeometry')
    A = {k: g.attr(k).outputs['Fac'] for k in ('w_grass', 'w_sand', 'w_rock', 'w_path')}
    n_big = g.noise(pos, 1.6, 3.0); n_fine = g.noise(pos, 45.0, 4.0); n_mid = g.noise(pos, 8.0, 4.0)
    dirt = g.mix(n_mid.outputs['Fac'], srgb((0.24, 0.17, 0.11)), srgb((0.38, 0.28, 0.18)))
    ground = g.mix(n_big.outputs['Fac'], srgb(pal['ground']), srgb(tuple(c * 0.75 for c in pal['grass'])))
    ground = g.mix(g.math('MULTIPLY', n_fine.outputs['Fac'], 0.6), ground, g.mix(0.6, ground, (0, 0, 0), 'MULTIPLY'))
    sand = g.mix(n_fine.outputs['Fac'], srgb((0.72, 0.64, 0.50)), srgb((0.84, 0.78, 0.64)))
    # pale cracked limestone: voronoi plates, dark crack lines, slight colour per plate
    vo = g.voronoi(pos, 6.0, 'DISTANCE_TO_EDGE'); vc = g.voronoi(pos, 6.0, 'F1')
    crack = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 22.0), clamp=True)
    vo2 = g.voronoi(pos, 19.0, 'DISTANCE_TO_EDGE'); crack2 = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo2.outputs['Distance'], 30.0), clamp=True)
    plate = g.mix(g.sep(vc.outputs['Color'])[0], srgb((0.74, 0.71, 0.64)), srgb((0.86, 0.84, 0.78)))
    plate = g.mix(g.math('MULTIPLY', n_mid.outputs['Fac'], 0.4), plate, srgb((0.62, 0.60, 0.55)))
    rock = g.mix(g.math('MAXIMUM', crack, g.math('MULTIPLY', crack2, 0.6)), plate, srgb((0.30, 0.28, 0.25)))
    col = g.mix(A['w_sand'], dirt, sand)
    col = g.mix(A['w_rock'], col, rock)
    col = g.mix(A['w_grass'], col, ground)
    col = g.mix(A['w_path'], col, srgb((0.52, 0.42, 0.30)))
    z = g.sep(pos)[2]; level = g.value(land.level if land.level is not None else -99.0, 'level')
    wet = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', level, 0.025), z), 40.0, clamp=True)
    band = g.math('MULTIPLY', wet, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', level, z), 25.0, clamp=True)))
    col = g.mix(g.math('MULTIPLY', band, 0.45), col, (0, 0, 0))
    if land.level is not None:
        under = g.math('MULTIPLY', g.math('SUBTRACT', level, z), 30.0, clamp=True)
        bed = g.mix(n_mid.outputs['Fac'], srgb(land.bed[0]), srgb(land.bed[1]))
        col = g.mix(g.math('MULTIPLY', under, 0.85), col, bed)
        ca = _caustics(g, pos, level, strength=land.caustics)
        col = g.mix(ca, col, g.mix(0.5, col, (1.0, 1.0, 0.95), 'SCREEN'))
        col = g.mix(g.math('MINIMUM', g.math('MULTIPLY', ca, 0.6), 1.0), col, g.mix(1.0, col, (1.6, 1.6, 1.5), 'MULTIPLY'))
    if pal.get('snow', 0) > 0:
        nz = g.sep(geo.outputs['Normal'])[2]
        sm = g.math('MULTIPLY', g.math('ADD', g.math('SUBTRACT', nz, 1 - pal['snow']), g.math('MULTIPLY', n_mid.outputs['Fac'], 0.3)), 6.0, clamp=True)
        sm = g.math('MULTIPLY', sm, g.math('SUBTRACT', 1.0, wet))
        col = g.mix(sm, col, (0.90, 0.92, 0.96))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.85})
    rough = g.math('SUBTRACT', 0.85, g.math('MULTIPLY', wet, 0.6)); g.put(p, 'Roughness', rough)
    h = g.math('ADD', g.math('MULTIPLY', n_fine.outputs['Fac'], 0.5), g.math('MULTIPLY', g.math('MULTIPLY', crack, A['w_rock']), -1.5))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.5, 'Height': h, 'Distance': 0.01}); g.put(p, 'Normal', b)
    _finish(g, p); return m

def mat_strata(kit, layers, seed=0, level=None):
    """Cross-section walls: soft colour bands along the 'sd' attribute (depth below the top, flattening with depth),
    wobbly band edges, grain, embedded pebbles (denser in gravel layers), hanging roots near the top."""
    m = _new_mat(kit.bpy, 'cw_strata'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    sd = g.attr('sd').outputs['Fac']; dtop = g.attr('dtop').outputs['Fac']
    hz = g.math('ADD', sx[0], sx[1])                                         # runs along the two front faces
    wob = g.noise(g.comb(hz, 0.0, g.math('MULTIPLY', sd, 0.2)), 2.2, 3.0)
    s = g.math('ADD', sd, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.07))
    total = sum(l[1] for l in layers[:-1]) + 0.6; stops = []; pstops = []; acc = 0.0; soft = 0.012
    for k, l in enumerate(layers):
        a = acc / total; b = min(1.0, (acc + l[1]) / total) if k < len(layers) - 1 else 1.0
        stops += [(min(1, a + soft / total) if k else 0.0, l[2]), (max(0.0, b - soft / total) if k < len(layers) - 1 else 1.0, tuple(c * 0.9 for c in l[2]))]
        pstops += [(a, (l[3],) * 3)]; acc += l[1]
    fac = g.math('DIVIDE', s, total)
    col = g.ramp(fac, stops); pden = g.sep(g.ramp(fac, pstops, 'CONSTANT'))[0]
    # grain and streaks
    n1 = g.noise(pos, 60.0, 5.0, 0.6); n2 = g.noise(g.comb(hz, g.math('MULTIPLY', sx[2], 6.0), 0.0), 3.0, 4.0)
    col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], 0.45), col, g.mix(0.55, col, (0, 0, 0), 'MULTIPLY'))
    col = g.mix(g.math('MULTIPLY', n2.outputs['Fac'], 0.25), col, g.mix(0.5, col, (1, 1, 1), 'SCREEN'))
    # pebbles
    vp = g.voronoi(pos, 34.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    radius = g.math('MULTIPLY', g.math('MULTIPLY', pden, 0.42), g.math('MULTIPLY_ADD', rr[0], 0.8, 0.4))
    peb = g.math('MULTIPLY', g.math('SUBTRACT', radius, vp.outputs['Distance']), 25.0, clamp=True)
    pcol = g.mix(rr[1], srgb((0.42, 0.40, 0.37)), srgb((0.78, 0.74, 0.66)))
    pcol = g.mix(g.math('MULTIPLY', rr[2], 0.5), pcol, srgb((0.62, 0.46, 0.32)))
    col = g.mix(peb, col, pcol)
    # roots near the top: thin wiggly vertical lines, random per lane, random length
    u = g.math('ADD', g.math('MULTIPLY', hz, 22.0), g.math('MULTIPLY', g.noise(g.comb(hz, sx[2], 0.0), 6.0, 2.0).outputs['Fac'], 3.0))
    lane = g.math('FLOOR', u); fr = g.math('FRACT', u)
    wn = g.node('ShaderNodeTexWhiteNoise', noise_dimensions='1D'); g.put(wn, 'W', lane)
    rlen = g.math('MULTIPLY', wn.outputs['Value'], 0.30)
    line = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', fr, 0.5)), 16.0), clamp=True)
    taper = g.math('MULTIPLY', g.math('SUBTRACT', rlen, dtop), 20.0, clamp=True)
    keep = g.math('GREATER_THAN', wn.outputs['Value'], 0.35)
    root = g.math('MULTIPLY', g.math('MULTIPLY', line, taper), keep)
    col = g.mix(g.math('MULTIPLY', root, 0.85), col, srgb((0.12, 0.08, 0.05)))
    if level is not None:   # saturated ground below the water table: darker, slightly cooler, soft upper edge
        wt = g.math('MULTIPLY', g.math('SUBTRACT', level - 0.04, g.math('ADD', sx[2], g.math('MULTIPLY', wob.outputs['Fac'], 0.06))), 8.0, clamp=True)
        col = g.mix(g.math('MULTIPLY', wt, 0.38), col, g.mix(1.0, col, srgb((0.55, 0.58, 0.62)), 'MULTIPLY'))
    top_dark = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', dtop, 30.0), clamp=True)
    col = g.mix(g.math('MULTIPLY', top_dark, 0.35), col, srgb((0.16, 0.11, 0.07)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.92})
    h = g.math('ADD', g.math('MULTIPLY', n1.outputs['Fac'], 0.3), g.math('ADD', g.math('MULTIPLY', peb, 0.8), g.math('MULTIPLY', root, 0.4)))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.45, 'Height': h, 'Distance': 0.006}); g.put(p, 'Normal', b)
    _finish(g, p); return m

def mat_water(kit, name='cw_water', tint=(0.24, 0.82, 0.78), density=2.2, ripple=1.0, ice=0.0, level=None, glow_amt=0.06):
    """Clear water: glass IOR 1.33 (transparent for shadow rays so the bed stays lit), turquoise absorption with depth,
    animated ripple normals on the top only (the cut faces stay flat glass). ice > 0 frosts and whitens it."""
    m = _new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry'); pos = tc.outputs['Object']
    zoff, w = g.phase(0.45); sx = g.sep(pos)
    p = g.comb(g.math('MULTIPLY', sx[0], 1.0), sx[1], zoff)
    r1 = g.noise(p, 9.0, 3.0, 0.55, '4D', w); r2 = g.noise(g.vmath('SCALE', p, scale=2.7), 9.0, 2.0, 0.5, '4D', g.math('MULTIPLY', w, 1.6))
    h = g.math('ADD', r1.outputs['Fac'], g.math('MULTIPLY', r2.outputs['Fac'], 0.45))
    topmask = g.math('GREATER_THAN', g.sep(geo.outputs['Normal'])[2], 0.7)
    bump = g.node('ShaderNodeBump', ins={'Strength': g.math('MULTIPLY', topmask, 0.18 * ripple), 'Height': h, 'Distance': 0.02})
    glass = g.node('ShaderNodeBsdfGlass', ins={'Color': (1, 1, 1), 'Roughness': 0.015 + 0.25 * ice, 'IOR': 1.33}, distribution='GGX')
    g.put(glass, 'Normal', bump)
    tr = g.node('ShaderNodeBsdfTransparent'); lp = g.node('ShaderNodeLightPath')
    mx = g.node('ShaderNodeMixShader'); g.link(lp.outputs['Is Shadow Ray'], mx.inputs[0]); g.link(glass, mx.inputs[1]); g.link(tr, mx.inputs[2])
    surf = mx
    if ice > 0:
        wd = g.node('ShaderNodeBsdfDiffuse', ins={'Color': (0.85, 0.92, 0.98)}); m2 = g.node('ShaderNodeMixShader')
        g.put(m2, 0, ice * 0.5); g.link(mx, m2.inputs[1]); g.link(wd, m2.inputs[2]); surf = m2
    if level is not None:
        # fake in-scatter: a faint turquoise glow so the water reads bright and clear, not smoky; a thin bright meniscus
        # line where the surface meets the cut face
        side = g.math('LESS_THAN', g.sep(geo.outputs['Normal'])[2], 0.5)
        glow = g.node('ShaderNodeEmission', ins={'Color': srgb(tuple(min(1, c * 1.15 + 0.08) for c in tint)), 'Strength': glow_amt})
        ad = g.node('ShaderNodeAddShader'); g.link(surf, ad.inputs[0]); g.link(glow, ad.inputs[1]); surf = ad
        men = g.math('MULTIPLY', side, g.math('MULTIPLY', g.math('SUBTRACT', sx[2], level - 0.005), 200.0, clamp=True))
        wl = g.node('ShaderNodeEmission', ins={'Color': (1.0, 1.0, 1.0), 'Strength': 1.6}); m3 = g.node('ShaderNodeMixShader')
        g.link(men, m3.inputs[0]); g.link(surf, m3.inputs[1]); g.link(wl, m3.inputs[2]); surf = m3
    vol = g.node('ShaderNodeVolumeAbsorption', ins={'Color': srgb(tint), 'Density': density})
    _finish(g, surf, vol); return m

def mat_gradient_bg(kit, top, bottom, strength=1.0, light=None, light_strength=1.0):
    """World: what the camera sees is a vertical gradient (top -> bottom colours); what lights the scene is `light`."""
    bpy = kit.bpy; wd = bpy.data.worlds.new('cw_world'); bpy.context.scene.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree; nt.nodes.clear(); g = G(nt, kit)
    tc = g.node('ShaderNodeTexCoord'); z = g.sep(tc.outputs['Generated'])
    d = g.vmath('NORMALIZE', tc.outputs['Window'])
    fac = g.math('ADD', g.math('MULTIPLY', g.sep(tc.outputs['Window'])[1], 1.0), 0.0)
    col = g.ramp(fac, [(0.0, bottom), (1.0, top)])
    bg_cam = g.node('ShaderNodeBackground', ins={'Color': col, 'Strength': strength})
    bg_light = g.node('ShaderNodeBackground', ins={'Color': srgb(light or top), 'Strength': light_strength})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bg_light, mx.inputs[1]); g.link(bg_cam, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface']); return wd

# =============================================================================================== water regions
def river(path, width=0.6, depth=0.32, level=-0.06, shelf=0.25, kind='river'):
    """A river along a polyline of (x, y) points (extend it past the block edges so it is cut open on the faces)."""
    return {'type': 'river', 'path': path, 'width': width, 'depth': depth, 'level': level, 'shelf': shelf, 'kind': kind}

def pond(center, radius, depth=0.35, level=-0.05, shelf=0.3, kind='pond', wobble=0.15):
    """An oval pond. Put it against an edge (centre near or past the edge) for a glass front."""
    r = radius if isinstance(radius, (tuple, list)) else (radius, radius)
    return {'type': 'pond', 'center': center, 'radius': r, 'depth': depth, 'level': level, 'shelf': shelf, 'kind': kind, 'wobble': wobble}

def basin(fn, depth=0.4, level=-0.04, shelf=0.4, kind='lagoon'):
    """Any shape: fn(x, y) -> signed distance in metres (negative inside the water)."""
    return {'type': 'basin', 'fn': fn, 'depth': depth, 'level': level, 'shelf': shelf, 'kind': kind}

def _sdist(w, x, y, seed):
    if w['type'] == 'river':
        P = catmull(w['path'], max(24, 12 * len(w['path']))); d = np.full(np.shape(x), 1e9)
        for a, b in zip(P[:-1], P[1:]):
            ab = b - a; L2 = ab @ ab + 1e-12
            t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / L2, 0, 1)
            d = np.minimum(d, np.hypot(x - a[0] - t * ab[0], y - a[1] - t * ab[1]))
        wob = 0.06 * w['width'] * fbm(x, y, seed + 11, 3, 2.0)
        return d - w['width'] / 2 + wob
    if w['type'] == 'pond':
        cx, cy = w['center']; rx, ry = w['radius']
        q = np.hypot((x - cx) / rx, (y - cy) / ry); ang = np.arctan2(y - cy, x - cx)
        wob = w.get('wobble', 0.15) * (0.6 * np.sin(3 * ang + seed) + 0.4 * np.sin(5 * ang + 2 * seed)) * 0.25
        return (q - 1 + wob) * min(rx, ry)
    return w['fn'](x, y)

def rolling(amp=0.1, freq=0.35, seed=0, tilt=(0.0, 0.0), base=0.0):
    """A gently rolling top: returns a height function h(x, y) for block(top=...)."""
    def f(x, y): return base + amp * fbm(x, y, seed + 5, 4, freq) + tilt[0] * x + tilt[1] * y
    return f

# =============================================================================================== the block
class Land:
    """What block() returns. Fields: size, depth, level (main water level or None), height(x, y), field(x, y),
    objects (dict), pal (season palette), mats (dict). Methods: scatter(...), cut(obj), place(obj, x, y)."""
    pass

def block(kit, size=(4.0, 4.0), depth=1.4, strata=None, top=None, water=None, seed=1, season='summer', zones=None,
          res=0.022, grass=1.0, grass_height=1.0, trees=10, tree_kinds=('round', 'round', 'cone', 'tall'), tree_scale=1.0, boulders=12,
          flowers=0.5, under=True, lilies=0, reeds=0.0, corals=0, shore_rock=0.0, keep_clear=(), tree_spots=None,
          sway=1.0, water_tint=(0.24, 0.82, 0.78), water_density=2.6, water_glow=0.022, bed=((0.86, 0.80, 0.64), (0.66, 0.62, 0.50)), caustics=1.6, bottom=None, name='cw_block'):
    """Build the block. Returns a Land.
    size (sx, sy) m; depth m; strata = list of layers (see STRATA); top = h(x, y) function or 2D array (rows y, cols x);
    water = list of river()/pond()/basin() regions (they share the first region's level for the water volume);
    season = name in SEASONS or dict; zones(x, y, h) -> dict of extra weights {'rock','sand','path','grass'} (arrays);
    grass density multiplier; trees count (or tree_spots=[(x, y, scale, kind)]); boulders count; flowers 0..1;
    under = underwater plants and stones; lilies count; reeds 0..1 density along banks; corals count (lagoon);
    shore_rock 0..1 = pale cracked rock shelf around the water; keep_clear = [(x, y, r)] no vegetation there."""
    bpy = kit.bpy; rng = np.random.default_rng(seed)
    sx, sy = (size, size) if np.isscalar(size) else size
    strata = strata or STRATA['meadow']; water = list(water or [])
    pal = dict(SEASONS['summer']); pal.update(SEASONS.get(season, {}) if isinstance(season, str) else season)
    level = water[0]['level'] if water else None
    L = Land(); L.kit = kit; L.size = (sx, sy); L.depth = depth; L.level = level; L.pal = pal; L.seed = seed; L.objects = {}; L.mats = {}
    L.water = water; L.keep_clear = list(keep_clear); L.bed = bed; L.caustics = caustics

    if top is None: top = rolling(0.08, 0.35, seed)
    if not callable(top):
        arr = np.asarray(top, float)
        def top(x, y, arr=arr):
            u = (np.asarray(x) / sx + 0.5) * (arr.shape[1] - 1); v = (np.asarray(y) / sy + 0.5) * (arr.shape[0] - 1)
            i = np.clip(np.floor(u).astype(int), 0, arr.shape[1] - 2); j = np.clip(np.floor(v).astype(int), 0, arr.shape[0] - 2)
            fu = np.clip(u - i, 0, 1); fv = np.clip(v - j, 0, 1)
            return (arr[j, i] * (1 - fu) + arr[j, i + 1] * fu) * (1 - fv) + (arr[j + 1, i] * (1 - fu) + arr[j + 1, i + 1] * fu) * fv

    def field(x, y):
        """All the per-point data: h, sd (min signed distance to water), w_grass, w_sand, w_rock, w_path, depth (below level)."""
        x = np.asarray(x, float); y = np.asarray(y, float); h = top(x, y) + 0.004 * fbm(x, y, seed + 3, 3, 25.0)
        sdmin = np.full(x.shape, 1e9)
        for k, w in enumerate(water):
            sd = _sdist(w, x, y, seed + k); sdmin = np.minimum(sdmin, sd)
            lv, D, sh = w['level'], w['depth'], w['shelf']
            bed = lv - 0.02 - D * smooth(0, sh, -sd) * (0.85 + 0.15 * fbm(x, y, seed + 21, 3, 3.0))
            bank = lv + 0.012 + 0.55 * np.maximum(sd, 0) ** 1.0
            target = np.where(sd < 0, bed, bank)
            k2 = 0.03; hmin = np.minimum(h, target); hh = h - target
            h = np.where(np.abs(hh) < k2, hmin - (k2 - np.abs(hh)) ** 2 / (4 * k2), hmin)
        F = {'h': h, 'sd': sdmin}
        lv = level if level is not None else -99
        F['depth'] = lv - h
        near = smooth(0.10, 0.0, sdmin) if water else np.zeros_like(h)
        rockw = np.zeros_like(h)
        if shore_rock > 0 and water:
            edge = 0.06 + 0.5 * shore_rock + 0.14 * shore_rock * fbm(x, y, seed + 31, 3, 1.5)
            rockw = smooth(edge, edge - 0.05, sdmin) * smooth(-0.25, -0.02, sdmin)
        sand = np.clip(near * (1 - rockw), 0, 1); sand = np.where(F['depth'] > 0, 1.0, sand)
        dryp = 0.5 + 0.5 * fbm(x, y, seed + 41, 3, 1.3)
        grassw = np.clip(1 - sand - rockw, 0, 1) * smooth(0.12, 0.3, dryp + 0.25)
        F.update(w_grass=grassw, w_sand=sand, w_rock=rockw, w_path=np.zeros_like(h))
        if zones:
            Z = zones(x, y, h)
            for k in ('rock', 'sand', 'path', 'grass'):
                if k in Z:
                    v = np.clip(np.asarray(Z[k], float), 0, 1)
                    if k == 'grass': v = v * (1 - F['w_rock']) * (1 - np.clip(F['w_sand'], 0, 1))
                    F['w_' + k] = np.maximum(F['w_' + k], v)
                    if k != 'grass': F['w_grass'] = F['w_grass'] * (1 - v)
        for (cx, cy, r) in L.keep_clear:
            F['w_grass'] = F['w_grass'] * smooth(r * 0.7, r, np.hypot(x - cx, y - cy))
        return F
    L.field = field; L.height = lambda x, y: field(x, y)['h']

    # ---------------------------------------------------------------- mesh: top grid + walls + bottom
    nx = int(round(sx / res)) + 1; ny = int(round(sy / res)) + 1
    xs = np.linspace(-sx / 2, sx / 2, nx); ys = np.linspace(-sy / 2, sy / 2, ny)
    X, Y = np.meshgrid(xs, ys); F = field(X, Y); Hm = F['h']
    V = np.stack([X.ravel(), Y.ravel(), Hm.ravel()], 1)
    ii = np.arange(nx * ny).reshape(ny, nx)
    Ft = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
    attrs = {k: ('FLOAT', F[k].ravel()) for k in ('w_grass', 'w_sand', 'w_rock', 'w_path')}
    mats = {'top': mat_top(kit, L), 'strata': mat_strata(kit, strata, seed, level), 'bottom': mat_simple(kit, 'cw_bottom', (0.16, 0.12, 0.09), 0.95)}
    L.mats.update(mats)
    top_ob = mk_mesh(bpy, name + '_top', V, Ft, [mats['top']], None, True, kit.coll, attrs)
    # boundary ring CCW seen from above: -Y edge (x up), +X edge (y up), +Y edge (x down), -X edge (y down)
    ring = [(i, 0) for i in range(nx)] + [(nx - 1, j) for j in range(1, ny)] + [(i, ny - 1) for i in range(nx - 2, -1, -1)] + [(0, j) for j in range(ny - 2, 0, -1)]
    zb = -depth; zmean = float(np.mean(Hm)); rows = max(8, int(depth / 0.06))
    WV = []; sdv = []; dtv = []
    for (i, j) in ring:
        x, y, zt = xs[i], ys[j], Hm[j, i]
        for r in range(rows + 1):
            u = r / rows; uu = u ** 1.6 if True else u
            z = zt + (zb - zt) * uu
            WV.append((x, y, z)); dt = zt - z; dtv.append(dt)
            w = max(0.0, 1 - dt / 0.7); sdv.append(dt * w + (zmean - z) * (1 - w))
    nr = len(ring); WF = []
    for k in range(nr):
        k2 = (k + 1) % nr
        for r in range(rows):
            a = k * (rows + 1) + r; b = k2 * (rows + 1) + r
            WF.append((a, a + 1, b + 1, b))          # outward normal for a CCW ring
    bot = [k * (rows + 1) + rows for k in range(nr)][::-1]; WF.append(tuple(bot))
    wall_ob = mk_mesh(bpy, name + '_walls', WV, WF, [mats['strata'], mats['bottom']], [0] * (len(WF) - 1) + [1], False, kit.coll,
                      {'sd': ('FLOAT', sdv), 'dtop': ('FLOAT', dtv)})
    L.objects['top'] = top_ob; L.objects['walls'] = wall_ob

    # ---------------------------------------------------------------- water volume (one box per block, at the first level)
    if water:
        e = 0.0015; zb2 = float(np.min(Hm)) - 0.05; lv = level
        bx = [(-sx / 2 + e, -sy / 2 + e), (sx / 2 - e, -sy / 2 + e), (sx / 2 - e, sy / 2 - e), (-sx / 2 + e, sy / 2 - e)]
        WVv = [(x, y, zb2) for x, y in bx] + [(x, y, lv) for x, y in bx]
        WFf = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        ice = 0.6 if pal.get('snow', 0) > 0.5 else 0.0
        mats['water'] = mat_water(kit, tint=water_tint, density=water_density, ice=ice, level=level, glow_amt=water_glow)
        L.objects['water'] = mk_mesh(bpy, name + '_water', WVv, WFf, [mats['water']], None, False, kit.coll)

    # ---------------------------------------------------------------- life
    L.scatter = lambda *a, **k: scatter(kit, L, *a, **k)
    _populate(kit, L, rng, grass=grass, grass_height=grass_height, trees=trees, tree_kinds=tree_kinds, tree_scale=tree_scale, boulders=boulders, flowers=flowers,
              under=under, lilies=lilies, reeds=reeds, corals=corals, tree_spots=tree_spots, sway=sway)
    L.cut = lambda ob, margin=0.0: cut(kit, L, ob, margin)
    L.place = lambda ob, x, y, dz=0.0: _place(L, ob, x, y, dz)
    return L

def _place(L, ob, x, y, dz=0.0):
    ob.location = (x, y, float(L.height(np.array([x]), np.array([y]))[0]) + dz); return ob

def cut(kit, L, ob, margin=0.0):
    """Clip an object to the block's footprint (boolean intersect with the block box) so it ends flush on the cut faces:
    piles, pipes, foundations, tunnels then show their own cross-section on the wall."""
    bpy = kit.bpy; sx, sy = L.size
    if 'clipbox' not in L.objects:
        e = 0.0008 - margin; x0, x1, y0, y1 = -sx / 2 + e, sx / 2 - e, -sy / 2 + e, sy / 2 - e; z0, z1 = -L.depth - 1, 10
        V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        Fb = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        cb = mk_mesh(bpy, 'cw_clipbox', V, Fb, (), None, False, None); L.objects['clipbox'] = cb
    md = ob.modifiers.new('cw_cut', 'BOOLEAN'); md.operation = 'INTERSECT'; md.object = L.objects['clipbox']; md.solver = 'EXACT'
    return ob

# =============================================================================================== instancing (wind-driven)
def _sway_tree(kit):
    """Geometry nodes: instance prototypes on the vertices of a point mesh (attributes variant, yaw, scale, sway),
    with wind: looping 4D noise tilt plus a travelling gust. Inputs Collection, Cos, Sin (driven by Kit.update)."""
    bpy = kit.bpy
    if 'cw_sway' in bpy.data.node_groups: return bpy.data.node_groups['cw_sway']
    ng = bpy.data.node_groups.new('cw_sway', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Collection', in_out='INPUT', socket_type='NodeSocketCollection')
    ng.interface.new_socket('Cos', in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket('Sin', in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket('Speed', in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket('Loop', in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    g = G(ng, kit); gi = g.node('NodeGroupInput'); go = g.node('NodeGroupOutput')
    ci = g.node('GeometryNodeCollectionInfo', ins={'Separate Children': True, 'Reset Children': True}); g.link(gi.outputs['Collection'], _sock(ci.inputs, 'Collection'))
    na = lambda n, t: g.node('GeometryNodeInputNamedAttribute', data_type=t, ins={'Name': n}).outputs['Attribute']
    var = na('variant', 'INT'); yaw = na('yaw', 'FLOAT'); scl = na('scale', 'FLOAT'); amp = na('sway', 'FLOAT')
    pos = g.node('GeometryNodeInputPosition').outputs[0]
    R = g.math('DIVIDE', g.math('MULTIPLY', gi.outputs['Speed'], gi.outputs['Loop']), 2 * math.pi)
    zo = g.math('MULTIPLY', gi.outputs['Cos'], R); w = g.math('MULTIPLY', gi.outputs['Sin'], R)
    ps = g.sep(pos); p4 = g.comb(g.math('MULTIPLY', ps[0], 1.3), g.math('MULTIPLY', ps[1], 1.3), zo)
    nz = g.noise(p4, 1.0, 1.0, 0.5, '4D', w)
    c = g.vmath('SUBTRACT', nz.outputs['Color'], (0.5, 0.5, 0.5))
    # gust: a slow band travelling along the wind; seamless because it uses the same circle
    gz = g.noise(g.comb(g.math('MULTIPLY', ps[0], 0.35), g.math('MULTIPLY', ps[1], 0.35), g.math('MULTIPLY', zo, 0.5)), 1.0, 0.0, 0.5, '4D', g.math('MULTIPLY', w, 0.5))
    gust = g.math('MULTIPLY_ADD', gz.outputs['Fac'], 1.4, -0.2)
    a = g.math('MULTIPLY', amp, gust)
    cs = g.sep(c)
    tx = g.math('MULTIPLY', g.math('ADD', g.math('MULTIPLY', cs[0], 2.0), 0.35), a)    # steady lean + flutter
    ty = g.math('MULTIPLY', g.math('MULTIPLY', cs[1], 2.0), a)
    vr = g.node('ShaderNodeVectorRotate', rotation_type='Z_AXIS'); g.put(vr, 'Vector', g.comb(tx, ty, 0.0)); g.put(vr, 'Angle', g.math('MULTIPLY', yaw, -1.0))
    lv = g.sep(vr.outputs['Vector'])
    eul = g.node('FunctionNodeEulerToRotation'); g.put(eul, 'Euler', g.comb(lv[0], lv[1], yaw))
    iop = g.node('GeometryNodeInstanceOnPoints', ins={'Pick Instance': True})
    g.link(gi.outputs[0], _sock(iop.inputs, 'Points')); g.link(ci.outputs[0], _sock(iop.inputs, 'Instance'))
    g.put(iop, 'Instance Index', var); g.put(iop, 'Rotation', eul.outputs[0]); g.put(iop, 'Scale', scl)
    g.link(iop.outputs[0], go.inputs[0]); return ng

def scatter(kit, L, name, protos, pts, yaw=None, scale=None, sway=0.0, variant=None, speed=0.6, z=None, sink=0.004):
    """Instance prototype objects (a list, or a bpy collection) on points pts (N x 2 or N x 3) with per-point yaw,
    scale, sway amplitude (radians) and variant index. z defaults to the terrain height. Wind is driven by Kit.update."""
    bpy = kit.bpy; pts = np.asarray(pts, float)
    if len(pts) == 0: return None
    n = len(pts); rng = np.random.default_rng(zlib.crc32(name.encode()))
    if pts.shape[1] == 2:
        zz = L.height(pts[:, 0], pts[:, 1]) - sink if z is None else np.full(n, z)
        pts = np.column_stack([pts, zz])
    if hasattr(protos, 'objects'): coll = protos; k = len(protos.objects)
    else:
        coll = bpy.data.collections.new(name + '_protos')
        for ob in protos: coll.objects.link(ob)
        k = len(protos)
    yaw = rng.uniform(0, 2 * math.pi, n) if yaw is None else np.broadcast_to(yaw, (n,))
    scale = rng.uniform(0.8, 1.2, n) if scale is None else np.broadcast_to(scale, (n,))
    variant = rng.integers(0, k, n) if variant is None else np.broadcast_to(variant, (n,))
    sw = np.broadcast_to(sway, (n,)).astype(float)
    ob = mk_mesh(bpy, name, pts, [], (), None, True, kit.coll,
                 {'yaw': ('FLOAT', yaw), 'scale': ('FLOAT', scale), 'sway': ('FLOAT', sw), 'variant': ('INT', variant)})
    md = ob.modifiers.new('cw_sway', 'NODES'); md.node_group = _sway_tree(kit)
    ids = {it.name: it.identifier for it in md.node_group.interface.items_tree if getattr(it, 'in_out', '') == 'INPUT'}
    for k, v in (('Collection', coll), ('Speed', float(speed)), ('Loop', float(kit.loop)), ('Cos', 1.0), ('Sin', 0.0)): gn_set(md, ids[k], v)
    kit._gn.append((ob, md, (ids['Cos'], ids['Sin'])))
    L.objects[name] = ob; return ob

def gn_set(md, ident, v):
    """Set a geometry-nodes modifier input (Blender 5.x: md.properties.inputs.<id>.value; older: md[id])."""
    try: getattr(md.properties.inputs, ident).value = v
    except AttributeError: md[ident] = v

def _jitter_grid(rng, sx, sy, step, margin=0.0):
    xs = np.arange(-sx / 2 + margin + step / 2, sx / 2 - margin, step); ys = np.arange(-sy / 2 + margin + step / 2, sy / 2 - margin, step)
    X, Y = np.meshgrid(xs, ys); P = np.column_stack([X.ravel(), Y.ravel()])
    return P + rng.uniform(-0.5, 0.5, P.shape) * step

def _darts(rng, sx, sy, n, rmin, ok, margin, tries=4000):
    out = []
    for _ in range(tries):
        if len(out) >= n: break
        p = np.array([rng.uniform(-sx / 2 + margin, sx / 2 - margin), rng.uniform(-sy / 2 + margin, sy / 2 - margin)])
        if not ok(p): continue
        if all(np.hypot(*(p - q)) >= rmin for q in out): out.append(p)
    return np.array(out).reshape(-1, 2)

# =============================================================================================== prototypes
def proto_tufts(kit, pal, n=6, height=0.05, seed=0, blades=(9, 15)):
    bpy = kit.bpy; rng = np.random.default_rng(seed + 7); obs = []
    mat = mat_varied(kit, 'cw_grass', [pal['grass'], pal['grass_tip'], pal['grass'], pal['grass_dry'], tuple(c * 0.8 for c in pal['grass'])],
                     rough=0.6, translucent=0.3, bump=0.0, tip=(pal['grass_tip'], 1.0 / height))
    for k in range(n):
        A = _Acc(); nb = rng.integers(*blades)
        for b in range(nb):
            r = rng.uniform(0, 0.012); a = rng.uniform(0, 2 * math.pi); bx, by = r * math.cos(a), r * math.sin(a)
            phi = a + rng.uniform(-0.6, 0.6); lean = rng.uniform(0.15, 0.7); h = height * rng.uniform(0.55, 1.15); wdt = rng.uniform(0.0025, 0.0045)
            dx, dy = math.cos(phi), math.sin(phi); px, py = -dy, dx; segs = 4; Vb = []
            for s in range(segs + 1):
                u = s / segs; off = lean * h * u * u; zz = h * u * (1 - 0.25 * lean * u)
                cx, cy = bx + dx * off, by + dy * off; ww = wdt * (1 - u) ** 0.8
                if s < segs: Vb += [(cx - px * ww, cy - py * ww, zz), (cx + px * ww, cy + py * ww, zz)]
                else: Vb += [(cx, cy, zz)]
            Fb = [(2 * s, 2 * s + 1, 2 * s + 3, 2 * s + 2) for s in range(segs - 1)] + [(2 * (segs - 1), 2 * (segs - 1) + 1, 2 * segs)]
            A.add(Vb, Fb)
        obs.append(A.build(bpy, f'cw_tuft{k}', [mat], True, None))
    return obs

def proto_flowers(kit, n=4, seed=0):
    bpy = kit.bpy; rng = np.random.default_rng(seed + 9); obs = []
    stem = mat_simple(kit, 'cw_stem', (0.25, 0.42, 0.14), 0.6)
    cols = [(0.98, 0.84, 0.18), (0.96, 0.96, 0.92), (0.90, 0.42, 0.62), (0.62, 0.48, 0.90), (0.98, 0.55, 0.20)]
    hv, hf = _icosphere(1)
    for k in range(n):
        A = _Acc(); m = mat_simple(kit, f'cw_bloom{k}', cols[k % len(cols)], 0.5, sss=0.1)
        for f in range(rng.integers(2, 5)):
            a = rng.uniform(0, 6.28); r = rng.uniform(0, 0.01); h = rng.uniform(0.035, 0.06); x0, y0 = r * math.cos(a), r * math.sin(a)
            pts = [(x0, y0, 0), (x0 + 0.003, y0, h * 0.5), (x0 + 0.004 * math.cos(a), y0 + 0.004 * math.sin(a), h)]
            v, fc = _tube(pts, [0.0011, 0.0009, 0.0008], 5, False); A.add(v, fc, 0)
            s = rng.uniform(0.0045, 0.007); A.add([(pts[-1][0] + p[0] * s, pts[-1][1] + p[1] * s, pts[-1][2] + p[2] * s * 0.55) for p in hv], hf, 1)
        obs.append(A.build(bpy, f'cw_flower{k}', [stem, m], True, None))
    return obs

def proto_rocks(kit, n=6, seed=0, color=(0.62, 0.60, 0.56), moss=0.5, snow=0.0, flat=0.6, name='cw_rock'):
    bpy = kit.bpy; obs = []; V0, F0 = _icosphere(3); mat = mat_rock(kit, name + '_mat', color, moss, snow=snow)
    for k in range(n):
        rng = np.random.default_rng(seed * 31 + k)
        V = _lumpy(V0, seed * 13 + k * 7, 0.22, 1.6, 0.08, 5.0) * np.array([1.0, rng.uniform(0.6, 0.95), rng.uniform(flat * 0.7, flat * 1.2)])
        V[:, 2] = np.maximum(V[:, 2], -0.25); V[:, 2] += 0.15
        obs.append(mk_mesh(bpy, f'{name}{k}', V, F0, [mat], None, True, None))
    return obs

def proto_trees(kit, pal, kinds=('round', 'cone', 'tall'), per_kind=3, seed=0, height=0.55):
    """Small procedural trees: a bent trunk with branches and clustered lumpy leaf masses. height in m."""
    bpy = kit.bpy; obs = []; V0, F0 = _icosphere(3)
    bark = mat_simple(kit, 'cw_bark', (0.30, 0.21, 0.14), 0.85, noise_amt=0.3, bump=0.3)
    birch = mat_simple(kit, 'cw_birch', (0.86, 0.84, 0.78), 0.7, noise_amt=0.2)
    leaf = mat_leaf(kit, 'cw_leaf', pal['leaf'], snow=pal.get('snow', 0))
    dens = pal.get('leaf_density', 1.0); i = 0
    for kind in kinds:
        for v in range(per_kind):
            rng = np.random.default_rng(seed * 101 + i); i += 1; A = _Acc(); H = height * rng.uniform(0.85, 1.15)
            lean = rng.uniform(-0.03, 0.03, 2)
            if kind in ('cone', 'tall'):
                tall = kind == 'tall'
                tr = [(0, 0, -0.02), (lean[0] * 0.3, lean[1] * 0.3, H * 0.4), (lean[0], lean[1], H * 0.85)]
                tv, tf = _tube(catmull(tr, 8), np.linspace(0.018, 0.004, 8) * H / 0.55, 8); A.add(tv, tf, 0)  # trunk
                nbl = int(30 * min(1.0, dens + 0.15))
                for s in range(nbl):
                    u = rng.uniform(0, 1) ** 0.85; a = rng.uniform(0, 6.28)
                    if tall: u = rng.uniform(0, 1); R = 0.11 * H * math.sin(math.pi * min(1, u * 0.9 + 0.08)) ** 0.7; r = 0.055 * H; zc = H * (0.30 + 0.66 * u)
                    else: R = (0.19 * (1 - u) + 0.02) * H; r = (0.075 * (1 - u) + 0.04) * H; zc = H * (0.20 + 0.74 * u)
                    rr = R * rng.uniform(0.35, 0.95)
                    c = np.array([lean[0] * (0.3 + u) + rr * math.cos(a), lean[1] * (0.3 + u) + rr * math.sin(a), zc])
                    Vb = _lumpy(V0, seed + i * 7 + s, 0.26, 3.2, 0.12, 9.0) * np.array([r, r, r * 0.7]) + c
                    A.add(Vb, F0, 1)
                A.add(_lumpy(V0, seed + i, 0.2, 3.0, 0.1, 9.0) * (0.04 * H) + np.array([lean[0] * 1.3, lean[1] * 1.3, H * 0.97]), F0, 1)
            else:
                tall = kind == 'tall'; fork = H * (0.38 if not tall else 0.30)
                cr_h = H * (0.24 if not tall else 0.11); cr_v = H * (0.20 if not tall else 0.36); cz = H * (0.66 if not tall else 0.64)
                tr = [(0, 0, -0.02), (lean[0] * 0.4, lean[1] * 0.4, fork * 0.6), (lean[0], lean[1], fork)]
                tv, tf = _tube(catmull(tr, 8), np.linspace(0.022, 0.014, 8) * H / 0.55, 8); A.add(tv, tf, 0)
                top = np.array([lean[0], lean[1], fork])
                nb = int(rng.integers(4, 7)) if not tall else 3; a0 = rng.uniform(0, 6.28)
                cl = [np.array([lean[0] * 1.3, lean[1] * 1.3, cz + cr_v * 0.75])]
                for b in range(nb):
                    a = a0 + b * 2 * math.pi / nb + rng.uniform(-0.4, 0.4); rr = cr_h * rng.uniform(0.7, 1.05)
                    cl.append(np.array([lean[0] + rr * math.cos(a), lean[1] + rr * math.sin(a), cz + cr_v * rng.uniform(-0.45, 0.45)]))
                for c in cl:
                    mid = (top + c) / 2 + np.array([0, 0, H * 0.04])
                    bv, bf = _tube(catmull([top, mid, c * 0.92 + top * 0.08], 6), np.linspace(0.010, 0.004, 6) * H / 0.55, 6); A.add(bv, bf, 0)
                for ci, c in enumerate(cl):
                    if rng.uniform() > dens + 0.15: continue
                    for s in range(int(rng.integers(5, 9))):
                        r = H * rng.uniform(0.07, 0.11) * (0.8 if tall else 1.0)
                        off = rng.normal(0, 1, 3) * np.array([r * 0.55, r * 0.55, r * 0.35])
                        sc = np.array([r, r, r * (0.78 if not tall else 1.2)])
                        Vb = _lumpy(V0, seed + i * 31 + ci * 7 + s, 0.26, 3.2, 0.12, 9.0) * sc + c + off
                        A.add(Vb, F0, 1)
            obs.append(A.build(bpy, f'cw_tree_{kind}{v}', [birch if (kind == 'tall' and v % 2) else bark, leaf], True, None))
    return obs

def proto_weed(kit, n=4, seed=0, height=0.14, colors=((0.30, 0.56, 0.18), (0.48, 0.60, 0.16), (0.26, 0.50, 0.30))):
    bpy = kit.bpy; rng = np.random.default_rng(seed + 13); obs = []
    mat = mat_varied(kit, 'cw_weed', list(colors), rough=0.5, translucent=0.35, bump=0.0)
    for k in range(n):
        A = _Acc()
        for b in range(rng.integers(5, 9)):
            a = rng.uniform(0, 6.28); r = rng.uniform(0, 0.015); h = height * rng.uniform(0.5, 1.2); ph = rng.uniform(0, 6.28)
            P = [(r * math.cos(a) + 0.012 * math.sin(ph + 3 * u) * u, r * math.sin(a) + 0.012 * math.cos(ph + 2 * u) * u, h * u) for u in np.linspace(0, 1, 7)]
            w = rng.uniform(0.004, 0.007); Vb = []; nx, ny = -math.sin(a), math.cos(a)
            for s, p in enumerate(P):
                ww = w * (1 - (s / 6) ** 2) + 0.0005; Vb += [(p[0] - nx * ww, p[1] - ny * ww, p[2]), (p[0] + nx * ww, p[1] + ny * ww, p[2])]
            A.add(Vb, [(2 * s, 2 * s + 1, 2 * s + 3, 2 * s + 2) for s in range(6)])
        obs.append(A.build(bpy, f'cw_weed{k}', [mat], True, None))
    return obs

def proto_corals(kit, seed=0):
    bpy = kit.bpy; obs = []; V0, F0 = _icosphere(2)
    cols = [(0.86, 0.22, 0.30), (0.98, 0.62, 0.18), (0.95, 0.82, 0.30), (0.56, 0.34, 0.72), (0.90, 0.46, 0.52)]
    for k, c in enumerate(cols):
        rng = np.random.default_rng(seed + 70 + k); A = _Acc(); m = mat_simple(kit, f'cw_coral{k}', c, 0.55, sss=0.15, bump=0.4)
        if k == 2:   # brain coral
            Vb = _lumpy(V0, k, 0.1, 3.0, 0.05, 9.0) * np.array([0.045, 0.04, 0.03]); A.add(Vb, F0, 0)
        else:
            for b in range(rng.integers(6, 12)):
                a = rng.uniform(0, 6.28); tilt = rng.uniform(0.1, 0.7); h = rng.uniform(0.04, 0.09)
                P = [(0, 0, 0), (math.cos(a) * tilt * h * 0.4, math.sin(a) * tilt * h * 0.4, h * 0.5), (math.cos(a) * tilt * h, math.sin(a) * tilt * h, h)]
                v, f = _tube(catmull(P, 6), np.linspace(0.006, 0.004, 6), 6); A.add(v, f, 0)
                tip = _lumpy(V0, k * 5 + b, 0.1, 3, 0.0, 1) * 0.0065 + np.array(P[-1]); A.add(tip, F0, 0)
        obs.append(A.build(bpy, f'cw_coral{k}', [m], True, None))
    return obs

def proto_lily(kit, n=4, seed=0):
    bpy = kit.bpy; rng = np.random.default_rng(seed + 17); obs = []
    pad = mat_varied(kit, 'cw_lily', [(0.22, 0.46, 0.14), (0.32, 0.52, 0.16), (0.26, 0.40, 0.12)], rough=0.35, bump=0.0)
    flo = mat_simple(kit, 'cw_lilyflower', (0.98, 0.86, 0.90), 0.5, sss=0.2)
    for k in range(n):
        A = _Acc(); r = rng.uniform(0.025, 0.04); seg = 28; notch = 0.35; Vp = [(0, 0, 0.002)]
        for s in range(seg + 1):
            a = notch + (2 * math.pi - notch) * s / seg; Vp.append((r * math.cos(a), r * math.sin(a), 0.0015 + 0.002 * (s % 2 == 0) * 0))
        A.add(Vp, [(0, s + 1, s + 2) for s in range(seg)], 0)
        if k == 0:
            for p in range(8):
                a = p / 8 * 6.28; A.add([(0, 0, 0.003), (0.012 * math.cos(a - 0.25), 0.012 * math.sin(a - 0.25), 0.012), (0.014 * math.cos(a), 0.014 * math.sin(a), 0.016), (0.012 * math.cos(a + 0.25), 0.012 * math.sin(a + 0.25), 0.012)], [(0, 1, 2, 3)], 1)
        obs.append(A.build(bpy, f'cw_lily{k}', [pad, flo], True, None))
    return obs

def proto_reeds(kit, n=3, seed=0, height=0.2):
    bpy = kit.bpy; rng = np.random.default_rng(seed + 19); obs = []
    mat = mat_varied(kit, 'cw_reed', [(0.38, 0.50, 0.18), (0.50, 0.56, 0.22), (0.30, 0.42, 0.16)], rough=0.6, translucent=0.2, bump=0.0)
    head = mat_simple(kit, 'cw_cattail', (0.30, 0.18, 0.10), 0.8)
    for k in range(n):
        A = _Acc()
        for b in range(rng.integers(7, 12)):
            a = rng.uniform(0, 6.28); h = height * rng.uniform(0.5, 1.1); lean = rng.uniform(0.02, 0.15)
            P = [(0, 0, 0), (math.cos(a) * lean * h * 0.3, math.sin(a) * lean * h * 0.3, h * 0.5), (math.cos(a) * lean * h, math.sin(a) * lean * h, h)]
            v, f = _tube(catmull(P, 5), np.linspace(0.002, 0.0006, 5), 4, False); A.add(v, f, 0)
            if b < 2:
                c = np.array(P[1]) * 1.5; v, f = _tube([c, c + np.array([0, 0, 0.03])], [0.004, 0.004], 8); A.add(v, f, 1)
        obs.append(A.build(bpy, f'cw_reeds{k}', [mat, head], True, None))
    return obs

def _populate(kit, L, rng, grass, grass_height, trees, tree_kinds, tree_scale, boulders, flowers, under, lilies, reeds, corals, tree_spots, sway):
    sx, sy = L.size; pal = L.pal; s = L.seed
    # grass: a dense jittered grid, kept where the grass weight wins a random draw
    if grass > 0:
        step = 0.028 / math.sqrt(grass); P = _jitter_grid(rng, sx, sy, step, 0.004); F = L.field(P[:, 0], P[:, 1])
        keep = (rng.uniform(0, 1, len(P)) < F['w_grass'] ** 1.3) & (F['depth'] < -0.006); P = P[keep]
        tufts = proto_tufts(kit, pal, 7, 0.05 * grass_height, s) + proto_tufts(kit, pal, 3, 0.085 * grass_height, s + 1, (16, 26))
        scatter(kit, L, 'cw_grass', tufts, P, scale=rng.uniform(0.7, 1.3, len(P)), sway=0.22 * sway, speed=0.9)
        if flowers > 0 and pal.get('flowers', 1) > 0:
            q = _jitter_grid(rng, sx, sy, 0.05, 0.02); Fq = L.field(q[:, 0], q[:, 1])
            fz = 0.5 + 0.5 * fbm(q[:, 0], q[:, 1], s + 51, 2, 1.6)
            keep = (Fq['w_grass'] > 0.6) & (fz > 1.0 - 0.32 * flowers * pal.get('flowers', 1)) & (rng.uniform(0, 1, len(q)) < 0.5)
            scatter(kit, L, 'cw_flowers', proto_flowers(kit, 4, s), q[keep], sway=0.18 * sway, speed=0.9)
    # trees
    if tree_spots is not None or trees:
        protos = proto_trees(kit, pal, tuple(dict.fromkeys(tree_kinds)), 3, s)
        kinds = list(dict.fromkeys(tree_kinds))
        if tree_spots is not None:
            T = np.array([(p[0], p[1]) for p in tree_spots]); sc = np.array([p[2] if len(p) > 2 else 1.0 for p in tree_spots])
            var = np.array([kinds.index(p[3]) * 3 + (k % 3) if len(p) > 3 else int(rng.integers(0, len(protos))) for k, p in enumerate(tree_spots)])
        else:
            def ok(p):
                f = L.field(np.array([p[0]]), np.array([p[1]]))
                return f['w_grass'][0] > 0.4 and f['sd'][0] > 0.12 and f['depth'][0] < -0.03
            T = _darts(rng, sx, sy, trees, 0.36, ok, 0.2); sc = rng.uniform(0.6, 1.35, len(T))
            var = np.array([kinds.index(tree_kinds[int(rng.integers(0, len(tree_kinds)))]) * 3 + int(rng.integers(0, 3)) for _ in range(len(T))])
        if len(T): scatter(kit, L, 'cw_trees', protos, T, scale=sc * tree_scale, variant=var, sway=0.025 * sway, speed=0.5, sink=0.01)
        L.trees = T
    # boulders: some on the banks, some in the grass
    if boulders:
        rk = proto_rocks(kit, 6, s, moss=0.6 if pal.get('snow', 0) < 0.5 else 0.0, snow=pal.get('snow', 0))
        def okb(p):
            f = L.field(np.array([p[0]]), np.array([p[1]])); return f['depth'][0] < -0.01
        B = _darts(rng, sx, sy, boulders, 0.12, okb, 0.1)
        if len(B): scatter(kit, L, 'cw_boulders', rk, B, scale=rng.uniform(0.06, 0.15, len(B)), sink=0.025)
        if L.water:
            q = _jitter_grid(rng, sx, sy, 0.09, 0.08); Fq = L.field(q[:, 0], q[:, 1])
            keep = (np.abs(Fq['sd'] - 0.02) < 0.05) & (rng.uniform(0, 1, len(q)) < 0.5)
            if keep.any(): scatter(kit, L, 'cw_bankstones', rk, q[keep], scale=rng.uniform(0.03, 0.08, keep.sum()), sink=0.015)
    if L.water and under:
        q = _jitter_grid(rng, sx, sy, 0.05, 0.03); Fq = L.field(q[:, 0], q[:, 1])
        sel = (Fq['depth'] > 0.06) & (rng.uniform(0, 1, len(q)) < 0.25)
        stones = proto_rocks(kit, 4, s + 3, color=(0.58, 0.56, 0.52), moss=0.0, name='cw_pebble')
        if sel.any(): scatter(kit, L, 'cw_bedstones', stones, q[sel], scale=rng.uniform(0.012, 0.035, sel.sum()), sink=0.006)
        wk = 0.25 if L.water[0].get('kind') == 'lagoon' else 1.0
        w2 = (Fq['depth'] > 0.07) & (0.5 + 0.5 * fbm(q[:, 0], q[:, 1], s + 61, 2, 1.8) > 0.6) & (rng.uniform(0, 1, len(q)) < 0.22 * wk)
        wd = np.minimum(Fq['depth'] * 0.9, 0.22) / 0.14
        if w2.any(): scatter(kit, L, 'cw_weed', proto_weed(kit, 4, s), q[w2], scale=wd[w2] * rng.uniform(0.6, 1.0, w2.sum()), sway=0.12 * sway, speed=0.35)
        if corals:
            def okc(p):
                f = L.field(np.array([p[0]]), np.array([p[1]])); return f['depth'][0] > 0.08
            C = _darts(rng, sx, sy, corals, 0.06, okc, 0.04)
            if len(C): scatter(kit, L, 'cw_corals', proto_corals(kit, s), C, scale=rng.uniform(2.0, 3.4, len(C)), sway=0.0, sink=0.012)
    if L.water and lilies:
        def okl(p):
            f = L.field(np.array([p[0]]), np.array([p[1]])); return f['depth'][0] > 0.05 and f['sd'][0] < -0.05
        centers = _darts(rng, sx, sy, max(1, lilies // 5), 0.25, okl, 0.08); P = []
        for c in centers:
            for _ in range(5 + int(rng.integers(0, 4))):
                p = c + rng.normal(0, 0.06, 2)
                if okl(p) and all(np.hypot(*(p - q)) > 0.05 for q in P): P.append(p)
        if P: scatter(kit, L, 'cw_lilies', proto_lily(kit, 4, s), np.array(P)[:lilies], scale=rng.uniform(0.8, 1.3, min(len(P), lilies)), sway=0.03, speed=0.3, z=L.level + 0.0008)
    if L.water and reeds > 0:
        q = _jitter_grid(rng, sx, sy, 0.05, 0.04); Fq = L.field(q[:, 0], q[:, 1])
        rz = 0.5 + 0.5 * fbm(q[:, 0], q[:, 1], s + 71, 2, 2.0)
        sel = (np.abs(Fq['sd'] + 0.01) < 0.05) & (rz > 1 - 0.55 * reeds) & (rng.uniform(0, 1, len(q)) < 0.7)
        if sel.any(): scatter(kit, L, 'cw_reeds', proto_reeds(kit, 3, s), q[sel], sway=0.08 * sway, speed=0.7)

# =============================================================================================== props (simple hooks)
def _box(x0, y0, z0, x1, y1, z1):
    V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    return V, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]

def pile(kit, L, x, y, length=0.8, radius=0.025, top=None, color=(0.42, 0.30, 0.18), clip=True, name='cw_pile'):
    """A vertical wooden pile driven into the block from z=top (default the terrain) down `length`. Clipped to the block,
    so a pile on the cut plane shows its section on the wall."""
    zt = float(L.height(np.array([x]), np.array([y]))[0]) if top is None else top
    v, f = _tube([(x, y, zt), (x, y, zt - length * 0.5), (x, y, zt - length)], [radius, radius * 0.97, radius * 0.6], 12)
    mat = L.mats.get('pile') or mat_simple(kit, 'cw_pile', color, 0.8, noise_amt=0.35, bump=0.3); L.mats['pile'] = mat
    ob = mk_mesh(kit.bpy, name, v, f, [mat], None, True, kit.coll)
    if clip: cut(kit, L, ob)
    return ob

def pipe(kit, L, path, radius=0.03, color=(0.80, 0.80, 0.78), clip=True, name='cw_pipe', ring=16):
    """A pipe along a 3D polyline (x, y, z) (drainage, utilities). Clipped to the block: it shows round ends on the cut faces."""
    P = catmull(path, max(8, 6 * len(path))); v, f = _tube(P, np.full(len(P), radius), ring)
    mat = mat_simple(kit, name + '_mat', color, 0.4)
    ob = mk_mesh(kit.bpy, name, v, f, [mat], None, True, kit.coll)
    if clip: cut(kit, L, ob)
    return ob

_HOUSE_MATS = {}
def house(kit, L, x, y, w=0.16, d=0.12, h=0.10, roof=0.07, yaw=0.0, wall=(0.92, 0.88, 0.80), roof_col=(0.55, 0.22, 0.14),
          lit=0.0, chimney=True, name='cw_house'):
    """A small house (walls, gable roof, windows, door, chimney). lit > 0 makes the windows glow (dusk/night)."""
    bpy = kit.bpy; A = _Acc()
    v, f = _box(-w / 2, -d / 2, -0.03, w / 2, d / 2, h); A.add(v, f, 0)
    o = 0.012; V = [(-w / 2 - o, -d / 2 - o, h), (w / 2 + o, -d / 2 - o, h), (w / 2 + o, 0, h + roof), (-w / 2 - o, 0, h + roof),
                    (-w / 2 - o, d / 2 + o, h), (w / 2 + o, d / 2 + o, h)]
    A.add(V, [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)], 1)
    if chimney: v, f = _box(w * 0.2, 0.01, h, w * 0.2 + 0.022, 0.033, h + roof + 0.02); A.add(v, f, 1)
    e = 0.0012
    ww = max(0.012, w * 0.09)
    for wx in (-w * 0.25, w * 0.25):
        for side in (-1, 1):
            yy = side * (d / 2 + e); A.add([(wx - ww, yy, h * 0.40), (wx + ww, yy, h * 0.40), (wx + ww, yy, h * 0.78), (wx - ww, yy, h * 0.78)], [(0, 1, 2, 3) if side < 0 else (3, 2, 1, 0)], 2)
    A.add([(w / 2 + e, -0.012, 0.0), (w / 2 + e, 0.012, 0.0), (w / 2 + e, 0.012, h * 0.55), (w / 2 + e, -0.012, h * 0.55)], [(0, 1, 2, 3)], 3)
    key = (wall, roof_col, lit)
    if key not in _HOUSE_MATS:
        _HOUSE_MATS[key] = [mat_simple(kit, 'cw_wall', wall, 0.8, noise_amt=0.08), mat_simple(kit, 'cw_roof', roof_col, 0.7, noise_amt=0.2, bump=0.4),
                            mat_glow(kit, 'cw_window', (1.0, 0.72, 0.36), 14.0 * lit) if lit else mat_simple(kit, 'cw_glass', (0.12, 0.16, 0.20), 0.15),
                            mat_simple(kit, 'cw_door', (0.30, 0.18, 0.10), 0.7)]
    ob = A.build(bpy, name, _HOUSE_MATS[key], False, kit.coll)
    _place(L, ob, x, y); ob.rotation_euler = (0, 0, yaw)
    if lit:
        ld = bpy.data.lights.new(name + '_glow', 'POINT'); ld.energy = 0.35 * lit; ld.color = (1.0, 0.70, 0.40); ld.shadow_soft_size = 0.03
        lo = bpy.data.objects.new(name + '_glow', ld); kit.coll.objects.link(lo); lo.location = (ob.location.x + 0.13 * math.cos(yaw), ob.location.y + 0.13 * math.sin(yaw), ob.location.z + h * 0.6)
    return ob

def mill(kit, L, x, y, yaw=0.0, wheel_r=0.09, rpm=6.0, lit=0.0, wheel_off=0.2, name='cw_mill'):
    """A watermill: a house plus a paddle wheel `wheel_off` m out along its yaw direction (put that on the water), turning
    with time (rpm, looping-safe)."""
    bpy = kit.bpy; hs = house(kit, L, x, y, 0.18, 0.13, 0.13, 0.08, yaw, (0.82, 0.74, 0.62), (0.40, 0.24, 0.16), lit, True, name)
    A = _Acc(); wood = mat_simple(kit, 'cw_millwood', (0.36, 0.24, 0.15), 0.8, noise_amt=0.3)
    for side in (-1, 1):
        th = np.linspace(0, 2 * math.pi, 25)
        ring = [(wheel_r * math.cos(a), side * 0.022, wheel_r * math.sin(a)) for a in th]
        v, f = _tube(ring, np.full(len(ring), 0.004), 6, False); A.add(v, f)
    for k in range(12):
        a = k / 12 * 2 * math.pi; c, s = math.cos(a), math.sin(a)
        v, f = _box(-0.003, -0.026, wheel_r * 0.35, 0.003, 0.026, wheel_r * 1.12)
        A.add([(p[0] * c - p[2] * s, p[1], p[0] * s + p[2] * c) for p in v], f)
    v, f = _tube([(0, -0.05, 0), (0, 0.05, 0)], [0.008, 0.008], 8); A.add(v, f)
    wh = A.build(bpy, name + '_wheel', [wood], False, kit.coll)
    off = wheel_off; wh.location = (hs.location.x + off * math.cos(yaw), hs.location.y + off * math.sin(yaw), (L.level if L.level is not None else hs.location.z) + wheel_r * 0.55)
    wh.rotation_euler = (0, 0, yaw + math.pi / 2)
    @kit.on_frame
    def _spin(t): wh.rotation_euler = (kit.cycles(t, rpm / 60.0), 0, yaw + math.pi / 2)
    return hs, wh

def bridge(kit, L, a, b, width=0.08, arch=0.05, color=(0.50, 0.40, 0.30), name='cw_bridge'):
    """An arched plank bridge from point a=(x, y) to b=(x, y), resting on the terrain heights at its ends."""
    a = np.array(a, float); b = np.array(b, float); za = float(L.height(a[:1], a[1:])[0]); zb = float(L.height(b[:1], b[1:])[0])
    d = b - a; n = np.array([-d[1], d[0]]) / np.linalg.norm(d); A = _Acc(); seg = 16; V = []
    for k in range(seg + 1):
        u = k / seg; p = a + d * u; z = za + (zb - za) * u + arch * math.sin(math.pi * u) + 0.01
        V += [(*(p - n * width / 2), z), (*(p + n * width / 2), z), (*(p - n * width / 2), z - 0.012), (*(p + n * width / 2), z - 0.012)]
    F = []
    for k in range(seg):
        i = 4 * k; F += [(i, i + 4, i + 5, i + 1), (i + 2, i + 3, i + 7, i + 6), (i, i + 2, i + 6, i + 4), (i + 1, i + 5, i + 7, i + 3)]
    A.add(V, F)
    for side in (-1, 1):
        rail = [(*(a + d * u + side * n * width / 2), za + (zb - za) * u + arch * math.sin(math.pi * u) + 0.045) for u in np.linspace(0, 1, 10)]
        v, f = _tube(rail, np.full(10, 0.0025), 5); A.add(v, f)
        for u in np.linspace(0.05, 0.95, 6):
            p = a + d * u + side * n * width / 2; z = za + (zb - za) * u + arch * math.sin(math.pi * u)
            v, f = _tube([(p[0], p[1], z), (p[0], p[1], z + 0.047)], [0.0025, 0.0025], 5); A.add(v, f)
    return A.build(kit.bpy, name, [mat_simple(kit, 'cw_bridgewood', color, 0.8, noise_amt=0.3)], False, kit.coll)

def lamp(kit, L, x, y, h=0.07, strength=0.25, name='cw_lamp'):
    """A small lamp post with a warm glowing head and a point light."""
    bpy = kit.bpy; A = _Acc(); v, f = _tube([(0, 0, 0), (0, 0, h)], [0.0025, 0.002], 6); A.add(v, f, 0)
    V0, F0 = _icosphere(1); A.add(V0 * 0.008 + np.array([0, 0, h]), F0, 1)
    ob = A.build(bpy, name, [mat_simple(kit, 'cw_iron', (0.08, 0.08, 0.08), 0.5), mat_glow(kit, 'cw_lamphead', (1.0, 0.74, 0.40), 25.0)], True, kit.coll)
    _place(L, ob, x, y)
    ld = bpy.data.lights.new(name + '_l', 'POINT'); ld.energy = strength; ld.color = (1.0, 0.72, 0.42); ld.shadow_soft_size = 0.01
    lo = bpy.data.objects.new(name + '_l', ld); kit.coll.objects.link(lo); lo.location = (ob.location.x, ob.location.y, ob.location.z + h + 0.012)
    return ob

def tunnel_mouth(kit, L, x, y, r=0.08, face='-Y', depth=0.6, name='cw_tunnel'):
    """A dark arched void cut into a wall face (face '-Y' or '+X'), for a castle passage or mine. Uses a boolean on the walls."""
    bpy = kit.bpy; sx, sy = L.size; A = _Acc(); th = np.linspace(0, math.pi, 13); prof = [(r * math.cos(a), r * math.sin(a)) for a in th] + [(-r, -r * 0.8), (r, -r * 0.8)]
    V = []
    for yy in (-0.02, depth):
        V += [(p[0], yy, p[1]) for p in prof]
    n = len(prof); F = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    cutter = mk_mesh(bpy, name + '_cutter', V, F, (), None, False, None)
    if face == '-Y': cutter.location = (x, -sy / 2, y)
    else: cutter.location = (sx / 2, x, y); cutter.rotation_euler = (0, 0, math.pi / 2)
    md = L.objects['walls'].modifiers.new(name, 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cutter; md.solver = 'EXACT'
    return cutter

# =============================================================================================== backgrounds and light
def _plane(kit, name, size, z, mat, loc=(0, 0)):
    V = [(-size + loc[0], -size + loc[1], z), (size + loc[0], -size + loc[1], z), (size + loc[0], size + loc[1], z), (-size + loc[0], size + loc[1], z)]
    return mk_mesh(kit.bpy, name, V, [(0, 1, 2, 3)], [mat], None, False, kit.coll)

def _sun(kit, az, el, strength, angle=6.0, color=(1, 1, 1), name='cw_sun'):
    bpy = kit.bpy; ld = bpy.data.lights.new(name, 'SUN'); ld.energy = strength; ld.angle = math.radians(angle); ld.color = color
    ob = bpy.data.objects.new(name, ld); kit.coll.objects.link(ob)
    ob.rotation_euler = (math.radians(90 - el), 0, math.radians(az + 90)); return ob

def cloud_shadows(kit, opacity=0.3, scale=0.5, speed=0.05, z=3.0):
    """An invisible plane high above that only casts soft moving cloud shadows (drifting light)."""
    m = _new_mat(kit.bpy, 'cw_cloudshadow'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    zo, w = g.phase(speed); p = g.vmath('ADD', tc.outputs['Object'], g.comb(0, 0, zo))
    n = g.noise(p, scale, 3.0, 0.55, '4D', w); f = g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.48), 6.0, clamp=True)
    tr = g.node('ShaderNodeBsdfTransparent'); df = g.node('ShaderNodeBsdfDiffuse', ins={'Color': (0, 0, 0)}); mx = g.node('ShaderNodeMixShader')
    g.link(g.math('MULTIPLY', f, opacity), mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(df, mx.inputs[2]); _finish(g, mx)
    ob = _plane(kit, 'cw_cloudshadow', 12, z, m)
    for a in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
    return ob

def studio(kit, color=(0.93, 0.92, 0.90), key_az=-130.0, key_el=48.0, key=3.2, angle=14.0, fill=0.9, floor_z=None, land=None, shadows=0.0):
    """Seamless studio: a matte floor (in colour) under the block, the same colour behind, a soft key sun and a fill.
    floor_z: floor height (default the block bottom, so it sits on the floor). shadows > 0 adds drifting cloud shadows."""
    fz = floor_z if floor_z is not None else (-land.depth if land else -1.4)
    mat = mat_simple(kit, 'cw_floor', color, 0.9); _plane(kit, 'cw_floor', 40, fz - 0.0005, mat)
    mat_gradient_bg(kit, color, color, 1.0, (1.0, 1.0, 1.0), fill)
    _sun(kit, key_az, key_el, key, angle, (1.0, 0.98, 0.95))
    if shadows: cloud_shadows(kit, shadows)

def sky(kit, top=(0.58, 0.68, 0.80), horizon=(0.80, 0.84, 0.89), sun_az=-120.0, sun_el=40.0, sun=3.0, clouds=7, mist=True, land=None, seed=3, behind_az=135.0):
    """Open sky for a floating island: a soft gradient, a few soft cloud cards (around behind_az, the direction opposite the
    camera azimuth), layers of mist below, drifting cloud shadows."""
    bpy = kit.bpy; mat_gradient_bg(kit, top, horizon, 1.0, (0.85, 0.90, 1.0), 0.9)
    _sun(kit, sun_az, sun_el, sun, 4.0, (1.0, 0.96, 0.90)); rng = np.random.default_rng(seed)
    def card_mat(name, color, alpha, sc, speed, soft=4.0, glow=1.0):
        m = _new_mat(bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); u = tc.outputs['Generated']
        zo, w = g.phase(speed); us = g.sep(u)
        r = g.math('LENGTH', 0) if False else g.vmath('LENGTH', g.vmath('MULTIPLY', g.vmath('SUBTRACT', u, (0.5, 0.5, 0)), (2.0, 2.0, 0)))
        edge = g.math('SUBTRACT', 1.0, r, clamp=True)
        n = g.noise(g.comb(g.math('MULTIPLY', us[0], 2.0), us[1], zo), sc, 4.0, 0.6, '4D', w)
        a = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', n.outputs['Fac'], g.math('MULTIPLY', edge, 0.9)), 0.95), soft, clamp=True), alpha)
        em = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': glow}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
        g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(em, mx.inputs[2]); _finish(g, mx); return m
    d = land.depth if land else 1.4
    for k in range(clouds):
        m = card_mat(f'cw_cloud{k}', (0.98, 0.98, 1.0), 0.95, 2.5, 0.02, 4.0, 1.5)
        a = math.radians(behind_az + rng.uniform(-38, 38)); r = rng.uniform(13, 20); s = rng.uniform(2.0, 3.6)
        ob = _plane(kit, f'cw_cloud{k}', 1, 0, m); ob.scale = (s * 1.8, s * 0.55, 1); ob.rotation_euler = (math.pi / 2, 0, a + math.pi / 2)
        ob.location = (r * math.cos(a), r * math.sin(a), rng.uniform(-4.5, -0.8) + 0.25 * r - 3.5)
        for at in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission'): setattr(ob, at, False)
    if mist:
        for k, (z, op) in enumerate(((-d - 1.9, 0.9), (-d - 1.4, 0.6), (-d - 1.0, 0.35))):
            m = card_mat(f'cw_mist{k}', (0.96, 0.97, 0.99), op, 1.4, 0.03, 3.0, 1.45)
            ob = _plane(kit, f'cw_mist{k}', 1, z, m); ob.scale = (9, 9, 1)
            for at in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission'): setattr(ob, at, False)
    cloud_shadows(kit, 0.35)

def dusk(kit, top=(0.16, 0.20, 0.36), horizon=(0.80, 0.52, 0.42), floor=(0.40, 0.34, 0.44), sun_az=-150.0, sun_el=9.0, sun=2.2, land=None):
    """Dusk studio: a deep blue-to-amber gradient, a low warm sun, a cool fill, a dark seamless floor."""
    mat_gradient_bg(kit, top, horizon, 1.0, (0.45, 0.55, 0.95), 0.55)
    _sun(kit, sun_az, sun_el, sun, 3.0, (1.0, 0.62, 0.36))
    fz = -land.depth if land else -1.4; _plane(kit, 'cw_floor', 40, fz - 0.0005, mat_backdrop(kit, 'cw_floor', top, horizon, floor))

def mat_backdrop(kit, name, top, horizon, floor, glow=0.35):
    """A seamless floor that reads as a dusk backdrop: screen-space gradient (amber glow up the frame, deep blue at the
    bottom) as a faint emission over a matte surface that still takes the block's shadow."""
    m = _new_mat(kit.bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); wy = g.sep(tc.outputs['Window'])[1]
    col = g.ramp(wy, [(0.0, tuple(c * 0.55 for c in top)), (0.55, floor), (1.0, horizon)])
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.9})
    g.put(p, 'Emission Color', col); g.put(p, 'Emission Strength', glow); _finish(g, p); return m

def birds(kit, n=4, center=(0.0, 0.0), radius=2.4, height=1.4, seed=5, size=0.04, color=(0.10, 0.10, 0.11)):
    """A few birds gliding on loose circles above the block, flapping in bursts. Loop-safe."""
    bpy = kit.bpy; rng = np.random.default_rng(seed); mat = mat_simple(kit, 'cw_bird', color, 0.6); out = []
    for k in range(n):
        body = mk_mesh(bpy, f'cw_bird{k}', *_tube([(-size * 0.5, 0, 0), (0, 0, 0.0), (size * 0.45, 0, 0)], [size * 0.08, size * 0.12, size * 0.05], 6), [mat], None, True, kit.coll)
        wings = []
        for side in (-1, 1):
            V = [(-size * 0.15, 0, 0), (size * 0.15, 0, 0), (0.0, side * size * 0.9, 0), (-size * 0.25, side * size * 0.7, 0)]
            wg = mk_mesh(bpy, f'cw_bird{k}w{side}', V, [(0, 1, 2, 3)], [mat], None, False, kit.coll); wg.parent = body; wings.append((wg, side))
        r = radius * rng.uniform(0.6, 1.1); h = height + rng.uniform(-0.3, 0.4); ph = rng.uniform(0, 6.28); laps = rng.choice([1, 1, 2]) * (1 if rng.uniform() < 0.5 else -1)
        flap = rng.uniform(2.5, 4.0); cx, cy = center[0] + rng.uniform(-0.6, 0.6), center[1] + rng.uniform(-0.6, 0.6)
        def pose(t, body=body, wings=wings, r=r, h=h, ph=ph, laps=laps, flap=flap, cx=cx, cy=cy):
            a = ph + laps * 2 * math.pi * t / kit.loop * max(1, round(kit.loop / 20.0))
            body.location = (cx + r * math.cos(a), cy + r * math.sin(a), h + 0.08 * math.sin(2 * a))
            body.rotation_euler = (math.radians(-12 * np.sign(laps)), 0, a + np.sign(laps) * math.pi / 2)
            f = kit.cycles(t, flap); burst = 0.5 + 0.5 * math.sin(kit.cycles(t, 0.25) + ph)
            ang = math.radians(10 + 35 * burst * math.sin(f))
            for wg, side in wings: wg.rotation_euler = (side * ang, 0, 0)
        kit.on_frame(pose); pose(0.0); out.append(body)
    return out

def falling_stones(kit, L, n=14, seed=9, color=(0.42, 0.36, 0.30)):
    """Stones and clods drifting down and away under a floating block (each loops through its fall). Loop-safe."""
    bpy = kit.bpy; rng = np.random.default_rng(seed); sx, sy = L.size; protos = proto_rocks(kit, 4, seed, color, 0.3, name='cw_fall')
    obs = []
    for k in range(n):
        src = protos[k % 4]; ob = bpy.data.objects.new(f'cw_fall{k}', src.data); kit.coll.objects.link(ob)
        s = rng.uniform(0.04, 0.13); ob.scale = (s, s, s)
        x0 = rng.uniform(-sx / 2 * 0.95, sx / 2 * 0.95); y0 = rng.uniform(-sy / 2 * 0.95, sy / 2 * 0.95)
        drift = rng.normal(0, 0.12, 2); fall = rng.uniform(0.5, 0.95); off = rng.uniform(0, 1); spin = rng.normal(0, 1.5, 3)
        def pose(t, ob=ob, x0=x0, y0=y0, drift=drift, fall=fall, off=off, spin=spin, s=s):
            u = (t / kit.loop * max(1, round(kit.loop / 12.0)) + off) % 1.0
            ob.location = (x0 + drift[0] * u, y0 + drift[1] * u, -L.depth - 0.06 - fall * u * u)
            ob.rotation_euler = tuple(spin * u * 2)
            sc = s * min(1.0, (1 - u) * 6) * min(1.0, u * 12 + 0.2); ob.scale = (sc, sc, sc)
        kit.on_frame(pose); pose(0.0); obs.append(ob)
    return obs

def hanging_roots(kit, L, n=40, seed=12, length=(0.08, 0.45), color=(0.30, 0.21, 0.13)):
    """Thin roots dangling from the bottom edges of a floating block, swaying a little. Loop-safe."""
    rng = np.random.default_rng(seed); sx, sy = L.size; A = _Acc(); z0 = -L.depth
    for k in range(n):
        side = rng.integers(0, 4); u = rng.uniform(-0.48, 0.48)
        x, y = [(u * sx, -sy / 2), (sx / 2, u * sy), (u * sx, sy / 2), (-sx / 2, u * sy)][side]
        x *= 0.985; y *= 0.985; ln = rng.uniform(*length); ph = rng.uniform(0, 6.28)
        P = [(x + 0.02 * math.sin(ph + 7 * t) * t, y + 0.02 * math.cos(ph + 5 * t) * t, z0 + 0.01 - ln * t) for t in np.linspace(0, 1, 8)]
        v, f = _tube(P, np.linspace(0.006, 0.0012, 8), 5); A.add(v, f)
    ob = A.build(kit.bpy, 'cw_roots', [mat_simple(kit, 'cw_rootmat', color, 0.85)], True, kit.coll)
    @kit.on_frame
    def _sway(t): ob.rotation_euler = (0.006 * math.sin(kit.cycles(t, 0.2)), 0.006 * math.cos(kit.cycles(t, 0.15)), 0)
    return ob

# =============================================================================================== camera
class Cam:
    """A product-shot camera on a sphere around a target. pose(az, el, dist) sets it; orbit/push are time helpers."""
    def __init__(self, kit, ob, target, az, el, dist):
        self.kit = kit; self.ob = ob; self.target = np.array(target, float); self.az = az; self.el = el; self.dist = dist; self.pose()
    def pose(self, az=None, el=None, dist=None, target=None):
        from mathutils import Vector
        if az is not None: self.az = az
        if el is not None: self.el = el
        if dist is not None: self.dist = dist
        if target is not None: self.target = np.array(target, float)
        a, e = math.radians(self.az), math.radians(self.el)
        p = self.target + self.dist * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        self.ob.location = tuple(p); d = Vector(tuple(self.target - p))
        self.ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    def orbit(self, t, deg_per_s=2.0, az0=None, el=None, dist=None, duration=None):
        """Slow orbit; with duration the move eases in and out (a real operator's move)."""
        base = self.__dict__.setdefault('_az0', self.az if az0 is None else az0)
        if duration:
            u = min(1.0, max(0.0, t / duration)); a = 0.2; n = 1 - a
            e = (u * u / (2 * a) / n) if u < a else ((a / 2 + (u - a)) / n if u < 1 - a else 1 - (1 - u) ** 2 / (2 * a * n))
            self.pose(base + deg_per_s * duration * e, el, dist)
        else: self.pose(base + deg_per_s * t, el, dist)

def camera(kit, land=None, aspect='16:9', az=-40.0, el=32.0, lens=60.0, fill=0.86, target=None, dist=None, top_extra=0.45, bottom_extra=0.0, name='cw_cam'):
    """High three-quarter product camera. aspect '16:9' or '9:16' (or a float w/h). fill = fraction of the frame the block
    spans (its bounding box from bottom to top_extra above z=0, so trees fit); the target is re-centred and dist computed
    to fit unless given. Sets scene.camera and the render resolution aspect is the caller's."""
    bpy = kit.bpy; cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36.0; cd.sensor_fit = 'AUTO'
    cd.clip_start = 0.05; cd.clip_end = 200
    ob = bpy.data.objects.new(name, cd); kit.coll.objects.link(ob); bpy.context.scene.camera = ob
    asp = 16 / 9 if aspect == '16:9' else 9 / 16 if aspect == '9:16' else float(aspect)
    th = 18.0 / lens; tanh, tanv = (th, th / asp) if asp >= 1 else (th * asp, th)
    if land is not None:
        sx, sy = land.size; tgt = np.array((0, 0, -land.depth * 0.42) if target is None else target, float)
        ztop = top_extra
        pts = np.array([(x, y, z) for x in (-sx / 2, sx / 2) for y in (-sy / 2, sy / 2) for z in (-land.depth - bottom_extra, ztop)])
    else:
        tgt = np.array(target or (0, 0, 0), float); pts = None
    if dist is None:
        dist = 8.0
        if pts is not None:   # exact fit: frame the block's bounding box at `fill` of the frame, centred (a few passes)
            for _ in range(6):
                a, e = math.radians(az), math.radians(el); dvec = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
                cp = tgt + dist * dvec; fwd = -dvec; right = np.cross(fwd, (0, 0, 1)); right /= np.linalg.norm(right); up = np.cross(right, fwd)
                v = pts - cp; z = v @ fwd; u = (v @ right) / z / tanh; w = (v @ up) / z / tanv
                tgt = tgt + right * ((u.max() + u.min()) / 2 * tanh * dist) + up * ((w.max() + w.min()) / 2 * tanv * dist)
                span = max((u.max() - u.min()) / 2, (w.max() - w.min()) / 2); dist *= span / fill
        else:
            dist = 2.5 / tanh / fill
    return Cam(kit, ob, tgt, az, el, dist)

def render_settings(bpy, W, H, samples=64, denoise=True, look='AgX - Base Contrast', exposure=0.0, threads=0):
    """Cycles CPU settings for stills (the film harness sets its own from SETTINGS)."""
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.resolution_percentage = 100
    cy = sc.cycles; cy.device = 'CPU'; cy.samples = samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
    cy.use_denoising = denoise; cy.denoiser = 'OPENIMAGEDENOISE'; apply_cycles(bpy)
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = look; sc.view_settings.exposure = exposure
    if threads: sc.render.threads_mode = 'FIXED'; sc.render.threads = threads

def apply_cycles(bpy, fast=False):
    """Bounce limits that suit the kit (glass water needs transmission depth; no caustics: they are faked).
    fast=True trims bounces for motion renders (about a third quicker, slightly darker under trees)."""
    cy = bpy.context.scene.cycles
    cy.max_bounces = 6 if fast else 8; cy.diffuse_bounces = 1 if fast else 2; cy.glossy_bounces = 1 if fast else 2
    cy.transmission_bounces = 5 if fast else 8; cy.transparent_max_bounces = 6 if fast else 12
    cy.volume_bounces = 0; cy.caustics_reflective = False; cy.caustics_refractive = False; cy.sample_clamp_indirect = 6.0
    try: cy.use_light_tree = True
    except Exception: pass
