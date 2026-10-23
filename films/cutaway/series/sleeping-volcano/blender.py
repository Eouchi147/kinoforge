"""The Sleeping Volcano (Cutaway showcase series, film 6; 20 s, 16:9). Drama, natural hazards, science.

A green island on a block of sea. The -Y cut runs through the volcano's crater, so the face shows the textbook section:
the cone's layers, the conduit and, deep down, the magma chamber. Beginning: the island sleeps at golden hour (a thin
steam wisp, gulls, fish in the glass sea). Middle: the chamber brightens, magma climbs the conduit and the cracks, birds
burst from the trees, the steam turns to smoke. End: at dusk a gentle eruption, lava fountains and a lava stream down
the east flank to the sea, which steams where the lava meets it. Nobody is in danger: there are no people on the island.

Kit: films/styles/cutaway/cutaway.py and cinematic/extras.py (imported, never edited). Everything new is in this file.

Shots (frame = t * 24):
  1 island    0.0-6.5 s   wide three-quarter, slow push and 4 degree arc     (where we are: the sleeping island)
  2 rise      6.5-13.5 s  crane up the cut face, chamber to crater           (the cause: the magma wakes and climbs)
  3 eruption 13.5-20.0 s  low wide at dusk, slow arc                         (the climax and the closing image)
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

G = cw.G
srgb = cw.srgb

SHOTS = [{'name': 'island', 'dur': 6.5}, {'name': 'rise', 'dur': 7.0}, {'name': 'eruption', 'dur': 6.5}]
DURATION = sum(s['dur'] for s in SHOTS)
FRAMES = {'island_a': 12, 'island_b': 120, 'rise_a': 170, 'rise_b': 300, 'erupt_a': 360, 'erupt_b': 460}   # check stills
SETTINGS = {'samples': 20, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - High Contrast', 'exposure': 0.1,
            'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 4.0, 'adaptive_min_samples': 8, 'denoising_prefilter': 'FAST'}

# ---- the world
LV = -0.05                       # sea level
SX = 3.0                         # block size (m)
CX, CY = 0.08, -1.45             # volcano centre: the -Y cut face (y = -1.5) runs through the crater
R_SHORE = 1.15                   # island radius
PEAK = 1.25                      # cone height scale
CR = 0.15                        # crater radius
SUN_AZ, SUN_EL = 92.0, 6.0      # low sun behind and to the right of every camera (just out of frame)
HORIZON = (0.96, 0.58, 0.34)
LAVA_AZ = math.radians(14.0)     # the lava stream runs down this flank (east, toward the camera side)
STRATA = [('soil', 0.05, (0.20, 0.14, 0.10), 0.05), ('ash', 0.07, (0.66, 0.63, 0.60), 0.05), ('tuff', 0.11, (0.76, 0.56, 0.34), 0.10),
          ('ash2', 0.05, (0.46, 0.44, 0.43), 0.10), ('scoria', 0.13, (0.55, 0.26, 0.17), 0.60), ('flow', 0.20, (0.25, 0.24, 0.26), 0.25),
          ('pumice', 0.07, (0.62, 0.58, 0.52), 0.15), ('basalt', 0.45, (0.30, 0.29, 0.31), 0.30), ('bedrock', 1.0, (0.17, 0.17, 0.20), 0.35)]

# ---- the story clock (seconds)
T_WAKE = 4.0          # the chamber starts to brighten
T_CLIMB = (6.9, 13.2) # magma front climbs the conduit (chamber top to crater floor)
T_BIRDS = 10.9        # birds burst from the trees
T_SMOKE = (10.0, 13.0)
T_ERUPT = 14.2        # first lava fountain
T_FLOW = (14.7, 17.7) # lava stream from the rim to the sea
T_DUSK = (8.0, 17.0)  # the light goes from golden hour to dusk
T_FADE = (19.2, 20.0)


def sm(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)


def cone_h(x, y):
    r = np.hypot(x - CX, y - CY)
    base = 0.035 + PEAK * np.clip(1 - r / (R_SHORE + 0.06), 0, 1) ** 1.7
    rim = 0.035 + PEAK * (1 - CR / (R_SHORE + 0.06)) ** 1.7
    h = np.minimum(base, rim + 0.012 * cw.fbm(x, y, 7, 2, 9.0))
    h = h - 0.12 * np.clip(1 - (r / CR) ** 2, 0, 1)                                   # the crater bowl
    ang = np.arctan2(y - CY, x - CX)
    gul = 0.014 * np.sin(11 * ang + 2.0 * cw.fbm(x, y, 3, 2, 1.5)) * cw.smooth(0.2, 0.5, r) * cw.smooth(1.25, 0.8, r)   # radial gullies
    return h + gul + 0.012 * cw.fbm(x, y, 5, 3, 2.2) * cw.smooth(0.25, 0.6, r)


def shore_sd(x, y):
    r = np.hypot(x - CX, y - CY); rs = R_SHORE + 0.07 * cw.fbm(x, y, 9, 3, 0.9)
    d = rs - r                                                                          # > 0 on the island, < 0 in the sea
    return np.where(d > 0, d * 2.4, d)       # steeper on land: the kit caps land at 0.55 m per metre of this distance


def zones(x, y, h):
    r = np.hypot(x - CX, y - CY)
    rock = cw.smooth(0.50, 0.34, r + 0.06 * cw.fbm(x, y, 13, 3, 3.0))                    # bare dark rock on the upper cone
    return {'path': rock}


def lava_path():
    """The stream's centre line: from the rim down the east flank, meandering, until it enters the sea."""
    P = []; s = 0.0
    while True:
        r = CR * 0.9 + s; a = LAVA_AZ + 0.10 * math.sin(s * 7.0) + 0.05 * math.sin(s * 17.0)
        x, y = CX + r * math.cos(a), CY + r * math.sin(a)
        P.append((x, y)); s += 0.012
        if r > R_SHORE + 0.16: break
    return np.array(P)


# =============================================================================================== materials
CTRL = {'glow': [], 'front': []}     # per-material Value sockets driven every frame (a node tree cannot link to another tree)


def ctrl(g, key, v0):
    s = g.value(v0, 'sv_' + key); CTRL[key].append(s); return s


def mat_magma(kit, name, front=False, flow=0.25, base=3.0):
    """Molten rock: churning crust and bright seams (4D noise in t). Optional rising front (world z < front glows)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry')
    t_val = ex.time_value(kit, g); glow = ctrl(g, 'glow', 0.4); front = ctrl(g, 'front', -2.0) if front else None
    pos = tc.outputs['Object']
    n1 = g.noise(pos, 6.0, 5.0, 0.62, '4D', g.math('MULTIPLY', t_val, flow), distortion=1.2)
    vo = g.voronoi(pos, 7.0, 'DISTANCE_TO_EDGE', '4D', g.math('MULTIPLY', t_val, flow * 0.6))
    seam = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 14.0), clamp=True)
    heat = g.math('ADD', g.math('MULTIPLY', n1.outputs['Fac'], 1.05), g.math('MULTIPLY', seam, 0.22))
    col = g.ramp(heat, [(0.30, (0.10, 0.02, 0.01)), (0.52, (0.72, 0.10, 0.02)), (0.70, (1.0, 0.42, 0.06)), (0.95, (1.0, 0.86, 0.45))])
    st = g.math('MULTIPLY', g.math('MULTIPLY', g.math('POWER', heat, 2.0), glow), base)
    if front is not None:
        z = g.sep(geo.outputs['Position'])[2]
        on = g.math('MULTIPLY', g.math('SUBTRACT', front, z), 30.0, clamp=True)
        tip = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', front, z)), 12.0), clamp=True)
        st = g.math('MULTIPLY', st, g.math('ADD', on, g.math('MULTIPLY', g.math('MULTIPLY', tip, on), 1.5)))
        rock = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.06, 0.05, 0.05)), 'Roughness': 0.9})
        e = g.node('ShaderNodeEmission', ins={'Color': col}); g.put(e, 'Strength', st)
        ad = g.node('ShaderNodeAddShader'); g.link(rock, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad)
    else:
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.10, 0.04, 0.03)), 'Roughness': 0.6})
        g.put(p, 'Emission Color', col); g.put(p, 'Emission Strength', st); cw._finish(g, p)
    try: m.cycles.emission_sampling = 'FRONT'
    except Exception: pass
    return m


def mat_card(kit, name, steam=(0.93, 0.92, 0.92), ash=(0.42, 0.36, 0.32), glow_col=(1.0, 0.38, 0.10), soft=1.6, scale=2.4):
    """Smoke or steam card: a soft round puff broken by noise that evolves in t. Per-object colour drives it:
    R = opacity, G = darkness (steam to ash), B = glow from below (lava light)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); oi = g.node('ShaderNodeObjectInfo'); t_val = ex.time_value(kit, g)
    gx, gy, _ = g.sep(tc.outputs['Generated']); oc = g.sep(oi.outputs['Color'])
    dx = g.math('SUBTRACT', gx, 0.5); dy = g.math('SUBTRACT', gy, 0.5)
    r = g.math('MULTIPLY', g.math('SQRT', g.math('ADD', g.math('MULTIPLY', dx, dx), g.math('MULTIPLY', dy, dy))), 2.0)
    fall = g.math('POWER', g.math('SUBTRACT', 1.0, r, clamp=True), soft)
    q = g.comb(g.math('MULTIPLY', gx, scale), g.math('MULTIPLY', gy, scale), g.math('MULTIPLY', oi.outputs['Random'], 40.0))
    n = g.noise(q, 1.5, 3.0, 0.55, '4D', g.math('ADD', g.math('MULTIPLY', t_val, 0.18), g.math('MULTIPLY', oi.outputs['Random'], 9.0)), distortion=0.4)
    den = g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.20), 2.4, clamp=True)
    a = g.math('MULTIPLY', g.math('MULTIPLY', fall, den), oc[0], clamp=True)
    col = g.mix(oc[1], srgb(steam), srgb(ash))
    shade = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.6), col, g.mix(0.5, col, (0, 0, 0), 'MULTIPLY'))
    shade = g.mix(1.0, shade, (1.0, 0.80, 0.62), 'MULTIPLY')          # warm: the cool sky fill must not turn the smoke blue
    df = g.node('ShaderNodeBsdfDiffuse', ins={'Color': shade})
    em = g.node('ShaderNodeEmission'); g.put(em, 'Color', g.mix(g.math('MINIMUM', oc[2], 1.0), g.mix(1.0, shade, (0.5, 0.5, 0.5), 'MULTIPLY'), srgb(glow_col)))
    g.put(em, 'Strength', g.math('ADD', 0.45, g.math('MULTIPLY', oc[2], g.math('MULTIPLY', g.math('SUBTRACT', 1.0, gy, clamp=True), 2.2))))   # a little self light: no blue cast from the sky fill
    ad = g.node('ShaderNodeAddShader'); g.link(df, ad.inputs[0]); g.link(em, ad.inputs[1])
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(ad, mx.inputs[2]); cw._finish(g, mx)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    return m


def card(kit, name, m):
    V = [(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)]
    ob = cw.mk_mesh(kit.bpy, name, V, [(0, 1, 2, 3)], [m], None, False, kit.coll)
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
    return ob


# =============================================================================================== story pieces
class Plume:
    """Puffs rising from a vent, billboarded to the camera. params(t) -> dict(rise, spread, size, grow, period, opacity, dark, glow, wind)."""
    def __init__(self, kit, name, m, vent, n, params, seed):
        self.cards = []; rng = np.random.default_rng(seed); self.vent = np.asarray(vent, float); self.params = params
        for k in range(n):
            ob = card(kit, f'{name}{k}', m); ph = (k + rng.uniform(-0.25, 0.25)) / n; jit = rng.normal(0, 1, 3); spin = rng.uniform(-0.4, 0.4)
            self.cards.append((ob, ph, jit, spin))
        kit.on_frame(self.pose)
    def pose(self, t):
        P = self.params(t)
        for ob, ph, jit, spin in self.cards:
            a = (t / P['period'] + ph) % 1.0
            off = np.array([P['wind'][0] * a + P['spread'] * jit[0] * a, P['wind'][1] * a + P['spread'] * jit[1] * a, P['rise'] * (a ** 0.8)])
            ob.location = tuple(self.vent + off)
            s = P['size'] * (0.35 + P['grow'] * a ** 0.7) * (1 + 0.15 * jit[2]); ob.scale = (s, s, s)
            fade = sm(0.0, 0.07, a) * (1.0 - sm(0.55, 0.92, a))          # dense right from the vent, thinning as it rises
            ob.color = (P['opacity'] * fade, P['dark'] * (0.7 + 0.3 * a), P['glow'] * (1 - a) ** 2, 1.0)
            ob['spin'] = spin * t
    def face(self, cam):
        from mathutils import Vector, Matrix
        for ob, *_ in self.cards:
            d = Vector(tuple(np.asarray(cam, float) - np.asarray(ob.location[:], float)))
            q = d.to_track_quat('Z', 'Y'); ob.rotation_euler = (q.to_matrix() @ Matrix.Rotation(ob.get('spin', 0.0), 3, 'Z')).to_euler()


def fountain(kit, vent, n=120, seed=11):
    """Lava fountain: glowing blobs on ballistic arcs (slow diorama gravity), cooling and shrinking as they fall."""
    bpy = kit.bpy; rng = np.random.default_rng(seed)
    hot = cw.mat_glow(kit, 'sv_bomb', (1.0, 0.55, 0.14), 26.0); V0, F0 = cw._icosphere(1); grav = 2.1; out = []
    for k in range(n):
        ob = cw.mk_mesh(bpy, f'sv_bomb{k}', V0 * 0.016, F0, [hot], None, True, kit.coll); ob.visible_shadow = False
        az = rng.uniform(0.15, math.pi - 0.15); vh = rng.uniform(0.02, 0.26); v0 = rng.uniform(1.0, 1.6); per = rng.uniform(0.0, 1.0); sz = rng.uniform(0.6, 1.4)
        def pose(t, ob=ob, az=az, vh=vh, v0=v0, per=per, sz=sz):
            I = sm(T_ERUPT, T_ERUPT + 1.6, t) * (0.85 + 0.15 * math.sin(1.7 * t + per * 6))
            if I <= 0.01: ob.scale = (0, 0, 0); ob.location = tuple(vent); return
            v = v0 * math.sqrt(I); T = 2 * v / grav; tt = t - T_ERUPT
            a = ((tt / T) + per) % 1.0 if tt > per * T else -1
            if a < 0: ob.scale = (0, 0, 0); ob.location = tuple(vent); return
            tau = a * T; z = v * tau - 0.5 * grav * tau * tau
            ob.location = (vent[0] + vh * tau * math.cos(az), vent[1] + vh * tau * math.sin(az), vent[2] + z)
            s = sz * (1.0 - 0.55 * a); ob.scale = (s, s, s * 1.25)
        kit.on_frame(pose); out.append(ob)
    return out


def embers(kit, vent, n=90, seed=21):
    """Sparks rising and drifting downwind from the crater, blinking out as they cool."""
    bpy = kit.bpy; rng = np.random.default_rng(seed); m = cw.mat_glow(kit, 'sv_ember', (1.0, 0.62, 0.22), 30.0); V0, F0 = cw._icosphere(1)
    for k in range(n):
        ob = cw.mk_mesh(bpy, f'sv_ember{k}', V0 * 0.0035, F0, [m], None, True, kit.coll); ob.visible_shadow = False
        per = rng.uniform(2.2, 3.6); ph = rng.uniform(0, 1); jx, jy = rng.normal(0, 0.12, 2); w = rng.uniform(0.6, 1.4)
        def pose(t, ob=ob, per=per, ph=ph, jx=jx, jy=jy, w=w):
            I = sm(T_ERUPT - 0.8, T_ERUPT + 1.0, t)
            a = (t / per + ph) % 1.0
            if I < 0.02: ob.scale = (0, 0, 0); return
            ob.location = (vent[0] + (0.10 + jx) * a + 0.02 * math.sin(5 * t + ph * 9), vent[1] + (0.22 + jy) * a * w, vent[2] + 0.05 + 0.85 * a * w)
            s = I * (1 - a) ** 0.6 * (0.6 + 0.4 * math.sin(13 * t + ph * 20) ** 2); ob.scale = (s, s, s)
        kit.on_frame(pose)


def lava_stream(kit, land):
    """A ribbon draped on the flank from the crater rim to the sea, revealed by an advancing front (t), with a flowing
    crust; 3 lights wake up as the front passes them."""
    bpy = kit.bpy; P = lava_path(); n = len(P)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); along = s / s[-1]
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.stack([-T[:, 1], T[:, 0]], 1)
    across = [-1.0, -0.5, 0.0, 0.5, 1.0]; V = []; AL = []; AC = []
    for i in range(n):
        w = 0.075 + 0.075 * along[i] ** 0.7
        for c in across:
            x, y = P[i] + N[i] * c * w / 2
            z = float(land.height(np.array([x]), np.array([y]))[0]) + 0.004 + 0.006 * (1 - c * c)
            z = max(z, LV + 0.002); V.append((x, y, z)); AL.append(along[i]); AC.append(c)
    k = len(across); F = [(i * k + j, i * k + j + 1, (i + 1) * k + j + 1, (i + 1) * k + j) for i in range(n - 1) for j in range(k - 1)]
    m = cw._new_mat(bpy, 'sv_lava'); g = G(m.node_tree, kit)
    t_val = ex.time_value(kit, g); fr = g.value(0.0, 'sv_front'); al = g.attr('along').outputs['Fac']; ac = g.attr('across').outputs['Fac']
    flow = g.comb(g.math('SUBTRACT', g.math('MULTIPLY', al, 30.0), g.math('MULTIPLY', t_val, 1.2)), g.math('MULTIPLY', ac, 1.5), 0.0)
    n1 = g.noise(flow, 1.3, 4.0, 0.6, '4D', g.math('MULTIPLY', t_val, 0.3))
    vo = g.voronoi(flow, 2.2, 'DISTANCE_TO_EDGE')
    seam = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 7.0), clamp=True)
    cool = g.math('MULTIPLY', g.math('SUBTRACT', fr, al), 1.6, clamp=True)             # older lava (far behind the front) crusts over
    heat = g.math('ADD', g.math('MULTIPLY', n1.outputs['Fac'], 0.8), g.math('MULTIPLY', seam, 0.6))
    heat = g.math('SUBTRACT', heat, g.math('MULTIPLY', cool, 0.25))
    heat = g.math('ADD', heat, g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('ABSOLUTE', ac)), 0.25))
    col = g.ramp(heat, [(0.35, (0.06, 0.03, 0.02)), (0.55, (0.70, 0.10, 0.02)), (0.72, (1.0, 0.42, 0.06)), (0.95, (1.0, 0.85, 0.42))])
    tip = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', fr, al)), 14.0), clamp=True)
    st = g.math('MULTIPLY', g.math('POWER', heat, 2.2), g.math('ADD', 9.0, g.math('MULTIPLY', tip, 10.0)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.07, 0.05, 0.05)), 'Roughness': 0.85})
    g.put(p, 'Emission Color', col); g.put(p, 'Emission Strength', st)
    edge = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', g.math('ABSOLUTE', ac), 0.75), 0.0), 4.0), clamp=True)
    mask = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', fr, al), 60.0, clamp=True), edge)
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader'); g.link(mask, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(p, mx.inputs[2])
    cw._finish(g, mx)
    try: m.cycles.emission_sampling = 'FRONT'
    except Exception: pass
    ob = cw.mk_mesh(bpy, 'sv_lava', V, F, [m], None, True, kit.coll, {'along': ('FLOAT', AL), 'across': ('FLOAT', AC)})
    ob.visible_shadow = False
    lights = []
    for q in (0.12, 0.45, 0.8):
        i = int(q * (n - 1)); x, y = P[i]; z = float(land.height(np.array([x]), np.array([y]))[0]) + 0.08
        ld = bpy.data.lights.new(f'sv_lavalight{q}', 'POINT'); ld.energy = 0.0; ld.color = (1.0, 0.42, 0.12); ld.shadow_soft_size = 0.08
        lo = bpy.data.objects.new(f'sv_lavalight{q}', ld); kit.coll.objects.link(lo); lo.location = (x, y, z); lo.visible_camera = False
        lights.append((ld, q))
    def pose(t):
        f = 0.0 if t < T_FLOW[0] else 1.04 * (1 - (1 - min(1.0, (t - T_FLOW[0]) / (T_FLOW[1] - T_FLOW[0]))) ** 1.7)
        fr.default_value = f
        for ld, q in lights: ld.energy = 3.5 * sm(q - 0.02, q + 0.12, f) * (0.9 + 0.1 * math.sin(9 * t + q * 20))
    kit.on_frame(pose)
    i_end = n - 1
    for i in range(n):
        if float(land.height(P[i:i + 1, 0], P[i:i + 1, 1])[0]) < LV + 0.005: i_end = i; break
    return ob, np.array([P[i_end, 0], P[i_end, 1], LV + 0.01])


class _Halo:
    """A soft additive glow card over the vent (camera only): the fountain's heat bloom."""
    def __init__(self): self.cards = []
    def face(self, cam): Plume.face(self, cam)
HALO = _Halo()


def halo(kit, vent):
    bpy = kit.bpy; m = cw._new_mat(bpy, 'sv_halo'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); gx, gy, _ = g.sep(tc.outputs['Generated'])
    dx = g.math('SUBTRACT', gx, 0.5); dy = g.math('SUBTRACT', gy, 0.5)
    r = g.math('MULTIPLY', g.math('SQRT', g.math('ADD', g.math('MULTIPLY', dx, dx), g.math('MULTIPLY', dy, dy))), 2.0)
    f = g.math('POWER', g.math('SUBTRACT', 1.0, r, clamp=True), 2.6); k = g.value(0.0, 'sv_halo_k')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.45, 0.14))}); g.put(e, 'Strength', g.math('MULTIPLY', f, k))
    tr = g.node('ShaderNodeBsdfTransparent'); ad = g.node('ShaderNodeAddShader'); g.link(tr, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    ob = card(kit, 'sv_halo', m); ob.location = tuple(np.asarray(vent) + np.array([0, 0.0, 0.22])); ob.scale = (0.9, 0.9, 0.9)
    HALO.cards.append((ob, 0, 0, 0)); ob['spin'] = 0.0
    def pose(t): k.default_value = 1.4 * sm(T_ERUPT - 0.3, T_ERUPT + 1.0, t) * (0.85 + 0.15 * math.sin(6.1 * t) * math.sin(2.3 * t + 1))
    kit.on_frame(pose)


def flock(kit, land, perches, seed=31):
    """Birds sitting in the crowns burst up and away from the cone at T_BIRDS, flapping hard, then gliding."""
    bpy = kit.bpy; rng = np.random.default_rng(seed); mat = cw.mat_simple(kit, 'sv_bird', (0.07, 0.07, 0.08), 0.6); size = 0.040
    for k, (x, y, z) in enumerate(perches):
        body = cw.mk_mesh(bpy, f'sv_bird{k}', *cw._tube([(-size * 0.5, 0, 0), (0, 0, 0), (size * 0.45, 0, 0)], [size * 0.09, size * 0.13, size * 0.05], 6), [mat], None, True, kit.coll)
        wings = []
        for side in (-1, 1):
            Vw = [(-size * 0.15, 0, 0), (size * 0.15, 0, 0), (0.0, side * size * 0.95, 0), (-size * 0.28, side * size * 0.72, 0)]
            wg = cw.mk_mesh(bpy, f'sv_bird{k}w{side}', Vw, [(0, 1, 2, 3)], [mat], None, False, kit.coll); wg.parent = body; wings.append((wg, side))
        away = np.array([x - CX, y - CY]); away = away / (np.linalg.norm(away) + 1e-6)
        away = away * 0.6 + np.array([-0.55, 0.65]) * 0.4; away /= np.linalg.norm(away)
        d0 = T_BIRDS + rng.uniform(0.0, 0.45); sp = rng.uniform(0.32, 0.45); cl = rng.uniform(0.18, 0.28); fl = rng.uniform(5.5, 7.5); ph = rng.uniform(0, 6)
        def pose(t, body=body, wings=wings, x=x, y=y, z=z, away=away, d0=d0, sp=sp, cl=cl, fl=fl, ph=ph):
            if t < d0 - 0.05: body.scale = (0, 0, 0); body.location = (x, y, z); return
            u = max(0.0, t - d0); body.scale = (1, 1, 1)
            dist = sp * (u + 0.6 * u * u / (1 + u)); up = cl * u + 0.22 * (1 - math.exp(-3 * u))
            body.location = (x + away[0] * dist + 0.02 * math.sin(2.1 * u + ph), y + away[1] * dist, z + up)
            body.rotation_euler = (0.0, math.radians(-18) * math.exp(-u), math.atan2(away[1], away[0]))
            beat = math.radians(12 + 48 * math.sin(2 * math.pi * fl * u + ph)) * (1.0 if u < 1.6 else 0.35 + 0.65 * (math.sin(1.5 * u) > 0.3))
            for wg, side in wings: wg.rotation_euler = (side * beat, 0, 0)
        kit.on_frame(pose); pose(0.0)


def title(kit, cam, text='The Sleeping Volcano'):
    bpy = kit.bpy; cu = bpy.data.curves.new('sv_title', 'FONT'); cu.body = text; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    font = os.path.join(root, 'ads', 'fonts', 'Archivo.ttf')
    if os.path.exists(font): cu.font = bpy.data.fonts.load(font)
    cu.size = 0.20; cu.space_character = 1.06
    ob = bpy.data.objects.new('sv_title', cu); kit.coll.objects.link(ob)
    m = cw._new_mat(bpy, 'sv_titlemat'); g = G(m.node_tree, kit); a = g.value(0.0, 'sv_title_a')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.98, 0.94, 0.86)), 'Strength': 1.15})
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader'); g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2])
    cw._finish(g, mx); cu.materials.append(m)
    for at in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, at, False)
    ob.parent = cam.ob; d = 5.0; ob.location = (0.0, d * 0.289 * 0.84, -d)    # upper third (half frame height at 35 mm is 0.289 d)
    def pose(t): a.default_value = sm(0.25, 0.9, t) * (1 - sm(1.85, 2.5, t))
    kit.on_frame(pose); return ob


# =============================================================================================== build
def build(bpy, ctx):
    W, H = ctx['W'], ctx['H']
    kit = cw.Kit(bpy, seed=6, loop=DURATION)
    sea = cw.basin(shore_sd, depth=0.46, level=LV, shelf=0.5, kind='lagoon')
    # trees: a forest belt on the lower slopes (dense, small: the cone stays the giant)
    rng = np.random.default_rng(4); spots = []
    for _ in range(4000):
        r = rng.uniform(0.40, R_SHORE - 0.10); a = rng.uniform(0, 2 * math.pi); x, y = CX + r * math.cos(a), CY + r * math.sin(a)
        if y < -SX / 2 + 0.03 or abs(x) > SX / 2 - 0.03: continue
        if abs(((a - LAVA_AZ + math.pi) % (2 * math.pi)) - math.pi) < 0.55 and r > 0.3: continue      # keep the lava's path clear
        if all(math.hypot(x - p[0], y - p[1]) > 0.115 for p in spots): spots.append((x, y, rng.uniform(0.6, 1.0) * (1.25 - 0.4 * (r - 0.5)), 'round' if rng.uniform() < 0.62 else 'cone'))
        if len(spots) >= 52: break
    land = cw.block(kit, size=(SX, SX), depth=1.8, strata=STRATA, seed=6, top=cone_h, water=[sea], zones=zones,
                    tree_spots=spots, tree_kinds=('round', 'cone'), tree_scale=0.42, boulders=0, keep_clear=[(CX, CY, 0.30)], flowers=0.35, corals=16, reeds=0.0, sway=1.3,
                    water_density=1.9, water_glow=0.012, water_tint=(0.16, 0.60, 0.66), bed=((0.78, 0.72, 0.56), (0.62, 0.58, 0.46)), caustics=0.45)
    # cut-face layering: the cone's own layers drape parallel to its flanks (nested, a stratovolcano), the old sea floor
    # below runs flat; an unconformity line at z = Z_OLD separates them (the kit's default flattens to the mean top height,
    # which turns a tall cone into one dark band)
    Z_OLD = -1.18; wall = land.objects['walls']; nv = len(wall.data.vertices)
    co = np.zeros(nv * 3); wall.data.vertices.foreach_get('co', co); z = co.reshape(-1, 3)[:, 2]
    dt = np.zeros(nv); wall.data.attributes['dtop'].data.foreach_get('value', dt)
    skin = 0.68; flat = np.minimum(dt, np.maximum(skin + (Z_OLD - z), skin))   # equals dt under the sea floor (no seam)
    core = np.maximum(skin - (dt - skin) * 0.5, 0.45)                   # mirrored, continuous: no steps between wall rows
    wc = np.clip((z - (Z_OLD - 0.18)) / 0.36, 0, 1); wc = wc * wc * (3 - 2 * wc)
    sdn = np.where(dt < skin, dt, core * wc + flat * (1 - wc))
    wall.data.attributes['sd'].data.foreach_set('value', sdn.astype(np.float32))
    # dark volcanic rock for the bare upper cone (this film's own copy of the top material: the kit's path colour)
    PATH = tuple(srgb((0.52, 0.42, 0.30)))[:3]
    for n in land.mats['top'].node_tree.nodes:
        if n.bl_idname == 'ShaderNodeMix':
            for sk in n.inputs:
                if sk.type == 'RGBA' and not sk.is_linked and all(abs(sk.default_value[c] - PATH[c]) < 1e-4 for c in range(3)):
                    sk.default_value = tuple(srgb((0.13, 0.11, 0.10)))[:3] + (1.0,)

    rig = ex.cine_light(kit, land, SUN_AZ, SUN_EL, sun=5.5, fill=0.85, amb=0.22, horizon=HORIZON)
    # the floor melts into the sky at the horizon (no hard line): bigger plane, far colour = the sky's horizon colour
    flo = rig['floor']
    for v in flo.data.vertices: v.co.x *= 8.0; v.co.y *= 8.0
    fem = [n for n in flo.active_material.node_tree.nodes if n.bl_idname == 'ShaderNodeEmission'][0]
    for l in list(fem.inputs['Color'].links): flo.active_material.node_tree.links.remove(l)
    fem.inputs['Color'].default_value = tuple(0.62 * np.array(srgb(HORIZON)[:3]) + 0.38 * np.array(srgb((0.40, 0.34, 0.48))[:3])) + (1.0,)
    fem.inputs['Strength'].default_value = 1.0
    ex.edge_spill(kit, land, '-Y', power=55.0)
    ex.edge_spill(kit, land, '+X', power=30.0)
    T = {'t': None}
    wnodes = [n for n in rig['world'].node_tree.nodes if n.bl_idname == 'ShaderNodeBackground']
    sun = rig['sun']; fill = rig.get('fill'); rim = rig.get('rim')
    e0 = {'fill': fill.data.energy if fill else 0, 'rim': rim.data.energy if rim else 0}
    def dusk(t):
        d = sm(*T_DUSK, t)
        sun.data.energy = 5.5 * (1 - 0.72 * d); sun.data.color = tuple(np.array((1.0, 0.66, 0.38)) * (1 - d) + np.array((1.0, 0.45, 0.26)) * d)
        if fill: fill.data.energy = e0['fill'] * (1 - 0.45 * d)
        if rim: rim.data.energy = e0['rim'] * (1 - 0.55 * d)
        if len(wnodes) >= 2: wnodes[0].inputs['Strength'].default_value = 1.0 - 0.5 * d; wnodes[1].inputs['Strength'].default_value = 0.22 * (1 - 0.4 * d)
        fem.inputs['Strength'].default_value = 1.0 - 0.5 * d
    kit.on_frame(dusk)

    # ---- the volcano's section on the -Y face: chamber, conduit, cracks
    eggs = ex.Eggs(kit, land); fy = eggs.faces['-Y']; fx = eggs.faces['+X']
    ch_u, ch_z = CX, -1.32
    chamber = mat_magma(kit, 'sv_chamber', base=3.2)
    eggs.hole_ellipse('-Y', ch_u, ch_z, 0.46, 0.20, 0.22, 'sv_chamber', chamber)
    zc = fy.top(CX) - 0.03
    s = np.linspace(0, 1, 26); P = np.stack([CX + 0.025 * np.sin(s * 9.0) + 0.02 * np.sin(s * 23.0), (ch_z + 0.17) + s * (zc - ch_z - 0.17)], 1)
    conduit = mat_magma(kit, 'sv_conduit', front=True, base=3.0)
    eggs.hole_tunnel('-Y', P, 0.032, 'sv_conduit', conduit)
    # cracks: thin magma veins spreading from the chamber and the conduit (proud of the face), lit by the same front
    crk = mat_magma(kit, 'sv_cracks', front=True, base=2.4); rng2 = np.random.default_rng(8); A = []
    seeds = [(-0.30, 0.12, -0.9), (0.32, 0.12, 0.9), (-0.10, 0.18, -0.3), (0.18, 0.17, 0.4), (0.0, 0.55, -1.0), (0.0, 0.85, 1.0), (0.0, 1.15, -1.0), (0.0, 1.5, 1.0), (0.0, 1.8, -1.0)]
    for su, sz_, lean in seeds:
        u0 = ch_u + su; z0 = ch_z + sz_ if sz_ < 0.3 else ch_z + sz_; pts = [(u0, -0.002, z0)]; ang = math.pi / 2 + 0.55 * lean
        for k in range(rng2.integers(9, 15)):
            ang += rng2.normal(0, 0.35); ang = min(max(ang, 0.35), math.pi - 0.35); st = rng2.uniform(0.03, 0.05)
            pts.append((pts[-1][0] + st * math.cos(ang), -0.002, pts[-1][2] + st * math.sin(ang)))
            if pts[-1][2] > fy.top(pts[-1][0]) - 0.08: break
        rr = np.linspace(0.0045, 0.0012, len(pts)); v, f = cw._tube([(p[0] - ch_u, p[1], p[2]) for p in pts], rr, 5, False); A.append((v, f, 0))
    cr_ob = ex.part(kit, 'sv_cracks', A, [crk]); fy.put(cr_ob, ch_u, 0.0)
    cr_ob.location = tuple(fy.world(ch_u, 0.0, -0.0005)); cr_ob.rotation_euler = (0, 0, 0)
    # the chamber's light on the strata around it, and the crater's light on the cone and the smoke
    def plight(name, loc, col, rad):
        ld = bpy.data.lights.new(name, 'POINT'); ld.energy = 0.0; ld.color = col; ld.shadow_soft_size = rad
        lo = bpy.data.objects.new(name, ld); kit.coll.objects.link(lo); lo.location = tuple(loc); lo.visible_camera = False; return ld
    l_ch = plight('sv_chamberlight', fy.world(ch_u, ch_z + 0.02, -0.16), (1.0, 0.40, 0.12), 0.15)
    l_cd = plight('sv_conduitlight', fy.world(CX, ch_z, -0.10), (1.0, 0.45, 0.14), 0.05)
    vent = np.array([CX, CY + 0.05, zc + 0.02])
    l_cr = plight('sv_craterlight', vent + np.array([0.0, 0.08, 0.16]), (1.0, 0.45, 0.16), 0.12)
    def heart(t):
        wake = sm(T_WAKE, T_CLIMB[1], t); er = sm(T_ERUPT - 0.4, T_ERUPT + 1.2, t)
        fl = 1 + 0.10 * math.sin(7.3 * t) + 0.06 * math.sin(17.9 * t + 1.3) + 0.05 * math.sin(2.1 * t)
        breathe = 0.85 + 0.15 * math.sin(2 * math.pi * t / 3.2)
        for sk in CTRL['glow']: sk.default_value = (0.38 * breathe + 0.75 * wake + 0.3 * er) * fl
        u = sm(*T_CLIMB, t); u = u ** 1.15
        fz = (ch_z + 0.10) + u * (zc + 0.04 - ch_z - 0.10) if t > T_CLIMB[0] - 0.01 else -2.0
        for sk in CTRL['front']: sk.default_value = fz
        l_ch.energy = (2.0 + 9.0 * wake + 3 * er) * fl
        l_cd.energy = 2.5 * sm(T_CLIMB[0], T_CLIMB[0] + 1.5, t) * fl
        l_cr.energy = (0.6 * sm(T_CLIMB[1] - 0.8, T_CLIMB[1], t) + 26.0 * er) * fl
    kit.on_frame(heart)

    # ---- easter eggs in the deep layers (museum lit)
    eggs.geode('-Y', -0.86, -1.52, a=0.085, b=0.07)
    eggs.ammonite('-Y', -1.28, -0.80)
    eggs.chest('+X', -0.25, -0.86)
    eggs.trilobite('+X', 0.80, -1.40)
    eggs.finish()
    ex.soften_roots(land)

    # ---- the eruption
    lava, entry = lava_stream(kit, land)
    fountain(kit, vent)
    embers(kit, vent)
    smoke_m = mat_card(kit, 'sv_smoke', soft=1.25)
    def crater_p(t):
        s1 = sm(*T_SMOKE, t); e = sm(T_ERUPT - 0.3, T_ERUPT + 2.0, t)
        return {'period': 5.0 - 1.0 * e, 'rise': 0.45 + 0.35 * s1 + 0.55 * e, 'spread': 0.05 + 0.12 * e, 'size': 0.16 + 0.10 * s1 + 0.30 * e, 'grow': 1.6 + 0.6 * e,
                'opacity': 0.55 + 0.40 * s1 + 0.25 * e, 'dark': 0.08 + 0.60 * s1 + 0.30 * e, 'glow': 1.7 * e, 'wind': (0.14 + 0.10 * e, 0.30 + 0.20 * e)}
    plume = Plume(kit, 'sv_plume', smoke_m, vent + np.array([0, 0.03, 0.0]), 18, crater_p, 41)
    steam_m = mat_card(kit, 'sv_steam', steam=(0.96, 0.95, 0.95), ash=(0.80, 0.78, 0.78), glow_col=(1.0, 0.45, 0.18))
    def steam_p(t):
        s1 = sm(T_FLOW[1] - 0.3, T_FLOW[1] + 1.2, t)
        return {'period': 3.0, 'rise': 0.65, 'spread': 0.08, 'size': 0.20, 'grow': 2.2, 'opacity': 0.95 * s1, 'dark': 0.0, 'glow': 0.4 * s1, 'wind': (0.05, 0.16)}
    steam = Plume(kit, 'sv_steam', steam_m, entry, 12, steam_p, 43)
    halo(kit, vent)
    # mist drifting low over the sea (two big soft cards, camera only)
    mist_m = mat_card(kit, 'sv_mist', steam=(0.98, 0.90, 0.84), soft=1.2, scale=1.4)
    mists = []
    for k, (mx_, my_, sz) in enumerate([(-1.05, 0.95, 1.5), (1.0, 0.9, 1.4), (1.15, -0.55, 1.1)]):
        ob = card(kit, f'sv_mist{k}', mist_m); ob.scale = (sz, sz * 0.55, 1); ob.color = (0.26, 0.0, 0.0, 1.0); mists.append((ob, mx_, my_))
        def mv(t, ob=ob, mx_=mx_, my_=my_, k=k):
            ob.location = (mx_ + 0.03 * t, my_ + 0.012 * t, LV + 0.025 + 0.008 * k); ob.color = (0.26 * (1 - 0.5 * sm(*T_DUSK, t)), 0.0, 0.0, 1.0)
        kit.on_frame(mv)

    # ---- life
    ex.fish(kit, land, (-1.30, -1.36), n=5, rx=0.15, ry=0.05, depth=(0.06, 0.2))
    ex.fish(kit, land, (1.37, 0.35), n=4, rx=0.06, ry=0.30, depth=(0.08, 0.22), name='sv_fish')
    cw.birds(kit, 3, center=(0.3, 0.6), radius=1.3, height=1.65, color=(0.92, 0.92, 0.90))         # gulls over the sea
    TS = np.array([(p[0], p[1], p[2]) for p in spots]); near = TS[(TS[:, 1] < -0.85) & (np.abs(TS[:, 0] - CX) < 1.1)]
    if len(near) < 6: near = TS[np.argsort(TS[:, 1])[:8]]
    perches = []
    for x, y, sc in near[:9]:
        gz = float(land.height(np.array([x]), np.array([y]))[0]); perches.append((x, y, gz + 0.55 * sc * 0.42 * 0.85))
    flock(kit, land, perches)

    ex.finish(bpy, W, H, bloom=0.30, threshold=1.0, vignette=0.28)
    cam = ex.ShotCam(kit)
    ttl = title(kit, cam)
    cw.apply_cycles(bpy, fast=True)
    sc = bpy.context.scene; cy = sc.cycles
    cy.max_bounces = 4; cy.diffuse_bounces = 1; cy.glossy_bounces = 1; cy.transmission_bounces = 4; cy.transparent_max_bounces = 16
    cy.adaptive_threshold = 0.04; cy.sample_clamp_direct = 12.0
    return {'kit': kit, 'land': land, 'cam': cam, 'eggs': eggs, 'plumes': [plume, steam, HALO], 'zc': zc, 'ch': (ch_u, ch_z), 'front': CTRL['front']}


# =============================================================================================== cameras
def shot_pose(S, name, u, t):
    if name == 'island':     # the sleeping island: wide three-quarter, a slow push and a small arc
        e = ex.ease(u); az = math.radians(-36 - 4 * e); el = math.radians(20 - 2 * e); D = 8.7 - 0.8 * e
        tgt = np.array((0.0, -0.10, -0.72))
        pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
        return pos, tgt, 35.0, D, 11.0, 0.0, 0.0
    if name == 'rise':       # crane up the cut face with the magma: chamber, conduit, crater, the birds
        ch_u, ch_z = S['ch']; e = ex.ease5(u)
        tz = (ch_z + 0.02) + e * (S['zc'] + 0.32 - ch_z - 0.02); D = 1.75 + 1.25 * e; el = math.radians(4 + 16 * e)
        tu = CX + 0.06 - 0.10 * e
        tgt = np.array((tu, -SX / 2, tz)); pos = np.array((tu + 0.38 + 0.25 * e, -SX / 2 - D * math.cos(el), tz + D * math.sin(el)))
        return pos, tgt, 38.0, float(np.linalg.norm(pos - tgt)), 6.0, 0.0, 0.0
    # eruption at dusk: low wide three-quarter, a slow arc; the ground shakes once at the first burst
    e = ex.ease(u); az = math.radians(-50 + 7 * e); el = math.radians(9.0 + 1.5 * e); D = 7.4 - 0.3 * e
    tgt = np.array((0.10, -0.40, -0.12))
    pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    k = max(0.0, t - T_ERUPT); shake = 0.006 * math.exp(-2.5 * k) * math.sin(38 * k) if t > T_ERUPT else 0.0
    return pos + np.array((0, 0, shake)), tgt, 28.0, D, 9.0, 0.0, shake


def frame(bpy, ctx, S, i, t):
    S['kit'].update(t)
    tl = ctx['timeline'].at(t); pos, tgt, lens, focus, fstop, roll, _ = shot_pose(S, tl['name'], tl['u'], t)
    S['cam'].set(pos, tgt, lens, focus, fstop, roll)
    for p in S['plumes']: p.face(pos)
    sc = bpy.context.scene; sc.view_settings.exposure = SETTINGS['exposure'] - 7.0 * sm(*T_FADE, t) ** 1.5
