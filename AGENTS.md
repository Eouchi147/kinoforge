# KINOFORGE: start here (every agent, every session)

KINOFORGE is Sam's AI-run film and video studio: films and ads made in code and with free tools, rendered on free
GitHub runners and Sam's Mac, directed like cinema. Since 16 Oct 2026 it is also the content engine of Unmissed, his AI
marketing agency. Sam (GitHub `Eouchi147`) owns everything and decides. This file is the map; the detail lives in `docs/`.
It is written for any coding agent (Muse Code, Codex, Cursor, Gemini CLI, Claude Code): rely on the files and the
checks below, not on what you think a studio usually does.

## 1. Start of every session (do this before anything else)
1. `git pull --rebase --autostash origin main` (many agents push to `main` all day).
2. `bash tools/verify.sh` (about 1 min, free). If a gate is red on `main`, fixing it comes first (or tell Sam).
3. Read `docs/STATUS.md` (now), the top day of `docs/LOG.md` (latest changes), then the files for your job below.

## 2. Read order
| When | Read |
| --- | --- |
| Always | this file, `docs/STATUS.md`, `docs/SOUL.md` (taste: the quality bar, Sam's verdicts, house styles, how to decide) |
| Before any change | `docs/MEMORY.md` (where things are written down, by whom, when) |
| Your job | the playbook in `docs/PLAYBOOKS/` (one per recurring job, each ends with a definition of done) |
| Film work | `films/director/CRAFT.md` (craft rules from Sam's verdicts), the engine's `SPEC.md` or `README.md`, the film's `NOTES.md` |
| Structural change | `docs/decisions/` (why things are the way they are; do not undo a decision without Sam) |
| Running a pipeline | `docs/WORKFLOWS.md` |
| Anything Unmissed or client | `harness/shots/policies/unmissed.md`, `docs/UNMISSED_HANDOFF.md` |
| History only | `docs/HANDOVER-2026-10-16.md` (snapshot of 16 Oct; older than STATUS and the decision records) |

## 3. Rules that never bend (and the gate that enforces each)
| Rule | Enforced by |
| --- | --- |
| **Money: no paid call without Sam's explicit go.** `docs/decisions/0001` (22 Oct 09:20) says spend nothing; a later repo entry (LOG 23 Oct, `films/director/CRAFT.md`, director `config.json`, commit 49f4b2a) records a capped paid rule from 22 Oct 20:50. Until Sam confirms which stands and a decision record says so, treat money as unconfirmed: free tools only, and ask him before any paid call | caps in code (`cap_usd`, ledgers, `OverBudget`); `films/director/config.json` |
| **Words, logos and numbers are set in code,** never drawn by an image or video model; AI prompts say "no text, no logos" | gates `text`, `prompts` |
| **House style for words on screen and in narration:** no em dash, no en dash, no "..." | gate `text`; director code guards; Kinetic compiler |
| **Honesty.** Facts checked with sources; Unmissed and client claims only in their own written words; demos say so on screen; AI content labelled where platforms ask (`docs/decisions/0012`) | director checker seat; your review |
| **Public repo.** No secrets, no client material, nothing personal about Sam or anyone (`docs/decisions/0009`) | gate `secrets`; your own diff review |
| **Never handle API keys.** Sam adds them as GitHub or Vercel secrets himself | gate `secrets` |
| **Sam approves** every look before production and everything before it is published or sent | playbooks |
| **Heavy work runs on GitHub runners** (or the Mac lane), never in a chat session | `docs/decisions/0002` |
| **Write it down:** every change adds a dated line to `docs/LOG.md` and updates `docs/STATUS.md` in the same commit or push | gate `docs` |
| **Craft:** every cut, move, effect and label has a written job; real-time moves; living worlds; no emoji or cartoon icons | `scenes.mjs`, `check.cjs` (CRAFT.md section 9) |

## 4. How to work
- **One thing at a time.** One film folder, one engine change or one doc per task. Do not touch another film's folder.
- **Verify before you claim.** Never write "done", "rendered", "fixed" or "delivered" without evidence you produced in this
  session: a passing `bash tools/verify.sh`, a run id with `success`, the asset listed in the release, numbers from
  ffprobe, a contact sheet you actually looked at. If you could not check something (for example you cannot open
  images), say so plainly.
- **Commit small, then push:** `bash tools/verify.sh`, `git add <your files only>`, commit, `git pull --rebase --autostash
  origin main`, `git push`. Never `git add -A` (other agents' work sits in the same tree); never force-push. Agents that
  only commit when asked (Muse Code) should be asked to commit and push as part of the task.
- **Gates fail loudly on purpose.** Read the "how to fix" line and fix the cause. An exception goes in
  `tools/verify-allow.txt` only for frozen legacy work or machine-written files, with the reason.
- **When unsure, ask Sam** (one short question, your recommendation first) if it costs money, publishes, touches a
  client, changes a rule or contradicts a verdict. Otherwise decide, write the reason down, and say so. He wants very few,
  very small decisions, results and numbers first; he reads on his phone.
- **Double-check before presenting.** If something does not make sense, fix it or say so. Name the weak spots of every delivery.

## 5. Definition of done (every task)
- `bash tools/verify.sh` passes (`--full` if you touched `films/lib/`, `films/director/`, `harness/` or `tools/`).
- The playbook's own definition of done is met, with evidence.
- `docs/LOG.md` has your dated line (what, why, cost, run ids); `docs/STATUS.md` is true; the playbook,
  `docs/WORKFLOWS.md`, a decision record or `docs/LESSONS.md` are updated if the process, a decision or a trap changed.
- Committed and pushed; CI `verify` green for your push.

## 6. Verify
`bash tools/verify.sh` runs the fast gates: secrets, json, syntax (Python and JS), workflows, text, prompts, battlemap
(scene plan of every Battle Map film), social (batch checks and tests), director (unit tests), docs (memory freshness).
`bash tools/verify.sh --full` adds the director tests in Chromium, `films/director/check.cjs` on every Battle Map film,
and the score selftest (needs `cd harness && npm ci && npx playwright install chromium`, plus `pip install numpy scipy
soundfile librosa pillow` and ffmpeg). CI: `.github/workflows/verify.yml` (every push), `verify-engine.yml` (engine changes).

## 7. Where things are
| Path | What |
| --- | --- |
| `docs/` | The system of record: `SOUL`, `MEMORY`, `STATUS`, `LOG`, `LESSONS`, `decisions/`, `PLAYBOOKS/`, `WORKFLOWS`, `research/` |
| `films/battles/<id>/` | Battle Map films (spec-driven, `spec.js` on `films/lib/battlemap/`); reference: `cannae` |
| `films/dark-corners/<id>/` | Dark Corners episodes, hand-built (Kinetic, Lantern Road, Clay) |
| `films/cutaway/`, `films/styles/cutaway/` | Cutaway productions and the Cutaway kit and looks (Blender); `films/lib/cutaway/` the spec-driven line (in progress) |
| `films/noor/` | NOOR Ramadan samples (Lantern Road; strict depiction rules in `docs/SOUL.md`) |
| `films/studio/<id>/` | Director jobs (`brief.json`, `status.json`, outputs) |
| `films/director/` | The free director pipeline (`README.md`, `DESIGN.md`, `CRAFT.md`, `LESSONS.md`, `SLATE.md`, tests) |
| `films/lib/` | Engines: `battlemap/`, `kinetic/`, `score/` (free music), `battle_mix.py` |
| `harness/` | Renderers (`render.cjs` canvas/WebGL, `dom-render.cjs` HTML, `blender_render.py`), `mac/` lane, `shots/` ad pipelines |
| `ads/`, `social/`, `boards/`, `pieces/` | Business ads in code, phone-format social videos, style boards, AI-footage pieces (paused) |
| `proto/` | The 14 anthology style prototypes (the house styles' origins) |
| `studio-web/` | The web studio on Vercel (director chat, films library) |
| `tools/verify.sh` | Every gate in one command; exceptions in `tools/verify-allow.txt` |
| `Eouchi147/rc-render` | Second public repo: render farm workflows `films.yml`, `stills.yml`, `remux.yml`, `chain.yml` (release `kino-films`) |

## 8. Accounts (Sam owns them; agents never see keys)
GitHub `Eouchi147/kinoforge` and `Eouchi147/rc-render`, both public (free Actions). Releases: `films` and `stills`,
`kino-films`, `film-logs` (rc-render), `ads`, `boards`, `pieces`, `social`, `gallery`, `voice`, `logs`. Secret
`OPENROUTER_API_KEY` (free models only now). Vercel project `kinoforge-studio` (redeploys on every push to `main`).
Unmissed site repo `Eouchi147/sovereign-studio` (private; its `site.config.js` is the source of every Unmissed claim).
Sam sees work as GitHub release links, files on his Mac (`Video Production/kino-films/`), and Claude pages.
