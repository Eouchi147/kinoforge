"""How does a dinosaur turn into stone? Time-driven materials (bpy, on the Cutaway kit's node builder).

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


def mat_bones(kit, D):
    """The fossil in the cut face (emission: Fable leaves it alone). Attribute bi = place along the skeleton (0 tail tip,
    1 skull), sh = 1 at a bone's centre line and 0 at its rim (painted roundness). 'front' moves the stone through the
    bones (cream bone to blue-grey stone with gold), 'wet' tints them with seeping water, 'balpha' fades them in."""
    m = cw._new_mat(kit.bpy, 'fs_bones'); g = G(m.node_tree, kit)
    bi = g.attr('bi').outputs['Fac']; sh = g.attr('sh').outputs['Fac']
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; n = g.noise(P, 40.0, 3.0)
    stone = g.math('MULTIPLY', g.math('SUBTRACT', D.val(g, 'front'), bi), 6.0, clamp=True)
    bone = g.mix(n.outputs['Fac'], srgb((0.98, 0.92, 0.78)), srgb((1.0, 0.97, 0.88)))
    rock = g.mix(n.outputs['Fac'], srgb((0.62, 0.66, 0.72)), srgb((0.80, 0.80, 0.78)))
    vo = g.voronoi(P, 90.0, 'F1'); fleck = g.math('LESS_THAN', vo.outputs['Distance'], 0.16)
    rock = g.mix(g.math('MULTIPLY', fleck, 0.8), rock, srgb((1.0, 0.80, 0.34)))
    col = g.mix(stone, bone, rock)
    col = g.mix(g.math('MULTIPLY', D.val(g, 'wet'), 0.55), col, srgb((0.45, 0.78, 1.0)))
    col = g.mix(1.0, col, g.math('ADD', 0.72, g.math('MULTIPLY', sh, 0.34)), 'MULTIPLY')
    e = g.node('ShaderNodeEmission', ins={'Color': col}); g.put(e, 'Strength', g.math('ADD', 1.0, g.math('MULTIPLY', D.val(g, 'bglow'), 0.6)))
    _alpha_out(g, e, D.val(g, 'balpha', 1.0)); return m


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
    clear = g.mix(strokes, srgb((0.16, 0.62, 0.66)), srgb((0.86, 0.96, 0.92)))
    murky = g.mix(strokes, srgb((0.52, 0.44, 0.30)), srgb((0.80, 0.70, 0.50)))
    col = g.mix(D.val(g, 'murk'), clear, murky)
    side = g.mix(D.val(g, 'murk'), srgb((0.10, 0.44, 0.52)), srgb((0.44, 0.36, 0.24)))
    col = g.mix(topf, side, col)
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    a = g.math('MULTIPLY', g.math('ADD', 0.62, g.math('MULTIPLY', D.val(g, 'murk'), 0.3)), D.val(g, 'walpha', 1.0))
    _alpha_out(g, e, a); return m


def mat_word(kit, D, name, color, alpha_name):
    """Words, plates and graphics set in code: emission with a driven alpha (Fable recolours them ink or paper)."""
    return mat_glow(kit, D, name, color, 1.0, alpha_name)
