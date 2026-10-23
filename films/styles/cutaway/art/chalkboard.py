"""chalkboard: the cutaway drawn in chalk on a slate blackboard (teaching).

Dusty white chalk for the outlines, and a few coloured sticks (yellow, pink, pale blue) for the soil layers, the water and each
find. Strokes are rough and grainy (the board's tooth breaks them up), the soil layers are rubbed in with the side of the chalk
(hatching smudged with a finger), and the board is a dark green-black slate with old eraser swipes, dust and a slim wooden
frame. Labels become chalk-white type on dark plates.

What it changes: the picture is a numpy stylization of the Cycles passes (_npr_lines.py); light and shadow are ignored, the
colour is the chalk's. Render cost: the reference's Cycles render plus about 5 s of numpy and about 1 s for the label pass.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _npr_lines as NL  # noqa: E402

BOARD = np.array([0.070, 0.100, 0.092], np.float32)
BOARD_HI = np.array([0.150, 0.190, 0.172], np.float32)
WHITE = np.array([0.94, 0.94, 0.89], np.float32)
YELLOW = np.array([0.98, 0.84, 0.36], np.float32)
PINK = np.array([0.96, 0.58, 0.68], np.float32)
BLUE = np.array([0.60, 0.80, 0.95], np.float32)
WOOD = np.array([0.30, 0.19, 0.11], np.float32)
FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))), 'ads', 'fonts', 'Archivo.ttf')
CHALKS = [WHITE, YELLOW, PINK, BLUE]
# chalk colour per soil layer (time strata: topsoil, sand, clay, loam, gravel, ochre, limestone, bedrock)
LAYER_CHALK = [0, 1, 2, 2, 3, 1, 0, 3]


def _grain(sh, s, seed, strength=0.65):
    g = 0.7 * NL.noise(sh, 0.8 * s, seed) + 0.5 * NL.noise(sh, 2.0 * s, seed + 1) + 0.25 * NL.fbm(sh, 9 * s, seed + 2, 2)
    return 1.0 - strength + strength * NL.smoothstep(-0.7, 0.9, g)


def stylize(P, info):
    img, alb, nrm, pos, dep, ob = P['img'], P['alb'], P['nrm'], P['pos'], P['dep'], P['ob']
    H, W = dep.shape; sh = (H, W); s = NL.px_scale(W)
    ma, sky = NL.region_ids(P)
    cut = NL.cls_mask(ma, 'strata'); bottom = NL.cls_mask(ma, 'bottom'); grass = NL.cls_mask(ma, 'grass'); leaf = NL.cls_mask(ma, 'leaf')
    water = NL.cls_mask(ma, 'water'); floor = NL.cls_mask(ma, 'floor'); top = NL.cls_mask(ma, 'top')
    obj = NL.cls_mask(ma, 'find', 'animal', 'build', 'bark', 'rock', 'plant', 'fly')
    lw = float(np.clip(2.6 / max(np.median(dep[~sky & ~floor]), 0.3), 0.8, 2.0))
    gm = NL.blur(grass.astype(np.float32), 3.0 * s); gmask = gm > 0.40
    # --- the slate: dark green-black, eraser swipes, dust, tooth
    out = np.zeros((H, W, 3), np.float32) + BOARD
    swipe = NL.noise(sh, 40 * s, 3, aniso=(3.2, 0.35)) * 0.6 + NL.fbm(sh, 140 * s, 4, 3) * 0.5
    ghost = NL.smoothstep(0.1, 1.3, swipe) * 0.9
    out = out + (BOARD_HI - BOARD)[None, None, :] * ghost[..., None]
    out = out * (1.0 + 0.05 * NL.noise(sh, 0.8 * s, 5)[..., None])
    # --- strokes: edges as in the other line looks
    E = NL.edge_maps(P, s)
    keyc = np.where(grass | gmask, 4, np.where(sky | floor, 0, ma)).astype(np.float32)
    obk = np.where(grass | gmask | sky | floor, 0, np.rint(ob)).astype(np.float32)
    key = keyc * 8192 + obk
    sil = np.zeros(sh, np.float32)
    for ax in (0, 1):
        sil = np.maximum(sil, (np.abs(key - np.roll(key, 1, ax)) > 0).astype(np.float32))
    far = NL.blur((grass | floor).astype(np.float32), 4 * s) > 0.02
    crease = NL.smoothstep(0.30, 0.65, E['crease']) * (~far)
    dep_e = NL.smoothstep(0.20, 0.55, E['depth']) * (~far)
    pal = info.get('strata') if isinstance(info, dict) else None
    lab = NL.strata_labels(alb, pal, 3.0 * s, 4.0 * s)
    lab_e = NL.label_edges(lab, cut) * (NL.blur(cut.astype(np.float32), 2.0) > 0.9)
    thin = np.maximum(crease * 0.8, lab_e * 0.9)
    heavy = np.maximum(sil, dep_e * 0.9)
    dx = NL.fbm(sh, 18 * s, 41, 3) * 1.3 * s; dy = NL.fbm(sh, 18 * s, 42, 3) * 1.3 * s
    bm = np.ones(sh, np.float32); b = int(16 * s); bm[:b] = bm[-b:] = 0; bm[:, :b] = bm[:, -b:] = 0
    lh = NL.blur(NL.warp(heavy, dx, dy), 1.0 * s * lw); lt = NL.blur(NL.warp(thin, dx, dy), 0.8 * s * lw)
    stroke_h = NL.smoothstep(0.13, 0.30, lh); stroke_t = NL.smoothstep(0.12, 0.28, lt) * 0.8
    # --- chalk colour of every outline: white, except finds which each take one coloured stick
    oid = np.rint(ob).astype(np.int32)
    which = np.where(obj & ~leaf, (oid * 7 + 1) % 3 + 1, 0)           # 1 yellow, 2 pink, 3 blue; 0 white
    which_s = np.rint(NL.blur(which.astype(np.float32), 5 * s)).astype(np.int32)
    which_d = np.where(NL.blur(obj.astype(np.float32), 5 * s) > 0.05, np.maximum(which, which_s), 0)
    col_lines = np.zeros((H, W, 3), np.float32) + WHITE
    for k, c in ((1, YELLOW), (2, PINK), (3, BLUE)):
        col_lines = np.where((which_d == k)[..., None], c, col_lines)
    col_lines = np.where((grass | gmask | top)[..., None] & ~obj[..., None] & ~leaf[..., None], YELLOW, col_lines)
    col_lines = np.where(water[..., None], BLUE, col_lines)
    # --- soil layers rubbed in with the side of the chalk: scribble hatching, smudged
    along = pos[..., 0] + pos[..., 1]; z = pos[..., 2]
    f = 38.0
    hat_a = NL.hatch(z - along * 0.9, f, 1.4 * s, min_px=3.5 * s); hat_b = NL.hatch(z + along * 0.9, f * 0.8, 1.2 * s, min_px=3.5 * s)
    jit = NL.noise(sh, 6 * s, 61)
    rub = np.clip(hat_a * (0.6 + 0.4 * (jit > -0.3)) + hat_b * 0.5 * (jit > 0.5), 0, 1)
    smudge = NL.blur(rub, 3.5 * s) * 1.8
    chalk_i = np.array(LAYER_CHALK, np.int32)[np.clip(lab, 0, 7)]
    lay_c = np.stack([CHALKS[k] for k in range(4)], 0)[chalk_i]                    # (H,W,3)
    layer_cov = np.clip(rub * 0.85 + smudge * 0.35, 0, 1) * cut * (NL.blur(lab_e, 2.5) < 0.03)
    # --- water: pale blue haze and wavy lines
    wl = NL.hatch(z + 0.01 * NL.noise(sh, 12 * s, 71), 46.0, 1.4 * s, min_px=3.5 * s)
    water_cov = np.clip(wl * 0.6 + NL.blur(wl, 4 * s) * 0.8, 0, 1) * water
    # --- grass flecks, foliage dust, ground
    tick = NL.smoothstep(1.4, 1.8, NL.noise(sh, 1.8 * s, 11, aniso=(4.0, 0.5))) * gmask
    leaf_cov = np.clip(NL.blur(leaf.astype(np.float32), 2.0 * s) * 0.22 + NL.smoothstep(0.9, 1.6, NL.noise(sh, 1.6 * s, 81)) * leaf * 0.5, 0, 1)
    dust_cov = NL.blur(((obj | bottom) & ~leaf).astype(np.float32), 5.0 * s) * 0.0
    # --- composite onto the slate with the board's tooth
    grain = _grain(sh, s, 91); grain2 = _grain(sh, s, 95, 0.8)
    def lay(base, cov, col, g):
        a = np.clip(cov * g, 0, 1)[..., None]; return base + (col - base) * a
    out = lay(out, layer_cov * 0.9, lay_c, grain)
    ofill = np.clip(hat_a * 0.7 + NL.blur(hat_a, 3 * s) * 1.0, 0, 1) * (obj & ~leaf) * 0.7
    cols_o = np.zeros((H, W, 3), np.float32) + WHITE
    for k, c in ((1, YELLOW), (2, PINK), (3, BLUE)):
        cols_o = np.where((which_d == k)[..., None], c, cols_o)
    out = lay(out, ofill, cols_o, grain)
    out = lay(out, water_cov * 0.9, np.broadcast_to(BLUE, (H, W, 3)), grain)
    out = lay(out, tick * 0.8, np.broadcast_to(YELLOW, (H, W, 3)), grain2)
    out = lay(out, leaf_cov * 0.8, np.broadcast_to(WHITE, (H, W, 3)), grain2)
    # fingertip smudge of the lines (dust), then the lines themselves
    L1 = np.maximum(stroke_h, stroke_t) * bm
    dust = NL.warp(NL.blur(L1, 3.5 * s), -2.0 * s * np.ones(sh, np.float32), -2.5 * s * np.ones(sh, np.float32)) * 0.35
    out = lay(out, dust, col_lines, np.ones(sh, np.float32) * 0.8)
    out = lay(out, L1 * 0.95, col_lines, grain2 * 1.05)
    # --- slim wooden frame with a hint of grain, and the board's vignette
    fr = int(13 * s)
    frame_m = np.zeros(sh, np.float32); frame_m[:fr] = frame_m[-fr:] = 1; frame_m[:, :fr] = frame_m[:, -fr:] = 1
    wood = WOOD[None, None, :] * (1 + 0.25 * NL.noise(sh, 2.0 * s, 101, aniso=(0.3, 6.0)))[..., None]
    shade_in = np.zeros(sh, np.float32); shade_in[fr:fr + 4, fr:W - fr] = 0.5; shade_in[fr:H - fr, fr:fr + 4] = 0.5
    out = out * (1 - shade_in[..., None] * 0.5)
    out = out * (1 - frame_m[..., None]) + wood * frame_m[..., None]
    out = out * NL.vignette(sh, 0.28)[..., None]
    return np.clip(out, 0, 1).astype(np.float32)


def apply(bpy, film, ctx):
    NL.setup(bpy, film, ctx, stylize)
    NL.recolor_overlay(film, (0.085, 0.12, 0.11), (0.94, 0.94, 0.89), font=FONT)


def frame(bpy, film, ctx, t, shot):
    NL.frame(bpy, film, ctx, t, shot)
