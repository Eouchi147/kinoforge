# Legacy lanes (13 to 16 Oct 2026): kept, not used for new work

The first lanes of the studio, before the film engines, rc-render `films.yml` and the director pipeline. They still
work as written, and their outputs are in releases, but new work uses the pages listed under "Alternatives". Do not
delete them without Sam: the prototypes they rendered are the origins of the house styles.

## Inputs and what each does
| Workflow (kinoforge) | What | Trigger | Output |
| --- | --- | --- | --- |
| `render.yml` | Renders the anthology prototypes in `proto/` (web scenes one runner each; Blender scenes in frame-range parts) | push `render/queue/*.json`, or dispatch `scenes` (comma list or `all`), `w`, `h`, `queue` | release `gallery` (`<scene>.mp4`, `<scene>.contact.jpg`) |
| `showcase.yml` | A scene agent writes each showcase film from its story and style | dispatch `films` | proven renders to `render`; all runs failed on 15 Oct (truncated replies, about US$2.51); frozen |
| `voice.yml` | Narration takes (OmniVoice), automatic take checker, placement | push `voice/queue/*.json` | release `voice` |
| `finish.yml` | Joins a showcase picture and narration, ducks the score, masters | after `render` and `voice` | release `showcase` (empty) |
| `director.yml` | The first multi-agent director (head, deputy, crew) from `films/<id>/brief.json` | push `films/*/brief.json` or dispatch `film` | the folder; replaced by `film.yml` (`/api/film` removed 22 Oct) |
| `motion.yml` | Human-motion baseline from licence-safe mocap | push `motion/queue/*.json` | release `motion` |
| `smoke.yml` | Regression: the harness still renders a frame | pushes touching `harness/` | none (pass or fail) |

## Exact steps (to re-render the prototypes, the only legacy lane worth running)
`gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/render.yml/dispatches -f ref=main -f 'inputs[scenes]=p03-lantern-road'`
Assets land in release `gallery`. The catalog lists the 15 rendered prototypes and pilots (series "Anthology prototypes").

## Alternatives
Films: `render-film-on-runners.md`; narration: `narration-and-score.md`; a film from a brief: `director-pipeline.md`.

## Checks before showing Sam
As any render.

## Known traps
- `docs/CI-PURPOSE.md` describes these lanes as the project's regression set with self-imposed limits (about 1,500
  runner-minutes a month); keep that footprint in mind for every lane.
- The pilots "The Dragon Who Couldn't Fly" and "Why the Moon Changes Shape" waited on Sam's narrator approval (14 Oct);
  no later verdict is recorded.

## Sources of truth
The workflow files' header comments, `docs/WORKFLOWS.md` ("Film lanes"), `docs/CI-PURPOSE.md`,
`docs/HANDOVER-2026-10-16.md` (snapshot).
