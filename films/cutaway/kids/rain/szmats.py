"""Where does rain come from? Time-driven materials (bpy, on the Cutaway kit's node builder).

As on the seasons loop (films/cutaway/loops/seasons/szmats.py), every colour or amount that changes in the story is a Value
or RGB node that `Drive` sets each frame, so the world can change inside one render. Materials meant to be repainted by
Fable keep a Principled BSDF with the story colour on its Base Color (Fable's paint reads it, keeps any transparent
cut-out mix). Materials Fable must leave alone (the bones, the sparkles, the water, the words) are emission only.
"""
import math

import cutaway as cw
from cutaway import G, srgb
import szworld as W


class Drive:
    def __init__(self): self.v = {}; self.c = {}
    def val(self, g, name, init=0.0):
        n = g.node('ShaderNodeValue'); n.outputs[0].default_value = init; n.label = name
        self.v.setdefault(name, []).append(n.outputs[0]); return n.outputs[0]
    def rgb(self, g, name, init=(0.5, 0.5, 0.5)):
        n = g.node('ShaderNodeRGB'); n.outputs[0].default_value = srgb(init); n.label = name
        self.c.setdefault(name, []).append(n.outputs[0]); return n.outputs[0]
    def set(self, name, x):
        for s in self.v.get(name, []): s.default_value = float(x)
    def setc(self, name, c):
        for s in self.c.get(name, []): s.default_value = srgb(c)


def _alpha_out(g, shader, alpha):
    """Surface = mix(transparent, shader, alpha): Fable's under_mask keeps such a cut-out and swaps only the shader."""
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(alpha, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(shader, mx.inputs[2]); cw._finish(g, mx); return mx


def paint(kit, D, name, color, rough=0.7, alpha=None, noise=0.12, drive=None):
    """A plain material: Principled with a base colour (a fixed sRGB, or the driven RGB `drive`), a little mottle, and
    an optional driven alpha (the name of a Drive value) for fades."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    col = D.rgb(g, drive, color) if drive else srgb(color)
    if noise:
        tc = g.node('ShaderNodeTexCoord'); n = g.noise(tc.outputs['Object'], 14.0, 3.0)
        col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], noise), col, g.mix(0.6, col, (0, 0, 0, 1), 'MULTIPLY'))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': rough})
    if alpha: _alpha_out(g, p, D.val(g, alpha, 1.0))
    else: cw._finish(g, p)
    return m


def varied(kit, D, name, colors, alpha=None, tip=None, height=0.1):
    """Per-object colour from Object Info Random over `colors` (plants, creatures in crowds); optional lighter tips."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    oi = g.node('ShaderNodeObjectInfo'); col = g.ramp(oi.outputs['Random'], [(i / max(1, len(colors) - 1), c) for i, c in enumerate(colors)])
    if tip is not None:
        z = g.sep(g.node('ShaderNodeTexCoord').outputs['Object'])[2]; f = g.math('MULTIPLY', z, 1.0 / height, clamp=True)
        col = g.mix(g.math('POWER', f, 1.4), g.mix(0.5, col, (0.0, 0.0, 0.0, 1), 'MULTIPLY'), g.mix(0.6, col, srgb(tip)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.6})
    if alpha: _alpha_out(g, p, D.val(g, alpha, 1.0))
    else: cw._finish(g, p)
    return m


def mat_top(kit, D):
    """The top: the bare ground of the moment ('ground', driven: today's earth, the fern floor, fresh mud, each new
    layer, worn rock), greened by plants ('green' amount, 'greencol'), a sandy bed along the water course (attribute rd
    = distance to the course, driven width 'rw'), darker and glossy while wet ('wet')."""
    m = cw._new_mat(kit.bpy, 'sz_top'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']
    rd = g.attr('rd').outputs['Fac']
    nb = g.noise(P, 1.4, 3.0); nm = g.noise(P, 7.0, 3.0); nf = g.noise(P, 34.0, 3.0)
    ground = g.mix(g.math('MULTIPLY', nm.outputs['Fac'], 0.5), D.rgb(g, 'ground'), g.mix(0.6, D.rgb(g, 'ground'), (0, 0, 0, 1), 'MULTIPLY'))
    gp = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', nb.outputs['Fac'], g.math('MULTIPLY', D.val(g, 'green'), 1.1)), 0.75), 4.0, clamp=True)
    green = g.mix(nm.outputs['Fac'], D.rgb(g, 'greencol'), g.mix(0.35, D.rgb(g, 'greencol'), (1.0, 1.0, 0.6, 1)))
    col = g.mix(gp, ground, green)
    # the water course: sand and pebbles on its bed and banks
    bank = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', D.val(g, 'rw'), 0.07), rd), 18.0, clamp=True)
    bank = g.math('MULTIPLY', bank, g.math('GREATER_THAN', D.val(g, 'rw'), 0.01))
    sand = g.mix(nf.outputs['Fac'], srgb((0.82, 0.70, 0.50)), srgb((0.92, 0.82, 0.62)))
    col = g.mix(bank, col, sand)
    # today: bare rock round the girl's dig (attribute rk), with cracks, where the land wore away
    rk = g.math('MULTIPLY', g.attr('rk').outputs['Fac'], D.val(g, 'rockamt'))
    vo = g.voronoi(P, 16.0, 'DISTANCE_TO_EDGE'); crack = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 30.0), clamp=True)
    stone = g.mix(nm.outputs['Fac'], srgb((0.74, 0.70, 0.62)), srgb((0.86, 0.82, 0.72)))
    stone = g.mix(g.math('MULTIPLY', crack, 0.5), stone, srgb((0.46, 0.42, 0.40)))
    col = g.mix(rk, col, stone)
    # the little rock face at the back of today's hollow: the fossil's own band colour, with fine layer lines
    geo = g.node('ShaderNodeNewGeometry'); steep = g.math('MULTIPLY', g.math('SUBTRACT', 0.80, g.sep(geo.outputs['Normal'])[2]), 4.0, clamp=True)
    lines = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ABSOLUTE', g.math('SINE', g.math('MULTIPLY', g.sep(P)[2], 220.0))), 0.85), 6.0, clamp=True)
    face = g.mix(g.math('MULTIPLY', lines, 0.6), srgb((0.40, 0.58, 0.52)), srgb((0.62, 0.76, 0.68)))
    col = g.mix(g.math('MULTIPLY', steep, rk), col, face)
    # the land around the block: a small step of light just outside it, then haze with distance (attribute far)
    fa = g.attr('far').outputs['Fac']
    col = g.mix(1.0, col, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MINIMUM', fa, 0.25), 0.9)), 'MULTIPLY')
    col = g.mix(g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', fa, 0.18), 0.0), 1.3), col, D.rgb(g, 'haze', (0.62, 0.74, 0.72)))
    wet = D.val(g, 'wet')
    col = g.mix(g.math('MULTIPLY', wet, 0.4), col, g.mix(1.0, col, (0.5, 0.5, 0.55, 1), 'MULTIPLY'))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col}); g.put(p, 'Roughness', g.math('SUBTRACT', 0.85, g.math('MULTIPLY', wet, 0.5)))
    cw._finish(g, p); return m


def mat_glow(kit, D, name, color, strength=1.0, alpha=None):
    """Pure emission (sparkles, glints, outlines); optional driven alpha."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': strength})
    if alpha: _alpha_out(g, e, D.val(g, alpha, 1.0))
    else: cw._finish(g, e)
    return m


def mat_water(kit, D):
    """Flat painted water (emission, so Fable keeps it): teal with ripple strokes and pale glints, browner and more opaque
    in a flood ('murk'), a pale meniscus line on the cut face, partly see-through."""
    m = cw._new_mat(kit.bpy, 'fs_water'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry'); P = tc.outputs['Object']; sx = g.sep(P)
    topf = g.math('GREATER_THAN', g.sep(geo.outputs['Normal'])[2], 0.5)
    zoff, w = g.phase(0.35)
    rn = g.noise(g.comb(g.math('MULTIPLY', sx[0], 4.0), g.math('MULTIPLY', sx[1], 16.0), zoff), 1.0, 2.0, 0.5, '4D', w)
    strokes = g.math('MULTIPLY', g.math('SUBTRACT', rn.outputs['Fac'], 0.58), 14.0, clamp=True)
    clear = g.mix(strokes, srgb((0.12, 0.50, 0.86)), srgb((0.74, 0.92, 1.0)))
    murky = g.mix(strokes, srgb((0.52, 0.44, 0.30)), srgb((0.80, 0.70, 0.50)))
    col = g.mix(D.val(g, 'murk'), clear, murky)
    side = g.mix(D.val(g, 'murk'), srgb((0.10, 0.44, 0.52)), srgb((0.44, 0.36, 0.24)))
    col = g.mix(topf, side, col)
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    a = g.math('MULTIPLY', g.math('ADD', 0.90, g.math('MULTIPLY', D.val(g, 'murk'), 0.1)), D.val(g, 'walpha', 1.0))
    _alpha_out(g, e, a); return m


def mat_word(kit, D, name, color, alpha_name):
    """Words, plates and graphics set in code: emission with a driven alpha (Fable recolours them ink or paper)."""
    return mat_glow(kit, D, name, color, 1.0, alpha_name)


def mat_soilwater(kit, D):
    """Water in the cut faces (emission over the strata, so Fable leaves it alone): the soil darkens blue from the top down
    as far as the wet front ('wfront', metres below the surface; attribute dep = depth below the local surface), and the
    sand below the water table ('gwl', slice z; attribute zs) holds shining water with a bright line at its top."""
    m = cw._new_mat(kit.bpy, 'fs_soilwater'); g = G(m.node_tree, kit)
    dep = g.attr('dep').outputs['Fac']; zs = g.attr('zs').outputs['Fac']; ux = g.attr('ux').outputs['Fac']
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']
    n = g.noise(g.comb(g.math('MULTIPLY', ux, 8.0), g.math('MULTIPLY', zs, 3.0), 0.0), 1.0, 3.0)
    ragged = g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.5), 0.14)
    fr = g.math('ADD', D.val(g, 'wfront'), g.math('MULTIPLY', ragged, g.math('MINIMUM', D.val(g, 'wfront'), 1.0)))
    wetsoil = g.math('MULTIPLY', g.math('SUBTRACT', fr, dep), 90.0, clamp=True)
    wetsoil = g.math('MULTIPLY', wetsoil, g.math('GREATER_THAN', D.val(g, 'wfront'), 0.004))
    gwl = D.val(g, 'gwl', W.GW_LO)
    in_sand = g.math('MULTIPLY', g.math('GREATER_THAN', zs, W.SAND_BOT), g.math('LESS_THAN', zs, W.SAND_TOP + 0.001))
    below = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', gwl, zs), 150.0, clamp=True), in_sand)
    line = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', zs, gwl)), 260.0), clamp=True), in_sand)
    sh = g.math('MULTIPLY', g.math('SUBTRACT', g.noise(g.comb(g.math('MULTIPLY', ux, 14.0), g.math('MULTIPLY', zs, 60.0), 0.0), 1.0, 2.0).outputs['Fac'], 0.5), 0.25)
    water = g.mix(g.math('ADD', 0.5, sh), srgb((0.10, 0.46, 0.86)), srgb((0.40, 0.78, 1.0)))
    col = g.mix(g.math('MINIMUM', g.math('MULTIPLY', below, 2.0), 1.0), srgb((0.05, 0.14, 0.40)), water)
    col = g.mix(line, col, srgb((0.86, 0.97, 1.0)))
    alpha = g.math('MAXIMUM', g.math('MAXIMUM', g.math('MULTIPLY', wetsoil, 0.66), g.math('MULTIPLY', below, 0.88)), g.math('MULTIPLY', line, 1.0))
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    _alpha_out(g, e, alpha); return m


def mat_vapor(kit, D):
    """The invisible water that rises (pale shimmering ribbons, thin and faint): alpha = the ribbon's own fade profile
    (attribute fa) times the driven amount 'a_vap'."""
    m = cw._new_mat(kit.bpy, 'fs_vapor'); g = G(m.node_tree, kit)
    fa = g.attr('fa').outputs['Fac']; e = g.attr('fe').outputs['Fac']
    col = g.mix(fa, srgb((0.80, 0.92, 1.0)), srgb((1.0, 0.99, 0.92)))
    a = g.math('MULTIPLY', g.math('MULTIPLY', fa, e), g.math('MULTIPLY', D.val(g, 'a_vap'), 0.62))
    em = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.2})
    _alpha_out(g, em, a); return m


def mat_rainbow(kit, D):
    """The rainbow: seven soft bands (attribute rb = band index 0..1 across the arc, e = soft edge), alpha 'a_rb'."""
    m = cw._new_mat(kit.bpy, 'fs_rainbow'); g = G(m.node_tree, kit)
    rb = g.attr('rb').outputs['Fac']; e = g.attr('fe').outputs['Fac']
    col = g.ramp(rb, [(0.0, (0.96, 0.30, 0.30)), (0.17, (1.0, 0.58, 0.24)), (0.34, (1.0, 0.88, 0.32)), (0.51, (0.48, 0.82, 0.42)),
                      (0.68, (0.34, 0.72, 0.92)), (0.84, (0.40, 0.46, 0.90)), (1.0, (0.66, 0.42, 0.84))])
    a = g.math('MULTIPLY', e, g.math('MULTIPLY', D.val(g, 'a_rb'), 0.78))
    em = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.1})
    _alpha_out(g, em, a); return m
