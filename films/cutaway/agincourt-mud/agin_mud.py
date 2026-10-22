"""Agincourt mud: the shared scene for the two Cutaway inserts of "The Battle of Agincourt" (Battle Map).

    A  (l06 to l07): the ploughed field in rain, puddles in the furrows, the soaked layers in the cut face; the English
                     archers hammer sharpened stakes in at an angle, then the line is ready to shoot.
    B  (l10 to l11): the French walk on foot through the mud; at the cut face we see their legs sink to the knee, slower
                     and slower; the woods on both sides squeeze the column into the neck.

Every beat is placed on the narration words read from films/battles/agincourt/cues.json (W(line, word)), every pose is a
pure function of the film time T (seconds on the Agincourt timeline), so any frame renders the same on any runner.
Free: Blender bpy 5.2.2, Cycles CPU, the Cutaway kit (films/styles/cutaway/cutaway.py, imported, not edited).

Layout (metres, block centred on the origin, top near z = 0): the march runs along +X (France at -X, England at +X).
The -Y face is the cut face the French front file walks along. Woods: the Agincourt wood along +Y, the Tramecourt wood
bulging in from -Y in the middle (the neck). Stakes in one zigzag row at x 1.5, archers right behind them, the English
men-at-arms behind the archers. Colours from the Battle Map engine (blocks.js TEAMS): England rome red, France carthage
blue, both trimmed gold; banners are the film's (field colour, gold border, gold disc, swallowtail).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
_KIT = os.path.join(ROOT, 'films', 'styles', 'cutaway')
if _KIT not in sys.path: sys.path.insert(0, _KIT)
import cutaway as cw  # noqa: E402

FPS = 24
_CUES = json.load(open(os.path.join(ROOT, 'films', 'battles', 'agincourt', 'cues.json')))
LINES = {l['id']: l for l in _CUES['lines']}


def W(line, word, n=1, end=False):
    """Start (or end) time in the film of the n-th occurrence of `word` in cue line `line`."""
    k = 0
    for w in LINES[line]['words']:
        if w[0].strip('.,!?;:').lower() == word.lower():
            k += 1
            if k == n: return float(w[2] if end else w[1])
    raise KeyError(f'{line}.{word}#{n}')


SPANS = {'A': ('l06', 'l08'), 'B': ('l10', 'l12')}   # first line, the line after the last


def span(name):
    """(t0, t1, f0, f1): film seconds and 24 fps film frames [f0, f1) the insert covers."""
    a, b = SPANS[name]; t0 = float(LINES[a]['start']); t1 = float(LINES[b]['start'])
    return t0, t1, int(round(t0 * FPS)), int(round(t1 * FPS))


# ============================================================================================ the field
SX, SY, DEPTH = 4.2, 3.2, 0.9
YF = -SY / 2                  # the -Y cut face (the French front file walks on it)
PER, AMP = 0.085, 0.011       # plough furrows: period along x, half height
LV = -0.0085                  # puddle water level
RES = 0.012
SOFT = 0.065                  # soft wet top layer thickness
STRATA = [('soft mud', SOFT, (0.15, 0.105, 0.07), 0.0), ('wet loam', 0.10, (0.33, 0.24, 0.155), 0.06),
          ('clay', 0.13, (0.53, 0.46, 0.37), 0.02), ('chalky marl', 0.15, (0.75, 0.70, 0.59), 0.18),
          ('deep', 1.0, (0.46, 0.38, 0.29), 0.30)]
FR = {'top': (0.13, 0.33, 0.80), 'trim': (0.98, 0.84, 0.46)}     # Battle Map TEAMS.carthage
EN = {'top': (0.78, 0.11, 0.12), 'trim': (0.98, 0.84, 0.46)}     # Battle Map TEAMS.rome


def near_bump(x): return np.exp(-((np.asarray(x, float) - 0.25) / 0.62) ** 4)
def near_pres(x): return np.clip((near_bump(x) - 0.03) / 0.12, 0.0, 1.0)
def y_near(x): return YF + 0.58 * near_bump(x)           # Tramecourt wood edge (wood is below it, y smaller)
def y_far(x):                                              # Agincourt wood edge (wood above it)
    x = np.asarray(x, float); return 0.80 - 0.09 * (x + SX / 2) / SX - 0.36 * np.exp(-((x - 0.35) / 0.75) ** 2)


def mask(x, y):
    """1 on the ploughed field, 0 in the woods."""
    x = np.asarray(x, float); y = np.asarray(y, float); yn = y_near(x); yf = y_far(x)
    nt = 1 - near_pres(x) * (1 - cw.smooth(yn - 0.03, yn + 0.09, y))
    return nt * cw.smooth(yf + 0.03, yf - 0.09, y)


def _base(x, y): return 0.009 * cw.fbm(x, y, 7, 3, 0.55) + 0.004 * cw.fbm(x, y, 8, 2, 2.5)
def _wood(x, y): return 0.022 + 0.008 * cw.fbm(x, y, 11, 3, 2.5)
def _phase(x, y): return 2 * np.pi * (x + 0.05 * cw.fbm(x * 0.3, y * 0.9, 9, 2, 1.0)) / PER
def furrow(x, y): return 0.5 + 0.5 * np.cos(_phase(np.asarray(x, float), np.asarray(y, float)))   # 1 crest, 0 trough


def top(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); m = mask(x, y)
    fur = AMP * np.cos(_phase(x, y)) * (0.85 + 0.3 * cw.fbm(x, y, 10, 2, 1.5))
    return _base(x, y) + m * fur + (1 - m) * _wood(x, y)


def gmid(x, y):
    """Ground height without the furrows (where a figure stands)."""
    x = np.asarray(x, float); y = np.asarray(y, float); m = mask(x, y)
    return _base(x, y) + (1 - m) * _wood(x, y)


def g1(x, y): return float(gmid(np.array([x]), np.array([y]))[0])


def tree_spots(seed=21):
    rng = np.random.default_rng(seed); pts = []
    def ok(x, y):
        far = y > float(y_far(x)) + 0.12 and y < SY / 2 - 0.07
        near = float(near_pres(x)) > 0.6 and y < float(y_near(x)) - 0.10 and y > YF + 0.07
        return far or near
    for _ in range(8000):
        if len(pts) >= 95: break
        x = rng.uniform(-SX / 2 + 0.07, SX / 2 - 0.07); y = rng.uniform(-SY / 2 + 0.07, SY / 2 - 0.07)
        if ok(x, y) and all((x - p[0]) ** 2 + (y - p[1]) ** 2 > 0.19 ** 2 for p in pts): pts.append((x, y))
    kinds = ['round', 'round', 'tall', 'cone']; out = []
    for x, y in pts:
        edge = min(abs(y - float(y_far(x))), abs(y - float(y_near(x))) if float(near_pres(x)) > 0.5 else 9.0)
        sc = rng.uniform(1.25, 1.75) if edge > 0.28 else rng.uniform(0.8, 1.15)
        out.append((x, y, sc, kinds[int(rng.integers(0, 4))]))
    return out


# ============================================================================================ small mesh helpers
def _ico(sub=2):
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    V = np.array([v.co[:] for v in bm.verts]); F = [tuple(v.index for v in f.verts) for f in bm.faces]; bm.free()
    return V, F


_ICO = {}
def ell(c, r, sub=2):
    if sub not in _ICO: _ICO[sub] = _ico(sub)
    V, F = _ICO[sub]; return V * np.asarray(r, float) + np.asarray(c, float), F


def tube(pts, radii, ring=10, cap=True):
    C = np.asarray(pts, float); n = len(C); R = np.asarray(radii, float)
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-12
    up = np.array([0, 0, 1.0]); V = []; F = []
    for k in range(n):
        a = up if abs(T[k] @ up) < 0.95 else np.array([1.0, 0, 0])
        N = np.cross(a, T[k]); N /= np.linalg.norm(N); B = np.cross(T[k], N)
        for j in range(ring):
            ph = 2 * math.pi * j / ring; V.append(C[k] + R[k] * (math.cos(ph) * N + math.sin(ph) * B))
    for k in range(n - 1):
        for j in range(ring):
            a = k * ring + j; b = k * ring + (j + 1) % ring; F.append((a, b, b + ring, a + ring))
    if cap:
        V.append(C[0]); c0 = len(V) - 1; F += [(c0, (j + 1) % ring, j) for j in range(ring)]
        V.append(C[-1]); c1 = len(V) - 1; base = (n - 1) * ring; F += [(c1, base + j, base + (j + 1) % ring) for j in range(ring)]
    return np.array(V), F


def torus(R, r, n=18, m=8):
    V = []; F = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m; V.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m):
            a = i * m + j; b = ((i + 1) % n) * m + j; c = ((i + 1) % n) * m + (j + 1) % m; d = i * m + (j + 1) % m; F.append((a, b, c, d))
    return np.array(V), F


class Acc:
    def __init__(self): self.V = []; self.F = []; self.M = []
    def add(self, VF, m=0, xf=None):
        V, F = VF; V = np.asarray(V, float)
        if xf is not None: V = xf(V)
        o = len(self.V); self.V += [tuple(v) for v in V]; self.F += [tuple(i + o for i in f) for f in F]; self.M += [m] * len(F)
    def mesh(self, bpy, name, mats, smooth=True, fix=False):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.V, [], self.F)
        for mt in mats: me.materials.append(mt)
        me.polygons.foreach_set('material_index', np.asarray(self.M, np.int32))
        me.polygons.foreach_set('use_smooth', np.full(len(self.F), bool(smooth)))
        if fix: _outward(me)
        me.update(); return me


def _outward(me):
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()


def obj(bpy, kit, name, me, parent=None):
    ob = bpy.data.objects.new(name, me); kit.coll.objects.link(ob)
    if parent is not None: ob.parent = parent
    return ob


def ease(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


def ease5(u):
    u = min(1.0, max(0.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)


def keys(T, K):
    """Piecewise eased interpolation through [(time, value), ...]."""
    if T <= K[0][0]: return K[0][1]
    for (ta, va), (tb, vb) in zip(K[:-1], K[1:]):
        if T <= tb: return va + (vb - va) * ease((T - ta) / max(1e-6, tb - ta))
    return K[-1][1]


# ============================================================================================ materials
def _mat(kit, name):
    m = kit.bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    m.node_tree.nodes.clear(); return m, cw.G(m.node_tree, kit)


def _out(g, sh):
    o = g.node('ShaderNodeOutputMaterial', target='ALL'); g.link(sh, o.inputs['Surface']); return o


def mat_mud(kit, rain):
    """The field top: furrow crests lighter and drier, troughs dark and glossy; the wood floor under the grass."""
    m, g = _mat(kit, 'ag_mudtop'); tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']
    fur = g.attr('ag_fur').outputs['Fac']; fld = g.attr('w_path').outputs['Fac']
    n_mid = g.noise(pos, 7.0, 4.0); n_fine = g.noise(pos, 70.0, 4.0); vo = g.voronoi(pos, 85.0, 'F1')
    crest = g.math('POWER', fur, 1.5)
    mud = g.mix(crest, cw.srgb((0.10, 0.07, 0.045)), cw.srgb((0.30, 0.215, 0.135)))
    mud = g.mix(g.math('MULTIPLY', n_mid.outputs['Fac'], 0.55), mud, g.mix(0.6, mud, (0.0, 0.0, 0.0), 'MULTIPLY'))
    clod = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 2.2), clamp=True), crest)
    mud = g.mix(g.math('MULTIPLY', clod, 0.45), mud, cw.srgb((0.38, 0.29, 0.19)))
    floor = g.mix(n_mid.outputs['Fac'], cw.srgb((0.14, 0.11, 0.06)), cw.srgb((0.25, 0.20, 0.10)))
    col = g.mix(fld, floor, mud)
    wet = 0.10 if rain else 0.16
    r_mud = g.math('MULTIPLY_ADD', crest, 0.42, wet)
    rough = g.mix(fld, 0.85, r_mud, dtype='FLOAT')
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': rough})
    h = g.math('ADD', g.math('MULTIPLY', n_fine.outputs['Fac'], 0.6), g.math('MULTIPLY', clod, 0.8))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.35, 'Height': h, 'Distance': 0.004}); g.put(p, 'Normal', b)
    _out(g, p); return m


def patch_strata(kit, mat):
    """The kit's strata walls, plus: the soft top layer darker and glossy (wet), firmer layers matte below it."""
    nt = mat.node_tree; g = cw.G(nt, kit)
    p = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    sd = g.attr('sd').outputs['Fac']; tc = g.node('ShaderNodeTexCoord'); sx = g.sep(tc.outputs['Object'])
    wob = g.noise(g.comb(g.math('ADD', sx[0], sx[1]), 0.0, 0.0), 9.0, 3.0)
    edge = g.math('ADD', SOFT - 0.006, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.014))
    wet = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', sd, edge), 1 / 0.012, clamp=True))
    lk = next(l for l in nt.links if l.to_node == p and l.to_socket.name == 'Base Color'); src = lk.from_socket
    seep = g.noise(g.comb(g.math('MULTIPLY', g.math('ADD', sx[0], sx[1]), 30.0), g.math('MULTIPLY', sd, 4.0), 0.0), 2.0, 2.0)
    dark = g.mix(g.math('MULTIPLY', wet, 0.72), src, cw.srgb((0.075, 0.05, 0.032)))
    g.link(dark, p.inputs['Base Color'])
    g.put(p, 'Roughness', g.math('MULTIPLY_ADD', wet, -0.72, 0.92))
    try:
        g.put(p, 'Coat Weight', g.math('MULTIPLY', wet, g.math('MULTIPLY_ADD', seep.outputs['Fac'], 0.5, 0.45)))
        g.put(p, 'Coat Roughness', 0.06)
    except KeyError: pass


def mat_puddle(kit, rain):
    """Muddy puddle water: glass, brown absorption; in rain, rings spread from every drop (two layers of cells)."""
    m, g = _mat(kit, 'ag_puddle'); tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry')
    pos = tc.outputs['Object']; sx = g.sep(pos); tv = g.value(0.0, 'ag_time')
    xy = g.comb(sx[0], sx[1], 0.0); hsum = None
    for scale, rate, ch in ((26.0, 1.5, 0), (19.0, 1.15, 1), (33.0, 1.8, 2)) if rain else ():
        v = g.voronoi(xy, scale, 'F1', '2D'); rr = g.sep(v.outputs['Color'])[ch]
        age = g.math('FRACT', g.math('MULTIPLY_ADD', tv, rate, g.math('MULTIPLY', rr, 7.0)))
        ring = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', v.outputs['Distance'], g.math('MULTIPLY', age, 0.6))), 11.0), clamp=True)
        amp = g.math('POWER', g.math('SUBTRACT', 1.0, age), 2.0)
        hh = g.math('MULTIPLY', ring, amp); hsum = hh if hsum is None else g.math('ADD', hsum, hh)
    zo, w = g.phase(0.25); nn = g.noise(g.comb(g.math('MULTIPLY', sx[0], 1.0), sx[1], zo), 14.0, 2.0, 0.5, '4D', w)
    h = g.math('MULTIPLY', nn.outputs['Fac'], 0.3) if hsum is None else g.math('ADD', hsum, g.math('MULTIPLY', nn.outputs['Fac'], 0.15))
    topm = g.math('GREATER_THAN', g.sep(geo.outputs['Normal'])[2], 0.7)
    bump = g.node('ShaderNodeBump', ins={'Strength': g.math('MULTIPLY', topm, 0.55 if rain else 0.12), 'Height': h, 'Distance': 0.002})
    glass = g.node('ShaderNodeBsdfGlass', ins={'Color': (1, 1, 1), 'Roughness': 0.02, 'IOR': 1.33}, distribution='GGX'); g.put(glass, 'Normal', bump)
    tr = g.node('ShaderNodeBsdfTransparent'); lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Shadow Ray'], mx.inputs[0]); g.link(glass, mx.inputs[1]); g.link(tr, mx.inputs[2])
    vol = g.node('ShaderNodeVolumeAbsorption', ins={'Color': cw.srgb((0.62, 0.47, 0.30)), 'Density': 26.0})
    o = _out(g, mx); g.link(vol, o.inputs['Volume'])
    return m, tv


def mat_rain(kit):
    m, g = _mat(kit, 'ag_rain')
    em = g.node('ShaderNodeEmission', ins={'Color': cw.srgb((0.86, 0.89, 0.93)), 'Strength': 1.15})
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader'); g.put(mx, 0, 0.62)
    g.link(em, mx.inputs[1]); g.link(tr, mx.inputs[2]); _out(g, mx); return m


def mat_flag(kit, name, field, trim):
    """Banner cloth from the film: field colour, gold border, gold disc (attributes fu, fv on the flag mesh)."""
    m, g = _mat(kit, name); u = g.attr('fu').outputs['Fac']; v = g.attr('fv').outputs['Fac']
    b = g.math('MAXIMUM', g.math('MAXIMUM', g.math('LESS_THAN', u, 0.08), g.math('GREATER_THAN', u, 0.93)),
               g.math('MAXIMUM', g.math('LESS_THAN', v, 0.11), g.math('GREATER_THAN', v, 0.89)))
    d = g.vmath('LENGTH', g.comb(g.math('SUBTRACT', u, 0.36), g.math('MULTIPLY', g.math('SUBTRACT', v, 0.5), 0.62), 0.0))
    disc = g.math('LESS_THAN', d, 0.15)
    col = g.mix(g.math('MAXIMUM', b, disc), cw.srgb(field), cw.srgb(trim))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.75})
    tr = g.node('ShaderNodeBsdfTranslucent', ins={'Color': col}); mx = g.node('ShaderNodeMixShader'); g.put(mx, 0, 0.18)
    g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2]); _out(g, mx); return m


def mat_legs(kit, name, base, metallic, mud_from=-0.030):
    """Leg material (object coordinates, origin at the hip): clean above, caked in mud below the knee."""
    m, g = _mat(kit, name); tc = g.node('ShaderNodeTexCoord'); z = g.sep(tc.outputs['Object'])[2]
    n = g.noise(tc.outputs['Object'], 90.0, 3.0)
    f = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', mud_from, g.math('MULTIPLY', n.outputs['Fac'], 0.012)), z), 120.0, clamp=True)
    clean = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': cw.srgb(base), 'Roughness': 0.32 if metallic else 0.8, 'Metallic': metallic})
    dirty = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': cw.srgb((0.13, 0.09, 0.06)), 'Roughness': 0.28})
    mx = g.node('ShaderNodeMixShader'); g.link(f, mx.inputs[0]); g.link(clean, mx.inputs[1]); g.link(dirty, mx.inputs[2]); _out(g, mx)
    return m


def materials(kit):
    S = lambda name, c, r=0.6, **k: cw.mat_simple(kit, name, c, r, **k)
    M = {'steel': S('ag_steel', (0.74, 0.76, 0.80), 0.30, metallic=1.0), 'steel_d': S('ag_steeld', (0.44, 0.45, 0.48), 0.40, metallic=1.0),
         'blue': S('ag_blue', FR['top'], 0.78), 'red': S('ag_red', EN['top'], 0.78), 'gold': S('ag_gold', FR['trim'], 0.38, metallic=0.55),
         'leather': S('ag_leather', (0.26, 0.16, 0.09), 0.7), 'wood': S('ag_wood', (0.42, 0.29, 0.17), 0.75), 'pale': S('ag_palewood', (0.82, 0.68, 0.48), 0.7),
         'skin': S('ag_skin', (0.88, 0.68, 0.54), 0.55, sss=0.1), 'hose': S('ag_hose', (0.40, 0.25, 0.15), 0.85), 'feather': S('ag_feather', (0.95, 0.93, 0.88), 0.7),
         'string': S('ag_string', (0.88, 0.85, 0.74), 0.6), 'mud': S('ag_mudcollar', (0.11, 0.075, 0.05), 0.22)}
    M['leg_fr'] = mat_legs(kit, 'ag_leg_fr', (0.74, 0.76, 0.80), 1.0)
    M['leg_en'] = mat_legs(kit, 'ag_leg_en', (0.74, 0.76, 0.80), 1.0)
    M['flag_fr'] = mat_flag(kit, 'ag_flag_fr', FR['top'], FR['trim']); M['flag_en'] = mat_flag(kit, 'ag_flag_en', EN['top'], EN['trim'])
    return M


# ============================================================================================ figures (about 0.17 m tall)
HIP = 0.068; LEG = 0.068
HAND_R = np.array([0.027, -0.028, 0.085]); HAND_L = np.array([0.011, 0.031, 0.072])


def soldier_body(bpy, M, team, snout=True, plume=None, name='ag_body'):
    """Armoured soldier (faces +X, origin on the ground between the feet): surcoat in the side's colour with a gold hem
    and a gold disc, steel arms and pauldrons, a bascinet (French: the pointed 'pig-face' visor)."""
    A = Acc(); cloth = 0; gold = 1; leath = 2; steel = 3; steeld = 4; plm = 5
    flat = lambda V: V * np.array([1.0, 0.86, 1.0])
    prof = [(0.049, 0.031), (0.060, 0.028), (0.076, 0.0235), (0.096, 0.026), (0.113, 0.025), (0.122, 0.013), (0.127, 0.005)]
    A.add(tube([(0, 0, z) for z, r in prof], [r for z, r in prof], 16), cloth, flat)
    A.add(torus(0.0305, 0.0027), gold, lambda V: flat(V + [0, 0, 0.0495]))
    A.add(torus(0.0236, 0.0028), leath, lambda V: flat(V + [0, 0, 0.0775]))
    A.add(tube([(0.0225, 0, 0.097), (0.0262, 0, 0.097)], [0.0085, 0.0085], 16), gold)
    A.add(tube([(-0.0262, 0, 0.097), (-0.0225, 0, 0.097)], [0.0085, 0.0085], 16), gold)
    for s in (-1, 1): A.add(ell((0, s * 0.0235, 0.116), (0.0135, 0.011, 0.009)), steel)
    A.add(tube([(0, -0.026, 0.114), (0.011, -0.032, 0.094), HAND_R + [-0.002, 0, 0.001]], [0.0074, 0.0067, 0.006], 8), steel)
    A.add(ell(HAND_R, (0.0078, 0.007, 0.007)), steeld)
    A.add(tube([(0, 0.026, 0.114), (0.005, 0.031, 0.093), HAND_L + [0, 0, 0.002]], [0.0074, 0.0067, 0.006], 8), steel)
    A.add(ell(HAND_L, (0.0075, 0.007, 0.007)), steeld)
    A.add(tube([(0, 0, 0.120), (0, 0, 0.133)], [0.022, 0.016], 12), steeld)
    A.add(ell((0, 0, 0.143), (0.0205, 0.019, 0.0225), 3), steel)
    A.add(tube([(-0.003, 0, 0.157), (-0.006, 0, 0.173)], [0.0115, 0.0004], 12), steel)
    if snout:
        A.add(tube([(0.009, 0, 0.141), (0.024, 0, 0.139), (0.037, 0, 0.1365)], [0.0135, 0.0088, 0.0018], 12), steel)
        A.add(tube([(0.0185, -0.0002, 0.1462), (0.0205, -0.0002, 0.1462)], [0.0105, 0.0105], 12, True), steeld,
              lambda V: V * np.array([1.0, 1.0, 0.16]) + np.array([0, 0, 0.1462 * 0.84]))   # eye slit band
    else:
        A.add(ell((0.011, 0, 0.140), (0.0125, 0.0165, 0.0145)), steel)
    mats = [M['blue'] if team == 'fr' else M['red'], M['gold'], M['leather'], M['steel'], M['steel_d']]
    if plume is not None:
        A.add(tube([(-0.006, 0, 0.162), (-0.020, 0, 0.178), (-0.038, 0, 0.177), (-0.050, 0, 0.167)], [0.004, 0.0062, 0.005, 0.0015], 8), plm)
        mats.append(M[plume])
    return A.mesh(bpy, name, mats)


def leg_mesh(bpy, M, mat='leg_fr', name='ag_leg'):
    A = Acc()
    A.add(tube([(0, 0, 0.004), (0, 0, -0.030), (0, 0, -0.057)], [0.0104, 0.0097, 0.0086], 10), 0)
    A.add(ell((0.0035, 0, -0.031), (0.0085, 0.0098, 0.0085)), 0)
    A.add(ell((0.007, 0, -0.0615), (0.0150, 0.0088, 0.0066)), 0)
    return A.mesh(bpy, name, [M[mat]], fix=True)


def polearm_mesh(bpy, M, name='ag_polearm'):
    """A poleaxe held at the right hand (origin), shaft slanted up and forward, axe blade and spike."""
    A = Acc(); a = np.array([-0.035, 0, -0.030]); b = np.array([0.058, 0, 0.150]); d = (b - a) / np.linalg.norm(b - a)
    A.add(tube([a, b], [0.0027, 0.0025], 8), 0)
    A.add(tube([b, b + d * 0.026], [0.0030, 0.0003], 8), 1)
    pp = np.array([d[2], 0, -d[0]]); c = b - d * 0.012 + pp * 0.010
    A.add(ell(c, (0.004, 0.0015, 0.004), 1), 1, lambda V: V)
    blade = [c + pp * 0.002 - d * 0.011, c + pp * 0.002 + d * 0.011, c + pp * 0.014 + d * 0.016, c + pp * 0.014 - d * 0.016]
    V = [p + [0, -0.0013, 0] for p in blade] + [p + [0, 0.0013, 0] for p in blade]
    A.add((np.array(V), [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]), 1)
    return A.mesh(bpy, name, [M['wood'], M['steel']], smooth=False)


def banner_pole_mesh(bpy, M, name='ag_bpole'):
    A = Acc(); A.add(tube([(-0.004, 0, -0.08), (0.004, 0, 0.245)], [0.0026, 0.0024], 8), 0)
    A.add(ell((0.004, 0, 0.249), (0.0055, 0.0055, 0.0055)), 1)
    return A.mesh(bpy, name, [M['wood'], M['gold']])


FLAG_NU, FLAG_NV = 14, 7


def flag_mesh(bpy, M, mat, name='ag_flag'):
    V = []; F = []; fu = []; fv = []
    for j in range(FLAG_NV):
        for i in range(FLAG_NU):
            V.append((0, 0, 0)); fu.append(i / (FLAG_NU - 1)); fv.append(j / (FLAG_NV - 1))
    for j in range(FLAG_NV - 1):
        for i in range(FLAG_NU - 1):
            a = j * FLAG_NU + i; F.append((a, a + 1, a + 1 + FLAG_NU, a + FLAG_NU))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.materials.append(M[mat])
    for an, arr in (('fu', fu), ('fv', fv)):
        at = me.attributes.new(an, 'FLOAT', 'POINT'); at.data.foreach_set('value', np.asarray(arr, np.float32))
    me.polygons.foreach_set('use_smooth', np.full(len(F), True)); me.update(); return me


def flag_pose(me, T, ph, w=0.075, h=0.046, wind=1.0):
    """Wave the flag: the hoist on the local Z axis (top at z 0), the fly streaming along local -X."""
    U = np.tile(np.linspace(0, 1, FLAG_NU), FLAG_NV); Vv = np.repeat(np.linspace(0, 1, FLAG_NV), FLAG_NU)
    notch = 0.22 * np.clip((U - 0.78) / 0.22, 0, 1) * (1 - np.abs(2 * Vv - 1))
    ue = U - notch
    x = -ue * w * (0.96 + 0.04 * np.sin(3.1 * T + ph))
    y = wind * 0.010 * ue * np.sin(7.0 * ue - 5.2 * T + ph) + 0.003 * ue * np.sin(13 * ue - 9 * T + 2 * ph)
    z = -Vv * h - 0.010 * ue * ue + 0.002 * np.sin(5 * ue - 4 * T + ph) * ue
    me.vertices.foreach_set('co', np.column_stack([x, y, z]).ravel().astype(np.float32)); me.update()


def archer_body(bpy, M, name='ag_archer'):
    """English archer (faces +X): red jack with a gold hem, brown hose, a kettle hat, a quiver on the back."""
    A = Acc(); red = 0; gold = 1; leath = 2; steel = 3; skin = 4; hose = 5; feath = 6
    flat = lambda V: V * np.array([1.0, 0.86, 1.0])
    for s in (-1, 1):
        A.add(tube([(0, s * 0.0118, 0.068), (0, s * 0.0118, 0.030), (0, s * 0.0118, 0.006)], [0.0085, 0.0078, 0.0068], 8), hose)
        A.add(ell((0.006, s * 0.0118, 0.004), (0.0125, 0.0078, 0.0058)), leath)
    prof = [(0.052, 0.028), (0.062, 0.026), (0.077, 0.022), (0.096, 0.0245), (0.112, 0.0235), (0.121, 0.012), (0.126, 0.005)]
    A.add(tube([(0, 0, z) for z, r in prof], [r for z, r in prof], 16), red, flat)
    A.add(torus(0.0278, 0.0026), gold, lambda V: flat(V + [0, 0, 0.0525]))
    A.add(torus(0.0222, 0.0028), leath, lambda V: flat(V + [0, 0, 0.0785]))
    A.add(tube([(0, -0.025, 0.113), (0.012, -0.031, 0.100), (0.022, -0.029, 0.096)], [0.0068, 0.0062, 0.0055], 8), red)
    A.add(ell((0.024, -0.028, 0.096), (0.0062, 0.0058, 0.0058)), skin)
    A.add(tube([(0, 0.025, 0.113), (0.006, 0.031, 0.093), (0.010, 0.031, 0.082)], [0.0068, 0.0062, 0.0055], 8), red)
    A.add(ell((0.011, 0.031, 0.080), (0.006, 0.0058, 0.0058)), skin)
    A.add(ell((0.002, 0, 0.139), (0.0165, 0.0158, 0.0175), 3), skin)
    A.add(ell((0, 0, 0.1465), (0.0186, 0.0186, 0.0128), 3), steel)
    A.add(tube([(0, 0, 0.1445), (0, 0, 0.1475)], [0.0285, 0.0285], 20), steel)
    A.add(tube([(-0.025, 0.010, 0.064), (-0.031, 0.014, 0.128)], [0.0072, 0.0078], 10), leath)
    A.add(ell((-0.031, 0.014, 0.133), (0.0085, 0.0085, 0.0065)), feath)
    return A.mesh(bpy, name, [M['red'], M['gold'], M['leather'], M['steel'], M['skin'], M['hose'], M['feather']])


A_HAND_R = np.array([0.024, -0.028, 0.096]); A_HAND_L = np.array([0.011, 0.031, 0.080])


def bow_mesh(bpy, M, name='ag_bow'):
    """Longbow at the left hand (origin), a little taller than the archer, belly curved forward, a straight string."""
    A = Acc(); z = np.linspace(-0.098, 0.108, 13); x = 0.011 * (1 - ((z - 0.005) / 0.103) ** 2)
    A.add(tube(np.column_stack([x, np.zeros_like(z), z]), 0.0013 + 0.0011 * (1 - np.abs(z / 0.105)), 6), 0)
    A.add(tube([(0, 0, -0.098), (0, 0, 0.108)], [0.0005, 0.0005], 4, False), 1)
    return A.mesh(bpy, name, [M['wood'], M['string']])


def mallet_mesh(bpy, M, name='ag_mallet'):
    A = Acc(); A.add(tube([(-0.008, 0, 0), (0.080, 0, 0)], [0.0023, 0.0023], 6), 0)
    A.add(tube([(0.083, 0, -0.0135), (0.083, 0, 0.0135)], [0.0082, 0.0082], 12), 0)
    return A.mesh(bpy, name, [M['wood']])


def stake_mesh(bpy, M, name='ag_stake'):
    """Sharpened stake, origin at the buried point, axis +Z, 0.21 m: both ends pointed, the top freshly cut (pale)."""
    A = Acc(); A.add(tube([(0, 0, 0.0), (0, 0, 0.022), (0, 0, 0.183)], [0.0004, 0.0066, 0.0064], 10), 0)
    A.add(tube([(0, 0, 0.183), (0, 0, 0.209)], [0.0064, 0.0003], 10), 1)
    return A.mesh(bpy, name, [M['wood'], M['pale']], fix=True)


def collar_mesh(bpy, M, name='ag_collar'):
    A = Acc(); A.add(torus(0.0118, 0.0042, 16, 8), 0, lambda V: V * np.array([1, 1, 0.45]))
    A.add(ell((0.0, 0.0, 0.0), (0.016, 0.016, 0.0028)), 0)
    return A.mesh(bpy, name, [M['mud']])


# ============================================================================================ the world
def make_cutter(bpy, land):
    """A solid outside the -Y face, below the terrain line: a BOOLEAN DIFFERENCE with it cuts figures and stakes flush on
    the face below the ground, so their buried parts show as sections in the soil."""
    nx = int(round(SX / RES)) + 1; xs = np.linspace(-SX / 2, SX / 2, nx); h = land.height(xs, np.full(nx, YF))
    xe = np.concatenate([[-SX / 2 - 0.5], xs, [SX / 2 + 0.5]]); he = np.concatenate([[h[0]], h, [h[-1]]])
    prof = [(xe[0], -DEPTH - 0.6), (xe[-1], -DEPTH - 0.6)] + list(zip(xe[::-1], he[::-1]))
    y0 = YF - 0.0007; y1 = YF - 0.6; n = len(prof)
    V = [(x, y0, z) for x, z in prof] + [(x, y1, z) for x, z in prof]
    F = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    me = bpy.data.meshes.new('ag_cutter'); me.from_pydata(V, [], F); _outward(me); me.update()
    return bpy.data.objects.new('ag_cutter', me)       # not linked: an operand only


def clip_front(ob, cutter):
    md = ob.modifiers.new('ag_front', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cutter; md.solver = os.environ.get('AG_SOLVER', 'EXACT')
    try: md.use_self = True
    except Exception: pass
    return md


class Rain:
    """Rain streaks over the block (one mesh, camera-facing quads rebuilt every frame from T; loop-free, deterministic)."""
    def __init__(self, kit, land, n=3800, seed=5, speed=3.4, length=0.085, width=0.0012, top=1.7, wind=(0.55, 0.22)):
        bpy = kit.bpy; rng = np.random.default_rng(seed); self.n = n
        self.x0 = rng.uniform(-SX / 2, SX / 2, n); self.y0 = rng.uniform(-SY / 2, SY / 2, n)
        self.sp = speed * rng.uniform(0.85, 1.15, n); self.wind = np.array(wind); self.top = top
        land_x = self.x0 + wind[0] * top / speed; land_y = self.y0 + wind[1] * top / speed
        self.floor = land.height(np.clip(land_x, -SX / 2, SX / 2), np.clip(land_y, -SY / 2, SY / 2))
        self.H = top - self.floor; self.off = rng.uniform(0, 1, n); self.len = length * rng.uniform(0.8, 1.2, n); self.w = width
        F = [(4 * k, 4 * k + 1, 4 * k + 2, 4 * k + 3) for k in range(n)]
        me = bpy.data.meshes.new('ag_rain'); me.from_pydata([(0, 0, 0)] * (4 * n), [], F); me.materials.append(mat_rain(kit))
        self.me = me; self.ob = obj(bpy, kit, 'ag_rain', me)
        for a in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'): setattr(self.ob, a, False)
    def update(self, T, cam):
        d = (T * self.sp + self.off * self.H) % self.H; tfall = d / self.sp
        P = np.column_stack([self.x0 + self.wind[0] * tfall, self.y0 + self.wind[1] * tfall, self.top - d])
        dirv = np.column_stack([np.full(self.n, self.wind[0]), np.full(self.n, self.wind[1]), -self.sp]); dirv /= np.linalg.norm(dirv, axis=1)[:, None]
        view = np.asarray(cam, float)[None, :] - P; side = np.cross(dirv, view); side /= np.linalg.norm(side, axis=1)[:, None] + 1e-9
        dist = np.linalg.norm(view, axis=1); wv = self.w * np.clip(dist / 2.0, 0.5, 2.0)[:, None]
        tail = P - dirv * self.len[:, None]
        V = np.stack([P - side * wv, P + side * wv, tail + side * wv * 0.4, tail - side * wv * 0.4], 1)
        inside = (np.abs(P[:, 0]) < SX / 2) & (np.abs(P[:, 1]) < SY / 2)
        V[~inside] = 0.0
        self.me.vertices.foreach_set('co', V.reshape(-1).astype(np.float32)); self.me.update()


def build_world(bpy, kit, rain):
    def zones(x, y, h): return {'path': mask(x, y)}
    land = cw.block(kit, size=(SX, SY), depth=DEPTH, strata=STRATA, top=top, water=None, seed=15, season='autumn', zones=zones,
                    res=RES, grass=1.0, grass_height=0.8, tree_spots=tree_spots(), tree_kinds=('round', 'tall', 'cone'),
                    boulders=0, flowers=0.0, under=False, sway=1.5 if rain else 1.0, name='ag_block')
    me = land.objects['top'].data; co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    at = me.attributes.new('ag_fur', 'FLOAT', 'POINT'); at.data.foreach_set('value', furrow(co[:, 0], co[:, 1]).astype(np.float32))
    me.materials[0] = mat_mud(kit, rain)
    patch_strata(kit, land.mats['strata'])
    e = 0.0015; zb = -0.07; bx = [(-SX / 2 + e, -SY / 2 + e), (SX / 2 - e, -SY / 2 + e), (SX / 2 - e, SY / 2 - e), (-SX / 2 + e, SY / 2 - e)]
    WV = [(x, y, zb) for x, y in bx] + [(x, y, LV) for x, y in bx]
    WF = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    pm, tv = mat_puddle(kit, rain)
    cw.mk_mesh(bpy, 'ag_puddles', WV, WF, [pm], None, False, kit.coll)
    return land, tv


def light(kit, land, mood):
    if mood == 'rain':
        cw.studio(kit, color=(0.47, 0.50, 0.53), key_az=-115, key_el=62, key=0.9, angle=35, fill=1.0, land=land)
        cw.mat_gradient_bg(kit, (0.56, 0.60, 0.64), (0.34, 0.37, 0.40), 1.0, (0.80, 0.85, 0.92), 1.25)
    else:
        cw.studio(kit, color=(0.55, 0.57, 0.58), key_az=-125, key_el=50, key=1.6, angle=22, fill=1.0, land=land, shadows=0.22)
        cw.mat_gradient_bg(kit, (0.68, 0.70, 0.72), (0.44, 0.46, 0.47), 1.0, (0.86, 0.88, 0.92), 1.2)


def settings(samples=64, exposure=0.0):
    return {'samples': samples, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'max_bounces': 8, 'clamp_indirect': 6.0, 'adaptive_min_samples': 16, 'denoising_prefilter': 'ACCURATE', 'exposure': exposure}


def set_dof(cam, fstop, dist):
    d = cam.ob.data
    if fstop: d.dof.use_dof = True; d.dof.aperture_fstop = fstop; d.dof.focus_distance = dist
    else: d.dof.use_dof = False


# ============================================================================================ the English line (both inserts)
NSTAKE = 22
STAKE_LEAN = math.radians(36)


def stake_base(k): return 1.50 + 0.024 * (k % 2), YF + k * 0.098


def stake_times(k):
    """Three mallet blows per stake, a wave from the near face outward, first blow on 'hammered', all done on 'them.'"""
    t0 = W('l07', 'hammered'); tl = W('l07', 'them', end=True) - 0.70
    t = t0 + (tl - t0) * k / (NSTAKE - 1); return [t, t + 0.34, t + 0.68]


D0, DSTEP = 0.032, 0.021


def stake_depth(T, k, done=False):
    if done: return D0 + 3 * DSTEP
    return D0 + sum(DSTEP * ease5((T - s) / 0.06) for s in stake_times(k))


class English:
    def __init__(self, bpy, kit, M, cutter, insert):
        self.insert = insert; self.stakes = []; self.archers = []; self.men = []
        sm = stake_mesh(bpy, M); am = archer_body(bpy, M); bm = bow_mesh(bpy, M); mm = mallet_mesh(bpy, M)
        for k in range(NSTAKE):
            xb, yb = stake_base(k); s = obj(bpy, kit, f'ag_stake{k}', sm)
            if k == 0: clip_front(s, cutter)
            self.stakes.append((s, xb, yb, g1(xb, yb)))
            ax, ay = xb + 0.058, (yb + 0.032 if k == 0 else yb)
            a = obj(bpy, kit, f'ag_archer{k}', am); az = g1(ax, ay) - 0.004
            a.location = (ax, ay, az); a.rotation_euler = (0, 0, math.pi + (0.06 if k % 3 == 1 else -0.04 if k % 3 == 2 else 0))
            bow = obj(bpy, kit, f'ag_bow{k}', bm, a); bow.location = tuple(A_HAND_L)
            mal = obj(bpy, kit, f'ag_mallet{k}', mm)
            self.archers.append({'ob': a, 'bow': bow, 'mal': mal, 'x': ax, 'y': ay, 'z': az, 'k': k, 'yaw': a.rotation_euler.z})
        bodies = [soldier_body(bpy, M, 'en', snout=False, plume=None, name='ag_enbody'), soldier_body(bpy, M, 'en', snout=False, plume='gold', name='ag_enbody_p')]
        lm = leg_mesh(bpy, M, 'leg_en', 'ag_enleg'); pm = polearm_mesh(bpy, M); bpm = banner_pole_mesh(bpy, M)
        ys = np.linspace(YF + 0.10, 0.58, 11)
        for j, y in enumerate(ys):
            banner = j in (2, 8)
            b = obj(bpy, kit, f'ag_en{j}', bodies[1 if j % 4 == 1 else 0])
            legs = [obj(bpy, kit, f'ag_en{j}_l{s}', lm, b) for s in (0, 1)]
            for L, s in zip(legs, (-1, 1)): L.location = (0, s * 0.0125, HIP)
            if banner:
                w = obj(bpy, kit, f'ag_en{j}_pole', bpm, b); w.location = tuple(HAND_R)
                fm = flag_mesh(bpy, M, 'flag_en', f'ag_enflag{j}'); fl = obj(bpy, kit, f'ag_en{j}_flag', fm, w); fl.location = (0.0, 0, 0.243)
            else:
                w = obj(bpy, kit, f'ag_en{j}_arm', pm, b); w.location = tuple(HAND_R); fm = None
            self.men.append({'ob': b, 'legs': legs, 'w': w, 'flag': fm, 'y': float(y) + 0.012 * math.sin(j * 2.3), 'j': j, 'ph': j * 1.7})

    def pose(self, T):
        A = self.insert == 'A'
        for k, (s, xb, yb, gz) in enumerate(self.stakes):
            d = stake_depth(T, k, done=not A)
            ax = np.array([-math.sin(STAKE_LEAN), 0.0, math.cos(STAKE_LEAN)])
            p = np.array([xb, yb, gz]) - ax * d
            s.location = tuple(p); s.rotation_euler = (0, -STAKE_LEAN, 0.04 * math.sin(k * 1.9))
        t_close = W('l07', 'close'); t_shoot = W('l07', 'shoot')
        for a in self.archers:
            k = a['k']; ob = a['ob']; yaw = a['yaw']; xb, yb = stake_base(k); gz = self.stakes[k][3]
            cy, sy_ = math.cos(yaw), math.sin(yaw)
            hand = np.array([a['x'] + cy * A_HAND_R[0] - sy_ * A_HAND_R[1], a['y'] + sy_ * A_HAND_R[0] + cy * A_HAND_R[1], a['z'] + A_HAND_R[2]])
            if A:
                ts = stake_times(k); ax = np.array([-math.sin(STAKE_LEAN), 0.0, math.cos(STAKE_LEAN)])
                def tip(j):
                    d = D0 + j * DSTEP; return np.array([xb, yb, gz]) + ax * (0.209 - d)
                def aim(j):
                    v = tip(j) - hand; return math.atan2(-v[2], v[0] * cy + v[1] * sy_), float(np.linalg.norm(v))
                (p0, l0), (p1, l1), (p2, l2) = aim(0), aim(1), aim(2)
                rest = 1.05; up = -2.25
                K = [(ts[0] - 0.75, rest), (ts[0] - 0.30, p0 + up), (ts[0] - 0.12, p0 + up - 0.12), (ts[0], p0),
                     (ts[0] + 0.17, p1 + up), (ts[1] - 0.10, p1 + up - 0.10), (ts[1], p1),
                     (ts[1] + 0.17, p2 + up), (ts[2] - 0.10, p2 + up - 0.10), (ts[2], p2), (ts[2] + 0.55, rest)]
                pitch = keys(T, K); L = keys(T, [(ts[0] - 0.2, l0), (ts[1] - 0.2, l1), (ts[2] - 0.2, l2)])
                a['mal'].hide_render = False
                a['mal'].location = tuple(hand); a['mal'].rotation_euler = (0, pitch, yaw)
                sc = min(1.75, max(0.9, L / 0.083)); a['mal'].scale = (sc, 1, 1)
                lean = 0.10 * max(0.0, math.sin(min(1.0, max(0.0, (T - ts[0] + 0.3) / 1.3)) * math.pi))
                rise = ease((T - t_close) / (t_shoot - t_close + 0.25))
            else:
                a['mal'].hide_render = True; lean = 0.0; rise = 1.0
            ph = k * 0.37
            ob.rotation_euler = (0.0, lean - 0.10 * rise, yaw)
            a['bow'].rotation_euler = (0.0, -0.45 * rise + 0.02 * math.sin(1.3 * T + ph), 0.0)
        t_move = W('l07', 'moved'); t_army = W('l07', 'forward', end=True) + 0.4
        for m in self.men:
            j = m['j']; ph = m['ph']
            if A:
                u = (T - t_move - 0.05 * j) / (t_army - t_move); walk = ease(u); moving = 0.0 < u < 1.0
            else:
                walk = 1.0; moving = False
            x = 2.02 - 0.15 * walk; y = m['y']; z = g1(x, y) - 0.006
            phase = 2 * math.pi * (0.15 * walk / 0.11) + ph
            m['ob'].location = (x, y, z + (0.003 * abs(math.cos(phase)) if moving else 0.0))
            m['ob'].rotation_euler = (0.03 * math.sin(phase) if moving else 0.0, 0.0, math.pi)
            sw = 0.38 * math.sin(phase) if moving else 0.0
            m['legs'][0].rotation_euler = (0, sw, 0); m['legs'][1].rotation_euler = (0, -sw, 0)
            if m['flag'] is not None:
                m['w'].rotation_euler = (0.0, -0.12, 0.0); flag_pose(m['flag'], T, ph, wind=1.0)
            else:
                m['w'].rotation_euler = (0.0, -0.15, 0.0)


# ============================================================================================ the French column (B)
NF, NR = 12, 5


class French:
    """The French on foot: NF files by NR ranks, file 0 on the -Y cut face. Pace and sinking are timed on the words:
    sunk to the ankle on 'advanced', to the knee on 'knees'; the woods close the files together from 'woods'."""
    T0 = 86.0

    def __init__(self, bpy, kit, M, cutter):
        rng = np.random.default_rng(1415); self.M = M; self.sol = []
        self.t_knees = W('l10', 'knees'); self.t_adv = W('l10', 'advanced'); self.t_swing = W('l11', 'swing')
        dt = 1.0 / 480.0; self.ts = np.arange(self.T0, 102.0, dt)
        v = 0.155 * (1 - 0.72 * cw.smooth(86.9, self.t_knees + 0.8, self.ts)) * (1 - 0.45 * cw.smooth(W('l11', 'woods'), W('l11', 'packed'), self.ts))
        self.X = np.cumsum(v) * dt; self.X += -0.85 - np.interp(86.703, self.ts, self.X)
        stride = 0.125 * (1 - 0.40 * cw.smooth(86.9, self.t_knees, self.ts))
        self.PH = np.cumsum(2 * np.pi * v / stride) * dt
        bodies = [soldier_body(bpy, M, 'fr', True, None, 'ag_frbody'), soldier_body(bpy, M, 'fr', True, 'gold', 'ag_frbody_p'),
                  soldier_body(bpy, M, 'fr', True, 'blue', 'ag_frbody_b')]
        lm = leg_mesh(bpy, M, 'leg_fr', 'ag_frleg'); pm = polearm_mesh(bpy, M, 'ag_frpole'); cm = collar_mesh(bpy, M); bpm = banner_pole_mesh(bpy, M, 'ag_frbpole')
        for r in range(NR):
            for f in range(NF):
                face = f == 0; banner = (r, f) in ((1, 3), (1, 8))
                b = obj(bpy, kit, f'ag_fr{r}_{f}', bodies[int(rng.integers(0, 3))])
                lw = 0.0052 if face else 0.0125
                legs = []
                for s in (-1, 1):
                    L = obj(bpy, kit, f'ag_fr{r}_{f}_l{s}', lm, b); L.location = (0, s * lw, HIP); legs.append(L)
                    if face: clip_front(L, cutter)
                cols = [obj(bpy, kit, f'ag_fr{r}_{f}_c{s}', cm) for s in (0, 1)]
                if banner:
                    w = obj(bpy, kit, f'ag_fr{r}_{f}_pole', bpm, b); w.location = tuple(HAND_R)
                    fm = flag_mesh(bpy, M, 'flag_fr', f'ag_frflag{r}{f}'); fl = obj(bpy, kit, f'ag_fr{r}_{f}_flag', fm, w); fl.location = (0.0, 0, 0.243)
                else:
                    w = obj(bpy, kit, f'ag_fr{r}_{f}_arm', pm, b); w.location = tuple(HAND_R); fm = None
                self.sol.append({'r': r, 'f': f, 'ob': b, 'legs': legs, 'cols': cols, 'w': w, 'flag': fm, 'lw': lw, 'face': face,
                                 'dx': 0.0 if face else float(rng.uniform(-0.022, 0.022)), 'dy': 0.0 if face else float(rng.uniform(-0.012, 0.012)),
                                 'ph': float(rng.uniform(0, 2 * np.pi)), 'sk': float(rng.uniform(-0.004, 0.004)), 'wph': float(rng.uniform(0, 6.28)),
                                 'stuck': face and r == 3})

    def Xf(self, T): return float(np.interp(T, self.ts, self.X))
    def Ph(self, T): return float(np.interp(T, self.ts, self.PH))
    def dr(self, T): return 0.19 - 0.06 * float(cw.smooth(90.0, 99.0, T))

    @staticmethod
    def yfile(f, x):
        b = float(near_bump(x)); yl = YF + min(1.0, b * 8.0) * (0.58 * b + 0.07); yu = float(y_far(x)) - 0.085
        return yl + (yu - yl) * f / (NF - 1)

    def sink(self, T): return 0.013 + 0.031 * float(cw.smooth(self.t_adv - 0.4, self.t_knees, T))

    def place(self, T):
        """x, y for every soldier at T (files never overlap: each rank stays behind the one in front)."""
        out = {}; ts = self.t_knees
        for s in self.sol:
            r, f = s['r'], s['f']; Tw = T
            if s['stuck'] and T > ts - 0.7: Tw = ts - 0.7 + 0.7 * (1 - math.exp(-(T - (ts - 0.7)) / 0.45))
            x = self.Xf(Tw) - r * self.dr(T) + s['dx']
            if r > 0: x = min(x, out[(r - 1, f)][0] - 0.068)
            out[(r, f)] = (x, self.yfile(f, x) + s['dy'], Tw)
        return out

    def pose(self, T):
        from mathutils import Euler, Vector
        P = self.place(T); sk0 = self.sink(T); ts = self.t_knees
        jost = float(cw.smooth(self.t_swing - 0.35, self.t_swing - 0.05, T)) * (1 - float(cw.smooth(self.t_swing + 0.6, self.t_swing + 1.3, T)))
        for s in self.sol:
            x, y, Tw = P[(s['r'], s['f'])]
            y2 = self.yfile(s['f'], x + 0.02); yaw = math.atan2(y2 - self.yfile(s['f'], x), 0.02) if not s['face'] or y > YF + 1e-4 else 0.0
            tired = float(cw.smooth(86.9, ts, T))
            ph = self.Ph(Tw) + s['ph']
            amp = 0.46 * (1 - 0.42 * tired)
            sink = sk0 + s['sk']; roll = 0.045 * math.sin(ph); pitch = 0.05 + 0.10 * tired
            if s['stuck'] and T > ts - 0.2:
                k = T - (ts - 0.2); sink += 0.007 * min(1.0, k / 0.6)
                roll += 0.16 * math.sin(2 * math.pi * 2.3 * k) * math.exp(-k / 1.1); pitch += 0.10 * min(1.0, k / 0.5)
                amp *= math.exp(-k / 0.5)
            gz = g1(x, y); z = gz - sink + 0.0035 * abs(math.cos(ph))
            s['ob'].location = (x, y, z); s['ob'].rotation_euler = (roll, pitch, yaw)
            sw = amp * math.sin(ph); R = Euler((roll, pitch, yaw), 'XYZ').to_matrix(); loc = Vector((x, y, z))
            for L, sgn, ang, col in zip(s['legs'], (-1, 1), (sw, -sw), s['cols']):
                L.rotation_euler = (0, ang, 0)
                hip = loc + R @ Vector((0, sgn * s['lw'], HIP)); dv = R @ (Euler((0, ang, 0), 'XYZ').to_matrix() @ Vector((0, 0, -1)))
                g = g1(hip.x, hip.y); depth = hip.z - g
                if dv.z < -0.2 and 0 < depth / -dv.z < LEG:
                    p = hip + dv * (depth / -dv.z); col.location = (p.x, p.y, g + 0.001); col.hide_render = False
                    col.rotation_euler = (0, 0, yaw); cs = 0.9 + 0.25 * min(1.0, (sink - 0.01) / 0.035); col.scale = (cs, cs, 1)
                else:
                    col.hide_render = True
            if s['flag'] is not None:
                s['w'].rotation_euler = (0.0, -0.10 + 0.04 * math.sin(ph), 0.0); flag_pose(s['flag'], T, s['wph'], wind=1.2)
            else:
                jx = jost * 0.30 * math.sin(2 * math.pi * 3.2 * T + s['wph']); jy = -jost * 0.35 * (0.5 + 0.5 * math.sin(2 * math.pi * 2.1 * T + 2 * s['wph']))
                s['w'].rotation_euler = (jx + 0.03 * math.sin(ph), jy - 0.05 * tired, 0.0)
