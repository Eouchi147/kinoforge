# The director pipeline: an approved brief in, a finished film out

Design: [`DESIGN.md`](DESIGN.md). Everything runs on GitHub runners (`.github/workflows/film.yml`) with OpenRouter models,
inside the job's cap. No Claude session in the loop. Nothing is published anywhere: the film lands in the release `films`
and waits for Sam.

## Money: paid by default, capped per film, gates before every next stage (Sam, 22 Oct 2026, 20:50)

"Cap the budget per film, but I need good results every time I pay." `config.json` `free_only: false` is the default:
the best model for each role (chosen by role, not by live ranking; `seats.py` checks every id against OpenRouter's live
list on the runner and logs its price before the first call), a hard cap per film, and quality gates so a film that
cannot reach the bar inside its cap stops and is never rendered.

| Role | Model (fallback) | Stage |
| --- | --- | --- |
| writer | anthropic/claude-opus-5.5 (claude-sonnet-5.5) | script |
| checker | google/gemini-4-argon (openai/gpt-6.1-sol), never the writer's provider | script |
| coder | anthropic/claude-opus-5.5 (claude-sonnet-5.5): the main picture draft | spec |
| coder2 | anthropic/claude-sonnet-5.5 (gemini-4-argon): a second draft, only when the cap leaves room | spec |
| repair | anthropic/claude-sonnet-5.5 (claude-opus-5.5): repairs and compose rounds, as edits | check, eyes |
| eyes | google/gemini-4-argon (claude-sonnet-5.5): scores contact sheets | eyes |
| crew | anthropic/claude-haiku-5.5 (claude-sonnet-5.5): the lessons | reflect |
| voice | ElevenLabs eleven-v4, `brian` (the battles' narrator), every line checked by Whisper, a misheard line retaken once | sound |
| music | the free procedural score (`films/lib/score`); Lyria only when the brief says `"music": "lyria"` | sound |

**The cap.** `brief.cap_usd`, default US$2.00, 0.50 to 5.00. Every call books its worst case (prompt tokens and
`max_tokens` at the live price) before it is sent, parallel calls included, and is refused if it could pass the cap.
Before the job starts, `start.py` checks the build key holds at least the film's usual cost (below) and stops with a
plain message if not, before anything is spent.

**The gates (Sam pays only for films that pass).**
1. Fact check (after the script, before any narration is paid): at most 20 % of the claims cut and at least 70 % of the
   target words left, nothing doubtful in the hook or the title line. Otherwise: stop.
2. Picture (after the spec, before any render): `check.cjs` passes (syntax, page and console errors, the line's lint and
   the engine's own scene checks, CRAFT.md section 9) and the eyes score the contact sheet at least 6.5 out of 10, with up
   to 2 compose rounds (each re-checked and re-scored, kept only if the score does not drop). Otherwise: stop, the best
   version and its contact sheet kept for a look, nothing rendered.
3. Narration: every line heard back by Whisper; a word error rate over 0.25 is retaken once (booked like any call).

**Expected cost per film** (150 s Battle Map; a 90 s film about 60 % of it; `config.json` `estimate_usd`):

| Stage | Usual | Worst inside the cap |
| --- | --- | --- |
| script (Opus draft and up to 2 rewrites, Gemini checks) | US$0.15 to 0.30 | 0.35 |
| sound (ElevenLabs about 330 words, retakes; music and mix free) | US$0.10 to 0.15 | 0.20 |
| spec (Opus draft, about 35k tokens in, 12k out; prompt cached for repairs) | US$0.45 to 0.55 | 0.70 |
| second draft (Sonnet), only when it fits | US$0.25 to 0.35 | 0.40 |
| checks and repairs (Sonnet edits, up to 3 per draft) | US$0.05 to 0.35 | 0.50 |
| eyes and compose (Gemini, 1 to 3 looks; Sonnet edits) | US$0.05 to 0.20 | 0.25 |
| reflect (Haiku) | under US$0.01 | 0.01 |
| render (GitHub runners) | free | free |
| **total** | **US$0.90 to 1.50** | **the cap (default 2.00)** |

## Credit (what Sam does, once; agents never touch keys)

Both OpenRouter keys are empty on 22 Oct 2026 evening (the studio key: limit US$5, US$5.00 used; the build key: about
US$1 or less). On openrouter.ai, Settings, Credits and Keys:
1. Add account credit: **US$25** covers about 15 films at the usual cost, with room for the director chat.
2. The **build key** (GitHub secret `OPENROUTER_API_KEY`, used by `film.yml`): raise its limit to **US$20** (about
   10 to 15 films; each film is also capped by its own `cap_usd`).
3. The **studio key** (Vercel env `OPENROUTER_API_KEY`, the director chat): raise its limit to **US$5 more** (a chat turn
   on Opus costs about US$0.02 to 0.05; when it runs dry the chat falls back to free models).
Nothing else changes: the keys stay where they are. A job that meets an empty key stops with "add credit" in
`status.json` and resumes where it stopped when re-run.

## Free mode (option)

`config.json` `free_only: true` (or `KF_FREE_ONLY=1` in the workflow env): every seat uses OpenRouter models whose id ends in `:free` (ranked live by published
intelligence, one per provider first; the eyes seat only gets free models that take images). A paid model id is refused
in code (`PaidRefused`), and any call that reports a cost stops the job (`OverBudget`). The sound stage is free too:
the narration is read by **Chatterbox** (MIT, CPU, in its own Python 3.11 env on the runner; `voice: "chatterbox"` or
`"chatterbox|path/to/ref.wav"` for a reference voice in this repo) or **Kokoro** (Apache 2.0, `voice: "kokoro|bm_george"`),
every line checked by Whisper (a take with word error above 0.15 is redone, at most 3 takes); the narration is placed on the beat grid of a quiet pad made in code (`pad.py`), the mix
runs, then the free procedural score engine re-scores it (`films/lib/score/remix.py <job dir>`, hook
`music_engines.procedural.remix` in `config.json`: it reads `cues.json`, `audio/vo/line*.mp3` and `ad.json`, writes
`audio/score_plan.json`, `audio/score.json` and a new `audio/mix.m4a`); if the engine is missing or fails, the pad stays
as the score and `status.json` says so. Free mode is weak for the picture (22 Oct: only a handful of capable free
models, rate limited, and the key's 1000 free requests a day ran out mid-job); use it for scripts and tests.

## Craft checks (CRAFT.md section 9, in `check.cjs`)

The writer, coder and eyes seats all read `CRAFT.md`. In code, before any render (`check.cjs`, `lint/battle-map.js`):
a scene list (`scenes`, 5 to 9, each with its job; on Battle Map v2 the engine's own `compileScenes` runs and its errors
are hard: shots need `from` and `why`, camera moves faster than a real camera are refused, shot count and jump cuts),
the shot count (at most 40 per 3 minutes) and average shot length (4 to 12 s), a written `why` on every cut, camera speed
for v1 `camera` keys (at most 0.25 frame widths per second and a 10 % per second push; twice that is a hard error), no
emoji in the spec, a `legend` and an `ambient` block on Battle Map (hard because the engine's SPEC.md documents them),
no overlapping or clipped text. Clip-art icon names are refused only on engines without refined glyphs (v2 redraws every
v1 name as a flat glyph, so there it is a warning to keep only icons with a job). `KF_CRAFT=0` turns the craft checks off
(tests, films made before CRAFT.md). The v2 Cannae passes every check; the v1 films fail them, as they should.

## Start a job

The web studio commits `films/studio/<id>/brief.json`; that push starts `film.yml`. By hand:

1. Write `films/studio/<id>/brief.json` (format below; `<id>` is lowercase letters, digits and dashes).
2. `git add films/studio/<id>/brief.json && git commit -m "film <id>: brief" && git pull --rebase && git push`.
3. Watch `films/studio/<id>/status.json` (or the run: `gh api repos/Eouchi147/kinoforge/actions/runs?per_page=3`).

Re-run or resume: Actions, `film`, Run workflow, `job=<id>`, `from=resume` (default: skips every stage whose outputs
exist, so nothing is paid twice) or `from=script|sound|spec|render|reflect` (clears that stage and the later ones).
CLI: `gh workflow run film.yml -f job=<id> -f from=spec`. A push of the brief with a new `approved_at` starts fresh.

## Brief format (`films/studio/<id>/brief.json`)

| field | required | meaning |
| --- | --- | --- |
| `id` | yes | the folder name |
| `title` | yes | working title, e.g. "The Battle of Tours" |
| `line` | no (`battle-map`) | production line: `battle-map` (16:9, Terrain maps) or `kinetic` (9:16, type and documents) |
| `subject` | yes | what the film is about, e.g. "The Battle of Tours, 732: Charles Martel stops the Umayyad army" |
| `angle` | no | the angle agreed in the chat with the director |
| `notes` | no | anything else from the chat (must-have moments, things to avoid) |
| `audience` | no | e.g. "kids 8 to 14" |
| `tone` | no | overrides the line's house tone |
| `target_seconds` | no (150) | film length target, 45 to 240 |
| `cap_usd` | no (2.00) | hard money cap for the whole job, 0.50 to 5.00 (free mode spends nothing) |
| `voice` | no (`elevenlabs/eleven-v4\|brian`) | paid mode: `model\|voice` as `harness/shots/factory.speech` takes it; free mode: `chatterbox`, `chatterbox\|ref.wav`, `kokoro\|bm_george` |
| `music` | no | `"lyria"` for a Lyria score (about US$0.08); default: the free procedural score |
| `approved_at` | yes | ISO time Sam approved the brief (a new value restarts the job) |
| `seats` | no | advanced: `{writer, checker, spec: [seatA, seatB], repair, eyes}` seat names from `studio-web/lib/crew.json` |

```json
{"id": "battle-of-tours", "title": "The Battle of Tours", "line": "battle-map",
 "subject": "The Battle of Tours (Poitiers), 732: Charles Martel's Franks stop the Umayyad army of Abd al-Rahman",
 "angle": "the shield wall that stood all day", "audience": "kids 8 to 14", "target_seconds": 90, "cap_usd": 1.5,
 "voice": "elevenlabs/eleven-v4|brian", "approved_at": "2026-10-22T10:00:00Z"}
```

## Stages and files (all in `films/studio/<id>/`)

| stage | code | writes | usual cost |
| --- | --- | --- | --- |
| script | `script.py`: writer drafts lines, picture ideas and claims; checker (another provider) rates every claim; at most 2 rewrites; still-doubtful claims cut; code guards; **gate 1** | `script.json`, `ad.json` | see the money table |
| sound | `sound.py`: a pad made in code as the beat grid, `harness/shots/prep.py` (ElevenLabs voice, Whisper word times), retakes of misheard lines, the line's mix (`films/lib/battle_mix.py`), then the free score (`films/lib/score/remix.py`) | `audio/`, `cues.json`, `film.json`, `index.html` | |
| spec | `spec.py`: the main draft (Opus); a second (Sonnet) only when it fits the cap | `cand/a.js`, `cand/b.js` | |
| check | `check.cjs` on each draft; problems back to the repair role as edits, at most 3 rounds; the best version of each draft is kept | `check/<a,b>/report.json`, `sheet.jpg` | |
| eyes | `look.py`: the eyes score the contact sheets and pick the winner; up to 2 compose rounds, each re-checked and re-scored; **gate 2** | `spec.js`, `check/final/`, `spec_log.json` | |
| render | `.github/workflows/films-render.yml` (reusable): parallel parts on ubuntu-24.04, join, sound, publish; runs only after gate 2 | release `films`: `<id>.mp4`, `<id>-preview.mp4`, `<id>-poster.jpg`, `<id>-sheet.jpg` | free |
| reflect | `reflect.py`: at most 3 one-line lessons appended to `LESSONS.md` (newest 40 kept; `spec.py` reads them) | `reflect.json`, `LESSONS.md` | |

Every call is in `ledger.json` (seat, model, task, cost, seconds) and refused when it could pass `cap_usd`. An HTTP 402
from OpenRouter (key out of credit) stops the job with that message. The run log is uploaded to the release `logs` as
`<id>-film.log`.

## `status.json` (the contract with the web studio)

```json
{"id": "battle-of-tours", "title": "...", "line": "battle-map",
 "stage": "script|sound|spec|check|eyes|render|reflect|done", "state": "queued|running|done|failed",
 "message": "one plain sentence for Sam", "usd": 0.42, "cap_usd": 0.9,
 "outputs": {"script": "films/studio/<id>/script.json", "audio": "...", "duration": 91.2, "spec": "...", "check_sheet": "...",
             "video": "https://github.com/Eouchi147/kinoforge/releases/download/films/<id>.mp4", "preview": "...", "poster": "...", "sheet": "...", "log": "..."},
 "stages": {"script": {"state": "done", "started_at": "...", "ended_at": "...", "usd": 0.21, "spent": 0.21}, "sound": {"usd": 0.33, "spent": 0.12}},
 "approved_at": "...", "run_url": "https://github.com/.../actions/runs/...", "updated_at": "2026-10-22T10:12:00Z"}
```

Committed by the runner after every stage (pull, rebase, push, retried). Finished: `stage` = `done`, `state` = `done`.
Failed: `state` = `failed`, `message` says why, `outputs.log` links the run log.

## Production lines (`lines.json`)

A line is config: engine folder, `SPEC.md`, example films (their `spec.js` and `cues.json` are shown to the coder),
aspect, render and delivery sizes, title line, house tone and structure, picture and spec rules, music and voice
direction, an optional lint module run in the page by `check.cjs`. A line is available when its `SPEC.md` exists.
`battle-map`: examples Cannae and Hastings, lint `lint/battle-map.js`. `kinetic`: example `films/studio/kinetic-demo`
(look reference `films/dark-corners/bamberg`); the engine reports its own spec errors through `window.KF_ERROR`.
A new line = a new entry in `lines.json` (and a lint module if the engine does not check its spec itself).

## Tests (no paid calls)

`python3 films/director/tests/test_director.py` runs the stages with recorded model replies: house rules, script
rounds and cuts (checker from another provider), the fact-check gate, the paid seats and the cap booking (parallel calls
included), the eyes gate, resume and fresh starts, lessons, free mode, and the whole spec stage in Chromium on the
Hastings cues (a broken draft is repaired, the eyes pick the winner, the compose round is re-checked and re-scored).
`cd studio-web && npx next build && node tests/flow.mjs` walks the web studio against a mock OpenRouter (status and
credit, the director's turns on the paid head seat, the out-of-credit message, the build route's checks, the job route).
`node films/director/check.cjs films/battles/hastings --line battle-map` checks any finished film.
