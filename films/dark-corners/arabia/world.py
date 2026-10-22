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
    # a second, lower crest in front of it: a layered dune scape (the camp row sits in the hollow before it)
    h = h + 0.075 * np.exp(-((y - 3.78) / 0.26) ** 2) * (0.72 + 0.28 * np.sin(1.9 * x + 0.6))
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
# The sky lives in its OWN Blender scene (S['sky_scene']) rendered without depth of field and alpha-composited UNDER the table
# scene. A card 5 m away from a lens focused at 0.4 m is a 30 px blur disc: that is why the old pin-hole stars read as bokeh.
SKY_Y = 4.95
def band_z(x):
    """Centre line of the Milky Way across the card (a gentle wave, tilted about 25 degrees near the camp)."""
    return 2.3 + 1.0 * np.sin(0.45 * (x + 1.8))

def sky_material(bpy):
    """Painted card sky (self-lit): night indigo gradient <-> dawn peach gradient (Value node 'dawn'), brush streaks, a faint Milky Way band."""
    m, N, L, p, out = _mat(bpy, 'card_sky')
    for n in list(N):
        if n.type not in ('OUTPUT_MATERIAL',): N.remove(n)
    out = N['Material Output']
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs['Vector'])
    zr = N.new('ShaderNodeMapRange'); zr.inputs['From Min'].default_value = 0.10; zr.inputs['From Max'].default_value = 3.6; zr.clamp = True
    zr.interpolation_type = 'SMOOTHSTEP'; L.new(sep.outputs['Z'], zr.inputs['Value'])
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.9, 6.0, 20.0); L.new(tc.outputs['Object'], mp.inputs['Vector'])
    ns = N.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 2.0; ns.inputs['Detail'].default_value = 3.0; ns.inputs['Roughness'].default_value = 0.55
    L.new(mp.outputs['Vector'], ns.inputs['Vector'])
    ad = N.new('ShaderNodeMath'); ad.operation = 'MULTIPLY_ADD'; L.new(ns.outputs['Fac'], ad.inputs[0]); ad.inputs[1].default_value = 0.22; L.new(zr.outputs['Result'], ad.inputs[2])
    ad2 = N.new('ShaderNodeMath'); ad2.operation = 'SUBTRACT'; L.new(ad.outputs['Value'], ad2.inputs[0]); ad2.inputs[1].default_value = 0.11
    def ramp(stops):
        r = N.new('ShaderNodeValToRGB'); r.color_ramp.interpolation = 'EASE'
        while len(r.color_ramp.elements) < len(stops): r.color_ramp.elements.new(0.5)
        for i, (pos, c) in enumerate(stops): r.color_ramp.elements[i].position = pos; r.color_ramp.elements[i].color = srgb(c)
        L.new(ad2.outputs['Value'], r.inputs['Fac']); return r
    night = ramp([(0.0, (0.20, 0.27, 0.50)), (0.30, (0.10, 0.145, 0.36)), (1.0, (0.030, 0.045, 0.15))])
    dawn = ramp([(0.0, (1.00, 0.66, 0.42)), (0.30, (0.88, 0.58, 0.58)), (0.65, (0.50, 0.46, 0.68)), (1.0, (0.16, 0.22, 0.46))])
    dv = N.new('ShaderNodeValue'); dv.outputs[0].default_value = 0.0
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    L.new(dv.outputs[0], sock(mx.inputs, 'Factor_Float')); L.new(night.outputs['Color'], sock(mx.inputs, 'A_Color')); L.new(dawn.outputs['Color'], sock(mx.inputs, 'B_Color'))
    # Milky Way: a soft band along band_z(x), broken by cloudy noise, faded out at dawn
    a1 = N.new('ShaderNodeMath'); a1.operation = 'ADD'; L.new(sep.outputs['X'], a1.inputs[0]); a1.inputs[1].default_value = 1.8
    a2 = N.new('ShaderNodeMath'); a2.operation = 'MULTIPLY'; L.new(a1.outputs['Value'], a2.inputs[0]); a2.inputs[1].default_value = 0.45
    a3 = N.new('ShaderNodeMath'); a3.operation = 'SINE'; L.new(a2.outputs['Value'], a3.inputs[0])
    a4 = N.new('ShaderNodeMath'); a4.operation = 'MULTIPLY_ADD'; L.new(a3.outputs['Value'], a4.inputs[0]); a4.inputs[1].default_value = 1.0; a4.inputs[2].default_value = 2.3
    a5 = N.new('ShaderNodeMath'); a5.operation = 'SUBTRACT'; L.new(sep.outputs['Z'], a5.inputs[0]); L.new(a4.outputs['Value'], a5.inputs[1])
    a6 = N.new('ShaderNodeMath'); a6.operation = 'DIVIDE'; L.new(a5.outputs['Value'], a6.inputs[0]); a6.inputs[1].default_value = 0.46
    a7 = N.new('ShaderNodeMath'); a7.operation = 'MULTIPLY'; L.new(a6.outputs['Value'], a7.inputs[0]); L.new(a6.outputs['Value'], a7.inputs[1])
    a8 = N.new('ShaderNodeMath'); a8.operation = 'MULTIPLY'; L.new(a7.outputs['Value'], a8.inputs[0]); a8.inputs[1].default_value = -1.0
    a9 = N.new('ShaderNodeMath'); a9.operation = 'EXPONENT'; L.new(a8.outputs['Value'], a9.inputs[0])
    mp2 = N.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (3.2, 1.0, 5.5); L.new(tc.outputs['Object'], mp2.inputs['Vector'])
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 2.2; n2.inputs['Detail'].default_value = 4.0; n2.inputs['Roughness'].default_value = 0.5; L.new(mp2.outputs['Vector'], n2.inputs['Vector'])
    n2r = N.new('ShaderNodeMapRange'); n2r.inputs['From Min'].default_value = 0.25; n2r.inputs['From Max'].default_value = 0.80; L.new(n2.outputs['Fac'], n2r.inputs['Value'])
    b1 = N.new('ShaderNodeMath'); b1.operation = 'MULTIPLY'; L.new(a9.outputs['Value'], b1.inputs[0]); L.new(n2r.outputs['Result'], b1.inputs[1])
    inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; L.new(dv.outputs[0], inv.inputs[1])
    b2 = N.new('ShaderNodeMath'); b2.operation = 'MULTIPLY'; L.new(b1.outputs['Value'], b2.inputs[0]); L.new(inv.outputs['Value'], b2.inputs[1])
    b3 = N.new('ShaderNodeMath'); b3.operation = 'MULTIPLY'; L.new(b2.outputs['Value'], b3.inputs[0]); b3.inputs[1].default_value = 0.17
    mw = N.new('ShaderNodeMix'); mw.data_type = 'RGBA'; mw.blend_type = 'ADD'
    L.new(b3.outputs['Value'], sock(mw.inputs, 'Factor_Float')); L.new(sock(mx.outputs, 'Result_Color'), sock(mw.inputs, 'A_Color')); sock(mw.inputs, 'B_Color').default_value = srgb((0.60, 0.66, 1.0))
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 0.9; L.new(sock(mw.outputs, 'Result_Color'), em.inputs['Color'])
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

def star_material(bpy, name, strength):
    """Pin-hole: a hole in the card with a lamp behind it. Colour tint and twinkle phase come from the vertex colour (RGB tint, A phase)."""
    m, N, L, p, out = _mat(bpy, name)
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL': N.remove(n)
    out = N['Material Output']
    at = N.new('ShaderNodeVertexColor'); at.layer_name = 'c'
    tw = N.new('ShaderNodeValue'); tw.outputs[0].default_value = 0.0
    m1 = N.new('ShaderNodeMath'); m1.operation = 'MULTIPLY_ADD'; L.new(tw.outputs[0], m1.inputs[0]); m1.inputs[1].default_value = 2.4; L.new(at.outputs['Alpha'], m1.inputs[2])
    m2 = N.new('ShaderNodeMath'); m2.operation = 'SINE'; L.new(m1.outputs['Value'], m2.inputs[0])
    m3 = N.new('ShaderNodeMath'); m3.operation = 'MULTIPLY_ADD'; L.new(m2.outputs['Value'], m3.inputs[0]); m3.inputs[1].default_value = 0.16; m3.inputs[2].default_value = 0.86
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; L.new(m3.outputs['Value'], st.inputs[0]); st.inputs[1].default_value = strength
    em = N.new('ShaderNodeEmission'); L.new(at.outputs['Color'], em.inputs['Color']); L.new(st.outputs['Value'], em.inputs['Strength'])
    L.new(em.outputs['Emission'], out.inputs['Surface'])
    return m, tw, st

def star_mesh(bpy, name, pts, mat, coll, seg=8, glint=False):
    """pts = [(x, y, z, r, (cr, cg, cb), phase)]; one disc (and an optional 4-point glint of two hair-thin cards) per star."""
    Vs, Fs, Cs = [], [], []
    for (x, y, z, r, col, ph) in pts:
        v, f = disc_mesh(r, seg); b = len(Vs)
        Vs += [(vx + x, y, vz + z) for vx, _, vz in v]; Fs += [tuple(b + i for i in tri) for tri in f]; Cs += [col + (ph,)] * len(v)
        if glint:
            for (ax, az) in ((1, 0), (0, 1)):
                b = len(Vs); L_, w = r * 3.0, r * 0.20
                quad = [(-L_ * ax - w * az, 0, -L_ * az - w * ax), (L_ * ax - w * az, 0, L_ * az - w * ax), (L_ * ax + w * az, 0, L_ * az + w * ax), (-L_ * ax + w * az, 0, -L_ * az + w * ax)]
                Vs += [(x + qx, y + 0.0004, z + qz) for qx, _, qz in quad]; Fs += [(b, b + 1, b + 2), (b, b + 2, b + 3)]; Cs += [col + (ph,)] * 4
    me = bpy.data.meshes.new(name); me.from_pydata(Vs, [], Fs); me.update()
    ca = me.color_attributes.new('c', 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set('color', np.array(Cs, np.float32).ravel())
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob); return ob

def build_sky(bpy, coll, S, W=(-7.0, 15.5)):
    rs = np.random.RandomState(7)
    mat, dv, em = sky_material(bpy); S['sky_dawn_nodes'] = [dv]; S['sky_em'] = em
    sroot = bpy.data.objects.new('sky_root', None); coll.objects.link(sroot); S['sky_root'] = sroot
    nx, nz = 100, 36; V, F = [], []
    for j in range(nz + 1):
        z = -0.3 + 11.0 * j / nz
        for i in range(nx + 1):
            x = W[0] + (W[1] - W[0]) * i / nx; V.append((x, SKY_Y + 0.05 * math.sin(x * 0.4) + 0.12 * z, z))
    for j in range(nz):
        for i in range(nx): a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    so = mesh_obj(bpy, 'sky_card', V, [tuple(reversed(f)) for f in F], mat, coll); so.parent = sroot; S['sky_obj'] = so
    def ypos(x, z): return SKY_Y + 0.05 * math.sin(x * 0.4) + 0.12 * z - 0.006
    tints = [(1.0, 0.93, 0.80), (0.82, 0.90, 1.0), (1.0, 1.0, 0.96), (1.0, 0.82, 0.62), (0.74, 0.84, 1.0)]
    def scatter(n, rlo, rhi, zlo, zhi, band=None, seed_off=0):
        out = []
        while len(out) < n:
            x = rs.uniform(W[0] + 0.3, W[1] - 0.3)
            if band is None: z = rs.uniform(zlo, zhi)
            else: z = float(band_z(x)) + rs.normal(0, band)
            if z < zlo or z > zhi: continue
            out.append((x, ypos(x, z), z, rs.uniform(rlo, rhi), tints[rs.randint(len(tints))], rs.uniform(0, 6.283)))
        return out
    # (name, count, radius range [m] ~ 0.35..1.7 px at 720x1280, strength, glint)
    classes = [('st_bright', 90, 0.0048, 0.0066, 55.0, True, None), ('st_mid', 1300, 0.0036, 0.0052, 26.0, False, None), ('st_small', 3600, 0.0022, 0.0034, 14.0, False, None), ('st_dust', 2200, 0.0013, 0.0020, 7.0, False, 0.30)]
    S['stars'] = []; S['stars_tw'] = []; S['stars_st'] = []
    for (nm, n, rlo, rhi, strength, glint, band) in classes:
        sm, tw, st = star_material(bpy, nm, strength); pts = scatter(n, rlo, rhi, 0.30, 7.5 if band is None else 6.0, band)
        ob = star_mesh(bpy, nm, pts, sm, coll, seg=8 if rhi > 0.003 else 6, glint=glint); ob.parent = sroot
        S['stars'].append(ob); S['stars_tw'].append(tw); S['stars_st'].append((st, strength))
    # painted wisps of cloud drifting along the card (moon-lit, they blush at dawn)
    cm = wisp_material(bpy, 'wisp'); S['wisps'] = []
    for k, (x, z, sx, sz) in enumerate(((-2.6, 2.9, 1.5, 0.16), (0.9, 3.5, 1.9, 0.20), (-0.6, 1.55, 1.1, 0.11), (3.4, 2.5, 1.6, 0.14), (8.6, 2.6, 1.8, 0.17), (10.8, 1.5, 1.2, 0.12), (6.4, 3.4, 1.5, 0.15))):
        v, f = disc_mesh(1.0, 28); o = bpy.data.objects.new(f'wisp{k}', bpy.data.meshes.new(f'wisp{k}')); o.data.from_pydata(v, [], f); o.data.update(); o.data.materials.append(cm)
        coll.objects.link(o); o.scale = (sx, 1.0, sz); o.location = (x, SKY_Y - 0.06, z); S['wisps'].append((o, x, z)); o.parent = sroot
    return SKY_Y

def wisp_material(bpy, name):
    m, N, L, p, out = _mat(bpy, name)
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL': N.remove(n)
    out = N['Material Output']
    tc = N.new('ShaderNodeTexCoord'); vm = N.new('ShaderNodeVectorMath'); vm.operation = 'LENGTH'; L.new(tc.outputs['Object'], vm.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.15; mr.inputs['From Max'].default_value = 0.98; mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    mr.interpolation_type = 'SMOOTHSTEP'; mr.clamp = True; L.new(vm.outputs['Value'], mr.inputs['Value'])
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.2, 1.2, 2.6); L.new(tc.outputs['Object'], mp.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.6; nz.inputs['Detail'].default_value = 3.0; L.new(mp.outputs['Vector'], nz.inputs['Vector'])
    nr = N.new('ShaderNodeMapRange'); nr.inputs['From Min'].default_value = 0.38; nr.inputs['From Max'].default_value = 0.70; L.new(nz.outputs['Fac'], nr.inputs['Value'])
    al = N.new('ShaderNodeMath'); al.operation = 'MULTIPLY'; L.new(mr.outputs['Result'], al.inputs[0]); L.new(nr.outputs['Result'], al.inputs[1])
    al2 = N.new('ShaderNodeMath'); al2.operation = 'MULTIPLY'; L.new(al.outputs['Value'], al2.inputs[0]); al2.inputs[1].default_value = 0.45
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = srgb((0.34, 0.42, 0.68)); em.inputs['Strength'].default_value = 0.85
    tr = N.new('ShaderNodeBsdfTransparent'); ms = N.new('ShaderNodeMixShader')
    L.new(al2.outputs['Value'], ms.inputs['Fac']); L.new(tr.outputs['BSDF'], ms.inputs[1]); L.new(em.outputs['Emission'], ms.inputs[2]); L.new(ms.outputs['Shader'], out.inputs['Surface'])
    return m

def build_moon(bpy, coll, S, pos=(-0.7, 4.80, 2.15), r=0.20):
    # moon: pale card disc with painted maria + a painted halo
    m, N, L, p, out = _mat(bpy, 'moon')
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL': N.remove(n)
    out = N['Material Output']
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 7.0; nz.inputs['Detail'].default_value = 4.0
    vm = N.new('ShaderNodeVectorMath'); vm.operation = 'SCALE'; vm.inputs['Scale'].default_value = 1.0 / r
    L.new(tc.outputs['Object'], vm.inputs[0]); L.new(vm.outputs['Vector'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.42; cr.color_ramp.elements[1].position = 0.60
    cr.color_ramp.elements[0].color = srgb((0.80, 0.78, 0.66)); cr.color_ramp.elements[1].color = srgb((1.0, 0.97, 0.84)); L.new(nz.outputs['Fac'], cr.inputs['Fac'])
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 2.6; L.new(cr.outputs['Color'], em.inputs['Color']); L.new(em.outputs['Emission'], out.inputs['Surface'])
    v, f = disc_mesh(r, 64); mo = bpy.data.objects.new('moon', bpy.data.meshes.new('moon')); mo.data.from_pydata(v, [], f); mo.data.update(); mo.data.materials.append(m)
    coll.objects.link(mo); mo.location = pos; mo.parent = S['sky_root']
    hm, hem = radial_glow(bpy, 'moon_halo', (0.50, 0.62, 1.0), 0.30, r * 0.9, r * 3.2)
    v2, f2 = disc_mesh(r * 3.2, 64); ho = bpy.data.objects.new('moon_halo', bpy.data.meshes.new('moon_halo')); ho.data.from_pydata(v2, [], f2); ho.data.update(); ho.data.materials.append(hm)
    coll.objects.link(ho); ho.location = (pos[0], pos[1] + 0.02, pos[2]); ho.parent = S['sky_root']
    S['moon'], S['moon_halo'], S['moon_em'], S['halo_em'] = mo, ho, em, hem
    # the rising sun (dawn): a hot disc and a wide soft halo painted on the card; placed per shot
    sm, sem = emissive(bpy, 'sun_disc', (1.0, 0.80, 0.52), 6.0)
    v3, f3 = disc_mesh(0.11, 48); so = bpy.data.objects.new('sun', bpy.data.meshes.new('sun')); so.data.from_pydata(v3, [], f3); so.data.update(); so.data.materials.append(sm); coll.objects.link(so)
    hm2, hem2 = radial_glow(bpy, 'sun_halo', (1.0, 0.62, 0.38), 1.1, 0.0, 0.95)
    v4, f4 = disc_mesh(0.95, 64); sh = bpy.data.objects.new('sun_halo', bpy.data.meshes.new('sun_halo')); sh.data.from_pydata(v4, [], f4); sh.data.update(); sh.data.materials.append(hm2); coll.objects.link(sh)
    S['sun'], S['sun_halo'], S['sun_em'], S['sun_halo_em'] = so, sh, sem, hem2


RIDGE_Y = 4.86
def ridge_top(x): return 1.02 + 0.30 * (0.55 + 0.30 * np.sin(0.62 * x + 0.9) + 0.20 * np.sin(1.45 * x + 2.1) + 0.10 * np.sin(3.1 * x + 0.3))

def build_ridge(bpy, coll, S, x0=-7.0, x1=15.0):
    """A far dark range painted on card (sky scene) with a caravan of tiny lamps creeping along its crest."""
    m, N, L, p, out = _mat(bpy, 'ridge_far')
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL': N.remove(n)
    out = N['Material Output']; dv = N.new('ShaderNodeValue'); dv.outputs[0].default_value = 0.0
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs['Vector'])
    zr = N.new('ShaderNodeMapRange'); zr.inputs['From Min'].default_value = 0.3; zr.inputs['From Max'].default_value = 1.35; zr.clamp = True; L.new(sep.outputs['Z'], zr.inputs['Value'])
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 1.0, 9.0); L.new(tc.outputs['Object'], mp.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 2.0; L.new(mp.outputs['Vector'], nz.inputs['Vector'])
    def col(a, b, c):
        r = N.new('ShaderNodeValToRGB'); r.color_ramp.interpolation = 'EASE'; r.color_ramp.elements[0].position = 0.0; r.color_ramp.elements[0].color = srgb(a); r.color_ramp.elements[1].position = 1.0; r.color_ramp.elements[1].color = srgb(b)
        mm = N.new('ShaderNodeMath'); mm.operation = 'MULTIPLY_ADD'; L.new(nz.outputs['Fac'], mm.inputs[0]); mm.inputs[1].default_value = 0.25; L.new(zr.outputs['Result'], mm.inputs[2]); L.new(mm.outputs['Value'], r.inputs['Fac']); return r
    nt = col((0.020, 0.026, 0.085), (0.060, 0.075, 0.190), 0); dw = col((0.30, 0.22, 0.42), (0.62, 0.42, 0.52), 0)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(dv.outputs[0], sock(mx.inputs, 'Factor_Float')); L.new(nt.outputs['Color'], sock(mx.inputs, 'A_Color')); L.new(dw.outputs['Color'], sock(mx.inputs, 'B_Color'))
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.0; L.new(sock(mx.outputs, 'Result_Color'), em.inputs['Color']); L.new(em.outputs['Emission'], out.inputs['Surface'])
    xs = np.linspace(x0, x1, int((x1 - x0) / 0.04) + 1); top = ridge_top(xs); n = len(xs)
    V = [(x, RIDGE_Y, -0.3) for x in xs] + [(x, RIDGE_Y, z) for x, z in zip(xs, top)]
    F = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    ob = mesh_obj(bpy, 'ridge_far', V, F, m, coll); S['ridge_dawn'] = dv
    # the caravan: eleven lamps, a camel's length apart, drifting left to right along the crest
    lm, lem = emissive(bpy, 'caravan_lamp', (1.0, 0.70, 0.36), 26.0); gm, gem = radial_glow(bpy, 'caravan_glow', (1.0, 0.62, 0.30), 0.8, 0.0, 0.016); S['caravan_em'] = (lem, gem); S['caravan'] = []
    for k in range(8):
        v, f = disc_mesh(0.0030, 10); o = bpy.data.objects.new(f'cv{k}', bpy.data.meshes.new(f'cv{k}')); o.data.from_pydata(v, [], f); o.data.update(); o.data.materials.append(lm); coll.objects.link(o)
        v2, f2 = disc_mesh(0.020, 20); h = bpy.data.objects.new(f'cvh{k}', bpy.data.meshes.new(f'cvh{k}')); h.data.from_pydata(v2, [], f2); h.data.update(); h.data.materials.append(gm); coll.objects.link(h); h.parent = o; h.location = (0, 0.002, 0)
        S['caravan'].append(o)
    return ob

def place_caravan(S, t, dawn=0.0):
    k_off = 0.016 * t
    for k, o in enumerate(S['caravan']):
        x = -2.4 + (0.17 * k + 0.11 * (k % 3) * (k > 2)) + k_off; z = float(ridge_top(np.array(x))) + 0.012 + 0.0015 * math.sin(t * 2 + k)
        o.location = (x, RIDGE_Y - 0.004, z); o.hide_render = dawn > 0.5

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
