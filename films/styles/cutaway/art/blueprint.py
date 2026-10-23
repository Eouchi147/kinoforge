"""blueprint: an engineering drawing of the cutaway (technology and how-it-works explainers).

The block is drawn as a cyanotype sheet: deep blueprint blue, a faint drafting grid, fine pale-cyan and white lines for every
silhouette and edge, flat fills with no photographic shading, and each soil layer of the cut faces hatched with its own
drawing symbol (diagonals, dots, cross-hatch, masonry, rock) locked to the world so it holds still when the camera moves.
A sheet border with zone ticks, a depth ruler along the left margin (a tick every 0.1 m of the block), dimension lines when
the block corners are in frame, and a "SECTION A-A" tag are set in code. Labels become pale-cyan type on blue plates.

What it changes: the whole picture is a numpy stylization of the Cycles passes (see _npr_lines.py): no new materials, the
light is only used to find the glass and the shadows (ignored). Render cost: the reference's Cycles render (same samples)
plus about 4 s of numpy and about 1 s for the label pass. The look needs no extra memory beyond a 1280x720 float stack.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _npr_lines as NL  # noqa: E402

BG = np.array([0.050, 0.190, 0.400], np.float32)
FILL_TOP = np.array([0.070, 0.235, 0.470], np.float32)
FILL_CUT = np.array([0.060, 0.210, 0.435], np.float32)
FILL_OBJ = np.array([0.100, 0.300, 0.540], np.float32)
LINE = np.array([0.84, 0.96, 1.00], np.float32)
FAINT = np.array([0.52, 0.78, 0.94], np.float32)
FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))), 'ads', 'fonts', 'JetBrainsMono.ttf')


def _segment(shape, p0, p1, width, soft=0.8):
    """Antialiased line segment (pixel coordinates x,y, origin top-left) as coverage 0..1, drawn only near its bounding box."""
    H, W = shape; out = np.zeros(shape, np.float32)
    x0, y0 = p0; x1, y1 = p1; pad = width + 3
    bx0 = int(max(0, min(x0, x1) - pad)); bx1 = int(min(W, max(x0, x1) + pad + 1)); by0 = int(max(0, min(y0, y1) - pad)); by1 = int(min(H, max(y0, y1) + pad + 1))
    if bx1 <= bx0 or by1 <= by0: return out
    yy, xx = np.mgrid[by0:by1, bx0:bx1].astype(np.float32)
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1); d = np.sqrt((xx - (x0 + t * dx)) ** 2 + (yy - (y0 + t * dy)) ** 2)
    out[by0:by1, bx0:bx1] = np.clip((width * 0.5 - d) / soft + 0.5, 0, 1)
    return out


def _dim_lines(shape, pts, s):
    """Dimension lines for the block when its corners are on screen: vertical (depth) on the left of the cut face,
    horizontal (width) under it, with extension lines and 45 degree ticks like a drawing."""
    out = np.zeros(shape, np.float32)
    if not pts: return out
    tl, bl, br, tl_o, bl_o, br_o = pts
    for a, b in ((tl, tl_o), (bl, bl_o), (tl_o, bl_o)):
        if a is None or b is None: continue
        out = np.maximum(out, _segment(shape, a, b, 1.1 * s))
    for p in (tl_o, bl_o):
        if p is None: continue
        out = np.maximum(out, _segment(shape, (p[0] - 7 * s, p[1] + 7 * s), (p[0] + 7 * s, p[1] - 7 * s), 1.6 * s))
    return out


def _ruler(shape, pos, wall, s):
    """A depth ruler along the left margin: a tick for every 0.1 of world height where the picture shows a wall there."""
    H, W = shape; out = np.zeros(shape, np.float32)
    col = int(min(W - 1, 60 * s))
    z = pos[:, col, 2]; ok = wall[:, col]
    if ok.sum() < 20: return out
    v = z * 10.0
    for y in range(1, H - 1):
        if not (ok[y] and ok[y - 1]): continue
        a, b = np.floor(v[y]), np.floor(v[y - 1])
        if a != b:
            major = (int(max(a, b)) % 5 == 0)
            ln = (22 if major else 11) * s
            out[max(0, y - 1):y + 1, int(8 * s):int(8 * s + ln)] = 1.0
    return out


def stylize(P, info):
    img, alb, nrm, pos, dep, ob = P['img'], P['alb'], P['nrm'], P['pos'], P['dep'], P['ob']
    H, W = dep.shape; sh = (H, W); s = NL.px_scale(W)
    ma, sky = NL.region_ids(P)
    cut = NL.cls_mask(ma, 'strata'); bottom = NL.cls_mask(ma, 'bottom'); grass = NL.cls_mask(ma, 'grass'); leaf = NL.cls_mask(ma, 'leaf')
    water = NL.cls_mask(ma, 'water'); floor = NL.cls_mask(ma, 'floor'); top = NL.cls_mask(ma, 'top')
    obj = NL.cls_mask(ma, 'find', 'animal', 'build', 'bark', 'rock', 'plant', 'fly')
    lw = float(np.clip(2.6 / max(np.median(dep[~sky & ~floor]), 0.3), 0.8, 2.0))
    # --- smooth the grass mask (blades -> one rounded ground band)
    gm = NL.blur(grass.astype(np.float32), 3.0 * s); gmask = gm > 0.40
    # --- flat fills, no shading at all
    fill = np.zeros((H, W, 3), np.float32) + BG
    fill = np.where((top | gmask)[..., None], FILL_TOP, fill)
    fill = np.where((cut | bottom)[..., None], FILL_CUT, fill)
    fill = np.where((obj | leaf)[..., None], FILL_OBJ, fill)
    fill = np.where(water[..., None], FILL_CUT * 0.9, fill)
    fill = np.where((sky | floor)[..., None], BG, fill)
    # --- drafting grid on the sheet (shows in the sky and on the floor, a ghost of it everywhere else)
    gx = np.arange(W)[None, :]; gy = np.arange(H)[:, None]
    mi = 16 * s; ma_ = 96 * s
    minor = (((gx % mi) < 1.0) | ((gy % mi) < 1.0)).astype(np.float32)
    major = (((gx % ma_) < 1.5) | ((gy % ma_) < 1.5)).astype(np.float32)
    grid = np.maximum(minor * 0.10, major * 0.20)
    gridw = np.where((sky | floor), 1.0, 0.35).astype(np.float32)
    # --- edges
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
    # soil layers: labels from the albedo, boundaries drawn as dashed lines, each layer hatched with its own symbol
    pal = info.get('strata') if isinstance(info, dict) else None
    lab = NL.strata_labels(alb, pal, 3.0 * s, 4.0 * s)
    lab_e = NL.label_edges(lab, cut) * NL.blur_edge((cut).astype(np.float32), 2.0) .clip(0, 1)
    along = pos[..., 0] + pos[..., 1]; z = pos[..., 2]
    dashm = (np.mod(along * 24.0, 1.0) < 0.62).astype(np.float32)
    layer_line = lab_e * dashm
    thin = np.maximum(crease * 0.9, layer_line * 0.8)
    heavy = np.maximum(sil, dep_e * 0.9)
    bm = np.ones(sh, np.float32); b = int(30 * s); bm[:b] = bm[-b:] = 0; bm[:, :b] = bm[:, -b:] = 0
    lh = NL.blur(heavy, 0.75 * s * lw); lt = NL.blur(thin, 0.6 * s * lw)
    line_h = NL.smoothstep(0.15, 0.30, lh); line_t = NL.smoothstep(0.13, 0.28, lt) * 0.75
    # --- hatching on the cut faces: one symbol per layer
    f = 36.0; w = 1.0 * s
    d1 = NL.hatch(z - along * 0.9, f, w, min_px=3.5 * s)            # "/"
    d2 = NL.hatch(z + along * 0.9, f, w, min_px=3.5 * s)            # "\"
    hz = NL.hatch(z, f * 1.1, w, min_px=3.5 * s)                     # horizontal
    dots = NL.hatch(along, f * 0.9, 1.9 * s, min_px=5.5 * s) * NL.hatch(z, f * 0.9, 1.9 * s, min_px=5.5 * s)
    row = np.floor(z * f * 0.8)
    mason = np.maximum(NL.hatch(z, f * 0.8, w, min_px=3.5 * s), NL.hatch(along + 0.5 * np.mod(row, 2) / (f * 0.8), f * 0.55, w, min_px=3.5 * s) * (np.mod(z * f * 0.8, 1.0) < 0.85))
    sym = [d1, dots, hz, d2, dots * 0.9 + 0.0, np.maximum(d1, d2), mason, np.maximum(d1 * 0.9, np.maximum(d2 * 0.9, hz * 0.0))]
    hat = np.zeros(sh, np.float32)
    for k in range(len(sym)):
        hat = np.where(lab == k, sym[k], hat)
    hat = hat * cut * (NL.blur(lab_e, 2.0) < 0.02)
    # bottom face and water: simple horizontal water lines
    wat_h = NL.hatch(z, 55.0, 0.9 * s, min_px=3.5 * s) * water
    # --- ground / grass ticks and foliage contour lines
    tick = NL.smoothstep(1.45, 1.8, NL.noise(sh, 1.8 * s, 11, aniso=(4.0, 0.5))) * gmask
    foliage = NL.hatch(z * 1.0 + nrm[..., 2] * 0.05, 70.0, 0.8 * s, min_px=4 * s) * leaf * 0.55
    obj_hat = NL.hatch(z - along * 0.8, 90.0, 0.8 * s, min_px=4 * s) * (obj & ~leaf) * 0.25
    # --- compose
    out = fill + (LINE - fill) * grid[..., None] * gridw[..., None] * 0.55
    sub = np.clip(hat * 0.55 + wat_h * 0.5 + tick * 0.5 + foliage + obj_hat, 0, 1)
    out = out + (FAINT[None, None, :] - out) * sub[..., None]
    L1 = np.maximum(line_h, line_t) * bm
    glow = NL.blur(L1, 2.2 * s) * 0.35
    out = out + (FAINT[None, None, :] - out) * np.clip(glow, 0, 1)[..., None] * 0.6
    out = out + (LINE[None, None, :] - out) * (L1 * 0.95)[..., None]
    # --- the sheet: border, zone ticks, ruler, dimension lines, a little cyanotype mottling
    sheet = np.zeros(sh, np.float32)
    m0 = int(14 * s); m1 = int(20 * s)
    sheet[m0:m0 + 2, m0:W - m0] = 1; sheet[H - m0 - 2:H - m0, m0:W - m0] = 1; sheet[m0:H - m0, m0:m0 + 2] = 1; sheet[m0:H - m0, W - m0 - 2:W - m0] = 1
    sheet[m1:m1 + 1, m1:W - m1] = 0.5; sheet[H - m1 - 1:H - m1, m1:W - m1] = 0.5; sheet[m1:H - m1, m1:m1 + 1] = 0.5; sheet[m1:H - m1, W - m1 - 1:W - m1] = 0.5
    for k in range(1, 8):          # zone ticks on the top and bottom
        x = int(W * k / 8); sheet[m0:m1 + 6, x:x + 1] = 1; sheet[H - m1 - 6:H - m0, x:x + 1] = 1
    for k in range(1, 5):
        y = int(H * k / 5); sheet[y:y + 1, m0:m1 + 6] = 1; sheet[y:y + 1, W - m1 - 6:W - m0] = 1
    ruler = _ruler(sh, pos, cut | bottom, s)
    out = out * (1 - sheet[..., None] * 0.9) + LINE[None, None, :] * (sheet * 0.9)[..., None]
    out = out * (1 - ruler[..., None] * 0.8) + FAINT[None, None, :] * (ruler * 0.8)[..., None]
    dims = info.get('dims') if isinstance(info, dict) else None
    if dims is not None and np.size(dims) > 0:
        pts = [None if np.isnan(p[0]) else (float(p[0]), float(p[1])) for p in np.asarray(dims).reshape(-1, 2)]
        dl = _dim_lines(sh, pts, s)
        out = out * (1 - dl[..., None] * 0.9) + LINE[None, None, :] * (dl * 0.9)[..., None]
    out = out * (1.0 + 0.02 * NL.fbm(sh, 80 * s, 5, 3) + 0.012 * NL.noise(sh, 0.8 * s, 6))[..., None]
    out = out * NL.vignette(sh, 0.22)[..., None]
    return np.clip(out, 0, 1).astype(np.float32)


def _dims(bpy, film, ctx, t, shot):
    """Screen positions of the block's dimension anchors (NaN when behind the camera)."""
    if not hasattr(film.O, 'project'): return {}
    try:
        st = next(iter(film.built.values())); land = st['land']; sx, sy = land.size; dp = land.depth
    except Exception:
        return {}
    off = 0.22
    pts = [(-sx / 2, -sy / 2, 0.0), (-sx / 2, -sy / 2, -dp), (sx / 2, -sy / 2, -dp),
           (-sx / 2 - off, -sy / 2, 0.0), (-sx / 2 - off, -sy / 2, -dp), (sx / 2, -sy / 2 - off, -dp - off)]
    q = NL.project_points(film, pts)
    return {'dims': np.array([[np.nan, np.nan] if p is None else p for p in q], np.float32)}


def apply(bpy, film, ctx):
    NL.setup(bpy, film, ctx, stylize)
    film.bp_tag = None
    if hasattr(film.O, 'text') and hasattr(film, 'r'):       # the line engine's overlay; a kit scene (adapter) has no text maker
        film.bp_tag = film.O.text('bp_section', 'SECTION A-A', 21 * film.r, (0.07, 0.09, 0.12), 'LEFT', 1.25, bold=0.3)
    NL.recolor_overlay(film, (0.045, 0.16, 0.34), (0.84, 0.96, 1.0), font=FONT)


def frame(bpy, film, ctx, t, shot):
    if getattr(film, 'bp_tag', None) is not None:
        r = film.r; film.bp_tag.set_alpha(0.95); film.bp_tag.place_text(-ctx['W'] / 2 + 46 * r, -ctx['H'] / 2 + 50 * r)
    NL.frame(bpy, film, ctx, t, shot, extra=_dims)
