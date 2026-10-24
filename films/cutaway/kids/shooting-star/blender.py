"""Little Big Questions: What is a shooting star? A SILENT story told by the picture (Cutaway, Fable look, 16:9, 24 fps,
68.4 s). Sam 23 Oct 20:09: no narration; real orchestral music (Grieg, Anitra's Dance, Musopen) and real sound effects carry
it; a few big words set in code. Source of truth: beats.json (11 beats: picture, words, sound, music) and szevents.py (the one
table of every timed event, anchored to the beats).

One fixed view of one lifted slice (a 2 degree sway over the whole film, no cuts). The slice is a hilltop at dusk turning to
night with a family camping on it; the sky above is the stage: the first stars, a magnifier window that shows a star, then a
pebble-sized rock rushing through the layers of the air, and the long streak of light on the music's brightest phrase.
Look: Fable (films/styles/cutaway/art/fable.py through art/_adapter.py), named by KF_ART_NAME; $KF_ART overrides it
($KF_ART=none renders the plain kit materials, for debugging). The night sky is this film's own card (szstory.py), Fable's
season card is hidden.
Files: szworld.py (heights, moods, the clock of beats), szevents.py (the event table), szmats.py (driven materials), szgeo.py
(rigid parts), szlife.py (the camp, the family, the animals, easter eggs, the mascot), szstory.py (the sky: stars, the Moon, the
streak, the window), szback.py (the world behind the block: hills, lake, village, clouds), szwords.py (captions, label), szui.py.
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
import szevents as EV  # noqa: E402

W.set_events(EV.EVENTS)
W.WORD_IN[EV.BEAT_NAMES['send']] = W.B.words_send
W.WORD_IN['streak'] = W.B.peak                     # METEOR! pops on the bright instant, after the streak has crossed the title's place          # the closing question waits for the breath of stillness

import szmats as M  # noqa: E402
import szstory as ST  # noqa: E402
import szback as BK  # noqa: E402
import szlife as LF  # noqa: E402
import szwords as WD  # noqa: E402
from szgeo import Parts, I3, tube, sphere, rx, ry  # noqa: E402

DURATION = W.DURATION
SETTINGS = {'samples': 32, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 6.0, 'adaptive_min_samples': 12,
            'denoising_prefilter': 'ACCURATE'}

AZ0, SWAY = W.VIEW_AZ, 2.0                 # camera azimuth; a 2 degree sway on one slow sine over the whole film
EL, LENS, FILL = 16.0, 50.0, 0.80
CAM_UP = 1.30                          # the aim is lifted (m): the block sits low in the frame and the sky is the stage
SUN_AZ = -118.0                        # the Moon and the fire light the front face
# the light of the moment (dusk, twilight, night, deep night): sun elevation, energy, colour; the paint tint; the haze colour
SUN = {'el': (14.0, 30.0, 52.0, 56.0), 'e': (2.4, 1.6, 1.3, 1.1),
       'col': ((1.0, 0.70, 0.46), (0.86, 0.66, 0.78), (0.62, 0.72, 1.0), (0.58, 0.68, 1.0))}
TINT = ((1.0, 0.80, 0.66), (0.70, 0.62, 0.78), (0.50, 0.58, 0.86), (0.44, 0.52, 0.80))
HAZE = ((0.86, 0.60, 0.58), (0.44, 0.40, 0.62), (0.20, 0.28, 0.50), (0.16, 0.24, 0.46))
LAKE = (((0.74, 0.50, 0.50), (0.90, 0.62, 0.46)), ((0.30, 0.30, 0.52), (0.40, 0.36, 0.56)), ((0.12, 0.22, 0.46), (0.20, 0.34, 0.60)), ((0.10, 0.18, 0.42), (0.16, 0.28, 0.54)))


def mix(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))


def blend4(t, vals):
    w = W.weights(t); a = [np.asarray(v, float) for v in vals]; o = sum(wi * ai for wi, ai in zip(w, a))
    return tuple(float(x) for x in np.atleast_1d(o)) if np.ndim(o) else float(o)


# ============================================================================== build helpers
def capture(L):
    """Remember the top grid and the walls' layout, so frame() can rewrite them for any t."""
    me = L.objects['top'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); top = co.reshape(-1, 3).astype(float)
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
    col = g.ramp(g.math('DIVIDE', g.math('SUBTRACT', z, zf), -zf), [(0.0, (0.07, 0.06, 0.10)), (0.55, (0.16, 0.12, 0.16)), (1.0, (0.28, 0.22, 0.26))])
    n = g.noise(P, 9.0, 3.0); col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.35), col, (0.05, 0.03, 0.05, 1))
    peb = g.math('LESS_THAN', g.voronoi(P, 14.0, 'F1').outputs['Distance'], 0.12)
    col = g.mix(g.math('MULTIPLY', peb, 0.5), col, cw.srgb((0.40, 0.38, 0.40)))
    col = M._tinted(g, D, col)
    cw._finish(g, g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.95}))
    V = []; F = []
    def wall(P0, P1, normal, n=40, rows=10):
        o = len(V)
        for i in range(n + 1):
            x, y = P0[0] + (P1[0] - P0[0]) * i / n, P0[1] + (P1[1] - P0[1]) * i / n
            zt = float(W.land_h(np.array([x]), np.array([y]))[0])
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


def build_world(kit, D, top_mat, res=0.1):
    """The land around and behind the block, out to the hills: one grid at the same heights (szworld.top_h) and in the
    same ground paint, minus the block's hole; the lake's basin is carved into it."""
    xs = np.round(np.arange(-12.0, 12.0 + 1e-6, res), 4); ys = np.round(np.arange(-9.0, 14.0 + 1e-6, res), 4)
    X, Y = np.meshgrid(xs, ys); nx, ny = len(xs), len(ys); ii = np.arange(nx * ny).reshape(ny, nx)
    q = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
    cx = (X[:-1, :-1] + X[1:, 1:]).ravel() / 2; cy = (Y[:-1, :-1] + Y[1:, 1:]).ravel() / 2
    keep = ~W.in_hole(cx, cy); q = q[keep]      # the hole the slice was lifted from
    used = np.unique(q); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used)); q = remap[q]
    P = np.column_stack([X.ravel(), Y.ravel()])[used]
    attrs = {'far': ('FLOAT', W.far(P[:, 0], P[:, 1]))}
    V = np.column_stack([P, W.land_h(P[:, 0], P[:, 1])])
    ob = cw.mk_mesh(kit.bpy, 'fs_world', V, q.tolist(), [top_mat], None, True, kit.coll, attrs)
    return {'ob': ob, 'P': P}



def build_lake(kit, D):
    """The lake in the land far behind on the left: a polar grid of water that follows the land's own curve, a little wider than
    its basin (the land hides the rest)."""
    nr, ns = 8, 72; V = []; F = []
    for i in range(nr + 1):
        r = 1.25 * i / nr
        for k in range(ns):
            a = 2 * math.pi * k / ns; x = W.LAKE_C[0] + r * W.LAKE_R[0] * math.cos(a); y = W.LAKE_C[1] + r * W.LAKE_R[1] * math.sin(a)
            V.append((x, y, float(W.lake_z(np.array([x]), np.array([y]))[0])))
    for i in range(nr):
        for k in range(ns): a = i * ns + k; b_ = i * ns + (k + 1) % ns; F.append((a, b_, b_ + ns, a + ns))
    ob = cw.mk_mesh(kit.bpy, 'fs_lakeplane', V, F, [M.mat_water(kit, D)], None, False, kit.coll); ob.visible_shadow = False
    return ob


# ============================================================================== harness entry points
def build(bpy, ctx):
    rng = np.random.default_rng(5)
    kit = cw.Kit(bpy, seed=5, loop=W.DURATION); D = M.Drive()
    L = cw.block(kit, size=(W.SX, W.SY), depth=-W.ZB, strata=W.STRATA, top=lambda x, y: W.slice_h(x, y, 0.0), water=None, seed=5, season='summer',
                 res=0.025, grass=0, trees=0, boulders=0, flowers=0, under=False, lilies=0, reeds=0, name='fs_block')
    geo = capture(L); hole = build_hole(kit, D, rng)
    L.objects['top'].data.materials[0] = M.mat_top(kit, D)
    world = build_world(kit, D, L.objects['top'].data.materials[0]); lake = build_lake(kit, D)
    cw.studio(kit, color=(0.93, 0.90, 0.84), key_az=SUN_AZ, key_el=45.0, key=3.2, angle=6.0, fill=0.8, land=L)
    cam = cw.camera(kit, L, '16:9' if ctx['W'] >= ctx['H'] else '9:16', az=AZ0, el=EL, lens=LENS, fill=FILL, top_extra=0.75, bottom_extra=W.GAP + 0.15)
    cam.pose(target=cam.target + np.array([0.0, 0.0, -W.ZB + W.GAP + CAM_UP]))
    back = BK.build(kit, D, cam, ctx)
    plants = LF.build_plants(kit, L, D, np.random.default_rng(7)); trees = LF.build_trees(kit, D)
    people = {sp.name: LF.build_person(kit, D, sp) for sp in LF.PEOPLE}
    camp = LF.build_camp(kit, D); fire = LF.build_fire(kit, D); eggs = LF.build_eggs(kit, D); owl = LF.owl_tree_parts(kit, D)
    flies = LF.build_fireflies(kit, D, np.random.default_rng(19)); snail = LF.build_snail(kit, D)
    words = WD.Words(kit, D, cam, ROOT)
    B = W.B
    sky = ST.Sky(kit, D, cam, ctx, np.random.default_rng(11)); win = ST.Window(kit, D, cam, np.random.default_rng(13))
    streaks = [ST.Streak(kit, D, cam, 'main', ST.PATH, B.streak0, B.peak - B.streak0, 1.5, 0.016, 1.0, 26, B.peak, 1.3),
               ST.Streak(kit, D, cam, 'zip', ((-0.15, 1.0), (-0.55, 0.82), (-1.15, 0.52)), B.streak1_0, 0.9, 0.35, 0.010, 0.7, 8, None, 0.7),
               ST.Streak(kit, D, cam, 'last', ((-0.90, 0.56), (-1.05, 0.50), (-1.25, 0.40)), B.last0, 0.8, 0.3, 0.007, 0.5, 5, None, 0.5)]
    crisp = words.obs + win.crisp + sky.crisp + [o for s_ in streaks for o in s_.crisp]
    cw.apply_cycles(bpy); sc = bpy.context.scene; sc.cycles.transparent_max_bounces = 24
    S = {'kit': kit, 'D': D, 'land': L, 'geo': geo, 'world': world, 'hole': hole, 'lake': lake, 'words': words, 'back': back, 'plants': plants, 'trees': trees, 'people': people, 'camp': camp, 'fire': fire, 'eggs': eggs, 'owl': owl, 'flies': flies, 'snail': snail, 'sky': sky, 'win': win, 'streaks': streaks,
         'cam': cam, 'az0': cam.az, 'sun': bpy.data.objects['cw_sun']}
    frame(bpy, ctx, S, 0, 0.0)
    art = os.environ.get('KF_ART', globals().get('KF_ART_NAME'))
    if art and art != 'none':
        import importlib.util
        sp = importlib.util.spec_from_file_location('kf_art_adapter', os.path.join(ROOT, 'films', 'styles', 'cutaway', 'art', '_adapter.py'))
        ad = importlib.util.module_from_spec(sp); sp.loader.exec_module(ad)
        S['art'] = ad.attach(bpy, ctx, art, kit=kit, land=L, cam=cam, settings=SETTINGS, strata=W.STRATA, words=crisp)
        for o in bpy.data.objects:
            if o.name == 'fable_card': o.hide_render = True
        S['art']._fable['card'] = {}
        S['art'].frame(bpy, ctx, 0.0)
    return S


def frame(bpy, ctx, S, i, t):
    kit, D = S['kit'], S['D']; kit.update(t); B = W.B
    # ---- the land: the slice's top and walls follow the lift
    tp = S['geo']['top']; z = W.top_h(tp[:, 0], tp[:, 1], t); co = tp.copy(); co[:, 2] = z
    me = S['land'].objects['top'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel()); me.update()
    wl = S['geo']['walls']; uu = S['geo']['uu']; zt = W.slice_h(wl[:, 0], wl[:, 1], t); zz = zt + (W.ZB - zt) * uu
    co = wl.copy(); co[:, 2] = zz + W.lift(t); me = S['land'].objects['walls'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel())
    me.attributes['sd'].data.foreach_set('value', (W.Z_MAX - zz).astype(np.float32)); me.attributes['dtop'].data.foreach_set('value', (zt - zz).astype(np.float32)); me.update()
    underside_pose(S['hole'], t)
    # ---- the light of the moment
    D.setc('tint', blend4(t, TINT)); D.setc('haze', blend4(t, HAZE)); D.set('night', W.night(t))
    D.setc('lake_a', blend4(t, [a for a, b in LAKE])); D.setc('lake_b', blend4(t, [b for a, b in LAKE]))
    # ---- the camera holds (a 2 degree sway over the whole film); the light follows the story
    S['cam'].pose(az=S['az0'] + SWAY * math.sin(2 * math.pi * t / W.DURATION))
    el = blend4(t, SUN['el'])
    S['sun'].rotation_euler = (math.radians(90 - el), 0, math.radians(SUN_AZ + 90))
    S['sun'].data.energy = blend4(t, SUN['e']); S['sun'].data.color = blend4(t, SUN['col'])
    LF.plants_pose(S['plants'], t); LF.trees_pose(S['trees'], t)
    hands = {n_: LF.person_pose(p_, t) for n_, p_ in S['people'].items()}
    LF.camp_pose(S['camp'], t); LF.fire_pose(S['fire'], D, t); LF.eggs_pose(S['eggs'], D, t, hands); LF.owl_pose(S['owl'], t, None)
    LF.flies_pose(S['flies'], t); LF.snail_pose(S['snail'], t)
    BK.pose(S['back'], D, t); S['sky'].pose(t, W, W.win(t, B.star_pulse, B.star_pulse + 1.6, 0.5)); S['win'].pose(t)
    for s_ in S['streaks']: s_.pose(t)
    S['words'].pose(t, None)
    if S.get('art') is not None: S['art'].frame(bpy, ctx, t)
