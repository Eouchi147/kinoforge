# Look board: papercraft

2026-10-23. Art direction module: films/styles/cutaway/art/papercraft.py (shared helpers: art/_post.py).

## The look
Layered cut paper, a handmade diorama under a desk lamp.

## What it changes
Flat posterised card colours with paper fibre (colour and bump), strata rebuilt as stacked deckled sheets with a pale torn core and a drop shadow on the sheet below, punched paper dots for pebbles, flat-shaded trees and rocks, one soft warm lamp, cream paper sky, kraft table, eight standing paper ridges behind the block casting real soft shadows.

## Stills runs
Local checks at 640x360, 8 spp on the 2-core chat box (frames 440 and 830). Runner stills at 640x360, 8 spp, frame 830 (tag looks-papercraft-r1, rc-render stills run, commit 3bbb164): the three compositor looks and clay finished in about 1 to 2.5 minutes of wall time per run including setup; the compositor (CPU device) works on the runner and matches the local picture. Local seconds per frame at 640x360 on the shared 2-core box were noisy (11 to 100 s, the box was loaded by other builders): papercraft about the reference, pixel and riso about the reference, claymation about 1.3 to 2 times. Round 2 (same day): papercraft cavity colour fixed (posterising crushed dark browns to olive), modules made generic (fallbacks when the engine's sets, overlay or land are missing, for the seasons-loop adapter). Full-size timing is for the Mac render.

## Weak spots
Grass blades are still real geometry (green but not clearly paper); the egg figures keep their kit shapes (flat colour helps, but they are not cut-outs); the paper edge is a shader effect on a flat face, so at grazing angles it does not catch light like a real sheet edge.

## Three project ideas where this look is the right choice
- Children's book publishers and museum exhibits (how the ground is built, one sheet per era)
- craft and stationery brands (a handmade look for a launch film)
- schools and science channels (geology, history timelines).
