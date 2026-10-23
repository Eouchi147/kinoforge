# Film: NOOR, The Descent, Night Five, Iqra (`noor-descent-05-iqra`)

A 158.8 s, 16:9 look sample for the NOOR Ramadan 2027 series (strand "The Descent", night 5): the first revelation in the
cave of Hira on Jabal an-Nur, told in the Lantern Road style with no person ever drawn. The Prophet's presence is a hand
lantern alone on the mountain path, the empty cave, the mat where he sat, the lantern set down at his door; the angel is
light only; Qur'an 96:1-5 is set in code in Amiri Quran from the King Fahd Complex text. Built and rendered on 22 Oct,
delivered 23 Oct (UTC), waiting on Sam's verdict. Styles: `docs/manual/styles/noor.md` (the rules),
`docs/manual/styles/lantern-road.md` (the technique).

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/noor/n05-iqra/` |
| Length, frames | 158.836 s, 3,813 frames at 24 fps |
| Picture | Lantern Road 16:9 (`kf.js` from Kleidion with a 1280x720 design frame); rendered 1280x720, delivered 1920x1080 |
| Script | `script.json`: 30 lines, 398 words; sources Qur'an 96:1-5, Qur'an 2:185, Sahih al-Bukhari 3 |
| Narration | Chatterbox (free, on the runner), `noor-sound.yml` |
| Score | free score engine, `middle_east_central_asia`, D hijaz, flute solo, seed 5; mix -14.06 LUFS, voice 16.6 dB over |
| Render | kinoforge `films-render.yml` run 39822483930 (part 11 hung 4.5 h: cancelled and re-ran the failed part) |
| Release | kinoforge `films`: `noor-descent-05-iqra.mp4`, `-preview.mp4`, `-sheet.jpg`, `-poster.jpg` |
| Cost | US$0 |
| Sam's verdict | waiting (voice, look) |

## Files that make it
`script.json` (display text, spoken `say` forms, gaps, score moods, the Arabic), `ad.json` (written by `place.py --prep`),
`audio/vo/*.mp3`, `audio/vo.json`, `audio/score_plan.json`, `audio/score.json`, `audio/mix.m4a`, `cues.json`, `film.json`,
`index.html`, `scene.js` (boot, camera, per-frame context, dissolves), `shots.js` (the shot plan and captions; every cut a cue
reference), `type.js` (captions, labels, title and end cards, the word, the verse panel), `kf.js` (multiplane core and post
chain), `paint.js`, `ambient.js` (from Kleidion), `fx.js` (glows, hand lantern, fanous, twinkling stars), `sets/` (`mountain`
with modes night, dusk, light, dawn; `cave` looking out, with the mat, water skin, dates, clay lamp; `valley`, Makkah at dusk
with the Kaaba and small idols in a ring; `house`, a lit doorway with the folded cloak and the lantern on the step; `sky`; and
`common`, `index`), `tools/stills.cjs`, `NOTES.md`; fonts `films/noor/fonts/`.

## Shot list (scene: shots)
1. Cold open: `o1` a dark peak, one lamp high in the rock; slow push.
2. Title: `title` a lantern rises; NOOR, The Descent, Night Five, Iqra, the word in Arabic.
3. Where: `a1` mountain at dusk, `a2` inside the cave, `a3` closer with JABAL AN-NUR and HIRA labels (changes of scale).
4. The valley: `b1` loud life, the idols round the Kaaba.
5. One man: `c1` the hand lantern climbs the path; `c2` closer, label AL-AMIN, the lantern reaches the cave; `d1` water, dates, the lamp.
6. The night: `e1` the cave mouth fills with light; `e2` the sky behind the peak is light; `e3` the word writes itself, READ;
   `e4` light breathes on each ask; `e6` close on the mat, the third ask.
7. The first words: `v` the illuminated panel draws itself, each verse with its meaning (captions off: the panel carries them).
8. What it means: `f1` the word stays; `f2` the lantern hurries down; `f3` the house doorway, the cloak, the lantern on the step.
9. Time: `f4` dawn (dissolve: the stars wheel).
10. The lantern sky: `l` one lantern rises with the word; end card "NOOR · Thirty Nights of Light · Tomorrow · Night Six".

## Exact steps to re-make it
1. Sound: `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/noor-sound.yml/dispatches -f ref=main -f 'inputs[films]=films/noor/n05-iqra'`
   (delete `audio/vo.json` first to re-voice). Pull.
2. Stills: `node films/noor/n05-iqra/tools/stills.cjs films/noor/n05-iqra --shots --out out/iqra` (`--param dbg=1`,
   `noglows=1`, `glowoff=i`, `hide=plane`).
3. Render: `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/films-render.yml/dispatches -f ref=main -f 'inputs[film]=films/noor/n05-iqra'`.
4. Check that no person appears in any frame and every Arabic line renders correctly; deliver.

## Fixes made on 22 Oct
- The glow texture is uploaded before the bloom reads it.
- The single word Iqra (title, e3, the lantern end) redrawn as a clean filled glyph run with no outline stroke: dark ink
  `#2C2416` over a soft warm glow on bright light, gold over a soft dark halo at night; written on by a wipe.

## Weak spots
- Wide sets are painted at screen density; the closest lenses (a3, c2 at 64 to 74 mm) soften the peak (painted at q 2 to help).
- The valley houses are simple boxes; the Kaaba and idols are tiny by design (wide only).
- Dusk and dawn warmth comes from tinting the painted sky (a big glow mesh leaked over the peak and was removed).

## To make a new one like it
`docs/manual/styles/noor.md` "Exact steps"; copy this folder's structure for a 16:9 night with a mountain and an interior.

## Sources of truth
`films/noor/n05-iqra/NOTES.md`, `script.json`, `shots.js`, `film.json`, `audio/score.json`, `films/noor/lib/place.py`,
`.github/workflows/noor-sound.yml`, `films-render.yml`, `docs/LOG.md` (22 Oct), `docs/STATUS.md` (NOOR).
