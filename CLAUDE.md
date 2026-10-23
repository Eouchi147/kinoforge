@AGENTS.md

## Claude Code only (everything that matters for every agent is in AGENTS.md above)
- Muse Code, Codex and Cursor never read this file: a rule written only here is lost. Put rules in `AGENTS.md` or `docs/`.
- `gh` GraphQL commands (`gh workflow run`, `gh release download`) are blocked in Claude Code sessions: use `gh api` (REST).
- Builder subagents: give each one folder and the playbook for its job; they run `bash tools/verify.sh` and write their
  `NOTES.md`; the coordinator writes `docs/LOG.md` and `docs/STATUS.md` and pushes.
- The Mac lane and delivery to Sam's Mac need the desktop connection's device tools and computer use
  (`docs/PLAYBOOKS/render-on-the-mac.md`, `deliver-to-sams-mac.md`).
- Commit trailer: the attribution lines from the session's system reminder.
