"""How does a dinosaur turn into stone? Words and graphics set in code, fixed to the camera (never drawn by a model).

A silent film (Sam 23 Oct 20:09): the words are the few big captions of beats.json, each in with a soft pop, large,
readable on a phone, at least 2.5 s on screen. Sam 24 Oct: "improve the graphical elements (text, box, frame)": the
graphics are now a painted storybook set (szui.py): Fredoka Bold (OFL, fonts/) in deep plum with a warm under-shadow, on
parchment cards with a hand-cut edge, a thin gold rim, gold sparkles and a soft floating shadow; a card pops in with a
small unfold and a settling tilt (pure functions of time):
  captions      HOW DO BONES TURN TO STONE? / LONG AGO / MUD / MILLIONS OF YEARS / BONE TO STONE / WHAT IS UNDER YOUR
                FEET? (whatever beats.json says; top centre, in the sky)
  the label     the key word (FOSSIL!) on a card, with a graceful tapered gold ribbon that draws itself down to a gold
                ring round the bone (it bows away from the girl and never crosses her)
  the clock     a storybook pocket watch (gold bezel, crown, cream face, plum hands with spade tips) whose hands spin
                backwards in the rewind and race forwards through the layers and the wearing away (its job: tell a
                6 year old that time is running backwards, then racing)
The API is unchanged: Words(kit, D, cam, root), .obs, .pose(t, bone_world). No em dash, en dash or three-dot ellipsis
anywhere (gate `text`).
"""
import math
import os

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M
import szui as UI

HERE = os.path.dirname(os.path.abspath(__file__))


def _lines(text, max_chars=23):
    """Break a caption into short lines (big type): greedy, at most max_chars a line."""
    out = []; cur = ''
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > max_chars: out.append(cur); cur = word
        else: cur = (cur + ' ' + word).strip()
    return '\n'.join(out + [cur])


INK, PAPER = (0.08, 0.10, 0.22), (0.99, 0.93, 0.80)      # kept for the films that copy this folder (Fable's word recolour)
DEPTH = 5.0          # words sit 5 m in front of the camera (camera space)
TEXT_Z = 0.0050      # the text stands this far in front of its card
UNDER = (0.93, 0.56, 0.22)    # the warm gold-orange under-shadow of the letters
UNDER_AT = (0.0065, -0.0085)


def _rrect(w, h, r, n=6):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n); pts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0.0))
    V = [(0, 0, 0)] + pts; F = [(0, i + 1, (i + 1) % len(pts) + 1) for i in range(len(pts))]
    return V, F


def _sym(profile, y0=0.0):
    """A hand: a symmetric outline from (half width, y) pairs along its length, as quads between the two sides."""
    R = [(w, y) for w, y in profile]; L = [(-w, y) for w, y in profile]; V = R + L; n = len(R)
    return V, [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]


class Words:
    def __init__(self, kit, D, cam, root):
        self.kit = kit; self.D = D; self.cam = cam; bpy = kit.bpy; self.obs = []
        font = os.path.join(HERE, 'fonts', 'Fredoka-Bold.ttf')
        if not os.path.exists(font): font = os.path.join(root, 'films', 'cutaway', 'ads', 'drainage', 'fonts', 'InterTight-ExtraBold.ttf')
        self.font = bpy.data.fonts.load(font) if os.path.exists(font) else None
        cd = cam.ob.data; self.hw = DEPTH * 18.0 / cd.lens; self.hh = self.hw * 9 / 16
        self.caps = []
        for i, (text, t_in, t_out) in enumerate(W.word_windows()):
            if text.strip().rstrip('!').upper() == W.KEY_WORD.upper(): self.key_text = text; continue
            an = f'a_cap{i}'; xy = (0.0, self.hh * 0.78)
            ob = self._text(f'fs_cap{i}', _lines(text), 0.22, an, xy, UI.PLUM, TEXT_Z)
            sh = self._text(f'fs_cap{i}_sh', _lines(text), 0.22, an, (xy[0] + UNDER_AT[0], xy[1] + UNDER_AT[1]), UNDER, TEXT_Z - 0.0012)
            pl = self._card(f'fs_cap{i}_pl', ob, an, i, clamp_top=True)
            self.caps.append((ob, pl, an, t_in, t_out, sh))
        key = getattr(self, 'key_text', W.KEY_WORD + '!')
        self.label = self._text('fs_label', key, 0.27, 'a_label', (0, 0), UI.PLUM, TEXT_Z)
        self.label_sh = self._text('fs_label_sh', key, 0.27, 'a_label', UNDER_AT, UNDER, TEXT_Z - 0.0012)
        self.label_pl = self._card('fs_label_pl', self.label, 'a_label', 11)
        self.label_h = float(self.label.dimensions.y)      # measured once at scale 1 (frames must not read the last frame's state)
        self._build_pointer(); self._build_clock()

    # ------------------------------------------------------------------------------------------ helpers
    def _own(self, ob):
        ob.parent = self.cam.ob; ob.matrix_parent_inverse.identity(); self.obs.append(ob)
        for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
        return ob

    def _text(self, name, body, size, alpha, xy, colour, z):
        bpy = self.kit.bpy; cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        if self.font: cu.font = self.font
        cu.size = size; cu.space_line = 1.0; cu.space_character = 1.05
        ob = bpy.data.objects.new(name, cu); self.kit.coll.objects.link(ob)
        cu.materials.append(UI.mat_flat(self.kit, self.D, name + 'm', alpha, colour))
        self._own(ob); ob.location = (xy[0], xy[1], -DEPTH + z); return ob

    def _mats(self, name, alpha):
        k, D = self.kit, self.D
        return [UI.mat_shadow(k, D, name + '_ms', alpha), UI.mat_gold(k, D, name + '_mg', alpha), UI.mat_paper(k, D, name + '_mp', alpha)]

    def _card(self, name, text, alpha, seed, clamp_top=False):
        bpy = self.kit.bpy; bpy.context.view_layer.update()
        dims = text.dimensions; w, h = dims.x + 2 * 0.15, dims.y + 2 * 0.105
        if clamp_top: text.location.y = min(text.location.y, self.hh * 0.975 - h / 2 - 0.05)      # a two-line card keeps its top inside the frame
        fl = UI.Flat(); UI.card(fl, w, h, min(0.13, h * 0.34), seed, (0, 1, 2))
        ob = fl.build(bpy, name, self._mats(name, alpha), self.kit.coll)
        self._own(ob); ob.location = (text.location[0], text.location[1], -DEPTH); return ob

    def _flat(self, name, fl, mats, z):
        ob = fl.build(self.kit.bpy, name, mats, self.kit.coll); self._own(ob); ob.location = (0, 0, -DEPTH + z); return ob

    # ------------------------------------------------------------------------------------------ the pointer to the bone
    def _build_pointer(self):
        """A tapered gold ribbon (rewritten each frame so it can draw itself) and a gold ring round the bone."""
        bpy = self.kit.bpy; NS = self.NS = 28
        V = [(0, 0, 0)] * (3 * (NS + 1)); F = []; E = []; S = []
        for k in range(NS + 1):
            for row, (e, s) in enumerate(((0.0, 0.56), (0.5, 0.80), (1.0, 0.28))): E.append(e); S.append(s)
        for k in range(NS):
            for row in range(2): a = 3 * k + row; F.append((a, a + 3, a + 4, a + 1))
        gold = UI.mat_gold(self.kit, self.D, 'fs_leaderm', 'a_label')
        self.leader = cw.mk_mesh(bpy, 'fs_leader', V, F, [gold], None, False, self.kit.coll, {'e': ('FLOAT', E), 'sh': ('FLOAT', S)})
        self._own(self.leader)
        fl = UI.Flat(); P, N = UI.circle_loop(0.056, 44); fl.tube(P, N, 0.021, 0, 0.0, grow=0.004)
        fl.star((0.056 * 0.78, 0.056 * 0.78), 0.030, 0, 0.0005); fl.star((-0.056 * 0.92, -0.056 * 0.55), 0.020, 0, 0.0005)
        self.dot = self._flat('fs_leaderdot', fl, [UI.mat_gold(self.kit, self.D, 'fs_leaderdotm', 'a_label')], 0.0006)

    # ------------------------------------------------------------------------------------------ the pocket watch
    def _build_clock(self):
        bpy = self.kit.bpy; k, D = self.kit, self.D
        self.clock_c = np.array([self.hw * 0.82, self.hh * 0.70]); r = 0.19
        mats = [UI.mat_shadow(k, D, 'fs_clk_s', 'a_clock', 0.36), UI.mat_gold(k, D, 'fs_clk_g', 'a_clock'), UI.mat_face(k, D, 'fs_clk_f', 'a_clock'),
                UI.mat_flat(k, D, 'fs_clk_i', 'a_clock', UI.PLUM)]
        fl = UI.Flat(); Pc, Nc = UI.circle_loop(r - 0.012, 72)
        fl.band(Pc, Nc, [(0.075, 1.0, 0.0), (0.030, 0.55, 0.0), (0.0, 0.0, 0.0)], 0, 0.0, at=(0.008, -0.026)); fl.fan(Pc, Nc, 0.0, 0.0, 0.0, 0, 0.0, at=(0.008, -0.026))
        # the crown and a little stem (behind the bezel)
        Pk, Nk = UI.rrect_loop(0.082, 0.062, 0.020, 0, 0.0, 0.03, 4)
        fl.fan(Pk, Nk, 0.0, 0.5, 0.62, 1, 0.0006, at=(0.0, r + 0.014)); fl.tube(Pk, Nk, 0.014, 1, 0.0007, at=(0.0, r + 0.014))
        for q in (-1, 0, 1): fl.poly([(q * 0.022 - 0.004, r + 0.002), (q * 0.022 + 0.004, r + 0.002), (q * 0.022 + 0.004, r + 0.044), (q * 0.022 - 0.004, r + 0.044)], 3, 0.0009, ss=[0.2] * 4)
        # the dark gold outline, the gold bezel (a lit tube), the cream face
        fl.band(Pc, Nc, [(0.028, 0.0, 0.10), (0.018, 1.0, 0.10)], 1, 0.0010)
        fl.tube(Pc, Nc, 0.036, 1, 0.0016)
        fl.band(Pc, Nc, [(-0.017, 0.0, 0.5), (-0.040, 0.45, 0.5), (-0.100, 1.0, 0.5)], 2, 0.0012)
        fl.fan(Pc, Nc, -0.100, 1.0, 0.5, 2, 0.0012)
        Pi, Ni = UI.circle_loop(r - 0.058, 72)
        fl.band(Pi, Ni, [(0.004, 0.0, 0.50), (0.0, 0.5, 0.82), (-0.004, 1.0, 0.50)], 1, 0.0020)
        # twelve ticks (the quarters longer, with a gold dot at the top)
        for q in range(12):
            a = 2 * math.pi * q / 12; c, s = math.cos(a), math.sin(a); big = q % 3 == 0; r0 = r - (0.108 if big else 0.092); r1 = r - 0.068; w = 0.0085 if big else 0.0055
            fl.poly([(r0 * c - w * s, r0 * s + w * c), (r1 * c - w * s, r1 * s + w * c), (r1 * c + w * s, r1 * s - w * c), (r0 * c + w * s, r0 * s - w * c)], 3, 0.0024, ss=[0.2] * 4)
        self.clock_pl = self._flat('fs_clock_pl', fl, mats, 0.0); self.clock_pl.location = (self.clock_c[0], self.clock_c[1], -DEPTH)
        # the two hands: spade tips, a ring at the tail (the minute hand also carries the gold hub)
        def hand(name, Lh, ww, z, hub):
            f2 = UI.Flat(); pr = [(0.5 * ww, -0.040), (0.55 * ww, -0.026), (0.20 * ww, 0.0), (0.20 * ww, 0.46 * Lh), (0.45 * ww, 0.54 * Lh), (ww, 0.64 * Lh),
                                  (0.70 * ww, 0.76 * Lh), (0.30 * ww, 0.88 * Lh), (0.0, Lh)]
            Vh, Fh = _sym(pr)
            o = len(f2.V)
            for (x, y) in Vh: f2.V.append((x, y, 0.0)); f2.E.append(0.5); f2.S.append(0.2)
            for fc in Fh: f2.F.append(tuple(o + j for j in fc)); f2.M.append(0)
            Pt, Nt = UI.circle_loop(0.014, 20); f2.fan(Pt, Nt, 0.0, 0.5, 0.2, 0, 0.0, at=(0.0, -0.046))
            if hub:
                Ph, Nh = UI.circle_loop(0.022, 24); f2.fan(Ph, Nh, 0.0, 0.5, 0.78, 1, 0.0010); f2.band(Ph, Nh, [(0.004, 0.0, 0.2), (-0.004, 1.0, 0.8)], 1, 0.0012)
            ob = self._flat(name, f2, [UI.mat_flat(k, D, name + 'm', 'a_clock', UI.PLUM), UI.mat_gold(k, D, name + 'g', 'a_clock')], z)
            ob.location = (self.clock_c[0], self.clock_c[1], -DEPTH + z); return ob
        self.hand_h = hand('fs_clockhour', r * 0.42, 0.017, 0.0040, False)
        self.hand = hand('fs_clockhand', r * 0.62, 0.013, 0.0056, True)

    # ------------------------------------------------------------------------------------------ per frame
    def pose(self, t, bone_world=None):
        B = W.B; D = self.D
        for ob, pl, an, t_in, t_out, sh in self.caps:
            a = W.sm(t_in, t_in + 0.35, t) * (1 - W.sm(t_out - 0.35, t_out, t)); D.set(an, a)
            self._pop(t, t_in, a, ob, pl, sh)
            sh.location = (ob.location.x + UNDER_AT[0] * ob.scale.x, ob.location.y + UNDER_AT[1] * ob.scale.y, sh.location.z)
        # the clock: backwards in the rewind, racing forwards through the layers, forwards again in the rain
        on = max(W.win(t, B.rw0, B.rw1 + 0.4, 0.3), W.win(t, B.stack0 - 0.3, B.stack1 + 0.4, 0.3), W.win(t, B.rain0, B.erode1 + 0.3, 0.3))
        D.set('a_clock', on)
        ang = -2 * math.pi * 1.6 * np.clip(t - B.rw0, 0, B.rw1 - B.rw0) + 2 * math.pi * 1.2 * np.clip(t - B.stack0, 0, B.stack1 - B.stack0) \
              + 2 * math.pi * 1.0 * np.clip(t - B.rain0, 0, B.erode1 - B.rain0)
        self.hand.rotation_euler = (0, 0, -float(ang)); self.hand_h.rotation_euler = (0, 0, -float(ang) / 12.0)
        pop = 0.85 + 0.15 * on
        for ob in (self.clock_pl, self.hand_h, self.hand): ob.scale = (pop, pop, 1); ob.hide_render = on < 0.01
        # the label: FOSSIL! up and to the right of the bone, a gold ribbon curling down to a ring round it
        a = W.sm(B.label0, B.label0 + 0.35, t) * (1 - W.sm(B.label1 - 0.4, B.label1, t)); D.set('a_label', a)
        show = a > 0.01 and bone_world is not None
        for ob in (self.label, self.label_sh, self.label_pl, self.leader, self.dot): ob.hide_render = not show
        if not show: return
        from mathutils import Vector
        p = self.cam.ob.matrix_basis.inverted() @ Vector(tuple(bone_world)); kk = DEPTH / max(-p.z, 1e-3); bx, by = p.x * kk, p.y * kk   # this frame's camera (matrix_world lags a frame)
        lx, ly = bx + 0.62, by + 0.50;      # up and to the right: the girl works on the left of the bone, the line never crosses her
        self.label.location = (lx, ly, -DEPTH + TEXT_Z); self.label_pl.location = (lx, ly, -DEPTH)
        self._pop(t, B.label0, a, self.label, self.label_pl, self.label_sh, pop0=0.88)
        self.label_sh.location = (lx + UNDER_AT[0] * self.label.scale.x, ly + UNDER_AT[1] * self.label.scale.y, -DEPTH + TEXT_Z - 0.0012)
        pop = self.label.scale.x
        # the ribbon: a quadratic curve from under the card to the ring, bowed to the right (away from the girl), drawn on over 0.55 s
        y0 = ly - (self.label_h / 2 + 0.105) * pop + 0.02
        P0 = np.array([lx - 0.12, y0]); Pb = np.array([bx, by])
        dd = Pb - P0; ln = np.linalg.norm(dd) + 1e-9; d = dd / ln; nrm = np.array([-d[1], d[0]])
        C = (P0 + Pb) / 2 + nrm * 0.16 * ln
        tail = C - Pb; tail /= np.linalg.norm(tail) + 1e-9; P1 = Pb + tail * 0.060            # stop at the ring, not on the bone
        g = W.sm(B.label0 + 0.20, B.label0 + 0.80, t)
        NS = self.NS; co = np.zeros((3 * (NS + 1), 3), np.float32)
        for q in range(NS + 1):
            u = g * q / NS; pt = (1 - u) ** 2 * P0 + 2 * u * (1 - u) * C + u * u * P1
            tg = 2 * (1 - u) * (C - P0) + 2 * u * (P1 - C); tg /= np.linalg.norm(tg) + 1e-9; nn = np.array([-tg[1], tg[0]])
            hw = 0.027 * (1 - u) ** 0.8 * (1 - 0.9 * (q / NS) ** 7) + 0.0035; z = -DEPTH + 0.0001
            if nn @ UI.LIGHT < 0: nn = -nn          # row 0 on the side turned to the light (upper left), row 2 on the shaded side
            for row, off in enumerate((1.0, 0.0, -1.0)):
                co[3 * q + row] = (*(pt + nn * off * hw), z)
        self.leader.hide_render = g < 0.02
        me = self.leader.data; me.vertices.foreach_set('co', co.ravel()); me.update()
        ring = W.sm(0.80, 1.0, g) * (1.0 + 0.08 * math.sin(2 * math.pi * 0.9 * max(0.0, t - B.label0)))
        self.dot.location = (bx, by, -DEPTH + 0.0006); self.dot.scale = (ring, ring, 1); self.dot.hide_render = ring < 0.02

    def _pop(self, t, t_in, a, ob, pl, sh, pop0=0.86):
        """A card pops in: grows from 86 percent with a small overshoot, unfolds from a slightly flat start, settles from a
        3 degree tilt (all pure functions of t)."""
        u = min(1.0, max(0.0, (t - t_in) / 0.35)); w = W.sm(t_in, t_in + 0.35, t)
        pop = pop0 + (1 - pop0) * w + 0.04 * math.sin(math.pi * u)
        sy = pop * (0.90 + 0.10 * W.sm(t_in, t_in + 0.45, t)); u2 = min(1.0, max(0.0, (t - t_in) / 0.6))
        rot = 0.055 * (1 - u2) ** 2 * math.cos(8.0 * u2)
        for o in (ob, pl, sh): o.scale = (pop, sy, 1); o.rotation_euler = (0, 0, rot); o.hide_render = a < 0.01
