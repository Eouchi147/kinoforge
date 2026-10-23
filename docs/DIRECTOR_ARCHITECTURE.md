# The director: architecture

> History (14 Oct 2026): the first paid multi-agent director (`harness/director/`, `director.yml`, never run). The film
> director in use is `films/director/` (`README.md`, `DESIGN.md`); the money rule is in `docs/decisions/`.

One chain of command, two places it runs, hard limits on money and loops.

```
                 Sam
                  │  talks (web studio, Director tab)
                  ▼
   HEAD ── strongest model inside $5/$25 per M tokens (today Claude Opus 5.5)
    │       talks with Sam · plans the film · final review · the only one who decides
    │
    ├── DEPUTY ── strong, half the price (today Claude Sonnet 5.5)
    │              reviews every stage, keeps the best draft, sends it back with concrete fixes
    │
    ├── CREW ──── the smartest models under $0.50/$1 per M (today MiMo v2.6 Pro, Claude Haiku 5.5, GLM 5.3 Flash)
    │              draft in parallel, 3 at a time, so one bad draft never decides the film
    │
    ├── EYES / EARS ── cheap multimodal models: contact sheets, narration (harness/review/judge.py)
    │
    ├── CHECKS ── code, not models: timings, coverage, word counts, causality links, the voice checker,
    │              the motion checker. Free, exact, and they run BEFORE any paid reviewer reads a draft
    │
    └── FREE ──── free models: last resort when every paid seat fails or a cap is reached
```

Seats are filled **live** from OpenRouter's model list (highest published intelligence index within the seat's price
ceiling and abilities, one model per provider so fallbacks fail independently). When a better model ships, it takes the
seat by itself. Seats, ceilings and caps: `studio-web/lib/crew.json`.

## Where it runs

| | Web studio (Vercel) | Build director (GitHub Actions) |
| --- | --- | --- |
| What | the conversation with Sam | pre-production of an approved film |
| Code | `studio-web/lib/agents.js`, `app/api/director` | `harness/director/agents.py`, `showrunner.py`, `.github/workflows/director.yml` |
| Time limit | 110 s per turn (every call has its own timeout) | 60 min per film |
| Key | `OPENROUTER_API_KEY` on Vercel (the studio key) | `OPENROUTER_API_KEY` GitHub secret (a separate build key with its own limit) |

## A conversation turn

1. Money check: the key's remaining balance and today's spend decide which seat leads (head → deputy → crew → free).
2. Opening turn: three crew models pitch in parallel; the head curates the best three.
3. Later turns: the head answers; if fresh material would clearly help it asks the crew once, then answers with the drafts.
4. Every call: own timeout, fallback through the seat's chain, strict JSON schema (or schema-as-instructions for models
   without it), cost booked. A turn may not pass `caps.turn_usd`.

Measured: opening turn 20 s, $0.017 (two crew drafts at $0.0003 each, Opus curating at $0.016).

## Building a film (after "Build it")

The brief is committed to `films/<id>/brief.json`, which starts `director.yml`:

1. **Plan** (head): direction, story spine, style pack, narrator and voice design, a note per stage, risks, acceptance list.
2. **Stages** story → script → shots → sound → style, each:
   crew drafts ×3 → code checks → crew self-fixes what the checks caught (≤2) → deputy picks the best, scores 0-10,
   lists blockers and fixes → crew revises (≤2) → accepted.
3. **Final review** (head): does it all tell one film? Pass, or fixes per stage → only those stages are redone (≤2 loops).
4. Still not passing after the loops: the head writes **one precise question for Sam** (`status.json`). No endless loops.
5. Outputs in `films/<id>/`: `plan.json`, one JSON per stage, `reviews.json`, `PLAN.md` (readable), `status.json`,
   `ledger.json` (every call: seat, model, task, cost, seconds). The narration job goes to `voice/jobs/<id>.json` and
   the voice lane starts by itself.

## Money

- Caps (`crew.json`): per message, per film, per day, plus a reserve below which the head steps down to the deputy.
- A call whose worst case would pass the film cap is refused before it is sent.
- Two OpenRouter keys, each with its own limit: the studio key (conversation) and the build key (GitHub). Neither can
  overspend the other.
- Anthropic and Google heads use prompt caching on the long system prompt.

## Next layers

- Scene build: the crew writes a declarative timeline (beats → shots → poses/cues) that the style pack's engine renders,
  not raw scene code. Engines stay deterministic; models only decide.
- Review of renders: contact sheets → Eyes (two cheap vision models) → deputy → head, same loop limits.
- Jev (TypeSafe AI, early access, not on OpenRouter): a candidate for the CHECKS layer (fast typed classify/score calls),
  not for writing. Revisit when it has public access.
