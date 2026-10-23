# Cutaway art look: flat-vector (pure 2D web film, no Blender)

The meadow example (`films/cutaway/meadow`) as a side-on cross-section in clean flat vector shapes, like a premium
science explainer, drawn on an HTML canvas in code: a floating block with a thin top strip and a darker right face, the
eight "time" strata in a limited palette with subtle gradients, one mark vocabulary per layer, the river cut as glass, a
dusk-gold sky with flat hills, film grain and a soft vignette; labels in thin Inter on ink pills with hairline leaders.
It is the twelfth look of the board (23 Oct), the only one outside Blender, and about 500 to 1000 times faster to render
than the Blender Cutaway. Board sent to Sam on 23 Oct; his pick is pending.

## Inputs
- `films/cutaway/looks/flat-vector/`: `index.html`, `scene.js` (the film), `film.json` (id
  `style-cutaway-art-flat-vector`, `line: "cutaway-web"`, 24 fps, 1920x1080, 40 s, no audio), `spec.json` and
  `cues.json` (copies of the meadow's), `NOTES.md`. No `blender.py` on purpose: rc-render picks the web path.
- Node 22, `harness/` (`npm ci --prefix harness`, `cd harness && npx playwright install chromium`), Inter fonts from the
  harness.

## What it is made of
- Contract: `window.KF = { width, height, fps, duration, canvas, shots, render(i, t) }`, `KF_READY` after fonts load.
  Every frame is a pure function of `t` (seeded RNG, no clock). Designed at 1920x1080, scaled to `?w=&h=`.
- Words and times are not retyped: the page loads `spec.json` and `cues.json` and resolves time references like the
  Cutaway engine (`l02.chest`, `l02>-0.6`, `outro`). On screen: MOLE TUNNEL, LOST CHEST, ROMAN JAR, T. REX, the 0 to
  66,000,000 YEARS AGO counter, the title card (CUTAWAY / What Lies Under a Meadow) and the end card.
- Content: the meadow's (big tree and 14 smaller trees, river with lilies, reeds, ducks, heron and fish, five houses, the
  mill with a turning wheel, bridge, lamps, boulders, flowers; all ten finds; deer, fawn, rabbit, fox, birds, butterflies,
  petals). Hedgehog, geode and well move from the +X face to the front face at their own depths (no second face in 2D).
- Shots (the spec's own ends, so frame numbers match the Blender meadow): map 0 to 7.2 s (the cut face draws in from the
  top down), ground to 12.9 s (title card), crane to 21.1 s (labels on their words), crane to 27.3 s (deep time and the
  counter), macro to 32.9 s (the skull), hero to 40 s (end card at 35.7 s). One deliberate change: labels stay on to the
  end of their shot once named, so at most three show at once.
- The canvas uses `getContext('2d', { willReadFrequently: true })`: CPU raster (Skia) instead of SwiftShader GL. That is
  the difference between 6.4 s and 0.2 s a frame. Keep it.

## Exact steps
1. Render board frames locally (the same renderer as rc-render's web path):
   `node harness/render.cjs films/cutaway/looks/flat-vector --out out/flat-vector --w 1920 --h 1080 --fps 24 --start 470 --end 471 --jpg`
   (also 830; 440 and 768 for the crane and the skull). `--end` is exclusive.
2. Whole film: same command with `--start 0 --end 960` (6.6 min on the 2-core chat box at 1920x1080), then encode:
   `ffmpeg -framerate 24 -i out/flat-vector/frames/%05d.jpg -c:v libx264 -crf 17 -pix_fmt yuv420p flat-vector.mp4`.
   Or on runners (after a push): rc-render `films.yml` with `film=films/cutaway/looks/flat-vector` (web films: 12 to 20
   parts) or `stills.yml`:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/stills.yml/dispatches -f ref=main \
     -f "inputs[film]=films/cutaway/looks/flat-vector" -f "inputs[frames]=470,830" -f "inputs[per_job]=2" \
     -f "inputs[tag]=looks-flat-vector-r1" -f "inputs[w]=1920" -f "inputs[h]=1080" -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   (not dispatched as of 23 Oct; the board frames were rendered locally).
3. A new place: new drawing code in a copy of `scene.js` (there is no preset system for the 2D look yet); keep words in
   `spec.json` and times in `cues.json`.
4. A 9:16 cut or a recolour is a re-run of minutes, not a farm job.

## Cost per frame
Drawing 60 ms at 1280x720, 113 ms at 1920x1080; end to end with `render.cjs` 0.15 s at 1280x720 and 0.41 s at
1920x1080 (mostly JPEG encode and transfer). The Blender Cutaway is about 1 to 3 min a frame on a runner.

## Best uses (from NOTES)
1. Explainer series for YouTube and schools ("what is under a city, a beach, a vineyard"): a full episode renders in
   minutes, so a weekly series is affordable.
2. Trade and local business ads (drainage, foundations, landscaping, pools, wells): a branded cross-section of the job,
   cut to 9:16 and 16:9 the same day.
3. Data and infographic pieces (soil health, water tables, carbon in farmland): clean labels and counters carry real
   numbers; changes cost minutes.

## Weak spots
2D only (pan and zoom with parallax; no orbit, no real depth, no rim light); animals and finds are simple flat shapes
(the T. rex is a stylised museum pose); the flat purple ground left of the block is a large calm area in crane and macro;
petals and butterflies are specks at 1280x720; only the meadow is drawn.

## Alternatives
The Blender looks (`cutaway-art.md`) for depth and light; the Kinetic or Battle Map web engines for other 2D grammars.

## Checks before showing Sam
Title fits the frame (round 1 ran off it); the T. rex reads as a dinosaur (round 1 read as a dog); labels on their words.

## Known traps
SwiftShader GL is 30 times slower: keep `willReadFrequently: true`. The skull macro is frame 768 and the wide is 830
(a first pass that ended the macro early was reverted to the spec's shot ends).

## Sources of truth
`films/cutaway/looks/flat-vector/NOTES.md`, `scene.js`, `index.html`, `film.json`, `harness/render.cjs`, rc-render
`films.yml` (web path). The code wins if they disagree.
