# Battle Map engine: the spec

One JSON-like object (a `spec.js` that `export default`s it, or a plain JSON file) drives a whole film. The engine is
`films/lib/battlemap/` (Three.js r0.186, harness kit). A film is just:

```html
<!-- films/battles/<name>/index.html -->
<script type="importmap">{ ...same importmap as the other harness films... }</script>
<script type="module">
  import { startBattleMap } from '/films/lib/battlemap/index.js';
  startBattleMap({ specUrl: './spec.js', cuesUrl: './cues.json' });
</script>
```

Render with the usual contract (`window.KF`, `KF_READY`): `node harness/render.cjs films/battles/<name> --w 1280 --h 720 ...`.
Fast stills in one browser session (bakes the sheet once): `node films/lib/battlemap/tools/stills.cjs films/battles/<name> --t 3,17.6,40 --out /tmp/x`.
Debug URL params: `prof=1` (timings), `nb=1` (hide blocks), `cam=x,z,dist,pitch,yaw` (override the camera).

Units: map units (a Cannae unit is about 20 m). `x` east, `z` south, `y` up, `heading` degrees clockwise from north
(0 = facing -z, 90 = facing east). The map is centred on the origin: `x` in `[-W/2, W/2]`, `z` in `[-D/2, D/2]`.

## 1. Time references (`at`, `until`, `dur`, `hide`...)

Everywhere a time is accepted you can write:

| form | meaning |
| --- | --- |
| `12.5` | seconds |
| `"l08"` / `"l08>"` | start / end of cue line `l08` |
| `"l08.charged"` | start of the word "charged" in line `l08` (case and punctuation ignored, prefix match) |
| `"l08.charged>"` | end of that word |
| `"l08.step#1"` | the second "step" in the line (0-based) |
| `"l05.bigger+0.25"` | offset in seconds, `+` or `-` |
| `"myMark"` | an entry of `spec.marks` (`{ myMark: "l03.commanders" }`) |
| `{ line, word, nth, edge, offset, snap }` | object form; `snap: true` snaps to the nearest music strong hit (0.3 s) |
| `{ hit: n }`, `{ beat: n }`, `{ downbeat: n }` | music grid from `cues.json` |

An entry's span is `{ at, until }` or `{ at, dur }`. A wrong word is a hard error (so the spec cannot silently drift from the audio).

Easings: `linear in out inOut inQuad outQuad inOutQuad smooth outBack inBack outElastic outBounce step`.

## 2. `world`: terrain from data

```js
world: { seed: 216, size: [760, 500], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 248, elevation: 31 }, sunEve: { azimuth: 284, elevation: 6 },
  style: { contour: 1.5, pxPerUnit: 5.4, palette: [[h, [r, g, b]], ...], paletteSoft: 5 },
  features: [ ... ] }
```

`res` is the height-grid spacing (1 unit), `meshStep` the render-mesh step. `style.pxPerUnit` is the sheet resolution
(5.4 px/unit, capped at about 4096 px). The sheet (paper, watercolour washes by height, engraved contours, 45 degree
hatching on shaded faces, hex-lattice trees, patchwork fields, water ripples, roads, grass tufts) is baked once on the GPU.

Feature types (all positions in map units; angles in degrees; polygons are lists of `[x, z]`):

| type | fields |
| --- | --- |
| `undulate` | `amp, scale, oct` fractal relief |
| `hill` | `at, r (number or [rx, rz]), h, rot, rough, crag, power` |
| `ridge` | `path, w, h, rough, crest, meander` (a ridge line) |
| `mountains` | `path + w` or `poly / at + r`; `h, scale, ridged (0..1), edge` |
| `river` | `path, w, depth, bank, meander, wl, taper, name` |
| `sea`, `lake` | `poly` (lake: or `at + r`), `shelf, beach, depth, smooth` (Chaikin passes, default 2) |
| `land` | `poly, shelf, beach, depth, smooth, wob, lift`: a landmass cut out of a `sea`; `wob` roughens the coast |
| `woods` | `at + r (+ rot, wob)` or `poly` |
| `farms` | `rect: [cx, cz, w, d, rotDeg]`, `cell: [w, d]`, `gap, skip, kinds` |
| `road` | `path, w, meander` |
| `flat` | `at, r, level, soft, amount` (flatten a camp or battlefield) |

## 3. `blocks`: armies

```js
blocks: {
  rome:   { team: 'rome', kind: 'infantry', x: -100, z: 0, heading: 90, len: 92, dep: 54,
            grid: { cols: 4, ranks: 3, gap: 2.4 }, count: 80000, hidden: true, height: 4 },
  carC:   { team: 'carthage', kind: 'infantry', x: 6, z: 0, heading: 270, len: 112, dep: 14, bulge: 0, hidden: true },
  carCav: { team: 'carthage', kind: 'cavalry', ... },   // a faster wedge-shaped block
}
```

- `team`: `rome` (deep red), `carthage` (royal blue), `neutral`, `green`, `gold`. `kind`: `infantry`, `elite` (denser lattice), `cavalry` (wedge front).
- `len` = the front (perpendicular to `heading`), `dep` = depth. `bulge` bends the line into an arc (sagitta = `bulge * len`; positive bows toward `heading`).
- `grid` makes a group of sub-blocks (`rome` is a group of 12 and also an id for the `group` selector); `count` is the soldier count the `counters` read.
- `hidden: true` starts invisible (alpha 0); `bannerScale`, `height`, `spacing` tune the look.

### `moves` (the choreography)

```js
moves: [
  { group: 'rome', at: 'l00.Rome', dur: 0.8, stagger: 0.17, appear: true },        // blocks drop in one by one
  { block: 'carC', at: 'l06.put', dur: 3.2, to: { bulge: 0.22, x: -17 }, ease: 'inOut' },
  { group: 'rome', at: 'l08.charged', dur: 7, by: { x: 82 }, ease: 'inQuad' },       // relative move
  { block: 'carCavS', at: 'l10.then', dur: 3, path: [[-100, 96], [-132, 60], [-108, 14], [-40, 22]] },  // smooth path, faces travel
  { block: 'x', at: t, dur: 2, wheel: { about: [px, pz], deg: 90 } },                // pivot about a point
  { group: 'rome', at: 'l13.packed', dur: 3.6, squeeze: { about: [28, 0], kx: .8, kz: .8, lenK: .8, depK: .8 } },
  { group: 'rome', at: 'l14.lost', dur: 2.4, stagger: 0.22, fadeTo: 1, alphaTo: 0.1, sinkTo: 0.9 }, // fade by numbers, never wounds
  { blocks: ['a', 'b'], at: t, dur: 0.4, vanish: true },
]
```

Selectors: `block`, `blocks: [...]`, `group`. Tracks that `to`/`by` can drive: `x z heading len dep bulge scale alpha drop lift fade sink`.
Moves on one track are sequential and each starts from the value the previous one left (so order them by time, they are sorted for you).
`appear` drops the block in (`appearFrom` height, `appearEase`). `stagger` offsets each member of a group or list.

## 4. `arrows`: inked arrows laid on the ground

```js
{ id: 'push', at: 'l09.pushed', until: 'l09.gap.', ease: 'out', team: 'rome', width: 6, path: [[-10, 0], [52, 0]],
  lift: 6, hide: 'l10.Meanwhile,', style: 'dash', head: true, smooth: true }
```

Drawn on by a pen-progress uniform from `at` to `until` (or `dur`), then held until `hide` (fades). `team`/`color`: `rome carthage ink gold cream green`.
`id` lets an icon `follow` the arrow tip. Catmull smoothing is on unless `smooth: false`.

## 5. `labels`, `counters`, `icons`, `volleys` (the overlay)

Anchors: `pos: [x, z]` (+ `y` height) or `block: 'id'` (follows the block) or `screen: [fx, fy]` (fraction of the frame).
World-anchored items follow the camera and get a leader line when offset (`dx`, `dy` in frame-heights; `leader: false` to hide).

```js
labels:   [{ at: 'l08.gave', until: 'l08.slowly,', text: 'THE MIDDLE GIVES WAY', block: 'carC', team: 'carthage', dx: 0.2, dy: -0.12 },
           { at: 1.3, until: 3.9, text: '2,200 YEARS AGO', screen: [0.5, 0.17], style: 'text', big: true, size: 1.9 }],
counters: [{ at: 'l05.80', until: 'l05.Rome\'s', block: 'rome', team: 'rome', from: 0, to: 80000, countDur: 1.1, step: 1000, suffix: 'SOLDIERS' }],
icons:    [{ at: 'l03.commanders', until: 'l04.On', icon: 'helmet', team: 'rome', pos: [-122, -22], y: 20, size: 22, anim: 'sway' },
           { follow: 'alps', at: 'l02.elephants,', icon: 'elephant', team: 'carthage', size: 26, anim: 'walk' }],
volleys:  [{ at: t, dur: 1.2, from: { block: 'a' }, to: { block: 'b' }, n: 36, flight: 0.9, spread: 0.35, team: 'carthage' }],   // lofted stroke-arcs; from/to = {block} or [x, z, radius] (unused in Cannae)
```

Icons drawn in code: `elephant ship crown helmet heart tent bow burst city book door flag question star laurel sword swords no hug check`.
`anim`: `bounce sway walk none`. Screen icons take `size` as a fraction of the frame height; `inner: [r, g, b]` recolours the `hug` centre.
Everything pops in with an `outBack` scale. No em or en dashes and no "..." in any text.

## 6. `camera`: keyframes (top-down, low soaring obliques, push-ins)

```js
camera: [
  { at: 0, target: [-170, 30], dist: 150, pitch: 13, yaw: 70, mm: 30 },                 // low, soaring
  { at: 'l00.together', target: [-108, 6], dist: 125, pitch: 15, yaw: 82, mm: 30, ease: 'spline' },
  { at: 17.4, target: [-45, 0], width: 470, pitch: 89.9, yaw: 0, mm: 35, ease: 'inOut' }, // top-down: `width` = ground width in view
]
```

`target` ground point, `dist` (orbit distance) or `width` (ground width that fits the frame; the engine solves the distance),
`pitch` (3 to 89.9), `yaw` (0 looks north, clockwise), `mm` focal length. `ease` applies to the move INTO the key; `spline`
makes the path C1 through three or more keys (use it for sweeps). Keys must be in time order; `cut: true` on a key jumps instead of easing.

## 7. `light`, `look`, `cards`, `insets`, `msaaOn`

```js
light: [{ at: 'l14.evening,', dur: 3.4, to: { eve: 1, haze: 1.3 }, ease: 'inOut' }],   // eve 0 golden afternoon -> 1 low red sun; also cloud, glint
look:  { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 } },   // fog, sky and sun colours: DEFAULT_LOOK in stage.js
cards: [ { at: 17.4, until: 21.7, scrim: 0.9, scrimCenter: 'rgba(20,10,4,0.85)', fadeIn: 0.25, fadeOut: 0.7,
           lines: [{ text: 'THE BATTLE OF CANNAE', size: 0.088, y: 0.44, delay: 0 }, { text: '216 BC', size: 0.07, y: 0.585, delay: 1.3, colorTop: '#ffd9a0', colorBottom: '#e2873a' }],
           ornaments: [{ y: 0.35, w: 0.62 }] },
         { at: 153.43, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, lines: [...] } ],
stages: { med: { world, blocks, moves, arrows, labels, icons, camera, light } },        // a second map with its own spec
insets: [ { stage: 'med', at: 22.4, until: 33.5, rect: [0.1, 0.1, 0.8, 0.8], tilt: -1.2, in: 0.55, out: 0.45, scrim: 0.55 },   // framed panel (relief inset)
          { stage: 'med', at: 127.6, until: 170, rect: [0, 0, 1, 1], frame: false, pop: false, in: 1.2, out: 0.01 } ],        // full-screen cut
msaaOn: [[0, 14], [118, 127]],   // anti-aliasing costs about 0.4 s/frame: enable only where it matters
```

A `stage` is a complete second Stage (own world, blocks, camera, labels). An `inset` renders it into a texture and shows it
as a framed panel over the main map (the main map is dimmed by `scrim`), or full screen with `rect: [0, 0, 1, 1]`
(the main render is skipped to save time). Stage times use the same clock, so cue words work inside stages too.

## 8. Worked example: a tiny two-block battle (about 12 lines)

```js
export default {
  world: { seed: 1, size: [400, 240], features: [{ type: 'undulate', amp: 4, scale: 80 },
    { type: 'river', path: [[-200, 70], [0, 80], [200, 60]], w: 7 }] },
  blocks: {
    red:  { team: 'rome', kind: 'infantry', x: -90, z: 0, heading: 90, len: 60, dep: 24, count: 10000, hidden: true },
    blue: { team: 'carthage', kind: 'infantry', x: 90, z: 0, heading: 270, len: 60, dep: 24, count: 8000, hidden: true },
  },
  moves: [
    { blocks: ['red', 'blue'], at: 'l01.armies', dur: 0.8, stagger: 0.2, appear: true },
    { block: 'red', at: 'l01.charged', dur: 4, by: { x: 150 }, ease: 'inQuad' },
    { block: 'blue', at: 'l01.charged', dur: 4, to: { bulge: -0.3, x: 120 }, ease: 'out' },
  ],
  labels: [{ at: 'l01.charged', until: 'l01.end', text: 'THE CHARGE', block: 'red', team: 'rome', dy: -0.2, big: true }],
  counters: [{ at: 'l01.armies', until: 'l01.charged', block: 'red', team: 'rome', from: 0, to: 10000, step: 100 }],
  arrows: [{ at: 'l01.charged', dur: 1.2, team: 'rome', width: 5, path: [[-60, 0], [40, 0]], lift: 6 }],
  camera: [{ at: 0, target: [0, 0], width: 320, pitch: 80, yaw: 0, mm: 35 },
           { at: 'l01.charged', target: [20, 0], width: 220, pitch: 50, yaw: 30, mm: 35, ease: 'inOut' }],
  cards: [{ at: 6, until: 12, fill: 'rgb(14,7,3)', fillAlpha: 0.84, lines: [{ text: 'BATTLE MAP', size: 0.13, y: 0.5 }] }],
};
```

The full film using every feature is `films/battles/cannae/spec.js` (read it next to its `cues.json`).

## 9. Look and cost notes

- Scale reads through size: keep the camera `width` / `dist` honest and put the lone figure in the same frame as the host.
- Geometry stays flat-shaded blocks with an ink border and a lattice of soldiers, so any army size reads at any distance. Banners are camera-facing.
- Cost on CPU SwiftShader at 1280x720: terrain + blocks about 0.5 s/frame (MSAA off), about 0.9 s with MSAA 4; the sheet bake is a one-off 4 to 10 s per stage.
- Determinism: all noise is seeded from `world.seed`; the only time inputs are `t` and the cue words.
