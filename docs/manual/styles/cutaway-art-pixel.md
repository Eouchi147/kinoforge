# Cutaway art look: pixel (16-bit game pixel art)

The Cutaway block as a pixel-art diorama: the world rendered at a quarter size (320 x 180 art pixels at 1280 wide), an
ordered Bayer dither, snapped to a fixed 32-colour palette, dark outlines, scaled up nearest-neighbour; labels and title
crisp at full resolution on top. Board sent to Sam on 23 Oct; his pick is pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/pixel.py`, helpers
`_post.py` (`Comp`, `split_overlay`, `array_image`).

## What it changes
- Render: the world renders at full size with samples capped at 6 (`min(samples, 6)`: 16 rendered pixels are averaged
  into one art pixel). The art is `ART_W = 320` pixels wide (180 high in 16:9): `SCALE = round(W / 320)`, 4 at 1280 wide.
  (The module docstring still says the world is rendered small; the code and NOTES render full size and average down.)
- Compositor (CPU): flat blur of SCALE/2 and bilinear scale down by SCALE (box average), display colours (AgX Medium High
  Contrast, exposure + 0.55), saturation 1.4, ordered 4 x 4 Bayer dither (amplitude 0.055), snap every pixel to the fixed
  32-colour `PALETTE` through a 16 x 16 x 16 colour-cube lookup image (`LV = 16`, Map UV, nearest), dark outlines where
  a Sobel filter on lightness passes 0.34, nearest-neighbour scale up.
- Words: `split_overlay` moves labels, leaders and title into a second scene rendered at full resolution on a
  transparent film and laid over the pixels, crisp.
- Depth of field, god rays and golden fog off; one world tint. Materials untouched (the palette does the styling).

## Exact steps (apply it)
1. Line film: `"look": {"art": "pixel"}`, or `KF_ART=pixel`.
2. Seasons board (exists): `films/cutaway/looks/seasons-pixel/`.
3. Meadow board (exists): `films/cutaway/looks/pixel/`; local 640x360, 8 spp, frames 440 and 830.
4. Runner still: `stills.yml` tag `looks-pixel-r1` (frame 830, 640x360, 8 spp, commit 3bbb164). Judge at 1280 wide or more:
   at 640 the art is only 160 pixels wide.

## Cost per frame
The docstring's estimate (a quarter to a third of the reference) assumed a small render; the code renders full size at
6 spp or fewer, which the NOTES measured as "about the reference" on the noisy shared 2-core box, plus a few seconds for
the full-size words scene. Runner still at 640x360: about 1 to 2.5 min per run including setup.

## Best uses (from NOTES)
Game studios and indie launches (a diorama intro or level map); retro-gaming and developer brands; educational games,
pixel-art explainers for tech audiences.

## Weak spots
The fixed palette can turn browns muddy; the dither is busy on gradients; thin geometry (grass) turns to noise; judge
at 1280 or larger.

## Alternatives
`flat-vector` (clean 2D, faster still), `risograph` (another print-like reduction).

## Checks before showing Sam
Labels crisp and unpixelated; no dither crawl that reads as noise in motion (not recorded as tested in motion).

## Known traps
Run the compositor on CPU (runners have no GPU); the words must come from the second scene, never from the pixelated
render.

## Sources of truth
`films/styles/cutaway/art/pixel.py`, `_post.py`, `films/cutaway/looks/pixel/NOTES.md`. The code wins if they disagree.
