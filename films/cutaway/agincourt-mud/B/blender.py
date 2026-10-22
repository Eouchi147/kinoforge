"""Agincourt mud, insert B (cue l10 to l11, film 86.703 to 100.867 s): the mud and the woods turn the battle.

Shot B1 (86.70 to just before 'The woods'): low on the -Y cut face, a slow track with the French front file walking
left to right toward the English. Through the face we see their legs go into the soft wet layer; each step is shorter
and slower; ankle deep on 'advanced', knee deep on 'knees', where the soldier in the middle of the frame stops dead and
wobbles, and the one behind bumps up to him.
    Job: what the mud does to a man in armour, seen from inside the ground.
Cut (0.15 s before 'The woods', after a 1.2 s hold): change of scale, from the legs to the whole army.
Shot B2 (to 100.87): high behind the English stakes, the camera rises slowly; the column comes at us between the two
woods, the files close together in the neck ('squeezed', 'packed'), on 'swing a weapon' the poleaxes clatter together.
    Job: the woods and the mud together pack the French into a space where they cannot fight.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agin_mud as am  # noqa: E402
from agin_mud import cw, W, ease, YF  # noqa: E402

T0, T1, F0, F1 = am.span('B')
DURATION = T1 - T0
SETTINGS = am.settings(64, 0.30)
CUT = W('l11', 'The') - 0.15


def build(bpy, ctx):
    kit = cw.Kit(bpy, seed=7, loop=0)
    land, tv = am.build_world(bpy, kit, rain=False)
    am.light(kit, land, 'after')
    M = am.materials(kit); cutter = am.make_cutter(bpy, land)
    en = am.English(bpy, kit, M, cutter, 'B'); fr = am.French(bpy, kit, M, cutter)
    cw.birds(kit, 4, center=(0.2, 1.1), radius=1.5, height=1.1, size=0.035)
    cam = cw.camera(kit, land, '16:9', az=-25, el=32, lens=45, fill=0.9)
    cw.apply_cycles(bpy)
    st = next(s for s in fr.sol if s['stuck'])
    xa = fr.place(T0)[(st['r'], st['f'])][0]; xb = fr.place(CUT)[(st['r'], st['f'])][0]
    return {'kit': kit, 'tv': tv, 'en': en, 'fr': fr, 'cam': cam, 'dfit': cam.dist, 'xa': xa, 'xb': xb}


def shot(T, S):
    if T < CUT:                                          # B1: low at the cut face, tracking with the walkers
        e = ease((T - T0) / (CUT - 0.5 - T0)); x = S['xa'] + 0.13 + (S['xb'] + 0.04 - S['xa'] - 0.13) * e
        return dict(az=-91 + 3 * e, el=6.0, dist=1.0, target=(x, YF + 0.02, -0.035), lens=45, f=6.0)
    e = ease((T - CUT) / (T1 - CUT))                     # B2: high behind the English, rising slowly
    return dict(az=-24 + 4 * e, el=30 + 9 * e, dist=S['dfit'] * (0.86 + 0.04 * e), target=(0.12 + 0.06 * e, 0.02, -0.34), lens=45, f=None)


def frame(bpy, ctx, S, i, t):
    T = (F0 + i) / am.FPS
    S['kit'].update(t); S['tv'].default_value = T
    sh = shot(T, S); cam = S['cam']; cam.ob.data.lens = sh['lens']
    cam.pose(az=sh['az'], el=sh['el'], dist=sh['dist'], target=sh['target']); am.set_dof(cam, sh['f'], sh['dist'])
    S['en'].pose(T); S['fr'].pose(T)
