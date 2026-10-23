# Cutaway: the cinematic extras (golden light, fog, god rays, easter eggs, animals)

`films/styles/cutaway/cinematic/extras.py` is the second Cutaway library: everything Sam asked for on 22 Oct 12:01
("cinema lighting (haze, fog, god rays), animated fauna and flora, easter eggs in the soil (dino bones, gold ore),
interesting angles"). It sits next to the kit (`cutaway.md`), never edits it, and is imported by every series film, the
line engine and the art directions. The same folder holds the comparison film `style-cutaway-cinematic`
(`docs/manual/films/style-cutaway-cinematic.md`), which Sam did NOT like on 23 Oct 17:32 for its camera moves and cuts.
Use the extras for light, life and eggs; do not copy that film's five-angle cutting (see `cutaway-seasons-loop.md`).

## Inputs
The kit, Blender `bpy` 5.2.2, a built `Land`.

## The API (`extras.py`)
```python
import cutaway as cw, extras as ex
rig  = ex.cine_light(kit, land, sun_az=-168, sun_el=8)          # warm low sun, cool fill, rim, sky dome, hazy floor
atm  = ex.atmosphere(kit, land)                                   # haze + ground fog pooling in the valley (one bounded volume)
ex.gobo(kit, land, rig['sun_dir'])                                # cloud gaps: drifting shadow card, invisible to the camera
eggs = ex.Eggs(kit, land); eggs.dino('-Y', u, z); eggs.finish()   # easter eggs in the cut face (+ museum lights)
ex.deer(kit, land, x, y, yaw)                                    # also ex.rabbit, ex.fox, ex.heron, ex.ducks, ex.fish,
                                                                  # ex.fireflies, ex.petals, ex.butterflies (see their docstrings)
ex.finish(bpy, W, H)                                              # compositor: bloom + vignette
cam = ex.ShotCam(kit); cam.set(pos, target, lens, focus, fstop)
```
Also: `Shafts` (art-directed god-ray cards, billboarded to the camera about their own axis, seen by camera rays only;
`Shafts.around` places beams round a tree crown), `Face` (face coordinates: `u` along the face, `z` height, `d` depth
into the block; face `-Y` has u = x, `+X` has u = y), `bowl` and `half_tube` (hollows closed from inside, no booleans),
`mat_pbr` (thin-film nacre, coat, glitter facets, emissive flecks), `ripples`, `soften_roots` (fewer, finer painted
roots on a film's own wall material), `edge_spill` (warm spot grazing the top layers of a face), `time_value`.
Everything that moves is a pure function of `t`, registered with `kit.on_frame`.

## The lighting recipe (from `cinematic/NOTES.md`)
- Key: warm sun (1.0, 0.66, 0.38), strength 6, angle 1.2 degrees, az 135, el 11, behind the block from every camera.
- Fill: a large cool disk area light on the camera side (0.6 x 900 W) and a dim blue sky ambient (0.2): the cut faces
  sit in cool shade, readable.
- Rim: a warm area light at sun az + 62 degrees.
- Museum lights: each egg gets a warm spot (2 to 5 W, 30 to 50 degree cone, soft blend) 0.4 to 0.75 m out from the face.
- Sky: camera rays see a golden-hour dome (orange horizon toward the sun, lilac away, deep blue zenith, sun disc and halo);
  other rays see a dim cool ambient. The floor fades into the horizon colour (no hard edge).
- Atmosphere: one thin volume slab from the water level to 0.25 m: ground fog in the low ground (density 7, falling off
  over 0.16 m) and a mist layer on the water (4D noise, wind 3.5 cm/s), anisotropy 0.7, step rate 6, 128 steps. The
  general `haze=` term is OFF: at 0.6, 0.35 and 0.12 it fogged the frame white or showed a seam.
- God rays: `Shafts` cards (12 canopy beams, 10 around the hero tree); gain per shot.
- Finish: AgX High Contrast, exposure 0.1, bloom threshold 1.2 strength 0.22, vignette 0.26, depth of field per shot.

## Easter eggs (by depth: recent near the top, deep time at the bottom)
`Eggs` kinds used across films: mole in its tunnel and nest, pirate chest, Roman amphora with coins, ammonite (nacre),
T. rex skeleton in a dug pocket, trilobite, gold vein (quartz, 22 nuggets, 260 flecks), geodes (amethyst glow),
hedgehog asleep, ancient well cut in half with a swaying bucket. Hollows are a transparent mask on the wall material in
face coordinates plus a bowl or half-tube mesh inside: cheap, and the cut stays clean. `Eggs.finish()` cuts the openings
into the wall and water materials: an art direction that replaces those materials must keep that mask (`cutaway-art.md`).

## Animals and small life
Roe deer and fawn (lift heads at `lift_at`), rabbits (hop, sit, sniff), fox (diagonal-pair trot), heron (one strike),
mallards with ring ripples, fish behind the glass, fireflies, petals and leaves, butterflies, birds; the mill wheel turns;
the cloud gaps and fog drift. All primitives (ellipsoids, tubes), storybook-sized so they read on a phone.

## Exact steps (use in a film)
1. In `blender.py`, add both paths and import:
   `for p in (os.path.join(ROOT, 'films/styles/cutaway'), os.path.join(ROOT, 'films/styles/cutaway/cinematic')): sys.path.insert(0, p)`
   then `import cutaway as cw, extras as ex`.
2. Build the land with the kit, then `rig = ex.cine_light(kit, land, sun_az, sun_el)`, eggs (`ex.Eggs`), animals, `ex.finish(bpy, W, H)`.
3. Set fog and shaft gains per shot (the cinematic film keeps `FOG_GAIN` and `SHAFT_GAIN` dicts per shot name).
4. Check with rc-render `stills.yml` (the cinematic film's check frames: 24, 84, 112, 150, 186, 222, 270).

## Cost (free 4-core runners, 22 Oct; large runner variance)
Close shots of the face (crane, macro) about 2 to 4 min a frame at 1280x720, 48 spp; wide shots that see the living top
and the fog 10 to 20 min (one hero frame took 49.7 min on one run and 7.0 min on the next). Locally, removing one thing
at a time: fog volume -25 %, glass water -14 %, shafts -7 %, grass -9 %. Levers in order: 16 to 24 spp (OIDN holds),
`cw.apply_cycles(bpy, fast=True)`, hide `ex_atmos` (fog) in wide shots, render wides at 960x540, drop house glow lights.
The series films skip volumes altogether (haze, mist and smoke as cards) and run at 3 to 7 s a frame on the Mac.

## Best uses
Any Cutaway film that wants golden light, living animals and museum-lit surprises; the line engine builds every set with it.

## Alternatives
Card-only haze (no volume): what the series films and the seasons loop do; cheaper and never fogs the frame.

## Checks before showing Sam
Eggs readable at phone size in the shot that names them; rays visible only where the camera looks toward the sun;
no seam where a fog box is seen edge-on.

## Known traps
- Full haze volume fogs the frame; rays must be cards (`docs/LESSONS.md`).
- Hole masks are hard-edged: a thin highlight line where a tunnel wall meets the face at extreme close range.
- Eggs are oversized for readability (a 0.85 m T. rex next to 0.2 m cottages); at hero distance they are glowing shapes.
- The T. rex skull is stylized and toy-like (head thrown back reads as broken in Under the City).

## Sources of truth
`films/styles/cutaway/cinematic/extras.py`, `cinematic/blender.py`, `cinematic/NOTES.md`, `docs/LOG.md` 22 Oct
("Cinematic Cutaway done"), `docs/SOUL.md` verdict table. The code wins if they disagree.
