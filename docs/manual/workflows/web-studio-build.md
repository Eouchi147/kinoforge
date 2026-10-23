# The web studio's build button

The web studio (https://kinoforge-studio.vercel.app, Vercel project `kinoforge-studio`, code in `studio-web/`) is where
Sam starts a film himself. In the Director tab he talks to the director chat until the brief is complete, picks a money
cap, and taps "Build this film". The button calls `POST /api/build`, which commits `films/studio/<id>/brief.json` to
`main`; that push starts `film.yml` (`director-pipeline.md`). The job page (`#job/<id>`) then polls `status.json` every
6 s and shows the stages and the spend. The Styles tab's "Start a film" opens the director on a live line (Cutaway in
16:9 or 9:16, Battle Map, Kinetic). The studio OS rework of 23 Oct may move these controls: its page is
`../system/studio-os.md` once written; `studio-web/` is the truth.

## Inputs
The brief fields the route requires: `title`, `line` (`battle-map`, `kinetic` or `cutaway`), `subject`, `angle`,
`audience`, `tone`; optional `target_seconds` (clamped to the line's range: battle-map 120 to 180, kinetic 60 to 180,
cutaway 30 to 90), `cap_usd` (0.50 to 5.00, default 2), `format` (cutaway: `16:9` or `9:16`), `music` (`lyria`),
`voice` (`model|voice`), `notes`. Environment on Vercel: `GITHUB_TOKEN` (commits the brief), `OPENROUTER_API_KEY` (the chat).

## Exact steps (what the route does, so an agent can do the same by hand)
1. Refuse if a required field is missing (400 "The brief still needs:" and the missing fields) or the line is unknown.
2. Refuse with 409 `no-github` if `GITHUB_TOKEN` is not set ("GitHub is not connected yet").
3. Refuse if the line's `SPEC.md` is not on `main` (`films/lib/battlemap/SPEC.md`, `films/lib/kinetic/SPEC.md`,
   `films/lib/cutaway/SPEC.md`).
4. Make the id from the title (lowercase, dashes, 40 characters; `-2`, `-3` if taken).
5. Replace dashes and three dots in every text field, set `approved_at` to now, write
   `films/studio/<id>/brief.json` with the commit message `studio: brief for <id> (<line>)`.
6. By hand, the same: write the JSON (`films/director/README.md` format), commit, push. Or dispatch `film.yml` with `job=<id>`.
7. Follow the job on the job page, or `status.json` in the repo.

## Alternatives
| Route | When |
| --- | --- |
| An agent writes the brief and pushes | Sam asked in chat, or a slate film |
| `film.yml` dispatch with `job=<id>` | resume or restart a stage |

## Checks before showing Sam
Before Sam's first paid build, the lead runs and checks one paid film (decision 0013, Consequences).

## Known traps
- Not tested live end to end as of 23 Oct: a real director turn, a real build commit and the `films` release listing
  were tested only against a mock OpenRouter (`studio-web/tests/flow.mjs`).
- A 402 from OpenRouter in the chat falls through to a free seat; the UI says so in one line.
- `approved_at` changes start a fresh job: re-saving an old brief restarts it.

## Sources of truth
`studio-web/app/api/build/route.js` (the code wins), `studio-web/components/Studio.jsx`, `studio-web/components/Job.jsx`,
`studio-web/app/api/job/route.js`, `docs/WORKFLOWS.md` ("Web studio"), `docs/STATUS.md` (Web studio).
