# Look board: stained-glass (leaded glass window, Art Nouveau, secular)

Module: `films/styles/cutaway/art/stained-glass.py` (shared helpers in `films/styles/cutaway/art/_jewel.py`). Folder
made by `python3 films/cutaway/looks/make.py stained-glass`.

## The look
The frame becomes a window. Every surface is cut into panes of jewel-coloured translucent glass (ruby, amber, gold,
emerald, sapphire, amethyst, teal) held by dark lead lines: the cut faces are bands of glass split into long irregular
panes with leaded band edges and small pebble roundels; the sky is a field of flat panes graded from sapphire to amber
with the sun as a leaded rosette (a disc, 20 alternating amber and gold rays, three rings); the land, trees, houses,
finds and animals are panes in their own colour, saturated. Each pane varies a little in tint, glows brighter at its
centre as if lit from behind, with streaks and seed bubbles. The compositor adds lead along every outline (Sobel edge
filter on the flat render, thresholded, thickened at full size), a soft glow and a vignette; the words stay crisp in
their own layer (white plates, lead-black ink). Grass blades and flowers are hidden (as glass they read as noise); the
turf is green panes. No figures, no religious symbols.

## Stills (local, this chat machine, Blender 5.2 bpy CPU)
| Round | Size, samples | Times (frames) | What changed |
| --- | --- | --- | --- |
| t1 | 480x270, 8 | 18.33, 34.58 (440, 830) | first pass: lead far too thick, small objects (trees, chest) turned into black blobs |
| t2 | 480x270, 8 | same | lead thinned everywhere (panes, band edges, sky, sun rays and rings), larger panes on objects, edge filter threshold raised, no dilation below full size, fewer bubbles. Accepted |

Measured on this 2-core shared box at 480x270, 8 samples: 18 to 32 s per frame (other builders rendering at the same
time), the cheapest of the three: emission only, no grass blades, 2 bounces.

Runner stills were not dispatched (this builder does not commit or push); the coordinator renders the board frames.

## Weak spots (honest)
- The panes are procedural cells in object space: on the big limestone face they read a little like a mosaic or tiles
  rather than cut glass designed by hand.
- The dig pocket around the T. rex is cut into many small dark panes; the bones are harder to read than in daylight looks.
- Lead from the edge filter depends on colour contrast, so outlines between similar colours are thinner or missing.
- In motion the object-space panes stay put on the surfaces (good), but the edge-filter lead is recomputed each frame
  and may flicker slightly on fine detail; not yet tested in a moving render.
- Only seen at 480x270 locally.

## Three projects where this look is the right choice
1. Heritage, architecture and craft brands (glass studios, restoration firms, historic hotels): a signature ad or
   social piece in the language of their own windows. They pay for a premium, crafted image.
2. Wineries, breweries and terroir food brands: a label-like hero frame of the land and its layers, also printable as a
   poster. They pay for a look that becomes part of the brand.
3. Cultural seasons and festivals (Art Nouveau exhibitions, city anniversaries, light festivals): title sequences and
   posters. They pay for a striking, period-flavoured identity.

## On the seasons loop (23 Oct, Sam's new base)
Board folder `films/cutaway/looks/seasons-stained-glass/`, frames 40, 100, 260. What differs from the meadow: the loop's
season ground (with its snow) is cut in large glass panes, leaves, ice and life are glass in their own colours; small
things get no inner lead (one tinted pane each, outlined by the compositor's edge lead); grass and flowers are hidden as
on the meadow; the leaded ground around the block takes the loop's season backdrop colour (green, ochre, blue); the edge
lead is masked off the ground, the ice sheet, the fallen leaves and the snowflakes (object index pass), else the patchy
snow turned into black scribble; the title is pale glass white (no plate). Rounds (270x480, 8 samples, local): r1 grey
backdrop, winter top black with lead; r2 seasonal backdrop, light blur before the edge filter; r3 no inner lead on small
things; r4 to r6 edge lead masked off the ground (pinholes in the index mask closed); r7 quieter backdrop, accepted.
10 to 19 s a frame here at 270x480, the cheapest. Weak spots: the backdrop panes are busy next to the block; spring
blossom canopies read as outlined blobs.

Second pass after the coordinator's review (23 Oct): the floor is now large quiet panes, darker and with little tint
variation; the canopies are proper leaf-glass panes (blossom, green, autumn gold) and the edge lead is masked off them
(their cut-out holes had turned them into black blobs); snowflakes are plain white glints with no lead. Round r8,
frames 40, 100, 180, 260, accepted. 25 to 41 s a frame here at 270x480.
