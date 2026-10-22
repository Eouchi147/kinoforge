# The Battle of Agincourt (1415): Battle Map film notes

Engine: `films/lib/battlemap/` (spec format: `SPEC.md` there). Film spec: `spec.js` (all times come from `cues.json` words, so a
re-cut of the voice moves the picture with it). 16:9, 24 fps, 147.278 s. Terrain style, England deep red, France royal blue.
The ASR spelled "Agincourt" wrongly in cue line l01 (do not use words of l01); "plowed" and "armor" are US spellings in the cues, the screen text is UK.

## Film-side code (no engine fork)
- `icons.js`: new icons registered through `registerIcon` (rain, thermo, sick, mud, bush, quill, weather, axe, hammer, clock, sweat, fall).
- `fx.js`: patches `StageOverlay.draw` to add `spec.rain` (slanted streaks between two cue times) and `spec.dim` (dark veil, optional theatre
  curtains for the playbill), and adds the `wood` team (stakes).
- Engine changes, both backward compatible: `registerIcon()` in `icons.js`; `blocks.js` now registers every cell of a `grid` group as its own
  selector (`fr.2.0`), so single cells can be moved.

## Structure
- Main stage: the battlefield, dry (hook, title, field, numbers). Stage `chan`: Channel map (England, Seine, Somme, northern France) shown full
  screen 16.3 to 40.03. Stage `wet`: the same battlefield baked a second time with a dark brown palette, faded in over "It had rained all night"
  (57.28, 1.8 s) so the mud arrives with the rain; it carries the rest of the film. Blocks, moves, labels, icons, camera are one shared object.
- Field: Agincourt wood west, Tramecourt wood east, narrowing to a neck (the funnel). England south facing north, France north facing south.

## Shot list against the cues

| time (s) | cue | picture |
| --- | --- | --- |
| 0 to 1.25 | | black card; low sweep over the empty field |
| 1.4 to 12.3 | l00 hook | "1415"; one small red block (SMALL, SICK + thermometer + sick face, SOAKING WET + rain streaks and cloud icon); camera pulls back, France's 15 blue blocks drop in (ONE OF FRANCE'S BIGGEST ARMIES); mud splat icon + check on England (MUD PICKS ENGLAND) |
| 12.95 to 16.3 | l01 | title card THE BATTLE OF AGINCOURT, 1415 |
| 16.3 to 40 | l02, l03 | Channel map: Henry's block and a ship cross to Harfleur (crown over France), port captured (city and flag), the block shrinks with sick face and thermometer, bushes pop on "bushes were busy", dashed march to Calais, a blue block and a no sign block the road |
| 40 to 48 | l04 | 25 OCTOBER 1415, both armies drop in, FRESHLY PLOUGHED FIELD, the two woods named |
| 48 to 57 | l05 | counter to 8,000 ENGLISH, LONGBOW ARCHERS (bow icons), FAR MORE on France (no invented number), knights (cavalry wedges + helmets) |
| 57 to 62 | l06 | rain streaks, dark cloud, brown wet stage fades in, mud splats, DEEP, STICKY MUD |
| 62 to 72 | l07 | stakes (26 x 2 little wedges) hammered in with hammer icons, the army walks forward three arrows wide to bowshot |
| 72 to 76 | l08 | three waves of volleys up and down onto France, low camera behind the English |
| 76.5 to 86 | l09 | French cavalry charge, slowed by mud (sinking), stopped at the stakes (bursts, no sign), turn back, vanish into their own lines |
| 86.7 to 94 | l10 | French on foot, heavy armour helmet, mud splats trail, blocks sink |
| 94 to 100 | l11 | green arrows from the woods, French squeeze into the neck, packed tight, sword with a no sign |
| 101 to 109.6 | l12 | contact at the stakes, EXHAUSTED sweat face, bows fall, hammers and axes, archers wheel in on both flanks |
| 110 to 114.6 | l13 | rear rank rides forward over the others, blocks jostle (heading wobble, lift), CHAOS bursts |
| 115 to 125.5 | l14 | dusk, clock icon, French blocks fade by number plates (THOUSANDS ...), crowns for the lords, English block shrinks a little (A FEW HUNDRED) |
| 126 to 134.6 | l15 | ALMOST 200 YEARS LATER; playbill plate HENRY V, A PLAY BY SHAKESPEARE with quill and crown, theatre curtains; WE FEW. / WE HAPPY FEW. on the words |
| 134.8 to 143.08 | l16 | heart between helmet and crown (marries the daughter), crown (heir to France), helmet, weather icon (ALWAYS CHECK THE WEATHER) |
| 143.078 to 147.278 | end | BATTLE MAP + The Battle of Agincourt, 1415 |

## Measured
Shared 2 core CPU box (load 4 to 6), SwiftShader, 1280x720. Chan stage about 1.0 to 1.3 s/frame, wet battlefield about 1.1 to 1.6 s/frame, hook with MSAA 4
(0 to 13 s) about 2 s/frame. A 5 s motion stretch (frames 1872 to 1992, cavalry charge) rendered at 1.21 s/frame including the one-off start (about 35 to 45 s: three sheet bakes and shader compile).
Estimate 3,534 frames at about 1.3 s = 77 min on this box, far less split over parallel parts.

## Known weak spots
- The Channel map is stylised and not to scale (blocks and icons are symbols); the narrow sea reads like a river at the steep camera angles.
- Mud is a darker brown palette, rain streaks and splat icons, not a true mud texture; fields keep a faint patchwork.
- Volley arrows are long dark streaks at the low camera; they read as "thousands" but are busy.
- Soldiers are lattice dots, blocks are not figures; losses are only fading blocks and plates (no counters for the French, the narration gives no number).
