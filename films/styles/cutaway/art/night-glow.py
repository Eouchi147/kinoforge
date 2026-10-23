"""Cutaway art direction `night-glow`: the block at night, alive with light (bioluminescence, fantasy and nature).

The look: the same meadow under a deep night sky full of stars, a large pale moon behind the block with a soft halo and a
faint green aurora on the horizon. Every surface goes dark and cool (moonlit, a hard silver terminator); the life and the
finds give the light: veins of cyan light run down from the turf as glowing roots, the pebbles glimmer like plankton,
the fine band lines between the layers shine faintly, the gold vein and the chest burn warm, the bones and the shell
fossil glow a pale sea-green at their edges, the river is luminous turquoise from inside with brighter ripple lines,
the grass tips and glowing moss spots on the turf shine green, the trees carry speckles of light, the windows of the
village are lit, and fireflies drift over the grass. The compositor adds a wide soft bloom and a vignette; the words
stay crisp in their own layer (pale plates, midnight ink).

What it changes: every material (moonlit dark paint plus emission for what glows), the world (night sky, stars, moon,
aurora), the floor, the lights (sun turned into a cool moon, fill, rim, edge spills, god rays and cloud shadows off,
museum spots dimmed to a glow), adds fireflies (the cinematic extras' fireflies), the compositor (bloom, vignette).

Render cost vs the reference: about the same or cheaper. Mostly emission, 3 bounces, no glass refraction (the water is
emissive and partly transparent); the fireflies add tiny emitters only.
"""
import importlib.util
import math
import os

import numpy as np

_s = importlib.util.spec_from_file_location('kf_art__jewel', os.path.join(os.path.dirname(os.path.abspath(__file__)), '_jewel.py'))
J = importlib.util.module_from_spec(_s); _s.loader.exec_module(J)
lin = J.lin

CYAN = (0.30, 1.00, 0.92)
SEA = (0.45, 1.00, 0.70)
LIME = (0.70, 1.00, 0.40)
GOLD = (1.00, 0.72, 0.28)
MOON = (0.80, 0.88, 1.00)
INK = (0.04, 0.06, 0.14)
PAPER = (0.90, 0.95, 0.98)

# night bands: deep and cool, each a little different so the layers still read
STRATA_NIGHT = {'topsoil': (0.16, 0.10, 0.20), 'sand': (0.30, 0.32, 0.46), 'clay': (0.36, 0.18, 0.40), 'loam': (0.24, 0.13, 0.32),
                'gravel': (0.14, 0.26, 0.36), 'ochre': (0.40, 0.32, 0.40), 'limestone': (0.10, 0.24, 0.36), 'bedrock': (0.05, 0.07, 0.18)}
FALLBACK = [(0.16, 0.10, 0.20), (0.30, 0.32, 0.46), (0.36, 0.18, 0.40), (0.24, 0.13, 0.32), (0.14, 0.26, 0.36), (0.10, 0.24, 0.36), (0.05, 0.07, 0.18)]
# finds and life that glow, and how (colour, edge glow strength)
GLOW = {'ex_bone': (SEA, 1.2), 'ex_tooth': (SEA, 1.2), 'ex_nacre': (CYAN, 1.6), 'ex_trilo': (SEA, 1.4), 'ex_gold': (GOLD, 2.5),
        'ex_quartz': ((0.70, 0.85, 1.0), 1.0), 'ex_amethyst': ((0.75, 0.45, 1.0), 2.5), 'ex_agate': ((0.55, 0.35, 0.90), 1.0),
        'ex_terracotta': ((1.0, 0.55, 0.30), 0.8), 'ex_bronze': (GOLD, 1.5), 'ex_chestwood': ((1.0, 0.60, 0.30), 0.5),
        'ex_straw': (LIME, 0.6), 'ex_spines': (LIME, 0.4), 'ex_molefur': (CYAN, 0.4), 'ex_wellwater': (CYAN, 2.0),
        'cw_lilyflower': ((1.0, 0.75, 0.95), 1.6), 'cw_bloom': ((0.95, 0.60, 1.0), 1.4), 'cw_cattail': (LIME, 0.5),
        'ex_deercoat': (SEA, 0.35), 'ex_foxred': (SEA, 0.35), 'ex_herongrey': (SEA, 0.5), 'ex_fish': (CYAN, 1.5), 'ex_fin': (CYAN, 1.5)}


def _key(n): return n.split('.')[0].rstrip('0123456789') if n.startswith(('cw_bloom', 'ex_fish', 'ex_fin')) else n.split('.')[0]


def _glow_add(g, shader, color, strength, facing_pow=2.0, base=0.15):
    """Add an edge glow (stronger at grazing angles) in a colour on top of a shader."""
    lw = g.node('ShaderNodeLayerWeight', ins={'Blend': 0.4})
    f = g.math('ADD', base, g.math('POWER', lw.outputs['Facing'], facing_pow))
    e = g.node('ShaderNodeEmission', ins={'Color': lin(color), 'Strength': g.math('MULTIPLY', f, strength)})
    ad = g.node('ShaderNodeAddShader'); g.link(shader, ad.inputs[0]); g.link(e, ad.inputs[1]); return ad


def _night(P, g, col, **kw):
    k = dict(amb=0.22, lit=0.55, ao=0.05, tex=0.05, cool=(0.30, 0.42, 0.85), warm=(0.62, 0.74, 1.0))
    k.update(kw); return P.shader(g, col, **k)


def _sky(bpy, cw, kit, md):
    wd = bpy.data.worlds.new('night_world')
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree; nt.nodes.clear(); g = cw.G(nt, kit)
    tc = g.node('ShaderNodeTexCoord'); d = g.vmath('NORMALIZE', tc.outputs['Generated']); dx, dy, dz = g.sep(d)
    el = g.math('ARCSINE', dz); az = g.math('ARCTAN2', dy, dx)
    e = g.math('DIVIDE', g.math('MAXIMUM', el, 0.0), math.pi / 2)
    col = g.ramp(e, [(0.0, (0.08, 0.14, 0.26)), (0.08, (0.05, 0.09, 0.20)), (0.35, (0.02, 0.04, 0.11)), (1.0, (0.005, 0.01, 0.04))])
    # aurora: a soft green curtain low over the horizon, slowly folding
    an = g.noise(g.comb(g.math('MULTIPLY', az, 2.4), g.math('MULTIPLY', el, 3.0), 0.0), 1.2, 3.0, 0.55)
    curtain = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', an.outputs['Fac'], 0.45), 4.0, clamp=True),
                     g.math('MULTIPLY', g.math('MULTIPLY', el, 18.0, clamp=True), g.math('MULTIPLY', g.math('SUBTRACT', 0.42, el), 5.0, clamp=True)))
    streak = g.noise(g.comb(g.math('MULTIPLY', az, 40.0), g.math('MULTIPLY', el, 1.0), 0.0), 1.0, 2.0, 0.5)
    curtain = g.math('MULTIPLY', curtain, g.math('ADD', 0.4, g.math('MULTIPLY', streak.outputs['Fac'], 0.9)))
    col = g.mix(1.0, col, g.vmath('SCALE', lin((0.10, 0.85, 0.55))[:3], scale=g.math('MULTIPLY', curtain, 0.22)), 'ADD')
    # stars: two layers of points, a few bright ones
    for sc, thr, k in ((180.0, 0.035, 1.2), (70.0, 0.05, 3.0)):
        vo = g.voronoi(d, sc, 'F1'); rr = g.sep(vo.outputs['Color'])
        star = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', thr, vo.outputs['Distance']), 1.0 / thr, clamp=True), g.math('GREATER_THAN', rr[0], 0.55))
        star = g.math('MULTIPLY', g.math('POWER', star, 2.0), g.math('MULTIPLY', el, 12.0, clamp=True))
        col = g.mix(1.0, col, g.vmath('SCALE', lin((0.85, 0.90, 1.0))[:3], scale=g.math('MULTIPLY', star, g.math('MULTIPLY', rr[1], k))), 'ADD')
    # the moon: a large pale disc with soft maria and a wide halo
    ang = g.math('ARCCOSINE', g.math('MINIMUM', g.vmath('DOT_PRODUCT', d, tuple(md)), 1.0))
    r0 = 0.07; disc = g.math('MULTIPLY', g.math('SUBTRACT', r0, ang), 300.0, clamp=True)
    mar = g.noise(d, 30.0, 3.0, 0.6)
    mcol = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', mar.outputs['Fac'], 0.45), 3.0, clamp=True), lin((1.6, 1.65, 1.7)), lin((1.05, 1.15, 1.30)))
    halo = g.math('MULTIPLY', g.math('EXPONENT', g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', ang, r0), 0.0), -7.0)), 0.30)
    col = g.mix(1.0, col, g.vmath('SCALE', lin((0.40, 0.55, 0.90))[:3], scale=halo), 'ADD')
    col = g.mix(disc, col, mcol)
    below = g.math('MULTIPLY', g.math('SUBTRACT', 0.0, el), 200.0, clamp=True)
    col = g.mix(below, col, lin((0.02, 0.04, 0.08)))
    bg_cam = g.node('ShaderNodeBackground', ins={'Color': col, 'Strength': 1.0})
    bg_light = g.node('ShaderNodeBackground', ins={'Color': lin((0.2, 0.3, 0.6)), 'Strength': 0.0})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bg_light, mx.inputs[1]); g.link(bg_cam, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
    return wd


def _strata(P, cw, kit, layers, m):
    g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    sd = g.attr('sd').outputs['Fac']; dtop = g.attr('dtop').outputs['Fac']; hz = g.math('ADD', sx[0], sx[1])
    wob = g.noise(g.comb(hz, 0.0, g.math('MULTIPLY', sd, 0.2)), 2.2, 3.0)
    s = g.math('ADD', sd, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.06))
    total = sum(l[1] for l in layers[:-1]) + 0.6; stops = []; pst = []; acc = 0.0; edges = []
    for k, l in enumerate(layers):
        c = STRATA_NIGHT.get(l[0], FALLBACK[k % len(FALLBACK)]); a = acc / total
        b = min(1.0, (acc + l[1]) / total) if k < len(layers) - 1 else 1.0
        stops += [(a + (0.0015 if k else 0.0), c), (max(a + 0.002, b - 0.0015) if k < len(layers) - 1 else 1.0, tuple(x * 0.7 for x in c))]
        pst.append((a, (l[3],) * 3)); acc += l[1]
        if k < len(layers) - 1: edges.append(acc)
    fac = g.math('DIVIDE', s, total); col = g.ramp(fac, stops[:32]); pden = g.sep(g.ramp(fac, pst, 'CONSTANT'))[0]
    n1 = g.noise(g.comb(g.math('MULTIPLY', hz, 3.0), g.math('MULTIPLY', sx[2], 60.0), 0.0), 1.5, 4.0, 0.6)
    col = g.mix(1.0, col, g.math('ADD', 0.85, g.math('MULTIPLY', n1.outputs['Fac'], 0.3)), 'MULTIPLY')
    sh = _night(P, g, col, amb=0.55, lit=0.25, tex=0.0)
    # glowing roots: cyan veins hanging from the turf, branching thinner at their tips, pulsing slowly
    u = g.math('ADD', g.math('MULTIPLY', hz, 11.0), g.math('MULTIPLY', g.noise(g.comb(hz, g.math('MULTIPLY', sx[2], 2.0), 0.0), 5.0, 3.0).outputs['Fac'], 3.5))
    lane = g.math('FLOOR', u); fr = g.math('FRACT', u)
    wn = g.node('ShaderNodeTexWhiteNoise', noise_dimensions='1D'); g.put(wn, 'W', lane)
    rlen = g.math('ADD', 0.06, g.math('MULTIPLY', wn.outputs['Value'], 0.40))
    width = g.math('ADD', 16.0, g.math('MULTIPLY', g.math('DIVIDE', dtop, rlen), 30.0))
    line = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', fr, 0.5)), width), clamp=True)
    fade = g.math('MULTIPLY', g.math('SUBTRACT', rlen, dtop), 8.0, clamp=True)
    root = g.math('MULTIPLY', g.math('MULTIPLY', line, fade), g.math('MULTIPLY', g.math('GREATER_THAN', wn.outputs['Value'], 0.5), g.math('MULTIPLY_ADD', wn.outputs['Value'], 1.6, -0.5)))
    # plankton: the pebbles glimmer
    vp = g.voronoi(pos, 30.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    radius = g.math('MULTIPLY', g.math('MULTIPLY', pden, 0.30), g.math('MULTIPLY_ADD', rr[0], 0.6, 0.4))
    dot = g.math('MULTIPLY', g.math('SUBTRACT', radius, vp.outputs['Distance']), 30.0, clamp=True)
    dot = g.math('MULTIPLY', dot, g.math('MULTIPLY_ADD', rr[1], 0.8, 0.2))
    # faint lines between the bands
    lines = None
    for b in edges:
        ln = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', s, b)), 1.0 / 0.004), clamp=True)
        lines = ln if lines is None else g.math('MAXIMUM', lines, ln)
    gcol = g.mix(g.math('MULTIPLY', rr[2], 1.0), lin(CYAN), lin(SEA))
    e1 = g.node('ShaderNodeEmission', ins={'Color': lin(CYAN), 'Strength': g.math('MULTIPLY', root, 3.0)})
    e2 = g.node('ShaderNodeEmission', ins={'Color': gcol, 'Strength': g.math('MULTIPLY', dot, 1.6)})
    e3 = g.node('ShaderNodeEmission', ins={'Color': lin((0.35, 0.65, 1.0)), 'Strength': g.math('MULTIPLY', lines, 0.6)})
    a = g.node('ShaderNodeAddShader'); g.link(sh, a.inputs[0]); g.link(e1, a.inputs[1])
    b2 = g.node('ShaderNodeAddShader'); g.link(a, b2.inputs[0]); g.link(e2, b2.inputs[1])
    c2 = g.node('ShaderNodeAddShader'); g.link(b2, c2.inputs[0]); g.link(e3, c2.inputs[1])
    J.under_mask(m, c2)


def _top(P, cw, kit, land):
    m = cw._new_mat(kit.bpy, 'night_top'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    A = {k: g.attr(k).outputs['Fac'] for k in ('w_grass', 'w_sand', 'w_rock')}
    col = g.mix(A['w_sand'], lin((0.08, 0.07, 0.10)), lin((0.22, 0.24, 0.30)))
    col = g.mix(A['w_rock'], col, lin((0.30, 0.34, 0.40)))
    col = g.mix(A['w_grass'], col, lin((0.04, 0.10, 0.08)))
    sh = _night(P, g, col, amb=0.25)
    # glowing moss: soft green spots on the turf, and a luminous bed under the water
    vo = g.voronoi(pos, 9.0, 'F1'); rr = g.sep(vo.outputs['Color'])
    moss = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', 0.22, vo.outputs['Distance']), 6.0, clamp=True), g.math('GREATER_THAN', rr[0], 0.6))
    moss = g.math('MULTIPLY', moss, A['w_grass'])
    glow = g.math('MULTIPLY', moss, 1.2)
    if land.level is not None:
        under = g.math('MULTIPLY', g.math('SUBTRACT', land.level, sx[2]), 20.0, clamp=True)
        glow = g.math('ADD', glow, g.math('MULTIPLY', under, 0.9))
    e = g.node('ShaderNodeEmission', ins={'Color': g.mix(g.math('GREATER_THAN', A['w_grass'], 0.5), lin(CYAN), lin(LIME)), 'Strength': glow})
    ad = g.node('ShaderNodeAddShader'); g.link(sh, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad); return m


def _grass(P, cw, kit, name):
    m = cw._new_mat(kit.bpy, name); g = cw.G(m.node_tree, kit)
    oi = g.node('ShaderNodeObjectInfo'); tc = g.node('ShaderNodeTexCoord')
    col = g.ramp(oi.outputs['Random'], [(0.0, (0.02, 0.07, 0.07)), (1.0, (0.06, 0.16, 0.12))])
    sh = _night(P, g, col, ao=0.0, tex=0.0)
    z = g.sep(tc.outputs['Object'])[2]; tip = g.math('POWER', g.math('MULTIPLY', z, 13.0, clamp=True), 4.0)
    on = g.math('GREATER_THAN', oi.outputs['Random'], 0.55)
    e = g.node('ShaderNodeEmission', ins={'Color': g.mix(oi.outputs['Random'], lin(LIME), lin(CYAN)), 'Strength': g.math('MULTIPLY', g.math('MULTIPLY', tip, on), 2.2)})
    ad = g.node('ShaderNodeAddShader'); g.link(sh, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad); return m


def _leaf(P, cw, kit, m):
    g = cw.G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); oi = g.node('ShaderNodeObjectInfo')
    col = g.mix(oi.outputs['Random'], lin((0.03, 0.08, 0.10)), lin((0.05, 0.14, 0.12)))
    sh = _night(P, g, col, rim=0.0)
    vo = g.voronoi(tc.outputs['Object'], 60.0, 'F1'); rr = g.sep(vo.outputs['Color'])
    sp = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', 0.12, vo.outputs['Distance']), 10.0, clamp=True), g.math('GREATER_THAN', rr[0], 0.82))
    e = g.node('ShaderNodeEmission', ins={'Color': g.mix(rr[1], lin(LIME), lin(CYAN)), 'Strength': g.math('MULTIPLY', sp, 3.0)})
    ad = g.node('ShaderNodeAddShader'); g.link(sh, ad.inputs[0]); g.link(e, ad.inputs[1]); J.set_surface(m, ad)


def _water(cw, kit, land, m):
    g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry'); pos = tc.outputs['Object']; sx = g.sep(pos)
    nz = g.sep(geo.outputs['Normal'])[2]; topf = g.math('GREATER_THAN', nz, 0.5)
    lv = land.level if land.level is not None else 0.0
    dd = g.math('MULTIPLY', g.math('SUBTRACT', lv, sx[2]), 1 / 0.42, clamp=True)
    col = g.ramp(dd, [(0.0, (0.40, 1.0, 0.92)), (0.15, (0.10, 0.70, 0.75)), (1.0, (0.02, 0.18, 0.35))])
    zoff, w = g.phase(0.35)
    rn = g.noise(g.comb(g.math('MULTIPLY', g.math('ADD', sx[0], sx[1]), 4.0), g.math('MULTIPLY', sx[2], 30.0), zoff), 1.0, 2.0, 0.5, '4D', w)
    rip = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', g.math('FRACT', g.math('MULTIPLY', rn.outputs['Fac'], 6.0)), 0.5)), 12.0), clamp=True)
    col = g.mix(g.math('MULTIPLY', rip, 0.5), col, lin(CYAN))
    rs = g.noise(g.comb(g.math('MULTIPLY', sx[0], 6.0), g.math('MULTIPLY', sx[1], 6.0), zoff), 1.0, 2.0, 0.5, '4D', w)
    surf = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', rs.outputs['Fac'], 0.5), 6.0, clamp=True), lin((0.05, 0.40, 0.45)), lin((0.45, 1.0, 0.95)))
    col = g.mix(topf, col, surf)
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': g.math('ADD', 0.9, g.math('MULTIPLY', topf, -0.3))})
    tr = g.node('ShaderNodeBsdfTransparent')
    mx = g.node('ShaderNodeMixShader'); g.put(mx, 0, 0.7); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2])
    J.under_mask(m, mx)


def _floor(cw, kit):
    m = cw._new_mat(kit.bpy, 'night_floor'); g = cw.G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    r = g.vmath('LENGTH', g.vmath('MULTIPLY', tc.outputs['Object'], (1, 1, 0)))
    near = g.math('EXPONENT', g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', r, 2.2), 0.0), -1.2))
    col = g.mix(near, lin((0.02, 0.04, 0.08)), lin((0.03, 0.12, 0.14)))
    e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0})
    t = g.node('ShaderNodeBsdfDiffuse', ins={'Color': lin((0.10, 0.14, 0.22))})
    ad = g.node('ShaderNodeAddShader'); g.link(e, ad.inputs[0]); g.link(t, ad.inputs[1]); cw._finish(g, ad); return m


def apply(bpy, film, ctx):
    cw = film.cw; ex = film.ex; sc = bpy.context.scene; W, H = ctx['W'], ctx['H']
    st = next(iter(film.built.values())); kit = st['kit']; land = st['land']; L = st['L']
    rig = st.get('rig'); sd = np.asarray(rig['sun_dir'] if rig else (-0.6, 0.6, 0.35), float)
    md = np.array([sd[0], sd[1], 0.0]); md = md / np.linalg.norm(md) * math.cos(math.radians(9)) + np.array([0, 0, math.sin(math.radians(9))])
    P = J.Paint(cw, kit)
    objs = J.scene_objects(film); seen = set()
    for m in J.scene_materials(objs):
        k = _key(m.name)
        if m.name in seen or J.principled(m) is None: continue
        seen.add(m.name)
        if k in ('cw_strata', 'cw_top', 'cw_water', 'ex_floor', 'cw_grass', 'cw_leaf', 'ex_shaft_mat', 'ex_gobo'): continue
        sock, val = J.base_color(m)
        g = cw.G(m.node_tree, kit)
        col = sock if sock is not None else val
        dark = g.mix(1.0, col, (0.55, 0.62, 0.80, 1.0), 'MULTIPLY')
        sh = _night(P, g, dark)
        if k in GLOW:
            c, s = GLOW[k]; sh = _glow_add(g, sh, c, s)
        J.set_surface(m, sh)
    _strata(P, cw, kit, L.strata, land.objects['walls'].material_slots[0].material)
    land.objects['top'].material_slots[0].material = _top(P, cw, kit, land)
    if 'water' in land.objects: _water(cw, kit, land, land.objects['water'].material_slots[0].material)
    done = {}
    for col in bpy.data.collections:
        for po in col.objects:
            for s in po.material_slots:
                if s.material is None: continue
                k = _key(s.material.name)
                if k == 'cw_grass':
                    if s.material.name not in done: done[s.material.name] = _grass(P, cw, kit, 'night_' + s.material.name)
                    s.material = done[s.material.name]
                elif k == 'cw_leaf' and s.material.name not in done:
                    _leaf(P, cw, kit, s.material); done[s.material.name] = s.material
    for o in objs:
        if o.name == 'ex_floor': o.material_slots[0].material = _floor(cw, kit)
        if o.name.startswith(('ex_shaft', 'ex_gobo')): J.hide(film, o)
    # ---- world and light: the sun becomes a cool moon; the museum spots become a faint glow on the finds
    wd = _sky(bpy, cw, kit, md)
    for s in film.built.values(): s['world'] = wd
    sc.world = wd
    J.lights(bpy, film, off_prefix=('ex_fill', 'ex_rim', 'ex_edge_spill'), scale={'ex_spot': 0.25, 'ex_sun': 0.35, 'cl_house': 1.6, 'cl_lamp': 2.5, 'cw_mill': 1.6})
    for o in objs:
        if o.type == 'LIGHT' and o.name == 'ex_sun':
            o.data.color = (0.62, 0.74, 1.0)
            from mathutils import Vector
            o.rotation_euler = Vector(tuple(md)).to_track_quat('Z', 'Y').to_euler()
        elif o.type == 'LIGHT' and o.name.startswith('ex_spot'): o.data.color = (0.55, 1.0, 0.85)
    # ---- fireflies over the grass (the cinematic extras' own, blinking on their own rhythm)
    before = set(bpy.data.objects.keys())
    T = getattr(land, 'trees', None)
    ex.fireflies(kit, land, 70, near=[tuple(p) for p in T] if T is not None and len(T) else None, z=(0.03, 0.30), name='ng_ff')
    for n in set(bpy.data.objects.keys()) - before: J.adopt(film, bpy.data.objects[n])
    # ---- render
    cy = sc.cycles; cy.max_bounces = 3; cy.diffuse_bounces = 1; cy.glossy_bounces = 1; cy.transmission_bounces = 2; cy.transparent_max_bounces = 24
    J.recolor_overlay(film, ink=INK, paper=PAPER)
    J.type_layer(bpy, film)
    ng, N, Lk, base = J.comp_begin(bpy, 'night_comp')
    img = base.outputs['Image']
    gl = N.new('CompositorNodeGlare')
    gl.inputs['Type'].default_value = 'Bloom'; gl.inputs['Quality'].default_value = 'Medium'
    gl.inputs['Threshold'].default_value = 0.35; gl.inputs['Strength'].default_value = 0.65; gl.inputs['Size'].default_value = 0.8
    Lk.new(img, gl.inputs['Image']); img = gl.outputs['Image']
    img = J.vignette(N, Lk, img, W, H, amount=0.30)
    J.comp_end(bpy, ng, img)
