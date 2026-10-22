"""Cinematic additions to the Cutaway kit (import next to cutaway.py; the kit itself is never edited).

    import cutaway as cw, extras as ex
    rig  = ex.cine_light(kit, land, sun_az=-168, sun_el=8)          # warm low sun, cool fill, rim, sky dome, hazy floor
    atm  = ex.atmosphere(kit, land)                                   # haze + ground fog pooling in the valley (one bounded volume)
    ex.gobo(kit, land, rig['sun_dir'])                                # cloud gaps: light shafts through the haze, drifting
    eggs = ex.Eggs(kit, land); eggs.dino('-Y', u, z); ...; eggs.finish()   # easter eggs in the cut face (+ museum lights)
    ex.deer(kit, land, x, y, yaw); ex.rabbit(...); ex.fox(...); ex.heron(...); ex.ducks(...); ex.fish(...)
    ex.fireflies(...); ex.petals(...); ex.butterflies(...)
    ex.finish(bpy, W, H)                                              # compositor: bloom + vignette
    cam = ex.ShotCam(kit); cam.set(pos, target, lens, focus, fstop)

Everything that moves is a pure function of t, registered with kit.on_frame (kit.update(t) poses it).
Face frames: a face is '-Y' (u = x) or '+X' (u = y); local object axes on a face: X along the face, Y into the block, Z up.
"""
import math

import numpy as np

import cutaway as cw

G = cw.G
srgb = cw.srgb


# =============================================================================================== small helpers
def ease(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)

def ease5(u):
    u = min(1.0, max(0.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)

def lerp(a, b, u):
    return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * u

def sph(az, el):
    a, e = math.radians(az), math.radians(el)
    return np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])

def look_at(ob, target):
    from mathutils import Vector
    d = Vector(tuple(np.asarray(target, float) - np.asarray(ob.location[:], float)))
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

def empty(kit, name, parent=None, loc=(0, 0, 0)):
    ob = kit.bpy.data.objects.new(name, None); kit.coll.objects.link(ob); ob.parent = parent; ob.location = loc; return ob

def ell(c, r, sub=2, lump=0.0, seed=0):
    """Ellipsoid (verts, faces) at c with radii r (optionally lumpy)."""
    V, F = cw._icosphere(sub)
    if lump: V = cw._lumpy(V, seed, lump, 2.0, lump * 0.3, 5.0)
    return V * np.asarray(r, float) + np.asarray(c, float), F

def cone(a, b, r0, r1=0.0002, ring=8):
    return cw._tube([a, (np.asarray(a) + np.asarray(b)) / 2, b], [r0, (r0 + r1) / 2, r1], ring)

def rot_pts(V, axis, ang, about=(0, 0, 0)):
    """Rotate points about an axis ('x', 'y', 'z') through `about`."""
    V = np.asarray(V, float) - np.asarray(about, float); c, s = math.cos(ang), math.sin(ang); out = V.copy()
    i, j = {'x': (1, 2), 'y': (2, 0), 'z': (0, 1)}[axis]
    out[:, i] = V[:, i] * c - V[:, j] * s; out[:, j] = V[:, i] * s + V[:, j] * c
    return out + np.asarray(about, float)

def part(kit, name, pieces, mats, parent=None, loc=(0, 0, 0), smooth=True):
    """One object from pieces [(V, F, mat_index)], origin = its pivot; parented."""
    A = cw._Acc()
    for V, F, m in pieces: A.add(V, F, m)
    ob = A.build(kit.bpy, name, mats, smooth, kit.coll); ob.parent = parent; ob.location = loc; return ob

def mat(kit, name, color, rough=0.6, **kw):
    key = ('ex', name)
    if key not in kit.mats: kit.mats[key] = cw.mat_simple(kit, name, color, rough, **kw)
    return kit.mats[key]

def mat_pbr(kit, name, color, rough=0.5, metallic=0.0, emission=None, strength=0.0, film=0.0, coat=0.0, bump=0.0, bump_scale=60.0,
            transmission=0.0, flecks=0.0):
    """Principled with optional thin film (nacre), coat, voronoi facet bump (glitter) and emissive flecks."""
    key = ('ex', name)
    if key in kit.mats: return kit.mats[key]
    m = cw._new_mat(kit.bpy, name); g = G(m.node_tree, kit)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb(color), 'Roughness': rough, 'Metallic': metallic})
    if film: g.put(p, 'Thin Film Thickness', film); g.put(p, 'Thin Film IOR', 1.45)
    if coat: g.put(p, 'Coat Weight', coat); g.put(p, 'Coat Roughness', 0.08)
    if transmission: g.put(p, 'Transmission Weight', transmission); g.put(p, 'IOR', 1.55)
    tc = g.node('ShaderNodeTexCoord')
    if bump:
        vo = g.voronoi(tc.outputs['Object'], bump_scale, 'F1')
        b = g.node('ShaderNodeBump', ins={'Strength': bump, 'Height': vo.outputs['Distance'], 'Distance': 0.004}); g.put(p, 'Normal', b)
    if emission is not None: g.put(p, 'Emission Color', srgb(emission)); g.put(p, 'Emission Strength', strength)
    if flecks:
        vo2 = g.voronoi(tc.outputs['Object'], 420.0, 'F1'); f = g.math('LESS_THAN', vo2.outputs['Distance'], 0.07)
        g.put(p, 'Emission Color', srgb((1.0, 0.86, 0.5))); g.link(g.math('MULTIPLY', f, flecks), cw._sock(p.inputs, 'Emission Strength'))
    cw._finish(g, p); kit.mats[key] = m
    try: m.cycles.emission_sampling = 'NONE' if not (emission or flecks) else 'FRONT'
    except Exception: pass
    return m

def time_value(kit, g, name='ex_t'):
    """A Value node that holds the time t in seconds (set every frame)."""
    v = g.value(0.0, name); kit.on_frame(lambda t, v=v: setattr(v, 'default_value', float(t))); return v


# =============================================================================================== light, sky, floor
def cine_light(kit, land, sun_az=-168.0, sun_el=8.0, sun=5.0, sun_color=(1.0, 0.66, 0.38), fill=0.9, rim=1.0,
               zenith=(0.20, 0.27, 0.46), horizon=(0.98, 0.70, 0.50), away=(0.56, 0.52, 0.62), ground=(0.24, 0.20, 0.22), amb=0.32):
    """Golden-hour rig. Warm key sun low and raking; a cool fill from the sky (world light) and a large soft cool area light
    on the camera side; a warm rim light behind the block; a sky dome that glows toward the sun (camera rays only);
    a floor under the block that fades into the haze with distance (no visible horizon edge)."""
    bpy = kit.bpy; sd = sph(sun_az, sun_el)
    # ---- world: camera sees the sky dome; everything else sees a dim cool ambient
    wd = bpy.data.worlds.new('ex_world'); bpy.context.scene.world = wd
    try: wd.use_nodes = True
    except Exception: pass
    nt = wd.node_tree; nt.nodes.clear(); g = G(nt, kit)
    tc = g.node('ShaderNodeTexCoord'); d = g.vmath('NORMALIZE', tc.outputs['Generated']); dz = g.sep(d)[2]
    dot = g.vmath('DOT_PRODUCT', d, tuple(sd)); dp = g.math('MAXIMUM', dot, 0.0)
    hz = g.vmath('NORMALIZE', g.vmath('MULTIPLY', d, (1, 1, 0))); hd = g.math('MAXIMUM', g.vmath('DOT_PRODUCT', hz, tuple(sd * np.array([1, 1, 0]) / max(1e-6, np.linalg.norm(sd[:2])))), 0.0)
    horiz = g.mix(g.math('POWER', hd, 2.2), srgb(away), srgb(horizon))                     # warm toward the sun, lilac away
    el = g.math('ADD', g.math('MULTIPLY', dz, 1.0), 0.0)
    sky = g.mix(g.math('POWER', g.math('MAXIMUM', el, 0.0), 0.55), horiz, srgb(zenith))
    below = g.mix(g.math('MINIMUM', g.math('MULTIPLY', g.math('ABSOLUTE', g.math('MINIMUM', el, 0.0)), 5.0), 1.0), horiz, srgb(ground))
    col = g.mix(g.math('GREATER_THAN', el, 0.0), below, sky)
    glow = g.math('ADD', g.math('MULTIPLY', g.math('POWER', dp, 8.0), 0.9), g.math('MULTIPLY', g.math('POWER', dp, 1400.0), 30.0))
    col = g.mix(1.0, col, g.vmath('SCALE', srgb(sun_color)[:3], scale=glow), 'ADD')
    bg_cam = g.node('ShaderNodeBackground', ins={'Color': col, 'Strength': 1.0})
    bg_light = g.node('ShaderNodeBackground', ins={'Color': g.mix(0.75, (0.42, 0.52, 0.85), col), 'Strength': amb})
    lp = g.node('ShaderNodeLightPath'); mx = g.node('ShaderNodeMixShader')
    g.link(lp.outputs['Is Camera Ray'], mx.inputs[0]); g.link(bg_light, mx.inputs[1]); g.link(bg_cam, mx.inputs[2])
    o = g.node('ShaderNodeOutputWorld'); g.link(mx, o.inputs['Surface'])
    # ---- lights
    out = {'sun_dir': sd, 'world': wd}
    out['sun'] = cw._sun(kit, sun_az, sun_el, sun, 1.2, sun_color, 'ex_sun')
    def area(name, az, el, dist, size, power, color, target=(0, 0, -0.3)):
        ld = bpy.data.lights.new(name, 'AREA'); ld.size = size; ld.shape = 'DISK'; ld.energy = power; ld.color = color
        ob = bpy.data.objects.new(name, ld); kit.coll.objects.link(ob); ob.location = tuple(np.array(target) + sph(az, el) * dist)
        look_at(ob, target); ob.visible_camera = False; ob.visible_glossy = False if name.endswith('fill') else True; return ob
    if fill: out['fill'] = area('ex_fill', -20, 32, 9.0, 6.0, 900 * fill, (0.62, 0.74, 1.0))
    if rim: out['rim'] = area('ex_rim', sun_az + 62, 22, 8.0, 3.0, 1400 * rim, (1.0, 0.78, 0.58), (0, 0, 0.1))
    # ---- floor that melts into the haze
    m = cw._new_mat(bpy, 'ex_floor'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    r = g.vmath('LENGTH', g.vmath('MULTIPLY', tc.outputs['Object'], (1, 1, 0)))
    far = g.math('MULTIPLY', g.math('SUBTRACT', r, 3.0), 1 / 22.0, clamp=True)
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': srgb((0.30, 0.25, 0.24)), 'Roughness': 0.95})
    e = g.node('ShaderNodeEmission', ins={'Color': g.mix(0.35, srgb(ground), srgb(horizon)), 'Strength': 0.30})
    mx = g.node('ShaderNodeMixShader'); g.link(g.math('POWER', far, 0.7), mx.inputs[0]); g.link(p, mx.inputs[1]); g.link(e, mx.inputs[2])
    cw._finish(g, mx)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    out['floor'] = cw._plane(kit, 'ex_floor', 60, -land.depth - 0.0005, m)
    return out


# =============================================================================================== atmosphere (volumes)
def atmosphere(kit, land, haze=0.10, fog=2.4, fog_top=0.11, mist=1.0, spill=0.5, ceiling=1.6, wind=(0.035, 0.012), color=(1.0, 0.93, 0.86),
               aniso=0.62, name='ex_atmos'):
    """One bounded volume box over the block: (1) soft haze that thins with height and fades out a little beyond the block
    edges (so the edges glow and shafts show), (2) ground fog pooling in the low ground and the river valley, broken up by
    drifting noise, densest just above the water (morning mist). Forward scattering (anisotropy) makes shafts toward the
    sun bright. The fog drifts with `wind` (m/s), deterministic in t."""
    bpy = kit.bpy; sx, sy = land.size; lv = land.level if land.level is not None else 0.0
    x0, x1, y0, y1 = -sx / 2 - spill, sx / 2 + spill, -sy / 2 - spill, sy / 2 + spill; z0, z1 = lv - 0.02, ceiling
    V, F = cw._box(x0, y0, z0, x1, y1, z1)
    m = cw._new_mat(bpy, name); g = G(m.node_tree, kit)
    tc = g.node('ShaderNodeTexCoord'); pos = tc.outputs['Object']; px, py, pz = g.sep(pos)
    tv = time_value(kit, g)
    # distance outside the footprint -> fade
    ox = g.math('MAXIMUM', g.math('SUBTRACT', g.math('ABSOLUTE', px), sx / 2), 0.0)
    oy = g.math('MAXIMUM', g.math('SUBTRACT', g.math('ABSOLUTE', py), sy / 2), 0.0)
    out = g.math('MAXIMUM', ox, oy); edge = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', out, 1.0 / spill), clamp=True)
    hfall = g.math('EXPONENT', g.math('MULTIPLY', g.math('MAXIMUM', pz, 0.0), -1.4))
    # drifting noise
    drift = g.comb(g.math('MULTIPLY', tv, -wind[0]), g.math('MULTIPLY', tv, -wind[1]), 0.0)
    q = g.vmath('ADD', pos, drift)
    n1 = g.noise(g.vmath('MULTIPLY', q, (1.0, 1.0, 2.2)), 1.7, 3.0, 0.55, '4D', g.math('MULTIPLY', tv, 0.04))
    n2 = g.noise(g.vmath('MULTIPLY', q, (1.0, 1.0, 3.0)), 5.5, 2.0, 0.5, '4D', g.math('MULTIPLY', tv, 0.07))
    brk = g.math('MULTIPLY', g.math('SUBTRACT', g.math('ADD', n1.outputs['Fac'], g.math('MULTIPLY', n2.outputs['Fac'], 0.35)), 0.52), 2.6, clamp=True)
    hz = g.math('MULTIPLY', g.math('MULTIPLY', edge, hfall), haze * 0.75)
    hz = g.math('ADD', hz, g.math('MULTIPLY', g.math('MULTIPLY', edge, g.math('MULTIPLY', brk, hfall)), haze * 0.5))
    # ground fog: density falls from the water level up to fog_top above it
    fz = g.math('SUBTRACT', 1.0, g.math('DIVIDE', g.math('SUBTRACT', pz, lv), fog_top), clamp=True)
    fz = g.math('POWER', fz, 1.6)
    fedge = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', out, 1.0 / 0.03), clamp=True)          # fog stays on the block (spills a hair over the edge)
    fogd = g.math('MULTIPLY', g.math('MULTIPLY', fz, g.math('ADD', g.math('MULTIPLY', brk, 0.85), 0.15)), g.math('MULTIPLY', fedge, fog))
    # mist sits on the water: an extra thin layer right at the surface
    mz = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', pz, lv + 0.012)), 1 / 0.03), clamp=True)
    fogd = g.math('ADD', fogd, g.math('MULTIPLY', g.math('MULTIPLY', mz, brk), mist * fog * 0.8))
    dens = g.math('ADD', hz, fogd)
    sc = g.node('ShaderNodeVolumeScatter', ins={'Color': srgb(color), 'Anisotropy': aniso}); g.put(sc, 'Density', dens)
    ab = g.node('ShaderNodeVolumeAbsorption', ins={'Color': srgb((0.92, 0.88, 0.86))}); g.put(ab, 'Density', g.math('MULTIPLY', dens, 0.15))
    ad = g.node('ShaderNodeAddShader'); g.link(sc, ad.inputs[0]); g.link(ab, ad.inputs[1])
    o = g.node('ShaderNodeOutputMaterial', target='ALL'); g.link(ad, o.inputs['Volume'])
    try: m.cycles.volume_sampling = 'DISTANCE'
    except Exception: pass
    ob = cw.mk_mesh(bpy, name, V, F, [m], None, False, kit.coll)
    return ob

def gobo(kit, land, sun_dir, dist=4.5, size=(10.0, 5.0), cover=0.45, scale=0.55, drift=0.05, name='ex_gobo'):
    """Clouds between the sun and the block (shadow only, invisible to the camera): gaps let shafts of light through the
    haze and dapple the top; the pattern drifts slowly (deterministic)."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); tv = time_value(kit, g)
    p = g.vmath('ADD', tc.outputs['Object'], g.comb(g.math('MULTIPLY', tv, drift), 0.0, 0.0))
    n = g.noise(p, scale, 3.0, 0.6, '4D', g.math('MULTIPLY', tv, 0.02))
    blk = g.math('MULTIPLY', g.math('SUBTRACT', n.outputs['Fac'], 0.5 - cover * 0.3), 7.0, clamp=True)
    tr = g.node('ShaderNodeBsdfTransparent'); df = g.node('ShaderNodeBsdfDiffuse', ins={'Color': (0, 0, 0)}); mx = g.node('ShaderNodeMixShader')
    g.link(g.math('MULTIPLY', blk, 0.92), mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(df, mx.inputs[2]); cw._finish(g, mx)
    w, h = size; V = [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)]
    ob = cw.mk_mesh(bpy, name, V, [(0, 1, 2, 3)], [m], None, False, kit.coll)
    c = np.array([0, 0, 0.25]) + np.asarray(sun_dir) * dist; ob.location = tuple(c)
    from mathutils import Vector
    ob.rotation_euler = Vector(tuple(-np.asarray(sun_dir))).to_track_quat('Z', 'Y').to_euler()
    for a in ('visible_camera', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(ob, a, False)
    return ob


class Shafts:
    """Art-directed god rays (the cheap half of the hybrid): long soft additive cards along the sunlight, crossing the block
    top at canopy height, billboarded to the camera around their own axis every frame, brightest when the camera looks
    toward the sun (forward scattering), breaking up and shimmering with drifting dust. Invisible to every ray but the
    camera's. Call update(camera_location) after the camera is posed."""
    def __init__(self, kit, land, sun_dir, n=16, seed=91, strength=1.0, color=(1.0, 0.80, 0.56), length=(3.6, 2.2), z=(0.10, 0.62), width=(0.05, 0.22),
                 spots=None, name='ex_shaft'):
        bpy = kit.bpy; self.sd = np.asarray(sun_dir, float) / np.linalg.norm(sun_dir); rng = np.random.default_rng(seed); sx, sy = land.size
        m = cw._new_mat(bpy, name + '_mat'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); geo = g.node('ShaderNodeNewGeometry'); tv = time_value(kit, g)
        oi = g.node('ShaderNodeObjectInfo'); lx, ly, _ = g.sep(tc.outputs['Generated'])
        across = g.math('EXPONENT', g.math('MULTIPLY', g.math('POWER', g.math('MULTIPLY', g.math('SUBTRACT', ly, 0.5), 2.0), 2.0), -3.2))
        along = g.math('MULTIPLY', g.math('MULTIPLY', lx, 6.0, clamp=True), g.math('MULTIPLY', g.math('SUBTRACT', 1.0, lx), 2.2, clamp=True))
        wp = g.sep(geo.outputs['Position'])
        ox = g.math('MAXIMUM', g.math('SUBTRACT', g.math('ABSOLUTE', wp[0]), sx / 2 - 0.05), 0.0); oy = g.math('MAXIMUM', g.math('SUBTRACT', g.math('ABSOLUTE', wp[1]), sy / 2 - 0.05), 0.0)
        foot = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('MAXIMUM', ox, oy), 1 / 0.35), clamp=True)
        dust = g.noise(g.comb(g.math('ADD', g.math('MULTIPLY', lx, 7.0), g.math('MULTIPLY', tv, 0.25)), g.math('MULTIPLY', ly, 1.5), g.math('MULTIPLY', oi.outputs['Random'], 30.0)), 2.2, 3.0, 0.6)
        brk = g.math('ADD', 0.35, g.math('MULTIPLY', dust.outputs['Fac'], 0.9))
        shimmer = g.math('ADD', 0.75, g.math('MULTIPLY', g.math('SINE', g.math('ADD', g.math('MULTIPLY', tv, 1.3), g.math('MULTIPLY', oi.outputs['Random'], 20.0))), 0.25))
        view = g.vmath('DOT_PRODUCT', g.vmath('SCALE', geo.outputs['Incoming'], scale=-1.0), tuple(self.sd))
        phase = g.math('ADD', 0.12, g.math('MULTIPLY', g.math('POWER', g.math('MAXIMUM', view, 0.0), 6.0), 1.6))
        a = g.math('MULTIPLY', g.math('MULTIPLY', g.math('MULTIPLY', across, along), g.math('MULTIPLY', foot, brk)), g.math('MULTIPLY', shimmer, phase))
        e = g.node('ShaderNodeEmission', ins={'Color': srgb(color)}); g.put(e, 'Strength', g.math('MULTIPLY', a, 0.55 * strength))
        tr = g.node('ShaderNodeBsdfTransparent'); ad = g.node('ShaderNodeAddShader'); g.link(tr, ad.inputs[0]); g.link(e, ad.inputs[1]); cw._finish(g, ad)
        try: m.cycles.emission_sampling = 'NONE'
        except Exception: pass
        self.cards = []
        for i in range(n):
            if spots is not None: c = spots[i % len(spots)]; px, py = c[0] + rng.normal(0, 0.25), c[1] + rng.normal(0, 0.25)
            else: px, py = rng.uniform(-sx / 2 * 0.85, sx / 2 * 0.85), rng.uniform(-sy / 2 * 0.85, sy / 2 * 0.85)
            P = np.array([px, py, float(land.height(np.array([px]), np.array([py]))[0]) + rng.uniform(*z)])
            L1, L2 = length[0] * rng.uniform(0.7, 1.2), length[1] * rng.uniform(0.7, 1.2); w = rng.uniform(*width)
            V = [(-L2, -w / 2, 0), (L1, -w / 2, 0), (L1, w / 2, 0), (-L2, w / 2, 0)]   # local X runs toward the sun
            ob = cw.mk_mesh(bpy, f'{name}{i}', V, [(0, 1, 2, 3)], [m], None, False, kit.coll); ob.location = tuple(P)
            for at in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_shadow', 'visible_volume_scatter'): setattr(ob, at, False)
            self.cards.append(ob)
    def update(self, cam):
        from mathutils import Matrix
        X = self.sd
        for ob in self.cards:
            v = np.asarray(cam, float) - np.asarray(ob.location[:], float); vp = v - (v @ X) * X; nz = np.linalg.norm(vp)
            Z = vp / nz if nz > 1e-6 else np.array([0, 0, 1.0])
            Y = np.cross(Z, X); Y /= np.linalg.norm(Y); Z = np.cross(X, Y)
            ob.rotation_euler = Matrix(((X[0], Y[0], Z[0]), (X[1], Y[1], Z[1]), (X[2], Y[2], Z[2]))).to_euler()


# =============================================================================================== compositor finish
def finish(bpy, W, H, bloom=0.22, threshold=1.2, size=0.55, vignette=0.26):
    """Bloom on bright highlights (water glints, lit windows, the sun) and a gentle vignette."""
    sc = bpy.context.scene
    ng = bpy.data.node_groups.new('ex_finish', 'CompositorNodeTree')
    ng.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    N, L = ng.nodes, ng.links
    rl = N.new('CompositorNodeRLayers'); go = N.new('NodeGroupOutput')
    gl = N.new('CompositorNodeGlare')
    gl.inputs['Type'].default_value = 'Bloom'; gl.inputs['Quality'].default_value = 'High'
    gl.inputs['Threshold'].default_value = threshold; gl.inputs['Strength'].default_value = bloom; gl.inputs['Size'].default_value = size
    gl.inputs['Clamp'].default_value = True; gl.inputs['Maximum'].default_value = 40.0
    L.new(rl.outputs['Image'], gl.inputs['Image'])
    ic = N.new('CompositorNodeImageCoordinates'); L.new(rl.outputs['Image'], ic.inputs['Image'])
    sp = N.new('ShaderNodeSeparateXYZ'); L.new(ic.outputs['Normalized'], sp.inputs[0])
    def m(op, a, vb=None, b=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        if isinstance(a, (int, float)): n.inputs[0].default_value = a
        else: L.new(a, n.inputs[0])
        if b is not None: L.new(b, n.inputs[1])
        elif vb is not None: n.inputs[1].default_value = vb
        return n.outputs[0]
    dx = m('SUBTRACT', sp.outputs[0], 0.5); dy = m('MULTIPLY', m('SUBTRACT', sp.outputs[1], 0.5), H / W)
    r2 = m('ADD', m('MULTIPLY', dx, b=dx), b=m('MULTIPLY', dy, b=dy))
    vg = N.new('ShaderNodeMapRange'); vg.interpolation_type = 'SMOOTHSTEP'; L.new(r2, vg.inputs['Value'])
    vg.inputs['From Min'].default_value = 0.05; vg.inputs['From Max'].default_value = 0.36
    vg.inputs['To Min'].default_value = 1.0; vg.inputs['To Max'].default_value = 1.0 - vignette
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    L.new(gl.outputs['Image'], mul.inputs['A']); L.new(vg.outputs[0], mul.inputs['B'])
    L.new(mul.outputs['Result'], go.inputs[0])
    sc.compositing_node_group = ng; sc.render.use_compositing = True
    return ng


# =============================================================================================== camera
class ShotCam:
    """One camera with depth of field; set(pos, target, lens, focus, fstop) per frame (focus: metres, or None = target)."""
    def __init__(self, kit, name='ex_cam'):
        bpy = kit.bpy; cd = bpy.data.cameras.new(name); cd.sensor_width = 36.0; cd.clip_start = 0.01; cd.clip_end = 300
        cd.dof.use_dof = True; cd.dof.aperture_blades = 7; cd.dof.aperture_rotation = 0.3
        self.ob = bpy.data.objects.new(name, cd); kit.coll.objects.link(self.ob); bpy.context.scene.camera = self.ob
    def set(self, pos, target, lens=50.0, focus=None, fstop=8.0, roll=0.0):
        self.ob.location = tuple(map(float, pos)); look_at(self.ob, target)
        if roll:
            from mathutils import Euler, Matrix
            self.ob.rotation_euler = (self.ob.rotation_euler.to_matrix() @ Matrix.Rotation(math.radians(roll), 3, 'Z')).to_euler()
        cd = self.ob.data; cd.lens = lens
        cd.dof.focus_distance = float(focus if focus is not None else np.linalg.norm(np.asarray(target, float) - np.asarray(pos, float)))
        cd.dof.aperture_fstop = fstop


# =============================================================================================== faces, cavities, museum lights
class Face:
    """A cut face of the block. u runs along the face (left to right seen from outside), z is height, d is depth into
    the block (d > 0 inside). Objects built in face-local axes (X along, Y inward, Z up) are placed with put()."""
    def __init__(self, land, name):
        sx, sy = land.size; self.name = name; self.land = land
        if name == '-Y': self.o = np.array([0.0, -sy / 2, 0.0]); self.r = np.array([1.0, 0, 0]); self.n = np.array([0, 1.0, 0]); self.rz = 0.0
        elif name == '+X': self.o = np.array([sx / 2, 0.0, 0.0]); self.r = np.array([0, 1.0, 0]); self.n = np.array([-1.0, 0, 0]); self.rz = math.pi / 2
        else: raise ValueError(name)
    def world(self, u, z, d=0.0): return self.o + u * self.r + d * self.n + np.array([0, 0, z])
    def put(self, ob, u, z, d=0.0, tilt=0.0):
        ob.location = tuple(self.world(u, z, d)); ob.rotation_euler = (0.0, -tilt, self.rz); return ob
    def top(self, u):
        p = self.world(u, 0, 0.004); return float(self.land.height(np.array([p[0]]), np.array([p[1]]))[0])

def bowl(a, b, depth, rings=8, seg=28):
    """Inside of a half-ellipsoid hollow opening on the face plane (Y = 0), going `depth` into the block (+Y)."""
    V = []; F = []
    for i in range(rings):
        th = (math.pi / 2) * i / rings
        for j in range(seg):
            ph = 2 * math.pi * j / seg; V.append((a * math.cos(th) * math.cos(ph), depth * math.sin(th), b * math.cos(th) * math.sin(ph)))
    V.append((0, depth, 0)); pole = len(V) - 1
    for i in range(rings - 1):
        for j in range(seg):
            k = i * seg + j; k2 = i * seg + (j + 1) % seg; F.append((k, k + seg, k2 + seg, k2))
    base = (rings - 1) * seg; F += [(base + j, pole, base + (j + 1) % seg) for j in range(seg)]
    return V, F

def half_tube(P2, r, ring=10):
    """Inside of a half-round tunnel along a path of (u, z) points on the face plane, going r into the block."""
    P = np.asarray(P2, float); T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.stack([-T[:, 1], T[:, 0]], 1)
    V = []; F = []
    for k in range(len(P)):
        for j in range(ring + 1):
            ph = math.pi * j / ring; c = math.cos(ph) * r; V.append((P[k, 0] + c * N[k, 0], r * math.sin(ph), P[k, 1] + c * N[k, 1]))
    for k in range(len(P) - 1):
        for j in range(ring):
            a = k * (ring + 1) + j; F.append((a, a + ring + 1, a + ring + 2, a + 1))
    return V, F

def mat_cavity(kit, color=(0.20, 0.13, 0.08)):
    key = ('ex', 'cavity')
    if key in kit.mats: return kit.mats[key]
    m = cw._new_mat(kit.bpy, 'ex_cavity'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
    n = g.noise(tc.outputs['Object'], 90.0, 4.0); n2 = g.noise(tc.outputs['Object'], 14.0, 3.0)
    col = g.mix(n2.outputs['Fac'], srgb(color), srgb(tuple(c * 1.6 for c in color)))
    col = g.mix(g.math('MULTIPLY', n.outputs['Fac'], 0.5), col, srgb((0.05, 0.035, 0.02)))
    p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.95})
    b = g.node('ShaderNodeBump', ins={'Strength': 0.8, 'Height': n.outputs['Fac'], 'Distance': 0.004}); g.put(p, 'Normal', b)
    cw._finish(g, p); kit.mats[key] = m; return m

class Eggs:
    """Easter eggs in the cut faces. Each adds objects (relief, half proud of the face) or a hollow (the wall material is
    made transparent over the opening and a bowl or tunnel mesh closes it from inside), plus a museum spot light.
    Call finish() once at the end (it patches the wall material with the openings)."""
    def __init__(self, kit, land, light_power=1.0, light_color=(1.0, 0.90, 0.76)):
        self.kit = kit; self.land = land; self.faces = {k: Face(land, k) for k in ('-Y', '+X')}
        self.openings = []          # (face, kind, data)
        self.lp = light_power; self.lc = light_color; self.items = {}
    # ---------------------------------------------------------------- shared
    def spot(self, face, u, z, power=4.0, out=0.55, up=0.32, size=34.0, blend=0.75, side=0.0, color=None, name='ex_museum'):
        bpy = self.kit.bpy; F = self.faces[face]; tgt = F.world(u, z, 0.0)
        pos = F.world(u + side, z + up, -out)
        ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = power * self.lp; ld.spot_size = math.radians(size); ld.spot_blend = blend
        ld.shadow_soft_size = 0.03; ld.color = color or self.lc
        ob = bpy.data.objects.new(name, ld); self.kit.coll.objects.link(ob); ob.location = tuple(pos); look_at(ob, tgt)
        ob.visible_camera = False; return ob
    def obj(self, name, pieces, mats, face, u, z, d=0.0, tilt=0.0):
        ob = part(self.kit, name, pieces, mats); self.faces[face].put(ob, u, z, d, tilt); return ob
    def hole_ellipse(self, face, u, z, a, b, depth, name):
        V, F = bowl(a * 1.03, b * 1.03, depth); ob = part(self.kit, name, [(V, F, 0)], [mat_cavity(self.kit)])
        self.faces[face].put(ob, u, z); self.openings.append((face, 'ell', (u, z, a, b))); return ob
    def hole_tunnel(self, face, P2, r, name):
        P2 = np.asarray(P2, float); V, F = half_tube(P2, r * 1.03)
        pieces = [(V, F, 0)]
        for e in (P2[0], P2[-1]):
            bv, bf = bowl(r * 1.03, r * 1.03, r * 1.0); pieces.append((np.asarray(bv) + np.array([e[0], 0, e[1]]), bf, 0))
        ob = part(self.kit, name, pieces, [mat_cavity(self.kit)]); self.faces[face].put(ob, 0.0, 0.0)
        for a, b in zip(P2[:-1], P2[1:]): self.openings.append((face, 'cap', (a[0], a[1], b[0], b[1], r)))
        return ob
    def finish(self):
        """Make the wall material transparent over every opening (shader mask in face coordinates)."""
        if not self.openings: return
        m = self.land.mats['strata']; nt = m.node_tree; g = G(nt, self.kit)
        outn = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial'][0]
        surf_link = outn.inputs['Surface'].links[0]; src = surf_link.from_socket
        tc = g.node('ShaderNodeTexCoord'); px, py, pz = g.sep(tc.outputs['Object']); sx, sy = self.land.size
        total = None
        for face in ('-Y', '+X'):
            ops = [o for o in self.openings if o[0] == face]
            if not ops: continue
            if face == '-Y': on = g.math('LESS_THAN', g.math('ABSOLUTE', g.math('ADD', py, sy / 2)), 0.004); u = px
            else: on = g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', px, sx / 2)), 0.004); u = py
            acc = None
            for _, kind, dat in ops:
                if kind == 'ell':
                    cu, cz, a, b = dat
                    du = g.math('DIVIDE', g.math('SUBTRACT', u, cu), a); dz = g.math('DIVIDE', g.math('SUBTRACT', pz, cz), b)
                    q = g.math('ADD', g.math('MULTIPLY', du, du), g.math('MULTIPLY', dz, dz)); k = g.math('LESS_THAN', q, 1.0)
                else:
                    au, az, bu, bz, r = dat; eu, ez = bu - au, bz - az; L2 = eu * eu + ez * ez
                    t = g.math('DIVIDE', g.math('ADD', g.math('MULTIPLY', g.math('SUBTRACT', u, au), eu), g.math('MULTIPLY', g.math('SUBTRACT', pz, az), ez)), L2)
                    t = g.math('MINIMUM', g.math('MAXIMUM', t, 0.0), 1.0)
                    qu = g.math('SUBTRACT', u, g.math('ADD', au, g.math('MULTIPLY', t, eu))); qz = g.math('SUBTRACT', pz, g.math('ADD', az, g.math('MULTIPLY', t, ez)))
                    k = g.math('LESS_THAN', g.math('ADD', g.math('MULTIPLY', qu, qu), g.math('MULTIPLY', qz, qz)), r * r)
                acc = k if acc is None else g.math('MAXIMUM', acc, k)
            fm = g.math('MULTIPLY', acc, on); total = fm if total is None else g.math('MAXIMUM', total, fm)
        tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader')
        g.link(total, mx.inputs[0]); nt.links.new(src, mx.inputs[1]); g.link(tr, mx.inputs[2])
        nt.links.remove(surf_link); nt.links.new(mx.outputs[0], outn.inputs['Surface'])

    # ---------------------------------------------------------------- the eggs
    def mole(self, face, u, z, length=0.55, r=0.026, light=3.0):
        """A mole digging along its tunnel just under the turf, ending in a round nest of dry grass. Paws dig, nose twitches."""
        kit = self.kit; s = np.linspace(0, 1, 14)
        P = np.stack([u + s * length, z + 0.022 * np.sin(s * 5.0 + 0.7) - 0.03 * s], 1)
        self.hole_tunnel(face, P, r, 'ex_mole_tunnel')
        nu, nz = P[-1, 0] + 0.05, P[-1, 1] - 0.012
        self.hole_ellipse(face, nu, nz, 0.058, 0.044, 0.05, 'ex_mole_nest')
        straw = mat(kit, 'ex_straw', (0.78, 0.64, 0.36), 0.8); A = []
        rng = np.random.default_rng(3)
        for k in range(46):
            a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0.022, 0.04); c = np.array([rr * math.cos(a), rng.uniform(0.012, 0.03), -0.03 + abs(rr * math.sin(a)) * 0.35])
            dv = np.array([-math.sin(a), rng.uniform(-0.3, 0.3), math.cos(a) * 0.3]) * rng.uniform(0.012, 0.022)
            v, f = cw._tube([c - dv, c, c + dv], [0.0012, 0.0013, 0.001], 4); A.append((v, f, 0))
        self.obj('ex_nest', A, [straw], face, nu, nz)
        # the mole: velvet body, pink snout and big pink digging paws (separate parts so they move)
        fur = mat(kit, 'ex_molefur', (0.12, 0.11, 0.12), 0.55, sss=0.0, noise_amt=0.15); pink = mat(kit, 'ex_pink', (0.92, 0.56, 0.58), 0.5, sss=0.2)
        eye = mat(kit, 'ex_eye', (0.01, 0.01, 0.01), 0.15)
        mu = u + length * 0.62; mz = float(np.interp(0.62, s, P[:, 1])) - 0.004
        root = empty(kit, 'ex_mole'); self.faces[face].put(root, mu, mz, 0.008)
        bv, bf = ell((0, 0, 0), (0.026, 0.013, 0.0145), 2, 0.05, 2)
        body = part(kit, 'ex_mole_body', [(bv, bf, 0), (*ell((0.029, -0.002, 0.001), (0.007, 0.006, 0.006)), 0),
                                           (*cone((0.033, -0.002, 0.001), (0.046, -0.003, 0.0), 0.0042, 0.0016, 8), 1),
                                           (*ell((0.046, -0.003, 0.0), (0.0022, 0.0022, 0.0022)), 1),
                                           (*ell((0.03, -0.008, 0.005), (0.0011, 0.0011, 0.0011)), 2),
                                           (*cone((-0.025, 0, 0.003), (-0.034, 0, 0.006), 0.0018, 0.0006, 6), 1)], [fur, pink, eye], root)
        paws = []
        for side, yy in ((1, -0.008), (-1, 0.008)):
            pv, pf = ell((0.006, 0, -0.002), (0.0085, 0.0035, 0.0075))
            fingers = [(*cone((0.012, 0, -0.002 + 0.003 * k), (0.019, 0, -0.002 + 0.0045 * k), 0.0012, 0.0003, 5), 0) for k in (-1, 0, 1)]
            paws.append(part(kit, f'ex_mole_paw{side}', [(pv, pf, 0)] + fingers, [pink], root, (0.018, yy, -0.006)))
        @kit.on_frame
        def _dig(t, paws=paws, body=body):
            for k, pw in enumerate(paws):
                ph = 2 * math.pi * 2.2 * t + k * math.pi; pw.rotation_euler = (0.0, 0.5 * math.sin(ph), (0.5 if k else -0.5) + 0.25 * math.cos(ph))
            body.rotation_euler = (0.0, 0.03 * math.sin(2 * math.pi * 1.1 * t), 0.04 * math.sin(2 * math.pi * 4.3 * t) * (math.sin(2 * math.pi * 0.4 * t) > 0.3))
        _dig(0.0)
        # a little molehill above the tunnel start
        F = self.faces[face]; p = F.world(u + 0.02, 0, 0.09)
        hv, hf = ell((0, 0, 0), (0.06, 0.05, 0.032), 3, 0.25, 9); hv[:, 2] = np.maximum(hv[:, 2], -0.004)
        hill = part(kit, 'ex_molehill', [(hv, hf, 0)], [mat(kit, 'ex_soil', (0.30, 0.20, 0.12), 0.95, noise_amt=0.4, bump=0.6)])
        cw._place(self.land, hill, p[0], p[1], -0.006)
        self.spot(face, mu + 0.08, mz, 2.6 * light / 3.0, out=0.42, up=0.26, size=40, name='ex_spot_mole')
        self.items['mole'] = (face, mu, mz)

    def hedgehog(self, face, u, z, light=3.0):
        """A hedgehog curled up asleep in a leaf-lined burrow; it breathes."""
        kit = self.kit; a, b, dep = 0.085, 0.058, 0.08
        self.hole_ellipse(face, u, z, a, b, dep, 'ex_hog_burrow')
        leaves = [mat(kit, f'ex_leaf{k}', c, 0.7, sss=0.1) for k, c in enumerate([(0.78, 0.40, 0.12), (0.62, 0.28, 0.10), (0.86, 0.62, 0.20)])]
        rng = np.random.default_rng(5); A = []
        for k in range(40):
            ang = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0, 0.8)
            c = np.array([rr * a * 0.9 * math.cos(ang), dep * 0.25 + rng.uniform(0, dep * 0.6), -b * 0.72 + rng.uniform(0, 0.02)])
            v, f = ell(c, (0.011, 0.007, 0.0016)); v = rot_pts(v, 'z', rng.uniform(0, 3.14), c); v = rot_pts(v, 'x', rng.uniform(-0.4, 0.4), c)
            A.append((v, f, int(rng.integers(0, 3))))
        self.obj('ex_hog_leaves', A, leaves, face, u, z)
        spine = mat_pbr(kit, 'ex_spines', (0.42, 0.32, 0.22), 0.6); skin = mat(kit, 'ex_hogface', (0.62, 0.48, 0.36), 0.7, sss=0.15)
        nose = mat(kit, 'ex_nose', (0.03, 0.02, 0.02), 0.2)
        root = empty(kit, 'ex_hog'); self.faces[face].put(root, u - 0.004, z - b * 0.38, 0.045)
        bv, bf = ell((0, 0, 0), (0.034, 0.03, 0.026), 2)
        P = [(bv, bf, 1)]
        V0, F0 = cw._icosphere(2); rng = np.random.default_rng(8)
        for v in V0:
            if v[0] > 0.55 and v[2] < 0.2: continue
            d = v / np.linalg.norm(v); base = d * np.array([0.033, 0.029, 0.025])
            tipc = base + (d + rng.normal(0, 0.15, 3) - np.array([0.25, 0, 0])) * 0.017
            cv, cf = cone(base, tipc, 0.0026, 0.0003, 5); P.append((cv, cf, 0))
        P.append((*ell((0.03, -0.004, -0.008), (0.012, 0.011, 0.01)), 1))
        P.append((*ell((0.041, -0.006, -0.011), (0.0028, 0.0028, 0.0028)), 2))
        body = part(kit, 'ex_hog_body', P, [spine, skin, nose], root)
        @kit.on_frame
        def _breathe(t, body=body):
            s = 1.0 + 0.035 * math.sin(2 * math.pi * 0.45 * t); body.scale = (s, s, 1.0 + 0.05 * math.sin(2 * math.pi * 0.45 * t))
        _breathe(0.0)
        self.spot(face, u, z, 2.4 * light / 3.0, out=0.45, up=0.25, size=40, side=-0.06, name='ex_spot_hog')
        self.items['hedgehog'] = (face, u, z)

    def chest(self, face, u, z, tilt=0.12, coins=36, light=4.0):
        """A buried pirate chest, lid ajar, gold glowing inside, coins spilling down the soil."""
        kit = self.kit; w, h, dp = 0.13, 0.065, 0.075
        wood = cw._new_mat(kit.bpy, 'ex_chestwood'); g = G(wood.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
        z_ = g.sep(tc.outputs['Object'])[2]; planks = g.math('FRACT', g.math('MULTIPLY', z_, 1 / 0.016)); line = g.math('LESS_THAN', planks, 0.12)
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (8.0, 8.0, 60.0)), 6.0, 3.0)
        col = g.mix(n.outputs['Fac'], srgb((0.36, 0.20, 0.09)), srgb((0.52, 0.31, 0.14))); col = g.mix(g.math('MULTIPLY', line, 0.8), col, srgb((0.12, 0.07, 0.03)))
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.75}); cw._finish(g, p)
        iron = mat_pbr(kit, 'ex_iron', (0.24, 0.22, 0.20), 0.45, metallic=0.85)
        gold = mat_pbr(kit, 'ex_gold', (1.0, 0.74, 0.30), 0.25, metallic=1.0, bump=0.25, bump_scale=900.0)
        goldglow = mat_pbr(kit, 'ex_goldglow', (1.0, 0.76, 0.32), 0.25, metallic=1.0, emission=(1.0, 0.72, 0.30), strength=2.5)
        P = []
        v, f = cw._box(-w / 2, -dp / 2, -h / 2, w / 2, dp / 2, h / 2); P.append((v, f, 0))
        for bx in (-w * 0.32, w * 0.32):
            v, f = cw._box(bx - 0.006, -dp / 2 - 0.002, -h / 2 - 0.001, bx + 0.006, dp / 2 + 0.002, h / 2 + 0.001); P.append((v, f, 1))
        v, f = cw._box(-0.009, -dp / 2 - 0.004, h / 2 - 0.022, 0.009, -dp / 2, h / 2 - 0.002); P.append((v, f, 2))
        # treasure heap inside (visible through the open lid)
        rng = np.random.default_rng(11)
        for k in range(26):
            c = np.array([rng.uniform(-w * 0.42, w * 0.42), rng.uniform(-dp * 0.35, dp * 0.35), h / 2 + rng.uniform(-0.004, 0.01)])
            cv, cf = cw._tube([c, c + np.array([0, 0, 0.002])], [0.008, 0.008], 10); cv = rot_pts(cv, 'x', rng.uniform(-0.8, 0.8), c); P.append((cv, cf, 3))
        body = self.obj('ex_chest', P, [wood, iron, gold, goldglow], face, u, z, 0.012, tilt)
        # the lid: a half barrel, hinged at the back edge, open 38 degrees
        th = np.linspace(0, math.pi, 13); prof = [(w / 2 * 0 + 0, dp / 2 * math.cos(a), dp / 2 * 0.62 * math.sin(a)) for a in th]
        V = []; F = []
        for xx in (-w / 2, w / 2):
            V += [(xx, y_, z__) for _, y_, z__ in prof]
        n_ = len(prof); F += [(k, k + 1, n_ + k + 1, n_ + k) for k in range(n_ - 1)] + [tuple(range(n_))[::-1], tuple(range(n_, 2 * n_))]
        V = np.array(V) + np.array([0, -dp / 2, 0])          # hinge line at y = +dp/2 after the shift back
        V[:, 1] += dp / 2 * 0  # keep
        lidp = [(V - np.array([0, -dp / 2, 0]) - np.array([0, dp / 2, 0]), F, 0)]
        for bx in (-w * 0.32, w * 0.32):
            bv = [(bx - 0.006, y_ * 1.04 - dp / 2, z__ * 1.04) for _, y_, z__ in prof] + [(bx + 0.006, y_ * 1.04 - dp / 2, z__ * 1.04) for _, y_, z__ in prof]
            lidp.append((bv, [(k, k + 1, n_ + k + 1, n_ + k) for k in range(n_ - 1)], 1))
        lid = part(kit, 'ex_chest_lid', lidp, [wood, iron], body, (0, dp / 2, h / 2)); lid.rotation_euler = (math.radians(-38), 0, 0)
        # coins spilling out of the front-left corner, down the soil
        A = []
        for k in range(coins):
            s = (k / coins) ** 0.8; c = np.array([-w * 0.45 - 0.02 - s * 0.09 + rng.normal(0, 0.012), rng.uniform(-0.004, 0.006), -h * 0.2 - s * 0.16 + rng.normal(0, 0.01)])
            cv, cf = cw._tube([c, c + np.array([0, 0.0022, 0])], [0.0085, 0.0085], 12)
            cv = rot_pts(cv, 'z', rng.uniform(-0.9, 0.9), c); cv = rot_pts(cv, 'x', rng.uniform(-0.6, 0.6), c); A.append((cv, cf, 0))
        self.obj('ex_coins', A, [gold], face, u, z, 0.0, tilt)
        self.spot(face, u - 0.03, z - 0.03, 4.0 * light / 4.0, out=0.5, up=0.3, size=36, name='ex_spot_chest')
        self.items['chest'] = (face, u, z)

    def amphora(self, face, u, z, tilt=0.55, light=3.5):
        """A Roman amphora lying in the clay with two shards and a few green bronze coins by its mouth."""
        kit = self.kit; L = 0.20
        prof = [(0.0, 0.0), (0.006, 0.005), (0.012, 0.022), (0.03, 0.05), (0.042, 0.085), (0.045, 0.11), (0.04, 0.135), (0.026, 0.152),
                (0.014, 0.165), (0.012, 0.19), (0.016, 0.197), (0.016, 0.202), (0.011, 0.202)]
        seg = 22; V = []; F = []
        for k, (r, hh) in enumerate(prof):
            for j in range(seg): a = 2 * math.pi * j / seg; V.append((hh - L / 2, r * math.cos(a), r * math.sin(a)))
        for k in range(len(prof) - 1):
            for j in range(seg): a0 = k * seg + j; b0 = k * seg + (j + 1) % seg; F.append((a0, b0, b0 + seg, a0 + seg))
        clay = cw._new_mat(kit.bpy, 'ex_terracotta'); g = G(clay.node_tree, kit); tc = g.node('ShaderNodeTexCoord')
        n = g.noise(tc.outputs['Object'], 35.0, 4.0); n2 = g.noise(tc.outputs['Object'], 6.0, 3.0)
        col = g.mix(n2.outputs['Fac'], srgb((0.70, 0.36, 0.20)), srgb((0.82, 0.50, 0.30)))
        col = g.mix(g.math('MULTIPLY', g.math('GREATER_THAN', n.outputs['Fac'], 0.62), 0.6), col, srgb((0.30, 0.20, 0.12)))
        p = g.node('ShaderNodeBsdfPrincipled', ins={'Base Color': col, 'Roughness': 0.8})
        b = g.node('ShaderNodeBump', ins={'Strength': 0.35, 'Height': n.outputs['Fac'], 'Distance': 0.003}); g.put(p, 'Normal', b); cw._finish(g, p)
        P = [(V, F, 0)]
        for side in (-1, 1):
            hp = [(0.135 - L / 2, side * 0.036, 0.0), (0.16 - L / 2, side * 0.04, 0.0), (0.18 - L / 2, side * 0.03, 0.0), (0.185 - L / 2, side * 0.014, 0.0)]
            hv, hf = cw._tube(cw.catmull(hp, 8), np.full(8, 0.0042), 6); P.append((hv, hf, 0))
        ob = self.obj('ex_amphora', P, [clay], face, u, z, 0.006, tilt)
        bronze = mat_pbr(kit, 'ex_bronze', (0.36, 0.52, 0.40), 0.5, metallic=0.6)
        A = []; rng = np.random.default_rng(21)
        tipdir = np.array([math.cos(tilt), 0, math.sin(tilt)])
        for k in range(7):
            c = tipdir * (0.12 + rng.uniform(0, 0.05)) + np.array([rng.normal(0, 0.012), rng.uniform(-0.003, 0.004), rng.normal(0, 0.012) - 0.01])
            cv, cf = cw._tube([c, c + np.array([0, 0.0018, 0])], [0.0068, 0.0068], 10); cv = rot_pts(cv, 'x', rng.uniform(-0.5, 0.5), c); A.append((cv, cf, 0))
        for k in range(2):
            c = np.array([-0.1 - 0.04 * k, 0.004, -0.05 + 0.03 * k]); sv, sf = ell(c, (0.018, 0.004, 0.012), 1, 0.3, k)
            A.append((sv, sf, 1))
        self.obj('ex_amphora_bits', A, [bronze, clay], face, u, z)
        self.spot(face, u, z, 3.5 * light / 3.5, out=0.55, up=0.3, size=34, name='ex_spot_amphora')
        self.items['amphora'] = (face, u, z)

    def ammonite(self, face, u, z, R=0.055, turns=3.3, tilt=0.4, light=3.0):
        """A big ammonite: a ribbed logarithmic spiral with a nacre sheen."""
        kit = self.kit; th = np.linspace(0, turns * 2 * math.pi, 260); b = math.log(R / 0.003) / th[-1]; r = 0.003 * np.exp(b * th)
        C = np.stack([r * np.cos(th), r * np.sin(th)], 1); rad = 0.30 * r * (1 + 0.10 * np.maximum(0, np.sin(th * 7.0)) ** 2)
        V = []; F = []; ring = 10
        for k in range(len(C)):
            nrm = C[k] / (np.linalg.norm(C[k]) + 1e-9)
            for j in range(ring):
                ph = 2 * math.pi * j / ring; V.append((C[k, 0] + rad[k] * math.cos(ph) * nrm[0], 0.004 - rad[k] * 0.75 * math.sin(ph), C[k, 1] + rad[k] * math.cos(ph) * nrm[1]))
        for k in range(len(C) - 1):
            for j in range(ring): a = k * ring + j; b_ = k * ring + (j + 1) % ring; F.append((a, b_, b_ + ring, a + ring))
        shell = mat_pbr(kit, 'ex_nacre', (0.80, 0.64, 0.46), 0.32, film=420.0, coat=0.4)
        self.obj('ex_ammonite', [(V, F, 0)], [shell], face, u, z, 0.0, tilt)
        self.spot(face, u, z, 3.0 * light / 3.0, out=0.45, up=0.28, size=30, name='ex_spot_ammonite')
        self.items['ammonite'] = (face, u, z)

    def trilobite(self, face, u, z, Lt=0.10, tilt=-0.3, light=3.0):
        """A trilobite in relief: head shield, segmented three-lobed thorax, tail."""
        kit = self.kit; ns, nt_ = 48, 22; V = []; F = []
        for i in range(ns + 1):
            s = i / ns * 2 - 1
            if s > 0.45: hw = 0.5 * Lt * math.sqrt(max(0.0, 1 - ((s - 0.45) / 0.58) ** 2)) * 1.0
            elif s > -0.55: hw = 0.5 * Lt * (0.84 + 0.06 * s)
            else: hw = 0.5 * Lt * 0.8 * math.sqrt(max(0.0, 1 - ((s + 0.55) / 0.47) ** 2))
            hw = max(hw, 0.0004)
            for j in range(nt_ + 1):
                tt = j / nt_ * 2 - 1; ax = math.exp(-(tt / 0.28) ** 2)
                seg = 0.0 if s > 0.45 or s < -0.55 else 0.22 * math.sin((s + 0.55) * 46.0) ** 2
                hgt = Lt * 0.11 * math.sqrt(max(0.0, 1 - tt * tt)) * (1 + 0.8 * ax) * (1 - seg) + (Lt * 0.035 if s > 0.45 and ax > 0.4 else 0)
                V.append((s * Lt * 0.5, 0.002 - hgt, tt * hw))
        for i in range(ns):
            for j in range(nt_): a = i * (nt_ + 1) + j; F.append((a, a + 1, a + nt_ + 2, a + nt_ + 1))
        V = np.array(V)
        for side in (-1, 1):   # the eyes
            ev, ef = ell((Lt * 0.36, -Lt * 0.09, side * Lt * 0.17), (0.005, 0.004, 0.005)); V = np.vstack([V, ev]); F += [tuple(np.array(f) + len(V) - len(ev)) for f in ef]
        stone = mat_pbr(kit, 'ex_trilo', (0.24, 0.20, 0.18), 0.35, coat=0.3)
        self.obj('ex_trilobite', [(V, F, 0)], [stone], face, u, z, 0.0, tilt)
        self.spot(face, u, z, 3.0 * light / 3.0, out=0.45, up=0.28, size=30, name='ex_spot_trilobite')
        self.items['trilobite'] = (face, u, z)

    def dino(self, face, u, z, scale=1.0, light=5.0):
        """A tyrannosaur skeleton lying in the shale, head thrown back (the classic fossil pose), tiny arms."""
        kit = self.kit; s = scale; y0 = 0.004
        bone = mat_pbr(kit, 'ex_bone', (0.84, 0.77, 0.62), 0.6, coat=0.1, bump=0.3, bump_scale=140.0); dark = mat(kit, 'ex_socket', (0.06, 0.05, 0.04), 0.9)
        tooth = mat_pbr(kit, 'ex_tooth', (0.96, 0.93, 0.84), 0.35)
        def pt(P2, r0, r1, ring=8, m=0, n=14):
            C = cw.catmull(P2, n); R = np.linspace(r0, r1, n); out = []
            for (a, c), rr in zip(C, R): out.append((a * s, y0, c * s))
            v, f = cw._tube(out, R * s, ring); return (v, f, m)
        P = []
        spine = [(-0.56, -0.03), (-0.44, 0.0), (-0.30, 0.03), (-0.16, 0.05), (0.0, 0.06), (0.12, 0.075), (0.22, 0.07), (0.29, 0.10), (0.31, 0.17), (0.27, 0.23), (0.21, 0.26)]
        C = cw.catmull(spine, 70)
        for k, (a, c) in enumerate(C):                       # vertebrae beads, bigger at the hip, tiny at the tail tip
            w_ = k / (len(C) - 1); r = (0.005 + 0.010 * math.sin(math.pi * min(1.0, w_ * 1.25)) ** 0.8) * s
            v, f = ell((a * s, y0, c * s), (r * 0.9, r, r * 1.05), 1); P.append((v, f, 0))
            if 0.35 < w_ < 0.75 and k % 2 == 0:              # neural spines on the back
                v, f = cw._tube([(a * s, y0, c * s), (a * s - 0.004 * s, y0, c * s + 0.03 * s)], [r * 0.45, r * 0.25], 5); P.append((v, f, 0))
        for k, a in enumerate(np.linspace(0.02, 0.21, 9)):      # ribs
            c = float(np.interp(a, [0.0, 0.12, 0.22], [0.06, 0.075, 0.07])); L = 0.12 - 0.035 * abs(k - 4) / 4
            P.append(pt([(a, c), (a + 0.025, c - L * 0.5), (a + 0.012, c - L)], 0.0045, 0.0022, 6))
        P.append((*ell((0.0, y0, 0.07 * s), (0.075 * s, 0.012 * s, 0.032 * s), 2), 0))       # pelvis
        P.append(pt([(0.0, 0.05), (0.05, -0.02), (0.07, -0.08)], 0.012, 0.009))              # femur
        P.append(pt([(0.07, -0.08), (0.04, -0.14), (0.0, -0.19)], 0.009, 0.007))             # tibia
        P.append(pt([(0.0, -0.19), (0.03, -0.205), (0.05, -0.21)], 0.006, 0.005))             # foot
        for k in range(3): P.append(pt([(0.05, -0.21), (0.068 + 0.006 * k, -0.215 + 0.008 * (k - 1)), (0.082 + 0.008 * k, -0.222 + 0.012 * (k - 1))], 0.004, 0.0015, 5))
        P.append(pt([(-0.03, 0.04), (0.04, -0.03), (0.035, -0.09), (-0.01, -0.15)], 0.009, 0.006))   # far leg (offset)
        P.append(pt([(0.21, 0.05), (0.235, 0.02), (0.255, 0.005)], 0.004, 0.003, 6))          # the tiny arms
        for k in range(2): P.append(pt([(0.255, 0.005), (0.27, -0.002 + 0.006 * k)], 0.0025, 0.001, 5))
        P.append(pt([(0.195, 0.045), (0.215, 0.015), (0.232, 0.006)], 0.0035, 0.0025, 6))
        body = self.obj('ex_dino', P, [bone, dark], face, u, z)
        # the skull: lofted sections, jaw slightly open, dark eye socket and window, teeth
        Ls = 0.20 * s; secs = 22; ring = 14; V = []; F = []; JV = []; JF = []
        def h_top(q): return (0.060 * (1 - 0.66 * q) + 0.010 * math.sin(math.pi * q) + 0.006 * math.exp(-((q - 0.22) / 0.06) ** 2)) * s
        def h_bot(q): return (-0.032 * (1 - 0.55 * q)) * s
        def wid(q): return (0.026 * (1 - 0.55 * q)) * s
        for i in range(secs + 1):
            q = i / secs; xx = -q * Ls; zt, zb, ww = h_top(q), h_bot(q), wid(q); zc = (zt + zb) / 2; rz = (zt - zb) / 2
            rnd_ = math.sqrt(max(0.05, min(1.0, q / 0.06))) if q < 0.06 else 1.0
            for j in range(ring):
                a = 2 * math.pi * j / ring; V.append((xx, y0 + ww * rnd_ * math.cos(a), zc + rz * rnd_ * math.sin(a)))
            if i < secs and 0.04 < q < 0.96:
                jt = zb + 0.002 * s; jb = jt - (0.026 * (1 - 0.45 * q)) * s; jc = (jt + jb) / 2; jr = (jt - jb) / 2
                for j in range(ring): a = 2 * math.pi * j / ring; JV.append((xx, y0 + ww * 0.85 * math.cos(a), jc + jr * math.sin(a)))
        for i in range(secs):
            for j in range(ring): a = i * ring + j; b_ = i * ring + (j + 1) % ring; F.append((a, b_, b_ + ring, a + ring))
        F.append(tuple(range(ring))[::-1]); F.append(tuple(range(secs * ring, secs * ring + ring)))
        nj = len(JV) // ring
        for i in range(nj - 1):
            for j in range(ring): a = i * ring + j; b_ = i * ring + (j + 1) % ring; JF.append((a, b_, b_ + ring, a + ring))
        JF.append(tuple(range(ring))[::-1]); JF.append(tuple(range((nj - 1) * ring, nj * ring)))
        piv = np.array([-0.05 * Ls, 0, h_bot(0.05)]); JV = rot_pts(JV, 'y', math.radians(-6), piv)
        SP = [(V, F, 0), (JV, JF, 0)]
        for q, zz, rr in ((0.26, 0.55, 0.012), (0.52, 0.35, 0.011), (0.10, 0.35, 0.007)):   # eye socket, antorbital window, temporal window
            c = np.array([-q * Ls, y0 - wid(q) * 0.97, (h_top(q) + h_bot(q)) / 2 + zz * (h_top(q) - h_bot(q)) / 2 * 0.6])
            ev, ef = ell(c, (rr * s * (1.4 if q > 0.4 else 1.0), 0.0016, rr * s)); SP.append((ev, ef, 1))
        for q in np.linspace(0.3, 0.95, 11):                 # teeth
            b0 = np.array([-q * Ls, y0 - wid(q) * 0.7, h_bot(q) + 0.002 * s]); tv, tf = cone(b0, b0 + np.array([-0.002, 0, -0.011 * s]), 0.0025 * s, 0.0002, 6); SP.append((tv, tf, 2))
        sk = part(kit, 'ex_dino_skull', SP, [bone, dark, tooth])
        # skull at the end of the neck, pointing back and up (head thrown back)
        F_ = self.faces[face]; base = np.array([0.21, 0.26]) * s
        sk.parent = body; sk.location = (base[0], 0.0, base[1]); sk.rotation_euler = (0.0, math.radians(22), 0.0)
        self.spot(face, u + 0.05, z + 0.02, 5.0 * light / 5.0, out=0.75, up=0.45, size=46, name='ex_spot_dino')
        self.spot(face, u + 0.20 * s, z + 0.28 * s, 0.8 * light / 5.0, out=0.32, up=0.16, size=30, side=0.08, name='ex_spot_skull')
        self.items['dino'] = (face, u, z); self.items['skull'] = (face, u + 0.12 * s, z + 0.28 * s)

    def gold(self, face, pts, width=0.022, nuggets=9, light=3.0):
        """A glittering gold-bearing quartz vein across the deep rock, with nuggets standing proud."""
        kit = self.kit; P = cw.catmull(pts, 60); rng = np.random.default_rng(31)
        quartz = mat_pbr(kit, 'ex_quartz', (0.62, 0.60, 0.56), 0.35, coat=0.3, flecks=3.0)
        gold = mat_pbr(kit, 'ex_gold', (1.0, 0.74, 0.30), 0.25, metallic=1.0, bump=0.25, bump_scale=900.0)
        T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.stack([-T[:, 1], T[:, 0]], 1)
        w = width * (0.6 + 0.8 * np.abs(np.sin(np.linspace(0, 9, len(P))) * np.cos(np.linspace(0, 4, len(P)))))
        V = []; F = []
        for k in range(len(P)):
            for side in (-1, 1): V.append((P[k, 0] + side * w[k] * N[k, 0], -0.0015, P[k, 1] + side * w[k] * N[k, 1]))
        for k in range(len(P) - 1): F.append((2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2))
        A = [(V, F, 0)]
        for k in range(nuggets):
            i = int(rng.integers(3, len(P) - 3)); c = np.array([P[i, 0] + rng.normal(0, 0.006), 0.0, P[i, 1] + rng.normal(0, 0.004)])
            r = rng.uniform(0.006, 0.014); nv, nf = ell(c, (r * 1.3, r * 0.8, r), 2, 0.35, k); A.append((nv, nf, 1))
        for k in range(120):    # fine gold specks along the vein
            i = int(rng.integers(0, len(P))); c = np.array([P[i, 0] + rng.normal(0, w[i] * 0.6), -0.002, P[i, 1] + rng.normal(0, w[i] * 0.6)])
            nv, nf = ell(c, (0.0022, 0.001, 0.0018), 1); A.append((nv, nf, 1))
        self.obj('ex_goldvein', A, [quartz, gold], face, 0.0, 0.0)
        mid = P[len(P) // 2]; self.spot(face, mid[0], mid[1], 3.0 * light / 3.0, out=0.6, up=0.35, size=48, name='ex_spot_gold')
        self.items['gold'] = (face, float(mid[0]), float(mid[1]))

    def geode(self, face, u, z, a=0.10, b=0.085, light=3.0):
        """A geode cracked open in the deep rock: a pale agate rim and a hollow of glowing amethyst points."""
        kit = self.kit; dep = 0.07
        self.hole_ellipse(face, u, z, a, b, dep, 'ex_geode_hole')
        rim = mat_pbr(kit, 'ex_agate', (0.78, 0.80, 0.84), 0.3, coat=0.5)
        amy = mat_pbr(kit, 'ex_amethyst', (0.55, 0.28, 0.80), 0.08, emission=(0.62, 0.32, 0.95), strength=0.35, coat=0.6)
        A = []; rng = np.random.default_rng(41)
        th = np.linspace(0, 2 * math.pi, 49)       # rim: a lumpy ring proud of the face
        ring = [(a * 1.06 * math.cos(t) * (1 + 0.05 * math.sin(5 * t)), -0.003, b * 1.06 * math.sin(t) * (1 + 0.05 * math.cos(4 * t))) for t in th]
        rv, rf = cw._tube(ring, np.full(len(ring), 0.011), 8, False); A.append((rv, rf, 0))
        for k in range(150):                      # crystals on the inside surface, pointing to the centre
            th_ = rng.uniform(0.05, 1.45); ph = rng.uniform(0, 2 * math.pi)
            p = np.array([a * 0.98 * math.cos(th_) * math.cos(ph), dep * 0.98 * math.sin(th_), b * 0.98 * math.cos(th_) * math.sin(ph)])
            tip = p + (np.array([0, dep * 0.35, 0]) - p) * rng.uniform(0.18, 0.32)
            cv, cf = cone(p, tip, rng.uniform(0.004, 0.008), 0.0003, 6); A.append((cv, cf, 1))
        self.obj('ex_geode', A, [rim, amy], face, u, z)
        bpy = kit.bpy; ld = bpy.data.lights.new('ex_geode_glow', 'POINT'); ld.energy = 0.25 * light / 3.0; ld.color = (0.75, 0.5, 1.0); ld.shadow_soft_size = 0.02
        lo = bpy.data.objects.new('ex_geode_glow', ld); kit.coll.objects.link(lo); lo.location = tuple(self.faces[face].world(u, z, 0.02)); lo.visible_camera = False
        self.spot(face, u, z, 3.0 * light / 3.0, out=0.5, up=0.3, size=32, name='ex_spot_geode')
        self.items['geode'] = (face, u, z)


# =============================================================================================== living things
def _path(P, n=200):
    C = cw.catmull(P, n); seg = np.linalg.norm(np.diff(C, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); return C, s

def _at(C, s, d):
    d = float(np.clip(d, 0, s[-1])); i = int(np.clip(np.searchsorted(s, d) - 1, 0, len(C) - 2)); u = (d - s[i]) / max(1e-9, s[i + 1] - s[i])
    p = C[i] + (C[i + 1] - C[i]) * u; tng = C[i + 1] - C[i]; return p, math.atan2(tng[1], tng[0])

def _ground(land, x, y): return float(land.height(np.array([x]), np.array([y]))[0])

def deer(kit, land, x, y, yaw, lift_at=5.0, lower_at=9.5, name='ex_deer', scale=1.0):
    """A roe deer grazing, lifting its head at lift_at (ears flick, looks around), lowering it again at lower_at."""
    coat = mat(kit, 'ex_deercoat', (0.56, 0.34, 0.18), 0.75, noise_amt=0.12); white = mat(kit, 'ex_white', (0.92, 0.90, 0.86), 0.8)
    dark = mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3)
    root = empty(kit, name); root.location = (x, y, _ground(land, x, y) - 0.002); root.rotation_euler = (0, 0, yaw); root.scale = (scale,) * 3
    hip = 0.050
    bv, bf = ell((0, 0, hip + 0.012), (0.038, 0.0155, 0.019), 2, 0.04, 3)
    body = part(kit, name + '_body', [(bv, bf, 0), (*ell((-0.035, 0, hip + 0.018), (0.008, 0.013, 0.013)), 1),
                                      (*ell((0.026, 0, hip + 0.013), (0.016, 0.0135, 0.017)), 0)], [coat, white], root)
    legs = []
    for k, (lx, ly) in enumerate(((0.026, -0.008), (0.026, 0.008), (-0.026, -0.008), (-0.026, 0.008))):
        P = [(0, 0, 0), (0.002 if lx > 0 else -0.004, 0, -hip * 0.45), (0, 0, -hip - 0.004)]
        lv, lf = cw._tube(cw.catmull(P, 6), np.linspace(0.0055, 0.0022, 6), 6)
        hv, hf = ell((0.001, 0, -hip - 0.002), (0.003, 0.0024, 0.003))
        legs.append(part(kit, f'{name}_leg{k}', [(lv, lf, 0), (hv, hf, 1)], [coat, dark], root, (lx, ly, hip + 0.004)))
    neck_piv = (0.032, 0, hip + 0.024)
    nv, nf = cw._tube(cw.catmull([(0, 0, 0), (0.016, 0, 0.018), (0.028, 0, 0.034)], 7), np.linspace(0.0095, 0.006, 7), 8)
    head = [(nv, nf, 0), (*ell((0.036, 0, 0.038), (0.012, 0.0072, 0.0082), 2), 0), (*ell((0.049, 0, 0.034), (0.006, 0.0048, 0.005)), 0),
            (*ell((0.055, 0, 0.0335), (0.0028, 0.0034, 0.0028)), 2), (*ell((0.04, -0.0066, 0.041), (0.0016, 0.0012, 0.0016)), 2),
            (*ell((0.04, 0.0066, 0.041), (0.0016, 0.0012, 0.0016)), 2), (*ell((0.046, 0, 0.029), (0.004, 0.0042, 0.002)), 1)]
    neck = part(kit, name + '_neck', head, [coat, white, dark], root, neck_piv)
    ears = []
    for side in (-1, 1):
        ev, ef = ell((0, side * 0.002, 0.009), (0.0035, 0.0014, 0.0085), 2); ears.append(part(kit, f'{name}_ear{side}', [(ev, ef, 0)], [coat], neck, (0.03, side * 0.0055, 0.045)))
    tail = part(kit, name + '_tail', [(*ell((-0.004, 0, 0), (0.005, 0.003, 0.004)), 0)], [white], root, (-0.039, 0, hip + 0.022))
    def pose(t):
        up = ease5((t - lift_at) / 0.9) * (1 - ease5((t - lower_at) / 1.2))
        nib = 0.06 * math.sin(2 * math.pi * 1.7 * t) * (1 - up)
        neck.rotation_euler = (0.0, math.radians(96 * (1 - up) - 6 * up) + nib, math.radians(18 * up * math.sin(2 * math.pi * 0.18 * (t - lift_at)) if up > 0 else 0))
        for k, e in enumerate(ears):
            fl = 0.5 * max(0.0, math.sin(2 * math.pi * 1.4 * t + k)) ** 12
            e.rotation_euler = (((-1) ** k) * (0.5 + fl * 0.8) * (0.6 + 0.4 * up), 0.0, 0.0)
        tail.rotation_euler = (0.0, -0.3 * max(0.0, math.sin(2 * math.pi * 0.7 * t)) ** 6, 0.0)
        body.rotation_euler = (0.0, 0.02 * (1 - up), 0.0)
        legs[0].rotation_euler = (0.0, -0.10 * (1 - up), 0.0); legs[1].rotation_euler = (0.0, -0.06 * (1 - up), 0.0)
    kit.on_frame(pose); pose(0.0); return root

def rabbit(kit, land, path, t0=0.0, period=1.25, hop=0.32, stride=0.055, name='ex_rabbit', color=(0.52, 0.42, 0.32), keep=None):
    """A rabbit hopping along a path (list of (x, y)): hop, sit and sniff, hop. Feet on the ground between hops."""
    fur = mat(kit, name + '_fur', color, 0.8, noise_amt=0.15); white = mat(kit, 'ex_white', (0.92, 0.90, 0.86), 0.8); dark = mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3)
    pink = mat(kit, 'ex_pink', (0.92, 0.56, 0.58), 0.5, sss=0.2)
    root = empty(kit, name)
    bv, bf = ell((0, 0, 0.016), (0.017, 0.011, 0.0125), 2, 0.05, 4)
    pieces = [(bv, bf, 0), (*ell((-0.008, 0, 0.012), (0.012, 0.0125, 0.012)), 0), (*ell((-0.019, 0, 0.017), (0.0045, 0.0045, 0.0045)), 1),
              (*ell((0.008, 0, 0.004), (0.006, 0.006, 0.004)), 0), (*ell((-0.012, -0.007, 0.004), (0.011, 0.004, 0.004)), 0),
              (*ell((-0.012, 0.007, 0.004), (0.011, 0.004, 0.004)), 0)]
    body = part(kit, name + '_body', pieces, [fur, white], root)
    hp = [(*ell((0.008, 0, 0.004), (0.0088, 0.0075, 0.008)), 0), (*ell((0.0165, 0, 0.002), (0.0025, 0.002, 0.002)), 2),
          (*ell((0.012, -0.0055, 0.0065), (0.0013, 0.0011, 0.0013)), 2), (*ell((0.012, 0.0055, 0.0065), (0.0013, 0.0011, 0.0013)), 2)]
    head = part(kit, name + '_head', hp, [fur, white, dark], body, (0.012, 0, 0.022))
    ears = []
    for side in (-1, 1):
        ev, ef = ell((0, 0, 0.011), (0.0035, 0.0012, 0.012)); iv, if_ = ell((0, -0.0004 * side, 0.011), (0.0022, 0.0008, 0.009))
        ears.append(part(kit, f'{name}_ear{side}', [(ev, ef, 0), (iv, if_, 1)], [fur, pink], head, (0.002, side * 0.0035, 0.008)))
    C, s = _path(path)
    def pose(t):
        tt = t + t0; n = math.floor(tt / period); f = tt / period - n
        prog = ease((f - (1 - hop / period * 1.0)) / (hop / period)) if f > 1 - hop / period else 0.0
        d = ((n + prog) * stride) % max(1e-6, s[-1] * 2)
        if d > s[-1]: d = 2 * s[-1] - d; back = True
        else: back = False
        p, ang = _at(C, s, d)
        if back: ang += math.pi
        z = _ground(land, p[0], p[1]) - 0.001 + 0.024 * math.sin(math.pi * prog)
        root.location = (p[0], p[1], z); root.rotation_euler = (0, 0, ang)
        body.rotation_euler = (0.0, -0.35 * math.sin(math.pi * prog) * (1 if prog < 0.5 else -0.6), 0.0)
        sniff = 0.08 * math.sin(2 * math.pi * 6 * tt) * (1 - math.sin(math.pi * prog))
        head.rotation_euler = (0.0, 0.1 + sniff * 0.3, 0.25 * math.sin(2 * math.pi * 0.3 * tt + 1.0))
        for k, e in enumerate(ears): e.rotation_euler = (((-1) ** k) * 0.18, 0.25 + 0.5 * math.sin(math.pi * prog), 0.0)
    kit.on_frame(pose); pose(0.0); return root

def fox(kit, land, path, speed=0.055, t0=0.0, name='ex_fox'):
    """A red fox trotting along a path; legs swing in diagonal pairs, the bushy tail floats behind."""
    red = mat(kit, 'ex_foxred', (0.86, 0.38, 0.10), 0.75, noise_amt=0.1); white = mat(kit, 'ex_white', (0.92, 0.90, 0.86), 0.8)
    dark = mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3); sock = mat(kit, 'ex_foxsock', (0.12, 0.08, 0.06), 0.7)
    root = empty(kit, name); hip = 0.028
    bv, bf = ell((0, 0, hip + 0.010), (0.033, 0.0115, 0.0125), 2, 0.04, 5)
    body = part(kit, name + '_body', [(bv, bf, 0), (*ell((0.024, 0, hip + 0.006), (0.012, 0.010, 0.012)), 1)], [red, white], root)
    legs = []
    for k, (lx, ly) in enumerate(((0.022, -0.006), (0.022, 0.006), (-0.022, -0.006), (-0.022, 0.006))):
        lv, lf = cw._tube([(0, 0, 0), (0, 0, -hip * 0.5), (0, 0, -hip - 0.002)], [0.0042, 0.003, 0.0024], 6)
        legs.append(part(kit, f'{name}_leg{k}', [(lv, lf, 0)], [sock], root, (lx, ly, hip + 0.004)))
    hp = [(*ell((0.012, 0, 0.004), (0.011, 0.0085, 0.009)), 0), (*cone((0.016, 0, 0.0015), (0.034, 0, -0.001), 0.0055, 0.0012, 8), 0),
          (*ell((0.034, 0, -0.001), (0.0018, 0.0018, 0.0018)), 2), (*ell((0.019, 0, -0.003), (0.008, 0.007, 0.004)), 1),
          (*cone((0.008, -0.005, 0.009), (0.006, -0.0065, 0.024), 0.0042, 0.0005, 6), 0), (*cone((0.008, 0.005, 0.009), (0.006, 0.0065, 0.024), 0.0042, 0.0005, 6), 0),
          (*ell((0.02, -0.0058, 0.0065), (0.0013, 0.001, 0.0013)), 2), (*ell((0.02, 0.0058, 0.0065), (0.0013, 0.001, 0.0013)), 2)]
    head = part(kit, name + '_head', hp, [red, white, dark], root, (0.034, 0, hip + 0.017))
    tp = cw.catmull([(0, 0, 0), (-0.02, 0, -0.006), (-0.04, 0, -0.004), (-0.055, 0, 0.002)], 9)
    tv, tf = cw._tube(tp, np.array([0.004, 0.008, 0.010, 0.0105, 0.0105, 0.0095, 0.008, 0.0055, 0.0015]), 8)
    wv, wf = ell(tp[-2], (0.007, 0.0065, 0.0065))
    tail = part(kit, name + '_tail', [(tv, tf, 0), (wv, wf, 1)], [red, white], root, (-0.032, 0, hip + 0.014))
    C, s = _path(path); freq = speed / 0.03
    def pose(t):
        d = ((t + t0) * speed) % (2 * s[-1]); back = d > s[-1]
        if back: d = 2 * s[-1] - d
        p, ang = _at(C, s, d); ang += math.pi if back else 0.0
        ph = 2 * math.pi * freq * (t + t0)
        root.location = (p[0], p[1], _ground(land, p[0], p[1]) - 0.0015 + 0.0016 * abs(math.sin(ph))); root.rotation_euler = (0, 0, ang)
        for k, lg in enumerate(legs):
            sgn = 1 if k in (0, 3) else -1; lg.rotation_euler = (0.0, 0.45 * sgn * math.sin(ph), 0.0)
        head.rotation_euler = (0.0, 0.05 * math.sin(2 * ph), 0.2 * math.sin(2 * math.pi * 0.15 * (t + t0)))
        tail.rotation_euler = (0.0, -0.1 + 0.06 * math.sin(ph), 0.15 * math.sin(ph * 0.5))
    kit.on_frame(pose); pose(0.0); return root

def heron(kit, land, x, y, yaw, strike_at=7.2, name='ex_heron'):
    """A grey heron standing in the shallows; it turns its head and, once, strikes at the water."""
    grey = mat(kit, 'ex_herongrey', (0.56, 0.60, 0.64), 0.7); white = mat(kit, 'ex_white', (0.92, 0.90, 0.86), 0.8)
    dark = mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3); beak = mat(kit, 'ex_beak', (0.92, 0.70, 0.22), 0.4)
    gz = _ground(land, x, y); lv_ = land.level if land.level is not None else gz
    root = empty(kit, name); root.location = (x, y, gz - 0.003); root.rotation_euler = (0, 0, yaw)
    hip = 0.07
    lp = []
    for side in (-1, 1):
        v, f = cw._tube([(0.002, side * 0.004, hip), (0.0, side * 0.004, hip * 0.5), (0.0, side * 0.004, 0.0)], [0.0018, 0.0016, 0.0015], 5); lp.append((v, f, 2))
        for k in (-1, 0, 1):
            v, f = cw._tube([(0, side * 0.004, 0.001), (0.012 * math.cos(k * 0.5), side * 0.004 + 0.012 * math.sin(k * 0.5), 0.001)], [0.001, 0.0006], 4); lp.append((v, f, 2))
    bv, bf = ell((0.0, 0, hip + 0.014), (0.026, 0.012, 0.014), 2); bv = rot_pts(bv, 'y', math.radians(25), (0, 0, hip + 0.014))
    wv, wf = ell((-0.004, 0, hip + 0.017), (0.024, 0.0128, 0.011), 2); wv = rot_pts(wv, 'y', math.radians(25), (0, 0, hip + 0.014))
    tv, tf = cone((-0.02, 0, hip + 0.004), (-0.034, 0, hip - 0.004), 0.008, 0.001, 6)
    body = part(kit, name + '_body', [(bv, bf, 1), (wv, wf, 0), (tv, tf, 0)] + lp, [grey, white, dark], root)
    neck_piv = (0.018, 0, hip + 0.024)
    NP = cw.catmull([(0, 0, 0), (0.006, 0, 0.012), (-0.002, 0, 0.026), (0.006, 0, 0.038)], 10)
    nv, nf = cw._tube(NP, np.linspace(0.0055, 0.0035, 10), 7)
    hd = [(nv, nf, 1), (*ell((0.010, 0, 0.040), (0.008, 0.0048, 0.0055)), 1), (*cone((0.016, 0, 0.039), (0.044, 0, 0.036), 0.0028, 0.0002, 6), 2),
          (*cone((0.004, 0, 0.043), (-0.014, 0, 0.044), 0.0012, 0.0003, 4), 3), (*ell((0.012, -0.0045, 0.0415), (0.0012, 0.0008, 0.0012)), 3),
          (*ell((0.012, 0.0045, 0.0415), (0.0012, 0.0008, 0.0012)), 3)]
    neck = part(kit, name + '_neck', hd, [grey, white, beak, dark], body, neck_piv)
    def pose(t):
        u = (t - strike_at) / 0.7; st = math.sin(math.pi * min(1, max(0, u))) if 0 < u < 1 else 0.0
        neck.rotation_euler = (0.0, math.radians(75 * st), math.radians(25 * math.sin(2 * math.pi * 0.12 * t)) * (1 - st))
        body.rotation_euler = (0.0, math.radians(10 * st), 0.0)
    kit.on_frame(pose); pose(0.0)
    ripples(kit, [(lambda t, x=x, y=y: (x, y))], lv_, 0.09, rate=0.6, name=name + '_rip')
    return root

def ripples(kit, where, level, size=0.08, rate=0.8, rings=3, name='ex_ripples'):
    """Expanding ring ripples on the water around moving points: where = [fn(t) -> (x, y)]."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name + '_mat'); g = G(m.node_tree, kit); tc = g.node('ShaderNodeTexCoord'); tv = time_value(kit, g)
    r = g.vmath('LENGTH', g.vmath('MULTIPLY', tc.outputs['Object'], (1, 1, 0))); rn = g.math('DIVIDE', r, size)
    ph = g.math('FRACT', g.math('SUBTRACT', g.math('MULTIPLY', rn, rings), g.math('MULTIPLY', tv, rate)))
    ring = g.math('POWER', g.math('SUBTRACT', 1.0, g.math('MULTIPLY', g.math('ABSOLUTE', g.math('SUBTRACT', ph, 0.5)), 2.0), clamp=True), 6.0)
    fade = g.math('SUBTRACT', 1.0, rn, clamp=True); a = g.math('MULTIPLY', g.math('MULTIPLY', ring, fade), 0.75)
    gl = g.node('ShaderNodeBsdfGlossy', ins={'Color': (1, 1, 1), 'Roughness': 0.05})
    em = g.node('ShaderNodeEmission', ins={'Color': (1.0, 0.85, 0.7), 'Strength': 0.25}); ad = g.node('ShaderNodeAddShader'); g.link(gl, ad.inputs[0]); g.link(em, ad.inputs[1])
    tr = g.node('ShaderNodeBsdfTransparent'); mx = g.node('ShaderNodeMixShader'); g.link(a, mx.inputs[0]); g.link(tr, mx.inputs[1]); g.link(ad, mx.inputs[2]); cw._finish(g, mx)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    obs = []
    for k, fn in enumerate(where):
        V = [(-size, -size, 0), (size, -size, 0), (size, size, 0), (-size, size, 0)]
        ob = cw.mk_mesh(bpy, f'{name}{k}', V, [(0, 1, 2, 3)], [m], None, False, kit.coll); ob.visible_shadow = False
        def mv(t, ob=ob, fn=fn):
            x, y = fn(t); ob.location = (x, y, level + 0.0012)
        kit.on_frame(mv); mv(0.0); obs.append(ob)
    return obs

def ducks(kit, land, path, n=3, speed=0.03, name='ex_duck'):
    """Mallards paddling down the river in a loose line, bobbing, each with its ring ripples."""
    brown = mat(kit, 'ex_duckbrown', (0.48, 0.38, 0.28), 0.6, noise_amt=0.15); green = mat_pbr(kit, 'ex_duckgreen', (0.06, 0.30, 0.16), 0.3, film=380.0)
    bill = mat(kit, 'ex_duckbill', (0.96, 0.76, 0.18), 0.4); white = mat(kit, 'ex_white', (0.92, 0.90, 0.86), 0.8); dark = mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3)
    C, s = _path(path); lv = land.level; fns = []
    for k in range(n):
        root = empty(kit, f'{name}{k}')
        bv, bf = ell((0, 0, 0.004), (0.017, 0.0095, 0.0075), 2); tv, tf = cone((-0.014, 0, 0.006), (-0.022, 0, 0.011), 0.005, 0.0008, 6)
        hv, hf = ell((0.013, 0, 0.0135), (0.0062, 0.0055, 0.006)); cv, cf = ell((0.009, 0, 0.0085), (0.004, 0.0062, 0.0015))
        bk, bkf = ell((0.0205, 0, 0.0125), (0.0045, 0.0026, 0.0012)); e1, e1f = ell((0.016, -0.0045, 0.0152), (0.0009, 0.0006, 0.0009)); e2, e2f = ell((0.016, 0.0045, 0.0152), (0.0009, 0.0006, 0.0009))
        part(kit, f'{name}{k}_body', [(bv, bf, 0), (tv, tf, 0), (hv, hf, 1), (cv, cf, 3), (bk, bkf, 2), (e1, e1f, 4), (e2, e2f, 4)], [brown, green, bill, white, dark], root)
        off = k * 0.07 + 0.02 * k * k
        def pos(t, off=off, k=k):
            d = (t * speed + off) % s[-1]; p, ang = _at(C, s, d)
            side = 0.04 * math.sin(2 * math.pi * 0.07 * t + k * 2.1); nrm = np.array([-math.sin(ang), math.cos(ang)])
            return p + nrm * side, ang
        def pose(t, root=root, pos=pos, k=k):
            p, ang = pos(t); root.location = (p[0], p[1], lv - 0.0025 + 0.0012 * math.sin(2 * math.pi * 0.9 * t + k))
            root.rotation_euler = (0.03 * math.sin(2 * math.pi * 0.7 * t + k), 0.03 * math.sin(2 * math.pi * 0.9 * t + k), ang)
        kit.on_frame(pose); pose(0.0); fns.append(lambda t, pos=pos: tuple(pos(t)[0]))
    ripples(kit, fns, lv, 0.06, rate=0.9, name=name + '_rip')

def fish(kit, land, center, n=5, rx=0.24, ry=0.07, depth=(0.05, 0.16), name='ex_fish'):
    """Fish swimming in loops in the river near the cut face (visible through the glass), tails beating."""
    cols = [(0.82, 0.48, 0.16), (0.55, 0.62, 0.50), (0.70, 0.70, 0.66), (0.90, 0.60, 0.20), (0.48, 0.56, 0.46)]
    rng = np.random.default_rng(51); lv = land.level
    for k in range(n):
        m = mat_pbr(kit, f'ex_fish{k}', cols[k % len(cols)], 0.3, metallic=0.3, film=300.0 if k % 2 else 0.0)
        fin = mat(kit, f'ex_fin{k}', tuple(c * 0.8 for c in cols[k % len(cols)]), 0.5, sss=0.3); eye = mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3)
        L = rng.uniform(0.022, 0.034); root = empty(kit, f'{name}{k}')
        bv, bf = ell((0, 0, 0), (L * 0.5, L * 0.12, L * 0.17), 2)
        body = part(kit, f'{name}{k}_body', [(bv, bf, 0), (*ell((L * 0.32, -L * 0.1, L * 0.04), (L * 0.03, L * 0.02, L * 0.03)), 2),
                                            (*ell((L * 0.32, L * 0.1, L * 0.04), (L * 0.03, L * 0.02, L * 0.03)), 2),
                                            ([(L * 0.05, 0, L * 0.14), (-L * 0.15, 0, L * 0.14), (-L * 0.05, 0, L * 0.26)], [(0, 1, 2)], 1)], [m, fin, eye], root)
        tl = part(kit, f'{name}{k}_tail', [([(0, 0, 0), (-L * 0.32, 0, L * 0.2), (-L * 0.26, 0, 0), (-L * 0.32, 0, -L * 0.2)], [(0, 1, 2), (0, 2, 3)], 0)], [fin], root, (-L * 0.45, 0, 0))
        ph = rng.uniform(0, 6.28); sp = rng.uniform(0.35, 0.55) * (1 if k % 2 else -1); zz = lv - rng.uniform(*depth); sc = rng.uniform(0.75, 1.1)
        cx, cy = center[0] + rng.uniform(-0.06, 0.06), center[1] + rng.uniform(-0.02, 0.03)
        def pose(t, root=root, tl=tl, ph=ph, sp=sp, zz=zz, sc=sc, cx=cx, cy=cy):
            a = ph + sp * t; x = cx + rx * sc * math.cos(a); y = cy + ry * sc * math.sin(a)
            dx = -rx * sc * math.sin(a) * sp; dy = ry * sc * math.cos(a) * sp
            root.location = (x, y, zz + 0.008 * math.sin(1.3 * t + ph)); root.rotation_euler = (0, 0.06 * math.sin(1.3 * t + ph), math.atan2(dy, dx))
            tl.rotation_euler = (0, 0, 0.5 * math.sin(2 * math.pi * 2.6 * t + ph))
        kit.on_frame(pose); pose(0.0)

def fireflies(kit, land, n=26, area=((-1.8, 1.8), (-1.8, 1.8)), z=(0.03, 0.22), seed=61, near=None, name='ex_fireflies'):
    """Fireflies drifting low over the grass and the banks, each blinking on its own rhythm."""
    bpy = kit.bpy; m = cw._new_mat(bpy, name + '_mat'); g = G(m.node_tree, kit); oi = g.node('ShaderNodeObjectInfo'); tv = time_value(kit, g)
    w = g.math('SINE', g.math('ADD', g.math('MULTIPLY', tv, g.math('ADD', 2.0, g.math('MULTIPLY', oi.outputs['Random'], 2.5))), g.math('MULTIPLY', oi.outputs['Random'], 40.0)))
    k = g.math('POWER', g.math('MAXIMUM', w, 0.0), 5.0)
    e = g.node('ShaderNodeEmission', ins={'Color': srgb((0.85, 1.0, 0.35))}); g.put(e, 'Strength', g.math('ADD', g.math('MULTIPLY', k, 60.0), 1.0)); cw._finish(g, e)
    try: m.cycles.emission_sampling = 'NONE'
    except Exception: pass
    rng = np.random.default_rng(seed); V0, F0 = cw._icosphere(1)
    for i in range(n):
        if near is not None:
            c = near[i % len(near)]; x0, y0 = c[0] + rng.normal(0, 0.25), c[1] + rng.normal(0, 0.25)
        else: x0, y0 = rng.uniform(*area[0]), rng.uniform(*area[1])
        ob = cw.mk_mesh(bpy, f'{name}{i}', V0 * 0.0028, F0, [m], None, True, kit.coll); ob.visible_shadow = False
        ph = rng.uniform(0, 6.28, 3); zz = rng.uniform(*z)
        def pose(t, ob=ob, x0=x0, y0=y0, ph=ph, zz=zz):
            x = x0 + 0.06 * math.sin(0.5 * t + ph[0]) + 0.025 * math.sin(1.3 * t + ph[1]); y = y0 + 0.06 * math.cos(0.4 * t + ph[1]) + 0.02 * math.sin(1.7 * t + ph[2])
            ob.location = (x, y, _ground(land, x, y) + zz + 0.02 * math.sin(0.9 * t + ph[2]))
        kit.on_frame(pose); pose(0.0)

def petals(kit, land, n=40, wind=(0.09, 0.025), box=((-2.0, 2.0), (-2.0, 2.0), (0.02, 0.75)), seed=71, name='ex_petals'):
    """Leaves and petals drifting through the light on the wind, tumbling; each fades in and out at the ends of its path."""
    bpy = kit.bpy; rng = np.random.default_rng(seed)
    mats = [mat(kit, f'{name}_m{k}', c, 0.6, sss=0.3) for k, c in enumerate([(0.95, 0.70, 0.78), (0.92, 0.62, 0.20), (0.82, 0.36, 0.12), (0.98, 0.94, 0.88)])]
    for i in range(n):
        V = [(-0.006, 0, 0), (0, -0.0035, 0.0006), (0.006, 0, 0), (0, 0.0035, 0.0006)]
        ob = cw.mk_mesh(bpy, f'{name}{i}', V, [(0, 1, 2, 3)], [mats[i % 4]], None, True, kit.coll)
        x0, y0, z0 = rng.uniform(*box[0]), rng.uniform(*box[1]), rng.uniform(*box[2]); ph = rng.uniform(0, 6.28, 3); sp = rng.uniform(0.7, 1.3)
        span = (box[0][1] - box[0][0])
        def pose(t, ob=ob, x0=x0, y0=y0, z0=z0, ph=ph, sp=sp):
            x = box[0][0] + ((x0 - box[0][0]) + wind[0] * sp * t) % span; y = y0 + wind[1] * sp * t + 0.05 * math.sin(0.7 * t + ph[0])
            z = z0 + 0.04 * math.sin(0.9 * t + ph[1]) - 0.01 * t
            g_ = _ground(land, min(max(x, -1.99), 1.99), min(max(y, -1.99), 1.99)); z = max(z, g_ + 0.02)
            ob.location = (x, y, z); ob.rotation_euler = (2.3 * t * sp + ph[0], 1.7 * t + ph[1], 0.8 * t + ph[2])
            u = (x - box[0][0]) / span; s_ = min(1.0, min(u, 1 - u) * 12); ob.scale = (s_, s_, s_)
        kit.on_frame(pose); pose(0.0)

def butterflies(kit, land, spots, seed=81, name='ex_bfly'):
    """Butterflies wandering over the flowers, wings beating."""
    bpy = kit.bpy; rng = np.random.default_rng(seed)
    cols = [(0.98, 0.56, 0.12), (0.98, 0.96, 0.90), (0.40, 0.55, 0.95)]
    for i, (cx, cy) in enumerate(spots):
        m = mat(kit, f'{name}_m{i}', cols[i % 3], 0.5, sss=0.25); dark = mat(kit, 'ex_dark', (0.05, 0.04, 0.04), 0.3)
        root = empty(kit, f'{name}{i}')
        part(kit, f'{name}{i}_b', [cw._tube([(-0.005, 0, 0), (0.005, 0, 0)], [0.0012, 0.001], 5) + (0,)], [dark], root)
        wings = []
        for side in (-1, 1):
            V = [(0.001, 0, 0), (0.008, side * 0.010, 0), (0.0, side * 0.013, 0), (-0.006, side * 0.009, 0)]
            wings.append(part(kit, f'{name}{i}_w{side}', [(V, [(0, 1, 2, 3)], 0)], [m], root))
        ph = rng.uniform(0, 6.28, 4)
        def pose(t, root=root, wings=wings, ph=ph, cx=cx, cy=cy):
            x = cx + 0.18 * math.sin(0.35 * t + ph[0]) + 0.05 * math.sin(1.1 * t + ph[1]); y = cy + 0.14 * math.sin(0.27 * t + ph[2])
            dx = 0.18 * 0.35 * math.cos(0.35 * t + ph[0]); dy = 0.14 * 0.27 * math.cos(0.27 * t + ph[2])
            root.location = (x, y, _ground(land, x, y) + 0.07 + 0.03 * math.sin(1.9 * t + ph[3])); root.rotation_euler = (0, 0, math.atan2(dy, dx))
            a = 1.1 * math.sin(2 * math.pi * 7.0 * t + ph[1])
            for k, w in enumerate(wings): w.rotation_euler = ((-1) ** k * (0.35 + 0.8 * max(0.0, a)), 0, 0)
        kit.on_frame(pose); pose(0.0)
