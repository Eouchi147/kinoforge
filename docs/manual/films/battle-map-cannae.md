# Film: The Battle of Cannae (`battle-map-cannae`), Battle Map v2, the reference film

A 157.6 s, 16:9 Battle Map film for kids 8 to 14 and curious adults: Hannibal's double envelopment of the Roman army on
2 August 216 BC, explained on a living engraved relief map with soldier figures on trays, ink arrows, a legend and planned
cameras. It is the reference film of the v2 engine (`films/lib/battlemap/`): every later battle copies its structure. First
made on v1 on 21 Oct 2026; re-directed on v2 on 22 Oct after Sam's verdict on v1; rendered and given the final free score on
22 Oct. Style: `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/battles/cannae/` |
| Length, frames | 157.629 s, 3,784 frames at 24 fps |
| Picture | rendered 1280x720, delivered 1920x1080 |
| Plan | 9 scenes, 26 shots, average shot 6.1 s; `scenes.mjs` 0 errors, 0 warnings |
| Teams | Rome deep red (`rome`), Carthage royal blue (`carthage`) |
| Light | morning haze, golden day, a low red sun in the evening |
| Narration | 18 lines, 354 words, ElevenLabs `eleven-v4` `brian`; title line `l01` at 17.4 s |
| Score | free score engine, `ancient_med`, D dorian, 62 bpm; mix -14.1 LUFS, voice 16.8 dB over the score |
| Render | rc-render `films.yml` run 39798701933; remux run 39817058161 (-14.2 LUFS, 157.6 s) |
| Release | rc-render `kino-films`: `battle-map-cannae.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/battle-map-cannae-v2.mp4` |
| Cost | US$0.2384 (prep: Lyria US$0.08, voice US$0.1584; cap US$0.90); render and score free |
| Sam's verdict | v1 (22 Oct): good concept, music not right, no emoji graphics, wants a legend, planned cameras, armies that never clip. v2: waiting |

## Files that make it
`film.json` (id, sizes, duration, `audio`), `index.html` (fonts, importmap, `startBattleMap`), `spec.js` (the whole film as
data), `cues.json` (narration lines and word times, music fields from the score), `ad.json` (the prep block: the 18 lines,
the voice cast, the voice brief, the Lyria prompt), `audio/vo/line*.mp3` and `audio/vo.json` (narration), `audio/casting.json`,
`audio/cast/`, `audio/music.mp3` and `music.json` (the Lyria score and beat map used for placement), `audio/mix_lyria.m4a`
(first mix, kept), `audio/score_plan.json`, `audio/score.json`, `audio/mix.m4a` (final mix), `ledger.json`, `NOTES.md`;
score steering `films/lib/score/hints/cannae.json`.

## The story and the edit (scene, time, job)
1. The host, 0 to 22.5 s: Rome sends a gigantic army; one man is about to beat it (low sweep as 12 legions rise rank by rank;
   reverse angle from Hannibal's standard; crane up into the plan view under the title card).
2. Hannibal, 22.5 to 33.9: who he is (dissolve to the Mediterranean map; the dashed route over the Alps).
3. Rome, 33.9 to 42.7: the two-headed command (the gold command star hops between VARRO and PAULLUS on "One. Day. Each.").
4. The field, 42.7 to 61.7: where and how many (2 AUGUST 216 BC; 80,000 and 50,000 counters; the heavy red arrow on "push").
5. The trap is set, 61.7 to 75.4: the centre bends into a bow; veterans at the ends; horsemen on the sides.
6. The jaws, 75.4 to 106.5: the Romans walk in, the middle gives way, the horsemen ride round, the decisive moment top-down.
7. Surrounded (climax), 106.5 to 127.8: closer and slower orbit around the ring, inside the press at 45 mm, the long pull back
   as the sun turns red; caption ABOUT 50,000 ROMANS LOST (Livy's figure is 48,200; the narration says "tens of thousands").
8. Rome refuses, 127.8 to 146.3: the twist (cut on "Nope."), new armies, Scipio, Zama.
9. The lesson, 146.3 to 157.6: the legend gives the verdict (Carthage won the battle, Rome the war); end card at 153.43 s.
Full camera plans, the living world and measurements: `films/battles/cannae/NOTES.md`.

## Sound
1. 21 Oct: `codead.yml` mode `prep` on `films/battles/cannae` (Lyria score from the `ad.json` prompt; 5 voices cast on 3 lines,
   `brian` won; Whisper word times), then `python3 films/lib/battle_mix.py films/battles/cannae` placed the lines on the
   Lyria beat grid and wrote `cues.json`, `film.json` and the first mix (now `audio/mix_lyria.m4a`).
2. 22 Oct: `python3 films/lib/score/remix.py films/battles/cannae` (hints `cannae.json`: calm hook, drums with the Roman charge
   from `l08`, the one swell at the turn `l11`, sober aftermath from `l14`, epilogue `l15`), then
   `python3 films/lib/score/cues_from_score.py films/battles/cannae` (music fields only), then rc-render `remux.yml` on the
   rendered film.

## Exact steps to re-make it
1. `node films/lib/battlemap/tools/scenes.mjs films/battles/cannae` (prints the plan; 0 errors).
2. Stills: `node films/lib/battlemap/tools/stills.cjs films/battles/cannae --t 3,17.6,40,80,112,130,150 --out out/cannae`.
3. Director check: `node films/director/check.cjs films/battles/cannae --line battle-map`.
4. Render: `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/battles/cannae' -f 'inputs[parts]=16' -f "inputs[ref]=$(git rev-parse HEAD)"`
   (the parts count used on 22 Oct is not recorded; 12 to 20 is the range).
5. Sound only: `remux.yml` with `inputs[film]=films/battles/cannae` (`docs/manual/sound/remux.md`).
6. Assembly and delivery: `films.yml` joins the parts, lays `audio/mix.m4a`, scales to 1920x1080 (crf 17, max 16 Mbps),
   makes the preview and the sheet, publishes to `kino-films`; then the check playbook and a copy to Sam's Mac with `-v2`.

## Weak spots (from NOTES.md)
- The Mediterranean map is stylised and not to scale; its armies are small groups of large figures (`figScale` 1.4).
- Figures are simple boxes at map scale (no faces, by design); in the 45 mm close shot they read as miniatures.
- Labels are placed by hand; no automatic collision avoidance with the legend panels.

## To make a new one like it
Follow `docs/manual/styles/battle-map.md` "Exact steps", copying `film.json`, `index.html` and the structure of `spec.js`
(sections `world`, `stages`, `blocks`, `moves`, `arrows`, `labels`, `counters`, `legend`, `ambient`, `scenes`, `cards`,
`msaaOn`) and the NOTES.md layout (how the battle is explained, the scene table, the living world, measured cost, weak spots).

## Sources of truth
`films/battles/cannae/NOTES.md`, `spec.js`, `cues.json`, `film.json`, `ad.json`, `ledger.json`, `audio/score.json`,
`films/lib/score/hints/cannae.json`, `docs/LOG.md` (21 and 22 Oct), `docs/SOUL.md` section 3.
