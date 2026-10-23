# Film: The Ship Called Care (`dark-corners-zong-lantern-road`), Dark Corners, Lantern Road

A 179.4 s, 9:16 Dark Corners episode (episode 2): the Zong, 1781, a British slave ship whose crew threw captives overboard
and whose owners claimed the insurance; the court case, Equiano and Sharp, and the abolition of 1807. Told in the Lantern Road
style with the lantern as the motif, and with strict restraint: no drowning, no bodies. The narration, score and sound are the
original episode mix. Made on 21 to 22 Oct; Zong was not in Sam's notes of 22 Oct, so this first KINOFORGE version stands.
Styles: `docs/manual/styles/lantern-road.md`, `docs/manual/styles/dark-corners.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/dark-corners/zong/` |
| Length, frames | 179.4 s, 4,306 frames at 24 fps |
| Picture | procedural painted 2.5D multiplane (Three.js in Chromium), Kuwahara radius 2 by default; rendered 720x1280, delivered 1080x1920 |
| Sound | the original episode mix (`audio/mix.m4a` from rc-render release `dark-films`), untouched |
| Edit | every cut on a `strong_hits` time or a narration start (the cut list is `SEQ` in `shots.js`); title card 14.9 to 17.4 s, end card 176.8 to 179.4 s |
| Render | rc-render `films.yml`, 21 to 22 Oct (run id not recorded) |
| Release | rc-render `kino-films`: `dark-corners-zong-lantern-road.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/` (among the first seven copied) |
| Cost | US$0 |
| Sam's verdict | not recorded (not in his 22 Oct notes) |

## Files that make it
`film.json`, `index.html`, `scene.js`, `shots.js` (the shot list against the cues), `common.js`, `lib.js` (multiplane placement,
relightable paint, glows, detail pass), `paint.js`, and one file per set built lazily (LRU of 3 live sets): `sea.js` +
`seaextra.js` (sea at dusk, moon and dawn, the ship, Jamaica ridge, Black River harbour, the captain with a spyglass, the name
board, the hull from the water with one rope and the climber, rain, rings), `deck.js` (night deck, swinging lantern, casks
with water level, chain), `court.js` (London court, candles that go out one by one, jury, judge, lawyer, dock), `docs.js`
(the claim, ledger, rule, the quoted line, King's Bench record with ink that writes in), `section.js` (the ship in section:
17 crew and 440 amber dots counting down to 208), `street.js` (a London lane at night, Equiano with a hand lamp, Sharp, the
letter, the lit study window), `road.js` (a hill road, lamps taking their light one by one, dawn, 1807), `lantern.js` (the
ship's lantern close up; the flame goes out at 176.05 to 176.6 s); `cues.json`, `audio/mix.m4a`, `NOTES.md`.

## The shot list (start times in s)
0 sea dusk, the promise | 6.9 court | 9.9 claim document | 11.6 lantern night | 14.6 title | 17.5 the Zong, name board |
24.8 lantern dusk (care) | 28.3 ship section: 17 crew, 440 captives | 38.2 ledger | 42.4 Jamaica passing unseen, the captain's
glass | 50.9 moon sea | 54.2 casks low | 58.4 the rule | 70.5 deck, 29 November by absence (an empty deck, a swinging lantern)
| 84.2 rain fills the casks | 90.4 chain coil | 95.0 rings on the water | 98.2 hanging chain | 101.0 moon sea | 106.4 dawn ship
| 109.1 Black River | 111.7 440 to 208 | 115.6 the claim | 120.6 jury | 125.0 lawyer | 127.6 the quoted line as a document |
131.3 Equiano and Sharp, the letter | 143.0 Sharp writing | 146.6 King's Bench record | 155.4 candles out | 162.1 ledger, price
only | 167.1 lamps ignite up the road | 172.3 1807 | 174.0 the lantern at dawn goes out | 176.8 end card. Full list in `NOTES.md`.

## Exact steps to re-make it
1. Local check: `node harness/render.cjs films/dark-corners/zong --w 720 --h 1280 --audio films/dark-corners/zong/audio/mix.m4a --mp4`
   (add `--start/--end` for chunks, `--param kr=3` for a stronger Kuwahara, `--param prof=1` for set build timings).
2. Render: rc-render `films.yml` (`inputs[film]=films/dark-corners/zong`, 12 to 20 parts, full ref).
3. Check and deliver.

## Cost and time
Local 2 core box, software GL, 720x1280: Kuwahara radius 2 about 2.1 to 2.3 s a frame (radius 3 about 4.2 s; radius 1 2.0 s);
set builds 1.5 to 4 s each (street about 3.1 s), once per set per chunk; the Kuwahara pass is about half the frame time.
Whole film about 2.5 h single-threaded on that box, split into parts on the farm.

## Weak spots
- Equiano, Sharp and the climber are blocky silhouettes, readable but crude close up.
- The hull side wall is flat; the stern cabin reads as a box in close shots; palms on the Jamaica ridge are scraggly.
- The street ground meets the building bases in a straight line.
- The BLACK RIVER label overlaps the mast at 111.7 s; captions on pale paper rely on a dark scrim.
- `tools/check.mjs` does not exist in this repo and there are no tests for this film.

## To make a new one like it
Start from Kleidion's re-directed core rather than this film's (Kleidion has the real-time walker rule and the camera speed
audit); keep the restraint rules of `docs/manual/styles/dark-corners.md`.

## Sources of truth
`films/dark-corners/zong/NOTES.md`, its `*.js`, `film.json`, `cues.json`, `docs/LOG.md` (21 and 22 Oct).
