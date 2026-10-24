"""How does a dinosaur turn into stone? Words and graphics set in code, fixed to the camera (never drawn by a model).

A silent film (Sam 23 Oct 20:09): the words are the few big captions of beats.json, each in with a soft pop, large,
readable on a phone, at least 2.5 s on screen (Inter Tight ExtraBold, OFL; ink on cream plates, as Fable recolours them):
  captions      HOW DO BONES TURN TO STONE? / LONG AGO / MUD / MILLIONS OF YEARS / BONE TO STONE / WHAT IS UNDER YOUR
                FEET? (whatever beats.json says; top centre, in the sky)
  the label     the key word (FOSSIL!) with a hairline leader to the bone in the rock face
  the clock     a dial whose hand spins backwards in the rewind and races forwards through the layers and the wearing
                away (its job: tell a 6 year old that time is running backwards, then racing)
No em dash, en dash or three-dot ellipsis anywhere (gate `text`).
"""
import math
import os

import numpy as np

import cutaway as cw
import szworld as W
import szmats as M

def _lines(text, max_chars=16):
    """Break a caption into short lines (big type): greedy, at most max_chars a line."""
    out = []; cur = ''
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > max_chars: out.append(cur); cur = word
        else: cur = (cur + ' ' + word).strip()
    return '\n'.join(out + [cur])


INK, PAPER = (0.08, 0.10, 0.22), (0.99, 0.93, 0.80)
DEPTH = 5.0          # words sit 5 m in front of the camera (camera space)


def _rrect(w, h, r, n=6):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n); pts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0.0))
    V = [(0, 0, 0)] + pts; F = [(0, i + 1, (i + 1) % len(pts) + 1) for i in range(len(pts))]
    return V, F


class Words:
    def __init__(self, kit, D, cam, root):
        self.kit = kit; self.D = D; self.cam = cam; bpy = kit.bpy; self.obs = []
        font = os.path.join(root, 'films', 'cutaway', 'ads', 'drainage', 'fonts', 'InterTight-ExtraBold.ttf')
        self.font = bpy.data.fonts.load(font) if os.path.exists(font) else None
        cd = cam.ob.data; self.hw = DEPTH * 18.0 / cd.lens; self.hh = self.hw * 9 / 16
        self.caps = []
        for i, (text, t_in, t_out) in enumerate(W.word_windows()):
            if text.strip().rstrip('!').upper() == W.KEY_WORD.upper(): self.key_text = text; continue
            ob = self._text(f'fs_cap{i}', _lines(text), 0.22, f'a_cap{i}', (0.0, self.hh * 0.78))
            pl = self._plate(f'fs_cap{i}_pl', ob, f'a_cap{i}', 0.10, 0.065)
            self.caps.append((ob, pl, f'a_cap{i}', t_in, t_out))
        self.label = self._text('fs_label', getattr(self, 'key_text', W.KEY_WORD + '!'), 0.22, 'a_label', (0, 0))
        self.label_pl = self._plate('fs_label_pl', self.label, 'a_label', 0.08, 0.05)
        self.label_h = float(self.label.dimensions.y)      # measured once at scale 1 (frames must not read the last frame's state)
        # the leader: a hairline from the label plate to the bone, and a dot on the bone
        m = M.mat_word(kit, D, 'fs_leader', INK, 'a_label')
        self.leader = cw.mk_mesh(bpy, 'fs_leader', [(0, 0, 0)] * 4, [(0, 1, 2, 3)], [m], None, False, kit.coll); self._own(self.leader)
        V, F = _rrect(0.034, 0.034, 0.017, 4)
        self.dot = cw.mk_mesh(bpy, 'fs_leaderdot', V, F, [m], None, False, kit.coll); self._own(self.dot)
        # the clock: a cream dial, an ink ring with twelve ticks, one hand
        self.clock_c = np.array([self.hw * 0.82, self.hh * 0.70]); r = 0.19
        V, F = _rrect(2 * r, 2 * r, r, 10)
        self.clock_pl = cw.mk_mesh(bpy, 'fs_clock_pl', V, F, [M.mat_word(kit, D, 'fs_clock_plm', PAPER, 'a_clock')], None, False, kit.coll); self._own(self.clock_pl)
        V = []; F = []; n = 48
        for k in range(n):
            a = 2 * math.pi * k / n; V += [((r - 0.022) * math.cos(a), (r - 0.022) * math.sin(a), 0), ((r - 0.004) * math.cos(a), (r - 0.004) * math.sin(a), 0)]
        F += [(2 * k, 2 * ((k + 1) % n), 2 * ((k + 1) % n) + 1, 2 * k + 1) for k in range(n)]
        for k in range(12):
            a = 2 * math.pi * k / 12; c, s = math.cos(a), math.sin(a); o = len(V); w = 0.007; r0, r1 = r - 0.055, r - 0.03
            V += [(r0 * c - w * s, r0 * s + w * c, 0), (r1 * c - w * s, r1 * s + w * c, 0), (r1 * c + w * s, r1 * s - w * c, 0), (r0 * c + w * s, r0 * s - w * c, 0)]
            F.append((o, o + 1, o + 2, o + 3))
        mi = M.mat_word(kit, D, 'fs_clockm', INK, 'a_clock')
        self.clock_ring = cw.mk_mesh(bpy, 'fs_clockring', V, F, [mi], None, False, kit.coll); self._own(self.clock_ring)
        V = [(-0.012, -0.02, 0), (0.012, -0.02, 0), (0.006, r - 0.04, 0), (-0.006, r - 0.04, 0)] + [(0.022 * math.cos(a), 0.022 * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 13)[:-1]]
        F = [(0, 1, 2, 3)] + [(4 + k, 4 + (k + 1) % 12, 4 + (k + 6) % 12) for k in range(12)]
        self.hand = cw.mk_mesh(bpy, 'fs_clockhand', V, F, [mi], None, False, kit.coll); self._own(self.hand)
        for ob, dz in ((self.clock_pl, 0.0), (self.clock_ring, 0.002), (self.hand, 0.004)):
            ob.location = (self.clock_c[0], self.clock_c[1], -DEPTH + dz)

    def _own(self, ob):
        ob.parent = self.cam.ob; ob.matrix_parent_inverse.identity(); self.obs.append(ob)
        for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
        return ob

    def _text(self, name, body, size, alpha, xy):
        bpy = self.kit.bpy; cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        if self.font: cu.font = self.font
        cu.size = size; cu.space_line = 0.95
        ob = bpy.data.objects.new(name, cu); self.kit.coll.objects.link(ob)
        cu.materials.append(M.mat_word(self.kit, self.D, name + 'm', INK, alpha))
        self._own(ob); ob.location = (xy[0], xy[1], -DEPTH + 0.004); return ob

    def _plate(self, name, text, alpha, px, py):
        bpy = self.kit.bpy; bpy.context.view_layer.update()
        dims = text.dimensions; w, h = dims.x + 2 * px, dims.y + 2 * py
        V, F = _rrect(w, h, min(h / 2, 0.08), 6)
        ob = cw.mk_mesh(bpy, name, V, F, [M.mat_word(self.kit, self.D, name + 'm', PAPER, alpha)], None, False, self.kit.coll)
        self._own(ob); ob.location = (text.location[0], text.location[1] + (h * 0.0), -DEPTH); ob['fs_off'] = (0.0, 0.0)
        # FONT objects centre on their text box; the plate is centred on the same point (measured below each frame)
        return ob

    def pose(self, t, bone_world=None):
        B = W.B; D = self.D
        for ob, pl, an, t_in, t_out in self.caps:
            a = W.sm(t_in, t_in + 0.35, t) * (1 - W.sm(t_out - 0.35, t_out, t)); D.set(an, a)
            pop = 0.86 + 0.14 * W.sm(t_in, t_in + 0.35, t) + 0.04 * math.sin(math.pi * min(1.0, max(0.0, (t - t_in) / 0.35)))
            for o in (ob, pl): o.scale = (pop, pop, 1); o.hide_render = a < 0.01
        # the clock: backwards in the rewind, racing forwards through the layers, forwards again in the rain
        on = max(W.win(t, B.rw0, B.rw1 + 0.4, 0.3), W.win(t, B.stack0 - 0.3, B.stack1 + 0.4, 0.3), W.win(t, B.rain0, B.erode1 + 0.3, 0.3))
        D.set('a_clock', on)
        ang = -2 * math.pi * 1.6 * np.clip(t - B.rw0, 0, B.rw1 - B.rw0) + 2 * math.pi * 1.2 * np.clip(t - B.stack0, 0, B.stack1 - B.stack0) \
              + 2 * math.pi * 1.0 * np.clip(t - B.rain0, 0, B.erode1 - B.rain0)
        self.hand.rotation_euler = (0, 0, -float(ang))
        pop = 0.85 + 0.15 * on
        for ob in (self.clock_pl, self.clock_ring, self.hand): ob.scale = (pop, pop, 1); ob.hide_render = on < 0.01
        # the label: FOSSIL above the bone, a hairline down to it
        a = W.sm(B.label0, B.label0 + 0.35, t) * (1 - W.sm(B.label1 - 0.4, B.label1, t)); D.set('a_label', a)
        show = a > 0.01 and bone_world is not None
        for ob in (self.label, self.label_pl, self.leader, self.dot): ob.hide_render = not show
        if show:
            from mathutils import Vector
            p = self.cam.ob.matrix_basis.inverted() @ Vector(tuple(bone_world)); k = DEPTH / max(-p.z, 1e-3); bx, by = p.x * k, p.y * k   # this frame's camera (matrix_world lags a frame)
            lx, ly = bx + 0.62, by + 0.50;      # up and to the right: the girl works on the left of the bone, the line never crosses her
            pop = 0.88 + 0.12 * W.sm(B.label0, B.label0 + 0.35, t)
            self.label.location = (lx, ly, -DEPTH + 0.004); self.label_pl.location = (lx, ly, -DEPTH)
            for ob in (self.label, self.label_pl): ob.scale = (pop, pop, 1)
            y0 = ly - (self.label_h / 2 + 0.04) * pop
            d = np.array([bx - lx, by - y0]); d /= np.linalg.norm(d) + 1e-9; nrm = np.array([-d[1], d[0]]) * 0.006
            P0 = np.array([lx - 0.10, y0]); P1 = np.array([bx, by])
            V = [(*(P0 - nrm), -DEPTH + 0.002), (*(P1 - nrm), -DEPTH + 0.002), (*(P1 + nrm), -DEPTH + 0.002), (*(P0 + nrm), -DEPTH + 0.002)]
            me = self.leader.data; me.vertices.foreach_set('co', np.array(V, np.float32).ravel()); me.update()
            self.dot.location = (bx, by, -DEPTH + 0.002)
