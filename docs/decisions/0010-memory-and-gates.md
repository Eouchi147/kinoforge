# 0010 Memory in the repo, rules as gates in code

- **Date:** 15 to 16 Oct 2026 (Sam: every change keeps STATUS and LOG current so another AI can take over); 22 Oct 20:24
  Toronto (Sam: a soul and memory so any agent, such as Meta's Muse Code, produces the same quality, relying on the build
  rather than the model).
- **Context:** Several AIs and many sub-agents work on the repo. Prose rules drift and get skipped; models differ.
  Research: `docs/research/AGENT_HARNESS_2026-10.md`.
- **Decision:** `AGENTS.md` is the one entry point; `docs/` is the system of record (`SOUL`, `MEMORY`, `STATUS`, `LOG`,
  `decisions/`, `PLAYBOOKS/`, `LESSONS`); every rule that can be checked is a gate in `tools/verify.py`, with the fix in its
  error message, run locally (`bash tools/verify.sh`) and in CI (`verify.yml`, `verify-engine.yml`). Exceptions only in
  `tools/verify-allow.txt`, each with a reason.
- **Consequences:** A red CI run means a rule was broken; fix it before new work. When you add a rule, add its gate (or say
  in `docs/MEMORY.md` why it cannot be checked).
- **Status:** Active.
