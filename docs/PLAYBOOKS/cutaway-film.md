# Make a Cutaway film on the line (spec-driven, no Blender code)

The Cutaway line (`films/lib/cutaway/`) builds a whole Cutaway film from `spec.json` (data: presets for the world,
eggs by depth, animals, a camera preset per shot, words) and `cues.json` (the narration's times). Free: Blender 5.2
Cycles on CPU, GitHub runners of the public repos. Use it for any new Cutaway film the presets can say; hand-built films
on the kit (`make-a-cutaway-film.md`, Venice) stay for places the presets cannot say. Read first: `docs/SOUL.md`
(Cutaway), `films/director/CRAFT.md`, `films/lib/cutaway/SPEC.md`, and the example `films/cutaway/meadow/`.

## Two ways in

**A. Through the director (no session needed).** Sam picks Cutaway on the Styles page of the web studio (or tells the
director "a Cutaway film about ..."); the brief gets `line: "cutaway"` and `format` (16:9 or 9:16), 30 to 90 s. "Build
this film" commits `films/studio/<id>/brief.json`; `film.yml` runs: script, sound, then the coder seat writes
`cand/a.json` (and `b.json`) from SPEC.md and the example; the check stage runs the validator (seconds) and the repair
rounds; the eyes get a 480 px Blender contact sheet of each passing draft; the winner is `spec.json`; `films-render.yml`
renders it (48 frames a part, up to 20 parts) to release `films`. Watch `status.json` or the job page.

**B. By hand (a session).**
1. Folder `films/cutaway/<id>/` (one film per folder). Narration: `script.json` (`{"title", "lines": [{"text"}]}`, no
   dashes, no "...", facts checked), then the sound (kinoforge `sound.yml`, free voice and score, see
   `make-a-battle-map-film.md` step 3) for `cues.json` and `audio/mix.m4a`. To lay out the picture before the sound:
   `python3 films/lib/cutaway/tools/cues_estimate.py films/cutaway/<id>` (estimated times; specs refer to words, so they
   survive the real narration).
2. `film.json` (copy the example's: id, title, `style: cutaway`, `line: cutaway`, fps 24, render 1280x720 or 720x1280,
   delivery 1920x1080 or 1080x1920, `samples: 20`, `duration` = the audio length, `audio`), and
   `cp films/lib/cutaway/blender.py films/cutaway/<id>/` (unchanged).
3. Write `spec.json`: the set first, then the scene list (each scene a job, begin, middle, end), then shots with a camera
   preset, `until` on a cue word and a `why`, eggs where the narration names them, labels at the word.
4. `python3 films/lib/cutaway/tools/validate.py films/cutaway/<id>` until it says OK (hard errors must go; read every soft
   one). It prints the render cost.
5. Look cheaply: `python3 films/lib/cutaway/tools/stills.py films/cutaway/<id> --w 400 --samples 6` (about 2 minutes on the
   2-core chat box for 8 stills; `sheet.jpg` with the narration under each still). Then full-quality stills on runners:

   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/<id>' -f 'inputs[frames]=<at most 8 frames, one per shot>' -f 'inputs[per_job]=2' \
     -f 'inputs[tag]=<id>-r1' -f 'inputs[w]=1280' -f 'inputs[h]=720' -f 'inputs[samples]=20' -f "inputs[ref]=$(git rev-parse HEAD)"
   bash /home/claude/rc-render/tools/getstills.sh <id>-r1 out/      # one stills run in flight at a time
   ```
   Open every still.
6. `bash tools/verify.sh`, `python3 films/lib/cutaway/tools/selftest.py` if you touched `films/lib/cutaway/`, LOG, STATUS,
   commit your folder only, push.
7. Render: rc-render `films.yml` (`film=films/cutaway/<id>`, `parts` = frames / 48, at most 20) to `kino-films`; the web
   studio's Films page lists it in the Cutaway section by itself once `<id>.mp4` is there if its id is in
   `CUTAWAY_FILMS` (`studio-web/lib/library.js`; add it there). Or the Mac lane.
8. Check (`check-before-showing-sam.md`) and deliver with its weak spots.

## Cost (free; measured)
| What | Where | Time |
| --- | --- | --- |
| Validator | anywhere | under 1 s |
| Scene build (one set, golden, 10 eggs, 10 animals) | any | about 10 s |
| Stills at 400 px, 6 samples | 2-core chat box | 10 to 24 s each |
| One frame of the example, 1280x720, 20 samples, golden (runner stills r1, r2, 23 Oct) | free 4-core runner (stills.yml) | map about 55 s, crane 70 to 90 s, macro 30 to 40 s, hero and end card about 50 s; one job in r1 took 29 min for two frames that took 3 min in r2 (runner variance) |
| The example film (40 s, 959 frames) | validator estimate | about 16 runner-hours: 20 parts of about 50 minutes, US$0 |

The validator's model (`frame_seconds` in `tools/validate.py`) is calibrated on these; update it and this table when a
run measures something new. Levers: `fog: 0`, `samples` 16, `time: day`, a shorter film.

## Definition of done
- `validate.py` OK; selftest passes if the library changed; every shot seen as a full-quality still; one moving stretch
  seen before a full render.
- LOG and STATUS updated; pushed; render checked and delivered with its weak spots named.
