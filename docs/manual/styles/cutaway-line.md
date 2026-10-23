# Cutaway: the spec-driven line (`films/lib/cutaway/`, films from data, no Blender code)

The Cutaway line makes a whole Cutaway film from two data files: `spec.json` (presets for the world, eggs by depth,
animals, a camera preset per shot, words) and `cues.json` (the narration's line and word times). The engine builds it
with the kit (`cutaway.md`) and the cinematic extras (`cutaway-cinematic.md`); a validator judges a spec in under a
second without Blender; a stills tool makes a contact sheet. The director (web studio) has a `cutaway` line that writes
the spec with a model. Built on 23 Oct after Sam (22 Oct 20:24) said "I love the cutaway style, I need it in the
kinoforge studio". Example film: `films/cutaway/meadow/` (`docs/manual/films/cutaway-line-meadow.md`).

Important since 23 Oct 17:32: Sam did not like camera moves and cuts in the cinematic test and chose the seasons loop
grammar (one fixed view, no cuts, a living world) as the base. The line's presets are cut-based (eight camera presets,
several shots). For a film in the house default, write ONE scene with ONE shot whose camera barely moves (`orbit` with a
small `deg`, or `hero`), or build on the seasons loop itself (`cutaway-seasons-loop.md`). Ask Sam before making a cut-based
film on the line.

## Inputs
- `script.json` (`{"title", "lines": [{"text"}]}`: no dashes, no "...", facts checked) or real narration.
- `cues.json`: from the sound stage (kinoforge `sound.yml`) or estimated by `tools/cues_estimate.py`.
- `film.json` and the line's generic `blender.py` (copied unchanged from `films/lib/cutaway/blender.py`).

## Files
| File | What it is |
| --- | --- |
| `films/lib/cutaway/SPEC.md` | The spec format (time references, sets, eggs, animals, cameras, words, cost, weak spots) |
| `films/lib/cutaway/presets.py` | The menu as data: `SIZES` (small 3x3x1.3, standard 4x4x1.6, deep 4x4x2.1), `TERRAIN`, `STRATA_TIME` and kit strata, `WATER` (river, stream, pond, lagoon, none), `TIMES` (day, golden, dusk, overcast, studio) with `TIME_COST`, `PROPS`, `EGGS` (default depths), `ANIMALS`, `CAMERAS`, label `SLOTS`, `RENDER` sizes |
| `films/lib/cutaway/layout.py` | A set spec resolved into numbers (deterministic from the seed) |
| `films/lib/cutaway/plan.py` | `spec.json` + `cues.json` to sets, a shot timeline and overlays; collects every error and warning at once |
| `films/lib/cutaway/timeref.py` | Time references: `12.5`, `"l08"`, `"l08>"`, `"l08.mole"`, `"l08.mole>"`, `"l08.step#1"`, `"l05.chest+0.4"`, `"start"`, `"end"`, `"outro"`, marks |
| `films/lib/cutaway/camera.py` | The eight camera presets as pure numpy (ease in, steady, ease out); `speed()` measures screen speed |
| `films/lib/cutaway/overlay.py` | Labels with hairline leaders, counters, captions, title and end cards, set in code (Instrument Sans) |
| `films/lib/cutaway/engine.py` | `Film`: builds only the sets the frame range needs; applies `look.art` or `$KF_ART` (`cutaway-art.md`) |
| `films/lib/cutaway/blender.py` | The generic scene (copy unchanged); `$KF_SPEC` picks another spec file (`KF_SPEC=cand/a.json`) |
| `films/lib/cutaway/tools/validate.py` | The validator (schema, presets, time references, CRAFT checks, camera speed, eggs, labels, cost) |
| `films/lib/cutaway/tools/stills.py` | Check stills and a contact sheet with the narration under each still |
| `films/lib/cutaway/tools/cues_estimate.py` | Estimated `cues.json` from `script.json` (`--wps 2.7 --title-line l01 --hold 3.2 --outro 4.2`) |
| `films/lib/cutaway/tools/selftest.py` | The example passes; 13 broken specs fail with the right message (about 15 s, no Blender) |
| `films/director/lines.json` (`cutaway`) | The director's line: 16:9 or 9:16, 30 to 90 s, 24 fps, 20 samples, tone, structure, picture and spec rules |

## The spec in one screen (full reference: `films/lib/cutaway/SPEC.md`)
```json
{
 "format": "16:9",
 "look": {"samples": 20, "quality": "fast", "exposure": 0.1, "art": "fable"},
 "title": {"text": "What Lies Under a Meadow", "kicker": "CUTAWAY", "at": "l01", "until": "l01>+2.6"},
 "end": {"text": "CUTAWAY", "sub": "What Lies Under a Meadow"},
 "marks": {},
 "sets": {"meadow": {"size": "standard", "strata": "time", "terrain": "rolling", "water": "river", "season": "summer",
   "time": "golden", "trees": 15, "fog": 0.0, "seed": 4, "props": {"village": 5, "mill": true},
   "eggs": [{"kind": "dino", "face": "-Y", "u": -0.78}], "animals": [{"kind": "deer"}]}},
 "scenes": [{"name": "The young layers", "set": "meadow", "job": "What is just under the turf?", "begin": "the treetops", "middle": "the finds appear", "end": "the Roman layer",
   "shots": [{"camera": "crane", "face": "-Y", "u": -0.7, "to": "dino", "until": "l02>-0.6", "why": "the reveal",
     "labels": [{"text": "T. REX", "at": "l02.giant", "until": "l02>", "point": "dino", "slot": "upper-left"}]}]}]
}
```
Leave `art` out for the plain look.

Rules the validator enforces: every shot has a `why`; shots run in order with no gaps and end on `until` (the last has
none); a word reference that is not in the line is an error naming the line's words; eggs: one of each kind per set (two
geodes), at most 12 per set, inside the block, not overlapping, recent above old above deep; labels in capitals, about
4 words, no dashes, no "...", at most two at once, never two in one slot, upper slots in `ground` shots, nothing in the
title card's place; camera speed: pan or crane at most 0.25 frames per second, push at most 10 % of the frame per second
(twice that is an error); a crane over the whole block needs about 6 s or more.

## Exact steps (by hand)
1. `mkdir films/cutaway/<id>`; write `script.json`.
2. Sound first if narrated: an `ad.json` prep block, push, then
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main -f 'inputs[folder]=films/cutaway/<id>' -f 'inputs[voice]=kokoro|bm_george'`
   (it commits `audio/`, `cues.json`, `film.json`; pull). No narration yet:
   `python3 films/lib/cutaway/tools/cues_estimate.py films/cutaway/<id>`. Nature-sound films: write
   `audio/make_audio.py` on the series kits (`docs/manual/films/cutaway-line-meadow.md`, sound section).
3. `film.json` (copy `films/cutaway/meadow/film.json`: `id`, `title`, `style: cutaway`, `line: cutaway`, fps 24, render
   1280x720 or 720x1280, delivery 1920x1080 or 1080x1920, `samples: 20`, `duration` = the audio length, `audio`) and
   `cp films/lib/cutaway/blender.py films/cutaway/<id>/`.
4. Write `spec.json`: the set first, then the scene list (job, begin, middle, end), then shots (camera preset, `until`
   on a cue word, `why`), eggs where the narration names them, labels on the word.
5. `python3 films/lib/cutaway/tools/validate.py films/cutaway/<id>` until it prints `OK` (no hard errors; read every soft
   one). Expected output on the example:
   ```
   OK
     soft cues.json is an estimate (no narration yet): word times will move when the narration is recorded
     cost: 959 frames, 60.7 s a frame, 16.2 runner-hours, 20 parts of about 51.5 min, US$0
     camera peaks: 0:map pan 0.005 push 0.008, 1:ground pan 0.0 push 0.01, 2:crane pan 0.039 push 0.017, 3:crane pan 0.186 push 0.023, 4:macro pan 0.002 push 0.026, 5:hero pan 0.006 push 0.0
   ```
6. Look cheaply: `python3 films/lib/cutaway/tools/stills.py films/cutaway/<id> --w 400 --samples 6` (about 2 min for 8
   stills on the 2-core box; writes `stills/t<centiseconds>.jpg`, `sheet.jpg`, `stills.json`). Then runner stills:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/<id>' -f 'inputs[frames]=<at most 8, one per shot>' -f 'inputs[per_job]=2' \
     -f 'inputs[tag]=<id>-r1' -f 'inputs[w]=1280' -f 'inputs[h]=720' -f 'inputs[samples]=20' -f "inputs[ref]=$(git rev-parse HEAD)"
   bash /home/claude/rc-render/tools/getstills.sh <id>-r1 out/
   ```
7. `bash tools/verify.sh`; `python3 films/lib/cutaway/tools/selftest.py` if you touched `films/lib/cutaway/`; LOG,
   STATUS; commit your folder only; push.
8. Render: rc-render `films.yml` (`film=films/cutaway/<id>`, `parts` = frames / 48, at most 20) to `kino-films`; add the
   id to `CUTAWAY_FILMS` in `studio-web/lib/library.js` so the web studio lists it. Or the Mac lane (the example ran there
   as 10 jobs `5-meadow-c00` to `c09`, about 6.5 s a frame).

## Through the director (no session)
Sam picks Cutaway on the Styles page (or tells the director "a Cutaway film about" a subject); the brief gets `line: "cutaway"`
and `format`; `film.yml` runs script, sound, the coder seat writes `cand/a.json` and `b.json`, the validator checks them,
the eyes get a 480 px Blender contact sheet, the winner becomes `spec.json`, `films-render.yml` renders 48 frames a part
(4 to 20 parts) to release `films`. Tested with mocks (`films/director/tests/test_cutaway_line.py`); not yet run live on
GitHub (STATUS 23 Oct). Paid seats follow `docs/decisions/0013` (cap per film).

## Cost (free, measured)
| What | Where | Time |
| --- | --- | --- |
| Validator | anywhere | under 1 s |
| Scene build (one set, golden, 10 eggs, 10 animals) | any | about 10 s |
| Stills 400 px, 6 spp | 2-core chat box | 10 to 24 s each |
| One frame 1280x720, 20 spp, golden | free 4-core runner | map about 55 s, crane 70 to 90 s, macro 30 to 40 s, hero about 50 s (rc-render stills runs 39880127743, 39884546069) |
| One frame, same | Sam's Mac (M4, METAL) | about 6.5 s |
| The 40 s example | validator estimate | about 16 runner-hours, 20 parts of about 50 min |

`TIME_COST` per light: studio 0.75, day 1.0, overcast 1.0, golden 1.5, dusk 1.45. `fog` costs about 2.5 times a wide
shot. Levers in order: `fog: 0`, `samples` 16, `time: "day"`, fewer lit houses at dusk, a shorter film.

## Alternatives
- Hand-built on the kit (Venice, the series) for places the presets cannot say (a city, a mine, a volcano).
- The seasons loop grammar for one fixed view and no cuts (Sam's base).
- The flat-vector web version for speed (`cutaway-flat-vector.md`).

## Checks before showing Sam
Validator OK; selftest passes if the library changed; every shot seen as a full-quality still; one moving stretch seen
before a full render; then `docs/PLAYBOOKS/check-before-showing-sam.md`.

## Known traps
- Specs refer to words, so they survive re-timed narration; a word missing from a line is a hard error (good).
- Labels are pinned to slots; the validator checks slots, not the picture behind them (the eyes stage does).
- Sets are presets: a castle, a city or a mine still needs a hand-built film. New presets go in `presets.py`,
  `layout.py` and `SPEC.md` together.
- One runner stills job once took 29 min for two frames that took 3 min in the next run (runner variance).

## Sources of truth
`films/lib/cutaway/SPEC.md`, `presets.py`, `engine.py`, `plan.py`, `camera.py`, `tools/*.py`,
`docs/PLAYBOOKS/cutaway-film.md`, `docs/WORKFLOWS.md` (director lines), `films/director/lines.json`, `docs/STATUS.md`.
The code wins if they disagree.
