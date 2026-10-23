"""The River Through Time (Cutaway showcase series, film 1; 20 s, 16:9).

A stream on a flat grassy block cuts down through the rock over ages until a canyon stands. Time is shown by the sun
racing round the sky and the light shifting, never by text. Fossils (an ammonite, a fish, a trilobite) are bared in the
canyon wall as the water cuts past them, each catching a museum light. The last shot is today: golden hour, a tiny
hiker on the rim, birds over the canyon.

Shots (frame = t * 24):
  1 then    0.0-6.0 s   wide three-quarter, a slow push: the flat block and its stream; time starts to race at 2.6 s
  2 ages    6.0-14.0 s  in front of the cut face, looking up the canyon; the camera cranes down with the water while
                        the fossils are bared one by one (change of scale: we go close to see the detail)
  3 today  14.0-20.0 s  low three-quarter into the setting sun; time has stopped; the hiker walks to the rim and stops

Kit: films/styles/cutaway/cutaway.py and cinematic/extras.py (imported, never edited). The block itself is built here,
because the kit's block is static: this one is re-shaped every frame (a height field carved over time), its rock is
banded by world height (so the canyon walls and the cut face share the same layers), and the water box sinks with it.
"""
import math
import os
import sys

import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, '..', '..', '..', '..'))
for p in (os.path.join(root, 'films', 'styles', 'cutaway', 'cinematic'), os.path.join(root, 'films', 'styles', 'cutaway')):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import extras as ex  # noqa: E402
from cutaway import G, srgb  # noqa: E402

SHOTS = [{'name': 'then', 'dur': 6.0}, {'name': 'ages', 'dur': 8.0}, {'name': 'today', 'dur': 6.0}]
DURATION = sum(s['dur'] for s in SHOTS)
SETTINGS = {'samples': 20, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - High Contrast', 'exposure': 0.1,
            'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 4.0, 'adaptive_min_samples': 8, 'denoising_prefilter': 'FAST'}
CHECK = {'then_open': 24, 'then_end': 130, 'ages_a': 190, 'ages_b': 260, 'ages_c': 320, 'today': 430}   # check-still frames

SX, SY, DEPTH = 4.0, 3.4, 1.5
W_RIM = 0.92          # final half width of the canyon at the rim (m)
D_FINAL = 1.03        # final depth of the canyon floor below the plateau (m)
SLOPE, F_MAX = 0.62, 1.15   # the cutting notch: side slope (raw depth per m) and its last floor depth (below the final floor, so it ends inside hf)
TITLE = 'The River Through Time'
FONT = os.path.join(root, 'ads', 'fonts', 'InstrumentSans.ttf')

# rock beds, top-down (time runs down): name, thickness m, sRGB, pebble density, erodibility k (hard beds stand as cliffs)
LAYERS = [('soil', 0.035, (0.30, 0.21, 0.13), 0.05, 1.0),
          ('pale limestone', 0.13, (0.90, 0.82, 0.66), 0.04, 0.25),      # the ammonite
          ('tan slope', 0.09, (0.78, 0.56, 0.36), 0.10, 2.2),
          ('buff sandstone', 0.14, (0.92, 0.76, 0.52), 0.03, 0.30),
          ('red shale', 0.12, (0.62, 0.22, 0.14), 0.10, 2.3),
          ('orange sandstone', 0.17, (0.84, 0.40, 0.20), 0.06, 0.35),
          ('grey limestone', 0.16, (0.66, 0.58, 0.54), 0.10, 0.28),      # the fish
          ('green shale', 0.15, (0.50, 0.54, 0.44), 0.05, 0.9),           # the trilobite
          ('brown sandstone', 0.09, (0.54, 0.35, 0.22), 0.25, 0.5),
          ('dark schist', 1.0, (0.21, 0.20, 0.23), 0.35, 0.4)]
SUN_END = (112.0, 7.5)          # golden hour, behind the block from the last camera
SUN_START = (-40.0, 38.0)       # morning light from the camera side
DAYS = 2.0                      # extra full turns of the sun during the time-lapse


# ============================================================================================ time
def s5(a, b, t): return ex.ease5((t - a) / (b - a))
_tt = np.linspace(0.0, 20.0, 4001)
_rate = np.array([ex.ease((t - 3.2) / 3.0) * (1.0 - ex.ease((t - 12.2) / 1.6)) for t in _tt])
_S = np.concatenate([[0.0], np.cumsum(0.5 * (_rate[1:] + _rate[:-1]) * np.diff(_tt))]); _S /= _S[-1]
def carve_s(t): return float(np.interp(t, _tt, _S))   # 0 = the stream on the flat block, 1 = today's canyon (eased in, steady, eased out)
def clock(t): return s5(2.6, 14.4, t)            # sun phase: races in the middle, still at both ends


def sun_at(t):
    """Sun azimuth and elevation (degrees) at time t: still, then racing round DAYS extra turns, then still at golden hour."""
    u = clock(t); az0, el0 = SUN_START; az1, el1 = SUN_END[0] + 360.0 * DAYS, SUN_END[1]
    az = az0 + (az1 - az0) * u
    el = el0 + (el1 - el0) * ex.ease(u) + 16.0 * math.sin(2 * math.pi * (DAYS + 0.5) * u) * math.sin(math.pi * u)
    return az, max(4.0, el)


# ============================================================================================ the land (height field)
_cum = np.cumsum([0.0] + [l[1] for l in LAYERS]); _Z = np.linspace(0, 2.0, 801)
_k = np.array([LAYERS[min(np.searchsorted(_cum, z, 'right') - 1, len(LAYERS) - 1)][4] for z in _Z])
_R = np.concatenate([[0.0], np.cumsum(0.5 * (_k[1:] + _k[:-1]) * np.diff(_Z))])
_R *= D_FINAL / np.interp(D_FINAL, _Z, _R)       # raw depth D_FINAL maps to real depth D_FINAL


def xc(y): return 0.10 * np.sin(1.2 * np.asarray(y) + 0.5) - 0.06


def raw_parts(x, y):
    """Static per-point data: plateau micro relief, distance from the river's line (with a ragged rim)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    plat = 0.005 * cw.fbm(x, y, 3, 3, 2.5) + 0.002 * cw.fbm(x, y, 9, 2, 12.0)
    a = np.abs(x - xc(y)); d = a + (0.045 * cw.fbm(x, y, 17, 3, 1.4) + 0.012 * cw.fbm(x, y, 23, 2, 6.0)) * cw.smooth(0.04, 0.30, a)   # ragged rim, clean river bed
    wmul = 1.0 + 0.10 * np.sin(0.9 * y + 1.3)
    return plat, np.maximum(d, 0.0), wmul


def height(x, y, s, parts=None):
    """Surface height at carve stage s. The final canyon hf is terraced by the beds; while it forms, the river cuts a
    V-shaped notch whose floor sinks with s; the surface is the higher of the two, so each point of the final wall is bared
    once the notch passes it (upper walls first, the deepest last) and stays put after that."""
    plat, d, wmul = parts if parts is not None else raw_parts(x, y)
    pf = 1.0 - cw.smooth(0.10, 1.0, d / (W_RIM * wmul))
    hf = -np.interp(D_FINAL * pf, _R, _Z)
    fl = 0.07 + (F_MAX - 0.07) * s ** 0.9
    rv = np.maximum(fl - SLOPE * np.sqrt(d * d + 0.0004), 0.0)
    h = np.maximum(hf, -np.interp(rv, _R, _Z))
    return h + plat * (1.0 - np.clip(-h / 0.03, 0.0, 1.0))


def floor_at(s): return float(height(np.array([xc(0.0)]), np.array([0.0]), s, (np.zeros(1), np.zeros(1), np.ones(1)))[0])
def level_at(s): return floor_at(s) + 0.030


class Terrain:
    """Top grid (dense across the canyon), walls straight down from its ring, a water box; reshaped by set(s)."""
    def __init__(self, kit):
        bpy = kit.bpy; self.kit = kit
        xin = np.arange(-1.30, 1.18, 0.012); xl = np.linspace(-SX / 2, -1.30, 26)[:-1]; xr = np.linspace(1.18, SX / 2, 29)[1:]
        self.xs = np.concatenate([xl, xin, xr]); self.ys = np.linspace(-SY / 2, SY / 2, int(SY / 0.024) + 1)
        nx, ny = len(self.xs), len(self.ys); X, Y = np.meshgrid(self.xs, self.ys); self.X, self.Y = X, Y
        self.parts = raw_parts(X, Y)
        H = height(X, Y, 0.0, self.parts)
        V = np.stack([X.ravel(), Y.ravel(), H.ravel()], 1); ii = np.arange(nx * ny).reshape(ny, nx)
        Ft = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
        self.lv_val = []                         # material Value nodes that follow the water level
        self.mat = mat_land(kit, self); self.mat_bottom = cw.mat_simple(kit, 'rt_bottom', (0.12, 0.11, 0.12), 0.95)
        self.top = cw.mk_mesh(bpy, 'rt_top', V, Ft, [self.mat], None, True, kit.coll)
        self.ring = [(i, 0) for i in range(nx)] + [(nx - 1, j) for j in range(1, ny)] + [(i, ny - 1) for i in range(nx - 2, -1, -1)] + [(0, j) for j in range(ny - 2, 0, -1)]
        self.rows = 40; nr = len(self.ring)
        self.ri = np.array([j * nx + i for i, j in self.ring]); self.uu = (np.arange(self.rows + 1) / self.rows) ** 1.5
        WV = self._walls(H.ravel()); WF = []
        for k in range(nr):
            k2 = (k + 1) % nr
            for r in range(self.rows): a = k * (self.rows + 1) + r; b = k2 * (self.rows + 1) + r; WF.append((a, a + 1, b + 1, b))
        WF.append(tuple([k * (self.rows + 1) + self.rows for k in range(nr)][::-1]))
        self.walls = cw.mk_mesh(bpy, 'rt_walls', WV, WF, [self.mat, self.mat_bottom], [0] * (len(WF) - 1) + [1], False, kit.coll)
        e = 0.0015; bx = [(-SX / 2 + e, -SY / 2 + e), (SX / 2 - e, -SY / 2 + e), (SX / 2 - e, SY / 2 - e), (-SX / 2 + e, SY / 2 - e)]
        zb = -DEPTH + 0.02; self.wv = [(x, y, zb) for x, y in bx] + [(x, y, 0.0) for x, y in bx]
        WFf = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        self.water_mat = cw.mat_water(kit, 'rt_water', tint=(0.06, 0.50, 0.54), density=9.0, level=0.0, glow_amt=0.04)
        for n in self.water_mat.node_tree.nodes:      # the kit bakes the level into the meniscus line: drive it instead
            if n.bl_idname == 'ShaderNodeMath' and n.operation == 'SUBTRACT' and abs(n.inputs[1].default_value + 0.005) < 1e-6: self.lv_val.append((n.inputs[1], -0.005))
        self.water = cw.mk_mesh(bpy, 'rt_water', self.wv, WFf, [self.water_mat], None, False, kit.coll)
        self.s = -1.0; self.set(0.0)

    def _walls(self, Hflat):
        zt = Hflat[self.ri]; X = self.X.ravel()[self.ri]; Y = self.Y.ravel()[self.ri]
        Z = zt[:, None] + (-DEPTH - zt[:, None]) * self.uu[None, :]
        return np.stack([np.repeat(X, self.rows + 1), np.repeat(Y, self.rows + 1), Z.ravel()], 1)

    def set(self, s):
        if abs(s - self.s) < 1e-7: return
        self.s = s; H = height(self.X, self.Y, s, self.parts).ravel()
        V = np.stack([self.X.ravel(), self.Y.ravel(), H], 1).astype(np.float32)
        me = self.top.data; me.vertices.foreach_set('co', V.ravel()); me.update()
        me = self.walls.data; me.vertices.foreach_set('co', self._walls(H).astype(np.float32).ravel()); me.update()
        lv = level_at(s); wv = np.array(self.wv, np.float32); wv[4:, 2] = lv
        me = self.water.data; me.vertices.foreach_set('co', wv.ravel()); me.update()
        for v in self.lv_val:
            if isinstance(v, tuple): v[0].default_value = lv + v[1]
            else: v.default_value = lv


def mat_land(kit, terr):
    """One material for the top and the cut faces: rock beds by world height (gently wobbled), grain, laminae, pebbles;
    grass on the untouched plateau; ledges dusted pale; rock darkened and wet at the waterline; a sandy bed under water."""
    m = cw._new_mat(kit.bpy, 'rt_land'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    geo = g.node('ShaderNodeNewGeometry'); nz = g.sep(geo.outputs['Normal'])[2]
    hz = g.math('ADD', sx[0], sx[1])
    depth = g.math('ADD', g.math('MULTIPLY', sx[2], -1.0), g.math('MULTIPLY', sx[0], 0.012))
    wob = g.noise(g.comb(g.math('MULTIPLY', hz, 1.0), 0.0, g.math('MULTIPLY', depth, 0.3)), 2.0, 3.0)
    s = g.math('ADD', depth, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.02))
    total = 1.6; stops = []; pst = []; acc = 0.0; soft = 0.006
    for k, l in enumerate(LAYERS):
        a = acc / total; b = min(1.0, (acc + l[1]) / total) if k < len(LAYERS) - 1 else 1.0
        stops += [(min(1, a + soft / total) if k else 0.0, tuple(min(1, c * 1.06) for c in l[2])), (max(0.0, b - soft / total) if k < len(LAYERS) - 1 else 1.0, tuple(c * 0.86 for c in l[2]))]
        pst += [(a, (l[3],) * 3)]; acc += l[1]
    fac = g.math('DIVIDE', s, total, clamp=True)
    col = g.ramp(fac, stops); pden = g.sep(g.ramp(fac, pst, 'CONSTANT'))[0]
    n1 = g.noise(pos, 70.0, 5.0, 0.6)
    lam = g.noise(g.comb(g.math('MULTIPLY', hz, 4.0), g.math('MULTIPLY', s, 70.0), 0.0), 1.0, 2.0, 0.5)      # thin laminae
    col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], 0.40), col, g.mix(0.55, col, (0, 0, 0), 'MULTIPLY'))
    col = g.mix(g.math('MULTIPLY', lam.outputs['Fac'], 0.18), col, g.mix(0.5, col, (1, 1, 1), 'SCREEN'))
    vp = g.voronoi(pos, 30.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    radius = g.math('MULTIPLY', g.math('MULTIPLY', pden, 0.42), g.math('MULTIPLY_ADD', rr[0], 0.8, 0.4))
    peb = g.math('MULTIPLY', g.math('SUBTRACT', radius, vp.outputs['Distance']), 25.0, clamp=True)
    col = g.mix(peb, col, g.mix(rr[1], srgb((0.40, 0.38, 0.36)), srgb((0.80, 0.76, 0.68))))
    # ledges: flat rock inside the canyon gathers pale dust
    inside = g.math('LESS_THAN', sx[2], -0.03)
    ledge = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', nz, 0.80), 6.0, clamp=True), inside)
    col = g.mix(g.math('MULTIPLY', ledge, 0.35), col, srgb((0.86, 0.76, 0.60)))
    # grass on the plateau that the river has not reached
    nb = g.noise(pos, 1.6, 3.0); nf = g.noise(pos, 45.0, 4.0)
    ground = g.mix(nb.outputs['Fac'], srgb((0.22, 0.32, 0.11)), srgb((0.26, 0.42, 0.12)))
    ground = g.mix(g.math('MULTIPLY', nf.outputs['Fac'], 0.5), ground, srgb((0.12, 0.16, 0.06)))
    gm = g.math('MULTIPLY', g.math('MULTIPLY', g.math('ADD', sx[2], 0.014), 1 / 0.010, clamp=True), g.math('MULTIPLY', g.math('SUBTRACT', nz, 0.72), 4.0, clamp=True))
    col = g.mix(gm, col, ground)
    # water line and bed (the level follows the river every frame)
    lv = g.value(0.0, 'rt_level'); terr.lv_val.append(lv.node.outputs[0] if hasattr(lv, 'node') else lv)
    wet = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', lv, 0.03), sx[2]), 30.0, clamp=True)
    col = g.mix(g.math('MULTIPLY', wet, 0.40), col, (0, 0, 0))
    under = g.math('MULTIPLY', g.math('SUBTRACT', lv, sx[2]), 60.0, clamp=True)
    bed = g.mix(nf.outputs['Fac'], srgb((0.50, 0.44, 0.34)), srgb((0.36, 0.32, 0.26)))
    col = g.mix(g.math('MULTIPLY', under, 0.8), col, bed)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.9})
    g.put(p, 'Roughness', g.math('SUBTRACT', 0.9, g.math('MULTIPLY', wet, 0.55)))
    h = g.math('ADD', g.math('MULTIPLY', n1.outputs['Fac'], 0.35), g.math('ADD', g.math('MULTIPLY', peb, 0.8), g.math('MULTIPLY', lam.outputs['Fac'], 0.5)))
    bm = g.node('ShaderNodeBump', ins={'Strength': 0.45, 'Height': h, 'Distance': 0.006}); g.put(p, 'Normal', bm)
    cw._finish(g, p); return m


# ============================================================================================ sky, sun, clouds, mist
class Sky:
    """A golden-hour sky dome (camera rays) that follows a moving sun; a dim cool ambient for everything else; the sun lamp;
    a far floor that melts into the horizon; cloud-gap shadows that race with the time-lapse."""
    def __init__(self, kit):
        bpy = kit.bpy; self.kit = kit
        wd = bpy.data.worlds.new('rt_world'); bpy.context.scene.world = wd
        try: wd.use_nodes = True
        except Exception: pass
        nt = wd.node_tree; nt.nodes.clear(); g = G(nt, kit)
        self.sv = [g.value(0.0) for _ in range(3)]; self.hv = [g.value(0.0) for _ in range(3)]
        self.warm = g.value(1.0, 'rt_warm')
        sd = g.comb(*self.sv); sh = g.comb(*self.hv)
        tc = g.node('ShaderNodeTexCoord'); d = g.vmath('NORMALIZE', tc.outputs['Generated']); dz = g.sep(d)[2]
        dp = g.math('MAXIMUM', g.vmath('DOT_PRODUCT', d, sd), 0.0)
        hz = g.vmath('NORMALIZE', g.vmath('MULTIPLY', d, (1, 1, 0))); hd = g.math('MAXIMUM', g.vmath('DOT_PRODUCT', hz, sh), 0.0)
        horizon = g.mix(self.warm, srgb((0.90, 0.92, 0.94)), srgb((0.98, 0.62, 0.36)))
        away = g.mix(self.warm, srgb((0.70, 0.80, 0.92)), srgb((0.46, 0.40, 0.54)))
        zenith = g.mix(self.warm, srgb((0.26, 0.48, 0.84)), srgb((0.12, 0.18, 0.38)))
        horiz = g.mix(g.math('POWER', hd, 2.2), away, horizon)
        sky = g.mix(g.math('POWER', g.math('MAXIMUM', dz, 0.0), 0.55), horiz, zenith)
        below = g.mix(g.math('MINIMUM', g.math('MULTIPLY', g.math('ABSOLUTE', g.math('MINIMUM', dz, 0.0)), 1.6), 1.0), horiz, g.mix(self.warm, srgb((0.52, 0.54, 0.56)), srgb((0.40, 0.30, 0.30))))
        col = g.mix(g.math('GREATER_THAN', dz, 0.0), below, sky)
        glow = g.math('ADD', g.math('MULTIPLY', g.math('POWER', dp, 18.0), 0.6), g.math('MULTIPLY', g.math('POWER', dp, 1400.0), 30.0))
        col = g.mix(1.0, col, g.vmath('SCALE', srgb((1.0, 0.72, 0.45))[:3], scale=glow), 'ADD')
        bg_cam = g.node('ShaderNodeBackground', ins={'Color': col, 'Strength': 1.0})
        bg_light = g.node('ShaderNodeBackground', ins={'Color': g.mix(0.75, (0.42, 0.52, 0.85), col), 'Strength': 0.26})
        lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
        g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bg_light, mx.inputs[1]); g.link(bg_cam, mx.inputs[2])
        o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
        self.sun = cw._sun(kit, 0, 45, 5.0, 1.2, (1, 1, 1), 'rt_sun')
        # cool fill from the camera side and a warm rim from the late sun
        def area(name, az, el, dist, size, power, color, target=(0, 0, -0.3)):
            ld = bpy.data.lights.new(name, 'AREA'); ld.size = size; ld.shape = 'DISK'; ld.energy = power; ld.color = color
            ob = bpy.data.objects.new(name, ld); kit.coll.objects.link(ob); ob.location = tuple(np.array(target) + ex.sph(az, el) * dist)
            ex.look_at(ob, target); ob.visible_camera = False; return ob
        self.fill = area('rt_fill', -40, 30, 9.0, 6.0, 650.0, (0.62, 0.74, 1.0))
        self.rim = area('rt_rim', SUN_END[0] + 62, 22, 8.0, 3.0, 1200.0, (1.0, 0.78, 0.58), (0, 0, 0.1))
        # far floor
        mf = cw._new_mat(bpy, 'rt_floor'); g2 = G(mf.node_tree, kit); tc2 = g2.node('ShaderNodeTexCoord')
        r = g2.vmath('LENGTH', g2.vmath('MULTIPLY', tc2.outputs['Object'], (1, 1, 0)))
        far = g2.math('MULTIPLY', g2.math('SUBTRACT', r, 2.4), 1 / 7.0, clamp=True)
        pf = g2.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.50, 0.46, 0.42)), 'Roughness': 0.95})
        self.fwarm = g2.value(1.0)
        e = g2.node('ShaderNodeEmission', ins={'Color': g2.mix(self.fwarm, srgb((0.86, 0.88, 0.90)), srgb((0.94, 0.66, 0.48))), 'Strength': 0.75})
        mx2 = g2.node('ShaderNodeMixShader'); g2.link(g2.math('POWER', far, 0.7), mx2.inputs[0]); g2.link(pf, mx2.inputs[1]); g2.link(e, mx2.inputs[2]); cw._finish(g2, mx2)
        try: mf.cycles.emission_sampling = 'NONE'
        except Exception: pass
        cw._plane(kit, 'rt_floor', 60, -DEPTH - 0.0005, mf)
        # cloud gaps (shadow only), moved along with the sun; the pattern drifts in sky time
        mg = cw._new_mat(bpy, 'rt_gobo'); g3 = G(mg.node_tree, kit); tc3 = g3.node('ShaderNodeTexCoord'); self.gclock = g3.value(0.0)
        pp = g3.vmath('ADD', tc3.outputs['Object'], g3.comb(self.gclock, g3.math('MULTIPLY', self.gclock, 0.3), 0.0))
        n = g3.noise(pp, 0.55, 3.0, 0.6, '4D', g3.math('MULTIPLY', self.gclock, 0.15))
        blk = g3.math('MULTIPLY', g3.math('SUBTRACT', n.outputs['Fac'], 0.47), 7.0, clamp=True)
        tr = g3.node('ShaderNodeBsdfTransparent'); df = g3.node('ShaderNodeBsdfDiffuse', ins={'Color': (0, 0, 0)}); mx3 = g3.node('ShaderNodeMixShader')
        g3.link(g3.math('MULTIPLY', blk, 0.85), mx3.inputs[0]); g3.link(tr, mx3.inputs[1]); g3.link(df, mx3.inputs[2]); cw._finish(g3, mx3)
        V = [(-6, -4, 0), (6, -4, 0), (6, 4, 0), (-6, 4, 0)]
        self.gobo = cw.mk_mesh(bpy, 'rt_gobo', V, [(0, 1, 2, 3)], [mg], None, False, kit.coll)
        for a in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(self.gobo, a, False)

    def set(self, t):
        from mathutils import Vector
        az, el = sun_at(t); sd = ex.sph(az, el); h = np.array([sd[0], sd[1], 0.0]); h /= np.linalg.norm(h)
        for v, c in zip(self.sv, sd): v.default_value = float(c)
        for v, c in zip(self.hv, h): v.default_value = float(c)
        warm = float(cw.smooth(34.0, 10.0, el)); self.warm.default_value = warm; self.fwarm.default_value = warm
        self.sun.rotation_euler = Vector(tuple(-sd)).to_track_quat('-Z', 'Y').to_euler()
        self.sun.data.color = tuple(np.array((1.0, 0.94, 0.86)) * (1 - warm) + np.array((1.0, 0.64, 0.38)) * warm)
        self.sun.data.energy = 4.6 + 1.2 * warm
        self.rim.data.energy = 1200.0 * cw.smooth(0.85, 1.0, clock(t))
        self.gobo.location = tuple(np.array([0, 0, 0.2]) + sd * 4.5)
        self.gobo.rotation_euler = Vector(tuple(-sd)).to_track_quat('Z', 'Y').to_euler()
        self.gclock.default_value = float(0.02 * t + 2.2 * clock(t))
        return az, el


def mist(kit):
    """Haze sheets lying in the canyon (camera rays only), soft-edged by the canyon walls; drift with the wind."""
    bpy = kit.bpy; m = cw._new_mat(bpy, 'rt_mist'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); tv = ex.time_value(kit, g, 'rt_mist_t')
    gain = g.value(0.0, 'rt_mist_gain'); p = tc.outputs['Object']; px, py, pz = g.sep(p)
    q = g.vmath('ADD', p, g.comb(g.math('MULTIPLY', tv, 0.03), g.math('MULTIPLY', tv, 0.012), 0.0))
    n = g.noise(q, 2.2, 3.0, 0.55); a = g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.35), 2.2, clamp=True)
    edge = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', px, -0.06)), 1 / 0.75), clamp=True)
    ends = g.math('MULTIPLY', g.math('SUBTRACT', SY / 2, g.math('ABSOLUTE', py)), 8.0, clamp=True)
    a = g.math('MULTIPLY', g.math('MULTIPLY', a, edge), g.math('MULTIPLY', ends, gain))
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.80, 0.60))}); g.put(e, 'Strength', g.math('MULTIPLY', a, 0.22))
    tr = g.node('ShaderNodeBsdfTransparent'); ad = g.node('ShaderNodeAddShader'); g.link(tr, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    obs = []
    for k, z in enumerate((-0.86, -0.62, -0.36)):
        V = [(-1.2, -SY / 2 + 0.003, z), (1.1, -SY / 2 + 0.003, z), (1.1, SY / 2 - 0.003, z), (-1.2, SY / 2 - 0.003, z)]
        ob = cw.mk_mesh(bpy, f'rt_mist{k}', V, [(0, 1, 2, 3)], [m], None, False, kit.coll)
        for at in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_shadow', 'visible_volume_scatter'): setattr(ob, at, False)
        obs.append(ob)
    return gain.node.outputs[0] if hasattr(gain, 'node') else gain


# ============================================================================================ life on the plateau
class Plain:
    """A minimal Land for the kit's scatter(): static plateau height (used for what never gets carved)."""
    def __init__(self):
        self.size = (SX, SY); self.depth = DEPTH; self.objects = {}; self.mats = {}; self.pal = dict(cw.SEASONS['summer'])
        self.height = lambda x, y: height(x, y, 1.0)


def vegetation(kit, land, terr):
    rng = np.random.default_rng(7); pal = land.pal
    P = cw._jitter_grid(rng, SX, SY, 0.034, 0.006)
    hfin = height(P[:, 0], P[:, 1], 1.0); keepdry = rng.uniform(0, 1, len(P)) < 0.85
    still = (hfin > -0.004) & keepdry; go = (hfin <= -0.004) & keepdry
    tufts = cw.proto_tufts(kit, pal, 6, 0.05, 3) + cw.proto_tufts(kit, pal, 2, 0.08, 4, (16, 24))
    coll = kit.bpy.data.collections.new('rt_tufts')
    for ob in tufts: coll.objects.link(ob)
    cw.scatter(kit, land, 'rt_grass', coll, P[still], scale=rng.uniform(0.7, 1.3, still.sum()), sway=0.26, speed=0.9)
    Q = P[go]; base = rng.uniform(0.7, 1.3, len(Q)); parts = raw_parts(Q[:, 0], Q[:, 1])
    dyn = cw.scatter(kit, land, 'rt_grass_go', coll, np.column_stack([Q, np.zeros(len(Q))]), scale=base, sway=0.26, speed=0.9)
    def follow(s):
        h = height(Q[:, 0], Q[:, 1], s, parts); sc = base * cw.smooth(-0.012, -0.004, h)
        me = dyn.data; me.vertices.foreach_set('co', np.column_stack([Q, h - 0.004]).astype(np.float32).ravel())
        me.attributes['scale'].data.foreach_set('value', sc.astype(np.float32)); me.update()
    q = cw._jitter_grid(rng, SX, SY, 0.06, 0.03); hq = height(q[:, 0], q[:, 1], 1.0)
    fz = 0.5 + 0.5 * cw.fbm(q[:, 0], q[:, 1], 51, 2, 1.6); sel = (hq > -0.004) & (fz > 0.72) & (rng.uniform(0, 1, len(q)) < 0.5)
    cw.scatter(kit, land, 'rt_flowers', cw.proto_flowers(kit, 4, 3), q[sel], sway=0.2, speed=0.9)
    spots = [(-1.70, 1.25, 1.25, 'round'), (-1.55, 0.55, 0.95, 'cone'), (-1.82, -0.15, 1.05, 'round'), (1.62, 1.35, 1.2, 'round'),
             (1.78, 0.62, 0.9, 'cone'), (1.45, 0.10, 1.0, 'cone'), (-1.40, 1.50, 0.8, 'cone')]
    protos = cw.proto_trees(kit, pal, ('round', 'cone'), 3, 5); kinds = ['round', 'cone']
    T = np.array([(a, b) for a, b, _, _ in spots]); var = np.array([kinds.index(k) * 3 + i % 3 for i, (_, _, _, k) in enumerate(spots)])
    cw.scatter(kit, land, 'rt_trees', protos, T, scale=np.array([s for _, _, s, _ in spots]), variant=var, sway=0.03, speed=0.5, sink=0.01)
    land.trees = T
    rk = cw.proto_rocks(kit, 5, 9, color=(0.80, 0.70, 0.56), moss=0.1)
    B = np.array([(-1.20, -1.40), (-1.28, 0.30), (1.15, -0.85), (1.22, 0.95), (-1.6, -1.0), (1.55, -1.45)])
    cw.scatter(kit, land, 'rt_boulders', rk, B, scale=rng.uniform(0.05, 0.11, len(B)), sink=0.02)
    return follow


# ============================================================================================ fossils in the canyon wall
def wall_point(y0, z0):
    """Point on the final west canyon wall at (y0, depth z0), its outward normal (into the canyon)."""
    xs = np.linspace(xc(y0) - W_RIM * 1.3, xc(y0), 600); hs = height(xs, np.full_like(xs, y0), 1.0)
    i = int(np.argmax(hs < z0)); x0 = float(xs[i]); e = 0.004
    hx = (height(np.array([x0 + e]), np.array([y0]), 1.0) - height(np.array([x0 - e]), np.array([y0]), 1.0))[0] / (2 * e)
    hy = (height(np.array([x0]), np.array([y0 + e]), 1.0) - height(np.array([x0]), np.array([y0 - e]), 1.0))[0] / (2 * e)
    n = np.array([-hx, -hy, 1.0]); n /= np.linalg.norm(n)
    return np.array([x0, y0, float(height(np.array([x0]), np.array([y0]), 1.0)[0])]), n


def place_on_wall(ob, P, n, sink=0.006, spin=0.0):
    """Face-local axes (X along, Y into the rock, Z up) onto the wall at P with outward normal n."""
    from mathutils import Matrix
    Y = -n; up = np.array([0, 0, 1.0]); Z = up - (up @ Y) * Y; Z /= np.linalg.norm(Z); X = np.cross(Y, Z)
    c, s_ = math.cos(spin), math.sin(spin); X, Z = c * X + s_ * Z, -s_ * X + c * Z
    M = Matrix(((X[0], Y[0], Z[0]), (X[1], Y[1], Z[1]), (X[2], Y[2], Z[2])))
    ob.rotation_euler = M.to_euler(); ob.location = tuple(P + Y * sink)


def fish_pieces():
    """A fossil fish in relief (face-local, proud toward -Y): skull, spine, ribs, fins, tail."""
    out = []; L = 0.10
    sp = np.array([(x, -0.004, 0.012 * math.sin(x / L * 2.2)) for x in np.linspace(-L, L * 0.75, 18)])
    V, F = cw._tube(sp, np.linspace(0.0022, 0.0034, len(sp)), 6); out.append((V, F, 0))
    V, F = ex.ell((L * 0.92, -0.004, 0.012 * math.sin(2.0)), (0.034, 0.007, 0.024), 2, 0.12, 4); out.append((V, F, 0))
    V, F = ex.ell((L * 1.02, -0.010, 0.016), (0.006, 0.003, 0.006), 1); out.append((V, F, 1))      # the eye
    for k in range(13):
        x = -L * 0.65 + k * L * 1.3 / 12; z0 = 0.012 * math.sin(x / L * 2.2); ln = 0.030 * (1 - abs(k - 7) / 14)
        for sgn in (1, -1):
            V, F = ex.cone((x, -0.004, z0), (x - 0.010, -0.003, z0 + sgn * ln), 0.0016, 0.0004, 5); out.append((V, F, 0))
    for k in range(7):
        a = math.radians(-34 + k * 11); V, F = ex.cone((-L, -0.004, 0.0), (-L - 0.045 * math.cos(a), -0.003, 0.045 * math.sin(a)), 0.0015, 0.0004, 5); out.append((V, F, 0))
    for k in range(5):
        x = -L * 0.1 + k * 0.012; V, F = ex.cone((x, -0.004, 0.022), (x - 0.010, -0.003, 0.040), 0.0012, 0.0003, 5); out.append((V, F, 0))
    return out


class Fossils:
    def __init__(self, kit, land):
        self.kit = kit; self.items = []
        eg = ex.Eggs(kit, land)
        eg.ammonite('-Y', 0.0, -0.2, R=0.095, tilt=0.0); eg.trilobite('-Y', 0.0, -0.4, Lt=0.25, tilt=0.0)
        bone = ex.mat_pbr(kit, 'rt_fishbone', (0.40, 0.30, 0.22), 0.4, coat=0.35, cavity=0.8); dark = ex.mat(kit, 'rt_eye', (0.06, 0.05, 0.05), 0.5)
        fish = ex.part(kit, 'rt_fish', fish_pieces(), [bone, dark]); fish.scale = (1.45, 1.45, 1.45)
        bpy = kit.bpy; O = bpy.data.objects
        for nm, ob, spot, y0, z0, spin in (('ammonite', O['ex_ammonite'], O['ex_spot_ammonite'], -1.40, -0.10, 0.3),
                                           ('fish', fish, None, -1.30, -0.54, 0.12),
                                           ('trilobite', O['ex_trilobite'], O['ex_spot_trilobite'], -1.36, -0.915, -0.4)):
            P, n = wall_point(y0, z0)
            if nm == 'ammonite':   # weathered half out of the cliff, turned toward the crane so the spiral reads (on the wall plane it is seen edge-on)
                v = np.array((0.80, -2.70, 0.20)) - P; v /= np.linalg.norm(v); nv = 0.3 * n + 0.7 * v; nv /= np.linalg.norm(nv)
                place_on_wall(ob, P + n * 0.03, nv, 0.0, spin)
            else: place_on_wall(ob, P, n, 0.006, spin)
            if spot is None:
                ld = bpy.data.lights.new('rt_spot_fish', 'SPOT'); ld.spot_size = math.radians(30); ld.spot_blend = 0.75; ld.shadow_soft_size = 0.03; ld.color = (1.0, 0.9, 0.76)
                spot = bpy.data.objects.new('rt_spot_fish', ld); kit.coll.objects.link(spot); spot.visible_camera = False
            spot.location = tuple(P + n * 0.42 + np.array([0, -0.12, 0.26])); ex.look_at(spot, P)
            # bared when the cut surface just outside it drops below its top
            q = P + n * 0.02; ts = np.linspace(3.0, 14.0, 1101)
            hs = np.array([height(np.array([q[0]]), np.array([q[1]]), carve_s(t))[0] for t in ts])
            t_rev = float(ts[int(np.argmax(hs < P[2] + 0.025))])
            self.items.append({'name': nm, 'ob': ob, 'spot': spot, 'P': P, 'n': n, 't': t_rev})
            print(f'fossil {nm}: bared at {t_rev:.2f} s, at {np.round(P, 3).tolist()}', flush=True)

    def update(self, t):
        for it in self.items:
            f = ex.ease((t - it['t']) / 0.8); it['spot'].data.energy = 4.0 * f
            it['ob'].hide_render = t < it['t'] - 1.5


# ============================================================================================ the hiker
def hiker(kit):
    """A tiny hiker (7.5 cm) with a red pack and a pole: walks to the rim in the last shot, stops, looks in."""
    bpy = kit.bpy; m = {k: ex.mat(kit, 'rt_h_' + k, c, r) for k, c, r in (('cloth', (0.20, 0.26, 0.34), 0.7), ('pack', (0.78, 0.16, 0.10), 0.6),
                                                                       ('skin', (0.78, 0.56, 0.42), 0.5), ('boot', (0.16, 0.12, 0.09), 0.8),
                                                                       ('hat', (0.86, 0.78, 0.58), 0.7), ('pole', (0.70, 0.70, 0.72), 0.3))}
    root_ob = ex.empty(kit, 'rt_hiker'); root_ob.scale = (1.5, 1.5, 1.5)
    body = ex.part(kit, 'rt_hiker_body', [(*ex.ell((0, 0, 0.052), (0.0085, 0.0065, 0.016), 2), 0), (*ex.ell((-0.0085, 0, 0.055), (0.0055, 0.008, 0.012), 2), 1),
                                         (*ex.ell((0.001, 0, 0.0735), (0.0058, 0.0058, 0.0064), 2), 2), (*ex.ell((0.001, 0, 0.0785), (0.0085, 0.0085, 0.0018), 2), 3)],
                   [m['cloth'], m['pack'], m['skin'], m['hat']], root_ob)
    legs = []
    for side in (-1, 1):
        lg = ex.part(kit, f'rt_hiker_leg{side}', [(*cw._tube([(0, 0, 0), (0, 0, -0.018), (0, 0, -0.036)], [0.0034, 0.003, 0.0026], 6), 0),
                                                 (*ex.ell((0.003, 0, -0.037), (0.0048, 0.0028, 0.0022), 1), 1)], [m['cloth'], m['boot']], root_ob, (0, side * 0.0036, 0.038))
        legs.append((lg, side))
    arm = ex.part(kit, 'rt_hiker_arm', [(*cw._tube([(0, 0, 0), (0.004, 0, -0.012), (0.010, 0, -0.020)], [0.0024, 0.0022, 0.002], 6), 0),
                                        (*cw._tube([(0.010, 0, -0.020), (0.012, 0, 0.0), (0.016, 0, -0.06)], [0.0007] * 3, 4), 1)], [m['cloth'], m['pole']], root_ob, (0.001, -0.0095, 0.064))
    A = np.array([0.98, -1.62]); B = np.array([0.70, -1.30]); T0, T1 = 14.6, 18.2
    def pose(t):
        root_ob.hide_render = t < 14.0
        for ob in [body, arm] + [l for l, _ in legs]: ob.hide_render = t < 14.0
        u = min(1.0, max(0.0, (t - T0) / (T1 - T0))); e = u * u * (3 - 2 * u) if u < 1 else 1.0
        p = A + (B - A) * (0.5 * u + 0.5 * e) if u < 1 else B
        z = float(height(np.array([p[0]]), np.array([p[1]]), carve_s(t))[0])
        d = B - A; yaw = math.atan2(d[1], d[0]); walking = 0.0 < u < 1.0
        ph = 2 * math.pi * 1.6 * (t - T0); sw = math.radians(26) * math.sin(ph) * (1.0 if walking else 0.0) * min(1.0, (1 - u) * 6)
        if not walking and t > T1: yaw = yaw + math.radians(25) * ex.ease((t - T1) / 1.2)       # turns to look along the canyon
        root_ob.location = (float(p[0]), float(p[1]), z + 0.0015 + (0.0012 * abs(math.sin(ph)) if walking else 0.0)); root_ob.rotation_euler = (0, 0, yaw)
        for lg, side in legs: lg.rotation_euler = (0, side * sw, 0)
        arm.rotation_euler = (0, -0.6 * sw, 0)
    kit.on_frame(pose); pose(0.0); return root_ob


# ============================================================================================ title
def title(kit, cam, lens):
    bpy = kit.bpy; cu = bpy.data.curves.new('rt_title', 'FONT'); cu.body = TITLE; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    try: cu.font = bpy.data.fonts.load(FONT)
    except Exception as e: print('font', e)
    d = 0.5; hh = d * 18.0 / lens * 9 / 16
    cu.size = hh * 2 * 0.062; cu.space_character = 1.05
    ob = bpy.data.objects.new('rt_title', cu); kit.coll.objects.link(ob); ob.parent = cam.ob; ob.location = (0, hh * 0.80, -d)
    m = cw._new_mat(bpy, 'rt_title_mat'); g = G(m.node_tree, kit); a = g.value(0.0, 'rt_title_a')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.10, 0.12, 0.16)), 'Strength': 1.0}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    cu.materials.append(m)
    for at in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_shadow', 'visible_volume_scatter'): setattr(ob, at, False)
    def fade(t): a.default_value = float(ex.ease(t / 0.6) * (1 - ex.ease((t - 1.9) / 0.6))); ob.hide_render = t > 2.6
    kit.on_frame(fade); return ob


# ============================================================================================ build and frames
def build(bpy, ctx):
    W, H = ctx['W'], ctx['H']
    kit = cw.Kit(bpy, seed=1, loop=DURATION)
    terr = Terrain(kit); land = Plain()
    follow = vegetation(kit, land, terr)
    sky = Sky(kit); mg = mist(kit)
    fos = Fossils(kit, land)
    hiker(kit)
    ex.deer(kit, land, -1.55, 0.75, 0.6, lift_at=4.2, lower_at=5.6)
    ex.deer(kit, land, -1.35, 0.35, 2.2, lift_at=17.2, lower_at=19.0, name='rt_deer2', scale=0.8)
    ex.butterflies(kit, land, [(1.35, -0.6), (-1.5, -0.9), (1.55, 0.4)])
    ex.petals(kit, land, 24)
    cw.birds(kit, 5, center=(-0.05, 0.1), radius=0.85, height=0.42, size=0.045)
    ex.finish(bpy, W, H, bloom=0.2, vignette=0.24)
    cam = ex.ShotCam(kit); title(kit, cam, 35.0)
    cw.apply_cycles(bpy, fast=True)
    sc = bpy.context.scene; cy = sc.cycles
    cy.max_bounces = 4; cy.diffuse_bounces = 1; cy.glossy_bounces = 1; cy.transmission_bounces = 4; cy.transparent_max_bounces = 8
    cy.adaptive_threshold = 0.03; cy.sample_clamp_direct = 12.0
    return {'kit': kit, 'terr': terr, 'follow': follow, 'sky': sky, 'mist': mg, 'fos': fos, 'cam': cam}


def shot_pose(name, u, t):
    """Camera for shot `name` at local progress u: pos, target, lens, focus, fstop, dof."""
    if name == 'then':       # wide three-quarter, a slow push and a 4 degree arc: the whole flat block and its stream
        e = ex.ease(u); az = math.radians(-50 + 4 * e); el = math.radians(27 - 2 * e); D = 6.3 - 0.5 * e; tgt = np.array((0.0, 0.0, -0.42))
        pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
        return pos, tgt, 35.0, D, 16.0, False
    if name == 'ages':       # in front of the cut face, looking up the canyon; cranes down with the water
        e = ex.ease(u); pos = ex.lerp((0.88, -2.80, 0.40), (0.72, -2.62, -0.06), e); tgt = ex.lerp((-0.70, -1.38, -0.16), (-0.50, -1.33, -0.72), e)
        return pos, tgt, 26.0, float(np.linalg.norm(pos - tgt)), 8.0, True
    # today: low three-quarter into the setting sun, a slow push toward the hiker
    e = ex.ease(u); az = math.radians(-80 + 5 * e); el = math.radians(13.0 - 2.0 * e); D = 5.1 - 0.8 * e; tgt = ex.lerp((0.0, -0.30, -0.36), (0.22, -0.70, -0.30), e)
    pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    return pos, tgt, 32.0, float(np.linalg.norm(pos - np.array((0.70, -1.30, 0.0)))), 11.0, True


def frame(bpy, ctx, S, i, t):
    S['kit'].update(t)
    s = carve_s(t); S['terr'].set(s); S['follow'](s); S['sky'].set(t); S['fos'].update(t)
    tl = ctx['timeline'].at(t); pos, tgt, lens, focus, fstop, dof = shot_pose(tl['name'], tl['u'], t)
    S['cam'].set(pos, tgt, lens, focus, fstop); S['cam'].ob.data.dof.use_dof = dof
    S['mist'].default_value = 1.0 if tl['name'] == 'today' else 0.35 * ex.ease((t - 8.0) / 3.0)
