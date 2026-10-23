# Cutaway: art directions (the hook that re-dresses a Cutaway film in another look)

An art direction is one Python module in `films/styles/cutaway/art/<name>.py` that re-dresses a finished Cutaway scene:
materials, world, lights, compositor, or a full numpy re-drawing of the render passes. The scene, the story, the timing
and the words stay the same. Sam asked on 23 Oct 16:34 for "at least ten art directions of the same Cutaway frame (not
only 3D: other textures and effects)", what each is for and how it earns, and one artistic look built around classical
music. Twelve were built and sent to him as a board (meadow frames, full size from the Mac lane); STATUS 23 Oct: waiting
on his pick. After his 17:32 verdict the looks were ported to the seasons loop (the house default).

The twelve: `fable`, `night-glow`, `stained-glass` (jewel looks, `_jewel.py`), `papercraft`, `claymation`, `pixel`,
`risograph` (`_post.py`), `storybook-ink`, `blueprint`, `chalkboard`, `engraving` (line art, `_npr_lines.py`), and
`flat-vector` (a separate 2D web film, not a module). One page each: `cutaway-art-<name>.md`, `cutaway-flat-vector.md`.

## Inputs
A Cutaway film built by the line engine (`films/lib/cutaway/`) or a kit scene that opts in through the adapter (today:
the seasons loop). Blender `bpy` 5.2.2; numpy.

## The contract of an art module
```python
def apply(bpy, film, ctx):             # once, after the scene is built
def frame(bpy, film, ctx, t, shot):    # optional, every frame, after the scene posed everything
```
`film` is the line engine's `Film` (`films/lib/cutaway/engine.py`): `film.built[set]` (`objs`, `hidden`, `kit`, `land`,
`world`, `L`, `rig`), `film.cam.ob`, `film.O.items` (the words, each with `.ob` and `.em`), `film.G`, `film.SETTINGS`,
`film.cw` (the kit), `film.ex` (the cinematic extras). On a kit scene the adapter gives the same names (`kind = 'kit'`,
one set `'main'`).

## How a look is switched on (three ways)
1. **Spec (line films):** `"look": {"art": "<name>"}` in `spec.json`. The engine loads `art/<name>.py` after the build
   and calls `apply`, then `frame` each frame (`engine.py`, `self.art`).
2. **Environment:** `KF_ART=<name>` overrides the spec (line films) or switches the look on (kit scenes with the hook).
   Example: `KF_ART=fable python3 harness/blender_render.py films/cutaway/loops/seasons --w 270 --h 480 --samples 8 --start 100 --end 101`.
3. **Module global (kit scenes):** a `blender.py` that sets `KF_ART_NAME = '<name>'` before running the scene's code.
   This is what `make_seasons.py` writes, so nothing leaks into the environment of a render process that runs several films.

## The adapter for kit scenes (`films/styles/cutaway/art/_adapter.py`)
`KitFilm` wraps a scene built directly on the kit so a look written for the line engine runs on it. In the scene's
`build`, at the very end:
```python
art = globals().get('KF_ART_NAME') or os.environ.get('KF_ART')
if art:
    import importlib.util
    sp = importlib.util.spec_from_file_location('kf_art_adapter', os.path.join(ROOT, 'films', 'styles', 'cutaway', 'art', '_adapter.py'))
    ad = importlib.util.module_from_spec(sp); sp.loader.exec_module(ad)
    S['art'] = ad.attach(bpy, ctx, art, kit=kit, land=L, cam=cam, settings=SETTINGS, strata=STRATA, words=[title_object])
    S['art'].frame(bpy, ctx, 0.0)
```
and the last line of `frame`: `if S.get('art') is not None: S['art'].frame(bpy, ctx, t)`. Without a look nothing
changes: seasons frame 100 at 180x320, 8 spp, rendered before and after adding the hook is identical (max pixel
difference 0, seasons `NOTES.md`). The adapter reads the sun direction from the scene's sun lamp, `L.strata` from the
`strata` argument (for looks that repaint the faces), and the words from `words`. The art `frame` runs after the scene's
own `frame`, so it can re-apply what the scene resets each frame (the seasons loop re-poses its sun every frame).

## Look-board folders (render a look like any film)
- Meadow boards: `python3 films/cutaway/looks/make.py <name> [<name> <name>]` (`reference` = no look) makes
  `films/cutaway/looks/<name>/` with the meadow's `spec.json` plus `"look": {"art": "<name>"}`, its `cues.json`, the
  line's `blender.py` and `film.json` (id `style-cutaway-art-<name>`, no audio). Board frames: 440 (the crane on the
  layers; the full-size Mac board used 470) and 830 (the hero); 768 is the T. rex macro.
- Seasons boards: `python3 films/cutaway/looks/make_seasons.py <name> [<name> <name>]` makes
  `films/cutaway/looks/seasons-<name>/` with a three-line `blender.py` (sets `KF_ART_NAME`, then `exec`s the loop's own
  `blender.py`) and the loop's `film.json` (id `cutaway-loop-seasons-art-<name>`, no audio). Board frames: 40 (spring),
  100 (summer), 260 (winter). All eleven Blender looks have seasons folders (23 Oct).
- Render board frames on runners (`stills.yml`, film = the board folder) or the Mac lane (full size, about 10 to 60 s
  a frame per LOG 23 Oct; runner stills of the reference board took over 30 min and were cancelled).

## Exact steps: write a new look
1. `films/styles/cutaway/art/<name>.py` with a module docstring that states the look, what it changes, where it works
   (line films, kit scenes) and its render cost against the reference.
2. Pick the shared helper that fits: `_jewel.py` (paint shaders, a words view layer, compositor begin and end,
   `under_mask`), `_post.py` (a compositor builder that runs on CPU, `split_overlay` for crisp words in a second scene,
   `array_image`, `walk_principled` and `on_materials`, fibre, grain, fingerprint and tool-mark textures) or
   `_npr_lines.py` (capture passes to EXR, stylize in numpy, then a one-sample words pass).
3. `python3 films/cutaway/looks/make.py <name>` and `python3 films/cutaway/looks/make_seasons.py <name>`.
4. Local checks: meadow at 480x270 or 640x360, 8 spp; seasons at 270x480, 8 spp. Write `films/cutaway/looks/<name>/NOTES.md`
   (the look, what it changes, stills rounds, measured seconds per frame, weak spots, three projects where it is right).
5. Board frames at full size (Mac lane or `stills.yml`); look at every one before showing Sam.

## Known traps (from `docs/LESSONS.md` and the look NOTES)
- `Eggs.finish` cuts the egg openings into the wall and water materials: a look that replaces them must keep the mask
  (`_jewel.under_mask(mat, shader)`), or the eggs vanish behind the wall.
- Words measured in the active view layer: keep them indirect-only in the picture layer, never removed, or the label
  plates are mis-sized.
- Instance prototypes (grass, leaves) are separate materials: repaint them too (`_jewel.scene_materials`), or the plants
  stay dark.
- Hide the loop's haze box in looks that repaint the sky (fable, night-glow do).
- Compositor looks must run the compositor on CPU (`scene.render.compositor_device = 'CPU'`) for GitHub runners.
- The line-art looks hide volumes during the capture (one frame took 19 min on a runner before that change).

## Cost summary (against the reference look)
| Look | Relative cost | Why |
| --- | --- | --- |
| stained-glass | 0.3 to 0.5 x | emission only, no grass blades, 2 bounces |
| fable | 0.6 to 0.8 x, plus 1 to 3 s compositing | emission paint, 3 bounces, no glass |
| night-glow | about 1 x or less | emission, 3 bounces, no glass |
| pixel | about 1 x or less (NOTES; the docstring's 0.25 to 0.33 x assumed a small render) | full-size render capped at 6 spp, plus a few s for the words scene |
| papercraft | about 1 x or a little less | no fog, no rays, simple diffuse |
| risograph | about 1 x | samples capped at 10, plus compositing |
| claymation | 1.1 to 1.3 x | subsurface and heavy bump |
| storybook-ink, blueprint, chalkboard, engraving | 1 x plus 3 to 10 s numpy and about 1 s words pass | same Cycles capture minus volumes |
| flat-vector | 500 to 1000 x faster | 2D canvas in a browser, 0.41 s a frame at 1920x1080 |

## Sources of truth
`films/styles/cutaway/art/*.py` (docstrings), `films/styles/cutaway/art/_adapter.py`, `films/lib/cutaway/engine.py`,
`films/cutaway/looks/make.py`, `make_seasons.py`, `films/cutaway/looks/*/NOTES.md`, `films/cutaway/loops/seasons/NOTES.md`,
`docs/LOG.md` and `docs/STATUS.md` (23 Oct), `docs/LESSONS.md`. The code wins if they disagree.
