# Film: The Battle of Thermopylae (`battle-map-thermopylae`), Battle Map v2

A 164.1 s, 16:9 Battle Map film: 480 BC, the biggest army ever seen against a few thousand Greeks at a narrow pass between a
cliff and the sea; the waiting, the arrows, the shield wall that takes turns, the hidden path, the last stand, Salamis and
Plataea, and the stone with the epitaph. Written, voiced and rendered on v1 on 21 to 22 Oct (the second group of four), then
re-directed on v2 on 22 Oct and rendered and re-scored the same day. Style: `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/thermopylae/` |
| Length, frames | 164.113 s, 3,939 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 9 scenes, 32 shots, average shot 5.1 s; `scenes.mjs` 0 errors, 0 warnings; `check.cjs` one soft note (galley glyphs at Salamis, kept) |
| Teams | Persia red (`rome`), Greek allies blue (`carthage`) |
| Narration | 18 lines, 397 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 13.07 s |
| Score | `ancient_med`, E phrygian, 58 bpm (archaic, severe); swell when the Immortals climb the hidden path; elegy for the Spartans; a small lift at Salamis; mix -14.09 LUFS, voice 17.1 dB over |
| Render | rc-render `films.yml`, 22 Oct (run id not recorded); final score by `remux.yml` (-14.2 LUFS; run id not recorded) |
| Release | rc-render `kino-films`: `battle-map-thermopylae.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-thermopylae-v2.mp4` |
| Cost | US$0.25448 (Lyria US$0.08, voice US$0.17448; cap US$0.50); render and score free |
| Sam's verdict | v1 battles (22 Oct): see Cannae; v2: waiting |

## Files that make it
`film.json`, `index.html` (imports `units.js`), `spec.js`, `units.js`, `cues.json`, `ad.json`, `audio/`, `ledger.json`,
`NOTES.md`; `films/lib/score/hints/thermopylae.json`. `units.js` registers four flat glyphs in the v2 style: `pass` (a cliff,
a narrow road and the sea), `trail` (a mountain with a dashed path), `stele` (the stone with the epitaph), `lambda` (a
Spartan shield, the Greek banner in the legend). No new terrain feature: the pass is the engine's `mountains` wall against a
`sea`, the coast road a `road`, the hidden path a thin `road` over the mountains. The night is a blue scrim card over a low
sun; the empire is shown by its armies rising from Egypt to India; the numbers are engine counters.

## The story and the edit
1. The invasion (Aegean map), 0 to l02: Persian columns cross into Greece (480 BC); push in to the tiny Greek block.
2. King of Kings (empire map), l02 to l03: XERXES; armies rise from Egypt to India; 1,000,000 by the ancient writers counts down
   to 100,000 by the modern ones; cut on "Still, a lot."
3. The allies (Aegean map), l03 to l04: rival cities team up; blue routes converge.
4. The pass, l04 to l06: why here; A Thermopylae, B the mountains, C the sea; about 7,000 Greeks, LEONIDAS, 300 SPARTANS.
5. The wait, l06 to l08: four days; cut to the front rank on "They did not."; the arrows; DIENEKES ("fight in the shade").
6. Wave after wave, l08 to l11: the front rank steps back through its lane; the Immortals fail; the king's standard jumps three
   times; two days on, the wall stands.
7. Surrounded (climax), l11 to l15: EPHIALTES; the hidden path (D); the night climb; most Greeks leave; 700 THESPIANS stay; the
   ring closes wide from above, then closer and lower; pull back on "So, the Persians won."
8. The war (Aegean map), l15 to l17: Athens burns; Salamis (galleys); Plataea, 479 BC.
9. The stone, l17 to the end: the empty pass in the evening, the epitaph card on the words, the end card.
Legend: PERSIA (Xerxes, 100,000, the modern estimate the line gives), GREEK ALLIES (Leonidas of Sparta, 7,000); units Hoplites,
Infantry and Archers; places A to D.

## Exact steps to re-make it
`node films/lib/battlemap/tools/scenes.mjs films/battles/thermopylae`; stills; `check.cjs --line battle-map`; render with
rc-render `films.yml` (`inputs[film]=films/battles/thermopylae`); sound only with `remux.yml`.

## Weak spots
- The Aegean and the empire are rough hand maps, not to scale; their armies are a few large figures on trays.
- The night is a blue scrim over a low sun, not a true night light.
- Each Persian wave marches up, presses, thins and melts away in about 6 s (compressed, as in every Battle Map film).
- The legend panels cover the left quarter of the frame.

## Known traps (this film)
The cues spell some words oddly ("Dianik," for Dienekes, "Effialty's" for Ephialtes, "Thespier" for Thespiae, "past" for
"pass" in `l10` and `l17`): the spec refers to neighbouring words.

## Sources of truth
`films/battles/thermopylae/NOTES.md`, `spec.js`, `units.js`, `film.json`, `cues.json`, `ad.json`, `ledger.json`,
`audio/score.json`, `films/lib/score/hints/thermopylae.json`, `docs/LOG.md` (22 Oct).
