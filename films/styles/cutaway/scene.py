"""Harness glue: turn a Cutaway look into a scene for harness/blender_render.py (DURATION, SETTINGS, build, frame).

    from scene import make
    DURATION, SETTINGS, build, frame = make('A', duration=8.0, move='orbit')
"""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path: sys.path.insert(0, here)
import cutaway as cw  # noqa: E402
import looks  # noqa: E402

def make(look, duration=8.0, move='orbit', samples=64, deg=16.0, fast=False, size=None):
    SETTINGS = {'samples': samples, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
                'max_bounces': 8, 'clamp_indirect': 6.0, 'adaptive_min_samples': 16, 'denoising_prefilter': 'ACCURATE'}

    def build(bpy, ctx):
        if size:   # override the harness resolution (lets one stills run mix 16:9 and 9:16 frames)
            sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = size; ctx = dict(ctx, W=size[0], H=size[1])
        aspect = '16:9' if ctx['W'] >= ctx['H'] else '9:16'
        kit = cw.Kit(bpy, seed=1, loop=duration)
        S = looks.LOOKS[look](bpy, kit, aspect)
        cw.apply_cycles(bpy, fast); sc = bpy.context.scene
        if fast: sc.cycles.adaptive_threshold = 0.04
        sc.view_settings.look = S['look']; sc.view_settings.exposure = S['exposure']
        S['kit'] = kit; S['az0'] = S['cam'].az; S['d0'] = S['cam'].dist
        return S

    def frame(bpy, ctx, S, i, t):
        S['kit'].update(t); cam = S['cam']
        u = min(1.0, max(0.0, t / duration)); e = u * u * (3 - 2 * u)          # one move: ease in, steady, ease out
        if move == 'orbit': cam.pose(az=S['az0'] - deg / 2 + deg * e)
        elif move == 'push': cam.pose(dist=S['d0'] * (1.0 - 0.12 * e))
    return duration, SETTINGS, build, frame
