# Cutaway art look: chalkboard (chalk on a slate blackboard, teaching)

The Cutaway drawn in chalk: dusty white outlines, soil layers rubbed in with yellow, pink and pale blue chalk (hatching
smudged with a finger), each find in its own coloured stick, water in blue wavy lines, grainy broken strokes, old eraser
swipes and dust, a slim wooden frame; labels in Archivo. Board sent to Sam on 23 Oct; his pick is pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/chalkboard.py`, helpers
`_npr_lines.py`; font `ads/fonts/Archivo.ttf` (OFL).

## What it changes
Numpy stylization of the Cycles passes (line-art pipeline, see `cutaway-art-storybook-ink.md`); light and shadow ignored,
colour is the chalk's. Board (0.070, 0.100, 0.092) with highlight, chalks white, yellow, pink, blue (`CHALKS`), wood frame;
`LAYER_CHALK = [0, 1, 2, 2, 3, 1, 0, 3]` assigns a chalk to each stratum. Labels become chalk-white type on dark plates.

## Exact steps (apply it)
1. Line film: `"look": {"art": "chalkboard"}`, or `KF_ART=chalkboard`.
2. Seasons board (exists): `films/cutaway/looks/seasons-chalkboard/`.
3. Meadow board (exists): `films/cutaway/looks/chalkboard/`; frames 440 and 830.

## Cost per frame
The reference's Cycles capture plus about 5 s of numpy and about 1 s for the words pass; about 25 s a frame at 640x360,
8 spp on a runner (same pipeline as storybook-ink); about 15 s at full size on the Mac lane.

## Best uses (from NOTES)
1. Teachers, tutoring brands, online courses: geology, land history, science topics.
2. Museum education departments: a gallery talk film or an activity sheet that feels like a lesson.
3. Farms, gardens, soil-testing businesses: "what is in your soil" explainers.

## Weak spots
Chalk grain is fixed to the screen (shimmer risk in motion); pixel-thin lines alias on far objects; simplified grass and
trees.

## Alternatives
`blueprint` (technical), `storybook-ink` (soft), `engraving` (historic).

## Checks before showing Sam
Coloured finds distinct from the layer chalks; labels readable on the dark plates.

## Known traps
Same as the line-art pipeline (volumes hidden during capture).

## Sources of truth
`films/styles/cutaway/art/chalkboard.py`, `_npr_lines.py`, `films/cutaway/looks/chalkboard/NOTES.md`. The code wins if
they disagree.
