# The Hidden Meadow (Cutaway showcase, film 3)

20 s, 24 fps, 480 frames, 9:16 (render 720x1280, out 1080x1920), 20 spp. Use it shows: wildlife documentary, kids,
nature brands. Files: `blender.py` (the whole scene), `film.json`. Kit: `films/styles/cutaway/cutaway.py` and
`films/styles/cutaway/cinematic/extras.py`, both imported and never edited (the rabbit model is copied into
`blender.py` so its motion can be our own). Free: Blender Cycles, all procedural, no downloaded assets.

## Story (beginning, middle, end)

- **Beginning (0 to 6 s):** a spring meadow in soft morning light, the world above. Two rabbits graze beside their burrow.
- **Middle (6 to 16.4 s):** the hidden world below: the warren, a mole, a fox den with two cubs, the ant nest. Then a
  hawk's shadow sweeps across the meadow; the two rabbits bolt into the burrow and we see them arrive underground.
- **End (16.4 to 20 s):** calm returns (the rabbits below lower their ears) and the camera breathes out to the whole block.

## Shots (and why each cut)

| # | Shot | Time | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | meadow | 0.0 to 6.0 s (frames 0 to 143) | Low three-quarter (az -62 to -57, el 8 to 12, 42 mm, f/6.3), into the side-back sun; a slow push that settles on the burrow mouth at the cut edge | The world above: where we are, who lives here. Title 0 to 2.5 s in the sky. |
| 2 | below | 6.0 to 12.5 s (144 to 299) | Frontal on the -Y cut face (az -82 to -77, el 7 to 5, 40 mm, f/7.1); a slow crane down the column of homes, warren to ants | The reveal. Cut motivated by shot 1 ending on the burrow mouth: we follow it down. |
| 3 | hawk | 12.5 to 20.0 s (300 to 479) | Three-quarter (az -50, el 20, 35 mm, f/8) on the top and the warren together; holds while the shadow passes and the rabbits dive, then from 16.4 s eases out to the whole block (el 23) | The event and the resolution: the cut lands as the shadow reaches the block; one frame holds both the threat above and the shelter below. |

Every move is eased (smoothstep, quintic for the pull back) and slow: 5 to 10 cm per second at block scale.

## Layout of the -Y cut face (one column, made for 9:16)

Face coordinates: u along the face (x), z height (top of the face about 0); the block is 1.6 x 1.6 m, 1.4 m deep.

| Home | Where | What it holds, and what moves |
| --- | --- | --- |
| Warren | mouth at u -0.30 (a notch in the cut edge, the top made transparent there), a run down to chamber A (u -0.12, z -0.23), a link to chamber B (u -0.34, z -0.37) | B: a doe and two kits on straw, breathing, ears twitching, sniffing; they look up at the hawk (13.05 s) and relax (16.4 s). A: empty straw until the two runners arrive. |
| Mole | tunnel u 0.07 to 0.37 just under the turf (z about -0.1), nest at its end, molehill on top | extras `Eggs.mole`: paws dig, nose twitches. |
| Fox den | den at u 0.12, z -0.57; its run climbs to a second notch at u 0.60 | one cub asleep curled nose to tail (breathing, an ear flick); one cub playing: play bow, pounce, back, every 2.6 s, tail wagging; a bone. |
| Ant nest | entrance at u -0.56 (small notch, anthill clods), one gallery down through four chambers (z -0.74 to -1.0) | 24 ants walk the gallery floor (down with a green leaf bit, up empty); the queen (pulsing), a pile of eggs, a leaf store. Nine more ants carry leaves across the top to the entrance. |

Burrows are hollows, not booleans: the wall material is transparent over each opening (extras `Eggs` masks) and a
half-tube or bowl closes it from inside. Our own cavity material darkens with depth into the block, so a tunnel reads
as a hole and not as a pipe. Each home has a soft warm museum spot and tiny glow lights along the runs.

## Easter eggs (deep time below the homes, museum-lit)

- -Y face: an **ammonite** (limestone, u 0.30, z -1.11), a **trilobite** (u -0.36, z -1.19), a cracked **geode** at the bottom (u 0.02, z -1.29).
- +X face: a **hedgehog** asleep in a leaf-lined burrow under the turf (it breathes), a lost **amphora** (z -0.62), a second **geode** (z -1.18).

## Life (at least three layers of motion in every shot)

- Top: grass and flowers in the travelling wind (kit), 7 bees (wings at 23 Hz, figure-eight flights), 3 butterflies,
  24 petals and leaves drifting, 46 pollen motes in the sun (camera only), the two rabbits grazing (head down nibbling,
  sniffing), 9 ants on a trail, 3 birds circling far off, god-ray cards shimmering (extras `Shafts`).
- Below: mole digging, ants marching, cubs (sleep and play), doe and kits breathing and twitching, the hedgehog breathing.
- Air: three haze cards behind the block drift (no volumes anywhere).

## Light and look

Morning sun from the side-back (az 158, el 27, warm 1.0/0.82/0.62, strength 7), weak cool fill (0.42) and sky ambient
(0.17) so the sun dominates the top and the hawk's shadow reads; warm rim; extras golden sky dome (bluer zenith for
spring); warm spill on the cut edges; museum spots underground. Compositor bloom and vignette (extras `finish`).
AgX Medium High Contrast, exposure +0.25. The title "The Hidden Meadow" is a Blender text object in Archivo
(`ads/fonts/Archivo.ttf`), emission, parented to the camera at the focus distance (sharp under depth of field), in the
sky in the upper third, fading in 0.25 to 0.85 s and out 1.85 to 2.5 s. Nothing else is written on screen.

The hawk itself is never seen: a flat horizontal silhouette (wings, tail, 0.75 m span) 0.85 m above the meadow toward
the sun, seen by shadow rays only. Projection between horizontal planes is a translation, so the shadow keeps the true
shape. Measured: dense backlit grass hides a real shadow (only about a quarter of the grass brightness is direct sun; the
rest is fill, bounce and translucency), so the shadow is also art-directed: the same silhouette laid over the grass
tips (8 cm) as two soft dark veils (a wide faint one, a tighter darker one), exactly where the sun would throw it at
that height, fading out near the cut edges and on the far and left sides so it never hangs in the air. It crosses the hawk shot's frame from right
to left (heading -0.77, -0.64; 1.1 m/s) and passes over the grazing spot at 14.0 s.

## Events for the sound designer

| time (s) | event | sound idea |
| --- | --- | --- |
| 0.0 to 12.5 | meadow morning: wind in grass, birds far off | birdsong bed, light wind, crickets |
| 0.0 to 6.0 | bees cross the meadow close to camera (7 bees all along) | bumblebee passes, one near 2.6 s |
| 0.25 to 2.5 | title fades in and out | (nothing; keep it nature only) |
| 6.0 | cut below the surface | everything above muffles (low-pass), close earthy room tone |
| 6.0 to 11.0 | mole digging (paw strokes at about 2.2 per second) in the top right | soft soil scratching, small dirt trickles |
| 6.11, 8.71, 11.31 | fox cub pounces (take-off); lands at 6.68, 9.28, 11.88 | tiny soft thump on straw, rustle |
| 7.5 to 12.5 | ants marching in the gallery (the crane reaches them) | very faint ticking or scratching |
| 12.5 | cut to the hawk shot; the shadow enters the block on the right (12.5 to 12.7) | birdsong stops, a hush |
| 13.08 to 14.32 | two slow wing beats overhead (the hawk is never seen) | large wings, a whoosh, distant hawk cry optional (bank has none) |
| 13.25 | the two rabbits on top look up | (silence) |
| 13.45 / 13.63 | rabbit 1 / rabbit 2 bolt for the burrow | quick thumps on turf |
| 13.86 / 14.07 | rabbit 1 / rabbit 2 drop into the burrow mouth | soft dirt scuffle |
| 13.9 to 14.15 | the shadow sweeps over the two grazing spots, just as the rabbits vanish | wind gust |
| 14.3 to 14.6 | the shadow leaves the block at the front left | |
| 15.10 / 15.38 | rabbit 1 / rabbit 2 arrive in chamber A and stop | muffled scrabble, then stillness |
| 16.4 | calm returns: rabbits below lower their ears; the camera begins its pull back | birdsong returns, wind |
| 16.4 to 20.0 | slow pull back to the whole block | bed swells gently to the end |

## Render cost

Measured on Sam's Mac lane (Apple M4 GPU, METAL), 720x1280, 20 spp, adaptive (threshold 0.04), OIDN denoise, 4 bounces,
no volumes, no motion blur, from the check logs (the `s/frame` line of each one-frame job):

| Round | Frames | s/frame |
| --- | --- | --- |
| 1 | 24, 336 | 4.8, 5.8 |
| 2 | 24, 200, 318, 336, 372, 470 | 4.6, 6.9, 6.0, 5.6, 5.6, 6.3 |
| 3 (Mac busy) | 24, 130, 250, 324, 372, 479 | 15.0, 14.8, 19.6, 14.5, 15.1, 21.0 |
| 4 (Mac busy) | 200, 312, 330, 342, 479 | 15.1, 12.5, 12.0, 17.0, 14.8 |
| 5 (Mac busy) | 330, 336 (final shadow check) | 13.8, 13.5 |

Rounds 1 and 2 ran on an idle lane (scene build 6 s): **about 5 to 7 s per frame**, so 480 frames take about 45 to 55
minutes. In rounds 3 and 4 the lead's film chunks were rendering on the same Mac at the same time (scene build went
from 6 s to 25 s, so the machine was shared, not the scene heavier: the changes between rounds were a few cards,
lights and materials): 12 to 21 s per frame. Build about 25 s on the 2-core chat box.

## Weak spots (honest)

- **The hawk shadow is half real, half art-directed** (see Light and look). In motion it reads as a dark shape sweeping
  over the meadow; in a single still it is soft, not a crisp silhouette.
- **Storybook scale:** rabbits (2.35x the extras model), cubs, ants (1.6x) and bees are oversized for a 1.6 m block so
  they read at phone size. The ants are about 2 cm long and read as moving dark dots with green leaf bits at 1080 px.
- **Rabbits in motion** are rigid models that hop and pitch along their run; the dive down the burrow is a quick
  head-first slide, not an animated run cycle.
- **Tunnels** are half tubes with a depth-shaded earth material: they read as hollows, but at the rim a thin highlight
  shows where the tube meets the face (the extras hole masks are hard-edged).
- **Trees** are the kit's lumpy-blob miniatures (one pink-blossom tree from the spring palette); they read as a diorama.
- **Plain strata:** the sand band between the fox den and the ants is a large plain area in the crane shot.

## Log

- 2026-10-23 (overnight build): first build, five check rounds on the Mac lane, local 270 to 405 px checks on the
  chat box; changes: burrows depth-shaded (read as hollows), side-back sun with weak fill so the top is
  sun-lit, art-directed hawk shadow veils on a right-to-left crossing (sitting in the grass, faded on the far and left
  edges so they never float), round trees, brighter ant nest, pebbles in the loam and sand, final framing clear of the
  frame edge. Cost: nothing (Mac lane and chat box). Best stills: `out/hidden-meadow-check4/frames/00200.png` (the
  hidden world) and `out/hidden-meadow-check3/frames/00130.png` (the meadow) in the Mac's `kinoforge-render` folder.
