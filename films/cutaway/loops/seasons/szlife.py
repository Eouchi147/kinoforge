"""Four seasons loop: atmosphere, animals, easter eggs and the title (bpy). Every piece is a pure function of t and
repeats on the 12 s loop. Kept small and self-contained so the shared films/styles/cutaway/cinematic extras can replace
any of them later.

Atmosphere   a light haze in a bounded box (god rays through the trees when the sun is low), ground fog in autumn,
             mist over the pond in spring; densities follow the season (szworld curves blend across the seam).
Animals      a duck comes down the stream in spring and leaves in summer; fish circle in the pond (seen through the glass,
             slow in winter); a squirrel buries acorns in autumn; a robin hops on the snow and leaves tracks.
Easter eggs  an ammonite fossil in the right cut face, a vein of gold flecks deep in the gravel (in szmats strata), the
             squirrel's acorn cache in a pocket under the bank (front face).
Title        "One pond. One year." set in code (Inter Tight SemiBold, OFL), fixed to the camera in the empty sky.
"""
import math, os
import numpy as np
import cutaway as cw
from cutaway import G, srgb
import szworld as W

CACHE = (1.18, 0.055, 0.04)             # acorn cache on the front face: x, half width, half height (z from the bank)
FOSSIL = (0.55, -0.80, 0.075)           # ammonite on the right (+X) face: y, z, radius

def _ell(c, r, sub=2):
    V, F = cw._icosphere(sub); return V * np.asarray(r, float) + np.asarray(c, float), F

def _hide(ob): ob.location = (0.0, 0.0, -60.0); ob.scale = (1e-3, 1e-3, 1e-3)

def path_at(P, u):
    """Point and heading at fraction u (0..1) of the arc length of polyline P (N x 2 or N x 3)."""
    P = np.asarray(P, float); seg = np.linalg.norm(np.diff(P, axis=0), axis=1); c = np.concatenate([[0], np.cumsum(seg)])
    s = np.clip(u, 0, 1) * c[-1]; i = min(int(np.searchsorted(c, s, 'right')) - 1, len(seg) - 1); f = (s - c[i]) / max(seg[i], 1e-9)
    p = P[i] + (P[i + 1] - P[i]) * f; d = P[i + 1] - P[i]
    return p, math.atan2(d[1], d[0])

# ------------------------------------------------------------------ atmosphere
def build_atmosphere(kit, D):
    bpy = kit.bpy
    # haze: a bounded box around the block and its trees; density per season (god rays in summer, crisp in winter)
    m = cw._new_mat(bpy, 'sz_haze'); g = G(m.node_tree, kit)
    v = g.node('ShaderNodeVolumePrincipled'); g.put(v, 'Density', D.val(g, 'haze', 0.02)); g.put(v, 'Anisotropy', 0.35)
    g.put(v, 'Color', D.rgb(g, 'hazecol', (1.0, 0.95, 0.88)))
    o = g.node('ShaderNodeOutputMaterial'); g.link(v, o.inputs['Volume'])
    V, F = cw._box(-2.6, -2.6, -W.DEPTH - 0.1, 2.6, 2.6, 1.7); hz = cw.mk_mesh(bpy, 'sz_haze', V, F, [m], None, False, kit.coll)
    # ground fog and pond mist: a thin slab hugging the top, densest low, drifting wisps
    m = cw._new_mat(bpy, 'sz_fog'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; s = g.sep(pos)
    zoff, w = g.phase(0.08); n = g.noise(g.vmath('ADD', g.vmath('MULTIPLY', pos, (1.6, 1.6, 3.0)), g.comb(zoff, 0.0, 0.0)), 1.0, 3.0, 0.55, '4D', w)
    wisp = g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.38), 3.0, clamp=True)
    low = g.math('EXPONENT', g.math('MULTIPLY', g.math('SUBTRACT', s[2], W.LV), -9.0))
    q = g.math('SQRT', g.math('ADD', g.math('POWER', g.math('DIVIDE', g.math('SUBTRACT', s[0], W.POND_C[0]), W.POND_R[0] * 1.1), 2.0),
                                g.math('POWER', g.math('DIVIDE', g.math('SUBTRACT', s[1], W.POND_C[1]), W.POND_R[1] * 1.1), 2.0)))
    pond = g.math('SUBTRACT', 1.4, q, clamp=True)
    where = g.math('MAXIMUM', g.math('MULTIPLY', pond, D.val(g, 'mist')), D.val(g, 'fog'))
    v = g.node('ShaderNodeVolumePrincipled'); g.put(v, 'Density', g.math('MULTIPLY', g.math('MULTIPLY', where, low), g.math('MULTIPLY', wisp, 2.2)))
    g.put(v, 'Color', (0.95, 0.96, 0.98)); g.put(v, 'Anisotropy', 0.2)
    o = g.node('ShaderNodeOutputMaterial'); g.link(v, o.inputs['Volume'])
    V, F = cw._box(-W.H - 0.25, -W.H - 0.25, W.LV - 0.01, W.H + 0.25, W.H + 0.25, 0.40); fg = cw.mk_mesh(bpy, 'sz_fog', V, F, [m], None, False, kit.coll)
    return {'haze': hz, 'fog': fg}

# ------------------------------------------------------------------ the duck (spring)
def build_duck(kit):
    bpy = kit.bpy; A = cw._Acc()
    mats = [cw.mat_simple(kit, 'sz_duckbody', (0.48, 0.40, 0.32), 0.7, noise_amt=0.25), cw.mat_simple(kit, 'sz_duckhead', (0.08, 0.32, 0.16), 0.3, metallic=0.2),
            cw.mat_simple(kit, 'sz_duckbeak', (0.92, 0.72, 0.16), 0.5), cw.mat_simple(kit, 'sz_duckchest', (0.42, 0.20, 0.12), 0.6),
            cw.mat_simple(kit, 'sz_duckwhite', (0.92, 0.92, 0.90), 0.6)]
    k = 1.5
    for c, r, m in [((0, 0, 0.012), (0.055, 0.032, 0.022), 0), ((-0.05, 0, 0.022), (0.022, 0.012, 0.010), 0), ((0.038, 0, 0.018), (0.022, 0.024, 0.018), 3),
                    ((0.046, 0, 0.040), (0.009, 0.009, 0.004), 4), ((0.050, 0, 0.055), (0.016, 0.014, 0.016), 1), ((0.068, 0, 0.052), (0.012, 0.005, 0.003), 2)]:
        v, f = _ell(np.array(c) * k, np.array(r) * k); A.add(v, f, m)
    ob = A.build(bpy, 'sz_duck', mats, True, kit.coll); _hide(ob); return ob

def duck_pose(ob, t):
    pond = [(0.05, -0.80), (0.25, -1.02), (0.55, -1.15), (0.40, -1.38), (0.05, -1.30), (-0.25, -1.12), (-0.12, -0.92), (0.05, -0.80)]
    sp = W._SP[W._SP[:, 1] < W.H - 0.02]                              # the stream inside the block, back to front
    down = np.vstack([sp, pond[:1]]); t = t % W.LOOP
    if 11.3 <= t or t < 1.1:
        u = ((t - 11.3) % W.LOOP) / 1.8; p, hd = path_at(down, u); sc = min(1.0, u * 8)
    elif t < 4.7:
        p, hd = path_at(pond, (t - 1.1) / 3.6); sc = 1.0
    elif t < 6.4:
        u = (t - 4.7) / 1.7; p, hd = path_at(down[::-1], u); sc = min(1.0, (1 - u) * 8)
    else:
        _hide(ob); return
    bob = 0.003 * math.sin(2 * math.pi * 3 * t / W.LOOP * 4)
    ob.location = (p[0], p[1], W.LV - 0.012 + bob); ob.rotation_euler = (0, 0, hd); ob.scale = (sc, sc, sc)

# ------------------------------------------------------------------ fish (seen through the glass)
def build_fish(kit, rng, n=3):
    bpy = kit.bpy; body = cw.mat_simple(kit, 'sz_fish', (0.70, 0.70, 0.62), 0.3, metallic=0.4, noise_amt=0.2)
    fin = cw.mat_simple(kit, 'sz_fin', (0.86, 0.30, 0.12), 0.5); out = []
    sp = np.array([W.blend(t, (0.8, 1.0, 0.7, 0.15)) for t in np.linspace(0, W.LOOP, 481)])
    F = np.concatenate([[0], np.cumsum((sp[1:] + sp[:-1]) / 2)]); F /= F[-1]           # loop-exact swimming phase
    for k in range(n):
        A = cw._Acc(); v, f = _ell((0, 0, 0), (0.038, 0.009, 0.015)); A.add(v, f, 0)
        A.add([(-0.032, 0, 0), (-0.058, 0, 0.016), (-0.058, 0, -0.016)], [(0, 1, 2)], 1)
        A.add([(0.0, 0, 0.012), (-0.016, 0, 0.026), (-0.022, 0, 0.011)], [(0, 1, 2)], 1)
        ob = A.build(bpy, f'sz_fish{k}', [body, fin], True, kit.coll); s = rng.uniform(1.1, 1.4); ob.scale = (s, s, s)
        out.append((ob, rng.uniform(0, 6.28), int(rng.integers(2, 4)), rng.uniform(0.18, 0.32), rng.uniform(0.10, 0.16), rng.uniform(-0.30, -0.14)))
    return {'fish': out, 'F': F}

def fish_pose(Fi, t):
    u = float(np.interp(t % W.LOOP, np.linspace(0, W.LOOP, len(Fi['F'])), Fi['F']))
    for ob, ph, laps, rx, ry, z in Fi['fish']:
        a = ph + 2 * math.pi * laps * u; cx, cy = W.POND_C[0] + 0.05, -1.30
        ob.location = (cx + rx * math.cos(a), cy + ry * math.sin(a), z + 0.02 * math.sin(2 * a))
        ob.rotation_euler = (0, 0, a + math.pi / 2 + 0.15 * math.sin(2 * math.pi * 24 * u))

# ------------------------------------------------------------------ squirrel (autumn) and its acorn cache
def build_squirrel(kit):
    bpy = kit.bpy; fur = cw.mat_simple(kit, 'sz_fur', (0.56, 0.28, 0.12), 0.8, noise_amt=0.2); A = cw._Acc(); k = 1.4
    parts = [((0, 0, 0.022), (0.030, 0.016, 0.018)), ((0.030, 0, 0.034), (0.014, 0.013, 0.013)), ((0.036, 0.007, 0.048), (0.003, 0.003, 0.007)),
             ((0.036, -0.007, 0.048), (0.003, 0.003, 0.007)), ((0.010, 0.010, 0.006), (0.008, 0.004, 0.006)), ((0.010, -0.010, 0.006), (0.008, 0.004, 0.006))]
    for c, r in parts: v, f = _ell(np.array(c) * k, np.array(r) * k); A.add(v, f)
    for i, u in enumerate(np.linspace(0, 1, 7)):                     # bushy tail curling up behind
        c = np.array([-0.030 - 0.02 * math.sin(u * 2.4), 0, 0.02 + 0.06 * u]) * k; r = (0.012 + 0.006 * math.sin(u * 3)) * k
        v, f = _ell(c, (r, r, r)); A.add(v, f)
    ob = A.build(bpy, 'sz_squirrel', [fur], True, kit.coll); _hide(ob); return ob

def squirrel_pose(ob, t):
    tree, dig = np.array([1.22, -1.08]), np.array([CACHE[0], -W.H + 0.10])
    if not (6.3 <= t < 8.9): _hide(ob); return
    if t < 6.9: u = (t - 6.3) / 0.6; p = tree + (dig - tree) * u; hd = math.atan2(*(dig - tree)[::-1]); bob = 0.012 * abs(math.sin(u * math.pi * 4)); sc = min(1, u * 6)
    elif t < 8.1: p = dig; hd = -math.pi / 2; bob = 0.006 * abs(math.sin((t - 6.9) * 18)); sc = 1.0
    else: u = (t - 8.1) / 0.8; p = dig + (tree - dig) * u; hd = math.atan2(*(tree - dig)[::-1]); bob = 0.012 * abs(math.sin(u * math.pi * 4)); sc = min(1, (1 - u) * 6)
    ob.location = (p[0], p[1], W.H_at(p[0], p[1]) + bob); ob.rotation_euler = (0.25 if 6.9 <= t < 8.1 else 0.0, 0, hd); ob.scale = (sc, sc, sc)

def build_cache(kit):
    """Acorns in a pocket under the bank, behind a hole in the front cut face (the hole is cut in szmats strata)."""
    bpy = kit.bpy; x, rx, rz = CACHE; zc = W.H_at(x, -W.H + 0.003) - 0.13
    mud = bpy.data.materials.get('sz_cavity') or cw.mat_simple(kit, 'sz_cavity', (0.17, 0.12, 0.08), 0.95, noise_amt=0.45, bump=0.5)
    nut = cw.mat_simple(kit, 'sz_acorn', (0.58, 0.36, 0.14), 0.4); cap = cw.mat_simple(kit, 'sz_acorncap', (0.32, 0.22, 0.12), 0.8, noise_amt=0.4)
    A = cw._Acc(); th = np.linspace(0, math.pi / 2, 7); ph = np.linspace(0, 2 * math.pi, 21)[:-1]; V = []; Fc = []
    for a in th:
        for b in ph: V.append((x + rx * 1.25 * math.sin(a) * math.cos(b), -W.H + 0.0006 + 0.09 * math.cos(a), zc + rz * 1.3 * math.sin(a) * math.sin(b)))
    for i in range(len(th) - 1):
        for j in range(len(ph)): Fc.append((i * 20 + j, i * 20 + (j + 1) % 20, (i + 1) * 20 + (j + 1) % 20, (i + 1) * 20 + j))
    A.add(V, Fc, 0)
    rng = np.random.default_rng(3)
    for k in range(6):
        c = np.array([x + rng.uniform(-0.035, 0.035), -W.H + 0.035 + rng.uniform(0, 0.03), zc - 0.022 + rng.uniform(0, 0.025)])
        v, f = _ell(c, (0.010, 0.010, 0.014)); A.add(v, f, 1); v, f = _ell(c + (0, 0, 0.010), (0.011, 0.011, 0.006)); A.add(v, f, 2)
    return A.build(bpy, 'sz_cache', [mud, nut, cap], True, kit.coll), zc

# ------------------------------------------------------------------ robin and tracks in the snow (winter)
def build_robin(kit):
    bpy = kit.bpy; A = cw._Acc(); k = 1.4
    for c, r, m in [((0, 0, 0.02), (0.022, 0.017, 0.018), 0), ((0.016, 0, 0.016), (0.013, 0.013, 0.013), 1), ((0.020, 0, 0.034), (0.011, 0.011, 0.011), 0),
                    ((0.032, 0, 0.034), (0.006, 0.002, 0.002), 2), ((-0.026, 0, 0.026), (0.014, 0.006, 0.003), 0)]:
        v, f = _ell(np.array(c) * k, np.array(r) * k); A.add(v, f, m)
    ob = A.build(bpy, 'sz_robin', [cw.mat_simple(kit, 'sz_robinback', (0.40, 0.34, 0.26), 0.7), cw.mat_simple(kit, 'sz_robinbreast', (0.90, 0.42, 0.14), 0.6),
                                   cw.mat_simple(kit, 'sz_robinbeak', (0.10, 0.08, 0.06), 0.5)], True, kit.coll)
    _hide(ob)
    hops = [np.array(p) for p in ((0.62, -0.72), (0.70, -0.80), (0.76, -0.90), (0.86, -0.96), (0.92, -1.06), (0.88, -1.17), (0.96, -1.26), (1.06, -1.30))]
    tm = mk_tracks(kit, hops)
    return {'ob': ob, 'hops': hops, 'tracks': tm}

def mk_tracks(kit, hops):
    V = []; F = []
    for p in hops:
        for side in (-1, 1):
            for j in range(3):                                          # three toes per foot
                a = side * 0.35 + (j - 1) * 0.45; c = p + np.array([0.0, side * 0.008])
                o = len(V); h = W.H_at(*c) + 0.0025
                V += [(c[0], c[1], h), (c[0] + 0.012 * math.cos(a), c[1] + 0.012 * math.sin(a), h), (c[0] + 0.012 * math.cos(a + 0.2), c[1] + 0.012 * math.sin(a + 0.2), h)]
                F.append((o, o + 1, o + 2))
    ob = cw.mk_mesh(kit.bpy, 'sz_tracks', V, F, [cw.mat_simple(kit, 'sz_track', (0.55, 0.60, 0.70), 0.9)], None, False, kit.coll)
    return {'ob': ob, 'co': np.array(V, np.float32), 'per': 6 * 3}

def robin_pose(R, t):
    ob, hops = R['ob'], R['hops']; t0, dt = 10.0, 0.16; n = len(hops); tr = R['tracks']
    if 9.7 <= t < 11.35:
        if t < t0:                                                      # flies down
            u = (t - 9.7) / (t0 - 9.7); p = hops[0]; ob.location = (p[0] - 0.3 * (1 - u), p[1] + 0.2 * (1 - u), W.H_at(*p) + 0.004 + 0.5 * (1 - u) ** 2); hd = -0.6
        elif t < t0 + dt * (n - 1):
            s = (t - t0) / dt; i = int(s); f = s - i; a, b = hops[i], hops[i + 1]; p = a + (b - a) * f
            ob.location = (p[0], p[1], W.H_at(*p) + 0.004 + 0.03 * math.sin(math.pi * f)); hd = math.atan2(*(b - a)[::-1])
        elif t < 11.0:
            p = hops[-1]; ob.location = (p[0], p[1], W.H_at(*p) + 0.004); hd = -0.9 + 0.5 * math.sin(t * 9)
        else:
            u = (t - 11.0) / 0.35; p = hops[-1]; ob.location = (p[0] + 0.4 * u, p[1] - 0.1 * u, W.H_at(*p) + 0.004 + 0.6 * u * u); hd = -0.2
        ob.rotation_euler = (0, 0, hd); ob.scale = (1, 1, 1)
    else:
        _hide(ob)
    # tracks: each print appears when the robin lands there and melts with the thaw
    co = tr['co'].copy(); land = t0 + dt * np.arange(n); melt = 1 - W.smooth(11.2, 11.7, t)
    for i in range(n):
        seen = (land[i] <= t < 11.8) * melt; blk = co[i * tr['per']:(i + 1) * tr['per']]
        c = blk.mean(0); blk[:] = c + (blk - c) * seen; blk[:, 2] -= 0 if seen > 0 else 50
        co[i * tr['per']:(i + 1) * tr['per']] = blk
    me = tr['ob'].data; me.vertices.foreach_set('co', co.ravel()); me.update()

# ------------------------------------------------------------------ easter eggs and the title
def build_fossil(kit):
    """An ammonite in the right cut face: a flat decal just in front of the wall, a log spiral with ribs."""
    bpy = kit.bpy; y0, z0, R = FOSSIL; m = cw._new_mat(bpy, 'sz_fossil'); g = G(m.node_tree, kit)
    oc = g.node('ShaderNodeTexCoord').outputs['Object']; s = g.sep(oc); u, v = s[1], s[2]
    r = g.math('MAXIMUM', g.math('SQRT', g.math('ADD', g.math('MULTIPLY', u, u), g.math('MULTIPLY', v, v))), 1e-4); th = g.math('ARCTAN2', v, u)
    k = 1 / math.log(2.4)                                              # the shell widens 2.4 times per turn
    whorl = g.math('FRACT', g.math('SUBTRACT', g.math('MULTIPLY', g.math('LOGARITHM', g.math('DIVIDE', r, R), math.e), k), g.math('DIVIDE', th, 2 * math.pi)))
    ribs = g.math('POWER', g.math('ABSOLUTE', g.math('SINE', g.math('MULTIPLY', th, 22.0))), 6.0)
    line = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MINIMUM', whorl, g.math('SUBTRACT', 1.0, whorl)), 14.0), clamp=True)
    col = g.mix(g.math('MULTIPLY', ribs, 0.35), srgb((0.80, 0.74, 0.62)), srgb((0.64, 0.58, 0.48)))
    col = g.mix(line, col, srgb((0.30, 0.25, 0.20)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.7})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.6, 'Height': g.math('ADD', g.math('MULTIPLY', ribs, 0.3), g.math('MULTIPLY', line, -1.0)), 'Distance': 0.004}); g.put(p, 'Normal', b)
    a = g.math('MULTIPLY', g.math('SUBTRACT', R, r), 300.0, clamp=True)
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader'); g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(p, mx.inputs[2])
    cw._finish(g, mx)
    n = 48; V = [(0, 0, 0)] + [(0, R * math.cos(2 * math.pi * i / n), R * math.sin(2 * math.pi * i / n)) for i in range(n)]
    ob = cw.mk_mesh(bpy, 'sz_fossil', V, [(0, i + 1, (i + 1) % n + 1) for i in range(n)], [m], None, False, kit.coll)
    ob.location = (W.H + 0.0008, y0, z0); return ob

def build_title(kit, cam, root, text='One pond. One year.'):
    bpy = kit.bpy; cu = bpy.data.curves.new('sz_title', 'FONT'); cu.body = text; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    font = os.path.join(root, 'films', 'cutaway', 'ads', 'drainage', 'fonts', 'InterTight-SemiBold.ttf')
    if os.path.exists(font): cu.font = bpy.data.fonts.load(font)
    cu.size = 0.125; cu.space_character = 1.04
    ob = bpy.data.objects.new('sz_title', cu); kit.coll.objects.link(ob)
    m = cw._new_mat(bpy, 'sz_titlemat'); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.20, 0.18, 0.16)), 'Strength': 1.0}); cw._finish(g, e); cu.materials.append(m)
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
    ob.parent = cam.ob; d = 5.0; top = d * 18.0 / 55.0                  # half the frame height at distance d (vertical sensor fit)
    ob.location = (0.0, top * 0.56, -d)
    return ob
