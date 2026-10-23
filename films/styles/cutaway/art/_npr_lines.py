"""Shared helpers for the line-art looks of the Cutaway line (storybook-ink, blueprint, chalkboard, engraving).

Not a look itself (no apply()). A look imports it with
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import _npr_lines as NL
and calls NL.setup(bpy, film, ctx, stylize, ...) from its apply(), NL.frame(...) from its frame().

How a line-art look renders (two renders per frame, both inside the look's frame() hook, so any runner can do it):
  1. CAPTURE: the real scene is rendered by Cycles (the film's own samples) with the overlay (labels, title) hidden. A
     compositor File Output writes the passes to a temp folder as float EXR: Combined (linear), Diffuse Colour (albedo),
     Normal, Position (world), Depth, Material Index, Object Index and any AOV the look asked for. They are read back as
     numpy arrays (bpy loads the EXR, no extra library).
  2. STYLIZE: the look's stylize(P, info) -> RGB (display sRGB, floats 0..1, top row first) is plain numpy (FFT blurs, noise,
     edge detection, world-locked hatching from the Position pass). No scipy, no OpenCV: the free runners only have numpy.
  3. FINAL: the harness's own render then draws the overlay objects alone (labels, title, set in code and crisp) over that
     picture through the compositor (Alpha Over) and writes the frame. Everything else is hidden for that render, so it costs
     about a second.
Passes in, hatching and lines out: the hatching is locked to the world (Position pass), so it does not swim when the camera
moves. Paper and chalk textures are fixed to the screen (as in any hand-made frame).

Cost: the capture render costs what the reference render costs (same scene, same samples; the volume rays and the glass are
still there, the look may switch some off), plus about 1 to 3 s of numpy per 1280x720 frame, plus about 1 s for the final.
"""
import glob
import os
import tempfile

import numpy as np

# ------------------------------------------------------------------------------------------- material classes (Material Index)
# 0 sky / nothing; the id of a pixel says what kind of thing it shows, so a look can treat grass, foliage or soil differently
CLS = dict(sky=0, strata=1, bottom=2, top=3, grass=4, leaf=5, bark=6, water=7, rock=8, build=9, find=10, animal=11, plant=12, floor=13, fly=14)
_MAT_RULES = [
    ('cw_strata', 'strata'), ('cw_bottom', 'bottom'), ('cw_top', 'top'), ('cw_water', 'water'), ('ex_wellwater', 'water'), ('_rip_mat', 'water'),
    ('cw_grass', 'grass'), ('cw_leaf', 'leaf'), ('cw_bark', 'bark'), ('cw_birch', 'bark'),
    ('cw_rock', 'rock'), ('cw_bankrock', 'rock'), ('cw_pebble', 'rock'),
    ('cw_wall', 'build'), ('cw_roof', 'build'), ('cw_window', 'build'), ('cw_door', 'build'), ('cw_millwood', 'build'), ('cw_bridgewood', 'build'),
    ('cw_iron', 'build'), ('cw_lamphead', 'build'),
    ('cw_bloom', 'plant'), ('cw_stem', 'plant'), ('cw_reed', 'plant'), ('cw_cattail', 'plant'), ('cw_lily', 'plant'), ('cw_weed', 'plant'),
    ('ex_floor', 'floor'), ('ex_gobo', 'floor'), ('cw_bird', 'fly'), ('_petals', 'fly'), ('_bfly', 'fly'),
    ('ex_deer', 'animal'), ('ex_fox', 'animal'), ('ex_heron', 'animal'), ('ex_duck', 'animal'), ('ex_fish', 'animal'), ('ex_fin', 'animal'),
    ('ex_mole', 'animal'), ('ex_hog', 'animal'), ('ex_spines', 'animal'), ('_fur', 'animal'), ('ex_pink', 'animal'), ('ex_nose', 'animal'),
    ('ex_beak', 'animal'), ('ex_eye', 'animal'),
    # the seasons loop (films/cutaway/loops/seasons) names its materials sz_*
    ('sz_strata', 'strata'), ('sz_top', 'top'), ('sz_block', 'bottom'), ('sz_water', 'water'), ('sz_ice', 'water'), ('sz_grass', 'grass'),
    ('sz_leaf', 'leaf'), ('sz_needles', 'leaf'), ('sz_pines', 'leaf'), ('sz_trees', 'leaf'), ('sz_bark', 'bark'), ('sz_birch', 'bark'),
    ('sz_bankstones', 'rock'), ('sz_boulders', 'rock'), ('sz_bedstones', 'rock'), ('sz_flowers', 'plant'), ('sz_reeds', 'plant'),
    ('sz_weed', 'plant'), ('sz_lilies', 'plant'), ('sz_fallen', 'fly'), ('sz_leaves', 'fly'), ('sz_flake', 'fly'), ('sz_snow', 'top'),
    ('sz_duck', 'animal'), ('sz_fish', 'animal'), ('sz_fin', 'animal'), ('sz_frog', 'animal'), ('sz_fur', 'animal'), ('sz_robin', 'animal'),
    ('sz_squirrel', 'animal'), ('sz_bird', 'animal'), ('sz_eye', 'animal'), ('sz_fly', 'fly'), ('sz_flywing', 'fly'),
]


def classify_materials(bpy):
    """Give every material the pass index of its class (ex_* finds and anything unnamed above = 'find')."""
    for m in bpy.data.materials:
        n = m.name; c = None
        for key, cls in _MAT_RULES:
            if n.startswith(key) or (key.startswith('_') and key in n): c = cls; break
        if c is None: c = 'find' if n.startswith('ex_') else 'find'
        m.pass_index = CLS[c]


# ------------------------------------------------------------------------------------------- capture / final through bpy
class Runner:
    def __init__(self, bpy, film, ctx, stylize, aovs=(), passes=None, samples=None, mat_hook=None):
        self.bpy = bpy; self.film = film; self.ctx = ctx; self.stylize = stylize; self.aovs = list(aovs)
        self.W, self.H = ctx['W'], ctx['H']; self.samples = samples
        self.dir = tempfile.mkdtemp(prefix='kf_npr_'); self.saved = None; self.n = 0
        sc = bpy.context.scene; vl = sc.view_layers[0]
        classify_materials(bpy)
        k = 0
        for st in getattr(film, 'built', {}).values():      # one object index per object: boundaries between objects become lines
            for ob in st['objs']:
                if ob.type == 'MESH': k += 1; ob.pass_index = k
        for a in ('use_pass_normal', 'use_pass_z', 'use_pass_position', 'use_pass_diffuse_color', 'use_pass_material_index', 'use_pass_object_index'):
            setattr(vl, a, True)
        for name in self.aovs: self._aov(vl, name)
        self.cap_group = self._capture_group(sc)
        self.fin_group = None
        self.img = None
        self.over = [e.ob for e in getattr(getattr(film, 'O', None), 'items', [])]      # overlay objects (labels, title): only these are drawn in the final render
        sc.compositing_node_group = self.cap_group
        self.orig = dict(samples=sc.cycles.samples, denoise=sc.cycles.use_denoising, adapt=sc.cycles.use_adaptive_sampling,
                         transp=sc.render.film_transparent, vt=sc.view_settings.view_transform, look=sc.view_settings.look,
                         exp=sc.view_settings.exposure)
        if samples: self.orig['samples'] = samples

    # --- aov
    def _aov(self, vl, name):
        for a in vl.aovs:
            if a.name == name: return
        a = vl.aovs.add(); a.name = name; a.type = 'VALUE'

    # --- compositor groups
    def _capture_group(self, sc):
        bpy = self.bpy
        ng = bpy.data.node_groups.new('npr_capture', 'CompositorNodeTree')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = ng.nodes.new('CompositorNodeRLayers'); fo = ng.nodes.new('CompositorNodeOutputFile'); go = ng.nodes.new('NodeGroupOutput')
        fo.format.media_type = 'IMAGE'; fo.format.file_format = 'OPEN_EXR'; fo.format.color_depth = '32'; fo.format.color_mode = 'RGBA'
        fo.directory = self.dir; fo.file_name = 'p_'
        fo.file_output_items.clear()
        want = [('img', 'Image', 'RGBA'), ('alb', 'Diffuse Color', 'RGBA'), ('nrm', 'Normal', 'RGBA'), ('pos', 'Position', 'RGBA'),
                ('dep', 'Depth', 'FLOAT'), ('ma', 'Material Index', 'FLOAT'), ('ob', 'Object Index', 'FLOAT')] + [(a, a, 'FLOAT') for a in self.aovs]
        for i, (nm, out, ty) in enumerate(want):
            fo.file_output_items.new(ty, nm); ng.links.new(rl.outputs[out], fo.inputs[i])
        ng.links.new(rl.outputs['Image'], go.inputs[0])
        self.names = [w[0] for w in want]
        return ng

    def _final_group(self, sc):
        bpy = self.bpy
        ng = bpy.data.node_groups.new('npr_final', 'CompositorNodeTree')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        im = ng.nodes.new('CompositorNodeImage'); rl = ng.nodes.new('CompositorNodeRLayers'); ao = ng.nodes.new('CompositorNodeAlphaOver')
        go = ng.nodes.new('NodeGroupOutput')
        self.img = bpy.data.images.new('npr_picture', self.W, self.H, alpha=False, float_buffer=True)
        self.img.colorspace_settings.name = 'Linear Rec.709'
        im.image = self.img
        ng.links.new(im.outputs['Image'], ao.inputs['Background']); ng.links.new(rl.outputs['Image'], ao.inputs['Foreground'])
        ng.links.new(ao.outputs[0], go.inputs[0])
        return ng

    # --- one frame
    def restore(self):
        """Undo the previous frame's final-render state (objects hidden, 1 sample, standard view transform)."""
        bpy = self.bpy; sc = bpy.context.scene
        if self.saved is not None:
            shown, objs = self.saved
            if getattr(self.film, 'shown', None) == shown:
                for ob, h in objs:
                    try: ob.hide_render = h
                    except ReferenceError: pass
            self.saved = None
        o = self.orig; cy = sc.cycles
        cy.samples = o['samples']; cy.use_denoising = o['denoise']; cy.use_adaptive_sampling = o['adapt']; sc.render.film_transparent = o['transp']
        sc.view_settings.view_transform = o['vt']
        try: sc.view_settings.look = o['look']
        except Exception: pass
        sc.view_settings.exposure = o['exp']

    def read(self, name):
        bpy = self.bpy; ps = glob.glob(os.path.join(self.dir, 'p_' + name + '*.exr'))
        if not ps: raise RuntimeError(f'pass {name} was not written to {self.dir}')
        im = bpy.data.images.load(ps[0], check_existing=False); im.colorspace_settings.name = 'Non-Color'
        a = np.empty(len(im.pixels), np.float32); im.pixels.foreach_get(a); w, h = im.size; bpy.data.images.remove(im)
        os.remove(ps[0])
        return a.reshape(h, w, -1)[::-1]

    def capture(self):
        bpy = self.bpy; sc = bpy.context.scene
        for p in glob.glob(os.path.join(self.dir, 'p_*')): os.remove(p)
        self.over_hide = [(ob, ob.hide_render) for ob in self.over]
        for ob in self.over: ob.hide_render = True        # the overlay is added after the stylization
        sc.compositing_node_group = self.cap_group
        sc.render.film_transparent = False
        bpy.ops.render.render(write_still=False)
        P = {}
        for nm in self.names:
            a = self.read(nm)
            P[nm] = a[..., :3].astype(np.float32) if nm in ('img', 'alb', 'nrm', 'pos') else a[..., 0].astype(np.float32)
        return P

    def finish(self, rgb):
        """Put the stylized picture and the overlay into the scene the harness is about to render (all else hidden, 1 sample)."""
        bpy = self.bpy; sc = bpy.context.scene
        if self.fin_group is None: self.fin_group = self._final_group(sc)
        for ob, h in self.over_hide: ob.hide_render = h
        lin = srgb_to_lin(np.clip(rgb, 0, 1))
        px = np.ones((self.H, self.W, 4), np.float32); px[..., :3] = lin[::-1]
        self.img.pixels.foreach_set(px.ravel()); self.img.update()
        sc.compositing_node_group = self.fin_group
        objs = []
        for st in getattr(self.film, 'built', {}).values():
            for ob in st['objs']:
                try:
                    if not ob.hide_render: objs.append((ob, False)); ob.hide_render = True
                except ReferenceError: pass
        self.saved = (getattr(self.film, 'shown', None), objs)
        cy = sc.cycles; cy.samples = 1; cy.use_denoising = False; cy.use_adaptive_sampling = False; sc.render.film_transparent = True
        sc.view_settings.view_transform = 'Standard'
        try: sc.view_settings.look = 'None'
        except Exception: pass
        sc.view_settings.exposure = 0.0
        # the overlay items re-draw themselves each frame (hide_render follows their alpha): nothing to restore for them

    def info(self, t, shot):
        d = {'t': t, 'shot': (shot or {}).get('camera', ''), 'W': self.W, 'H': self.H, 'frame': self.n}
        return d


def setup(bpy, film, ctx, stylize, aovs=(), samples=None):
    """Called by a look's apply(); returns the Runner (kept on the film as film.npr)."""
    r = Runner(bpy, film, ctx, stylize, aovs=aovs, samples=samples); film.npr = r; return r


def frame(bpy, film, ctx, t, shot, extra=None):
    """Called by a look's frame(): capture, stylize, hand the picture to the final render."""
    import time
    r = film.npr; r.restore()
    t0 = time.time(); P = r.capture(); t1 = time.time()
    info = r.info(t, shot)
    pal = strata_palette(film)
    if pal is not None: info['strata'] = np.asarray(pal, np.float32)
    if extra: info.update(extra(bpy, film, ctx, t, shot))
    dump = os.environ.get('KF_NPR_DUMP')
    if dump:
        np.savez_compressed(dump, **P, **{'info_' + k: np.asarray(v) for k, v in info.items() if isinstance(v, (int, float, str, np.ndarray, list, tuple))})
    rgb = r.stylize(P, info); t2 = time.time()
    r.finish(rgb); r.n += 1
    print(f'npr frame: capture {t1 - t0:.1f}s, stylize {t2 - t1:.1f}s', flush=True)


# =================================================================================================================== numpy toolkit
def srgb_to_lin(c):
    c = np.asarray(c, np.float32); return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


def lin_to_srgb(c):
    c = np.clip(np.asarray(c, np.float32), 0, None); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055).astype(np.float32)


def lum(c):
    return (0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]).astype(np.float32)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-12), 0.0, 1.0); return t * t * (3 - 2 * t)


def mix(a, b, t):
    t = np.asarray(t, np.float32)
    if np.ndim(a) == 3 and t.ndim == 2: t = t[..., None]
    return a + (b - a) * t


_kcache = {}


def _gauss_kernel_f(shape, sigma):
    key = (shape, round(float(sigma), 3))
    if key not in _kcache:
        if len(_kcache) > 40: _kcache.clear()
        h, w = shape; fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.rfftfreq(w)[None, :]
        _kcache[key] = np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2)).astype(np.float32)
    return _kcache[key]


def blur(a, sigma):
    """Gaussian blur (FFT, wraps at the borders: fine for a picture whose borders are paper)."""
    if sigma <= 0.05: return a
    a = np.asarray(a, np.float32)
    if a.ndim == 3: return np.stack([blur(a[..., i], sigma) for i in range(a.shape[2])], -1)
    k = _gauss_kernel_f(a.shape, sigma); return np.fft.irfft2(np.fft.rfft2(a) * k, s=a.shape).astype(np.float32)


def blur_edge(a, sigma):
    """Blur with the borders replicated (no wrap): pads by 3 sigma first."""
    p = int(3 * sigma) + 1
    if a.ndim == 3: pad = ((p, p), (p, p), (0, 0))
    else: pad = ((p, p), (p, p))
    b = blur(np.pad(a, pad, mode='edge'), sigma); return b[p:-p, p:-p]


_ncache = {}


def noise(shape, sigma, seed=0, aniso=(1.0, 1.0)):
    """Smooth band-limited noise, mean 0, std 1 (white noise blurred; cached per shape/sigma/seed)."""
    key = (shape, round(float(sigma), 3), seed, aniso)
    if key not in _ncache:
        if len(_ncache) > 60: _ncache.clear()
        rng = np.random.default_rng(seed * 7919 + int(sigma * 100)); w = rng.standard_normal(shape).astype(np.float32)
        if aniso == (1.0, 1.0): n = blur(w, sigma)
        else:   # anisotropic: different sigma per axis (fibres)
            h, wd = shape; fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.rfftfreq(wd)[None, :]
            k = np.exp(-2 * (np.pi ** 2) * ((sigma * aniso[0]) ** 2 * fx ** 2 + (sigma * aniso[1]) ** 2 * fy ** 2)).astype(np.float32)
            n = np.fft.irfft2(np.fft.rfft2(w) * k, s=shape).astype(np.float32)
        _ncache[key] = (n / (n.std() + 1e-9)).astype(np.float32)
    return _ncache[key]


def fbm(shape, sigma, seed=0, octaves=4, gain=0.55):
    """Fractal noise, std about 1: octaves from sigma down to sigma / 2^(octaves-1)."""
    out = np.zeros(shape, np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        s = sigma / (2 ** o)
        if s < 0.6: break
        out += amp * noise(shape, s, seed + o * 17); tot += amp * amp; amp *= gain
    return (out / np.sqrt(max(tot, 1e-6))).astype(np.float32)


def grad(a):
    """Central differences (gy, gx)."""
    gy = np.zeros_like(a); gx = np.zeros_like(a)
    gy[1:-1] = (a[2:] - a[:-2]) * 0.5; gx[:, 1:-1] = (a[:, 2:] - a[:, :-2]) * 0.5
    return gy, gx


def gradmag(a):
    gy, gx = grad(a); return np.sqrt(gx * gx + gy * gy)


def dilate(m, r):
    """Max filter of radius r (square-ish, separable) for a mask."""
    r = int(round(r))
    if r <= 0: return m
    out = m
    for ax in (0, 1):
        acc = out.copy()
        for s in range(1, r + 1):
            acc = np.maximum(acc, np.roll(out, s, ax)); acc = np.maximum(acc, np.roll(out, -s, ax))
        out = acc
    return out


def warp(img, dx, dy):
    """Sample img at (x + dx, y + dy), bilinear, edges clamped. img (H,W) or (H,W,C); dx, dy (H,W) in pixels."""
    H, W = dx.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x = np.clip(xx + dx, 0, W - 1.001); y = np.clip(yy + dy, 0, H - 1.001)
    x0 = x.astype(np.int32); y0 = y.astype(np.int32); fx = x - x0; fy = y - y0
    def g(yi, xi): return img[yi, xi]
    if img.ndim == 3: fx = fx[..., None]; fy = fy[..., None]
    return (g(y0, x0) * (1 - fx) * (1 - fy) + g(y0, x0 + 1) * fx * (1 - fy) + g(y0 + 1, x0) * (1 - fx) * fy + g(y0 + 1, x0 + 1) * fx * fy).astype(np.float32)


def px_scale(W):
    """1.0 at 1280 px wide: multiply pixel sizes by this so a look is the same at any delivery size."""
    return W / 1280.0


# ------------------------------------------------------------------------------------------------------------- scene analysis
def region_ids(P, cls_names=None):
    """Material class per pixel (int8) and a sky mask."""
    ma = np.rint(P['ma']).astype(np.int16); sky = (P['dep'] > 1e8) | (P['nrm'].sum(-1) == 0)
    return ma, sky


def cls_mask(ma, *names):
    m = np.zeros(ma.shape, bool)
    for n in names: m |= ma == CLS[n]
    return m


def edge_maps(P, px=1.0, grass_soft=True):
    """Three edge strengths in 0..1 from the passes: 'sil' (object and material boundaries, silhouettes), 'crease'
    (normal changes inside a surface) and 'depth' (depth jumps). The index passes are rounded first, so a boundary is
    one pixel wide whatever the antialiasing did to the pass."""
    ma, sky = region_ids(P)
    d = P['dep'].copy(); d[sky] = np.nanmax(d[~sky]) * 1.5 if (~sky).any() else 1.0
    cls = np.where(sky, 0, ma).astype(np.float32)
    # silhouettes: class or object index differs from a neighbour (4-neighbourhood, one pixel), grass interior ignored
    ob = np.rint(P['ob']).astype(np.int32)
    key = cls * 4096 + ob.astype(np.float32)
    e = np.zeros(cls.shape, np.float32)
    for ax in (0, 1):
        dd = np.abs(key - np.roll(key, 1, ax)) > 0
        e = np.maximum(e, dd.astype(np.float32)); e = np.maximum(e, np.roll(dd, -1, ax).astype(np.float32))
    e[0] = e[-1] = 0; e[:, 0] = e[:, -1] = 0
    n = P['nrm']; ng = np.zeros(cls.shape, np.float32)
    for c in range(3): ng += gradmag(blur(n[..., c], 0.7)) ** 2
    ng = np.sqrt(ng)
    ld = np.log(np.maximum(d, 1e-3)); dgm = gradmag(blur(ld, 0.6))
    return dict(sil=e, crease=np.clip(ng * 1.5, 0, 1), depth=np.clip(dgm * 40.0, 0, 1), ma=ma, sky=sky, dep=d)


def ink_lines(strength, width, softness, wobble_amp=0.0, seed=0, thresh=0.5, vary=0.0, vary_px=40.0, scale=1.0):
    """Turn an edge strength map into strokes of a given width (px): blur-and-threshold, so lines have rounded ends and a
    width that follows `strength` and a slow noise (`vary`): the pen presses harder in places. Returns coverage 0..1."""
    shape = strength.shape
    if wobble_amp > 0:
        dx = fbm(shape, 14 * scale, seed + 1, 3) * wobble_amp * scale; dy = fbm(shape, 14 * scale, seed + 2, 3) * wobble_amp * scale
        strength = warp(strength, dx, dy)
    s = blur(strength, max(0.4, width * 0.5 * scale))
    peak = s.max() + 1e-6
    t = thresh * (1.0 - vary * fbm(shape, vary_px * scale, seed + 3, 2) * 0.5)
    t = t * (0.2 + 0.8 * np.clip(blur(strength, 3.0 * scale) * 6, 0, 1) ** 0.0)
    return smoothstep(t * 0.0 + t * (1 - softness), t * (1 + softness) + 1e-4, s / (width * 0.5 * scale + 0.5) * 1.0)


def project_points(film, pts):
    """World points -> pixel coordinates (origin top-left, y down) in the delivery frame, via the overlay's camera maths."""
    W, H = film.O.W, film.O.H; out = []
    for p in pts:
        q = film.O.project(p) if hasattr(film.O, 'project') else None
        out.append(None if q is None else (W / 2 + q[0], H / 2 - q[1]))
    return out


def save_png(path, rgb):
    """Tiny PNG writer (8-bit) for the dev loop (no PIL needed)."""
    import struct, zlib
    a = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8); h, w, _ = a.shape
    raw = b''.join(b'\x00' + a[y].tobytes() for y in range(h))
    def ch(t, d): c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw, 6)) + ch(b'IEND', b''))


# ------------------------------------------------------------------------------------------------------------- more helpers
def group_blur(A, ma, sky, groups, sigma):
    """Colour smoothing that does not cross between groups of material classes (normalized convolution): flat washes that
    stop at the lines. groups: list of tuples of class names; pixels in no group (and the sky) go to the last blur."""
    out = np.zeros_like(A); done = np.zeros(ma.shape, bool)
    for g in groups:
        m = cls_mask(ma, *g) & ~sky
        if not m.any(): continue
        mf = m.astype(np.float32); den = blur(mf, sigma) + 1e-4
        num = blur(A * mf[..., None], sigma)
        out = np.where(m[..., None], num / den[..., None], out); done |= m
    rest = ~done
    if rest.any():
        mf = rest.astype(np.float32); den = blur(mf, sigma) + 1e-4; num = blur(A * mf[..., None], sigma)
        out = np.where(rest[..., None], num / den[..., None], out)
    return out


def hatch(u, per_unit, width_px, min_px=3.0, max_px=60.0, soft=0.9):
    """Antialiased parallel lines of the scalar field u (world coordinate along a direction, from the Position pass):
    one line every 1/per_unit units of u, width_px pixels wide on screen. Lines fade out where they would be closer than
    min_px pixels (far away) so distant hatching never turns into noise. Returns coverage 0..1."""
    v = u * per_unit
    gy, gx = grad(blur(v, 0.8)); pxv = np.sqrt(gx * gx + gy * gy) + 1e-6          # screen pixels per... (v units per pixel)
    spacing_px = 1.0 / pxv                                                       # pixels between two lines
    ph = v - np.floor(v); d = np.abs(ph - 0.5)                                    # 0 at the line centre... (0.5 = on a line)
    dist_px = (0.5 - d) / pxv                                                     # pixel distance from the line centre
    cov = np.clip((width_px * 0.5 - dist_px) / soft + 0.5, 0, 1)
    fade = smoothstep(min_px * 0.8, min_px * 1.6, spacing_px) * (1 - smoothstep(max_px * 0.8, max_px * 1.4, spacing_px))
    return (cov * fade).astype(np.float32)


def paper(shape, base, seed=3, scale=1.0, fibre=0.035, mottle=0.04, grain=0.02):
    """A sheet of paper: base colour (3,), fibres (anisotropic noise), slow mottling and fine grain. Returns (H,W,3)."""
    n = fibre * (0.6 * noise(shape, 1.1 * scale, seed + 1, aniso=(0.5, 3.0)) + 0.6 * noise(shape, 1.1 * scale, seed + 2, aniso=(3.0, 0.5)))
    m = mottle * fbm(shape, 90 * scale, seed + 3, 4) + grain * noise(shape, 0.7 * scale, seed + 4)
    t = 1.0 + n + m
    return np.clip(np.asarray(base, np.float32)[None, None, :] * t[..., None], 0, 1)


def vignette(shape, strength=0.18, power=2.4):
    H, W = shape; y, x = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 1.41
    return 1.0 - strength * np.clip(r, 0, 1) ** power


def recolor_overlay(film, paper_rgb, ink_rgb, font=None):
    """Re-colour the overlay (labels, title, counters) so it belongs to the look: light things become paper_rgb, dark ink_rgb.
    Colours in sRGB 0..1. font: path to a ttf for the text objects (optional). Words stay what the script says."""
    import bpy
    for e in getattr(getattr(film, 'O', None), 'items', []):
        if getattr(e, 'em', None) is None: continue
        c = e.em.inputs['Color'].default_value; l = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        tgt = paper_rgb if l > 0.35 else ink_rgb
        e.em.inputs['Color'].default_value = (*[float(v) for v in srgb_to_lin(np.array(tgt))], 1.0)
        e.em.inputs['Strength'].default_value = 1.0
        if font and e.ob.type == 'FONT': e.ob.data.font = bpy.data.fonts.load(font)


STRATA_TIME = [(0.26, 0.17, 0.10), (0.90, 0.74, 0.46), (0.78, 0.44, 0.28), (0.56, 0.36, 0.22), (0.62, 0.58, 0.54), (0.84, 0.60, 0.28), (0.88, 0.84, 0.74), (0.24, 0.25, 0.30)]


def strata_labels(alb, palette=None, sigma=3.0, vote=5.0):
    """Which soil layer each pixel of a cut face belongs to (index into the strata palette): nearest colour of the smoothed
    albedo, then a majority vote (the one-hot maps are blurred by `vote` px) so thin slivers of a blend colour vanish.
    Deterministic, so a layer keeps its pattern in every frame."""
    pal = np.asarray(palette if palette is not None else STRATA_TIME, np.float32)
    A = lin_to_srgb(blur(alb, sigma))
    d = ((A[..., None, :] - pal[None, None, :, :]) ** 2).sum(-1)
    first = np.argmin(d, -1)
    votes = np.stack([blur((first == k).astype(np.float32), vote) for k in range(len(pal))], -1)
    return np.argmax(votes, -1).astype(np.int16)


def strata_palette(film):
    """The strata colours (sRGB) of the first built set, top-down; None if not found."""
    try:
        st = next(iter(film.built.values())); return [tuple(l[2]) for l in st['L'].strata] or None
    except Exception:
        return None


def label_edges(lab, valid):
    """1 where the layer label changes between neighbours (inside `valid`)."""
    e = np.zeros(lab.shape, bool)
    for ax in (0, 1):
        e |= lab != np.roll(lab, 1, ax)
    return (e & valid).astype(np.float32)


def tone_hatch(u, per_unit, D, thresh=0.1, cover=0.8, min_px=3.0, hair=0.38, soft=0.8):
    """Engraver's lines: parallel lines of the field u (one per 1/per_unit), each as wide as the tone D (0..1) asks: a
    hairline for a light tone, nearly solid for a dark one. Lines vanish where D < thresh and where they would be closer than
    min_px pixels. The width follows D smoothly along the line (the lines swell and thin, as burin lines do)."""
    v = u * per_unit
    gy, gx = grad(blur(v, 0.8)); pxv = np.sqrt(gx * gx + gy * gy) + 1e-6
    ph = v - np.floor(v); dist_v = np.minimum(ph, 1 - ph)                           # distance to the nearest line, in line spacings
    spacing_px = 1.0 / pxv
    half_px = np.maximum(D * cover * 0.5 * spacing_px, hair) * (D > thresh)
    cov = np.clip((half_px - dist_v * spacing_px) / soft + 0.5, 0, 1)
    fade = smoothstep(min_px * 0.8, min_px * 1.6, spacing_px)
    return (cov * fade).astype(np.float32)
