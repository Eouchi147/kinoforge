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
lerp_ = None
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

@shot(25.42, 27.92, 'C1_hard')
def C1(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.8, az=-70, el=20, fill=0.10)
    tx, ty = -2.10, 1.10
    hide(S['thorn'], False); S['thorn'].location = (tx, ty, gz(tx, ty)); S['thorn'].rotation_euler = (0, 0, 0.4)
    hide(S['thorn2'], False); S['thorn2'].location = (tx + 0.16, ty + 0.12, gz(tx + 0.16, ty + 0.12)); S['thorn2'].rotation_euler = (0, 0, 1.9)
    pos = ez(t, 25.42, 27.92, (tx + 0.02, ty - 0.55, 0.050), (tx + 0.04, ty - 0.38, 0.060), 's'); tgt = (tx + 0.03, ty, 0.06)
    c.camera(pos, tgt, lens=40.0, fstop=3.0, focus=(tx, ty, 0.05))

@shot(27.92, 33.7, 'C2_hunger')
def C2(c, t, u):
    S = c.S; c.light(moon=0.35, az=-105, el=25, fill=0.05, amb=0.25)
    bx, by = 1.70, 0.85
    lit_tents(S, c, t, glow=2.0, p1=1.0)
    lamp(S, 1, bx, by + 0.02, power=0.9, t=t, flick_seed=5)
    n = 5 + (1 if t >= 32.6 else 0)
    spots = [(-0.075, -0.05), (0.075, -0.05), (-0.085, 0.07), (0.085, 0.07), (0.0, -0.095), (0.0, 0.0)]
    for k in range(n):
        b = S['bowls'][k]; hide(b, False); x, y = bx + spots[k][0], by + spots[k][1] + 0.0
        b.location = (x, y, gz(x, y) - 0.001); pop = 1.0 if k < 5 else (0.6 + 0.4 * ease(clamp((t - 32.6) / 0.25), 'o') if t >= 32.6 else 0.0)
        b.scale = (pop, pop, pop)
        S['bowl_dates'][k].hide_render = (k >= 2 and k < 5) or k == 5     # a few bowls hold dates, most are empty
        if k < 2: S['bowl_dates'][k].scale = (0.6, 0.6, 0.5)
    pos = ez(t, 27.92, 33.7, (bx - 0.05, by - 0.42, 0.075), (bx - 0.02, by - 0.28, 0.080), 's'); tgt = ez(t, 27.92, 33.7, (bx, by + 0.28, 0.05), (bx, by + 0.02, 0.025), 's')
    c.camera(pos, tgt, lens=40.0, fstop=3.2, focus=(bx, by, 0.02))

@shot(33.7, 37.22, 'C3_lone_lamp')
def C3(c, t, u):
    S = c.S; c.light(moon=0.5, az=-100, el=22, fill=0.06, amb=0.25)
    x, y = 0.35, 0.85
    fl = 1.0 + 0.0
    l = lamp(S, 0, x, y, power=1.3, t=t, flick_seed=7)
    pos = ez(t, 33.7, 37.22, (x - 0.10, y - 0.36, 0.045), (x - 0.04, y - 0.22, 0.040), 's'); tgt = (x, y, 0.028)
    c.camera(pos, tgt, lens=40.0, fstop=2.8, focus=(x, y, 0.02))

@shot(37.22, 39.62, 'D1_families')
def D1(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.55, az=-110, el=22, fill=0.10, amb=0.25)
    glow_camp(S, 2.6, sil={0: ('head', 'veil', 'body'), 2: ('head', 'veil', 'body', 'arm', 'bundle', 'bhead'), 4: ('head', 'veil', 'body')}, t=t)
    pos = ez(t, 37.22, 39.62, (-2.55, 1.55, 0.085), (-1.55, 1.58, 0.090), 's'); tgt = ez(t, 37.22, 39.62, (-2.40, 3.2, 0.09), (-1.40, 3.2, 0.09), 's')
    c.camera(pos, tgt, lens=26.0, fstop=3.5, focus=(-2.0, 3.2, 0.08))

@shot(39.62, 41.52, 'D2_dark_tent')
def D2(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.5, az=-110, el=22, fill=0.10, amb=0.25)
    dim = ez(t, 39.9, 40.8, 1.0, 0.0, 's')
    sil = {0: ('head', 'veil', 'body'), 2: ('head', 'veil', 'body', 'arm', 'bundle', 'bhead'), 4: ('head', 'veil', 'body'), 3: ('head', 'veil', 'body')}
    for k, tt in enumerate(S['camp']):
        x, y = W.CAMP[k]; tt.show(sil=sil.get(k, ()) if (k != 3 or dim > 0.3) else ()); tt.root.location = (x, y, gz(x, y)); tt.root.rotation_euler = (0, 0, D((k * 37) % 17 - 8))
        tt.glow_em.inputs['Strength'].default_value = 2.6 * ((0.03 + 0.97 * dim) if k == 3 else 1.0)
    pos = ez(t, 39.62, 41.52, (-1.55, 1.9, 0.085), (-1.43, 2.35, 0.080), 's'); tgt = (-1.30, 3.14, 0.085)
    c.camera(pos, tgt, lens=30.0, fstop=3.2, focus=(-1.30, 3.14, 0.07))

TC, TS = W.spline_pts(W.TRACK_PTS, 0.01)

def track_pos(d, off=0.14):
    p, tg = path_at(TC, TS, d); n = np.array([-tg[1], tg[0]])
    q = p - n * off   # the rider keeps beside the tracks (towards the camera side)
    return q, tg

@shot(41.52, 46.0, 'E1_follow_tracks')
def E1(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.8, az=-100, el=22, fill=0.12)
    d = 0.9 + 0.27 * (t - 41.52); q, tg = track_pos(d); yaw = yaw_of(tg[0], tg[1])
    ride(S, 'ride', q[0], q[1], yaw, t, d, arm=(10, 6, 14), head=(wobble(t, 0.5, 8), 2, 0), neck=(0, 2))
    pos = (q[0] + 0.02, q[1] - 0.56, 0.085); tgt = (q[0] + 0.09, q[1], 0.115)
    c.camera(pos, tgt, lens=38.0, fstop=3.0, focus=(q[0], q[1], 0.12))
    for k, tt in enumerate(S['camp']):
        x, y = W.CAMP[k]; tt.show(); tt.root.location = (x, y, gz(x, y)); tt.glow_em.inputs['Strength'].default_value = 2.0

@shot(46.0, 48.99, 'E2_two_tents')
def E2(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.55, az=-95, el=20, fill=0.10, amb=0.25)
    stop = 47.7
    d = 2.18 + 0.27 * (min(t, stop) - 46.0) - (0.0 if t < stop else 0.0); q, tg = track_pos(d); yaw = yaw_of(tg[0], tg[1])
    moving = t < stop
    point = ez(t, 47.7, 48.3, 0.0, 1.0, 'o')
    ride(S, 'ride', q[0], q[1], yaw, t, d, moving=moving, arm=(8 + 78 * point, 6, 20 * (1 - point)), head=(-8 * point, 3, 0), neck=(0, 2 + 6 * point), brow=(0.6 * point, 8 * point))
    lit_tents(S, c, t, glow=2.0 + 1.8 * ez(t, 47.7, 48.2, 0.0, 1.0), p1=1.0 + ez(t, 47.7, 48.2, 0.0, 1.0))
    pos = ez(t, 46.0, 48.99, (q[0] - 0.65, q[1] - 0.20, 0.150), (q[0] - 0.60, q[1] - 0.12, 0.175), 's'); tgt = (1.25, 1.62, 0.105)
    c.camera(pos, tgt, lens=34.0, fstop=3.5, focus=(q[0] + 0.1, q[1], 0.18) if t < 47.7 else (1.4, 1.6, 0.1))

OLD_P, SAS_P = (1.30, 1.36), (0.98, 1.30)

def camp_actors(S, t, sas=None, old=None, camels=True, sasaa_kw=None, old_kw=None):
    if camels:
        camel_stand(S, 'she1', 0.58, 1.60, -80.0, t, neck=(wobble(t, 0.2, 6), 2)); camel_stand(S, 'she2', 0.78, 1.82, -95.0, t, neck=(wobble(t, 0.17, 6, 1.0), 0))
        camel_stand(S, 'calf1', 0.40, 1.45, -60.0, t); camel_stand(S, 'calf2', 0.30, 1.70, -110.0, t)
        camel_stand(S, 'ride', 0.45, 1.02, -70.0, t, neck=(wobble(t, 0.15, 6), 0))

@shot(48.99, 52.0, 'F1_old_man')
def F1(c, t, u):
    S = c.S; c.light(moon=0.35, az=-105, el=24, fill=0.07, amb=0.25)
    lit_tents(S, c, t, glow=2.0, p1=1.2)
    old = S['fig']['old']; k = ez(t, 49.6, 50.6, 0.0, 1.0, 's')
    fig_pose(old, OLD_P[0], OLD_P[1], 180.0 + 8 * k, lean=14.0 - 4 * k, head=(-6 * (1 - k), -4 + 6 * k, 0), armR=(32, 6, 70), armL=(10, 6, 0), mouth=talk(t, 49.2, 50.9, 5.0, 1.0), brow=(0.2, -3), blink=blink_at(t, [50.3]))
    S['staff'].hide_render = False; hide(S['staff'], False); S['staff'].location = (OLD_P[0] + 0.020, OLD_P[1] - 0.030, gz(*OLD_P)); S['staff'].rotation_euler = (D(-6), 0, 0)
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], -75.0, head=(10, 1, 0), mouth='closed', brow=(0.3, 4))
    camp_actors(S, t)
    pos = ez(t, 48.99, 52.0, (1.12, 0.92, 0.100), (1.22, 1.00, 0.108), 's'); tgt = ez(t, 48.99, 52.0, (1.25, 1.40, 0.095), (OLD_P[0] + 0.005, OLD_P[1], 0.112), 's')
    c.camera(pos, tgt, lens=36.0, fstop=3.2, focus=(OLD_P[0], OLD_P[1], 0.10))

@shot(52.0, 54.58, 'F2_found_camels')
def F2(c, t, u):
    S = c.S; c.light(moon=0.35, az=-105, el=24, fill=0.07, amb=0.25)
    lit_tents(S, c, t, glow=2.0, p1=1.1)
    old = S['fig']['old']; pt = ez(t, 52.9, 53.6, 0.0, 1.0, 'o')
    fig_pose(old, OLD_P[0], OLD_P[1], 150.0, lean=10.0, head=(ez(t, 52.0, 53.0, 0, 20, 's'), 0, 0), armR=(32 + 40 * pt, 8 + 14 * pt, 60 - 40 * pt), armL=(10, 6, 0), mouth=talk(t, 52.0, 54.3, 5.0, 2.0), brow=(0.3, -3))
    hide(S['staff'], False); S['staff'].location = (OLD_P[0] + 0.020, OLD_P[1] - 0.030, gz(*OLD_P)); S['staff'].rotation_euler = (D(-6), 0, 0)
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], -50.0, head=(ez(t, 52.9, 53.6, 10.0, 40.0, 's'), 3, 0), mouth='closed', brow=(0.5, 5))
    camp_actors(S, t)
    pos = ez(t, 52.0, 54.58, (1.12, 0.78, 0.105), (0.95, 0.80, 0.110), 's'); tgt = ez(t, 52.0, 54.58, (1.12, 1.35, 0.10), (0.78, 1.45, 0.10), 's')
    c.camera(pos, tgt, lens=30.0, fstop=3.5, focus=(1.1, 1.35, 0.1))

@shot(54.58, 57.95, 'F3_milk')
def F3(c, t, u):
    S = c.S; c.light(moon=0.30, az=-105, el=24, fill=0.06, amb=0.22)
    lit_tents(S, c, t, glow=2.0, p1=1.2)
    mx, my = 1.19, 1.26; hide(S['milkbowl'], False); S['milkbowl'].location = (mx, my, gz(mx, my))
    old = S['fig']['old']
    fig_pose(old, OLD_P[0], OLD_P[1], 195.0, lean=18.0, head=(-5, -8, 0), armR=(26, 10, 52), armL=(40, 12, 48), mouth=talk(t, 55.0, 57.5, 5.0, 3.0), brow=(0.2, -6), blink=blink_at(t, [56.6]))
    S['milkbowl'].location = (mx, my, gz(mx, my))
    camp_actors(S, t)
    pos = ez(t, 54.58, 57.95, (1.05, 0.88, 0.062), (1.12, 1.00, 0.070), 's'); tgt = ez(t, 54.58, 57.95, (mx + 0.06, my, 0.040), (mx + 0.08, my, 0.058), 's')
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(mx, my, 0.015))

def tent2_lamp(S, t, power=1.0):
    return lamp(S, 2, 2.28, 1.585, power=power, t=t, flick_seed=9)

@shot(57.95, 60.7, 'G1_woman_calls')
def G1(c, t, u):
    S = c.S; c.light(moon=0.30, az=-105, el=24, fill=0.05, amb=0.22)
    call = 0.5 + 0.5 * math.sin((t - 58.6) * 2 * math.pi * 1.6) if 58.6 < t < 60.4 else 0.0
    lit_tents(S, c, t, glow=2.3, p1=0.8, sil2=('head', 'veil', 'body', 'arm'), glow2=1.0 + 0.5 * ez(t, 58.6, 58.9, 0.0, 1.0))
    ar = S['t2'].sil['arm']; ar.rotation_euler = (0, D(35 - 55 * call), 0); ar.location = (-0.0065 - 0.004 * call, -W_DP, 0.044 + 0.012 * call)
    tent2_lamp(S, t, 0.8)
    turn = ez(t, 58.6, 59.5, 0.0, 1.0, 's')
    fig_pose(S['fig']['sasaa'], 1.86, 1.22, 180.0 + 139.0 * turn, head=(0, 0, 0), mouth='closed', brow=(0.4, 4))
    fig_pose(S['fig']['old'], 2.02, 1.18, 180.0 + 151.0 * turn, lean=10.0, head=(0, 0, 0), mouth='closed')
    hide(S['staff'], False); S['staff'].location = (2.045, 1.15, gz(2.02, 1.18)); S['staff'].rotation_euler = (0, 0, 0)
    pos = ez(t, 57.95, 60.7, (1.95, 0.62, 0.085), (2.05, 0.74, 0.095), 's'); tgt = (2.30, 1.72, 0.085)
    c.camera(pos, tgt, lens=32.0, fstop=3.5, focus=(2.35, 1.7, 0.08))

W_DP = A.Tent.DP + 0.0058

@shot(60.7, 63.34, 'G2_given_birth')
def G2(c, t, u):
    S = c.S; c.light(moon=0.25, az=-105, el=24, fill=0.04, amb=0.20)
    appear = t >= 61.9
    sil = ('head', 'veil', 'body', 'arm', 'bundle', 'bhead') if appear else ('head', 'veil', 'body', 'arm')
    lit_tents(S, c, t, glow=2.3, p1=0.7, sil2=sil)
    S['t2'].sil['arm'].rotation_euler = (0, D(35), 0)
    pk = ez(t, 61.9, 62.3, 0.0, 1.0, 'o'); S['t2'].glow_em.inputs['Strength'].default_value = 2.3 * (1.0 + 0.25 * pk)
    for nm in ('bundle', 'bhead'):
        o = S['t2'].sil[nm]; s = (0.55 + 0.45 * pk) if appear else 1.0; o.scale = (s, 1.0, s)
    tent2_lamp(S, t, 0.7 + 0.5 * pk)
    pos = ez(t, 60.7, 63.34, (2.18, 0.82, 0.085), (2.26, 1.08, 0.088), 's'); tgt = (2.33, 1.74, 0.075)
    c.camera(pos, tgt, lens=34.0, fstop=3.2, focus=(2.35, 1.7, 0.07))

def dialog_light(c, S, t, *, lamp_xy, p=1.0):
    c.light(moon=0.25, az=-110, el=22, fill=0.05, amb=0.20)
    lit_tents(S, c, t, glow=2.2, p1=1.0, sil2=('head', 'veil', 'body', 'arm', 'bundle', 'bhead'))
    S['t2'].sil['arm'].rotation_euler = (0, D(35), 0)
    lamp(S, 2, lamp_xy[0], lamp_xy[1], power=p, t=t, flick_seed=11)

def old_cu(S, t, yaw=165.0, lean=6.0, head=(0, 0, 0), arm=(30, 8, 60), mouth='closed', brow=(0, -4), armL=(10, 6, 0), blink=0.0):
    fig_pose(S['fig']['old'], OLD_P[0], OLD_P[1], yaw, lean=lean, head=head, armR=arm, armL=armL, mouth=mouth, brow=brow, blink=blink)
    hide(S['staff'], False); S['staff'].location = (OLD_P[0] + 0.022, OLD_P[1] - 0.030, gz(*OLD_P)); S['staff'].rotation_euler = (0, 0, 0)

@shot(63.34, 66.0, 'H1_boy_or_girl')
def H1(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(OLD_P[0] - 0.07, OLD_P[1] - 0.09), p=1.1)
    old_cu(S, t, yaw=172.0, lean=5.0, head=(ez(t, 63.3, 64.2, -10, 4, 's'), 2 - 4 * math.sin(clamp((t - 64.6) / 1.0) * math.pi), 0), arm=(26, 8, 70), mouth=talk(t, 63.5, 65.6, 6.0, 5.0), brow=(0.7 * ez(t, 64.5, 64.9, 0, 1), -5), blink=blink_at(t, [64.2]))
    fig_pose(S['fig']['sasaa'], SAS_P[0] - 0.08, SAS_P[1] - 0.02, -70.0, head=(0, 0, 0))
    pos = ez(t, 63.34, 66.0, (OLD_P[0] + 0.07, OLD_P[1] - 0.34, 0.100), (OLD_P[0] + 0.04, OLD_P[1] - 0.27, 0.102), 's'); tgt = (OLD_P[0] - 0.004, OLD_P[1], 0.104)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(OLD_P[0], OLD_P[1] - 0.014, 0.104))

@shot(66.0, 69.41, 'H2_one_of_us')
def H2(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(OLD_P[0] - 0.07, OLD_P[1] - 0.09), p=1.1)
    ch = ez(t, 67.6, 68.4, 0.0, 1.0, 's')
    old_cu(S, t, yaw=150.0, lean=4.0, head=(ez(t, 66.0, 67.0, 10, -8, 's'), 3, 0), arm=(24 + 20 * ch, 6, 78 - 20 * ch), mouth=talk(t, 66.2, 69.0, 6.0, 6.0), brow=(0.4, -4), blink=blink_at(t, [67.3]))
    fig_pose(S['fig']['sasaa'], SAS_P[0] - 0.08, SAS_P[1] - 0.02, -70.0, head=(0, 0, 0))
    pos = ez(t, 66.0, 69.41, (OLD_P[0] - 0.22, OLD_P[1] - 0.26, 0.096), (OLD_P[0] - 0.14, OLD_P[1] - 0.30, 0.100), 's'); tgt = (OLD_P[0], OLD_P[1], 0.103)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(OLD_P[0], OLD_P[1] - 0.01, 0.104))

@shot(69.41, 71.0, 'H3_bury_her')
def H3(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(OLD_P[0] - 0.05, OLD_P[1] - 0.07), p=0.7)
    old_cu(S, t, yaw=178.0, lean=2.0, head=(0, 0, 0), arm=(14, 8, 8), mouth=talk(t, 69.6, 71.5, 5.0, 8.0), brow=(0.0, -12))
    pos = ez(t, 69.41, 71.0, (OLD_P[0] + 0.00, OLD_P[1] - 0.32, 0.092), (OLD_P[0] + 0.01, OLD_P[1] - 0.26, 0.094), 's'); tgt = (OLD_P[0], OLD_P[1], 0.100)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(OLD_P[0], OLD_P[1] - 0.014, 0.102))

@shot(71.0, 72.17, 'H4_reaction')
def H4(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(SAS_P[0] + 0.08, SAS_P[1] - 0.08), p=0.9)
    k = ez(t, 71.0, 71.5, 0.0, 1.0, 'o')
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], 180.0 - 18.0, head=(-4, -2 + 2 * k, 0), mouth='closed', brow=(-0.6 * k, 10 * k), blink=blink_at(t, [71.9], 0.14))
    pos = (SAS_P[0] + 0.06, SAS_P[1] - 0.30, 0.108); tgt = (SAS_P[0], SAS_P[1], 0.112)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(SAS_P[0], SAS_P[1] - 0.014, 0.112))

@shot(72.17, 74.02, 'I_it_was_a_girl')
def I_(c, t, u):
    S = c.S; c.light(moon=0.15, az=-105, el=24, fill=0.02, amb=0.18)
    lit_tents(S, c, t, glow=2.6, p1=0.6, sil2=('head', 'veil', 'body', 'arm', 'bundle', 'bhead'))
    S['t2'].sil['arm'].rotation_euler = (0, D(35), 0)
    br = 1.0 + 0.03 * math.sin((t - 72.17) * 2 * math.pi * 0.8)
    for nm in ('bundle', 'bhead'): S['t2'].sil[nm].scale = (br, 1.0, br)
    tent2_lamp(S, t, 0.9)
    pos = ez(t, 72.17, 74.02, (2.30, 0.98, 0.080), (2.33, 1.10, 0.082), 's'); tgt = (2.34, 1.74, 0.070)
    c.camera(pos, tgt, lens=36.0, fstop=3.2, focus=(2.35, 1.7, 0.07))

@shot(74.02, 77.3, 'J1_asked_to_buy')
def J1(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(1.15, 1.18), p=1.2)
    p = ez(t, 75.4, 76.2, 0.0, 1.0, 'o')
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], -65.0, lean=4.0 * p, head=(ez(t, 74.0, 74.8, 0, -12, 's'), 2, 0), armR=(30 + 40 * p, 14 + 14 * p, 40 - 8 * p), armL=(8, 6, 0), mouth=talk(t, 74.2, 76.6, 6.0, 12.0), brow=(0.4, 5), blink=blink_at(t, [75.0]))
    old_cu(S, t, yaw=115.0, lean=8.0, head=(ez(t, 75.8, 76.6, 0, 10, 's'), 2, 0), arm=(34, 8, 66), mouth='closed', brow=(0.0, -3))
    pos = ez(t, 74.02, 77.3, (1.17, 0.84, 0.098), (1.14, 0.92, 0.100), 's'); tgt = (1.14, 1.33, 0.100)
    c.camera(pos, tgt, lens=26.0, fstop=3.2, focus=(1.14, 1.33, 0.1))

@shot(77.3, 80.4, 'J2_insulted')
def J2(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(OLD_P[0] - 0.07, OLD_P[1] - 0.09), p=1.0)
    k = ez(t, 77.8, 78.6, 0.0, 1.0, 'o')
    old_cu(S, t, yaw=172.0 - 12 * k, lean=12.0 * (1 - k) - 2.0 * k, head=(0, 6 * k, 0), arm=(40 + 40 * k, 8 + 8 * k, 56 - 36 * k), mouth='closed' if t < 78.8 else talk(t, 78.8, 80.3, 6.0, 15.0), brow=(0.9 * k, -16 * k), blink=0.0)
    S['staff'].rotation_euler = (D(-6 - 8 * k), 0, 0)
    pos = ez(t, 77.3, 80.4, (OLD_P[0] + 0.05, OLD_P[1] - 0.33, 0.098), (OLD_P[0] + 0.03, OLD_P[1] - 0.26, 0.105), 's'); tgt = (OLD_P[0], OLD_P[1], 0.104 + 0.004 * k)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(OLD_P[0], OLD_P[1] - 0.014, 0.105))

@shot(80.4, 83.75, 'J3_free_man')
def J3(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(OLD_P[0] - 0.07, OLD_P[1] - 0.09), p=1.0)
    old_cu(S, t, yaw=168.0, lean=-2.0, head=(ez(t, 80.4, 82.0, -8, 6, 's'), 6, 0), arm=(46 + 14 * math.sin((t - 80.4) * 5), 10, 48), mouth=talk(t, 80.5, 83.3, 6.0, 16.0), brow=(0.8, -14), blink=blink_at(t, [82.0]))
    S['staff'].rotation_euler = (D(-14), 0, 0)
    pos = ez(t, 80.4, 83.75, (OLD_P[0] - 0.12, OLD_P[1] - 0.30, 0.098), (OLD_P[0] - 0.05, OLD_P[1] - 0.24, 0.106), 's'); tgt = (OLD_P[0], OLD_P[1], 0.108)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(OLD_P[0], OLD_P[1] - 0.014, 0.108))

@shot(83.75, 88.2, 'K1_answered')
def K1(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(SAS_P[0] + 0.07, SAS_P[1] - 0.09), p=0.9)
    br = math.sin((t - 83.75) * 2 * math.pi * 0.25) * 1.0
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], 180.0 - 14.0, bob=0.0008 * br, head=(ez(t, 83.75, 86.5, 8, -2, 's'), 1 + 0.8 * br, 0), armR=(10, 5, 0), mouth=talk(t, 85.6, 87.6, 4.0, 20.0) if t > 85.6 else 'closed', brow=(0.3, 3), blink=blink_at(t, [85.2]))
    pos = ez(t, 83.75, 88.2, (SAS_P[0] + 0.11, SAS_P[1] - 0.36, 0.100), (SAS_P[0] + 0.07, SAS_P[1] - 0.30, 0.104), 's'); tgt = (SAS_P[0], SAS_P[1], 0.112)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(SAS_P[0], SAS_P[1] - 0.014, 0.112))

@shot(88.2, 91.95, 'K2_buying_her_life')
def K2(c, t, u):
    S = c.S; dialog_light(c, S, t, lamp_xy=(SAS_P[0] + 0.06, SAS_P[1] - 0.08), p=0.8)
    hand = ez(t, 89.0, 89.5, 0.0, 1.0, 'o')
    fig_pose(S['fig']['sasaa'], SAS_P[0], SAS_P[1], 180.0, head=(0, 2 + 3 * ez(t, 89.4, 90.2, 0.0, 1.0), 0), armR=(40 * hand + 8 * (1 - hand), 18 * (1 - hand) + 6 * hand, 92 * hand), armL=(8, 6, 0),
             mouth=talk(t, 88.4, 91.2, 5.5, 21.0), brow=(0.2, 6), blink=blink_at(t, [91.5]))
    zoom = ez(t, 88.2, 91.95, 0.0, 1.0, 's')
    pos = (SAS_P[0] + 0.03 - 0.02 * zoom, SAS_P[1] - 0.30 + 0.07 * zoom, 0.104 + 0.004 * zoom); tgt = (SAS_P[0], SAS_P[1], 0.112)
    c.camera(pos, tgt, lens=42.0, fstop=2.6, focus=(SAS_P[0], SAS_P[1] - 0.016, 0.112))

# ---------------------------------------------------------------- the price: camels handed over, rope by rope
ANIMALS = [('she1', 92.45, 0), ('she2', 93.75, 1), ('calf1', 94.95, 2), ('calf2', 95.75, 3), ('ride', 97.0, 4)]
LPOS = {'she1': (0.62, 1.42, -80.0), 'she2': (0.50, 1.62, -85.0), 'calf1': (0.70, 1.15, -80.0), 'calf2': (0.52, 1.02, -75.0), 'ride': (0.34, 1.30, -80.0)}

def price_scene(c, t, S):
    from mathutils import Vector
    dialog_light(c, S, t, lamp_xy=(1.15, 1.16), p=1.2)
    old, sas = S['fig']['old'], S['fig']['sasaa']
    # arm pulses: Sasaa reaches out, the old man takes the rope
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

def bump(t, a, b, c_):
    if t <= a or t >= c_: return 0.0
    return smoothstep3((t - a) / (b - a)) if t < b else 1.0 - smoothstep3((t - b) / (c_ - b))

@shot(91.95, 94.95, 'L1_two_pregnant')
def L1(c, t, u):
    S = c.S; price_scene(c, t, S)
    pos = ez(t, 91.95, 94.95, (0.95, 0.60, 0.100), (0.98, 0.70, 0.105), 's'); tgt = ez(t, 91.95, 94.95, (0.80, 1.38, 0.10), (0.92, 1.36, 0.10), 's')
    c.camera(pos, tgt, lens=28.0, fstop=3.5, focus=(0.9, 1.35, 0.1))

@shot(94.95, 96.35, 'L2_calves')
def L2(c, t, u):
    S = c.S; price_scene(c, t, S)
    pos = ez(t, 94.95, 96.35, (1.05, 0.70, 0.085), (1.00, 0.78, 0.088), 's'); tgt = (0.90, 1.30, 0.085)
    c.camera(pos, tgt, lens=36.0, fstop=3.2, focus=(0.9, 1.3, 0.09))

@shot(96.35, 98.85, 'L3_riding_camel')
def L3(c, t, u):
    S = c.S; price_scene(c, t, S)
    pos = ez(t, 96.35, 98.85, (0.62, 0.66, 0.115), (0.70, 0.60, 0.120), 's'); tgt = ez(t, 96.35, 98.85, (0.78, 1.30, 0.11), (0.82, 1.30, 0.10), 's')
    c.camera(pos, tgt, lens=26.0, fstop=3.5, focus=(0.8, 1.3, 0.1))

HOME_PTS = [(1.0, 1.05), (0.45, 0.88), (-0.25, 0.72), (-1.0, 0.74), (-1.7, 0.98), (-2.3, 1.22)]
HC, HS = W.spline_pts(HOME_PTS, 0.01)
STAMP_STEP = 0.085
def stamps_along(S, C, Sd, d_now, count, lat=0.011, first=0.0):
    """Footprints already pressed behind the walker: stamp k sits at distance first + k*step, alternating left/right."""
    for k in range(min(count, len(S['stamps']))):
        dk = first + k * STAMP_STEP
        o = S['stamps'][k]
        if dk > d_now - 0.04: o.hide_render = True; continue
        p, tg = path_at(C, Sd, dk); n = np.array([-tg[1], tg[0]]); side = 1 if k % 2 else -1; q = p + n * lat * side
        o.hide_render = False; o.location = (q[0], q[1], gz(q[0], q[1])); o.rotation_euler = (0, 0, D(yaw_of(tg[0], tg[1]) + 3.0 * side))

STOP_S = 0.78
@shot(98.85, 101.8, 'M1_walked_home')
def M1(c, t, u):
    S = c.S; day_default(c); c.light(moon=0.8, az=-100, el=22, fill=0.12)
    d = min(0.27 * (t - 98.85), STOP_S); p, tg = path_at(HC, HS, d); yaw = yaw_of(tg[0], tg[1])
    moving = d < STOP_S - 1e-6
    fig_pose(S['fig']['sasaa'], p[0], p[1], yaw, step=(d / 0.17 if moving else None), bob=0.0015 * abs(math.sin(d / 0.17 * math.pi * 2)), lean=2.5, head=(0, -3, 0), armR=(12 * math.sin(d / 0.17 * 6.28), 4, 6), armL=(-12 * math.sin(d / 0.17 * 6.28), 4, 6), mouth='closed', brow=(-0.2, 3))
    stamps_along(S, HC, HS, d, 40)
    lit_tents(S, c, t, glow=2.0, p1=0.8)
    cam_p = (p[0] - 0.12, p[1] - 0.62, 0.080); tgt = (p[0] + 0.14, p[1] + 0.02, 0.095)
    c.camera(cam_p, tgt, lens=32.0, fstop=3.5, focus=(p[0], p[1], 0.10))

@shot(101.8, 104.9, 'M2_promise')
def M2(c, t, u):
    S = c.S; c.light(moon=1.0, az=-100, el=26, fill=0.10, amb=0.28)
    p, tg = path_at(HC, HS, STOP_S); k = ez(t, 102.3, 103.4, 0.0, 1.0, 's')
    fig_pose(S['fig']['sasaa'], p[0], p[1], 0.0 + 8 * k, head=(0, -6 + 28 * k, 0), armR=(8 + 14 * k, 6, 64 * ez(t, 103.4, 104.0, 0.0, 1.0, 'o')), armL=(8, 6, 0), mouth='closed', brow=(0.5 * k, 3))
    stamps_along(S, HC, HS, STOP_S + 0.1, 40)
    pos = (p[0] - 0.04, p[1] - 0.34, 0.062); tgt = ez(t, 101.8, 104.9, (p[0] + 0.02, p[1] + 1.2, 0.16), (p[0] - 0.12, p[1] + 1.6, 0.30), 's')
    c.camera(pos, tgt, lens=30.0, fstop=3.2, focus=(p[0], p[1], 0.10))

@shot(104.9, 108.95, 'M3_every_girl')
def M3(c, t, u):
    S = c.S; c.light(moon=0.8, az=-100, el=26, fill=0.10, amb=0.28)
    p, tg = path_at(HC, HS, STOP_S)
    fig_pose(S['fig']['sasaa'], p[0], p[1], 20.0, head=(-12, 4, 0), armR=(40, 8, 70), armL=(8, 6, 0), mouth='closed', brow=(0.3, 5), blink=blink_at(t, [106.4]))
    stamps_along(S, HC, HS, STOP_S + 0.1, 40)
    offs = [(-0.10, 0.12, 105.5), (0.12, 0.08, 106.2), (-0.03, 0.26, 106.95), (0.10, 0.27, 107.5)]
    for k, (ox, oy, tt) in enumerate(offs):
        x, y = p[0] + ox, p[1] + oy; on = ez(t, tt, tt + 0.25, 0.0, 1.0, 'o')
        if k == 0: lamp(S, 3, x, y, on=on, power=1.6, t=t, flick_seed=20 + k)
        else: lamp(S, k - 1, x, y, on=on, power=0.0, t=t, flick_seed=20 + k, nl=True) if False else lamp(S, k - 1, x, y, on=on, power=1.0, t=t, flick_seed=20 + k, nl=True)
    S['field'].show(t, [107.7, 1e9, 1e9, 1e9, 1e9])
    pos = ez(t, 104.9, 108.95, (p[0] - 0.02, p[1] - 0.30, 0.060), (p[0] + 0.05, p[1] - 0.26, 0.070), 's'); tgt = ez(t, 104.9, 108.95, (p[0] + 0.02, p[1] + 0.20, 0.090), (p[0] + 0.02, p[1] + 0.42, 0.045), 's')
    c.camera(pos, tgt, lens=34.0, fstop=3.0, focus=(p[0], p[1], 0.10))

TILE_X = [(-0.17, 0.66), (-0.057, 0.60), (0.057, 0.60), (0.17, 0.66)]
TILE_T = [113.0, 113.8, 115.05, 117.38]
def tiles_show(S, t, bump_k=None):
    for k, (r, txt) in enumerate(S['tiles']):
        tt = TILE_T[k]
        if t < tt: continue
        hide(r, False); x, y = TILE_X[k]; r.location = (x, y, gz(x, y) - 0.002); r.rotation_euler = (0, 0, D((k - 1.5) * 4.0))
        a = clamp((t - tt) / 0.4); s = 0.78 * (1.0 if a >= 1 else (0.5 + 0.7 * smoothstep3(a / 0.6) if a < 0.6 else 1.2 - 0.2 * smoothstep3((a - 0.6) / 0.4)))
        r.scale = (s, s, s); txt.show(t=t, times=[tt + 0.1]); txt.root.hide_render = False
        if txt.items: txt.items[0][0].hide_render = False

FIELD_T = [107.7, 113.0, 113.85, 115.1, 117.45]
@shot(108.95, 113.0, 'N1_records_cannot_agree')
def N1(c, t, u):
    S = c.S; c.light(moon=0.9, az=-100, el=26, fill=0.10, amb=0.30)
    S['field'].show(t, FIELD_T)
    pos = ez(t, 108.95, 113.0, (0.20, -0.62, 0.52), (0.08, -0.36, 0.34), 's'); tgt = ez(t, 108.95, 113.0, (-0.2, 1.4, 0.04), (-0.1, 1.2, 0.04), 's')
    c.camera(pos, tgt, lens=28.0, fstop=4.0, focus=(0.0, 1.2, 0.05))
    p, tg = path_at(HC, HS, STOP_S); fig_pose(S['fig']['sasaa'], p[0], p[1], 20.0, head=(0, 5, 0))
    stamps_along(S, HC, HS, STOP_S + 0.1, 40)

@shot(113.0, 119.3, 'N2_numbers')
def N2(c, t, u):
    S = c.S; c.light(moon=0.8, az=-100, el=26, fill=0.14, amb=0.30)
    S['field'].show(t, FIELD_T); tiles_show(S, t)
    pos = ez(t, 113.0, 119.3, (0.05, -0.28, 0.200), (0.0, 0.02, 0.105), 's'); tgt = ez(t, 113.0, 119.3, (0.0, 0.80, 0.060), (0.0, 0.70, 0.072), 's')
    c.camera(pos, tgt, lens=28.0, fstop=3.5, focus=(0.0, 0.62, 0.07))

@shot(119.3, 122.2, 'N3_every_number_a_girl')
def N3(c, t, u):
    S = c.S; c.light(moon=0.7, az=-100, el=26, fill=0.12, amb=0.28)
    S['field'].show(t, FIELD_T); tiles_show(S, t)
    pos = ez(t, 119.3, 122.2, (0.0, 0.10, 0.105), (0.02, 0.50, 0.075), 's'); tgt = ez(t, 119.3, 122.2, (0.0, 0.70, 0.075), (0.00, 1.70, 0.050), 's')
    c.camera(pos, tgt, lens=28.0, fstop=2.8, focus=(0.0, 0.65, 0.07) if t < 120.8 else (0.0, 1.5, 0.04))

# ---------------------------------------------------------------- Mecca
def mecca_scene(S, t, lit=(0, 1, 2, 3, 4, 5, 6, 7), door_on=1.0):
    for k, (root, door) in enumerate(S['houses']):
        hide(root, False)
        for ch in root.children:
            if ch.name.startswith(f'house{k}_win') and 'fr' not in ch.name: ch.hide_render = k not in lit
        if door is not None: door.hide_render = door_on < 0.5
    S['mecca_far'] = S['mecca_far']

def mecca_light(c, **kw):
    c.light(moon=0.0, moon_vis=0.0, az=-100, el=26, fill=0.10, amb=0.32, **kw)

@shot(122.2, 124.0, 'O1_not_alone')
def O1(c, t, u):
    S = c.S; mecca_light(c); c.light(fill=0.06)
    mecca_scene(S, t)
    on = ez(t, 122.55, 122.85, 0.0, 1.0, 'o'); lx, ly = 9.00, 1.20
    lamp(S, 0, lx, ly, on=on, power=1.8, t=t, flick_seed=30)
    zx = ez(t, 122.9, 124.0, 9.62, 9.18, 's'); d = 9.62 - zx
    fig_pose(S['fig']['zayd'], zx, 1.30, 90.0 + 0.0, step=(d / 0.17 if t > 122.9 else None), head=(0, 0, 0), armR=(10 * math.sin(d / 0.17 * 6.28), 4, 6), armL=(-10 * math.sin(d / 0.17 * 6.28), 4, 6), mouth='closed')
    S['fig']['zayd'].hide(t < 122.9)
    pos = ez(t, 122.2, 124.0, (8.92, 0.72, 0.060), (8.98, 0.66, 0.070), 's'); tgt = (9.05, 1.25, 0.065)
    c.camera(pos, tgt, lens=36.0, fstop=2.8, focus=(lx, ly, 0.02))

@shot(124.0, 128.7, 'O2_mecca_zayd')
def O2(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    lamp(S, 0, 9.12, 1.42, power=1.8, t=t, flick_seed=31); lamp(S, 1, 8.40, 1.60, power=1.2, t=t, flick_seed=32)
    k = ez(t, 126.0, 126.9, 0.0, 1.0, 's')
    fig_pose(S['fig']['zayd'], 9.00, 1.20, 90.0 + 90.0 * k, head=(ez(t, 126.0, 127.0, 20, 0, 's'), 2, 0), armR=(8, 4, 0), armL=(8, 4, 0), mouth='closed', brow=(0.3, 4), blink=blink_at(t, [127.4]))
    show_hud(S, 'mecca', t, 124.2, 128.0, 0.31)
    pos = ez(t, 124.0, 128.7, (8.55, 0.38, 0.100), (8.72, 0.50, 0.105), 's'); tgt = ez(t, 124.0, 128.7, (9.05, 2.3, 0.080), (9.05, 1.60, 0.100), 's')
    c.camera(pos, tgt, lens=28.0, fstop=3.5, focus=(9.0, 1.3, 0.08) if t > 126.0 else (9.0, 2.2, 0.08))

FA_X, FA_Y = 9.00, 2.22
@shot(128.7, 131.45, 'P1_father_door')
def P1(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    lamp(S, 0, 8.55, 1.55, power=1.0, t=t, flick_seed=33)
    fig_pose(S['fig']['father'], FA_X - 0.03, FA_Y, 0.0, head=(0, -14, 0), armR=(6, 4, 0), armL=(6, 4, 0), mouth='closed', brow=(-0.3, -6))
    zx = ez(t, 128.7, 131.45, 8.30, 8.62, 's'); d = zx - 8.30
    fig_pose(S['fig']['zayd'], zx, 1.80, -75.0, step=d / 0.17, head=(0, 0, 0), armR=(10 * math.sin(d / 0.17 * 6.28), 4, 6), armL=(-10 * math.sin(d / 0.17 * 6.28), 4, 6), mouth='closed', brow=(0.0, 6))
    pos = ez(t, 128.7, 131.45, (8.62, 1.22, 0.085), (8.72, 1.32, 0.090), 's'); tgt = (9.0, 2.35, 0.075)
    c.camera(pos, tgt, lens=30.0, fstop=3.5, focus=(FA_X - 0.03, FA_Y, 0.08))

@shot(131.45, 134.95, 'P2_do_not_kill')
def P2(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    lamp(S, 0, 8.60, 1.62, power=1.6, t=t, flick_seed=34)
    ph = ez(t, 132.85, 133.35, 0.0, 1.0, 'o')
    fig_pose(S['fig']['zayd'], 8.78, 1.90, -35.0, head=(0, 2, 0), armR=(10 + 70 * ph, 10 + 10 * ph, 20 + 70 * ph), armL=(8, 4, 0), mouth=talk(t, 131.7, 134.5, 6.0, 40.0), brow=(0.7 * ph, 8 * ph), blink=blink_at(t, [132.6]))
    fig_pose(S['fig']['father'], 9.05, 2.18, 150.0, head=(ez(t, 131.5, 132.3, 0, -10, 's'), -4, 0), armR=(6, 4, 0), armL=(6, 4, 0), mouth='closed', brow=(-0.2, -8))
    pos = ez(t, 131.45, 134.95, (8.70, 1.52, 0.100), (8.64, 1.60, 0.104), 's'); tgt = (8.80, 1.90, 0.104)
    c.camera(pos, tgt, lens=42.0, fstop=2.8, focus=(8.78, 1.89, 0.104))

@shot(134.95, 137.4, 'P3_pay_keep')
def P3(c, t, u):
    from mathutils import Vector
    S = c.S; mecca_light(c); mecca_scene(S, t)
    lamp(S, 0, 8.70, 1.55, power=1.5, t=t, flick_seed=35)
    ex = ez(t, 135.2, 135.9, 0.0, 1.0, 'o')
    zf, ff = S['fig']['zayd'], S['fig']['father']
    fig_pose(zf, 8.80, 1.90, -75.0, head=(0, 2, 0), armR=(10 + 62 * ex, 8, 24 + 22 * ex), armL=(8, 4, 0), mouth=talk(t, 135.0, 136.9, 6.0, 41.0), brow=(0.3, 5), blink=blink_at(t, [136.3]))
    fig_pose(ff, 9.04, 1.96, 105.0, head=(ez(t, 135.0, 136.4, 0, 8, 's'), -6 * ex, 0), armR=(6 + 30 * ez(t, 136.2, 136.8, 0, 1, 's'), 6, 20), armL=(6, 4, 0), mouth='closed', brow=(-0.3, -6))
    S['bpy'].context.view_layer.update()
    hp = zf.hand['R'].matrix_world.translation; po = S['pouch']; hide(po, False); po.location = (hp.x, hp.y - 0.001, hp.z - 0.012); po.rotation_euler = (0, 0, 0)
    pos = ez(t, 134.95, 137.4, (8.88, 1.40, 0.090), (8.92, 1.50, 0.094), 's'); tgt = (8.92, 1.94, 0.096)
    c.camera(pos, tgt, lens=34.0, fstop=3.0, focus=(8.92, 1.94, 0.096))

def zayd_girl(S, t, x, y, yaw, d, gscale, step=True, face=None):
    zf, gf = S['fig']['zayd'], S['fig']['girl']
    ph = d / 0.17
    fig_pose(zf, x, y, yaw, step=ph if step else None, bob=0.0014 * abs(math.sin(ph * math.pi * 2)), head=(0, 0, 0), armR=(10 * math.sin(ph * 6.28), 4, 6), armL=(8, 26, 8), mouth='closed' if face is None else face, brow=(0.2, 4))
    nx, ny = -math.cos(math.radians(yaw)) * 0.0 + 0.0, 0.0
    rx, ry = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))      # figure-right vector in world (yaw about Z of +X)
    gx, gy = x - rx * (0.060 + 0.012 * gscale), y - ry * (0.060 + 0.012 * gscale)
    fig_pose(gf, gx, gy, yaw, step=ph if step else None, scale=gscale, bob=0.0014 * abs(math.sin(ph * math.pi * 2 + 1.0)), head=(0, 0, 0), armR=(-10 * math.sin(ph * 6.28), 40, -4), armL=(10 * math.sin(ph * 6.28), 4, 6), mouth='closed', brow=(0.1, 3))

@shot(137.4, 139.5, 'Q1_raised')
def Q1(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    d = 0.20 * (t - 137.4); x = 9.60 - d
    lamp(S, 0, 8.95, 1.45, power=1.2, t=t, flick_seed=36)
    zayd_girl(S, t, x, 1.10, 90.0, d, 1.0)
    pos = (x - 0.10, 0.55, 0.075); tgt = (x - 0.03, 1.10, 0.085)
    c.camera(pos, tgt, lens=36.0, fstop=3.2, focus=(x, 1.1, 0.08))

@shot(139.5, 142.95, 'Q2_grown')
def Q2(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    d = 0.20 * (t - 139.5) + 0.42; x = 9.18 - d
    gs = seg(t, [(139.5, 1.0), (140.4, 1.0), (140.45, 1.25), (141.2, 1.25), (141.25, 1.45), (141.9, 1.45), (141.95, 1.62)], 'h') if False else (1.0 if t < 140.4 else 1.22 if t < 141.2 else 1.40 if t < 141.9 else 1.58)
    lamp(S, 0, 8.55, 1.50, power=1.2, t=t, flick_seed=37)
    zayd_girl(S, t, x, 1.12, 90.0, d, gs)
    pos = (x - 0.14, 0.58, 0.090); tgt = (x - 0.04, 1.12, 0.100)
    c.camera(pos, tgt, lens=34.0, fstop=3.2, focus=(x, 1.12, 0.10))

@shot(142.95, 144.9, 'Q3_take_her')
def Q3(c, t, u):
    S = c.S; mecca_light(c); mecca_scene(S, t)
    lamp(S, 0, 8.60, 1.50, power=1.4, t=t, flick_seed=38)
    op = ez(t, 143.4, 143.9, 0.0, 1.0, 'o')
    zf, gf, ff = S['fig']['zayd'], S['fig']['girl'], S['fig']['father']
    fig_pose(zf, 8.74, 1.92, -50.0, head=(0, 2, 0), armR=(10 + 60 * op, 6, 30), armL=(8, 4, 0), mouth=talk(t, 143.0, 144.6, 6.0, 42.0), brow=(0.2, 4), blink=blink_at(t, [144.3]))
    fig_pose(gf, 8.58, 1.80, -20.0, scale=1.58, head=(0, 0, 0), armR=(6, 6, 0), armL=(8, 18, 0), mouth='closed', brow=(0.1, 3))
    fig_pose(ff, 9.10, 2.12, 160.0, head=(0, -6, 0), armR=(6, 4, 0), armL=(6, 4, 0), mouth='closed', brow=(-0.2, -6))
    pos = ez(t, 142.95, 144.9, (8.88, 1.28, 0.100), (8.84, 1.36, 0.104), 's'); tgt = (8.82, 1.95, 0.100)
    c.camera(pos, tgt, lens=30.0, fstop=3.2, focus=(8.80, 1.9, 0.10))

# ---------------------------------------------------------------- the grandson poet
PX_, PY_ = -2.72, 0.95
def poet_set(c, S, t, lamp_p=1.3):
    c.light(moon=0.55, az=-100, el=22, fill=0.07, amb=0.25)
    lamp(S, 0, PX_ + 0.20, PY_ - 0.17, power=lamp_p, t=t, flick_seed=50)
    for k in range(3):
        pass

@shot(144.9, 148.45, 'R1_years_later')
def R1(c, t, u):
    S = c.S; poet_set(c, S, t)
    wr = math.sin((t - 145.0) * 2 * math.pi * 1.2)
    fig_pose(S['fig']['poet'], PX_, PY_, 165.0, seated=True, head=(-4, -14 + 3 * wr, 0), armR=(52 + 8 * wr, 8, 74), armL=(30, 10, 52), mouth='closed', brow=(0.2, 3), blink=blink_at(t, [146.4]))
    sc = S['scroll']; hide(sc['root'], False); sc['root'].location = (PX_ - 0.07, PY_ - 0.13, gz(PX_, PY_)); sc['root'].rotation_euler = (0, 0, D(22))
    for o in sc['marks']: o.hide_render = False
    sc['stylus'].hide_render = True
    pos = ez(t, 144.9, 148.45, (PX_ + 0.10, PY_ - 0.46, 0.085), (PX_ + 0.06, PY_ - 0.34, 0.095), 's'); tgt = (PX_, PY_, 0.085)
    c.camera(pos, tgt, lens=40.0, fstop=3.0, focus=(PX_, PY_, 0.09))

@shot(148.45, 152.0, 'R2_famous_poet')
def R2(c, t, u):
    S = c.S; poet_set(c, S, t, 1.0)
    rec = ez(t, 148.6, 149.4, 0.0, 1.0, 'o')
    fig_pose(S['fig']['poet'], PX_, PY_ + 0.05, 180.0, head=(wobble(t, 0.5, 6), 6 * rec, 0), armR=(40 + 70 * rec * (0.7 + 0.3 * math.sin(t * 3)), 20, 40), armL=(10, 8, 10), mouth=talk(t, 148.8, 151.8, 6.0, 51.0), brow=(0.4, 4))
    rs = np.random.RandomState(2)
    for k, ls in enumerate(S['listeners']):
        th = math.radians(200 + 140 * k / 6.0 + 4.0 * (k % 2)); r = 0.30 + 0.03 * (k % 3)
        x, y = PX_ + r * math.cos(th), PY_ + 0.05 + r * math.sin(th) * 0.8
        ls.hide(False); ls.pose(loc=(x, y, gz(x, y)), yaw=yaw_of(-math.cos(th), -math.sin(th)), seated=True, head=(0, 4, 0))
    lamp(S, 1, PX_ - 0.18, PY_ - 0.15, power=0.8, t=t, flick_seed=51)
    pos = ez(t, 148.45, 152.0, (PX_ + 0.02, PY_ - 0.62, 0.100), (PX_ - 0.02, PY_ - 0.50, 0.095), 's'); tgt = (PX_, PY_ + 0.05, 0.085)
    c.camera(pos, tgt, lens=34.0, fstop=3.2, focus=(PX_, PY_ + 0.05, 0.09))

@shot(152.0, 154.72, 'R3_one_line')
def R3(c, t, u):
    S = c.S; poet_set(c, S, t, 1.3)
    fig_pose(S['fig']['poet'], PX_, PY_, 175.0, seated=True, head=(ez(t, 152.0, 153.2, -2, -10, 's'), -10, 0), armR=(56, 6, 60), armL=(30, 10, 50), mouth='closed', brow=(0.3, 3), blink=blink_at(t, [153.0]))
    sc = S['scroll']; hide(sc['root'], False); sc['root'].location = (PX_ - 0.07, PY_ - 0.13, gz(PX_, PY_)); sc['root'].rotation_euler = (0, 0, D(22))
    pos = ez(t, 152.0, 154.72, (PX_ + 0.05, PY_ - 0.30, 0.095), (PX_ - 0.05, PY_ - 0.36, 0.108), 's'); tgt = ez(t, 152.0, 154.72, (PX_ - 0.01, PY_, 0.088), (PX_ - 0.07, PY_ - 0.13, 0.100), 's')
    c.camera(pos, tgt, lens=40.0, fstop=3.0, focus=(PX_ - 0.03, PY_ - 0.07, 0.095))

VERSE_T = [[154.50, 154.85, 155.37], [155.88, 156.23], [156.66, 157.33], [158.32, 158.60, 158.94], [159.28, 159.62]]
@shot(154.72, 160.42, 'S_verse')
def S_(c, t, u):
    S = c.S; c.light(moon=0.35, az=-110, el=24, fill=0.05, amb=0.22)
    vx, vy = PX_, PY_ - 0.20; v = S['verse']; hide(v['root'], False); v['root'].location = (vx, vy, gz(vx, vy)); v['root'].rotation_euler = (0, 0, 0)
    for k, L in enumerate(v['lines']): L.show(t=t, times=VERSE_T[k], pop_s=0.35)
    lamp(S, 0, vx + 0.19, vy - 0.12, power=1.7, t=t, flick_seed=52); lamp(S, 1, vx - 0.19, vy - 0.10, power=0.8, t=t, flick_seed=53)
    pos = ez(t, 154.72, 160.42, (vx - 0.03, vy - 0.62, 0.130), (vx - 0.01, vy - 0.40, 0.140), 's'); tgt = (vx, vy, 0.115)
    c.camera(pos, tgt, lens=34.0, fstop=3.5, focus=(vx, vy, 0.12))

# ---------------------------------------------------------------- dawn: a girl grew up
G_PTS = [(-3.2, 2.20), (-2.6, 2.05), (-1.9, 2.18), (-1.2, 2.35), (-0.5, 2.28)]
GC, GS = W.spline_pts(G_PTS, 0.01)

def dawn_light(c, k):
    c.light(dawn=k, moon=lerp(0.6, 1.3, k), az=lerp(-100, 20, k), el=lerp(24, 7, k), moon_k=lerp(10000, 3600, k), fill=0.10 + 0.05 * k, fill_k=lerp(8000, 6500, k), amb=lerp(0.3, 0.55, k),
            stars=1.0 - 0.9 * k, moon_vis=1.0 if k < 0.45 else 0.0, sky_em=lerp(0.9, 1.5, k), exposure=0.15 * k)

def field_dim(S, k):
    S['M']['flame_em'].inputs['Strength'].default_value = 18.0 * (1.0 - 0.55 * k)

@shot(160.42, 164.4, 'T1_nobody_knows')
def T1(c, t, u):
    S = c.S; k = ez(t, 160.4, 172.0, 0.0, 0.85, 'l'); dawn_light(c, k); field_dim(S, k)
    S['field'].show(t, FIELD_T)
    pos = ez(t, 160.42, 164.4, (-0.95, -0.40, 0.22), (-0.35, -0.30, 0.17), 's'); tgt = ez(t, 160.42, 164.4, (-0.50, 1.5, 0.05), (0.15, 1.5, 0.05), 's')
    c.camera(pos, tgt, lens=28.0, fstop=4.0, focus=(-0.2, 1.4, 0.05))

GIRL_S = 1.58
@shot(164.4, 175.9, 'T2_girl_grew_up')
def T2(c, t, u):
    S = c.S; k = ez(t, 160.4, 172.0, 0.0, 0.85, 'l'); dawn_light(c, k); field_dim(S, k)
    S['field'].show(t, FIELD_T)
    d = 0.17 * (t - 164.4); d = min(d, 0.17 * (170.0 - 164.4)); p, tg = path_at(GC, GS, 0.35 + d); moving = t < 170.0
    fig_pose(S['fig']['girl'], p[0], p[1], yaw_of(tg[0], tg[1]), scale=GIRL_S, step=(d / 0.17 if moving else None), bob=0.0014 * abs(math.sin(d / 0.17 * 6.28)), head=(0, 4 if not moving else 0, 0),
             armR=(10 * math.sin(d / 0.17 * 6.28), 4, 6), armL=(-10 * math.sin(d / 0.17 * 6.28), 4, 6), mouth='closed')
    stamps_along(S, GC, GS, 0.35 + d, 44, first=0.0)
    # camera: low at the foot of the dune, then craning up and away
    cr = ez(t, 169.0, 173.3, 0.0, 1.0, 's')
    pos = ez(t, 164.4, 169.2, (-2.55, 1.05, 0.060), (-1.85, 1.10, 0.075), 's') if t < 169.2 else (lerp(-1.85, -1.55, cr), lerp(1.10, 0.20, cr), lerp(0.075, 0.32, cr))
    tgt = ez(t, 164.4, 169.2, (-2.4, 2.1, 0.12), (p[0] + 0.05, p[1], 0.14), 's') if t < 169.2 else (p[0] + 0.1, p[1], lerp(0.14, 0.17, cr))
    c.camera(pos, tgt, lens=34.0 if t < 169.2 else lerp(34.0, 28.0, cr), fstop=3.5, focus=(p[0], p[1], 0.13))
    show_hud(S, 'end_title', t, 173.28, 175.9, 0.28, fade=0.0001, stagger=0.06); show_hud(S, 'end_sub', t, 173.9, 175.9, 0.205, fade=0.0001, stagger=0.12)
