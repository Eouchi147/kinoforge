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
- Nothing. All five Unmissed directions are rendered (release `ads`) and on the private Claude page "Unmissed Ad Directions" (https://claude.ai/artifact/6zvTkrN7mpTTCQZc3i99bN).

## Waiting on Sam
- Pick one or two of the five Unmissed directions (page "Unmissed Ad Directions"): v1 Manifesto (kinetic type, 16 s),
  v2 The Catch (3D ring, 18 s), v3 The Call (real call + captions, 27 s), v4 Night Shift (cinematic footage, 23 s),
  v5 Bento (bright tiles, 18 s). `unmissed-01` v4 was rejected ("really bad quality").
- The Unmissed chat should decide where video sits in the new offer (see `docs/UNMISSED_HANDOFF.md`).

## Next (in order)
1. Polish the chosen direction (sound balance: the listening checks flagged weak ducking in v1 and quiet interface sounds in v4), then its 9:16 phone layout and a French version if wanted.
2. A 9:16 version of the Unmissed ad laid out for phones (not a blurred-fill crop).
3. Restaurant portfolio ad: Type in Motion as the spine, Hero Close-ups and the good Freeze Frame clip as inserts,
   a Flash Editorial 9:16 social cut. Budget under $5.
4. Detailing and barber ads in the same system; Smart Mount ad redone in the new looks.
5. Wire the web studio's Build button to `board.yml`, `codead.yml` and `piece.yml` with a phone approval step.

## Money (OpenRouter build key, $50 limit)
- Key usage read $35.03 at 04:21 UTC on 16 Oct (before the Night Shift footage). Earlier per-run records had undercounted by about $4.
- This round (five directions): prep about $0.30, Night Shift stills $0.45 and clips $1.60, listening checks about $0.05. About $2.40.
- About $12 to $13 left. The key's usage figure updates late; read it before a run.
- Web studio key (Vercel): $5 limit, about $2 used.
