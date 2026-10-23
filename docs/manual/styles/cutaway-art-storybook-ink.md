# Cutaway art look: storybook-ink (children's picture book: ink and watercolour)

The Cutaway as a picture-book page: ink outlines of varied weight, watercolour washes that pool at the lines, warm paper
showing through, light pencil hatching in the shadows, slightly desaturated warm colour; a wet-in-wet sky, grass as a
smooth green band, glass water as a teal wash. Board sent to Sam on 23 Oct; his pick is pending. The module docstring
still says "work in progress"; the NOTES record it as built, tuned and run on runners.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/storybook-ink.py`,
helpers `films/styles/cutaway/art/_npr_lines.py` (numpy only, no scipy).

## How it renders (the line-art pipeline, two renders per frame inside the look's `frame()`)
1. CAPTURE: Cycles renders the real scene (the film's own samples) with the words hidden; a compositor File Output writes
   float EXR passes (Combined, Diffuse Colour, Normal, world Position, Depth, Material Index, Object Index, AOVs) to a
   temp folder; they are read back as numpy arrays. Volumes (haze, light-shaft objects) are hidden during the capture.
2. STYLIZE: `stylize(P, info)` in plain numpy: material classes (`GROUPS`: strata, top, grass, leaf, water, rock, build,
   bark and plant, find, animal), light relative to its own neighbourhood (a spotlight is a glow, a cast shadow is a
   shadow), pen weight from camera distance (closer is bolder), washes, hatching locked to the world (Position pass),
   paper fixed to the screen. Colours: ink (0.22, 0.13, 0.10), paper (0.968, 0.930, 0.835), pencil, sky top and low,
   grass, leaf, water (constants in the module).
3. FINAL: the harness render draws only the words over that picture (Alpha Over), about 1 s.

## Exact steps (apply it)
1. Line film: `"look": {"art": "storybook-ink"}`, or `KF_ART=storybook-ink`.
2. Seasons board (exists): `films/cutaway/looks/seasons-storybook-ink/`; checked at 360x640 with `KF_ART` (NOTES).
3. Meadow board (exists): `films/cutaway/looks/storybook-ink/`; frames 440 and 830.
4. Runner stills (done for this look): rc-render `stills.yml`, 640x360, 8 spp, frames 440 and 830, tags
   `looks-storybook-ink-r1` (run 40025708724) and `looks-storybook-ink-r2` (run 40028913182).

## Cost per frame
Runner, 640x360, 8 spp: both r2 jobs done in about 87 s including about 60 s of setup, so about 25 s a frame (before
volumes were hidden from the capture, frame 440 took 19 minutes on a runner). Local 2-core box, 1280x720, 8 spp: Cycles
capture about 50 s (hero) to 110 s (frame 440), numpy 2 to 7 s, words pass about 1 s. Full size on the Mac lane about
15 s a frame (NOTES).

## Best uses (from NOTES)
1. A children's book publisher or parenting brand explaining nature or the body (how a seed grows, what lives under a garden).
2. A museum or science centre family trail: "what is under our feet" panels and short films.
3. A school or library reading-week film told over a soft hand-made picture.

## Weak spots
Paper texture stays put on the screen while the camera moves (as paper does) but screen-space noise can shimmer between
frames; pixel-thin lines can alias on far objects (they fade out below a minimum spacing); grass and tree interiors are
simplified on purpose. The seasons loop's fixed view avoids most of the motion risk.

## Alternatives
`fable` (paint), `chalkboard`, `engraving`, `blueprint` (same pipeline).

## Checks before showing Sam
Judge the hero at frame 830 (768 is the dinosaur macro; the hero shot starts at 790).

## Known traps
Hide volumes during the capture (19 min a frame otherwise). The passes must be read from EXR with bpy (no extra library
on runners).

## Sources of truth
`films/styles/cutaway/art/storybook-ink.py`, `_npr_lines.py`, `films/cutaway/looks/storybook-ink/NOTES.md`. The code wins
if they disagree.
