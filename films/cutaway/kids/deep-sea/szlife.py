"""What lives in the deep sea? The life: the little submarine (and the series' snail in its porthole), the fish, the turtle,
the rubber duck, the lantern fish, jellyfish, the glowing squid, the friendly anglerfish, the hot vent and its tube worms,
marine snow, bubbles, the sparkles of the final bloom, the toys on the seafloor, and the sea's own life (boat, gulls, whale,
island). Each class is ONE mesh of rigid pieces (szgeo.Parts) posed from t every frame (pure functions of time).

Slice frame: z = 0 at the sea surface, depth below it; world = slice + lift(t). Creatures face +x (forward), y to the
left, z up; R = rz(yaw) @ ry(pitch) @ rx(roll) with positive pitch = nose down.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
import szsea as SEA
from szgeo import Parts, I3, rx, ry, rz, sphere, tube, cone, box, disc

B = W.B
SQ2 = math.sqrt(2.0)


def SD(kit, D, name, color, **k):
    """A creature of the deep: like M.sea, but it keeps a floor of light so it reads as a dim coloured shape in the dark."""
    k.setdefault('keep', 0.5); return M.sea(kit, D, name, color, **k)


def orient(yaw=0.0, pitch=0.0, roll=0.0): return rz(yaw) @ ry(pitch) @ rx(roll)


def put(pr, k, P, R, sc, off, Rl=None, s=(1.0, 1.0, 1.0)):
    """Place piece k of a creature at world position P, orientation R, size sc: at local offset `off` (in units of sc), with
    its own local rotation Rl and its own scale s."""
    p = np.asarray(P, float) + R @ (sc * np.asarray(off, float)); pr.set(k, p, R if Rl is None else R @ Rl, sc * np.asarray(s, float))


def dome(r=(1, 1, 1), sub=2):
    """The upper half of a sphere (a jellyfish bell): vertices and faces."""
    V, F = sphere((0, 0, 0), r, sub); keep = [f for f in F if all(V[i][2] >= -1e-6 for i in f)]
    used = sorted({i for f in keep for i in f}); mp = {o: n for n, o in enumerate(used)}
    return V[used], [tuple(mp[i] for i in f) for f in keep]


def wz(t): return W.lift(t)


def slice_to_world(p, t): return np.array([p[0], p[1], p[2] + W.lift(t)], float)


# ====================================================================================== the submarine and its snail
SUB_K = 1.6


def build_sub(kit, D):
    pr = Parts('fs_sub')
    hull = M.sea(kit, D, 'fs_subhull', (0.95, 0.40, 0.30), shade=0.30, tex=0.04, keep=0.6)
    cream = M.sea(kit, D, 'fs_subcream', (0.99, 0.92, 0.76), shade=0.22, tex=0.02, keep=0.6)
    teal = M.sea(kit, D, 'fs_subteal', (0.12, 0.52, 0.58), shade=0.28, tex=0.02, keep=0.6)
    cabin = M.glow(kit, D, 'fs_subcabin', (0.80, 0.94, 0.92), 0.9)                     # the lit cabin seen through the porthole
    lamp = M.glow(kit, D, 'fs_sublamp', (1.0, 0.96, 0.78), 1.0, 'lampA')
    snail_s = M.sea(kit, D, 'fs_snshell', (0.96, 0.52, 0.40), shade=0.2, tex=0.0, lamps=False, flat=True)
    snail_b = M.sea(kit, D, 'fs_snband', (0.99, 0.82, 0.38), shade=0.2, tex=0.0, lamps=False, flat=True)
    snail_m = M.sea(kit, D, 'fs_snbody', (0.90, 0.88, 0.70), shade=0.2, tex=0.0, lamps=False, flat=True)
    snail_e = M.glow(kit, D, 'fs_sneye', (0.10, 0.10, 0.18), 1.0)
    mats = [hull, cream, teal, cabin, lamp, snail_s, snail_b, snail_m, snail_e]
    s = {}
    s['hull'] = pr.add(*sphere((0, 0, 0), (0.31, 0.185, 0.185), 3), m=0)
    s['belly'] = pr.add(*sphere((0.0, 0, -0.065), (0.27, 0.15, 0.13), 2), m=1)
    ring = lambda x, r: [(x, r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 29)]
    s['stripe0'] = pr.add(*tube(ring(-0.115, 0.1845 * 0.92 + 0.012), [0.011] * 29, 6, False), m=1)
    s['stripe1'] = pr.add(*tube(ring(-0.195, 0.1845 * 0.78 + 0.012), [0.011] * 29, 6, False), m=1)
    s['tower'] = pr.add(*tube([(0, 0, 0.0), (0, 0, 0.05), (0, 0, 0.10)], [0.05, 0.048, 0.042], 10, True), m=2, pivot=(0, 0, 0))
    s['tdome'] = pr.add(*sphere((0, 0, 0.0), (0.050, 0.044, 0.030), 2), m=2)
    s['peri'] = pr.add(*tube([(0, 0, 0), (0, 0, 0.09), (0.03, 0, 0.12), (0.06, 0, 0.12)], [0.010, 0.010, 0.010, 0.010], 6, True), m=1)
    pring = [(0.0, 0.082 * math.cos(a), 0.082 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)]     # a ring in the y-z plane, then turned to face -y
    s['port'] = pr.add(*tube(pring, [0.016] * 25, 7, False), m=1)
    s['glass'] = pr.add(*sphere((0, 0, 0), (0.024, 0.076, 0.076), 2), m=3)
    s['lamp'] = pr.add(*sphere((0, 0, 0), (0.03, 0.03, 0.03), 2), m=4)
    s['hub'] = pr.add(*sphere((0, 0, 0), (0.03, 0.026, 0.026), 2), m=2)
    s['blade'] = [pr.add(*sphere((0, 0, 0.055), (0.012, 0.025, 0.06), 1), m=2) for _ in range(3)]
    s['fin_v'] = pr.add(*sphere((0, 0, 0), (0.075, 0.012, 0.075), 2), m=2)
    s['fin_h'] = pr.add(*sphere((0, 0, 0), (0.075, 0.075, 0.012), 2), m=2)
    # the snail in the porthole (the series' mascot): shell, band, body, two eye stalks with eyes
    s['sn_shell'] = pr.add(*sphere((0, 0, 0.030), (0.026, 0.017, 0.028), 2), m=5)
    s['sn_band'] = pr.add(*sphere((0, 0, 0.030), (0.016, 0.0185, 0.018), 2), m=6)
    s['sn_body'] = pr.add(*sphere((0.012, 0, 0.007), (0.040, 0.012, 0.008), 2), m=7)
    s['sn_stalks'] = [pr.add(*tube([(0, 0, 0), (0.004, sd * 0.004, 0.022)], [0.0025, 0.0018], 5), m=7) for sd in (-1, 1)]
    s['sn_eyes'] = [pr.add(*sphere((0.004, sd * 0.004, 0.024), (0.0035, 0.0035, 0.0035), 1), m=8) for sd in (-1, 1)]
    pr.build(kit.bpy, mats, kit.coll)
    # the headlamp's cone of light and the lure's cone (cone meshes, apex at the origin, axis +z, length 1)
    cv_, cf_ = cone((0, 0, 0), 0.0, 1.0, 20, 0.34)
    bm_l = M.beam(kit, D, 'fs_beamm_l', (1.0, 0.96, 0.80), 'lampA', 0.34)
    bm_u = M.beam(kit, D, 'fs_beamm_u', (1.0, 0.86, 0.48), 'lureA', 0.40)
    # cone() builds base at z=0 widening to r_top at z=h; we want the apex at z=0: build it as r at 0 -> r_top at h
    b1 = cw.mk_mesh(kit.bpy, 'fs_beam', cv_, cf_, [bm_l], None, True, kit.coll); b1.visible_shadow = False
    b2 = cw.mk_mesh(kit.bpy, 'fs_beam_lure', cv_, cf_, [bm_u], None, True, kit.coll); b2.visible_shadow = False
    return {'parts': pr, 's': s, 'beam': b1, 'beam_u': b2}


def sub_state(t):
    """Position (slice frame), orientation and speed of the submarine at t."""
    d = W.sub_depth(t); x = W.sub_x(t); y = W.sub_y(t)
    bob = 0.010 * math.sin(2 * math.pi * t / 3.2) * (1.0 - W.sm(0.0, 0.3, d))
    pos = np.array([x, y, -d + bob], float)
    # the nose follows the heading a little: slalom -> yaw; pitch from the story
    dt = 0.15; vx = (W.sub_x(t + dt) - W.sub_x(t - dt)) / (2 * dt); vz = -(W.sub_depth(t + dt) - W.sub_depth(t - dt)) / (2 * dt)
    yaw = 0.14 * math.sin(2 * math.pi * t / 6.0) + 0.0 * vx
    pitch = W.sub_pitch(t) + 0.03 * math.sin(2 * math.pi * t / 4.4)
    roll = 0.05 * math.sin(2 * math.pi * t / 5.3 + 1.0)
    return pos, orient(yaw, pitch, roll), vx, vz


def sub_pose(Sb, D, t):
    pr = Sb['parts']; s = Sb['s']; pos, R, vx, vz = sub_state(t); z0 = wz(t); P = pos + np.array([0, 0, z0]); k = SUB_K
    put(pr, s['hull'], P, R, k, (0, 0, 0)); put(pr, s['belly'], P, R, k, (0.02, 0, -0.0), None, (1, 1, 1))
    pr.hide(s['belly'])
    put(pr, s['stripe0'], P, R, k, (0, 0, 0)); put(pr, s['stripe1'], P, R, k, (0, 0, 0))
    put(pr, s['tower'], P, R, k, (-0.01, 0, 0.145)); put(pr, s['tdome'], P, R, k, (-0.01, 0, 0.245))
    put(pr, s['peri'], P, R, k, (0.03, 0, 0.255))
    # the porthole faces the camera (-y side), forward of the middle; a little turn to show its round face
    pc = (0.115, -0.152, 0.02)
    # ring and glass are built in the y-z plane (axis x); they are fine as is: the porthole's axis points along +x, so turn them to -y
    Rt = rz(-math.pi / 2)
    put(pr, s['port'], P, R, k, pc, Rt); put(pr, s['glass'], P, R, k, (pc[0], pc[1] + 0.005, pc[2]), Rt)
    put(pr, s['lamp'], P, R, k, (0.318, 0, -0.01), None, (1, 1, 1))
    put(pr, s['hub'], P, R, k, (-0.318, 0, 0.0))
    spin = 2 * math.pi * 2.2 * t + 0.0
    for j, b in enumerate(s['blade']): put(pr, b, P, R, k, (-0.335, 0, 0), rx(spin + j * 2 * math.pi / 3))
    put(pr, s['fin_v'], P, R, k, (-0.26, 0, 0.10)); put(pr, s['fin_h'], P, R, k, (-0.26, 0, 0.0))
    # the snail inside the porthole: faces +x, rides in the glass; peeks at the start, looks around, waves at the squid, the lure and the end
    wave = max(W.win(t, B.snwave0, B.snwave1, 0.4), W.win(t, B.snwave2, B.snwave3, 0.4), W.win(t, B.end_wave0, B.end_wave1, 0.4))
    look = 0.5 * math.sin(2 * math.pi * t / 6.0)
    base = np.array([pc[0] - 0.010, pc[1] + 0.012, pc[2] - 0.05]) / k; sk = 0.85
    Rs = rz(0.0)
    for nm in ('sn_shell', 'sn_band', 'sn_body'): put(pr, s[nm], P, R, k, base, Rs, (sk, sk, sk))
    head = base + np.array([0.040 * sk, 0, 0.010 * sk])
    for j, ph in zip(s['sn_stalks'] + s['sn_eyes'], (0, 1, 0, 1)):
        wob = rx(0.25 * math.sin(2 * math.pi * 0.5 * t + ph) + (0.7 * wave * math.sin(2 * math.pi * 1.7 * t)) * (1 if ph == 0 else -1))
        up = 1.0 + 0.6 * wave
        put(pr, j, P, R, k, head, Rs @ wob, (sk, sk, sk * up))
    pr.commit()
    # lamp and beams (world positions for the shader, cone meshes for the picture)
    dirw = R @ np.array([1.0, 0, 0]); tip = P + R @ (k * np.array([0.33, 0, -0.01]))
    D.setv('lampP', tip); D.setv('lampD', dirw)
    on = W.keys(t, [(20.4, 0.0), (21.6, 1.0), (B.lamp_off, 1.0), (B.lamp_off + 0.8, 0.0), (B.lamp_on, 0.0), (B.lamp_on + 0.9, 1.0), (63.0, 1.0), (65.0, 0.0)])
    D.set('lampA', on)
    from mathutils import Vector
    b = Sb['beam']; b.hide_render = on < 0.02
    if on >= 0.02:
        q = Vector((0, 0, 1)).rotation_difference(Vector(tuple(dirw))); b.location = tuple(tip); b.rotation_euler = q.to_euler(); b.scale = (1.0, 1.0, 1.5)
    return P, R


# ====================================================================================== fish (sunlight zone)
FISH_N = 14


def fish_parts(kit, D, name, n, cols, eye=(0.075, 0.062), keep=0.0):
    pr = Parts(name); mats = [M.sea(kit, D, f'{name}_c{i}', c, shade=0.28, tex=0.04, keep=keep) for i, c in enumerate(cols)]
    mats += [M.sea(kit, D, name + '_w', (1.0, 1.0, 1.0), shade=0.05, tex=0.0, lamps=False, flat=True), M.glow(kit, D, name + '_p', (0.07, 0.07, 0.18), 1.0)]
    nc = len(cols); fi = []
    for i in range(n):
        c = i % nc
        d = {'body': pr.add(*sphere((0, 0, 0), (0.5, 0.17, 0.22), 2), m=c),
             'tail': pr.add(*sphere((-0.13, 0, 0), (0.15, 0.025, 0.17), 1), m=c, pivot=(0, 0, 0)),
             'fin': pr.add(*sphere((0, 0, 0.0), (0.12, 0.02, 0.10), 1), m=c),
             'ew': [pr.add(*sphere((0, 0, 0), (eye[0],) * 3, 1), m=nc) for _ in range(2)],
             'ep': [pr.add(*sphere((0, 0, 0), (eye[1],) * 3, 1), m=nc + 1) for _ in range(2)]}
        fi.append(d)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'f': fi}


def fish_put(pr, d, P, R, sc, t, ph, wag=1.0, show=1.0, sw=0.5):
    if show < 0.02:
        for k in [d['body'], d['tail'], d['fin']] + d['ew'] + d['ep']: pr.hide(k)
        return
    put(pr, d['body'], P, R, sc, (0, 0, 0), None, (show, show, show))
    wg = 0.5 * wag * math.sin(2 * math.pi * 1.8 * t + ph * 7.0)
    put(pr, d['tail'], P, R, sc * show, (-0.46, 0, 0), rz(wg)); put(pr, d['fin'], P, R, sc * show, (0.02, 0, 0.2), None)
    for j, sd in enumerate((-1, 1)):
        put(pr, d['ew'][j], P, R, sc * show, (0.28, sd * 0.125, 0.07)); put(pr, d['ep'][j], P, R, sc * show, (0.31, sd * 0.157, 0.075))


def build_fish(kit, D):
    return fish_parts(kit, D, 'fs_fish', FISH_N, [(1.0, 0.82, 0.22), (1.0, 0.54, 0.32), (0.30, 0.52, 0.96)])


def fish_pose(Fi, t):
    pr = Fi['parts']; rng = np.random.default_rng(3)
    ph = rng.uniform(0, 6.28, FISH_N); ax = rng.uniform(0.28, 0.55, FISH_N); ay = rng.uniform(0.18, 0.34, FISH_N); w = rng.uniform(0.36, 0.55, FISH_N)
    cx = rng.uniform(0.10, 0.30, FISH_N); cz = rng.uniform(0.20, 0.62, FISH_N); sc = rng.uniform(0.25, 0.32, FISH_N); dirn = rng.choice([-1, 1], FISH_N)
    z0 = wz(t); vis = W.sm(14.0, 17.0, t)        # as the water darkens the sunlight fish drift off and fade (by shrinking) in the twilight
    gone = 1.0 - W.sm(11.5, 13.0, t)
    tt = t if t < 12.5 else 12.5
    for i, d in enumerate(Fi['f']):
        a = dirn[i] * w[i] * tt + ph[i]
        x = 0.38 + cx[i] * 0.4 + 0.5 * ax[i] * math.cos(a); y = -0.12 + ay[i] * math.sin(a) * 1.6; z = -cz[i] + 0.04 * math.sin(1.3 * t + ph[i])
        vx = -dirn[i] * ax[i] * 1.9 * math.sin(a); vy = dirn[i] * ay[i] * 1.6 * math.cos(a)
        yaw = math.atan2(vy, vx)
        # keep them clear of the front and the walls
        fish_put(pr, d, (x, y, z + z0), orient(yaw, 0.0, 0.08 * math.sin(1.1 * t + ph[i])), sc[i], t, ph[i], 1.0, gone)
    pr.commit()


# ====================================================================================== the turtle
def build_turtle(kit, D):
    pr = Parts('fs_turtle')
    shell = M.sea(kit, D, 'fs_tshell', (0.18, 0.62, 0.46), shade=0.3, tex=0.05); plate = M.sea(kit, D, 'fs_tplate', (0.52, 0.84, 0.58), shade=0.2, tex=0.03)
    skin = M.sea(kit, D, 'fs_tskin', (0.64, 0.82, 0.50), shade=0.25, tex=0.03); belly = M.sea(kit, D, 'fs_tbelly', (0.97, 0.90, 0.66), shade=0.2, tex=0.02)
    eyew = M.sea(kit, D, 'fs_tew', (1, 1, 1), shade=0.05, tex=0.0, lamps=False, flat=True); eyep = M.glow(kit, D, 'fs_tep', (0.07, 0.07, 0.18), 1.0)
    s = {'shell': pr.add(*sphere((0, 0, 0.05), (0.52, 0.42, 0.28), 2), m=0), 'belly': pr.add(*sphere((0, 0, -0.04), (0.46, 0.36, 0.14), 2), m=3),
         'head': pr.add(*sphere((0, 0, 0), (0.17, 0.14, 0.14), 2), m=2), 'tail': pr.add(*sphere((0, 0, 0), (0.12, 0.04, 0.04), 1), m=2),
         'plates': [pr.add(*sphere((0, 0, 0), (0.10, 0.10, 0.03), 1), m=1) for _ in range(5)],
         'fl': [pr.add(*sphere((0.0, 0, 0), (0.24, 0.08, 0.025), 1), m=2, pivot=(-0.17, 0, 0)) for _ in range(4)],
         'ew': [pr.add(*sphere((0, 0, 0), (0.05, 0.05, 0.05), 1), m=4) for _ in range(2)], 'ep': [pr.add(*sphere((0, 0, 0), (0.028, 0.028, 0.028), 1), m=5) for _ in range(2)]}
    pr.build(kit.bpy, [shell, plate, skin, belly, eyew, eyep], kit.coll)
    return {'parts': pr, 's': s}


def turtle_path(t):
    """Slice frame: the turtle glides in from the left at depth 0.4 to 0.55, across the front, and out through the right (shrinks
    behind the sub's wake): visible 3 to 15 s."""
    u = (t - 2.0) / 13.5
    x = -1.0 + 2.0 * u; y = -0.30 + 0.06 * math.sin(2.5 * u); z = -(0.42 + 0.10 * math.sin(3.0 * u))
    return np.array([x, y, z]), math.atan2(0.0, 1.0) + 0.14 * math.sin(3.0 * u)


def turtle_pose(Tu, t):
    pr = Tu['parts']; s = Tu['s']; show = W.win(t, 2.0, 15.2, 0.9)
    allp = [s['shell'], s['belly'], s['head'], s['tail']] + s['plates'] + s['fl'] + s['ew'] + s['ep']
    if show < 0.02:
        for k in allp: pr.hide(k)
        pr.commit(); return
    p, yaw = turtle_path(t); P = p + np.array([0, 0, wz(t)]); R = orient(yaw, 0.04 * math.sin(2 * math.pi * t / 3.0), 0.05 * math.sin(2 * math.pi * t / 5.0)); sc = 0.36 * show
    put(pr, s['shell'], P, R, sc, (0, 0, 0)); put(pr, s['belly'], P, R, sc, (0, 0, 0))
    bob = 0.12 * math.sin(2 * math.pi * t / 2.5)
    put(pr, s['head'], P, R, sc, (0.58, 0, 0.06 + 0.02 * math.sin(2 * math.pi * t / 4.0)), ry(0.1)); put(pr, s['tail'], P, R, sc, (-0.54, 0, 0.0), rz(0.3 * math.sin(2 * math.pi * t / 2.0)))
    for j, (px, py) in enumerate([(-0.18, 0.12), (0.12, -0.07), (0.01, 0.0), (0.0, 0.0), (-0.3, 0.0)]):
        put(pr, s['plates'][j], P, R, sc, (px, py, 0.31 - 0.28 * (abs(px) + abs(py)) * 0.6))
    flap = 0.5 * math.sin(2 * math.pi * t / 2.5)
    put(pr, s['fl'][0], P, R, sc, (0.22, 0.30, -0.03), rz(0.9) @ rx(-0.2 + flap)); put(pr, s['fl'][1], P, R, sc, (0.22, -0.30, -0.03), rz(-0.9) @ rx(0.2 - flap))
    put(pr, s['fl'][2], P, R, sc, (-0.22, 0.26, -0.03), rz(2.3) @ rx(-0.2 + 0.6 * flap)); put(pr, s['fl'][3], P, R, sc, (-0.22, -0.26, -0.03), rz(-2.3) @ rx(0.2 - 0.6 * flap))
    for j, sd in enumerate((-1, 1)):
        put(pr, s['ew'][j], P, R, sc, (0.66, sd * 0.09, 0.12)); put(pr, s['ep'][j], P, R, sc, (0.695, sd * 0.10, 0.125))
    pr.commit()


# ====================================================================================== the rubber duck on the surface
def build_duck(kit, D):
    pr = Parts('fs_duck')
    y = M.sea(kit, D, 'fs_duck_y', (1.0, 0.84, 0.16), shade=0.3, tex=0.03); o = M.sea(kit, D, 'fs_duck_o', (1.0, 0.50, 0.12), shade=0.3, tex=0.02)
    k = M.glow(kit, D, 'fs_duck_k', (0.08, 0.08, 0.16), 1.0); w = M.sea(kit, D, 'fs_duck_w', (1, 1, 1), shade=0.05, tex=0.0, lamps=False, flat=True)
    s = {'body': pr.add(*sphere((0, 0, 0.12), (0.50, 0.38, 0.32), 2), m=0), 'head': pr.add(*sphere((0.34, 0, 0.42), (0.26, 0.24, 0.25), 2), m=0),
         'beak': pr.add(*sphere((0.58, 0, 0.38), (0.15, 0.11, 0.05), 2), m=1), 'tail': pr.add(*sphere((-0.50, 0, 0.30), (0.17, 0.08, 0.12), 2), m=0),
         'wing': [pr.add(*sphere((-0.05, sd * 0.31, 0.16), (0.27, 0.06, 0.15), 2), m=0) for sd in (-1, 1)],
         'ew': [pr.add(*sphere((0.46, sd * 0.13, 0.50), (0.052, 0.052, 0.052), 1), m=3) for sd in (-1, 1)],
         'ep': [pr.add(*sphere((0.495, sd * 0.14, 0.505), (0.030, 0.030, 0.030), 1), m=2) for sd in (-1, 1)]}
    pr.build(kit.bpy, [y, o, k, w], kit.coll); return {'parts': pr, 's': s}


DUCK_XY = (-0.62, -0.20)


def duck_pose(Du, t):
    pr = Du['parts']; s = Du['s']; sc = 0.15; z0 = wz(t)
    bob = 0.012 * math.sin(2 * math.pi * t / 3.0 + 0.5); sq = W.win(t, B.duck_hop0, B.duck_hop1, 0.12) + W.win(t, B.end_duck0, B.end_duck1, 0.12)
    P = np.array([DUCK_XY[0], DUCK_XY[1], z0 - 0.04 + bob + 0.03 * sq]); R = orient(0.6 + 0.35 * math.sin(2 * math.pi * t / 9.0), 0.0, 0.10 * math.sin(2 * math.pi * t / 3.0 + 1.0) + 0.25 * sq * math.sin(40 * t))
    for k in [s['body'], s['head'], s['beak'], s['tail']] + s['wing'] + s['ew'] + s['ep']: put(pr, k, P, R, sc, (0, 0, 0))
    pr.commit()


# ====================================================================================== glow envelopes (the animals' own light)
def bloom_env(t, delay=0.0):
    """The whole slice's lights on together at the climax, going out one by one on the way up."""
    return W.win(t, B.bloom0 + delay, B.bloom1 + 1.6 + delay * 0.5, 0.45)


def jelly_env(t, cue):
    if t >= B.bloom1 + 5.5: return 0.30 * W.sm(B.bloom1 + 5.5, B.bloom1 + 7.0, t)      # a few little lights still twinkle far below at the end
    own = W.sm(cue, cue + 0.9, t) * (1.0 - W.sm(B.bloom1 + 0.3, B.bloom1 + 2.6, t))
    return max(own, bloom_env(t))


# ====================================================================================== twilight: lantern fish and big-eyed fish
LANT_N = 10


def build_lantern(kit, D):
    pr = Parts('fs_lantern')
    body = SD(kit, D, 'fs_lf_b', (0.62, 0.72, 0.92), shade=0.28, tex=0.04); dot = M.glow(kit, D, 'fs_lf_d', (0.55, 0.95, 1.0), 2.2)
    ew = SD(kit, D, 'fs_lf_w', (1, 1, 1), shade=0.05, tex=0.0, lamps=False, flat=True); ep = M.glow(kit, D, 'fs_lf_p', (0.07, 0.07, 0.18), 1.0)
    f = []
    for i in range(LANT_N):
        f.append({'body': pr.add(*sphere((0, 0, 0), (0.5, 0.17, 0.2), 2), m=0), 'tail': pr.add(*sphere((-0.13, 0, 0), (0.15, 0.025, 0.16), 1), m=0),
                  'dots': [pr.add(*sphere((0, 0, 0), (0.07, 0.07, 0.07), 1), m=1) for _ in range(3)],
                  'ew': [pr.add(*sphere((0, 0, 0), (0.075, 0.075, 0.075), 1), m=2) for _ in range(2)], 'ep': [pr.add(*sphere((0, 0, 0), (0.05, 0.05, 0.05), 1), m=3) for _ in range(2)]})
    pr.build(kit.bpy, [body, dot, ew, ep], kit.coll); return {'parts': pr, 'f': f}


def lantern_pose(La, t):
    pr = La['parts']; rng = np.random.default_rng(11); z0 = wz(t)
    sp, _, _, _ = sub_state(t); c = sp
    k = W.win(t, B.lant0, B.lant1, 0.6)      # they come to the submarine on the swell and leave again
    ph = rng.uniform(0, 6.28, LANT_N); rad = rng.uniform(0.32, 0.55, LANT_N); tilt = rng.uniform(-0.6, 0.6, LANT_N); sp_ = rng.uniform(0.9, 1.3, LANT_N)
    for i, d in enumerate(La['f']):
        allp = [d['body'], d['tail']] + d['dots'] + d['ew'] + d['ep']
        if k < 0.02:
            for q in allp: pr.hide(q)
            continue
        a = sp_[i] * 2.2 * (t - B.lant0) + ph[i]; r = rad[i] * (0.4 + 0.6 * k)
        p = c + np.array([r * math.cos(a), 0.2 * math.sin(a * 0.5 + ph[i]) - 0.04, 0.55 * r * math.sin(a) + 0.04 * tilt[i]]) + np.array([0, 0, z0])
        v = np.array([-r * math.sin(a), 0.0, 0.55 * r * math.cos(a)]); yaw = 0.0; pitch = -math.atan2(v[2], v[0]) if v[0] >= 0 else -math.atan2(-v[2], -v[0])
        yaw = 0.0 if v[0] >= 0 else math.pi
        R = orient(yaw, pitch if v[0] >= 0 else -pitch, 0.0); sc = 0.13 * k
        put(pr, d['body'], p, R, sc, (0, 0, 0)); put(pr, d['tail'], p, R, sc, (-0.46, 0, 0), rz(0.5 * math.sin(2 * math.pi * 2.5 * t + ph[i])))
        on = W.sm(B.lant0 + 0.4 + 0.07 * i, B.lant0 + 0.8 + 0.07 * i, t) * (0.85 + 0.15 * math.sin(6 * t + i))
        for j, off in enumerate([(0.1, -0.13, -0.12), (-0.1, -0.15, -0.1), (0.3, -0.12, -0.1)]):
            put(pr, d['dots'][j], p, R, sc * on, off)
        for j, sd in enumerate((-1, 1)):
            put(pr, d['ew'][j], p, R, sc, (0.30, sd * 0.13, 0.07)); put(pr, d['ep'][j], p, R, sc, (0.335, sd * 0.15, 0.075))
    pr.commit()


BIGEYE_N = 3


def build_bigeye(kit, D):
    return fish_parts(kit, D, 'fs_bigeye', BIGEYE_N, [(0.72, 0.80, 0.94), (0.78, 0.70, 0.92), (0.66, 0.84, 0.88)], eye=(0.17, 0.115), keep=0.5)


def bigeye_pose(Bi, t):
    pr = Bi['parts']; z0 = wz(t)
    for i, d in enumerate(Bi['f']):
        t0 = B.twi0 + 0.3 + 1.6 * i; t1 = t0 + 6.4
        u = (t - t0) / (t1 - t0); show = W.win(t, t0, t1, 0.8)
        x = 1.0 - 2.0 * u; y = -0.25 + 0.16 * i - 0.1; z = -(1.05 + 0.22 * i + 0.05 * math.sin(2 * math.pi * u * 2))
        fish_put(pr, d, (x, y, z + z0), orient(math.pi + 0.1 * math.sin(2 * math.pi * u * 2), 0.0, 0.0), 0.30, t, i, 0.7, show)
    pr.commit()


# ====================================================================================== jellyfish
JELLY = [((-0.92, 0.04, -2.05), 0.21, (0.40, 0.72, 1.0), 'jel0', 'B_j0'), ((0.98, 0.22, -1.85), 0.19, (1.0, 0.52, 0.82), 'jel1', 'B_j1'),
         ((-0.30, 0.32, -1.85), 0.20, (0.62, 1.0, 0.60), 'jel2', 'B_j2'), ((0.40, -0.02, -1.30), 0.19, (0.86, 0.82, 1.0), 'jel3', 'B_j3')]
JEL_CUE = None


def build_jelly(kit, D):
    pr = Parts('fs_jelly'); mats = []
    for i, (p, s, c, dr, ev) in enumerate(JELLY):
        mats.append(SD(kit, D, f'fs_jb{i}', tuple(x * 0.55 for x in c), shade=0.2, tex=0.03, glow=2.1, glow_color=c, glow_drive=dr))
        mats.append(SD(kit, D, f'fs_jt{i}', tuple(x * 0.65 for x in c), shade=0.1, tex=0.0, glow=1.6, glow_color=c, glow_drive=dr))
    eye = M.glow(kit, D, 'fs_je', (0.10, 0.08, 0.20), 1.0); hi = M.glow(kit, D, 'fs_jh', (1.0, 1.0, 1.0), 1.0); bl = M.glow(kit, D, 'fs_jbl', (1.0, 0.55, 0.65), 0.9)
    mats += [eye, hi, bl]; ne = len(JELLY) * 2
    J = []
    for i in range(len(JELLY)):
        J.append({'bell': pr.add(*dome((0.5, 0.5, 0.42), 3), m=2 * i), 'rim': pr.add(*tube([(0.5 * math.cos(a), 0.5 * math.sin(a), 0.0) for a in np.linspace(0, 2 * math.pi, 25)], [0.035] * 25, 6, False), m=2 * i),
                  'tent': [pr.add(*tube([(0, 0, 0), (0, 0, -0.25), (0, 0, -0.5), (0, 0, -0.75)], [0.026, 0.02, 0.014, 0.006], 6, True), m=2 * i + 1, pivot=(0, 0, 0)) for _ in range(6)],
                  'arm': [pr.add(*tube([(0, 0, 0), (0, 0, -0.18), (0, 0, -0.34)], [0.06, 0.05, 0.02], 6, True), m=2 * i + 1) for _ in range(2)],
                  'eye': [pr.add(*sphere((0, 0, 0), (0.055, 0.055, 0.055), 1), m=ne) for _ in range(2)], 'hi': [pr.add(*sphere((0, 0, 0), (0.02, 0.02, 0.02), 1), m=ne + 1) for _ in range(2)],
                  'bl': [pr.add(*sphere((0, 0, 0), (0.06, 0.02, 0.04), 1), m=ne + 2) for _ in range(2)]})
    pr.build(kit.bpy, mats, kit.coll); return {'parts': pr, 'j': J}


def jelly_pos(i, t):
    p, s, c, dr, ev = JELLY[i]
    return np.array([p[0] + 0.05 * math.sin(2 * math.pi * t / 11.0 + i), p[1] + 0.03 * math.cos(2 * math.pi * t / 9.0 + i), p[2] + 0.05 * math.sin(2 * math.pi * t / 7.0 + 2 * i) + 0.0 * t])


def jelly_pose(Je, D, t):
    pr = Je['parts']; z0 = wz(t); face = rz(math.radians(-62.0))
    for i, d in enumerate(Je['j']):
        p, s, c, dr, ev = JELLY[i]; cue = getattr(B, ev)
        env = jelly_env(t, cue); D.set(dr, env)
        P = jelly_pos(i, t) + np.array([0, 0, z0]); R = orient(0.3 * i, 0.06 * math.sin(2 * math.pi * t / 5.0 + i), 0.05 * math.cos(2 * math.pi * t / 6.0 + i))
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t / 2.4 + i * 1.7); sz = s * 2.3
        put(pr, d['bell'], P, R, sz, (0, 0, 0), None, (1.0 + 0.10 * pulse, 1.0 + 0.10 * pulse, 1.0 - 0.18 * pulse))
        put(pr, d['rim'], P, R, sz, (0, 0, -0.01), None, (1.0 + 0.10 * pulse, 1.0 + 0.10 * pulse, 1.0 - 0.18 * pulse))
        for j, tn in enumerate(d['tent']):
            a = 2 * math.pi * j / 6 + 0.4; sw = 0.32 * math.sin(2 * math.pi * t / 3.0 + j * 1.1 + i)
            put(pr, tn, P, R, sz, (0.40 * math.cos(a) * (1 + 0.10 * pulse), 0.40 * math.sin(a) * (1 + 0.10 * pulse), -0.06), rx(sw) @ ry(0.5 * sw * math.cos(j)))
        for j, ar in enumerate(d['arm']):
            put(pr, ar, P, R, sz, (0.07 * (1 if j else -1), 0.0, -0.05), rx(0.15 * math.sin(2 * math.pi * t / 3.4 + j)))
        for j, sd in enumerate((-1, 1)):
            e = np.array([0.0, 0.0, 0.0]); fx, fy = math.cos(math.radians(-62.0)), math.sin(math.radians(-62.0)); side = np.array([-fy, fx, 0.0])
            base = np.array([fx, fy, 0.0]) * 0.455 + side * (sd * 0.17) + np.array([0, 0, 0.11])
            put(pr, d['eye'][j], P, R, sz, base); put(pr, d['hi'][j], P, R, sz, base + np.array([fx, fy, 0.0]) * 0.03 + np.array([0, 0, 0.025]) + side * 0.015)
            put(pr, d['bl'][j], P, R, sz, np.array([fx, fy, 0.0]) * 0.43 + side * (sd * 0.30) + np.array([0, 0, 0.0]), rz(math.radians(-62.0) + math.pi / 2))
    pr.commit()


# ====================================================================================== the glowing squid
def build_squid(kit, D):
    pr = Parts('fs_squid')
    body = SD(kit, D, 'fs_sq_b', (0.96, 0.58, 0.62), shade=0.25, tex=0.04, glow=0.55, glow_color=(0.9, 0.45, 0.65), glow_drive='squid')
    spot = M.glow(kit, D, 'fs_sq_s', (0.55, 1.0, 0.95), 2.4, 'squid'); ew = SD(kit, D, 'fs_sq_w', (1, 1, 1), shade=0.05, tex=0.0, lamps=False, flat=True)
    ep = M.glow(kit, D, 'fs_sq_p', (0.07, 0.07, 0.18), 1.0)
    s = {'mantle': pr.add(*sphere((0, 0, 0), (0.55, 0.23, 0.23), 3), m=0), 'head': pr.add(*sphere((0, 0, 0), (0.28, 0.25, 0.24), 2), m=0),
         'fin': [pr.add(*sphere((0, 0, 0), (0.20, 0.17, 0.02), 1), m=0, pivot=(0.1, 0, 0)) for _ in range(2)],
         'tent': [pr.add(*tube([(0, 0, 0), (0.15, 0, -0.02), (0.30, 0, 0.0)], [0.045, 0.034, 0.016], 6, True), m=0) for _ in range(6)],
         'spots': [pr.add(*sphere((0, 0, 0), (0.085, 0.085, 0.085), 1), m=1) for _ in range(9)],
         'ew': [pr.add(*sphere((0, 0, 0), (0.115, 0.115, 0.115), 2), m=2) for _ in range(2)], 'ep': [pr.add(*sphere((0, 0, 0), (0.075, 0.075, 0.075), 1), m=3) for _ in range(2)]}
    pr.build(kit.bpy, [body, spot, ew, ep], kit.coll); return {'parts': pr, 's': s}


SQUID_KEYS = None


def squid_path(t):
    ks = [(B.sq0, (0.95, 0.40, -1.62)), (B.sq0 + 1.5, (0.55, 0.05, -1.90)), (B.sq0 + 3.0, (0.0, -0.22, -2.02)), (B.sq0 + 4.5, (-0.5, -0.28, -1.78)), (B.sq1, (-0.92, 0.0, -1.70))]
    return W.spline_keys(t, ks)


def squid_pose(Sq, D, t):
    pr = Sq['parts']; s = Sq['s']; show = W.win(t, B.sq0, B.sq1, 0.5)
    allp = [s['mantle'], s['head']] + s['fin'] + s['tent'] + s['spots'] + s['ew'] + s['ep']
    D.set('squid', max(W.win(t, B.sq0 + 0.3, B.sq1 - 0.2, 0.5), bloom_env(t, 0.1)) * (1.0 if t < B.bloom1 + 1.8 else 0.0))
    if show < 0.02:
        for k in allp: pr.hide(k)
        pr.commit(); return
    p = squid_path(t); v = (squid_path(t + 0.1) - squid_path(t - 0.1)) / 0.2
    P = p + np.array([0, 0, wz(t)]); yaw = math.atan2(v[1], v[0]); pitch = -math.atan2(v[2], math.hypot(v[0], v[1]))
    R = orient(yaw, pitch, 0.1 * math.sin(2 * math.pi * t / 2.0)); sc = 0.62 * show
    jet = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.3)
    put(pr, s['mantle'], P, R, sc, (-0.25, 0, 0), None, (1.0 + 0.04 * jet, 1.0 - 0.08 * jet, 1.0 - 0.08 * jet)); put(pr, s['head'], P, R, sc, (0.34, 0, 0))
    for j, sd in enumerate((-1, 1)): put(pr, s['fin'][j], P, R, sc, (-0.62, sd * 0.10, 0.0), rz(sd * 0.5) @ rx(sd * 0.35 * math.sin(2 * math.pi * 1.6 * t)))
    for j, tn in enumerate(s['tent']):
        a = 2 * math.pi * j / 6; put(pr, tn, P, R, sc, (0.52, 0.10 * math.cos(a), 0.09 * math.sin(a)), ry(0.15 * math.sin(2 * math.pi * t / 1.7 + j)) @ rz(0.3 * math.cos(a)))
    pat = [(-0.1, 0.20, 0.10), (-0.3, 0.18, 0.12), (-0.5, 0.15, 0.09), (-0.2, -0.20, 0.10), (-0.4, -0.17, 0.12), (-0.6, -0.12, 0.08), (-0.15, 0.0, 0.23), (-0.4, 0.0, 0.22), (-0.62, 0.0, 0.17)]
    for j, off in enumerate(pat):
        blink = 0.5 + 0.5 * math.sin(2 * math.pi * 1.3 * t - j * 0.9)
        put(pr, s['spots'][j], P, R, sc, off, None, (0.6 + 0.6 * blink,) * 3)
    for j, sd in enumerate((-1, 1)):
        put(pr, s['ew'][j], P, R, sc, (0.46, sd * 0.17, 0.08)); put(pr, s['ep'][j], P, R, sc, (0.54, sd * 0.185, 0.085))
    pr.commit()


# ====================================================================================== the friendly anglerfish (only some have a lure)
def build_angler(kit, D):
    pr = Parts('fs_angler')
    body = SD(kit, D, 'fs_an_b', (0.46, 0.34, 0.74), shade=0.26, tex=0.04); belly = SD(kit, D, 'fs_an_l', (0.74, 0.64, 0.92), shade=0.2, tex=0.03)
    cheek = SD(kit, D, 'fs_an_c', (1.0, 0.56, 0.68), shade=0.1, tex=0.0, lamps=False)
    ew = SD(kit, D, 'fs_an_w', (1, 1, 1), shade=0.05, tex=0.0, lamps=False, flat=True); ep = M.glow(kit, D, 'fs_an_p', (0.08, 0.06, 0.20), 1.0)
    hi = M.glow(kit, D, 'fs_an_h', (1, 1, 1), 1.0); smile = M.glow(kit, D, 'fs_an_s', (0.20, 0.08, 0.28), 1.0)
    stalk = SD(kit, D, 'fs_an_st', (0.30, 0.22, 0.50), shade=0.15, tex=0.0)
    lure = M.glow(kit, D, 'fs_an_lure', (1.0, 0.90, 0.50), 3.2, 'lure')
    s = {'body': pr.add(*sphere((0, 0, 0), (0.50, 0.42, 0.40), 3), m=0), 'belly': pr.add(*sphere((0.06, 0, -0.14), (0.40, 0.34, 0.27), 2), m=1),
         'tail': pr.add(*sphere((-0.18, 0, 0), (0.24, 0.03, 0.22), 2), m=0, pivot=(0, 0, 0)), 'dors': pr.add(*sphere((0, 0, 0), (0.15, 0.03, 0.12), 2), m=0),
         'sidefin': [pr.add(*sphere((-0.1, 0, 0), (0.15, 0.04, 0.08), 2), m=1, pivot=(0, 0, 0)) for _ in range(2)],
         'ew': [pr.add(*sphere((0, 0, 0), (0.125, 0.125, 0.125), 2), m=2) for _ in range(2)], 'ep': [pr.add(*sphere((0, 0, 0), (0.08, 0.08, 0.08), 2), m=3) for _ in range(2)],
         'hi': [pr.add(*sphere((0, 0, 0), (0.028, 0.028, 0.028), 1), m=4) for _ in range(2)], 'cheek': [pr.add(*sphere((0, 0, 0), (0.07, 0.02, 0.05), 1), m=8) for _ in range(2)],
         'smile': pr.add(*tube([(0.0, y, -0.06 * (1 - (y / 0.2) ** 2)) for y in np.linspace(-0.2, 0.2, 13)], [0.014] * 13, 5, True), m=5),
         'stalk': pr.add(*tube([(0, 0, 0), (0.0, 0, 0.22), (0.12, 0, 0.40), (0.30, 0, 0.46), (0.44, 0, 0.40)], [0.020, 0.017, 0.014, 0.013, 0.012], 6, True), m=6),
         'bulb': pr.add(*sphere((0, 0, 0), (0.115, 0.115, 0.115), 2), m=7), 'halo': pr.add(*sphere((0, 0, 0), (0.30, 0.30, 0.30), 2), m=9)}
    halo = M.glow(kit, D, 'fs_an_halo', (1.0, 0.88, 0.45), 2.0, None, 'haloA')
    pr.build(kit.bpy, [body, belly, ew, ep, hi, smile, stalk, lure, cheek, halo], kit.coll)
    pr.ob.visible_shadow = False
    return {'parts': pr, 's': s, 'cheek_mat': cheek}


def angler_state(t):
    """Slice-frame position/yaw of the anglerfish: it slides out from behind the rock at the left, rises to the submarine and
    stays by it; then drifts back down to the dark as the submarine goes on."""
    ks = [(B.an0, (-1.0, -0.20, -2.62)), (B.an0 + 1.5, (-0.90, -0.26, -2.5)), (B.an1 - 3.6, (-0.78, -0.30, -2.40)), (B.an1 - 1.4, (-0.78, -0.30, -2.36)), (B.an1 + 1.4, (-0.82, -0.30, -2.44)), (B.an1 + 3.5, (-0.92, -0.20, -2.66))]
    return W.spline_keys(t, ks)


def angler_pose(An, D, t):
    pr = An['parts']; s = An['s']; show = W.win(t, B.an0, B.an1 + 3.2, 0.6)
    allp = [s['body'], s['belly'], s['tail'], s['dors'], s['smile'], s['stalk'], s['bulb'], s['halo']] + s['sidefin'] + s['ew'] + s['ep'] + s['hi'] + s['cheek']
    lure_on = max(W.win(t, B.lure0, B.lure1, 0.6), bloom_env(t, 0.2)); D.set('lure', lure_on * (1.0 if t < B.bloom1 + 1.8 else 0.0)); D.set('lureA', W.win(t, B.lure0 + 0.3, B.lure1 - 0.2, 0.7))
    if show < 0.02:
        for k in allp: pr.hide(k)
        pr.commit(); D.setv('lureP', (0, 0, 5)); D.set('lureA', 0.0); return None
    p = angler_state(t); P = p + np.array([0, 0, wz(t)]); sc = 0.62 * show
    bobv = 0.04 * math.sin(2 * math.pi * t / 2.6)
    R = orient(0.05 * math.sin(2 * math.pi * t / 3.4), -0.10 + 0.05 * math.sin(2 * math.pi * t / 2.6), 0.0); P = P + np.array([0, 0, bobv])
    put(pr, s['body'], P, R, sc, (0, 0, 0)); put(pr, s['belly'], P, R, sc, (0, 0, 0))
    put(pr, s['tail'], P, R, sc, (-0.52, 0, 0.0), rz(0.35 * math.sin(2 * math.pi * 1.4 * t))); put(pr, s['dors'], P, R, sc, (-0.18, 0, 0.40), ry(0.2))
    for j, sd in enumerate((-1, 1)): put(pr, s['sidefin'][j], P, R, sc, (0.0, sd * 0.40, -0.12), rz(sd * 0.5) @ rx(sd * 0.5 * math.sin(2 * math.pi * 1.4 * t + j)))
    for j, sd in enumerate((-1, 1)):
        put(pr, s['ew'][j], P, R, sc, (0.34, sd * 0.215, 0.13)); put(pr, s['ep'][j], P, R, sc, (0.40, sd * 0.225, 0.14)); put(pr, s['hi'][j], P, R, sc, (0.43, sd * 0.215, 0.18))
        put(pr, s['cheek'][j], P, R, sc, (0.42, sd * 0.25, -0.10))
    put(pr, s['smile'], P, R, sc, (0.485, 0, -0.10), None)
    sw = 0.16 * math.sin(2 * math.pi * t / 2.2) + 0.10 * W.win(t, B.lure0, B.lure1, 0.6) * math.sin(2 * math.pi * 1.1 * t)
    Rs = ry(sw + 0.5 * (1.0 - W.sm(B.lure0 - 1.0, B.lure0 + 0.8, t)) * -1.0 + 0.0)
    put(pr, s['stalk'], P, R, sc, (0.24, 0, 0.30), Rs, (1.45, 1.0, 1.55))
    tipoff = np.array([0.24, 0, 0.30]) + Rs @ (np.array([0.44, 0, 0.40]) * np.array([1.45, 1.0, 1.55]))
    put(pr, s['bulb'], P, R, sc, tipoff, None, (1.0 + 0.10 * math.sin(2 * math.pi * 1.5 * t),) * 3)
    ha = 0.30 * lure_on; D.set('haloA', ha)
    if ha > 0.01: put(pr, s['halo'], P, R, sc, tipoff, None, (1.0 + 0.12 * math.sin(2 * math.pi * 1.5 * t),) * 3)
    else: pr.hide(s['halo'])
    lp = P + R @ (sc * tipoff); D.setv('lureP', lp - np.array([0, 0, 0.0]))
    pr.commit(); return lp


# ====================================================================================== the seafloor: rocks, toys, the hot vent and its tube worms
FZ = SEA.floor_z
VX, VY = SEA.VENT_XY
WORMS = [(0.22 * math.cos(a) + 0.04 * math.sin(3 * a), 0.19 * math.sin(a), 0.30 + 0.12 * ((i * 5) % 4) / 3.0, 0.10 * ((i * 3) % 5 - 2)) for i, a in enumerate(np.linspace(0.2, 2 * math.pi + 0.2, 13)[:-1])]
TOYBOAT = (-0.74, 0.22); SANDAL = (0.10, -0.43); CHEST = (-0.30, 0.34)
ROCKS = [(-1.02, -0.18, 0.30, 0.22), (-0.95, 0.30, 0.22, 0.16), (0.98, -0.30, 0.20, 0.14), (0.15, 0.42, 0.18, 0.12)]     # x, y, size, height


def build_floor_life(kit, D):
    pr = Parts('fs_floorlife')
    rock = SD(kit, D, 'fs_rock', (0.30, 0.30, 0.52), shade=0.3, tex=0.08); rock2 = SD(kit, D, 'fs_rock2', (0.42, 0.36, 0.56), shade=0.3, tex=0.08)
    chim = SD(kit, D, 'fs_chim', (0.26, 0.28, 0.44), shade=0.3, tex=0.08); rimg = M.glow(kit, D, 'fs_chimrim', (1.0, 0.60, 0.22), 2.4, 'ventA')
    cream = SD(kit, D, 'fs_wtube', (0.96, 0.92, 0.82), shade=0.25, tex=0.03); red = SD(kit, D, 'fs_wplume', (0.92, 0.14, 0.20), shade=0.2, tex=0.03, glow=0.5, glow_color=(1.0, 0.25, 0.30), glow_drive='ventA')
    hullr = SD(kit, D, 'fs_thull', (0.90, 0.22, 0.24), shade=0.3, tex=0.02); sail = SD(kit, D, 'fs_tsail', (0.98, 0.96, 0.90), shade=0.2, tex=0.02)
    wood = SD(kit, D, 'fs_twood', (0.55, 0.34, 0.20), shade=0.3, tex=0.03); gold = SD(kit, D, 'fs_tgold', (1.0, 0.80, 0.30), shade=0.2, tex=0.0, glow=0.4, glow_color=(1.0, 0.8, 0.3), glow_drive='chest')
    sole = SD(kit, D, 'fs_sole', (0.98, 0.52, 0.58), shade=0.25, tex=0.02); strap = SD(kit, D, 'fs_strap', (0.18, 0.66, 0.70), shade=0.25, tex=0.02)
    mats = [rock, rock2, chim, rimg, cream, red, hullr, sail, wood, gold, sole, strap]
    s = {'rocks': [pr.add(*sphere((0, 0, 0), (1.0, 0.85, 0.7), 2), m=i % 2) for i in range(len(ROCKS))],
         'chim': [pr.add(*cone((0, 0, -0.05), 0.15 * k, 0.34 * k + 0.05, 14, 0.07 * k), m=2) for k in (1.0, 0.72, 0.55)],
         'rim': pr.add(*tube([(0.07 * math.cos(a), 0.07 * math.sin(a), 0.0) for a in np.linspace(0, 2 * math.pi, 17)], [0.018] * 17, 6, False), m=3),
         'worm': [], 'sandal': [], 'chest': [], 'boat': []}
    for i in range(len(WORMS)):
        tube_ = pr.add(*tube([(0, 0, 0), (0.01, 0, 0.33), (-0.01, 0, 0.66), (0.0, 0, 1.0)], [0.045, 0.040, 0.038, 0.036], 8, True), m=4, pivot=(0, 0, 0))
        feath = [pr.add(*sphere((0, 0, 0.0), (0.016, 0.016, 0.11), 1), m=5, pivot=(0, 0, 0)) for _ in range(7)]
        s['worm'].append({'tube': tube_, 'f': feath, 'col': pr.add(*sphere((0, 0, 0), (0.05, 0.05, 0.03), 1), m=5)})
    # toy boat: hull, mast, sail
    s['boat'] = [pr.add(*sphere((0, 0, 0), (0.17, 0.065, 0.06), 2), m=6), pr.add(*sphere((0.02, 0, 0.0), (0.16, 0.055, 0.04), 1), m=8),
                 pr.add(*tube([(0, 0, 0), (0, 0, 0.30)], [0.008, 0.007], 5, True), m=8), pr.add(*sphere((0, 0, 0), (0.002, 0.095, 0.12), 1), m=7)]
    s['sandal'] = [pr.add(*sphere((0, 0, 0), (0.15, 0.058, 0.011), 2), m=10), pr.add(*tube([(0.02, 0.05, 0), (0.07, 0.0, 0.03), (0.02, -0.05, 0)], [0.008] * 3, 5, True), m=11),
                   pr.add(*tube([(0.07, 0.0, 0.03), (0.11, 0.0, 0.0)], [0.008, 0.008], 5, True), m=11)]
    s['chest'] = [pr.add(*box((0, 0, 0.04), (0.18, 0.11, 0.08)), m=8), pr.add(*sphere((0, 0, 0.08), (0.09, 0.055, 0.045), 2), m=8), pr.add(*box((0.0, 0, 0.055), (0.02, 0.114, 0.12)), m=9),
                  pr.add(*sphere((0.092, 0, 0.07), (0.012, 0.016, 0.016), 1), m=9)]
    pr.build(kit.bpy, mats, kit.coll)
    # the vent's plume: warm shimmering blobs rising
    pm = M.glow(kit, D, 'fs_plume', (1.0, 0.66, 0.34), 1.3, None, 'plumeA')
    pl = Parts('fs_plume')
    for i in range(16): pl.add(*sphere((0, 0, 0), (1, 1, 1), 1), m=0)
    pl.build(kit.bpy, [pm], kit.coll); pl.ob.visible_shadow = False
    return {'parts': pr, 's': s, 'plume': pl}


def floor_pose(Fl, D, t):
    pr = Fl['parts']; s = Fl['s']; z0 = wz(t); Z = lambda x, y: FZ(x, y) + z0
    for i, (x, y, sz, h) in enumerate(ROCKS):
        pr.set(s['rocks'][i], (x, y, Z(x, y) + h * 0.15), rz(i * 1.3), (sz, sz * 0.9, h))
    kk = [(1.0, 0.0, 0.0), (0.72, 0.11, -0.08), (0.55, -0.10, 0.10)]
    for i, k in enumerate(s['chim']): pr.set(k, (VX + kk[i][1], VY + kk[i][2], Z(VX, VY)), I3, 1.0)
    topz = Z(VX, VY) + 0.34 + 0.05 - 0.05; D.setv('ventP', (VX, VY, topz + 0.10 - z0 + z0))
    ventA = max(W.sm(B.vent0 + 0.5, B.vent0 + 3.5, t), 0.0) * (1.0 - W.sm(B.unseen0 + 0.5, B.unseen0 + 2.6, t)) * 0.9
    ventA = max(ventA, 0.0); D.set('ventA', ventA)
    pr.set(s['rim'], (VX, VY, topz - 0.02), I3, 1.0)
    grow = W.sm(B.vent0 + 0.6, B.vent0 + 5.2, t)
    for i, (wx, wy, H, lean) in enumerate(WORMS):
        d = s['worm'][i]; x, y = VX + wx, VY + wy; zb = Z(x, y) - 0.02
        g = 0.35 + 0.65 * grow
        sway = 0.10 * math.sin(2 * math.pi * t / 4.0 + i * 1.3); sway2 = 0.07 * math.cos(2 * math.pi * t / 5.0 + i)
        R = rx(lean * 0.6 + sway2) @ ry(lean + sway)
        pr.set(d['tube'], (x, y, zb), R, (1.0, 1.0, H * 0.45 * g))
        tip = np.array([x, y, zb]) + R @ np.array([0.0, 0.0, H * 0.45 * g])
        pr.set(d['col'], tip, R, (1.0, 1.0, 1.0))
        for j, f in enumerate(d['f']):
            a = 2 * math.pi * j / 7; sp = 0.55 + 0.12 * math.sin(2 * math.pi * t / 2.5 + i + j)
            pr.set(f, tip, R @ rz(a) @ ry(sp), (1.0, 1.0, 0.7 + 0.5 * grow))
    # toys
    bx, by = TOYBOAT; pr.set(s['boat'][0], (bx, by, Z(bx, by) + 0.04), rz(0.5) @ ry(0.0) @ rx(0.5), 1.0); pr.set(s['boat'][1], (bx, by, Z(bx, by) + 0.065), rz(0.5) @ rx(0.5), 1.0)
    R = rz(0.5) @ rx(0.5); pr.set(s['boat'][2], np.array([bx, by, Z(bx, by) + 0.05]) + R @ np.array([0.0, 0, 0.02]), R, 1.0); pr.set(s['boat'][3], np.array([bx, by, Z(bx, by) + 0.05]) + R @ np.array([0.0, 0.0, 0.19]), R, 1.0)
    sx_, sy_ = SANDAL; Rs = rz(2.2) @ ry(-0.08)
    for k in s['sandal']: pr.set(k, (sx_, sy_, Z(sx_, sy_) + 0.012), Rs, 1.0)
    cx, cy = CHEST; Rc = rz(-0.4)
    for k in s['chest']: pr.set(k, (cx, cy, Z(cx, cy) - 0.01), Rc, 1.0)
    D.set('chest', W.pulse(t, B.chest0, B.chest0 + 1.2) * 1.0 + 0.0)
    pr.commit()
    pl = Fl['plume']
    for i in range(16):
        age = ((t / 3.2 + i / 16.0) % 1.0); h = age * 0.95
        x = VX + 0.05 * math.sin(2 * math.pi * (age * 1.5 + i * 0.37)); y = VY + 0.05 * math.cos(2 * math.pi * (age * 1.3 + i * 0.21)); r = 0.035 + 0.09 * age
        sc = r * (1.0 if ventA > 0.02 else 0.0) * (0.0 if age < 0.03 else 1.0)
        pl.set(i, (x, y, topz + 0.02 + h), I3, (sc, sc, sc * 1.3) if sc > 1e-4 else 0.0)
    D.set('plumeA', ventA * 0.34); pl.commit()


# ====================================================================================== marine snow, bubbles, ripples, sparkles
SNOW_N = 56


def build_snow(kit, D):
    pr = Parts('fs_snow'); m = M.sea(kit, D, 'fs_snowm', (0.80, 0.90, 1.0), shade=0.0, tex=0.0, flat=True)
    for i in range(SNOW_N): pr.add(*sphere((0, 0, 0), (1, 1, 1), 0), m=0)
    pr.build(kit.bpy, [m], kit.coll); pr.ob.visible_shadow = False; return {'parts': pr}


def snow_pose(Sn, t):
    pr = Sn['parts']; rng = np.random.default_rng(21); z0 = wz(t); n = SNOW_N
    x0 = rng.uniform(-W.HX + 0.1, W.HX - 0.1, n); y0 = rng.uniform(-W.HY + 0.1, W.HY - 0.12, n); zz = rng.uniform(0.0, W.DEEP - 0.2, n); sp = rng.uniform(0.02, 0.06, n); sz = rng.uniform(0.006, 0.012, n); ph = rng.uniform(0, 6.28, n)
    for i in range(n):
        z = -((zz[i] + sp[i] * t) % (W.DEEP - 0.2)) - 0.05
        x = x0[i] + 0.03 * math.sin(0.5 * t + ph[i]); y = y0[i] + 0.03 * math.cos(0.4 * t + ph[i])
        d = -z; a = 1.0 if d > 0.55 else 0.0          # snow shows in the dark water, not the sunlit shallows
        pr.set(i, (x, y, z + z0), I3, sz[i] * a if a else 0.0)
    pr.commit()


BUB_N = 40


def build_bubbles(kit, D):
    pr = Parts('fs_bubbles'); m = M.glow(kit, D, 'fs_bubm', (0.86, 1.0, 1.0), 1.3, None, 'bubA')
    for i in range(BUB_N): pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), m=0)
    pr.build(kit.bpy, [m], kit.coll); pr.ob.visible_shadow = False; return {'parts': pr}


def bubbles_pose(Bu, D, t):
    pr = Bu['parts']; z0 = wz(t); dt = 0.13; N = BUB_N; cyc = N * dt; D.set('bubA', 0.42)
    for k in range(N):
        n = math.floor((t - k * dt) / cyc); tb = k * dt + n * cyc; age = t - tb
        if age < 0 or age > 3.4 or tb < 0:
            pr.hide(k); continue
        sp, R, vx, vz = sub_state(tb)
        if sp[2] > -0.06:
            pr.hide(k); continue
        rr = np.random.default_rng(k + 17 * (n % 7)); o = R @ (SUB_K * np.array([-0.34, 0.0, 0.03])) + rr.uniform(-0.03, 0.03, 3)
        z = sp[2] + o[2] + 0.22 * age + 0.03 * age * age
        if z > -0.012: pr.hide(k); continue
        x = sp[0] + o[0] + 0.04 * math.sin(2.5 * age + k); y = sp[1] + o[1] + 0.03 * math.cos(2 * age + k)
        pr.set(k, (x, y, z + z0), I3, (0.012 + 0.012 * rr.uniform()) * min(1.0, age * 4))
    pr.commit()


def build_ripples(kit, D):
    pr = Parts('fs_ripples'); m = M.glow(kit, D, 'fs_ripm', (1.0, 1.0, 1.0), 1.2, None, 'ripA')
    N = 8
    for i in range(N): pr.add(*tube([(math.cos(a), math.sin(a), 0.0) for a in np.linspace(0, 2 * math.pi, 33)], [0.035] * 33, 5, False), m=0)
    pr.build(kit.bpy, [m], kit.coll); pr.ob.visible_shadow = False
    # splash droplets: 14 small white spheres on arcs at the dive and the surfacing
    dp = Parts('fs_drops'); dm = M.glow(kit, D, 'fs_dropm', (0.95, 1.0, 1.0), 1.4)
    for i in range(24): dp.add(*sphere((0, 0, 0), (1, 1, 1), 1), m=0)
    dp.build(kit.bpy, [dm], kit.coll); dp.ob.visible_shadow = False
    return {'parts': pr, 'drops': dp, 'N': N}


def ripples_pose(Rp, D, t):
    pr = Rp['parts']; z0 = wz(t); D.set('ripA', 0.55)
    # (time, x, y): the dive, the surfacing; and a small ring round the duck when it squeaks
    ev = [(B.dive, W.sub_x(B.dive), W.sub_y(B.dive)), (B.dive + 0.35, W.sub_x(B.dive), W.sub_y(B.dive)), (B.surf, W.sub_x(B.surf), W.sub_y(B.surf)), (B.surf + 0.4, W.sub_x(B.surf), W.sub_y(B.surf)),
          (B.duck_hop0, DUCK_XY[0], DUCK_XY[1]), (B.end_duck0, DUCK_XY[0], DUCK_XY[1]), (B.dive - 0.6, W.sub_x(B.dive), W.sub_y(B.dive)), (B.surf + 0.8, W.sub_x(B.surf), W.sub_y(B.surf))]
    for i, (t0, x, y) in enumerate(ev):
        age = t - t0
        if 0 <= age < 1.7:
            r = 0.04 + 0.28 * age; fade = 1.0 - age / 1.7
            pr.set(i, (x, y, z0 + 0.004), I3, (r, r * 0.8, 0.2 * fade + 0.01))
        else: pr.hide(i)
    pr.commit()
    dp = Rp['drops']; k = 0
    for (t0, x, y) in [(B.dive, W.sub_x(B.dive), W.sub_y(B.dive)), (B.surf, W.sub_x(B.surf), W.sub_y(B.surf))]:
        for j in range(12):
            age = t - t0 - 0.0
            if 0 <= age < 1.0:
                a = 2 * math.pi * j / 12 + 0.3 * (k % 3); vh = 0.30 + 0.08 * (j % 3); vz = 1.15 + 0.2 * (j % 2)
                px = x + vh * math.cos(a) * age; py = y + vh * math.sin(a) * 0.8 * age; pz = vz * age - 4.0 * age * age
                if pz < 0: dp.hide(k)
                else: dp.set(k, (px, py, pz + z0), I3, 0.018 * (1.0 - age * 0.5))
            else: dp.hide(k)
            k += 1
    dp.commit()


TW_N = 110


def build_twinkles(kit, D):
    pr = Parts('fs_twinkles'); cols = [(0.60, 0.95, 1.0), (1.0, 0.60, 0.86), (1.0, 0.90, 0.50), (0.78, 1.0, 0.72), (0.84, 0.76, 1.0)]
    mats = [M.glow(kit, D, f'fs_tw{i}', c, 2.6) for i, c in enumerate(cols)]
    for i in range(TW_N): pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), m=i % len(cols))
    pr.build(kit.bpy, mats, kit.coll); pr.ob.visible_shadow = False
    rng = np.random.default_rng(5); P = np.zeros((TW_N, 3)); win = np.zeros((TW_N, 2)); kind = np.zeros(TW_N, int)
    for i in range(TW_N):
        if i < 16:             # the twilight lanterns' own plankton on the swell
            kind[i] = 0; P[i] = (rng.uniform(-1.0, 1.0), rng.uniform(-0.5, 0.45), -rng.uniform(0.95, 1.6)); a = B.lant0 + 0.3 + rng.uniform(0, 1.8); win[i] = (a, a + rng.uniform(1.2, 2.4))
        elif i < 48:           # plankton round the jellyfish while they light up
            kind[i] = 1; j = i % 3; c = np.array(JELLY[j][0]); P[i] = c + rng.normal(0, 0.25, 3) * np.array([1.0, 0.8, 1.0]); P[i][2] = min(P[i][2] + 0.1, -1.2)
            a = getattr(B, JELLY[j][4]) + rng.uniform(0.2, 2.8); win[i] = (a, a + rng.uniform(1.5, 3.5))
        else:                  # the final bloom: lights everywhere, from the floor up
            kind[i] = 2; P[i] = (rng.uniform(-1.05, 1.05), rng.uniform(-0.55, 0.5), -rng.uniform(0.9, 2.82)); a = B.bloom0 + 0.9 * (P[i][2] + 2.9) * -0.0 + (2.82 + P[i][2]) * 0.55 + rng.uniform(0, 0.4)
            b = B.bloom1 + 1.6 + rng.uniform(0, 1.4) + (2.82 + P[i][2]) * 0.25; win[i] = (a, b)
    return {'parts': pr, 'P': P, 'win': win, 'kind': kind, 'rng': rng.uniform(0, 6.28, TW_N)}


def twinkles_pose(Tw, t):
    pr = Tw['parts']; z0 = wz(t)
    for i in range(TW_N):
        a, b = Tw['win'][i]; k = W.win(t, a, b, 0.4); ph = Tw['rng'][i]
        if Tw['kind'][i] == 2 and t > B.bloom1 + 5.5: k = 0.55 * W.sm(B.bloom1 + 5.5, B.bloom1 + 7.0, t) if i % 7 == 0 else 0.0
        if k < 0.02: pr.hide(i); continue
        p = Tw['P'][i] + np.array([0.02 * math.sin(t + ph), 0.0, 0.03 * math.sin(0.8 * t + ph)])
        tw = 0.65 + 0.35 * math.sin(2 * math.pi * 1.3 * t + ph * 3.0); s = 0.022 * k * tw * (1.0 + 0.35 * (i % 3))
        pr.set(i, (p[0], p[1], p[2] + z0), I3, s)
    pr.commit()


# ====================================================================================== the message in a bottle (squid beat) and the bubbles of the glass
def build_bottle(kit, D):
    pr = Parts('fs_bottle')
    glass = SD(kit, D, 'fs_bglass', (0.60, 0.92, 0.80), shade=0.15, tex=0.0, alpha='bottleA'); cork = SD(kit, D, 'fs_bcork', (0.80, 0.56, 0.34), shade=0.25, tex=0.03)
    paper = SD(kit, D, 'fs_bpaper', (1.0, 0.94, 0.78), shade=0.15, tex=0.0)
    s = {'body': pr.add(*tube([(-0.12, 0, 0), (0.05, 0, 0), (0.10, 0, 0)], [0.05, 0.05, 0.05], 10, True), m=0), 'neck': pr.add(*tube([(0.10, 0, 0), (0.17, 0, 0), (0.21, 0, 0)], [0.04, 0.022, 0.022], 8, True), m=0),
         'cork': pr.add(*tube([(0.21, 0, 0), (0.245, 0, 0)], [0.020, 0.020], 8, True), m=1), 'scroll': pr.add(*tube([(-0.09, 0, 0), (0.08, 0, 0)], [0.026, 0.026], 8, True), m=2)}
    pr.build(kit.bpy, [glass, cork, paper], kit.coll); return {'parts': pr, 's': s}


def bottle_pose(Bo, D, t):
    pr = Bo['parts']; s = Bo['s']; u = (t - B.bot0) / (B.bot1 - B.bot0); show = W.win(t, B.bot0, B.bot1, 0.7); D.set('bottleA', 0.75)
    if show < 0.02:
        for k in s.values(): pr.hide(k)
        pr.commit(); return
    x = 1.0 - 2.0 * u; y = 0.05; z = -(1.52 + 0.12 * math.sin(2 * math.pi * u * 1.5)); P = np.array([x, y, z + wz(t)])
    R = orient(0.0, 0.5 * math.sin(2 * math.pi * u * 1.5) + 0.2, 0.3 * math.sin(2 * math.pi * u * 2.0))
    for k in s.values(): pr.set(k, P, R, show * 1.0)
    pr.commit()


# ====================================================================================== the sunny sea round the slice: island, boat, beach ball, gulls, whale
def wxy(a, b): return W.world_xy(a, b)


def _gpts(f): return f


def build_world_life(kit, D):
    SW = lambda kit, D, name, color, **k: M.sea(kit, D, name, color, world=True, **{**k, 'lamps': False})
    pr = Parts('fs_isle')
    sand = SW(kit, D, 'fs_isand', (0.98, 0.82, 0.52), shade=0.25, tex=0.05, lamps=False); grass = SW(kit, D, 'fs_igrass', (0.30, 0.74, 0.40), shade=0.3, tex=0.06, lamps=False)
    trunk = SW(kit, D, 'fs_itrunk', (0.62, 0.40, 0.26), shade=0.3, tex=0.04, lamps=False); frond = SW(kit, D, 'fs_ifrond', (0.20, 0.66, 0.38), shade=0.3, tex=0.05, lamps=False)
    nut = SW(kit, D, 'fs_inut', (0.45, 0.30, 0.20), shade=0.3, tex=0.0, lamps=False); bucket = SW(kit, D, 'fs_ibucket', (0.92, 0.18, 0.20), shade=0.3, tex=0.0, lamps=False)
    castle = SW(kit, D, 'fs_icastle', (0.96, 0.76, 0.46), shade=0.4, tex=0.04, lamps=False); flag = SW(kit, D, 'fs_iflag', (0.98, 0.36, 0.52), shade=0.2, tex=0.0, lamps=False)
    mats = [sand, grass, trunk, frond, nut, bucket, castle, flag]
    s = {'sand': pr.add(*sphere((0, 0, 0), (3.0, 2.3, 0.62), 3), m=0), 'hill': pr.add(*sphere((0.5, 0.2, 0.0), (1.9, 1.5, 0.95), 3), m=1),
         'trunk': pr.add(*tube([(0, 0, 0), (0.12, 0, 0.9), (0.05, 0, 1.8), (-0.25, 0, 2.55)], [0.15, 0.12, 0.10, 0.08], 8, True), m=2),
         'fronds': [pr.add(*sphere((0, 0, 0), (0.95, 0.16, 0.05), 2), m=3, pivot=(-0.9, 0, 0)) for _ in range(7)], 'nuts': [pr.add(*sphere((0, 0, 0), (0.11, 0.11, 0.11), 1), m=4) for _ in range(3)],
         'bucket': pr.add(*cone((0, 0, 0), 0.20, 0.26, 12, 0.27), m=5), 'bhandle': pr.add(*tube([(-0.2, 0, 0.2), (0, 0, 0.5), (0.2, 0, 0.2)], [0.016] * 3, 5, True), m=5),
         'castle': [pr.add(*cone((0, 0, 0), 0.22, 0.30, 10, 0.18), m=6), pr.add(*cone((0.3, 0.1, 0), 0.14, 0.22, 10, 0.11), m=6), pr.add(*cone((-0.28, 0.12, 0), 0.14, 0.22, 10, 0.11), m=6)],
         'flag': pr.add(*sphere((0, 0, 0), (0.002, 0.10, 0.07), 1), m=7), 'pole': pr.add(*tube([(0, 0, 0), (0, 0, 0.22)], [0.008, 0.007], 4, True), m=2)}
    pr.build(kit.bpy, mats, kit.coll)
    # the sailing boat
    bt = Parts('fs_boat')
    hull = SW(kit, D, 'fs_bhull', (0.20, 0.42, 0.86), shade=0.3, tex=0.02, lamps=False); white = SW(kit, D, 'fs_bwhite', (0.99, 0.97, 0.92), shade=0.3, tex=0.02, lamps=False)
    red = SW(kit, D, 'fs_bred', (0.95, 0.30, 0.28), shade=0.3, tex=0.0, lamps=False); wood = SW(kit, D, 'fs_bwood', (0.62, 0.40, 0.26), shade=0.3, tex=0.0, lamps=False)
    bs = {'hull': bt.add(*sphere((0, 0, 0.1), (0.9, 0.34, 0.26), 3), m=0), 'deck': bt.add(*sphere((0, 0, 0.26), (0.78, 0.28, 0.05), 2), m=3), 'stripe': bt.add(*sphere((0, 0, 0.22), (0.92, 0.345, 0.04), 2), m=1),
          'mast': bt.add(*tube([(0, 0, 0.2), (0, 0, 2.1)], [0.035, 0.025], 6, True), m=3), 'sail': bt.add(*sphere((0, 0, 0), (0.025, 0.55, 0.85), 2), m=1), 'jib': bt.add(*sphere((0, 0, 0), (0.02, 0.38, 0.60), 2), m=2),
          'flag': bt.add(*sphere((0, 0, 0), (0.02, 0.17, 0.09), 1), m=2)}
    bt.build(kit.bpy, [hull, white, red, wood], kit.coll)
    # the beach ball: six painted panels (pieces, since a posed mesh has no stable object coordinates)
    bm = [SW(kit, D, f'fs_ball{i}', c, shade=0.3, tex=0.0) for i, c in enumerate([(0.95, 0.22, 0.22), (1.0, 0.99, 0.94), (1.0, 0.82, 0.18), (0.20, 0.52, 0.95)])]
    ball = Parts('fs_ball'); bv, bf = sphere((0, 0, 0), (1, 1, 1), 3)
    for q, ci in enumerate([0, 1, 2, 1, 3, 1]):
        fs = []
        for f in bf:
            c = np.mean([bv[i] for i in f], axis=0); az = (math.atan2(c[1], c[0]) / (2 * math.pi)) % 1.0
            if int(az * 6) == q: fs.append(f)
        ball.add(bv, fs, m=ci)
    ball.build(kit.bpy, bm, kit.coll)
    # gulls and whale
    gl = Parts('fs_gulls'); gw = SW(kit, D, 'fs_gull', (0.99, 0.99, 0.98), shade=0.35, tex=0.0, lamps=False); gg = SW(kit, D, 'fs_gullg', (0.64, 0.68, 0.76), shade=0.3, tex=0.0, lamps=False)
    go = SW(kit, D, 'fs_gullo', (1.0, 0.62, 0.16), shade=0.2, tex=0.0, lamps=False); ge = M.glow(kit, D, 'fs_gulle', (0.1, 0.1, 0.18), 1.0)
    G_ = []
    for i in range(5):
        G_.append({'body': gl.add(*sphere((0, 0, 0), (0.30, 0.10, 0.10), 2), m=0), 'head': gl.add(*sphere((0.30, 0, 0.03), (0.09, 0.08, 0.08), 2), m=0), 'beak': gl.add(*sphere((0.41, 0, 0.02), (0.06, 0.02, 0.02), 1), m=2),
                   'tail': gl.add(*sphere((-0.34, 0, 0.0), (0.11, 0.06, 0.012), 1), m=0), 'eye': [gl.add(*sphere((0.35, sd * 0.055, 0.05), (0.014, 0.014, 0.014), 1), m=3) for sd in (-1, 1)],
                   'wing': [gl.add(*sphere((0, sd * 0.30, 0), (0.12, 0.34, 0.02), 2), m=1 if True else 0, pivot=(0, 0, 0)) for sd in (-1, 1)]})
    gl.build(kit.bpy, [gw, gg, go, ge], kit.coll)
    wh = Parts('fs_whale'); wb = SW(kit, D, 'fs_whaleb', (0.34, 0.52, 0.86), shade=0.3, tex=0.03, lamps=False); wl = SW(kit, D, 'fs_whalel', (0.90, 0.95, 1.0), shade=0.2, tex=0.0, lamps=False)
    we = M.glow(kit, D, 'fs_whalee', (0.08, 0.08, 0.18), 1.0)
    ws = {'back': wh.add(*sphere((0, 0, 0), (3.0, 1.1, 0.95), 3), m=0), 'belly': wh.add(*sphere((0.4, 0, -0.35), (2.2, 0.95, 0.6), 2), m=1), 'eye': wh.add(*sphere((0, 0, 0), (0.09, 0.09, 0.09), 1), m=2),
          'fluke': [wh.add(*sphere((0, 0, 0), (0.55, 0.9, 0.06), 2), m=0, pivot=(0.3, 0, 0)) for _ in range(1)], 'smile': wh.add(*tube([(0.0, y, -0.08 * (1 - (y / 0.5) ** 2)) for y in np.linspace(-0.5, 0.5, 9)], [0.02] * 9, 5, True), m=2)}
    wh.build(kit.bpy, [wb, wl, we], kit.coll)
    sp = Parts('fs_spout'); sm_ = M.glow(kit, D, 'fs_spoutm', (0.96, 1.0, 1.0), 1.4, None, 'spoutA')
    for i in range(22): sp.add(*sphere((0, 0, 0), (1, 1, 1), 1), m=0)
    sp.build(kit.bpy, [sm_], kit.coll); sp.ob.visible_shadow = False
    return {'isle': pr, 's': s, 'boat': bt, 'bs': bs, 'ball': ball, 'gulls': gl, 'g': G_, 'whale': wh, 'ws': ws, 'spout': sp}


ISLE = (-4.7, 4.6); WHALE = (3.9, 7.6); BALL = (2.7, 1.6)


def boat_ab(t): return (7.4 - 0.062 * t, 3.4)


def world_life_pose(Wl, D, t):
    pr = Wl['isle']; s = Wl['s']; sea_ = lambda a, b, z=0.0: np.array([*wxy(a, b), z])
    P = sea_(*ISLE, -0.16); face = 0.5
    pr.set(s['sand'], P, rz(0.3), 1.0); pr.set(s['hill'], P + np.array([0, 0, 0.15]), rz(0.3), 1.0)
    tp = P + rz(0.3) @ np.array([0.7, -0.2, 0.42]); pr.set(s['trunk'], tp, rz(0.9), 1.0)
    top = tp + rz(0.9) @ np.array([-0.25, 0, 2.55]); sway = 0.06 * math.sin(2 * math.pi * t / 4.0)
    for j, f in enumerate(s['fronds']):
        a = 2 * math.pi * j / 7 + 0.3; pr.set(f, top, rz(a) @ ry(-0.45 + sway + 0.12 * math.sin(2 * math.pi * t / 3.0 + j)) , 1.0)
    for j, n in enumerate(s['nuts']): pr.set(n, top + np.array([0.12 * math.cos(2.1 * j), 0.12 * math.sin(2.1 * j), -0.14]), I3, 1.0)
    bp = P + rz(0.3) @ np.array([-1.2, -1.45, 0.62]); pr.set(s['bucket'], bp, rz(0.3), 1.0); pr.set(s['bhandle'], bp, rz(0.3 + 1.2), 1.0)
    cp = P + rz(0.3) @ np.array([-0.5, -1.55, 0.62])
    for c, off in zip(s['castle'], [(0, 0, 0), (0, 0, 0), (0, 0, 0)]): pr.set(c, cp, rz(0.3), 1.0)
    pr.set(s['pole'], cp + np.array([0, 0, 0.28]), I3, 1.0); pr.set(s['flag'], cp + np.array([0, 0.06, 0.47]) , rz(0.3 * math.sin(2 * math.pi * t / 1.5)), 1.0)
    pr.commit()
    bt = Wl['boat']; bs = Wl['bs']; a, b = boat_ab(t); bp = sea_(a, b, 0.0); bob = 0.05 * math.sin(2 * math.pi * t / 3.6); heading = math.atan2(-W.RIGHT[1], -W.RIGHT[0])   # sails to the screen left
    R = rz(heading) @ rx(0.05 * math.sin(2 * math.pi * t / 4.2)) @ ry(0.04 * math.sin(2 * math.pi * t / 3.1)); Z = np.array([0, 0, 0.0 + bob])
    for k in ('hull', 'deck', 'stripe'): bt.set(bs[k], bp + Z, R, 1.0)
    bt.set(bs['mast'], bp + Z, R, 1.0); bt.set(bs['sail'], bp + Z + R @ np.array([-0.05, 0.0, 1.15]), R @ ry(0.0), 1.0)
    bt.set(bs['sail'], bp + Z + R @ np.array([-0.05, 0.0, 1.15]), R, (1.0, 1.0, 1.0)); bt.set(bs['jib'], bp + Z + R @ np.array([0.45, 0.0, 0.95]), R, 1.0)
    bt.set(bs['flag'], bp + Z + R @ np.array([0.0, 0.0, 2.1]), R @ rz(0.3 * math.sin(2 * math.pi * t / 1.2)), 1.0)
    bt.commit()
    ball = Wl['ball']; q = sea_(*BALL, 0.05 + 0.04 * math.sin(2 * math.pi * t / 3.3 + 1.0)); [ball.set(k, q, rz(0.05 * t) @ rx(0.1 * math.sin(t)), 0.30) for k in range(6)]; ball.commit()
    gl = Wl['gulls']
    for i, d in enumerate(Wl['g']):
        a0, b0 = [(-2.5, 4.5), (-6.0, 5.0), (3.0, 5.5), (6.5, 4.0), (-0.5, 6.5)][i]; r = 1.6 + 0.5 * (i % 3); w = 0.32 + 0.05 * (i % 2); ph = i * 1.3
        ang = w * t * (1 if i % 2 else -1) + ph; ca, cb = a0 + r * math.cos(ang), b0 + r * 0.6 * math.sin(ang); z = 3.4 + 0.8 * (i % 3) + 0.25 * math.sin(0.9 * t + ph)
        vA = -r * math.sin(ang) * (1 if i % 2 else -1); vB = r * 0.6 * math.cos(ang) * (1 if i % 2 else -1)
        v = W.RIGHT * vA + W.AWAY * vB; yaw = math.atan2(v[1], v[0]); pos = np.array([*wxy(ca, cb), z]); Rg = orient(yaw, 0.0, 0.15 * (1 if i % 2 else -1)); flap = 0.55 * math.sin(2 * math.pi * 2.0 * t + ph)
        for k in [d['body'], d['head'], d['beak'], d['tail']] + d['eye']: put(gl, k, pos, Rg, 1.0, (0, 0, 0)) if False else gl.set(k, pos, Rg, 1.0)
        for j, sd in enumerate((-1, 1)): gl.set(d['wing'][j], pos + Rg @ np.array([0.0, 0.0, 0.0]), Rg @ rx(sd * (-flap)), 1.0)
    gl.commit()
    wh = Wl['whale']; ws = Wl['ws']; WS = 0.62; wp = sea_(*WHALE, -0.08 + 0.06 * math.sin(2 * math.pi * t / 8.0)); Rw = rz(math.atan2(W.RIGHT[1], W.RIGHT[0]) + math.pi + 0.15) @ rx(0.04 * math.sin(2 * math.pi * t / 8.0))
    for k in ('back', 'belly'): wh.set(ws[k], wp, Rw, WS)
    side = Rw @ (WS * np.array([1.75, 0.84, 0.30])); wh.set(ws['eye'], wp + side, Rw, 1.6 * WS); wh.set(ws['smile'], wp + Rw @ (WS * np.array([2.35, 0.70, 0.06])), Rw @ rz(-1.45), WS)
    for f in ws['fluke']: wh.set(f, wp + Rw @ (WS * np.array([-3.05, 0.0, 0.45 + 0.12 * math.sin(2 * math.pi * t / 4.0)])), Rw @ ry(-0.9), WS)
    wh.commit()
    # spouts: a fan of drops from the blowhole
    sp = Wl['spout']; blow = wp + Rw @ (WS * np.array([0.2, 0.0, 0.85])); k = 0; D.set('spoutA', 0.85)
    for t0 in B.spouts:
        age = t - t0
        for j in range(11):
            if 0 <= age < 1.9:
                a = (j - 5) / 5.0; vh = 0.9 * a; vz = 3.2 - 0.4 * abs(a); px = vh * age; pz = vz * age - 2.2 * age * age
                if pz > -0.2 and k < 22: sp.set(k, blow + np.array([*(W.RIGHT * px), pz]) * 1.0 + np.array([0, 0, 0]), I3, 0.11 * (1.0 - 0.4 * age / 1.9)); k += 1
    for q in range(k, 22): sp.hide(q)
    sp.commit()


# ====================================================================================== the torch's small patch of seafloor (only a tiny piece has been seen)
POOL_XY = (0.10, -0.14)


def build_pool(kit, D):
    pr = Parts('fs_pool'); mo = M.glow(kit, D, 'fs_pool_o', (1.0, 0.90, 0.62), 1.0, None, 'poolA'); mi = M.glow(kit, D, 'fs_pool_i', (1.0, 0.95, 0.74), 1.2, None, 'poolB')
    a = pr.add(*disc((0, 0, 0), 0.36, 28), m=0); b = pr.add(*disc((0, 0, 0), 0.22, 28), m=1)
    pr.build(kit.bpy, [mo, mi], kit.coll); pr.ob.visible_shadow = False
    return {'parts': pr, 'a': a, 'b': b}


def pool_pose(Pl, D, t):
    pr = Pl['parts']; on = W.win(t, B.unseen0 + 0.9, B.unseen0 + 4.8, 0.9)
    D.set('poolA', 0.28 * on); D.set('poolB', 0.42 * on)
    if on < 0.02:
        pr.hide(Pl['a']); pr.hide(Pl['b'])
    else:
        x, y = POOL_XY; z = SEA.floor_z(x, y) + 0.03 + wz(t); sq = (1.0 + 0.03 * math.sin(2 * math.pi * t / 2.0))
        pr.set(Pl['a'], (x, y, z), I3, sq); pr.set(Pl['b'], (x, y, z + 0.004), I3, sq)
    pr.commit()
