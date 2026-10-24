"""What lives in the deep sea? Time-driven materials (bpy, on the Cutaway kit's node builder).

Everything under the water is EMISSION ONLY (Fable leaves emission-only materials alone) and is lit by this file's own
sea shader, not by Blender lights: a painted flat colour with one hard toon step from the sun, multiplied by the light
that is left at its depth (sunlight fades with depth), tinted toward the water's colour with depth, plus the light of
three small lamps that the story drives: the submarine's headlamp (a cone), the anglerfish's lure (a ball of light) and
the glow of the hot vent (a ball of warm light). Glowing animals are plain emission with a driven strength.
Every amount is a Value or RGB node that `Drive` sets each frame, so one render holds the whole story (pure function of t).
"""
import math

import cutaway as cw
from cutaway import G, srgb
import szworld as W

DEEPN = W.DEEP

# depth -> (ambient light left, fog amount, fog colour): sunlight fades as you go down (NOAA zones, painted)
DEPTH_STOPS = [(0.00, 1.00, 0.02, (0.30, 0.86, 0.95)), (0.84, 0.86, 0.22, (0.14, 0.66, 0.88)), (1.25, 0.62, 0.42, (0.20, 0.36, 0.72)),
               (1.70, 0.38, 0.62, (0.14, 0.18, 0.52)), (2.30, 0.20, 0.80, (0.05, 0.07, 0.24)), (2.90, 0.14, 0.86, (0.03, 0.04, 0.17))]


class Drive:
    def __init__(self): self.v = {}; self.c = {}; self.r = {}
    def val(self, g, name, init=0.0):
        n = g.node('ShaderNodeValue'); n.outputs[0].default_value = init; n.label = name
        self.v.setdefault(name, []).append(n.outputs[0]); return n.outputs[0]
    def rgb(self, g, name, init=(0.5, 0.5, 0.5)):
        n = g.node('ShaderNodeRGB'); n.outputs[0].default_value = srgb(init); n.label = name
        self.c.setdefault(name, []).append(n.outputs[0]); return n.outputs[0]
    def vec(self, g, name, init=(0.0, 0.0, 0.0)):
        """A raw 3-vector (positions, directions) carried in an RGB node's colour: never colour-converted."""
        n = g.node('ShaderNodeRGB'); n.outputs[0].default_value = tuple(init) + (1.0,); n.label = name
        self.r.setdefault(name, []).append(n.outputs[0]); return n.outputs[0]
    def set(self, name, x):
        for s in self.v.get(name, []): s.default_value = float(x)
    def setc(self, name, c):
        for s in self.c.get(name, []): s.default_value = srgb(c)
    def setv(self, name, p):
        for s in self.r.get(name, []): s.default_value = (float(p[0]), float(p[1]), float(p[2]), 1.0)


def _alpha_out(g, shader, alpha):
    """Surface = mix(transparent, shader, alpha)."""
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.put(mx, 0, alpha); g.link(tr, mx.inputs[1]); g.link(shader, mx.inputs[2]); cw._finish(g, mx); return mx


def _depth(g, D):
    """(world position, depth below the slice's surface in metres): depth = lift - world z."""
    geo = g.node('ShaderNodeNewGeometry'); P = geo.outputs['Position']
    d = g.math('SUBTRACT', D.val(g, 'lift', W.LIFT0), g.sep(P)[2])
    return geo, P, d


def _ramp1(g, x, stops, ch):
    """A float ramp over x (depth m) from DEPTH_STOPS (ch 1 = ambient, 2 = fog amount)."""
    return g.sep(g.ramp(g.math('DIVIDE', x, DEEPN, clamp=True), [(s[0] / DEEPN, (s[ch],) * 3) for s in stops]))[0]


def _lamps(g, D, P):
    """The three story lamps as a colour (to add, multiplied by the thing's own colour): the submarine's headlamp (a soft
    cone along 'lampD' from 'lampP'), the lure (a round pool of gold) and the vent (a round pool of amber)."""
    v = g.vmath('SUBTRACT', P, D.vec(g, 'lampP')); dist = g.vmath('LENGTH', v)
    dirn = g.vmath('SCALE', v, (0, 0, 0), scale=g.math('DIVIDE', 1.0, g.math('MAXIMUM', dist, 0.001)))
    cosang = g.vmath('DOT_PRODUCT', dirn, D.vec(g, 'lampD'))
    cone = g.math('MULTIPLY', g.math('SUBTRACT', cosang, 0.90), 14.0, clamp=True)
    fall = g.math('DIVIDE', 1.0, g.math('ADD', 1.0, g.math('MULTIPLY', g.math('MULTIPLY', dist, dist), 1.1)))
    beam = g.math('MULTIPLY', g.math('MULTIPLY', cone, fall), g.math('MULTIPLY', D.val(g, 'lampA'), 1.5), clamp=True)
    dl = g.vmath('DISTANCE', P, D.vec(g, 'lureP'))
    lure = g.math('MULTIPLY', g.math('EXPONENT', g.math('MULTIPLY', g.math('MULTIPLY', dl, dl), -2.6)), g.math('MULTIPLY', D.val(g, 'lureA'), 1.5), clamp=True)
    dv = g.vmath('DISTANCE', P, D.vec(g, 'ventP'))
    vent = g.math('MULTIPLY', g.math('EXPONENT', g.math('MULTIPLY', g.math('MULTIPLY', dv, dv), -2.0)), g.math('MULTIPLY', D.val(g, 'ventA'), 1.1), clamp=True)
    black = (0, 0, 0, 1)
    s = g.mix(1.0, g.mix(beam, black, srgb((1.0, 0.95, 0.76))), g.mix(lure, black, srgb((1.0, 0.82, 0.42))), 'ADD')
    return g.mix(1.0, s, g.mix(vent, black, srgb((1.0, 0.55, 0.22))), 'ADD')


def sea(kit, D, name, color, shade=0.24, tex=0.07, alpha=None, glow=0.0, glow_color=None, lamps=True, flat=False, tint=None, glow_drive=None, world=False, keep=0.0):
    """A creature or object under the sea: painted flat colour, one hard toon step from the sun, the light left at its depth,
    the water's tint, and the three story lamps. color: sRGB. glow: a constant extra emission (bright eyes, lamps)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    geo, P, d = _depth(g, D)
    tc = g.node('ShaderNodeTexCoord'); n = g.noise(tc.outputs['Object'], 11.0, 3.0)
    base = g.mix(g.math('MULTIPLY', n.outputs['Fac'], tex * 3.0, clamp=True), srgb(color), g.mix(0.28, srgb(color), (0, 0, 0, 1))) if tex else srgb(color)
    if tint is not None: base = g.mix(1.0, base, srgb(tint), 'MULTIPLY')
    key = g.vmath('DOT_PRODUCT', geo.outputs['Normal'], (-0.35, -0.45, 0.82))
    step = g.math('MULTIPLY', g.math('SUBTRACT', key, 0.05), 6.0, clamp=True)
    k = 1.0 if flat else g.math('ADD', 1.0 - shade, g.math('MULTIPLY', step, shade))
    amb = 1.0 if world else _ramp1(g, d, DEPTH_STOPS, 1); fogk = 0.0 if world else _ramp1(g, d, DEPTH_STOPS, 2)
    fogc = g.ramp(g.math('DIVIDE', d, DEEPN, clamp=True), [(s[0] / DEEPN, s[3]) for s in DEPTH_STOPS])
    if keep: amb = g.math('MAXIMUM', amb, keep); fogk = g.math('MULTIPLY', fogk, 1.0 - 0.7 * keep)
    kk = g.math('MULTIPLY', k, amb)
    lit = g.mix(1.0, base, g.comb(kk, kk, kk), 'MULTIPLY')
    col = g.mix(g.math('MULTIPLY', fogk, 0.85), lit, fogc)
    if lamps: col = g.mix(1.0, col, g.mix(1.0, base, _lamps(g, D, P), 'MULTIPLY'), 'ADD')
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    if glow > 0 and glow_color is not None:
        e2 = g.node('ShaderNodeEmission', ins={'Color': srgb(glow_color), 'Strength': glow if glow_drive is None else g.math('MULTIPLY', D.val(g, glow_drive, 0.0), glow)}); ad = g.node('ShaderNodeAddShader'); g.link(e, ad.inputs[0]); g.link(e2, ad.inputs[1]); e = ad
    if alpha: _alpha_out(g, e, D.val(g, alpha, 1.0))
    else: cw._finish(g, e)
    return m


def glow(kit, D, name, color, strength=1.0, drive=None, alpha=None, base=None):
    """Pure emission (the animals' own light, sparkles, lamps). strength is a constant times the driven Value `drive` (0..1)
    when given. Emission-only, so Fable leaves it alone, and the bloom turns the bright ones soft."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    s = strength if drive is None else g.math('MULTIPLY', D.val(g, drive, 1.0), strength)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': s})
    if alpha: _alpha_out(g, e, D.val(g, alpha, 1.0))
    else: cw._finish(g, e)
    return m


def glow_rgb(kit, D, name, color_drive, strength=1.0, init=(1, 1, 1)):
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': D.rgb(g, color_drive, init), 'Strength': strength}); cw._finish(g, e); return m


def mat_word(kit, D, name, color, alpha_name):
    """Words, plates and graphics set in code: emission with a driven alpha (Fable recolours them ink or paper)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': 1.0}); _alpha_out(g, e, D.val(g, alpha_name, 1.0)); return m


# ---------------------------------------------------------------------------------------------------- the stage
def wall(kit, D, name='fs_wallm'):
    """The back and left walls of the column: painted water from sunlit turquoise to midnight, with soft horizontal brush
    strokes, slanted sun rays that fade with depth, gold hairlines where the zones change, lit by the three lamps."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    geo, P, d = _depth(g, D); px = g.sep(P)
    tc = g.node('ShaderNodeTexCoord'); O = tc.outputs['Object']; ox = g.sep(O)
    dn = g.math('DIVIDE', d, DEEPN, clamp=True)
    stops = [(0.00, (0.46, 0.92, 0.96)), (0.12, (0.20, 0.78, 0.92)), (0.29, (0.14, 0.62, 0.90)), (0.40, (0.30, 0.42, 0.86)), (0.52, (0.34, 0.28, 0.74)), (0.62, (0.22, 0.17, 0.58)),
             (0.80, (0.10, 0.10, 0.38)), (1.0, (0.06, 0.07, 0.28))]
    col = g.ramp(dn, stops)
    hz = g.math('ADD', ox[0], ox[1])
    st = g.noise(g.comb(g.math('MULTIPLY', hz, 1.4), g.math('MULTIPLY', d, 22.0), 0.0), 1.2, 3.0, 0.6)
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.5), 0.34), col, g.mix(1.0, col, (1.2, 1.2, 1.3, 1.0), 'MULTIPLY'), 'MULTIPLY') if False else col
    tone = g.math('ADD', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.5), 0.22))
    col = g.mix(1.0, col, g.comb(tone, tone, tone), 'MULTIPLY')
    # sun rays: slanted bands, bright near the top, gone by the twilight
    sl = g.math('ADD', hz, g.math('MULTIPLY', d, 0.55))
    rays = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ABSOLUTE', g.math('SINE', g.math('MULTIPLY', sl, 5.5))), 0.55), 2.2, clamp=True)
    rays = g.math('MULTIPLY', rays, g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', dn, 2.4), clamp=True), 0.55))
    col = g.mix(rays, col, srgb((0.80, 0.98, 0.96)))
    # gold hairlines at the zone changes
    for z in W.ZONES[1:3]:
        line = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', d, z)), 120.0), clamp=True), 0.9)
        col = g.mix(line, col, srgb((0.99, 0.80, 0.36)))
    col = g.mix(1.0, col, g.mix(1.0, col, _lamps(g, D, P), 'MULTIPLY'), 'ADD')
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}); cw._finish(g, e); return m


def surface(kit, D, name='fs_topm'):
    """The column's own sea surface, seen from the side and a little above: bright turquoise with pale ripple strokes and
    glints, partly see-through so the submarine can be seen under it."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); O = tc.outputs['Object']; ox = g.sep(O)
    zoff, w = g.phase(0.5)
    rn = g.noise(g.comb(g.math('MULTIPLY', ox[0], 3.2), g.math('MULTIPLY', ox[1], 9.0), zoff), 1.0, 2.0, 0.5, '4D', w)
    strokes = g.math('MULTIPLY', g.math('SUBTRACT', rn.outputs['Fac'], 0.56), 12.0, clamp=True)
    col = g.mix(strokes, g.mix(D.val(g, 'dusk'), srgb((0.22, 0.80, 0.90)), srgb((0.94, 0.62, 0.52))), g.mix(D.val(g, 'dusk'), srgb((0.88, 1.0, 0.97)), srgb((1.0, 0.88, 0.62))))
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    _alpha_out(g, e, 0.62); return m


def sea_world(kit, D, name='fs_seam'):
    """The sunny sea out to the horizon: turquoise near, deepening a little, then haze toward the sky's own colour; long pale
    brush strokes for the swell, bright glints near the sun side; golden at the end."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); O = tc.outputs['Object']; ox = g.sep(O)
    geo = g.node('ShaderNodeNewGeometry')
    r = g.vmath('DISTANCE', geo.outputs['Position'], D.vec(g, 'camP'))
    far = g.math('DIVIDE', g.math('SUBTRACT', r, 11.0), 10.5, clamp=True)
    zoff, w = g.phase(0.4)
    # swell strokes: stretched noise along the ground, drifting
    sn = g.noise(g.comb(g.math('MULTIPLY', ox[0], 0.55), g.math('MULTIPLY', ox[1], 1.4), zoff), 1.0, 3.0, 0.55, '4D', w)
    strokes = g.math('MULTIPLY', g.math('SUBTRACT', sn.outputs['Fac'], 0.57), 9.0, clamp=True)
    day_n = srgb((0.17, 0.72, 0.84)); day_f = srgb((0.10, 0.52, 0.76)); dusk_n = srgb((0.30, 0.46, 0.66)); dusk_f = srgb((0.40, 0.40, 0.60))
    near = g.mix(D.val(g, 'dusk'), day_n, dusk_n); fari = g.mix(D.val(g, 'dusk'), day_f, dusk_f)
    col = g.mix(g.math('MULTIPLY', far, 1.6, clamp=True), near, fari)
    glint = g.mix(D.val(g, 'dusk'), srgb((0.88, 1.0, 0.98)), srgb((1.0, 0.82, 0.58)))
    col = g.mix(g.math('MULTIPLY', strokes, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', far, 0.7))), col, glint)
    col = g.mix(g.math('POWER', far, 1.3), col, D.rgb(g, 'seahaze', (0.82, 0.93, 0.92)))
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}); cw._finish(g, e); return m


def haze_wall(kit, D, name='fs_holem'):
    """The hole the slice was lifted from: deep water-blue walls, darker toward the floor."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); O = tc.outputs['Object']; oz = g.sep(O)[2]
    u = g.math('DIVIDE', g.math('SUBTRACT', oz, 0.0), -(W.DEEP + W.BASE + 0.05), clamp=True)
    col = g.ramp(u, [(0.0, (0.12, 0.62, 0.80)), (0.25, (0.08, 0.38, 0.66)), (0.6, (0.05, 0.14, 0.40)), (1.0, (0.02, 0.04, 0.14))])
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}); cw._finish(g, e); return m


def beam(kit, D, name, color, amount, peak=0.30):
    """A soft cone of light seen through the water (a cone mesh, apex at its origin, axis +Z, length 1): faint at the
    apex, fading to nothing at the far end, with a driven amount."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); z = g.sep(tc.outputs['Object'])[2]
    geo = g.node('ShaderNodeNewGeometry'); inc = g.math('ABSOLUTE', g.vmath('DOT_PRODUCT', geo.outputs['Normal'], geo.outputs['Incoming']))
    fade = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, z, clamp=True), g.math('MULTIPLY', z, 8.0, clamp=True))
    a = g.math('MULTIPLY', g.math('MULTIPLY', g.math('POWER', inc, 1.5), fade), g.math('MULTIPLY', D.val(g, amount), peak))
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color), 'Strength': 2.0}); _alpha_out(g, e, a); return m


def rays(kit, D, name='fs_raysm'):
    """Sun shafts in the sunlight zone: tall faint pale quads (Object y = along the shaft, 0 at the top)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); O = tc.outputs['Object']; ox = g.sep(O)
    u = g.math('ABSOLUTE', ox[0]); across = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', u, 2.0), clamp=True)
    along = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', ox[1], -1.0), clamp=True), 1.0)
    zoff, w = g.phase(0.3)
    sh = g.noise(g.comb(g.math('MULTIPLY', ox[0], 3.0), 0.0, zoff), 1.0, 2.0, 0.5, '4D', w)
    a = g.math('MULTIPLY', g.math('MULTIPLY', g.math('POWER', across, 1.4), along), g.math('MULTIPLY', g.math('ADD', 0.5, sh.outputs['Fac']), 0.30))
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.92, 1.0, 0.92)), 'Strength': 1.0}); _alpha_out(g, e, g.math('MULTIPLY', a, D.val(g, 'raysA', 1.0))); return m


def far_card(kit, D, hw, hh, name='fs_farm'):
    """The sea beyond the 3D sea, on a card held by the camera in front of Fable's painted backdrop: haze colour from the sea's
    edge up to a painted horizon, lighter toward the top, with long brush strokes, a faint far island and three tiny sails;
    it fades out at the top so the painted sky shows above (the hills of Fable's card are hidden behind it)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); O = tc.outputs['Object']; ox = g.sep(O)
    u = g.math('DIVIDE', ox[0], hw); v = g.math('DIVIDE', ox[1], hh)
    haze = D.rgb(g, 'seahaze', (0.70, 0.86, 0.84))
    st = g.noise(g.comb(g.math('MULTIPLY', u, 1.3), g.math('MULTIPLY', v, 30.0), 0.0), 1.5, 3.0, 0.55)
    tone = g.math('ADD', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.5), 0.10))
    light = g.mix(D.val(g, 'dusk'), srgb((0.95, 1.0, 0.98)), srgb((1.0, 0.82, 0.62)))
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', v, 0.0), 1.1, clamp=True), haze, light)
    col = g.mix(1.0, col, g.comb(tone, tone, tone), 'MULTIPLY')
    far_c = g.mix(0.45, haze, srgb((0.30, 0.50, 0.58)))
    # far island (a low dome) and sails (little triangles on a thin hull)
    du = g.math('SUBTRACT', u, -0.52); dome = g.math('MULTIPLY', g.math('SUBTRACT', g.math('MULTIPLY', 0.045, g.math('SQRT', g.math('MAXIMUM', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MULTIPLY', du, du), 1.0 / 0.0225)), 0.0))), g.math('SUBTRACT', v, 0.17)), 260.0, clamp=True)
    dome = g.math('MULTIPLY', dome, g.math('MULTIPLY', g.math('SUBTRACT', v, 0.17), 260.0, clamp=True))
    col = g.mix(g.math('MULTIPLY', dome, 0.85), col, g.mix(0.35, far_c, (0.2, 0.5, 0.35, 1.0)))
    for cu, cv, k in ((0.26, 0.205, 1.0), (0.64, 0.25, 0.8), (-0.12, 0.19, 0.7)):
        dx = g.math('ABSOLUTE', g.math('SUBTRACT', u, cu)); dy = g.math('SUBTRACT', v, cv)
        tri = g.math('MULTIPLY', g.math('MULTIPLY', g.math('MULTIPLY', dy, 300.0, clamp=True), g.math('MULTIPLY', g.math('SUBTRACT', 0.075 * k, dy), 300.0, clamp=True)),
                     g.math('MULTIPLY', g.math('SUBTRACT', g.math('MULTIPLY', 0.028 * k, g.math('SUBTRACT', 1.0, g.math('DIVIDE', dy, 0.075 * k), clamp=True)), dx), 500.0, clamp=True))
        hull = g.math('MULTIPLY', g.math('MULTIPLY', g.math('MULTIPLY', g.math('ADD', dy, 0.012), 300.0, clamp=True), g.math('MULTIPLY', g.math('SUBTRACT', 0.0, dy), 300.0, clamp=True)), g.math('MULTIPLY', g.math('SUBTRACT', 0.04 * k, dx), 400.0, clamp=True))
        col = g.mix(g.math('MULTIPLY', tri, 0.9), col, srgb((1.0, 0.99, 0.95))); col = g.mix(g.math('MULTIPLY', hull, 0.8), col, srgb((0.28, 0.40, 0.62)))
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    alpha = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', v, 0.36), 10.0, clamp=True))
    _alpha_out(g, e, alpha); return m
