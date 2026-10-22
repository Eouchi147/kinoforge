"""Agincourt mud, insert A (cue l06 to l07, film 57.284 to 71.982 s): the field is a trap before anyone moves.

Shot A1 (57.28 to the end of 'mud.' plus a held beat): high and wide, the block as a map from the French side, rain
falling, rings spreading in the furrow puddles, the cut faces soaked; one slow push down toward the field.
    Job: the viewer sees the whole ploughed field full of water, the English small on the far edge.
Cut (a hold of 0.55 s after 'mud.', before 'The English archers'): change of scale, from the field to the people on it.
Shot A2 (to 71.98): low on the -Y cut face at the English line, looking along the row of stakes. The archers hammer the
stakes in at an angle, points toward the French, three blows each, in a wave from the near face outward between
'hammered' and 'them.'; the nearest stake is cut by the face so its point goes into the soft wet layer in section.
On 'Then Henry moved his whole army forward' the men-at-arms come up behind and the camera eases up and back to show the
line facing the long wet field; on 'shoot' the archers lift their bows.
    Job: why the field is a trap, and that the English are ready for it.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agin_mud as am  # noqa: E402
from agin_mud import cw, W, ease, YF  # noqa: E402

T0, T1, F0, F1 = am.span('A')
DURATION = T1 - T0
SETTINGS = am.settings(64, 0.45)
CUT = W('l06', 'mud', end=True) + 0.55
T_PULL = W('l07', 'Then') - 0.5


def build(bpy, ctx):
    kit = cw.Kit(bpy, seed=6, loop=0)
    land, tv = am.build_world(bpy, kit, rain=True)
    am.light(kit, land, 'rain'); am.mist(kit, 0.55)
    M = am.materials(kit); cutter = am.make_cutter(bpy, land)
    en = am.English(bpy, kit, M, cutter, 'A')
    rain = am.Rain(kit, land)
    crows = am.Crows(bpy, kit, [(x, float(am.y_far(x)) - 0.06 + 0.02 * k) for k, x in enumerate((-1.25, -1.08, -0.93))])
    worms = am.Worms(bpy, kit, [(1.24, -0.050, 0.034, 0.0), (1.63, -0.105, 0.030, 1.7), (1.43, -0.035, 0.028, 3.1)])
    am.easter_eggs(bpy, kit, coin=(1.355, -0.150))
    cam = cw.camera(kit, land, '16:9', az=-150, el=44, lens=50, fill=0.92)
    cw.apply_cycles(bpy)
    return {'kit': kit, 'tv': tv, 'en': en, 'rain': rain, 'cam': cam, 'dfit': cam.dist, 'crows': crows, 'worms': worms}


def shot(T, S):
    if T < CUT:                                          # A1: high, wide, one slow push down
        e = ease((T - T0) / (CUT - T0))
        return dict(az=-151 + 4 * e, el=44 - 5 * e, dist=S['dfit'] * (0.84 - 0.08 * e), target=(0.22 + 0.18 * e, 0.05, -0.20 + 0.04 * e),
                    lens=50, f=None)
    d = ease((T - CUT) / (T_PULL - CUT))                 # A2: a slow drift while the stakes go in ...
    e = ease((T - T_PULL) / (T1 - T_PULL))               # ... then up and back to the line facing the field
    return dict(az=-73 - 3 * d - 13 * e, el=11 + 1 * d + 9 * e, dist=0.92 + 0.03 * d + 0.48 * e,
                target=(1.47 - 0.02 * d - 0.20 * e, YF + 0.06 + 0.22 * e, 0.005 - 0.01 * e), lens=45, f=11.0 + 4.0 * e)


def frame(bpy, ctx, S, i, t):
    T = (F0 + i) / am.FPS
    S['kit'].update(t); S['tv'].default_value = T
    sh = shot(T, S); cam = S['cam']; cam.ob.data.lens = sh['lens']
    cam.pose(az=sh['az'], el=sh['el'], dist=sh['dist'], target=sh['target']); am.set_dof(cam, sh['f'], sh['dist'])
    S['en'].pose(T)
    S['rain'].update(T, cam.ob.location); S['crows'].pose(T); S['worms'].pose(T)
