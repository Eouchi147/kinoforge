# Cutaway art look: blueprint (engineering drawing)

The Cutaway as a cyanotype sheet: deep blueprint blue, a faint drafting grid, fine pale-cyan and white lines for every
edge, flat fills with no photographic shading, each soil layer hatched with its own drawing symbol, a sheet border with
zone ticks, a depth ruler, dimension lines and a "SECTION A-A" tag; labels in JetBrains Mono. Board sent to Sam on 23
Oct; his pick is pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/blueprint.py`, helpers
`_npr_lines.py`; font `ads/fonts/JetBrainsMono.ttf` (OFL).

## What it changes
The whole picture is a numpy stylization of the Cycles passes (the line-art pipeline, see `cutaway-art-storybook-ink.md`
"How it renders"): no new materials; light is used only to find glass and shadows. Colours: background (0.050, 0.190,
0.400), fills for top, cut and objects, line (0.84, 0.96, 1.00), faint line (0.52, 0.78, 0.94). Hatch symbols per layer
(diagonals, dots, cross-hatch, masonry, rock) locked to the world so they hold still when the camera moves; dashed layer
boundaries; set in code: the sheet border with zone ticks, a depth ruler in the left margin (a tick every 0.1 m of the
block), dimension lines when the block corners are in frame, the SECTION A-A tag. Labels become pale-cyan type on blue
plates.

## Exact steps (apply it)
1. Line film: `"look": {"art": "blueprint"}`, or `KF_ART=blueprint`.
2. Seasons board (exists): `films/cutaway/looks/seasons-blueprint/`; checked at 360x640 with `KF_ART` (NOTES).
3. Meadow board (exists): `films/cutaway/looks/blueprint/`; frames 440 and 830.
4. Runner stills were not run for this look (only storybook-ink was); full-size board frames came from the Mac lane.

## Cost per frame
The reference's Cycles capture (same samples, volumes hidden) plus about 4 s of numpy and about 1 s for the words pass at
1280x720. Same pipeline as storybook-ink: about 25 s a frame on a runner at 640x360, 8 spp; about 15 s at full size on the
Mac lane.

## Best uses (from NOTES)
1. Civil, geotechnical or drilling companies: site investigations, foundations, tunnels (how-it-works).
2. Tech or infrastructure start-ups whose product sits under the ground or in a system (cables, water, heat pumps).
3. Engineering schools or standards bodies: a process as a section drawing.

## Weak spots
Screen-space noise can shimmer in motion; pixel-thin lines can alias on far objects; grass and tree interiors simplified.

## Alternatives
`flat-vector` (clean explainer), `engraving`, `chalkboard`.

## Checks before showing Sam
Dimension lines and ruler must not collide with labels; judge the hero at 830.

## Known traps
Same as the line-art pipeline: hide volumes during capture; EXR passes read back with bpy.

## Sources of truth
`films/styles/cutaway/art/blueprint.py`, `_npr_lines.py`, `films/cutaway/looks/blueprint/NOTES.md`. The code wins if they
disagree.
