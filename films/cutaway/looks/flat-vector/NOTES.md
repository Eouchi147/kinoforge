# Cutaway look: flat-vector (pure 2D, no Blender)

23 Oct 2026: flat-vector look board built (index.html + scene.js, canvas 2D in code); board frames 440, 470, 768, 830 rendered
locally with harness/render.cjs in Chromium; US$0; no runner used (stills.yml not dispatched, see "Runs").

## The look
The meadow example as a side-on cross-section in clean flat vector shapes, like a premium science explainer: a floating
block of land with a thin top strip and a darker right face (a light oblique hint so it reads as a block cut out of the
world), the eight "time" strata of `presets.STRATA_TIME` in a limited palette with subtle vertical gradients, one mark
vocabulary per layer (roots, sand grains, clay streaks, loam crumbs, gravel pebbles, ochre dashes, limestone shells and
bedding bands, bedrock cracks), the river cut as glass, a dusk-gold sky with flat hills, film grain and a soft vignette.
Labels are crisp thin type (Inter, bundled) on ink pills with a hairline leader and a target ring, set in code.

Same content as `films/cutaway/meadow`: big tree and 14 smaller trees (round, poplar, pine), river with lilies, reeds,
ducks, heron and fish, five village houses, the mill with a turning wheel, bridge, three lamps, boulders, flowers. Finds:
mole tunnel and nest, chest leaking gold, Roman amphora with shards and coins, ammonite, T. rex skeleton, trilobite, gold
seam in a quartz vein, hedgehog in a leaf burrow, geode, the old well cut in half with its bucket. Animals: deer, fawn,
rabbit, fox, heron, three ducks, five fish, three butterflies, four birds, 36 petals.

Words and times are not retyped: the page loads `spec.json` and `cues.json` (copies of the meadow's) and resolves time
references like the Cutaway engine (`l02.chest`, `l02>-0.6`, `outro`). On screen: MOLE TUNNEL, LOST CHEST, ROMAN JAR,
T. REX, the 0 to 66,000,000 YEARS AGO counter, the title card (CUTAWAY / What Lies Under a Meadow) and the end card.

## Contract and files
- `index.html` (Inter fonts from the harness), `scene.js` (the film), `film.json` (id `style-cutaway-art-flat-vector`,
  fps 24, 1920x1080, 40 s), `spec.json` and `cues.json` (copies of the meadow's). No `blender.py` on purpose: rc-render
  `stills.yml` and `films.yml` pick the web path (Chromium, `harness/render.cjs`) when there is no `blender.py`.
- `window.KF = { width, height, fps, duration, canvas, shots, render(i, t) }`, `KF_READY` after fonts load. Every frame is
  a pure function of t (seeded RNG, no clock). Designed at 1920x1080 and scaled to `?w=&h=`.
- The canvas is created with `willReadFrequently: true`: that keeps it on the CPU (Skia) instead of SwiftShader GL. It
  is the difference between 6.4 s and 0.2 s per frame. Keep it.

## Shots (the meadow spec's shot list, in 2D)
map (0 to 7.2 s: wide, the cut face draws in from the top down), ground (to 12.9 s: close on the grass at the corner of
the cut, into the sun; title card), crane (to 21.1 s: down the cut face, labels arrive on their words), crane (to 27.3 s:
into deep time with the counter), macro (to 32.9 s: the skull, T. REX), hero (to 40 s: the whole section, wide; end card
at 35.7 s). Shot ends are the spec's own, so frame numbers match the Blender meadow (440 and 470 the upper layers, 768 the
skull, 830 the whole section). One deliberate change: labels stay on until the end of their shot once named (an explainer
builds its diagram up), so at most three show at once. Hedgehog, geode and well sit on the +X face in the Blender line; here
they move to the front face at their own depths (there is no full second face in 2D).

## Runs and board frames
- Local only, harness/render.cjs in headless Chromium (the same renderer and flags as rc-render stills.yml for web films).
- Board frames (1920x1080): 470 (the upper layers close: mole, chest, amphora with MOLE TUNNEL, LOST CHEST and ROMAN JAR)
  and 830 (the whole section, wide). Also rendered: 440 (same crane; ROMAN JAR is not named until 19.2 s, so two labels)
  and 768 (the skull close, T. REX).
- r6: a first pass ended the macro early so 768 was wide; the coordinator confirmed 768 is the skull in the Blender film
  and 830 the wide, so the spec's own shot ends are back.
- Rounds: r1 first pass (6.4 s/frame on SwiftShader GL; title ran off the frame; skeleton read as a dog); r2 CPU canvas,
  title right-aligned and sized to fit, chest and mole redrawn, gold seam tapered, limestone bedding, horizon glow; r3 to
  r5 the T. rex rebuilt as a horizontal museum pose (deep skull, short thick neck, ribcage, tiny arm, zig-zag hind legs,
  vertebrae), trilobite redrawn, macro reframed, molehill and crumbs fixed.
- No stills.yml dispatch: the builder rules for this session forbid commit and push, and the runner checks out a pushed
  commit. After the coordinator pushes: `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches
  -f ref=main -f "inputs[film]=films/cutaway/looks/flat-vector" -f "inputs[frames]=470,830" -f "inputs[per_job]=2"
  -f "inputs[tag]=looks-flat-vector-r1" -f "inputs[w]=1920" -f "inputs[h]=1080" -f "inputs[ref]=<full hash>"`.

## Render speed (measured here, 23 Oct)
- Drawing only (in the page, 96 frames across the film): 60 ms per frame at 1280x720, 113 ms at 1920x1080.
- End to end with harness/render.cjs (draw, JPEG encode, transfer, write): 0.15 s per frame at 1280x720; the whole 40 s
  film (960 frames) at 1920x1080 in 6.6 min, 0.41 s per frame, on this 2-core machine (most of it is JPEG encode and
  transfer out of the page, not drawing).
- Reference: the Blender Cutaway is about 1 to 3 minutes per frame on a runner (30+ minutes per frame today). This look is
  roughly 500 to 1000 times faster: a full film renders in minutes on one machine, a 9:16 cut or a recolour is a re-run,
  not a farm job.

## Weak spots (honest)
- It is 2D: no camera orbit, no real depth, no rim light on the block; the "camera" is pan and zoom with parallax.
- Animals and finds are simple flat shapes made for phone size; the T. rex is a stylised museum pose, not a fossil cast.
- The flat purple ground below the horizon is plain; at the crane and macro it shows as a large calm area left of the block.
- Petals and butterflies are small and can read as specks at 1280x720.
- Only the meadow is drawn: a new place means new drawing code (no preset system like the Blender line yet).

## Where this look is the right choice
1. Explainer series for YouTube and schools ("what is under a city, a beach, a vineyard"): a full episode renders in
   minutes, so a weekly series is affordable; channels and educational publishers pay for volume and clarity.
2. Trade and local business ads (drainage, foundations, landscaping, pool builders, well drillers): a branded cross-section
   of the client's job with their words set in code, cut to 9:16 and 16:9 the same day.
3. Data and infographic pieces for brands and agencies (soil health, water tables, carbon in farmland): the clean labels
   and counters carry real numbers, and changes after review cost a re-render of minutes, not a farm queue.
