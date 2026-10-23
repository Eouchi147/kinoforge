# Status (updated 23 Oct 2026, director paid mode)

## Kids explainers in Fable (Sam, 23 Oct 19:34; starting)
- Several 1-minute Fable Cutaway films for kids aged 6 to 8: big concepts made simple (dinosaurs, planet Earth, animals,
  space, oceans), wise and playful minimal narration, music at the centre, one fixed living view, happy bustling world.
- Storage: everything on Sam's Samsung X5 (`KINOFORGE/films/`); nothing on the Mac's own disk.

## Studio OS and manual (Sam, 23 Oct 18:17; in progress)
- AI manual `docs/manual/` (system and workflows done; styles, films and sound being written), human guide `docs/GUIDE.md`
  (after the manual), catalog `tools/catalog.py` to `studio-web/public/data/catalog.json` (done), studio OS `studio-web/`
  (deployed 23 Oct; waiting on Sam: set `STUDIO_PASSCODE` on Vercel), upgrade research
  (`docs/research/STUDIO_UPGRADES_2026-10.md`, done; QC gate `tools/qc.py` being built).

## Cutaway art directions (Sam, 23 Oct 16:34)
- Done: twelve looks on the meadow frames, full size from the Mac lane, sent to Sam with a board; guide doc sent
  (Claude doc "Cutaway: where to take it and how it earns"). Waiting on Sam's pick.
- In progress: the looks ported to the seasons loop (Sam 17:32: the seasons loop is the base); `_adapter.py`,
  look-board folders `films/cutaway/looks/seasons-<name>/`.
- Next after his pick: the Fable music film on the seasons grammar (Borodin, In the Steppes of Central Asia, public
  domain Musopen recording in rc-render release `music`; cuts 1:57 and 3:17, long cut by default).

## What Lies Under a Meadow (Cutaway line example; Sam, 15:58 "go")
- Rendering on the Mac lane from the Samsung X5 (959 frames, about 6.5 s a frame, done about 17:45 Toronto); sound done
  (`films/cutaway/meadow/audio/mix.m4a`, -16 LUFS, no voice). Then: encode on the Mac, check, deliver to `kino-films/`.

## Sam's external drive (23 Oct)
- Samsung X5 (1.9 TB, about 815 GB free), connected to this session as a folder. `KINOFORGE/render/` is the Mac lane's
  home (code copy, `mac-jobs/`); `KINOFORGE/frames/` the frames; `KINOFORGE/films/` an archive of every finished film.
  Start line: `exec(open('/Volumes/Samsung X5/KINOFORGE/render/harness/mac/go.py').read())`. Render leftovers in the iCloud
  folder deleted (Sam, 14:09). Lane running from the drive since 15:34 Toronto (gen 1); a test frame rendered to the drive in 4.7 s.
- Superseded v1 films stay in `Video Production/kino-films/` until Sam says (only copies; iCloud-only, no Mac disk).

## Cutaway showcase series (Sam, 22 Oct 22:18; due on his wake, 23 Oct morning)
- Six 20 s films, no voice, CC0 nature recordings plus a quiet score (`films/cutaway/series/README.md`). Final files go to
  Sam's Mac `Video Production/kino-films/series/`.
- Reef and Wreck: done (Mac lane, 480 frames; 20.0 s, -16.2 LUFS; on the Mac with preview and sheet). Weak spot: the
  opening wide holds nearly still for about 7 s.
- The Gold Mine: done (Mac lane, 480 frames at about 5 s each, 9:16 1080x1920, 20.0 s, -16.2 LUFS). Weak spot: the
  title is small over the moonlit trees.
- River Through Time (-16.2 LUFS), Sleeping Volcano (-16.4), Under the City (-16.3): done on rc-render `films.yml`
  (runs 39894366759, 39895728062, 39896034330), 20.0 s each, no frozen frames, on the Mac. Weak spot: River's water reads
  as a pale grey trench more than water.
- The Hidden Meadow: done (run 39896254752; 9:16, 20.0 s, -16.2 LUFS, no frozen frames), on the Mac. All six series
  films are on Sam's Mac and were sent to him; waiting on his verdict.
- Agincourt v2: done (run 39908562175, 147.3 s, -14.2 LUFS, no frozen frames); both mud inserts checked on their
  boundary frames (after the overlay fix in rc-render 54c1bb4); on Sam's Mac as `battle-map-agincourt-v2.mp4`. All eight
  battles now done on Battle Map v2.
- Also delivered to the Mac on 23 Oct: Why Venice Sinks (`under-the-surface-venice.mp4`, 2:37, -14.1 LUFS) and the
  cinematic look test (`style-cutaway-cinematic.mp4`, 12 s, silent). Agincourt v2: both inserts landed; chain.yml
  dispatched by hand at 04:21 UTC (its cron had not fired).

## Cutaway in the studio (23 Oct, in progress)
- Sam (22 Oct, 20:24 Toronto): "I love the cutaway style, I need it in the kinoforge studio." Free tools only.
- Web studio: Films page has a Cutaway section and filters; Cutaway films appear on their own once their files are in rc-render `kino-films` (seasons loop now; Venice, the drainage ad in both formats, the cinematic test and the line example when they land). Styles page shows the five house styles (Cutaway, Battle Map, Kinetic, Lantern Road, Clay) with a poster each; "Start a film" on a live line opens the director with that line (Cutaway: 16:9 or 9:16). The director chat and `/api/build` know the `cutaway` line (30 to 90 s, format in the brief).
- Engine: `films/lib/cutaway/` (spec-driven: a model writes data, not Blender code; SPEC.md, validator, stills tool, selftest). Example `films/cutaway/meadow/` (40 s, estimated cues, no narration yet). Runner check stills r1 and r2 (rc-render `stills.yml` runs 39880127743, 39884546069): every shot renders at 1280x720, 20 samples; about 30 to 90 s a frame; the 40 s example is about 16 runner-hours (not rendered as a film yet: one full render on `films.yml`, 20 parts, when Sam wants to see it moving).
- Director: line `cutaway` wired (16:9 and 9:16, 30 to 90 s): coder writes `spec.json`, the validator is the check, a Blender contact sheet for the eyes, `films-render.yml` with 48 frames a part. Tested with mocks (`films/director/tests/test_cutaway_line.py`); not yet run live on GitHub. Playbook `docs/PLAYBOOKS/cutaway-film.md`.

## Paid director with caps and gates (23 Oct, ready, nothing run)
- Sam (22 Oct, 20:50): capped paid films, good results every time he pays, best tool per job. Director code is ready (`films/director/README.md`, "Money"): paid mode by default in `config.json` (free mode kept as `free_only: true`), models by role (writer Opus 5.5, checker Gemini 4 Argon, coder Opus with a Sonnet second draft only when it fits, repairs Sonnet, eyes Gemini, lessons Haiku; ids and prices checked on the runner by `seats.py`), ElevenLabs `brian` with Whisper retakes, free procedural score. Cap per film default US$2.00 (0.50 to 5.00), worst case booked before every call. Gates: fact check before narration; checks plus an eyes score of 6.5/10 before any render; a film that cannot pass stops and is not rendered. Usual cost US$0.90 to 1.50 per 2.5 min film.
- Web studio: cap chooser ($1, $2, $3, $5) before "Build this film", spend per stage on the job page, plain messages for no GitHub and no credit; `studio-web/tests/flow.mjs` passes against a mock OpenRouter.
- **Waiting on Sam:** add credit: about US$25 account credit, build key limit US$20, studio key US$5 more (README "Credit"). No paid job has been dispatched.

## Gates and agent harness (23 Oct, done)
- Any agent starts at `AGENTS.md` (Muse Code, Codex, Cursor read it; Claude Code through `CLAUDE.md`, Gemini CLI through `.gemini/settings.json`; Muse's committed memory `.agents/memory/MEMORY.md` is an index into `docs/`). Then `docs/SOUL.md` (taste, verdicts, styles), `docs/MEMORY.md` (who writes what), `docs/decisions/` (12 records), `docs/PLAYBOOKS/` (9 jobs, each with a definition of done), `docs/LESSONS.md`. Research with sources: `docs/research/AGENT_HARNESS_2026-10.md`.
- `bash tools/verify.sh` (fast, about 1 min) and `--full` (about 10 min): every house rule as a gate; run it before every commit. CI: `verify.yml` on every push (green), `verify-engine.yml` on engine changes. Main passes all gates.
- **Money rule:** settled by `docs/decisions/0013` (capped paid films with quality gates; Sam, 22 Oct 20:50).

## NOOR Ramadan samples (22 Oct, started 14:30 UTC; delivered 23 Oct 00:40 UTC, waiting on Sam's verdict)
- Sam asked (Noor Codex chat) for 2 to 3 free sample videos for the NOOR Ramadan 2027 series (series bible: Claude doc "NOOR · Thirty Nights of Light").
- Building in `films/noor/`: `n05-iqra` (The Descent, Night 5), `j30-amma` (Tonight's Juz, Night 30), then a 9:16 short from Iqra. Narration and score: `noor-sound.yml` (free). Picture: Lantern Road engine, rendered by `films-render.yml` (free), release `films`.
- `j30-amma` picture done (NOTES.md in its folder); render dispatched on `films-render.yml` (release `films`, asset `noor-juz-30-amma.mp4`).
- n05-iqra picture done (20 shots, 158.8 s) and the 9:16 short s05-iqra-short (36.4 s); both rendering on `films-render.yml` to release `films`.

## Rework after Sam's verdicts (22 Oct, 09:20 Toronto): in progress
- **Spend nothing.** Free models and free tools only. The paid director test job (battle-of-tours) was cancelled after
  US$0.36. The studio key shows $0 left; the director chat runs on a free model.
- The verdicts and the house rules are in `films/director/CRAFT.md` (read before any film work); lessons in `LESSONS.md`.
- Running (agents, nothing rendered yet):
  - free procedural score engine (`films/lib/score/`): done, the 8 battles re-scored (narration kept); brightening and cue beat grids in progress; Sam to listen to three excerpts;
  - Battle Map engine v2 (no emoji, refined heraldic graphics, legend panel, formations that never overlap, planned camera per scene, living world) with Cannae as the reference film: done (9 scenes, 26 shots, 0 check errors), Cannae v2 done with the final score and on Sam's Mac (`-v2`); the other battles are re-directed on v2 (Hastings, Waterloo, Thermopylae, Gaugamela, Hattin, Ain Jalut done with the final score and on Sam's Mac as `-v2`; Agincourt renders after its two Cutaway inserts);
  - Kleidion re-directed (done: 9 scenes, 29 shots instead of 64, opening in real time, fuller worlds); done and on Sam's Mac (`-v2`);
  - Arabia re-directed (done: pin-hole star sky in its own no-blur pass, 31 shots in 9 scenes instead of 49, fuller camp, cut-paper cards); done and on Sam's Mac (`-v2`);
  - Bamberg polished (done: eight movements, every effect with a job); done and on Sam's Mac (`-v2`);
  - director pipeline: done; paid with caps and gates by default since 23 Oct (see above), free mode kept; first free day: Salamis through script and sound, stopped at the picture spec by the free daily limit (1,000 requests); resumes 00:10 UTC by a scheduled task; Great Emu War after it.
  - new style **Cutaway** (Sam, 10:11): Blender kit and a four-look style board in `films/styles/cutaway/`, nothing rendered on runners yet. Sam (10:16) wants all four uses built: briefs in `films/cutaway/` (sample trade ad, Why Venice Sinks, Agincourt mud inserts, seasons loop); the kit's first usable version landed (516ec0b); four builders are on them now.
- Next: re-render on GitHub runners (free), new stories through the free director, one render home for the studio.

## Web studio (22 Oct, studio-web/)
- Reworked: `/api/media` streams release assets (allow-list: rc-render `kino-films`, kinoforge `films` and `gallery`; Range forwarded, no token) so previews play and seek; the old pilot clips in `studio-web/public/media/` are now committed (`.gitignore` exception) and deploy.
- Films page lists the 12 `kino-films` films (posters in `public/posters/`) plus anything in kinoforge release `films` (live, cached 60 s), 16:9 and 9:16 players, download link to the full file on GitHub.
- Director chat makes the pipeline brief (`title, line, subject, angle, audience, tone, target_seconds, notes`); "Build this film" (`/api/build`) commits `films/studio/<id>/brief.json` (with `approved_at` and the cap Sam picks, default 2.00); the job page (`#job/<id>`, `/api/job`) polls `status.json` every 6 s. A 402 from OpenRouter now falls through to the free seat; the UI says so in one line; Setup shows the key's remaining credit.
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
(16 Oct wording below; films resumed at Sam's request on 21 Oct, so which lane comes first is an open question for him:
`docs/decisions/0011`.)
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
