"""How is a volcano born? Time-driven materials (bpy, on the Cutaway kit's node builder).

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


def mat_land(kit, D):
    """The ground of the slice's top and of the world round it (one material): dark volcanic rock, a pale sand beach and sea
    floor (attribute bch), greened from the shore up by the plants ('front' against attribute gq, 0 at the summit and 1 at the
    shore) or green all the time on the older islands (attribute gperm), a step of light just outside the block and haze with
    distance (attribute far, colour 'haze')."""
    m = cw._new_mat(kit.bpy, 'sz_top'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']
    nb = g.noise(P, 1.6, 3.0); nm = g.noise(P, 7.0, 3.0); nf = g.noise(P, 34.0, 3.0)
    rock = g.mix(nm.outputs['Fac'], srgb((0.22, 0.16, 0.21)), srgb((0.36, 0.27, 0.30)))
    rock = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', nf.outputs['Fac'], 0.55), 3.0, clamp=True), 0.5), rock, srgb((0.52, 0.40, 0.40)))
    gcol = g.mix(nm.outputs['Fac'], srgb((0.24, 0.62, 0.32)), srgb((0.44, 0.76, 0.34)))
    gcol = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', nb.outputs['Fac'], 0.5), 0.6), gcol, srgb((0.14, 0.48, 0.30)))
    gq = g.attr('gq').outputs['Fac']; gp = g.attr('gperm').outputs['Fac']
    reach = g.math('MULTIPLY', g.math('SUBTRACT', D.val(g, 'front'), g.math('SUBTRACT', 1.0, gq)), 7.0, clamp=True)
    patchy = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', nb.outputs['Fac'], g.math('MULTIPLY', D.val(g, 'front'), 0.35)), 0.55), 6.0, clamp=True)
    gm = g.math('MAXIMUM', g.math('MULTIPLY', reach, patchy), gp)
    col = g.mix(gm, rock, gcol)
    sand = g.mix(nf.outputs['Fac'], srgb((0.93, 0.80, 0.55)), srgb((0.99, 0.90, 0.68)))
    col = g.mix(g.attr('bch').outputs['Fac'], col, sand)
    col = g.mix(g.attr('dp').outputs['Fac'], col, g.mix(nm.outputs['Fac'], srgb((0.30, 0.62, 0.62)), srgb((0.40, 0.72, 0.68))))
    fa = g.attr('far').outputs['Fac']
    col = g.mix(1.0, col, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MINIMUM', fa, 0.25), 0.9)), 'MULTIPLY')
    col = g.mix(g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', fa, 0.18), 0.0), 1.3), col, D.rgb(g, 'haze', (0.40, 0.70, 0.74)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.9})
    cw._finish(g, p); return m




def mat_glow(kit, D, name, color, strength=1.0, alpha=None):
    """Pure emission (sparkles, glints, outlines); optional driven alpha."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': strength})
    if alpha: _alpha_out(g, e, D.val(g, alpha, 1.0))
    else: cw._finish(g, e)
    return m


def mat_water(kit, D):
    """Flat painted sea water (emission, so Fable keeps it): turquoise with ripple strokes and pale glints on the surface, a
    deeper blue on the cut faces, partly see-through (the sand shows through the shallows)."""
    m = cw._new_mat(kit.bpy, 'fs_water'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry'); P = tc.outputs['Object']; sx = g.sep(P)
    topf = g.math('GREATER_THAN', g.sep(geo.outputs['Normal'])[2], 0.5)
    zoff, w = g.phase(0.35)
    rn = g.noise(g.comb(g.math('MULTIPLY', sx[0], 4.0), g.math('MULTIPLY', sx[1], 16.0), zoff), 1.0, 2.0, 0.5, '4D', w)
    strokes = g.math('MULTIPLY', g.math('SUBTRACT', rn.outputs['Fac'], 0.58), 14.0, clamp=True)
    clear = g.mix(strokes, srgb((0.10, 0.62, 0.74)), srgb((0.88, 0.98, 0.96)))
    side = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', 0.0, g.sep(P)[2]), 1.4, clamp=True), srgb((0.16, 0.66, 0.74)), srgb((0.06, 0.34, 0.56)))
    col = g.mix(topf, side, clear)
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    _alpha_out(g, e, g.math('MULTIPLY', 0.62, D.val(g, 'walpha', 1.0))); return m


def mat_lava(kit, D, name='fs_lava'):
    """Lava and magma (emission: Fable leaves it alone). Attribute ht = heat 0 to 1 (white-gold hot, orange, red, then dark
    and see-through when cold), e = 0 at the edge to 1 in the middle (a darker, redder crust at the edge). 'pulse' breathes."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    ht = g.attr('ht').outputs['Fac']; e = g.attr('e').outputs['Fac']
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']
    zoff, w = g.phase(0.5)
    n = g.noise(g.comb(g.math('MULTIPLY', g.sep(P)[0], 9.0), g.math('MULTIPLY', g.sep(P)[2], 9.0), zoff), 1.0, 3.0, 0.5, '4D', w)
    h = g.math('ADD', ht, g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.5), 0.35))
    col = g.ramp(g.math('MINIMUM', g.math('MAXIMUM', h, 0.0), 1.0), [(0.0, (0.22, 0.10, 0.12)), (0.18, (0.72, 0.14, 0.10)), (0.45, (1.0, 0.42, 0.12)), (0.75, (1.0, 0.72, 0.22)), (1.0, (1.0, 0.94, 0.55))])
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', e, 2.2, clamp=True)), 0.55), col, srgb((0.45, 0.10, 0.10)))
    em = g.node('ShaderNodeEmission', ins={'Color': col}); g.put(em, 'Strength', g.math('ADD', 0.9, g.math('MULTIPLY', g.math('ADD', ht, D.val(g, 'pulse')), 0.9)))
    alpha = g.math('MULTIPLY', g.math('MULTIPLY', ht, 9.0, clamp=True), 1.0)
    _alpha_out(g, em, alpha); return m




def mat_word(kit, D, name, color, alpha_name):
    """Words, plates and graphics set in code: emission with a driven alpha (Fable recolours them ink or paper)."""
    return mat_glow(kit, D, name, color, 1.0, alpha_name)
