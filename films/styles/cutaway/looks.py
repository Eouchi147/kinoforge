"""The four Cutaway board looks, each a build(bpy, kit, aspect) -> dict(land, cam, look, exposure). Used by board.py and test/blender.py."""
import math
import numpy as np
import cutaway as cw

RIVER = [(-0.9, 2.5), (-0.5, 1.2), (0.35, 0.45), (0.1, -0.6), (0.55, -1.5), (0.75, -2.6)]

def look_a(bpy, kit, aspect='16:9'):
    """A, Studio block: white seamless, a river with lily pads splitting a grassy block, trees, boulders."""
    land = cw.block(kit, size=(4.0, 4.0), depth=1.25, strata=cw.STRATA['meadow'], seed=4,
                    top=cw.rolling(amp=0.10, freq=0.32, seed=4, base=0.02),
                    water=[cw.river(RIVER, width=0.72, depth=0.34, level=-0.05, shelf=0.22)],
                    trees=16, tree_kinds=('round', 'round', 'cone'), boulders=14, flowers=0.6, lilies=22, reeds=0.5)
    cw.studio(kit, color=(0.94, 0.935, 0.925), key_az=-150, key_el=50, key=3.4, angle=14, fill=0.95, land=land, shadows=0.22)
    cw.birds(kit, 3, center=(0.3, 0.5), radius=2.0, height=1.2)
    cam = cw.camera(kit, land, aspect, az=-42, el=33 if aspect == '16:9' else 38, lens=60, fill=0.86 if aspect == '16:9' else 0.90)
    return {'land': land, 'cam': cam, 'look': 'AgX - Base Contrast', 'exposure': 0.25}

def look_b(bpy, kit, aspect='16:9'):
    """B, Floating island: open sky and mist, a pond with a glass front, trees, stones falling away below, birds."""
    land = cw.block(kit, size=(3.6, 3.6), depth=1.1, strata=cw.STRATA['red'], seed=7,
                    top=cw.rolling(amp=0.16, freq=0.4, seed=7, base=0.04, tilt=(0.0, 0.02)),
                    water=[cw.pond((0.25, -1.45), (0.95, 0.8), depth=0.42, level=-0.04, shelf=0.35)],
                    trees=5, tree_kinds=('round', 'tall', 'round'), boulders=12, flowers=0.8, grass=1.15, grass_height=1.3, reeds=0.6)
    cw.sky(kit, land=land, sun_az=-135, sun_el=42, sun=3.2)
    cw.falling_stones(kit, land, 16)
    cw.birds(kit, 4, center=(0.5, 0.8), radius=2.2, height=1.3)
    cam = cw.camera(kit, land, aspect, az=-48, el=24 if aspect == '16:9' else 30, lens=55, fill=0.70 if aspect == '16:9' else 0.80,
                    target=(0, 0, -0.75))
    return {'land': land, 'cam': cam, 'look': 'AgX - Base Contrast', 'exposure': 0.15}

def look_c(bpy, kit, aspect='16:9'):
    """C, Lagoon cut: a shore of pale cracked rock, a clear lagoon open on two faces, corals, weed and stones on the floor."""
    def lag(x, y):
        q = np.hypot((x - 0.75) / 2.1, (y + 0.75) / 2.0); return (q - 1) * 1.6 + 0.12 * cw.fbm(x, y, 5, 3, 1.2)
    def zones(x, y, h):
        r = np.hypot(x + 1.3, y - 1.3); return {'grass': cw.smooth(1.75, 1.3, r)}
    land = cw.block(kit, size=(4.0, 4.0), depth=1.2, strata=cw.STRATA['lagoon'], seed=11,
                    top=cw.rolling(amp=0.05, freq=0.4, seed=11, base=0.05),
                    water=[cw.basin(lag, depth=0.5, level=-0.03, shelf=0.55)], shore_rock=1.0, zones=zones,
                    trees=0, boulders=6, flowers=0.2, corals=46, water_tint=(0.26, 0.82, 0.80), water_density=2.0, grass_height=1.3)
    cw.studio(kit, color=(0.90, 0.89, 0.87), key_az=-140, key_el=58, key=3.6, angle=12, fill=1.0, land=land)
    cam = cw.camera(kit, land, aspect, az=-45, el=30 if aspect == '16:9' else 36, lens=60, fill=0.86 if aspect == '16:9' else 0.90)
    return {'land': land, 'cam': cam, 'look': 'AgX - Base Contrast', 'exposure': 0.3}

def look_d(bpy, kit, aspect='16:9'):
    """D, Mill at dusk: the river block at dusk with a little village, a turning watermill, a bridge and lamps."""
    houses = [(-1.15, -0.55, 0.3), (-1.45, 0.25, -0.2), (-0.95, 0.85, 0.5), (1.25, 0.9, 1.2), (1.45, 0.1, 1.6), (-1.6, -1.25, 0.0)]
    mill_at = (0.74, -0.80)
    clear = [(x, y, 0.2) for x, y, _ in houses] + [(mill_at[0], mill_at[1], 0.24)]
    def zones(x, y, h):
        # a dirt lane from the bridge through the village
        P = np.array([(-1.8, -1.6), (-1.2, -0.9), (-0.7, -0.15), (-0.25, 0.25), (0.75, 0.3), (1.6, 0.45)]); d = np.full(np.shape(x), 9.0)
        for a, b in zip(P[:-1], P[1:]):
            ab = b - a; t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / (ab @ ab), 0, 1); d = np.minimum(d, np.hypot(x - a[0] - t * ab[0], y - a[1] - t * ab[1]))
        return {'path': cw.smooth(0.06, 0.03, d + 0.01 * cw.fbm(x, y, 3, 2, 8))}
    land = cw.block(kit, size=(4.0, 4.0), depth=1.25, strata=cw.STRATA['meadow'], seed=4,
                    top=cw.rolling(amp=0.10, freq=0.32, seed=4, base=0.02),
                    water=[cw.river(RIVER, width=0.72, depth=0.34, level=-0.05, shelf=0.22)], zones=zones, keep_clear=clear,
                    trees=11, tree_kinds=('round', 'cone', 'cone'), boulders=10, flowers=0.3, lilies=10, reeds=0.5,
                    water_density=2.8, water_glow=0.006)
    cw.dusk(kit, land=land, sun_az=-165, sun_el=12, sun=3.0)
    for k, (x, y, yaw) in enumerate(houses):
        cw.house(kit, land, x, y, w=0.21, d=0.15, h=0.13, roof=0.09, yaw=yaw, lit=1.5, roof_col=[(0.55, 0.22, 0.14), (0.30, 0.30, 0.34), (0.48, 0.28, 0.18)][k % 3], name=f'cw_house{k}')
    cw.mill(kit, land, mill_at[0], mill_at[1], yaw=math.pi, lit=1.5, wheel_r=0.11, wheel_off=0.21)
    cw.bridge(kit, land, (-0.25, 0.25), (0.75, 0.30), width=0.09, arch=0.06)
    for k, (x, y) in enumerate([(-0.85, -0.35), (-0.35, 0.12), (0.88, 0.18), (-1.3, -1.0)]):
        cw.lamp(kit, land, x, y, name=f'cw_lamp{k}')
    cw.birds(kit, 3, center=(0.4, 0.6), radius=2.0, height=1.1)
    cam = cw.camera(kit, land, aspect, az=-40, el=31 if aspect == '16:9' else 37, lens=60, fill=0.86 if aspect == '16:9' else 0.90)
    return {'land': land, 'cam': cam, 'look': 'AgX - Medium High Contrast', 'exposure': 0.9}

LOOKS = {'A': look_a, 'B': look_b, 'C': look_c, 'D': look_d}
NAMES = {'A': 'studio-block', 'B': 'floating-island', 'C': 'lagoon-cut', 'D': 'mill-at-dusk'}
