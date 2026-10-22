"""Cutaway, cinematic hero version (style comparison for the board; 12 s, five pre-planned angles).

The D look's river village at golden hour, relit for cinema: a low warm sun raking across the block, cool fill, warm rim,
haze, ground fog and mist in the valley, light shafts through the trees and through cloud gaps, bloom and a vignette.
The cut faces hide easter eggs placed by depth (recent near the top, dinosaurs deep), each under a museum spot.
Animals and plants move all the time (deterministic in t). Kit: ../cutaway.py (imported, never edited); additions: extras.py.

Shots (frame = t * 24; one stills run of FRAMES shows every angle):
  1 map     0.0-2.0 s  top-down map, fog drifting, long shadows           (understanding: where we are)
  2 ground  2.0-4.5 s  ground level at the block's edge, into the sun     (arrival: stakes and scale, the living top)
  3 crane   4.5-8.0 s  vertical crane down the -Y cut face                (the reveal: layers read as time)
  4 macro   8.0-10.0 s close on the T. rex skull                          (the payoff: the smile)
  5 hero   10.0-12.0 s low three-quarter, sun behind the block            (the closing image: the whole world, rim-lit)
"""
import math
import os
import sys

import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
for p in (here, os.path.dirname(here)):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import extras as ex  # noqa: E402

SHOTS = [{'name': 'map', 'dur': 2.0}, {'name': 'ground', 'dur': 2.5}, {'name': 'crane', 'dur': 3.5}, {'name': 'macro', 'dur': 2.0}, {'name': 'hero', 'dur': 2.0}]
DURATION = sum(s['dur'] for s in SHOTS)
FRAMES = {'map': 24, 'ground': 84, 'crane_top': 112, 'crane': 150, 'crane_low': 186, 'macro': 222, 'hero': 270}   # check stills
SETTINGS = {'samples': 48, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - High Contrast', 'exposure': 0.1,
            'max_bounces': 8, 'volume_bounces': 0, 'clamp_indirect': 4.0, 'adaptive_min_samples': 8, 'denoising_prefilter': 'FAST',
            'volume_step_rate': 6.0}

FOG_GAIN = {'map': 1.0, 'ground': 0.4, 'crane': 1.0, 'macro': 1.0, 'hero': 0.7}
SHAFT_GAIN = {'map': 0.35, 'ground': 1.0, 'crane': 0.8, 'macro': 0.0, 'hero': 1.0}
SUN_AZ, SUN_EL = 135.0, 11.0
RIVER = [(-0.7, 2.6), (-0.55, 1.4), (0.25, 0.6), (0.05, -0.4), (0.35, -1.3), (0.4, -2.6)]
STRATA = [('topsoil', 0.07, (0.26, 0.17, 0.10), 0.05), ('sand', 0.10, (0.90, 0.74, 0.46), 0.08), ('clay', 0.14, (0.78, 0.44, 0.28), 0.03),
          ('loam', 0.16, (0.56, 0.36, 0.22), 0.20), ('gravel', 0.10, (0.62, 0.58, 0.54), 0.9), ('ochre', 0.05, (0.84, 0.60, 0.28), 0.12),
          ('limestone', 0.68, (0.88, 0.84, 0.74), 0.05), ('bedrock', 1.0, (0.24, 0.25, 0.30), 0.35)]   # time runs down: recent soil, Roman loam, fossil limestone, ancient bedrock
HOUSES = [(1.20, 0.90, 1.2), (1.48, 0.15, 1.6), (1.05, -0.30, 0.4), (-1.15, 0.75, 0.3), (-1.50, 1.45, -0.2), (-1.35, 0.05, 0.9)]
MILL = (0.98, -1.05)
LANE = [(-2.1, 0.3), (-1.4, 0.35), (-0.8, 0.15), (-0.3, 0.06), (0.6, 0.16), (1.1, 0.35), (1.7, 0.55), (2.1, 0.6)]


def _lane_zone(x, y, h):
    P = np.array(LANE); d = np.full(np.shape(x), 9.0)
    for a, b in zip(P[:-1], P[1:]):
        ab = b - a; t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / (ab @ ab), 0, 1); d = np.minimum(d, np.hypot(x - a[0] - t * ab[0], y - a[1] - t * ab[1]))
    return {'path': cw.smooth(0.055, 0.025, d + 0.01 * cw.fbm(x, y, 3, 2, 8))}


def build(bpy, ctx):
    W, H = ctx['W'], ctx['H']
    kit = cw.Kit(bpy, seed=1, loop=DURATION)
    clear = [(x, y, 0.3) for x, y, _ in HOUSES] + [(MILL[0], MILL[1], 0.32)]
    land = cw.block(kit, size=(4.0, 4.0), depth=1.6, strata=STRATA, seed=4, top=cw.rolling(amp=0.10, freq=0.32, seed=4, base=0.03),
                    water=[cw.river(RIVER, width=0.7, depth=0.34, level=-0.05, shelf=0.22)], zones=_lane_zone, keep_clear=clear,
                    trees=15, tree_kinds=('round', 'cone', 'round', 'tall'), boulders=10, flowers=0.7, lilies=12, reeds=0.6, sway=1.45,
                    water_density=2.8, water_glow=0.0, water_tint=(0.14, 0.56, 0.58), bed=((0.40, 0.38, 0.30), (0.28, 0.27, 0.22)), caustics=0.35)
    for k, (x, y, yaw) in enumerate(HOUSES):
        cw.house(kit, land, x, y, w=0.21, d=0.15, h=0.13, roof=0.09, yaw=yaw, lit=1.6,
                 roof_col=[(0.55, 0.22, 0.14), (0.30, 0.30, 0.34), (0.48, 0.28, 0.18)][k % 3], name=f'cw_house{k}')
    cw.mill(kit, land, MILL[0], MILL[1], yaw=math.pi, lit=1.6, wheel_r=0.11, wheel_off=0.40)
    cw.bridge(kit, land, (-0.32, 0.06), (0.62, 0.16), width=0.09, arch=0.06)
    for k, (x, y) in enumerate([(-0.85, 0.24), (-0.38, -0.03), (0.75, 0.05), (1.45, 0.62)]):
        cw.lamp(kit, land, x, y, name=f'cw_lamp{k}')

    rig = ex.cine_light(kit, land, SUN_AZ, SUN_EL, sun=6.0, fill=0.9, amb=0.24)
    atmos, fog_gain = ex.atmosphere(kit, land, haze=float(os.environ.get('EX_HAZE', 0.0)), fog=float(os.environ.get('EX_FOG', 7.0)), fog_top=float(os.environ.get('EX_FOGTOP', 0.16)), ceiling=float(os.environ.get('EX_CEIL', 0.25)), spill=0.3, aniso=0.7)
    ex.gobo(kit, land, rig['sun_dir'])
    # the hero tree: the big round tree by the mill sits right in front of the sun from the hero camera (rays round its crown)
    T = np.asarray(land.trees); k = int(np.argmin(np.hypot(T[:, 0] - 1.33, T[:, 1] + 0.88))); gz = float(land.height(T[k:k + 1, 0], T[k:k + 1, 1])[0])
    crown = (T[k, 0], T[k, 1], gz + 0.48)
    shafts = ex.Shafts(kit, land, rig['sun_dir'], beams=ex.Shafts.around(crown, 0.2, rig['sun_dir'], 12), canopy=12, strength=2.4)

    # ---- easter eggs, by depth (recent near the top, deep time at the bottom)
    eggs = ex.Eggs(kit, land); fy = eggs.faces['-Y']; fx = eggs.faces['+X']
    eggs.mole('-Y', -1.30, fy.top(-1.1) - 0.115)
    eggs.chest('-Y', -1.18, fy.top(-1.18) - 0.31)
    eggs.amphora('-Y', -0.42, fy.top(-0.42) - 0.46)
    eggs.ammonite('-Y', 0.20, -0.84)
    eggs.dino('-Y', -0.78, -0.98)
    eggs.trilobite('-Y', -1.48, -1.235)
    eggs.gold('-Y', [(-1.85, -1.36), (-1.15, -1.45), (-0.55, -1.37), (0.05, -1.50), (0.65, -1.44), (1.2, -1.5)])
    eggs.hedgehog('+X', -1.05, fx.top(-1.05) - 0.17)
    eggs.geode('+X', -0.45, -1.06)
    eggs.well('+X', 0.62, r=0.07)
    eggs.geode('-Y', 0.42, -1.43, a=0.085, b=0.07)
    eggs.finish()
    ex.soften_roots(land)
    ex.edge_spill(kit, land, '-Y')
    ex.edge_spill(kit, land, '+X', power=35.0)

    # ---- life
    ex.deer(kit, land, -1.05, -1.22, 0.25, lift_at=5.4, lower_at=9.8)
    ex.deer(kit, land, -0.80, -1.48, 0.55, lift_at=6.6, lower_at=10.6, name='ex_fawn', scale=0.72)
    ex.rabbit(kit, land, [(-1.75, -1.55), (-1.45, -1.72), (-1.05, -1.66), (-0.7, -1.78)], t0=0.3)
    ex.rabbit(kit, land, [(1.75, -1.75), (1.55, -1.45), (1.6, -1.1), (1.35, -0.85)], t0=0.9, name='ex_rabbit2', color=(0.60, 0.50, 0.40))
    ex.fox(kit, land, [(1.78, -0.15), (1.62, -0.75), (1.48, -1.35), (1.25, -1.85)], speed=0.05)
    ex.heron(kit, land, 0.66, -1.70, math.pi * 0.92)
    ex.ducks(kit, land, [(0.18, 0.55), (0.08, -0.2), (0.22, -0.9), (0.36, -1.5), (0.40, -1.95)], n=3, speed=0.03)
    ex.fish(kit, land, (0.38, -1.83), n=5)
    ex.fireflies(kit, land, 28, near=[(-0.25, -0.7), (0.75, -0.5), (-0.4, 0.9), (0.6, 1.2), (-1.4, -0.5), (1.2, -1.5)])
    ex.petals(kit, land, 44)
    ex.butterflies(kit, land, [(-1.3, -0.85), (1.35, -0.55), (-0.55, -1.45)])
    cw.birds(kit, 4, center=(0.2, 0.3), radius=2.2, height=1.1)

    ex.finish(bpy, W, H)
    cam = ex.ShotCam(kit)
    cw.apply_cycles(bpy)
    sc = bpy.context.scene; cy = sc.cycles
    cy.volume_bounces = 0; cy.volume_step_rate = SETTINGS['volume_step_rate']; cy.volume_max_steps = 128
    cy.adaptive_threshold = 0.035; cy.sample_clamp_direct = 12.0          # converge sooner; tame sun glints on water
    try: cy.volume_biased = True
    except Exception: pass
    cy.transparent_max_bounces = 16
    return {'kit': kit, 'land': land, 'cam': cam, 'eggs': eggs, 'rig': rig, 'shafts': shafts, 'fog_gain': fog_gain}


def shot_pose(S, name, u):
    """Camera for shot `name` at local progress u (0..1). Returns pos, target, lens, focus, fstop, roll."""
    eggs = S['eggs']
    if name == 'map':                    # straight down, a slow drift and turn: the map
        e = ex.ease(u); pos = (0.08 - 0.06 * e, -0.05, 12.6 - 0.5 * e); tgt = (0.08 - 0.06 * e, -0.049, 0.0)
        return pos, tgt, 50.0, 11.0, 16.0, 22.0 + 6.0 * e
    if name == 'ground':                 # at the edge, eye on the grass, into the sun, a slow dolly along the face
        e = ex.ease(u); pos = ex.lerp((2.36, -2.52, 0.30), (2.24, -2.45, 0.29), e); tgt = (-0.8, -1.40, -0.22)
        return pos, tgt, 28.0, float(np.linalg.norm(np.array(pos) - np.array((0.66, -1.85, 0.0)))), 5.6, 0.0
    if name == 'crane':                  # vertical crane down the cut face, treetops to the deepest layer
        e = ex.ease5(u); tz = 0.32 + (-1.10 - 0.32) * e; el = math.radians(20 - 19 * e); D = 2.45
        tgt = (-0.52, -2.0, tz); pos = (-0.52 + 0.30, -2.0 - D, tz + D * math.tan(el))
        return pos, tgt, 40.0, D / math.cos(el), 5.6, 0.0
    if name == 'macro':                  # close on the skull, a slow push
        f, uu, zz = eggs.items['skull']; c = eggs.faces[f].world(uu - 0.04, zz - 0.01, 0.0)
        k = 1.0 - 0.10 * ex.ease(u); off = np.array([0.50, -0.92, 0.13]) * k
        return tuple(c + off), tuple(c), 55.0, float(np.linalg.norm(off)), 4.0, 0.0
    # hero: low three-quarter from the +X side, the sun behind the block, a slow arc
    e = ex.ease(u); az = math.radians(-46 + 8 * e); el = math.radians(3.0); D = 4.6; tgt = np.array((0.15, -0.15, -0.36))
    pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    return tuple(pos), tuple(tgt), 28.0, D - 2.0, 8.0, 0.0


def frame(bpy, ctx, S, i, t):
    S['kit'].update(t)
    tl = ctx['timeline'].at(t); pos, tgt, lens, focus, fstop, roll = shot_pose(S, tl['name'], tl['u'])
    S['cam'].set(pos, tgt, lens, focus, fstop, roll); S['shafts'].update(pos)
    S['shafts'].gain.default_value = SHAFT_GAIN[tl['name']]; S['fog_gain'].default_value = FOG_GAIN[tl['name']]
