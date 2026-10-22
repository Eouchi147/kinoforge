# The director pipeline: an approved brief in, a finished film out

Design: [`DESIGN.md`](DESIGN.md). Everything runs on GitHub runners (`.github/workflows/film.yml`) with OpenRouter models,
inside the job's cap. No Claude session in the loop. Nothing is published anywhere: the film lands in the release `films`
and waits for Sam.

## Start a job

The web studio commits `films/studio/<id>/brief.json`; that push starts `film.yml`. By hand:

1. Write `films/studio/<id>/brief.json` (format below; `<id>` is lowercase letters, digits and dashes).
2. `git add films/studio/<id>/brief.json && git commit -m "film <id>: brief" && git pull --rebase && git push`.
3. Watch `films/studio/<id>/status.json` (or the run: `gh api repos/Eouchi147/kinoforge/actions/runs?per_page=3`).

Re-run or resume: Actions, `film`, Run workflow, `job=<id>`, `from=resume` (default: skips every stage whose outputs
exist, so nothing is paid twice) or `from=script|sound|spec|render|reflect` (clears that stage and the later ones).
CLI: `gh workflow run film.yml -f job=<id> -f from=spec`. A push of the brief with a new `approved_at` starts fresh.

## Brief format (`films/studio/<id>/brief.json`)

| field | required | meaning |
| --- | --- | --- |
| `id` | yes | the folder name |
| `title` | yes | working title, e.g. "The Battle of Tours" |
| `line` | no (`battle-map`) | production line: `battle-map` (16:9, Terrain maps) or `kinetic` (9:16, type and documents) |
| `subject` | yes | what the film is about, e.g. "The Battle of Tours, 732: Charles Martel stops the Umayyad army" |
| `angle` | no | the angle agreed in the chat with the director |
| `notes` | no | anything else from the chat (must-have moments, things to avoid) |
| `audience` | no | e.g. "kids 8 to 14" |
| `tone` | no | overrides the line's house tone |
| `target_seconds` | no (150) | film length target, 45 to 240 |
| `cap_usd` | no (1.5) | hard money cap for the whole job, 0.30 to 5.00 |
| `voice` | no (`elevenlabs/eleven-v4\|brian`) | narrator, `model\|voice` as `harness/shots/factory.speech` takes it |
| `approved_at` | yes | ISO time Sam approved the brief (a new value restarts the job) |
| `seats` | no | advanced: `{writer, checker, spec: [seatA, seatB], repair, eyes}` seat names from `studio-web/lib/crew.json` |

```json
{"id": "battle-of-tours", "title": "The Battle of Tours", "line": "battle-map",
 "subject": "The Battle of Tours (Poitiers), 732: Charles Martel's Franks stop the Umayyad army of Abd al-Rahman",
 "angle": "the shield wall that stood all day", "audience": "kids 8 to 14", "target_seconds": 90, "cap_usd": 0.9,
 "voice": "elevenlabs/eleven-v4|brian", "approved_at": "2026-10-22T10:00:00Z"}
```

## Stages and files (all in `films/studio/<id>/`)

| stage | code | writes | usual cost |
| --- | --- | --- | --- |
| script | `script.py`: writer (head seat) drafts lines + picture ideas + claims; checker (deputy seat, a different provider) rates every claim; at most 2 rewrites; still-doubtful claims cut; code guards (dashes, "...", URLs, kid-safe words, counts) | `script.json`, `ad.json` | US$0.05 to 0.20 |
| sound | `sound.py`: `harness/shots/prep.py` (voice, Lyria score, Whisper word times) then the line's mix (`films/lib/battle_mix.py`) | `audio/`, `cues.json`, `film.json`, `index.html` | US$0.15 to 0.25 |
| spec | `spec.py`: two drafts in parallel from two providers (head + coder when cap >= 1.4, else the two best coder models) | `cand/a.js`, `cand/b.js` | US$0.05 to 0.50 |
| check | `check.cjs` on each draft; problems back to the coder seat as edits, at most 3 repair rounds; the best version of each draft is kept | `check/<a,b>/report.json`, `sheet.jpg` | US$0.01 to 0.05 per repair |
| eyes | `look.py`: eyes seat scores the contact sheets, picks the winner, lists fixes; one compose round, checked again (kept only if it still passes) | `spec.js`, `check/final/`, `spec_log.json` | about US$0.01 |
| render | `.github/workflows/films-render.yml` (reusable): parallel parts on ubuntu-24.04, join, sound, publish | release `films`: `<id>.mp4`, `<id>-preview.mp4`, `<id>-poster.jpg`, `<id>-sheet.jpg` | free |
| reflect | `reflect.py`: at most 3 one-line lessons appended to `LESSONS.md` (newest 40 kept; `spec.py` reads them) | `reflect.json`, `LESSONS.md` | under US$0.01 |

Every call is in `ledger.json` (seat, model, task, cost, seconds) and refused when it could pass `cap_usd`. An HTTP 402
from OpenRouter (key out of credit) stops the job with that message. The run log is uploaded to the release `logs` as
`<id>-film.log`.

## `status.json` (the contract with the web studio)

```json
{"id": "battle-of-tours", "title": "...", "line": "battle-map",
 "stage": "script|sound|spec|check|eyes|render|reflect|done", "state": "queued|running|done|failed",
 "message": "one plain sentence for Sam", "usd": 0.42, "cap_usd": 0.9,
 "outputs": {"script": "films/studio/<id>/script.json", "audio": "...", "duration": 91.2, "spec": "...", "check_sheet": "...",
             "video": "https://github.com/Eouchi147/kinoforge/releases/download/films/<id>.mp4", "preview": "...", "poster": "...", "sheet": "...", "log": "..."},
 "stages": {"script": {"state": "done", "started_at": "...", "ended_at": "...", "usd": 0.08}},
 "approved_at": "...", "run_url": "https://github.com/.../actions/runs/...", "updated_at": "2026-10-22T10:12:00Z"}
```

Committed by the runner after every stage (pull, rebase, push, retried). Finished: `stage` = `done`, `state` = `done`.
Failed: `state` = `failed`, `message` says why, `outputs.log` links the run log.

## Production lines (`lines.json`)

A line is config: engine folder, `SPEC.md`, example films (their `spec.js` and `cues.json` are shown to the coder),
aspect, render and delivery sizes, title line, house tone and structure, picture and spec rules, music and voice
direction, an optional lint module run in the page by `check.cjs`. A line is available when its `SPEC.md` exists.
`battle-map`: examples Cannae and Hastings, lint `lint/battle-map.js`. `kinetic`: example `films/studio/kinetic-demo`
(look reference `films/dark-corners/bamberg`); the engine reports its own spec errors through `window.KF_ERROR`.
A new line = a new entry in `lines.json` (and a lint module if the engine does not check its spec itself).

## Tests (no paid calls)

`python3 films/director/tests/test_director.py` runs the stages with recorded model replies: house rules, script
rounds and cuts (checker from another provider), resume and fresh starts, lessons, and the whole spec stage in Chromium
on the Hastings cues (a broken draft is repaired, the eyes pick the winner, the compose round is re-checked).
`node films/director/check.cjs films/battles/hastings --line battle-map` checks any finished film.
