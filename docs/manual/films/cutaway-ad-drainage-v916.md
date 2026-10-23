# Film recipe: Sample trade ad, drainage and landscaping, 9:16 (`cutaway-ad-drainage-v916`)

A 15 s vertical trade ad for an INVENTED business, "Fieldstone Drainage and Landscaping", marked Sample on screen, with
no phone and no website ("Your logo here" on the end card), so nobody mistakes it for a real company. Purpose (brief):
show Unmissed's trade clients (landscaping, drainage, pools, plumbing, foundations) an ad no local competitor has: the
cut shows the work the customer never sees. A soggy yard, the water trapped on clay in the cut face, the drain laid as a
time-lapse, a dry sunny lawn with a robin. Music only (free score engine), words on screen. Rendered on GitHub runners
and copied to Sam's Mac (23 Oct). Verdict pending. The 16:9 twin is `cutaway-ad-drainage-v169` (same scene).

## Folder and every file
`films/cutaway/ads/drainage/`:
| File | What |
| --- | --- |
| `brief.md` | the four beats, words, safe box, sample rules |
| `ad.py` | the shared scene for both deliveries (yard strata with perched water, trench, gravel, pipe, downspout, fence, shrubs, patio, robin, worm, ball, words, camera plan) on the kit |
| `v916/blender.py` | three lines: picks `'9:16'` and calls `ad.build` / `ad.frame` |
| `v916/film.json` | id, 15 s, 24 fps, render 720x1280, delivery 1080x1920, 48 spp, `audio/mix.m4a` |
| `v916/audio/mix.m4a`, `score.json` | the music (written by `music.py` into both folders) |
| `music.py`, `score_plan.json` | the music recipe |
| `fonts/InterTight-ExtraBold.ttf`, `InterTight-SemiBold.ttf`, `OFL.txt` | the words' face (OFL) |

## The four beats (brief and `ad.py`)
| Time | Picture | Words (set in code) |
| --- | --- | --- |
| 0.0 to 3.0 | a backyard block after rain: a puddle on the lawn; the cut face shows water trapped above heavy grey clay | "Soggy lawn / after every rain?" (0.30 to 2.80 s) |
| 3.0 to 6.5 | slow push to the cut face: the water sits on the clay and has nowhere to go | "The problem is / under the grass." (3.15 to 6.25 s) |
| 6.5 to 11.5 | the fix as a time-lapse: trench opens (6.55 to 7.60), gravel bed (7.45 to 8.05), perforated pipe settles (7.95 to 8.55), gravel cover (8.50 to 9.10), backfill (9.05 to 9.60), turf returns (9.50 to 10.05); the soil water draws down into the pipe and out of its mouth (9.00 to 11.30); the puddle dries (9.35 to 11.05) | "We fix what / you can't see." (6.75 to 11.20 s) |
| 11.5 to 15.0 | sun, the lawn dry and green; a robin flies in (11.2 s), pecks and pulls a worm; a kid's ball rolls out of the shrubs | end card from 12.25 s: the sample name, Sample, Your logo here, "Book a yard check" |

Yard: `SX = SY = 3.0` m, `DEPTH = 0.85`, strata turf, topsoil, loam, then heavy grey-blue clay from 0.28 m
(`CLAY_S`), perched water 0.10 m above the clay at the start; trench along x at `Y0 = -0.32`, width 0.26, floor 0.46 m,
pipe radius 0.055, from the downspout at the house wall (the house is off the block beyond -X) to the +X cut face.
Words: camera-parented text in Inter Tight with a soft shadow, landing with a fade and a small settle; `build()` checks
every word sits inside the social safe box R-2-08 of the 9:16 frame (`SAFE_916 = (0.11, 0.78, 0.15, 0.65)`: x0, x1, y0,
y1 as fractions, y from the top) and fails the render if any word leaves it.
Camera (`CAM['9:16']`, keys at 0, 3, 6.5, 11.5, 15 s: azimuth, elevation, distance factor, target): (-44, 18, 1.00),
(-40, 15, 0.92), (-12, 4, 0.31, target at the +X face by the trench), (-27, 17, 0.50), (-37, 21, 0.95); eased; base camera
`az -44, el 18, lens 55, fill 0.98, top_extra 0.62`. Settings: 48 spp, OIDN ACCURATE, AgX Base Contrast, exposure 0.2,
max bounces 8, clamp indirect 6.

## Exact steps that made it
1. Music (both folders at once):
   `SCORE_SAMPLES=<folder with Strings/ and Woodwinds/ of VSCO-2 CE (CC0)> python3 films/cutaway/ads/drainage/music.py`.
   The engine plans long films (its tonic resolve sits 11 s before the end), so `score_plan.json` is 22.5 s long (early
   modern Europe palette, F ionian, 84 bpm, seed 3, solo flute, frame drum; sections calm 0, turn 8.1, triumph 11.5;
   hits: a swell at 6.5 s, a harp chime at 11.55 s); the script keeps 0 to 15 s, fades the last 2.4 s, normalises to
   -14 LUFS (peak under -2 dBFS), sets true silence on the last 20 ms, and writes `v916/audio/mix.m4a` and
   `v169/audio/mix.m4a` (AAC 256k) plus `score.json` (measured -14.03 LUFS, engine samples+synth).
2. Local look: `python3 harness/blender_render.py films/cutaway/ads/drainage/v916 --w 360 --h 640 --samples 16 --start 200 --end 201`.
3. Push, then render on GitHub runners (LOG 22 Oct: "both formats dispatched for render"; parts and run id not recorded;
   the playbook value for Blender films is 24):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/ads/drainage/v916' -f 'inputs[parts]=24' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   The join lays the music and scales to 1080x1920.
4. Checked (15 s, -14.2 LUFS) and copied to Sam's Mac (LOG 23 Oct: "Drainage ads (both formats, 15 s, -14.2 LUFS) and both Agincourt inserts
   landed; ads copied to Sam's Mac").

Expected assets (seen 23 Oct): `cutaway-ad-drainage-v916.mp4` 10,191,774 bytes, `-preview.mp4`, `-sheet.jpg`.

## Cost
US$0 (runners, free tools). Per-frame time not recorded.

## Sam's verdict
Pending (`docs/SOUL.md` lists the drainage sample ad under "Waiting on his verdict").

## Weak spots (LOG 22 Oct)
The framing crops the house at the left edge; the puddle reads weakly in stills.

## Rules this film must keep
Invented business marked Sample; no phone, no website; no claims about Unmissed; words in code, one face, inside R-2-08;
no dash, no "..." on screen; nothing published or sent before Sam has watched it (`films/cutaway/README.md`).

## To make a new one like it (another trade)
1. Copy `ads/drainage/` to `ads/<trade>/`; keep the four-beat shape (problem in the yard, the cause in the cut, the fix as
   a time-lapse, the result with life).
2. Change the strata and the hidden problem in `ad.py`, the words in `WORDS`, `NAME`, `CTA`; keep `SAFE_916` checking.
3. A real client: their own written words only (`harness/shots/policies/unmissed.md`, `docs/decisions/0012`), and Sam
   approves before anything is sent.
4. Music: adjust `score_plan.json` hits to your beats; run `music.py`.

## Checks before showing Sam
The safe box (build fails if broken); length 15.0 s; -14 LUFS; every word legible on a phone; Sample visible.

## Known traps
The score engine resolves 11 s before a plan's end: plan longer than the ad and cut it.

## Sources of truth
`films/cutaway/ads/drainage/brief.md`, `ad.py`, `music.py`, `score_plan.json`, `v916/*`, `docs/LOG.md` (22 and 23 Oct),
`docs/SOUL.md`. The code wins if they disagree.
