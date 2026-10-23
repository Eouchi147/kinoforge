"""The Gold Mine (Cutaway showcase series, film 5; 20 s, 9:16, night).

A rocky mountain block under stars and a big moon, pines on its flanks, a timber mine entrance with a lantern. The -Y cut
face opens the mountain: three lantern-lit galleries on timber sets, a ladder shaft, rails with an ore cart, miners with
picks and helmet lamps, a cavern with a still pool and a bat colony. Warm lantern light against cold blue rock.
Story: a miner walks into the mine at night (beginning); inside, the work goes on as the camera cranes down the face,
until the deepest miner's pick strikes the gold vein in a burst of sparks (middle); the ring of it wakes the bats, which
burst out of the cavern and pour out of the mine entrance across the moon (end).

Kit: ../../../styles/cutaway/cutaway.py and cinematic/extras.py (imported, never edited). Everything new is here.
Shots (SHOTS timeline): night 0-6 s, descent 6-14 s, flight 14-20 s. Event times: NOTES.md.
"""
import math
import os
import sys

import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(here, '..', '..', '..', '..'))
for p in (os.path.join(ROOT, 'films', 'styles', 'cutaway'), os.path.join(ROOT, 'films', 'styles', 'cutaway', 'cinematic')):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import extras as ex  # noqa: E402

G = cw.G
srgb = cw.srgb
SHOTS = [{'name': 'night', 'dur': 6.0}, {'name': 'descent', 'dur': 8.0}, {'name': 'flight', 'dur': 6.0}]
DURATION = sum(s['dur'] for s in SHOTS)
FRAMES = {'night': 30, 'descent_top': 168, 'descent_mid': 222, 'strike': 266, 'bats': 300, 'flight': 400, 'end': 470}
SETTINGS = {'samples': 20, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Medium High Contrast',
            'exposure': 0.9, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 3.0, 'adaptive_min_samples': 8,
            'denoising_prefilter': 'FAST'}

SX = SY = 2.6
DEPTH = 2.2
FY = -SY / 2                      # the -Y cut face plane (the camera side of the interior)
WARM = (1.0, 0.60, 0.26)
MOON_COL = (0.62, 0.74, 1.0)
STRIKES = (8.6, 9.8, 11.0)        # the gold miner's pick blows (the last one finds the gold)
T_GOLD = STRIKES[-1]
T_BATS = 11.45                    # the bats wake
T_OUT = 14.15                     # the bats pour out of the entrance (shot 3)

# interior layout on the -Y face (u = x, z = height); galleries: floor z, height 2r, centre-line u0..u1
R_G = 0.08
SHAFT_U, SHAFT_W = 0.10, 0.065
G1 = dict(u0=-0.82, u1=0.22, zf=0.00)
G2 = dict(u0=-0.38, u1=0.18, zf=-0.62)
G3 = dict(u0=-0.22, u1=0.30, zf=-1.30)
CAVE = dict(u=0.14, z=-1.66, a=0.27, b=0.18, d=0.26)
POOL_LEVEL = -1.755
D_G = 0.17                        # gallery depth into the rock


# =============================================================================================== terrain
def _sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def bench_s(x, y):
    xb = -0.84 - 0.30 * (y + SY / 2)          # the yard in front of the entrance narrows toward the back
    return _sstep(xb, xb + 0.17, x)

def top(x, y):
    s = bench_s(x, y)
    mass = 0.36 + 0.86 * np.exp(-((x - 0.40) ** 2 / 1.3 + (y - 0.55) ** 2 / 1.6))
    crag = 0.06 * cw.fbm(x, y, 17, 4, 1.6) + 0.025 * cw.fbm(x, y, 23, 3, 5.0)
    return s * (mass + crag) + (1 - s) * (-0.004 + 0.003 * cw.fbm(x, y, 5, 2, 6.0))


# =============================================================================================== small mesh helpers
def quad(a, b, c, d): return [a, b, c, d], [(0, 1, 2, 3)]

def W(u, d, z): return (u, FY + d, z)            # face coordinates -> world (the -Y face)

def box(c, s):
    (x, y, z), (a, b, h) = c, s
    return cw._box(x - a / 2, y - b / 2, z - h / 2, x + a / 2, y + b / 2, z + h / 2)

def mk(kit, name, pieces, mats, smooth=False):
    return ex.part(kit, name, pieces, mats, smooth=smooth)

def cam_only(ob):
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
    return ob


# =============================================================================================== materials
def mat_rock_in(kit):
    """Inside rock of the galleries: cold blue-grey with grain and chisel marks (warm only where the lanterns reach)."""
    key = ('gm', 'rock')
    if key in kit.mats: return kit.mats[key]
    m = cw._new_mat(kit.bpy, 'gm_rock'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    n = g.noise(tc.outputs['Object'], 60.0, 4.0); n2 = g.noise(tc.outputs['Object'], 9.0, 3.0)
    col = g.mix(n2.outputs['Fac'], srgb((0.20, 0.21, 0.25)), srgb((0.40, 0.41, 0.46)))
    col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.45), col, srgb((0.08, 0.08, 0.10)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.85})
    vo = g.voronoi(tc.outputs['Object'], 45.0, 'F1')
    b = g.node('ShaderNodeBump', ins={'Strength': 0.7, 'Height': g.math('ADD', vo.outputs['Distance'], g.math('MULTIPLY', n.outputs['Fac'], 0.6)), 'Distance': 0.004})
    g.put(p, 'Normal', b); cw._finish(g, p); kit.mats[key] = m; return m

def mat_wood(kit):
    key = ('gm', 'wood')
    if key in kit.mats: return kit.mats[key]
    m = cw._new_mat(kit.bpy, 'gm_wood'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (40.0, 40.0, 4.0)), 3.0, 4.0)
    col = g.mix(n.outputs['Fac'], srgb((0.26, 0.16, 0.09)), srgb((0.48, 0.32, 0.18)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.8}); cw._finish(g, p); kit.mats[key] = m; return m

def mat_water_pool(kit):
    m = cw._new_mat(kit.bpy, 'gm_pool'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); tv = ex.time_value(kit, g, 'gm_pool_t')
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (1, 1, 0)), 38.0, 2.0, 0.5, '4D', g.math('MULTIPLY', tv, 0.35))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.55, 0.80, 0.90)), 'Roughness': 0.03, 'IOR': 1.33, 'Transmission Weight': 1.0})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.25, 'Height': n.outputs['Fac'], 'Distance': 0.002}); g.put(p, 'Normal', b)
    lp = g.node('ShaderNodeLightPath'); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Shadow Ray'], mx.inputs[0]); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2])
    v = g.node('ShaderNodeVolumeAbsorption', ins={'Color': srgb((0.20, 0.62, 0.70)), 'Density': 1.6})
    cw._finish(g, mx, v); return m


# =============================================================================================== night sky, moon, floor
def night(kit, land):
    bpy = kit.bpy
    wd = bpy.data.worlds.new('gm_world'); bpy.context.scene.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree; nt.nodes.clear(); g = G(nt, kit); tv = ex.time_value(kit, g, 'gm_sky_t')
    tc = g.node('ShaderNodeTexCoord'); d = g.vmath('NORMALIZE', tc.outputs['Generated']); dz = g.sep(d)[2]
    el = g.math('MAXIMUM', dz, 0.0)
    sky = g.mix(g.math('POWER', el, 0.45), srgb((0.10, 0.14, 0.27)), srgb((0.010, 0.016, 0.045)))
    # stars: one-pixel points, varied brightness, twinkling, fading into the horizon glow
    vo = g.voronoi(g.vmath('SCALE', d, scale=170.0), 1.0, 'F1')
    pt = g.math('LESS_THAN', vo.outputs['Distance'], 0.12)
    bright = g.math('POWER', g.sep(vo.outputs['Color'])[0], 6.0)
    tw = g.noise(g.vmath('SCALE', d, scale=400.0), 1.0, 0.0, 0.5, '4D', g.math('MULTIPLY', tv, 2.2))
    star = g.math('MULTIPLY', g.math('MULTIPLY', pt, bright), g.math('ADD', 0.35, g.math('MULTIPLY', tw.outputs['Fac'], 1.3)))
    star = g.math('MULTIPLY', star, g.math('MULTIPLY', el, 12.0, clamp=True))
    vo2 = g.voronoi(g.vmath('SCALE', d, scale=60.0), 1.0, 'F1')          # a few bigger, brighter stars
    pt2 = g.math('MULTIPLY', g.math('LESS_THAN', vo2.outputs['Distance'], 0.07), g.math('GREATER_THAN', g.sep(vo2.outputs['Color'])[1], 0.82))
    star = g.math('ADD', star, g.math('MULTIPLY', pt2, g.math('MULTIPLY', el, 8.0, clamp=True)))
    col = g.mix(g.math('MULTIPLY', star, 3.0), sky, srgb((0.85, 0.90, 1.0)), 'ADD')
    bg_cam = g.node('ShaderNodeBackground', ins={'Color': col, 'Strength': 1.0})
    bg_light = g.node('ShaderNodeBackground', ins={'Color': srgb((0.30, 0.40, 0.75)), 'Strength': 0.07})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bg_light, mx.inputs[1]); g.link(bg_cam, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
    # moonlight from behind-left (rims the peak, the pines and the block edges), a soft cool fill on the camera side
    moon = cw._sun(kit, 128.0, 34.0, 1.6, 0.6, MOON_COL, 'gm_moonlight')
    ld = bpy.data.lights.new('gm_fill', 'AREA'); ld.size = 6.0; ld.shape = 'DISK'; ld.energy = 260.0; ld.color = (0.55, 0.66, 1.0)
    fo = bpy.data.objects.new('gm_fill', ld); kit.coll.objects.link(fo); fo.location = tuple(np.array((0, 0, -0.5)) + ex.sph(-75, 22) * 9.0)
    ex.look_at(fo, (0, 0, -0.5)); fo.visible_camera = False; fo.visible_glossy = False
    # floor: dark ground under the mountain that melts into the night horizon
    m = cw._new_mat(bpy, 'gm_floor'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    r = g.vmath('LENGTH', g.vmath('MULTIPLY', tc.outputs['Object'], (1, 1, 0)))
    far = g.math('MULTIPLY', g.math('SUBTRACT', r, 7.0), 1 / 22.0, clamp=True)
    p = g.node('ShaderNodeEmission', ins={'Color': srgb((0.022, 0.026, 0.040)), 'Strength': 1.0})   # unlit: the side lights must not pool on it
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.10, 0.14, 0.27)), 'Strength': 0.45})
    mx = g.node('ShaderNodeMixShader'); g.link(g.math('POWER', far, 0.6), mx.inputs[0]); g.link(p, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx)
    cw._plane(kit, 'gm_floor', 60, -DEPTH - 0.0005, m)
    return {'moonlight': moon}

def ridges(kit):
    """Two bands of far mountains around the back of the block (camera rays only): depth in the night."""
    bpy = kit.bpy
    for k, (R, hmax, col, seed) in enumerate(((16.0, 3.4, (0.045, 0.060, 0.115), 3), (26.0, 6.5, (0.070, 0.090, 0.165), 7))):
        m = cw._new_mat(bpy, f'gm_ridge{k}'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); u, v, _ = g.sep(tc.outputs['UV'])
        n = g.noise(g.comb(g.math('MULTIPLY', u, 9.0 + 5 * k), float(seed), 0.0), 1.0, 5.0, 0.55)
        ridge = g.math('ADD', 0.35, g.math('MULTIPLY', n.outputs['Fac'], 0.75))
        inside = g.math('LESS_THAN', v, ridge)
        e = g.node('ShaderNodeEmission', ins={'Color': srgb(col), 'Strength': 1.0}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
        g.link(inside, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx)
        V = []; F = []; UV = []; n_ = 64
        for i in range(n_ + 1):
            a = 2 * math.pi * i / n_
            for zz in (-DEPTH, -DEPTH + hmax):
                V.append((R * math.cos(a), R * math.sin(a), zz))
        for i in range(n_): F.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
        ob = cw.mk_mesh(bpy, f'gm_ridge{k}', V, F, [m], None, False, kit.coll)
        uvl = ob.data.uv_layers.new(name='UVMap')
        for poly in ob.data.polygons:
            for li in poly.loop_indices:
                vi = ob.data.loops[li].vertex_index; uvl.data[li].uv = ((vi // 2) / n_, float(vi % 2))
        cam_only(ob)

class Moon:
    """A big moon and a few moonlit cloud wisps, set at 'infinity' (always 40 m from the camera along a fixed direction
    per shot, so a camera move does not slide it like a near object). Camera rays only."""
    def __init__(self, kit):
        bpy = kit.bpy; self.kit = kit
        m = cw._new_mat(bpy, 'gm_moon'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
        n = g.noise(tc.outputs['Object'], 2.2, 5.0, 0.6); n2 = g.voronoi(tc.outputs['Object'], 3.0, 'F1')
        mare = g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.45), 2.5, clamp=True)
        lum = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ADD', g.math('MULTIPLY', mare, 0.35), g.math('MULTIPLY', g.math('LESS_THAN', n2.outputs['Distance'], 0.12), 0.12)), 1.0))
        e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.96, 0.95, 0.88))}); g.put(e, 'Strength', g.math('MULTIPLY', lum, 9.0)); cw._finish(g, e)
        th = np.linspace(0, 2 * math.pi, 49)[:-1]; R = 1.05
        V = [(0, 0, 0)] + [(R * math.cos(a), R * math.sin(a), 0) for a in th]; F = [(0, 1 + i, 1 + (i + 1) % 48) for i in range(48)]
        self.disc = cam_only(cw.mk_mesh(bpy, 'gm_moon', V, F, [m], None, False, kit.coll))
        # halo
        mh = cw._new_mat(bpy, 'gm_halo'); g = G(mh.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
        r = g.vmath('LENGTH', tc.outputs['Object']); f = g.math('POWER', g.math('SUBTRACT', 1.0, g.math('DIVIDE', r, 7.0), clamp=True), 3.0)
        e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.55, 0.66, 0.95))}); g.put(e, 'Strength', g.math('MULTIPLY', f, 0.9))
        tr = g.node('ShaderNodeBsdfTransparent'); ad = g.node('ShaderNodeAddShader'); g.link(tr, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad)
        V = [(-7, -7, 0), (7, -7, 0), (7, 7, 0), (-7, 7, 0)]
        self.halo = cam_only(cw.mk_mesh(bpy, 'gm_halo', V, [(0, 1, 2, 3)], [mh], None, False, kit.coll))
        # cloud wisps drifting across the moon
        mc = cw._new_mat(bpy, 'gm_cloud'); g = G(mc.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); oi = g.node('ShaderNodeObjectInfo')
        q = g.vmath('ADD', g.vmath('MULTIPLY', tc.outputs['Object'], (0.35, 1.4, 1.0)), g.comb(g.math('MULTIPLY', oi.outputs['Random'], 50.0), 0.0, 0.0))
        n = g.noise(q, 0.9, 6.0, 0.6)
        lx, ly, _ = g.sep(tc.outputs['Generated'])
        edge = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SINE', g.math('MULTIPLY', lx, math.pi)), g.math('SINE', g.math('MULTIPLY', ly, math.pi))), 1.0)
        a = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.47), 4.0, clamp=True), edge)
        e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.30, 0.36, 0.52)), 'Strength': 0.75})
        tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
        g.link(g.math('MULTIPLY', a, 0.85), mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx)
        self.clouds = []
        for k, (w, h, off, sp) in enumerate(((9.0, 1.6, (-3.0, 0.9), 0.16), (12.0, 2.2, (2.0, -1.4), 0.10), (7.0, 1.2, (5.0, 2.4), 0.22))):
            V = [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)]
            ob = cam_only(cw.mk_mesh(bpy, f'gm_cloud{k}', V, [(0, 1, 2, 3)], [mc], None, False, kit.coll))
            ob.data.uv_layers.new(name='UVMap'); self.clouds.append((ob, off, sp))
    def place(self, cam_ob, direction, t, D=40.0):
        from mathutils import Vector
        d = np.asarray(direction, float); d /= np.linalg.norm(d); c = np.asarray(cam_ob.location[:], float) + d * D
        q = Vector(tuple(-d)).to_track_quat('Z', 'Y').to_euler()
        for ob, dd in ((self.disc, 0.0), (self.halo, 0.5)):
            ob.location = tuple(c + d * dd); ob.rotation_euler = q
        side = np.cross(d, (0, 0, 1.0)); side /= np.linalg.norm(side); up = np.cross(side, d)
        for ob, (ox, oy), sp in self.clouds:
            p = c - d * 2.0 + side * (ox - 6.0 + sp * t * 1.0) + up * oy
            ob.location = tuple(p); ob.rotation_euler = q

def screen_dir(pos, target, sx, sy, lens, aspect_hw):
    """World direction of a point on screen (sx, sy in -1..1, x right, y up) for a camera at pos looking at target
    (9:16: the sensor width 36 mm fits the frame height)."""
    f = np.asarray(target, float) - np.asarray(pos, float); f /= np.linalg.norm(f)
    r = np.cross(f, (0, 0, 1.0)); r /= np.linalg.norm(r); u = np.cross(r, f)
    hh = 18.0 / lens; hw = hh / aspect_hw
    d = f + r * sx * hw + u * sy * hh; return d / np.linalg.norm(d)


# =============================================================================================== the mine interior
class Mine:
    def __init__(self, kit, land, eggs):
        self.kit = kit; self.land = land; self.eggs = eggs; self.bpy = kit.bpy
        self.rock = mat_rock_in(kit); self.wood = mat_wood(kit)
        self.floor = ex.mat_pbr(kit, 'gm_floor_in', (0.24, 0.21, 0.19), 0.9, bump=0.4, bump_scale=120.0)
        self.iron = ex.mat_pbr(kit, 'gm_iron', (0.32, 0.30, 0.29), 0.38, metallic=0.85)
        self.lamps = []

    def opening_cap(self, a, b, r): self.eggs.openings.append(('-Y', 'cap', (a[0], a[1], b[0], b[1], r)))

    def gallery(self, name, u0, u1, zf, gaps_floor=(), gaps_ceil=(), open_left=False, D=D_G, r=R_G):
        h = 2 * r; zc = zf + r; uL, uR = u0 - r * 0.92, u1 + r * 0.92
        self.opening_cap((u0, zc), (u1, zc), r)
        def spans(a, b, gaps):
            out = []; cur = a
            for g0, g1 in sorted(gaps): out.append((cur, g0)); cur = g1
            out.append((cur, b)); return [(x, y) for x, y in out if y - x > 1e-4]
        P = []; Fl = []
        for a, b in spans(uL, uR, gaps_floor):
            v, f = quad(W(a, 0.001, zf), W(b, 0.001, zf), W(b, D, zf), W(a, D, zf)); Fl.append((v, f, 0))
        for a, b in spans(uL, uR, gaps_ceil):
            v, f = quad(W(a, 0.001, zf + h), W(a, D, zf + h), W(b, D, zf + h), W(b, 0.001, zf + h)); P.append((v, f, 0))
        v, f = quad(W(uL, D, zf - 0.01), W(uR, D, zf - 0.01), W(uR, D, zf + h), W(uL, D, zf + h)); P.append((v, f, 0))
        if not open_left:
            v, f = quad(W(uL, 0.001, zf), W(uL, D, zf), W(uL, D, zf + h), W(uL, 0.001, zf + h)); P.append((v, f, 0))
        v, f = quad(W(uR, 0.001, zf), W(uR, 0.001, zf + h), W(uR, D, zf + h), W(uR, D, zf)); P.append((v, f, 0))
        mk(self.kit, f'gm_{name}_rock', P, [self.rock]); mk(self.kit, f'gm_{name}_floor', Fl, [self.floor])
        # timber sets: a post near the face, one at the back, a cap across; every ~0.2 m
        T = []; s = 0.012; n = max(2, int((uR - uL) / 0.2))
        for k in range(n + 1):
            u = uL + 0.03 + (uR - uL - 0.06) * k / n
            if any(g0 - 0.01 < u < g1 + 0.01 for g0, g1 in list(gaps_floor) + list(gaps_ceil)): continue
            for d in (0.016, D - 0.02):
                v, f = box((u, FY + d, zf + (h - s) / 2), (s, s, h - s)); T.append((v, f, 0))
            v, f = box((u, FY + D / 2, zf + h - s / 2), (s * 1.1, D - 0.01, s)); T.append((v, f, 0))
        mk(self.kit, f'gm_{name}_timber', T, [self.wood])
        return dict(uL=uL, uR=uR, zf=zf, h=h)

    def shaft(self, u, w, segs, D=0.15):
        self.opening_cap((u, segs[0][0]), (u, segs[-1][1]), w)
        P = []; T = []
        for zt, zb in segs:
            v, f = quad(W(u - w, D, zb), W(u + w, D, zb), W(u + w, D, zt), W(u - w, D, zt)); P.append((v, f, 0))
            for su in (-1, 1):
                v, f = quad(W(u + su * w, 0.001, zb), W(u + su * w, D, zb), W(u + su * w, D, zt), W(u + su * w, 0.001, zt)); P.append((v, f, 0))
            for zz in np.arange(zb + 0.12, zt - 0.02, 0.22):           # cribbing frames round the shaft
                v, f = box((u, FY + D - 0.008, zz), (2 * w, 0.012, 0.012)); T.append((v, f, 0))
                for su in (-1, 1):
                    v, f = box((u + su * (w - 0.006), FY + D / 2, zz), (0.012, D, 0.012)); T.append((v, f, 0))
        mk(self.kit, 'gm_shaft_rock', P, [self.rock]); mk(self.kit, 'gm_shaft_crib', T, [self.wood])

    def ladder(self, u, zt, zb, d=0.115):
        P = []
        for su in (-1, 1):
            v, f = box((u + su * 0.022, FY + d, (zt + zb) / 2), (0.006, 0.006, zt - zb)); P.append((v, f, 0))
        for zz in np.arange(zb + 0.015, zt, 0.03):
            v, f = box((u, FY + d, zz), (0.044, 0.004, 0.004)); P.append((v, f, 0))
        mk(self.kit, 'gm_ladder', P, [self.wood])

    def rails(self, name, u0, u1, zf, y0=FY, ground=None):
        P = []; Q = []
        for us in np.arange(u0, u1, 0.035):
            z = zf if ground is None else ground(us)
            v, f = box((us, y0 + 0.08, z + 0.002), (0.012, 0.085, 0.004)); P.append((v, f, 0))
        for dy in (0.055, 0.105):
            if ground is None:
                v, f = box(((u0 + u1) / 2, y0 + dy, zf + 0.007), (u1 - u0, 0.004, 0.006)); Q.append((v, f, 0))
            else:
                xs = np.arange(u0, u1 + 1e-6, 0.03)
                for a, b in zip(xs[:-1], xs[1:]):
                    za, zb = ground(a) + 0.007, ground(b) + 0.007
                    v, f = cw._box(a, y0 + dy - 0.002, min(za, zb) - 0.003, b, y0 + dy + 0.002, max(za, zb) + 0.003); Q.append((v, f, 0))
        mk(self.kit, f'gm_{name}_sleepers', P, [self.wood]); mk(self.kit, f'gm_{name}_rails', Q, [self.iron])

    def lantern(self, name, pos, power=0.5, seed=0, rope=None):
        bpy = self.bpy; kit = self.kit
        glow = ex.mat_pbr(kit, 'gm_lantern_glass', (1.0, 0.8, 0.5), 0.2, emission=(1.0, 0.62, 0.28), strength=14.0)
        P = []
        v, f = box((0, 0, 0), (0.012, 0.012, 0.016)); P.append((v, f, 1))
        v, f = box((0, 0, 0.0095), (0.016, 0.016, 0.003)); P.append((v, f, 0))
        v, f = box((0, 0, -0.0095), (0.016, 0.016, 0.003)); P.append((v, f, 0))
        if rope:
            v, f = box((0, 0, rope / 2 + 0.011), (0.0015, 0.0015, rope)); P.append((v, f, 0))
        ob = ex.part(kit, f'gm_lantern_{name}', P, [self.iron, glow]); ob.location = tuple(pos)
        ld = bpy.data.lights.new(f'gm_lamp_{name}', 'POINT'); ld.energy = power; ld.color = WARM; ld.shadow_soft_size = 0.008
        lo = bpy.data.objects.new(f'gm_lamp_{name}', ld); kit.coll.objects.link(lo); lo.location = tuple(np.asarray(pos) + np.array((0, -0.012, 0)))
        rng = np.random.default_rng(100 + seed); ph = rng.uniform(0, 6.28, 3); fr = rng.uniform(5.0, 9.0, 3)
        def flick(t, ld=ld, ph=ph, fr=fr, base=power, ob=ob, pos=pos):
            k = 1.0 + 0.07 * math.sin(fr[0] * t + ph[0]) + 0.05 * math.sin(fr[1] * 1.7 * t + ph[1]) + 0.04 * math.sin(fr[2] * 2.9 * t + ph[2])
            ld.energy = base * k
            ob.rotation_euler = (0.06 * math.sin(1.3 * t + ph[0]), 0.05 * math.sin(1.1 * t + ph[1]), 0)
        kit.on_frame(flick); self.lamps.append(lo); return ob


# =============================================================================================== little people and animals
def miner(kit, name, shirt=(0.55, 0.20, 0.16), tool='pick', scale=1.0):
    """A small miner (about 8.5 cm): legs, body, head, helmet with a lamp, a working arm with a pick (or a lantern).
    Local axes: X forward, Z up, origin between the feet. Returns the parts to pose."""
    bpy = kit.bpy; s = scale
    skin = ex.mat(kit, 'gm_skin', (0.78, 0.56, 0.42), 0.6); cloth = ex.mat(kit, f'gm_shirt_{name}', shirt, 0.8)
    trousers = ex.mat(kit, 'gm_trousers', (0.20, 0.17, 0.15), 0.85); helm = ex.mat_pbr(kit, 'gm_helmet', (0.62, 0.48, 0.24), 0.35, metallic=0.4)
    lamp = ex.mat_pbr(kit, 'gm_headlamp', (1, 0.9, 0.7), 0.2, emission=(1.0, 0.82, 0.55), strength=30.0)
    wood = mat_wood(kit); iron = ex.mat_pbr(kit, 'gm_iron', (0.32, 0.30, 0.29), 0.38, metallic=0.85)
    root = ex.empty(kit, f'gm_{name}')
    body = ex.part(kit, f'gm_{name}_body', [
        (*ex.ell((0, 0, 0.051 * s), (0.011 * s, 0.0135 * s, 0.017 * s), 2), 0),
        (*ex.ell((0.001 * s, 0, 0.073 * s), (0.0092 * s, 0.0088 * s, 0.0095 * s), 2), 1),
        (*ex.ell((0.0, 0, 0.0785 * s), (0.0105 * s, 0.0102 * s, 0.0068 * s), 2), 2),
        (*ex.ell((0.0, 0, 0.0752 * s), (0.0135 * s, 0.013 * s, 0.0012 * s), 1), 2),
        (*ex.ell((0.0105 * s, 0, 0.0795 * s), (0.0022 * s, 0.0028 * s, 0.0028 * s), 1), 3),
        (*cw._tube([(0, 0.013 * s, 0.063 * s), (0.004 * s, 0.017 * s, 0.050 * s), (0.008 * s, 0.015 * s, 0.040 * s)], [0.0042 * s, 0.004 * s, 0.0036 * s], 6), 0),
    ], [cloth, skin, helm, lamp], root)
    legs = []
    for side in (-1, 1):
        lg = ex.part(kit, f'gm_{name}_leg{side}', [(*cw._tube([(0, 0, 0), (0, 0, -0.018 * s), (0, 0, -0.034 * s)], [0.0055 * s, 0.005 * s, 0.0045 * s], 6), 0),
                                                   (*ex.ell((0.003 * s, 0, -0.035 * s), (0.0065 * s, 0.0045 * s, 0.003 * s), 1), 1)],
                     [trousers, ex.mat(kit, 'gm_boot', (0.10, 0.08, 0.07), 0.7)], root, (0, side * 0.0065 * s, 0.036 * s))
        legs.append(lg)
    P = [(*cw._tube([(0, 0, 0), (0, 0, -0.013 * s), (0, 0, -0.025 * s)], [0.0042 * s, 0.004 * s, 0.0036 * s], 6), 0),
         (*ex.ell((0, 0, -0.027 * s), (0.0035 * s, 0.0035 * s, 0.0035 * s), 1), 1)]
    mats = [cloth, skin, wood, iron]
    if tool == 'pick':
        P.append((*cw._tube([(0, 0, -0.022 * s), (0, 0, -0.05 * s), (0, 0, -0.062 * s)], [0.0018 * s] * 3, 5), 2))
        P.append((*cw._tube([(-0.016 * s, 0, -0.064 * s), (-0.004 * s, 0, -0.062 * s), (0.004 * s, 0, -0.062 * s), (0.017 * s, 0, -0.066 * s)],
                            [0.0005 * s, 0.0024 * s, 0.0024 * s, 0.0005 * s], 6), 3))
    elif tool == 'lantern':
        glow = ex.mat_pbr(kit, 'gm_lantern_glass', (1.0, 0.8, 0.5), 0.2, emission=(1.0, 0.62, 0.28), strength=14.0); mats.append(glow)
        v, f = box((0, 0, -0.038 * s), (0.008 * s, 0.008 * s, 0.011 * s)); P.append((v, f, 4))
    arm = ex.part(kit, f'gm_{name}_arm', P, mats, root, (0, -0.014 * s, 0.063 * s))
    return {'root': root, 'body': body, 'legs': legs, 'arm': arm, 's': s}

def walk_pose(M, t, speed=2.2, swing=0.45, arm=True):
    ph = 2 * math.pi * speed * t
    for k, lg in enumerate(M['legs']): lg.rotation_euler = (0, swing * math.sin(ph + k * math.pi), 0)
    if arm: M['arm'].rotation_euler = (0, -swing * 0.8 * math.sin(ph), 0)
    M['body'].location = (0, 0, 0.0012 * M['s'] * abs(math.sin(ph)))

def swing_angle(t, strikes, period):
    """Pick arm angle (radians, about the side axis) for blows at the given times: slow raise, fast strike, a short hold."""
    past = [s for s in strikes if s <= t]; fut = [s for s in strikes if s > t]
    if not fut: tau = t - past[-1] if past else 0.0; return -math.radians(58 + 10 * min(1.0, tau / 0.4))
    nxt = fut[0]; dt = nxt - t
    up, down = math.radians(-168), math.radians(-56)
    if dt < 0.22: q = 1 - dt / 0.22; return up + (down - up) * q ** 2.2          # the strike accelerates
    prev = past[-1] if past else nxt - period
    tau = t - prev; rise = max(0.2, (nxt - prev) - 0.22 - 0.12)
    if tau < 0.12: return down
    q = ex.ease(min(1.0, (tau - 0.12) / rise)); return down + (up - down) * q

def bat(kit, name, scale=1.0):
    bpy = kit.bpy; s = scale; m = ex.mat(kit, 'gm_bat', (0.07, 0.055, 0.05), 0.75)
    wm = ex.mat(kit, 'gm_batwing', (0.11, 0.08, 0.07), 0.6)
    body = ex.part(kit, f'gm_{name}', [(*ex.ell((0, 0, 0), (0.008 * s, 0.0042 * s, 0.0042 * s), 1), 0),
                                       (*ex.ell((0.0085 * s, 0, 0.001 * s), (0.0035 * s, 0.003 * s, 0.003 * s), 1), 0),
                                       (*cone((0.009 * s, 0.0018 * s, 0.003 * s), (0.0085 * s, 0.0024 * s, 0.0065 * s), 0.0012 * s), 0),
                                       (*cone((0.009 * s, -0.0018 * s, 0.003 * s), (0.0085 * s, -0.0024 * s, 0.0065 * s), 0.0012 * s), 0)], [m])
    wings = []
    for side in (-1, 1):
        V = [(0.006 * s, 0, 0), (-0.006 * s, 0, 0), (-0.010 * s, side * 0.012 * s, 0), (-0.004 * s, side * 0.019 * s, 0.0),
             (0.002 * s, side * 0.026 * s, 0), (0.004 * s, side * 0.014 * s, 0)]
        wg = cw.mk_mesh(bpy, f'gm_{name}w{side}', V, [(0, 1, 2, 3, 4, 5)], [wm], None, False, kit.coll); wg.parent = body; wings.append((wg, side))
    return body, wings

def cone(a, b, r0): return ex.cone(a, b, r0)


# =============================================================================================== the scene
def build(bpy, ctx):
    W_, H_ = ctx['W'], ctx['H']
    kit = cw.Kit(bpy, seed=5, loop=DURATION)
    STRATA = [('turf', 0.05, (0.17, 0.15, 0.12), 0.1), ('scree', 0.20, (0.44, 0.45, 0.49), 0.5), ('slate', 0.42, (0.27, 0.30, 0.37), 0.12),
              ('quartzite', 0.26, (0.52, 0.54, 0.59), 0.25), ('schist', 0.55, (0.31, 0.33, 0.41), 0.3), ('bedrock', 1.0, (0.19, 0.20, 0.26), 0.4)]
    season = {'grass': (0.20, 0.30, 0.16), 'grass_tip': (0.42, 0.48, 0.30), 'grass_dry': (0.40, 0.40, 0.28), 'ground': (0.22, 0.23, 0.20),
              'leaf': [(0.10, 0.20, 0.12), (0.12, 0.24, 0.14), (0.09, 0.17, 0.11), (0.14, 0.25, 0.15)], 'flowers': 0.0, 'snow': 0.0, 'leaf_density': 1.0}
    rng = np.random.default_rng(12); spots = []
    while len(spots) < 30:
        x, y = rng.uniform(-1.18, 1.18), rng.uniform(-1.18, 1.18)
        if bench_s(np.array([x]), np.array([y]))[0] < 0.95: continue
        if x < -0.45 and y < -0.85: continue                 # keep the entrance and the yard clear
        h = float(top(np.array([x]), np.array([y]))[0])
        if h > 1.02: continue                                  # tree line below the summit
        if any(math.hypot(x - a, y - b) < 0.24 for a, b, *_ in spots): continue
        spots.append((x, y, rng.uniform(0.55, 0.95), 'cone'))
    land = cw.block(kit, size=(SX, SY), depth=DEPTH, strata=STRATA, top=top, water=None, seed=6, season=season, grass=0.4, grass_height=0.8,
                    tree_kinds=('cone',), tree_spots=spots, boulders=14, flowers=0.0, sway=0.9, keep_clear=[(-1.05, -1.15, 0.28)])
    rig = night(kit, land); ridges(kit); moon = Moon(kit)
    eggs = ex.Eggs(kit, land, light_power=0.55, light_color=(1.0, 0.86, 0.66))
    mine = Mine(kit, land, eggs)

    # ---- galleries, shaft, cavern, pool
    sg = (SHAFT_U - SHAFT_W, SHAFT_U + SHAFT_W)
    mine.gallery('g1', G1['u0'], G1['u1'], G1['zf'], gaps_floor=[sg], open_left=True)
    mine.gallery('g2', G2['u0'], G2['u1'], G2['zf'], gaps_floor=[sg], gaps_ceil=[sg])
    mine.gallery('g3', G3['u0'], G3['u1'], G3['zf'], gaps_ceil=[sg])
    mine.shaft(SHAFT_U, SHAFT_W, [(G1['zf'], G2['zf'] + 2 * R_G), (G2['zf'], G3['zf'] + 2 * R_G)])
    mine.ladder(SHAFT_U, G1['zf'] + 0.01, G3['zf'])
    cave_pts = cavern(kit, eggs, mine)
    V, F = cw._box(CAVE['u'] - 0.25, FY + 0.003, CAVE['z'] - 0.2, CAVE['u'] + 0.25, FY + 0.30, POOL_LEVEL)
    cw.mk_mesh(bpy, 'gm_pool', V, F, [mat_water_pool(kit)], None, False, kit.coll)
    # the portal: a timber frame and a plank roof where the adit meets the hillside; rails out onto the yard
    pu = G1['u0'] - R_G * 0.92; P = []
    for d in (0.008, D_G - 0.004):
        v, f = box((pu + 0.006, FY + d, 0.085), (0.016, 0.016, 0.17)); P.append((v, f, 0))
    v, f = box((pu + 0.006, FY + D_G / 2, 0.172), (0.018, D_G + 0.03, 0.018)); P.append((v, f, 0))
    for k in range(5):
        v, f = box((pu + 0.03 + 0.035 * k, FY + D_G / 2, 0.188 + 0.006 * k), (0.034, D_G + 0.02, 0.006)); P.append((v, f, 0))
    mk(kit, 'gm_portal', P, [mine.wood])
    gfun = lambda x: float(land.height(np.array([x]), np.array([FY + 0.08]))[0])
    mine.rails('yard', -SX / 2 + 0.005, pu - 0.004, 0.0, ground=lambda x: max(gfun(x), -0.002))
    mine.rails('g1', pu - 0.004, SHAFT_U - SHAFT_W - 0.03, G1['zf'])
    mine.rails('g3', G3['u0'] - 0.05, G3['u1'] + 0.02, G3['zf'])
    # post and lantern at the entrance, lanterns in the galleries, the shaft and the cave
    v, f = box((pu - 0.05, FY + 0.20, 0.06), (0.01, 0.01, 0.13)); mk(kit, 'gm_post', [(v, f, 0)], [mine.wood])
    mine.lantern('door', (pu - 0.05, FY + 0.186, 0.118), 1.2, 1)
    for k, (u, z, pw) in enumerate(((-0.60, G1['zf'] + 0.128, 0.7), (-0.12, G1['zf'] + 0.128, 0.7), (-0.24, G2['zf'] + 0.128, 0.7),
                                    (0.02, G2['zf'] + 0.128, 0.55), (-0.18, G3['zf'] + 0.128, 0.6), (0.20, G3['zf'] + 0.128, 0.75))):
        mine.lantern(f'in{k}', W(u, 0.10, z), pw, 10 + k, rope=0.012)
    mine.lantern('shaft', W(SHAFT_U + 0.04, 0.12, -0.30), 0.45, 20)
    mine.lantern('cave', W(CAVE['u'] + 0.19, 0.12, POOL_LEVEL + 0.03), 0.9, 21)
    mine.lantern('cave2', W(CAVE['u'] - 0.17, 0.15, POOL_LEVEL + 0.07), 0.5, 22, rope=0.03)

    # ---- easter eggs (museum-lit, by depth)
    fy = eggs.faces['-Y']
    eggs.chest('-Y', -1.00, -0.40, light=2.5)
    eggs.ammonite('-Y', 0.42, -0.86, light=2.2)
    eggs.trilobite('-Y', -0.62, -1.08, light=2.2)
    eggs.geode('-Y', -0.40, -1.92, light=2.6)
    eggs.gold('-Y', [(0.39, -1.16), (0.47, -1.29), (0.52, -1.44), (0.60, -1.62), (0.72, -1.80), (0.90, -1.96)], nuggets=24, light=2.4)
    eggs.geode('+X', -0.40, -1.25, light=2.6)
    eggs.ammonite('+X', 0.35, -0.70, light=2.2)
    eggs.finish()
    canary = canary_cage(kit, mine, W(-0.42, 0.06, G1['zf'] + 0.118))
    ex.soften_roots(land)
    rock_face(kit, land)
    raking(kit)

    # ---- gold at the face of the deepest gallery: nuggets in the end wall, one big one that wakes at the strike
    gold = ex.mat_pbr(kit, 'ex_gold', (1.0, 0.74, 0.30), 0.25, metallic=1.0, bump=0.25, bump_scale=900.0)
    m = cw._new_mat(bpy, 'gm_goldwake'); g = G(m.node_tree, kit); gv = g.value(0.0, 'gm_goldwake')
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((1.0, 0.76, 0.32)), 'Roughness': 0.2, 'Metallic': 1.0, 'Emission Color': srgb((1.0, 0.70, 0.26))})
    g.link(gv, cw._sock(p.inputs, 'Emission Strength')); cw._finish(g, p)
    uE = G3['u1'] + R_G * 0.92 - 0.004; A = []; rng = np.random.default_rng(77)
    for k in range(16):
        c = (uE, FY + rng.uniform(0.02, D_G - 0.02), G3['zf'] + rng.uniform(0.03, 0.15)); r = rng.uniform(0.003, 0.007)
        A.append((*ex.ell(c, (r * 0.6, r * 1.2, r), 2, 0.35, k), 0))
    mk(kit, 'gm_gold_face', A, [gold], smooth=True)
    big = mk(kit, 'gm_gold_big', [(*ex.ell((uE - 0.002, FY + 0.05, G3['zf'] + 0.075), (0.007, 0.016, 0.012), 2, 0.4, 3), 0)], [m], smooth=True)
    ld = bpy.data.lights.new('gm_goldflash', 'POINT'); ld.energy = 0.0; ld.color = (1.0, 0.74, 0.36); ld.shadow_soft_size = 0.01
    gfl = bpy.data.objects.new('gm_goldflash', ld); kit.coll.objects.link(gfl); gfl.location = (uE - 0.03, FY + 0.03, G3['zf'] + 0.08)
    sparks = Sparks(kit, (uE - 0.006, FY + 0.03, G3['zf'] + 0.06))

    # ---- people
    walker = miner(kit, 'walker', (0.30, 0.34, 0.46), tool='lantern')
    wl = bpy.data.lights.new('gm_walker_lamp', 'POINT'); wl.energy = 0.35; wl.color = WARM; wl.shadow_soft_size = 0.006
    wlo = bpy.data.objects.new('gm_walker_lamp', wl); kit.coll.objects.link(wlo); wlo.parent = walker['arm']; wlo.location = (0, -0.008, -0.038)
    pusher = miner(kit, 'pusher', (0.50, 0.24, 0.16), tool=None)
    climber = miner(kit, 'climber', (0.34, 0.40, 0.30), tool=None)
    dig1 = miner(kit, 'dig1', (0.46, 0.30, 0.20)); dig2 = miner(kit, 'dig2', (0.32, 0.30, 0.42))
    goldm = miner(kit, 'goldminer', (0.58, 0.22, 0.14))
    cart = ore_cart(kit, mine)
    bats_in = [bat(kit, f'batc{k}', 1.35) for k in range(14)]
    bats_out = [bat(kit, f'bato{k}', 3.4) for k in range(34)]

    S = {'kit': kit, 'land': land, 'moon': moon, 'eggs': eggs, 'mine': mine, 'walker': walker, 'pusher': pusher, 'climber': climber,
         'dig1': dig1, 'dig2': dig2, 'goldm': goldm, 'cart': cart, 'bats_in': bats_in, 'bats_out': bats_out, 'sparks': sparks,
         'goldwake': gv, 'goldflash': ld, 'canary': canary, 'pu': pu, 'uE': uE, 'cave_pts': cave_pts}
    hw = H_ / W_
    for nm in ('night', 'flight'):                    # the moon's direction is fixed per shot (from the shot's middle pose)
        p2, t2, l2, _f, _s, ms = shot_pose(nm, 0.5, 0.0); _MOON_DIR[nm] = screen_dir(p2, t2, ms[0], ms[1], l2, hw)
    life(S)
    ex.finish(bpy, W_, H_, bloom=0.30, threshold=1.0, size=0.6, vignette=0.30)
    S['cam'] = ex.ShotCam(kit)
    S['title'] = title(kit, S['cam'])
    cw.apply_cycles(bpy, fast=True)
    cy = bpy.context.scene.cycles
    cy.max_bounces = 4; cy.diffuse_bounces = 1; cy.glossy_bounces = 1; cy.transmission_bounces = 4; cy.transparent_max_bounces = 10
    cy.adaptive_threshold = 0.04; cy.sample_clamp_direct = 10.0; cy.sample_clamp_indirect = 3.0
    return S


def cavern(kit, eggs, mine):
    """The cave under the deepest gallery: a lumpy hollow (not a clean bowl), stalactites, a still pool at the bottom.
    Returns ceiling points (u, d, z) where the bats can hang."""
    c = CAVE; a, b, dep = c['a'] * 1.03, c['b'] * 1.03, c['d']
    V, F = ex.bowl(a, b, dep, rings=18, seg=56); V = np.asarray(V, float)
    w = np.clip(V[:, 1] / dep, 0, 1) ** 0.6
    n = cw.fbm(V[:, 0] * 1.0 + V[:, 1] * 1.3, V[:, 2] - V[:, 1] * 0.7, 3, 4, 9.0)
    ctr = np.array((0.0, dep * 0.45, 0.0)); dv = ctr - V; dv /= np.maximum(np.linalg.norm(dv, axis=1)[:, None], 1e-6)
    n2 = cw.fbm(V[:, 0] * 2.0 - V[:, 1], V[:, 2] * 2.0 + V[:, 1], 9, 3, 14.0)
    V = V + dv * (w * (0.05 * (n + 0.35) + 0.02 * n2))[:, None]
    ob = ex.part(kit, 'gm_cave', [(V, F, 0)], [mine.rock]); eggs.faces['-Y'].put(ob, c['u'], c['z'], 0.0015)
    eggs.openings.append(('-Y', 'ell', (c['u'], c['z'], c['a'], c['b'])))
    rng = np.random.default_rng(21); stone = ex.mat_pbr(kit, 'gm_dripstone', (0.50, 0.49, 0.50), 0.4, coat=0.4)
    up = np.where((V[:, 2] > b * 0.45) & (V[:, 1] > 0.03) & (V[:, 1] < dep * 0.9))[0]
    A = []; hang = []
    for k, i in enumerate(rng.permutation(up)[:40]):
        p = V[i]
        if k < 22:
            L = rng.uniform(0.015, 0.05); r = rng.uniform(0.004, 0.009)
            A.append((*ex.cone(p + np.array((0, 0, 0.004)), p - np.array((0, 0, L)), r), 0))
        elif abs(p[0]) < a * 0.7: hang.append((c['u'] + p[0], p[1], c['z'] + p[2]))
    ex.part(kit, 'gm_stalactites', [(np.asarray(v) + np.array((c['u'], FY + 0.0015, c['z'])), f, m) for v, f, m in A], [stone])
    return hang

def rock_face(kit, land):
    """Patch this film's strata material: blotchy mottling and fine cracks so the cut faces read as hard rock, not felt."""
    nt = land.mats['strata'].node_tree; g = G(nt, kit)
    p = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]; bump = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBump'][0]
    bc = p.inputs['Base Color'].links[0].from_socket; hs = bump.inputs['Height'].links[0].from_socket
    pos = g.node('ShaderNodeTexCoord').outputs['Object']
    big = g.noise(pos, 3.0, 4.0, 0.6); warp = g.noise(pos, 4.0, 3.0, 0.5)
    q = g.vmath('ADD', pos, g.vmath('SCALE', g.vmath('SUBTRACT', warp.outputs['Color'], (0.5, 0.5, 0.5)), scale=0.25))
    vor = g.voronoi(q, 2.2, 'DISTANCE_TO_EDGE'); vor2 = g.voronoi(q, 6.5, 'DISTANCE_TO_EDGE')
    gate = g.math('MULTIPLY', g.math('SUBTRACT', g.noise(pos, 5.0, 2.0).outputs['Fac'], 0.42), 6.0, clamp=True)   # fractures die out here and there
    crack = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vor.outputs['Distance'], 110.0), clamp=True), gate)
    crack2 = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vor2.outputs['Distance'], 160.0), clamp=True), g.math('SUBTRACT', 1.0, gate))
    mot = g.math('MULTIPLY', g.math('SUBTRACT', big.outputs['Fac'], 0.3), 1.6, clamp=True)
    col = g.mix(mot, g.mix(1.0, bc, (0.80, 0.81, 0.85), 'MULTIPLY'), g.mix(1.0, bc, (1.14, 1.14, 1.17), 'MULTIPLY'))
    col = g.mix(g.math('ADD', g.math('MULTIPLY', crack, 0.55), g.math('MULTIPLY', crack2, 0.22)), col, srgb((0.05, 0.055, 0.07)))
    g.link(col, p.inputs['Base Color'])
    h = g.math('ADD', hs, g.math('SUBTRACT', g.math('MULTIPLY', big.outputs['Fac'], 0.5), g.math('ADD', g.math('MULTIPLY', crack, 0.35), g.math('MULTIPLY', crack2, 0.15))))
    g.link(h, bump.inputs['Height']); bump.inputs['Strength'].default_value = 0.7

def raking(kit):
    """Cool light skimming each camera-facing cut face from its side: it brings out the rock texture."""
    bpy = kit.bpy
    for name, pos, tgt, pw in (('gm_rake_y', (-SX / 2 - 1.6, FY - 0.45, -0.3), (0.8, FY, -0.9), 42.0),
                               ('gm_rake_x', (SX / 2 + 0.45, -SY / 2 - 1.6, -0.3), (SX / 2, 0.8, -0.9), 48.0)):
        ld = bpy.data.lights.new(name, 'AREA'); ld.size = 1.4; ld.shape = 'DISK'; ld.energy = pw; ld.color = (0.60, 0.70, 1.0)
        ob = bpy.data.objects.new(name, ld); kit.coll.objects.link(ob); ob.location = pos; ex.look_at(ob, tgt)
        ob.visible_camera = False; ob.visible_glossy = False

def canary_cage(kit, mine, pos):
    """Easter egg: the miners' canary in its cage, hung from a timber cap near the entrance (it hops)."""
    bpy = kit.bpy; brass = ex.mat_pbr(kit, 'gm_brass', (0.80, 0.62, 0.30), 0.3, metallic=0.9)
    P = []; R = 0.014; Hc = 0.026
    for k in range(10):
        a = 2 * math.pi * k / 10; P.append((*cw._tube([(R * math.cos(a), R * math.sin(a), -Hc), (R * math.cos(a), R * math.sin(a), 0)], [0.0007, 0.0007], 4), 0))
    for zz in (-Hc, -Hc * 0.5, 0):
        ring = [(R * math.cos(a), R * math.sin(a), zz) for a in np.linspace(0, 2 * math.pi, 25)]
        P.append((*cw._tube(ring, np.full(25, 0.0009), 4, False), 0))
    P.append((*ex.ell((0, 0, 0.003), (R, R, 0.006), 1), 0)); P.append((*cw._tube([(0, 0, 0.008), (0, 0, 0.016)], [0.0008, 0.0008], 4), 0))
    P.append((*cw._tube([(-R, 0, -Hc * 0.62), (R, 0, -Hc * 0.62)], [0.0008, 0.0008], 4), 0))
    cage = ex.part(kit, 'gm_cage', P, [brass]); cage.location = tuple(pos)
    yel = ex.mat_pbr(kit, 'gm_canary', (1.0, 0.82, 0.12), 0.5, emission=(1.0, 0.8, 0.2), strength=0.4)
    bird = ex.part(kit, 'gm_canary', [(*ex.ell((0, 0, 0.004), (0.0055, 0.004, 0.0045), 1), 0), (*ex.ell((0.004, 0, 0.0085), (0.003, 0.003, 0.003), 1), 0),
                                      (*ex.cone((0.0068, 0, 0.0085), (0.0095, 0, 0.0082), 0.0011), 1), (*ex.cone((-0.004, 0, 0.004), (-0.009, 0, 0.002), 0.0022), 0)],
                   [yel, ex.mat(kit, 'gm_beak', (0.9, 0.5, 0.1), 0.5)], cage, (0, 0, -Hc * 0.62))
    ld = bpy.data.lights.new('gm_canary_spot', 'SPOT'); ld.energy = 0.35; ld.spot_size = math.radians(40); ld.spot_blend = 0.8; ld.color = (1.0, 0.9, 0.7)
    lo = bpy.data.objects.new('gm_canary_spot', ld); kit.coll.objects.link(lo); lo.location = tuple(np.asarray(pos) + np.array((0.0, -0.25, 0.12))); ex.look_at(lo, pos)
    lo.visible_camera = False
    def hop(t, bird=bird, cage=cage):
        k = t % 1.7; up = max(0.0, math.sin(math.pi * min(1.0, k / 0.25))) if k < 0.25 else 0.0
        side = 1 if int(t / 1.7) % 2 else -1
        bird.location = (0.003 * side * (1 if k > 0.12 else -1), 0, -Hc * 0.62 + 0.004 * up)
        bird.rotation_euler = (0, 0, (0 if side > 0 else math.pi) + 0.25 * math.sin(3.1 * t))
        cage.rotation_euler = (0.03 * math.sin(1.2 * t), 0.02 * math.sin(0.9 * t), 0)
    kit.on_frame(hop); return bird

def ore_cart(kit, mine):
    rust = ex.mat_pbr(kit, 'gm_cart', (0.38, 0.22, 0.14), 0.6, metallic=0.5)
    ore = ex.mat_pbr(kit, 'gm_ore', (0.28, 0.27, 0.30), 0.8, flecks=6.0)
    P = []
    v, f = box((0, 0, 0.034), (0.074, 0.048, 0.004)); P.append((v, f, 0))
    for sx_ in (-1, 1):
        v, f = box((sx_ * 0.037, 0, 0.051), (0.004, 0.048, 0.034)); P.append((v, f, 0))
        v, f = box((0, sx_ * 0.024, 0.051), (0.074, 0.004, 0.034)); P.append((v, f, 0))
    rng = np.random.default_rng(4)
    for k in range(22):
        c = (rng.uniform(-0.03, 0.03), rng.uniform(-0.018, 0.018), 0.064 + rng.uniform(0, 0.012)); r = rng.uniform(0.006, 0.011)
        P.append((*ex.ell(c, (r, r * 0.9, r * 0.8), 1, 0.4, k), 1))
    body = ex.part(kit, 'gm_cart', P, [rust, ore])
    wheels = []
    for wx in (-0.022, 0.022):
        for wy in (-0.025, 0.025):
            th = np.linspace(0, 2 * math.pi, 13)
            V, F = cw._tube([(0, -0.003, 0), (0, 0.003, 0)], [0.012, 0.012], 12)
            spoke = cw._box(-0.011, -0.0035, -0.0015, 0.011, 0.0035, 0.0015)
            wh = ex.part(kit, f'gm_wheel{len(wheels)}', [(V, F, 0), (*spoke, 1)], [mine.iron, rust], body, (wx, wy, 0.022))
            wheels.append(wh)
    return {'body': body, 'wheels': wheels}

class Sparks:
    """Sparks off the pick: tiny glowing points thrown out of the rock face (toward the camera), falling and dying."""
    def __init__(self, kit, at, n=40, seed=9):
        bpy = kit.bpy; rng = np.random.default_rng(seed); self.at = np.asarray(at, float)
        m = ex.mat_pbr(kit, 'gm_spark', (1, 0.8, 0.4), 0.3, emission=(1.0, 0.72, 0.30), strength=60.0)
        self.obs = []
        for k in range(n):
            V, F = ex.ell((0, 0, 0), (0.0026, 0.0026, 0.0026), 1)
            ob = cw.mk_mesh(bpy, f'gm_spark{k}', V, F, [m], None, False, kit.coll); ob.visible_shadow = False
            v = np.array([rng.uniform(-0.75, -0.15), rng.uniform(-0.65, 0.05), rng.uniform(0.05, 0.55)]); v = v / np.linalg.norm(v) * rng.uniform(0.25, 0.55)
            self.obs.append((ob, v, rng.uniform(0.35, 0.8), rng.uniform(0, 1)))
    def update(self, t, strikes):
        past = [s for s in strikes if s <= t]; tau = t - past[-1] if past else 99.0
        big = bool(past) and past[-1] == strikes[-1]
        for k, (ob, v, life, r) in enumerate(self.obs):
            show = tau < life and (big or r < 0.45)
            ob.hide_render = not show
            if show:
                p = self.at + v * tau + np.array((0, 0, -0.5 * 1.6 * tau * tau)); ob.location = tuple(p)
                s = max(0.15, 1.0 - tau / life); ob.scale = (s, s, s)


def life(S):
    kit = S['kit']; land = S['land']; mine = S['mine']
    walk_path = np.array([(-1.24, -0.88), (-1.12, -1.02), (-1.00, -1.14), (S['pu'] - 0.02, FY + 0.09)])
    def ground(x, y): return float(land.height(np.array([x]), np.array([y]))[0])
    def pose(t):
        # the walker crosses the yard to the entrance and goes in (0.6 to 5.4 s)
        Mw = S['walker']; u = ex.ease(min(1.0, max(0.0, (t - 0.6) / 4.8)))
        seg = u * (len(walk_path) - 1); i = min(int(seg), len(walk_path) - 2); f = seg - i
        p = walk_path[i] + (walk_path[i + 1] - walk_path[i]) * f; dirv = walk_path[i + 1] - walk_path[i]
        inside = p[0] > S['pu'] - 0.03
        Mw['root'].location = (p[0], p[1], max(ground(p[0], p[1]), 0.0)); Mw['root'].rotation_euler = (0, 0, math.atan2(dirv[1], dirv[0]))
        moving = 0.6 < t < 5.4
        walk_pose(Mw, t if moving else 0.0, 1.8, 0.45 if moving else 0.0, arm=False)
        Mw['arm'].rotation_euler = (0, math.radians(-38), 0)
        for ob in [Mw['body'], Mw['arm']] + Mw['legs']: ob.hide_render = t > 5.6
        # the cart and its pusher roll down the top gallery (1.5 to 10.5 s)
        q = ex.ease(min(1.0, max(0.0, (t - 1.5) / 9.0))); cu = -0.66 + (-0.06 + 0.66) * q
        cart = S['cart']; cart['body'].location = W(cu, 0.08, G1['zf'] + 0.010 - 0.022 + 0.022)
        cart['body'].location = (cu, FY + 0.08, G1['zf'] + 0.0)
        for wh in cart['wheels']: wh.rotation_euler = (0, cu / 0.012, 0)
        Mp = S['pusher']; Mp['root'].location = (cu - 0.068, FY + 0.075, G1['zf'] + 0.004); Mp['root'].rotation_euler = (0, 0, 0)
        mv = 1.5 < t < 10.5
        walk_pose(Mp, t if mv else 0.0, 1.2, 0.35 if mv else 0.0, arm=False); Mp['arm'].rotation_euler = (0, math.radians(-78), 0)
        Mp['body'].rotation_euler = (0, math.radians(14), 0)
        # the climber goes down the ladder (5.6 to 12.6 s)
        Mc = S['climber']; qc = min(1.0, max(0.0, (t - 5.6) / 7.0)); steps = qc * 18; fs = steps % 1.0
        zc = -0.02 - (0.585) * (int(steps) + ex.ease(min(1.0, fs * 1.6))) / 18
        Mc['root'].location = (SHAFT_U, FY + 0.088, zc); Mc['root'].rotation_euler = (0, 0, math.pi / 2)
        alt = 1 if int(steps) % 2 else -1; climbing = 0 < qc < 1
        for k, lg in enumerate(Mc['legs']): lg.rotation_euler = (0, (0.35 * alt * (1 if k else -1)) if climbing else 0.0, 0)
        Mc['arm'].rotation_euler = (0, math.radians(-160 + (12 * alt if climbing else 0)), 0)
        # two diggers at the end of the middle gallery, never in step
        for M, u0_, t0, P_ in ((S['dig1'], G2['u0'] - 0.04, 0.3, 1.15), (S['dig2'], G2['u0'] + 0.13, 0.85, 1.4)):
            M['root'].location = (u0_, FY + 0.075, G2['zf'] + 0.002); M['root'].rotation_euler = (0, 0, math.pi)
            strikes = [t0 + k * P_ for k in range(int((DURATION - t0) / P_) + 1)]
            M['arm'].rotation_euler = (0, swing_angle(t, strikes, P_), 0)
            M['body'].rotation_euler = (0, 0.15 * math.sin(swing_angle(t, strikes, P_) + 2.0), 0)
        # the gold miner: three blows, the last one finds the gold
        Mg = S['goldm']; Mg['root'].location = (S['uE'] - 0.062, FY + 0.06, G3['zf'] + 0.002); Mg['root'].rotation_euler = (0, 0, 0)
        if t < T_GOLD + 0.35: Mg['arm'].rotation_euler = (0, swing_angle(t, [s for s in STRIKES], 1.2), 0)
        else:                                       # he lowers the pick and leans in to look
            q = ex.ease(min(1.0, (t - T_GOLD - 0.35) / 0.8)); Mg['arm'].rotation_euler = (0, math.radians(-66 + 30 * q), 0)
            Mg['body'].rotation_euler = (0, math.radians(10 * q), 0)
        S['sparks'].update(t, STRIKES)
        tau = t - T_GOLD
        S['goldwake'].default_value = 0.0 if tau < 0 else 14.0 * math.exp(-tau / 0.5) + 2.0
        S['goldflash'].energy = 0.0 if tau < 0 else 3.5 * math.exp(-tau / 0.35) + 0.12
        bats_inside(S, t); bats_outside(S, t)
    kit.on_frame(pose)

def _flap(wings, t, rate=6.0, amp=1.0, ph=0.0, fold=0.0):
    a = math.sin(2 * math.pi * rate * t + ph)
    for wg, side in wings:
        wg.rotation_euler = (side * (0.25 + 0.75 * amp * a) * (1 - fold) - side * fold * 1.3, 0, 0)
        wg.scale = (1, 1 - 0.75 * fold, 1)

def bats_inside(S, t):
    rng = np.random.default_rng(55); c = CAVE
    for k, (body, wings) in enumerate(S['bats_in']):
        hp = S['cave_pts'][k % len(S['cave_pts'])]
        hang = np.array((hp[0], FY + hp[1], hp[2] - 0.004)); tw = T_BATS + rng.uniform(0, 0.55); ph = rng.uniform(0, 6.28)
        dirv = np.array((rng.uniform(-0.55, 0.55), -1.0, rng.uniform(0.15, 0.6))); sp = rng.uniform(0.55, 0.85)
        if t < tw:                                   # hanging head down, wings folded, a little sway and a shiver
            body.location = tuple(hang - np.array((0, 0, 0.008))); body.rotation_euler = (0.0, math.pi / 2 + 0.08 * math.sin(1.4 * t + ph), 0.6 * k)
            _flap(wings, t, 0.5, 0.1, ph, fold=1.0); body.hide_render = False
            if t > T_GOLD and t < tw: body.rotation_euler = (0.0, math.pi / 2 + 0.25 * math.sin(14 * t + ph), 0.6 * k)
            continue
        tau = t - tw; dist = sp * tau * (0.4 + min(1.0, tau / 0.6) * 0.6)
        p = hang + np.array((0, 0, -0.03 * min(1.0, tau / 0.25))) + dirv / np.linalg.norm(dirv) * dist
        p = p + np.array((0.02 * math.sin(9 * tau + ph), 0, 0.015 * math.sin(7 * tau + ph * 2)))
        body.location = tuple(p); body.hide_render = tau > 3.0
        yaw = math.atan2(dirv[1], dirv[0]); body.rotation_euler = (0.2 * math.sin(5 * tau + ph), -0.3, yaw)
        _flap(wings, t, 6.5, 1.0, ph)

def bats_outside(S, t):
    rng = np.random.default_rng(88); pu = S['pu']
    for k, (body, wings) in enumerate(S['bats_out']):
        t0 = T_OUT + 0.11 * k + rng.uniform(0, 0.08); ph = rng.uniform(0, 6.28)
        tau = t - t0
        if tau < 0: body.hide_render = True; continue
        body.hide_render = False
        start = np.array((pu - 0.02, FY + rng.uniform(0.04, 0.14), 0.07))
        md = _MOON_DIR.get('flight', np.array((0.3, 0.6, 0.75))); md = md / np.linalg.norm(md)
        side = np.cross(md, (0, 0, 1.0)); side /= np.linalg.norm(side); upv = np.cross(side, md)
        spread = side * rng.normal(0, 0.16) + upv * rng.normal(0, 0.12)
        aim = md + np.array((0, 0, 0.42)) + spread; aim /= np.linalg.norm(aim)      # up over the ridge, toward the moon
        out = np.array((-1.0, 0.0, 0.25)); sp = rng.uniform(0.95, 1.3)
        e1 = min(1.0, tau / 0.45); k2 = max(0.0, tau - 0.25)
        p = start + out * 0.16 * (e1 * e1 * (3 - 2 * e1)) + aim * sp * k2 ** 1.15
        p = p + side * 0.06 * math.sin(3.7 * tau + ph) + upv * 0.04 * math.sin(5.3 * tau + ph)
        body.location = tuple(p); body.hide_render = tau > 7.0
        vel = out * 0.3 * (1 - e1) + aim * sp
        body.rotation_euler = (0.25 * math.sin(4 * tau + ph), -math.atan2(vel[2], np.hypot(vel[0], vel[1])) * 0.6, math.atan2(vel[1], vel[0]))
        _flap(wings, t, 5.5, 1.0, ph)

def title(kit, cam):
    bpy = kit.bpy; cu = bpy.data.curves.new('gm_title', 'FONT'); cu.body = 'The Gold Mine'; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    font = os.path.join(ROOT, 'ads', 'fonts', 'Archivo.ttf')
    if os.path.exists(font): cu.font = bpy.data.fonts.load(font)
    cu.size = 0.24; cu.space_character = 1.12
    ob = bpy.data.objects.new('gm_title', cu); kit.coll.objects.link(ob)
    m = cw._new_mat(bpy, 'gm_titlemat'); g = G(m.node_tree, kit); a = g.value(0.0, 'gm_title_a')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.86, 0.62)), 'Strength': 1.6}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx); cu.materials.append(m)
    cam_only(ob); ob.parent = cam.ob
    return {'ob': ob, 'a': a}


# =============================================================================================== shots
def shot_pose(name, u, t):
    """pos, target, lens, focus distance, f-stop, moon screen position (sx, sy) for this shot."""
    if name == 'night':          # the mountain at night; a slow push toward the lantern at the entrance
        e = ex.ease(u); tgt = ex.lerp((0.0, 0.0, -0.40), (-0.30, -0.70, -0.25), e)
        az = math.radians(-60 + 6 * e); el = math.radians(13 - 3 * e); D = 6.9 - 1.9 * e
        pos = tgt + D * np.array((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        return pos, tgt, 35.0, D, 11.0, (0.42, 0.62)
    if name == 'descent':        # crane down the cut face, then a slow push in on the deepest gallery
        a = ex.ease5(min(1.0, u / 0.56)); b = ex.ease(max(0.0, (u - 0.56) / 0.44))
        tu = -0.12 + 0.34 * a + 0.02 * b; tz = -0.18 - 1.22 * a - 0.02 * b; Dd = 1.62 - 0.67 * a - 0.10 * b
        el = math.radians(9 - 5 * a)
        tgt = np.array((tu, FY + 0.08, tz)); pos = np.array((tu - 0.20, FY - Dd, tz + Dd * math.tan(el)))
        return pos, tgt, 32.0, Dd + 0.08, 9.0, None
    # flight: low by the yard, the entrance and the moon; the bats pour out; the camera rises and pulls back
    e = ex.ease(u); tgt = ex.lerp((-0.62, -0.95, 0.42), (-0.15, -0.30, 0.15), e)
    az = math.radians(-112 + 12 * e); el = math.radians(3 + 12 * e); D = 2.3 + 4.2 * e
    pos = tgt + D * np.array((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    return pos, tgt, 30.0, D, 11.0, (0.28, 0.60)

_MOON_DIR = {}

def frame(bpy, ctx, S, i, t):
    S['kit'].update(t)
    tl = ctx['timeline'].at(t); name = tl['name']
    pos, tgt, lens, focus, fstop, ms = shot_pose(name, tl['u'], t)
    S['cam'].set(pos, tgt, lens, focus, fstop)
    hw = ctx['H'] / ctx['W']
    if ms is not None:
        S['moon'].place(S['cam'].ob, _MOON_DIR[name], t)
        for ob in [S['moon'].disc, S['moon'].halo] + [c[0] for c in S['moon'].clouds]: ob.hide_render = False
    else:
        for ob in [S['moon'].disc, S['moon'].halo] + [c[0] for c in S['moon'].clouds]: ob.hide_render = True
    # the title: first 2.5 s, faded in and out, upper third
    a = min(1.0, max(0.0, (t - 0.25) / 0.6)) * min(1.0, max(0.0, (2.5 - t) / 0.5))
    S['title']['a'].default_value = a; S['title']['ob'].hide_render = a <= 0.0
    d = 5.0; half_h = d * 18.0 / lens
    S['title']['ob'].location = (0.0, half_h * 0.58, -d); sc = half_h / 3.3 * 0.9; S['title']['ob'].scale = (sc, sc, sc)
