# Sound: `remux.yml` (new sound on a finished film, picture untouched)

rc-render workflow `remux.yml` replaces a finished film's soundtrack without re-rendering a single frame: it downloads
`<id>.mp4` from the rc-render release `kino-films`, lays the film folder's current audio (`film.json` `audio`, at a kinoforge
ref you give), and republishes `<id>.mp4` and `<id>-preview.mp4`. It is how every Battle Map v2 film got its final free
score after its picture had rendered (the v2 pictures do not snap to music), and it is the rule for any later re-score or
re-mix: never re-render the picture for a sound change (`docs/LESSONS.md`).

## Inputs
- A film already in `kino-films` as `<id>.mp4` (the `id` in `film.json`).
- The new mix committed and pushed in kinoforge at the film folder's `film.json` `audio` path (usually `audio/mix.m4a`).

## Exact steps
1. Make and commit the new mix (for example `python3 films/lib/score/remix.py films/battles/<id>` then
   `python3 films/lib/score/cues_from_score.py films/battles/<id>`), push, take the full hash: `REF=$(git rev-parse HEAD)`.
2. Dispatch:
   `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/remux.yml/dispatches -f ref=main -f 'inputs[film]=films/battles/<id>' -f "inputs[ref]=$REF"`
3. What the job does (ubuntu-24.04, 30 min timeout): sparse checkout of the film folder at `ref`; checks the audio file
   exists and prints its duration; `gh release download kino-films -p "<id>.mp4"`;
   `ffmpeg -i old.mp4 -i <audio> -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart <id>.mp4`;
   a preview at 960 wide for 1920 wide films (else 540), crf 24, AAC 128k; uploads both with `--clobber`.
4. Find the run: `gh api "repos/Eouchi147/rc-render/actions/workflows/remux.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion]'`;
   write the run id in `docs/LOG.md`.
5. Check the new file: loudness (about -14 LUFS), length equal to `film.json`, and listen to the opening, the turn and the end.

## Recorded runs
Cannae v2: render run 39798701933, remux run 39817058161 (-14.2 LUFS, 157.6 s). The other battles' remux run ids are not
recorded in the LOG (Hastings, Hattin and Gaugamela remuxed on 22 Oct; Ain Jalut's remux was cancelled once and re-run;
Waterloo, Thermopylae, Agincourt followed). The kino-films file keeps its name; Sam's Mac copies carry `-v2`.

## Alternatives
| Route | When |
| --- | --- |
| Re-render with rc-render `films.yml` | only when the picture changed |
| kinoforge `films-render.yml` | director films and NOOR live in kinoforge release `films`; `remux.yml` reads only `kino-films`, so a sound change there needs a re-render or a manual remux (not built) |

## Known traps
- `-shortest`: if the new mix is shorter than the picture, the film is cut to the mix; keep `film.json` `duration` and the
  mix length equal.
- The `ref` must be a branch or a FULL commit hash; a short hash fails the checkout.
- Only `<id>.mp4` and the preview are replaced; the contact sheet and poster stay as they were (picture unchanged).

## Sources of truth
rc-render `.github/workflows/remux.yml`, `docs/WORKFLOWS.md`, `docs/PLAYBOOKS/render-on-github.md`, `docs/LOG.md` (22 Oct).
