# Film: The Battle of Hastings (`battle-map-hastings`), Battle Map v2

A 155.4 s, 16:9 Battle Map film: 1066, three kings in one year, the English shield wall on Senlac hill, William's feigned
flight, Harold's fall and a French-speaking king whose words changed English. Two maps: England, the Channel and Normandy
(the build-up and the coronation), and the battlefield `bat` (the ridge, the gentle south slope, marshy ponds and woods,
the London road). Made on v1 on 21 Oct, re-directed on v2 on 22 Oct, rendered and re-scored on 22 Oct.
Style: `docs/manual/styles/battle-map.md`; reference film: `battle-map-cannae.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/hastings/` |
| Length, frames | 155.401 s, 3,730 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 8 scenes, 30 shots, average shot 5.2 s |
| Teams | England royal blue (`carthage`), Normandy deep red (`rome`), Norway gold |
| Narration | 18 lines, 349 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 12.47 s |
| Score | `medieval_europe`, G dorian, 76 bpm, lute and fiddle, dry tabor; swell at the feigned flight (`l12`); mix -14.1 LUFS, voice 17.0 dB over |
| Render | rc-render `films.yml`, 22 Oct (run id not recorded); final score by `remux.yml` (-14.2 LUFS; run id not recorded) |
| Release | rc-render `kino-films`: `battle-map-hastings.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-hastings-v2.mp4` |
| Cost | US$0.23496 (Lyria US$0.08, voice US$0.15496; cap US$0.60); render and score free |
| Sam's verdict | v1 battles (22 Oct): see Cannae; v2: waiting |

## Files that make it
`film.json`, `index.html`, `spec.js`, `cues.json`, `ad.json`, `audio/` (vo, casting, Lyria music and beat map, `mix_lyria.m4a`,
`score_plan.json`, `score.json`, `mix.m4a`), `ledger.json`, `NOTES.md`; score steering `films/lib/score/hints/hastings.json`.
No film-side code: the v1 cartoon icons (crowns, crosses, bursts, question marks, books, helmet, tapestry, laurel) were removed;
the only glyphs left are the galleys (who crosses the sea, and when).

## The story and the edit
1. The hill at dawn, 0 to 17.4 s (bat): 1066, three kings in one year; crane up under the title card.
2. The crown, 17.4 to 34.3 (main): Harold crowned in London, William across the sea; the hold through "excuse me, that crown
   was promised to me"; galleys gather on "fleet".
3. Two invasions, 34.3 to 53.9 (main): Stamford Bridge, then William lands at PEVENSEY; the 250 MILES counter rides Harold's
   march back; hold on "Busy month."
4. The hill, 53.9 to 73.0 (bat): 14 OCTOBER 1066, the shield wall locks, William's army forms below; hold on "Not fun."
5. The wall holds, 73.0 to 98.1: volleys, knights uphill into the axes, the rumour, the panic, the rally.
6. The trick, 98.1 to 117.2: the feigned flight shown wide from above, then closer and lower, then wide again for the repeat.
7. The king falls (climax), 117.2 to 134.7: Harold's standard sinks; slow orbit over it (caption BAYEUX TAPESTRY, 1070s);
   cut on "Without".
8. The Conqueror, 134.7 to 155.4 (main): Westminster Abbey; BUEF, JUREE, JUGE ride across the Channel on "beef, jury and
   judge"; end card at 151.2 s.
Legend: ENGLAND (King Harold), NORMANDY (Duke William), NORWAY (Harald Hardrada); strengths about 7,000 a side labelled
MEN, ESTIMATED (sources vary from about 5,000 to 13,000); units Foot soldiers, Archers, Knights; places A The Channel,
B Stamford Bridge, C Senlac Hill. Full table: `films/battles/hastings/NOTES.md`.

## Sound
Same route as Cannae: `codead.yml` prep (21 Oct) and `battle_mix.py`, then `remix.py` with `hints/hastings.json` (battle
`l08`, turn `l12`, result `l14` aftermath, epilogue `l17`: "the swell at the feigned flight; Harold's fall is sober; the
coronation lifts; the French words at the end are light"), `cues_from_score.py`, `remux.yml`.

## Exact steps to re-make it
`node films/lib/battlemap/tools/scenes.mjs films/battles/hastings`; stills with `tools/stills.cjs`; `node films/director/check.cjs films/battles/hastings --line battle-map`;
render `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/battles/hastings' -f 'inputs[parts]=16' -f "inputs[ref]=$(git rev-parse HEAD)"`;
sound only with `remux.yml`. Delivery as Cannae. Note: the director tests read a frozen v1 copy of this film in
`films/director/tests/fixtures/hastings-v1/`; do not point tests at the live folder.

## Weak spots
- The England map is stylised and not to scale; the Channel is narrow.
- The battlefield shows one English line of 8 blocks; the real wall was longer and deeper.
- The arrow in Harold's eye is not drawn (the narration says historians argue; the picture does not take sides).

## To make a new one like it
`docs/manual/styles/battle-map.md`; this film is the model for a two-map battle where the field is a full-screen second stage.

## Sources of truth
`films/battles/hastings/NOTES.md`, `spec.js`, `cues.json`, `film.json`, `ad.json`, `ledger.json`, `audio/score.json`,
`films/lib/score/hints/hastings.json`, `docs/LOG.md` (21 and 22 Oct).
