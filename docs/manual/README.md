# The KINOFORGE manual (for AI agents)

This is the AI manual of KINOFORGE, Sam's AI-run film and video studio: how the studio is built, how every workflow is
run, how every style is made, and how every film was made, step by step, so any agent can make a new film from zero or
recreate an existing one exactly. It is written to be read by models: literal commands, file paths, inputs and outputs,
and "not recorded" where the record is silent. It summarises the repo; when a page and the code disagree, the code wins,
then the newest dated record (`docs/LOG.md`, `docs/decisions/`, Sam's verdicts in `docs/SOUL.md`).

House law is `AGENTS.md` (read it first, every session). This manual does not replace it, the playbooks
(`docs/PLAYBOOKS/`) or the engines' own specs; it ties them together.

## Read order
1. `AGENTS.md`: session start (pull, `bash tools/verify.sh`, read STATUS), the rules that never bend, how to work.
2. `docs/STATUS.md` (now) and the top day of `docs/LOG.md` (latest changes).
3. `docs/SOUL.md` (taste, Sam's verdicts) and `films/director/CRAFT.md` (craft rules) before any film work.
4. This README, then `system/architecture.md` (the map) and `system/autonomous-run.md` (brief to delivered film).
5. For your job: the style page, the film page closest to what you are making, and the workflow pages it names.
6. Before you show anything: `system/quality-checks.md`, `system/deliver-to-sam.md`; after any change:
   `system/keeping-the-record.md`.

## How to make any film from zero
1. **Subject and approval.** The subject comes from Sam (chat, the web studio, or `films/director/SLATE.md`). A new look
   or a new client: a style board of free stills first, Sam picks (`docs/decisions/0008`).
2. **Pick the style** from `styles/` (or the catalog's `styles`): what it is for, its engine, its known traps. Sam's
   latest Cutaway verdict (23 Oct): the seasons loop grammar (one fixed view, no cuts, a living world) is the base; he did
   not like the cinematic test (camera moves, cuts).
3. **Pick the route** (`system/autonomous-run.md`):
   - Director pipeline (no session): a brief in `films/studio/<id>/brief.json` on the `battle-map`, `kinetic` or
     `cutaway` line, capped money (`workflows/director-pipeline.md`, `workflows/web-studio-build.md`).
   - By hand (best craft today): copy the closest film folder (its page in `films/`), follow the style page's exact
     steps and its playbook (`docs/PLAYBOOKS/`).
4. **Sound first** for narrated films (`workflows/narration-and-score.md`, `sound/`); the picture follows `cues.json`.
   No-voice films: recordings from the sound bank plus a quiet score (`sound/sfx-bank.md`, `sound/score-engine.md`).
5. **Plan, build, check:** scene list with a job each, a reason for every cut, the engine's checks to zero errors,
   `bash tools/verify.sh`.
6. **Look:** small local stills, then full-quality stills on runners (`workflows/check-stills.md`). Open every still.
7. **Render:** runners (`workflows/render-film-on-runners.md`) or the Mac lane (`workflows/render-on-the-mac.md`);
   waits on other renders go in a chain (`workflows/follow-up-chains.md`).
8. **Check, deliver, record:** `system/quality-checks.md`, `system/deliver-to-sam.md`, `system/keeping-the-record.md`,
   and the catalog (`system/catalog.md`). Nothing is published without Sam.

## How to recreate an existing film
1. Find it: `python3 tools/catalog.py --stdout` (or `studio-web/public/data/catalog.json`) gives each film's `id`,
   `folder`, `recipe` page, `status`, release asset and `made_with`.
2. Read its page in `films/` (what makes it, the commands and run ids that made it, the sound, the assembly, weak spots)
   and the folder's `NOTES.md`.
3. Check out the version you want. The folder at `main` is the latest version; a re-made film's `NOTES.md` records the
   old version's last commit where the re-direction kept one (`docs/PLAYBOOKS/redirect-from-sams-notes.md`, step 4);
   the first Kleidion was kept in `films/dark-corners/kleidion_old/` (removed in commit 212953a; `git show 212953a^:films/dark-corners/kleidion_old/<file>`). Otherwise use `git log -- <folder>`.
4. The sound is committed (`audio/mix.m4a`, `cues.json`): reuse it. Regenerate only if the page says how
   (`workflows/narration-and-score.md`, the series sound kit).
5. Render with the same workflow, inputs and `ref` (a FULL commit hash) the page records. Every frame is a function of
   the frame index (seeded, no clocks), so the same commit gives the same film; a bit-for-bit match across render homes
   (Metal on the Mac versus CPU on runners) is not recorded.
6. Inserts (Agincourt): render the inserts first, then the host film (`film.json` `inserts`).
7. Check against the recorded numbers (length, loudness) with `system/quality-checks.md`.

## Index

### System (`system/`)
| Page | What |
| --- | --- |
| [architecture.md](system/architecture.md) | Repos, releases, render homes (rc-render workflows, kinoforge workflows, the Mac lane on the Samsung X5 drive, Vercel studio), accounts |
| [autonomous-run.md](system/autonomous-run.md) | Brief to delivered film, both routes, every decision point and who decides, what to do when a run stops |
| [gates.md](system/gates.md) | `tools/verify.sh`: every gate, how to fix, other checks |
| [money-and-keys.md](system/money-and-keys.md) | Decision 0013: caps, what costs money, keys, credit |
| [quality-checks.md](system/quality-checks.md) | Numbers, contact sheet, moving stretches, targets by kind, what to reject |
| [deliver-to-sam.md](system/deliver-to-sam.md) | Links, the Mac, the web studio, the message |
| [keeping-the-record.md](system/keeping-the-record.md) | LOG, STATUS, NOTES, decisions, lessons, the catalog |
| [catalog.md](system/catalog.md) | `studio-web/public/data/catalog.json`: what it holds, how `tools/catalog.py` builds it |
| `studio-os.md` | The studio OS (web studio rework of 23 Oct), written by its builder |

### Workflows (`workflows/`)
| Page | Started by | Cost |
| --- | --- | --- |
| [render-film-on-runners.md](workflows/render-film-on-runners.md) | rc-render `films.yml` | free |
| [check-stills.md](workflows/check-stills.md) | rc-render `stills.yml` | free |
| [render-on-the-mac.md](workflows/render-on-the-mac.md) | job JSON in `KINOFORGE/render/mac-jobs/`; `harness/mac/go.py` in Blender | free |
| [remux-sound.md](workflows/remux-sound.md) | rc-render `remux.yml` | free |
| [follow-up-chains.md](workflows/follow-up-chains.md) | rc-render `chain.yml` rule (every 15 min) | free |
| [fetch-music.md](workflows/fetch-music.md) | rc-render `music-fetch.yml` | free |
| [build-the-sound-bank.md](workflows/build-the-sound-bank.md) | rc-render `sfx-bank.yml` | free |
| [narration-and-score.md](workflows/narration-and-score.md) | kinoforge `sound.yml`, `noor-sound.yml` | free |
| [director-pipeline.md](workflows/director-pipeline.md) | brief push or kinoforge `film.yml`; `films-render.yml` | capped, usual US$0.90 to 1.50 |
| [web-studio-build.md](workflows/web-studio-build.md) | "Build this film" (`POST /api/build`) | as the director |
| [social.md](workflows/social.md) | kinoforge `social.yml` (paused) | free plus optional music |
| [ads.md](workflows/ads.md) | kinoforge `codead.yml` (paused) | about US$0.06 an ad |
| [style-boards-and-ai-footage.md](workflows/style-boards-and-ai-footage.md) | kinoforge `board.yml`, `piece.yml` | paid, Sam's go per job |
| [legacy-lanes.md](workflows/legacy-lanes.md) | `render.yml`, `showcase.yml`, `voice.yml`, `finish.yml`, `director.yml`, `motion.yml`, `smoke.yml` | history |

### Styles (`styles/`, written by the "cutaway" and "lines" writers)
| Page | What |
| --- | --- |
| [cutaway.md](styles/cutaway.md) | The Cutaway kit and house style |
| [cutaway-line.md](styles/cutaway-line.md) | The spec-driven Cutaway line (`films/lib/cutaway/`, `spec.json` as data) |
| [cutaway-seasons-loop.md](styles/cutaway-seasons-loop.md) | The seasons loop grammar, the base since 23 Oct |
| [cutaway-cinematic.md](styles/cutaway-cinematic.md) | The cinematic version (moving cameras, cuts; Sam did not like the test) |
| [cutaway-art.md](styles/cutaway-art.md) | The art direction hook (`look.art`, `$KF_ART`, `_adapter.py` for the seasons loop) |
| [cutaway-board-looks.md](styles/cutaway-board-looks.md) | The 12-look board and how it was made |
| [cutaway-flat-vector.md](styles/cutaway-flat-vector.md) | Flat vector, the Cutaway as a 2D web film |
| `cutaway-art-<look>.md` | One page per Blender look: [fable](styles/cutaway-art-fable.md), [night-glow](styles/cutaway-art-night-glow.md), [stained-glass](styles/cutaway-art-stained-glass.md), [papercraft](styles/cutaway-art-papercraft.md), [claymation](styles/cutaway-art-claymation.md), [pixel](styles/cutaway-art-pixel.md), [risograph](styles/cutaway-art-risograph.md), [storybook-ink](styles/cutaway-art-storybook-ink.md), [blueprint](styles/cutaway-art-blueprint.md), [chalkboard](styles/cutaway-art-chalkboard.md), [engraving](styles/cutaway-art-engraving.md) |
| [battle-map.md](styles/battle-map.md) | Battle Map v2 (Terrain) |
| [kinetic.md](styles/kinetic.md) | Kinetic |
| [lantern-road.md](styles/lantern-road.md) | Lantern Road |
| [clay.md](styles/clay.md) | Clay |
| [dark-corners.md](styles/dark-corners.md) | The Dark Corners series |
| [noor.md](styles/noor.md) | NOOR (Ramadan samples; strict depiction rules) |
| [business-ads.md](styles/business-ads.md) | Business looks (Bento, Screen Story, Type in Motion) and the Unmissed ads |
| [social.md](styles/social.md) | Social templates (card-motion, bento, type-motion) |
| [ai-pieces.md](styles/ai-pieces.md) | AI-footage pieces (paused) |
| [anthology-prototypes.md](styles/anthology-prototypes.md) | The anthology prototypes (`proto/`) and the two pilots |

### Sound (`sound/`, written by the "lines" writer)
| Page | What |
| --- | --- |
| [score-engine.md](sound/score-engine.md) | The free procedural score (`films/lib/score/`) |
| [narration.md](sound/narration.md) | Voices: Kokoro, Chatterbox, ElevenLabs; auditions; Whisper checks |
| [battle-mix.md](sound/battle-mix.md) | Narration on a beat grid (`films/lib/battle_mix.py`) |
| [sfx-bank.md](sound/sfx-bank.md) | The CC0 recording bank and how films use it |
| [music-fetch.md](sound/music-fetch.md) | Music from Commons with licences |
| [remux.md](sound/remux.md) | New sound on a finished film |
| [loudness.md](sound/loudness.md) | Loudness targets and checks |

### Films (`films/<id>.md`, one per film; ids are `film.json` ids)
The "cutaway" writer covers the Cutaway films and loops, the "lines" writer every other film. A page may be pending: the
catalog's `recipe` field points at the page when it exists. The anthology prototypes are covered by
`styles/anthology-prototypes.md` and the Unmissed ads by `styles/business-ads.md`.

| Series | Film | id | Status | Folder |
| --- | --- | --- | --- | --- |
| Battle Map | [The Battle of Cannae](films/battle-map-cannae.md) (reference) | `battle-map-cannae` | delivered | `films/battles/cannae` |
| Battle Map | [The Battle of Hastings](films/battle-map-hastings.md) | `battle-map-hastings` | delivered | `films/battles/hastings` |
| Battle Map | [The Battle of Agincourt](films/battle-map-agincourt.md) | `battle-map-agincourt` | delivered | `films/battles/agincourt` |
| Battle Map | [The Battle of Waterloo](films/battle-map-waterloo.md) | `battle-map-waterloo` | delivered | `films/battles/waterloo` |
| Battle Map | [The Battle of Thermopylae](films/battle-map-thermopylae.md) | `battle-map-thermopylae` | delivered | `films/battles/thermopylae` |
| Battle Map | [The Battle of Gaugamela](films/battle-map-gaugamela.md) | `battle-map-gaugamela` | delivered | `films/battles/gaugamela` |
| Battle Map | [The Battle of Hattin](films/battle-map-hattin.md) | `battle-map-hattin` | delivered | `films/battles/hattin` |
| Battle Map | [The Battle of Ain Jalut](films/battle-map-ain-jalut.md) | `battle-map-ain-jalut` | delivered | `films/battles/ain-jalut` |
| Battle Map (inserts) | [Agincourt mud insert A](films/cutaway-agincourt-mud-A.md) | `cutaway-agincourt-mud-A` | rendered | `films/cutaway/agincourt-mud/A` |
| Battle Map (inserts) | [Agincourt mud insert B](films/cutaway-agincourt-mud-B.md) | `cutaway-agincourt-mud-B` | rendered | `films/cutaway/agincourt-mud/B` |
| Battle Map (director) | [The Battle of Salamis](films/salamis.md) | `salamis` | in-progress | `films/studio/salamis` |
| Battle Map (director) | [The Battle of Tours](films/battle-of-tours.md) | `battle-of-tours` | draft | `films/studio/battle-of-tours` |
| Kinetic (director) | [The Great Emu War](films/great-emu-war.md) | `great-emu-war` | draft | `films/studio/great-emu-war` |
| Director examples | [Kinetic line example](films/kinetic-demo.md) | `kinetic-demo` | draft | `films/studio/kinetic-demo` |
| Dark Corners | [A Hundred Thousand Good Nights](films/dark-corners-bamberg-kinetic.md) (Kinetic) | `dark-corners-bamberg-kinetic` | delivered | `films/dark-corners/bamberg` |
| Dark Corners | [The Ship Called Care](films/dark-corners-zong-lantern-road.md) (Lantern Road) | `dark-corners-zong-lantern-road` | delivered | `films/dark-corners/zong` |
| Dark Corners | [As They Say](films/dark-corners-kleidion-lantern-road.md) (Lantern Road) | `dark-corners-kleidion-lantern-road` | delivered | `films/dark-corners/kleidion` |
| Dark Corners | [I Am Buying Her Life](films/dark-corners-arabia-clay.md) (Clay) | `dark-corners-arabia-clay` | delivered | `films/dark-corners/arabia` |
| NOOR | [Juz Amma](films/noor-juz-30-amma.md) | `noor-juz-30-amma` | delivered | `films/noor/j30-amma` |
| NOOR | [Iqra](films/noor-descent-05-iqra.md) | `noor-descent-05-iqra` | delivered | `films/noor/n05-iqra` |
| NOOR | [Iqra (short)](films/noor-descent-05-iqra-short.md) | `noor-descent-05-iqra-short` | delivered | `films/noor/s05-iqra-short` |
| Under the Surface | [Why Venice Sinks](films/under-the-surface-venice.md) | `under-the-surface-venice` | delivered | `films/cutaway/venice` |
| Cutaway loops | [Four seasons over one block](films/cutaway-loop-seasons.md) | `cutaway-loop-seasons` | delivered | `films/cutaway/loops/seasons` |
| Cutaway | [What Lies Under a Meadow](films/cutaway-line-meadow.md) (the line example) | `cutaway-line-meadow` | in-progress | `films/cutaway/meadow` |
| Cutaway | [Drainage sample ad, 16:9](films/cutaway-ad-drainage-v169.md) | `cutaway-ad-drainage-v169` | delivered | `films/cutaway/ads/drainage/v169` |
| Cutaway | [Drainage sample ad, 9:16](films/cutaway-ad-drainage-v916.md) | `cutaway-ad-drainage-v916` | delivered | `films/cutaway/ads/drainage/v916` |
| Cutaway showcase | [The River Through Time](films/cutaway-series-river-time.md) | `cutaway-series-river-time` | delivered | `films/cutaway/series/river-time` |
| Cutaway showcase | [Under the City](films/cutaway-series-under-the-city.md) | `cutaway-series-under-the-city` | delivered | `films/cutaway/series/under-the-city` |
| Cutaway showcase | [The Hidden Meadow](films/cutaway-series-hidden-meadow.md) | `cutaway-series-hidden-meadow` | delivered | `films/cutaway/series/hidden-meadow` |
| Cutaway showcase | [Reef and Wreck](films/cutaway-series-reef-and-wreck.md) | `cutaway-series-reef-and-wreck` | delivered | `films/cutaway/series/reef-and-wreck` |
| Cutaway showcase | [The Gold Mine](films/cutaway-series-gold-mine.md) | `cutaway-series-gold-mine` | delivered | `films/cutaway/series/gold-mine` |
| Cutaway showcase | [The Sleeping Volcano](films/cutaway-series-sleeping-volcano.md) | `cutaway-series-sleeping-volcano` | delivered | `films/cutaway/series/sleeping-volcano` |
| Styles | [Cutaway, cinematic hero version](films/style-cutaway-cinematic.md) | `style-cutaway-cinematic` | delivered | `films/styles/cutaway/cinematic` |
| Styles | [Cutaway motion test](films/style-cutaway-test.md) (never rendered) | `style-cutaway-test` | draft | `films/styles/cutaway/test` |
| Unmissed ads | `unmissed-01`, `unmissed-v1` to `-v5` | see `styles/business-ads.md` | delivered | `ads/<id>` |
| Anthology prototypes | 15 rendered prototypes and pilots (`p01` to `p16`, no `p14`) | see `styles/anthology-prototypes.md` | rendered | `proto/<id>` |
The look boards (`films/cutaway/looks/<look>/` on the meadow, `seasons-<look>/` on the seasons loop) are styles, not
films: see the Cutaway art pages; their board images are in `studio-web/public/looks/`.

## Page format (every page in this manual)
A paragraph "what this is", then **Inputs**, **Exact steps** (numbered, literal commands, paths, dispatch calls with
inputs, expected outputs and how to check them), **Alternatives** (other routes, when, cost), **Checks before showing
Sam**, **Known traps**, **Sources of truth**. Film pages add: the folder and every file, the commands and run ids that made
it, the sound, the assembly, delivery, cost, Sam's verdict, weak spots, and "to make a new one like it". House style: no
em dash, no en dash, no "..."; facts only from the repo; "not recorded" where the record is silent.

## Keeping this manual true
Change a page in the same commit as the process it describes, and log it. When a film is rendered, delivered or judged,
update its row in `tools/catalog.py` and run `python3 tools/catalog.py`.
