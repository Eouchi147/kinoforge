"""Dressing of the Arabia table: scatter (rocks, wind-blown tufts, thorn scrub), palms and an oasis pool, rugs, pots, saddles, sacks,
small fires with clay smoke, goats, drifting sand grains, caravan lights on a far ridge, flags. Static things are built once in world
coordinates (heights from the terrain); moving things are pure functions of the pose time t."""
import math
import numpy as np
from kit import *
from kit import _mat
import world as W
from actors import pivot, mk, D, torus

def gz(x, y):
    if x > 6.0:
        import blender
        return float(blender.mecca_h(np.array(x), np.array(y)))
    return float(W.terrain_h(np.array(x), np.array(y)))

def raw_obj(bpy, name, V, F, mat, coll, smooth=True, shadow=True):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in V], [], [tuple(f) for f in F]); me.update()
    if smooth: me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.update()
    if mat is not None: me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    if not shadow: set_vis(ob, False)
    return ob

def dist_to_poly(px, py, pts):
    best = 9.0
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        u = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        best = min(best, math.hypot(px - (ax + u * dx), py - (ay + u * dy)))
    return best

def blocked(x, y, S, margin=0.0):
    """True where a rock or tuft would sit on something (a pad, a path, a lamp)."""
    for (px, py, r0, r1) in W.PADS:
        if math.hypot(x - px, (y - py) * 1.15) < r1 * 0.92 + margin: return True
    for pts in S['paths']:
        if dist_to_poly(x, y, pts) < 0.12 + margin: return True
    if 'field_xy' not in S: S['field_xy'] = np.array([(a, b) for a, b, _ in S['field'].pts])
    if float(np.min(np.hypot(S['field_xy'][:, 0] - x, S['field_xy'][:, 1] - y))) < 0.045 + margin: return True
    for (px, py, r) in S.get('keepout', []):
        if math.hypot(x - px, y - py) < r + margin: return True
    return False

# --------------------------------------------------------------------------------------------------------------- rocks, tufts, scrub
def rock_mesh(rs, r, seg=9, rings=6):
    """A lumpy clay stone: squashed sphere with a flat-ish bottom; returns (V, F) around the origin, base at z = 0."""
    V, F = [], []
    sx, sy, sz = r * rs.uniform(0.8, 1.3), r * rs.uniform(0.7, 1.1), r * rs.uniform(0.45, 0.8)
    for i in range(rings + 1):
        ph = math.pi * i / rings
        for j in range(seg):
            th = 2 * math.pi * j / seg; bump = 1.0 + 0.18 * (rs.rand() - 0.5)
            V.append((sx * bump * math.sin(ph) * math.cos(th), sy * bump * math.sin(ph) * math.sin(th), max(-0.35 * sz, sz * math.cos(ph)) + 0.35 * sz))
    for i in range(rings):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg; F.append((a, b, b + seg, a + seg))
    return V, F

def build_scatter(bpy, S, M, coll, region, nrock, ntuft, nscrub, seed=5, rock_mat=None, tuft_mat=None, name='sc'):
    """Rocks (a few big ones, many small), tufts of dry grass (sway with the wind) and low thorn scrub, scattered over a region."""
    rs = np.random.RandomState(seed); x0, x1, y0, y1 = region
    def place(n, margin, tries=4000):
        out = []; k = 0
        while len(out) < n and k < tries:
            k += 1; x = rs.uniform(x0, x1); y = rs.uniform(y0, y1)
            if blocked(x, y, S, margin): continue
            out.append((x, y))
        return out
    # rocks: clusters of 1 to 4
    V, F = [], []
    for (x, y) in place(nrock, 0.03):
        big = rs.rand() < 0.12; n = 1 if big else rs.randint(1, 4)
        for q in range(n):
            ox, oy = (0, 0) if q == 0 else (rs.uniform(-0.05, 0.05), rs.uniform(-0.05, 0.05)); px, py = x + ox, y + oy
            r = rs.uniform(0.040, 0.075) if big else rs.uniform(0.010, 0.030) * (0.6 if q else 1.0)
            v, f = rock_mesh(rs, r); yaw = rs.uniform(0, 6.28); c, s_ = math.cos(yaw), math.sin(yaw); z0 = gz(px, py) - 0.006
            b = len(V); V += [(px + c * a - s_ * bb, py + s_ * a + c * bb, z0 + zz) for a, bb, zz in v]; F += [tuple(b + i for i in tri) for tri in f]
    S[name + '_rocks'] = raw_obj(bpy, name + '_rocks', V, F, rock_mat or M['rock'], coll)
    # tufts: 5 to 9 curved blades each, base weights kept for the sway
    V, F, BASE, WGT, PH = [], [], [], [], []
    for (x, y) in place(ntuft, 0.02):
        z0 = gz(x, y) - 0.002; nb = rs.randint(5, 10); hh = rs.uniform(0.022, 0.055); ph = rs.uniform(0, 6.28)
        for q in range(nb):
            a = rs.uniform(0, 6.28); lean = rs.uniform(0.10, 0.55); h = hh * rs.uniform(0.6, 1.0); w = 0.0020
            dx, dy = math.cos(a), math.sin(a); nx_, ny_ = -dy, dx; b = len(V)
            for k in range(4):
                u = k / 3.0; px = x + dx * lean * h * u * u + 0.0; py = y + dy * lean * h * u * u; pz = z0 + h * u; ww = w * (1 - 0.8 * u * u)
                V.append((px - nx_ * ww, py - ny_ * ww, pz)); V.append((px + nx_ * ww, py + ny_ * ww, pz)); WGT += [u * u, u * u]; PH += [ph, ph]
            for k in range(3): F.append((b + 2 * k, b + 2 * k + 1, b + 2 * k + 3, b + 2 * k + 2))
    S[name + '_tufts'] = raw_obj(bpy, name + '_tufts', V, F, tuft_mat or M['tuft'], coll)
    S[name + '_tuft_base'] = np.array(V, np.float32); S[name + '_tuft_w'] = np.array(WGT, np.float32); S[name + '_tuft_ph'] = np.array(PH, np.float32)
    # scrub: little thorny bushes (crossed thin tubes) joined into one mesh
    V, F = [], []
    for (x, y) in place(nscrub, 0.05):
        z0 = gz(x, y) - 0.002; h = rs.uniform(0.025, 0.05)
        for q in range(rs.randint(7, 12)):
            a = rs.uniform(0, 6.28); lean = rs.uniform(0.3, 1.0); hh = h * rs.uniform(0.55, 1.0); dx, dy = math.cos(a) * lean, math.sin(a) * lean
            pts = [(x + dx * hh * t * 0.6 + rs.uniform(-1, 1) * 0.002 * t, y + dy * hh * t * 0.6, z0 + hh * t) for t in (0.0, 0.4, 0.75, 1.0)]
            rad = [0.0017, 0.0013, 0.0009, 0.0003]; ring = 5; b = len(V)
            for k, (p, r_) in enumerate(zip(pts, rad)):
                for j in range(ring):
                    th = 2 * math.pi * j / ring; V.append((p[0] + r_ * math.cos(th), p[1] + r_ * math.sin(th), p[2]))
            for k in range(3):
                for j in range(ring): aa = b + k * ring + j; bb_ = b + k * ring + (j + 1) % ring; F.append((aa, bb_, bb_ + ring, aa + ring))
    S[name + '_scrub'] = raw_obj(bpy, name + '_scrub', V, F, M['thorn'], coll)

def sway_tufts(S, name, t, amp=0.006, wind=0.9):
    """Wind through the dry grass: the blade tips lean and flutter (pure function of t)."""
    ob = S[name + '_tufts']; base = S[name + '_tuft_base']; w = S[name + '_tuft_w']; ph = S[name + '_tuft_ph']
    gust = 0.6 + 0.4 * math.sin(t * 0.7)
    dx = amp * w * (np.sin(t * 2.6 * wind + ph * 3.1) * 0.7 + 1.1 * gust); dy = amp * 0.4 * w * np.sin(t * 2.1 * wind + ph)
    V = base.copy(); V[:, 0] += dx; V[:, 1] += dy
    ob.data.vertices.foreach_set('co', V.ravel()); ob.data.update()

# --------------------------------------------------------------------------------------------------------------- palms and the oasis
class Palm:
    """Clay date palm: ringed trunk, nine serrated fronds on pivots that sway, a hanging bunch of dates."""
    def __init__(self, bpy, name, coll, M, h=0.34, lean=(0.0, 0.0), seed=1):
        rs = np.random.RandomState(seed); self.name = name; self.h = h
        self.root = pivot(bpy, name + '_root', coll); self.root.rotation_euler = (D(lean[0]), D(lean[1]), 0.0)
        rings = []; n = 18
        for k in range(n + 1):
            z = h * k / n; rr = (0.0115 - 0.0038 * k / n) * (1.0 + 0.07 * (k % 2)) * (1.25 if k == 0 else 1.0); rings.append((z - 0.004, rr, rr * 0.96))
        v, f = loft_z(rings, 14, True, True); mk(bpy, name + '_trunk', v, f, M['palm'], coll, self.root, noise_amp=0.0006, seed=seed)
        self.crown = pivot(bpy, name + '_crown', coll, self.root, (0, 0, h))
        self.fronds = []
        # one frond mesh shared by all (a long serrated arch); each frond has its own pivot with yaw, droop and size
        L_ = 0.20; seg = 14; V, F = [], []
        for k in range(seg + 1):
            u = k / seg; x = L_ * u; z = 0.050 * math.sin(math.pi * u * 0.55) - 0.22 * u * u * 0.5; wd = 0.0105 * math.sin(math.pi * min(1.0, u * 1.05) ** 0.8) * (0.70 + 0.30 * abs(math.sin(u * 26.0)))
            V += [(x, -wd, z - 0.0016), (x, 0.0, z + 0.0016), (x, wd, z - 0.0016)]
        for k in range(seg):
            b = 3 * k; F += [(b, b + 3, b + 4, b + 1), (b + 1, b + 4, b + 5, b + 2)]
        me = bpy.data.meshes.new(name + '_frond'); me.from_pydata(V, [], F); me.update(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.materials.append(M['frond'])
        for q in range(10):
            yaw = 360.0 * q / 10 + rs.uniform(-12, 12); pv = pivot(bpy, f'{name}_fp{q}', coll, self.crown); pv.rotation_euler = (0, 0, D(yaw))
            fo = bpy.data.objects.new(f'{name}_fr{q}', me); coll.objects.link(fo); fo.parent = pv; s = rs.uniform(0.85, 1.15); fo.scale = (s, 1.0, s)
            fo.rotation_euler = (0, D(rs.uniform(-18, 28)), 0); self.fronds.append((pv, yaw, rs.uniform(0, 6.28), fo))
        for q in range(3):
            a = 2 * math.pi * q / 3; dt = ellipsoid(bpy, f'{name}_dt{q}', (0.0045, 0.0045, 0.0075), M['dates'], coll, seg=10, rings=6); dt.parent = self.crown
            dt.location = (0.008 * math.cos(a), 0.008 * math.sin(a), -0.010)
        self.base_rot = (D(lean[0]), D(lean[1]))

    def place(self, x, y, yaw=0.0):
        self.root.location = (x, y, gz(x, y) - 0.004); self.root.rotation_euler = (self.base_rot[0], self.base_rot[1], D(yaw))

    def sway(self, t, amp=1.0):
        gust = 0.55 + 0.45 * math.sin(t * 0.45 + self.h * 9)
        for (pv, yaw, ph, fo) in self.fronds:
            fo_ = 0.05 * amp * gust * math.sin(t * 1.9 + ph) + 0.035 * amp * math.sin(t * 3.4 + ph * 2)
            pv.rotation_euler = (D(2.5 * amp * gust * math.sin(t * 1.5 + ph)), fo_, D(yaw) + 0.04 * amp * math.sin(t * 0.9 + ph))
            # note: rotation about pivot's y bends the frond up and down; the x/z terms flutter it sideways

    def hide(self, h=True): hide(self.root, h)

def water_mat(bpy):
    m, N, L, p, out = _mat(bpy, 'oasis_water')
    p.inputs['Base Color'].default_value = srgb((0.08, 0.20, 0.30)); p.inputs['Roughness'].default_value = 0.08; p.inputs['Metallic'].default_value = 0.0
    try: p.inputs['IOR'].default_value = 1.33
    except Exception: pass
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 70.0; nz.inputs['Detail'].default_value = 2.0
    S_ = N.new('ShaderNodeValue'); S_.outputs[0].default_value = 0.0
    vv = N.new('ShaderNodeMapping'); L.new(tc.outputs['Object'], vv.inputs['Vector'])
    L.new(vv.outputs['Vector'], nz.inputs['Vector']); L.new(S_.outputs[0], nz.inputs['W'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; bp.inputs['Distance'].default_value = 0.002
    L.new(nz.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs['Normal'], p.inputs['Normal'])
    return m, S_

class Oasis:
    """A shallow pool ringed with stones, reeds and palms."""
    def __init__(self, bpy, name, coll, M, x, y, palms, rs_seed=3, r=0.17):
        rs = np.random.RandomState(rs_seed); self.x, self.y = x, y; self.root = pivot(bpy, name + '_root', coll)
        z0 = gz(x, y) - 0.002; self.palms = []
        wm, self.wnode = water_mat(bpy); self.wmat = wm
        v, f = loft_z([(z0 - 0.004, r * 1.18, r * 0.92), (z0 + 0.0008, r * 1.10, r * 0.86), (z0 + 0.0010, r * 0.97, r * 0.76), (z0 + 0.0010, 0.0, 0.0)], 40, False, False)
        # flat water disc
        V = [(x + r * 0.97 * math.cos(2 * math.pi * j / 40), y + r * 0.78 * math.sin(2 * math.pi * j / 40), z0 + 0.0014) for j in range(40)] + [(x, y, z0 + 0.0014)]
        F = [(40, j, (j + 1) % 40) for j in range(40)]
        self.water = raw_obj(bpy, name + '_water', V, F, wm, coll)
        V, F = [], []
        for j in range(26):                                                       # stones ringing the pool
            a = 2 * math.pi * j / 26 + rs.uniform(-0.05, 0.05); px, py = x + r * 1.10 * math.cos(a), y + r * 0.90 * math.sin(a)
            v, ff = rock_mesh(rs, rs.uniform(0.008, 0.016), 8, 5); zz = gz(px, py) - 0.006; b = len(V); V += [(px + a_, py + b_, zz + c_) for a_, b_, c_ in v]; F += [tuple(b + i for i in tri) for tri in ff]
        raw_obj(bpy, name + '_ring', V, F, M['rock'], coll)
        V, F = [], []
        for k in range(46):                                                       # reeds
            a = rs.uniform(0, 6.28); rr = rs.uniform(0.86, 1.28); px, py = x + r * rr * math.cos(a), y + r * 0.9 * rr * math.sin(a); h = rs.uniform(0.022, 0.05); lean = rs.uniform(0.0, 0.25); b = len(V)
            ax, ay = math.cos(a), math.sin(a)
            for q in range(3):
                u = q / 2.0; V += [(px + ax * lean * h * u * u - 0.0013 * (1 - u), py + ay * lean * h * u * u, gz(px, py) + h * u), (px + ax * lean * h * u * u + 0.0013 * (1 - u), py + ay * lean * h * u * u, gz(px, py) + h * u)]
            F += [(b, b + 1, b + 3, b + 2), (b + 2, b + 3, b + 5, b + 4)]
        self.reeds = raw_obj(bpy, name + '_reeds', V, F, M['reed'], coll)
        for k, (dx, dy, h, ln) in enumerate(palms):
            p = Palm(bpy, f'{name}_palm{k}', coll, M, h=h, lean=ln, seed=rs_seed * 10 + k); p.place(x + dx, y + dy, rs.uniform(0, 360)); self.palms.append(p)

    def animate(self, t):
        self.wnode.outputs[0].default_value = t * 0.35
        for p in self.palms: p.sway(t)

# --------------------------------------------------------------------------------------------------------------- fire, smoke, goats
class Fire:
    """A small cook fire: ring of stones, crossed sticks, embers, three tongues of flame, a warm light and eight clay smoke puffs."""
    def __init__(self, bpy, name, coll, M, with_light=True, seed=1):
        rs = np.random.RandomState(seed); self.root = pivot(bpy, name + '_root', coll)
        for j in range(9):
            a = 2 * math.pi * j / 9; st = ellipsoid(bpy, f'{name}_st{j}', (0.0085, 0.0070, 0.0060), M['stone'], coll, seg=12, rings=8, noise_amp=0.0004, seed=seed + j); st.parent = self.root
            st.location = (0.022 * math.cos(a), 0.022 * math.sin(a), 0.004); st.rotation_euler = (0, 0, a)
        for j in range(3):
            tb = tube(bpy, f'{name}_stick{j}', [(-0.016, 0, 0.0), (0, 0, 0.007), (0.016, 0, 0.0)], [0.0022, 0.0020, 0.0022], M['pole'], coll, n=8, ring=6, lateral=(0, 1, 0)); tb.parent = self.root; tb.rotation_euler = (0, 0, D(60 * j + 10)); tb.location = (0, 0, 0.002)
        em = ellipsoid(bpy, name + '_embers', (0.015, 0.015, 0.0035), M['ember'], coll, seg=14, rings=6); em.parent = self.root; em.location = (0, 0, 0.0045); set_vis(em, False)
        self.flames = []
        for j, (dx, dy, hh) in enumerate(((0.0, 0.0, 1.0), (0.007, 0.004, 0.7), (-0.006, -0.004, 0.8))):
            fl = ellipsoid(bpy, f'{name}_fl{j}', (0.0042, 0.0042, 0.0125), M['flame'], coll, seg=12, rings=8, shape=lambda x, y, z: (x * (1 - 0.7 * max(0, z)), y * (1 - 0.7 * max(0, z)), z)); fl.parent = self.root
            fl.location = (dx, dy, 0.0085 + 0.011 * hh); set_vis(fl, False); self.flames.append((fl, hh, rs.uniform(0, 6.28)))
        self.light = None
        if with_light:
            ld = bpy.data.lights.new(name + '_light', 'POINT'); ld.energy = 0.5; ld.shadow_soft_size = 0.01; ld.use_temperature = True; ld.temperature = 1800
            self.light = bpy.data.objects.new(name + '_light', ld); coll.objects.link(self.light); self.light.parent = self.root; self.light.location = (0, 0, 0.022)
        self.puffs = []
        for j in range(8):
            p = ellipsoid(bpy, f'{name}_smoke{j}', (0.0065, 0.0060, 0.0055), M['smoke'], coll, seg=12, rings=8, noise_amp=0.0006, seed=seed + 40 + j); p.parent = self.root; self.puffs.append((p, rs.uniform(0, 1), rs.uniform(-1, 1)))

    def place(self, x, y): self.root.location = (x, y, gz(x, y) - 0.002)

    def animate(self, t, hit=0.0, power=1.0, wind=(0.9, 0.25)):
        for (fl, hh, ph) in self.flames:
            s = 1.0 + 0.22 * math.sin(t * 17.0 + ph) + 0.12 * math.sin(t * 31.0 + ph * 2) + 0.25 * hit
            fl.scale = (s * 0.9, s * 0.9, s * (0.9 + 0.25 * math.sin(t * 13.0 + ph))); fl.rotation_euler = (0.12 * math.sin(t * 9 + ph), 0.12 * math.cos(t * 7 + ph), 0)
        if self.light is not None: self.light.data.energy = 0.5 * power * (1.0 + 0.18 * math.sin(t * 19.0) + 0.12 * math.sin(t * 29.0 + 1.0) + 0.4 * hit)
        for (p, ph, jx) in self.puffs:
            age = (t * 0.30 + ph) % 1.0; z = 0.028 + age * 0.17; x = wind[0] * 0.10 * age * age + 0.006 * jx * math.sin(age * 9 + ph * 6); y = wind[1] * 0.10 * age * age
            s = (0.55 + 2.4 * age) * (1.0 - smooth(0.70, 1.0, age)) * (smooth(0.0, 0.12, age)); p.location = (x, y, z); p.scale = (max(0.01, s),) * 3
            p.rotation_euler = (age * 3, age * 2, ph * 6)

    def hide(self, h=True): hide(self.root, h)

class Goat:
    """A clay goat: barrel body, neck, horned head with a beard, four thin legs; grazes (head dips), flicks its tail."""
    def __init__(self, bpy, name, coll, M, col='a', seed=1):
        mc = M['goat_' + col]; dk = M['goat_c']; self.root = pivot(bpy, name + '_root', coll); self.body = pivot(bpy, name + '_body', coll, self.root)
        torso = ellipsoid(bpy, name + '_torso', (0.020, 0.034, 0.019), mc, coll, seg=22, rings=12, noise_amp=0.0004, seed=seed); torso.parent = self.body; torso.location = (0, 0, 0.040)
        rump = ellipsoid(bpy, name + '_rump', (0.019, 0.022, 0.018), mc, coll, seg=16, rings=10, seed=seed + 1); rump.parent = self.body; rump.location = (0, -0.022, 0.041)
        self.neckp = pivot(bpy, name + '_neckp', coll, self.body, (0, 0.030, 0.050))
        nk = tube(bpy, name + '_neck', [(0, 0, 0), (0, 0.010, 0.012), (0, 0.016, 0.026)], [0.0100, 0.0085, 0.0075], mc, coll, n=10, ring=10, lateral=(1, 0, 0)); nk.parent = self.neckp
        hp = pivot(bpy, name + '_headp', coll, self.neckp, (0, 0.018, 0.028)); self.headp = hp
        hd = ellipsoid(bpy, name + '_head', (0.0075, 0.0120, 0.0078), mc, coll, seg=14, rings=10, seed=seed + 2); hd.parent = hp; hd.location = (0, 0.004, 0.0)
        mz = ellipsoid(bpy, name + '_muzzle', (0.0055, 0.0070, 0.0055), mc, coll, seg=12, rings=8, seed=seed + 3); mz.parent = hp; mz.location = (0, 0.014, -0.0035)
        for sx in (-1, 1):
            e = ellipsoid(bpy, f'{name}_eye{sx}', (0.0013, 0.0011, 0.0015), dk, coll, seg=8, rings=6); e.parent = hp; e.location = (sx * 0.0066, 0.008, 0.0020)
            ea = ellipsoid(bpy, f'{name}_ear{sx}', (0.0070, 0.0030, 0.0020), mc, coll, seg=10, rings=6); ea.parent = hp; ea.location = (sx * 0.0100, 0.0, 0.0030); ea.rotation_euler = (0, D(sx * 12), D(-sx * 18))
            hn = tube(bpy, f'{name}_horn{sx}', [(sx * 0.004, 0.0, 0.007), (sx * 0.0065, -0.004, 0.015), (sx * 0.0055, -0.011, 0.020)], [0.0020, 0.0014, 0.0005], M['horn'], coll, n=8, ring=6, lateral=(0, 1, 0)); hn.parent = hp
        bd = ellipsoid(bpy, name + '_beard', (0.0020, 0.0030, 0.0060), M['goat_b'], coll, seg=8, rings=6); bd.parent = hp; bd.location = (0, 0.0145, -0.0100)
        self.legs = {}
        for key, (lx, ly) in (('FL', (-0.010, 0.020)), ('FR', (0.010, 0.020)), ('HL', (-0.010, -0.024)), ('HR', (0.010, -0.024))):
            lg = tube(bpy, f'{name}_leg{key}', [(0, 0, 0.0), (0, 0.001, -0.016), (0, 0.0, -0.032)], [0.0034, 0.0028, 0.0022], mc, coll, n=8, ring=8, lateral=(1, 0, 0)); lg.parent = self.body; lg.location = (lx, ly, 0.034)
            hf = ellipsoid(bpy, f'{name}_hoof{key}', (0.0026, 0.0034, 0.0020), dk, coll, seg=8, rings=6); hf.parent = lg; hf.location = (0, 0.0, -0.0325)
        tl = tube(bpy, name + '_tail', [(0, 0, 0), (0, -0.005, 0.005), (0, -0.008, 0.010)], [0.0030, 0.0022, 0.0012], mc, coll, n=8, ring=6, lateral=(1, 0, 0)); tl.parent = self.body; tl.location = (0, -0.040, 0.050); self.tail = tl

    def pose(self, x, y, yaw, t, graze=0.0, seed=0.0):
        self.root.location = (x, y, gz(x, y) - 0.001); self.root.rotation_euler = (0, 0, D(yaw)); ph = seed
        gp = graze * (0.5 + 0.5 * math.sin(t * 0.9 + ph)); self.neckp.rotation_euler = (D(55 * gp - 6), 0, D(8 * math.sin(t * 0.6 + ph)))
        self.headp.rotation_euler = (D(-20 * gp + 8 * math.sin(t * 1.3 + ph)), 0, 0); self.body.location = (0, 0, 0.0004 * math.sin(t * 2.4 + ph)); self.tail.rotation_euler = (D(12 * math.sin(t * 7.0 + ph)), 0, D(18 * math.sin(t * 5.0 + ph)))

    def hide(self, h=True): hide(self.root, h)

# --------------------------------------------------------------------------------------------------------------- drifting sand
class Drift:
    """Clay-sand grains blown along the ground (saltation hops). The pattern is world-fixed and wraps inside a box round the camera target."""
    def __init__(self, bpy, coll, M, n=260, seed=9, P=(1.8, 1.2)):
        rs = np.random.RandomState(seed); self.n = n; self.P = P; self.b = np.stack([rs.uniform(0, P[0], n), rs.uniform(0, P[1], n)], 1); self.ph = rs.uniform(0, 1, n); self.sz = rs.uniform(0.0016, 0.0034, n)
        self.sp = rs.uniform(0.7, 1.3, n); self.hop = rs.uniform(0.002, 0.012, n)
        # each grain is an eight-faced clay crumb; the mesh is rewritten every pose
        self.unit = np.array([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -0.6)], np.float32)
        F = []
        for k in range(n):
            b = 6 * k; F += [(b, b + 2, b + 4), (b + 2, b + 1, b + 4), (b + 1, b + 3, b + 4), (b + 3, b, b + 4), (b + 2, b, b + 5), (b + 1, b + 2, b + 5), (b + 3, b + 1, b + 5), (b, b + 3, b + 5)]
        self.ob = raw_obj(bpy, 'drift', np.zeros((6 * n, 3)), F, M['grain'], coll, smooth=False)

    def animate(self, t, cx, cy, wind=(0.055, 0.012)):
        Px, Py = self.P; u = self.b[:, 0] + wind[0] * self.sp * t; v = self.b[:, 1] + wind[1] * self.sp * t
        wx = cx + ((u - cx + Px / 2) % Px) - Px / 2; wy = cy + ((v - cy + Py / 2) % Py) - Py / 2
        z = np.array([gz(a, b) for a, b in zip(wx, wy)]) + 0.002 + self.hop * np.abs(np.sin(2 * math.pi * (0.9 * t * self.sp + self.ph)))
        V = (self.unit[None, :, :] * self.sz[:, None, None]) + np.stack([wx, wy, z], 1)[:, None, :]
        self.ob.data.vertices.foreach_set('co', V.reshape(-1, 3).astype(np.float32).ravel()); self.ob.data.update()

# --------------------------------------------------------------------------------------------------------------- static camp props (world coords)
def tex_rug(bpy, name, mat, coll, x, y, w, d, yaw=0.0, seed=0):
    """A woven rug lying on the sand: a rounded rectangle whose vertices follow the terrain."""
    rs = np.random.RandomState(seed); nx, ny = 14, 8; c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)); V, F = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            u = (i / nx - 0.5) * w; v = (j / ny - 0.5) * d; px, py = x + c * u - s_ * v, y + s_ * u + c * v
            edge = min(i, nx - i, j, ny - j) / 2.0; z = gz(px, py) + 0.0012 + 0.0016 * min(1.0, edge) + 0.0004 * rs.rand()
            V.append((px, py, z))
    for j in range(ny):
        for i in range(nx): a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    ob = raw_obj(bpy, name, V, F, mat, coll); return ob

def pot_obj(bpy, name, mat, coll, x, y, s=1.0, seed=0, kind='jar'):
    """A clay jar (round belly, neck, lip) or a wide bowl-pot, standing on the ground."""
    z0 = gz(x, y) - 0.001
    if kind == 'jar': prof = [(0.0, 0.0), (0.0075, 0.0004), (0.0125, 0.007), (0.0145, 0.016), (0.0125, 0.025), (0.0070, 0.031), (0.0060, 0.037), (0.0085, 0.040), (0.0060, 0.0415), (0.0048, 0.040)]
    else: prof = [(0.0, 0.0), (0.008, 0.0004), (0.0135, 0.006), (0.0160, 0.013), (0.0150, 0.0165), (0.0120, 0.0155), (0.0, 0.0145)]
    v, f = loft_z([(z * s, r * s, r * s) for (r, z) in prof], 18, False, False)
    o = mk(bpy, name, v, f, mat, coll, None, noise_amp=0.0004, seed=seed); o.location = (x, y, z0); return o

def saddle_obj(bpy, name, M, coll, x, y, yaw=0.0, seed=0):
    """A camel saddle on the ground: two rolled pads and a striped blanket, with a rope across."""
    r = pivot(bpy, name, coll); r.location = (x, y, gz(x, y) - 0.001); r.rotation_euler = (0, 0, D(yaw))
    for sx in (-1, 1):
        p = ellipsoid(bpy, f'{name}_pad{sx}', (0.0085, 0.021, 0.0105), M['pouch'], coll, seg=14, rings=8, noise_amp=0.0004, seed=seed); p.parent = r; p.location = (sx * 0.0105, 0, 0.0095)
    bl = ellipsoid(bpy, name + '_blanket', (0.026, 0.026, 0.0035), M['rug'], coll, seg=18, rings=6, noise_amp=0.0003, seed=seed + 1); bl.parent = r; bl.location = (0, -0.002, 0.0210); bl.rotation_euler = (0, 0, D(20))
    return r

def sack_obj(bpy, name, M, coll, x, y, yaw=0.0, seed=0):
    r = pivot(bpy, name, coll); r.location = (x, y, gz(x, y) - 0.001); r.rotation_euler = (0, 0, D(yaw))
    for k, (dx, dy, s) in enumerate(((0, 0, 1.0), (0.018, 0.006, 0.8))):
        o = ellipsoid(bpy, f'{name}_s{k}', (0.0095 * s, 0.0085 * s, 0.0115 * s), M['sack'], coll, seg=14, rings=10, noise_amp=0.0005, seed=seed + k); o.parent = r; o.location = (dx, dy, 0.0105 * s)
    return r

def flag_obj(bpy, name, M, coll, x, y, z, h=0.075, seed=0):
    """A striped cloth banner on a pole (Mecca rooftops); the cloth pivot sways with the wind."""
    r = pivot(bpy, name, coll); r.location = (x, y, z)
    pl = tube(bpy, name + '_pole', [(0, 0, 0), (0, 0, h * 0.5), (0, 0, h)], [0.0016, 0.0014, 0.0012], M['pole'], coll, n=8, ring=6, lateral=(1, 0, 0)); pl.parent = r
    cp = pivot(bpy, name + '_cp', coll, r, (0.0, 0, h * 0.97)); nx, ny = 8, 3; V, F = [], []
    for j in range(ny + 1):
        for i in range(nx + 1): V.append((i / nx * 0.034, 0.0, -j / ny * 0.018))
    for j in range(ny):
        for i in range(nx): a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new(name + '_cloth'); me.from_pydata(V, [], F); me.update(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.materials.append(M['rug'])
    co = bpy.data.objects.new(name + '_cloth', me); coll.objects.link(co); co.parent = cp
    return (r, me, np.array(V, np.float32))

def sway_flag(fl, t, seed=0.0, amp=0.006):
    r, me, base = fl; V = base.copy(); u = base[:, 0] / 0.034
    V[:, 1] += amp * u * np.sin(t * 5.5 + u * 5.0 + seed); V[:, 2] += 0.0015 * u * np.sin(t * 4.0 + u * 3.0 + seed)
    me.vertices.foreach_set('co', V.ravel()); me.update()


# --------------------------------------------------------------------------------------------------------------- the whole dressing
FIRE1 = (1.90, 1.52); FIRE2 = (-1.45, 2.72); FIRE3 = (10.15, 1.30)
OASIS_R = (3.10, 2.75); OASIS_L = (-3.55, 1.75)
GOAT_P = [(1.78, 1.20, 40.0), (2.02, 1.14, 160.0)]
SEATS = [(-1.52, 2.66, 40.0), (-1.38, 2.64, 140.0), (-1.46, 2.80, 270.0)]      # listeners at the family fire


# --------------------------------------------------------------------------------------------------------------- foreground framing
def _fg_grass(rs, nblades=22, hmax=0.11):
    V, F = [], []
    for q in range(nblades):
        a = rs.uniform(0, 6.28); r0 = rs.uniform(0.0, 0.020); h = hmax * rs.uniform(0.45, 1.0); lean = rs.uniform(0.15, 0.7); w = 0.0036
        dx, dy = math.cos(a), math.sin(a); nx_, ny_ = -dy, dx; bx, by = dx * r0, dy * r0; b = len(V)
        for k in range(5):
            u = k / 4.0; px = bx + dx * lean * h * u * u; py = by + dy * lean * h * u * u; pz = h * u; ww = w * (1 - 0.85 * u * u)
            V.append((px - nx_ * ww, py - ny_ * ww, pz)); V.append((px + nx_ * ww, py + ny_ * ww, pz))
        for k in range(4): F.append((b + 2 * k, b + 2 * k + 1, b + 2 * k + 3, b + 2 * k + 2))
    return V, F

def build_fg(bpy, S, M, coll):
    """Four foreground clusters (two grass clumps, two stone groups) that a low camera frames the bottom corners with (see fg_place)."""
    rs = np.random.RandomState(21); S['fgc'] = []
    for k in range(2):
        V, F = _fg_grass(rs, 22 + 4 * k, 0.10 + 0.02 * k); o = raw_obj(bpy, f'fgc_grass{k}', V, F, M['tuft'], coll); S['fgc'].append(o)
    for k in range(2):
        V, F = [], []
        for q in range(3 + k):
            r = rs.uniform(0.020, 0.040) * (1.0 if q == 0 else 0.6); v, f = rock_mesh(rs, r); b = len(V); ox, oy = rs.uniform(-0.04, 0.04), rs.uniform(-0.04, 0.04)
            V += [(a + ox, bb + oy, zz) for a, bb, zz in v]; F += [tuple(b + i for i in tri) for tri in f]
        o = raw_obj(bpy, f'fgc_rock{k}', V, F, M['rock'], coll); S['fgc'].append(o)
    for o in S['fgc']: o.hide_render = True

def fg_place(S, pos, tgt, which=(0, 3), side=(-1.0, 1.0)):
    """Frame a low shot: put two clusters on the ground ahead of the camera, one near each bottom corner (they sit out of focus)."""
    for o in S['fgc']: o.hide_render = True
    h = pos[2]
    if h > 0.30: return
    fx, fy = tgt[0] - pos[0], tgt[1] - pos[1]; n = math.hypot(fx, fy)
    if n < 1e-6: return
    fx, fy = fx / n, fy / n; rx, ry = fy, -fx
    d = 0.28 + 2.0 * max(0.0, h - 0.10); sc = 1.7 * d / 0.30
    for k, sd in zip(which, side):
        x = pos[0] + fx * d * (1.0 + 0.12 * sd) + rx * sd * 0.40 * d; y = pos[1] + fy * d * (1.0 + 0.12 * sd) + ry * sd * 0.40 * d
        o = S['fgc'][k]; o.hide_render = False; o.location = (x, y, gz(x, y) - 0.004); o.rotation_euler = (0, 0, 1.7 * k + 0.9 * sd); o.scale = (sc, sc, sc)

def build_dress(bpy, S, M, coll):
    """Everything that makes the table look lived in. Called once, after the props (it needs the lamp field)."""
    S['paths'] = [[(x, y) for x, y in W.TRACK_PTS], [(1.0, 1.05), (0.45, 0.88), (-0.25, 0.72), (-1.0, 0.74), (-1.7, 0.98), (-2.3, 1.22)], [(-3.2, 2.20), (-2.6, 2.05), (-1.9, 2.18), (-1.2, 2.35), (-0.5, 2.28)]]
    S['keepout'] = [(FIRE1[0], FIRE1[1], 0.08), (FIRE2[0], FIRE2[1], 0.10), (OASIS_R[0], OASIS_R[1], 0.30), (OASIS_L[0], OASIS_L[1], 0.24), (-1.85, 1.05, 0.12), (-2.72, 0.95, 0.30), (0.0, 0.35, 0.16), (0.0, 0.95, 0.30)]
    build_scatter(bpy, S, M, coll, (-4.0, 4.0, -0.7, 3.6), 170, 1100, 55, seed=5, name='sc')
    S['keepout'] = [(FIRE3[0], FIRE3[1], 0.10), (9.0, 1.25, 0.14), (9.0, 1.9, 0.5), (8.8, 1.9, 0.3), (9.4, 1.1, 0.5), (10.4, 1.35, 0.3)]
    build_scatter(bpy, S, M, coll, (6.7, 11.5, -0.6, 2.2), 50, 190, 12, seed=8, name='mc')
    # oases and palms
    S['oasisR'] = Oasis(bpy, 'oasR', coll, M, OASIS_R[0], OASIS_R[1], [(-0.18, 0.05, 0.36, (3, 4)), (0.12, 0.12, 0.30, (-4, 2)), (0.0, -0.10, 0.27, (5, -3)), (0.27, -0.02, 0.34, (-2, -6)), (-0.06, 0.18, 0.39, (2, 3))], rs_seed=3, r=0.17)
    S['oasisL'] = Oasis(bpy, 'oasL', coll, M, OASIS_L[0], OASIS_L[1], [(-0.15, 0.03, 0.33, (3, 5)), (0.12, 0.08, 0.28, (-4, 2)), (0.0, 0.17, 0.37, (2, -4))], rs_seed=4, r=0.12)
    S['mpalms'] = []
    for k, (x, y, h, ln) in enumerate(((7.15, 3.95, 0.36, (3, 2)), (8.55, 4.20, 0.40, (-2, 3)), (10.15, 3.95, 0.34, (4, -2)), (11.05, 3.65, 0.31, (-3, -3)), (6.95, 1.75, 0.30, (4, 1)), (11.15, 2.0, 0.33, (-4, 2)))):
        p = Palm(bpy, f'mp{k}', coll, M, h=h, lean=ln, seed=60 + k); p.place(x, y, 37 * k); S['mpalms'].append(p)
    S['fgpalms'] = []
    for k, (x, y, h, ln) in enumerate(((8.12, 0.78, 0.30, (0, 3)), (8.62, 0.78, 0.30, (0, -2)), (9.12, 0.78, 0.30, (0, 2)))):
        p = Palm(bpy, f'fp{k}', coll, M, h=h, lean=ln, seed=80 + k); p.place(x, y, 53 * k); S['fgpalms'].append(p)
    # camp props
    S['camp_props'] = []
    def P_(o): S['camp_props'].append(o); return o
    P_(tex_rug(bpy, 'rug_t1a', M['rug'], coll, 1.42, 1.34, 0.30, 0.16, 6, 1)); P_(tex_rug(bpy, 'rug_t1b', M['rug2'], coll, 1.12, 1.52, 0.18, 0.12, -24, 2)); P_(tex_rug(bpy, 'rug_t2', M['rug2'], coll, 2.35, 1.56, 0.30, 0.14, -4, 3))
    for k, (x, y, s, kind) in enumerate(((1.74, 1.40, 1.0, 'jar'), (1.80, 1.30, 0.8, 'jar'), (1.68, 1.31, 0.9, 'pot'), (2.62, 1.52, 1.0, 'jar'), (2.68, 1.60, 0.7, 'pot'), (0.72, 2.00, 1.0, 'jar'))):
        P_(pot_obj(bpy, f'pot{k}', M['pot'] if k % 2 == 0 else M['pot2'], coll, x, y, s, k, kind))
    P_(saddle_obj(bpy, 'saddle0', M, coll, 1.72, 1.82, 24, 1)); P_(saddle_obj(bpy, 'saddle1', M, coll, 2.68, 1.98, -30, 2)); P_(sack_obj(bpy, 'sack0', M, coll, 0.98, 1.92, 20, 1)); P_(sack_obj(bpy, 'sack1', M, coll, 1.14, 2.02, -35, 2)); P_(sack_obj(bpy, 'sack2', M, coll, 2.88, 1.42, 80, 3))
    for k, (x, y) in enumerate(W.CAMP[:5]):                                         # the families' tents each have a rug and a jar
        P_(tex_rug(bpy, f'rug_c{k}', M['rug2'] if k % 2 else M['rug'], coll, x + 0.02, y - 0.12, 0.17, 0.10, (k * 17) % 30 - 15, 10 + k))
        P_(pot_obj(bpy, f'potc{k}', M['pot'], coll, x + 0.15, y - 0.10, 0.8, k, 'jar'))
    S['fire1'] = Fire(bpy, 'fire1', coll, M, True, 1); S['fire1'].place(*FIRE1)
    S['fire2'] = Fire(bpy, 'fire2', coll, M, True, 2); S['fire2'].place(*FIRE2); S['fire2'].root.scale = (0.8, 0.8, 0.8)
    S['fire3'] = Fire(bpy, 'fire3', coll, M, True, 3); S['fire3'].place(*FIRE3)
    S['goats'] = [Goat(bpy, 'goat0', coll, M, 'a', 1), Goat(bpy, 'goat1', coll, M, 'b', 2), Goat(bpy, 'goat2', coll, M, 'a', 3)]
    S['drift'] = Drift(bpy, coll, M); build_fg(bpy, S, M, coll)
    S['walls'] = []
    for k in range(2):                                        # low mud walls Zayd and the girl walk behind (Mecca, 137 to 143 s)
        wl = ellipsoid(bpy, f'lowwall{k}', (0.080, 0.024, 0.088), M['wall'], coll, seg=24, rings=12, noise_amp=0.0008, noise_freq=45.0, seed=30 + k); wl.location = (9.0, 0.86, 0.0); wl.hide_render = True; S['walls'].append(wl)
    # Mecca extras: a stall with a striped awning and jars, banners on roofs, a well
    S['mecca_props'] = []
    def MP(o): S['mecca_props'].append(o); return o
    sx_, sy_ = 10.42, 1.62
    for dx in (-0.10, 0.10):
        MP(tube(bpy, f'stallpole{dx}', [(sx_ + dx, sy_ - 0.05, gz(sx_, sy_) - 0.002), (sx_ + dx, sy_ - 0.05, gz(sx_, sy_) + 0.06), (sx_ + dx, sy_ - 0.05, gz(sx_, sy_) + 0.09)], [0.0028, 0.0026, 0.0024], M['pole'], coll, n=8, ring=6, lateral=(1, 0, 0)))
        MP(tube(bpy, f'stallpolb{dx}', [(sx_ + dx, sy_ + 0.07, gz(sx_, sy_) - 0.002), (sx_ + dx, sy_ + 0.07, gz(sx_, sy_) + 0.06), (sx_ + dx, sy_ + 0.07, gz(sx_, sy_) + 0.075)], [0.0028, 0.0026, 0.0024], M['pole'], coll, n=8, ring=6, lateral=(1, 0, 0)))
    V, F = [], []
    for j in range(5):
        for i in range(11):
            u = i / 10 * 0.26 - 0.13; v = j / 4; V.append((sx_ + u, sy_ - 0.06 + 0.14 * v, gz(sx_, sy_) + 0.093 - 0.016 * v + 0.003 * math.sin(i * 1.3) * (1 - v)))
    for j in range(4):
        for i in range(10): a = j * 11 + i; F.append((a, a + 1, a + 12, a + 11))
    MP(raw_obj(bpy, 'awning', V, F, M['rug'], coll)); MP(tex_rug(bpy, 'rug_stall', M['rug2'], coll, sx_, sy_ + 0.01, 0.26, 0.12, 0, 5))
    for k, (dx, dy, kind, s) in enumerate(((-0.09, 0.0, 'jar', 1.0), (-0.05, 0.03, 'pot', 0.8), (0.02, 0.0, 'jar', 0.9), (0.08, 0.03, 'pot', 0.9), (0.11, -0.02, 'jar', 0.7))): MP(pot_obj(bpy, f'mpot{k}', M['pot'] if k % 2 else M['pot2'], coll, sx_ + dx, sy_ + dy, s, k, kind))
    S['flags'] = []
    for k, hi in enumerate((0, 3, 4, 7)):
        x, y, w, d, h = W.MECCA_HOUSES[hi][:5]; S['flags'].append(flag_obj(bpy, f'flag{k}', M, coll, x + w * 0.5, y - 0.02, gz(x, y) + h + 0.008, 0.06 + 0.01 * (k % 2)))
    for k, (x, y, yaw) in enumerate(((7.72, 1.62, 25.0), (7.55, 1.52, -40.0))): MP(sack_obj(bpy, f'msack{k}', M, coll, x, y, yaw, k))
    MP(tex_rug(bpy, 'rug_m1', M['rug'], coll, 9.78, 1.42, 0.28, 0.15, 8, 7)); MP(tex_rug(bpy, 'rug_m2', M['rug2'], coll, 8.20, 1.50, 0.22, 0.12, -12, 8))

def animate_dress(S, t, hit=0.0, show_fire=(), wind=(0.9, 0.25)):
    """Per-pose motion of the living things that are visible (the rest are hidden by the shot)."""
    sway_tufts(S, 'sc', t); sway_tufts(S, 'mc', t, amp=0.005)
    S['oasisR'].animate(t); S['oasisL'].animate(t)
    for p in S['mpalms'] + S['fgpalms']: p.sway(t)
    for k, nm in enumerate(('fire1', 'fire2', 'fire3')):
        if nm in show_fire: S[nm].animate(t + k * 1.7, hit, 1.0, wind)
    for k, f in enumerate(S['flags']): sway_flag(f, t, seed=0.9 * k)
