# Film recipe: Four seasons over one block (`cutaway-loop-seasons`)

A seamless 12 s social loop, 9:16: one block with a pond cut open on the front face, a year passing over it in one fixed
view with a 3 degree sway and no cuts. Sam's verdict (23 Oct 2026, 17:32 Toronto): he liked it ("barely any camera
movement, no cuts, lively world"); it became the base for all Cutaway work (`docs/manual/styles/cutaway-seasons-loop.md`).
Built and rendered on 22 Oct; on Sam's Mac and in release `kino-films`.

## Folder and every file
`films/cutaway/loops/seasons/`:
| File | What |
| --- | --- |
| `brief.md` | The story table (spring, summer, autumn, winter, each change with a visible reason); planned a 90 degree orbit, built as a 3 degree sway |
| `film.json` | id `cutaway-loop-seasons`, series "Cutaway loops", 12 s, 24 fps, 288 frames, render 720x1280, delivery 1080x1920, 40 spp, `loop: true`, `audio/mix.m4a` |
| `blender.py` | `build` and `frame` (scene contract), constants `AZ0 = -48`, `SWAY = 3`, `EL = 30`, `LENS = 55`, `WIDTH = 0.85`, `TZ = 0.32`, `SUN_AZ = -120`, `STRATA`, `SEASON`, `GRASS`, `LEAF`, `TREES`, `DROPPERS`, frog, ice, leaves, snow, birds, flies; opt-in art hook |
| `szworld.py` | Land and timeline in pure numpy: `LOOP = 12.0`, `S = 3.2`, `DEPTH = 1.25`, `LV = -0.05`, `STREAM`, `pond_sd`, `land_h`, `field`, `kc`, `weights`, `blend`, `win`, `CURVES` |
| `szmats.py` | Season-driven materials (`Drive` sets node values each frame) |
| `szlife.py` | Atmosphere, duck, fish, squirrel, acorn cache, robin and tracks, ammonite, title |
| `NOTES.md` | The art-direction hook (23 Oct) |
| `audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a` | The exact 12 s loop of sound |
| `studio-web/public/posters/cutaway-loop-seasons.jpg` | Its poster in the web studio (committed) |

## The film, second by second
| Time | Season | What changes (each with a reason we can see) |
| --- | --- | --- |
| 0 to 3 s | spring | the thaw ends, blossom, fresh grass and flowers, the frog swims up from its burrow, birds circle, roots grow in the face, morning mist on the pond |
| 3 to 6 s | summer | full green, the pond warm and bright (caustics), dragonflies, the frog at the surface |
| 6 to 9 s | autumn | leaves turn and fall from the two trees beside the pond, land on it and sink past the glass; the frog dives and digs into the mud; birds leave; ground fog |
| 9 to 12 s | winter | snow falls and settles, the pond freezes from the banks (ice in the cut face), the frog sleeps in its chamber (the surprise); then the thaw: melt, wet ground, birds return |

Life (`szlife.py`): a duck comes down the stream in spring and leaves in summer; fish circle behind the glass (slow in
winter); a squirrel buries acorns in autumn; a robin hops on the snow and leaves tracks. Eggs: an ammonite on the +X face
(`FOSSIL = (0.55, -0.80, 0.075)`), a vein of gold flecks in the gravel, the acorn cache under the front bank
(`CACHE = (1.18, 0.055, 0.04)`). Title "One pond. One year." (Inter Tight SemiBold from
`films/cutaway/ads/drainage/fonts/`, emission colour (0.20, 0.18, 0.16), size 0.125, parented to the camera at 5 m, in
the sky; on for the whole loop).

## Exact steps that made it
1. Picture: the scene as above; check frames locally with
   `python3 harness/blender_render.py films/cutaway/loops/seasons --w 270 --h 480 --samples 8 --start 100 --end 101`;
   seam check: render frames 287 and 0 and compare (`blender.py` docstring).
2. Sound: `python3 films/cutaway/loops/seasons/audio/make_audio.py` (writes `audio/mix.m4a` and `mix.json`; `mix.wav` local).
3. Commit, push, render on GitHub runners:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/loops/seasons' -f 'inputs[parts]=12' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   (LOG 22 Oct: "full render dispatched (12 parts)"; the run id is not recorded.) Each part renders its frames at
   720x1280, 40 spp (film.json), encodes crf 12; the join concatenates, lays `audio/mix.m4a`, scales to 1080x1920
   (lanczos, crf 17, maxrate 16M), writes `cutaway-loop-seasons.mp4`, `-preview.mp4` (540 wide), `-sheet.jpg`
   (fps 1/6, 8x4 tiles), and publishes to release `kino-films`.
4. Check (LOG 22 Oct: "rendered, checked, copied to Sam's Mac") and deliver to `Video Production/kino-films/`.

Expected assets in `kino-films` (seen 23 Oct): `cutaway-loop-seasons.mp4` (6,900,972 bytes),
`cutaway-loop-seasons-preview.mp4`, `cutaway-loop-seasons-sheet.jpg`.

## The sound (exact loop, free, deterministic)
`audio/make_audio.py`: notes and events start inside [0, 12) and render on a 36 s buffer with full tails and reverb; the
buffer is folded (0 to 12 + 12 to 24 + 24 to 36); noise beds periodic in the frequency domain; the limiter runs on three
copies and keeps the middle. Score: the free score engine (`films/lib/score`, Composer voices: string pad, harp-like
pluck, hall), D major, one chord per season at 0, 3, 6, 9 s: D(add9), G(add9), Bm, A(sus4). Ambience synthesised in the
script: wind all year (a whistle in winter), leaf rustle in spring and summer, birds in spring, summer and on the thaw,
frogs at the surface in spring (1.95, 2.45, 3.05, 3.9, 4.8 s), leaves dropping on the pond in autumn, ice creaks in
winter. Measured: 12.0 s, -18.02 LUFS, peak -2.0 dBFS, seam jump 0.040 against a 99.9th-percentile step of 0.152; score
-28 LUFS and ambience -26.1 LUFS before the mix.

## Cost
US$0 (GitHub runners, free tools). Per-frame time not recorded. Art looks on it: 10 to 35 s a frame at 270x480, 8 spp
on the 2-core chat box.

## Sam's verdict
23 Oct 17:32: liked; the base for Cutaway work (`docs/SOUL.md`, `films/director/CRAFT.md`).

## Weak spots
Not recorded as a list for this film. Known from the code: the kit trees are lumpy-blob miniatures (`cutaway.md`); the
title stays on for the whole loop.

## Variants made from it
Art-direction boards `films/cutaway/looks/seasons-<name>/` for all eleven Blender looks (frames 40, 100, 260):
`python3 films/cutaway/looks/make_seasons.py <name>`. Three were reviewed and accepted locally (fable, night-glow,
stained-glass); see `docs/manual/styles/cutaway-art-*.md`.

## To make a new one like it
Follow `docs/manual/styles/cutaway-seasons-loop.md` "Exact steps: a new film on this grammar".

## Checks before showing Sam
Seam (frames 287 and 0); length 12.0 s; 1080x1920; loudness about -18 LUFS (a quiet loop); a contact sheet; watch it loop
three times.

## Known traps
Winter reads at frame 260, not 230; drive season colours through nodes (the kit bakes a season at build time); one
height function for everything.

## Sources of truth
`films/cutaway/loops/seasons/*`, `docs/LOG.md` 22 and 23 Oct, `docs/SOUL.md`, `films/director/CRAFT.md`, rc-render
`films.yml`. The code wins if they disagree.
