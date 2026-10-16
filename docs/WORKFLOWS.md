# Workflows: how to run every pipeline

All pipelines run on GitHub's free runners (`.github/workflows/`). Start one from the Actions tab ("Run workflow"), or with
the REST API (the `gh` CLI's GraphQL commands may be blocked in some sessions; REST always works):

```bash
gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/<file>.yml/dispatches -f ref=main -f inputs[<name>]=<value>
gh api "repos/Eouchi147/kinoforge/actions/workflows/<file>.yml/runs?per_page=1" --jq '.workflow_runs[0] | [.id,.status,.conclusion]'
```

Outputs land in GitHub releases. Download an asset by id (works where `gh release download` does not):

```bash
gh api repos/Eouchi147/kinoforge/releases/tags/<release> --jq '.assets[] | "\(.id) \(.name)"'
gh api -H "Accept: application/octet-stream" repos/Eouchi147/kinoforge/releases/assets/<id> > <file>
```

A new workflow file is only registered after GitHub processes a push that contains it. If dispatching gives 404, push
another commit and try again.

---

## Business ads

### `codead.yml`: an ad built in code
- **What:** renders `ads/<id>/index.html` frame by frame (Chromium), adds voice, music and interface sounds, mixes to -14 LUFS.
- **Input:** `ad` = the folder name under `ads/`. The folder holds `index.html` (the scene) and `ad.json`:
  `voice` (an ElevenLabs voice name), `vo` (lines with start times), `music.prompt`, `sfx` (cue times and kinds:
  ring, click, pop, whoosh, check, chime), `cap_usd`.
- **Output:** release `ads`: `<id>.mp4` (16:9 master), `<id>-sheet.jpg`, `codead.log`. Cost record `ads/<id>/ledger.json` is committed.
- **Cost:** picture free; voice about $0.002 per line; music about $0.05 to $0.08. About 6 minutes per run.
- **Code:** `harness/shots/codead.py`, `harness/dom-render.cjs`, `ads/lib/motion.js`.
- **Local preview (free):** `cd harness && npm ci && npx playwright install chromium && cd ..` then
  `node harness/dom-render.cjs ads/<id> --stills 1.5,6,12 --stills-only --out out/<id>` (key frames as PNG), or without
  `--stills-only` for the full silent MP4. Query parameters reach the page with `--param key=value` (photos, variants).
- **Writing a scene:** a fixed 1920x1080 stage; `window.KF = { duration, fps, render(i, t) }` sets every style from `t`
  (no CSS transitions); set `window.KF_READY = true` after fonts and images load. Use `ads/lib/motion.js`
  (`seg`, `ease`, `words`, `rise`). Keep scene windows and `ad.json` timings in step.

### `board.yml`: a style board
- **What:** generates stills per look so Sam can choose before any video money is spent. Optional: background removal
  (`"cutout": true` gives `<id>.cut.png`, transparent) and short image-to-video tests (`"clips"`).
- **Input:** `board` = folder under `boards/`, holding `board.json`: `cap_usd`, `aspect`, `frames` (id, model, prompt,
  optional aspect and cutout), optional `clips` (id, from = a frame id or a file in the folder, prompt, seconds, model).
- **Output:** release `boards`: `<board>-<frame>.jpg`, `.cut.png`, `.mp4`, `<board>-board.log`. `boards/<id>/ledger.json`
  and `account.json` (the key's usage before and after) are committed.
- **Cost:** about $0.09 per Seedream still, $0.14 per Gemini still, $0.60 per 6 s Veo 3.1 Fast clip.
- **Code:** `harness/shots/board.py`. Every paid output is saved the moment it exists.

### `piece.yml`: an ad from AI footage (the shot factory)
- **What:** the head director writes a treatment from the brief, references and keyframes are generated and scored,
  clips are generated from the keyframes, then voice, music, edit, end card set in code, 9:16 cut, head review.
- **Input:** `piece` = folder under `pieces/` with `brief.json` (type, tier, policy, aspect, direction, duration, brand,
  idea, end_card, notes, cap; controls: `stop_after`, `redo_keyframes`, `redo_clips`, `accept_keyframes`, `clip_audio`).
- **Output:** release `pieces` (mp4s, keyframes sheet, contact sheet, work archive, log); `pieces/<id>/*.json` committed.
- **Cost:** tiers in `factory.py`: draft (Veo 3.1 Lite 720p, cap $4), standard (Veo 3.1 Fast 1080p, cap $10),
  premium (Veo 3.1, cap $12). Use `stop_after: "keyframes"` to check stills before paying for video.
- **Caution:** the automatic clip re-render doubled costs on 15 Oct. Prefer `stop_after` and a human look over loops.

## Film lanes (parked while ads come first)

| Workflow | What | Trigger |
| --- | --- | --- |
| `render.yml` | Renders the anthology prototypes in `proto/` to the `gallery` release | push `render/queue/*.json` or run by hand |
| `showcase.yml` | Scene agent writes each showcase film from its story and style; proven renders go to `render` | by hand |
| `voice.yml` | Narration takes (OmniVoice), automatic take checker, placement; `voice` release | push `voice/queue/*.json` |
| `finish.yml` | Joins picture and narration, ducks the score, masters; `showcase` release | after `render` and `voice` |
| `director.yml` | The multi-agent director builds a film from an approved brief in `films/<id>/` | push `films/*/brief.json` |
| `motion.yml` | Learns a human-motion baseline from licence-safe mocap; `motion` release | push `motion/queue/*.json` |
| `smoke.yml` | Regression: the harness still renders a frame | pushes touching `harness/` |

## Checking a result before Sam sees it

```bash
ffmpeg -i ad.mp4 -vf "fps=1.2,scale=480:-2,tile=4x3" -frames:v 1 sheet.jpg      # contact sheet
ffprobe -v error -show_entries format=duration -of csv=p=0 ad.mp4               # length
```
Look at the sheet and at least one moving clip. Reject warping, melting, extra fingers, unreadable or wrong text,
claims outside the policy, and anything that could read as alcohol or pork for a halal-friendly client.
