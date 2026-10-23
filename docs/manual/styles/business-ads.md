# Style: business ads built in code (Unmissed and its clients)

Business ads are 15 to 30 s films for Unmissed (Sam's AI marketing agency) and its owner-run clients in Canada: premium,
modern, honest. The picture is an HTML/CSS (or Three.js) scene on a fixed 1920x1080 stage, stepped frame by frame in
headless Chromium (`harness/dom-render.cjs`), so every word, logo and number is exact and costs nothing; music and voice are
prepared first and the picture is timed to them ("music first"). The pipeline is `codead.yml` (`harness/shots/prep.py`,
`harness/shots/codead.py`). Six ads exist (`ads/unmissed-01`, `ads/unmissed-v1` to `-v5`, release `ads`). Sam's chosen
direction is **Bento** (`unmissed-v5`, loved on 16 Oct). The lane is paused (`docs/PLAYBOOKS/make-a-business-ad.md`): Bento
polish, natural voices and a 9:16 layout wait on Sam; paid calls need his go per job.

## Inputs
- The client's claims in its own written words (Unmissed: `harness/shots/policies/unmissed.md` and the Unmissed site's
  `site.config.js` in the private repo `Eouchi147/sovereign-studio`). A demo shows an invented business and says
  "Demo with an invented business"; an AI-made element carries "Made with AI, checked by a person" where the platform asks
  (`docs/decisions/0012`).
- A look Sam picked on a style board (`docs/decisions/0008`): no video before his pick.
- Fonts: `ads/fonts/` (Instrument Sans variable 400 to 700 and width 75 to 100 %, Archivo, JetBrains Mono; all SIL OFL).
- `OPENROUTER_API_KEY` as a GitHub secret (Sam adds it; agents never see it).

## The looks (`harness/shots/directions/*.md`)
| Look | What it is | Status |
| --- | --- | --- |
| **Bento** (`ads/unmissed-v5`) | Apple-style product film on the day theme: a big grid of white tiles (radius 40 px, soft layered shadows), each a tiny live UI (calls, leads, reviews, website, Google profile, run-for-you checklist); a CSS camera glides and punches into each tile on its beat, pulls back, tiles collapse into the ring logo | Sam's chosen direction |
| **Screen Story** (`ads/board/screen-story`) | the product working on a 3D phone, clean type beside it, Apple and Stripe launch language | "amazing" (15 Oct) |
| **Type in Motion** (`ads/board/type-motion`) | kinetic type in brand colours, one bold variable face, photos only inside letters or masks; real photo cut-outs, never drawn objects | "great" (the drawn bread looked fake) |
| Manifesto (`unmissed-v1`), The Catch (`unmissed-v2`, Three.js glass ring) | kinetic type slams / 3D cinematic depth | "a little" |
| The Call (`unmissed-v3`) | no narrator: a real-sounding call as huge kinetic captions | loved, but the voice "too fake" |
| Night Shift (`unmissed-v4`) | AI footage of an empty restaurant at night | "a big NO" |
| AI-image looks (Flash Editorial, Hero Close-ups, Freeze Frame) | kept only as inserts (Freeze Frame: one solid subject only); Voltage retired ("AI slop"), Documentary rejected; Classic used once for keyframes only (`pieces/unmissed-brand-01`), no verdict recorded | see `ai-pieces.md` |

## The craft bar (`ads/UNMISSED_DIRECTION.md`)
- Music first: the score exists before the picture (`audio/music.mp3`, beat map `audio/music.json`: bpm, beats, downbeat
  guess, 0.1 s energy curve, `biggest_rise_s`). Every cut, word entrance, camera move and colour change lands on a beat or
  half-beat; big moments on downbeats or the drop; nothing idles more than about 1.5 s.
- Scale and contrast: words that matter 120 to 420 px on the 1920x1080 stage, tracking -0.03 to -0.05 em; nothing important
  under 36 px; safe margin 96 px; one idea per frame; no layout more than twice in a row.
- Real motion design: hard cuts on the beat, masked reveals, scale punches (1.15 to 1.0 in 4 to 6 frames, expo-out), whips,
  zoom-throughs, match cuts, parallax, a moving stage camera, glows; motion blur on (`render.sub` 2 to 4 sub-frames), film
  grain in post (`post.grain` 5).
- Voice placed on beats (`audio.vo[].start`); never speed a line up, move the next cue instead.
- Night palette: bg `#05070f`, glow `#0b1530` / `#070c1c`, ink `#f4f6fb`, `#c3cad8`, `#98a1b5`, accent `#79b4ff`, action blue
  `#2f7df6`, deep `#0b3b8f`, violet `#8c6eff` (logo only), ok `#5ad69a`, alert `#ff6b6b`. Day (Bento): bg `#f4f6fa`, surface
  `#ffffff`, ink `#0b1020`, ink2 `#3d4658`, accent `#2456c9`, soft blue `#e7eeff`.
- End card: the ring logo (ring `#2f7df6`, node `#79b4ff` at one o'clock), "Unmissed", "A premium presence. An AI front
  desk.", small "Made with AI, checked by a person".

## Exact steps
1. Folder `ads/<id>/`: `TREATMENT.md` (the director's treatment), `ad.json`, `index.html`.
2. `ad.json` prep block: `music.prompt` (instrumental only, no vocals; a tempo; where the build, drop or stop falls),
   `voice_brief`, `voice_cast` (candidate ElevenLabs voices, e.g. `["eric", "brian", "river"]`), `vo` lines; or `dialogue`
   (lines with `who`, `voice`, `text`, ElevenLabs v3 tags like `[casual]` allowed); `cap_usd` (0.5 to 0.6 was used).
3. Prep on GitHub (paid, about US$0.05 to 0.07 an ad; Sam's go first):
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/codead.yml/dispatches -f ref=main -f 'inputs[ad]=<id>' -f 'inputs[mode]=prep'`.
   It commits `audio/music.mp3`, `audio/music.json`, `audio/casting.json` (an audio model scores every candidate's reel and
   writes `best` and `why`), `audio/vo/*.mp3`, `audio/vo.json` or `audio/dialogue.json` (Whisper word times). Pull.
4. Check the beat grid (trackers halve or double the tempo: librosa with `start_bpm`), then write the `audio` block
   (`music`, `music_offset`, `music_gain_db`, `duck_ratio`, `music_fade_s`, voice start times), `sfx` (`t`, `kind`: ring,
   click, pop, whoosh, check, chime, impact, tick, riser; synthesised in `codead.py`), `cues` (named scene times),
   `render.sub`, `post.grain`. Cut the music on whole bars with short equal-power cross-fades if it must be shorter (Bento's
   `music_edit.mp3`, recorded in `audio.music_edit`).
5. Scene `index.html`: fixed 1920x1080 stage; `window.KF = { duration, fps: 30, render(i, t) }` sets every style from `t`
   (no CSS transitions); reads `./ad.json` at load; `window.KF_READY = true` after fonts, images and ad.json load. Helpers
   from `/ads/lib/motion.js`: `seg`, `ease`, `words`, `letters`, `rise`, `show`, `mulberry` (seeded random), `fitStage`.
6. Local stills (free): `node harness/dom-render.cjs ads/<id> --stills 1.5,6,12 --stills-only --out out/<id>`; a silent MP4
   without `--stills-only`; `--param key=value` passes query parameters.
7. Render on GitHub (about US$0.01 for the listening check):
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/codead.yml/dispatches -f ref=main -f 'inputs[ad]=<id>' -f 'inputs[mode]=render'`.
   Output in release `ads`: `<id>.mp4` (16:9 master, -14 LUFS), `<id>-sheet.jpg`, `<id>-listen.json` (an audio model's
   transcript and notes on voice, music, sounds and mix); `ads/<id>/ledger.json` committed. About 6 minutes a run.
8. Check every frame and the listening notes; show Sam; nothing is published without him.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Older single-step ad (`unmissed-01`: `voice`, `vo` with start times, `music.prompt` in ad.json, no `audio` block) | a quick ad where voice and music are generated during the render | about US$0.05 to 0.11 a run |
| Social templates (`social.md`) | 9:16 client tips and teach cards | free except optional music |
| Cutaway trade ad (Cutaway manual, `films/cutaway/ads/drainage`) | the work is underground (drainage, foundations) | free |
| Free voice (Kokoro or Chatterbox through `sound.yml`) and the free score | when Sam wants no spend; not yet tried on an ad | free |

## Checks before showing Sam
- Claims match the policy word for word; demo label present; AI line on the end card.
- No layout repeated more than twice; every cut on a beat; nothing important under 36 px.
- The listening check (`<id>-listen.json`) has no problem left; the voice sounds natural (Sam: "the voices should sound the
  most natural possible, not AI at all").
- Bitrate capped (grain is incompressible): `codead` caps at crf 20, max 14 Mbps (v1 first came out at 72 Mbps).

## Known traps
- A new workflow file is registered only after a push that touches it (`codead.yml` was not registered at first).
- Lyria returns audio only when streamed; music calls had always failed before `factory.music()` was rewritten.
- Beat trackers halve or double tempos (v1 found 61.5 for a 124 track, v4 143.5 for 72).
- Dialogue recognition failed with faster-whisper on new PyAV: decode with librosa or ffmpeg first.
- Never measure the stage before the fonts load (an early `offsetWidth` read shifts glyph rasterization).
- `fitStage()` scales uniformly and letterboxes another aspect; a 9:16 version needs its own layout.
- Square stills fed to a 16:9 video model get pillarboxed: crop first (Night Shift footage).

## Sources of truth
`ads/UNMISSED_DIRECTION.md`, `ads/*/TREATMENT.md`, `ads/*/ad.json`, `harness/shots/prep.py`, `codead.py`, `factory.py`,
`harness/dom-render.cjs`, `ads/lib/motion.js`, `harness/shots/directions/`, `harness/shots/policies/unmissed.md`,
`docs/WORKFLOWS.md` (codead), `docs/PLAYBOOKS/make-a-business-ad.md`, `docs/SOUL.md` sections 3 to 5, `docs/LOG.md` (15 and 16 Oct).
