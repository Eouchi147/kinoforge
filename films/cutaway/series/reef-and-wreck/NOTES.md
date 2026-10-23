# Reef and Wreck (Cutaway showcase, film 4)

Use it shows: ocean, travel, adventure, tourism. 20 s, 16:9, 24 fps (480 frames), 1280x720 render, 1920x1080 out, 20 spp.
Kit: `films/styles/cutaway/cutaway.py` and `cinematic/extras.py`, imported and never edited. Everything new is in
`blender.py` (rays, palms, boat, wreck, chest, school, turtle, anemones, sea fans, diver, splash, title).

## Story (beginning, middle, end)

A little tropical island sits on a block that is mostly clear turquoise sea, cut open on two glass faces.
- **Beginning:** a diver sits on the gunwale of a small boat, then rolls back into the sea.
- **Middle:** she sinks past light rays and the reef. A school of fish turns together, and a sea turtle glides across.
- **End:** she reaches the sunken ship, hovers over its open chest, and her torch finds the gold.

## Shots (each cut has a reason)

| # | Shot | Time | Frames | Camera | Job |
| --- | --- | --- | --- | --- | --- |
| 1 | arrive | 0.0 to 7.0 s | 0-167 | Wide three-quarter at 40 mm and f/16, with a slow push (8.9 to 8.0 m) and a 7 degree arc | Where we are: the island, the boat and the whole sea cut open. The title shows here. The diver's roll-off (4.8 to 5.7 s) is the inciting moment. |
| 2 | descent | 7.0 to 13.5 s | 168-323 | Outside the -Y glass at 30 mm and f/6. The camera sinks with the diver, lagging her by about 0.3 s, from a split view (the boat's hull above, the reef below) to the reef floor. | Cut on motion: she is already under water, so we go under with her. The journey: rays, the school turning, the turtle crossing in front. |
| 3 | wreck | 13.5 to 20.0 s | 324-479 | Close at sand level through the -Y glass at 38 mm and f/5, with a slow push of 0.22 m | Cut when she nears the sea bed, to the reward: the broken hull, the chest by the bow, gold on the sand, the amphora egg in the rock below. She arrives, hovers and reaches out. The torch lights the gold, which glows (16.6 s on). Final image. |

## Elements and their jobs

- **Island:** a sand beach ring, grass, five palms whose fronds sway in gusts, three gulls circling. It says "tropical" and "travel" at a glance.
- **Boat:** a white dinghy with a blue rim, a bench and an oar. It bobs and rolls on the swell, with ring ripples. It is the diver's start and the surface landmark seen from below in shot 2.
- **Sea:** the kit's calm glass water, with tint (0.20, 0.80, 0.84), density 1.05 (glass clear) and glow 0.035. The pale sand bed carries strong soft caustics (0.9) that drift with t. A 0.65 m shelf slopes from the island to the floor 0.85 m down.
- **Light rays (`Rays`):** 22 soft additive cards from the surface down along the sunlight (sun az 135, el 52). They are billboarded to the camera about their own axis and shimmer with drifting dust. They are visible to camera and transmission rays only, so they show through the glass. Gain is set per shot (arrive 0.25, descent 1.7, wreck 1.2). From above they read as streaks, so they are kept low there.
- **Reef:**
  - 80 kit corals, 44 swaying anemones in 4 colours, 12 branching sea fans and 22 reef rocks.
  - They grow densest on the island slope and toward the near (+X, -Y) corner.
  - The wreck site and the diver's column stay open sand, so the story reads.
- **School:** 34 silver-blue fish with yellow tails circle the middle of the sea. At 10.2 s they turn together: each fish flips 180 degrees over 0.9 s, delayed by its place in the school, so the turn ripples through it. Their tails beat faster during the turn.
- **Turtle:** it glides the whole film along the -Y glass, 0.25 m behind it, from right to left (x 1.75 to -1.4). It has slow 2.6 s strokes of its long fore-flippers, small rear flippers, a scute-patterned shell and a small bob. It crosses in front of the camera in shot 2.
- **Reef fish:** 5 fish loop near the reef corner (the kit's `ex.fish`).
- **Diver:** black suit, yellow tank and fins, a mask, a regulator and a torch. The sequence:
  1. She sits on the gunwale with her back to the sea.
  2. She rolls back 2.5 rad into the water (4.8 to 5.7 s).
  3. She blends into a head-first descent along a smooth path, kicking her fins.
  4. She hovers 10 cm over the sand by the chest from 15.9 s.
  5. Her torch arm reaches toward the gold from 16.5 s.

  Bubble puffs leave her regulator every 1.6 s, rise, wobble and vanish at the surface. The splash at 5.35 s throws 18 droplets and leaves ring ripples. The torch is a spot light that switches on as she goes under.
- **Wreck:**
  - A 1.05 m wooden hull (a ship, so oversized next to the diver, like the eggs in the cinematic look).
  - It lies three-quarter to the camera and lists toward the glass, so we see into it.
  - Planks are torn out of one side, showing 11 ribs. It has deck beams, a broken mast stub, and the fallen mast with its yard on the sand.
  - Its wood is greened with algae.
- **Chest:** brass-banded, the lid thrown open. It holds a heap of gold with glints, a ruby and an emerald, with 26 coins spilled on the sand. A warm glow light swells when the torch finds it.
- **Title:** "Reef and Wreck" in Instrument Sans (`ads/fonts`), set in code as a Blender text object at the focus distance. It fades in over 0 to 0.7 s and out over 1.9 to 2.5 s. Nothing else is written on screen.

## Easter eggs (museum-lit, in the rock under the sea floor)

1. **Roman amphora** in the sand layer under the wreck (-Y face, u -0.40). It hints at an older wreck below this one and sits in the frame of shot 3.
2. **Ammonite** in the white limestone (-Y face, u 0.70), with a nacre sheen.
3. **Trilobite** in the limestone (+X face).
4. **Geode** cracked open in the basalt (+X face), with glowing amethyst.
5. The **gold** itself, hidden in plain sight on the sand until the torch lands on it.

The kit's painted roots are switched off (`soften_roots(amount=0)`): there are no roots under the sea.

## Ambient motion (at least three layers in every shot)

- **arrive:** surface ripples and moving caustics, palm fronds in gusts, the boat bobbing with its ripples, gulls, the turtle and the school in the glass, faint rays.
- **descent:** rays shimmering, bubbles, the school circling then turning, the turtle stroking past, anemones and fans swaying, caustics on the slope, the boat's hull bobbing above.
- **wreck:** caustics drifting on the sand, anemones and weed swaying, the diver's fins and bob, bubbles, the school and the rays in the background, the gold glow pulsing gently once lit.

## Events for the sound designer

| time (s) | event | sound idea |
| --- | --- | --- |
| 0.0 | open on the island and the sea, wind in the palms, gulls | sea surf on a beach (soft, distant), palm fronds rustling, two or three gull calls |
| 0.0-2.5 | title fades in and out | no sound for the title (ambience only) |
| 2.0-4.8 | the boat bobs, water laps its hull | small water laps against a wooden hull |
| 4.8 | the diver tips back off the gunwale | a creak of the boat and a short rustle of gear |
| 5.35 | the diver enters the water | a splash (body entry), droplets falling back |
| 5.7-7.0 | under the surface | the sound goes muffled; first bubble burst from the regulator |
| 7.0 | CUT under water (split view) | a full underwater bed: low hum, distant reef crackle |
| 5.35-20.0 | a bubble puff every 1.6 s | regulator exhale (puffs at 5.35, 6.95, 8.55, 10.15, 11.75, 13.35, 14.95, 16.55, 18.15, 19.75 s) |
| 10.2 | the school turns together | a soft underwater whoosh |
| 10.5-13.0 | the turtle glides across in front | a slow water swish on each flipper stroke (every 2.6 s) |
| 13.5 | CUT to the wreck | the reef crackle comes closer; a faint wooden creak of the hull |
| 15.9 | the diver arrives and hovers | slow fin swishes, one bubble exhale |
| 16.6-17.6 | the torch finds the gold, which glows | a tiny bright glint (a shell or glass chime from a nature recording, very soft) |
| 18.0-20.0 | she reaches toward the chest; hold | one last bubble exhale; the ambience holds to the end |

## Render cost (measured)

The Mac lane uses the MacBook Air M4 GPU (METAL), 1280x720 at 20 spp, with adaptive sampling (threshold 0.03), OIDN, 4 bounces and no volumes. Scene build is 0.6 s on the Mac.

| Round | Frame (shot) | s/frame |
| --- | --- | --- |
| 1 | 40 arrive, 128 arrive | 4.0, 4.6 |
| 1 | 200 descent, 262 descent | 5.0, 6.4 |
| 1 | 336 wreck, 440 wreck | 6.4, 6.3 |
| 2 | 20 arrive, 190 descent, 250 descent, 300 descent, 420 wreck | 4.1, 5.3, 6.0, 7.2, 6.2 |
| 3 | 60 arrive, 132 arrive (splash), 245 descent, 290 descent, 400 wreck, 470 wreck | 4.6, 4.7, 6.4, 6.4, 6.4, 6.3 |
| 4 | 129 and 134 arrive (splash), 330 wreck, 462 wreck | 4.9, 4.6, 6.2, 6.3 |

Across 21 frames the range is 4.0 to 7.2 s/frame, about 5.8 s/frame on average. That is well under the 15 s target, so the 480 frames take about 45 to 50 min on the Mac.

Best stills: round 3 frame 245 (the descent: diver, school, turtle, rays) and frame 470 (the end: the diver's torch on the chest), in `kinoforge-render/out/reef-and-wreck-check3/frames/`.

## Weak spots (honest)

- The figures are storybook primitives: the diver, the turtle and the fish are ellipsoids and tubes. They read at film distance, not up close.
- The scale is storybook too. The wreck is oversized next to the diver, and the boat is a toy dinghy.
- The descent shot's top band is the air above the sea, seen through nothing. Over the sea it reads as a pale strip (the far floor and sky).
- The light rays are cards. From above (shot 1) they read as faint streaks, so they are kept dim there.
- The torch beam is a spot light only. There is no volumetric beam (no volumes, for cost).

## Log
- 2026-10-23: first build and four Mac check rounds (21 stills, see Render cost). Cost 0 (Sam's Mac, free tools).
  - Round 1 to 2: wreck turned three-quarter to the glass, sea floor cleared at the wreck site, teal floor, lights hidden through the glass (the chest glow showed as a ball), rays gain set per shot.
  - Round 2 to 3: splash crash fixed (numpy bool), bubbles in puffs, the school turns beside the diver and in frame, the turtle at mid-water, bed pebbles off, title higher.
  - Round 3 to 4: bigger splash, stronger gold glow.
