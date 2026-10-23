# The director pipeline (kinoforge `film.yml`, then `films-render.yml`)

An approved brief in, a finished film out, with no Claude session in the loop. Stages, each committing
`films/studio/<id>/status.json`: script (writer plus a fact checker from another provider) then gate 1 (facts), sound,
spec (one or two drafts), check (code checks and repairs), eyes (contact sheets scored) then gate 2, render
(`films-render.yml` to kinoforge release `films`), reflect (lessons). Paid by default inside a hard cap per film (decision
0013); free mode available. Lines: `battle-map` (16:9, 120 to 180 s), `kinetic` (9:16, 60 to 180 s), `cutaway` (16:9 or
9:16, 30 to 90 s; spec is data checked by the line validator, a Blender contact sheet for the eyes). The full end-to-end
view with who decides is `../system/autonomous-run.md`.

## Inputs
`films/studio/<id>/brief.json` (format in `films/director/README.md`): `id`, `title`, `line`, `subject`, `angle`,
`audience`, `tone`, `target_seconds`, `cap_usd` (0.50 to 5.00, default 2.00), `voice` (paid default
`elevenlabs/eleven-v4|brian`; free `chatterbox` or `kokoro|bm_george`), optional `notes`, `format` (cutaway), `music`
(`lyria`), `approved_at` (a new value restarts the job). Workflow inputs: `job` (the id), `from` (`resume` default, or
`script`, `sound`, `spec`, `render`, `reflect`).

## Exact steps
1. One job at a time: check `films/studio/*/status.json` for a job still `running`.
2. Write the brief (from Sam's subject, or `films/director/SLATE.md`), commit and push it: the push of a changed
   `films/studio/*/brief.json` starts `film.yml`. Or dispatch:
   ```bash
   gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/film.yml/dispatches -f ref=main \
     -f 'inputs[job]=<id>' -f 'inputs[from]=resume'
   ```
3. Watch `films/studio/<id>/status.json` (`git pull` every few minutes: `stage`, `state`, `message`, `usd`, `stages`)
   and the run: `gh api "repos/Eouchi147/kinoforge/actions/workflows/film.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion]'`.
4. On a stop, read `status.json` `message` and the log (release `logs`, `<id>-film.log`):
   - 402 (no credit) or cap reached: tell Sam; after credit, resume (`from=resume`; finished stages are skipped, nothing is paid twice).
   - free daily limit (free mode): wait for 00:00 UTC; resume.
   - gate failed: nothing was rendered; look at `check/final/` and the sheet; fix the brief or the line; `from=<stage>`.
   - code bug: fix the director, add a test in `films/director/tests/test_director.py`, `bash tools/verify.sh --full`.
5. Done (`stage` and `state` = `done`): release `films` has `<id>.mp4`, `<id>-preview.mp4`, `<id>-poster.jpg`,
   `<id>-sheet.jpg`. Read the new lessons in `films/director/LESSONS.md`; promote a rule for every film to `CRAFT.md` or a check.
6. Check (`../system/quality-checks.md`), deliver with the cost from `ledger.json` against the cap; LOG, STATUS, catalog.

Render by hand (a director film, or any folder into kinoforge `films`):
```bash
gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/films-render.yml/dispatches -f ref=main \
  -f 'inputs[film]=films/studio/<id>' -f 'inputs[parts]=0' -f 'inputs[ref]=main'
```
(`parts=0` is auto: about 200 frames a part, 48 for Blender films, 4 to 20 parts.)

## Cost (paid mode, 150 s Battle Map)
Usual US$0.90 to 1.50 (script 0.15 to 0.30, sound 0.10 to 0.15, spec 0.45 to 0.55, second draft 0.25 to 0.35 when it
fits, repairs 0.05 to 0.35, eyes 0.05 to 0.20, reflect under 0.01); worst case the cap. Render free. A 90 s film about 60 %.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| The web studio's "Build this film" (`web-studio-build.md`) | Sam starts it himself | as above |
| Free mode (`free_only: true` in `films/director/config.json` or `KF_FREE_ONLY=1`) | tests, scripts | US$0; picture spec weak |
| Hand-built film (Route B in `../system/autonomous-run.md`) | best craft today, new styles, Lantern Road, Clay | free |

## Checks before showing Sam
The pipeline's gates are not a substitute for `quality-checks.md`. Name the cost and the weak spots.

## Known traps
- As of 23 Oct no director film has finished: Salamis (free day) stopped at the picture spec; paid mode waits on credit;
  the Salamis resume (run 39877596998) stopped before any call because its old brief capped it at US$0.50 (raise it to
  2.00 with the ElevenLabs voice, `from=script`). The Great Emu War stopped at script (free limit). battle-of-tours was a
  cancelled paid test (US$0.36).
- The cutaway line is tested with mocks (`films/director/tests/test_cutaway_line.py`), not yet live.
- Free models: about 1,000 requests a day per key, few capable ones; keep one job at a time.
- Runner commits to `main` collide when jobs finish together: the workflow pulls, rebases and retries.
- Director tests use one job folder per run (`_selftest<pid>`), ignored by git.

## Sources of truth
`.github/workflows/film.yml` and `films-render.yml`, `films/director/README.md`, `films/director/config.json`,
`films/director/lines.json`, `docs/PLAYBOOKS/run-the-free-director.md`, `docs/PLAYBOOKS/cutaway-film.md`.
