# Battle Map engine: the spec (v2, 22 Oct 2026)

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
The edit plan and its checks, no browser: `node films/lib/battlemap/tools/scenes.mjs films/battles/<name>` (exit code 1 on errors).
Debug URL params: `prof=1` (timings), `nb=1` (hide blocks), `cam=x,z,width,pitch,yaw` (override the camera), `dbg=1` (full scene report in the console).
The engine loads its own fonts (Cinzel 600/700/800 display, Cormorant Garamond 500i/600/600i text): films need no font links.

Units: map units (a Cannae unit is about 20 m). `x` east, `z` south, `y` up, `heading` degrees clockwise from north
(0 = facing -z, 90 = facing east). The map is centred on the origin: `x` in `[-W/2, W/2]`, `z` in `[-D/2, D/2]`.

## 0. What v2 changes (read this first if you are moving a v1 film onto v2)

Sam's verdict of 22 Oct (films/director/CRAFT.md): no emoji or cartoon graphics; a motion-graphics legend; every set pre-planned
with its camera; armies that look better and never clip; living worlds; Hollywood-level editing. v2 answers each point:

| v2 | what it is | spec |
| --- | --- | --- |
| armies | many small soldier figures (instanced) standing on movement trays, rank and file, banners; a spacing solver so units meet at a front and never pass through each other; dust behind moving units and along fronts; casualties thin the ranks | `blocks` (unchanged) + section 3 |
| glyphs | refined flat vector set: heraldic banners, unit symbols, place glyphs, annotations. v1 icon names still work and draw refined replacements | section 5 |
| labels | cartographic tags (small caps, paper halo, hairline leader to a ringed dot, team rule drawn on); screen labels become documentary captions; clean counters | section 5 |
| legend | sides panel (banner, name, commander, strength), key panel (unit symbols, lettered places linked to map markers), scale bar and compass | section 10 |
| scenes | sets (time of day, haze, cloud) + shots with a written reason, opening frame and motivated moves; compiled to camera keys; speed limits refuse fake fast moves; shot count, short shots and jump cuts are checked | section 11 |
| living world | camps (tents, palisade, fires, people), walkers on roads, smoke, birds, wind gusts over the grass, flowing water, drifting cloud shadows | section 12 |

Backward compatible: a v1 spec renders on v2 unchanged (figures replace slabs, glyphs and tags replace icons and plates).
To keep the v1 look of one part: `armies: 'blocks'` (slabs) and `overlayStyle: 'v1'` (plates and bouncy icons). v1 films that
registered their own cartoon icons (`registerIcon`) still draw them: the re-directing builder must redraw those in the v2 style
(see section 5) or swap them for engine glyphs.

### Moving a v1 film onto v2 (checklist for the builders of the other battles)
1. Write the scene list first (5 to 9 scenes, each with a `job`), then the shots (`why`, `from`, `moves`). Replace the `camera`
   array with `scenes` and the `insets` that only switched maps with `stage` + `inset: 'full'` on the scene. Run `tools/scenes.mjs`
   until there are no errors; read every warning.
2. Remove cartoon icons and gags (hearts, bouncing crowns, burst stars, question marks, emoji-like props). Keep a glyph only if it
   carries information (a place, a unit type, a commander, a route follower). Humour lives in the narration and the timing (a cut on
   a punchline, a hold), never in clip art. Film-side `icons.js` with cartoon drawings must go or be redrawn flat (one ink weight,
   flat fills, no faces, no shine, no drop shadow).
3. Add a `legend`: the two sides (with `at` on the word that names them, strengths with `strengthAt`), the unit kinds used, and the
   2 to 4 key places (`pos` puts a lettered marker on the map, linked to the key row when it appears).
4. Add `ambient`: at least camps or walkers + birds + `wind` + river `flow` so every wide shot has three layers of motion.
5. Labels: drop labels that only repeat the narration; keep names, numbers, dates and the one phrase a shot is about.
   `big: true` screen labels become captions (keep them to dates and numbers). Delete `style: 'text'` workarounds.
6. Army blocks: check the kinds (`infantry`, `elite`, `cavalry`, `light`, `archers`, `elephant`, `marker`) and that no two blocks
   are authored on top of each other for long (the solver keeps them apart but a front should be meant). `appear` now raises the
   ranks front to back instead of dropping a slab; `fadeTo` thins the ranks.
7. Light: use the scene `set.time` (0 day, 1 low red sun) instead of separate `light` keys, except for an evening that falls inside a scene.
8. Contact sheet with one still per shot, then 5 s motion stretches; see `films/battles/cannae/NOTES.md` for the reference.

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

Easings: `linear in out inOut inQuad outQuad inOutQuad smooth outBack inBack outElastic outBounce step`, and the camera
operator's `cam` (ease in 30 %, steady middle, ease out; peak speed 1.43 x average), `camSoft` (45 %, peak 1.82 x) and `camLong` (20 %, peak 1.25 x).
Scene moves default to `cam`. `inOut` (cubic) peaks at 3 x the average speed: avoid it for cameras.

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
- v2 figures: `kind` also picks the figure: `infantry` (shield, spear), `elite` (crest, bigger shield), `cavalry` (horse and rider, lance),
  `light` / `archers` (no shield, a bow stave, looser order), `elephant` (with a tower), `marker` (tray and banner, no figures).
  `figures: 'cavalry'` overrides the figure for a block; `figures: false` gives a tray only. `figScale` (1) enlarges the figures (use 1.3
  to 1.5 on a continent-scale map). `spacing` (map units between files) defaults per kind (infantry 1.7, cavalry 2.2 x 2.8, elephant 4.4);
  `maxFigures` (1600) caps a block (the cell grows to fit). `tray: [r, g, b]` and `trayAlpha` (0.9) style the tray; `banner: false` hides
  the standard (in a `grid` group every other member carries one; `bannerEvery: 1` gives all of them one). `dust: false` stops its dust.
- Solver: each frame, blocks whose figures meet are kept apart at a front (ranks compress over about 3 units, a dust line rises). The
  contact normal is the facing of the block that is advancing into the other, so fronts, flanks and rear attacks all hold. Members of the
  same `grid` group are not separated (a `squeeze` is meant). `solid: false` lets a block pass through (ghosts, fords); `weight` (1) makes a
  block yield less (2 = holds its ground, the other side gives).
- Figures march with a bob and lean when their block moves (speed from the tracks), idle with a small sway, appear rank by rank from the
  front (`appear`), and thin out by casualty when `fadeTo` runs (about 70 % of the figures go at `fadeTo: 1`; they shrink and sink, never fall).

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

Selectors: `block`, `blocks: [...]`, `group`.
For `fadeTo` (casualties) keep `alphaTo` at 0.5 or more in v2: the tray stays readable and the thinning does the telling. Tracks that `to`/`by` can drive: `x z heading len dep bulge scale alpha drop lift fade sink`.
Moves on one track are sequential and each starts from the value the previous one left (so order them by time, they are sorted for you).
`appear` drops the block in (`appearFrom` height, `appearEase`). `stagger` offsets each member of a group or list.

## 4. `arrows`: inked arrows laid on the ground

```js
{ id: 'push', at: 'l09.pushed', until: 'l09.gap.', ease: 'out', team: 'rome', width: 6, path: [[-10, 0], [52, 0]],
  lift: 6, hide: 'l10.Meanwhile,', style: 'dash', head: true, smooth: true }
```

Drawn on by a pen-progress uniform from `at` to `until` (or `dur`), then held until `hide` (fades). `team`/`color`: `rome carthage ink gold cream green`.
v2 strokes are tapered ink (thin at the tail, full width after `taperLen`, default 36 units; `taper` = tail width fraction, 0.3; `taper: 1`
for an even line), with a swept head that is drawn on last (`headLen` 2.4 x width, `headW` 1.7 x width) and a paper halo (`halo`, units).
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

v2 glyphs (`icons.js`, flat, one ink weight, paper halo, no faces): heraldry `banner` (swallowtail pennant), `vexillum` (Roman standard),
`shield`; unit symbols `u-infantry u-heavy u-cavalry u-light u-archers u-elephant u-ships u-artillery u-commander` (team tinted frames);
places `town fort camp river ford hill mountain woods bridge sea plain`; annotations `crown helmet commander star laurel book scroll sword
swords clash no check question gate ring envelop elephant galley tent tapestry cross`.
v1 names map to refined glyphs: `city` = town, `flag` = banner, `burst` = clash, `door` = gate, `heart` = ring, `hug` = envelop, `ship` = galley,
`bow` = archers symbol. Prefer the information glyphs; the annotations are for rare, meaningful use.
`anim`: `none`, `float` (a slow 2.5 % drift; `bounce` maps to it), `walk` (a small step while following an arrow), `sway`; `fallAt` tips a glyph over.
World icons size in map units but are clamped on screen to `minPx`..`maxPx` (fractions of the frame height, 0.035..0.16) so they stay
legible and never cartoonish. `hidden: true` places an anchor (for `hop`) without drawing. Icons fade and settle in (no overshoot).
Labels: `style` `tag` (default for world labels), `caption` (default for `screen` labels: a soft dark band with gold rules),
`plate` (v1). `align: left|right|center` (auto from `dx`), `rule: false` drops the team underline, `leader: false` the hairline.
Counters draw a large tabular number in the team colour with its suffix under a drawn-on rule.
`markers: [{ id, at, until, pos, y, glyph, letter, team, label, labelUntil | labelDur (4 s), size (frame height fraction, 0.06) }]` pin a place
glyph with a lettered badge on the map (the legend creates them from its places). No em or en dashes and no "..." in any text.

## 6. `camera`: keyframes (top-down, low soaring obliques, push-ins)

```js
camera: [
  { at: 0, target: [-170, 30], dist: 150, pitch: 13, yaw: 70, mm: 30 },                 // low, soaring
  { at: 'l00.together', target: [-108, 6], dist: 125, pitch: 15, yaw: 82, mm: 30, ease: 'spline' },
  { at: 17.4, target: [-45, 0], width: 470, pitch: 89.9, yaw: 0, mm: 35, ease: 'inOut' }, // top-down: `width` = ground width in view
]
```

Prefer `scenes` (section 11): the `camera` array is what scenes compile to, and stays for v1 films and quick tests.
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

## 8. Worked example: a tiny two-block battle (v1 style, still valid)

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
- v2 armies are instanced figures (about 30 triangles each, 3,000 to 4,000 in a big battle) on trays; banners are camera-facing.
- Cost on CPU SwiftShader at 1280x720 (profiled, `prof=1`): engine update (figures, solver, dust, ambient) 15 to 45 ms, GPU render
  50 to 100 ms without MSAA; MSAA 4 adds about 0.4 s, so keep `msaaOn` to the low close shots. Measured wall time per frame is in each
  film's NOTES.md. The sheet bake is a one-off 4 to 10 s per stage.
- Determinism: all noise is seeded from `world.seed`; the only time inputs are `t` and the cue words.

## 10. `legend`: the motion-graphics frame

```js
legend: {
  title: { text: 'THE BATTLE OF CANNAE', sub: '2 August 216 BC', at: 'l02.Hannibal,' },
  show: [['l02.Hannibal,', 'l17.since.>']],                  // when the sides panel is on screen (slides in and out)
  corner: 'tl',                                               // sides panel corner (tl tr bl br); key: key.corner (default bl)
  sides: [{ id: 'rome', team: 'rome', name: 'ROME', commander: 'Varro and Paullus', commanderAt: 'l03.commanders', banner: 'vexillum',
            at: 'l03.Rome.', strength: 80000, strengthAt: 'l05.80', strengthLabel: 'SOLDIERS', dimAt: 'l14.lost' }, ...],
  key: { show: [['l04.armies', 'l12']], unitsTitle: 'FORCES', placesTitle: 'PLACES' },
  units: [{ id: 'inf', kind: 'infantry', name: 'Infantry', teams: ['rome', 'carthage'], at: 'l05.soldiers.' },
          { id: 'vets', kind: 'elite', name: 'Veteran infantry', team: 'carthage', at: 'l07.best' }],
  places: [{ id: 'aufidus', letter: 'B', glyph: 'river', name: 'River Aufidus', at: 'l04.river.', pos: [-150, 168], stage: 'med'?,
             label: 'RIVER AUFIDUS' | false, labelDur: 4, markerSize: 0.06, until }],
  focus: [{ entry: 'vets', at: 'l11.best', until: 'l11.left,' }],   // highlight a row while the narration talks about it
  scale: { unitM: 20, show: [['l04', 'l12']] }, compass: true,       // scale bar and north arrow, on views pitched above 50 degrees
}
```

Every row grows in on its own `at` (the word that first names it); the panels grow with their rows. A place with `pos` becomes a
lettered marker on its stage's map, and while the row is new a dashed hairline links the row's badge to the marker. Sizes scale with
the frame height (row text about 2.5 % of the height) so the legend reads on a phone. `dimAt` greys a side out (defeat); `focus` tints a
row (use it for the verdict: who won the battle, who won the war). Keep the key to 3 unit kinds and 2 to 4 places.

## 11. `scenes`: sets and pre-planned cameras (the edit)

```js
scenes: [
  { id: 'S6', name: 'The jaws', at: 'l08', job: 'the Romans walk into the bow, the horsemen ride round, and the trap closes',
    set: { time: [0.05, 0.2], haze: 1.1, cloud: 0.3 },        // time: 0 day .. 1 low red sun; [a, b] drifts through the scene
    stage: 'med', inset: 'full',                              // optional: the scene plays on another map, full screen
    transition: 'cut' | { type: 'dissolve', dur: 0.8 },       // a dissolve only for a change of world or of time
    climax: true,                                             // allows shots under 2 s
    shots: [
      { at: 'l08', why: 'behind the Roman ranks as they charge: the weight of the push',
        from: { target: [-56, 0], dist: 112, pitch: 15, yaw: 90, mm: 35 },        // the opening frame (dist or width)
        moves: [{ until: 'l08.and', to: { target: [-28, 0], dist: 104 } }] },      // moves chain; `at` to start later (a hold first)
      { at: 'l08.and', why: 'high angle: the middle gives way', from: { ... }, moves: [{ at: 'l08.slowly,', dur: 4, by: { yaw: 8, zoom: 0.9 }, ease: 'camSoft' }] },
    ] },
]
```

- A shot starts with a cut at `at` (the first shot of a scene at the scene's start); it ends where the next shot (or scene) starts.
  `why` is the reason for the cut (new information, change of place or time, reaction, change of scale): it is printed in the report.
- A move: `to` (absolute pose fields) and/or `by` (`target: [dx, dz]`, `yaw`, `pitch`, `mm`, `zoom` = multiply width/dist), `until` or
  `dur`, `ease` (default `cam`). A move that starts after the previous one ends holds the frame in between.
- Speed limits (CRAFT.md section 4, peaks): pan 0.26 frame widths per second, zoom 0.16 per second (log of the distance), yaw 16 and
  pitch 12 degrees per second (`cameraLimits` overrides). A faster move is an ERROR: the film will not start. Start earlier, move less or
  hold longer; `fast: 'reason'` on a move allows it (a whip at the climax), and the reason is the record.
- Warnings: scene count outside 5 to 9, shot count outside 18 to 35 per 150 s (hard error over 40 per 180 s), shots under 2 s outside a
  `climax` scene, jump cuts (consecutive shots on one map with under 30 degrees of change, under 15 degrees of pitch and less than a size
  step), missing `why` or `job`, moves that outlive their shot.
- `sceneChecks: 'warn'` turns errors into console warnings (for drafts only).
- A scene with `stage` + `inset` creates the full-screen (or framed: `inset: { rect, tilt, scrim }`) inset for its span; its dissolve
  fades the other map in. Same-map dissolves render the outgoing frame once more and fade it off the incoming shot.

## 12. `ambient`: the living world (per stage)

```js
ambient: {
  wind: [1.2, 0.35], gusts: 0.6,                       // banners, dust and smoke drift; gusts sweep over the grass (0 = off)
  flow: { dir: [1, 0.08], speed: 1.2, glint: 1.2 },    // moving glints on rivers and the sea
  camps: [{ pos: [-235, 80], size: [50, 34], rot: 0, team: 'rome', style: 'grid' | 'scatter', tents: 28, fires: 3, people: 14, palisade: true }],
  walkers: [{ path: [[x, z], ...], n: 6, gap: 4, speed: 1.6, kind: 'light' | 'cavalry', team: 'neutral', loop: true, offset: 0, at, until }],
  smoke: [{ pos: [x, z], n: 12, alpha: 0.22, height: 10, at, until }],      // columns (camp fires, burning villages, the battle's smoke)
  birds: [{ center: [x, z], r: 50, h: 30, n: 7, speed: 7, dir: 1 } | { path: [[x0, z0], [x1, z1]], n: 5, h: 40, speed: 9 }],
}
```

Cloud shadows drift by themselves (`look.cloud`). Positions are `pos` / `center` / `path`; `at` and `until` are always times.
CRAFT.md asks for at least three layers of ambient motion in every wide shot: on Cannae they are cloud shadows, grass gusts, river
glints, camp smoke and people, birds, road walkers and the army dust.
