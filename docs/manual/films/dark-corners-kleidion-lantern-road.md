# Film: As They Say (`dark-corners-kleidion-lantern-road`), Dark Corners, Lantern Road (re-directed)

A 169.0 s, 9:16 Dark Corners episode: Kleidion, 1014, Emperor Basil II's victory over Tsar Samuel of Bulgaria, the order to
blind the captives ("about fifteen thousand, as they say"), the long road home of groups led by one man with one eye left, and
the question of whether the chroniclers' numbers were true. Lantern Road style. The narration, score and sound are the
original episode mix. First KINOFORGE version 21 Oct (64 shots); re-directed on 22 Oct after Sam's verdict ("too many cuts;
the first scene is sped up; it does not flow"): 9 scenes, 29 shots, real-time movement, fuller worlds. The blinding is never
shown. Styles: `docs/manual/styles/lantern-road.md`, `docs/manual/styles/dark-corners.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/dark-corners/kleidion/` (the old version was kept as `kleidion_old/` on 22 Oct; it is no longer in the tree) |
| Length, frames | 169.049 s, 4,058 frames at 24 fps |
| Picture | painted multiplane, `kf.js` core (half-resolution Kuwahara, 2-level bloom, one final pass); rendered 720x1280, delivered 1080x1920 |
| Edit | 9 scenes, 29 shots (was 64), average 5.8 s, one shot under 2 s ("The key."); only two dissolves (night falls; a day passes) |
| Sound | the original episode mix (`audio/mix.m4a` from rc-render release `dark-films`), untouched |
| Render | rc-render `films.yml` run 39797513657 (169.04 s), checked on a 2 s contact sheet, 22 Oct |
| Release | rc-render `kino-films`: `dark-corners-kleidion-lantern-road.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/dark-corners-kleidion-lantern-road-v2.mp4` |
| Cost | US$0 |
| Sam's verdict | v1 (22 Oct): too many cuts, sped-up opening, does not flow. v2: waiting |

## Files that make it
`film.json`, `index.html` (loads `scene.js` with the harness importmap), `scene.js` (boot, camera keyframes with the `glide`
ease, per-frame context `F`, captions, labels, title card, dissolves, the set cache; `window.__kf.audit()` prints every shot's
camera speed), `shots.js` (the shot table, captions from word timings, place and name `LABELS`), `kf.js` (painted planes with a
relightable material and a wind shear `uSway`, additive glow canvas, the lean post chain), `paint.js` (brush engine, unchanged
from p03), `figs.js` (people with a planted foot gait, back and front views, helmets, shields, spears; horses walk to gallop),
`ambient.js` (`birds`, `smoke`, `motes`, `shaft`, `shaftAB`, `hazeBand`, `paintGrassStrip`), `sets/` (road, march, page, city,
pass, camp, gorge, field, table, prilep, blank, common, index; `light.js` with `floorLight`, `rubble`, `ruts`, `ledgeTrees`,
`horizonGlow`), `cues.json`, `audio/mix.m4a`, `NOTES.md`.

## Why the first opening looked sped up, and the fix
Walkers moved at a constant screen speed while the road runs through a ten-fold change of scale; the camera jumped from wide to
close in two seconds; stride was set by time. Now every walker is driven in metres and metres per second on the ground (road
4 m wide, a person 1.75 m, a walk about 1.2 m/s), the screen position projects that ground point, and the gait phase is
distance divided by stride (`ph = d / (0.6 * 1.75 * stride)`). The opening is one continuous 8.4 s shot with a slow glide; the
escort halts at 4.2 to 5.4 s. The same rule drives the horses, the pursuers, the wall attack and the torch column.

## Scenes
1. The road, 0 to 12.19 s: a hill road at dusk; lanterns light group by group; close on hands on shoulders, "Blind."
2. The page, 12.19 to 18.65: the manuscript fills; candles dim to 50 %; the title card.
3. Two enemies, 18.65 to 34.99: Constantinople and Basil; Samuel at his fire; the tally plank fills to forty.
4. Near-death, 34.99 to 44.61: Basil's column in the gorge; Samuel among the dead lifts his head.
5. Kleidion, 44.61 to 76.74: the wall goes up (one 10 s dolly); "The key."; three waves; night (dissolve): the general's torches
   cross the mountain; rout, flares, the captives.
6. The escape and the gorge, 76.74 to 90.88: the son lifts his father into the saddle; the fires relit; the governor's column
   dies in a gorge; the banner lies still.
7. The order, 90.88 to 112.36: the wax seal; the chronicler's page; groups of a hundred walk home.
8. Prilep, 112.36 to 128.87: Samuel sees them, collapses; the cup held for eight seconds; dawn (dissolve), the window dark.
9. As they say, 128.87 to 169.05: the second manuscript, both numbers struck out; Bulgaria fights on; the nickname; the road at
   dusk, the last lantern goes out on "say"; end card at 166.45 s.
The reason for every one of the 29 cuts, what lives in every wide and the colour script: `films/dark-corners/kleidion/NOTES.md`.

## Exact steps to re-make it
1. Stills in time order (out of order once left an orange glow): `node harness/render.cjs films/dark-corners/kleidion --w 720 --h 1280 --start <f> --end <f+1> --jpg --out out/kleidion`;
   `?prof=1` logs set build times, `?hide=planeName` hides a painted plane. (NOTES.md measured with `node tools/dev.mjs`, a
   helper that is not in this repo; use `harness/render.cjs`.)
2. In the page console, `window.__kf.audit()` to check camera speeds.
3. Render: rc-render `films.yml` (`inputs[film]=films/dark-corners/kleidion`, 12 to 20 parts, full ref); check; deliver with `-v2`.

## Cost and time
On a shared 2 core box the old build took 6.85 s a frame and this one 6.36 s at the same moment (cost did not go up); on a quiet
machine the old build measured 0.9 to 1.3 s a frame at 720x1280. Sets build lazily on their first frame (2.5 to 14 s).

## Weak spots
- Horses and riders are flat profile silhouettes; the gorge walls are blocky slabs; the ledge trees hardly read.
- The night field is sparse (simple shapes in mist); characters at close range (march) are puppet-like.

## Sources of truth
`films/dark-corners/kleidion/NOTES.md`, its `*.js` and `sets/`, `film.json`, `cues.json`, `docs/LOG.md` (22 Oct),
`films/director/CRAFT.md`, `docs/LESSONS.md`.
