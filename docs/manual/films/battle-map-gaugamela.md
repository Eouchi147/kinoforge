# Film: The Battle of Gaugamela (`battle-map-gaugamela`), Battle Map v2

A 151.3 s, 16:9 Battle Map film: 331 BC, young Alexander against Darius III on a plain levelled for scythed chariots; the march
sideways, the chariots that fail, the gap, the wedge, Darius running, and an empire that changes hands. Made on v1 on 21 to
22 Oct (second group of four), re-directed on v2 on 22 Oct, rendered and re-scored the same day.
Style: `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/gaugamela/` |
| Length, frames | 151.252 s, 3,631 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 9 scenes, 27 shots, average shot 5.6 s; `scenes.mjs` 0 errors, 0 warnings |
| Teams | Macedon deep red (`rome`), Persia royal blue (`carthage`); dawn haze, bright day, a low red sun as Darius runs |
| Narration | 17 lines, 330 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 14.58 s |
| Score | `middle_east_central_asia`, D hijaz, 72 bpm, ney-like flute, oud and darbuka; swell as Alexander's wedge charges the gap; mix -14.09 LUFS, voice 16.9 dB over |
| Render | rc-render `films.yml`, 22 Oct (run id not recorded); final score by `remux.yml` (-14.2 LUFS; run id not recorded) |
| Release | rc-render `kino-films`: `battle-map-gaugamela.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-gaugamela-v2.mp4` |
| Cost | US$0.23376 (Lyria US$0.08, voice US$0.15376; cap US$0.50); render and score free |
| Sam's verdict | v1 battles (22 Oct): see Cannae; v2: waiting |

## Files that make it
`film.json`, `index.html` (imports `kinds.js` and `fx.js`), `spec.js`, `kinds.js`, `fx.js`, `cues.json`, `ad.json`, `audio/`,
`ledger.json`, `NOTES.md`; `films/lib/score/hints/gaugamela.json`.
`kinds.js`: the scythed chariot as a figure kind in `FIG_KINDS` (two horses, a car with a team breastwork, two spoked wheels
each with a blade out of the hub, a driver), used with `figures: 'chariot'` (kind stays `cavalry` for the tray), and the flat
unit symbol `u-chariot` (`registerIcon`) for the legend. `fx.js`: only the empire as a hatched territory with an inked edge on
the `asia` map, growing on "master of the Persian Empire" and "stretched from Greece to India". The v1 cartoon icons are gone;
the levelled ground is a dashed ink ring and a lettered place, the gap a gold dashed ring with one tag.

## The story and the edit
1. A young king, 0 to 19.6 s: low behind Alexander's horsemen; the Persian host rises; 1 OCTOBER 331 BC; crane up under the title.
2. The road east, 19.6 to 32.1 (asia map): GRANICUS, 334 BC and ISSUS, 333 BC; PERSIA / Darius III; his biggest army yet.
3. The trap on the plain, 32.1 to 52.1: River Tigris (A), the levelled ground ringed on "smoothed" (B), a chariot close at 45 mm,
   the planned charge as five dashed blue arrows.
4. Sideways, 52.1 to 79.6: 47,000 counter; cut low on "Nobody knows exactly", caption ONE ANCIENT WRITER SAYS 1,000,000 on "truly
   ridiculous"; the army slides east and the Persian line stretches to follow.
5. The chariots charge, 79.6 to 92.1: the columns step apart into lanes; the chariots are stopped at the back; cut on "So much
   for the secret weapon".
6. The gap, 92.1 to 112.6: THE GAP opens; the decisive moment wide from above: the COMPANION CAVALRY wedge drives at DARIUS.
7. The king runs (climax), 112.6 to 124.6: closer and lower (40 mm): Darius's chariot turns and runs; PARMENION under attack;
   Alexander turns back.
8. The army falls apart, 124.6 to 136.1: low red sun; the Persian blocks thin; Darius's lone chariot over the Tigris; 330 BC.
9. Master of Asia, 136.1 to 151.3 (asia map): the empire as a hatched red territory stretching from GREECE to INDIA; end card at 147.05 s.

## Exact steps to re-make it
`node films/lib/battlemap/tools/scenes.mjs films/battles/gaugamela`; stills; `check.cjs --line battle-map`; render with
rc-render `films.yml` (`inputs[film]=films/battles/gaugamela`); sound only with `remux.yml`. Measured locally only as a 640x360
smoke test (about 3.5 s a frame after a 27 s start); full-quality stills on runners.

## Weak spots
- The army sizes are symbolic: five small chariot blocks stand for about 200 chariots, four elephants for fifteen.
- The asia map is schematic and not to scale.
- The Persian strength is left blank in the legend on purpose (the narration says nobody knows).
- Labels are placed by hand; no collision avoidance with the legend panels.

## Sources of truth
`films/battles/gaugamela/NOTES.md`, `spec.js`, `kinds.js`, `fx.js`, `film.json`, `cues.json`, `ad.json`, `ledger.json`,
`audio/score.json`, `films/lib/score/hints/gaugamela.json`, `docs/LOG.md` (22 Oct).
