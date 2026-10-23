"""Shared helpers for three Cutaway art directions: fable, night-glow and stained-glass (jewel-toned looks).

Not an art direction itself (the leading underscore keeps it out of the look list). The looks load it by path:

    import importlib.util, os
    _s = importlib.util.spec_from_file_location('kf_art__jewel', os.path.join(os.path.dirname(__file__), '_jewel.py'))
    J = importlib.util.module_from_spec(_s); _s.loader.exec_module(J)

What is here:
- lin(c): an sRGB colour as a linear RGBA tuple (the kit's srgb()).
- overlay_objects(film), scene_objects(film): the words layer (labels, title, counter, dip) and everything else.
- type_layer(bpy, film): moves the words into their own view layer so the picture can be filtered in the compositor
  (painterly filters, glow) while the words stay crisp; returns the two layer names. The words layer renders only the
  overlay objects over a transparent background (cheap).
- hide(film, ob), adopt(film, ob): hide an object of the built set for good / add a new object to the set, so the engine's
  per-shot visibility switch (Film._show) keeps them that way.
- principled(mat), base_color(g, mat): read a kit material's base colour (a linked socket or a value) to rebuild it.
- recolor_overlay(film, ink, paper): restyle the words layer (ink and paper colours), keeping its alpha fades.
- comp_begin / comp_end: a compositor tree with the picture and the words layers, the words laid over at the end.
- vignette(N, L, img, W, H, amount): a soft vignette in the compositor (same maths as the cinematic extras).
Free: Blender bpy 5.2, Cycles CPU, nothing downloaded.
"""
import math

import numpy as np


def lin(c, a=1.0):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (f(c[0]), f(c[1]), f(c[2]), a)


def overlay_objects(film):
    return [e.ob for e in film.O.items]


def scene_objects(film):
    ov = {o.name for o in overlay_objects(film)}; out = []
    for st in film.built.values():
        for o in st['objs']:
            try:
                if o.name not in ov: out.append(o)
            except ReferenceError: pass
    return out


def hide(film, ob):
    ob.hide_render = True
    for st in film.built.values():
        if ob in st['objs']: st['hidden'].add(ob.name)


def adopt(film, ob, set_name=None):
    st = film.built[set_name] if set_name else next(iter(film.built.values()))
    st['objs'].append(ob); return ob


def principled(mat):
    if not mat or not mat.node_tree: return None
    for n in mat.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeBsdfPrincipled': return n
    return None


def base_color(mat):
    """(socket, None) when the base colour is linked, else (None, linear RGBA)."""
    p = principled(mat)
    if p is None: return None, None
    s = p.inputs['Base Color']
    if s.is_linked: return s.links[0].from_socket, None
    return None, tuple(s.default_value)


def output_node(mat):
    for n in mat.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeOutputMaterial': return n
    return None


def set_surface(mat, shader_socket, keep_volume=False):
    nt = mat.node_tree; o = output_node(mat)
    if o is None: o = nt.nodes.new('ShaderNodeOutputMaterial')
    if hasattr(shader_socket, 'outputs') and not hasattr(shader_socket, 'is_output'): shader_socket = shader_socket.outputs[0]
    for l in list(o.inputs['Surface'].links): nt.links.remove(l)
    nt.links.new(shader_socket, o.inputs['Surface'])
    if not keep_volume:
        for l in list(o.inputs['Volume'].links): nt.links.remove(l)
    o.target = 'ALL'


def scene_materials(objs):
    seen = {}
    for o in objs:
        for s in getattr(o, 'material_slots', []):
            if s.material is not None: seen[s.material.name] = s.material
        # instancers (geometry nodes on point meshes) carry no slots: their prototypes do
        for md in getattr(o, 'modifiers', []):
            if md.type == 'NODES':
                for it in md.node_group.interface.items_tree if md.node_group else []:
                    if getattr(it, 'socket_type', '') == 'NodeSocketCollection':
                        try: c = md[it.identifier]
                        except Exception: c = None
                        if c is not None:
                            for po in c.all_objects:
                                for s in po.material_slots:
                                    if s.material is not None: seen[s.material.name] = s.material
    return list(seen.values())


def recolor_overlay(film, ink=(0.07, 0.09, 0.12), paper=(0.97, 0.96, 0.93)):
    """Restyle the words layer: plates (pills) in paper, text, rules, leaders and dots in ink. Alpha fades untouched."""
    for e in film.O.items:
        em = getattr(e, 'em', None)
        if em is None: continue
        n = e.ob.name
        if n == 'cl_dip': continue
        is_paper = n.endswith('_pl') or 'plate' in n or n.endswith('pl') or n in ('cl_tplate', 'cl_eplate', 'cl_countpl', 'cl_cappl')
        em.inputs['Color'].default_value = lin(paper if is_paper else ink)


def type_layer(bpy, film, samples=16):
    """Words in their own view layer ('type'), the world in 'paint'. Returns ('paint', 'type')."""
    sc = bpy.context.scene
    words = bpy.data.collections.new('art_words'); world = bpy.data.collections.new('art_world')
    sc.collection.children.link(world); sc.collection.children.link(words)
    ov = {o.name for o in overlay_objects(film)}
    for o in list(sc.collection.objects):
        (words if o.name in ov else world).objects.link(o); sc.collection.objects.unlink(o)
    cam = film.cam.ob
    if cam.name not in words.objects: words.objects.link(cam)        # the words are parented to the camera
    paint = sc.view_layers[0]; paint.name = 'paint'
    tl = sc.view_layers.new('type')
    paint.layer_collection.children['art_words'].exclude = True
    tl.layer_collection.children['art_world'].exclude = True
    tl.use_sky = False; tl.samples = samples
    try: tl.cycles.use_denoising = False
    except Exception: pass
    return 'paint', 'type'


def comp_begin(bpy, name):
    sc = bpy.context.scene
    ng = bpy.data.node_groups.new(name, 'CompositorNodeTree')
    ng.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    N, L = ng.nodes, ng.links
    rl = N.new('CompositorNodeRLayers'); rl.layer = 'paint'
    return ng, N, L, rl


def comp_end(bpy, ng, img, words=True):
    N, L = ng.nodes, ng.links; sc = bpy.context.scene
    go = N.new('NodeGroupOutput')
    if words:
        rt = N.new('CompositorNodeRLayers'); rt.layer = 'type'
        ao = N.new('CompositorNodeAlphaOver')
        L.new(img, ao.inputs['Background']); L.new(rt.outputs['Image'], ao.inputs['Foreground'])
        img = ao.outputs['Image']
    L.new(img, go.inputs[0])
    sc.compositing_node_group = ng; sc.render.use_compositing = True
    return ng


def cmath(N, L, op, a, b=None):
    n = N.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    return n.outputs[0]


def cmix(N, L, fac, a, b, blend='MIX'):
    n = N.new('ShaderNodeMix'); n.data_type = 'RGBA'; n.blend_type = blend
    for key, v in (('Factor', fac), ('A', a), ('B', b)):
        s = n.inputs[key] if key == 'Factor' else n.inputs[key + '_Color'] if (key + '_Color') in n.inputs else None
        if s is None:
            s = [x for x in n.inputs if x.name == key and x.enabled][0]
        if isinstance(v, (int, float)): s.default_value = v
        elif isinstance(v, tuple): s.default_value = v
        else: L.new(v, s)
    return [o for o in n.outputs if o.name == 'Result' and o.enabled][0]


def uv(N, L, img):
    """Normalized image coordinates split into x (0..1) and y (0..1)."""
    ic = N.new('CompositorNodeImageCoordinates'); L.new(img, ic.inputs['Image'])
    sp = N.new('ShaderNodeSeparateXYZ'); L.new(ic.outputs['Normalized'], sp.inputs[0])
    return ic.outputs['Normalized'], sp.outputs[0], sp.outputs[1]


def vignette(N, L, img, W, H, amount=0.2, r0=0.05, r1=0.36):
    _, x, y = uv(N, L, img)
    dx = cmath(N, L, 'SUBTRACT', x, 0.5); dy = cmath(N, L, 'MULTIPLY', cmath(N, L, 'SUBTRACT', y, 0.5), H / W)
    r2 = cmath(N, L, 'ADD', cmath(N, L, 'MULTIPLY', dx, dx), cmath(N, L, 'MULTIPLY', dy, dy))
    vg = N.new('ShaderNodeMapRange'); vg.interpolation_type = 'SMOOTHSTEP'; L.new(r2, vg.inputs['Value'])
    vg.inputs['From Min'].default_value = r0; vg.inputs['From Max'].default_value = r1
    vg.inputs['To Min'].default_value = 1.0; vg.inputs['To Max'].default_value = 1.0 - amount
    return cmix(N, L, 1.0, img, vg.outputs[0], 'MULTIPLY')


def lights(bpy, film, keep_prefix=(), scale=None, off_prefix=()):
    """Scale or switch off the set's lights by name prefix. scale: {prefix: factor}."""
    for o in scene_objects(film):
        if o.type != 'LIGHT': continue
        n = o.name
        if any(n.startswith(p) for p in off_prefix): hide(film, o); continue
        for p, k in (scale or {}).items():
            if n.startswith(p): o.data.energy *= k; break


def rotation_profile(profile, ring=28, cap=True):
    """A surface of revolution: profile = [(z, r)] bottom to top. Returns (V, F) with a pointed or flat cap."""
    V = []; F = []; n = len(profile)
    for z, r in profile:
        for k in range(ring):
            a = 2 * math.pi * k / ring; V.append((r * math.cos(a), r * math.sin(a), z))
    for j in range(n - 1):
        for k in range(ring):
            a = j * ring + k; b = j * ring + (k + 1) % ring
            F.append((a, b, b + ring, a + ring))
    if cap:
        z0 = profile[0][0]; z1 = profile[-1][0]
        V.append((0, 0, z0)); c0 = len(V) - 1; V.append((0, 0, z1)); c1 = len(V) - 1
        for k in range(ring):
            F.append((c0, (k + 1) % ring, k))
            a = (n - 1) * ring + k; b = (n - 1) * ring + (k + 1) % ring; F.append((a, b, c1))
    return V, F


def tree_points(film, set_name=None):
    """The kit's tree spots: (N x 3 positions, scale, variant) read from the 'cw_trees' instancer of the set."""
    st = film.built[set_name] if set_name else next(iter(film.built.values()))
    ob = st['land'].objects.get('cw_trees')
    if ob is None: return np.zeros((0, 3)), np.zeros(0), np.zeros(0, int), None
    me = ob.data; P = np.array([v.co[:] for v in me.vertices])
    def att(name, dflt):
        a = me.attributes.get(name)
        return np.array([d.value for d in a.data]) if a is not None else dflt
    return P, att('scale', np.ones(len(P))), att('variant', np.zeros(len(P), int)).astype(int), ob
