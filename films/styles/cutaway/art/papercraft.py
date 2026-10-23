"""Art direction `papercraft`: layered cut paper, a handmade diorama under a desk lamp.

Every surface becomes flat-coloured card: colours are posterised to a handful of paper tones and multiplied by visible
paper fibre (two crossing stretched noises plus fine grain, also as a bump so the lamp rakes across it). The soil layers
on the cut faces are rebuilt as stacked sheets: each stratum a flat sheet with a deckled, slightly torn edge (a pale
torn-paper core shows along the lower edge), a soft drop shadow cast on the sheet below, and punched paper dots instead of
pebbles. Trees, rocks and the like are flat-shaded (faceted, folded card). The golden-hour rig is swapped for one warm
desk lamp (a large soft sun from the front left, so shadows are soft but real), a cream paper sky, a kraft paper table,
and three standing ridges of layered paper behind the block that cast real soft shadows on each other. God-ray cards are
off. What it changes: materials, world, lights, three extra meshes. No compositor. Render cost vs the reference: about
the same or a little less (no fog, no god rays, no glass-heavy light, simple diffuse shading); the paper bump adds a bit.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _post as P  # noqa: E402
import cutaway as cw  # noqa: E402
from cutaway import srgb  # noqa: E402

PAPER_CREAM = (0.93, 0.86, 0.72)


def posterize(g, col, n):
    """Snap each channel to n levels (flat paper tones)."""
    s = g.sep(col)
    f = lambda ch: g.math('DIVIDE', g.math('FLOOR', g.math('ADD', g.math('MULTIPLY', ch, float(n)), 0.5)), float(n))
    return g.comb(f(s[0]), f(s[1]), f(s[2]))


def paper_filter(levels=7, fib=0.30, scale=380.0, dark=1.0, gamma=False):
    def fn(g, c):
        if dark != 1.0: c = srgb((0.36, 0.25, 0.18))[:3]
        tc = g.node('ShaderNodeTexCoord'); f = P.fibre(g, tc.outputs['Object'], scale)
        if dark == 1.0:
            if gamma:       # posterise in a perceptual space so dark tones keep their hue (used on the seasons loop)
                c = g.vmath('POWER', c, (1 / 2.2,) * 3); c = posterize(g, c, levels); c = g.vmath('POWER', c, (2.2,) * 3)
            else: c = posterize(g, c, levels)
        return g.mix(1.0, c, g.vmath('ADD', (1.0 - fib * 0.5,) * 3, g.vmath('SCALE', (fib,) * 3, scale=f)), 'MULTIPLY')
    return fn


def paper_surface(m, kit, levels=7, dark=1.0, gamma=False, colour=True):
    """Principled materials -> flat card with fibre."""
    for n in m.node_tree.nodes:
        if n.bl_idname != 'ShaderNodeBsdfPrincipled': continue
        g = cw.G(m.node_tree, kit)
        P.set_default_principled(n, **{'Roughness': 0.93, 'Metallic': 0.0, 'Specular IOR Level': 0.12, 'Transmission Weight': 0.0, 'Coat Weight': 0.0,
                                      'Subsurface Weight': 0.0, 'Sheen Weight': 0.0})
        if n.inputs['Roughness'].is_linked:
            for l in list(n.inputs['Roughness'].links): g.L.remove(l)
            n.inputs['Roughness'].default_value = 0.93
        if colour: P.insert_colour_filter(g, n, paper_filter(levels, dark=dark, gamma=gamma))
        # replace any bump with the paper fibre
        if n.inputs['Normal'].is_linked:
            for l in list(n.inputs['Normal'].links): g.L.remove(l)
        tc = g.node('ShaderNodeTexCoord'); f = P.fibre(g, tc.outputs['Object'], 380.0)
        b = g.node('ShaderNodeBump', ins={'Strength': 0.35, 'Height': f, 'Distance': 0.0015}); g.link(b.outputs['Normal'], n.inputs['Normal'])


def strata_paper(film, kit, land):
    """Rebuild the cut-face material as stacked sheets (reads the layers off the kit's own strata ramps)."""
    old = land.mats['strata']; nt = old.node_tree
    ramps = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeValToRGB']
    col_r = [r for r in ramps if r.color_ramp.interpolation != 'CONSTANT'][0]; peb_r = [r for r in ramps if r.color_ramp.interpolation == 'CONSTANT'][0]
    div = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeMath' and n.operation == 'DIVIDE' and abs(n.inputs[1].default_value) > 0.5][0]
    total = float(div.inputs[1].default_value)
    els = [(e.position, tuple(e.color)[:3]) for e in col_r.color_ramp.elements]
    bands = []                                            # (start fac, linear colour)
    for k in range(0, len(els), 2): bands.append((els[k][0] if k else 0.0, els[k][1]))
    pden = [tuple(e.color)[0] for e in peb_r.color_ramp.elements]
    starts = [b[0] if i else 0.0 for i, b in enumerate(bands)]
    # in the kit the band edges sit `soft` earlier than the colour stops; the true edge of band k is the start of its first stop minus soft
    soft = 0.012 / total
    edges = [0.0] + [max(0.0, s - soft) for s in starts[1:]]
    m = old; g = cw.G(nt, kit)
    old_p = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]       # keeps the egg openings patched in after it
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    sd = g.attr('sd').outputs['Fac']; hz = g.math('ADD', sx[0], sx[1])
    wob = g.noise(g.comb(hz, 0.0, g.math('MULTIPLY', sd, 0.2)), 2.2, 3.0)
    deck = g.noise(g.comb(hz, g.math('MULTIPLY', sx[2], 1.0), 0.0), 140.0, 5.0, 0.7)
    deck2 = g.noise(g.comb(g.math('MULTIPLY', hz, 7.0), g.math('MULTIPLY', sx[2], 1.0), 0.0), 420.0, 2.0, 0.6)
    s = g.math('ADD', sd, g.math('ADD', g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.045),
                               g.math('ADD', g.math('MULTIPLY', g.math('SUBTRACT', deck.outputs['Fac'], 0.5), 0.016), g.math('MULTIPLY', g.math('SUBTRACT', deck2.outputs['Fac'], 0.5), 0.006))))
    fac = g.math('DIVIDE', s, total)
    def const_ramp(vals_pos, vals):
        n = g.node('ShaderNodeValToRGB'); cr = n.color_ramp; cr.interpolation = 'CONSTANT'
        while len(cr.elements) < len(vals_pos): cr.elements.new(0.5)
        for el, p, v in zip(cr.elements, vals_pos, vals): el.position = p; el.color = v
        g.put(n, 'Fac', fac); return n.outputs['Color']
    # a tiny bit of squash: eps to keep positions strictly increasing
    pos_ = [0.0] + [e + 1e-5 * i for i, e in enumerate(edges[1:], 1)]
    col = const_ramp(pos_, [b[1] + (1.0,) for b in bands])
    start = g.sep(const_ramp(pos_, [(e, e, e, 1.0) for e in edges]))[0]
    nxt = [edges[i + 1] if i + 1 < len(edges) else 9.0 for i in range(len(edges))]
    endv = g.sep(const_ramp(pos_, [(e, e, e, 1.0) for e in nxt]))[0]
    pd = g.sep(const_ramp(pos_, [(min(1.0, p * 1.0),) * 3 + (1.0,) for p in pden]))[0]
    d = g.math('SUBTRACT', fac, start)                        # distance below the top of this sheet, in fac units
    lam = 0.016 / total
    shadow = g.math('EXPONENT', g.math('MULTIPLY', d, -1.0 / lam))
    col = g.mix(g.math('MULTIPLY', shadow, 0.42), col, g.mix(1.0, col, (0.12, 0.07, 0.05), 'MULTIPLY'))
    # torn pale core along the lower edge of each sheet
    tear = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', endv, fac), 1.0 / (0.0035 / total)), clamp=True)
    tear = g.math('MULTIPLY', tear, g.math('GREATER_THAN', endv, 8.0 * 0 + 0.0))
    tear = g.math('MULTIPLY', tear, g.math('LESS_THAN', endv, 5.0))
    core = g.mix(g.noise(pos, 300.0, 3.0).outputs['Fac'], srgb((0.96, 0.92, 0.82)), srgb((0.86, 0.80, 0.68)))
    col = g.mix(g.math('MULTIPLY', tear, 0.85), col, core)
    # punched paper dots in place of pebbles
    vp = g.voronoi(pos, 30.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    radius = g.math('MULTIPLY', g.math('MULTIPLY', pd, 0.40), g.math('MULTIPLY_ADD', rr[0], 0.8, 0.4))
    peb = g.math('MULTIPLY', g.math('SUBTRACT', radius, vp.outputs['Distance']), 300.0, clamp=True)
    pcol = g.mix(rr[1], srgb((0.55, 0.50, 0.45)), srgb((0.86, 0.80, 0.68)))
    pcol = g.mix(g.math('MULTIPLY', rr[2], 0.5), pcol, srgb((0.70, 0.52, 0.36)))
    rim = g.math('MULTIPLY', g.math('SUBTRACT', radius, vp.outputs['Distance']), 300.0, clamp=True)
    inner = g.math('MULTIPLY', g.math('SUBTRACT', radius * 0.0 + g.math('SUBTRACT', radius, 0.012), vp.outputs['Distance']), 300.0, clamp=True) if False else None
    col = g.mix(peb, col, pcol)
    # roots near the top are thin dark threads in the kit; here a few torn dark-paper strips near the top of the topsoil
    f = P.fibre(g, pos, 380.0)
    col = g.mix(1.0, col, g.vmath('ADD', (0.85,) * 3, g.vmath('SCALE', (0.30,) * 3, scale=f)), 'MULTIPLY')
    p = old_p
    for k in ('Base Color', 'Normal'):
        for l in list(p.inputs[k].links): g.L.remove(l)
    g.link(col, p.inputs['Base Color']); p.inputs['Roughness'].default_value = 0.95
    P.set_default_principled(p, **{'Specular IOR Level': 0.1})
    h = g.math('ADD', g.math('MULTIPLY', start, 6.0), g.math('MULTIPLY', f, 0.02))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.9, 'Height': h, 'Distance': 0.004}); g.link(b.outputs['Normal'], p.inputs['Normal'])


def patchwork(m, kit):
    """The meadow top as patches of cut paper: per-patch tone, a thin shadow line along each patch edge (season colours stay)."""
    nt = m.node_tree; g = cw.G(nt, kit); p = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]
    tcn = g.node('ShaderNodeTexCoord'); pos = tcn.outputs['Object']
    vo = g.voronoi(pos, 11.0, 'F1'); ve = g.voronoi(pos, 11.0, 'DISTANCE_TO_EDGE')
    tone = g.math('ADD', 0.95, g.math('MULTIPLY', g.sep(vo.outputs['Color'])[0], 0.55))
    edge = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', ve.outputs['Distance'], 42.0), clamp=True)
    def fn(g_, c):
        c = g_.mix(1.0, c, g_.vmath('SCALE', (1.0, 1.0, 1.0), scale=tone), 'MULTIPLY')
        return g_.mix(g_.math('MULTIPLY', edge, 0.5), c, g_.mix(1.0, c, (0.35, 0.30, 0.25), 'MULTIPLY'))
    P.insert_colour_filter(g, p, fn)


def strata_patch(film, kit, m):
    """The seasons loop's own strata material (sz_strata: snow cap, gold vein, frog chamber, roots stay): hard sheet edges,
    deckle, a drop shadow under each sheet and a torn pale core, added on top of its own colour chain."""
    nt = m.node_tree; g = cw.G(nt, kit)
    ramps = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeValToRGB']
    col_r = [r for r in ramps if r.color_ramp.interpolation != 'CONSTANT'][0]
    div = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeMath' and n.operation == 'DIVIDE' and abs(n.inputs[1].default_value) > 0.5][0]
    total = float(div.inputs[1].default_value)
    els = [e.position for e in col_r.color_ramp.elements]
    starts = [0.0] + [els[k] for k in range(2, len(els), 2)]
    soft = 0.012 / total; edges = [0.0] + [max(0.0, x - soft) for x in starts[1:]]
    col_r.color_ramp.interpolation = 'CONSTANT'
    # deckle on the band edges: finer noise added to the depth that feeds the bands
    src = div.inputs[0].links[0].from_socket; g.L.remove(div.inputs[0].links[0])
    tcn = g.node('ShaderNodeTexCoord'); pos = tcn.outputs['Object']; sx = g.sep(pos); hz = g.math('ADD', sx[0], sx[1])
    deck = g.noise(g.comb(hz, sx[2], 0.0), 140.0, 5.0, 0.7); deck2 = g.noise(g.comb(g.math('MULTIPLY', hz, 7.0), sx[2], 0.0), 420.0, 2.0, 0.6)
    g.link(g.math('ADD', src, g.math('ADD', g.math('MULTIPLY', g.math('SUBTRACT', deck.outputs['Fac'], 0.5), 0.016), g.math('MULTIPLY', g.math('SUBTRACT', deck2.outputs['Fac'], 0.5), 0.006))), div.inputs[0])
    fac = div.outputs[0]
    for n in nt.nodes:                                       # the kit's 60/m mottling becomes paper-scale grain
        if n.bl_idname == 'ShaderNodeTexNoise' and abs(n.inputs['Scale'].default_value - 60.0) < 1e-3: n.inputs['Scale'].default_value = 800.0
    pos_ = [0.0] + [e + 1e-5 * i for i, e in enumerate(edges[1:], 1)]
    def const_ramp(vals):
        n = g.node('ShaderNodeValToRGB'); cr = n.color_ramp; cr.interpolation = 'CONSTANT'
        while len(cr.elements) < len(pos_): cr.elements.new(0.5)
        for el, p_, v in zip(cr.elements, pos_, vals): el.position = p_; el.color = (v, v, v, 1.0)
        g.put(n, 'Fac', fac); return g.sep(n.outputs['Color'])[0]
    start = const_ramp(edges); endv = const_ramp([edges[i + 1] if i + 1 < len(edges) else 9.0 for i in range(len(edges))])
    d = g.math('SUBTRACT', fac, start)
    shadow = g.math('EXPONENT', g.math('MULTIPLY', d, -total / 0.024))
    tear = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('SUBTRACT', endv, fac), total / 0.0035), clamp=True)
    tear = g.math('MULTIPLY', tear, g.math('LESS_THAN', endv, 5.0))
    core = g.mix(g.noise(pos, 300.0, 3.0).outputs['Fac'], srgb((0.96, 0.92, 0.82)), srgb((0.86, 0.80, 0.68)))
    f = P.fibre(g, pos, 380.0)
    def fn(g_, c):
        c = g_.mix(g_.math('MULTIPLY', shadow, 0.6), c, g_.mix(1.0, c, (0.12, 0.07, 0.05), 'MULTIPLY'))
        c = g_.mix(g_.math('MULTIPLY', tear, 0.85), c, core)
        return g_.mix(1.0, c, g_.vmath('ADD', (0.85,) * 3, g_.vmath('SCALE', (0.30,) * 3, scale=f)), 'MULTIPLY')
    p = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]
    P.insert_colour_filter(g, p, fn); p.inputs['Roughness'].default_value = 0.95
    P.set_default_principled(p, **{'Specular IOR Level': 0.1})


def ridges(film, kit, land, soft=False):
    """Three standing sheets of layered paper behind the block: wavy tops, flat colours, real shadows on each other."""
    bpy = kit.bpy; z0 = -land.depth - 0.001
    k_ = (float(land.size[0]) if hasattr(land.size, '__len__') else float(land.size)) / 4.0
    specs = [(5.4, 3.0, (0.80, 0.62, 0.42), 1.0), (7.0, 3.8, (0.55, 0.64, 0.50), 2.3), (8.8, 4.8, (0.40, 0.52, 0.52), 3.7), (10.8, 6.0, (0.78, 0.54, 0.46), 5.1)]
    out = []
    if soft:      # the loop: pastel, lower and farther, so the title and the seasons stay readable
        pas = [(0.93, 0.80, 0.62), (0.82, 0.87, 0.76), (0.72, 0.82, 0.82), (0.94, 0.80, 0.74)]
        specs = [(d_ * 1.25, h_ * 0.65, pas[i], p_) for i, (d_, h_, c_, p_) in enumerate(specs)]
    specs = [(d_ * k_, h_ * k_, c_, p_) for d_, h_, c_, p_ in specs]
    for k, (dist, hgt, c, ph), ax in [(k, sp, a) for k, sp in enumerate(specs) for a in (0, 1)]:
        N = 220; xs = np.linspace(-16, 16, N)
        top = hgt * (0.62 + 0.20 * np.sin(xs * 0.31 + ph) + 0.12 * np.sin(xs * 0.83 + ph * 2.1) + 0.06 * np.sin(xs * 2.1 + ph))
        top = np.maximum(top, 0.35 * hgt)
        V = []; Fc = []
        for i, x in enumerate(xs):
            d_ = dist + 0.15 * math.sin(x * 0.2 + ph)
            if ax == 0: V += [(x, d_, z0), (x, d_, z0 + top[i])]
            else: V += [(-d_, x, z0), (-d_, x, z0 + top[i])]
        for i in range(N - 1): Fc.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
        m = cw._new_mat(bpy, f'pc_ridge{k}_{ax}'); g = cw.G(m.node_tree, kit); tcn = g.node('ShaderNodeTexCoord')
        f = P.fibre(g, tcn.outputs['Object'], 6.0)
        cc = g.mix(1.0, srgb(c), g.vmath('ADD', (0.82,) * 3, g.vmath('SCALE', (0.36,) * 3, scale=f)), 'MULTIPLY')
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': cc, 'Roughness': 0.95}); P.set_default_principled(p, **{'Specular IOR Level': 0.1}); cw._finish(g, p)
        ob = cw.mk_mesh(bpy, f'pc_ridge{k}_{ax}', V, Fc, [m], None, False, kit.coll); out.append(ob)
    return out


def apply(bpy, film, ctx):
    name, st = P.sets_of(bpy, film)[0]; kit = st['kit']; land = st.get('land')
    sc = bpy.context.scene
    # ---- materials
    kitscene = P.is_kit(film)
    for m in list(bpy.data.materials):
        if not m.node_tree or m.name.startswith('cl_') or m.name.startswith('pc_'): continue
        if m.name in ('cw_water', 'ex_shaft_mat', 'ex_gobo') or m.name.startswith('cw_window') or m.name.startswith('cw_lamphead') or m.name == 'ex_floor': continue
        if m.name in ('cw_strata', 'sz_strata') or m.name in ('sz_water', 'sz_ice', 'sz_haze', 'sz_fog', 'sz_titlemat'): continue
        if m.name == 'cw_floor': paper_surface(m, kit, colour=False); continue        # the loop drives the floor colour by season
        paper_surface(m, kit, dark=0.5 if m.name in ('ex_cavity', 'ex_dig') else 1.0, gamma=kitscene)
    if kitscene and bpy.data.materials.get('sz_strata'): strata_patch(film, kit, bpy.data.materials['sz_strata'])
    elif land is not None and 'strata' in getattr(land, 'mats', {}): strata_paper(film, kit, land)
    # ---- flat shading on the folded-card things
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.data: continue
        names = {mm.name for mm in o.data.materials if mm}
        if names & {'cw_leaf', 'cw_rock_mat', 'cw_bankrock_mat', 'cw_bark', 'cw_roof', 'cw_wall', 'cw_pebble_mat', 'ex_bone', 'ex_white', 'ex_terracotta'} or any(n.startswith(('cw_leaf', 'cw_roof', 'cw_wall', 'cw_rock', 'sz_leaf', 'sz_needles')) for n in names):
            o.data.polygons.foreach_set('use_smooth', [False] * len(o.data.polygons)); o.data.update()
    if kitscene:
        for o in list(bpy.data.objects):
            if o.name == 'sz_grass': o.hide_render = True      # real blades off: the meadow is cut paper (patchwork on the top material)
        topm = bpy.data.materials.get('sz_top')
        if topm: patchwork(topm, kit)
    P.hide_shafts(film)
    for o in P.all_scene_objects(film):
        if o.name.startswith('ex_gobo'): o.hide_render = True
    st['hidden'] = {o.name for o in st['objs'] if o.hide_render}
    # ---- the table and the sky
    fl = bpy.data.materials.get('ex_floor')
    if fl:
        nt = fl.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        g = cw.G(nt, kit); tcn = g.node('ShaderNodeTexCoord'); f = P.fibre(g, tcn.outputs['Object'], 9.0, 4.0)
        cc = g.mix(1.0, srgb((0.86, 0.72, 0.52)), g.vmath('ADD', (0.8,) * 3, g.vmath('SCALE', (0.4,) * 3, scale=f)), 'MULTIPLY')
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': cc, 'Roughness': 0.95}); P.set_default_principled(p, **{'Specular IOR Level': 0.1}); cw._finish(g, p)
    wd = st.get('world') or sc.world
    if wd is None: wd = bpy.data.worlds.new('pc_world'); sc.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    g = cw.G(nt, kit); tcn = g.node('ShaderNodeTexCoord'); el = g.sep(g.vmath('NORMALIZE', tcn.outputs['Generated']))[2]
    sky = g.mix(g.math('POWER', g.math('MAXIMUM', el, 0.0), 0.5), srgb((0.99, 0.90, 0.74)), srgb((0.95, 0.74, 0.58)))
    bgc = g.node('ShaderNodeBackground', ins={'Color': sky, 'Strength': 0.85}); bgl = g.node('ShaderNodeBackground', ins={'Color': srgb((1.0, 0.88, 0.72)), 'Strength': 0.55})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader'); g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bgl, mx.inputs[1]); g.link(bgc, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
    # ---- the desk lamp
    for ld in bpy.data.lights:
        if ld.name == 'ex_sun':
            ld.energy = 4.2; ld.color = (1.0, 0.80, 0.56); ld.angle = math.radians(9.0)
        elif ld.name == 'ex_rim': ld.energy = 0.0
        elif ld.name == 'ex_fill': ld.energy = 500.0; ld.color = (1.0, 0.86, 0.72)
    sun = bpy.data.objects.get('ex_sun')
    if sun:
        az, el_ = math.radians(-72.0), math.radians(42.0)
        sun.rotation_euler = (math.pi / 2 - el_, 0.0, az + math.pi / 2)          # points from (az, el) toward the block
        sun.rotation_mode = 'XYZ'
    st['ridges'] = ridges(film, kit, land, soft=kitscene) if land is not None else []
    sc.view_settings.exposure = 0.2


def frame(bpy, film, ctx, t, shot):
    pass
