#!/usr/bin/env python3
"""Check stills of a Cutaway line film: build the scene once, render chosen times, write a contact sheet.

    python3 films/lib/cutaway/tools/stills.py <film dir> [--spec cand/a.json] [--out dir] [--w 480 --h 270] [--samples 8]
                                              [--times 3,10.5] [--max 8]

Default times: the middle of every shot (at most --max, the longest shots first), plus a frame inside the title card
and the end card. Writes <out>/stills/t<centiseconds>.jpg, <out>/sheet.jpg (each still with its time and the narration
heard at that moment, for the eyes seat) and <out>/stills.json (seconds per still). Needs bpy (pip install bpy==5.2.2);
Pillow for the sheet (skipped without it). Used by the director's eyes stage and by hand (the 2-core chat box is slow:
keep --w 480 and --samples 8 there; real check stills go to rc-render stills.yml).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.dirname(HERE)
sys.path.insert(0, LIB)


def pick_times(film, n):
    pl = film.plan; T = []
    shots = sorted(pl.shots, key=lambda s: -(s['t1'] - s['t0']))[:max(1, n - 2)]
    for s in sorted(shots, key=lambda s: s['t0']): T.append((round((s['t0'] + s['t1']) / 2, 2), f'shot {s["i"]} {s["camera"]}'))
    if pl.title: T.append((round(min(pl.title['until'] - 0.3, pl.title['at'] + 1.2), 2), 'title card'))
    if pl.end: T.append((round(pl.duration - 1.5, 2), 'end card'))
    out = []
    for t, why in sorted(T):
        if not out or t - out[-1][0] > 0.4: out.append((t, why))
    return out[:n]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('film'); ap.add_argument('--spec'); ap.add_argument('--out'); ap.add_argument('--w', type=int, default=480)
    ap.add_argument('--h', type=int, default=0); ap.add_argument('--samples', type=int, default=8); ap.add_argument('--times'); ap.add_argument('--max', type=int, default=8)
    ap.add_argument('--fps', type=int, default=24)
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    import bpy
    import engine
    film = engine.Film(a.film, a.spec)
    W = a.w; H = a.h or (round(W * 9 / 16) if film.plan.fmt == '16:9' else round(W * 16 / 9))
    times = [(float(x), 'asked') for x in a.times.split(',')] if a.times else pick_times(film, a.max)
    out = os.path.abspath(a.out or os.path.join(a.film, 'check', 'stills')); os.makedirs(os.path.join(out, 'stills'), exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.resolution_percentage = 100; sc.render.fps = a.fps
    sc.render.engine = 'CYCLES'; sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
    cy = sc.cycles; cy.device = 'CPU'; cy.samples = a.samples; cy.use_adaptive_sampling = True; cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'
    sc.view_settings.view_transform = 'AgX'
    ctx = {'W': W, 'H': H, 'fps': a.fps, 'duration': film.DURATION, 'timeline': None, 'out': out, 'scene_dir': a.film, 'times': [t for t, _ in times]}
    t0 = time.time(); state = film.build(bpy, ctx); build_s = time.time() - t0
    rec = []
    for t, why in times:
        i = int(round(t * a.fps)); s0 = time.time(); sc.frame_set(i); film.frame(bpy, ctx, state, i, i / a.fps)
        f = os.path.join(out, 'stills', f't{int(round(t * 100)):06d}.jpg'); sc.render.filepath = f; bpy.ops.render.render(write_still=True)
        rec.append({'t': t, 'why': why, 'file': os.path.relpath(f, out), 's': round(time.time() - s0, 1)}); print(f'still {t:.2f} s ({why}): {rec[-1]["s"]} s', flush=True)
    json.dump({'build_s': round(build_s, 1), 'w': W, 'h': H, 'samples': a.samples, 'stills': rec}, open(os.path.join(out, 'stills.json'), 'w'), indent=1)
    try: sheet(out, rec, film, W, H)
    except ImportError: print('no Pillow: contact sheet skipped')


def sheet(out, rec, film, W, H, cols=4, tw=330):
    from PIL import Image, ImageDraw, ImageFont
    cues = film.plan.cues; th = round(tw * H / W); cap = 52; rows = (len(rec) + cols - 1) // cols
    im = Image.new('RGB', (cols * (tw + 8) + 8, rows * (th + cap + 8) + 8), (21, 17, 13)); d = ImageDraw.Draw(im)
    try: font = ImageFont.truetype(os.path.join(engine_root(), 'ads', 'fonts', 'InstrumentSans.ttf'), 12)
    except Exception: font = ImageFont.load_default()
    for k, r in enumerate(rec):
        x = 8 + (k % cols) * (tw + 8); y = 8 + (k // cols) * (th + cap + 8)
        im.paste(Image.open(os.path.join(out, r['file'])).convert('RGB').resize((tw, th)), (x, y))
        ln = None
        for l in cues.get('lines', []):
            if r['t'] >= l['start'] - 0.05: ln = l
        text = f"{r['t']:.1f} s {ln['id'] if ln else ''} [{r['why']}] " + (ln['text'] if ln else '(no narration)')
        words = text.split(); lines = ['']
        for w in words:
            if d.textlength(lines[-1] + ' ' + w, font=font) > tw: lines.append(w)
            else: lines[-1] = (lines[-1] + ' ' + w).strip()
        for j, l in enumerate(lines[:3]): d.text((x + 2, y + th + 3 + 15 * j), l, fill=(235, 235, 235), font=font)
    im.save(os.path.join(out, 'sheet.jpg'), quality=82); print('sheet', os.path.join(out, 'sheet.jpg'))


def engine_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(LIB)))


if __name__ == '__main__':
    main()
