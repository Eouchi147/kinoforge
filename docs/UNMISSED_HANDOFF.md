# KINOFORGE → Unmissed: video production handoff

Two Claude chats work for Sam. **This one (KINOFORGE, "Video production")** builds and runs the video studio.
**The Unmissed chat** owns the agency: offer, pricing, positioning, sales. This page is how they stay in sync.
Updated by the KINOFORGE chat; the Unmissed chat should read it before planning anything that involves video.

## Decision (Sam, 15 Oct 2026)
Focus the studio on what makes money: premium short video ads for Unmissed clients. Films and channels wait until revenue comes in.
Path: (1) 4–5 portfolio ads this week → (2) studio "Build" button runs the ad factory with Sam approving stills on his phone →
(3) first 2–3 clients through Unmissed → (4) films later.

## What the studio delivers (target, once the current tests pass)
- 15–30 s premium ads, 16:9 master + 9:16 social cut, voiceover, original score, brand end card (logo and text set in code, never AI-drawn).
- Looks (15 Oct, after Sam rejected the stylised cartoon look): **Hero Close-ups** (photoreal product and food, no people), **Freeze Frame**
  (high-speed studio), **Flash Editorial** (hard-flash on colour, social), **Documentary** (people, riskiest), and two built in code with no AI fees:
  **Type in Motion** (kinetic typography) and **Screen Story** (product UI on a phone; the look for Unmissed's own ad).
- Rule: a style board of stills first; Sam picks the look before any video money is spent.
- Human checkpoints: Sam picks the look from a style board, then approves the stills, before any video money is spent.
- Production cost (AI fees): roughly $3–10 per ad at draft/standard quality, up to ~$15 premium. Turnaround target: same day to 48 h.
- Status today: pipeline in testing (first piece: Smart Mount ad, in progress). Expect the first portfolio pieces within days, not hours.

## 16 Oct 2026: KINOFORGE read the new Unmissed offer (site config of 15 Oct)
Applied in `harness/shots/policies/unmissed.md`: three plans (Presence, AI Front Desk, Complete), phone answering live,
tagline "A premium presence. An AI front desk.", the night theme and glass ring, the retired items (founding offer, free proof
build, pay after, December launch). The Unmissed brand ad v1 (`ads/unmissed-01`) follows the site's hero line and hero chips.

### Questions for the Unmissed chat (Sam relays the answers)
1. **Where does video sit in the new offer?** The old answer (one 15 to 30 s ad a month in the core plan, a free 15 s concept
   ad for warm prospects) predates the new plans, and the free proof build is now retired. Options: a short ad inside Presence
   or Complete (for example one a month in place of some social posts), a paid add-on, or only Unmissed's own marketing.
   Our cost per ad: built in code about $0.10 to $0.50; with AI footage about $3 to $10.
2. **Concept ads for prospects:** still made (shown in a call, not handed over), or stopped?
3. **Domain:** `docs/brand/socials.md` names getunmissed.com. Is it live, so end cards can show it?
4. **Ads in the night theme by default?** KINOFORGE assumed yes, to match the site's hero.

## What the KINOFORGE chat needed from the Unmissed chat (answered 15 Oct, see below)
1. How video fits the single productized offer: included deliverable, tiered add-on, or the lead magnet (e.g. a free 15 s concept ad as the outreach hook).
2. The 3 industries / ICP to build concept ads for. Current proposal: Toronto real estate, restaurants, health & beauty clinics (plus Smart Mount as the home-services case).
3. Unmissed brand basics for the Unmissed brand film: positioning line, tagline, colours, logo file, tone.
4. Which claims are allowed in client-facing pieces (no invented testimonials or numbers).

## Rules both chats keep
- Concept ads use invented brands, Sam's own brands, or clients who agreed. Label portfolio pieces "concept".
- Realistic AI content gets the platform AI label (YouTube, Meta, TikTok).
- Nothing published or sent to a client without Sam's approval.

## Where things are
- Finished pieces: GitHub release `pieces` in Eouchi147/kinoforge, and sent to Sam in chat.
- How the ad factory works: `harness/shots/factory.py`, engines menu `docs/ENGINES.md`, directions `harness/shots/directions/`.

## Applied from the Unmissed chat's answers (15 Oct 2026)
- Policy file `harness/shots/policies/unmissed.md`: claims allowed/banned, industries (restaurants and caterers without alcohol or pork,
  auto repair and detailing, non-medical barbers and beauty; no clinics; real estate later), modest wardrobe, no dashes or "...",
  no prices, no URL, AI label, Sam approves everything. The director reads it for every piece with `"policy": "unmissed"`.
- Code guard on every spoken and written word: dashes and ellipses removed; lines with banned claims, prices, URLs, ratings or counts dropped.
- Unmissed end card drawn in code: ink background, ring-and-node logo (#2f7df6 ring, #79b4ff node), Instrument Sans, tagline and second line, no URL.
- Concept ads carry "Concept by Unmissed, AI-assisted" in the corner for the whole piece and on the end card.
- Budget: standard tier capped at US$10 AI fees per ad; premium only when the client pays.
- Smart Mount: cleared by Sam (15 Oct) for public use, including as Unmissed portfolio.
- 15 Oct: the first concept ads (cartoon look) were rejected by Sam; the looks were redone (see the looks in `AGENTS.md`).

## Client material: private storage (PARKED by Sam on 15 Oct until there are paying clients; speed first)
The public kinoforge repo and its releases are for invented-business concepts and studio code only.
Plan: a private repo (e.g. `Eouchi147/unmissed-productions`) holds client briefs, uploads and finished ads; its own workflow
checks out the public studio code and runs the same factory; outputs go to that private repo's releases. Sam's steps when needed:
create the private repo, add the OPENROUTER_API_KEY secret there. Private-repo runs use the account's monthly Actions minutes
(about 30-60 minutes per ad, mostly waiting on the video models).
