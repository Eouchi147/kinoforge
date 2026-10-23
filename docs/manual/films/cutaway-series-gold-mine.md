# Film recipe: The Gold Mine (`cutaway-series-gold-mine`)

Cutaway showcase series, film 5. 20 s, 9:16, night. Use it shows: history, adventure, games, mining and construction. A
rocky mountain under stars and a big moon; a miner with a lantern walks into the timber mine; inside the cut face,
lantern-lit galleries, a ladder shaft, an ore cart on rails and miners at work, until the deepest miner's third pick blow
strikes the gold vein in a burst of sparks; the ring wakes the bat colony, which bursts out and pours from the entrance
toward the moon. Rendered on Sam's Mac (Mac lane) and assembled there on 23 Oct. Not in release `kino-films` (on Sam's
Mac only). Verdict pending.

Note for new work: three shots; the house default since 23 Oct 17:32 is one fixed view (`cutaway-seasons-loop.md`).

## Folder and every file
`films/cutaway/series/gold-mine/`: `film.json` (20 s, 24 fps, 480 frames, render 720x1280, delivery 1080x1920, 20 spp,
`audio/mix.m4a`), `blender.py` (everything new), `NOTES.md`, `audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a`.

## How the picture is built (from NOTES and `blender.py`)
- Block `SX = SY = 2.6` m, `DEPTH = 2.2`, summit 1.2 m (tall for 9:16), a flat yard at the front left for the entrance.
- Strata cold blue-greys: turf, scree, slate, quartzite, schist, bedrock; `rock_face` adds mottling and sparse fractures.
- 30 pines (kit cone trees), sparse alpine grass, boulders; moon disc, halo and three drifting cloud wisps (the moon set
  per shot at 40 m from the camera along a fixed direction, so moves never slide it); twinkling one-pixel stars; two bands
  of far ridges.
- Light: moonlight from behind-left (`MOON_COL = (0.62, 0.74, 1.0)`), cool fill, two raking cool lights along the faces;
  10 warm lanterns (`WARM = (1.0, 0.60, 0.26)`) flickering each on its own; a gold flash light. The floor is unlit
  (emission only) so side lights cannot pool on it.
- Mine: timber entrance with a plank roof and a lantern on a post, rails onto the yard; three galleries (boxes behind
  capsule openings) with timber sets every 20 cm; a cribbed ladder shaft; an ore cart (rolls 1.5 to 10.5 s, wheels turn)
  and its pusher; a climber (5.6 to 12.6 s, 18 rungs); two diggers never in step; the gold miner, the vein with 24 nuggets,
  sparks; a cave with 22 stalactites, a clear pool (glass section) and two lanterns; 14 cave bats and 34 outside.
- Eggs under museum spots: the miners' canary hopping in its brass cage, an old strongbox half buried in the scree,
  ammonites (-Y and +X), a trilobite, geodes on each face, the gold vein.
- Title in Archivo (`ads/fonts/Archivo.ttf`), on screen 0.25 to 2.5 s.
- `STRIKES = (8.6, 9.8, 11.0)`; check frames `FRAMES = {night 30, descent_top 168, descent_mid 222, strike 266, bats 300,
  flight 400, end 470}`. SETTINGS: 20 spp, AgX Medium High Contrast, exposure 0.9, max bounces 4, clamp indirect 3,
  adaptive 0.04, OIDN, no volumes (clouds are cards), compositor bloom and vignette.

## Shots (and why each cut)
| # | Shot | Time (frames) | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | night | 0 to 6 s (0 to 143) | three-quarter from front-right (az -60 to -54), 35 mm, eased push 6.9 to 5.0 m toward the entrance | the mountain, the night, the hidden mine; title |
| 2 | descent | 6 to 14 s (144 to 335) | square to the -Y face, 32 mm; eased crane (ease5) from the top gallery to the deepest (6.0 to 10.5 s), then a slow push in (10.5 to 14 s) | the work, the strike, the bats |
| 3 | flight | 14 to 20 s (336 to 479) | low by the yard, looking at the entrance with the moon above (az -112), 30 mm; eased rise and pull back to the whole mountain | the bats leave; closing image |
Cut 1 to 2 follows the miner inside; cut 2 to 3 shows where the bats go (out of the entrance 0.15 s after the cut).

## Exact render route that made it (Mac lane, then ffmpeg on the Mac)
1. Six check rounds on the Mac lane (`out/gold-mine-check1` to `check6`; best stills `check3/frames/00300.png`,
   `check6/frames/00470.png`, `check6/frames/00030.png`).
2. Full render on the Mac lane at about 5 s a frame (LOG 23 Oct). Jobs as for Reef and Wreck, at 720x1280:
   ```json
   {"film": "films/cutaway/series/gold-mine", "out": "out/series/gold-mine", "w": 720, "h": 1280, "samples": 20, "start": 0, "end": 48, "device": "METAL"}
   ```
   (`end` exclusive; ten chunks of 48 frames, `6-gold-mine-c00.json` to `c09.json`.)
3. Count 480 frames (`ls <out>/frames/[0-9]*.png | wc -l`).
4. Assemble on the Mac. The coordinator ran these on the Mac's Linux shell (`R` = the lane home, then
   `Video Production/kinoforge-render/`; `F` = `$R/films/cutaway/series/gold-mine`), from `Video Production/kino-films/series/`:
   ```bash
   ffmpeg -v error -y -framerate 24 -i $R/out/series/gold-mine/frames/%05d.png -i $F/audio/mix.m4a -map 0:v -map 1:a \
     -vf scale=1080:1920:flags=lanczos -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k \
     -shortest -movflags +faststart cutaway-series-gold-mine.mp4
   ffmpeg -v error -y -i cutaway-series-gold-mine.mp4 -vf scale=540:-2 -c:v libx264 -crf 24 -c:a aac -b:a 128k cutaway-series-gold-mine-preview.mp4
   ffmpeg -v error -y -i cutaway-series-gold-mine.mp4 -vf "fps=1,scale=216:-1,tile=10x2" -frames:v 1 cutaway-series-gold-mine-sheet.jpg
   ```
5. Checked: 9:16, 1080x1920, 20.0 s, -16.2 LUFS; delivered to Sam's Mac `Video Production/kino-films/series/`; archived
   on the Samsung X5 `KINOFORGE/films/`.

## The sound (`audio/make_audio.py`; sources in `films/cutaway/series/SOUND.md`)
Night wind and crickets (`campaign_night_1`, `wind_plain`), an owl at 2.0 s (`owl_tawny`), the miner's gravel steps from
0.6 s every 0.55 s (`steps_gravel_1`), the lantern handle creak (`squeaky_steps_1`), cart wheels and rumble from 1.5 s
(`squeaky_barrow_4`, `steam_between_wagons`) and its clunk at 10.48 s (`iron_bar_fall_2`); inside: cave air from 5.8 s
(`cave_1`), lantern sparkle (`candle_sparkle_2`), drips (`drops_1`), ladder creaks every 0.78 s, both diggers' picks
(`hammer_concrete`), bright clicks at 8.61 and 9.81 s and the ringing strike at 11.01 s (`anvil_1`), sparks
(`fire_foley`) and chips; the bats shiver at 11.0 s (`cloth`), squeak and drop at 11.45 s (`bats`), wings burst past the
lens (`flight_*`, `whoosh_4` at 12.6 s), and pour out toward the moon from 14.15 s, thinning. Score: key D minor, cello,
viola, violin and a synthesised Karplus-Strong dulcimer; turn on the gold, 11.0 s; loudest 3 s 10.0 dB under the nature.
Measured: -16.11 LUFS, peak -1.62 dBFS, 20.0 s.

## Cost
US$0. Mac, 720x1280, 20 spp: costliest chunk (frames 262 to 267) 5.5 s a frame; single-frame checks 2.9 to 6.8 s; full
film estimate about 36 min. Scene build 0.5 s on the Mac (3 s on the 2-core chat box).

## Sam's verdict
Pending.

## Weak spots (from NOTES and STATUS)
The title is small over the moonlit trees (STATUS); pale blue-grey faces with shader-only fractures, a plain area between
gallery and vein; primitive 8.5 cm figures (specks in the wides); box galleries with capsule openings; storybook bats
(specks at the end); the strike is small on screen (the flash, bloom, sparks and sound carry it, best frames 266 to 280);
the walking miner is not followed inside and the cart is not unloaded; yard boulders look like snow lumps; no fog or haze.

## To make a new one like it
Warm practicals against cold rock; a gallery cross-section as boxes behind openings; the climax on light and sound; the
moon placed per shot at a fixed far distance. In the house default, one view of the whole lit mountain with the work
alive in every gallery.

## Checks before showing Sam
480 frames; 20.0 s; 1080x1920; strike frames 266 to 280; bats readable at the end.

## Known traps
Round notes: faces read as flat felt (add `rock_face`), fractures too strong read as crazy paving, a black pool (let
light reach its bed), raking lights pooled on the floor (make the floor emission only).

## Sources of truth
`films/cutaway/series/gold-mine/NOTES.md`, `blender.py`, `audio/*`, `films/cutaway/series/SOUND.md`, `harness/mac/go.py`,
rc-render `films.yml`, `docs/LOG.md` and `docs/STATUS.md` (23 Oct). The code wins if they disagree.
