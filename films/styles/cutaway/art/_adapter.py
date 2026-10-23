"""Adapter: lets a Cutaway art direction (films/styles/cutaway/art/<name>.py) dress a scene built directly on the kit
(films/styles/cutaway/cutaway.py), not by the line engine. First user: the seasons loop (films/cutaway/loops/seasons).

An art module is written against the line engine's Film (films/lib/cutaway/engine.py) and reads:
    film.built[set]['objs' | 'hidden' | 'kit' | 'land' | 'world' | 'L' | 'rig'], film.cam.ob, film.O.items (the words,
    each with .ob and .em), film.G, film.SETTINGS, film.cw (the kit), film.ex (the cinematic extras).
KitFilm gives the same names for a kit scene: one set 'main' with every object of the scene but the words, the kit and
its Land, the scene's world, L.strata (the scene's strata list, for looks that repaint the cut faces), rig.sun_dir (from
the scene's sun lamp, as posed when apply runs), the camera, and the words as overlay items. kind = 'kit' tells an art
module it is on a kit scene (helpers: _jewel.is_kit), where per-frame code of the scene may reset lights and colours
after apply; the art module's frame() runs after the scene's own frame(), so it can re-apply what it needs.

Use from a kit scene's blender.py (opt-in, so the scene renders exactly as before without it):

    S['art'] = _adapter.attach(bpy, ctx, art_name, kit=kit, land=L, cam=cam, settings=SETTINGS, strata=STRATA, words=[title])
    and each frame, after the scene has posed everything:  if S.get('art'): S['art'].frame(bpy, ctx, t)
"""
import importlib.util
import os
import sys
from types import SimpleNamespace

ART = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.dirname(ART)


class _Word:
    """A words object as the art modules see an overlay element: .ob, and .em (its Emission node, or None)."""
    def __init__(self, ob):
        self.ob = ob; self.em = None
        for m in getattr(ob.data, 'materials', []) or []:
            if m is None or not m.node_tree: continue
            for n in m.node_tree.nodes:
                if n.bl_idname == 'ShaderNodeEmission': self.em = n; break
            if self.em is not None: break


class KitFilm:
    kind = 'kit'

    def __init__(self, bpy, ctx, kit, land, cam, settings=None, strata=None, words=()):
        for p in (STYLE, os.path.join(STYLE, 'cinematic')):
            if p not in sys.path: sys.path.insert(0, p)
        import cutaway as cw
        import extras as ex
        self.cw, self.ex = cw, ex
        self.SETTINGS = dict(settings or {}); self.SETTINGS.setdefault('exposure', 0.0)
        self.cam = cam                                   # has .ob, like the engine's ShotCam
        self.O = SimpleNamespace(items=[_Word(o) for o in words])
        self.G = {}
        wn = {o.name for o in words}
        objs = [o for o in bpy.context.scene.objects if o.name not in wn]
        sun = next((o for o in objs if o.type == 'LIGHT' and o.data.type == 'SUN'), None)
        sd = (-0.6, 0.6, 0.35)
        bpy.context.view_layer.update()
        if sun is not None:
            v = sun.matrix_world.to_3x3() @ __import__('mathutils').Vector((0, 0, 1)); sd = (v.x, v.y, v.z)
        self.built = {'main': {'objs': objs, 'hidden': {o.name for o in objs if o.hide_render}, 'kit': kit, 'land': land,
                               'world': bpy.context.scene.world, 'L': SimpleNamespace(name='main', strata=strata or [], time='kit'),
                               'rig': {'sun_dir': sd}}}
        self.art = None

    def frame(self, bpy, ctx, t):
        if self.art is not None and hasattr(self.art, 'frame'): self.art.frame(bpy, self, ctx, t, None)


def load_art(name):
    path = os.path.join(ART, name + '.py')
    if not os.path.exists(path): raise RuntimeError(f'unknown art direction {name!r} (no {path})')
    sp = importlib.util.spec_from_file_location('kf_art_' + name, path); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
    return mod


def attach(bpy, ctx, name, kit, land, cam, settings=None, strata=None, words=()):
    """Build the adapter, run the art module's apply() on the finished scene, return the adapter (call .frame each frame)."""
    film = KitFilm(bpy, ctx, kit, land, cam, settings, strata, words)
    film.art = load_art(name)
    film.art.apply(bpy, film, ctx)
    print(f'art direction: {name} (kit scene)', flush=True)
    return film
