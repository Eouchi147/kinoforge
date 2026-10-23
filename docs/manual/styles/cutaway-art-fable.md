# Cutaway art look: fable (mid-century storybook painting)

The same Cutaway block painted rather than rendered: the feel of 1950s hand-painted animation backgrounds (gouache,
stylised tall trees, patterned layers, bold flat colour shapes). No character, logo or name of any studio. It is the
look planned for the classical-music film Sam asked for on 23 Oct 16:34 ("synced, poetic, exotic, Disney-inspired"):
STATUS 23 Oct names "the Fable music film on the seasons grammar" (Borodin, In the Steppes of Central Asia, Musopen 2012,
public domain, in rc-render release `music`, cuts 1:57 and 3:17, long cut by default) as next after Sam's pick. Board
sent to Sam on 23 Oct; his pick is pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/fable.py` with the
shared helpers `films/styles/cutaway/art/_jewel.py`.

## What it changes
- Palette (jewel): midnight (0.07, 0.10, 0.25), deep teal, teal, emerald, jade, gold (0.96, 0.74, 0.30), pale gold, coral
  (0.95, 0.47, 0.38), deep coral, plum, cream, ink; constants at the top of `fable.py`.
- Every material of the set becomes flat paint (`_jewel.Paint`: emission in a cool shadow colour, one hard toon
  terminator from the low sun, contact shadow via ambient occlusion, gouache mottle, optional rim).
- World: a painted gradient sky (midnight to teal to coral and gold), a large soft sun ringed by painted halos, long flat
  cloud streaks, layered flat hills with tiny spire trees and a gold rim toward the sun.
- Trees: kit trees hidden, tall decorative forms at the same spots (spires, tiered crowns, ovals) with fine vertical
  striations and a gold rim, a few in coral blossom, swaying as whole shapes in `frame`.
- Cut faces: flat jewel bands (plum, gold, coral, deep coral, teal gravel, gold ochre, teal limestone, midnight bedrock),
  darker at the foot of each band, divided by fine glowing gold lines; pebbles as flat cream dots with a thin ring; faint
  laminae and gold flecks like stars deep down. Egg openings kept with `_jewel.under_mask`.
- Water: translucent teal with gold glints and painted ripple lines.
- Lights: sun softened; fill, rim and edge spills off; museum spots halved. View transform Standard.
- Compositor: anisotropic Kuwahara brushwork, paper grain, soft glow, vignette; words in their own view layer, crisp,
  midnight ink on cream plates.
- Animals, eggs, houses, mill and bridge keep their shapes and are repainted.
- On the seasons loop: the loop's season-driven ground, grass, leaves (blossom, autumn, thinning), snow and ice are kept
  and repainted (their colours drive the paint, ambient 0.85 to 0.88, saturation 1.45); the kit trees stay (their seasons
  are the story); the backdrop is a painted wash following the loop's own season colour; the haze box `sz_haze` is
  hidden; the sun is softened each frame after the loop sets it; the title is midnight ink with no plate.

## Exact steps (apply it)
1. Line film: add `"art": "fable"` to `spec.json` `look`, or render with `KF_ART=fable`.
2. Seasons loop board: `python3 films/cutaway/looks/make_seasons.py fable` (folder exists:
   `films/cutaway/looks/seasons-fable/`). Local check:
   `python3 harness/blender_render.py films/cutaway/looks/seasons-fable --w 270 --h 480 --samples 8 --start 40 --end 41`
   (also 100 and 260).
3. Meadow board: `python3 films/cutaway/looks/make.py fable` (folder `films/cutaway/looks/fable/`). Local check:
   `python3 harness/blender_render.py films/cutaway/looks/fable --w 640 --h 360 --samples 12 --start 440 --end 441` (and 830).
4. Full-size board or film: Mac lane job (`docs/PLAYBOOKS/render-on-the-mac.md`) or rc-render `stills.yml` / `films.yml`
   with `film=films/cutaway/looks/fable` (or your film folder).

## Cost per frame
Cheaper than the reference: mostly emission, 3 bounces, no glass refraction, no world lighting, about 0.6 to 0.8 times the
reference plus 1 to 3 s of Kuwahara compositing at 1280x720. Measured on the shared 2-core box at 640x360, 12 spp: 55 s
(crane, frame 440) and 73 s (hero) with other builders running; board frame 830 at 640x360, 8 spp: 54.5 s. Seasons loop
at 270x480, 8 spp: 13 to 32 s. Full-size board frames on the Mac lane: part of the "about 10 to 60 s a frame" for the
twelve looks (LOG 23 Oct); not split per look.

## Best uses (from NOTES)
1. Children's and family brands (toy makers, picture-book publishers, family attractions): a 30 to 60 s story ad or
   launch film that feels like a classic animated feature.
2. Museums, heritage sites and natural parks: poetic "what lies under" films for a gallery screen or social.
3. Wineries, terroir food brands and luxury hospitality: the soil under a vineyard or estate told with classical music.
How a film in it should feel: slow eased moves like a multiplane pan across painted layers, the music carrying the
changes, long holds on sky and trees, few labels, the sun lowering into the hills by the end.

## Weak spots
- Grass blades are geometry; the filter softens them, but very close ground shots show blades.
- Painted trees sway as whole shapes, not in the grass wind field.
- Kuwahara brushwork is screen space: it may shimmer at high-contrast edges in motion (not yet tested moving).
- Sky paper grain is fixed to the screen (reads as paint on a board; unproven in motion).
- Bones read pale cream-grey on the midnight dig pocket in the macro.
- On the 9:16 seasons loop the brushwork is subtler because the block is small in frame.

## Alternatives
`storybook-ink` (picture-book line and wash), `papercraft` (handmade), `night-glow` (same jewel family at night).

## Checks before showing Sam
Words crisp on their plates; eggs visible (not behind the painted wall); one moving stretch watched for brush shimmer.

## Known traps
Rounds recorded in NOTES: the words layer came out opaque over a black picture (fix: film transparent plus the
Environment pass for the sky); plates mis-sized when words left the active layer (keep them indirect-only); eggs hidden
when the wall shader dropped the openings (`under_mask`); on the loop, plants stayed dark until instance prototypes were
repainted (`_jewel.scene_materials`).

## Sources of truth
`films/styles/cutaway/art/fable.py` (docstring and constants), `_jewel.py`, `films/cutaway/looks/fable/NOTES.md`,
`films/cutaway/looks/seasons-fable/NOTES.md`, `docs/STATUS.md` (Cutaway art directions), `docs/LOG.md` 23 Oct. The code
wins if they disagree.
