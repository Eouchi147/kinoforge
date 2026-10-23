# The River Through Time (Cutaway showcase, film 1)

20 s, 24 fps, 16:9 (1280x720 render, 1920x1080 out), 20 spp, no voice, no music. Use it shows: geology, time-lapse,
science explainers. Files: `film.json`, `blender.py` (the whole scene), `audio/` (the sound designer's folder).

## Story (beginning, middle, end)

- **Beginning:** a flat grassy block in morning light with a small stream running across it. A deer grazes.
- **Middle:** time starts to race (the sun swings round the sky, shadows sweep, cloud shadows race, the light warms and
  cools). The stream cuts down through the rock beds. As the cut passes them, three fossils are bared in the canyon wall,
  youngest first: an ammonite, a fish, a trilobite. Each one catches a museum light as it appears.
- **End:** time stops at golden hour, today. The canyon stands. A tiny hiker walks to the rim and stops to look in;
  birds circle over the canyon.

No words on screen apart from the title. Time is shown only by the sun and the light.

## Shots (and why each cut)

| # | Shot | Time | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | then | 0.0 to 6.0 s (frames 0-143) | Wide three-quarter, 35 mm, f/16. A slow push (6.3 to 5.8 m) and a 4 degree arc. | Where we are: a flat world and a little stream. Time begins to race at 2.6 s and the cut starts at 3.2 s, so the change starts inside the wide shot. |
| 2 | ages | 6.0 to 14.0 s (frames 144-335) | In front of the cut face, looking into the canyon at its west wall, 26 mm, f/8. The camera cranes down 0.5 m as the water sinks. | **Cut reason:** change of scale. We go close to see the fossils being bared one by one. The crane follows the river down through the beds. |
| 3 | today | 14.0 to 20.0 s (frames 336-479) | Low three-quarter into the setting sun, 32 mm, f/11. A slow push toward the hiker's rim (4.4 to 3.5 m) and a 5 degree arc. | **Cut reason:** change of time (time has stopped; this is now). The result we can name: the canyon, with a person for scale. |

Every move is eased in and out and slow (under 10 % of frame per second).

## Elements and their jobs

| Element | Job |
| --- | --- |
| The carved height field (`Terrain`) | The story itself. Each frame the top is re-shaped: a V notch sinks with the river while the final terraced canyon limits it, so every point of the final wall is bared once and then stays. Hard beds stand as cliffs, soft beds as slopes. |
| Rock beds by world height (`mat_land`) | Time made visible: the canyon walls and the cut face share the same horizontal beds. Old is deep. |
| Water box that sinks with the floor | The cause: the river does the cutting, and its level drops with the floor (glass, turquoise depth, a meniscus line on the cut face). |
| Racing sun, sky dome and shadows (`Sky`) | The passing of ages without text. The sun turns 2 extra full times, its height swings and the light warms when it is low. |
| Cloud-gap shadows (`rt_gobo`) | Time cue and life: they drift slowly in real time and race during the time-lapse. |
| Grass in the cut zone (`rt_grass_go`) | Follows the ground down and shrinks away where the rock is bared, so the meadow gives way to the canyon. |
| Museum spots on the fossils | Guide the eye to each reveal; they fade in over 0.8 s when the fossil is bared. |
| Hiker (7.5 cm x 1.25, red pack) | Scale and the human ending: today someone stands where the river once ran at grass level. |
| Birds, deer, butterflies, petals, wind in the grass and trees, water ripples | The living world (CRAFT section 5): at least three layers of motion in every shot. |
| Canyon mist sheets (`rt_mist`) | Depth and golden-hour air in the last shot; faint in the middle shot. |
| Title | "The River Through Time", Instrument Sans, set in code (a Blender text object on the camera), 0 to 2.5 s, faded in and out. |

Ambient motion per shot: then (grass and tree wind, deer grazing and looking up, butterflies, petals, birds, water,
cloud shadows); ages (racing sun and shadows, racing cloud shadows, sinking water with ripples, mist, grass on the rim);
today (grass wind, birds over the canyon, hiker walking, deer, mist drifting, water).

## Easter eggs

1. **Ammonite** in the pale limestone near the rim (the youngest bed with a fossil), a nacre sheen.
2. **Fossil fish** in the orange sandstone, mid wall: skull, spine, ribs, fins, tail fan.
3. **Trilobite** in the green shale, near the floor (trilobites are the oldest of the three).
4. Real geology in miniature: hard beds (limestones, sandstones) make cliffs and soft beds (shales) make slopes, as in a real canyon.

## Events for the sound designer

Nature recordings only (no music, no voice). Times in seconds.

| time (s) | event | sound idea |
| --- | --- | --- |
| 0.0 | Morning on the meadow, a small stream | light wind in grass, a trickling brook, distant songbirds |
| 0.0 to 2.5 | Title in and out | nothing extra |
| 2.6 | Time starts to race (sun moves) | the ambience begins to speed up or swell: wind rising |
| 3.2 | The stream starts cutting | the brook grows into running water |
| 4.2 | The deer lifts its head | (optional) a soft rustle |
| 6.0 | Cut to the canyon wall | the river is louder and closer: rushing water |
| 6.0 to 13.0 | The canyon deepens; sun swings round twice | long wind gusts, water rumble rising, maybe a small rockfall at 9.5 |
| 7.99 | Ammonite bared, its light comes on | a small stone crack or trickle of grit |
| 11.31 | Fish bared | a small stone crack or trickle of grit |
| 12.11 | Trilobite bared | a small stone crack or trickle of grit |
| 12.2 to 14.4 | Time slows to a stop | the rush settles |
| 14.0 | Cut to today, golden hour | evening canyon: wind on the rim, the river far below, a raven or swifts |
| 14.6 to 18.2 | The hiker walks to the rim | footsteps on dry gravel |
| 18.2 | The hiker stops and turns to look | steps stop; the wind holds |
| 17.2 | The second deer lifts its head | nothing, or a faint rustle |
| 20.0 | End | let the wind tail out |

## Render cost (measured on Sam's Mac, M4 GPU, METAL, 1280x720, 20 spp)

See the measured numbers below (filled from the check rounds).

## Weak spots (honest)

See the end of the build.
