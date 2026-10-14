"""mac_render.py — render a KINOFORGE Blender scene on a Mac with Blender.app (Metal GPU), straight to an MP4.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P harness/mac_render.py -- proto/<scene> [--w 1920 --h 1080 --samples 64]

* Runs inside Blender's own Python (no pip, no ffmpeg, no Xcode needed). Uses the Apple GPU through Metal when present.
* Frames go to renders/<scene>/frames/*.jpg; an interrupted render resumes where it stopped (existing frames are kept).
* Stop-motion pairs: by contract frame 2k+1 is the same picture as 2k, so odd frames are copied, never path-traced again.
* At the end Blender's built-in encoder writes renders/<scene>/<scene>.mp4 (H.264, high quality, no audio: the mix is added later).
"""
import sys, os, time, shutil, importlib.util

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def opt(name, default, cast=str):
    if name in argv: return cast(argv[argv.index(name) + 1])
    return default
scene_arg = [a for a in argv if not a.startswith('--') and (argv.index(a) == 0 or not argv[argv.index(a) - 1].startswith('--'))][0]
W, H, FPS = opt('--w', 1920, int), opt('--h', 1080, int), opt('--fps', 24, int)
SAMPLES = opt('--samples', 64, int); START = opt('--start', 0, int); END = opt('--end', -1, int)
os.environ['KF_NO_PAIR_REUSE'] = '1'            # pairs are handled here (copy), the scene must not try its own trick
os.environ.setdefault('KF_SPP_CAP', '0')

import bpy  # noqa: E402
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene_dir = os.path.join(root, scene_arg); name = os.path.basename(scene_dir.rstrip('/'))
# frames live outside iCloud-synced folders (~/Movies), only the finished MP4 is copied back next to the studio files
out = os.path.abspath(os.path.expanduser(opt('--out', os.path.join('~/Movies/KINOFORGE renders', name)))); fdir = os.path.join(out, 'frames'); os.makedirs(fdir, exist_ok=True)
deliver = os.path.join(root, 'renders'); os.makedirs(deliver, exist_ok=True)
spec = importlib.util.spec_from_file_location('kf_scene', os.path.join(scene_dir, 'blender.py')); mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, scene_dir); spec.loader.exec_module(mod)
duration = getattr(mod, 'DURATION', 6.0)
settings = {'samples': SAMPLES, 'denoise': True, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast', 'exposure': 0.0, 'max_bounces': 6, 'volume_bounces': 1, 'clamp_indirect': 8.0}
settings.update({k: v for k, v in getattr(mod, 'SETTINGS', {}).items() if k != 'samples'})
ctx = {'W': W, 'H': H, 'fps': FPS, 'duration': duration, 'timeline': None, 'out': out, 'scene_dir': scene_dir}

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; r = sc.render
r.resolution_x, r.resolution_y, r.resolution_percentage, r.fps = W, H, 100, FPS
r.engine = 'CYCLES'; r.image_settings.file_format = 'JPEG'; r.image_settings.quality = 95; r.image_settings.color_mode = 'RGB'
cy = sc.cycles
gpu = False
try:                                              # Apple GPU via Metal
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices: d.use = (d.type == 'METAL')
    gpu = any(d.use for d in prefs.devices)
except Exception as e: print('Metal not available:', e, flush=True)
cy.device = 'GPU' if gpu else 'CPU'
cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02; cy.use_denoising = True
try: cy.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
cy.max_bounces = settings['max_bounces']; cy.sample_clamp_indirect = settings['clamp_indirect']; cy.use_light_tree = True
vs = sc.view_settings; vs.view_transform = settings['view_transform']
try: vs.look = settings['look']
except Exception: pass
vs.exposure = settings['exposure']
total = int(round(duration * FPS)); end = total if END < 0 else min(END, total)
sc.frame_start = 0; sc.frame_end = total - 1
t0 = time.time(); state = mod.build(bpy, ctx)
cy.samples = SAMPLES                              # the scene's build() may cap samples for CPU budgets: on the GPU we want the full count
print(f'KINOFORGE | {name} | {W}x{H} | {SAMPLES} spp | device {cy.device} | frames {START}..{end - 1} of {total} | built in {time.time() - t0:.1f}s', flush=True)

t1 = time.time(); done = 0
for i in range(START, end):
    path = os.path.join(fdir, f'{i:05d}.jpg')
    if os.path.exists(path) and os.path.getsize(path) > 0: continue          # resume
    prev = os.path.join(fdir, f'{i - 1:05d}.jpg')
    if i % 2 == 1 and os.path.exists(prev):                                     # the second frame of a stop-motion pair
        shutil.copyfile(prev, path); continue
    sc.frame_set(i); mod.frame(bpy, ctx, state, i, i / FPS)
    r.filepath = path; bpy.ops.render.render(write_still=True); done += 1
    el = time.time() - t1; left = sum(1 for k in range(i + 1, end) if k % 2 == 0)
    print(f'frame {i + 1}/{end}   {el / done:.1f} s per picture   about {left * el / done / 60:.0f} min left', flush=True)

# encode with Blender's own FFmpeg (a throwaway scene holding the image sequence)
files = sorted(f for f in os.listdir(fdir) if f.endswith('.jpg'))
if len(files) == total or '--encode-partial' in argv:
    enc = bpy.data.scenes.new('encode')
    if bpy.context.window: bpy.context.window.scene = enc
    enc.render.resolution_x, enc.render.resolution_y, enc.render.resolution_percentage, enc.render.fps = W, H, 100, FPS
    enc.sequence_editor_create()
    seq = enc.sequence_editor
    strips = seq.strips if hasattr(seq, 'strips') else seq.sequences
    st = strips.new_image('frames', os.path.join(fdir, files[0]), 1, 1)
    for f in files[1:]: st.elements.append(f)
    enc.frame_start, enc.frame_end = 1, len(files)
    try: enc.render.image_settings.media_type = 'VIDEO'          # Blender 5.x: choose video output before the container
    except Exception: pass
    enc.render.image_settings.file_format = 'FFMPEG'
    ff = enc.render.ffmpeg; ff.format = 'MPEG4'; ff.codec = 'H264'; ff.constant_rate_factor = 'HIGH'; ff.ffmpeg_preset = 'GOOD'; ff.audio_codec = 'NONE'
    enc.view_settings.view_transform = 'Standard'; enc.view_settings.look = 'None'; enc.view_settings.exposure = 0.0
    enc.render.filepath = os.path.join(out, name + '.mp4')
    bpy.ops.render.render(animation=True, scene=enc.name)
    mp4 = [f for f in os.listdir(out) if f.startswith(name) and f.endswith('.mp4')]
    if mp4: shutil.copyfile(os.path.join(out, mp4[0]), os.path.join(deliver, name + '.mp4'))
    print('KINOFORGE | done | ' + (os.path.join(deliver, name + '.mp4') if mp4 else 'encode failed: frames are in ' + fdir), flush=True)
else:
    print(f'KINOFORGE | {len(files)}/{total} frames on disk — run the same command again to finish', flush=True)
