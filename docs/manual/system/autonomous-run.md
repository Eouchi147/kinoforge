# A fully autonomous run: brief to delivered film

How the studio goes from an idea to a film in Sam's hands with the fewest human steps, every decision point, and who
decides. Two routes exist. Route A (the director pipeline) needs no agent session at all after the brief. Route B (an
agent builds the film by hand on an engine or the Cutaway line) gives the best craft today. Both end with the same checks
and the same delivery. Sam's approval is the only human step in each: the subject (and look) before production, and the
film before anything is published.

## Inputs
- A subject from Sam (chat, the web studio's Director tab, or `films/director/SLATE.md`).
- The line or style (`docs/manual/styles/`), the format (16:9 or 9:16), the length, the money cap.

## Route A: the director pipeline (no session in the loop)
| Step | What happens | Who decides | Where it is recorded |
| --- | --- | --- | --- |
| 1. Brief | Sam talks to the director chat (web studio, Director tab); it fills `title, line, subject, angle, audience, tone, target_seconds, notes` (and `format` for Cutaway) | Sam (subject, angle) | the chat |
| 2. Cap | Sam picks US$1, 2, 3 or 5 before "Build this film" (default 2.00) | Sam | `brief.json` `cap_usd` |
| 3. Build | "Build this film" (`POST /api/build`) commits `films/studio/<id>/brief.json` with `approved_at`; the push starts `film.yml` | Sam (the tap is the approval) | git history |
| 4. Credit check | `start.py` checks the build key holds the film's usual cost; stops with "add credit" if not | code | `status.json` |
| 5. Script | writer drafts; checker (another provider) rates every claim; up to 2 rewrites; doubtful claims cut | code and models | `script.json`, `ledger.json` |
| 6. Gate 1, facts | at most 20 % of claims cut, at least 70 % of target words left, nothing doubtful in the hook or title; else stop | code | `status.json` |
| 7. Sound | narration (paid: ElevenLabs `brian`; free: Chatterbox or Kokoro), Whisper check and retakes, beat grid, free score, mix | code | `audio/`, `cues.json`, `film.json` |
| 8. Spec | coder writes the picture (Battle Map and Kinetic: `spec.js`; Cutaway: `spec.json` data), second draft if the cap allows | models | `cand/` |
| 9. Check | `check.cjs` (web lines) or the line validator (Cutaway), up to 3 repair rounds | code | `check/` |
| 10. Gate 2, eyes | contact sheets scored, at least 6.5 of 10, up to 2 compose rounds; else stop, nothing rendered | code and the eyes model | `spec_log.json`, `status.json` |
| 11. Render | `films-render.yml` (parts on runners) to kinoforge release `films`: `<id>.mp4`, `-preview.mp4`, `-poster.jpg`, `-sheet.jpg` | code | release, `status.json` |
| 12. Reflect | up to 3 lessons appended to `films/director/LESSONS.md` | code | `LESSONS.md` |
| 13. Shown in the studio | the job page (`#job/<id>`) polls `status.json`; the Films page lists the release film | none | web studio |
| 14. Check | an agent runs `quality-checks.md` (numbers, sheet, three stretches) | agent | `docs/LOG.md` |
| 15. Deliver | link or Mac copy, numbers, cost against the cap, weak spots | agent | LOG, STATUS, catalog |
| 16. Publish | anything leaving the studio (social, a client, YouTube) | **Sam only** | LOG |
Steps 4 to 13 run on GitHub with no session. Steps 14 and 15 need an agent (or Sam watching the job page).

## Route B: an agent builds the film (best craft today)
| Step | What happens | Who decides |
| --- | --- | --- |
| 1. Subject and look | Sam names the subject; for a new look or client, a style board of free stills first (0008), Sam picks | Sam |
| 2. Folder | `films/<series>/<id>/` from the closest existing film (its recipe in `docs/manual/films/`) | agent |
| 3. Script and facts | `script.json` or `ad.json` prep lines, every fact checked against two sources, listed in `NOTES.md` | agent |
| 4. Sound first | `sound.yml` (free narration, free score, mix) or the series sound kit for no-voice films; the picture follows `cues.json` | agent (voice audition if new) |
| 5. Plan | scene list (each with a job), shot list with a reason per cut, camera per scene, in `NOTES.md` | agent, by `CRAFT.md` |
| 6. Build | engine spec or Blender scene; checks (`scenes.mjs`, `check.cjs`, Cutaway `validate.py`) to zero errors | agent |
| 7. Look | local stills, then runner stills (`stills.yml`, at most 8 frames, one run in flight); open every still | agent |
| 8. Gates and record | `bash tools/verify.sh`, NOTES, LOG, STATUS, commit, push | agent |
| 9. Render home | Mac lane if the Mac is connected and Sam agreed to its use today; else `films.yml` | agent (ask Sam once a day for the Mac) |
| 10. Check, deliver | `quality-checks.md`, `deliver-to-sam.md` | agent |
| 11. Publish | | **Sam only** |

## The decision points, in one list
| Decision | Who | Rule |
| --- | --- | --- |
| Subject, angle, audience | Sam | `SOUL.md` 6.3: subjects are his |
| A new look or a new client's look | Sam, from a board | 0008 |
| A house style or look he already approved | agent | `SOUL.md` 6.2 (reversible, in your folder) |
| Money cap (director) | Sam | 0013 (default 2.00) |
| Any paid image or video generation | Sam, per job | 0008, 0013 |
| Voice for a new series | agent auditions, Sam hears it in the first film | `SOUL.md` 2 (natural voices) |
| Shot list, cuts, camera, sound timing | agent | `CRAFT.md`; every element has a written job |
| Render home and parts | agent | `architecture.md`; Mac use asked once a day |
| Re-direct after a verdict | agent, from Sam's notes | `docs/PLAYBOOKS/redirect-from-sams-notes.md` |
| Publish, post, send to a client | Sam | AGENTS.md section 3 |
| Change a rule or contradict a verdict | Sam | AGENTS.md section 4 |

## When a run stops (and what to do)
| Stop | Where it shows | Do |
| --- | --- | --- |
| No credit (HTTP 402) or cap reached | `status.json` `message` | Tell Sam in one line; after credit, `film.yml` with `from=resume` |
| Free models' daily limit (free mode) | `status.json`, log | Wait for 00:00 UTC; resume; one job at a time |
| Gate 1 or Gate 2 failed | `status.json`, `check/final/` | Nothing was rendered; read the sheet; fix the brief or the line; restart from the stage |
| A render part hangs or fails | the run's jobs | Cancel, `rerun-failed-jobs` (see `../workflows/render-film-on-runners.md`) |
| A render waits on another | | a `chain.yml` rule, never a session watcher |
| The chat container restarts | | everything that must happen later is on GitHub or in STATUS |

## Alternatives
- Free mode (US$0): Route A with `free_only: true`; script and sound are fine, the picture spec is weak.
- Hand-built films with no engine (Lantern Road, Clay): Route B only; their recipes are in `docs/manual/films/`.

## Checks before showing Sam
`quality-checks.md` for every film from either route. The delivery names the cost and the weak spots.

## Known traps
- As of 23 Oct 2026 Route A has not produced a finished film: the free day stopped Salamis at the picture spec, and
  paid mode waits on credit. The Cutaway line in the director is tested with mocks, not live. Watch the first paid run.
- Run one director job at a time (free limits, shared runner queue).
- The web studio's build needs `GITHUB_TOKEN` on Vercel; without it the button says "GitHub is not connected yet".

## Sources of truth
`films/director/README.md`, `.github/workflows/film.yml`, `studio-web/app/api/build/route.js`, `docs/PLAYBOOKS/*.md`,
`docs/decisions/0005`, `0008`, `0013`, `docs/SOUL.md` section 6, `AGENTS.md`.
