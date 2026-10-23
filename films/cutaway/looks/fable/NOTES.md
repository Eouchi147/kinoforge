# Look board: fable (mid-century storybook painting)

Module: `films/styles/cutaway/art/fable.py` (shared helpers in `films/styles/cutaway/art/_jewel.py`). Folder made by
`python3 films/cutaway/looks/make.py fable` (meadow spec with `look.art = "fable"`).

## The look
The meadow block painted, not rendered: the feel of 1950s hand-painted animation backgrounds (stylised tall trees and
patterned layers, bold flat colour shapes, gouache texture). A jewel palette (deep teal, emerald, gold, coral, midnight
blue); a painted gradient sky (midnight to teal to coral and gold) with a large soft sun ringed by painted halos and long
flat cloud streaks; layered hills on the horizon with tiny spire trees and a gold rim toward the sun; the kit trees
replaced by tall decorative forms (spires, tiered crowns, ovals) with fine vertical striations and a gold rim, a few in
coral blossom, swaying gently; the cut faces as flat jewel bands (plum, gold, coral, deep coral, teal gravel, gold ochre,
teal limestone, midnight bedrock), darker at the foot of each band, divided by fine glowing gold lines, pebbles as flat
cream dots with a thin ring, faint laminae and gold flecks like stars in the deep layers; the river a translucent teal
with gold glints and painted ripple lines. Brushwork from an anisotropic Kuwahara filter, paper grain, soft glow. The
words are set in code, crisp in their own view layer, midnight ink on cream plates. No studio character, logo or name.

## Stills (local, this chat machine, Blender 5.2 bpy CPU; no runner stills, see below)
| Round | Size, samples | Times (frames) | What changed |
| --- | --- | --- | --- |
| t1 | 480x270, 8 | 18.33, 32.0, 36.0 (440, 768, 864) | first pass: words layer came out opaque over a black picture (view-layer alpha) |
| t2 | 480x270, 8 | same | film transparent + Environment pass for the sky: picture back. Label plates mis-sized (words excluded from the active view layer, so text was not measured); eggs hidden behind the wall (my wall shader dropped the egg openings) |
| t3 | 640x360, 12 | same | words kept in the picture layer as indirect-only (measured, invisible); wall and water repainted inside the egg-opening mask; finds brighter; amphora cream on the coral band |
| t4 | 640x360, 12 | 18.33, 36.0 | laminae in the deep layers, coral trees lighter. Accepted |

Measured on this 2-core shared box at 640x360, 12 samples: 55 s (crane, frame 440) and 73 s (hero) per frame, with
other builders rendering at the same time; the reference took 21 s per frame at 480x270, 8 samples here. The look is
mostly emission with 3 bounces and no glass, so on a clean machine expect it at or below the reference's cost, plus 1 to
3 s of compositing (Kuwahara) at 1280x720.

Runner stills were not dispatched: this builder does not commit or push (the runner checks out a pushed commit). The
coordinator renders the final board frames (440, 830) from the working tree.

## What a short film in this look should feel like
A fable told without words: slow, eased camera moves like a multiplane pan across painted layers, the music carrying
the cuts (a classical piece, each find revealed on a phrase), the gold lines catching the light as the camera sinks
through time. Warm and wondering rather than informative: few labels, long holds on the sky and the trees, the sun
lowering into the hills by the end. It should feel like the opening pages of a picture book read aloud by an orchestra.

## Weak spots (honest)
- Grass blades are still geometry; the filter softens them into a painted fringe, but very close ground shots will show
  blades rather than painted shapes.
- The painted trees sway as whole shapes (rotation in `frame`), not in the wind field of the grass.
- Kuwahara brushwork is computed per frame in screen space: in motion it shimmers slightly at high-contrast edges
  (not yet tested in a moving render).
- The sky's paper grain is fixed to the screen (like paint on a board under a moving camera): reads as intended in
  stills, unproven in motion.
- The bones read pale cream-grey rather than bright ivory on the midnight dig pocket in the macro shot.
- Only seen at 640x360 locally; full-size stills not yet looked at.

## Three projects where this look is the right choice
1. Children's and family brands (toy makers, picture-book publishers, family attractions): a 30 to 60 s story ad or
   launch film that feels like a classic animated feature. They pay for warmth and wonder.
2. Museums, heritage sites and natural parks: "what lies under" explainer films for a gallery screen or social, poetic
   rather than technical. They pay for an exhibit piece that families stop for.
3. Wineries, terroir food brands and luxury hospitality: the land cut open to show the soil under a vineyard or an
   estate, told with classical music. They pay for premium storytelling about place and origin.
