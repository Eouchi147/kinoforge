"""Life, light and small surprises for "Why Venice Sinks" (Sam, 22 Oct 12:01: cinema lighting, haze, god rays, animated
fauna, easter eggs in the soil that make people smile). Built in this folder on top of the kit; cheap by design:
haze and god rays are camera-only translucent cards (no volume scattering), animals are small meshes moved in code.

    mist_sheets   lagoon mist lying on the water, drifting (morning haze)
    god_rays      soft shafts of sunlight falling through the haze (church and morning scenes)
    fish, crab    swimming and side-stepping behind the glass of the cut faces
    pigeons       pecking on the campo
    amphora, coin, anchor   lost things in the mud, set into the cut faces
    cellar_cat    a cellar in the cut face with a cat asleep in it while the sea floods the street above
"""
import math
import numpy as np
import cutaway as cw
import arch


def _cam_only(ob):
    for at in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        try: setattr(ob, at, False)
        except Exception: pass
    return ob


def _soft_mat(kit, name, color, strength, alpha_fn):
    """Emission over transparency with an alpha built by alpha_fn(g, uv) (a socket). Returns (material, alpha gain socket)."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); a = alpha_fn(g, tc)
    gain = g.value(1.0, 'gain'); a = g.math('MULTIPLY', a, gain)
    em = g.node('ShaderNodeEmission', ins={'Color': cw.srgb(color), 'Strength': strength}); tr = g.node('ShaderNodeBsdfTransparent')
    mx = g.node('ShaderNodeMixShader'); g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(em, mx.inputs[2]); cw._finish(g, mx)
    return m, gain


def mist_sheets(kit, z, size=4.0, n=3, color=(0.96, 0.96, 0.97), opacity=0.32, name='vz_mist'):
    """Thin sheets of mist lying just above the water, drifting slowly (camera only, so they cost almost nothing)."""
    def alpha(g, tc):
        zo, w = g.phase(0.04); u = tc.outputs['Generated']; us = g.sep(u)
        nz = g.noise(g.comb(g.math('MULTIPLY', us[0], 2.2), g.math('MULTIPLY', us[1], 2.2), zo), 2.0, 3.0, 0.55, '4D', w)
        e = g.math('MINIMUM', g.math('MINIMUM', us[0], g.math('SUBTRACT', 1.0, us[0])), g.math('MINIMUM', us[1], g.math('SUBTRACT', 1.0, us[1])))
        edge = g.math('MULTIPLY', e, 6.0, clamp=True)
        return g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', nz.outputs['Fac'], 0.42), 2.6, clamp=True), g.math('MULTIPLY', edge, opacity))
    m, gain = _soft_mat(kit, name + '_m', color, 1.15, alpha); obs = []
    for k in range(n):
        s = size * (0.5 + 0.05 * k); V = [(-s, -s, z + 0.012 * k), (s, -s, z + 0.012 * k), (s, s, z + 0.012 * k), (-s, s, z + 0.012 * k)]
        ob = cw.mk_mesh(kit.bpy, f'{name}{k}', V, [(0, 1, 2, 3)], [m], None, False, kit.coll); _cam_only(ob); obs.append(ob)
    return obs, gain


def god_rays(kit, sun_az, sun_el, center=(0, 0, 0), n=6, length=5.0, radius=0.22, spread=1.2, color=(1.0, 0.86, 0.62), seed=3, name='vz_rays'):
    """Soft shafts of light along the sun direction, ending on the scene: cones whose edges fade (Layer Weight facing)
    and whose ends fade, slowly breathing. Camera only. Returns (objects, gain socket)."""
    rng = np.random.default_rng(seed)
    def alpha(g, tc):
        lw = g.node('ShaderNodeLayerWeight', ins={'Blend': 0.5}); core = g.math('POWER', g.math('SUBTRACT', 1.0, lw.outputs['Facing']), 2.4)
        u = g.sep(tc.outputs['Generated'])[2]
        ends = g.math('MULTIPLY', g.math('MULTIPLY', u, 3.0, clamp=True), g.math('MULTIPLY', g.math('SUBTRACT', 1.0, u), 1.6, clamp=True))
        zo, w = g.phase(0.03); nz = g.noise(g.comb(g.math('MULTIPLY', u, 3.0), zo, 0.0), 1.5, 2.0, 0.5, '4D', w)
        return g.math('MULTIPLY', g.math('MULTIPLY', core, ends), g.math('MULTIPLY', g.math('ADD', nz.outputs['Fac'], 0.2), 0.16))
    m, gain = _soft_mat(kit, name + '_m', color, 1.6, alpha)
    a, e = math.radians(sun_az), math.radians(sun_el); d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    from mathutils import Vector
    obs = []
    for k in range(n):
        r = radius * rng.uniform(0.6, 1.3); V, F = cw._tube([(0, 0, 0), (0, 0, length)], [r * 0.7, r * 1.25], 16, False)
        ob = cw.mk_mesh(kit.bpy, f'{name}{k}', V, F, [m], None, True, kit.coll)
        off = np.array([rng.uniform(-spread, spread), rng.uniform(-spread, spread), 0.0]) + np.array(center)
        ob.location = tuple(off); ob.rotation_euler = Vector(tuple(d)).to_track_quat('Z', 'Y').to_euler(); _cam_only(ob); obs.append(ob)
    return obs, gain


def _fish_mesh(kit, M, name, L=0.022, color=(0.62, 0.66, 0.70)):
    A = cw._Acc(); xs = np.linspace(-L / 2, L / 2, 9); rad = [0.0008 + 0.0042 * math.sin(math.pi * (k + 0.5) / 9) ** 0.8 for k in range(9)]
    v, f = cw._tube([(x, 0, 0) for x in xs], rad, 8); A.add([(a, b * 0.55, c) for a, b, c in v], f, 0)
    A.add([(-L / 2, 0, 0), (-L / 2 - 0.007, 0, 0.004), (-L / 2 - 0.007, 0, -0.004)], [(0, 1, 2)], 0)
    return A.build(kit.bpy, name, [M.get('fish', color, 0.35, 0.15, 0)], True, kit.coll)


def fish(kit, M, spots, name='vz_fish'):
    """Small fish swimming in slow loops at spots [(x, y, z, radius)] behind the glass; tails beat."""
    obs = []
    for k, spot in enumerate(spots):
        x, y, z, r = spot[:4]; along_y = len(spot) > 4 and spot[4] == 'y'
        ob = _fish_mesh(kit, M, f'{name}{k}', 0.018 + 0.006 * (k % 3), [(0.62, 0.66, 0.70), (0.80, 0.70, 0.45), (0.55, 0.60, 0.52)][k % 3])
        ph = 1.7 * k; sp = 0.12 + 0.03 * (k % 2)
        def pose(t, ob=ob, x=x, y=y, z=z, r=r, ph=ph, sp=sp, ay=along_y):
            a = ph + sp * t; dx, dy = r * math.cos(a), 0.25 * r * math.sin(a); hd = a + math.pi / 2
            if ay: dx, dy = dy, dx; hd = math.pi / 2 - hd
            ob.location = (x + dx, y + dy, z + 0.006 * math.sin(t * 0.7 + ph))
            ob.rotation_euler = (0, 0, hd + 0.25 * math.sin(t * 9 + ph))
        kit.on_frame(pose); pose(0.0); obs.append(ob)
    return obs


def crab(kit, M, x, y, z, name='vz_crab', span=0.08, yaw=0.0):
    """A small crab side-stepping to and fro on the seabed, legs ticking."""
    A = cw._Acc(); V0, F0 = cw._icosphere(2); A.add(V0 * np.array([0.011, 0.008, 0.004]), F0, 0)
    for side in (-1, 1):
        for j in range(3):
            a = side * (0.6 + 0.35 * j); p0 = np.array([0.006 * math.cos(a), 0.006 * math.sin(a) * side, 0]); p1 = p0 + np.array([0.008 * math.cos(a) * side * 0 + 0.002 * (j - 1), 0.009 * side, -0.004])
            v, f = cw._tube([p0, p0 + [0.002 * (j - 1), 0.006 * side, 0.002], p1], [0.0012, 0.001, 0.0006], 5); A.add(v, f, 0)
        v, f = cw._tube([(0.009, 0.004 * side, 0.001), (0.016, 0.006 * side, 0.004)], [0.0016, 0.0024], 6); A.add(v, f, 0)
    ob = A.build(kit.bpy, name, [M.get('crab', (0.66, 0.26, 0.14), 0.5, 0.1, 0)], True, kit.coll)
    def pose(t, ob=ob):
        u = math.sin(t * 0.45); ob.location = (x + span * 0.5 * u * math.cos(yaw), y + span * 0.5 * u * math.sin(yaw), z + 0.0008 * abs(math.sin(t * 6)))
        ob.rotation_euler = (0, 0, yaw + math.pi / 2 + 0.08 * math.sin(t * 6))
    kit.on_frame(pose); pose(0.0); return ob


def pigeons(kit, M, center, n=12, r=0.16, seed=4, name='vz_pigeon'):
    """Pigeons on the campo: they peck, turn and take little hops."""
    rng = np.random.default_rng(seed); mat = [M.get('pigeon', (0.48, 0.50, 0.56), 0.6, 0.15, 0), M.get('pigeonhd', (0.30, 0.36, 0.40), 0.5, 0, 0)]
    V0, F0 = cw._icosphere(2); obs = []
    for k in range(n):
        A = cw._Acc(); A.add(V0 * np.array([0.0055, 0.0035, 0.0035]) + [0, 0, 0.004], F0, 0); A.add(V0 * 0.0022 + [0.005, 0, 0.0072], F0, 1)
        A.add([(-0.005, -0.002, 0.005), (-0.009, 0, 0.006), (-0.005, 0.002, 0.005)], [(0, 1, 2)], 0)
        ob = A.build(kit.bpy, f'{name}{k}', mat, True, kit.coll)
        a0 = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0.03, r); x0 = center[0] + rr * math.cos(a0); y0 = center[1] + rr * math.sin(a0)
        ph = rng.uniform(0, 10); yaw0 = rng.uniform(0, 2 * math.pi)
        def pose(t, ob=ob, x0=x0, y0=y0, ph=ph, yaw0=yaw0):
            hop = max(0.0, math.sin(t * 0.9 + ph)) ** 30; step = math.floor((t * 0.9 + ph) / (2 * math.pi))
            yaw = yaw0 + 0.9 * step; ox = 0.015 * math.cos(1.3 * step + ph); oy = 0.015 * math.sin(1.7 * step + ph)
            ob.location = (x0 + ox, y0 + oy, center[2] + 0.006 * hop)
            ob.rotation_euler = (0, 0.5 * max(0.0, math.sin(t * 3.1 + ph)) ** 4, yaw)
        kit.on_frame(pose); pose(0.0); obs.append(ob)
    return obs


def _flat(ob, face, s, z, depth=0.02, out=0.0022, sx=4.0, sy=4.0):
    """Set a relief object into a cut face: flattened to `depth` across the face, standing just proud of it."""
    if face == '-Y': ob.location = (s, -sy / 2 - out, z); ob.scale = (1, depth, 1)
    else: ob.location = (sx / 2 + out, s, z); ob.scale = (depth, 1, 1)
    return ob


def amphora(kit, M, face, s, z, tilt=0.5, size=1.0, sx=4.0, sy=4.0, name='vz_amphora'):
    """A lost Roman amphora lying in the mud (seen in the cut as a relief)."""
    prof = [(0.002, -0.07), (0.010, -0.06), (0.026, -0.03), (0.032, 0.0), (0.030, 0.03), (0.016, 0.055), (0.009, 0.065), (0.009, 0.085), (0.012, 0.09)]
    V, F = arch._revolve([(r * size, zz * size) for r, zz in prof], 18)
    A = cw._Acc(); A.add(V, F, 0)
    for side in (-1, 1):
        v, f = cw._tube([(side * 0.010 * size, 0, 0.08 * size), (side * 0.024 * size, 0, 0.078 * size), (side * 0.026 * size, 0, 0.05 * size)], [0.0025 * size] * 3, 6); A.add(v, f, 0)
    ob = A.build(kit.bpy, name, [M.get('terracotta', (0.74, 0.42, 0.26), 0.8, 0.25, 0.3)], True, kit.coll)
    ob.rotation_euler = (0, tilt, 0) if face == '-Y' else (tilt, 0, 0)
    return _flat(ob, face, s, z, 0.06, 0.0024, sx, sy)


def coin(kit, M, face, s, z, r=0.009, sx=4.0, sy=4.0, name='vz_coin'):
    """A Venetian gold ducat in the mud, face out, with a raised rim."""
    A = cw._Acc(); V, F = cw._tube([(0, -0.0012, 0), (0, 0.0012, 0)], [r, r], 24); A.add(V, F, 0)
    v, f = cw._tube([(0, -0.0016, 0), (0, -0.0012, 0)], [r * 0.6, r * 0.6], 16); A.add(v, f, 0)
    ob = A.build(kit.bpy, name, [M.get('gold', (0.95, 0.74, 0.30), 0.25, 0.1, 0.2)], True, kit.coll)
    ob.rotation_euler = (0, 0.3, 0) if face == '-Y' else (0, 0, math.pi / 2)
    if face == '-Y': ob.location = (s, -sy / 2 - 0.0025, z)
    else: ob.location = (sx / 2 + 0.0025, s, z)
    return ob


def anchor(kit, M, face, s, z, size=1.0, tilt=0.4, sx=4.0, sy=4.0, name='vz_anchor'):
    """An old iron anchor stuck in the mud: shank, stock, curved arms with flukes, a ring."""
    A = cw._Acc(); k = size
    v, f = cw._tube([(0, 0, -0.05 * k), (0, 0, 0.06 * k)], [0.004 * k] * 2, 8); A.add(v, f, 0)
    v, f = cw._tube([(-0.035 * k, 0, 0.05 * k), (0.035 * k, 0, 0.05 * k)], [0.0035 * k] * 2, 8); A.add(v, f, 0)
    arc = [(0.045 * k * math.sin(a), 0, -0.05 * k + 0.045 * k * (1 - math.cos(a))) for a in np.linspace(-1.2, 1.2, 13)]
    v, f = cw._tube(arc, [0.0035 * k] * 13, 8); A.add(v, f, 0)
    for sd in (-1, 1):
        p = np.array(arc[0 if sd < 0 else -1]); A.add([tuple(p + [0, -0.001, 0]), tuple(p + [sd * 0.012 * k, -0.001, 0.016 * k]), tuple(p + [-sd * 0.006 * k, -0.001, 0.012 * k])], [(0, 1, 2)], 0)
    ring = [(0.009 * k * math.sin(a), 0, 0.072 * k + 0.009 * k * math.cos(a)) for a in np.linspace(0, 2 * math.pi, 17)]
    v, f = cw._tube(ring, [0.0018 * k] * 17, 6, False); A.add(v, f, 0)
    ob = A.build(kit.bpy, name, [M.get('rust', (0.30, 0.20, 0.15), 0.85, 0.35, 0.4)], True, kit.coll)
    ob.rotation_euler = (0, tilt, 0) if face == '-Y' else (tilt, 0, 0)
    return _flat(ob, face, s, z, 0.25, 0.0026, sx, sy)


def cellar_cat(kit, M, x, z0, z1, w=0.16, sy=4.0, name='vz_cellar'):
    """A small cellar seen in the -Y cut face under a house: plaster walls in shadow, a floor, a lamp, and a ginger cat
    curled up asleep, breathing slowly. Drawn on the face plane (with the cat in relief)."""
    bpy = kit.bpy; y = -sy / 2 - 0.0026; A = cw._Acc()
    A.add([(x - w / 2 - 0.006, y + 0.0004, z0 - 0.006), (x + w / 2 + 0.006, y + 0.0004, z0 - 0.006), (x + w / 2 + 0.006, y + 0.0004, z1 + 0.006), (x - w / 2 - 0.006, y + 0.0004, z1 + 0.006)], [(0, 1, 2, 3)], 0)
    A.add([(x - w / 2, y, z0), (x + w / 2, y, z0), (x + w / 2, y, z1), (x - w / 2, y, z1)], [(0, 1, 2, 3)], 1)
    A.add([(x - w / 2, y - 0.0002, z0), (x + w / 2, y - 0.0002, z0), (x + w / 2 - 0.012, y - 0.0002, z0 + 0.012), (x - w / 2 + 0.012, y - 0.0002, z0 + 0.012)], [(0, 1, 2, 3)], 2)
    for k in range(3):   # barrels against the back wall
        V, F = cw._tube([(x + w / 2 - 0.02 - 0.024 * k, y - 0.002, z0 + 0.001), (x + w / 2 - 0.02 - 0.024 * k, y - 0.002, z0 + 0.024)], [0.009, 0.009], 12); A.add(V, F, 3)
    V0, F0 = cw._icosphere(1); A.add(V0 * 0.003 + [x - w / 2 + 0.018, y - 0.004, z1 - 0.012], F0, 4)
    room = A.build(bpy, name, [M.get('stoneframe', (0.86, 0.84, 0.78), 0.7, 0.05, 0.1), M.get('plaster', (0.36, 0.28, 0.22), 0.9, 0.15, 0.1),
                               M.get('cellarfloor', (0.30, 0.24, 0.20), 0.9, 0.2, 0.1), M.get('barrel', (0.40, 0.27, 0.16), 0.75, 0.3, 0.2),
                               cw.mat_glow(kit, 'vz_cellarlamp', (1.0, 0.72, 0.36), 18.0)], False, kit.coll)
    ld = bpy.data.lights.new(name + '_l', 'POINT'); ld.energy = 0.05; ld.color = (1.0, 0.72, 0.40); ld.shadow_soft_size = 0.004
    lo = bpy.data.objects.new(name + '_l', ld); kit.coll.objects.link(lo); lo.location = (x - w / 2 + 0.018, y - 0.015, z1 - 0.014)
    C = cw._Acc(); c = np.array([x - 0.02, y - 0.006, z0 + 0.008])
    C.add(V0 * np.array([0.016, 0.006, 0.0085]) + c, F0, 0)
    C.add(V0 * 0.0062 + c + [0.016, -0.001, 0.003], F0, 0)
    for sd in (-1, 1): C.add([tuple(c + [0.016 + sd * 0.004, -0.004, 0.008]), tuple(c + [0.016 + sd * 0.0045, -0.004, 0.0128]), tuple(c + [0.016 + sd * 0.0012, -0.004, 0.009])], [(0, 1, 2)], 0)
    tail = [tuple(c + [-0.016 + 0.018 * (1 - math.cos(a)), -0.004, -0.004 + 0.002 * math.sin(a)]) for a in np.linspace(0, 1.6, 8)]
    v, f = cw._tube(tail, [0.0022] * 8, 6); C.add(v, f, 0)
    for sd in (-1, 1): C.add([tuple(c + [0.016 + sd * 0.0025, -0.0072, 0.0035]), tuple(c + [0.016 + sd * 0.0025 + 0.0018, -0.0072, 0.0035]), tuple(c + [0.016 + sd * 0.0025 + 0.0009, -0.0072, 0.0031])], [(0, 1, 2)], 1)
    cat = C.build(bpy, name + '_cat', [M.get('ginger', (0.86, 0.50, 0.20), 0.8, 0.2, 0.2), M.get('catlid', (0.10, 0.07, 0.05), 0.6, 0, 0)], True, kit.coll)
    cat_base = np.array([v.co[:] for v in cat.data.vertices]); cc = c.copy()
    def breathe(t):
        s = 1.0 + 0.05 * math.sin(t * 1.6)
        V = cat_base.copy(); V[:, 2] = cc[2] + (V[:, 2] - cc[2]) * s
        cat.data.vertices.foreach_set('co', V.astype(np.float32).reshape(-1)); cat.data.update()
    kit.on_frame(breathe)
    return [room, cat, lo]
