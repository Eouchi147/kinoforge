# The Battle of Gaugamela (331 BC): Battle Map film notes

Engine: `films/lib/battlemap/` (spec format: `SPEC.md` there). Film spec: `spec.js` (every time is a cue word from `cues.json`, so a re-cut of the voice moves
the picture with it). 16:9, 24 fps, 151.252 s. Terrain style, Macedonians deep red (`rome` team), Persians royal blue (`carthage` team), Alexander's charge arrows gold.
No engine change. Film-side code only: `icons.js` (registerIcon) and `fx.js` (patches `StageOverlay.draw`, same pattern as Agincourt).

## Word-match gotchas (the ASR spelled some words oddly; matching is exact first, then prefix)
`l01` is the title line (ASR "Gagamella", do not use its words). `plane` (plain), `smooths`, `Scythe`, `Parmenian`, `realized` are the ASR forms.
`So` matches the exact word "So" only (not "soldiers"); `The#1` in l08 is "The chariots rattled"; `Alexander` in l13 is the exact word at 122.10 ("Alexander's" at 118.26 is not exact).

## Film-side additions
- `icons.js`: `chariot` (variants via `fill`: `fast`, `royal`, `royalfast`, `broken`; spinning scythed wheel, speed lines), `wheel` (big spinning bladed wheel), `roller`,
  `strike` (parchment tag with a silly number crossed out; the text is `fill`), `spiral`, `bulb`, `sweat`, `calendar`, `clock`, `exclaim`, `puff`.
- `fx.js`: `spec.sheen` (glossy glint over the smoothed ellipse), `spec.glows` (the pulsing golden gap), `spec.zones` (the empire as a rounded territory that grows between keys, on the `asia` stage).

## Structure
- Main stage: the dry plain. The smoothed ground is a raised pale disc (a `flat` feature at height 11.6 with a cream palette band) centred (-120, 0), radius 118,
  plus a shimmering sheen overlay. The Tigris runs down the east side. Macedonians start in the south facing north; "right" is east (screen right).
- Stage `asia` (full-screen insets 18.3 to 31.9 and 135.8 to the end): Macedon, Granicus, Issus, Gaugamela, Greece, India on a schematic map (not to scale).
- Persians: 24 line blocks in three rows (stretch by sliding block k east by 10 k units; then the centre gap by k>=4 +14, k<4 -14), Darius's elite guard behind, two cavalry wings east, one west.
- Macedonians: `mac` grid (6 columns x 2 ranks, the columns step apart by 16 units into five lanes), Parmenion's elite block (hangs back on the left), Companion cavalry wedge (scale 1.9 for the "giant wedge"), a rear line where the chariots stop.

## Shot list against the cues
| time (s) | cue | picture |
| --- | --- | --- |
| 0 to 14.1 | l00 | black, "331 BC", low sweep; one small red block with a crown (A YOUNG KING), 20 blue blocks drop in (THE MOST POWERFUL EMPIRE ON EARTH), OUTNUMBERED + question; a loopy red arrow with a spiral icon (A PLAN THAT LOOKS COMPLETELY MAD) |
| 14.35 to 19.3 | l01 | title card THE BATTLE OF GAUGAMELA, 331 BC |
| 18.3 to 31.9 | l02 | map: Macedon, the red block marches to Granicus (WIN ONE) and Issus (WIN TWO) with crossed swords, Darius's blue blocks and crown at Gaugamela (GREAT KING OF PERSIA, WAITING, HIS BIGGEST ARMY YET) |
| 32 to 43 | l03 | the plain: Persians appear, TIGRIS RIVER, NORTHERN IRAQ TODAY, a roller zigzags over the pale disc with sparkles (SMOOTHED FLAT), WHY? and a big question, THE SECRET WEAPON |
| 43 to 52 | l04 | SCYTHED CHARIOTS (big icon), BLADES ON THE WHEELS (huge spinning wheel), SMOOTH GROUND (sheen), FULL SPEED (six chariots dash with speed lines) |
| 52 to 63 | l05 | Macedonians drop in, counter 47,000 MEN, ABOUT; FAR MORE on the Persians (blocks pulse, three rows); NOBODY KNOWS EXACTLY; book; "1,000,000?" and "800,000?" tags struck through (TRULY RIDICULOUS) |
| 63.6 to 74.6 | l06 | ALEXANDER'S PLAN; straight arrow crossed out (no sign); the army slides east (SIDEWAYS, TO THE RIGHT, FURTHER AND FURTHER), OFF THE SMOOTH GROUND |
| 75 to 79 | l07 | DARIUS HAS TO FOLLOW: his line stretches east, sweat face |
| 79.6 to 91.4 | l08 | five chariots dash down five lanes; the columns step apart; chariots stop at the back, tip over; STOPPED AT THE BACK; SO MUCH FOR THE SECRET WEAPON |
| 92 to 100.7 | l09 | blue horsemen ride around the east end; the line stretches; the gap opens and glows (A GAP OPENS) |
| 101 to 104.3 | l10 | bulb over the Companion wedge: EXACTLY WHAT ALEXANDER WAITED FOR |
| 105 to 111.8 | l11 | the wedge grows (THE BEST CAVALRY, A GIANT WEDGE), gold charge arrow through the gap, STRAIGHT AT DARIUS |
| 112.6 to 115.7 | l12 | close-up: Darius's royal chariot with exclaim, turns, puffs of dust, speed lines, flees east |
| 116 to 124 | l13 | cut to the west: Persian cavalry hit Parmenion (sweat, exclaim), the gold arrow turns Alexander back |
| 124.6 to 129 | l14 | THE KING HAS FLED, question marks, the Persian blocks wobble, drift and fade by number (no wounds) |
| 129.6 to 135.4 | l15 | dusk; DARIUS RUNS EAST over the Tigris; calendar WITHIN A YEAR; a crown falls, officers' helmets (no gore) |
| 135.8 to 147.05 | l16 | map: the empire grows (Persia, then Greece to India), AGE 25, AGE 30, gold arrow GREECE to INDIA, NEVER LOST A BATTLE with laurel and stars |
| 147.052 to 151.252 | end | BATTLE MAP + The Battle of Gaugamela, 331 BC |

## Known weak spots
- The `asia` map is schematic; the Mediterranean dominates the early camera. Blocks and icons are symbols, not to scale.
- The ancient silly numbers (1,000,000 and 800,000) are jokes struck through on screen; the narration gives no figure for the Persians (only "far more").
- The chariots are 2D icons following arrows over a 3D map (they stand up like paper cut-outs by design).
