"""What is a shooting star? The sky: the night card with the Moon, the stars, the streaks, the magnifier window (bpy + numpy).

Every pose is a pure function of t. The sky is the stage; everything here is flat painted light in the camera's own space
(like the words), in the crisp 'type' layer of the Fable look so it stays sharp over the brushwork. Screen units: x runs
-1.8 to 1.8 and y -1.01 to 1.01 at the 5 m the words sit at. The sky region is y above about 0.28 (the hills' crest).
  Sky      the night card (far behind): sunset to night gradient, the setting sun, the rising Moon with painted halos, a faint
           milky way and far stars; and the near stars (twinkling four-point stars that come out one by one at dusk)
  Streak   a ribbon of gold light with a hot head, a soft halo and shed sparks: the first small zip, the long meteor on the
           music's brightest phrase, the last tiny one in the final bars
  Window   the round magnifier window (gold frame, handle, a small ring on the sky and two gold lines): a star (a giant ball of
           fire, very far away), then dark space with a small rock tumbling, then the soft layers of the air through which the
           rock rushes and glows orange, yellow, white until it burns up high above the clouds
"""
import math
import zlib

import numpy as np

import cutaway as cw
from cutaway import G, srgb
import szworld as W
import szmats as M
import szui as UI
from szgeo import Parts, I3, rz

DL = 5.0                      # the picture layer: 5 m in front of the camera (as the words)
STAR_POS = (0.30, 0.36)       # the bright star the window shows
PATH = ((0.46, 1.10), (-0.30, 0.96), (-1.62, 0.30))      # the long streak: quadratic Bezier, screen units
WIN_C = (1.10, 0.50)          # the window's centre
gz = lambda x, y, t: float(W.top_h(np.array([x]), np.array([y]), t)[0])


def bez(P, u):
    u = np.asarray(u, float)[..., None]; P0, P1, P2 = (np.array(p) for p in P)
    return (1 - u) ** 2 * P0 + 2 * u * (1 - u) * P1 + u * u * P2


# ============================================================================== tiny crisp-mesh kit
def cmat(kit, D, name, colour, alpha, amul=None):
    """Emission whose colour is a node chain (never a plain default: Fable's word recolour must not reach it), alpha driven
    by the Drive value `alpha`, optionally times amul(g) (an attribute shape)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    c = colour(g)
    if isinstance(c, (tuple, list)): n = g.node('ShaderNodeRGB'); n.outputs[0].default_value = srgb(tuple(c)); c = n.outputs[0]
    e = g.node('ShaderNodeEmission', ins={'Color': c, 'Strength': 1.0})
    a = D.val(g, alpha, 1.0)
    if amul is not None: a = g.math('MULTIPLY', a, amul(g))
    M._alpha_out(g, e, a); return m


def _e(g): return g.attr('e').outputs['Fac']
def _sh(g): return g.attr('sh').outputs['Fac']


class Flat:
    """Flat pieces in one mesh (z per piece, a material slot each), point attributes e and sh."""
    def __init__(self): self.V = []; self.F = []; self.M = []; self.E = []; self.S = []
    def fan(self, c, ring, mat, z, e0=1.0, e1=0.0, s0=1.0, s1=0.4):
        o = len(self.V); self.V.append((c[0], c[1], z)); self.E.append(e0); self.S.append(s0)
        for p in ring: self.V.append((p[0], p[1], z)); self.E.append(e1); self.S.append(s1)
        n = len(ring); self.F += [(o, o + 1 + k, o + 1 + (k + 1) % n) for k in range(n)]; self.M += [mat] * n
    def circle(self, c, r, mat, z, n=40, **kw):
        self.fan(c, [(c[0] + r * math.cos(a), c[1] + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)], mat, z, **kw)
    def poly(self, pts, mat, z, e=1.0, sh=0.6):
        o = len(self.V)
        for p in pts: self.V.append((p[0], p[1], z)); self.E.append(e); self.S.append(sh)
        for k in range(1, len(pts) - 1): self.F.append((o, o + k, o + k + 1)); self.M.append(mat)
    def star(self, c, L, mat, z, k=0.24, rot=0.0, e1=0.0):
        pts = []
        for q in range(8):
            r = L if q % 2 == 0 else L * k; a = math.pi * q / 4 + rot; pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
        self.fan(c, pts, mat, z, 1.0, e1, 1.0, 0.5)
    def build(self, bpy, name, mats, coll):
        return cw.mk_mesh(bpy, name, self.V, self.F, mats, self.M, False, coll, {'e': ('FLOAT', self.E), 'sh': ('FLOAT', self.S)})


def piece_mesh(kind, **kw):
    """(V, F, E, S) of one movable piece in its own frame: 'star' (four-point), 'halo' (soft disc), 'disc'."""
    fl = Flat()
    if kind == 'star': fl.star((0, 0), 1.0, 0, 0.0, kw.get('k', 0.24))
    elif kind == 'halo': fl.circle((0, 0), 1.0, 0, 0.0, n=kw.get('n', 28), e0=1.0, e1=0.0)
    elif kind == 'disc': fl.circle((0, 0), 1.0, 0, 0.0, n=kw.get('n', 28), e0=1.0, e1=1.0, s0=1.0, s1=0.3)
    return np.array(fl.V), fl.F, fl.E, fl.S


class Pieces:
    """Many small movable flat pieces (stars, halos, sparks) in one crisp mesh, parked at scale 0 when unused."""
    def __init__(self, kit, D, cam, name, mats, z):
        self.kit = kit; self.cam = cam; self.name = name; self.pr = Parts(name); self.E = []; self.S = []; self.mats = mats; self.z = z; self.ob = None
    def add(self, kind, m, **kw):
        V, F, E, S = piece_mesh(kind, **kw); self.E += E; self.S += S; return self.pr.add(V, F, m)
    def add_custom(self, V, F, E, S, m):
        self.E += list(E); self.S += list(S); return self.pr.add(np.array(V), F, m)
    def build(self):
        ob = self.pr.build(self.kit.bpy, self.mats, self.kit.coll, smooth=False, attrs={'e': ('FLOAT', self.E), 'sh': ('FLOAT', self.S)})
        ob.parent = self.cam.ob; ob.matrix_parent_inverse.identity(); ob.location = (0, 0, -DL + self.z)
        for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
        self.ob = ob; return ob
    def set(self, k, x, y, s=1.0, rot=0.0, sy=None):
        self.pr.set(k, (x, y, 0.0), rz(rot), (s, s if sy is None else sy, s))
    def hide(self, k): self.pr.hide(k)
    def commit(self): self.pr.commit()


def own(kit, cam, ob, z):
    ob.parent = cam.ob; ob.matrix_parent_inverse.identity(); ob.location = (0, 0, -DL + z)
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
    return ob


# ============================================================================== the sky
class Sky:
    """The night card, the Moon, and the near stars."""
    def __init__(self, kit, D, cam, ctx, rng):
        bpy = kit.bpy; self.D = D; self.cam = cam; self.crisp = []
        cd = cam.ob.data; self.hw = DL * 18.0 / cd.lens; self.hh = self.hw * 9 / 16
        # ---- the card, far behind everything
        Dd = 60.0; sw = 18.0 / cd.lens * Dd; hw, hh = sw * 1.25, sw * 9 / 16 * 1.25
        m = cw._new_mat(bpy, 'fs_nightsky'); g = G(m.node_tree, kit)
        tc = g.node('ShaderNodeTexCoord'); sx = g.sep(tc.outputs['Object'])
        u = g.math('DIVIDE', sx[0], sw); v = g.math('DIVIDE', sx[1], sw * 9 / 16); asp = 16 / 9
        gg = g.math('MULTIPLY', g.math('ADD', v, 0.15), 1 / 1.15, clamp=True)
        col = g.mix(g.math('POWER', g.math('MULTIPLY', gg, 2.2, clamp=True), 0.9), D.rgb(g, 'sky_low', (0.9, 0.5, 0.4)), D.rgb(g, 'sky_mid', (0.4, 0.3, 0.5)))
        col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', gg, 0.35), 1.7, clamp=True), col, D.rgb(g, 'sky_top', (0.1, 0.1, 0.3)))
        st = g.noise(g.comb(g.math('MULTIPLY', u, 2.0), g.math('MULTIPLY', v, 26.0), 0.0), 2.5, 4.0, 0.6)
        col = g.mix(g.math('MULTIPLY', g.math('SUBTRACT', st.outputs['Fac'], 0.5), 0.14), col, srgb((0.8, 0.8, 1.0)), 'OVERLAY')
        # the sunset glow low on the horizon (driven amount), warm
        gl = g.math('MULTIPLY', g.math('EXPONENT', g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', v, 0.12), g.math('SUBTRACT', v, 0.12)), -9.0)), D.val(g, 'glow', 1.0))
        col = g.mix(g.math('MULTIPLY', gl, 0.75, clamp=True), col, D.rgb(g, 'glow_c', (1.0, 0.7, 0.4)), 'SCREEN')
        # the setting sun: a soft disc with painted halo rings (it sinks behind the hills)
        def disc(un, vn, r0, colname, alpha, ringk, ringsteps=4):
            du = g.math('MULTIPLY', g.math('SUBTRACT', u, D.val(g, un, 0.0)), asp); dv = g.math('SUBTRACT', v, D.val(g, vn, 0.0))
            r = g.math('SQRT', g.math('ADD', g.math('MULTIPLY', du, du), g.math('MULTIPLY', dv, dv)))
            halo = g.math('EXPONENT', g.math('MULTIPLY', g.math('MAXIMUM', g.math('SUBTRACT', r, r0), 0.0), -9.0))
            rings = g.math('DIVIDE', g.math('FLOOR', g.math('MULTIPLY', halo, ringsteps)), ringsteps)
            return r, rings
        r, rings = disc('sun_u', 'sun_v', 0.085, 'sun', 'sun_a', 0.4)
        sunc = D.rgb(g, 'sun_c', (1.0, 0.85, 0.55))
        col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', rings, 0.45), D.val(g, 'sun_a', 1.0)), col, sunc, 'SCREEN')
        col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', 0.085, r), 260.0, clamp=True), D.val(g, 'sun_a', 1.0)), col, sunc)
        # the Moon: cream disc, soft darker seas, painted halo rings
        r, rings = disc('moon_u', 'moon_v', 0.075, 'moon', 'moon_a', 0.4, 5)
        mc = D.rgb(g, 'moon_c', (0.97, 0.95, 0.84))
        col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', rings, 0.30), D.val(g, 'moon_a', 1.0)), col, srgb((0.62, 0.70, 0.95)), 'SCREEN')
        sea = g.noise(g.comb(g.math('MULTIPLY', u, 14.0), g.math('MULTIPLY', v, 14.0), 2.0), 1.0, 3.0, 0.5)
        mooncol = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', sea.outputs['Fac'], 0.46), 3.0, clamp=True), 0.28), mc, srgb((0.78, 0.76, 0.70)))
        col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', g.math('SUBTRACT', 0.075, r), 300.0, clamp=True), D.val(g, 'moon_a', 1.0)), col, mooncol)
        # a faint milky way and far stars (night only)
        dd = g.math('SUBTRACT', g.math('ADD', g.math('MULTIPLY', u, 0.55), g.math('MULTIPLY', v, -0.9)), 0.15)
        band = g.math('EXPONENT', g.math('MULTIPLY', g.math('MULTIPLY', dd, dd), -6.0))
        mw = g.noise(g.comb(g.math('MULTIPLY', u, 5.0), g.math('MULTIPLY', v, 5.0), 1.0), 2.0, 4.0, 0.6)
        col = g.mix(g.math('MULTIPLY', g.math('MULTIPLY', band, g.math('MULTIPLY', g.math('SUBTRACT', mw.outputs['Fac'], 0.30), 1.0, clamp=True)), g.math('MULTIPLY', D.val(g, 'night', 0.0), 0.34)), col, srgb((0.62, 0.66, 0.95)), 'SCREEN')
        vo = g.voronoi(g.comb(g.math('MULTIPLY', u, 46.0), g.math('MULTIPLY', v, 26.0), 0.0), 1.0, 'F1', '2D')
        dots = g.math('MULTIPLY', g.math('SUBTRACT', 0.050, vo.outputs['Distance'], clamp=True), 18.0)
        dots = g.math('MULTIPLY', dots, g.math('MULTIPLY', D.val(g, 'night', 0.0), g.math('MULTIPLY', g.math('SUBTRACT', v, 0.18), 4.0, clamp=True)))
        col = g.mix(g.math('MULTIPLY', g.math('MINIMUM', dots, 1.0), 0.45), col, srgb((0.95, 0.95, 1.0)), 'SCREEN')
        cw._finish(g, g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}))
        V = [(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)]
        self.card = cw.mk_mesh(bpy, 'fs_nightcard', V, [(0, 1, 2, 3)], [m], None, False, kit.coll)
        self.card.parent = cam.ob; self.card.matrix_parent_inverse.identity(); self.card.location = (0, 0, -Dd)
        for a in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_shadow', 'visible_volume_scatter'): setattr(self.card, a, False)
        # ---- the near stars: four-point twinkles, each comes out at its own moment of the dusk
        mats = [cmat(kit, D, 'fs_star', lambda g: g.mix(_sh(g), srgb((0.80, 0.86, 1.0)), srgb((1.0, 0.98, 0.88))), 'a_stars', lambda g: g.math('MAXIMUM', g.math('MULTIPLY', _e(g), 0.0), 1.0)),
                cmat(kit, D, 'fs_starglow', lambda g: srgb((0.86, 0.90, 1.0)), 'a_stars', lambda g: g.math('MULTIPLY', g.math('POWER', _e(g), 2.2), 0.55))]
        self.st = Pieces(kit, D, cam, 'fs_stars', mats, 0.0)
        self.stars = []
        n = 78
        for k in range(n):
            x = rng.uniform(-1.74, 1.74); y = rng.uniform(0.30, 0.99)
            if k < 6: x, y = [(-1.35, 0.42), (-0.55, 0.30), (-1.62, 0.78), (0.7, 0.92), (-0.1, 0.46), (1.6, 0.55)][k]
            big = k < 12
            L = rng.uniform(0.032, 0.05) if big else rng.uniform(0.010, 0.024)
            t_on = rng.uniform(1.5, 14.0) if k > 0 else 2.6
            if k < 6: t_on = 1.2 + 1.9 * k
            self.stars.append((self.st.add('star', 0, k=0.2 if big else 0.28), self.st.add('halo', 1), x, y, L, t_on, rng.uniform(0, 6.28), rng.uniform(0.35, 0.9)))
        # the bright star the window shows
        self.hero = (self.st.add('star', 0, k=0.16), self.st.add('halo', 1))
        self.st.build(); self.crisp.append(self.st.ob)

    def pose(self, t, W_, hero_pulse):
        D = self.D; night = W.night(t); D.set('night', night)
        w = W.weights(t); P = {
            'sky_top': ((0.20, 0.26, 0.54), (0.11, 0.14, 0.38), (0.03, 0.06, 0.20), (0.02, 0.04, 0.15)),
            'sky_mid': ((0.62, 0.40, 0.58), (0.28, 0.24, 0.50), (0.06, 0.12, 0.32), (0.04, 0.09, 0.26)),
            'sky_low': ((1.00, 0.62, 0.36), (0.62, 0.38, 0.52), (0.12, 0.22, 0.46), (0.08, 0.16, 0.40)),
            'glow_c': ((1.0, 0.62, 0.30), (0.80, 0.42, 0.50), (0.16, 0.26, 0.52), (0.10, 0.18, 0.44)),
            'sun_c': ((1.0, 0.84, 0.52), (1.0, 0.62, 0.44), (0.6, 0.5, 0.6), (0.4, 0.4, 0.6)),
            'moon_c': ((0.99, 0.90, 0.72), (0.98, 0.93, 0.80), (0.98, 0.96, 0.86), (0.98, 0.96, 0.88))}
        for k, cols in P.items(): D.setc(k, tuple(sum(wi * c[j] for wi, c in zip(w, cols)) for j in range(3)))
        D.set('glow', 1.0 - 0.8 * W.sm(6.0, 16.0, t))
        # the sun sinks behind the hills in the first seconds; the Moon rises on the left and climbs slowly
        su = 0.46; sv = W.keys(t, [(0.0, 0.20), (7.5, -0.06)]); D.set('sun_u', su); D.set('sun_v', sv); D.set('sun_a', 1.0 - W.sm(6.0, 8.0, t))
        D.set('moon_u', -0.62); D.set('moon_v', W.keys(t, [(0.0, 0.06), (4.0, 0.06), (24.0, 0.44), (68.4, 0.54)])); D.set('moon_a', W.sm(2.0, 6.0, t))
        # the near stars
        D.set('a_stars', 1.0)
        for a, h, x, y, L, t_on, ph, rate in self.stars:
            k = W.sm(t_on, t_on + 0.7, t)
            if k < 1e-3: self.st.hide(a); self.st.hide(h); continue
            pop = k * (1 + 0.25 * math.sin(math.pi * min(1.0, (t - t_on) / 0.7)))
            tw = 0.82 + 0.22 * math.sin(2 * math.pi * rate * t + ph)
            self.st.set(a, x, y, L * pop * tw, 0.15 * math.sin(0.3 * t + ph)); self.st.set(h, x, y, L * 2.6 * pop * tw)
        a, h = self.hero; k = W.sm(3.0, 3.8, t) * (1 + 0.25 * hero_pulse); tw = 0.9 + 0.1 * math.sin(2.2 * t)
        self.st.set(a, *STAR_POS, 0.07 * k * tw * (1 + 0.6 * hero_pulse), 0.1 * math.sin(0.5 * t)); self.st.set(h, *STAR_POS, 0.22 * k * (1 + 0.5 * hero_pulse))
        self.st.commit()


# ============================================================================== the streaks
class Streak:
    """A ribbon of light along a quadratic path, a hot head with a soft halo and a glint, sparks it sheds. The head moves from
    t0 for `dur` seconds; the tail follows `lag` seconds behind and catches up, so the trail grows, then melts into the head."""
    N = 40

    def __init__(self, kit, D, cam, name, path, t0, dur, lag, width, heat=1.0, K=20, peak=None, life=1.1):
        bpy = kit.bpy; self.D = D; self.path = path; self.t0 = t0; self.dur = dur; self.lag = lag; self.w = width; self.heat = heat; self.K = K
        self.peak = peak; self.life = life; self.name = name; self.an = 'a_' + name; self.crisp = []
        n = self.N; V = [(0, 0, 0)] * (2 * (n + 1)); F = []; E = []
        for i in range(n + 1): E += [i / n, i / n]
        for i in range(n): F.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
        def col(g): return g.ramp(_e(g), [(0.0, (1.0, 0.45, 0.16)), (0.5, (1.0, 0.78, 0.34)), (0.85, (1.0, 0.95, 0.74)), (1.0, (1.0, 1.0, 0.96))])
        mats = [cmat(kit, D, f'fs_{name}_rib', col, self.an, lambda g: g.math('POWER', g.math('MAXIMUM', _e(g), 0.0), 1.3))]
        self.rib = own(kit, cam, cw.mk_mesh(bpy, f'fs_{name}_ribbon', V, F, mats, None, False, kit.coll, {'e': ('FLOAT', E)}), 0.0045)
        hm = [cmat(kit, D, f'fs_{name}_halo', lambda g: srgb((1.0, 0.82, 0.46)), self.an, lambda g: g.math('MULTIPLY', g.math('POWER', _e(g), 2.0), 0.9)),
              cmat(kit, D, f'fs_{name}_core', lambda g: srgb((1.0, 0.99, 0.92)), self.an, lambda g: g.math('MULTIPLY', g.math('POWER', _e(g), 1.2), 1.0)),
              cmat(kit, D, f'fs_{name}_spark', lambda g: g.mix(_sh(g), srgb((1.0, 0.62, 0.22)), srgb((1.0, 0.97, 0.80))), self.an, lambda g: g.math('ADD', g.math('MULTIPLY', _e(g), 0.0), 1.0))]
        self.pc = Pieces(kit, D, cam, f'fs_{name}_pcs', hm, 0.0050)
        self.halo = self.pc.add('halo', 0, n=32); self.core = self.pc.add('halo', 1, n=24); self.glint = self.pc.add('star', 1, k=0.12)
        self.sp = [(self.pc.add('star', 2, k=0.3), np.random.default_rng(zlib.crc32(name.encode()) % 997 + k).uniform(-1, 1, 3)) for k in range(K)]
        self.pc.build(); self.crisp = [self.rib, self.pc.ob]
        self.rib.hide_render = True

    def head_u(self, t): return float(np.clip((t - self.t0) / self.dur, 0, 1))
    def tail_u(self, t): return float(np.clip((t - self.t0 - self.lag) / self.dur, 0, 1))

    def pose(self, t):
        D = self.D; t1 = self.t0 + self.dur + self.lag
        a = W.sm(self.t0 - 0.02, self.t0 + 0.08, t) * (1 - W.sm(t1 - 0.5, t1, t))
        D.set(self.an, a)
        uh, ut = self.head_u(t), self.tail_u(t)
        on = a > 0.01 and uh > 0 and ut < uh
        self.rib.hide_render = not on
        if not on:
            self.pc.hide(self.halo); self.pc.hide(self.core); self.pc.hide(self.glint)
            for k, _ in self.sp: self.pc.hide(k)
            self.pc.commit(); return
        n = self.N; us = ut + (uh - ut) * np.arange(n + 1) / n; pts = bez(self.path, us)
        tg = np.gradient(pts, axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None] + 1e-9; nr = np.column_stack([-tg[:, 1], tg[:, 0]])
        flare = W.win(t, self.peak - 0.15, self.peak + 0.9, 0.4) if self.peak else 0.0
        wd = self.w * (1.0 + 0.8 * flare) * (np.arange(n + 1) / n) ** 0.8
        co = np.zeros((2 * (n + 1), 3), np.float32)
        co[0::2, :2] = pts + nr * wd[:, None]; co[1::2, :2] = pts - nr * wd[:, None]
        me = self.rib.data; me.vertices.foreach_set('co', co.ravel()); me.update()
        h = bez(self.path, uh); rr = self.w * 3.2 * self.heat * (1 + 1.6 * flare)
        self.pc.set(self.halo, h[0], h[1], rr * 2.4); self.pc.set(self.core, h[0], h[1], rr * 0.8)
        self.pc.set(self.glint, h[0], h[1], rr * (1.3 + 1.2 * flare), 0.6 * t)
        for k, (j, r3) in enumerate(self.sp):
            ts = self.t0 + self.dur * (0.04 + 0.9 * k / self.K) + 0.05 * r3[2]; age = t - ts
            if age < 0 or age > self.life * (1 + 0.5 * flare): self.pc.hide(j); continue
            p = bez(self.path, np.clip((ts - self.t0) / self.dur, 0, 1)); f = age / self.life
            x = p[0] + r3[0] * 0.07 * age; y = p[1] + r3[1] * 0.04 * age - 0.06 * age * age
            self.pc.set(j, x, y, self.w * (1.1 + r3[2]) * 1.9 * (1 - f) * self.heat, 3.0 * age)
        self.pc.commit()


# ============================================================================== the magnifier window
class Window:
    """The round magnifier window (gold frame, handle, small ring on the sky, two gold lines): one window, three views
    that cross-fade: a star (a giant glowing ball, far away), dark space with a small rock tumbling, the layers of the air with
    the rock rushing down through them, glowing orange, yellow, white, and burning up high above the clouds."""

    def __init__(self, kit, D, cam, rng):
        bpy = kit.bpy; self.kit = kit; self.D = D; self.cam = cam; self.obs = []
        cd = cam.ob.data; self.hh = DL * 18.0 / cd.lens * 9 / 16; self.R = 0.40; Rl = self.R; self.C = WIN_C
        def obz(ob, z): return own(kit, cam, ob, z)
        # ---- the background disc: dark space, or the layers of the air (soft bands), static stars in the dark
        m = cw._new_mat(bpy, 'fs_winbg'); g = G(m.node_tree, kit)
        P = g.node('ShaderNodeTexCoord').outputs['Object']; sx = g.sep(P); y = g.math('DIVIDE', sx[1], 1.0); x = g.math('DIVIDE', sx[0], 1.0)
        space = g.mix(g.math('MULTIPLY', g.math('ADD', y, 1.0), 0.5, clamp=True), srgb((0.06, 0.08, 0.22)), srgb((0.02, 0.03, 0.10)))
        yy = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ADD', y, 1.0), 0.5, clamp=True))
        # thin dark top layer, then four layers, each lighter and bluer, soft edges between (the air gets thicker lower down)
        stops = [(0.00, (0.03, 0.05, 0.17)), (0.17, (0.03, 0.05, 0.17)), (0.20, (0.07, 0.13, 0.38)), (0.40, (0.07, 0.13, 0.38)), (0.43, (0.16, 0.30, 0.60)),
                 (0.58, (0.16, 0.30, 0.60)), (0.61, (0.36, 0.54, 0.80)), (0.74, (0.36, 0.54, 0.80)), (0.77, (0.62, 0.78, 0.92)), (1.00, (0.78, 0.88, 0.97))]
        air = g.ramp(yy, stops)
        col = g.mix(D.val(g, 'wair', 0.0), space, air)
        vo = g.voronoi(g.comb(g.math('MULTIPLY', x, 11.0), g.math('MULTIPLY', y, 11.0), 0.0), 1.0, 'F1', '2D')
        dots = g.math('MULTIPLY', g.math('SUBTRACT', 0.075, vo.outputs['Distance'], clamp=True), 14.0)
        dots = g.math('MULTIPLY', dots, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', D.val(g, 'wair', 0.0), g.math('MULTIPLY', g.math('SUBTRACT', 0.85, y, clamp=True), 1.2, clamp=True))))
        col = g.mix(g.math('MINIMUM', dots, 0.8), col, srgb((0.95, 0.95, 1.0)))
        r = g.vmath('LENGTH', g.comb(sx[0], sx[1], 0.0)); vig = g.math('MULTIPLY', g.math('SUBTRACT', r, 0.72), 1.0 / 0.28, clamp=True)
        col = g.mix(g.math('MULTIPLY', vig, 0.30), col, srgb((0.02, 0.03, 0.08)))
        e = g.node('ShaderNodeEmission', ins={'Color': col, 'Strength': 1.0}); M._alpha_out(g, e, D.val(g, 'a_win', 0.0))
        fl = Flat(); fl.circle((0, 0), 1.0, 0, 0.0, n=72, e0=1.0, e1=1.0)
        self.bg = obz(fl.build(bpy, 'fs_winbg', [m], kit.coll), 0.0)
        # ---- everything that moves inside: pieces in window units (R = 1); one mesh object, scaled with the pop
        mats = [cmat(kit, D, 'fs_w_fire', lambda g: g.mix(_sh(g), srgb((1.0, 0.50, 0.14)), srgb((1.0, 0.86, 0.40))), 'a_wstar', lambda g: g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', _e(g), 0.0)), 1.0)),        # 0 star body
                cmat(kit, D, 'fs_w_starglow', lambda g: srgb((1.0, 0.62, 0.24)), 'a_wstar', lambda g: g.math('MULTIPLY', g.math('POWER', _e(g), 1.8), 0.85)),        # 1 star glow
                cmat(kit, D, 'fs_w_ray', lambda g: srgb((1.0, 0.82, 0.38)), 'a_wstar', lambda g: g.math('MULTIPLY', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', _e(g), 0.0)), 0.8)),   # 2 corona
                cmat(kit, D, 'fs_w_rock', lambda g: g.mix(_sh(g), srgb((0.30, 0.22, 0.20)), srgb((0.74, 0.58, 0.46))), 'a_wrock', lambda g: g.math('ADD', g.math('MULTIPLY', _e(g), 0.0), 1.0)),  # 3 rock
                cmat(kit, D, 'fs_w_crater', lambda g: srgb((0.26, 0.18, 0.17)), 'a_wrock', lambda g: g.math('MULTIPLY', g.math('ADD', g.math('MULTIPLY', _e(g), 0.0), 1.0), 0.8)),   # 4 crater
                cmat(kit, D, 'fs_w_heat', lambda g: g.mix(D.val(g, 'heat', 0.0), srgb((1.0, 0.42, 0.12)), srgb((1.0, 0.97, 0.88))), 'a_wheat', lambda g: g.math('MULTIPLY', g.math('POWER', _e(g), 1.7), 0.8)),  # 5 heat glow
                cmat(kit, D, 'fs_w_flash', lambda g: srgb((1.0, 0.98, 0.9)), 'a_wflash', lambda g: g.math('MULTIPLY', g.math('POWER', _e(g), 1.5), 0.95)),    # 6 flash
                cmat(kit, D, 'fs_w_spark', lambda g: g.mix(_sh(g), srgb((1.0, 0.60, 0.22)), srgb((1.0, 0.97, 0.8))), 'a_wspark', lambda g: g.math('ADD', g.math('MULTIPLY', _e(g), 0.0), 1.0)),  # 7 spark
                cmat(kit, D, 'fs_w_cloud', lambda g: srgb((0.97, 0.98, 1.0)), 'a_wair', lambda g: g.math('MULTIPLY', g.math('POWER', _e(g), 0.55), 0.9)),    # 8 cloud puffs
                cmat(kit, D, 'fs_w_trail', lambda g: g.ramp(_e(g), [(0.0, (1.0, 0.36, 0.10)), (0.5, (1.0, 0.66, 0.24)), (1.0, (1.0, 0.95, 0.75))]), 'a_wheat', lambda g: g.math('POWER', g.math('MAXIMUM', _e(g), 0.0), 1.4))]   # 9 trail
        self.pc = Pieces(kit, D, cam, 'fs_winpieces', mats, 0.0020)
        pc = self.pc
        # the star: glow, body, corona (a ring of 16 long soft rays)
        self.s_glow = pc.add('halo', 1, n=36); self.s_body = pc.add('disc', 0, n=36)
        self.s_rays = [pc.add('star', 2, k=0.10) for _ in range(2)]
        # the rock: a lumpy polygon, craters (own pieces so they turn with it)
        a = np.linspace(0, 2 * math.pi, 14, endpoint=False); rr = 1 + 0.16 * rng.uniform(-1, 1, 14)
        pts = [(math.cos(q) * r, math.sin(q) * r * 0.86) for q, r in zip(a, rr)]
        fl2 = Flat(); fl2.fan((0.0, 0.0), pts, 3, 0.0, 1.0, 1.0, 1.0, 0.25)
        self.rock = pc.add_custom(fl2.V, fl2.F, fl2.E, fl2.S, 3)
        self.CR = ((-0.30, 0.18, 0.20), (0.28, -0.22, 0.17), (0.10, 0.34, 0.11), (-0.18, -0.30, 0.10))
        self.craters = [pc.add('disc', 4, n=12) for _ in self.CR]
        # heat: three glow discs, a flash, the trail ribbon is its own mesh below
        self.h_big = pc.add('halo', 5, n=32); self.h_mid = pc.add('halo', 5, n=32); self.h_core = pc.add('halo', 6, n=24)
        self.flash = pc.add('halo', 6, n=36)
        self.sparks = [(pc.add('star', 7, k=0.3), rng.uniform(-1, 1, 3)) for _ in range(26)]
        self.puffs = [(pc.add('halo', 8, n=24), rng.uniform(0, 1, 3)) for _ in range(7)]
        pc.build(); self.pcob = pc.ob
        # the trail behind the rock: a ribbon (rewritten each frame)
        n = 20; V = [(0, 0, 0)] * (2 * (n + 1)); F = []; E = []
        for i in range(n + 1): E += [i / n, i / n]
        for i in range(n): F.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
        self.trail = obz(cw.mk_mesh(bpy, 'fs_wintrail', V, F, [mats[9]], None, False, kit.coll, {'e': ('FLOAT', E)}), 0.0016); self.TN = n
        for ob in (self.bg, self.pcob, self.trail): self.obs.append(ob)
        self.pcob.location = (0, 0, -DL + 0.0020)
        self.rock_p = None
        self._build_frame(kit, D, lambda ob, z: obz(ob, z), Rl)
        self.crisp = [self.bg, self.pcob, self.trail] + self.crisp

    # the gold frame, handle, ring and lines: exactly the fossil film's (the coordinator's upgraded design)
    def _build_frame(self, kit, D, own, Rl):
        bpy = kit.bpy; self.crisp = []; al = 'a_lens'
        def mats3(tag): return [UI.mat_shadow(kit, D, f'fs_lf{tag}s', al, 0.40), UI.mat_gold(kit, D, f'fs_lf{tag}g', al),
                                UI.mat_flat(kit, D, f'fs_lf{tag}c', al, (1.0, 0.98, 0.90), taper=True),
                                UI.mat_gold(kit, D, f'fs_lf{tag}p', al, ((0.16, 0.07, 0.20), (0.36, 0.17, 0.36), (0.62, 0.38, 0.52)))]
        fl = UI.Flat(); rc = Rl + 0.014; Pc, Nc = UI.circle_loop(rc, 120); Pw, Nw = UI.circle_loop(Rl, 120)
        fl.band(Pc, Nc, [(0.085, 1.0, 0.0), (0.040, 0.55, 0.0), (-0.020, 0.0, 0.0)], 0, 0.0, at=(0.012, -0.034))
        fl.band(Pc, Nc, [(0.043, 0.0, 0.08), (0.032, 1.0, 0.08)], 1, 0.0006)
        fl.tube(Pc, Nc, 0.060, 1, 0.0012, grow=0.008)
        fl.band(Pw, Nw, [(0.0, 0.0, 0.10), (-0.009, 1.0, 0.10)], 1, 0.0006)
        fl.band(Pc, Nc, [(0.0045, 0.0, 0.55), (0.0, 0.5, 0.92), (-0.0045, 1.0, 0.55)], 1, 0.0020)
        for q in range(12):
            a = 2 * math.pi * q / 12 + 0.26; c = np.array([rc * math.cos(a), rc * math.sin(a)]); Ps, Ns = UI.circle_loop(0.0125, 14)
            fl.fan(Ps, Ns, 0.0, 0.5, 0.40, 1, 0.0026, at=tuple(c)); fl.band(Ps, Ns, [(0.0, 0.0, 0.20), (-0.0045, 1.0, 0.95)], 1, 0.0028, at=tuple(c))
        n = 18; ang = np.linspace(math.radians(112), math.radians(170), n); wd = 0.036 * np.sin(np.linspace(0, math.pi, n)) ** 0.8
        A = np.column_stack([(Rl * 0.84 + wd) * np.cos(ang), (Rl * 0.84 + wd) * np.sin(ang)]); Bq = np.column_stack([(Rl * 0.84 - wd) * np.cos(ang), (Rl * 0.84 - wd) * np.sin(ang)])
        fl.strip(A, Bq, 2, 0.0040, es=np.sin(np.linspace(0, math.pi, n)) * 0.62, ss=0.5)
        Pd, Nd = UI.circle_loop(0.022, 16); fl.fan(Pd, Nd, 0.0, 0.5, 0.5, 2, 0.0040, at=(-Rl * 0.70 * 0.86, Rl * 0.70 * 0.55 + 0.02))
        self.frame = own(fl.build(bpy, 'fs_lensframe', mats3('f'), kit.coll), 0.006)
        h = UI.Flat(); x0, x1, x2 = Rl + 0.00, Rl + 0.13, Rl + 0.27
        def bar(xa, xb, wa, wb, mat, z, rows=(0.45, 0.95, 0.30)):
            m = 8; xs = np.linspace(xa, xb, m); ws = np.linspace(wa, wb, m)
            top = np.column_stack([xs, ws]); mid = np.column_stack([xs, ws * 0.35]); bot = np.column_stack([xs, -ws])
            h.strip(top, mid, mat, z, es=0.0, ss=rows[0]); h.strip(mid, bot, mat, z, es=1.0, ss=rows[2])
        bar(x0, x0 + 0.075, 0.030, 0.036, 1, 0.0010)
        bar(x0 + 0.075, x2, 0.040, 0.046, 3, 0.0014)
        Pe, Ne = UI.circle_loop(0.046, 24); h.fan(Pe, Ne, 0.0, 0.5, 0.45, 3, 0.0014, at=(x2, 0.0))
        h.band(*UI.circle_loop(0.046, 24), [(0.003, 0.0, 0.2), (-0.006, 1.0, 0.8)], 1, 0.0020, at=(x2, 0.0))
        h.poly([(x0 + 0.075, 0.048), (x0 + 0.075 + 0.020, 0.048), (x0 + 0.075 + 0.020, -0.048), (x0 + 0.075, -0.048)], 1, 0.0018, ss=[0.8] * 4)
        h.strip(np.column_stack([np.linspace(x0 + 0.12, x2 - 0.01, 6), np.full(6, 0.022)]), np.column_stack([np.linspace(x0 + 0.12, x2 - 0.01, 6), np.full(6, 0.016)]), 2, 0.0024, es=0.5, ss=0.5)
        self.handle = own(h.build(bpy, 'fs_lenshandle', mats3('h'), kit.coll), 0.004)
        rs = 0.075; r = UI.Flat(); Pr, Nr = UI.circle_loop(rs, 48)
        r.band(Pr, Nr, [(0.030, 1.0, 0.0), (0.012, 0.55, 0.0), (-0.004, 0.0, 0.0)], 0, 0.0, at=(0.006, -0.016))
        r.tube(Pr, Nr, 0.020, 1, 0.0010, grow=0.004); r.star((rs * 0.72, rs * 0.72), 0.034, 1, 0.0020)
        self.ring = own(r.build(bpy, 'fs_lensring', mats3('r'), kit.coll), 0.006)
        V = [(0, 0, 0)] * 12; F = []; E = []; S = []
        for q in range(4):
            for row, (e, sv) in enumerate(((0.0, 0.62), (0.5, 0.92), (1.0, 0.30))): E.append(e); S.append(sv)
        for k in range(2):
            for row in range(2): a_ = 6 * k + row; F.append((a_, a_ + 3, a_ + 4, a_ + 1))
        self.lines = own(cw.mk_mesh(bpy, 'fs_lenslines', V, F, [UI.mat_gold(kit, D, 'fs_lflg', al)], None, False, kit.coll, {'e': ('FLOAT', E), 'sh': ('FLOAT', S)}), 0.005)
        self.crisp = [self.frame, self.handle, self.ring, self.lines]

    # ------------------------------------------------------------------------------------------ the story inside
    def rock_state(self, t):
        """(x, y, radius, spin) of the rock in window units (R = 1)."""
        B = W.B; rk = 0.26
        if t < B.air_in:
            return 0.06 * math.sin(0.7 * t), 0.05 + 0.04 * math.cos(0.9 * t), rk, 0.9 * t
        u = W.sm(B.air_in, B.air_in + 1.8, t)
        y = 0.05 + (0.92 - 0.05) * u; r = rk + (0.15 - rk) * u; x = 0.06 * math.sin(0.7 * t) * (1 - u) + 0.0
        if t > B.enter:
            s = (t - B.enter) / (B.streak0 - B.enter); y = 0.92 - 0.66 * min(1.0, s) ** 1.8
            if t > B.streak0: v = min(1.0, (t - B.streak0) / (B.peak - B.streak0)); y = 0.26 - 0.50 * v ** 1.15
            x = 0.0 + 0.10 * math.sin(0.4 * t)
        return x, y, r, 0.9 * t + 2.0 * (t > B.enter) * (t - B.enter) * 0.4

    def pose(self, t):
        B = W.B; D = self.D; pc = self.pc; R = self.R
        o = max(W.sm(B.win0, B.win1, t) * (1 - W.sm(B.win_close0, B.win_close1, t)), W.sm(B.win2, B.win3, t) * (1 - W.sm(B.win_close2, B.win_close3, t)))
        show = o > 0.01
        for ob in self.obs + [self.frame, self.handle, self.ring, self.lines]: ob.hide_render = not show
        if not show: return
        cx, cy = self.C; pop = o * (1.0 + 0.06 * math.sin(math.pi * min(1.0, o)))
        D.set('a_win', min(1.0, o * 1.6)); D.set('a_lens', min(1.0, o * 1.6))
        wstar = W.sm(B.win0 + 0.2, B.win1 + 0.4, t) * (1 - W.sm(B.win_close0 - 0.3, B.win_close1, t))
        wair = W.sm(B.air_in, B.air_in + 1.6, t) * (1 - W.sm(B.win_close2 - 0.4, B.win_close3, t)); D.set('wair', wair)
        wrock = W.sm(B.win2 + 0.1, B.win3 + 0.3, t) * (1 - W.sm(B.peak + 0.2, B.peak + 0.8, t))
        D.set('a_wstar', wstar); D.set('a_wrock', wrock); D.set('a_wair', wair)
        # --- the star: a giant calm ball, glowing, with soft long rays turning slowly; it breathes a little when told
        pulse = W.win(t, B.star_pulse, B.star_pulse + 1.6, 0.5)
        sp = 1.0 + 0.05 * math.sin(2 * math.pi * 0.35 * t) + 0.08 * pulse
        pc.set(self.s_glow, 0.0, 0.0, 0.95 * sp); pc.set(self.s_body, 0.0, 0.0, 0.42 * sp)
        for q, j in enumerate(self.s_rays): pc.set(j, 0.0, 0.0, 0.80 * sp, 0.12 * t + q * math.pi / 4)
        # --- the rock and its heat
        x, y, rk, spin = self.rock_state(t)
        burn = W.sm(B.peak, B.peak + 0.55, t)
        vis = wrock * (1 - burn)
        h = W.sm(B.glow0, B.glow1, t) ** 1.2 if t < B.peak else 0.0
        heat = W.keys(t, [(B.glow0 - 2.0, 0.0), (B.glow0 + 3.0, 0.0), (B.glow1 - 3.0, 0.6), (B.peak, 1.0)])      # orange to white
        D.set('heat', heat); D.set('a_wheat', min(1.0, h * 1.3) * (1 - burn))
        if vis < 1e-3 or wrock < 1e-3:
            pc.hide(self.rock); [pc.hide(j) for j in self.craters]
        else:
            pc.set(self.rock, x, y, rk * vis, spin); Rs = np.array([[math.cos(spin), -math.sin(spin)], [math.sin(spin), math.cos(spin)]])
            for j, (qx, qy, qr) in zip(self.craters, self.CR):
                q = Rs @ np.array([qx, qy * 0.86]) * rk * vis; pc.set(j, x + q[0], y + q[1], qr * rk * vis, spin)
        sz = rk * (1.0 + 2.2 * h)
        if h * (1 - burn) > 0.01:
            pc.set(self.h_big, x, y, sz * 2.4); pc.set(self.h_mid, x, y, sz * 1.5); pc.set(self.h_core, x, y, sz * 0.9)
        else:
            for j in (self.h_big, self.h_mid, self.h_core): pc.hide(j)
        # the trail above the rock (it falls head first), longer as it speeds up
        fast = W.sm(B.enter, B.streak0, t) * 0.5 + W.sm(B.streak0, B.peak, t) * 0.8
        Lt = (0.10 + 0.95 * fast) * R; n = self.TN
        co = np.zeros((2 * (n + 1), 3), np.float32); ang = 0.18
        d = np.array([math.sin(ang), math.cos(ang)])
        nrm = np.array([d[1], -d[0]])
        for i in range(n + 1):
            f = i / n; p = np.array([x, y]) * 1.0 + d * Lt / R * (1 - f); wdt = rk * 0.55 * f ** 0.8 * (1 + 0.8 * h)
            co[2 * i, :2] = p + nrm * wdt; co[2 * i + 1, :2] = p - nrm * wdt
        me = self.trail.data; me.vertices.foreach_set('co', co.ravel()); me.update()
        self.trail.hide_render = not (h * (1 - burn) > 0.02)
        # --- the burn-up flash, the sparks that fall away, the puffs of cloud at the bottom
        fl = W.win(t, B.peak - 0.05, B.peak + 1.1, 0.3); D.set('a_wflash', fl)
        if fl > 0.01: pc.set(self.flash, x, y, 0.15 + 0.55 * W.sm(B.peak, B.peak + 0.9, t))
        else: pc.hide(self.flash)
        D.set('a_wspark', 1.0)
        for k, (j, r3) in enumerate(self.sparks):
            tb = B.enter + 6.0 + (B.peak - B.enter - 6.0) * k / len(self.sparks) if k < 14 else B.peak + 0.05 + 0.04 * k
            life = 1.0 if k < 14 else 2.6; age = t - tb
            if age < 0 or age > life: pc.hide(j); continue
            xs0, ys0, _, _ = self.rock_state(min(tb, B.peak)); f = age / life
            if k < 14: px, py = xs0 + r3[0] * 0.10 + 0.04 * r3[1] * age, ys0 + 0.08 * (1 + r3[2]) * age - 0.02 * age * age
            else: px, py = x + r3[0] * 0.50 * f ** 0.6, y + r3[1] * 0.30 * f ** 0.6 - 0.25 * f * f
            pc.set(j, px, py, 0.05 * (1 - f) * (0.7 + 0.5 * abs(r3[2])), 2.0 * age)
        for q, (j, r3) in enumerate(self.puffs):
            if wair < 0.01: pc.hide(j); continue
            px = -0.85 + 1.7 * ((r3[0] + 0.01 * t * (1 + r3[1])) % 1.0); py = -0.80 - 0.05 * r3[2]
            pc.set(j, px, py, 0.34 + 0.12 * r3[1], 0.0, 0.16)
        pc.commit()
        # --- place everything with the pop
        for ob in (self.bg, self.pcob, self.trail): ob.location = (cx, cy, ob.location.z); ob.scale = (pop * R, pop * R, 1)
        self.pcob.scale = (pop * R, pop * R, 1)
        # ring on the sky and the two gold lines
        tgt = np.array(STAR_POS) if t < 20 else bez(PATH, 0.22)
        ro = max(W.win(t, B.win1 - 0.1, B.win_close0 + 0.1, 0.3), W.win(t, B.ring0, B.peak + 0.4, 0.4))
        bx, by = tgt
        self.frame.location = (cx, cy, self.frame.location.z); self.frame.scale = (pop, pop, 1)
        v = np.array([cx - bx, cy - by]); dist = np.linalg.norm(v) + 1e-9; u = v / dist; nrm2 = np.array([-u[1], u[0]])
        self.handle.location = (cx, cy, self.handle.location.z); self.handle.scale = (pop, pop, 1); self.handle.rotation_euler = (0, 0, math.atan2(v[1], v[0]) - 0.55)
        self.ring.location = (bx, by, self.ring.location.z); self.ring.scale = (ro, ro, 1); self.ring.hide_render = ro < 0.02
        co = np.zeros((12, 3), np.float32)
        for k, sd in enumerate((-1, 1)):
            a = np.array([bx, by]) + nrm2 * sd * 0.078 * ro; b = np.array([cx, cy]) + nrm2 * sd * R * pop
            tg = (b - a) / (np.linalg.norm(b - a) + 1e-9); nn = np.array([-tg[1], tg[0]])
            if nn @ UI.LIGHT < 0: nn = -nn
            for q, (pt, hw) in enumerate(((a, 0.0055 * ro), (b, 0.0075 * pop))):
                for row, off in enumerate((1.0, 0.0, -1.0)): co[6 * k + 3 * q + row] = (*(pt + nn * off * hw), 0.0)
        me = self.lines.data; me.vertices.foreach_set('co', co.ravel()); me.update(); self.lines.hide_render = ro < 0.02
