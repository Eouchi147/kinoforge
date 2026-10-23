# Film recipe: The Sleeping Volcano (`cutaway-series-sleeping-volcano`)

Cutaway showcase series, film 6. 20 s, 16:9. Use it shows: drama, natural hazards, science explainers (how a volcano
works, in one picture). A green island volcano on a 3 m block of turquoise sea at golden hour; the -Y cut runs through the
crater, so the face is the textbook section (nested cone layers, conduit, magma chamber); the magma wakes and climbs,
birds lift, steam turns to smoke, and at dusk a gentle eruption sends a lava stream down to the steaming sea. No people
anywhere. Rendered on GitHub runners, delivered 23 Oct. Verdict pending.

Note for new work: three shots; the house default since 23 Oct 17:32 is one fixed view (`cutaway-seasons-loop.md`).

## Folder and every file
`films/cutaway/series/sleeping-volcano/`: `film.json` (20 s, 24 fps, 480 frames, 1280x720 to 1920x1080, 20 spp; note
says "Render on the Mac lane (METAL)", but the final render ran on runners), `blender.py`, `NOTES.md`,
`audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a`.

## How the picture is built (from NOTES)
| Element | Job |
| --- | --- |
| Cone on the -Y cut (crater cut in half) | the hero: shape and section in one image |
| Nested cone layers, old sea floor below, a soft unconformity at z = -1.05 m | the science; the wall's `sd` attribute is recomputed in this film (the kit's default turned the tall cone into one dark band) |
| Magma chamber | breathes (3.2 s cycle) while asleep, brightens from 4 s, flickers |
| Conduit and seven side cracks | a rising front lights them from 6.9 to 13.2 s |
| Chamber, conduit and crater lights | glow on the strata, the cone and the smoke's underside |
| Forest belt low, bare dark rock above | alive island, volcanic summit |
| Turquoise sea with corals, weed, pebbles, two fish schools behind the glass | life and scale |
| Steam wisp, smoke, ash plume (billboard cards) | the escalation as one rising column |
| 120 lava bombs on slow-gravity arcs, 90 embers, a vent halo | the eruption, gentle |
| Lava stream (ribbon draped on the flank, revealed by a front, crust cooling behind) | the consequence, ending in the sea |
| Sea steam at the lava entry | fire meets water |
| Golden hour to dusk (sun, sky, fill, floor fade 8 to 17 s) | time passes; the lava becomes the key light |
| Low mist cards over the sea | depth without a volume |
| Title "The Sleeping Volcano" (Archivo, warm white, 0.25 to 2.5 s) | the name |
Eggs: a geode left of the chamber (-Y), an ammonite in the sea-floor sediment (-Y), a pirate chest under the sea floor
(+X), a trilobite deep on the +X face. Settings: 20 spp, adaptive 0.04, OIDN, max bounces 4 (transparent 16), no volumes,
no motion blur; 378 objects. Fade to black over the last 0.8 s.

## Shots (and why each cut)
| # | Shot | Time (frames) | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | island | 0 to 6.5 s (0 to 155) | wide three-quarter from the +X/-Y side, 35 mm, eased push 8.7 to 7.9 m, 4 degree arc | the sleeping island; title above the cone |
| 2 | rise | 6.5 to 13.5 s (156 to 323) | close on the chamber (38 mm, f/6), cranes up the face with the magma front to the crater, tilting down 4 to 20 degrees and pulling back | the cause; arrives as the birds lift |
| 3 | eruption | 13.5 to 20 s (324 to 479) | low wide (28 mm, 9 to 10.5 degrees up), slow 7 degree arc and push; one damped vertical jolt at 14.2 s | the climax and the end image (cut 0.7 s before the first fountain) |
Check frames: 30, 120, 175, 235, 300, 345, 420, 450. Best still: round 5 frame 420 (on Sam's Mac,
`Video Production/kinoforge-render/out/sleeping-volcano-check5/frames/00420.png`).

## Exact render route that made it
1. Five Mac-lane check rounds (NOTES "Render cost").
2. Full film on GitHub runners, `films.yml`, 20 parts:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/series/sleeping-volcano' -f 'inputs[parts]=20' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   Run 39895728062 (success 04:53 UTC, 23 Oct; the LOG lists it second of three with River and City, and its end time
   matches the release asset time).
3. Checked: 20.0 s, no frozen frames, -16.4 LUFS (STATUS); 1 fps contact sheet; copied to Sam's Mac
   `Video Production/kino-films/series/` and sent.

Expected assets (seen 23 Oct): `cutaway-series-sleeping-volcano.mp4` 14,053,249 bytes, with preview, sheet and poster.

## The sound (`audio/make_audio.py`; sources in `films/cutaway/series/SOUND.md`)
Waves (`small_waves_ocean`), forest bed, gulls at 0.3 s (`gulls_harbor`), a far fumarole hiss at 0.5 s (`steam_hiss_3`);
from 4.0 s a felt rumble (`thunder_3` slowed) and mud-pot boil (`big_broth`, slowed); rock cracks as the magma climbs at
7.8, 9.4, 11.3, 12.7 s (`ice_crack_*`, slowed); the hiss thickens at 10.0 s; a flock takes off 10.9 to 11.25 s
(`flight_*`) with alarm calls (`crows_1`); a beat of quiet at the dusk cut; the eruption boom at 14.2 s (`thunder_2`) and a
rock tumble; fire beds (`fireplace_2`, `fire_branching_1`), bombs thudding at 15.4, 16.5, 18.3 s; the lava meets the sea at
17.7 s (`water_that_burns`) and steam roars up (`steam_hiss_3`). Score: key C, cello, harp, viola, violin (deep drones);
swells at the eruption (14.2 s) and settles; loudest 3 s 10.0 dB under the nature. Measured: -16.34 LUFS, peak -1.79 dBFS.

## Cost
US$0. Mac, 1280x720, 20 spp: 4 to 6 s a frame cool, 9 to 15 s hot (one 21 s outlier); full film 35 min to 2 h there.
Runner time: not recorded. Levers: 16 samples, drop the 3 mist cards, fewer plume cards (18 to 12).

## Sam's verdict
Pending.

## Weak spots (from NOTES)
Smoke is cards (soft blobs up close; grainy small puffs 14.2 to 14.6 s before the column fills); the cone face is dark at
dusk (layers fade into shadow); the lava stream reads as a glowing line through the trees; the chamber's lava-lake pattern
is a little regular; kit trees and simple birds; cracks read as thin black lines before the magma reaches them; a soft
horizon line at dusk; the builder checked stills only.

## To make a new one like it
Cut through the feature (the crater) so the face is the diagram; recompute the wall `sd` when the top is tall; drive the
whole palette from a light change (golden to dusk) so the climax lights itself.

## Checks before showing Sam
Watch the plume and fountain move (the builder could not); 20.0 s; -16 LUFS; the fade to black.

## Known traps
The kit's default strata coordinate flattens to the mean top height: recompute `sd` for tall tops.

## Sources of truth
`films/cutaway/series/sleeping-volcano/NOTES.md`, `blender.py`, `audio/*`, `films/cutaway/series/SOUND.md`,
`docs/LOG.md`, `docs/STATUS.md` (23 Oct). The code wins if they disagree.
