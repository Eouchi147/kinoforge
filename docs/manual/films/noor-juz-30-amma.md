# Film: NOOR, Tonight's Juz, Juz Thirty, Juz Amma (`noor-juz-30-amma`)

A 139.0 s, 16:9 look sample for the NOOR Ramadan 2027 series (strand "Tonight's Juz", night 30): what the thirtieth part of
the Qur'an holds, taught with lanterns and an illuminated page: thirty parts, 37 surahs, the first words (96:1), the Night of
Decree (97:1, 97:3, a thousand months is more than 83 years, the odd nights of the last ten), al-Ikhlas (a third of the
Qur'an), and the three surahs before sleep. Lantern Road style; no person, prophet or angel shown in any form (the bedroom is
empty); Qur'anic Arabic set in code in Amiri Quran. Built and rendered on 22 Oct, delivered 23 Oct (UTC), waiting on Sam's
verdict. Styles: `docs/manual/styles/noor.md`, `docs/manual/styles/lantern-road.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/noor/j30-amma/` |
| Length, frames | 138.976 s, 3,336 frames at 24 fps |
| Picture | Lantern Road 16:9; rendered 1280x720, delivered 1920x1080 |
| Script | `script.json`: 24 lines, 346 words; sources Qur'an 96:1-5, 97:1-5, 112:1-4, 113, 114; Sahih al-Bukhari 3, 2017, 5013, 5017 |
| Narration | Chatterbox (free), `noor-sound.yml` |
| Score | `middle_east_central_asia`, D dorian, flute solo, seed 30; mix -14.07 LUFS, voice 16.8 dB over |
| Render | kinoforge `films-render.yml` (run id not recorded); re-rendered on 22 Oct after the Arabic spacing fix |
| Release | kinoforge `films`: `noor-juz-30-amma.mp4`, `-preview.mp4`, `-sheet.jpg`, `-poster.jpg` |
| Cost | US$0 |
| Sam's verdict | waiting |

## Files that make it
`script.json`, `ad.json`, `audio/` (vo, `vo.json`, `score_plan.json`, `score.json`, `mix.m4a`), `cues.json`, `film.json`,
`index.html`, `scene.js` (boot, camera, per-frame context `F`, captions timed by the spoken words, title and end cards),
`shots.js` (20 shots; every time a reference to a line or word via `resolver`), `gfx.js` (teaching graphics on the crisp
overlay: 30 arches, 37 rosettes, 1,000 months to 83 years, ten lanterns with the odd nights, the one-third circle), `lib.js`
(lanterns, oil lamp, stars, crescent, Arabic setting with `forAmiri()`), `kf.js` (from Kleidion, changed to a 1280x720 frame),
`paint.js`, `sets/` (`study` with the rehal, mushaf, niche and three lanterns; `path`, a garden hill of thirty lanterns; `page`,
an indigo illuminated page, gold on blue; `mountain`, Jabal an-Nur at night with the cave as a light; `night`, the Night of
Decree over flat roofs with a rope of ten lanterns; `bedroom`, a child's room at night with nobody in it; `sky`, a lantern sky
then dawn; `index`), `NOTES.md`.

## Shot list (20 shots)
s01 study, cold open | s02 sky, title with عَمَّ | s03 path wide, thirty dark lanterns, the arches draw | s04 path climb, one lantern
a night, the 30th on "the last one" | s05 page, عَمَّ in gold | s06 page wide, 37 rosettes | s07 study niche, three treasures |
s08 page, al-Alaq | s09 mountain, the cave a light | s10 page, 96:1 with its meaning | s11 night wide, al-Qadr, 97:1 |
s12 night closer, 97:3, a thousand months, more than 83 years | s13 night roofs, ten lanterns 21 to 30, the odd ones brighten |
s14 page, al-Ikhlas verse by verse | s15 page wide, one third of a circle fills | s16 bedroom wide, al-Falaq and an-Nas named |
s17 bedroom close, the lamp turned low | s18 sky full, thirty lanterns | s19 study lamp, "Do not put the lamp out" | s20 sky dawn
(dissolve: time passes), Eid morning, end card. Ambient life: lamp flicker and smoke, dust in the light, twinkling stars,
fireflies, drifting haze, palms and cypresses swaying (shader wind), house lamps in the valley.

## Exact steps to re-make it
1. Sound: `noor-sound.yml` with `inputs[films]=films/noor/j30-amma`.
2. Stills: `node films/noor/n05-iqra/tools/stills.cjs films/noor/j30-amma --shots --out out/amma`; look at every Arabic line.
3. Render: kinoforge `films-render.yml` with `inputs[film]=films/noor/j30-amma`; check; deliver.

## Fixes made on 22 Oct
More space between every Arabic line and the English under it (in the al-Ikhlas panel the kasra no longer touches the meaning;
96:1, 97:1, 97:3 and the al-Falaq and an-Nas names too), checked at 1280x720, then re-rendered.

## Weak spots
- Rooms are simple painted boxes; the rehal and bed are flat shapes up close.
- The page shots carry the teaching; between graphics the indigo page is plain for a few seconds.
- The mountain shot is dark; the cave light is small on a phone.
- Built and checked against a mock timing first; checked again on the real narration before the render.

## Sources of truth
`films/noor/j30-amma/NOTES.md`, `script.json`, `shots.js`, `gfx.js`, `lib.js`, `film.json`, `audio/score.json`,
`.github/workflows/noor-sound.yml`, `docs/LOG.md` (22 Oct).
