# Film: The Battle of Hattin (`battle-map-hattin`), Battle Map v2

A 141.6 s, 16:9 Battle Map film: July 1187, Saladin lures the crusader army into the dry hills of Galilee and waits for thirst;
the advice ignored, the march, the lake in sight, the brush fire, the break-out at the Horns of Hattin, the cup of water and
Jerusalem. Teams are colours only, with no religious badges. Made on v1 on 21 to 22 Oct (second group of four), re-directed on
v2 on 22 Oct, rendered and re-scored the same day. Style: `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/hattin/` |
| Length, frames | 141.55 s, 3,398 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 9 scenes, 28 shots, average shot 5.1 s; `scenes.mjs` 0 errors, 0 warnings |
| Teams | crusaders red (`rome`), Saladin's army blue (`carthage`) |
| Light | July heat (a warm haze veil), evening, a blue night lit by the brush fire, a clear morning, dusk at the Horns |
| Narration | 16 lines, 327 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 11.05 s |
| Score | `middle_east_central_asia`, A hijaz, 66 bpm (dry, thirsty, slower pulse); swell as the army breaks into pieces around the red tent; sober ending, Saladin's mercy; mix -14.09 LUFS, voice 17.0 dB over |
| Render | rc-render `films.yml`, 22 Oct (run id not recorded); final score by `remux.yml` (-14.2 LUFS; run id not recorded) |
| Release | rc-render `kino-films`: `battle-map-hattin.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-hattin-v2.mp4` |
| Cost | US$0.2248 (Lyria US$0.08, voice US$0.1448; cap US$0.50); render and score free |
| Sam's verdict | v1 battles (22 Oct): see Cannae; v2: waiting |

## Files that make it
`film.json`, `index.html` (imports `kinds.js` and `fx.js`), `spec.js`, `kinds.js`, `fx.js`, `cues.json`, `ad.json`, `audio/`,
`ledger.json`, `NOTES.md`; `films/lib/score/hints/hattin.json`.
`kinds.js`: figure kinds `flame` (a burning tuft of dry grass) and `pavilion` (King Guy's red tent) in `FIG_KINDS`, and the unit
symbol `u-horse-archers`. `fx.js`: the brush fire (`ambient.fires`: flames light one after another along the line, flicker,
send up dark smoke, glow over the night veil), the red tent that collapses (`ambient.pavilions`), the heat (`heat`: a warm
veil only), smoke drifting into the camp (`smoke`), the night (`dim`, no stars), territories on the Levant map (`regions`:
Egypt and Syria blue, the crusader states red, the south turns blue when Jerusalem falls). Thirst is told by the map, not by a
prop: the water is always on screen as lettered places (B Sea of Galilee, C the springs), the horse archers bar the way, an
ink sightline runs from the camp to the lake on "they could see the water".

## The story and the edit
1. Lured, 0 to 16.0 s: GALILEE, 1187; the column marches east; SALADIN's standard; "and then he waited"; crane under the title.
2. Saladin, 16.0 to 27.4 (Levant): CAIRO, DAMASCUS; the crusader states, JERUSALEM and the string of castles.
3. The bait, 27.4 to 51.0: Tiberias burns (A); the rescue route from SAFFURIYA; RAYMOND OF TRIPOLI, "don't go" (held);
   3 JULY 1187; COUNTESS ESCHIVA; cut back to KING GUY on "marched anyway".
4. Across the dry hills, 51.0 to 64.9: heat veil; 20,000 counter; horse archers ride round, volleys; the way to water blocked.
5. The dry plateau, 64.9 to 85.3: Saladin's army between them and the lake; vultures; the sightline; night: the fire runs down
   the line; smoke drifts into the camp.
6. The Horns of Hattin (climax), 85.3 to 106.7: the break-out toward C the springs and D the Horns; the army breaks into pieces
   (top-down); circling the saddle as KING GUY'S TENT is surrounded and falls (4 JULY 1187); the king taken.
7. A cup of water, 106.7 to 114.4: Saladin's standard walks up to the king; pull back over the Horns.
8. Jerusalem, 114.4 to 131.0 (Levant): 2 OCTOBER 1187 ("without a massacre"); 1191, RICHARD THE LIONHEART reaches ACRE.
9. The lesson, 131.0 to 141.6: the empty hazy hills and the Horns; end card at 137.35 s.

## Exact steps to re-make it
`node films/lib/battlemap/tools/scenes.mjs films/battles/hattin`; stills; `check.cjs --line battle-map`; render with rc-render
`films.yml` (`inputs[film]=films/battles/hattin`); sound only with `remux.yml`. Local 640x360 smoke test: 0.8 to 1.7 s a still
after a 15 s start.

## Weak spots
- The Levant is stylised (simplified territories); the Galilee map is not to scale (Saffuriya to Tiberias is stretched).
- The ring of Saladin's army forms by riding round the horns at map speed; fast on the map by design.
- The fire's smoke columns are engine puffs and the drifting smoke a 2D overlay, tuned to read at night.

## Known traps (this film)
Cue spellings: "Tiberius" (`l03`), "Hatton" (`l01`), "Hatim" (`l09`), "Hateen" (`l15`); `l04.go.#1` is the second "don't go".

## Sources of truth
`films/battles/hattin/NOTES.md`, `spec.js`, `kinds.js`, `fx.js`, `film.json`, `cues.json`, `ad.json`, `ledger.json`,
`audio/score.json`, `films/lib/score/hints/hattin.json`, `docs/LOG.md` (22 Oct).
