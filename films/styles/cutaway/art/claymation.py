"""Art direction `claymation`: plasticine stop-motion, the whole block sculpted in clay.

Every material becomes clay: saturated colour, a waxy low sheen, a touch of subsurface scattering, and a hand-made bump
built from three things: lumps (low-frequency noise), fingerprints (concentric rings around voronoi cell centres, each cell
one thumb press) and tool marks (distorted wave bands, like a modelling tool dragged through the surface). The cut face
keeps its strata but gets the same sculpted surface; trees and rocks get a real lumpy displacement. The golden-hour rig
stays (warm low sun) but with a bigger, softer sun and no god rays, over a painted turquoise-to-cream cyclorama and a clay
baseboard, like a miniature set under a practical lamp. Stop-motion feel: animation is stepped on twos (12 poses a second)
and the surface texture "boils" a hair from pose to pose, as real clay does between frames. What it changes: materials,
world, a few modifiers, the sun, per-frame boil. No compositor. Render cost vs the reference: a little more (subsurface and
a heavier bump on every surface), roughly 1.1 to 1.3 times; the fog and god rays that cost most in the reference are off.
"""
import math
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _post as P  # noqa: E402
import cutaway as cw  # noqa: E402
from cutaway import srgb  # noqa: E402

BOIL = []          # value sockets that shift the texture lookup a little every pose


def _boil_pos(g, pos):
    bx = g.value(0.0, 'kf_boil_x'); by = g.value(0.0, 'kf_boil_y'); BOIL.append((bx, by))
    return g.vmath('ADD', pos, g.comb(bx, by, g.math('MULTIPLY', bx, -1.0)))


def clay_height(g, pos, thumb=24.0):
    """Lumps + fingerprints + tool marks as one 0..1-ish height socket."""
    p = _boil_pos(g, pos)
    lump = g.noise(p, 7.0, 4.0, 0.55); fine = g.noise(p, 90.0, 3.0, 0.6)
    vo = g.voronoi(p, thumb, 'F1')
    warp = g.noise(p, 30.0, 2.0)
    rings = g.math('SINE', g.math('ADD', g.math('MULTIPLY', vo.outputs['Distance'], 85.0), g.math('MULTIPLY', warp.outputs['Fac'], 2.6)))
    cellmask = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', vo.outputs['Distance'], 2.1), clamp=True)           # strongest at the thumb centre
    press = g.math('MULTIPLY', g.math('MULTIPLY', rings, 0.3), cellmask)
    wv = g.node('ShaderNodeTexWave', wave_type='BANDS', bands_direction='DIAGONAL', ins={'Scale': 11.0, 'Distortion': 4.0, 'Detail': 2.0, 'Detail Scale': 1.5, 'Detail Roughness': 0.6})
    g.put(wv, 'Vector', p)
    groove = g.math('MULTIPLY', g.math('GREATER_THAN', wv.outputs['Fac'], 0.86), g.math('GREATER_THAN', g.noise(p, 2.4, 2.0).outputs['Fac'], 0.52))
    h = g.math('ADD', g.math('MULTIPLY', lump.outputs['Fac'], 0.85), g.math('ADD', g.math('MULTIPLY', fine.outputs['Fac'], 0.18), g.math('ADD', press, g.math('MULTIPLY', groove, -0.45))))
    return h


def clay_material(m, kit, strong=1.0, sat=1.28, thumb=24.0, colour=True, rough=0.52):
    for n in m.node_tree.nodes:
        if n.bl_idname != 'ShaderNodeBsdfPrincipled': continue
        g = cw.G(m.node_tree, kit)
        for k in ('Roughness',):
            for l in list(n.inputs[k].links): g.L.remove(l)
        P.set_default_principled(n, **{'Roughness': rough, 'Metallic': 0.0, 'Specular IOR Level': 0.45, 'Coat Weight': 0.0, 'Transmission Weight': 0.0,
                                      'Subsurface Weight': 0.12, 'Subsurface Scale': 0.012, 'Sheen Weight': 0.0})
        try: n.inputs['Subsurface Radius'].default_value = (1.0, 0.45, 0.3)
        except Exception: pass
        def sat_fn(g_, c):
            hs = g_.node('ShaderNodeHueSaturation', ins={'Saturation': sat, 'Value': 1.0, 'Fac': 1.0}); g_.put(hs, 'Color', c); return hs.outputs['Color']
        if colour: P.insert_colour_filter(g, n, sat_fn)
        if n.inputs['Normal'].is_linked:
            for l in list(n.inputs['Normal'].links): g.L.remove(l)
        tc = g.node('ShaderNodeTexCoord'); h = clay_height(g, tc.outputs['Object'], thumb)
        b = g.node('ShaderNodeBump', ins={'Strength': 0.8 * strong, 'Height': h, 'Distance': 0.012}); g.link(b.outputs['Normal'], n.inputs['Normal'])


def apply(bpy, film, ctx):
    name, st = P.sets_of(bpy, film)[0]; kit = st['kit']; land = st.get('land'); sc = bpy.context.scene
    BOIL.clear()
    kitscene = P.is_kit(film)
    for m in list(bpy.data.materials):
        if not m.node_tree or m.name.startswith('cl_') or m.name in ('cw_water', 'ex_shaft_mat', 'ex_gobo', 'ex_floor') or m.name.startswith(('cw_window', 'cw_lamphead')): continue
        if kitscene:     # the seasons loop: bigger thumbs and bolder lumps so they read at phone size; colours stay season-driven
            if m.name in ('sz_water', 'sz_ice', 'sz_haze', 'sz_fog', 'sz_titlemat'): continue
            clay_material(m, kit, strong=2.4 if m.name in ('sz_strata', 'sz_top') else 1.6, sat=1.45, thumb=9.0, colour=(m.name != 'cw_floor'), rough=0.4)
            continue
        clay_material(m, kit, strong=1.5 if m.name == 'cw_strata' else 1.0)
    if kitscene:
        for o in list(bpy.data.objects):
            if o.name == 'sz_grass': o.hide_render = True      # clay does not do blades: the top is modelled with thumb dents
    # the strata: clay seams (a darker pinched line between layers) on top of the kit's soft bands
    # (kept as is: the kit's wobbly bands already read as rolled slabs of clay)
    # baseboard
    fl = bpy.data.materials.get('ex_floor')
    if fl:
        nt = fl.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        g = cw.G(nt, kit); tc = g.node('ShaderNodeTexCoord'); h = clay_height(g, g.vmath('SCALE', tc.outputs['Object'], scale=0.25))
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.82, 0.55, 0.30)), 'Roughness': 0.55})
        P.set_default_principled(p, **{'Subsurface Weight': 0.1, 'Subsurface Scale': 0.012})
        b = g.node('ShaderNodeBump', ins={'Strength': 0.6, 'Height': h, 'Distance': 0.03}); g.link(b.outputs['Normal'], p.inputs['Normal']); cw._finish(g, p)
    # a painted cyclorama instead of the golden sky
    wd = st.get('world') or sc.world
    if wd is None: wd = bpy.data.worlds.new('cl_world'); sc.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    g = cw.G(nt, kit); tcn = g.node('ShaderNodeTexCoord'); fy = g.math('ADD', g.sep(tcn.outputs['Window'])[1], 0.2)
    sky = g.mix(g.math('MINIMUM', g.math('MAXIMUM', fy, 0.0), 1.0), srgb((1.0, 0.78, 0.50)), srgb((0.08, 0.50, 0.66)))
    bgc = g.node('ShaderNodeBackground', ins={'Color': sky, 'Strength': 1.0}); bgl = g.node('ShaderNodeBackground', ins={'Color': srgb((1.0, 0.84, 0.64)), 'Strength': 0.5})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader'); g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bgl, mx.inputs[1]); g.link(bgc, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
    # lights: a bigger, softer practical lamp
    for ld in bpy.data.lights:
        if ld.name == 'ex_sun': ld.angle = math.radians(14.0); ld.energy = 5.0
        elif ld.name == 'ex_fill': ld.energy = 1100.0; ld.color = (1.0, 0.84, 0.68)
    P.hide_shafts(film)
    for o in P.all_scene_objects(film):
        if o.name.startswith('ex_gobo'): o.hide_render = True
    st['hidden'] = {o.name for o in st['objs'] if o.hide_render}
    # sculpted lumps: a real displacement on leaf masses and rocks
    tex = bpy.data.textures.new('kf_clay_lump', 'CLOUDS'); tex.noise_scale = 0.35; tex.noise_depth = 2
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.data or len(o.data.vertices) < 60: continue
        names = {mm.name for mm in o.data.materials if mm}
        if any(n.startswith(('cw_leaf', 'cw_rock', 'cw_bankrock', 'cw_pebble', 'sz_leaf', 'sz_needles')) for n in names):
            md = o.modifiers.new('kf_lump', 'DISPLACE'); md.texture = tex; md.strength = 0.035 if not kitscene else 0.06; md.mid_level = 0.5; md.texture_coords = 'LOCAL'
    sc.view_settings.exposure = 0.25


def frame(bpy, film, ctx, t, shot):
    # stepped on twos: 12 poses a second, and the clay boils a hair between poses
    k = int(math.floor(t * 12 + 1e-6)); tq = k / 12.0
    for _n, st in P.sets_of(bpy, film): st['kit'].update(tq)
    a = ((zlib.crc32(f'boil{k}'.encode()) & 0xffff) / 65535.0 - 0.5) * 0.012; b = ((zlib.crc32(f'boy{k}'.encode()) & 0xffff) / 65535.0 - 0.5) * 0.012
    for bx, by in BOIL: bx.default_value = a; by.default_value = b
