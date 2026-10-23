# The Sleeping Volcano (Cutaway showcase series, film 6)

`cutaway-series-sleeping-volcano`: 20 s, 24 fps (480 frames), 16:9, rendered 1280x720 at 20 samples, delivered 1920x1080.
Use it shows: drama, natural hazards, science explainers (how a volcano works, in one picture).
Picture: `blender.py` here, on the Cutaway kit (`films/styles/cutaway/cutaway.py`) and the cinematic extras
(`films/styles/cutaway/cinematic/extras.py`), both imported and not edited. Everything new is in `blender.py`.
Free: Blender 5.2, all procedural, no downloaded assets. Sound: nature recordings only (events table below).

## Story in 20 s

- **Beginning (0 to 6.5 s): the island sleeps.** A green island volcano on a 3 m block of turquoise sea at golden hour.
  The -Y cut runs through the crater, so the face is the textbook section: the cone's nested layers, a dark conduit and,
  deep down, a dull red magma chamber that breathes. A thin white steam wisp leaves the crater. Gulls circle.
- **Middle (6.5 to 13.5 s): it wakes.** Close on the chamber: the molten rock churns and brightens. The magma climbs the
  conduit and the side cracks, and the camera climbs with it to the crater. Birds burst out of the trees (10.9 s). The
  steam turns to grey smoke.
- **End (13.5 to 20 s): a gentle eruption at dusk.** Wide and low. The ground jolts once, lava fountains rise from the
  crater with embers and a dark ash plume lit orange from below, a lava stream runs down the east flank and reaches the
  sea, where steam bursts up. The light has gone to dusk. Fade to black over the last 0.8 s. No people anywhere: nobody
  is in danger.

## Shots (the reason for each cut)

| # | Shot | Time | Frames | Camera | Job |
| --- | --- | --- | --- | --- | --- |
| 1 | island | 0 to 6.5 s | 0 to 155 | wide three-quarter from the +X/-Y side, 35 mm, a slow eased push (8.7 to 7.9 m) with a 4 degree arc | where we are: the whole block reads at once, the title sits above the cone |
| 2 | rise | 6.5 to 13.5 s | 156 to 323 | starts close on the chamber (38 mm, f/6), cranes up the cut face with the magma front to the crater, tilting down from 4 to 20 degrees and pulling back | the cause: the cut to the chamber happens because it has just started to brighten (4 s); the camera is motivated by the rising magma and arrives as the birds lift |
| 3 | eruption | 13.5 to 20 s | 324 to 479 | low wide three-quarter (28 mm, 9 to 10.5 degrees up, room above the cone for the plume), a slow 7 degree arc and push; one damped vertical jolt at 14.2 s | the climax and the end image: we cut wide 0.7 s before the first fountain so the eruption happens on screen |

Every move is eased (smoothstep or quintic) and real time. Check frames (one per beat): 30, 120, 175, 235, 300, 345, 420, 450.

## The job of every element

| Element | Job |
| --- | --- |
| Cone on the -Y cut (crater cut in half) | the hero: shape plus section in one image, readable at phone size |
| Nested cone layers, flat old sea floor below, a soft unconformity at z = -1.05 m | a stratovolcano is built of its own eruptions: the science in the picture. The wall's `sd` attribute is recomputed in this film (the kit's default flattens to the mean top height, which turned the tall cone into one dark band) |
| Magma chamber (glowing hollow in the face) | the threat; breathes slowly while asleep (3.2 s cycle), brightens from 4 s, flickers |
| Conduit and seven side cracks | the path; a rising front (world z) lights them from 6.9 to 13.2 s |
| Chamber, conduit and crater lights | the glow spills onto the strata, the cone and the underside of the smoke |
| Forest belt on the lower slopes, bare dark rock above | the island is alive; the bare summit says volcano |
| Turquoise sea with corals, weed, pebbles and two fish schools behind the glass | life and scale; the sea is where the story ends |
| Steam wisp, then smoke, then the ash plume (billboard cards) | the escalation, readable as one rising column |
| Lava fountains (120 glowing bombs on slow-gravity arcs), 90 embers, a vent halo | the eruption, gentle and beautiful |
| Lava stream (ribbon draped on the flank, revealed by a front, crust cooling behind) | the consequence; it ends in the sea |
| Sea steam at the lava entry | the closing beat: fire meets water |
| Golden hour to dusk (sun, sky, fill and floor fade from 8 to 17 s) | time passes; the lava becomes the key light |
| Low mist cards over the sea | haze and depth without a volume |
| Title "The Sleeping Volcano" (Archivo, warm white, 0.25 to 2.5 s) | the name, then out of the way |

## Ambient motion (at least three layers in every shot)

- Shot 1: grass and trees in the wind, sea ripples and caustics, the steam wisp, gulls circling, fish behind the glass, mist drifting, the chamber breathing.
- Shot 2: the magma churning (4D noise), the flicker of the chamber light on the strata, the rising front in the conduit and cracks, then wind in the trees, the smoke and the birds.
- Shot 3: fountains, embers, the plume, the lava stream, the sea steam, sea ripples, wind in the trees.

## Easter eggs (museum-lit, in the deep layers)

1. **Geode** cracked open in the bedrock left of the chamber (-Y face), glowing amethyst.
2. **Ammonite** in the sea-floor sediment at the left of the -Y face.
3. **Pirate chest** buried under the sea floor on the +X face, gold glowing inside.
4. **Trilobite** deep on the +X face.

## Events for the sound designer (nature recordings only)

| time (s) | event | sound idea |
| --- | --- | --- |
| 0.0 | island at golden hour | gentle waves lapping on a beach, light wind in leaves |
| 0.3 to 6.5 | gulls circling | distant gull calls (two or three, sparse) |
| 0.5 onward | steam wisp from the crater | very soft fumarole hiss (geyser steam, far) |
| 4.0 | chamber starts to brighten | a very low, almost felt rumble begins (distant thunder, low-passed) |
| 6.5 | cut to the chamber (underground) | waves drop away, the rumble and a slow bubbling (mud pot) come forward |
| 6.9 to 13.2 | magma climbs the conduit | rising rumble, mud pot bubbling, small rock cracks (stones cracking) |
| 10.0 to 13.0 | steam turns to smoke | the hiss thickens |
| 10.9 to 11.4 | birds burst from the trees | a flock taking off (wing flutter), a few alarm calls |
| 13.5 | cut wide at dusk | a beat of near silence, waves back, wind |
| 14.2 | first lava fountain, the ground jolts | a deep boom (close thunder clap, low-passed) and a short rock tumble |
| 14.2 to 20 | fountains and embers | crackling fire (large bonfire), occasional thuds of falling bombs |
| 14.7 to 17.7 | lava stream runs down the flank | slow crackle and creak of a big fire, stones rolling |
| 17.7 | lava reaches the sea | a loud hiss (water on hot stones), then steam roaring |
| 17.7 to 20 | sea steam rises | steam hiss under the waves |
| 19.2 to 20.0 | fade to black | everything fades with the picture; last sound: a wave |

## Render cost (measured on Sam's Mac lane, M4 GPU, METAL, 1280x720, 20 samples)

Each check job renders one frame; the "s/frame" line in the job log includes the first-frame scene sync. Scene build 2.4 s
(7.3 s when the Mac was hot), 378 objects.

| Round (23 Oct, UTC) | Frames | s/frame |
| --- | --- | --- |
| 1 (02:40) | 30, 175, 280, 380, 455 | 7.0, 5.4, 4.4, 3.9, 4.0 |
| 2 (02:50) | 30, 175, 300, 380, 465 | 5.3, 4.2, 5.1, 4.2, 4.0 |
| 3 (03:05) | 30, 175, 235, 305, 400, 470 | 5.6, 5.5, 4.2, 4.3, 4.0, 4.3 |
| 4 (03:15) | 30, 235, 300, 330, 420 | 9.7, 20.9, 14.9, 9.2, 11.3 |
| 5 (03:25, final scene) | 120, 300, 345, 420, 450 | 14.6, 15.1, 11.9, 12.2, 14.0 |

- **Cool Mac: about 4 to 6 s a frame. Hot or shared Mac: about 9 to 15 s a frame (one 21 s outlier).** The slowdown in
  rounds 4 and 5 is the machine, not the scene: in the same window the other builders' frames slowed 2 to 3 times as
  well (river-time 3 to 6 s became 14 to 16 s) and this film's pure-CPU scene build went from 2.4 s to 7.3 s. The MacBook
  Air has no fan, so a long queue throttles it.
- Full film estimate: 480 frames x 4 to 15 s = about 35 min (cool) to 2 h (throttled).
- Settings: 20 samples, adaptive threshold 0.04, OIDN denoise, max bounces 4 (diffuse 1, glossy 1, transmission 4,
  transparent 16), no volumes (smoke, steam, mist and the vent halo are cards), no motion blur.
- Levers if it must be faster: 16 samples; drop the 3 mist cards; fewer plume cards (18 to 12).

## Weak spots (honest)

- **Smoke is cards.** The ash plume reads as a warm glowing column at phone size, but up close it is soft blobs, and
  the first second of the eruption (around 14.2 to 14.6 s) shows small grainy puffs before the column fills in.
- **The cone face is dark at dusk.** The nested layers read well in shot 1 and the crane; in the last shot the face is
  mostly lit by the conduit and chamber, so the layers fade into shadow (deliberate for dusk, but less science on screen).
- **Lava stream** is a ribbon on the far flank: it reads as a glowing line threading through the trees, not as a wide
  flow. The trees are kept out of a corridor around it, but some crowns still overlap it from the closing angle.
- **Chamber texture** is a cracked lava-lake pattern (bright seams on dark crust): very readable, a little regular.
- **Trees** are the kit's lumpy miniatures; birds are simple dark silhouettes (about 8 cm wingspan on a 3 m block).
- **Cracks** read as thin black lines before the magma reaches them (6.5 to 9 s), then glow.
- The sky shows a soft horizon line where the floor meets the dome at dusk; it reads as a distant sea horizon.
- Not seen moving yet: checked on stills only (frames 30, 120, 175, 235, 300, 345, 420, 450, 465, 470). The puff
  cycles (plume, steam) and the fountain are continuous functions of t, but their motion should be checked in the first
  full render.

## Best still

Round 5, frame 420 (17.5 s, the eruption at dusk, lava reaching the sea):
`/Users/sam/Desktop/Projects/AI tools/Video Production/kinoforge-render/out/sleeping-volcano-check5/frames/00420.png`
(on Sam's Mac). Shot 1 at its best: round 5 frame 120.
