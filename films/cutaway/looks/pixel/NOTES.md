# Look board: pixel

2026-10-23. Art direction module: films/styles/cutaway/art/pixel.py (shared helpers: art/_post.py).

## The look
16-bit game pixel art: 320 x 180 art pixels at 1280 wide, 32-colour palette.

## What it changes
Compositor: render at full size with 6 spp, box-average down by 4, grade, ordered 4x4 Bayer dither, snap to a fixed 32-colour palette through a 16x16x16 colour cube lookup image, dark outlines on brightness jumps, scale up nearest-neighbour. Labels and title come from their own full-resolution scene laid on top, crisp. DOF and shafts off.

## Stills runs
Local checks at 640x360, 8 spp on the 2-core chat box (frames 440 and 830). Runner stills and seconds per frame: see the lines added below as runs finish.

## Weak spots
Fixed palette can turn browns muddy and the dither gives a busy texture on gradients; thin geometry (grass) turns to noise; at runner 640 wide the art is 160 pixels wide, judge at 1280.

## Three project ideas where this look is the right choice
- Game studios and indie game launches (a diorama intro or a level map)
- retro-gaming and developer brands
- educational games, pixel-art explainers for tech and crypto audiences.
