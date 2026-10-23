# Cutaway art look: risograph (three spot inks, halftone, misregistration)

The Cutaway as an editorial riso print: the picture separated into fluorescent pink, teal and yellow inks, each through
its own coarse halftone screen, plates slightly out of register, multiplied onto grained cream paper; labels printed in
one dark ink. Board sent to Sam on 23 Oct; LOG 23 Oct notes the halftone is too coarse. His pick is pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/risograph.py`, helpers
`_post.py`.

## What it changes
- Render: as usual, depth of field and god rays off; samples capped at 10 in code (`min(samples, 10)`; the docstring
  says 8): the halftone hides the noise.
- Compositor (CPU): display colours, a bolder grade, separation into three inks by optical density (a 3 x 3 matrix
  solved in code from each ink's transmittance, `INKS`), order `pink, teal, yellow`.
- Halftone: round dots, `CELL = 9.0` px cells at 1280 wide, screen angles pink 15, teal 75, yellow 45 degrees; ink gains
  pink 0.82, teal 1.3, yellow 0.95; uneven laydown (white speckle).
- Misregistration: teal (3, -2) px, yellow (-2, 3) px at 1280 wide.
- Paper: cream (0.965, 0.935, 0.865) with fibre grain; overprints mix like real riso (pink on yellow orange, teal on
  yellow green, all three a deep violet-navy).
- Words: printed afterwards in one dark ink from their own full-resolution scene.

## Exact steps (apply it)
1. Line film: `"look": {"art": "risograph"}`, or `KF_ART=risograph`.
2. Seasons board (exists): `films/cutaway/looks/seasons-risograph/`.
3. Meadow board (exists): `films/cutaway/looks/risograph/`; local 640x360, 8 spp, frames 440 and 830.
4. Runner still: `stills.yml` tag `looks-risograph-r1` (frame 830, 640x360, 8 spp, commit 3bbb164). Judge the dots at
   full size.
5. If the dots must be finer (the open LOG note), lower `CELL` and re-check at full size.

## Cost per frame
About the reference, plus a few seconds for compositing and the words scene. Runner still at 640x360: about 1 to 2.5 min
per run including setup.

## Best uses (from NOTES)
Posters, album and festival art, editorial illustration; cultural institutions and indie publishers; craft food and drink.

## Weak spots
Warm scenes land mostly in pink and yellow (teal only in greens and shadows); halftone eats fine detail, so the eggs
become blobs at phone size; halftone too coarse (LOG 23 Oct).

## Alternatives
`pixel` (another reduction), `stained-glass` (poster-like), `engraving` (print).

## Checks before showing Sam
The finds must still read at 1080 wide on a phone; labels in one clean ink.

## Known traps
Compositor on CPU for runners; judge only at full size (the screen is set in pixels at 1280 wide).

## Sources of truth
`films/styles/cutaway/art/risograph.py`, `_post.py`, `films/cutaway/looks/risograph/NOTES.md`, `docs/LOG.md` 23 Oct. The
code wins if they disagree.
