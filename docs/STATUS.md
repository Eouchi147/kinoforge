# Status (updated 16 Oct 2026, 03:45 UTC)

## Focus
Premium short video ads for Unmissed and its clients, to bring in money. Films and channels are parked until then.
Path agreed with Sam on 15 Oct: (1) 4 or 5 portfolio ads, (2) the studio's Build button runs the ad pipeline with Sam
approving on his phone, (3) first 2 or 3 clients through Unmissed, (4) films later.

## Done
- Six business looks defined and shown on a style board (private Claude artifact "Restaurant Ad Looks", round 1 and 2).
  Sam's verdicts are in `AGENTS.md` (The looks). Documentary dropped; Hero Close-ups kept as short food inserts (Claude's call).
- Type in Motion v2 for the invented restaurant "Saffron Hearth Kitchen": real photo cut-outs (bread, tea glasses),
  photo inside the word "fire". Scene: `ads/board/type-motion` (render with `--param fire=... bread=... tea=...`).
- Freeze Frame tested in motion: torn-bread clip good; spice-burst clip warps mid-way (do not use).
- Unmissed ad v1 built in code: `ads/unmissed-01` (night theme and glass ring of the new Unmissed site; scenes follow the
  15 Oct offer: call answered, booked, missed call texted back, review request, premium presence; end card
  "A premium presence. An AI front desk."). 25.6 s, 16:9.
- Pipelines: `codead.yml` (code ads with voice, music, sounds), `board.yml` (stills, cut-outs, short clips), `piece.yml` (AI footage).
- Music fixed: Lyria audio is now requested as a stream (it never worked before).
- Handover docs: `AGENTS.md`, `CLAUDE.md`, `docs/WORKFLOWS.md`, this file, `docs/LOG.md`.

## Running now
- Nothing. Unmissed ad v4 is finished and with Sam (release `ads`: `unmissed-01.mp4`). Four runs cost $0.223 in all.

## Waiting on Sam
- Watch Unmissed ad v4 and say yes or what to change.
- The Unmissed chat should decide where video sits in the new offer (Presence, AI Front Desk, Complete): the free concept
  ad was retired with the free proof build (the free audit is now the only free thing). See `docs/UNMISSED_HANDOFF.md`.

## Next (in order)
1. Sam's notes on `unmissed-01`, then a French version if wanted (the site is bilingual).
2. A 9:16 version of the Unmissed ad laid out for phones (not a blurred-fill crop).
3. Restaurant portfolio ad: Type in Motion as the spine, Hero Close-ups and the good Freeze Frame clip as inserts,
   a Flash Editorial 9:16 social cut. Budget under $5.
4. Detailing and barber ads in the same system; Smart Mount ad redone in the new looks.
5. Wire the web studio's Build button to `board.yml`, `codead.yml` and `piece.yml` with a phone approval step.

## Money (OpenRouter build key, $50 limit)
- About $30.85 used before the Unmissed ad run (key usage read $29.37 before style board round 2, which cost $1.47).
- Of that: about $29 on the first five ad tests in the rejected cartoon look; about $3.10 on the two style-board rounds.
- The key's usage figure updates late; per-call costs in the ledgers are the reliable figure.
- Web studio key (Vercel): $5 limit, about $2 used.
