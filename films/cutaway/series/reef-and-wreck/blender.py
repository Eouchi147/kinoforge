"""Reef and Wreck (Cutaway showcase series, film 4). 20 s, 16:9, 24 fps. Ocean, travel, adventure, tourism.

A small tropical island on a block that is mostly clear sea. The cut faces are glass: under the surface we see light
rays, a coral reef with anemones, a school of fish, a sea turtle, and a sunken wooden ship with an open chest of gold.
A diver rolls back off a little boat and swims down to the chest.

Shots (frame = t * 24):
  1 arrive   0.0-7.0 s   wide three-quarter, slow push and arc; title; the diver rolls off the boat (splash 5.3 s)
  2 descent  7.0-13.5 s  through the -Y glass, the camera sinks with the diver past light rays; the school turns (10.2 s),
                         the turtle glides across in front (10.5-13 s)
  3 wreck   13.5-20.0 s  close on the wreck and the chest; the diver arrives, hovers, her torch finds the gold (17 s)
Kit: films/styles/cutaway/cutaway.py and cinematic/extras.py (imported, never edited). Everything new lives here.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
for p in (os.path.join(ROOT, 'films', 'styles', 'cutaway'), os.path.join(ROOT, 'films', 'styles', 'cutaway', 'cinematic')):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import extras as ex  # noqa: E402

G = cw.G; srgb = cw.srgb
SHOTS = [{'name': 'arrive', 'dur': 7.0}, {'name': 'descent', 'dur': 6.5}, {'name': 'wreck', 'dur': 6.5}]
DURATION = sum(s['dur'] for s in SHOTS)
SETTINGS = {'samples': 20, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Medium High Contrast',
            'exposure': 0.15, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 4.0, 'adaptive_min_samples': 8,
            'denoising_prefilter': 'FAST'}
TITLE = 'Reef and Wreck'

LV = -0.03                       # sea level
SEA_D = 0.85                     # sea depth beyond the island shelf
ISLE, ISLE_R = (-0.50, 0.85), 0.95
SUN_AZ, SUN_EL = 135.0, 52.0
BOAT = (-0.32, -1.08, 0.30)      # x, y, yaw
WRECK = (-0.88, -1.30, -0.48)    # x, y, yaw (bow toward the near glass, three-quarter to the camera)
CHEST = (-0.06, -1.70)
T_ROLL, T_IN, T_SWIM, T_ARRIVE = 4.8, 5.35, 5.7, 15.9
T_TURN = 10.2                    # the school turns together
RAY_GAIN = {'arrive': 0.25, 'descent': 1.7, 'wreck': 1.2}
STRATA = [('sand', 0.10, (0.92, 0.84, 0.64), 0.10), ('rubble', 0.10, (0.80, 0.74, 0.62), 0.65), ('limestone', 0.22, (0.86, 0.82, 0.72), 0.05),
          ('basalt', 1.0, (0.22, 0.23, 0.27), 0.30)]


def _isle_sd(x, y):
    """Signed distance to the island shore (positive on the island)."""
    r = ISLE_R * (1.0 + 0.10 * cw.fbm(x, y, 7, 3, 1.1))
    return r - np.hypot(x - ISLE[0], (y - ISLE[1]) * 1.12)


def _top(x, y):
    s = _isle_sd(x, y)
    return 0.015 + 0.10 * np.clip(s / 0.6, 0, 1) ** 0.8 + 0.006 * cw.fbm(x, y, 3, 3, 3.0)


def _zones(x, y, h):
    s = _isle_sd(x, y)
    return {'sand': cw.smooth(0.24, 0.13, s)}


# ============================================================================== small builders
def _mat_emit_card(kit, name, color, strength, fade_bottom=True):
    """Additive soft card (for light rays): bright under the surface, fading down; dust breakup and shimmer drift with t."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); oi = g.node('ShaderNodeObjectInfo')
    tv = ex.time_value(kit, g); lx, ly, _ = g.sep(tc.outputs['Generated'])
    across = g.math('EXPONENT', g.math('MULTIPLY', g.math('POWER', g.math('MULTIPLY', g.math('SUBTRACT', ly, 0.5), 2.0), 2.0), -3.5))
    top = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, lx), 1 / 0.04, clamp=True)            # soft at the surface
    down = g.math('POWER', lx, 1.6)                                                         # fades toward the sea bed
    dust = g.noise(g.comb(g.math('ADD', g.math('MULTIPLY', lx, 5.0), g.math('MULTIPLY', tv, 0.18)), g.math('MULTIPLY', ly, 1.4),
                          g.math('MULTIPLY', oi.outputs['Random'], 30.0)), 2.2, 3.0, 0.6)
    brk = g.math('ADD', 0.35, g.math('MULTIPLY', dust.outputs['Fac'], 0.9))
    shim = g.math('ADD', 0.72, g.math('MULTIPLY', g.math('SINE', g.math('ADD', g.math('MULTIPLY', tv, 0.9), g.math('MULTIPLY', oi.outputs['Random'], 40.0))), 0.28))
    a = g.math('MULTIPLY', g.math('MULTIPLY', across, g.math('MULTIPLY', top, down)), g.math('MULTIPLY', brk, shim))
    gain = g.value(1.0, name + '_gain')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color)}); g.put(e, 'Strength', g.math('MULTIPLY', g.math('MULTIPLY', a, strength), gain))
    tr = g.node('ShaderNodeBsdfTransparent'); ad = g.node('ShaderNodeAddShader'); g.link(tr, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    return m, gain


class Rays:
    """Underwater light rays: long soft cards from the surface down along the sunlight, turned to the camera about their
    own axis every frame. Visible to camera and transmission rays (we see them through the glass), nothing else."""
    def __init__(self, kit, land, sun_dir, n=16, seed=5):
        self.sd = sd = np.asarray(sun_dir, float) / np.linalg.norm(sun_dir); rng = np.random.default_rng(seed)
        m, self.gain = _mat_emit_card(kit, 'rw_ray', (0.80, 0.97, 1.0), 0.85); self.cards = []
        k = 0
        while len(self.cards) < n and k < 400:
            k += 1; x, y = rng.uniform(-1.5, 1.2), rng.uniform(-1.75, -0.5)
            bed = float(land.height(np.array([x]), np.array([y]))[0])
            if LV - bed < 0.3: continue
            L = (LV - bed) / sd[2] * rng.uniform(0.8, 1.0); w = rng.uniform(0.05, 0.16)
            V = [(-L, -w / 2, 0), (0, -w / 2, 0), (0, w / 2, 0), (-L, w / 2, 0)]
            ob = cw.mk_mesh(kit.bpy, f'rw_ray{len(self.cards)}', V, [(0, 1, 2, 3)], [m], None, False, kit.coll)
            ob.location = (x, y, LV - 0.004)
            for at in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_volume_scatter'): setattr(ob, at, False)
            self.cards.append(ob)
    def update(self, cam):
        from mathutils import Matrix
        X = self.sd
        for ob in self.cards:
            v = np.asarray(cam, float) - np.asarray(ob.location[:], float); vp = v - (v @ X) * X; nz = np.linalg.norm(vp)
            Z = vp / nz if nz > 1e-6 else np.array([0, 0, 1.0]); Y = np.cross(Z, X); Y /= np.linalg.norm(Y); Z = np.cross(X, Y)
            ob.rotation_euler = Matrix(((X[0], Y[0], Z[0]), (X[1], Y[1], Z[1]), (X[2], Y[2], Z[2]))).to_euler()


def _hull(L, B, H, ns=36, nphi=14, open_fn=None):
    """A boat hull shell along X (bow +X), open on top. open_fn(s, phi) -> True skips a face (broken planks)."""
    V = []; F = []
    S = np.linspace(-0.9, 1.0, ns)
    for s in S:
        b = B * (max(0.0, 1 - s * s) ** 0.55 if s > 0 else max(0.0, 1 - s ** 4) ** 0.5)
        keel = -H * (1 - 0.25 * s * s); sheer = 0.12 * H * s * s
        for j in range(nphi + 1):
            ph = math.pi * j / nphi; c = math.cos(ph); sn = math.sin(ph)
            V.append((s * L / 2, b * c, sheer + (keel - sheer) * sn ** 0.8 if True else 0))
    for i in range(ns - 1):
        for j in range(nphi):
            if open_fn and open_fn(S[i], math.pi * (j + 0.5) / nphi): continue
            a = i * (nphi + 1) + j; F.append((a, a + 1, a + nphi + 2, a + nphi + 1))
    F.append(tuple(range(nphi, -1, -1)))     # the transom
    return np.array(V), F, S


def _mat_wood(kit, name, base, plank=55.0, algae=0.0):
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); o = tc.outputs['Object']
    ox, oy, oz = g.sep(o)
    bands = g.node('ShaderNodeTexWave', ins={'Scale': plank, 'Distortion': 0.4}); g.put(bands, 'Vector', g.comb(oz, oz, oz))
    n = g.noise(g.vmath('MULTIPLY', o, (6.0, 40.0, 40.0)), 4.0, 4.0, 0.6)
    col = g.mix(g.math('MULTIPLY', bands.outputs['Fac'], 0.45), srgb(base), srgb(tuple(c * 0.55 for c in base)))
    col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.5), col, srgb(tuple(min(1, c * 1.25) for c in base)))
    if algae:
        na = g.noise(g.vmath('MULTIPLY', o, (3.0, 3.0, 3.0)), 3.0, 3.0, 0.6)
        col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', na.outputs['Fac'], 0.45), 3.0 * algae, clamp=True), col, srgb((0.30, 0.42, 0.24)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.85})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.4, 'Height': bands.outputs['Fac'], 'Distance': 0.003}); g.put(p, 'Normal', b)
    cw._finish(g, p); return m


def _mat_bubble(kit):
    m = cw._new_mat(kit.bpy, 'rw_bubble'); g = G(m.node_tree, kit); lw = g.node('ShaderNodeLayerWeight', ins={'Blend': 0.35})
    e = g.node('ShaderNodeEmission', ins={'Color': (0.85, 0.97, 1.0), 'Strength': 1.4}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(g.math('POWER', lw.outputs['Facing'], 2.0), mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    return m


def _frame_from(X, up=(0, 0, 1.0)):
    X = np.asarray(X, float); X = X / np.linalg.norm(X); u = np.asarray(up, float)
    Z = u - (u @ X) * X; nz = np.linalg.norm(Z); Z = Z / nz if nz > 1e-6 else np.array([0, 1.0, 0]); Y = np.cross(Z, X)
    return np.stack([X, Y, Z], 1)


def _set_rot(ob, M):
    from mathutils import Matrix
    ob.rotation_euler = Matrix(tuple(tuple(float(v) for v in r) for r in M)).to_euler()


# ============================================================================== the island, the boat, the wreck
def palms(kit, land):
    trunk = ex.mat(kit, 'rw_trunk', (0.50, 0.38, 0.26), 0.85, noise_amt=0.3, bump=0.6)
    leaf = cw.mat_varied(kit, 'rw_frond', [(0.26, 0.50, 0.14), (0.34, 0.58, 0.16), (0.22, 0.44, 0.12)], rough=0.5, translucent=0.35, bump=0.0)
    nut = ex.mat(kit, 'rw_coconut', (0.36, 0.26, 0.14), 0.7)
    spots = [(-0.86, 0.70, 0.66, 0.35, 0.2), (-0.32, 1.02, 0.60, -0.4, 1.4), (-0.50, 0.40, 0.54, 0.55, 2.6), (-0.06, 0.66, 0.46, -0.25, 4.0), (-0.95, 1.15, 0.50, 0.3, 5.1)]
    rng = np.random.default_rng(31); fronds = []
    for k, (x, y, hgt, lean, ph) in enumerate(spots):
        gz = float(land.height(np.array([x]), np.array([y]))[0]); la = rng.uniform(0, 6.28)
        P = [(0, 0, 0), (lean * 0.05 * math.cos(la), lean * 0.05 * math.sin(la), hgt * 0.4), (lean * 0.16 * math.cos(la), lean * 0.16 * math.sin(la), hgt)]
        Pc = cw.catmull(P, 14); tv, tf = cw._tube(Pc, np.linspace(0.020, 0.012, 14), 8)
        base = ex.part(kit, f'rw_palm{k}', [(tv, tf, 0)], [trunk], loc=(x, y, gz - 0.01))
        crown = np.array(Pc[-1])
        nv = []
        for c in range(3):
            a = c * 2.1 + la; nv.append((*ex.ell(crown + np.array([0.012 * math.cos(a), 0.012 * math.sin(a), -0.012]), (0.009, 0.009, 0.010)), 0))
        ex.part(kit, f'rw_nuts{k}', nv, [nut], base)
        nf = 9
        for f in range(nf):
            yaw = 2 * math.pi * f / nf + rng.uniform(-0.2, 0.2); Lf = rng.uniform(0.17, 0.23) * hgt / 0.45; droop = rng.uniform(0.6, 1.0)
            A = []; sN = 14; spine = []
            for i in range(sN + 1):
                s = i / sN; spine.append((s * Lf, 0.0, Lf * (0.35 * s - droop * 0.75 * s * s)))
            spine = np.array(spine)
            for i in range(1, sN):
                s = i / sN; ll = Lf * 0.32 * math.sin(math.pi * min(1, s * 1.1)) * (1 - 0.3 * s)
                for side in (-1, 1):
                    p0 = spine[i]; tip = p0 + np.array([ll * 0.45, side * ll, -ll * 0.35]); w = 0.006 * (1 - s * 0.5)
                    A.append(([p0, p0 + np.array([w, 0, 0.001]), tip], [(0, 1, 2)], 0))
            rv, rf = cw._tube(spine, np.linspace(0.003, 0.0008, len(spine)), 4, False); A.append((rv, rf, 0))
            fo = ex.part(kit, f'rw_frond{k}_{f}', A, [leaf], base, loc=tuple(crown))
            fo.rotation_euler = (0, 0, yaw); fronds.append((fo, yaw, rng.uniform(0, 6.28), rng.uniform(0.5, 0.8)))
    def sway(t):
        for fo, yaw, ph, fr in fronds:
            gust = 0.6 + 0.4 * math.sin(2 * math.pi * 0.11 * t + ph * 0.3)
            fo.rotation_euler = (0.06 * gust * math.sin(2 * math.pi * fr * t + ph), 0.05 * gust * math.sin(2 * math.pi * fr * 0.8 * t + ph * 1.7), yaw + 0.04 * math.sin(2 * math.pi * 0.3 * t + ph))
    kit.on_frame(sway); sway(0.0)


def boat(kit):
    paint = ex.mat(kit, 'rw_paint', (0.94, 0.93, 0.88), 0.45); stripe = ex.mat(kit, 'rw_stripe', (0.10, 0.36, 0.62), 0.45)
    wood = _mat_wood(kit, 'rw_boatwood', (0.62, 0.44, 0.26), 140.0)
    L, B, H = 0.36, 0.075, 0.055
    V, F, S = _hull(L, B, H, 24, 10)
    Vi = V.copy(); Vi[:, 1] *= 0.93; Vi[:, 2] = Vi[:, 2] * 0.92 + 0.002
    mats = [paint, wood, stripe]
    root = ex.empty(kit, 'rw_boat')
    ex.part(kit, 'rw_boat_hull', [(V, F, 0), (Vi, [f[::-1] for f in F], 1)], mats, root)
    seat = cw._box(-0.03, -0.068, -0.012, 0.03, 0.068, -0.004); ex.part(kit, 'rw_boat_seat', [(seat[0], seat[1], 1)], mats, root, smooth=False)
    rim = [(s * L / 2, sd * B * (max(0, 1 - s * s) ** 0.55 if s > 0 else max(0, 1 - s ** 4) ** 0.5), 0.12 * H * s * s - 0.008) for sd in (-1, 1) for s in S]
    for sd in (0, 1):
        pts = rim[sd * len(S):(sd + 1) * len(S)]; rv, rf = cw._tube(pts, np.full(len(pts), 0.0035), 6, False); ex.part(kit, f'rw_boat_stripe{sd}', [(rv, rf, 2)], mats, root)
    oar = cw._tube([(-0.12, 0.02, 0.004), (0.10, 0.035, 0.006)], [0.0025, 0.0025], 6); ex.part(kit, 'rw_oar', [(oar[0], oar[1], 1)], mats, root)
    bx, by, yaw = BOAT
    def pose(t):
        root.location = (bx, by, LV + 0.022 + 0.004 * math.sin(2 * math.pi * 0.45 * t))
        root.rotation_euler = (0.04 * math.sin(2 * math.pi * 0.38 * t + 1.0), 0.025 * math.sin(2 * math.pi * 0.45 * t), yaw + 0.03 * math.sin(2 * math.pi * 0.05 * t))
    kit.on_frame(pose); pose(0.0)
    ex.ripples(kit, [lambda t: (bx, by)], LV, 0.16, rate=0.5, rings=3, name='rw_boatrip')
    return root


def wreck(kit, land):
    wood = _mat_wood(kit, 'rw_wreckwood', (0.62, 0.46, 0.30), 60.0, algae=0.8)
    dark = ex.mat(kit, 'rw_wreckdark', (0.10, 0.08, 0.06), 0.9)
    L, B, H = 1.05, 0.17, 0.21
    def broken(s, ph):   # a hole torn in the side that faces the glass, and the deck gone
        return (-0.15 < s < 0.42 and ph > math.pi * 0.55 and ph < math.pi * 0.9 and (s * 7 + ph * 3) % 1.0 > 0.15) or (0.62 < s < 0.7 and ph > math.pi * 0.6)
    V, F, S = _hull(L, B, H, 40, 16, open_fn=broken)
    Vi = V.copy(); Vi[:, 1] *= 0.94; Vi[:, 2] = Vi[:, 2] * 0.95 + 0.004
    pieces = [(V, F, 0), (Vi, [f[::-1] for f in F], 0)]
    for s in np.linspace(-0.7, 0.85, 11):    # ribs
        b = B * (max(0, 1 - s * s) ** 0.55 if s > 0 else max(0, 1 - s ** 4) ** 0.5) * 0.92
        keel = -H * (1 - 0.25 * s * s) * 0.93; sheer = 0.12 * H * s * s
        P = [(s * L / 2, b * math.cos(ph), sheer + (keel - sheer) * math.sin(ph) ** 0.8) for ph in np.linspace(0, math.pi, 12)]
        rv, rf = cw._tube(P, np.full(12, 0.007), 5, False); pieces.append((rv, rf, 0))
    for s in (-0.5, -0.1, 0.3, 0.7):         # deck beams
        b = B * (max(0, 1 - s * s) ** 0.55 if s > 0 else max(0, 1 - s ** 4) ** 0.5); bv, bf = cw._tube([(s * L / 2, -b, 0.01), (s * L / 2, b, 0.01)], [0.008, 0.008], 6); pieces.append((bv, bf, 0))
    mv, mf = cw._tube([(0.05, 0, -0.15), (0.05, 0, 0.24), (0.06, 0.01, 0.30)], [0.018, 0.016, 0.012], 8); pieces.append((mv, mf, 0))   # broken mast stub
    kv, kf = cw._tube([(-L * 0.46, 0, -H * 0.8), (L * 0.5, 0, -H * 0.75)], [0.012, 0.012], 6); pieces.append((kv, kf, 1))
    ob = ex.part(kit, 'rw_wreck', pieces, [wood, dark])
    x, y, yaw = WRECK; bed = float(land.height(np.array([x]), np.array([y]))[0])
    ob.location = (x, y, bed + H * 0.42); ob.rotation_euler = (-0.50, 0.06, yaw)
    # the fallen mast and its yard lying on the sand beside the hull
    m2 = ex.part(kit, 'rw_mast', [(*cw._tube([(0, 0, 0), (0.62, 0, 0)], [0.016, 0.011], 8), 0), (*cw._tube([(0.42, -0.16, 0.01), (0.46, 0.16, 0.01)], [0.008, 0.008], 6), 0)], [wood])
    m2.location = (x - 0.62, y - 0.32, bed + 0.012); m2.rotation_euler = (0.0, -0.03, 0.35)
    return ob, bed


def chest(kit, land):
    wood = _mat_wood(kit, 'rw_chestwood', (0.40, 0.24, 0.13), 260.0, algae=0.4)
    brass = ex.mat_pbr(kit, 'rw_brass', (0.62, 0.48, 0.24), 0.35, metallic=1.0)
    gold = ex.mat_pbr(kit, 'rw_gold', (1.0, 0.76, 0.32), 0.22, metallic=1.0, flecks=1.2)
    gem_r = ex.mat_pbr(kit, 'rw_ruby', (0.85, 0.06, 0.12), 0.05, emission=(0.9, 0.1, 0.15), strength=0.6, coat=1.0)
    gem_g = ex.mat_pbr(kit, 'rw_emerald', (0.05, 0.70, 0.30), 0.05, emission=(0.1, 0.9, 0.4), strength=0.5, coat=1.0)
    w, d, h = 0.085, 0.055, 0.042; cx, cy = CHEST; bed = float(land.height(np.array([cx]), np.array([cy]))[0])
    root = ex.empty(kit, 'rw_chest', loc=(cx, cy, bed - 0.006)); root.rotation_euler = (0.04, -0.06, 0.25)
    P = []
    for (x0, y0, z0, x1, y1, z1) in [(-w / 2, -d / 2, 0, w / 2, -d / 2 + 0.004, h), (-w / 2, d / 2 - 0.004, 0, w / 2, d / 2, h), (-w / 2, -d / 2, 0, -w / 2 + 0.004, d / 2, h),
                                     (w / 2 - 0.004, -d / 2, 0, w / 2, d / 2, h), (-w / 2, -d / 2, 0, w / 2, d / 2, 0.004)]:
        bv, bf = cw._box(x0, y0, z0, x1, y1, z1); P.append((bv, bf, 0))
    for xx in (-w * 0.32, w * 0.32):
        bv, bf = cw._box(xx - 0.004, -d / 2 - 0.0015, 0, xx + 0.004, d / 2 + 0.0015, h + 0.001); P.append((bv, bf, 1))
    gv, gf = ex.ell((0, 0, h * 0.82), (w * 0.46, d * 0.44, h * 0.32), 2, 0.25, 3); P.append((gv, gf, 2))
    ex.part(kit, 'rw_chest_box', P, [wood, brass, gold], root, smooth=False)
    # the lid: a half barrel hinged at the back edge, thrown open
    lid = ex.empty(kit, 'rw_chest_lidpivot', root, (0, d / 2, h)); lid.rotation_euler = (math.radians(-112), 0, 0)
    LV_ = []; LF = []; seg = 10
    for i in range(2):
        for j in range(seg + 1):
            a = math.pi * j / seg; LV_.append(((i - 0.5) * w, -d / 2 + d / 2 * math.cos(a) * 1.0 + d / 2 - d / 2, d / 2 * math.sin(a) * 0.7))
    LV_ = [(p[0], -d / 2 * (1 - math.cos(math.pi * (k % (seg + 1)) / seg)), p[2]) for k, p in enumerate(LV_)]
    for j in range(seg): LF.append((j, j + 1, seg + 2 + j, seg + 1 + j))
    ex.part(kit, 'rw_chest_lid', [(LV_, LF, 0)], [wood], lid, smooth=True)
    # spilled coins and gems on the sand
    rng = np.random.default_rng(17); C = []
    for k in range(26):
        a = rng.uniform(-1.2, 1.9); r = rng.uniform(0.05, 0.13)
        c = np.array([r * math.cos(a), -abs(r * math.sin(a)) - 0.01, 0.007 + rng.uniform(0, 0.004)])
        cv, cf = cw._tube([c, c + np.array([0, 0, 0.0016])], [0.0062, 0.0062], 10); cv = ex.rot_pts(cv, 'x', rng.uniform(-0.5, 0.5), c); C.append((cv, cf, 0))
    for k in range(6):
        c = np.array([rng.uniform(-0.03, 0.03), rng.uniform(-0.02, 0.02), h * 1.05]); gv, gf = ex.ell(c, (0.006, 0.006, 0.005), 1); C.append((gv, gf, 1 + k % 2))
    ex.part(kit, 'rw_coins', C, [gold, gem_r, gem_g], root)
    bp = kit.bpy; ld = bp.data.lights.new('rw_goldglow', 'POINT'); ld.energy = 0.35; ld.color = (1.0, 0.78, 0.40); ld.shadow_soft_size = 0.02
    lo = bp.data.objects.new('rw_goldglow', ld); kit.coll.objects.link(lo); lo.parent = root; lo.location = (0, -0.01, h * 1.6); lo.visible_camera = False; lo.visible_transmission = False; lo.visible_glossy = False
    return root, bed, lo


# ============================================================================== life
def school(kit, n=34, center=(-0.05, -1.25, -0.44), rx=0.55, ry=0.26):
    body = ex.mat_pbr(kit, 'rw_fishbody', (0.55, 0.72, 0.86), 0.3, metallic=0.5, film=340.0)
    tailm = ex.mat(kit, 'rw_fishtail', (1.0, 0.82, 0.18), 0.5, sss=0.3); eye = ex.mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3)
    rng = np.random.default_rng(71); ts = np.linspace(0, DURATION + 1, 2400); v0 = 0.24
    vel = v0 * (1 - 2 * np.array([ex.ease((t - T_TURN) / 0.9) for t in ts]))
    phi = np.concatenate([[0], np.cumsum(0.5 * (vel[1:] + vel[:-1]) * np.diff(ts))])
    def center_at(t):
        p = np.interp(t, ts, phi) / max(rx, ry) + 0.43          # phase chosen so the turn happens beside the diver, in frame
        return np.array([center[0] + rx * math.cos(p), center[1] + ry * math.sin(p), center[2] + 0.05 * math.sin(0.5 * t)]), p
    fish = []
    for k in range(n):
        L = rng.uniform(0.026, 0.034); root = ex.empty(kit, f'rw_fish{k}')
        bv, bf = ex.ell((0, 0, 0), (L * 0.5, L * 0.11, L * 0.2), 2)
        ex.part(kit, f'rw_fishb{k}', [(bv, bf, 0), (*ex.ell((L * 0.3, -L * 0.09, L * 0.04), (L * 0.035, L * 0.02, L * 0.035)), 2),
                                     (*ex.ell((L * 0.3, L * 0.09, L * 0.04), (L * 0.035, L * 0.02, L * 0.035)), 2)], [body, tailm, eye], root)
        tl = ex.part(kit, f'rw_fisht{k}', [([(0, 0, 0), (-L * 0.34, 0, L * 0.22), (-L * 0.26, 0, 0), (-L * 0.34, 0, -L * 0.22)], [(0, 1, 2), (0, 2, 3)], 1)], [body, tailm, eye], root, (-L * 0.45, 0, 0))
        off = np.array([rng.normal(0, 0.09), rng.normal(0, 0.05), rng.normal(0, 0.045)]); dl = 0.35 * (off[0] + 0.2) + rng.uniform(0, 0.15)
        fish.append((root, tl, off, dl, rng.uniform(0, 6.28)))
    def pose(t):
        for root, tl, off, dl, ph in fish:
            tt = t - dl; c, p = center_at(tt); c2, _ = center_at(tt + 0.05)
            tang = np.array([-rx * math.sin(p), ry * math.cos(p)]); hd = math.atan2(tang[1], tang[0])
            flip = ex.ease((tt - T_TURN) / 0.9); hd = hd + math.pi * flip * (1 if off[1] > 0 else 1)
            cs, sn = math.cos(hd), math.sin(hd); o = np.array([cs * off[0] - sn * off[1], sn * off[0] + cs * off[1], off[2]])
            root.location = tuple(c + o + np.array([0, 0, 0.01 * math.sin(2 * t + ph)]))
            root.rotation_euler = (0.25 * math.sin(math.pi * flip), 0.0, hd + 0.08 * math.sin(1.7 * t + ph))
            tl.rotation_euler = (0, 0, 0.5 * math.sin(2 * math.pi * (3.0 + 2.0 * math.sin(math.pi * flip)) * t + ph))
    kit.on_frame(pose); pose(0.0)


def turtle(kit, path=((1.75, -1.72, -0.40), (0.6, -1.74, -0.47), (-0.4, -1.70, -0.45), (-1.4, -1.62, -0.36)), t0=0.0, t1=20.0):
    shell = cw._new_mat(kit.bpy, 'rw_shell'); g = G(shell.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    vo = g.voronoi(g.vmath('MULTIPLY', tc.outputs['Object'], (1.0, 1.3, 1.0)), 28.0, 'DISTANCE_TO_EDGE'); n = g.noise(tc.outputs['Object'], 60.0, 4.0)
    col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.8), srgb((0.36, 0.30, 0.16)), srgb((0.56, 0.42, 0.20)))
    col = g.mix(g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 14.0), clamp=True), col, srgb((0.14, 0.11, 0.06)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.4, 'Coat Weight': 0.4}); cw._finish(g, p)
    skin = ex.mat(kit, 'rw_tskin', (0.46, 0.50, 0.40), 0.6, noise_amt=0.35, bump=0.5); belly = ex.mat(kit, 'rw_tbelly', (0.86, 0.80, 0.60), 0.7)
    eye = ex.mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3); M = [shell, skin, belly, eye]
    root = ex.empty(kit, 'rw_turtle'); S = 1.1
    sv, sf = ex.ell((0, 0, 0.006 * S), (0.075 * S, 0.058 * S, 0.024 * S), 3); sv[:, 2] = np.maximum(sv[:, 2], 0.0)
    pv, pf = ex.ell((0, 0, 0.002 * S), (0.07 * S, 0.052 * S, 0.012 * S), 2)
    hv, hf = ex.ell((0.095 * S, 0, 0.004 * S), (0.024 * S, 0.017 * S, 0.014 * S), 2)
    nv, nf = cw._tube([(0.06 * S, 0, 0.002 * S), (0.085 * S, 0, 0.004 * S)], [0.013 * S, 0.012 * S], 8)
    e1 = ex.ell((0.106 * S, -0.012 * S, 0.008 * S), (0.003 * S, 0.002 * S, 0.003 * S)); e2 = ex.ell((0.106 * S, 0.012 * S, 0.008 * S), (0.003 * S, 0.002 * S, 0.003 * S))
    ex.part(kit, 'rw_turtle_body', [(sv, sf, 0), (pv, pf, 2), (nv, nf, 1), (hv, hf, 1), (*e1, 3), (*e2, 3)], M, root)
    fl = []
    for side in (-1, 1):
        for front in (True, False):
            pv_ = (0.04 * S, side * 0.045 * S, 0) if front else (-0.055 * S, side * 0.04 * S, 0)
            pz = ex.empty(kit, f'rw_tpiv{side}{front}', root, pv_)
            ln, wd = (0.075 * S, 0.02 * S) if front else (0.03 * S, 0.014 * S)
            fv, ff = ex.ell((-0.12 * ln if front else -0.3 * ln, side * ln * 0.62, 0), (ln * 0.19 if front else ln * 0.3, ln * 0.62 if front else ln * 0.45, 0.0035 * S), 2)
            fv = ex.rot_pts(fv, 'z', side * (-0.62 if front else -0.9))
            ex.part(kit, f'rw_tflip{side}{front}', [(fv, ff, 1)], M, pz); fl.append((pz, side, front))
    C = cw.catmull(path, 120); seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
    def pose(t):
        u = min(1.0, max(0.0, (t - t0) / (t1 - t0))); s = u * seg[-1]
        p = np.array([np.interp(s, seg, C[:, k]) for k in range(3)]); q = np.array([np.interp(min(s + 0.02, seg[-1]), seg, C[:, k]) for k in range(3)])
        stroke = math.sin(2 * math.pi * t / 2.6)
        root.location = tuple(p + np.array([0, 0, 0.012 * math.sin(2 * math.pi * t / 2.6 - 0.8)]))
        hd = math.atan2(q[1] - p[1], q[0] - p[0]); root.rotation_euler = (0.06 * stroke, -0.06 + 0.04 * stroke, hd)
        for pz, side, front in fl:
            if front: pz.rotation_euler = (side * 0.38 * stroke, 0.0, side * 0.22 * math.cos(2 * math.pi * t / 2.6))
            else: pz.rotation_euler = (side * 0.15 * stroke, 0, 0)
    kit.on_frame(pose); pose(0.0)


def anemone_protos(kit, seed=0):
    bp = kit.bpy; obs = []; rng = np.random.default_rng(seed + 90)
    cols = [((0.95, 0.45, 0.62), (0.98, 0.80, 0.86)), ((0.62, 0.36, 0.86), (0.90, 0.80, 1.0)), ((0.98, 0.58, 0.20), (1.0, 0.90, 0.60)), ((0.40, 0.78, 0.66), (0.86, 1.0, 0.90))]
    for k, (c0, c1) in enumerate(cols):
        m = cw.mat_varied(kit, f'rw_anem{k}', [c0, c1, c0], rough=0.45, translucent=0.4, bump=0.0, tip=(c1, 22.0))
        A = cw._Acc(); cv, cf = cw._tube([(0, 0, 0), (0, 0, 0.018)], [0.012, 0.010], 10); A.add(cv, cf, 0)
        for j in range(26):
            a = rng.uniform(0, 6.28); r0 = rng.uniform(0.002, 0.010); h = rng.uniform(0.022, 0.040); out = rng.uniform(0.3, 0.8)
            P = [(r0 * math.cos(a), r0 * math.sin(a), 0.017), ((r0 + out * h * 0.4) * math.cos(a), (r0 + out * h * 0.4) * math.sin(a), 0.017 + h * 0.6),
                 ((r0 + out * h * 0.8) * math.cos(a), (r0 + out * h * 0.8) * math.sin(a), 0.017 + h)]
            v, f = cw._tube(cw.catmull(P, 5), np.linspace(0.0024, 0.0009, 5), 5); A.add(v, f, 0)
        obs.append(A.build(bp, f'rw_anem{k}', [m], True, None))
    return obs


def fan_protos(kit, seed=0):
    bp = kit.bpy; rng = np.random.default_rng(seed + 95); obs = []
    for k, c in enumerate([(0.62, 0.22, 0.52), (0.92, 0.40, 0.28)]):
        m = cw.mat_simple(kit, f'rw_fan{k}', c, 0.6, sss=0.2); A = cw._Acc()
        def branch(p, d, L, depth):
            q = p + d * L; v, f = cw._tube([p, (p + q) / 2, q], [0.0022 * (depth + 1) / 3, 0.0018 * (depth + 1) / 3, 0.0012], 4, False); A.add(v, f, 0)
            if depth > 0:
                for s in (-1, 1):
                    a = s * rng.uniform(0.3, 0.6); d2 = np.array([d[0] * math.cos(a) - d[2] * math.sin(a) * 0, 0.0, 0.0]); ang = math.atan2(d[2], d[0]) + a
                    branch(q, np.array([math.cos(ang), rng.normal(0, 0.03), math.sin(ang)]), L * 0.72, depth - 1)
        for b in range(3): ang = math.radians(60 + 30 * b); branch(np.zeros(3), np.array([math.cos(ang), 0, math.sin(ang)]), 0.035, 4)
        obs.append(A.build(bp, f'rw_fan{k}', [m], True, None))
    return obs


def reef(kit, land, keep):
    rng = np.random.default_rng(23)
    def ok(x, y, mind=0.12):
        f = land.field(np.array([x]), np.array([y]))
        if f['depth'][0] < mind: return False
        return all(math.hypot(x - a, y - b) > r for a, b, r in keep)
    def region(n, box, dens_fn, rmin):
        P = []
        for _ in range(n * 30):
            if len(P) >= n: break
            x, y = rng.uniform(*box[0]), rng.uniform(*box[1])
            if rng.uniform() > dens_fn(x, y) or not ok(x, y): continue
            if all(math.hypot(x - a, y - b) > rmin for a, b in P): P.append((x, y))
        return np.array(P)
    def reefw(x, y):   # dense around the island slope and toward the near (+X, -Y) corner
        s = _isle_sd(x, y); slope = math.exp(-((s + 0.45) / 0.35) ** 2)
        corner = math.exp(-(((x - 1.25) / 0.75) ** 2 + ((y + 1.35) / 0.65) ** 2))
        site = 1.0 - math.exp(-(((x + 0.55) / 0.85) ** 2 + ((y + 1.55) / 0.55) ** 2))   # the wreck site stays open sand
        return min(1.0, 0.03 + 0.8 * slope + 1.0 * corner) * site
    box = ((-1.9, 1.92), (-1.93, 0.4))
    C = region(80, box, reefw, 0.08)
    land.scatter('rw_corals', cw.proto_corals(kit, 3), C, scale=rng.uniform(1.2, 2.3, len(C)), sway=0.0, sink=0.012)
    A = region(44, box, reefw, 0.06)
    land.scatter('rw_anemones', anemone_protos(kit), A, scale=rng.uniform(1.2, 2.0, len(A)), sway=0.16, speed=0.35, sink=0.008)
    Fn = region(12, box, reefw, 0.15)
    land.scatter('rw_fans', fan_protos(kit), Fn, scale=rng.uniform(2.2, 3.2, len(Fn)), sway=0.06, speed=0.3, sink=0.004)
    R = region(22, box, reefw, 0.14)
    land.scatter('rw_reefrock', cw.proto_rocks(kit, 5, 41, color=(0.70, 0.66, 0.58), moss=0.0, name='rw_rock'), R, scale=rng.uniform(0.06, 0.13, len(R)), sink=0.03)


class Diver:
    """A scuba diver (wetsuit, yellow tank and fins, a torch). Sits on the boat's gunwale, rolls back into the sea at
    T_ROLL, swims down along a path to the chest and hovers there, torch on the gold."""
    def __init__(self, kit, land, chest_bed):
        self.kit = kit; bp = kit.bpy
        suit = ex.mat(kit, 'rw_suit', (0.05, 0.06, 0.08), 0.45); yel = ex.mat(kit, 'rw_yellow', (0.98, 0.72, 0.08), 0.35)
        mask = ex.mat_pbr(kit, 'rw_mask', (0.10, 0.30, 0.36), 0.05, coat=1.0); skin = ex.mat(kit, 'rw_skin', (0.80, 0.58, 0.44), 0.5)
        M = [suit, yel, mask, skin]
        self.root = root = ex.empty(kit, 'rw_diver')
        tv, tf = ex.ell((0, 0, 0), (0.048, 0.024, 0.019), 2)
        hv, hf = ex.ell((0.066, 0, 0.003), (0.014, 0.012, 0.013), 2)
        mv, mf = ex.ell((0.075, 0, -0.004), (0.006, 0.010, 0.007), 1)
        kv, kf = cw._tube([(-0.032, 0, 0.024), (0.03, 0, 0.024)], [0.0115, 0.0115], 10)
        rv, rf = ex.ell((0.073, 0, -0.012), (0.004, 0.004, 0.004), 1)
        ex.part(kit, 'rw_diver_body', [(tv, tf, 0), (hv, hf, 0), (mv, mf, 2), (kv, kf, 1), (rv, rf, 1)], M, root)
        self.legs = []
        for side in (-1, 1):
            pz = ex.empty(kit, f'rw_hip{side}', root, (-0.04, side * 0.011, -0.002))
            lv_, lf_ = cw._tube([(0, 0, 0), (-0.045, 0, -0.002), (-0.085, 0, 0)], [0.0095, 0.008, 0.0062], 8)
            fv = [(-0.08, -0.011, 0), (-0.08, 0.011, 0), (-0.13, 0.016, 0.003), (-0.13, -0.016, 0.003)]
            ex.part(kit, f'rw_leg{side}', [(lv_, lf_, 0), (fv, [(0, 1, 2, 3)], 1)], M, pz); self.legs.append((pz, side))
        self.arms = []
        for side in (-1, 1):
            pz = ex.empty(kit, f'rw_shoulder{side}', root, (0.036, side * 0.024, 0.0))
            av, af = cw._tube([(0, 0, 0), (-0.03, 0, -0.002), (-0.058, 0, 0)], [0.0068, 0.006, 0.005], 8); gv, gf = ex.ell((-0.062, 0, 0), (0.006, 0.005, 0.005), 1)
            P = [(av, af, 0), (gv, gf, 0)]
            if side < 0:
                cv, cf = cw._tube([(-0.058, 0, -0.004), (-0.078, 0, -0.004)], [0.004, 0.0045], 8); P.append((cv, cf, 1))
            ex.part(kit, f'rw_arm{side}', P, M, pz); self.arms.append((pz, side))
            if side < 0:
                ld = bp.data.lights.new('rw_torch', 'SPOT'); ld.energy = 2.2; ld.spot_size = math.radians(30); ld.spot_blend = 0.6; ld.shadow_soft_size = 0.004; ld.color = (1.0, 0.95, 0.85)
                to = bp.data.objects.new('rw_torch', ld); kit.coll.objects.link(to); to.parent = pz; to.location = (-0.08, 0, -0.004); to.rotation_euler = (0, math.radians(90), 0)
                to.visible_camera = False; to.visible_transmission = False; to.visible_glossy = False; self.torch = to
        # the path
        bx, by, yaw = BOAT; n_out = np.array([math.sin(yaw), -math.cos(yaw), 0.0])     # the boat's -Y side, outward
        self.n_out = n_out; self.gun = np.array([bx, by, LV + 0.03]) + n_out * 0.068
        cx, cy = CHEST
        self.hover = np.array([cx - 0.15, cy + 0.07, chest_bed + 0.10])
        self.roll_end = self._roll(1.0)[0]
        self.path = cw.catmull([tuple(self.roll_end), tuple(self.roll_end + n_out * 0.03 + np.array([0.0, 0, -0.14])),
                                (cx - 0.30, cy + 0.22, LV - 0.40), (cx - 0.30, cy + 0.10, chest_bed + 0.17), tuple(self.hover)], 160)
        self.seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(self.path, axis=0), axis=1))]
        self.bubbles = []; bm = _mat_bubble(kit); rng = np.random.default_rng(9)
        for k in range(28):
            bv, bf = ex.ell((0, 0, 0), (1, 1, 1), 1); r = rng.uniform(0.003, 0.0075)
            ob = ex.part(kit, f'rw_bubble{k}', [(bv * r, bf, 0)], [bm]); ob.visible_shadow = False; self.bubbles.append((ob, r, (k % 3) / 3.0 + rng.uniform(0, 0.03), rng.uniform(0, 6.28)))   # three puffs in flight, one every 1.6 s
        kit.on_frame(self.pose); self.pose(0.0)
        # the splash: droplets thrown up, a foam ring and ripples
        sm = ex.mat(kit, 'rw_spray', (0.95, 0.98, 1.0), 0.2, emission=(0.9, 0.97, 1.0), strength=0.6); self.drops = []
        for k in range(26):
            bv, bf = ex.ell((0, 0, 0), (1, 1, 1), 1); r = rng.uniform(0.006, 0.013)
            ob = ex.part(kit, f'rw_drop{k}', [(bv * r, bf, 0)], [sm]); a = rng.uniform(0, 6.28); sp = rng.uniform(0.15, 0.4); up = rng.uniform(0.6, 1.1)
            self.drops.append((ob, np.array([math.cos(a) * sp, math.sin(a) * sp, up])))
        self.splash_at = self.gun + n_out * 0.10
        kit.on_frame(self.splash); self.splash(0.0)
        sx, sy = self.splash_at[:2]
        ex.ripples(kit, [lambda t: (sx, sy) if t > T_IN else (sx, sy + 9.0)], LV, 0.26, rate=1.1, rings=3, name='rw_splashrip')

    def _roll(self, e):
        from mathutils import Matrix, Vector
        n = self.n_out; up = np.array([0, 0, 1.0]); X = up; Z = n; Y = np.cross(Z, X); M0 = np.stack([X, Y, Z], 1)
        k = np.cross(up, n); R = np.array(Matrix.Rotation(2.5 * e, 3, Vector(tuple(k))))
        M = R @ M0
        pivot = self.gun + n * 0.10 * e + np.array([0, 0, -0.07 * e * e])
        return pivot + M @ np.array([0.035, 0, 0]), M

    def at(self, t):
        """Root position and orientation at time t."""
        if t < T_ROLL: p, M = self._roll(0.0); p = p + np.array([0, 0, 0.004 * math.sin(2 * math.pi * 0.45 * t)])
        elif t < T_SWIM: p, M = self._roll(ex.ease((t - T_ROLL) / (T_SWIM - T_ROLL)))
        else:
            u = ex.ease((t - T_SWIM) / (T_ARRIVE - T_SWIM)) ** 0.9; s = u * self.seg[-1]
            p = np.array([np.interp(s, self.seg, self.path[:, k]) for k in range(3)])
            q = np.array([np.interp(min(s + 0.04, self.seg[-1]), self.seg, self.path[:, k]) for k in range(3)])
            d = q - p
            if np.linalg.norm(d) < 1e-4 or u > 0.995: d = np.array([1.0, -0.15, -0.12])
            d = d / np.linalg.norm(d); d = d * np.array([1, 1, 0.75]); M = _frame_from(d)
            if t < T_SWIM + 0.8:     # blend out of the roll
                from mathutils import Matrix
                _, M1 = self._roll(1.0); w = ex.ease((t - T_SWIM) / 0.8)
                q1 = Matrix(M1.tolist()).to_quaternion(); q2 = Matrix(M.tolist()).to_quaternion(); M = np.array(q1.slerp(q2, w).to_matrix())
            if t > T_ARRIVE - 0.4: p = p + np.array([0, 0, 0.006 * math.sin(2 * math.pi * 0.35 * (t - T_ARRIVE))])
        return p, M

    def pose(self, t):
        p, M = self.at(t); self.root.location = tuple(p); _set_rot(self.root, M)
        if t < T_ROLL: kick, f = 0.08, 0.3
        elif t < T_SWIM: kick, f = 0.25, 1.2
        elif t < T_ARRIVE: kick, f = 0.38, 1.1
        else: kick, f = 0.16, 0.6
        for pz, side in self.legs:
            base = -0.9 if t < T_ROLL else 0.0
            pz.rotation_euler = (0, base + side * kick * math.sin(2 * math.pi * f * t), 0)
        for pz, side in self.arms:
            if t < T_ROLL: a = -0.25
            elif side > 0: a = -0.15
            else:
                a = -0.25 + (-2.2 + 0.25) * ex.ease((t - T_SWIM) / 1.2)
                a += -0.45 * ex.ease((t - (T_ARRIVE + 0.6)) / 1.2)
            pz.rotation_euler = (0, a + (0.03 * math.sin(1.3 * t) if t > T_SWIM else 0), side * 0.2)
        self.torch.data.energy = 0.0 if t < T_IN else 2.2 * ex.ease((t - T_IN) / 0.6)
        # bubbles: puffs from the regulator every 1.6 s, rising and wobbling, gone at the surface
        for ob, r, ph, wp in self.bubbles:
            if t < T_IN + 0.1: ob.hide_render = True; continue
            age = ((t - T_IN) + ph * 1.6 * 3) % (1.6 * 3); te = t - age
            if te < T_IN: ob.hide_render = True; continue
            p0, M0 = self.at(te); src = p0 + M0 @ np.array([0.075, 0, 0.0])
            z = src[2] + 0.10 * age + 0.02 * age * age
            if z > LV - 0.006: ob.hide_render = True; continue
            ob.hide_render = False; ob.location = (src[0] + 0.012 * math.sin(4 * age + wp), src[1] + 0.012 * math.cos(3.3 * age + wp), z)

    def splash(self, t):
        a = t - T_IN
        for ob, v in self.drops:
            if a < 0 or a > 0.7: ob.hide_render = True; continue
            p = self.splash_at + v * a + np.array([0, 0, -1.6 * a * a])
            ob.hide_render = bool(p[2] < LV); ob.location = tuple(map(float, p))


def title(kit):
    bp = kit.bpy; cu = bp.data.curves.new('rw_title', 'FONT'); cu.body = TITLE; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    font = os.path.join(ROOT, 'ads', 'fonts', 'InstrumentSans.ttf')
    if os.path.exists(font): cu.font = bp.data.fonts.load(font)
    cu.size = 1.0; cu.space_character = 1.06
    ob = bp.data.objects.new('rw_title', cu); kit.coll.objects.link(ob)
    m = cw._new_mat(bp, 'rw_titlemat'); g = G(m.node_tree, kit); alpha = g.value(0.0, 'rw_title_alpha')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.98, 0.94)), 'Strength': 1.15}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(alpha, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx); cu.materials.append(m)
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
    return ob, alpha


# ============================================================================== build and frame
def build(bpy, ctx):
    W, H = ctx['W'], ctx['H']
    kit = cw.Kit(bpy, seed=4, loop=DURATION)
    land = cw.block(kit, size=(4.0, 4.0), depth=1.32, strata=STRATA, seed=6, top=_top,
                    water=[cw.basin(lambda x, y: _isle_sd(x, y), depth=SEA_D, level=LV, shelf=0.65)], zones=_zones,
                    grass=0.8, grass_height=1.2, trees=0, boulders=4, flowers=0.25, under=False, corals=0,
                    water_tint=(0.20, 0.80, 0.84), water_density=1.05, water_glow=0.035,
                    bed=((0.95, 0.89, 0.72), (0.84, 0.77, 0.58)), caustics=0.9)
    rig = ex.cine_light(kit, land, SUN_AZ, SUN_EL, sun=4.6, sun_color=(1.0, 0.88, 0.70), fill=0.8, rim=0.6,
                        zenith=(0.14, 0.36, 0.70), horizon=(0.80, 0.80, 0.70), away=(0.60, 0.78, 0.90), ground=(0.50, 0.70, 0.72), amb=0.40)
    fl = bpy.data.materials.get('ex_floor')          # a pale sea-sand floor instead of the dusk floor (tropical daylight)
    if fl:
        for n in fl.node_tree.nodes:
            if n.bl_idname == 'ShaderNodeBsdfPrincipled': n.inputs['Base Color'].default_value = srgb((0.30, 0.46, 0.50))
    palms(kit, land)
    boat(kit)
    wr, wbed = wreck(kit, land)
    ch, cbed, glow = chest(kit, land)
    keep = [(WRECK[0], WRECK[1], 0.62), (CHEST[0], CHEST[1], 0.2), (BOAT[0] + 0.05, BOAT[1] - 0.3, 0.22), (-0.2, -1.5, 0.2)]
    reef(kit, land, keep)
    rays = Rays(kit, land, rig['sun_dir'], 22)
    school(kit)
    turtle(kit)
    ex.fish(kit, land, (1.05, -1.78), n=5, rx=0.22, ry=0.06, depth=(0.62, 0.74), name='rw_reeffish')
    diver = Diver(kit, land, cbed)
    cw.birds(kit, 3, center=(-0.5, 0.8), radius=1.2, height=1.1, size=0.05, color=(0.92, 0.92, 0.90))
    # easter eggs in the rock under the sea floor, museum lit
    eggs = ex.Eggs(kit, land, light_power=0.8); fy = eggs.faces['-Y']
    eggs.amphora('-Y', -0.40, fy.top(-0.40) - 0.085, tilt=0.30, light=3.0)
    eggs.ammonite('-Y', 0.70, -1.10, R=0.05)
    eggs.trilobite('+X', -0.85, -1.08, Lt=0.15)
    eggs.geode('+X', 0.55, -1.22, a=0.075, b=0.06)
    eggs.finish()
    ex.soften_roots(land, amount=0.0)
    ex.finish(bpy, W, H, bloom=0.2, threshold=1.3, vignette=0.24)
    cam = ex.ShotCam(kit); tob, talpha = title(kit)
    cw.apply_cycles(bpy, fast=True)
    cy = bpy.context.scene.cycles
    cy.max_bounces = 4; cy.diffuse_bounces = 1; cy.glossy_bounces = 1; cy.transmission_bounces = 4; cy.transparent_max_bounces = 10
    cy.adaptive_threshold = 0.03; cy.sample_clamp_direct = 10.0
    return {'kit': kit, 'land': land, 'cam': cam, 'rays': rays, 'diver': diver, 'title': tob, 'talpha': talpha, 'glow': glow, 'bed': cbed}


def shot_pose(S, name, u, t):
    """Camera for shot `name` at local progress u. Returns pos, target, lens, focus, fstop."""
    if name == 'arrive':          # wide three-quarter: slow push and a small arc (the island, the boat, the sea cut open)
        e = ex.ease(u); az = math.radians(-34 - 7 * e); el = math.radians(25 - 2 * e); D = 8.9 - 0.9 * e
        tgt = np.array([0.0, -0.15, -0.42 + 0.04 * e])
        pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
        return pos, tgt, 40.0, D, 16.0
    if name == 'descent':         # through the -Y glass: the camera sinks with the diver, a little lag behind her
        dv = S['diver']; ps = [dv.at(t - k * 0.12)[0] for k in range(6)]; dp = np.mean(ps, 0)
        tz = float(np.clip(dp[2] - 0.04, S['bed'] + 0.22, LV - 0.16)); tx = -0.30 + 0.35 * (dp[0] + 0.30)
        tgt = np.array([tx, -1.40, tz]); pos = np.array([tx - 0.10, -2.0 - 0.80, tz + 0.08])
        return pos, tgt, 30.0, float(np.linalg.norm(pos - np.array([dp[0], dp[1], dp[2]]))), 6.0
    # wreck: close on the chest by the bow, a slow push; the diver arrives from the upper left
    e = ex.ease(u); cx, cy = CHEST; b = S['bed']
    tgt = np.array([cx - 0.20, cy + 0.10, b + 0.04]); pos = np.array([cx - 0.28 - 0.04 * e, -2.0 - 0.95 + 0.22 * e, b + 0.13 - 0.02 * e])
    return pos, tgt, 38.0, float(np.linalg.norm(pos - np.array([cx, cy, b + 0.03]))), 5.0


def frame(bpy, ctx, S, i, t):
    S['kit'].update(t)
    tl = ctx['timeline'].at(t); pos, tgt, lens, focus, fstop = shot_pose(S, tl['name'], tl['u'], t)
    S['cam'].set(pos, tgt, lens, focus, fstop); S['rays'].update(pos); S['rays'].gain.default_value = RAY_GAIN[tl['name']]
    S['glow'].data.energy = 0.35 + (3.5 * ex.ease((t - 16.6) / 1.0) * (0.85 + 0.15 * math.sin(2 * math.pi * 1.3 * t)) if t > 16.6 else 0.0)
    a = ex.ease(t / 0.7) * (1 - ex.ease((t - 1.9) / 0.6)); S['talpha'].default_value = a; S['title'].hide_render = a <= 0.001
    if a > 0.001:                 # set in the camera's view at the focus distance (sharp), upper third
        cam = S['cam'].ob; d = focus * 0.9; hw = d * 18.0 / lens; hh = hw * ctx['H'] / ctx['W']
        S['title'].parent = cam; S['title'].location = (0.0, hh * 0.80, -d); S['title'].rotation_euler = (0, 0, 0)
        S['title'].scale = (hh * 0.12,) * 3
