# Remux sound on a finished film (rc-render `remux.yml`)

Lays a film folder's current audio over its finished picture without re-rendering: takes `<id>.mp4` from rc-render
`kino-films`, maps the video stream unchanged (`-c:v copy`) with the folder's `film.json` `audio` file as AAC 256k,
`-shortest`, and republishes `<id>.mp4` and `<id>-preview.mp4` to `kino-films`. Free, a few minutes. Used on 22 Oct to
give all eight Battle Map v2 films their final score (Cannae run 39817058161, -14.2 LUFS). The depth on the sound side
(the score engine, re-mixing) is in `docs/manual/sound/remux.md`.

## Inputs
| Input | Meaning | Default |
| --- | --- | --- |
| `film` | film folder in kinoforge (its `film.json` `id` names the release asset) | required |
| `ref` | kinoforge branch or FULL commit hash holding the new audio | `main` |

## Exact steps
1. Make the new mix in the folder (`audio/mix.m4a`; re-score with `films/lib/score/`, or `sound.yml`). Encode to a temp
   file and verify it before replacing the old one.
2. Commit, push; `REF=$(git rev-parse HEAD)`.
3. Dispatch:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/remux.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/battles/<id>' -f "inputs[ref]=$REF"
   ```
4. Run id: `gh api "repos/Eouchi147/rc-render/actions/workflows/remux.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion]'`.
5. Check loudness and length on the new file (`../system/quality-checks.md`), log the run id and LUFS.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Re-render with `films.yml` | the picture changed too | free, slower |
| Local ffmpeg remux (same command) | a film outside `kino-films` (kinoforge `films`, a Mac-lane film) | free |

## Checks before showing Sam
New length equals the old (the picture is untouched; `-shortest` cuts to the shorter stream: an audio file shorter than
the picture shortens the film). Loudness on target.

## Known traps
- Only for films in `kino-films`; a director film lives in kinoforge `films` (remux it locally).
- The release preview is replaced too; the sheet and poster are not touched.
- Never re-render the picture for a sound change.
- Ain Jalut's remux was cancelled once and re-run (22 Oct): check the run concluded `success`.

## Sources of truth
rc-render `.github/workflows/remux.yml`, `docs/LESSONS.md` (Sound), `docs/LOG.md` (22 Oct).
