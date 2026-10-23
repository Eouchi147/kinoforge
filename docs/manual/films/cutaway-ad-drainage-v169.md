# Film recipe: Sample trade ad, drainage and landscaping, 16:9 (`cutaway-ad-drainage-v169`)

The 16:9 delivery of the 15 s sample trade ad for the INVENTED business "Fieldstone Drainage and Landscaping" (marked
Sample, no phone, no website). Same scene, words, music and beats as the 9:16 version; only the aspect, the camera keys
and the title-safe box differ. Full recipe of the shared scene: `docs/manual/films/cutaway-ad-drainage-v916.md`.
Rendered on GitHub runners and copied to Sam's Mac (23 Oct). Verdict pending.

## Folder and every file
`films/cutaway/ads/drainage/v169/`: `blender.py` (picks `'16:9'`, calls `ad.build` and `ad.frame` from `../ad.py`),
`film.json` (id `cutaway-ad-drainage-v169`, 15 s, 24 fps, render 1280x720, delivery 1920x1080, 48 spp,
`audio/mix.m4a`), `audio/mix.m4a` and `audio/score.json` (same music as v916, written by `../music.py`). Shared:
`../ad.py`, `../music.py`, `../score_plan.json`, `../fonts/`, `../brief.md`.

## What differs from 9:16 (from `ad.py`)
- Safe box: `SAFE_169 = (0.05, 0.95, 0.06, 0.90)` (title-safe for 16:9); `build()` fails the render if a word leaves it.
- Camera keys `CAM['16:9']` at 0, 3, 6.5, 11.5, 15 s (azimuth, elevation, distance factor, target): (-44, 17, 1.06),
  (-40, 14, 0.97), (-12, 4, 0.34, target at the +X face by the trench), (-27, 16, 0.54), (-38, 19, 1.12); base camera
  `az -44, el 17, lens 50, fill 0.78, top_extra 0.62`.
- Everything else (beats, words, timings, robin, ball, music) is identical.

## Exact steps that made it
1. Music: `python3 films/cutaway/ads/drainage/music.py` writes both folders' `audio/mix.m4a` (-14.03 LUFS).
2. Local look: `python3 harness/blender_render.py films/cutaway/ads/drainage/v169 --w 640 --h 360 --samples 16 --start 200 --end 201`.
3. Push; render on GitHub runners (parts and run id not recorded; playbook value 24 for Blender):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/ads/drainage/v169' -f 'inputs[parts]=24' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
4. Checked (15 s, -14.2 LUFS) and copied to Sam's Mac (LOG 23 Oct).

Expected assets (seen 23 Oct): `cutaway-ad-drainage-v169.mp4` 13,007,715 bytes, `-preview.mp4` (960 wide), `-sheet.jpg`.

## Sound
Music only, from the free score engine (see the v916 page): F ionian, flute solo, a swell at 6.5 s as the fix starts, a
harp chime at 11.55 s on the sun, 2.4 s fade, -14 LUFS.

## Cost
US$0. Per-frame time not recorded.

## Sam's verdict
Pending.

## Weak spots
The framing crops the house at the left edge; the puddle reads weakly in stills (LOG 22 Oct).

## To make a new one like it
Make both aspects from one scene file: a three-line `blender.py` per delivery that passes the aspect, a camera key table
per aspect, and a safe box per aspect checked in `build()`.

## Checks before showing Sam
As v916: length, loudness, the words inside the safe box, Sample on the end card.

## Known traps
Keep both aspects in one `ad.py`: a fix made in one delivery folder would not reach the other.

## Sources of truth
`films/cutaway/ads/drainage/ad.py`, `v169/*`, `music.py`, `brief.md`, `docs/LOG.md` (22 and 23 Oct). The code wins if
they disagree.
