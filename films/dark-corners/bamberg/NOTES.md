# Dark Corners: "A Hundred Thousand Good Nights" (Bamberg, 1628), Kinetic style

9:16, 24 fps, 163.315 s = 3920 frames, rendered 720x1280 (delivered 1080x1920; every size is H-relative). Audio is the original episode mix; picture follows `cues.json`
(every landing time is looked up from the narration word times by `E.tw(line, word, nth)`, nothing is hard-coded except the cut points between cards).

## Build
- Canvas 2D only (no three.js, no WebGL in the render path). The finish pass of `harness/kit/film.js` (vignette 0.30, grain, warm highlights) is re-done in 2D: baked vignette + grain tile (deterministic per-frame offset), warm tint baked into the parchment. This is what makes it ~0.2 to 0.5 s/frame instead of ~1 s.
- `scene.js` composer + scene dispatch + shakes; `engine.js` typographic engine (words LAND on word times: slam / stamp / pop / type; handwriting writer with tremor, wet ink, squash); `lib.js` helpers; `textures.js` dark card, parchment (letter), cold court paper, ink dropout, vignette, grain; `map.js` the dark city map and the two graphs; `scenes_*.js` the shots.
- Query: `?w=&h=`, `?safe=1` draws the platform-UI safe mask. Deterministic (two launches give byte-identical PNGs).
- Colour script: ink-black card + cream type (narration) | cold grey paper + black typed print (the court) | warm parchment + shaky ink (Junius's letter). ONE red mark in the whole film: "I am innocent." The executioner's plea is a third hand (IM Fell English, double-struck, tilted).
- Honesty: no invented names or facts. Names on the map are abstract pen scrawls; the court's name for him to repeat is a typed slip reading NAME. Dates 28 / 29 / 30 June 1628 and "August 1628" follow the original episode script; "Johannes Junius" and "Veronica" are in the narration. "JUNIUS, 1628" on the drawer label.
- Restraint: no bodies. Torture is words and objects only: the vise plates closing on the word "thumbs", a rope with the word "him" hanging from it that drops and jerks eight times with a tally.

## Shot list (seconds on the film timeline, cue id)
| t | scene | picture |
|---|-------|---------|
| 0.00 | o1 | dark; IN, **1628** stamp @0.625 (strong hit 0.65), A GERMAN MAYOR / WAS ARRESTED, cut @3.40 to AND ACCUSED / OF BEING A / **WITCH.** @5.63 |
| 5.95 | o2a | IN **PRISON** @6.22, cell-bar hairlines draw down |
| 6.62 | o2b | hard cut to parchment: HE WROTE, "a secret letter to his daughter." written glyph by glyph on the word times, underline; shakes on hits 8.34, 8.71 |
| 9.35 | o3 | EVERYTHING YOU'RE / ABOUT TO HEAR / REALLY / HAPPENED. |
| 12.90 | title | **DARK CORNERS** + A Hundred Thousand Good Nights (slam @13.15, fade out 15.05) |
| 15.30 | x1a/x1b | HIS NAME WAS / JOHANNES / JUNIUS. then HE LIVED IN / BAMBERG, / IN GERMANY. over the street grid drawing itself (18.85) |
| 21.40 | x2 | AT THAT TIME, MANY PEOPLE BELIEVED; WITCHES CAUSED / STORMS / SICKNESS / FAILED / HARVESTS.; AND THE RULERS OF BAMBERG DECIDED TO HUNT THEM DOWN. |
| 33.10 | x3 | THEIR METHOD WAS SIMPLE; ARREST SOMEONE (first node); TORTURE THEM UNTIL THEY GIVE NAMES (two edges, two nodes with scrawls); THEN ARREST THOSE PEOPLE (four more) |
| 41.60 | x4 | JUNIUS'S WIFE WAS NAMED (edge to her node); SHE WAS EXECUTED (X on the node) |
| 47.00 | x5 | THEN **SIX** PEOPLE NAMED HIM: six nodes, six edges converge on JUNIUS |
| 49.60 | a1-a3 | cold court paper: COURT RECORD, **28 JUNE 1628**, typed testimony; Q and A; I DON'T KNOW. struck out by a black bar; THE JUDGES DIDN'T CARE. |
| 61.62 | t1 | date ticks 28 > 29 > 30 JUNE on "Two days later"; THEY / **TORTURED** / HIM. |
| 64.60 | t2 | THE COURT WROTE DOWN THAT / HE FELT / **NO PAIN.** stamped in a double frame @67.03 |
| 67.90 | t3 | hard cut (hit 67.895) to parchment: IN HIS LETTER, HE WROTE SOMETHING VERY DIFFERENT.; then his hand writes They crushed / his thumbs ...; two plates close on "thumbs" (hit 72.098) |
| 75.12 | t4 | They tied his hands behind his back, / pulled him up by a rope: rope draws down, "him" hangs on it, drops @81.6, **EIGHT TIMES.** eight jerks + tally on the beats 83.56 ... 85.72 |
| 86.40 | silence | dark, the tally fades |
| 87.78 | k1/k2 | THEN SOMETHING STRANGE HAPPENED.; THE EXECUTIONER (the man who had just tortured him,) BEGGED HIM: |
| 95.10 | k3 | the plea in another hand (IM Fell, double struck): Confess to something. True or not. If you don't, they will never stop. (the last line repeats down the page) |
| 102.60 | l1 | SO JUNIUS LIED.; his story typed in court print; THE DEVIL. with a double image |
| 109.20 | l2 | THEN THEY WANTED **NAMES.** |
| 111.07 | l3 | the map again: a line walks the town street by street (legs flash on the three beats), names written at the corners |
| 117.50 | l4 | WHEN HE COULDN'T THINK OF ANYONE (empty dashed slot); a cold typed NAME slip falls in on "name."; AND HE REPEATED IT: names multiply across the town, accelerating |
| 123.80 | e1 | hard cut to parchment: He wrote all of this to his daughter, Veronica, over several days, with hands that barely worked. (tremor and sag grow, a blot at the end) |
| 131.80 | e2 | HE ASKED HER TO HIDE THE LETTER.: the page shrinks, folds in thirds, slides behind a slit of light |
| 134.47 | e3 | HE WROTE: then, the one red mark, **I am / innocent.** written in a trembling hand with a red glow |
| 138.20 | e4 | AND HE ENDED WITH: Good night. Your father will never see you again. (the writing weakens and fades) |
| 144.85 | f1 | THAT **AUGUST** 1628 JOHANNES JUNIUS WAS EXECUTED. (name struck through) |
| 148.95 | f2a | HIS LETTER PROBABLY NEVER REACHED HIS DAUGHTER.: the folded letter rises (hit 149.03) |
| 152.20 | f2b | THE COURT KEPT IT IN HIS FILE.: the letter drops into a folder in an archive drawer, cover closes on the hit 154.5 |
| 154.72 | f3a | AND THAT IS WHY, ALMOST FOUR HUNDRED YEARS LATER, over the shut drawer, dust in the lamp, slow push-in |
| 158.80 | f3b | WE CAN STILL READ IT.: the cover opens (hit ~159.2), warm light on the letter, held to 160.7 |
| 160.715 | end card | DARK CORNERS + A Hundred Thousand Good Nights (last 2.6 s) |

## Measured (720x1280, this 2-core box, harness render.cjs)
- JPEG capture: 0.16 to 0.43 s/frame (incl. warm-up on short ranges; heaviest are the map scenes ~110 to 124 s and the fold). PNG capture 0.50 s/frame over 96 frames (PNG encode is about half of it).
- Byte-identical output across two launches.

## Safe zone (R-2-08: x 0.11 to 0.78 W, y 0.15 to 0.65 H) and known weak spots
- All narration type is fitted to the 0.67 W measure and stays in y 0.15 to 0.65 H. Decorative graphics (map graph, drawer, tally echo, rope, letter strip, the "they will never stop" echo lines) may run into the lower zone by design. The thumbscrew rod and some scrawls reach the right UI strip (decorative).
- Weak: the fold (e2) is a simple 3-panel flip with flat back faces; the map graph is small on the frame (nodes and scrawls are legible but fine); lower half of parchment cards is empty by safe-zone discipline.
