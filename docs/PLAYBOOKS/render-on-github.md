# Render on GitHub (free runners)

Decision: `docs/decisions/0002`. Reference: `docs/WORKFLOWS.md`. All dispatches go through the REST API; `ref` is a
branch or a FULL commit hash (`git rev-parse HEAD`); a short hash fails the checkout. Push your film first.

## Which workflow
| Need | Workflow (repo) | Inputs | Output |
| --- | --- | --- | --- |
| A hand-built film or insert | `films.yml` (rc-render) | `film` (folder in kinoforge), `parts` (web 12 to 20, Blender 24), `ref` | release `kino-films`: `<id>.mp4`, `<id>-preview.mp4`, contact sheet |
| Full-quality check stills | `stills.yml` (rc-render) | `film`, `frames` (comma list, at most 20; keep it to 8), `tag`, `w`, `h`, `samples`, `ref`, `per_job` | release `stills`: `<tag>-f<frame>.jpg`; download with `bash tools/getstills.sh <tag> <dir>` in rc-render |
| New sound on a finished film | `remux.yml` (rc-render) | `film`, `ref` | replaces `<id>.mp4` and `<id>-preview.mp4` in `kino-films` |
| A render that must wait for others | `chain.yml` (rc-render, every 15 min) | add a `rule <marker> <film> <parts> <needed assets...>` line | dispatches `films.yml` once, writes `chain-<marker>.done` to `film-logs` |
| Narration and score | `sound.yml` (kinoforge) | `folder`, `voice`, `redo`, `audition` | commits `audio/`, `cues.json`, `film.json` |
| Director films | `film.yml` then `films-render.yml` (kinoforge) | `job` | release `films` |

## Steps
1. Push; take the full hash: `REF=$(git rev-parse HEAD)`.
2. Dispatch, e.g.
   `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/battles/<id>' -f 'inputs[parts]=16' -f "inputs[ref]=$REF"`
3. Find the run (the dispatch returns no id): `gh api "repos/Eouchi147/rc-render/actions/workflows/films.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion,.created_at]'`.
   Write the run id in `docs/LOG.md`.
4. Watch it: `gh api repos/Eouchi147/rc-render/actions/runs/<id>/jobs --jq '.jobs[] | [.name,.status,.conclusion]'`.
   A part that hangs (one did for 4.5 h on 22 Oct) or fails: cancel, then re-run only the failed jobs:
   `gh api -X POST repos/Eouchi147/rc-render/actions/runs/<id>/rerun-failed-jobs`. Failed part logs go to release `film-logs`.
5. When it is done, list the assets: `gh api repos/Eouchi147/rc-render/releases/tags/kino-films --jq '.assets[] | "\(.id) \(.name) \(.size)"'`.
6. Continue with `check-before-showing-sam.md`.

## Pitfalls
- The runner queue is shared by every builder: one stills run in flight per builder; do not dispatch the same film twice.
- A new workflow file is registered only after a push that touches it (404 before).
- Never loop renders automatically; a failed look is fixed in the scene, not by re-rendering.

## Definition of done
- The run concluded `success` (or every failed part was re-run to success); the asset is listed in the release with a
  plausible size; the run id is in `docs/LOG.md`.
