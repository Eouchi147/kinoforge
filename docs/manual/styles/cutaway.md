# Cutaway: the kit (Blender library every Cutaway film is built on)

The Cutaway style is a block of land cut out of the world: a living landscape on top, four clean cross-section faces
(strata, pebbles, roots) and water as a clear glassy volume you can see into. The kit is one Python library,
`films/styles/cutaway/cutaway.py`, run inside Blender `bpy` 5.2.2 with Cycles (CPU on GitHub runners, METAL GPU on Sam's
Mac). Everything is procedural: no downloaded assets, no paid calls. Every Cutaway film imports the kit and never edits
it; what a film needs beyond it is built in the film's own `blender.py`. Decision: `docs/decisions/0004-cutaway-style.md`.
Sam's verdicts: the board "looks amazing" (22 Oct); he loves the style and wants it in the studio (22 Oct 20:24); the
house default for new films is the seasons loop grammar (`cutaway-seasons-loop.md`, 23 Oct 17:32).

Related pages: `cutaway-board-looks.md` (the four board looks), `cutaway-cinematic.md` (light, fog, eggs, animals),
`cutaway-line.md` (spec-driven films), `cutaway-seasons-loop.md` (the house default), `cutaway-art.md` (art directions).

## Inputs
- A story where the cut shows something you could not otherwise see (docs/SOUL.md section 4, Cutaway).
- Blender `bpy` 5.2.2 as a Python module (`pip install bpy==5.2.2`, Python 3.13) or the Blender 5.2 app (Mac lane).
- `numpy`. Fonts for words on screen from `ads/fonts/` (Instrument Sans, Archivo, JetBrains Mono, all OFL) or
  `films/cutaway/ads/drainage/fonts/` (Inter Tight, OFL).

## Files
| File | What it is |
| --- | --- |
| `films/styles/cutaway/cutaway.py` | The kit (library): `Kit`, `block()`, water regions, vegetation, props, backgrounds, cameras, time |
| `films/styles/cutaway/looks.py` | The four board looks A to D (`cutaway-board-looks.md`) |
| `films/styles/cutaway/scene.py` | Glue for `harness/blender_render.py`: `make(look, duration, move, samples, deg, fast, size)` returns `DURATION, SETTINGS, build, frame` |
| `films/styles/cutaway/board.py` | Local still renderer for the board looks |
| `films/styles/cutaway/board/` | The board stills (jpg q90): A, A vertical, B, C, D, D vertical |
| `films/styles/cutaway/test/` | Motion test film `style-cutaway-test` (8 s, look A, eased 16 degree orbit, 32 spp, `fast=True`); never rendered as a film (LOG 22 Oct: "the cinematic version comes first") |
| `films/styles/cutaway/stills/board/` | All four looks in one folder for rc-render `stills.yml`: frame % 4 picks the look (24, 25, 26, 27 = A, B, C, D) |
| `films/styles/cutaway/stills/A` to `D` | One look per folder |
| `films/styles/cutaway/stills/mixed/` | Looks and aspects mixed: frame % 4 = 0 A 9:16, 1 B 16:9, 2 C 16:9, 3 D 9:16 |
| `films/styles/cutaway/cinematic/` | The cinematic extras (`extras.py`) and the cinematic test film |
| `films/styles/cutaway/art/` | The art directions (`cutaway-art.md`) |

## The scene contract (every Cutaway `blender.py`)
`harness/blender_render.py` loads the film folder's `blender.py` and needs:

```python
DURATION = 8.0                      # seconds (or SHOTS = [{'name': 'a', 'dur': 4.0}, {'name': 'b', 'dur': 4.0}])
SETTINGS = {'samples': 48, 'denoise': True}   # also motion_blur, view_transform, look, exposure, max_bounces
def build(bpy, ctx): return state   # ctx = {W, H, fps, duration, timeline}
def frame(bpy, ctx, state, i, t):   # pose everything for frame i at time t; deterministic
```

Every frame must be a pure function of the frame index (seeded randomness, no clocks): a runner renders any frame range
alone. On runners `films.yml` passes `--samples` from `film.json` `samples` (default 24), which overrides `SETTINGS`.

## Exact steps (a new film on the kit)
1. Make the folder `films/cutaway/<id>/` with `film.json` (copy a series film's: `id`, `title`, `style: "cutaway"`,
   `duration`, `fps: 24`, `frames`, `render_w`/`render_h` 1280x720 or 720x1280, `w`/`h` 1920x1080 or 1080x1920,
   `samples` 20, `audio`).
2. Write `blender.py`. Minimal working scene (from `films/styles/cutaway/README.md`):

   ```python
   import os, sys
   ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
   sys.path.insert(0, os.path.join(ROOT, 'films/styles/cutaway'))
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
   (Adjust the `ROOT` depth to the folder depth: series films use four `..`.)
3. Coordinates: metres, block centred on the origin, top near z = 0, bottom at z = -depth. The camera-facing faces are
   **-Y** (left in frame) and **+X** (right) at the default azimuth (-40 degrees). Water cut open on a face must reach
   that face (run a river past the edge, put a pond centre near the edge).
4. Look locally at low size (2-core chat box: 60 to 100 s for 480x270 at 12 spp):
   `python3 harness/blender_render.py films/cutaway/<id> --w 640 --h 360 --samples 16 --start N --end N+1`
   (`--end` is exclusive). Frames land in `out/<id>/frames/%05d.png`.
5. Push, then full-quality stills on runners (one stills run in flight per builder, at most 8 frames):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/<id>' -f 'inputs[frames]=40,150,300' -f 'inputs[per_job]=2' \
     -f 'inputs[tag]=<id>-r1' -f 'inputs[w]=1280' -f 'inputs[h]=720' -f 'inputs[samples]=20' -f "inputs[ref]=$(git rev-parse HEAD)"
   bash /home/claude/rc-render/tools/getstills.sh <id>-r1 out/
   ```
   Or the Mac lane when connected (`docs/PLAYBOOKS/render-on-the-mac.md`): about 3 to 7 s a frame at 1280x720, 20 spp.
6. Render: rc-render `films.yml` (`parts` 20 to 24 for Blender) or Mac lane chunks plus ffmpeg (see any series film page,
   for example `docs/manual/films/cutaway-series-reef-and-wreck.md`).

## The API (what the kit gives)
`cw.block(kit, <parameters below>)` returns a `Land`:

| Parameter | Meaning (default) |
| --- | --- |
| `size` | `(sx, sy)` in metres, or one number (4 x 4) |
| `depth` | block thickness (1.4) |
| `strata` | layers top-down `(name, thickness_m, sRGB, pebble_density 0..1)`; the last fills the rest. Presets `cw.STRATA`: `meadow`, `red`, `limestone`, `lagoon`, `mud` |
| `top` | height function `h(x, y)` (numpy, vectorised) or a 2D array; `cw.rolling(amp, freq, seed, tilt, base)` makes one |
| `water` | regions: `cw.river(path, width, depth, level, shelf)`, `cw.pond(center, radius or (rx, ry), depth, level)`, `cw.basin(fn_signed_distance, depth, level)`; one water volume per block at the **first** region's level |
| `season` | `'summer'`, `'spring'`, `'autumn'`, `'winter'` (snow, frosted water) or a dict overriding `cw.SEASONS` keys |
| `zones(x, y, h)` | extra weights `{'rock', 'sand', 'path', 'grass'}` (paths, pale rock, beaches) |
| `grass`, `grass_height` | density and height multipliers (1, 1) |
| `trees`, `tree_kinds`, `tree_spots` | count and kinds (`round`, `cone`; `tall` reads toy-like), or exact spots `[(x, y, scale, kind)]` |
| `boulders`, `flowers` | boulder count (12), flower amount 0..1 (0.5) |
| `under`, `corals`, `lilies`, `reeds` | underwater stones and weed (True), corals (0), lily pads (0), reeds 0..1 (0) |
| `shore_rock` | 0..1 shelf of raised pale limestone plates with cracks (lagoon look) |
| `keep_clear` | `[(x, y, r)]` no grass or trees there (for buildings) |
| `tree_scale`, `sway`, `water_tint`, `water_density`, `water_glow` | tree size; wind amount; water absorption colour and density; in-scatter glow (0.022; 0 at dusk or night) |
| `bed`, `caustics` | two sRGB tones of the underwater floor; caustic strength (0.5; 0.2 at dusk) |

`Land` fields and methods: `size`, `depth`, `level`, `pal`, `objects` (`top`, `walls`, `water`, `cw_grass` and the rest),
`mats`, `height(x, y)`, `field(x, y)`, `scatter(name, protos, pts, yaw, scale, sway, variant, z)`, `cut(obj)` (clip an
object flush to the faces), `place(obj, x, y, dz)`.

Props: `cw.pile`, `cw.pipe`, `cw.house`, `cw.mill` (turning wheel), `cw.bridge`, `cw.lamp`, `cw.tunnel_mouth`. Animate
any object with `kit.on_frame(fn)`; `fn(t)` runs inside `kit.update(t)`.

Backgrounds and life: `cw.studio` (seamless matte floor, key, fill, optional cloud shadows), `cw.sky` (gradient,
cloud cards, mist), `cw.dusk`, `cw.birds`, `cw.falling_stones`, `cw.hanging_roots`, `cw.cloud_shadows`.

Camera: `cw.camera(kit, land, aspect, az, el, lens, fill, target, dist, top_extra)` returns a `Cam` with `pose(az, el,
dist, target)` and `orbit(t, deg_per_s, duration)`; it frames the block's bounding box at `fill`, centred, in either
aspect (16:9 defaults el 32, fill 0.86; 9:16 el 27, fill 0.93).

Helpers: `cw.fbm`, `cw.vnoise`, `cw.cells`, `cw.smooth`, `cw.catmull`, `cw.mk_mesh`, `cw.gn_set`, `cw.mat_simple`,
`cw.mat_rock`, `cw.mat_glow`, `cw.render_settings(bpy, W, H, samples, look, exposure)`, `cw.apply_cycles(bpy, fast)`.

Time and loops: all motion is a pure function of `t` through `kit.update(t)`. Every motion closes a circle after
`kit.loop` seconds, so `[0, loop)` loops seamlessly; integer cycles per loop with `kit.cycles(t, per_second)`.

How it is built (for whoever extends it): one top grid mesh (about 2 cm cells) displaced by the height function, rivers
and ponds carved by signed distance; separate wall and bottom meshes built straight down from the boundary ring (no
boolean), carrying attributes `sd` (strata coordinate) and `dtop`; a strata shader (colour ramp over `sd`, wobbled band
edges, grain, voronoi pebbles, painted roots, a dark band under the turf); water as one closed glass box (IOR 1.33,
transparent to shadow rays, turquoise absorption, ripple bump on the top only, caustics faked in the bed shader);
vegetation prototypes instanced by one geometry-nodes group (`cw_sway`).

## Cost (free; measured 22 Oct)
| Render | Where | Cost |
| --- | --- | --- |
| Scene build (any look) | anywhere | 2 to 9 s |
| Motion frame 1280x720, 32 spp, `fast=True` | 4-core runner | about 20 to 70 s |
| Board still 1920x1080, 128 spp | 4-core runner | A and B about 7 min; C and D about 20 min |
| Preview 480x270, 12 spp | 2-core chat box | 60 to 100 s |
| Series films, 1280x720, 20 spp | Sam's Mac (M4, METAL) | about 3 to 7 s a frame cool, 9 to 16 s when the fanless Mac throttles |

Levers: `samples`, `fast=True`, `grass` density, `apply_cycles(bpy, fast=True)`, fewer mist layers, no volumes.

## Alternatives
- The spec-driven line (`cutaway-line.md`): no Blender code at all, for any place the presets can say. Prefer it.
- The seasons loop grammar (`cutaway-seasons-loop.md`): Sam's chosen base; start new films from it.
- The flat-vector 2D look (`cutaway-flat-vector.md`): about 500 to 1000 times faster, but 2D and only the meadow drawn.

## Checks before showing Sam
- `docs/PLAYBOOKS/check-before-showing-sam.md`: length, size, loudness, freeze and black detection, a contact sheet,
  three moving stretches. For a loop, render frames `last` and `0` and compare.
- Every cut and move has a written job (`films/director/CRAFT.md` sections 1 to 4); words set in code, no dash, no "...".

## Known traps
- A full haze volume fogs the whole frame: make god rays as light cards (`docs/LESSONS.md`).
- Boolean props (`cut`, `tunnel_mouth`) use the EXACT solver: slow for hundreds of objects (Agincourt used Manifold).
- Dense underwater weed reads as dirt through the glass; the `tall` tree reads toy-like.
- One water level per block: no waterfalls, no two rivers at different levels.
- Runners: one stills run in flight per builder, at most 8 frames; `ref` must be a full commit hash.

## Weak spots (honest, from the README)
Trees are lumpy-blob miniatures; water is one flat bump-mapped volume; caustics are faked; grass blades show in very close
shots; strata are a shader on flat walls (painted roots); houses, mill, bridge and lamps read at board distance only.

## Sources of truth
`films/styles/cutaway/README.md`, `films/styles/cutaway/cutaway.py`, `scene.py`, `board.py`, `test/`, `stills/`,
`docs/decisions/0004-cutaway-style.md`, `docs/PLAYBOOKS/make-a-cutaway-film.md`, `harness/blender_render.py`,
rc-render `.github/workflows/films.yml` and `stills.yml`. The code wins if they disagree.
