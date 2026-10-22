# Dark Corners: "A Hundred Thousand Good Nights" (Bamberg, 1628), Kinetic style (polish pass of 22 Oct 2026)

9:16, 24 fps, 163.315 s = 3920 frames, rendered 720x1280 (delivered 1080x1920; every size is H-relative). Audio is the original episode mix, untouched; picture follows `cues.json`
(every landing time is looked up from the narration word times by `E.tw(line, word, nth)`; only cut points between cards are written as seconds).
Decision: polished the hand-built film rather than rebuilding on `films/lib/kinetic/` (the spec engine has no town plan, paper fold, transitions or rope). `films/lib/kinetic/` is untouched.

## The idea: one desk, eight movements
Everything happens on ONE table seen from above: a dark desk lit by a candle low on the left (loose papers, an inkwell and a quill in the lower half, kept dark), and the documents laid on it:
the letter (warm parchment), the court record (cold paper, no candle: the court has no warmth), the plan of the town (dark paper). Scenes meet by a transition with a reason.

| # | movement | time | visual idea | how it begins |
|---|----------|------|-------------|---------------|
| 1 | THE PROMISE | 0 to 15.3 | the date stamped on the desk; a cell (light bars); the letter laid down while he writes it; the pledge; the title | start |
| 2 | THE TOWN | 15.3 to 49.2 | his name shrinks to a label while the plan of Bamberg draws itself; the camera pushes in on "hunt them down"; the chain of accusations grows on the plan | the letter is pulled off the desk (slide down, 9.28) |
| 3 | THE RECORD | 49.2 to 67.4 | cold court pages: testimony, the answer struck out; next page, the date rolls 28 to 30 (time passing); NO PAIN stamped | the page slides in from the right (49.2) |
| 4 | HIS TRUTH | 67.4 to 86 | his page is dropped on the record on the hit 67.895; thumbs, rope, eight falls, a tally | page falls from the top and lands on the hit |
| 5 | THE PLEA | 86 to 102.6 | the dark after the tally; the executioner's plea in another hand | ink bleeds out of the tally and turns the page to dark (85.95 to 87.5) |
| 6 | THE NAMES | 102.6 to 123.4 | the lie (a double image), "names", the plan again: camera down to street level, the pen walks three real streets, then pulls back as the town fills with names | text exchange, then the plan redraws under the type |
| 7 | THE LETTER | 123.4 to 144.85 | the letter returns (echo of movement 1), fails, folds along its creases, slips behind a slit of light; "I am innocent"; "Good night" | page slides up from the bottom (123.4) |
| 8 | THE ARCHIVE | 144.85 to 163.3 | August; the folded letter rises; the drawer rises; the file closes; the drawer opens on the letter in warm light; end card | dissolve to the series card (160.7) |

## Audit: what every effect is for (one line each) and what was removed
Kept, with its job:
- Stamp lands (1628, DARK CORNERS, NO PAIN, end card) with a 3 to 7 px shake: a stamp strikes a surface. Nothing else with type shakes any more.
- Page-landing hit 67.895 (8 px): his page is dropped on the record; the cut sits on the music hit.
- Rope load (81.8) and the eight falls (6 px each): each fall IS the shake; thumbscrew plates close on "thumbs": the one image of the act.
- File cover thump 154.5: the cover closes.
- Word landing (short vertical stretch, then rest; one soft rebound only on the key word): weight, then stillness. Softened from the first version (1.30 to 1.20).
- Cell bars (6.2): where we are. Light stripes on the desk are the bars' light.
- Light-bar hairlines, title rule, labels: structure, not decoration.
- Name label (18.5): his name moves to the corner and becomes the caption of the town.
- Camera on the plan: wide, settle (18.7 to 24); push in on "hunt them down" (29 to 33); frame the chain (33 to 49); street level for the walk (112 to 117.5); pull back over the consequence (118 to 123).
- Chain nodes land on their words; X on the wife on "executed"; six edges converge on "named him".
- Odometer date 28 to 29 to 30 on "two days later": elapsed time.
- Black bar on "I DON'T KNOW" on "judges": the judges strike it out.
- Double image on DEVIL: a lie is two images. One quiet ghost pair, then it settles.
- Tally (eight strokes) and its ink-bleed: the count is the one thing the ink did not take; silence follows.
- Fold of the letter: the letter is hidden; the outside carries the name it is for (Veronica).
- Candle flicker (very slow, +/-12 percent) on the desk and the parchment, not on the court's cold paper: the candle is Junius's world.
- Paper grain, ink dropout, ink spread (0.7 px blur under the ink on paper): the type belongs to the material.
Removed or replaced:
- Exposure flashes on every payoff and shakes on every payoff word (decorative).
- The "they will never stop" echo lines running down the page (decorative; the plea now holds after "stop.").
- Hard cuts between cards of one document (record, letter): now one page and text exchanges, or a page turn.
- Repeated "COURT RECORD" header re-typing on every court card.
- The three 28/29/30 date slams (replaced by the roller).
- Hard cuts into every scene: replaced by slides, a bleed and a dissolve; the one hard cut left (letter to desk at 131.88) is invisible (the full-frame page becomes the sheet).

## Transitions (each one motivated)
slide in from the bottom (letter laid on the desk, 6.35 and 123.4: bookends), slide out downward (letter set aside, 9.28), slide in from the right (a page of the record, 49.2),
slide out upward (next page of the record, 61.3), drop from the top landing on the hit (67.395 to 67.895), ink bleed from the tally (85.95), dissolve (end card, 160.715).

## Build
- Canvas 2D only. `scene.js` composer (scene layers, transitions, finish), `engine.js` typographic engine (words LAND on word times; handwriting writer), `kit.js` text blocks, `map.js` the plan, `fold.js` the paper fold, `textures.js` desk / parchment / cold paper, `scenes_open.js` (1, 2), `scenes_record.js` (3, 4), `scenes_plea.js` (5, 6), `scenes_end.js` (7, 8).
- Query: `?w=&h=`, `?safe=1` draws the platform-UI safe mask. Deterministic. Stills: `node films/lib/kinetic/tools/stills.cjs films/dark-corners/bamberg --t 5,20 --out DIR` (works on this film).
- The plan of Bamberg is schematic, not surveyed: the two arms of the Regnitz around the island town, the cathedral hill with contour rings and the cathedral on top, lanes, houses set along them, market-garden strips to the south east. No street is named; nodes carry pen scrawls (no invented people). The folder label reads JOHANNES JUNIUS, the drawer plate JUNIUS, 1628; the outside of the letter reads "Veronica" (named in the narration).
- Fold: each flap is cut into 18 slices bent about its hinge (free end leads), perspective, lamp from the north (a vertical flap goes dark), back face with the writing showing through mirrored, cast shadow, layer edges when folded.
- Colour script: ink-black desk + cream type (narration) | cold grey paper + black print (the court) | warm parchment + shaky ink (Junius). ONE red mark: "I am innocent." (it stays faintly while he says good night). The executioner's plea is a third hand (IM Fell English, double struck).
- Restraint: no bodies. Torture is words and objects only.

## Measured (720x1280, shared 2-core box, stills tool, in-page time)
0.05 to 0.4 s/frame (heaviest: the bleed, the walk with many names, the fold). Wall-clock of the harness renderer was noisy because other jobs shared the machine.

## Known weak spots (honest)
- The plan is readable and has real structure but is still a schematic; the houses are plain footprints (no roofs, no hatching).
- The bleed mask is computed at one third resolution (soft by design).
- While the page shrinks (131.9 to 132.5) the first words of "HE ASKED HER" are faded in late so they do not sit on cream.
- Safe zone: narration type stays in y 0.15 to 0.65; decorative graphics (desk dressing, tally, drawer, plan) use the lower half by design.
