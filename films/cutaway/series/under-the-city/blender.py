"""Under the City (Cutaway showcase series #2). 20 s, 16:9, 24 fps. Infrastructure, trades, how a city works.

A dusk street of row houses sits on a block cut out of the city. The camera sinks down the cut face through the layers
a city stands on: utility pipes and cables, a brick sewer with a rat, a metro train rushing past in its tunnel, old brick
foundations, a Roman floor, and dinosaur bones at the very bottom. Then the whole block, top to bottom, at nightfall.

Shots (SHOTS timeline; frame = t * 24):
  1 street   0.0-4.5 s   high three-quarter, slow push down: dusk, lamps come on, a bus, a car, steam from the manhole
  2 descent  4.5-15.5 s  crane down the -Y cut face: pipes, sewer and rat, metro pass, bricks, Roman floor, the T. rex
  3 city    15.5-20.0 s  wide low three-quarter, slow pull back and rise: the whole column at once, a second train, last window
Kit: films/styles/cutaway/cutaway.py and cinematic/extras.py (imported, never edited). Everything here is procedural.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
for p in (os.path.join(ROOT, 'films', 'styles', 'cutaway'), os.path.join(ROOT, 'films', 'styles', 'cutaway', 'cinematic'), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import cutaway as cw  # noqa: E402
import extras as ex  # noqa: E402

G = cw.G
srgb = cw.srgb

SHOTS = [{'name': 'street', 'dur': 4.5}, {'name': 'descent', 'dur': 11.0}, {'name': 'city', 'dur': 4.5}]
DURATION = 20.0
FRAMES = {'street': 40, 'pipes': 150, 'sewer': 200, 'metro': 252, 'roman': 320, 'dino': 368, 'city': 440}   # check stills
SETTINGS = {'samples': 20, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Medium High Contrast',
            'exposure': 0.25, 'max_bounces': 4, 'volume_bounces': 0, 'clamp_indirect': 4.0, 'adaptive_min_samples': 8, 'denoising_prefilter': 'FAST'}

SX, SY, DEPTH = 4.6, 1.5, 2.6
FY = -SY / 2                     # the cut face the camera sinks down (-Y)
LIM = SX / 2 - 0.02              # vehicles fade out past the block's ends
SUN_AZ, SUN_EL = 112.0, 4.0
# time runs down: street, utility fill, clay (sewer), grey till (metro), rubble (old brick), Roman loam, fossil limestone, bedrock
STRATA = [('asphalt', 0.05, (0.13, 0.13, 0.14), 0.5), ('base', 0.07, (0.50, 0.48, 0.45), 0.9), ('fill', 0.40, (0.66, 0.54, 0.38), 0.15),
          ('clay', 0.34, (0.60, 0.40, 0.27), 0.04), ('till', 0.50, (0.47, 0.46, 0.44), 0.35), ('rubble', 0.22, (0.50, 0.37, 0.29), 0.55),
          ('roman', 0.22, (0.62, 0.44, 0.27), 0.18), ('limestone', 0.65, (0.86, 0.82, 0.72), 0.05), ('bedrock', 1.0, (0.24, 0.25, 0.30), 0.35)]
SEWER = (-0.70, 0.11)            # centre z, radius (half tunnel cut lengthwise by the face)
METRO = (-1.11, 0.20)
MANHOLE_U = 0.95


# =============================================================================================== small helpers
def mono(ts, vs, t):
    """Monotone cubic through (ts, vs), flat at both ends (eased start and stop, no overshoot)."""
    ts = np.asarray(ts, float); vs = np.asarray(vs, float)
    if t <= ts[0]: return float(vs[0])
    if t >= ts[-1]: return float(vs[-1])
    d = np.diff(vs) / np.diff(ts); m = np.zeros(len(ts))
    for k in range(1, len(ts) - 1):
        m[k] = 2 * d[k - 1] * d[k] / (d[k - 1] + d[k]) if d[k - 1] * d[k] > 0 else 0.0
    k = int(np.searchsorted(ts, t) - 1); h = ts[k + 1] - ts[k]; s = (t - ts[k]) / h
    return float((2 * s ** 3 - 3 * s ** 2 + 1) * vs[k] + (s ** 3 - 2 * s ** 2 + s) * h * m[k] + (-2 * s ** 3 + 3 * s ** 2) * vs[k + 1] + (s ** 3 - s ** 2) * h * m[k + 1])

def smooth(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)

def box(x0, y0, z0, x1, y1, z1): return cw._box(x0, y0, z0, x1, y1, z1)

def cyl_y(c, r, y0, y1, seg=24):
    """Cylinder along +Y (into the block) from y0 to y1, centred at c=(x, z), both ends capped."""
    V = []; F = []
    for y in (y0, y1):
        for j in range(seg): a = 2 * math.pi * j / seg; V.append((c[0] + r * math.cos(a), y, c[1] + r * math.sin(a)))
    for j in range(seg): j2 = (j + 1) % seg; F.append((j, j2, seg + j2, seg + j))
    F.append(tuple(range(seg))[::-1]); F.append(tuple(range(seg, 2 * seg)))
    return V, F

def hide_from_light(ob):
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)

def mat_masked(kit, name, color, rough=0.45, metallic=0.0, emission=None, strength=0.0, lim=LIM, coat=0.0):
    """Principled that turns transparent past |x| > lim (vehicles drive in and out of the cut ends cleanly)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb(color), 'Roughness': rough, 'Metallic': metallic})
    if coat: g.put(p, 'Coat Weight', coat)
    if emission is not None: g.put(p, 'Emission Color', srgb(emission)); g.put(p, 'Emission Strength', strength)
    geo = g.node('ShaderNodeNewGeometry'); x = g.sep(geo.outputs['Position'])[0]
    out = g.math('GREATER_THAN', g.math('ABSOLUTE', x), lim)
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader'); g.link(out, mx.inputs[0]); g.link(p, mx.inputs[1]); g.link(tr, mx.inputs[2])
    cw._finish(g, mx)
    return m

def mat_add(kit, name, color, strength, fade='x', lim=LIM, noise=0.0, drift=(0.0, 0.0)):
    """Additive glow card (transparent + emission): light cones, streaks, steam, haze. Gradient along Generated `fade`."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); gx, gy, gz = g.sep(tc.outputs['Generated'])
    a = {'x': gx, 'y': gy, 'z': gz, '1-z': g.math('SUBTRACT', 1.0, gz), 'mid': g.math('SUBTRACT', 1.0, g.math('ABSOLUTE', g.math('MULTIPLY', g.math('SUBTRACT', gz, 0.5), 2.0)))}[fade]
    a = g.math('POWER', a, 1.5)
    if noise:
        tv = ex.time_value(kit, g)
        q = g.vmath('ADD', tc.outputs['Object'], g.comb(g.math('MULTIPLY', tv, -drift[0]), 0.0, g.math('MULTIPLY', tv, -drift[1])))
        n = g.noise(q, noise, 3.0, 0.6, '4D', g.math('MULTIPLY', tv, 0.15))
        a = g.math('MULTIPLY', a, g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.35), 2.2, clamp=True))
    geo = g.node('ShaderNodeNewGeometry'); x = g.sep(geo.outputs['Position'])[0]
    a = g.math('MULTIPLY', a, g.math('LESS_THAN', g.math('ABSOLUTE', x), lim))
    gain = g.value(1.0, name + '_gain')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color)}); g.put(e, 'Strength', g.math('MULTIPLY', g.math('MULTIPLY', a, strength), gain))
    tr = g.node('ShaderNodeBsdfTransparent'); ad = g.node('ShaderNodeAddShader'); g.link(tr, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    return m, gain

def mat_glow_anim(kit, name, color, strength):
    """Emission whose strength is a Value node (switching lamps and windows)."""
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit); v = g.value(0.0, name + '_on')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb(color)}); g.put(e, 'Strength', g.math('MULTIPLY', v, strength)); cw._finish(g, e)
    return m, v

def mat_brick(kit, name, c1=(0.56, 0.26, 0.16), c2=(0.44, 0.20, 0.13), mortar=(0.30, 0.26, 0.22), scale=26.0, axes='xz'):
    key = ('utc', name)
    if key in kit.mats: return kit.mats[key]
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); px, py, pz = g.sep(tc.outputs['Object'])
    vec = g.comb(px, g.math('ADD', pz, py), 0.0) if axes == 'xz' else g.comb(g.math('ADD', px, py), pz, 0.0)
    br = g.node('ShaderNodeTexBrick', ins={'Vector': vec, 'Color1': srgb(c1), 'Color2': srgb(c2), 'Mortar': srgb(mortar), 'Scale': scale,
                                           'Mortar Size': 0.018, 'Mortar Smooth': 0.2, 'Bias': 0.0, 'Brick Width': 0.5, 'Row Height': 0.25})
    n = g.noise(tc.outputs['Object'], 60.0, 3.0)
    col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.35), br.outputs['Color'], srgb((0.10, 0.07, 0.05)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.85})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.5, 'Height': g.math('SUBTRACT', 1.0, br.outputs['Fac']), 'Distance': 0.002}); g.put(p, 'Normal', b)
    cw._finish(g, p); kit.mats[key] = m; return m


# =============================================================================================== the street (top)
def mat_road(kit):
    """Asphalt with a damp dusk sheen, a dashed centre line, kerb-side gutters."""
    m = cw._new_mat(kit.bpy, 'utc_road'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); px, py, pz = g.sep(tc.outputs['Object'])
    n = g.noise(tc.outputs['Object'], 140.0, 4.0); n2 = g.noise(tc.outputs['Object'], 3.0, 3.0)
    col = g.mix(n.outputs['Fac'], srgb((0.07, 0.07, 0.075)), srgb((0.15, 0.15, 0.16)))
    dash = g.math('MULTIPLY', g.math('LESS_THAN', g.math('ABSOLUTE', g.math('ADD', py, 0.19)), 0.007), g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', px, 2.4)), 0.5))
    col = g.mix(dash, col, srgb((0.86, 0.74, 0.40)))
    wet = g.math('MULTIPLY', g.math('SUBTRACT', n2.outputs['Fac'], 0.42), 4.0, clamp=True)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col}); g.put(p, 'Roughness', g.mix(wet, 0.55, 0.16, dtype='FLOAT'))
    b = g.node('ShaderNodeBump', ins={'Strength': 0.25, 'Height': n.outputs['Fac'], 'Distance': 0.002}); g.put(p, 'Normal', b)
    cw._finish(g, p); return m

def build_street(kit, land, rng):
    bpy = kit.bpy; out = {}
    land.objects['top'].data.materials[0] = mat_road(kit)
    walk = cw.mat_simple(kit, 'utc_walk', (0.50, 0.48, 0.45), 0.8, noise_amt=0.12, bump=0.15)
    kerb = cw.mat_simple(kit, 'utc_kerb', (0.62, 0.60, 0.57), 0.7)
    A = cw._Acc()
    A.add(*box(-SX / 2, FY - 0.0004, -0.01, SX / 2, -0.50, 0.016), 0)                 # front sidewalk (its section shows on the cut face)
    A.add(*box(-SX / 2, -0.505, -0.01, SX / 2, -0.49, 0.018), 1)                        # kerb
    A.add(*box(-SX / 2, 0.11, -0.01, SX / 2, 0.40, 0.016), 0)                           # back sidewalk
    A.add(*box(-SX / 2, 0.10, -0.01, SX / 2, 0.115, 0.018), 1)
    for x in np.arange(-SX / 2 + 0.3, SX / 2, 0.3):                                     # slab joints
        A.add(*box(x - 0.0015, FY + 0.01, 0.016, x + 0.0015, -0.51, 0.0165), 1)
    out['walks'] = A.build(bpy, 'utc_walks', [walk, kerb], False, kit.coll)
    # manhole cover, cut in half by the face (its shaft runs down to the sewer)
    th = np.linspace(0, math.pi, 17); V = [(MANHOLE_U + 0.055 * math.cos(a), FY + 0.055 * math.sin(a), 0.0172) for a in th] + [(MANHOLE_U, FY, 0.0172)]
    F = [(len(V) - 1, k, k + 1) for k in range(16)]
    cw.mk_mesh(bpy, 'utc_manhole', V, F, [cw.mat_simple(kit, 'utc_iron', (0.10, 0.10, 0.11), 0.4, metallic=0.6, bump=0.6)], None, False, kit.coll)
    out['houses'] = build_houses(kit, land, rng)
    out['lamps'] = build_lamps(kit, land)
    out['bus'] = build_vehicle(kit, 'bus'); out['car'] = build_vehicle(kit, 'car')
    out['steam'] = build_steam(kit)
    return out

def build_houses(kit, land, rng):
    """A terrace of row houses facing the street, two or three floors, lit and dark windows, stoops, cornices."""
    bpy = kit.bpy; walls = [(0.52, 0.22, 0.15), (0.80, 0.72, 0.58), (0.44, 0.48, 0.50), (0.62, 0.32, 0.20), (0.70, 0.62, 0.48), (0.38, 0.40, 0.34)]
    mats = [cw.mat_simple(kit, f'utc_facade{k}', c, 0.85, noise_amt=0.1) for k, c in enumerate(walls)]
    mats += [cw.mat_glow(kit, 'utc_win_lit', (1.0, 0.68, 0.34), 5.0), cw.mat_simple(kit, 'utc_win_dark', (0.05, 0.06, 0.08), 0.12),
             cw.mat_simple(kit, 'utc_trim', (0.86, 0.83, 0.76), 0.7), cw.mat_simple(kit, 'utc_roof', (0.17, 0.16, 0.17), 0.8), cw.mat_simple(kit, 'utc_door', (0.18, 0.10, 0.07), 0.6)]
    LIT, DARK, TRIM, ROOF, DOOR = 6, 7, 8, 9, 10
    switch = []; A = cw._Acc(); x = -SX / 2; k = 0; y0, y1 = 0.42, SY / 2
    while x < SX / 2 - 0.05:
        w = min(rng.choice([0.30, 0.34, 0.38]), SX / 2 - x); floors = int(rng.choice([2, 3, 3])); fh = 0.125; h = floors * fh + 0.03
        c = k % 6 if k % 6 != (k - 1) % 6 else (k + 1) % 6
        A.add(*box(x, y0, -0.01, x + w, y1, h), c)
        A.add(*box(x - 0.002, y0 - 0.008, h - 0.012, x + w + 0.002, y1, h + 0.01), TRIM)          # cornice
        A.add(*box(x + 0.01, y0 + 0.02, h + 0.01, x + w - 0.01, y1 - 0.05, h + 0.035), ROOF)        # roof parapet
        A.add(*box(x + w * 0.62, y0 + 0.06, h + 0.035, x + w * 0.72, y0 + 0.10, h + 0.09), c)        # chimney
        dx = x + 0.05; A.add(*box(dx, y0 - 0.0015, 0.016, dx + 0.05, y0, 0.105), DOOR)              # door
        A.add(*box(dx - 0.008, y0 - 0.03, 0.0, dx + 0.058, y0, 0.026), TRIM)                          # stoop
        for f in range(floors):
            cols = [x + w * 0.62, x + w * 0.86] if f == 0 else [x + w * 0.25, x + w * 0.5, x + w * 0.75]
            if f == 0 and w < 0.33: cols = [x + w * 0.74]
            for cx in cols:
                z0 = f * fh + 0.045; z1 = z0 + 0.065; ww = 0.022
                A.add(*box(cx - ww - 0.004, y0 - 0.006, z0 - 0.008, cx + ww + 0.004, y0, z0 - 0.002), TRIM)  # sill
                lit = rng.uniform() < 0.55
                if not lit and len(switch) < 3 and f > 0 and rng.uniform() < 0.5 and abs(cx) < 1.6:
                    switch.append((cx, z0, z1, ww)); continue
                A.add([(cx - ww, y0 - 0.0012, z0), (cx + ww, y0 - 0.0012, z0), (cx + ww, y0 - 0.0012, z1), (cx - ww, y0 - 0.0012, z1)], [(0, 1, 2, 3)], LIT if lit else DARK)
        x += w; k += 1
    ob = A.build(bpy, 'utc_houses', mats, False, kit.coll)
    # windows that switch on (two during the opening, the last one at the very end)
    sw = []
    for i, (cx, z0, z1, ww) in enumerate(switch):
        m, v = mat_glow_anim(kit, f'utc_win_sw{i}', (1.0, 0.70, 0.36), 5.0)
        cw.mk_mesh(bpy, f'utc_win_sw{i}', [(cx - ww, y0 - 0.0013, z0), (cx + ww, y0 - 0.0013, z0), (cx + ww, y0 - 0.0013, z1), (cx - ww, y0 - 0.0013, z1)], [(0, 1, 2, 3)], [m], None, False, kit.coll)
        sw.append(v)
    for i, xx in enumerate((-1.3, 0.1, 1.45)):           # warm spill from the windows onto the back sidewalk
        ld = bpy.data.lights.new(f'utc_house_glow{i}', 'POINT'); ld.energy = 0.6; ld.color = (1.0, 0.66, 0.36); ld.shadow_soft_size = 0.05
        lo = bpy.data.objects.new(ld.name, ld); kit.coll.objects.link(lo); lo.location = (xx, 0.30, 0.16)
    return {'ob': ob, 'switch': sw}

def build_lamps(kit, land):
    """Street lamps on the front sidewalk that flicker on at dusk; each throws a faint cone of light (camera-only card)."""
    bpy = kit.bpy; iron = cw.mat_simple(kit, 'utc_lampiron', (0.06, 0.06, 0.07), 0.45, metallic=0.5)
    head, on = mat_glow_anim(kit, 'utc_lamphead', (1.0, 0.76, 0.46), 30.0)
    cone_m, cone_gain = mat_add(kit, 'utc_lampcone', (1.0, 0.72, 0.42), 0.55, fade='z')
    lamps = []
    for k, x in enumerate((-1.75, -0.6, 0.55, 1.7)):
        y = -0.53; h = 0.19; A = cw._Acc()
        v, f = cw._tube([(x, y, 0.016), (x, y, h), (x, y - 0.0, h + 0.012), (x, y + 0.05, h + 0.016)], [0.0035, 0.003, 0.0028, 0.0025], 8); A.add(v, f, 0)
        V0, F0 = cw._icosphere(1); A.add(V0 * np.array([0.012, 0.012, 0.007]) + np.array([x, y + 0.055, h + 0.008]), F0, 1)
        A.build(bpy, f'utc_lamp{k}', [iron, head], True, kit.coll)
        ld = bpy.data.lights.new(f'utc_lamp{k}_l', 'SPOT'); ld.energy = 0.0; ld.color = (1.0, 0.70, 0.40); ld.spot_size = math.radians(110); ld.spot_blend = 0.6; ld.shadow_soft_size = 0.01
        lo = bpy.data.objects.new(ld.name, ld); kit.coll.objects.link(lo); lo.location = (x, y + 0.055, h - 0.002); lo.rotation_euler = (0, 0, 0)
        # cone card (a truncated cone, open), additive, seen by the camera only
        seg = 20; r0, r1, z0, z1 = 0.008, 0.11, h, 0.018; V = []; F = []
        for zz, rr in ((z1, r1), (z0, r0)):
            for j in range(seg): a = 2 * math.pi * j / seg; V.append((x + rr * math.cos(a), y + 0.055 + rr * math.sin(a), zz))
        F = [(j, (j + 1) % seg, seg + (j + 1) % seg, seg + j) for j in range(seg)]
        co = cw.mk_mesh(bpy, f'utc_lampcone{k}', V, F, [cone_m], None, False, kit.coll); hide_from_light(co)
        lamps.append(lo)
    return {'lights': lamps, 'on': on, 'cone': cone_gain}

def build_vehicle(kit, kind):
    """A bus (red and cream, lit windows) or a small car, with turning wheels, headlights (a real spot) and tail lights."""
    bpy = kit.bpy
    if kind == 'bus': L, W, H, r, body, z0 = 0.42, 0.095, 0.115, 0.019, (0.66, 0.07, 0.05), 0.012
    else: L, W, H, r, body, z0 = 0.18, 0.075, 0.05, 0.014, (0.20, 0.32, 0.44), 0.008
    mb = mat_masked(kit, f'utc_{kind}_body', body, 0.35, coat=0.6); mw = mat_masked(kit, f'utc_{kind}_win', (0.1, 0.1, 0.1), 0.2, emission=(1.0, 0.82, 0.55), strength=3.0 if kind == 'bus' else 0.3)
    mh = mat_masked(kit, f'utc_{kind}_head', (1, 1, 1), 0.2, emission=(1.0, 0.92, 0.78), strength=25.0); mt = mat_masked(kit, f'utc_{kind}_tail', (0.4, 0, 0), 0.3, emission=(1.0, 0.08, 0.04), strength=12.0)
    mr = mat_masked(kit, f'utc_{kind}_roof', (0.86, 0.82, 0.72) if kind == 'bus' else body, 0.5); mk = mat_masked(kit, f'utc_{kind}_tyre', (0.03, 0.03, 0.03), 0.8)
    root = ex.empty(kit, f'utc_{kind}'); A = cw._Acc()
    if kind == 'bus':
        A.add(*box(-L / 2, -W / 2, z0, L / 2, W / 2, H), 0)
        A.add(*box(-L / 2 + 0.01, -W / 2 + 0.004, H, L / 2 - 0.01, W / 2 - 0.004, H + 0.008), 4)
        for s in (-1, 1):
            yy = s * (W / 2 + 0.0008)
            A.add([(-L / 2 + 0.03, yy, 0.058), (L / 2 - 0.05, yy, 0.058), (L / 2 - 0.05, yy, 0.098), (-L / 2 + 0.03, yy, 0.098)], [(0, 1, 2, 3) if s < 0 else (3, 2, 1, 0)], 1)
        A.add([(L / 2 + 0.0008, -W / 2 + 0.008, 0.055), (L / 2 + 0.0008, W / 2 - 0.008, 0.055), (L / 2 + 0.0008, W / 2 - 0.008, 0.102), (L / 2 + 0.0008, -W / 2 + 0.008, 0.102)], [(0, 1, 2, 3)], 1)
    else:
        A.add(*box(-L / 2, -W / 2, z0, L / 2, W / 2, H * 0.62), 0)
        A.add([(-L * 0.30, -W / 2 + 0.004, H * 0.62), (L * 0.18, -W / 2 + 0.004, H * 0.62), (L * 0.08, -W / 2 + 0.008, H), (-L * 0.24, -W / 2 + 0.008, H),
               (-L * 0.30, W / 2 - 0.004, H * 0.62), (L * 0.18, W / 2 - 0.004, H * 0.62), (L * 0.08, W / 2 - 0.008, H), (-L * 0.24, W / 2 - 0.008, H)],
              [(0, 1, 2, 3), (7, 6, 5, 4), (3, 2, 6, 7), (1, 5, 6, 2), (0, 3, 7, 4)], 1)
    for s in (-1, 1):
        V0, F0 = cw._icosphere(1)
        A.add(V0 * np.array([0.002, 0.008, 0.006]) + np.array([L / 2, s * (W / 2 - 0.014), z0 + 0.016]), F0, 2)
        A.add(V0 * np.array([0.002, 0.006, 0.006]) + np.array([-L / 2, s * (W / 2 - 0.012), z0 + 0.02]), F0, 3)
    A.build(bpy, f'utc_{kind}_shell', [mb, mw, mh, mt, mr], False, kit.coll).parent = root
    wheels = []
    for wx in ((-L * 0.32, L * 0.30) if kind == 'bus' else (-L * 0.30, L * 0.30)):
        for s in (-1, 1):
            V, F = cyl_y((0, 0), r, -0.006, 0.006, 14); V = np.array(V)
            w = cw.mk_mesh(bpy, f'utc_{kind}_wheel', V, F, [mk], None, True, kit.coll); w.parent = root; w.location = (wx, s * (W / 2 - 0.004), r); wheels.append(w)
    ld = bpy.data.lights.new(f'utc_{kind}_beam', 'SPOT'); ld.energy = 1.4 if kind == 'bus' else 0.9; ld.color = (1.0, 0.90, 0.74); ld.spot_size = math.radians(55); ld.spot_blend = 0.5; ld.shadow_soft_size = 0.005
    lo = bpy.data.objects.new(ld.name, ld); kit.coll.objects.link(lo); lo.parent = root; lo.location = (L / 2 + 0.01, 0, z0 + 0.02); lo.rotation_euler = (0, math.radians(76), 0)
    return {'root': root, 'wheels': wheels, 'r': r, 'beam': lo}

def build_steam(kit):
    """Three soft steam wisps rising from the manhole (additive noise cards, drifting up)."""
    bpy = kit.bpy; m, gain = mat_add(kit, 'utc_steam', (0.80, 0.78, 0.76), 0.32, fade='mid', noise=9.0, drift=(0.02, 0.06)); cards = []
    for k in range(3):
        w, h = 0.10, 0.30; V = [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)]
        ob = cw.mk_mesh(bpy, f'utc_steam{k}', V, [(0, 1, 2, 3)], [m], None, False, kit.coll); hide_from_light(ob); cards.append(ob)
    return {'cards': cards, 'gain': gain}


# =============================================================================================== under the street (the face)
def pipe_section(kit, eggs, face, u, z, r, wall, inside, name, length=0.35, ring=0.22, glow=None):
    """A pipe cut across by the face: its wall ring and what it carries (water, gas, sewage, light)."""
    pieces = [(*cyl_y((0, 0), r, -0.004, length, 28), 0), (*cyl_y((0, 0), r * (1 - ring), -0.0055, -0.003, 28), 1)]
    mw = ex.mat_pbr(kit, name + '_wall', wall, 0.35, coat=0.5)
    mi = ex.mat_pbr(kit, name + '_in', inside, 0.12, emission=glow, strength=6.0 if glow else 0.0)
    return eggs.obj(name, pieces, [mw, mi], face, u, z)

def build_utilities(kit, land, eggs):
    out = {}; F = eggs.faces['-Y']
    pipe_section(kit, eggs, '-Y', -0.42, -0.31, 0.068, (0.10, 0.28, 0.66), (0.05, 0.16, 0.24), 'utc_watermain', ring=0.16)
    pipe_section(kit, eggs, '-Y', 0.12, -0.22, 0.036, (0.95, 0.72, 0.08), (0.10, 0.09, 0.08), 'utc_gas')
    pipe_section(kit, eggs, '-Y', 0.36, -0.42, 0.02, (0.95, 0.42, 0.06), (0.10, 0.12, 0.14), 'utc_fibre', glow=(0.55, 0.95, 1.0), ring=0.5)
    pipe_section(kit, eggs, '-Y', 1.30, -0.40, 0.052, (0.66, 0.34, 0.20), (0.24, 0.17, 0.10), 'utc_drain')
    pipe_section(kit, eggs, '-Y', -1.12, -0.26, 0.042, (0.86, 0.86, 0.84), (0.75, 0.30, 0.10), 'utc_heat_a', ring=0.35)
    pipe_section(kit, eggs, '-Y', -1.00, -0.26, 0.042, (0.86, 0.86, 0.84), (0.20, 0.30, 0.50), 'utc_heat_b', ring=0.35)
    pipe_section(kit, eggs, '-Y', -1.85, -0.36, 0.045, (0.10, 0.28, 0.66), (0.05, 0.16, 0.24), 'utc_water2', ring=0.16)
    pipe_section(kit, eggs, '-Y', 1.85, -0.25, 0.03, (0.95, 0.72, 0.08), (0.10, 0.09, 0.08), 'utc_gas2')
    # electrical duct bank: a concrete block with six conduits
    conc = cw.mat_simple(kit, 'utc_concrete', (0.62, 0.61, 0.58), 0.85, noise_amt=0.15, bump=0.3)
    P = [(*box(-0.13, -0.005, -0.075, 0.13, 0.30, 0.075), 0)]; cols = [(0.06, 0.06, 0.06), (0.85, 0.40, 0.06), (0.70, 0.10, 0.08)]
    for i, cu in enumerate((-0.075, 0.0, 0.075)):
        for j, cz in enumerate((-0.035, 0.035)):
            P.append((*cyl_y((cu, cz), 0.024, -0.0065, 0.0, 20), 1 + (i + j) % 3)); P.append((*cyl_y((cu, cz), 0.012, -0.0075, 0.0, 16), 4))
    eggs.obj('utc_ductbank', P, [conc] + [ex.mat_pbr(kit, f'utc_conduit{c}', col, 0.4) for c, col in enumerate(cols)] + [ex.mat_pbr(kit, 'utc_copper', (0.85, 0.45, 0.22), 0.3, metallic=1.0)],
             '-Y', 0.66, -0.34)
    # a telecom cable along the face just under the road base, with pulses of light travelling along it (data)
    cab = cw.mk_mesh(kit.bpy, 'utc_cable', *cw._tube([(-SX / 2, FY + 0.004, -0.150), (SX / 2, FY + 0.004, -0.150)], [0.0075, 0.0075], 10), [ex.mat_pbr(kit, 'utc_cablejacket', (0.05, 0.05, 0.06), 0.4)], None, True, kit.coll)
    pm = cw.mat_glow(kit, 'utc_pulse', (0.55, 0.95, 1.0), 14.0); pulses = []
    for k in range(7):
        V, Fc = cw._tube([(-0.02, 0, 0), (0.02, 0, 0)], [0.0045, 0.0045], 8)
        pulses.append(cw.mk_mesh(kit.bpy, f'utc_pulse{k}', V, Fc, [pm], None, True, kit.coll))
    out['pulses'] = pulses
    # the manhole shaft, cut in half, from the street down to the sewer, with its ladder
    shaft = eggs.hole_tunnel('-Y', [(MANHOLE_U, -0.012), (MANHOLE_U, SEWER[0] + SEWER[1] * 0.6)], 0.05, 'utc_shaft', material=mat_brick(kit, 'utc_brick_shaft', axes='yz', scale=30.0))
    rust = ex.mat_pbr(kit, 'utc_rung', (0.30, 0.16, 0.08), 0.6, metallic=0.6); A = []
    for zz in np.arange(-0.06, SEWER[0] + 0.02, -0.055):
        A.append((*cw._tube([(-0.03, 0.035, zz), (0.03, 0.035, zz)], [0.003, 0.003], 6), 0))
    eggs.obj('utc_ladder', A, [rust], '-Y', MANHOLE_U, 0.0)
    eggs.spot('-Y', 0.1, -0.30, power=5.0, out=0.6, up=0.25, size=60, name='utc_spot_pipes')
    # small finds in the fill: a lost green bottle, and an earthworm
    prof = [(0.0, 0.0), (0.018, 0.0), (0.02, 0.01), (0.02, 0.05), (0.012, 0.065), (0.007, 0.08), (0.007, 0.092), (0.0085, 0.095), (0.0, 0.095)]
    V = []; Fb = []; seg = 18
    for k, (rr, hh) in enumerate(prof):
        for j in range(seg): a = 2 * math.pi * j / seg; V.append((hh - 0.047, rr * math.cos(a), rr * math.sin(a)))
    for k in range(len(prof) - 1):
        for j in range(seg): a0 = k * seg + j; b0 = k * seg + (j + 1) % seg; Fb.append((a0, b0, b0 + seg, a0 + seg))
    eggs.obj('utc_bottle', [(V, Fb, 0)], [ex.mat_pbr(kit, 'utc_glass', (0.16, 0.42, 0.20), 0.08, transmission=0.6, coat=0.3)], '-Y', -1.55, -0.33, 0.004, 0.5)
    worm = cw.mk_mesh(kit.bpy, 'utc_worm', *cw._tube([(0, 0, 0), (0.01, 0, 0), (0.02, 0, 0), (0.03, 0, 0)], [0.004] * 4, 6), [ex.mat_pbr(kit, 'utc_wormskin', (0.72, 0.40, 0.38), 0.4, coat=0.6)], None, True, kit.coll)
    out['worm'] = worm
    return out

def build_sewer(kit, land, eggs, rng):
    """A brick sewer cut lengthwise: dark flowing water, a walkway, a caged lamp, a drip, a rat."""
    bpy = kit.bpy; zc, r = SEWER; out = {}
    eggs.hole_tunnel('-Y', [(-2.18, zc), (2.18, zc)], r, 'utc_sewer', material=mat_brick(kit, 'utc_brick_sewer', (0.50, 0.26, 0.16), (0.40, 0.21, 0.13), (0.22, 0.20, 0.17), 30.0))
    wl = zc - r + 0.035
    # water: glossy, flowing (bump noise moving along +x)
    m = cw._new_mat(bpy, 'utc_sewage'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); tv = ex.time_value(kit, g)
    q = g.vmath('ADD', tc.outputs['Object'], g.comb(g.math('MULTIPLY', tv, -0.12), 0.0, 0.0))
    n = g.noise(g.vmath('MULTIPLY', q, (1.0, 3.0, 1.0)), 40.0, 3.0, 0.6, '4D', g.math('MULTIPLY', tv, 0.4))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.05, 0.07, 0.05)), 'Roughness': 0.06})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.35, 'Height': n.outputs['Fac'], 'Distance': 0.003}); g.put(p, 'Normal', b); cw._finish(g, p)
    d_at = lambda z: math.sqrt(max(0.0, r * r - (z - zc) ** 2))
    cw.mk_mesh(bpy, 'utc_sewage', [(-2.18, FY + 0.03, wl), (2.18, FY + 0.03, wl), (2.18, FY + d_at(wl) + 0.01, wl), (-2.18, FY + d_at(wl) + 0.01, wl)], [(0, 1, 2, 3)], [m], None, False, kit.coll)
    stone = cw.mat_simple(kit, 'utc_ledge', (0.40, 0.36, 0.32), 0.8, noise_amt=0.2, bump=0.4)
    cw.mk_mesh(bpy, 'utc_ledge', *box(-2.18, FY - 0.0005, zc - r, 2.18, FY + 0.032, wl + 0.012), [stone], None, False, kit.coll)
    # caged lamp on the back wall
    lamp_on = mat_glow_anim(kit, 'utc_sewerbulb', (1.0, 0.62, 0.30), 40.0)
    A = cw._Acc(); V0, F0 = cw._icosphere(1); A.add(V0 * 0.008, F0, 0)
    for a in np.linspace(0, math.pi, 5): A.add(*cw._tube([(0.012 * math.cos(a), 0.012 * math.sin(a) - 0.004, -0.012), (0.012 * math.cos(a), 0.012 * math.sin(a) - 0.004, 0.012)], [0.0012, 0.0012], 4), 1)
    bulb = A.build(bpy, 'utc_sewerlamp', [lamp_on[0], cw.mat_simple(kit, 'utc_cage', (0.08, 0.08, 0.08), 0.5, metallic=0.6)], True, kit.coll)
    bulb.location = (0.15, FY + d_at(zc + 0.05) - 0.012, zc + 0.05)
    ld = bpy.data.lights.new('utc_sewer_l', 'POINT'); ld.energy = 0.5; ld.color = (1.0, 0.62, 0.32); ld.shadow_soft_size = 0.008
    lo = bpy.data.objects.new(ld.name, ld); kit.coll.objects.link(lo); lo.location = (0.15, FY + d_at(zc + 0.05) - 0.03, zc + 0.05)
    out['lamp'] = (lamp_on[1], ld)
    # mist on the water (additive card, drifting downstream)
    mm, _ = mat_add(kit, 'utc_sewermist', (0.85, 0.70, 0.52), 0.25, fade='1-z', noise=14.0, drift=(0.08, 0.0))
    mc = cw.mk_mesh(bpy, 'utc_sewermist', [(-2.18, FY + 0.05, wl), (2.18, FY + 0.05, wl), (2.18, FY + 0.05, wl + 0.06), (-2.18, FY + 0.05, wl + 0.06)], [(0, 1, 2, 3)], [mm], None, False, kit.coll); hide_from_light(mc)
    # a drip from the vault and its ring
    drop = cw.mk_mesh(bpy, 'utc_drop', cw._icosphere(1)[0] * np.array([0.0028, 0.0028, 0.0045]), cw._icosphere(1)[1], [ex.mat_pbr(kit, 'utc_dropmat', (0.6, 0.65, 0.6), 0.05, coat=1.0)], None, True, kit.coll)
    th = np.linspace(0, 2 * math.pi, 25)
    ringob = cw.mk_mesh(bpy, 'utc_dropring', *cw._tube([(math.cos(a), math.sin(a), 0) for a in th], np.full(25, 0.06), 5, False), [ex.mat_pbr(kit, 'utc_ringmat', (0.5, 0.5, 0.45), 0.05, coat=1.0)], None, True, kit.coll)
    out['drop'] = (drop, ringob, wl, d_at)
    eggs.spot('-Y', 0.2, zc, power=2.5, out=0.6, up=0.18, size=50, name='utc_spot_sewer', color=(1.0, 0.80, 0.6))
    out['rat'] = build_rat(kit, wl + 0.012)
    return out

def build_rat(kit, z):
    bpy = kit.bpy; fur = ex.mat_pbr(kit, 'utc_rat_fur', (0.30, 0.27, 0.24), 0.7, bump=0.25, bump_scale=300.0)
    pink = ex.mat(kit, 'utc_rat_pink', (0.78, 0.52, 0.50), 0.5); eye = ex.mat_pbr(kit, 'utc_rat_eye', (0.01, 0.01, 0.01), 0.05, coat=1.0)
    root = ex.empty(kit, 'utc_rat'); root.location = (0.0, FY + 0.018, z)
    body = ex.part(kit, 'utc_rat_body', [(*ex.ell((0, 0, 0.017), (0.032, 0.015, 0.014), 2, 0.05, 1), 0),
                                          (*ex.ell((-0.018, 0, 0.012), (0.018, 0.016, 0.013), 2, 0.0, 2), 0)], [fur], root)
    head = ex.part(kit, 'utc_rat_head', [(*ex.ell((0.016, 0, 0.0), (0.019, 0.0105, 0.0095), 2), 0), (*ex.cone((0.03, 0, -0.002), (0.042, 0, -0.004), 0.005, 0.0015, 8), 0),
                                         (*ex.ell((0.042, 0, -0.004), (0.0022, 0.0022, 0.0022), 1), 1),
                                         (*ex.ell((0.008, -0.009, 0.010), (0.006, 0.002, 0.0065), 1), 1), (*ex.ell((0.008, 0.009, 0.010), (0.006, 0.002, 0.0065), 1), 1),
                                         (*ex.ell((0.024, -0.0085, 0.004), (0.0022, 0.0018, 0.0022), 1), 2), (*ex.ell((0.024, 0.0085, 0.004), (0.0022, 0.0018, 0.0022), 1), 2)],
                   [fur, pink, eye], root, (0.028, 0, 0.022))
    P = np.array([(0, 0, 0), (-0.02, 0, 0.002), (-0.045, 0.004, 0.0), (-0.07, 0.0, -0.004)])
    tail = ex.part(kit, 'utc_rat_tail', [(*cw._tube(cw.catmull(P, 12), np.linspace(0.003, 0.0008, 12), 6), 0)], [pink], root, (-0.034, 0, 0.012))
    legs = []
    for lx, s in ((0.018, -1), (0.018, 1), (-0.02, -1), (-0.02, 1)):
        legs.append(ex.part(kit, 'utc_rat_leg', [(*ex.ell((0, 0, -0.004), (0.005, 0.003, 0.006), 1), 0)], [pink], root, (lx, s * 0.009, 0.006)))
    return {'root': root, 'body': body, 'head': head, 'tail': tail, 'legs': legs}

def build_metro(kit, land, eggs):
    """The metro tunnel cut lengthwise: segment rings, a track bed, warm wall lamps; the train (three cars, lit windows
    with passengers, headlights, light streaks) and its interior lights."""
    bpy = kit.bpy; zc, r = METRO; out = {}
    m = cw._new_mat(bpy, 'utc_segments'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); px, py, pz = g.sep(tc.outputs['Object'])
    groove = g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', px, 4.0)), 0.035)
    n = g.noise(tc.outputs['Object'], 25.0, 4.0)
    col = g.mix(n.outputs['Fac'], srgb((0.40, 0.40, 0.39)), srgb((0.58, 0.57, 0.55))); col = g.mix(g.math('MULTIPLY', groove, 0.8), col, srgb((0.10, 0.10, 0.10)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.8}); cw._finish(g, p)
    eggs.hole_tunnel('-Y', [(-2.2, zc), (2.2, zc)], r, 'utc_metro', material=m)
    d_at = lambda z: math.sqrt(max(0.0, r * r - (z - zc) ** 2))
    zf = zc - 0.13; conc = cw.mat_simple(kit, 'utc_trackbed', (0.36, 0.35, 0.34), 0.9, noise_amt=0.2, bump=0.4)
    cw.mk_mesh(bpy, 'utc_trackbed', *box(-2.2, FY - 0.0005, zc - r, 2.2, FY + d_at(zf) + 0.02, zf), [conc], None, False, kit.coll)
    steel = ex.mat_pbr(kit, 'utc_rail', (0.7, 0.7, 0.72), 0.25, metallic=1.0); A = []
    for dd in (0.03, 0.10):
        A.append((*box(-2.2, dd - 0.003, zf, 2.2, dd + 0.003, zf + 0.008), 0))
    for x in np.arange(-2.15, 2.2, 0.06): A.append((*box(x - 0.008, 0.012, zf - 0.0005, x + 0.008, 0.125, zf + 0.002), 1))
    ex.part(kit, 'utc_rails', A, [steel, ex.mat(kit, 'utc_sleeper', (0.20, 0.18, 0.16), 0.9)], None, (0, FY, 0))
    # warm wall lamps along the back of the tunnel
    lm = cw.mat_glow(kit, 'utc_tunnellamp', (1.0, 0.70, 0.40), 22.0); A = cw._Acc()
    for x in np.arange(-2.0, 2.05, 0.5): A.add(*box(x - 0.018, FY + d_at(zc + 0.12) - 0.012, zc + 0.115, x + 0.018, FY + d_at(zc + 0.12) + 0.01, zc + 0.127), 0)
    A.build(bpy, 'utc_tunnellamps', [lm], False, kit.coll)
    for i, x in enumerate((-1.0, 0.0, 1.0)):
        ld = bpy.data.lights.new(f'utc_tunnel_l{i}', 'POINT'); ld.energy = 0.55; ld.color = (1.0, 0.68, 0.38); ld.shadow_soft_size = 0.02
        lo = bpy.data.objects.new(ld.name, ld); kit.coll.objects.link(lo); lo.location = (x, FY + 0.12, zc + 0.10)
    out['train'] = build_train(kit, zf)
    return out

def build_train(kit, zf, rng=None):
    bpy = kit.bpy; rng = np.random.default_rng(12)
    body = mat_masked(kit, 'utc_train_body', (0.78, 0.78, 0.80), 0.3, metallic=0.3, coat=0.5); stripe = mat_masked(kit, 'utc_train_stripe', (0.80, 0.10, 0.08), 0.4)
    win = mat_masked(kit, 'utc_train_win', (0.1, 0.1, 0.1), 0.2, emission=(1.0, 0.86, 0.62), strength=5.0); pax = mat_masked(kit, 'utc_train_pax', (0.03, 0.03, 0.035), 0.8)
    head = mat_masked(kit, 'utc_train_head', (1, 1, 1), 0.2, emission=(1.0, 0.95, 0.85), strength=40.0); tail = mat_masked(kit, 'utc_train_tail', (0.4, 0, 0), 0.3, emission=(1.0, 0.06, 0.03), strength=20.0)
    dark = mat_masked(kit, 'utc_train_under', (0.05, 0.05, 0.05), 0.7)
    root = ex.empty(kit, 'utc_train'); A = cw._Acc(); CL, gap, W, H = 0.48, 0.02, 0.105, 0.165; n = 3; total = n * CL + (n - 1) * gap
    for c in range(n):
        x0 = -total / 2 + c * (CL + gap); x1 = x0 + CL
        A.add(*box(x0, -W / 2, 0.012, x1, W / 2, H), 0)
        A.add(*box(x0 + 0.01, -W / 2 + 0.006, 0.0, x1 - 0.01, W / 2 - 0.006, 0.014), 6)
        for s in (-1, 1):
            yy = s * (W / 2 + 0.0008); f = (lambda q: q) if s < 0 else (lambda q: q[::-1])
            A.add([(x0, yy, 0.030), (x1, yy, 0.030), (x1, yy, 0.042), (x0, yy, 0.042)], [f((0, 1, 2, 3))], 1)
            A.add([(x0 + 0.02, yy, 0.068), (x1 - 0.02, yy, 0.068), (x1 - 0.02, yy, 0.128), (x0 + 0.02, yy, 0.128)], [f((0, 1, 2, 3))], 2)
            if s < 0:
                for k in range(int(rng.integers(5, 9))):     # passengers: silhouettes against the warm windows
                    px = rng.uniform(x0 + 0.04, x1 - 0.04); ph = rng.uniform(0.0, 0.012)
                    V, F = ex.ell((px, yy - 0.0006, 0.090 + ph), (0.0085, 0.0008, 0.010), 1); A.add(V, F, 3)
                    V, F = ex.ell((px, yy - 0.0006, 0.070 + ph), (0.015, 0.0008, 0.012), 1); A.add(V, F, 3)
    for s in (-1, 1):
        V0, F0 = cw._icosphere(1)
        A.add(V0 * np.array([0.002, 0.009, 0.008]) + np.array([total / 2, s * 0.028, 0.035]), F0, 4)
        A.add(V0 * np.array([0.002, 0.007, 0.007]) + np.array([-total / 2, s * 0.028, 0.035]), F0, 5)
    A.build(bpy, 'utc_train_shell', [body, stripe, win, pax, head, tail, dark], False, kit.coll).parent = root
    # light streaks trailing the train (additive cards, camera only), brightest at the train
    sm, sgain = mat_add(kit, 'utc_streak', (1.0, 0.82, 0.58), 3.0, fade='x', lim=2.18)
    for k, (zz, w, L) in enumerate(((0.035, 0.008, 1.1), (0.098, 0.03, 0.8), (0.035, 0.006, 0.7))):
        V = [(-total / 2 - L, -W / 2 - 0.004, zz - w / 2), (-total / 2, -W / 2 - 0.004, zz - w / 2), (-total / 2, -W / 2 - 0.004, zz + w / 2), (-total / 2 - L, -W / 2 - 0.004, zz + w / 2)]
        ob = cw.mk_mesh(bpy, f'utc_streak{k}', V, [(0, 1, 2, 3)], [sm], None, False, kit.coll); ob.parent = root; hide_from_light(ob)
    lights = []
    for i, x in enumerate((-0.5, 0.5)):
        ld = bpy.data.lights.new(f'utc_train_l{i}', 'POINT'); ld.energy = 0.0; ld.color = (1.0, 0.86, 0.62); ld.shadow_soft_size = 0.03
        lo = bpy.data.objects.new(ld.name, ld); kit.coll.objects.link(lo); lo.parent = root; lo.location = (x, -W / 2 - 0.02, 0.10); lights.append(ld)
    ld = bpy.data.lights.new('utc_train_beam', 'SPOT'); ld.energy = 0.0; ld.color = (1.0, 0.94, 0.85); ld.spot_size = math.radians(70); ld.spot_blend = 0.5
    lo = bpy.data.objects.new(ld.name, ld); kit.coll.objects.link(lo); lo.parent = root; lo.location = (total / 2 + 0.01, 0, 0.05); lo.rotation_euler = (0, math.radians(90), 0); lights.append(ld)
    root.location = (-9.0, FY + 0.012 + W / 2, zf)
    return {'root': root, 'lights': lights, 'total': total, 'streak': sgain}

def build_old_city(kit, land, eggs):
    """Old brick foundations (a vaulted cellar with a barrel, a wall footing, a horseshoe), then the Roman floor:
    a mosaic slab, an amphora with coins, a fallen column drum."""
    bpy = kit.bpy; brick = mat_brick(kit, 'utc_brick_old', (0.58, 0.30, 0.18), (0.46, 0.24, 0.15), (0.40, 0.36, 0.30), 24.0)
    eggs.hole_ellipse('-Y', -0.75, -1.47, 0.20, 0.10, 0.12, 'utc_cellar', material=brick)
    th = np.linspace(0, math.pi, 22)
    arch = [(-0.75 + 0.215 * math.cos(a), 0.0, -1.47 + 0.115 * math.sin(a)) for a in th]
    eggs.obj('utc_arch', [(*cw._tube(arch, np.full(22, 0.018), 8, False), 0)], [brick], '-Y', 0.0, 0.0)
    # a barrel in the cellar
    prof = [(0.020, -0.03), (0.026, -0.015), (0.028, 0.0), (0.026, 0.015), (0.020, 0.03)]; V = []; F = []; seg = 18
    for k, (rr, hh) in enumerate(prof):
        for j in range(seg): a = 2 * math.pi * j / seg; V.append((hh, rr * math.cos(a), rr * math.sin(a)))
    for k in range(len(prof) - 1):
        for j in range(seg): a0 = k * seg + j; b0 = k * seg + (j + 1) % seg; F.append((a0, b0, b0 + seg, a0 + seg))
    F.append(tuple(range(seg))[::-1]); F.append(tuple(range((len(prof) - 1) * seg, len(prof) * seg)))
    eggs.obj('utc_barrel', [(V, F, 0)], [ex.mat_pbr(kit, 'utc_oak', (0.36, 0.22, 0.12), 0.7, bump=0.2)], '-Y', -0.70, -1.535, 0.05, 0.0)
    eggs.obj('utc_footing', [(*box(-0.36, -0.012, -0.075, 0.36, 0.06, 0.075), 0), (*box(-0.38, -0.016, -0.10, 0.38, 0.06, -0.075), 1)],
             [brick, cw.mat_simple(kit, 'utc_footstone', (0.55, 0.52, 0.48), 0.9, noise_amt=0.25, bump=0.6)], '-Y', 0.62, -1.47)
    th = np.linspace(0.35, 2 * math.pi - 0.35, 20)
    eggs.obj('utc_horseshoe', [(*cw._tube([(0.03 * math.cos(a), 0.0, 0.034 * math.sin(a)) for a in th], np.full(20, 0.0055), 6, False), 0)],
             [ex.mat_pbr(kit, 'utc_rust', (0.42, 0.20, 0.09), 0.8, metallic=0.4, bump=0.4)], '-Y', 1.42, -1.46, 0.0, 0.4)
    eggs.spot('-Y', -0.2, -1.48, power=4.5, out=0.6, up=0.25, size=70, name='utc_spot_bricks')
    # Roman floor: a mosaic slab, fallen and leaning back, half proud of the face
    m = cw._new_mat(bpy, 'utc_mosaic'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); px, py, pz = g.sep(tc.outputs['Object'])
    T = 95.0; qx = g.math('DIVIDE', g.math('FLOOR', g.math('MULTIPLY', px, T)), T); qz = g.math('DIVIDE', g.math('FLOOR', g.math('MULTIPLY', pz, T)), T)
    rr = g.math('MAXIMUM', g.math('ABSOLUTE', g.math('DIVIDE', qx, 0.17)), g.math('ABSOLUTE', g.math('DIVIDE', qz, 0.105)))
    band = g.ramp(rr, [(0.0, (0.80, 0.30, 0.16)), (0.12, (0.92, 0.88, 0.78)), (0.20, (0.10, 0.09, 0.09)), (0.27, (0.86, 0.66, 0.30)), (0.36, (0.92, 0.88, 0.78)),
                       (0.70, (0.10, 0.09, 0.09)), (0.76, (0.92, 0.88, 0.78)), (0.84, (0.72, 0.28, 0.16)), (0.92, (0.10, 0.09, 0.09))], 'CONSTANT')
    wave = g.math('GREATER_THAN', g.math('SINE', g.math('ADD', g.math('MULTIPLY', qx, 70.0), g.math('MULTIPLY', g.math('SINE', g.math('MULTIPLY', qz, 70.0)), 1.6))), 0.0)
    inwave = g.math('MULTIPLY', g.math('GREATER_THAN', rr, 0.40), g.math('LESS_THAN', rr, 0.66))
    col = g.mix(g.math('MULTIPLY', inwave, wave), band, srgb((0.18, 0.30, 0.36)))
    gx = g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', px, T)), 0.16); gz = g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', pz, T)), 0.16)
    lost = g.math('GREATER_THAN', g.noise(tc.outputs['Object'], 9.0, 3.0).outputs['Fac'], 0.66)
    grout = g.math('MAXIMUM', g.math('MAXIMUM', gx, gz), lost)
    col = g.mix(grout, col, srgb((0.42, 0.36, 0.28)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.5}); g.put(p, 'Coat Weight', 0.2)
    bmp = g.node('ShaderNodeBump', ins={'Strength': 0.5, 'Height': g.math('SUBTRACT', 1.0, grout), 'Distance': 0.0015}); g.put(p, 'Normal', bmp); cw._finish(g, p)
    rng = np.random.default_rng(31); n = 40; ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    rad = 1.0 - 0.08 * rng.uniform(0, 1, n); rad[5:9] *= 0.82; rad[24:27] *= 0.86
    V = [(0.0, 0.0, 0.0)] + [(0.20 * rad[k] * math.cos(a), 0.0, 0.125 * rad[k] * math.sin(a)) for k, a in enumerate(ang)]
    # clamp to a rough rectangle (a floor fragment, broken edges)
    V = [(max(-0.185, min(0.185, v[0])), 0.0, max(-0.112, min(0.112, v[2]))) for v in V]
    Fm = [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)]
    Vb = [(v[0], 0.014, v[2]) for v in V]; Fb = [(0, 1 + (k + 1) % n, 1 + k) for k in range(n)]
    side = [(1 + k, 1 + (k + 1) % n, n + 2 + (k + 1) % n, n + 2 + k) for k in range(n)]
    VV = V + Vb; FF = [tuple(i for i in f) for f in Fm] + [tuple(i + n + 1 for i in f) for f in Fb] + side
    slab = eggs.obj('utc_mosaic', [(np.array(VV)[:, [0, 1, 2]], FF, 0)], [m], '-Y', -0.55, -1.69, -0.008, 0.0)
    slab.rotation_euler = (math.radians(-20), 0, 0)
    eggs.spot('-Y', -0.55, -1.69, power=4.0, out=0.55, up=0.3, size=40, name='utc_spot_mosaic', color=(1.0, 0.86, 0.68))
    eggs.amphora('-Y', 0.25, -1.70, tilt=0.35, light=3.5)
    # a fallen column drum, fluted marble
    ring = 40; V = []; F = []
    for x in (-0.12, 0.12):
        for j in range(ring):
            a = 2 * math.pi * j / ring; rr_ = 0.052 * (1 - 0.07 * max(0.0, math.cos(a * 10)) ** 2); V.append((x, rr_ * math.cos(a) + 0.02, rr_ * math.sin(a)))
    F = [(j, (j + 1) % ring, ring + (j + 1) % ring, ring + j) for j in range(ring)] + [tuple(range(ring))[::-1], tuple(range(ring, 2 * ring))]
    eggs.obj('utc_column', [(V, F, 0)], [ex.mat_pbr(kit, 'utc_marble', (0.88, 0.85, 0.78), 0.35, coat=0.2, cavity=0.6)], '-Y', 0.95, -1.72, 0.0, 0.12)
    eggs.spot('-Y', 0.85, -1.70, power=3.0, out=0.5, up=0.25, size=40, name='utc_spot_column')

def build_motes(kit, n=46, seed=8):
    """Dust motes drifting in front of the face (catch the warm practicals)."""
    bpy = kit.bpy; rng = np.random.default_rng(seed); m = cw.mat_glow(kit, 'utc_mote', (1.0, 0.86, 0.66), 1.6); obs = []
    V0, F0 = cw._icosphere(1)
    for k in range(n):
        ob = cw.mk_mesh(bpy, f'utc_mote{k}', V0 * 0.0016, F0, [m], None, True, kit.coll); hide_from_light(ob)
        obs.append((ob, rng.uniform(-1.3, 1.5), rng.uniform(-0.22, -0.03), rng.uniform(-2.3, -0.05), rng.uniform(0, 6.28), rng.uniform(0.6, 1.4)))
    return obs

def build_background(kit, rng):
    """A far skyline at dusk (dark blocks with scattered lit windows) behind a haze card, so the frame has a city around it."""
    bpy = kit.bpy; m = cw._new_mat(bpy, 'utc_skyline'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    pos = tc.outputs['Object']; px, py, pz = g.sep(pos)
    br = g.node('ShaderNodeTexBrick', ins={'Vector': g.comb(g.math('ADD', px, py), pz, 0.0), 'Color1': (1, 1, 1, 1), 'Color2': (0, 0, 0, 1), 'Mortar': (0, 0, 0, 1), 'Scale': 3.0,
                                           'Mortar Size': 0.35, 'Brick Width': 0.45, 'Row Height': 0.5, 'Bias': 0.0})
    vo = g.voronoi(g.vmath('MULTIPLY', pos, (3.2, 3.2, 2.0)), 1.0, 'F1', rand=1.0)
    lit = g.math('MULTIPLY', g.math('GREATER_THAN', vo.outputs['Color'], 0.62), g.math('GREATER_THAN', br.outputs['Fac'], 0.5))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.04, 0.045, 0.07)), 'Roughness': 0.8})
    g.put(p, 'Emission Color', srgb((1.0, 0.72, 0.40))); g.put(p, 'Emission Strength', g.math('MULTIPLY', lit, 1.6)); cw._finish(g, p)
    A = cw._Acc()
    for k in range(34):
        a = math.radians(rng.uniform(55, 185)); R = rng.uniform(10.0, 15.0); w = rng.uniform(0.8, 2.0); d = rng.uniform(0.8, 1.6); h = rng.uniform(1.0, 5.5)
        cx, cy = R * math.cos(a), R * math.sin(a); V, F = box(-w / 2, -d / 2, -DEPTH - 0.01, w / 2, d / 2, -DEPTH + h + 2.0)
        ca, sa = math.cos(a), math.sin(a); V = [(cx + x * ca - y * sa, cy + x * sa + y * ca, z) for x, y, z in V]; A.add(V, F, 0)
    sk = A.build(bpy, 'utc_skyline', [m], False, kit.coll)
    for a in ('visible_shadow', 'visible_diffuse', 'visible_glossy'): setattr(sk, a, False)
    hm, _ = mat_add(kit, 'utc_haze', (0.86, 0.52, 0.36), 0.75, fade='1-z', lim=99.0)
    for k, a in enumerate((80, 120, 160)):
        ar = math.radians(a); R = 8.5; c = (R * math.cos(ar), R * math.sin(ar)); t_ = (-math.sin(ar), math.cos(ar)); hw = 4.6
        V = [(c[0] - t_[0] * hw, c[1] - t_[1] * hw, -DEPTH), (c[0] + t_[0] * hw, c[1] + t_[1] * hw, -DEPTH), (c[0] + t_[0] * hw, c[1] + t_[1] * hw, 1.8), (c[0] - t_[0] * hw, c[1] - t_[1] * hw, 1.8)]
        ob = cw.mk_mesh(bpy, f'utc_haze{k}', V, [(0, 1, 2, 3)], [hm], None, False, kit.coll); hide_from_light(ob)

def build_title(kit, cam):
    bpy = kit.bpy; cu = bpy.data.curves.new('utc_title', 'FONT'); cu.body = 'Under the City'; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    font = os.path.join(ROOT, 'ads', 'fonts', 'InstrumentSans.ttf')
    if os.path.exists(font): cu.font = bpy.data.fonts.load(font)
    cu.size = 0.085; cu.space_character = 1.06
    ob = bpy.data.objects.new('utc_title', cu); kit.coll.objects.link(ob)
    m = cw._new_mat(bpy, 'utc_titlemat'); g = G(m.node_tree, kit); a = g.value(0.0, 'utc_title_a')
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((1.0, 0.95, 0.88)), 'Strength': 1.6}); tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
    g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(e, mx.inputs[2]); cw._finish(g, mx); cu.materials.append(m)
    hide_from_light(ob); ob.parent = cam.ob; d = 2.0; half_h = d * (36.0 * 9 / 16) / 2 / 35.0
    ob.location = (0.0, half_h * 0.62, -d)
    return a


# =============================================================================================== harness entry points
def build(bpy, ctx):
    W, H = ctx['W'], ctx['H']; rng = np.random.default_rng(5)
    kit = cw.Kit(bpy, seed=5, loop=DURATION)
    trees = [(x, -0.655, 0.52, 'round') for x in (-2.05, -1.15, 0.0, 1.15, 2.05)] + [(x, 0.30, 0.42, 'round') for x in (-1.75, 0.95)]
    land = cw.block(kit, size=(SX, SY), depth=DEPTH, strata=STRATA, seed=5, top=lambda x, y: np.zeros_like(np.asarray(x, float)),
                    water=None, res=0.03, grass=0, trees=0, tree_spots=trees, tree_kinds=('round',), boulders=0, flowers=0, under=False, sway=1.3)
    rig = ex.cine_light(kit, land, SUN_AZ, SUN_EL, sun=3.2, sun_color=(1.0, 0.48, 0.24), fill=0.75, rim=0.8,
                        zenith=(0.035, 0.06, 0.16), horizon=(0.95, 0.46, 0.26), away=(0.26, 0.22, 0.40), ground=(0.06, 0.05, 0.07), amb=0.22)
    S = {'kit': kit, 'land': land, 'rig': rig}
    S['street'] = build_street(kit, land, rng)
    eggs = ex.Eggs(kit, land, light_power=0.9, light_color=(1.0, 0.84, 0.64)); S['eggs'] = eggs
    S['util'] = build_utilities(kit, land, eggs)
    S['sewer'] = build_sewer(kit, land, eggs, rng)
    S['metro'] = build_metro(kit, land, eggs)
    build_old_city(kit, land, eggs)
    eggs.dino('-Y', -0.12, -2.10, scale=0.72, light=4.0)
    eggs.ammonite('-Y', 1.05, -2.12, R=0.06)
    eggs.trilobite('-Y', -1.25, -2.30)
    eggs.finish()
    ex.soften_roots(land)
    ex.edge_spill(kit, land, '-Y', power=28.0)
    S['motes'] = build_motes(kit)
    build_background(kit, rng)
    cw.birds(kit, 3, center=(0.3, 0.6), radius=1.8, height=1.3)
    ex.finish(bpy, W, H, bloom=0.28, threshold=1.0, vignette=0.3)
    S['cam'] = ex.ShotCam(kit); S['title'] = build_title(kit, S['cam'])
    cw.apply_cycles(bpy, fast=True)
    cy = bpy.context.scene.cycles
    cy.max_bounces = 4; cy.diffuse_bounces = 2; cy.glossy_bounces = 2; cy.transmission_bounces = 4; cy.transparent_max_bounces = 10
    cy.adaptive_threshold = 0.04; cy.sample_clamp_direct = 12.0; cy.sample_clamp_indirect = 4.0
    frame(bpy, ctx, S, 0, 0.0)
    return S


# ---------------------------------------------------------------- motion (all pure functions of t)
def bus_x(t): return -1.55 + 0.30 * t if t < 13.0 else -2.75 + 0.30 * (t - 13.0)
def car_x(t): return 1.25 - 0.34 * t if t < 12.0 else 2.75 - 0.34 * (t - 15.0)
TRAIN = [(9.55, -3.1, 2.6), (16.9, 3.1, -2.6)]          # (start time, start x, speed m/s): pass 1 in the descent, pass 2 in the wide

def train_x(t):
    for t0, x0, v in TRAIN:
        x = x0 + v * (t - t0)
        if t >= t0 and abs(x) < 3.2: return x, v
    return -9.0, 2.6

def rat_pose(R, t):
    """Scurries in along the walkway, stops, sniffs; flinches and dashes off when the train rumbles past below."""
    keys_t = [0.0, 6.9, 7.9, 9.85, 10.5, 20.0]; keys_x = [1.6, 0.95, 0.30, 0.30, -0.45, -0.45]
    x = float(np.interp(t, keys_t, keys_x)); v = (np.interp(t + 0.02, keys_t, keys_x) - np.interp(t - 0.02, keys_t, keys_x)) / 0.04
    run = min(1.0, abs(v) / 0.4); R['root'].location.x = x; R['root'].rotation_euler = (0, 0, math.pi)
    ph = t * 26.0
    R['body'].location.z = 0.002 * run * abs(math.sin(ph))
    for i, lg in enumerate(R['legs']): lg.rotation_euler = (0, 0.9 * run * math.sin(ph + (math.pi if i in (1, 2) else 0)), 0)
    sniff = (1 - run) * (0.5 + 0.5 * math.sin(t * 9.0))
    look = smooth(9.75, 9.9, t) * (1 - smooth(10.0, 10.2, t))            # head up at the rumble
    R['head'].rotation_euler = (0, -0.25 * look - 0.12 * sniff + 0.05 * math.sin(t * 31.0) * (1 - run), 0.15 * math.sin(t * 2.3) * (1 - run))
    R['tail'].rotation_euler = (0, 0.1 * math.sin(t * 3.1), 0.35 * math.sin(t * 4.2 + 1.0) * (0.4 + 0.6 * run))

def shot_pose(name, u, t):
    """Camera for shot `name` at local progress u (0..1). Returns pos, target, lens, focus, fstop."""
    if name == 'street':      # high three-quarter over the street, a slow push down toward the cut edge
        e = ex.ease(u); az = math.radians(-66 + 6 * e); el = math.radians(27 - 7 * e); D = 5.0 - 1.1 * e; tgt = np.array((0.15 - 0.1 * e, -0.15, -0.10 - 0.12 * e))
        pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
        return pos, tgt, 35.0, 4.0, 22.0
    if name == 'descent':     # crane down the cut face, street to dinosaur
        ts = [4.5, 6.4, 8.3, 10.4, 12.4, 13.9, 15.5]
        tz = mono(ts, [0.06, -0.30, -0.69, -1.10, -1.48, -1.71, -2.08], t)
        tx = mono([4.5, 8.3, 10.4, 13.9, 15.5], [0.30, 0.25, 0.05, 0.10, -0.25], t)
        D = mono([4.5, 13.9, 15.5], [2.25, 2.15, 1.70], t); el = math.radians(mono([4.5, 7.0, 15.5], [15.0, 9.0, 6.0], t))
        tgt = np.array((tx, FY, tz)); pos = tgt + np.array([0.32, -D * math.cos(el), D * math.sin(el)])
        return pos, tgt, 35.0, float(np.linalg.norm(pos - tgt)), 5.6
    e = ex.ease(u)            # city: wide, low, a slow pull back and rise: the whole column
    az = math.radians(-60 + 4 * e); el = math.radians(6 + 4 * e); D = 8.6 + 0.8 * e; tgt = np.array((0.05, 0.0, -1.10 + 0.05 * e))
    pos = tgt + D * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    return pos, tgt, 35.0, D, 16.0

def frame(bpy, ctx, S, i, t):
    kit = S['kit']; kit.update(t)
    tl = ctx['timeline'].at(t) if ctx.get('timeline') else {'name': 'street', 'u': 0.0}
    pos, tgt, lens, focus, fstop = shot_pose(tl['name'], tl['u'], t)
    S['cam'].set(pos, tgt, lens, focus, fstop)
    S['title'].default_value = smooth(0.25, 0.85, t) * (1 - smooth(1.9, 2.5, t))
    st = S['street']
    # street lamps come on, one by one, with a flicker
    on = 0.0
    lev = []
    for k, lo in enumerate(st['lamps']['lights']):
        t0 = 0.55 + 0.32 * k; f = smooth(t0, t0 + 0.25, t)
        if t0 < t < t0 + 0.35 and int(t * 24) % 3 == 1: f *= 0.35
        lev.append(f); lo.data.energy = 1.1 * f
    st['lamps']['on'].default_value = float(np.mean(lev)); st['lamps']['cone'].default_value = float(np.mean(lev))
    sw = st['houses']['switch']
    for k, v in enumerate(sw): v.default_value = smooth((2.0, 3.3, 18.6)[k % 3], (2.0, 3.3, 18.6)[k % 3] + 0.12, t)
    # vehicles
    for kind, xf, y, sgn in (('bus', bus_x, -0.36, 1.0), ('car', car_x, -0.02, -1.0)):
        V = st[kind]; x = xf(t); V['root'].location = (x, y, 0.0); V['root'].rotation_euler = (0, 0, 0 if sgn > 0 else math.pi)
        for w in V['wheels']: w.rotation_euler = (0, sgn * x / V['r'], 0)
        V['beam'].data.energy = (1.4 if kind == 'bus' else 0.9) * (1.0 if abs(x) < LIM else 0.0)
    # steam
    for k, c in enumerate(st['steam']['cards']):
        ph = (t / 3.2 + k / 3.0) % 1.0; c.location = (MANHOLE_U + 0.01 * math.sin(t * 0.7 + k) + 0.012 * (k - 1), FY + 0.03, 0.02 + 0.10 * ph)
        c.scale = (1.0 + 0.8 * ph, 1, 1.0 + 0.5 * ph)
    # utilities: data pulses travel the cable, the worm wriggles
    U = S['util']
    for k, p in enumerate(U['pulses']):
        x = ((t * 0.9 + k * SX / 7) % SX) - SX / 2; p.location = (x, FY + 0.004, -0.150)
    U['worm'].location = (-0.98 + 0.006 * math.sin(t * 0.8), FY + 0.003, -0.43); U['worm'].rotation_euler = (0, 0.35 * math.sin(t * 2.6), 0.0)
    U['worm'].scale = (1.0 + 0.18 * math.sin(t * 5.0), 1.0, 1.0 - 0.1 * math.sin(t * 5.0))
    # sewer: lamp buzz, the drip, the rat
    sw_ = S['sewer']; v, ld = sw_['lamp']; fl = 1.0 - 0.25 * (math.sin(t * 37.0) > 0.93) - 0.1 * math.sin(t * 13.0) ** 8
    v.default_value = fl; ld.energy = 0.5 * fl
    drop, ringob, wl, d_at = sw_['drop']; per = 1.7; ph = (t % per) / per; zt = SEWER[0] + 0.07
    if ph < 0.45:
        q = ph / 0.45; drop.location = (0.42, FY + 0.05, zt - (zt - wl) * q * q); drop.hide_render = False; ringob.hide_render = True
    else:
        q = (ph - 0.45) / 0.55; drop.hide_render = True; ringob.hide_render = q > 0.8
        ringob.location = (0.42, FY + 0.05, wl + 0.0008); ringob.scale = (0.004 + 0.03 * q, 0.004 + 0.03 * q, 0.02)
    rat_pose(sw_['rat'], t)
    # metro
    T = S['metro']['train']; x, vel = train_x(t); T['root'].location.x = x; T['root'].rotation_euler = (0, 0, 0 if vel > 0 else math.pi)
    inside = 1.0 if abs(x) < 2.6 else 0.0
    for k, ld in enumerate(T['lights']): ld.energy = (0.5 if k < 2 else 2.5) * inside
    # dust motes drift; they jump a little as the train passes
    shake = math.exp(-((x) / 1.2) ** 2) if abs(x) < 3.0 else 0.0
    for ob, x0, d0, z0, phm, sp in S['motes']:
        ob.location = (x0 + 0.03 * math.sin(t * 0.3 * sp + phm) + 0.01 * shake * math.sin(t * 40 + phm), FY + d0, z0 + 0.025 * math.sin(t * 0.22 * sp + phm * 2) - 0.004 * t)
