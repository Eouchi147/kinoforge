"""Clay puppets and props: Figure (robed person), Camel, Tent, Lamp, Rope, tiles/letters. Every pose() is a pure function of its args."""
import math
import numpy as np
from kit import *
from kit import _mat

D = math.radians

def torus(R, r, seg=36, ring=10, squash=1.0):
    V, F = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(ring):
            b = 2 * math.pi * j / ring
            rr = R + r * math.cos(b)
            V.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b) * squash))
    for i in range(seg):
        for j in range(ring):
            a = i * ring + j; b = i * ring + (j + 1) % ring; c = ((i + 1) % seg) * ring + (j + 1) % ring; d = ((i + 1) % seg) * ring + j
            F.append((a, b, c, d))
    return V, F

def mk(bpy, name, v, f, mat, coll, parent=None, loc=(0, 0, 0), noise_amp=0.0004, noise_freq=70.0, seed=0):
    ob = mesh_obj(bpy, name, v, f, mat, coll, noise_amp=noise_amp, noise_freq=noise_freq, seed=seed)
    if parent is not None: ob.parent = parent
    ob.location = loc
    return ob

def pivot(bpy, name, coll, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); e.empty_display_size = 0.005; coll.objects.link(e)
    if parent is not None: e.parent = parent
    e.location = loc; e.rotation_mode = 'XYZ'
    return e

FIG_STYLES = {
    # robe, mantle, sash, cloth(headdress), skin, beard, cloth kind, beard size (rx, ry, rz) or None, height scale
    'sasaa': dict(robe=(0.92, 0.88, 0.76), mantle=(0.16, 0.22, 0.45), sash=(0.55, 0.20, 0.14), cloth=(0.95, 0.93, 0.86), band=(0.12, 0.10, 0.09), skin=(0.72, 0.47, 0.31), beard=((0.0100, 0.0078, 0.0085), (0.10, 0.07, 0.06)), kind='ghutra', h=1.0),
    'old': dict(robe=(0.52, 0.45, 0.36), mantle=(0.40, 0.33, 0.26), sash=(0.30, 0.22, 0.16), cloth=(0.80, 0.76, 0.66), band=(0.2, 0.16, 0.12), skin=(0.68, 0.45, 0.30), beard=((0.0112, 0.0095, 0.022), (0.92, 0.91, 0.88)), kind='turban', h=0.92),
    'zayd': dict(robe=(0.74, 0.70, 0.58), mantle=(0.20, 0.40, 0.36), sash=(0.60, 0.42, 0.14), cloth=(0.88, 0.86, 0.80), band=(0.10, 0.09, 0.08), skin=(0.70, 0.46, 0.30), beard=((0.0098, 0.0075, 0.0085), (0.35, 0.30, 0.26)), kind='ghutra', h=1.0),
    'father': dict(robe=(0.46, 0.38, 0.30), mantle=(0.26, 0.20, 0.17), sash=(0.30, 0.22, 0.16), cloth=(0.62, 0.55, 0.46), band=(0.10, 0.09, 0.08), skin=(0.66, 0.43, 0.29), beard=((0.0100, 0.0085, 0.0095), (0.10, 0.08, 0.07)), kind='turban', h=1.0),
    'girl': dict(robe=(0.80, 0.42, 0.44), mantle=(0.55, 0.24, 0.32), sash=(0.92, 0.80, 0.50), cloth=(0.92, 0.70, 0.62), band=(0.5, 0.2, 0.2), skin=(0.74, 0.50, 0.34), beard=None, kind='scarf', h=0.60),
    'woman': dict(robe=(0.62, 0.30, 0.34), mantle=(0.30, 0.22, 0.34), sash=(0.92, 0.80, 0.50), cloth=(0.80, 0.55, 0.50), band=(0.5, 0.2, 0.2), skin=(0.74, 0.50, 0.34), beard=None, kind='scarf', h=0.96),
    'poet': dict(robe=(0.34, 0.30, 0.55), mantle=(0.80, 0.70, 0.45), sash=(0.92, 0.82, 0.55), cloth=(0.92, 0.90, 0.82), band=(0.34, 0.30, 0.55), skin=(0.72, 0.47, 0.31), beard=((0.0092, 0.0072, 0.0080), (0.08, 0.07, 0.07)), kind='turban', h=1.0),
    'listener': dict(robe=(0.58, 0.52, 0.40), mantle=(0.34, 0.30, 0.28), sash=(0.30, 0.22, 0.16), cloth=(0.80, 0.76, 0.66), band=(0.2, 0.16, 0.12), skin=(0.68, 0.45, 0.30), beard=None, kind='ghutra', h=0.95),
}

class Figure:
    """Robed clay figure facing +Y in its own frame. Pose with fig.pose(...) (all angles in degrees)."""
    def __init__(self, bpy, name, style, coll, seed=1, lite=False):
        st = dict(FIG_STYLES[style]); self.style = st; self.name = name; self.lite = lite
        s = st['h']; self.sc = s
        M = lambda tag, col, **kw: clay(bpy, f'{name}_{tag}', col, tuple(x * 0.82 for x in col), seed=seed * 10 + len(tag), **kw)
        mats = dict(robe=M('robe', st['robe'], rough=0.72), mantle=M('mantle', st['mantle'], rough=0.72), sash=M('sash', st['sash'], rough=0.6),
                    cloth=M('cloth', st['cloth'], rough=0.74), band=M('band', st['band'], rough=0.55), skin=M('skin', st['skin'], rough=0.5),
                    dark=M('dark', (0.03, 0.025, 0.03), rough=0.25, sss=0.0), shoe=M('shoe', (0.20, 0.12, 0.07), rough=0.7))
        if st['beard']: mats['beard'] = M('beard', st['beard'][1], rough=0.8)
        self.mats = mats
        root = pivot(bpy, name + '_root', coll); self.root = root
        body = pivot(bpy, name + '_body', coll, root); self.body = body
        # robe + mantle yoke + sash
        rings = [(0.010, 0.036, 0.030), (0.020, 0.0335, 0.028), (0.040, 0.028, 0.0235), (0.058, 0.0255, 0.022), (0.074, 0.0285, 0.0215), (0.085, 0.0275, 0.020), (0.093, 0.0165, 0.0155)]
        v, f = loft_z(rings, 36); mk(bpy, name + '_robe', v, f, mats['robe'], coll, body, seed=seed)
        rings = [(0.058, 0.0272, 0.0238), (0.068, 0.0302, 0.0240), (0.082, 0.0300, 0.0225), (0.090, 0.0285, 0.0215), (0.0955, 0.0175, 0.0165)]
        v, f = loft_z(rings, 36); mk(bpy, name + '_mantle', v, f, mats['mantle'], coll, body, seed=seed + 1)
        v, f = torus(0.0262, 0.0042, 32, 8, 1.0); mk(bpy, name + '_sash', v, f, mats['sash'], coll, body, loc=(0, 0.0, 0.051), seed=seed + 2)
        # head
        hp = pivot(bpy, name + '_headp', coll, body, (0, 0, 0.094)); self.headp = hp
        head = ellipsoid(bpy, name + '_head', (0.0182, 0.0185, 0.0200), mats['skin'], coll, noise_amp=0.00025, seed=seed + 3); head.parent = hp; head.location = (0, 0, 0.0185)
        nose = ellipsoid(bpy, name + '_nose', (0.0042, 0.0050, 0.0058), mats['skin'], coll, seg=16, rings=10, seed=seed + 4); nose.parent = hp; nose.location = (0, 0.0178, 0.0172)
        self.eyes = []
        for sx in (-1, 1):
            e = ellipsoid(bpy, f'{name}_eye{sx}', (0.0027, 0.0021, 0.0030), mats['dark'], coll, seg=14, rings=10); e.parent = hp; e.location = (sx * 0.0068, 0.0166, 0.0225); self.eyes.append(e)
        self.brows = []
        for sx in (-1, 1):
            pts = [(-0.0050, 0, 0), (0, 0.0004, 0.0008), (0.0050, 0, 0)]
            b = tube(bpy, f'{name}_brow{sx}', pts, [0.0009, 0.0011, 0.0009], mats['dark'], coll, n=10, ring=8, lateral=(0, 1, 0))
            b.parent = hp; b.location = (sx * 0.0070, 0.0172, 0.0268); self.brows.append(b)
        sm = [(-0.0050, 0, 0.0016), (-0.0025, 0, 0.0003), (0, 0, 0), (0.0025, 0, 0.0003), (0.0050, 0, 0.0016)]
        flat = [(-0.0045, 0, 0), (0, 0, 0), (0.0045, 0, 0)]
        self.mouths = {
            'closed': tube(bpy, name + '_m_closed', flat, [0.0009, 0.0010, 0.0009], mats['dark'], coll, n=10, ring=8, lateral=(0, 1, 0)),
            'smile': tube(bpy, name + '_m_smile', sm, [0.0009, 0.0010, 0.0010, 0.0010, 0.0009], mats['dark'], coll, n=14, ring=8, lateral=(0, 1, 0)),
            'open': ellipsoid(bpy, name + '_m_open', (0.0038, 0.0020, 0.0033), mats['dark'], coll, seg=14, rings=10),
            'oh': ellipsoid(bpy, name + '_m_oh', (0.0021, 0.0018, 0.0026), mats['dark'], coll, seg=12, rings=8),
        }
        for k, m in self.mouths.items(): m.parent = hp; m.location = (0, (0.0172 if k not in ('open', 'oh') else 0.0166) + (0.0016 if st['beard'] else 0.0), 0.0108)
        if st['beard']:
            r = st['beard'][0]
            bd = ellipsoid(bpy, name + '_beard', r, mats['beard'], coll, seg=24, rings=14, noise_amp=0.0004, noise_freq=90.0, seed=seed + 5); bd.parent = hp; bd.location = (0, 0.0108, 0.0032 - max(0.0, r[2] - 0.0095) * 0.55)
            self.beard = bd
        # headdress
        k = st['kind']; cl = mats['cloth']
        if k == 'ghutra':
            dome = ellipsoid(bpy, name + '_dome', (0.0215, 0.0215, 0.0165), cl, coll, seg=28, rings=14, noise_amp=0.0004, seed=seed + 6); dome.parent = hp; dome.location = (0, -0.0008, 0.0345)
            rings = [(0.000, 0.0230, 0.0090, 0, -0.0150), (-0.022, 0.0260, 0.0075, 0, -0.0160), (-0.044, 0.0275, 0.0070, 0, -0.0150), (-0.052, 0.0262, 0.0065, 0, -0.0145)]
            v, f = loft_z(rings, 28); mk(bpy, name + '_drape', v, f, cl, coll, hp, loc=(0, 0, 0.0245), seed=seed + 7)
            v, f = torus(0.0200, 0.0030, 28, 8, 1.0); mk(bpy, name + '_agal', v, f, mats['band'], coll, hp, loc=(0, -0.0008, 0.0335), seed=seed + 8)
            fl = ellipsoid(bpy, name + '_flapL', (0.0040, 0.0085, 0.020), cl, coll, seg=14, rings=10, seed=seed + 9); fl.parent = hp; fl.location = (-0.0205, -0.002, 0.0090)
            fr = ellipsoid(bpy, name + '_flapR', (0.0040, 0.0085, 0.020), cl, coll, seg=14, rings=10, seed=seed + 10); fr.parent = hp; fr.location = (0.0205, -0.002, 0.0090)
        elif k == 'turban':
            for q in range(3):
                v, f = torus(0.0185 - 0.0010 * q, 0.0052, 30, 8, 0.9); mk(bpy, f'{name}_wrap{q}', v, f, cl, coll, hp, loc=(0, -0.0006, 0.0300 + 0.0068 * q), seed=seed + 11 + q)
            dome = ellipsoid(bpy, name + '_dome', (0.0185, 0.0185, 0.0120), cl, coll, seg=24, rings=12, noise_amp=0.0004, seed=seed + 15); dome.parent = hp; dome.location = (0, -0.0006, 0.0455)
        else:   # scarf: close wrap with a soft back drape
            dome = ellipsoid(bpy, name + '_dome', (0.0210, 0.0212, 0.0190), cl, coll, seg=26, rings=14, noise_amp=0.0004, seed=seed + 6); dome.parent = hp; dome.location = (0, -0.0020, 0.0315)
            rings = [(0.000, 0.0215, 0.0100, 0, -0.0120), (-0.024, 0.0250, 0.0090, 0, -0.0130), (-0.046, 0.0230, 0.0080, 0, -0.0100)]
            v, f = loft_z(rings, 28); mk(bpy, name + '_drape', v, f, cl, coll, hp, loc=(0, 0, 0.0230), seed=seed + 7)
        # arms: shoulder -> elbow -> hand
        self.sh, self.el, self.hand = {}, {}, {}
        for sx, nm in ((-1, 'L'), (1, 'R')):
            sp = pivot(bpy, f'{name}_sh{nm}', coll, body, (sx * 0.0288, 0, 0.082)); ep = pivot(bpy, f'{name}_el{nm}', coll, sp, (0, 0, -0.0260))
            v, f = sweep(*round_caps(np.array([(0, 0, 0.003), (0, 0, -0.013), (0, 0, -0.0265)]), [0.0092, 0.0088, 0.0082], [0.0092, 0.0088, 0.0082]), ring=14); mk(bpy, f'{name}_ua{nm}', v, f, mats['mantle'], coll, sp, seed=seed + 20)
            v, f = sweep(*round_caps(np.array([(0, 0, 0.0), (0, 0, -0.012), (0, 0, -0.0235)]), [0.0082, 0.0078, 0.0068], [0.0082, 0.0078, 0.0068]), ring=14); mk(bpy, f'{name}_fa{nm}', v, f, mats['robe'], coll, ep, seed=seed + 21)
            hd = ellipsoid(bpy, f'{name}_hand{nm}', (0.0066, 0.0062, 0.0072), mats['skin'], coll, seg=14, rings=10, seed=seed + 22); hd.parent = ep; hd.location = (0, 0, -0.0275)
            self.sh[nm], self.el[nm], self.hand[nm] = sp, ep, hd
        self.feet = []
        for sx in (-1, 1):
            ft = ellipsoid(bpy, f'{name}_foot{sx}', (0.0085, 0.0150, 0.0058), mats['shoe'], coll, seg=16, rings=10, seed=seed + 25); ft.parent = root; ft.location = (sx * 0.0120, 0.012, 0.0045); self.feet.append(ft)
        self.objs = [root]; self.brow_bias = {'sasaa': -5.0, 'zayd': -4.0}.get(style, 0.0)
        root.scale = (s, s, s)

    def hide(self, h=True):
        hide(self.root, h)

    def pose(self, loc=(0, 0, 0), yaw=0.0, bob=0.0, lean=0.0, roll=0.0, head=(0.0, 0.0, 0.0), armL=(0, 4, 0), armR=(0, 4, 0), mouth='closed', brow=(0.0, 0.0),
             blink=0.0, step=None, seated=False, twist=0.0, scale=1.0):
        """loc/yaw place the figure; head = (yaw, pitch, roll) deg (pitch + = look up); arm = (pitch fwd, roll out, elbow bend); step = walk phase in turns or None."""
        r = self.root; r.location = loc; r.rotation_euler = (0, 0, D(yaw)); r.scale = (self.sc * scale,) * 3
        self.body.location = (0, 0, bob); self.body.rotation_euler = (D(lean), D(roll), D(twist))
        self.headp.rotation_euler = (D(-head[1]), D(head[2]), D(head[0]))
        for nm, a, sx in (('L', armL, -1), ('R', armR, 1)):
            self.sh[nm].rotation_euler = (D(a[0]), D(-sx * a[1]), 0.0); self.el[nm].rotation_euler = (D(a[2]), 0.0, 0.0)
        for k, m in self.mouths.items(): m.hide_render = (k != mouth)
        for b, sx in zip(self.brows, (-1, 1)):
            b.location = (sx * 0.0070, 0.0172, 0.0268 + brow[0] * 0.0022); b.rotation_euler = (0.0, D(-sx * (brow[1] + self.brow_bias)), 0.0)
        for e in self.eyes: e.scale = (1.0, 1.0, max(0.12, 1.0 - blink * 0.88))
        for ft in self.feet: ft.hide_render = seated
        if seated: self.body.location = (0, 0, bob - 0.026)
        if step is None or seated:
            for ft, sx in zip(self.feet, (-1, 1)): ft.location = (sx * 0.0120, 0.012, 0.0045); ft.rotation_euler = (0, 0, 0)
        else:
            ph = step * 2 * math.pi
            for ft, sx, off in zip(self.feet, (-1, 1), (0.0, math.pi)):
                sw = math.sin(ph + off); lift = max(0.0, math.cos(ph + off))
                ft.location = (sx * 0.0120, 0.012 + 0.016 * sw, 0.0045 + 0.007 * lift); ft.rotation_euler = (D(-14 * lift), 0, 0)


CAMEL_STYLES = {
    'ride': dict(col=(0.80, 0.58, 0.32), col2=(0.70, 0.48, 0.26), belly=1.0, size=1.0),
    'she1': dict(col=(0.86, 0.72, 0.52), col2=(0.76, 0.62, 0.44), belly=1.22, size=0.98),
    'she2': dict(col=(0.62, 0.44, 0.28), col2=(0.52, 0.36, 0.23), belly=1.20, size=1.0),
    'calf': dict(col=(0.88, 0.76, 0.58), col2=(0.78, 0.66, 0.50), belly=1.0, size=0.55),
}

class Camel:
    """Dromedary facing +Y. pose(loc, yaw, gait=None|phase turns, neck=(yaw, pitch), ...)."""
    def __init__(self, bpy, name, style, coll, seed=1, saddle=False):
        st = CAMEL_STYLES[style]; self.sc = st['size']; self.name = name
        mc = clay(bpy, name + '_fur', st['col'], st['col2'], rough=0.8, seed=seed * 3, var_scale=9.0)
        mdk = clay(bpy, name + '_dark', (0.03, 0.025, 0.03), (0.04, 0.03, 0.03), rough=0.3, sss=0.0, seed=seed * 3 + 1)
        mhoof = clay(bpy, name + '_hoof', (0.22, 0.17, 0.13), (0.18, 0.13, 0.10), rough=0.7, seed=seed * 3 + 2)
        root = pivot(bpy, name + '_root', coll); self.root = root
        body = pivot(bpy, name + '_body', coll, root, (0, 0, 0)); self.body = body
        b = st['belly']
        tors = ellipsoid(bpy, name + '_torso', (0.034 * b, 0.092, 0.040 * b), mc, coll, seg=36, rings=20, noise_amp=0.0005, seed=seed); tors.parent = body; tors.location = (0, 0.0, 0.126)
        def part(nm, rad, loc, par=body, rot=(0, 0, 0), sd=0):
            o = ellipsoid(bpy, f'{name}_{nm}', rad, mc, coll, seg=24, rings=14, noise_amp=0.0004, seed=seed + sd); o.parent = par; o.location = loc; o.rotation_euler = rot; return o
        part('hump', (0.025, 0.033, 0.030), (0, -0.012, 0.168), sd=1)
        part('chest', (0.030, 0.040, 0.040), (0, 0.056, 0.118), sd=2)
        part('rump', (0.031 * b, 0.040, 0.036 * b), (0, -0.062, 0.128), sd=3)
        np_ = pivot(bpy, name + '_neckp', coll, body, (0, 0.066, 0.140)); self.neckp = np_
        pts = [(0, 0.0, 0.0), (0, 0.020, 0.030), (0, 0.040, 0.066), (0, 0.054, 0.098)]
        nk = tube(bpy, name + '_neck', pts, [0.0165, 0.0135, 0.0115, 0.0105], mc, coll, n=26, ring=18, lateral=(1, 0, 0), noise_amp=0.0004, seed=seed + 4); nk.parent = np_
        hd = pivot(bpy, name + '_headp', coll, np_, (0, 0.056, 0.100)); self.headp = hd
        part('head', (0.0115, 0.022, 0.0120), (0, 0.010, 0.002), hd, (D(18), 0, 0), 5)
        part('muzzle', (0.0105, 0.012, 0.0095), (0, 0.027, -0.004), hd, (D(18), 0, 0), 6)
        for sx in (-1, 1):
            e = ellipsoid(bpy, f'{name}_eye{sx}', (0.0026, 0.0022, 0.0030), mdk, coll, seg=12, rings=8); e.parent = hd; e.location = (sx * 0.0100, 0.0105, 0.0070)
            part(f'ear{sx}', (0.0042, 0.0030, 0.0090), (sx * 0.0070, 0.0000, 0.0140), hd, (D(-20), D(-sx * 20), 0), 7)
            nos = ellipsoid(bpy, f'{name}_nostril{sx}', (0.0013, 0.0012, 0.0020), mdk, coll, seg=10, rings=6); nos.parent = hd; nos.location = (sx * 0.0042, 0.0375, -0.0038)
        tl = tube(bpy, name + '_tail', [(0, 0, 0), (0, -0.007, -0.020), (0, -0.010, -0.040), (0, -0.007, -0.052)], [0.004, 0.0035, 0.0030, 0.0042], mc, coll, n=14, ring=10, lateral=(1, 0, 0), seed=seed + 8)
        tl.parent = body; tl.location = (0, -0.098, 0.145)
        self.legs = {}
        for key, (lx, ly) in (('FL', (-0.023, 0.058)), ('FR', (0.023, 0.058)), ('HL', (-0.023, -0.064)), ('HR', (0.023, -0.064))):
            hip = pivot(bpy, f'{name}_hip{key}', coll, body, (lx, ly, 0.116)); knee = pivot(bpy, f'{name}_knee{key}', coll, hip, (0, 0, -0.052))
            th = tube(bpy, f'{name}_thigh{key}', [(0, 0, 0.004), (0, 0, -0.026), (0, 0, -0.052)], [0.0108, 0.0092, 0.0082], mc, coll, n=12, ring=14, lateral=(1, 0, 0), seed=seed + 9); th.parent = hip
            sh = tube(bpy, f'{name}_shin{key}', [(0, 0, 0.0), (0, 0, -0.028), (0, 0, -0.054)], [0.0082, 0.0072, 0.0068], mc, coll, n=12, ring=14, lateral=(1, 0, 0), seed=seed + 10); sh.parent = knee
            hf = ellipsoid(bpy, f'{name}_hoof{key}', (0.0098, 0.0128, 0.0045), mhoof, coll, seg=16, rings=8); hf.parent = knee; hf.location = (0, 0.003, -0.0595)
            self.legs[key] = (hip, knee)
        if saddle:
            ms = striped(bpy, name + '_blanket', [(0.55, 0.15, 0.12), (0.92, 0.80, 0.52), (0.18, 0.20, 0.38), (0.92, 0.80, 0.52)], period=0.010, axis=1, widths=[0.4, 0.1, 0.4, 0.1])
            v, f = loft_z([(0.150, 0.0300, 0.040, 0, -0.012), (0.168, 0.0285, 0.0385, 0, -0.012), (0.196, 0.0200, 0.0300, 0, -0.012)], 28, True, False)
            mk(bpy, name + '_saddle', v, f, ms, coll, body, noise_amp=0.0003, seed=seed + 11)
        self.root.scale = (self.sc,) * 3

    def hide(self, h=True): hide(self.root, h)

    def pose(self, loc=(0, 0, 0), yaw=0.0, gait=None, neck=(0.0, 0.0), amp=1.0, pitch=0.0, roll=0.0, rest=0.0):
        """gait = phase in turns (None = standing); neck = (yaw, pitch up+) deg; rest = 0..1 kneel-ish sink."""
        r = self.root; r.location = loc; r.rotation_euler = (0, 0, D(yaw)); r.scale = (self.sc,) * 3
        bob = 0.0; swing = {k: 0.0 for k in self.legs}; kn = {k: 0.0 for k in self.legs}; nod = 0.0; rl = roll
        if gait is not None:
            ph = gait * 2 * math.pi
            for k, off in (('FL', 0.0), ('HL', 0.0), ('FR', math.pi), ('HR', math.pi)):
                sw = math.sin(ph + off); swing[k] = 24.0 * amp * sw; kn[k] = -38.0 * amp * max(0.0, math.cos(ph + off)) if True else 0.0
            bob = 0.0022 * amp * abs(math.sin(ph)) * 1.0; rl = roll + 2.2 * amp * math.sin(ph); nod = 3.5 * amp * math.sin(ph * 2 + 0.6)
        self.body.location = (0, 0, bob - rest * 0.030); self.body.rotation_euler = (D(pitch), D(rl), 0.0)
        self.last = dict(loc=tuple(loc), yaw=yaw, bob=bob - rest * 0.030, pitch=pitch, roll=rl, sc=self.sc)
        for k, (hip, knee) in self.legs.items():
            hip.rotation_euler = (D(swing[k]), 0, 0); knee.rotation_euler = (D(kn[k] + rest * 90.0), 0, 0)
        self.neckp.rotation_euler = (D(-neck[1] * 0.4 + nod * 0.6), 0, D(neck[0] * 0.5)); self.headp.rotation_euler = (D(-neck[1] * 0.6 + nod * 0.4 + 6), 0, D(neck[0] * 0.5))

class Lamp:
    """Small clay oil lamp with an emissive flame and (optionally) a real warm point light."""
    def __init__(self, bpy, name, coll, mat_clay, flame_mat, with_light=True, scale=1.0, seed=1):
        self.root = pivot(bpy, name + '_root', coll)
        d = ellipsoid(bpy, name + '_dish', (0.0125, 0.0125, 0.0055), mat_clay, coll, seg=24, rings=10, noise_amp=0.0003, seed=seed); d.parent = self.root; d.location = (0, 0, 0.0035)
        sp = ellipsoid(bpy, name + '_spout', (0.0042, 0.0075, 0.0034), mat_clay, coll, seg=14, rings=8, seed=seed + 1); sp.parent = self.root; sp.location = (0, 0.0130, 0.0055)
        fl = ellipsoid(bpy, name + '_flame', (0.0030, 0.0030, 0.0072), flame_mat, coll, seg=16, rings=10, shape=lambda x, y, z: (x * (1 - 0.65 * max(0, z)), y * (1 - 0.65 * max(0, z)), z)); fl.parent = self.root; fl.location = (0, 0.0150, 0.0105 + 0.0066)
        set_vis(fl, False); self.flame = fl; self.light = None
        if with_light:
            ld = bpy.data.lights.new(name + '_light', 'POINT'); ld.energy = 0.3; ld.shadow_soft_size = 0.004; ld.use_temperature = True; ld.temperature = 2100
            self.light = bpy.data.objects.new(name + '_light', ld); coll.objects.link(self.light); self.light.parent = self.root; self.light.location = (0, 0.0150, 0.0175)
        self.root.scale = (scale,) * 3; self.scale = scale; self.base_energy = 0.3

    def pose(self, loc, on=1.0, flick=0.0, power=1.0, yaw=0.0):
        self.root.location = loc; self.root.rotation_euler = (0, 0, D(yaw))
        vis = on > 0.01; hide(self.root, not vis)
        if self.light is not None: self.light.hide_render = not vis; self.light.data.energy = self.base_energy * power * on * (1.0 + 0.10 * flick)
        s = on * (1.0 + 0.10 * flick); self.flame.scale = (s, s, s * (1.0 + 0.12 * flick))

class Rope:
    """A hanging rope between two world points; the mesh is rebuilt per pose (pure function of its arguments)."""
    def __init__(self, bpy, name, coll, mat, r=0.0022, n=18, ring=8):
        self.n, self.ring, self.r = n, ring, r; V = [(0, 0, 0)] * (n * ring + 2)
        F = []
        for k in range(n - 1):
            for j in range(ring):
                a = k * ring + j; b = k * ring + (j + 1) % ring; F.append((a, b, b + ring, a + ring))
        for j in range(ring): F.append((n * ring, (j + 1) % ring, j)); F.append((n * ring + 1, (n - 1) * ring + j, (n - 1) * ring + (j + 1) % ring))
        me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
        me.materials.append(mat); self.me = me; self.ob = bpy.data.objects.new(name, me); coll.objects.link(self.ob)

    def set(self, a, b, sag=0.0, visible=True, jitter=0.0):
        self.ob.hide_render = not visible
        if not visible: return
        a = np.array(a, float); b = np.array(b, float); n, ring = self.n, self.ring
        t = np.linspace(0, 1, n)[:, None]; C = a + (b - a) * t; C[:, 2] -= sag * 4 * t[:, 0] * (1 - t[:, 0])
        T = np.gradient(C, axis=0); T /= np.maximum(1e-9, np.linalg.norm(T, axis=1))[:, None]
        up = np.array([0, 0, 1.0]); V = np.zeros((n * ring + 2, 3))
        for k in range(n):
            N1 = np.cross(T[k], up)
            if np.linalg.norm(N1) < 1e-6: N1 = np.array([1.0, 0, 0])
            N1 /= np.linalg.norm(N1); N2 = np.cross(T[k], N1)
            rr = self.r * (1.0 + 0.12 * math.sin(k * 1.9))
            for j in range(ring):
                ph = 2 * math.pi * j / ring; V[k * ring + j] = C[k] + rr * (math.cos(ph) * N1 + math.sin(ph) * N2)
        V[n * ring] = C[0] - T[0] * 1e-4; V[n * ring + 1] = C[-1] + T[-1] * 1e-4
        self.me.vertices.foreach_set('co', V.astype(np.float32).ravel()); self.me.update()


def glow_cloth(bpy, name, col_in=(1.0, 0.62, 0.26), col_out=(0.55, 0.22, 0.08), strength=2.2, cx=0.0, cz=0.05, rad=0.16):
    """Lit cloth seen from outside: warm emission, brightest around the lamp, with a woven thread texture."""
    m, N, L, p, out = _mat(bpy, name)
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL': N.remove(n)
    out = N['Material Output']
    tc = N.new('ShaderNodeTexCoord'); vm = N.new('ShaderNodeVectorMath'); vm.operation = 'DISTANCE'
    L.new(tc.outputs['Object'], vm.inputs[0]); vm.inputs[1].default_value = (cx, 0.0, cz)
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = rad; L.new(vm.outputs['Value'], mr.inputs['Value'])
    mr.interpolation_type = 'SMOOTHSTEP'; mr.clamp = True
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = srgb(col_in); cr.color_ramp.elements[1].color = srgb(col_out); L.new(mr.outputs['Result'], cr.inputs['Fac'])
    wv = N.new('ShaderNodeTexNoise'); wv.inputs['Scale'].default_value = 260.0; wv.inputs['Detail'].default_value = 0.0; L.new(tc.outputs['Object'], wv.inputs['Vector'])
    mm = N.new('ShaderNodeMath'); mm.operation = 'MULTIPLY_ADD'; L.new(wv.outputs['Fac'], mm.inputs[0]); mm.inputs[1].default_value = 0.35; mm.inputs[2].default_value = 0.82
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; sock(mx.inputs, 'Factor_Float').default_value = 1.0
    L.new(cr.outputs['Color'], sock(mx.inputs, 'A_Color')); L.new(mm.outputs['Value'], sock(mx.inputs, 'B_Color'))
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = strength; L.new(sock(mx.outputs, 'Result_Color'), em.inputs['Color']); L.new(em.outputs['Emission'], out.inputs['Surface'])
    return m, em

class Tent:
    """Goat-hair tent: slanted striped roof, back + side walls, poles, guy ropes. Closed = a glowing front curtain with a silhouette on it."""
    W, DP = 0.19, 0.115
    def __init__(self, bpy, name, coll, M, closed=False, seed=1):
        from mathutils import Vector, noise
        self.name = name; self.closed = closed
        root = pivot(bpy, name + '_root', coll); self.root = root
        cloth = M['goat']; W, DP = self.W, self.DP
        def roof_z(x, y):
            u = (y + DP) / (2 * DP)
            z = 0.138 - 0.054 * u + 0.010 * (1 - (x / W) ** 2) * (1 - 0.4 * u)
            return z - 0.050 * smooth(0.10, 0.19, abs(x)) * 1.0
        def hand(vv, amp=0.0012, f=45.0):
            return amp * noise.noise(Vector((vv[0] * f + seed * 5.3, vv[1] * f, vv[2] * f)))
        # roof
        nx, ny = 36, 22; V, F = [], []
        for j in range(ny + 1):
            y = -DP + 2 * DP * j / ny
            for i in range(nx + 1):
                x = -W + 2 * W * i / nx; z = roof_z(x, y); V.append((x, y, z + hand((x, y, z), 0.0012)))
        for j in range(ny):
            for i in range(nx): a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
        mk(bpy, name + '_roof', V, F, cloth, coll, root, noise_amp=0.0, seed=seed)
        # solid thickness lip is implied by the double-sided shader (cloth is thin); walls
        def wall(pts_top, pts_bot, nm):
            n = len(pts_top); Vw = []
            for k in range(7):
                for (tp, bt) in zip(pts_top, pts_bot):
                    t = k / 6.0; v = tuple(bt[a] + (tp[a] - bt[a]) * t for a in range(3)); Vw.append((v[0], v[1], v[2] + hand(v, 0.0015)))
            Fw = [(k * n + i, k * n + i + 1, (k + 1) * n + i + 1, (k + 1) * n + i) for k in range(6) for i in range(n - 1)]
            mk(bpy, name + nm, Vw, Fw, cloth, coll, root, noise_amp=0.0, seed=seed)
        ys = np.linspace(-DP * 0.35, DP, 14)
        for sx in (-1, 1):
            wall([(sx * W, y, roof_z(sx * W, y)) for y in ys], [(sx * W * 1.04, y, 0.0) for y in ys], f'_side{sx}')
        xs = np.linspace(-W, W, 20); wall([(x, DP, roof_z(x, DP)) for x in xs], [(x * 1.04, DP * 1.02, 0.0) for x in xs], '_back')
        # poles + guy ropes
        mp = M['pole']
        for sx in (-1, 1):
            tube(bpy, f'{name}_pole{sx}', [(sx * W * 0.97, -DP, -0.004), (sx * W * 0.97, -DP, 0.07), (sx * W * 0.97, -DP, roof_z(sx * W * 0.97, -DP) + 0.002)], [0.0030, 0.0028, 0.0026], mp, coll, n=10, ring=8, lateral=(1, 0, 0)).parent = root
            pg = (sx * (W + 0.075), -DP - 0.085, 0.0)
            gr = tube(bpy, f'{name}_guy{sx}', [(sx * W, -DP, roof_z(sx * W, -DP)), ((sx * W + pg[0]) / 2, (-DP + pg[1]) / 2, 0.052), pg], [0.0011, 0.0011, 0.0011], M['rope'], coll, n=12, ring=6, lateral=(0, 1, 0)); gr.parent = root
            pg2 = (sx * (W + 0.08), DP + 0.07, 0.0)
            gr2 = tube(bpy, f'{name}_guyb{sx}', [(sx * W, DP, roof_z(sx * W, DP)), ((sx * W + pg2[0]) / 2, (DP + pg2[1]) / 2, 0.034), pg2], [0.0011, 0.0011, 0.0011], M['rope'], coll, n=12, ring=6, lateral=(0, 1, 0)); gr2.parent = root
            for pgx in (pg, pg2):
                pk = ellipsoid(bpy, f'{name}_peg', (0.0028, 0.0028, 0.0070), mp, coll, seg=10, rings=6); pk.parent = root; pk.location = (pgx[0], pgx[1], 0.001)
        # floor rug
        mr = M['rug']; v, f = loft_z([(0.0003, 0.150, 0.088), (0.0030, 0.146, 0.084)], 4 * 8, True, True)
        rg = mk(bpy, name + '_rug', v, f, mr, coll, root, loc=(0, 0.0, 0.0), noise_amp=0.0003, seed=seed)
        self.lamp_pos = (0.03, -0.015, 0.003)
        if closed:
            Vc, Fc = [], []; nxc, nzc = 30, 14
            for j in range(nzc + 1):
                for i in range(nxc + 1):
                    x = -W + 2 * W * i / nxc; zt = roof_z(x, -DP); z = zt * j / nzc
                    Vc.append((x * 1.0, -DP - 0.004 * math.sin(math.pi * i / nxc) * math.sin(math.pi * j / nzc / 1.1), z))
            for j in range(nzc):
                for i in range(nxc): a = j * (nxc + 1) + i; Fc.append((a, a + nxc + 1, a + nxc + 2, a + 1))
            self.glow_mat, self.glow_em = glow_cloth(bpy, name + '_glow', cz=0.05, rad=0.19)
            self.curtain = mk(bpy, name + '_curtain', Vc, Fc, self.glow_mat, coll, root, noise_amp=0.0, seed=seed)
            set_vis(self.curtain, False)
            # seam + flap tie lines
            mk(bpy, name + '_seam', *sweep(*round_caps(np.array([(0.0, -DP - 0.0045, 0.002), (0.0, -DP - 0.0045, 0.06), (0.0, -DP - 0.0045, 0.12)]), [0.0012] * 3, [0.0012] * 3), ring=6), M['pole'], coll, root)
            dk = M['sil']; self.sil = {}
            y0 = -DP - 0.0058
            def cut(nm, rad, loc):
                o = ellipsoid(bpy, f'{name}_sil_{nm}', rad, dk, coll, seg=22, rings=12, noise_amp=0.0004, noise_freq=100.0, seed=seed + len(nm)); o.parent = root; o.location = loc; set_vis(o, False); self.sil[nm] = o; return o
            cut('head', (0.0125, 0.0014, 0.0135), (-0.030, y0, 0.088)); cut('veil', (0.0205, 0.0014, 0.0300), (-0.030, y0, 0.064)); cut('body', (0.0265, 0.0014, 0.0300), (-0.030, y0, 0.034))
            cut('arm', (0.0090, 0.0014, 0.0220), (-0.0065, y0, 0.044)); self.sil['arm'].rotation_euler = (0, D(35), 0)
            cut('bundle', (0.0125, 0.0014, 0.0078), (0.000, y0, 0.048)); self.sil['bundle'].rotation_euler = (0, D(-25), 0)
            cut('bhead', (0.0062, 0.0014, 0.0064), (0.0095, y0, 0.0545))
            self.sil_keys = ['head', 'veil', 'body', 'arm']
        else:
            self.curtain = None

    def hide(self, h=True): hide(self.root, h)

    def show(self, sil=()):
        """Show the tent; silhouettes only for the names listed."""
        hide(self.root, False)
        if self.closed:
            for k, o in self.sil.items(): o.hide_render = k not in sil
