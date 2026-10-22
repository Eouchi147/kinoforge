#!/usr/bin/env python3
"""KINOFORGE Blender renderer (bpy as a Python module, CPU Cycles). Same frame naming as render.cjs.

    python3 harness/blender_render.py proto/<scene> [--out out/<scene>] [--w 1280 --h 720 --fps 24] [--samples 96]
                                      [--start 0 --end N] [--engine CYCLES|BLENDER_EEVEE_NEXT|BLENDER_WORKBENCH] [--mp4 --audio f.wav]

Scene contract (proto/<scene>/blender.py):
    DURATION = 6.0                         # seconds (or SHOTS = [{'name':..., 'dur':...}, ...])
    def build(bpy, ctx) -> state           # ctx = {W,H,fps,duration,timeline(shots)}; create everything, return a dict
    def frame(bpy, ctx, state, i, t)       # pose camera/objects for frame i at time t (deterministic)
    SETTINGS = {'samples': 96, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Medium High Contrast', 'exposure': 0, 'film_transparent': False}
"""
import argparse, importlib.util, os, sys, time, subprocess, json

ap = argparse.ArgumentParser()
ap.add_argument('scene'); ap.add_argument('--out'); ap.add_argument('--w', type=int, default=1280); ap.add_argument('--h', type=int, default=720)
ap.add_argument('--fps', type=int, default=24); ap.add_argument('--samples', type=int, default=None); ap.add_argument('--start', type=int, default=0); ap.add_argument('--end', type=int, default=-1)
ap.add_argument('--engine', default=None); ap.add_argument('--mp4', action='store_true'); ap.add_argument('--audio'); ap.add_argument('--contact', action='store_true'); ap.add_argument('--threads', type=int, default=0)
ap.add_argument('--device', default='CPU', help='CPU, or METAL / CUDA / OPTIX / HIP / ONEAPI for a GPU (inside the Blender app: blender -b --python harness/blender_render.py -- <args>)')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])

import bpy  # noqa: E402
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene_dir = os.path.join(root, a.scene); name = os.path.basename(scene_dir.rstrip('/'))
out = os.path.abspath(a.out or os.path.join(root, 'out', name)); frames_dir = os.path.join(out, 'frames'); os.makedirs(frames_dir, exist_ok=True)
spec = importlib.util.spec_from_file_location('kf_scene', os.path.join(scene_dir, 'blender.py')); mod = importlib.util.module_from_spec(spec); sys.path.insert(0, scene_dir); spec.loader.exec_module(mod)

class Timeline:
    def __init__(self, shots):
        self.shots = []; t = 0.0
        for i, s in enumerate(shots): d = dict(s); d['i'] = i; d['start'] = t; t += s['dur']; self.shots.append(d)
        self.total = t
    def at(self, t):
        s = self.shots[-1]
        for x in self.shots:
            if t < x['start'] + x['dur']: s = x; break
        local = t - s['start']; return {'i': s['i'], 'shot': s, 't': local, 'u': max(0.0, min(1.0, local / s['dur'])), 'name': s.get('name', '')}

shots = getattr(mod, 'SHOTS', None); timeline = Timeline(shots) if shots else None
duration = getattr(mod, 'DURATION', timeline.total if timeline else 6.0)
settings = {'samples': 96, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast', 'exposure': 0.0, 'film_transparent': False, 'engine': 'CYCLES', 'max_bounces': 6, 'volume_bounces': 1, 'clamp_indirect': 8.0}
settings.update(getattr(mod, 'SETTINGS', {}))
if a.samples: settings['samples'] = a.samples
if a.engine: settings['engine'] = a.engine
ctx = {'W': a.w, 'H': a.h, 'fps': a.fps, 'duration': duration, 'timeline': timeline, 'out': out, 'scene_dir': scene_dir}

# fresh scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.resolution_x = a.w; sc.render.resolution_y = a.h; sc.render.resolution_percentage = 100; sc.render.fps = a.fps
sc.render.engine = settings['engine']; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'; sc.render.image_settings.color_depth = '8'
sc.render.film_transparent = settings['film_transparent']
if settings['engine'] == 'CYCLES':
    cy = sc.cycles; cy.device = 'CPU'
    if a.device.upper() != 'CPU':   # GPU (Apple M-series: METAL); preferences are reset by read_factory_settings, so set them here
        cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = a.device.upper(); cp.get_devices()
        for dv in cp.devices: dv.use = True
        cy.device = 'GPU'; print('GPU', a.device, [(dv.name, dv.type) for dv in cp.devices], flush=True)
    cy.samples = settings['samples']; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
    cy.use_denoising = settings['denoise']; cy.denoiser = 'OPENIMAGEDENOISE'; cy.max_bounces = settings['max_bounces']; cy.volume_bounces = settings['volume_bounces']
    cy.sample_clamp_indirect = settings['clamp_indirect']; cy.use_light_tree = True
    cy.adaptive_min_samples = settings.get('adaptive_min_samples', 8); cy.denoising_prefilter = settings.get('denoising_prefilter', 'FAST'); cy.volume_step_rate = settings.get('volume_step_rate', 2.0)
    cy.time_limit = settings.get('time_limit', 0)
    sc.render.use_motion_blur = settings['motion_blur']; sc.render.motion_blur_shutter = 0.5
    if a.threads: sc.render.threads_mode = 'FIXED'; sc.render.threads = a.threads
vs = sc.view_settings; vs.view_transform = settings['view_transform']
try: vs.look = settings['look']
except Exception as e:
    valid = [l.name for l in bpy.types.ColorManagedViewSettings.bl_rna.properties['look'].enum_items] if hasattr(bpy.types.ColorManagedViewSettings.bl_rna.properties['look'], 'enum_items') else []
    print(f'WARNING: look {settings["look"]!r} not available ({e}); valid: {valid[:12]}', flush=True)
vs.exposure = settings['exposure']
sc.frame_start = 0; sc.frame_end = int(round(duration * a.fps)) - 1

t0 = time.time(); state = mod.build(bpy, ctx); print(f'built in {time.time()-t0:.1f}s; {len(bpy.data.objects)} objects', flush=True)
total = int(round(duration * a.fps)); end = total if a.end < 0 else min(a.end, total)
print(f'rendering [{a.start}, {end}) of {total} frames @{a.fps} fps, {a.w}x{a.h}, {settings["engine"]} {settings["samples"]} spp', flush=True)
t1 = time.time()
for i in range(a.start, end):
    t = i / a.fps; sc.frame_set(i); mod.frame(bpy, ctx, state, i, t)
    sc.render.filepath = os.path.join(frames_dir, f'{i:05d}.png'); bpy.ops.render.render(write_still=True)
    done = i - a.start + 1; el = time.time() - t1
    if done % 6 == 0 or i == end - 1: print(f'frame {i+1}/{end}  {el/done:.1f} s/frame  eta {(end-i-1)*el/done/60:.1f} min', flush=True)
if a.mp4 and a.start == 0 and end == total:
    mp4 = os.path.join(out, name + '.mp4'); cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(a.fps), '-i', os.path.join(frames_dir, '%05d.png')]
    if a.audio: cmd += ['-i', a.audio]
    cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']
    if a.audio: cmd += ['-c:a', 'aac', '-b:a', '256k', '-shortest']
    subprocess.run(cmd + [mp4], check=True); print('wrote', mp4)
    if a.contact:
        step = max(1, total // 12); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', f"select='not(mod(n\\,{step}))',scale=320:-2,tile=6x2", '-frames:v', '1', '-q:v', '3', os.path.join(out, name + '.contact.jpg')], check=True)
print(f'done in {(time.time()-t0)/60:.1f} min')
