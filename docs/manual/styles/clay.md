# Style: Clay (stop-motion in Blender)

Clay makes a film look like a hand-animated stop-motion set: clay figures and props on a table world, animated on twos
(every channel sampled on even frames, the odd frame repeats it) with a small per-pose hand jitter, squash and stretch,
replacement smears and mouths, deadpan timing, shallow tabletop depth of field, pose-seeded grain, and paper-and-clay
graphics (cut paper cards with a tape strip, clay letters) instead of digital overlays. It is hand-built per film in Python
for Blender 5.2 (`bpy`) and rendered with Cycles on CPU. Origins: `proto/p10-clay` (a 6 s snail gag) and `proto/p15-moon-lesson`
(a 62.5 s clay classroom demonstration). Film: Dark Corners Arabia ("I Am Buying Her Life"), 9:16, re-directed on 22 Oct.
Good when the world is full (oases, fires, animals, cloth that breathes), the sky is crisp and the cuts are motivated.

## Inputs
- The final sound and timing (`audio/mix.m4a`, `cues.json` with words and `strong_hits`).
- A scene list and a shot list with a written reason for every cut (Arabia keeps them in code: `director.SCENES`, `WHY`).
- Blender 5.2 as a Python module: `pip install bpy==5.2.2 numpy` on Python 3.13 (runners), or the Blender app on Sam's Mac
  (Mac lane, Metal GPU).

## The look (what makes it this style)
| Element | Rule (as built in Arabia and p10) |
| --- | --- |
| Animation on twos | every channel is a function of the pose frame `pf = (i // 2) * 2`, plus a small per-pose hand jitter seeded with crc32 |
| Pair reuse | the odd frame of each pair renders only a 2x2 border and a `render_write` handler copies the even frame's PNG, so pairs are byte-identical and path tracing is halved (`KF_NO_PAIR_REUSE=1` turns it off) |
| Materials | clay (soft subsurface look), card, sand, striped cloth and emissive materials in `kit.py`; dunes as a height field with camel prints |
| Sky | its own Cycles scene with no depth of field, composited under the table scene (`film_transparent`): a painted card, about 11,000 emissive pin-hole stars in four classes (0.35 to 1.7 px), a Milky Way band, moon and halo, side wings so the sky holds when the camera looks along the table |
| Graphics | cut paper and clay in their own scene without depth of field: dated place card taped to the sky, name card, number tiles set into the sand, a verse on a scroll, the end card |
| World | `dress.py`: scatter of rocks, tufts and scrub, oases with palms, rugs, jars, saddles, fires with clay smoke puffs, goats, saltating sand, breathing tents, caravan lamps; foreground clusters out of focus at the bottom corners of low shots (near, middle, far layers) |
| Camera | trapezoid eases with real-camera speeds, slow pushes, arcs, cranes; time and scale changes hidden behind low walls or carried by a move rather than a dissolve |
| Compositor | sky under the table, HUD over it where shown, pose-seeded grain, a corner falloff; two to four node groups switched per frame |
| Music-hit pulse | `hit_env` from `strong_hits` drives lamp flicker, flame emission and tent glow |
| Restraint | modest wardrobe; what may not be shown is told by a lone lamp, a glowing tent, a silhouette in the cloth |

## Exact steps (a new film)
1. Folder with `film.json` (`style: "clay"`, `render_w` 720, `render_h` 1280 for 9:16, `samples` 24, `audio`) and a
   `blender.py` that follows the harness contract (`build` once, `frame` per frame, `SETTINGS`). Split the code as Arabia
   does: `kit.py` (materials, helpers, easing, text meshes), `world.py` (terrain, sky, lights), `actors.py` (figures, animals,
   tents), `props.py`, `dress.py` (the full world), `director.py` (scenes, shots, reasons, camera keys, HUD).
2. Stills locally at small size:
   `python3 harness/blender_render.py <folder> --out out/<id> --w 360 --h 640 --samples 8 --start <f> --end <f+1>`
   (36 stills in three passes was Arabia's QC); check the sky at full size (720x1280, 24 spp) separately.
3. Full-quality check stills on runners: rc-render `stills.yml` (`film`, `frames` up to 8, `tag`, `w`, `h`, `samples`, full
   `ref`); download with `bash tools/getstills.sh <tag> <dir>` in rc-render.
4. Do a no-render dry run over every pose (Arabia: build plus 2,110 poses, 0 errors) and a pair-reuse check through the
   real harness (pairs byte-identical).
5. Render: rc-render `films.yml` with about 24 parts (Blender films; about 80 min); or the Mac lane (`docs/PLAYBOOKS/render-on-the-mac.md`).
6. Check and deliver.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Mac lane (Blender app, `--device METAL`) | long or heavy renders when Sam's Mac is free; about 7 GitHub runners' worth | free, uses Sam's machine (fanless: slows after an hour) |
| Lower samples (`KF_ARABIA_SPP_CAP=16`) and fewer scatter tufts | the busiest shots are over budget | free |
| Lantern Road | a painted look with fewer characters | free |

## Checks before showing Sam
- Stars crisp pin-holes (no bokeh blobs) in a separate no-depth-of-field pass.
- Every cut has a written reason; no dissolves for show; 18 to 35 shots for 2.5 to 3 min (Arabia 31, one over).
- The bottom third of low shots is not bare (foreground clusters, scatter).
- Number tiles and cards are in focus when they land.

## Known traps
- A star card 5 m away through a lens focused at 0.4 m turns every star into a 30 px blob: stars need their own pass with no
  depth of field (`docs/LESSONS.md`).
- Muting the Render Layers node in the compositor gives a grey frame: switch node groups instead.
- The workflow passes `--samples 96`; Arabia's `build()` caps it at 20 (`KF_ARABIA_SPP_CAP=0` lifts the cap).
- The camera can end up inside the terrain: clamp it to the ground.
- A string of evenly spaced lamps reads as fairy lights: fewer, dimmer, irregular.
- Scene build takes 60 to 100 s once per render part; count it in the part budget.

## Cost
Free. Arabia at 720x1280 and 24 spp: 67 to 116 CPU-s a frame on a loaded 2 core box; with the 20 spp cap about 60 to 100
CPU-s, about 15 to 25 s wall on a 4 vCPU runner; pair reuse halves it to about 2,110 path-traced poses for 4,220 frames:
about 45 to 50 CPU-hours, 24 parts of about 30 minutes.

## Sources of truth
`films/dark-corners/arabia/NOTES.md` and its `*.py`, `proto/p10-clay/NOTES.md`, `proto/p15-moon-lesson/NOTES.md`,
`harness/blender_render.py`, `docs/SOUL.md` section 4, `docs/LESSONS.md` (Rendering).
