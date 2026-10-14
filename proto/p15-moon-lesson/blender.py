"""WHY THE MOON CHANGES SHAPE — Clay lesson, 16:9, Blender Cycles CPU, animated ON 2s (stop-motion grammar).

A desk lamp is the Sun; a clay Earth sits on a turntable; a clay Moon rides a bent wire arm around it; a thumb-sized clay
kid stands on top of the Earth ("you"). Real light does the physics: the phases in the POV shots are what the lamp
actually lights, seen from where the kid stands. The orbit is raised to the kid's eye line and the lamp is 28 degrees
above it, so the full moon clears the Earth's shadow (the real Moon misses it thanks to its 5-degree tilt).
Timing comes from timing.json (beats aligned to the narration). Contract: DURATION, SETTINGS, build(), frame().
Units: metres. Z up. The lamp is at -X; full moon is at +X.
"""
import math, os, json, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('p10lib', os.path.join(HERE, '..', '..', 'proto', 'p10-clay', 'blender.py'))
P = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(P)
clay, paper, uv_sphere, tube, mesh_obj, empty, _light, sock, jit, lerp, clamp, smooth = P.clay, P.paper, P.uv_sphere, P.tube, P.mesh_obj, P.empty, P._light, P.sock, P.jit, P.lerp, P.clamp, P.smooth

TIMING = json.load(open(os.path.join(HERE, 'timing.json')))
DURATION = TIMING['duration']
FPS = 24
SETTINGS = {'samples': 16, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 4, 'clamp_indirect': 6.0}
B = {b['id']: (b['t0'], b['t1']) for b in TIMING['beats']}

E = (0.0, 0.0, 0.11)             # Earth centre
ER, MR, OR = 0.050, 0.0175, 0.185   # Earth radius, Moon radius, orbit radius
OZ = E[2] + ER + 0.016           # orbit plane: the kid's eye line
LAMP_EL = math.radians(18)
LAMP = (E[0] - 0.80 * math.cos(LAMP_EL), 0.0, E[2] + 0.80 * math.sin(LAMP_EL))
KID_TOP = (E[0], E[1], E[2] + ER)

def moon_pos(th, dz=0.0):
    """th = 0: new moon (between Earth and lamp, at -X); pi/2: first quarter (at -Y, toward the lens side); pi: full (+X)."""
    return (E[0] - OR * math.cos(th), E[1] - OR * math.sin(th), OZ + dz)

def ease(u): u = clamp(u); return u * u * (3 - 2 * u)
def seg(t, a, b): return ease((t - a) / max(1e-6, b - a))

# ----------------------------------------------------------------------------------------- choreography (t in seconds, already on 2s)
def moon_th(t):
    h0, h1 = B['hook']; m0, m1 = B['myth']; s0, s1 = B['setup']; n0, n1 = B['new']; q0, q1 = B['quarter']; f0, f1 = B['full']; e0, e1 = B['seat']
    if t < m0: return math.pi * 0.62
    if t < s0: return math.pi                                    # myth: behind the Earth, sliding into its shadow
    if t < n0: return lerp(math.pi, 2 * math.pi, seg(t, s0 + 1.0, s1))   # setup: it travels round to new moon
    if t < q0: return 2 * math.pi
    if t < f0: return lerp(2 * math.pi, 2.5 * math.pi, seg(t, q0 - 0.2, q0 + 1.6))
    if t < e0: return lerp(2.5 * math.pi, 3 * math.pi, seg(t, f0 - 0.2, f0 + 1.8))
    return 3 * math.pi + 2 * math.pi * ((t - e0) / max(1.0, B['end'][1] - e0)) * 1.15

def moon_dz(t):
    m0, m1 = B['myth']
    down = OZ - (E[2] - 0.80 * 0 - math.tan(LAMP_EL) * (OR + 0.0) - 0.0)        # drop from the orbit plane to the shadow axis
    axis = E[2] - math.tan(LAMP_EL) * OR                                        # height of the Earth's shadow axis at the Moon's distance
    d = axis - OZ
    into = seg(t, m0 + 1.2, m0 + 3.0) * (1 - seg(t, m1 - 1.6, m1 - 0.2))
    return d * into

def lamp_on(t):
    return 0.0 if t >= TIMING.get('lamp_off', B['light'][0] + 0.65) else 1.0

# camera shots: returns (location, target, lens_mm, focus_point)
def cam_at(t):
    h0, h1 = B['hook']; m0, m1 = B['myth']; s0, s1 = B['setup']; k0, k1 = B['stand']
    th = moon_th(t); M = np.array(moon_pos(th, moon_dz(t)))
    Ev = np.array(E); kid_eye = np.array(KID_TOP) + np.array((0, 0, 0.019))
    if t < m0:                                                   # HOOK: macro on the Moon; the lens circles from its night side to its day side
        u = seg(t, h0 + 2.4, h1 - 0.2)
        a = lerp(math.radians(-25), math.radians(-150), u)       # angle around the Moon, measured from +X
        d = 0.165
        loc = M + np.array((d * math.cos(a), d * math.sin(a), 0.012))
        return loc, M, 85, M
    if t < s0:                                                   # MYTH: a side view across the Earth to the Moon behind it
        tgt = (Ev + M) / 2 + np.array((0.03, 0, -0.01))
        return tgt + np.array((0.05, -0.62, 0.06)), tgt, 50, M
    if t < k0:                                                   # SETUP: crane back from the Earth to the whole desk, lamp included
        u = seg(t, s0, s1 - 0.6)
        tgt = lerp(Ev, np.array((-0.30, 0.0, 0.17)), u)
        loc = lerp(Ev + np.array((0.10, -0.38, 0.06)), np.array((-0.20, -1.45, 0.42)), u)
        return loc, tgt, lerp(50, 35, u), Ev
    if t < B['new'][0]:                                          # STAND: push in to the kid on top of the Earth
        u = seg(t, k0, k1 - 0.3)
        tgt = lerp(Ev + np.array((0, 0, 0.03)), kid_eye - np.array((0, 0, 0.006)), u)
        loc = lerp(np.array((-0.10, -0.55, 0.25)), kid_eye + np.array((0.045, -0.12, 0.025)), u)
        return loc, tgt, lerp(40, 60, u), tgt
    if t < B['seat'][0]:                                         # POV: over the kid's shoulder, the lens follows the Moon
        look = M - kid_eye; look[2] = 0; look /= np.linalg.norm(look)
        side = np.array((-look[1], look[0], 0))
        loc = kid_eye - look * 0.115 + side * 0.03 + np.array((0, 0, 0.022))
        return loc, M, 40, M
    if t < B['light'][0]:                                        # SEAT: high three-quarter, the whole system turning
        e0, e1 = B['seat']; u = seg(t, e0, e1)
        loc = np.array((0.30, -0.62, 0.52)) + np.array((-0.08, 0.0, -0.04)) * u
        tgt = Ev + np.array((-0.05, 0, 0.0))
        return loc, tgt, 32, Ev
    l0, l1 = B['light']; n0, n1 = B['end']                       # LIGHT OFF → END: slow push to the kid looking at the dark Moon
    u = seg(t, l0, n1)
    loc = lerp(np.array((0.26, -0.52, 0.36)), kid_eye + np.array((0.10, -0.16, 0.04)), u)
    tgt = lerp(Ev, (kid_eye + M) / 2, u)
    return loc, tgt, lerp(35, 45, u), kid_eye

# ----------------------------------------------------------------------------------------- build
def build(bpy, ctx):
    from mathutils import Vector
    import bmesh
    from mathutils import noise
    sc = bpy.context.scene; coll = sc.collection; S = {}
    try: sc.render.use_persistent_data = True
    except Exception: pass
    try: sc.render.compositor_device = 'CPU'
    except Exception: pass
    cy = sc.cycles
    cy.diffuse_bounces = 3; cy.glossy_bounces = 2; cy.transmission_bounces = 2; cy.transparent_max_bounces = 4
    cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
    cy.seed = 0; cy.use_animated_seed = False
    if os.environ.get('KF_NOBOUNCE'): cy.max_bounces = 0; cy.diffuse_bounces = 0
    if os.environ.get('KF_ONLY'):
        for o in bpy.data.objects: pass
    try: cy.denoising_quality = 'BALANCED'
    except Exception: pass
    cy.adaptive_threshold = max(cy.adaptive_threshold, 0.04)
    cap = int(os.environ.get('KF_SPP_CAP', 16))
    if cap > 0 and cy.samples > cap: cy.samples = cap

    M = {
        'earth':  clay(bpy, 'clay_earth', (0.10, 0.36, 0.72), (0.27, 0.56, 0.25), rough=0.45, seed=21, var_scale=5.5),
        'moon':   clay(bpy, 'clay_moon', (0.78, 0.77, 0.74), (0.62, 0.61, 0.59), rough=0.62, sss=0.0, bump=0.32, seed=22, var_scale=9.0),   # opaque: SSS would let the lamp glow through a 3.5 cm ball
        'base':   clay(bpy, 'clay_base', (0.55, 0.20, 0.14), (0.47, 0.16, 0.11), rough=0.5, seed=23),
        'post':   clay(bpy, 'clay_post', (0.86, 0.80, 0.66), (0.80, 0.73, 0.60), rough=0.5, seed=24),
        'lamp':   clay(bpy, 'clay_lamp', (0.13, 0.42, 0.40), (0.10, 0.35, 0.34), rough=0.38, seed=25),
        'shirt':  clay(bpy, 'clay_shirt', (0.96, 0.70, 0.12), (0.90, 0.62, 0.10), rough=0.5, sss=0.06, seed=26),
        'skin':   clay(bpy, 'clay_skin', (0.86, 0.60, 0.44), (0.80, 0.55, 0.40), rough=0.5, sss=0.08, seed=27),
        'hair':   clay(bpy, 'clay_hair', (0.16, 0.09, 0.06), (0.12, 0.07, 0.05), rough=0.55, seed=28),
        'pants':  clay(bpy, 'clay_pants', (0.22, 0.28, 0.52), (0.18, 0.24, 0.46), rough=0.5, seed=29),
        'dot':    clay(bpy, 'clay_dot', (0.02, 0.02, 0.025), (0.03, 0.03, 0.03), rough=0.2, sss=0.0, bump=0.02, seed=30),
        'red':    clay(bpy, 'clay_red', (0.85, 0.12, 0.10), (0.70, 0.08, 0.07), rough=0.45, seed=31),
        'desk':   paper(bpy, 'desk', (0.42, 0.27, 0.15), (0.34, 0.21, 0.11), rough=0.7, stroke=(1.0, 14.0, 1.0), stroke_scale=5.0, tooth=0.04, mottle=2.5),
        'wall':   paper(bpy, 'backdrop', (0.07, 0.09, 0.17), (0.05, 0.07, 0.13), rough=0.9, stroke=(1.0, 1.0, 18.0), stroke_scale=3.0, tooth=0.0, mottle=2.0, top_col=(0.03, 0.04, 0.09), top_z=(0.1, 0.9)),
    }
    # wire: dark metal
    wire = bpy.data.materials.new('wire')
    try: wire.use_nodes = True
    except Exception: pass
    bs = wire.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value = (0.08, 0.08, 0.085, 1); bs.inputs['Metallic'].default_value = 1.0; bs.inputs['Roughness'].default_value = 0.35
    # bulb: emissive (switched with the lamp)
    bulb = bpy.data.materials.new('bulb')
    try: bulb.use_nodes = True
    except Exception: pass
    bb = bulb.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value = (1, 0.92, 0.75, 1)
    bb.inputs['Emission Color'].default_value = (1.0, 0.86, 0.62, 1); bb.inputs['Emission Strength'].default_value = 30.0
    S['bulb'] = bb

    # ---------------- set: desk (painted card), a curved night-blue backdrop with pin-prick stars
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=60, y_segments=40, size=1.0)
    gv = [(v.co.x * 1.3 - 0.2, v.co.y * 0.75 + 0.25, 0.0004 * noise.noise(Vector((v.co.x * 9, v.co.y * 9, 0.2)))) for v in bm.verts]
    gf = [tuple(vv.index for vv in f.verts) for f in bm.faces]; bm.free()
    desk = mesh_obj(bpy, 'desk', gv, gf, M['desk'], coll)
    try: desk.visible_diffuse = False      # the lamp's pool on the desk must not light the Moon's night side (clarity of the phases)
    except Exception: pass
    V, F = [], []; nx, nz = 64, 24
    for j in range(nz + 1):
        for i in range(nx + 1):
            x = -1.6 + 3.2 * i / nx; a = (j / nz) * (math.pi / 2)
            V.append((x, 0.95 - 0.35 * math.cos(a) + 0.35, 0.35 * (1 - math.cos(a)) + 1.2 * (j / nz) ** 1.5 - 0.001))
    for j in range(nz):
        for i in range(nx):
            q = j * (nx + 1) + i; F.append((q, q + 1, q + nx + 2, q + nx + 1))
    mesh_obj(bpy, 'backdrop', V, F, M['wall'], coll)
    rng = np.random.default_rng(7)
    star = bpy.data.materials.new('star')
    try: star.use_nodes = True
    except Exception: pass
    sb = star.node_tree.nodes['Principled BSDF']; sb.inputs['Emission Color'].default_value = (1, 0.95, 0.85, 1); sb.inputs['Emission Strength'].default_value = 3.0
    for k in range(70):
        x = rng.uniform(-1.4, 1.4); z = rng.uniform(0.25, 1.15); y = 1.25 - 0.002
        uv_sphere(bpy, f'star{k}', rng.uniform(0.0016, 0.0032), star, coll, seg=8, rings=6, scale=(1, 0.3, 1)).location = (x, y, z)

    # ---------------- turntable: clay base, post; Earth on top (spins), kid on the north pole
    uv_sphere(bpy, 'base', 0.075, M['base'], coll, seg=48, rings=16, scale=(1, 1, 0.16), noise_amp=0.0012, seed=31).location = (E[0], E[1], 0.008)
    tube(bpy, 'post', [(E[0], E[1], 0.0), (E[0], E[1], 0.03), (E[0], E[1], E[2] - ER + 0.005)], [0.009, 0.0085, 0.008], M['post'], coll, n=12, ring=16, noise_amp=0.0003, seed=32)
    earth_spin = empty(bpy, 'earth_spin', coll, loc=E)
    earth = uv_sphere(bpy, 'earth', ER, M['earth'], coll, seg=64, rings=40, noise_amp=0.0012, noise_freq=40.0, seed=33)
    earth.parent = earth_spin
    for k in range(9):                                          # pressed-on clay continents (slightly raised)
        th = rng.uniform(0, 2 * math.pi); ph = rng.uniform(0.35, 2.6); r = rng.uniform(0.012, 0.024)
        n = np.array((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)))
        if n[2] > 0.88: continue
        blob = uv_sphere(bpy, f'land{k}', r, clay(bpy, f'clay_land{k}', (0.30, 0.58, 0.22), (0.24, 0.48, 0.18), rough=0.5, seed=40 + k), coll, seg=24, rings=12, scale=(1, 1, 0.22), noise_amp=0.001, seed=50 + k)
        blob.parent = earth_spin; blob.location = tuple(n * (ER - 0.0012))
        blob.rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector(n)).to_euler()
    S['earth_spin'] = earth_spin

    # the kid (2.2 cm): legs, body, head, hair, eyes; group pivot at the soles
    kid = empty(bpy, 'kid', coll, loc=KID_TOP)
    def part(o, loc): o.parent = kid; o.location = loc; return o
    for sx in (-0.0024, 0.0024):
        part(tube(bpy, f'leg{sx}', [(0, 0, 0.0), (0, 0, 0.004), (0, 0, 0.0075)], [0.0019, 0.0018, 0.0018], M['pants'], coll, n=8, ring=12, seed=60), (sx, 0, 0))
    part(uv_sphere(bpy, 'torso', 0.0052, M['shirt'], coll, seg=24, rings=14, scale=(1, 0.85, 1.25), noise_amp=0.0002, seed=61), (0, 0, 0.0118))
    head = empty(bpy, 'kid_head', coll, parent=kid, loc=(0, 0, 0.0175))
    for o, loc in [(uv_sphere(bpy, 'head', 0.0052, M['skin'], coll, seg=24, rings=16, noise_amp=0.0002, seed=62), (0, 0, 0.0035)),
                   (uv_sphere(bpy, 'hair', 0.0055, M['hair'], coll, seg=24, rings=16, scale=(1.02, 1.02, 0.75), noise_amp=0.0003, seed=63), (0, 0.0006, 0.0052)),
                   (uv_sphere(bpy, 'eyeL', 0.0008, M['dot'], coll, seg=10, rings=8), (-0.0018, -0.0047, 0.0040)),
                   (uv_sphere(bpy, 'eyeR', 0.0008, M['dot'], coll, seg=10, rings=8), (0.0018, -0.0047, 0.0040))]:
        o.parent = head; o.location = loc
    for sx in (-1, 1):
        part(tube(bpy, f'arm{sx}', [(sx * 0.0052, 0, 0.0145), (sx * 0.0068, 0, 0.0105), (sx * 0.0072, -0.0005, 0.0075)], [0.0014, 0.0013, 0.0015], M['shirt'], coll, n=8, ring=10, seed=64), (0, 0, 0))
    S['kid'] = kid; S['kid_head'] = head

    # moon arm: a wire from the post up to the orbit plane, out to the Moon; the whole arm turns about the post
    arm = empty(bpy, 'moon_arm', coll, loc=(E[0], E[1], 0.03))
    S['arm'] = arm
    moon = uv_sphere(bpy, 'moon', MR, M['moon'], coll, seg=48, rings=32, noise_amp=0.0006, noise_freq=90.0, seed=70)
    S['moon'] = moon
    S['wire'] = None; S['wire_mat'] = wire

    # lamp: weighted base, two arms, a conical clay shade with an emissive bulb; a spot light inside does the lighting
    L = np.array(LAMP); foot = np.array((LAMP[0] - 0.10, 0.06, 0.0))
    uv_sphere(bpy, 'lamp_base', 0.07, M['lamp'], coll, seg=40, rings=14, scale=(1, 1, 0.22), noise_amp=0.001, seed=80).location = tuple(foot + np.array((0, 0, 0.012)))
    elbow = np.array((LAMP[0] - 0.22, 0.04, LAMP[2] * 0.62))
    tube(bpy, 'lamp_arm1', [tuple(foot + np.array((0, 0, 0.02))), tuple((foot + elbow) / 2 + np.array((0, 0, 0.01))), tuple(elbow)], [0.007, 0.0065, 0.006], M['lamp'], coll, n=16, ring=14, seed=81)
    tube(bpy, 'lamp_arm2', [tuple(elbow), tuple((elbow + L) / 2 + np.array((0, 0, 0.03))), tuple(L - np.array((0.03, 0, -0.02)))], [0.006, 0.0058, 0.0055], M['lamp'], coll, n=16, ring=14, seed=82)
    d = (np.array(E) - L); d /= np.linalg.norm(d)
    # shade: open cone along d, built as a lathe
    V, F = [], []; ring = 40
    for j, (r, z) in enumerate([(0.022, -0.035), (0.028, -0.02), (0.046, 0.025), (0.062, 0.055)]):
        for i in range(ring):
            a = 2 * math.pi * i / ring; V.append((r * math.cos(a), r * math.sin(a), z))
    for j in range(3):
        for i in range(ring):
            a = j * ring + i; b = j * ring + (i + 1) % ring; F.append((a, b, b + ring, a + ring))
    shade = mesh_obj(bpy, 'lamp_shade', V, F, M['lamp'], coll, noise_amp=0.0008, seed=83)
    sol = shade.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = 0.004
    shade.location = tuple(L); shade.rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector(d)).to_euler()
    bulb_o = uv_sphere(bpy, 'bulb', 0.016, bulb, coll, seg=24, rings=16); bulb_o.location = tuple(L + d * 0.012)
    try: bulb_o.visible_shadow = False
    except Exception: pass
    S['lamp'] = _light(bpy, coll, 'lamp_spot', 'SPOT', tuple(L + d * 0.034), target=E, energy=190.0, size=0.012, kelvin=3600)
    S['lamp'].data.spot_size = math.radians(56); S['lamp'].data.spot_blend = 0.5
    S['lamp_E'] = 190.0
    # room: a dim cool fill (the room at night) so the Moon's night side reads as clay, not a hole
    S['fill'] = _light(bpy, coll, 'room_fill', 'AREA', (0.9, -1.2, 0.9), E, energy=0.9, size=1.6, kelvin=9000)
    S['bounce'] = _light(bpy, coll, 'bounce', 'AREA', (0.0, -0.4, -0.05), E, energy=0.12, size=0.5, kelvin=4200)
    wd = bpy.data.worlds.new('room'); sc.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    bg = wd.node_tree.nodes.get('Background')
    if bg is not None: bg.inputs['Color'].default_value = (0.006, 0.008, 0.016, 1.0); bg.inputs['Strength'].default_value = 1.0

    # the red clay X (the myth), parked out of view until its beat
    X = empty(bpy, 'myth_x', coll); S['X'] = X
    for k, ang in enumerate((math.radians(45), math.radians(-45))):
        bar = tube(bpy, f'xbar{k}', [(-0.034, 0, 0), (0, 0, 0.0008), (0.034, 0, 0)], [0.0062, 0.0068, 0.0062], M['red'], coll, n=16, ring=16, lateral=(0, 0, 1), noise_amp=0.0006, seed=90 + k)
        bar.parent = X; bar.rotation_euler = (0, ang, 0)

    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); coll.objects.link(cam); sc.camera = cam
    cd.sensor_width = 36.0; cd.clip_start = 0.004; cd.clip_end = 20
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 5.6
    S['cam'] = cam

    # compositor grain (pose-seeded) + soft corner falloff — the same finish as the clay prototype
    S['grain'] = None
    try:
        ng = bpy.data.node_groups.new('kf_finish', 'CompositorNodeTree'); sc.compositing_node_group = ng
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        N, Lk = ng.nodes, ng.links
        rl = N.new('CompositorNodeRLayers')
        ic = N.new('CompositorNodeImageCoordinates'); Lk.new(rl.outputs['Image'], ic.inputs['Image'])
        wn = N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '4D'; Lk.new(ic.outputs['Pixel'], wn.inputs['Vector'])
        amt = 0.03
        gm = N.new('ShaderNodeMath'); gm.operation = 'MULTIPLY_ADD'; Lk.new(wn.outputs['Value'], gm.inputs[0]); gm.inputs[1].default_value = 2 * amt; gm.inputs[2].default_value = 1 - amt
        W, H = float(ctx['W']), float(ctx['H'])
        sub = N.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; Lk.new(ic.outputs['Pixel'], sub.inputs[0]); sub.inputs[1].default_value = (W / 2, H / 2, 0.0)
        scl = N.new('ShaderNodeVectorMath'); scl.operation = 'SCALE'; Lk.new(sub.outputs['Vector'], scl.inputs[0]); scl.inputs['Scale'].default_value = 2.0 / W
        dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; Lk.new(scl.outputs['Vector'], dot.inputs[0]); Lk.new(scl.outputs['Vector'], dot.inputs[1])
        vg = N.new('ShaderNodeMath'); vg.operation = 'MULTIPLY_ADD'; Lk.new(dot.outputs['Value'], vg.inputs[0]); vg.inputs[1].default_value = -0.16; vg.inputs[2].default_value = 1.0
        gv2 = N.new('ShaderNodeMath'); gv2.operation = 'MULTIPLY'; Lk.new(gm.outputs['Value'], gv2.inputs[0]); Lk.new(vg.outputs['Value'], gv2.inputs[1])
        mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; sock(mix.inputs, 'Factor_Float').default_value = 1.0
        Lk.new(rl.outputs['Image'], sock(mix.inputs, 'A_Color')); Lk.new(gv2.outputs['Value'], sock(mix.inputs, 'B_Color'))
        out = N.new('NodeGroupOutput'); Lk.new(sock(mix.outputs, 'Result_Color'), out.inputs['Image'])
        sc.render.use_compositing = True; S['grain'] = wn
    except Exception as e:
        print('moon: compositor finish unavailable:', e)

    S['dup'] = {'last': None, 'pending': None, 'enabled': os.environ.get('KF_NO_PAIR_REUSE', '') == '', 'total': int(round(ctx['duration'] * ctx['fps']))}
    if S['dup']['enabled']: bpy.app.handlers.render_write.append(P._pair_reuse_handler(S))
    return S

def _wire(bpy, S, mpos):
    """rebuild the bent wire for this pose: up the post, out along the orbit radius, a small kink, into the Moon."""
    from mathutils import Vector
    if S['wire'] is not None:
        me = S['wire'].data; bpy.data.objects.remove(S['wire'], do_unlink=True); bpy.data.meshes.remove(me)
    m = np.array(mpos); base = np.array((E[0], E[1], 0.032)); top = np.array((E[0], E[1], E[2] - ER - 0.004))
    out = (m - np.array(E)); out[2] = 0; L = np.linalg.norm(out); out = out / max(L, 1e-6)
    p1 = base + out * 0.012; p2 = np.array((*(np.array(E[:2]) + out[:2] * (ER + 0.012)), E[2] - ER - 0.004))
    p3 = np.array((*(np.array(E[:2]) + out[:2] * (OR - 0.03)), min(m[2], OZ) - 0.012 if m[2] < OZ - 0.01 else m[2] - 0.022))
    p4 = m - np.array((0, 0, MR * 0.8))
    S['wire'] = tube(bpy, 'wire', [tuple(base), tuple(p1), tuple(p2), tuple(p3), tuple(p4)], [0.0011] * 5, S['wire_mat'], bpy.context.scene.collection, n=40, ring=8)

def frame(bpy, ctx, S, i, t):
    from mathutils import Vector, Euler
    pf = (i // 2) * 2; tp = pf / FPS                                # ON 2s
    th = moon_th(tp); mp = moon_pos(th, moon_dz(tp))
    mp = (mp[0] + jit(pf, 'mx', 0.0002), mp[1] + jit(pf, 'my', 0.0002), mp[2] + jit(pf, 'mz', 0.0002))
    S['moon'].location = mp; S['moon'].rotation_euler = (0.0, 0.0, -th + jit(pf, 'mr', 0.01))   # tidally locked: the same face to the Earth
    _wire(bpy, S, mp)
    S['earth_spin'].rotation_euler = (0.0, 0.0, 0.35 * tp + jit(pf, 'es', 0.006))
    # the kid turns to face the Moon (on 2s, with a little anticipation lag) and tips the head up a touch
    look = np.array(mp) - np.array(KID_TOP); yaw = math.atan2(look[1], look[0]) + math.pi / 2
    S['kid'].rotation_euler = (0.0, 0.0, yaw + jit(pf, 'ky', 0.03))
    S['kid'].location = (KID_TOP[0] + jit(pf, 'kx', 0.0002), KID_TOP[1] + jit(pf, 'kyy', 0.0002), KID_TOP[2] - 0.0005)
    dark = TIMING.get('lamp_off', B['light'][0] + 0.65)
    S['kid_head'].rotation_euler = (math.radians(-6 + (10 if tp > dark + 0.6 else 0)) + jit(pf, 'kh', 0.02), 0.0, 0.0)
    # lamp: on/off (the click)
    on = lamp_on(tp)
    S['lamp'].data.energy = S['lamp_E'] * on; S['bulb'].inputs['Emission Strength'].default_value = 30.0 * on + 0.2
    S['fill'].data.energy = 0.9 if on else 1.7
    # the red X: squashes onto the lens on "something else", then pulls off
    m0, m1 = B['myth']; x0 = TIMING.get('x_at', m0 + 5.4)
    loc, tgt, lens, focus = cam_at(tp)
    cam = S['cam']; cam.location = Vector(tuple(loc)); fwd = Vector(tuple(np.array(tgt) - np.array(loc))).normalized()
    cam.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens; cam.data.dof.focus_distance = float(np.linalg.norm(np.array(focus) - np.array(loc)))
    cam.data.dof.aperture_fstop = 11.0 if B['new'][0] <= tp < B['seat'][0] else (5.6 if lens < 70 else 8.0)
    if x0 <= tp < m1 - 0.3:
        u = (tp - x0) / 0.35; s = 0.0 if u < 0 else (1.25 if u < 1 else 0.92 if u < 1.4 else 1.0)
        out = clamp((tp - (m1 - 0.9)) / 0.5); s *= (1 - out)
        X = S['X']; X.hide_render = s <= 0
        for c in X.children: c.hide_render = s <= 0
        X.location = Vector(tuple(np.array(loc) + np.array(fwd) * 0.30)); X.rotation_euler = cam.rotation_euler; X.rotation_euler.rotate_axis('X', math.radians(90))
        X.scale = (s, s, s * (0.82 if 0 <= u < 1 else 1.0))
        if s > 0: cam.data.dof.focus_distance = 0.30
    else:
        S['X'].hide_render = True
        for c in S['X'].children: c.hide_render = True
    if S.get('grain') is not None: S['grain'].inputs['W'].default_value = pf * 0.731 + 0.17
    P._pair_reuse(bpy, ctx, S, i)
