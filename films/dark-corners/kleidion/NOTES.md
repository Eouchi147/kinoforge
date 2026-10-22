# As They Say (Kleidion, 1014): Lantern Road, re-directed 22 Oct 2026

Original Dark Corners episode in the Lantern Road style (living painting, painted 2.5D multiplane, motivated light), 9:16, 169.049 s,
driven by `audio/mix.m4a` and `cues.json`. The sound and its timing are untouched; only the picture was re-directed.
`index.html` loads `scene.js` (three.js via the harness importmap).

Sam's verdict on the first version: too many cuts, the first scene is sped up, it does not flow, it is not smooth. This version follows
`films/director/CRAFT.md`: 9 scenes, 29 shots (was 64, average 5.8 s), every cut has a reason, real-time movement, living worlds.

## Files
- `scene.js` boot, camera keyframes with the `glide` ease (ease in, steady middle, ease out), per-frame context `F`, captions, labels, title card, dissolves,
  set cache (LRU of 3). `window.__kf.audit()` prints the camera speed of every shot (pan and tilt in % of the frame per second, zoom in % per second).
- `shots.js` the shot table (cuts sit on sentence ends or strong hits), captions from the word timings, place and name `LABELS`.
- `kf.js` painted planes with relightable material and a wind shear (`uSway`) for grass strips, additive glow canvas, lean post chain.
- `paint.js` brush engine (unchanged). `figs.js` people (planted foot gait, back and front views, helmets, shields, spears), horses (walk to gallop, three bone legs).
- `ambient.js` shared life: `birds`, `smoke`, `motes`, `shaft`, `shaftAB`, `hazeBand`, `paintGrassStrip`.
- `sets/*.js` painted once per set: road, march, page, city, pass, camp, gorge, field, table, prilep. `sets/light.js` has the lit floor (`floorLight`), `rubble`,
  `ruts`, `ledgeTrees` and a flat `horizonGlow` that replaced the cloud-like glows.

## Diagnosis: why the first scene looked sped up
1. The walkers moved at a constant speed on the screen while the road runs through a ten fold change of scale (far switchback to the foreground) and over a ground that is
   tilted: the same screen speed is a crawl in the foreground and a sprint in the distance.
2. The camera jumped from the wide to a close framing in two seconds and slid sideways faster than a person could pan.
3. Feet and ground did not agree: stride was set by time, not by distance.
Fix: every walker is driven in metres and metres per second on the ground (road 4 m wide, a person 1.75 m, a walk about 1.2 m/s), the screen position comes from
projecting that ground point, and the gait phase is distance divided by stride (`ph = d / (0.6 * 1.75 * stride)`), so a foot never skates. The opening is one
continuous 8.4 s shot with a slow glide (a few % per second). The escort halts at 4.2 to 5.4 s and the column goes on.
The same rule drives the horses (gait from distance), the pursuers, the wall attack and the night torch column.

## Scenes (place, dramatic question, beginning, middle, end, camera plan)
1. THE ROAD, 0 to 12.19. A hill road at dusk. Who is walking it? Begin: wide, a long column descends the switchbacks. Middle: lanterns light group by group on the hits, the
   escort halts. End: close on one group with hands on shoulders, "Blind." Camera: one slow glide down and in, then a gentle lateral track beside the group.
2. THE PAGE, 12.19 to 18.65. A desk by candlelight. Who wrote it down? Begin: the manuscript fills with script, line by line. Middle: the candles dim (to 50 %). End: title card
   DARK CORNERS / As They Say on the dim desk. Camera: down the page, then a slow pull back.
3. TWO ENEMIES, 18.65 to 34.99. Constantinople and the Bulgarian camp. Who are they, how long have they fought? Begin: the skyline and Basil. Middle: Samuel at his fire, the far
   camp lights up. End: the tally plank fills to forty. Camera: slow push on Basil, a rise from the fire to the camp, a push on the plank.
4. NEAR-DEATH, 34.99 to 38.73 and 38.73 to 44.61. How close did each come to dying? Begin: Basil's column in the gorge. Middle: stones from the rim, the rear rider wheels and gallops toward us.
   Then the night field, Samuel among the dead: a breath, at the end he lifts his head. Camera: a slow push in each.
5. KLEIDION, 44.61 to 76.74. Will the wall hold? Begin: the wall goes up, one long dolly (workers, carts, dust). Middle: the key; three waves break on the wall. Time passes (dissolve):
   the general's torches cross the mountain and come down behind the wall. End: rout, flares, the captives on the floor. Camera: a long dolly, a held view, a tilt down at the end.
6. THE ESCAPE AND THE GORGE, 76.74 to 90.88. Is the war over? Begin: pursuers with torches close in. Middle: the son lifts his father into the saddle, they ride off into the dark. The Bulgarian
   fires are relit; the governor's column dies in a gorge (dust, stones, a banner that lies still). End: the banner stays down. Camera: follows the riders, then two slow pushes.
7. THE ORDER, 90.88 to 112.36. What did Basil order and how was it written? Begin: the wax seal. Middle: the chronicler's page ("about fifteen thousand, as they say"). End: groups of
   a hundred walk home, each led by one man with one eye left; the blinding is never shown. Camera: pushes on the seal and the page, then the road and a lateral track.
8. PRILEP, 112.36 to 128.87. What does Samuel do when he sees them? Begin: from the rampart, groups with lanterns on the plain. Middle: he collapses, the water, the cup,
   the lamp gutters. End: dawn, the window lit then dark. Camera: a slow push, a slow drift over the cup, a push on the keep.
9. AS THEY SAY, 128.87 to 169.05. Was it true, and what is left? Begin: the second manuscript. Middle: both numbers struck out, Bulgaria fights on, the nickname, a time lapse of the empty
   terrace. End: the road at dusk, the last lantern goes out on "say", end card. Camera: pull backs, a push on the camp, a slow rise, a lantern road.

## Shot list and the reason for each cut (times in s)
| shot | time | set | what, and why the cut is here |
|---|---|---|---|
| r1a | 0 to 8.43 | road | the whole opening in one shot: place and scale first. No cut needed. |
| r1b | to 12.19 | march | change of scale: close on one group as "Blind." lands. Cut on the end of the sentence. Holds under the next line (J cut). |
| p2a | to 18.65 | page | change of place and time: the written source. One shot: the script appears, the candles dim for the title. |
| c3a | to 25.73 | city | change of place: the emperor, as the narrator names him. Cut on the end of the sentence. Lamps light on the hits. |
| c3b | to 31.81 | camp | the enemy: change of place and side. The lift on the hit lights the far camp. |
| c3b to c3c | 31.81 | table | change of scale: the forty years as a tally (new information: the number). |
| n4a | to 38.73 | gorge | new line, new place: the ambush. Stones on the hits at 36.27 and 37.22. |
| n4b | to 44.61 | field | the second near-death: change of place and time (night). One push, a breath, he lifts his head on "dead". |
| k5a | to 54.89 | pass | new scene: the wall. One 10 s dolly shows its scale and the work. |
| k5b | to 56.42 | table | detail on the name: the key (1.5 s, the one short shot, it is the word "The key."). |
| k5c | to 62.34 | pass | the same view for three waves: the attack. Held on the wall after the last wave. |
| k5d | to 68.80 | pass | time passes: a dissolve to night, the general's column. |
| k5e | to 76.74 | pass | consequence: the rout; the camera comes down to the captives only once the flares have burned. |
| e6a | to 82.69 | field | change of place: the field at night. One continuous action (pursuers, lift, ride off). |
| e6b | to 85.31 | camp | reaction: the Bulgarian fires relit. |
| e6c | to 90.88 | gorge | change of place and time: the governor's column. The banner lies still, the last held frame. |
| o7a | to 93.34 | table | new scene: the order, the seal, on the hit at 91.95. |
| o7b | to 100.77 | page | new information: what the chronicler wrote. |
| o7c | to 103.95 | road | change of place: groups set out, lanterns on one by one (L cut: the next line starts under it). |
| o7d | to 108.60 | march | change of scale: the hands on the shoulders, one eye left. |
| o7e | to 112.36 | road | pull back: the long road home, the consequence. |
| l8a | to 116.75 | prilep | change of place: the rampart, Samuel, the lanterns. He collapses. |
| l8b | to 125.19 | table | change of place and time: the cup of water, held for eight seconds. |
| l8c | to 128.87 | prilep | time passes (dissolve): dawn, the window dark. |
| a9a | to 140.11 | page | new scene: was it true? The second manuscript. |
| a9b | to 144.91 | page | the pull back that shows both numbers struck out. |
| a9c | to 149.51 | camp | change of place: Bulgaria fights on. |
| a9d | to 160.89 | city | change of place: the nickname; the time lapse (the lamps rise and fall) is one shot. |
| a9e | to 169.05 | road | the last lanterns go out on "say"; end card at 166.45. |
Only dissolves are k5d (night) and l8c (a day passes). Everything else is a hard cut. Average shot 5.8 s, one shot under 2 s.

## What lives in every wide shot (three or more layers of motion)
Road: wind in grass strips and banners, hamlet smoke, crows, drifting haze, lanterns flicker. March: dust at the feet, crows, haze, motes. Page and table: candle smoke, a moth,
drifting dust in the beam, flicker on the paper. City: gulls, hearth smoke, boats under sail, a patrol on the sea wall, glints on the water, windows lighting. Camp: smoke, crows,
haze, sparks. Gorge: sun shafts, birds in the gap, haze, motes, falling stones and dust. Field: crows over the moon, a mist, far torches searching, grass in the wind. Pass: workers,
ox carts, braziers, smoke. Prilep: swifts, hearth smoke, mist, a lantern flicker.
Gorge and pass floors have light and shadow wedges, rubble with cast shadows and cart ruts; the horizon is a flat afterglow band (`horizonGlow`), not a cloud.

## Colour script
Dusk indigo and violet with warm lantern light (road, march, camp); Byzantine purple and gold (city); golden hour in the gorge and the pass; candlelit parchment and wood
(page, table); cold moonlit blue (field); dawn rose (Prilep ending).

## Measured cost
`node tools/dev.mjs`, 720x1280 through `harness/render.cjs`. The machine was shared (load 12 to 13 on 2 cores) so absolute times are not reliable: on the same machine at the same
moment the old build took 6.85 s per frame and this one 6.36 s, so the cost did not go up. On a quiet machine the old build measured 0.9 to 1.3 s per frame at 720x1280.
Sets build lazily on their first frame (2.5 to 14 s).

## Known weak spots
- Horses and riders are still flat profile silhouettes (better walk and gallop, but no volume). The gorge cliff walls are still blocky slabs; the ledge trees hardly read.
- The night field is sparse: the fallen are simple shapes in mist.
- Characters at close range (march) are puppet-like.
- Rendering stills out of order (a later shot before an earlier one of the same set) once showed a leftover orange glow; sequential renders were clean.
- Debug: `?prof=1` logs set build times; `?hide=planeName` hides a painted plane.
