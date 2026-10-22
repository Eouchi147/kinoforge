"""Four seasons loop: season-driven materials and the node patches that keep the loop seamless (bpy, built on the kit).

The kit bakes a season into its materials at build time. Here every season-dependent colour or amount is a Value, RGB or
ColorRamp node that `Drive` sets each frame from the timeline in world.py. Noise is read through coordinates that do
not change under a 90 degree turn (`inv_vec` on the top, `fold_vec` on the walls) and per-instance colour comes from a
turn-invariant function of the instance position (`inv_rand`), so the four copies of each plant look the same.
"""
import math
import cutaway as cw
from cutaway import G, srgb
import szworld as W

PI = math.pi

# ------------------------------------------------------------------ per-frame drivers
class Drive:
    def __init__(self): self.v = {}; self.c = {}; self.r = {}
    def val(self, g, name, init=0.0):
        n = g.node('ShaderNodeValue'); n.outputs[0].default_value = init; n.label = name
        self.v.setdefault(name, []).append(n.outputs[0]); return n.outputs[0]
    def rgb(self, g, name, init=(0.5, 0.5, 0.5)):
        n = g.node('ShaderNodeRGB'); n.outputs[0].default_value = srgb(init); n.label = name
        self.c.setdefault(name, []).append(n.outputs[0]); return n.outputs[0]
    def ramp(self, g, name, fac, n_stops):
        n = g.node('ShaderNodeValToRGB'); cr = n.color_ramp
        while len(cr.elements) < n_stops: cr.elements.new(0.5)
        for i, el in enumerate(cr.elements): el.position = i / (n_stops - 1)
        g.put(n, 'Fac', fac); self.r.setdefault(name, []).append(cr); return n.outputs['Color']
    def set(self, name, x):
        for s in self.v.get(name, []): s.default_value = float(x)
    def setc(self, name, c):
        for s in self.c.get(name, []): s.default_value = srgb(c)
    def setramp(self, name, cols):
        for cr in self.r.get(name, []):
            for el, c in zip(cr.elements, cols): el.color = srgb(c)

# ------------------------------------------------------------------ invariant coordinates
def inv_vec(g, pos, zscale=1.0):
    """Cone embedding: a 90 degree wedge rolled into a cone, so 3D noise read here is the same under a 90 degree turn,
    continuous everywhere and undistorted (locally isometric) except at the centre."""
    s = g.sep(pos); x, y, z = s[0], s[1], s[2]
    r = g.math('SQRT', g.math('ADD', g.math('MULTIPLY', x, x), g.math('MULTIPLY', y, y)))
    p4 = g.math('MULTIPLY', g.math('ARCTAN2', y, x), 4.0); q = g.math('MULTIPLY', r, 0.25)
    return g.comb(g.math('MULTIPLY', g.math('COSINE', p4), q), g.math('MULTIPLY', g.math('SINE', p4), q),
                  g.math('ADD', g.math('MULTIPLY', r, 0.9682), g.math('MULTIPLY', z, zscale)))

def fold_vec(g, pos):
    """Walls: turn every face onto the -Y face, so the four faces carry the same texture (seams only on the corners)."""
    s = g.sep(pos); th = g.math('ARCTAN2', s[1], s[0])
    k = g.math('FLOOR', g.math('DIVIDE', g.math('ADD', th, 3 * PI / 4), PI / 2))
    vr = g.node('ShaderNodeVectorRotate', rotation_type='Z_AXIS'); g.put(vr, 'Vector', pos); g.put(vr, 'Angle', g.math('MULTIPLY', k, -PI / 2))
    return vr.outputs['Vector']

def inv_rand(g, scale=37.0):
    """Per-instance random in 0..1 that is identical for the four turned copies (built from x*x + y*y and x*x*y*y)."""
    oi = g.node('ShaderNodeObjectInfo'); s = g.sep(oi.outputs['Location'])
    xx = g.math('MULTIPLY', s[0], s[0]); yy = g.math('MULTIPLY', s[1], s[1])
    v = g.comb(g.math('MULTIPLY', g.math('ADD', xx, yy), 3.1), g.math('MULTIPLY', g.math('MULTIPLY', xx, yy), 5.3), g.math('MULTIPLY', s[2], 7.0))
    n = g.noise(v, scale, 0.0, 0.5)
    return g.math('MULTIPLY_ADD', g.math('SUBTRACT', n.outputs['Fac'], 0.5), 2.6, 0.5, clamp=True)

def _principled(nt):
    return next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')

def _base_src(g, p, key='Base Color'):
    s = p.inputs[key]
    if s.is_linked: src = s.links[0].from_socket; g.t.links.remove(s.links[0]); return src
    return tuple(s.default_value)

def patch_random(mat):
    """Replace Object Info Random (differs between the four copies) with inv_rand."""
    nt = mat.node_tree; g = G(nt); links = [l for l in nt.links if l.from_node.bl_idname == 'ShaderNodeObjectInfo' and l.from_socket.name == 'Random']
    if not links: return
    r = inv_rand(g)
    for l in links:
        to = l.to_socket; nt.links.remove(l); nt.links.new(r, to)

def patch_snow(mat, D, kit, up=0.55, tint=None):
    """Snow on the upward faces (amount driven by 'snow'); optional seasonal colour tint (driven RGB `tint`)."""
    nt = mat.node_tree; g = G(nt, kit); p = _principled(nt); col = _base_src(g, p)
    if tint: col = g.mix(1.0, col, D.rgb(g, tint, (1, 1, 1)), 'MULTIPLY')
    geo = g.node('ShaderNodeNewGeometry'); nz = g.sep(geo.outputs['Normal'])[2]
    tc = g.node('ShaderNodeTexCoord'); n = g.noise(tc.outputs['Object'], 14.0, 2.0)
    m = g.math('MULTIPLY', g.math('SUBTRACT', nz, up), 5.0, clamp=True)
    a = g.math('MULTIPLY', g.math('ADD', g.math('MULTIPLY', D.val(g, 'snow'), 1.4), g.math('SUBTRACT', n.outputs['Fac'], 0.85)), 5.0, clamp=True)
    col = g.mix(g.math('MULTIPLY', m, a), col, srgb((0.92, 0.94, 0.97)))
    g.put(p, 'Base Color', col)

# ------------------------------------------------------------------ materials
def mat_top(kit, D):
    m = cw._new_mat(kit.bpy, 'sz_top'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; geo = g.node('ShaderNodeNewGeometry'); P = inv_vec(g, pos)
    wg = g.attr('wg').outputs['Fac']; ws = g.attr('ws').outputs['Fac']
    n_big = g.noise(P, 1.6, 3.0); n_mid = g.noise(P, 8.0, 4.0); n_fine = g.noise(P, 45.0, 4.0)
    dirt = g.mix(n_mid.outputs['Fac'], srgb((0.24, 0.17, 0.11)), srgb((0.38, 0.28, 0.18)))
    ground = g.mix(n_big.outputs['Fac'], D.rgb(g, 'ground'), D.rgb(g, 'ground2'))
    ground = g.mix(g.math('MULTIPLY', n_fine.outputs['Fac'], 0.6), ground, g.mix(0.6, ground, (0, 0, 0), 'MULTIPLY'))
    sand = g.mix(n_fine.outputs['Fac'], srgb((0.72, 0.64, 0.50)), srgb((0.84, 0.78, 0.64)))
    col = g.mix(ws, dirt, sand); col = g.mix(wg, col, ground)
    # autumn litter on the grass: warm speckles
    nl = g.noise(P, 30.0, 2.0); lit = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', nl.outputs['Fac'], g.math('MULTIPLY', D.val(g, 'litter'), 0.45)), 0.85), 9.0, clamp=True), wg)
    lcol = g.mix(n_mid.outputs['Fac'], srgb((0.74, 0.36, 0.10)), srgb((0.80, 0.58, 0.18)))
    col = g.mix(g.math('MULTIPLY', lit, 0.8), col, lcol)
    z = g.sep(pos)[2]
    wetb = g.math('MULTIPLY', g.math('SUBTRACT', W.LV + 0.025, z), 40.0, clamp=True)
    band = g.math('MULTIPLY', wetb, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', W.LV, z), 25.0, clamp=True)))
    col = g.mix(g.math('MULTIPLY', band, 0.45), col, (0, 0, 0))
    under = g.math('MULTIPLY', g.math('SUBTRACT', W.LV, z), 30.0, clamp=True)
    bed = g.mix(n_mid.outputs['Fac'], D.rgb(g, 'bedA'), D.rgb(g, 'bedB'))
    col = g.mix(g.math('MULTIPLY', under, 0.85), col, bed)
    # caustics (looping, read through the invariant coordinates; faded at the cone apex in the pool centre)
    zoff, w = g.phase(0.25); Pc = g.vmath('ADD', P, g.comb(0.0, 0.0, zoff))
    v1 = g.voronoi(Pc, 7.0, 'DISTANCE_TO_EDGE', '4D', w); v2 = g.voronoi(g.vmath('SCALE', Pc, scale=1.37), 9.0, 'DISTANCE_TO_EDGE', '4D', g.math('MULTIPLY', w, 1.3))
    c1 = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', v1.outputs['Distance'], 9.0), clamp=True)
    c2 = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', v2.outputs['Distance'], 11.0), clamp=True)
    c = g.math('POWER', g.math('MAXIMUM', c1, c2), 2.0); d = g.math('SUBTRACT', W.LV, z)
    rr = g.math('SQRT', g.math('ADD', g.math('POWER', g.sep(pos)[0], 2.0), g.math('POWER', g.sep(pos)[1], 2.0)))
    apex = g.math('MULTIPLY', g.math('SUBTRACT', rr, 0.08), 4.0, clamp=True)
    ca = g.math('MULTIPLY', g.math('MULTIPLY', c, g.math('MULTIPLY', g.math('MULTIPLY', d, 60.0, clamp=True), g.math('EXPONENT', g.math('MULTIPLY', d, -2.0)))),
                g.math('MULTIPLY', D.val(g, 'caus', 1.0), g.math('MULTIPLY', apex, 1.6)))
    col = g.mix(ca, col, g.mix(0.5, col, (1.0, 1.0, 0.95), 'SCREEN'))
    col = g.mix(g.math('MINIMUM', g.math('MULTIPLY', ca, 0.6), 1.0), col, g.mix(1.0, col, (1.6, 1.6, 1.5), 'MULTIPLY'))
    # meltwater: the thawed ground is dark and glossy for a moment
    wet = g.math('MULTIPLY', D.val(g, 'wet'), g.math('SUBTRACT', 1.0, under))
    col = g.mix(g.math('MULTIPLY', wet, 0.45), col, g.mix(1.0, col, srgb((0.45, 0.45, 0.45)), 'MULTIPLY'))
    # snow: settles on the upward ground, patchy first, then covering
    nz = g.sep(geo.outputs['Normal'])[2]; up = g.math('MULTIPLY', g.math('SUBTRACT', nz, 0.5), 4.0, clamp=True)
    amt = g.math('MULTIPLY', g.math('ADD', g.math('MULTIPLY', D.val(g, 'snow'), 1.45), g.math('MULTIPLY', g.math('SUBTRACT', n_mid.outputs['Fac'], 0.5), 0.9)), 1.0)
    sm = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', amt, 0.45), 6.0, clamp=True), g.math('MULTIPLY', up, g.math('SUBTRACT', 1.0, under)))
    snowc = g.mix(n_fine.outputs['Fac'], srgb((0.86, 0.89, 0.95)), srgb((0.96, 0.97, 0.99)))
    col = g.mix(sm, col, snowc)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col})
    rough = g.math('SUBTRACT', g.math('SUBTRACT', 0.85, g.math('MULTIPLY', wetb, 0.6)), g.math('MULTIPLY', wet, 0.45)); g.put(p, 'Roughness', rough)
    b = g.node('ShaderNodeBump', ins={'Strength': 0.45, 'Height': g.math('MULTIPLY', n_fine.outputs['Fac'], 0.5), 'Distance': 0.01}); g.put(p, 'Normal', b)
    cw._finish(g, p); return m

def mat_strata(kit, D, layers, burrow):
    """Cross-section walls (as the kit's, read through fold_vec), plus: a snow cap, fine roots that grow in spring,
    and the frog's chamber cut into the mud under each cove (a hole that opens to the cavity behind it)."""
    m = cw._new_mat(kit.bpy, 'sz_strata'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = fold_vec(g, tc.outputs['Object']); sx = g.sep(pos)
    sd = g.attr('sd').outputs['Fac']; dtop = g.attr('dtop').outputs['Fac']
    hz = sx[0]
    wob = g.noise(g.comb(hz, 0.0, g.math('MULTIPLY', sd, 0.2)), 2.2, 3.0)
    s = g.math('ADD', sd, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.07))
    total = sum(l[1] for l in layers[:-1]) + 0.6; stops = []; pstops = []; acc = 0.0; soft = 0.012
    for k, l in enumerate(layers):
        a = acc / total; b = min(1.0, (acc + l[1]) / total) if k < len(layers) - 1 else 1.0
        stops += [(min(1, a + soft / total) if k else 0.0, l[2]), (max(0.0, b - soft / total) if k < len(layers) - 1 else 1.0, tuple(c * 0.9 for c in l[2]))]
        pstops += [(a, (l[3],) * 3)]; acc += l[1]
    fac = g.math('DIVIDE', s, total)
    col = g.ramp(fac, stops); pden = g.sep(g.ramp(fac, pstops, 'CONSTANT'))[0]
    n1 = g.noise(pos, 60.0, 5.0, 0.6); n2 = g.noise(g.comb(hz, g.math('MULTIPLY', sx[2], 6.0), 0.0), 3.0, 4.0)
    col = g.mix(g.math('MULTIPLY', n1.outputs['Fac'], 0.45), col, g.mix(0.55, col, (0, 0, 0), 'MULTIPLY'))
    col = g.mix(g.math('MULTIPLY', n2.outputs['Fac'], 0.25), col, g.mix(0.5, col, (1, 1, 1), 'SCREEN'))
    vp = g.voronoi(pos, 34.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    radius = g.math('MULTIPLY', g.math('MULTIPLY', pden, 0.42), g.math('MULTIPLY_ADD', rr[0], 0.8, 0.4))
    peb = g.math('MULTIPLY', g.math('SUBTRACT', radius, vp.outputs['Distance']), 25.0, clamp=True)
    pcol = g.mix(rr[1], srgb((0.42, 0.40, 0.37)), srgb((0.78, 0.74, 0.66)))
    pcol = g.mix(g.math('MULTIPLY', rr[2], 0.5), pcol, srgb((0.62, 0.46, 0.32)))
    col = g.mix(peb, col, pcol)
    u = g.math('ADD', g.math('MULTIPLY', hz, 22.0), g.math('MULTIPLY', g.noise(g.comb(hz, sx[2], 0.0), 6.0, 2.0).outputs['Fac'], 3.0))
    lane = g.math('FLOOR', u); fr = g.math('FRACT', u)
    wn = g.node('ShaderNodeTexWhiteNoise', noise_dimensions='1D'); g.put(wn, 'W', lane)
    rlen = g.math('MULTIPLY', g.math('MULTIPLY', wn.outputs['Value'], 0.32), D.val(g, 'roots', 1.0))
    line = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', fr, 0.5)), 16.0), clamp=True)
    taper = g.math('MULTIPLY', g.math('SUBTRACT', rlen, dtop), 20.0, clamp=True)
    root = g.math('MULTIPLY', g.math('MULTIPLY', line, taper), g.math('GREATER_THAN', wn.outputs['Value'], 0.35))
    col = g.mix(g.math('MULTIPLY', root, 0.85), col, srgb((0.12, 0.08, 0.05)))
    wt = g.math('MULTIPLY', g.math('SUBTRACT', W.LV - 0.04, g.math('ADD', sx[2], g.math('MULTIPLY', wob.outputs['Fac'], 0.06))), 8.0, clamp=True)
    col = g.mix(g.math('MULTIPLY', wt, 0.38), col, g.mix(1.0, col, srgb((0.55, 0.58, 0.62)), 'MULTIPLY'))
    top_dark = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', dtop, 30.0), clamp=True)
    col = g.mix(g.math('MULTIPLY', top_dark, 0.5), col, srgb((0.10, 0.08, 0.05)))
    # snow cap on the cut edge (dry land only: the cove edges are under water)
    cap = g.math('MULTIPLY', g.math('SUBTRACT', g.math('MULTIPLY', D.val(g, 'snow'), 0.024), dtop), 600.0, clamp=True)
    cap = g.math('MULTIPLY', cap, g.math('GREATER_THAN', sx[2], W.LV + 0.006))
    col = g.mix(cap, col, srgb((0.92, 0.94, 0.97)))
    # the frog's chamber: an ellipse plus a narrow tunnel up to the bed; edges darkened
    bx, bz, rx, rz, bed_z = burrow
    ex = g.math('DIVIDE', g.math('SUBTRACT', sx[0], bx), rx); ez = g.math('DIVIDE', g.math('SUBTRACT', sx[2], bz), rz)
    e = g.math('SQRT', g.math('ADD', g.math('MULTIPLY', ex, ex), g.math('MULTIPLY', ez, ez)))
    op = D.val(g, 'burrow'); tn = D.val(g, 'tunnel')
    hole = g.math('LESS_THAN', e, g.math('MULTIPLY', op, 1.0))
    slot = g.math('MULTIPLY', g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', sx[0], bx)), g.math('MULTIPLY', tn, 0.024)),
                  g.math('MULTIPLY', g.math('GREATER_THAN', sx[2], bz), g.math('LESS_THAN', sx[2], bed_z + 0.004)))
    cut = g.math('MAXIMUM', hole, slot)
    rim = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', e, g.math('MULTIPLY', op, 1.0))), 9.0), clamp=True), g.math('GREATER_THAN', op, 0.05))
    col = g.mix(g.math('MULTIPLY', rim, 0.55), col, srgb((0.10, 0.07, 0.05)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.92})
    h = g.math('ADD', g.math('MULTIPLY', n1.outputs['Fac'], 0.3), g.math('ADD', g.math('MULTIPLY', peb, 0.8), g.math('MULTIPLY', root, 0.4)))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.45, 'Height': h, 'Distance': 0.006}); g.put(p, 'Normal', b)
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(cut, mx.inputs[0]); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2])
    cw._finish(g, mx); return m

def mat_water(kit, D):
    m = cw._new_mat(kit.bpy, 'sz_water'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry'); P = inv_vec(g, tc.outputs['Object'])
    zoff, w = g.phase(0.45); p = g.vmath('ADD', P, g.comb(0.0, 0.0, zoff))
    r1 = g.noise(p, 9.0, 3.0, 0.55, '4D', w); r2 = g.noise(g.vmath('SCALE', p, scale=2.7), 9.0, 2.0, 0.5, '4D', g.math('MULTIPLY', w, 1.6))
    hgt = g.math('ADD', r1.outputs['Fac'], g.math('MULTIPLY', r2.outputs['Fac'], 0.45))
    topmask = g.math('GREATER_THAN', g.sep(geo.outputs['Normal'])[2], 0.7)
    bump = g.node('ShaderNodeBump', ins={'Strength': g.math('MULTIPLY', topmask, 0.18), 'Height': hgt, 'Distance': 0.02})
    glass = g.node('ShaderNodeBsdfGlass', ins={'Color': (1, 1, 1), 'Roughness': 0.015, 'IOR': 1.33}, distribution='GGX'); g.put(glass, 'Normal', bump)
    tr = g.node('ShaderNodeBsdfTransparent'); lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Shadow Ray'], mx.inputs[0]); g.link(glass, mx.inputs[1]); g.link(tr, mx.inputs[2])
    vol = g.node('ShaderNodeVolumeAbsorption'); g.put(vol, 'Color', D.rgb(g, 'wtint', (0.2, 0.78, 0.74))); g.put(vol, 'Density', D.val(g, 'wdens', 3.2))
    cw._finish(g, mx, vol); return m

def mat_ice(kit, D):
    """Pond ice: frosted and pale, present where the freeze front has reached (from the banks inwards), cracked, with
    snow dusting the top. Transparent where not frozen."""
    m = cw._new_mat(kit.bpy, 'sz_ice'); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); P = inv_vec(g, tc.outputs['Object']); geo = g.node('ShaderNodeNewGeometry')
    sd = g.attr('sdw').outputs['Fac']; n = g.noise(P, 6.0, 3.0)
    front = g.math('ADD', g.math('MULTIPLY', D.val(g, 'ice'), 0.95), g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.5), 0.18))
    a = g.math('MULTIPLY', g.math('ADD', sd, g.math('SUBTRACT', front, 0.02)), 60.0, clamp=True)
    a = g.math('MULTIPLY', a, g.math('MULTIPLY', D.val(g, 'ice'), 30.0, clamp=True))
    vo = g.voronoi(P, 9.0, 'DISTANCE_TO_EDGE'); crack = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 40.0), clamp=True)
    col = g.mix(n.outputs['Fac'], srgb((0.70, 0.84, 0.92)), srgb((0.88, 0.94, 0.98)))
    col = g.mix(g.math('MULTIPLY', crack, 0.6), col, srgb((0.97, 0.99, 1.0)))
    nz = g.sep(geo.outputs['Normal'])[2]
    sn = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', g.math('MULTIPLY', D.val(g, 'snow'), 1.2), n.outputs['Fac']), 1.15), 6.0, clamp=True),
                g.math('GREATER_THAN', nz, 0.7))
    col = g.mix(sn, col, srgb((0.95, 0.96, 0.99)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.22, 'Subsurface Weight': 0.2})
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(g.math('MULTIPLY', a, 0.93), mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(p, mx.inputs[2])
    cw._finish(g, mx); return m

def mat_grass(kit, D, height):
    m = cw._new_mat(kit.bpy, 'sz_grass'); g = G(m.node_tree, kit)
    col = D.ramp(g, 'grass', inv_rand(g), 5)
    tc = g.node('ShaderNodeTexCoord'); z = g.sep(tc.outputs['Object'])[2]; f = g.math('MULTIPLY', z, 1.0 / height, clamp=True)
    col = g.mix(g.math('POWER', f, 1.6), g.mix(0.55, col, (0.02, 0.05, 0.01), 'MULTIPLY'), g.mix(0.5, col, D.rgb(g, 'gtip')))
    col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', D.val(g, 'snow'), 0.55), f), col, srgb((0.93, 0.95, 0.98)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.6})
    tr = g.node('ShaderNodeBsdfTranslucent', ins={'Color': col}); mx = g.node('ShaderNodeMixShader')
    g.put(mx, 0, 0.3); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2]); cw._finish(g, mx); return m

def mat_leaf(kit, D, evergreen=False):
    """Leaf masses: seasonal palette per tree, blossom in spring, thinning canopy (cut out by a density threshold),
    snow on top. The evergreen version keeps its needles."""
    m = cw._new_mat(kit.bpy, 'sz_needles' if evergreen else 'sz_leaf'); g = G(m.node_tree, kit)
    oc = g.node('ShaderNodeTexCoord').outputs['Object']; rnd = inv_rand(g)
    if evergreen: col = g.ramp(rnd, [(0, (0.12, 0.26, 0.12)), (0.5, (0.16, 0.32, 0.14)), (1, (0.10, 0.22, 0.11))])
    else: col = D.ramp(g, 'leaf', g.math('MULTIPLY_ADD', g.noise(oc, 7.0, 2.0).outputs['Fac'], 0.6, g.math('MULTIPLY', rnd, 0.7)), 5)
    vo = g.voronoi(oc, 70.0, 'F1'); nn = g.noise(oc, 9.0, 3.0)
    shade = g.math('MULTIPLY_ADD', vo.outputs['Distance'], 0.9, 0.35)
    col = g.mix(g.math('SUBTRACT', 1.0, shade, clamp=True), col, g.mix(0.7, col, (0, 0, 0), 'MULTIPLY'))
    col = g.mix(g.math('MULTIPLY', nn.outputs['Fac'], 0.4), col, g.mix(0.35, col, srgb((0.9, 0.95, 0.5)), 'MIX'))
    if not evergreen:
        nb = g.noise(oc, 16.0, 2.0)
        bl = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', nb.outputs['Fac'], 0.42), 7.0, clamp=True), D.val(g, 'bloss'))
        pink = g.mix(g.sep(vo.outputs['Color'])[0], srgb((0.97, 0.74, 0.84)), srgb((0.99, 0.95, 0.94)))
        col = g.mix(bl, col, pink)
    geo = g.node('ShaderNodeNewGeometry'); nz = g.sep(geo.outputs['Normal'])[2]
    sn = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', nz, 0.35), 4.0, clamp=True), g.math('MULTIPLY', D.val(g, 'snow'), 1.2, clamp=True))
    col = g.mix(sn, col, srgb((0.93, 0.95, 0.98)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.65})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.6, 'Height': vo.outputs['Distance'], 'Distance': 0.01}); g.put(p, 'Normal', b)
    tr = g.node('ShaderNodeBsdfTranslucent', ins={'Color': col}); mx = g.node('ShaderNodeMixShader')
    g.put(mx, 0, 0.22); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2]); out = mx
    if not evergreen:
        thr = g.math('ADD', g.math('MULTIPLY', g.noise(oc, 9.0, 1.0).outputs['Fac'], 0.75), g.math('MULTIPLY', rnd, 0.25))
        keep = g.math('MULTIPLY', g.math('ADD', g.math('SUBTRACT', g.math('MULTIPLY', D.val(g, 'dens', 1.0), 0.95), thr), 0.32), 14.0, clamp=True)
        t2 = g.node('ShaderNodeBsdfTransparent'); m2 = g.node('ShaderNodeMixShader')
        g.link(keep, m2.inputs[0]); g.link(t2, m2.inputs[1]); g.link(mx, m2.inputs[2]); out = m2
    cw._finish(g, out); return m

def mat_bark(kit, D, color, name):
    m = cw.mat_simple(kit, name, color, 0.85, noise_amt=0.3, bump=0.3); patch_snow(m, D, kit, up=0.45); return m

def mat_frog(kit):
    m = cw._new_mat(kit.bpy, 'sz_frog'); g = G(m.node_tree, kit)
    oc = g.node('ShaderNodeTexCoord').outputs['Object']; z = g.sep(oc)[2]
    vo = g.voronoi(oc, 70.0, 'F1'); spot = g.math('LESS_THAN', vo.outputs['Distance'], 0.22)
    top = g.mix(g.noise(oc, 40.0, 3.0).outputs['Fac'], srgb((0.24, 0.42, 0.12)), srgb((0.40, 0.56, 0.18)))
    top = g.mix(g.math('MULTIPLY', spot, 0.7), top, srgb((0.10, 0.16, 0.06)))
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', 0.016, z), 120.0, clamp=True), top, srgb((0.86, 0.82, 0.52)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.35, 'Subsurface Weight': 0.15}); cw._finish(g, p); return m

def mat_leafbits(kit):
    """The falling leaves: colour per leaf from attribute lc, darkening with attribute decay."""
    m = cw._new_mat(kit.bpy, 'sz_fallen'); g = G(m.node_tree, kit)
    lc = g.attr('lc').outputs['Fac']; dc = g.attr('decay').outputs['Fac']
    col = g.ramp(lc, [(0.0, (0.86, 0.38, 0.08)), (0.3, (0.92, 0.62, 0.14)), (0.55, (0.70, 0.20, 0.07)), (0.8, (0.95, 0.78, 0.22)), (1.0, (0.58, 0.40, 0.14))])
    col = g.mix(dc, col, srgb((0.22, 0.15, 0.08)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.55})
    tr = g.node('ShaderNodeBsdfTranslucent', ins={'Color': col}); mx = g.node('ShaderNodeMixShader')
    g.put(mx, 0, 0.3); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2]); cw._finish(g, mx); return m

def patch_wind(kit):
    """The kit's wind reads point positions; feed it turn-invariant coordinates so the four copies sway alike."""
    bpy = kit.bpy; ng = bpy.data.node_groups.get('cw_sway')
    if ng is None or ng.get('sz_inv'): return
    posn = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeInputPosition']
    links = [l for l in ng.links if l.from_node in posn]
    g = G(ng, kit); src = posn[0].outputs[0]; s = g.sep(src); x, y, z = s[0], s[1], s[2]
    r = g.math('SQRT', g.math('ADD', g.math('MULTIPLY', x, x), g.math('MULTIPLY', y, y)))
    p4 = g.math('MULTIPLY', g.math('ARCTAN2', y, x), 4.0); q = g.math('MULTIPLY', r, 0.5)
    v = g.comb(g.math('MULTIPLY', g.math('COSINE', p4), q), g.math('MULTIPLY', g.math('SINE', p4), q), z)
    for l in links:
        to = l.to_socket; ng.links.remove(l); ng.links.new(v, to)
    ng['sz_inv'] = 1
