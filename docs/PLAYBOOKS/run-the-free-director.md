# Run the director (a film from a brief, no hand coding)

The director pipeline (`films/director/`, workflow `film.yml`) writes the script, checks the facts, makes the sound, writes
the picture spec, checks it in code and with a vision model, renders and learns. Default: capped paid mode, the best model per role with a hard cap per film (`cap_usd`, default US$2.00) and quality gates before each paid stage (`docs/decisions/0013`); free mode (`free_only: true`) stays available. Lines: `battle-map`
(16:9) and `kinetic` (9:16). Decision: `docs/decisions/0005`. Full reference: `films/director/README.md`.

## Steps
1. **One job at a time.** In free mode the free models allow about 1,000 requests a day per key (reset 00:00 UTC). Check
   `films/studio/*/status.json` for a job still running before you start another.
2. **Brief.** `films/studio/<id>/brief.json` (format in `films/director/README.md`): `id`, `title`, `line`, `subject`,
   `angle`, `audience`, `target_seconds`, `cap_usd` (0.50 to 5.00, default 2.00), `voice` (paid mode: `elevenlabs/eleven-v4|brian`; free mode: `chatterbox` or `kokoro|bm_george`), `approved_at` (the time Sam approved
   the subject; a new value restarts the job). Subjects come from Sam or `films/director/SLATE.md`.
3. **Start:** commit and push the brief (the push starts `film.yml`), or dispatch
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/film.yml/dispatches -f ref=main -f 'inputs[job]=<id>'`.
4. **Watch** `films/studio/<id>/status.json` (pull every few minutes) and the run
   (`gh api "repos/Eouchi147/kinoforge/actions/workflows/film.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion]'`).
5. **When a stage fails:** read `status.json` `message` and the log (release `logs`, `<id>-film.log`). No credit (HTTP 402) or the cap reached: tell Sam (he adds credit or raises the cap; never handle keys), then resume. A 429 or the free daily
   limit: wait for the reset and resume with `-f 'inputs[from]=resume'` (skips finished stages). A bad stage: `from=<stage>`
   (script, sound, spec, render, reflect). Fix code problems in the director, add a test in
   `films/director/tests/test_director.py`, run `bash tools/verify.sh --full`.
6. **When it is done:** the film is in release `films` (`<id>.mp4`, `-preview.mp4`, `-poster.jpg`, `-sheet.jpg`). Run
   `check-before-showing-sam.md`. `reflect.py` has appended lessons to `films/director/LESSONS.md`: read them; promote a
   lesson that applies to every film into CRAFT.md or a check.

## Definition of done
- `status.json` says `done`; the film passed `check-before-showing-sam.md`; LOG and STATUS updated with the run id and
  the cost from `ledger.json` against the cap; Sam has the link, with the weak spots named.
