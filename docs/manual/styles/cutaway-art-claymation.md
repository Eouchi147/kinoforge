# Cutaway art look: claymation (plasticine stop-motion)

The whole block sculpted in clay: saturated waxy colour with fingerprints and tool marks, real lumpy leaves and rocks, a
painted cyclorama, and stop-motion timing (poses on twos, the texture boiling between poses). Board sent to Sam on 23
Oct; LOG 23 Oct flags it as "close to the base look". His pick is pending.

Not to confuse with the house style **Clay** (`proto/p10-clay`, Dark Corners Arabia), a separate hand-built Blender style.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/claymation.py`,
helpers `_post.py` (fingerprint and tool-mark texture builders).

## What it changes
- Every material: saturated clay colour, a waxy low sheen, a touch of subsurface scattering, and a bump built from lumps
  (low-frequency noise), fingerprints (concentric rings round voronoi cell centres, one thumb press per cell) and tool
  marks (distorted wave bands).
- Cut face: strata kept, same sculpted surface. Trees and rocks: real lumpy displacement.
- Light: the golden-hour rig stays with a bigger, softer sun; no god rays; fog off.
- World: painted turquoise-to-cream cyclorama and a clay baseboard (a miniature set under a practical lamp).
- Time: animation stepped on twos (12 poses a second) and the surface "boils" a hair from pose to pose (`BOIL` value
  sockets shift the texture lookup each pose in `frame`).
- No compositor.

## Exact steps (apply it)
1. Line film: `"look": {"art": "claymation"}`, or `KF_ART=claymation`.
2. Seasons board (exists): `films/cutaway/looks/seasons-claymation/`.
3. Meadow board (exists): `films/cutaway/looks/claymation/`; local 640x360, 8 spp, frames 440 and 830.
4. Runner still: `stills.yml` tag `looks-claymation-r1` (frame 830, 640x360, 8 spp, commit 3bbb164).

## Cost per frame
The slowest look: about 1.1 to 1.3 times the reference (subsurface and bump everywhere) by the module's estimate; 1.3 to
2 times on the noisy shared 2-core box. Runner still at 640x360, 8 spp: about 1 to 2.5 min per run including setup.

## Best uses (from NOTES)
Family, kids, toy and food brands wanting handmade warmth; museum and children's TV explainers; a brand mascot short.

## Weak spots
Grass and fine geometry stay thin and clean, so the clay feel lives in surfaces; pebbles plus tool marks give a pepper-dot
look on lower strata that can look dirty; slowest look; close to the base look on the board (LOG).

## Alternatives
`papercraft` (handmade, cheaper), the house style Clay for character films.

## Checks before showing Sam
Watch a moving stretch: the on-twos timing and the boil must read as stop-motion, not as a dropped-frame fault.

## Known traps
`frame` steps time by re-running `kit.update(tq)` for every set at `tq = floor(t * 12) / 12`, so everything registered
with the kit (wind, water, animals, eggs) moves on twos; the camera is posed by the engine and is not stepped. Something a
film poses outside the kit keeps moving on ones unless that film steps it too.

## Sources of truth
`films/styles/cutaway/art/claymation.py`, `_post.py`, `films/cutaway/looks/claymation/NOTES.md`, `docs/LOG.md` 23 Oct.
The code wins if they disagree.
