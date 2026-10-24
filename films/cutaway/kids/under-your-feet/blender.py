"""Little Big Questions: Who lives under your feet? A SILENT story told by the picture (Cutaway, Fable look, 16:9, 24 fps,
74 s). No narration; real orchestral music (Mozart, The Marriage of Figaro, overture, Musopen, CC0) and real sound effects
carry it; a few big words set in code. Source of truth: beats.json (11 beats: picture, words, sound, music).

One fixed view of one block (a 2 degree sway over the whole film, no cuts): a slice of a park lawn with a big tree, lifted
out of the land; the years pass on top (the seasons loop) while a tiny cicada nymph waits underground among its busy
neighbours (worms, ants, a mole, grubs, the tree's roots) and then climbs out, all together, and sings. EVERY event of the
picture is anchored to a beat in the one table below (EVENTS: beat, fraction of the way through it); change beats.json and
the whole film re-times itself. The words come from beats.json too (szwords.py).
Look: Fable (films/styles/cutaway/art/fable.py through art/_adapter.py), named by the module global KF_ART_NAME.
Files: szworld.py (heights, the clock of beats, the years and seasons), szmats.py (driven materials), szgeo.py (rigid parts),
szpark.py (the lawn, the big tree, the park and its people, the easter eggs on top, the snail), szunder.py (the cut face:
tunnels, roots, the neighbours, the easter eggs underground), szcic.py (the cicada thread: egg, nymph, the wait, the climb,
the shell, the song), szback.py (the world behind the block), szwords.py (captions, clock, label), this file.
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
# Beats: hook, scurry, reveal, meet, years, stir, emerge, climb, split, sing, send.
# ==============================================================================================================
BEAT_NAMES = {'hook': 'hook', 'scurry': 'scurry', 'reveal': 'reveal', 'meet': 'meet', 'years': 'years', 'stir': 'stir',
              'emerge': 'emerge', 'climb': 'climb', 'split': 'split', 'sing': 'sing', 'send': 'send'}
# Absolute-time helpers: most events are written as seconds of the film (the music is timed in seconds); `T(s)` converts to
# (beat, u) so a re-timed beats.json moves them with their beat.
EVENTS = {}


def _beat_of(s):
    for b in W.BEATS:
        if b['t0'] - 1e-6 <= s < b['t1'] - 1e-6: return b['name'], (s - b['t0']) / (b['t1'] - b['t0'])
    b = W.BEATS[-1]; return b['name'], (s - b['t0']) / (b['t1'] - b['t0'])


def T(**kw):
    """EVENTS from film seconds (designed against the first music edit): each is stored as (beat name, fraction)."""
    for k, s in kw.items(): EVENTS[k] = _beat_of(s)


# ---- the egg and the first steps (hook, scurry): the egg on its twig glints, cracks, the nymph tumbles, walks to the hole
T(egg_glint0=0.8, crack0=5.3, crack1=5.7, fall0=5.7, fall1=6.35, walk0=6.35, walk1=7.9, dive0=7.9, dive1=8.2,
  shaft0=8.2, shaft1=12.3)                 # the shaft: the nymph digs down the cut face (reaches its root at 12.3)
# ---- the reveal (first tutti burst at 8.75): tunnels glow open, neighbours pop in
T(reveal0=8.75, tun_worm0=8.80, tun_worm1=9.9, tun_ant0=9.05, tun_ant1=10.4, tun_mole0=9.3, tun_mole1=10.2, tun_grub0=9.6, tun_grub1=10.4,
  pop_worm=8.9, pop_ant=9.3, pop_mole=9.6, pop_grub=10.0, roots_on0=10.4, roots_on1=11.6)
# ---- meet: the nymph hooks on and sips (12.3), the label (14.6 to 17.9)
T(settle0=12.3, settle1=13.3, label0=14.6, label1=17.9)
# ---- years (the seasons run from the start of meet to the end of years; the clock races in years), 22.15 to 27.6
T(yr0=14.25, yr1=27.6, stack0=22.15, stack1=27.6, rw0=-10.0, rw1=-10.0, rain0=-10.0, erode1=-10.0)
# ---- stir: the soil warms, the nymphs unhook, crawl to the shaft (28.4 to 34.0)
T(warm0=27.8, warm1=32.0, unhook0=28.4, gather0=29.2, gather1=33.4, up0=32.6)
# ---- emerge (finale tutti at film 34.0): they pop out of the lawn and march to the tree
T(pop0=34.0, pop1=34.5, march0=36.5, march1=42.0, bird_up=34.2, look0=34.4)
# ---- climb (43.6 to 55.55) and split (55.55 to 59.7), sing (59.7)
T(climb0=42.4, climb1=54.0, crack_shell0=55.55, ease0=56.0, ease1=58.8, open0=59.7, open1=60.1, song0=60.1, final=68.05, sun_gold0=59.7)
# ---- send
T(lie0=69.0, lie1=70.4, wave0=69.5)
W.set_events({k: (BEAT_NAMES[b], u) for k, (b, u) in EVENTS.items()})
W.WORD_IN[BEAT_NAMES['stir']] = W.B.gather0 - 0.2
W.WORD_IN[BEAT_NAMES['send']] = W.B.final            # the closing question waits for the last chord

import szmats as M  # noqa: E402
import szpark as PK  # noqa: E402
import szunder as UG  # noqa: E402
import szcic as CI  # noqa: E402
import szback as BK  # noqa: E402
import szwords as WD  # noqa: E402
from szgeo import Parts, I3, tube, sphere, rx, ry  # noqa: E402

DURATION = W.DURATION
SETTINGS = {'samples': 20, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 6.0, 'adaptive_min_samples': 12,
            'denoising_prefilter': 'ACCURATE'}

AZ0, SWAY = W.VIEW_AZ, 2.0                 # camera azimuth; a 2 degree sway on one slow sine over the whole film
EL, LENS, FILL = 21.0, 50.0, 0.92
CAM_DZ = 0.12                          # extra lift of the aim (m)
SUN_AZ = -118.0                        # sun from the front left, so the front face takes the light
# sun per season (spring, summer, autumn, winter): elevation, energy, colour
SUN = {'el': (50.0, 58.0, 30.0, 24.0), 'e': (3.3, 3.5, 3.0, 2.7),
       'col': ((1.0, 0.97, 0.90), (1.0, 0.96, 0.86), (1.0, 0.80, 0.58), (0.90, 0.94, 1.0))}
EARTH = (0.46, 0.34, 0.24)
GREEN = ((0.52, 0.80, 0.34), (0.40, 0.70, 0.30), (0.66, 0.64, 0.26), (0.90, 0.94, 1.0))       # the lawn through the seasons
HAZE = ((0.66, 0.80, 0.74), (0.64, 0.78, 0.72), (0.76, 0.68, 0.58), (0.78, 0.82, 0.90))


def mix(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))


def blend4(t, vals):
    w = W.weights(t); a = [np.asarray(v, float) for v in vals]; o = sum(wi * ai for wi, ai in zip(w, a))
    return tuple(float(x) for x in np.atleast_1d(o)) if np.ndim(o) else float(o)


# ============================================================================== build helpers
def capture(L):
    """Remember the top grid and the walls' layout, so frame() can rewrite them for any t."""
    me = L.objects['top'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); top = co.reshape(-1, 3).astype(float)
    a = me.attributes.new('rd', 'FLOAT', 'POINT'); a.data.foreach_set('value', np.full(len(top), 9.0, np.float32))
    a = me.attributes.new('rk', 'FLOAT', 'POINT'); a.data.foreach_set('value', np.zeros(len(top), np.float32))
    a = me.attributes.new('far', 'FLOAT', 'POINT'); a.data.foreach_set('value', np.zeros(len(top), np.float32))
    me = L.objects['walls'].data; n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); wl = co.reshape(-1, 3).astype(float)
    zt0 = W.slice_h(wl[:, 0], wl[:, 1], 0.0); uu = np.clip((wl[:, 2] - zt0) / (W.ZB - zt0), 0, 1)        # the slice's own frame
    return {'top': top, 'walls': wl, 'uu': uu}


def build_hole(kit, D, rng):
    """The hole the slice was lifted from, directly beneath it: dark earthy walls, a dark floor, as deep as the slice, with
    roots and pebbles hanging off the slice's underside and a little soil trickling now and then."""
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
            T_ = 4.5; age = ((t / T_ + ph) % 1.0) * T_; fall = 0.5 * 9.8 * 0.25 * age * age; z = zb - fall
            if age < 1.6 and z > W.HOLE_FLOOR: pr.set(j, (x, y, z), I3, 1.0)
            else: pr.hide(j)
    pr.commit()


def build_world(kit, D, top_mat, res=0.1):
    """The land around and behind the block, out to the hills: one grid at the same heights (szworld.top_h) and in the same
    ground paint, minus the hole the slice was lifted from."""
    xs = np.round(np.arange(-12.0, 12.0 + 1e-6, res), 4); ys = np.round(np.arange(-9.0, 14.0 + 1e-6, res), 4)
    X, Y = np.meshgrid(xs, ys); nx, ny = len(xs), len(ys); ii = np.arange(nx * ny).reshape(ny, nx)
    q = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
    cx = (X[:-1, :-1] + X[1:, 1:]).ravel() / 2; cy = (Y[:-1, :-1] + Y[1:, 1:]).ravel() / 2
    keep = ~W.in_hole(cx, cy); q = q[keep]
    used = np.unique(q); remap = -np.ones(nx * ny, int); remap[used] = np.arange(len(used)); q = remap[q]
    P = np.column_stack([X.ravel(), Y.ravel()])[used]
    attrs = {'rd': ('FLOAT', np.full(len(P), 9.0)), 'rk': ('FLOAT', np.zeros(len(P))), 'far': ('FLOAT', W.far(P[:, 0], P[:, 1]))}
    V = np.column_stack([P, W.top_h(P[:, 0], P[:, 1], 0.0)])
    ob = cw.mk_mesh(kit.bpy, 'fs_world', V, q.tolist(), [top_mat], None, True, kit.coll, attrs)
    return {'ob': ob, 'P': P}


# ============================================================================== harness entry points
def build(bpy, ctx):
    rng = np.random.default_rng(5)
    kit = cw.Kit(bpy, seed=5, loop=W.DURATION); D = M.Drive()
    L = cw.block(kit, size=(W.SX, W.SY), depth=-W.ZB, strata=W.STRATA, top=lambda x, y: W.slice_h(x, y, 0.0), water=None, seed=5, season='summer',
                 res=0.025, grass=0, trees=0, boulders=0, flowers=0, under=False, lilies=0, reeds=0, name='fs_block')
    geo = capture(L); hole = build_hole(kit, D, rng)
    L.objects['top'].data.materials[0] = M.mat_top(kit, D)
    world = build_world(kit, D, L.objects['top'].data.materials[0])
    park = PK.build(kit, L, D, rng)
    under = UG.build(kit, D, rng)
    cic = CI.build(kit, D, rng, under, park)
    cw.studio(kit, color=(0.93, 0.90, 0.84), key_az=SUN_AZ, key_el=45.0, key=3.2, angle=6.0, fill=0.8, land=L)
    cam = cw.camera(kit, L, '16:9' if ctx['W'] >= ctx['H'] else '9:16', az=AZ0, el=EL, lens=LENS, fill=FILL, top_extra=0.80, bottom_extra=W.GAP - 0.02)
    cam.pose(target=cam.target + np.array([0.0, 0.0, -W.ZB + W.GAP + CAM_DZ]))   # framed on the lifted slice, its gap and the hole's rim
    back = BK.build(kit, D, cam, ctx)
    words = WD.Words(kit, D, cam, ROOT)
    cw.apply_cycles(bpy); sc = bpy.context.scene; sc.cycles.transparent_max_bounces = 24
    S = {'kit': kit, 'D': D, 'land': L, 'geo': geo, 'world': world, 'hole': hole, 'park': park, 'under': under, 'cic': cic, 'back': back, 'words': words,
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
    # ---- the land: top and walls (the lawn, lifted)
    tp = S['geo']['top']; z = W.top_h(tp[:, 0], tp[:, 1], t); co = tp.copy(); co[:, 2] = z
    me = S['land'].objects['top'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel()); me.update()
    wl = S['geo']['walls']; uu = S['geo']['uu']; zt = W.slice_h(wl[:, 0], wl[:, 1], t); zz = zt + (W.ZB - zt) * uu
    co = wl.copy(); co[:, 2] = zz + W.lift(t); me = S['land'].objects['walls'].data; me.vertices.foreach_set('co', co.astype(np.float32).ravel())
    me.attributes['sd'].data.foreach_set('value', (W.Z_MAX - zz).astype(np.float32)); me.attributes['dtop'].data.foreach_set('value', (zt - zz).astype(np.float32)); me.update()
    # ---- the season on the lawn: green in spring and summer, gold in autumn, snow in winter
    w = W.weights(t); wi = float(w[3])
    D.setc('ground', mix(EARTH, (0.94, 0.96, 1.0), min(1.0, wi * 1.15)))
    D.set('green', 0.95 * (1 - 0.1 * wi)); D.setc('greencol', blend4(t, GREEN))
    D.set('wet', 0.0); D.set('rw', 0.0); D.set('rockamt', 0.0)
    world_pose = S['world']; P = world_pose['P']
    me = world_pose['ob'].data; me.vertices.foreach_set('co', np.column_stack([P, W.top_h(P[:, 0], P[:, 1], t)]).astype(np.float32).ravel()); me.update()
    underside_pose(S['hole'], t)
    D.setc('haze', blend4(t, HAZE)); D.set('murk', 0.0); D.set('walpha', 1.0)
    # ---- the camera holds (a 2 degree sway over the whole film); the light follows the seasons, and the gold of the song
    S['cam'].pose(az=S['az0'] + SWAY * math.sin(2 * math.pi * t / W.DURATION))
    dbg = os.environ.get('KF_DEBUG_CAM')
    if dbg: a_, e_, d_ = [float(x) for x in dbg.split(',')]; S['cam'].pose(az=a_, el=e_, dist=S['cam'].dist * d_)
    gold = W.win(t, B.sun_gold0, B.final + 3.0, 1.0)
    el = blend4(t, SUN['el']) - 10.0 * gold
    S['sun'].rotation_euler = (math.radians(90 - el), 0, math.radians(SUN_AZ + 90))
    S['sun'].data.energy = blend4(t, SUN['e']) * (1 + 0.12 * gold); S['sun'].data.color = mix(blend4(t, SUN['col']), (1.0, 0.84, 0.56), 0.6 * gold)
    # ---- life
    PK.pose(S['park'], D, t); UG.pose(S['under'], D, t); CI.pose(S['cic'], D, t, S['under'], S['park'])
    BK.pose(S['back'], D, t)
    S['words'].pose(t, CI.label_point(S['cic'], S['under'], t))
    if S.get('art') is not None: S['art'].frame(bpy, ctx, t)
