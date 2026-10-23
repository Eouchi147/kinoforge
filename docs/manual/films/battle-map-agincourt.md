# Film: The Battle of Agincourt (`battle-map-agincourt`), Battle Map v2 with two Cutaway inserts

A 147.3 s, 16:9 Battle Map film: 1415, a small, sick, soaked English army against one of France's biggest; the night of rain,
the stakes, the arrows, the funnel between two woods, the crush, the cost, Shakespeare and Troyes. It is the only battle
with inserts: two Blender Cutaway clips (`films/cutaway/agincourt-mud/`, by another builder) show the mud up close, laid
frame-exactly over the map shots by rc-render `films.yml`. Made on v1 on 21 Oct, re-directed on v2 on 22 Oct around the
inserts, rendered on 23 Oct once both inserts existed. Style: `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/agincourt/` |
| Length, frames | 147.278 s, 3,535 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 9 scenes, 29 shots, average shot 5.1 s |
| Maps | main stage: the battlefield, dry; `chan`: the Channel map; `wet`: the same battlefield baked again with a dark brown palette, dissolving in on "It had rained all night" |
| Teams | England deep red (`rome`), France royal blue (`carthage`) |
| Inserts (`film.json`) | `cutaway-agincourt-mud-A` over frames 1375 to 1727 (about 57.3 to 72.0 s); `cutaway-agincourt-mud-B` over frames 2081 to 2420 (about 86.7 to 100.8 s) |
| Narration | 17 lines, 354 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 13.12 s |
| Score | `medieval_europe`, E aeolian, 70 bpm, lute, fiddle and recorder-like flute, tabor; swell as the woods squeeze the French; mix -14.09 LUFS, voice 17.1 dB over |
| Render | rc-render `films.yml` run 39900294683 (insert A laid, insert B missing: overlay bug), then run 39908562175 (both inserts, 147.3 s, -14.2 LUFS, no frozen frames), 23 Oct |
| Release | rc-render `kino-films`: `battle-map-agincourt.mp4`, `-preview.mp4`, `-sheet.jpg`, `-poster.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-agincourt-v2.mp4` (sent to him 23 Oct) |
| Cost | US$0.238 (Lyria US$0.08, voice US$0.158; cap US$0.60); render, inserts and score free |
| Sam's verdict | v1 battles (22 Oct): see Cannae; v2: waiting |

## Files that make it
`film.json` (with `inserts`), `index.html`, `spec.js`, `fx.js` (`spec.rain`: slanted rain streaks between two cue times; in
the hook, all night in `l06`, and over northern France on "always check the weather"), `cues.json`, `ad.json`, `audio/`,
`ledger.json`, `NOTES.md`; `films/lib/score/hints/agincourt.json`. The v1 `icons.js` (rain cloud, thermometer, sick face, mud
splat and others) is deleted; the only glyph left is one galley on Henry's crossing. The stakes are drawn as the map symbol
for a row of stakes (a zigzag ink line).

## The story and the edit
1. The odds, 0 to 17.9 s (dry): a small red block in the rain (caption 1415); France rises across the field; "Spoiler" crane.
2. The road to Calais, 17.9 to 40.0 (chan): crossing, Harfleur taken, the army sick (the hold through "Very, very sick. Let's
   just say the bushes were busy."), the march north, the French across the road.
3. The field, 40.0 to 57.3 (dry): 25 OCTOBER 1415, the two woods (C, D), 8,000 counter, archers on both wings; into insert A.
4. Rain and stakes, 57.3 to 71.2 (wet, under insert A): a 1.8 s dissolve to the wet field; stakes go in; the line walks forward.
5. Arrows and horses, 71.2 to 86.7 (wet): out of A top-down (cut on "close enough to shoot."), volleys, the charge stopped at
   the stakes; into insert B.
6. The funnel, 86.7 to 100.3 (wet, under insert B): the French on foot sinking; the column narrows between the woods.
7. The crush (climax), 100.3 to 115.0: out of B top-down (cut on "swing a weapon."), the archers wheel in on the flank, the
   rear pushes the front.
8. The cost, 115.0 to 126.1: the long pull back, FRANCE dims; cut on "The English lost a few hundred."
9. After, 126.1 to 147.3 (chan): HENRY V, BY WILLIAM SHAKESPEARE, ABOUT 1599 ("We few. We happy few."), TROYES, 1420, the rain
   starts over France; end card at 143.08 s.
The map shots under the inserts are complete fallbacks. Full table and legend: `films/battles/agincourt/NOTES.md`.

## Exact steps to re-make it
1. Render the inserts first (Cutaway manual: `films/cutaway/agincourt-mud/` A and B) so `cutaway-agincourt-mud-A.mp4` and
   `-B.mp4` exist in `kino-films`.
2. `node films/lib/battlemap/tools/scenes.mjs films/battles/agincourt`; stills; `check.cjs --line battle-map`.
3. Render: `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/battles/agincourt' -f 'inputs[parts]=16' -f "inputs[ref]=$(git rev-parse HEAD)"`.
   The join downloads each insert, scales it to 1920x1080, trims it to `last - first + 1` frames, shifts it to `first / fps`
   and overlays it enabled by time with half a frame of margin (rc-render commit 54c1bb4). A render that waits on others can
   be a `chain.yml` rule (it was dispatched by hand at 04:21 UTC on 23 Oct when the cron had not fired).
4. Check the boundary frames of both inserts (1375, 1727, 2081, 2420) plus the usual checks.

## Weak spots
- The Channel map is stylised and not to scale; Troyes and London are placed by eye.
- The mud on the map is a darker brown palette and rain streaks, not a true mud texture (the inserts carry the close-up mud).
- Losses are thinning ranks; no counter for the French (the narration gives no number; modern estimates 12,000 to 36,000).

## Known traps (this film)
- The speech recogniser misspelled "Agincourt" in cue line `l01`: do not use words of `l01` in the spec. "plowed" and "armor"
  are US spellings in the cues; screen text is UK.
- In a chain of ffmpeg overlays, `enable='between(n,a,b)'` on the second overlay does not see the main frame numbers (insert B
  never showed in run 39900294683): enable by time and test with two inserts (`docs/LESSONS.md`).

## To make a new one like it
A battle with close-ups the map cannot show: plan the cuts into and out of each insert on the map (a high shot from the side
the insert shows, a top-down consequence shot after it), keep the map shots under the inserts complete, list the inserts in
`film.json`, and render the inserts first.

## Sources of truth
`films/battles/agincourt/NOTES.md`, `spec.js`, `fx.js`, `film.json`, `cues.json`, `ad.json`, `ledger.json`, `audio/score.json`,
`films/lib/score/hints/agincourt.json`, rc-render `.github/workflows/films.yml`, `docs/LOG.md` (22 and 23 Oct), `docs/STATUS.md`.
