# Narration and score (kinoforge `sound.yml`, `noor-sound.yml`)

Free sound for a narrated film folder, made on a runner and committed back: narration with Kokoro (Apache 2.0) or
Chatterbox (MIT), every line heard back by Whisper; the lines placed on a beat grid (`films/lib/battle_mix.py`, which
writes `cues.json` and `film.json`); the free procedural score (`films/lib/score/`, VSCO-2 CE CC0 samples plus synthesis,
steered by `ad.json` `prep.score`); the final mix by `films/lib/score/remix.py` (`audio/mix.m4a`). US$0. Venice was made
this way (Kokoro `bm_george` won the audition; -14.1 LUFS, voice 17.5 dB over the score). `noor-sound.yml` is the NOOR
variant (Chatterbox, `films/noor/lib/place.py`). The sound side in depth (score palettes, mixing, voices):
`docs/manual/sound/narration.md` and `docs/manual/sound/score-engine.md`.

## Inputs
`sound.yml`:
| Input | Meaning | Default |
| --- | --- | --- |
| `folder` | film folder holding `ad.json` with a `prep` block (`vo` lines, `voice`, `title_line`, `score` hints, optional `audition`) | required |
| `voice` | override `prep.voice`: `kokoro\|bm_george`, `kokoro\|bf_emma`, `chatterbox`, `chatterbox\|<ref.wav>` | blank |
| `redo` | `true` re-voices (deletes `audio/vo.json`, `audio/vo/`) | `false` |
| `audition` | comma list of voices (or `ad` for `prep.audition.voices`): voices only the audition lines (default the first two) into `<folder>/audition/<voice>/` with `report.json`; makes nothing else | blank |
`noor-sound.yml`: `films` = comma list of NOOR folders, each with `script.json`.

## Exact steps
1. Write `ad.json` with a `prep` block (copy `films/cutaway/venice/ad.json` or a battle's); no dashes, no "..." in lines;
   facts checked. Commit and push: the workflow checks out `main`.
2. Optional audition:
   ```bash
   gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main \
     -f 'inputs[folder]=films/cutaway/<id>' -f 'inputs[audition]=kokoro|bm_george,kokoro|bf_emma,chatterbox'
   ```
   Pull; read `<folder>/audition/report.json` (words per second, pitch range and movement, pauses, word error rate: 2.3
   to 3.0 words a second and more pitch movement read as natural) and listen to the takes.
3. Make the sound:
   ```bash
   gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main \
     -f 'inputs[folder]=films/cutaway/<id>' -f 'inputs[voice]=kokoro|bm_george'
   ```
   NOOR: `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/noor-sound.yml/dispatches -f ref=main -f 'inputs[films]=films/noor/<id>'`.
4. Watch: `gh api "repos/Eouchi147/kinoforge/actions/workflows/sound.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.status,.conclusion]'`.
   The log goes to release `logs`.
5. `git pull --rebase`: the runner committed `audio/vo/*.mp3`, `audio/vo.json`, `audio/score_plan.json`,
   `audio/score.json`, `audio/mix.m4a`, `cues.json`, `film.json`. The picture now follows `cues.json`: never change its timing.
6. Listen to the mix; check loudness (about -14 LUFS for narrated films).

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Director sound stage (paid: ElevenLabs `brian` with Whisper retakes; free mode: Chatterbox or Kokoro) | director films | paid inside the cap, or free |
| `codead.yml` prep (Lyria score with a beat map, ElevenLabs casting, dialogue with Whisper times) | ads; it also accepts folder paths such as `films/battles/cannae` (used 21 Oct for the battles) | about US$0.05 to 0.07 an ad |
| No voice: CC0 recordings from the sound bank plus a quiet score (`films/cutaway/series/audio_kit.py`, `music_kit.py`, the folder's `audio/make_audio.py`; `KF_SOUND_DUR` for lengths other than 20 s) | showcase and nature films, the meadow | free |
| Re-score only (picture unchanged) | a music note from Sam | `films/lib/score/remix.py`, then `remux.yml` |

## Checks before showing Sam
Every line heard back (word error under the threshold; Whisper words differ from the script, so on-screen words come from
the script timed by alignment); loudness on target; the score does not fight the voice.

## Known traps
- Chatterbox needs `setuptools<81` in its env (resemble-perth imports `pkg_resources`); both workflows pin it.
- Kokoro British voices (`bf_*`, `bm_*`) are phonemised en-gb by the workflow.
- `voice_free.py` skips a folder whose `audio/vo.json` exists: use `redo=true` (or delete it for NOOR) to re-voice.
- apt mirrors have hung for 30 min on some runners: `sound.yml` takes a static ffmpeg build first.
- Encode mixes to a temp file and verify before replacing (checkpoint commits once caught half-written mixes).
- Beat trackers halve or double the tempo: check the grid before timing cuts to music.

## Sources of truth
`.github/workflows/sound.yml` and `noor-sound.yml` (their header comments), `films/director/voice_free.py`,
`films/lib/battle_mix.py`, `films/lib/score/README.md`, `docs/LESSONS.md` (Sound), `docs/WORKFLOWS.md`.
