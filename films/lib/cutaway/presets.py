"""Presets of the Cutaway line: everything a spec can name, as data (pure Python, no Blender).

A spec never carries Blender code: it names a block size, a strata preset, a water shape, a season, a time of day,
an amount of vegetation, props from the kit, easter eggs by depth, animals, and a camera preset per shot. This file
is the menu; films/lib/cutaway/SPEC.md documents it, the validator checks against it, the engine builds from it.
Distances are metres on a 4 m block (the kit's default); presets scale with the block size.
"""

# ------------------------------------------------------------------ the block
SIZES = {            # (sx, sy, depth)
    'small': (3.0, 3.0, 1.3),
    'standard': (4.0, 4.0, 1.6),
    'deep': (4.0, 4.0, 2.1),
}
TERRAIN = {          # rolling(amp, freq, base)
    'flat': (0.025, 0.30, 0.02),
    'rolling': (0.10, 0.32, 0.03),
    'hills': (0.17, 0.42, 0.04),
}
# Deep time: recent soil at the top, a Roman loam, fossil limestone, ancient bedrock (the cinematic film's layers).
STRATA_TIME = [('topsoil', 0.07, (0.26, 0.17, 0.10), 0.05), ('sand', 0.10, (0.90, 0.74, 0.46), 0.08), ('clay', 0.14, (0.78, 0.44, 0.28), 0.03),
               ('loam', 0.16, (0.56, 0.36, 0.22), 0.20), ('gravel', 0.10, (0.62, 0.58, 0.54), 0.9), ('ochre', 0.05, (0.84, 0.60, 0.28), 0.12),
               ('limestone', 0.68, (0.88, 0.84, 0.74), 0.05), ('bedrock', 1.0, (0.24, 0.25, 0.30), 0.35)]
STRATA_NAMES = ['time', 'meadow', 'red', 'limestone', 'lagoon', 'mud']


def strata(name):
    if name == 'time': return STRATA_TIME
    import cutaway as cw
    return cw.STRATA[name]


SEASONS = ['summer', 'spring', 'autumn', 'winter']

# Water shapes on a 4 m block (scaled with the block). Each one reaches a camera-facing cut face (-Y or +X), so the
# water shows as glass in the section.
WATER = {
    'none': None,
    'river': {'type': 'river', 'path': [(-0.7, 2.6), (-0.55, 1.4), (0.25, 0.6), (0.05, -0.4), (0.35, -1.3), (0.4, -2.6)], 'width': 0.7, 'depth': 0.34, 'level': -0.05, 'shelf': 0.22},
    'stream': {'type': 'river', 'path': [(-2.6, 0.9), (-1.2, 0.6), (-0.2, -0.3), (0.5, -1.2), (0.7, -2.6)], 'width': 0.42, 'depth': 0.24, 'level': -0.04, 'shelf': 0.18},
    'pond': {'type': 'pond', 'center': (0.55, -1.6), 'radius': (0.85, 0.6), 'depth': 0.38, 'level': -0.05, 'shelf': 0.3},
    'lagoon': {'type': 'lagoon', 'center': (1.35, -1.35), 'radius': 1.75, 'depth': 0.42, 'level': -0.04, 'shelf': 0.45},
}
WATER_ANIMALS = {'ducks', 'fish', 'heron'}
RIVER_PROPS = {'mill', 'bridge'}

# ------------------------------------------------------------------ light
TIMES = ['day', 'golden', 'dusk', 'overcast', 'studio']
# what the time of day costs on a runner, relative to plain day light (lights, sky dome, shafts)
TIME_COST = {'studio': 0.75, 'day': 1.0, 'overcast': 1.0, 'golden': 1.5, 'dusk': 1.45}

# ------------------------------------------------------------------ props (kit), eggs (cinematic extras), animals
PROPS = ['village', 'mill', 'bridge', 'lamps', 'pipes', 'piles']

# Easter eggs in the cut faces, placed by depth below the turf. class: recent near the top, deep time at the bottom.
# depth: default metres below the top (on the 'time' strata); size: half extent along the face (u) and up (z) for overlap checks.
EGGS = {
    'mole':      {'cls': 'recent', 'depth': 0.115, 'size': (0.36, 0.07), 'center_du': 0.30, 'what': 'a mole digging its tunnel under the turf, its nest at the end'},
    'hedgehog':  {'cls': 'recent', 'depth': 0.17, 'size': (0.08, 0.06), 'what': 'a hedgehog asleep in a leaf-lined burrow, breathing'},
    'chest':     {'cls': 'recent', 'depth': 0.31, 'size': (0.10, 0.08), 'what': 'a pirate chest ajar, gold coins spilling into the soil'},
    'amphora':   {'cls': 'recent', 'depth': 0.46, 'size': (0.13, 0.08), 'what': 'a Roman amphora with shards and bronze coins'},
    'ammonite':  {'cls': 'old', 'depth': 0.84, 'size': (0.07, 0.07), 'what': 'an ammonite spiral with a nacre sheen'},
    'dino':      {'cls': 'old', 'depth': 0.98, 'size': (0.50, 0.33), 'center_du': -0.12, 'center_dz': 0.06, 'what': 'a T. rex skeleton in the fossil limestone (macro target: its skull)'},
    'trilobite': {'cls': 'old', 'depth': 1.235, 'size': (0.10, 0.06), 'what': 'a trilobite at the base of the limestone'},
    'geode':     {'cls': 'deep', 'depth': 1.10, 'size': (0.10, 0.09), 'what': 'a geode cracked open, glowing amethyst points'},
    'gold':      {'cls': 'deep', 'depth': 1.42, 'size': (None, 0.05), 'what': 'a gold-bearing quartz vein across the bedrock, nuggets glinting'},
    'well':      {'cls': 'recent', 'depth': 0.78, 'size': (0.08, None), 'what': 'an ancient stone well cut in half, a bucket swaying on its rope'},
}
EGG_ORDER = {'recent': 0, 'old': 1, 'deep': 2}
FACES = ['-Y', '+X']
MAX_EGGS_PER_SET = 12        # each egg has its own museum light; more than this slows every frame of that set

ANIMALS = {
    'deer': 'a roe deer grazing, lifting its head to look around',
    'fawn': 'a fawn (a small deer)',
    'rabbit': 'a rabbit hopping, sitting, sniffing',
    'fox': 'a red fox trotting across the meadow',
    'heron': 'a heron in the shallows; it strikes at the water once (needs water)',
    'ducks': 'mallards paddling with ring ripples (needs water)',
    'fish': 'fish swimming behind the glass of the cut face (needs water)',
    'birds': 'birds gliding in loose circles above the block',
    'fireflies': 'fireflies blinking low over the banks (best at dusk)',
    'butterflies': 'butterflies over the flowers',
    'petals': 'petals and leaves drifting on the wind',
}

# ------------------------------------------------------------------ camera presets
CAMERAS = {
    'map': 'straight down on the whole block, a slow drift and turn: where we are (understanding)',
    'orbit': 'high three-quarter on the whole block, a slow eased orbit: the world, wide',
    'push': 'high three-quarter, a slow push toward a target (an egg, a point) while it frames it: attention',
    'pull': 'the reverse of push: from close to the whole block, the consequence (good for an ending)',
    'ground': 'low at the corner of the cut, eye on the grass, looking along the -Y face into the light: arrival, scale',
    'crane': 'a vertical crane down a cut face from the treetops to a depth or an egg: the reveal, layers read as time',
    'macro': 'close on one egg, a slow push, shallow focus: the payoff',
    'hero': 'low three-quarter, the sun behind the block, a slow arc: the closing image',
}
CLOSE = {'crane', 'macro'}

# Label slots (centre of the label, pixels of the delivery frame, origin at the centre, y up), per format.
SLOTS = {
    '16:9': {'upper-left': (-560, 330), 'upper-right': (560, 330), 'lower-left': (-560, -330), 'lower-right': (560, -330),
             'left': (-620, 60), 'right': (620, 60), 'top': (0, 410), 'bottom': (0, -420)},
    '9:16': {'upper-left': (-230, 620), 'upper-right': (230, 620), 'lower-left': (-230, -600), 'lower-right': (230, -600),
             'left': (-250, 250), 'right': (250, 250), 'top': (0, 760), 'bottom': (0, -760)},
}
REF = {'16:9': (1920, 1080), '9:16': (1080, 1920)}
RENDER = {'16:9': (1280, 720), '9:16': (720, 1280)}
