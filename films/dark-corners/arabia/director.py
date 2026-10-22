"""The shot list of the Arabia film: every shot is a pure function of the pose time t (seconds, even frames only)."""
import math, os
import numpy as np
from kit import *
from kit import _mat
import world as W
import actors as A
import props as P
from actors import D, pivot, mk

# ------------------------------------------------------------------------------------------------ helpers
def gz(x, y):
    if x > 6.0:
        import blender
        return float(blender.mecca_h(np.array(x), np.array(y)))
    return float(W.terrain_h(np.array(x), np.array(y)))

def V3(*a): return np.array(a, float)
def ez(t, t0, t1, a, b, e='s'):
    u = clamp((t - t0) / (t1 - t0)); u = ease(u, e)
    if isinstance(a, (tuple, list, np.ndarray)): return tuple(float(x + (y - x) * u) for x, y in zip(a, b))
    return a + (b - a) * u
def seg(t, keys, e='s'):
    """keys = [(t, value), ...]: piecewise eased interpolation, values scalars or tuples."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t <= t1: return ez(t, t0, t1, a, b, e)
    return keys[-1][1]
def snapt(t): return round(t * 12.0) / 12.0
def blink_at(t, times, dur=0.17):
    return 1.0 if any(0 <= t - b < dur for b in times) else 0.0
def talk(t, t0, t1, rate=7.0, seed=0.0):
    """Mouth state while speaking: open/closed flapping on 2s (stop-motion replacement mouths), 'closed' outside t0..t1."""
    if t < t0 or t > t1: return 'closed'
    k = int((t - t0) * rate); h = hash01('talk', seed, k)
    return 'open' if h > 0.62 else ('oh' if h > 0.42 else 'closed')
def wobble(t, f=1.0, a=1.0, ph=0.0): return a * math.sin(2 * math.pi * f * t + ph)
def path_at(C, s, d):
    """Point and unit tangent at distance d along the sampled polyline C (cumulative lengths s)."""
    d = clamp(d, 0.0, s[-1] - 1e-6); i = int(np.searchsorted(s, d)); i = max(1, min(i, len(C) - 1))
    u = (d - s[i - 1]) / max(1e-9, s[i] - s[i - 1]); p = C[i - 1] + (C[i] - C[i - 1]) * u; tg = C[i] - C[i - 1]; tg = tg / np.linalg.norm(tg)
    return p, tg
def yaw_of(dx, dy): return math.degrees(math.atan2(-dx, dy))      # facing +Y = 0, facing -X = 90, +X = -90

SAND_RIM = None
SHOTS = []
import json
try: HITS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cues.json')))['strong_hits']
except Exception: HITS = []
def hit_env(t, decay=0.22):
    """0..1 pulse after each strong music hit (the lamps and glows breathe on the score's hits)."""
    e = 0.0
    for h in HITS:
        if 0.0 <= t - h < decay * 3: e = max(e, math.exp(-(t - h) / decay))
        elif h > t: break
    return e
WHY = {}
def shot(t0, t1, name='', why='', scene=0):
    """A shot is cut for a written reason (WHY); `scene` is its scene number in SCENES (NOTES.md prints both)."""
    def deco(fn):
        SHOTS.append((snapt(t0), snapt(t1), name or fn.__name__, fn)); WHY[name or fn.__name__] = (why, scene); return fn
    return deco

class Ctx:
    """Per-pose context handed to a shot."""
    def __init__(self, S, bpy, t):
        self.S, self.bpy, self.t = S, bpy, t
        self.cam = dict(pos=(0, -1, 0.3), tgt=(0, 0, 0.1), lens=35.0, fstop=5.6, focus=None, roll=0.0)
        self.lt = dict(moon=0.55, az=-35.0, el=24.0, moon_k=9500.0, fill=0.10, fill_k=8000.0, fill_off=(-0.25, 0.0, 0.25), amb=0.30, exposure=0.0, dawn=0.0,
                       stars=1.0, moon_vis=1.0, sky_em=0.9)
    def camera(self, pos, tgt, lens=35.0, fstop=5.6, focus=None, roll=0.0): self.cam = dict(pos=tuple(pos), tgt=tuple(tgt), lens=lens, fstop=fstop, focus=focus, roll=roll)
    def light(self, **kw): self.lt.update(kw)

def hide_all(S):
    for k in ('fig',):
        for f in S[k].values(): f.hide(True)
    for f in S['listeners']: f.hide(True)
    for c in S['camel'].values(): c.hide(True)
    for t in [S['t1'], S['t2']] + S['camp']: t.hide(True)
    for l in S['lamps'] + S['lamps_nl']: l.pose((0, 0, -5), 0.0)
    for r in S['ropes']: r.ob.hide_render = True
    for o in S['props_all']: hide(o, True)
    for st in S['stamps']: st.hide_render = True
    S['hud_on'] = False
    for hd in S['hud'].values():
        hd['root'].hide_render = True
        for o in hd['objs']: o.hide_render = True
        for L in hd['lines']:
            L.root.hide_render = True
            for o, x, u in L.items: o.hide_render = True
    S['field'].hide_all()
    S['fire_on'] = []
    for nm in ('fire1', 'fire2', 'fire3'): S[nm].hide(True)
    for g in S['goats']: g.hide(True)
    for p in S['fgpalms']: p.hide(True)
    for o in S['walls']: o.hide_render = True
    S['moon'].hide_render = False
    for L_ in (S['title'], S['title_sub']):
        for it in L_.items: it[0].hide_render = True
    for g in S['tiles']:
        for it in g[1].items: it[0].hide_render = True

# ------------------------------------------------------------------------------------------------ props
def bowl_mesh(bpy, name, mat, coll, r=0.0175, h=0.010, seed=1):
    prof = [(0.0, 0.0), (0.45 * r, 0.0004), (0.80 * r, 0.0035), (1.0 * r, h * 0.95), (0.97 * r, h), (0.88 * r, h * 0.94), (0.68 * r, h * 0.45), (0.36 * r, h * 0.22), (0.0, h * 0.19)]
    rings = [(z, rr, rr) for (rr, z) in prof]
    v, f = loft_z(rings, 24, False, False)
    return mk(bpy, name, v, f, mat, coll, None, noise_amp=0.0003, seed=seed)

def build_props(bpy, ctx, S, M, coll):
    PA = S['props_all'] = []
    def reg(o): PA.append(o); return o
    S['camp'] = []
    for k, (x, y) in enumerate(W.CAMP):
        t = A.Tent(bpy, f'camp{k}', coll, M, True, 20 + k); t.root.scale = (0.62, 0.62, 0.62); S['camp'].append(t)
        for o in t.sil.values(): o.hide_render = True
    # bowls
    S['bowls'] = []
    for k in range(7):
        r = reg(pivot(bpy, f'bowl{k}', coll)); b = bowl_mesh(bpy, f'bowl{k}_m', M['bowl'], coll, r=0.0175 if k < 5 else 0.011, seed=k); b.parent = r
        dt = ellipsoid(bpy, f'bowl{k}_dates', (0.008, 0.008, 0.004), M['dates'], coll, seg=12, rings=8); dt.parent = r; dt.location = (0, 0, 0.0045); S.setdefault('bowl_dates', []).append(dt)
        S['bowls'].append(r)
    r = reg(pivot(bpy, 'milkbowl', coll)); b = bowl_mesh(bpy, 'milkbowl_m', M['bowl'], coll, r=0.020, h=0.012, seed=9); b.parent = r
    ml = ellipsoid(bpy, 'milk_surface', (0.0152, 0.0152, 0.0013), M['milk'], coll, seg=20, rings=6); ml.parent = r; ml.location = (0, 0, 0.0075); S['milkbowl'] = r
    S['thorn'] = reg(P.thorn_bush(bpy, coll, M['thorn'], 3, 16, 0.075)); S['thorn2'] = reg(P.thorn_bush(bpy, coll, M['thorn'], 8, 12, 0.055))
    # footprint stamps (shared mesh)
    sm = P.stamp_data(bpy, 'stamp', 0.0075, 0.0135); sm.materials.append(M['stamp_rim']); sm.materials.append(M['stamp_in'])
    S['stamps'] = []
    for k in range(44):
        o = bpy.data.objects.new(f'stamp{k}', sm); coll.objects.link(o); o.hide_render = True; S['stamps'].append(o)
    # staff for the old man, pouch, cushions
    pts = [(0, 0, 0), (0.001, 0, 0.040), (0.0, 0.001, 0.080), (-0.004, 0.001, 0.100)]
    S['staff'] = reg(tube(bpy, 'staff', pts, [0.0028, 0.0027, 0.0025, 0.0033], M['pole'], coll, n=14, ring=8, lateral=(0, 1, 0)))
    pr = reg(pivot(bpy, 'pouch', coll)); pb = ellipsoid(bpy, 'pouch_m', (0.0085, 0.0070, 0.0095), M['pouch'], coll, seg=18, rings=10, noise_amp=0.0004, seed=3); pb.parent = pr; pb.location = (0, 0, 0.0095)
    pt = ellipsoid(bpy, 'pouch_tie', (0.0045, 0.0045, 0.0022), M['pouch'], coll, seg=12, rings=6); pt.parent = pr; pt.location = (0, 0, 0.0200); S['pouch'] = pr
    S['cushions'] = []
    for k in range(3):
        cu = reg(ellipsoid(bpy, f'cushion{k}', (0.030, 0.026, 0.0075), M['rug'] if k != 1 else M['goat'], coll, seg=24, rings=10, noise_amp=0.0006, seed=70 + k)); S['cushions'].append(cu)
    # scroll with marks (o3) and the verse scroll (g2)
    S['scroll'] = build_scroll(bpy, coll, M, reg, marks=True)
    S['verse'] = build_scroll(bpy, coll, M, reg, marks=False)
    # number tiles
    S['tiles'] = []
    for k, num in enumerate(('30', '96', '360', '400')):
        r = reg(pivot(bpy, f'tile{k}', coll)); rings = [(0.0, 0.058, 0.0125), (0.006, 0.060, 0.0135), (0.060, 0.058, 0.0135), (0.066, 0.052, 0.0120), (0.070, 0.040, 0.009)]
        v, f = loft_z(rings, 4 * 10, True, True)
        slab = mk(bpy, f'tile{k}_slab', v, f, M['tile'], coll, r, noise_amp=0.0007, seed=80 + k)
        txt = P.Lettering(bpy, f'num{k}', coll, num, 0.044, M['num'], per='word', extrude=0.006, bevel=0.0018); txt.root.parent = r
        txt.root.location = (0, -0.0120, 0.030); S['tiles'].append((r, txt))
    # title lettering in the dunes (letters pop in), HUD texts set in build_hud
    S['title'] = P.Lettering(bpy, 'title', coll, 'DARK CORNERS', 0.040, M['letters'], per='letter', extrude=0.010, bevel=0.0022)
    S['title_sub'] = P.Lettering(bpy, 'title_sub', coll, 'I Am Buying Her Life', 0.0205, M['letters'], per='word', extrude=0.006, bevel=0.0014)
    S['title_lamp'] = None
    pl = reg(pivot(bpy, 'plinth', coll)); v, f = loft_z([(-0.012, 0.205, 0.0125), (0.0, 0.208, 0.0135), (0.010, 0.208, 0.0135), (0.150, 0.208, 0.0135), (0.158, 0.200, 0.0125), (0.162, 0.186, 0.0105)], 4 * 12, True, True)
    mk(bpy, 'plinth_slab', v, f, M['tile'], coll, pl, noise_amp=0.0009, seed=9); S['plinth'] = pl
    # lamp field: ~400 lamps scattered across the clay desert, nearest the centre first
    def field_pts(n):
        rs = np.random.RandomState(3); pts = []
        tries = 0
        while len(pts) < n and tries < 200000:
            tries += 1; x = rs.uniform(-3.7, 3.7); y = rs.uniform(0.55, 3.7)
            if abs(x) < 0.45 and 0.30 < y < 0.95: continue
            if min([math.hypot(x - a, y - b) for a, b, _ in pts] or [9]) < 0.085: continue
            pts.append((x, y, 0.0))
        pts.sort(key=lambda p: math.hypot(p[0] - 0.3, (p[1] - 1.1) * 1.2))
        return [(x, y, float(W.terrain_h(np.array(x), np.array(y)))) for x, y, _ in pts]
    S['field'] = P.LampField(bpy, coll, M['lampclay'], M['flame'], field_pts, [8, 22, 66, 264, 40])
    # Mecca
    S['houses'] = []
    for k, (x, y, w, d, h, wi, dr) in enumerate(W.MECCA_HOUSES):
        root, door = P.build_house(bpy, f'house{k}', coll, M, w=w, d=d, h=h, seed=100 + k, door=dr, windows=wi); root.location = (x, y, gz(x, y)); S['houses'].append((root, door))
        reg(root)
    # far cards for Mecca
    S['mecca_far'] = [W.cut_dunes(bpy, coll, M['paper_far'][k], f'mecca_far{k}', y, 5.5, 18.0, base, amp, 40 + k) for k, (y, base, amp) in enumerate(((4.18, 0.22, 0.40), (4.44, 0.34, 0.42)))]

def build_scroll(bpy, coll, M, reg, marks=True):
    r = reg(pivot(bpy, 'scroll' if marks else 'verse', coll)); S = {'root': r}
    wd, hg = (0.105, 0.26) if marks else (0.115, 0.20)
    rings = [(0.0, wd, 0.0035), (0.002, wd, 0.0045), (0.0075, wd, 0.0045), (0.009, wd, 0.0030)]
    # sheet as a loft along Z of a very flat ellipse => lay it upright: height along Z
    v, f = loft_z([(0.004, wd, 0.0030), (0.010, wd * 1.0, 0.0034), (hg - 0.010, wd, 0.0034), (hg, wd, 0.0030)], 36, True, True)
    S['sheet'] = mk(bpy, r.name + '_sheet', v, f, M['parch'], coll, r, noise_amp=0.0004, noise_freq=60.0, seed=5)
    for nm, z in (('top', hg + 0.004), ('bot', 0.0)):
        o = ellipsoid(bpy, f'{r.name}_rod_{nm}', (wd + 0.012, 0.0085, 0.0085), M['pole'], coll, seg=24, rings=10, noise_amp=0.0004, seed=7); o.parent = r; o.location = (0, 0, z)
        for sx in (-1, 1):
            kb = ellipsoid(bpy, f'{r.name}_knob_{nm}{sx}', (0.0065, 0.0065, 0.0065), M['pole'], coll, seg=12, rings=8); kb.parent = r; kb.location = (sx * (wd + 0.0175), 0, z)
    # stand: two small posts + base
    for sx in (-1, 1):
        o = tube(bpy, f'{r.name}_post{sx}', [(sx * (wd + 0.02), 0.012, -0.002), (sx * (wd + 0.02), 0.014, hg * 0.6), (sx * (wd + 0.02), 0.016, hg + 0.02)], [0.0035, 0.0032, 0.0030], M['pole'], coll, n=10, ring=8, lateral=(0, 1, 0)); o.parent = r
    S['marks'] = []
    if marks:
        rs = np.random.RandomState(19)
        for row in range(14):
            Vv, Ff = [], []; z = hg - 0.020 - row * 0.0155
            x = -wd + 0.014
            while x < wd - 0.014:
                ln = rs.uniform(0.004, 0.016) * (1 if rs.rand() > 0.2 else 0.5)
                if x + ln > wd - 0.012: break
                b = len(Vv)
                for q in range(2):
                    for j in range(6):
                        th = 2 * math.pi * j / 6; Vv.append((x + ln * q + 0.0014 * math.cos(th), -0.0042, z + 0.0014 * math.sin(th) + 0.0016 * (rs.rand() - 0.5)))
                for j in range(6): Ff.append((b + j, b + (j + 1) % 6, b + 6 + (j + 1) % 6, b + 6 + j))
                x += ln + rs.uniform(0.004, 0.009)
                if rs.rand() < 0.18: x += 0.012
            me = bpy.data.meshes.new(f'marks{row}'); me.from_pydata(Vv, [], Ff); me.update(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.materials.append(M['ink'])
            o = bpy.data.objects.new(f'marks{row}', me); coll.objects.link(o); o.parent = r; S['marks'].append(o)
        # stylus
        S['stylus'] = tube(bpy, 'stylus', [(0, 0, 0), (0.012, -0.004, 0.030), (0.024, -0.008, 0.062)], [0.0010, 0.0020, 0.0026], M['pole'], coll, n=10, ring=8, lateral=(0, 1, 0)); S['stylus'].parent = r
    else:
        S['lines'] = []
        for k, line in enumerate(('He gave life', 'to the', 'buried girl,', 'so she was', 'not buried.')):
            L = P.Lettering(bpy, f'verse{k}', coll, line, 0.0215, M['ink'], per='word', extrude=0.0035, bevel=0.0010, spacing=1.0)
            L.root.parent = r; L.root.location = (0, -0.0050, hg - 0.040 - k * 0.0285); S['lines'].append(L)
    return S

def card_mesh(bpy, name, w, h, mat, hs, seed=1, th=0.0036, rad=0.006):
    """A hand-cut paper card: rounded rectangle with a slightly wavering scissor edge, thick enough to catch light."""
    rs = np.random.RandomState(seed); pts = []; n = 72
    for k in range(n):
        a = 2 * math.pi * k / n; ca, sa = math.cos(a), math.sin(a); e = 0.16                               # superellipse rectangle
        x = (w / 2) * np.sign(ca) * abs(ca) ** e; y = (h / 2) * np.sign(sa) * abs(sa) ** e
        j = 1.0 + 0.004 * math.sin(k * 0.9 + seed) + 0.003 * math.sin(k * 2.3 + 1.7 * seed)
        pts.append((x * j, y * j))
    V = [(x, y, 0.0) for x, y in pts] + [(x, y, th) for x, y in pts] + [(0, 0, 0.0), (0, 0, th)]
    F = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)] + [(2 * n + 1, n + k, n + (k + 1) % n) for k in range(n)] + [(2 * n, (k + 1) % n, k) for k in range(n)]
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); hs.collection.objects.link(ob); set_vis(ob, True); return ob

def build_hud(bpy, ctx, S, M, coll):
    """Title cards: hand-cut paper with clay lettering, in their own tiny scene (no depth of field), alpha-composited over the picture."""
    hs = bpy.data.scenes.new('hud'); S['hud_scene'] = hs
    hs.render.engine = 'CYCLES'; hs.render.resolution_x = ctx['W']; hs.render.resolution_y = ctx['H']; hs.render.resolution_percentage = 100
    hs.render.film_transparent = True; hs.cycles.device = 'CPU'; hs.cycles.samples = 10; hs.cycles.use_denoising = False; hs.cycles.max_bounces = 2
    hs.cycles.seed = 0; hs.cycles.use_animated_seed = False
    hs.render.use_compositing = False
    hc = bpy.data.cameras.new('hudcam'); hc.lens = 35.0; hc.sensor_width = 36.0; hc.dof.use_dof = False
    ho = bpy.data.objects.new('hudcam', hc); hs.collection.objects.link(ho); hs.camera = ho; ho.location = (0, 0, 0)
    ld = bpy.data.lights.new('hudlight', 'AREA'); ld.energy = 3.2; ld.size = 0.4; lo = bpy.data.objects.new('hudlight', ld); hs.collection.objects.link(lo); lo.location = (-0.20, 0.25, 0.12)
    lo.rotation_euler = (math.radians(24), math.radians(-24), 0)
    wd = bpy.data.worlds.new('hudworld'); hs.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    bgn = wd.node_tree.nodes.get('Background')
    if bgn is not None: bgn.inputs['Strength'].default_value = 0.6
    paper_m = P.cream_letters(bpy, 'card_paper', (0.93, 0.85, 0.66), 0.62, seed=58)
    ink_m = clay(bpy, 'card_ink', (0.36, 0.15, 0.10), (0.30, 0.12, 0.08), rough=0.5, sss=0.05, seed=59)
    tape_m = clay(bpy, 'card_tape', (0.78, 0.64, 0.40), (0.70, 0.56, 0.34), rough=0.7, seed=60)
    S['hud'] = {}
    def card(name, lines, pad=0.020, per='word', seed=1, tilt=-2.0):
        """lines = [(text, size)]: one Lettering per line stacked on a paper card with tape and an ink rule."""
        root = pivot(bpy, 'hud_' + name, coll); coll.objects.unlink(root); hs.collection.objects.link(root); items = []; objs = []; widths = []; hts = []
        for k, (txt, size, pr) in enumerate(lines):
            L = P.Lettering(bpy, f'hud_{name}_{k}', coll, txt, size, ink_m, per=pr, extrude=0.0042, bevel=0.0009, plane='XY')
            for o in [L.root] + [it[0] for it in L.items]: coll.objects.unlink(o); hs.collection.objects.link(o)
            for o, x, u in L.items: set_vis(o, True)
            widths.append(L.width); hts.append(size * 1.18); items.append(L)
        w = max(widths) + 2 * pad; h = sum(hts) + 2 * pad * 0.9 + 0.006 * (len(lines) - 1)
        card_o = card_mesh(bpy, f'hud_{name}_card', w, h, paper_m, hs, seed=seed); card_o.parent = root; card_o.location = (0, 0, -0.0036)
        y = h / 2 - pad * 0.95
        for k, L in enumerate(items):
            y -= hts[k] * 0.5; L.root.parent = root; L.root.location = (0, y, 0.0004); y -= hts[k] * 0.5 + 0.006
        tp = card_mesh(bpy, f'hud_{name}_tape', 0.040, 0.0125, tape_m, hs, seed=seed + 7, th=0.0016); tp.parent = root; tp.location = (w * 0.30, h / 2 - 0.0035, 0.0); tp.rotation_euler = (0, 0, math.radians(-7))
        objs += [card_o, tp]
        if len(lines) > 1:
            rl = card_mesh(bpy, f'hud_{name}_rule', max(widths) * 0.62, 0.0017, ink_m, hs, seed=seed + 3, th=0.0030); rl.parent = root
            rl.location = (0, h / 2 - pad * 0.95 - hts[0] - 0.0035, 0.0); objs.append(rl)
        S['hud'][name] = dict(root=root, lines=items, objs=objs, w=w, h=h, tilt=tilt)
    card('place', [('ARABIA', 0.034, 'letter'), ('AROUND 600', 0.0185, 'word')], seed=1, tilt=-2.2)
    card('name', [('SASAA', 0.030, 'letter'), ('OF THE TAMIM TRIBE', 0.0125, 'word')], seed=2, tilt=1.8)
    card('mecca', [('MECCA', 0.034, 'letter'), ('ZAYD', 0.0150, 'letter')], seed=3, tilt=-1.6)
    card('end', [('DARK CORNERS', 0.0285, 'letter'), ('I Am Buying Her Life', 0.0172, 'word')], pad=0.024, seed=4, tilt=1.2)
    for nm, hd in S['hud'].items(): hd['root'].hide_render = True; [setattr(o, 'hide_render', True) for o in hd['objs']]
    # a shadow catcher behind the cards so they sit on the picture with a soft shadow
    cp = bpy.data.objects.new('hud_catcher', bpy.data.meshes.new('hud_catcher')); cp.data.from_pydata([(-0.5, -0.8, 0), (0.5, -0.8, 0), (0.5, 0.8, 0), (-0.5, 0.8, 0)], [], [(0, 1, 2, 3)]); cp.data.update()
    hs.collection.objects.link(cp); cp.location = (0, 0, -0.5 - 0.016)
    try: cp.is_shadow_catcher = True
    except Exception: pass
    S['hud_catcher'] = cp

def show_hud(S, name, t, t_on, t_off, y, d=0.5, x=0.0, stagger=0.11):
    """A paper card slides in from below, settles with a small overshoot (on 2s), letters pop in one by one, then it lifts out."""
    hd = S['hud'][name]; vis = t_on <= t < t_off; root = hd['root']
    for o in hd['objs']: o.hide_render = not vis
    root.hide_render = not vis
    for L in hd['lines']:
        L.root.hide_render = not vis
        if not vis:
            for o, xx, u in L.items: o.hide_render = True
    if not vis: return
    S['hud_on'] = True
    uin = clamp((t - t_on) / 0.55); e = 1 - (1 - uin) ** 3; over = 0.012 * math.sin(uin * math.pi * 2.0) * (1 - uin)
    uout = clamp((t - (t_off - 0.45)) / 0.45); eo = uout * uout
    yy = y * 36.0 * d / 35.0 - (1 - e) * 0.20 + over + eo * 0.22
    wob = 0.5 * math.sin(t * 1.7 + hd['w'] * 40.0)
    root.location = (x, yy, -d); root.rotation_euler = (0, 0, math.radians(hd['tilt'] * min(1.0, e + 0.2) + wob + 6.0 * (1 - e)))
    s = 1.0 - 0.10 * eo; root.scale = (s, s, s)
    for k, L in enumerate(hd['lines']):
        times = [t_on + 0.30 + 0.45 * k + stagger * i for i in range(len(L.items))]
        L.show(t=t, times=times, pop_s=0.30)
    if uout > 0.92:
        for o in hd['objs']: o.hide_render = True
        for L in hd['lines']:
            for o, xx, u in L.items: o.hide_render = True

# ------------------------------------------------------------------------------------------------ frame application
def render_pose(bpy, ctx, S, pf):
    from mathutils import Vector, Quaternion
    t = pf / 24.0
    hide_all(S)
    S['hit'] = hit_env(t); S['flame_base'] = 18.0
    sh = None
    for s in SHOTS:
        if s[0] <= t < s[1]: sh = s; break
    if sh is None: sh = SHOTS[-1]
    c = Ctx(S, bpy, t); c.sun = (-0.30, 4.80, 0.60); c.t0, c.t1, c.name = sh[0], sh[1], sh[2]; c.u = clamp((t - sh[0]) / max(1e-6, sh[1] - sh[0]))
    sh[3](c, t, c.u)
    import dress as Dz
    Dz.animate_dress(S, t, S['hit'], tuple(S['fire_on']), (0.9, 0.25))
    for tt, ph in [(S['t1'], 0.0), (S['t2'], 1.3)] + [(q, 0.7 * (k + 2)) for k, q in enumerate(S['camp'])]:
        if not tt.root.hide_render: tt.breathe(t, 1.0, ph)
    if getattr(c, 'drift', True):
        cs_ = c.cam; p_ = np.array(cs_['pos'], float); g_ = np.array(cs_['tgt'], float); ctr = p_ + 0.55 * (g_ - p_)
        S['drift'].ob.hide_render = False; S['drift'].animate(t, float(ctr[0]), float(ctr[1]))
    else: S['drift'].ob.hide_render = True
    if os.environ.get('KF_LT'): c.lt.update(eval(os.environ['KF_LT']))
    if os.environ.get('KF_CAM'): c.cam.update(eval(os.environ['KF_CAM']))
    # camera (+ per-pose hand jitter of the stand: +-0.4 mm, +-0.03 deg)
    cam, cd = S['cam'], S['camd']; cs = c.cam
    pos = Vector(cs['pos']) + Vector((jit(pf, 'cx', 0.0004), jit(pf, 'cy', 0.0004), jit(pf, 'cz', 0.0004)))
    pos.z = max(pos.z, gz(pos.x, pos.y) + 0.032)         # the stand never sinks into the sand
    tgt = Vector(cs['tgt']); cam.location = pos
    q = (tgt - pos).to_track_quat('-Z', 'Y')
    if cs['roll']: q = q @ Quaternion((0, 0, 1), math.radians(cs['roll']))
    cam.rotation_euler = q.to_euler()
    cd.lens = cs['lens']; cd.dof.aperture_fstop = cs['fstop']; cd.dof.focus_distance = max(0.05, (Vector(cs['focus'] if cs['focus'] is not None else cs['tgt']) - pos).length)
    bpy.context.view_layer.update()
    sk = S['skycam']; sk.location = cam.location; sk.rotation_euler = cam.rotation_euler; sk.data.lens = cd.lens      # the sky scene sees what the table camera sees, minus the depth of field
    # lights
    L = c.lt; sc = bpy.context.scene
    ml = S['moon_light']; az, el = math.radians(L['az']), math.radians(L['el'])
    pv = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))); ml.rotation_euler = (-pv).to_track_quat('-Z', 'Y').to_euler()
    ml.data.energy = L['moon']; ml.data.temperature = L['moon_k']
    f = S['fill']; R = cam.rotation_euler.to_matrix(); ox, oy, oz = L['fill_off']; f.location = pos + R @ Vector((ox, oy, oz))
    f.rotation_euler = (tgt - f.location).to_track_quat('-Z', 'Y').to_euler(); dd = max(0.2, (tgt - f.location).length)
    f.data.energy = L['fill'] * math.pi * dd * dd; f.data.temperature = L['fill_k']; f.data.size = max(0.3, 0.6 * dd)
    bg = S['world_bg']
    if bg is not None: bg.inputs['Strength'].default_value = L['amb']
    for dv in S['sky_dawn_nodes']: dv.outputs[0].default_value = L['dawn']
    S['sky_em'].inputs['Strength'].default_value = L['sky_em']
    for (st, base), tw in zip(S['stars_st'], S['stars_tw']): st.inputs[1].default_value = base * L['stars']; tw.outputs[0].default_value = t
    S['sky_bg_dawn'].outputs[0].default_value = L['dawn']
    S['sky_root'].location = (0.006 * t, 0.0, 0.0); S['ridge_dawn'].outputs[0].default_value = L['dawn']; W.place_caravan(S, t, L['dawn'])
    for (o, x0, z0) in S['wisps']: o.location = (x0 + 0.028 * t, o.location[1], z0 + 0.012 * math.sin(t * 0.05 + x0))
    mx_, mz_ = getattr(c, 'moon_pos', (-0.7, 2.15)); S['moon'].location = (mx_, 4.80, mz_); S['moon_halo'].location = (mx_, 4.82, mz_)
    S['moon'].hide_render = L['moon_vis'] < 0.5; S['moon_halo'].hide_render = L['moon_vis'] < 0.5
    sv = clamp((L['dawn'] - 0.12) / 0.5); S['sun'].hide_render = sv <= 0.0; S['sun_halo'].hide_render = sv <= 0.0
    S['sun_em'].inputs['Strength'].default_value = 6.0 * sv; S['sun_halo_em'].inputs['Strength'].default_value = 1.1 * sv
    sp = c.sun if hasattr(c, 'sun') else (-0.30, 4.80, 0.60)
    S['sun'].location = sp; S['sun_halo'].location = (sp[0], sp[1] + 0.004, sp[2])
    sc.view_settings.exposure = L['exposure']
    S['M']['flame_em'].inputs['Strength'].default_value = S['flame_base'] * (1.0 + 0.45 * S['hit'])

def fig_pose(f, x, y, yaw, **kw):
    f.hide(False); f.pose(loc=(x, y, gz(x, y)), yaw=yaw, **kw)

def lamp(S, k, x, y, z=None, on=1.0, flick_seed=0.0, t=0.0, power=1.0, lit=True, yaw=0.0, nl=False):
    pool = S['lamps_nl'] if nl else S['lamps']; l = pool[k]
    fl = (hash01('fl', flick_seed, int(t * 12)) - 0.5) * 2.0 if on > 0 else 0.0
    l.pose((x, y, (gz(x, y) if z is None else z)), on, fl + 1.5 * S.get('hit', 0.0), power, yaw)
    return l

def ride(S, cam_key, x, y, yaw, t, dist, fig='sasaa', amp=1.0, neck=(0, 0), moving=True, arm=(8, 4, 0), armL=(8, 4, 0), head=(0, 0, 0), mouth='closed', brow=(0, 0), seat=(0.0, -0.012, 0.186), lean=0.0):
    """Camel walking (gait phase from distance) with the rider seated on the saddle; returns the camel."""
    from mathutils import Matrix, Vector, Euler
    cm = S['camel'][cam_key]; cm.hide(False)
    cm.pose(loc=(x, y, gz(x, y)), yaw=yaw, gait=(dist / 0.13 if moving else None), neck=neck, amp=amp if moving else 0.0)
    l = cm.last; M = Matrix.LocRotScale(Vector(l['loc']), Euler((0, 0, D(l['yaw']))), Vector((l['sc'],) * 3)) @ Matrix.LocRotScale(Vector((0, 0, l['bob'])), Euler((D(l['pitch']), D(l['roll']), 0)), None)
    p = M @ Vector(seat); f = S['fig'][fig]; f.hide(False)
    f.pose(loc=(p.x, p.y, p.z), yaw=yaw, lean=l['pitch'] + lean, roll=l['roll'], seated=False, armR=arm, armL=armL, head=head, mouth=mouth, brow=brow)
    for ft in f.feet: ft.hide_render = True
    return cm

# ------------------------------------------------------------------------------------------------ the film: 9 scenes, 31 shots
# Every shot has a written reason (why=...) and every scene a place, a dramatic question, a beginning, a middle, an end and one camera plan.
SCENES = [
    dict(n=1, name='The night search', t0=0.0, t1=11.656, place='Sasaa\'s ridge above the camps, then the camel tracks (night, stars)',
         q='Who is out there at night, and what does he find?', beg='The sky: moon, stars, the dated card; a man shades his eyes on the ridge.',
         mid='He scans the valley of lamps; the camera follows his gaze down to the camel tracks.', end='The tracks lead to a far glow and a column of smoke: two tents.',
         cam='Tilt down from the stars with a slow dolly to Sasaa (one move); then a slider pan along the tracks to the glow.'),
    dict(n=2, name='The old records', t0=11.656, t1=18.94, place='A scribe\'s scroll in the dunes (lamp, ink pot)',
         q='Can this be believed?', beg='A dark scroll, a lamp.', mid='Rows of script are written in, line by line.', end='The title is raised in clay letters on a plinth.',
         cam='Slow push-in on the scroll; then a slow push to the title plinth.'),
    dict(n=3, name='The hard years', t0=18.94, t1=41.52, place='Sasaa\'s ridge and the families\' camp at the oasis',
         q='What was this world like for a newborn girl?', beg='Sasaa is named; his tribe and rank are on a paper name card.', mid='Hunger: dry thorn, empty bowls; one lamp alone in the sand.',
         end='A row of lit tents with figures in the cloth; one tent goes dark. "But it happened."',
         cam='A slow arc round Sasaa; a low slider past the thorn to the bowls; the camera slides from the lone lamp along the tents to the dark one.'),
    dict(n=4, name='The two tents', t0=41.52, t1=74.02, place='The two tents on the sand: the old man\'s and the woman\'s, a fire, camels and goats between',
         q='Boy or girl?', beg='Sasaa follows the tracks and finds two lit tents.', mid='The old man: your camels are safe, their milk kept us alive. A woman calls: she has given birth. The old man asks: boy or girl?',
         end='"It was a girl." The tent glows, held in silence.',
         cam='An orbit round the rider from the side to behind; a slow dolly and a push to the milk; a dolly toward the woman\'s tent; a push-in on the old man; static holds on the answers.'),
    dict(n=5, name='The price', t0=74.02, t1=98.85, place='The old man\'s rug, the fire, the camels',
         q='Will he sell her, and for what?', beg='Sasaa asks to buy her.', mid='The old man is insulted (a free man does not sell his children). Sasaa answers: I am buying her life.',
         end='Five camels, one by one, are handed over on ropes, the last the one he rode.', cam='Two-shot; slow pushes on each speaker; a wide dolly on the herd; a low angle on the last camel.'),
    dict(n=6, name='The promise', t0=98.85, t1=122.2, place='The dunes at night, then the field of lamps',
         q='What does he do with what he has lost?', beg='He walks home without a camel; his footprints behind him.', mid='He stops under the stars and promises; a lamp is lit for each girl, the numbers arrive on tiles.',
         end='"Every number was a girl": the camera moves through a field of lamps.', cam='Tracking walk, then a tilt up to the stars; a long crane down into the field; a dolly through the lamps.'),
    dict(n=7, name='Mecca', t0=122.2, t1=144.9, place='Mecca at night: clay houses, palms, a stall, a fire',
         q='Is he the only one?', beg='A lamp is lit in the dark; Zayd walks in; MECCA card.', mid='A father at his door; Zayd stands between him and his daughter: do not kill her, I will pay for her keep.',
         end='He raises her (she grows up behind three walls); "if you want her back, take her."', cam='A crane back to reveal the town; a slow push toward the two men; a lateral track behind low walls; a push to the three of them.'),
    dict(n=8, name='The poet', t0=144.9, t1=160.42, place='A poet\'s lamp-lit corner of the camp, listeners around him',
         q='What did the grandson say about his grandfather?', beg='A poet writes alone.', mid='The camera pulls back: he is famous, a crowd listens. One line is about his grandfather.',
         end='The verse is set in clay letters on a scroll.', cam='A pull-back slider with a small crane; a push on the poet\'s face; a slow crane up the scroll.'),
    dict(n=9, name='Dawn', t0=160.42, t1=175.84, place='The same desert at dawn, the field of lamps burning down',
         q='Who grew up?', beg='Dawn over the lamps: nobody knows how many.', mid='One girl walks up the dune.',
         end='The sun clears the ridge; end card.', cam='A slow crane over the lamps; a low tracking shot, then a crane up and away.'),
]

def sky_light(c, **kw): c.light(**kw)

def tents_lit(S, c, t, glow=2.2, p1=1.0, sil2=(), glow2=1.0):
    t1, t2 = S['t1'], S['t2']
    t1.show(); t2.show(sil=sil2)
    for tt, (x, y) in ((t1, W.TENT1), (t2, W.TENT2)): tt.root.location = (x, y, gz(x, y)); tt.root.rotation_euler = (0, 0, 0)
    t2.glow_em.inputs['Strength'].default_value = glow * glow2 * (1.0 + 0.04 * (hash01('t2g', int(t * 8)) - 0.5) + 0.12 * S.get('hit', 0.0))
    lx, ly, lz = t1.lamp_pos; x, y = W.TENT1
    return lamp(S, 0, x + lx, y + ly, gz(x, y) + lz, power=p1 * 1.0, flick_seed=1, t=t)

def camp_row(S, glow=2.0, dark=None, sil=None, t=0.0):
    for k, tt in enumerate(S['camp']):
        x, y = W.CAMP[k]; tt.show(sil=(sil or {}).get(k, ())); tt.root.location = (x, y, gz(x, y)); tt.root.rotation_euler = (0, 0, D((k * 37) % 17 - 8))
        g = glow * (0.04 if dark == k else 1.0) * (1.0 + 0.05 * (hash01('cg', k, int(t * 8)) - 0.5)); tt.glow_em.inputs['Strength'].default_value = g

def fire_on(S, nm): S['fire_on'].append(nm); S[nm].hide(False)

def goats_on(S, t, which=(0, 1), graze=1.0):
    for q in which:
        x, y, yaw = dz.GOAT_P[q % len(dz.GOAT_P)]; S['goats'][q].hide(False); S['goats'][q].pose(x, y, yaw + 8 * math.sin(t * 0.3 + q), t, graze, seed=q * 1.7)

def seats_on(S, t, n=3):
    """Three listeners sit round the families' fire (they look at it, now and then at each other)."""
    for k in range(n):
        x, y, yaw = dz.SEATS[k]; ls = S['listeners'][k]; ls.hide(False)
        ls.pose(loc=(x, y, gz(x, y)), yaw=yaw_of(dz.FIRE2[0] - x, dz.FIRE2[1] - y), seated=True, head=(6 * math.sin(t * 0.5 + k * 2.0), 3 + 2 * math.sin(t * 0.8 + k), 0), bob=0.0008 * math.sin(t * 1.2 + k))

def night(c, **kw):
    d = dict(moon=1.0, az=-105, el=28, moon_k=11000, fill=0.16, amb=0.30); d.update(kw); c.light(**d)

SX, SY = -1.85, 1.05          # the ridge where Sasaa stands with his camel (opening)

def sasaa_stand(S, t, x, y, yaw, head=(0, 0, 0), **kw):
    f = S['fig']['sasaa']; fig_pose(f, x, y, yaw, head=head, bob=wobble(t, 0.4, 0.0006), **kw); return f

def camel_stand(S, key, x, y, yaw, t, neck=(0, 0), **kw):
    c = S['camel'][key]; c.hide(False); c.pose(loc=(x, y, gz(x, y)), yaw=yaw, gait=None, neck=neck, **kw); return c

def cam_keys(t, keys, e='t'):
    """Camera keyframes [(t, pos, tgt), ...] with a steady-middle ease between each pair."""
    if t <= keys[0][0]: return keys[0][1], keys[0][2]
    for (t0, p0, g0), (t1, p1, g1) in zip(keys, keys[1:]):
        if t <= t1: u = ease((t - t0) / (t1 - t0), e); return lerp(p0, p1, u), lerp(g0, g1, u)
    return keys[-1][1], keys[-1][2]

import dress as dz

# ================================================================================================ SCENE 1: the night search
@shot(0.0, 6.6, 'A1_stars_to_ridge', scene=1, why='Opening: the sky and the date first (hook, place), then the man; one continuous tilt-and-dolly so the eye is led from the stars to Sasaa. Cut at 6.6 when the narration turns to "what he found".')
def A1(c, t, u):
    S = c.S
    k = ease(clamp((t - 0.9) / 3.8), 't')
    pos = ez(t, 0.0, 6.6, (-1.40, -0.10, 0.086), (-1.50, 0.30, 0.094), 't')
    fk = ease(clamp((t - 1.6) / 3.0), 's')
    tgt = (lerp(-0.95, SX + 0.13, k), lerp(4.8, SY, k), lerp(1.8, 0.105, k))
    c.camera(pos, tgt, lens=30.0, fstop=4.0, focus=(lerp(-0.8, SX, fk), lerp(4.8, SY, fk), lerp(1.0, 0.1, fk)))
    night(c, moon=0.9, az=-110, el=22, fill=0.14); c.moon_pos = (-0.80, 2.35)
    hy = ez(t, 2.4, 3.4, 40.0, -35.0, 's') if t < 5.0 else ez(t, 5.0, 5.8, -35.0, -10.0, 's')
    arm = (100.0, 10.0, 88.0)
    ar = ez(t, 2.0, 2.8, (8, 4, 0), arm) if t < 5.0 else ez(t, 5.0, 5.8, arm, (8, 4, 0))
    sasaa_stand(S, t, SX, SY, -150.0, head=(hy, 3, 0), armR=ar, mouth='closed', brow=(0.4, 3))
    camel_stand(S, 'ride', SX + 0.24, SY + 0.10, -105.0, t, neck=(wobble(t, 0.25, 8), 4))
    camp_row(S, 2.0, t=t); fire_on(S, 'fire2'); seats_on(S, t)
    show_hud(S, 'place', t, 0.9, 5.9, 0.30)

@shot(6.6, 11.656, 'A2_tracks_to_glow', scene=1, why='New information at the turn of the narration ("what he found that night"): the tracks he follows lead to a glow. The slider pan carries the eye from the prints to the far tents and their smoke.')
def A2(c, t, u):
    S = c.S; night(c, moon=0.9, az=-160, el=14, fill=0.10)
    pos, tgt = cam_keys(t, [(6.6, (-3.55, 2.45, 0.075), (-2.75, 2.58, 0.040)), (11.656, (-2.85, 2.05, 0.150), (1.10, 1.70, 0.120))])
    foc = (-3.0, 2.62, 0.03) if t < 9.0 else ez(t, 9.0, 10.8, (-3.0, 2.62, 0.03), (1.45, 1.55, 0.12), 's')
    c.camera(pos, tgt, lens=30.0, fstop=3.2, focus=foc)
    tents_lit(S, c, t, glow=1.6 + 1.6 * ez(t, 8.0, 9.0, 0.0, 1.0), p1=0.0)
    S['lamps'][0].pose((0, 0, -5), 0.0); fire_on(S, 'fire1'); camp_row(S, 1.6, t=t)

# ================================================================================================ SCENE 2: the old records
def scribe_set(S, t):
    pass

@shot(11.656, 16.6, 'A3_the_scroll', scene=2, why='A change of place and register: the "old Arabic records" become an object we can read. Rows of script are set in step with the narration; the push-in is the viewer leaning in to read.')
def A3(c, t, u):
    S = c.S; night(c, moon=0.30, az=-120, el=30, fill=0.06, amb=0.25)
    sx, sy = 0.00, 0.35; scr = S['scroll']; r = scr['root']; hide(r, False); r.location = (sx, sy, gz(sx, sy)); r.rotation_euler = (0, 0, D(-8)); r.scale = (1.0, 1.0, 1.0)
    n = len(scr['marks']); rows_t = [11.45 + 0.37 * k for k in range(n)]
    for k, o in enumerate(scr['marks']): o.hide_render = t < rows_t[k]
    scr['stylus'].hide_render = True
    lamp(S, 0, sx - 0.16, sy - 0.12, power=1.0, t=t, flick_seed=3)
    pos, tgt = cam_keys(t, [(11.656, (-0.24, -0.18, 0.070), (0.0, 0.35, 0.085)), (16.6, (0.08, -0.14, 0.120), (0.0, 0.35, 0.130))])
    c.camera(pos, tgt, lens=40.0, fstop=3.5, focus=(sx, sy, 0.10)); c.moon_pos = (-0.70, 2.20)

@shot(16.6, 18.94, 'A4_title', scene=2, why='The promise of the film is paid here: the title is raised in clay on a plinth right after the records line ends (hold on silence), before the first name.')
def A4(c, t, u):
    S = c.S; night(c, moon=0.8, az=-95, el=24, fill=0.14); c.moon_pos = (-0.95, 2.15)
    x, y = 0.0, 0.95; z0 = gz(x, y)
    pl = S['plinth']; hide(pl, False); pl.location = (x, y, z0)
    ti = S['title']; ti.root.location = (x, y - 0.0165, z0 + 0.098); ts = S['title_sub']; ts.root.location = (x, y - 0.0150, z0 + 0.050)
    ti.show(t=t, times=[16.8 + 0.07 * k for k in range(len(ti.items))], pop_s=0.35); ts.show(t=t, times=[17.75, 17.95, 18.15, 18.3, 18.45], pop_s=0.3)
    lamp(S, 0, x - 0.17, y - 0.20, power=1.0, t=t, flick_seed=2)
    pos, tgt = cam_keys(t, [(16.6, (0.00, 0.02, 0.105), (0.0, y, z0 + 0.078)), (18.94, (0.01, 0.14, 0.108), (0.0, y, z0 + 0.078))])
    c.camera(pos, tgt, lens=35.0, fstop=4.5, focus=(x, y - 0.015, z0 + 0.078))

# ================================================================================================ SCENE 3: the hard years
@shot(18.94, 25.4, 'B1_sasaa_named', scene=3, why='A man needs a name: Sasaa is named ("His name was Sasaa") and ranked ("a nobleman of the Tamim tribe") on a paper card. One slow arc round him lets the camp and the oasis show behind; no cut inside the sentence.')
def B1(c, t, u):
    S = c.S; night(c, moon=0.7, az=-120, el=24, fill=0.20); c.moon_pos = (-1.10, 2.30)
    pos, tgt = cam_keys(t, [(18.94, (SX - 0.30, SY - 0.50, 0.095), (SX + 0.02, SY, 0.118)), (25.4, (SX + 0.06, SY - 0.36, 0.115), (SX, SY, 0.118))])
    c.camera(pos, tgt, lens=40.0, fstop=3.5, focus=(SX, SY, 0.115))
    look = ez(t, 22.0, 23.0, 12.0, -6.0, 's')
    nod = -5.0 * math.sin(clamp((t - 20.7) / 0.9) * math.pi) if t > 20.7 else 0.0
    sasaa_stand(S, t, SX, SY, 190.0, head=(ez(t, 19.6, 20.4, 18.0, 0.0) if t < 21.9 else look, nod + 2.0, 0), armR=(8, 5, 0), armL=(14, 6, 0), mouth='closed', brow=(0.3, 5), blink=blink_at(t, [19.9, 21.6, 23.3]))
    camel_stand(S, 'ride', SX + 0.22, SY + 0.18, -140.0, t, neck=(wobble(t, 0.2, 10), 3))
    camp_row(S, 2.2, t=t); lamp(S, 0, SX + 0.10, SY - 0.16, power=0.9, t=t, flick_seed=1); fire_on(S, 'fire2'); seats_on(S, t)
    show_hud(S, 'name', t, 19.4, 24.9, 0.27)

HX, HY = -0.60, 2.55         # the hunger corner: a thorn, a rug of empty bowls, in front of the families' tents
@shot(25.4, 33.7, 'C1_hunger', scene=3, why='Change of place and scale: from the man to what hunger looks like. A low slider passes dry thorn (foreground), empty bowls (middle) and the lit tents (far) so the scene explains "one more mouth" with objects, not words. A bowl is filled on "mouth" (33.4).')
def C1(c, t, u):
    S = c.S; night(c, moon=0.5, az=-105, el=22, fill=0.10, amb=0.25); c.moon_pos = (-1.2, 2.30)
    hide(S['thorn'], False); S['thorn'].location = (HX - 0.30, HY - 0.10, gz(HX - 0.30, HY - 0.10)); S['thorn'].rotation_euler = (0, 0, 0.4); S['thorn'].scale = (1.5, 1.5, 1.5)
    hide(S['thorn2'], False); S['thorn2'].location = (HX + 0.28, HY + 0.10, gz(HX + 0.28, HY + 0.10)); S['thorn2'].rotation_euler = (0, 0, 1.9); S['thorn2'].scale = (1.4, 1.4, 1.4)
    n = 5 + (1 if t >= 32.6 else 0)
    spots = [(-0.075, -0.05), (0.075, -0.05), (-0.085, 0.07), (0.085, 0.07), (0.0, -0.095), (0.0, 0.0)]
    for k in range(n):
        b = S['bowls'][k]; hide(b, False); x, y = HX + spots[k][0], HY + spots[k][1]
        b.location = (x, y, gz(x, y) - 0.001); pop = 1.0 if k < 5 else (0.6 + 0.4 * ease(clamp((t - 32.6) / 0.25), 'o') if t >= 32.6 else 0.0)
        b.scale = (pop, pop, pop); S['bowl_dates'][k].hide_render = (k >= 2 and k < 5) or k == 5
        if k < 2: S['bowl_dates'][k].scale = (0.6, 0.6, 0.5)
    lamp(S, 1, HX, HY + 0.03, power=0.9, t=t, flick_seed=5)
    camp_row(S, 2.0, t=t); fire_on(S, 'fire2'); seats_on(S, t)
    pos, tgt = cam_keys(t, [(25.4, (HX - 0.72, HY - 0.46, 0.050), (HX - 0.30, HY - 0.02, 0.060)), (33.7, (HX - 0.18, HY - 0.30, 0.075), (HX, HY, 0.030))])
    c.camera(pos, tgt, lens=36.0, fstop=3.0, focus=(HX - 0.20, HY, 0.05) if t < 30.0 else (HX, HY, 0.02))

LX, LY = -0.30, 2.52
@shot(33.7, 41.52, 'C2_lamp_to_tents', scene=3, why='"Some buried her alive" is not shown: one lamp alone in the sand (held on the line), then at "Not every family" the camera slides off it along the lit tents. Silhouettes in the cloth are the families; one tent goes dark on "But it happened" (the hit at 39.68).')
def C2(c, t, u):
    S = c.S; night(c, moon=0.55, az=-110, el=22, fill=0.10, amb=0.25); c.moon_pos = (-1.4, 2.40)
    sil = {0: ('head', 'veil', 'body'), 2: ('head', 'veil', 'body', 'arm', 'bundle', 'bhead'), 4: ('head', 'veil', 'body'), 3: ('head', 'veil', 'body')}
    dim = ez(t, 39.9, 40.8, 1.0, 0.0, 's')
    for k, tt in enumerate(S['camp']):
        x, y = W.CAMP[k]; tt.show(sil=sil.get(k, ()) if (k != 3 or dim > 0.3) else ()); tt.root.location = (x, y, gz(x, y)); tt.root.rotation_euler = (0, 0, D((k * 37) % 17 - 8))
        tt.glow_em.inputs['Strength'].default_value = 2.5 * ((0.03 + 0.97 * dim) if k == 3 else 1.0) * (1.0 + 0.05 * (hash01('cg', k, int(t * 8)) - 0.5))
    lamp(S, 0, LX, LY, power=1.4, t=t, flick_seed=7)
    fire_on(S, 'fire2'); seats_on(S, t)
    c34 = W.CAMP[3]
    pos, tgt = cam_keys(t, [(33.7, (LX - 0.10, LY - 0.34, 0.045), (LX, LY, 0.030)), (36.9, (LX - 0.08, LY - 0.30, 0.045), (LX, LY, 0.030)), (41.52, (-1.85, 2.18, 0.080), (c34[0] - 0.02, c34[1], 0.085))])
    c.camera(pos, tgt, lens=34.0, fstop=3.0, focus=(LX, LY, 0.025) if t < 38.0 else (c34[0], c34[1] - 0.1, 0.07))

TC, TS = W.spline_pts(W.TRACK_PTS, 0.01)
def track_pos(d, off=0.14):
    p, tg = path_at(TC, TS, d); n = np.array([-tg[1], tg[0]])
    q = p - n * off
    return q, tg

# ================================================================================================ SCENE 4: the two tents
OLD_P, SAS_P = (1.30, 1.36), (0.98, 1.30)
@shot(41.52, 49.11, 'E_follow_to_tents', scene=4, why='Arrival as one move: a lateral track beside the rider on the tracks (41.5), the camera swings behind him as he crests (46.2, on the hit "Late at night"), he stops and points at the two tents (47.7); the fire and its smoke tell us people are there.')
def E(c, t, u):
    S = c.S; night(c, moon=0.9, az=-115, el=22, fill=0.14); c.moon_pos = (-0.6, 2.2)
    stop = 47.7
    d = 2.7 + 0.245 * (min(t, stop) - 41.52) if t < 46.16 else 3.837 + 0.27 * (min(t, stop) - 46.16)
    q, tg = track_pos(d); yaw = yaw_of(tg[0], tg[1]); moving = t < stop
    point = ez(t, 47.7, 48.3, 0.0, 1.0, 'o')
    ride(S, 'ride', q[0], q[1], yaw, t, d, moving=moving, arm=(10 + 76 * point, 6, 14 * (1 - point)), head=(wobble(t, 0.5, 8) * (1 - point) - 8 * point, 2 + point, 0), neck=(0, 2 + 6 * point), brow=(0.6 * point, 3 * point))
    # camera: beside the rider, then (46.2 to 47.7) round to behind and a little above
    dx, dy = float(tg[0]), float(tg[1]); k = ez(t, 45.4, 47.4, 0.0, 1.0, 's')
    side = (q[0] + 0.02, q[1] - 0.74, 0.095); behind = (q[0] - dx * 0.46 - dy * 0.06, q[1] - dy * 0.46 + dx * 0.06, 0.20)
    pos = lerp(side, behind, k)
    tg_side = (q[0] + 0.01, q[1], 0.130); tg_beh = (q[0] + 0.50 * (1.55 - q[0]), q[1] + 0.50 * (1.62 - q[1]), 0.13)
    c.camera(pos, lerp(tg_side, tg_beh, k), lens=lerp(32.0, 28.0, k), fstop=3.8, focus=(q[0], q[1], 0.12) if t < 47.7 else (1.6, 1.65, 0.1))
    fl = ez(t, 47.7, 48.2, 0.0, 1.0)
    tents_lit(S, c, t, glow=2.0 + 2.4 * fl, p1=1.0 + 1.0 * fl); camp_row(S, 2.0, t=t); fire_on(S, 'fire1'); goats_on(S, t, (0, 1)); fire_on(S, 'fire2'); seats_on(S, t)

def camp_actors(S, t, camels=True):
    if camels:
        camel_stand(S, 'she1', 0.58, 1.60, -80.0, t, neck=(wobble(t, 0.2, 6), 2)); camel_stand(S, 'she2', 0.78, 1.82, -95.0, t, neck=(wobble(t, 0.17, 6, 1.0), 0))
        camel_stand(S, 'calf1', 0.40, 1.45, -60.0, t); camel_stand(S, 'calf2', 0.30, 1.70, -110.0, t)
        camel_stand(S, 'ride', 0.45, 1.02, -70.0, t, neck=(wobble(t, 0.15, 6), 0))

@shot(49.11, 57.95, 'F_old_man_milk', scene=4, why='The old man gives two facts, the camels are safe and their milk kept the family alive. A slow dolly shows both men and the camels behind (they are the proof); from 54.6 the camera lowers and pushes to the milk bowl at his feet (a change of scale to the detail the line names).')
def F(c, t, u):
    S = c.S; night(c, moon=0.35, az=-105, el=24, fill=0.09, amb=0.25); c.moon_pos = (-0.4, 2.3)
    tents_lit(S, c, t, glow=2.0, p1=1.2)
    old = S['fig']['old']; k = ez(t, 49.6, 50.6, 0.0, 1.0, 's'); pt = ez(t, 52.9, 53.6, 0.0, 1.0, 'o'); mk_ = ez(t, 54.4, 55.2, 0.0, 1.0, 's')
    mx, my = 1.22, 1.24; hide(S['milkbowl'], False); S['milkbowl'].location = (mx, my, gz(mx, my))
    yaw = 180.0 + 8 * k if t < 52.0 else lerp(150.0, 190.0, mk_) if t >= 52.0 else 188.0
    fig_pose(old, OLD_P[0] + 0.02 * mk_, OLD_P[1] + 0.04 * mk_, 180.0 + 8 * k if t < 52.0 else lerp(150.0, 190.0, mk_), lean=(14.0 - 4 * k) if t < 52.0 else lerp(10.0, 20.0, mk_),
             head=((-6 * (1 - k), -4 + 6 * k, 0) if t < 52.0 else (ez(t, 52.0, 53.0, 0, 20, 's') * (1 - mk_) + (-5) * mk_, -12 * mk_, 0)),
             armR=((32, 6, 70) if t < 52.0 else (32 + 40 * pt * (1 - mk_) + (18 - 32) * mk_, 8 + 14 * pt * (1 - mk_) + 4 * mk_, 60 - 40 * pt * (1 - mk_) - 40 * mk_)), armL=(10 + 26 * mk_, 6 + 8 * mk_, 30 * mk_),
             mouth=talk(t, 49.2, 50.9, 5.0, 1.0) if t < 51.9 else talk(t, 52.0, 57.5, 5.0, 2.0), brow=(0.2, -3 - 3 * mk_), blink=blink_at(t, [50.3, 56.6]))
    hide(S['staff'], False); S['staff'].location = (OLD_P[0] + 0.020, OLD_P[1] - 0.030, gz(*OLD_P)); S['staff'].rotation_euler = (D(-6), 0, 0)
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], -75.0 if t < 52.0 else lerp(-75.0, -50.0, ez(t, 52.0, 52.9, 0, 1)), head=(10 + 30 * pt, 1 + 2 * pt, 0), mouth='closed', brow=(0.3 + 0.2 * pt, 4))
    camp_actors(S, t); fire_on(S, 'fire1'); goats_on(S, t, (0, 1)); camp_row(S, 2.0, t=t)
    pos, tgt = cam_keys(t, [(49.11, (1.12, 0.92, 0.100), (1.25, 1.40, 0.095)), (54.0, (1.20, 1.00, 0.108), (OLD_P[0] + 0.005, OLD_P[1], 0.112)), (57.95, (1.06, 0.96, 0.080), (mx + 0.03, my + 0.05, 0.075))], 't')
    c.camera(pos, tgt, lens=36.0, fstop=3.2, focus=(OLD_P[0], OLD_P[1], 0.10) if t < 54.4 else (mx + 0.02, my + 0.02, 0.04))

W_DP = A.Tent.DP + 0.0058
def tent2_lamp(S, t, power=1.0): return lamp(S, 2, 2.28, 1.585, power=power, t=t, flick_seed=9)

@shot(57.95, 63.37, 'G_woman_calls', scene=4, why='A voice from elsewhere, so the camera turns with the men toward it and moves to the woman\'s tent; the birth is a silhouette appearing in the cloth at 61.9 ("She had just given birth") and the camera is allowed to settle on it.')
def G(c, t, u):
    S = c.S; night(c, moon=0.30, az=-105, el=24, fill=0.06, amb=0.22); c.moon_pos = (-0.2, 2.2)
    appear = t >= 61.9; call = 0.5 + 0.5 * math.sin((t - 58.6) * 2 * math.pi * 1.6) if 58.6 < t < 60.4 else 0.0
    sil = ('head', 'veil', 'body', 'arm', 'bundle', 'bhead') if appear else ('head', 'veil', 'body', 'arm')
    pk = ez(t, 61.9, 62.3, 0.0, 1.0, 'o')
    tents_lit(S, c, t, glow=2.3, p1=0.8, sil2=sil, glow2=1.0 + 0.5 * ez(t, 58.6, 58.9, 0.0, 1.0) + (0.25 * pk if appear else 0.0))
    ar = S['t2'].sil['arm']; ar.rotation_euler = (0, D(35 - 55 * call), 0); ar.location = (-0.0065 - 0.004 * call, -W_DP, 0.044 + 0.012 * call)
    for nm in ('bundle', 'bhead'):
        o = S['t2'].sil[nm]; s = (0.55 + 0.45 * pk) if appear else 1.0; o.scale = (s, 1.0, s)
    tent2_lamp(S, t, 0.8 + (0.5 * pk if appear else 0.0))
    turn = ez(t, 58.6, 59.5, 0.0, 1.0, 's')
    fig_pose(S['fig']['sasaa'], 1.86, 1.22, 180.0 + 139.0 * turn, head=(0, 0, 0), mouth='closed', brow=(0.4, 4))
    fig_pose(S['fig']['old'], 2.02, 1.18, 180.0 + 151.0 * turn, lean=10.0, head=(0, 0, 0), mouth='closed')
    hide(S['staff'], False); S['staff'].location = (2.045, 1.15, gz(2.02, 1.18)); S['staff'].rotation_euler = (0, 0, 0)
    fire_on(S, 'fire1'); goats_on(S, t, (0, 1)); camp_row(S, 2.0, t=t)
    pos, tgt = cam_keys(t, [(57.95, (1.78, 0.52, 0.090), (2.05, 1.40, 0.090)), (60.7, (2.02, 0.72, 0.092), (2.28, 1.72, 0.088)), (63.37, (2.26, 1.00, 0.088), (2.33, 1.74, 0.075))], 't')
    c.camera(pos, tgt, lens=32.0, fstop=3.5, focus=(2.35, 1.7, 0.08) if t > 60.0 else (1.95, 1.2, 0.09))

def dialog_light(c, S, t, *, lamp_xy, p=1.0):
    night(c, moon=0.25, az=-110, el=22, fill=0.20, fill_k=4200, amb=0.22); c.moon_pos = (-0.4, 2.3)
    tents_lit(S, c, t, glow=2.2, p1=1.0, sil2=('head', 'veil', 'body', 'arm', 'bundle', 'bhead'))
    S['t2'].sil['arm'].rotation_euler = (0, D(35), 0)
    lamp(S, 2, lamp_xy[0], lamp_xy[1], power=p, t=t, flick_seed=11)
    fire_on(S, 'fire1')

def old_cu(S, t, yaw=165.0, lean=6.0, head=(0, 0, 0), arm=(30, 8, 60), mouth='closed', brow=(0, -4), armL=(10, 6, 0), blink=0.0):
    fig_pose(S['fig']['old'], OLD_P[0], OLD_P[1], yaw, lean=lean, head=head, armR=arm, armL=armL, mouth=mouth, brow=brow, blink=blink)
    hide(S['staff'], False); S['staff'].location = (OLD_P[0] + 0.022, OLD_P[1] - 0.030, gz(*OLD_P)); S['staff'].rotation_euler = (0, 0, 0)

@shot(63.37, 71.0, 'H_boy_or_girl', scene=4, why='The question is the whole film, so it gets one long uninterrupted face: the old man asks, the camera creeps in (4 % a second). The fire at his side and a lamp light his eyes; nothing else moves.')
def H(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(OLD_P[0] - 0.07, OLD_P[1] - 0.09), p=1.1 if t < 69.4 else 0.7)
    if t < 66.0: yaw, lean, head, arm, brow = 172.0, 5.0, (ez(t, 63.3, 64.2, -10, 4, 's'), 2 - 4 * math.sin(clamp((t - 64.6) / 1.0) * math.pi), 0), (26, 8, 70), (0.7 * ez(t, 64.5, 64.9, 0, 1), -5)
    elif t < 69.41:
        ch = ez(t, 67.6, 68.4, 0.0, 1.0, 's'); yaw, lean, head, arm, brow = 150.0, 4.0, (ez(t, 66.0, 67.0, 10, -8, 's'), 3, 0), (24 + 20 * ch, 6, 78 - 20 * ch), (0.4, -4)
    else: yaw, lean, head, arm, brow = 178.0, 2.0, (0, 0, 0), (14, 8, 8), (0.0, -12)
    yaw = lerp(172.0, 150.0, ez(t, 65.6, 66.4, 0, 1, 's')) if 65.6 <= t < 66.4 else (lerp(150.0, 178.0, ez(t, 69.0, 69.9, 0, 1, 's')) if 69.0 <= t < 69.9 else yaw)
    old_cu(S, t, yaw=yaw, lean=lean, head=head, arm=arm, mouth=talk(t, 63.5, 71.4, 6.0, 5.0 + int(t > 66.0)), brow=brow, blink=blink_at(t, [64.2, 67.3, 70.2]))
    fig_pose(S['fig']['sasaa'], SAS_P[0] - 0.08, SAS_P[1] - 0.02, -70.0, head=(0, 0, 0))
    goats_on(S, t, (0,)); camp_actors(S, t, camels=False)
    pos, tgt = cam_keys(t, [(63.37, (OLD_P[0] + 0.07, OLD_P[1] - 0.34, 0.100), (OLD_P[0] - 0.004, OLD_P[1], 0.104)), (71.0, (OLD_P[0] + 0.0, OLD_P[1] - 0.25, 0.094), (OLD_P[0], OLD_P[1], 0.100))], 't')
    c.camera(pos, tgt, lens=42.0, fstop=4.2, focus=(OLD_P[0], OLD_P[1] - 0.014, 0.104))

@shot(71.0, 72.214, 'H4_reaction', scene=4, why='Reaction: cut to Sasaa on "bury her" so we see the words land on him (a reaction needs more than 24 frames; held to the hit at 72.214).')
def H4(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(SAS_P[0] + 0.08, SAS_P[1] - 0.08), p=0.9)
    k = ez(t, 71.0, 71.5, 0.0, 1.0, 'o')
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], 180.0 - 18.0, head=(-4, -2 + 2 * k, 0), mouth='closed', brow=(0.6 * k, -6 * k), blink=blink_at(t, [71.9], 0.14))
    pos = (SAS_P[0] + 0.06, SAS_P[1] - 0.30, 0.108); tgt = (SAS_P[0], SAS_P[1], 0.112)
    c.camera(pos, tgt, lens=42.0, fstop=4.2, focus=(SAS_P[0], SAS_P[1] - 0.014, 0.112))

@shot(72.214, 74.02, 'I_it_was_a_girl', scene=4, why='The answer is given to the tent, not to a face: the camera holds on the woman\'s tent, glowing, with a slow breath in the silhouette. The hold after the key line is the scene\'s end.')
def I_(c, t, u):
    S = c.S; night(c, moon=0.15, az=-105, el=24, fill=0.02, amb=0.18); c.moon_pos = (0.0, 2.3)
    tents_lit(S, c, t, glow=2.6, p1=0.6, sil2=('head', 'veil', 'body', 'arm', 'bundle', 'bhead'))
    S['t2'].sil['arm'].rotation_euler = (0, D(35), 0)
    br = 1.0 + 0.03 * math.sin((t - 72.214) * 2 * math.pi * 0.8)
    for nm in ('bundle', 'bhead'): S['t2'].sil[nm].scale = (br, 1.0, br)
    tent2_lamp(S, t, 0.9); fire_on(S, 'fire1'); camp_row(S, 1.8, t=t)
    pos, tgt = cam_keys(t, [(72.214, (2.30, 0.98, 0.080), (2.34, 1.74, 0.070)), (74.02, (2.33, 1.10, 0.082), (2.34, 1.74, 0.070))], 't')
    c.camera(pos, tgt, lens=36.0, fstop=3.2, focus=(2.35, 1.7, 0.07))

# ================================================================================================ SCENE 5: the price
@shot(74.02, 77.16, 'J1_asked_to_buy', scene=5, why='Two people, one question: a two-shot so we see both faces and the distance between them while Sasaa asks to buy her; the old man turns away at the end of the sentence.')
def J1(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(1.15, 1.18), p=1.2)
    p = ez(t, 75.4, 76.2, 0.0, 1.0, 'o')
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], -65.0, lean=4.0 * p, head=(ez(t, 74.0, 74.8, 0, -12, 's'), 2, 0), armR=(30 + 40 * p, 14 + 14 * p, 40 - 8 * p), armL=(8, 6, 0), mouth=talk(t, 74.2, 76.6, 6.0, 12.0), brow=(0.4, 2), blink=blink_at(t, [75.0]))
    old_cu(S, t, yaw=115.0, lean=8.0, head=(ez(t, 75.8, 76.6, 0, 10, 's'), 2, 0), arm=(34, 8, 66), mouth='closed', brow=(0.0, -3))
    goats_on(S, t, (0,)); camp_actors(S, t, camels=False)
    pos, tgt = cam_keys(t, [(74.02, (1.17, 0.50, 0.100), (1.14, 1.33, 0.100)), (77.16, (1.15, 0.60, 0.102), (1.14, 1.33, 0.100))], 't')
    c.camera(pos, tgt, lens=34.0, fstop=4.0, focus=(1.14, 1.33, 0.1))

@shot(77.16, 83.75, 'J2_free_man', scene=5, why='The old man\'s insult and his principle are one thought ("A free man does not sell his children"), so one shot: the camera arcs from his right to his left while his face hardens. Cut only after "children".')
def J2(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(OLD_P[0] - 0.07, OLD_P[1] - 0.09), p=1.0)
    k = ez(t, 77.8, 78.6, 0.0, 1.0, 'o')
    if t < 80.4: yaw, lean, head, arm, mouth, brow = 172.0 - 12 * k, 12.0 * (1 - k) - 2.0 * k, (0, 6 * k, 0), (40 + 40 * k, 8 + 8 * k, 56 - 36 * k), ('closed' if t < 78.8 else talk(t, 78.8, 80.3, 6.0, 15.0)), (0.9 * k, -16 * k)
    else: yaw, lean, head, arm, mouth, brow = 168.0, -2.0, (ez(t, 80.4, 82.0, -8, 6, 's'), 6, 0), (46 + 14 * math.sin((t - 80.4) * 5), 10, 48), talk(t, 80.5, 83.3, 6.0, 16.0), (0.8, -14)
    if t >= 80.4: yaw = lerp(160.0, 168.0, ez(t, 80.4, 81.0, 0, 1))
    old_cu(S, t, yaw=yaw, lean=lean, head=head, arm=arm, mouth=mouth, brow=brow, blink=blink_at(t, [82.0]))
    S['staff'].rotation_euler = (D(-6 - 8 * k) if t < 80.4 else D(-14), 0, 0)
    camp_actors(S, t, camels=False)
    pos, tgt = cam_keys(t, [(77.16, (OLD_P[0] + 0.05, OLD_P[1] - 0.33, 0.098), (OLD_P[0], OLD_P[1], 0.104)), (83.75, (OLD_P[0] - 0.08, OLD_P[1] - 0.25, 0.106), (OLD_P[0], OLD_P[1], 0.108))], 't')
    c.camera(pos, tgt, lens=42.0, fstop=4.2, focus=(OLD_P[0], OLD_P[1] - 0.014, 0.105))

@shot(83.75, 91.95, 'K_buying_her_life', scene=5, why='The title line. Sasaa answers; the camera has been moving in on his face since the old man\'s refusal and now pushes to its closest. The long pause before "I am buying her life" is held, not covered.')
def K(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(SAS_P[0] + 0.07, SAS_P[1] - 0.09), p=0.9 if t < 88.2 else 0.8)
    br = math.sin((t - 83.75) * 2 * math.pi * 0.25) * 1.0; hand = ez(t, 89.0, 89.5, 0.0, 1.0, 'o')
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], lerp(180.0 - 14.0, 180.0, ez(t, 87.8, 88.8, 0, 1)), bob=0.0008 * br, head=(ez(t, 83.75, 86.5, 8, -2, 's') * (1 - ez(t, 87.8, 88.4, 0, 1)), 1 + 0.8 * br + 3 * ez(t, 89.4, 90.2, 0.0, 1.0), 0),
             armR=(10 + 30 * hand, 5 + 13 * (1 - hand), 92 * hand), armL=(8, 6, 0), mouth=talk(t, 85.6, 87.6, 4.0, 20.0) if 85.6 < t < 88.0 else (talk(t, 88.4, 91.2, 5.5, 21.0) if t >= 88.4 else 'closed'), brow=(0.3, 3 if t < 88.2 else -1), blink=blink_at(t, [85.2, 91.5]))
    goats_on(S, t, (0,)); camp_actors(S, t, camels=False)
    pos, tgt = cam_keys(t, [(83.75, (SAS_P[0] + 0.11, SAS_P[1] - 0.36, 0.100), (SAS_P[0], SAS_P[1], 0.112)), (91.95, (SAS_P[0] + 0.00, SAS_P[1] - 0.22, 0.106), (SAS_P[0], SAS_P[1], 0.112))], 't')
    c.camera(pos, tgt, lens=42.0, fstop=4.2, focus=(SAS_P[0], SAS_P[1] - 0.016, 0.112))

ANIMALS = [('she1', 92.45, 0), ('she2', 93.75, 1), ('calf1', 94.95, 2), ('calf2', 95.75, 3), ('ride', 97.0, 4)]
LPOS = {'she1': (0.60, 1.52, -100.0), 'she2': (0.60, 1.28, -80.0), 'calf1': (0.74, 1.66, -95.0), 'calf2': (0.72, 1.12, -85.0), 'ride': (0.36, 1.40, -92.0)}

def bump(t, a, b, c_):
    if t <= a or t >= c_: return 0.0
    return smoothstep3((t - a) / (b - a)) if t < b else 1.0 - smoothstep3((t - b) / (c_ - b))

def price_scene(c, t, S):
    from mathutils import Vector
    dialog_light(c, S, t, lamp_xy=(1.15, 1.16), p=1.2)
    old, sas = S['fig']['old'], S['fig']['sasaa']
    reach = 0.0; take = 0.0
    for (nm, tt, k) in ANIMALS:
        reach = max(reach, bump(t, tt - 0.45, tt, tt + 0.30)); take = max(take, bump(t, tt - 0.12, tt + 0.12, tt + 0.55))
    fig_pose(sas, SAS_P[0], SAS_P[1], -65.0, lean=3.0 * reach, head=(0, 2, 0), armR=(8 + 62 * reach, 6 + 8 * reach, 18 + 10 * reach), armL=(10 + 30 * reach, 6, 24), mouth='closed', brow=(0.2, 5))
    old_cu(S, t, yaw=115.0, lean=4.0, head=(0, 2, 0), arm=(10 + 62 * take, 6 + 6 * take, 22 + 14 * take), mouth='closed', brow=(0.0, 0), armL=(10, 6, 0))
    for (nm, tt, k) in ANIMALS:
        x, y, yaw = LPOS[nm]; camel_stand(S, nm, x, y, yaw, t, neck=(wobble(t, 0.2, 5, k), 2))
    bpy = S['bpy']; bpy.context.view_layer.update()
    hs = {'sas': sas.hand['R'].matrix_world.translation.copy(), 'sasL': sas.hand['L'].matrix_world.translation.copy(), 'old': old.hand['R'].matrix_world.translation.copy()}
    for (nm, tt, k) in ANIMALS:
        cm = S['camel'][nm]; hp = (cm.headp.matrix_world @ Vector((0, 0.020, -0.004)))
        start = hs['sas'] if k % 2 == 0 else hs['sasL']
        end = hs['old']; tgt = start if t < tt else end
        S['ropes'][k].set(hp, tgt, sag=0.012, visible=True)

@shot(91.95, 96.502, 'L1_herd_handed_over', scene=5, why='The price is a list, so the picture is a list: two pregnant camels, then their calves, each roped and handed over on its word. One wide slow dolly lets the herd gather in frame.')
def L1(c, t, u):
    S = c.S; price_scene(c, t, S)
    pos, tgt = cam_keys(t, [(91.95, (1.04, 0.62, 0.105), (1.03, 1.34, 0.100)), (96.502, (0.98, 0.76, 0.098), (1.00, 1.34, 0.095))], 't')
    c.camera(pos, tgt, lens=24.0, fstop=4.5, focus=(1.0, 1.33, 0.1)); goats_on(S, t, (0,))

@shot(96.502, 98.85, 'L3_the_riding_camel', scene=5, why='The last camel is the one he rode: a change of angle and scale (low, close) on the hit at 96.502 because this is the cost to him. Held to the end of the line.')
def L3(c, t, u):
    S = c.S; price_scene(c, t, S)
    pos, tgt = cam_keys(t, [(96.502, (0.80, 0.52, 0.125), (0.78, 1.34, 0.095)), (98.85, (0.90, 0.58, 0.130), (0.90, 1.34, 0.095))], 't')
    c.camera(pos, tgt, lens=22.0, fstop=4.5, focus=(0.8, 1.35, 0.1))

# ================================================================================================ SCENE 6: the promise
HOME_PTS = [(1.0, 1.05), (0.45, 0.88), (-0.25, 0.72), (-1.0, 0.74), (-1.7, 0.98), (-2.3, 1.22)]
HC, HS = W.spline_pts(HOME_PTS, 0.01)
STAMP_STEP = 0.085
def stamps_along(S, C, Sd, d_now, count, lat=0.011, first=0.0):
    for k in range(min(count, len(S['stamps']))):
        dk = first + k * STAMP_STEP
        o = S['stamps'][k]
        if dk > d_now - 0.04: o.hide_render = True; continue
        p, tg = path_at(C, Sd, dk); n = np.array([-tg[1], tg[0]]); side = 1 if k % 2 else -1; q = p + n * lat * side
        o.hide_render = False; o.location = (q[0], q[1], gz(q[0], q[1])); o.rotation_euler = (0, 0, D(yaw_of(tg[0], tg[1]) + 3.0 * side))

STOP_S = 0.78
@shot(98.85, 105.094, 'M1_walk_home_promise', scene=6, why='One take for "walked home without them" and "that night he made a promise": a tracking shot beside him (footprints behind), he stops at the end of the walk (101.4), and the camera lowers and tilts up past him to the stars as the promise is made. The tilt is the vow.')
def M1(c, t, u):
    S = c.S; night(c, moon=0.9, az=-100, el=24, fill=0.12, amb=0.28); c.moon_pos = (-0.35, 2.30)
    d = min(0.27 * (t - 98.85), STOP_S); p, tg = path_at(HC, HS, d); yaw = yaw_of(tg[0], tg[1]); moving = d < STOP_S - 1e-6
    k = ez(t, 102.3, 103.4, 0.0, 1.0, 's')
    if moving: fig_pose(S['fig']['sasaa'], p[0], p[1], yaw, step=(d / 0.17), bob=0.0015 * abs(math.sin(d / 0.17 * math.pi * 2)), lean=2.5, head=(0, -3, 0), armR=(12 * math.sin(d / 0.17 * 6.28), 4, 6), armL=(-12 * math.sin(d / 0.17 * 6.28), 4, 6), mouth='closed', brow=(-0.2, 3))
    else: fig_pose(S['fig']['sasaa'], p[0], p[1], lerp(yaw, 8.0, k), head=(0, -6 + 28 * k, 0), armR=(8 + 14 * k, 6, 64 * ez(t, 103.4, 104.0, 0.0, 1.0, 'o')), armL=(8, 6, 0), mouth='closed', brow=(0.5 * k, 3))
    stamps_along(S, HC, HS, d + (0.1 if not moving else 0.0), 40)
    tents_lit(S, c, t, glow=2.0, p1=0.8); fire_on(S, 'fire1')
    a = ez(t, 100.8, 102.6, 0.0, 1.0, 's')
    pos = lerp((p[0] - 0.12, p[1] - 0.62, 0.080), (p[0] - 0.04, p[1] - 0.34, 0.062), a) if True else None
    walk_tgt = (p[0] + 0.14, p[1] + 0.02, 0.095); sky_tgt = ez(t, 101.8, 105.094, (p[0] + 0.02, p[1] + 1.2, 0.16), (p[0] - 0.12, p[1] + 1.6, 0.30), 's')
    tgt = lerp(walk_tgt, sky_tgt, a)
    c.camera(pos, tgt, lens=lerp(32.0, 30.0, a), fstop=lerp(3.5, 3.2, a), focus=(p[0], p[1], 0.10))

@shot(105.094, 108.878, 'M3_a_lamp_for_each', scene=6, why='"Every girl he heard of, he would save": the promise becomes a lamp, then another, then the first of a field. The camera drifts round him slowly so each lamp lights in a new part of the frame.')
def M3(c, t, u):
    S = c.S; night(c, moon=0.8, az=-100, el=26, fill=0.10, amb=0.28); c.moon_pos = (-0.4, 2.3)
    p, tg = path_at(HC, HS, STOP_S)
    fig_pose(S['fig']['sasaa'], p[0], p[1], 20.0, head=(-12, 4, 0), armR=(40, 8, 70), armL=(8, 6, 0), mouth='closed', brow=(0.3, 5), blink=blink_at(t, [106.4]))
    stamps_along(S, HC, HS, STOP_S + 0.1, 40)
    offs = [(-0.10, 0.12, 105.5), (0.12, 0.08, 106.2), (-0.03, 0.26, 106.95), (0.10, 0.27, 107.5)]
    for k, (ox, oy, tt) in enumerate(offs):
        x, y = p[0] + ox, p[1] + oy; on = ez(t, tt, tt + 0.25, 0.0, 1.0, 'o')
        if k == 0: lamp(S, 3, x, y, on=on, power=1.6, t=t, flick_seed=20 + k)
        else: lamp(S, k - 1, x, y, on=on, power=1.0, t=t, flick_seed=20 + k, nl=True)
    S['field'].show(t, [107.7, 1e9, 1e9, 1e9, 1e9])
    pos, tgt = cam_keys(t, [(105.094, (p[0] - 0.02, p[1] - 0.30, 0.060), (p[0] + 0.02, p[1] + 0.20, 0.090)), (108.878, (p[0] + 0.05, p[1] - 0.26, 0.070), (p[0] + 0.02, p[1] + 0.42, 0.045))], 't')
    c.camera(pos, tgt, lens=34.0, fstop=3.0, focus=(p[0], p[1], 0.10))

TILE_X = [(-0.17, 0.66), (-0.057, 0.60), (0.057, 0.60), (0.17, 0.66)]
TILE_T = [113.0, 113.8, 115.05, 117.38]
def tiles_show(S, t):
    for k, (r, txt) in enumerate(S['tiles']):
        tt = TILE_T[k]
        if t < tt: continue
        hide(r, False); x, y = TILE_X[k]; r.location = (x, y, gz(x, y) - 0.002); r.rotation_euler = (0, 0, D((k - 1.5) * 4.0))
        a = clamp((t - tt) / 0.4); s = 0.78 * (1.0 if a >= 1 else (0.5 + 0.7 * smoothstep3(a / 0.6) if a < 0.6 else 1.2 - 0.2 * smoothstep3((a - 0.6) / 0.4)))
        r.scale = (s, s, s); txt.show(t=t, times=[tt + 0.1]); txt.root.hide_render = False
        if txt.items: txt.items[0][0].hide_render = False

FIELD_T = [107.7, 113.0, 113.85, 115.1, 117.45]
@shot(108.878, 119.397, 'N_records_cannot_agree', scene=6, why='Scale change on the hit at 108.878: from one man to a whole field. One long crane down (high and wide = understanding the count) lands low beside the tiles as each number arrives (30, 96, 360, 400) and the field grows with it.')
def N(c, t, u):
    S = c.S; night(c, moon=0.9, az=-100, el=26, fill=0.12, amb=0.30); c.moon_pos = (-0.4, 2.3)
    S['field'].show(t, FIELD_T); tiles_show(S, t)
    p, tg = path_at(HC, HS, STOP_S); fig_pose(S['fig']['sasaa'], p[0], p[1], 20.0, head=(0, 5, 0)) if t < 113.0 else None
    stamps_along(S, HC, HS, STOP_S + 0.1, 40)
    pos, tgt = cam_keys(t, [(108.878, (0.22, -0.62, 0.55), (-0.2, 1.4, 0.04)), (113.0, (0.08, -0.40, 0.36), (-0.1, 1.15, 0.04)), (119.397, (0.0, 0.02, 0.105), (0.0, 0.70, 0.072))], 't')
    c.camera(pos, tgt, lens=28.0, fstop=4.0 if t < 113.0 else 3.5, focus=(0.0, 1.2, 0.05) if t < 113.0 else (0.0, 0.62, 0.07))
    fire_on(S, 'fire1')

@shot(119.397, 122.2, 'N3_every_number_a_girl', scene=6, why='The sentence changes the numbers into people: the camera leaves the tiles and moves into the lamps at lamp height; focus pulls from the tiles to the field. Held in silence to the end of the scene.')
def N3(c, t, u):
    S = c.S; night(c, moon=0.7, az=-100, el=26, fill=0.12, amb=0.28); c.moon_pos = (-0.4, 2.3)
    S['field'].show(t, FIELD_T); tiles_show(S, t)
    pos, tgt = cam_keys(t, [(119.397, (0.0, 0.10, 0.105), (0.0, 0.70, 0.075)), (122.2, (0.0, 0.34, 0.095), (0.0, 1.70, 0.050))], 't')
    c.camera(pos, tgt, lens=28.0, fstop=lerp(8.0, 3.5, smoothstep3(clamp((t - 120.2) / 1.2))), focus=(0.0, lerp(0.60, 1.5, smoothstep3(clamp((t - 120.2) / 1.2))), 0.06))

# ================================================================================================ SCENE 7: Mecca
def mecca_scene(S, t, lit=(0, 1, 2, 3, 4, 5, 6, 7), door_on=1.0, fire=True, fgp=False):
    for k, (root, door) in enumerate(S['houses']):
        hide(root, False)
        for ch in root.children:
            if ch.name.startswith(f'house{k}_win') and 'fr' not in ch.name: ch.hide_render = k not in lit
        if door is not None: door.hide_render = door_on < 0.5
    if fire: fire_on(S, 'fire3')
    for p in S['fgpalms']: p.hide(not fgp)

def mecca_light(c, **kw):
    c.light(moon=0.7, moon_vis=1.0, az=-100, el=26, fill=0.26, fill_k=5200, amb=0.42, **kw); c.moon_pos = (9.55, 2.55)

@shot(122.2, 128.7, 'O_not_alone_mecca', scene=7, why='A change of place the story needs us to feel: one lamp is lit (the same gesture as Sasaa\'s) and the camera cranes back and up to reveal a whole town; Zayd walks in and turns to us as the MECCA card lands. A crane because the information is scale.')
def O(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    on = ez(t, 122.55, 122.85, 0.0, 1.0, 'o'); lx, ly = 9.00, 1.20
    lamp(S, 0, lx, ly, on=on, power=1.8, t=t, flick_seed=30); lamp(S, 1, 8.40, 1.60, power=1.2 * ez(t, 124.0, 124.6, 0, 1), t=t, flick_seed=32, on=ez(t, 124.0, 124.6, 0, 1))
    zx = ez(t, 122.9, 124.3, 9.62, 9.18, 's') if t < 124.6 else 9.18
    k = ez(t, 126.0, 126.9, 0.0, 1.0, 's'); zx = lerp(zx, 9.00, ez(t, 124.3, 126.0, 0, 1, 's'))
    d = 9.62 - zx
    moving = 122.9 < t < 126.0
    fig_pose(S['fig']['zayd'], zx, 1.30 - 0.10 * ez(t, 124.3, 126.0, 0, 1, 's'), 90.0 + 90.0 * k, step=(d / 0.17 if moving else None), head=(ez(t, 126.0, 127.0, 20, 0, 's') if t > 125.8 else 0.0, 2, 0),
             armR=(10 * math.sin(d / 0.17 * 6.28) if moving else 8, 4, 6 if moving else 0), armL=(-10 * math.sin(d / 0.17 * 6.28) if moving else 8, 4, 6 if moving else 0), mouth='closed', brow=(0.3, 4), blink=blink_at(t, [127.4]))
    S['fig']['zayd'].hide(t < 122.9)
    pos, tgt = cam_keys(t, [(122.2, (8.92, 0.72, 0.062), (9.05, 1.25, 0.065)), (124.0, (8.94, 0.62, 0.075), (9.05, 1.45, 0.080)), (128.7, (8.88, 0.10, 0.205), (9.02, 1.65, 0.105))], 't')
    c.camera(pos, tgt, lens=34.0, fstop=3.0 if t < 124.5 else 4.5, focus=(lx, ly, 0.02) if t < 124.5 else (9.0, 1.3, 0.09))
    show_hud(S, 'mecca', t, 124.2, 128.2, 0.31)

FA_X, FA_Y = 9.00, 2.22
@shot(128.7, 137.392, 'P_zayd_and_the_father', scene=7, why='One push toward what matters: from the wide (a father at his door, Zayd coming) to the two men and the pouch of payment. The father turns on "Zayd told him"; the pouch passes on "I will pay"; the camera keeps moving in, never cutting inside the exchange.')
def P_exchange(c, t, u):
    from mathutils import Vector
    S = c.S; mecca_light(c); mecca_scene(S, t)
    lamp(S, 0, 8.55 if t < 131.3 else 9.20, 1.55 if t < 131.3 else 1.50, power=1.0 if t < 131.3 else 1.6, t=t, flick_seed=33)
    zf, ff = S['fig']['zayd'], S['fig']['father']
    walk = ez(t, 128.7, 132.0, 0.0, 1.0, 't'); zx = lerp(8.30, 8.80, walk); d = zx - 8.30; moving = t < 132.0
    ph = ez(t, 132.85, 133.35, 0.0, 1.0, 'o'); ex = ez(t, 135.2, 135.9, 0.0, 1.0, 'o')
    zyaw = lerp(-75.0, -70.0, ez(t, 132.0, 133.0, 0, 1)); zy = lerp(1.80, 1.90, walk)
    fig_pose(zf, zx, zy, zyaw, step=(d / 0.17 if moving else None), head=(0, 2, 0),
             armR=((10 * math.sin(d / 0.17 * 6.28), 4, 6) if moving else (10 + 70 * ph * (1 - ex) + 62 * ex, 10 + 10 * ph * (1 - ex) + 8 * ex, 20 + 70 * ph * (1 - ex) + (24 + 22 * ex - 20) * ex)),
             armL=(8, 4, 0) if not moving else (-10 * math.sin(d / 0.17 * 6.28), 4, 6), mouth=talk(t, 131.7, 136.9, 6.0, 40.0) if t > 131.6 else 'closed', brow=(0.7 * ph, 3 * ph + 2) if t > 131.6 else (0.0, 6), blink=blink_at(t, [132.6, 136.3]))
    turn = ez(t, 131.5, 132.3, 0.0, 1.0, 's')
    fig_pose(ff, lerp(FA_X - 0.03, 9.06, turn), lerp(FA_Y, 1.98, turn), lerp(0.0, 110.0, turn), head=(ez(t, 131.5, 132.3, 0, -10, 's') + (ez(t, 135.0, 136.4, 0, 8, 's') if t > 135.0 else 0.0), (-14 + 10 * turn) + (-6 * ex), 0),
             armR=(6 + 30 * ez(t, 136.2, 136.8, 0, 1, 's'), 6, 20), armL=(6, 4, 0), mouth='closed', brow=(-0.3 * turn, -6))
    S['bpy'].context.view_layer.update()
    if t > 135.0:
        hp = zf.hand['R'].matrix_world.translation; po = S['pouch']; hide(po, False); po.location = (hp.x, hp.y - 0.001, hp.z - 0.012); po.rotation_euler = (0, 0, 0)
    pos, tgt = cam_keys(t, [(128.7, (8.62, 1.22, 0.085), (9.0, 2.35, 0.075)), (131.31, (8.72, 1.32, 0.090), (9.0, 2.22, 0.085)), (133.0, (9.22, 1.46, 0.102), (8.84, 1.93, 0.104)), (134.95, (9.06, 1.48, 0.100), (8.88, 1.94, 0.100)), (137.392, (8.92, 1.50, 0.094), (8.92, 1.94, 0.096))], 't')
    fcs = (FA_X - 0.03, FA_Y, 0.08) if t < 131.3 else ((8.80, 1.90, 0.104) if t < 134.95 else (8.92, 1.94, 0.096))
    c.camera(pos, tgt, lens=lerp(30.0, 40.0, ez(t, 131.0, 134.0, 0, 1, 's')), fstop=3.5 if t < 131.3 else 3.2, focus=fcs)

def zayd_girl(S, t, x, y, yaw, d, gscale, step=True):
    zf, gf = S['fig']['zayd'], S['fig']['girl']; ph = d / 0.17
    fig_pose(zf, x, y, yaw, step=ph if step else None, bob=0.0014 * abs(math.sin(ph * math.pi * 2)), head=(0, 0, 0), armR=(10 * math.sin(ph * 6.28), 4, 6), armL=(8, 26, 8), mouth='closed', brow=(0.2, 4))
    rx, ry = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    gx, gy = x - rx * (0.060 + 0.012 * gscale), y - ry * (0.060 + 0.012 * gscale)
    fig_pose(gf, gx, gy, yaw, step=ph if step else None, scale=gscale, bob=0.0014 * abs(math.sin(ph * math.pi * 2 + 1.0)), head=(0, 0, 0), armR=(-10 * math.sin(ph * 6.28), 40, -4), armL=(10 * math.sin(ph * 6.28), 4, 6), mouth='closed', brow=(0.1, 3))

WALL_X = (9.14, 8.84)
@shot(137.392, 143.058, 'Q_raised_and_grown', scene=7, why='Years pass in one walk: Zayd and the girl cross the street behind two low walls that sweep through the frame; she is smaller before each wall and taller after it, so time passes without a dissolve or a visible jump. The camera tracks with them at their pace.')
def Q(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t, fire=True)
    lamp(S, 0, 8.55, 1.50, power=1.2, t=t, flick_seed=37)
    d = 0.21 * (t - 137.392); x = 9.60 - d
    gs = 1.0 if x > WALL_X[0] else (1.28 if x > WALL_X[1] else 1.58)
    for o, wx in zip(S['walls'], WALL_X): o.hide_render = False; o.location = (wx, 0.86, gz(wx, 0.86) - 0.004)
    zayd_girl(S, t, x, 1.10, 90.0, d, gs)
    pos = (x - 0.05, 0.47, 0.078); tgt = (x - 0.04, 1.10, 0.092)
    c.camera(pos, tgt, lens=34.0, fstop=3.2, focus=(x, 1.10, 0.09))

@shot(143.058, 144.9, 'Q3_take_her', scene=7, why='On the hit at 143.058 we are at the door: the three of them in one frame (Zayd, the grown girl, the father) as the line "take her" is said; the choice is the father\'s, so he is in frame. Held to the end of the line.')
def Q3(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    lamp(S, 0, 8.60, 1.50, power=1.4, t=t, flick_seed=38)
    op = ez(t, 143.4, 143.9, 0.0, 1.0, 'o')
    zf, gf, ff = S['fig']['zayd'], S['fig']['girl'], S['fig']['father']
    fig_pose(zf, 8.74, 1.92, -50.0, head=(0, 2, 0), armR=(10 + 60 * op, 6, 30), armL=(8, 4, 0), mouth=talk(t, 143.0, 144.6, 6.0, 42.0), brow=(0.2, 4), blink=blink_at(t, [144.3]))
    fig_pose(gf, 8.58, 1.80, -20.0, scale=1.58, head=(0, 0, 0), armR=(6, 6, 0), armL=(8, 18, 0), mouth='closed', brow=(0.1, 3))
    fig_pose(ff, 9.10, 2.12, 160.0, head=(0, -6, 0), armR=(6, 4, 0), armL=(6, 4, 0), mouth='closed', brow=(-0.2, -6))
    pos, tgt = cam_keys(t, [(143.058, (8.88, 1.28, 0.100), (8.82, 1.95, 0.100)), (144.9, (8.84, 1.38, 0.104), (8.82, 1.95, 0.100))], 't')
    c.camera(pos, tgt, lens=30.0, fstop=3.2, focus=(8.80, 1.9, 0.10))

# ================================================================================================ SCENE 8: the poet
PX_, PY_ = -2.72, 0.95
def poet_set(c, S, t, lamp_p=1.3):
    night(c, moon=0.55, az=-100, el=22, fill=0.07, amb=0.25); c.moon_pos = (-3.0, 2.3)
    lamp(S, 0, PX_ + 0.20, PY_ - 0.17, power=lamp_p, t=t, flick_seed=50)

@shot(144.9, 152.0, 'R_years_later_famous', scene=8, why='Years later and famous are one sentence, told as a pull-back: we start close on a man writing alone and the camera slides back and up to reveal the circle of listeners; the reveal lands on "most famous" (149.3).')
def R(c, t, u):
    S = c.S; poet_set(c, S, t, 1.3 if t < 148.5 else 1.0)
    wr = math.sin((t - 145.0) * 2 * math.pi * 1.2); rec = ez(t, 148.6, 149.4, 0.0, 1.0, 'o'); w2 = ez(t, 148.2, 149.2, 0.0, 1.0, 's')
    fig_pose(S['fig']['poet'], PX_, PY_ + 0.05 * w2, lerp(165.0, 180.0, w2), seated=True, head=(lerp(-4.0, wobble(t, 0.5, 6), w2), lerp(-14 + 3 * wr, 6 * rec, w2), 0),
             armR=(lerp(52 + 8 * wr, 40 + 70 * rec * (0.7 + 0.3 * math.sin(t * 3)), w2), lerp(8, 20, w2), lerp(74, 40, w2)), armL=(lerp(30, 10, w2), lerp(10, 8, w2), lerp(52, 10, w2)),
             mouth=talk(t, 148.8, 151.8, 6.0, 51.0), brow=(0.2 + 0.2 * w2, 3), blink=blink_at(t, [146.4, 150.6]))
    sc = S['scroll']; hide(sc['root'], False); sc['root'].location = (PX_ - 0.13, PY_ - 0.02, gz(PX_, PY_)); sc['root'].rotation_euler = (0, 0, D(28)); sc['root'].scale = (0.5, 0.5, 0.5)
    for o in sc['marks']: o.hide_render = False
    sc['stylus'].hide_render = True
    for k, ls in enumerate(S['listeners']):
        th = math.radians(200 + 140 * k / 6.0 + 4.0 * (k % 2)); r = 0.30 + 0.03 * (k % 3)
        x, y = PX_ + r * math.cos(th), PY_ + 0.05 + r * math.sin(th) * 0.8
        ls.hide(False); ls.pose(loc=(x, y, gz(x, y)), yaw=yaw_of(-math.cos(th), -math.sin(th)), seated=True, head=(6 * math.sin(t * 0.6 + k), 3 + 2 * math.sin(t * 0.9 + k), 0), bob=0.0007 * math.sin(t * 1.1 + k))
    lamp(S, 1, PX_ - 0.18, PY_ - 0.15, power=0.8, t=t, flick_seed=51)
    pos, tgt = cam_keys(t, [(144.9, (PX_ + 0.10, PY_ - 0.46, 0.085), (PX_ - 0.03, PY_, 0.085)), (148.2, (PX_ + 0.04, PY_ - 0.42, 0.095), (PX_ - 0.02, PY_, 0.088)), (152.0, (PX_ - 0.40, PY_ - 0.50, 0.140), (PX_ - 0.02, PY_ + 0.02, 0.085))], 't')
    c.camera(pos, tgt, lens=lerp(40.0, 34.0, ez(t, 148.0, 150.5, 0, 1, 's')), fstop=4.0, focus=(PX_, PY_ + 0.05, 0.09))

@shot(152.0, 154.72, 'R3_one_line', scene=8, why='"One line was about his grandfather": the camera returns to his face, close, because the next thing we see is what he wrote. Short because it is a breath, not a scene.')
def R3(c, t, u):
    S = c.S; poet_set(c, S, t, 1.3)
    fig_pose(S['fig']['poet'], PX_, PY_, 175.0, seated=True, head=(ez(t, 152.0, 153.2, -2, -10, 's'), -10, 0), armR=(56, 6, 60), armL=(30, 10, 50), mouth='closed', brow=(0.3, 3), blink=blink_at(t, [153.0]))
    sc = S['scroll']; hide(sc['root'], False); sc['root'].location = (PX_ - 0.13, PY_ - 0.02, gz(PX_, PY_)); sc['root'].rotation_euler = (0, 0, D(28)); sc['root'].scale = (0.5, 0.5, 0.5)
    for o in sc['marks']: o.hide_render = False
    sc['stylus'].hide_render = True
    pos, tgt = cam_keys(t, [(152.0, (PX_ + 0.10, PY_ - 0.34, 0.100), (PX_ - 0.01, PY_, 0.090)), (154.72, (PX_ + 0.02, PY_ - 0.30, 0.100), (PX_ - 0.07, PY_ - 0.02, 0.092))], 't')
    c.camera(pos, tgt, lens=40.0, fstop=4.0, focus=(PX_ - 0.03, PY_ - 0.02, 0.095))

VERSE_T = [[154.50, 154.85, 155.37], [155.88, 156.23], [156.66, 157.33], [158.32, 158.60, 158.94], [159.28, 159.62]]
@shot(154.72, 160.42, 'S_the_verse', scene=8, why='The line itself, set in clay letters word by word on the beat of the voice (no text is read before it is spoken). A slow crane up the scroll lets the last line "not buried" stand alone at the top of the frame; held for the pause after.')
def S_(c, t, u):
    S = c.S; night(c, moon=0.35, az=-110, el=24, fill=0.05, amb=0.22); c.moon_pos = (-3.1, 2.3)
    vx, vy = PX_, PY_ - 0.20; v = S['verse']; hide(v['root'], False); v['root'].location = (vx, vy, gz(vx, vy)); v['root'].rotation_euler = (0, 0, 0)
    for k, L in enumerate(v['lines']): L.show(t=t, times=VERSE_T[k], pop_s=0.35)
    lamp(S, 0, vx + 0.19, vy - 0.12, power=1.7, t=t, flick_seed=52); lamp(S, 1, vx - 0.19, vy - 0.10, power=0.8, t=t, flick_seed=53)
    pos, tgt = cam_keys(t, [(154.72, (vx - 0.03, vy - 0.60, 0.115), (vx, vy, 0.105)), (160.42, (vx - 0.01, vy - 0.42, 0.135), (vx, vy, 0.118))], 't')
    c.camera(pos, tgt, lens=34.0, fstop=3.5, focus=(vx, vy, 0.12))

# ================================================================================================ SCENE 9: dawn
G_PTS = [(-3.3, 1.50), (-2.7, 1.60), (-2.0, 1.50), (-1.3, 1.70), (-0.6, 1.85)]
GC, GS = W.spline_pts(G_PTS, 0.01)
G_FINAL = tuple(float(v) for v in path_at(GC, GS, 0.35 + 0.17 * (170.0 - 164.4))[0])

def dawn_light(c, k):
    c.light(dawn=k, moon=lerp(0.6, 1.3, k), az=lerp(-100, 20, k), el=lerp(24, 7, k), moon_k=lerp(10000, 3600, k), fill=0.10 + 0.05 * k, fill_k=lerp(8000, 6500, k), amb=lerp(0.3, 0.55, k),
            stars=1.0 - 0.9 * k, moon_vis=1.0 if k < 0.45 else 0.0, sky_em=lerp(0.9, 1.5, k), exposure=0.15 * k)
    c.moon_pos = (-0.5, 2.3)

def field_dim(S, k): S['flame_base'] = 18.0 * (1.0 - 0.55 * k)

@shot(160.42, 164.4, 'T1_nobody_knows', scene=9, why='The count is unknowable, so we see all of it at once: a slow crane over the field of lamps as the night turns to dawn. A hold on the wide, because the next shot picks one.')
def T1(c, t, u):
    S = c.S; k = ez(t, 160.4, 172.0, 0.0, 0.85, 'l'); dawn_light(c, k); field_dim(S, k)
    S['field'].show(t, FIELD_T); fire_on(S, 'fire1') if False else None
    pos, tgt = cam_keys(t, [(160.42, (-0.95, -0.40, 0.22), (-0.50, 1.5, 0.05)), (164.4, (-0.35, -0.30, 0.17), (0.15, 1.5, 0.05))], 't')
    c.camera(pos, tgt, lens=28.0, fstop=4.0, focus=(-0.2, 1.4, 0.05))

GIRL_S = 1.58
@shot(164.4, 175.9, 'T2_girl_grew_up', scene=9, why='"Somewhere in that desert, a girl grew up": one girl, walking, grown, her own footprints behind her, and the sun clearing the ridge behind. A low tracking move (steady pace), then the crane up and away on "camels" gives the film its last image and room for the end card.')
def T2(c, t, u):
    S = c.S; k = ez(t, 160.4, 172.0, 0.0, 0.85, 'l'); dawn_light(c, k); field_dim(S, k)
    S['field'].show(t, FIELD_T)
    d = 0.17 * (t - 164.4); d = min(d, 0.17 * (170.0 - 164.4)); p, tg = path_at(GC, GS, 0.35 + d); moving = t < 170.0
    fig_pose(S['fig']['girl'], p[0], p[1], yaw_of(tg[0], tg[1]), scale=GIRL_S, step=(d / 0.17 if moving else None), bob=0.0014 * abs(math.sin(d / 0.17 * 6.28)), head=(0, 4 if not moving else 0, 0),
             armR=(10 * math.sin(d / 0.17 * 6.28), 4, 6), armL=(-10 * math.sin(d / 0.17 * 6.28), 4, 6), mouth='closed')
    stamps_along(S, GC, GS, 0.35 + d, 44, first=0.0)
    cr = ez(t, 169.0, 173.3, 0.0, 1.0, 's')
    pos = (lerp(p[0] - 0.30, p[0] - 0.55, cr), lerp(0.95, 0.35, cr), lerp(0.055, 0.20, cr)); tgt = (p[0] + 0.1, p[1], lerp(0.14, 0.17, cr))
    c.camera(pos, tgt, lens=lerp(46.0, 36.0, cr), fstop=4.0, focus=(p[0], p[1], 0.13))
    gx, gy = G_FINAL; rx, ry = -1.64, 1.19; sunx = rx + (gx - rx) * (4.80 - ry) / (gy - ry); c.sun = (sunx, 4.80, 0.52)
    show_hud(S, 'end', t, 173.28, 175.9, 0.22)
