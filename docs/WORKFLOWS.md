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

A new workflow file is only registered after GitHub processes a push that changes it. If dispatching gives 404, push a
commit that touches that workflow file (a blank line is enough), wait about 20 seconds, then dispatch again.

---

## Business ads

### `codead.yml`: an ad built in code (music first)
- **Two modes, one or several ads per run** (`ad` = comma-separated ids, `mode` = `prep` or `render`):
  1. `prep` (`harness/shots/prep.py`): makes the score (Lyria) and its beat map (`audio/music.json`: bpm, beats, a downbeat
     guess, a 0.1 s energy curve, the biggest rise), casts the narrator (every voice in `prep.voice_cast` reads every line,
     an audio model scores the reels, `audio/casting.json`), records dialogue with Whisper word timings (`audio/dialogue.json`).
     Files are committed to `ads/<id>/audio/`. About $0.05 to $0.07 per ad.
  2. Write the scene to that audio: `ads/<id>/index.html` reads `./ad.json` (its `cues`, `duration`, and `audio` block with
     `music_offset`, gains, voice/dialogue start times) so picture and sound share one timeline. Beat trackers often halve or
     double the tempo: check the grid (librosa with `start_bpm`) before timing cuts.
  3. `render` (`harness/shots/codead.py`): renders the scene (motion blur from `render.sub` sub-frames, film grain from
     `post.grain`), mixes the prepared audio (ducking, -14 LUFS), runs the listening check. About $0.01 per ad.
- **Older single-step ads** (like `unmissed-01`) still work: without an `audio` block, voice and music are generated during render.

### (previous description of the single-step mode)
- **What:** renders `ads/<id>/index.html` frame by frame (Chromium), adds voice, music and interface sounds, mixes to -14 LUFS.
- **Input:** `ad` = the folder name under `ads/`. The folder holds `index.html` (the scene) and `ad.json`:
  `voice` (an ElevenLabs voice name), `vo` (lines with start times), `music.prompt`, `sfx` (cue times and kinds:
  ring, click, pop, whoosh, check, chime), `cap_usd`.
- **Output:** release `ads`: `<id>.mp4` (16:9 master), `<id>-sheet.jpg`, `<id>-listen.json` (an audio model's transcript and notes on voice, music, sounds and mix), the music stem, `codead.log`. Cost record `ads/<id>/ledger.json` is committed.
- **Cost:** picture free; voice about $0.002 per line; music about $0.05 to $0.08. About 6 minutes per run.
- **Code:** `harness/shots/codead.py`, `harness/dom-render.cjs`, `ads/lib/motion.js`.
- **Local preview (free):** `cd harness && npm ci && npx playwright install chromium && cd ..` then
  `node harness/dom-render.cjs ads/<id> --stills 1.5,6,12 --stills-only --out out/<id>` (key frames as PNG), or without
  `--stills-only` for the full silent MP4. Query parameters reach the page with `--param key=value` (photos, variants).
- **Writing a scene:** a fixed 1920x1080 stage; `window.KF = { duration, fps, render(i, t) }` sets every style from `t`
  (no CSS transitions); set `window.KF_READY = true` after fonts and images load. Use `ads/lib/motion.js`
  (`seg`, `ease`, `words`, `rise`). Keep scene windows and `ad.json` timings in step.
- **Other sizes:** `fitStage(stage, { w, h })` scales the stage uniformly to the render size (`--w`/`--h`); a different
  aspect is letterboxed, never stretched. A 9:16 version needs its own layout (see the social lane below). Never measure
  the stage before the fonts load (an early `offsetWidth` read shifts glyph rasterization).

### `social.yml`: phone-format (9:16) social videos from templates
- **What:** renders a batch of short videos for TikTok, Instagram Reels, YouTube Shorts and Facebook Reels from code
  templates (`social/templates/<template>/`), one runner per video. Three looks so far: `card-motion` (A, the client's own
  card in motion), `bento` (B), `type-motion` (C). Everything about the lane: `social/README.md`.
- **Input:** `batch` = folder under `social/batches/` (for example `smartmount/2026-12`) holding `batch.json`: `client`,
  `batch`, `render` (`sub` = motion-blur sub-frames), optional `music` (`enabled`, `prompt`, `cap_usd`, `gain_db`,
  `offset_s`) and `videos` (`id`, `template`, `card` with eyebrow, title, body, fact, `photo`, `platforms`, optional
  `figure`). Optional `only` = comma-separated video ids.
- **Steps:** plan (`social/lib/check.mjs`: words, house style, photos, templates, captions; music made once by
  `harness/shots/social.py music` and committed with `ledger.json`); per video: captions (`social/lib/captions.mjs`, code,
  no AI), safe-zone check (`social/lib/safecheck.mjs`, every frame: fails if a word, number, URL or logo mark leaves rule
  R-2-08's box, x 0.11 to 0.78 and y 0.15 to 0.65 of the frame; the one constant is `SAFE` in `social/lib/brief.mjs`),
  render (`harness/dom-render.cjs`, 1080x1920, 30 fps), mix and cover (`social.py finish`: -14 LUFS, or a silent track);
  ledger job commits the render records.
- **Output:** release `social`: `<client>-<batch>-<id>.mp4`, `-cover.jpg`, `-captions.json` (TikTok, Instagram, YouTube title
  and description, Facebook, the AI disclosure note). Committed: `social/batches/<client>/<batch>/audio/music.mp3`,
  `ledger.json` (`calls` with costs, `renders`). Nothing is posted by the lane. Posting gate (`social/README.md`): nothing
  before Sam approves the batch, and nothing for Smart Mount while smartmount.ca is parked (smartmount `api/_parked.js`).
- **Cost:** pictures free; music about $0.04 to $0.08 once per batch (cap in `batch.json`); runner time about 3 to 5 minutes
  per video (Chromium setup plus the render), so about 40 to 60 job-minutes for 12 videos (see the minute limit in
  `docs/CI-PURPOSE.md`).
- **Local, free:** `node social/lib/check.mjs social/batches/<client>/<batch>`; stills: `node harness/dom-render.cjs
  social/templates/<t> --w 1080 --h 1920 --stills 0.5,3,7 --stills-only --param brief=/social/batches/<client>/<batch>/batch.json
  --param id=<video id>` (`--param guides=1` shows the platform zones); `node social/lib/safecheck.mjs social/templates/<t>`.

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

## Web studio: make a film from a conversation
Open https://kinoforge-studio.vercel.app (Vercel sign-in), Director tab, name a subject, agree the brief, tap "Build this film". The studio commits `films/studio/<id>/brief.json`; `film.yml` runs; the job page (`#job/<id>`) shows stages and spend from `films/studio/<id>/status.json`; the finished film appears under Films (release `films` of this repo). Media is streamed through `/api/media` from public releases (allow-list in `studio-web/lib/media.js`).
By hand: commit `films/studio/<id>/brief.json` (format in `films/director/README.md`). Free-only by default since 22 Oct 2026: free OpenRouter seats, Chatterbox or Kokoro narration on the runner, the free score engine; a paid model is refused in code. Resume or restart a stage: dispatch `film.yml` with `job=<id>` and `from=` (REST: `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/film.yml/dispatches -f ref=main -f 'inputs[job]=<id>'`).

Lines: `battle-map` (16:9), `kinetic` (9:16) and, since 23 Oct, `cutaway` (16:9 or 9:16 by the brief's `format`, 30 to
90 s; Blender). For a Blender line the coder seat writes `spec.json` (data, `films/lib/cutaway/SPEC.md`), the check stage
runs the line's validator (`films/lib/cutaway/tools/validate.py`, seconds) instead of Chromium, the eyes get a 480 px
Blender contact sheet (`tools/stills.py`; `film.yml` installs bpy 5.2.2 in its own Python 3.13), and `films-render.yml`
renders it with 48 frames a part (4 to 20 parts). The Styles page's "Start a film" opens the director on a line.
Cutaway films by hand: `docs/PLAYBOOKS/cutaway-film.md`.

## Re-render a hand-built film (Dark Corners, Battle Map) on free runners
The film folder in this repo (`films/<series>/<id>/`: `film.json`, `cues.json`, `audio/mix.m4a`, `index.html` or
`blender.py`) is rendered by rc-render's `films.yml` (parallel parts, join with the film's own sound, release
`kino-films`; the same `id` replaces the old file). Dispatch through the REST API (GraphQL is blocked in Claude Code
sessions); `ref` must be a branch or a **full** commit hash (a short hash fails the checkout):
`gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/dark-corners/bamberg' -f 'inputs[parts]=14' -f "inputs[ref]=$(git rev-parse HEAD)"`.
Web films: 12 to 20 parts, 10 to 25 minutes. Blender films: 24 parts, about 80 minutes. Costs nothing (GitHub runners;
see the terms note in the handover).

Inserts: a film.json may list `inserts: [{film, first, last}]`: finished clips from `kino-films` (for example the Cutaway mud scenes in Agincourt) laid frame-exactly over film frames first to last before scaling. Render the inserts first.

Check stills (no video; one run in flight per builder, at most 8 frames, because the runner queue is shared with the film renders): rc-render `stills.yml` (inputs film, frames as a comma list up to 20, tag, w, h, samples,
ref), frames grouped per runner (`per_job`, default 4), files `<tag>-f<frame>.jpg` in release `stills`; download with
`bash tools/getstills.sh <tag> <dir>` in rc-render (REST; `gh release download` needs GraphQL, which is blocked in Claude Code sessions).

New sound on a finished film (re-score or re-mix, picture unchanged): rc-render `remux.yml` (inputs film, ref): takes `<id>.mp4` from `kino-films`, lays the folder's current `film.json` audio, republishes `<id>.mp4` and `<id>-preview.mp4`.

Free narration and score for any film folder with an `ad.json` prep block: kinoforge `sound.yml` (inputs folder, voice; Kokoro or Chatterbox on the runner, the free score engine), commits `audio/`, `cues.json`, `film.json`.

## Render on Sam's Mac (M4 GPU through Metal), the Mac lane
Lane home since 23 Oct: Sam's external drive, `/Volumes/Samsung X5/KINOFORGE/render/` (code copy: harness, films/lib, films/styles, films/cutaway, ads/fonts; `mac-jobs/`; frames under `KINOFORGE/frames/`; film archive in `KINOFORGE/films/`); refresh the code from GitHub's tarball when the films change. Fallback when the drive is unplugged: `Video Production/kinoforge-render/` (iCloud, file locks). Blender 5.2 app; the lane is started once per Blender launch by typing in Blender's Python console: `exec(open('/Volumes/Samsung X5/KINOFORGE/render/harness/mac/go.py').read())` (computer use, Blender only; not possible while Sam is in a full-screen app). Jobs: drop a JSON file in the lane home's `mac-jobs/` (`{film, out, w, h, samples, start, end, device: "METAL"}`; device_commit_files from the container works even when the Mac's Linux shell is down); frames land in `<out>/frames`, the log and job move to `mac-jobs/done/`. Measured 22 Oct: Venice at 1280x720, 24 samples: about 7.5 s per frame on the M4 GPU (10 cores), about 7 times one GitHub runner. The MacBook Air has no fan: expect slowdowns on long runs; keep it plugged in and awake. Free disk on the Mac was about 14 GB.

Follow-up renders (one render waiting on others) live in rc-render `chain.yml`, checked every 15 minutes on GitHub: a rule dispatches `films.yml` once all its needed assets exist in `kino-films`, then writes a marker `chain-<name>.done` to `film-logs`. No chat session has to stay alive.

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

## Spend records (23 Oct 2026)
rc-render `films.yml` (join) and `remux.yml` end with a `spend record` step: it appends the run (id, jobs, seconds, billable minutes) to `<film id>-run.json` in release `kino-films`. `python3 tools/spend.py --fetch-runs` reads them into `data/spend/runs.json`; `python3 tools/spend.py` rebuilds `studio-web/public/data/spend.json`. Paid calls go through `films/lib/spend_log.py` into the film's `ledger.json`.
