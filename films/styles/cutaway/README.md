# Cutaway (KINOFORGE style)

A block of land cut out of the world: the top is a living landscape, the four sides are a clean cross-section (strata,
pebbles, roots), and water is a clear glassy volume you can see into. Free: Blender `bpy` 5.2.2, Cycles CPU, everything
procedural (no downloaded assets, no paid calls).

| File | What it is |
| --- | --- |
| `cutaway.py` | **The kit (library).** Import it from any film: `block()`, water regions, vegetation, props, backgrounds, cameras, time |
| `looks.py` | The four board looks (A Studio block, B Floating island, C Lagoon cut, D Mill at dusk), each a `look_x(bpy, kit, aspect)` |
| `scene.py` | Glue for `harness/blender_render.py`: `make(look, duration, move, samples)` returns `DURATION, SETTINGS, build, frame` |
| `board.py` | Local still renderer: `python3 films/styles/cutaway/board.py A --aspect 16:9 --w 1920 --samples 96` |
| `board/` | The style board stills (jpg q90) |
| `test/` | Motion test film (8 s, 24 fps, 1280x720, look A, slow eased orbit) for rc-render `films.yml` |
| `stills/A..D/` | One-frame film folders so the board stills can be rendered on free runners (rc-render `stills.yml`) |

## Use it from a film (the API)

```python
import os, sys
sys.path.insert(0, '<repo>/films/styles/cutaway')     # e.g. os.path.join(root, 'films/styles/cutaway')
import cutaway as cw

DURATION = 8.0
SETTINGS = {'samples': 48, 'denoise': True}

def build(bpy, ctx):
    kit  = cw.Kit(bpy, seed=3, loop=DURATION)          # loop: every motion repeats exactly after this many seconds
    land = cw.block(kit, size=(4, 4), depth=1.3, strata=cw.STRATA['meadow'],
                    top=cw.rolling(amp=0.1, freq=0.3, seed=3),
                    water=[cw.river([(-0.9, 2.5), (0.3, 0.4), (0.7, -2.6)], width=0.7, depth=0.34, level=-0.05)],
                    season='summer', trees=12, boulders=12, lilies=20, reeds=0.5)
    cw.studio(kit, land=land)                          # or cw.sky(kit, land=land) / cw.dusk(kit, land=land)
    cam = cw.camera(kit, land, aspect='16:9' if ctx['W'] >= ctx['H'] else '9:16', az=-42, el=33)
    cw.apply_cycles(bpy)
    return {'kit': kit, 'land': land, 'cam': cam}

def frame(bpy, ctx, S, i, t):
    S['kit'].update(t)                                 # wind, water, caustics, birds, mill wheel, falling stones
    S['cam'].orbit(t, deg_per_s=2.0, duration=DURATION)
```

Coordinates: metres, block centred on the origin, top near z = 0, bottom at z = -depth. The camera-facing front faces
are **-Y** (left in frame) and **+X** (right) at the default azimuth (-40 degrees). Water cut open on the faces must reach
those faces (run a river path past the edge, put a pond centre near the edge).

### `cw.block(kit, ...)` returns a `Land`

| Parameter | Meaning (default) |
| --- | --- |
| `size` | `(sx, sy)` in metres, or one number (4 x 4) |
| `depth` | block thickness (1.4) |
| `strata` | list of layers top-down: `(name, thickness_m, sRGB, pebble_density 0..1)`; the last fills the rest. Presets `cw.STRATA`: `meadow`, `red`, `limestone`, `lagoon`, `mud` |
| `top` | height function `h(x, y)` (numpy, vectorised) or a 2D array (rows y, cols x). `cw.rolling(amp, freq, seed, tilt, base)` makes one |
| `water` | list of regions: `cw.river(path, width, depth, level, shelf)`, `cw.pond(center, radius or (rx, ry), depth, level)`, `cw.basin(fn_signed_distance, depth, level)`. One water volume per block at the **first** region's level |
| `season` | `'summer'`, `'spring'`, `'autumn'`, `'winter'` (snow on top, frosted water, bare-ish trees) or a dict overriding `cw.SEASONS` keys |
| `zones(x, y, h)` | returns extra weights `{'rock', 'sand', 'path', 'grass'}` (arrays 0..1): paths, pale rock, beaches |
| `grass`, `grass_height` | density and height multipliers (1, 1) |
| `trees`, `tree_kinds`, `tree_spots` | count and kinds (`round`, `cone`, `tall`), or exact spots `[(x, y, scale, kind)]` |
| `boulders`, `flowers` | boulder count (12), flower amount 0..1 (0.5) |
| `under`, `corals`, `lilies`, `reeds` | underwater stones and weed (True), coral count (0), lily pad count (0), reeds 0..1 (0) |
| `shore_rock` | 0..1 pale cracked rock shelf around the water (lagoon look) |
| `keep_clear` | `[(x, y, r)]` no grass or trees there (for buildings) |
| `sway`, `water_tint`, `water_density` | wind amount, water absorption colour and density |

`Land` fields and methods: `size`, `depth`, `level`, `pal`, `objects` (dict: `top`, `walls`, `water`, `cw_grass`, ...),
`mats`, `height(x, y)`, `field(x, y)` (h, signed distance to water, zone weights, depth below the water),
`scatter(name, protos, pts, yaw, scale, sway, variant, z)` (instance any objects with wind), `cut(obj)` (clip an object
to the block so it ends flush on the cut faces), `place(obj, x, y, dz)` (stand an object on the terrain).

### Props (simple hooks; all clipped or placed on the terrain)

- `cw.pile(kit, land, x, y, length, radius, top)` wooden pile driven down from the surface; on the cut plane it shows its section (Venice).
- `cw.pipe(kit, land, [(x, y, z), ...], radius, color)` a pipe along a 3D path, clipped flush to the faces (drainage, utilities).
- `cw.house(kit, land, x, y, w, d, h, roof, yaw, wall, roof_col, lit)`; `cw.mill(kit, land, x, y, yaw, wheel_r, rpm, lit)` (the wheel turns);
  `cw.bridge(kit, land, a, b, width, arch)`; `cw.lamp(kit, land, x, y)`; `cw.tunnel_mouth(kit, land, x, z, r, face)` (an arched void in a wall).
- Any other mesh: build it, then `land.cut(obj)` and/or `land.place(obj, x, y)`. Animate it with `kit.on_frame(fn)`; `fn(t)` is called by `kit.update(t)`.

### Backgrounds, life, camera

- `cw.studio(kit, color, key_az, key_el, key, angle, fill, land, shadows)` seamless matte floor, soft key sun, fill; `shadows` > 0 adds drifting cloud shadows.
- `cw.sky(kit, top, horizon, sun_az, sun_el, sun, clouds, mist, land)` floating-island sky: gradient, cloud cards, mist layers, cloud shadows.
- `cw.dusk(kit, top, horizon, floor, sun_az, sun_el, sun, land)` dusk studio: blue-to-amber, low warm sun, cool fill.
- `cw.birds(kit, n, center, radius, height)`; `cw.falling_stones(kit, land, n)`; `cw.cloud_shadows(kit, opacity)`.
- `cw.camera(kit, land, aspect='16:9'|'9:16', az, el, lens, fill, target, dist)` returns a `Cam`: `pose(az, el, dist, target)`,
  `orbit(t, deg_per_s, duration)`. Distance is computed so the block fills `fill` of the frame in either aspect.
- `cw.render_settings(bpy, W, H, samples, look, exposure)` for stills; `cw.apply_cycles(bpy)` sets the bounce limits the kit expects.

### Time and loops

All motion is a pure function of `t` through `kit.update(t)`: grass, flowers, reeds, weed and trees sway in a travelling
wind (geometry nodes, looping 4D noise), water ripples and caustics move (looping 4D noise), birds circle and flap,
stones fall, the mill wheel turns. Every motion closes a circle after `kit.loop` seconds, so a render of `[0, loop)` loops
seamlessly (social loops: set `loop` to the clip length). Integer cycles per loop: use `kit.cycles(t, per_second)`.

## How it is built (for whoever extends it)

- **Block**: one top grid mesh (about 2 cm cells) displaced by the height function with rivers and ponds carved by signed
  distance (smooth banks, a shelf, a bed); separate wall and bottom meshes built straight down from the boundary ring, so
  the cut faces are exactly planar and crisp (no boolean). Walls carry attributes `sd` (strata coordinate: depth below the
  local top, flattening with depth, so the top bands follow the terrain and sag under the river) and `dtop`.
- **Strata shader**: colour ramp over `sd` with noise-wobbled band edges, grain and streaks, voronoi pebbles (density per
  layer), random-length roots hanging from the top, a dark band under the turf.
- **Water**: one closed box at the water level, inset 1.5 mm from the faces; the opaque terrain hides it wherever the ground
  is above the level, so it shows only in the river or pond and on the cut faces. Glass IOR 1.33 (transparent to shadow
  rays so the bed stays lit), turquoise volume absorption, ripple bump on the top face only. Caustics are faked in the
  bed shader (two animated voronoi edge layers fading with depth).
- **Vegetation**: prototypes built in code (tufts of tapered curved blades, flowers, lumpy-blob trees, rocks, weed, corals,
  lily pads, reeds), instanced by one geometry-nodes group (`cw_sway`) on point meshes with per-point yaw, scale, variant
  and sway amplitude. Per-instance colour via Object Info Random.

## The board

| Look | File | What it shows |
| --- | --- | --- |
| A Studio block | `board/A-studio-block.jpg`, `board/A-studio-block-vertical.jpg` | white seamless, a river with lily pads splitting a grassy block, cut open as glass on the front face |
| B Floating island | `board/B-floating-island.jpg` | open sky, clouds, mist below, a pond with a glass front, hanging roots, stones falling away, birds |
| C Lagoon cut | `board/C-lagoon-cut.jpg` | raised pale limestone shore with cracks, a clear lagoon open on two faces, corals, weed, stones |
| D Mill at dusk | `board/D-mill-at-dusk.jpg`, `board/D-mill-at-dusk-vertical.jpg` | the river block at dusk: lit cottages, a turning watermill, a bridge, lamps, a lane (storytelling) |

Render the board on free runners (one job per still), then download:

```bash
gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches -f ref=main \
  -f 'inputs[film]=films/styles/cutaway/stills/D' -f 'inputs[frames]=24' -f 'inputs[tag]=cutaway-D' \
  -f 'inputs[w]=1920' -f 'inputs[h]=1080' -f 'inputs[samples]=128' -f "inputs[ref]=$(git rev-parse HEAD)"
bash /home/claude/rc-render/tools/getstills.sh cutaway-D out/
```

Locally (slow on a 2-core box; use for 480 px checks): `python3 films/styles/cutaway/board.py A --w 480 --samples 12`
(`--border x0 x1 y0 y1` renders a crop, `--build-only` just builds).

## Render cost and weak spots

COST_PLACEHOLDER

Weak spots (honest list):
- Trees are lumpy-blob miniatures (trunk, branches, clustered leaf masses). They read as a diorama, not as real trees at close range; no leaf cards.
- Water is one flat volume per block at one level: no waterfalls, no two rivers at different levels, no flow along a slope. The surface is a bump-mapped plane (no real waves).
- Caustics are faked in the bed shader; real refracted caustics are off (too noisy on CPU).
- Grass blades are geometry; very close shots (block filling more than the frame) show the blade count; far shots are cheap.
- Strata are a shader on flat walls: no real pebbles sticking out, no crumbly edge. Roots on the wall are painted lines.
- The limestone shore is cellular plates (can look like paving if the plates are too even).
- Houses, mill, bridge and lamps are simple boxes and tubes; they read at board distance only.
- The underwater floor of a very large lagoon can look sparse; raise `corals` and keep weed low (dense weed reads as dirt through the glass).
- Boolean props (`cut`, `tunnel_mouth`) use the EXACT solver: fine for a few objects, slow for hundreds.
