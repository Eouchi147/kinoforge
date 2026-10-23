# Cutaway art look: papercraft (layered cut paper under a desk lamp)

The Cutaway block as a handmade cut-paper diorama: flat posterised card colours with visible paper fibre, the strata
rebuilt as stacked deckled sheets, one warm desk lamp, a cream paper sky, a kraft table. Board sent to Sam on 23 Oct;
his pick is pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/papercraft.py`, helpers
`films/styles/cutaway/art/_post.py` (`walk_principled`, `on_materials`, fibre and grain texture builders).

## What it changes
- Materials: colours posterised to a handful of paper tones and multiplied by paper fibre (two crossing stretched
  noises plus fine grain), also used as bump so the lamp rakes across it. Paper cream (0.93, 0.86, 0.72).
- Cut faces: each stratum a flat sheet with a deckled, slightly torn edge (a pale torn core along the lower edge), a soft
  drop shadow on the sheet below, punched paper dots instead of pebbles.
- Trees and rocks flat-shaded (faceted folded card).
- Light: the golden-hour rig swapped for one warm desk lamp (a large soft sun from the front left, soft real shadows).
- World: cream paper sky, kraft paper table, standing ridges of layered paper behind the block that cast soft shadows on
  each other: `ridges()` builds eight sheets (four distances, 5.4, 7.0, 8.8 and 10.8 m, each on the two far sides, +Y
  and -X), wavy tops, flat colours with fibre (the docstrings still say three; the code and NOTES say eight).
- God-ray cards off. No compositor.

## Exact steps (apply it)
1. Line film: `"look": {"art": "papercraft"}`, or `KF_ART=papercraft`.
2. Seasons board (exists): `films/cutaway/looks/seasons-papercraft/` (frames 40, 100, 260).
3. Meadow board (exists): `films/cutaway/looks/papercraft/`; local check at 640x360, 8 spp, frames 440 and 830.
4. Runner still: rc-render `stills.yml` (`film=films/cutaway/looks/papercraft`, `frames=830`, `w=640`, `h=360`,
   `samples=8`, tag `looks-papercraft-r1`, made at commit 3bbb164).

## Cost per frame
About the reference or a little less (no fog, no god rays, simple diffuse; the paper bump adds a bit). Runner stills at
640x360, 8 spp: about 1 to 2.5 min of wall time per run including setup. Local 2-core box timings were noisy (11 to
100 s a frame, box shared). Full-size time: the Mac render's (not split per look).

## Best uses (from NOTES)
Children's book publishers and museum exhibits (how the ground is built, one sheet per era); craft and stationery brands
(a handmade launch film); schools and science channels (geology, history timelines).

## Weak spots
Grass blades stay real geometry (green, not clearly paper); egg figures keep their kit shapes; the paper edge is a shader
on a flat face, so at grazing angles it does not catch light like a real sheet edge.

## Alternatives
`claymation` (handmade 3D), `storybook-ink` (drawn), `flat-vector` (2D).

## Checks before showing Sam
Dark browns must not posterise to olive (round 2 fix of the cavity colour).

## Known traps
The modules were made generic in round 2 (fallbacks when the engine's sets, overlay or land are missing) so they run on
the seasons loop through the adapter.

## Sources of truth
`films/styles/cutaway/art/papercraft.py`, `_post.py`, `films/cutaway/looks/papercraft/NOTES.md`. The code wins if they
disagree.
