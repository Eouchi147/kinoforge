# Film recipe: The River Through Time (`cutaway-series-river-time`)

Cutaway showcase series, film 1 (Sam, 22 Oct 2026 22:18: "a beautiful series, no voice, just nature sounds, to showcase
at least 5 different uses of the cutaway style"). 20 s, 16:9. Use it shows: geology, time-lapse, science explainers. A
stream on a flat grassy block cuts down through the rock beds over ages until a canyon stands; time is shown only by the
sun racing and the light shifting; an ammonite, a fish and a trilobite are bared in the canyon wall as the water passes
them; the last shot is today, golden hour, a tiny hiker on the rim. Rendered on GitHub runners, delivered 23 Oct.

Note for new work: this film cuts three times and moves its camera; Sam's later verdict (23 Oct 17:32) prefers one fixed
view with no cuts (`docs/manual/styles/cutaway-seasons-loop.md`). Its verdict is still pending.

## Folder and every file
`films/cutaway/series/river-time/`: `film.json` (id, 20 s, 24 fps, 480 frames, render 1280x720, delivery 1920x1080,
20 spp, `audio/mix.m4a`), `blender.py` (the whole scene), `NOTES.md` (story, shots, elements, eggs, sound events, cost,
weak spots), `audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a`. Shared: `films/cutaway/series/README.md`,
`SOUND.md`, `audio_kit.py`, `music_kit.py`. Kit and extras imported, never edited.

## How the picture is built (`blender.py`)
- The block is built in the film (the kit's block is static): `SX, SY, DEPTH = 4.0, 3.4, 1.5`; a height field re-shaped
  every frame (a V notch sinking with the river inside the final terraced canyon, `W_RIM = 0.92` m half width at the rim,
  `D_FINAL = 1.03` m deep), so every point of the final wall is bared once and stays; hard beds stand as cliffs, soft beds
  as slopes; rock banded by world height (`mat_land`) so the canyon walls and the cut face share the same beds; a water
  box that sinks with the floor.
- Sky and sun (`Sky`): the sun turns 2 extra full times (peak about 140 degrees a second), warms when low; cloud-gap
  shadows (`rt_gobo`) drift and race; canyon mist sheets (`rt_mist`); museum spots fade in over 0.8 s on each fossil.
- Life: deer (heads lift 4.2 and 17.2 s), birds, butterflies, petals, wind, a 7.5 cm hiker with a red pack.
- Title "The River Through Time", Instrument Sans (`ads/fonts/InstrumentSans.ttf`), a Blender text object on the camera,
  in 0 to 0.6 s, out 1.9 to 2.5 s. Nothing else written.
- SETTINGS: 20 spp, adaptive (threshold 0.03 per NOTES), OIDN FAST prefilter, AgX High Contrast, exposure 0.1, max
  bounces 4 (diffuse 1, glossy 1, transmission 4), no volumes (haze is cards), no motion blur.

## Shots (and why each cut)
| # | Shot | Time (frames) | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | then | 0 to 6 s (0 to 143) | wide three-quarter, 35 mm, f/16, slow push 6.3 to 5.8 m, 4 degree arc | where we are; time races from 2.6 s, cutting from 3.2 s |
| 2 | ages | 6 to 14 s (144 to 335) | at the cut face looking into the canyon's west wall, 26 mm, f/8, cranes down 0.5 m with the water | change of scale: the fossils bared one by one |
| 3 | today | 14 to 20 s (336 to 479) | low three-quarter into the setting sun, 32 mm, f/11, push 4.4 to 3.5 m, 5 degree arc | change of time: the canyon now, a person for scale |

Timing: fossils bared at 7.99 (ammonite), 11.31 (fish), 12.11 s (trilobite); cutting steady from 6.2 s, eases out 12.2 to
13.8 s; sun stops racing at 14.4 s; hiker appears 14.0, walks 14.6 to 18.2, turns to look 18.2 to 19.4 s. Check frames:
30, 120, 160, 230, 290, 330, 360, 400, 470, 479; best still 300 (all three fossils).

## Exact render route that made it
1. Check stills on the Mac lane (5 rounds, see NOTES "Render cost").
2. Full film on GitHub runners (LOG 23 Oct: River Through Time "dispatched to GitHub runners (20 parts) to spread the load"):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/series/river-time' -f 'inputs[parts]=20' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   Run 39894366759 (dispatched 03:19 UTC, success 04:53 UTC on 23 Oct; the LOG lists runs 39894366759, 39895728062,
   39896034330 for River, Volcano and City in that order, and the run end times match the release asset times). The join lays `audio/mix.m4a`, scales to 1920x1080 and publishes
   `cutaway-series-river-time.mp4`, `-preview.mp4`, `-sheet.jpg`, `-poster.jpg` to release `kino-films`.
3. Checked: 20.0 s, no frozen frames, about -16.2 LUFS (STATUS), reviewed on a 1 fps contact sheet; copied to Sam's Mac
   `Video Production/kino-films/series/` and sent to him (LOG 23 Oct); archived on the Samsung X5 `KINOFORGE/films/`.

Expected assets (seen 23 Oct): `cutaway-series-river-time.mp4` 25,606,032 bytes, with preview, sheet and poster.

## The sound (`audio/make_audio.py`, details in `films/cutaway/series/SOUND.md`)
Real recordings from the BigSoundBank CC0 bank (rc-render release `sfx-bank`) placed on the NOTES event table (`EV`):
morning brook (`small_stream_4`), forest bed, wind all through (`wind_plain`); the brook grows into a river
(`mountain_stream_1`); a rockfall at 9.5 s and grit as each fossil is bared (`fall_of_stone` at 7.99, 11.31, 12.11 s);
today: evening birds, a raven at 15.6 s (`crows_1`), the hiker's gravel steps every 0.3125 s from 14.91 to 18.04 s
(`steps_gravel_1`). Score (`music_kit`, VSCO-2 CE samples): slow strings and harp in D, chords D, Bm7, G, A sus4 to A,
D; the turn as time slows, 12.2 to 14.4 s; its loudest 3 s sit 10.0 dB under the nature's. Measured: -16.1 LUFS, peak
-2.28 dBFS, 20.0 s, AAC 256k 48 kHz.
Rebuild: `SFX_BANK=<folder of FLACs> SCORE_SAMPLES=<VSCO-2 CE folder> python3 films/cutaway/series/river-time/audio/make_audio.py`
(without `$SFX_BANK` the kit uses `~/.cache/kinoforge/sfx-bank` or downloads `sfx-bank.tar` once; without samples the
score engine synthesises). About 10 s.

## Cost
US$0. Mac checks at 1280x720, 20 spp: 2.9 to 6.3 s a frame idle, up to 16.3 s when the lane was busy (whole film about
30 min idle, up to 2 h busy). Runner time for the film: not recorded.

## Sam's verdict
Pending (STATUS 23 Oct: "waiting on his verdict").

## Weak spots (from NOTES and STATUS)
River water reads as a pale grey trench more than water (STATUS); carving is a height-field morph, not erosion (smooth
walls, no talus or overhangs); fossils oversized (19 cm ammonite in a 1 m canyon); the fish is thin; grass storybook-tall
against the 11 cm hiker; time-lapse animals move in real time and sit mostly out of the middle shot; a soft visible
horizon line behind the canyon in the last shot.

## To make a new one like it
1. Copy the folder; keep the three-act shape (then, ages, today) only if Sam asks for cuts; otherwise one fixed view.
2. Write the event table in NOTES first (time, event, sound idea); keep fossil times printed by `build`.
3. Check 6 frames on the Mac lane or `stills.yml`; render with `films.yml` 20 parts; sound from the event table.

## Checks before showing Sam
`docs/PLAYBOOKS/check-before-showing-sam.md` (20.0 s, 1920x1080, about -16 LUFS for these quiet films, no freezes), a
contact sheet, the three moving stretches.

## Known traps
The kit's static block cannot carve: re-shape the top yourself each frame (numpy is cheap). The fanless Mac throttles.

## Sources of truth
`films/cutaway/series/river-time/NOTES.md`, `blender.py`, `audio/make_audio.py`, `audio/mix.json`,
`films/cutaway/series/README.md`, `SOUND.md`, `docs/LOG.md` and `docs/STATUS.md` (23 Oct). The code wins if they disagree.
