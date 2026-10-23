"""Cutaway art direction `fable`: a mid-century storybook painting (hand-painted background art in gouache).

The look: the same block of land, painted rather than rendered. A jewel palette (deep teal, emerald, gold, coral,
midnight blue); a painted gradient sky from midnight to teal to coral and gold, with a large soft sun ringed by painted
halos and long flat cloud streaks; layered hills as flat silhouettes on the horizon with tiny spire trees; the trees
replaced by tall decorative forms (spires, tiered crowns, ovals) with fine vertical striations and a gold rim on the sun
side, a few in coral blossom; the cut faces painted as flat jewel bands, darker at the foot of each band, divided by fine
gold lines, pebbles as flat dots, gold flecks like stars in the deep layers; the water a flat translucent teal with gold
glints and painted ripple lines. Shading is flat paint (emission) plus one hard toon terminator from the low sun, soft
contact shadows (ambient occlusion) and cool shadow colour; the compositor turns the render into brushwork (anisotropic
Kuwahara), lays a paper grain and a soft glow, then sets the words (crisp, in their own view layer, on cream plates).
Inspired by the feel of 1950s hand-painted animation backgrounds; no character, logo or name of any studio.

What it changes: every material of the set (paint shaders), the world (painted sky and hills), the floor, the trees
(kit trees hidden, new stylised trees at the same spots, swaying gently), the lights (sun softened, fill, rim and edge
spills off, museum spots halved), view transform Standard, the compositor (brushwork, grain, glow, vignette), the words'
colours (midnight ink on cream). Animals, eggs, houses, mill and bridge keep their shapes and are repainted.

Render cost vs the reference: cheaper. Mostly emission with few bounces (3), no glass refraction, no world lighting:
about 0.6 to 0.8 times the reference per frame on the same machine, plus about 1 to 3 s of compositing at 1280x720.
"""
import importlib.util
import math
import os

import numpy as np

_s = importlib.util.spec_from_file_location('kf_art__jewel', os.path.join(os.path.dirname(os.path.abspath(__file__)), '_jewel.py'))
J = importlib.util.module_from_spec(_s); _s.loader.exec_module(J)
lin = J.lin

# ---------------------------------------------------------------------------------------------- palette (sRGB)
MIDNIGHT = (0.07, 0.10, 0.25)
DEEP_TEAL = (0.04, 0.27, 0.31)
TEAL = (0.10, 0.45, 0.47)
EMERALD = (0.07, 0.44, 0.30)
DARK_EMERALD = (0.03, 0.24, 0.19)
JADE = (0.40, 0.70, 0.47)
GOLD = (0.96, 0.74, 0.30)
PALE_GOLD = (1.00, 0.89, 0.60)
CORAL = (0.95, 0.47, 0.38)
DEEP_CORAL = (0.72, 0.26, 0.27)
PLUM = (0.34, 0.14, 0.26)
CREAM = (0.99, 0.93, 0.80)
INK = (0.08, 0.10, 0.22)

# the 'time' strata (topsoil to bedrock) as jewel bands: warm near the turf, cooling to midnight at the bottom
STRATA_PAINT = {'topsoil': PLUM, 'sand': (0.95, 0.72, 0.36), 'clay': CORAL, 'loam': DEEP_CORAL, 'gravel': (0.20, 0.40, 0.42),
                'ochre': GOLD, 'limestone': (0.12, 0.40, 0.42), 'bedrock': MIDNIGHT, 'pale': PALE_GOLD, 'deep': MIDNIGHT,
                'chalk': (0.70, 0.84, 0.74), 'marl': (0.30, 0.56, 0.50), 'rock': (0.12, 0.30, 0.40), 'rust': DEEP_CORAL,
                'band': GOLD, 'red': CORAL, 'silt': (0.30, 0.50, 0.48), 'mud': DEEP_TEAL}
FALLBACK = [PLUM, (0.95, 0.72, 0.36), CORAL, DEEP_CORAL, GOLD, TEAL, DEEP_TEAL, MIDNIGHT]

# named kit materials repainted with a fixed jewel colour (the rest keep their own colour, saturated a little)
RECOLOR = {'cw_wall': CREAM, 'cw_roof': DEEP_CORAL, 'cw_door': PLUM, 'cw_millwood': (0.50, 0.26, 0.22), 'cw_bridgewood': (0.58, 0.30, 0.24),
           'cw_rock_mat': (0.36, 0.52, 0.56), 'cw_bankrock_mat': (0.50, 0.62, 0.62), 'cw_pebble_mat': (0.30, 0.50, 0.52),
           'cw_bottom': MIDNIGHT, 'cw_iron': INK, 'cw_bark': PLUM, 'cw_stem': DARK_EMERALD, 'cw_reed': (0.16, 0.48, 0.34),
           'cw_cattail': DEEP_CORAL, 'cw_lily': (0.10, 0.50, 0.36), 'cw_lilyflower': (1.0, 0.80, 0.82), 'cw_weed': (0.10, 0.44, 0.36),
           'cw_bird': INK, 'ex_cavity': (0.20, 0.08, 0.16), 'ex_dig': (0.10, 0.20, 0.30), 'ex_soil': PLUM, 'ex_terracotta': CORAL,
           'ex_chestwood': (0.48, 0.20, 0.18), 'ex_bone': (0.98, 0.92, 0.78), 'ex_trilo': (0.98, 0.84, 0.62), 'ex_nacre': (0.98, 0.86, 0.74),
           'ex_masonry': (0.70, 0.62, 0.66), 'ex_wellstone': (0.74, 0.66, 0.70), 'ex_wellroof': DEEP_CORAL, 'ex_wellwood': (0.50, 0.26, 0.22),
           'ex_deercoat': (0.86, 0.50, 0.30), 'ex_foxred': (0.96, 0.44, 0.20), 'ex_herongrey': (0.70, 0.78, 0.86), 'ex_molefur': (0.22, 0.16, 0.30),
           'ex_spines': (0.40, 0.24, 0.24), 'ex_straw': GOLD, 'ex_quartz': (0.92, 0.90, 0.96)}


def _key(name):
    return name.split('.')[0]


# ---------------------------------------------------------------------------------------------- the paint shader
class Paint:
    """Flat paint: emission in a cool shadow colour + a hard toon terminator from the sun + contact shadow + gouache mottle."""
    def __init__(self, cw, kit):
        self.cw = cw; self.kit = kit

    def shader(self, g, col, amb=0.60, lit=0.55, ao=0.05, tex=0.07, tex_scale=22.0, rim=0.0, cool=(0.62, 0.72, 0.98)):
        tc = g.node('ShaderNodeTexCoord')
        n = g.noise(tc.outputs['Object'], tex_scale, 3.0, 0.55); n2 = g.noise(tc.outputs['Object'], tex_scale * 0.18, 2.0, 0.5)
        m = g.math('ADD', g.math('MULTIPLY_ADD', n.outputs['Fac'], 2 * tex, 1 - tex), g.math('MULTIPLY', g.math('SUBTRACT', n2.outputs['Fac'], 0.5), tex))
        col = g.mix(1.0, col, m, 'MULTIPLY')
        shadow = g.mix(1.0, col, cool + (1.0,), 'MULTIPLY')
        a = g.node('ShaderNodeAmbientOcclusion', ins={'Distance': ao}); a.samples = 8
        occl = g.math('MULTIPLY_ADD', a.outputs['AO'], 0.55, 0.45)
        e = g.node('ShaderNodeEmission', ins={'Color': g.mix(1.0, shadow, occl, 'MULTIPLY'), 'Strength': amb})
        warm = tuple(lit * c for c in lin((1.0, 0.90, 0.74))[:3]) + (1.0,)
        t = g.node('ShaderNodeBsdfToon', ins={'Color': g.mix(1.0, col, warm, 'MULTIPLY'), 'Size': 0.62, 'Smooth': 0.04})
        t.component = 'DIFFUSE'
        ad = g.node('ShaderNodeAddShader'); g.link(e, ad.inputs[0]); g.link(t, ad.inputs[1])
        if rim > 0:
            lw = g.node('ShaderNodeLayerWeight', ins={'Blend': 0.35})
            r = g.math('POWER', lw.outputs['Facing'], 3.0)
            re = g.node('ShaderNodeEmission', ins={'Color': lin(PALE_GOLD), 'Strength': g.math('MULTIPLY', r, rim)})
            a2 = g.node('ShaderNodeAddShader'); g.link(ad, a2.inputs[0]); g.link(re, a2.inputs[1]); ad = a2
        return ad

    def material(self, name, col, **kw):
        cw = self.cw; m = cw._new_mat(self.kit.bpy, name); g = cw.G(m.node_tree, self.kit)
        sh = self.shader(g, lin(col) if isinstance(col, tuple) and len(col) == 3 else col, **kw); cw._finish(g, sh); return m

    def convert(self, mat, override=None, sat=1.25, **kw):
        """Rebuild a kit material in paint, from its own base colour (or an override colour)."""
        cw = self.cw; g = cw.G(mat.node_tree, self.kit)
        if override is not None: col = lin(override)
        else:
            sock, val = J.base_color(mat)
            if sock is None and val is None: return False
            col = sock if sock is not None else val
            hs = g.node('ShaderNodeHueSaturation', ins={'Saturation': sat, 'Value': 1.0, 'Color': col}); col = hs.outputs['Color']
        J.set_surface(mat, self.shader(g, col, **kw)); return True


# ---------------------------------------------------------------------------------------------- world: sky and hills
def _sky(bpy, cw, kit, sd):
    wd = bpy.data.worlds.new('fable_world')
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree; nt.nodes.clear(); g = cw.G(nt, kit)
    tc = g.node('ShaderNodeTexCoord'); d = g.vmath('NORMALIZE', tc.outputs['Generated']); dx, dy, dz = g.sep(d)
    el = g.math('ARCSINE', dz); az = g.math('ARCTAN2', dy, dx)
    sdh = np.array([sd[0], sd[1], 0.0]); sdh /= max(1e-6, np.linalg.norm(sdh))
    hd = g.math('MAXIMUM', g.vmath('DOT_PRODUCT', g.vmath('NORMALIZE', g.comb(dx, dy, 0.0)), tuple(sdh)), 0.0)
    toward = g.math('POWER', hd, 2.0)
    e = g.math('DIVIDE', g.math('MAXIMUM', el, 0.0), math.pi / 2)
    sun_side = g.ramp(e, [(0.0, PALE_GOLD), (0.035, (1.0, 0.76, 0.46)), (0.10, CORAL), (0.22, (0.62, 0.34, 0.46)),
                          (0.36, (0.20, 0.36, 0.50)), (0.62, (0.09, 0.20, 0.38)), (1.0, MIDNIGHT)])
    away = g.ramp(e, [(0.0, (0.96, 0.62, 0.52)), (0.06, (0.80, 0.46, 0.50)), (0.18, (0.38, 0.38, 0.56)), (0.34, (0.12, 0.34, 0.46)),
                      (0.60, (0.07, 0.18, 0.36)), (1.0, MIDNIGHT)])
    col = g.mix(toward, away, sun_side)
    # brushed sky: long horizontal strokes, very low contrast
    st = g.noise(g.comb(g.math('MULTIPLY', az, 2.0), g.math('MULTIPLY', el, 38.0), 0.0), 2.5, 4.0, 0.6)
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.5), 0.16), col, lin(PALE_GOLD), 'OVERLAY')
    # long flat cloud streaks (coral, a gold lower lip toward the sun)
    cn = g.noise(g.comb(g.math('MULTIPLY', az, 1.6), g.math('MULTIPLY', el, 22.0), 3.0), 1.4, 2.0, 0.45)
    band = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', el, 0.05), 30.0, clamp=True), g.math('MULTIPLY', g.math('SUBTRACT', 0.36, el), 12.0, clamp=True))
    cl = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', cn.outputs['Fac'], 0.60), 60.0, clamp=True), band)
    lip = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', cn.outputs['Fac'], 0.57), 60.0, clamp=True), band)
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', lip, cl, clamp=True), g.math('ADD', 0.35, toward)), col, lin(PALE_GOLD))
    col = g.mix(g.math('MULTIPLY', cl, 0.92), col, g.mix(toward, lin((0.86, 0.50, 0.58)), lin((0.98, 0.62, 0.50))))
    # the sun: a large soft disc with painted halo rings
    ang = g.math('ARCCOSINE', g.math('MINIMUM', g.vmath('DOT_PRODUCT', d, tuple(sd)), 1.0))
    r0 = 0.085
    disc = g.math('MULTIPLY', g.math('SUBTRACT', r0, ang), 260.0, clamp=True)
    halo = g.math('EXPONENT', g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', ang, r0), 0.0), -9.0))
    rings = g.math('DIVIDE', g.math('FLOOR', g.math('MULTIPLY', halo, 4.0)), 4.0)
    col = g.mix(g.math('MULTIPLY', rings, 0.42), col, lin((1.0, 0.84, 0.56)), 'SCREEN')
    col = g.mix(disc, col, lin((1.0, 0.95, 0.80)))
    # layered hills on the horizon (far to near), with tiny spire trees on the near ridges, a gold rim toward the sun
    hills = [(0.050, 0.030, 2.2, (0.56, 0.46, 0.62), 0.0), (0.034, 0.026, 3.4, (0.30, 0.42, 0.58), 0.0),
             (0.022, 0.020, 5.0, (0.10, 0.33, 0.40), 0.010), (0.010, 0.012, 7.5, (0.04, 0.22, 0.24), 0.016)]
    for i, (base, amp, f, c, spike) in enumerate(hills):
        rn = g.noise(g.comb(g.math('MULTIPLY', az, f), 7.3 * i + 1.0, 0.0), 1.0, 2.0, 0.5)
        ridge = g.math('ADD', base, g.math('MULTIPLY', g.math('SUBTRACT', rn.outputs['Fac'], 0.5), 2 * amp))
        if spike:
            vo = g.voronoi(g.comb(g.math('MULTIPLY', az, 40.0 + 9 * i), 3.1 * i, 0.0), 1.0, 'F1', '2D')
            on = g.math('GREATER_THAN', g.sep(vo.outputs['Color'])[0], 0.55)
            sp = g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 3.2), clamp=True), on)
            ridge = g.math('ADD', ridge, g.math('MULTIPLY', g.math('POWER', sp, 1.6), spike))
        inside = g.math('MULTIPLY', g.math('SUBTRACT', ridge, el), 900.0, clamp=True)
        rim = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', ridge, el), 700.0), clamp=True), inside), toward)
        hcol = g.mix(g.math('MULTIPLY', toward, 0.25), lin(c), lin(CORAL))
        hcol = g.mix(g.math('MULTIPLY', rim, 0.8), hcol, lin(GOLD))
        col = g.mix(inside, col, hcol)
    below = g.math('MULTIPLY', g.math('SUBTRACT', 0.0, el), 400.0, clamp=True)
    col = g.mix(below, col, lin((0.04, 0.22, 0.24)))
    bg_cam = g.node('ShaderNodeBackground', ins={'Color': col, 'Strength': 1.0})
    bg_light = g.node('ShaderNodeBackground', ins={'Color': lin((0.5, 0.6, 0.8)), 'Strength': 0.0})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bg_light, mx.inputs[1]); g.link(bg_cam, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
    return wd


# ---------------------------------------------------------------------------------------------- set materials
def _strata(P, cw, kit, layers, level):
    m = cw._new_mat(kit.bpy, 'fable_strata'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    sd = g.attr('sd').outputs['Fac']; dtop = g.attr('dtop').outputs['Fac']
    hz = g.math('ADD', sx[0], sx[1])
    wob = g.noise(g.comb(hz, 0.0, g.math('MULTIPLY', sd, 0.2)), 2.2, 3.0)
    s = g.math('ADD', sd, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.06))
    total = sum(l[1] for l in layers[:-1]) + 0.6; stops = []; pst = []; acc = 0.0; edges = []
    for k, l in enumerate(layers):
        c = STRATA_PAINT.get(l[0], FALLBACK[k % len(FALLBACK)])
        a = acc / total; b = min(1.0, (acc + l[1]) / total) if k < len(layers) - 1 else 1.0
        foot = tuple(x * 0.78 for x in c)
        stops += [(a + (0.0015 if k else 0.0), c), (max(a + 0.002, b - 0.0015) if k < len(layers) - 1 else 1.0, foot)]
        pst.append((a, (l[3],) * 3)); acc += l[1]
        if k < len(layers) - 1: edges.append(acc)
    stops = stops[:32]
    fac = g.math('DIVIDE', s, total)
    col = g.ramp(fac, stops); pden = g.sep(g.ramp(fac, pst, 'CONSTANT'))[0]
    # gouache: horizontal strokes and a broad mottle
    n1 = g.noise(g.comb(g.math('MULTIPLY', hz, 3.0), g.math('MULTIPLY', sx[2], 60.0), 0.0), 1.5, 4.0, 0.6)
    n2 = g.noise(pos, 4.0, 3.0, 0.5)
    tone = g.math('ADD', g.math('MULTIPLY', g.math('SUBTRACT', n1.outputs['Fac'], 0.5), 0.22), g.math('MULTIPLY', g.math('SUBTRACT', n2.outputs['Fac'], 0.5), 0.14))
    col = g.mix(1.0, col, g.math('ADD', 1.0, tone), 'MULTIPLY')
    # pebbles: flat dots, a lighter tint of their band, a thin darker ring
    vp = g.voronoi(pos, 30.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    radius = g.math('MULTIPLY', g.math('MULTIPLY', pden, 0.40), g.math('MULTIPLY_ADD', rr[0], 0.7, 0.45))
    dist = vp.outputs['Distance']
    dot = g.math('MULTIPLY', g.math('SUBTRACT', radius, dist), 60.0, clamp=True)
    ring = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', radius, 0.05), dist), 60.0, clamp=True)
    col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', ring, dot), 0.5), col, lin(INK))
    col = g.mix(dot, col, g.mix(g.math('MULTIPLY_ADD', rr[1], 0.4, 0.35), col, lin(CREAM)))
    # fine gold lines between the bands
    lines = None
    for b in edges:
        ln = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', s, b)), 1.0 / 0.0032), clamp=True)
        lines = ln if lines is None else g.math('MAXIMUM', lines, ln)
    # gold flecks like stars in the deep layers (below the ochre)
    deep_at = sum(l[1] for l in layers[:6]) if len(layers) > 6 else 0.62
    vf = g.voronoi(pos, 70.0, 'F1'); rf = g.sep(vf.outputs['Color'])
    fleck = g.math('MULTIPLY', g.math('SUBTRACT', 0.06, vf.outputs['Distance']), 80.0, clamp=True)
    fleck = g.math('MULTIPLY', fleck, g.math('GREATER_THAN', rf[2], 0.80))
    fleck = g.math('MULTIPLY', fleck, g.math('MULTIPLY', g.math('SUBTRACT', s, deep_at + 0.06), 8.0, clamp=True))
    # roots near the top: dark plum hairlines of random length
    u = g.math('ADD', g.math('MULTIPLY', hz, 18.0), g.math('MULTIPLY', g.noise(g.comb(hz, sx[2], 0.0), 6.0, 2.0).outputs['Fac'], 3.0))
    lane = g.math('FLOOR', u); fr = g.math('FRACT', u)
    wn = g.node('ShaderNodeTexWhiteNoise', noise_dimensions='1D'); g.put(wn, 'W', lane)
    rlen = g.math('MULTIPLY', wn.outputs['Value'], 0.24)
    line = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', fr, 0.5)), 14.0), clamp=True)
    root = g.math('MULTIPLY', g.math('MULTIPLY', line, g.math('MULTIPLY', g.math('SUBTRACT', rlen, dtop), 20.0, clamp=True)), g.math('GREATER_THAN', wn.outputs['Value'], 0.4))
    col = g.mix(g.math('MULTIPLY', root, 0.9), col, lin((0.16, 0.06, 0.14)))
    top_dark = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', dtop, 40.0), clamp=True)
    col = g.mix(g.math('MULTIPLY', top_dark, 0.5), col, lin(DARK_EMERALD))
    sh = P.shader(g, col, amb=0.78, lit=0.30, ao=0.05, tex=0.0)
    # gold: lines and flecks glow a little (emission on top of the paint)
    glow = g.math('MAXIMUM', g.math('MULTIPLY', lines, 1.0), g.math('MULTIPLY', fleck, 1.4))
    ge = g.node('ShaderNodeEmission', ins={'Color': lin(GOLD), 'Strength': 1.15})
    mx = g.node('ShaderNodeMixShader'); g.link(glow, mx.inputs[0]); g.link(sh, mx.inputs[1]); g.link(ge, mx.inputs[2])
    cw._finish(g, mx); return m


def _top(P, cw, kit, land):
    m = cw._new_mat(kit.bpy, 'fable_top'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    A = {k: g.attr(k).outputs['Fac'] for k in ('w_grass', 'w_sand', 'w_rock', 'w_path')}
    nb = g.noise(pos, 1.3, 2.0, 0.5); nm = g.noise(pos, 7.0, 3.0, 0.5)
    ground = g.ramp(nb.outputs['Fac'], [(0.3, DARK_EMERALD), (0.55, EMERALD), (0.75, (0.16, 0.52, 0.36))])
    sand = g.mix(nm.outputs['Fac'], lin((0.93, 0.76, 0.48)), lin((0.98, 0.84, 0.58)))
    col = g.mix(A['w_sand'], lin((0.40, 0.20, 0.24)), sand)
    col = g.mix(A['w_rock'], col, lin((0.62, 0.70, 0.72)))
    col = g.mix(A['w_grass'], col, ground)
    col = g.mix(A['w_path'], col, lin((0.96, 0.70, 0.52)))
    if land.level is not None:
        lv = land.level; under = g.math('MULTIPLY', g.math('SUBTRACT', lv, sx[2]), 12.0, clamp=True)
        bed = g.mix(under, lin((0.20, 0.52, 0.50)), lin((0.06, 0.26, 0.34)))
        col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', lv + 0.004, sx[2]), 200.0, clamp=True), col, bed)
    J.set_surface(m, P.shader(g, col, amb=0.62, lit=0.55, ao=0.06, tex=0.06, tex_scale=14.0)); return m


def _grass(P, cw, kit, name):
    m = cw._new_mat(kit.bpy, name); g = cw.G(m.node_tree, kit)
    oi = g.node('ShaderNodeObjectInfo'); tc = g.node('ShaderNodeTexCoord')
    col = g.ramp(oi.outputs['Random'], [(0.0, DARK_EMERALD), (0.45, EMERALD), (0.8, (0.12, 0.50, 0.40)), (1.0, (0.30, 0.62, 0.42))])
    z = g.sep(tc.outputs['Object'])[2]; tip = g.math('POWER', g.math('MULTIPLY', z, 14.0, clamp=True), 2.0)
    col = g.mix(g.math('MULTIPLY', tip, 0.55), col, lin((0.78, 0.80, 0.42)))
    J.set_surface(m, P.shader(g, col, amb=0.60, lit=0.50, ao=0.0, tex=0.0)); return m


def _water(cw, kit, land, sd):
    m = cw._new_mat(kit.bpy, 'fable_water'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry'); pos = tc.outputs['Object']; sx = g.sep(pos)
    nz = g.sep(geo.outputs['Normal'])[2]; topf = g.math('GREATER_THAN', nz, 0.5)
    lv = land.level if land.level is not None else 0.0
    dd = g.math('MULTIPLY', g.math('SUBTRACT', lv, sx[2]), 1 / 0.42, clamp=True)
    side = g.ramp(dd, [(0.0, (0.30, 0.70, 0.66)), (0.08, TEAL), (0.6, DEEP_TEAL), (1.0, (0.05, 0.14, 0.30))])
    # painted ripple lines on the cut face, a cream meniscus at the surface
    wl = g.noise(g.comb(g.math('MULTIPLY', g.math('ADD', sx[0], sx[1]), 1.2), g.math('MULTIPLY', sx[2], 26.0), 0.0), 1.0, 1.0, 0.4)
    wv = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', g.math('FRACT', g.math('MULTIPLY', wl.outputs['Fac'], 7.0)), 0.5)), 16.0), clamp=True)
    side = g.mix(g.math('MULTIPLY', wv, 0.18), side, lin(JADE))
    men = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', sx[2], lv - 0.004)), 1 / 0.004), clamp=True)
    side = g.mix(men, side, lin(CREAM))
    # the surface: teal with gold glints where it mirrors the sun, broken into short strokes
    zoff, w = g.phase(0.4)
    rn = g.noise(g.comb(g.math('MULTIPLY', sx[0], 5.0), g.math('MULTIPLY', sx[1], 22.0), zoff), 1.0, 2.0, 0.5, '4D', w)
    view = g.vmath('NORMALIZE', g.vmath('SCALE', geo.outputs['Incoming'], scale=-1.0))
    refl = g.vmath('REFLECT', view, (0, 0, 1))
    glint = g.math('POWER', g.math('MAXIMUM', g.vmath('DOT_PRODUCT', refl, tuple(sd)), 0.0), 6.0)
    strokes = g.math('MULTIPLY', g.math('SUBTRACT', rn.outputs['Fac'], 0.56), 18.0, clamp=True)
    surf = g.mix(g.math('MULTIPLY', strokes, g.math('ADD', 0.25, glint)), lin((0.12, 0.50, 0.52)), lin(PALE_GOLD))
    col = g.mix(topf, side, surf)
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    tr = g.node('ShaderNodeBsdfTransparent')
    mx = g.node('ShaderNodeMixShader'); g.put(mx, 0, g.math('ADD', 0.62, g.math('MULTIPLY', topf, 0.18))); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2])
    cw._finish(g, mx); return m


def _floor(cw, kit):
    m = cw._new_mat(kit.bpy, 'fable_floor'); g = cw.G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    r = g.vmath('LENGTH', g.vmath('MULTIPLY', tc.outputs['Object'], (1, 1, 0)))
    far = g.math('MULTIPLY', g.math('SUBTRACT', r, 2.6), 1 / 16.0, clamp=True)
    n = g.noise(tc.outputs['Object'], 0.6, 2.0, 0.5)
    col = g.mix(g.math('POWER', far, 0.6), g.mix(n.outputs['Fac'], lin((0.03, 0.17, 0.18)), lin((0.05, 0.24, 0.22))), lin((0.04, 0.22, 0.24)))
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    t = g.node('ShaderNodeBsdfToon', ins={'Color': lin((0.10, 0.30, 0.26)), 'Size': 0.7, 'Smooth': 0.05})
    mx = g.node('ShaderNodeAddShader'); g.link(e, mx.inputs[0]); g.link(t, mx.inputs[1]); cw._finish(g, mx); return m


# ---------------------------------------------------------------------------------------------- trees
def _tree_mat(cw, kit, name, crown, deep):
    m = cw._new_mat(kit.bpy, name); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos); oi = g.node('ShaderNodeObjectInfo')
    zf = g.math('DIVIDE', sx[2], g.math('ADD', g.attr('fable_h', 'OBJECT').outputs['Fac'], 1e-3))
    col = g.mix(g.math('POWER', g.math('MINIMUM', g.math('MAXIMUM', zf, 0.0), 1.0), 0.8), lin(deep), lin(crown))
    col = g.mix(g.math('MULTIPLY', oi.outputs['Random'], 0.35), col, lin(JADE))
    # fine vertical striations (the painted texture of a stylised tree)
    angle = g.math('ARCTAN2', sx[1], sx[0])
    wv = g.noise(g.comb(g.math('MULTIPLY', angle, 1.0), g.math('MULTIPLY', sx[2], 3.0), 0.0), 2.0, 2.0, 0.5)
    stripes = g.math('ABSOLUTE', g.math('SINE', g.math('ADD', g.math('MULTIPLY', angle, 11.0), g.math('MULTIPLY', wv.outputs['Fac'], 4.0))))
    stripes = g.math('MULTIPLY', g.math('SUBTRACT', stripes, 0.86), 9.0, clamp=True)
    col = g.mix(g.math('MULTIPLY', stripes, 0.45), col, g.mix(1.0, col, lin((0.35, 0.45, 0.55)), 'MULTIPLY'))
    return m, g, col


def _trees(bpy, film, P, cw, kit, land, sd):
    pts, scale, var, inst = J.tree_points(film)
    out = []
    if inst is not None: J.hide(film, inst)
    rng = np.random.default_rng(7)
    mats = {}
    for kind, crown, deep in (('green', EMERALD, DARK_EMERALD), ('teal', TEAL, DEEP_TEAL), ('coral', CORAL, DEEP_CORAL)):
        m, g, col = _tree_mat(cw, kit, 'fable_tree_' + kind, crown, deep)
        J.set_surface(m, P.shader(g, col, amb=0.66, lit=0.60, ao=0.08, tex=0.05, tex_scale=30.0, rim=1.2)); mats[kind] = m
    trunk = P.material('fable_trunk', PLUM, amb=0.7, lit=0.4, ao=0.0)
    for i, (p, s, v) in enumerate(zip(pts, scale, var)):
        s = float(s); x, y, z = map(float, p)
        kind = ('spire', 'tiered', 'oval')[(int(v) + i) % 3] if int(v) < 3 else 'spire'
        H = 0.62 * s * (1.35 if kind == 'spire' else 1.0); base = H * (0.16 if kind == 'spire' else 0.26)
        prof = []
        for j in range(25):
            q = j / 24
            if kind == 'spire': r = 0.10 * s * (q ** 0.45) * ((1 - q) ** 0.85) * 1.9
            elif kind == 'tiered': r = 0.17 * s * ((1 - q) ** 0.75) * (0.62 + 0.38 * abs(math.sin(math.pi * q * 3.0 + 0.4))) * min(1.0, q * 8)
            else: r = 0.14 * s * math.sqrt(max(0.0, 1 - (2 * q - 1) ** 2))
            prof.append((base + q * (H - base), max(r, 0.0004)))
        V, F = J.rotation_profile(prof, 28)
        col = 'coral' if rng.uniform() < 0.18 else ('teal' if rng.uniform() < 0.4 else 'green')
        ob = cw.mk_mesh(bpy, f'fable_tree{i}', V, F, [mats[col]], None, True, kit.coll)
        ob['fable_h'] = H; ob.location = (x, y, z - 0.01)
        tV, tF = J.rotation_profile([(0.0, 0.016 * s), (base + 0.02, 0.010 * s)], 10)
        tr = cw.mk_mesh(bpy, f'fable_trunk{i}', tV, tF, [trunk], None, True, kit.coll); tr.parent = ob
        J.adopt(film, ob); J.adopt(film, tr)
        out.append((ob, rng.uniform(0, 2 * math.pi), 0.012 + 0.01 * rng.uniform()))
    return out


# ---------------------------------------------------------------------------------------------- the hook
def apply(bpy, film, ctx):
    cw = film.cw; sc = bpy.context.scene; W, H = ctx['W'], ctx['H']
    st = next(iter(film.built.values())); kit = st['kit']; land = st['land']; L = st['L']
    rig = st.get('rig'); sd = np.asarray(rig['sun_dir'] if rig else (-0.6, 0.6, 0.35), float); sd = sd / np.linalg.norm(sd)
    P = Paint(cw, kit)
    film._fable = {}
    # ---- materials
    objs = J.scene_objects(film); seen = set()
    for m in J.scene_materials(objs):
        k = _key(m.name)
        if m.name in seen: continue
        seen.add(m.name)
        if k in ('cw_strata', 'cw_top', 'cw_water', 'ex_floor', 'cw_leaf', 'cw_grass', 'ex_shaft_mat', 'ex_gobo'): continue
        if J.principled(m) is None: continue
        if k in RECOLOR: P.convert(m, RECOLOR[k], amb=0.66, lit=0.5, ao=0.04)
        else: P.convert(m, None, sat=1.3, amb=0.66, lit=0.5, ao=0.04)
    walls = land.objects['walls']; walls.material_slots[0].material = _strata(P, cw, kit, L.strata, land.level)
    land.objects['top'].material_slots[0].material = _top(P, cw, kit, land)
    if 'water' in land.objects: land.objects['water'].material_slots[0].material = _water(cw, kit, land, sd)
    grass_mats = {}
    for col in bpy.data.collections:
        for po in col.objects:
            for s in po.material_slots:
                if s.material is not None and _key(s.material.name) == 'cw_grass':
                    if s.material.name not in grass_mats: grass_mats[s.material.name] = _grass(P, cw, kit, 'fable_' + s.material.name)
                    s.material = grass_mats[s.material.name]
    for o in objs:
        if o.name == 'ex_floor': o.material_slots[0].material = _floor(cw, kit)
    # god rays: warm gold, a little stronger (the painted rays of a storybook sunset)
    sm = bpy.data.materials.get('ex_shaft_mat')
    if sm is not None:
        for n in sm.node_tree.nodes:
            if n.bl_idname == 'ShaderNodeEmission': n.inputs['Color'].default_value = lin((1.0, 0.82, 0.52))
    # ---- world, lights
    wd = _sky(bpy, cw, kit, sd)
    for s in film.built.values(): s['world'] = wd
    sc.world = wd
    J.lights(bpy, film, off_prefix=('ex_fill', 'ex_rim', 'ex_edge_spill'), scale={'ex_spot': 0.35, 'ex_sun': 0.32, 'cl_house': 0.6, 'cl_lamp': 0.6, 'cw_mill': 0.6})
    for o in objs:
        if o.type == 'LIGHT' and o.name == 'ex_sun': o.data.color = (1.0, 0.86, 0.66)
    # ---- trees
    film._fable['trees'] = _trees(bpy, film, P, cw, kit, land, sd)
    # ---- render: flat paint wants few bounces and the Standard view (colours as painted)
    cy = sc.cycles; cy.max_bounces = 3; cy.diffuse_bounces = 1; cy.glossy_bounces = 1; cy.transmission_bounces = 2; cy.transparent_max_bounces = 24
    sc.view_settings.view_transform = 'Standard'
    try: sc.view_settings.look = 'None'
    except Exception: pass
    sc.view_settings.exposure = film.SETTINGS['exposure']
    # ---- words: midnight ink on cream, in their own layer, laid over the brushwork
    J.recolor_overlay(film, ink=INK, paper=CREAM)
    J.type_layer(bpy, film)
    ng, N, Lk, rl = J.comp_begin(bpy, 'fable_comp')
    img = rl.outputs['Image']
    kw = N.new('CompositorNodeKuwahara')
    try: kw.inputs['Type'].default_value = 'Anisotropic'
    except Exception: pass
    kw.inputs['Size'].default_value = max(2.0, 5.0 * W / 1280.0); kw.inputs['Uniformity'].default_value = 4
    kw.inputs['Sharpness'].default_value = 0.75; kw.inputs['Eccentricity'].default_value = 1.1
    Lk.new(img, kw.inputs['Image']); img = kw.outputs['Image']
    # paper grain and a broad wash (screen space, like paint on a board)
    nrm, x, y = J.uv(N, Lk, img)
    sv = N.new('ShaderNodeVectorMath'); sv.operation = 'MULTIPLY'; Lk.new(nrm, sv.inputs[0]); sv.inputs[1].default_value = (W / 1280.0 * 16, W / 1280.0 * 9, 1)
    gr = N.new('ShaderNodeTexNoise'); gr.inputs['Scale'].default_value = 26.0; gr.inputs['Detail'].default_value = 6.0; gr.inputs['Roughness'].default_value = 0.75
    Lk.new(sv.outputs[0], gr.inputs['Vector'])
    wa = N.new('ShaderNodeTexNoise'); wa.inputs['Scale'].default_value = 0.35; wa.inputs['Detail'].default_value = 3.0
    Lk.new(sv.outputs[0], wa.inputs['Vector'])
    grain = J.cmath(N, Lk, 'ADD', J.cmath(N, Lk, 'MULTIPLY', J.cmath(N, Lk, 'SUBTRACT', gr.outputs['Fac'], 0.5), 0.10),
                    J.cmath(N, Lk, 'ADD', 1.0, J.cmath(N, Lk, 'MULTIPLY', J.cmath(N, Lk, 'SUBTRACT', wa.outputs['Fac'], 0.5), 0.08)))
    img = J.cmix(N, Lk, 1.0, img, grain, 'MULTIPLY')
    gl = N.new('CompositorNodeGlare')
    gl.inputs['Type'].default_value = 'Bloom'; gl.inputs['Quality'].default_value = 'Medium'
    gl.inputs['Threshold'].default_value = 0.72; gl.inputs['Strength'].default_value = 0.28; gl.inputs['Size'].default_value = 0.7
    Lk.new(img, gl.inputs['Image']); img = gl.outputs['Image']
    img = J.vignette(N, Lk, img, W, H, amount=0.16)
    J.comp_end(bpy, ng, img)


def frame(bpy, film, ctx, t, shot):
    """The painted trees sway a little in the wind (pure function of t)."""
    for ob, ph, amp in film._fable.get('trees', []):
        ob.rotation_euler = (amp * math.sin(0.9 * t + ph), amp * 0.7 * math.cos(0.7 * t + 1.3 * ph), 0.0)
