"""Shared clay kit for the Arabia film (adapted from proto/p10-clay/blender.py): helpers, geometry, clay and card materials."""
import math
import os
import shutil
import zlib

import numpy as np

# ----------------------------------------------------------------------------------------------- small helpers
def sock(coll, ident):
    """Socket by identifier (ShaderNodeMix has several sockets per name)."""
    for s in coll:
        if s.identifier == ident: return s
    raise KeyError(ident)

def srgb(c):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (f(c[0]), f(c[1]), f(c[2]), 1.0)

def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def smooth(a, b, x):
    u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u)

def ease(u, k):
    u = clamp(u)
    if k == 'l': return u
    if k == 's': return u * u * (3 - 2 * u)
    if k == 'o': return 1 - (1 - u) ** 2
    if k == 'O': return 1 - (1 - u) ** 3
    if k == 'i': return u * u
    if k == 'I': return u ** 3
    if k == 'h': return 0.0 if u < 1 else 1.0
    raise ValueError(k)

def lerp(a, b, u):
    if isinstance(a, (tuple, list)): return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u

def track(keys, f):
    """keys = [(frame, value[, ease_into_this_key]), ...] sorted by frame (keys sit on even frames: poses are on 2s)."""
    if f <= keys[0][0]: return keys[0][1]
    for k0, k1 in zip(keys, keys[1:]):
        if f <= k1[0]:
            e = k1[2] if len(k1) > 2 else 's'
            return lerp(k0[1], k1[1], ease((f - k0[0]) / float(k1[0] - k0[0]), e))
    return keys[-1][1]

def jit(pf, tag, amp=1.0):
    """Deterministic per-pose jitter in [-amp, amp] (crc32: stable across processes, unlike hash())."""
    h = zlib.crc32(f'{pf}|{tag}'.encode()) & 0xffffffff
    return (h / 4294967295.0 * 2.0 - 1.0) * amp

def catmull(points, n):
    P = np.asarray(points, float); m = len(P)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for k in range(n):
        s = k / (n - 1) * (m - 1); i = min(int(s), m - 2); u = s - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out.append(0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    return np.array(out)

# ----------------------------------------------------------------------------------------------- geometry
def round_caps(C, A, B, start=True, end=True, k=7):
    """Prepend/append hemispherical rings so swept tubes end in rounded clay tips."""
    C, A, B = list(C), list(A), list(B)
    def cap(c, t, a, b):
        pts = []
        for j in range(1, k + 1):
            al = (j / k) * math.radians(88)
            pts.append((c + t * min(a, b) * math.sin(al), a * math.cos(al), b * math.cos(al)))
        return pts
    if start:
        t = np.asarray(C[0]) - np.asarray(C[1]); t /= np.linalg.norm(t)
        pre = cap(np.asarray(C[0]), t, A[0], B[0])[::-1]
        C = [p[0] for p in pre] + C; A = [p[1] for p in pre] + A; B = [p[2] for p in pre] + B
    if end:
        t = np.asarray(C[-1]) - np.asarray(C[-2]); t /= np.linalg.norm(t)
        post = cap(np.asarray(C[-1]), t, A[-1], B[-1])
        C = C + [p[0] for p in post]; A = A + [p[1] for p in post]; B = B + [p[2] for p in post]
    return np.array(C), np.array(A), np.array(B)

def sweep(C, A, B, ring=36, lateral=(0.0, 1.0, 0.0)):
    """Generalised cylinder: elliptic cross-section (A along the lateral axis, B along the curve normal), closed ends."""
    C = np.asarray(C, float); n = len(C); Y = np.asarray(lateral, float)
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
    verts, faces = [], []
    for k in range(n):
        Nk = np.cross(Y, T[k]); Nk /= max(1e-9, np.linalg.norm(Nk)); Bk = np.cross(T[k], Nk)
        for j in range(ring):
            ph = 2 * math.pi * j / ring
            verts.append(C[k] + A[k] * math.cos(ph) * Bk + B[k] * math.sin(ph) * Nk)
    for k in range(n - 1):
        for j in range(ring):
            a = k * ring + j; b = k * ring + (j + 1) % ring
            faces.append((a, b, b + ring, a + ring))
    verts.append(C[0] - T[0] * 1e-4); c0 = len(verts) - 1
    faces += [(c0, (j + 1) % ring, j) for j in range(ring)]
    verts.append(C[-1] + T[-1] * 1e-4); c1 = len(verts) - 1; base = (n - 1) * ring
    faces += [(c1, base + j, base + (j + 1) % ring) for j in range(ring)]
    return [tuple(v) for v in verts], faces

def mesh_obj(bpy, name, verts, faces, mat, coll, noise_amp=0.0, noise_freq=50.0, seed=0, smooth_shade=True):
    import bmesh
    from mathutils import Vector, noise
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.normal_update()
    if noise_amp > 0:  # hand-made imperfection: smooth lumps along the normal
        off = Vector((seed * 3.17, seed * 1.31, seed * 2.03))
        disp = [(v, noise.noise(v.co * noise_freq + off) + 0.35 * noise.noise(v.co * noise_freq * 2.7 + off * 2)) for v in bm.verts]
        for v, d in disp: v.co += v.normal * (noise_amp * d)
    bm.to_mesh(me); bm.free()
    if smooth_shade: me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.update()
    if mat is not None: me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

def uv_sphere(bpy, name, r, mat, coll, seg=40, rings=24, scale=(1, 1, 1), shape=None, noise_amp=0.0, noise_freq=60.0, seed=0):
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    verts = []
    for v in bm.verts:
        x, y, z = v.co
        if shape: x, y, z = shape(x, y, z)
        verts.append((x * r * scale[0], y * r * scale[1], z * r * scale[2]))
    faces = [tuple(vv.index for vv in f.verts) for f in bm.faces]; bm.free()
    return mesh_obj(bpy, name, verts, faces, mat, coll, noise_amp, noise_freq, seed)

def tube(bpy, name, pts, radii, mat, coll, n=40, ring=20, lateral=(0, 1, 0), noise_amp=0.0, seed=0):
    C = catmull(pts, n); R = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(radii)), radii)
    C, A, B = round_caps(C, R, R)
    v, f = sweep(C, A, B, ring=ring, lateral=lateral)
    return mesh_obj(bpy, name, v, f, mat, coll, noise_amp, 120.0, seed)

def lid_mesh(r_in, r_out, seg=36, rings=10):
    """Thick hemispherical clay eyelid (pole +Z, rim at z = 0)."""
    V, F = [], []
    for r in (r_out, r_in):
        for i in range(rings + 1):
            ph = (math.pi / 2) * i / rings
            for j in range(seg):
                th = 2 * math.pi * j / seg
                V.append((r * math.sin(ph) * math.cos(th), r * math.sin(ph) * math.sin(th), r * math.cos(ph)))
    n = (rings + 1) * seg
    for k in range(2):
        for i in range(rings):
            for j in range(seg):
                a = k * n + i * seg + j; b = k * n + i * seg + (j + 1) % seg
                F.append((a, b, b + seg, a + seg) if k == 0 else (a, a + seg, b + seg, b))
    for j in range(seg):
        a = rings * seg + j; b = rings * seg + (j + 1) % seg
        F.append((a, a + n, b + n, b))
    return V, F

def empty(bpy, name, coll, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); e.empty_display_size = 0.01; coll.objects.link(e)
    if parent is not None: e.parent = parent
    e.location = loc
    return e

# ----------------------------------------------------------------------------------------------- materials
def _mat(bpy, name):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    N, L = m.node_tree.nodes, m.node_tree.links
    return m, N, L, N['Principled BSDF'], N['Material Output']

def _camera_branch(N, L, p_full, out, cheap_inputs):
    """Full shader (bump, SSS) for camera rays only; a cheap twin for bounce rays. Cycles skips the unused branch of a
    Mix Shader whose factor is exactly 0/1, so bump noise is not evaluated on indirect hits (most of the shading work)."""
    p_cheap = N.new('ShaderNodeBsdfPrincipled')
    for k, v in cheap_inputs.items():
        if isinstance(v, tuple) and v and v[0] == 'link': L.new(v[1], p_cheap.inputs[k])
        else: p_cheap.inputs[k].default_value = v
    lp = N.new('ShaderNodeLightPath'); ms = N.new('ShaderNodeMixShader')
    L.new(lp.outputs['Is Camera Ray'], ms.inputs['Fac'])
    L.new(p_cheap.outputs['BSDF'], ms.inputs[1]); L.new(p_full.outputs['BSDF'], ms.inputs[2])
    L.new(ms.outputs['Shader'], out.inputs['Surface'])

def clay(bpy, name, col, col2=None, rough=0.55, sss=0.3, bump=0.15, seed=0.0, var_scale=7.0):
    """Plasticine: Principled + subsurface (0.3, r = 0.02/0.01/0.008 m), thumb-worked lumps (noise 40) + stretched dents +
    fine tooth as bump, mottled colour, small hand-made vertex lumps on the mesh itself."""
    m, N, L, p, out = _mat(bpy, name)
    tc = N.new('ShaderNodeTexCoord')
    mp0 = N.new('ShaderNodeMapping'); mp0.inputs['Location'].default_value = (seed * 1.37, seed * 0.71, seed * 2.11)
    L.new(tc.outputs['Object'], mp0.inputs['Vector'])
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 40.0; n1.inputs['Detail'].default_value = 1.5; n1.inputs['Roughness'].default_value = 0.55
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 1.0, 5.0)
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 16.0; n2.inputs['Detail'].default_value = 0.0
    n3 = N.new('ShaderNodeTexNoise'); n3.inputs['Scale'].default_value = 300.0; n3.inputs['Detail'].default_value = 0.0
    L.new(mp0.outputs['Vector'], n1.inputs['Vector']); L.new(mp0.outputs['Vector'], mp.inputs['Vector'])
    L.new(mp.outputs['Vector'], n2.inputs['Vector']); L.new(mp0.outputs['Vector'], n3.inputs['Vector'])
    dent = N.new('ShaderNodeMapRange'); dent.inputs['From Min'].default_value = 0.56; dent.inputs['From Max'].default_value = 0.70
    L.new(n2.outputs['Fac'], dent.inputs['Value'])
    a = N.new('ShaderNodeMath'); a.operation = 'MULTIPLY_ADD'; L.new(n3.outputs['Fac'], a.inputs[0]); a.inputs[1].default_value = 0.18; L.new(n1.outputs['Fac'], a.inputs[2])
    b = N.new('ShaderNodeMath'); b.operation = 'MULTIPLY_ADD'; L.new(dent.outputs['Result'], b.inputs[0]); b.inputs[1].default_value = -0.45; L.new(a.outputs['Value'], b.inputs[2])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.02
    L.new(b.outputs['Value'], bp.inputs['Height']); L.new(bp.outputs['Normal'], p.inputs['Normal'])
    c1 = srgb(col); c2 = srgb(col2) if col2 else tuple(x * 0.82 for x in c1[:3]) + (1.0,)
    n4 = N.new('ShaderNodeTexNoise'); n4.inputs['Scale'].default_value = var_scale; n4.inputs['Detail'].default_value = 0.5
    L.new(mp0.outputs['Vector'], n4.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.38; mr.inputs['From Max'].default_value = 0.66
    L.new(n4.outputs['Fac'], mr.inputs['Value'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; sock(mx.inputs, 'A_Color').default_value = c1; sock(mx.inputs, 'B_Color').default_value = c2
    L.new(mr.outputs['Result'], sock(mx.inputs, 'Factor_Float')); L.new(sock(mx.outputs, 'Result_Color'), p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Subsurface Weight'].default_value = sss
    p.inputs['Subsurface Radius'].default_value = (1.0, 0.5, 0.4)
    p.inputs['Subsurface Scale'].default_value = 0.02          # -> radius (0.02, 0.01, 0.008) m
    try: p.subsurface_method = 'BURLEY'                         # cheaper than random walk on CPU, same read for clay
    except Exception: pass
    _camera_branch(N, L, p, out, {'Base Color': ('link', sock(mx.outputs, 'Result_Color')), 'Roughness': rough})
    return m

def paper(bpy, name, col, col2, rough=0.86, stroke=(1.2, 26.0, 1.0), stroke_scale=6.0, tooth=0.05, mottle=3.0, top_col=None, top_z=(0.02, 0.30)):
    """Painted paper / card: brush streaks between two tones, broad mottling, paper tooth bump (camera rays only),
    optional painted vertical gradient toward top_col (sky cards)."""
    m, N, L, p, out = _mat(bpy, name)
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = stroke
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    ns = N.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = stroke_scale; ns.inputs['Detail'].default_value = 2.0; ns.inputs['Roughness'].default_value = 0.6
    L.new(mp.outputs['Vector'], ns.inputs['Vector'])
    nm = N.new('ShaderNodeTexNoise'); nm.inputs['Scale'].default_value = mottle; nm.inputs['Detail'].default_value = 1.0
    L.new(tc.outputs['Object'], nm.inputs['Vector'])
    mix_f = N.new('ShaderNodeMath'); mix_f.operation = 'MULTIPLY_ADD'; L.new(ns.outputs['Fac'], mix_f.inputs[0]); mix_f.inputs[1].default_value = 0.7; L.new(nm.outputs['Fac'], mix_f.inputs[2])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.62; mr.inputs['From Max'].default_value = 1.02
    L.new(mix_f.outputs['Value'], mr.inputs['Value'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; sock(mx.inputs, 'A_Color').default_value = srgb(col); sock(mx.inputs, 'B_Color').default_value = srgb(col2)
    L.new(mr.outputs['Result'], sock(mx.inputs, 'Factor_Float'))
    col_out = sock(mx.outputs, 'Result_Color')
    if top_col is not None:
        sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs['Vector'])
        zr = N.new('ShaderNodeMapRange'); zr.inputs['From Min'].default_value = top_z[0]; zr.inputs['From Max'].default_value = top_z[1]
        L.new(sep.outputs['Z'], zr.inputs['Value'])
        g2 = N.new('ShaderNodeMix'); g2.data_type = 'RGBA'; L.new(col_out, sock(g2.inputs, 'A_Color')); sock(g2.inputs, 'B_Color').default_value = srgb(top_col)
        L.new(zr.outputs['Result'], sock(g2.inputs, 'Factor_Float')); col_out = sock(g2.outputs, 'Result_Color')
    L.new(col_out, p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    if tooth > 0:
        nt = N.new('ShaderNodeTexNoise'); nt.inputs['Scale'].default_value = 900.0; nt.inputs['Detail'].default_value = 0.0
        L.new(tc.outputs['Object'], nt.inputs['Vector'])
        bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = tooth; bp.inputs['Distance'].default_value = 0.01
        L.new(nt.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs['Normal'], p.inputs['Normal'])
        _camera_branch(N, L, p, out, {'Base Color': ('link', col_out), 'Roughness': rough})
    return m
def _light(bpy, coll, name, kind, loc, target=None, rot=None, energy=1.0, size=0.5, kelvin=5500, visible=False):
    from mathutils import Vector
    ld = bpy.data.lights.new(name, type=kind); ld.energy = energy
    if kind == 'AREA': ld.shape = 'SQUARE'; ld.size = size
    if kind == 'SUN': ld.angle = size
    ld.use_temperature = True; ld.temperature = kelvin
    ob = bpy.data.objects.new(name, ld); coll.objects.link(ob); ob.location = loc
    if target is not None:
        d = Vector(target) - Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if rot is not None: ob.rotation_euler = rot
    try: ob.visible_camera = visible
    except Exception: pass
    return ob


# ----------------------------------------------------------------------------------------------- more geometry
def loft_z(rings, seg=32, cap_top=True, cap_bot=True):
    """Surface of revolution with elliptic rings along +Z. rings = [(z, rx, ry[, cx, cy]), ...] bottom to top."""
    V, F = [], []
    n = len(rings)
    for r in rings:
        z, rx, ry = r[0], r[1], r[2]; cx = r[3] if len(r) > 3 else 0.0; cy = r[4] if len(r) > 4 else 0.0
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            V.append((cx + rx * math.cos(ph), cy + ry * math.sin(ph), z))
    for k in range(n - 1):
        for j in range(seg):
            a = k * seg + j; b = k * seg + (j + 1) % seg
            F.append((a, a + seg, b + seg, b))
    if cap_bot:
        r = rings[0]; V.append((r[3] if len(r) > 3 else 0.0, r[4] if len(r) > 4 else 0.0, r[0])); c = len(V) - 1
        F += [(c, (j + 1) % seg, j) for j in range(seg)]
    if cap_top:
        r = rings[-1]; V.append((r[3] if len(r) > 3 else 0.0, r[4] if len(r) > 4 else 0.0, r[0])); c = len(V) - 1; base = (n - 1) * seg
        F += [(c, base + j, base + (j + 1) % seg) for j in range(seg)]
    return V, F

def ellipsoid(bpy, name, rad, mat, coll, seg=32, rings=18, noise_amp=0.0, noise_freq=80.0, seed=0, shape=None):
    """UV sphere scaled to semi-axes rad=(rx, ry, rz)."""
    return uv_sphere(bpy, name, 1.0, mat, coll, seg=seg, rings=rings, scale=rad, shape=shape, noise_amp=noise_amp, noise_freq=noise_freq, seed=seed)

def text_mesh(bpy, name, text, size, mat, coll, extrude=0.01, bevel=0.002, align='CENTER', spacing=1.0, line_spacing=1.0, noise_amp=0.0, plane='XZ', valign='CENTER'):
    """Extruded clay letters (Blender's built-in font), converted to a mesh. Faces +Y... text lies in the XZ plane, front toward -Y."""
    cu = bpy.data.curves.new(name + '_c', 'FONT'); cu.body = text; cu.size = size; cu.extrude = extrude; cu.bevel_depth = bevel
    cu.bevel_resolution = 2; cu.resolution_u = 4; cu.align_x = align; cu.align_y = valign; cu.space_character = spacing; cu.space_line = line_spacing
    ob = bpy.data.objects.new(name + '_tmp', cu); coll.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    coll.objects.unlink(ob); bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
    # text is created in XY (front toward +Z): rotate so it stands up in XZ and reads from -Y
    if plane == 'XZ': me.transform(__import__('mathutils').Matrix.Rotation(math.pi / 2, 4, 'X'))
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.update()
    if mat is not None: me.materials.append(mat)
    o = bpy.data.objects.new(name, me); coll.objects.link(o)
    return o

def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive: c.hide_render = h

def set_vis(ob, shadow=True):
    try: ob.visible_shadow = shadow
    except Exception: pass

def smoothstep3(x): x = clamp(x); return x * x * (3 - 2 * x)

def hash01(*a):
    h = zlib.crc32('|'.join(str(x) for x in a).encode()) & 0xffffffff
    return h / 4294967295.0

def striped(bpy, name, cols, period=0.012, axis=0, rough=0.7, bump=0.2, seed=0.0, widths=None, wob=0.0015):
    """Cloth strips (goat hair / rugs): band colours cycle along the object axis, with a wobbly edge and thumb-worked bump."""
    m, N, L, p, out = _mat(bpy, name)
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 60.0; nz.inputs['Detail'].default_value = 1.0
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    wb = N.new('ShaderNodeMath'); wb.operation = 'MULTIPLY_ADD'; L.new(nz.outputs['Fac'], wb.inputs[0]); wb.inputs[1].default_value = wob; wb.inputs[2].default_value = 0.0
    ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; L.new(sep.outputs[['X', 'Y', 'Z'][axis]], ad.inputs[0]); L.new(wb.outputs['Value'], ad.inputs[1])
    dv = N.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; L.new(ad.outputs['Value'], dv.inputs[0]); dv.inputs[1].default_value = period
    fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'; L.new(dv.outputs['Value'], fr.inputs[0])
    # colour ramp over the band
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'
    k = len(cols); widths = widths or [1.0 / k] * k; acc = 0.0
    while len(cr.color_ramp.elements) < k: cr.color_ramp.elements.new(0.5)
    for i, (c, w) in enumerate(zip(cols, widths)):
        cr.color_ramp.elements[i].position = acc; cr.color_ramp.elements[i].color = srgb(c); acc += w
    L.new(fr.outputs['Value'], cr.inputs['Fac'])
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 90.0; n1.inputs['Detail'].default_value = 2.0
    L.new(tc.outputs['Object'], n1.inputs['Vector'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.004
    L.new(n1.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs['Normal'], p.inputs['Normal'])
    L.new(cr.outputs['Color'], p.inputs['Base Color']); p.inputs['Roughness'].default_value = rough
    p.inputs['Subsurface Weight'].default_value = 0.15; p.inputs['Subsurface Radius'].default_value = (1.0, 0.5, 0.4); p.inputs['Subsurface Scale'].default_value = 0.01
    _camera_branch(N, L, p, out, {'Base Color': ('link', cr.outputs['Color']), 'Roughness': rough})
    return m

def emissive(bpy, name, col, strength=4.0):
    m, N, L, p, out = _mat(bpy, name)
    e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = srgb(col); e.inputs['Strength'].default_value = strength
    L.new(e.outputs['Emission'], out.inputs['Surface'])
    return m, e


def sandy(bpy, name, col, col2, col3=None, rough=0.9, ripple=0.30, sss=0.1):
    """Sand-clay: mottled colour (3 tones), thumb-pressed lumps, long wind-ripple bump lines, fine grain. Object coords = world."""
    m, N, L, p, out = _mat(bpy, name)
    tc = N.new('ShaderNodeTexCoord')
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 34.0; n1.inputs['Detail'].default_value = 2.0; n1.inputs['Roughness'].default_value = 0.55
    L.new(tc.outputs['Object'], n1.inputs['Vector'])
    n3 = N.new('ShaderNodeTexNoise'); n3.inputs['Scale'].default_value = 420.0; n3.inputs['Detail'].default_value = 0.0
    L.new(tc.outputs['Object'], n3.inputs['Vector'])
    # wind ripples: bands along a direction, distorted by noise
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 0.18, 1.0); mp.inputs['Rotation'].default_value = (0.0, 0.0, math.radians(-18))
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = N.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'; wv.wave_profile = 'SAW'
    wv.inputs['Scale'].default_value = 38.0; wv.inputs['Distortion'].default_value = 2.5; wv.inputs['Detail'].default_value = 1.0; wv.inputs['Detail Scale'].default_value = 1.2
    L.new(mp.outputs['Vector'], wv.inputs['Vector'])
    h1 = N.new('ShaderNodeMath'); h1.operation = 'MULTIPLY_ADD'; L.new(n3.outputs['Fac'], h1.inputs[0]); h1.inputs[1].default_value = 0.20; L.new(n1.outputs['Fac'], h1.inputs[2])
    h2 = N.new('ShaderNodeMath'); h2.operation = 'MULTIPLY_ADD'; L.new(wv.outputs['Fac'], h2.inputs[0]); h2.inputs[1].default_value = ripple; L.new(h1.outputs['Value'], h2.inputs[2])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.42; bp.inputs['Distance'].default_value = 0.01
    L.new(h2.outputs['Value'], bp.inputs['Height']); L.new(bp.outputs['Normal'], p.inputs['Normal'])
    n4 = N.new('ShaderNodeTexNoise'); n4.inputs['Scale'].default_value = 2.2; n4.inputs['Detail'].default_value = 1.5
    L.new(tc.outputs['Object'], n4.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.38; cr.color_ramp.elements[1].position = 0.64
    cr.color_ramp.elements[0].color = srgb(col); cr.color_ramp.elements[1].color = srgb(col2)
    L.new(n4.outputs['Fac'], cr.inputs['Fac'])
    c_out = cr.outputs['Color']
    if col3 is not None:
        n5 = N.new('ShaderNodeTexNoise'); n5.inputs['Scale'].default_value = 9.0; n5.inputs['Detail'].default_value = 1.0
        L.new(tc.outputs['Object'], n5.inputs['Vector'])
        mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.52; mr.inputs['From Max'].default_value = 0.70; L.new(n5.outputs['Fac'], mr.inputs['Value'])
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(c_out, sock(mx.inputs, 'A_Color')); sock(mx.inputs, 'B_Color').default_value = srgb(col3)
        L.new(mr.outputs['Result'], sock(mx.inputs, 'Factor_Float')); c_out = sock(mx.outputs, 'Result_Color')
    L.new(c_out, p.inputs['Base Color']); p.inputs['Roughness'].default_value = rough
    p.inputs['Subsurface Weight'].default_value = sss; p.inputs['Subsurface Radius'].default_value = (1.0, 0.5, 0.4); p.inputs['Subsurface Scale'].default_value = 0.02
    try: p.subsurface_method = 'BURLEY'
    except Exception: pass
    _camera_branch(N, L, p, out, {'Base Color': ('link', c_out), 'Roughness': rough})
    return m
