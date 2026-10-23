# Architecture: repos, releases, render homes, the web studio

KINOFORGE is two public GitHub repos, a set of GitHub releases that hold every finished file, three render homes (free
GitHub runners in two repos, and Sam's Mac with his external drive) and a web studio on Vercel. Nothing heavy runs in a
chat session: a session writes code and data, pushes, dispatches a workflow, and reads the result back from a release.
This page is the map; each workflow has its own page in `docs/manual/workflows/`.

## Inputs
- Read access to `Eouchi147/kinoforge` and `Eouchi147/rc-render` (both public; `gh` CLI with a token for dispatches).
- For the Mac lane only: Sam's Claude desktop connection (device file tools and computer use). Other agents cannot reach the Mac.

## The parts

### 1. `Eouchi147/kinoforge` (this repo): the studio's source and memory
| Path | What lives there |
| --- | --- |
| `AGENTS.md`, `CLAUDE.md` | Entry point and house law for every agent |
| `docs/` | System of record: `SOUL.md` (taste), `STATUS.md` (now), `LOG.md` (history), `MEMORY.md` (who writes what), `LESSONS.md`, `decisions/`, `PLAYBOOKS/`, `WORKFLOWS.md`, `research/`, and this manual (`docs/manual/`) |
| `films/<series>/<id>/` | One film per folder: `film.json` (id, title, sizes, fps, duration, audio, optional `inserts`), `cues.json` (narration times), `audio/mix.m4a`, and either `index.html` (web film, rendered in Chromium) or `blender.py` (Blender film), plus `NOTES.md` (the film's memory) |
| `films/lib/` | Engines: `battlemap/` (Battle Map, Three.js), `kinetic/` (Kinetic), `cutaway/` (the spec-driven Cutaway line), `score/` (free procedural music), `battle_mix.py` (narration on a beat grid) |
| `films/styles/cutaway/` | The Cutaway kit (`cutaway.py`), the cinematic extras (`cinematic/extras.py`), the 11 Blender art looks (`art/<look>.py`) |
| `films/cutaway/` | Cutaway productions (Venice, drainage ad, Agincourt inserts, seasons loop, showcase series, meadow) and the look boards (`looks/`) |
| `films/director/` | The director pipeline (script, sound, spec, check, eyes, render, reflect), `CRAFT.md`, `lines.json`, `config.json`, tests |
| `films/studio/<id>/` | Director jobs: `brief.json`, `status.json`, `ledger.json`, the outputs |
| `harness/` | Renderers: `render.cjs` (canvas or WebGL page to frames), `dom-render.cjs` (HTML ads), `blender_render.py` (Blender films, CPU or a GPU device), `mac/go.py` (the Mac lane), `shots/` (ad pipelines) |
| `ads/`, `social/`, `boards/`, `pieces/` | Business ads in code, phone-format social templates and batches, AI style boards, AI-footage pieces (lanes paused) |
| `proto/` | The 14 anthology style prototypes (origins of the house styles) and two pilots |
| `studio-web/` | The web studio (Next.js on Vercel); `public/data/catalog.json` is the catalog built by `tools/catalog.py` |
| `tools/` | `verify.sh` / `verify.py` (every gate), `verify-allow.txt` (exceptions), `catalog.py` |
| `.github/workflows/` | kinoforge workflows: `film.yml`, `films-render.yml`, `sound.yml`, `noor-sound.yml`, `codead.yml`, `social.yml`, `board.yml`, `piece.yml`, `verify.yml`, `verify-engine.yml`, and the legacy lanes |

### 2. `Eouchi147/rc-render`: the render farm
A second public repo shared with other projects of Sam. Only these lanes are KINOFORGE's (its `AGENTS.md` says so):
| Workflow | Job | Release it writes |
| --- | --- | --- |
| `films.yml` | Render any kinoforge film folder in parallel parts, join, lay the film's audio, lay `inserts`, scale, publish | `kino-films` (`<id>.mp4`, `<id>-preview.mp4`, `<id>-sheet.jpg`, `<id>-poster.jpg`); failed part logs to `film-logs` |
| `stills.yml` | Full-quality check frames of a film folder | `stills` (`<tag>-f<frame 5 digits>.jpg`) |
| `remux.yml` | New sound on a finished film, picture untouched | replaces `<id>.mp4` and `<id>-preview.mp4` in `kino-films` |
| `chain.yml` | Every 15 min: dispatch `films.yml` once a rule's needed assets exist | marker `chain-<name>.done` in `film-logs` |
| `sfx-bank.yml` | Build the BigSoundBank CC0 sound bank | `sfx-bank` (`sfx-bank.tar`, `sfx-bank.csv`) |
| `music-fetch.yml` | Fetch a public domain or CC0 recording from Wikimedia Commons with its licence record | `music` (`<name>.<ext>`, `<name>.licence.json`) |
Helper: `tools/getstills.sh <tag> <dir>` downloads stills by tag prefix through REST.
Every rc-render job checks out kinoforge at the `ref` you pass (a branch or a FULL 40-character commit hash).

### 3. Releases (where every finished file lives; all public)
| Repo | Release | Holds |
| --- | --- | --- |
| rc-render | `kino-films` | Hand-built films: 8 Battle Map v2, 4 Dark Corners, Venice, the seasons loop, the drainage ad (2 formats), the Agincourt inserts, the cinematic test, 4 showcase series films (catalog lists them) |
| rc-render | `stills` | Check stills (not for publishing) |
| rc-render | `film-logs` | Failed part logs, chain markers |
| rc-render | `sfx-bank`, `music` | Sound bank and music recordings with licences |
| kinoforge | `films` | Director films and NOOR samples (`films-render.yml`) |
| kinoforge | `ads` | Code ads (`codead.yml`) and prep logs |
| kinoforge | `social`, `boards`, `pieces` | Social batch videos (none rendered yet), AI style boards, AI-footage pieces |
| kinoforge | `gallery` | The anthology prototypes (`render.yml`) |
| kinoforge | `logs`, `voice`, `motion`, `showcase` | Director run logs, legacy lanes |
Download any asset by id (REST works where `gh release download` is blocked):
```bash
gh api repos/Eouchi147/<repo>/releases/tags/<release> --jq '.assets[] | "\(.id) \(.name) \(.size)"'
gh api -H "Accept: application/octet-stream" repos/Eouchi147/<repo>/releases/assets/<id> > <file>
```
Public link form: `https://github.com/Eouchi147/<repo>/releases/download/<release>/<asset>`.

### 4. Render homes (decision `docs/decisions/0002`)
| Home | Use it for | Speed (measured) | Reach |
| --- | --- | --- | --- |
| rc-render `films.yml` (free 4-core ubuntu-24.04 runners, CPU) | Hand-built films and inserts, web or Blender | Web films 12 to 20 parts in 10 to 25 min; Blender films 24 parts, about 80 min; Cutaway frame 30 to 90 s at 1280x720, 20 samples | Any agent with `gh` |
| kinoforge `films-render.yml` | Director films (called by `film.yml`), also by hand | Same runners; parts auto (about 200 frames a part, 48 for Blender) | Any agent |
| The Mac lane (Sam's MacBook Air M4, Blender 5.2 app, Metal GPU) | Blender films when the Mac is connected | Venice 1280x720 at 24 samples about 7.5 s a frame (about 7 runners); meadow about 6.5 s a frame; fanless, slows to about 13 s a frame after an hour | Only a session with Sam's desktop connection |
The Mac lane's home is Sam's external drive `Samsung X5` (1.9 TB): `KINOFORGE/render/` (code copy and `mac-jobs/`),
`KINOFORGE/frames/` (frames), `KINOFORGE/films/` (archive of every finished film). Fallback when the drive is unplugged:
the iCloud folder `Video Production/kinoforge-render/`. Start line in Blender's Python console:
`exec(open('/Volumes/Samsung X5/KINOFORGE/render/harness/mac/go.py').read())`. Details: `../workflows/render-on-the-mac.md`.

### 5. The web studio (Vercel project `kinoforge-studio`, `studio-web/`)
Next.js 15 app at https://kinoforge-studio.vercel.app (Vercel sign-in), redeployed on every push to `main`. Tabs today:
Director (chat that makes a brief; "Build this film"), Films (the library: `KINO_FILMS` and `CUTAWAY_FILMS` in
`studio-web/lib/library.js`, plus the live `films` release), Renders, Styles ("Start a film" on a live line), Setup.
API routes: `/api/director` (chat), `/api/build` (commits the brief), `/api/job` (job status), `/api/media` (streams
release assets with Range from an allow-list in `studio-web/lib/media.js`: rc-render `kino-films`, kinoforge `films` and
`gallery`), `/api/films`, `/api/status`, `/api/models`, `/api/decision`. Environment on Vercel (Sam sets them; agents
never see them): `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. The studio OS rework (23 Oct) reads
`studio-web/public/data/catalog.json`; its own page is `studio-os.md` in this folder once its builder writes it.

### 6. Accounts and keys (Sam owns all; agents never handle keys)
GitHub `Eouchi147` (both repos, Actions, releases). OpenRouter: the build key (GitHub secret `OPENROUTER_API_KEY`, used
by `film.yml`, `codead.yml`, `board.yml`, `piece.yml`, `social.yml` music) and the studio key (Vercel env, the director
chat). Vercel project `kinoforge-studio`. The Unmissed site repo `Eouchi147/sovereign-studio` (private) holds every
Unmissed claim in `site.config.js`. See `money-and-keys.md`.

## Exact steps (find your way in a new session)
1. `cd kinoforge && git pull --rebase --autostash origin main && bash tools/verify.sh`.
2. Read `docs/STATUS.md`, the top day of `docs/LOG.md`, `docs/SOUL.md`.
3. Find the thing: `python3 tools/catalog.py --stdout | python3 -c "import json,sys; [print(f['id'], f['status'], f['folder']) for f in json.load(sys.stdin)['films']]"`.
4. Open the film's recipe (`docs/manual/films/<id>.md`) or the style's (`docs/manual/styles/<id>.md`), then the workflow page.

## Alternatives
- Rendering in the chat container: only tiny checks (a few stills at 400 px). It has 2 cores and restarts.
- Paid cloud GPUs: not set up; not needed so far (US$0 render cost on runners and the Mac).

## Checks before showing Sam
See `quality-checks.md`. Every film reaches Sam only after the numbers, a contact sheet and three moving stretches.

## Known traps
- `gh workflow run` and `gh release download` use GraphQL, blocked in Claude Code sessions: use `gh api` (REST).
- A cross-repo `ref` must be a branch or a FULL commit hash; a short hash fails the checkout.
- A new workflow file is registered only after a push that touches it (404 before).
- The runner queue is shared by all builders and by Sam's other projects in rc-render.
- GitHub's terms for hosted runners make paid client production there a grey area (`docs/HANDOVER-2026-10-16.md`
  section g; `docs/CI-PURPOSE.md` sets a self-imposed limit of about 1,500 runner-minutes a month). Client jobs need
  another home before they start.
- `kino-films` also holds three files that are not films: a stray 900 MB `picture.mp4` (22 Oct; could not be deleted
  from a session) and `ins0.mp4`, `ins1.mp4` (the Agincourt join's insert copies). Ignore them.

## Sources of truth
`AGENTS.md`, `docs/decisions/0002-render-homes.md`, `docs/WORKFLOWS.md`, rc-render `.github/workflows/*.yml` and
`AGENTS.md`, `studio-web/lib/library.js`, `studio-web/lib/media.js`, `harness/mac/go.py`. The code wins where they disagree.
