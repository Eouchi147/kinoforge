# Under the City (Cutaway showcase #2)

Use it shows: infrastructure, real estate, trades, how a city works. 16:9, 20 s, 24 fps, 480 frames, 1280x720 render,
1920x1080 out, 20 spp. Picture: `blender.py` here (imports the kit `films/styles/cutaway/cutaway.py` and
`films/styles/cutaway/cinematic/extras.py`, neither edited). Everything procedural, no downloaded assets, nothing paid.
Sound: `audio/` (made by the sound designer from the event table below).

## Story (beginning, middle, end)

- **Beginning (0 to 4.5 s):** a dusk street of row houses on a block cut out of the city. The street lamps flicker on
  one by one, a red bus and a small car pass each other, two windows light up, steam rises from a manhole. The title.
- **Middle (4.5 to 15.5 s):** the camera sinks down the cut face, through the layers a city stands on: the pipes and
  cables under the pavement (and the manhole shaft with its ladder), the brick sewer where a rat scurries in and sniffs,
  the metro tunnel as a train rushes past (the rat flinches), the old brick foundations of an earlier city, a Roman floor,
  and at the very bottom a T. rex in the limestone. The descent ends with a slow push in on the skull.
- **End (15.5 to 20 s):** the whole column at once, top to bottom, at nightfall: the bus drives back in on top while a
  second train crosses the other way below, and the last window on the street lights up. The city, working, on its past.

## Shots (and the reason for each cut)

| # | Shot | Time | Frames | Camera | Job |
| --- | --- | --- | --- | --- | --- |
| 1 | street | 0.0 to 4.5 s | 0 to 107 | high three-quarter (az -66 to -60, el 27 to 20), 35 mm, slow push down toward the cut edge, f/22 | where we are: a living street at dusk; the title over the sky |
| 2 | descent | 4.5 to 15.5 s | 108 to 371 | crane straight down the -Y face, 35 mm, f/5.6, a monotone eased curve through stations (street 4.5 s, pipes 6.4, sewer 8.3, metro 10.4, bricks 12.4, Roman 13.9, bones 15.5); the last 1.6 s push in from 2.15 to 1.7 m | the reveal: each layer is older than the one above |
| 3 | city | 15.5 to 20.0 s | 372 to 479 | wide low three-quarter (az -60 to -56, el 6 to 10), 35 mm, slow pull back and rise, f/16 | the payoff: the whole machine and its history in one frame |

- Cut 1 to 2: the push down ends at the cut edge by the steaming manhole; we go where the steam comes from.
- Cut 2 to 3: from the oldest thing (the skull) straight out to the whole block: scale and time in one jump.

## Layers (top down) and the job of every element

| Depth | Layer | What is in it | Job |
| --- | --- | --- | --- |
| top | street | asphalt with a damp sheen and a dashed centre line, kerbs and sidewalks (the front sidewalk's section shows on the face), a terrace of 13 row houses (two or three floors, lit and dark windows, stoops, cornices, chimneys), 4 street lamps with light cones, 7 trees, a bus, a car, a manhole with steam, 3 birds, a far skyline behind a dusk haze card | the city as people know it; the warm windows against the cool dusk set the colour story |
| 0 to 0.12 m | asphalt, road base | a telecom cable along the face with cyan pulses of light travelling on it (data) | the newest, busiest layer |
| 0.12 to 0.52 m | utility fill | pipe sections cut across: blue water mains, yellow gas, district heating pair, an orange fibre duct with a glowing core, a clay storm drain, a concrete duct bank with six conduits and copper; the manhole shaft (cut in half, brick lined, ladder) down to the sewer; a lost green bottle; an earthworm | what trades build and fix |
| 0.52 to 0.86 m | clay | the brick sewer cut lengthwise: flowing dark water with a mist card, a stone walkway, a caged warm lamp that buzzes, a drip and its ring every 1.7 s, the rat | the hidden plumbing, and the first animal |
| 0.86 to 1.36 m | grey till | the metro tunnel cut lengthwise: concrete segment rings, track bed, rails and sleepers, warm wall lamps, the train (three cars, lit windows with passenger silhouettes, headlights, red tail lights, light streaks, its interior light sweeps the tunnel) | the one loud, fast moment |
| 1.36 to 1.58 m | rubble | an older city: a vaulted brick cellar with a barrel, a brick wall on a stone footing, a horseshoe | history begins |
| 1.58 to 1.80 m | Roman loam | a fallen mosaic floor fragment (tile pattern, meander band, missing tesserae), an amphora with bronze coins, a fluted marble column drum | the classic dig |
| 1.80 to 2.45 m | fossil limestone | the T. rex skeleton (the cinematic kit's egg, scale 0.72) in its dug pocket, an ammonite, a trilobite | deep time, the bottom of everything |
| below | bedrock | dark slate | the floor |

Light: a dusk rig (`ex.cine_light`): a very low deep orange sun behind the block (az 112, el 4), a deep blue zenith,
cool fill on the camera side, warm rim; the cut face is in cool shade, lit by its own warm practicals (sewer lamp, tunnel
lamps, the train) and soft museum spots on each find (bricks, mosaic, column, amphora, pipes, sewer, dinosaur, ammonite,
trilobite). No volumes: haze, mist, steam, lamp cones and train streaks are additive cards seen only by the camera.
Dust motes drift in front of the face and shiver as the train passes. Finish: AgX Medium High Contrast, exposure 0.25,
bloom (threshold 1.0, 0.28), vignette 0.3.

Ambient motion per shot (at least three each): street: lamps, bus, car, trees in the wind, steam, birds, windows.
Descent: data pulses, worm, sewer water and mist, lamp buzz, drip, rat, train, motes. City: bus, car, train, trees,
pulses, steam, birds, last window.

## Easter eggs

The rat (it stops to sniff, looks up at the rumble, then bolts), the earthworm, the lost green bottle, data pulses in
the cable, passenger silhouettes in the train, the barrel in the old cellar, the horseshoe, the Roman coins by the
amphora, the mosaic's missing tiles, the ammonite, the trilobite, the T. rex.

## Events for the sound designer

| time (s) | event | sound idea |
| --- | --- | --- |
| 0.0 | dusk street, evening traffic far off, birds | city dusk bed, a few birds |
| 0.55, 0.87, 1.19, 1.51 | the four street lamps flicker on, one by one (left to right) | soft electrical tick or hum swell each |
| 0.0 to 4.5 | the bus drives left to right in the near lane, the car right to left in the far lane | bus engine pass (close), small car pass |
| 2.0, 3.3 | a window lights up | (none, or a faint domestic sound) |
| 0.0 to 4.5 | steam rises from the manhole | low hiss under the street |
| 4.5 | cut: the camera starts down the face; the street closes over us | street sound filtered and fading |
| 4.5 to 7.0 | pipes and cables | water running in a pipe, a gas hiss is not needed (keep it calm) |
| 6.7, 8.4, 10.1 | drip falls into the sewer water (one every 1.7 s; the ones in shot) | single water drops |
| 6.9 to 7.9 | the rat scurries in along the walkway | small scurry, claws on stone |
| 7.9 to 9.85 | the rat stops and sniffs; the sewer water flows; the lamp buzzes | sewer flow, a squeak at about 8.4 |
| 9.6 | far rumble: the train is coming (its light reaches the tunnel) | low rumble building |
| 9.85 | the rat looks up | (sync to the rumble) |
| 10.0 to 10.5 | the rat bolts away to the left | quick scurry |
| 10.74 | the train's nose is at the frame centre (enters frame about 10.3, tail clears about 11.6), left to right | metro roar and rail clatter, peak here, then away |
| 12.4 | old brick cellar | stillness, a trickle of grit |
| 13.9 | Roman floor | stillness, a slow drip with stone reverb |
| 14.8 to 15.5 | slow push in on the T. rex skull | near silence, deep room tone |
| 15.5 | cut to the whole block (wide) | the city fades back in, distant |
| 16.2 | the car drives in from the right on top | faint car |
| 16.9 to 19.3 | the second train crosses below, right to left; centre at 18.1 | distant rumble (it is far now) |
| 15.5 to 20.0 | the bus drives in from the left on top | faint bus |
| 18.6 | the last window lights up | (none) |
| 20.0 | end | fade out |

## Check stills

Frames 40 (street), 150 (pipes), 200 (sewer and rat), 252 (metro, train in frame), 320 (bricks and Roman), 368 (bones),
440 (city, second train).

## Render cost

To be measured on the Mac lane (see below).

## Log

- 2026-10-23 02:40 UTC: first build (scene builds in 2.2 s, 186 objects, 30 lights). Mac round 1: 3.2 to 4.8 s/frame. Cost: 0.
- 2026-10-23 02:55 UTC: round 2: calmer dusk sky, real skyline windows, soft cool face fill, sewer bigger and lit, rat bigger, crane and wide closer.
- 2026-10-23 03:00 UTC: round 2b: tree roots in the fill, an old cast-iron main, three people walking home, skyline as dark silhouettes, face fill aimed below the street.
- 2026-10-23 03:15 UTC: round 3: face fill down to 45 W and exposure 0.1 (round 2 read flat and toy-like), darker limestone and floor, softer skyline haze, tunnel end caps kept inside the block (they bulged out of the side faces).
