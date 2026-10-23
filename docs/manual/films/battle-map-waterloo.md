# Film: The Battle of Waterloo (`battle-map-waterloo`), Battle Map v2

A 158.5 s, 16:9 Battle Map film: June 1815, Napoleon back from Elba, Wellington's hidden line behind a ridge, the farms as
forts, the squares, the Prussians and the Guard, exile to Saint Helena and the word "Waterloo". Made on v1 on 21 Oct,
re-directed on v2 on 22 Oct (with film-side artillery and hollow squares), rendered and re-scored on 22 Oct.
Style: `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/waterloo/` |
| Length, frames | 158.506 s, 3,805 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 9 scenes, 28 shots, average shot 5.6 s; `scenes.mjs` 0 errors, 0 warnings; `check.cjs` no hard problems |
| Teams | France blue, Wellington's British-led army red, Prussia green |
| Narration | 17 lines, 379 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 10.75 s |
| Score | `early_modern_europe`, D aeolian (D minor), 84 bpm, clarinet and bassoon, harp and pizzicato, muted march drum; swell as the Prussians and the Guard arrive; a restrained lift into D major at the end; mix -14.1 LUFS, voice 17.0 dB over. The Lyria score used for placement was extended by repeated bars (`audio/music_ext.wav`) |
| Render | rc-render `films.yml`, 22 Oct (run id not recorded); final score by `remux.yml` (-14.2 LUFS; run id not recorded) |
| Release | rc-render `kino-films`: `battle-map-waterloo.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-waterloo-v2.mp4` |
| Cost | US$0.24904 (Lyria US$0.08, voice US$0.16904; cap US$0.60); render and score free |
| Sam's verdict | v1 battles (22 Oct): see Cannae; v2: waiting |

## Files that make it
`film.json`, `index.html` (imports `units.js` before the engine), `spec.js`, `units.js`, `cues.json`, `ad.json`, `audio/`,
`ledger.json`, `NOTES.md`; `films/lib/score/hints/waterloo.json`.
`units.js` (no engine file changed): an `artillery` figure kind added to the exported `FIG_KINDS` (a field gun on its carriage,
two spoked wheels, trail, bronze barrel, two gunners), used as `kind: 'marker'` with `figures: 'artillery'` because the
director's lint only knows the engine's kinds; a `tricolore` glyph (staff, gold eagle finial, vertical blue, white, red
flag); a `brig` glyph (a flat two-masted ship) that follows the exile, escape and Saint Helena routes. Squares are built from
blocks: at "formed squares" four line blocks contract into south faces and three thin faces rise rank by rank; the spacing
solver keeps the French horsemen out of them.

## The story and the edit
1. The return (Europe map), 0 to l03: JUNE 1815, Napoleon, the exile to Elba and the escape, six red arrows on "declared war",
   the continent turns red on "All of it" (a second bake of the map fades in).
2. Two armies, l03 to l05: the French line, WELLINGTON, BLÜCHER; the blue wedge between the two allied arrows.
3. The ridge, l05 to l07: 18 JUNE 1815; the line steps back behind the crest; Hougoumont (C), La Haye Sainte (D).
4. The lie in, l07 to l08: rain haze clearing; caption 11:30 AM; hold through "a very expensive lie in".
5. Morning attacks, l08 to l10: Hougoumont holds, the centre thrown back, the British cavalry runs on into the guns (cut wide
   on the punchline).
6. The squares, l10 to l11: the horsemen against hollow squares (the key panel steps aside).
7. The Prussians come, l11 to l13: Plancenoit in evening light; the Imperial Guard climbs.
8. The turn (climax), l13 to l15: the line rises and fires (wide), the Guard reels (low and close), the rout, the Duke's words,
   22 JUNE 1815.
9. Saint Helena, l15 to the end: the brig's long voyage; slow push to the speck of SAINT HELENA (1,900 KM FROM AFRICA); the
   dictionary plate and the end card.
Legend: FRANCE (Napoleon, about 73,000), ALLIED ARMY (Duke of Wellington, about 68,000), PRUSSIA (Marshal Blücher, about 50,000
reached the field); units Infantry, Cavalry, Artillery; places A the ridge, B Waterloo, C Hougoumont, D La Haye Sainte.

## Exact steps to re-make it
`node films/lib/battlemap/tools/scenes.mjs films/battles/waterloo`; stills; `node films/director/check.cjs films/battles/waterloo --line battle-map`;
render with rc-render `films.yml` (`inputs[film]=films/battles/waterloo`, 12 to 20 parts, full ref); sound only with `remux.yml`.

## Weak spots
- Europe and the South Atlantic are rough hand maps, not to scale (Elba sits almost on the coast).
- The squares are 22 units (about 180 m) across so they read from above; real squares were far smaller.
- Compressed army moves are faster than real marching, as in every Battle Map film.
- The legend panels cover the left quarter; shots keep the action centre right.

## To make a new one like it
The model for an early-modern battle with guns: copy `units.js` for artillery and build formations (squares) out of blocks
rather than drawing them.

## Sources of truth
`films/battles/waterloo/NOTES.md`, `spec.js`, `units.js`, `film.json`, `cues.json`, `ad.json`, `ledger.json`, `audio/score.json`,
`films/lib/score/hints/waterloo.json`, `docs/LOG.md` (21 and 22 Oct).
