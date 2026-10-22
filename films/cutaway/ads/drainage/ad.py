"""Drainage sample ad (Cutaway style): the shared scene for both deliveries (v916/blender.py, v169/blender.py).

Invented business, marked Sample on screen: "Fieldstone Drainage and Landscaping". No phone, no website.
15 s, four beats (brief.md):
  0.0 to 3.0   a backyard block after rain, a puddle on the lawn; the cut face shows water trapped above heavy grey clay
  3.0 to 6.5   slow push to the cut face: the water sits on the clay and has nowhere to go
  6.5 to 11.5  the fix as a time-lapse: a trench opens along the yard, gravel pours, a perforated pipe settles, gravel and
               soil close, the turf returns; the water in the soil draws down into the pipe and runs out of its mouth
  11.5 to 15.0 sun, the lawn dry and green; end card (sample name, Sample, Your logo here, Book a yard check)

Words are set in code as camera-parented text (Inter Tight, OFL, static weights in ../fonts), one face, a soft shadow;
every word sits inside the social safe box R-2-08 of the 9:16 frame (x 0.11 to 0.78, y 0.15 to 0.65): build() checks it
and fails the render if any word leaves the box. Free: Blender bpy 5.2 Cycles CPU, everything procedural.

The Cutaway kit (films/styles/cutaway/cutaway.py) is imported, never edited: what the ad needs beyond it (the yard
strata with the perched water, the trench, gravel, pipe, spout, fence, shrubs, patio, words) is built here.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../../../..'))
sys.path.insert(0, os.path.join(ROOT, 'films/styles/cutaway'))
import cutaway as cw  # noqa: E402

DURATION = 15.0
SETTINGS = {'samples': 48, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.2, 'max_bounces': 8, 'clamp_indirect': 6.0, 'adaptive_min_samples': 16, 'denoising_prefilter': 'ACCURATE'}

# ------------------------------------------------------------------------------------------------ the words (set in code)
WORDS = [  # (key, text, start, end)
    ('w1', 'Soggy lawn\nafter every rain?', 0.30, 2.80),
    ('w2', 'The problem is\nunder the grass.', 3.15, 6.25),
    ('w3', 'We fix what\nyou can’t see.', 6.75, 11.20),
]
CARD_IN = 12.25                     # the end card lands after the sunny lawn has been seen for a beat
NAME = 'Fieldstone Drainage\nand Landscaping'
CTA = 'Book a yard check'
SAFE_916 = (0.11, 0.78, 0.15, 0.65)  # R-2-08: x0, x1, y0, y1 as fractions of the 9:16 frame (y from the top)
SAFE_169 = (0.05, 0.95, 0.06, 0.90)  # title-safe for the 16:9 delivery

# ------------------------------------------------------------------------------------------------ the yard
SX = SY = 3.0
DEPTH = 1.0
RES = 0.022
# strata top-down: (name, thickness m, sRGB, pebble density); clay top sits 0.22 m below the lawn
STRATA = [('turf', 0.05, (0.20, 0.14, 0.09), 0.02), ('topsoil', 0.07, (0.31, 0.22, 0.14), 0.08),
          ('loam', 0.10, (0.47, 0.35, 0.23), 0.18), ('clay', 0.34, (0.55, 0.55, 0.54), 0.01),
          ('clay2', 0.16, (0.46, 0.47, 0.48), 0.03), ('deep', 1.0, (0.40, 0.34, 0.28), 0.25)]
CLAY_S = 0.22                         # strata coordinate of the clay top
H0 = 0.075                            # perched water above the clay at the start (m)
LAWN = 0.04                           # lawn height
PUD_C = (0.05, 0.28)                  # puddle centre and radii (a shallow bowl in the lawn)
PUD_R = (0.56, 0.34)
PUD_D = 0.034                         # bowl depth
PUD_LEVEL = LAWN - PUD_D * 0.42       # water level in the bowl
Y0 = -0.32                            # trench centre line (runs along x, from X_START to the +X cut face)
TW = 0.20                             # trench width
X_START = -0.95
DTR = 0.40                            # trench floor depth (below z = 0)
BED = 0.06                            # gravel bed under the pipe
PR = 0.046                            # pipe radius
COVER_Z = -0.12                       # top of the gravel cover
PATIO = (-SX / 2, -0.80, -SY / 2, -0.86)   # x0, x1, y0, y1

# ------------------------------------------------------------------------------------------------ timeline (s)
T_OPEN = (6.55, 7.60)
T_BED = (7.45, 8.05)
T_PIPE = (7.95, 8.55)
T_COVER = (8.50, 9.10)
T_BACK = (9.05, 9.60)
T_TURF = (9.50, 10.05)
T_DRAIN = (9.00, 11.30)
T_PUDDLE = (9.35, 11.05)
T_SUN = (11.00, 12.10)

def ramp(t, ab):
    a, b = ab; return min(1.0, max(0.0, (t - a) / (b - a)))

def ease(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)

def ease_out(u):
    u = min(1.0, max(0.0, u)); return 1 - (1 - u) ** 3

def lerp(a, b, u):
    return a + (b - a) * u

def lerp3(a, b, u):
    return tuple(lerp(x, y, u) for x, y in zip(a, b))

# ================================================================================================ terrain
def top_fn(x, y):
    """Lawn: nearly flat with a soft low bowl where the rain collects."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    h = LAWN + 0.010 * cw.fbm(x, y, 21, 3, 0.45)
    q = np.hypot((x - PUD_C[0]) / PUD_R[0], (y - PUD_C[1]) / PUD_R[1])
    q = q * (1 + 0.10 * np.sin(3 * np.arctan2(y - PUD_C[1], x - PUD_C[0]) + 1.3))
    return h - PUD_D * cw.smooth(1.0, 0.15, q)

def zones(x, y, h):
    x = np.asarray(x, float); y = np.asarray(y, float)
    bed = np.maximum(cw.smooth(-SX / 2 + 0.34, -SX / 2 + 0.28, x) * (y > -0.70), cw.smooth(SY / 2 - 0.34, SY / 2 - 0.28, y))
    pat = ((x < PATIO[1] + 0.02) & (y < PATIO[3] + 0.02)).astype(float)
    return {'path': np.maximum(bed, pat)}

# ================================================================================================ materials made here
def mat_yard_strata(kit, layers, V):
    """The kit's strata look (bands along 'sd', wobble, grain, pebbles, roots, dark band under the turf) plus the perched
    water: a turquoise wet band sitting on the clay top whose height falls as the drain works (drawdown toward the trench,
    flow streaks moving into it), and an overall wetness. V collects the driven value sockets."""
    G = cw.G; m = cw._new_mat(kit.bpy, 'yard_strata'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    sd = g.attr('sd').outputs['Fac']; dtop = g.attr('dtop').outputs['Fac']
    hz = g.math('ADD', sx[0], sx[1])
    wob = g.noise(g.comb(hz, 0.0, g.math('MULTIPLY', sd, 0.2)), 2.2, 3.0)
    s = g.math('ADD', sd, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.05))
    total = sum(l[1] for l in layers[:-1]) + 0.6; stops = []; pstops = []; acc = 0.0; soft = 0.010
    for k, l in enumerate(layers):
        a = acc / total; b = min(1.0, (acc + l[1]) / total) if k < len(layers) - 1 else 1.0
        stops += [(min(1, a + soft / total) if k else 0.0, l[2]), (max(0.0, b - soft / total) if k < len(layers) - 1 else 1.0, tuple(c * 0.9 for c in l[2]))]
        pstops += [(a, (l[3],) * 3)]; acc += l[1]
    fac = g.math('DIVIDE', s, total)
    col = g.ramp(fac, stops); pden = g.sep(g.ramp(fac, pstops, 'CONSTANT'))[0]
    n1 = g.noise(pos, 60.0, 5.0, 0.6); n2 = g.noise(g.comb(hz, g.math('MULTIPLY', sx[2], 6.0), 0.0), 3.0, 4.0)
    col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], 0.40), col, g.mix(0.55, col, (0, 0, 0), 'MULTIPLY'))
    col = g.mix(g.math('MULTIPLY', n2.outputs['Fac'], 0.22), col, g.mix(0.5, col, (1, 1, 1), 'SCREEN'))
    # clay: smooth, dense, faint horizontal laminations (heavy grey clay reads as one mass)
    inclay = g.math('MULTIPLY', g.math('SUBTRACT', s, CLAY_S), 200.0, clamp=True)
    lam = g.noise(g.comb(g.math('MULTIPLY', hz, 0.6), g.math('MULTIPLY', sx[2], 40.0), 0.0), 2.0, 2.0)
    col = g.mix(g.math('MULTIPLY', inclay, g.math('MULTIPLY', lam.outputs['Fac'], 0.25)), col, g.mix(0.5, col, (1, 1, 1), 'SCREEN'))
    vp = g.voronoi(pos, 34.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    radius = g.math('MULTIPLY', g.math('MULTIPLY', pden, 0.42), g.math('MULTIPLY_ADD', rr[0], 0.8, 0.4))
    peb = g.math('MULTIPLY', g.math('SUBTRACT', radius, vp.outputs['Distance']), 25.0, clamp=True)
    pcol = g.mix(rr[1], cw.srgb((0.42, 0.40, 0.37)), cw.srgb((0.78, 0.74, 0.66)))
    col = g.mix(peb, col, pcol)
    u = g.math('ADD', g.math('MULTIPLY', hz, 22.0), g.math('MULTIPLY', g.noise(g.comb(hz, sx[2], 0.0), 6.0, 2.0).outputs['Fac'], 3.0))
    lane = g.math('FLOOR', u); fr = g.math('FRACT', u)
    wn = g.node('ShaderNodeTexWhiteNoise', noise_dimensions='1D'); g.put(wn, 'W', lane)
    rlen = g.math('MULTIPLY', wn.outputs['Value'], 0.16)
    line = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', fr, 0.5)), 16.0), clamp=True)
    taper = g.math('MULTIPLY', g.math('SUBTRACT', rlen, dtop), 20.0, clamp=True)
    root = g.math('MULTIPLY', g.math('MULTIPLY', line, taper), g.math('GREATER_THAN', wn.outputs['Value'], 0.35))
    col = g.mix(g.math('MULTIPLY', root, 0.85), col, cw.srgb((0.12, 0.08, 0.05)))
    top_dark = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', dtop, 30.0), clamp=True)
    col = g.mix(g.math('MULTIPLY', top_dark, 0.45), col, cw.srgb((0.14, 0.10, 0.06)))
    # ---- the perched water on the clay
    P = g.value(0.0, 'drain'); WET = g.value(1.0, 'wet'); TM = g.value(0.0, 'time'); FLOWV = g.value(0.0, 'flow')
    V.update(drain=P, wet=WET, time=TM, flow=FLOWV)
    dx = g.math('MAXIMUM', g.math('SUBTRACT', X_START, sx[0]), 0.0)
    dy = g.math('MAXIMUM', g.math('SUBTRACT', g.math('ABSOLUTE', g.math('SUBTRACT', sx[1], Y0)), TW / 2), 0.0)
    d = g.math('SQRT', g.math('ADD', g.math('MULTIPLY', dx, dx), g.math('MULTIPLY', dy, dy)))
    DM, WW = 3.8, 0.9
    f = g.math('DIVIDE', g.math('SUBTRACT', g.math('MULTIPLY', P, DM + WW), d), WW)
    f = g.math('MINIMUM', g.math('MAXIMUM', f, 0.0), 1.0)
    hw = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', f, f)), H0)     # drawdown: a curved water table
    stop = g.math('SUBTRACT', CLAY_S, hw)
    above_clay = g.math('MULTIPLY', g.math('SUBTRACT', CLAY_S + 0.003, s), 400.0, clamp=True)
    inb = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', s, stop), 400.0, clamp=True), above_clay)
    inb = g.math('MULTIPLY', inb, g.math('MULTIPLY', hw, 300.0, clamp=True))
    # flow streaks: noise sliding toward the trench while it drains
    cs = g.math('SUBTRACT', d, g.math('MULTIPLY', TM, 0.35))
    st = g.noise(g.comb(g.math('MULTIPLY', cs, 9.0), g.math('MULTIPLY', sx[2], 55.0), 0.0), 1.0, 3.0, 0.6)
    streak = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.45), 3.0, clamp=True), FLOWV)
    wcol = g.mix(0.62, col, cw.srgb((0.20, 0.55, 0.68)), 'MIX')
    wcol = g.mix(g.math('MULTIPLY', streak, 0.6), wcol, cw.srgb((0.62, 0.86, 0.94)))
    menisc = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', s, stop)), 500.0), clamp=True),
                    g.math('MULTIPLY', hw, 200.0, clamp=True))
    col = g.mix(inb, col, wcol)
    col = g.mix(g.math('MULTIPLY', menisc, 0.7), col, cw.srgb((0.78, 0.94, 1.0)))
    # wet soil above the water (dark after rain, drying in the sun)
    dark = g.math('MULTIPLY', g.math('MULTIPLY', WET, 0.38), g.math('SUBTRACT', 1.0, inclay))
    col = g.mix(dark, col, g.mix(1.0, col, cw.srgb((0.55, 0.52, 0.50)), 'MULTIPLY'))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col})
    g.put(p, 'Roughness', g.math('SUBTRACT', 0.92, g.math('ADD', g.math('MULTIPLY', inb, 0.75), g.math('MULTIPLY', dark, 0.4))))
    h = g.math('ADD', g.math('MULTIPLY', n1.outputs['Fac'], 0.3), g.math('ADD', g.math('MULTIPLY', peb, 0.8), g.math('MULTIPLY', root, 0.4)))
    h = g.math('MULTIPLY', h, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', inb, 0.8)))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.45, 'Height': h, 'Distance': 0.006}); g.put(p, 'Normal', b)
    cw._finish(g, p); return m

def mat_gravel(kit, V):
    """Clean drainage stone: rounded grey-beige pebbles with dark gaps; darker and bluish when water runs through."""
    m = cw._new_mat(kit.bpy, 'gravel'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    vo = g.voronoi(pos, 55.0, 'F1'); ve = g.voronoi(pos, 55.0, 'DISTANCE_TO_EDGE')
    rr = g.sep(vo.outputs['Color'])
    c = g.mix(rr[0], cw.srgb((0.50, 0.49, 0.46)), cw.srgb((0.80, 0.78, 0.72)))
    c = g.mix(g.math('MULTIPLY', rr[1], 0.5), c, cw.srgb((0.66, 0.58, 0.48)))
    gap = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', ve.outputs['Distance'], 14.0), clamp=True)
    c = g.mix(gap, c, cw.srgb((0.10, 0.09, 0.08)))
    WG = g.value(0.0, 'gravel_wet'); V['gravel_wet'] = WG
    low = g.math('MULTIPLY', g.math('SUBTRACT', -DTR + 0.16, sx[2]), 18.0, clamp=True)     # water collects low, around the pipe
    wv = g.math('MULTIPLY', WG, g.math('ADD', 0.35, g.math('MULTIPLY', low, 0.65)))
    c = g.mix(wv, c, g.mix(0.55, g.mix(1.0, c, cw.srgb((0.45, 0.62, 0.72)), 'MULTIPLY'), cw.srgb((0.20, 0.52, 0.64))))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': c})
    g.put(p, 'Roughness', g.math('SUBTRACT', 0.75, g.math('MULTIPLY', wv, 0.6)))
    hb = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 2.2), clamp=True)
    b = g.node('ShaderNodeBump', ins={'Strength': 0.8, 'Height': hb, 'Distance': 0.01}); g.put(p, 'Normal', b)
    cw._finish(g, p); return m

def mat_backfill(kit):
    m = cw._new_mat(kit.bpy, 'backfill'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    n = g.noise(pos, 40.0, 5.0, 0.6); n2 = g.noise(pos, 7.0, 3.0)
    c = g.mix(n2.outputs['Fac'], cw.srgb((0.30, 0.21, 0.13)), cw.srgb((0.44, 0.32, 0.21)))
    c = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.5), c, g.mix(0.6, c, (0, 0, 0), 'MULTIPLY'))
    turf = g.math('MULTIPLY', g.math('SUBTRACT', sx[2], LAWN - 0.035), 60.0, clamp=True)
    c = g.mix(g.math('MULTIPLY', turf, 0.7), c, cw.srgb((0.14, 0.10, 0.06)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': c, 'Roughness': 0.92})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.5, 'Height': n.outputs['Fac'], 'Distance': 0.006}); g.put(p, 'Normal', b)
    cw._finish(g, p); return m

def mat_pipe(kit):
    """Pale perforated drain pipe: rows of dark slots around it (pipe-local coordinates: axis along x)."""
    m = cw._new_mat(kit.bpy, 'pipe'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    ang = g.node('ShaderNodeMath', operation='ARCTAN2'); g.put(ang, 0, sx[2]); g.put(ang, 1, sx[1])
    v = g.math('MULTIPLY', ang.outputs[0], 6 / (2 * math.pi))
    uu = g.math('MULTIPLY', sx[0], 1 / 0.06)
    fu = g.math('SUBTRACT', g.math('FRACT', uu), 0.5); fv = g.math('SUBTRACT', g.math('FRACT', g.math('ADD', v, g.math('MULTIPLY', g.math('FLOOR', uu), 0.5))), 0.5)
    dd = g.math('SQRT', g.math('ADD', g.math('MULTIPLY', g.math('MULTIPLY', fu, fu), 1.0), g.math('MULTIPLY', g.math('MULTIPLY', fv, fv), 5.0)))
    hole = g.math('MULTIPLY', g.math('SUBTRACT', 0.24, dd), 60.0, clamp=True)
    rib = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('ABSOLUTE', g.math('SUBTRACT', g.math('FRACT', g.math('MULTIPLY', sx[0], 1 / 0.012)), 0.5))), 1.0)
    c = g.mix(g.math('MULTIPLY', rib, 0.15), cw.srgb((0.84, 0.84, 0.80)), cw.srgb((0.93, 0.93, 0.90)))
    r = g.vmath('LENGTH', g.comb(0.0, sx[1], sx[2]))
    outer = g.math('GREATER_THAN', r, PR * 0.93)
    c = g.mix(g.math('MULTIPLY', hole, outer), c, cw.srgb((0.06, 0.06, 0.06)))
    c = g.mix(g.math('SUBTRACT', 1.0, outer), c, cw.srgb((0.10, 0.10, 0.10)))       # inside the pipe: dark
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': c, 'Roughness': 0.38})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.25, 'Height': rib, 'Distance': 0.003}); g.put(p, 'Normal', b)
    cw._finish(g, p); return m

def mat_flow(kit, V, name='pipe_water', glass=False):
    """Water moving in the pipe and out of its mouth: clear turquoise with streaks sliding along +x; the spout fades out
    toward its tip (attribute 'u' 0..1 along it)."""
    m = cw._new_mat(kit.bpy, name); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    TM = V.setdefault('time_' + name, g.value(0.0, 'time'))
    st = g.noise(g.comb(g.math('MULTIPLY', g.math('SUBTRACT', sx[0], g.math('MULTIPLY', TM, 0.9)), 14.0), g.math('MULTIPLY', sx[1], 40.0), g.math('MULTIPLY', sx[2], 40.0)), 1.0, 3.0, 0.6)
    s = g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.5), 3.0, clamp=True)
    c = g.mix(s, cw.srgb((0.14, 0.50, 0.62)), cw.srgb((0.70, 0.90, 0.96)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': c, 'Roughness': 0.06})
    g.put(p, 'Emission Color', c); g.put(p, 'Emission Strength', 0.15)
    b = g.node('ShaderNodeBump', ins={'Strength': 0.3, 'Height': st.outputs['Fac'], 'Distance': 0.004}); g.put(p, 'Normal', b)
    sh = p
    if glass:
        gl = g.node('ShaderNodeBsdfGlass', ins={'Color': cw.srgb((0.80, 0.95, 0.98)), 'Roughness': 0.02, 'IOR': 1.33})
        g.put(gl, 'Normal', b)
        mx = g.node('ShaderNodeMixShader'); g.put(mx, 0, 0.55); g.link(p, mx.inputs[1]); g.link(gl, mx.inputs[2]); sh = mx
        u = g.attr('u').outputs['Fac']; fade = g.math('MULTIPLY', g.math('SUBTRACT', u, 0.55), 2.3, clamp=True)
        tr = g.node('ShaderNodeBsdfTransparent'); m2 = g.node('ShaderNodeMixShader')
        g.link(fade, m2.inputs[0]); g.link(sh, m2.inputs[1]); g.link(tr, m2.inputs[2]); sh = m2
    cw._finish(g, sh); return m

def mat_text(kit, name, color, strength, alpha_sock_store):
    """Camera-only flat colour with an opacity: emission mixed with transparent (black colour = a shadow layer)."""
    m = cw._new_mat(kit.bpy, name); g = cw.G(m.node_tree, kit)
    A = g.value(0.0, 'alpha'); alpha_sock_store.append(A)
    e = g.node('ShaderNodeEmission', ins={'Color': cw.srgb(color), 'Strength': strength})
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(A, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2])
    cw._finish(g, mx); return m

def patch_top_material(mat):
    """The kit's top shader: turn its pale 'path' colour into dark garden mulch (shrub beds, under the patio)."""
    target = cw.srgb((0.52, 0.42, 0.30))
    for n in mat.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeMix' and getattr(n, 'data_type', '') == 'RGBA':
            s = n.inputs.get('B_Color') if hasattr(n.inputs, 'get') else None
            if s is None:
                s = next((x for x in n.inputs if x.identifier == 'B_Color'), None)
            if s is not None and not s.is_linked and all(abs(a - b) < 1e-3 for a, b in zip(s.default_value[:3], target[:3])):
                s.default_value = cw.srgb((0.17, 0.11, 0.07)); return True
    print('note: path colour node not found in the top material (kit changed?); mulch keeps the kit colour', flush=True)
    return False

# ================================================================================================ geometry made here
def mesh_parts(me):
    nv = len(me.vertices); co = np.zeros(nv * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    np_ = len(me.polygons); ls = np.zeros(np_, np.int64); lt = np.zeros(np_, np.int64); mi = np.zeros(np_, np.int64)
    me.polygons.foreach_get('loop_start', ls); me.polygons.foreach_get('loop_total', lt); me.polygons.foreach_get('material_index', mi)
    lv = np.zeros(len(me.loops), np.int64); me.loops.foreach_get('vertex_index', lv)
    faces = [lv[a:a + n] for a, n in zip(ls, lt)]
    attrs = {}
    for at in me.attributes:
        if at.domain == 'POINT' and at.data_type == 'FLOAT' and not at.name.startswith('.') and at.name != 'position':
            a = np.zeros(nv); at.data.foreach_get('value', a); attrs[at.name] = a
    return co, faces, mi, attrs

def sub_mesh(bpy, name, co, faces, sel, mi, attrs, mats, coll, smooth_shade=True):
    idx = [i for i in range(len(faces)) if sel[i]]
    if not idx: return None
    used = np.unique(np.concatenate([faces[i] for i in idx])); remap = -np.ones(len(co), np.int64); remap[used] = np.arange(len(used))
    F = [tuple(remap[faces[i]]) for i in idx]
    at = {k: ('FLOAT', v[used]) for k, v in attrs.items()}
    return cw.mk_mesh(bpy, name, co[used], F, mats, [int(mi[i]) for i in idx], smooth_shade, coll, at)

def strata_attrs(h, z, zmean):
    dt = np.maximum(h - z, 0.0); w = np.maximum(0.0, 1 - dt / 0.7)
    return dt * w + (zmean - z) * (1 - w), dt

def grid_wall(xy0, xy1, ztop_fn, zbot, ncol, nrow, flip=False):
    """A vertical wall from point xy0 to xy1 (columns), from ztop(x, y) down to zbot (rows). Returns V, F."""
    V = []; F = []
    for c in range(ncol + 1):
        u = c / ncol; x = lerp(xy0[0], xy1[0], u); y = lerp(xy0[1], xy1[1], u); zt = float(ztop_fn(x, y))
        for r in range(nrow + 1):
            V.append((x, y, lerp(zt, zbot, r / nrow)))
    for c in range(ncol):
        for r in range(nrow):
            a = c * (nrow + 1) + r; b = (c + 1) * (nrow + 1) + r
            F.append((a, a + 1, b + 1, b) if not flip else (a, b, b + 1, a + 1))
    return V, F

class Prism:
    """A fill body in the trench: columns along x (xs), a cross-section from yA to yB with a flat bottom z0 and a lumpy
    top that set_top() moves per frame (gravel pouring, soil closing). The end cap at the last column sits on the cut face."""
    def __init__(self, kit, name, xs, yA, yB, z0, mat, ny=8, lump=0.0, seed=0):
        self.kit = kit; self.xs = np.asarray(xs, float); self.nx = len(xs); self.ny = ny; self.yA = yA; self.yB = yB; self.z0 = z0
        self.ys = np.linspace(yA, yB, ny); rng = np.random.default_rng(seed)
        self.lump = lump * rng.uniform(-1, 1, (self.nx, ny)); self.lump[:, 0] = 0; self.lump[:, -1] = 0
        M = ny + 2; V = []; F = []
        for i, x in enumerate(self.xs):
            V.append((x, yA, z0))
            for y in self.ys: V.append((x, y, z0 + 0.001))
            V.append((x, yB, z0))
        for i in range(self.nx - 1):
            for k in range(M):
                a = i * M + k; b = i * M + (k + 1) % M
                F.append((a, b, b + M, a + M))
        F.append(tuple(range(M)))                                     # start cap
        F.append(tuple((self.nx - 1) * M + k for k in range(M))[::-1])   # end cap (on the cut face)
        self.M = M; self.ob = cw.mk_mesh(kit.bpy, name, V, F, [mat], None, False, kit.coll)
        self.co = np.array(V, float)
    def set_top(self, ztop):
        """ztop: array (nx, ny) of top heights."""
        z = np.maximum(np.asarray(ztop, float) + self.lump, self.z0 + 0.0008)
        co = self.co.reshape(self.nx, self.M, 3).copy(); co[:, 1:-1, 2] = z
        self.ob.data.vertices.foreach_set('co', co.ravel()); self.ob.data.update()

def build_pipe_mesh(bpy, name, length, r, ri, mat, coll, ring=28):
    """A hollow pipe along +x from 0 to length (pipe-local), with annular ends."""
    V = []; F = []
    xs = np.linspace(0, length, max(2, int(length / 0.03)))
    for x in xs:
        for j in range(ring):
            a = 2 * math.pi * j / ring; V.append((x, r * math.cos(a), r * math.sin(a)))
    for x in xs:
        for j in range(ring):
            a = 2 * math.pi * j / ring; V.append((x, ri * math.cos(a), ri * math.sin(a)))
    n = len(xs); off = n * ring
    for i in range(n - 1):
        for j in range(ring):
            a = i * ring + j; b = i * ring + (j + 1) % ring
            F.append((a, b, b + ring, a + ring))
            F.append((off + a, off + a + ring, off + b + ring, off + b))
    for i, sgn in ((0, -1), (n - 1, 1)):
        for j in range(ring):
            a = i * ring + j; b = i * ring + (j + 1) % ring
            f = (a, b, off + b, off + a); F.append(f if sgn > 0 else f[::-1])
    return cw.mk_mesh(bpy, name, V, F, [mat], None, True, coll)

def segment_section(ri, depth, n=14):
    """Cross-section (y, z) of water lying in a pipe of inner radius ri, `depth` deep from the bottom: the lower arc of the
    circle from one end of the surface chord to the other (angles from +y; the bottom is at 270 degrees)."""
    depth = max(1e-4, min(depth, 2 * ri - 1e-4)); ts = math.asin(max(-1.0, min(1.0, (depth - ri) / ri)))
    return [(ri * math.cos(a), ri * math.sin(a)) for a in np.linspace(math.pi - ts, 2 * math.pi + ts, n)]

class PipeWater:
    def __init__(self, kit, name, length, ri, mat, n=14):
        self.n = n; self.length = length; self.ri = ri
        V = [(0, 0, 0)] * (2 * n); F = [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
        for j in range(n):
            k = (j + 1) % n; F.append((j, k, n + k, n + j))
        self.ob = cw.mk_mesh(kit.bpy, name, V, F, [mat], None, False, kit.coll)
    def set_depth(self, depth):
        sec = segment_section(self.ri * 0.985, depth, self.n)
        V = [(0.0, y, z) for y, z in sec] + [(self.length, y, z) for y, z in sec]
        self.ob.data.vertices.foreach_set('co', np.array(V, float).ravel()); self.ob.data.update()

class Spout:
    """Water leaving the pipe mouth on the cut face: a tapering tube on a falling arc, 'u' 0..1 along it (fades out)."""
    def __init__(self, kit, name, origin, mat, nseg=26, ring=12):
        self.o = np.array(origin, float); self.nseg = nseg; self.ring = ring
        V = np.zeros(((nseg + 1) * ring, 3)); F = []
        for i in range(nseg):
            for j in range(ring):
                a = i * ring + j; b = i * ring + (j + 1) % ring; F.append((a, a + ring, b + ring, b))
        F.append(tuple(range(ring))); u = np.repeat(np.linspace(0, 1, nseg + 1), ring)
        self.ob = cw.mk_mesh(kit.bpy, name, V, F, [mat], None, True, kit.coll, {'u': ('FLOAT', u)})
    def set(self, length, radius):
        s = np.linspace(0, 1, self.nseg + 1) * max(length, 1e-3)
        P = np.stack([self.o[0] + 0.30 * s, np.full_like(s, self.o[1]), self.o[2] - 1.1 * s * s], 1)
        T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
        V = []
        for i in range(len(s)):
            N = np.cross(T[i], (0, 1, 0)); N /= np.linalg.norm(N) + 1e-9; B = np.cross(T[i], N)
            r = radius * (1 - 0.45 * s[i] / max(length, 1e-3)) * (0.85 if i == 0 else 1.0)
            for j in range(self.ring):
                a = 2 * math.pi * j / self.ring; V.append(P[i] + r * (math.cos(a) * N + 0.8 * math.sin(a) * B))
        self.ob.data.vertices.foreach_set('co', np.array(V, float).ravel()); self.ob.data.update()

def build_fence(kit, L):
    """A plain board fence along the two back edges (-X from the patio to the corner, +Y full length)."""
    A = cw._Acc(); h = 0.22; e = 0.03
    runs = [((-SX / 2 + e, -0.62), (-SX / 2 + e, SY / 2 - e)), ((-SX / 2 + e, SY / 2 - e), (SX / 2 - 0.012, SY / 2 - e))]
    for (x0, y0), (x1, y1) in runs:
        Lr = math.hypot(x1 - x0, y1 - y0); dxu, dyu = (x1 - x0) / Lr, (y1 - y0) / Lr; nx_, ny_ = -dyu, dxu
        k = 0; s = 0.0; bw = 0.052
        while s < Lr - 0.01:
            w = min(bw, Lr - s); xm = x0 + dxu * (s + w / 2); ym = y0 + dyu * (s + w / 2)
            zt = float(L.height(np.array([xm]), np.array([ym]))[0]); hh = h * (1 + 0.012 * ((k * 7) % 3))
            c = [(xm - dxu * w / 2 * 0.94, ym - dyu * w / 2 * 0.94), (xm + dxu * w / 2 * 0.94, ym + dyu * w / 2 * 0.94)]
            V = []
            for (px, py) in c:
                for t in (-0.009, 0.009): V.append((px + nx_ * t, py + ny_ * t))
            VV = [(v[0], v[1], zt - 0.03) for v in V] + [(v[0], v[1], zt + hh) for v in V]
            A.add(VV, [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6)], 0)
            s += bw; k += 1
        npost = max(2, int(Lr / 0.5) + 1)
        for q in range(npost):
            u = q / (npost - 1); xm = lerp(x0, x1, u); ym = lerp(y0, y1, u); zt = float(L.height(np.array([xm]), np.array([ym]))[0])
            px, py = xm - nx_ * 0.022, ym - ny_ * 0.022
            v, f = cw._box(px - 0.016, py - 0.016, zt - 0.03, px + 0.016, py + 0.016, zt + h + 0.018); A.add(v, f, 1)
        for zr in (0.05, 0.17):
            pts = []
            for u in np.linspace(0, 1, 2):
                xm = lerp(x0, x1, u); ym = lerp(y0, y1, u); pts.append((xm - nx_ * 0.016, ym - ny_ * 0.016))
            zt = LAWN + zr; (ax, ay), (bx, by) = pts
            V = [(ax - nx_ * 0.008, ay - ny_ * 0.008, zt), (ax + nx_ * 0.008, ay + ny_ * 0.008, zt), (bx + nx_ * 0.008, by + ny_ * 0.008, zt), (bx - nx_ * 0.008, by - ny_ * 0.008, zt)]
            V = V + [(p[0], p[1], p[2] + 0.024) for p in V]
            A.add(V, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], 1)
    wood = cw.mat_simple(kit, 'fence_wood', (0.56, 0.44, 0.33), 0.8, noise_amt=0.25, bump=0.25)
    post = cw.mat_simple(kit, 'fence_post', (0.42, 0.33, 0.25), 0.8, noise_amt=0.25, bump=0.25)
    return A.build(kit.bpy, 'fence', [wood, post], False, kit.coll)

def build_shrubs(kit, L):
    bpy = kit.bpy; V0, F0 = cw._icosphere(2); protos = []
    leaf = cw.mat_leaf(kit, 'shrub_leaf', [(0.15, 0.33, 0.11), (0.21, 0.40, 0.13), (0.12, 0.27, 0.10), (0.26, 0.44, 0.15)])
    bloom = cw.mat_leaf(kit, 'shrub_bloom', [(0.86, 0.84, 0.90), (0.80, 0.62, 0.78), (0.92, 0.90, 0.86), (0.70, 0.74, 0.92)])
    for k in range(5):
        rng = np.random.default_rng(40 + k); A = cw._Acc()
        for b in range(int(rng.integers(7, 11))):
            r = rng.uniform(0.045, 0.07); c = np.array([rng.normal(0, 0.05), rng.normal(0, 0.05), rng.uniform(0.04, 0.12)])
            Vb = cw._lumpy(V0, 50 + k * 13 + b, 0.25, 3.0, 0.1, 8.0) * np.array([r, r, r * 0.85]) + c; A.add(Vb, F0, 0)
        if k >= 3:
            for b in range(9):
                c = np.array([rng.normal(0, 0.06), rng.normal(0, 0.06), rng.uniform(0.10, 0.17)]); r = rng.uniform(0.012, 0.018)
                A.add(cw._lumpy(V0, 90 + b, 0.2, 3, 0.05, 6) * r + c, F0, 1)
        protos.append(A.build(bpy, f'shrub{k}', [leaf, bloom], True, None))
    pts = []; rng = np.random.default_rng(5)
    for y in np.arange(-0.48, SY / 2 - 0.30, 0.25): pts.append((-SX / 2 + 0.17 + rng.normal(0, 0.02), y + rng.normal(0, 0.03)))
    for x in np.arange(-SX / 2 + 0.17, SX / 2 - 0.12, 0.25): pts.append((x + rng.normal(0, 0.03), SY / 2 - 0.17 + rng.normal(0, 0.02)))
    pts = np.array(pts)
    return cw.scatter(kit, L, 'shrubs', protos, pts, scale=rng.uniform(0.85, 1.25, len(pts)), sway=0.03, speed=0.6, sink=0.01)

def build_patio(kit, L):
    A = cw._Acc(); x0, x1, y0, y1 = PATIO; s = 0.235; j = 0.008; zt = LAWN + 0.028; zb = LAWN - 0.012
    xs = np.arange(x0, x1, s); ys = np.arange(y0, y1, s); k = 0
    for xa in xs:
        for ya in ys:
            xb = min(xa + s - j, x1); yb = min(ya + s - j, y1); xa2 = xa if xa <= x0 + 1e-6 else xa; ya2 = ya
            v, f = cw._box(xa2 + (0.0 if xa <= x0 + 1e-6 else 0.0), ya2, zb, xb, yb, zt + 0.003 * ((k * 5) % 3)); A.add(v, f, k % 2); k += 1
    m1 = cw.mat_simple(kit, 'paver_a', (0.72, 0.70, 0.66), 0.8, noise_amt=0.10, bump=0.25)
    m2 = cw.mat_simple(kit, 'paver_b', (0.66, 0.64, 0.60), 0.8, noise_amt=0.10, bump=0.25)
    ob = A.build(kit.bpy, 'patio', [m1, m2], False, kit.coll)
    # a planter on the patio
    V0, F0 = cw._icosphere(2); B = cw._Acc()
    pv, pf = cw._tube([(0, 0, 0), (0, 0, 0.07)], [0.045, 0.055], 20); B.add(pv, pf, 0)
    for b in range(7):
        rng = np.random.default_rng(70 + b); c = np.array([rng.normal(0, 0.025), rng.normal(0, 0.025), rng.uniform(0.09, 0.14)])
        B.add(cw._lumpy(V0, 70 + b, 0.25, 3, 0.1, 8) * 0.035 + c, F0, 1)
    pot = B.build(kit.bpy, 'planter', [cw.mat_simple(kit, 'terracotta', (0.66, 0.36, 0.22), 0.7, noise_amt=0.1), kit.bpy.data.materials['shrub_leaf']], True, kit.coll)
    pot.location = (x0 + 0.20, y0 + 0.40, zt)
    return ob

# ================================================================================================ words
class Words:
    """Text placed in camera space (frame fractions), with a soft shadow, landing (fade and a small settle) and resting."""
    def __init__(self, kit, cam_ob, cd, W, H, fonts):
        self.kit = kit; self.cam = cam_ob; self.cd = cd; self.W = W; self.H = H; self.fonts = fonts; self.items = []
        self.dz = 0.30; big = 18.0 / cd.lens * self.dz
        self.hw, self.hh = (big, big * H / W) if W >= H else (big * W / H, big)
        self.big = big
    def to_local(self, fx, fy):
        return ((fx - 0.5) * 2 * self.hw + self.cd.shift_x * 2 * self.big, (0.5 - fy) * 2 * self.hh + self.cd.shift_y * 2 * self.big)
    def frac(self, lx, ly):
        return (lx - self.cd.shift_x * 2 * self.big) / (2 * self.hw) + 0.5, 0.5 - (ly - self.cd.shift_y * 2 * self.big) / (2 * self.hh)
    def _font_ob(self, name, body, font, size_frac, mat, z_off, align='LEFT', spacing=1.0, line=0.98):
        bpy = self.kit.bpy; cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.font = font
        cu.size = size_frac * 2 * self.hh; cu.align_x = align; cu.align_y = 'TOP'; cu.space_line = line; cu.space_character = spacing
        cu.resolution_u = 14; cu.fill_mode = 'BOTH'; cu.materials.append(mat)
        ob = bpy.data.objects.new(name, cu); self.kit.coll.objects.link(ob); ob.parent = self.cam
        for a in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter', 'visible_shadow'):
            setattr(ob, a, False)
        ob.location = (0, 0, -self.dz + z_off); return ob, cu
    def text(self, key, body, fx, fy, size, t_in, t_out, weight='bold', color=(1, 1, 1), shadow=True, align='LEFT', spacing=1.0,
             max_w=None, rise=0.010, line=0.98):
        font = self.fonts[weight]; alphas = []; mat = mat_text(self.kit, key + '_m', color, 10.0, alphas)
        ob, cu = self._font_ob(key, body, font, size, mat, 0.0, align, spacing, line)
        it = {'key': key, 'obs': [ob], 'mats': alphas, 'shadow_alpha': [], 'fx': fx, 'fy': fy, 't_in': t_in, 't_out': t_out, 'rise': rise,
              'size': size, 'align': align, 'max_w': max_w, 'body': body}
        if shadow:
            n = 5
            for k in range(n):
                sa = []; sm = mat_text(self.kit, f'{key}_s{k}_m', (0, 0, 0), 1.0, sa)
                so, scu = self._font_ob(f'{key}_s{k}', body, font, size, sm, -0.0004 - 0.0001 * k, align, spacing, line)
                scu.offset = 0.006 * cu.size * (k + 1) / n * 6
                it['obs'].append(so); it['shadow_alpha'].append((sa[0], 0.075))
        self.items.append(it); return it
    def panel(self, key, fx0, fy0, fx1, fy1, t_in, t_out, color, strength=1.0, radius=0.5, alpha=1.0):
        """A rounded rectangle (the call-to-action pill) behind words; corners: radius as a fraction of the height."""
        bpy = self.kit.bpy; alphas = []; mat = mat_text(self.kit, key + '_m', color, strength, alphas)
        (x0, y0), (x1, y1) = self.to_local(fx0, fy1), self.to_local(fx1, fy0)
        r = (y1 - y0) * radius; V = []
        for cx, cy, a0 in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
            for k in range(9):
                a = math.radians(a0 + 90 * k / 8); V.append((cx + r * math.cos(a), cy + r * math.sin(a), 0.0))
        me = bpy.data.meshes.new(key); me.from_pydata(V, [], [tuple(range(len(V)))]); me.materials.append(mat)
        ob = bpy.data.objects.new(key, me); self.kit.coll.objects.link(ob); ob.parent = self.cam
        for a in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter', 'visible_shadow'):
            setattr(ob, a, False)
        ob.location = (0, 0, -self.dz - 0.0006)
        it = {'key': key, 'obs': [ob], 'mats': alphas, 'shadow_alpha': [], 'fx': None, 'fy': None, 't_in': t_in, 't_out': t_out, 'rise': 0.010,
              'panel': True, 'alpha': alpha, 'box': (fx0, fy0, fx1, fy1)}
        self.items.append(it); return it
    def layout(self):
        """Place each text item; scale it down if it is wider than max_w (fraction of the width)."""
        bpy = self.kit.bpy; dg = bpy.context.evaluated_depsgraph_get(); dg.update()
        for it in self.items:
            if it.get('panel'): it['base'] = [tuple(o.location) for o in it['obs']]; continue
            ob = it['obs'][0]; bb = np.array([list(v) for v in ob.evaluated_get(dg).bound_box])
            w = (bb[:, 0].max() - bb[:, 0].min()) / (2 * self.hw)
            if it['max_w'] and w > it['max_w']:
                s = it['max_w'] / w
                for o in it['obs']: o.data.size *= s; o.data.offset *= s
            lx, ly = self.to_local(it['fx'], it['fy'])
            it['base'] = [(lx, ly, o.location.z) for o in it['obs']]
            for o, b in zip(it['obs'], it['base']): o.location = b
            sh = 0.06 * it['obs'][0].data.size
            for k, o in enumerate(it['obs'][1:]): o.location = (lx + sh * 0.35, ly - sh * 0.6, o.location.z); it['base'][k + 1] = tuple(o.location)
    def boxes(self):
        """Frame-fraction boxes (x0, x1, y0, y1) of every word item, for the safe-zone check."""
        bpy = self.kit.bpy; dg = bpy.context.evaluated_depsgraph_get(); dg.update(); out = []
        for it in self.items:
            ob = it['obs'][0]
            if it.get('panel'):
                fx0, fy0, fx1, fy1 = it['box']; out.append((it['key'], fx0, fx1, fy0, fy1)); continue
            bb = np.array([list(v) for v in ob.evaluated_get(dg).bound_box]); lx, ly = it['base'][0][:2]
            ax, ay = self.frac(lx + bb[:, 0].min(), ly + bb[:, 1].max()); bx, by = self.frac(lx + bb[:, 0].max(), ly + bb[:, 1].min())
            out.append((it['key'], ax, bx, ay, by))
        return out
    def update(self, t):
        for it in self.items:
            a_in = ease_out(ramp(t, (it['t_in'], it['t_in'] + 0.40))); a_out = 1 - ease(ramp(t, (it['t_out'], it['t_out'] + 0.30)))
            a = a_in * a_out * it.get('alpha', 1.0)
            for A in it['mats']: A.default_value = a
            for A, k in it['shadow_alpha']: A.default_value = a * k
            dy = (1 - ease_out(ramp(t, (it['t_in'], it['t_in'] + 0.55)))) * it['rise'] * 2 * self.hh
            hide = a <= 0.001
            for o, b in zip(it['obs'], it['base']):
                o.location = (b[0], b[1] - dy, b[2]); o.hide_render = hide

# ================================================================================================ build
def build(bpy, ctx, aspect):
    W, H = ctx['W'], ctx['H']; v = aspect == '9:16'
    kit = cw.Kit(bpy, seed=7, loop=0)
    land = cw.block(kit, size=(SX, SY), depth=DEPTH, strata=STRATA, seed=7, top=top_fn, water=None, zones=zones, res=RES,
                    grass=1.35, grass_height=0.72, trees=0, tree_kinds=('tall', 'round'), tree_spots=[(-0.62, 0.86, 1.05, 'round')],
                    boulders=0, flowers=0.0, under=False, sway=0.9)
    S = {'kit': kit, 'land': land, 'V': {}}
    sc = bpy.context.scene
    patch_top_material(land.mats['top'])
    # ---- the yard strata with perched water replaces the kit's strata on the walls
    ys_mat = mat_yard_strata(kit, STRATA, S['V'])
    walls = land.objects['walls']; walls.data.materials[0] = ys_mat
    # ---- grid lines (the kit's top grid) and the trench corridor on them
    nx = int(round(SX / RES)) + 1; xs = np.linspace(-SX / 2, SX / 2, nx); ys = np.linspace(-SY / 2, SY / 2, nx)
    jA = int(np.argmin(np.abs(ys - (Y0 - TW / 2)))); jB = int(np.argmin(np.abs(ys - (Y0 + TW / 2)))); iA = int(np.argmin(np.abs(xs - X_START)))
    yA, yB, xA, xB = float(ys[jA]), float(ys[jB]), float(xs[iA]), SX / 2
    S.update(yA=yA, yB=yB, xA=xA, xB=xB)
    hfn = lambda x, y: float(land.height(np.array([x]), np.array([y]))[0])
    # ---- top: split the corridor into chunks (they vanish as the trench opens and return with the turf)
    top = land.objects['top']; co, faces, mi, attrs = mesh_parts(top.data); zmean = float(co[:, 2].mean())
    cen = np.array([co[f].mean(0) for f in faces])
    corr = (cen[:, 1] > yA) & (cen[:, 1] < yB) & (cen[:, 0] > xA)
    NCH = 26; ch = np.clip(((cen[:, 0] - xA) / (xB - xA) * NCH).astype(int), 0, NCH - 1)
    tmat = list(top.data.materials)
    main = sub_mesh(bpy, 'yard_top', co, faces, ~corr, mi, attrs, tmat, kit.coll)
    chunks = []
    for k in range(NCH):
        o = sub_mesh(bpy, f'yard_top_c{k}', co, faces, corr & (ch == k), mi, attrs, tmat, kit.coll)
        chunks.append((o, xA + (k + 0.5) / NCH * (xB - xA)))
    kit.coll.objects.unlink(top); land.objects['top'] = main
    # grass: the corridor's tufts move to per-chunk objects
    gob = land.objects.get('cw_grass'); gchunks = []
    if gob is not None:
        me = gob.data; n = len(me.vertices); P = np.zeros(n * 3); me.vertices.foreach_get('co', P); P = P.reshape(-1, 3)
        A = {}
        for nm, kind in (('yaw', 'FLOAT'), ('scale', 'FLOAT'), ('sway', 'FLOAT'), ('variant', 'INT')):
            arr = np.zeros(n, np.float32 if kind == 'FLOAT' else np.int32); me.attributes[nm].data.foreach_get('value', arr); A[nm] = arr
        inside = (P[:, 1] > yA - 0.004) & (P[:, 1] < yB + 0.004) & (P[:, 0] > xA - 0.004)
        keep = ~inside
        nm2 = bpy.data.meshes.new('cw_grass_main'); nm2.from_pydata([tuple(p) for p in P[keep]], [], [])
        for nm, kind in (('yaw', 'FLOAT'), ('scale', 'FLOAT'), ('sway', 'FLOAT'), ('variant', 'INT')):
            at = nm2.attributes.new(nm, kind, 'POINT'); at.data.foreach_set('value', A[nm][keep].astype(np.float32 if kind == 'FLOAT' else np.int32))
        gob.data = nm2
        coll = bpy.data.collections.get('cw_grass_protos')
        cidx = np.clip(((P[:, 0] - xA) / (xB - xA) * NCH).astype(int), 0, NCH - 1)
        for k in range(NCH):
            sel = inside & (cidx == k)
            o = cw.scatter(kit, land, f'trench_grass{k}', coll, P[sel], yaw=A['yaw'][sel], scale=A['scale'][sel], sway=A['sway'][sel],
                           variant=A['variant'][sel], speed=0.9) if (sel.any() and coll is not None) else None
            gchunks.append((o, xA + (k + 0.5) / NCH * (xB - xA)))
    S['chunks'] = chunks; S['gchunks'] = gchunks
    # ---- walls: cut the trench column out of the +X face, replace it with a lower patch (always) and an upper patch
    wco, wfaces, wmi, wattrs = mesh_parts(walls.data)
    wcen = np.array([wco[f].mean(0) for f in wfaces])
    col_sel = (np.abs(wcen[:, 0] - SX / 2) < 1e-4) & (wcen[:, 1] > yA) & (wcen[:, 1] < yB)
    wmats = list(walls.data.materials)
    nw = sub_mesh(bpy, 'yard_walls', wco, wfaces, ~col_sel, wmi, wattrs, wmats, kit.coll, smooth_shade=False)
    kit.coll.objects.unlink(walls); land.objects['walls'] = nw
    ncol = jB - jA
    def wall_obj(name, ztop_fn, zbot, nrow):
        V, F = grid_wall((SX / 2, yA), (SX / 2, yB), ztop_fn, zbot, ncol, nrow)
        V = np.array(V); hh = np.array([hfn(p[0], p[1]) for p in V]); sdv, dtv = strata_attrs(hh, V[:, 2], zmean)
        return cw.mk_mesh(bpy, name, V, F, [ys_mat], None, False, kit.coll, {'sd': ('FLOAT', sdv), 'dtop': ('FLOAT', dtv)})
    wall_obj('face_lower', lambda x, y: -DTR, -DEPTH, 24)
    S['face_upper'] = wall_obj('face_upper', hfn, -DTR, 22)
    # ---- the trench: two side walls, the floor and the end wall (strata inside; hidden by the turf until it opens)
    A_ = cw._Acc(); nxs = int((xB - xA) / 0.03)
    for yy, flip in ((yA, True), (yB, False)):
        V, F = grid_wall((xA, yy), (xB, yy), hfn, -DTR, nxs, 22, flip); A_.add(V, F)
    V, F = grid_wall((xA, yA), (xA, yB), hfn, -DTR, ncol, 22, False); A_.add(V, F)
    fx_ = np.linspace(xA, xB, nxs + 1); fy_ = np.linspace(yA, yB, 6)
    V = [(x, y, -DTR) for x in fx_ for y in fy_]; F = [(i * 6 + j, (i + 1) * 6 + j, (i + 1) * 6 + j + 1, i * 6 + j + 1) for i in range(nxs) for j in range(5)]
    A_.add(V, F)
    TV = np.array(A_.V); hh = np.array([hfn(p[0], p[1]) for p in TV]); sdv, dtv = strata_attrs(hh, TV[:, 2], zmean)
    cw.mk_mesh(bpy, 'trench', TV, A_.F, [ys_mat], None, False, kit.coll, {'sd': ('FLOAT', sdv), 'dtop': ('FLOAT', dtv)})
    # ---- fills: gravel (bed, then cover), backfill soil
    e = 0.0015; px_ = np.concatenate([np.linspace(xA + e, xB - 0.0004, 70)])
    S['gravel'] = Prism(kit, 'gravel', px_, yA + e, yB - e, -DTR + 0.0005, mat_gravel(kit, S['V']), ny=9, lump=0.007, seed=3)
    S['backfill'] = Prism(kit, 'backfill', px_, yA + e, yB - e, COVER_Z, mat_backfill(kit), ny=9, lump=0.003, seed=4)
    S['px'] = px_; S['py'] = S['gravel'].ys
    S['hgrid'] = np.array([[hfn(x, y) for y in S['gravel'].ys] for x in px_])
    # ---- the pipe (hollow, perforated) with water in it; the spout at its mouth on the cut face
    yc = (yA + yB) / 2; S['yc'] = yc; plen = (xB + 0.0008) - (xA + 0.05)
    pipe = build_pipe_mesh(bpy, 'drain_pipe', plen, PR, PR * 0.86, mat_pipe(kit), kit.coll)
    S['pipe'] = pipe; S['pipe_seat'] = (xA + 0.05, yc, -DTR + BED + PR)
    S['pwater'] = PipeWater(kit, 'pipe_water', plen + 0.0003, PR * 0.86, mat_flow(kit, S['V'], 'pipe_water'))
    S['pwater'].ob.parent = pipe
    S['spout'] = Spout(kit, 'spout', (xB + 0.0012, yc, -DTR + BED + PR - PR * 0.86 * 0.55), mat_flow(kit, S['V'], 'spout', glass=True))
    # ---- puddle water: a small glass box over the bowl only (never near the trench)
    m_w = cw.mat_water(kit, 'puddle_water', tint=(0.60, 0.58, 0.40), density=6.0, ripple=0.6)
    bx0, bx1 = PUD_C[0] - PUD_R[0] * 1.15, PUD_C[0] + PUD_R[0] * 1.15; by0, by1 = PUD_C[1] - PUD_R[1] * 1.15, PUD_C[1] + PUD_R[1] * 1.15
    assert by0 > yB + 0.05, 'puddle box must stay clear of the trench'
    zb_ = LAWN - PUD_D - 0.03
    Vb = [(bx0, by0, zb_), (bx1, by0, zb_), (bx1, by1, zb_), (bx0, by1, zb_), (bx0, by0, 0), (bx1, by0, 0), (bx1, by1, 0), (bx0, by1, 0)]
    S['puddle'] = cw.mk_mesh(bpy, 'puddle', Vb, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], [m_w], None, False, kit.coll)
    # ---- the yard around it
    build_fence(kit, land); build_shrubs(kit, land); build_patio(kit, land)
    # ---- sky backdrop and light (overcast after the rain, then sun)
    wd = cw.mat_gradient_bg(kit, (0.46, 0.51, 0.57), (0.72, 0.75, 0.78), 1.0, (0.82, 0.86, 0.92), 1.2)
    S['ramp'] = next(n for n in wd.node_tree.nodes if n.bl_idname == 'ShaderNodeValToRGB')
    bgs = [n for n in wd.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground']
    S['bg_light'] = next(n for n in bgs if not n.inputs['Color'].is_linked)
    S['sun'] = cw._sun(kit, 25.0, 50.0, 0.8, 30.0, (0.90, 0.94, 1.0), 'sun')
    cw.cloud_shadows(kit, 0.22)
    # ---- camera
    cam = cw.camera(kit, land, aspect, az=-44, el=33 if not v else 36, lens=55 if v else 50, fill=0.86 if not v else 0.92, top_extra=0.3)
    cd = cam.ob.data
    if v: cd.shift_y = 0.085
    else: cd.shift_x = -0.15
    S['cam'] = cam; S['d0'] = cam.dist; S['t0'] = tuple(cam.target)
    # ---- words
    fonts = {'bold': bpy.data.fonts.load(os.path.join(HERE, 'fonts', 'InterTight-ExtraBold.ttf')),
             'semi': bpy.data.fonts.load(os.path.join(HERE, 'fonts', 'InterTight-SemiBold.ttf'))}
    Wd = Words(kit, cam.ob, cd, W, H, fonts); S['words'] = Wd
    if v:
        X0, Y0w, SZ, MW = 0.12, 0.172, 0.064, 0.645
        for key, body, a, b in WORDS: Wd.text(key, body, X0, Y0w, SZ, a, b, max_w=MW)
        Wd.panel('tag_bg', X0, 0.163, X0 + 0.135, 0.187, CARD_IN, 99, (0.0, 0.0, 0.0), 1.0, 0.5, alpha=0.38)
        Wd.text('tag', 'SAMPLE', X0 + 0.0675, 0.1675, 0.0145, CARD_IN, 99, 'semi', shadow=False, align='CENTER', spacing=1.25)
        Wd.text('name', NAME, X0, 0.205, 0.043, CARD_IN + 0.08, 99, max_w=MW)
        Wd.text('logo', 'Your logo here', X0, 0.318, 0.0205, CARD_IN + 0.20, 99, 'semi')
        Wd.panel('cta_bg', X0, 0.372, X0 + 0.43, 0.418, CARD_IN + 0.32, 99, (0.16, 0.50, 0.25), 1.0, 0.5)
        Wd.text('cta', CTA, X0 + 0.215, 0.3825, 0.0235, CARD_IN + 0.32, 99, 'bold', shadow=False, align='CENTER')
    else:
        X0, Y0w, SZ, MW = 0.065, 0.11, 0.074, 0.40
        for key, body, a, b in WORDS: Wd.text(key, body, X0, Y0w, SZ, a, b, max_w=MW)
        Wd.panel('tag_bg', X0, 0.095, X0 + 0.078, 0.137, CARD_IN, 99, (0.0, 0.0, 0.0), 1.0, 0.5, alpha=0.38)
        Wd.text('tag', 'SAMPLE', X0 + 0.039, 0.1035, 0.026, CARD_IN, 99, 'semi', shadow=False, align='CENTER', spacing=1.25)
        Wd.text('name', NAME, X0, 0.17, 0.066, CARD_IN + 0.08, 99, max_w=0.42)
        Wd.text('logo', 'Your logo here', X0, 0.345, 0.034, CARD_IN + 0.20, 99, 'semi')
        Wd.panel('cta_bg', X0, 0.43, X0 + 0.255, 0.51, CARD_IN + 0.32, 99, (0.16, 0.50, 0.25), 1.0, 0.5)
        Wd.text('cta', CTA, X0 + 0.1275, 0.449, 0.040, CARD_IN + 0.32, 99, 'bold', shadow=False, align='CENTER')
    Wd.layout()
    box = SAFE_916 if v else SAFE_169; bad = []
    for key, x0, x1, y0, y1 in Wd.boxes():
        ok = x0 >= box[0] - 1e-3 and x1 <= box[1] + 1e-3 and y0 >= box[2] - 1e-3 and y1 <= box[3] + 1e-3
        print(f'  words {key:8s} x {x0:.3f} to {x1:.3f}, y {y0:.3f} to {y1:.3f}  {"ok" if ok else "OUTSIDE THE SAFE BOX"}', flush=True)
        if not ok: bad.append(key)
    if bad: raise SystemExit(f'safe box ({"R-2-08" if v else "title safe"}) broken by: {bad}')
    cw.apply_cycles(bpy); sc.cycles.transparent_max_bounces = 24
    S['aspect'] = aspect
    return S

# ================================================================================================ camera plan
CAM = {  # per beat: (time, az, el, dist factor, target or None for the block centre)
    '9:16': [(0.0, -46.0, 35.0, 1.00, None), (3.0, -43.0, 34.0, 0.95, None),
             (6.5, -14.0, 13.0, 0.36, (SX / 2, Y0 + 0.05, -0.30)),
             (11.5, -30.0, 27.0, 0.66, (0.55, -0.15, -0.30)), (15.0, -38.0, 33.0, 0.93, None)],
    '16:9': [(0.0, -46.0, 33.0, 1.00, None), (3.0, -43.0, 32.0, 0.95, None),
             (6.5, -14.0, 12.0, 0.40, (SX / 2, Y0 + 0.05, -0.27)),
             (11.5, -30.0, 25.0, 0.68, (0.55, -0.15, -0.30)), (15.0, -38.0, 31.0, 0.93, None)],
}

def cam_pose(S, t):
    keys = CAM[S['aspect']]; t0 = np.array(S['t0'])
    for a, b in zip(keys[:-1], keys[1:]):
        if t <= b[0] or b is keys[-1]:
            u = ease(ramp(t, (a[0], b[0])))
            ta = t0 if a[4] is None else np.array(a[4]); tb = t0 if b[4] is None else np.array(b[4])
            return lerp(a[1], b[1], u), lerp(a[2], b[2], u), S['d0'] * lerp(a[3], b[3], u), tuple(lerp(ta, tb, u))

# ================================================================================================ per frame
def frame(bpy, ctx, S, i, t):
    kit = S['kit']; kit.update(t); V = S['V']
    az, el, dist, tgt = cam_pose(S, t); S['cam'].pose(az=az, el=el, dist=dist, target=tgt)
    xA, xB = S['xA'], S['xB']
    # the trench opens toward the face, the turf returns from the far end
    xo = lerp(xA - 0.05, xB + 0.05, ease(ramp(t, T_OPEN))); xt = lerp(xA - 0.05, xB + 0.05, ease(ramp(t, T_TURF)))
    for lst in (S['chunks'], S['gchunks']):
        for o, xm in lst:
            if o is not None: o.hide_render = (xo > xm) and not (xt > xm)
    S['face_upper'].hide_render = xo > xB
    # gravel: bed then cover, each poured as a front moving along the trench
    px = S['px'][:, None]; z0 = -DTR
    f1 = np.clip((lerp(xA - 0.3, xB + 0.3, ramp(t, T_BED)) - px) / 0.3, 0, 1)
    f2 = np.clip((lerp(xA - 0.3, xB + 0.3, ramp(t, T_COVER)) - px) / 0.3, 0, 1)
    zg = z0 + BED * f1 + (COVER_Z - z0 - BED) * f2 + np.zeros((1, len(S['py'])))
    S['gravel'].set_top(zg); S['gravel'].ob.hide_render = t < T_BED[0]
    f3 = np.clip((lerp(xA - 0.3, xB + 0.3, ramp(t, T_BACK)) - px) / 0.3, 0, 1)
    S['backfill'].set_top(COVER_Z + (S['hgrid'] - 0.004 - COVER_Z) * f3); S['backfill'].ob.hide_render = t < T_BACK[0]
    # the pipe is lowered in and settles on the bed
    sx_, sy_, sz_ = S['pipe_seat']; u = ramp(t, T_PIPE); drop = 0.55 * (1 - ease_out(u))
    S['pipe'].location = (sx_, sy_, sz_ + drop); S['pipe'].hide_render = t < T_PIPE[0]
    # water: drawdown in the soil, through the gravel, along the pipe and out of its mouth
    P = ease(ramp(t, T_DRAIN)); V['drain'].default_value = P; V['time'].default_value = t
    flow = ramp(t, (9.0, 9.6)) * (1 - ease(ramp(t, (10.9, 11.6))))
    V['flow'].default_value = flow * 0.9
    V['wet'].default_value = 1 - ease(ramp(t, (9.6, 12.0)))
    V['gravel_wet'].default_value = ramp(t, (9.1, 9.7)) * (1 - 0.8 * ease(ramp(t, (10.8, 12.0))))
    for k in ('time_pipe_water', 'time_spout'):
        if k in V: V[k].default_value = t
    depth = PR * 0.86 * 2 * (0.06 + 0.42 * flow)
    S['pwater'].set_depth(depth); S['pwater'].ob.hide_render = t < 9.05 or t > 11.7
    sp_len = 0.42 * ease_out(ramp(t, (9.3, 9.8))); sp_r = 0.016 * flow ** 0.7
    S['spout'].set(sp_len, max(sp_r, 1e-4)); S['spout'].ob.hide_render = sp_len < 0.01 or sp_r < 0.002
    # puddle drains away into the soil
    lv = lerp(PUD_LEVEL, LAWN - PUD_D - 0.012, ease(ramp(t, T_PUDDLE)))
    pz = S['puddle'].data.vertices
    for k in range(4, 8): pz[k].co.z = lv
    S['puddle'].data.update(); S['puddle'].hide_render = t > T_PUDDLE[1] + 0.05
    # light: overcast after rain, then sun
    s = ease(ramp(t, T_SUN)); sun = S['sun'].data
    sun.energy = lerp(0.8, 3.6, s); sun.angle = math.radians(lerp(30.0, 4.0, s)); sun.color = lerp3((0.90, 0.94, 1.0), (1.0, 0.95, 0.86), s)
    el_ = S['ramp'].color_ramp.elements
    el_[0].color = cw.srgb(lerp3((0.72, 0.75, 0.78), (0.80, 0.88, 0.95), s)); el_[-1].color = cw.srgb(lerp3((0.46, 0.51, 0.57), (0.33, 0.56, 0.84), s))
    S['bg_light'].inputs['Color'].default_value = cw.srgb(lerp3((0.82, 0.86, 0.92), (0.80, 0.88, 1.0), s))
    S['bg_light'].inputs['Strength'].default_value = lerp(1.25, 0.85, s)
    S['words'].update(t)
