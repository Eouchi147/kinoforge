# Cutaway, cinematic hero version (style comparison)

Sam, 22 Oct 12:01: keep the cross-section worlds, but lift them with cinema lighting, haze, fog and god rays, living
animals and plants, easter eggs in the soil, and interesting camera angles. This folder is the comparison piece. It
uses the D look's river village and imports the kit (`../cutaway.py`, never edited). Everything new is in `extras.py`,
which other films can reuse. Free: Blender 5.2.2 Cycles CPU, all procedural, no downloaded assets (so no CREDITS file).

| File | What it is |
| --- | --- |
| `film.json` | id `style-cutaway-cinematic`, 12 s, 24 fps, 1280x720 render, 1920x1080 out, 64 spp, no audio |
| `blender.py` | the scene: layout, eggs, animals, the five shots (SHOTS timeline), per-shot camera, lens, focus and shaft gain |
| `extras.py` | reusable additions: `cine_light`, `atmosphere`, `gobo`, `Shafts`, `finish`, `ShotCam`, `Face`, `Eggs` (holes + 10 eggs), animals |
| `board/` | the five stills at 1920x1080 (jpg q90) |

## The five angles (one job each)

The film is the five angles in story order. Each check-still frame lands on one angle.

| # | Shot | Time (frames) | Still | Job |
| --- | --- | --- | --- | --- |
| 1 | map | 0 to 2 s (0-47) | 24 | Top-down map with a slow drift and turn. Long shadows, fog in the valley. Job: where we are (understanding). |
| 2 | ground | 2 to 4.5 s (48-107) | 84 | Low at the block's edge, looking along the cut face into the sun, f/4. The face recedes with its lit eggs, past the grass, trees, a lit cottage and the sun. Job: arrival, scale, a living world. |
| 3 | crane | 4.5 to 8 s (108-191) | 150 (also 112, 186) | Slow vertical crane down the -Y cut face, from the treetops and the river glass with its fish to the gold vein. The eggs appear one by one. Job: the reveal (the layers read as time). This is the motion test. |
| 4 | macro | 8 to 10 s (192-239) | 222 | Close on the T. rex skull, 55 mm, f/4, with a slow push. Pebbles go to bokeh. Job: the payoff (the smile). |
| 5 | hero | 10 to 12 s (240-287) | 270 | Low three-quarter, 28 mm, the sun behind the block. The camera arcs 8 degrees, so the sun slides behind the big tree by the mill and rays burst round its crown. Job: the closing image (the whole world, rim-lit). |

Shots run 1.5 to 3.5 s because this is a style reel. A real film would hold each idea longer (CRAFT section 2).

## Lighting recipe (`cine_light`, `atmosphere`, `gobo`, `Shafts`, `finish`)

- **Key:** a warm sun (1.0, 0.66, 0.38), strength 6, angle 1.2 degrees for crisp shadows. It sits at az 135, el 11, behind the block from every camera angle. The tops are lit and rim-lit, the grass glows through, and shadows run long toward the camera.
- **Fill:** both camera-facing cut faces are in cool shade. A large cool disk area light on the camera side (power 0.6 x 900 W) and a dim blue sky ambient (0.2) keep the strata readable.
- **Rim:** a warm area light at sun az + 62 degrees separates the block edges from the background.
- **Museum lights:** each egg has its own warm spot (2 to 5 W, 30 to 50 degree cone, soft blend) set 0.4 to 0.75 m out from the face. That puts a soft pool of light on each surprise. The geode, the mole's nest and the tunnel also get tiny glow lights.
- **Sky:** camera rays see a golden-hour dome (orange horizon toward the sun, lilac away, deep blue zenith, a sun disc and halo). Other rays see only a dim cool ambient. The floor fades into the horizon colour with distance, so there is no hard edge.
- **Atmosphere:** one bounded volume box over the block (footprint plus 0.5 m, up to 1.6 m), forward scattering (anisotropy 0.7), single scatter (volume bounces 0), biased ray marching (step rate 4, 256 max steps). It holds:
  - thin haze (0.12) that thins with height and fades past the edges;
  - ground fog that pools in the low ground and the river valley;
  - a thin mist layer right on the water.

  Fog and mist are broken up by drifting 4D noise (wind 3.5 cm/s, deterministic in t) and stay on the block (they spill 3 cm over the edge).
- **God rays (hybrid):** the real volume gives depth and glow. On its own it gave no readable shafts: at density 0.6 it turned into a white fog bank, and with a low sun most of the volume is lit. The readable rays are art-directed shaft cards (`Shafts`): additive emission strips along the sunlight, billboarded to the camera around their own axis every frame, brightest when the camera looks toward the sun. Dust breakup and shimmer drift with t. They are invisible to every ray except the camera's. There are two sets:
  - 12 canopy beams that land on the grass through the trees;
  - 10 beams grazing the crown of the hero tree, placed by `Shafts.around`. The hero camera's arc was chosen so this crown passes in front of the sun.

  The gain is set per shot: map 0.35, ground 1, crane 0.8, macro 0, hero 1.
- **Cloud gaps:** `gobo` is a shadow-only cloud card between the sun and the block, invisible to the camera. Its gaps dapple the top and the haze, and the pattern drifts.
- **Finish:** AgX High Contrast, exposure 0.1. Compositor bloom (threshold 1.2, strength 0.22) on the water glints, lit windows, gold and the sun, plus a gentle vignette (0.26). Depth of field is set per shot (7 blades).

## Easter eggs (placed by depth: recent at the top, deep time at the bottom)

-Y face (the crane column, left to right and top to bottom):
1. **Mole in its tunnel** (just under the turf). A winding tunnel ends in a round nest of straw with a warm glow. The mole digs (its pink paws turn) and twitches its nose. A molehill sits on the turf above.
2. **Pirate chest** (clay, about 0.3 m down). The lid is ajar, gold glows inside, and coins spill down through the soil.
3. **Roman amphora** (loam, about 0.45 m down). It lies tilted, with two shards and green bronze coins by its mouth.
4. **Ammonite** (top of the shale band). A ribbed spiral with a nacre (thin-film) sheen.
5. **T. rex skeleton** (shale, about 1 m down). Head thrown back in the classic fossil pose, with ribs, neural spines, a sprawled leg and the tiny arms. The skull has teeth, an eye socket and windows.
6. **Trilobite** (chalk band, about 1.24 m down). Head shield, a three-lobed segmented thorax, eyes.
7. **Gold vein** (deep rock, about 1.4 m down). A quartz vein crosses the face with gold nuggets standing proud and glinting flecks.

+X face (seen in the hero and map angles):
8. **Hedgehog** asleep in a leaf-lined burrow just under the turf. It breathes.
9. **Ancient well.** A masonry shaft cut in half by the face, running from the turf down to dark water, with a bucket on its rope swaying. The stone ring and a little roof sit on top.
10. **Geode** cracked open in the deep rock: a pale agate rim and glowing amethyst points.

Hollows (the mole tunnel and nest, the burrow, the well, the geode) use no booleans. The wall material is made
transparent over each opening by a shader mask in face coordinates, and a bowl or half-tube mesh closes the hole from
inside. This is cheap, and the cut stays perfectly clean.

## Life (all deterministic in t)

- **Wind:** the kit's travelling gusts move the grass, flowers, reeds and trees (sway raised to 1.45).
- **Deer:** a roe deer and a fawn graze, then lift their heads at 5.4 s and 6.6 s (ears flick, a look around) and lower them again.
- **Rabbits:** two hop along paths: a hop, then sit and sniff.
- **Fox:** a red fox trots along the east meadow, legs in diagonal pairs, its bushy tail floating.
- **Heron:** stands in the shallows by the cut face, turns its head and strikes once at 7.2 s, with ring ripples.
- **Ducks:** three mallards paddle down the river, bobbing, each with ring ripples.
- **Fish:** five swim loops in the river right behind the glass cut face, tails beating.
- **Small life:** 28 fireflies blink low over the banks, 44 petals and leaves tumble on the wind, three butterflies wander over the flowers, and four birds circle.
- **Moving light:** the mill wheel turns, the cloud gaps drift and the fog drifts.

## Render cost

(Measured numbers are filled in from the stills runs below.)

- **Scene build:** 4 to 8 s.
- **Local previews** on the 2-core chat box (shared, loaded), 480x270 at 16 spp: 15 to 45 s a frame. Volumes add about 30 %.
- **Runner stills:** see the run log at the end of this file.

## Weak spots (honest)

- **Shafts:** the god rays are cards. They read best in the hero and ground angles (looking toward the sun). From the side they are faint, and from top-down they are mostly hidden on purpose. The real volume adds depth but does not make crisp shafts by itself at this cost.
- **Animal scale:** the animals are storybook-sized, larger than the houses imply, so they read at phone size. The deer are about 10 cm tall on a 4 m block. They are made of primitives (ellipsoids and tubes): clean silhouettes, but not sculpted.
- **Readability at hero scale:** the eggs are oversized for readability (a 0.85 m T. rex next to 0.2 m cottages). At the hero distance they read as glowing shapes. They read clearly in the crane and macro angles.
- **The skull** is stylized: a lofted wedge with dark windows and cone teeth. It reads as a "dinosaur skull" in a friendly, toy-like way, not as a museum cast.
- **Hollow edges:** the hole masks are hard-edged. At extreme close range, a thin highlight line can show where a tunnel wall meets the face.
- **The ground shot** puts the near cut face out of focus by design. Its eggs read as warm glows, not as objects.
- **The map shot's** dark floor shows around the block, and the fog is subtle from straight above.
