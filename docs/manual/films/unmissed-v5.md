# Ad: Unmissed, Bento (`unmissed-v5`), Sam's chosen direction

An 18 s, 16:9 brand ad for Unmissed in the site's day theme: an Apple-style product film where a bento grid of white tiles,
each a tiny live UI (calls answered, leads followed up, reviews asked for, a website, a Google profile, a run-for-you
checklist), is toured by a gliding CSS camera that punches into each tile on its beat, pulls back to the whole system and
collapses into the ring logo. Built music first on 16 Oct 2026 as version 5 of five directions. Sam's verdict (16 Oct):
**loved, "all together, sound and visuals"**: Bento is the chosen direction for Unmissed. Style: `docs/manual/styles/business-ads.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `ads/unmissed-v5/` |
| Length | 18.0 s, 1920x1080, 30 fps; motion blur `render.sub` 3, grain `post.grain` 5 |
| Music | Lyria (`audio/music.mp3`, 118 bpm brief: bright, upbeat, premium modern electronic pop, a short stop around 12 s, a final hit around 16 s), edited to `audio/music_edit.mp3` (two beat-aligned cuts: original 7.356 to 11.389 s and 20.067 to 21.048 s removed, 35 ms equal-power cross-fades); `music_offset` 4.6 s, gain -5 dB, duck ratio 2.5 |
| Voice | ElevenLabs `jessica` (cast by `xiaomi/mimo-v2.6-pro`: "warm and bright, upbeat, naturally human") |
| Render | `codead.yml` mode `render`, 16 Oct; listening check: no problems |
| Release | kinoforge `ads`: `unmissed-v5.mp4` (155 MB), `-sheet.jpg`, `-listen.json`, `-prep.log` |
| Cost | US$0.06464 (music US$0.04, voice US$0.021, listening US$0.00364); cap US$0.60 |
| Verdict | loved; next steps (a new voice, polish, a 9:16 layout, French) wait on Sam |

## Structure (`TREATMENT.md`, timings in `ad.json` `cues`)
Beat = 60/118 s; drop at 1.25 s. Tiles flip up into place one per half-beat (pops 0.12 to 0.67 s); punch into Calls at 1.25 s
("Calls, answered."), whip to Leads 3.28 s ("Leads, followed up."), Reviews 5.32 s ("Reviews, asked for."), Website and Google
profile 7.35 s ("A website that looks the part."); pull back at 8.88 s, the music's stop at 9.39 s, the whole bento at 9.75 s
with the checklist ticking (9.89, 10.91, 11.42 s) under "All built for you, and run for you."; tiles collapse at 11.68 s and the
ring logo draws on the hit at 12.44 s; "Unmissed. A premium presence. An AI front desk." End card on the day palette with the
small AI line; "Demo with an invented business" bottom left. The website tile uses `/ads/unmissed-01/media/bread-oven.jpg`.
Sound effects: a quiet pop on each tile flip, whooshes on camera whips, checks on ticks, an impact on the logo.

## Exact steps to re-make it
1. Local stills: `node harness/dom-render.cjs ads/unmissed-v5 --stills 1.5,6,12 --stills-only --out out/unmissed-v5`.
2. Render (about US$0.01 for the listening check; Sam's go first for anything paid):
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/codead.yml/dispatches -f ref=main -f 'inputs[ad]=unmissed-v5' -f 'inputs[mode]=render'`.
   The committed `audio/` is reused; `prep` would make new paid music and voice.
3. Check the sheet, the listening notes and every claim against `harness/shots/policies/unmissed.md`.

## Weak spots
- The voice is synthetic (Sam's bar: fully natural); a natural voice is the first next step.
- 16:9 only; a 9:16 layout needs its own composition (`fitStage` letterboxes, it does not re-lay out).
- The master was not bitrate-capped (155 MB for 18 s); re-render with the current `codead` cap (crf 20, max 14 Mbps).

## To make a new one like it
Copy the folder's structure: a large grid plane with tiles, a camera as a CSS transform, micro animations per tile on beat
times derived from one `drop` and `beat` in `ad.json` `cues`; music first, edited on whole bars if needed.

## Sources of truth
`ads/unmissed-v5/TREATMENT.md`, `ad.json`, `index.html`, `ledger.json`, `audio/casting.json`, `ads/UNMISSED_DIRECTION.md`,
`docs/LOG.md` (16 Oct), `docs/SOUL.md` section 3.
