# The studio director: from a conversation to a finished film (design, 22 Oct 2026)

> The design as first written. The money and seat sections below describe the original paid design; the mode in force
> is in `config.json` and `README.md`, and the money rule in `docs/decisions/` (see `AGENTS.md` section 3).

Goal (Sam, 22 Oct): the studio makes films like the Battle Map and Dark Corners series about **any subject**, from a
simple discussion with the director, **self-contained and self-sufficient**: no Claude Code session in the loop. Sam
talks to the director in the web studio, approves the brief, and gets the finished film back. Everything else runs on
GitHub runners with OpenRouter models, inside caps.

## The two production lines (styles the director can make with no hand coding)
| Line | Engine | Format | Good for |
| --- | --- | --- | --- |
| `battle-map` | `films/lib/battlemap/` (spec-driven, Terrain style) | 16:9, about 2.5 min | battles, campaigns, journeys, expeditions, anything about places and movement |
| `kinetic` | `films/lib/kinetic/` (spec-driven, Kinetic style, generalised from Bamberg) | 9:16, about 1 to 3 min | any story told through words, dates, numbers, documents, quotes: history, science, true stories |
Lantern Road and Clay stay hand-built for now (bespoke sets); they become lines when they have a spec-driven engine.

## The pipeline (`.github/workflows/film.yml`, folder `films/studio/<id>/`)
The web studio commits `films/studio/<id>/brief.json` (that push starts `film.yml`; it can also be dispatched with
`job=<id>`). Every stage writes `status.json` (stage, state, message, usd so far, outputs) and commits it, so the studio
shows progress. Every paid call is booked against the job cap in `brief.json` (`cap_usd`, default 1.50) and the ledger.

1. **Script** (`films/director/script.py`): the writer seat drafts the narration from the brief: 15 to 18 lines, about
   330 words, house structure (hook, title line `l01` = "The Battle of X." or the film title, beats linked by but/therefore,
   one clear picture idea per line, a closing line with a smile), house tone per line (Battle Map: upbeat with a glint
   of dark humour, kid-clear; Dark Corners: plain, restrained, adult). It also returns a **claims list** (every fact the
   script states). A checker seat from a different provider verifies each claim (true / doubtful / false, with a reason);
   doubtful or false claims go back to the writer (at most 2 rounds); anything still doubtful is cut. Code guards: no
   em or en dashes, no "...", no URLs, kid-safe words for Battle Map. Writes `ad.json` (prep block: voice, music prompt,
   vo lines) and `script.json` (lines, claims, verdicts).
2. **Sound** (`harness/shots/prep.py`, then `films/lib/battle_mix.py`): narration (the series narrator), score (Lyria 3
   Pro), word timings; the narration laid on the score's beat grid; `cues.json`, `film.json`, `audio/mix.m4a`.
3. **Picture spec** (`films/director/spec.py`): the coder seat writes `spec.js` for the line's engine from: the engine's
   SPEC.md, two finished example specs of that line, the cues (line and word times), the script's picture ideas, and
   `films/director/LESSONS.md`. **Probe** (idea taken from Harness2's Propose, Probe, Compose): two candidate specs are
   drafted in parallel by different models.
4. **Checks, in code first** (`films/director/check.cjs`): load the film in headless Chromium, render stills at every
   line start and a few word times, catch page errors, missing icons, unknown time refs, labels off screen, overlapping
   labels, blank frames. Errors go back to the coder seat (at most 3 repair rounds per candidate).
5. **Eyes** (`films/director/look.py`): the eyes seat gets a contact sheet of each surviving candidate with the
   narration line under each still, scores clarity (could a child follow it), match to the words, beauty, and lists
   fixes. The better candidate wins; its fixes go back to the coder seat once (compose), then the checks run again.
6. **Render**: the same parallel-parts renderer as rc-render (`.github/workflows/films-render.yml`, reusable), release
   `films`: `<id>.mp4`, `<id>-preview.mp4`, `<id>-poster.jpg`, `<id>-sheet.jpg`.
7. **Reflect** (`films/director/reflect.py`): one short paragraph of lessons from this job (what the checks and eyes
   caught, what was fixed) appended to `LESSONS.md` (Harness2's "experience reflector", kept small: the newest 40 lessons).
8. **Done**: `status.json` = done with the film's links; the studio shows it in the library. Sam watches and approves;
   nothing is published anywhere without him.

## Seats (filled live from OpenRouter, `studio-web/lib/crew.json`; build side `harness/director/agents.py`)
writer = head seat; checker = deputy seat (different provider from the writer); coder = head seat for the spec, crew
seat for repairs; eyes = eyes seat. Free models are the last resort when money is short.

## Money
Expected per film: script and checks about US$0.10, sound about US$0.25, spec and repairs about US$0.20 to 0.50, eyes
about US$0.02. Cap per job 1.50 by default. The build key needs credit for this to run.

## Not adopted from Harness2 (google-research/harness2)
The framework itself (Python 3.12, uv, Google Cloud CLI for model runs, Codex/OpenCode executors with unrestricted
network, built for benchmark evaluation of agent harnesses). Too heavy and the wrong shape for a render pipeline.
Two of its ideas are used: probing several candidates and composing the best (step 3 to 5), and a persistent lessons
memory updated after every job (step 7).
