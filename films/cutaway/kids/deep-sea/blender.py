"""Little Big Questions: What lives in the deep sea? A SILENT story told by the picture (Cutaway, Fable look, 16:9, 24 fps,
70.5 s). No narration; real orchestral music (Mendelssohn, The Hebrides, Musopen Symphony) and real sound effects carry it;
a few big words set in code. Source of truth: beats.json (11 beats: picture, words, sound, music).

One fixed view of one lifted slice (a 2 degree sway over the whole film, no cuts): a tall column of ocean floats a little
above the hole it was lifted from in a sunny sea that carries on to the horizon with an island, a boat, gulls and a whale.
A little round submarine (with the series' snail in its porthole) dives through it: sunlight zone, twilight zone, midnight
zone, the seafloor with a hot vent and giant tube worms. Every event of the picture is anchored to a beat in the one table
below (EVENTS: beat, seconds into it); change beats.json and the whole film re-times itself.
Look: Fable (films/styles/cutaway/art/fable.py through art/_adapter.py), named by KF_ART_NAME ($KF_ART overrides it).
Files: szworld.py (clock of beats, measures, the submarine's path), szmats.py (the sea shader and materials), szgeo.py (rigid
parts), szsea.py (the stage), szlife.py (everything alive), szwords.py and szui.py (captions, label), this file.
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
# THE EVENT TABLE: every timed event of the picture, as (beat, seconds after the beat starts).
# ==============================================================================================================
BEAT_NAMES = {'hook': 'hook', 'sun': 'sunlight zone', 'twi': 'twilight zone', 'mid': 'midnight zone', 'glow': 'they glow', 'squid': 'glowing squid',
              'lantern': 'the lantern', 'vent': 'hot vents', 'bloom': 'all the lights', 'unseen': 'only a tiny piece', 'home': 'back to the surface'}
EVENTS = {
    'dive': ('sun', 0.1), 'surf': ('home', 1.4), 'duck_hop0': ('hook', 2.6), 'duck_hop1': ('hook', 3.1), 'end_duck0': ('home', 1.6), 'end_duck1': ('home', 2.1),
    # twilight: the lantern fish light up on the swell (recording 0:17 to 0:19.5)
    'twi0': ('twi', 0.0), 'lant0': ('twi', 3.4), 'lant1': ('twi', 6.9), 'B_j3': ('twi', 3.8),
    # they glow: the cello theme; the key word GLOW! on the first jellyfish
    'B_j0': ('glow', 0.2), 'B_j1': ('glow', 1.8), 'B_j2': ('glow', 3.5), 'label0': ('glow', 0.2), 'label1': ('glow', 3.2),
    # the squid, the bottle, the snail waves
    'sq0': ('squid', 0.2), 'sq1': ('squid', 6.2), 'bot0': ('squid', 0.0), 'bot1': ('lantern', 0.5), 'snwave0': ('squid', 2.2), 'snwave1': ('squid', 4.4),
    # the lantern: the anglerfish slides out, lights its lure over the submarine
    'an0': ('lantern', 0.0), 'an1': ('lantern', 6.0), 'lure0': ('lantern', 2.4), 'lure1': ('lantern', 5.8), 'snwave2': ('lantern', 3.6), 'snwave3': ('lantern', 5.4),
    'lamp_off': ('lantern', 1.3), 'lamp_on': ('lantern', 5.7),
    # the vent
    'vent0': ('vent', 0.0), 'chest0': ('vent', 5.2),
    # the climax: every light at once on the tutti (recording 1:37)
    'bloom0': ('bloom', -0.5), 'bloom1': ('bloom', 4.0),
    'unseen0': ('unseen', 0.0), 'end_wave0': ('home', 2.6), 'end_wave1': ('home', 5.8), 'words_send': ('home', 1.5),
    # names the shared caption and label code reads (a pocket watch and a ribbon label that this film does not use are parked at the end)
    'rw0': ('home', 20.0), 'rw1': ('home', 20.0), 'stack0': ('home', 20.0), 'stack1': ('home', 20.0), 'rain0': ('home', 20.0), 'erode1': ('home', 20.0),
}
W.set_events({k: (BEAT_NAMES[b], s / (W.BEAT[BEAT_NAMES[b]]['t1'] - W.BEAT[BEAT_NAMES[b]]['t0'])) for k, (b, s) in EVENTS.items()})
W.B.spouts = [W.bt('hook', 1.2 / 5.5), W.bt('sunlight zone', 5.0 / 8.0), W.bt('glow'.replace('glow', 'they glow'), 0.2), W.bt('only a tiny piece', 0.5 / 5.0), W.bt('back to the surface', 4.5 / 6.0)]
W.WORD_IN[BEAT_NAMES['home']] = W.B.words_send          # the last words wait for the final chord

import szmats as M  # noqa: E402
import szsea as SEA  # noqa: E402
import szlife as LF  # noqa: E402
import szwords as WD  # noqa: E402

DURATION = W.DURATION
SETTINGS = {'samples': 32, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast',
            'exposure': 0.0, 'max_bounces': 3, 'volume_bounces': 0, 'clamp_indirect': 6.0, 'adaptive_min_samples': 12,
            'denoising_prefilter': 'ACCURATE'}

AZ0, SWAY = W.VIEW_AZ, 2.0
EL, LENS, FILL = 13.0, 50.0, 0.94
SUN_AZ = -118.0


def fit_camera(kit, aspect):
    """Frame the lifted slice (its box from the gap under it to the sea surface on top) plus room for the title above and a
    little sea under it. Same exact-fit loop as cw.camera."""
    asp = 16 / 9 if aspect == '16:9' else 9 / 16
    th = 18.0 / LENS; tanh, tanv = (th, th / asp) if asp >= 1 else (th * asp, th)
    z_lo, z_hi = W.GAP - 0.20, W.LIFT0 + 1.35
    pts = np.array([(x, y, z) for x in (-W.HX, W.HX) for y in (-W.HY, W.HY) for z in (z_lo, z_hi)])
    tgt = np.array((0.0, 0.0, (z_lo + z_hi) / 2)); dist = 8.0; az, el = AZ0, EL
    for _ in range(8):
        a, e = math.radians(az), math.radians(el); dvec = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        cp = tgt + dist * dvec; fwd = -dvec; right = np.cross(fwd, (0, 0, 1)); right /= np.linalg.norm(right); up = np.cross(right, fwd)
        v = pts - cp; z = v @ fwd; u = (v @ right) / z / tanh; w = (v @ up) / z / tanv
        tgt = tgt + right * ((u.max() + u.min()) / 2 * tanh * dist) + up * ((w.max() + w.min()) / 2 * tanv * dist)
        span = max((u.max() - u.min()) / 2, (w.max() - w.min()) / 2); dist *= span / FILL
    return cw.camera(kit, None, aspect, az=az, el=el, lens=LENS, target=tuple(tgt), dist=dist)


# ============================================================================== harness entry points
def build(bpy, ctx):
    rng = np.random.default_rng(5)
    kit = cw.Kit(bpy, seed=5, loop=W.DURATION); D = M.Drive()
    L = SEA.build_floor(kit, D)
    stage = SEA.build_stage(kit, D, rng)
    sub = LF.build_sub(kit, D); fish = LF.build_fish(kit, D); turtle = LF.build_turtle(kit, D); duck = LF.build_duck(kit, D)
    lantern = LF.build_lantern(kit, D); bigeye = LF.build_bigeye(kit, D); jelly = LF.build_jelly(kit, D); squid = LF.build_squid(kit, D); angler = LF.build_angler(kit, D)
    floorlife = LF.build_floor_life(kit, D); snow = LF.build_snow(kit, D); bub = LF.build_bubbles(kit, D); rip = LF.build_ripples(kit, D)
    pool = LF.build_pool(kit, D); tw = LF.build_twinkles(kit, D); bottle = LF.build_bottle(kit, D); world = LF.build_world_life(kit, D)
    cw.studio(kit, color=(0.93, 0.90, 0.84), key_az=SUN_AZ, key_el=45.0, key=2.0, angle=6.0, fill=0.8, land=L)
    cam = fit_camera(kit, '16:9' if ctx['W'] >= ctx['H'] else '9:16')
    far = SEA.build_far(kit, D, cam, ctx); D.setv('camP', tuple(cam.ob.location))
    words = WD.Words(kit, D, cam, ROOT)
    cw.apply_cycles(bpy); sc = bpy.context.scene; sc.cycles.transparent_max_bounces = 24
    S = {'kit': kit, 'D': D, 'land': L, 'stage': stage, 'sub': sub, 'fish': fish, 'turtle': turtle, 'duck': duck, 'lantern': lantern, 'bigeye': bigeye, 'jelly': jelly,
         'squid': squid, 'angler': angler, 'floor': floorlife, 'snow': snow, 'bub': bub, 'rip': rip, 'pool': pool, 'tw': tw, 'bottle': bottle, 'world': world, 'words': words,
         'cam': cam, 'az0': cam.az, 'sun': bpy.data.objects['cw_sun']}
    frame(bpy, ctx, S, 0, 0.0)
    art = os.environ.get('KF_ART', globals().get('KF_ART_NAME'))
    if art and art != 'none':
        import importlib.util
        sp = importlib.util.spec_from_file_location('kf_art_adapter', os.path.join(ROOT, 'films', 'styles', 'cutaway', 'art', '_adapter.py'))
        ad = importlib.util.module_from_spec(sp); sp.loader.exec_module(ad)
        S['art'] = ad.attach(bpy, ctx, art, kit=kit, land=L, cam=cam, settings=SETTINGS, strata=SEA.FLOOR_STRATA, words=words.obs)
        S['art'].frame(bpy, ctx, 0.0)
    return S


def frame(bpy, ctx, S, i, t):
    kit, D = S['kit'], S['D']; kit.update(t); B = W.B
    z = W.lift(t); D.set('lift', z)
    # the seafloor block rides the slice
    for k in ('top', 'walls'): S['land'].objects[k].location.z = z - W.DEEP
    # the light of the day: bright, then the golden evening of the calm ending
    w = W.weights(t); dusk = w[2]; D.set('dusk', dusk)
    D.setc('seahaze', tuple((1 - dusk) * a + dusk * b for a, b in zip((0.70, 0.86, 0.84), (0.80, 0.44, 0.46))))
    D.set('raysA', 1.0 - 0.7 * dusk)
    D.set('wflash', 0.20 * W.sm(W.B.bloom0 - 0.05, W.B.bloom0 + 0.10, t) * (1.0 - W.sm(W.B.bloom0 + 0.2, W.B.bloom0 + 1.6, t)) + 0.12 * LF.bloom_env(t))
    SEA.stage_pose(S['stage'], D, t)
    LF.sub_pose(S['sub'], D, t); LF.fish_pose(S['fish'], t); LF.turtle_pose(S['turtle'], t); LF.duck_pose(S['duck'], t)
    LF.lantern_pose(S['lantern'], t, D); LF.bigeye_pose(S['bigeye'], t); LF.jelly_pose(S['jelly'], D, t); LF.squid_pose(S['squid'], D, t)
    lure_p = LF.angler_pose(S['angler'], D, t)
    LF.floor_pose(S['floor'], D, t); LF.snow_pose(S['snow'], t); LF.bubbles_pose(S['bub'], D, t); LF.ripples_pose(S['rip'], D, t)
    LF.pool_pose(S['pool'], D, t); LF.twinkles_pose(S['tw'], t); LF.bottle_pose(S['bottle'], D, t); LF.world_life_pose(S['world'], D, t)
    # the lure's light on the submarine: a cone from the lure down onto it
    from mathutils import Vector
    bu = S['sub']['beam_u']; la = D.v['lureA'][0].default_value if D.v.get('lureA') else 0.0
    bu.hide_render = (lure_p is None) or la < 0.02
    if lure_p is not None and la >= 0.02:
        tgt = LF.sub_state(t)[0] + np.array([0.0, 0.0, W.lift(t)]); d = tgt - lure_p; ln = float(np.linalg.norm(d))
        bu.location = tuple(lure_p); bu.rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector(tuple(d / ln))).to_euler(); bu.scale = (1.2, 1.2, ln * 1.5)
    # camera: fixed, a 2 degree sway over the whole film; the sun softly lit from the front left
    S['cam'].pose(az=S['az0'] + SWAY * math.sin(2 * math.pi * t / W.DURATION))
    S['sun'].rotation_euler = (math.radians(90 - 50.0), 0, math.radians(SUN_AZ + 90)); S['sun'].data.energy = 2.4 + 0.0 * dusk
    S['sun'].data.color = tuple((1 - dusk) * a + dusk * b for a, b in zip((1.0, 0.97, 0.90), (1.0, 0.70, 0.50)))
    # the label (GLOW!) points at the first jellyfish
    jp = LF.jelly_pos(0, t) + np.array([0, 0, W.lift(t) + 0.04])
    S['words'].pose(t, jp)
    if S.get('art') is not None: S['art'].frame(bpy, ctx, t)
