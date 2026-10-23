# Cutaway art look: engraving (19th-century encyclopaedia plate)

The Cutaway as a sepia copperplate: no flat colour, every tone made of parallel lines whose width follows the tone,
cross-hatched deep shadows, lines that follow the forms (along the soil layers, over the relief, round foliage clumps),
cream paper with foxing and fibres, a thin double plate border. Labels become ink on paper plates. Board sent to Sam on
23 Oct; his pick is pending. LOG 23 Oct: "Line-art looks: engraving density tweak".

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/engraving.py`, helpers
`_npr_lines.py`.

## What it changes
- Adds one AOV output `sd` (the strata coordinate) to the `cw_strata` material, so the hatching on the cut faces runs
  along the layers and bends with every fold.
- Everything else is the numpy stylization of the passes (line-art pipeline, see `cutaway-art-storybook-ink.md`): paper
  (0.935, 0.885, 0.760), ink (0.20, 0.115, 0.065); hatching width from tone (hairlines in light, nearly solid in dark),
  cross-hatch in deep shadow; ground lines ride the relief, foliage lines wrap each clump, water and walls run level;
  double plate border with a faint plate mark.

## Exact steps (apply it)
1. Line film: `"look": {"art": "engraving"}`, or `KF_ART=engraving`.
2. Seasons board (exists): `films/cutaway/looks/seasons-engraving/`.
3. Meadow board (exists): `films/cutaway/looks/engraving/`; frames 440 and 830.

## Cost per frame
The reference's Cycles capture plus about 6 s of numpy and about 1 s for the words pass; about 25 s a frame at 640x360,
8 spp on a runner (same pipeline as storybook-ink); about 15 s at full size on the Mac lane.

## Best uses (from NOTES)
1. A history channel, heritage trust or archaeology film (Roman layers, medieval sites).
2. Publishers of illustrated history, rare-book and map dealers (an animated plate for a launch).
3. A museum, or a law or finance firm with old roots wanting a serious, timeless look.

## Weak spots
Screen-space paper can shimmer in motion; pixel-thin lines alias on far objects; simplified grass and trees.

## Alternatives
`blueprint`, `storybook-ink`, `chalkboard` (same pipeline); Battle Map for history films with armies.

## Checks before showing Sam
Hatch density must keep the finds readable (the density was tweaked on 23 Oct).

## Known traps
`apply` adds the `sd` AOV to any material whose name contains `strata` and has an Attribute node reading `sd`
(`cw_strata`, or `sz_strata` of the seasons loop). A scene with no such material gets level hatching (world height) on
its cut faces instead: give a new film's wall material that name and attribute if the lines must follow the layers.

## Sources of truth
`films/styles/cutaway/art/engraving.py`, `_npr_lines.py`, `films/cutaway/looks/engraving/NOTES.md`, `docs/LOG.md` 23 Oct.
The code wins if they disagree.
