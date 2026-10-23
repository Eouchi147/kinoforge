# Cutaway: the four board looks (A Studio block, B Floating island, C Lagoon cut, D Mill at dusk)

The first Cutaway style board (22 Oct 2026), the one Sam called "amazing". Four looks of the same kit, each a function
`look_x(bpy, kit, aspect)` in `films/styles/cutaway/looks.py` returning `{land, cam, look, exposure}`. They are starting
points for a film's set: copy the call you need into your own `blender.py`. Look D (the river village) is the base the
cinematic test was built on (`cutaway-cinematic.md`).

## Inputs
The kit (`cutaway.md`), Blender `bpy` 5.2.2, an aspect (`'16:9'` or `'9:16'`).

## The four looks (exact parameters in `looks.py`)
| Look | What it shows | Block and strata | Background and light | Camera | Finish |
| --- | --- | --- | --- | --- | --- |
| A Studio block | white seamless; a river with lily pads splitting a grassy block | 4 x 4 m, depth 1.25, `STRATA['meadow']`, seed 4, `rolling(0.10, 0.32, base 0.02)`, river `RIVER` width 0.72 depth 0.34, 16 trees (round, round, cone), 14 boulders, flowers 0.6, 22 lilies, reeds 0.5 | `cw.studio` colour (0.94, 0.935, 0.925), key az -150 el 50 strength 3.4 angle 14, fill 0.95, cloud shadows 0.22; 3 birds | az -42, el 33 (27 in 9:16), lens 60, fill 0.86 (0.93) | AgX Base Contrast, exposure 0.25 |
| B Floating island | open sky and mist, a pond with a glass front, hanging roots, falling stones, birds | 3.6 x 3.6 m, depth 1.1, `STRATA['red']`, seed 7, `rolling(0.16, 0.4, base 0.04, tilt (0, 0.02))`, pond (0.25, -1.45) radii (0.95, 0.8), 9 round trees x1.2, grass 1.15, height 1.3 | `cw.sky` sun az -135 el 42 strength 3.2; `falling_stones` 12; `hanging_roots` 46; 4 birds | az -48, el 24 (30), lens 55, fill 0.70 (0.80), target (0, 0, -0.75) | AgX Base Contrast, exposure 0.15 |
| C Lagoon cut | raised pale limestone shore with cracks, a clear lagoon open on two faces, corals, weed | 4 x 4 m, depth 1.2, `STRATA['lagoon']`, seed 11, basin lagoon depth 0.5, shelf 0.55, `shore_rock=1.0`, 46 corals, no trees, water tint (0.26, 0.82, 0.80) density 2.0 | `cw.studio` (0.90, 0.89, 0.87), key az -140 el 58 strength 3.6 | az -45, el 30 (27), lens 60, fill 0.86 (0.93) | AgX Base Contrast, exposure 0.3 |
| D Mill at dusk | the river block at dusk: six lit cottages, a turning watermill, a bridge, four lamps, a dirt lane | as A plus `zones` (a lane), `keep_clear` round houses and mill, 11 trees, water density 5.0, glow 0, dark bed, caustics 0.2 | `cw.dusk` sun az -165 el 12 strength 3.0; houses `lit=1.5`; mill `wheel_r=0.11`; 3 birds | az -40, el 31 (27), lens 60, fill 0.86 (0.93) | AgX Medium High Contrast, exposure 0.9 |

## Exact steps
1. Local still (slow on the 2-core box; use 480 px for checks):
   `python3 films/styles/cutaway/board.py A --aspect 16:9 --w 480 --samples 12`
   Full size: `python3 films/styles/cutaway/board.py A --aspect 16:9 --w 1920 --samples 96 --out films/styles/cutaway/board/A-studio-block.jpg`.
   `--border x0 x1 y0 y1` renders a crop, `--build-only` builds without rendering, `--t` picks the time.
2. Whole board on runners (one job per still), after pushing:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/styles/cutaway/stills/board' -f 'inputs[frames]=24,25,26,27' -f 'inputs[per_job]=2' -f 'inputs[tag]=cutaway-b' \
     -f 'inputs[w]=1920' -f 'inputs[h]=1080' -f 'inputs[samples]=128' -f "inputs[ref]=$(git rev-parse HEAD)"
   bash /home/claude/rc-render/tools/getstills.sh cutaway-b out/
   ```
   Frame % 4 picks the look (24 A, 25 B, 26 C, 27 D). For vertical stills use `stills/mixed` (0 A 9:16, 1 B 16:9,
   2 C 16:9, 3 D 9:16) or pass `--w 1080 --h 1920`.
3. To use a look in a film: `import looks; d = looks.look_d(bpy, kit, aspect)`, or copy its `cw.block` call and
   change only what the story needs. As a moving scene: `from scene import make; DURATION, SETTINGS, build, frame =
   make('A', duration=8.0, move='orbit', samples=32, deg=16.0, fast=True)` (moves: `orbit`, `push`, `none`).

Expected outputs: `films/styles/cutaway/board/A-studio-block.jpg`, `A-studio-block-vertical.jpg`, `B-floating-island.jpg`,
`C-lagoon-cut.jpg`, `D-mill-at-dusk.jpg`, `D-mill-at-dusk-vertical.jpg` (already committed, jpg q90).

## Cost
Runner, 1920x1080, 128 spp: A and B about 7 min a still; C (large glass area) and D (many small lights) about 20 min.
1280x720, 64 spp: about 1.5 to 6 min a job including setup (dusk fastest, sky slowest).

## Best uses
A: ads and clean explainers (white studio, the work underground reads clearly; the drainage ad uses `cw.studio` too).
B: fantasy, openings, "a world apart". C: travel, sea, tourism. D:
storytelling, villages, dusk moods (the cinematic test and the line's `village`, `mill`, `bridge`, `lamps` props).

## Alternatives
The line's sets (`cutaway-line.md`) give the same worlds from data (`time: studio`, `water: lagoon`, `props.mill`).

## Checks before showing Sam
Open every still at full size; the water must reach the camera-facing face where it is cut; nothing clipped at the frame.

## Known traps
- C's limestone plates can look like paving if too even; very large lagoon floors look sparse (raise `corals`).
- In D, small lights make Cycles slow (about 20 min a 1920 still).
- B's stacked transparent mist and cloud cards are the slowest part of the sky look.

## Sources of truth
`films/styles/cutaway/looks.py`, `board.py`, `scene.py`, `stills/`, `films/styles/cutaway/README.md` (The board),
`docs/LOG.md` 22 Oct ("Cutaway base kit finished"). The code wins if they disagree.
