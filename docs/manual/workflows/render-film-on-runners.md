# Render a film on free runners (rc-render `films.yml`)

Renders any kinoforge film folder (web `index.html` or Blender `blender.py`) in parallel parts on free GitHub runners,
joins the parts, lays finished inserts frame-exactly, lays the film's own audio, scales to the delivery size and
publishes `<id>.mp4`, `<id>-preview.mp4`, `<id>-sheet.jpg` and `<id>-poster.jpg` to rc-render release `kino-films`. The
same id replaces the old file. Costs nothing. Every hand-built film in the catalog with a `kino-films` video was made this way.

## Inputs
| Input | Meaning | Default |
| --- | --- | --- |
| `film` | film folder in kinoforge, e.g. `films/battles/cannae` | required |
| `parts` | parallel parts (each one runner) | `12` |
| `ref` | kinoforge branch or FULL 40-character commit hash the runners check out | `main` |
The folder needs `film.json` with `id`, `duration`, `fps` (24), `render_w`, `render_h`, `w`, `h` (delivery size),
`samples` (Blender, default 24), `audio` (path inside the folder, e.g. `audio/mix.m4a`, or empty for silent), optional
`inserts: [{film, first, last}]` (ids of finished films in `kino-films`, laid over frames `first` to `last`).
Kind is chosen by the folder: `blender.py` present means Blender (bpy 5.2.2, Python 3.13, CPU Cycles), else web
(Node 22, Playwright Chromium, `harness/render.cjs`).

## Exact steps
1. Push your film; take the full hash: `REF=$(git rev-parse HEAD)` (after `git push`).
2. Pick `parts`: web films 12 to 20 (10 to 25 min); Blender films 24 (about 80 min), or frames divided by about 48 for
   Cutaway films, at most 20 to 24. Total frames = ceil(duration x fps).
3. Dispatch:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/battles/<id>' -f 'inputs[parts]=16' -f "inputs[ref]=$REF"
   ```
   (`-f ref=main` is the rc-render branch that holds the workflow; `inputs[ref]` is the kinoforge commit.)
4. Find the run id (the dispatch returns none):
   `gh api "repos/Eouchi147/rc-render/actions/workflows/films.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion,.created_at]'`.
   Write it in `docs/LOG.md` or the film's `NOTES.md`.
5. Watch: `gh api repos/Eouchi147/rc-render/actions/runs/<run id>/jobs --jq '.jobs[] | [.name,.status,.conclusion]'`
   (jobs: `plan`, `part 0` to `part N-1`, `join`).
6. A part that fails or hangs (one hung 4.5 h on 22 Oct): cancel the run
   (`gh api -X POST repos/Eouchi147/rc-render/actions/runs/<id>/cancel`), then re-run only the failed jobs:
   `gh api -X POST repos/Eouchi147/rc-render/actions/runs/<id>/rerun-failed-jobs`. The failed part's log is in release
   `film-logs` as `<folder name>-part-<k>.log`.
7. Done: `gh api repos/Eouchi147/rc-render/releases/tags/kino-films --jq '.assets[] | select(.name|startswith("<id>")) | "\(.id) \(.name) \(.size)"'`.
8. Check (`../system/quality-checks.md`), then deliver (`../system/deliver-to-sam.md`); update the catalog row.

## What the join does (to reproduce it anywhere, e.g. on the Mac)
1. Each part: frames `a` to `b` encoded `libx264 -preset medium -crf 12 -pix_fmt yuv420p`.
2. Concatenate parts (`-f concat -c copy`) into `picture.mp4`.
3. Inserts: download `<insert>.mp4` from `kino-films`, scale to `render_w x render_h`, trim to `last-first+1` frames,
   shift by `first/fps`, overlay enabled by time `between(t,(first-0.5)/fps,(last+0.5)/fps)`.
4. Final: scale to `w x h` (lanczos), `libx264 -preset slow -crf 17 -maxrate 16M -bufsize 32M -pix_fmt yuv420p
   -movflags +faststart`, audio AAC 256k, `-shortest`.
5. Preview 960 wide (540 wide for 9:16), crf 24, AAC 128k. Sheet: `fps=1/6,scale=240:-2,tile=8x4`. Poster: the title
   line's start + 2 s (from `cues.json` `title_line`), else 30 % in.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| kinoforge `films-render.yml` (same recipe, release `films`, parts `0` = auto) | director films, or a film you want in kinoforge's release | free |
| The Mac lane (`render-on-the-mac.md`) | Blender films when Sam's Mac is connected; about 7 runners' worth | free |
| `chain.yml` rule (`follow-up-chains.md`) | the film needs inserts that are still rendering | free |

## Checks before showing Sam
Run concluded `success` (or every failed part re-run to success); the asset is listed with a plausible size; then the
full `quality-checks.md`.

## Known traps
- A short commit hash in `inputs[ref]` fails the checkout. Push before dispatching: runners check out GitHub, not your disk.
- `gh workflow run` (GraphQL) is blocked in Claude Code sessions; REST dispatch always works.
- Two overlays in a chain: enabling the second by frame number `n` never fires (Agincourt insert B, 22 Oct); the
  workflow now enables by time (rc-render 54c1bb4).
- Do not dispatch the same film twice; the queue is shared with every builder and with Sam's other projects.
- Never loop renders automatically: a bad look is fixed in the scene.
- Playwright 1.56 does not install on `ubuntu-latest`: the workflow pins `ubuntu-24.04`.

## Sources of truth
rc-render `.github/workflows/films.yml` (the code wins), `docs/PLAYBOOKS/render-on-github.md`, `docs/WORKFLOWS.md`
("Re-render a hand-built film"), `docs/decisions/0002-render-homes.md`.
