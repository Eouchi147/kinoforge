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
def shot(t0, t1, name=''):
    def deco(fn):
        SHOTS.append((snapt(t0), snapt(t1), name or fn.__name__, fn)); return fn
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
    for h in S['hud'].values(): h.root.hide_render = True; [setattr(it[0], 'hide_render', True) for it in h.items]
    S['hud_on'] = False
    S['field'].hide_all()
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
    pl = reg(pivot(bpy, 'plinth', coll)); v, f = loft_z([(-0.012, 0.215, 0.040), (0.0, 0.215, 0.040), (0.008, 0.212, 0.038), (0.012, 0.205, 0.034)], 4 * 12, True, True)
    mk(bpy, 'plinth_slab', v, f, M['tile'], coll, pl, noise_amp=0.0009, seed=9); S['plinth'] = pl
    # lamp field: ~400 lamps scattered across the clay desert, nearest the centre first
    def field_pts(n):
        rs = np.random.RandomState(3); pts = []
        tries = 0
        while len(pts) < n and tries < 200000:
            tries += 1; x = rs.uniform(-3.7, 3.7); y = rs.uniform(0.55, 3.7)
            if abs(x - 0.4) < 0.5 and 0.5 < y < 1.5: continue
            if min([math.hypot(x - a, y - b) for a, b, _ in pts] or [9]) < 0.085: continue
            pts.append((x, y, 0.0))
        pts.sort(key=lambda p: math.hypot(p[0] - (-1.7), (p[1] - 1.2) * 1.2))
        return [(x, y, float(W.terrain_h(np.array(x), np.array(y)))) for x, y, _ in pts]
    S['field'] = P.LampField(bpy, coll, M['lampclay'], M['flame'], field_pts, [30, 66, 264, 40])
    # Mecca
    S['houses'] = []
    for k, (x, y, w, d, h, wi, dr) in enumerate(W.MECCA_HOUSES):
        root, door = P.build_house(bpy, f'house{k}', coll, M, w=w, d=d, h=h, seed=100 + k, door=dr, windows=wi); root.location = (x, y, gz(x, y)); S['houses'].append((root, door))
        reg(root)
    # far cards for Mecca
    S['mecca_far'] = [W.cut_dunes(bpy, coll, M['paper_far'][k], f'mecca_far{k}', y, 5.5, 18.0, base, amp, 40 + k) for k, (y, base, amp) in enumerate(((4.18, 0.22, 0.40), (4.44, 0.34, 0.42)))]

def build_scroll(bpy, coll, M, reg, marks=True):
    r = reg(pivot(bpy, 'scroll' if marks else 'verse', coll)); S = {'root': r}
    wd, hg = (0.115, 0.17) if marks else (0.115, 0.20)
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
        for row in range(9):
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

def build_hud(bpy, ctx, S, M, coll):
    """Title-card lettering lives in its own tiny scene (no depth of field) and is alpha-composited over the picture."""
    hs = bpy.data.scenes.new('hud'); S['hud_scene'] = hs
    hs.render.engine = 'CYCLES'; hs.render.resolution_x = ctx['W']; hs.render.resolution_y = ctx['H']; hs.render.resolution_percentage = 100
    hs.render.film_transparent = True; hs.cycles.device = 'CPU'; hs.cycles.samples = 8; hs.cycles.use_denoising = False; hs.cycles.max_bounces = 2
    hs.cycles.seed = 0; hs.cycles.use_animated_seed = False
    hs.render.use_compositing = False
    hc = bpy.data.cameras.new('hudcam'); hc.lens = 35.0; hc.sensor_width = 36.0; hc.dof.use_dof = False
    ho = bpy.data.objects.new('hudcam', hc); hs.collection.objects.link(ho); hs.camera = ho; ho.location = (0, 0, 0)
    ld = bpy.data.lights.new('hudlight', 'AREA'); ld.energy = 2.0; ld.size = 0.4; lo = bpy.data.objects.new('hudlight', ld); hs.collection.objects.link(lo); lo.location = (-0.15, 0.2, 0.15)
    lo.rotation_euler = (math.radians(20), math.radians(-20), 0)
    wd = bpy.data.worlds.new('hudworld'); hs.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    def hud(name, text, size, per='word'):
        L = P.Lettering(bpy, 'hud_' + name, coll, text, size, M['hud'], per=per, extrude=0.004, bevel=0.0010, plane='XY')
        for o in [L.root] + [it[0] for it in L.items]:
            coll.objects.unlink(o); hs.collection.objects.link(o)
        for o, x, u in L.items: set_vis(o, False)
        S['hud'][name] = L; return L
    hud('arabia', 'ARABIA,', 0.026); hud('around', 'AROUND 600', 0.017); hud('mecca', 'MECCA', 0.030)
    hud('end_title', 'DARK CORNERS', 0.040, 'letter'); hud('end_sub', 'I Am Buying Her Life', 0.0200)

def show_hud(S, name, t, t_on, t_off, y, d=0.5, fade=0.35, stagger=0.0):
    """HUD text (y = vertical offset in frame heights, + up); pops in at t_on, shrinks out by t_off."""
    L = S['hud'][name]; vis = t_on <= t < t_off
    L.root.hide_render = not vis
    if not vis:
        for o, x, u in L.items: o.hide_render = True
        return
    S['hud_on'] = True
    L.root.location = (0.0, y * 36.0 * d / 35.0, -d); L.root.rotation_euler = (0, 0, 0); L.root.scale = (1.0, 1.0, 1.0)
    times = [t_on + stagger * k for k in range(len(L.items))]
    L.show(t=t, times=times)
    out = clamp((t - (t_off - fade)) / fade)
    if out > 0:
        s = 1.0 - 0.15 * out
        for o, x, u in L.items: o.scale = tuple(a * s for a in o.scale)
        if out > 0.6:
            for o, x, u in L.items: o.hide_render = True

# ------------------------------------------------------------------------------------------------ frame application
def render_pose(bpy, ctx, S, pf):
    from mathutils import Vector, Quaternion
    t = pf / 24.0
    hide_all(S)
    for h in S['hud'].values(): h.root.hide_render = True
    sh = None
    for s in SHOTS:
        if s[0] <= t < s[1]: sh = s; break
    if sh is None: sh = SHOTS[-1]
    c = Ctx(S, bpy, t); c.t0, c.t1, c.name = sh[0], sh[1], sh[2]; c.u = clamp((t - sh[0]) / max(1e-6, sh[1] - sh[0]))
    sh[3](c, t, c.u)
    if os.environ.get('KF_LT'): c.lt.update(eval(os.environ['KF_LT']))
    if os.environ.get('KF_CAM'): c.cam.update(eval(os.environ['KF_CAM']))
    # camera (+ per-pose hand jitter of the stand: +-0.4 mm, +-0.03 deg)
    cam, cd = S['cam'], S['camd']; cs = c.cam
    pos = Vector(cs['pos']) + Vector((jit(pf, 'cx', 0.0004), jit(pf, 'cy', 0.0004), jit(pf, 'cz', 0.0004)))
    tgt = Vector(cs['tgt']); cam.location = pos
    q = (tgt - pos).to_track_quat('-Z', 'Y')
    if cs['roll']: q = q @ Quaternion((0, 0, 1), math.radians(cs['roll']))
    cam.rotation_euler = q.to_euler()
    cd.lens = cs['lens']; cd.dof.aperture_fstop = cs['fstop']; cd.dof.focus_distance = max(0.05, (Vector(cs['focus'] if cs['focus'] is not None else cs['tgt']) - pos).length)
    bpy.context.view_layer.update()
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
    S['sky_em'].inputs['Strength'].default_value = L['sky_em']; S['stars_em'].inputs['Strength'].default_value = 14.0 * L['stars']
    S['moon'].hide_render = L['moon_vis'] < 0.5; S['moon_halo'].hide_render = L['moon_vis'] < 0.5
    sc.view_settings.exposure = L['exposure']

def fig_pose(f, x, y, yaw, **kw):
    f.hide(False); f.pose(loc=(x, y, gz(x, y)), yaw=yaw, **kw)

def lamp(S, k, x, y, z=None, on=1.0, flick_seed=0.0, t=0.0, power=1.0, lit=True, yaw=0.0, nl=False):
    pool = S['lamps_nl'] if nl else S['lamps']; l = pool[k]
    fl = (hash01('fl', flick_seed, int(t * 12)) - 0.5) * 2.0 if on > 0 else 0.0
    l.pose((x, y, (gz(x, y) if z is None else z)), on, fl, power, yaw)
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

# ------------------------------------------------------------------------------------------------ shots (filled in below)

SX, SY = -1.80, 1.50          # the ridge where Sasaa stands with his camel (opening, x1)

def sasaa_stand(S, t, x, y, yaw, head=(0, 0, 0), **kw):
    f = S['fig']['sasaa']; fig_pose(f, x, y, yaw, head=head, bob=wobble(t, 0.4, 0.0006), **kw); return f

def camel_stand(S, key, x, y, yaw, t, neck=(0, 0), **kw):
    c = S['camel'][key]; c.hide(False); c.pose(loc=(x, y, gz(x, y)), yaw=yaw, gait=None, neck=neck, **kw); return c

@shot(0.0, 6.6, 'A1_sky_to_dune')
def A1(c, t, u):
    S = c.S
    # camera: starts looking up at the pin-hole stars and the moon, tilts down and drifts in to the ridge
    k = ease(clamp((t - 0.6) / 4.6), 's')
    pos = ez(t, 0.0, 6.6, (-0.95, -0.55, 0.13), (-1.28, 0.20, 0.115), 's')
    tgt = (lerp(-0.85, SX + 0.15, k), lerp(4.8, SY, k), lerp(1.9, 0.115, k))
    c.camera(pos, tgt, lens=30.0, fstop=4.0, focus=(lerp(-0.8, SX, ease(clamp((t - 1.5) / 3.0), 's')), lerp(4.8, SY, ease(clamp((t - 1.5) / 3.0), 's')), 0.1))
    c.light(moon=0.7, az=-40, el=20)
    # Sasaa and his camel on the ridge, looking for tracks: head turns, hand shades the eyes
    hy = ez(t, 2.4, 3.4, 40.0, -35.0, 's') if t < 5.0 else ez(t, 5.0, 5.8, -35.0, -10.0, 's')
    arm = (100.0, 10.0, 88.0) if 2.2 < t < 5.6 else (8, 4, 0)
    sasaa_stand(S, t, SX, SY, -150.0, head=(hy, 3, 0), armR=ez(t, 2.0, 2.8, (8, 4, 0), arm) if t < 5.0 else ez(t, 5.0, 5.8, arm, (8, 4, 0)), mouth='closed', brow=(0.4, 6))
    camel_stand(S, 'ride', SX + 0.20, SY + 0.12, -105.0, t, neck=(wobble(t, 0.25, 8), 4))
    for k, tt in enumerate(S['camp']):
        x, y = W.CAMP[k]; tt.show(); tt.root.location = (x, y, gz(x, y)); tt.root.rotation_euler = (0, 0, D(wobble(0, 0, 0))); tt.glow_em.inputs['Strength'].default_value = 1.6
        tt.glow_em.inputs['Strength'].default_value = 1.6
    show_hud(S, 'arabia', t, 0.9, 5.9, 0.30); show_hud(S, 'around', t, 1.2, 5.9, 0.235)

def day_default(c):
    c.light(moon=1.0, az=-105, el=28, moon_k=11000, fill=0.16, amb=0.30)

def glow_camp(S, glow=1.8, dark=None, sil=None, t=0.0):
    for k, tt in enumerate(S['camp']):
        x, y = W.CAMP[k]; tt.show(sil=(sil or {}).get(k, ())); tt.root.location = (x, y, gz(x, y)); tt.root.rotation_euler = (0, 0, D((k * 37) % 17 - 8))
        g = glow * (0.04 if dark == k else 1.0) * (1.0 + 0.05 * (hash01('cg', k, int(t * 8)) - 0.5)); tt.glow_em.inputs['Strength'].default_value = g

def lit_tents(S, c, t, glow=2.2, p1=1.0, sil2=(), glow2=1.0):
    t1, t2 = S['t1'], S['t2']
    t1.show(); t2.show(sil=sil2)
    for tt, (x, y) in ((t1, W.TENT1), (t2, W.TENT2)): tt.root.location = (x, y, gz(x, y)); tt.root.rotation_euler = (0, 0, 0)
    t2.glow_em.inputs['Strength'].default_value = glow * glow2 * (1.0 + 0.04 * (hash01('t2g', int(t * 8)) - 0.5))
    lx, ly, lz = t1.lamp_pos; x, y = W.TENT1
    return lamp(S, 0, x + lx, y + ly, gz(x, y) + lz, power=p1 * 1.0, flick_seed=1, t=t)

@shot(6.6, 11.62, 'A2_tracks')
def A2(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.9, az=-100, el=22)
    pos = ez(t, 6.6, 11.62, (-3.62, 3.00, 0.060), (-3.05, 2.80, 0.075), 's')
    tgt = ez(t, 6.6, 11.62, (-3.0, 2.78, 0.035), (0.9, 1.62, 0.115), 's')
    foc = ez(t, 6.6, 9.4, (-3.20, 2.84, 0.03), (-3.20, 2.84, 0.03)) if t < 9.4 else ez(t, 9.4, 11.0, (-3.20, 2.84, 0.03), (1.45, 1.55, 0.12), 's')
    c.camera(pos, tgt, lens=30.0, fstop=2.8, focus=foc)
    # the two tents, far away along the tracks: only the glow of their lamps at first
    lit_tents(S, c, t, glow=1.6 + 1.4 * ez(t, 8.2, 9.2, 0.0, 1.0), p1=0.0)
    S['t1'].show(); S['lamps'][0].pose((0, 0, -5), 0.0)

@shot(11.62, 16.6, 'A3_records')
def A3(c, t, u):
    S = c.S; c.light(moon=0.35, az=-120, el=30, fill=0.05, amb=0.25)
    sx, sy = 0.00, 0.35; scr = S['scroll']; r = scr['root']; hide(r, False); r.location = (sx, sy, gz(sx, sy)); r.rotation_euler = (0, 0, D(-8))
    rows_t = [11.4, 12.2, 12.8, 13.3, 13.9, 14.5, 15.1, 15.6, 16.05]
    for k, o in enumerate(scr['marks']): o.hide_render = t < rows_t[k]
    scr['stylus'].hide_render = True
    lamp(S, 0, sx - 0.14, sy - 0.10, power=1.6, t=t, flick_seed=3)
    pos = ez(t, 11.62, 16.6, (-0.22, -0.20, 0.060), (0.12, -0.10, 0.105), 's'); tgt = ez(t, 11.62, 16.6, (0.0, 0.35, 0.085), (0.0, 0.35, 0.120), 's')
    c.camera(pos, tgt, lens=40.0, fstop=3.2, focus=(sx, sy, 0.09))

@shot(16.6, 18.94, 'A4_title')
def A4(c, t, u):
    S = c.S; c.light(moon=0.8, az=-95, el=24, fill=0.12)
    x, y = 0.0, 0.85; z = gz(x, y) + 0.020
    ti = S['title']; ti.root.location = (x, y, z + 0.020); ts = S['title_sub']; ts.root.location = (x, y, z - 0.010)
    ti.show(t=t, times=[16.8 + 0.07 * k for k in range(len(ti.items))], pop_s=0.35); ts.show(t=t, times=[17.75, 17.95, 18.15, 18.3, 18.45], pop_s=0.3)
    S['plinth'].location = (x, y - 0.003, gz(x, y)); hide(S['plinth'], False)
    lamp(S, 0, x - 0.20, y - 0.14, power=1.2, t=t, flick_seed=2)
    pos = ez(t, 16.6, 18.94, (0.02, -0.10, 0.075), (0.03, 0.18, 0.085), 's'); tgt = (0.0, y, z + 0.015)
    c.camera(pos, tgt, lens=35.0, fstop=4.0, focus=tgt)

@shot(18.94, 22.0, 'B1_sasaa')
def B1(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.7, az=-120, el=24, fill=0.20)
    pos = ez(t, 18.94, 22.0, (SX + 0.06, SY - 0.46, 0.105), (SX + 0.03, SY - 0.36, 0.115), 's'); tgt = (SX, SY, 0.118)
    c.camera(pos, tgt, lens=40.0, fstop=3.5, focus=(SX, SY, 0.115))
    nod = -5.0 * math.sin(clamp((t - 20.7) / 0.9) * math.pi) if t > 20.7 else 0.0
    sasaa_stand(S, t, SX, SY, 180.0, head=(ez(t, 19.6, 20.4, 18.0, 0.0), nod + 2.0, 0), armR=(8, 5, 0), armL=(8, 5, 0), mouth='closed', brow=(0.2, 4), blink=blink_at(t, [19.9, 21.6]))
    camel_stand(S, 'ride', SX + 0.22, SY + 0.18, -150.0, t, neck=(wobble(t, 0.2, 10), 3))
    glow_camp(S, 2.0, t=t)
    lamp(S, 0, SX + 0.10, SY - 0.16, power=0.9, t=t, flick_seed=1)

@shot(22.0, 25.4, 'B2_nobleman')
def B2(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.6, az=-125, el=22, fill=0.16)
    pos = ez(t, 22.0, 25.4, (SX - 0.30, SY - 0.30, 0.085), (SX - 0.20, SY - 0.34, 0.100), 's'); tgt = (SX + 0.05, SY, 0.120)
    c.camera(pos, tgt, lens=40.0, fstop=3.0, focus=(SX, SY, 0.115))
    sasaa_stand(S, t, SX, SY, 205.0, head=(ez(t, 22.0, 23.0, 10.0, -6.0), 2 + wobble(t, 0.3, 1.5), 0), armR=(8, 5, 0), armL=(14, 6, 0), mouth='closed', brow=(0.5, 6), blink=blink_at(t, [23.3]))
    camel_stand(S, 'ride', SX + 0.24, SY + 0.12, -130.0, t, neck=(wobble(t, 0.2, 8), 3))
    glow_camp(S, 2.4, t=t)
    lamp(S, 0, SX - 0.09, SY - 0.12, power=0.6, t=t, flick_seed=4)
