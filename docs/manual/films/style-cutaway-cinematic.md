# Film recipe: Cutaway, cinematic hero version (`style-cutaway-cinematic`)

The 12 s style comparison piece Sam asked for on 22 Oct 12:01 (cinema lighting, haze, fog, god rays, living animals and
plants, easter eggs in the soil, interesting angles): the D look's river village at golden hour, relit, in five
pre-planned angles (map, ground, crane, macro, hero). Silent. Rendered on GitHub runners, delivered to Sam's Mac on 23 Oct.

**Sam's verdict (23 Oct 17:32 Toronto): he did not like it** (camera moves, cuts). He liked the seasons loop instead
("barely any camera movement, no cuts, lively world"), which became the base (`docs/SOUL.md`, `films/director/CRAFT.md`).
Keep this film as the record of what NOT to repeat in its cutting; its lighting and life (`extras.py`) remain in use.

## Folder and every file
`films/styles/cutaway/cinematic/`: `film.json` (id, series "Styles", 12 s, 24 fps, render 1280x720, delivery 1920x1080,
`samples: 20`, no audio; note lists stills frames 24, 84, 112, 150, 186, 222, 270), `blender.py` (layout, eggs, animals,
the five shots, per-shot camera, lens, focus and shaft gain), `extras.py` (the reusable library,
`docs/manual/styles/cutaway-cinematic.md`), `NOTES.md`, `board/` (the five stills at 1920x1080).

## How it is built (`blender.py`)
- The D look's river village (`RIVER` path), `STRATA` as time: topsoil, sand, clay, loam (Roman), gravel, ochre, a thick
  pale fossil limestone, dark slate bedrock (the same list became the line's `strata: "time"`).
- `SUN_AZ, SUN_EL = 135, 11`; `ex.cine_light`, `ex.atmosphere` (fog only; haze off), `ex.gobo`, `Shafts`, `edge_spill`,
  `soften_roots`, `ex.finish`.
- Eggs (-Y crane column): mole and nest, pirate chest, Roman amphora, ammonite, T. rex in a dug pocket, trilobite, gold
  vein, a second geode; (+X): hedgehog, ancient well, geode. Museum spot on each.
- Life: roe deer and fawn (heads lift 5.4 and 6.6 s), two rabbits, a fox, a heron (strikes at 7.2 s), three mallards,
  five fish behind the glass, 28 fireflies, 44 petals, three butterflies, four birds; mill wheel, cloud gaps, fog drift.
- `SHOTS`: map 2.0 s, ground 2.5 s, crane 3.5 s, macro 2.0 s, hero 2.0 s. `FOG_GAIN` map 1, ground 0.4, crane 1, macro 1,
  hero 0.7; `SHAFT_GAIN` map 0.35, ground 1, crane 0.8, macro 0, hero 1.
- `SETTINGS`: 48 spp in the file (runners use film.json's 20), AgX High Contrast, exposure 0.1, max bounces 8, volume
  step rate 6, OIDN FAST.

| # | Shot | Time (frames) | Still | Job |
| --- | --- | --- | --- | --- |
| 1 | map | 0 to 2 s (0 to 47) | 24 | top-down with a slow drift and turn: where we are |
| 2 | ground | 2 to 4.5 s (48 to 107) | 84 | low at the block's edge, along the face into the sun, f/4: arrival and scale |
| 3 | crane | 4.5 to 8 s (108 to 191) | 150 (also 112, 186) | down the -Y face from treetops and river glass to the gold: the reveal |
| 4 | macro | 8 to 10 s (192 to 239) | 222 | the T. rex skull, 55 mm, f/4, slow push: the payoff |
| 5 | hero | 10 to 12 s (240 to 287) | 270 | low three-quarter, 28 mm, sun behind; an 8 degree arc slides the sun behind the hero tree so rays burst round its crown |
NOTES: shots run 1.5 to 3.5 s because it is a style reel; a real film holds each idea longer.

## Exact steps that made it
1. Board stills on runners (`stills.yml`, frames 24, 84, 112, 150, 186, 222, 270), rounds r2 to r4 (NOTES cost table).
2. The motion test on runners at 20 samples, 24 parts (LOG 22 Oct: "motion test dispatched at 20 samples (24 parts)"):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/styles/cutaway/cinematic' -f 'inputs[parts]=24' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   Run id not recorded. Output `style-cutaway-cinematic.mp4` (14,741,740 bytes, seen 23 Oct), `-preview.mp4`, `-sheet.jpg`.
3. Reviewed on a contact sheet (12 s, silent) and copied to Sam's Mac as `kino-films/style-cutaway-cinematic.mp4`
   (LOG and STATUS 23 Oct).

## Sound
None (silent test).

## Cost
US$0. Runner stills: close shots 2 to 4 min a frame at 1280x720, 48 spp; wides 10 to 20 min, with large variance (hero
frame 49.7 min on one run, 7.0 min on the next). Board stills at 1920x1080, 48 spp: 6 to 50 min each. Over the 90 s a
frame budget; levers in `docs/manual/styles/cutaway-cinematic.md`.

## Weak spots (from NOTES)
Cost (wides); shafts are cards (faint from the side); storybook animals (deer about 10 cm on a 4 m block); oversized eggs
(a 0.85 m T. rex beside 0.2 m cottages); a stylized toy-like skull; hard-edged hole masks; the ground shot's near face is
out of focus by design; a plain limestone band on +X in the hero; the dark floor around the block in the map shot. And
the verdict: too many cuts and moves for Sam's taste.

## To make a new one like it
Do not, unless Sam asks: use `docs/manual/styles/cutaway-seasons-loop.md`. For a lighting reference, reuse `extras.py`
and this film's sun, fog and shaft gains in a fixed view.

## Checks before showing Sam
The check playbook; length 12 s; silent by design.

## Known traps
A tall haze volume fogged the frame white and showed a seam edge-on: fog only, rays as cards. Runner timing varies by
seven times for the same frame.

## Sources of truth
`films/styles/cutaway/cinematic/NOTES.md`, `blender.py`, `extras.py`, `film.json`, `docs/SOUL.md` (verdict table),
`films/director/CRAFT.md`, `docs/LOG.md` (22 and 23 Oct). The code wins if they disagree.
