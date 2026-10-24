"""Little Big Questions, pilot: How does a dinosaur turn into stone? A SILENT story told by the picture (Cutaway, Fable
look, 16:9, 24 fps, 60 s). Sam 23 Oct 20:09: no narration; real orchestral music and real sound effects carry it; a few
big words set in code. Source of truth: beats.json (10 beats: picture, words, sound, music).

One fixed view of one block (a 2 degree sway over the whole film, no cuts); the world changes in front of the camera and
that is the story. The beats will be re-timed to the phrases of the chosen recording (choreographed to the music), so
EVERY event of the picture is anchored to a beat in the one table below (EVENTS: beat, fraction of the way through it);
change beats.json and the whole film re-times itself. The words come from beats.json too (szwords.py).
Look: Fable (films/styles/cutaway/art/fable.py through art/_adapter.py), named by the module global KF_ART_NAME as the
seasons board folders do; $KF_ART overrides it ($KF_ART=none renders the plain kit materials, for debugging).
Files: szworld.py (heights, the clock of beats, moods), szmats.py (driven materials), szgeo.py (rigid parts, the
dinosaur), szlife.py (life, plants, the girl, easter eggs, the mascot), szstory.py (set pieces of single beats: the peel,
babies, turtle, skeleton, mammoths, the magnifier window), szfossil.py (the skeleton in the cut face), szback.py (the
world behind the block), szwords.py (captions, clock, label), this file (the event table, build and frame).
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
BEAT_NAMES = {'hook': 'hook', 'rewind': 'rewind', 'living': 'the living world', 'rests': 'the old dinosaur rests',
              'mud': 'mud covers the bones', 'layers': 'layer on layer', 'stone': 'bone to stone', 'wear': 'the land wears away',
              'find': 'the find', 'send': 'the send-off'}
EVENTS = {
    # hook: today; the red ball rolls in and stops on the grass (the mascot peeks at the bone, the fossil glints)
    'ball0': ('hook', 0.12), 'ball1': ('hook', 0.50),
    # rewind: today's plants fold, the ground above the old one peels away upward, the sky runs back, ferns grow
    'rw0': ('rewind', 0.00), 'peel0': ('rewind', 0.15), 'peel1': ('rewind', 0.75), 'rw1': ('rewind', 1.00),
    'fern0': ('rewind', 0.45), 'fern1': ('living', 0.08),
    # the living world: the dinosaur arrives and walks to the ferns, munches; babies splash; the turtle plods by
    'dino_in0': ('rewind', 0.70), 'dino_in1': ('living', 0.03), 'walk0': ('living', 0.00), 'walk1': ('living', 0.20),
    'munch0': ('living', 0.20), 'munch1': ('living', 0.86), 'turtle0': ('living', 0.05), 'turtle1': ('rests', 0.40),
    # the old dinosaur rests: the babies grow and walk off with the herd; it walks to the bank, lies down, stays still
    'grow0': ('living', 0.80), 'grow1': ('rests', 0.15), 'leave0': ('rests', 0.05), 'leave1': ('rests', 0.90),
    'towater0': ('living', 0.86), 'towater1': ('rests', 0.35), 'lie0': ('rests', 0.35), 'lie1': ('rests', 0.65),
    'curl0': ('rests', 0.60), 'curl1': ('rests', 0.92), 'soft0': ('living', 0.90), 'soft1': ('rests', 0.85),
    'leaf0': ('rests', 0.50), 'leaf1': ('rests', 0.98),
    # mud: rain and a gentle flood; the body fades to the skeleton; the mud covers it like a blanket; bones in the face
    'rainA0': ('mud', 0.00), 'rainA1': ('mud', 0.80), 'flood0': ('mud', 0.08), 'flood1': ('mud', 0.30), 'flood2': ('mud', 0.70),
    'flood3': ('mud', 0.95), 'skel0': ('mud', 0.15), 'skel1': ('mud', 0.40), 'mud0': ('mud', 0.42), 'mud1': ('mud', 0.82),
    'bones_in0': ('mud', 0.72), 'bones_in1': ('mud', 0.95),
    # layer on layer: five layers, each brought by water (slots), the eras race by above (forest, ice, mammoths, grass, forest)
    'stack0': ('layers', 0.00), 'stack1': ('layers', 1.00), 'hump1': ('layers', 0.15),
    # bone to stone: the magnifier window opens, drops seep in, the stone front runs along; THE HIT at 43.0 s (5/6 of the beat)
    'lens0': ('stone', 0.02), 'lens1': ('stone', 0.10), 'seep0': ('stone', 0.10), 'seep1': ('stone', 0.78), 'stone0': ('stone', 0.20),
    'hit': ('stone', 5.0 / 6.0), 'lens2': ('stone', 0.95), 'lens3': ('wear', 0.12),
    # the land wears away: wind and rain, the top wears down, the hills shrink; today's meadow comes back
    'rain0': ('wear', 0.00), 'rain1': ('wear', 0.85), 'erode0': ('wear', 0.03), 'erode1': ('wear', 0.80),
    'green0': ('wear', 0.55), 'green1': ('find', 0.05),
    # the find: she runs in from the meadow beside the dig, kneels at the little rock face, brush, brush (47.0 to 49.4);
    # the bone appears ON THE CLIMAX at 49.5 s (1/3 of the beat) with FOSSIL!; she jumps for joy
    'girl0': ('wear', 0.58), 'girl1': ('wear', 0.95), 'kneel0': ('wear', 0.93), 'kneel1': ('find', 0.02), 'brush0': ('find', 0.00),
    'brush1': ('find', 0.32), 'pit0': ('find', 0.01), 'pit1': ('find', 1.0 / 3.0), 'cheer0': ('find', 0.345), 'cheer1': ('find', 0.62),
    'label0': ('find', 1.0 / 3.0), 'label1': ('find', 0.70), 'flyup0': ('find', 0.35),      # the label: 2.75 s on screen
    # the send-off: the ball rolls back; she lifts her toy dinosaur up beside the fossil on the final swell (57 to 60 s);
    # WHAT IS UNDER YOUR FEET? over the last quiet chord (60 to 65 s); the mascot waves
    'ballback0': ('send', 0.08), 'ballback1': ('send', 0.28), 'hold0': ('send', 2.5 / 10.5), 'hold1': ('send', 5.5 / 10.5),
    'words_send': ('send', 5.5 / 10.5), 'wave0': ('send', 0.60),
}
W.set_events({k: (BEAT_NAMES[b], u) for k, (b, u) in EVENTS.items()})
W.WORD_IN[BEAT_NAMES['send']] = W.B.words_send          # the last words wait for the last chord

import szmats as M  # noqa: E402
import szlife as LF  # noqa: E402
import szstory as ST  # noqa: E402
import szfossil as FO  # noqa: E402
import szback as BK  # noqa: E402
import szwords as WD  # noqa: E402
from szgeo import Parts, I3, tube, sphere, rx, ry  # noqa: E402

DURATION = W.DURATION
SETTINGS = {'samples': 32, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 6.0, 'adaptive_min_samples': 12,
            'denoising_prefilter': 'ACCURATE'}

AZ0, SWAY = W.VIEW_AZ, 2.0                 # camera azimuth; a 2 degree sway on one slow sine over the whole film
EL, LENS, FILL = 21.0, 50.0, 0.84
CAM_DZ = 0.12                          # extra lift of the aim (m)
SUN_AZ = -118.0                        # sun from the front left, so the front face takes the light
# sun per mood (today, fern era, evening, deep time): elevation, energy, colour
SUN = {'el': (52.0, 42.0, 14.0, 34.0), 'e': (3.4, 3.2, 2.4, 2.4),
       'col': ((1.0, 0.97, 0.90), (1.0, 0.90, 0.72), (1.0, 0.66, 0.46), (0.86, 0.90, 1.0))}
TODAY_EARTH, FERN_FLOOR = (0.46, 0.34, 0.24), (0.30, 0.30, 0.20)
MEADOW, MOSS = (0.42, 0.70, 0.32), (0.20, 0.50, 0.30)
SLOT_GROUND = {'forest': (0.30, 0.40, 0.22), 'ice': (0.93, 0.96, 1.0), 'mammoth': (0.74, 0.62, 0.36), 'grass': (0.52, 0.64, 0.30)}
SLOT_GREEN = {'forest': 0.75, 'ice': 0.0, 'mammoth': 0.25, 'grass': 0.85}


def mix(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))


def band_color(z):
    """The colour of the rock band at height z (the bare top while layers stack or wear away)."""
    zz = W.Z_MAX
    for name, th, col, _ in W.STRATA:
        if z > zz - th: return col
        zz -= th
    return W.STRATA[-1][2]


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


def build_water(kit, D):
    """Two waters, one material: a ribbon along the river's bed (the river long ago, the brook today; a skirt where it
    leaves through the right cut face) and a box over the whole top that only shows in the floods."""
    e = 0.0015; bx = [(-W.HX + e, -W.HY + e), (W.HX - e, -W.HY + e), (W.HX - e, W.HY - e), (-W.HX + e, W.HY - e)]
    V = [(x, y, -1.0) for x, y in bx] + [(x, y, 0.0) for x, y in bx]
    F = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mat = M.mat_water(kit, D)
    ob = cw.mk_mesh(kit.bpy, 'fs_flood', V, F, [mat], None, False, kit.coll); ob.visible_shadow = False
    C = cw.catmull([tuple(p) for p in W.RIVER], 260); T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.column_stack([-T[:, 1], T[:, 0]])
    n = len(C) - 1; Fr = [(4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3) for i in range(n)]      # one free quad per segment
    rib = cw.mk_mesh(kit.bpy, 'fs_river', np.zeros((4 * n, 3)), Fr, [mat], None, False, kit.coll); rib.visible_shadow = False
    on_slice = W.in_slice(C[:, 0], C[:, 1]); on_land = ~W.in_hole(C[:, 0], C[:, 1])
    seg_slice = on_slice[:-1] & on_slice[1:]; seg_land = on_land[:-1] & on_land[1:]
    return {'ob': ob, 'xy': np.array(bx), 'rib': rib, 'C': C, 'N': N, 'seg_slice': seg_slice, 'seg_land': seg_land}


def water_pose(Wt, t):
    bz = W.base(t); w, d = W.channel(t); f = W.flood_level(t); e = 0.0015
    if f > -0.9:
        lf = W.lift(t); lv = bz + f + 0.02 + lf; Wt['ob'].hide_render = False
        V = [(x, y, bz - 0.2 + lf) for x, y in Wt['xy']] + [(x, y, lv) for x, y in Wt['xy']]
        Wt['ob'].data.vertices.foreach_set('co', np.array(V, np.float32).ravel()); Wt['ob'].data.update()
    else: Wt['ob'].hide_render = True
    if d < 1e-3 or w < 0.01: Wt['rib'].hide_render = True; return
    hw = w + 0.05; C, N = Wt['C'], Wt['N']
    # the river on the slice is lifted with it; on the land it stays at the land's level; segments over the gap are left
    # out, so it ends at the slice's edge and at the hole's rim (it reads as cut from this very spot)
    zs = bz - 0.012 - 0.5 * d + W.lift(t); zl = W.land_water(t) - W.drop(C[:, 0], C[:, 1])
    A = C[:-1]; Bp = C[1:]; NA = N[:-1] * hw; NB = N[1:] * hw
    Q = np.stack([A - NA, Bp - NB, Bp + NB, A + NA], 1)                      # (n, 4, 2)
    za = np.where(Wt['seg_slice'], zs, zl[:-1]); zb_ = np.where(Wt['seg_slice'], zs, zl[1:])
    Z = np.stack([za, zb_, zb_, za], 1)
    S = Wt['seg_slice']; Q[S] = np.clip(Q[S], [-W.HX + e, -W.HY + e], [W.HX - e, W.HY - e])
    V = np.concatenate([Q, Z[..., None]], 2)
    V[~(Wt['seg_slice'] | Wt['seg_land'])] = (0.0, 0.0, -50.0)
    Wt['rib'].hide_render = False
    Wt['rib'].data.vertices.foreach_set('co', V.reshape(-1, 3).astype(np.float32).ravel()); Wt['rib'].data.update()


def build_rain(kit, D, rng, n=520):
    pr = Parts('fs_rain'); m = M.mat_glow(kit, D, 'fs_rainm', (0.82, 0.90, 1.0), 0.9)
    for k in range(n): pr.add([(-0.0018, 0, 0), (0.0018, 0, 0), (0.0018, 0, 0.09), (-0.0018, 0, 0.09)], [(0, 1, 2, 3)])
    pr.build(kit.bpy, [m], kit.coll, smooth=False)
    pr.ob.visible_shadow = False
    return {'parts': pr, 'xy': rng.uniform([-2.6, -1.8], [2.6, 2.0], (n, 2)), 'z0': rng.uniform(0, 4.4, n), 'v': rng.uniform(3.2, 4.2, n), 'ph': rng.uniform(0, 1, n)}


def rain_pose(Rn, t):
    pr = Rn['parts']; B = W.B; k = max(0.6 * W.win(t, B.rainA0, B.rainA1, 0.6), W.win(t, B.rain0, B.rain1, 0.6)); tilt = 0.35
    Rt = np.array([[math.cos(tilt), 0, math.sin(tilt)], [0, 1, 0], [-math.sin(tilt), 0, math.cos(tilt)]])
    for i in range(len(Rn['z0'])):
        if k < 0.02 or Rn['ph'][i] > k: pr.hide(i); continue
        z = 3.6 - ((Rn['z0'][i] + Rn['v'][i] * t) % 4.4); x, y = Rn['xy'][i]
        x = x - 0.35 * (3.6 - z)
        if abs(x) < W.HX and abs(y) < W.HY and z < W.base(t) + W.lift(t) + 0.02: pr.hide(i); continue
        if not (abs(x) < W.HX + W.HM and abs(y) < W.HY + W.HM) and z < 0.0: pr.hide(i); continue
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
    dino = LF.build_dino(kit, D); girl = LF.build_girl(kit, D); dug = LF.build_dug_bone(kit, D)
    critters = LF.build_critters(kit, D, rng); birds = LF.build_birds(kit, D, rng); flutter = LF.build_flutter(kit, D, rng)
    eggs = LF.build_eggs(kit, D); snail = LF.build_snail(kit, D)
    story = {'peel': ST.build_peel(kit, D), 'babies': ST.build_babies(kit, D, list(dino.ob.data.materials)), 'turtle': ST.build_turtle(kit, D),
             'leaf': ST.build_leaf(kit, D), 'skel': ST.build_skeleton(kit, D, dino), 'mammoths': ST.build_mammoths(kit, D),
             'saplings': ST.build_saplings(kit, D, rng)}
    fossil = FO.build(kit, D); rain = build_rain(kit, D, rng)
    cw.studio(kit, color=(0.93, 0.90, 0.84), key_az=SUN_AZ, key_el=45.0, key=3.2, angle=6.0, fill=0.8, land=L)
    cam = cw.camera(kit, L, '16:9' if ctx['W'] >= ctx['H'] else '9:16', az=AZ0, el=EL, lens=LENS, fill=FILL, top_extra=0.75, bottom_extra=W.GAP + 0.15)
    cam.pose(target=cam.target + np.array([0.0, 0.0, -W.ZB + W.GAP + CAM_DZ]))   # framed on the lifted slice, its gap and the hole's rim
    back = BK.build(kit, D, cam, ctx)
    words = WD.Words(kit, D, cam, ROOT)
    lens = ST.Lens(kit, D, cam, (W.DINO_LIE_X - 0.12 * W.DINO_K, -W.HY, W.Z_ANC + 0.09))      # slice frame: the lens adds lift(t)
    cw.apply_cycles(bpy); sc = bpy.context.scene; sc.cycles.transparent_max_bounces = 24
    S = {'kit': kit, 'D': D, 'land': L, 'geo': geo, 'water': water, 'world': world, 'hole': hole, 'plants': plants, 'trees': trees, 'dino': dino, 'girl': girl, 'dug': dug,
         'critters': critters, 'birds': birds, 'flutter': flutter, 'eggs': eggs, 'snail': snail, 'story': story, 'lens': lens, 'fossil': fossil, 'rain': rain, 'back': back, 'words': words,
         'cam': cam, 'az0': cam.az, 'sun': bpy.data.objects['cw_sun']}
    frame(bpy, ctx, S, 0, 0.0)
    art = os.environ.get('KF_ART', globals().get('KF_ART_NAME'))
    if art and art != 'none':
        import importlib.util
        sp = importlib.util.spec_from_file_location('kf_art_adapter', os.path.join(ROOT, 'films', 'styles', 'cutaway', 'art', '_adapter.py'))
        ad = importlib.util.module_from_spec(sp); sp.loader.exec_module(ad)
        S['art'] = ad.attach(bpy, ctx, art, kit=kit, land=L, cam=cam, settings=SETTINGS, strata=W.STRATA, words=words.obs)
        S['art'].frame(bpy, ctx, 0.0)
    return S


def frame(bpy, ctx, S, i, t):
    kit, D = S['kit'], S['D']; kit.update(t); B = W.B
    # ---- the land: top and walls follow the story's heights
    tp = S['geo']['top']; z = W.top_h(tp[:, 0], tp[:, 1], t); co = tp.copy(); co[:, 2] = z
    me = S['land'].objects['top'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel()); me.update()
    wl = S['geo']['walls']; uu = S['geo']['uu']; zt = W.slice_h(wl[:, 0], wl[:, 1], t); zz = zt + (W.ZB - zt) * uu
    co = wl.copy(); co[:, 2] = zz + W.lift(t); me = S['land'].objects['walls'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel())
    me.attributes['sd'].data.foreach_set('value', (W.Z_MAX - zz).astype(np.float32)); me.attributes['dtop'].data.foreach_set('value', (zt - zz).astype(np.float32)); me.update()
    # ---- the ground's colour of the moment
    e = W.era(t); anc = W.ancient(t); bz = W.base(t)
    bare = band_color(bz - 0.004)
    if t < B.flood0: bare = mix(TODAY_EARTH, FERN_FLOOR, 1 - e)
    elif t > B.green0: bare = mix(bare, TODAY_EARTH, e)
    # each new layer's top takes its era (forest floor, ice, steppe, grassland) once its water has drained
    era_green = 0.0; si = W.slot_at(t)
    if si >= 0 and t < B.erode0 + 0.8:
        kind = W.SLOT_ERAS[si]; k = W.sm(W.SLOTS[si][1] + 0.05, W.SLOTS[si][1] + 0.45, t)
        prev = SLOT_GROUND[W.SLOT_ERAS[si - 1]] if si > 0 else bare
        gprev = SLOT_GREEN[W.SLOT_ERAS[si - 1]] if si > 0 else 0.0
        bare = mix(prev, SLOT_GROUND[kind], k); era_green = gprev + (SLOT_GREEN[kind] - gprev) * k
        if t > B.erode0:
            v = W.sm(B.erode0, B.erode0 + 0.8, t); era_green *= 1 - v; bare = mix(bare, band_color(bz - 0.004), v)
    D.setc('ground', bare)
    D.set('green', max(e, 0.9 * anc, era_green) * (1 - 0.8 * max(0.0, W.flood_level(t) + 0.06) / 0.11))
    D.setc('greencol', mix(MOSS, MEADOW, e))
    fl = W.flood_level(t); wet = W.keys(t, [(B.flood0, 0.0), (B.flood2, 1.0), (B.stack1 + 0.6, 0.0)]) if B.flood0 < t < B.stack1 + 0.7 else 0.0
    D.set('wet', max(wet, 0.6 * W.win(t, B.rain0 + 0.5, B.rain1 + 0.4, 0.5), 0.5 * W.win(t, B.rainA0 + 0.5, B.flood0 + 0.5, 0.4)))
    D.set('rw', W.channel(t)[0]); D.set('rockamt', e)
    # ---- water: the river and brook in their bed, the flood over everything
    water_pose(S['water'], t); world_pose(S['world'], t); underside_pose(S['hole'], t)
    D.setc('haze', blend4(t, ((0.66, 0.78, 0.74), (0.34, 0.54, 0.52), (0.72, 0.56, 0.52), (0.72, 0.76, 0.84))))
    D.set('murk', W.sm(-0.05, 0.02, fl)); D.set('walpha', 1.0)
    # ---- the camera holds (a 2 degree sway over the whole film); the light follows the story
    S['cam'].pose(az=S['az0'] + SWAY * math.sin(2 * math.pi * t / W.DURATION))
    el = blend4(t, SUN['el']) - 8.0 * max(W.win(t, B.rain0, B.rain1, 0.8), W.win(t, B.rainA0, B.rainA1, 0.8))
    S['sun'].rotation_euler = (math.radians(90 - el), 0, math.radians(SUN_AZ + 90))
    S['sun'].data.energy = blend4(t, SUN['e']) * (1 - 0.35 * W.win(t, B.rain0, B.rain1, 0.8)); S['sun'].data.color = blend4(t, SUN['col'])
    # ---- life
    LF.plants_pose(S['plants'], t); LF.trees_pose(S['trees'], t); LF.dino_pose(S['dino'], D, t)
    LF.girl_pose(S['girl'], t); bone = LF.dug_bone_pose(S['dug'], t)
    LF.critters_pose(S['critters'], t); LF.birds_pose(S['birds'], t); LF.flutter_pose(S['flutter'], t); LF.eggs_pose(S['eggs'], t); LF.snail_pose(S['snail'], t)
    st = S['story']; ST.peel_pose(st['peel'], D, t); ST.babies_pose(st['babies'], D, t); ST.turtle_pose(st['turtle'], t)
    ST.leaf_pose(st['leaf'], t); ST.skeleton_pose(st['skel'], D, t); ST.mammoths_pose(st['mammoths'], t); ST.saplings_pose(st['saplings'], t)
    S['lens'].pose(t)
    FO.pose(S['fossil'], D, t); rain_pose(S['rain'], t); BK.pose(S['back'], D, t)
    S['words'].pose(t, bone)
    if S.get('art') is not None: S['art'].frame(bpy, ctx, t)
