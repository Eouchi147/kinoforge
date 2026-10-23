# Research: making this repo agent-proof (23 Oct 2026)

Question (Sam, 22 Oct 20:24 Toronto): any AI agent working on KINOFORGE from GitHub (he uses Meta's Muse Code these days)
must take over and produce the same quality, by relying on the build rather than on the model at hand.
What follows is what was found, with sources, and what this repo does about it. "Unknown" means not found.

## 1. Which file each agent reads

| Agent | Reads at start | Notes | Source |
| --- | --- | --- | --- |
| Muse Code (Meta, terminal agent) | `AGENTS.md`, else `CLAUDE.md`, else `.agents/AGENTS.md`, else `.claude/CLAUDE.md`, at each level from the workspace up to the `.git` root; the first existing file wins per level, the deeper file wins | Project rules load only after the user trusts the workspace. Committed project memory: `.agents/memory/` with a `MEMORY.md` index (up to 48 files listed, read on demand), loaded even when untrusted. Skills: `.agents/skills/<id>/SKILL.md`. Hooks: `.muse/hooks.json`. Will not commit or push unless asked in the session. A "verification observer" checks that the agent ran the work it claims. `muse exec` exit code says how the run ended, not whether the work is correct: "gate on your own test command" | [Meta: configuration](https://dev.meta.ai/docs/muse-code/configuration), [Meta: extending](https://dev.meta.ai/docs/muse-code/extending), [Meta: overview](https://dev.meta.ai/docs/muse-code) |
| OpenAI Codex | `AGENTS.override.md` or `AGENTS.md`, one per directory from the project root down to the working directory, joined in order | Stops adding files at 32 KiB in total (`project_doc_max_bytes`) | [OpenAI: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| Claude Code | `CLAUDE.md`, not `AGENTS.md` | Official advice: a `CLAUDE.md` that imports `@AGENTS.md`, plus Claude-only notes. Target under 200 lines; instructions are context, not enforcement: "write it as a hook" when it must happen | [Anthropic: memory](https://code.claude.com/docs/en/memory) |
| Gemini CLI | `GEMINI.md` by default | `context.fileName` in `.gemini/settings.json` can list `AGENTS.md` | [Gemini CLI: GEMINI.md](https://www.geminicli.com/docs/cli/gemini-md) |
| Cursor | `AGENTS.md` at the root (plain markdown), plus `.cursor/rules/*.mdc` | | [Cursor: rules](https://docs.cursor.com/context/rules) |

Muse Code's launch date: Meta's pages do not give one (first version 0.1.0 in the changelog). A third-party preview
article dates the announcement to 5 Aug 2026 and calls itself unverified. Which model version runs it: unknown here.
The page agents.md itself could not be fetched from this session (blocked).

**Decision for this repo:** `AGENTS.md` at the root is the one entry point (every agent above reads it, Gemini through a
two-line `.gemini/settings.json`). `CLAUDE.md` imports it. Muse never reads `CLAUDE.md` while `AGENTS.md` exists, so
nothing important may live only in `CLAUDE.md`. `.agents/memory/MEMORY.md` exists only as an index into `docs/`, so
Muse's committed memory points at the same files instead of growing a second memory. `AGENTS.md` stays short (Codex
stops at 32 KiB; Claude Code advises under 200 lines; OpenAI's own repo uses about 100 lines).

## 2. What keeps quality from drifting between models

1. **A map, not an encyclopedia.** OpenAI's Codex team keeps `AGENTS.md` at about 100 lines as a table of contents and
   treats a structured `docs/` folder as the system of record, with plans and decision logs checked in.
   [OpenAI: harness engineering](https://openai.com/index/harness-engineering)
2. **Rules in code, with the fix in the error message.** Same source: "we write the error messages to inject remediation
   instructions into agent context"; "Human taste is captured once, then enforced continuously". Anthropic says the same
   from the other side: an instruction file is context, not enforcement; anything that must happen belongs in a hook or a check.
   [Anthropic: memory](https://code.claude.com/docs/en/memory)
3. **Progress file, feature list, init script, one thing at a time, verify before claiming.** Anthropic's long-running
   harness: a progress file plus git history so a fresh agent knows the state; a JSON feature list where agents may only
   flip `passes` (JSON because models overwrite Markdown more readily); an `init.sh` run at the start of every session with a
   basic end-to-end check; one feature per session; a commit and a progress note at the end. Failure modes it fixes:
   declaring victory early, building too much at once and leaving a broken half-state, marking work done without an
   end-to-end test. [Anthropic: effective harnesses for long-running agents](https://anthropic.com/engineering/effective-harnesses-for-long-running-agents)
4. **Specs before code, a constitution of non-negotiables.** Spec-driven development (GitHub Spec Kit): specify, plan,
   tasks, implement, with a `constitution.md` of principles every plan is checked against; "the codebase becomes the
   de-facto specification" when there is none. [Microsoft: Spec Kit](https://devblogs.microsoft.com/blog/spec-driven-development-spec-kit)
5. **Decision records.** Short records of context, decision, consequences, never rewritten, superseded by a new record,
   so a newcomer (or a new model) does not undo a decision whose reason it cannot see. [Nygard's format, arc42](https://docs.arc42.org/tips/9-5/)
6. **Probe, compose, reflect** (google-research/harness2, assessed on 22 Oct in `films/director/DESIGN.md`): several
   candidates checked in code, the best composed, lessons appended after every job. Already used by the director.
7. **Golden examples and contact sheets.** The director already shows the coder two finished example specs and judges a
   contact sheet with the narration under each still; a frozen fixture keeps the tests honest when the live films change.

## 3. What this repo does with it (23 Oct 2026)

| Finding | Here |
| --- | --- |
| One short entry file every agent reads | `AGENTS.md` (map, read order, non-negotiables, verify, definition of done); `CLAUDE.md` = `@AGENTS.md` + Claude notes |
| Docs as system of record | `docs/SOUL.md` (taste), `docs/MEMORY.md` (how memory works), `docs/STATUS.md` (now), `docs/LOG.md` (history), `docs/decisions/` (records), `docs/PLAYBOOKS/` (one per recurring job, each with a definition of done) |
| Rules as gates with the fix in the message | `bash tools/verify.sh` (`tools/verify.py`); exceptions only in `tools/verify-allow.txt` with a reason; CI `verify.yml` on every push, `verify-engine.yml` on engine changes |
| Init and end-to-end check at session start | `AGENTS.md` step 1: pull, `bash tools/verify.sh`, read STATUS |
| Verify before claiming | Definition of done in `AGENTS.md` and every playbook: a run id with its conclusion, a release asset listed, a contact sheet looked at |
| Small scope | One film folder or one engine per change; the playbooks are one job each |
| Muse never commits unless asked | Playbooks say "commit and push" as an explicit step; Sam's request to an agent should include it |

## 4. Limits (what a build cannot fix)

- Taste. The gates catch broken rules, not a dull film. `docs/SOUL.md` and Sam's verdicts carry taste; only Sam judges it.
- Looking at pictures. An agent that cannot open images cannot do the contact-sheet review; the playbooks say to stop and
  say so instead of claiming the check.
- Sam's Mac and the Mac lane need the Claude desktop connection (device tools, computer use). Other agents cannot reach
  it: they deliver a release link instead.
- Muse Code specifics beyond the pages above (model, limits, how its observers judge) are unknown; the design relies only
  on the common denominator: a root `AGENTS.md`, shell commands, git, and a check script whose exit code is the truth.
