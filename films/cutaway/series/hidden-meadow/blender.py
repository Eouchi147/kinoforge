"""The Hidden Meadow (Cutaway showcase series, film 3). 20 s, 9:16, 24 fps. Wildlife documentary, kids, nature brands.

A spring meadow in soft morning light sits on a block of earth cut open on two faces. Above: grass and flowers in the
wind, bees, butterflies, rabbits grazing beside their burrow. Below, in the cut face, one column of hidden homes: the
rabbit warren (two chambers, a mother with two kits), a mole digging its tunnel, a fox den with two cubs, an ant nest
busy with ants carrying leaf bits down to the queen. A hawk's shadow sweeps across the meadow; the two rabbits on top
bolt into the burrow and we see them arrive in the warren; calm returns and the camera pulls back to the whole world.

Shots (SHOTS; frame = t * 24):
  1 meadow  0.0-6.0 s   low three-quarter on the meadow, into the morning sun, a slow descending push (title 0-2.5 s)
  2 below   6.0-12.5 s  frontal on the -Y cut face, a slow crane down the column of homes (warren to ants)
  3 hawk   12.5-20.0 s  three-quarter on the top and the warren: the shadow passes (13.0-14.6 s), the rabbits dive
                        (13.4-15.3 s), then a slow pull back to the whole block (16.4-20 s)
Kit: films/styles/cutaway/cutaway.py and cinematic/extras.py (both imported, never edited). Everything moves as a
pure function of t. No volumes: haze and mist are cards, god rays are extras.Shafts cards.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
for p in (os.path.join(ROOT, 'films', 'styles', 'cutaway', 'cinematic'), os.path.join(ROOT, 'films', 'styles', 'cutaway'), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import extras as ex  # noqa: E402

G = cw.G
srgb = cw.srgb

SHOTS = [{'name': 'meadow', 'dur': 6.0}, {'name': 'below', 'dur': 6.5}, {'name': 'hawk', 'dur': 7.5}]
DURATION = sum(s['dur'] for s in SHOTS)
SETTINGS = {'samples': 20, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Medium High Contrast',
            'exposure': 0.25, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 4.0, 'adaptive_min_samples': 8,
            'denoising_prefilter': 'FAST'}
CHECK = {'title': 24, 'meadow': 110, 'below_top': 160, 'below_low': 285, 'hawk_dive': 330, 'arrive': 366, 'end': 470}

S_SIZE, DEPTH = 1.6, 1.4
SUN_AZ, SUN_EL = 158.0, 27.0
SHAFT_GAIN = {'meadow': 1.0, 'below': 0.25, 'hawk': 0.7}
STRATA = [('topsoil', 0.06, (0.22, 0.15, 0.09), 0.04), ('loam', 0.52, (0.52, 0.34, 0.20), 0.10), ('sand', 0.45, (0.80, 0.65, 0.42), 0.10),
          ('limestone', 0.20, (0.86, 0.82, 0.72), 0.05), ('bedrock', 1.0, (0.30, 0.29, 0.33), 0.30)]
TREES = [(-0.52, 0.50, 1.0, 'cone'), (0.36, 0.60, 0.80, 'round'), (-0.08, 0.66, 0.62, 'round')]
# the -Y face column of homes, in face coordinates (u = x, z); top of the face is about z = 0
WARREN_X = -0.30                      # burrow mouth (a notch at the cut edge)
WARREN = [(WARREN_X, 0.02), (-0.285, -0.08), (-0.235, -0.155), (-0.15, -0.205), (-0.10, -0.225)]
CH_A = (-0.12, -0.225, 0.125, 0.068)   # arrival chamber
CH_B = (-0.34, -0.365, 0.115, 0.062)   # nursery: mother and two kits
LINK_AB = [(-0.20, -0.255), (-0.25, -0.30), (-0.30, -0.345)]
FOX_X = 0.60
FOXT = [(FOX_X, 0.02), (0.585, -0.17), (0.47, -0.36), (0.33, -0.48), (0.22, -0.53)]
DEN = (0.12, -0.565, 0.165, 0.088)
ANT_X = -0.56
ANTS = [(ANT_X, 0.02), (-0.55, -0.20), (-0.53, -0.44), (-0.46, -0.62), (-0.33, -0.735), (-0.19, -0.775), (-0.05, -0.80),
        (0.08, -0.86), (0.17, -0.93), (0.05, -0.99), (-0.12, -1.0), (-0.27, -0.965)]
ANT_CH = [(-0.33, -0.735, 0.085, 0.048), (-0.05, -0.80, 0.085, 0.048), (0.17, -0.93, 0.072, 0.042), (-0.13, -1.0, 0.085, 0.046)]
GRAZE = [(-0.20, -0.52), (-0.50, -0.60)]     # where the two rabbits on top graze (short-cropped lawn, a trodden run to the burrow)
RS = 2.0                              # rabbit scale (the extras rabbit is storybook-small for a 4 m block; this block is 1.6 m)
T_SHADOW, T_ALARM, T_GO = 12.7, 13.25, 13.45     # hawk shadow reaches the block; rabbits look up; rabbits bolt
T_SAFE, T_CALM = 15.3, 16.4


# =============================================================================================== small helpers
def _runs(x, y, h):
    """Trodden rabbit runs from the grazing lawns to the burrow mouth (the kit's 'path' zone: bare earth)."""
    d = np.full(np.shape(x), 9.0)
    for gx, gy in GRAZE:
        a = np.array([gx, gy]); b = np.array([WARREN_X, -S_SIZE / 2]); ab = b - a
        t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / (ab @ ab), 0, 1); d = np.minimum(d, np.hypot(x - a[0] - t * ab[0], y - a[1] - t * ab[1]))
    return {'path': cw.smooth(0.03, 0.012, d + 0.008 * cw.fbm(x, y, 3, 2, 14)) * 0.8}

def smooth01(a, b, x):
    if b == a: return 1.0 if x >= b else 0.0
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)

def ground(land, x, y): return float(land.height(np.array([x]), np.array([y]))[0])

def emit_mat(kit, name, color, strength, alpha_node=None):
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': strength}); cw._finish(g, e)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    return m

def camera_only(ob):
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)

def top_holes(kit, land, holes):
    """Burrow mouths: the top surface goes transparent over small circles at the cut edge (the half tunnel behind the face
    shows through), the same trick extras.Eggs uses on the faces."""
    m = land.mats['top']; nt = m.node_tree; g = G(nt, kit)
    outn = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial'][0]
    lk = outn.inputs['Surface'].links[0]; src = lk.from_socket
    tc = g.node('ShaderNodeTexCoord'); px, py, _ = g.sep(tc.outputs['Object']); acc = None
    for cx, cy, r in holes:
        dx = g.math('SUBTRACT', px, cx); dy = g.math('SUBTRACT', py, cy)
        k = g.math('LESS_THAN', g.math('ADD', g.math('MULTIPLY', dx, dx), g.math('MULTIPLY', dy, dy)), r * r)
        acc = k if acc is None else g.math('MAXIMUM', acc, k)
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(acc, mx.inputs[0]); nt.links.new(src, mx.inputs[1]); g.link(tr, mx.inputs[2])
    nt.links.remove(lk); nt.links.new(mx.outputs[0], outn.inputs['Surface'])

def tunnel(eggs, face, pts, r, name, n=12):
    """A half-round tunnel along (u, z) points, open on the face, with no end caps (it opens to the sky or a chamber)."""
    P = cw.catmull(np.asarray(pts, float), n); V, F = ex.half_tube(P, r * 1.03)
    ob = ex.part(eggs.kit, name, [(V, F, 0)], [cavity(eggs.kit)]); eggs.faces[face].put(ob, 0.0, 0.0, 0.0015)
    for a, b in zip(P[:-1], P[1:]): eggs.openings.append((face, 'cap', (a[0], a[1], b[0], b[1], r)))
    return P

def cavity(kit):
    """Earth inside a burrow: lit soil at the rim, falling to deep shade at the back (local Y = depth into the block),
    so a tunnel reads as a hollow, not as a pipe."""
    key = ('hm', 'cavity')
    if key in kit.mats: return kit.mats[key]
    m = cw._new_mat(kit.bpy, 'hm_cavity'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']
    n = g.noise(pos, 90.0, 4.0); n2 = g.noise(pos, 14.0, 3.0); py = g.sep(pos)[1]
    rim = g.mix(n2.outputs['Fac'], srgb((0.40, 0.28, 0.17)), srgb((0.56, 0.40, 0.25)))
    deep = g.math('POWER', g.math('MULTIPLY', py, 1 / 0.04, clamp=True), 0.8)
    col = g.mix(deep, rim, srgb((0.075, 0.05, 0.035)))
    col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.35), col, srgb((0.05, 0.035, 0.02)))
    pr = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.97})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.9, 'Height': n.outputs['Fac'], 'Distance': 0.005}); g.put(pr, 'Normal', b)
    cw._finish(g, pr); kit.mats[key] = m; return m

def chamber(eggs, u, z, a, b, depth, name):
    return eggs.hole_ellipse('-Y', u, z, a, b, depth, name, material=cavity(eggs.kit))

def mouth_rim(kit, land, x, r, seed, name):
    """A crescent of loose soil clods round a burrow mouth on the top (inside the block only)."""
    rng = np.random.default_rng(seed); soil = ex.mat(kit, 'hm_soil', (0.30, 0.20, 0.12), 0.95, noise_amt=0.4, bump=0.5); A = []
    for k in range(16):
        a = rng.uniform(0.05, math.pi - 0.05); rr = r * rng.uniform(1.05, 1.6)
        cx, cy = x + rr * math.cos(a), -S_SIZE / 2 + rr * math.sin(a); z = ground(land, cx, cy)
        v, f = ex.ell((cx, cy, z + 0.002), np.array((0.012, 0.010, 0.007)) * rng.uniform(0.7, 1.5), 1, 0.3, int(rng.integers(0, 99))); A.append((v, f, 0))
    return ex.part(kit, name, A, [soil])

def straw_bed(kit, eggs, face, u, z, a, n, seed, name):
    rng = np.random.default_rng(seed); straw = ex.mat(kit, 'ex_straw', (0.78, 0.64, 0.36), 0.8); A = []
    for k in range(n):
        c = np.array([rng.uniform(-a, a), rng.uniform(0.01, 0.06), rng.uniform(-0.006, 0.006)])
        dv = np.array([rng.uniform(-1, 1), rng.uniform(-0.3, 0.3), rng.uniform(-0.15, 0.15)]); dv = dv / np.linalg.norm(dv) * rng.uniform(0.012, 0.024)
        v, f = cw._tube([c - dv, c, c + dv], [0.0013, 0.0014, 0.001], 4); A.append((v, f, 0))
    return eggs.obj(name, A, [straw], face, u, z)

def point_glow(kit, name, loc, power, color=(1.0, 0.78, 0.5), soft=0.02):
    ld = kit.bpy.data.lights.new(name, 'POINT'); ld.energy = power; ld.color = color; ld.shadow_soft_size = soft
    ob = kit.bpy.data.objects.new(name, ld); kit.coll.objects.link(ob); ob.location = tuple(map(float, loc)); ob.visible_camera = False; return ob

def orient(ob, fwd, up=(0, 0, 1.0)):
    from mathutils import Vector
    f = Vector(tuple(map(float, fwd)))
    if f.length < 1e-9: return
    ob.rotation_euler = f.to_track_quat('X', 'Z').to_euler()


# =============================================================================================== rabbits (extras' model, own motion)
class Bunny:
    """The extras rabbit model (copied so the motion can be our own): body, head, ears; root scale RS."""
    def __init__(self, kit, name, scale=RS, color=(0.52, 0.42, 0.32)):
        fur = ex.mat(kit, name + '_fur', color, 0.8, noise_amt=0.15); white = ex.mat(kit, 'ex_white', (0.92, 0.90, 0.86), 0.8)
        dark = ex.mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3); pink = ex.mat(kit, 'ex_pink', (0.92, 0.56, 0.58), 0.5, sss=0.2); ell = ex.ell
        self.root = ex.empty(kit, name); self.root.scale = (scale,) * 3
        bv, bf = ell((0, 0, 0.016), (0.017, 0.011, 0.0125), 2, 0.05, 4)
        pieces = [(bv, bf, 0), (*ell((-0.008, 0, 0.012), (0.012, 0.0125, 0.012)), 0), (*ell((-0.019, 0, 0.017), (0.0045, 0.0045, 0.0045)), 1),
                  (*ell((0.008, 0, 0.004), (0.006, 0.006, 0.004)), 0), (*ell((-0.012, -0.007, 0.004), (0.011, 0.004, 0.004)), 0),
                  (*ell((-0.012, 0.007, 0.004), (0.011, 0.004, 0.004)), 0)]
        self.body = ex.part(kit, name + '_body', pieces, [fur, white], self.root)
        hp = [(*ell((0.008, 0, 0.004), (0.0088, 0.0075, 0.008)), 0), (*ell((0.0165, 0, 0.002), (0.0025, 0.002, 0.002)), 2),
              (*ell((0.012, -0.0055, 0.0065), (0.0013, 0.0011, 0.0013)), 2), (*ell((0.012, 0.0055, 0.0065), (0.0013, 0.0011, 0.0013)), 2)]
        self.head = ex.part(kit, name + '_head', hp, [fur, white, dark], self.body, (0.012, 0, 0.022))
        self.ears = []
        for side in (-1, 1):
            ev, ef = ell((0, 0, 0.011), (0.0035, 0.0012, 0.012)); iv, if_ = ell((0, -0.0004 * side, 0.011), (0.0022, 0.0008, 0.009))
            self.ears.append(ex.part(kit, f'{name}_ear{side}', [(ev, ef, 0), (iv, if_, 1)], [fur, pink], self.head, (0.002, side * 0.0035, 0.008)))
    def look(self, t, alert, ph=0.0, graze=0.0, hop=0.0):
        """alert 0..1 (ears up, head up and still); graze 0..1 (head down nibbling); hop 0..1 (body stretch)."""
        sniff = 0.08 * math.sin(2 * math.pi * 6 * t + ph) * (1 - alert)
        nib = graze * (1 - alert) * (0.55 + 0.08 * math.sin(2 * math.pi * 2.2 * t + ph))
        self.head.rotation_euler = (0.0, 0.1 + nib + sniff * 0.3 - 0.25 * alert, 0.25 * math.sin(2 * math.pi * 0.3 * t + ph) * (1 - alert) + 0.35 * alert * math.sin(2 * math.pi * 0.5 * (t - T_ALARM)))
        for k, e in enumerate(self.ears):
            tw = 0.25 * max(0.0, math.sin(2 * math.pi * 0.7 * t + ph + 2 * k)) ** 10
            e.rotation_euler = (((-1) ** k) * (0.18 - 0.1 * alert), 0.30 - 0.45 * alert + 0.5 * hop + 0.2 * (1 - alert) * graze + tw, 0.0)
        self.body.rotation_euler = (0.0, -0.35 * hop, 0.0)
        br = 1.0 + 0.025 * math.sin(2 * math.pi * (0.9 + 1.4 * alert) * t + ph); self.body.scale = (1.0, br, br)

def rabbit_runner(kit, land, face, spot, yaw0, route_uz, end_uz, end_yaw, name, t_go, run_time, ph, color=(0.52, 0.42, 0.32), scale=2.35):
    """A rabbit grazing on the top at `spot` (x, y); it looks up at T_ALARM, bolts at t_go to the burrow mouth, runs down
    the tunnel (route in face u, z at depth d) and settles in the arrival chamber at end_uz."""
    b = Bunny(kit, name, scale=scale, color=color); F = face; d_in = 0.026
    x0, y0 = spot; mouth = np.array([WARREN_X, -S_SIZE / 2 + 0.05, ground(land, WARREN_X, -S_SIZE / 2 + 0.05)])
    pts = [np.array([x0, y0, ground(land, x0, y0)])]
    mid = (pts[0] + mouth) / 2; mid[2] = ground(land, mid[0], mid[1]); pts.append(mid); pts.append(mouth)
    for (u, z) in route_uz: pts.append(F.world(u, z - 0.03, d_in))
    pts.append(F.world(end_uz[0], end_uz[1], d_in + 0.012))
    P = np.array(pts); seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    dense = np.linspace(0, s[-1], 400); C = np.stack([np.interp(dense, s, P[:, k]) for k in range(3)], 1)
    sm = C.copy()
    for _ in range(6): sm[1:-1] = (sm[:-2] + sm[1:-1] * 2 + sm[2:]) / 4    # soften the corners of the run
    sm[0] = P[0]; sm[-1] = P[-1]; L = s[-1]
    top_end = s[2]
    def pose(t):
        u = (t - t_go) / run_time
        if u <= 0:            # grazing, then alarmed
            al = smooth01(T_ALARM, T_ALARM + 0.18, t); p = P[0]
            yaw = yaw0 + 0.3 * math.sin(2 * math.pi * 0.11 * t + ph) * (1 - al)
            b.root.location = tuple(p); b.root.rotation_euler = (0, 0, yaw); b.look(t, al, ph, graze=1.0)
            b.root.location = (p[0], p[1], p[2] - 0.001); return
        if u >= 1:            # safe in the chamber: alert, then calm
            al = 1.0 - smooth01(T_CALM - 0.4, T_CALM + 0.8, t); p = P[-1]
            b.root.location = tuple(p); b.root.rotation_euler = (0, 0, end_yaw); b.look(t, al * 0.8, ph); return
        dist = L * (1 - (1 - u) ** 1.7)          # bolts from a standstill at full speed, slows into the chamber
        i = int(np.clip(np.searchsorted(dense, dist), 1, len(dense) - 1)); p = sm[i]; fwd = sm[min(i + 4, len(sm) - 1)] - sm[max(i - 4, 0)]
        hopf = abs(math.sin(math.pi * 5.0 * (t - t_go)))
        lift = 0.02 * hopf if dist < top_end else 0.004 * hopf
        b.root.location = (p[0], p[1], p[2] + lift); orient(b.root, fwd)
        b.look(t, 0.6, ph, hop=hopf)
    kit.on_frame(pose); pose(0.0); return b

def resting_rabbit(kit, face, u, z, d, yaw, name, scale=RS, ph=0.0, color=(0.52, 0.42, 0.32), alert_gain=1.0):
    b = Bunny(kit, name, scale, color); face.put(b.root, u, z, d); b.root.rotation_euler = (0, 0, face.rz + yaw)
    def pose(t, b=b):
        al = alert_gain * smooth01(T_SHADOW + 0.35, T_SHADOW + 0.6, t) * (1 - smooth01(T_CALM, T_CALM + 1.0, t))
        b.look(t, al, ph, graze=0.25)
    kit.on_frame(pose); pose(0.0); return b


# =============================================================================================== fox cubs
def cub(kit, face, u, z, d, yaw, name, sleeping=False, scale=1.55):
    red = ex.mat(kit, 'hm_cubred', (0.80, 0.42, 0.18), 0.8, noise_amt=0.12); white = ex.mat(kit, 'ex_white', (0.92, 0.90, 0.86), 0.8)
    dark = ex.mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3); sock = ex.mat(kit, 'ex_foxsock', (0.12, 0.08, 0.06), 0.7); ell = ex.ell; cone = ex.cone
    root = ex.empty(kit, name); face.put(root, u, z, d); root.rotation_euler = (0, 0, face.rz + yaw); root.scale = (scale,) * 3
    hip = 0.022
    if sleeping:   # curled nose to tail
        bv, bf = ell((0, 0, 0.011), (0.026, 0.017, 0.011), 2, 0.04, 5)
        body = ex.part(kit, name + '_body', [(bv, bf, 0), (*ell((0.012, -0.002, 0.008), (0.012, 0.012, 0.008)), 1)], [red, white], root)
        hp = [(*ell((0, 0, 0), (0.011, 0.009, 0.0075)), 0), (*cone((0.004, 0, -0.001), (0.019, 0.0, -0.003), 0.005, 0.0012, 8), 0),
              (*ell((0.019, 0, -0.003), (0.0016, 0.0016, 0.0016)), 2), (*cone((-0.003, -0.005, 0.005), (-0.006, -0.007, 0.017), 0.0038, 0.0005, 6), 0),
              (*cone((-0.003, 0.005, 0.005), (-0.006, 0.007, 0.017), 0.0038, 0.0005, 6), 0),
              (*ell((0.007, -0.0062, 0.003), (0.003, 0.0006, 0.0006)), 2)]
        head = ex.part(kit, name + '_head', hp, [red, white, dark], root, (0.022, -0.012, 0.009))
        tp = cw.catmull([(-0.024, 0.0, 0.008), (-0.03, -0.014, 0.007), (-0.012, -0.024, 0.007), (0.012, -0.024, 0.008)], 9)
        tv, tf = cw._tube(tp, np.array([0.006, 0.0085, 0.0095, 0.0095, 0.009, 0.0085, 0.007, 0.005, 0.0015]), 8)
        wv, wf = ell(tp[-2], (0.006, 0.0055, 0.0055)); ex.part(kit, name + '_tail', [(tv, tf, 0), (wv, wf, 1)], [red, white], root)
        def pose(t):
            s = 1.0 + 0.04 * math.sin(2 * math.pi * 0.5 * t); body.scale = (1.0, s, s)
            ear = 0.3 * max(0.0, math.sin(2 * math.pi * 0.23 * t + 1.0)) ** 30
            head.rotation_euler = (ear * 0.3, 0.0, 0.05 * math.sin(2 * math.pi * 0.5 * t))
        kit.on_frame(pose); pose(0.0); return root
    bv, bf = ell((0, 0, hip + 0.010), (0.026, 0.011, 0.012), 2, 0.04, 5)
    body = ex.part(kit, name + '_body', [(bv, bf, 0), (*ell((0.018, 0, hip + 0.006), (0.010, 0.009, 0.010)), 1)], [red, white], root)
    legs = []
    for k, (lx, ly) in enumerate(((0.017, -0.006), (0.017, 0.006), (-0.017, -0.006), (-0.017, 0.006))):
        lv, lf = cw._tube([(0, 0, 0), (0, 0, -hip * 0.5), (0, 0, -hip - 0.002)], [0.0042, 0.0032, 0.0026], 6)
        legs.append(ex.part(kit, f'{name}_leg{k}', [(lv, lf, 0)], [sock], root, (lx, ly, hip + 0.004)))
    hp = [(*ell((0.010, 0, 0.004), (0.0115, 0.0095, 0.0095)), 0), (*cone((0.014, 0, 0.0015), (0.028, 0, -0.001), 0.0058, 0.0013, 8), 0),
          (*ell((0.028, 0, -0.001), (0.0019, 0.0019, 0.0019)), 2), (*ell((0.016, 0, -0.003), (0.007, 0.006, 0.004)), 1),
          (*cone((0.006, -0.005, 0.010), (0.004, -0.0075, 0.026), 0.0048, 0.0006, 6), 0), (*cone((0.006, 0.005, 0.010), (0.004, 0.0075, 0.026), 0.0048, 0.0006, 6), 0),
          (*ell((0.018, -0.006, 0.007), (0.0016, 0.0012, 0.0016)), 2), (*ell((0.018, 0.006, 0.007), (0.0016, 0.0012, 0.0016)), 2)]
    head = ex.part(kit, name + '_head', hp, [red, white, dark], root, (0.026, 0, hip + 0.016))
    tp = cw.catmull([(0, 0, 0), (-0.014, 0, -0.004), (-0.028, 0, -0.002), (-0.04, 0, 0.003)], 9)
    tv, tf = cw._tube(tp, np.array([0.004, 0.007, 0.0085, 0.009, 0.009, 0.008, 0.0065, 0.0045, 0.0013]), 8)
    wv, wf = ell(tp[-2], (0.0055, 0.005, 0.005))
    tail = ex.part(kit, name + '_tail', [(tv, tf, 0), (wv, wf, 1)], [red, white], root, (-0.024, 0, hip + 0.012))
    base = root.location.copy()
    def pose(t):
        # play: a crouch (play bow), a little pounce forward, back again, every 2.6 s; the tail wags all the time
        c = (t % 2.6) / 2.6; bow = smooth01(0.0, 0.25, c) * (1 - smooth01(0.35, 0.45, c)); jump = math.sin(math.pi * min(1, max(0, (c - 0.35) / 0.22))) if 0.35 < c < 0.57 else 0.0
        fw = smooth01(0.35, 0.57, c) * (1 - smooth01(0.7, 1.0, c))
        off = face.r * (0.03 * fw * (1 if math.cos(yaw) > 0 else -1)) + np.array([0, 0, 0.022 * jump])
        root.location = (base[0] + off[0], base[1] + off[1], base[2] + off[2])
        body.rotation_euler = (0.0, -0.32 * bow + 0.2 * jump, 0.0)
        for k, lg in enumerate(legs): lg.rotation_euler = (0.0, (0.9 * bow if k < 2 else -0.15 * bow) + 0.5 * jump * (1 if k < 2 else -1), 0.0)
        head.rotation_euler = (0.25 * math.sin(2 * math.pi * 0.4 * t), 0.15 * bow - 0.1 * jump, 0.2 * math.sin(2 * math.pi * 0.25 * t))
        tail.rotation_euler = (0.0, -0.2 + 0.3 * bow, 0.55 * math.sin(2 * math.pi * 3.2 * t))
    kit.on_frame(pose); pose(0.0); return root


# =============================================================================================== ants
def ant_parts(kit, name, queen=False, leaf=True):
    body = ex.mat(kit, 'hm_ant', (0.22, 0.08, 0.05), 0.35); leafm = ex.mat(kit, 'hm_antleaf', (0.42, 0.66, 0.18), 0.6, sss=0.3); ell = ex.ell
    k = 1.7 if queen else 1.0
    P = [(*ell((-0.0055 * k, 0, 0.0022), (0.0042 * k * (1.4 if queen else 1), 0.0031 * k, 0.0029 * k)), 0), (*ell((0.0, 0, 0.0024), (0.0026, 0.0016, 0.0017)), 0),
         (*ell((0.0045, 0, 0.0028), (0.0021, 0.0019, 0.0019)), 0)]
    for s in (-1, 1):
        for j, x in enumerate((-0.0015, 0.0, 0.0015)):
            v, f = cw._tube([(x, 0, 0.0018), (x + 0.0012 * (j - 1), s * 0.0042, 0.0016), (x + 0.0022 * (j - 1), s * 0.0058, 0.0)], [0.00045, 0.0004, 0.0003], 4)
            P.append((v, f, 0))
        v, f = cw._tube([(0.0058, s * 0.0008, 0.0036), (0.0075, s * 0.0028, 0.0058), (0.0098, s * 0.0034, 0.0052)], [0.0004, 0.00035, 0.0003], 4); P.append((v, f, 0))
    mats = [body]
    if leaf:
        P.append(([(0.003, 0, 0.004), (0.006, -0.002, 0.012), (0.009, 0.0, 0.016), (0.0075, 0.002, 0.009)], [(0, 1, 2, 3)], 1)); mats.append(leafm)
    return P, mats

def ant_column(kit, eggs, face, route, n, speed, r, name, seed):
    """Ants walking the tunnel floor up and down the route (ping-pong); going down they carry a leaf bit, coming up empty."""
    C = cw.catmull(np.asarray(route, float), 160); seg = np.linalg.norm(np.diff(C, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); L = s[-1]
    rng = np.random.default_rng(seed)
    for i in range(n):
        P, mats = ant_parts(kit, f'{name}{i}')
        with_leaf = ex.part(kit, f'{name}{i}_l', P, mats); P2, m2 = ant_parts(kit, f'{name}{i}', leaf=False)
        bare = ex.part(kit, f'{name}{i}_b', P2, m2)
        sc = 1.6 * rng.uniform(0.9, 1.1); with_leaf.scale = bare.scale = (sc,) * 3
        off = rng.uniform(0, 2 * L); sp = speed * rng.uniform(0.85, 1.15); dd = rng.uniform(0.25, 0.6) * r
        def pose(t, wl=with_leaf, br=bare, off=off, sp=sp, dd=dd, k=i):
            q = (off + sp * t) % (2 * L); down = q < L; dist = q if down else 2 * L - q
            j = int(np.clip(np.searchsorted(s, dist), 1, len(C) - 1)); a, b = C[j - 1], C[j]; w = (dist - s[j - 1]) / max(1e-9, s[j] - s[j - 1]); p = a + (b - a) * w
            tg = (b - a) if down else (a - b); tg = tg / (np.linalg.norm(tg) + 1e-9); nrm = np.array([-tg[1], tg[0]])
            if nrm[1] > 0: nrm = -nrm
            p = p + nrm * (r * 0.72); wob = 0.0012 * math.sin(2 * math.pi * 7 * t + k)
            pos = face.world(p[0], p[1] + wob, dd); fwd = face.r * tg[0] + np.array([0, 0, tg[1]])
            for ob, on in ((wl, down), (br, not down)):
                ob.location = tuple(pos) if on else (0, 0, -50); orient(ob, fwd)
        kit.on_frame(pose); pose(0.0)
    return C

def surface_ants(kit, land, path, n, speed, name, seed):
    C = cw.catmull(np.asarray(path, float), 120); seg = np.linalg.norm(np.diff(C, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); L = s[-1]
    rng = np.random.default_rng(seed)
    for i in range(n):
        P, mats = ant_parts(kit, f'{name}{i}'); ob = ex.part(kit, f'{name}{i}', P, mats); ob.scale = (1.7,) * 3; off = rng.uniform(0, L)
        def pose(t, ob=ob, off=off, k=i):
            dist = (off + speed * t) % L; j = int(np.clip(np.searchsorted(s, dist), 1, len(C) - 1)); p = C[j]; tg = C[j] - C[j - 1]
            side = 0.004 * math.sin(2 * math.pi * 1.3 * t + k); nrm = np.array([-tg[1], tg[0]]) / (np.linalg.norm(tg) + 1e-9)
            x, y = p + nrm * side; ob.location = (x, y, ground(land, x, y) + 0.001)
            sc = min(1.0, min(dist, L - dist) / 0.02) * 1.7; ob.scale = (sc,) * 3; orient(ob, (tg[0], tg[1], 0.0))
        kit.on_frame(pose); pose(0.0)


# =============================================================================================== bees, motes, hawk, haze
def bees(kit, land, spots, seed=17, name='hm_bee'):
    rng = np.random.default_rng(seed); ell = ex.ell
    yel = ex.mat(kit, 'hm_beeyel', (0.95, 0.70, 0.12), 0.5); blk = ex.mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3)
    wing = cw._new_mat(kit.bpy, 'hm_wing'); g = G(wing.node_tree, kit)
    gl = g.node('ShaderNodeBsdfGlossy', ins={'Color': (1, 1, 1, 1), 'Roughness': 0.15}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.put(mx, 0, 0.6); g.link(gl, mx.inputs[1]); g.link(tr, mx.inputs[2]); cw._finish(g, mx)
    for i, (cx, cy) in enumerate(spots):
        root = ex.empty(kit, f'{name}{i}'); root.scale = (1.6,) * 3
        ex.part(kit, f'{name}{i}_b', [(*ell((-0.003, 0, 0), (0.0055, 0.0042, 0.0042)), 0), (*ell((-0.0038, 0, 0), (0.0016, 0.0046, 0.0046)), 1),
                                       (*ell((-0.0068, 0, 0), (0.0012, 0.0036, 0.0036)), 1), (*ell((0.0032, 0, 0.0004), (0.0034, 0.0034, 0.0034)), 1),
                                       (*ell((0.0068, 0, 0.0), (0.0024, 0.0026, 0.0026)), 1)], [yel, blk], root)
        wings = []
        for sd in (-1, 1):
            V = [(0.002, 0, 0.003), (0.0, sd * 0.009, 0.004), (-0.006, sd * 0.008, 0.0035), (-0.003, sd * 0.002, 0.003)]
            wings.append(ex.part(kit, f'{name}{i}_w{sd}', [(V, [(0, 1, 2, 3)], 0)], [wing], root))
        ph = rng.uniform(0, 6.28, 5); r1, r2 = rng.uniform(0.05, 0.12, 2)
        def pose(t, root=root, wings=wings, ph=ph, cx=cx, cy=cy, r1=r1, r2=r2):
            x = cx + r1 * math.sin(0.9 * t + ph[0]) + 0.02 * math.sin(3.1 * t + ph[1]); y = cy + r2 * math.sin(0.7 * t + ph[2]) + 0.02 * math.sin(2.7 * t + ph[3])
            dx = r1 * 0.9 * math.cos(0.9 * t + ph[0]) + 0.062 * math.cos(3.1 * t + ph[1]); dy = r2 * 0.7 * math.cos(0.7 * t + ph[2]) + 0.054 * math.cos(2.7 * t + ph[3])
            x = min(max(x, -0.78), 0.78); y = min(max(y, -0.78), 0.78)
            root.location = (x, y, ground(land, x, y) + 0.075 + 0.025 * math.sin(1.7 * t + ph[4])); root.rotation_euler = (0, 0, math.atan2(dy, dx))
            a = math.sin(2 * math.pi * 23.0 * t + ph[1])
            for k, w in enumerate(wings): w.rotation_euler = ((-1) ** k * 0.9 * a, 0, 0)
        kit.on_frame(pose); pose(0.0)

def motes(kit, land, n=46, seed=23, name='hm_mote'):
    """Pollen and dust specks hanging in the low sun, drifting slowly (camera only)."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name + '_mat'); g = G(m.node_tree, kit); oi = g.node('ShaderNodeObjectInfo')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.86, 0.6))}); g.put(e, 'Strength', g.math('ADD', 2.0, g.math('MULTIPLY', oi.outputs['Random'], 5.0))); cw._finish(g, e)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    rng = np.random.default_rng(seed); V0, F0 = cw._icosphere(1)
    for i in range(n):
        ob = cw.mk_mesh(bpy, f'{name}{i}', V0 * rng.uniform(0.0011, 0.0022), F0, [m], None, True, kit.coll); camera_only(ob)
        x0, y0, z0 = rng.uniform(-0.85, 0.85), rng.uniform(-0.85, 0.85), rng.uniform(0.03, 0.6); ph = rng.uniform(0, 6.28, 3)
        def pose(t, ob=ob, x0=x0, y0=y0, z0=z0, ph=ph):
            ob.location = (x0 + 0.04 * math.sin(0.23 * t + ph[0]) + 0.008 * t, y0 + 0.04 * math.sin(0.19 * t + ph[1]), z0 + 0.03 * math.sin(0.31 * t + ph[2]) + 0.004 * t)
        kit.on_frame(pose); pose(0.0)

def hawk(kit, land, sun_dir, h=0.85, t_mid=14.0, speed=1.1, heading=(0.42, -0.91), over=(-0.36, -0.52), name='hm_hawk',
         veil=(0.06, 0.09, 0.12), veil_alpha=0.2):
    """A hawk's shadow. The hawk itself is never seen: a flat horizontal silhouette (wings, tail) high between the sun and
    the meadow, seen by shadow rays only (projection between horizontal planes is a translation, so the shadow keeps the
    true shape). Dense backlit grass hides a real shadow (most of its light is fill, bounce and translucency), so the
    shadow is also art-directed: the same silhouette laid in the grass at three blade heights as soft dark veils (camera
    rays only), each exactly where the sun would throw it at that height. Two slow wing beats; it passes `over` at t_mid."""
    bpy = kit.bpy; m = ex.mat(kit, 'hm_hawkm', (0.1, 0.08, 0.06), 0.8)
    vm = cw._new_mat(bpy, 'hm_veil'); g = G(vm.node_tree, kit)
    tr = g.node('ShaderNodeBsdfTransparent'); dk = g.node('ShaderNodeBsdfDiffuse', ins={'Color': (0.0, 0.0, 0.0, 1.0)}); mx = g.node('ShaderNodeMixShader')
    geo = g.node('ShaderNodeNewGeometry'); wx, wy, _ = g.sep(geo.outputs['Position']); hs = S_SIZE / 2 - 0.004    # only over the block
    inside = g.math('MULTIPLY', g.math('LESS_THAN', g.math('ABSOLUTE', wx), hs), g.math('LESS_THAN', g.math('ABSOLUTE', wy), hs))
    g.link(g.math('MULTIPLY', inside, veil_alpha), mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(dk, mx.inputs[2]); cw._finish(g, mx)
    def wing(sd):
        return [(0.02, 0, 0), (0.035, sd * 0.06, 0), (0.02, sd * 0.15, 0), (-0.005, sd * 0.23, 0), (-0.035, sd * 0.22, 0), (-0.04, sd * 0.17, 0),
                (-0.055, sd * 0.12, 0), (-0.04, sd * 0.05, 0), (-0.03, 0, 0)]
    bodyV = [(0.085, 0, 0), (0.06, 0.018, 0), (0.0, 0.026, 0), (-0.07, 0.016, 0), (-0.13, 0.04, 0), (-0.145, 0.0, 0), (-0.13, -0.04, 0), (-0.07, -0.016, 0), (0.0, -0.026, 0), (0.06, -0.018, 0)]
    def bird(nm, mat, shadow_only):
        root = ex.empty(kit, nm)
        body = ex.part(kit, nm + '_body', [(bodyV, [tuple(range(len(bodyV)))], 0)], [mat], root); wings = []
        for sd in (-1, 1):
            V = wing(sd); F = [tuple(range(len(V)))] if sd > 0 else [tuple(reversed(range(len(V))))]
            wings.append(ex.part(kit, f'{nm}_w{sd}', [(V, F, 0)], [mat], root))
        for ob in [body] + wings:
            if shadow_only:
                for at in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, at, False)
            else: camera_only(ob)
        root.scale = (1.7,) * 3; return root, wings
    birds = [(bird(name, m, True), h)] + [(bird(f'{name}_veil{k}', vm, False), -z) for k, z in enumerate(veil)]
    sd = np.asarray(sun_dir, float); hd = np.array([heading[0], heading[1], 0.0]); hd /= np.linalg.norm(hd)
    zt = ground(land, *over)
    def pose(t):
        S = np.array([over[0], over[1], zt]) + hd * speed * (t - t_mid) + np.array([-hd[1], hd[0], 0]) * 0.12 * math.sin(0.9 * (t - t_mid))
        rz = math.atan2(hd[1], hd[0]) + 0.12 * math.cos(0.9 * (t - t_mid))
        beat = math.sin(2 * math.pi * 1.6 * (t - t_mid + 0.3)) if abs(t - t_mid + 0.3) < 0.62 else 0.0
        for (root, wings), hh in birds:      # hh > 0: the hawk, hh above the ground; hh < 0: a veil -hh above the ground
            p = S + sd * (hh / sd[2]) if hh > 0 else S + np.array([0, 0, -hh]) + sd * (-hh / sd[2]) * 0.0
            if hh < 0:   # where the shadow line through the hawk meets the plane z = ground - hh
                hp = S + sd * (h / sd[2]); p = hp - sd * ((hp[2] - (zt - hh)) / sd[2])
            root.location = tuple(p); root.rotation_euler = (0, 0, rz)
            for w in wings: w.scale = (1.0, 1.0 - 0.3 * abs(beat), 1.0)
    kit.on_frame(pose); pose(0.0); return birds[0][0][0]

def haze_cards(kit, cam_az=-56.0, name='hm_haze'):
    """Morning haze as cards (no volume): wide soft emissive bands behind the block that veil the horizon and the floor,
    drifting slowly; camera rays only."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name + '_mat'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); tv = ex.time_value(kit, g)
    gx, gy, _ = g.sep(tc.outputs['UV'])
    band = g.math('MULTIPLY', g.math('SINE', g.math('MULTIPLY', gy, math.pi)), 1.0); band = g.math('POWER', g.math('MAXIMUM', band, 0.0), 1.6)
    edge = g.math('MULTIPLY', g.math('SINE', g.math('MULTIPLY', gx, math.pi)), 1.6, clamp=True)
    n = g.noise(g.comb(g.math('ADD', g.math('MULTIPLY', gx, 6.0), g.math('MULTIPLY', tv, 0.03)), g.math('MULTIPLY', gy, 2.0), 0.0), 1.4, 3.0, 0.5)
    a = g.math('MULTIPLY', g.math('MULTIPLY', band, edge), g.math('ADD', 0.35, g.math('MULTIPLY', n.outputs['Fac'], 0.9)))
    oi = g.node('ShaderNodeObjectInfo'); a = g.math('MULTIPLY', a, g.math('ADD', 0.35, g.math('MULTIPLY', oi.outputs['Random'], 0.3)))
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.88, 0.74)), 'Strength': 0.75}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(g.math('MINIMUM', a, 0.85), mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    away = ex.sph(cam_az + 180, 0); side = np.array([-away[1], away[0], 0])
    for k, (dist, w, z0, z1) in enumerate([(2.6, 9.0, -1.9, 0.0), (4.5, 14.0, -2.2, 0.5), (7.5, 22.0, -2.6, 1.2)]):
        c = away * dist; V = [tuple(c - side * w / 2 + (0, 0, z0)), tuple(c + side * w / 2 + (0, 0, z0)), tuple(c + side * w / 2 + (0, 0, z1)), tuple(c - side * w / 2 + (0, 0, z1))]
        ob = cw.mk_mesh(bpy, f'{name}{k}', V, [(0, 1, 2, 3)], [m], None, False, kit.coll); camera_only(ob)
        ob.data.uv_layers.new(name='UVMap')

def title(kit, cam, root, text='The Hidden Meadow'):
    bpy = kit.bpy; cu = bpy.data.curves.new('hm_title', 'FONT'); cu.body = text; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    font = os.path.join(root, 'ads', 'fonts', 'Archivo.ttf')
    if os.path.exists(font): cu.font = bpy.data.fonts.load(font)
    cu.size = 1.0; cu.space_character = 1.06
    ob = bpy.data.objects.new('hm_title', cu); kit.coll.objects.link(ob)
    m = cw._new_mat(bpy, 'hm_titlemat'); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.97, 0.92)), 'Strength': 1.6}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    alpha = g.value(0.0, 'hm_title_alpha'); g.link(alpha, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx)
    cu.materials.append(m); camera_only(ob); ob.parent = cam.ob
    bpy.context.view_layer.update(); w = ob.dimensions[0]
    if w < 0.5: w = 0.56 * len(text)          # dimensions not evaluated: a fair estimate for Archivo
    return {'ob': ob, 'alpha': alpha, 'w1': w}


# =============================================================================================== build
def build(bpy, ctx):
    W, H = ctx['W'], ctx['H']
    kit = cw.Kit(bpy, seed=5, loop=DURATION)
    holes = [(WARREN_X, -S_SIZE / 2, 0.052), (FOX_X, -S_SIZE / 2, 0.046), (ANT_X, -S_SIZE / 2, 0.022)]
    clear = [(x, y, r * 2.2) for x, y, r in holes]
    season = dict(cw.SEASONS['spring']); season['leaf'] = [(0.42, 0.66, 0.22), (0.55, 0.72, 0.28), (0.98, 0.66, 0.78), (0.36, 0.60, 0.20)]
    clear += [(x, y, 0.07) for x, y in GRAZE]
    land = cw.block(kit, size=(S_SIZE, S_SIZE), depth=DEPTH, strata=STRATA, seed=5, top=cw.rolling(amp=0.03, freq=0.9, seed=5, base=0.0),
                    season=season, keep_clear=clear, zones=_runs, tree_spots=TREES, tree_kinds=('round', 'cone'), boulders=3, flowers=1.0, sway=1.35, res=0.016)
    top_holes(kit, land, holes)
    rig = ex.cine_light(kit, land, SUN_AZ, SUN_EL, sun=7.0, sun_color=(1.0, 0.82, 0.62), fill=0.42, rim=0.5,
                        zenith=(0.16, 0.34, 0.72), horizon=(0.99, 0.80, 0.60), away=(0.52, 0.62, 0.84), ground=(0.22, 0.24, 0.22), amb=0.17)
    sd = rig['sun_dir']
    T = np.asarray(land.trees); crown = (T[0, 0], T[0, 1], ground(land, T[0, 0], T[0, 1]) + 0.5)
    shafts = ex.Shafts(kit, land, sd, beams=ex.Shafts.around(crown, 0.18, sd, 9, L=(1.2, 2.2), w=(0.03, 0.10)), canopy=7, strength=2.0, spill=0.5)
    haze_cards(kit)

    # ---- the column of homes in the -Y face (and eggs in both faces)
    eggs = ex.Eggs(kit, land); fy = eggs.faces['-Y']; fx = eggs.faces['+X']
    tunnel(eggs, '-Y', [(u, fy.top(u) + 0.02 if k == 0 else z) for k, (u, z) in enumerate(WARREN)], 0.055, 'hm_warren_run', 12)
    tunnel(eggs, '-Y', LINK_AB, 0.045, 'hm_warren_link', 6)
    chamber(eggs, CH_A[0], CH_A[1], CH_A[2], CH_A[3], 0.11, 'hm_chamber_a')
    chamber(eggs, CH_B[0], CH_B[1], CH_B[2], CH_B[3], 0.11, 'hm_chamber_b')
    straw_bed(kit, eggs, '-Y', CH_B[0], CH_B[1] - CH_B[3] * 0.78, CH_B[2] * 0.75, 70, 3, 'hm_nest_b')
    straw_bed(kit, eggs, '-Y', CH_A[0], CH_A[1] - CH_A[3] * 0.82, CH_A[2] * 0.7, 40, 4, 'hm_nest_a')
    zb = CH_B[1] - CH_B[3] * 0.80
    resting_rabbit(kit, fy, CH_B[0] + 0.035, zb, 0.042, math.pi, 'hm_doe', ph=0.4, color=(0.50, 0.40, 0.31))
    resting_rabbit(kit, fy, CH_B[0] - 0.05, zb, 0.03, 0.2, 'hm_kit1', scale=1.15, ph=1.7, color=(0.60, 0.50, 0.40))
    resting_rabbit(kit, fy, CH_B[0] - 0.012, zb - 0.002, 0.07, -0.4, 'hm_kit2', scale=1.05, ph=2.9, color=(0.46, 0.38, 0.30))
    eggs.spot('-Y', CH_B[0], CH_B[1], 2.6, out=0.42, up=0.24, size=40, side=0.05, name='hm_spot_b')
    eggs.spot('-Y', CH_A[0], CH_A[1], 2.2, out=0.42, up=0.26, size=44, side=-0.05, name='hm_spot_a')
    point_glow(kit, 'hm_glow_b', fy.world(CH_B[0], CH_B[1] + 0.02, 0.02), 0.10)
    # the two rabbits on top, and their run down the warren to chamber A
    run = [(WARREN_X, fy.top(WARREN_X) - 0.02)] + WARREN[1:]
    rabbit_runner(kit, land, fy, GRAZE[0], 2.6, run, (CH_A[0] + 0.035, CH_A[1] - CH_A[3] * 0.85 + 0.0), 0.0, 'hm_runner1', T_GO, 1.65, 0.7)
    rabbit_runner(kit, land, fy, GRAZE[1], 0.4, run, (CH_A[0] - 0.045, CH_A[1] - CH_A[3] * 0.85 + 0.0), math.pi, 'hm_runner2', T_GO + 0.18, 1.75, 2.2,
                  color=(0.58, 0.47, 0.36))
    mouth_rim(kit, land, WARREN_X, 0.052, 1, 'hm_rim_warren')
    for k, (u, z) in enumerate([WARREN[1], WARREN[3], LINK_AB[1]]): point_glow(kit, f'hm_wglow{k}', fy.world(u, z, 0.025), 0.04)
    # mole
    eggs.mole('-Y', 0.07, fy.top(0.07) - 0.095, length=0.30, r=0.034, light=2.6, size=1.45)
    # fox den with two cubs
    tunnel(eggs, '-Y', [(u, fy.top(u) + 0.02 if k == 0 else z) for k, (u, z) in enumerate(FOXT)], 0.048, 'hm_fox_run', 12)
    chamber(eggs, DEN[0], DEN[1], DEN[2], DEN[3], 0.13, 'hm_den')
    zden = DEN[1] - DEN[3] * 0.84
    straw_bed(kit, eggs, '-Y', DEN[0], zden + 0.004, DEN[2] * 0.75, 60, 6, 'hm_den_bed')
    cub(kit, fy, DEN[0] - 0.06, zden, 0.05, 0.0, 'hm_cub_sleep', sleeping=True)
    cub(kit, fy, DEN[0] + 0.07, zden, 0.04, math.pi, 'hm_cub_play')
    bone = ex.mat(kit, 'hm_bone', (0.90, 0.86, 0.76), 0.6)
    bv, bf = cw._tube([(-0.02, 0, 0), (0.02, 0, 0)], [0.003, 0.003], 6)
    eggs.obj('hm_bone', [(bv, bf, 0), (*ex.ell((-0.021, 0, 0.002), (0.004, 0.004, 0.0045)), 0), (*ex.ell((0.021, 0, 0.002), (0.004, 0.004, 0.0045)), 0)],
             [bone], '-Y', DEN[0] + 0.125, zden + 0.006, 0.06, tilt=0.2)
    eggs.spot('-Y', DEN[0], DEN[1], 3.0, out=0.45, up=0.25, size=46, side=0.06, name='hm_spot_den')
    point_glow(kit, 'hm_glow_den', fy.world(DEN[0], DEN[1] + 0.03, 0.03), 0.12)
    mouth_rim(kit, land, FOX_X, 0.046, 2, 'hm_rim_fox')
    for k, (u, z) in enumerate(FOXT[1:4]): point_glow(kit, f'hm_fglow{k}', fy.world(u, z, 0.022), 0.035)
    # ant nest: one long gallery through four chambers, the queen, eggs, a leaf store, ants walking
    tunnel(eggs, '-Y', [(u, fy.top(u) + 0.02 if k == 0 else z) for k, (u, z) in enumerate(ANTS)], 0.024, 'hm_ant_run', 26)
    for k, (u, z, a, b) in enumerate(ANT_CH): chamber(eggs, u, z, a, b, 0.07, f'hm_antch{k}')
    rng = np.random.default_rng(9); white = ex.mat(kit, 'hm_anteggs', (0.97, 0.95, 0.88), 0.5, sss=0.4); A = []
    for k in range(26):
        A.append((*ex.ell((rng.uniform(-0.035, 0.035), rng.uniform(0.006, 0.03), rng.uniform(0.0, 0.012)), (0.0034, 0.0026, 0.0024)), 0))
    u, z, a, b = ANT_CH[2]; eggs.obj('hm_ant_eggs', A, [white], '-Y', u, z - b * 0.72)
    leafs = ex.mat(kit, 'hm_leafstore', (0.40, 0.58, 0.18), 0.6, sss=0.3); A = []
    for k in range(30):
        c = np.array([rng.uniform(-0.045, 0.045), rng.uniform(0.006, 0.03), rng.uniform(0.0, 0.016)])
        v, f = ex.ell(c, (0.006, 0.004, 0.0009)); v = ex.rot_pts(v, 'y', rng.uniform(-0.6, 0.6), c); A.append((v, f, 0))
    u, z, a, b = ANT_CH[3]; eggs.obj('hm_leaf_store', A, [leafs], '-Y', u, z - b * 0.7)
    P, mats = ant_parts(kit, 'hm_queen', queen=True, leaf=False); q = ex.part(kit, 'hm_queen', P, mats); q.scale = (2.0,) * 3
    u, z, a, b = ANT_CH[0]; fy.put(q, u, z - b * 0.62, 0.015)
    def _queen(t, q=q): q.scale = (2.0, 2.0, 2.0 + 0.08 * math.sin(2 * math.pi * 0.8 * t))
    kit.on_frame(_queen)
    ant_column(kit, eggs, fy, [(u, fy.top(u) + 0.01 if k == 0 else z) for k, (u, z) in enumerate(ANTS)], 24, 0.055, 0.024, 'hm_ant', 31)
    eggs.spot('-Y', -0.10, -0.86, 5.5, out=0.5, up=0.25, size=52, side=0.0, name='hm_spot_ants')
    point_glow(kit, 'hm_glow_eggs', fy.world(ANT_CH[2][0], ANT_CH[2][1], 0.02), 0.05)
    for k, i in enumerate((1, 3, 4, 6, 8, 10)): point_glow(kit, f'hm_aglow{k}', fy.world(ANTS[i][0], ANTS[i][1], 0.012), 0.04)
    surface_ants(kit, land, [(-0.05, -0.30), (-0.25, -0.42), (-0.42, -0.62), (-0.53, -0.74), (ANT_X, -0.79)], 9, 0.05, 'hm_sant', 41)
    # deep time
    eggs.ammonite('-Y', 0.30, -1.11, R=0.05)
    eggs.trilobite('-Y', -0.36, -1.19, Lt=0.14)
    eggs.geode('-Y', 0.02, -1.29, a=0.07, b=0.058)
    eggs.hedgehog('+X', -0.38, fx.top(-0.38) - 0.15)
    eggs.amphora('+X', 0.22, -0.62)
    eggs.geode('+X', -0.10, -1.18, a=0.08, b=0.065)
    eggs.finish()
    ex.soften_roots(land)
    ex.edge_spill(kit, land, '-Y', power=55.0)
    ex.edge_spill(kit, land, '+X', power=30.0)

    # ---- life on top
    bees(kit, land, [(-0.1, -0.35), (0.25, -0.2), (-0.45, -0.15), (0.4, -0.55), (0.05, 0.15), (-0.3, -0.6), (0.55, 0.1)])
    ex.butterflies(kit, land, [(-0.15, -0.25), (0.35, -0.45), (-0.5, 0.05)])
    for i in range(3):
        ob = bpy.data.objects.get(f'ex_bfly{i}')
        if ob is not None: ob.scale = (2.0,) * 3
    ex.petals(kit, land, 24, wind=(0.05, 0.015), box=((-0.8, 0.8), (-0.8, 0.8), (0.03, 0.45)))
    motes(kit, land)
    cw.birds(kit, 3, center=(-0.6, 1.0), radius=1.4, height=1.3)
    hawk(kit, land, sd)

    ex.finish(bpy, W, H, bloom=0.2, threshold=1.3, vignette=0.24)
    cam = ex.ShotCam(kit)
    ttl = title(kit, cam, ROOT)
    cw.apply_cycles(bpy, fast=True)
    cy = bpy.context.scene.cycles
    cy.max_bounces = 4; cy.diffuse_bounces = 2; cy.glossy_bounces = 1; cy.transmission_bounces = 2; cy.transparent_max_bounces = 12
    cy.adaptive_threshold = 0.04; cy.sample_clamp_direct = 12.0
    S = {'kit': kit, 'land': land, 'cam': cam, 'eggs': eggs, 'shafts': shafts, 'title': ttl}
    return S


# =============================================================================================== shots
def shot_pose(S, name, u, t):
    """Camera for shot `name` at local progress u. Returns pos, target, lens, focus, fstop."""
    if name == 'meadow':          # low on the meadow into the morning sun; a slow descending push toward the burrow mouth
        e = ex.ease(u); az = math.radians(-62 + 5 * e); el = math.radians(8.0 + 4.0 * e); D = 1.75 - 0.30 * e
        tgt = ex.lerp((-0.22, -0.40, 0.16), (-0.27, -0.62, 0.0), e)
    elif name == 'below':         # frontal on the cut face: a slow crane down the column of homes
        e = ex.ease(u); az = math.radians(-82 + 5 * e); el = math.radians(7.0 - 2.0 * e); D = 1.62 - 0.12 * e
        tgt = np.array((-0.06 + 0.02 * e, -S_SIZE / 2, -0.30 - 0.36 * e))
    else:                         # hawk: hold on the top and the warren, then the long breath out to the whole world
        hold = ex.ease(u * 7.5 / 3.9) * 0.08; out = ex.ease5((t - 16.4) / 3.6) if t > 16.4 else 0.0
        az = math.radians(-50 - 3 * hold + 6 * out); el = math.radians(20.0 + 3.0 * out); D = 2.15 - 0.6 * hold + 1.6 * out
        tgt = ex.lerp((-0.20, -0.48, -0.14), (0.0, 0.0, -0.56), out)
    tgt = np.asarray(tgt, float)
    pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    lens = {'meadow': 42.0, 'below': 40.0, 'hawk': 35.0}[name]; fstop = {'meadow': 6.3, 'below': 7.1, 'hawk': 8.0}[name]
    return pos, tgt, lens, D, fstop


def frame(bpy, ctx, S, i, t):
    S['kit'].update(t)
    tl = ctx['timeline'].at(t); name = tl['name']
    pos, tgt, lens, focus, fstop = shot_pose(S, name, tl['u'], t)
    S['cam'].set(pos, tgt, lens, focus, fstop); S['shafts'].update(pos)
    S['shafts'].gain.default_value = SHAFT_GAIN[name]
    # title: the first 2.5 s, faded in and out; set at the focus distance so the depth of field keeps it sharp
    T = S['title']; a = smooth01(0.25, 0.85, t) * (1 - smooth01(1.85, 2.5, t)); T['alpha'].default_value = a
    ob = T['ob']
    if a > 0:
        d = focus; half = d * 18.0 / lens          # sensor fit AUTO: 36 mm spans the longer side
        half_h, half_w = (half, half * ctx['W'] / ctx['H']) if ctx['W'] < ctx['H'] else (half * ctx['H'] / ctx['W'], half)
        sc = 1.36 * half_w / T['w1']; ob.scale = (sc,) * 3; ob.location = (0.0, half_h * 0.62, -d); ob.hide_render = False
    else:
        ob.hide_render = True
