"""P07 ASH ASCENT — KINOFORGE Blender scene (bpy 5.2, Cycles CPU).

Dawn over a volcanic highland: a lone rider crosses a knife-edge ridge above a sea of cloud; the sun's limb breaks the
west flank of a far volcano on frame 91 (3.79 s), its light floods the cloud sea (the volcano's shadow wedge stays blue)
and runs onto the ridge and the rider, who halts and lifts his staff; hard cut to black (and silence) at frame 130.

Render-cost design (see NOTES.md): the cloud sea is a homogeneous Principled Volume inside a closed shell mesh whose top
is the billowed surface (numpy Worley domes), so Cycles integrates it analytically — a noise-driven heterogeneous volume
cost ~5x more per frame. Lighting rays see a node fit of the 5.2 sky; camera rays see the real sky with the sun disc.

Contract (harness/blender_render.py): SHOTS, SETTINGS, build(bpy, ctx) -> state, frame(bpy, ctx, state, i, t).
Everything at module level is pure numpy/math (no bpy) so audio.py can import the gait / timing functions.
Units: metres. +Y = along the ridge (toward the volcano and the sun), +Z up.
"""
import math
import numpy as np

FPS = 24
TOTAL = 144                      # 6.0 s
CUT = 130                        # first black frame (t = 5.4167 s)
DURATION = TOTAL / FPS
SHOTS = [{'name': 'S1 ash ascent (aerial EWS, 50 mm)', 'dur': CUT / FPS},
         {'name': 'BLACK (hard cut, silence)', 'dur': (TOTAL - CUT) / FPS}]
SETTINGS = {'samples': 64, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX',
            'look': 'AgX - Medium High Contrast', 'exposure': -3.1, 'film_transparent': False,
            'max_bounces': 2, 'volume_bounces': 0, 'clamp_indirect': 8.0}   # vb 0 + volume emission stand-in: -37 % on cloud pixels (NOTES)

# ----------------------------------------------------------------------------------------------- timing
T_CREST = 91 / 24                # first frame the sun's limb shows (camera view); SUN_ROT is solved/verified for it
T_REACT = 4.30                   # horse checks its walk as the light reaches him (rendered: first light ~3.9 s, full ~4.8 s)
T_HALT = 4.95                    # fully halted
SUN_EL0, SUN_EL1 = 2.0, 5.0      # degrees, linear over the take (brief)
SUN_ENERGY = 18.0                # W/m2: ~6x the 5.2 sky's horizontal irradiance (~3.4), a real low-sun ratio
LENS = 50.0

def smoothstep(a, b, x):
    u = np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)

def sun_elevation(t):
    return SUN_EL0 + (SUN_EL1 - SUN_EL0) * min(max(t, 0.0), CUT / FPS) / (CUT / FPS)

# ----------------------------------------------------------------------------------------------- noise (numpy)
def _perm(seed):
    p = np.random.default_rng(seed).permutation(256)
    return np.concatenate([p, p]).astype(np.int64)

_GRAD = np.array([(math.cos(a), math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
_ROT = [(math.cos(a), math.sin(a)) for a in np.radians([0, 37, 71, 113, 151, 197, 239, 281])]

def perlin(x, y, perm):
    x = np.asarray(x, float); y = np.asarray(y, float)
    xi = np.floor(x); yi = np.floor(y); xf = x - xi; yf = y - yi
    xi = xi.astype(np.int64) & 255; yi = yi.astype(np.int64) & 255
    def g(ix, iy, dx, dy):
        h = perm[perm[ix] + iy] & 15
        return _GRAD[h, 0] * dx + _GRAD[h, 1] * dy
    u = xf * xf * xf * (xf * (xf * 6 - 15) + 10); v = yf * yf * yf * (yf * (yf * 6 - 15) + 10)
    a = g(xi, yi, xf, yf); b = g(xi + 1, yi, xf - 1, yf); c = g(xi, yi + 1, xf, yf - 1); d = g(xi + 1, yi + 1, xf - 1, yf - 1)
    ab = a + u * (b - a); cd = c + u * (d - c)
    return 1.4 * (ab + v * (cd - ab))            # ~[-1, 1]

def fbm(x, y, perm, octaves=5, lac=2.03, gain=0.5):
    s = 0.0; amp = 1.0; f = 1.0; norm = 0.0
    for o in range(octaves):
        c, sn = _ROT[o % 8]
        s = s + amp * perlin((x * c - y * sn) * f + 13.7 * o, (x * sn + y * c) * f + 7.3 * o, perm)
        norm += amp; amp *= gain; f *= lac
    return s / norm

def ridged(x, y, perm, octaves=4, lac=2.1, gain=0.55):
    s = 0.0; amp = 1.0; f = 1.0; norm = 0.0
    for o in range(octaves):
        c, sn = _ROT[(o + 3) % 8]
        n = 1.0 - np.abs(perlin((x * c - y * sn) * f + 5.1 * o, (x * sn + y * c) * f + 11.9 * o, perm))
        s = s + amp * n * n; norm += amp; amp *= gain; f *= lac
    return s / norm                               # [0, 1], sharp crests at 1

P_A, P_B, P_C, P_D = _perm(11), _perm(23), _perm(37), _perm(53)

# ----------------------------------------------------------------------------------------------- the ridge
def crest_x(y):
    """Crest line; the local jog at y~5 turns the riding line ~25 deg across the camera's view (3/4 rear, not dead-on)."""
    y = np.asarray(y, float)
    return 10.0 * np.sin((y - 60.0) / 190.0) + 4.0 * np.sin(y / 61.0 + 1.3) + 9.0 * np.tanh((y - 5.0) / 18.0)

def crest_z(y):
    """The spine descends gently past the rider and tapers into the cloud sea toward the volcano (~y 1000)."""
    y = np.asarray(y, float)
    z = -0.07 * y - 0.00013 * y * np.abs(y) * (y > 0)
    z = z + 1.4 * np.sin(y / 43.0) + 0.7 * np.sin(y / 19.0 + 0.7) + 2.2 * np.sin(y / 71.0 + 2.2)
    z = z - np.where(y < -260.0, 0.004 * (y + 260.0) ** 2, 0.0)          # falls away behind the camera
    return z

# gendarmes / tors: (y, v, height, radius) — towers on or beside the crest give the rider a scale; none on his path
_TORS = [(-150, 6.5, 5.0, 5.0), (-70, -7.0, 4.0, 4.0), (52, 6.5, 4.5, 4.0), (142, 0.0, 6.5, 4.5), (215, -6.0, 5.0, 4.0),
         (300, 0.5, 9.5, 6.0), (395, 5.5, 6.0, 5.0), (520, -0.5, 12.0, 7.5), (640, 4.0, 7.0, 6.0), (760, 0.0, 9.0, 7.0)]

def _gullies(y, av):
    """Anisotropic ridged noise: channels and spurs that run down the fall line (across the ridge)."""
    s = 0.0; amp = 1.0; norm = 0.0
    for o, (fy, fv) in enumerate([(1 / 26.0, 1 / 150.0), (1 / 12.0, 1 / 60.0), (1 / 5.5, 1 / 25.0)]):
        n = 1.0 - np.abs(perlin(y * fy + 3.1 * o, av * fv + 1.7 * o, P_A))
        s = s + amp * n * n; norm += amp; amp *= 0.5
    return s / norm

def ridge_height(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    v = x - crest_x(y); av = np.abs(v)
    w = 1.6                                                                # crest rounding (m)
    k = np.where(v > 0, 1.18, 1.06) + 0.18 * fbm(y / 110.0, 3.7 + 0 * y, P_B, 3)      # ~47-50 deg flanks
    z = crest_z(y) - k * (np.sqrt(av * av + w * w) - w) - 0.0016 * np.maximum(av - 20.0, 0.0) ** 2
    m = smoothstep(1.5, 10.0, av)                                          # keep the riding line clean
    z = z + m * np.minimum(av, 140.0) * 0.42 * (_gullies(y, av) - 0.55)
    z = z + m * 4.0 * fbm(x / 40.0, y / 40.0, P_B, 5)                      # buttress-scale lumps
    z = z + m * 1.2 * fbm(x / 9.0, y / 9.0, P_C, 4)                        # rock steps
    z = z + 0.22 * fbm(x / 3.0, y / 3.0, P_D, 2)                           # texture everywhere (riding line too)
    for (ty, tv, th, tr) in _TORS:
        tx = crest_x(ty) + tv
        d2 = ((x - tx) ** 2 + (y - ty) ** 2) / (tr * tr)
        z = z + th * np.exp(-d2 * d2) * (0.6 + 0.4 * fbm(x / 2.5, y / 2.5, P_D, 3))
    return z

# ----------------------------------------------------------------------------------------------- islands / volcano
# islands rising out of the cloud sea (cx, cy, height of top z, radius, elongation dir deg, aspect, seed)
ISLANDS = [(-820.0, 1250.0, -95.0, 260.0, 35.0, 2.4, 61),
           (-260.0, 2350.0, -150.0, 180.0, -20.0, 1.6, 67),
           (760.0, 1650.0, -135.0, 150.0, 10.0, 1.3, 71),
           (1500.0, 3900.0, -60.0, 420.0, -10.0, 2.0, 73),
           (-2100.0, 4300.0, -40.0, 520.0, 25.0, 2.2, 79)]

def island_height(x, y, isl):
    cx, cy, top, r, ang, asp, seed = isl
    p = _perm(seed); a = math.radians(ang)
    dx = x - cx; dy = y - cy
    u = (dx * math.cos(a) + dy * math.sin(a)) / (r * asp); v = (-dx * math.sin(a) + dy * math.cos(a)) / r
    d = np.sqrt(u * u + v * v)
    base = -260.0
    shape = np.clip(1.0 - d, 0.0, None) ** 1.35
    z = base + (top - base) * shape * (0.72 + 0.28 * ridged(x / (r * 0.35), y / (r * 0.35), p, 4))
    return z + 6.0 * fbm(x / 35.0, y / 35.0, p, 4) * (shape > 0)

VOLC = (420.0, 11800.0)          # far volcano centre (x, y)
VOLC_TOP = 1180.0

def volcano_height(x, y):
    """Steep (~40 deg) cone with a rounded summit, crater notch, radial gullies and a small west parasitic cone."""
    cx, cy = VOLC
    dx = np.asarray(x, float) - cx; dy = np.asarray(y, float) - cy; r = np.sqrt(dx * dx + dy * dy)
    rk = np.minimum(np.sqrt(r * r + 120.0 ** 2) - 120.0, 4300.0) / 1000.0
    z = VOLC_TOP - 1000.0 * (1.05 * rk - 0.12 * rk * rk)                 # ~46 deg at the summit, ~34 deg at the cloud line
    z = np.maximum(z, 610.0 - 0.80 * np.sqrt((dx + 1150.0) ** 2 + (dy * 1.3) ** 2))
    z = z - 48.0 * np.exp(-(r / 190.0) ** 2)
    ang = np.arctan2(dx, -dy)                                   # 0 = facing the camera; the +-pi seam is on the hidden far side
    gul = ridged(ang * 10.0, r / 700.0, P_D, 4)
    z = z + (gul - 0.5) * np.clip(r / 900.0, 0, 1) * 70.0
    z = z + 45.0 * fbm(ang * 2.2, r / 1400.0, P_B, 3) * np.clip(r / 500.0, 0, 1)     # irregular flanks: no perfect cone
    z = z + 34.0 * np.clip(dx / 260.0, -1, 1) * np.exp(-(r / 330.0) ** 2)           # broken crater rim: east lip higher
    return z

# ----------------------------------------------------------------------------------------------- cloud sea (top surface)
def _hash01(ix, iy, seed):
    h = (ix.astype(np.uint64) * np.uint64(0x9E3779B1)) ^ (iy.astype(np.uint64) * np.uint64(0x85EBCA77)) ^ np.uint64(seed * 0x27D4EB2F)
    h = h ^ (h >> np.uint64(15)); h = h * np.uint64(0x2C1B3C6D); h = h ^ (h >> np.uint64(12)); h = h * np.uint64(0x297A2D39); h = h ^ (h >> np.uint64(15))
    return (h & np.uint64(0xFFFFFF)).astype(np.float64) / float(0x1000000)

def worley_f1(x, y, cell, seed):
    gx = np.asarray(x, float) / cell; gy = np.asarray(y, float) / cell
    ix = np.floor(gx).astype(np.int64); iy = np.floor(gy).astype(np.int64)
    best = np.full(gx.shape, 1e9)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx = ix + dx; cy = iy + dy
            px = cx + 0.12 + 0.76 * _hash01(cx, cy, seed); py = cy + 0.12 + 0.76 * _hash01(cx, cy, seed + 7)
            best = np.minimum(best, (gx - px) ** 2 + (gy - py) ** 2)
    return np.sqrt(best)

CLOUD_BASE = -214.0
P_CL = _perm(91)

EARTH_R = 6.371e6
CAM_REF = (55.0, -265.0)          # mid-take camera ground position: curvature is measured from here

def curvature_drop(x, y):
    """The deck falls away with the Earth's curvature, so the cloud horizon sits ~0.5 deg below the sky horizon."""
    return ((np.asarray(x, float) - CAM_REF[0]) ** 2 + (np.asarray(y, float) - CAM_REF[1]) ** 2) / (2.0 * EARTH_R)

def cloud_top(x, y, cam_y=-330.0):
    """Billowed top of the cloud sea (m): multi-scale rounded domes on a slow swell; billows flatten far away
    (sub-pixel: no swim, cheaper rays); the deck follows the Earth's curvature."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    far = 1.0 - smoothstep(5000.0, 12000.0, y - cam_y)
    z = CLOUD_BASE + 16.0 * fbm(x / 800.0, y / 800.0, P_CL, 3) - curvature_drop(x, y)
    for cell, amp, seed in [(150.0, 34.0, 3), (58.0, 12.0, 5), (22.0, 4.0, 9)]:
        f = np.clip(worley_f1(x, y, cell, seed) / 0.78, 0.0, 1.0)
        z = z + far * amp * (1.0 - f * f) ** 0.65
    return z

# ----------------------------------------------------------------------------------------------- rider path / gait
SPEED = 1.55                     # m/s walk
STRIDE = 1.70                    # m per stride
Y0 = 0.0                         # rider's start position along the ridge

def _speed(t):
    return SPEED * (1.0 - smoothstep(T_REACT, T_HALT, t))

_TT = np.arange(0.0, DURATION + 0.05, 1.0 / 480.0)
_DIST = np.concatenate([[0.0], np.cumsum(0.5 * (_speed(_TT[1:]) + _speed(_TT[:-1])) * np.diff(_TT))])

def rider_dist(t):
    return float(np.interp(t, _TT, _DIST))

def rider_root(t):
    """Position on the crest + heading (rad, 0 = +Y) + pitch (rad) of the ridge line at the rider."""
    y = Y0 + rider_dist(t)
    x = float(crest_x(y)); z = float(ridge_height(x, y))
    y2 = y + 1.2; x2 = float(crest_x(y2)); z2 = float(ridge_height(x2, y2))
    y1 = y - 1.2; x1 = float(crest_x(y1)); z1 = float(ridge_height(x1, y1))
    head = math.atan2(x2 - x1, y2 - y1); pitch = math.atan2(z2 - z1, math.hypot(x2 - x1, y2 - y1))
    return np.array([x, y, z]), head, pitch

# lateral-sequence walk: LH, LF, RH, RF; duty factor 0.62
LEGS = [('LH', -0.16, -0.60, 0.00), ('LF', -0.16, 0.58, 0.25), ('RH', 0.16, -0.60, 0.50), ('RF', 0.16, 0.58, 0.75)]
DUTY = 0.62

def gait_phase(t):
    return rider_dist(t) / STRIDE

def hoof_local(t, leg):
    """Hoof position in the horse frame (x right, y fwd, z up) relative to the hip's ground point, + lift."""
    name, hx, hy, off = leg
    ph = gait_phase(t) - off
    q = ph - math.floor(ph)
    if q < DUTY:                                            # stance: hoof slides back relative to the body
        s = 0.31 * STRIDE * (1.0 - 2.0 * q / DUTY); lift = 0.0
    else:                                                   # swing: forward with an arc
        w = (q - DUTY) / (1.0 - DUTY); e = w * w * (3 - 2 * w)
        s = 0.31 * STRIDE * (-1.0 + 2.0 * e); lift = 0.16 * math.sin(math.pi * w) ** 1.2
    stand = smoothstep(T_REACT + 0.1, T_HALT, t)            # square up for the halt
    s = float((1 - stand) * s + stand * (0.05 if hy > 0 else -0.04)); lift = float(lift * (1 - stand))
    return s, lift

def hoof_plants(t0=0.0, t1=CUT / FPS):
    """Times (s) of every hoof plant (swing -> stance) — used by audio.py for the faint thuds."""
    out = []
    tt = np.arange(t0, t1, 1.0 / 480.0)
    for leg in LEGS:
        prev = None
        for t in tt:
            if t > T_REACT + 0.25: break
            ph = gait_phase(t) - leg[3]; q = ph - math.floor(ph)
            st = q < DUTY
            if prev is False and st: out.append((round(float(t), 4), leg[0]))
            prev = st
    return sorted(out)

# ----------------------------------------------------------------------------------------------- camera path
CAM_BACK0, CAM_BACK1 = 330.0, 205.0     # metres behind the rider along -Y
CAM_SIDE = 0.20                         # lateral offset (fraction of back) to the right (+X)
CAM_DEP0, CAM_DEP1 = 8.7, 8.4           # depression angle to the rider (deg)
FRAME_X, FRAME_Y = 0.36, 0.22           # where the rider sits in frame (0..1 from left / bottom)
BANK = 3.0                              # degrees of roll over the move

def _hermite(u, m0=1.35, m1=0.12):
    u = min(max(u, 0.0), 1.0)
    return (u ** 3 - 2 * u * u + u) * m0 + (-2 * u ** 3 + 3 * u * u) + (u ** 3 - u * u) * m1

def camera_pose(t, W=1280, H=720):
    """-> (location xyz, yaw, pitch, roll) in radians; yaw 0 = looking +Y, positive = toward -X (Blender Z rot)."""
    u = _hermite(min(t, CUT / FPS) / (CUT / FPS))
    back = CAM_BACK0 + (CAM_BACK1 - CAM_BACK0) * u
    dep = math.radians(CAM_DEP0 + (CAM_DEP1 - CAM_DEP0) * u)
    rp, _, _ = rider_root(t)
    aim = rp + np.array([0.0, 0.0, 1.2])                  # the rider's body, not the bobbing silhouette
    horiz = math.hypot(back, back * CAM_SIDE)
    loc = np.array([rp[0] + back * CAM_SIDE, rp[1] - back, aim[2] + horiz * math.tan(dep)])
    d = aim - loc
    bearing = math.atan2(d[0], d[1])                      # + toward +X
    elev = math.atan2(d[2], math.hypot(d[0], d[1]))
    sw = 36.0; sh = sw * H / W
    tx = math.atan((2 * FRAME_X - 1) * (sw / 2) / LENS); ty = math.atan((2 * FRAME_Y - 1) * (sh / 2) / LENS)
    yaw = -(bearing - tx)                                  # Blender: +Z rotation turns left (toward -X)
    pitch = elev - ty
    roll = math.radians(BANK) * float(smoothstep(0.4, 5.2, t))
    return loc, yaw, pitch, roll

# ----------------------------------------------------------------------------------------------- bpy helpers
def _mesh_from_grid(bpy, name, X, Y, Z):
    nu, nv = Z.shape
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).astype(np.float64)
    idx = np.arange(nu * nv).reshape(nu, nv)
    quads = np.stack([idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()], 1)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], quads)
    me.shade_smooth()
    me.update()
    return me

def _obj(bpy, name, me, mat=None, parent=None):
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat is not None: me.materials.append(mat)
    if parent is not None: ob.parent = parent
    return ob

def _capsule(bpy, name, r, half_len, seg=12, rings=8, axis='Y'):
    """Capsule along +axis centred at origin: total length 2*half_len + 2r."""
    verts = []; faces = []
    for i in range(rings + 1):
        th = math.pi * i / rings
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            x = r * math.sin(th) * math.cos(ph); z = r * math.sin(th) * math.sin(ph); y = r * math.cos(th)
            y += half_len if i <= rings // 2 else -half_len
            verts.append((x, y, z))
    for i in range(rings):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg; c = (i + 1) * seg + (j + 1) % seg; d = (i + 1) * seg + j
            faces.append((a, d, c, b))
    if axis == 'Z': verts = [(x, -z, y) for (x, y, z) in verts]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.shade_smooth(); me.update()
    return me

def _cylinder(bpy, name, r0, r1, seg=10):
    """Unit-length tapered cylinder along +Z from z=0 to z=1 (scale z for length)."""
    verts = []; faces = []
    for j in range(seg):
        a = 2 * math.pi * j / seg
        verts.append((r0 * math.cos(a), r0 * math.sin(a), 0.0)); verts.append((r1 * math.cos(a), r1 * math.sin(a), 1.0))
    for j in range(seg):
        k = (j + 1) % seg
        faces.append((2 * j, 2 * k, 2 * k + 1, 2 * j + 1))
    faces.append(tuple(2 * j for j in reversed(range(seg)))); faces.append(tuple(2 * j + 1 for j in range(seg)))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.shade_smooth(); me.update()
    return me

def _nodes(mat):
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    return nt.nodes, nt.links

def _math(N, L, op, a=None, b=None, clamp=False, va=None, vb=None):
    m = N.new('ShaderNodeMath'); m.operation = op; m.use_clamp = clamp
    if a is not None: L.new(a, m.inputs[0])
    elif va is not None: m.inputs[0].default_value = va
    if b is not None: L.new(b, m.inputs[1])
    elif vb is not None: m.inputs[1].default_value = vb
    return m.outputs[0]

SKY_TYPE = 'MULTIPLE_SCATTERING'   # 5.2: the Nishita model is 'SINGLE_SCATTERING'; multiple scattering reads as real dawn

def _sky_node(N, sky_nodes, disc=False):
    s = N.new('ShaderNodeTexSky'); s.sky_type = SKY_TYPE; s.sun_disc = disc
    s.sun_size = math.radians(0.5); s.altitude = 3000.0; s.air_density = 1.0; s.aerosol_density = 1.0; s.ozone_density = 1.0
    sky_nodes.append(s)
    return s

HAZE_COOL = (4.6, 5.6, 6.8)       # linear horizon-haze colours sampled from the sky at the key frame
HAZE_WARM = (4.6, 5.6, 6.8)       # terrain is backlit: the air in front of it is in its own shadow -> cool haze only

# horizon-weighted sky radiance at azimuth 90 deg from the sun (sun el 3.5 deg), by elevation (deg) — sampled from 5.2's sky
_SKY_EL = [(0, (4.2, 4.2, 3.0)), (1, (3.96, 4.12, 3.15)), (5, (2.06, 3.0, 3.55)), (10, (1.21, 2.04, 3.05)), (20, (0.63, 1.17, 2.07)),
           (35, (0.38, 0.74, 1.41)), (60, (0.26, 0.51, 1.0)), (90, (0.22, 0.44, 0.89))]
# azimuthal gain by cos(angle to the sun's azimuth): forward glow and the anti-sun belt
_SKY_AZ = [(-1.0, (1.9, 1.9, 1.85)), (0.0, (1.0, 1.0, 1.0)), (0.866, (1.85, 1.75, 1.6)), (1.0, (2.6, 2.4, 2.1))]
# horizontal-irradiance ratio vs 3.5 deg, per sun elevation (from the same equirects)
_SKY_GAIN = [(2.0, (0.85, 0.77, 0.72)), (3.5, (1.0, 1.0, 1.0)), (5.0, (1.13, 1.20, 1.26))]

def sky_gain(el):
    xs = [e for e, _ in _SKY_GAIN]
    return tuple(float(np.interp(el, xs, [c[k] for _, c in _SKY_GAIN])) for k in range(3))

def _ramp(N, stops, scale):
    r = N.new('ShaderNodeValToRGB'); els = r.color_ramp.elements
    while len(els) < len(stops): els.new(0.5)
    for e, (pos, col) in zip(els, stops):
        e.position = pos; e.color = (col[0] / scale, col[1] / scale, col[2] / scale, 1.0)
    return r

def _sky_fit(N, L):
    tc = N.new('ShaderNodeTexCoord')
    nrm = N.new('ShaderNodeVectorMath'); nrm.operation = 'NORMALIZE'; L.new(tc.outputs['Generated'], nrm.inputs[0])
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(nrm.outputs[0], sep.inputs[0])
    el = _math(N, L, 'ARCSINE', _math(N, L, 'MAXIMUM', sep.outputs[2], vb=0.0))
    elu = _math(N, L, 'MULTIPLY', el, vb=2.0 / math.pi)                       # 0 at horizon .. 1 at zenith
    base = _ramp(N, [(e / 90.0, c) for e, c in _SKY_EL], 5.0); L.new(elu, base.inputs[0])
    comb = N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs[0], comb.inputs[0]); L.new(sep.outputs[1], comb.inputs[1])
    hn = N.new('ShaderNodeVectorMath'); hn.operation = 'NORMALIZE'; L.new(comb.outputs[0], hn.inputs[0])
    dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; L.new(hn.outputs[0], dot.inputs[0])
    a = math.radians(SUN_ROT); dot.inputs[1].default_value = (math.sin(a), math.cos(a), 0.0)
    cu = _math(N, L, 'MULTIPLY_ADD', dot.outputs['Value'], vb=0.5); cu.node.inputs[2].default_value = 0.5
    az = _ramp(N, [((c + 1) / 2, g) for c, g in _SKY_AZ], 3.0); L.new(cu, az.inputs[0])
    fade = _math(N, L, 'EXPONENT', _math(N, L, 'MULTIPLY', elu, vb=-3.2))                 # azimuth effect fades upward
    # M = 1 + (3*az - 1) * fade
    az3 = N.new('ShaderNodeVectorMath'); az3.operation = 'MULTIPLY_ADD'; L.new(az.outputs[0], az3.inputs[0])
    az3.inputs[1].default_value = (3.0, 3.0, 3.0); az3.inputs[2].default_value = (-1.0, -1.0, -1.0)
    m = N.new('ShaderNodeVectorMath'); m.operation = 'MULTIPLY_ADD'; L.new(az3.outputs[0], m.inputs[0]); L.new(fade, m.inputs[1])
    m.inputs[2].default_value = (1.0, 1.0, 1.0)
    col = N.new('ShaderNodeVectorMath'); col.operation = 'MULTIPLY'; L.new(base.outputs[0], col.inputs[0]); L.new(m.outputs[0], col.inputs[1])
    gain = N.new('ShaderNodeVectorMath'); gain.operation = 'MULTIPLY'; L.new(col.outputs[0], gain.inputs[0])
    gain.inputs[1].default_value = (5.0, 5.0, 5.0)
    return gain.outputs[0], gain.inputs[1]

DECK_HAZE_COOL = (3.96, 4.12, 3.15)   # horizon sky radiance (el ~1 deg) 90 deg from the sun / toward the sun
DECK_HAZE_WARM = (11.3, 10.4, 6.2)

def _haze(N, L, shader_out, dist_scale=40000.0, strength=1.0, start=0.0, cool=None, warm=None, sharp=10.0, base=None):
    """Aerial perspective: mix the surface toward a horizon-haze colour (warm toward the sun's azimuth) by distance.
    Static (no per-frame update -> no shader recompiles); emission sampling is disabled on these materials."""
    cam = N.new('ShaderNodeCameraData'); geo = N.new('ShaderNodeNewGeometry')
    neg = N.new('ShaderNodeVectorMath'); neg.operation = 'SCALE'; neg.inputs['Scale'].default_value = -1.0
    L.new(geo.outputs['Incoming'], neg.inputs[0])
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(neg.outputs[0], sep.inputs[0])
    comb = N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs[0], comb.inputs[0]); L.new(sep.outputs[1], comb.inputs[1])
    nrm = N.new('ShaderNodeVectorMath'); nrm.operation = 'NORMALIZE'; L.new(comb.outputs[0], nrm.inputs[0])
    dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; L.new(nrm.outputs[0], dot.inputs[0])
    a = math.radians(SUN_ROT); dot.inputs[1].default_value = (math.sin(a), math.cos(a), 0.0)
    w = _math(N, L, 'POWER', _math(N, L, 'MAXIMUM', dot.outputs['Value'], vb=0.0), vb=sharp)
    col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'; L.new(w, col.inputs['Factor'])
    col.inputs['A'].default_value = (*(cool or HAZE_COOL), 1); col.inputs['B'].default_value = (*(warm or HAZE_WARM), 1)
    em = N.new('ShaderNodeEmission'); L.new(col.outputs['Result'], em.inputs['Color']); em.inputs['Strength'].default_value = strength
    dist = _math(N, L, 'MAXIMUM', _math(N, L, 'SUBTRACT', cam.outputs['View Distance'], vb=start), vb=0.0)
    f = _math(N, L, 'DIVIDE', dist, vb=-dist_scale)
    f = _math(N, L, 'EXPONENT', f)
    f = _math(N, L, 'SUBTRACT', None, f, va=1.0)
    if base is not None:                                     # thicker haze low down (near the cloud deck)
        z0, z1, amt = base
        sp = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sp.inputs[0])
        mr = N.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; L.new(sp.outputs[2], mr.inputs['Value'])
        mr.inputs['From Min'].default_value = z0; mr.inputs['From Max'].default_value = z1
        mr.inputs['To Min'].default_value = amt; mr.inputs['To Max'].default_value = 0.0
        f = _math(N, L, 'ADD', f, mr.outputs['Result'], clamp=True)
    mix = N.new('ShaderNodeMixShader'); L.new(f, mix.inputs[0]); L.new(shader_out, mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    return mix.outputs[0]

def _rock_material(bpy, name, dist_scale, ash=True, haze_strength=1.0, bump=True, base_haze=None):
    mat = bpy.data.materials.new(name); N, L = _nodes(mat)
    out = N.new('ShaderNodeOutputMaterial')
    bs = N.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value = 0.9
    geo = N.new('ShaderNodeNewGeometry')
    # basalt base colour: near-black <-> warm dark grey, by noise
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.11; n1.inputs['Detail'].default_value = 3
    n1.inputs['Roughness'].default_value = 0.62; L.new(geo.outputs['Position'], n1.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); L.new(n1.outputs['Fac'], cr.inputs[0])
    cr.color_ramp.elements[0].position = 0.38; cr.color_ramp.elements[0].color = (0.016, 0.015, 0.016, 1)
    cr.color_ramp.elements[1].position = 0.70; cr.color_ramp.elements[1].color = (0.075, 0.066, 0.058, 1)
    col = cr.outputs[0]
    if ash:
        # pale ash on upward-facing ground (Geometry normal z), patchy
        sepn = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], sepn.inputs[0])
        n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 0.06; n2.inputs['Detail'].default_value = 1
        L.new(geo.outputs['Position'], n2.inputs['Vector'])
        up = _math(N, L, 'ADD', sepn.outputs[2], _math(N, L, 'MULTIPLY', n2.outputs['Fac'], vb=0.10))
        ar = N.new('ShaderNodeValToRGB'); L.new(up, ar.inputs[0])
        ar.color_ramp.elements[0].position = 0.955; ar.color_ramp.elements[0].color = (0, 0, 0, 1)
        ar.color_ramp.elements[1].position = 1.04; ar.color_ramp.elements[1].color = (1, 1, 1, 1)
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(ar.outputs[0], mx.inputs['Factor'])
        L.new(col, mx.inputs['A']); mx.inputs['B'].default_value = (0.30, 0.28, 0.26, 1)
        col = mx.outputs['Result']
    L.new(col, bs.inputs['Base Color'])
    # rock bump
    if bump:
        n3 = N.new('ShaderNodeTexNoise'); n3.inputs['Scale'].default_value = 0.9; n3.inputs['Detail'].default_value = 2
        L.new(geo.outputs['Position'], n3.inputs['Vector'])
        bmp = N.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.45; bmp.inputs['Distance'].default_value = 0.25
        L.new(n3.outputs['Fac'], bmp.inputs['Height']); L.new(bmp.outputs['Normal'], bs.inputs['Normal'])
    sh = _haze(N, L, bs.outputs[0], dist_scale, haze_strength, base=base_haze)
    L.new(sh, out.inputs['Surface'])
    mat.cycles.emission_sampling = 'NONE'
    return mat

def _cloud_volume_material(bpy, name):
    mat = bpy.data.materials.new(name); N, L = _nodes(mat)
    out = N.new('ShaderNodeOutputMaterial')
    pv = N.new('ShaderNodeVolumePrincipled'); pv.inputs['Anisotropy'].default_value = 0.3
    pv.inputs['Color'].default_value = (0.93, 0.95, 1.0, 1); pv.inputs['Density'].default_value = 0.05
    for nm in ('Density Attribute', 'Color Attribute', 'Temperature Attribute'):
        pv.inputs[nm].default_value = ''           # no attribute dependency -> Cycles treats the medium as homogeneous
    pv.inputs['Blackbody Intensity'].default_value = 0.0
    # single scattering (volume_bounces 0) + a faint constant sky-blue emission standing in for multiple scattering;
    # constant -> the medium stays homogeneous (analytic, no ray-marching)
    pv.inputs['Emission Strength'].default_value = 0.008; pv.inputs['Emission Color'].default_value = (0.55, 0.72, 1.0, 1)
    L.new(pv.outputs[0], out.inputs['Volume'])
    return mat

SHELL_END = 13600.0                # volumetric cloud sea ends behind the volcano; a hazed surface deck carries it to the horizon

def _far_deck(bpy):
    """Opaque continuation of the cloud deck from SHELL_END to 150 km (same surface function, curvature, haze)."""
    y_cam = -330.0
    ys = [SHELL_END - 200.0]
    while ys[-1] < 150000.0:
        ys.append(ys[-1] + 0.02 * (ys[-1] - y_cam))
    ys = np.array(ys); nv = 120; d = ys - y_cam
    xl = 60.0 - d * math.tan(math.radians(36.0)) - 400.0; xr = 60.0 + d * math.tan(math.radians(25.0)) + 400.0
    tj = np.linspace(0.0, 1.0, nv)
    X = xl[:, None] + (xr - xl)[:, None] * tj[None, :]; Y = np.repeat(ys[:, None], nv, 1)
    return _mesh_from_grid(bpy, 'KF_FarDeck', X, Y, cloud_top(X, Y, y_cam))

def _cloud_shell(bpy):
    """Closed mesh: camera-frustum-shaped heightfield top (cloud_top) + side walls + flat bottom (outward normals)."""
    y_cam = -330.0
    ys = [-120.0]
    while ys[-1] < SHELL_END:
        d = ys[-1] - y_cam
        ys.append(min(SHELL_END, ys[-1] + max(5.0, 0.0105 * d)))
    ys = np.array(ys); nv = 250
    d = ys - y_cam
    xl = 60.0 - d * math.tan(math.radians(33.0)) - 250.0; xr = 60.0 + d * math.tan(math.radians(22.0)) + 250.0
    tj = np.linspace(0.0, 1.0, nv)
    X = xl[:, None] + (xr - xl)[:, None] * tj[None, :]; Y = np.repeat(ys[:, None], nv, 1)
    Z = cloud_top(X, Y, y_cam)
    nu = len(ys); zb = -420.0
    top = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    idx = np.arange(nu * nv).reshape(nu, nv)
    quads = np.stack([idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()], 1).tolist()
    per = list(idx[0, :]) + list(idx[1:, -1]) + list(idx[-1, -2::-1]) + list(idx[-2:0:-1, 0])   # CCW seen from above
    nb = len(top); bot = top[per].copy(); bot[:, 2] = zb
    verts = np.concatenate([top, bot], 0)
    n = len(per)
    for k in range(n):
        a, b = per[k], per[(k + 1) % n]; ab, bb = nb + k, nb + (k + 1) % n
        quads.append([a, ab, bb, b])
    faces = quads + [list(range(nb + n - 1, nb - 1, -1))]
    me = bpy.data.meshes.new('KF_CloudShell'); me.from_pydata(verts, [], faces); me.shade_smooth(); me.update()
    return me

def _dark_material(bpy, name, col, sheen=0.7, rough=0.55):
    mat = bpy.data.materials.new(name); N, L = _nodes(mat)
    out = N.new('ShaderNodeOutputMaterial'); bs = N.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (*col, 1); bs.inputs['Roughness'].default_value = rough
    bs.inputs['Sheen Weight'].default_value = sheen; bs.inputs['Sheen Roughness'].default_value = 0.35
    bs.inputs['Sheen Tint'].default_value = (1.0, 0.8, 0.6, 1)
    L.new(bs.outputs[0], out.inputs['Surface'])
    return mat

def _axis_coords(c0, c1, center_lo, center_hi, fine, growth):
    """1-D coordinates from c0 to c1, spacing `fine` inside [center_lo, center_hi], growing linearly outside."""
    def sp(c):
        if c < center_lo: return fine + growth * (center_lo - c)
        if c > center_hi: return fine + growth * (c - center_hi)
        return fine
    out = [c0]; c = c0
    while c < c1:
        c = c + sp(c); out.append(min(c, c1))
    return np.array(out)

# ----------------------------------------------------------------------------------------------- build
def build(bpy, ctx):
    from mathutils import Vector, Matrix, Euler, Quaternion
    sc = bpy.context.scene
    sc.render.use_persistent_data = True
    cy = sc.cycles
    cy.volume_biased = True; cy.volume_step_rate = 2.0; cy.volume_max_steps = 128      # brief: ray-marched, step rate 2.0
    cy.adaptive_threshold = 0.12; cy.adaptive_min_samples = 8                          # OIDN cleans the rest
    cy.denoising_prefilter = 'FAST'                     # 'ACCURATE' re-denoises albedo/normal: ~13 CPU-s per 720p frame
    cy.use_volume_guiding = False; cy.use_light_tree = False           # two lights only: the tree costs ~11 %
    cy.debug_use_spatial_splits = True                                 # better BVH for the long thin far cloud-shell tris (~-5 %)
    cy.caustics_reflective = False; cy.caustics_refractive = False
    cy.diffuse_bounces = 0; cy.glossy_bounces = 0; cy.transmission_bounces = 0; cy.transparent_max_bounces = 2   # basalt albedo <= 0.07: indirect is invisible but each bounce can enter the cloud volume
    sky_nodes = []

    # --- world: camera rays see the physical 5.2 sky (with the sun disc); every other ray sees a cheap node fit of the
    #     same sky without the disc (the Sun lamp is the key). The fit was sampled from an equirect of MULTIPLE_SCATTERING.
    w = bpy.data.worlds.new('KF_World'); sc.world = w
    N, L = _nodes(w)
    wo = N.new('ShaderNodeOutputWorld'); bg = N.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 1.0
    s_cam = _sky_node(N, sky_nodes, disc=True)
    fit, sky_gain = _sky_fit(N, L)
    # camera rays: the real sky above the horizon; below it (where the curved cloud deck falls away) the fit's
    # horizon radiance, i.e. the glowing horizon haze — 5.2's sky shows a dark 'ground' there instead
    tcw = N.new('ShaderNodeTexCoord'); nw = N.new('ShaderNodeVectorMath'); nw.operation = 'NORMALIZE'; L.new(tcw.outputs['Generated'], nw.inputs[0])
    sepw = N.new('ShaderNodeSeparateXYZ'); L.new(nw.outputs[0], sepw.inputs[0])
    above = N.new('ShaderNodeMapRange'); above.interpolation_type = 'SMOOTHSTEP'; L.new(sepw.outputs[2], above.inputs['Value'])
    above.inputs['From Min'].default_value = -0.0035; above.inputs['From Max'].default_value = 0.0035
    lp = N.new('ShaderNodeLightPath')
    fac = _math(N, L, 'MULTIPLY', lp.outputs['Is Camera Ray'], above.outputs['Result'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    L.new(fac, mx.inputs['Factor']); L.new(fit, mx.inputs['A']); L.new(s_cam.outputs[0], mx.inputs['B'])
    L.new(mx.outputs['Result'], bg.inputs['Color']); L.new(bg.outputs[0], wo.inputs['Surface'])

    # --- sun lamp (direction set per frame)
    ld = bpy.data.lights.new('KF_Sun', 'SUN'); ld.energy = SUN_ENERGY; ld.angle = math.radians(0.5); ld.color = (1.0, 0.64, 0.40)
    sun = bpy.data.objects.new('KF_Sun', ld); sc.collection.objects.link(sun); sun.rotation_mode = 'QUATERNION'

    # --- terrain: sheared, variable-resolution grid that follows the crest line
    rock = _rock_material(bpy, 'KF_Basalt', dist_scale=150000.0)
    isl_m = _rock_material(bpy, 'KF_IslandRock', dist_scale=38000.0, bump=False, base_haze=(-200.0, -90.0, 0.08))
    ys = _axis_coords(-520.0, 1000.0, -170.0, 110.0, 0.62, 0.0060)
    vh = _axis_coords(0.0, 330.0, -1.0, 5.0, 0.4, 0.040)
    vs = np.concatenate([-vh[::-1][:-1], vh])
    Yg, Vg = np.meshgrid(ys, vs, indexing='ij')
    Xg = Vg + crest_x(Yg)
    Zg = ridge_height(Xg, Yg)
    terr = _obj(bpy, 'KF_Ridge', _mesh_from_grid(bpy, 'KF_Ridge', Xg, Yg, Zg), rock)

    # islands (coarser grids)
    for k, isl in enumerate(ISLANDS):
        cx, cy_, top, r, ang, asp, seed = isl
        R = r * asp * 1.05
        n = 150 if k < 3 else 120
        g = np.linspace(-R, R, n)
        X, Y = np.meshgrid(cx + g, cy_ + g, indexing='xy')     # rows = y, cols = x (+Z winding)
        Z = island_height(X, Y, isl)
        _obj(bpy, f'KF_Island{k}', _mesh_from_grid(bpy, f'KF_Island{k}', X, Y, Z), isl_m)

    # far volcano: radial grid
    vmat = _rock_material(bpy, 'KF_VolcanoRock', dist_scale=110000.0, ash=False, bump=False, base_haze=(-180.0, 700.0, 0.20))
    rr = np.concatenate([np.linspace(0, 400, 40, endpoint=False), np.geomspace(400, 6500, 120)])
    aa = np.linspace(math.pi, -math.pi, 360)              # clockwise -> +Z normals
    Rg, Ag = np.meshgrid(rr, aa, indexing='ij')
    Xv = VOLC[0] + Rg * np.cos(Ag); Yv = VOLC[1] + Rg * np.sin(Ag)
    Zv = np.maximum(volcano_height(Xv, Yv), -300.0)
    _obj(bpy, 'KF_Volcano', _mesh_from_grid(bpy, 'KF_Volcano', Xv, Yv, Zv), vmat)

    # --- cloud sea: homogeneous Principled Volume inside a closed shell whose top is the billowed cloud surface.
    #     (Shape lives in the mesh, so Cycles integrates the medium analytically: no ray-marching, no empty-air steps.)
    cmat = _cloud_volume_material(bpy, 'KF_CloudSea')
    _obj(bpy, 'KF_CloudSea', _cloud_shell(bpy), cmat)
    dmat = bpy.data.materials.new('KF_FarDeck'); N, L = _nodes(dmat)
    do = N.new('ShaderNodeOutputMaterial'); db = N.new('ShaderNodeBsdfDiffuse'); db.inputs['Color'].default_value = (0.62, 0.66, 0.74, 1)
    L.new(_haze(N, L, db.outputs[0], 26000.0, start=SHELL_END - 600.0, cool=DECK_HAZE_COOL, warm=DECK_HAZE_WARM, sharp=4.0), do.inputs['Surface'])
    dmat.cycles.emission_sampling = 'NONE'
    _obj(bpy, 'KF_FarDeck', _far_deck(bpy), dmat)

    # --- the rider (horse + rider), dark, sheen for the sun rim
    horse_m = _dark_material(bpy, 'KF_Horse', (0.030, 0.024, 0.020))
    cloak_m = _dark_material(bpy, 'KF_Cloak', (0.022, 0.022, 0.026), sheen=0.9, rough=0.7)
    root = bpy.data.objects.new('KF_RiderRoot', None); sc.collection.objects.link(root); root.rotation_mode = 'XYZ'
    body = _obj(bpy, 'KF_Body', _capsule(bpy, 'KF_Body', 0.31, 0.46), horse_m, root); body.location = (0, 0, 1.22)
    neck_piv = bpy.data.objects.new('KF_NeckPivot', None); sc.collection.objects.link(neck_piv); neck_piv.parent = root
    neck_piv.location = (0, 0.66, 1.38); neck_piv.rotation_mode = 'XYZ'
    neck = _obj(bpy, 'KF_Neck', _capsule(bpy, 'KF_Neck', 0.14, 0.26, axis='Z'), horse_m, neck_piv); neck.location = (0, 0, 0.30)
    head = _obj(bpy, 'KF_Head', _capsule(bpy, 'KF_Head', 0.10, 0.17), horse_m, neck_piv)
    head.location = (0, 0.18, 0.66); head.rotation_euler = (math.radians(-55), 0, 0)
    tail = _obj(bpy, 'KF_Tail', _cylinder(bpy, 'KF_Tail', 0.07, 0.02), horse_m, root)
    tail.location = (0, -0.86, 1.36); tail.rotation_euler = (math.radians(160), 0, 0); tail.scale = (1, 1, 0.75)
    seat = bpy.data.objects.new('KF_Seat', None); sc.collection.objects.link(seat); seat.parent = root
    seat.location = (0, -0.10, 1.52); seat.rotation_mode = 'XYZ'
    torso = _obj(bpy, 'KF_Torso', _capsule(bpy, 'KF_Torso', 0.16, 0.17, axis='Z'), cloak_m, seat); torso.location = (0, 0, 0.36)
    cloak = _obj(bpy, 'KF_Cloak', _cylinder(bpy, 'KF_Cloak', 0.40, 0.15, seg=12), cloak_m, seat)
    cloak.location = (0, -0.06, -0.22); cloak.scale = (1.0, 0.9, 0.78); cloak.rotation_euler = (math.radians(-8), 0, 0)
    head_piv = bpy.data.objects.new('KF_HeadPivot', None); sc.collection.objects.link(head_piv); head_piv.parent = seat
    head_piv.location = (0, 0, 0.66); head_piv.rotation_mode = 'XYZ'
    rhead = _obj(bpy, 'KF_RiderHead', _capsule(bpy, 'KF_RiderHead', 0.105, 0.02, axis='Z'), cloak_m, head_piv); rhead.location = (0, 0.02, 0.10)
    thighs = []
    for sx in (-1, 1):
        th = _obj(bpy, f'KF_RLeg{sx}', _cylinder(bpy, f'KF_RLeg{sx}', 0.07, 0.05), cloak_m, seat)
        th.location = (0.22 * sx, 0.05, 0.02); th.rotation_euler = (math.radians(165), math.radians(-12 * sx), 0); th.scale = (1, 1, 0.62)
        thighs.append(th)
    staff = _obj(bpy, 'KF_Staff', _cylinder(bpy, 'KF_Staff', 0.022, 0.016, seg=6), horse_m, seat)
    staff.location = (0.27, 0.22, -0.55); staff.rotation_euler = (math.radians(8), math.radians(4), 0); staff.scale = (1, 1, 2.35)
    legs = []
    for (nm, hx, hy, off) in LEGS:
        up_ = _obj(bpy, f'KF_{nm}_up', _cylinder(bpy, f'KF_{nm}_up', 0.075, 0.06), horse_m); up_.rotation_mode = 'QUATERNION'
        lo_ = _obj(bpy, f'KF_{nm}_lo', _cylinder(bpy, f'KF_{nm}_lo', 0.05, 0.042), horse_m); lo_.rotation_mode = 'QUATERNION'
        legs.append((up_, lo_))

    # --- camera
    cd = bpy.data.cameras.new('KF_Cam'); cd.lens = LENS; cd.sensor_width = 36.0; cd.sensor_fit = 'HORIZONTAL'
    cd.clip_start = 1.0; cd.clip_end = 600000.0
    cam = bpy.data.objects.new('KF_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; cam.rotation_mode = 'QUATERNION'

    # --- compositor finish: halation on highlights, vignette <= 0.4 stop, deterministic grain
    grain_w = _compositor(bpy, sc)

    return {'samples': sc.cycles.samples, 'sky_gain': sky_gain, 'sky_nodes': sky_nodes, 'sun': sun, 'cam': cam, 'root': root, 'neck_piv': neck_piv, 'head_piv': head_piv,
            'seat': seat, 'legs': legs, 'world_bg': bg, 'grain_w': grain_w, 'staff': staff, 'cloak': cloak,
            'hide_on_black': [o for o in sc.objects if o.type in ('MESH', 'LIGHT')]}

def _compositor(bpy, sc):
    ng = bpy.data.node_groups.new('KF_Finish', 'CompositorNodeTree')
    ng.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    N, L = ng.nodes, ng.links
    rl = N.new('CompositorNodeRLayers'); go = N.new('NodeGroupOutput')
    gl = N.new('CompositorNodeGlare')
    gl.inputs['Type'].default_value = 'Bloom'; gl.inputs['Quality'].default_value = 'Medium'
    gl.inputs['Threshold'].default_value = 60.0; gl.inputs['Strength'].default_value = 0.28; gl.inputs['Size'].default_value = 0.40
    gl.inputs['Saturation'].default_value = 1.0
    gl.inputs['Clamp'].default_value = True; gl.inputs['Maximum'].default_value = 250.0   # the sun disc is ~1e6: bound its bloom
    L.new(rl.outputs['Image'], gl.inputs['Image'])
    ic = N.new('CompositorNodeImageCoordinates'); L.new(rl.outputs['Image'], ic.inputs['Image'])
    # vignette: 1 - 0.24 * smoothstep(0.25, 0.85, r^2) on aspect-corrected normalized coords (≈0.4 stop in corners)
    sepc = N.new('ShaderNodeSeparateXYZ'); L.new(ic.outputs['Normalized'], sepc.inputs[0])
    def m(op, a, b=None, vb=None, va=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        if isinstance(a, (int, float)): n.inputs[0].default_value = a
        else: L.new(a, n.inputs[0])
        if b is not None: L.new(b, n.inputs[1])
        elif vb is not None: n.inputs[1].default_value = vb
        return n.outputs[0]
    dx = m('MULTIPLY', m('SUBTRACT', sepc.outputs[0], vb=0.5), vb=1.0)
    dy = m('MULTIPLY', m('SUBTRACT', sepc.outputs[1], vb=0.5), vb=0.5625)
    r2 = m('ADD', m('MULTIPLY', dx, dx), m('MULTIPLY', dy, dy))
    vg = N.new('ShaderNodeMapRange'); vg.interpolation_type = 'SMOOTHSTEP'; L.new(r2, vg.inputs['Value'])
    vg.inputs['From Min'].default_value = 0.04; vg.inputs['From Max'].default_value = 0.33
    vg.inputs['To Min'].default_value = 1.0; vg.inputs['To Max'].default_value = 0.76
    # grain: 4-D white noise on pixel coords, W = frame (set per frame) -> multiplicative, ±4 %
    wn = N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '4D'; L.new(ic.outputs['Pixel'], wn.inputs['Vector'])
    g = m('ADD', m('MULTIPLY', m('SUBTRACT', wn.outputs['Value'], vb=0.5), vb=0.08), vb=1.0)
    gain = m('MULTIPLY', g, vg.outputs[0])
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    L.new(gl.outputs['Image'], mul.inputs['A']); L.new(gain, mul.inputs['B'])
    L.new(mul.outputs['Result'], go.inputs[0])
    sc.compositing_node_group = ng; sc.render.use_compositing = True
    return wn.inputs['W']

# ----------------------------------------------------------------------------------------------- per frame
def _sun_dir(el_deg, rot_deg):
    el = math.radians(el_deg); rot = math.radians(rot_deg)
    return np.array([math.sin(rot) * math.cos(el), math.cos(rot) * math.cos(el), math.sin(el)])

SUN_ROT = 0.37                    # azimuth (deg, + toward +X): first limb pixel on frame 91 (3.79 s) — verified on renders, not just analytically

def _place_segment(ob, p0, p1):
    from mathutils import Vector
    a = Vector(p0); b = Vector(p1); d = b - a
    ob.location = a; ob.rotation_quaternion = d.to_track_quat('Z', 'Y'); ob.scale = (1.0, 1.0, max(d.length, 1e-3))

def frame(bpy, ctx, st, i, t):
    from mathutils import Vector, Matrix, Euler
    sc = bpy.context.scene
    black = i >= CUT
    if st.get('black') != black:
        sc.render.dither_intensity = 0.0 if black else 1.0       # true 0 on the black frames
        for ob in st['hide_on_black']: ob.hide_render = black
        st['world_bg'].inputs['Strength'].default_value = 0.0 if black else 1.0
        st['black'] = black
    sc.cycles.samples = 1 if black else st['samples']
    st['grain_w'].default_value = float(i) * 1.618
    if black:
        return
    # sun
    el = sun_elevation(t)
    for s in st['sky_nodes']:
        s.sun_elevation = math.radians(el); s.sun_rotation = math.radians(SUN_ROT)
    g = sky_gain(el); st['sky_gain'].default_value = (5.0 * g[0], 5.0 * g[1], 5.0 * g[2])
    d = _sun_dir(el, SUN_ROT)
    st['sun'].rotation_quaternion = Vector(d).to_track_quat('Z', 'Y')
    # camera
    loc, yaw, pitch, roll = camera_pose(t, ctx['W'], ctx['H'])
    cam = st['cam']; cam.location = Vector(loc)
    Mc = Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Rotation(math.pi / 2 + pitch, 4, 'X') @ Matrix.Rotation(roll, 4, 'Z')
    cam.rotation_quaternion = Mc.to_quaternion()
    # rider
    rp, head, rpitch = rider_root(t)
    ph = gait_phase(t)
    stand = float(smoothstep(T_REACT + 0.1, T_HALT, t))
    bob = 0.035 * math.cos(4 * math.pi * ph) * (1 - stand)
    root = st['root']
    root.location = Vector(rp) + Vector((0, 0, bob))
    root.rotation_euler = Euler((rpitch * 0.8, 0.012 * math.sin(2 * math.pi * ph) * (1 - stand), -head), 'XYZ')
    react = float(smoothstep(T_REACT - 0.05, T_REACT + 0.45, t))
    nod = 0.06 * math.sin(4 * math.pi * ph + 0.6) * (1 - stand)
    st['neck_piv'].rotation_euler = (math.radians(-38) + nod + 0.30 * react, 0, 0)        # + = neck more upright: head up
    st['seat'].rotation_euler = (0.05 * math.sin(4 * math.pi * ph + 1.2) * (1 - stand) + 0.06 * react, 0, 0)  # rider straightens
    st['head_piv'].rotation_euler = (0.30 * react, 0, 0.10 * react)                    # looks up toward the sun
    lift = float(smoothstep(T_REACT + 0.05, T_REACT + 0.55, t)) - 0.25 * float(smoothstep(T_REACT - 0.15, T_REACT + 0.05, t)) * (1.0 - float(smoothstep(T_REACT + 0.05, T_REACT + 0.3, t)))
    st['staff'].location = (0.27, 0.22 + 0.10 * lift, -0.55 + 0.62 * lift)
    st['staff'].rotation_euler = (math.radians(8 + 14 * lift), math.radians(4), 0)
    st['cloak'].rotation_euler = (math.radians(-8) - 0.05 * math.sin(2 * math.pi * 0.9 * t), 0, 0.03 * math.sin(2 * math.pi * 0.6 * t + 1))
    # legs: planted hooves on the real terrain height, 2-bone IK in the leg plane
    bpy.context.view_layer.update()
    M = root.matrix_world
    fwd = Vector((math.sin(head), math.cos(head), 0.0))
    for (nm, hx, hy, off), (up_, lo_) in zip(LEGS, st['legs']):
        hip = M @ Vector((hx, hy, 1.10))
        s, lift = hoof_local(t, (nm, hx, hy, off))
        base = Vector(rp) + Vector((math.cos(head) * hx, -math.sin(head) * hx, 0)) + fwd * (hy + s)
        gz = float(ridge_height(base.x, base.y))
        hoof = Vector((base.x, base.y, gz + 0.03 + lift))
        L1, L2 = 0.52, 0.60
        dvec = hoof - hip; dist = min(dvec.length, L1 + L2 - 1e-3)
        dvec.normalize(); hoof_c = hip + dvec * dist
        a = (L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist); a = max(-1.0, min(1.0, a))
        ang = math.acos(a)
        bend = -1.0 if hy > 0 else 1.0                       # front knees forward, hocks backward
        side = fwd.cross(Vector((0, 0, 1))).normalized()
        knee_dir = dvec * math.cos(ang) + (dvec.cross(side)).normalized() * math.sin(ang) * bend
        knee = hip + knee_dir * L1
        _place_segment(up_, hip, knee); _place_segment(lo_, knee, hoof_c)
