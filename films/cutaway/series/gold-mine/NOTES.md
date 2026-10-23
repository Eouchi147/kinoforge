# The Gold Mine (Cutaway showcase, film 5)

Use it shows: history, adventure, games, mining and construction. 9:16, 20 s, 24 fps (480 frames), rendered 720x1280,
delivered 1080x1920. Night. Blender Cycles with the Cutaway kit (`films/styles/cutaway/cutaway.py`) and the cinematic
extras (`films/styles/cutaway/cinematic/extras.py`), both imported and never edited. Everything new is in `blender.py`.
All procedural, no downloaded assets, no paid calls.

## Story (beginning, middle, end)

- **Beginning:** a rocky mountain at night under stars and a big moon, pines on its flanks. A miner with a lantern
  crosses the yard and walks into the timber mine entrance. Inside the cut face, lanterns glow in the galleries.
- **Middle:** the camera cranes down the cut face: an ore cart rolls on rails, a miner climbs down the ladder shaft, two
  diggers swing picks, and at the deepest gallery a miner strikes the gold vein three times. The third blow throws
  sparks and the gold flares.
- **End:** the ring of the strike wakes the bat colony in the cave below. The bats drop from the ceiling and burst out
  toward the camera. Cut outside: bats pour out of the entrance and rise over the ridge toward the moon as the camera
  pulls back to the whole lit mountain.

## Shots (and the reason for each cut)

| # | Shot | Time | Frames | Camera | Job |
| --- | --- | --- | --- | --- | --- |
| 1 | night | 0 to 6 s | 0-143 | three-quarter from the front-right (az -60 to -54), 35 mm, slow eased push from 6.9 m to 5.0 m toward the entrance | where we are: the mountain, the night, the hidden mine. Title on screen 0.25 to 2.5 s |
| 2 | descent | 6 to 14 s | 144-335 | square to the -Y cut face, 32 mm; eased crane (ease5) from the top gallery down the shaft to the deepest gallery (6.0 to 10.5 s), then a slow push in (10.5 to 14 s) | the work and the strike, then the bats |
| 3 | flight | 14 to 20 s | 336-479 | low by the yard, looking at the entrance with the moon above (az -112), 30 mm; eased rise and pull back to the whole mountain | the bats leave; the closing image |

- Cut 1 to 2 (6.0 s): the push in shot 1 runs toward the entrance the miner just entered, so the cut follows him inside.
- Cut 2 to 3 (14.0 s): the bats have just flown out of the cave toward the camera; the cut shows where they go (out of
  the entrance, 0.15 s after the cut).
- The moon is set at infinity per shot (40 m from the camera along a fixed direction), so camera moves never slide it.

## Every element and its job

| Element | Job |
| --- | --- |
| Mountain block (2.6 x 2.6 m, 2.2 m deep, summit 1.2 m) | the place; tall for 9:16. A flat yard at the front-left for the entrance |
| Strata: turf, scree, slate, quartzite, schist, bedrock (cold blue-greys) | cold rock against the warm lanterns; `rock_face` adds mottling and sparse fractures so it reads as hard rock |
| Pines (30, kit cone trees), sparse alpine grass, a few boulders | the mountain's skin; they sway in the kit wind (ambient motion) |
| Moon disc, halo and three drifting cloud wisps | the night's light source and the end point of the bats' flight; clouds drift (ambient motion) |
| Stars (one-pixel points, twinkling) and two bands of far ridges | night and depth |
| Moonlight (sun from behind-left), cool fill, two raking cool lights along the cut faces | rim on peak and pines; texture on the faces |
| Entrance: timber frame, plank roof, lantern on a post, rails out onto the yard | the way in (beginning) and the way out (end) |
| Three galleries (box interiors behind capsule openings), timber sets every 20 cm, a cribbed ladder shaft | the mine as a readable cross-section |
| Lanterns (10, warm point lights, each flickering on its own) | warm against cold; ambient motion in every shot |
| Ore cart (rolls 1.5 to 10.5 s, wheels turn) and its pusher | the work |
| Climber on the ladder (5.6 to 12.6 s, 18 rungs) | links the levels; leads the eye down during the crane |
| Two diggers in the middle gallery (never in step) | the work goes on everywhere |
| Gold miner, gold vein with nuggets, gold in the gallery's end wall, sparks, gold flash light | the climax |
| Cave: lumpy hollow, 22 stalactites, a clear pool, two lanterns | where the bats live; the pool is a glass section (light reaches its bed) |
| 14 cave bats, 34 bats outside | the consequence and the ending |

## Easter eggs (each under a small museum spot)

1. **The miners' canary** in its brass cage, hung in the top gallery by the entrance; it hops from side to side.
2. **An old strongbox** half buried in the scree left of the middle gallery, lid ajar, coins spilling down (kit chest).
3. **Ammonite** in the slate right of the shaft (-Y face) and a second one on the +X face.
4. **Trilobite** in the schist left of the deepest gallery.
5. **Geodes** with glowing amethyst in the bedrock, one on each face.
6. **The gold vein** runs on from the gallery's end wall down the face, quartz with 24 nuggets.

## Ambient motion per shot (at least three layers each)

- night: pines sway, stars twinkle, cloud wisps drift past the moon, lanterns flicker, the walker walks, the cart rolls
  inside the face, the canary hops.
- descent: lanterns flicker (and sway slightly), cart rolls, climber climbs, diggers swing, gold miner swings, pool
  ripples, sparks, bats shiver and then fly.
- flight: bats stream out and rise, stars twinkle, clouds drift, pines sway, lanterns flicker.

## Events for the sound designer

All times in seconds from the start of the film. Sound: real nature recordings and real foley only (BigSoundBank CC0),
no music, no voice.

| time (s) | event | sound idea |
| --- | --- | --- |
| 0.0 to 6.0 | night on the mountain, wide | soft mountain wind in pines, distant crickets; an owl once around 2.0 |
| 0.6 to 5.4 | miner walks across the gravel yard into the entrance | slow footsteps on gravel, a lantern handle creaking |
| 1.5 to 10.5 | ore cart rolls along the top gallery | iron wheels on rails, low rumble (muffled until 6.0, close after) ; a soft clunk when it stops at 10.5 |
| 6.0 | cut inside the mountain | wind drops away; cave room tone, water drips (every 1 to 2 s) |
| 6.05, 7.2, 8.35, 9.5, 10.65, 11.8, 12.95 | digger 1 pick blows (middle gallery) | pick on rock, medium distance |
| 6.45, 7.85, 9.25, 10.65, 12.05, 13.45 | digger 2 pick blows | pick on rock, a little further away |
| 5.6 to 12.6 | climber goes down the ladder (a rung about every 0.39 s) | wooden ladder creaks, soft boot steps |
| 8.6, 9.8 | gold miner's first two blows (small sparks) | pick on hard quartz, a bright click |
| 11.0 | third blow: big spark burst, the gold flares | pick on quartz with a ring, a tiny scatter of falling chips |
| 11.0 to 11.45 | the bats shiver on the cave ceiling | faint leathery rustle |
| 11.45 to 14.0 | the bats drop and burst out toward the camera | sudden flutter of many wings, squeaks, a whoosh as they pass the lens around 12.5 to 13.5 |
| 14.0 | cut outside | night wind returns |
| 14.15 to 17.9 | 34 bats pour out of the entrance (one every 0.11 s) | dense wing flutter near the entrance, thinning |
| 15.0 to 20.0 | the bats rise over the ridge toward the moon | flutter fading into the wind; crickets |
| 20.0 | end | let the wind ring out (no hard stop) |

## Render cost (measured on Sam's Mac, M4 GPU, METAL, 720x1280, 20 spp)

MEASURE_PLACEHOLDER

Settings: 20 spp, adaptive (threshold 0.04), OIDN denoise, max bounces 4 (diffuse 1, glossy 1, transmission 4), no
volumes (fog and haze are cards), no motion blur, compositor bloom and vignette.

## Check stills

Mac lane rounds `out/gold-mine-check1..3` (on Sam's Mac, `Video Production/kinoforge-render/out/`).

## Weak spots (honest)

WEAK_PLACEHOLDER
