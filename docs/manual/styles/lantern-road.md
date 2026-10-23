# Style: Lantern Road (living painting, painted 2.5D multiplane)

Lantern Road makes a film look like a moving oil or gouache painting: every set is a stack of procedurally painted
canvases (thousands of tapered brush dabs over an underpainting) placed at true depths, so a dolly or a crane gives real
parallax; practical lights (lanterns, lamps, candles, torches) relight the paint around them; a warm and cool colour script
is carried by light, not by grade; a painterly Kuwahara pass, bloom, grain and vignette finish it. It is hand-built per film
in Three.js (WebGL in headless Chromium) on a shared core derived from the prototype `proto/p03-lantern-road`. Films:
Dark Corners Zong ("The Ship Called Care") and Kleidion ("As They Say"), both 9:16; NOOR samples Iqra and Juz Amma (16:9)
and the Iqra short (9:16). Good when the light tells the story, moves are slow and real, and every set breathes.

## Inputs
- The final sound and its timing (`audio/mix.m4a`, `cues.json` with line and word times, strong hits). The picture follows
  it and never retimes it.
- A scene list (5 to 9 scenes, each one place and one dramatic question) and a shot table with the reason for every cut.
- Tools: Node 22 and the harness (`cd harness && npm ci && npx playwright install chromium`).

## The look (what makes it this style)
| Element | Rule (as built) |
| --- | --- |
| Planes | each set is 6 to 10 painted canvases at depth D (sky, far peaks, mid ground, fog bands, ridges, road, near brush, out of focus foreground), scaled by D/f so they paint at screen density; colour from a value and temperature field with jitter, direction from a flow field, paper mottling |
| Relighting | plane shader = paint x ambient + paint luminance toward the light's hue x the sum of lantern lights with soft falloff (up to 8 lights a plane, `NL`); a lantern that catches warms the wall, road and fog around it; additive glow sprites feed the bloom |
| Finish | Kuwahara painterly pass (prototype radius 4 on the kit; Kleidion and NOOR `kf.js` half-resolution Kuwahara; Zong radius 2 by default, `--param kr=3` stronger), 2-level bloom, grain, vignette, shadow tint blue and highlight tint amber; tone mapping off so painted values render exactly |
| Fine-brush detail layer | figures, banners and small objects drawn per frame in screen space and composited after the finish with the same grade and a radius 1 Kuwahara, so a figure 1/40 of the frame survives |
| Type | crisp, drawn after the finish (never Kuwahara'd): Cormorant Garamond italic captions, Cinzel titles in the prototype; NOOR sets Qur'anic Arabic in Amiri Quran |
| Figures | planted gait: feet are world-space plants, gait phase = distance / stride, walkers driven in metres and metres per second on the ground (Kleidion: road 4 m wide, a person 1.75 m, a walk about 1.2 m/s) |
| Camera | multiplane camera (`glide` ease: ease in, steady middle, ease out); slow pushes, crane reveals, lateral tracks; `window.__kf.audit()` (Kleidion) prints each shot's pan, tilt and zoom speed in % of the frame a second |
| Living world | in every wide: wind in grass strips (shader shear `uSway`), smoke, birds, motes, haze bands, lamp flicker, shafts of light, water glints, small figures at work |
| Edit | 18 to 35 shots for 2.5 min (Kleidion 29 shots, average 5.8 s), hard cuts by default, a dissolve only for passing time or a change of world |

## Exact steps (a new film)
1. Start from the closest film: Kleidion (`films/dark-corners/kleidion/`, 9:16) or NOOR Iqra (`films/noor/n05-iqra/`, 16:9).
   Copy `kf.js` (multiplane core and post chain; change the design frame for the aspect: Kleidion 720x1280, NOOR 1280x720),
   `paint.js` (brush engine, unchanged since p03) and `ambient.js` (`birds`, `smoke`, `motes`, `shaft`, `hazeBand`,
   `paintGrassStrip`). Never edit another film's folder; copy.
2. Write `film.json` (`id`, `series`, `title`, `style: "lantern-road"`, `duration` = the mix length, `fps` 24, `render_w/h`,
   `w/h`, `audio`), `index.html` (the harness importmap for three and `scene.js` as a module).
3. Sets: one file per place in `sets/` (painted once per set, built lazily on its first frame, an LRU cache of 3 live sets).
   Each set returns its planes, lights and per-frame life. Paint at screen density for the lens you will use; close lenses
   (64 to 74 mm) soften wide sets (paint those at a higher quality).
4. `shots.js`: the shot table. Every cut time is a cue reference (a line start, a word, a strong hit), never typed seconds,
   so the picture re-fits a new take. Each shot names its set, camera keys and the reason for the cut.
5. `scene.js`: boot, camera keyframes, per-frame context, captions from the word timings, labels, title and end cards,
   dissolves, the set cache.
6. Stills: `node harness/render.cjs <folder> --w 720 --h 1280 --start <f> --end <f+1> --jpg --out out/<id>` per shot, or the
   NOOR tool `node films/noor/n05-iqra/tools/stills.cjs <folder> --shots` (two stills per shot; `--param dbg=1`,
   `noglows=1`, `glowoff=i`, `hide=plane`). Look at each. Render stills in time order (see traps).
7. Write `NOTES.md`: scenes (place, question, beginning, middle, end, camera plan), the shot table with the reason for each
   cut, what lives in every wide, the colour script, measured cost, weak spots.
8. Render on free runners: rc-render `films.yml` (`inputs[film]=<folder>`, `inputs[parts]` 12 to 20, full `ref`), release
   `kino-films`; NOOR used kinoforge `films-render.yml` to release `films`.
9. Check and deliver (`docs/PLAYBOOKS/check-before-showing-sam.md`).

## Alternatives
| Route | When |
| --- | --- |
| Clay (`clay.md`) | the story needs characters with weight and comedy timing, and a full 3D world |
| Kinetic (`kinetic.md`) | the story is documents and numbers; atrocity told by words and objects only |
| Cutaway (the Cutaway manual pages) | the story is what lies under the ground or the water |

## Checks before showing Sam
- Real-time moves: no constant screen speed across a big perspective change (Kleidion's first opening read as sped up).
- Shot count 18 to 35 per 2.5 min, a reason per cut, a hold after every key line.
- Three layers of motion in every wide; lights motivated (a lantern, a window, the moon).
- Restraint: Dark Corners shows no drowning, no bodies, no blinding; NOOR shows no person at all (`noor.md`).
- Captions never twice on screen, inside the phone safe zone on 9:16.

## Known traps
- Constant screen speed over a ten-fold change of scale reads as sped up: plan moves in metres per second, gait from
  distance (Kleidion diagnosis, `docs/LESSONS.md`).
- Rendering stills out of order (a later shot of a set before an earlier one) once left an orange glow; sequential renders
  were clean.
- A big glow mesh on the sky plane leaked over the peak (Iqra): tint the painted sky instead.
- A glow texture must be uploaded before the bloom reads it (Iqra).
- Vertical slats on painted peaks came from keying the value gradient to an unfiltered ridge function (p03 v3): box-filter
  the ridge.
- Kuwahara is about half the frame time; set builds cost 1.5 to 14 s once per set per render part.
- Figures stay silhouettes (Equiano, Sharp, horses in profile): honest weak spot in every film so far.

## Cost
Free on runners. Measured on the shared 2 core box at 720x1280: Zong about 2.1 to 2.3 s a frame at Kuwahara radius 2 (4.2 s
at radius 3); Kleidion 0.9 to 1.3 s a frame on a quiet machine; p03 2.8 to 3.6 s a frame at 1280x720. A 3 min film renders in
12 to 20 parallel parts in about 10 to 25 minutes on rc-render.

## Sources of truth
`proto/p03-lantern-road/NOTES.md`, `films/dark-corners/kleidion/NOTES.md` and `kf.js`, `films/dark-corners/zong/NOTES.md`
and `lib.js`, `films/noor/n05-iqra/NOTES.md`, `films/noor/j30-amma/NOTES.md`, `docs/SOUL.md` section 4,
`films/director/CRAFT.md`.
