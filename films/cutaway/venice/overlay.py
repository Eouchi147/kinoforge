"""Clean graphic overlays set in code for the Cutaway films: labels with a hairline leader, counters, arrows, a title.

Every element is a flat object parented to the camera at a fixed distance in front of the lens, visible to camera rays
only (no shadows, no reflections), so it reads as a 2D layer laid over the picture while Cycles renders it in the same
pass. Positions are in pixels of the delivery frame (origin at the centre, x right, y up). Anchors in the world are
projected through the camera every frame so leaders stay pinned to what they point at while the camera moves.
One text face (Instrument Sans, OFL, ads/fonts). Words and numbers come from the script; nothing is drawn by a model.
"""
import math
import numpy as np
import cutaway as cw

INK = (0.07, 0.09, 0.12)
PAPER = (0.97, 0.96, 0.93)


class Overlay:
    def __init__(self, kit, cam_ob, font_path, W, H, exposure=0.0, dist=0.5):
        self.kit = kit; self.bpy = kit.bpy; self.cam = cam_ob; self.W = W; self.H = H; self.d = dist
        self.font = self.bpy.data.fonts.load(font_path)
        self.gain = 1.0 / (2 ** exposure)       # emission so that the chosen colours survive the view exposure
        self.items = []; self.lens = cam_ob.data.lens

    # --------------------------------------------------------------------- geometry helpers
    def upx(self):
        """Local units per delivery pixel at the overlay plane."""
        return 2 * self.d * (self.cam.data.sensor_width / 2) / self.cam.data.lens / self.W

    def to_local(self, x, y, z_off=0.0):
        u = self.upx(); return (x * u, y * u, -self.d + z_off)

    def project(self, p):
        """World point -> delivery pixels (origin centre), from the camera's current location and rotation."""
        from mathutils import Matrix, Vector
        M = Matrix.LocRotScale(Vector(self.cam.location), self.cam.rotation_euler.to_quaternion(), Vector((1, 1, 1)))
        q = M.inverted() @ Vector(p)
        if q.z > -1e-6: return None
        k = (self.cam.data.lens / (self.cam.data.sensor_width / 2)) * (self.W / 2)
        return (q.x / -q.z * k, q.y / -q.z * k)

    def _mat(self, name, color):
        bpy = self.bpy; m = cw._new_mat(bpy, name); g = cw.G(m.node_tree, self.kit)
        em = g.node('ShaderNodeEmission', ins={'Color': cw.srgb(color), 'Strength': self.gain})
        tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
        a = g.value(0.0, 'alpha'); g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(em, mx.inputs[2]); cw._finish(g, mx)
        try: m.blend_method = 'BLEND'
        except Exception: pass
        return m, a, em

    def _obj(self, ob):
        ob.parent = self.cam
        for at in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
            try: setattr(ob, at, False)
            except Exception: pass
        ob.hide_render = True
        return ob

    # --------------------------------------------------------------------- elements
    def text(self, name, body, px, color=INK, align='CENTER', spacing=1.0, bold=0.0):
        bpy = self.bpy; cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.font = self.font; cu.align_x = align; cu.align_y = 'CENTER'
        cu.space_character = spacing; cu.offset = bold * 0.018; cu.resolution_u = 6
        ob = bpy.data.objects.new(name, cu); self.kit.coll.objects.link(ob)
        m, a, em = self._mat(name + '_m', color); cu.materials.append(m)
        e = Elem(self, ob, a, kind='text'); e.px = px; e.em = em; self._obj(ob); self.items.append(e); return e

    def mesh(self, name, color, n_verts, faces):
        V = np.zeros((n_verts, 3)); ob = cw.mk_mesh(self.bpy, name, V, faces, [], None, False, self.kit.coll)
        m, a, em = self._mat(name + '_m', color); ob.data.materials.append(m)
        e = Elem(self, ob, a, kind='mesh'); e.em = em; self._obj(ob); self.items.append(e); return e

    def pill(self, name, color=PAPER, seg=8):
        n = 4 * (seg + 1); F = [tuple(range(n))]
        e = self.mesh(name, color, n, F); e.seg = seg; return e

    def line(self, name, color=INK):
        return self.mesh(name, color, 4, [(0, 1, 2, 3)])

    def dot(self, name, color=INK, seg=12):
        return self.mesh(name, color, seg, [tuple(range(seg))])

    def arrow(self, name, color=INK):
        return self.mesh(name, color, 7, [(0, 1, 2, 3), (4, 5, 6)])

    def hide_all(self):
        for e in self.items: e.set_alpha(0.0)


class Elem:
    def __init__(self, ov, ob, alpha_node, kind):
        self.ov = ov; self.ob = ob; self.a = alpha_node; self.kind = kind; self.alpha = 0.0

    def set_alpha(self, v):
        v = float(max(0.0, min(1.0, v))); self.alpha = v; self.a.default_value = v; self.ob.hide_render = v < 0.004

    def set_text(self, body):
        if self.ob.data.body != body: self.ob.data.body = body

    def place_text(self, x, y, px=None, z_off=0.0):
        u = self.ov.upx(); s = (px or self.px) * u
        self.ob.scale = (s, s, s); self.ob.location = self.ov.to_local(x, y, z_off)

    def text_size_px(self):
        """Width and height of the text in delivery pixels (layout from the font, scale 1 = 1 unit per em)."""
        self.ov.bpy.context.view_layer.update()
        d = self.ob.dimensions; u = self.ov.upx()
        return d.x / u, d.y / u

    def set_verts(self, pts_px, z_off=0.0):
        V = np.array([self.ov.to_local(x, y, z_off) for x, y in pts_px], np.float32).reshape(-1)
        self.ob.data.vertices.foreach_set('co', V); self.ob.data.update()

    def pill_shape(self, x0, y0, x1, y1, r, z_off=-0.0004):
        seg = self.seg; pts = []
        for (cx, cy, a0) in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
            for k in range(seg + 1):
                a = math.radians(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.set_verts(pts, z_off)

    def line_shape(self, a, b, width=1.3, z_off=0.0):
        a = np.array(a, float); b = np.array(b, float); d = b - a; L = np.linalg.norm(d) + 1e-9; n = np.array([-d[1], d[0]]) / L * width / 2
        self.set_verts([a - n, b - n, b + n, a + n], z_off)

    def dot_shape(self, c, r=3.0, z_off=0.0):
        seg = len(self.ob.data.vertices)
        self.set_verts([(c[0] + r * math.cos(2 * math.pi * k / seg), c[1] + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)], z_off)

    def arrow_shape(self, a, b, p=1.0, width=2.2, head=11.0, z_off=0.0):
        """A thin arrow drawn on from a towards b (p = 0..1), with a tapered head."""
        a = np.array(a, float); b = np.array(b, float); d = b - a; L = np.linalg.norm(d) + 1e-9; t = d / L; n = np.array([-t[1], t[0]])
        tip = a + d * max(0.02, p); hb = tip - t * head; body_end = hb if np.dot(hb - a, t) > 0 else a
        w = width / 2; hw = head * 0.42
        self.set_verts([a - n * w * 0.5, body_end - n * w, body_end + n * w, a + n * w * 0.5, hb - n * hw, tip, hb + n * hw], z_off)


def ease(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def fade(t, t0, t1, fin=0.35, fout=0.35):
    """Opacity for an element shown from t0 to t1 with soft fades."""
    if t < t0 or t > t1: return 0.0
    return min(ease((t - t0) / fin) if fin > 0 else 1.0, ease((t1 - t) / fout) if fout > 0 else 1.0)


class Label:
    """Small caps label on a paper pill, with an optional hairline leader to a world anchor and a dot on the anchor."""
    def __init__(self, ov, name, body, px=17, leader=True, color=INK, paper=PAPER):
        self.ov = ov; self.body = body.upper()
        self.plate = ov.pill(name + '_pl', paper); self.txt = ov.text(name + '_tx', self.body, px, color, 'CENTER', 1.12, bold=0.5)
        self.lead = ov.line(name + '_ld', color) if leader else None; self.dot = ov.dot(name + '_dt', color) if leader else None
        self.size = None

    def set_body(self, body):
        body = body.upper()
        if body != self.body: self.body = body; self.txt.set_text(body); self.size = None

    def show(self, alpha, pos, anchor=None, draw=1.0):
        """pos: label centre (px). anchor: world point (or a px tuple via ('px', x, y)); draw: leader draw-on 0..1."""
        for e in (self.plate, self.txt, self.lead, self.dot):
            if e: e.set_alpha(alpha)
        if alpha <= 0.004: return
        if self.size is None:
            self.txt.place_text(0, 0); self.size = self.txt.text_size_px()
        w, h = self.size; px = self.txt.px; padx, pady = px * 0.75, px * 0.55
        x, y = pos; self.txt.place_text(x, y - h * 0.08)
        self.plate.pill_shape(x - w / 2 - padx, y - px * 0.5 - pady, x + w / 2 + padx, y + px * 0.5 + pady, px * 0.5 + pady)
        if self.lead and anchor is not None:
            ap = anchor[1:] if (isinstance(anchor, tuple) and anchor and anchor[0] == 'px') else self.ov.project(anchor)
            if ap is None: self.lead.set_alpha(0); self.dot.set_alpha(0); return
            ap = np.array(ap, float); c = np.array([x, y], float); d = ap - c
            # leave the pill from its nearest edge
            ex = (w / 2 + padx) if abs(d[0]) * (px + 2 * pady) > abs(d[1]) * (w + 2 * padx) else None
            if ex is not None: start = c + np.array([math.copysign(ex, d[0]), d[1] * ex / (abs(d[0]) + 1e-9)])
            else: ey = px * 0.5 + pady; start = c + np.array([d[0] * ey / (abs(d[1]) + 1e-9), math.copysign(ey, d[1])])
            end = start + (ap - start) * ease(draw)
            self.lead.line_shape(start, end, 1.4); self.dot.dot_shape(ap, 3.2); self.dot.set_alpha(alpha * ease((draw - 0.7) / 0.3))
