# Showrunner playbook — how KINOFORGE makes a film, every time

This is the operating manual for the studio's AI director (the Showrunner on OpenRouter) and for any agent working in
this repo. It encodes how the films so far were actually made, including the mistakes that were caught. Follow it in
order. Where it points to another document, that document is part of the rules.

Read first: `docs/DIRECTORS_RULEBOOK.md` (§0 common sense + R-0-08 polish are blockers above everything),
`harness/README.md` (scene contract), this file.

## 0. Non-negotiables

1. **Common sense (§0).** Everything on screen makes sense to an ordinary viewer. Complete anatomy, ground contact,
   motion matches facing, story actions visible, continuity, nothing stray.
2. **Polish (R-0-08).** Clean, smooth, harmonious. Nothing harsh, scratchy or clunky unless the style asks for it.
3. **One story per film.** Every episode has its own original story and structure (YouTube "inauthentic content").
4. **No real people, no existing characters or brands.** Kids' films stay kind and safe.
5. **Sam does as little as possible.** One decision at a time, in plain words, with the exact action. Never ask him
   something the repo, the rulebook or a sensible default can answer.
6. **Licence ledger.** Every tool, model and dataset used is listed in `docs/LICENCES.md` with its licence. Nothing
   is published while a non-commercial item is in the film. (Today nothing is published; tests may use anything.)

## 1. The pipeline (stage → what you produce → where it lives → gate)

| Stage | You produce | Files | Gate (Sam) |
| --- | --- | --- | --- |
| Idea | 3 pitches, then one chosen through conversation | web studio chat | — |
| Story | Brief: logline, beats ("but/therefore"), characters, ending image, narrator, music mood | `films/<id>/brief.json` | **Gate 1: "Build it"** |
| Style | Style pack + motion profile + colour script + sound palette | `films/<id>/style.json` | — |
| Script & shots | Narration lines with start times; shot list with size, lens, move, motivation; cue sheet (frame numbers) | `films/<id>/script.json`, `NOTES.md` | — |
| Build | Scene code in the style pack's renderer; puppets/characters from the pack's library | `films/<id>/scene.js` or `blender.py` | — |
| Animatic | Low-res full-length render + contact sheets + narration takes | GitHub `gallery` / `voice` releases | **Gate 2: animatic** |
| Review loop | Eyes + Ears + motion checker until zero blockers | `films/<id>/REVIEW.md` | — |
| Render | 1080p on GitHub (tests) or the Mac (finals) | `render/queue/*.json`; Mac helper | **Gate 3: final picture** |
| Deliver | Video, captions (SRT), thumbnail options, title, description with credits + AI disclosure | `films/<id>/deliver/` | **Gate 4: deliver** |

## 2. Story (before any code)

- Hook in the first 3 s. A turn at ~70%. An ending image that rhymes with or inverts the opening.
- Every beat causes the next ("but", "therefore"). Every payoff is set up on screen ≥15% of runtime earlier.
- Each beat is an *action you can see*, written as a frame description: who, where, doing what, readable on a phone.
- Characters: silhouette-readable, one want, one flaw. Kids' films: comic, warm, never cruel.
- Narration is minimal and wise: it never describes what the picture already shows; it adds meaning.

## 3. Style packs and motion

Choose the pack that serves the story (`studio-web/lib/data.js` lists them). Each pack defines its renderer, character
kit and **motion profile**: never use raw realistic motion in a stylised pack. Apply the style layer in this order:
base motion → cartoon filter (k per style) → re-time (shoot on 1s/2s/3s, holds) → shape (squash, smears) → secondary
springs → imperfections and camera → forbid-list check → plausibility check (`harness/motion/check.py --profile <style>`).
Values per style: blueprint "Style motion" table (Reference doc, Studio blueprint tab).

Hard-won rules from the prototypes:
- Paper theatre: pins and rods only; creases must live on the paper (clip them); no scratch-like lines; the hillock
  in front must never hide a character standing on the ground.
- Characters that stand on the ground share the ground plane's depth so their feet stay locked during camera moves.
- A breath, a throw, a puff: aim it at its target and size it to reach it (see `aimTarget` in p16).
- Never stretch narration in time to fit the picture: generate takes that fit their window instead.
- When the camera pushes in on a moment, start the push after the action begins, never before.

## 4. Building a scene

Follow the scene contract in `harness/README.md`. Deterministic in (frame, time). Poses on 2s for stop-motion and
paper. Build the world first, then shots, then performance, then sound.

**Look at your own frames before anyone else does:** render one frame per beat
(`node harness/render.cjs <scene> --w 640 --h 360 --start f --end f+1 --jpg`), tile them, inspect them, fix, repeat.

## 5. Sound

- Music: `sampler.py` over VSCO-2 CE (real orchestral samples). Each character has an instrument voice
  (Peter-and-the-Wolf casting) when characters do not speak.
- Effects: BigSoundBank field recordings. Bound every effect with `length=`; long files otherwise play for minutes.
- Narration: the voice lane (`harness/voice/narrate.py`, `.github/workflows/voice.yml`). One job file per film
  (`voice/jobs/<film>.json`): each line has text, start, window end, tone, target pace. ≥4 takes per line; the checker
  rejects repeated/missing/extra words, pace outside the target, unwanted pauses, takes that do not fit the window,
  and voice drift. Then the Ears judge listens to the assembled track.
- Mix: duck music under the narrator, −14 LUFS integrated, −1.5 dBFS ceiling (limit, then trim).

## 6. The review loop (nothing reaches Sam before it passes)

1. Contact sheets: one tile per ~4 s plus every shot's first and last frame, plus a key-moments sheet (each beat's
   cause and effect).
2. Eyes: `python3 harness/review/judge.py eyes films/<id>/STORY.md sheets/*.jpg --out review.json` (two vision
   judges, different providers; blockers need agreement or a critical rating). `KF_BUDGET=free|low|best` picks the
   judges' price tier (free while building); free judges fall back to schema-in-prompt JSON and retry on rate limits.
3. Ears: `python3 harness/review/judge.py ears voice/jobs/<id>.json narration.wav`.
4. Motion: `harness/motion/check.py` on every character performance.
5. Route each finding to the step that caused it, fix, re-render only what changed, re-judge. Log every pass in
   `REVIEW.md` (pass number, findings, fixes). After 3 loops on the same finding, ask Sam one precise question.
6. Verify at full size what a sheet cannot show (small props, hands, faces).

## 7. Rendering

- Tests and prototypes: GitHub Actions. Push a queue file: `render/queue/<name>.json` →
  `{"scenes":[{"scene":"<dir>","parts":24,"frames":<n>}],"w":1920,"h":1080,"fps":24}`. Results go to the `gallery` release.
- Finals: Sam's Mac (Blender with Metal, Chromium for web styles), through the Mac helper. Until it is installed, give
  Sam one command with a copy button, nothing else.
- Never babysit renders with expensive polling: wait long, check once.

## 8. Talking to Sam

- One thing at a time. Say what it is, why (one clause), and the exact steps, numbered, each a single action.
- Lead with results. No jargon (say "the narrator", not "TTS"; "the studio's machines", not "runners").
- When something cannot be done, say so plainly and give the best alternative.
- Never claim something works until it has been checked.

## 9. When things fail

- A tool or model fails: read the log first (`logs`/`voice` releases), fix the cause, re-run only what failed.
- A render looks wrong: find the cause in the scene logic, not a cosmetic patch.
- A judge flags something you disagree with: verify at full size; if it is a sampling artefact, record why in REVIEW.md.
