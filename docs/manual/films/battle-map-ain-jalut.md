# Film: The Battle of Ain Jalut (`battle-map-ain-jalut`), Battle Map v2

A 139.6 s, 16:9 Battle Map film: 1260, the Mongols who almost never lost meet the Mamluks of Egypt in a valley in Palestine;
the threat and the rude answer, the Khan's death, Baybars's feigned retreat, the ambush from the hills, Qutuz's rally, and two
and a half centuries of Mamluk Egypt. Made on v1 on 21 to 22 Oct (second group of four), re-directed on v2 on 22 Oct, rendered
and re-scored the same day (its remux was cancelled once and re-run). Style: `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/ain-jalut/` |
| Length, frames | 139.628 s, 3,352 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 9 scenes, 23 shots, average shot 6.1 s; `scenes.mjs` 0 errors, 0 warnings |
| Maps | `emp`: Asia, the Middle East and Eastern Europe (1 degree of longitude = 6 units, of latitude = 8; not to scale in the Levant) for the opening and the epilogue; main stage: the valley of Ain Jalut (Goliath's Spring in the west) |
| Teams | Mamluks deep red (`rome`), Mongols royal blue (`carthage`) |
| Narration | 17 lines, 315 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 13.61 s |
| Score | `middle_east_central_asia` with Central Asian colour: E minor pentatonic, 84 bpm, bowed solo (solo violin), galloping steppe drum; swell at the ambush; mix -14.12 LUFS, voice 17.3 dB over |
| Render | rc-render `films.yml`, 22 Oct (run id not recorded); final score by `remux.yml` (-14.2 LUFS; cancelled once and re-run; run id not recorded) |
| Release | rc-render `kino-films`: `battle-map-ain-jalut.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-ain-jalut-v2.mp4` |
| Cost | US$0.22048 (Lyria US$0.08, voice US$0.14048; cap US$0.50); render and score free |
| Sam's verdict | v1 battles (22 Oct): see Cannae; v2: waiting |

## Files that make it
`film.json`, `index.html` (imports `kinds.js` and `fx.js`), `spec.js`, `kinds.js` (the unit symbol `u-horse-archers`),
`fx.js` (only the territory ink: the Mongol Empire spreading from Mongolia at the start, the Mamluk realm spreading from Cairo
at the end, with a thin edge), `cues.json`, `ad.json`, `audio/`, `ledger.json`, `NOTES.md`; `films/lib/score/hints/ain-jalut.json`.
The v1 icons (censored scroll, hat, mirror, smirk and others), bouncing crowns, bursts, question marks and the timeline bar are
gone; the letters ride the dashed message routes as the engine's flat scroll glyph (a message really travelled). The feigned
retreat is told by choreography and ink; the hidden army appears only on "the main Mamluk army was waiting".

## The story and the edit
1. Almost never lost, 0 to 18.6 s (emp): MONGOLIA, the empire spreads like ink; the horsemen's arrow west into PALESTINE.
2. The empire, 18.6 to 28.4: CHINA to EASTERN EUROPE; BAGHDAD, 1258; DAMASCUS.
3. Surrender or else, 28.4 to 42.1: HULAGU's message rides to CAIRO; the answer rides back; hold on "Let's leave it at that".
4. Luck changes, 42.1 to 60.1: AUGUST 1259, KARAKORUM; KITBUQA and the smaller army; SULTAN QUTUZ and BAYBARS march.
5. The valley, 60.1 to 74.7: 3 SEPTEMBER 1260; A Ain Jalut, B the valley, C the Hills of Galilee; the Mongol horsemen.
6. The feigned retreat, 74.7 to 87.4: Baybars rides out, turns, runs up the valley; the Mongols charge after him.
7. Ambush (climax), 87.4 to 113.7: the main Mamluk army rises; hit from both sides (top-down); the line bows; QUTUZ rides in
   (45 mm); the second charge; KITBUQA's block thins; MONGOL EMPIRE dims.
8. Never conquered, 113.7 to 130.9 (emp): AIN JALUT marked; the Mongol arrow stops at a gold dashed line; SULTAN BAYBARS.
9. Two and a half centuries, 130.9 to 139.6: the Mamluk realm spreads from Cairo to Syria; caption 1260 TO 1517; end card at 135.43 s.

## Exact steps to re-make it
`node films/lib/battlemap/tools/scenes.mjs films/battles/ain-jalut`; stills; `check.cjs --line battle-map`; render with
rc-render `films.yml` (`inputs[film]=films/battles/ain-jalut`); sound only with `remux.yml`. Local 640x360 smoke test: 0.9 to
4.2 s a still after a 20 s start.

## Weak spots
- The Mediterranean on the `emp` map is drawn as an inland sea and reads like a lake at close zoom (unchanged from v1).
- Kitbuqa's death is told by his block thinning and the legend dimming (no wounds, by design).
- The map blocks are symbols (`figScale` 1.4), not armies to scale.

## Known traps (this film)
Cue spellings: "Angelut" (`l01`), "Ainjalut," (`l06`), "Babers" (`l08`), "mondles" (`l11`), "Khutuz" (`l12`), "Kitbuka" (`l13`),
"Katoos" (`l15`); screen text is spelled correctly.

## Sources of truth
`films/battles/ain-jalut/NOTES.md`, `spec.js`, `kinds.js`, `fx.js`, `film.json`, `cues.json`, `ad.json`, `ledger.json`,
`audio/score.json`, `films/lib/score/hints/ain-jalut.json`, `docs/LOG.md` (22 Oct).
