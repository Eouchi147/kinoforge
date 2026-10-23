# 0005 The director runs on free seats and free sound by default

- **Date:** 22 Oct 2026. **Decided by:** Sam (spend nothing; films about any subject from a conversation).
- **Context:** The director pipeline (`films/director/`, `film.yml`) was designed with paid seats (head, deputy, crew) and
  paid sound (ElevenLabs, Lyria).
- **Decision:** Free-only by default: curated free OpenRouter models per role (`config.json` `free_seats`), a checker seat
  from a different model than the writer, Chatterbox or Kokoro narration checked by Whisper, the free score engine.
  Two production lines are spec-driven and need no hand coding: `battle-map` and `kinetic` (`lines.json`).
- **Consequences:** Script and sound work on free models; the picture spec is the weak stage (first live run: 19 check
  errors, repairs starved by the 1,000 requests a day limit). One job at a time. Lantern Road and Clay stay hand-built.
  `films/director/DESIGN.md`'s money section describes the old paid design.
- **Status:** Active. Playbook: `docs/PLAYBOOKS/run-the-free-director.md`.

- **Amended** by 0013: the director's default is the capped paid mode; free mode stays available.
