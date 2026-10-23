# Look board: claymation

2026-10-23. Art direction module: films/styles/cutaway/art/claymation.py (shared helpers: art/_post.py).

## The look
Plasticine stop-motion: the whole block sculpted in clay.

## What it changes
Every material becomes saturated waxy clay with subsurface, lumps, fingerprints (voronoi thumb rings) and tool-mark grooves as bump; real lumpy displacement on leaf masses and rocks; painted turquoise to cream cyclorama; clay baseboard; softer bigger lamp; animation stepped on twos (12 poses a second) with the texture boiling a hair between poses.

## Stills runs
Local checks at 640x360, 8 spp on the 2-core chat box (frames 440 and 830). Runner stills at 640x360, 8 spp, frame 830 (tag looks-claymation-r1, rc-render stills run, commit 3bbb164): the three compositor looks and clay finished in about 1 to 2.5 minutes of wall time per run including setup; the compositor (CPU device) works on the runner and matches the local picture. Local seconds per frame at 640x360 on the shared 2-core box were noisy (11 to 100 s, the box was loaded by other builders): papercraft about the reference, pixel and riso about the reference, claymation about 1.3 to 2 times. Round 2 (same day): papercraft cavity colour fixed (posterising crushed dark browns to olive), modules made generic (fallbacks when the engine's sets, overlay or land are missing, for the seasons-loop adapter). Full-size timing is for the Mac render.

## Weak spots
Grass and fine geometry stay thin and clean, so the clay feel lives mostly in surfaces; the pepper-dot look on the lower strata comes from pebbles plus tool marks and can look dirty; subsurface and bump make it the slowest look.

## Three project ideas where this look is the right choice
- Family and kids brands, toy and food brands wanting a handmade warmth
- museum and children's TV explainers
- a brand mascot short where the clay look carries the personality.
