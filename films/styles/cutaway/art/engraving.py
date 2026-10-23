"""engraving: a 19th-century encyclopaedia plate of the cutaway (history).

Sepia copperplate line work on cream paper: no flat colour at all, every tone is made of parallel lines whose width follows
the tone (hairlines in the light, nearly solid in the dark), cross-hatched in the deep shadows, as a burin would cut them.
The lines follow the forms: on the cut faces they run along the soil layers themselves (an AOV of the strata material gives the
layer coordinate, so the hatching bends with every fold), on the ground they ride the relief, on the foliage they wrap round
each clump, on water and walls they run level. A thin double plate border with a faint plate mark sits round the picture.
Labels become ink on paper plates, like captions.

What it changes: it adds one AOV output ('sd', the strata coordinate) to the cw_strata material; everything else is a numpy
stylization of the Cycles passes (_npr_lines.py). Render cost: the reference's Cycles render plus about 6 s of numpy and
about 1 s for the label pass.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _npr_lines as NL  # noqa: E402

PAPER = np.array([0.935, 0.885, 0.760], np.float32)
INK = np.array([0.20, 0.115, 0.065], np.float32)


def stylize(P, info):
    img, alb, nrm, pos, dep, ob = P['img'], P['alb'], P['nrm'], P['pos'], P['dep'], P['ob']
    sd = P.get('sd')
    H, W = dep.shape; sh = (H, W); s = NL.px_scale(W)
    ma, sky = NL.region_ids(P)
    cut = NL.cls_mask(ma, 'strata'); bottom = NL.cls_mask(ma, 'bottom'); grass = NL.cls_mask(ma, 'grass'); leaf = NL.cls_mask(ma, 'leaf')
    water = NL.cls_mask(ma, 'water'); floor = NL.cls_mask(ma, 'floor'); top = NL.cls_mask(ma, 'top'); bark = NL.cls_mask(ma, 'bark')
    build = NL.cls_mask(ma, 'build')
    lw = float(np.clip(2.6 / max(np.median(dep[~sky & ~floor]), 0.3), 0.8, 2.0))
    gm = NL.blur(grass.astype(np.float32), 3.0 * s); gmask = gm > 0.40
    # --- line density follows the picture scale: about 5 px between lines whatever the camera distance (quantized so it does not crawl)
    zc = cut | bottom
    gzy, gzx = NL.grad(NL.blur(pos[..., 2], 1.0))
    gz = np.sqrt(gzx * gzx + gzy * gzy)[zc]
    pxm = 1.0 / max(float(np.median(gz[gz > 1e-5])) if (gz > 1e-5).any() else 1 / 390.0, 1e-4)
    kf = float(2 ** (np.round(np.log2(np.clip(pxm / 390.0, 0.35, 1.6)) * 3) / 3))
    # --- tone: how dark each place must be drawn. The material's own darkness (layers, leaves, bark) carries most of it,
    # the light adds cast shadows and the glow round a find, as an engraver would add them to a drawing
    Lr = NL.lum(img) / np.maximum(NL.lum(alb), 0.05)
    rel = NL.blur(np.clip(Lr, 0, 3), 2.0 * s) / (NL.blur(np.clip(Lr, 0, 3), 40 * s) + 0.05)
    Alum = NL.lum(NL.lin_to_srgb(NL.blur(alb, 1.2 * s)))
    shadow = NL.smoothstep(0.9, 0.35, rel); glow = NL.smoothstep(1.1, 2.2, rel)
    pal = info.get('strata') if isinstance(info, dict) else None
    palc = np.asarray(pal if pal is not None else NL.STRATA_TIME, np.float32)
    layerD = np.clip((1.0 - NL.lum(palc)) * 1.5 - 0.02, 0.22, 1.0)
    lab = NL.strata_labels(alb, pal, 3.0 * s, 4.0 * s)
    Dl = NL.blur(layerD[lab], 1.5 * s)
    D = np.clip(((1.0 - Alum) - 0.16) * 1.55 + 0.35 * shadow - 0.25 * glow, 0, 1)
    D = np.where(cut, np.clip(0.65 * Dl + 0.35 * D, 0, 1), D)
    vv = NL.lum(NL.lin_to_srgb(np.clip(img / (1 + img) * 1.6, 0, 1)))
    D = np.where(water, np.clip(0.30 + 0.5 * (0.6 - NL.blur(vv, 2 * s)), 0.15, 0.7), D)
    D = np.where(leaf, np.clip(0.30 + 0.45 * shadow + 0.35 * (1 - np.clip(NL.blur(nrm[..., 2], 2 * s) * 0.5 + 0.6, 0, 1)), 0, 1), D)
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    cl = NL.smoothstep(0.3, 1.3, NL.fbm(sh, 80 * s, 31, 3) + 0.2)
    Dsky = np.clip((0.06 + 0.36 * (1 - yy / 0.62).clip(0, 1) ** 1.6) * (1 - 0.8 * cl), 0, 1)
    fl = NL.blur(NL.lum(img), 6 * s); fref = np.percentile(fl[floor], 85) + 1e-6 if floor.any() else 1.0
    Dfloor = np.clip(NL.smoothstep(0.05, 0.8, 1 - fl / fref) * 0.8 + 0.05, 0, 1)
    D = np.where(sky, Dsky, np.where(floor, Dfloor, D))
    D = np.where(gmask & ~leaf, np.maximum(D, 0.45), D)
    D = NL.blur(D, 0.9 * s)
    # --- line fields, per kind of surface (world locked)
    along = pos[..., 0] + pos[..., 1]; z = pos[..., 2]
    sdv = sd if sd is not None else z * -1.0
    cut_f = (cut | bottom)
    u1 = np.where(cut_f, sdv, np.where(top | gmask, pos[..., 1] + 0.35 * pos[..., 0],
                np.where(leaf, nrm[..., 2] * 0.9 + nrm[..., 0] * 0.35,
                np.where(bark, along, np.where(water | build, z, np.where(floor, pos[..., 0] - pos[..., 1], z - along * 0.7))))))
    f1 = kf * np.where(cut_f, 78.0, np.where(top | gmask, 80.0, np.where(leaf, 7.0 / kf, np.where(bark, 140.0, np.where(floor, 22.0, 110.0)))))
    u1 = np.where(sky, np.mgrid[0:H, 0:W][0].astype(np.float32) / (6.0 * s), u1); f1 = np.where(sky, 1.0, f1)
    f1 = f1.astype(np.float32)
    u2 = np.where(cut_f, sdv * 0.8 - along * 0.55, np.where(leaf, nrm[..., 1] * 0.9 - nrm[..., 0] * 0.3, np.where(top | gmask, pos[..., 0] - 0.4 * pos[..., 1], z + along * 0.8)))
    f2 = (kf * np.where(cut_f, 70.0, np.where(leaf, 7.0 / kf, 90.0))).astype(np.float32)
    u3 = z - along * 0.8; f3 = np.full(sh, 120.0 * kf, np.float32)
    # hatch(u*f): the helper takes a per-unit scalar, so fold the per-pixel frequency into u
    p1 = NL.tone_hatch(u1 * f1, 1.0, D, thresh=0.09, min_px=3.4 * s)
    p2 = NL.tone_hatch(u2 * f2, 1.0, np.clip((D - 0.34) / 0.5, 0, 1), thresh=0.04, min_px=3.4 * s)
    p3 = NL.tone_hatch(u3 * f3, 1.0, np.clip((D - 0.72) / 0.28, 0, 1), thresh=0.04, min_px=3.4 * s)
    tone = np.maximum(p1, np.maximum(p2 * 0.95, p3 * 0.9))
    # sky: engraved sky is only a few level lines; keep it light
    tone = np.where(sky, p1 * 0.85, tone)
    # grass: short upright strokes
    tick = NL.smoothstep(1.2, 1.7, NL.noise(sh, 1.7 * s, 11, aniso=(4.0, 0.5))) * gmask * 0.8
    tone = np.maximum(tone, tick)
    # --- outlines: precise, thin, a little heavier on silhouettes
    E = NL.edge_maps(P, s)
    keyc = np.where(grass | gmask, 4, np.where(sky | floor, 0, ma)).astype(np.float32)
    obk = np.where(grass | gmask | sky | floor, 0, np.rint(ob)).astype(np.float32)
    key = keyc * 8192 + obk
    sil = np.zeros(sh, np.float32)
    for ax in (0, 1):
        sil = np.maximum(sil, (np.abs(key - np.roll(key, 1, ax)) > 0).astype(np.float32))
    far = NL.blur((grass | floor).astype(np.float32), 4 * s) > 0.02
    crease = NL.smoothstep(0.35, 0.70, E['crease']) * (~far) * (~leaf)
    dep_e = NL.smoothstep(0.20, 0.55, E['depth']) * (~far)
    dx = NL.fbm(sh, 30 * s, 41, 2) * 0.7 * s; dy = NL.fbm(sh, 30 * s, 42, 2) * 0.7 * s
    lh = NL.blur(NL.warp(np.maximum(sil, dep_e * 0.9), dx, dy), 0.7 * s * lw); lt = NL.blur(NL.warp(crease, dx, dy), 0.55 * s * lw)
    line = np.maximum(NL.smoothstep(0.15, 0.28, lh), NL.smoothstep(0.14, 0.27, lt) * 0.6)
    # --- ink on paper
    pap = NL.paper(sh, PAPER, 7, s, fibre=0.025, mottle=0.03, grain=0.012)
    fox = NL.smoothstep(1.5, 2.6, NL.fbm(sh, 22 * s, 9, 3)) * 0.10
    pap = pap * (1 - fox[..., None] * np.array([0.25, 0.45, 0.8], np.float32)[None, None, :])
    ink_a = np.clip(np.maximum(tone * 0.93, line * 0.97), 0, 1)
    ink_a = ink_a * (0.88 + 0.12 * NL.noise(sh, 1.0 * s, 51).clip(-1, 1)) * (0.93 + 0.07 * NL.noise(sh, 30 * s, 52))
    out = pap + (INK[None, None, :] - pap) * ink_a[..., None]
    # --- the plate: a double rule, a faint plate mark, blank paper outside; the picture is cut at the plate edge
    m = int(34 * s)
    inside = np.zeros(sh, bool); inside[m:H - m, m:W - m] = True
    out = np.where(inside[..., None], out, pap)
    rule = np.zeros(sh, np.float32)
    w1 = max(2, int(2.4 * s)); w2 = max(1, int(1.2 * s)); g = int(7 * s)
    def box(m_, w):
        rule[m_ - w:m_, m_ - w:W - m_ + w] = 1; rule[H - m_:H - m_ + w, m_ - w:W - m_ + w] = 1
        rule[m_ - w:H - m_ + w, m_ - w:m_] = 1; rule[m_ - w:H - m_ + w, W - m_:W - m_ + w] = 1
    box(m, w1); box(m + g + w1, w2)
    rule[m + g + w1:m + g + w1 + w2, m + g + w1:W - m - g - w1] = 1; rule[H - m - g - w1 - w2:H - m - g - w1, m + g + w1:W - m - g - w1] = 1
    rule[m + g + w1:H - m - g - w1, m + g + w1:m + g + w1 + w2] = 1; rule[m + g + w1:H - m - g - w1, W - m - g - w1 - w2:W - m - g - w1] = 1
    # inner thin rule cuts the picture: nothing is drawn between the two rules except paper
    ring = np.zeros(sh, bool); gi = m + g + w1 + w2
    ring[:] = True; ring[gi:H - gi, gi:W - gi] = False; ring &= inside
    out = np.where(ring[..., None], pap, out)
    mark = NL.blur(np.pad(np.zeros((H - 2 * (m - 6), W - 2 * (m - 6)), np.float32) + 1, m - 6), 2.5 * s)
    out = out * (1 - 0.06 * np.clip(NL.blur(rule, 3 * s) * 2, 0, 1))[..., None]
    out = out + (INK[None, None, :] - out) * (rule * 0.95)[..., None]
    out = out * NL.vignette(sh, 0.16)[..., None]
    return np.clip(out, 0, 1).astype(np.float32)


def apply(bpy, film, ctx):
    nt = bpy.data.materials['cw_strata'].node_tree
    att = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeAttribute' and n.attribute_name == 'sd'][0]
    aov = nt.nodes.new('ShaderNodeOutputAOV'); aov.aov_name = 'sd'; nt.links.new(att.outputs['Fac'], aov.inputs['Value'])
    NL.setup(bpy, film, ctx, stylize, aovs=['sd'])
    NL.recolor_overlay(film, (0.97, 0.93, 0.82), (0.20, 0.115, 0.065))


def frame(bpy, film, ctx, t, shot):
    NL.frame(bpy, film, ctx, t, shot)
