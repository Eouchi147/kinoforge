"""Little Big Questions, film 2: How is a volcano born? A SILENT story told by the picture (Cutaway, Fable look, 16:9, 24 fps,
72.3 s). Sam 23 Oct 20:09: no narration; real orchestral music and real sound effects carry it; a few big words set in code.
Source of truth: beats.json (11 beats: picture, words, sound, music).

One fixed view of one block (a 2 degree sway over the whole film, no cuts): a slice of a young volcano island, lifted out of a
sunny sea a little above the hole (a column of sea) it came from. The slice is cut through the volcano's axis, so the front
face is a cross-section: layers of lava, the crack, the glowing magma chamber. The story (facts: docs/research/KIDS_FACTS_2026-10.md
1.2.1): magma deep down is lighter than the rock and rises; it finds a crack; gas bubbles push like a shaken fizzy drink;
it bursts out of the TOP and is now lava; it cools into brand new rock; each eruption adds a layer and the mountain grows;
plants find a home and slowly it turns to rich soil; the islands of Hawaii were built this way.

EVERY event of the picture is anchored to a beat in the one table below (EVENTS: beat, fraction of the way through it); change
beats.json and the whole film re-times itself. The music's big entrance (31.4 s) is the first eruption, its eight orchestral
hits (43.4 to 56.8 s) are the eight more, the last on the piece's own final crash.
Look: Fable (films/styles/cutaway/art/fable.py through art/_adapter.py), named by the module global KF_ART_NAME.
Files: szworld.py (island, layers, magma level, clock of beats, moods), szmats.py (materials), szgeo.py (rigid parts), szvolc.py (the
cut face, flows, fountains, the sea of the slice, bottle and sandcastle), szlife.py (plants, palms, gulls, dolphins, boat, easter eggs,
the surfing snail), szback.py (the sea to the horizon, far islands, clouds, the gold rings), szwords.py and szui.py (captions, clock,
label), this file (the event table, build and frame).
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
# Beats: hook, magma, rises, gas, erupt, flows, layers, growth, rest, islands, send.
# ==============================================================================================================
BEAT_NAMES = {k: k for k in ('hook', 'magma', 'rises', 'gas', 'erupt', 'flows', 'layers', 'growth', 'rest', 'islands', 'send')}
EVENTS = {
    # hook: the beach ball rolls in
    'ball0': ('hook', 0.08163), 'ball1': ('hook', 0.4898), 'surf0': ('hook', 0.0),
    # magma: the chamber glows; MAGMA and its ribbon (2.9 s)
    'glow0': ('magma', 0.0), 'label0': ('magma', 0.09722), 'label1': ('magma', 0.90278),
    # rises: the magma front creeps up the crack (lighter than the rock); gas: bubbles swell, the bottle is shaken, the slice trembles
    'rise0': ('rises', 0.00833), 'rise1': ('gas', 0.0), 'gas0': ('gas', 0.04591), 'gas1': ('gas', 0.96419), 'rumble0': ('gas', 0.18365),
    'rumble1': ('gas', 0.96419), 'bottle0': ('gas', 0.22957), 'fly0': ('gas', 0.59688),
    # the nine eruptions: the music's big entrance (31.39 s), then its eight hits (43.35, 44.31, 47.28, 48.22, 51.15, 52.09, 53.04) and the final crash (56.82)
    'e0': ('erupt', 0.0), 'e1': ('layers', 0.175), 'e2': ('layers', 0.335), 'e3': ('layers', 0.83), 'e4': ('layers', 0.98667),
    'e5': ('growth', 0.27941), 'e6': ('growth', 0.37157), 'e7': ('growth', 0.46471), 'e8': ('growth', 0.83529),
    # the clock spins while the layers pile up
    'stack0': ('layers', 0.11667), 'stack1': ('growth', 0.90196),
    # rest: plants find a home (green from the shore up), the soil forms; islands: a gold ring round each island in turn
    'rest0': ('rest', 0.04), 'green1': ('rest', 0.93333), 'soil0': ('rest', 0.2), 'soil1': ('islands', 0.0),
    'ring0': ('islands', 0.13333), 'ring1': ('islands', 0.3), 'ring2': ('islands', 0.46667), 'ring3': ('islands', 0.63333),
    # the snail waves
    'wave0': ('send', 0.18182),
    # unused names of the caption kit's clock (the volcano film needs only the layers' clock): parked long before the film
    'rw0': ('hook', -100.0), 'rw1': ('hook', -99.0), 'rain0': ('hook', -100.0), 'erode1': ('hook', -99.0),
}
W.set_events({k: (BEAT_NAMES[b], u) for k, (b, u) in EVENTS.items()})
W.WORD_IN['flows'] = 38.5           # NEW ROCK waits until the first lava has begun to cool

import szmats as M  # noqa: E402
import szlife as LF  # noqa: E402
import szvolc as VO  # noqa: E402
import szback as BK  # noqa: E402
import szwords as WD  # noqa: E402
from szgeo import Parts, I3, tube, sphere, rx, ry, rz  # noqa: E402

DURATION = W.DURATION
SETTINGS = {'samples': 32, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 6.0, 'adaptive_min_samples': 12,
            'denoising_prefilter': 'ACCURATE'}

AZ0, SWAY = W.VIEW_AZ, 2.0
EL, LENS, FILL = 27.0, 50.0, 0.84
CAM_DZ = 0.12
SUN_AZ = -118.0
SUN = {'el': (54.0, 50.0, 30.0, 50.0), 'e': (3.4, 3.4, 3.0, 3.4), 'col': ((1.0, 0.97, 0.90), (1.0, 0.96, 0.86), (1.0, 0.80, 0.60), (1.0, 0.98, 0.94))}


def blend4(t, vals):
    w = W.weights(t); a = [np.asarray(v, float) for v in vals]; o = sum(wi * ai for wi, ai in zip(w, a))
    return tuple(float(x) for x in np.atleast_1d(o)) if np.ndim(o) else float(o)


def far(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    d = np.hypot(np.maximum(np.abs(x) - W.HX, 0), np.maximum(np.abs(y) - W.HY, 0))
    return np.where(W.in_block(x, y), 0.0, 0.18 + 0.62 * W.smooth(0.0, 9.0, d))


# ============================================================================== build helpers
def capture(L):
    """Remember the top grid and the walls' layout, so frame() can rewrite them for any t; the ground's static attributes."""
    me = L.objects['top'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); top = co.reshape(-1, 3).astype(float)
    x, y = top[:, 0], top[:, 1]; hf = W.h_final(x, y)
    for name, val in (('bch', W.smooth(0.15, 0.08, hf)), ('gq', np.clip(W.rr(x, y) / W.RS, 0, 1)), ('gperm', np.zeros(n)), ('far', np.zeros(n)), ('dp', W.smooth(0.0, -0.22, hf))):
        a = me.attributes.new(name, 'FLOAT', 'POINT'); a.data.foreach_set('value', np.asarray(val, np.float32))
    me = L.objects['walls'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); wl = co.reshape(-1, 3).astype(float)
    zt0 = W.h_now(wl[:, 0], wl[:, 1], 0.0); uu = np.clip((wl[:, 2] - zt0) / (W.ZB - zt0), 0, 1)
    return {'top': top, 'walls': wl, 'uu': uu}


def build_hole(kit, D, rng):
    """The hole the slice was lifted from, directly beneath it: a column of sea, as deep as the slice (turquoise at the top,
    deep blue at the bottom, a sandy floor), 0.10 m wider than the slice on every side; seaweed, shells and dripping drops
    hang off the slice's underside."""
    bpy = kit.bpy; X0, X1, Y0, Y1 = -W.HX - W.HM, W.HX + W.HM, -W.HY - W.HM, W.HY + W.HM; zf = W.HOLE_FLOOR
    m = cw._new_mat(bpy, 'fs_holewall'); g = cw.G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); P = tc.outputs['Object']; sx = g.sep(P); z = sx[2]
    k = g.math('DIVIDE', g.math('SUBTRACT', z, 0.0), zf, clamp=True)
    col = g.ramp(k, [(0.0, (0.12, 0.66, 0.74)), (0.35, (0.07, 0.46, 0.64)), (0.75, (0.04, 0.24, 0.46)), (1.0, (0.03, 0.13, 0.30))])
    n1 = g.noise(g.comb(g.math('ADD', sx[0], sx[1]), g.math('MULTIPLY', z, 9.0), 0.0), 2.0, 3.0)
    col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', n1.outputs['Fac'], 0.55), 4.0, clamp=True), 0.28), col, cw.srgb((0.70, 0.95, 0.95)))
    cw._finish(g, g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}))
    V = []; F = []
    def wall(P0, P1, normal, n=40, rows=10):
        o = len(V)
        for i in range(n + 1):
            x, y = P0[0] + (P1[0] - P0[0]) * i / n, P0[1] + (P1[1] - P0[1]) * i / n
            zt = float(W.land_h(np.array([x]), np.array([y]), 0.0)[0]) * 0.0
            for r in range(rows + 1): V.append((x, y, zt + (zf - zt) * r / rows))
        for i in range(n):
            for r in range(rows):
                a = o + i * (rows + 1) + r; c = o + (i + 1) * (rows + 1) + r; q = (a, a + 1, c + 1, c)
                p0, p1, p2 = np.array(V[q[0]]), np.array(V[q[1]]), np.array(V[q[2]])
                F.append(q if np.cross(p1 - p0, p2 - p0) @ np.asarray(normal) > 0 else q[::-1])
    wall((X0, Y1), (X1, Y1), (0, -1, 0)); wall((X0, Y0), (X0, Y1), (1, 0, 0)); wall((X1, Y0), (X1, Y1), (-1, 0, 0)); wall((X0, Y0), (X1, Y0), (0, 1, 0))
    o = len(V); V += [(X0, Y0, zf), (X1, Y0, zf), (X1, Y1, zf), (X0, Y1, zf)]; F.append((o, o + 1, o + 2, o + 3))
    hole = cw.mk_mesh(bpy, 'fs_hole', V, F, [m], None, False, kit.coll)
    pr = Parts('fs_underside'); items = []
    mats = [M.paint(kit, D, 'sz_weed', (0.18, 0.56, 0.36), noise=0.0), M.paint(kit, D, 'sz_shell', (0.99, 0.80, 0.70), noise=0.0), M.paint(kit, D, 'sz_drop', (0.62, 0.90, 1.0), noise=0.0)]
    for k in range(60):
        side = k % 4; u = rng.uniform(0.04, 0.96)
        x, y = [(-W.HX + 2 * W.HX * u, -W.HY + 0.02), (W.HX - 0.02, -W.HY + 2 * W.HY * u), (-W.HX + 2 * W.HX * u, W.HY - 0.02), (-W.HX + 0.02, -W.HY + 2 * W.HY * u)][side]
        x += rng.uniform(-0.02, 0.15) * (1 if x < 0 else -1) * 0.3; L = rng.uniform(0.12, 0.34); b = rng.uniform(-0.05, 0.05, 2)
        pts = [(0, 0, 0.01), (b[0] * 0.4, b[1] * 0.4, -L * 0.4), (b[0], b[1], -L * 0.75), (b[0] * 1.3, b[1] * 1.3, -L)]
        v, f = tube(pts, [0.013, 0.010, 0.007, 0.003], 6); items.append(('weed', pr.add(v, f, 0), x, y, rng.uniform(0, 6.28)))
    for k in range(18):
        x, y = rng.uniform(-W.HX + 0.05, W.HX - 0.05), rng.uniform(-W.HY + 0.05, W.HY - 0.05)
        if k % 2: x = np.sign(x) * (W.HX - rng.uniform(0.02, 0.2))
        else: y = np.sign(y) * (W.HY - rng.uniform(0.02, 0.2))
        r = rng.uniform(0.022, 0.04); v, f = sphere((0, 0, -r * 0.4), (r, r * 0.9, r * 0.7), 1); items.append(('shell', pr.add(v, f, 1), x, y, 0.0))
    for k in range(12):
        x, y = rng.uniform(-W.HX + 0.1, W.HX - 0.1), -W.HY + rng.uniform(0.02, 0.5); v, f = sphere((0, 0, 0), (0.012, 0.012, 0.016), 1)
        items.append(('drop', pr.add(v, f, 2), x, y, rng.uniform(0, 1)))
    pr.build(bpy, mats, kit.coll)
    return {'hole': hole, 'parts': pr, 'items': items}


def underside_pose(H, t):
    pr = H['parts']; zb = W.ZB + W.lift(t)
    for kind, j, x, y, ph in H['items']:
        if kind == 'weed': pr.set(j, (x, y, zb), rx(0.12 * math.sin(0.8 * t + ph)) @ ry(0.10 * math.cos(0.6 * t + ph)))
        elif kind == 'shell': pr.set(j, (x, y, zb))
        else:
            T = 4.0; age = ((t / T + ph) % 1.0) * T; fall = 0.5 * 9.8 * 0.25 * age * age; z = zb - fall
            if age < 1.6 and z > W.HOLE_FLOOR: pr.set(j, (x, y, z), I3, 1.0)
            else: pr.hide(j)
    pr.commit()


def build_world(kit, D, top_mat, water_mat, res=0.1):
    """The sea floor and the older islands round the block, out to the horizon (one grid, same ground paint), minus the hole;
    and the sea's own surface (a translucent sheet at sea level, curving away), also minus the hole."""
    xs = np.round(np.arange(-12.0, 12.0 + 1e-6, res), 4); ys = np.round(np.arange(-9.0, 14.0 + 1e-6, res), 4)
    X, Y = np.meshgrid(xs, ys); nx, ny = len(xs), len(ys); ii = np.arange(nx * ny).reshape(ny, nx)
    q = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
    cx = (X[:-1, :-1] + X[1:, 1:]).ravel() / 2; cy = (Y[:-1, :-1] + Y[1:, 1:]).ravel() / 2
    keep = ~W.in_hole(cx, cy); q = q[keep]
    used = np.unique(q); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used)); q = remap[q]
    P = np.column_stack([X.ravel(), Y.ravel()])[used]
    ab = W.island_bump(P[:, 0], P[:, 1])
    attrs = {'bch': ('FLOAT', W.smooth(0.10, 0.05, ab)), 'gq': ('FLOAT', np.ones(len(P))), 'gperm': ('FLOAT', W.smooth(0.07, 0.14, ab)), 'far': ('FLOAT', far(P[:, 0], P[:, 1])), 'dp': ('FLOAT', W.smooth(0.02, -0.20, ab))}
    V = np.column_stack([P, W.land_h(P[:, 0], P[:, 1])])
    ob = cw.mk_mesh(kit.bpy, 'fs_world', V, q.tolist(), [top_mat], None, True, kit.coll, attrs)
    sea = cw.mk_mesh(kit.bpy, 'fs_seaworld', np.column_stack([P, W.sea_h(P[:, 0], P[:, 1], 0.0)]), q.tolist(), [water_mat], None, False, kit.coll); sea.visible_shadow = False
    return {'ob': ob, 'P': P, 'sea': sea}


def world_pose(Wd, t):
    P = Wd['P']; me = Wd['sea'].data
    me.vertices.foreach_set('co', np.column_stack([P, W.sea_h(P[:, 0], P[:, 1], t)]).astype(np.float32).ravel()); me.update()


# ============================================================================== harness entry points
def build(bpy, ctx):
    rng = np.random.default_rng(5)
    kit = cw.Kit(bpy, seed=5, loop=W.DURATION); D = M.Drive()
    L = cw.block(kit, size=(W.SX, W.SY), depth=-W.ZB, strata=W.STRATA, top=lambda x, y: W.h_now(x, y, 0.0), water=None, seed=5, season='summer',
                 res=0.025, grass=0, trees=0, boulders=0, flowers=0, under=False, lilies=0, reeds=0, name='fs_block')
    geo = capture(L); hole = build_hole(kit, D, rng)
    L.objects['top'].data.materials[0] = M.mat_land(kit, D)
    water = VO.build_water(kit, D)
    seamat = water['top'].data.materials[0]
    world = build_world(kit, D, L.objects['top'].data.materials[0], seamat)
    plants = LF.build_plants(kit, L, D, rng); palms = LF.build_palms(kit, D, rng)
    face = VO.build_face(kit, D, rng); flows = VO.build_flows(kit, D); fount = VO.build_fountain(kit, D, rng); bottle = VO.build_bottle(kit, D, rng)
    gulls = LF.build_gulls(kit, D, rng); dolph = LF.build_dolphins(kit, D); boat = LF.build_boat(kit, D); eggs = LF.build_eggs(kit, D); snail = LF.build_snail(kit, D)
    cw.studio(kit, color=(0.93, 0.90, 0.84), key_az=SUN_AZ, key_el=45.0, key=3.2, angle=6.0, fill=0.8, land=L)
    cam = cw.camera(kit, L, '16:9' if ctx['W'] >= ctx['H'] else '9:16', az=AZ0, el=EL, lens=LENS, fill=FILL, top_extra=0.75, bottom_extra=W.GAP + 0.15)
    cam.pose(target=cam.target + np.array([0.0, 0.0, -W.ZB + W.GAP + CAM_DZ]))
    back = BK.build(kit, D, cam, ctx)
    words = WD.Words(kit, D, cam, ROOT)
    cw.apply_cycles(bpy); sc = bpy.context.scene; sc.cycles.transparent_max_bounces = 24
    S = {'kit': kit, 'D': D, 'land': L, 'geo': geo, 'water': water, 'world': world, 'hole': hole, 'plants': plants, 'palms': palms, 'face': face, 'flows': flows,
         'fount': fount, 'bottle': bottle, 'gulls': gulls, 'dolph': dolph, 'boat': boat, 'eggs': eggs, 'snail': snail, 'back': back, 'words': words,
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
    kit, D = S['kit'], S['D']; kit.update(t); B = W.B; lf = W.lift(t)
    # ---- the island: top and walls follow the layers; the cut face's bands follow the same shells
    tp = S['geo']['top']; z = W.h_now(tp[:, 0], tp[:, 1], t) + lf; co = tp.copy(); co[:, 2] = z
    me = S['land'].objects['top'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel()); me.update()
    wl = S['geo']['walls']; uu = S['geo']['uu']; zt = W.h_now(wl[:, 0], wl[:, 1], t); zz = zt + (W.ZB - zt) * uu
    co = wl.copy(); co[:, 2] = zz + lf; me = S['land'].objects['walls'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel())
    me.attributes['sd'].data.foreach_set('value', W.sd_wall(wl[:, 0], wl[:, 1], zz).astype(np.float32)); me.attributes['dtop'].data.foreach_set('value', (zt - zz).astype(np.float32)); me.update()
    # ---- the paint of the moment
    D.set('front', W.keys(t, [(B.rest0, 0.0), (B.green1, 1.12)])); D.set('walpha', 1.0)
    D.setc('haze', blend4(t, ((0.40, 0.70, 0.74), (0.40, 0.72, 0.76), (0.62, 0.66, 0.66), (0.50, 0.74, 0.80))))
    # ---- water, the sea round, the cut face, the volcano
    VO.water_pose(S['water'], t); LF_world = S['world']; world_pose(LF_world, t); underside_pose(S['hole'], t)
    VO.face_pose(S['face'], D, t); VO.flows_pose(S['flows'], D, t); VO.fountain_pose(S['fount'], t); bottle_pt = VO.bottle_pose(S['bottle'], t)
    # ---- the camera holds (a 2 degree sway); the light follows the story (a warm flush at every eruption)
    S['cam'].pose(az=S['az0'] + SWAY * math.sin(2 * math.pi * t / W.DURATION))
    S['sun'].rotation_euler = (math.radians(90 - blend4(t, SUN['el'])), 0, math.radians(SUN_AZ + 90))
    S['sun'].data.energy = blend4(t, SUN['e']); S['sun'].data.color = blend4(t, SUN['col'])
    # ---- life
    LF.plants_pose(S['plants'], t); LF.palms_pose(S['palms'], t); LF.gulls_pose(S['gulls'], t); LF.dolphins_pose(S['dolph'], t); LF.boat_pose(S['boat'], t)
    LF.eggs_pose(S['eggs'], t); LF.snail_pose(S['snail'], t)
    BK.pose(S['back'], D, t)
    chamber = np.array([W.XC, W.YC - 0.003, W.CH_Z + lf])
    S['words'].pose(t, chamber)
    if S.get('art') is not None: S['art'].frame(bpy, ctx, t)
