# Film recipe: What Lies Under a Meadow (`cutaway-line-meadow`)

The example film of the spec-driven Cutaway line (`films/lib/cutaway/`): 39.937 s, 16:9, built entirely from
`spec.json` + `cues.json` by the line engine, no film-specific Blender code. A golden meadow with a river, a village and
a mill; the camera goes under it, reading the cut face from the top down: a mole, a lost chest, a Roman jar, then deep
time (a counter rolls to 66,000,000 YEARS AGO) and the giant's skull; back on top for the end. No narration yet (cues
are estimated); the sound is CC0 nature recordings and a quiet score. Sam said "go" at 15:58 Toronto on 23 Oct; it
rendered on the Mac lane from the Samsung X5; encode, check and delivery were next (STATUS 23 Oct). Not in release
`kino-films` as of 23 Oct. Verdict: none yet. It is also the source of the twelve art-direction board frames
(`docs/manual/styles/cutaway-art.md`).

Note: it is cut-based (6 shots, 8 camera presets available); Sam's 17:32 verdict prefers one fixed view.

## Folder and every file
`films/cutaway/meadow/`:
| File | What |
| --- | --- |
| `script.json` | title and 5 narration lines (l00 hook, l01 title, l02 young layers, l03 deep time, l04 the smile) |
| `cues.json` | estimated by `films/lib/cutaway/tools/cues_estimate.py` (`estimated: true`, `title_line` l01, `outro_s` 4.2, 5 lines) |
| `spec.json` | format 16:9, look 20 spp fast, title and end cards, one set `meadow`, four scenes, six shots |
| `film.json` | id, `line: cutaway`, 24 fps, render 1280x720, delivery 1920x1080, 20 spp, `duration` 39.937, `audio/mix.m4a` |
| `blender.py` | identical copy of `films/lib/cutaway/blender.py` |
| `audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a` | the sound |

## The spec (exact, abridged only in the egg and animal lists' layout)
Set `meadow`: size standard (4 x 4 x 1.6 m), strata `time`, terrain rolling, water river, season summer, time golden,
trees 15, flowers 0.7, reeds 0.6, lilies 12, boulders 10, shafts 1.0, fog 0.0, seed 4, props village 5, mill, bridge,
lamps 3. Eggs: -Y mole (u -1.30), chest (-1.18), amphora (-0.42), ammonite (0.20), dino (-0.78), trilobite (-1.48), gold
(-0.33, span 3.0); +X hedgehog (-1.05), geode (-0.45, depth 1.40), well (0.62). Animals: deer, fawn, rabbit, fox, heron,
ducks 3, fish 5, butterflies 3, birds 4, petals 36.
Scenes and shots:
| Scene | Shot camera | Until | Why | Words |
| --- | --- | --- | --- | --- |
| Arrival | map | `l00>+0.4` | the whole meadow from above first | |
| Arrival | ground | `l02+0.2` | change of scale to the grass at the cut, into the low sun; the title lands | title "What Lies Under a Meadow", kicker CUTAWAY, `l01` to `l01>+2.6` |
| The young layers | crane `-Y`, u -0.7, to amphora | `l02>-0.6` | the reveal, each find on its word | MOLE TUNNEL (`l02.mole`), LOST CHEST (`l02.chest`), ROMAN JAR (`l02.roman`) |
| Deep time | crane `-Y`, u -0.7, from -0.45 to 1.25 | `l03.bones-0.2` | the layers below are millions of years old | counter 0 to 66000000 from `l03.years` to `l03.millions>`, caption YEARS AGO |
| Deep time | macro on dino | `l04.grass>` | the payoff on the skull | T. REX (`l03.giant`) |
| Back on top | hero | (to the end) | the consequence; end card | end card CUTAWAY / What Lies Under a Meadow |

Validator output (run 23 Oct by this writer): `OK`, one soft note (cues are an estimate), cost "959 frames, 60.7 s a
frame, 16.2 runner-hours, 20 parts of about 51.5 min, US$0", camera peaks well inside the limits (crane pan 0.186 at most).

## Exact steps that made it
1. `script.json`, then `python3 films/lib/cutaway/tools/cues_estimate.py films/cutaway/meadow`.
2. `cp films/lib/cutaway/blender.py films/cutaway/meadow/`; `film.json`; `spec.json`.
3. `python3 films/lib/cutaway/tools/validate.py films/cutaway/meadow` (OK); `python3 films/lib/cutaway/tools/selftest.py`.
4. Local stills: `python3 films/lib/cutaway/tools/stills.py films/cutaway/meadow --w 400 --samples 6`; 9:16 re-cut checked
   locally (8 stills; the map shot fits the turned block, the vertical ground shot aims further in).
5. Runner stills: rc-render `stills.yml` r1 (run 39880127743, 8 frames) and r2 (run 39884546069, 3 frames) at 1280x720,
   20 spp: every shot renders with its labels, counter, title and end card.
6. Sound (below), then the film on the Mac lane from the Samsung X5 (LOG 23 Oct): 10 jobs `5-meadow-c00` to `5-meadow-c09`,
   1280x720, 20 spp, METAL, about 6.5 s a frame, about 1 h 45 min. A job file (lane home
   `/Volumes/Samsung X5/KINOFORGE/render/mac-jobs/`, frames to `/Volumes/Samsung X5/KINOFORGE/frames/<film-id>`):
   ```json
   {"film": "films/cutaway/meadow", "out": "/Volumes/Samsung X5/KINOFORGE/frames/cutaway-line-meadow", "w": 1280, "h": 720, "samples": 20, "start": 0, "end": 96, "device": "METAL"}
   ```
   (the exact frame ranges per job are not recorded; 959 frames over 10 jobs is about 96 each; `end` is exclusive).
7. Next (not recorded as done): count 959 frames (`ls frames/[0-9]*.png`), encode with the four ffmpeg commands of
   `docs/manual/films/cutaway-series-reef-and-wreck.md` (`-frames:v 959`, scale 1920:1080, audio `audio/mix.m4a`), check,
   deliver to `Video Production/kino-films/` and archive on the X5; add to `kino-films` for the web studio (its id is in
   `CUTAWAY_FILMS`, `studio-web/lib/library.js`).
   Or render on runners: rc-render `films.yml` with `film=films/cutaway/meadow`, `parts=20` (validator: about 16
   runner-hours).

## The sound (`audio/make_audio.py`)
Uses the series kits (`films/cutaway/series/audio_kit.py`, `music_kit.py`) with `KF_SOUND_DUR=39.937`. Events from
`cues.json` and `spec.json`: ground 7.2, crane 12.9, mole 15.18, chest 17.62, jar 19.25, deep 22.4, years 23.96 to 25.5,
bones 27.5, top 29.0, end card about 35.8 s. Beds: evening birds, a small stream, wind, crickets (from the grass), all
muffled under the turf and near silent in deep time, full again on top; a bee across the low sun; under the turf a
`countryside` bed low-passed, the mole's paw strokes (`steps_mud`, 2.2 a second), a dirt trickle, a glint of gold
(`candle_sparkle_2`), earth settling round the Roman jar; deep time: `cave_1`, a slow low `whoosh_3` for the years, deep
stone settling, two drips by the giant (`drops_1`). Score: harp and strings in D, low and still in deep time, the flute
when we come back up. Measured: 39.937 s, -16.05 LUFS (m4a decoded -16.09), peak -2.0 dBFS, fade in 1.0 s, out 2.5 s, AAC
256k, all CC0. Rebuild: `python3 films/cutaway/meadow/audio/make_audio.py`.

## Cost
US$0. Runner frames (stills r1, r2): map about 55 s, crane 70 to 90 s, macro 30 to 40 s, hero about 50 s; Mac about 6.5 s.

## Sam's verdict
None yet.

## Weak spots (line SPEC)
Preset sets only; storybook animals and eggs of primitives; one egg of each kind, not placed by meaning; labels pinned to
slots; golden light is slow. Cues are estimates: when a narration is recorded, the word times move (the spec follows the
words) and the picture must be re-rendered.

## To make a new one like it
`docs/manual/styles/cutaway-line.md` "Exact steps (by hand)". For the house default, one scene and one near-still shot.

## Checks before showing Sam
959 frames; 39.9 s; labels on their words; counter reads 66,000,000; the check playbook.

## Known traps
Frame 768 is the skull macro, 830 the hero; board frames use 440 or 470 and 830.

## Sources of truth
`films/cutaway/meadow/*`, `films/lib/cutaway/SPEC.md`, `docs/PLAYBOOKS/cutaway-film.md`, `docs/LOG.md` and
`docs/STATUS.md` (23 Oct). The code wins if they disagree.
