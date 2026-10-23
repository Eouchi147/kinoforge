# Film: A Hundred Thousand Good Nights (`dark-corners-bamberg-kinetic`), Dark Corners, Kinetic

A 163.3 s, 9:16 Dark Corners episode: Bamberg, 1628, Johannes Junius, the mayor accused of witchcraft, tortured into naming
others, and the letter he smuggled to his daughter Veronica. Told in the Kinetic style as eight movements on ONE candle-lit
desk seen from above: the letter (warm parchment), the court record (cold paper, no candle), the plan of the town (dark paper).
The narration, score and sound are the original episode mix. First KINOFORGE version on 21 Oct; polished on 22 Oct after
Sam's verdict ("good but not polished; effects with no intent"): every effect now has a written job.
Styles: `docs/manual/styles/kinetic.md`, `docs/manual/styles/dark-corners.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/dark-corners/bamberg/` |
| Length, frames | 163.315 s, 3,920 frames at 24 fps |
| Picture | Canvas 2D in headless Chromium; rendered 720x1280, delivered 1080x1920 (every size relative to the frame height) |
| Sound | the original episode mix (`audio/mix.m4a`, from rc-render release `dark-films`), untouched; -14 LUFS on the render |
| Render | rc-render `films.yml` run 39790691570 (polish pass; review found text overprinting at card changes near 148 s; all 38 changes audited and fixed), then run 39800373137 (final) |
| Release | rc-render `kino-films`: `dark-corners-bamberg-kinetic.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/dark-corners-bamberg-kinetic-v2.mp4` (the first version kept beside it) |
| Cost | US$0 (picture and render free; the original episode's sound was made earlier by the rc-render dark pipeline) |
| Sam's verdict | first version (22 Oct): good but not polished, effects with no intent. Polished version: waiting |

## Files that make it
`film.json`, `index.html` (fonts Bebas Neue, Cormorant Garamond italic 500 and 600, Special Elite, IM Fell English regular and
italic from `harness/node_modules/@fontsource`), `scene.js` (composer: scene layers, transitions, finish), `engine.js`
(typographic engine: words land on word times; handwriting writer), `kit.js` (text blocks), `lib.js`, `map.js` (the schematic
plan of Bamberg), `fold.js` (the paper fold), `textures.js` (desk, parchment, cold paper), `scenes_open.js` (movements 1, 2),
`scenes_record.js` (3, 4), `scenes_plea.js` (5, 6), `scenes_end.js` (7, 8), `cues.json`, `audio/mix.m4a`, `NOTES.md`.
Landing times are looked up from the narration word times with `E.tw(line, word, nth)`; only cut points between cards are
written as seconds.

## The eight movements
| # | Movement | Time (s) | Visual idea | How it begins |
| --- | --- | --- | --- | --- |
| 1 | The promise | 0 to 15.3 | the date stamped on the desk; a cell (light bars); the letter laid down while he writes; the pledge; the title | start |
| 2 | The town | 15.3 to 49.2 | his name shrinks to a label while the plan draws itself; push in on "hunt them down"; the chain of accusations | the letter is pulled off the desk (9.28) |
| 3 | The record | 49.2 to 67.4 | cold court pages; the answer struck out; the date rolls 28 to 30; NO PAIN stamped | a page slides in from the right |
| 4 | His truth | 67.4 to 86 | his page drops on the record on the hit 67.895; thumbs, rope, eight falls, a tally | page falls from the top and lands on the hit |
| 5 | The plea | 86 to 102.6 | the dark after the tally; the executioner's plea in another hand | ink bleeds out of the tally (85.95 to 87.5) |
| 6 | The names | 102.6 to 123.4 | the lie as a double image; the plan again: down to street level, the pen walks three streets, pull back as the town fills with names | text exchange, the plan redraws |
| 7 | The letter | 123.4 to 144.85 | the letter returns, fails, folds along its creases, slips behind a slit of light; "I am innocent"; "Good night" | page slides up from the bottom |
| 8 | The archive | 144.85 to 163.3 | August; the folded letter rises; the drawer; the file closes; the drawer opens on the letter in warm light; end card | dissolve to the series card (160.7) |
The audit of every effect (kept with its job, or removed) and every motivated transition is in `NOTES.md`; ONE red mark in
the film ("I am innocent."); the executioner's plea is a third hand (IM Fell English, double struck); no bodies.

## Exact steps to re-make it
1. Stills: `node films/lib/kinetic/tools/stills.cjs films/dark-corners/bamberg --t 5,20,60,90,130,155 --out out/bamberg`
   (works on this film); `?safe=1` draws the platform-UI safe mask.
2. Render: `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/dark-corners/bamberg' -f 'inputs[parts]=14' -f "inputs[ref]=$(git rev-parse HEAD)"`.
3. Check every card change for overprinting, the safe zone, length 163.3 s, about -14 LUFS; deliver with `-v2`.

## Cost and time
Measured 0.05 to 0.4 s a frame at 720x1280 (heaviest: the bleed, the walk with many names, the fold). Free.

## Weak spots
- The plan is a readable schematic, not a survey; houses are plain footprints (no roofs, no hatching). No street is named.
- The bleed mask is computed at one third resolution (soft by design).
- While the page shrinks (131.9 to 132.5 s) the first words of "HE ASKED HER" fade in late so they do not sit on cream.
- Narration type stays in y 0.15 to 0.65; desk dressing, tally, drawer and plan use the lower half by design.

## To make a new one like it
Prefer the spec-driven engine `films/lib/kinetic/` (generalised from this film); hand-build only what the engine lacks and
then add it to the engine as a card type (`docs/manual/styles/kinetic.md`).

## Sources of truth
`films/dark-corners/bamberg/NOTES.md`, its `*.js`, `film.json`, `cues.json`, `docs/LOG.md` (21 and 22 Oct), `films/director/CRAFT.md`.
