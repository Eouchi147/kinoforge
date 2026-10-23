# Film recipe: Agincourt mud insert B (`cutaway-agincourt-mud-B`)

A 14.164 s Cutaway insert (16:9, no sound of its own) laid frame-exactly into "The Battle of Agincourt" (Battle Map, id
`battle-map-agincourt`) over film frames 2081 to 2420 (cue l10 to l11, film 86.703 to 100.867 s): the French advance on
foot in armour through the mud; through the cut face we see their legs sink to the knee, slower and slower; the woods
squeeze the column into the neck. The turn of the battle. Rendered on GitHub runners after one fix; laid into Agincourt
v2 (rc-render run 39908562175), delivered as `battle-map-agincourt-v2.mp4` (23 Oct). Verdict pending.

Shared world, layout, colours and rules: `docs/manual/films/cutaway-agincourt-mud-A.md` and `agin_mud.py`.

## Folder and every file
`films/cutaway/agincourt-mud/B/blender.py` (the shots), `B/film.json` (id, 14.164 s, 24 fps, render 1280x720, delivery
1920x1080, 64 spp, `audio: ""`); shared `../agin_mud.py`, `../brief.md`, `../NOTES.md`.

## How it is built (differences from A)
- `am.build_world(rain=False)`, `am.light(kit, land, 'after')`: a low warm sun (13 degrees) breaking through behind the
  Agincourt wood into a thin ground haze (`am.haze(density=0.34)`), grey sky, raking light, long shadows; mist 0.28.
- French in carthage blue surcoats with gold hem and disc, steel arms and legs (mud caked below the knee), pointed-visor
  bascinets, poleaxes, two banners (blue, gold border, gold disc, swallowtail); English as in A.
- File 0 of the French front walks exactly on the -Y cut plane, legs straddling it; a boolean against a solid outside the
  face, below the terrain line, cuts their buried parts flush (Manifold solver), so the legs show as sections in the soil.
  Shin deep from the start, knee deep on "knees"; each boot is pulled up as it swings forward (slow strides), a fat mud
  lip rings each leg at the face, and every pulled-out boot leaves a dark hole in the section that closes up behind it.
- Crows on the face edge ahead of the walkers lift on "advanced" (+0, 0.16, 0.30, 0.46 s); three worms; an easter egg
  ammonite in the marl under the French (`am.easter_eggs(shell=(-1.12, -0.140))`).
- `SETTINGS = am.settings(64, 0.30)`: 64 spp, exposure 0.30.

## Shots
- **B1** (86.70 s to 0.15 s before "The woods", after a 1.2 s hold): very low at the -Y face (24 mm at soil level, legs in
  the foreground), a slow track with the French front file walking left to right toward the English; ankle deep on
  "advanced", knee deep on "knees", where the soldier in the middle of the frame stops dead and wobbles and the next bumps
  into him. Cut: change of scale, legs to army.
- **B2** (to 100.87 s): high behind the English stakes, a slow rise; the blue column comes between the two woods, files
  close up in the neck ("squeezed", "packed"); on "swing a weapon" the poleaxes clatter together.

## Exact steps that made it
1. Check stills on runners: last approved round `agin-r7B-f*` (commit 0ee3b60). LOG 22 Oct: "Agincourt insert B fixed
   (front rank on the cut plane, legs sunk to the knee in section, mud rings, holes closing behind each step) and
   dispatched".
2. Render on GitHub runners (parts and run id not recorded; 24 is the playbook value):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/agincourt-mud/B' -f 'inputs[parts]=24' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   Output `cutaway-agincourt-mud-B.mp4` (11,458,106 bytes, seen 23 Oct), silent, 1920x1080.
3. Host join: as in A. The first Agincourt v2 run (39900294683) laid A but not B: in a chain of ffmpeg overlays the second
   overlay's `n` does not count the main frames. rc-render `films.yml` now enables each insert by time with half a frame of
   margin (commit 54c1bb4, tested on all eight boundary frames); the re-run 39908562175 laid both.

## Sound
None of its own: the Agincourt film's mix.

## Cost
US$0. Runner stills about 3 to 4 min a frame for B1, 2 to 3 min for B2 (64 spp, 1280x720). Frame pose 1 to 3 s locally
with the Manifold solver (EXACT was about 40 s a frame).

## Sam's verdict
Pending.

## Weak spots (from NOTES)
God rays are subtle (thin haze, low sun behind the wood; more haze made B1 milky; a separate shafts pass is the next
step); the crows are small in B1; the mud surface does not deform (no ruts; the lips and section holes carry it); rigid
figures (a hip swing and body bob, no bending knees).

## To make a new insert like it
See A's page; for bodies in the cut, straddle the cut plane and boolean the buried parts flush with Manifold.

## Checks before showing Sam
Host boundary frames 2080, 2081, 2420, 2421 after the join; both inserts present (test with two inserts, not one).

## Known traps
Overlay enable by time, not `n` (`docs/LESSONS.md`); EXACT booleans are too slow for many figures.

## Sources of truth
`films/cutaway/agincourt-mud/NOTES.md`, `brief.md`, `agin_mud.py`, `B/*`, `films/battles/agincourt/film.json`, rc-render
`films.yml`, `docs/LOG.md`, `docs/LESSONS.md`. The code wins if they disagree.
