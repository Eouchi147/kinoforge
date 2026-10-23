# 0001 Spend nothing: free models and free tools only

- **Date:** 22 Oct 2026, 09:20 Toronto. **Decided by:** Sam ("spend nothing").
- **Context:** The OpenRouter build key (US$50) was nearly used up by tests (about US$1.2 estimated left on 22 Oct); the
  studio key (US$5) was empty. A paid director test job (battle-of-tours) was running.
- **Decision:** No paid call of any kind. Text seats use OpenRouter models whose id ends in `:free`; narration uses free
  open voices on the runner (Chatterbox, MIT; Kokoro, Apache 2.0); music uses the free procedural score engine; pictures
  are made in code (web or Blender) and rendered on free runners or Sam's Mac.
- **Enforced in code:** `films/director/config.json` `free_only: true`; a paid model id raises `PaidRefused`; any call that
  reports a cost stops the job (`OverBudget`). Only Sam turns it off.
- **Consequences:** The paid lanes (`board.yml`, `piece.yml`, Lyria and ElevenLabs in `codead.yml` prep) are not used.
  Free models are rate-limited (1,000 requests a day per key; few capable ones): run one director job at a time. The
  handover's money section (16 Oct) is history, not the rule.
- **Status:** Superseded by 0013 (Sam, 22 Oct 20:50 Toronto).

