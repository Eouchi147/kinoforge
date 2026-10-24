"""How is a volcano born? The volcano itself (bpy + numpy). Every pose is a pure function of t.

  the cut face   the magma chamber (breathing), the dark crack up from it, the magma in the crack (rises, lighter than the
                 rock), gas bubbles that swell as they rise, the soil that forms on the new rock, little fish in the sea band
  the crater     a glowing lake at the vent when the magma arrives
  the fountain   nine eruptions (the first on the music's big entrance, then its eight hits): glowing drops out of the TOP
  the flows      lava ribbons down the slopes (gold, red, then cold and dark) and steam where they meet the sea
  the sea        the water of the slice: its top, and its cut faces, only where the island does not fill them
  the bottle     the visual explanation: a shaken fizzy drink on the beach that pops with the volcano; its cap lands on the
                 sandcastle (the small visual joke)
"""
import math

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
from szgeo import Parts, sphere, tube, cone, box, disc, rz, ry, rx, euler, I3

YF = -W.HY - 0.0035           # the cut face's overlays stand this far in front of it (slice frame): scorch, crack, chamber, magma, bubbles from the wall outwards


def gh(x, y, t):
    """Ground height at (x, y) on the slice, in the slice frame (no lift)."""
    return float(W.h_now(np.array([x]), np.array([y]), t)[0])


# ============================================================================== the cut face
def _poly_fan(P, hts, es):
    V = [(0.0, 0.0, 0.0)]; F = []; H = [hts[0]]; E = [es[0]]
    for i, (x, z) in enumerate(P): V.append((x, YF, z)); H.append(hts[1]); E.append(es[1])
    return V, H, E


def build_face(kit, D, rng):
    bpy = kit.bpy; out = {}
    lava = M.mat_lava(kit, D, 'fs_magma')
    dark = M.mat_glow(kit, D, 'fs_crack', (0.10, 0.04, 0.10), 1.0)
    # the chamber: a rounded, lumpy blob (dark scorched edge, then three glowing rings)
    th = np.linspace(0, 2 * math.pi, 56, endpoint=False)
    def ring(k):
        x = W.XC + k * W.CH_A * np.cos(th) * (1 + 0.06 * np.sin(3 * th + 0.4)); z = W.CH_Z + k * W.CH_B * np.sin(th) * (1 + 0.10 * np.cos(2 * th)) * np.where(np.sin(th) < 0, 0.85, 1.0)
        return np.column_stack([x, z])
    def fan_rings(rings, yv):
        V = [(W.XC, yv, W.CH_Z)]; H = [1.0]; E = [1.0]; F = []; rows = []
        for k, (sc, ht, e) in enumerate(rings):
            P = ring(sc); rows.append(len(V))
            for (x, z) in P: V.append((x, yv, z)); H.append(ht); E.append(e)
        n = len(th)
        for i in range(n): F.append((0, rows[0] + i, rows[0] + (i + 1) % n))
        for a, b in zip(rows, rows[1:]):
            for i in range(n): F.append((a + i, b + i, b + (i + 1) % n, a + (i + 1) % n))
        return V, F, H, E
    V, F, _, _ = fan_rings([(1.12, 0, 0)], YF + 0.0030)
    # the dark scorch: just a bigger fan in the dark material
    P = ring(1.14); V = [(W.XC, YF + 0.0030, W.CH_Z)] + [(x, YF + 0.0030, z) for x, z in P]; n = len(th)
    out['scorch'] = cw.mk_mesh(bpy, 'fs_scorch', V, [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)], [dark], None, False, kit.coll)
    V, F, H, E = fan_rings([(0.28, 0.80, 1.0), (0.66, 0.55, 0.62), (1.0, 0.30, 0.0)], YF + 0.0000)
    out['chamber'] = cw.mk_mesh(bpy, 'fs_chamber', V, F, [lava], None, False, kit.coll, {'ht': ('FLOAT', H), 'e': ('FLOAT', E)})
    # the crack and the magma in it: strips along z (rewritten each frame, the top follows the crater floor)
    NR = 56
    Fq = [(3 * i + c, 3 * i + c + 1, 3 * (i + 1) + c + 1, 3 * (i + 1) + c) for i in range(NR - 1) for c in (0, 1)]
    out['crack'] = cw.mk_mesh(bpy, 'fs_cracks', np.zeros((3 * NR, 3)), Fq, [dark], None, False, kit.coll)
    out['magma'] = cw.mk_mesh(bpy, 'fs_magmastrip', np.zeros((3 * NR, 3)), Fq, [lava], None, False, kit.coll,
                              {'ht': ('FLOAT', np.zeros(3 * NR)), 'e': ('FLOAT', np.tile([0.0, 1.0, 0.0], NR))})
    out['NR'] = NR
    # bubbles in the magma: flat discs on the face
    pr = Parts('fs_bubbles'); bm = M.mat_glow(kit, D, 'fs_bubble', (1.0, 0.97, 0.78), 1.9)
    out['bub'] = []
    for k in range(34):
        Vd = [(0, 0, 0)] + [(math.cos(a), 0, math.sin(a)) for a in np.linspace(0, 2 * math.pi, 15)[:-1]]
        j = pr.add(Vd, [(0, 1 + i, 1 + (i + 1) % 14) for i in range(14)], 0)
        out['bub'].append((j, rng.uniform(0, 1), rng.uniform(-1, 1), rng.uniform(0.7, 1.4)))
    pr.build(bpy, [bm], kit.coll, smooth=False); pr.ob.visible_shadow = False; out['bubp'] = pr
    # the crater lake: a glowing half disc at the vent (horizontal)
    nsg = 20; V = [(0, 0, 0)] + [(math.cos(a), math.sin(a) * 0.9, 0) for a in np.linspace(0, math.pi, nsg)]
    Fd = [(0, 1 + i, 2 + i) for i in range(nsg - 1)]
    out['lake'] = cw.mk_mesh(bpy, 'fs_lake', V, Fd, [lava], None, False, kit.coll, {'ht': ('FLOAT', [0.95] + [0.55] * nsg), 'e': ('FLOAT', [1.0] + [0.0] * nsg)})
    # soil on the new rock: a strip along the cut face's top edge (brown, with a green lip), grows in the calm
    NX = 70
    Fs = [(3 * i + c, 3 * i + c + 1, 3 * (i + 1) + c + 1, 3 * (i + 1) + c) for i in range(NX - 1) for c in (0, 1)]
    sm_ = M.paint(kit, D, 'sz_soil', (0.34, 0.20, 0.13), noise=0.2)
    gm = M.paint(kit, D, 'sz_soillip', (0.36, 0.70, 0.30), noise=0.1)
    out['soil'] = cw.mk_mesh(bpy, 'fs_soil', np.zeros((3 * NX, 3)), Fs, [sm_, gm], [1, 0] * (NX - 1), False, kit.coll)
    out['NX'] = NX
    # fish in the sea band of the cut face
    pr2 = Parts('fs_fish'); fm = [M.paint(kit, D, 'sz_fish1', (1.0, 0.55, 0.20), noise=0.0), M.paint(kit, D, 'sz_fish2', (0.98, 0.84, 0.25), noise=0.0)]
    out['fish'] = []
    for k in range(4):
        body = pr2.add(*sphere((0, 0, 0), (0.034, 0.008, 0.017), 1), m=k % 2)
        tail = pr2.add([(-0.026, 0, 0), (-0.056, 0, 0.020), (-0.056, 0, -0.020)], [(0, 1, 2), (0, 2, 1)], m=k % 2)
        out['fish'].append((body, tail, rng.uniform(0, 6.28), -1 if k % 2 else 1, 0.5 + 0.5 * k))
    pr2.build(bpy, fm, kit.coll); out['fishp'] = pr2
    return out


def _strip_rows(zs, xs, hw, taper, dy=0.0):
    """Vertices (3 per row: left, centre, right) of a vertical strip on the face."""
    V = np.zeros((len(zs), 3, 3)); w = hw * taper
    V[:, 0, 0] = xs - w; V[:, 1, 0] = xs; V[:, 2, 0] = xs + w; V[:, :, 1] = YF + dy; V[:, :, 2] = zs[:, None]
    return V.reshape(-1, 3)


def face_pose(F, D, t):
    lf = W.lift(t); NR = F['NR']
    for k in ('scorch', 'chamber', 'crack', 'magma', 'bubp', 'soil', 'fishp'):
        ob = F[k].ob if k in ('bubp', 'fishp') else F[k]; ob.location = (0, 0, lf)
    top = W.pipe_top(t); lvl = W.magma_level(t)
    # the crack: a dark hairline from the chamber to the crater (always there)
    zs = np.linspace(W.PIPE_Z0, top, NR); xs = W.pipe_x(zs)
    cw_ = np.sin(np.linspace(0.0, math.pi, NR)) ** 0.25
    taper = (0.45 + 0.55 * np.clip((zs - W.PIPE_Z0) / 0.08, 0, 1)) * (0.75 + 0.25 * cw_)
    me = F['crack'].data; me.vertices.foreach_set('co', _strip_rows(zs, xs, W.PIPE_W * 1.15, taper, 0.0020).astype(np.float32).ravel()); me.update()
    # the magma in it: from the chamber to its front, a round nose
    m = F['magma']; fill = max(lvl - W.PIPE_Z0, 1e-4)
    zs2 = W.PIPE_Z0 + fill * np.linspace(0, 1, NR); xs2 = W.pipe_x(zs2)
    nose = np.sqrt(np.clip(1 - ((zs2 - (lvl - 0.045)) / 0.045), 0, 1)) * (zs2 > lvl - 0.045) + (zs2 <= lvl - 0.045)
    wide = (0.7 + 0.3 * np.clip((zs2 - W.PIPE_Z0) / 0.1, 0, 1)) * nose
    on = lvl > W.PIPE_Z0 + 0.025
    m.hide_render = not on
    if on:
        me = m.data; me.vertices.foreach_set('co', _strip_rows(zs2, xs2, W.PIPE_W * 0.86, wide, -0.0012).astype(np.float32).ravel()); me.update()
        heat = 0.55 + 0.35 * (zs2 - W.PIPE_Z0) / max(fill, 1e-3) + 0.25 * W.sm(W.B.gas0, W.B.e0, t)
        ht = np.repeat(np.clip(heat, 0, 1)[:, None], 3, 1)
        me.attributes['ht'].data.foreach_set('value', ht.ravel().astype(np.float32))
    # the chamber breathes: a slow pulse that swells with the story (D 'pulse' lights both)
    D.set('pulse', 0.18 * math.sin(2 * math.pi * t / 2.6) + 0.5 * W.sm(W.B.glow0, W.B.glow0 + 3.5, t) * 0.25 + 0.5 * W.gas_amount(t) * math.sin(2 * math.pi * 6.0 * t) * 0.25)
    # bubbles: little glowing blobs lift off the chamber into the crack; in the gas they swell as they rise
    pr = F['bubp']; g = W.gas_amount(t); lift_on = W.sm(W.B.rise0, W.B.rise0 + 1.5, t) * (1 - W.sm(W.B.e0 + 0.2, W.B.e0 + 1.2, t))
    for j, ph, off, spd in F['bub']:
        if lift_on < 0.01 or lvl < W.PIPE_Z0 + 0.06: pr.hide(j); continue
        cyc = 3.0 / spd; u = ((t / cyc + ph) % 1.0)
        z = W.PIPE_Z0 + 0.02 + (lvl - W.PIPE_Z0 - 0.06) * u
        r = (0.0075 + 0.0170 * g * (0.4 + 0.6 * u)) * lift_on
        x = W.pipe_x(z) + off * W.PIPE_W * 0.45 * (1 - 0.4 * r / 0.02)
        pr.set(j, (x, YF - 0.0030, z), I3, r)
    pr.commit()
    # the crater lake
    lk = F['lake']; cf = W.crater_floor(t); arrive = W.sm(W.B.gas1 - 1.2, W.B.gas1 + 0.4, t) * (1 - W.sm(W.B.e0 + 3.0, W.B.e0 + 7.0, t))
    for e in W.ERUPT[1:]: arrive = max(arrive, W.win(t, e - 0.3, e + 2.5, 0.4))
    lk.hide_render = arrive < 0.02
    if arrive >= 0.02:
        rad = W.CR_R * 0.85 * (0.5 + 0.5 * arrive)
        V = np.array([(0, 0, 0)] + [(math.cos(a), math.sin(a) * 0.9, 0) for a in np.linspace(0, math.pi, 20)]) * (rad, rad / W.KY * 0.6, 1)
        V = V + (W.XC, W.YC + 0.012, cf + 0.003 + lf)
        lk.data.vertices.foreach_set('co', V.astype(np.float32).ravel()); lk.data.update()
    # the soil
    so = F['soil']; NX = F['NX']; k = W.sm(W.B.soil0, W.B.soil1, t)
    so.hide_render = k < 0.02
    if k >= 0.02:
        xs = np.linspace(-1.06, 1.06 - 0.06, NX) * 1.0 + W.XC * 0; xs = np.linspace(W.XC - 0.98, W.XC + 0.98, NX)
        zt = W.h_now(xs, np.full(NX, W.YC), t) - 0.0; thick = 0.040 * k * (0.7 + 0.3 * np.sin(np.linspace(0, 3.14, NX)))
        edge = np.clip(1 - (np.abs(xs - W.XC) / 0.98) ** 6, 0, 1)
        V = np.zeros((NX, 3, 3)); V[:, :, 0] = xs[:, None]; V[:, :, 1] = YF
        V[:, 0, 2] = zt + 0.002; V[:, 1, 2] = zt + 0.002 - thick * 0.5 * edge; V[:, 2, 2] = zt + 0.002 - thick * edge
        so.data.vertices.foreach_set('co', V.reshape(-1, 3).astype(np.float32).ravel()); so.data.update()
    # fish swim to and fro in the sea band, each in its own stretch
    fp = F['fishp']
    for body, tail, ph, side, sp in F['fish']:
        x0 = W.XC + side * (W.RS + 0.18 + 0.12 * sp) + 0.0; x0 = float(np.clip(x0, -W.HX + 0.12, W.HX - 0.12))
        x = x0 + 0.10 * math.sin(0.5 * t + ph); z = -0.12 - 0.05 * sp + 0.02 * math.sin(1.7 * t + ph) + lf
        dirn = 1 if math.cos(0.5 * t + ph) > 0 else -1
        ground = gh(x, W.YC, t)
        if ground > -0.04: fp.hide(body); fp.hide(tail); continue
        R = rz(0.0 if dirn > 0 else math.pi) @ ry(0.0); wag = rx(0.0) @ rz(0.25 * math.sin(9 * t + ph))
        fp.set(body, (x, YF - 0.002, z), R, 1.2); fp.set(tail, (x, YF - 0.002, z), R @ wag, 1.2)
    fp.commit()


# ============================================================================== the sea of the slice
def build_water(kit, D):
    bpy = kit.bpy; mat = M.mat_water(kit, D); e = 0.0012; out = {}
    nx, ny = 73, 45; xs = np.linspace(-W.HX + e, W.HX - e, nx); ys = np.linspace(-W.HY + e, W.HY - e, ny)
    X, Y = np.meshgrid(xs, ys); ii = np.arange(nx * ny).reshape(ny, nx)
    Fq = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
    out['top'] = cw.mk_mesh(bpy, 'fs_seatop', np.column_stack([X.ravel(), Y.ravel(), np.zeros(nx * ny)]), Fq.tolist(), [mat], None, False, kit.coll)
    out['top'].visible_shadow = False; out['xy'] = np.column_stack([X.ravel(), Y.ravel()])
    # the four cut faces: a column of sea only where the island does not fill it
    n = 64; out['sides'] = []
    for name, p0, p1 in (('f', (-W.HX + e, -W.HY - 0.0015), (W.HX - e, -W.HY - 0.0015)), ('b', (-W.HX + e, W.HY + 0.0015), (W.HX - e, W.HY + 0.0015)),
                         ('l', (-W.HX - 0.0015, -W.HY + e), (-W.HX - 0.0015, W.HY - e)), ('r', (W.HX + 0.0015, -W.HY + e), (W.HX + 0.0015, W.HY - e))):
        u = np.linspace(0, 1, n); xy = np.column_stack([p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u])
        Fs = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(n - 1)]
        if name in ('f', 'r'): pass
        else: Fs = [f[::-1] for f in Fs]
        ob = cw.mk_mesh(bpy, 'fs_sea' + name, np.zeros((2 * n, 3)), Fs, [mat], None, False, kit.coll); ob.visible_shadow = False
        out['sides'].append((ob, xy))
    return out


def water_pose(Wt, t):
    lf = W.lift(t); sea = W.Z_SEA + lf + 0.004
    me = Wt['top'].data; xy = Wt['xy']
    me.vertices.foreach_set('co', np.column_stack([xy, np.full(len(xy), sea)]).astype(np.float32).ravel()); me.update()
    for ob, xy_ in Wt['sides']:
        h = W.h_now(xy_[:, 0], xy_[:, 1], t) + lf; top = np.full(len(xy_), sea)
        bot = np.minimum(h, top - 1e-4)
        V = np.zeros((len(xy_), 2, 3)); V[:, 0, :2] = xy_; V[:, 1, :2] = xy_; V[:, 0, 2] = bot; V[:, 1, 2] = top
        ob.data.vertices.foreach_set('co', V.reshape(-1, 3).astype(np.float32).ravel()); ob.data.update()


# ============================================================================== lava flows, fountains, steam
def build_flows(kit, D):
    bpy = kit.bpy; lava = M.mat_lava(kit, D, 'fs_lava'); out = {'flows': [], 'N': 40}
    N = out['N']
    Fq = [(3 * i + c, 3 * i + c + 1, 3 * (i + 1) + c + 1, 3 * (i + 1) + c) for i in range(N - 1) for c in (0, 1)]
    for j in range(9):
        ks = [W.FLOW_OF[j]] + ([W.FLOW_EXTRA[j]] if j in W.FLOW_EXTRA else [])
        for k in ks:
            ob = cw.mk_mesh(bpy, f'fs_flow{j}_{k}', np.zeros((3 * N, 3)), Fq, [lava], None, False, kit.coll,
                            {'ht': ('FLOAT', np.zeros(3 * N)), 'e': ('FLOAT', np.tile([0.0, 1.0, 0.0], N))})
            ob.visible_shadow = False
            out['flows'].append((j, k, ob, W.flow_path(k, N)))
    # steam where a flow meets the sea (soft white puffs)
    pr = Parts('fs_steam'); sm_ = M.paint(kit, D, 'sz_steam', (1.0, 0.99, 0.97), noise=0.0)
    out['steam'] = []
    for fi, (j, k, ob, P) in enumerate(out['flows']):
        for q in range(5): out['steam'].append((fi, q, pr.add(*sphere((0, 0, 0), (1, 1, 0.8), 1), 0)))
    pr.build(bpy, [sm_], kit.coll); pr.ob.visible_shadow = False; out['steamp'] = pr
    return out


def flows_pose(FL, D, t):
    lf = W.lift(t); N = FL['N']; tau = W.FLOW_COOL / 2.4
    for fi, (j, k, ob, P) in enumerate(FL['flows']):
        t0 = W.ERUPT[j]; dur = W.FLOW_DUR * (0.8 + 0.2 * W.STRENGTH[j])
        f = W.sm(t0 + 0.2, t0 + 0.2 + dur, t)
        if t < t0 + 0.2 or t > t0 + 0.2 + dur + W.FLOW_COOL + 2.0: ob.hide_render = True; continue
        ob.hide_render = False
        s = np.linspace(0, 1, N) * f; s_ = np.clip(s, 0, 1)
        idx = s_ * (N - 1); i0 = np.clip(np.floor(idx).astype(int), 0, N - 2); fr = idx - i0
        xy = P[i0] * (1 - fr)[:, None] + P[i0 + 1] * fr[:, None]
        d = np.gradient(xy, axis=0); nrm = np.column_stack([-d[:, 1], d[:, 0]]); nrm /= (np.linalg.norm(nrm, axis=1)[:, None] + 1e-9)
        hw = 0.034 + 0.034 * np.sin(math.pi * np.clip(np.linspace(0, 1, N) ** 0.7, 0, 1)) ** 0.5
        hw = hw * (0.5 + 0.5 * W.STRENGTH[j] ** 0.5) * np.where(np.linspace(0, 1, N) > 0.9, 0.7, 1.0)
        # the flow's head is thick and round; points not yet reached collapse onto the head
        z = W.h_now(xy[:, 0], xy[:, 1], t) + lf + 0.007
        V = np.zeros((N, 3, 3))
        for c, sd in enumerate((-1, 0, 1)):
            V[:, c, :2] = xy + nrm * hw[:, None] * sd; V[:, c, 2] = z + (0.004 if sd == 0 else 0.0)
        # heat: lava reaches each point at t0 + s * dur, then cools
        arrive = t0 + 0.2 + np.linspace(0, 1, N) * dur
        age = np.maximum(t - arrive, 0.0); heat = np.exp(-age / tau) * (np.linspace(0, 1, N) * f <= f + 1e-9)
        heat = np.where(t < arrive, 1.0, heat)
        ht = np.repeat(heat[:, None], 3, 1)
        me = ob.data; me.vertices.foreach_set('co', V.reshape(-1, 3).astype(np.float32).ravel())
        me.attributes['ht'].data.foreach_set('value', ht.ravel().astype(np.float32)); me.update()
    pr = FL['steamp']
    for fi, q, p in FL['steam']:
        j, k, ob, P = FL['flows'][fi]; t0 = W.ERUPT[j]; dur = W.FLOW_DUR * (0.8 + 0.2 * W.STRENGTH[j]); ta = t0 + 0.2 + dur
        if not (ta - 0.3 < t < ta + W.FLOW_COOL + 1.5): pr.hide(p); continue
        T = 2.4; age = (((t - ta) / T + q / 5.0) % 1.0); fade = W.sm(ta - 0.3, ta + 0.6, t) * (1 - W.sm(ta + W.FLOW_COOL - 0.5, ta + W.FLOW_COOL + 1.5, t))
        x, y = P[-1]; r = (0.030 + 0.075 * age) * fade * (0.6 + 0.4 * W.STRENGTH[j])
        c = (x + 0.05 * math.sin(2 * math.pi * age + q), y + 0.03 * age, W.Z_SEA + 0.02 + lf + 0.40 * age)
        if r < 2e-3: pr.hide(p)
        else: pr.set(p, c, I3, r)
    pr.commit()


def build_fountain(kit, D, rng, per=110):
    pr = Parts('fs_fountain'); gm = M.mat_glow(kit, D, 'fs_fount', (1.0, 0.62, 0.20), 2.6); gm2 = M.mat_glow(kit, D, 'fs_fount2', (1.0, 0.88, 0.40), 3.0)
    items = []
    for j in range(9):
        for i in range(per):
            r = rng.uniform(0.034, 0.060) * (0.8 + 0.3 * W.STRENGTH[j])
            p = pr.add(*sphere((0, 0, 0), (1, 1, 1), 0), m=i % 2)
            ang = rng.uniform(0, 2 * math.pi); sp = rng.uniform(0.05, 0.50)
            items.append((j, i, p, r, rng.uniform(1.8, 3.0), sp * math.cos(ang), sp * math.sin(ang) * 0.7 + 0.08, rng.uniform(0, 1)))
    pr.build(kit.bpy, [gm, gm2], kit.coll, smooth=False); pr.ob.visible_shadow = False
    return {'parts': pr, 'items': items, 'per': per}


def fountain_pose(Fo, t):
    pr = Fo['parts']; lf = W.lift(t); g = 6.0
    for j, i, p, r, vz, vx, vy, u in Fo['items']:
        e = W.ERUPT[j]; S = W.STRENGTH[j]; dur = 1.1 + 1.0 * S
        tl = e + 0.05 + u * dur
        a = t - tl
        if a < 0 or a > 3.0: pr.hide(p); continue
        v = vz * (0.55 + 0.45 * S); x = W.XC + vx * a * (0.6 + 0.4 * S) + 0.02 * math.sin(i); y = W.YC + 0.03 + vy * a * 0.6
        z0 = W.crater_floor(tl) + 0.02; z = z0 + v * a - 0.5 * g * a * a
        gnd = gh(x, y, t) + 0.01
        if z < gnd: pr.hide(p); continue
        pr.set(p, (x, y, z + lf), I3, r * (1 - 0.35 * W.sm(0.6, 1.0, a / (2 * v / g))))
    pr.commit()


# ============================================================================== the bottle (the visual explanation) and the sandcastle
BOTTLE = (0.80, -0.72)
CASTLE = (0.56, -0.50)
BK = 1.5       # storybook scale


def build_bottle(kit, D, rng):
    pr = Parts('fs_bottle')
    mats = [M.paint(kit, D, 'sz_soda', (0.97, 0.50, 0.18), noise=0.0), M.paint(kit, D, 'sz_label', (0.99, 0.96, 0.88), noise=0.0), M.paint(kit, D, 'sz_cap', (0.86, 0.18, 0.22), noise=0.0),
            M.paint(kit, D, 'sz_foam', (1.0, 0.98, 0.94), noise=0.0), M.paint(kit, D, 'sz_sand', (0.93, 0.80, 0.54)), M.paint(kit, D, 'sz_sandd', (0.84, 0.68, 0.42)),
            M.paint(kit, D, 'sz_flag', (0.95, 0.30, 0.30), noise=0.0), M.paint(kit, D, 'sz_bucket', (0.20, 0.55, 0.92), noise=0.0), M.paint(kit, D, 'sz_spade', (1.0, 0.82, 0.20), noise=0.0)]
    b = {}
    prof = [(0.0, 0.040), (0.02, 0.048), (0.12, 0.052), (0.17, 0.050), (0.20, 0.040), (0.23, 0.024), (0.26, 0.019), (0.285, 0.018)]
    V, F = tube([(0, 0, z) for z, _ in prof], [r for _, r in prof], 14, True); b['body'] = pr.add(V, F, 0)
    V, F = tube([(0, 0, 0.05), (0, 0, 0.13)], [0.0535, 0.0535], 14, True); b['label'] = pr.add(V, F, 1)
    V, F = tube([(0, 0, 0.285), (0, 0, 0.305)], [0.021, 0.021], 12, True); b['cap'] = pr.add(V, F, 2)
    b['foam'] = [pr.add(*sphere((0, 0, 0), (1, 1, 1), 1), 3) for _ in range(34)]
    b['fizz'] = [pr.add(*sphere((0, 0, 0), (1, 1, 1), 0), 3) for _ in range(18)]
    # the sandcastle: a keep and two towers with cone roofs, a red flag, a blue bucket and a yellow spade
    b['castle'] = []
    def tower(cx, cy, r, h, roof):
        V, F = tube([(cx, cy, 0.0), (cx, cy, h)], [r, r * 0.92], 12, True); b['castle'].append(pr.add(V, F, 4))
        V, F = cone((cx, cy, h), r * 1.12, roof, 12, 0.0); b['castle'].append(pr.add(V, F, 5))
    V, F = box((0, 0, 0.035), (0.20, 0.13, 0.07)); b['castle'].append(pr.add(V, F, 4))
    tower(0.0, 0.0, 0.034, 0.145, 0.05); tower(-0.085, -0.05, 0.022, 0.100, 0.035); tower(0.085, -0.05, 0.022, 0.100, 0.035)
    b['flag'] = pr.add([(0, 0, 0.22), (0.05, 0, 0.235), (0, 0, 0.25)], [(0, 1, 2), (0, 2, 1)], 6)
    V, F = tube([(0, 0, 0.195), (0, 0, 0.255)], [0.003, 0.003], 5, True); b['pole'] = pr.add(V, F, 5)
    V, F = tube([(0, 0, 0.0), (0, 0, 0.07)], [0.040, 0.055], 14, True); b['bucket'] = pr.add(V, F, 7)
    V, F = tube([(0, 0, 0.0), (0, 0, 0.09)], [0.006, 0.006], 6, True); b['handle'] = pr.add(V, F, 8)
    V, F = box((0, 0, 0.0), (0.05, 0.004, 0.06)); b['blade'] = pr.add(V, F, 8)
    pr.build(kit.bpy, mats, kit.coll)
    return {'parts': pr, 'b': b, 'rng': np.random.default_rng(3), 'foam_v': [(rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), rng.uniform(1.5, 2.8), rng.uniform(0.019, 0.034), rng.uniform(0, 1)) for _ in range(34)]}


def bottle_pose(Bt, t):
    B = W.B; pr = Bt['parts']; b = Bt['b']; lf = W.lift(t); g = 7.0
    bx, by = BOTTLE; gz = gh(bx, by, t) + lf
    sh = W.sm(B.bottle0, B.e0, t)                              # the shaking grows until it pops
    wob = BK and (0.05 + 0.20 * sh) * math.sin(2 * math.pi * (3.0 + 6.0 * sh) * t) * (1 if t < B.e0 + 0.15 else math.exp(-(t - B.e0 - 0.15) * 3))
    R = rx(0.6 * wob) @ ry(0.8 * wob)
    for k in ('body', 'label'): pr.set(b[k], (bx, by, gz), R, BK)
    # the cap: strains, then pops off at the eruption and lands on top of the sandcastle's keep
    cx, cy = CASTLE; gzc = gh(cx, cy, t) + lf
    land = np.array([cx, cy, gzc + 0.150 * BK + 0.012])
    n0 = np.array([bx, by, gz + 0.305 * BK]); tau = 1.15; a = t - B.e0
    if a < 0: pr.set(b['cap'], n0 + R @ np.array([0, 0, 0.01 * sh * BK]), R, BK)
    elif a < tau:
        p = n0 + (land - n0) * (a / tau); p[2] = n0[2] + (land[2] - n0[2]) * (a / tau) + 0.55 * math.sin(math.pi * a / tau)
        pr.set(b['cap'], p, rx(7.0 * a) @ ry(4.0 * a), BK)
    else: pr.set(b['cap'], land, rz(0.5), BK)
    # foam jets up at the pop, then a foam cap on the neck that settles
    for i, (j, (vx, vy, vz, r, u)) in enumerate(zip(b['foam'], Bt['foam_v'])):
        a2 = t - B.e0 - 0.05 - 0.5 * u
        if a2 < 0 or a2 > 2.6:
            if a2 >= 2.6 and i < 6: pr.set(j, (bx + 0.012 * (i - 3) * BK, by + 0.01 * ((i % 2) * 2 - 1) * BK, gz + (0.29 - 0.05 * W.sm(2.6, 6.0, a2)) * BK), I3, 0.020 * BK * (1 - 0.3 * W.sm(2.6, 7.0, a2)))
            else: pr.hide(j)
            continue
        z = gz + 0.30 * BK + vz * a2 - 0.5 * g * a2 * a2
        if z < gz + 0.02: pr.hide(j); continue
        pr.set(j, (bx + vx * a2 * 0.5, by + vy * a2 * 0.5, z), I3, r * BK)
    # tiny fizz bubbles rise from the neck while it is shaken
    for i, j in enumerate(b['fizz']):
        if sh < 0.05 or t > B.e0: pr.hide(j); continue
        T = 1.1; age = ((t * 1.0 / T + i / 18.0) % 1.0)
        pr.set(j, (bx + 0.03 * math.sin(7 * i + 3 * t) * BK, by + 0.01 * math.cos(5 * i), gz + (0.31 + 0.22 * age) * BK), I3, 0.011 * BK * sh * (1 - age))
    # the sandcastle with its flag fluttering, the bucket and spade beside it
    for j in b['castle']: pr.set(j, (cx, cy, gzc - 0.004), I3, BK)
    pr.set(b['pole'], (cx, cy, gzc - 0.004), I3, BK)
    pr.set(b['flag'], (cx, cy, gzc - 0.004), rz(0.35 * math.sin(2 * math.pi * 1.1 * t)), BK)
    bxp, byp = cx - 0.20, cy - 0.06; gzb = gh(bxp, byp, t) + lf
    pr.set(b['bucket'], (bxp, byp, gzb), rx(math.pi) @ I3 if False else I3, BK * 0.9)
    sx_, sy_ = cx + 0.14, cy - 0.16; gzs = gh(sx_, sy_, t) + lf
    pr.set(b['handle'], (sx_, sy_, gzs + 0.02), rx(0.35), BK); pr.set(b['blade'], (sx_, sy_, gzs + 0.005), rz(0.3), BK * 0.7)
    pr.commit()
    return np.array([bx, by, gz + 0.2 * BK])
