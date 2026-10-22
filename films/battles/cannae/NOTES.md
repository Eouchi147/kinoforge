# The Battle of Cannae (216 BC): Battle Map film notes

Engine: `films/lib/battlemap/` (spec format: `SPEC.md` there). Film spec: `spec.js` (times come from `cues.json` words, so a
re-cut of the voice moves the picture with it). 16:9, 24 fps, 157.629 s. Look: KINOFORGE Terrain (engraved relief map), Rome
deep red, Carthage royal blue, golden afternoon light that turns to a low red sun in the evening. Every word on screen is set in code.

## Shot list against the cues

| time (s) | cue | picture |
| --- | --- | --- |
| 0 to 1 | | black card fades out |
| 1.3 to 3.9 | l00 "2,200 years ago" | low soaring sweep over the plain, big outlined "2,200 YEARS AGO" |
| 3.7 to 12 | "Rome sent one of the biggest armies" | Rome's 12 blocks drop in one by one (ROME plate); a lone blue block far away on "one man" (ONE MAN plate), camera swings out to show the gap |
| 12 to 17 | "lesson soldiers still study today" | book icon, plate STILL STUDIED TODAY, camera climbs to top-down |
| 17.4 to 21.7 | music rise | title card THE BATTLE OF CANNAE, then 216 BC (warm gradient), heavy dark scrim, camera snaps top-down underneath |
| 22.4 to 33.5 | l02 Hannibal, Carthage, the Alps | relief inset (framed panel, slight tilt): helmet + city at Carthage, dashed route over the Alps with an elephant following the arrow, burst at the end ("just to make a point") |
| 33.9 to 42.3 | l03 Rome, two commanders | Rome block, two helmets swapping (TWO COMMANDERS), "what could possibly go wrong?" |
| 42 to 52 | l04 the plain, the river, 2 August 216 BC | camera pulls to the Aufidus, date plate |
| 49.5 to 57 | l05 80,000 vs 50,000 | counters count up (80,000 SOLDIERS / 50,000 SOLDIERS), BE BIGGER / PUSH HARD / WIN |
| 57 to 75 | l06, l07 Hannibal's plan | middle bows toward Rome into a crescent (LIKE A BOW), best soldiers at the ends, cavalry on the wings (plates, pops) |
| 75.4 to 83.8 | l08 charge | Roman group charges (THE ROMANS CHARGE), crescent gives way step by step with the words (SLOWLY, STEP BY STEP, EXACTLY AS PLANNED + check) |
| 84 to 89.5 | l09 deeper into the gap | Romans push to the middle, crescent wraps (THEY THINK THEY ARE WINNING, laurel, DEEPER AND DEEPER) |
| 90 to 98 | l10 cavalry | Carthage's horse chases Rome's off (CHASED OFF + burst), then swings behind (dashed arrows, BEHIND THE ROMANS) |
| 98.8 to 105.8 | l11 envelopment | both elite blocks step in on LEFT and RIGHT, horsemen shut the back door |
| 106.5 to 111.8 | l12 surrounded, hug | SURROUNDED, gold loop drawn around; stillness and a bouncing heart on "hug"; plate HISTORY'S LEAST FUN GROUP HUG |
| 112.5 to 117.2 | l13 packed | Rome compresses (squeeze), sword icon with a no sign (PACKED SO TIGHTLY, NO ROOM TO LIFT A SWORD) |
| 117.9 to 126.9 | l14 evening | camera drops low, sun goes red, Roman blocks fade by numbers (TENS OF THOUSANDS LOST), two helmets for the two commanders |
| 127.8 to 135.8 | l15 Rome refuses | full-screen cut to the Mediterranean relief map: WON THE WAR? / NOPE, new Roman armies march out of Rome |
| 136.5 to 145.4 | l16 Scipio, 202 BC | 14 YEARS LATER, 202 BC, ship carries Scipio to Africa, HE STUDIED HIS TRICKS with a book |
| 146.3 to 153.4 | l17 copying the hug | HANNIBAL WON THE BATTLE (crown), ROME WON THE WAR (laurel), then the double-envelopment icon (blue pincer round a red block) is stamped again and again on the map |
| 153.43 to 157.63 | end | end card BATTLE MAP + "The Battle of Cannae, 216 BC" |

## Measured

The sandbox is a 2 core CPU box shared with other builders (load average 6 to 7 during these runs), SwiftShader, 1280x720.
`tools/bench.sh`: battle stretch (1900) min 0.89, median 1.06 s/frame; envelopment stretch (2700) min 0.77, median 0.99;
epilogue full-screen stage (3400) min 0.93, median 1.10 with inset samples 0. A quiet box measured about 0.5 s/frame for
terrain and blocks earlier in the build (MSAA off); MSAA 4 adds about 0.4 s and is on only for 0 to 14 s and 118 to 127 s.
First frame 5 to 17 s (sheet bake, one off). A 5 s motion stretch (120 frames, 78 to 83 s) rendered at 1.4 s/frame under that load.
Full film estimate: 3,782 frames at about 1 s = about 1 h 5 min on a shared box, well under that on a quiet runner.

## Known weak spots

- The ground is a calm engraved plain: scale and drama come from the camera and the 80,000 vs 50,000 counters more than from the terrain.
- The Mediterranean map is stylised (Italy, Sicily, Sardinia, Corsica, Africa) and not to scale; coasts are Chaikin smoothed hand polygons.
- Soldiers are a lattice of dots, not figures. Hug icons are small stamps in the last 7 s.
- Label plates can sit over the blocks they describe on tight shots.
