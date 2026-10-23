# 0006 Film music from the free procedural score engine

- **Date:** 22 Oct 2026. **Decided by:** Sam's verdict on the battle music plus the spend-nothing rule.
- **Context:** Lyria scores were full orchestral and did not follow the film's structure; Sam wants the warm ambient feel
  of Age of Empires and Anno; paid music is no longer allowed.
- **Decision:** `films/lib/score/`: CC0 VSCO-2 CE samples plus synthesis, four palettes by era and place, deterministic,
  one swell into the turn, mixed at -14 LUFS with the voice about 16 dB over the score. Finished renders get new sound with
  rc-render `remux.yml` instead of a re-render.
- **Enforced in code:** `python3 films/lib/score/selftest.py` (in `tools/verify.sh --full`).
- **Status:** Active. Three 30 s excerpts were sent to Sam on 22 Oct; his verdict on the feel: not recorded yet.
