# Film: NOOR, Iqra (short) (`noor-descent-05-iqra-short`)

A 36.4 s, 9:16 short cut from the Iqra film for phones: the word Iqra written in gold light, the five first verses (96:1-5)
on the illuminated panel, and their meaning over the mountain at night, ending with the series tag. No new narration and
nothing paid: the sound is three pieces of the Iqra film's own mix joined with short fades; the same sets are reframed for
9:16. Same NOOR rules (no person shown; Arabic set in code). Built and rendered on 22 Oct, delivered 23 Oct (UTC), waiting on
Sam's verdict. Styles: `docs/manual/styles/noor.md`; parent film: `noor-descent-05-iqra.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/noor/s05-iqra-short/` |
| Length, frames | 36.438 s, 875 frames at 24 fps |
| Picture | Lantern Road; rendered 720x1280, delivered 1080x1920; short lenses (18 to 26 mm) because the sets were painted for 16:9 (at 20 mm one design px is one screen px) |
| Sound | excerpts of `films/noor/n05-iqra/audio/mix.m4a` joined by `make_short.py` |
| Render | kinoforge `films-render.yml` (run id not recorded) |
| Release | kinoforge `films`: `noor-descent-05-iqra-short.mp4`, `-preview.mp4`, `-sheet.jpg`, `-poster.jpg` |
| Cost | US$0 |
| Sam's verdict | waiting |

## Files that make it
`make_short.py`, `cues.json` and `film.json` (written by it), `audio/mix.m4a` (written by it), `index.html`, `scene.js`, `kf.js`,
`shots.js` (three shots), `type.js`; the sets are read from the Iqra film.

## How the sound is cut (`make_short.py`)
Three segments of the Iqra mix, each from 0.3 to 0.35 s before its first line to 0.7 to 1.6 s after its last: `word` (line
`e3`), `verses` (`e7` to `v5`), `meaning` (`m1` to `m2`); a 1.0 s silent lead-in so the hook title lands first; each piece
faded in and out over 0.3 s (`atrim`, `afade`), joined with `concat`, padded 0.4 s at the end. `cues.json` keeps those lines
with times shifted to the short's timeline, plus `segments`, the `arabic` table and `marks.hook` (0 to 3.4 s).

## Shot list
1. `w` sky: the hook, the sky fills with gold light, the word writes itself (Iqra), READ on the spoken "Read".
2. `v` sky: the illuminated panel verse by verse (a 0.5 s dissolve hides the join in the sound).
3. `m` mountain at night: the word stays with us, then the series tag (dissolve 0.5 s).
Captions are built from the word timings in chunks of up to about 8 words, skipping the verse lines (the panel carries them).

## Exact steps to re-make it
1. `python3 films/noor/s05-iqra-short/make_short.py` (needs the Iqra mix; writes `cues.json`, `film.json`, `audio/mix.m4a`).
2. Stills: `node films/noor/n05-iqra/tools/stills.cjs films/noor/s05-iqra-short --shots --w 720 --h 1280 --out out/short`.
3. Render: kinoforge `films-render.yml` with `inputs[film]=films/noor/s05-iqra-short`; check the 9:16 safe zone; deliver.

## Weak spots
Not recorded separately (the parent film's weak spots apply: sets painted for 16:9, the valley simple, warmth from sky tint).

## Sources of truth
`films/noor/s05-iqra-short/make_short.py`, `shots.js`, `film.json`, `cues.json`, `docs/LOG.md` (22 Oct).
