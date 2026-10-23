# Code ads (kinoforge `codead.yml`) (lane paused)

Business ads built in code, music first. Two modes, one or several ads per run: `prep` (`harness/shots/prep.py`: a
Lyria score and its beat map, voice casting where every candidate reads every line and an audio model scores the reels,
dialogue with Whisper word times; committed to `ads/<id>/audio/`) and `render` (`harness/shots/codead.py`: the scene
`ads/<id>/index.html` rendered frame by frame in Chromium with optional motion blur and grain, mixed with the prepared
audio, -14 LUFS, a listening check by an audio model). Outputs in kinoforge release `ads`: `<id>.mp4`, `<id>-sheet.jpg`,
`<id>-listen.json`; cost in `ads/<id>/ledger.json`. Made this way: `unmissed-01` and the five Unmissed directions
`unmissed-v1` to `-v5` (Sam's verdicts in the catalog; Bento v5 loved and chosen). Paused: Bento polish, natural voices,
a 9:16 layout and a French version wait on Sam.

## Inputs
| Input | Meaning | Default |
| --- | --- | --- |
| `ad` | comma list of ad ids under `ads/`, or folder paths (e.g. `films/battles/cannae`) | required |
| `mode` | `prep` or `render` | `render` |
The folder: `index.html` (fixed 1920x1080 stage; `window.KF = {duration, fps, render(i, t)}`, every style set from `t`;
`window.KF_READY = true` after fonts and images load; helpers in `ads/lib/motion.js`: `seg`, `ease`, `words`, `rise`,
`fitStage`) and `ad.json` (`cues`, `duration`, `audio` block with `music_offset`, gains, voice and dialogue start
times, `cap_usd`; older single-step ads: `voice`, `vo`, `music.prompt`, `sfx`).

## Exact steps
1. Brief (business invented and marked Sample, or Sam's own cleared brand; claims only in its written words:
   `harness/shots/policies/unmissed.md`); style board first for a new look; Sam picks.
2. Write `ad.json` prep; commit, push; dispatch prep (paid, about US$0.05 to 0.07, needs Sam's go):
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/codead.yml/dispatches -f ref=main -f 'inputs[ad]=<id>' -f 'inputs[mode]=prep'`.
3. Pull `ads/<id>/audio/` (`music.json`: bpm, beats, downbeat guess, energy curve, biggest rise; `casting.json`;
   `dialogue.json`). Check the beat grid with librosa (`start_bpm`) before timing cuts.
4. Write the scene to that audio. Preview locally (free):
   `node harness/dom-render.cjs ads/<id> --stills 1.5,6,12 --stills-only --out out/<id>`.
5. Render (about US$0.01): same dispatch with `inputs[mode]=render`; about 6 min.
6. Download from release `ads`; read `<id>-listen.json`; check; deliver; nothing is published without Sam.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Cutaway trade ad (`films/cutaway/ads/drainage/`) | trades whose work is underground or hidden | free |
| Social templates (`social.md`) | 9:16 batches | free plus optional music |
| AI footage (`style-boards-and-ai-footage.md`) | inserts only; one solid subject | paid, Sam's go |

## Checks before showing Sam
Claims match the policy word for word; words, logos and numbers set in code; the listening check has no problems; the
render passes `../system/quality-checks.md`.

## Known traps
- Lyria returns audio only when streamed; its scores do not follow the brief's structure (most ads needed a
  `music_offset`, a delayed copy or bar-aligned cuts).
- ElevenLabs premade voices for dialogue were "too fake" (The Call).
- Grain is incompressible: codead caps the bitrate (crf 20, max 14 Mbps).
- A new workflow file is registered only after a push touching it (`codead.yml` on 16 Oct).
- Never measure the stage before fonts load.

## Sources of truth
`.github/workflows/codead.yml`, `harness/shots/prep.py`, `harness/shots/codead.py`, `docs/WORKFLOWS.md` ("Business ads"),
`docs/PLAYBOOKS/make-a-business-ad.md`, `docs/SOUL.md` (business looks and verdicts).
