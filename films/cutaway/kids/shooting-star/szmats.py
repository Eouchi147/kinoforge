"""What is a shooting star? Time-driven materials (bpy, on the Cutaway kit's node builder).

As on the seasons loop, every colour or amount that changes in the story is a Value or RGB node that `Drive` sets each
frame. The one that matters here is `tint`: the colour of the light of the moment (sunset gold, twilight rose, night blue),
multiplied into every painted material, so one number per frame takes the whole world from dusk to night while the glowing
things (fire, windows, stars, fireflies, the streak) are emission and ignore it. Materials meant to be repainted by Fable keep
a Principled BSDF with the story colour on its Base Color (Fable's paint reads it, keeps any transparent cut-out mix).
Materials Fable must leave alone (the glowing things, the water, the words) are emission only.
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


def _tinted(g, D, col):
    """col multiplied by the light of the moment."""
    return g.mix(1.0, col, D.rgb(g, 'tint', (1.0, 1.0, 1.0)), 'MULTIPLY')


def paint(kit, D, name, color, rough=0.7, alpha=None, noise=0.12, drive=None, lit=True):
    """A plain material: Principled with a base colour (a fixed sRGB, or the driven RGB `drive`), a little mottle, the light
    of the moment (tint) and an optional driven alpha (the name of a Drive value) for fades."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    col = D.rgb(g, drive, color) if drive else srgb(color)
    if noise:
        tc = g.node('ShaderNodeTexCoord'); n = g.noise(tc.outputs['Object'], 14.0, 3.0)
        col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], noise), col, g.mix(0.6, col, (0, 0, 0, 1), 'MULTIPLY'))
    if lit: col = _tinted(g, D, col)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': rough})
    if alpha: _alpha_out(g, p, D.val(g, alpha, 1.0))
    else: cw._finish(g, p)
    return m


def varied(kit, D, name, colors, alpha=None, tip=None, height=0.1):
    """Per-object colour from Object Info Random over `colors` (plants, crowds); optional lighter tips; tinted by the night."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    oi = g.node('ShaderNodeObjectInfo'); col = g.ramp(oi.outputs['Random'], [(i / max(1, len(colors) - 1), c) for i, c in enumerate(colors)])
    if tip is not None:
        z = g.sep(g.node('ShaderNodeTexCoord').outputs['Object'])[2]; f = g.math('MULTIPLY', z, 1.0 / height, clamp=True)
        col = g.mix(g.math('POWER', f, 1.4), g.mix(0.5, col, (0.0, 0.0, 0.0, 1), 'MULTIPLY'), g.mix(0.6, col, srgb(tip)))
    col = _tinted(g, D, col)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.6})
    if alpha: _alpha_out(g, p, D.val(g, alpha, 1.0))
    else: cw._finish(g, p)
    return m


def mat_top(kit, D):
    """The hilltop: meadow green over earth, trodden bare round the fire (driven 'fire' amount lights a warm circle on the
    grass), hazier and bluer with distance (attribute far, driven 'haze'), tinted by the light of the moment."""
    m = cw._new_mat(kit.bpy, 'sz_top'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; sx = g.sep(P)
    nb = g.noise(P, 1.4, 3.0); nm = g.noise(P, 7.0, 3.0)
    grass = g.mix(g.math('MULTIPLY', nm.outputs['Fac'], 0.9), srgb((0.30, 0.56, 0.30)), srgb((0.42, 0.70, 0.34)))
    grass = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', nb.outputs['Fac'], 0.45), 1.2, clamp=True), grass, srgb((0.22, 0.46, 0.30)))
    # the ground trodden bare in a ring round the campfire (earth brown)
    r = g.vmath('LENGTH', g.comb(g.math('SUBTRACT', sx[0], W.FIRE[0]), g.math('SUBTRACT', sx[1], W.FIRE[1]), 0.0))
    bare = g.math('MULTIPLY', g.math('SUBTRACT', 0.62, r), 4.0, clamp=True)
    earth = g.mix(nm.outputs['Fac'], srgb((0.50, 0.36, 0.24)), srgb((0.58, 0.44, 0.30)))
    col = g.mix(bare, grass, earth)
    # the land around the block: a small step of light just outside it, then haze with distance (attribute far)
    fa = g.attr('far').outputs['Fac']
    col = g.mix(1.0, col, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MINIMUM', fa, 0.25), 0.9)), 'MULTIPLY')
    col = _tinted(g, D, col)
    col = g.mix(g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', fa, 0.18), 0.0), 0.8), col, D.rgb(g, 'haze', (0.30, 0.38, 0.58)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.85})
    cw._finish(g, p); return m


def mat_glow(kit, D, name, color, strength=1.0, alpha=None):
    """Pure emission (sparkles, glints, windows, fire); optional driven alpha."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': strength})
    if alpha: _alpha_out(g, e, D.val(g, alpha, 1.0))
    else: cw._finish(g, e)
    return m


def mat_drive_glow(kit, D, name, drive, strength=1.0, alpha=None):
    """Emission whose colour is a driven RGB (a window's warm light, the fire, the lake's sky colour)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': D.rgb(g, drive), 'Strength': strength})
    if alpha: _alpha_out(g, e, D.val(g, alpha, 1.0))
    else: cw._finish(g, e)
    return m


def mat_halo(kit, D, name, color, alpha_name, power=2.0, strength=1.0):
    """A soft round glow on a disc (centre at the object origin, radius = the disc's radius `R` kept in the attribute 'rr'
    = 0 at the centre and 1 at the rim): emission with a smooth radial falloff, alpha driven. For fire light on the grass,
    the head of the streak, the moon's halo."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    rr = g.attr('rr').outputs['Fac']
    fall = g.math('POWER', g.math('SUBTRACT', 1.0, rr, clamp=True), power)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': strength})
    a = g.math('MULTIPLY', fall, D.val(g, alpha_name, 1.0))
    _alpha_out(g, e, a); return m


def mat_water(kit, D):
    """The lake: emission in the night sky's own colours (driven 'lake_a' to 'lake_b'), long soft ripple strokes, the stars
    mirrored as small bright dots that shimmer, a pale moon path; Fable leaves emission alone."""
    m = cw._new_mat(kit.bpy, 'fs_lake'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; sx = g.sep(P)
    zoff, w = g.phase(0.25)
    rn = g.noise(g.comb(g.math('MULTIPLY', sx[0], 3.0), g.math('MULTIPLY', sx[1], 16.0), zoff), 1.0, 2.0, 0.5, '4D', w)
    strokes = g.math('MULTIPLY', g.math('SUBTRACT', rn.outputs['Fac'], 0.56), 10.0, clamp=True)
    col = g.mix(g.math('MULTIPLY', sx[1], 0.0), D.rgb(g, 'lake_a', (0.10, 0.20, 0.40)), D.rgb(g, 'lake_b', (0.14, 0.26, 0.46)))
    col = g.mix(g.math('MULTIPLY', strokes, 0.22), col, srgb((0.62, 0.74, 0.92)))
    # mirrored stars: tiny bright dots (voronoi cells' centres), twinkling with the phase
    vo = g.voronoi(g.comb(g.math('MULTIPLY', sx[0], 9.0), g.math('MULTIPLY', sx[1], 9.0), g.math('MULTIPLY', zoff, 0.5)), 1.0, 'F1', '3D')
    dot = g.math('MULTIPLY', g.math('SUBTRACT', 0.075, vo.outputs['Distance'], clamp=True), 13.0)
    dot = g.math('MULTIPLY', dot, g.math('MULTIPLY', D.val(g, 'night', 0.0), g.math('MULTIPLY', rn.outputs['Fac'], 1.6, clamp=True)))
    col = g.mix(g.math('MINIMUM', dot, 1.0), col, srgb((1.0, 0.96, 0.78)))
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}); cw._finish(g, e); return m
