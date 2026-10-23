# Keeping the record (LOG, STATUS, MEMORY and the rest)

The repo is the only memory every agent shares; chat history and a model's habits do not carry over. If it matters, it
is in the right file the same day, in the same commit as the change. This page is the short form of `docs/MEMORY.md`.

## Inputs
- Your change, its evidence (run ids, asset names, numbers), its cost, and any verdict of Sam (verbatim, dated).

## Exact steps (every change)
1. Before: `git pull --rebase --autostash origin main`; read `docs/STATUS.md` and the top day of `docs/LOG.md`.
2. Do one thing (one film folder, one engine change, one doc).
3. `bash tools/verify.sh` (`--full` for engines, the director, the harness or tools).
4. Write it down in the same commit:
   - `docs/LOG.md`: one line under today's `## <day> <Mon> <year>` heading (UTC, newest day first): what changed, why,
     the cost ("US$0"), run ids. Append-only: never rewrite an old line; add a correcting line.
   - `docs/STATUS.md`: rewrite the section the change affects (now: running, done, waiting on Sam, next, money). Newest
     section first; remove what is no longer true.
   - The film's `NOTES.md` for film work (scene list, shot reasons, measured seconds per frame, weak spots, run ids).
     A builder working inside one film folder may log there instead of `docs/LOG.md`.
   - The playbook, `docs/WORKFLOWS.md` or this manual if the process changed; `docs/LESSONS.md` if you hit a trap (one
     line, phrased as a rule; if code can check it, add the check to `tools/verify.py`).
   - A decision record in `docs/decisions/NNNN-*.md` if Sam decided something structural (never edit an old one;
     supersede it).
   - `docs/SOUL.md` section 3 and, for craft, `films/director/CRAFT.md` when Sam gives a verdict (his words, dated).
   - `tools/catalog.py` tables when a film is rendered, delivered or judged; then `python3 tools/catalog.py`.
5. `git add <your files only>` (never `-A`), commit with the session's trailer lines, `git pull --rebase --autostash
   origin main`, `git push`. Never force-push.
6. Report with evidence and weak spots.

## Which file holds what
| File | Holds | Rule |
| --- | --- | --- |
| `AGENTS.md` | Entry point, read order, non-negotiables, map | Short; a map |
| `docs/SOUL.md` | Taste: quality bar, Sam's verdicts, house styles, rejected work, how to decide | Sam's words, dated |
| `docs/STATUS.md` | Now | Rewrite freely |
| `docs/LOG.md` | History, one dated line per change | Append-only |
| `docs/decisions/` | Big choices and why | Supersede, never edit |
| `docs/LESSONS.md` | Studio-wide traps | One line each, a rule |
| `films/director/LESSONS.md` | The director's own lessons (newest 40, written by `reflect.py`) | Read by `spec.py` |
| `films/director/CRAFT.md` | Craft rules from Sam's verdicts | Section 9 is enforced by `check.cjs` |
| `docs/PLAYBOOKS/*.md` | One recurring job each, with a definition of done | Change with the process |
| `docs/WORKFLOWS.md` | Every workflow: inputs, outputs, cost, pitfalls | Change with the workflow |
| `docs/manual/` | This AI manual: system, workflows, styles, films, sound | Change with the process; facts from the record only |
| `<film>/NOTES.md` | One film's memory | Written while building |
| Engine `SPEC.md` / `README.md` | The contract of an engine | Code and spec never disagree |
| `studio-web/public/data/catalog.json` | Everything made, for the studio OS | Built by `tools/catalog.py`, never edited by hand |
| `docs/HANDOVER-2026-10-16.md` | Snapshot of 16 Oct | Frozen history |

## Alternatives
None for the shared memory. Private tool memories (Claude memory, Muse Code memory) may hold pointers, never the only copy of a fact.

## Checks before showing Sam
Your LOG line names the evidence; STATUS is true after your change; `bash tools/verify.sh` passes (the docs gate fails
for a missing LOG line).

## Known traps
- Many agents push to `main` all day: pull with rebase before every commit and push.
- The chat container restarts and loses background watchers: anything that must happen later lives on GitHub
  (`chain.yml`, a scheduled task), and its plan is written in STATUS.
- No secrets, no client material, nothing personal about Sam or anyone (the repo is public, decision 0009).
- House style in every file: no em dash, no en dash, no "...".

## Sources of truth
`docs/MEMORY.md`, `AGENTS.md` sections 1 to 5, `tools/verify.py` (gate `docs`), `docs/decisions/0010-memory-and-gates.md`.
