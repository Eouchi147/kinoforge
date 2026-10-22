#!/usr/bin/env python3
"""Render Cutaway board stills (CPU Cycles, free).

    python3 films/styles/cutaway/board.py A [--aspect 16:9|9:16] [--w 1920] [--samples 96] [--t 0] [--out board/A-studio-block.jpg]
"""
import argparse, os, sys, time
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
ap = argparse.ArgumentParser(); ap.add_argument('look'); ap.add_argument('--aspect', default='16:9'); ap.add_argument('--w', type=int, default=1920)
ap.add_argument('--samples', type=int, default=96); ap.add_argument('--t', type=float, default=1.0); ap.add_argument('--out'); ap.add_argument('--threads', type=int, default=0)
ap.add_argument('--border', type=float, nargs=4, help='render only x0 x1 y0 y1 (0..1) (inspection crops)')
ap.add_argument('--blend', help='also save the .blend here (debug)')
a = ap.parse_args()
import bpy  # noqa: E402
import cutaway as cw, looks  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
W = a.w; H = round(W * 9 / 16) if a.aspect == '16:9' else round(W * 16 / 9)
t0 = time.time(); kit = cw.Kit(bpy, seed=1, loop=8.0)
S = looks.LOOKS[a.look](bpy, kit, a.aspect)
cw.render_settings(bpy, W, H, a.samples, look=S['look'], exposure=S['exposure'], threads=a.threads)
kit.update(a.t); bpy.context.scene.frame_set(int(a.t * 24))
print(f'built in {time.time() - t0:.1f}s, {len(bpy.data.objects)} objects', flush=True)
if a.border:
    r = bpy.context.scene.render; r.use_border = True; r.use_crop_to_border = True; r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = a.border
if a.blend: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.blend))
out = os.path.abspath(a.out or os.path.join(here, 'board', f'{a.look}-{looks.NAMES[a.look]}{"-vertical" if a.aspect == "9:16" else ""}.jpg'))
os.makedirs(os.path.dirname(out), exist_ok=True); png = out.rsplit('.', 1)[0] + '.tmp.png'
bpy.context.scene.render.filepath = png; t1 = time.time(); bpy.ops.render.render(write_still=True)
print(f'rendered {W}x{H} {a.samples} spp in {time.time() - t1:.1f}s', flush=True)
from PIL import Image  # noqa: E402
Image.open(png).convert('RGB').save(out, quality=90); os.remove(png); print('wrote', out)
