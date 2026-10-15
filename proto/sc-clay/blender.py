"""P10 CLAY - KINOFORGE Blender scene (bpy 5.2, Cycles CPU).
A clay snail, proud of its new shell, is pancaked by a falling clay apple - and re-inflates, dignified.

Contract (harness/blender_render.py): DURATION, SETTINGS, build(bpy, ctx) -> state, frame(bpy, ctx, state, i, t).
Stop-motion rules baked in:
  * animated ON 2s: every channel is evaluated at the pose frame pf = floor(i/2)*2, so frame pairs are identical;
  * hand-on-puppet jitter per pose (+-0.3 mm / +-0.5 deg), seeded by the pose index (deterministic);
  * film grain in the compositor seeded by the pose index (identical within a pair: one photo held for 2 frames);
  * no motion blur; the apple's fall is shown with one replacement smear pose (R-5-03).
Render budget: because frame 2k+1 is by definition the same picture as frame 2k, an odd frame rendered right after its
even partner in the same process is not path-traced again: frame() turns on a 2x2-pixel border and a render_write
handler copies the even frame's PNG over the odd one (byte-identical pair). Single-frame calls (--start N --end N+1),
the first frame of any range, and the clip's last frame always render in full. Disable with KF_NO_PAIR_REUSE=1.
Samples are capped at SPP_CAP inside build() because CI passes --samples 96 unless the queue entry overrides it
(KF_P10_SPP_CAP=<n> changes the cap, 0 lifts it). OIDN 'BALANCED' and a 0.04 noise threshold are set in build() too.
Units: metres. World: camera looks along +Y, screen-right = +X, up = +Z. The snail faces -X in its own frame and is
turned 25 deg toward the lens (3/4 view).
"""
import math
import os
import shutil
import zlib

import numpy as np

DURATION = 6.0
SETTINGS = {
    'samples': 16, 'denoise': True, 'motion_blur': False,    # brief asked 64: measured 297 CPU-s/frame at 720p, see SPP_CAP
    'view_transform': 'AgX', 'look': 'AgX - Base Contrast',   # 'AgX - Medium Contrast' does not exist in bpy 5.2
    'exposure': -3.4, 'max_bounces': 4, 'clamp_indirect': 6.0,
}

FPS = 24
SPP_CAP = 16                  # measured at 1280x720 here: 64 spp = 297 CPU-s/frame (does not fit CI), 16 spp = 71 CPU-s; same picture after OIDN
G = 9.81                      # real gravity (R-9-03)
PX = -0.030                   # world x of the snail's pivot (ground point under the shell centre)
YAW = math.radians(25)        # 3/4 view: the face turns toward the lens
APPLE_R = 0.046
F_DROP, F_HIT = 32, 52        # the apple lets go (off screen, 3.4 m up) / first impact pose
SHELL_BASE = (0.0, 0.0, 0.0262)
SHELL_C = (0.0, 0.0, 0.0670)
HEAD_PIVOT = (-0.063, 0.0, 0.042)
HEAD_C = (-0.067, 0.0, 0.0600)
HEAD_R = 0.0205
STALK_L, EYE_R, PUPIL_R = 0.034, 0.0118, 0.0062
SEAM_X = 0.100                # vertical seam between the two card sheets
SKY_W = 110.0                 # W/m^2 on the ground only
SKY_TILT = 3.0                # deg toward the lens: the high apple's umbra lands in the visible foreground and slides in as it falls
CAM_LOC = (-0.030, -0.560, 0.066)
CAM_TGT = (-0.030, 0.000, 0.0720)

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

# ----------------------------------------------------------------------------------------------- build
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

def _pair_reuse_handler(state):
    def _after_write(scene, *args):
        d = state['dup']
        if d.get('pending'):
            src, dst = d['pending']; d['pending'] = None
            try: shutil.copyfile(src, dst)
            except Exception as e: print('p10-clay: pair reuse copy failed:', e, flush=True)
    return _after_write

def build(bpy, ctx):
    from mathutils import Vector
    import bmesh
    from mathutils import noise
    sc = bpy.context.scene; coll = sc.collection
    S = {}

    # ---------------- render tuning (harness has already applied SETTINGS)
    try: sc.render.use_persistent_data = True     # keep BVH/shaders between frames: only transforms change
    except Exception: pass
    try: sc.render.compositor_device = 'CPU'
    except Exception: pass
    cy = sc.cycles
    cy.diffuse_bounces = 3; cy.glossy_bounces = 2; cy.transmission_bounces = 2; cy.transparent_max_bounces = 4
    cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
    cy.seed = 0; cy.use_animated_seed = False
    # budget (see NOTES "Render budget"): OIDN balanced and a 0.04 noise threshold are invisible on clay after denoising;
    # the sample cap protects the CI budget because the workflow passes --samples 96 unless the queue entry says otherwise
    try: cy.denoising_quality = 'BALANCED'
    except Exception: pass
    cy.adaptive_threshold = max(cy.adaptive_threshold, 0.04)
    cap = int(os.environ.get('KF_P10_SPP_CAP', SPP_CAP))
    if cap > 0 and cy.samples > cap:
        print(f'p10-clay: samples {cy.samples} -> {cap} (scene cap for the CI budget; KF_P10_SPP_CAP=0 lifts it)', flush=True)
        cy.samples = cap

    # ---------------- materials (sRGB picks)
    M = {
        'body':   clay(bpy, 'clay_body', (0.93, 0.76, 0.40), (0.86, 0.64, 0.33), seed=1),
        'shell':  clay(bpy, 'clay_shell', (0.07, 0.48, 0.55), (0.05, 0.38, 0.46), rough=0.30, seed=2, var_scale=11.0),
        'stripe': clay(bpy, 'clay_stripe', (0.97, 0.90, 0.76), (0.93, 0.84, 0.68), rough=0.36, seed=3),
        'eye':    clay(bpy, 'clay_eye', (0.96, 0.95, 0.91), (0.93, 0.92, 0.88), rough=0.24, bump=0.05, seed=4),
        'pupil':  clay(bpy, 'clay_pupil', (0.022, 0.022, 0.028), (0.03, 0.03, 0.035), rough=0.14, sss=0.0, bump=0.03, seed=5),
        'apple':  clay(bpy, 'clay_apple', (0.80, 0.10, 0.11), (0.60, 0.05, 0.07), rough=0.46, seed=6, var_scale=5.0),
        'stem':   clay(bpy, 'clay_stem', (0.40, 0.25, 0.13), (0.30, 0.18, 0.09), rough=0.6, seed=7),
        'leaf':   clay(bpy, 'clay_leaf', (0.36, 0.60, 0.21), (0.27, 0.50, 0.16), rough=0.5, seed=8),
        'grass':  clay(bpy, 'clay_grass', (0.40, 0.62, 0.26), (0.30, 0.52, 0.20), rough=0.55, seed=9),
        'mouth':  clay(bpy, 'clay_mouth', (0.30, 0.12, 0.08), (0.25, 0.10, 0.07), rough=0.5, sss=0.0, bump=0.03, seed=10),
        'ground': paper(bpy, 'paper_ground', (0.26, 0.34, 0.17), (0.21, 0.28, 0.14)),
        'skyA':   paper(bpy, 'card_sky_a', (0.60, 0.74, 0.80), (0.55, 0.69, 0.77), rough=0.9, stroke=(1.0, 1.0, 22.0), stroke_scale=4.0, tooth=0.0, mottle=2.0, top_col=(0.36, 0.53, 0.70)),
        'skyB':   paper(bpy, 'card_sky_b', (0.66, 0.78, 0.82), (0.61, 0.74, 0.79), rough=0.9, stroke=(1.0, 1.0, 22.0), stroke_scale=4.0, tooth=0.0, mottle=2.0, top_col=(0.41, 0.57, 0.72)),
    }

    # ---------------- set: painted-paper ground, two bowed card sky sheets with a seam, foreground clay grass
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=96, y_segments=72, size=1.0)
    gv = []
    for v in bm.verts:
        x, y = v.co.x * 0.8, v.co.y * 0.62 + 0.10
        gv.append((x, y, 0.0006 * noise.noise(Vector((x * 6, y * 6, 0.3))) - 0.0004))
    gf = [tuple(vv.index for vv in f.verts) for f in bm.faces]; bm.free()
    receivers = bpy.data.collections.new('sky_receivers'); coll.children.link(receivers)
    mesh_obj(bpy, 'ground', gv, gf, M['ground'], receivers)

    def sheet(name, x0, x1, ydepth, mat, bow=0.018, lean=0.06):
        nx, nz = 48, 24; V, F = [], []
        for j in range(nz + 1):
            z = 0.62 * j / nz
            for i in range(nx + 1):
                x = x0 + (x1 - x0) * i / nx; u = (x - (x0 + x1) / 2) / ((x1 - x0) / 2)
                y = ydepth + bow * (1 - u * u) + lean * z + 0.0015 * noise.noise(Vector((x * 9, z * 9, 1.7)))
                V.append((x, y, z))
        for j in range(nz):
            for i in range(nx):
                a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
        return mesh_obj(bpy, name, V, F, mat, coll)
    sheet('sky_left', -0.75, SEAM_X + 0.010, 0.360, M['skyA'])
    sheet('sky_right', SEAM_X, 0.80, 0.354, M['skyB'], bow=0.012)
    V = [(SEAM_X, 0.3545 + 0.06 * z, z) for z in (0.0, 0.62)] + [(SEAM_X + 0.0025, 0.3575 + 0.06 * z, z) for z in (0.0, 0.62)]
    mesh_obj(bpy, 'sky_seam_edge', V, [(0, 1, 3, 2)], M['skyB'], coll)

    blades = [(-0.156, -0.170, 0.031, 0.30, -0.25, 1.0), (-0.149, -0.177, 0.024, -0.15, -0.35, 2.0), (-0.164, -0.163, 0.021, 0.55, 0.1, 3.0),
              (-0.141, -0.167, 0.017, -0.45, 0.2, 4.0), (-0.170, -0.174, 0.027, 0.15, -0.3, 5.0)]
    for k, (bx, by, hgt, lean_x, lean_y, sd) in enumerate(blades):
        pts = [(bx, by, -0.004), (bx + lean_x * hgt * 0.15, by + lean_y * hgt * 0.1, hgt * 0.45), (bx + lean_x * hgt * 0.45, by + lean_y * hgt * 0.25, hgt * 0.85), (bx + lean_x * hgt * 0.8, by + lean_y * hgt * 0.4, hgt)]
        tube(bpy, f'grass_{k}', pts, [0.0040, 0.0031, 0.0019, 0.0006], M['grass'], coll, n=28, ring=14, lateral=(1, 0, 0), noise_amp=0.0004, seed=sd)

    # ---------------- snail hierarchy: root (placement, 3/4 turn, jitter) > squash (S&S) > body / shell_base > shell / head_pivot > head
    root = empty(bpy, 'snail_root', coll, loc=(PX, 0, 0))
    squash = empty(bpy, 'snail_squash', coll, parent=root)
    blockers = bpy.data.collections.new('sky_blockers'); coll.children.link(blockers)
    # body: a generalised cylinder from tail tip (+x) to the neck inside the head (-x), foot sunk 2-3 mm into the paper
    ctrl = [(0.080, 0.0040, 0.0014, 0.0012), (0.073, 0.0058, 0.0070, 0.0052), (0.060, 0.0082, 0.0140, 0.0090), (0.042, 0.0104, 0.0196, 0.0122),
            (0.020, 0.0118, 0.0232, 0.0144), (0.000, 0.0124, 0.0246, 0.0156), (-0.022, 0.0126, 0.0240, 0.0156), (-0.040, 0.0136, 0.0220, 0.0160),
            (-0.053, 0.0205, 0.0196, 0.0168), (-0.061, 0.0330, 0.0178, 0.0172), (-0.065, 0.0465, 0.0168, 0.0168), (-0.067, 0.0570, 0.0150, 0.0150)]
    smp = catmull([(c[0], 0.0, c[1], c[2], c[3]) for c in ctrl], 110)
    C, A, B = smp[:, :3], smp[:, 3], smp[:, 4]
    C, A, B = round_caps(C, A, B, start=True, end=False)
    v, f = sweep(C, A, B, ring=40)
    body = mesh_obj(bpy, 'snail_body', v, f, M['body'], blockers, noise_amp=0.00045, noise_freq=55.0, seed=11)
    body.parent = squash

    # shell: a coiled clay snake (log spiral, tube radius proportional so turns touch) + a cream snake pressed in the groove
    shell_base = empty(bpy, 'shell_base', coll, parent=squash, loc=SHELL_BASE)
    shell_off = Vector(SHELL_C) - Vector(SHELL_BASE)
    q, turns, R0, th0, spire = 0.5, 2.55, 0.0342, -math.pi * 0.55, 0.011
    cc = (1 - q) / (1 + q)
    th = th0 + np.linspace(0, turns * 2 * math.pi, 300); u = (th - th0) / (2 * math.pi)
    rho = R0 * q ** u; rr = cc * rho * 1.03
    Cs = np.stack([rho * np.cos(th), -spire * (u / turns) ** 0.8, rho * np.sin(th)], 1) + np.array(shell_off)
    Cs, As, Bs = round_caps(Cs, rr, rr)
    v, f = sweep(Cs, As, Bs, ring=36)
    shell = mesh_obj(bpy, 'shell', v, f, M['shell'], blockers, noise_amp=0.00035, noise_freq=70.0, seed=12)
    shell.parent = shell_base
    th2 = th0 + np.linspace(0.15, (turns - 1.0) * 2 * math.pi, 220); u2 = (th2 - th0) / (2 * math.pi)
    ro, ri = R0 * q ** u2, R0 * q ** (u2 + 1)
    r_in = cc * ri * 1.03; rs = 0.46 * r_in
    yo = -spire * (u2 / turns) ** 0.8; yi = -spire * (np.minimum(u2 + 1, turns) / turns) ** 0.8
    rg = 0.5 * ((ro - cc * ro * 1.03) + (ri + cc * ri * 1.03))
    Cst = np.stack([rg * np.cos(th2), (yo + yi) / 2 - 0.86 * r_in, rg * np.sin(th2)], 1) + np.array(shell_off)
    Cst, Ast, Bst = round_caps(Cst, rs, rs)
    v, f = sweep(Cst, Ast, Bst, ring=16)
    stripe = mesh_obj(bpy, 'shell_stripe', v, f, M['stripe'], coll, noise_amp=0.00015, noise_freq=120.0, seed=13)
    stripe.parent = shell_base
    # contact meshes for the apple (local vertex arrays + one merged polygon list; transformed per pose)
    cont, polys, off = [], [], 0
    for ob, which in ((body, 'body'), (shell, 'shell'), (stripe, 'shell')):
        Vl = np.array([v.co[:] for v in ob.data.vertices]); cont.append((Vl, which))
        polys += [tuple(i + off for i in p.vertices) for p in ob.data.polygons]; off += len(Vl)
    S['contact'], S['contact_polys'] = cont, polys
    S['shell_top_local'] = float(np.max(cont[1][0][:, 2]))      # shell-base frame

    # head + lower tentacles on a pivot inside the neck
    head_pivot = empty(bpy, 'head_pivot', coll, parent=squash, loc=HEAD_PIVOT)
    hoff = Vector(HEAD_C) - Vector(HEAD_PIVOT)
    head = uv_sphere(bpy, 'snail_head', HEAD_R, M['body'], blockers, seg=40, rings=26, scale=(1.06, 1.0, 0.96), noise_amp=0.0003, noise_freq=80.0, seed=14)
    head.parent = head_pivot; head.location = hoff
    # replacement mouths (stop-motion style): a smile, a small 'o', a flat line - one visible at a time
    def on_head(dx, dy, dz, k=1.0):
        d = Vector((dx, dy, dz)).normalized()
        return hoff + Vector((d.x * HEAD_R * 1.06, d.y * HEAD_R * 1.0, d.z * HEAD_R * 0.96)) * k
    smile = [tuple(on_head(-0.86, 0.40 * s, -0.30 - 0.12 * (1 - s * s), 1.0)) for s in (-1.0, -0.5, 0.0, 0.5, 1.0)]
    flat = [tuple(on_head(-0.88, 0.30 * s, -0.33, 1.0)) for s in (-1.0, 0.0, 1.0)]
    S['mouths'] = {
        'smile': tube(bpy, 'mouth_smile', smile, [0.0011, 0.0013, 0.0013, 0.0013, 0.0011], M['mouth'], coll, n=24, ring=10, lateral=(1, 0, 0), seed=17),
        'flat': tube(bpy, 'mouth_flat', flat, [0.0011, 0.0012, 0.0011], M['mouth'], coll, n=12, ring=10, lateral=(1, 0, 0), seed=18),
        'o': uv_sphere(bpy, 'mouth_o', 1.0, M['mouth'], coll, seg=20, rings=12, scale=(0.0016, 0.0030, 0.0040), seed=19),
    }
    S['mouths']['o'].location = on_head(-0.88, 0.0, -0.34, 0.97)
    S['mouths']['o'].rotation_euler = (0.0, math.radians(-20), 0.0)
    for mo in S['mouths'].values(): mo.parent = head_pivot
    S['anchors'] = {}
    for side, nm in ((-1, 'L'), (1, 'R')):
        d = Vector((-0.30, 0.44 * side, 0.85)).normalized()
        S['anchors'][nm] = hoff + Vector((d.x * HEAD_R * 1.06, d.y * HEAD_R * 1.0, d.z * HEAD_R * 0.96)) * 0.86

    # eyes: world-space puppets (never squashed: they pop out of the pancake instead)
    for nm in ('L', 'R'):
        pts = [(0, 0, -0.004), (0, 0, STALK_L * 0.5), (0, 0, STALK_L)]
        st = tube(bpy, f'stalk_{nm}', pts, [0.0042, 0.0034, 0.0029], M['body'], coll, n=16, ring=18, lateral=(1, 0, 0), seed=21 if nm == 'L' else 22)
        st.rotation_mode = 'QUATERNION'
        ey = uv_sphere(bpy, f'eye_{nm}', EYE_R, M['eye'], coll, seg=40, rings=24, noise_amp=0.00012, noise_freq=160.0, seed=23 if nm == 'L' else 24)
        ey.rotation_mode = 'QUATERNION'
        pu = uv_sphere(bpy, f'pupil_{nm}', 1.0, M['pupil'], coll, seg=28, rings=14, scale=(PUPIL_R, 0.0019, PUPIL_R))
        pu.parent = ey; pu.location = (0, EYE_R * 0.90, 0)
        lv, lf = lid_mesh(EYE_R * 1.035, EYE_R * 1.11)
        lid = mesh_obj(bpy, f'lid_{nm}', lv, lf, M['body'], coll, noise_amp=0.00008, noise_freq=200.0, seed=25 if nm == 'L' else 26)
        lid.parent = ey
        S['stalk_' + nm], S['eye_' + nm], S['pupil_' + nm], S['lid_' + nm] = st, ey, pu, lid

    # ---------------- apple: dented sphere (vertex push, no boolean), stem, leaf
    def apple_shape(x, y, z):
        phi = math.acos(max(-1.0, min(1.0, z)))
        z2 = z - 0.30 * math.exp(-(phi / 0.42) ** 2) + 0.10 * math.exp(-((math.pi - phi) / 0.34) ** 2)
        w = 1.0 + 0.055 * z - 0.03 * (1 - z * z)
        return x * w, y * w, z2 * 0.94
    apple = uv_sphere(bpy, 'apple', APPLE_R, M['apple'], blockers, seg=56, rings=32, shape=apple_shape, noise_amp=0.0007, noise_freq=40.0, seed=31)
    apple.rotation_mode = 'QUATERNION'
    sp = [(0, 0, APPLE_R * 0.58), (0.001, 0, APPLE_R * 0.90), (0.004, 0.001, APPLE_R * 1.12), (0.009, 0.002, APPLE_R * 1.24)]
    stem = tube(bpy, 'apple_stem', sp, [0.0032, 0.0028, 0.0024, 0.0021], M['stem'], blockers, n=16, ring=12, lateral=(0, 1, 0), seed=32)
    stem.parent = apple
    def leaf_shape(x, y, z):
        return x, y * (1 - 0.65 * abs(x)), z + 0.35 * x * x
    leaf = uv_sphere(bpy, 'apple_leaf', 1.0, M['leaf'], blockers, seg=32, rings=16, scale=(0.024, 0.011, 0.0024), shape=leaf_shape, seed=33)
    leaf.parent = apple; leaf.location = (0.020, 0.002, APPLE_R * 1.02); leaf.rotation_euler = (0.35, -0.40, 0.25)
    S['apple'] = apple
    S['apple_v'] = np.array([v.co[:] for v in apple.data.vertices])

    # ---------------- camera: 50 mm, low (5.8 cm off the paper, looking up at the eyes), f/4, locked off
    cd = bpy.data.cameras.new('cam'); cd.lens = 50.0; cd.sensor_width = 36.0; cd.clip_start = 0.01; cd.clip_end = 30.0
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0; cd.dof.aperture_blades = 7; cd.dof.aperture_rotation = 0.2
    cam = bpy.data.objects.new('cam', cd); coll.objects.link(cam); sc.camera = cam
    cam.location = CAM_LOC
    cam.rotation_euler = (Vector(CAM_TGT) - Vector(CAM_LOC)).to_track_quat('-Z', 'Y').to_euler()
    focus = Vector((PX - 0.040, -0.030, 0.07))          # between the eyes and the shell face
    cd.dof.focus_distance = (focus - Vector(CAM_LOC)).length
    S['cam'] = cam; S['cam_rot'] = cam.rotation_euler.copy()

    # ---------------- lights: studio key/fill/rim + a near-vertical 'sky' sun (1.4 deg) that only the apple and the
    # snail's main masses shadow, and that only lights the paper ground (receiver-linked): the gag light can be strong enough
    # for the falling apple's shadow to read without flattening the studio modelling on the puppets
    tgt = (PX, 0.0, 0.055)
    S['key'] = _light(bpy, coll, 'key', 'AREA', (-0.78, -0.62, 0.86), tgt, energy=300.0, size=1.0, kelvin=4000)
    S['fill'] = _light(bpy, coll, 'fill', 'AREA', (0.95, -0.80, 0.30), tgt, energy=60.0, size=1.0, kelvin=8000)
    S['rim'] = _light(bpy, coll, 'rim', 'AREA', (0.30, 0.30, 0.42), (PX, 0.0, 0.08), energy=40.0, size=0.4, kelvin=5200)
    sky = _light(bpy, coll, 'sky', 'SUN', (0, 0, 2.0), rot=(math.radians(-SKY_TILT), 0.0, 0.0), energy=SKY_W, size=math.radians(1.2), kelvin=6500)
    sky.light_linking.blocker_collection = blockers
    sky.light_linking.receiver_collection = receivers
    S['sky'] = sky

    wd = bpy.data.worlds.new('room'); sc.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    bg = wd.node_tree.nodes.get('Background')
    if bg is not None: bg.inputs['Color'].default_value = (0.030, 0.032, 0.036, 1.0); bg.inputs['Strength'].default_value = 1.0

    # ---------------- compositor: pose-seeded multiplicative grain + gentle corner falloff (scene-linear, before AgX)
    S['grain'] = None
    try:
        ng = bpy.data.node_groups.new('kf_finish', 'CompositorNodeTree'); sc.compositing_node_group = ng
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        N, Lk = ng.nodes, ng.links
        rl = N.new('CompositorNodeRLayers')
        ic = N.new('CompositorNodeImageCoordinates'); Lk.new(rl.outputs['Image'], ic.inputs['Image'])
        wn = N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '4D'; Lk.new(ic.outputs['Pixel'], wn.inputs['Vector'])
        amt = 0.035
        gm = N.new('ShaderNodeMath'); gm.operation = 'MULTIPLY_ADD'; Lk.new(wn.outputs['Value'], gm.inputs[0]); gm.inputs[1].default_value = 2 * amt; gm.inputs[2].default_value = 1 - amt
        W, H = float(ctx['W']), float(ctx['H'])
        sub = N.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; Lk.new(ic.outputs['Pixel'], sub.inputs[0]); sub.inputs[1].default_value = (W / 2, H / 2, 0.0)
        scl = N.new('ShaderNodeVectorMath'); scl.operation = 'SCALE'; Lk.new(sub.outputs['Vector'], scl.inputs[0]); scl.inputs['Scale'].default_value = 2.0 / W
        dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; Lk.new(scl.outputs['Vector'], dot.inputs[0]); Lk.new(scl.outputs['Vector'], dot.inputs[1])
        vg = N.new('ShaderNodeMath'); vg.operation = 'MULTIPLY_ADD'; Lk.new(dot.outputs['Value'], vg.inputs[0]); vg.inputs[1].default_value = -0.13; vg.inputs[2].default_value = 1.0
        gv2 = N.new('ShaderNodeMath'); gv2.operation = 'MULTIPLY'; Lk.new(gm.outputs['Value'], gv2.inputs[0]); Lk.new(vg.outputs['Value'], gv2.inputs[1])
        mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; sock(mix.inputs, 'Factor_Float').default_value = 1.0
        Lk.new(rl.outputs['Image'], sock(mix.inputs, 'A_Color')); Lk.new(gv2.outputs['Value'], sock(mix.inputs, 'B_Color'))
        out = N.new('NodeGroupOutput'); Lk.new(sock(mix.outputs, 'Result_Color'), out.inputs['Image'])
        sc.render.use_compositing = True
        S['grain'] = wn
    except Exception as e:
        print('p10-clay: compositor finish unavailable:', e)

    # ---------------- on-2s pair reuse (see module docstring)
    S['dup'] = {'last': None, 'pending': None, 'enabled': os.environ.get('KF_NO_PAIR_REUSE', '') == '', 'total': int(round(ctx['duration'] * ctx['fps']))}
    if S['dup']['enabled']:
        bpy.app.handlers.render_write.append(_pair_reuse_handler(S))

    S['objs'] = {'root': root, 'squash': squash, 'shell_base': shell_base, 'head_pivot': head_pivot, 'body': body}
    return S

# ----------------------------------------------------------------------------------------------- animation (pose frames)
D = math.radians
K_BODY_SZ = [(0, 1.0), (16, 1.0), (18, 0.95, 'o'), (20, 1.05, 's'), (22, 0.99, 's'), (24, 1.0, 's'), (26, 1.0), (28, 1.045, 'o'),
             (32, 1.03, 's'), (36, 0.985, 's'), (48, 0.975, 's'), (50, 0.96, 's'), (52, 0.45, 'l'), (54, 0.15, 'l'), (78, 0.15),
             (80, 0.135, 's'), (82, 0.37, 'l'), (84, 0.32, 's'), (90, 0.32), (92, 0.30, 's'), (94, 0.68, 'l'), (96, 0.62, 's'),
             (102, 0.62), (104, 0.58, 's'), (106, 1.22, 'l'), (108, 0.92, 's'), (110, 1.05, 's'), (112, 0.985, 's'), (114, 1.0, 's'),
             (118, 1.0), (120, 0.97, 's'), (122, 1.02, 's'), (124, 1.03, 's'), (128, 1.025, 's')]
K_SHELL_SZ = [(0, 1.0), (50, 1.0), (52, 0.45, 'l'), (54, 0.15, 'l'), (106, 0.17, 's'), (108, 0.16, 's'), (110, 1.25, 'l'), (112, 0.90, 's'),
              (114, 1.05, 's'), (116, 0.985, 's'), (118, 1.0, 's')]
K_SHELL_ROCK = [(0, 0.0), (14, 0.0), (16, D(-2.5), 's'), (18, D(6.0), 'o'), (20, D(-4.0), 's'), (22, D(2.0), 's'), (24, D(0.0), 's'),
                (110, 0.0), (112, D(-5.0), 's'), (114, D(3.0), 's'), (116, D(-1.0), 's'), (118, 0.0, 's')]
K_SHELL_PUFF = [(0, 1.0), (26, 1.0), (28, 1.06, 'o'), (32, 1.035, 's'), (36, 1.0, 's')]
K_HEAD_PITCH = [(0, 0.0), (4, D(-3), 's'), (8, D(2), 's'), (14, D(5), 'o'), (26, D(5)), (28, D(8), 'o'), (32, D(6), 's'), (34, D(11), 'o'),
                (36, D(15), 'o'), (48, D(16), 's'), (50, D(11), 's'), (52, 0.0, 'l'), (106, 0.0), (112, D(-5), 's'), (118, D(-6), 's'),
                (120, D(4), 'o'), (122, D(7), 's'), (126, D(9), 's')]
K_HEAD_YAW = [(0, 0.0), (122, 0.0), (124, D(14), 'o'), (126, D(18), 's'), (130, D(17), 's')]
# eye stalks: (pitch forward+, splay outward+, length scale)
K_STALK = {
    'L': [(0, (12, 12, 1.0)), (4, (24, 14, 0.97), 'o'), (6, (22, 14, 0.98), 's'), (8, (-8, 15, 1.0), 'i'), (10, (-34, 17, 1.02), 'l'),
          (12, (-52, 19, 1.0), 'o'), (14, (-44, 18, 1.0), 's'), (18, (-49, 18, 1.0), 's'), (20, (-39, 17, 1.0), 's'), (22, (-45, 18, 1.0), 's'),
          (24, (-44, 18, 1.0), 's'), (32, (-42, 17, 1.0)), (34, (-6, 14, 1.04), 'o'), (36, (13, 12, 1.06), 'o'), (38, (9, 13, 1.04), 's'),
          (48, (8, 15, 1.04)), (50, (2, 18, 0.96), 's'), (52, (10, 58, 1.05), 'l'), (54, (6, 84, 1.16), 'o'), (58, (5, 86, 1.15), 's'),
          (80, (5, 86, 1.15)), (82, (10, 68, 1.12), 'o'), (92, (10, 66, 1.12)), (94, (34, 40, 1.08), 'o'), (104, (34, 38, 1.08)),
          (106, (6, 14, 1.06), 'o'), (108, (14, 18, 1.0), 's'), (112, (38, 26, 0.98), 's'), (116, (42, 24, 0.97), 's'),
          (118, (30, 14, 0.90), 's'), (120, (2, 8, 1.07), 'o'), (122, (5, 10, 1.0), 's'), (124, (4, 10, 1.0), 's')],
    'R': [(0, (8, 11, 1.0)), (4, (20, 13, 0.97), 'o'), (6, (21, 13, 0.98), 's'), (8, (4, 14, 1.0), 'i'), (10, (-26, 16, 1.02), 'l'),
          (12, (-46, 18, 1.0), 'o'), (14, (-50, 18, 1.0), 's'), (16, (-44, 17, 1.0), 's'), (18, (-48, 18, 1.0), 's'), (20, (-43, 17, 1.0), 's'),
          (22, (-45, 18, 1.0), 's'), (24, (-44, 18, 1.0), 's'), (32, (-42, 17, 1.0)), (34, (-14, 14, 1.03), 'o'), (36, (10, 11, 1.06), 'o'),
          (38, (7, 12, 1.04), 's'), (48, (6, 14, 1.04)), (50, (0, 17, 0.96), 's'), (52, (-12, 54, 1.05), 'l'), (54, (-24, 66, 1.18), 'o'),
          (58, (-22, 64, 1.16), 's'), (80, (-22, 64, 1.16)), (82, (-16, 56, 1.12), 'o'), (92, (-16, 54, 1.12)), (94, (26, 46, 1.08), 'o'),
          (104, (26, 44, 1.08)), (106, (2, 12, 1.06), 'o'), (108, (8, 16, 1.0), 's'), (112, (-24, 30, 1.0), 's'), (116, (-28, 33, 0.99), 's'),
          (118, (-12, 18, 0.90), 's'), (120, (3, 8, 1.07), 'o'), (122, (4, 9, 1.0), 's'), (124, (3, 9, 1.0), 's')],
}
K_EYE_SIZE = [(0, 1.0), (32, 1.0), (34, 1.10, 'o'), (40, 1.12, 's'), (48, 1.20, 's'), (50, 1.22, 's'), (52, 1.28, 'l'), (54, 1.34, 'o'),
              (58, 1.30, 's'), (80, 1.30), (82, 1.24, 'o'), (94, 1.14, 'o'), (106, 1.06, 'o'), (110, 1.0, 's')]
K_BLINK = [(0, 1.0), (12, 1.0), (14, 0.92, 's'), (32, 0.92), (34, 1.05, 'o'), (36, 1.0, 's'), (112, 1.0), (114, 0.80, 'l'),
           (116, 1.0, 'o'), (130, 1.0), (132, 0.90, 'l'), (134, 0.78, 'i'), (136, 0.78), (138, 0.90, 'o'), (140, 1.0, 'o')]
# eyelids: rotation about the eye's local X. +50 open, 0 = lid line across the pupil centre (half-lidded), -90 closed
K_LID = [(0, 42.0), (12, 42.0), (14, 8.0, 's'), (32, 6.0), (34, 62.0, 'o'), (38, 66.0, 's'), (50, 72.0, 's'), (52, 85.0, 'l'),
         (80, 85.0), (94, 70.0, 'o'), (106, 60.0, 'o'), (110, -12.0, 's'), (114, -88.0, 'l'), (116, -20.0, 'o'), (118, -14.0, 's'),
         (120, 40.0, 'o'), (124, 4.0, 's'), (130, 2.0), (132, -48.0, 'l'), (134, -90.0, 'i'), (136, -90.0), (138, -46.0, 'o'),
         (140, -2.0, 'o'), (142, 0.0, 's')]
K_PUPIL = [(0, 1.0), (36, 1.0), (48, 0.82, 's'), (52, 1.05, 'l'), (54, 1.10, 'l'), (60, 1.10), (62, 0.40, 'l'), (80, 0.42),
           (82, 0.60, 'o'), (94, 0.80, 'o'), (106, 1.0, 'o')]
K_GAZE = [(0, 'front'), (8, 'front'), (12, 'shell', 'o'), (32, 'shell'), (34, 'up', 'o'), (50, 'up'), (52, 'popped', 'l'), (106, 'popped'),
          (110, 'dazed', 'o'), (118, 'dazed'), (122, 'front', 's'), (124, 'cam', 'o')]
K_MOUTH = [(0, 'smile'), (34, 'o'), (52, 'flat'), (124, 'smile')]   # replacement mouths (step changes)
K_CAM = [(0, (0.0, 0.0, 0.0)), (50, (0.0, 0.0, 0.0)), (52, (0.0028, -0.0062, 0.85), 'h'), (54, (-0.0014, 0.0030, -0.40), 'h'), (56, (0.0, 0.0, 0.0), 'h')]

def _rest_dir(pitch, splay, side):
    p, s = math.radians(pitch), math.radians(splay)
    return (-math.sin(p) * math.cos(s), side * math.sin(s), math.cos(p) * math.cos(s))

def apple_state(pf):
    """Apple pose for a pose frame -> (xy, mode, quaternion, scale, extra) or None.
    mode 'air': free fall from 3.4 m under real g (h0 = g*T^2/2, T = 20 f), extra = height of its lowest point above the shell;
    'smear': one replacement smear pose, extra = gap above the shell; 'contact': rests on the snail/paper (raycast), extra =
    (press into the clay, bounce lift)."""
    from mathutils import Vector, Quaternion
    x0 = PX + 0.003
    T = (F_HIT - F_DROP) / FPS
    base_q = Quaternion((1, 0, 0), math.radians(7)) @ Quaternion((0, 0, 1), math.radians(-35))
    if pf < F_DROP: return None
    if pf < F_HIT - 2:
        tau = (F_HIT - pf) / FPS
        return Vector((x0, 0.0, 0.0)), 'air', base_q, (1.0, 1.0, 1.0), G * T * tau - 0.5 * G * tau * tau
    if pf < F_HIT:
        return Vector((x0, 0.0, 0.0)), 'smear', base_q, (0.64, 0.64, 2.7), 0.016
    keys = {52: (0.70, 0.005, 0.0), 54: (1.12, 0.002, 0.009), 56: (0.90, 0.004, 0.0), 58: (1.03, 0.003, 0.0), 60: (1.0, 0.003, 0.0)}
    if pf <= 60:
        sz, press, lift = keys[pf]; sxy = 1.0 / math.sqrt(sz)
        return Vector((x0, 0.0, 0.0)), 'contact', base_q, (sxy, sxy, sz), (press, lift)
    # roll-off: rock (anticipation), roll right & back along the flattened tail, drop off onto the paper, rock, settle
    dirv = Vector((0.92, 0.39, 0.0)).normalized()
    dist = track([(60, 0.0), (64, -0.0045, 's'), (66, 0.0, 's'), (74, 0.072, 'i'), (76, 0.095, 'l'), (88, 0.165, 'o'),
                  (92, 0.158, 's'), (96, 0.161, 's'), (98, 0.160, 's')], pf)
    axis = Vector((0, 0, 1)).cross(dirv).normalized()
    q = Quaternion(axis, dist / 0.160 * math.radians(265)) @ base_q    # ~rolling (slight skid) so it comes to rest on its side
    return Vector((x0, 0.0, 0.0)) + dirv * dist, 'contact', q, (1.0, 1.0, 1.0), (0.0015, {78: 0.004}.get(pf, 0.0))

def _contact_tree(S, M_body, M_shell):
    from mathutils.bvhtree import BVHTree
    Ws = []
    for Vl, which in S['contact']:
        M = np.array(M_body if which == 'body' else M_shell)
        Ws.append(Vl @ M[:3, :3].T + M[:3, 3])
    W = np.vstack(Ws)
    return BVHTree.FromPolygons([tuple(v) for v in W], S['contact_polys']), float(Ws[1][:, 2].max())

def _rest_height(tree, xy, Vrot):
    """Lowest-contact drop of a rigid vertex cloud onto the posed snail + the paper (z = 0): origin z so nothing sinks."""
    from mathutils import Vector
    low = Vrot[Vrot[:, 2] < np.percentile(Vrot[:, 2], 28)]
    best = -1e9
    for vx, vy, vz in low[::2]:
        hit = tree.ray_cast(Vector((xy.x + vx, xy.y + vy, 0.5)), Vector((0.0, 0.0, -1.0)), 1.0)
        h = max(0.0, hit[0].z) if hit[0] is not None else 0.0
        best = max(best, h - vz)
    return best

def _pair_reuse(bpy, ctx, S, i):
    """Odd frame right after its even partner in this process: skip path tracing, copy the partner's PNG after write."""
    d = S.get('dup')
    if not d or not d['enabled']: return
    sc = bpy.context.scene
    fdir = os.path.join(ctx['out'], 'frames')
    if d.get('pending'):                       # safety: the handler did not fire for the previous frame -> copy now
        src, dst = d['pending']; d['pending'] = None
        try: shutil.copyfile(src, dst)
        except Exception as e: print('p10-clay: pair reuse late copy failed:', e, flush=True)
    prev = os.path.join(fdir, f'{i - 1:05d}.png')
    reuse = (i % 2 == 1) and d['last'] == i - 1 and i < d['total'] - 1 and os.path.exists(prev)
    if reuse:
        d['pending'] = (prev, os.path.join(fdir, f'{i:05d}.png'))
        sc.render.use_border = True; sc.render.use_crop_to_border = False
        sc.render.border_min_x, sc.render.border_max_x = 0.0, 2.0 / max(1, sc.render.resolution_x)
        sc.render.border_min_y, sc.render.border_max_y = 0.0, 2.0 / max(1, sc.render.resolution_y)
    else:
        sc.render.use_border = False
        d['last'] = i

def frame(bpy, ctx, S, i, t):
    from mathutils import Vector, Matrix, Euler, Quaternion
    pf = (i // 2) * 2                  # ON 2s
    tp = pf / FPS
    O = S['objs']

    # ---------------- snail body squash & stretch (rough volume: X ~ sz^-0.25 (1.6 at 0.15), Y ~ sz^-0.42)
    sz = track(K_BODY_SZ, pf)
    if pf < 48 or pf > 116: sz *= 1.0 + 0.006 * math.sin(2 * math.pi * tp / 2.4)    # breathing (R-5-06)
    sx, sy = sz ** -0.25, sz ** -0.42
    jx, jy, jr = jit(pf, 'sx', 0.0003), jit(pf, 'sy', 0.0003), jit(pf, 'sr', D(0.5))
    yaw = YAW + jr
    O['root'].location = (PX + jx, jy, 0.0); O['root'].rotation_euler = (0.0, 0.0, yaw)
    O['squash'].scale = (sx, sy, sz)

    ssz = track(K_SHELL_SZ, pf); ssx, ssy = ssz ** -0.25, ssz ** -0.42
    puff = track(K_SHELL_PUFF, pf)
    O['shell_base'].scale = (puff * ssx / sx, puff * ssy / sy, puff * ssz / sz)
    O['shell_base'].rotation_euler = (0.0, track(K_SHELL_ROCK, pf) + jit(pf, 'shr', D(0.5)), 0.0)

    hp, hy = track(K_HEAD_PITCH, pf) + jit(pf, 'hp', D(0.5)), track(K_HEAD_YAW, pf)
    O['head_pivot'].rotation_euler = (0.0, hp, hy)     # +Y rotation lifts the face (-X) and tilts the head back

    mouth = [k[1] for k in K_MOUTH if k[0] <= pf][-1]
    for nm, mo in S['mouths'].items(): mo.hide_render = (nm != mouth)

    # ---------------- eyes (world space, from the squashed head's anchors)
    M_root = Matrix.LocRotScale(Vector((PX + jx, jy, 0.0)), Euler((0, 0, yaw)), None)
    M_sq = M_root @ Matrix.Diagonal((sx, sy, sz, 1.0))
    R_head = Euler((0.0, hp, hy)).to_matrix()
    M_hp = M_sq @ Matrix.LocRotScale(Vector(HEAD_PIVOT), R_head, None)
    R_yaw = Euler((0, 0, yaw)).to_matrix()
    R_dir = R_yaw @ R_head
    cam_p = Vector(CAM_LOC)            # nominal lens position (never the jolted one: no state may leak between frames)
    shell_w = M_root @ Vector(SHELL_C)
    fwd = (R_yaw @ Vector((-1.0, 0.0, 0.0))).normalized()
    es, bl, ps, lid = track(K_EYE_SIZE, pf), track(K_BLINK, pf), track(K_PUPIL, pf), track(K_LID, pf)
    tremble = D(1.6) if 38 <= pf <= 50 else D(0.6) if 62 <= pf <= 66 else 0.0
    for nm, side in (('L', -1), ('R', 1)):
        p, s, ls = track(K_STALK[nm], pf)
        d_loc = Vector(_rest_dir(p + math.degrees(jit(pf, 'p' + nm, D(0.5)) + (tremble if (pf // 2) % 2 else -tremble)), s, side))
        dw = (R_dir @ d_loc).normalized()
        base = M_hp @ S['anchors'][nm]
        L = STALK_L * ls
        reach = L + EYE_R * 0.55 * es
        eye_c = base + dw * reach
        if eye_c.z < EYE_R * es + 0.0005:      # popped eyes rest on the paper instead of sinking into it
            eye_c.z = EYE_R * es + 0.0005; dw = (eye_c - base).normalized(); L = max(0.01, (eye_c - base).length - EYE_R * 0.55 * es)
        st = S['stalk_' + nm]
        st.location = base; st.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(dw); st.scale = (1.0, 1.0, L / STALK_L)
        to_cam = (cam_p - eye_c).normalized()
        def gdir(name):   # gaze targets are cheated toward the lens so the pupils read from a low side camera
            if name == 'front': return (fwd + 0.55 * to_cam + Vector((0, 0, 0.08))).normalized()
            if name == 'shell': return ((shell_w - eye_c).normalized() + 0.55 * to_cam).normalized()
            if name == 'up': return (Vector((0.0, 0.0, 1.0)) + 0.75 * to_cam).normalized()
            if name == 'cam': return to_cam
            if name == 'popped': return (to_cam + Vector((0.35 * side, 0.0, 0.25))).normalized()
            if name == 'dazed': return (to_cam + (Vector((-0.7, 0.0, -0.45)) if side < 0 else Vector((0.75, 0.0, 0.6)))).normalized()
        g = None
        for k0, k1 in zip(K_GAZE, K_GAZE[1:]):
            if pf <= k1[0]:
                u = ease((pf - k0[0]) / float(k1[0] - k0[0]), k1[2] if len(k1) > 2 else 's') if pf > k0[0] else 0.0
                g = gdir(k0[1]).lerp(gdir(k1[1]), u).normalized(); break
        if g is None: g = gdir(K_GAZE[-1][1])
        g = (Quaternion(Vector((0, 0, 1)), jit(pf, 'g' + nm, D(1.0))) @ g).normalized()
        up = Vector((0, 0, 1)) if abs(g.z) < 0.92 else Vector((0, -1, 0))
        xa = g.cross(up).normalized(); za = xa.cross(g).normalized()
        R = Matrix((xa, g, za)).transposed()
        ey = S['eye_' + nm]
        ey.location = eye_c; ey.rotation_quaternion = R.to_quaternion(); ey.scale = (es, es, es * bl)
        S['pupil_' + nm].scale = (ps, 1.0, ps)
        S['lid_' + nm].rotation_euler = (math.radians(lid + jit(pf, 'l' + nm, 1.5)), 0.0, 0.0)

    # ---------------- apple (contact by raycasting its lower vertices onto the posed snail + paper: dented clay is not a sphere)
    ap = apple_state(pf)
    A = S['apple']
    vis = ap is not None
    A.hide_render = not vis
    for c in A.children: c.hide_render = not vis
    if vis:
        xy, mode, q, scl, extra = ap
        if pf >= 96:  # resting prop still gets the hand jitter
            xy = xy + Vector((jit(pf, 'ax', 0.0003), jit(pf, 'ay', 0.0003), 0.0)); q = Quaternion(Vector((0, 0, 1)), jit(pf, 'ar', D(0.5))) @ q
        Rm = np.array(q.to_matrix()); Vrot = (S['apple_v'] * np.array(scl)) @ Rm.T
        M_sb = M_sq @ Matrix.LocRotScale(Vector(SHELL_BASE), Euler((0.0, O['shell_base'].rotation_euler[1], 0.0)), Vector(O['shell_base'].scale))
        if mode in ('air', 'smear'):
            top = (M_sb @ Vector((0.0, 0.0, S['shell_top_local']))).z
            z = top + extra - float(Vrot[:, 2].min())
        elif pf <= 98:
            tree, _ = _contact_tree(S, M_sq, M_sb)
            press, lift = extra
            z = _rest_height(tree, xy, Vrot) - press + lift
        else:
            z = -float(Vrot[:, 2].min())
        A.location = (xy.x, xy.y, z); A.rotation_quaternion = q; A.scale = scl

    # ---------------- set jolt on impact (the table is hit; the camera stand is not)
    dx, dz, roll = track(K_CAM, pf)
    S['cam'].location = Vector(CAM_LOC) + Vector((dx, 0.0, dz))
    S['cam'].rotation_euler = (S['cam_rot'].to_quaternion() @ Quaternion(Vector((0, 0, 1)), math.radians(roll))).to_euler()

    # ---------------- grain seeded by the pose (identical within a frame pair)
    if S.get('grain') is not None:
        S['grain'].inputs['W'].default_value = pf * 0.731 + 0.17

    _pair_reuse(bpy, ctx, S, i)
