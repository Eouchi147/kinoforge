"""P04 WITNESS - KINOFORGE Blender scene (Cycles CPU).
1628, a study at night: a quill stops mid-word; the writer turns to the window; torchlight is coming up the lane.

Contract (harness/blender_render.py): SHOTS, SETTINGS, build(bpy, ctx) -> state, frame(bpy, ctx, state, i, t).
Units metres, Z up. The writer sits near the origin facing +Y; the leaded window is in the north wall (inner face y=1.40),
front-left of him; the lane runs almost due north from that window, straight at the S2 camera through the glass.
Camera placement is solved from frame targets (NIB_FR/FLAME_FR, HEAD_FR/WIN_FRX). Everything is procedural and deterministic
(integer-hash noise and seeded random.Random; no clocks). A render_write handler applies the one grade's film finish
(halation on highlights, vignette, seeded grain) to every written PNG.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix, Quaternion, Euler

FPS = 24
S1_F, S2_F = 63, 81                      # cut on frame 63 (t = 2.625 s); 144 frames = 6.0 s
SHOTS = [
    {'name': 'S1 ECU 85mm f/2 - the nib writes, stops; rack to the flame', 'dur': S1_F / FPS},
    {'name': 'S2 MS 35mm behind-left - push to the window; the head turns', 'dur': S2_F / FPS},
]
T_CUT = S1_F / FPS
T_STOP = 1.90            # the quill stops (mid-word)
T_RACK0, T_RACK1 = 1.60, 2.45
T_DIP, T_TURN, T_TURN_END, T_SETTLE = 3.19, 3.40, 3.40 + 10 / FPS, 3.40 + 18 / FPS
T_RATTLE, T_HORN = 4.60, 5.00
T_PUSH_END = 5.60        # push-in ends; hold the last 0.4 s

SETTINGS = {'samples': 64, 'denoise': True,          # brief asked 96; 64 for the CI budget (see NOTES)
            'motion_blur': False, 'view_transform': 'AgX',
            'look': 'AgX - Medium High Contrast', 'exposure': -0.3, 'film_transparent': False,
            'max_bounces': 6, 'volume_bounces': 1, 'clamp_indirect': 8.0}

# ------------------------------------------------------------------ layout (metres)
ROOM = dict(x0=-2.6, x1=1.8, y0=-2.4, y1=1.40, z1=2.75, wt=0.30)
WIN = dict(x0=-1.45, x1=-0.75, z0=1.00, z1=1.90, yg=1.56)            # opening + glazing plane
DESK = dict(x0=-0.68, x1=0.68, y0=0.26, y1=0.96, top=0.755, th=0.055)
BOOK = dict(cx=0.015, cy=0.475, w=0.215, d=0.300, h=0.044, rot=-6.0)     # the sheet lies on a closed ledger
CANDLE_XY = (0.30, 0.74)
FIG = Vector((0.0, -0.08, 0.0))            # figure floor centre
NECK = Vector((0.0, 0.055, 1.085))         # head pivot (world)
LANE_ANG = math.radians(8.0)               # the lane runs (almost) due north from the window: up it come the torches
LANE_O = Vector((-1.10, 1.70, 0.0))
TORCHES = [dict(s0=19.7, lat=-0.40, h=2.15, ph=0.0, e=1.00, seed=31),     # seen through the glass
           dict(s0=22.2, lat=0.70, h=2.00, ph=1.3, e=0.85, seed=37),      # seen through the glass
           dict(s0=19.7, lat=-2.40, h=2.30, ph=2.1, e=2.40, seed=41),     # flanking: throws light onto his face
           dict(s0=24.7, lat=0.10, h=2.10, ph=3.7, e=0.80, seed=43)]
TORCH_SPEED = 2.45
E_CANDLE = 6.0
WB_K = 2800.0                                      # camera white balance (tungsten stock)
NIB_FR, FLAME_FR = (0.57, 0.28), (0.31, 0.68)      # S1 frame targets (x, y up)
HEAD_FR, WIN_FRX = (0.70, 0.46), 0.24              # S2 frame targets at the start of the push
S2_DIST, S2_CAMZ, S2_PUSH = 2.15, 1.45, 0.42
E_TORCH = 1350.0
SKY_W = 3.0                                          # moonlit sky through the window (cool fill)
CANDLE_K, TORCH_K = 1800.0, 1650.0              # amber candle vs red-orange pitch torches


# ------------------------------------------------------------------ deterministic noise + easing
def _hash(i, s=0):
    x = (int(i) * 0x27d4eb2d + int(s) * 0x165667b1 + 0x9e3779b9) & 0xffffffff
    x ^= x >> 15; x = (x * 0x85ebca6b) & 0xffffffff
    x ^= x >> 13; x = (x * 0xc2b2ae35) & 0xffffffff
    x ^= x >> 16
    return x / 4294967296.0


def vnoise(t, s=0):
    i = math.floor(t); f = t - i; u = f * f * (3.0 - 2.0 * f)
    return (_hash(i, s) * (1.0 - u) + _hash(i + 1, s) * u) * 2.0 - 1.0


def fbm(t, s=0, octaves=3):
    v = n = 0.0; a = f = 1.0
    for o in range(octaves):
        v += a * vnoise(t * f + 17.3 * o, s + 101 * o); n += a; a *= 0.5; f *= 2.07
    return v / n


def clamp(x, a=0.0, b=1.0): return a if x < a else (b if x > b else x)
def lerp(a, b, u): return a + (b - a) * u


def smooth(a, b, x):
    u = clamp((x - a) / (b - a)); return u * u * (3.0 - 2.0 * u)


def smoother(a, b, x):
    u = clamp((x - a) / (b - a)); return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)


def ease_out(a, b, x, p=2.0):
    u = clamp((x - a) / (b - a)); return 1.0 - (1.0 - u) ** p


# ------------------------------------------------------------------ node helpers
def _sock(sockets, key):
    if isinstance(key, int): return sockets[key]
    for s in sockets:
        if s.identifier == key: return s
    for s in sockets:
        if s.name == key: return s
    raise KeyError(key)


class NB:
    """Tiny shader-graph builder. Values are constants or output sockets."""
    def __init__(self, nt): self.nt = nt

    def node(self, kind, inputs=None, **props):
        n = self.nt.nodes.new(kind)
        for k, v in props.items(): setattr(n, k, v)
        for k, v in (inputs or {}).items(): self.put(n, k, v)
        return n

    def put(self, n, key, v):
        s = _sock(n.inputs, key)
        if isinstance(v, bpy.types.NodeSocket): self.nt.links.new(v, s); return
        dv = s.default_value
        if hasattr(dv, '__len__'):
            if isinstance(v, (int, float)): v = (v,) * len(dv)
            elif len(v) == 3 and len(dv) == 4: v = (v[0], v[1], v[2], 1.0)
        s.default_value = v

    def math(self, op, a, b=0.0, c=0.0, clamp_=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp_)
        self.put(n, 0, a); self.put(n, 1, b); self.put(n, 2, c)
        return n.outputs[0]

    def mix(self, fac, a, b, blend='MIX'):
        n = self.node('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        self.put(n, 'Factor_Float', fac); self.put(n, 'A_Color', a); self.put(n, 'B_Color', b)
        return _sock(n.outputs, 'Result_Color')

    def ramp(self, fac, stops, interp='LINEAR'):
        n = self.node('ShaderNodeValToRGB'); self.put(n, 'Fac', fac)
        cr = n.color_ramp; cr.interpolation = interp
        els = cr.elements
        while len(els) < len(stops): els.new(0.5)
        for e, (p, c) in zip(els, stops):
            e.position = p; e.color = (c[0], c[1], c[2], 1.0) if len(c) == 3 else c
        return n.outputs['Color']

    def noise(self, vec, scale, detail=4.0, rough=0.5, dist=0.0, ntype='FBM'):
        n = self.node('ShaderNodeTexNoise', {'Scale': scale, 'Detail': detail, 'Roughness': rough, 'Distortion': dist})
        try: n.noise_type = ntype
        except Exception: pass
        if vec is not None: self.put(n, 'Vector', vec)
        return n

    def bump(self, height, strength, distance, normal=None):
        n = self.node('ShaderNodeBump', {'Strength': strength, 'Distance': distance, 'Height': height})
        if normal is not None: self.put(n, 'Normal', normal)
        return n.outputs['Normal']

    def mapping(self, vec, scale=(1, 1, 1), rot=(0, 0, 0), loc=(0, 0, 0)):
        n = self.node('ShaderNodeMapping', {'Vector': vec, 'Scale': scale, 'Rotation': rot, 'Location': loc})
        return n.outputs['Vector']


P_KEYS = {'base': 'Base Color', 'rough': 'Roughness', 'metal': 'Metallic', 'ior': 'IOR', 'alpha': 'Alpha',
          'normal': 'Normal', 'sss': 'Subsurface Weight', 'sss_r': 'Subsurface Radius', 'sss_s': 'Subsurface Scale',
          'spec': 'Specular IOR Level', 'trans': 'Transmission Weight', 'coat': 'Coat Weight', 'coat_r': 'Coat Roughness',
          'sheen': 'Sheen Weight', 'sheen_r': 'Sheen Roughness', 'sheen_t': 'Sheen Tint', 'emit': 'Emission Color',
          'emit_s': 'Emission Strength', 'thin': 'Thin Wall'}


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    return m, NB(nt), nt.nodes.new('ShaderNodeOutputMaterial')


def principled(nb, **kw):
    p = nb.node('ShaderNodeBsdfPrincipled')
    try: p.subsurface_method = 'BURLEY'
    except Exception: pass
    for k, v in kw.items(): nb.put(p, P_KEYS[k], v)
    return p


def surf(nb, out, shader_out):
    nb.nt.links.new(shader_out, _sock(out.inputs, 'Surface'))


# ------------------------------------------------------------------ materials
def mat_plaster(name, tint=(0.47, 0.42, 0.35), world=True, soot_x=None):
    m, nb, out = new_mat(name)
    pos = nb.node('ShaderNodeNewGeometry').outputs['Position'] if world else nb.node('ShaderNodeTexCoord').outputs['Object']
    z = nb.node('ShaderNodeSeparateXYZ', {'Vector': pos}).outputs['Z']
    nbig = nb.noise(pos, 1.3, 3.0, 0.62)
    nmid = nb.noise(pos, 7.0, 4.0, 0.55)
    nfine = nb.noise(pos, 60.0, 3.0, 0.60)
    c = nb.ramp(nmid.outputs['Fac'], [(0.30, tuple(x * 0.80 for x in tint)), (0.70, tint)])
    stain = nb.ramp(nbig.outputs['Fac'], [(0.40, (1, 1, 1)), (0.72, (0.62, 0.56, 0.47))])
    c = nb.mix(1.0, c, stain, 'MULTIPLY')
    grime = nb.ramp(nb.math('MULTIPLY', z, 1.0 / 0.75, clamp_=True), [(0.0, (0.40, 0.37, 0.33)), (1.0, (1, 1, 1))], 'EASE')
    c = nb.mix(1.0, c, grime, 'MULTIPLY')
    soot = nb.ramp(nb.math('MULTIPLY_ADD', z, 1.0 / 0.9, -1.85 / 0.9, clamp_=True), [(0.0, (1, 1, 1)), (1.0, (0.55, 0.52, 0.49))], 'EASE')
    c = nb.mix(1.0, c, soot, 'MULTIPLY')
    if soot_x is not None:   # candle-smoke smudge on the wall above where the desk candle usually stands
        sep = nb.node('ShaderNodeSeparateXYZ', {'Vector': pos})
        dx = nb.math('ABSOLUTE', nb.math('SUBTRACT', sep.outputs['X'], soot_x))
        sm = nb.math('MULTIPLY', nb.math('SUBTRACT', 1.0, nb.math('MULTIPLY', dx, 2.6, clamp_=True), clamp_=True),
                     nb.math('MULTIPLY_ADD', sep.outputs['Z'], 0.9, -1.0, clamp_=True))
        smc = nb.ramp(sm, [(0.0, (1, 1, 1)), (1.0, (0.62, 0.58, 0.54))], 'EASE')
        c = nb.mix(1.0, c, smc, 'MULTIPLY')
    rough = nb.math('MULTIPLY_ADD', nfine.outputs['Fac'], 0.20, 0.76)
    nrm = nb.bump(nb.math('ADD', nfine.outputs['Fac'], nb.math('MULTIPLY', nmid.outputs['Fac'], 0.6)), 0.22, 0.004)
    nrm = nb.bump(nbig.outputs['Fac'], 0.10, 0.03, nrm)
    p = principled(nb, base=c, rough=rough, normal=nrm, spec=0.35)
    surf(nb, out, p.outputs[0])
    return m


def mat_oak(name, base=(0.090, 0.050, 0.025), direction='Y', scale=9.0, rough=(0.38, 0.62), wax=0.15):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    w = nb.node('ShaderNodeTexWave', {'Vector': co, 'Scale': scale, 'Distortion': 9.0, 'Detail': 2.0,
                                       'Detail Scale': 1.6, 'Detail Roughness': 0.6}, wave_type='BANDS', bands_direction=direction)
    n = nb.noise(co, 3.0, 2.0, 0.6)
    lo = tuple(x * 0.55 for x in base); hi = tuple(min(1.0, x * 1.55) for x in base)
    c = nb.ramp(w.outputs['Fac'], [(0.15, lo), (0.85, hi)])
    c = nb.mix(nb.math('MULTIPLY', n.outputs['Fac'], 0.6), c, tuple(x * 0.7 for x in base))
    r = nb.ramp(w.outputs['Fac'], [(0.0, (rough[0],) * 3), (1.0, (rough[1],) * 3)])
    nrm = nb.bump(w.outputs['Fac'], 0.10, 0.002)
    p = principled(nb, base=c, rough=r, normal=nrm, coat=wax, coat_r=0.35)
    surf(nb, out, p.outputs[0])
    return m


def mat_floor(name):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    co_r = nb.mapping(co, rot=(0, 0, math.pi / 2))            # planks run north-south (toward the window)
    br = nb.node('ShaderNodeTexBrick', {'Vector': co_r, 'Color1': (0.060, 0.034, 0.019), 'Color2': (0.042, 0.026, 0.015),
                                        'Mortar': (0.004, 0.003, 0.002), 'Scale': 1.0, 'Mortar Size': 0.0035,
                                        'Mortar Smooth': 0.2, 'Bias': 0.0, 'Brick Width': 1.85, 'Row Height': 0.215},
                 offset=0.37, offset_frequency=3, squash=1.0, squash_frequency=1)
    w = nb.node('ShaderNodeTexWave', {'Vector': co_r, 'Scale': 3.0, 'Distortion': 10.0, 'Detail': 2.0,
                                       'Detail Scale': 1.4}, wave_type='BANDS', bands_direction='Y')
    grain = nb.ramp(w.outputs['Fac'], [(0.1, (0.72, 0.72, 0.72)), (0.9, (1.25, 1.2, 1.15))])
    c = nb.mix(1.0, br.outputs['Color'], grain, 'MULTIPLY')
    wear = nb.noise(co, 0.9, 3.0, 0.6)
    c = nb.mix(nb.math('MULTIPLY_ADD', wear.outputs['Fac'], 0.8, -0.25, clamp_=True), c, (0.085, 0.060, 0.040))
    r = nb.math('MULTIPLY_ADD', wear.outputs['Fac'], 0.25, 0.32)
    r = nb.math('MAXIMUM', r, nb.math('SUBTRACT', 1.0, br.outputs['Fac']))
    nrm = nb.bump(br.outputs['Fac'], 0.35, 0.004)
    nrm = nb.bump(w.outputs['Fac'], 0.06, 0.002, nrm)
    p = principled(nb, base=c, rough=r, normal=nrm, spec=0.45)
    surf(nb, out, p.outputs[0])
    return m


def mat_paper(name, tint=(0.80, 0.735, 0.60)):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    laid = nb.node('ShaderNodeTexWave', {'Vector': co, 'Scale': 350.0, 'Distortion': 0.6, 'Detail': 1.0},
                   wave_type='BANDS', bands_direction='Y')
    chain = nb.node('ShaderNodeTexWave', {'Vector': co, 'Scale': 12.0, 'Distortion': 0.3, 'Detail': 0.0},
                    wave_type='BANDS', bands_direction='X', wave_profile='SAW')
    fib = nb.noise(nb.mapping(co, scale=(1.0, 3.0, 1.0)), 700.0, 5.0, 0.72, 0.8)
    fox = nb.noise(co, 18.0, 3.0, 0.6)
    c = nb.mix(nb.math('MULTIPLY_ADD', fox.outputs['Fac'], 1.6, -0.95, clamp_=True), tint, (0.62, 0.50, 0.33))
    c = nb.mix(nb.math('MULTIPLY', fib.outputs['Fac'], 0.25), c, (0.86, 0.80, 0.68))
    h = nb.math('ADD', nb.math('MULTIPLY', laid.outputs['Fac'], 0.35), fib.outputs['Fac'])
    h = nb.math('ADD', h, nb.math('MULTIPLY', nb.math('POWER', chain.outputs['Fac'], 30.0), 0.5))
    nrm = nb.bump(h, 0.30, 0.0004)
    p = principled(nb, base=c, rough=0.62, normal=nrm, spec=0.4, sheen=0.6, sheen_r=0.35)
    surf(nb, out, p.outputs[0])
    return m


def mat_simple(name, base, rough=0.5, metal=0.0, **kw):
    m, nb, out = new_mat(name)
    p = principled(nb, base=base, rough=rough, metal=metal, **kw)
    surf(nb, out, p.outputs[0])
    return m


def mat_noisy(name, base, rough=(0.4, 0.7), scale=60.0, bump=0.15, metal=0.0, **kw):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    n = nb.noise(co, scale, 3.0, 0.6)
    n2 = nb.noise(co, scale * 0.12, 2.0, 0.5)
    c = nb.mix(nb.math('MULTIPLY', n2.outputs['Fac'], 0.7), base, tuple(x * 0.6 for x in base))
    r = nb.math('MULTIPLY_ADD', n.outputs['Fac'], rough[1] - rough[0], rough[0])
    nrm = nb.bump(n.outputs['Fac'], bump, 0.002)
    p = principled(nb, base=c, rough=r, metal=metal, normal=nrm, **kw)
    surf(nb, out, p.outputs[0])
    return m


def mat_wool(name, base=(0.052, 0.045, 0.040)):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    n = nb.noise(co, 380.0, 2.0, 0.7)
    tw = nb.node('ShaderNodeTexWave', {'Vector': co, 'Scale': 160.0, 'Distortion': 2.0, 'Detail': 1.0},
                 wave_type='BANDS', bands_direction='DIAGONAL')
    blot = nb.noise(co, 6.0, 2.0, 0.5)
    c = nb.mix(nb.math('MULTIPLY', blot.outputs['Fac'], 0.5), base, tuple(x * 1.5 for x in base))
    nrm = nb.bump(nb.math('ADD', n.outputs['Fac'], nb.math('MULTIPLY', tw.outputs['Fac'], 0.5)), 0.25, 0.0015)
    p = principled(nb, base=c, rough=0.92, sheen=1.0, sheen_r=0.40, sheen_t=(1.0, 0.92, 0.85), spec=0.25, normal=nrm)
    surf(nb, out, p.outputs[0])
    return m


def mat_skin(name):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    n = nb.noise(co, 900.0, 2.0, 0.6)
    mot = nb.noise(co, 40.0, 2.0, 0.5)
    c = nb.mix(nb.math('MULTIPLY', mot.outputs['Fac'], 0.5), (0.50, 0.33, 0.25), (0.42, 0.24, 0.18))
    p = principled(nb, base=c, rough=0.50, sss=0.35, sss_r=(1.0, 0.42, 0.22), sss_s=0.010, spec=0.45,
                   normal=nb.bump(n.outputs['Fac'], 0.06, 0.0005))
    surf(nb, out, p.outputs[0])
    return m


def mat_quill(name):
    m, nb, out = new_mat(name)
    z = nb.node('ShaderNodeSeparateXYZ', {'Vector': nb.node('ShaderNodeTexCoord').outputs['Object']}).outputs['Z']
    c = nb.ramp(z, [(0.0, (0.010, 0.010, 0.014)), (0.0045, (0.012, 0.011, 0.014)), (0.0075, (0.32, 0.22, 0.10)),
                    (0.016, (0.66, 0.56, 0.38)), (0.30, (0.74, 0.66, 0.48))])
    r = nb.ramp(z, [(0.0, (0.12,) * 3), (0.006, (0.12,) * 3), (0.01, (0.32,) * 3)])
    p = principled(nb, base=c, rough=r, sss=0.4, sss_r=(1.0, 0.75, 0.45), sss_s=0.003, coat=0.4, coat_r=0.2)
    surf(nb, out, p.outputs[0])
    return m


def mat_feather(name):
    m, nb, out = new_mat(name)
    uv = nb.node('ShaderNodeTexCoord').outputs['UV']
    sep = nb.node('ShaderNodeSeparateXYZ', {'Vector': uv})
    u, v = sep.outputs['X'], sep.outputs['Y']                     # u along the rachis 0..1, v across -1..1
    av = nb.math('ABSOLUTE', v)
    barbs = nb.node('ShaderNodeTexWave', {'Vector': nb.node('ShaderNodeCombineXYZ', {
        'X': nb.math('ADD', u, nb.math('MULTIPLY', av, 0.30)), 'Y': v, 'Z': 0.0}).outputs[0],
        'Scale': 55.0, 'Distortion': 1.5, 'Detail': 2.0}, wave_type='BANDS', bands_direction='X')
    rag = nb.noise(uv, 9.0, 3.0, 0.6)
    split = nb.math('GREATER_THAN', nb.math('SINE', nb.math('MULTIPLY', u, 47.0)), 0.93)
    edge = nb.math('ADD', av, nb.math('MULTIPLY', rag.outputs['Fac'], 0.22))
    alpha = nb.math('SUBTRACT', 1.0, nb.math('MULTIPLY_ADD', edge, 7.0, -6.3, clamp_=True), clamp_=True)
    alpha = nb.math('MULTIPLY', alpha, nb.math('SUBTRACT', 1.0, nb.math('MULTIPLY', split, nb.math('GREATER_THAN', av, 0.55))))
    tip = nb.ramp(u, [(0.0, (0.80, 0.77, 0.70)), (0.75, (0.66, 0.62, 0.56)), (1.0, (0.30, 0.27, 0.24))])
    c = nb.mix(nb.math('MULTIPLY', barbs.outputs['Fac'], 0.35), tip, (0.45, 0.42, 0.38))
    p = principled(nb, base=c, rough=0.65, sheen=0.6, sheen_r=0.3, spec=0.3)
    tl = nb.node('ShaderNodeBsdfTranslucent', {'Color': (0.85, 0.72, 0.52)})
    mx = nb.node('ShaderNodeMixShader'); nb.put(mx, 0, 0.35)
    nb.nt.links.new(p.outputs[0], mx.inputs[1]); nb.nt.links.new(tl.outputs[0], mx.inputs[2])
    tr = nb.node('ShaderNodeBsdfTransparent')
    mx2 = nb.node('ShaderNodeMixShader'); nb.put(mx2, 0, alpha)
    nb.nt.links.new(tr.outputs[0], mx2.inputs[1]); nb.nt.links.new(mx.outputs[0], mx2.inputs[2])
    surf(nb, out, mx2.outputs[0])
    return m


def mat_flame(name, strength=26.0, t_core=1950.0, t_tip=1450.0, t_base=1250.0, edge_soft=0.9):
    """Emission driven by a blackbody gradient (consistent with the lights under the camera white balance)."""
    m, nb, out = new_mat(name)
    gz = nb.node('ShaderNodeSeparateXYZ', {'Vector': nb.node('ShaderNodeTexCoord').outputs['Generated']}).outputs['Z']
    tk = nb.ramp(gz, [(0.0, (t_base / 3000.0,) * 3), (0.22, (t_core / 3000.0,) * 3), (0.55, ((t_core + t_tip) / 6000.0,) * 3),
                      (1.0, (t_tip / 3000.0,) * 3)])
    temp = nb.math('MULTIPLY', nb.node('ShaderNodeRGBToBW', {'Color': tk}).outputs[0], 3000.0)
    col = nb.node('ShaderNodeBlackbody', {'Temperature': temp}).outputs[0]
    k = nb.ramp(gz, [(0.0, (0.15,) * 3), (0.2, (1.0,) * 3), (0.6, (0.75,) * 3), (1.0, (0.12,) * 3)])
    kb = nb.node('ShaderNodeRGBToBW', {'Color': k}).outputs[0]
    em = nb.node('ShaderNodeEmission', {'Color': col, 'Strength': nb.math('MULTIPLY', kb, strength)})
    lw = nb.node('ShaderNodeLayerWeight', {'Blend': 0.45})
    a = nb.math('POWER', lw.outputs['Facing'], edge_soft)
    tr = nb.node('ShaderNodeBsdfTransparent')
    mx = nb.node('ShaderNodeMixShader'); nb.put(mx, 0, a)
    nb.nt.links.new(em.outputs[0], mx.inputs[1]); nb.nt.links.new(tr.outputs[0], mx.inputs[2])
    surf(nb, out, mx.outputs[0])
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    return m


def mat_glass(name):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    wav = nb.noise(nb.mapping(co, scale=(1.0, 1.0, 2.2)), 9.0, 2.0, 0.5)
    seeds = nb.noise(co, 140.0, 1.0, 0.5)
    nrm = nb.bump(nb.math('ADD', wav.outputs['Fac'], nb.math('MULTIPLY', seeds.outputs['Fac'], 0.25)), 0.55, 0.02)
    g = principled(nb, base=(0.80, 0.86, 0.76), rough=0.07, ior=1.52, trans=1.0, thin=True, normal=nrm, spec=0.6)
    lp = nb.node('ShaderNodeLightPath')
    tr = nb.node('ShaderNodeBsdfTransparent', {'Color': (0.78, 0.82, 0.72)})
    mx = nb.node('ShaderNodeMixShader')
    nb.nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs[0])
    nb.nt.links.new(g.outputs[0], mx.inputs[1]); nb.nt.links.new(tr.outputs[0], mx.inputs[2])
    surf(nb, out, mx.outputs[0])
    return m


def mat_volume(name, density, color=(0.86, 0.83, 0.80), aniso=0.3):
    m, nb, out = new_mat(name)
    v = nb.node('ShaderNodeVolumePrincipled', {'Color': color, 'Density': density, 'Anisotropy': aniso})
    nb.nt.links.new(v.outputs[0], _sock(out.inputs, 'Volume'))
    return m


def mat_cobble(name):
    m, nb, out = new_mat(name)
    co = nb.node('ShaderNodeTexCoord').outputs['Object']
    vo = nb.node('ShaderNodeTexVoronoi', {'Vector': co, 'Scale': 6.0}, feature='DISTANCE_TO_EDGE')
    d = vo.outputs['Distance']
    c = nb.ramp(d, [(0.0, (0.010, 0.010, 0.010)), (0.08, (0.045, 0.042, 0.040))])
    r = nb.ramp(d, [(0.0, (0.85,) * 3), (0.10, (0.30,) * 3)])
    p = principled(nb, base=c, rough=r, normal=nb.bump(d, 0.6, 0.03))
    surf(nb, out, p.outputs[0])
    return m


# ------------------------------------------------------------------ geometry helpers
def link(ob, parent=None):
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None: ob.parent = parent
    return ob


def mesh_ob(name, bm, mat=None, smooth=False, parent=None, mats=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth: me.shade_smooth()
    for mm in ([mat] if mat is not None else []) + (mats or []): me.materials.append(mm)
    return link(bpy.data.objects.new(name, me), parent)


def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); e.location = loc; e.empty_display_size = 0.05
    return link(e, parent)


def bm_box(x0, x1, y0, y1, z0, z1, bm=None, M=None):
    bm = bm or bmesh.new()
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1); z0, z1 = min(z0, z1), max(z0, z1)
    T = Matrix.Translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)) @ Matrix.Diagonal((x1 - x0, y1 - y0, z1 - z0, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=(M @ T) if M is not None else T)
    return bm


def box(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0, parent=None, M=None):
    ob = mesh_ob(name, bm_box(x0, x1, y0, y1, z0, z1, M=M), mat, parent=parent)
    if bevel > 0:
        b = ob.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 2; b.limit_method = 'ANGLE'
    return ob


def bm_cyl(r1, r2, depth, segs=32, caps=True, M=None):
    bm = bmesh.new()
    T = Matrix.Translation((0, 0, depth / 2))
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth,
                          matrix=(M @ T) if M is not None else T)
    return bm


def bm_lathe(profile, segs=40, M=None, close_top=True, disp=None):
    """profile: [(r, z)] bottom->top; optional disp(angle, z) radial offset. Returns bmesh (open bottom)."""
    bm = bmesh.new(); rows = []
    for (r, z) in profile:
        row = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            rr = r + (disp(a, z) if disp else 0.0)
            p = Vector((rr * math.sin(a), rr * math.cos(a), z))
            row.append(bm.verts.new(M @ p if M is not None else p))
        rows.append(row)
    for j in range(len(rows) - 1):
        for k in range(segs):
            bm.faces.new((rows[j][k], rows[j][(k + 1) % segs], rows[j + 1][(k + 1) % segs], rows[j + 1][k]))
    if close_top:
        c = bm.verts.new(sum((v.co for v in rows[-1]), Vector()) / segs)
        for k in range(segs): bm.faces.new((rows[-1][k], rows[-1][(k + 1) % segs], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_rings(rings, segs, disp=None):
    """rings: [(z, rx, ry, cx, cy)] elliptical cross-sections bottom->top (world coords). angle 0 = +Y (front)."""
    bm = bmesh.new(); rows = []
    for (z, rx, ry, cx, cy) in rings:
        row = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            d = disp(a, z) if disp else 0.0
            row.append(bm.verts.new((cx + (rx + d) * math.sin(a), cy + (ry + d) * math.cos(a), z)))
        rows.append(row)
    for j in range(len(rows) - 1):
        for k in range(segs):
            bm.faces.new((rows[j][k], rows[j][(k + 1) % segs], rows[j + 1][(k + 1) % segs], rows[j + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_teardrop(width, height, segs=24, rings=18):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        zz = (z + 1.0) / 2.0                                       # 0 bottom .. 1 top
        w = (math.sin(math.pi * min(1.0, zz ** 0.62)) ** 0.9) if zz > 0 else 0.0
        w = max(w, 0.0)
        r = math.hypot(x, y)
        s = (w / r) if r > 1e-6 else 0.0
        v.co = Vector((x * s * width / 2, y * s * width / 2, zz * height))
    return bm


def add_subsurf(ob, levels=1, render=2):
    s = ob.modifiers.new('subsurf', 'SUBSURF'); s.levels = levels; s.render_levels = render
    return s


def add_solidify(ob, thick, offset=0.0):
    s = ob.modifiers.new('solidify', 'SOLIDIFY'); s.thickness = thick; s.offset = offset
    return s


def place_between(ob, a, b):
    d = b - a
    ob.rotation_mode = 'QUATERNION'
    ob.location = a
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    ob.scale = (1.0, 1.0, d.length)


def mb_capsule(mb, a, b, r_surf, k=1.0):
    a, b = Vector(a), Vector(b)
    e = mb.elements.new(type='CAPSULE')
    e.co = (a + b) / 2; e.radius = r_surf / 0.574 * k; e.size_x = (b - a).length / 2
    e.rotation = Vector((1, 0, 0)).rotation_difference((b - a).normalized())
    return e


def mb_ball(mb, c, r_surf, k=1.0):
    e = mb.elements.new(type='BALL'); e.co = Vector(c); e.radius = r_surf / 0.574 * k
    return e


def mb_ellipsoid(mb, c, semi, r=0.1, rot=None):
    e = mb.elements.new(type='ELLIPSOID'); e.co = Vector(c); e.radius = r
    u = 0.574 * r
    e.size_x, e.size_y, e.size_z = semi[0] / u, semi[1] / u, semi[2] / u
    if rot is not None: e.rotation = rot
    return e


# ------------------------------------------------------------------ handwriting (abstract looped strokes, no glyphs)
def word_path(x0, y0, loops, seed, pitch=0.0030, height=0.0036):
    rng = random.Random(seed)
    tall = set(rng.sample(range(loops), max(1, loops // 3)))
    hs = [height * (1.75 if k in tall else 1.0) * (0.85 + 0.3 * rng.random()) for k in range(loops)]
    N = loops * 16; pts = []
    for k in range(N + 1):
        th = 2 * math.pi * loops * k / N
        li = min(loops - 1, int(th / (2 * math.pi)))
        u = x0 + pitch * th / (2 * math.pi) - 0.00095 * math.sin(th)
        v = y0 + hs[li] * 0.5 * (1 - math.cos(th)) + 0.0004 * math.sin(th * 0.37 + seed)
        pts.append((u, v, th))
    cum = [0.0]
    for a, b in zip(pts, pts[1:]): cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return {'pts': pts, 'cum': cum, 'L': cum[-1]}


def path_at(wp, s):
    cum = wp['cum']; pts = wp['pts']; s = clamp(s, 0.0, wp['L'])
    lo, hi = 0, len(cum) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if cum[mid] <= s: lo = mid
        else: hi = mid
    seg = cum[hi] - cum[lo]; f = (s - cum[lo]) / seg if seg > 0 else 0.0
    a, b = pts[lo], pts[hi]
    return lerp(a[0], b[0], f), lerp(a[1], b[1], f), lerp(a[2], b[2], f)


def ink_curve(name, paths, parent, mat, bevel=0.00030, flat=0.32):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = bevel; cu.bevel_resolution = 0; cu.fill_mode = 'FULL'
    cu.use_fill_caps = True
    for pts in paths:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for p, q in zip(sp.points, pts): p.co = (q[0], q[1], 0.00005, 1.0)
    cu.materials.append(mat)
    ob = link(bpy.data.objects.new(name, cu), parent); ob.scale = (1.0, 1.0, flat)
    return ob


# ------------------------------------------------------------------ camera helpers
def look_quat(C, T):
    return (T - C).normalized().to_track_quat('-Z', 'Y')


def project(C, q, lens, P):
    M = q.to_matrix(); R, U, F = M.col[0], M.col[1], -M.col[2]
    d = P - C; z = d.dot(F); tx = 18.0 / lens; ty = tx * 9.0 / 16.0
    return 0.5 + 0.5 * d.dot(R) / z / tx, 0.5 + 0.5 * d.dot(U) / z / ty


def solve_cam(C, P, fx, fy, lens):
    """Roll-free orientation that puts world point P at frame position (fx, fy) (0..1, y up)."""
    T = P.copy(); dist = (P - C).length; tx = 18.0 / lens; ty = tx * 9.0 / 16.0
    for _ in range(40):
        q = look_quat(C, T); px, py = project(C, q, lens, P)
        ex, ey = fx - px, fy - py
        if abs(ex) + abs(ey) < 1e-6: break
        M = q.to_matrix()
        T = T - M.col[0] * (ex * 2 * tx * dist) - M.col[1] * (ey * 2 * ty * dist)
    return look_quat(C, T)


# ------------------------------------------------------------------ the film finish (one grade, every frame)
def _apply_finish(path, frame):
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    im = np.asarray(Image.open(path).convert('RGB')).astype(np.float32) / 255.0
    H, W, _ = im.shape; k = W / 1280.0
    lw = np.array([0.2126, 0.7152, 0.0722], np.float32)
    lum = im @ lw
    hm = np.clip((lum - 0.80) / 0.20, 0.0, 1.0) ** 2                       # halation: highlights only
    hal = ndimage.gaussian_filter(hm, sigma=10.0 * k)
    im = im + hal[..., None] * np.array([1.0, 0.46, 0.16], np.float32) * 0.18
    sh = np.clip(1.0 - (im @ lw) / 0.22, 0.0, 1.0) ** 2                      # blue-black: tint only the deep shadows
    im = im + sh[..., None] * np.array([-0.006, 0.002, 0.018], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2.0)
    im = im * (1.0 - 0.28 * np.clip((r - 0.30) / 0.70, 0.0, 1.0) ** 1.5)[..., None]   # vignette ~0.47 stop at corners
    rng = np.random.default_rng(4040 + int(frame))                               # seeded grain (deterministic)
    g = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), sigma=0.6 * max(1.0, k))
    g /= (g.std() + 1e-6)
    cg = rng.standard_normal((H, W, 3)).astype(np.float32)
    l2 = np.clip(im @ lw, 0.0, 1.0)
    amp = 0.030 * (0.35 + 0.65 * 4.0 * l2 * (1.0 - l2)) + 0.004
    im = im + (g[..., None] * 0.9 + cg * 0.12) * amp[..., None]
    Image.fromarray(np.clip(im * 255.0 + 0.5, 0, 255).astype(np.uint8), 'RGB').save(path)


def _kf_p04_finish(scene, *args):
    p = scene.render.filepath
    if p.lower().endswith('.png'):
        try: _apply_finish(p, scene.frame_current)
        except Exception as e: print('p04 finish failed:', e)


# ------------------------------------------------------------------ build
def build(bpy_, ctx):
    sc = bpy.context.scene
    st = {}
    cy = sc.cycles
    for k, v in dict(caustics_reflective=False, caustics_refractive=False, blur_glossy=1.0, diffuse_bounces=3,
                     glossy_bounces=2, transmission_bounces=6, transparent_max_bounces=8,
                     light_sampling_threshold=0.01).items():
        try: setattr(cy, k, v)
        except Exception: pass
    sc.render.use_persistent_data = True
    vs = sc.view_settings
    try: vs.use_white_balance = True; vs.white_balance_temperature = WB_K
    except Exception: pass
    for h in list(bpy.app.handlers.render_write):
        if getattr(h, '__name__', '') == '_kf_p04_finish': bpy.app.handlers.render_write.remove(h)
    bpy.app.handlers.render_write.append(_kf_p04_finish)

    # --- world: a dark blue night beyond the window
    w = bpy.data.worlds.new('Night'); w.use_nodes = True
    bg = w.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.0040, 0.0060, 0.0160, 1.0); bg.inputs['Strength'].default_value = 1.0
    sc.world = w

    # --- materials
    M = {}
    M['plaster'] = mat_plaster('Plaster', soot_x=CANDLE_XY[0])
    M['plaster_out'] = mat_plaster('PlasterOut', tint=(0.20, 0.18, 0.16))
    M['oak'] = mat_oak('Oak')
    M['oak_z'] = mat_oak('OakZ', direction='Z', scale=7.0)
    M['oak_dark'] = mat_oak('OakDark', base=(0.040, 0.024, 0.013), scale=6.0, rough=(0.5, 0.75), wax=0.05)
    M['floor'] = mat_floor('Floor')
    M['paper'] = mat_paper('Paper')
    M['paper2'] = mat_paper('PaperOld', tint=(0.74, 0.66, 0.50))
    M['ink'] = mat_simple('Ink', (0.008, 0.009, 0.015), rough=0.16, spec=0.7)
    M['ink_dry'] = mat_simple('InkDry', (0.020, 0.018, 0.022), rough=0.45, spec=0.4)
    M['wool'] = mat_wool('Wool')
    M['wool_b'] = mat_wool('WoolBearer', base=(0.012, 0.011, 0.010))
    M['skin'] = mat_skin('Skin')
    M['quill'] = mat_quill('Quill')
    M['feather'] = mat_feather('Feather')
    M['wax'] = mat_simple('Wax', (0.80, 0.74, 0.58), rough=0.40, sss=0.6, sss_r=(1.0, 0.85, 0.6), sss_s=0.010)
    M['waxpool'] = mat_simple('WaxPool', (0.78, 0.68, 0.48), rough=0.08, sss=0.5, sss_r=(1.0, 0.8, 0.5), sss_s=0.008)
    M['pewter'] = mat_noisy('Pewter', (0.42, 0.40, 0.37), rough=(0.24, 0.45), scale=90.0, bump=0.08, metal=1.0)
    M['wick'] = mat_simple('Wick', (0.02, 0.016, 0.014), rough=0.9, emit=(1.0, 0.25, 0.04), emit_s=1.5)
    M['flame'] = mat_flame('Flame', strength=24.0)
    M['torchflame'] = mat_flame('TorchFlame', strength=18.0, t_core=1650.0, t_tip=1250.0, t_base=1150.0)
    M['glaze'] = mat_simple('Stoneware', (0.045, 0.038, 0.032), rough=0.16, coat=0.6, coat_r=0.08)
    M['leather'] = mat_noisy('Leather', (0.085, 0.040, 0.022), rough=(0.45, 0.72), scale=140.0, bump=0.2)
    M['leather_g'] = mat_noisy('LeatherGreen', (0.030, 0.045, 0.028), rough=(0.5, 0.75), scale=140.0, bump=0.15)
    M['lead'] = mat_noisy('Lead', (0.055, 0.055, 0.060), rough=(0.38, 0.6), scale=200.0, bump=0.1, metal=0.75)
    M['glass'] = mat_glass('Glass')
    M['cobble'] = mat_cobble('Cobbles')
    M['pole'] = mat_simple('Pole', (0.03, 0.02, 0.012), rough=0.8)
    st['M'] = M

    R = ROOM; T = R['wt']; X0, X1, Y0, Y1, ZC = R['x0'], R['x1'], R['y0'], R['y1'], R['z1']
    YO = Y1 + T

    # --- room shell
    box('Floor', X0 - T, X1 + T, Y0 - T, YO, -0.06, 0.0, M['floor'])
    box('Ceiling', X0 - T, X1 + T, Y0 - T, YO, ZC, ZC + 0.12, M['plaster'])
    box('WallW', X0 - T, X0, Y0 - T, YO, 0.0, ZC + 0.12, M['plaster'])
    box('WallE', X1, X1 + T, Y0 - T, YO, 0.0, ZC + 0.12, M['plaster'])
    box('WallS', X0 - T, X1 + T, Y0 - T, Y0, 0.0, ZC + 0.12, M['plaster'])
    Wn = WIN
    box('WallN_l', X0 - T, Wn['x0'], Y1, YO, 0.0, ZC + 0.12, M['plaster'])
    box('WallN_r', Wn['x1'], X1 + T, Y1, YO, 0.0, ZC + 0.12, M['plaster'])
    box('WallN_b', Wn['x0'], Wn['x1'], Y1, YO, 0.0, Wn['z0'], M['plaster'])
    box('WallN_t', Wn['x0'], Wn['x1'], Y1, YO, Wn['z1'], ZC + 0.12, M['plaster'])
    for k, x in enumerate([Wn['x0'] - 0.16, Wn['x1'] + 0.02, 0.86]):   # timber posts of the framed wall
        box(f'Post{k}', x, x + 0.14, Y1 - 0.028, Y1 + 0.01, 0.0, ZC, M['oak_dark'], bevel=0.01)
    box('Girt', X0, X1, Y1 - 0.03, Y1 + 0.01, 2.06, 2.21, M['oak_dark'], bevel=0.01)
    box('Rail', X0, X1, Y1 - 0.022, Y1 + 0.01, 0.0, 0.16, M['oak_dark'], bevel=0.006)
    for k, x in enumerate([-1.75, -0.35, 1.05]):            # ceiling joists
        box(f'Joist{k}', x - 0.075, x + 0.075, Y0, Y1, ZC - 0.17, ZC, M['oak_dark'], bevel=0.01)
    box('Sill', Wn['x0'] - 0.05, Wn['x1'] + 0.05, Y1 - 0.045, Wn['yg'], Wn['z0'] - 0.035, Wn['z0'], M['oak'], bevel=0.005)

    # --- shelf on the north wall: books and a jug (silhouettes against the candle-lit plaster)
    box('Shelf', -0.42, 0.56, Y1 - 0.20, Y1, 1.365, 1.392, M['oak_dark'], bevel=0.004)
    for k, x in enumerate([-0.36, 0.48]):
        box(f'Bracket{k}', x - 0.015, x + 0.015, Y1 - 0.15, Y1, 1.24, 1.365, M['oak_dark'], bevel=0.003)
    rb = random.Random(17); x = -0.39
    leathers = [M['leather'], M['leather_g'], mat_noisy('LeatherRed', (0.10, 0.025, 0.018), rough=(0.45, 0.7), scale=140.0, bump=0.2)]
    for k in range(9):
        wdt = rb.uniform(0.026, 0.052); hgt = rb.uniform(0.17, 0.27); dep = rb.uniform(0.13, 0.17)
        lean = math.radians(rb.uniform(-2, 2) if k != 6 else 14.0)
        Mk = Matrix.Translation((x + wdt / 2, Y1 - 0.02 - dep / 2, 1.392)) @ Matrix.Rotation(lean, 4, 'Y')
        box(f'ShelfBook{k}', -wdt / 2, wdt / 2, -dep / 2, dep / 2, 0.0, hgt, leathers[k % 3], bevel=0.003, M=Mk)
        x += wdt + (0.004 if k != 5 else 0.06)
    mesh_ob('Jug', bm_lathe([(0.045, 0.0), (0.060, 0.05), (0.062, 0.09), (0.050, 0.14), (0.030, 0.17), (0.028, 0.20),
                             (0.033, 0.215), (0.030, 0.22)], 28, Matrix.Translation((0.47, Y1 - 0.10, 1.392)), close_top=True),
            M['glaze'], smooth=True)

    # --- the leaded window (rig so it can rattle)
    win = empty('WindowRig', ((Wn['x0'] + Wn['x1']) / 2, Wn['yg'], Wn['z0']))
    st['win'] = win; wx = win.location.x; wz = win.location.z
    fy0, fy1 = Wn['yg'] - 0.03 - Wn['yg'], Wn['yg'] + 0.03 - Wn['yg']
    hw = (Wn['x1'] - Wn['x0']) / 2; hh = Wn['z1'] - Wn['z0']; fw = 0.045
    box('WinFrameL', -hw, -hw + fw, fy0, fy1, 0.0, hh, M['oak'], 0.004, win)
    box('WinFrameR', hw - fw, hw, fy0, fy1, 0.0, hh, M['oak'], 0.004, win)
    box('WinFrameB', -hw, hw, fy0, fy1, 0.0, 0.05, M['oak'], 0.004, win)
    box('WinFrameT', -hw, hw, fy0, fy1, hh - fw, hh, M['oak'], 0.004, win)
    box('Mullion', -0.025, 0.025, fy0 - 0.01, fy1, 0.0, hh, M['oak'], 0.004, win)
    lights = [(-hw + fw, -0.025), (0.025, hw - fw)]
    za, zb = 0.05, hh - fw
    bmL = bmesh.new()
    th60 = math.tan(math.radians(60.0))
    for (a0, a1) in lights:
        wd = (a1 - a0) / 3.0
        gbm = bmesh.new()
        for vv in [(a0, 0.0, za), (a1, 0.0, za), (a1, 0.0, zb), (a0, 0.0, zb)]: gbm.verts.new(vv)
        gbm.faces.new(gbm.verts)
        mesh_ob('Glass', gbm, M['glass'], parent=win)
        segs = []
        for sgn in (1, -1):
            for kk in range(-14, 16):
                ak = a0 + kk * wd
                # line z = za + sgn*th60*(a - ak) clipped to the rectangle
                ts = []
                for a in (a0, a1):
                    z = za + sgn * th60 * (a - ak)
                    if za <= z <= zb: ts.append((a, z))
                for z in (za, zb):
                    a = ak + (z - za) / (sgn * th60)
                    if a0 <= a <= a1: ts.append((a, z))
                ts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in ts))
                if len(ts) >= 2: segs.append((ts[0], ts[-1]))
        for zz in (za + (zb - za) / 3, za + 2 * (zb - za) / 3):
            segs.append(((a0, zz), (a1, zz)))
        for (p, q) in segs:
            pa, pb = Vector((p[0], 0.0, p[1])), Vector((q[0], 0.0, q[1]))
            L = (pb - pa).length
            if L < 0.004: continue
            rot = Vector((1, 0, 0)).rotation_difference((pb - pa).normalized()).to_matrix().to_4x4()
            Mx = Matrix.Translation((pa + pb) / 2) @ rot @ Matrix.Diagonal((L + 0.005, 0.011, 0.0065, 1.0))
            bmesh.ops.create_cube(bmL, size=1.0, matrix=Mx)
        for (a, b) in [((a0, za), (a1, za)), ((a0, zb), (a1, zb)), ((a0, za), (a0, zb)), ((a1, za), (a1, zb))]:
            pa, pb = Vector((a[0], 0.0, a[1])), Vector((b[0], 0.0, b[1])); L = (pb - pa).length
            rot = Vector((1, 0, 0)).rotation_difference((pb - pa).normalized()).to_matrix().to_4x4()
            bmesh.ops.create_cube(bmL, size=1.0, matrix=Matrix.Translation((pa + pb) / 2) @ rot @ Matrix.Diagonal((L, 0.012, 0.008, 1.0)))
    mesh_ob('Cames', bmL, M['lead'], parent=win)

    # --- desk
    D = DESK; zt = D['top']
    box('DeskTop', D['x0'], D['x1'], D['y0'], D['y1'], zt - D['th'], zt, M['oak'], bevel=0.008)
    for k, (x, y) in enumerate([(D['x0'] + 0.07, D['y0'] + 0.07), (D['x1'] - 0.07, D['y0'] + 0.07),
                                (D['x0'] + 0.07, D['y1'] - 0.07), (D['x1'] - 0.07, D['y1'] - 0.07)]):
        prof = [(0.030, 0.0), (0.036, 0.04), (0.028, 0.10), (0.042, 0.22), (0.046, 0.30), (0.030, 0.42), (0.040, 0.52),
                (0.034, 0.60), (0.040, zt - D['th'] - 0.10), (0.040, zt - D['th'])]
        ob = mesh_ob(f'Leg{k}', bm_lathe(prof, 20, Matrix.Translation((x, y, 0.0)), close_top=True), M['oak_z'], smooth=True)
    box('ApronF', D['x0'] + 0.05, D['x1'] - 0.05, D['y0'] + 0.04, D['y0'] + 0.065, zt - D['th'] - 0.11, zt - D['th'], M['oak'])
    box('ApronB', D['x0'] + 0.05, D['x1'] - 0.05, D['y1'] - 0.065, D['y1'] - 0.04, zt - D['th'] - 0.11, zt - D['th'], M['oak'])

    # --- a closed leather ledger on the desk; the sheet being written lies on it
    Bk = BOOK
    MB = Matrix.Translation((Bk['cx'], Bk['cy'], zt)) @ Matrix.Rotation(math.radians(Bk['rot']), 4, 'Z')
    box('Ledger', -Bk['w'] / 2, Bk['w'] / 2, -Bk['d'] / 2, Bk['d'] / 2, 0.0, Bk['h'], M['leather'], bevel=0.005, M=MB)
    box('LedgerPages', -Bk['w'] / 2 + 0.006, Bk['w'] / 2 - 0.002, -Bk['d'] / 2 + 0.004, Bk['d'] / 2 - 0.004, 0.005, Bk['h'] - 0.005, M['paper2'], M=MB)
    MP = MB @ Matrix.Translation((0.004, 0.006, Bk['h'] + 0.0009)) @ Matrix.Rotation(math.radians(-3.0), 4, 'Z')
    pf = empty('PaperFrame'); pf.matrix_world = MP
    st['MP'] = MP.copy()
    pw, ph = 0.19, 0.26
    box('Sheet', -pw / 2, pw / 2, -ph / 2, ph / 2, -0.00035, 0.0, M['paper'], parent=pf)
    box('Sheet2', -pw / 2 + 0.003, pw / 2 + 0.004, -ph / 2 - 0.004, ph / 2 - 0.002, -0.0007, -0.00035, M['paper2'], parent=pf)

    # handwriting: static lines above + the line being written (abstract loops, never glyphs)
    rng = random.Random(1628)
    LINE_Y = -0.072; LS = 0.0105; XL, XR = -0.080, 0.080
    static = []
    for li in range(1, 13):
        y = LINE_Y + li * LS
        if y > ph / 2 - 0.018: break
        x = XL + rng.uniform(0.0, 0.004)
        while x < XR - 0.012:
            n = rng.randint(2, 7)
            wp = word_path(x, y, n, rng.randint(0, 99999))
            static.append(wp['pts']); x = wp['pts'][-1][0] + rng.uniform(0.0042, 0.0062)
    xw = XL + 0.002
    for n in (4, 3, 6):                                 # words already on the current line
        wp = word_path(xw, LINE_Y, n, rng.randint(0, 99999)); static.append(wp['pts']); xw = wp['pts'][-1][0] + 0.0050
    ink_curve('InkStatic', static, pf, M['ink_dry'])
    WA = word_path(xw, LINE_Y, 5, 501); WB = word_path(WA['pts'][-1][0] + 0.0052, LINE_Y, 8, 502)
    st['WA'], st['WB'] = WA, WB
    st['inkA'] = ink_curve('InkA', [WA['pts']], pf, M['ink'])
    st['inkB'] = ink_curve('InkB', [WB['pts']], pf, M['ink'])
    for ob in (st['inkA'], st['inkB']):
        ob.data.bevel_factor_mapping_end = 'SPLINE'; ob.data.bevel_factor_end = 1.0
    blot = mesh_ob('InkBlot', bm_cyl(1.0, 1.0, 0.00012, 24), M['ink'], parent=pf, smooth=False)
    st['blot'] = blot

    # --- inkpot, paper stack, books
    ip = mesh_ob('Inkpot', bm_lathe([(0.034, 0.0), (0.038, 0.016), (0.036, 0.034), (0.026, 0.046), (0.015, 0.052),
                                      (0.016, 0.058), (0.0135, 0.059), (0.012, 0.050)], 32,
                                     Matrix.Translation((0.25, 0.43, zt)), close_top=True), M['glaze'], smooth=True)
    stack = random.Random(7)
    zz = zt
    for k in range(6):
        a = math.radians(stack.uniform(-3, 3)); dx, dy = stack.uniform(-0.004, 0.004), stack.uniform(-0.004, 0.004)
        Mk = Matrix.Translation((-0.45 + dx, 0.58 + dy, zz)) @ Matrix.Rotation(a + math.radians(4), 4, 'Z')
        box(f'Stack{k}', -0.103, 0.103, -0.145, 0.145, 0.0, 0.0024, M['paper2'] if k % 2 else M['paper'], M=Mk)
        zz += 0.0024
    Mtop = Matrix.Translation((-0.45, 0.58, zz + 0.00002)) @ Matrix.Rotation(math.radians(4), 4, 'Z')
    tf = empty('StackFrame'); tf.matrix_world = Mtop
    rng2 = random.Random(99); stat2 = []
    for li in range(11):
        y = 0.12 - li * 0.0215; x = -0.085
        while x < 0.075:
            wp = word_path(x, y, rng2.randint(2, 6), rng2.randint(0, 9999), pitch=0.0034, height=0.004)
            stat2.append(wp['pts']); x = wp['pts'][-1][0] + 0.006
    ink_curve('InkStack', stat2, tf, M['ink_dry'], bevel=0.00035)
    for k, (h_, c_) in enumerate([(0.045, M['leather']), (0.035, M['leather_g'])]):
        Mb = Matrix.Translation((-0.47, 0.86, zt + (0.0 if k == 0 else 0.045))) @ Matrix.Rotation(math.radians(8 - 14 * k), 4, 'Z')
        box(f'Book{k}', -0.13, 0.13, -0.09, 0.09, 0.0, h_, c_, bevel=0.004, M=Mb)
        box(f'BookPages{k}', -0.124, 0.128, -0.087, 0.087, 0.004, h_ - 0.004, M['paper2'], M=Mb)

    # --- candle in a pewter chamberstick
    cx, cyy = CANDLE_XY
    Mc = Matrix.Translation((cx, cyy, zt))
    mesh_ob('Chamberstick', bm_lathe([(0.064, 0.0), (0.066, 0.003), (0.068, 0.011), (0.064, 0.012), (0.058, 0.005),
                                       (0.020, 0.005), (0.019, 0.009), (0.017, 0.022), (0.0195, 0.024), (0.0185, 0.026),
                                       (0.0125, 0.026)], 40, Mc, close_top=True), M['pewter'], smooth=True)
    tb = bmesh.new()   # ring handle (a torus)
    Rt, rt, nu, nv = 0.016, 0.0035, 24, 10
    rows = []
    for i_ in range(nu):
        a = 2 * math.pi * i_ / nu; row = []
        for j_ in range(nv):
            b_ = 2 * math.pi * j_ / nv
            rr = Rt + rt * math.cos(b_)
            row.append(tb.verts.new((cx + 0.080 + rr * math.cos(a), cyy + rt * math.sin(b_), zt + 0.014 + rr * math.sin(a))))
        rows.append(row)
    for i_ in range(nu):
        for j_ in range(nv):
            tb.faces.new((rows[i_][j_], rows[(i_ + 1) % nu][j_], rows[(i_ + 1) % nu][(j_ + 1) % nv], rows[i_][(j_ + 1) % nv]))
    tor = mesh_ob('Handle', tb, M['pewter'], smooth=True)
    tor.rotation_euler = (0, 0, 0)
    zc0 = zt + 0.026
    CH = 0.050                                                    # burned-down stub
    mesh_ob('Candle', bm_cyl(0.0118, 0.0112, CH, 28, M=Mc @ Matrix.Translation((0, 0, 0.026))), M['wax'], smooth=True)
    for k, (a, h_, s_) in enumerate([(0.4, 0.030, 1.0), (2.3, 0.018, 0.8), (4.4, 0.038, 0.7)]):
        db = bmesh.new(); bmesh.ops.create_uvsphere(db, u_segments=12, v_segments=8, radius=1.0)
        Md = Matrix.Translation((cx + 0.0112 * math.cos(a), cyy + 0.0112 * math.sin(a), zc0 + h_)) @ Matrix.Diagonal((0.0032 * s_, 0.0032 * s_, 0.010 * s_, 1.0))
        bmesh.ops.transform(db, matrix=Md, verts=db.verts)
        mesh_ob(f'Drip{k}', db, M['wax'], smooth=True)
    ztop_c = zc0 + CH
    mesh_ob('WaxPool', bm_cyl(0.0095, 0.0095, 0.0008, 24, M=Matrix.Translation((cx, cyy, ztop_c - 0.0016))), M['waxpool'], smooth=True)
    wk = mesh_ob('Wick', bm_cyl(0.0007, 0.0005, 0.0085, 8, M=Matrix.Translation((cx, cyy, ztop_c - 0.001)) @ Matrix.Rotation(math.radians(9), 4, 'X')), M['wick'], smooth=True)
    flame_base = Vector((cx, cyy - 0.0008, ztop_c + 0.0045))
    fl = mesh_ob('Flame', bm_teardrop(0.0085, 0.030), M['flame'], smooth=True)
    fl.location = flame_base; fl.visible_shadow = False
    try: fl.visible_volume_scatter = False
    except Exception: pass
    st['flame'], st['flame_base'] = fl, flame_base
    cl = bpy.data.lights.new('CandleLight', 'POINT'); cl.energy = E_CANDLE; cl.shadow_soft_size = 0.005
    cl.use_temperature = True; cl.temperature = CANDLE_K; cl.color = (1.0, 1.0, 1.0)
    clo = link(bpy.data.objects.new('CandleLight', cl)); clo.location = flame_base + Vector((0, 0, 0.012))
    st['candle'] = clo
    st['flame_pt'] = flame_base + Vector((0, 0, 0.011))

    # --- the writer
    torso = empty('Torso', FIG.copy()); st['torso'] = torso

    def cloak_disp(a, z):
        fall = max(0.0, 1.0 - z / 1.08) ** 1.1
        return (0.013 * math.sin(7 * a + 0.6) + 0.007 * math.sin(13 * a + 2.1 + 3 * z)) * fall + 0.003 * math.sin(23 * a + z * 9)
    rings = [(0.00, 0.41, 0.43, 0.0, 0.04), (0.16, 0.385, 0.40, 0.0, 0.04), (0.33, 0.345, 0.37, 0.0, 0.04),
             (0.46, 0.31, 0.34, 0.0, 0.05), (0.56, 0.255, 0.20, 0.0, 0.03), (0.70, 0.245, 0.165, 0.0, 0.05),
             (0.84, 0.255, 0.16, 0.0, 0.085), (0.95, 0.245, 0.15, 0.0, 0.115), (1.01, 0.21, 0.125, 0.0, 0.13),
             (1.05, 0.14, 0.10, 0.0, 0.135), (1.075, 0.07, 0.07, 0.0, 0.135), (1.088, 0.02, 0.02, 0.0, 0.135)]
    cloak = mesh_ob('Cloak', bm_rings(rings, 48, cloak_disp), M['wool'], smooth=True, parent=torso)
    add_subsurf(cloak, 1, 1)
    cape_rings = [(0.79, 0.275, 0.185, 0.0, 0.075), (0.88, 0.272, 0.178, 0.0, 0.098), (0.96, 0.258, 0.162, 0.0, 0.118),
                  (1.02, 0.205, 0.132, 0.0, 0.130), (1.065, 0.125, 0.105, 0.0, 0.136), (1.092, 0.06, 0.07, 0.0, 0.137)]
    cape = mesh_ob('Cape', bm_rings(cape_rings, 48, lambda a, z: 0.010 * math.sin(9 * a + 1.0) * max(0.0, (1.0 - z) * 4.0)),
                   M['wool'], smooth=True, parent=torso)
    add_solidify(cape, 0.008, 1.0); add_subsurf(cape, 1, 1)

    # head pivot, hood, face
    neck = empty('Neck', NECK - FIG, parent=torso); neck.rotation_mode = 'XYZ'; st['neck'] = neck
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=24, radius=1.0)
    HC = Vector((0.0, 0.028, 0.100))                                  # head centre in neck space (rest)
    fwd = Vector((0.0, 0.92, -0.30)).normalized()
    THR = 0.12                                                         # hood worn back: rim near the ears (83 deg)
    kill = [f for f in hb.faces if (f.calc_center_median().normalized()).dot(fwd) > THR]
    bmesh.ops.delete(hb, geom=kill, context='FACES')
    for v in hb.verts:                                                # snap the rim onto the cone: a clean edge, no stair-steps
        if v.is_boundary:
            d = v.co.normalized(); side = (d - fwd * d.dot(fwd))
            if side.length > 1e-6: v.co = fwd * THR + side.normalized() * math.sqrt(1.0 - THR * THR)
    for v in hb.verts:
        v.co = Vector((v.co.x * 0.128 * 0.93, v.co.y * 0.128 * 1.10, v.co.z * 0.128 * 1.08))
    for v in hb.verts:
        x, y, z = v.co
        d = v.co.normalized().dot(fwd)
        if d > 0.05:                                                              # cowl: the rim reaches forward
            k_ = (d - 0.05) / (THR - 0.05); v.co.y = y + 0.012 * k_                     # slight lip at the rim
        x, y, z = v.co
        if y < 0.0 and z > 0.02: v.co.y = y - 0.035 * (-y / 0.14) * (z / 0.14)          # soft peak at the back
        if z < -0.02:
            k_ = (-0.02 - z) / 0.12; v.co.x = x * (1.0 + 0.45 * k_); v.co.y = y * (1.0 + 0.30 * k_) - 0.02 * k_; v.co.z = z - 0.045 * k_   # drape onto the cape
        v.co = v.co + HC + Vector((0.0, -0.030, 0.020))                       # worn back: the profile reads in silhouette
    bmesh.ops.recalc_face_normals(hb, faces=hb.faces)
    hood = mesh_ob('Hood', hb, M['wool'], smooth=True, parent=neck)
    add_solidify(hood, 0.016, 1.0); add_subsurf(hood, 1, 1)

    fmb = bpy.data.metaballs.new('Face'); fmb.resolution = 0.006; fmb.render_resolution = 0.0032; fmb.threshold = 0.6
    face = link(bpy.data.objects.new('Face', fmb), neck); fmb.materials.append(M['skin'])
    H = HC
    mb_ellipsoid(fmb, H + Vector((0, -0.010, 0.012)), (0.068, 0.084, 0.080), 0.1)
    mb_ellipsoid(fmb, H + Vector((0, 0.036, -0.058)), (0.046, 0.044, 0.034), 0.06)
    for sx in (-1, 1): mb_ball(fmb, H + Vector((0.044 * sx, 0.056, -0.006)), 0.019)
    mb_capsule(fmb, H + Vector((-0.032, 0.074, 0.026)), H + Vector((0.032, 0.074, 0.026)), 0.013)
    mb_capsule(fmb, H + Vector((0.0, 0.086, 0.014)), H + Vector((0.0, 0.101, -0.019)), 0.0075)
    mb_ball(fmb, H + Vector((0.0, 0.101, -0.022)), 0.0098)
    mb_ellipsoid(fmb, H + Vector((0.0, 0.082, -0.047)), (0.020, 0.008, 0.008), 0.03)
    mb_ball(fmb, H + Vector((0.0, 0.076, -0.084)), 0.019)
    mb_capsule(fmb, H + Vector((0.0, -0.005, -0.075)), H + Vector((0.0, -0.020, -0.150)), 0.040)
    beard = bmesh.new(); bmesh.ops.create_uvsphere(beard, u_segments=20, v_segments=12, radius=1.0)
    for v in beard.verts:
        x_, y_, z_ = v.co
        v.co = H + Vector((x_ * 0.047, 0.052 + y_ * 0.030 + 0.008 * max(0.0, -z_), -0.078 + z_ * 0.036 - 0.008 * max(0.0, -z_) ** 2))
    hair = mat_noisy('Hair', (0.045, 0.032, 0.024), rough=(0.55, 0.8), scale=900.0, bump=0.4, sheen=0.8, sheen_r=0.3)
    bd = mesh_ob('Beard', beard, hair, smooth=True, parent=neck)

    # right hand + quill rig (origin = nib tip)
    rig = empty('PenRig'); rig.rotation_mode = 'QUATERNION'; st['rig'] = rig
    qb = bmesh.new()
    prof = [(0.00025, 0.0), (0.0011, 0.0035), (0.0021, 0.008), (0.0027, 0.013), (0.0030, 0.030), (0.0033, 0.075),
            (0.0030, 0.12), (0.0022, 0.17), (0.0010, 0.225), (0.0002, 0.232)]
    qbm = bm_lathe(prof, 14, close_top=True)
    for v in qbm.verts:
        z = v.co.z
        if z < 0.014: v.co.y *= 0.62 + 0.38 * (z / 0.014)                 # flattened nib
        v.co.x += 0.10 * (z / 0.232) ** 2 * 0.06                           # slight curve of the shaft
    quill = mesh_ob('Quill', qbm, M['quill'], smooth=True, parent=rig)
    vb = bmesh.new(); uvl = vb.loops.layers.uv.new('UVMap')
    NU = 26; rowsv = []
    for i_ in range(NU + 1):
        u = i_ / NU; z = 0.112 + u * 0.118
        xc = 0.10 * (z / 0.232) ** 2 * 0.06
        wl = 0.011 * math.sin(math.pi * min(1.0, u * 1.15) ** 0.7) + 0.0005
        wr = 0.020 * math.sin(math.pi * min(1.0, u * 1.08) ** 0.8) + 0.0005
        row = [vb.verts.new((xc - wl, 0.0045 + 0.0010 * math.sin(u * 3), z)), vb.verts.new((xc, 0.0040, z)),
               vb.verts.new((xc + wr, 0.0040 + 0.0030 * u, z - 0.010 * (1 - u)))]
        rowsv.append((row, u))
    for i_ in range(NU):
        (ra, ua), (rb, ub) = rowsv[i_], rowsv[i_ + 1]
        for j_, (vv0, vv1) in enumerate([(-1.0, 0.0), (0.0, 1.0)]):
            f = vb.faces.new((ra[j_], ra[j_ + 1], rb[j_ + 1], rb[j_]))
            for lp, (uu, vv) in zip(f.loops, [(ua, vv0), (ua, vv1), (ub, vv1), (ub, vv0)]): lp[uvl].uv = (uu, vv)
    vane = mesh_ob('Vane', vb, M['feather'], smooth=True, parent=rig)

    hmb = bpy.data.metaballs.new('Hand'); hmb.resolution = 0.004; hmb.render_resolution = 0.0016; hmb.threshold = 0.6
    hand = link(bpy.data.objects.new('Hand', hmb), rig); hmb.materials.append(M['skin'])
    # rig-local: +Z along the shaft, +Y = back of the hand (away from the paper), +X = little-finger side
    def chain(pts, radii):
        for (a, b), (ra, rb) in zip(zip(pts, pts[1:]), zip(radii, radii[1:])): mb_capsule(hmb, a, b, (ra + rb) / 2)
    chain([(-0.002, 0.0098, 0.031), (0.004, 0.0118, 0.050), (0.009, 0.0085, 0.069), (0.013, -0.004, 0.090)],
          [0.0062, 0.0068, 0.0080, 0.0094])                                   # index: pad on top of the shaft
    chain([(-0.0098, 0.0015, 0.035), (-0.0165, -0.0025, 0.052), (-0.0185, -0.011, 0.072), (-0.004, -0.023, 0.101)],
          [0.0074, 0.0082, 0.0098, 0.0130])                                   # thumb: pad on the radial side
    chain([(0.0062, -0.0055, 0.024), (0.0125, -0.0085, 0.044), (0.0225, -0.0160, 0.066), (0.027, -0.019, 0.091)],
          [0.0062, 0.0068, 0.0078, 0.0090])                                   # middle: supports from below
    chain([(0.026, -0.0215, 0.054), (0.0305, -0.030, 0.061), (0.0345, -0.034, 0.075), (0.037, -0.029, 0.095)],
          [0.0058, 0.0064, 0.0074, 0.0084])                                   # ring: curled under
    chain([(0.036, -0.035, 0.071), (0.041, -0.041, 0.084), (0.043, -0.036, 0.100)], [0.0052, 0.0060, 0.0072])   # little
    mb_ellipsoid(hmb, (0.024, -0.025, 0.114), (0.030, 0.0145, 0.031), 0.05)
    mb_capsule(hmb, (0.020, -0.029, 0.130), (0.020, -0.034, 0.180), 0.021)
    nail = bmesh.new(); bmesh.ops.create_uvsphere(nail, u_segments=12, v_segments=8, radius=1.0)
    for v in nail.verts: v.co = Vector((-0.0145 + v.co.x * 0.0020, 0.0008 + v.co.y * 0.0055, 0.039 + v.co.z * 0.0062))
    mesh_ob('ThumbNail', nail, mat_simple('Nail', (0.62, 0.50, 0.44), rough=0.25, sss=0.3, sss_r=(1, 0.5, 0.3), sss_s=0.004), smooth=True, parent=rig)

    # sleeves (tapered open tubes placed between world points every frame)
    def sleeve(name, r0, r1):
        ob = mesh_ob(name, bm_cyl(r0, r1, 1.0, 28, caps=False), M['wool'], smooth=True)
        add_solidify(ob, 0.007, 1.0); add_subsurf(ob, 1, 1)
        return ob
    st['sl_ru'] = sleeve('SleeveRU', 0.060, 0.056); st['sl_rf'] = sleeve('SleeveRF', 0.054, 0.050)
    st['sl_lu'] = sleeve('SleeveLU', 0.060, 0.056); st['sl_lf'] = sleeve('SleeveLF', 0.054, 0.052)
    st['sh_r'] = Vector((0.205, 0.115, 0.955)); st['el_r'] = Vector((0.285, 0.165, 0.745))     # torso-local
    st['sh_l'] = Vector((-0.205, 0.115, 0.955)); st['el_l'] = Vector((-0.355, 0.200, 0.765))

    # left hand resting on the written stack
    lmb = bpy.data.metaballs.new('LHand'); lmb.resolution = 0.006; lmb.render_resolution = 0.0028
    lh = link(bpy.data.objects.new('LHand', lmb)); lmb.materials.append(M['skin'])
    LB = Vector((-0.385, 0.475, zz + 0.016))
    Rl = Matrix.Rotation(math.radians(-14.0), 3, 'Z')
    def lp_(x, y, z): return LB + Rl @ Vector((x, y, z))
    mb_ellipsoid(lmb, lp_(0.0, 0.0, 0.0), (0.040, 0.045, 0.012), 0.05, rot=Rl.to_quaternion())
    for k, (x, L_, r_) in enumerate([(-0.026, 0.070, 0.0075), (-0.009, 0.080, 0.0080), (0.008, 0.077, 0.0076), (0.024, 0.062, 0.0068)]):
        a = lp_(x * 1.1, 0.035, 0.002); b_ = lp_(x * 1.25, 0.035 + L_ * 0.55, 0.000); c_ = lp_(x * 1.3, 0.035 + L_, -0.008)
        mb_capsule(lmb, a, b_, r_); mb_capsule(lmb, b_, c_, r_ * 0.92)
    mb_capsule(lmb, lp_(-0.034, -0.012, 0.0), lp_(-0.058, 0.025, -0.004), 0.010)
    mb_capsule(lmb, lp_(-0.058, 0.025, -0.004), lp_(-0.066, 0.052, -0.008), 0.0085)
    mb_capsule(lmb, lp_(0.0, -0.035, 0.002), lp_(0.0, -0.075, 0.006), 0.022)
    st['wr_l'] = lp_(0.0, -0.068, 0.006)

    # --- outside: the lane (north-west), facades, cobbles, torches, bearers, moon
    ML = Matrix.Translation(LANE_O) @ Matrix.Rotation(LANE_ANG, 4, 'Z')   # local x = across (right), y = up-lane
    st['ML'] = ML
    box('Ground', -5.0, 5.0, 0.0, 57.0, -0.20, -0.15, M['cobble'], M=ML)
    box('FacadeL', -5.0, -3.0, 1.5, 55.0, -0.15, 6.5, M['plaster_out'], M=ML)
    box('FacadeR', 3.0, 5.0, 1.5, 55.0, -0.15, 6.5, M['plaster_out'], M=ML)
    box('JettyL', -3.0, -2.6, 4.0, 55.0, 2.9, 6.5, M['plaster_out'], M=ML)
    box('JettyR', 2.6, 3.0, 6.0, 55.0, 2.9, 6.5, M['plaster_out'], M=ML)
    box('EndHouse', -5.0, 5.0, 55.0, 57.0, -0.15, 7.5, M['plaster_out'], M=ML)
    for k in range(10):                                           # dark doorways along the lane
        side = -1 if k % 2 == 0 else 1; s_ = 4.0 + k * 4.6
        box(f'Door{k}', side * 3.02, side * 2.98, s_, s_ + 1.0, -0.15, 2.0, M['oak_dark'], M=ML)
    st['torches'] = []
    for k, td in enumerate(TORCHES):
        L_ = bpy.data.lights.new(f'Torch{k}', 'POINT'); L_.energy = E_TORCH; L_.shadow_soft_size = 0.12
        L_.use_temperature = True; L_.temperature = TORCH_K
        lo = link(bpy.data.objects.new(f'Torch{k}', L_))
        tfl = mesh_ob(f'TorchFlame{k}', bm_teardrop(0.13, 0.34, 16, 12), M['torchflame'], smooth=True)
        tfl.visible_shadow = False
        pole = mesh_ob(f'TorchPole{k}', bm_cyl(0.022, 0.018, 0.75, 10), M['pole'])
        bear = mesh_ob(f'Bearer{k}', bm_rings([(0.0, 0.28, 0.24, 0, 0), (0.9, 0.22, 0.17, 0, 0), (1.42, 0.21, 0.13, 0, 0),
                                               (1.52, 0.11, 0.10, 0, 0), (1.62, 0.10, 0.10, 0, 0), (1.80, 0.07, 0.08, 0, -0.01),
                                               (1.84, 0.01, 0.01, 0, -0.01)], 16), M['wool_b'], smooth=True)
        st['torches'].append((td, lo, tfl, pole, bear))
    moon = bpy.data.lights.new('Moon', 'SUN'); moon.energy = 0.22; moon.angle = math.radians(0.5)
    moon.use_temperature = True; moon.temperature = 7500.0
    mo = link(bpy.data.objects.new('Moon', moon))
    sky = bpy.data.lights.new('SkyFill', 'AREA'); sky.shape = 'RECTANGLE'; sky.size = 1.1; sky.size_y = 1.3
    sky.energy = SKY_W; sky.use_temperature = True; sky.temperature = 9000.0
    sko = link(bpy.data.objects.new('SkyFill', sky)); sko.location = ((WIN['x0'] + WIN['x1']) / 2, YO + 0.45, (WIN['z0'] + WIN['z1']) / 2 + 0.15)
    sko.rotation_euler = (math.radians(-90.0), 0.0, 0.0); sko.visible_camera = False; sko.visible_glossy = False; sko.visible_transmission = False
    mo.rotation_euler = Vector((0, 0, -1)).rotation_difference(Vector((0.42, -0.72, -0.55)).normalized()).to_euler()

    # --- volumes (homogeneous: distance-sampled, cheap)
    st['fogs'] = [box('RoomFog', X0, X1, Y0, YO, 0.0, ZC, mat_volume('RoomFogMat', 0.05, aniso=0.30))]

    # --- camera
    camd = bpy.data.cameras.new('Cam'); camd.sensor_width = 36.0; camd.sensor_fit = 'HORIZONTAL'
    camd.clip_start = 0.01; camd.clip_end = 200.0
    camd.dof.use_dof = True; camd.dof.aperture_blades = 7; camd.dof.aperture_rotation = math.radians(12)
    cam = link(bpy.data.objects.new('Cam', camd)); cam.rotation_mode = 'QUATERNION'
    sc.camera = cam; st['cam'] = cam

    bpy.context.view_layer.update()
    # --- shot cameras (solved so the subject lands on a chosen frame position)
    nib0 = MP @ Vector((WA['pts'][0][0], WA['pts'][0][1], 0.0))
    nib_mid = MP @ Vector((WB['pts'][0][0], LINE_Y + 0.002, 0.0))
    st['nib_ref'] = nib_mid
    fpt = st['flame_pt']
    dir0 = Vector((fpt.x - nib_mid.x, fpt.y - nib_mid.y, 0.0)).normalized()

    def s1(dl, h):
        C = nib_mid - (Matrix.Rotation(math.radians(dl), 3, 'Z') @ dir0) * 0.318 + Vector((0.0, 0.0, h))
        Q = solve_cam(C, nib_mid, NIB_FR[0], NIB_FR[1], 85.0)
        return C, Q, project(C, Q, 85.0, fpt)
    dl, h = -7.0, 0.03
    for _ in range(25):                      # Newton on (azimuth, height) -> flame at FLAME_FR
        C, Q, f0 = s1(dl, h)
        e = (FLAME_FR[0] - f0[0], FLAME_FR[1] - f0[1])
        if abs(e[0]) + abs(e[1]) < 1e-4: break
        fa = s1(dl + 0.5, h)[2]; fb = s1(dl, h + 0.002)[2]
        j11, j21 = (fa[0] - f0[0]) / 0.5, (fa[1] - f0[1]) / 0.5
        j12, j22 = (fb[0] - f0[0]) / 0.002, (fb[1] - f0[1]) / 0.002
        det = j11 * j22 - j12 * j21
        if abs(det) < 1e-12: break
        dl += clamp((j22 * e[0] - j12 * e[1]) / det, -6.0, 6.0); h = clamp(h + (-j21 * e[0] + j11 * e[1]) / det, 0.008, 0.12)
    C1, Q1, ff = s1(dl, h)
    st['C1'], st['Q1'] = C1, Q1
    head_w = NECK + HC
    st['head_w'] = head_w
    win_c = Vector(((WIN['x0'] + WIN['x1']) / 2, Y1, (WIN['z0'] + WIN['z1']) / 2))
    st['win_c'] = win_c

    def s2(beta):
        C = head_w + Vector((-math.sin(math.radians(beta)), -math.cos(math.radians(beta)), 0.0)) * S2_DIST
        C.z = S2_CAMZ
        Q = solve_cam(C, head_w, HEAD_FR[0], HEAD_FR[1], 35.0)
        return C, Q, project(C, Q, 35.0, win_c)
    lo_b, hi_b = 5.0, 70.0                    # bisection on the bearing -> window centre at WIN_FRX
    for _ in range(40):
        mid = 0.5 * (lo_b + hi_b)
        if s2(mid)[2][0] < WIN_FRX: hi_b = mid          # larger bearing -> window further left
        else: lo_b = mid
    C2a, Q2, wf = s2(0.5 * (lo_b + hi_b))
    toward = (win_c - C2a).normalized()
    st['C2a'], st['C2b'], st['Q2'] = C2a, C2a + toward * S2_PUSH, Q2
    print('p04: S1 cam', tuple(round(x, 3) for x in C1), 'az', round(dl, 2), 'h', round(h, 3), 'flame->', tuple(round(x, 3) for x in ff),
          '| S2 cam', tuple(round(x, 3) for x in C2a), 'bearing', round(0.5 * (lo_b + hi_b), 1), 'window->', tuple(round(x, 3) for x in wf),
          'end: head->', tuple(round(x, 3) for x in project(st['C2b'], Q2, 35.0, head_w)), 'window->', tuple(round(x, 3) for x in project(st['C2b'], Q2, 35.0, win_c)))
    hv = win_c - head_w
    st['yaw_win'] = math.degrees(math.atan2(-hv.x, hv.y)); st['pitch_win'] = math.degrees(math.atan2(hv.z, hv.xy.length))
    tn = nib_mid - head_w
    st['yaw_nib'] = math.degrees(math.atan2(-tn.x, tn.y)); st['pitch_nib'] = math.degrees(math.atan2(tn.z, tn.xy.length))
    print('p04: head yaw/pitch to window', round(st['yaw_win'], 1), round(st['pitch_win'], 1), 'to nib', round(st['yaw_nib'], 1), round(st['pitch_nib'], 1))
    return st


# ------------------------------------------------------------------ animation
def nib_state(st, t):
    """Returns (u, v, lift, fracA, fracB, theta) in paper space."""
    WA, WB = st['WA'], st['WB']
    vA = 0.65 * WA['L'] / 0.70
    if t < 0.70:
        s = WA['L'] * 0.35 + vA * t
        u, v, th = path_at(WA, s); return u, v, 0.0, s / WA['L'], 0.0, th
    if t < 0.84:
        k = smooth(0.70, 0.84, t)
        a, b = WA['pts'][-1], WB['pts'][0]
        return lerp(a[0], b[0], k), lerp(a[1], b[1], k), 0.0026 * math.sin(math.pi * k), 1.0, 0.0, 0.0
    # word B: steady, falter from 1.45 s, a last slow stroke, stop at T_STOP
    n = 60; tt = min(t, T_STOP); dt = (tt - 0.84) / n; s = 0.0
    for j in range(n):
        x = 0.84 + (j + 0.5) * dt
        g = 1.0 - 0.72 * smooth(1.45, 1.68, x)
        g *= 1.0 - smooth(1.76, T_STOP, x)
        s += vA * g * dt
    u, v, th = path_at(WB, s)
    return u, v, 0.0, 1.0, s / WB['L'], th


def pose_writing(st, t):
    u, v, lift, fa, fb, th = nib_state(st, t)
    MP = st['MP']
    nib = MP @ Vector((u, v, 0.00012 + lift))
    st['nib_now'] = nib
    rig = st['rig']; rig.location = nib
    Z = Vector((0.30, -0.42, 0.855)).normalized()
    X = Vector((0, 0, 1)).cross(Z).normalized(); Y = Z.cross(X)
    base = Matrix((X, Y, Z)).transposed().to_quaternion()
    writing = 1.0 - smooth(1.70, T_STOP, t)
    wob = Euler((math.radians(1.6 * math.sin(th) * writing), math.radians(1.0 * math.cos(th) * writing + 3.0 * lift / 0.0026), 0.0)).to_quaternion()
    rig.rotation_quaternion = base @ wob
    for ob, f in ((st['inkA'], fa), (st['inkB'], fb)):
        ob.data.bevel_factor_end = max(0.0005, f); ob.hide_render = f <= 0.0005
    blot = st['blot']
    if t >= T_STOP:
        ub, vb, *_ = nib_state(st, T_STOP)
        r = 0.0004 + 0.0017 * ease_out(T_STOP, 2.6, t, 2.5)
        blot.location = (ub, vb, 0.00002); blot.scale = (r, r * 0.92, 1.0); blot.hide_render = False
    else:
        blot.hide_render = True


def candle_level(t):
    e = 1.0 + 0.07 * fbm(t * 5.3, 11) + 0.04 * fbm(t * 13.7, 12)
    e -= 0.10 * max(0.0, fbm(t * 1.7, 13) - 0.25)
    e -= 0.38 * math.exp(-((t - (T_RATTLE + 0.08)) / 0.10) ** 2)          # draught from the rattling window
    return e


def pose_candle(st, t):
    lv = candle_level(t)
    st['candle'].data.energy = E_CANDLE * lv
    fl = st['flame']
    g = math.exp(-((t - (T_RATTLE + 0.08)) / 0.12) ** 2)
    fl.scale = (1.0 - 0.05 * fbm(t * 6.1, 21), 1.0 - 0.05 * fbm(t * 5.7, 22), 0.92 + 0.10 * fbm(t * 6.6, 23) - 0.25 * g)
    fl.rotation_euler = (math.radians(4.0 * fbm(t * 2.3, 24) - 16.0 * g), math.radians(4.0 * fbm(t * 2.1, 25) + 6.0 * g), 0.0)
    lean = Euler(fl.rotation_euler).to_matrix() @ Vector((0, 0, 0.011))
    st['candle'].location = st['flame_base'] + lean


def head_angles(st, t):
    y0, p0 = st['yaw_nib'], st['pitch_nib']
    yw, pw = st['yaw_win'], st['pitch_win']
    yd, pd = y0 - 3.5, p0 - 4.0                       # anticipation: small dip + counter-turn
    yo, po, ro = yw + 3.5, pw + 2.0, -4.0             # overshoot
    if t < T_DIP: y, p, r = y0, p0, 0.0
    elif t < T_TURN:
        k = smooth(T_DIP, T_TURN, t); y, p, r = lerp(y0, yd, k), lerp(p0, pd, k), 0.0
    elif t < T_TURN_END:
        k = smoother(T_TURN, T_TURN_END, t); y, p, r = lerp(yd, yo, k), lerp(pd, po, k), lerp(0.0, ro, k)
    else:
        k = ease_out(T_TURN_END, T_SETTLE, t, 2.2); y, p, r = lerp(yo, yw, k), lerp(po, pw, k), lerp(ro, -1.5, k)
    p += 0.35 * fbm(t * 0.7, 61); y += 0.3 * fbm(t * 0.6, 62)
    return y, p, r


def pose_figure(st, t):
    y, p, r = head_angles(st, t)
    st['neck'].rotation_euler = Euler((math.radians(p), math.radians(r), math.radians(y)), 'XYZ')
    breath = math.sin(2 * math.pi * t / 3.7 + 0.8)
    follow = 2.2 * smoother(T_TURN + 3 / FPS, T_SETTLE + 4 / FPS, t)        # torso follows 2 deg, 3 f late
    tor = st['torso']
    tor.rotation_euler = (0.0, 0.0, math.radians(follow)); tor.scale = (1.0 + 0.003 * breath, 1.0 + 0.004 * breath, 1.0 + 0.0035 * breath)
    bpy.context.view_layer.update()
    Mt = tor.matrix_world
    shr, elr, shl, ell = (Mt @ st[k] for k in ('sh_r', 'el_r', 'sh_l', 'el_l'))
    wr_r = st['rig'].matrix_world @ Vector((0.020, -0.034, 0.182))
    place_between(st['sl_ru'], shr, elr); place_between(st['sl_rf'], elr, wr_r)
    place_between(st['sl_lu'], shl, ell); place_between(st['sl_lf'], ell, st['wr_l'])


def lane_point(st, s, lat, h):
    return st['ML'] @ Vector((lat, s, h))


def pose_torches(st, t):
    grow = 0.30 + 0.70 * smooth(2.4, 6.0, t)            # more torches catch / the mob closes in
    for (td, lo, tfl, pole, bear) in st['torches']:
        s = td['s0'] - TORCH_SPEED * t
        step = 2 * math.pi * 1.9 * t + td['ph']
        lat = td['lat'] + 0.05 * math.sin(step * 0.5)
        P = lane_point(st, s, lat, td['h'] + 0.035 * abs(math.sin(step)))
        fl = 1.0 + 0.20 * fbm(t * 7.0, td['seed']) + 0.08 * fbm(t * 19.0, td['seed'] + 5)
        lo.data.energy = E_TORCH * td['e'] * fl * grow
        lo.location = P + Vector((0, 0, 0.10))
        tfl.location = P - Vector((0, 0, 0.04))
        tfl.scale = (1.0 + 0.10 * fbm(t * 8.0, td['seed'] + 9), 1.0, 1.0 + 0.18 * fbm(t * 9.0, td['seed'] + 3))
        tfl.rotation_euler = (math.radians(10 * fbm(t * 3.0, td['seed'] + 7)), math.radians(14 * fbm(t * 2.6, td['seed'] + 8)), 0.0)
        pole.location = P - Vector((0, 0, 0.72)); pole.rotation_euler = (math.radians(6.0), math.radians(-8.0), 0.0)
        bear.location = lane_point(st, s + 0.25, lat - 0.28, 0.0) + Vector((0, 0, -0.15 + 0.03 * abs(math.sin(step))))
        bear.rotation_euler = (0.0, 0.0, LANE_ANG + math.pi)


def pose_window(st, t):
    w = st['win']; d = t - T_RATTLE
    a = 0.0 if d < 0 else 0.45 * math.exp(-d * 9.0) * math.sin(2 * math.pi * 23.0 * d)
    w.rotation_euler = (math.radians(a), math.radians(0.3 * a), 0.0)


def pose_camera(st, shot, t):
    cam = st['cam']; cd = cam.data
    if shot == 0:
        cam.location = st['C1']; cam.rotation_quaternion = st['Q1']
        cd.lens = 85.0; cd.dof.aperture_fstop = 2.0
        F = -(st['Q1'].to_matrix().col[2])
        d_nib = (st['nib_now'] - st['C1']).dot(F); d_fl = (st['flame_pt'] - st['C1']).dot(F)
        k = smoother(T_RACK0, T_RACK1, t)
        cd.dof.focus_distance = 1.0 / lerp(1.0 / d_nib, 1.0 / d_fl, k)       # rack in diopters
    else:
        k = smoother(T_CUT, T_PUSH_END, t)
        C = st['C2a'].lerp(st['C2b'], k)
        cam.location = C; cam.rotation_quaternion = st['Q2']
        cd.lens = 35.0; cd.dof.aperture_fstop = 4.0
        F = -(st['Q2'].to_matrix().col[2])
        cd.dof.focus_distance = (st['head_w'] - C).dot(F)


def frame(bpy_, ctx, st, i, t):
    tl = ctx.get('timeline')
    shot = tl.at(t)['i'] if tl else (0 if t < T_CUT else 1)
    pose_writing(st, t)
    pose_candle(st, t)
    pose_figure(st, t)
    pose_torches(st, t)
    pose_window(st, t)
    pose_camera(st, shot, t)
    for f in st['fogs']: f.hide_render = (shot == 0)     # the ECU gains nothing from the fog; S2 needs it
