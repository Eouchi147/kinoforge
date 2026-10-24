"""Who lives under your feet? The cicada thread (bpy + numpy). Every pose is a pure function of t.

One tiny egg on a twig of the big tree hatches (5.3 s); the nymph tumbles to the lawn, shuffles to a little hole and slips in
(8 s); it digs a shaft down the cut face to a root of the tree and sips (12 s). Years pass above (the seasons loop). In the
spring of the seventeenth year (a card says "17 YEARS") the soil warms; it and four others (all together) climb the shaft,
pop out of the lawn (34 s), blink at the sun and march to the tree, climb the trunk (42 s), and on the tree their backs split
(55.55 s) and the grown cicadas ease out, pale, wings crumpled; on the music's biggest climax (59.7 s) the wings snap open, the
bodies darken, the eyes glow red and they sing: gold rings and little notes spread over the park, to the final chord (68 s).
Sound is shown as rings and notes (a picture of singing). Sources: docs/research/KIDS_FACTS_2026-10.md 2.1 (nymphs feed on
root fluid for 13 or 17 years; they emerge together when the soil warms to about 18 C). The egg on the twig and the shell
that splits are added from general knowledge of cicada life; the singing is Sam's brief.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
import szunder as UG
import szpark as PK
from szgeo import Parts, sphere, tube, cone, box, disc, rz, ry, rx, euler, I3

NAMES = ['M', 'S1', 'S2', 'S3', 'S4']
PERCH = {'M': (-1.08 - 0.20, 0.50), 'S1': (-1.08 - 1.05, 0.15), 'S2': (-1.08 + 0.95, 0.30), 'S3': (-1.08 + 0.45, 0.19), 'S4': (-1.08 - 0.55, 0.40)}      # (angle round the trunk, height)


def sm(a, b, t): return W.sm(a, b, t)


def frame_up(n):
    """Frame for a creature on the trunk: its x (forward) is up, its z is the surface normal n (a unit vector)."""
    z = np.asarray(n, float); x = np.array([0.0, 0.0, 1.0]); y = np.cross(z, x); y /= np.linalg.norm(y); return np.column_stack([x, y, z])


def frame_dir(f, up=(0.0, 0.0, 1.0)):
    """Frame whose x is the unit vector f (in 3D) and whose z is as near `up` as possible."""
    x = np.asarray(f, float); x = x / (np.linalg.norm(x) + 1e-9); z = np.asarray(up, float) - x * (np.asarray(up, float) @ x)
    if np.linalg.norm(z) < 1e-6: z = np.array([0.0, 1.0, 0.0]) - x * x[1]
    z /= np.linalg.norm(z); y = np.cross(z, x); return np.column_stack([x, y, z])


def cam_frame():
    a = math.radians(W.VIEW_AZ); e = math.radians(21.0); dv = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    f = -dv; rgt = np.cross(f, (0, 0, 1)); rgt /= np.linalg.norm(rgt); up = np.cross(rgt, f); return np.column_stack([rgt, up, dv])


CAMR = cam_frame()


def build_one(pr):
    c = {}
    c['body'] = pr.add(*sphere((-0.004, 0, 0), (0.050, 0.027, 0.027), 2), m=0)
    c['abd'] = pr.add(*sphere((-0.040, 0, -0.002), (0.034, 0.024, 0.024), 2), m=0)
    c['head'] = pr.add(*sphere((0.050, 0, 0.002), (0.027, 0.026, 0.025), 2), m=1)
    c['eyes'] = [pr.add(*sphere((0.062, sd * 0.017, 0.013), (0.0105, 0.0095, 0.0105), 1), m=2) for sd in (-1, 1)]
    c['glint'] = [pr.add(*sphere((0.069, sd * 0.0185, 0.018), (0.0035, 0.003, 0.0035), 1), m=10) for sd in (-1, 1)]
    c['arms'] = [pr.add(*tube([(0.040, sd * 0.020, -0.012), (0.066, sd * 0.030, -0.028), (0.084, sd * 0.030, -0.040)], [0.0085, 0.0075, 0.0095], 6), m=0) for sd in (-1, 1)]
    c['claws'] = [pr.add(*sphere((0.088, sd * 0.030, -0.044), (0.0105, 0.008, 0.0105), 1), m=3) for sd in (-1, 1)]
    c['legs'] = [pr.add(*tube([(0.0, sd * 0.018, -0.010), (-0.004 + 0.02 * q, sd * 0.040, -0.028), (-0.010 + 0.036 * q, sd * 0.046, -0.046)], [0.0060, 0.0050, 0.0035], 5), m=0) for sd in (-1, 1) for q in (-1, 0, 1)]
    c['slit'] = pr.add(*box((0.0, 0, 0.0262), (0.070, 0.006, 0.004)), m=4)
    c['sip'] = pr.add(*tube([(0.070, 0, -0.010), (0.088, 0, -0.030)], [0.0035, 0.0025], 5), m=9)
    # the grown cicada: body, wide head, red eyes, four wings
    c['a_body'] = pr.add(*sphere((-0.010, 0, 0), (0.060, 0.027, 0.027), 2), m=5)
    c['a_head'] = pr.add(*sphere((0.056, 0, 0.003), (0.023, 0.036, 0.021), 2), m=5)
    c['a_eyes'] = [pr.add(*sphere((0.060, sd * 0.034, 0.006), (0.0155, 0.0125, 0.0155), 2), m=6) for sd in (-1, 1)]
    c['a_glint'] = [pr.add(*sphere((0.068, sd * 0.040, 0.012), (0.004, 0.0035, 0.004), 1), m=10) for sd in (-1, 1)]
    c['a_legs'] = [pr.add(*tube([(0.02 - 0.03 * q, sd * 0.020, -0.008), (0.02 - 0.03 * q + 0.01, sd * 0.040, -0.026), (0.02 - 0.03 * q + 0.016, sd * 0.050, -0.046)], [0.0050, 0.0042, 0.0030], 5), m=8) for sd in (-1, 1) for q in (0, 1, 2)]
    w = []
    for sd in (-1, 1):
        # fore wing (long) and hind wing (shorter) as flat leaf shapes hinged at the shoulder, lying back along the body
        for (L, wd, off) in ((0.200, 0.058, 0.0), (0.150, 0.046, 0.004)):
            pts = [(0.0, 0.0, 0.0), (-0.20 * L, sd * wd * 0.55, 0.0), (-0.55 * L, sd * wd * 0.95, 0.0), (-0.90 * L, sd * wd * 0.75, 0.0), (-L, sd * wd * 0.25, 0.0), (-0.55 * L, sd * wd * 0.05, 0.0)]
            V = [(0.034 + off, sd * 0.022, 0.014)] + [(p[0] + 0.034 + off, p[1] + sd * 0.022, 0.014) for p in pts[1:]]
            wing = pr.add(np.array(V), [(0, 1, 2, 5), (5, 2, 3, 4)] if sd > 0 else [(5, 2, 1, 0), (4, 3, 2, 5)], m=7)
            vein = pr.add(*tube([V[0], V[1], V[2], V[3]], [0.004, 0.0035, 0.003, 0.0025], 4), m=8)
            w.append((wing, vein, sd))
    c['wings'] = w
    return c


def build(kit, D, rng, under, park):
    pr = Parts('fs_cic'); cic = {n: build_one(pr) for n in NAMES}
    mats = [M.paint(kit, D, 'sz_nymph', (0.80, 0.56, 0.30), noise=0.0, drive='nymphcol'), M.paint(kit, D, 'sz_nymphhead', (0.90, 0.68, 0.40), noise=0.0),
            M.paint(kit, D, 'sz_nympheye', (0.08, 0.05, 0.08), noise=0.0), M.paint(kit, D, 'sz_nymphclaw', (0.99, 0.90, 0.72), noise=0.0),
            M.paint(kit, D, 'sz_slit', (0.30, 0.18, 0.10), noise=0.0), M.paint(kit, D, 'sz_adult', (0.20, 0.14, 0.12), noise=0.0, drive='cicbody'),
            M.paint(kit, D, 'sz_redeye', (0.96, 0.16, 0.14), noise=0.0), M.paint(kit, D, 'sz_wing', (1.0, 0.92, 0.70), noise=0.0, alpha='wingalpha'),
            M.paint(kit, D, 'sz_vein', (0.96, 0.58, 0.20), noise=0.0), M.paint(kit, D, 'sz_proboscis', (0.96, 0.86, 0.70), noise=0.0),
            M.paint(kit, D, 'sz_glintw', (1.0, 1.0, 1.0), noise=0.0)]
    pr.build(kit.bpy, mats, kit.coll)
    # egg on a twig
    pe = Parts('fs_egg'); em = [M.paint(kit, D, 'sz_eggshell', (0.99, 0.95, 0.80), noise=0.0), M.paint(kit, D, 'sz_twig', (0.46, 0.30, 0.22), noise=0.0)]
    eggs = [pe.add(*sphere((0, 0, 0), (0.012, 0.012, 0.022), 2), m=0) for _ in range(3)]
    halves = [pe.add(*sphere((0, 0, 0), (0.012, 0.012, 0.012), 1), m=0) for _ in range(2)]
    pe.build(kit.bpy, em, kit.coll)
    # sparkles, crumbs, rings and notes
    ps = Parts('fs_song'); gm = [M.mat_glow(kit, D, 'fs_songg', (1.0, 0.84, 0.34), 2.6), M.mat_glow(kit, D, 'fs_songc', (1.0, 0.52, 0.42), 2.4),
                                 M.mat_glow(kit, D, 'fs_songt', (0.40, 0.92, 0.88), 2.4), M.mat_glow(kit, D, 'fs_songw', (1.0, 0.97, 0.86), 2.8)]
    star = [(0, 0, 0)] + [((0.03 if k % 2 == 0 else 0.008) * math.cos(math.pi * k / 4), 0, (0.03 if k % 2 == 0 else 0.008) * math.sin(math.pi * k / 4)) for k in range(8)]
    sf = [(0, 1 + k, 1 + (k + 1) % 8) for k in range(8)]
    ring = []
    for k in range(5 * 3):
        r0, r1 = 0.90, 1.0; V = []; F = []
        for q in range(40):
            a = 2 * math.pi * q / 40; V += [(r0 * math.cos(a), r0 * math.sin(a), 0), (r1 * math.cos(a), r1 * math.sin(a), 0)]
        F = [(2 * q, 2 * q + 1, 2 * ((q + 1) % 40) + 1, 2 * ((q + 1) % 40)) for q in range(40)]
        ring.append(ps.add(V, F, m=k % 2 * 3))
    notes = []
    for k in range(5 * 3):
        mi = k % 3
        h = ps.add(*sphere((0, 0, 0), (0.016, 0.0115, 0.012), 1), m=mi); st = ps.add(*tube([(0.014, 0, 0.002), (0.014, 0, 0.056)], [0.0032, 0.0032], 4), m=mi)
        fl = ps.add([(0.014, 0, 0.056), (0.040, 0, 0.040), (0.036, 0, 0.026), (0.014, 0, 0.040)], [(0, 1, 2, 3)], m=mi); notes.append((h, st, fl))
    stars = [ps.add(star, sf, m=0 if k % 2 else 3) for k in range(14)]
    big = [ps.add(star, sf, m=3) for _ in range(6)]
    ps.build(kit.bpy, gm, kit.coll, smooth=False); ps.ob.visible_shadow = False
    pc = Parts('fs_crumbs'); crumbs = [pc.add(*sphere((0, 0, 0), (0.012, 0.012, 0.012), 1), m=0) for _ in range(14)]
    pc.build(kit.bpy, [M.paint(kit, D, 'sz_crumb', (0.46, 0.30, 0.20), noise=0.0)], kit.coll)
    return {'pr': pr, 'c': cic, 'egg': pe, 'eggs': eggs, 'halves': halves, 'song': ps, 'ring': ring, 'notes': notes, 'stars': stars, 'big': big, 'crumbs': pc, 'crumb_ids': crumbs}


# ------------------------------------------------------------------ places
def tree_base(t): return np.array([PK.TX, PK.TY, PK.gz(PK.TX, PK.TY, t) - 0.01])


def egg_world(t): return tree_base(t) + np.array(PK.BRANCHES[0]) + np.array([0.0, 0.0, 0.0])


def trunk_point(who, h):
    a = PERCH[who][0]; r = PK.trunk_r(h) + 0.016; return np.array([PK.TX + r * math.cos(a), PK.TY + r * math.sin(a), 0.0]), np.array([math.cos(a), math.sin(a), 0.0])


def hatchling_path(t):
    """The hatchling: on the twig, falling, shuffling over the lawn to the hole, diving in. Returns (pos world, forward 3D, mode)."""
    B = W.B
    egg = egg_world(t)
    start = np.array([egg[0], egg[1], egg[2]])
    land = np.array([PK.TX + 0.30, PK.TY - 0.30, 0.0]); hole = np.array([W.HOLE_XY[0], W.HOLE_XY[1], 0.0])
    zl = lambda x, y: PK.gz(x, y, t)
    if t < B.crack1: return start + np.array([0, 0, 0.0]), np.array([0.0, 0.0, -1.0]), 'twig'
    if t < B.fall1:
        u = (t - B.fall0) / (B.fall1 - B.fall0); u = float(np.clip(u, 0, 1))
        x = start[0] + (land[0] - start[0]) * u; y = start[1] + (land[1] - start[1]) * u
        z = start[2] + (zl(land[0], land[1]) + 0.012 - start[2]) * (u * u) + 0.03 * math.sin(math.pi * u)
        return np.array([x, y, z]), np.array([0.2, -0.3, -1.0]), 'fall'
    if t < B.dive0:
        u = (t - B.walk0) / (B.dive0 - B.walk0); u = float(np.clip(u, 0, 1)); s = W.smooth(0, 1, u)
        x = land[0] + (hole[0] - land[0]) * s + 0.04 * math.sin(2 * math.pi * 3 * u) * (1 - u); y = land[1] + (hole[1] - land[1]) * s
        f = hole - land; f[2] = 0
        return np.array([x, y, zl(x, y) + 0.012]), f, 'walk'
    u = float(np.clip((t - B.dive0) / (B.shaft0 - B.dive0), 0, 1))
    x, y = hole[0], hole[1]
    return np.array([x, y, zl(x, y) + 0.012 - 0.06 * u]), np.array([0.0, 0.0, -1.0]), 'dive'


def nymph_k(t):
    """The nymphs grow over the years (bigger each year), from hatchling to ready."""
    B = W.B; return (0.55 + 0.60 * sm(B.yr0, B.yr1, t)) * (1.0 + 1.6 * (1.0 - sm(B.settle0, B.label0 - 0.4, t)))      # big enough to follow while it is new


def main_world(who, t, lift):
    """Where a nymph is, as (position, frame R, mode, scale, sipping flag) for any time; None when not shown."""
    B = W.B; idx = NAMES.index(who)
    if who == 'M' and t < B.shaft0:
        if t < B.crack0: return None
        pos, f, mode = hatchling_path(t)
        pos = pos.copy(); pos[2] += 0.0
        return pos, frame_dir(f), mode, 1.5 if mode != 'twig' else 0.0, 0.0
    st, p, ang, mode, u = UG.nymph_state(who, t)
    k = nymph_k(t)
    if st == 'hidden': return None
    if st == 'face':
        if who != 'M':
            appear = UG.pop_k(t, B.roots_on0 + 0.25 * idx, 0.5)
            if appear < 0.02: return None
            k = k * appear
        # direction along the path in the face plane; on its post it clings to the root
        f = np.array([math.cos(ang), 0.0, math.sin(ang)])
        pos = np.array([p[0], UG.FY - 0.058, p[1] + lift])
        if mode in ('sip', 'unhook'):
            # clings to the root: lies along it, head toward the trunk, a little above the root's surface
            C = UG.PATH_ROOT['R3'] if who in ('M', 'S3') else (UG.PATH_ROOT['R1'] if who in ('S1', 'S4') else UG.PATH_ROOT['R2'])
            s_ = float(np.argmin(np.linalg.norm(C.P - p, axis=1)))
            sss = np.linspace(0, C.L, 200); q = np.array([C.at(s)[0] for s in sss]); i = int(np.argmin(np.linalg.norm(q - p, axis=1))); _, d = C.at(sss[i])
            f = np.array([-d[0], 0.0, -d[1]])      # head toward the trunk (up the root)
            pos = np.array([p[0] + 0.0, UG.FY - 0.060, p[1] + lift]) + np.array([-d[1], 0.0, d[0]]) * 0.0
        if mode == 'wait': f = np.array([0.0, 0.0, 1.0])
        return pos, frame_dir(f, (0.0, -1.0, 0.0)), mode, k, 1.0 if mode in ('sip',) else 0.0
    # on the lawn and the tree
    pop = B.pop0 + 0.16 * idx
    hole = np.array([W.HOLE_XY[0], W.HOLE_XY[1], 0.0])
    if t < pop + 0.5:                                    # rises out of the hole
        u = float(np.clip((t - pop) / 0.5, 0, 1)); z = PK.gz(hole[0], hole[1], t) - 0.05 + 0.07 * u + 0.05 * math.sin(math.pi * u)
        return np.array([hole[0], hole[1], z]), frame_dir(np.array([0.0, 0.5, 0.2])), 'out', k, 0.0
    m0 = pop + 2.2 + 0.2 * idx; m1 = B.march1 - 0.3 * (4 - idx)
    ang_, h_ = PERCH[who]; tp, n = trunk_point(who, 0.0)
    foot = np.array([tp[0], tp[1], 0.0])
    if t < m1:
        u = W.smooth(m0, m1, t)
        if t < m0: u = 0.0
        # a wobbly walk: sway sideways a little
        x = hole[0] + (foot[0] - hole[0]) * u + 0.025 * math.sin(2 * math.pi * 1.4 * t + idx) * (1 - u); y = hole[1] + (foot[1] - hole[1]) * u
        f = foot - hole; f[2] = 0
        stretch = W.win(t, pop + 0.6, m0, 0.3)               # blink at the sun, front arms up
        return np.array([x, y, PK.gz(x, y, t) + 0.016 * k]), frame_dir(f), 'march' if u > 0 else 'look', k, stretch
    # up the trunk
    c0 = B.climb0 + 0.25 * idx; c1 = B.crack_shell0 - 1.6
    u = W.smooth(c0, c1, t) if t > c0 else 0.0
    h = h_ * u
    if t <= c0 + 0.001:
        u2 = float(np.clip((t - m1) / max(c0 - m1, 1e-3), 0, 1))
        base = tree_base(t); pos = np.array([foot[0], foot[1], PK.gz(foot[0], foot[1], t) + 0.016 * k])
        return pos, frame_up(n), 'climb', k, 0.0
    base = tree_base(t); hh = h_ * u
    tp, n = trunk_point(who, hh)
    pos = np.array([tp[0], tp[1], base[2] + 0.02 + 0.06 + hh]) + n * (0.016 * k)
    return pos, frame_up(n), 'climb', k, 0.0


def put_all(pr, ids, p, R, k, lift_z=0.0):
    """Place a creature's pieces (all in its own frame) at world p with frame R and scale k."""
    def flat(x):
        for y in x:
            if isinstance(y, (list, tuple)): yield from flat(y)
            else: yield y
    for j in flat(ids):
        if isinstance(j, int): pr.set(j, p, R, k)


def label_point(C, under, t):
    return np.array([UG.NYMPH_POST[0] + 0.0, UG.FY - 0.07, UG.NYMPH_POST[1] + W.lift(t) + 0.03])


# ------------------------------------------------------------------ pose
def pose(C, D, t, under, park):
    B = W.B; pr = C['pr']; lift = W.lift(t)
    nym = sm(B.open0 - 0.05, B.open0 + 1.0, t)
    D.setc('cicbody', tuple(float(x) for x in (np.array([0.88, 0.96, 0.80]) * (1 - sm(B.ease0, B.ease1, t)) + np.array([0.80, 0.88, 0.70]) * sm(B.ease0, B.ease1, t))) if t < B.open0 else
           tuple(float(x) for x in (np.array([0.82, 0.90, 0.72]) * (1 - sm(B.open0, B.open0 + 2.0, t)) + np.array([0.16, 0.12, 0.12]) * sm(B.open0, B.open0 + 2.0, t))))
    D.setc('nymphcol', tuple(float(x) for x in (np.array([0.80, 0.56, 0.30]) * (1 - sm(B.crack_shell0, B.crack_shell0 + 0.8, t)) + np.array([0.86, 0.72, 0.52]) * sm(B.crack_shell0, B.crack_shell0 + 0.8, t))))
    D.set('wingalpha', 0.0)       # replaced below by the per-time value
    wa = 0.0 if t < B.ease0 else (0.42 + 0.18 * sm(B.ease0, B.open0, t))
    D.set('wingalpha', wa)
    P = pr
    # ---- the egg on the twig
    pe = C['egg']; egg = egg_world(t)
    for q, j in enumerate(C['eggs']):
        a = 0.0 if t < B.crack0 else 1.0
        vis = 1.0 if t < B.crack0 + 0.1 else 0.0
        if vis: pe.set(j, egg + np.array([-0.012 + 0.014 * q, 0.0, -0.010 * q]) , rx(0.5 + 0.3 * q), 3.0 * (1 + 0.10 * math.sin(2 * math.pi * 6 * t) * W.win(t, B.crack0 - 0.5, B.crack0 + 0.1, 0.1)) if q == 1 else 3.0)
        else: pe.hide(j)
    for q, j in enumerate(C['halves']):
        u = float(np.clip((t - B.crack0) / 0.4, 0, 1))
        if 0 < u and t < B.crack1 + 1.2:
            pe.set(j, egg + np.array([-0.002 + (0.014 + 0.03 * u) * (1 if q else -1), 0.0, -0.010 - 0.04 * u * u]), rx(0.3 + 2 * u), 3.0 * (1 - W.sm(B.crack1 + 0.6, B.crack1 + 1.2, t)))
        else: pe.hide(j)
    pe.commit()
    # ---- the five nymphs / cicadas
    pcr = C['crumbs']; ps = C['song']; nsong = 0
    for idx, who in enumerate(NAMES):
        c = C['c'][who]; w = main_world(who, t, lift)
        hide_n = lambda: [pr.hide(j) for j in _ids(c, 'n')]
        hide_a = lambda: [pr.hide(j) for j in _ids(c, 'a')]
        if w is None: hide_n(); hide_a(); continue
        p, R, mode, k, flag = w
        # nymph (or its shell after the split)
        n_k = k if mode != 'twig' else 0.0
        if t >= B.crack_shell0: n_k = k
        if n_k < 0.02: hide_n()
        else:
            for nm in ('body', 'abd', 'head'): pr.set(c[nm], p, R, n_k * (1 + 0.035 * math.sin(2 * math.pi * 1.4 * t + idx) * (1.0 if mode == 'sip' else 0.0)))
            for j in c['eyes'] + c['glint']: pr.set(j, p, R, n_k)
            stretch = flag if mode in ('march', 'look') else 0.0
            for q, j in enumerate(c['arms']):
                Rr = R @ ry(-1.1 * stretch + 0.15 * math.sin(2 * math.pi * 2.0 * t + q)) if mode not in ('sip',) else R
                pr.set(j, p, Rr, n_k); pr.set(c['claws'][q], p, Rr, n_k)
            walk = 2 * math.pi * 2.2 * t + idx
            for q, j in enumerate(c['legs']):
                sg = 1 if (q + q // 3) % 2 == 0 else -1
                pr.set(j, p, R @ ry(0.35 * sg * math.sin(walk) * (1.0 if mode in ('march', 'out', 'climb', 'crawl', 'dig') else 0.0)), n_k)
            sipping = mode == 'sip' and t > B.settle0
            if sipping: pr.set(c['sip'], p, R, n_k)
            else: pr.hide(c['sip'])
            shows_slit = W.sm(B.crack_shell0 - 0.2, B.crack_shell0 + 0.4, t)
            if shows_slit > 0.05 and mode == 'climb': pr.set(c['slit'], p, R, n_k * shows_slit)
            else: pr.hide(c['slit'])
        # the grown cicada, easing out of the back of the shell
        ek = sm(B.ease0 + 0.25 * idx * 0.0, B.ease1, t)
        if t < B.ease0 + 0.05 * idx or mode != 'climb': hide_a()
        else:
            e0 = B.ease0 + 0.18 * idx; ek = sm(e0, B.ease1 + 0.1 * idx * 0.0, t)
            tilt = 0.9 * (1 - ek) + 0.08; off = np.array([-0.01 + 0.05 * ek, 0.0, 0.03 + 0.012 * ek])
            Ra = R @ ry(-tilt)
            pa = p + R @ (off * n_k)
            ka = (0.30 + 0.95 * ek) * k * 1.3
            wing_open = sm(B.open0, B.open0 + 0.25, t) * 1.0
            wk = (0.28 + 0.30 * ek) * (1 - wing_open) + 1.0 * wing_open
            for nm in ('a_body', 'a_head'): pr.set(c[nm], pa, Ra, ka)
            for j in c['a_eyes'] + c['a_glint']: pr.set(j, pa, Ra, ka * (1 + 0.18 * sm(B.open0, B.open0 + 0.6, t)))
            for q, j in enumerate(c['a_legs']): pr.set(j, pa, Ra, ka)
            song = W.win(t, B.song0, B.final + 2.6, 0.4)
            buzz = 0.06 * math.sin(2 * math.pi * 14 * t + idx) * song
            for wi, (wing, vein, sd) in enumerate(c['wings']):
                spread = 0.30 * (1 - wing_open) + (0.55 + 0.5 * W.win(t, B.open0, B.open0 + 0.5, 0.15)) * wing_open
                spread = spread if t < B.open0 else (0.55 + 0.5 * W.win(t, B.open0, B.open0 + 0.5, 0.2) + (0.0 if t < B.song0 else 0.0))
                Rw = Ra @ rx(sd * (spread + buzz)) @ ry(0.12 * (wi % 2))
                sc = ka * wk
                pr.set(wing, pa, Rw, sc); pr.set(vein, pa, Rw, sc)
        # sparkles at the pop (pure functions)
    pr.commit()
    # ---- crumbs and sparkles at the pop-out, the song's rings and notes
    hole = np.array([W.HOLE_XY[0], W.HOLE_XY[1], PK.gz(W.HOLE_XY[0], W.HOLE_XY[1], t) + 0.01])
    for q, j in enumerate(C['crumb_ids']):
        u = (t - B.pop0 - 0.05 * (q % 5)) / 1.0
        if 0 < u < 1:
            a = 2 * math.pi * q / 14; sp = 0.12 + 0.06 * (q % 3)
            pcr.set(j, hole + np.array([sp * math.cos(a) * u, sp * math.sin(a) * u * 0.7, 0.20 * u - 0.28 * u * u]), I3, 1.0 - 0.3 * u)
        else: pcr.hide(j)
    pcr.commit()
    # stars at the pop and the final burst
    for q, j in enumerate(C['stars']):
        u = (t - B.pop0 - 0.04 * q) / 1.1; a = 2 * math.pi * q / 14 + 0.3
        if 0 < u < 1: ps.set(j, hole + np.array([0.20 * u * math.cos(a), 0.12 * u * math.sin(a), 0.10 + 0.24 * u]), CAMR, 1.0 * math.sin(math.pi * u) * 1.2)
        else: ps.hide(j)
    perch_pts = []
    for idx, who in enumerate(NAMES):
        w = main_world(who, t, lift)
        if w is not None and w[2] == 'climb' and t > B.ease0: perch_pts.append(w[0] + w[1] @ np.array([0.02, 0.0, 0.06]))
        else: perch_pts.append(None)
    song = W.win(t, B.open0, B.final + 3.0, 0.3); hum = W.win(t, B.final + 2.0, 100.0, 1.2) * 0.4
    for idx in range(5):
        pp = perch_pts[idx]
        for r in range(3):
            j = C['ring'][idx * 3 + r]
            if r == 2 or pp is None or (song < 0.02 and hum < 0.02) or t < B.open0: ps.hide(j); continue
            T_ = 1.5 if hum < 0.3 else 2.6; age = ((t / T_ + r / 2.0 + idx * 0.13) % 1.0)
            rad = 0.04 + 0.22 * age ** 0.8 if hum < 0.3 else 0.03 + 0.14 * age ** 0.8
            sc = rad * (1.0 - W.sm(0.80, 1.0, age)) * min(1.0, max(song, hum) * 1.5)
            ps.set(j, pp, CAMR @ rz(0.0), sc if sc > 0.01 else 0.0) if sc > 0.01 else ps.hide(j)
        for r in range(3):
            h, st, fl = C['notes'][idx * 3 + r]
            if pp is None or t < B.open0 + 0.2 or (song < 0.02 and hum < 0.02): [ps.hide(x) for x in (h, st, fl)]; continue
            T_ = 2.8; age = ((t / T_ + r / 3.0 + idx * 0.21) % 1.0)
            pos = pp + np.array([0.35 * age * (1 if (idx + r) % 2 else -1) * 0.8, 0.10 * math.sin(6 * age + idx), 0.10 + 0.55 * age])
            pos = pos + np.array([0.05 * math.sin(2 * math.pi * 1.2 * t + idx), 0.0, 0.0])
            s_ = 1.15 * math.sin(math.pi * age) ** 0.5 * min(1.0, max(song, hum) * 1.5)
            Rn = CAMR @ rz(0.25 * math.sin(2 * math.pi * 0.8 * t + idx + r))
            for x in (h, st, fl): ps.set(x, pos, Rn, s_)
    # the burst on the first open and the final chord
    for q, j in enumerate(C['big']):
        u = (t - B.open0) / 1.3; u2 = (t - B.final) / 1.6
        base = np.mean([x for x in perch_pts if x is not None], axis=0) if any(x is not None for x in perch_pts) else None
        if base is None: ps.hide(j); continue
        if 0 < u < 1: ps.set(j, base + np.array([0.0, 0.0, 0.15]) + CAMR @ np.array([0.42 * math.cos(2 * math.pi * q / 6), 0.42 * math.sin(2 * math.pi * q / 6), 0.0]) * u, CAMR, 2.2 * math.sin(math.pi * u))
        elif 0 < u2 < 1: ps.set(j, base + np.array([0.0, 0.0, 0.2]) + CAMR @ np.array([0.60 * math.cos(2 * math.pi * q / 6 + 0.5), 0.60 * math.sin(2 * math.pi * q / 6 + 0.5), 0.0]) * u2, CAMR, 3.0 * math.sin(math.pi * u2))
        else: ps.hide(j)
    ps.commit()


def _ids(c, kind):
    if kind == 'n': return [c['body'], c['abd'], c['head'], c['slit'], c['sip']] + c['eyes'] + c['glint'] + c['arms'] + c['claws'] + c['legs']
    out = [c['a_body'], c['a_head']] + c['a_eyes'] + c['a_glint'] + c['a_legs']
    for wing, vein, sd in c['wings']: out += [wing, vein]
    return out
