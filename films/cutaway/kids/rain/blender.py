"""Little Big Questions: Where does rain come from? A SILENT story told by the picture (Cutaway, Fable look, 16:9, 24 fps, 73 s).
No narration; real orchestral music (Smetana, Vltava) and real sound effects carry it; a few big words set in code. Source of
truth: beats.json (10 beats: picture, words, sound, music).

One fixed view of one lifted slice of hillside (a brook, a lake, soil and groundwater; the camera sways 2 degrees over the whole
film, no cuts); the sky above the slice carries the cloud story. EVERY event of the picture is anchored to a beat in the one
table below (EVENTS: beat, fraction of the way through it); change beats.json and the whole film re-times itself. The words
come from beats.json too (szwords.py).
Look: Fable (films/styles/cutaway/art/fable.py through art/_adapter.py), named by the module global KF_ART_NAME as the
seasons board folders do; $KF_ART overrides it ($KF_ART=none renders the plain kit materials, for debugging).
Files: szworld.py (heights, the clock of beats, moods), szmats.py (driven materials), szgeo.py (rigid parts), szlife.py (life,
the child, easter eggs, the snail), szstory.py (cloud, vapour, soil water, lake, boat, the magnifier window), szback.py (the world
behind: hills, village, sea, rainbow), szwords.py (captions), this file (the event table, build and frame).
"""
import math
import os
import sys

import numpy as np

KF_ART_NAME = 'fable'

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
for p in (os.path.join(ROOT, 'films', 'styles', 'cutaway'), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import szworld as W  # noqa: E402

# ==============================================================================================================
# THE EVENT TABLE: every timed event of the picture, as (beat, u) = u of the way through that beat of beats.json.
# Beats: hook, rewind, living (the living world), rests (the old dinosaur rests), mud (mud covers the bones),
# layers (layer on layer), stone (bone to stone), wear (the land wears away), find (the find), send (the send-off).
# ==============================================================================================================
# Beats: hook, sun (the sun warms), vapour (invisible water), drops (tiny drops), million (a million), first (first drops), soak (soaking in),
# sunagain (the sun again), around (around and around), yours (your rain). Fractions are computed from the music edit (73.0 s).
BEAT_NAMES = {'hook': 'hook', 'sun': 'the sun warms', 'vapour': 'invisible water', 'drops': 'tiny drops', 'million': 'a million', 'first': 'first drops', 'soak': 'soaking in', 'sunagain': 'the sun again', 'around': 'around and around', 'yours': 'your rain'}
EVENTS = {
    'sun0': ('sun', 0.0000), 'sun1': ('sun', 0.9167), 'vap0': ('sun', 0.8333),
    'vapup0': ('vapour', 0.0769), 'vap1': ('drops', 0.8462), 'cool0': ('vapour', 0.9231),
    'cool1': ('drops', 0.9231), 'cloud0': ('drops', 0.1538), 'cloud1': ('million', 0.6579),
    'lens0': ('million', 0.0239), 'lens1': ('million', 0.1077), 'lensj1': ('million', 0.2990),
    'lensj2': ('million', 0.4545), 'lensj3': ('million', 0.6100), 'lensj4': ('million', 0.7536),
    'lensj5': ('million', 0.8612), 'lens2': ('million', 0.9211), 'lens3': ('first', 0.0211),
    'dark0': ('million', 0.4187), 'dark1': ('million', 0.9928), 'drop0': ('first', 0.0000),
    'rainsoft': ('first', 0.6235), 'child0': ('first', 0.1717), 'umbrella0': ('first', 0.3524),
    'umbrella1': ('first', 0.4578), 'snail0': ('first', 0.1114), 'soak0': ('first', 0.9247),
    'soak1': ('soak', 0.7229), 'gw1': ('sunagain', 0.0854), 'swell1': ('soak', 0.5422),
    'boat0': ('soak', 0.0602), 'drop1': ('sunagain', 0.1220), 'jump0': ('soak', 0.2048),
    'jump1': ('soak', 0.8795), 'sunback0': ('sunagain', 0.0000), 'sunback1': ('sunagain', 0.5732),
    'rainbow0': ('sunagain', 0.4683), 'rainbow1': ('sunagain', 0.8049), 'cshrink0': ('sunagain', 0.0854),
    'cshrink1': ('around', 0.1351), 'sea0': ('around', 0.0270), 'vap2a': ('around', 0.2027),
    'vap2b': ('yours', 0.6512), 'cloud2a': ('around', 0.9459), 'cloud2b': ('yours', 0.8837),
    'words_end': ('yours', 0.0000), 'chord1': ('yours', 0.4128), 'chord2': ('yours', 0.6453),
}
W.set_events({k: (BEAT_NAMES[b], u) for k, (b, u) in EVENTS.items()})
W.WORD_IN[BEAT_NAMES['yours']] = W.B.words_end + 0.35          # the closing question

import szmats as M  # noqa: E402
import szlife as LF  # noqa: E402
import szstory as ST  # noqa: E402
import szback as BK  # noqa: E402
import szwords as WD  # noqa: E402
from szgeo import Parts, I3, tube, sphere, rx, ry  # noqa: E402

DURATION = W.DURATION
SETTINGS = {'samples': 32, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 6.0, 'adaptive_min_samples': 12,
            'denoising_prefilter': 'ACCURATE'}

AZ0, SWAY = W.VIEW_AZ, 2.0
EL, LENS, FILL = 21.0, 50.0, 0.84
CAM_DZ = 0.12
SUN_AZ = -118.0
# sun per mood (fresh morning, warm sun, golden clearing, grey rain): elevation, energy, colour
SUN = {'el': (50.0, 58.0, 24.0, 42.0), 'e': (3.4, 3.9, 2.8, 1.7),
       'col': ((1.0, 0.97, 0.90), (1.0, 0.95, 0.80), (1.0, 0.80, 0.58), (0.80, 0.86, 1.0))}
SOIL = (0.40, 0.28, 0.20)
MEADOW, MEADOW_WET = (0.42, 0.70, 0.32), (0.26, 0.58, 0.30)


def mix(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))


def blend4(t, vals):
    w = W.weights(t); a = [np.asarray(v, float) for v in vals]; o = sum(wi * ai for wi, ai in zip(w, a))
    return tuple(float(x) for x in np.atleast_1d(o)) if np.ndim(o) else float(o)


# ============================================================================== build helpers
def capture(L):
    """Remember the top grid and the walls' layout, so frame() can rewrite them for any t."""
    me = L.objects['top'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); top = co.reshape(-1, 3).astype(float)
    a = me.attributes.new('rd', 'FLOAT', 'POINT'); a.data.foreach_set('value', W.river_d(top[:, 0], top[:, 1]).astype(np.float32))
    a = me.attributes.new('rk', 'FLOAT', 'POINT'); a.data.foreach_set('value', W.rock_patch(top[:, 0], top[:, 1]).astype(np.float32))
    a = me.attributes.new('far', 'FLOAT', 'POINT'); a.data.foreach_set('value', np.zeros(len(top), np.float32))
    me = L.objects['walls'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); wl = co.reshape(-1, 3).astype(float)
    zt0 = W.slice_h(wl[:, 0], wl[:, 1], 0.0); uu = np.clip((wl[:, 2] - zt0) / (W.ZB - zt0), 0, 1)        # the slice's own frame
    return {'top': top, 'walls': wl, 'uu': uu}


def build_hole(kit, D, rng):
    """The hole the slice was lifted from, directly beneath it: dark earthy walls (darker towards the bottom, faint roots
    and pebbles in the earth), a dark floor, as deep as the slice. Only its far walls and floor show past the slice."""
    bpy = kit.bpy; X0, X1, Y0, Y1 = -W.HX - W.HM, W.HX + W.HM, -W.HY - W.HM, W.HY + W.HM; zf = W.HOLE_FLOOR
    m = cw._new_mat(bpy, 'sz_hole'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; z = g.sep(P)[2]
    col = g.ramp(g.math('DIVIDE', g.math('SUBTRACT', z, zf), -zf), [(0.0, (0.10, 0.07, 0.07)), (0.55, (0.24, 0.16, 0.13)), (1.0, (0.38, 0.27, 0.21))])
    n = g.noise(P, 9.0, 3.0); col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.35), col, (0.05, 0.03, 0.03, 1))
    peb = g.math('LESS_THAN', g.voronoi(P, 14.0, 'F1').outputs['Distance'], 0.12)
    col = g.mix(g.math('MULTIPLY', peb, 0.5), col, cw.srgb((0.50, 0.44, 0.40)))
    cw._finish(g, g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.95}))
    V = []; F = []
    def wall(P0, P1, normal, n=40, rows=10):
        o = len(V)
        for i in range(n + 1):
            x, y = P0[0] + (P1[0] - P0[0]) * i / n, P0[1] + (P1[1] - P0[1]) * i / n
            zt = float(W.land_h(np.array([x]), np.array([y]), 0.0)[0])
            for r in range(rows + 1): V.append((x, y, zt + (zf - zt) * r / rows))
        for i in range(n):
            for r in range(rows):
                a = o + i * (rows + 1) + r; c = o + (i + 1) * (rows + 1) + r; q = (a, a + 1, c + 1, c)
                p0, p1, p2 = np.array(V[q[0]]), np.array(V[q[1]]), np.array(V[q[2]])
                F.append(q if np.cross(p1 - p0, p2 - p0) @ np.asarray(normal) > 0 else q[::-1])
    wall((X0, Y1), (X1, Y1), (0, -1, 0)); wall((X0, Y0), (X0, Y1), (1, 0, 0)); wall((X1, Y0), (X1, Y1), (-1, 0, 0)); wall((X0, Y0), (X1, Y0), (0, 1, 0))
    o = len(V); V += [(X0, Y0, zf), (X1, Y0, zf), (X1, Y1, zf), (X0, Y1, zf)]; F.append((o, o + 1, o + 2, o + 3))
    hole = cw.mk_mesh(bpy, 'fs_hole', V, F, [m], None, False, kit.coll)
    # under the slice: roots and pebbles hanging off its underside, and a little soil now and then trickling into the hole
    pr = Parts('fs_underside'); items = []
    mats = [M.paint(kit, D, 'sz_root', (0.36, 0.24, 0.18), noise=0.0), M.paint(kit, D, 'sz_pebble', (0.62, 0.58, 0.54)), M.paint(kit, D, 'sz_soil', (0.40, 0.30, 0.22), noise=0.0)]
    for k in range(70):
        side = k % 4; u = rng.uniform(0.04, 0.96)
        x, y = [(-W.HX + 2 * W.HX * u, -W.HY + 0.02), (W.HX - 0.02, -W.HY + 2 * W.HY * u), (-W.HX + 2 * W.HX * u, W.HY - 0.02), (-W.HX + 0.02, -W.HY + 2 * W.HY * u)][side]
        x += rng.uniform(-0.02, 0.15) * (1 if x < 0 else -1) * 0.3; L = rng.uniform(0.10, 0.30); b = rng.uniform(-0.05, 0.05, 2)
        pts = [(0, 0, 0.01), (b[0] * 0.4, b[1] * 0.4, -L * 0.4), (b[0], b[1], -L * 0.75), (b[0] * 1.3, b[1] * 1.3, -L)]
        v, f = tube(pts, [0.012, 0.009, 0.006, 0.003], 6); items.append(('root', pr.add(v, f, 0), x, y, rng.uniform(0, 6.28)))
    for k in range(22):
        x, y = rng.uniform(-W.HX + 0.05, W.HX - 0.05), rng.uniform(-W.HY + 0.05, W.HY - 0.05)
        if k % 2: x = np.sign(x) * (W.HX - rng.uniform(0.02, 0.2))
        else: y = np.sign(y) * (W.HY - rng.uniform(0.02, 0.2))
        r = rng.uniform(0.025, 0.05); v, f = sphere((0, 0, -r * 0.4), (r, r * 0.9, r * 0.8), 1); items.append(('pebble', pr.add(v, f, 1), x, y, 0.0))
    for k in range(10):
        x, y = rng.uniform(-W.HX + 0.1, W.HX - 0.1), -W.HY + rng.uniform(0.02, 0.4); v, f = sphere((0, 0, 0), (0.013, 0.013, 0.013), 1)
        items.append(('soil', pr.add(v, f, 2), x, y, rng.uniform(0, 1)))
    pr.build(bpy, mats, kit.coll)
    return {'hole': hole, 'parts': pr, 'items': items}


def underside_pose(H, t):
    pr = H['parts']; zb = W.ZB + W.lift(t)
    for kind, j, x, y, ph in H['items']:
        if kind == 'root': pr.set(j, (x, y, zb), rx(0.10 * math.sin(0.8 * t + ph)) @ ry(0.08 * math.cos(0.6 * t + ph)))
        elif kind == 'pebble': pr.set(j, (x, y, zb))
        else:      # a grain of soil falls every 4.5 s or so, from under the slice to the hole's floor
            T = 4.5; age = ((t / T + ph) % 1.0) * T; fall = 0.5 * 9.8 * 0.25 * age * age; z = zb - fall
            if age < 1.6 and z > W.HOLE_FLOOR: pr.set(j, (x, y, z), I3, 1.0)
            else: pr.hide(j)
    pr.commit()


def build_world(kit, D, top_mat, water_mat, res=0.1):
    """The land around and behind the block, out to the hills: one grid at the same heights (szworld.top_h) and in the
    same ground paint (it follows every era), minus the block and the viewing trench; and a flood sheet with the same
    holes (the floods spread over the whole plain)."""
    xs = np.round(np.arange(-12.0, 12.0 + 1e-6, res), 4); ys = np.round(np.arange(-9.0, 14.0 + 1e-6, res), 4)
    X, Y = np.meshgrid(xs, ys); nx, ny = len(xs), len(ys); ii = np.arange(nx * ny).reshape(ny, nx)
    q = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
    cx = (X[:-1, :-1] + X[1:, 1:]).ravel() / 2; cy = (Y[:-1, :-1] + Y[1:, 1:]).ravel() / 2
    keep = ~W.in_hole(cx, cy); q = q[keep]      # the hole the slice was lifted from
    used = np.unique(q); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used)); q = remap[q]
    P = np.column_stack([X.ravel(), Y.ravel()])[used]
    attrs = {'rd': ('FLOAT', W.river_d(P[:, 0], P[:, 1])), 'rk': ('FLOAT', np.zeros(len(P))), 'far': ('FLOAT', W.far(P[:, 0], P[:, 1]))}
    V = np.column_stack([P, W.top_h(P[:, 0], P[:, 1], 0.0)])
    ob = cw.mk_mesh(kit.bpy, 'fs_world', V, q.tolist(), [top_mat], None, True, kit.coll, attrs)
    fl = cw.mk_mesh(kit.bpy, 'fs_floodworld', V, q.tolist(), [water_mat], None, False, kit.coll); fl.visible_shadow = False
    return {'ob': ob, 'P': P, 'flood': fl}


def world_pose(Wd, t):
    P = Wd['P']; z = W.top_h(P[:, 0], P[:, 1], t)
    me = Wd['ob'].data; me.vertices.foreach_set('co', np.column_stack([P, z]).astype(np.float32).ravel()); me.update()
    f = W.flood_level(t)
    if f > -0.9:
        lv = W.Z_NOW + f + 0.02; Wd['flood'].hide_render = False
        me = Wd['flood'].data; me.vertices.foreach_set('co', np.column_stack([P, lv - W.drop(P[:, 0], P[:, 1])]).astype(np.float32).ravel()); me.update()
    else: Wd['flood'].hide_render = True


def world_pose(Wd, t):
    P = Wd['P']; z = W.top_h(P[:, 0], P[:, 1], t)
    me = Wd['ob'].data; me.vertices.foreach_set('co', np.column_stack([P, z]).astype(np.float32).ravel()); me.update()
    Wd['flood'].hide_render = True


def build_water(kit, D):
    """The brook: a ribbon along its bed (rewritten each frame to follow the sloping ground, to swell in the rain and to be
    cut at the slice's edge and the hole's rim: it reads as cut from this very spot)."""
    mat = M.mat_water(kit, D)
    C = cw.catmull([tuple(p) for p in W.RIVER], 260); T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.column_stack([-T[:, 1], T[:, 0]])
    n = len(C) - 1; Fr = [(4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3) for i in range(n)]
    rib = cw.mk_mesh(kit.bpy, 'fs_river', np.zeros((4 * n, 3)), Fr, [mat], None, False, kit.coll); rib.visible_shadow = False
    on_slice = W.in_slice(C[:, 0], C[:, 1]); on_land = ~W.in_hole(C[:, 0], C[:, 1])
    seg_slice = on_slice[:-1] & on_slice[1:]; seg_land = on_land[:-1] & on_land[1:]
    inlake = W.lake_r(C[:, 0], C[:, 1]) < 0.97                    # the lake itself is drawn by its own water
    return {'rib': rib, 'C': C, 'N': N, 'seg_slice': seg_slice, 'seg_land': seg_land, 'lake': inlake[:-1] | inlake[1:]}


def water_pose(Wt, t):
    w, d = W.channel(t); e = 0.0015
    hw = w + 0.05; C, N = Wt['C'], Wt['N']
    A = C[:-1]; Bp = C[1:]; NA = N[:-1] * hw; NB = N[1:] * hw
    Q = np.stack([A - NA, Bp - NB, Bp + NB, A + NA], 1)
    rel = W.Z_NOW + W.relief(C[:, 0], C[:, 1]) - 0.5 * d - 0.014
    zs = rel + W.lift(t); zl = rel - W.drop(C[:, 0], C[:, 1])
    S = Wt['seg_slice']
    za = np.where(S, zs[:-1], zl[:-1]); zb_ = np.where(S, zs[1:], zl[1:])
    Z = np.stack([za, zb_, zb_, za], 1)
    Q[S] = np.clip(Q[S], [-W.HX + e, -W.HY + e], [W.HX - e, W.HY - e])
    V = np.concatenate([Q, Z[..., None]], 2)
    V[~(S | Wt['seg_land']) | Wt['lake']] = (0.0, 0.0, -50.0)
    Wt['rib'].data.vertices.foreach_set('co', V.reshape(-1, 3).astype(np.float32).ravel()); Wt['rib'].data.update()


RAIN_N = 760
RAIN_TOP = 2.75


def build_rain(kit, D, rng, n=RAIN_N):
    pr = Parts('fs_rain'); m = M.mat_glow(kit, D, 'fs_rainm', (0.84, 0.92, 1.0), 1.0)
    for k in range(n): pr.add([(-0.0018, 0, 0), (0.0018, 0, 0), (0.0018, 0, 0.10), (-0.0018, 0, 0.10)], [(0, 1, 2, 3)])
    pr.build(kit.bpy, [m], kit.coll, smooth=False)
    pr.ob.visible_shadow = False
    xy = rng.uniform([-2.7, -1.9], [2.7, 2.1], (n, 2))
    top = np.where(W.in_slice(xy[:, 0], xy[:, 1]), W.Z_NOW + W.relief(xy[:, 0], xy[:, 1]), W.Z_NOW + W.relief(xy[:, 0], xy[:, 1]) - W.drop(xy[:, 0], xy[:, 1]))
    return {'parts': pr, 'xy': xy, 'z0': rng.uniform(0, 3.8, n), 'v': rng.uniform(3.2, 4.2, n), 'ph': rng.uniform(0, 1, n), 'top': top}


def rain_pose(Rn, t):
    pr = Rn['parts']; k = W.rain_k(t); tilt = 0.30
    Rt = np.array([[math.cos(tilt), 0, math.sin(tilt)], [0, 1, 0], [-math.sin(tilt), 0, math.cos(tilt)]])
    SP = 3.8; L = W.lift(t)
    cx = ST.CLOUD_P[0]
    for i in range(len(Rn['z0'])):
        if k < 0.02 or Rn['ph'][i] > k / 0.8: pr.hide(i); continue
        z = RAIN_TOP - ((Rn['z0'][i] + Rn['v'][i] * t) % SP); x, y = Rn['xy'][i]
        x = x - 0.30 * (RAIN_TOP - z)
        ins = abs(x) < W.HX and abs(y) < W.HY
        if z < Rn['top'][i] + (L if ins else 0.0) + 0.01: pr.hide(i); continue
        if (not (abs(x) < W.HX + W.HM and abs(y) < W.HY + W.HM) or True) and z < -0.05 - float(W.drop(x, y)) * 0.0 and not ins and abs(x) < W.HX + W.HM and abs(y) < W.HY + W.HM: pr.hide(i); continue
        pr.set(i, (x, y, z), Rt)
    pr.commit()


# ============================================================================== harness entry points
def build(bpy, ctx):
    rng = np.random.default_rng(5)
    kit = cw.Kit(bpy, seed=5, loop=W.DURATION); D = M.Drive()
    L = cw.block(kit, size=(W.SX, W.SY), depth=-W.ZB, strata=W.STRATA, top=lambda x, y: W.slice_h(x, y, 0.0), water=None, seed=5, season='summer',
                 res=0.025, grass=0, trees=0, boulders=0, flowers=0, under=False, lilies=0, reeds=0, name='fs_block')
    geo = capture(L); hole = build_hole(kit, D, rng)
    L.objects['top'].data.materials[0] = M.mat_top(kit, D)
    water = build_water(kit, D)
    world = build_world(kit, D, L.objects['top'].data.materials[0], water['rib'].data.materials[0])
    plants = LF.build_plants(kit, L, D, rng); trees = LF.build_trees(kit, D)
    girl = LF.build_girl(kit, D)
    birds = LF.build_birds(kit, D, rng); flutter = LF.build_flutter(kit, D, rng); critters = LF.build_critters(kit, D, rng)
    eggs = LF.build_eggs(kit, D); snail = LF.build_snail(kit, D)
    story = {'cloud1': ST.build_cloud(kit, D, 'fs_cloud1', 31, [(-0.10, [-0.70, -0.35, 0.0, 0.35, 0.70], 0.30), (0.12, [-0.52, -0.17, 0.18, 0.52], 0.34), (0.32, [-0.30, 0.05, 0.36], 0.30), (0.50, [-0.08, 0.2], 0.22)], 'rcloud'),
             'cloud2': ST.build_cloud(kit, D, 'fs_cloud2', 47, [(-0.06, [-0.42, -0.1, 0.22], 0.26), (0.10, [-0.26, 0.08], 0.28), (0.26, [-0.06], 0.20)], 'rcloud2'),
             'vapour': ST.build_vapour(kit, D, rng), 'soil': ST.build_soil(kit, D, rng), 'lake': ST.build_lake(kit, D, rng), 'boat': ST.build_boat(kit, D)}
    rain = build_rain(kit, D, rng)
    cw.studio(kit, color=(0.93, 0.90, 0.84), key_az=SUN_AZ, key_el=45.0, key=3.2, angle=6.0, fill=0.8, land=L)
    cam = cw.camera(kit, L, '16:9' if ctx['W'] >= ctx['H'] else '9:16', az=AZ0, el=EL, lens=LENS, fill=FILL, top_extra=1.7, bottom_extra=W.GAP + 0.15)
    cam.pose(target=cam.target + np.array([0.0, 0.0, -W.ZB + W.GAP + CAM_DZ]))
    back = BK.build(kit, D, cam, ctx)
    words = WD.Words(kit, D, cam, ROOT)
    lens = ST.Lens(kit, D, cam, ST.CLOUD_P + np.array([0.0, 0.0, -0.1]))
    cw.apply_cycles(bpy); sc = bpy.context.scene; sc.cycles.transparent_max_bounces = 24
    S = {'kit': kit, 'D': D, 'land': L, 'geo': geo, 'water': water, 'world': world, 'hole': hole, 'plants': plants, 'trees': trees, 'girl': girl,
         'critters': critters, 'birds': birds, 'flutter': flutter, 'eggs': eggs, 'snail': snail, 'story': story, 'lens': lens, 'rain': rain, 'back': back, 'words': words,
         'cam': cam, 'az0': cam.az, 'sun': bpy.data.objects['cw_sun']}
    frame(bpy, ctx, S, 0, 0.0)
    art = os.environ.get('KF_ART', globals().get('KF_ART_NAME'))
    if art and art != 'none':
        import importlib.util
        sp = importlib.util.spec_from_file_location('kf_art_adapter', os.path.join(ROOT, 'films', 'styles', 'cutaway', 'art', '_adapter.py'))
        ad = importlib.util.module_from_spec(sp); sp.loader.exec_module(ad)
        S['art'] = ad.attach(bpy, ctx, art, kit=kit, land=L, cam=cam, settings=SETTINGS, strata=W.STRATA, words=words.obs + lens.crisp)
        S['art'].frame(bpy, ctx, 0.0)
    return S


def frame(bpy, ctx, S, i, t):
    kit, D = S['kit'], S['D']; kit.update(t); B = W.B
    # ---- the land: top and walls follow the heights (the slice bobs; the brook swells)
    tp = S['geo']['top']; z = W.top_h(tp[:, 0], tp[:, 1], t); co = tp.copy(); co[:, 2] = z
    me = S['land'].objects['top'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel()); me.update()
    wl = S['geo']['walls']; uu = S['geo']['uu']; zt = W.slice_h(wl[:, 0], wl[:, 1], t); zz = zt + (W.ZB - zt) * uu
    co = wl.copy(); co[:, 2] = zz + W.lift(t); me = S['land'].objects['walls'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel())
    me.attributes['sd'].data.foreach_set('value', (W.Z_MAX - zz).astype(np.float32)); me.attributes['dtop'].data.foreach_set('value', (zt - zz).astype(np.float32)); me.update()
    # ---- the ground's colour of the moment
    wet = W.wet(t)
    D.setc('ground', mix(SOIL, (0.30, 0.22, 0.18), wet)); D.set('green', 1.0)
    D.setc('greencol', mix(MEADOW, MEADOW_WET, wet)); D.set('wet', wet)
    D.set('rw', W.channel(t)[0]); D.set('rockamt', 0.0)
    water_pose(S['water'], t); world_pose(S['world'], t); underside_pose(S['hole'], t)
    D.setc('haze', blend4(t, ((0.66, 0.80, 0.78), (0.70, 0.84, 0.76), (0.80, 0.72, 0.62), (0.62, 0.68, 0.74))))
    D.set('murk', 0.0); D.set('walpha', 1.0)
    # ---- the cloud's colour: white, grey and heavy as the drops join, white again when the sun is back
    g = W.keys(t, [(B.dark0, 0.0), (B.dark1, 1.0), (B.drop1 - 1.0, 1.0), (B.sunback1, 0.0)])
    D.setc('rcloud', mix((1.0, 0.98, 0.94), (0.70, 0.74, 0.82), g)); D.setc('rcloud2', (1.0, 0.98, 0.94))
    # ---- the camera holds (a 2 degree sway over the whole film); the light follows the story
    S['cam'].pose(az=S['az0'] + SWAY * math.sin(2 * math.pi * t / W.DURATION))
    S['sun'].rotation_euler = (math.radians(90 - blend4(t, SUN['el'])), 0, math.radians(SUN_AZ + 90))
    S['sun'].data.energy = blend4(t, SUN['e']); S['sun'].data.color = blend4(t, SUN['col'])
    # ---- life and story
    LF.plants_pose(S['plants'], t); LF.trees_pose(S['trees'], t)
    LF.girl_pose(S['girl'], t)
    LF.critters_pose(S['critters'], t); LF.birds_pose(S['birds'], t); LF.flutter_pose(S['flutter'], t); LF.eggs_pose(S['eggs'], t); LF.snail_pose(S['snail'], t)
    st = S['story']; g1, c1, g2, c2 = ST.cloud_state(t)
    ST.cloud_pose(st['cloud1'], t, g1, c1); ST.cloud_pose(st['cloud2'], t, g2, c2, 1.7)
    ST.vapour_pose(st['vapour'], D, t); ST.soil_pose(st['soil'], D, t); ST.lake_pose(st['lake'], t); ST.boat_pose(st['boat'], t)
    S['lens'].pose(t)
    rain_pose(S['rain'], t); BK.pose(S['back'], D, t)
    S['words'].pose(t, None)
    if S.get('art') is not None: S['art'].frame(bpy, ctx, t)
