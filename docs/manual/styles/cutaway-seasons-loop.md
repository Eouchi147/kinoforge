# Cutaway: the seasons loop grammar (THE HOUSE DEFAULT for new Cutaway films)

Sam, 23 Oct 2026, 17:32 Toronto: he did not like the cinematic test (camera moves, cuts) and liked the seasons loop:
"barely any camera movement, no cuts, lively world". Recorded in `docs/SOUL.md` (verdict table) and
`films/director/CRAFT.md` ("The seasons loop is the base for Cutaway work: one fixed view, the world changes and lives in
front of it"). So every new Cutaway film starts from this grammar unless Sam asks otherwise. The reference film is
`films/cutaway/loops/seasons/` (`cutaway-loop-seasons`, `docs/manual/films/cutaway-loop-seasons.md`): 12 s, 9:16, one
pond cut open on the front face, a year passing in a seamless loop.

## The grammar (what makes it the house default)
1. **One fixed view.** A high three-quarter camera (az -48, el 30, lens 55) framing the whole block, the block spanning
   0.85 of the frame width and sitting low (aim 0.32 m above the top). The only move is a very slow sway: 3 degrees of
   azimuth on one sine over the whole loop, so it returns to its start. No cuts, no cranes, no pushes.
2. **The world tells the story.** Change happens in front of the camera, each with a reason we can see: light (sun
   height, colour, angle), colour (ground, grass, leaves, water tint), growth and decay (grass height, flowers on and off,
   lily pads growing and gone, blossom, canopy density, roots in the face), weather (snow, ice from the banks, meltwater,
   mist, ground fog), and life (birds leave and return, a duck, fish behind the glass, a squirrel caching acorns, a robin
   leaving tracks, a frog going down to sleep in the mud).
3. **A surprise in the cut face** that makes people watch twice: the frog's winter chamber in the mud, an ammonite, a gold
   vein, the acorn cache.
4. **A living world at every moment** (CRAFT section 5): wind in grass and trees, water ripples and caustics, at least
   three layers of motion.
5. **Seamless when it is a loop:** every season curve is periodic (spring on both sides of the seam), every motion repeats
   on the loop (`cw.Kit(loop=12)`), the camera sway is a full sine; sound is folded to an exact loop.
6. **Words set in code, few:** one title ("One pond. One year.", Inter Tight SemiBold, fixed to the camera in the sky,
   on for the whole loop).

## Inputs
The kit (`cutaway.md`), Blender `bpy` 5.2.2, numpy, the free score engine (`films/lib/score/`) for sound.

## How the reference is built (files in `films/cutaway/loops/seasons/`)
| File | Job |
| --- | --- |
| `szworld.py` | Pure numpy, no bpy: the land (`S = 3.2` m block, `DEPTH = 1.25`, water level `LV = -0.05`, a pond cut open on the -Y face fed by a stream from the back, mounds), `field(x, y)` (height, signed distance to water, grass and sand weights, depth), and the year: `LOOP = 12.0`, `kc(t, keys)` (periodic keyframes with smoothstep), `weights(t)` (spring, summer, autumn, winter colour weights that sum to 1), `blend(t, vals)`, `win(t, a, b)`, and `CURVES` (snow, ice, wet, canopy density, blossom, grass height, litter, roots, caustics, frog burrow and tunnel, birds, mist, fog) |
| `szmats.py` | Season-driven materials: every season-dependent colour or amount is a Value, RGB or ColorRamp node that `Drive` sets each frame (the kit bakes a season at build time; this file makes the year turn inside one render). `patch_snow`, `mat_top`, `mat_strata` (with the frog burrow and the acorn cache), `mat_water`, `mat_ice`, `mat_grass`, `mat_leaf`, `mat_bark`, `mat_frog` |
| `szlife.py` | Atmosphere (haze box with god rays when the sun is low, spring mist, autumn ground fog), the duck, fish, squirrel, robin and its tracks, the acorn cache, the ammonite (+X face), the title |
| `blender.py` | `build`: the kit block reshaped from `szworld.field` (one source of truth for heights), frogs, materials, `populate` (grass, flowers, 14 trees at fixed spots, boulders, bank and bed stones, weed, reeds, lily pads), ice, falling leaves, snow (1,500 flakes), birds, dragonflies, `cw.studio` backdrop, the camera; `frame`: drives every colour and curve from `t`, sways the camera, moves sun height, colour, energy and angle, grows and shrinks things, poses all life. Opt-in art hook at the end (`cutaway-art.md`) |
| `audio/make_audio.py` | The exact 12 s loop of sound (below) |

Timeline: 0 to 3 s spring (thaw ends, blossom, frog swims up, roots grow); 3 to 6 s summer (full green, warm bright
pond, caustics, dragonflies); 6 to 9 s autumn (leaves turn, fall and sink past the glass, the frog digs in, birds leave);
9 to 12 s winter (snow, ice from the banks, the frog asleep in its chamber), then the thaw back into spring.

Settings: 40 spp, denoise ACCURATE prefilter, AgX Base Contrast, exposure 0.2, max bounces 8, no volume bounces, clamp
indirect 6, adaptive min samples 16, `transparent_max_bounces = 64` (cut-out canopies stack many layers).

## Exact steps: a new film on this grammar
1. Copy the reference folder: `cp -r films/cutaway/loops/seasons films/cutaway/<group>/<id>` (keep `szworld.py`,
   `szmats.py`, `szlife.py`, `blender.py`, `audio/make_audio.py`; delete `audio/mix.*` and `__pycache__`). Fix the `ROOT`
   depth in `blender.py` (four `..` from `films/cutaway/loops/seasons`) and in `audio/make_audio.py`.
2. `film.json`: new `id` and `title`, `duration` and `frames` (= duration x 24), `loop: true` only if it loops, format
   (720x1280 render and 1080x1920 delivery for 9:16; 1280x720 and 1920x1080 for 16:9), `samples` 40 (or 20 to save time),
   `audio: "audio/mix.m4a"`.
3. Write the story as a table first (time, what changes, the reason we can see), like `brief.md`. One place, one view.
4. In `szworld.py`: the land (`S`, `DEPTH`, `LV`, `STREAM`, `pond_sd`, `land_h`) and the timeline (`LOOP` = the film
   length; `weights`; `CURVES`). Keep every curve periodic if it loops; for a film with an end, let the curves end.
5. In `blender.py`: `AZ0`, `SWAY`, `EL`, `LENS`, `WIDTH`, `TZ`, `SUN_AZ`, `STRATA`, `SEASON` (per-phase colours and
   light), `GRASS`, `LEAF`, `TREES` (fixed spots), and what `populate` scatters. Keep the camera fixed (`SWAY` 3 degrees
   or less).
6. In `szlife.py`: the life and the surprise in the face, each a pure function of `t`; change the title text in
   `build_title` (words set in code: no dash, no three-dot ellipsis).
7. Check locally (2-core box): `python3 harness/blender_render.py films/cutaway/<group>/<id> --w 270 --h 480 --samples 8 --start 100 --end 101`.
   For a loop, render the last frame and frame 0 and compare (the reference's seam is smaller than a normal frame step).
8. Sound: edit `audio/make_audio.py` (chords per phase, ambience events per phase) and run
   `python3 films/cutaway/<group>/<id>/audio/make_audio.py` (writes `audio/mix.m4a` and `mix.json`; `mix.wav` stays local).
9. Push; runner stills (`stills.yml`, at most 8 frames, one per phase); then render with rc-render `films.yml`:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/<group>/<id>' -f 'inputs[parts]=12' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   (the reference used 12 parts), or the Mac lane.
10. Check (`docs/PLAYBOOKS/check-before-showing-sam.md`) and deliver with weak spots named.

To dress the result in an art direction (fable, night-glow and the others): `python3 films/cutaway/looks/make_seasons.py <name>`
makes `films/cutaway/looks/seasons-<name>/` (see `cutaway-art.md`); for your own film, set `$KF_ART=<name>` or a module
global `KF_ART_NAME` before its `blender.py` runs.

## The sound recipe (exact loop)
`audio/make_audio.py`: every note and event starts inside `[0, LOOP)` and is rendered on a 3 x LOOP buffer with its full
tail and reverb; the buffer is folded (0 to 12 + 12 to 24 + 24 to 36), which is exactly what a looping player plays. Noise
beds are periodic in the frequency domain (`pnoise`); the limiter runs on three copies and keeps the middle. Score: the
free engine's Composer voices (string pad, harp-like pluck, hall reverb), D major, one chord per season: spring D(add9),
summer G(add9), autumn Bm, winter A(sus4), back to D at the seam. Ambience synthesised in the script for what we see:
wind all year (a whistle in winter), leaves rustling in spring and summer, birds in spring and summer and on the thaw,
frogs in spring, leaves dropping on the pond in autumn, ice creaks in winter. Measured (`mix.json`): 12.0 s, -18.02 LUFS,
peak -2.0 dBFS, seam jump 0.040 against a 99.9th-percentile step of 0.152.

## Cost
The reference rendered on GitHub runners (`films.yml`, 12 parts, 22 Oct); per-frame time not recorded. The art looks on
it: 10 to 35 s a frame at 270x480, 8 spp on the 2-core chat box (look NOTES).

## Alternatives
- The spec line with ONE shot and a near-still camera (`cutaway-line.md`), when a preset set is enough.
- The flat-vector 2D page (`cutaway-flat-vector.md`) when speed matters more than depth.

## Checks before showing Sam
No cut, no visible camera move beyond the sway; every change has a visible cause; seam check for loops; three layers of
motion at every moment; the surprise in the face readable at phone size; numbers per the check playbook.

## Known traps
- The kit bakes a season into materials at build time: drive season colours through nodes each frame (`szmats.Drive`).
- Snow cover peaks 10.5 to 11.15 s: frame 230 (9.6 s) is still mostly autumn; judge winter at frame 260.
- Heights must come from one function (`szworld.field`), or plants, leaves and ice float or sink.
- Cut-out canopies need `transparent_max_bounces` high (64).
- The brief planned a 90 degree orbit; the build uses a 3 degree sway (the code wins).

## Sources of truth
`films/cutaway/loops/seasons/` (`brief.md`, `NOTES.md`, `blender.py`, `szworld.py`, `szmats.py`, `szlife.py`,
`audio/make_audio.py`, `audio/mix.json`, `film.json`), `docs/SOUL.md` section 3, `films/director/CRAFT.md` (verdicts),
`docs/STATUS.md`. The code wins if they disagree.
