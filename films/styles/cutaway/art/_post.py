"""Shared helpers for the Cutaway art directions (films/styles/cutaway/art/*.py). Not an art direction itself.

What is in here (all procedural, free, Blender 5.2 bpy, Cycles CPU):
- Comp: a tiny builder for the compositor (Blender 5 keeps the compositor as a node group on the scene, the output is
  the group's Image socket, and every node setting is an input socket). The compositor runs on the CPU
  (scene.render.compositor_device = 'CPU') so it works on the GitHub runners that have no GPU.
- split_overlay: moves the words (labels, title, end card, leaders: set in code by overlay.py) into a second scene that
  is rendered at full resolution on a transparent film, so a look can lay them over the picture crisp, whatever it does
  to the picture itself (pixelate, halftone, ...).
- array_image: a numpy array becomes an image (paper grain, halftone screens, dither matrices).
- walk_principled / on_materials: restyle every material of the scene in one pass.
- Small procedural-texture builders on the kit's node helper G (cutaway.py): fibre, grain, fingerprints, tool marks.
"""
import math
import os
import sys

import numpy as np

ART = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ART))))
for _p in (os.path.join(ROOT, 'films', 'styles', 'cutaway'),):
    if _p not in sys.path: sys.path.insert(0, _p)

import cutaway as cw  # noqa: E402

srgb = cw.srgb


def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# ===================================================================================== compositor
class Comp:
    """Compositor node-group builder. c = Comp(bpy, scene); n = c.node('CompositorNodeBlur', {'Image': x, 'Size': (3, 3)})."""

    def __init__(self, bpy, sc):
        self.bpy = bpy; self.sc = sc
        self.ng = bpy.data.node_groups.new('kf_art_comp', 'CompositorNodeTree')
        sc.compositing_node_group = self.ng
        sc.render.compositor_device = 'CPU'; sc.render.use_compositing = True
        try: sc.render.compositor_precision = 'FULL'
        except Exception: pass
        self.ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        self.N = self.ng.nodes; self.L = self.ng.links; self.out = self.N.new('NodeGroupOutput'); self._k = 0

    def node(self, kind, ins=None, **attrs):
        n = self.N.new(kind); self._k += 1; n.location = ((self._k % 12) * 230, -(self._k // 12) * 300)
        for a, v in attrs.items(): setattr(n, a, v)
        for key, v in (ins or {}).items(): self.put(n, key, v)
        return n

    def put(self, n, key, v):
        s = n.inputs[key] if not isinstance(key, int) else n.inputs[key]
        if hasattr(v, 'outputs') and not hasattr(v, 'is_output'): v = v.outputs[0]
        if hasattr(v, 'is_output'): self.L.new(v, s); return
        if isinstance(v, (tuple, list)) and hasattr(s.default_value, '__len__') and len(v) != len(s.default_value):
            v = tuple(v) + (1.0,) * (len(s.default_value) - len(v))
        s.default_value = v

    def o(self, n, key=0):
        return n.outputs[key]

    def math(self, op, a, b=0.0, c=0.0, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp); self.put(n, 0, a); self.put(n, 1, b); self.put(n, 2, c); return n.outputs[0]

    def mix(self, fac, a, b, blend='MIX', clamp=False):
        n = self.node('ShaderNodeMix', data_type='RGBA', blend_type=blend, clamp_result=clamp, clamp_factor=True)
        self.put(n, 'Factor', fac); self.put(n, 'A', a); self.put(n, 'B', b); return n.outputs['Result']

    def vmath(self, op, a, b=(0, 0, 0), scale=None):
        n = self.node('ShaderNodeVectorMath', operation=op); self.put(n, 0, a); self.put(n, 1, b)
        if scale is not None: self.put(n, 'Scale', scale)
        return n.outputs['Value'] if op in ('DOT_PRODUCT', 'LENGTH', 'DISTANCE') else n.outputs['Vector']

    def sep(self, img):
        n = self.node('CompositorNodeSeparateColor', mode='RGB'); self.put(n, 'Image', img); return n.outputs

    def comb(self, r, g, b, a=1.0):
        n = self.node('CompositorNodeCombineColor', mode='RGB')
        for k, v in zip(('Red', 'Green', 'Blue', 'Alpha'), (r, g, b, a)): self.put(n, k, v)
        return n.outputs['Image']

    def scale(self, img, x, y=None, kind='Relative', interp='Nearest'):
        n = self.node('CompositorNodeScale'); n.inputs['Type'].default_value = kind
        n.inputs['Interpolation'].default_value = interp; self.put(n, 'Image', img); self.put(n, 'X', x); self.put(n, 'Y', x if y is None else y); return n.outputs['Image']

    def translate(self, img, x, y, interp='Bilinear'):
        n = self.node('CompositorNodeTranslate'); n.inputs['Interpolation'].default_value = interp
        self.put(n, 'Image', img); self.put(n, 'X', x); self.put(n, 'Y', y); return n.outputs['Image']

    def image(self, im):
        n = self.node('CompositorNodeImage'); n.image = im; return n.outputs['Image']

    def render(self, scene, layer=None):
        n = self.node('CompositorNodeRLayers'); n.scene = scene
        if layer: n.layer = layer
        return n

    def display(self, img, view='Standard', look='None', exposure=0.0, display='sRGB'):
        """Scene-linear to display (view transform applied inside the compositor), so later steps work on what the viewer sees."""
        if exposure:
            ex = self.node('CompositorNodeExposure'); self.put(ex, 'Image', img); self.put(ex, 'Exposure', float(exposure)); img = ex.outputs['Image']
        n = self.node('CompositorNodeConvertToDisplay'); self.put(n, 'Image', img)
        n.view_settings.view_transform = view
        try: n.view_settings.look = look
        except Exception: pass
        n.display_settings.display_device = display
        return n.outputs['Image']

    def finish(self, img):
        self.L.new(img if hasattr(img, 'is_output') else img.outputs[0], self.out.inputs[0])


def display_raw(sc):
    """The compositor already produced display-referred values: save them untouched."""
    vs = sc.view_settings; vs.view_transform = 'Raw'
    try: vs.look = 'None'
    except Exception: pass
    vs.exposure = 0.0; vs.gamma = 1.0


def array_image(bpy, name, arr, linear=True):
    """numpy float array (H, W) or (H, W, 3|4), row 0 = bottom (Blender's order) -> a float image. Non-colour data."""
    a = np.asarray(arr, np.float32)
    if a.ndim == 2: a = np.stack([a, a, a, np.ones_like(a)], -1)
    elif a.shape[2] == 3: a = np.concatenate([a, np.ones(a.shape[:2] + (1,), np.float32)], -1)
    h, w = a.shape[:2]
    im = bpy.data.images.new(name, w, h, alpha=True, float_buffer=True)
    try: im.colorspace_settings.name = 'Non-Color' if linear else 'sRGB'
    except Exception: pass
    im.pixels.foreach_set(a.reshape(-1)); im.update(); im.pack() if False else None
    return im


# ===================================================================================== the words in their own scene
def split_overlay(bpy, film, ctx, exposure_gain=True):
    """Move the code-set words (film.O items: labels, title, end card, counters) out of the picture scene into a second
    scene 'kf_words' that shares the camera. Rendered at full resolution on a transparent film; the art direction's
    compositor lays it over its own picture, crisp. Returns the words scene (and its render settings are final)."""
    A = bpy.context.scene; W, H = ctx['W'], ctx['H']
    B = bpy.data.scenes.new('kf_words')
    B.render.engine = 'CYCLES'; B.render.film_transparent = True; B.render.resolution_x = W; B.render.resolution_y = H
    B.render.resolution_percentage = 100; B.render.fps = A.render.fps
    cy = B.cycles; cy.device = 'CPU'; cy.samples = 6; cy.use_adaptive_sampling = False; cy.use_denoising = False
    cy.max_bounces = 2; cy.transparent_max_bounces = 16; cy.volume_bounces = 0
    B.view_settings.view_transform = 'Standard'
    B.camera = film.cam.ob
    for e in film.O.items:
        ob = e.ob
        for c in list(ob.users_collection): c.objects.unlink(ob)
        B.collection.objects.link(ob)
    if film.cam.ob.name not in B.collection.objects: B.collection.objects.link(film.cam.ob)
    return B


# ===================================================================================== materials
def principled_nodes(bpy):
    """Yield (material, node) for every Principled BSDF in the scene's materials."""
    for m in bpy.data.materials:
        if not m.node_tree: continue
        for n in m.node_tree.nodes:
            if n.bl_idname == 'ShaderNodeBsdfPrincipled': yield m, n


def base_color_socket(node):
    return node.inputs['Base Color']


def input_source(node, key):
    """The socket feeding `key`, or None."""
    s = node.inputs[key]
    return s.links[0].from_socket if s.is_linked else None


def set_default_principled(node, **vals):
    """Set Principled inputs by name where they exist (names differ a little between Blender versions)."""
    for k, v in vals.items():
        for cand in (k, k.replace(' ', '_')):
            if cand in node.inputs:
                try: node.inputs[cand].default_value = v
                except Exception: pass
                break


def insert_colour_filter(g, node, fn):
    """Put fn(g, colour_socket_or_value) between whatever feeds Base Color and the Base Color input.
    fn returns the new colour socket. g is a cutaway.G on the material's tree."""
    s = node.inputs['Base Color']
    if s.is_linked:
        src = s.links[0].from_socket; g.L.remove(s.links[0]); new = fn(g, src)
    else:
        new = fn(g, tuple(s.default_value))
    g.link(new, s)
    return new


def kit_G(m, kit=None):
    return cw.G(m.node_tree, kit)


# ===================================================================================== procedural texture builders (on G)
def fibre(g, pos, scale=380.0, stretch=6.0, detail=3.0):
    """Paper fibre: two crossing stretched noises plus fine grain. Returns a 0..1 socket centred near 0.5."""
    sx = g.sep(pos)
    a = g.noise(g.comb(g.math('MULTIPLY', sx[0], 1.0), g.math('MULTIPLY', sx[1], 1.0 / stretch), sx[2]), scale, detail, 0.55)
    b = g.noise(g.comb(g.math('MULTIPLY', sx[0], 1.0 / stretch), g.math('MULTIPLY', sx[1], 1.0), g.math('MULTIPLY', sx[2], 0.7)), scale * 0.8, detail, 0.55)
    c = g.noise(pos, scale * 2.4, 2.0, 0.6)
    return g.math('MULTIPLY', g.math('ADD', g.math('ADD', a.outputs['Fac'], b.outputs['Fac']), g.math('MULTIPLY', c.outputs['Fac'], 0.6)), 1.0 / 2.6)


def srgb_tuple_scale(c, k):
    return tuple(min(1.0, x * k) for x in c)


# ===================================================================================== misc scene helpers
def hide_shafts(film):
    """God-ray cards (ex_shaft_mat) off: looks that do not want volumetric light."""
    import bpy
    for st in film.built.values():
        for o in st['objs']:
            if o.name.startswith('ex_shaft') or o.name.startswith('cl_shaft') or (o.data and getattr(o.data, 'materials', None) and any(m and m.name == 'ex_shaft_mat' for m in o.data.materials)):
                o.hide_render = True
        st['hidden'] = {o.name for o in st['objs'] if o.hide_render}


def all_scene_objects(film):
    for st in film.built.values():
        for o in st['objs']: yield o


def lights(bpy):
    return list(bpy.data.lights)
