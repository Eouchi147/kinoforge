# Status (updated 22 Oct 2026, 14:00 UTC)

## NOOR Ramadan samples (22 Oct, started 14:30 UTC)
- Sam asked (Noor Codex chat) for 2 to 3 free sample videos for the NOOR Ramadan 2027 series (series bible: Claude doc "NOOR · Thirty Nights of Light").
- Building in `films/noor/`: `n05-iqra` (The Descent, Night 5), `j30-amma` (Tonight's Juz, Night 30), then a 9:16 short from Iqra. Narration and score: `noor-sound.yml` (free). Picture: Lantern Road engine, rendered by `films-render.yml` (free), release `films`.

## Rework after Sam's verdicts (22 Oct, 09:20 Toronto): in progress
- **Spend nothing.** Free models and free tools only. The paid director test job (battle-of-tours) was cancelled after
  US$0.36. The studio key shows $0 left; the director chat runs on a free model.
- The verdicts and the house rules are in `films/director/CRAFT.md` (read before any film work); lessons in `LESSONS.md`.
- Running (agents, nothing rendered yet):
  - free procedural score engine (`films/lib/score/`): done, the 8 battles re-scored (narration kept); brightening and cue beat grids in progress; Sam to listen to three excerpts;
  - Battle Map engine v2 (no emoji, refined heraldic graphics, legend panel, formations that never overlap, planned camera per scene, living world) with Cannae as the reference film: done (9 scenes, 26 shots, 0 check errors), Cannae v2 rendering on free runners; the other battles are re-directed on v2 (Hastings, Waterloo, Thermopylae, Gaugamela, Hattin, Ain Jalut rendering; Agincourt waits for its two Cutaway inserts);
  - Kleidion re-directed (done: 9 scenes, 29 shots instead of 64, opening in real time, fuller worlds); re-rendering on free runners (rc-render films.yml, 16 parts);
  - Arabia re-directed (done: pin-hole star sky in its own no-blur pass, 31 shots in 9 scenes instead of 49, fuller camp, cut-paper cards); rendering on free runners (24 parts, Blender, about 1 to 2 hours);
  - Bamberg polished (done: eight movements, every effect with a job); re-rendering now on free runners (rc-render run 39790691570);
  - director pipeline: done and free-only by default; first live jobs running: `films/studio/salamis/` and `films/studio/great-emu-war/` (watch their status.json).
  - new style **Cutaway** (Sam, 10:11): Blender kit and a four-look style board in `films/styles/cutaway/`, nothing rendered on runners yet. Sam (10:16) wants all four uses built: briefs in `films/cutaway/` (sample trade ad, Why Venice Sinks, Agincourt mud inserts, seasons loop); the kit's first usable version landed (516ec0b); four builders are on them now.
- Next: re-render on GitHub runners (free), new stories through the free director, one render home for the studio.

## Web studio (22 Oct, studio-web/)
- Reworked: `/api/media` streams release assets (allow-list: rc-render `kino-films`, kinoforge `films` and `gallery`; Range forwarded, no token) so previews play and seek; the old pilot clips in `studio-web/public/media/` are now committed (`.gitignore` exception) and deploy.
- Films page lists the 12 `kino-films` films (posters in `public/posters/`) plus anything in kinoforge release `films` (live, cached 60 s), 16:9 and 9:16 players, download link to the full file on GitHub.
- Director chat makes the pipeline brief (`title, line, subject, angle, audience, tone, target_seconds, notes`); "Build this film" (`/api/build`) commits `films/studio/<id>/brief.json` (with `approved_at`, cap 1.50); the job page (`#job/<id>`, `/api/job`) polls `status.json` every 6 s. A 402 from OpenRouter now falls through to the free seat; the UI says so in one line; Setup shows the key's remaining credit.
- Not tested live (needs the Vercel deployment and real keys): a real director turn, a real build commit, the release `films` listing (the release does not exist yet). Local test used a mock OpenRouter (`OPENROUTER_BASE`, tests only).

## Films (22 Oct)
- Done, in rc-render release `kino-films` (12 films, each with a phone preview and a contact sheet): Dark Corners Bamberg
  (Kinetic), Zong and Kleidion (Lantern Road), Arabia (Clay); Battle Map Cannae, Hastings, Agincourt, Waterloo, Thermopylae,
  Gaugamela, Hattin, Ain Jalut. The first seven are also on Sam's Mac (`Video Production/kino-films/`); the Mac disconnected
  before the last five. Build key: about US$1.2 estimated left (17 Oct read plus this night's ledgers).
- Engine for the battles: `films/lib/battlemap/` (spec format `SPEC.md`); sound for the battles: `films/lib/battle_mix.py`.

## Running now (22 Oct, overnight)
- Films lane: Dark Corners restyled (`films/dark-corners/`: Bamberg Kinetic, Zong and Kleidion Lantern Road, Arabia Clay) and the
  Battle Map series in Terrain (`films/battles/`: Cannae, Hastings, Agincourt, Waterloo). Renders: rc-render `films.yml`,
  release `kino-films`. Build key had about US$3.2 left on 17 Oct; battle audio prep capped at US$0.6 to 0.9 each.

## Handover
On 16 Oct Sam moved all building into one new Claude chat, project "Unmissed with studio". KINOFORGE becomes the content
engine inside Unmissed; Sam's approval is the only human step. **Start with `docs/HANDOVER-2026-10-16.md`**: snapshot,
what works, how to start a job, costs per content type, money, decisions, open problems, recommendation.

## Focus
Premium short video ads for Unmissed and its clients, to bring in money. Films and channels are parked. New since 16 Oct:
the **social lane** (`social/`, workflow `social.yml`) for Unmissed's Social Autopilot (12 short videos a month per
client on TikTok, Reels, Shorts, Facebook Reels); first client Smart Mount (Toronto opening in December).

## Done
- **Board `site-samples-v2` (16 Oct, late):** 27 AI stills (cap US$3.00) for invented sample businesses in new industries (realtor, cleaning, salon and barber, renovation and installers, landscaping, burger and fast food, sit-down dining, cafe), previews only, marked Sample and AI-generated there. Done: US$2.34 spent (key about US$8.98 left); stills in the `boards` release.
- **Board `site-samples-v1` (16 Oct, for Unmissed's website template library):** 12 AI stills (Seedream 5 Pro, cap
  US$1.50, about US$0.09 each) for two invented sample businesses, used only in the template previews, marked Sample
  and AI-generated there; no people, no text, no logos; anything that looks like poor workmanship is discarded. Done:
  US$0.81 spent; `hs-mechanical` discarded; 11 stills in the `boards` release.
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
- Board `site-samples-v3-food` (17 Oct): 24 food stills for Unmissed's restaurant templates, cap US$3.00.
- Board `site-samples-v3-industries` (17 Oct): 27 stills for new template industries, cap US$3.00.

## Waiting on Sam
- **Smart Mount's videos: STOPPED by Sam on 16 Oct 2026 (17:32 Toronto)** after he watched the check videos: "they are not
  good, especially because the photo you used is a bad job photo". The install photos in
  `social/clients/smartmount/media/` must not be used again. If the lane restarts, it uses imagery with no copyright
  problem (made in code, licence-free stock, or AI-generated with each platform's AI label) and "a clean professional
  look on everything", shown to Sam on a new style board first. Nothing was rendered on GitHub, nothing posted, $0 spent.
- How to get natural voices (paid audition of other voice models, a human voice, or a mix); whether The Call's AI
  receptionist must sound like Unmissed's live phone agent.
- Bento next steps (new voice, polish, 9:16 layout, French).
- Where production runs (GitHub terms and the runner-minute limit; see the handover, section g).
- The four Unmissed questions in `docs/UNMISSED_HANDOFF.md`.

## Next (in order, for the new chat)
0. Social lane: stopped by Sam on 16 Oct (see Waiting on Sam). Do not dispatch `social.yml`; restart only when he asks.
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
