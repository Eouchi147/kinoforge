# 0013 Capped paid films with quality gates (supersedes 0001)

- **Date:** 22 Oct 2026, 20:50 Toronto. **Decided by:** Sam, in the main chat: "if completely free is weak, then I want you
  to be cost effective and cap the budget per film but I need good results every time I pay. Try using the best tools for
  the job so I can start using the studio directly."
- **Context:** Under 0001 (spend nothing) the free director got through script and sound but its picture spec failed the
  checks (19 errors) and repairs were starved by the free tier's 1,000 requests a day; few capable free models exist.
- **Decision:** Paid models are allowed again, inside a hard cap per film (default US$2.00, a brief may set 0.50 to 5.00),
  booked before every call. Best tool per stage, chosen by role; free tools wherever they are as good (rendering on GitHub
  runners or the Mac lane, the procedural score engine). Quality gates before each paid stage (fact check before sound;
  spec checks and the eyes score before any render); a film that cannot pass inside its cap stops with a clear message and
  is not rendered. Free mode stays available (`free_only: true` in `films/director/config.json`).
- **Not covered:** paid image or video generation (style boards, AI footage) still needs Sam's go per job (0008).
- **Consequences:** Sam adds credit to the two OpenRouter keys (studio key on Vercel, build key on GitHub); agents never
  handle keys. The first paid film is run and checked by the lead before Sam uses the studio himself.
- **Status:** Active. Supersedes 0001; amends 0005 (the director's default is the capped paid mode).
