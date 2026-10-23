# 0003 Battle Map engine v2 for every battle film

- **Date:** 22 Oct 2026. **Decided by:** Sam's verdict on the v1 battles; engine by Claude.
- **Context:** Sam: good concept, but emoji-like graphics, no legend, unplanned cameras, armies that clip, the wrong music.
- **Decision:** `films/lib/battlemap/` v2: soldier figures on movement trays with a spacing solver (units meet at a front,
  never pass through), a flat heraldic glyph set (no cartoon icons), a legend panel (sides, unit kinds, lettered places),
  scenes with planned shots and a written reason per cut compiled to camera keys with speed limits, a living world
  (camps, smoke, birds, wind, water). Every battle is re-directed on v2; Cannae is the reference film.
- **Enforced in code:** `node films/lib/battlemap/tools/scenes.mjs <film>` (exit 1 on errors) and
  `films/director/check.cjs` (craft checks from CRAFT.md section 9), both in `tools/verify.sh`.
- **Consequences:** v1 specs still render, but new work uses `scenes`, `legend`, `ambient`. The v1 example used by the
  director tests is frozen in `films/director/tests/fixtures/hastings-v1/`.
- **Status:** Active. Spec: `films/lib/battlemap/SPEC.md`. Playbook: `docs/PLAYBOOKS/make-a-battle-map-film.md`.
