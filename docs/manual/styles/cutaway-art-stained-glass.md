# Cutaway art look: stained-glass (leaded glass window, Art Nouveau, secular)

The frame becomes a window: every surface cut into panes of jewel-coloured translucent glass held by dark lead lines;
the sky a fan of flat panes graded from sapphire to amber with the sun as a leaded rosette. No figures, no religious
symbols. Board sent to Sam on 23 Oct; his pick is pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/stained-glass.py`,
helpers `_jewel.py`.

## What it changes
- Every material: emission glass with procedural cells (panes) and lead lines; colours lead (0.035, 0.035, 0.045), ruby,
  amber, gold, emerald, sapphire, amethyst, teal, opal (constants in the module); each pane varies a little in tint,
  glows brighter at its centre as if lit from behind, with streaks and seed bubbles.
- Cut faces: bands of glass split into long irregular panes, leaded band edges, small round pebble roundels
  (`STRATA_GLASS`).
- World: paned sky, sun rosette (a disc, 20 alternating amber and gold rays, three rings); floor of dark leaded slabs.
- Grass blades and small flowers hidden (as glass they are noise); the turf is green panes.
- Lights: no effect (the glass is emissive). View transform Standard.
- Compositor: lead along every outline (Sobel edge filter on the flat render, thresholded, thickened at full size), a
  soft glow and a vignette; words crisp in their own layer (white plates, lead-black ink).
- On the seasons loop: the season ground (with its snow) cut in large panes; leaves, ice and life are glass in their own
  colours; small things get no inner lead (one tinted pane each, outlined by the edge lead); the ground around the block
  takes the loop's season backdrop colour; the edge lead is masked off the ground, ice, fallen leaves and snowflakes with
  the object index pass (else patchy snow became black scribble); the title is pale glass white, no plate.

## Exact steps (apply it)
1. Line film: `"look": {"art": "stained-glass"}`, or `KF_ART=stained-glass`.
2. Seasons board (exists): `films/cutaway/looks/seasons-stained-glass/`, frames 40, 100, 260 at 270x480, 8 spp.
3. Meadow board (exists): `films/cutaway/looks/stained-glass/`, frames 440 and 830 at 480x270, 8 spp.
4. Full size: Mac lane or rc-render.

## Cost per frame
The cheapest Blender look: emission only, no grass blades, 2 bounces, about 0.3 to 0.5 times the reference plus 1 to 2 s
of compositing at 1280x720. Measured on the shared 2-core box: 18 to 32 s a frame at 480x270, 8 spp; 10 to 19 s on the
seasons loop at 270x480.

## Best uses (from NOTES)
1. Heritage, architecture and craft brands (glass studios, restoration firms, historic hotels): a signature ad.
2. Wineries, breweries, terroir food: a label-like hero frame, also printable as a poster.
3. Cultural seasons and festivals (Art Nouveau exhibitions, anniversaries, light festivals): titles and posters.

## Weak spots
- Procedural object-space panes read a little like mosaic or tiles on the big limestone face.
- The T. rex dig pocket is cut into many small dark panes: bones harder to read.
- Edge lead depends on colour contrast: thin or missing between similar colours.
- Edge lead is recomputed per frame: may flicker on fine detail in motion (not yet tested moving).
- Seasons loop: backdrop panes busy next to the block; spring blossom canopies read as outlined blobs.

## Alternatives
`fable` (paint), `night-glow`, `risograph` (print).

## Checks before showing Sam
Small objects must not turn into black blobs (round 1 problem: lead too thick); look at full size.

## Known traps
Lead far too thick at first (thinned everywhere, larger panes on objects, higher edge threshold, no dilation below full
size). On the loop, mask the edge lead off ground, ice, leaves and snow (close pinholes in the index mask).

## Sources of truth
`films/styles/cutaway/art/stained-glass.py`, `_jewel.py`, `films/cutaway/looks/stained-glass/NOTES.md`,
`films/cutaway/looks/seasons-stained-glass/NOTES.md`. The code wins if they disagree.
