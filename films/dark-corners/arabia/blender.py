"""Dark Corners: I Am Buying Her Life (Arabia, c. 600), KINOFORGE Clay style. Blender 5.2 / Cycles CPU, 720x1280, animated on 2s.

Contract (harness/blender_render.py): DURATION, SETTINGS, build(bpy, ctx) -> state, frame(bpy, ctx, state, i, t). The picture follows the
original episode's final mix (audio/mix.m4a, cues.json); nothing here changes its timing. Split into modules next to this file:
kit.py (clay/card materials, geometry), world.py (terrain, sky, moon), actors.py (figures, camels, tents, lamps, ropes),
props.py (lettering, scroll, lamp field, houses), director.py (the shot list). NOTES.md has the shot list and the render budget.
"""
import math, os, shutil, sys
import numpy as np
from kit import *
from kit import _mat
import world as W
import actors as A
import props as P

DURATION = 175.84
SETTINGS = {'samples': 24, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 4, 'clamp_indirect': 6.0}
FPS = 24
SPP_CAP = 24      # the render workflow passes --samples 96 unless the queue overrides it; KF_ARABIA_SPP_CAP=0 lifts the cap

def make_materials(bpy):
    M = {'sand': sandy(bpy, 'sand', (0.74, 0.58, 0.38), (0.66, 0.50, 0.33), (0.80, 0.64, 0.44))}
    M['street'] = sandy(bpy, 'street', (0.70, 0.55, 0.38), (0.62, 0.48, 0.34), (0.76, 0.60, 0.42), ripple=0.12)
    M['goat'] = striped(bpy, 'goat_hair', [(0.20, 0.14, 0.10), (0.15, 0.10, 0.07), (0.58, 0.46, 0.33), (0.18, 0.12, 0.09), (0.12, 0.08, 0.06)], period=0.022, axis=0, widths=[0.28, 0.24, 0.10, 0.22, 0.16], rough=0.85)
    M['pole'] = clay(bpy, 'wood', (0.42, 0.28, 0.16), (0.34, 0.22, 0.13), rough=0.7, seed=40)
    M['rope'] = clay(bpy, 'rope', (0.72, 0.60, 0.40), (0.60, 0.48, 0.32), rough=0.85, seed=41)
    M['rug'] = striped(bpy, 'rug', [(0.62, 0.16, 0.12), (0.90, 0.78, 0.50), (0.14, 0.20, 0.38), (0.90, 0.78, 0.50), (0.62, 0.16, 0.12), (0.30, 0.22, 0.14)], period=0.030, axis=1, widths=[0.25, 0.06, 0.25, 0.06, 0.25, 0.13], rough=0.9)
    M['sil'] = clay(bpy, 'sil', (0.07, 0.045, 0.035), (0.09, 0.06, 0.04), rough=0.8, sss=0.0, seed=42)
    M['lampclay'] = clay(bpy, 'lamp_clay', (0.50, 0.30, 0.20), (0.42, 0.24, 0.16), rough=0.6, seed=43)
    M['flame'], M['flame_em'] = emissive(bpy, 'flame', (1.0, 0.72, 0.30), 18.0)
    M['bowl'] = clay(bpy, 'bowl', (0.60, 0.36, 0.22), (0.50, 0.28, 0.18), rough=0.55, seed=44)
    M['milk'] = clay(bpy, 'milk', (0.97, 0.95, 0.88), (0.92, 0.90, 0.82), rough=0.3, seed=45)
    M['dates'] = clay(bpy, 'dates', (0.26, 0.12, 0.07), (0.20, 0.09, 0.05), rough=0.4, seed=46)
    M['thorn'] = clay(bpy, 'thorn', (0.30, 0.22, 0.14), (0.24, 0.17, 0.11), rough=0.8, seed=47)
    M['stamp_rim'] = clay(bpy, 'stamp_rim', (0.78, 0.62, 0.42), (0.70, 0.54, 0.36), rough=0.9, sss=0.05, seed=48)
    M['stamp_in'] = clay(bpy, 'stamp_in', (0.50, 0.38, 0.26), (0.44, 0.33, 0.23), rough=0.9, sss=0.05, seed=49)
    M['stone'] = clay(bpy, 'stone', (0.58, 0.55, 0.50), (0.48, 0.46, 0.42), rough=0.8, seed=50)
    M['pouch'] = clay(bpy, 'pouch', (0.48, 0.22, 0.16), (0.40, 0.17, 0.12), rough=0.7, seed=51)
    M['parch'] = clay(bpy, 'parch', (0.90, 0.80, 0.58), (0.84, 0.72, 0.50), rough=0.8, sss=0.2, seed=52)
    M['ink'] = clay(bpy, 'ink', (0.16, 0.10, 0.08), (0.12, 0.08, 0.06), rough=0.5, sss=0.0, seed=53)
    M['letters'] = P.cream_letters(bpy, 'letters', (0.97, 0.92, 0.76), 0.5, seed=54)
    M['hud'] = P.cream_letters(bpy, 'hud', (0.98, 0.93, 0.78), 0.9, seed=55)
    M['tile'] = clay(bpy, 'tile', (0.52, 0.30, 0.22), (0.44, 0.24, 0.18), rough=0.7, seed=56)
    M['num'] = P.cream_letters(bpy, 'num', (0.98, 0.92, 0.72), 0.7, seed=57)
    M['wall'] = clay(bpy, 'mecca_wall', (0.80, 0.66, 0.48), (0.72, 0.58, 0.42), rough=0.85, seed=58)
    M['wall2'] = clay(bpy, 'mecca_wall2', (0.66, 0.50, 0.36), (0.58, 0.44, 0.32), rough=0.85, seed=59)
    M['glowwin'], M['glowwin_em'] = emissive(bpy, 'glowwin', (1.0, 0.68, 0.30), 4.0)
    M['glowdoor'], M['glowdoor_em'] = emissive(bpy, 'glowdoor', (1.0, 0.66, 0.28), 3.0)
    M['paper_far'] = [paper(bpy, f'far{k}', c, tuple(x * 0.92 for x in c), rough=0.95, stroke=(1.0, 1.0, 12.0), stroke_scale=3.0, tooth=0.0, mottle=2.0) for k, c in enumerate(((0.16, 0.20, 0.38), (0.12, 0.15, 0.31), (0.09, 0.11, 0.25)))]
    return M

def mecca_h(x, y):
    return 0.010 * np.sin(1.3 * x + 0.5 * y) + 0.008 * np.sin(0.9 * y + 1.1) + 0.2 * W.smoothv(3.6, 4.6, y)

def build(bpy, ctx):
    from mathutils import Vector
    sc = bpy.context.scene; coll = sc.collection; S = {'bpy': bpy, 'ctx': ctx}
    try: sc.render.use_persistent_data = True
    except Exception: pass
    try: sc.render.compositor_device = 'CPU'
    except Exception: pass
    cy = sc.cycles
    cy.diffuse_bounces = 3; cy.glossy_bounces = 2; cy.transmission_bounces = 2; cy.transparent_max_bounces = 6
    cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0; cy.seed = 0; cy.use_animated_seed = False
    try: cy.denoising_quality = 'BALANCED'
    except Exception: pass
    cy.adaptive_threshold = max(cy.adaptive_threshold, 0.04)
    cap = int(os.environ.get('KF_ARABIA_SPP_CAP', SPP_CAP))
    if cap > 0 and cy.samples > cap: cy.samples = cap
    M = make_materials(bpy); S['M'] = M
    # ---------------- set
    W.build_terrain(bpy, M['sand'], coll, region=(-4.2, 4.2, -1.5, 4.6), fine=[(-4.0, 0.6, 1.0, 3.2), (0.6, 3.3, 0.9, 2.7)])
    W.build_terrain(bpy, M['street'], coll, region=(6.4, 11.8, -1.5, 4.6), fine=[], fn=mecca_h, prints=False, name='mecca_ground')
    W.build_sky(bpy, coll, S); W.build_moon(bpy, coll, S); W.make_lights(bpy, coll, S)
    for k, (y, base, amp) in enumerate(((4.18, 0.20, 0.30), (4.42, 0.30, 0.34), (4.68, 0.42, 0.36))):
        W.cut_dunes(bpy, coll, M['paper_far'][k], f'far_dunes{k}', y, -16.0, 5.5, base, amp, 20 + k)
    # ---------------- actors
    S['fig'] = {}
    for nm, st in (('sasaa', 'sasaa'), ('old', 'old'), ('zayd', 'zayd'), ('father', 'father'), ('girl', 'girl'), ('woman', 'woman'), ('poet', 'poet')):
        S['fig'][nm] = A.Figure(bpy, nm, st, coll, seed=1 + len(S['fig']) * 7)
    S['listeners'] = [A.Figure(bpy, f'lis{k}', 'listener', coll, seed=90 + k * 5, lite=True) for k in range(7)]
    S['camel'] = {'ride': A.Camel(bpy, 'cRide', 'ride', coll, 3, saddle=True), 'she1': A.Camel(bpy, 'cShe1', 'she1', coll, 5), 'she2': A.Camel(bpy, 'cShe2', 'she2', coll, 7),
                  'calf1': A.Camel(bpy, 'cCalf1', 'calf', coll, 9), 'calf2': A.Camel(bpy, 'cCalf2', 'calf', coll, 11)}
    S['t1'] = A.Tent(bpy, 't1', coll, M, False, 1); S['t2'] = A.Tent(bpy, 't2', coll, M, True, 2)
    S['lamps'] = [A.Lamp(bpy, f'lamp{k}', coll, M['lampclay'], M['flame'], True, 1.0, 60 + k) for k in range(6)]
    S['lamps_nl'] = [A.Lamp(bpy, f'lampn{k}', coll, M['lampclay'], M['flame'], False, 1.0, 80 + k) for k in range(4)]
    S['ropes'] = [A.Rope(bpy, f'rope{k}', coll, M['rope']) for k in range(6)]
    S['all'] = []
    S['hud'] = {}
    return finish_build(bpy, ctx, S, M, coll)

def finish_build(bpy, ctx, S, M, coll):
    import director as Dr
    Dr.build_props(bpy, ctx, S, M, coll)
    # camera
    cd = bpy.data.cameras.new('cam'); cd.lens = 35.0; cd.sensor_width = 36.0; cd.clip_start = 0.01; cd.clip_end = 60.0
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 5.6; cd.dof.aperture_blades = 7
    cam = bpy.data.objects.new('cam', cd); coll.objects.link(cam); bpy.context.scene.camera = cam; S['cam'] = cam; S['camd'] = cd
    Dr.build_hud(bpy, ctx, S, M, coll)
    # compositor: pose-seeded grain + corner falloff
    S['grain'] = None
    try:
        sc = bpy.context.scene
        ng = bpy.data.node_groups.new('kf_finish', 'CompositorNodeTree'); sc.compositing_node_group = ng
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        N, Lk = ng.nodes, ng.links
        rl = N.new('CompositorNodeRLayers')
        ic = N.new('CompositorNodeImageCoordinates'); Lk.new(rl.outputs['Image'], ic.inputs['Image'])
        wn = N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '4D'; Lk.new(ic.outputs['Pixel'], wn.inputs['Vector'])
        amt = 0.03
        gm = N.new('ShaderNodeMath'); gm.operation = 'MULTIPLY_ADD'; Lk.new(wn.outputs['Value'], gm.inputs[0]); gm.inputs[1].default_value = 2 * amt; gm.inputs[2].default_value = 1 - amt
        Wd, Hd = float(ctx['W']), float(ctx['H'])
        sub = N.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; Lk.new(ic.outputs['Pixel'], sub.inputs[0]); sub.inputs[1].default_value = (Wd / 2, Hd / 2, 0.0)
        scl = N.new('ShaderNodeVectorMath'); scl.operation = 'SCALE'; Lk.new(sub.outputs['Vector'], scl.inputs[0]); scl.inputs['Scale'].default_value = 2.0 / Hd
        dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; Lk.new(scl.outputs['Vector'], dot.inputs[0]); Lk.new(scl.outputs['Vector'], dot.inputs[1])
        vg = N.new('ShaderNodeMath'); vg.operation = 'MULTIPLY_ADD'; Lk.new(dot.outputs['Value'], vg.inputs[0]); vg.inputs[1].default_value = -0.22; vg.inputs[2].default_value = 1.0
        gv2 = N.new('ShaderNodeMath'); gv2.operation = 'MULTIPLY'; Lk.new(gm.outputs['Value'], gv2.inputs[0]); Lk.new(vg.outputs['Value'], gv2.inputs[1])
        mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; sock(mix.inputs, 'Factor_Float').default_value = 1.0
        Lk.new(gv2.outputs['Value'], sock(mix.inputs, 'B_Color'))
        hl = N.new('CompositorNodeRLayers'); hl.scene = S['hud_scene']
        ao = N.new('CompositorNodeAlphaOver'); Lk.new(rl.outputs['Image'], ao.inputs['Background']); Lk.new(hl.outputs['Image'], ao.inputs['Foreground'])
        S['hud_node'] = hl
        Lk.new(ao.outputs['Image'], sock(mix.inputs, 'A_Color'))
        out = N.new('NodeGroupOutput'); Lk.new(sock(mix.outputs, 'Result_Color'), out.inputs['Image'])
        sc.render.use_compositing = True; S['grain'] = wn
    except Exception as e:
        print('arabia: compositor finish unavailable:', e)
    # on-2s pair reuse (odd frame right after its even partner: skip path tracing, copy the PNG)
    S['dup'] = {'last': None, 'pending': None, 'enabled': os.environ.get('KF_NO_PAIR_REUSE', '') == '', 'total': int(round(ctx['duration'] * ctx['fps']))}
    if S['dup']['enabled']: bpy.app.handlers.render_write.append(_pair_reuse_handler(S))
    return S

def _pair_reuse_handler(state):
    def _after_write(scene, *args):
        d = state['dup']
        if d.get('pending'):
            src, dst = d['pending']; d['pending'] = None
            try: shutil.copyfile(src, dst)
            except Exception as e: print('arabia: pair reuse copy failed:', e, flush=True)
    return _after_write

def _pair_reuse(bpy, ctx, S, i):
    d = S.get('dup')
    if not d or not d['enabled']: return
    sc = bpy.context.scene; fdir = os.path.join(ctx['out'], 'frames')
    if d.get('pending'):
        src, dst = d['pending']; d['pending'] = None
        try: shutil.copyfile(src, dst)
        except Exception as e: print('arabia: pair reuse late copy failed:', e, flush=True)
    prev = os.path.join(fdir, f'{i - 1:05d}.png')
    reuse = (i % 2 == 1) and d['last'] == i - 1 and i < d['total'] - 1 and os.path.exists(prev)
    if reuse:
        d['pending'] = (prev, os.path.join(fdir, f'{i:05d}.png'))
        sc.render.use_border = True; sc.render.use_crop_to_border = False
        sc.render.border_min_x, sc.render.border_max_x = 0.0, 2.0 / max(1, sc.render.resolution_x)
        sc.render.border_min_y, sc.render.border_max_y = 0.0, 2.0 / max(1, sc.render.resolution_y)
    else:
        sc.render.use_border = False; d['last'] = i

def frame(bpy, ctx, S, i, t):
    import director as Dr
    pf = (i // 2) * 2                   # ON 2s: every channel is a function of the pose frame
    Dr.render_pose(bpy, ctx, S, pf)
    if S.get('grain') is not None: S['grain'].inputs['W'].default_value = pf * 0.731 + 0.17
    _pair_reuse(bpy, ctx, S, i)
