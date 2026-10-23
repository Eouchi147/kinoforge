"""storybook-ink: a children's picture book (work in progress)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _npr_lines as NL  # noqa: E402

INK = np.array([0.22, 0.13, 0.10], np.float32)
PAPER = np.array([0.968, 0.930, 0.835], np.float32)
PENCIL = np.array([0.46, 0.36, 0.33], np.float32)
SKY_TOP = np.array([0.66, 0.80, 0.84], np.float32)
SKY_LOW = np.array([0.99, 0.88, 0.72], np.float32)
GRASS = np.array([0.56, 0.70, 0.36], np.float32)
LEAF = np.array([0.47, 0.62, 0.34], np.float32)
WATER = np.array([0.56, 0.78, 0.76], np.float32)
GROUPS_BIG = [('strata', 'bottom'), ('top',), ('grass',), ('leaf',), ('water',)]
GROUPS = [('strata', 'bottom'), ('top',), ('grass',), ('leaf',), ('water',), ('rock',), ('build',), ('bark', 'plant'), ('find',), ('animal',)]


def stylize(P, info):
    img, alb, nrm, pos, dep, ob = P['img'], P['alb'], P['nrm'], P['pos'], P['dep'], P['ob']
    H, W = dep.shape; sh = (H, W); s = NL.px_scale(W)
    ma, sky = NL.region_ids(P)
    grass = NL.cls_mask(ma, 'grass'); leaf = NL.cls_mask(ma, 'leaf'); soil = NL.cls_mask(ma, 'strata', 'bottom'); water = NL.cls_mask(ma, 'water')
    build = NL.cls_mask(ma, 'build'); bark = NL.cls_mask(ma, 'bark'); floor = NL.cls_mask(ma, 'floor')
    lw = float(np.clip(2.6 / max(np.median(dep[~sky & ~floor]), 0.3), 0.8, 2.2))      # closer camera, bolder pen
    # --- the light alone: relative to its own neighbourhood, so a spotlight is a glow and a cast shadow is a shadow
    L = NL.lum(img) / np.maximum(NL.lum(alb), 0.05)
    Lb = NL.blur(np.clip(L, 0, 3), 2.0 * s); Lm = NL.blur(np.clip(L, 0, 3), 40 * s) + 0.05
    rel = Lb / Lm
    shade = 0.90 + 0.14 * np.clip(rel - 1.0, -0.8, 1.0) * 1.0                    # glow: a touch lighter, shadow: a touch darker
    shade = np.clip(shade, 0.78, 1.05)
    # --- flat colours from the albedo pass, smoothed inside each kind of thing (washes stop at the lines)
    A = NL.group_blur(alb, ma, sky, GROUPS_BIG, 4.0 * s); A2 = NL.group_blur(alb, ma, sky, GROUPS, 1.2 * s)
    A = np.where(soil[..., None], 0.5 * A + 0.5 * A2, 0.75 * A + 0.25 * A2)
    small = NL.cls_mask(ma, 'find', 'animal', 'build', 'bark', 'plant', 'rock')
    A = np.where(small[..., None], A2, A)
    A = NL.lin_to_srgb(A)
    g = NL.lum(A)[..., None]; A = np.clip(g + (A - g) * 1.12, 0, 1)
    A = np.clip(A ** 0.80 * np.array([1.05, 1.0, 0.92], np.float32), 0, 1)
    # --- grass: smooth rounded silhouette from the blade mask
    gm = NL.blur(grass.astype(np.float32), 3.0 * s) + 0.08 * NL.fbm(sh, 10 * s, 5, 2)
    gmask = NL.smoothstep(0.33, 0.45, gm) > 0.5
    # --- sky: wet-in-wet wash
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    t = np.clip(NL.smoothstep(0.0, 0.66, yy) ** 1.1 + 0.10 * NL.fbm(sh, 120 * s, 21, 3), 0, 1)[..., None]
    skyc = SKY_TOP[None, None, :] * (1 - t) + SKY_LOW[None, None, :] * t
    cl = NL.smoothstep(0.5, 1.2, NL.fbm(sh, 70 * s, 31, 3) + 0.3 * (1 - yy * 2))
    skyc = skyc + (PAPER[None, None, :] - skyc) * (0.5 * cl[..., None])
    # --- wash layer per kind of thing
    wash = A * shade[..., None]
    lit = np.clip(0.5 + (rel - 1.0) * 0.8 + 0.5 * (NL.blur(nrm[..., 2], 3 * s) * 0.5 + 0.2), 0, 1)
    leaf_c = LEAF[None, None, :] * (0.80 + 0.34 * lit[..., None]) * np.array([1.0, 1.0, 1.05], np.float32)
    wash = np.where(leaf[..., None], leaf_c, wash)
    grass_c = GRASS[None, None, :] * (0.92 + 0.12 * NL.fbm(sh, 18 * s, 8, 2)[..., None])
    gfill = gmask & ~(leaf | build | bark | NL.cls_mask(ma, 'top', 'find', 'rock', 'plant'))
    wash = np.where(gfill[..., None], grass_c, wash)
    wash = np.where(grass[..., None] & ~(leaf | build | bark)[..., None], grass_c, wash)
    # glass water: soft teal wash over what is seen through it
    seen = NL.blur(NL.lin_to_srgb(np.clip(img / (1 + img) * 1.6, 0, 1)), 3 * s)
    wat_c = WATER[None, None, :] * 0.62 + seen * 0.55 * np.array([0.9, 1.0, 1.0], np.float32)
    wash = np.where(water[..., None], wat_c, wash)
    wash = np.where(sky[..., None], skyc, wash)
    fl = NL.blur(NL.lum(img), 6 * s); fref = np.percentile(fl[floor], 85) + 1e-6 if floor.any() else 1.0
    fsh = NL.smoothstep(0.05, 0.75, 1 - fl / fref)
    far = NL.smoothstep(4.0, 16.0, dep)[..., None]
    floor_c = (np.array([0.96, 0.90, 0.78], np.float32)[None, None, :] * (1 - 0.30 * fsh[..., None]) * (1 - far) + skyc * far)
    wash = np.where(floor[..., None], floor_c, wash)
    wash = np.where((gmask & sky)[..., None], grass_c, wash)
    # --- ink lines: three weights from the passes
    E = NL.edge_maps(P, s)
    keyc = np.where(grass | gmask, 4, np.where(sky | floor, 0, ma)).astype(np.float32)
    obk = np.where(grass | gmask | sky | floor, 0, np.rint(ob)).astype(np.float32)
    key = keyc * 8192 + obk
    sil = np.zeros(sh, np.float32)
    for ax in (0, 1):
        d = np.abs(key - np.roll(key, 1, ax)) > 0
        sil = np.maximum(sil, d.astype(np.float32))
    sil[0] = sil[-1] = 0; sil[:, 0] = sil[:, -1] = 0
    notgrass = ~(gmask | (NL.blur(grass.astype(np.float32), 4 * s) > 0.2) | (NL.blur(floor.astype(np.float32), 3 * s) > 0.02))
    crease = np.clip(NL.smoothstep(0.30, 0.65, E['crease']), 0, 1) * notgrass
    dep_e = np.clip(NL.smoothstep(0.20, 0.55, E['depth']), 0, 1) * notgrass
    alb_g = NL.gradmag(NL.lum(NL.blur(NL.lin_to_srgb(alb), 0.9)))
    soil_e = NL.smoothstep(0.045, 0.12, alb_g) * soil.astype(np.float32)
    thin = np.maximum(crease * (1 - leaf) * 0.9 + crease * leaf * 0.5, soil_e * 0.9)
    heavy = np.maximum(sil, dep_e)
    dx = NL.fbm(sh, 24 * s, 41, 3) * 1.5 * s; dy = NL.fbm(sh, 24 * s, 42, 3) * 1.5 * s
    press = 1.0 + 0.30 * NL.fbm(sh, 55 * s, 43, 2)
    lift = NL.smoothstep(-1.7, -1.0, NL.fbm(sh, 8 * s, 44, 2))
    h_ = NL.blur(NL.warp(heavy, dx, dy), 0.9 * s * lw) * press * (1.0 if lw < 1.01 else 1.0)
    t_ = NL.blur(NL.warp(thin, dx, dy), 0.7 * s * lw) * press
    th = 1.0 / lw ** 0.5
    line = np.maximum(NL.smoothstep(0.16 * th, 0.30 * th, h_), NL.smoothstep(0.17 * th, 0.33 * th, t_) * 0.75) * lift
    bm = np.ones(sh, np.float32); b = int(6 * s); bm[:b] = bm[-b:] = 0; bm[:, :b] = bm[:, -b:] = 0
    line = line * bm
    # --- watercolor: pigment pools at the lines, the wash slides off them, granulation, blooms
    near = NL.blur(np.clip(np.maximum(heavy, thin), 0, 1), 4 * s)
    pool = 1.0 - 0.14 * np.clip(near * 3.0, 0, 1)
    wx = NL.fbm(sh, 55 * s, 51, 3) * 2.6 * s + 2.0 * s; wy = NL.fbm(sh, 55 * s, 52, 3) * 2.6 * s + 1.2 * s
    wash = NL.warp(wash, wx, wy) * pool[..., None]
    dens = 1.0 + 0.035 * NL.fbm(sh, 45 * s, 61, 3) + 0.018 * NL.noise(sh, 1.0 * s, 62) + 0.016 * NL.noise(sh, 2.4 * s, 63)
    bloom = NL.smoothstep(0.9, 1.8, NL.fbm(sh, 60 * s, 64, 2))
    wash = wash * dens[..., None]
    wash = wash + (PAPER[None, None, :] - wash) * (0.16 * bloom)[..., None]
    wash = wash + (PAPER[None, None, :] - wash) * 0.03
    # --- pencil hatching in the shadows, locked to the world
    shadow = NL.smoothstep(0.82, 0.45, rel) * (~sky) * (~gmask)
    shadow = NL.blur(shadow.astype(np.float32), 1.5 * s)
    u = pos[..., 2] - 0.8 * pos[..., 0] - 0.2 * pos[..., 1]
    hat = NL.hatch(u, 90.0, 1.0 * s, min_px=4.0 * s)
    pen = hat * shadow * (0.6 + 0.4 * np.clip(NL.noise(sh, 1.4 * s, 71) * 0.5 + 0.6, 0, 1)) * 0.6
    wash = wash * (1 - pen[..., None] * (1 - PENCIL[None, None, :]) * 0.9)
    # --- paper and ink
    pap = NL.paper(sh, PAPER, 3, s, fibre=0.02, mottle=0.03, grain=0.012)
    out = wash * (pap / PAPER[None, None, :])
    inkc = INK[None, None, :] * (1 + 0.2 * NL.noise(sh, 30 * s, 81)[..., None])
    out = out * (1 - line[..., None] * 0.92) + inkc * (line[..., None] * 0.92)
    out = out * NL.vignette(sh, 0.12)[..., None]
    return np.clip(out, 0, 1).astype(np.float32)


def apply(bpy, film, ctx):
    NL.setup(bpy, film, ctx, stylize)
    NL.recolor_overlay(film, (0.99, 0.95, 0.85), (0.22, 0.13, 0.10))


def frame(bpy, film, ctx, t, shot):
    NL.frame(bpy, film, ctx, t, shot)
