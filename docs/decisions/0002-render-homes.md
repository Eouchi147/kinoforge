# 0002 Render homes: free GitHub runners plus the Mac lane

- **Date:** 21 to 22 Oct 2026. **Decided by:** Sam (render on GitHub runners and his Mac), built by Claude.
- **Context:** Rendering films in the chat container overloads its 2 cores and dies with the session. Films need hours of
  CPU. GitHub-hosted runners are free for public repos; Sam's MacBook (M4, Blender installed) renders Blender films about
  7 times faster than one runner.
- **Decision:**
  - Hand-built films and inserts: rc-render `films.yml` (parallel parts, join, the film's own sound, release `kino-films`);
    check stills: rc-render `stills.yml` (release `stills`); new sound on a finished film: rc-render `remux.yml`;
    renders that wait on other renders: rc-render `chain.yml` (every 15 min).
  - Director films: kinoforge `film.yml` then `films-render.yml` (release `films`). Narration and score: kinoforge
    `sound.yml`, `noor-sound.yml`.
  - Blender films when the Mac is connected: the Mac lane (`harness/mac/go.py` job watcher inside Blender, Metal GPU).
- **Consequences:** No chat session has to stay alive for a render. Runner minutes are shared: one stills run in flight
  per builder. GitHub's terms for hosted runners are a grey area for client production work (`docs/HANDOVER-2026-10-16.md`
  section g): client jobs need another home before they start. The Mac lane works only through Sam's Claude desktop
  connection; other agents cannot use it.
- **Status:** Active. Playbooks: `docs/PLAYBOOKS/render-on-github.md`, `render-on-the-mac.md`.
