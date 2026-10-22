# NOOR · Tonight's Juz · Juz Thirty (Juz Amma): Lantern Road build

Sample film for the NOOR Ramadan 2027 series (strand "Tonight's Juz", Night 30). 16:9, rendered at 1280x720, delivered 1920x1080,
24 fps. Picture follows `audio/mix.m4a` and `cues.json` (written by `films/noor/lib/place.py` from `noor-sound.yml`); never retimed.
Every shot time is a reference to a narration line or word (`shots.js`, `resolver`), so the picture re-fits itself to any new take.

## Files
- `scene.js` boot, camera, per-frame context `F`, captions (display text from cues, timed by the spoken words), title and end cards.
- `shots.js` the shot table (20 shots) and captions. `gfx.js` the teaching graphics on the crisp overlay. `lib.js` shared helpers:
  lanterns (fanous), oil lamp, stars, crescent, Arabic setting. `kf.js` and `paint.js` from Kleidion (kf.js changed to a 1280x720 frame).
- `sets/`: `study` (room, rehal and mushaf, niche with three lanterns, oil lamp), `path` (garden hill, thirty lanterns), `page`
  (indigo illuminated page, gold on blue), `mountain` (Jabal an-Nur at night, the cave as a light), `night` (the Night of Decree over
  flat roofs, the rope of ten lanterns), `bedroom` (child's room at night, nobody in it), `sky` (lantern sky, then dawn).

## Rules kept
- No person, prophet or angel is shown in any form; no figure, face or silhouette. Revelation is a light on the mountain.
- Qur'anic Arabic only from `script.json` `arabic` (King Fahd Complex Uthmani text via quranenc / npm quran-json), set in Amiri Quran
  (OFL). That text writes open (staggered) tanween with U+065E and U+0656; Amiri draws them at U+08F1 and U+08F2, so `forAmiri()` maps
  them for display only (97:3). Every Arabic line was looked at rendered.
- Meanings under the Arabic replace the caption for those lines (`noCap`), so no line of type is on screen twice.
- No em or en dashes, no "..." on screen.

## Shot list (scenes and why each cut happens)
| shot | set | covers | why the cut |
|---|---|---|---|
| s01 | study | cold open c1 | the place where a juz is read; slow push to the open mushaf |
| s02 | sky | title | new place (the sky): one lantern rises under the title, Arabic عَمَّ |
| s03 | path wide | w1 | thirty parts: thirty dark lanterns up the hill, the thirty arches draw |
| s04 | path climb | w2, w3 start | change of scale: the camera climbs as the lanterns light one per night; the 30th on "the last one" |
| s05 | page | w3 "People call it" | to the page where the first word is written: عَمَّ in gold |
| s06 | page wide | w4 | new information: 37 rosettes fill as the count runs to 37 |
| s07 | study niche | e1 | three treasures: three lanterns light in the niche |
| s08 | page | t1a | the first treasure's name in its gold band (al-Alaq) |
| s09 | mountain | t1b | where it came down: Jabal an-Nur, the cave a light |
| s10 | page | t1c, t1d | 96:1 written with its meaning; "the last part / the first words" |
| s11 | night wide | t2a, t2b | al-Qadr: the still bright night; 97:1 |
| s12 | night closer | t2c, t2d | 97:3; a thousand months counted, then "more than 83 years" |
| s13 | night roofs | t2e | when: ten lanterns 21 to 30, the odd ones brighten |
| s14 | page | t3a, t3b | al-Ikhlas: the four verses land one by one |
| s15 | page wide | t3c | one third of a circle fills with gold |
| s16 | bedroom wide | m1, m2 | before sleep: al-Falaq and an-Nas named |
| s17 | bedroom close | m3 | the lamp turned low by the bed: "you can do the same" |
| s18 | sky full | l1 | thirty lanterns over the hills |
| s19 | study lamp | l2 | "Do not put the lamp out": the flame, steady |
| s20 | sky dawn | l3, end | time passes (dissolve): dawn, Eid morning; end card |

Ambient life in every wide: lamp flicker and smoke, dust in the lamp light, twinkling stars, fireflies, drifting haze, swaying palms and
cypresses (shader wind), house lamps flickering in the valley.

## Weak spots (honest)
- Rooms are simple painted boxes; the rehal and bed are flat shapes up close.
- The page shots carry the teaching; between graphics the indigo page is plain for a few seconds.
- The mountain shot is dark; the cave light is small on a phone.
- Built and checked against a mock timing first; checked again on the real narration before the render.
