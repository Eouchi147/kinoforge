"""What lives in the deep sea? The stage: the lifted column of ocean, the hole it came from, and the sea all round.

The slice is OPEN on its two near faces (the front and the right one): a tall room of painted water with a back wall and a
left wall (sunlit turquoise at the top, midnight at the foot, gold hairlines at the zone changes), a translucent sea
surface on top, gold rails on its edges, and the seafloor as a real Cutaway block of strata at its foot. It floats
`GAP` above the hole it was lifted from in the sea (the sea carries on at its natural level to the horizon).
Slice frame: z = 0 at the sea surface, x across the front face, y into the picture; world = slice + lift(t).
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, box, I3, rx, ry, rz

# the seafloor's relief (m above the seafloor's own top): a few soft dunes, a low mound for the vent, a dip for the toy boat
VENT_XY = (0.50, 0.12)
FLOOR_STRATA = [('sand', 0.07, (0.94, 0.76, 0.46), 0.05), ('silt', 0.10, (0.34, 0.58, 0.58), 0.05), ('mud', 0.12, (0.20, 0.38, 0.52), 0.10),
                ('rock', 1.0, (0.13, 0.22, 0.46), 0.30)]


def floor_h(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    dunes = 0.035 * np.sin(2.4 * x + 0.7) * np.cos(3.1 * y + 0.3) + 0.03 * np.sin(5.2 * x - 1.1) * 0.5
    mound = 0.16 * np.exp(-(((x - VENT_XY[0]) / 0.34) ** 2 + ((y - VENT_XY[1]) / 0.30) ** 2))
    return dunes + mound + 0.05


def floor_z(x, y):
    """World-less slice-frame height of the seafloor's top at (x, y)."""
    return -W.DEEP + floor_h(x, y)


def build_floor(kit, D):
    """The seafloor block (real Cutaway strata on its cut faces, painted by Fable) with a painted sand top."""
    L = cw.block(kit, size=(W.SX, W.SY), depth=W.BASE, strata=FLOOR_STRATA, top=lambda x, y: floor_h(x, y), water=None, seed=7, season='summer', res=0.03,
                 grass=0, trees=0, boulders=0, flowers=0, under=False, lilies=0, reeds=0, name='fs_floor')
    L.objects['top'].data.materials[0] = M.sea(kit, D, 'fs_sand', (0.88, 0.72, 0.46), shade=0.18, tex=0.10)
    return L


def _quad(a, b, c, d):
    return [a, b, c, d], [(0, 1, 2, 3)]


def build_stage(kit, D, rng):
    bpy = kit.bpy; out = {}
    hx, hy, dp = W.HX, W.HY, W.DEEP
    # ---- the two painted walls of the water (back, left), the surface, the rails
    wm = M.wall(kit, D)
    back = cw.mk_mesh(bpy, 'fs_back', [(-hx, hy, -dp - 0.02), (hx, hy, -dp - 0.02), (hx, hy, 0.0), (-hx, hy, 0.0)], [(0, 1, 2, 3)], [wm], None, False, kit.coll)
    left = cw.mk_mesh(bpy, 'fs_left', [(-hx, -hy, -dp - 0.02), (-hx, hy, -dp - 0.02), (-hx, hy, 0.0), (-hx, -hy, 0.0)], [(0, 1, 2, 3)], [wm], None, False, kit.coll)
    top = cw.mk_mesh(bpy, 'fs_surface', [(-hx, -hy, 0.0), (hx, -hy, 0.0), (hx, hy, 0.0), (-hx, hy, 0.0)], [(0, 1, 2, 3)], [M.surface(kit, D)], None, False, kit.coll)
    top.visible_shadow = False
    gold = M.glow(kit, D, 'fs_rail', (0.98, 0.78, 0.34), 1.0)
    pr = Parts('fs_rails'); r = 0.016; ids = []
    def bar(a, b, rr=r):
        a = np.asarray(a, float); b = np.asarray(b, float); V, F = tube([a, (a + b) / 2, b], [rr, rr, rr], 6, True); return pr.add(V, F, 0)
    for a, b in [((-hx, -hy, 0), (hx, -hy, 0)), ((hx, -hy, 0), (hx, hy, 0)), ((hx, hy, 0), (-hx, hy, 0)), ((-hx, hy, 0), (-hx, -hy, 0)),
                 ((hx, -hy, 0), (hx, -hy, -dp)), ((-hx, -hy, 0), (-hx, -hy, -dp)), ((hx, hy, 0), (hx, hy, -dp))]: ids.append(bar(a, b))
    for z in W.ZONES[1:3]:      # the zone changes: a gold bar across the near corner post (a tick) on the front and the right
        ids.append(bar((hx, -hy - 0.07, -z), (hx, -hy, -z), 0.012))
        ids.append(bar((hx + 0.07, -hy, -z), (hx, -hy, -z), 0.012))
    pr.build(bpy, [gold], kit.coll, smooth=True)
    for k in range(pr.n): pr.set(k, (0, 0, 0), I3, 1.0)
    out.update(back=back, left=left, top=top, rails=pr)
    # ---- sun shafts in the sunlight zone (static slanted quads near the back wall)
    rm = M.rays(kit, D)
    # the shader reads Object coordinates x (across) and y (along): give each shaft its own object so that holds
    shafts = []
    for k, (x0, w, lean) in enumerate([(-0.85, 0.34, 0.32), (-0.40, 0.22, 0.28), (0.10, 0.42, 0.34), (0.55, 0.26, 0.30), (0.95, 0.34, 0.28)]):
        L = 0.95; y0 = 0.15 + 0.1 * (k % 3)
        # a quad in the xz plane whose local x is across and local y is down: build vertices (u across, v along) -> (x, y0, z) with a lean
        Vk = [(-w / 2, 0.0, 0.0), (w / 2, 0.0, 0.0), (w / 2, -L, 0.0), (-w / 2, -L, 0.0)]
        ob = cw.mk_mesh(bpy, f'fs_shaft{k}', Vk, [(0, 1, 2, 3)], [rm], None, False, kit.coll)
        ob.rotation_euler = (math.pi / 2, 0.0, 0.0)      # stand it up in the xz plane: local y -> world -z
        ob.visible_shadow = False
        shafts.append((ob, x0, y0, lean))
    out['shafts'] = shafts
    # ---- the hole in the sea, directly beneath the slice: deep-water walls and a floor
    hm = M.haze_wall(kit, D)
    X0, X1, Y0, Y1 = -hx - W.HM, hx + W.HM, -hy - W.HM, hy + W.HM; zf = -(dp + W.BASE + 0.05)
    HV = []; HF = []
    def hwall(P0, P1):
        o = len(HV); HV.extend([(P0[0], P0[1], 0.0), (P1[0], P1[1], 0.0), (P1[0], P1[1], zf), (P0[0], P0[1], zf)]); HF.append((o, o + 1, o + 2, o + 3)); HF.append((o + 3, o + 2, o + 1, o))
    hwall((X0, Y1), (X1, Y1)); hwall((X0, Y0), (X0, Y1)); hwall((X1, Y0), (X1, Y1)); hwall((X0, Y0), (X1, Y0))
    o = len(HV); HV.extend([(X0, Y0, zf), (X1, Y0, zf), (X1, Y1, zf), (X0, Y1, zf)]); HF.append((o, o + 1, o + 2, o + 3))
    out['hole'] = cw.mk_mesh(bpy, 'fs_hole', HV, HF, [hm], None, False, kit.coll)
    # ---- the sea: one big flat sheet with a rectangular hole, out to the horizon (world frame, z = 0)
    R = 140.0
    SV = [(-R, -R, 0), (R, -R, 0), (R, R, 0), (-R, R, 0), (X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)]
    SF = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    sea = cw.mk_mesh(bpy, 'fs_sea', SV, SF, [M.sea_world(kit, D)], None, False, kit.coll); sea.visible_shadow = False
    out['sea'] = sea
    return out


def stage_pose(S, D, t):
    z = W.lift(t)
    for k in ('back', 'left', 'top'): S[k].location.z = z
    S['hole'].location.z = 0.0
    pr = S['rails']
    for k in range(pr.n): pr.set(k, (0, 0, z), I3, 1.0)
    pr.commit()
    for ob, x0, y0, lean in S['shafts']:
        ob.location = (x0, y0, z); ob.rotation_euler = (math.pi / 2, 0.0, 0.0)
        sw = 0.04 * math.sin(2 * math.pi * t / 9.0 + x0 * 3.0)
        ob.rotation_euler = (math.pi / 2, math.atan(lean) * -1.0 + sw, 0.0)


def build_far(kit, D, cam, ctx):
    """The far card (see szmats.far_card): held by the camera, 8 m in front of Fable's own backdrop card."""
    bpy = kit.bpy; cd = cam.ob.data; W_, H_ = ctx['W'], ctx['H']
    dist = cam.ob.location.length + 7.0
    sw = cd.sensor_width / 2 / cd.lens * dist
    hw, hh = (sw, sw * H_ / W_) if W_ >= H_ else (sw * W_ / H_, sw)
    k = 1.2; V = [(-hw * k, -hh * k, 0), (hw * k, -hh * k, 0), (hw * k, hh * k, 0), (-hw * k, hh * k, 0)]
    ob = cw.mk_mesh(bpy, 'fs_far', V, [(0, 1, 2, 3)], [M.far_card(kit, D, hw, hh)], None, False, kit.coll)
    ob.parent = cam.ob; ob.matrix_parent_inverse.identity(); ob.location = (0.0, 0.0, -dist); ob.rotation_euler = (0, 0, 0)
    for a in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_shadow', 'visible_volume_scatter'): setattr(ob, a, False)
    return ob
