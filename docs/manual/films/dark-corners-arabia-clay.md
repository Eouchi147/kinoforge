# Film: I Am Buying Her Life (`dark-corners-arabia-clay`), Dark Corners, Clay (re-directed)

A 175.8 s, 9:16 Dark Corners episode: Arabia, around 600, where some families buried newborn girls alive; Sasaa of the Tamim
tribe pays his camels to save one girl and promises to save every girl he hears of; Zayd in Mecca does the same; years later a
famous poet writes of his grandfather. Clay style in Blender, with restraint: no burial and no infant on screen. The narration,
score and sound are the original episode mix. First KINOFORGE version 21 Oct (51 shots, then 49); re-directed on 22 Oct after
Sam's verdict ("the stars are not rendered properly, the cuts do not feel natural, the screen feels too bare"): a separate
pin-hole star sky, 31 shots in 9 scenes with a reason per cut, a fuller world, paper-and-clay cards.
Styles: `docs/manual/styles/clay.md`, `docs/manual/styles/dark-corners.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/dark-corners/arabia/` |
| Length, frames | 175.84 s, 4,221 frames at 24 fps (`DURATION` in code equals `film.json`) |
| Picture | Blender 5.2 Cycles CPU, OIDN; rendered 720x1280, delivered 1080x1920; animated on twos with pair reuse |
| Samples | the workflow passes `--samples 96`; `build()` caps it at 20 (`SPP_CAP`; `KF_ARABIA_SPP_CAP=0` lifts it); `film.json` `samples` 24 |
| Edit | 9 scenes, 31 shots, average 5.7 s, shortest 1.2 s (H4 reaction), longest 11.5 s; no dissolves |
| Sound | the original episode mix (`audio/mix.m4a` from rc-render release `dark-films`), untouched; -14.0 LUFS on the render |
| Render | rc-render `films.yml` run 39810673282 (24 parts; 175.8 s, -14.0 LUFS), checked on a 2 s contact sheet, 22 Oct |
| Release | rc-render `kino-films`: `dark-corners-arabia-clay.mp4`, `-preview.mp4`, `-sheet.jpg` |
| On Sam's Mac | `Video Production/kino-films/dark-corners-arabia-clay-v2.mp4` |
| Cost | US$0 |
| Sam's verdict | v1 (22 Oct): bad stars, unnatural cuts, bare screen. v2: waiting |

## Files that make it
| File | Holds |
| --- | --- |
| `blender.py` | harness contract, materials, the sky scene, compositor groups (sky, HUD), pair reuse |
| `kit.py` | clay, card, sand, striped and emissive materials; geometry helpers; easing; text meshes |
| `world.py` | height-field dunes with camel prints, sky card, pin-hole stars, Milky Way, moon, dawn sun, far ridge and caravan lamps, lights |
| `actors.py` | figures, camels, lamps, ropes, goat-hair tents that breathe, silhouette cutouts |
| `props.py` | clay lettering (cached glyph advances), lamp field, houses of Mecca, thorn bush, stamps |
| `dress.py` | scatter (about 1,200 tufts, 170 rocks, 55 scrub plants), palms and oases, fires and smoke, goats, drifting sand, rugs, pots, saddles, sacks, flags, foreground clusters |
| `director.py` | scenes and shots with reasons (`SCENES`, `WHY`), camera keys, the paper-card HUD, per-pose state, the music-hit pulse |
Plus `film.json`, `cues.json`, `audio/mix.m4a`, `NOTES.md` (the scene and shot tables are generated from `director.py`).

## Scenes (time, dramatic question)
1. The night search, 0 to 11.66 s: who is out there at night, and what does he find? (tilt from the stars to Sasaa; the tracks lead to two tents)
2. The old records, 11.66 to 18.94: can this be believed? (a scroll written in; the title raised in clay)
3. The hard years, 18.94 to 41.52: what was this world like for a newborn girl? (the name card; hunger; a lone lamp; one tent goes dark on "But it happened")
4. The two tents, 41.52 to 74.02: boy or girl? (the old man, the milk, the woman's tent; "It was a girl." held in silence)
5. The price, 74.02 to 98.85: will he sell her, and for what? ("I am buying her life"; five camels handed over, the last the one he rode)
6. The promise, 98.85 to 122.20: what does he do with what he has lost? (the vow under the stars; a field of lamps; number tiles 30, 96, 360, 400)
7. Mecca, 122.20 to 144.90: is he the only one? (Zayd and the father; she grows up behind three walls; "take her")
8. The poet, 144.90 to 160.42: what did the grandson say? (the verse in clay letters on a scroll)
9. Dawn, 160.42 to 175.84: who grew up? (one girl walks up the dune; the sun clears the ridge; end card in the last 2.6 s)
Every shot's reason: `films/dark-corners/arabia/NOTES.md`.

## Exact steps to re-make it
1. Install `pip install bpy==5.2.2 numpy` (Python 3.13).
2. Small stills: `python3 harness/blender_render.py films/dark-corners/arabia --out out/arabia --w 360 --h 640 --samples 8 --start <f> --end <f+1>`;
   the star sky at full size: `--w 720 --h 1280 --samples 24` at t=94 s and t=125.5 s (frames 2256 and 3012).
3. Render: `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/dark-corners/arabia' -f 'inputs[parts]=24' -f "inputs[ref]=$(git rev-parse HEAD)"`
   (about 80 minutes). Or the Mac lane.
4. Check (stars, the bottom third of low shots, tiles in focus), deliver with `-v2`.

## Cost and time
Measured (720x1280, 24 spp, loaded 2 core box): 67 CPU-s (tents and faces), 80 to 93 (night sky with the Milky Way), 116 (Mecca
street with a card); with the 20 spp cap about 60 to 100 CPU-s, about 15 to 25 s wall on a 4 vCPU runner. Pair reuse halves
the path-traced count to about 2,110 poses: about 45 to 50 CPU-hours, about 24 parts of 30 minutes. Scene build 60 to 100 s
per part. Levers if too slow: `KF_ARABIA_SPP_CAP=16`, fewer scatter tufts in `build_dress`.

## Weak spots
- The lowest wide shots still show smooth sand in the bottom third (softened by the clusters, not removed).
- The Milky Way band is painted and slightly diagonal at the left end, reading as a brush stroke.
- The sky above about 25 degrees on the side wings has no stars (seen only when the camera looks along the table).
- Dawn streaks can shimmer a little at 24 spp; figures are small in the widest shots; 31 shots is one over the guide.

## Sources of truth
`films/dark-corners/arabia/NOTES.md`, its `*.py`, `film.json`, `cues.json`, `harness/blender_render.py`, `docs/LOG.md` (21 and
22 Oct), `docs/LESSONS.md` (stars need their own pass).
