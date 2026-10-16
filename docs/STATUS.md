# Status (updated 16 Oct 2026, 21:10 UTC)

## Handover
On 16 Oct Sam moved all building into one new Claude chat, project "Unmissed with studio". KINOFORGE becomes the content
engine inside Unmissed; Sam's approval is the only human step. **Start with `docs/HANDOVER-2026-10-16.md`**: snapshot,
what works, how to start a job, costs per content type, money, decisions, open problems, recommendation.

## Focus
Premium short video ads for Unmissed and its clients, to bring in money. Films and channels are parked. New since 16 Oct:
the **social lane** (`social/`, workflow `social.yml`) for Unmissed's Social Autopilot (12 short videos a month per
client on TikTok, Reels, Shorts, Facebook Reels); first client Smart Mount (Toronto opening in December).

## Done
- **Social lane built (16 Oct, not yet run on GitHub):** three 9:16 templates from the same brief (Smart Mount card
  tip-height, real photo `rattan.webp`): A `card-motion` (Smart Mount's own card brought to life, 12.4 s), B `bento`
  (Unmissed's Bento language in Smart Mount colours, 14.4 s), C `type-motion` (kinetic type over the real photo, 13.6 s).
  Every word, number, URL and logo mark stays inside rule R-2-08's safe box (x 0.11 to 0.78, y 0.15 to 0.65 of the frame;
  one constant, `SAFE` in `social/lib/brief.mjs`), checked on every frame by `social/lib/safecheck.mjs` for the 3 samples
  and all 12 batch videos under each look. Captions per platform built in code (`social/lib/captions.mjs`), the hook on
  the first line. First batch `social/batches/smartmount/2026-12/batch.json`: 12 videos (6 tips, 6 teach cards, English;
  bodies of v07, v10, v11 corrected on 16 Oct), in a mix of the three looks, as Sam asked on 16 Oct (four videos each,
  alternating in posting order: B for v01, v05, v08, v12; A for v02, v04, v06, v10; C for v03, v07, v09, v11). Posting gate: nothing posted before Sam approves
  the batch, and nothing for Smart Mount while smartmount.ca is parked. Style board rendered locally (key frames, contact sheets,
  540x960 check videos) and handed to the main chat for Sam (not in the repo; any local render recreates it, see
  `social/README.md`). `fitStage()` in `ads/lib/motion.js` now scales uniformly (a 9:16 stage no
  longer stretches); every existing ad renders exactly as before (40 stills compared).
- Six business looks shown on style boards (private Claude page "Restaurant Ad Looks"); verdicts in `AGENTS.md`.
- Five Unmissed ad directions built music first and rendered (`ads/unmissed-v1` to `-v5`, release `ads`, page
  "Unmissed Ad Directions"). Sam's verdicts (16 Oct): **Bento (v5) loved, the chosen direction**; The Call (v3) loved but
  the voice too fake; The Catch (v2) and Manifesto (v1) "a little"; Night Shift (v4) a big no.
- Pipelines: `codead.yml` (code ads, prep and render), `board.yml` (stills, cut-outs, short clips), `piece.yml` (AI footage).
- Handover saved: private pilot code, web studio clips and working scripts copied to Sam's Mac
  (`Video Production/kinoforge-handover-2026-10-16/`); sources of the review pages in `docs/pages/`.

## Running now
- Nothing. No Actions run, no paid call, no agent.

## Waiting on Sam
- **Smart Mount's December videos:** look decided on 16 Oct (a mix of A, B and C, four each). Waiting on: music (one
  AI instrumental clip for the batch, about $0.04 to $0.08, cap $0.20, or silent; Unmissed's gate S6 says no music we do
  not hold a licence for until it is settled), then Sam approves every video before it is posted. Posting also waits for
  smartmount.ca to come back (parked since 13 Oct until the business is registered).
- How to get natural voices (paid audition of other voice models, a human voice, or a mix); whether The Call's AI
  receptionist must sound like Unmissed's live phone agent.
- Bento next steps (new voice, polish, 9:16 layout, French).
- Where production runs (GitHub terms and the runner-minute limit; see the handover, section g).
- The four Unmissed questions in `docs/UNMISSED_HANDOFF.md`.

## Next (in order, for the new chat)
0. Social lane: on `main` since 16 Oct, looks set in the batch. Once Sam answers on music, dispatch `social.yml` with
   `batch=smartmount/2026-12` and `only=v01-tip-height,v02-teach-arc,v03-tip-studs` (one video per look, about 15 runner
   minutes: the last 30 days hold about 2,550, the cap is 3,000); check the release `social`; the other nine after 1 Nov.
1. Natural voices, then Bento polish, its 9:16 layout and a French version.
2. Job contract between Unmissed's admin and the engine (dispatch, signed callbacks, private outputs).
3. Bento as a brief-driven template, so a client ad needs no coding session.
4. Production compute and client storage moved to private homes before the first client job.

## Money (OpenRouter)
- Build key ($50 limit, GitHub secret): last read $35.03 on 16 Oct about 04:33 (lags); about $2.40 came after it.
  Estimated $12 to $13 left. Sum of all ledgers: $36.29.
- Studio key ($5 limit, Vercel): $4.91 used, $0.09 left (read 16 Oct 17:22).
- The social lane cost nothing so far (built and checked locally, no paid call). Its only paid call is the optional batch
  music (Lyria), booked against the batch's cap when `social.yml` runs.
