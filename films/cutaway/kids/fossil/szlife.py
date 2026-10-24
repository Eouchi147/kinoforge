"""How does a dinosaur turn into stone? Everything alive on the block, and the easter eggs (bpy + numpy).

Every pose is a pure function of t. Each piece has a job (CRAFT section 1):
  dinosaur      the story itself: walks in, munches ferns; old, it walks to the bank, lies down and stays still
                (gentle: no wound, no predator, no breathing, never shown as sleep; research 1.1.1)
  ferns, tree ferns, conifers   say "long ago" at a glance; the ferns it eats shrink as it munches
  meadow trees, grass, flowers  say "today"; they fold away when time rewinds and grow back after the rain
  little plants on each new layer, a lizard crossing it   millions of years: life comes and goes on every new top
  birds, butterflies, a rabbit (today); dragonflies, lizards, birds (long ago)   a busy, happy world (three layers of motion)
  the girl with her brush and hat, her dog with a stick   the finder: kneels, brushes, the bone pokes out, she cheers
  a flock of birds flying up from the tree   the cheer moment
Easter eggs (Sam 23 Oct 19:43: generic everyday things kids know, some obvious, one or two hidden, animated where
possible; never a brand or a character): a red ball lost in the soil of the front face (obvious), a toy car in the soil
of the right face (hidden), a rubber duck bobbing down the brook, a kite stuck in a tree and tugging, a teddy bear left on
the meadow, a toy dinosaur the girl sets down beside the real fossil, her dog chasing about with a stick.
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, Dino, sphere, tube, cone, box, disc, quad, rz, ry, rx, euler, I3

TOP = W.top_h


def gz(x, y, t):
    return float(TOP(np.array([x]), np.array([y]), t)[0])


def path_at(P, u):
    P = np.asarray(P, float); seg = np.linalg.norm(np.diff(P, axis=0), axis=1); c = np.concatenate([[0], np.cumsum(seg)])
    s = float(np.clip(u, 0, 1)) * c[-1]; i = min(int(np.searchsorted(c, s, 'right')) - 1, len(seg) - 1); f = (s - c[i]) / max(seg[i], 1e-9)
    p = P[i] + (P[i + 1] - P[i]) * f; d = P[i + 1] - P[i]
    return p, math.atan2(d[1], d[0])


def lumpy_ball(c, r, seed, sub=2, amp=0.18):
    V, F = cw._icosphere(sub); V = cw._lumpy(V, seed, amp, 2.6, 0.06, 7.0); return V * np.asarray(r, float) + np.asarray(c, float), F


# ============================================================================== the dinosaur
def build_dino(kit, D):
    body = M.paint(kit, D, 'sz_dino', (0.36, 0.70, 0.56), alpha='dalpha', noise=0.0)
    # belly cream and soft coral spots on the back, painted in the base colour (Fable keeps it)
    g = cw.G(body.node_tree, kit); p = next(n for n in body.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    geo = g.node('ShaderNodeNewGeometry'); nz = g.sep(geo.outputs['Normal'])[2]
    belly = g.math('MULTIPLY', g.math('SUBTRACT', -0.05, nz), 3.0, clamp=True)
    col = g.mix(belly, cw.srgb((0.36, 0.70, 0.56)), cw.srgb((0.98, 0.90, 0.66)))
    vo = g.voronoi(g.node('ShaderNodeTexCoord').outputs['Object'], 9.0, 'F1')
    spot = g.math('MULTIPLY', g.math('LESS_THAN', vo.outputs['Distance'], 0.24), g.math('MULTIPLY', g.math('SUBTRACT', nz, 0.35), 4.0, clamp=True))
    col = g.mix(g.math('MULTIPLY', spot, 0.8), col, cw.srgb((0.96, 0.56, 0.42)))
    g.put(p, 'Base Color', col)
    eye = M.paint(kit, D, 'sz_dinoeye', (0.06, 0.06, 0.10), alpha='dalpha', noise=0.0)
    return Dino(kit.bpy, 'fs_dino', [body, eye], kit.coll, W.DINO_K)


def dino_pose(dn, D, t):
    B = W.B
    a = W.sm(B.dino_in0, B.dino_in1, t) * (1 - W.sm(B.skel0, B.skel1, t))     # what remains is the skeleton (szstory)
    D.set('dalpha', a); dn.ob.hide_render = a < 0.01
    if a < 0.01: return
    x_in, x_munch, x_lie = -1.70, -0.80, W.DINO_LIE_X
    walk = 0.0; amt = 0.0
    if t < B.walk1:
        u = W.sm(B.walk0, B.walk1, t); x = x_in + (x_munch - x_in) * u; amt = 1.0 if B.walk0 < t < B.walk1 else 0.0
    elif t < B.towater0:
        x = x_munch
    else:
        u = W.sm(B.towater0, B.towater1, t); x = x_munch + (x_lie - x_munch) * u; amt = 1.0 if t < B.towater1 else 0.0
    if amt: walk = 2 * math.pi * 1.1 * t
    amt *= 0.9
    y = W.DINO_Y
    # munching: the neck dips to the ferns and lifts to chew, about every 2.2 s
    mu = W.win(t, B.munch0 - 0.3, B.munch1 + 0.2, 0.5) * (0.5 - 0.5 * math.cos(2 * math.pi * (t - B.munch0) / 2.2))
    lie = W.sm(B.lie0, B.lie1, t); curl = W.sm(B.curl0, B.curl1, t)
    eyes = 1.0 - W.sm(B.curl0 + 0.4, B.curl1, t)
    blink = 0.0 if lie > 0.5 else max(0.0, 1 - abs(((t + 0.7) % 3.1) - 0.08) / 0.08)
    tail = math.sin(2 * math.pi * t / 2.6) * (1 - curl)
    breathe = 0.0      # it died: no breathing, no sleep (research 1.1.1: never 'sleep' for death)
    bob = 0.012 * math.sin(walk * 2) if amt else 0.0
    zg = gz(x, y, t) if t < B.flood0 else W.Z_ANC + W.lift(t)
    dn.pose((x, y, zg - 0.01), 0.0, mu * (1 - lie), lie, walk, amt, tail, curl, eyes * (1 - blink), breathe, bob)


# ============================================================================== plants
def proto_fern(kit, mat, seed, height, fronds=7):
    """A fern: arching fronds with leaflets (sawtooth strips), one object (instanced)."""
    rng = np.random.default_rng(seed); A = cw._Acc()
    for f in range(fronds):
        a = 2 * math.pi * f / fronds + rng.uniform(-0.3, 0.3); L = height * rng.uniform(0.75, 1.15); n = 9
        d = np.array([math.cos(a), math.sin(a), 0]); side = np.array([-math.sin(a), math.cos(a), 0])
        pts = [d * (L * 0.62 * u) + np.array([0, 0, L * (0.95 * u - 0.55 * u * u)]) for u in np.linspace(0, 1, n)]
        V = []; Fc = []
        for i, p in enumerate(pts):
            w = L * 0.20 * math.sin(math.pi * min(1.0, (i + 0.6) / n)) * (1.0 if i % 2 == 0 else 0.55)
            V += [tuple(p - side * w), tuple(p), tuple(p + side * w)]
        for i in range(n - 1):
            o = 3 * i; Fc += [(o, o + 3, o + 4, o + 1), (o + 1, o + 4, o + 5, o + 2)]
        A.add(V, Fc)
    return A.build(kit.bpy, f'fs_fern{seed}', [mat], True, None)


def world_pts(rng, step, rmax, rmin=0.0):
    """Jittered points on the land around the block (not on it, not in the viewing trench), from rmin to rmax metres away."""
    xs = np.arange(-W.HX - rmax, W.HX + rmax, step); ys = np.arange(-W.HY - rmax, W.HY + rmax, step)
    X, Y = np.meshgrid(xs, ys); P = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.5, 0.5, (X.size, 2)) * step
    d = np.hypot(np.maximum(np.abs(P[:, 0]) - W.HX, 0), np.maximum(np.abs(P[:, 1]) - W.HY, 0))
    ok = ~W.in_hole(P[:, 0], P[:, 1]) & (d <= rmax) & (d >= rmin)
    # thinner with distance (the haze takes over)
    ok &= rng.uniform(0, 1, len(P)) < np.clip(1.15 - d / rmax, 0.15, 1.0)
    return P[ok]


def behind(P, margin=-0.6):
    """Keep points that are not between the camera and the block (tall things there would wall off the view)."""
    return P[W.depth_s(P[:, 0], P[:, 1]) > float(min(W.depth_s(np.array([-W.HX, W.HX]), np.array([-W.HY, -W.HY])))) - margin]


def build_plants(kit, L, D, rng):
    """Ferns (long ago), grass and flowers (today), the little plants of each new layer: instanced by the kit's scatter
    (wind sway), their heights and sizes rewritten every frame (they follow the moving top and grow or fold away)."""
    out = {}
    fern_m = M.varied(kit, D, 'sz_fern', [(0.10, 0.46, 0.30), (0.20, 0.58, 0.32), (0.32, 0.66, 0.36), (0.12, 0.40, 0.34)], tip=(0.70, 0.84, 0.44), height=0.14)
    ferns = [proto_fern(kit, fern_m, s, h) for s, h in ((1, 0.14), (2, 0.18), (3, 0.11), (4, 0.22))]
    xs = np.arange(-W.HX + 0.05, W.HX - 0.03, 0.085); X, Y = np.meshgrid(xs, np.arange(-W.HY + 0.05, W.HY - 0.03, 0.085))
    P = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.035, 0.035, (X.size, 2))
    rd = W.river_d(P[:, 0], P[:, 1])
    lane = (np.abs(P[:, 1] - W.DINO_Y) < 0.26) & (P[:, 0] > -1.9) & (P[:, 0] < 1.15)
    keep = (rd > 0.34) & ~lane & (rng.uniform(0, 1, len(P)) < 0.85)
    P = P[keep]
    Pw = behind(world_pts(rng, 0.12, 4.0)); Pw = Pw[W.river_d(Pw[:, 0], Pw[:, 1]) > 0.34]; P = np.vstack([P, Pw])
    # the clump it munches, right in front of its nose
    clump = np.array([(0.10, W.DINO_Y - 0.02), (0.20, W.DINO_Y + 0.08), (0.02, W.DINO_Y + 0.10), (0.16, W.DINO_Y - 0.12)])
    P = np.vstack([P, clump]); n = len(P)
    sc = rng.uniform(0.8, 1.4, n); sc[-4:] = (1.6, 1.4, 1.3, 1.2)
    ob = L.scatter('sz_ferns', ferns, P, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 4, n), sway=0.10, speed=0.5, z=0.0)
    out['ferns'] = (ob, P, sc, rng.uniform(0, 0.5, n))
    # grass and flowers (today)
    pal = dict(cw.SEASONS['summer'])
    gm = M.varied(kit, D, 'sz_grass', [(0.44, 0.70, 0.30), (0.56, 0.78, 0.34), (0.38, 0.64, 0.28), (0.62, 0.80, 0.38)], tip=(0.90, 0.94, 0.56), height=0.07)
    tufts = cw.proto_tufts(kit, pal, 6, 0.06, 7, (8, 13))
    for o in tufts: o.data.materials[0] = gm
    xs = np.arange(-W.HX + 0.02, W.HX - 0.01, 0.034); X, Y = np.meshgrid(xs, np.arange(-W.HY + 0.02, W.HY - 0.01, 0.034))
    Q = np.column_stack([X.ravel(), Y.ravel()]) + rng.uniform(-0.016, 0.016, (X.size, 2))
    rd = W.river_d(Q[:, 0], Q[:, 1]); rk = W.rock_patch(Q[:, 0], Q[:, 1])
    Q = Q[(rd > 0.19) & (rk < 0.25) & (np.abs(Q) < [W.HX - 0.006, W.HY - 0.006]).all(1)]
    Qw = world_pts(rng, 0.05, 1.8); Qw = Qw[W.river_d(Qw[:, 0], Qw[:, 1]) > 0.19]; Q = np.vstack([Q, Qw]); n = len(Q)
    sc = rng.uniform(0.7, 1.3, n)
    ob = L.scatter('sz_grass', tufts, Q, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 6, n), sway=0.22, speed=0.9, z=0.0)
    out['grass'] = (ob, Q, sc, rng.uniform(0, 0.4, n))
    fl = cw.proto_flowers(kit, 5, 7)
    R = rng.uniform([-W.HX + 0.05, -W.HY + 0.05], [W.HX - 0.05, W.HY - 0.05], (260, 2))
    R = R[(W.river_d(R[:, 0], R[:, 1]) > 0.22) & (W.rock_patch(R[:, 0], R[:, 1]) < 0.05)]
    Rw = world_pts(rng, 0.16, 2.2); Rw = Rw[W.river_d(Rw[:, 0], Rw[:, 1]) > 0.22]; R = np.vstack([R, Rw]); n = len(R)
    sc = rng.uniform(0.9, 1.5, n)
    ob = L.scatter('sz_flowers', fl, R, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 5, n), sway=0.18, speed=0.9, z=0.0)
    out['flowers'] = (ob, R, sc, rng.uniform(0.2, 0.7, n))
    # little plants on each new layer (deep time): sprout after each flood, buried by the next
    small = [proto_fern(kit, fern_m, 11 + s, 0.07, 5) for s in range(3)]
    S = rng.uniform([-W.HX + 0.06, -W.HY + 0.06], [W.HX - 0.06, W.HY - 0.06], (150, 2)); S = np.vstack([S, world_pts(rng, 0.18, 2.0)]); n = len(S)
    sc = rng.uniform(0.8, 1.3, n); slot = rng.integers(-1, 5, n)      # -1: the mud blanket's own plants
    ob = L.scatter('sz_sprouts', small, S, yaw=rng.uniform(0, 6.28, n), scale=sc, variant=rng.integers(0, 3, n), sway=0.10, speed=0.6, z=0.0)
    out['sprouts'] = (ob, S, sc, slot, rng.uniform(0, 0.3, n))
    return out


def _set_pts(ob, P, z, sc):
    me = ob.data; co = np.column_stack([P, z]).astype(np.float32)
    me.vertices.foreach_set('co', co.ravel()); me.attributes['scale'].data.foreach_set('value', np.asarray(sc, np.float32)); me.update()


def plants_pose(pl, t):
    B = W.B; e = W.era(t)
    ob, P, sc, d = pl['ferns']
    grow = np.clip((t - B.fern0 - d * (B.fern1 - B.fern0)) / 0.9, 0, 1); grow = grow * grow * (3 - 2 * grow)
    gone = W.smooth(B.mud0 - 0.2, B.mud1 - 0.6, t)                       # buried by the blanket
    k = grow * (1 - gone); eaten = W.sm(B.munch0 + 0.6, B.munch1, t)
    kk = sc * k; kk[-4:] *= (1 - eaten) * 1.0
    on = k.max() > 1e-3 if np.ndim(k) else k > 1e-3
    ob.hide_render = not on
    if on: _set_pts(ob, P, TOP(P[:, 0], P[:, 1], t) - 0.006, kk)
    # today: folds away in the rewind, grows back after the rain
    for key, rate in (('grass', 0.7), ('flowers', 0.9)):
        ob, Q, sc, d = pl[key]
        fold = 1 - W.smooth(B.rw0 + d * 0.3, B.rw0 + d * 0.3 + 0.25, t)
        back = np.clip((t - B.green0 - d * 2.0) / rate, 0, 1); back = back * back * (3 - 2 * back)
        k = np.where(t < B.green0, fold, back); on = float(np.max(k)) > 1e-3
        ob.hide_render = not on
        if on: _set_pts(ob, Q, TOP(Q[:, 0], Q[:, 1], t) - 0.004, sc * k)
    ob, S, sc, slot, d = pl['sprouts']
    k = np.zeros(len(S))
    if B.mud1 - 0.5 < t < B.erode1:
        # the blanket's plants: after the flood drains, until the first later layer arrives
        tops = [(B.flood3 - 0.2, W.SLOTS[0][0])] + [(W.SLOTS[i][1] + 0.25, (W.SLOTS[i + 1][0] if i < 4 else B.erode0 + 1.6)) for i in range(5)]
        for j, (a, b) in enumerate(tops):
            m = (slot == (j - 1)) & (j == 0 or W.SLOT_ERAS[j - 1] in ('mammoth', 'grass'))
            g = np.clip((t - a - d[m]) / 0.45, 0, 1); g = g * g * (3 - 2 * g); f = 1 - W.smooth(b - 0.35, b, t)
            k[m] = g * f
    on = k.max() > 1e-3; ob.hide_render = not on
    if on: _set_pts(ob, S, TOP(S[:, 0], S[:, 1], t) - 0.004, sc * k)


def _tree(A, base, H, crown_r, seed, mat_trunk=0, mat_crown=1, kind='round'):
    """A storybook tree into an _Acc-like (V, F, m) list: a soft trunk and a few round leaf masses (or a fir, a palm-like
    tree fern, a monkey-puzzle conifer for long ago)."""
    rng = np.random.default_rng(seed); x, y = base; parts = []
    if kind == 'round':
        v, f = tube([(x, y, -0.02), (x + 0.01, y, H * 0.45), (x, y + 0.01, H * 0.62)], [0.028 * H / 0.6, 0.022 * H / 0.6, 0.016 * H / 0.6], 8); parts.append((v, f, mat_trunk))
        for c in [(0, 0, 0.78), (-0.45, 0.1, 0.62), (0.45, -0.1, 0.64), (0.1, 0.42, 0.66), (-0.1, -0.42, 0.62), (0.0, 0.0, 1.0)]:
            r = crown_r * rng.uniform(0.6, 0.85); v, f = lumpy_ball((x + c[0] * crown_r, y + c[1] * crown_r, H * c[2]), (r, r, r * 0.85), seed + len(parts)); parts.append((v, f, mat_crown))
    elif kind == 'fir':
        v, f = tube([(x, y, -0.02), (x, y, H * 0.25)], [0.02, 0.016], 8); parts.append((v, f, mat_trunk))
        for i in range(4):
            z0 = H * (0.18 + 0.2 * i); v, f = cone((x, y, z0), crown_r * (1 - 0.2 * i), H * 0.36, 14); parts.append((v, f, mat_crown))
    elif kind == 'treefern':
        v, f = tube([(x, y, -0.02), (x + 0.02, y, H * 0.5), (x + 0.01, y + 0.01, H)], [0.03, 0.026, 0.022], 8); parts.append((v, f, mat_trunk))
        n = 9
        for k in range(n):
            a = 2 * math.pi * k / n + rng.uniform(-0.2, 0.2); L = crown_r * rng.uniform(0.9, 1.15)
            d = np.array([math.cos(a), math.sin(a), 0]); sd = np.array([-math.sin(a), math.cos(a), 0]); top = np.array([x + 0.01, y + 0.01, H])
            pts = [top + d * L * u + np.array([0, 0, L * (0.5 * u - 0.75 * u * u)]) for u in np.linspace(0, 1, 7)]
            V = []; Fc = []
            for i, p in enumerate(pts):
                w = L * 0.16 * math.sin(math.pi * min(1.0, (i + 0.5) / 7)); V += [tuple(p - sd * w), tuple(p), tuple(p + sd * w)]
            for i in range(6): o = 3 * i; Fc += [(o, o + 3, o + 4, o + 1), (o + 1, o + 4, o + 5, o + 2)]
            parts.append((np.array(V), Fc, mat_crown))
    elif kind == 'puzzle':
        v, f = tube([(x, y, -0.02), (x, y, H)], [0.03, 0.014], 8); parts.append((v, f, mat_trunk))
        for i in range(5):
            z0 = H * (0.45 + 0.12 * i); r = crown_r * (1.0 - 0.15 * i)
            v, f = lumpy_ball((x, y, z0), (r, r, r * 0.28), seed + i, 2, 0.12); parts.append((v, f, mat_crown))
    return parts


# meadow trees today (x, y, height, crown radius, kind); the kite is stuck in the third one
TODAY_TREES = [(-1.50, 0.78, 0.66, 0.20, 'round'), (-0.65, 0.90, 0.56, 0.17, 'round'), (0.95, 0.80, 0.70, 0.21, 'round'),
               (1.62, -0.30, 0.62, 0.13, 'fir'), (-1.62, -0.25, 0.44, 0.13, 'round'), (0.20, 0.95, 0.50, 0.11, 'fir')]
OLD_TREES = [(-1.58, -0.66, 0.58, 0.30, 'treefern'), (-1.35, 0.62, 0.64, 0.30, 'treefern'), (-0.25, 0.84, 0.56, 0.26, 'treefern'),
             (1.12, 0.66, 0.60, 0.28, 'treefern'), (1.58, -0.70, 0.46, 0.24, 'treefern'), (-0.85, 0.95, 0.92, 0.20, 'puzzle'),
             (0.48, 0.96, 0.84, 0.18, 'puzzle'), (1.05, 1.00, 0.96, 0.19, 'puzzle')]


def world_trees(rng):
    """Trees on the land around the block, both eras: (x, y, height, crown, kind)."""
    today, old = [], []
    pts = behind(world_pts(rng, 1.25, 5.0, 0.35), -1.4); pts = pts[W.river_d(pts[:, 0], pts[:, 1]) > 0.45]
    for i, (x, y) in enumerate(pts):
        h = rng.uniform(0.40, 0.62)
        today.append((x, y, h, h * 0.30, 'round' if rng.uniform() < 0.7 else 'fir'))
    pts = behind(world_pts(rng, 1.05, 5.0, 0.35), -1.4); pts = pts[W.river_d(pts[:, 0], pts[:, 1]) > 0.45]
    for i, (x, y) in enumerate(pts):
        h = rng.uniform(0.40, 0.75); k = rng.uniform()
        old.append((x, y, h, h * 0.45, 'treefern') if k < 0.6 else (x, y, h * 1.3, h * 0.22, 'puzzle'))
    return today, old


def build_trees(kit, D):
    pr = Parts('fs_trees')
    mats = [M.paint(kit, D, 'sz_trunk', (0.46, 0.30, 0.24)), M.varied(kit, D, 'sz_crown', [(0.26, 0.62, 0.36), (0.40, 0.70, 0.36), (0.18, 0.52, 0.38)]),
            M.paint(kit, D, 'sz_fir', (0.14, 0.44, 0.40)), M.varied(kit, D, 'sz_oldleaf', [(0.10, 0.48, 0.34), (0.24, 0.60, 0.30), (0.08, 0.40, 0.36)]),
            M.paint(kit, D, 'sz_oldtrunk', (0.40, 0.28, 0.22))]
    items = []
    wt, wo = world_trees(np.random.default_rng(17))
    allt = TODAY_TREES + wt + OLD_TREES + wo; n_today = len(TODAY_TREES) + len(wt)
    for i, (x, y, H, r, kind) in enumerate(allt):
        old = i >= n_today
        mc = {'round': 1, 'fir': 2, 'treefern': 3, 'puzzle': 3}[kind]
        ids = [pr.add(v, f, mc if m == 1 else (4 if old else 0), pivot=(x, y, 0)) for v, f, m in _tree(None, (x, y), H, r, 100 + i, 0, 1, kind)]
        items.append((ids, x, y, old, (i * 0.37) % 1.0, i * 1.7))
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'items': items}


def trees_pose(T, t):
    B = W.B; pr = T['parts']
    for ids, x, y, old, d, ph in T['items']:
        if old: k = W.sm(B.fern0 + d * 0.8, B.fern0 + d * 0.8 + 1.0, t) * (1 - W.sm(B.mud0 - 0.2 + d * 0.5, B.mud1 - 0.6, t))
        else: k = np.where(t < B.green0, 1 - W.sm(B.rw0 + d * 0.25, B.rw0 + d * 0.25 + 0.3, t), W.sm(B.green0 + d * 0.9, B.green0 + d * 0.9 + 1.1, t))
        k = float(k); z = gz(x, y, t) - 0.01
        R = euler(0.015 * math.sin(0.9 * t + ph), 0.012 * math.cos(0.7 * t + ph), 0.0)
        for j in ids:
            if k < 1e-3: pr.hide(j)
            else: pr.set(j, (x, y, z), R, k)
    pr.commit()


# ============================================================================== creatures
def _ell(c, r, sub=1): return sphere(c, r, sub)


def build_birds(kit, D, rng, n=4, flock=7):
    pr = Parts('fs_birds'); m = M.paint(kit, D, 'sz_bird', (0.18, 0.20, 0.30), noise=0.0); out = []
    for k in range(n + flock):
        s = 0.045 if k < n else 0.034
        b = pr.add(*tube([(-s * 0.5, 0, 0), (0, 0, 0), (s * 0.45, 0, 0.004)], [s * 0.09, s * 0.14, s * 0.06], 6))
        w = [pr.add([(-s * 0.18, 0, 0), (s * 0.18, 0, 0), (0.0, sd * s * 0.95, 0), (-s * 0.32, sd * s * 0.7, 0)], [(0, 1, 2, 3)]) for sd in (-1, 1)]
        out.append((b, w, rng.uniform(2.0, 2.6), rng.uniform(0.95, 1.35), rng.uniform(0, 6.28), rng.uniform(2.6, 3.6)))
    pr.build(kit.bpy, [m], kit.coll, smooth=False)
    return {'parts': pr, 'birds': out, 'n': n}


def birds_pose(Bd, t):
    B = W.B; pr = Bd['parts']; n = Bd['n']
    # circling birds: today and long ago, gone during deep time (floods and layers) and the rain
    pres = 1 - W.sm(B.flood0, B.flood1, t) * (1 - W.sm(B.green0, B.green1, t))
    for i, (b, wings, r, h, a0, flap) in enumerate(Bd['birds']):
        if i < n:
            a = a0 + 0.42 * t; rr = r + (1 - pres) * 7.0
            P = (rr * math.cos(a), rr * math.sin(a) * 0.7 + 0.3, h + W.lift(t) + (1 - pres) * 2.0 + 0.06 * math.sin(0.8 * t + a0)); yaw = a + math.pi / 2
            amp = math.radians(12 + 30 * (0.5 + 0.5 * math.sin(0.5 * t + a0))) * math.sin(2 * math.pi * flap * t)
            show = pres > 0.02
        else:
            j = i - n; t0 = B.flyup0 + 0.09 * j; u = max(0.0, t - t0)
            tx, ty, tz = 0.95 + 0.12 * math.cos(j * 2.1), 0.80 + 0.10 * math.sin(j * 2.1), 0.52 + 0.04 * (j % 3) + W.lift(t)
            ang = -1.9 + 0.45 * j
            P = (tx + math.cos(ang) * 1.3 * u, ty + math.sin(ang) * 0.6 * u, tz + 0.95 * u + 0.25 * u * u); yaw = ang
            amp = math.radians(45) * math.sin(2 * math.pi * 6.0 * t + j) if u > 0 else 0.0
            show = (W.B.green1 < t) and (u < 4.0)
            if u <= 0: P = (tx, ty, tz)
        if not show:
            pr.hide(b); [pr.hide(w) for w in wings]; continue
        R = rz(yaw); pr.set(b, P, R)
        for w, sd in zip(wings, (-1, 1)): pr.set(w, P, R @ rx(sd * amp))
    pr.commit()


def build_flutter(kit, D, rng, n_fly=5, n_drag=3):
    """Butterflies (today) and dragonflies (long ago): bodies and flapping wings."""
    pr = Parts('fs_flutter'); out = []
    cols = [(0.97, 0.52, 0.36), (0.99, 0.80, 0.30), (0.70, 0.84, 0.98), (0.92, 0.62, 0.86), (1.0, 0.66, 0.22)]
    mats = [M.paint(kit, D, 'sz_bug', (0.12, 0.10, 0.16), noise=0.0)] + [M.paint(kit, D, f'sz_wing{k}', c, noise=0.0) for k, c in enumerate(cols)] + \
           [M.paint(kit, D, 'sz_dragon', (0.10, 0.50, 0.70), noise=0.0), M.paint(kit, D, 'sz_dwing', (0.86, 0.95, 1.0), noise=0.0)]
    for k in range(n_fly):
        b = pr.add(*tube([(-0.008, 0, 0), (0.008, 0, 0)], [0.0025, 0.0025], 6), m=0)
        ws = []
        for sd in (-1, 1):
            V = [(0, 0, 0)] + [(0.020 * math.cos(a) * (1 + 0.3 * math.sin(2 * a)) - 0.002, sd * 0.024 * abs(math.sin(a)) + sd * 0.002, 0) for a in np.linspace(-0.3, math.pi + 0.3, 10)]
            ws.append(pr.add(V, [(0, i, i + 1) for i in range(1, 10)], m=1 + k % 5))
        out.append(('fly', b, ws, rng.uniform(-1.4, 1.4), rng.uniform(-0.7, 0.8), rng.uniform(0, 6.28)))
    for k in range(n_drag):
        b = pr.add(*tube([(-0.05, 0, 0), (0.0, 0, 0), (0.016, 0, 0)], [0.003, 0.005, 0.006], 6), m=6)
        ws = []
        for sd in (-1, 1):
            for off in (0.008, -0.004):
                ws.append(pr.add([(off, 0, 0.003), (off + 0.007, sd * 0.042, 0.003), (off - 0.006, sd * 0.044, 0.003)], [(0, 1, 2)], m=7))
        out.append(('drag', b, ws, rng.uniform(-0.6, 0.9), rng.uniform(-0.2, 0.3), rng.uniform(0, 6.28)))
    pr.build(kit.bpy, mats, kit.coll, smooth=False)
    return {'parts': pr, 'bugs': out}


def flutter_pose(Fl, t):
    B = W.B; pr = Fl['parts']; e = W.era(t); old = W.ancient(t)
    for kind, b, ws, hx, hy, ph in Fl['bugs']:
        if kind == 'fly':
            show = e > 0.6; x = hx + 0.35 * math.sin(0.55 * t + ph) + 0.12 * math.sin(1.7 * t + 2 * ph); y = hy + 0.22 * math.sin(0.43 * t + 1.3 * ph)
            z = gz(x, y, t) + 0.12 + 0.06 * math.sin(1.3 * t + ph) + 0.03 * abs(math.sin(5.0 * t + ph))
            yaw = math.atan2(0.22 * 0.43 * math.cos(0.43 * t + 1.3 * ph), 0.35 * 0.55 * math.cos(0.55 * t + ph)); amp = 0.15 + 1.0 * abs(math.sin(2 * math.pi * 4.5 * t + ph))
            s = 1.6
        else:
            show = old > 0.5; a = ph + 0.9 * t; rr = 0.35 + 0.2 * math.sin(1.7 * t + ph)
            x = hx + rr * math.cos(a) + 0.15 * math.sin(3.1 * t + ph); y = hy + rr * math.sin(a) * 0.6
            z = W.water_level(t) + 0.12 + 0.05 * math.sin(2.9 * t + ph) if W.water_level(t) > -5 else gz(x, y, t) + 0.15
            yaw = a + math.pi / 2 + 0.3 * math.sin(4.0 * t); amp = 0.5 * math.sin(97.0 * t + ph); s = 1.4
        if not show or abs(x) > W.HX - 0.02 or abs(y) > W.HY - 0.02:
            pr.hide(b); [pr.hide(w) for w in ws]; continue
        R = rz(yaw); pr.set(b, (x, y, z), R, s)
        for i, w in enumerate(ws):
            sd = -1 if (i % 4 if kind == 'drag' else i) < (2 if kind == 'drag' else 1) else 1
            pr.set(w, (x, y, z), R @ rx(sd * amp), s)
    pr.commit()


def build_critters(kit, D, rng):
    """The rabbit and the dog (today), lizards (long ago and on the new layers)."""
    pr = Parts('fs_critters')
    mats = [M.paint(kit, D, 'sz_rabbit', (0.80, 0.70, 0.60)), M.paint(kit, D, 'sz_rabbitw', (0.99, 0.96, 0.92), noise=0.0),
            M.paint(kit, D, 'sz_dog', (0.86, 0.60, 0.32)), M.paint(kit, D, 'sz_dogdark', (0.36, 0.22, 0.16), noise=0.0),
            M.paint(kit, D, 'sz_stick', (0.56, 0.40, 0.26)), M.paint(kit, D, 'sz_lizard', (0.52, 0.76, 0.36)), M.paint(kit, D, 'sz_lizard2', (0.92, 0.66, 0.30))]
    out = {}
    # rabbit (about 9 cm long), facing +x
    rb = [pr.add(*_ell((0, 0, 0.032), (0.042, 0.030, 0.030), 2), m=0), pr.add(*_ell((0.036, 0, 0.056), (0.020, 0.018, 0.019), 2), m=0),
          pr.add(*_ell((0.030, 0.008, 0.088), (0.006, 0.004, 0.022), 1), m=0), pr.add(*_ell((0.030, -0.008, 0.088), (0.006, 0.004, 0.022), 1), m=0),
          pr.add(*_ell((-0.044, 0, 0.040), (0.011, 0.011, 0.011), 1), m=1)]
    out['rabbit'] = rb
    # dog (about 14 cm long) with a stick
    dg = {'body': pr.add(*_ell((0, 0, 0.060), (0.062, 0.030, 0.030), 2), m=2), 'head': pr.add(*_ell((0.0, 0, 0.0), (0.026, 0.022, 0.022), 2), m=2),
          'snout': pr.add(*_ell((0.026, 0, -0.006), (0.016, 0.012, 0.011), 1), m=2), 'nose': pr.add(*_ell((0.042, 0, -0.004), (0.005, 0.005, 0.005), 1), m=3),
          'earL': pr.add(*_ell((-0.006, 0.020, 0.004), (0.010, 0.005, 0.016), 1), m=3), 'earR': pr.add(*_ell((-0.006, -0.020, 0.004), (0.010, 0.005, 0.016), 1), m=3),
          'tail': pr.add(*tube([(0, 0, 0), (-0.02, 0, 0.02), (-0.03, 0, 0.04)], [0.006, 0.005, 0.003], 6), m=2),
          'stick': pr.add(*tube([(0, -0.06, 0), (0, 0.06, 0)], [0.004, 0.004], 6), m=4),
          'legs': [pr.add(*tube([(0, 0, 0), (0, 0, -0.045)], [0.008, 0.007], 6), m=2) for _ in range(4)]}
    out['dog'] = dg
    # lizards (about 10 cm): body and tail in one, four little legs
    lz = []
    for k in range(4):
        b = pr.add(*tube([(0.05, 0, 0.008), (0.02, 0, 0.010), (-0.02, 0, 0.009), (-0.06, 0, 0.005), (-0.09, 0, 0.003)], [0.008, 0.011, 0.010, 0.005, 0.002], 6), m=5 + k % 2)
        legs = [pr.add(*tube([(0, 0, 0), (0, sd * 0.016, -0.007)], [0.003, 0.0025], 5), m=5 + k % 2) for sd in (-1, 1, -1, 1)]
        lz.append((b, legs))
    out['lizards'] = lz
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, **out}


DK, RK = 1.6, 1.6   # the dog and the rabbit at storybook scale (readable on a phone)
RABBIT_PATH = [(-1.30, -0.70), (-1.05, -0.45), (-1.45, -0.25), (-0.80, -0.30), (-0.60, -0.60), (-1.00, -0.85), (-1.30, -0.70)]
DOG_PATH = [(1.20, 0.95), (1.10, 0.40), (0.85, -0.45), (1.25, -0.80), (1.62, -0.55), (1.50, -0.10), (1.05, -0.40), (0.75, -0.62), (1.25, -0.80)]


def critters_pose(C, t):
    B = W.B; pr = C['parts']; e = W.era(t)
    # the rabbit hops round the left meadow (a hop of 0.32 s, a pause of 0.45 s)
    rb = C['rabbit']
    if W.today(t) > 0.95:
        cyc = 0.77; hopn = int(t // cyc); f = (t % cyc) / 0.32
        u0 = (hopn * 0.035) % 1.0; u1 = ((hopn + 1) * 0.035) % 1.0
        p0, hd = path_at(RABBIT_PATH, u0); p1, _ = path_at(RABBIT_PATH, u1)
        if f < 1: p = p0 + (p1 - p0) * W.sm(0, 1, f); hop = 0.045 * math.sin(math.pi * f)
        else: p = p1; hop = 0.0
        z = gz(p[0], p[1], t) + hop * RK; R = rz(hd)
        sit = 1.0 if f >= 1 else 0.0
        for j in rb: pr.set(j, (p[0], p[1], z), R @ ry(-0.25 * sit), RK)
    else:
        for j in rb: pr.hide(j)
    # the dog: arrives with the girl, runs loops with its stick, jumps at the cheer
    dg = C['dog']
    if t > B.girl0 and e > 0.9:
        u = ((t - B.girl0) * 0.075) % 1.0; p, hd = path_at(DOG_PATH, u); run = 2 * math.pi * 3.2 * t
        # the visual joke: after the cheer the dog dashes to the fossil bone and sits by it, wagging hard (its bone?)
        j0 = B.cheer0 + 0.5; sit = W.sm(j0 + 0.7, j0 + 0.9, t)
        if t > j0:
            pu, hdu = path_at(DOG_PATH, ((j0 - B.girl0) * 0.075) % 1.0); seat = np.array([W.DIG[0] - 0.05, W.DIG[1] - 0.17])
            v = W.sm(j0, j0 + 0.8, t); p = pu + (seat - pu) * v; hd = math.atan2(seat[1] - pu[1], seat[0] - pu[0]) if v < 1 else 1.9
            if v >= 1: run = 0.0
        jump = 0.06 * max(0.0, math.sin(math.pi * (t - B.cheer0) / 0.5)) if B.cheer0 < t < B.cheer0 + 1.5 and ((t - B.cheer0) % 0.5) < 0.5 else 0.0
        z = gz(p[0], p[1], t) + (0.045 + 0.008 * abs(math.sin(run)) + jump) * DK; R = rz(hd)
        root = np.array([p[0], p[1], z - 0.06 * DK])
        if t > B.cheer0 + 0.5: jump = 0.0; z = gz(p[0], p[1], t) + 0.045 * DK; root = np.array([p[0], p[1], z - 0.06 * DK])
        Rs = R @ ry(-0.45 * (sit if t > B.cheer0 + 0.5 else 0.0))       # sitting: the front comes up
        pr.set(dg['body'], root, Rs, DK)
        hp = root + Rs @ (np.array([0.062, 0, 0.088]) * DK); tilt = rx(0.35 * (sit if t > B.cheer0 + 0.5 else 0.0) * math.sin(2 * math.pi * 0.6 * t))
        pr.set(dg['head'], hp, R @ tilt, DK)
        for k in ('snout', 'nose', 'earL', 'earR'): pr.set(dg[k], hp, R @ tilt @ (rx(0.25 * math.sin(run)) if k.startswith('ear') else I3), DK)
        if t > B.cheer0 + 0.5:   # the stick lies where it dropped it
            sp, _ = path_at(DOG_PATH, ((B.cheer0 + 0.5 - B.girl0) * 0.075) % 1.0); pr.set(dg['stick'], (sp[0], sp[1], gz(sp[0], sp[1], t) + 0.005 * DK), rz(0.7), DK)
        else: pr.set(dg['stick'], hp + R @ (np.array([0.03, 0, -0.012]) * DK), R, DK)
        wag = 4.0 if t < B.cheer0 + 0.5 else 9.0
        pr.set(dg['tail'], root + Rs @ (np.array([-0.058, 0, 0.07]) * DK), Rs @ rz(0.6 * math.sin(2 * math.pi * wag * t)), DK)
        for i, (lx, ly, phs) in enumerate(((0.04, 0.018, 0), (0.04, -0.018, math.pi), (-0.04, 0.018, math.pi), (-0.04, -0.018, 0))):
            pr.set(dg['legs'][i], root + R @ (np.array([lx, ly, 0.045]) * DK), R @ ry(0.6 * math.sin(run + phs)), DK)
    else:
        for k, v in dg.items():
            if k == 'legs': [pr.hide(j) for j in v]
            else: pr.hide(v)
    # lizards: two scurry about the ferns long ago; one crosses each new layer in deep time
    for k, (b, legs) in enumerate(C['lizards']):
        show = False
        if k < 2 and W.ancient(t) > 0.7:
            a = 0.5 * t + k * 3.0; x = (-0.6 if k == 0 else 0.9) + 0.35 * math.cos(a); y = 0.35 * math.sin(a * 1.3) - (0.2 if k == 0 else -0.05)
            hd = math.atan2(0.35 * 1.3 * math.cos(a * 1.3), -0.35 * math.sin(a)); show = True
        elif k >= 2:
            for j, (a0, b0) in enumerate(W.SLOTS):
                if j % 2 != k - 2: continue
                s0 = b0 + 0.15; s1 = (W.SLOTS[j + 1][0] - 0.2) if j < 4 else W.B.seep1
                if s0 < t < s1:
                    u = (t - s0) / (s1 - s0); x = -1.5 + 2.6 * u if j % 2 == 0 else 1.4 - 2.6 * u; y = -0.25 + 0.3 * math.sin(3 * u + j); hd = 0.0 if j % 2 == 0 else math.pi
                    show = True
        if not show:
            pr.hide(b); [pr.hide(j) for j in legs]; continue
        wig = 0.35 * math.sin(2 * math.pi * 5 * t + k); R = rz(hd + wig * 0.4)
        z = gz(x, y, t) + 0.006; pr.set(b, (x, y, z), R, 1.3)
        for i, j in enumerate(legs):
            off = np.array([0.025 if i < 2 else -0.02, 0.0, 0.006]) * 1.3; pr.set(j, np.array([x, y, z]) + R @ off, R @ rz((-1) ** i * 0.6 * math.sin(2 * math.pi * 5 * t + i)), 1.3)
    pr.commit()


# ============================================================================== the girl (a storybook figure, no face detail)
def build_girl(kit, D):
    pr = Parts('fs_girl')
    mats = [M.paint(kit, D, 'sz_dress', (0.96, 0.48, 0.40)), M.paint(kit, D, 'sz_skin', (0.66, 0.44, 0.32), noise=0.0),
            M.paint(kit, D, 'sz_hair', (0.20, 0.12, 0.10), noise=0.0), M.paint(kit, D, 'sz_hat', (0.96, 0.82, 0.46)),
            M.paint(kit, D, 'sz_ribbon', (0.14, 0.52, 0.56), noise=0.0), M.paint(kit, D, 'sz_boots', (0.16, 0.40, 0.46), noise=0.0),
            M.paint(kit, D, 'sz_brush', (0.62, 0.40, 0.24), noise=0.0), M.paint(kit, D, 'sz_bristle', (0.98, 0.92, 0.74), noise=0.0),
            M.paint(kit, D, 'sz_toydino', (0.42, 0.80, 0.34), noise=0.0)]
    g = {}
    # all pieces are built in the girl's own frame (x forward, z up), pivots at their joints; she is about 32 cm tall
    g['legL'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.10)], [0.012, 0.011], 8), m=1)
    g['legR'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.10)], [0.012, 0.011], 8), m=1)
    g['bootL'] = pr.add(*_ell((0.008, 0, -0.103), (0.020, 0.013, 0.010), 1), m=5)
    g['bootR'] = pr.add(*_ell((0.008, 0, -0.103), (0.020, 0.013, 0.010), 1), m=5)
    g['dress'] = pr.add(*cone((0, 0, 0.0), 0.062, 0.12, 16, 0.030), m=0)
    g['torso'] = pr.add(*_ell((0, 0, 0.14), (0.034, 0.040, 0.040), 2), m=0)
    g['head'] = pr.add(*_ell((0, 0, 0.215), (0.040, 0.040, 0.042), 2), m=1)
    g['hair'] = pr.add(*_ell((-0.010, 0, 0.222), (0.040, 0.043, 0.040), 2), m=2)
    g['plait'] = pr.add(*tube([(-0.03, 0, 0.21), (-0.05, 0, 0.17), (-0.052, 0, 0.14)], [0.010, 0.009, 0.007], 6), m=2)
    g['brim'] = pr.add(*cone((0, 0, 0.247), 0.074, 0.006, 24, 0.074), m=3)
    g['crown'] = pr.add(*_ell((0, 0, 0.255), (0.040, 0.040, 0.030), 2), m=3)
    g['ribbon'] = pr.add(*cone((0, 0, 0.250), 0.0415, 0.010, 20, 0.0415), m=4)
    g['armL'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.085)], [0.010, 0.009], 6), m=1)
    g['armR'] = pr.add(*tube([(0, 0, 0), (0, 0, -0.085)], [0.010, 0.009], 6), m=1)
    g['brush'] = pr.add(*tube([(0, 0, -0.080), (0, 0, -0.125)], [0.005, 0.005], 6), m=6)
    g['bristle'] = pr.add(*box((0, 0, -0.135), (0.026, 0.010, 0.022)), m=7)
    # the toy dinosaur she carries and sets down: a small copy of the long-neck, in toy green
    toy = Dino(kit.bpy, 'fs_toytmp', [mats[8], mats[2]], None, 0.085)
    V, F, Mi = toy.rigid(0.0, 0.0); kit.bpy.data.objects.remove(toy.ob, do_unlink=True)
    g['toy'] = pr.add(V, F, m=8)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'g': g}


GK = 1.7        # storybook scale: the girl is about 54 cm tall on the 3.6 m block, so she reads on a phone


def girl_pose(G_, t):
    """She comes in from the left meadow, kneels in the little hollow beside the rock face, brushes (the bone appears out
    of the rock), jumps for joy, then stands and holds her toy dinosaur up next to the real fossil."""
    B = W.B; pr = G_['parts']; g = G_['g']; k_ = GK
    if t < B.girl0 or t < B.green0:
        for v in g.values(): pr.hide(v)
        pr.commit(); return None
    kneel_at = np.array([W.DIG[0] - 0.24, W.DIG[1] - 0.15])
    path = [np.array([-0.80, 1.02]), np.array([-0.55, 0.30]), np.array([-0.45, -0.30]), kneel_at]      # she runs out from behind the big tree at the back and hops the brook
    u = W.sm(B.girl0, B.girl1, t); p, hd = path_at(path, u)
    walking = B.girl0 < t < B.girl1
    face_bone = math.atan2(W.DIG[1] + 0.04 - kneel_at[1], W.DIG[0] - kneel_at[0])
    face_cam = math.atan2(-0.88, 0.47)
    def turn_to(a0, a1, f): return a0 + ((((a1 - a0) + math.pi) % (2 * math.pi)) - math.pi) * f
    yaw = turn_to(hd, face_bone, W.sm(B.girl1 - 0.25, B.kneel0 + 0.1, t))
    yaw = turn_to(yaw, face_cam, W.sm(B.hold0 - 0.3, B.hold0 + 0.2, t))
    kn = W.sm(B.kneel0, B.kneel1, t) * (1 - W.sm(B.cheer0, B.cheer0 + 0.3, t))
    ch = W.win(t, B.cheer0, B.cheer1, 0.25)
    jump = 0.05 * max(0.0, math.sin(2 * math.pi * (t - B.cheer0) / 0.6)) if B.cheer0 < t < B.cheer0 + 1.2 else 0.0
    sw = math.sin(2 * math.pi * 2.6 * t) if walking else 0.0      # running steps
    z0 = gz(p[0], p[1], t) + (0.112 - 0.075 * kn + jump) * k_
    root = np.array([p[0], p[1], z0]); R0 = rz(yaw)
    lean = 0.45 * kn * W.win(t, B.brush0, B.brush1, 0.3) + 0.2 * kn
    Rb = R0 @ ry(lean)
    for k, sd, ph in (('legL', 1, 0.0), ('legR', -1, math.pi)):
        a = 0.45 * sw * (1 if ph == 0 else -1)
        Rl = R0 @ ry(a + 1.45 * kn); hip = root + R0 @ np.array([0, sd * 0.018 * k_, 0.0])
        pr.set(g[k], hip, Rl, k_); pr.set(g['boot' + k[-1]], hip, Rl, k_)
    for k in ('dress', 'torso', 'head', 'hair', 'plait', 'brim', 'crown', 'ribbon'):
        pr.set(g[k], root, Rb, k_)
    sh = lambda sd: root + Rb @ (np.array([0.0, sd * 0.042, 0.168]) * k_)
    brush = W.win(t, B.brush0, B.brush1, 0.25) * kn
    bs = math.sin(2 * math.pi * 2.2 * t)
    aL = ry(-0.45 * sw) if walking else ry(-0.5 * kn)
    aR = ry(0.45 * sw) if walking else I3
    if brush > 0.01: aR = rx(-0.35 * bs * brush) @ ry(-(1.25 + 0.25 * bs) * brush)      # brush, brush, on the rock face
    if ch > 0.01:
        aL = rx(2.5 * ch) @ ry(-0.2 * ch); aR = rx(-2.5 * ch) @ ry(-0.2 * ch)
    hold = W.sm(B.hold0, B.hold1, t)
    if hold > 0.01:
        aL = ry(-2.7 * hold) @ rx(0.35 * hold)       # the toy held high, next to the fossil
        aR = rz(0.0) @ rx(-0.5 * hold)
    pr.set(g['armL'], sh(1), Rb @ aL, k_); pr.set(g['armR'], sh(-1), Rb @ aR, k_)
    pr.set(g['brush'], sh(-1), Rb @ aR, k_); pr.set(g['bristle'], sh(-1), Rb @ aR, k_)
    hand = sh(1) + Rb @ aL @ (np.array([0, 0, -0.09]) * k_)
    pr.set(g['toy'], hand + Rb @ aL @ (np.array([0, 0, -0.035]) * k_), R0 @ rz(math.pi / 2 + 0.6 * hold), k_)
    pr.commit()
    return root


# ============================================================================== the bone that pokes out (today)
def build_dug_bone(kit, D):
    m = M.paint(kit, D, 'sz_dugbone', (0.88, 0.86, 0.80), noise=0.1)
    pr = Parts('fs_dugbone')
    v, f = tube([(-0.075, 0, 0), (0.075, 0, 0)], [0.016, 0.016], 10); i0 = pr.add(v, f)
    ks = [pr.add(*_ell((sx * 0.078, sy * 0.016, 0), (0.024, 0.020, 0.020), 2)) for sx in (-1, 1) for sy in (-1, 1)]
    pr.build(kit.bpy, [m], kit.coll)
    return {'parts': pr, 'ids': [i0] + ks}


BONE_K = 1.7


def dug_bone_pose(Db, t):
    """The bone in the little rock face (today): hidden in the rock until her brushing clears it; returns the point the
    FOSSIL label points at."""
    pr = Db['parts']; show = W.today(t) > 0.5
    c = (W.DIG[0], W.DIG[1] + 0.050, W.Z_NOW - W.HOLLOW_D + 0.060 + W.lift(t))
    for j in Db['ids']:
        if show: pr.set(j, c, rz(0.12) @ ry(-0.10), BONE_K)
        else: pr.hide(j)
    pr.commit()
    return np.array([c[0] - 0.06, c[1] - 0.03, c[2] + 0.02])


# ============================================================================== easter eggs
def build_eggs(kit, D):
    pr = Parts('fs_eggs')
    mats = [M.paint(kit, D, 'sz_ball', (0.92, 0.18, 0.16), noise=0.0), M.paint(kit, D, 'sz_ballw', (0.99, 0.96, 0.90), noise=0.0),
            M.paint(kit, D, 'sz_car', (0.20, 0.46, 0.86), noise=0.0), M.paint(kit, D, 'sz_wheel', (0.12, 0.12, 0.16), noise=0.0),
            M.paint(kit, D, 'sz_duck', (1.0, 0.84, 0.16), noise=0.0), M.paint(kit, D, 'sz_beak', (1.0, 0.52, 0.12), noise=0.0),
            M.paint(kit, D, 'sz_kite', (0.98, 0.42, 0.40), noise=0.0), M.paint(kit, D, 'sz_kite2', (0.99, 0.82, 0.30), noise=0.0),
            M.paint(kit, D, 'sz_teddy', (0.78, 0.52, 0.28)), M.paint(kit, D, 'sz_teddy2', (0.96, 0.84, 0.66), noise=0.0),
            M.paint(kit, D, 'sz_string', (0.96, 0.96, 0.92), noise=0.0), M.paint(kit, D, 'sz_pad', (0.24, 0.58, 0.34), noise=0.0)]
    e = {}
    # a red ball with a white band, lost in today's soil of the front face (half out of the wall)
    e['ball'] = pr.add(*sphere((0, 0, 0), (0.036, 0.036, 0.036), 2), m=0)
    e['band'] = pr.add(*cone((0, 0, -0.006), 0.0372, 0.012, 20, 0.0372), m=1)
    # a little blue toy car in the right face's soil, nose out (the hidden one)
    e['car'] = [pr.add(*box((0, 0, 0.012), (0.075, 0.036, 0.020)), m=2), pr.add(*box((-0.006, 0, 0.030), (0.036, 0.032, 0.018)), m=2)] + \
               [pr.add(*tube([(wx, -0.021, 0.004), (wx, 0.021, 0.004)], [0.009, 0.009], 10), m=3) for wx in (-0.024, 0.024)]
    # a rubber duck bobbing down the brook
    e['duck'] = [pr.add(*_ell((0, 0, 0.012), (0.030, 0.022, 0.018), 2), m=4), pr.add(*_ell((0.020, 0, 0.038), (0.014, 0.014, 0.014), 2), m=4),
                 pr.add(*_ell((0.036, 0, 0.036), (0.009, 0.006, 0.004), 1), m=5), pr.add(*_ell((-0.030, 0, 0.022), (0.008, 0.010, 0.006), 1), m=4)]
    e['pad'] = pr.add(*cone((0, 0, -0.004), 0.045, 0.003, 18, 0.045), m=11)
    # a kite stuck in the big tree, tugging in the wind, its tail of bows dangling
    k1 = pr.add([(0, 0, 0.09), (0.05, 0, 0.0), (0, 0, -0.05), (0, 0.0005, 0.0)], [(0, 1, 2), (0, 2, 3)], m=6)
    k2 = pr.add([(0, -0.0005, 0.09), (-0.05, -0.0005, 0.0), (0, -0.0005, -0.05)], [(0, 1, 2)], m=7)
    tail = [pr.add([(-0.012, 0, 0.0), (0.012, 0, 0.008), (0.012, 0, -0.008), (-0.012, 0, 0.0)], [(0, 1, 2)], m=7 - i % 2) for i in range(5)]
    e['kite'] = (k1, k2, tail)
    # a teddy bear left sitting on the meadow
    e['teddy'] = [pr.add(*_ell((0, 0, 0.034), (0.030, 0.028, 0.034), 2), m=8), pr.add(*_ell((0.004, 0, 0.082), (0.024, 0.024, 0.022), 2), m=8),
                  pr.add(*_ell((0.002, 0.020, 0.100), (0.009, 0.004, 0.009), 1), m=8), pr.add(*_ell((0.002, -0.020, 0.100), (0.009, 0.004, 0.009), 1), m=8),
                  pr.add(*_ell((0.022, 0, 0.078), (0.010, 0.012, 0.009), 1), m=9), pr.add(*_ell((0.018, 0, 0.036), (0.014, 0.020, 0.020), 1), m=9),
                  pr.add(*_ell((0.022, 0.024, 0.008), (0.018, 0.010, 0.010), 1), m=8), pr.add(*_ell((0.022, -0.024, 0.008), (0.018, 0.010, 0.010), 1), m=8),
                  pr.add(*_ell((0.0, 0.032, 0.046), (0.010, 0.010, 0.020), 1), m=8), pr.add(*_ell((0.0, -0.032, 0.046), (0.010, 0.010, 0.020), 1), m=8)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'e': e}


BALL_R = 0.036 * 1.6
CAR = (W.HX - 0.012, 0.30, -0.046)
DUCK_PATH = [p for p in cw.catmull([tuple(q) for q in W.RIVER], 240) if abs(p[0]) < W.HX - 0.25 and abs(p[1]) < W.HY - 0.15]
KITE = (1.08, 0.56, 0.46)          # on the camera side of the big tree's crown
TEDDY = (-1.05, -0.62)


def _roll(p0, p1, u, t):
    p = np.asarray(p0) + (np.asarray(p1) - np.asarray(p0)) * u; d = np.asarray(p1) - np.asarray(p0); L = np.linalg.norm(d)
    ang = L * u / BALL_R; ax = math.atan2(d[1], d[0])
    return p, rz(ax) @ ry(ang)


def eggs_pose(E, t):
    """Today: the red ball rolls in (hook) and back (send-off), the toy car in the right face, the rubber duck down the
    brook, the kite tugging in the tree, the teddy. Long ago: the visual joke, a yellow flower floating down the river
    on its pad, shaped exactly like a rubber duck."""
    B = W.B; pr = E['parts']; e = E['e']; td = W.today(t) > 0.97 and W.base(t) < W.Z_NOW + 0.01
    def put(j, p, R=None, s=1.0, on=None):
        if (td if on is None else on): pr.set(j, p, R, s)
        else: pr.hide(j)
    # the red ball
    if t < B.rw0 + 0.3:
        u = W.sm(B.ball0, B.ball1, t); p, Rb = _roll((-1.85, -0.32), (-1.00, -0.44), u, t); sc = 1.6 * (1 - W.sm(B.rw0, B.rw0 + 0.3, t))
    else:
        u = W.sm(B.ballback0, B.ballback1, t); p, Rb = _roll((-1.85, -0.86), (-1.18, -0.80), u, t); sc = 1.6 * (1.0 if t > B.ballback0 else 0.0)
    inside = abs(p[0]) < W.HX - 0.02
    zb = gz(max(p[0], -W.HX + 0.03), p[1], t) + BALL_R
    put(e['ball'], (p[0], p[1], zb), Rb, sc, sc > 0.01 and inside and (t < B.rw0 + 0.3 or td))
    put(e['band'], (p[0], p[1], zb), Rb @ rx(math.pi / 2), sc, sc > 0.01 and inside and (t < B.rw0 + 0.3 or td))
    for j in e['car']: put(j, (CAR[0], CAR[1], CAR[2] + W.lift(t)), I3)
    # today: the rubber duck floats down the brook; long ago: the duck-shaped flower floats down the river on a pad
    old = W.ancient(t) > 0.6 and t < B.flood0
    u = (t * 0.035) % 1.0; DP = DUCK_PATH; p, hdg = path_at(DP, u); xs, ys = float(p[0]), float(p[1])
    lv = W.water_level(t); bob = 0.004 * math.sin(2 * math.pi * 0.9 * t)
    Rd = rz(hdg + 0.25 * math.sin(0.6 * t)) @ rx(0.08 * math.sin(2 * math.pi * 0.9 * t))
    for j in e['duck']: put(j, (xs, ys, lv - 0.008 + bob), Rd, 1.5, td or old)
    put(e['pad'], (xs, ys, lv + 0.001), Rd, 1.5, old)
    k1, k2, tail = e['kite']; tug = 0.22 * math.sin(2 * math.pi * 0.7 * t) + 0.08 * math.sin(2 * math.pi * 1.9 * t)
    Rk = rz(-1.0) @ rx(0.35 + tug) @ ry(0.3)
    kp = (KITE[0], KITE[1], KITE[2] + W.lift(t)); put(k1, kp, Rk, 1.5); put(k2, kp, Rk, 1.5)
    base = np.array(kp) + Rk @ np.array([0, 0, -0.075])
    for i, j in enumerate(tail):
        sw = 0.03 * math.sin(2 * math.pi * 0.7 * t - 0.6 * i) * (i + 1) / 5
        put(j, base + np.array([sw, 0.0, -0.05 * (i + 1)]), rz(-1.0) @ rx(tug * 0.5), 1.5)
    tz = gz(TEDDY[0], TEDDY[1], t) - 0.004
    for j in e['teddy']: put(j, (TEDDY[0], TEDDY[1], tz), rz(-1.2), 1.6)
    pr.commit()


# ============================================================================== the series mascot: a little snail
SNAIL_HOME = (1.42, -W.HY + 0.07)
SK = 2.8     # the mascot is about 14 cm long: findable on a phone, still small


def build_snail(kit, D):
    """The series' silent recurring creature (research 4.1: a tiny creature in the corner of every block who reacts and
    never speaks): a little snail with a coral and gold shell on the front left corner. It is there in every era (snails
    are older than dinosaurs), riding the top as it sinks and rises; it hides in its shell when time rewinds, in the floods
    and in the rain, and its eyes stretch up at the cheer."""
    pr = Parts('fs_snail')
    mats = [M.paint(kit, D, 'sz_snailshell', (0.96, 0.52, 0.40), noise=0.0), M.paint(kit, D, 'sz_snailband', (0.99, 0.82, 0.38), noise=0.0),
            M.paint(kit, D, 'sz_snailbody', (0.86, 0.84, 0.66), noise=0.0), M.paint(kit, D, 'sz_snaileye', (0.10, 0.10, 0.18), noise=0.0)]
    s = {'shell': pr.add(*sphere((0, 0, 0.030), (0.026, 0.017, 0.028), 2), m=0), 'band': pr.add(*sphere((0.0, 0, 0.030), (0.016, 0.0185, 0.018), 2), m=1),
         'body': pr.add(*sphere((0.012, 0, 0.007), (0.040, 0.012, 0.008), 2), m=2)}
    s['stalks'] = [pr.add(*tube([(0, 0, 0), (0.004, sd * 0.004, 0.022)], [0.0025, 0.0018], 5), m=2) for sd in (-1, 1)]
    s['eyes'] = [pr.add(*sphere((0.004, sd * 0.004, 0.024), (0.0035, 0.0035, 0.0035), 1), m=3) for sd in (-1, 1)]
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 's': s}


def snail_pose(Sn, t):
    """Today it sits on the front right corner above the fossil's skull and peeks over the edge at it; long ago it rides
    the turtle; it hides in its shell in the rewind, the floods and the rain; it stretches up at the cheer and waves its
    eye stalks at the end."""
    B = W.B; pr = Sn['parts']; s = Sn['s']
    import szstory as ST
    riding = W.ancient(t) > 0.5 and t < B.flood0
    if riding:
        tp, tyaw = ST.turtle_pos(t); p = tp + np.array([0, 0, 0.068 * ST.TURTLE_K]); hdg = tyaw
    else:
        x, y = SNAIL_HOME; x = x - 0.06 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 30.0)); p = np.array([x, y, gz(x, y, t) - 0.002]); hdg = -math.pi / 2 + 0.5
    hide = max(W.win(t, B.rw0 - 0.2, B.rw1 + 0.2, 0.25), W.win(t, B.flood0 - 0.3, B.stack1 + 0.4, 0.3), W.win(t, B.rain0, B.rain1 + 0.3, 0.3))
    out = 1 - hide
    up = 1 + 0.6 * W.win(t, B.cheer0, B.hold0 + 0.5, 0.3)
    peek = 0.35 * W.win(t, 0.6, B.rw0 - 0.3, 0.5)                        # leans over the edge to look at the bone
    wave = W.sm(B.wave0, B.wave0 + 0.4, t) * 0.7 * math.sin(2 * math.pi * 1.6 * t)
    R = rz(hdg) @ ry(peek)
    pr.set(s['shell'], p, R, SK); pr.set(s['band'], p, R, SK)
    if out < 0.02:
        pr.hide(s['body']); [pr.hide(j) for j in s['stalks'] + s['eyes']]
    else:
        pr.set(s['body'], p, R, (out * SK, SK, SK))
        head = p + R @ (np.array([0.040 * out, 0, 0.010]) * SK)
        for j, ph in zip(s['stalks'] + s['eyes'], (0, 1, 0, 1)):
            wob = rx(0.25 * math.sin(2 * math.pi * 0.5 * t + ph) + wave * (1 if ph == 0 else -1))
            pr.set(j, head, R @ wob, (out * SK, out * SK, out * up * SK))
    pr.commit()
