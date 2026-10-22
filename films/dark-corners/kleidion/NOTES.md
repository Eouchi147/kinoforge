# As They Say (Kleidion, 1014): Lantern Road build

Original Dark Corners episode re-made in the Lantern Road style (living painting, painted 2.5D multiplane, motivated light), 9:16,
169.049 s, driven by `audio/mix.m4a` and `cues.json` (never retimed). `index.html` loads `scene.js` (three.js via the harness importmap).

## Files
- `scene.js` boot, camera keyframes, per-frame context `F`, captions, labels, title card, `words` overlays, set cache (LRU of 3).
- `shots.js` the shot table (cuts on `strong_hits`), captions from word timings, place/name `LABELS`.
- `kf.js` painted planes with relightable material, additive glow canvas, lean post chain (bloom, half-res Kuwahara, grade, grain).
- `paint.js` brush engine (from `proto/p03-lantern-road`, unchanged). `figs.js` people (planted-foot gait), horse, banners, torches.
- `sets/*.js` painted once per set: road, march, page, city, pass, camp, gorge, field, table, prilep.

## Shot list against the cues (times in s)
| shot | time | set | what |
|---|---|---|---|
| o1a o1b | 0 to 5.37 | road | captive column descends the switchbacks (o1: "captured a whole army") |
| o2a | to 8.43 | road | lanterns light one group at a time on 5.9, 6.34, 6.53, 6.92, 7.48 |
| o2b | to 10.94 | march | hands on shoulders, one lantern ("Blind.") |
| o3a o3b | to 15.78 | page | manuscript, script writing itself ("nine hundred years ago") |
| title | to 18.65 | road | DARK CORNERS / As They Say after the promise |
| x1a x1b x1c | to 25.73 | city | Constantinople dusk, Basil II on the terrace, lamps light on the hits |
| x2a x2b | to 31.81 | camp | Samuel at the fire, the Byzantine camp across the valley |
| x2c | to 34.99 | table | tally plank fills to 39 ("almost forty years") |
| x3a x3b | to 38.73 | gorge | riders in the gorge, stones fall, one escapes (ambush) |
| x3c x3d x3e | to 44.61 | field | night field, one still figure among the fallen |
| w1a w1b w1c | to 54.89 | pass | Samuel's wall going up |
| w1d | to 55.84 | table | the iron key ("The key.") |
| w2a w2b w2c | to 62.34 | pass | Basil attacks again and again, dust and volleys, the wall holds |
| t1a t1b | to 68.80 | pass (night) | torch column crosses the mountain and comes down behind the wall |
| t2a t2b t2c | to 74.12 | pass (night) | rout flares, defenders run, captives |
| s1a s1b s1c s1d | to 82.69 | field | pursuers with torches, the son lifts Samuel onto a horse, gallop |
| r1a | to 85.31 | camp | Bulgarian fires relit one by one |
| r1b | to 90.88 | gorge | governor's column, stones, a banner lies down, fade out |
| b1 | to 93.34 | table | wax seal pressed on the hit at 91.95 |
| b2a b2b | to 100.77 | page | the chronicler's page, "fifteen thousand" underlined |
| b3a b3b b3c | to 112.36 | road, march | groups of a hundred, one lantern each, the long road home |
| d1a d1b d1c | to 116.75 | prilep | Samuel on the rampart sees the lanterns, collapses |
| d2a d2b d2c d2d | to 125.57 | table | lamp and jug, cup filled, drunk, the flame gutters out |
| d3a d3b | to 128.87 | prilep (dawn) | window lit, then dark |
| q1a to q1d | to 140.39 | page | second manuscript (fourteen thousand), "nothing about blinding" |
| q2 | to 144.94 | page | both numbers struck out as the camera pulls back |
| f1a to f1e | to 160.89 | camp, city | Bulgaria fights on, THE BULGAR SLAYER in gold, time-lapse of the empty terrace |
| f2a f2b | to 166.45 | road | lantern groups walk away; last lantern out on "say" (165.74) |
| end | to 169.05 | road | DARK CORNERS / As They Say (last 2.6 s) |

Labels (no dashes): THE BALKANS 1014, BASIL II, CONSTANTINOPLE, SAMUEL, KLEIDION PASS, NIKEPHOROS XIPHIAS, PRILEP, 1014 TO 1018.
The blinding is never shown: lanterns and hands on shoulders tell it. Bulgarian banners are plain dark red (no crescent).

## Colour script
Dusk indigo and violet with warm lantern light (road, march, camp); Byzantine purple and gold (city); golden hour in the gorge and the
pass; candlelit parchment and wood (page, table); cold moonlit blue (field); dawn rose (Prilep ending).

## Measured cost (2-core box, other jobs running)
Frames at 720x1280: about 0.9 to 1.3 s each (`harness/render.cjs`, 72-frame stretch: 1.25 s/frame average); sets build lazily in 2.5 to 12 s
(first frame of each set), then about 0.2 to 0.5 s per frame at 360x640. 1080x1920 also works (about 2.9 s/frame).

## Known weak spots
- Walkers are puppet-like at close range (march); horses are simple profile silhouettes.
- The pass and gorge floors are flat-lit; the pass wall could take warmer gold.
- Table scenes (tally, key, seal stamp, cup) are simple vector shapes on blurry wood.
- Prilep lantern line is small beads of dark figures; it reads best at b3c.
- Debug: `?prof=1` logs set build times; `?hide=planeName` hides a painted plane.
- Fixed: after painted textures upload (`initTexture`) the renderer state is reset, otherwise the first frame of a set showed the
  previous frame's glow canvas.
