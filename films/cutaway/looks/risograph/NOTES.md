# Look board: risograph

2026-10-23. Art direction module: films/styles/cutaway/art/risograph.py (shared helpers: art/_post.py).

## The look
A riso print: pink, teal and yellow spot inks, halftone, misregistration, paper grain.

## What it changes
Compositor: display colours, bolder grade, separation of the picture into three inks by optical density (3x3 matrix solved from ink transmittances), coarse round halftone dots at 15, 75 and 45 degrees, uneven ink laydown, plates a few pixels out of register, multiplied onto grained cream paper. Labels are printed after in one dark ink from their own full-resolution scene.

## Stills runs
Local checks at 640x360, 8 spp on the 2-core chat box (frames 440 and 830). Runner stills at 640x360, 8 spp, frame 830 (tag looks-risograph-r1, rc-render stills run, commit 3bbb164): the three compositor looks and clay finished in about 1 to 2.5 minutes of wall time per run including setup; the compositor (CPU device) works on the runner and matches the local picture. Local seconds per frame at 640x360 on the shared 2-core box were noisy (11 to 100 s, the box was loaded by other builders): papercraft about the reference, pixel and riso about the reference, claymation about 1.3 to 2 times. Round 2 (same day): papercraft cavity colour fixed (posterising crushed dark browns to olive), modules made generic (fallbacks when the engine's sets, overlay or land are missing, for the seasons-loop adapter). Full-size timing is for the Mac render.

## Weak spots
Warm scenes land mostly in pink and yellow, teal only appears in greens and shadows, so the palette is not three balanced inks; halftone eats fine detail and the small things in the soil (eggs) become blobs at phone size; needs full size to judge the dots.

## Three project ideas where this look is the right choice
- Posters, album and festival art, editorial illustration
- cultural institutions and indie publishers
- craft food and drink brands.
