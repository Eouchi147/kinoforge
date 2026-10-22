"""The six sets of "Why Venice Sinks", each a Cutaway block at the origin (only one is visible per shot).

    city    Venice: canals, palazzi, a campanile on a campo, Santa Maria della Salute, gondolas; poles on the cut faces
    lagoon  the empty lagoon 1,500 years ago: mud flats, reeds, a strip of sand, boats arriving; a stone house that sinks
    site    a building site: poles driven down by pile drivers, then boards, white stone and brick walls built up
    pole    one pole deep in the mud, close: no air down there; it turns stony grey
    sink    a diagram block: mud squeezed, the sea rising on a gauge, a factory pumping groundwater, then stopping
    inlet   a lagoon inlet: the MOSE gates on the seabed fill with air and swing up; the sea outside rises, the lagoon stays

Each builder returns a Set: its objects (shown or hidden per shot), its land, and update(t, shot) for its own animation.
Everything is a pure function of the film time t and the shot, so any frame renders alone (free runners, in parallel).
"""
import math
import numpy as np
import cutaway as cw
import arch

LV = -0.05                       # the lagoon's water level (block coordinates, metres)
DEPTH = 1.3
# lagoon mud strata: grey silt and mud, the pale firm clay band (the caranto), sand, deep clay
VZ_STRATA = [('fill', 0.04, (0.50, 0.46, 0.40), 0.15), ('silt', 0.14, (0.52, 0.50, 0.46), 0.02), ('mud', 0.32, (0.40, 0.39, 0.36), 0.03),
             ('caranto', 0.12, (0.80, 0.71, 0.50), 0.05), ('sand', 0.20, (0.62, 0.56, 0.44), 0.35), ('deep', 1.0, (0.44, 0.38, 0.32), 0.12)]
CARANTO_SD = (0.50, 0.62)
WOOD_POLE = (0.72, 0.54, 0.33)
WATER_TINT = (0.30, 0.66, 0.62)


def smoothstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= a); return u * u * (3 - 2 * u)


class Set:
    def __init__(self, name):
        self.name = name; self.objs = []; self.land = None; self.update = lambda t, shot: None; self.data = {}; self.lights = []


def vsock(mat, label):
    """The output socket of the Value node with this label in a material (the film animates it)."""
    return [n for n in mat.node_tree.nodes if n.type == 'VALUE' and n.label == label][0].outputs[0]


def _track(bpy):
    return set(o.name for o in bpy.data.objects)


def _zmean(land):
    sx, sy = land.size; X, Y = np.meshgrid(np.linspace(-sx / 2, sx / 2, 90), np.linspace(-sy / 2, sy / 2, 90))
    return float(np.mean(land.height(X, Y)))


def strata_z(zt, zmean, sd_target):
    """Height where the kit's strata coordinate reaches sd_target below a local top zt (bisection on the kit's formula)."""
    lo, hi = zt - 3.0, zt
    for _ in range(40):
        z = (lo + hi) / 2; dt = zt - z; w = max(0.0, 1 - dt / 0.7); sd = dt * w + (zmean - z) * (1 - w)
        if sd > sd_target: lo = z
        else: hi = z
    return (lo + hi) / 2


def _path_samples(path, step):
    P = cw.catmull(path, 400); seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    out = []
    for q in np.arange(0, s[-1], step):
        i = int(np.searchsorted(s, q) - 1); i = max(0, min(i, len(P) - 2)); u = (q - s[i]) / max(seg[i], 1e-9)
        p = P[i] + (P[i + 1] - P[i]) * u; t = (P[i + 1] - P[i]) / max(seg[i], 1e-9); out.append((q, p, t))
    return out, s[-1]


def _path_at(path_pts, q):
    P = path_pts['P']; s = path_pts['s']; i = int(np.searchsorted(s, q) - 1); i = max(0, min(i, len(P) - 2)); seg = s[i + 1] - s[i]
    u = (q - s[i]) / max(seg, 1e-9); p = P[i] + (P[i + 1] - P[i]) * u; t = (P[i + 1] - P[i]) / max(seg, 1e-9); return p, t


def _path_table(path):
    P = cw.catmull(path, 400); seg = np.linalg.norm(np.diff(P, axis=0), axis=1); return {'P': P, 's': np.concatenate([[0], np.cumsum(seg)])}


def _yaw_facing(d):
    """yaw so that a building's facade (local -Y) faces direction d (x, y)."""
    return math.atan2(d[0], -d[1])


def grid(land, res=0.008):
    """Precompute the land's depth below the water level on a grid (fast lookups while placing buildings)."""
    sx, sy = land.size; xs = np.arange(-sx / 2, sx / 2 + res / 2, res); ys = np.arange(-sy / 2, sy / 2 + res / 2, res)
    X, Y = np.meshgrid(xs, ys); land._grid = (xs[0], ys[0], res, land.field(X, Y)['depth'], land.height(X, Y))


def _look(land, x, y, k=3):
    x0, y0, res = land._grid[:3]; A = land._grid[k]
    i = int(round((y - y0) / res)); j = int(round((x - x0) / res)); i = min(max(i, 0), A.shape[0] - 1); j = min(max(j, 0), A.shape[1] - 1)
    return float(A[i, j])


def _on_land(land, x, y, margin=0.0, need=0.012):
    sx, sy = land.size
    if abs(x) >= sx / 2 - margin or abs(y) >= sy / 2 - margin: return False
    if getattr(land, '_grid', None) is not None: return _look(land, x, y) < -need
    F = land.field(np.array([x]), np.array([y])); return F['depth'][0] < -need


def _footprint_ok(land, x, y, w, d, yaw, taken, keep, margin=0.04):
    c, s = math.cos(yaw), math.sin(yaw)
    for a in (-0.5, 0.5, 0.0):
        for b in (-0.5, 0.5, 0.0):
            px = x + a * w * c - b * d * s; py = y + a * w * s + b * d * c
            if not _on_land(land, px, py, margin): return False
    r = 0.5 * math.hypot(w, d)
    for (kx, ky, kr) in keep:
        if math.hypot(x - kx, y - ky) < kr + r * 0.8: return False
    for (tx, ty, tr) in taken:
        if math.hypot(x - tx, y - ty) < (tr + r) * 0.78: return False
    return True


class Lamps:
    """Lamp posts whose heads and lights switch on at dusk (the film sets level 0..1)."""
    def __init__(self, kit):
        self.kit = kit; bpy = kit.bpy; m = cw._new_mat(bpy, 'vz_lamphead'); g = cw.G(m.node_tree, kit)
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': cw.srgb((0.85, 0.82, 0.70)), 'Roughness': 0.3})
        g.put(p, 'Emission Color', cw.srgb((1.0, 0.74, 0.42))); g.put(p, 'Emission Strength', 0.0); cw._finish(g, p)
        self.mat = m; self.sock = cw._sock(p.inputs, 'Emission Strength'); self.lights = []
        self.iron = cw.mat_simple(kit, 'vz_iron', (0.07, 0.07, 0.08), 0.5)

    def add(self, land, x, y, h=0.05, name='vz_lamp'):
        bpy = self.kit.bpy; A = cw._Acc(); v, f = cw._tube([(0, 0, 0), (0, 0, h)], [0.0018, 0.0014], 6); A.add(v, f, 0)
        V0, F0 = cw._icosphere(1); A.add(V0 * 0.005 + np.array([0, 0, h + 0.003]), F0, 1)
        ob = A.build(bpy, name, [self.iron, self.mat], True, self.kit.coll); cw._place(land, ob, x, y)
        ld = bpy.data.lights.new(name + '_l', 'POINT'); ld.energy = 0.0; ld.color = (1.0, 0.72, 0.42); ld.shadow_soft_size = 0.01
        lo = bpy.data.objects.new(name + '_l', ld); self.kit.coll.objects.link(lo); lo.location = (ob.location.x, ob.location.y, ob.location.z + h + 0.01)
        self.lights.append(ld); return ob

    def level(self, v, stagger=None):
        self.sock.default_value = 14.0 * v
        for k, ld in enumerate(self.lights): ld.energy = 0.08 * v


# ================================================================================================= city
def build_city(kit, M, lamps):
    bpy = kit.bpy; S = Set('city'); before = _track(bpy)
    canal_path = [(-0.75, -2.7), (-0.45, -1.5), (0.1, -0.62), (0.9, 0.02), (1.7, 0.33), (2.7, 0.45)]
    rio1 = [(-2.7, -0.05), (-1.7, -0.32), (-1.0, -0.78), (-0.42, -1.12)]
    rio2 = [(0.72, 2.7), (0.95, 1.6), (0.86, 0.62), (0.62, -0.02)]
    def lag(x, y): return np.minimum(1.62 - y, x + 1.62) + 0.03 * cw.fbm(x, y, 4, 2, 2.0)
    water = [cw.river(canal_path, width=0.44, depth=0.24, level=LV, shelf=0.10), cw.river(rio1, width=0.15, depth=0.14, level=LV, shelf=0.05),
             cw.river(rio2, width=0.15, depth=0.14, level=LV, shelf=0.05), cw.basin(lag, depth=0.20, level=LV, shelf=0.25)]
    top = lambda x, y: -0.022 + 0.002 * cw.fbm(x, y, 9, 2, 3.0)
    campo = (-0.52, 0.42); campo_r = 0.30
    def zones(x, y, h):
        return {'rock': np.ones_like(x)}
    land = cw.block(kit, size=(4.0, 4.0), depth=DEPTH, strata=VZ_STRATA, top=top, water=water, seed=21, zones=zones, grass=0, trees=0,
                    boulders=0, flowers=0, under=True, water_tint=WATER_TINT, water_density=2.4, name='city')
    S.land = land; zm = _zmean(land); grid(land)
    keep = [(1.62, -1.58, 0.44), (campo[0], campo[1], campo_r)]
    taken = []
    # Santa Maria della Salute at the front corner, its temple front towards the Grand Canal
    sal = arch.salute(kit, M, 1.60, -1.56, -0.022, s=1.25, yaw=math.radians(-135), name='vz_salute'); S.data['salute'] = sal
    # the campo: a church, the campanile, a well head, people
    arch.campanile(kit, M, campo[0] + 0.24, campo[1] + 0.32, -0.022, h=0.56, w=0.07)
    arch.church(kit, M, campo[0] - 0.22, campo[1] + 0.36, -0.022, w=0.15, d=0.26, h=0.15, yaw=0.0)
    taken += [(campo[0] + 0.24, campo[1] + 0.32, 0.06), (campo[0] - 0.22, campo[1] + 0.36, 0.16)]
    well = cw.mk_mesh(bpy, 'vz_well', *arch._revolve([(0.016, -0.02), (0.016, 0.012), (0.019, 0.016), (0.012, 0.016)], 16), [M.get('stone', arch.STONE, 0.6, 0.05, 0.1)], None, True, kit.coll)
    well.location = (campo[0] + 0.05, campo[1] - 0.05, -0.022)
    # palazzi along the Grand Canal, facades to the water, then the islands filled
    tab = _path_table(canal_path); samples, Lc = _path_samples(canal_path, 0.01); rng = np.random.default_rng(5)
    k = 0
    for side in (-1, 1):
        q = 0.15
        while q < Lc - 0.1:
            p, t = _path_at(tab, q); n = np.array([-t[1], t[0]]) * side
            w = float(rng.uniform(0.15, 0.24)); d = float(rng.uniform(0.13, 0.18)); h = float(rng.uniform(0.11, 0.19))
            c = p + n * (0.22 + 0.035 + d / 2); yaw = _yaw_facing(-n)
            if _footprint_ok(land, c[0], c[1], w, d, yaw, taken, keep):
                arch.palazzo(kit, M, c[0], c[1], -0.022, w, d, h, yaw, seed=k, name=f'vz_pal{k}'); taken.append((c[0], c[1], 0.5 * math.hypot(w, d))); k += 1
                q += w + float(rng.uniform(0.0, 0.02))
            else: q += 0.04
    # the rest of the islands
    tries = 0
    while tries < 1600 and k < 95:
        tries += 1; x, y = rng.uniform(-1.9, 1.9, 2); w = float(rng.uniform(0.14, 0.24)); d = float(rng.uniform(0.12, 0.18)); h = float(rng.uniform(0.10, 0.17))
        yaw = float(rng.choice([0, math.pi / 2, math.pi, -math.pi / 2])) + float(rng.normal(0, 0.05))
        if _footprint_ok(land, x, y, w, d, yaw, taken, keep):
            arch.palazzo(kit, M, x, y, -0.022, w, d, h, yaw, seed=k + 100, water_door=False, name=f'vz_pal{k}'); taken.append((x, y, 0.5 * math.hypot(w, d))); k += 1
    S.data['n_palazzi'] = k
    # bridges: a white stone arch over the Grand Canal, small ones over the rios
    stone = (0.88, 0.86, 0.80)
    cw.bridge(kit, land, (-0.30, -0.46), (0.28, -0.95), width=0.07, arch=0.07, color=stone, name='vz_rialto')
    cw.bridge(kit, land, (-1.08, -0.62), (-0.90, -0.95), width=0.04, arch=0.03, color=stone, name='vz_br1')
    cw.bridge(kit, land, (0.74, 0.95), (1.05, 1.05), width=0.04, arch=0.03, color=stone, name='vz_br2')
    # lamps along the canal banks (dark by day, warm at dusk)
    for j, q in enumerate(np.linspace(0.5, Lc - 0.5, 14)):
        p, t = _path_at(tab, q); n = np.array([-t[1], t[0]]) * (1 if j % 2 else -1); c = p + n * 0.245
        if _on_land(land, c[0], c[1], 0.05, 0.005): lamps.add(land, c[0], c[1], name=f'vz_lamp{j}')
    # boats: gondolas both ways along the canal, a few small boats moored
    boats = []
    for j, (q0, v, off) in enumerate([(0.7, 0.020, -0.07), (3.6, -0.018, 0.08), (1.8, 0.016, 0.03), (4.4, -0.020, -0.05)]):
        g, parts = arch.gondola(kit, M, name=f'vz_gon{j}'); boats.append((g, q0, v, off, bpy.data.objects[g['oar']] if 'oar' in g else None))
    for j, q in enumerate([1.2, 2.6, 3.3]):
        p, t = _path_at(tab, q); n = np.array([-t[1], t[0]]); c = p + n * 0.18 * (1 if j % 2 else -1)
        b, parts = arch.boat(kit, M, (0.40, 0.30, 0.20) if j % 2 else (0.22, 0.30, 0.42), 0.06, 0, f'vz_moor{j}', j)
        b.location = (c[0], c[1], LV - 0.004); b.rotation_euler = (0, 0, math.atan2(t[1], t[0]))
    # people on the campo
    walkers = []
    for j in range(9):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.04, 0.22); col = arch.PASTELS[j % len(arch.PASTELS)]
        f = arch.figure(kit, M, (col[0] * 0.55, col[1] * 0.5, col[2] * 0.6), 0.03, f'vz_walk{j}')
        walkers.append((f, campo[0] + r * math.cos(a), campo[1] + r * math.sin(a) - 0.05, rng.uniform(0, 2 * math.pi), rng.uniform(0.006, 0.012)))
    # the high-water walkways across the campo (shown only in the flood)
    ww = [arch.walkway(kit, M, (campo[0] - 0.28, campo[1] - 0.18), (campo[0] + 0.26, campo[1] - 0.10), -0.022, name='vz_ww0'),
          arch.walkway(kit, M, (campo[0] - 0.05, campo[1] - 0.32), (campo[0] - 0.02, campo[1] + 0.18), -0.022, name='vz_ww1')]
    wwalkers = []
    for j in range(6):
        f = arch.figure(kit, M, [(0.20, 0.28, 0.45), (0.45, 0.20, 0.18), (0.25, 0.35, 0.25), (0.35, 0.30, 0.42), (0.50, 0.40, 0.22), (0.18, 0.18, 0.22)][j], 0.03, f'vz_wwalk{j}')
        wwalkers.append((f, j))
    # poles and the stone foundation drawn on the two front cut faces (dense under the Salute)
    pole_m = arch.mat_pole_section(kit, 'vz_polecut_city', WOOD_POLE); board_m = arch.mat_band(kit, 'vz_board', (0.30, 0.20, 0.12), 0.4)
    stone_m = arch.mat_band(kit, 'vz_stoneband', (0.90, 0.88, 0.82), 0.2)
    P, B, St = [], [], []
    for face in ('-Y', '+X'):
        s = -1.99
        while s < 1.99:
            x, y = (s, -1.995) if face == '-Y' else (1.995, s)
            dense = (face == '-Y' and 1.18 < s < 1.99) or (face == '+X' and -1.99 < s < -1.12)
            step = 0.0135 if dense else 0.022; half = 0.0042 if dense else 0.005
            if _on_land(land, x, y, 0.0, 0.016):
                zt = float(land.height(np.array([x]), np.array([y]))[0]); zc = strata_z(zt, zm, CARANTO_SD[0] + 0.035)
                P.append(arch.face_quad(face, s, zc, zt - 0.03, half, 4.0, 4.0))
                P[-1][0] = list(P[-1][0]); P[-1][1] = list(P[-1][1])
                mid = (np.array(P[-1][0]) + np.array(P[-1][1])) / 2; P[-1][0] = tuple(mid + (np.array(P[-1][0]) - mid) * 0.25); P[-1][1] = tuple(mid + (np.array(P[-1][1]) - mid) * 0.25)
                B.append(arch.face_quad(face, s + step / 2, zt - 0.03, zt - 0.021, step / 2 + 0.0002, 4.0, 4.0, 0.0014))
                St.append(arch.face_quad(face, s + step / 2, zt - 0.021, zt + 0.0005, step / 2 + 0.0002, 4.0, 4.0, 0.0014))
            s += step
    for nm, Q, m in (('vz_cityposes', P, pole_m), ('vz_cityboards', B, board_m), ('vz_citystone', St, stone_m)):
        ob = arch.section_mesh(kit, nm, m, len(Q)); arch.set_quads(ob, Q)
    S.data['pole_mat'] = pole_m
    cw.birds(kit, 4, center=(0.2, 0.3), radius=2.0, height=1.0, seed=12, size=0.035, color=(0.92, 0.92, 0.94))
    water_ob = land.objects['water']; base = np.array([v.co[:] for v in water_ob.data.vertices])
    S.data['water_base'] = base

    def set_level(dz):
        V = base.copy(); V[4:, 2] = LV + dz; water_ob.data.vertices.foreach_set('co', V.astype(np.float32).reshape(-1)); water_ob.data.update()

    def update(t, shot):
        st = shot.get('city', {})
        flood = st.get('flood', 0.0); set_level(flood(t) if callable(flood) else flood)
        for g, q0, v, off, oar in boats:
            q = min(Lc - 0.3, max(0.3, q0 + v * t)); p, tt = _path_at(tab, q); n = np.array([-tt[1], tt[0]])
            c = p + n * off; d = tt * (1 if v > 0 else -1)
            g.location = (c[0], c[1], LV - 0.003 + 0.0015 * math.sin(t * 1.7 + q0)); g.rotation_euler = (0.03 * math.sin(t * 1.3 + q0), 0, math.atan2(d[1], d[0]))
            if oar: oar.rotation_euler = (0, 0.35 * math.sin(t * 2.2 + q0), 0.3 * math.sin(t * 1.1 + q0))
        show_walk = st.get('walkways', False)
        for o in ww: o.hide_render = not show_walk
        for f, x0, y0, a0, sp in walkers:
            f.hide_render = show_walk
            a = a0 + sp * t * 6; x = x0 + 0.05 * math.cos(a); y = y0 + 0.05 * math.sin(a)
            f.location = (x, y, -0.021 + 0.0012 * abs(math.sin(t * 7 + a0))); f.rotation_euler = (0, 0, a + math.pi / 2)
        for f, j in wwalkers:
            f.hide_render = not show_walk
            if show_walk:
                a, b = ((campo[0] - 0.28, campo[1] - 0.18), (campo[0] + 0.26, campo[1] - 0.10)) if j < 4 else ((campo[0] - 0.05, campo[1] - 0.32), (campo[0] - 0.02, campo[1] + 0.18))
                u = ((j * 0.27 + t * 0.016) % 1.0) if j % 2 == 0 else (1 - (j * 0.31 + t * 0.016) % 1.0)
                x = a[0] + (b[0] - a[0]) * u; y = a[1] + (b[1] - a[1]) * u
                f.location = (x, y, -0.022 + 0.034 + 0.0012 * abs(math.sin(t * 7 + j))); f.rotation_euler = (0, 0, math.atan2(b[1] - a[1], b[0] - a[0]) + (0 if j % 2 == 0 else math.pi) + math.pi / 2)
    S.update = update
    S.objs = [bpy.data.objects[n] for n in _track(bpy) - before]
    S.data['campo'] = campo; S.data['zmean'] = zm
    return S


# ================================================================================================= lagoon, 1,500 years ago
def build_lagoon(kit, M):
    bpy = kit.bpy; S = Set('lagoon'); before = _track(bpy)
    # mud flats (barene) as low islands, a long strip of sand at the back with the sea beyond it
    islands = [(0.55, -1.72, 0.55, 0.42), (-0.9, -0.5, 0.45, 0.30), (0.6, 0.35, 0.40, 0.25), (-1.4, 0.8, 0.30, 0.22), (1.5, -0.4, 0.28, 0.20)]
    def fn(x, y):
        d = np.full(np.shape(x), 9.0)
        for (cx, cy, rx, ry) in islands:
            q = np.hypot((x - cx) / rx, (y - cy) / ry) + 0.12 * cw.fbm(x, y, 7, 3, 2.5); d = np.minimum(d, (q - 1) * min(rx, ry))
        strip = np.abs(y - 1.45 - 0.08 * np.sin(x * 1.3)) - 0.17 + 0.02 * cw.fbm(x, y, 3, 2, 3.0)
        return -np.minimum(d, strip)          # negative where water
    def top(x, y):
        dune = 0.035 * np.exp(-((y - 1.45 - 0.08 * np.sin(x * 1.3)) / 0.10) ** 2) * (0.7 + 0.3 * cw.fbm(x, y, 5, 3, 2.0))
        return -0.032 + 0.006 * cw.fbm(x, y, 2, 3, 2.0) + dune
    def zones(x, y, h):
        strip = np.abs(y - 1.45 - 0.08 * np.sin(x * 1.3))
        sand = cw.smooth(0.2, 0.08, strip); return {'sand': sand, 'path': (1 - sand) * 0.35}
    land = cw.block(kit, size=(4.0, 4.0), depth=DEPTH, strata=VZ_STRATA, top=top, water=[cw.basin(fn, depth=0.16, level=LV, shelf=0.3)],
                    seed=31, zones=zones, grass=0.55, grass_height=0.8, trees=0, boulders=0, flowers=0.0, under=True, reeds=0.9,
                    water_tint=WATER_TINT, water_density=2.4, name='lagoon')
    S.land = land; zm = _zmean(land)
    # boats of the first settlers arriving from the left, slowing to a stop at the mud flats
    rng = np.random.default_rng(3); boats = []
    for j, (y0, x1, delay) in enumerate([(-1.05, -0.12, 0.0), (-0.85, -0.35, 1.6), (-1.25, 0.02, 3.1)]):
        b, parts = arch.boat(kit, M, (0.42, 0.32, 0.22), 0.09, 2 + (j % 2), f'vz_lboat{j}', j + 7); boats.append((b, y0, x1, delay))
    # the stone house on the mud flat at the front face (it sinks in shot 2b)
    hx, hy = 0.62, -2.0 + 0.065 - 0.0015
    house = cw.house(kit, land, hx, hy, w=0.20, d=0.13, h=0.12, roof=0.08, yaw=0.0, wall=(0.86, 0.84, 0.78), roof_col=(0.55, 0.30, 0.20), name='vz_sinkhouse')
    z0 = house.location.z; S.data['house'] = house
    ring_m = cw.mat_simple(kit, 'vz_mudring', (0.30, 0.26, 0.20), 0.9)
    ring = cw.mk_mesh(bpy, 'vz_mudring', *arch._revolve([(0.15, 0.0), (0.135, 0.004), (0.12, 0.0)], 28), [ring_m], None, True, kit.coll)
    ring.location = (hx, hy + 0.065, z0 - 0.002); ring.scale = (1.0, 0.7, 1.0)
    cw.birds(kit, 3, center=(0.0, 0.2), radius=2.0, height=0.9, seed=4, size=0.035, color=(0.92, 0.92, 0.94))

    def update(t, shot):
        st = shot.get('lagoon', {})
        arrive = st.get('arrive')           # film time when the boats set off
        for b, y0, x1, delay in boats:
            if arrive is None: b.hide_render = True; continue
            b.hide_render = False; u = smoothstep(0, 9.0, t - arrive - delay); x = -2.0 + 0.12 + (x1 + 1.88) * (1 - (1 - u) ** 2)
            b.location = (x, y0, LV - 0.004 + 0.0015 * math.sin(t * 1.5 + y0 * 9)); b.rotation_euler = (0.02 * math.sin(t * 1.2 + delay), 0, 0.05 * math.sin(t * 0.3 + delay))
            b.hide_render = (t - arrive - delay) < 0
        sink = st.get('sink')               # (t_start, duration)
        house.hide_render = sink is None; ring.hide_render = sink is None
        if sink is not None:
            u = smoothstep(sink[0], sink[0] + sink[1], t); d = 0.09 * (u ** 1.3)
            house.location.z = z0 - d; house.rotation_euler = (0.0, math.radians(5.5) * u, 0.0)
            ring.scale = (1.0 + 0.5 * u, 0.7 + 0.35 * u, 1.0); ring.location.z = z0 - 0.002 - 0.006 * u
    S.update = update
    S.objs = [bpy.data.objects[n] for n in _track(bpy) - before]
    S.data['zmean'] = zm
    return S


# ================================================================================================= building site
SITE_X = (0.52, 2.0); SITE_Y = (-2.0, -0.52); PIT_Z = -0.12; POLE_R = 0.021; POLE_SP = 0.062


def build_site(kit, M):
    bpy = kit.bpy; S = Set('site'); before = _track(bpy)
    def pit(x, y):
        bx = cw.smooth(SITE_X[0] - 0.05, SITE_X[0] + 0.02, x) * cw.smooth(SITE_Y[1] + 0.05, SITE_Y[1] - 0.02, y); return bx
    top = lambda x, y: -0.02 + 0.004 * cw.fbm(x, y, 3, 3, 2.0) + (PIT_Z + 0.02) * pit(x, y)
    def zones(x, y, h):
        work = cw.smooth(1.9, 1.2, np.hypot(x - 1.1, y + 1.1)); return {'path': np.maximum(work, pit(x, y))}
    land = cw.block(kit, size=(4.0, 4.0), depth=DEPTH, strata=VZ_STRATA, top=top, water=None, seed=41, zones=zones, grass=0.8, grass_height=0.8,
                    trees=5, tree_kinds=('round', 'tall'), boulders=4, flowers=0.2, name='site')
    S.land = land; zm = _zmean(land)
    pole_m = cw.mat_simple(kit, 'vz_polewood', WOOD_POLE, 0.8, noise_amt=0.3, bump=0.3); sec_m = arch.mat_pole_section(kit, 'vz_polecut_site', WOOD_POLE)
    zc = strata_z(-0.02, zm, CARANTO_SD[0] + 0.04); L = PIT_Z - zc        # poles reach into the pale clay band
    xs = np.arange(SITE_X[0] + 0.05, SITE_X[1] - 0.01, POLE_SP); ys = np.arange(SITE_Y[0] + 0.03, SITE_Y[1] - 0.04, POLE_SP)
    poles = []
    V, F = cw._tube([(0, 0, -L), (0, 0, -L + 0.05), (0, 0, 0)], [0.003, POLE_R, POLE_R], 12)
    me = bpy.data.meshes.new('vz_pole'); me.from_pydata([tuple(v) for v in V], [], F); me.materials.append(pole_m)
    for p in me.polygons: p.use_smooth = True
    # driving order: the front row along the -Y face first (the hero pole near the corner), then row by row
    order = []
    for j, y in enumerate(ys):
        for i, x in enumerate(xs[::-1]): order.append((x, y, i, j))
    for k, (x, y, i, j) in enumerate(order):
        ob = bpy.data.objects.new(f'vz_pole{k}', me); kit.coll.objects.link(ob); ob.location = (x, y, PIT_Z)
        poles.append({'ob': ob, 'x': x, 'y': y, 'i': i, 'j': j, 'k': k})
    S.data['poles'] = poles; S.data['L'] = L; S.data['zc'] = zc
    # pole sections on the cut faces: the front row on -Y, the last column on +X
    face_poles = [p for p in poles if p['j'] == 0] + [p for p in poles if p['i'] == 0 and p['j'] > 0]
    sec = arch.section_mesh(kit, 'vz_sitesec', sec_m, len(face_poles))
    # pile drivers with a worker each
    rigs = []
    for r in range(3):
        rig, wt = arch.pile_driver(kit, M, 0, 0, 0, name=f'vz_rig{r}'); wk = arch.figure(kit, M, [(0.55, 0.25, 0.18), (0.25, 0.32, 0.50), (0.42, 0.40, 0.22)][r], 0.032, f'vz_worker{r}')
        rigs.append((rig, wt, wk))
    # a stack of logs waiting, two more workers
    logs = cw._Acc(); rng = np.random.default_rng(8)
    for row in range(3):
        for c in range(6 - row):
            y0 = -0.95 + (c + row * 0.5) * 0.045; z0 = 0.022 + row * 0.038
            v, f = cw._tube([(-0.95, y0, z0), (-0.55 + rng.uniform(-0.03, 0.03), y0, z0)], [0.02, 0.02], 10); logs.add(v, f)
    lg = logs.build(bpy, 'vz_logs', [pole_m], True, kit.coll); lg.location = (0, 0, -0.02)
    for r, (x, y) in enumerate([(-0.45, -0.7), (-0.6, -1.25)]):
        f = arch.figure(kit, M, [(0.30, 0.30, 0.40), (0.50, 0.32, 0.22)][r], 0.032, f'vz_sitewk{r}'); cw._place(land, f, x, y); f.rotation_euler = (0, 0, r * 2.0)
    # boards (in rows), white stone (in rows), brick walls (rising), all reaching the cut faces
    board_m = cw.mat_simple(kit, 'vz_boards', (0.48, 0.34, 0.20), 0.8, noise_amt=0.35, bump=0.3)
    stone_m = cw.mat_simple(kit, 'vz_istrian', (0.92, 0.90, 0.85), 0.6, noise_amt=0.06, bump=0.15)
    brick_m = cw.mat_simple(kit, 'vz_brick', arch.BRICK, 0.85, noise_amt=0.25, bump=0.35)
    x0, x1, y0, y1 = SITE_X[0] + 0.01, SITE_X[1] + 0.0012, SITE_Y[0] - 0.0012, SITE_Y[1] - 0.01
    nb = 14; boards = []
    for r in range(nb):
        A = cw._Acc(); ya = y1 - (y1 - y0) * (r + 1) / nb; yb = y1 - (y1 - y0) * r / nb
        for c in range(6):
            xa = x0 + (x1 - x0) * c / 6; xb = x0 + (x1 - x0) * (c + 1) / 6 - 0.003
            v, f = cw._box(xa, ya + 0.0015, PIT_Z, xb, yb - 0.0015, PIT_Z + 0.016); A.add(v, f)
        boards.append(A.build(bpy, f'vz_boardrow{r}', [board_m], False, kit.coll))
    stones = []
    for r in range(10):
        A = cw._Acc(); ya = y1 - (y1 - y0) * (r + 1) / 10; yb = y1 - (y1 - y0) * r / 10
        for c in range(7):
            off = 0.5 if r % 2 else 0.0; xa = x0 + (x1 - x0) * (c + off - 0.5) / 7; xb = xa + (x1 - x0) / 7 - 0.003; xa = max(xa, x0); xb = min(xb, x1)
            if xb - xa < 0.02: continue
            v, f = cw._box(xa, ya + 0.002, PIT_Z + 0.016, xb, yb - 0.002, PIT_Z + 0.05); A.add(v, f)
        stones.append(A.build(bpy, f'vz_stonerow{r}', [stone_m], False, kit.coll))
    wall_t = 0.05; WH = 0.42; walls = []
    for nm, (a, b, c, d) in {'S': (x0, y0, x1, y0 + wall_t), 'E': (x1 - wall_t, y0, x1, y1), 'N': (x0, y1 - wall_t, x1, y1), 'W': (x0, y0, x0 + wall_t, y1)}.items():
        A = cw._Acc(); v, f = cw._box(a, b, 0.0, c, d, 1.0); A.add(v, f)
        ob = A.build(bpy, f'vz_wall{nm}', [brick_m], False, kit.coll); ob.location = (0, 0, PIT_Z + 0.05); walls.append(ob)
    S.data.update(boards=boards, stones=stones, walls=walls)

    def pole_state(p, t, stage, tl):
        """(visible, head z) of a pole for the shot's stage."""
        k = p['k']; rise = 0.34
        if stage == 'one':
            if k > 0: return False, PIT_Z
            hits = max(0.0, (tl + 3.0) / 1.15); n = int(hits); frac = hits - n
            drop = n + smoothstep(0.86, 1.0, frac); return True, PIT_Z + rise * max(0.0, 1 - drop / 12.0)
        if stage == 'many':
            front = 0.55 * len(poles) + tl * 1.2          # later the same day: more than half are in, three rigs working
            if k < front - 3: return True, PIT_Z
            if k < front: return True, PIT_Z + rise * max(0.0, 1 - (front - k) / 3.0)
            return False, PIT_Z
        return True, PIT_Z

    def update(t, shot):
        st = shot.get('site', {}); stage = st.get('stage', 'done'); tl = t - shot['t0']
        quads = []
        for p in poles:
            vis, zh = pole_state(p, t, stage, tl); p['ob'].hide_render = not vis; p['ob'].location.z = zh; p['zh'] = zh if vis else None
        for p in face_poles:
            zh = p['zh']
            if zh is None: quads.append([(0, 0, -5)] * 4); continue
            face, s = ('-Y', p['x']) if p['j'] == 0 else ('+X', p['y'])
            zt = min(zh, PIT_Z); zb = zh - L
            q = arch.face_quad(face, s, zb, zt, POLE_R * 0.95, 4.0, 4.0); mid = (np.array(q[0]) + np.array(q[1])) / 2
            q[0] = tuple(mid + (np.array(q[0]) - mid) * 0.2); q[1] = tuple(mid + (np.array(q[1]) - mid) * 0.2); quads.append(q)
        arch.set_quads(sec, quads)
        # rigs over the poles being driven
        driving = [p for p in poles if p['zh'] is not None and p['zh'] > PIT_Z + 0.002][:3] if stage in ('one', 'many') else []
        for r, (rig, wt, wk) in enumerate(rigs):
            if r < len(driving):
                p = driving[r]; rig.hide_render = wt.hide_render = wk.hide_render = False
                rig.location = (p['x'], p['y'], PIT_Z); ph = ((tl + 3.0) / 1.15 + r * 0.37) % 1.0
                lift = 0.12 * smoothstep(0.0, 0.8, ph) if ph < 0.86 else 0.12 * (1 - smoothstep(0.86, 0.95, ph))
                wt.location = (p['x'], p['y'], p['zh'] + 0.002 + lift); wk.location = (p['x'] - 0.09, p['y'] + 0.05, PIT_Z + 0.002 * math.sin(ph * 6.28))
                wk.rotation_euler = (0.25 * smoothstep(0.0, 0.8, ph) if ph < 0.86 else 0.0, 0, -0.6)
            else: rig.hide_render = wt.hide_render = wk.hide_render = True
        # the foundation built up (l06): boards row by row, then stone, then the walls rise
        b = st.get('build')
        if b is None:
            for o in boards + stones + walls: o.hide_render = True
        else:
            t_b, t_s, t_w, t_end = b
            for r, o in enumerate(boards):
                ta = t_b + (t_s - t_b) * r / len(boards) * 0.9; u = smoothstep(ta, ta + 0.5, t); o.hide_render = u <= 0; o.location.z = 0.05 * (1 - u)
            for r, o in enumerate(stones):
                ta = t_s + (t_w - t_s) * r / len(stones) * 0.9; u = smoothstep(ta, ta + 0.5, t); o.hide_render = u <= 0; o.location.z = 0.05 * (1 - u)
            u = smoothstep(t_w, t_end, t)
            for o in walls: o.hide_render = u <= 0.001; o.scale.z = max(0.001, WH * u)
    S.update = update
    S.objs = [bpy.data.objects[n] for n in _track(bpy) - before]
    S.data['zmean'] = zm
    return S


# ================================================================================================= one pole, close
def build_pole(kit, M):
    bpy = kit.bpy; S = Set('pole'); before = _track(bpy)
    sz = 1.4
    land = cw.block(kit, size=(sz, sz), depth=DEPTH, strata=VZ_STRATA, top=lambda x, y: -0.02 + 0 * x,
                    water=[cw.basin(lambda x, y: -1.0 + 0.0 * x, depth=0.16, level=LV, shelf=0.01)], seed=51, grass=0, trees=0, boulders=0,
                    flowers=0, under=True, water_tint=WATER_TINT, water_density=2.0, name='poleblk')
    S.land = land; zm = _zmean(land); bed = float(land.height(np.array([0.0]), np.array([-sz / 2 + 0.01]))[0])
    sec_m = arch.mat_pole_section(kit, 'vz_polecut_big', WOOD_POLE, (0.60, 0.60, 0.58))
    zc = strata_z(bed, zm, CARANTO_SD[0] + 0.05); top = bed - 0.05
    q = arch.face_quad('-Y', 0.0, zc, top, 0.06, sz, sz); mid = (np.array(q[0]) + np.array(q[1])) / 2
    q[0] = tuple(mid + (np.array(q[0]) - mid) * 0.15); q[1] = tuple(mid + (np.array(q[1]) - mid) * 0.15)
    pole = arch.section_mesh(kit, 'vz_bigpole', sec_m, 1); arch.set_quads(pole, [q])
    S.data.update(pole_mat=sec_m, bed=bed, zc=zc, top=top, sz=sz)
    # neighbouring poles at the edges of the frame, so it reads as one of many
    sm = arch.section_mesh(kit, 'vz_nbpoles', sec_m, 4)
    Q = []
    for s in (-0.36, -0.22, 0.22, 0.36):
        qq = arch.face_quad('-Y', s, zc + 0.02 * abs(s), top - 0.01, 0.045, sz, sz); m2 = (np.array(qq[0]) + np.array(qq[1])) / 2
        qq[0] = tuple(m2 + (np.array(qq[0]) - m2) * 0.15); qq[1] = tuple(m2 + (np.array(qq[1]) - m2) * 0.15); Q.append(qq)
    arch.set_quads(sm, Q)
    # bubbles: on the face, in the water and the top of the mud; none deeper down
    bub_m = cw.mat_simple(kit, 'vz_bubble', (0.95, 0.97, 1.0), 0.1); rng = np.random.default_rng(9); bubbles = []
    V0, F0 = cw._icosphere(1)
    for k in range(22):
        ob = cw.mk_mesh(bpy, f'vz_bub{k}', V0 * float(rng.uniform(0.003, 0.006)), F0, [bub_m], None, True, kit.coll)
        bubbles.append((ob, float(rng.uniform(-0.55, 0.55)), float(rng.uniform(0, 1)), float(rng.uniform(0.012, 0.03)), k < 7))
    # mineral specks drifting into the pole (l09)
    spk_m = cw.mat_simple(kit, 'vz_speck', (0.85, 0.86, 0.88), 0.4); specks = []
    for k in range(26):
        ob = cw.mk_mesh(bpy, f'vz_spk{k}', V0 * 0.0035, F0, [spk_m], None, True, kit.coll)
        specks.append((ob, float(rng.uniform(-0.3, 0.3)), float(rng.uniform(zc + 0.05, top - 0.02)), float(rng.uniform(0, 1))))
    stone_sock = vsock(sec_m, 'stone')

    def update(t, shot):
        st = shot.get('pole', {})
        y_face = -sz / 2 - 0.004
        for ob, x, ph, sp, in_mud in bubbles:
            if in_mud:   # a few bubbles in the top of the mud that slow and stop as they go deeper
                u = (ph + t * 0.05) % 1.0; z = bed - 0.03 - 0.10 * u; ob.location = (x * 0.5, y_face, z)
                ob.scale = (1 - u,) * 3; ob.hide_render = u > 0.98
            else:
                u = (ph + t * sp / 0.2) % 1.0; z = bed + 0.01 + (LV - bed - 0.02) * u
                ob.location = (x + 0.01 * math.sin(t * 2 + ph * 9), y_face + 0.02, z); ob.hide_render = False
        s = st.get('stone')
        stone_sock.default_value = 0.0 if s is None else 0.85 * smoothstep(s[0], s[1], t)
        for ob, x0, z0, ph in specks:
            if s is None: ob.hide_render = True; continue
            u = smoothstep(s[0] + ph * 2.0, s[0] + ph * 2.0 + 2.2, t); ob.hide_render = u <= 0 or u >= 1
            ob.location = (x0 * (1 - u) + math.copysign(0.05, x0) * u, y_face, z0)
    S.update = update
    S.objs = [bpy.data.objects[n] for n in _track(bpy) - before]
    return S


# ================================================================================================= why it sinks (diagram)
SEA_X = 1.15
BANDS = [('mud', (0.40, 0.39, 0.36), -0.46), ('caranto', (0.80, 0.71, 0.50), -0.56), ('aquifer', (0.50, 0.58, 0.62), -0.78), ('clay', (0.46, 0.40, 0.33), -DEPTH - 0.002)]


def build_sink(kit, M, lamps):
    bpy = kit.bpy; S = Set('sink'); before = _track(bpy)
    sea = cw.basin(lambda x, y: (SEA_X - x) + 0.03 * cw.fbm(x, y, 2, 2, 2.0) * 0, depth=0.28, level=LV, shelf=0.10)
    land = cw.block(kit, size=(4.0, 4.0), depth=DEPTH, strata=VZ_STRATA, top=lambda x, y: -0.022 + 0 * x, water=[sea], seed=61,
                    zones=lambda x, y, h: {'rock': np.where(x > -0.9, 1.0, 0.0), 'path': np.where(x <= -0.9, 1.0, 0.0)}, grass=0, trees=0, boulders=0,
                    flowers=0, under=False, water_tint=WATER_TINT, water_density=2.4, name='sinkblk')
    S.land = land
    moving = [land.objects['top'], land.objects['walls']]
    rng = np.random.default_rng(6); k = 0
    for y in np.arange(-1.85, 1.9, 0.27):     # palazzi facing the sea
        w = 0.22; d = 0.16; h = float(rng.uniform(0.12, 0.19))
        moving.append(arch.palazzo(kit, M, SEA_X - 0.16, y, -0.022, w, d, h, _yaw_facing((1, 0)), seed=k + 300, name=f'vz_spal{k}')); k += 1
    for x in np.arange(-0.6, 0.7, 0.3):
        for y in np.arange(-1.7, 1.8, 0.34):
            if (x, y) == (0, 0): continue
            if abs(x - 0.2) < 0.15 and abs(y + 0.75) < 0.15: continue
            h = float(rng.uniform(0.10, 0.16)); moving.append(arch.palazzo(kit, M, x, y, -0.022, 0.2, 0.15, h, float(rng.choice([0, math.pi])), seed=k + 300, water_door=False, name=f'vz_spal{k}')); k += 1
    moving.append(arch.campanile(kit, M, 0.2, -0.75, -0.022, h=0.5, w=0.065, name='vz_scamp'))
    # the factory with its chimney, and the pump house over the well at the front face
    A = cw._Acc(); v, f = cw._box(-1.75, -1.1, -0.02, -1.15, -0.55, 0.16); A.add(v, f, 0)
    for j in range(4):
        x = -1.75 + 0.15 * j; A.add([(x, -1.1, 0.16), (x + 0.15, -1.1, 0.16), (x + 0.15, -0.55, 0.16), (x + 0.15, -0.55, 0.22)][:3] + [(x + 0.15, -1.1, 0.22)], [(0, 1, 3)], 1)
        A.add([(x, -1.1, 0.16), (x + 0.15, -1.1, 0.22), (x + 0.15, -0.55, 0.22), (x, -0.55, 0.16)], [(0, 1, 2, 3)], 1)
    v, f = cw._tube([(-1.3, -0.65, 0.1), (-1.3, -0.65, 0.62)], [0.035, 0.026], 12); A.add(v, f, 2)
    fac = A.build(bpy, 'vz_factory', [M.get('fwall', (0.66, 0.60, 0.54), 0.85, 0.1, 0.2), M.get('froof', (0.42, 0.40, 0.40), 0.7, 0.1, 0.2), M.get('brick', arch.BRICK, 0.85, 0.2, 0.3)], False, kit.coll)
    moving.append(fac)
    PX = -1.35
    A = cw._Acc(); v, f = cw._box(PX - 0.12, -2.0 + 0.004, -0.02, PX + 0.12, -1.75, 0.11); A.add(v, f, 0)
    A.add([(PX - 0.13, -2.0, 0.11), (PX + 0.13, -2.0, 0.11), (PX + 0.13, -1.74, 0.11), (PX - 0.13, -1.74, 0.11), (PX, -2.0, 0.16), (PX, -1.74, 0.16)], [(0, 1, 4), (3, 5, 2), (0, 4, 5, 3), (1, 2, 5, 4)], 1)
    ph = A.build(bpy, 'vz_pumphouse', [M.get('fwall', (0.66, 0.60, 0.54), 0.85, 0.1, 0.2), M.get('froof', (0.42, 0.40, 0.40), 0.7, 0.1, 0.2)], False, kit.coll)
    moving.append(ph)
    wheel = cw.mk_mesh(bpy, 'vz_valve', *cw._tube([(0.03 * math.cos(a), 0, 0.03 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)], np.full(25, 0.004), 6, False), [M.get('red', (0.70, 0.12, 0.10), 0.5, 0, 0)], None, True, kit.coll)
    wheel.location = (PX + 0.17, -1.95, 0.03); moving.append(wheel)
    smoke = []; sm_m = cw.mat_simple(kit, 'vz_smoke', (0.85, 0.85, 0.86), 0.9)
    V0, F0 = cw._icosphere(2)
    for j in range(7):
        o = cw.mk_mesh(bpy, f'vz_smoke{j}', cw._lumpy(V0, j, 0.2) * 0.03, F0, [sm_m], None, True, kit.coll); smoke.append((o, j / 7))
    # the tide gauge on the sea wall (+X face side), moving with the ground
    G = cw._Acc(); v, f = cw._box(-0.012, -0.002, -0.40, 0.012, 0.002, 0.10); G.add(v, f, 0)
    for j in range(26):
        z = -0.40 + j * 0.02; ln = 0.008 if j % 5 else 0.016; v, f = cw._box(-0.012, -0.0032, z - 0.0012, -0.012 + ln, -0.002, z + 0.0012); G.add(v, f, 1)
    gauge = G.build(bpy, 'vz_gauge', [M.get('white', (0.95, 0.95, 0.93), 0.5, 0, 0), M.get('ink', (0.05, 0.05, 0.06), 0.5, 0, 0)], False, kit.coll)
    gauge.location = (2.0 + 0.0025, -1.0, 0.0); gauge.rotation_euler = (0, 0, math.pi / 2); moving.append(gauge)
    S.data['gauge'] = gauge
    # the hand-drawn section on both front faces: bands that compress, the pipe with flowing water
    N = 80; band_m = [arch.mat_band(kit, f'vz_band_{nm}', c, 0.35, 0.3 if nm == 'aquifer' else 0.0, alt=(0.66, 0.64, 0.58) if nm == 'aquifer' else None) for nm, c, _ in BANDS]
    def prof(face):
        s = np.linspace(-2.0, 2.0, N)
        if face == '-Y': h = land.height(s, np.full(N, -1.999))
        else: h = land.height(np.full(N, 1.999), s)
        return s, h
    faces = {f: prof(f) for f in ('-Y', '+X')}
    band_obs = {}
    for face in faces:
        for b, (nm, c, zb) in enumerate(BANDS):
            V = np.zeros((2 * N, 3)); F = [(i, i + 1, N + i + 1, N + i) for i in range(N - 1)]
            ob = cw.mk_mesh(bpy, f'vz_band{face}{nm}', V, F, [band_m[b]], None, False, kit.coll); band_obs[(face, b)] = ob
    aq_mix = vsock(band_m[2], 'mix')
    pipe_m = cw.mat_simple(kit, 'vz_pipewall', (0.62, 0.64, 0.66), 0.4); flow_m = cw.mat_simple(kit, 'vz_flow', (0.30, 0.62, 0.86), 0.3, emission=(0.3, 0.62, 0.86), strength=0.6)
    pipe = arch.section_mesh(kit, 'vz_pipesec', pipe_m, 1); dashes = arch.section_mesh(kit, 'vz_pipeflow', flow_m, 14)
    lamps_unused = lamps
    base = np.array([v.co[:] for v in land.objects['water'].data.vertices]); water_ob = land.objects['water']

    def offs(t, st):
        sq = st.get('squeeze'); pump = st.get('pump'); d = 0.0
        if sq: d += 0.016 * smoothstep(sq[0], sq[1], t)
        if pump: d += 0.022 * smoothstep(pump[0], pump[1], t)
        return d

    def update(t, shot):
        st = shot.get('sink', {}); d = offs(t, st)
        for o in moving:
            if 'z0' not in o: o['z0'] = o.location.z
            o.location.z = o['z0'] - d
        rise = st.get('rise'); r = 0.02 * smoothstep(rise[0], rise[1], t) if rise else (0.02 if st.get('risen') else 0.0)
        V = base.copy(); V[4:, 2] = LV + r; water_ob.data.vertices.foreach_set('co', V.astype(np.float32).reshape(-1)); water_ob.data.update()
        # bands: top band from the (lowered) top down to its base; the mud base itself moves down only by the pumping share
        for face, (s, h) in faces.items():
            ztop = h - d; prev = ztop
            for b, (nm, c, zb) in enumerate(BANDS):
                lo = np.minimum(np.full(N, zb), prev - 0.0001)
                out = 0.0016
                if face == '-Y': P = [(x, -2.0 - out, z) for x, z in zip(s, prev)] + [(x, -2.0 - out, z) for x, z in zip(s, lo)]
                else: P = [(2.0 + out, y, z) for y, z in zip(s, prev)] + [(2.0 + out, y, z) for y, z in zip(s, lo)]
                ob = band_obs[(face, b)]; ob.data.vertices.foreach_set('co', np.array(P, np.float32).reshape(-1)); ob.data.update(); prev = lo
        pump = st.get('pump'); stop = st.get('stop')
        drained = smoothstep(pump[0], pump[1], t) if pump else (1.0 if st.get('pumped') else 0.0)
        aq_mix.default_value = 0.8 * drained                 # the water-bearing sand dries out while it is pumped
        # the pipe from the pump house down into the aquifer, water dashes flowing up while pumping
        show = st.get('pipe', False); pipe.hide_render = dashes.hide_render = not show; wheel.hide_render = not show; ph.hide_render = not show
        if show:
            zt = -0.022 - d; zb = BANDS[2][2] + 0.05
            arch.set_quads(pipe, [arch.face_quad('-Y', PX, zb, zt, 0.018, 4.0, 4.0, 0.0024)])
            Q = []
            if stop is None or t < stop: ph_ = t * 0.09
            else: x_ = min(1.0, t - stop); ph_ = (stop + x_ - 0.5 * x_ * x_) * 0.09      # the flow eases to a stop over 1 s
            for j in range(14):
                z = zb + ((j / 14 + ph_ / (zt - zb)) % 1.0) * (zt - zb - 0.03)
                Q.append(arch.face_quad('-Y', PX, z, z + 0.022, 0.009, 4.0, 4.0, 0.0034))
            arch.set_quads(dashes, Q)
            wheel.rotation_euler = (0, math.radians(180) * (smoothstep(stop, stop + 1.0, t) if stop else 0.0), 0)
        for o, ph0 in smoke:
            u = (ph0 + t * 0.06) % 1.0; o.location = (-1.3 + 0.25 * u, -0.65 + 0.1 * u, 0.62 - d + 0.5 * u); s_ = 0.6 + 1.6 * u
            o.scale = (s_, s_, s_); o.hide_render = u > 0.97
    S.update = update
    S.objs = [bpy.data.objects[n] for n in _track(bpy) - before]
    S.data['PX'] = PX
    return S


# ================================================================================================= the lagoon inlet and the MOSE gates
GATE_HX = 0.13; GATE_L = 0.42; GATE_W = 0.075; GATE_ANG = 52.0


def build_inlet(kit, M):
    bpy = kit.bpy; S = Set('inlet'); before = _track(bpy)
    def seg_d(x, y):
        yy = np.clip(y, -0.95, 3.0); return np.hypot(x, y - yy)
    fn = lambda x, y: (seg_d(x, y) - 0.36 - 0.025 * cw.fbm(x, y, 8, 3, 2.0))        # negative inside the strip of land
    water = [cw.basin(lambda x, y: -fn(x, y), depth=0.22, level=LV, shelf=0.18)]
    def top(x, y):
        d = seg_d(x, y); return -0.03 + 0.12 * np.exp(-(d / 0.24) ** 2) * (0.75 + 0.25 * cw.fbm(x, y, 5, 3, 2.5))
    def zones(x, y, h):
        d = seg_d(x, y); return {'sand': cw.smooth(0.16, 0.30, d)}
    land = cw.block(kit, size=(4.0, 4.0), depth=DEPTH, strata=VZ_STRATA, top=top, water=water, seed=71, zones=zones, grass=0.9, grass_height=1.1,
                    trees=0, tree_spots=[(0.0, 0.6, 0.9, 'round'), (-0.05, 1.3, 1.0, 'round'), (0.08, 1.75, 0.8, 'round')], boulders=6, flowers=0.1, under=True,
                    water_tint=WATER_TINT, water_density=2.2, name='inletblk')
    S.land = land
    # the lighthouse at the tip of the strip
    A = cw._Acc(); v, f = _cone((0, 0, 0), 0.045, 0.032, 0.30, 16); A.add(v, f, 0)
    for j in range(3):
        v, f = _cone((0, 0, 0.05 + j * 0.09), 0.0435 - j * 0.0045, 0.040 - j * 0.0045, 0.04, 16); A.add(v, f, 1)
    v, f = _cone((0, 0, 0.30), 0.03, 0.03, 0.035, 12); A.add(v, f, 2)
    v, f = _cone((0, 0, 0.335), 0.036, 0.004, 0.03, 12); A.add(v, f, 1)
    lh = A.build(bpy, 'vz_lighthouse', [M.get('white', (0.95, 0.95, 0.93), 0.5, 0, 0), M.get('red', (0.70, 0.12, 0.10), 0.5, 0, 0), M.get('lglass', (0.95, 0.85, 0.55), 0.2, 0, 0)], False, kit.coll)
    JET = (-0.12, 0.16, -1.24, -0.84, 0.05)
    jet = cw.mk_mesh(bpy, 'vz_jetty', *cw._box(JET[0], JET[2], -0.36, JET[1], JET[3], JET[4]), [M.get('concrete', (0.62, 0.62, 0.60), 0.85, 0.1, 0.2)], None, False, kit.coll)
    lh.location = (0.02, -1.0, JET[4])
    # the gates: a row hinged across the inlet on the seabed
    gates = []; y = -1.995 + GATE_W / 2
    while y < -1.24 - GATE_W / 2 + 0.01:
        bed = float(land.height(np.array([GATE_HX - GATE_L / 2]), np.array([y]))[0])
        g = arch.gate(kit, M, GATE_L, GATE_W, 0.03, name=f'vz_gate{len(gates)}'); g.location = (GATE_HX, y, bed + 0.004); g.rotation_euler = (0, 0, math.pi)
        gates.append((g, bed)); y += GATE_W
    # the caisson the gates rest in, on the seabed across the inlet
    # two water bodies: lagoon (left, stays) and sea (right, rises), split at the gate line
    kw = land.objects['water']; kw.hide_render = True; wm = kw.data.materials[0]; e = 0.0015; zb2 = float(np.min([v.co.z for v in kw.data.vertices]))
    XG = GATE_HX - GATE_L * math.cos(math.radians(GATE_ANG)) / 2
    def prism(name, poly):
        n = len(poly); V = [(x, y, zb2) for x, y in poly] + [(x, y, LV) for x, y in poly]
        F = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        return cw.mk_mesh(bpy, name, V, F, [wm], None, False, kit.coll)
    lag_w = prism('vz_lagw', [(-2.0 + e, -2.0 + e), (XG - 0.0007, -2.0 + e), (XG - 0.0007, 2.0 - e), (-2.0 + e, 2.0 - e)])
    sea_w = prism('vz_seaw', [(XG + 0.0007, -2.0 + e), (2.0 - e, -2.0 + e), (2.0 - e, 2.0 - e), (0.1, 2.0 - e), (0.1, JET[2] + 0.02), (XG + 0.0007, JET[2] + 0.02)])
    sea_base = np.array([v.co[:] for v in sea_w.data.vertices])
    bubbles = []; V0, F0 = cw._icosphere(1); bm = cw.mat_simple(kit, 'vz_gbub', (0.95, 0.97, 1.0), 0.1); rng = np.random.default_rng(13)
    for k in range(30):
        o = cw.mk_mesh(bpy, f'vz_gb{k}', V0 * float(rng.uniform(0.003, 0.007)), F0, [bm], None, True, kit.coll); bubbles.append((o, float(rng.uniform(-1.98, -1.3)), float(rng.uniform(0, 1))))
    b, parts = arch.boat(kit, M, (0.70, 0.66, 0.60), 0.10, 1, 'vz_iboat', 2); b.location = (-1.1, -1.5, LV - 0.004); b.rotation_euler = (0, 0, 0.4)
    cw.birds(kit, 3, center=(0.2, 0.0), radius=2.0, height=1.0, seed=8, size=0.035, color=(0.92, 0.92, 0.94))

    def update(t, shot):
        st = shot.get('inlet', {}); rise = st.get('rise'); sea = st.get('sea')
        u = smoothstep(rise[0], rise[1], t) if rise else (1.0 if st.get('up') else 0.0)
        for j, (g, bed) in enumerate(gates):
            uj = smoothstep(0.0 + 0.04 * j, 1.0, u) if u < 1 else 1.0
            g.rotation_euler = (0, -math.radians(GATE_ANG) * uj + math.radians(1.5), math.pi)
        r = 0.075 * smoothstep(sea[0], sea[1], t) if sea else (0.075 if st.get('high') else 0.0)
        V = sea_base.copy(); V[len(V) // 2:, 2] = LV + r; sea_w.data.vertices.foreach_set('co', V.astype(np.float32).reshape(-1)); sea_w.data.update()
        for o, y0, ph in bubbles:
            if rise is None or not (rise[0] <= t <= rise[1] + 1.5): o.hide_render = True; continue
            v = (ph + (t - rise[0]) * 0.6) % 1.0; o.hide_render = False
            o.location = (GATE_HX - GATE_L * 0.5 * math.cos(math.radians(GATE_ANG) * u) + 0.03 * math.sin(ph * 20), y0, -0.25 + 0.22 * v)
        b.location.z = LV - 0.004 + 0.0015 * math.sin(t * 1.4)
    S.update = update
    S.objs = [bpy.data.objects[n] for n in _track(bpy) - before]
    S.data['gates'] = gates; S.data['XG'] = XG
    return S


def _cone(c, r0, r1, h, n):
    V = []; F = []
    for k in range(n):
        a = 2 * math.pi * k / n; V.append((c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a), c[2]))
    for k in range(n):
        a = 2 * math.pi * k / n; V.append((c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a), c[2] + h))
    F = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)] + [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    return V, F


BUILDERS = {'city': lambda kit, M, lamps: build_city(kit, M, lamps), 'lagoon': lambda kit, M, lamps: build_lagoon(kit, M),
            'site': lambda kit, M, lamps: build_site(kit, M), 'pole': lambda kit, M, lamps: build_pole(kit, M),
            'sink': lambda kit, M, lamps: build_sink(kit, M, lamps), 'inlet': lambda kit, M, lamps: build_inlet(kit, M)}
