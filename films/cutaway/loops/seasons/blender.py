"""Social loop: four seasons over one block (Cutaway style). 12 s, 9:16, 24 fps, 288 frames, a seamless loop.

Story (each change has a reason we can see):
  0 to 3 s   spring: the thaw ends, blossom on the trees, fresh grass and flowers, the frog swims up from its burrow,
             birds circle, roots grow a little in the cut face.
  3 to 6 s   summer: full green, the pond warm and bright (caustics), dragonflies over the water, the frog at the surface.
  6 to 9 s   autumn: leaves turn and fall, land on the pond and sink past the glass of the cut face; the frog dives
             and digs into the mud; the birds leave.
  9 to 12 s  winter: snow falls and settles, the pond freezes from the banks (ice in the cut face), the frog sleeps in
             its chamber in the mud (the surprise); then the thaw: snow and ice melt, the ground is wet, birds return.
Camera: a fixed high three-quarter view with a very slow sway (3 degrees of azimuth on a 12 s sine), so it returns
to its start. Seamless loop: the year itself closes (spring on both sides of the seam), every motion repeats on 12 s.
Check: render frames 287 and 0 and compare.
Life and light (szlife.py): haze with god rays, spring mist, autumn ground fog; a duck, fish behind the glass, a squirrel
burying acorns, a robin leaving tracks in the snow; easter eggs in the cut faces (an ammonite, a gold vein, the acorn
cache); the title "One pond. One year." set in code.
Art directions (opt-in): $KF_ART=<name> (or KF_ART_NAME set by a look-board folder, films/cutaway/looks/seasons-<name>/)
dresses the finished scene with films/styles/cutaway/art/<name>.py through art/_adapter.py; without it, unchanged.
Files: szworld.py (land, pond, timeline), szmats.py (season-driven materials), szlife.py, this file (build and frame),
audio/make_audio.py (ambience and the loopable score -> audio/mix.m4a). Kit: films/styles/cutaway/cutaway.py (imported).
"""
import os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
for p in (os.path.join(ROOT, 'films', 'styles', 'cutaway'), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import szworld as W  # noqa: E402
import szmats as M  # noqa: E402
import szlife as LF  # noqa: E402

DURATION = W.LOOP
SETTINGS = {'samples': 40, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.2, 'max_bounces': 8, 'volume_bounces': 0, 'clamp_indirect': 6.0, 'adaptive_min_samples': 16,
            'denoising_prefilter': 'ACCURATE'}

AZ0, SWAY = -48.0, 3.0                 # camera azimuth and its slow sway (degrees, one 12 s sine)
EL, LENS, WIDTH, TZ = 30.0, 55.0, 0.85, 0.32   # block spans WIDTH of the frame; aim TZ m above the top so it sits low
SUN_AZ = -120.0                        # key light from the left, so shafts of light cross the view
STRATA = [('topsoil', 0.07, (0.20, 0.14, 0.09), 0.03), ('mud', 0.15, (0.31, 0.24, 0.17), 0.04), ('sand', 0.13, (0.79, 0.67, 0.49), 0.10),
          ('clay', 0.17, (0.65, 0.61, 0.55), 0.02), ('loam', 0.26, (0.48, 0.33, 0.21), 0.25), ('gravel', 0.12, (0.58, 0.51, 0.43), 0.85),
          ('deep', 1.0, (0.33, 0.25, 0.19), 0.30)]
SEASON = {   # (spring, summer, autumn, winter), sRGB
    'ground':  ((0.27, 0.40, 0.13), (0.22, 0.33, 0.11), (0.33, 0.29, 0.13), (0.38, 0.35, 0.27)),
    'ground2': ((0.30, 0.48, 0.15), (0.24, 0.43, 0.11), (0.34, 0.33, 0.14), (0.42, 0.40, 0.31)),
    'gtip':    ((0.74, 0.84, 0.38), (0.66, 0.80, 0.30), (0.74, 0.62, 0.30), (0.72, 0.68, 0.56)),
    'bedA':    ((0.84, 0.78, 0.62), (0.86, 0.80, 0.62), (0.66, 0.56, 0.40), (0.72, 0.72, 0.68)),
    'bedB':    ((0.64, 0.60, 0.48), (0.66, 0.62, 0.48), (0.48, 0.40, 0.28), (0.54, 0.54, 0.52)),
    'wtint':   ((0.18, 0.78, 0.76), (0.28, 0.82, 0.60), (0.58, 0.60, 0.30), (0.30, 0.62, 0.84)),
    'wdens':   (3.0, 3.3, 4.4, 2.6),
    'bg':      ((0.89, 0.93, 0.88), (0.95, 0.92, 0.83), (0.95, 0.87, 0.77), (0.86, 0.90, 0.95)),
    'sun_col': ((1.00, 0.95, 0.88), (1.00, 0.86, 0.64), (1.00, 0.72, 0.46), (0.84, 0.90, 1.00)),   # morning, golden, low amber, pale
    'sun_e':   (3.0, 3.9, 3.1, 2.3),
    'sun_el':  (30.0, 46.0, 22.0, 17.0),
    'sun_ang': (12.0, 3.5, 6.0, 10.0),
    'haze':    (0.045, 0.070, 0.060, 0.035),
    'hazecol': ((0.98, 0.98, 0.96), (1.0, 0.92, 0.80), (1.0, 0.88, 0.76), (0.88, 0.92, 1.0)),
    'fill':    (0.90, 0.85, 0.85, 1.05),
    'fill_col': ((1.0, 1.0, 1.0), (1.0, 0.98, 0.95), (1.0, 0.95, 0.90), (0.88, 0.92, 1.0)),
    'reedtint': ((1.0, 1.0, 1.0), (0.95, 1.0, 0.9), (1.5, 1.0, 0.55), (1.35, 1.25, 1.0)),
}
GRASS = [((0.38, 0.62, 0.20), (0.72, 0.82, 0.36), (0.38, 0.62, 0.20), (0.50, 0.60, 0.24), (0.30, 0.50, 0.16)),
         ((0.30, 0.56, 0.15), (0.66, 0.80, 0.30), (0.30, 0.56, 0.15), (0.55, 0.55, 0.22), (0.24, 0.45, 0.12)),
         ((0.48, 0.46, 0.18), (0.70, 0.62, 0.30), (0.56, 0.44, 0.18), (0.62, 0.48, 0.22), (0.40, 0.38, 0.16)),
         ((0.52, 0.50, 0.38), (0.70, 0.68, 0.56), (0.58, 0.54, 0.42), (0.62, 0.58, 0.46), (0.46, 0.44, 0.34))]
LEAF = [((0.42, 0.66, 0.22), (0.55, 0.74, 0.28), (0.48, 0.70, 0.25), (0.36, 0.60, 0.20), (0.62, 0.78, 0.32)),
        ((0.20, 0.42, 0.13), (0.28, 0.50, 0.15), (0.16, 0.34, 0.12), (0.36, 0.52, 0.18), (0.24, 0.46, 0.14)),
        ((0.82, 0.40, 0.10), (0.88, 0.62, 0.16), (0.64, 0.22, 0.08), (0.92, 0.74, 0.22), (0.72, 0.30, 0.10)),
        ((0.46, 0.33, 0.18), (0.52, 0.38, 0.20), (0.40, 0.28, 0.16), (0.56, 0.42, 0.24), (0.44, 0.30, 0.17))]
TREES = [(0.95, 1.00, 1.25, 'round'), (1.35, 0.50, 0.95, 'cone'), (0.50, 1.32, 1.00, 'cone'), (1.32, 1.30, 0.80, 'round'),
         (-1.10, 0.62, 1.10, 'tall'), (-1.32, 1.28, 0.90, 'cone'), (-0.42, 1.36, 0.85, 'round'), (0.88, 0.02, 1.00, 'round'),
         (1.32, -0.38, 0.90, 'tall'), (-0.92, -0.92, 1.00, 'tall'), (1.22, -1.08, 1.05, 'round'), (-1.30, -1.32, 0.70, 'cone'),
         (0.42, -0.30, 0.75, 'round'), (-1.25, -0.20, 0.80, 'round')]
DROPPERS = [(-0.92, -0.92), (1.22, -1.08)]          # the two trees beside the pond whose leaves fall onto it
BURROW_X = 0.30; FROG = 1.75; TREE_K = 1.45     # TREE_K: the kit's trees are small for a 3.2 m block

# ============================================================================== build helpers
def _set_attr(me, name, arr):
    a = me.attributes.get(name) or me.attributes.new(name, 'FLOAT', 'POINT'); a.data.foreach_set('value', np.asarray(arr, np.float32))

def reshape(bpy, L):
    """Rewrite the kit's top, walls and water box from szworld.field (one source of truth for heights, so the plants,
    leaves, frog and ice placed from it sit exactly on the mesh) and add the attributes the season materials read."""
    me = L.objects['top'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3).astype(float)
    F = W.field(co[:, 0], co[:, 1]); co[:, 2] = F['h']
    me.vertices.foreach_set('co', co.astype(np.float32).ravel())
    _set_attr(me, 'sdw', F['sd']); _set_attr(me, 'wg', F['wg']); _set_attr(me, 'ws', F['ws']); me.update()
    zmean = float(F['h'].mean()); zb = -W.DEPTH
    me = L.objects['walls'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3).astype(float)
    key = np.round(co[:, 0] * 2e4).astype(np.int64) * 1000003 + np.round(co[:, 1] * 2e4).astype(np.int64)
    _, inv = np.unique(key, return_inverse=True); zt_old = np.full(inv.max() + 1, -1e9); np.maximum.at(zt_old, inv, co[:, 2])
    zo = zt_old[inv]; frac = np.where(np.abs(zb - zo) > 1e-6, (co[:, 2] - zo) / (zb - zo), 1.0)
    zt = W.field(co[:, 0], co[:, 1])['h']; z = zt + (zb - zt) * frac; co[:, 2] = z
    dt = zt - z; w = np.maximum(0.0, 1 - dt / 0.7); sd = dt * w + (zmean - z) * (1 - w)
    me.vertices.foreach_set('co', co.astype(np.float32).ravel()); _set_attr(me, 'sd', sd); _set_attr(me, 'dtop', dt); me.update()
    me = L.objects['water'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    lo = co[:, 2] < W.LV - 0.01; co[lo, 2] = float(F['h'].min()) - 0.05; me.vertices.foreach_set('co', co.ravel()); me.update()

def jitter_q(rng, step, margin=0.004):
    """Jittered grid over the whole top."""
    xs = np.arange(-W.H + step / 2, W.H - margin, step)
    X, Y = np.meshgrid(xs, xs); P = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.5, 0.5, (X.size, 2)) * step
    return P[(np.abs(P) < W.H - margin).all(1)]

def scatter4(kit, L, name, protos, P, yaw, scale, variant, z, **kw):
    pts = np.column_stack([P, z]); ob = L.scatter(name, protos, pts, yaw=np.asarray(yaw, float), scale=np.asarray(scale, float), variant=np.asarray(variant).astype(int), **kw)
    return ob, np.asarray(scale, float)

def populate(kit, L, D, rng):
    pal = dict(cw.SEASONS['summer']); pal['leaf_density'] = 1.0; out = {}
    # grass (season colour by material, height by the scale attribute)
    P = jitter_q(rng, 0.029); F = W.field(P[:, 0], P[:, 1])
    keep = (rng.uniform(0, 1, len(P)) < F['wg'] ** 0.7) & (F['depth'] < -0.006)
    for tx, ty, s, _ in TREES: keep &= np.hypot(P[:, 0] - tx, P[:, 1] - ty) > 0.05 * s * TREE_K
    P = P[keep]; F = W.field(P[:, 0], P[:, 1])
    mg = M.mat_grass(kit, D, 0.085)
    tufts = cw.proto_tufts(kit, pal, 7, 0.05, 7) + cw.proto_tufts(kit, pal, 3, 0.085, 8, (16, 26))
    for ob in tufts: ob.data.materials[0] = mg
    ob, sc = scatter4(kit, L, 'sz_grass', tufts, P, rng.uniform(0, 2 * math.pi, len(P)), rng.uniform(0.7, 1.3, len(P)),
                      rng.integers(0, len(tufts), len(P)), F['h'] - 0.004, sway=0.22, speed=0.9)
    out['grass'] = (ob, sc)
    # flowers: spring meadow (most), a few summer ones
    q = jitter_q(rng, 0.05, 0.03); Fq = W.field(q[:, 0], q[:, 1]); fz = 0.5 + 0.5 * W.fbm(q[:, 0], q[:, 1], 51, 2, 1.6)
    keep = (Fq['wg'] > 0.6) & (fz > 0.52) & (rng.uniform(0, 1, len(q)) < 0.55) & (Fq['sd'] > 0.06)
    q = q[keep]; Fq = W.field(q[:, 0], q[:, 1]); n = len(q)
    on = (11.85 + rng.uniform(0, 1.6, n)) % W.LOOP
    off = np.where(rng.uniform(0, 1, n) < 0.55, rng.uniform(3.0, 4.6, n), rng.uniform(5.6, 7.2, n))
    ob, sc = scatter4(kit, L, 'sz_flowers', cw.proto_flowers(kit, 4, 7), q, rng.uniform(0, 6.28, n), rng.uniform(0.8, 1.2, n),
                      rng.integers(0, 4, n), Fq['h'] - 0.004, sway=0.18, speed=0.9)
    out['flowers'] = (ob, sc, on, off)
    # trees: deciduous (round, tall, birch) and evergreens, each with its own size and variant
    leaf = M.mat_leaf(kit, D); ever = M.mat_leaf(kit, D, evergreen=True)
    bark = M.mat_bark(kit, D, (0.30, 0.21, 0.14), 'sz_bark'); birch = M.mat_bark(kit, D, (0.86, 0.84, 0.78), 'sz_birch')
    dec = cw.proto_trees(kit, pal, ('round', 'tall'), 3, 7); con = cw.proto_trees(kit, pal, ('cone',), 2, 9)
    for ob in dec:
        ob.data.materials[1] = leaf; ob.data.materials[0] = birch if ob.data.materials[0].name.startswith('cw_birch') else bark
    for ob in con: ob.data.materials[1] = ever; ob.data.materials[0] = bark
    td = [t for t in TREES if t[3] != 'cone']; tc = [t for t in TREES if t[3] == 'cone']
    Pd = np.array([(t[0], t[1]) for t in td]); Pc = np.array([(t[0], t[1]) for t in tc])
    hd = W.field(Pd[:, 0], Pd[:, 1])['h'] - 0.01; hc = W.field(Pc[:, 0], Pc[:, 1])['h'] - 0.01
    var = np.array([(0 if t[3] == 'round' else 3) + k % 3 for k, t in enumerate(td)])
    scatter4(kit, L, 'sz_trees', dec, Pd, rng.uniform(0, 6.28, len(td)), np.array([t[2] for t in td]) * TREE_K, var, hd, sway=0.025, speed=0.5)
    scatter4(kit, L, 'sz_pines', con, Pc, rng.uniform(0, 6.28, len(tc)), np.array([t[2] for t in tc]) * TREE_K, np.arange(len(tc)) % 2, hc, sway=0.02, speed=0.5)
    # boulders on the banks and in the grass
    rk = cw.proto_rocks(kit, 6, 7, moss=0.6); bed = cw.proto_rocks(kit, 4, 10, color=(0.55, 0.53, 0.48), moss=0.3, name='cw_pebble')
    M.patch_snow(rk[0].data.materials[0], D, kit)          # not the bed pebbles: they are under water
    B = np.array([(1.05, -0.62), (-1.38, -0.85), (-0.55, 0.30), (0.15, 0.62), (1.42, 0.05), (-0.62, -1.42)])
    Fb = W.field(B[:, 0], B[:, 1])
    scatter4(kit, L, 'sz_boulders', rk, B, rng.uniform(0, 6.28, len(B)), np.array([0.09, 0.07, 0.06, 0.05, 0.08, 0.05]), np.arange(len(B)) % 6, Fb['h'] - 0.02)
    q = jitter_q(rng, 0.085, 0.06); Fq = W.field(q[:, 0], q[:, 1]); keep = (np.abs(Fq['sd']) < 0.05) & (rng.uniform(0, 1, len(q)) < 0.4)
    q = q[keep]; Fq = W.field(q[:, 0], q[:, 1])
    scatter4(kit, L, 'sz_bankstones', rk, q, rng.uniform(0, 6.28, len(q)), rng.uniform(0.022, 0.05, len(q)), rng.integers(0, 6, len(q)), Fq['h'] - 0.012)
    q = jitter_q(rng, 0.05, 0.03); Fq = W.field(q[:, 0], q[:, 1]); keep = (Fq['depth'] > 0.06) & (rng.uniform(0, 1, len(q)) < 0.22)
    q = q[keep]; Fq = W.field(q[:, 0], q[:, 1])
    scatter4(kit, L, 'sz_bedstones', bed, q, rng.uniform(0, 6.28, len(q)), rng.uniform(0.012, 0.033, len(q)), rng.integers(0, 4, len(q)), Fq['h'] - 0.006)
    # underwater weed
    q = jitter_q(rng, 0.05, 0.03); Fq = W.field(q[:, 0], q[:, 1])
    keep = (Fq['depth'] > 0.08) & (0.5 + 0.5 * W.fbm(q[:, 0], q[:, 1], 61, 2, 1.8) > 0.55) & (rng.uniform(0, 1, len(q)) < 0.25)
    q = q[keep]; Fq = W.field(q[:, 0], q[:, 1]); wd = np.minimum(Fq['depth'] * 0.9, 0.22) / 0.14
    weed = cw.proto_weed(kit, 4, 7)
    scatter4(kit, L, 'sz_weed', weed, q, rng.uniform(0, 6.28, len(q)), wd * rng.uniform(0.6, 1.0, len(q)), rng.integers(0, 4, len(q)), Fq['h'] - 0.006, sway=0.12, speed=0.35)
    # reeds along the banks (green, then brown, then pale under snow)
    q = jitter_q(rng, 0.05, 0.05); Fq = W.field(q[:, 0], q[:, 1]); rz = 0.5 + 0.5 * W.fbm(q[:, 0], q[:, 1], 71, 2, 2.0)
    keep = (np.abs(Fq['sd'] + 0.01) < 0.045) & (rz > 0.62) & (rng.uniform(0, 1, len(q)) < 0.7)
    q = q[keep]; Fq = W.field(q[:, 0], q[:, 1])
    reeds = cw.proto_reeds(kit, 3, 7)
    for mname in ('cw_reed',):
        mt = kit.bpy.data.materials[mname]; M.patch_snow(mt, D, kit, up=0.3, tint='reedtint')
    scatter4(kit, L, 'sz_reeds', reeds, q, rng.uniform(0, 6.28, len(q)), rng.uniform(0.8, 1.2, len(q)), rng.integers(0, 3, len(q)), Fq['h'] - 0.004, sway=0.08, speed=0.7)
    # lily pads in the pool: grow in spring, gone before the ice
    lil = cw.proto_lily(kit, 4, 7)
    q = []
    for c in ((0.42, -1.05), (-0.12, -1.18), (0.66, -1.30)):
        for _ in range(9):
            p = np.array(c) + rng.normal(0, 0.06, 2)
            f = W.field(p[:1], p[1:])
            if f['depth'][0] > 0.05 and f['sd'][0] < -0.05 and all(np.hypot(*(p - o)) > 0.055 for o in q): q.append(p)
    q = np.array(q); n = len(q)
    ob, sc = scatter4(kit, L, 'sz_lilies', lil, q, rng.uniform(0, 6.28, n), rng.uniform(0.8, 1.3, n), rng.integers(0, 4, n), np.full(n, W.LV + 0.0008), sway=0.03, speed=0.3)
    out['lilies'] = (ob, sc, rng.uniform(0.0, 1.6, n))
    return out

def _ellipsoid(c, r, sub=2, seed=0, lump=0.0):
    V, Fc = cw._icosphere(sub)
    if lump: V = cw._lumpy(V, seed, lump, 3.0, 0.0, 1.0)
    return V * np.asarray(r) + np.asarray(c), Fc

def build_frogs(kit, L, D):
    """The frog and its chamber in the mud behind the front cut face, under the pond."""
    bpy = kit.bpy; fm = M.mat_frog(kit); eye = cw.mat_simple(kit, 'sz_eye', (0.03, 0.03, 0.03), 0.15)
    mud = cw.mat_simple(kit, 'sz_cavity', (0.17, 0.12, 0.08), 0.95, noise_amt=0.45, bump=0.5)
    bed = float(W.H_at(BURROW_X, -W.H + 0.003)); bz = bed - 0.17; rx, rz = 0.115, 0.075
    A = cw._Acc()
    for c, r, m in [((0, 0, 0), (0.036, 0.026, 0.019), 0), ((0.030, 0, 0.004), (0.020, 0.022, 0.015), 0),
                    ((0.036, 0.013, 0.016), (0.0072,) * 3, 1), ((0.036, -0.013, 0.016), (0.0072,) * 3, 1),
                    ((0.024, 0.020, -0.012), (0.012, 0.0048, 0.0048), 0), ((0.024, -0.020, -0.012), (0.012, 0.0048, 0.0048), 0)]:
        v, f = _ellipsoid(np.array(c) * FROG, np.array(r) * FROG, 2); A.add(v, f, m)
    frogs = []
    for k in range(1):
        root = bpy.data.objects.new(f'sz_frogroot{k}', None); kit.coll.objects.link(root); root.rotation_euler = (0, 0, k * math.pi / 2)
        body = A.build(bpy, f'sz_frog{k}', [fm, eye], True, kit.coll); body.parent = root
        legs = []
        for side in (-1, 1):
            v, f = _ellipsoid((-0.016 * FROG, 0, 0), (0.017 * FROG, 0.0068 * FROG, 0.0068 * FROG), 2)
            v2, f2 = _ellipsoid((-0.040 * FROG, 0, -0.002), (0.015 * FROG, 0.005 * FROG, 0.005 * FROG), 2)
            B = cw._Acc(); B.add(v, f); B.add(v2, f2); lg = B.build(bpy, f'sz_frogleg{k}{side}', [fm], True, kit.coll)
            lg.parent = body; lg.location = (-0.018 * FROG, side * 0.021 * FROG, -0.004 * FROG); legs.append((lg, side))
        # the chamber: a bowl behind the wall, larger than the hole, and a short tunnel up to the bed
        th = np.linspace(0, math.pi / 2, 9); ph = np.linspace(0, 2 * math.pi, 25)[:-1]; V = []; Fc = []
        for a in th:
            for b in ph:
                V.append((BURROW_X + rx * 1.2 * math.sin(a) * math.cos(b), -W.H + 0.0006 + 0.16 * math.cos(a), bz + rz * 1.25 * math.sin(a) * math.sin(b)))
        nph = len(ph)
        for i in range(len(th) - 1):
            for j in range(nph): Fc.append((i * nph + j, i * nph + (j + 1) % nph, (i + 1) * nph + (j + 1) % nph, (i + 1) * nph + j))
        o = len(V); w = 0.036; y0, y1 = -W.H + 0.0006, -W.H + 0.08; z0, z1 = bz, bed + 0.01
        V += [(BURROW_X - w, y0, z0), (BURROW_X - w, y1, z0), (BURROW_X - w, y1, z1), (BURROW_X - w, y0, z1),
              (BURROW_X + w, y0, z0), (BURROW_X + w, y1, z0), (BURROW_X + w, y1, z1), (BURROW_X + w, y0, z1)]
        Fc += [(o, o + 1, o + 2, o + 3), (o + 4, o + 7, o + 6, o + 5), (o + 1, o + 5, o + 6, o + 2)]
        cav = cw.mk_mesh(bpy, f'sz_cavity{k}', V, Fc, [mud], None, True, kit.coll); cav.parent = root
        frogs.append((body, legs))
    # a faint warm light in the chamber while it is open, so the sleeping frog reads in the cut face
    ld = bpy.data.lights.new('sz_den', 'POINT'); ld.energy = 0.0; ld.color = (1.0, 0.78, 0.52); ld.shadow_soft_size = 0.03
    den = bpy.data.objects.new('sz_den', ld); kit.coll.objects.link(den); den.location = (BURROW_X + 0.03, -W.H + 0.03, bz + 0.03)
    yb = -W.H + 0.07
    way = [(0.00, (BURROW_X, yb, bz + 0.035), 1.2, 1.0), (0.45, (BURROW_X, yb, bed + 0.014), 1.4, 0.8),
           (1.60, (0.26, -1.30, W.LV - 0.014), 1.6, 0.0), (3.40, (0.05, -1.08, W.LV - 0.012), 2.6, 0.0),
           (5.20, (0.48, -1.00, W.LV - 0.012), 0.5, 0.0), (6.50, (0.40, -1.28, W.LV - 0.016), -1.5, -0.6),
           (7.70, (BURROW_X, yb, bed + 0.016), -0.5, -0.9), (8.60, (BURROW_X, yb, bz), 0.0, -0.15), (11.60, (BURROW_X, yb, bz), 0.0, 0.0)]
    return {'frogs': frogs, 'way': way, 'burrow': (BURROW_X, bz, rx, rz, bed), 'den': ld}

def frog_pose(F, kit, t):
    way = F['way']; t = t % W.LOOP; ext = way + [(way[0][0] + W.LOOP,) + way[0][1:]]
    for a, b in zip(ext, ext[1:]):
        if a[0] <= t < b[0]: break
    u = (t - a[0]) / (b[0] - a[0]); e = u * u * (3 - 2 * u)
    pos = np.array(a[1]) + (np.array(b[1]) - np.array(a[1])) * e
    yaw = a[2] + (b[2] - a[2]) * e; pitch = a[3] + (b[3] - a[3]) * e
    moving = np.linalg.norm(np.array(b[1]) - np.array(a[1])) / (b[0] - a[0]) > 0.01
    sleep = 8.7 < t < 11.65
    kick = (0.55 + 0.45 * math.sin(kit.cycles(t, 2.0))) if moving else (0.25 + 0.1 * math.sin(kit.cycles(t, 0.5)))
    if sleep: kick = 0.0
    breathe = 1.0 + (0.03 * math.sin(kit.cycles(t, 0.5)) if sleep else 0.0)
    F['den'].energy = 0.35 * W.cv('burrow', t)
    for body, legs in F['frogs']:
        body.location = tuple(pos); body.rotation_euler = (0.0, -pitch, yaw); body.scale = (1.0, 1.0, breathe)
        for lg, side in legs:
            lg.rotation_euler = (0.0, 0.15 * kick, side * (0.35 - 0.5 * kick)); lg.scale = (0.75 + 0.55 * kick, 1.0, 1.0)

def build_ice(kit, D):
    bpy = kit.bpy; n = 101; e = 0.0009
    xs = np.linspace(-W.H + e, W.H - e, n); X, Y = np.meshgrid(xs, xs)
    V = np.column_stack([X.ravel(), Y.ravel(), np.full(X.size, W.LV + 0.004)]).tolist()
    ii = np.arange(n * n).reshape(n, n); Fc = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1).tolist()
    bottom = []
    edges = [np.column_stack([xs, np.full(n, -W.H + e)]), np.column_stack([np.full(n, W.H - e), xs]),
             np.column_stack([xs[::-1], np.full(n, W.H - e)]), np.column_stack([np.full(n, -W.H + e), xs[::-1]])]
    for P in edges:
        o = len(V); V += [(x, y, W.LV + 0.004) for x, y in P]; V += [(x, y, W.LV - 0.01) for x, y in P]
        bottom += list(range(o + n, o + 2 * n))
        Fc += [(o + i, o + n + i, o + n + i + 1, o + i + 1) for i in range(n - 1)]
    V = np.array(V); sd = W.pond_sd(V[:, 0], V[:, 1])
    ob = cw.mk_mesh(bpy, 'sz_ice', V, Fc, [M.mat_ice(kit, D)], None, False, kit.coll, {'sdw': ('FLOAT', sd)})
    return {'ob': ob, 'bottom': np.array(bottom), 'co': V.astype(np.float32)}

# ------------------------------------------------------------------ falling leaves (autumn), snow (winter)
def _leaf_shape():
    L, Wd = 0.05, 0.03
    return np.array([(L / 2, 0, 0.0), (0, Wd / 2, 0.004), (-L / 2, 0, 0.0), (0, -Wd / 2, 0.004), (0, 0, -0.002)]), [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]

def build_leaves(kit, D, rng):
    """Leaves drop from the two deciduous trees of each corner: most land on the coves, float, then sink past the glass
    to the bed (and rot into the mud before spring); the rest land on the grass and go under the snow."""
    deci = [t for t in TREES if (t[0], t[1]) in DROPPERS]; rows = []
    for k in range(1):
        for (tx, ty, s, kind) in deci:
            for j in range(80):
                st = np.array([tx, ty]) + rng.normal(0, 0.08, 2); z0 = W.H_at(tx, ty) + 0.30 * s * TREE_K + rng.uniform(-0.06, 0.06)
                water = rng.uniform() < 0.62
                for _ in range(40):
                    if water:
                        tg = np.array([rng.uniform(-0.50, 0.95), rng.uniform(-1.57, -1.20)])
                        f = W.field(tg[:1], tg[1:])
                        if f['sd'][0] < -0.06: break
                    else:
                        tg = np.array([tx, ty]) + rng.normal(0, 0.22, 2)
                        f = W.field(tg[:1], tg[1:])
                        if f['sd'][0] > 0.05 and (np.abs(tg) < W.H - 0.03).all(): break
                td = rng.uniform(6.05, 8.4); zl = W.LV + 0.001 if water else float(f['h'][0]) + 0.006
                tf = (z0 - zl) / rng.uniform(0.26, 0.36); fl = rng.uniform(0.4, 1.0) if water else 0.0
                zbed = float(f['h'][0]) + 0.005; ts = (W.LV - zbed) / rng.uniform(0.09, 0.14) if water else 0.0
                tdecay = rng.uniform(9.7, 10.4) if water else rng.uniform(9.5, 10.2)
                r = [st[0], st[1], z0, tg[0], tg[1], zl, zbed, td, tf, fl, ts, tdecay, float(water), rng.uniform(0, 1), rng.uniform(0, 6.28),
                     rng.uniform(2.5, 4.5), rng.uniform(0, 6.28), rng.uniform(-1.5, 1.5)]
                rows.append(r)
    A = np.array(rows); shp, sf = _leaf_shape(); n = len(A)
    V = np.zeros((n * 5, 3)); Fc = [tuple(i * 5 + j for j in f) for i in range(n) for f in sf]
    ob = cw.mk_mesh(kit.bpy, 'sz_leaves', V, Fc, [M.mat_leafbits(kit)], None, False, kit.coll,
                    {'lc': ('FLOAT', np.repeat(A[:, 13], 5)), 'decay': ('FLOAT', np.zeros(n * 5))})
    return {'ob': ob, 'A': A, 'shape': shp}

def _rotm(yaw, pitch, roll):
    cy, sy, cp, sp, cr, sr = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch), np.cos(roll), np.sin(roll)
    R = np.empty((len(yaw), 3, 3))
    R[:, 0, 0] = cy * cp; R[:, 0, 1] = cy * sp * sr - sy * cr; R[:, 0, 2] = cy * sp * cr + sy * sr
    R[:, 1, 0] = sy * cp; R[:, 1, 1] = sy * sp * sr + cy * cr; R[:, 1, 2] = sy * sp * cr - cy * sr
    R[:, 2, 0] = -sp; R[:, 2, 1] = cp * sr; R[:, 2, 2] = cp * cr
    return R

def leaves_pose(Lv, t):
    A = Lv['A']; n = len(A); t = t % W.LOOP
    x0, y0, z0, xt, yt, zl, zb, td, tf, fl, ts, tdc, water, lc, yaw0, om, ph, spin = A.T
    s = t - td; x = np.full(n, 1e3); y = np.zeros(n); z = np.zeros(n); pitch = np.zeros(n); roll = np.zeros(n); yaw = yaw0.copy(); scl = np.zeros(n)
    fall = (s >= 0) & (s < tf); u = np.clip(s / np.maximum(tf, 1e-3), 0, 1); e = u * u * (3 - 2 * u)
    sw = 0.05 * np.sin(om * s + ph) * (1 - u)
    x = np.where(fall, x0 + (xt - x0) * e + sw * np.cos(yaw0), x); y = np.where(fall, y0 + (yt - y0) * e + sw * np.sin(yaw0), y)
    z = np.where(fall, z0 + (zl - z0) * u, z)
    pitch = np.where(fall, 0.7 * np.sin(om * s + ph), pitch); roll = np.where(fall, 0.5 * np.cos(om * 0.8 * s), roll); yaw = np.where(fall, yaw0 + spin * s, yaw)
    landed = s >= tf; s2 = s - tf
    flo = landed & (water > 0.5) & (s2 < fl)
    x = np.where(flo, xt + 0.02 * np.sin(0.7 * s2 + ph), x); y = np.where(flo, yt, y); z = np.where(flo, zl, z); yaw = np.where(flo, yaw0 + spin * tf + 0.3 * s2, yaw)
    sink = landed & (water > 0.5) & (s2 >= fl); s3 = s2 - fl; us = np.clip(s3 / np.maximum(ts, 1e-3), 0, 1)
    x = np.where(sink, xt + 0.02 * np.sin(0.7 * fl + ph) + 0.03 * np.sin(1.3 * s3 + ph) * (1 - us), x); y = np.where(sink, yt + 0.02 * np.cos(1.1 * s3) * (1 - us), y)
    z = np.where(sink, zl + (zb - zl) * us, z); pitch = np.where(sink, 0.5 * np.sin(2.2 * s3 + ph) * (1 - us), pitch)
    yaw = np.where(sink, yaw0 + spin * tf + 0.3 * fl + 0.5 * s3 * (1 - us), yaw)
    ground = landed & (water < 0.5); x = np.where(ground, xt, x); y = np.where(ground, yt, y); z = np.where(ground, zl, z); yaw = np.where(ground, yaw0 + spin * tf, yaw)
    vis = s >= 0
    decay = np.clip((t - tdc) / 1.2, 0, 1) * vis
    scl = np.where(vis, np.clip(s / 0.15, 0, 1) * (1 - np.clip((t - tdc - 0.6) / 1.0, 0, 1)), 0.0)
    R = _rotm(yaw, pitch, roll); V = np.einsum('nij,kj->nki', R, Lv['shape']) * scl[:, None, None] + np.column_stack([x, y, z])[:, None, :]
    V[scl <= 1e-4] = (0.0, 0.0, -50.0)
    me = Lv['ob'].data; me.vertices.foreach_set('co', V.astype(np.float32).ravel())
    me.attributes['decay'].data.foreach_set('value', np.repeat(decay, 5).astype(np.float32)); me.update()

def build_snow(kit, rng, n=1500):
    bpy = kit.bpy; r = 0.0075
    shp = np.array([(r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0), (0, 0, r), (0, 0, -r)]); sf = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    m = cw.mat_simple(kit, 'sz_flake', (0.97, 0.98, 1.0), 0.6, emission=(0.95, 0.97, 1.0), strength=0.35)
    Fc = [tuple(i * 6 + j for j in f) for i in range(n) for f in sf]
    ob = cw.mk_mesh(bpy, 'sz_snow', np.zeros((n * 6, 3)), Fc, [m], None, False, kit.coll)
    for a in ('visible_shadow',): setattr(ob, a, False)
    xy = rng.uniform(-3.0, 3.0, (n, 2)); z0 = rng.uniform(-0.6, 2.9, n); tb = rng.uniform(8.9, 10.8, n); v = rng.uniform(0.32, 0.55, n)
    inside = (np.abs(xy) < W.H).all(1); gz = np.where(inside, np.maximum(W.field(xy[:, 0], xy[:, 1])['h'], W.LV + 0.004), -W.DEPTH)
    return {'ob': ob, 'xy': xy, 'z0': z0, 'tb': tb, 'v': v, 'gz': gz, 'ph': rng.uniform(0, 6.28, n), 'end': rng.uniform(10.9, 11.3, n), 'shape': shp}

def snow_pose(Sn, t):
    s = t - Sn['tb']; z = Sn['z0'] - Sn['v'] * s
    alive = (s >= 0) & (z > Sn['gz']) & (t < Sn['end'] + 0.35)
    sc = np.clip(s / 0.4, 0, 1) * np.clip((Sn['end'] + 0.35 - t) / 0.35, 0, 1) * alive
    x = Sn['xy'][:, 0] + 0.05 * np.sin(1.3 * s + Sn['ph']); y = Sn['xy'][:, 1] + 0.05 * np.cos(1.1 * s + Sn['ph'])
    V = Sn['shape'][None] * sc[:, None, None] + np.column_stack([x, y, z])[:, None, :]; V[sc <= 1e-4] = (0.0, 0.0, -50.0)
    me = Sn['ob'].data; me.vertices.foreach_set('co', V.astype(np.float32).ravel()); me.update()

# ------------------------------------------------------------------ birds (turn with the loop) and dragonflies
def build_birds(kit, rng, n=3):
    bpy = kit.bpy; mat = cw.mat_simple(kit, 'sz_bird', (0.12, 0.11, 0.11), 0.6); out = []; size = 0.05
    for k in range(n):
        body = cw.mk_mesh(bpy, f'sz_bird{k}', *cw._tube([(-size * 0.5, 0, 0), (0, 0, 0), (size * 0.45, 0, 0)], [size * 0.08, size * 0.12, size * 0.05], 6), [mat], None, True, kit.coll)
        wings = []
        for side in (-1, 1):
            V = [(-size * 0.15, 0, 0), (size * 0.15, 0, 0), (0.0, side * size * 0.9, 0), (-size * 0.25, side * size * 0.7, 0)]
            wg = cw.mk_mesh(bpy, f'sz_bird{k}w{side}', V, [(0, 1, 2, 3)], [mat], None, False, kit.coll); wg.parent = body; wings.append((wg, side))
        out.append((body, wings, rng.uniform(1.7, 2.3), rng.uniform(0.75, 1.15), k * 2 * math.pi / n + rng.uniform(-0.4, 0.4), rng.uniform(2.6, 3.6)))
    return out

def birds_pose(B, kit, t):
    """Each bird circles the block once per loop. They fly out in autumn and come back with the thaw."""
    p = W.cv('birds', t)
    for body, wings, r, h, a0, flap in B:
        a = a0 + 2 * math.pi * t / W.LOOP; rr = r + (1 - p) * 9.0
        body.location = (rr * math.cos(a), rr * math.sin(a), h + (1 - p) * 2.5 + 0.08 * math.sin(kit.cycles(t, 1 / 6.0) + a0))
        body.rotation_euler = (math.radians(-12), 0, a + math.pi / 2)
        f = kit.cycles(t, flap); burst = 0.5 + 0.5 * math.sin(kit.cycles(t, 0.25) + a0); ang = math.radians(10 + 35 * burst * math.sin(f))
        for wg, side in wings: wg.rotation_euler = (side * ang, 0, 0)

def build_flies(kit, rng, n=3):
    bpy = kit.bpy; body_m = cw.mat_simple(kit, 'sz_fly', (0.10, 0.36, 0.72), 0.3, metallic=0.5)
    wing_m = cw.mat_simple(kit, 'sz_flywing', (0.92, 0.95, 1.0), 0.1); out = []
    for k in range(n):
        v, f = cw._tube([(-0.04, 0, 0), (0.0, 0, 0), (0.02, 0, 0)], [0.0025, 0.004, 0.0045], 6)
        body = cw.mk_mesh(bpy, f'sz_fly{k}', v, f, [body_m], None, True, kit.coll); wings = []
        for side in (-1, 1):
            for off in (0.006, -0.004):
                V = [(off, 0, 0.003), (off + 0.006, side * 0.032, 0.003), (off - 0.004, side * 0.034, 0.003)]
                wg = cw.mk_mesh(bpy, f'sz_fly{k}w{side}{off}', V, [(0, 1, 2)], [wing_m], None, False, kit.coll); wg.parent = body; wings.append((wg, side))
        out.append((body, wings, rng.uniform(0, 6.28), rng.uniform(0.7, 1.2), rng.uniform(3.1, 3.5), rng.uniform(6.0, 6.4)))
    return out

def flies_pose(Fl, t):
    for body, wings, ph, sp, t_in, t_out in Fl:
        pres = W.smooth(t_in, t_in + 0.6, t) * (1 - W.smooth(t_out - 0.6, t_out, t))
        ang = ph + 0.9 * sp * t; rr = 0.42 + 0.25 * math.sin(1.7 * t + ph)
        x, y = rr * math.cos(ang) + 0.18 * math.sin(3.1 * t + ph), rr * math.sin(ang) + 0.18 * math.cos(2.3 * t)
        far = (1 - pres) * 5.0
        body.location = (x + far * math.cos(ph), y + far * math.sin(ph), W.LV + 0.10 + 0.05 * math.sin(2.9 * t + ph) + far * 0.4)
        body.rotation_euler = (0, 0, ang + math.pi / 2 + 0.3 * math.sin(4.0 * t))
        for i, (wg, side) in enumerate(wings): wg.rotation_euler = (side * 0.5 * math.sin(97.0 * t + i), 0, 0)
        body.hide_render = bool(pres < 0.02)

# ============================================================================== harness entry points
def build(bpy, ctx):
    rng = np.random.default_rng(7)
    kit = cw.Kit(bpy, seed=7, loop=W.LOOP); D = M.Drive()
    L = cw.block(kit, size=(W.S, W.S), depth=W.DEPTH, strata=STRATA, top=W.land_h, water=[cw.basin(W.pond_sd, depth=0.32, level=W.LV, shelf=0.30)],
                 seed=7, season='summer', res=0.02, grass=0, trees=0, boulders=0, flowers=0, under=False, lilies=0, reeds=0, name='sz_block')
    reshape(bpy, L)
    F = build_frogs(kit, L, D); cache, zc = LF.build_cache(kit)
    L.objects['top'].data.materials[0] = M.mat_top(kit, D)
    L.objects['walls'].data.materials[0] = M.mat_strata(kit, D, STRATA, F['burrow'], (LF.CACHE[0], zc, LF.CACHE[1], LF.CACHE[2]))
    L.objects['water'].data.materials[0] = M.mat_water(kit, D)
    pop = populate(kit, L, D, rng)
    ice = build_ice(kit, D); leaves = build_leaves(kit, D, rng); snow = build_snow(kit, rng)
    birds = build_birds(kit, rng); flies = build_flies(kit, rng)
    life = {'atmo': LF.build_atmosphere(kit, D), 'duck': LF.build_duck(kit), 'fish': LF.build_fish(kit, rng), 'squirrel': LF.build_squirrel(kit),
            'robin': LF.build_robin(kit), 'fossil': LF.build_fossil(kit)}
    cw.studio(kit, color=SEASON['bg'][0], key_az=SUN_AZ, key_el=45.0, key=3.4, angle=9.0, fill=0.9, land=L)
    aspect = '16:9' if ctx['W'] >= ctx['H'] else '9:16'
    cam = cw.camera(kit, L, aspect, az=AZ0, el=EL, lens=LENS)
    a = math.radians(AZ0); span = W.S * (abs(math.cos(a)) + abs(math.sin(a)))      # the block's width across the view
    half = math.atan(18.0 / LENS * (min(ctx['W'], ctx['H']) / max(ctx['W'], ctx['H'])))
    cam.pose(dist=span / WIDTH / 2 / math.tan(half) * 0.95, target=(0.0, 0.0, TZ))   # 0.95: perspective widens the near corner
    life['title'] = LF.build_title(kit, cam, ROOT)
    cw.apply_cycles(bpy); bpy.context.scene.cycles.transparent_max_bounces = 64   # cut-out canopies stack many layers
    wd = bpy.context.scene.world; nodes = wd.node_tree.nodes
    bgs = [n for n in nodes if n.bl_idname == 'ShaderNodeBackground']
    S = {'kit': kit, 'land': L, 'D': D, 'cam': cam, 'life': life, 'pop': pop, 'frog': F, 'ice': ice, 'leaves': leaves, 'snow': snow, 'birds': birds, 'flies': flies,
         'sun': bpy.data.objects['cw_sun'], 'floor': M._principled(bpy.data.materials['cw_floor'].node_tree),
         'ramp': next(n for n in nodes if n.bl_idname == 'ShaderNodeValToRGB').color_ramp,
         'bg_light': next(b for b in bgs if not b.inputs['Color'].is_linked)}
    frame(bpy, ctx, S, 0, 0.0)
    # opt-in art direction (films/styles/cutaway/art/<name>.py) through the kit adapter: the look-board folders set
    # KF_ART_NAME before running this file, or $KF_ART names it; without either, nothing here changes the film
    art = globals().get('KF_ART_NAME') or os.environ.get('KF_ART')
    if art:
        import importlib.util
        sp = importlib.util.spec_from_file_location('kf_art_adapter', os.path.join(ROOT, 'films', 'styles', 'cutaway', 'art', '_adapter.py'))
        ad = importlib.util.module_from_spec(sp); sp.loader.exec_module(ad)
        S['art'] = ad.attach(bpy, ctx, art, kit=kit, land=L, cam=cam, settings=SETTINGS, strata=STRATA, words=[life['title']])
        S['art'].frame(bpy, ctx, 0.0)
    return S

def frame(bpy, ctx, S, i, t):
    kit, D = S['kit'], S['D']; kit.update(t); B = lambda k: W.blend(t, SEASON[k])
    for k in ('ground', 'ground2', 'gtip', 'bedA', 'bedB', 'wtint', 'reedtint'): D.setc(k, B(k))
    D.set('wdens', B('wdens'))
    wts = W.weights(t)
    D.setramp('grass', [tuple(sum(w * np.array(GRASS[s][j]) for s, w in enumerate(wts))) for j in range(5)])
    D.setramp('leaf', [tuple(sum(w * np.array(LEAF[s][j]) for s, w in enumerate(wts))) for j in range(5)])
    for k in ('snow', 'ice', 'wet', 'dens', 'bloss', 'litter', 'roots', 'caus', 'burrow', 'tunnel', 'mist', 'fog'): D.set(k, W.cv(k, t))
    D.set('haze', B('haze')); D.setc('hazecol', B('hazecol'))
    # the camera sways and returns; the light's height and colour follow the season
    S['cam'].pose(az=AZ0 + SWAY * math.sin(2 * math.pi * t / W.LOOP))
    el = B('sun_el'); S['sun'].rotation_euler = (math.radians(90 - el), 0, math.radians(SUN_AZ + 90))
    S['sun'].data.energy = B('sun_e'); S['sun'].data.color = B('sun_col'); S['sun'].data.angle = math.radians(B('sun_ang'))
    bg = cw.srgb(B('bg')); S['floor'].inputs['Base Color'].default_value = bg
    for el_ in S['ramp'].elements: el_.color = bg
    bl = S['bg_light']   # an art direction may replace the world: then its own light stays as it set it
    try:
        if 'Color' in bl.inputs: bl.inputs['Color'].default_value = cw.srgb(B('fill_col')); bl.inputs['Strength'].default_value = B('fill')
    except ReferenceError:
        pass
    # growth and decay
    ob, sc = S['pop']['grass']; ob.data.attributes['scale'].data.foreach_set('value', (sc * W.cv('grassh', t)).astype(np.float32)); ob.data.update()
    ob, sc, on, off = S['pop']['flowers']; ob.data.attributes['scale'].data.foreach_set('value', (sc * W.win(t, on, off, 0.5)).astype(np.float32)); ob.data.update()
    ob, sc, d0 = S['pop']['lilies']; g = W.smooth(d0, d0 + 1.4, t) * (1 - W.smooth(7.0, 8.8, t))
    ob.data.attributes['scale'].data.foreach_set('value', (sc * g).astype(np.float32)); ob.data.update()
    ice = S['ice']; co = ice['co'].copy(); co[ice['bottom'], 2] = W.LV + 0.004 - (0.01 + 0.06 * W.cv('ice', t))
    ice['ob'].data.vertices.foreach_set('co', co.ravel()); ice['ob'].data.update()
    lf = S['life']; LF.duck_pose(lf['duck'], t); LF.fish_pose(lf['fish'], t); LF.squirrel_pose(lf['squirrel'], t); LF.robin_pose(lf['robin'], t)
    frog_pose(S['frog'], kit, t); leaves_pose(S['leaves'], t); snow_pose(S['snow'], t); birds_pose(S['birds'], kit, t); flies_pose(S['flies'], t)
    if S.get('art') is not None: S['art'].frame(bpy, ctx, t)
