# Look board: pixel

2026-10-23. Art direction module: films/styles/cutaway/art/pixel.py (shared helpers: art/_post.py).

## The look
16-bit game pixel art: 320 x 180 art pixels at 1280 wide, 32-colour palette.

## What it changes
Compositor: render at full size with 6 spp, box-average down by 4, grade, ordered 4x4 Bayer dither, snap to a fixed 32-colour palette through a 16x16x16 colour cube lookup image, dark outlines on brightness jumps, scale up nearest-neighbour. Labels and title come from their own full-resolution scene laid on top, crisp. DOF and shafts off.

## Stills runs
Local checks at 640x360, 8 spp on the 2-core chat box (frames 440 and 830). Runner stills at 640x360, 8 spp, frame 830 (tag looks-pixel-r1, rc-render stills run, commit 3bbb164): the three compositor looks and clay finished in about 1 to 2.5 minutes of wall time per run including setup; the compositor (CPU device) works on the runner and matches the local picture. Local seconds per frame at 640x360 on the shared 2-core box were noisy (11 to 100 s, the box was loaded by other builders): papercraft about the reference, pixel and riso about the reference, claymation about 1.3 to 2 times. Round 2 (same day): papercraft cavity colour fixed (posterising crushed dark browns to olive), modules made generic (fallbacks when the engine's sets, overlay or land are missing, for the seasons-loop adapter). Full-size timing is for the Mac render.

## Weak spots
Fixed palette can turn browns muddy and the dither gives a busy texture on gradients; thin geometry (grass) turns to noise; at runner 640 wide the art is 160 pixels wide, judge at 1280.

## Three project ideas where this look is the right choice
- Game studios and indie game launches (a diorama intro or a level map)
- retro-gaming and developer brands
- educational games, pixel-art explainers for tech and crypto audiences.
