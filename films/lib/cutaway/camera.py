"""Camera presets of the Cutaway line (pure numpy): a preset name + a few parameters -> the camera at any moment.

Every move is a real operator's move: an ease in, a steady middle, an ease out, over the whole shot (never sped up to
fit the narration). pose(shot, layout, u, aspect) returns position, target, lens, focus distance, f-stop and roll; the
engine applies it to the Blender camera, the validator measures its screen speed (CRAFT.md section 4).
Coordinates: metres, the block centred on the origin, the turf near z = 0, the camera-facing cut faces -Y and +X.
"""
import math

import numpy as np

CAMERAS_OK = ['map', 'orbit', 'push', 'pull', 'ground', 'crane', 'macro', 'hero']


def ease_io(u, a=0.25):
    """Ease in, steady middle, ease out: a = share of the move spent easing at each end."""
    u = max(0.0, min(1.0, u)); n = 1 - a
    if u < a: return u * u / (2 * a) / n
    if u < 1 - a: return (a / 2 + (u - a)) / n
    return 1 - (1 - u) ** 2 / (2 * a * n)


def ease5(u):
    u = max(0.0, min(1.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)


def sph(az, el):
    a, e = math.radians(az), math.radians(el)
    return np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])


def tans(lens, aspect):
    """tan of the half field of view (horizontal, vertical) for a 36 mm sensor fitted to the larger side."""
    asp = 16 / 9 if aspect == '16:9' else 9 / 16
    th = 18.0 / lens
    return (th, th / asp) if asp >= 1 else (th * asp, th)


def basis(pos, tgt, roll=0.0):
    pos = np.asarray(pos, float); f = np.asarray(tgt, float) - pos; f /= np.linalg.norm(f) + 1e-12
    up0 = np.array([0, 1.0, 0]) if abs(f[2]) > 0.999 else np.array([0, 0, 1.0])
    r = np.cross(f, up0); r /= np.linalg.norm(r) + 1e-12; u = np.cross(r, f)
    if roll:
        c, s = math.cos(math.radians(roll)), math.sin(math.radians(roll)); r, u = c * r + s * u, -s * r + c * u
    return f, r, u


def fit(L, az, el, lens, aspect, fill, target=None, top_extra=0.45):
    """The kit's framing: the block's bounding box at `fill` of the frame, centred, from azimuth/elevation (degrees)."""
    sx, sy = L.size; tanh, tanv = tans(lens, aspect)
    tgt = np.array((0, 0, -L.depth * 0.42) if target is None else target, float)
    pts = np.array([(x, y, z) for x in (-sx / 2, sx / 2) for y in (-sy / 2, sy / 2) for z in (-L.depth, top_extra)])
    dist = 8.0; dvec = sph(az, el)
    for _ in range(6):
        cp = tgt + dist * dvec; fwd = -dvec; right = np.cross(fwd, (0, 0, 1)); right /= np.linalg.norm(right); up = np.cross(right, fwd)
        v = pts - cp; z = v @ fwd; uu = (v @ right) / z / tanh; w = (v @ up) / z / tanv
        tgt = tgt + right * ((uu.max() + uu.min()) / 2 * tanh * dist) + up * ((w.max() + w.min()) / 2 * tanv * dist)
        span = max((uu.max() - uu.min()) / 2, (w.max() - w.min()) / 2); dist *= span / fill
    return tgt, dist


FACE = {   # origin offset, along (u), outward normal, lean toward the front corner
    '-Y': (lambda L: np.array([0.0, -L.sy / 2, 0.0]), np.array([1.0, 0, 0]), np.array([0, -1.0, 0]), 1.0),
    '+X': (lambda L: np.array([L.sx / 2, 0.0, 0.0]), np.array([0, 1.0, 0]), np.array([1.0, 0, 0]), -1.0),
}


def target_point(L, ref):
    """A shot target: an egg id or kind, "water", "mill", "house", or [x, y, z]. None when unknown."""
    if ref is None: return None
    if isinstance(ref, (list, tuple)) and len(ref) == 3: return np.array(ref, float)
    if isinstance(ref, str):
        r = ref[4:] if ref.startswith('egg:') else ref
        p = L.egg_point(r)
        if p is not None: return np.array(p, float)
        if r == 'water':
            w = L.water_point('-Y'); return None if w is None else np.array((w[0], w[1], (L.level or 0.0)), float)
        if r == 'mill' and L.mill: return np.array((L.mill[0], L.mill[1], 0.1), float)
        if r == 'house' and L.houses: return np.array((L.houses[0][0], L.houses[0][1], 0.08), float)
    return None


def pose(shot, L, u, aspect='16:9'):
    """The camera of `shot` (dict: camera + params) on layout L at local progress u (0..1)."""
    cam = shot['camera']; k = L.sx / 4.0; v = aspect == '9:16'; d = shot.get('dir', 1) or 1
    if cam == 'map':
        e = ease_io(u); tanh, tanv = tans(50.0, aspect); fill = shot.get('fill', 0.86)
        H = max(L.sx, L.sy) / fill / (2 * min(tanh, tanv)) * 1.06
        drift = 0.06 * k * d
        pos = (0.08 * k - drift * e, -0.05, H * (1 - 0.04 * e)); tgt = (0.08 * k - drift * e, -0.049, 0.0)
        return dict(pos=pos, tgt=tgt, lens=50.0, focus=H, fstop=16.0, roll=shot.get('roll', 22.0) + shot.get('turn', 6.0) * d * e)
    if cam in ('orbit', 'push', 'pull'):
        e = ease_io(u); el = shot.get('el', 27.0 if v else 30.0); az0 = shot.get('az', -50.0); lens = shot.get('lens', 50.0)
        if cam == 'orbit':
            tgt, dist = fit(L, az0, el, lens, aspect, shot.get('fill', 0.93 if v else 0.86))
            az = az0 + shot.get('deg', 8.0) * d * e
            return dict(pos=tuple(tgt + dist * sph(az, el)), tgt=tuple(tgt), lens=lens, focus=dist, fstop=11.0, roll=0.0)
        tgt0, dist0 = fit(L, az0, el, lens, aspect, shot.get('fill', 0.93 if v else 0.86))
        T = target_point(L, shot.get('target'))
        amount = shot.get('amount', 0.22)
        if cam == 'pull': e = 1 - e
        tgt = tgt0 if T is None else tgt0 + (T - tgt0) * e * shot.get('aim', 0.6)
        dist = dist0 * (1 - amount * e); az = az0 + shot.get('deg', 3.0) * d * (e if cam == 'push' else 1 - e)
        return dict(pos=tuple(tgt + dist * sph(az, el)), tgt=tuple(tgt), lens=lens, focus=dist, fstop=11.0, roll=0.0)
    if cam == 'ground':
        e = ease_io(u); c = np.array([L.sx / 2, -L.sy / 2, 0.0])
        pos = c + np.array([0.36 * k, -0.52 * k, 0.30]) + (np.array([-0.12, 0.07, -0.01]) * k) * e
        tgt = np.array([-0.8 * k, -L.sy / 2 + 0.6 * k, -0.22])
        foc = float(np.linalg.norm(pos - np.array([0.66 * k, -L.sy / 2 + 0.15 * k, 0.0])))
        return dict(pos=tuple(pos), tgt=tuple(tgt), lens=24.0 if v else 28.0, focus=foc, fstop=5.6, roll=0.0)
    if cam == 'crane':
        face = shot.get('face', '-Y'); o, r, out, lean = FACE[face]; o = o(L)
        e = ease5(u) if shot.get('ease', 'smooth') == 'smooth' else ease_io(u)
        to = shot.get('to'); uu = shot.get('u')
        z1 = -L.depth * 0.7
        if isinstance(to, str):
            p = L.egg_point(to[4:] if to.startswith('egg:') else to)
            if p is not None:
                eg = L.egg(to[4:] if to.startswith('egg:') else to); z1 = p[2]; uu = eg['u'] if uu is None else uu
        elif isinstance(to, (int, float)): z1 = -float(to)
        uu = 0.0 if uu is None else float(uu); z0 = shot.get('from', 0.32)
        tz = z0 + (z1 - z0) * e; el = math.radians(20 - 19 * e); D = shot.get('dist', 2.45 * k * (0.85 if v else 1.0))
        tgt = o + r * uu + np.array([0, 0, tz]); pos = tgt + r * (0.30 * k * lean) + out * D + np.array([0, 0, D * math.tan(el)])
        return dict(pos=tuple(pos), tgt=tuple(tgt), lens=36.0 if v else 40.0, focus=D / math.cos(el), fstop=5.6, roll=0.0)
    if cam == 'macro':
        T = target_point(L, shot.get('target'))
        eg = L.egg(shot['target'][4:] if str(shot.get('target', '')).startswith('egg:') else shot.get('target')) if isinstance(shot.get('target'), str) else None
        face = eg['face'] if eg else '-Y'; o, r, out, lean = FACE[face]
        if T is None: T = o(L) + np.array([0, 0, -0.5])
        c = T + r * (-0.04) + np.array([0, 0, -0.01])
        kk = 1.0 - shot.get('amount', 0.10) * ease_io(u); off = (r * 0.50 * lean + out * 0.92 + np.array([0, 0, 0.13])) * kk * shot.get('dist', 1.0)
        return dict(pos=tuple(c + off), tgt=tuple(c), lens=45.0 if v else 55.0, focus=float(np.linalg.norm(off)), fstop=4.0, roll=0.0)
    if cam == 'hero':
        e = ease_io(u); az = math.radians(shot.get('az', -46.0) + shot.get('deg', 8.0) * d * e); el = math.radians(shot.get('el', 3.0))
        D = 4.6 * k * (1.3 if v else 1.0); tgt = np.array((0.15 * k, -0.15 * k, -0.36 * L.depth / 1.6))
        pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
        return dict(pos=tuple(pos), tgt=tuple(tgt), lens=24.0 if v else 28.0, focus=D - 2.0 * k, fstop=8.0, roll=0.0)
    raise ValueError(f'unknown camera {cam!r}')


# ------------------------------------------------------------------ speed (CRAFT.md section 4), measured on screen
def _samples(L):
    xs = np.linspace(-L.sx / 2, L.sx / 2, 9); ys = np.linspace(-L.sy / 2, L.sy / 2, 9); zs = np.linspace(-L.depth, 0.0, 7)
    top = [(x, y, float(L.height(np.array([x]), np.array([y]))[0])) for x in xs for y in ys]
    fy = [(x, -L.sy / 2, z) for x in xs for z in zs]; fx = [(L.sx / 2, y, z) for y in ys for z in zs]
    pts = np.array(top + fy + fx, float)
    eggs = [L.egg_point(e['id']) for e in L.eggs]
    return np.vstack([pts] + [np.array([p], float) for p in eggs if p is not None])


def project(c, pts, aspect):
    f, r, u = basis(c['pos'], c['tgt'], c.get('roll', 0.0)); tanh, tanv = tans(c['lens'], aspect)
    v = pts - np.asarray(c['pos'], float); z = v @ f
    with np.errstate(divide='ignore', invalid='ignore'):
        x = (v @ r) / z / tanh / 2; y = (v @ u) / z / tanv / 2
    return x, y, z


def speed(shot, L, dur, aspect='16:9', n=40):
    """Peak screen speeds over the shot: pan (frames per second: the median slide of what is in frame, the zoom part
    removed) and push (scale change per second, from the camera's distance to its target and the lens)."""
    pts = _samples(L); fps = n / max(dur, 1e-3); pan = 0.0; push = 0.0
    prev = None
    for i in range(n + 1):
        uu = i / n; c = pose(shot, L, uu, aspect); x, y, z = project(c, pts, aspect)
        dist = float(np.linalg.norm(np.asarray(c['tgt']) - np.asarray(c['pos']))) / c['lens']
        if prev is not None:
            px, py, pz, pd = prev
            ok = (z > 0.05) & (pz > 0.05) & (np.abs(x) < 0.5) & (np.abs(y) < 0.5) & (np.abs(px) < 0.5) & (np.abs(py) < 0.5)
            zr = math.log(pd / dist) if dist > 0 and pd > 0 else 0.0
            if ok.sum() >= 4:
                dx = x[ok] - px[ok] * (1 + zr); dy = y[ok] - py[ok] * (1 + zr)
                pan = max(pan, float(np.median(np.hypot(dx, dy))) * fps)
            push = max(push, abs(zr) * fps)
        prev = (x, y, z, dist)
    return {'pan': round(pan, 3), 'push': round(push, 3)}
