# Film recipe: Reef and Wreck (`cutaway-series-reef-and-wreck`)

Cutaway showcase series, film 4. 20 s, 16:9. Use it shows: ocean, travel, adventure, tourism. A small tropical island on
a block that is mostly clear turquoise sea, cut open on two glass faces; a diver rolls off a little boat, sinks past light
rays, a coral reef, a school of fish that turns together and a sea turtle, and reaches a sunken ship where her torch finds
the gold. Rendered on Sam's Mac (Mac lane) and assembled with the Mac's ffmpeg on 23 Oct. Not in release `kino-films`
(on Sam's Mac only). Verdict pending.

Note for new work: three shots; the house default since 23 Oct 17:32 is one fixed view (`cutaway-seasons-loop.md`).

## Folder and every file
`films/cutaway/series/reef-and-wreck/`: `film.json` (20 s, 24 fps, 480 frames, 1280x720 to 1920x1080, 20 spp,
`audio/mix.m4a`), `blender.py` (everything new: rays, palms, boat, wreck, chest, school, turtle, anemones, sea fans,
diver, splash, title), `NOTES.md`, `audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a`.

## How the picture is built (from NOTES)
- Island: sand beach ring, grass, five palms with fronds swaying in gusts, three gulls.
- Boat: white dinghy, blue rim, bench, oar; bobs and rolls with ring ripples.
- Sea: the kit's calm glass water, tint (0.20, 0.80, 0.84), density 1.05, glow 0.035; pale sand bed with strong caustics
  (0.9); a 0.65 m shelf from the island to the floor 0.85 m down. The kit's painted roots off (`soften_roots(amount=0)`).
- Rays (`Rays`): 22 soft additive cards along the sunlight (sun az 135, el 52), billboarded to the camera about their own
  axis, camera and transmission rays only; gain per shot: arrive 0.25, descent 1.7, wreck 1.2.
- Reef: 80 kit corals, 44 swaying anemones in 4 colours, 12 sea fans, 22 rocks, densest on the slope and the near corner;
  the wreck site and the diver's column kept open.
- School: 34 silver-blue fish with yellow tails; at 10.2 s each flips 180 degrees over 0.9 s, delayed by its place, so the
  turn ripples through; tails beat faster in the turn. 5 reef fish (`ex.fish`).
- Turtle: glides the whole film 0.25 m behind the -Y glass, right to left (x 1.75 to -1.4), 2.6 s fore-flipper strokes.
- Diver: black suit, yellow tank and fins, mask, regulator, torch (a spot light that switches on under water); sits on the
  gunwale, rolls back 2.5 rad (4.8 to 5.7 s), splash at 5.35 s (18 droplets, rings), head-first descent kicking, hovers
  10 cm over the sand from 15.9 s, torch arm reaches from 16.5 s; bubble puffs every 1.6 s.
- Wreck: a 1.05 m wooden hull, three-quarter to the camera, listing toward the glass, planks torn out showing 11 ribs, deck
  beams, mast stub, fallen mast and yard, algae green. Chest: brass-banded, lid open, gold with glints, a ruby, an
  emerald, 26 coins on the sand, a warm glow that swells when the torch finds it (16.6 s on).
- Eggs (museum-lit): Roman amphora under the wreck (-Y, u -0.40), ammonite (-Y, u 0.70), trilobite (+X), geode (+X).
- Title "Reef and Wreck", Instrument Sans (`ads/fonts`), a text object at the focus distance, in 0 to 0.7 s, out 1.9 to
  2.5 s.
- Settings: 20 spp, adaptive 0.03, OIDN, 4 bounces, no volumes.

## Shots (and why each cut)
| # | Shot | Time (frames) | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | arrive | 0 to 7 s (0 to 167) | wide three-quarter, 40 mm, f/16, slow push 8.9 to 8.0 m, 7 degree arc | island, boat, the sea cut open; title; the roll-off (4.8 to 5.7 s) |
| 2 | descent | 7 to 13.5 s (168 to 323) | outside the -Y glass, 30 mm, f/6, sinks with the diver lagging about 0.3 s, from a split view to the reef floor | cut on motion: under with her; rays, the school turning, the turtle |
| 3 | wreck | 13.5 to 20 s (324 to 479) | close at sand level through the glass, 38 mm, f/5, slow push 0.22 m | the reward: hull, chest, gold; torch lights the gold |

## Exact render route that made it (Mac lane, then ffmpeg on the Mac)
1. Check rounds 1 to 4 on the Mac lane (21 stills; best: round 3 frames 245 and 470 in `kinoforge-render/out/reef-and-wreck-check3/frames/`).
2. Full render on the Mac lane (LOG 23 Oct: "On the Mac lane: Reef and Wreck, The Gold Mine"). At that time the lane home
   was the iCloud copy `Video Production/kinoforge-render/` (the Samsung X5 drive came later on 23 Oct). A job is a JSON
   file in the lane home's `mac-jobs/` (or `mac-queue/` for the older lane thread), one per frame range, for example:
   ```json
   {"film": "films/cutaway/series/reef-and-wreck", "out": "out/series/reef-and-wreck", "w": 1280, "h": 720, "samples": 20, "start": 0, "end": 48, "device": "METAL"}
   ```
   (`end` is exclusive; name chunks `5-<film>-c00.json`, `5-<film>-c01.json`, so check jobs named `0-<name>.json` run first). The
   job files are in step 4 below. The lane runs
   `blender -b --python harness/blender_render.py -- <film> --out <out> --w --h --fps 24 --start --end --device METAL --samples 20`
   under `caffeinate -i`; frames land in `<out>/frames/%05d.png`; logs and jobs move to `mac-jobs/done/`.
3. Count frames: `ls <out>/frames/[0-9]*.png | wc -l` must be 480 (never count `._` files on the exFAT drive).
4. Assemble with ffmpeg on the Mac (LOG: "assembled with the Mac's ffmpeg: 20.0 s, -16.2 LUFS, preview and sheet
   checked"). The coordinator ran these on the Mac's Linux shell (lane home then `Video Production/kinoforge-render/`, `R` = that folder,
`F` = `$R/films/cutaway/series/reef-and-wreck`), from `Video Production/kino-films/series/`:
   ```bash
   ffmpeg -framerate 24 -i $R/out/series/reef-and-wreck/frames/%05d.png -i $F/audio/mix.m4a -map 0:v -map 1:a \
     -vf scale=1920:1080:flags=lanczos -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k \
     -shortest -movflags +faststart cutaway-series-reef-and-wreck.mp4
   ffmpeg -y -i cutaway-series-reef-and-wreck.mp4 -vf scale=960:-2 -c:v libx264 -crf 24 -c:a aac -b:a 128k cutaway-series-reef-and-wreck-preview.mp4
   ffmpeg -y -i cutaway-series-reef-and-wreck.mp4 -vf "fps=1,scale=384:-1,tile=5x4" -frames:v 1 cutaway-series-reef-and-wreck-sheet.jpg
   ```
   Checks then run: ffprobe duration 20.011 s, `ebur128` integrated -16.2 LUFS, `freezedetect` none. The jobs were ten
   chunks of 48 frames, `5-reef-and-wreck-c00.json` to `c09.json`, out `out/series/reef-and-wreck`, 1280x720 (Gold Mine 720x1280), 20 samples, METAL.
5. Delivered to Sam's Mac `Video Production/kino-films/series/` with its preview and sheet; archived on the Samsung X5
   `KINOFORGE/films/`. To publish it to `kino-films` as well, upload the three files to the release (or re-render with
   rc-render `films.yml`, 20 parts).

## The sound (`audio/make_audio.py`; sources in `films/cutaway/series/SOUND.md`)
Surf (`small_waves_ocean`) and terns (`sea_tern`); water laps the hull at 2.0, 2.9, 3.8, 4.7 s (`splash_small_1`); a boat
creak as she tips back at 4.8 s (`creaking_door_2`) and a rustle of gear at 4.9 s (`cloth`); the splash at 5.35 s
(`splash_big_1`); under water from 5.5 s (`underwater`, `water_bubbles`), first bubbles at 5.8 s and her regulator
exhales every 1.6 s from 6.95 s (`bubbles_burst`); the school turns at 10.05 s (`whoosh_3`); slow strokes through water
(`whoosh_5`); the hull creaks at 13.8 and 16.9 s. Score: key E, cello, glock, harp, viola, violin; turns at the school
(10.2 s) and the gold (17 s, a soft bell); loudest 3 s 10.0 dB under the nature. Measured: -16.16 LUFS, peak -1.98 dBFS,
20.0 s. Rebuild: `python3 films/cutaway/series/reef-and-wreck/audio/make_audio.py`.

## Cost
US$0. Mac (M4, METAL), 1280x720, 20 spp: 4.0 to 7.2 s a frame, about 5.8 s average over 21 frames; 480 frames in about
45 to 50 min. Scene build 0.6 s on the Mac.

## Sam's verdict
Pending.

## Weak spots
The opening wide holds nearly still for about 7 s (STATUS); figures are storybook primitives; the wreck is oversized next
to the diver and the boat is a toy dinghy; the descent shot's top band reads as a pale strip; rays are cards (faint from
above); the torch is a spot light with no volumetric beam.

## To make a new one like it
Keep the sea as the kit's glass water and put the story behind the glass; reserve open sand where the story happens;
rays as billboarded cards with per-shot gain; render on the Mac lane in chunks, then the four ffmpeg commands above.

## Checks before showing Sam
480 frames counted; 20.0 s; 1920x1080; about -16 LUFS; preview and sheet looked at; the splash frames (129 to 134).

## Known traps
Round notes: the chest glow showed as a ball through the glass (lights hidden through the glass), a numpy bool crash in
the splash, bed pebbles off. macOS writes `._` files on the exFAT drive.

## Sources of truth
`films/cutaway/series/reef-and-wreck/NOTES.md`, `blender.py`, `audio/*`, `films/cutaway/series/SOUND.md`,
`harness/mac/go.py`, `docs/PLAYBOOKS/render-on-the-mac.md`, rc-render `films.yml` (join), `docs/LOG.md` and
`docs/STATUS.md` (23 Oct). The code wins if they disagree.
