# How KINOFORGE remembers (read once; follow every time)

The repo is the only memory that every agent shares. Chat history, a tool's private memory and a model's habits do not
carry over to the next agent. So: if it matters, it is in one of the files below, in the right one, the same day.

## The files, and what each one is for

| File | Holds | Who writes it | When | Rule |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | The entry point: what this is, read order, non-negotiables, how to verify, the map | Whoever changes a rule or the layout | Rarely | Short (about 100 to 150 lines). A map, not an encyclopedia |
| `docs/SOUL.md` | Taste and judgement: the quality bar, Sam's verdicts and their lessons, house styles, rejected work, how to decide | Whoever records a new verdict of Sam | After every verdict | Sam's words, dated |
| `docs/STATUS.md` | **Now**: what is running, done, waiting on Sam, next, money | Every agent | Every change that alters the state | Rewrite freely; remove what is no longer true. Newest section first |
| `docs/LOG.md` | **History**: one dated line per change or decision | Every agent | Every change, same commit (or same push) | **Append-only.** Newest day first, `## 23 Oct 2026` headings (UTC). Never rewrite an old line: add a correcting line |
| `docs/decisions/NNNN-*.md` | **Decision records**: the big choices, why, what they rule out | Whoever makes or reverses a big decision (usually from Sam's words) | When the decision is made | Never edit the decision; supersede it with a new record and mark the old one "Superseded by NNNN" |
| `docs/LESSONS.md` | Studio-wide technical and craft lessons (ffmpeg, models, runners, rendering) | Anyone who hit a trap | When you hit it | One line each, phrased as a rule |
| `films/director/LESSONS.md` | The director's own lessons (newest 40) | `films/director/reflect.py` after every job, and people for seed lessons | Every director job | Read by `spec.py` before every draft |
| `films/director/CRAFT.md` | The craft rules for films (cuts, camera, living worlds, graphics, music, checks) | Whoever records a craft verdict of Sam | After a craft verdict | Its section 9 is enforced in `check.cjs` |
| `docs/PLAYBOOKS/*.md` | How to do each recurring job, step by step, with a definition of done | Whoever changes how the job is done | When the process changes | Change the playbook in the same commit as the process |
| `docs/WORKFLOWS.md` | Every GitHub workflow: inputs, outputs, cost, pitfalls | Whoever changes a workflow | Same commit | |
| `<film folder>/NOTES.md` | One film's memory: scene list, shot reasons, weak spots, render cost, check results | The film's builder | While building | A builder working only inside one film folder may log there instead of `docs/LOG.md` |
| Engine `SPEC.md` / `README.md` | The contract of an engine (`films/lib/battlemap/SPEC.md`, `films/lib/kinetic/SPEC.md`, `films/styles/cutaway/README.md`, `films/lib/score/README.md`) | Whoever changes the engine | Same commit | Code and spec never disagree |
| `docs/HANDOVER-2026-10-16.md` | A dated snapshot of 16 Oct (accounts, releases, costs, risks) | Nobody (frozen) | Never | History. Where it disagrees with STATUS or a decision record, they win |
| `docs/research/*.md` | Research notes with sources | The researcher | Once | Dated in the file name |
| `.agents/memory/MEMORY.md` | Only an index into the files above, for Muse Code's committed memory | Whoever adds a file to this table | Rarely | No facts of its own |
| `CLAUDE.md` | `@AGENTS.md` plus Claude Code notes | Claude sessions | Rarely | Never the only home of a rule (Muse and Codex do not read it) |

## The loop for every change

1. **Before:** `git pull --rebase --autostash origin main`, read `docs/STATUS.md`, the top of `docs/LOG.md`, the playbook.
2. **Do one thing** (one film folder, one engine change, one doc). Small commits.
3. **Check:** `bash tools/verify.sh` (and `--full` if you touched an engine, the director or the harness). Fix every FAIL.
4. **Write it down in the same commit:** a line in `docs/LOG.md` (what changed, why, cost), `docs/STATUS.md` if the state
   changed, the playbook or `WORKFLOWS.md` if the process changed, a decision record if a big choice was made, a lesson
   if you hit a trap.
5. **Commit, pull with rebase, push.** Other agents push to `main` all the time; pull often. Never force-push.
6. **Report** with evidence (run ids, asset names, durations, what you looked at), and the weak spots.

## What the gates enforce about memory (`tools/verify.py`, gate `docs`)

- A change set (your unpushed commits plus your working tree, or the commits of a push in CI) that changes code, films or
  workflows must also change `docs/LOG.md`. A builder whose changes stay inside one film or style folder may instead
  update that folder's `NOTES.md`. Files written by machines (ledgers, `status.json`, audio outputs, check output,
  `films/director/LESSONS.md`) are exempt: see `tools/verify-allow.txt`.
- `docs/LOG.md` keeps `## <day> <Mon> <year>` headings, newest first.
- Warnings (not failures): lines removed from the log; `docs/STATUS.md` not updated alongside a log line.
- What the gate cannot see: whether your line is true and useful. Write it so the next agent can act on it.

## Writing style for every memory file

Plain English, short sentences, facts with dates (UTC unless marked) and numbers. Say "unknown" when you do not know.
No em or en dashes, no "..." (house style, also in docs). No secrets, no personal details about Sam or anyone (the repo
is public), no client material.
