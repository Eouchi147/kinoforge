# Check stills (rc-render `stills.yml`)

Renders single full-quality frames of any kinoforge film folder on free runners and uploads them to rc-render release
`stills` as `<tag>-f<frame, 5 digits>.jpg`. Use it to look at the real picture (full size, full samples) before paying
runner hours for a whole film. Costs nothing. Every Cutaway, Venice, drainage and Agincourt round was checked this way
(tags such as `venice-r6`, `drain169-r4`, `agin-r9B`, `cutaway-line-r2`).

## Inputs
| Input | Meaning | Default |
| --- | --- | --- |
| `film` | film folder in kinoforge | required |
| `frames` | comma list of frame numbers (at most 20 are used; keep it to 8) | required |
| `per_job` | frames rendered by one runner (saves setup time) | `4` |
| `tag` | name prefix for the files, e.g. `<id>-r1` | required |
| `w`, `h` | size | `1280`, `720` |
| `samples` | Blender samples (blank = the film default) | blank |
| `ref` | kinoforge branch or FULL commit hash | `main` |

## Exact steps
1. Push; `REF=$(git rev-parse HEAD)`.
2. Pick one frame per shot (at most 8): frame = seconds x fps.
3. Dispatch:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/<id>' -f 'inputs[frames]=120,480,900' -f 'inputs[per_job]=2' \
     -f 'inputs[tag]=<id>-r1' -f 'inputs[w]=1280' -f 'inputs[h]=720' -f 'inputs[samples]=20' -f "inputs[ref]=$REF"
   ```
4. Watch: `gh api "repos/Eouchi147/rc-render/actions/workflows/stills.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion]'`.
5. Download (in a clone of rc-render): `bash tools/getstills.sh <id>-r1 out/` (REST; prints each file). Without the clone:
   `gh api repos/Eouchi147/rc-render/releases/tags/stills --jq '.assets[] | select(.name|startswith("<id>-r1-")) | "\(.id) \(.name)"'`
   then `gh api -H 'Accept: application/octet-stream' repos/Eouchi147/rc-render/releases/assets/<id> > file.jpg`.
6. Open every still. Write the round, what changed and the measured time per frame in the film's `NOTES.md`.
7. Next round: a new tag (`-r2`), never reuse one (files are clobbered).

## Measured cost (runner, 1280x720, 20 samples, Cutaway)
Map about 55 s a frame, crane 70 to 90 s, macro 30 to 40 s, hero and end card about 50 s, plus 2 to 5 min setup per
job. Runner variance is large: one r1 job took 29 min for two frames that took 3 min in r2. Art looks: 2 to 15 min a
still; the reference board frames took over 30 min on runners and about 15 s each on the Mac lane (23 Oct).

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Local small stills in the chat box: `python3 films/lib/cutaway/tools/stills.py films/cutaway/<id> --w 400 --samples 6` (Cutaway line, `sheet.jpg` with narration under each), `python3 harness/blender_render.py <folder> --w 640 --h 360 --samples 16 --start N --end N+1` (any Blender film), `node films/lib/battlemap/tools/stills.cjs films/battles/<id> --t <times> --out out/<id>` (Battle Map) | first look, layout | free, 2 cores, keep it small |
| Mac lane check job (name it `0-<name>.json` so it jumps the queue) | Sam's Mac connected | free, about 7 times a runner |

## Checks before showing Sam
Stills are for you, not for Sam, unless he asked for a board. A board for Sam goes on a page with the stills side by side.

## Known traps
- One stills run in flight per builder, at most 8 frames: the queue is shared with film renders (22 Oct: about 30 stills
  runs queued behind films).
- The tag prefix match in `getstills.sh` is `<tag>-`: a tag that is a prefix of another (`r1` and `r1A`) mixes files.
- Failed jobs leave a log in `film-logs` named `<tag>-f<frames>.log`.

## Sources of truth
rc-render `.github/workflows/stills.yml`, rc-render `tools/getstills.sh`, `docs/PLAYBOOKS/cutaway-film.md` (cost
table), `docs/LOG.md` (22 to 23 Oct).
