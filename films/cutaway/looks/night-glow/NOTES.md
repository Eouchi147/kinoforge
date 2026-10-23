# Look board: night-glow (bioluminescent night)

Module: `films/styles/cutaway/art/night-glow.py` (shared helpers in `films/styles/cutaway/art/_jewel.py`). Folder made
by `python3 films/cutaway/looks/make.py night-glow`.

## The look
The meadow at night, alive with light. A deep night sky with stars, a large pale moon low behind the block with a halo,
a faint green aurora along the horizon. Surfaces go dark and cool (moonlit, a hard silver terminator); the life and the
finds give the light: cyan veins of light hang from the turf like glowing roots, the pebbles glimmer like plankton, faint
blue lines divide the layers, the bones and the shell fossil glow sea-green at their edges, the gold vein and the chest
burn warm, the river is luminous turquoise from inside with brighter ripple lines, grass tips and moss spots glow green,
the trees carry speckles of light, the village windows are lit, and 70 fireflies (the cinematic extras' own, blinking)
drift over the grass. Wide soft bloom and a vignette in the compositor; words crisp in their own layer (pale plates,
midnight ink). AgX view (kept from the line) so the glows roll off softly.

## Stills (local, this chat machine, Blender 5.2 bpy CPU)
| Round | Size, samples | Times (frames) | What changed |
| --- | --- | --- | --- |
| t1 | 480x270, 8 | 18.33, 36.0 (440, 864) | first pass: layers too dark to read, root veins a uniform curtain, moon out of frame |
| t2 | 480x270, 8 | 18.33, 34.58 (440, 830) | bands lifted (violet and blue, each different), fewer and thinner veins with varied brightness, moon lowered to 9 degrees so it sits in the hero frame. Accepted |

Measured on this 2-core shared box at 480x270, 8 samples: about 60 s per frame (other builders rendering at the same
time; the reference was 21 s here at the same settings when the box was quieter). Mostly emission, 3 bounces, no glass;
expect about the reference's cost on a clean machine.

Runner stills were not dispatched (this builder does not commit or push); the coordinator renders the board frames.

## Weak spots (honest)
- The bands are all in the blue to violet range: they read as layers, but less distinct than in daylight.
- The fireflies are tiny emitters: at 640x360 they are specks; they need the full size to read.
- The edge glow on the finds uses the facing angle, so flat finds seen straight on (the amphora) glow less.
- Root veins are a shader on the flat wall (no depth), like the kit's roots.
- Only seen at 480x270 locally.

## Three projects where this look is the right choice
1. Natural history museums, aquariums and science centres: night-life and soil-life explainers, planetarium or gallery
   loops. They pay for wonder that still teaches.
2. Fantasy and gaming brands, festivals and night events (light festivals, night markets, zoo night openings): teaser
   and social loops. They pay for a striking, shareable night image.
3. Wellness, sleep and meditation apps: calm looping backgrounds (fireflies, glowing water, slow moon). They pay for
   long, quiet, loopable footage.

## On the seasons loop (23 Oct, Sam's new base)
Board folder `films/cutaway/looks/seasons-night-glow/`, frames 40, 100, 260. What differs from the meadow: the loop's
season materials keep their own colours, dimmed less than the rest (so blossom, green, autumn and snow read under the
moon); the grass tips glow; snowflakes, the ice edge, the frog, the acorns and the fish glow; the loop's haze box is
hidden; the loop re-poses the sun each frame, so this look turns it back into the low cool moon each frame; the title is
pale (no plate on the loop). Rounds (270x480, 8 samples, local): r1 seasons read, but the dark title vanished on the dark
ground; r2 pale title, accepted. 13 to 35 s a frame here at 270x480. Weak spots: the camera looks down, so the night sky
(moon, aurora, stars) is not in this frame: the background is a dark floor; the summer grass tips glow busily.
