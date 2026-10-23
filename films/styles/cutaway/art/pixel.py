"""Art direction `pixel`: a 16-bit game, the Cutaway as a pixel-art diorama.

The world is rendered small (a quarter of the frame, 320 x 180 for a 1280 x 720 still: every pixel of it becomes a 4 x 4
block) with a tiny pixel filter so edges stay aliased, then the compositor (a) takes the picture to display colours,
(b) adds an ordered 4 x 4 Bayer dither, (c) snaps every pixel to a fixed 32-colour palette (a 16 x 16 x 16 colour cube
looked up in an image, nearest palette colour by perceptual distance), and (d) scales it up nearest-neighbour: crisp
pixel clusters, no blur. Dark outlines are drawn where the picture jumps in brightness. The labels, leaders and the
title (set in code, overlay.py) live in a second scene rendered at full resolution and are laid over the pixels
afterwards, so they stay crisp and readable. Depth of field, god rays and the golden fog are off (pixel art is flat in
focus). What it changes: render resolution, compositor, one world tint; materials are left alone (the palette does the
styling). Render cost vs the reference: about a quarter to a third (16 times fewer pixels, plus a few seconds for the
full-size words scene).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _post as P  # noqa: E402

# the palette (own choice, 32 colours): dusk sky, grass, soil, water, bone and metal
PALETTE = [
    '#120d1c', '#2c2140', '#4d3a5a', '#7a4f6a', '#b0657a', '#e08a6d', '#f2b47a', '#f9dfa3',
    '#fff5df', '#3b2416', '#5c3a20', '#7f5230', '#a5703d', '#cf9a5a', '#e6c488', '#8a3b2b',
    '#c0573a', '#16301f', '#24502b', '#3a7a2f', '#6aa83a', '#a6cf5a', '#d6e07a', '#1e4a54',
    '#2c7b82', '#5cb6b0', '#a7e0d4', '#6a6a72', '#9a98a0', '#d8d2c8', '#e8c14a', '#c9463d',
]
LV = 16            # levels per channel of the colour cube
ART_W = 320        # the art is 320 pixels wide (180 high in 16:9): every art pixel is a SCALE x SCALE block


def _lab(rgb):
    rgb = np.asarray(rgb, float)
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = lin @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lut_array():
    """(16, 256, 3): x = blue * 16 + red, y = green; each cell holds the nearest palette colour (Lab distance, lightness weighted a little)."""
    pal = np.array([P.hexrgb(h) for h in PALETTE]); pl = _lab(pal)
    g, b, r = np.meshgrid(np.arange(LV), np.arange(LV), np.arange(LV), indexing='ij')
    cells = np.stack([r, g, b], -1).reshape(-1, 3) / (LV - 1.0); cl = _lab(cells)
    w = np.array([1.15, 1.0, 1.0]); d = (((cl[:, None, :] - pl[None]) * w) ** 2).sum(-1); idx = d.argmin(1)
    out = pal[idx].reshape(LV, LV, LV, 3)          # [g, b, r]
    img = np.zeros((LV, LV * LV, 3), np.float32)
    for gi in range(LV):
        for bi in range(LV): img[gi, bi * LV:(bi + 1) * LV] = out[gi, bi]
    return img


def bayer(n=4):
    m = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16.0 - 0.5 + 1 / 32
    return m


def apply(bpy, film, ctx):
    W, H = ctx['W'], ctx['H']; sc = bpy.context.scene
    SCALE = max(1, int(round(W / ART_W)))                   # screen pixels per art pixel (4 at 1280 wide)
    # ---- the world, small and crisp
    sc.cycles.samples = min(sc.cycles.samples, 6)           # 16 rendered pixels are averaged into one art pixel
    # ---- the words in their own scene
    B = P.split_overlay(bpy, film, ctx)
    P.hide_shafts(film)
    # ---- compositor
    w, h = W // SCALE, H // SCALE
    bm = bayer(); dith = np.tile(bm, (h // 4 + 1, w // 4 + 1))[:h, :w]
    dim = P.array_image(bpy, 'kf_dither', dith)
    lim = P.array_image(bpy, 'kf_lut', lut_array())
    C = P.Comp(bpy, sc)
    rl = C.render(sc); words = C.render(B)
    bl = C.node('CompositorNodeBlur', {'Image': rl.outputs['Image'], 'Size': (SCALE / 2.0, SCALE / 2.0)}); bl.inputs['Type'].default_value = 'Flat'
    small = C.scale(bl.outputs['Image'], 1.0 / SCALE, interp='Bilinear')
    col = C.display(small, view='AgX', look='AgX - Medium High Contrast', exposure=film.SETTINGS['exposure'] + 0.55)
    # a little lift in saturation and contrast so the palette picks the lively colours
    hs = C.node('CompositorNodeHueSat', {'Image': col, 'Saturation': 1.4, 'Value': 1.0})
    col = hs.outputs['Image']
    d = C.image(dim); amp = 0.055
    dd = C.vmath('SCALE', d, scale=amp)
    sep = C.sep(C.mix(1.0, col, dd, 'ADD'))
    q = lambda ch: C.math('FLOOR', C.math('MULTIPLY', C.math('MINIMUM', C.math('MAXIMUM', ch, 0.0), 0.9999), float(LV)))
    ri, gi, bi = q(sep['Red']), q(sep['Green']), q(sep['Blue'])
    u = C.math('DIVIDE', C.math('ADD', C.math('ADD', C.math('MULTIPLY', bi, float(LV)), ri), 0.5), float(LV * LV))
    v = C.math('DIVIDE', C.math('ADD', gi, 0.5), float(LV))
    uv = C.comb(u, v, 1.0)
    mu = C.node('CompositorNodeMapUV'); mu.inputs['Interpolation'].default_value = 'Nearest'
    C.put(mu, 'Image', C.image(lim)); C.put(mu, 'UV', uv)
    pic = mu.outputs['Image']
    # outlines: dark where neighbouring pixels jump in lightness
    lum = C.node('CompositorNodeRGBToBW', {'Image': col}).outputs[0]
    sob = C.node('CompositorNodeFilter', {'Image': lum, 'Factor': 1.0}); sob.inputs['Type'].default_value = 'Sobel'
    edge = C.math('GREATER_THAN', C.math('ABSOLUTE', sob.outputs['Image']), 0.34)
    ink = C.mix(C.math('MULTIPLY', edge, 0.85), pic, P.hexrgb(PALETTE[0]) + (1.0,))
    big = C.scale(ink, float(SCALE), interp='Nearest')
    # words on top at full resolution
    ow = C.node('CompositorNodeAlphaOver', {'Background': big, 'Foreground': words.outputs['Image']})
    dbg = os.environ.get('KF_DBG')
    C.finish({'1': col, '2': rl.outputs['Image'], '3': words.outputs['Image'], '4': small, '5': pic}.get(dbg) or ow.outputs['Image'])
    P.display_raw(sc)
    film.pixel = {'scene_words': B}


def frame(bpy, film, ctx, t, shot):
    film.cam.ob.data.dof.use_dof = False
    if os.environ.get('KF_DBG') == '9':
        B = film.pixel['scene_words']
        print('WORDS', [(o.name, round(o.scale[0], 5), [round(v, 3) for v in o.location], o.type) for o in B.objects if not o.hide_render], flush=True)
    if os.environ.get('KF_DBG') == '8':
        B = film.pixel['scene_words']; B.render.filepath = '/tmp/claude-0/-home-claude/b576bd3d-71d2-5bea-b286-3ba8d53b8c9d/scratchpad/out/words.png'
        B.render.image_settings.file_format = 'PNG'; B.render.image_settings.color_mode = 'RGBA'
        bpy.ops.render.render(scene='kf_words', write_still=True)
