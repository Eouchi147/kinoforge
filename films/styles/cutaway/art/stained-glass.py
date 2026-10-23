"""Cutaway art direction `stained-glass`: a leaded glass window in the Art Nouveau manner (secular, no figures).

The look: the whole frame becomes a window. Every surface is cut into panes of jewel-coloured translucent glass
(ruby, amber, gold, emerald, sapphire, amethyst) held by thick dark lead lines (came): the cut faces are bands of glass,
each band split into long irregular panes, the band edges leaded; pebbles are small round roundels; the sky is a fan of
flat panes graded from sapphire to amber, with the sun as a leaded rosette of rays and rings; the land, trees, houses,
finds and animals are panes in their own colour, saturated. Each pane varies a little in tint and glows brighter at its
centre as if lit from behind, with a faint streaky glass texture and seed bubbles. The compositor adds lead along every
outline (an edge filter on the flat render, thickened), a soft glow of light through the glass and a vignette; the words
stay crisp in their own layer (white plates, lead-black ink). The grass blades and small flowers are hidden (as glass
they would be noise); the turf is cut into green panes instead.

What it changes: every material (emission glass with procedural cells and lead), the world (paned sky and a sun
rosette), the floor (dark leaded slabs), the grass and flowers (hidden), the lights (no effect: the glass is emissive;
only the sun is kept for nothing but shadows, which do not show), view transform Standard, the compositor (edge lead,
glow, vignette).

Works on the line films and on the seasons loop (a kit scene, through art/_adapter.py): there the loop's season-driven
ground (with its snow), leaves (blossom, autumn, thinning), ice and life keep their own colours as glass, the grass and
flowers are hidden as on the line, the ground under the block takes the loop's season backdrop colour, and the title is
set in pale glass white (it has no plate there).

Render cost vs the reference: cheaper. Emission only, no grass blades (the most expensive geometry), 2 bounces: about
0.3 to 0.5 times the reference per frame, plus 1 to 2 s of compositing at 1280x720.
"""
import importlib.util
import math
import os

import numpy as np

_s = importlib.util.spec_from_file_location('kf_art__jewel', os.path.join(os.path.dirname(os.path.abspath(__file__)), '_jewel.py'))
J = importlib.util.module_from_spec(_s); _s.loader.exec_module(J)
lin = J.lin

LEAD = (0.035, 0.035, 0.045)
RUBY = (0.78, 0.10, 0.18)
AMBER = (0.98, 0.58, 0.12)
GOLD = (1.00, 0.80, 0.26)
EMERALD = (0.10, 0.62, 0.32)
SAPPHIRE = (0.10, 0.24, 0.72)
AMETHYST = (0.48, 0.20, 0.66)
TEAL = (0.06, 0.52, 0.58)
OPAL = (0.92, 0.90, 0.80)

STRATA_GLASS = {'topsoil': (0.40, 0.14, 0.12), 'sand': GOLD, 'clay': AMBER, 'loam': RUBY, 'gravel': (0.30, 0.42, 0.50),
                'ochre': (1.0, 0.70, 0.20), 'limestone': TEAL, 'bedrock': SAPPHIRE}
FALLBACK = [(0.40, 0.14, 0.12), GOLD, AMBER, RUBY, (0.30, 0.42, 0.50), TEAL, SAPPHIRE, AMETHYST]
RECOLOR = {'cw_wall': OPAL, 'cw_roof': RUBY, 'cw_door': (0.40, 0.14, 0.12), 'cw_window': GOLD, 'cw_millwood': (0.62, 0.32, 0.14),
           'cw_bridgewood': (0.66, 0.36, 0.16), 'cw_rock_mat': (0.40, 0.52, 0.70), 'cw_bankrock_mat': (0.55, 0.62, 0.74),
           'cw_pebble_mat': (0.30, 0.50, 0.66), 'cw_bottom': (0.08, 0.10, 0.30), 'cw_bark': (0.46, 0.22, 0.12), 'cw_leaf': EMERALD,
           'cw_lily': EMERALD, 'cw_lilyflower': (1.0, 0.72, 0.84), 'cw_reed': (0.30, 0.62, 0.24), 'cw_cattail': (0.56, 0.26, 0.10),
           'ex_cavity': (0.20, 0.10, 0.24), 'ex_dig': (0.12, 0.14, 0.36), 'ex_terracotta': AMBER, 'ex_bone': OPAL, 'ex_tooth': OPAL,
           'ex_gold': GOLD, 'ex_goldglow': GOLD, 'ex_chestwood': (0.56, 0.22, 0.10), 'ex_nacre': (0.80, 0.86, 0.98), 'ex_trilo': (0.98, 0.84, 0.60),
           'ex_amethyst': AMETHYST, 'ex_agate': (0.36, 0.24, 0.62), 'ex_quartz': OPAL, 'ex_masonry': (0.62, 0.60, 0.70), 'ex_wellstone': (0.66, 0.64, 0.74)}


def _key(n): return n.split('.')[0]


def glass(g, col, pos, scale=14.0, lead=0.03, sat=1.6, var=0.18, glow=1.0, bubbles=True):
    """Leaded glass on any surface: voronoi panes in object space, per-pane tint, brighter centres, streaks, bubbles."""
    hs = g.node('ShaderNodeHueSaturation', ins={'Saturation': sat, 'Value': 1.1, 'Color': col}); col = hs.outputs['Color']
    ve = g.voronoi(pos, scale, 'DISTANCE_TO_EDGE'); vf = g.voronoi(pos, scale, 'F1'); rr = g.sep(vf.outputs['Color'])
    de = ve.outputs['Distance']                                        # 0 at a pane edge, about 0.5 at its centre
    col = g.mix(1.0, col, g.math('ADD', 1.0 - var, g.math('MULTIPLY', rr[0], 2 * var)), 'MULTIPLY')
    col = g.mix(g.math('MULTIPLY', rr[1], 0.12), col, lin((1.0, 0.85, 0.55)))
    light = g.math('ADD', 0.72, g.math('MULTIPLY', g.math('MULTIPLY', de, 3.0, clamp=True), 0.38))
    st = g.noise(g.comb(g.math('MULTIPLY', g.sep(pos)[0], 3.0), g.math('MULTIPLY', g.sep(pos)[2], 40.0), g.math('MULTIPLY', g.sep(pos)[1], 3.0)), 3.0, 3.0, 0.6)
    light = g.math('MULTIPLY', light, g.math('ADD', 0.90, g.math('MULTIPLY', st.outputs['Fac'], 0.2)))
    bub = g.voronoi(pos, scale * 5.0, 'F1')
    bubble = g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', 0.08, bub.outputs['Distance']), 25.0, clamp=True), g.math('GREATER_THAN', g.sep(bub.outputs['Color'])[0], 0.7))
    if bubbles: light = g.math('ADD', light, g.math('MULTIPLY', bubble, 0.25))
    c = g.mix(1.0, col, light, 'MULTIPLY')
    is_lead = g.math('LESS_THAN', de, lead)
    c = g.mix(is_lead, c, lin(LEAD))
    e = g.node('ShaderNodeEmission', ins={'Color': c, 'Strength': glow}); return e


def _sky(bpy, cw, kit, sd):
    wd = bpy.data.worlds.new('glass_world')
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree; nt.nodes.clear(); g = cw.G(nt, kit)
    tc = g.node('ShaderNodeTexCoord'); d = g.vmath('NORMALIZE', tc.outputs['Generated'])
    # panes: voronoi cells on the sphere, each flat-coloured by the sky gradient at its own centre
    vf = g.voronoi(d, 7.0, 'F1'); ve = g.voronoi(d, 7.0, 'DISTANCE_TO_EDGE')
    cpos = g.vmath('NORMALIZE', vf.outputs['Position']); cz = g.sep(cpos)[2]
    ce = g.math('DIVIDE', g.math('MAXIMUM', g.math('ARCSINE', cz), 0.0), math.pi / 2)
    toward = g.math('POWER', g.math('MAXIMUM', g.vmath('DOT_PRODUCT', cpos, tuple(sd)), 0.0), 2.0)
    sky = g.ramp(ce, [(0.0, (1.0, 0.66, 0.30)), (0.08, (0.92, 0.40, 0.36)), (0.22, (0.56, 0.26, 0.58)), (0.45, (0.20, 0.26, 0.70)), (1.0, (0.06, 0.10, 0.42))])
    sky = g.mix(g.math('MULTIPLY', toward, 0.6), sky, lin(GOLD))
    rr = g.sep(vf.outputs['Color'])
    sky = g.mix(1.0, sky, g.math('ADD', 0.85, g.math('MULTIPLY', rr[0], 0.3)), 'MULTIPLY')
    light = g.math('ADD', 0.78, g.math('MULTIPLY', g.math('MULTIPLY', ve.outputs['Distance'], 3.0, clamp=True), 0.3))
    col = g.mix(1.0, sky, light, 'MULTIPLY')
    lead = g.math('LESS_THAN', ve.outputs['Distance'], 0.011)
    # the sun: a rosette of rays and rings around its direction
    ang = g.math('ARCCOSINE', g.math('MINIMUM', g.vmath('DOT_PRODUCT', d, tuple(sd)), 1.0))
    up = np.array([0, 0, 1.0]); a1 = np.cross(sd, up); a1 /= np.linalg.norm(a1); a2 = np.cross(sd, a1)
    phi = g.math('ARCTAN2', g.vmath('DOT_PRODUCT', d, tuple(a2)), g.vmath('DOT_PRODUCT', d, tuple(a1)))
    sector = g.math('FRACT', g.math('DIVIDE', g.math('ADD', phi, math.pi), 2 * math.pi / 20))
    sec_lead = g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', sector, 0.5)), 0.03)
    alt = g.math('MODULO', g.math('FLOOR', g.math('DIVIDE', g.math('ADD', phi, math.pi), 2 * math.pi / 20)), 2.0)
    rays = g.math('LESS_THAN', ang, 0.62)
    ray_col = g.mix(alt, lin((1.0, 0.74, 0.30)), lin((1.0, 0.56, 0.22)))
    ray_col = g.mix(1.0, ray_col, g.math('SUBTRACT', 1.15, g.math('MULTIPLY', ang, 0.6)), 'MULTIPLY')
    col = g.mix(rays, col, ray_col)
    lead = g.math('MAXIMUM', g.math('MULTIPLY', lead, g.math('SUBTRACT', 1.0, rays)), g.math('MULTIPLY', rays, sec_lead))
    disc = g.math('LESS_THAN', ang, 0.13)
    col = g.mix(disc, col, lin((1.0, 0.95, 0.72)))
    for r in (0.13, 0.30, 0.62):
        ring = g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', ang, r)), 0.005)
        lead = g.math('MAXIMUM', lead, ring)
    lead = g.math('MULTIPLY', lead, g.math('SUBTRACT', 1.0, g.math('LESS_THAN', ang, 0.121)))
    col = g.mix(lead, col, lin(LEAD))
    bg_cam = g.node('ShaderNodeBackground', ins={'Color': col, 'Strength': 1.0})
    bg_light = g.node('ShaderNodeBackground', ins={'Color': lin((0.5, 0.5, 0.5)), 'Strength': 0.0})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bg_light, mx.inputs[1]); g.link(bg_cam, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
    return wd


def _strata(cw, kit, layers, m):
    g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    sd = g.attr('sd').outputs['Fac']; hz = g.math('ADD', sx[0], sx[1])
    wob = g.noise(g.comb(hz, 0.0, g.math('MULTIPLY', sd, 0.2)), 1.6, 2.0)
    s = g.math('ADD', sd, g.math('MULTIPLY', g.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.07))
    total = sum(l[1] for l in layers[:-1]) + 0.6; stops = []; acc = 0.0; edges = []; pst = []
    for k, l in enumerate(layers):
        c = STRATA_GLASS.get(l[0], FALLBACK[k % len(FALLBACK)]); a = acc / total
        stops.append((a, c)); pst.append((a, (l[3],) * 3)); acc += l[1]
        if k < len(layers) - 1: edges.append(acc)
    fac = g.math('DIVIDE', s, total)
    col = g.ramp(fac, stops, 'CONSTANT'); pden = g.sep(g.ramp(fac, pst, 'CONSTANT'))[0]
    # long panes along the bands: the cell space is stretched along the face
    cell = g.comb(g.math('MULTIPLY', hz, 0.45), g.math('MULTIPLY', s, 1.0), 0.0)
    e = glass(g, col, cell, scale=6.0, lead=0.022, sat=1.4)
    # leaded band edges and pebble roundels
    lead = None
    for b in edges:
        ln = g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', s, b)), 0.0035)
        lead = ln if lead is None else g.math('MAXIMUM', lead, ln)
    vp = g.voronoi(pos, 22.0, 'F1'); rr = g.sep(vp.outputs['Color'])
    rad = g.math('MULTIPLY', g.math('MULTIPLY', pden, 0.42), g.math('MULTIPLY_ADD', rr[0], 0.5, 0.5))
    inside = g.math('LESS_THAN', vp.outputs['Distance'], rad)
    ring = g.math('MULTIPLY', g.math('LESS_THAN', vp.outputs['Distance'], g.math('ADD', rad, 0.04)), g.math('SUBTRACT', 1.0, inside))
    ring = g.math('MULTIPLY', ring, g.math('GREATER_THAN', rad, 0.02))
    lead = g.math('MAXIMUM', lead, ring)
    rcol = g.mix(rr[1], lin((0.80, 0.90, 1.0)), lin((1.0, 0.86, 0.50)))
    re = g.node('ShaderNodeEmission', ins={'Color': g.mix(1.0, rcol, g.math('SUBTRACT', 1.1, g.math('MULTIPLY', vp.outputs['Distance'], 1.5)), 'MULTIPLY'), 'Strength': 1.0})
    m1 = g.node('ShaderNodeMixShader'); g.link(g.math('MULTIPLY', inside, g.math('GREATER_THAN', rad, 0.02)), m1.inputs[0]); g.link(e, m1.inputs[1]); g.link(re, m1.inputs[2])
    le = g.node('ShaderNodeEmission', ins={'Color': lin(LEAD), 'Strength': 1.0})
    m2 = g.node('ShaderNodeMixShader'); g.link(lead, m2.inputs[0]); g.link(m1, m2.inputs[1]); g.link(le, m2.inputs[2])
    J.under_mask(m, m2)


def _top(cw, kit, land):
    m = cw._new_mat(kit.bpy, 'glass_top'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    A = {k: g.attr(k).outputs['Fac'] for k in ('w_grass', 'w_sand', 'w_rock')}
    n = g.noise(pos, 1.2, 2.0)
    green = g.mix(n.outputs['Fac'], lin((0.12, 0.50, 0.20)), lin((0.36, 0.70, 0.22)))
    col = g.mix(A['w_sand'], lin((0.40, 0.16, 0.10)), lin(GOLD))
    col = g.mix(A['w_rock'], col, lin(OPAL))
    col = g.mix(A['w_grass'], col, green)
    if land.level is not None:
        under = g.math('MULTIPLY', g.math('SUBTRACT', land.level + 0.004, sx[2]), 200.0, clamp=True)
        col = g.mix(under, col, lin(TEAL))
    cw._finish(g, glass(g, col, pos, scale=5.0, lead=0.022, sat=1.3)); return m


def _water(cw, kit, land, m):
    g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; sx = g.sep(pos)
    lv = land.level if land.level is not None else 0.0
    dd = g.math('MULTIPLY', g.math('SUBTRACT', lv, sx[2]), 1 / 0.42, clamp=True)
    col = g.ramp(dd, [(0.0, (0.30, 0.80, 0.88)), (0.5, (0.08, 0.42, 0.70)), (1.0, (0.06, 0.16, 0.50))], 'CONSTANT')
    cell = g.comb(g.math('MULTIPLY', g.math('ADD', sx[0], sx[1]), 0.6), g.math('MULTIPLY', sx[2], 2.0), g.math('MULTIPLY', sx[1], 0.6))
    e = glass(g, col, cell, scale=6.0, lead=0.022, sat=1.2)
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader'); g.put(mx, 0, 0.85); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2])
    J.under_mask(m, mx)


def _floor(cw, kit, tinted=False):
    """Dark leaded slabs; tinted=True (the seasons loop) takes its colour from an RGB node set each frame from the loop's
    own season backdrop, so the window's ground changes with the year."""
    m = cw._new_mat(kit.bpy, 'glass_floor'); g = cw.G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    rgb = g.node('ShaderNodeRGB'); rgb.outputs[0].default_value = lin((0.10, 0.14, 0.30))
    e = glass(g, rgb.outputs[0] if tinted else lin((0.10, 0.14, 0.30)), tc.outputs['Object'], scale=0.9, lead=0.02, sat=1.0 if not tinted else 1.3, glow=0.55 if not tinted else 0.85)
    cw._finish(g, e); return m, rgb


def apply(bpy, film, ctx):
    cw = film.cw; sc = bpy.context.scene; W, H = ctx['W'], ctx['H']
    st = next(iter(film.built.values())); kit = st['kit']; land = st['land']; L = st['L']
    rig = st.get('rig'); sd = np.asarray(rig['sun_dir'] if rig else (-0.6, 0.6, 0.35), float); sd = sd / np.linalg.norm(sd)
    kitscene = J.is_kit(film); film._glass = {}
    objs = J.scene_objects(film); seen = set()
    for m in J.scene_materials(objs):
        k = _key(m.name)
        if m.name in seen: continue
        seen.add(m.name)
        if k in ('cw_strata', 'cw_top', 'cw_water', 'ex_floor', 'ex_shaft_mat', 'ex_gobo') or m.name.startswith('ex_shaft'): continue
        g = cw.G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
        if k in RECOLOR: col = lin(RECOLOR[k])
        else:
            sock, val = J.base_color(m)
            if sock is None and val is None: continue
            col = sock if sock is not None else val
        big = k == 'sz_top'     # the seasons ground (its own season colour and snow), cut in large panes
        # on the seasons loop the many small things (fallen leaves, flakes, canopies, animals) get no inner lead (it
        # turned them black at this distance): one tinted pane each, outlined by the edge lead in the compositor
        ld = 0.022 if big else (0.0 if kitscene else 0.025)
        J.under_mask(m, glass(g, col, tc.outputs['Object'], scale=5.0 if big else 14.0, lead=ld, bubbles=big))
    _strata(cw, kit, L.strata, land.objects['walls'].material_slots[0].material)
    if not kitscene: land.objects['top'].material_slots[0].material = _top(cw, kit, land)
    if 'water' in land.objects: _water(cw, kit, land, land.objects['water'].material_slots[0].material)
    for o in objs:
        if o.name == 'ex_floor': o.material_slots[0].material = _floor(cw, kit)[0]
        if o.name == 'cw_floor':
            src = o.material_slots[0].material; m, rgb = _floor(cw, kit, tinted=kitscene); o.material_slots[0].material = m
            film._glass['bg'] = (J.principled(src), rgb)
        if o.name in ('cw_grass', 'cw_flowers', 'sz_grass', 'sz_flowers', 'sz_haze') or o.name.startswith(('ex_shaft', 'ex_gobo')): J.hide(film, o)
    wd = _sky(bpy, cw, kit, sd)
    for s in film.built.values(): s['world'] = wd
    sc.world = wd
    cy = sc.cycles; cy.max_bounces = 2; cy.diffuse_bounces = 0; cy.glossy_bounces = 0; cy.transmission_bounces = 1
    cy.transparent_max_bounces = max(16, cy.transparent_max_bounces)
    sc.view_settings.view_transform = 'Standard'
    try: sc.view_settings.look = 'None'
    except Exception: pass
    J.recolor_overlay(film, ink=(0.99, 0.96, 0.86) if kitscene else (0.03, 0.03, 0.04), paper=(0.98, 0.97, 0.94))
    J.type_layer(bpy, film)
    if kitscene:
        land.objects['top'].pass_index = 7; sc.view_layers['paint'].use_pass_object_index = True
        for o in objs:      # and none on what lies on it: fallen leaves, snowflakes, the ice sheet (a cut-out over the whole top), mist
            if o.name in ('sz_leaves', 'sz_snow', 'sz_ice', 'sz_fog'): o.pass_index = 7
    ng, N, Lk, base = J.comp_begin(bpy, 'glass_comp')
    img = base.outputs['Image']
    # lead along every outline: an edge filter on the flat render, thresholded and thickened
    sob = N.new('CompositorNodeFilter')
    try: sob.inputs['Type'].default_value = 'Sobel'
    except Exception: pass
    bl = N.new('CompositorNodeBlur'); Lk.new(img, bl.inputs['Image'])       # a light blur first: lead on shapes, not on texture
    r = max(1.0, 1.5 * max(W, H) / 1280.0)
    try: bl.inputs['Size'].default_value = (r, r)
    except Exception: pass
    Lk.new(bl.outputs['Image'], sob.inputs['Image'])
    bw = N.new('CompositorNodeRGBToBW'); Lk.new(sob.outputs['Image'], bw.inputs['Image'])
    edge = J.cmath(N, Lk, 'GREATER_THAN', bw.outputs['Val'], 0.55)
    if kitscene:    # no edge lead inside the seasons ground (its snow and litter are patchy): its own panes lead it
        rl = [n for n in N if n.bl_idname == 'CompositorNodeRLayers' and n.layer == 'paint'][0]
        im = N.new('CompositorNodeIDMask'); im.inputs['Index'].default_value = 7; Lk.new(rl.outputs['Object Index'], im.inputs['ID value'])
        px = max(1, int(round(2.0 * max(W, H) / 1280.0)))
        cl = N.new('CompositorNodeDilateErode'); Lk.new(im.outputs['Alpha'], cl.inputs['Mask']); cl.inputs['Size'].default_value = px + 1   # close pinholes
        er = N.new('CompositorNodeDilateErode'); Lk.new(cl.outputs['Mask'], er.inputs['Mask']); er.inputs['Size'].default_value = -(2 * px + 1)
        edge = J.cmath(N, Lk, 'MULTIPLY', edge, J.cmath(N, Lk, 'SUBTRACT', 1.0, er.outputs['Mask']))
    di = N.new('CompositorNodeDilateErode'); Lk.new(edge, di.inputs['Mask']); di.inputs['Size'].default_value = int(round(1.0 * W / 1280.0))
    img = J.cmix(N, Lk, di.outputs['Mask'], img, lin(LEAD))
    gl = N.new('CompositorNodeGlare')
    gl.inputs['Type'].default_value = 'Bloom'; gl.inputs['Quality'].default_value = 'Medium'
    gl.inputs['Threshold'].default_value = 0.7; gl.inputs['Strength'].default_value = 0.25; gl.inputs['Size'].default_value = 0.6
    Lk.new(img, gl.inputs['Image']); img = gl.outputs['Image']
    img = J.vignette(N, Lk, img, W, H, amount=0.22)
    J.comp_end(bpy, ng, img)


def frame(bpy, film, ctx, t, shot):
    """On the seasons loop: the leaded ground under the block takes the loop's season backdrop colour (set by its own
    frame just before), deepened like coloured glass. Nothing to do on the line films."""
    bg = film._glass.get('bg')
    if bg is None or bg[0] is None: return
    import colorsys
    c = bg[0].inputs['Base Color'].default_value
    h, sat, v = colorsys.rgb_to_hsv(c[0], c[1], c[2])
    r, g, b = colorsys.hsv_to_rgb(h, min(1.0, sat * 3.5 + 0.18), v * 0.10)
    bg[1].outputs[0].default_value = (r, g, b, 1.0)
