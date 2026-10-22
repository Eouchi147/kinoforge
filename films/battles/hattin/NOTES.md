# The Battle of Hattin (1187): Battle Map film notes

Engine: `films/lib/battlemap/` (spec format: `SPEC.md` there). Film spec: `spec.js` (every time comes from `cues.json` words, so a re-cut of the
voice moves the picture with it). 16:9, 24 fps, 141.55 s. Terrain style. Teams are colours only, no religious badges: crusaders red (`rome`), Saladin's army blue (`carthage`).
Cue spellings to remember: the ASR writes "Tiberius" in l03 and "Tiberias" in l04, "armor", "Hatton/Hatim/Hateen"; repeated words use `#n` (`l04.don't#1`, `l04.said#1`, `l05.in#1`, `l07.they#1`, `l10.some#1`, `l12.a#1`).

## Film-side code (no engine change)
- `icons.js`: sun (sunglasses), flask (empty, sad), hook (with worm), castle, thermo (mercury climbs), flame, cough, eye, cup (iced water), hothelmet (helmet with heat lines), hourglass, twinpeaks, drop, sweat, tent2.
- `fx.js`: patches `StageOverlay.draw` to add `spec.shimmer` (heat haze veil and rising wavy bands), `spec.smoke` (world-anchored puffs drifting on a wind vector), `spec.dim` (night veil with twinkling stars, or a dark veil for plates).

## Structure
- Main stage = Galilee, 1 unit about 100 m: Saffuriya far west, the dry plateau (camp), the Horns of Hattin (two hills, saddle between), the springs (stream) just north, Tiberias and the Sea of Galilee in the east.
- Stage `lev` = the Levant, 1 unit about 1.5 km (Mediterranean, Nile delta, Jordan, Lebanon, Dead Sea): Egypt and Syria as blue slabs, the crusader states as red slabs, castles along the coast. Full-screen insets 15.4 to 27.376 (l02) and 114.405 to 131.03 (l13, l14).

## Shot list against the cues
| time (s) | cue | picture |
| --- | --- | --- |
| 0 to 11 | l00 | black card; low sweep; 1187; blue sultan block on the far hills (THE SULTAN), dashed lure arrow, red army drops in (AN ENTIRE ARMY) and marches the long corridor; sun in sunglasses + heat haze (THE MIDDLE OF SUMMER); hourglass (WAITING); empty flask (THIRSTY) |
| 11.05 to 15.7 | l01 | title card THE BATTLE OF HATTIN, 1187 |
| 15.4 to 27.4 | l02 | Levant: Saladin block, EGYPT and SYRIA slabs, ALMOST 90 YEARS, ship arrow from Europe, crusader slab, Jerusalem (crown), castles pop down the coast |
| 27.4 to 36.7 | l03 | Galilee: SUMMER 1187, Saladin's block round the lake to Tiberias, burst, SEA OF GALILEE, IT WAS BAIT with a fishing hook and worm over Tiberias, crusader army appears, rescue arrow |
| 37 to 50.3 | l04 | six lord helmets with small NO plates, JULY thermometer rising, NO WATER ON THE WAY (flask + no sign), his wife in Tiberias (heart), second big DON'T GO, KING GUY OF JERUSALEM (crown), HE MARCHES ANYWAY |
| 50.9 to 57.3 | l05 | counter 20,000 CRUSADERS, march arrow across dry hills, heat shimmer, helmet with heat lines, thermometer |
| 58 to 64.4 | l06 | six horse archers circle (ring arrow, volleys), then line up east: way to water blocked (drop + no sign) |
| 64.9 to 75 | l07 | evening light, stuck on the dry plateau, Saladin's army line, the lake, eye + dashed gaze arrow, no sign |
| 75.7 to 84.8 | l08 | night veil and stars, flames along the line, smoke puffs drift into the camp, thirsty flask, coughing faces |
| 85.3 to 91.9 | l09 | morning, break-through arrow to the springs, TWO HILLS, THE HORNS OF HATTIN |
| 92.6 to 100.9 | l10 | the 8 pieces scatter, some charge, some flee up the two hills, KING GUY'S RED TENT, blue ring closes |
| 101.3 to 106.1 | l11 | tent icon falls, ring tightens, red pieces fade, KING GUY CAPTURED (crown, ring arrows) |
| 106.7 to 113.8 | l12 | Saladin walks up; goblet of iced water plate, check mark (A SIGN HIS LIFE WOULD BE SPARED) |
| 114.4 to 123.4 | l13 | Levant again: THREE MONTHS LATER, Saladin to Jerusalem (blue flag), 1099 flashback plate (dimmed), WITHOUT A MASSACRE (laurel) |
| 123.7 to 130.7 | l14 | ship arrow from Europe, RICHARD THE LIONHEART (crown), Jerusalem stays blue (no sign on the arrow) |
| 131 to 137.35 | l15 | dry hills, dim: THE LESSON OF HATTIN (book), NEVER CROSS DRY HILLS IN JULY (sun), ESPECIALLY IN A METAL SUIT (helmet + heat lines) |
| 137.35 to 141.55 | end | BATTLE MAP + The Battle of Hattin, 1187 |

## Measured
Shared box under load 6 to 9: stills 0.4 to 1.8 s, a 5 s stretch (frames 1404 to 1523, circling archers) 1.8 s/frame average including a 12 s start. The two stages bake once (4 to 8 s each; cold start 25 s on this box).

## Known weak spots
- The Levant is stylised: slabs for lands, symbols for castles; the sea dominates the west of the frame in the Europe shots.
- Only the blocks are units; losses are fading blocks (no numbers: the narration gives none except 20,000).
- The ring around the tent climbs the Horns when tight; the flask icon reads as a sad canteen, not a perfect flask.
