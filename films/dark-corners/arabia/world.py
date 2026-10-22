"""World of the Arabia film: sand-clay terrain (analytic height field, coarse + fine tiles), painted card sky with pin-hole stars,
a clay moon, cut-card far dunes, lights. Metres, +Y away from the main camera, +Z up."""
import math
import numpy as np
from kit import *
from kit import _mat, _light, _camera_branch

# ----------------------------------------------------------------------------------------------- places (world coords)
TENT1 = (1.45, 1.60)         # the old man's tent (open front, lamp inside)
TENT2 = (2.35, 1.78)         # the woman's tent (closed, glowing cloth)
PADS = [  # (x, y, inner radius, outer radius): flattened clay where puppets and props stand
    (TENT1[0], TENT1[1], 0.30, 0.62), (TENT2[0], TENT2[1], 0.30, 0.62), (1.7, 0.85, 0.32, 0.66), (0.35, 0.85, 0.30, 0.6),
    (-1.7, 1.55, 0.35, 0.8), (-1.0, 2.3, 0.22, 0.5), (-2.1, 1.1, 0.35, 0.8), (0.0, 0.0, 0.35, 0.8), (0.9, 0.25, 0.35, 0.8),
]
TRACK_PTS = [(-3.9, 3.05), (-3.0, 2.75), (-2.2, 2.55), (-1.4, 2.10), (-0.6, 2.02), (0.1, 1.85), (0.55, 1.70), (0.85, 1.60)]
MECCA_X = 9.0
CAMP = [(-3.30, 3.02), (-2.88, 3.14), (-2.46, 3.00), (-2.04, 3.16), (-1.62, 3.05), (-1.20, 3.18)]
PADS += [(x, y, 0.18, 0.34) for (x, y) in CAMP]
# (x, y, half width, half depth, height, windows, door): the toy town of Mecca, fronts facing the camera
MECCA_HOUSES = [(7.55, 2.50, 0.11, 0.09, 0.11, 1, False), (8.20, 2.62, 0.13, 0.10, 0.15, 2, False), (9.00, 2.50, 0.14, 0.11, 0.13, 1, True), (9.75, 2.64, 0.12, 0.10, 0.17, 2, False),
                (10.45, 2.52, 0.12, 0.09, 0.12, 1, False), (8.00, 3.55, 0.13, 0.10, 0.18, 2, False), (8.95, 3.65, 0.14, 0.10, 0.14, 1, False), (9.90, 3.55, 0.13, 0.10, 0.19, 2, False)]

def _sines(seed, n, kmin, kmax, amp0):
    rs = np.random.RandomState(seed); out = []
    for i in range(n):
        k = rs.uniform(kmin, kmax); a = rs.uniform(0, 2 * math.pi)
        out.append((amp0 * rs.uniform(0.5, 1.0) / (1 + 0.3 * i), k * math.cos(a), k * math.sin(a), rs.uniform(0, 2 * math.pi)))
    return out
_LOW = _sines(5, 7, 1.2, 3.8, 0.02)

def base_h(x, y):
    w = 0.30 * np.sin(1.1 * x + 0.8 * y + 0.7) + 0.16 * np.sin(2.7 * x - 1.9 * y + 2.1)
    a = math.radians(-18); k = 2 * math.pi / 1.45
    u = (x * math.cos(a) + y * math.sin(a)) * k + w * 2.0
    s = np.sin(u) + 0.32 * np.sin(2 * u + 0.9)
    h = 0.040 * s
    for (am, kx, ky, ph) in _LOW: h = h + am * np.sin(kx * x + ky * y + ph)
    # the far edge rises into a big dune wall that hides the foot of the sky card
    h = h + 0.30 * smoothv(3.5, 4.6, y) * (0.75 + 0.25 * np.sin(1.3 * x + 0.4))
    # front edge drops a little so the camera can sit low
    return h

def smoothv(a, b, x):
    u = np.clip((x - a) / (b - a), 0.0, 1.0); return u * u * (3 - 2 * u)

def terrain_h(x, y):
    h = base_h(x, y)
    for (px, py, r0, r1) in PADS:
        d = np.sqrt((x - px) ** 2 + ((y - py) * 1.15) ** 2); w = 1.0 - smoothv(r0, r1, d)
        hc = float(base_h(np.array(px), np.array(py)))
        h = h * (1 - w) + (hc * 0.5) * w
    return h

# ----------------------------------------------------------------------------------------------- tracks
def spline_pts(pts, step):
    P = np.array(pts, float); n = max(4, int(sum(np.linalg.norm(P[1:] - P[:-1], axis=1)) / step * 3))
    C = catmull(P, n); seg = np.linalg.norm(C[1:] - C[:-1], axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    return C, s

def camel_prints(pts, lateral, stride, phase=0.0, a=0.013, b=0.010):
    """Alternating left/right pad prints along a path -> [(x, y, dir_x, dir_y, a, b)]."""
    C, s = spline_pts(pts, 0.01); out = []
    for side in (-1, 1):
        d = phase + (0.0 if side < 0 else stride / 2)
        while d < s[-1] - 0.05:
            i = int(np.searchsorted(s, d)); i = min(i, len(C) - 2)
            t = C[i + 1] - C[i]; t /= np.linalg.norm(t); n = np.array([-t[1], t[0]])
            p = C[i] + n * lateral * side
            out.append((p[0], p[1], t[0], t[1], a, b)); d += stride
    return out

def build_prints():
    pr = []
    pr += camel_prints([(x, y - 0.00) for x, y in TRACK_PTS], 0.020, 0.085, 0.0)
    pr += camel_prints([(x + 0.0, y + 0.075) for x, y in TRACK_PTS], 0.019, 0.083, 0.03)
    return pr
PRINTS = build_prints()

def apply_prints(X, Y, H):
    """Add the dents to a regular grid (X, Y 1-D axes); slices a local window per print."""
    x0, y0 = X[0], Y[0]; dx = X[1] - X[0]; dy = Y[1] - Y[0]
    for (px, py, tx, ty, a, b) in PRINTS:
        R = 1.5 * max(a, b) + 0.01
        i0 = int(math.floor((px - R - x0) / dx)); i1 = int(math.ceil((px + R - x0) / dx)); j0 = int(math.floor((py - R - y0) / dy)); j1 = int(math.ceil((py + R - y0) / dy))
        if i1 < 0 or j1 < 0 or i0 >= len(X) or j0 >= len(Y): continue
        i0, j0 = max(i0, 0), max(j0, 0); i1, j1 = min(i1, len(X) - 1), min(j1, len(Y) - 1)
        gx, gy = np.meshgrid(X[i0:i1 + 1], Y[j0:j1 + 1], indexing='ij')
        u = (gx - px) * tx + (gy - py) * ty; v = -(gx - px) * ty + (gy - py) * tx
        r2 = (u / a) ** 2 + (v / b) ** 2
        dent = np.clip(1 - r2, 0.0, None) ** 1.5 * -0.0042 + 0.0011 * np.exp(-((np.sqrt(r2) - 1.25) / 0.3) ** 2)
        H[i0:i1 + 1, j0:j1 + 1] += dent

def grid_mesh(X, Y, H, cell_mask=None):
    nx, ny = len(X), len(Y)
    gx, gy = np.meshgrid(X, Y, indexing='ij')
    V = np.stack([gx, gy, H], -1).reshape(-1, 3)
    idx = np.arange(nx * ny).reshape(nx, ny)
    a = idx[:-1, :-1]; b = idx[1:, :-1]; c = idx[1:, 1:]; d = idx[:-1, 1:]
    F = np.stack([a, b, c, d], -1)
    if cell_mask is not None: F = F[cell_mask]
    F = F.reshape(-1, 4)
    used = np.unique(F); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used))
    return V[used], remap[F]

def make_mesh(bpy, name, V, F, mat, coll):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V)); me.vertices.foreach_set('co', np.asarray(V, np.float32).ravel())
    me.loops.add(F.size); me.loops.foreach_set('vertex_index', F.ravel().astype(np.int32))
    me.polygons.add(len(F)); me.polygons.foreach_set('loop_start', np.arange(0, F.size, 4, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(len(F), 4, np.int32))
    me.polygons.foreach_set('use_smooth', np.ones(len(F), bool)); me.update(); me.validate()
    if mat is not None: me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

def snap(v, lo, step): return lo + step * round((v - lo) / step)

def build_terrain(bpy, mat, coll, region=(-4.2, 4.2, -1.5, 4.6), cs=0.024, fs=0.006, fine=None, fn=terrain_h, prints=True, name='sand'):
    x0, x1, y0, y1 = region
    nx = int(round((x1 - x0) / cs)); ny = int(round((y1 - y0) / cs))
    X = x0 + cs * np.arange(nx + 1); Y = y0 + cs * np.arange(ny + 1)
    rects = []
    for (a, b, c, d) in (fine or []):
        rects.append((snap(a, x0, cs), snap(b, x0, cs), snap(c, y0, cs), snap(d, y0, cs)))
    gx, gy = np.meshgrid(X, Y, indexing='ij'); H = fn(gx, gy)
    if prints: apply_prints(X, Y, H)
    cm = np.ones((nx, ny), bool)
    cx = (X[:-1] + X[1:]) / 2; cy = (Y[:-1] + Y[1:]) / 2
    for (a, b, c, d) in rects: cm &= ~(((cx[:, None] > a) & (cx[:, None] < b)) & ((cy[None, :] > c) & (cy[None, :] < d)))
    V, F = grid_mesh(X, Y, H, cm); objs = [make_mesh(bpy, name, V, F, mat, coll)]
    for k, (a, b, c, d) in enumerate(rects):
        fx = np.arange(int(round((b - a) / fs)) + 1) * fs + a; fy = np.arange(int(round((d - c) / fs)) + 1) * fs + c
        gx, gy = np.meshgrid(fx, fy, indexing='ij'); Hf = fn(gx, gy)
        if prints: apply_prints(fx, fy, Hf)
        V, F = grid_mesh(fx, fy, Hf); objs.append(make_mesh(bpy, f'{name}_fine{k}', V, F, mat, coll))
    return objs


# ----------------------------------------------------------------------------------------------- sky, stars, moon, far dunes
def sky_material(bpy):
    """Painted card sky (self-lit): night indigo gradient <-> dawn peach gradient (Value node 'dawn'), brush streaks."""
    m, N, L, p, out = _mat(bpy, 'card_sky')
    for n in list(N):
        if n.type not in ('OUTPUT_MATERIAL',): N.remove(n)
    out = N['Material Output']
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs['Vector'])
    zr = N.new('ShaderNodeMapRange'); zr.inputs['From Min'].default_value = 0.10; zr.inputs['From Max'].default_value = 3.0; zr.clamp = True
    zr.interpolation_type = 'SMOOTHSTEP'; L.new(sep.outputs['Z'], zr.inputs['Value'])
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.9, 6.0, 20.0); L.new(tc.outputs['Object'], mp.inputs['Vector'])
    ns = N.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 2.0; ns.inputs['Detail'].default_value = 3.0; ns.inputs['Roughness'].default_value = 0.55
    L.new(mp.outputs['Vector'], ns.inputs['Vector'])
    # gradient position perturbed by the brush noise
    ad = N.new('ShaderNodeMath'); ad.operation = 'MULTIPLY_ADD'; L.new(ns.outputs['Fac'], ad.inputs[0]); ad.inputs[1].default_value = 0.22; L.new(zr.outputs['Result'], ad.inputs[2])
    ad2 = N.new('ShaderNodeMath'); ad2.operation = 'SUBTRACT'; L.new(ad.outputs['Value'], ad2.inputs[0]); ad2.inputs[1].default_value = 0.11
    def ramp(stops):
        r = N.new('ShaderNodeValToRGB'); r.color_ramp.interpolation = 'EASE'
        while len(r.color_ramp.elements) < len(stops): r.color_ramp.elements.new(0.5)
        for i, (pos, c) in enumerate(stops): r.color_ramp.elements[i].position = pos; r.color_ramp.elements[i].color = srgb(c)
        L.new(ad2.outputs['Value'], r.inputs['Fac']); return r
    night = ramp([(0.0, (0.20, 0.28, 0.52)), (0.35, (0.11, 0.16, 0.38)), (1.0, (0.035, 0.05, 0.16))])
    dawn = ramp([(0.0, (1.00, 0.66, 0.42)), (0.30, (0.88, 0.58, 0.58)), (0.65, (0.50, 0.46, 0.68)), (1.0, (0.16, 0.22, 0.46))])
    dv = N.new('ShaderNodeValue'); dv.outputs[0].default_value = 0.0
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    L.new(dv.outputs[0], sock(mx.inputs, 'Factor_Float')); L.new(night.outputs['Color'], sock(mx.inputs, 'A_Color')); L.new(dawn.outputs['Color'], sock(mx.inputs, 'B_Color'))
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 0.9; L.new(sock(mx.outputs, 'Result_Color'), em.inputs['Color'])
    L.new(em.outputs['Emission'], out.inputs['Surface'])
    return m, dv, em

def radial_glow(bpy, name, col, strength, r_in, r_out):
    """Soft painted halo: emission fading to transparent with distance from the object's centre (object coords, disc in XZ)."""
    m, N, L, p, out = _mat(bpy, name)
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL': N.remove(n)
    out = N['Material Output']
    tc = N.new('ShaderNodeTexCoord'); vm = N.new('ShaderNodeVectorMath'); vm.operation = 'LENGTH'; L.new(tc.outputs['Object'], vm.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = r_in; mr.inputs['From Max'].default_value = r_out; mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    mr.interpolation_type = 'SMOOTHSTEP'; mr.clamp = True; L.new(vm.outputs['Value'], mr.inputs['Value'])
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = srgb(col); em.inputs['Strength'].default_value = strength
    tr = N.new('ShaderNodeBsdfTransparent'); ms = N.new('ShaderNodeMixShader')
    L.new(mr.outputs['Result'], ms.inputs['Fac']); L.new(tr.outputs['BSDF'], ms.inputs[1]); L.new(em.outputs['Emission'], ms.inputs[2]); L.new(ms.outputs['Shader'], out.inputs['Surface'])
    return m, em

def disc_mesh(r, seg=24, z=0.0):
    V = [(0, 0, 0)] + [(r * math.cos(2 * math.pi * j / seg), 0.0, r * math.sin(2 * math.pi * j / seg)) for j in range(seg)]
    F = [(0, 1 + j, 1 + (j + 1) % seg) for j in range(seg)]
    return V, F

def build_sky(bpy, coll, S, W=(-16.0, 18.0)):
    from mathutils import Vector, noise
    SKY_Y = 4.95
    mat, dv, em = sky_material(bpy); S['sky_dawn_nodes'] = [dv]; S['sky_em'] = em
    nx, nz = 80, 30; V, F = [], []
    for j in range(nz + 1):
        z = -0.3 + 6.8 * j / nz
        for i in range(nx + 1):
            x = W[0] + (W[1] - W[0]) * i / nx; V.append((x, SKY_Y + 0.05 * math.sin(x * 0.4) + 0.12 * z, z))
    for j in range(nz):
        for i in range(nx): a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    S['sky_obj'] = mesh_obj(bpy, 'sky_card', V, [tuple(reversed(f)) for f in F], mat, coll)
    # stars: pin-holes in the card, lit from behind
    rs = np.random.RandomState(7); sm, se = emissive(bpy, 'pinholes', (1.0, 0.93, 0.78), 14.0)
    Vs, Fs = [], []
    for k in range(520):
        x = rs.uniform(W[0] + 0.3, W[1] - 0.3); z = rs.uniform(0.32, 3.4) if k < 380 else rs.uniform(0.32, 1.3); r = rs.uniform(0.0011, 0.0030) * (1.8 if rs.rand() < 0.08 else 1.0)
        y = SKY_Y + 0.05 * math.sin(x * 0.4) + 0.12 * z - 0.004; v, f = disc_mesh(r, 8)
        b = len(Vs); Vs += [(vx + x, y, vz + z) for vx, _, vz in v]; Fs += [tuple(b + i for i in tri) for tri in f]
    me = bpy.data.meshes.new('stars'); me.from_pydata(Vs, [], Fs); me.update(); me.materials.append(sm)
    so = bpy.data.objects.new('stars', me); coll.objects.link(so); set_vis(so, False); S['stars'] = so; S['stars_em'] = se
    return SKY_Y

def build_moon(bpy, coll, S, pos=(-0.7, 4.80, 2.15), r=0.20):
    # moon: pale card disc with painted maria + a soft halo painted on card
    m, N, L, p, out = _mat(bpy, 'moon')
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL': N.remove(n)
    out = N['Material Output']
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 7.0; nz.inputs['Detail'].default_value = 4.0
    vm = N.new('ShaderNodeVectorMath'); vm.operation = 'SCALE'; vm.inputs['Scale'].default_value = 1.0 / r
    L.new(tc.outputs['Object'], vm.outputs and vm.inputs[0]); L.new(vm.outputs['Vector'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.42; cr.color_ramp.elements[1].position = 0.60
    cr.color_ramp.elements[0].color = srgb((0.80, 0.78, 0.66)); cr.color_ramp.elements[1].color = srgb((1.0, 0.97, 0.84)); L.new(nz.outputs['Fac'], cr.inputs['Fac'])
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 2.6; L.new(cr.outputs['Color'], em.inputs['Color']); L.new(em.outputs['Emission'], out.inputs['Surface'])
    v, f = disc_mesh(r, 64); mo = bpy.data.objects.new('moon', bpy.data.meshes.new('moon')); mo.data.from_pydata(v, [], f); mo.data.update(); mo.data.materials.append(m)
    coll.objects.link(mo); mo.location = pos; set_vis(mo, False)
    hm, hem = radial_glow(bpy, 'moon_halo', (0.62, 0.72, 1.0), 0.55, 0.0, r * 3.6)
    v2, f2 = disc_mesh(r * 3.6, 64); ho = bpy.data.objects.new('moon_halo', bpy.data.meshes.new('moon_halo')); ho.data.from_pydata(v2, [], f2); ho.data.update(); ho.data.materials.append(hm)
    coll.objects.link(ho); ho.location = (pos[0], pos[1] - 0.004, pos[2]); set_vis(ho, False)
    S['moon'], S['moon_halo'], S['moon_em'], S['halo_em'] = mo, ho, em, hem

def cut_dunes(bpy, coll, mat, name, y, x0, x1, base_z, amp, seed, thick=0.006):
    """Cut-card dune silhouette: a flat card with a smooth ridge line on top (stands on the table, faces -Y)."""
    rs = np.random.RandomState(seed); ph = rs.uniform(0, 6.28, 4); n = int((x1 - x0) / 0.04)
    xs = np.linspace(x0, x1, n + 1)
    top = base_z + amp * (0.55 + 0.30 * np.sin(xs * 0.75 + ph[0]) + 0.20 * np.sin(xs * 1.7 + ph[1]) + 0.10 * np.sin(xs * 3.3 + ph[2]))
    V = [(x, y, -0.15) for x in xs] + [(x, y, z) for x, z in zip(xs, top)] + [(x, y + thick, -0.15) for x in xs] + [(x, y + thick, z) for x, z in zip(xs, top)]
    k = n + 1; F = [(i, i + 1, k + i + 1, k + i) for i in range(n)] + [(2 * k + i + 1, 2 * k + i, 3 * k + i, 3 * k + i + 1) for i in range(n)]
    F += [(k + i, k + i + 1, 3 * k + i + 1, 3 * k + i) for i in range(n)]    # top lip
    return mesh_obj(bpy, name, V, F, mat, coll)

def make_lights(bpy, coll, S):
    S['moon_light'] = _light(bpy, coll, 'moon_light', 'SUN', (0, 0, 3), rot=(0, 0, 0), energy=1.0, size=math.radians(4.0), kelvin=9500)
    S['fill'] = _light(bpy, coll, 'cam_fill', 'AREA', (0, -1, 1), (0, 0, 0), energy=10.0, size=0.5, kelvin=8000)
    wd = bpy.data.worlds.new('night'); bpy.context.scene.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    bg = wd.node_tree.nodes.get('Background'); S['world_bg'] = bg
    if bg is not None: bg.inputs['Color'].default_value = (0.05, 0.07, 0.16, 1.0); bg.inputs['Strength'].default_value = 0.5
