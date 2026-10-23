# Film recipe: Under the City (`cutaway-series-under-the-city`)

Cutaway showcase series, film 2. 20 s, 16:9. Use it shows: infrastructure, real estate, trades, how a city works. A dusk
street of row houses on a block cut out of the city; the camera sinks down the cut face through pipes and cables, a brick
sewer with a rat, a metro train rushing past, old brick foundations, a Roman floor, and a T. rex at the bottom; then the
whole column at nightfall. Rendered on GitHub runners, delivered 23 Oct. Verdict pending.

Note for new work: three shots with a long crane; Sam's later verdict prefers one fixed view, no cuts
(`docs/manual/styles/cutaway-seasons-loop.md`).

## Folder and every file
`films/cutaway/series/under-the-city/`: `film.json` (20 s, 24 fps, 480 frames, 1280x720 to 1920x1080, 20 spp; note
lists check frames 40, 150, 200, 252, 320, 368, 440), `blender.py`, `NOTES.md`, `audio/make_audio.py`, `audio/mix.json`,
`audio/mix.m4a`. Kit and cinematic extras imported, never edited.

## How the picture is built
Layers top down (NOTES table): street (asphalt with a damp sheen, kerbs, 13 row houses with lit and dark windows, 4 street
lamps with light cones, 7 trees, a bus, a car, a steaming manhole, 3 birds, a far skyline behind a dusk haze card);
0 to 0.12 m asphalt and road base with a telecom cable carrying cyan light pulses; 0.12 to 0.52 m utility fill (blue water
mains, yellow gas, a district heating pair, an orange fibre duct, a clay storm drain, a concrete duct bank, the manhole
shaft with a ladder, a lost green bottle, an earthworm); 0.52 to 0.86 m clay with the brick sewer (flowing water, mist
card, walkway, a buzzing caged lamp, a drip every 1.7 s, the rat); 0.86 to 1.36 m grey till with the metro tunnel
(segment rings, track, warm lamps, a three-car train with lit windows and silhouettes, headlights, streak cards); 1.36 to
1.58 m rubble (a vaulted cellar with a barrel, a wall, a horseshoe); 1.58 to 1.80 m Roman loam (mosaic fragment with
missing tesserae, amphora with coins, a fluted column); 1.80 to 2.45 m fossil limestone (the extras' T. rex at scale
0.72, an ammonite, a trilobite); bedrock slate below.
Light: `ex.cine_light` dusk rig (sun az 112, el 4, deep blue zenith, cool fill, warm rim); the face lit by its own
practicals and museum spots; no volumes (haze, mist, steam, lamp cones and streaks are additive camera-only cards); dust
motes that shiver when the train passes. Finish: AgX Medium High Contrast, exposure 0.25, bloom (threshold 1.0, 0.28),
vignette 0.3. Final settings: glossy 1, transparent 6, adaptive threshold 0.05, OIDN. 31 lights, no glass water, no grass.
Title in Instrument Sans (`ads/fonts`) over the sky in the street shot.

## Shots (and why each cut)
| # | Shot | Time (frames) | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | street | 0 to 4.5 s (0 to 107) | high three-quarter (az -66 to -60, el 27 to 20), 35 mm, f/22, slow push down toward the cut edge | a living street at dusk; title |
| 2 | descent | 4.5 to 15.5 s (108 to 371) | crane straight down the -Y face, 35 mm, f/5.6, monotone eased curve through stations (street 4.5, pipes 6.4, sewer 8.3, metro 10.4, bricks 12.4, Roman 13.9, bones 15.5 s), last 1.6 s a push in from 2.15 to 1.7 m | the reveal: each layer older than the one above |
| 3 | city | 15.5 to 20 s (372 to 479) | wide low three-quarter (az -60 to -56, el 6 to 10), 35 mm, f/16, slow pull back and rise | the whole machine and its history |
Cut 1 to 2 on the push ending at the steaming manhole; cut 2 to 3 from the oldest thing straight out to the whole block.
Events: lamps flicker on 0.55, 0.87, 1.19, 1.51 s; windows 2.0, 3.3, 18.6 s; rat in 6.9 to 7.9, sniffs to 9.85, bolts
10.0 to 10.5; train nose at frame centre 10.74 s; second train below, centre 18.1 s.

## Exact render route that made it
1. Mac lane checks, five rounds (NOTES "Render cost" and "Log", 23 Oct 02:40 to 03:45 UTC).
2. Full film on GitHub runners, `films.yml`, 20 parts (LOG 23 Oct "On GitHub runners (films.yml, 20 parts)"):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/series/under-the-city' -f 'inputs[parts]=20' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   Run 39896034330 (success 05:04 UTC, 23 Oct; matches the release asset time).
3. Checked: 20.0 s, no frozen frames, about -16.3 LUFS, 1 fps contact sheet; copied to Sam's Mac
   `Video Production/kino-films/series/` and sent (LOG 23 Oct).

Expected assets (seen 23 Oct): `cutaway-series-under-the-city.mp4` 18,563,988 bytes, with preview, sheet and poster.

## The sound (`audio/make_audio.py`; sources in `films/cutaway/series/SOUND.md`)
Street at dusk (`paris_by_night`, `evening_birds`), the bus passing left to right at 0.2 s (`london_bus`), manhole steam
(`steam_hiss_1`); sewer bed (`sewer_1`), drips at 6.7, 8.4, 10.1 s (`drops_4`), rat claws (`pencil_2`) and a squeak
(`mouse_screams`) at 8.4 s, the bolt at 10.0 s; `train_passage_1` placed three times (SOUND.md spot
starts: "metro roars past" at 8.74 s, "rumble before the train" at 9.60 s, "second train far below" at 16.10 s, so the
roar peaks with the train at frame centre, 10.74 s); grit in the cellar at 12.4 s (`fall_of_stone`), a Roman drip at
13.9 s (`drops_3`), cave stillness from 11.3 s (`cave_2`); the street bed back from 15.3 s and a faint bus at 15.5 s. Score: key A minor to C, cello, harp, viola, violin; turn on the metro (10.74 s); loudest
3 s 10.0 dB under the nature. Measured: -16.18 LUFS, peak -1.88 dBFS, 20.0 s.
Rebuild: `python3 films/cutaway/series/under-the-city/audio/make_audio.py` (see `SFX_BANK`, `SCORE_SAMPLES` in
`docs/manual/films/cutaway-series-river-time.md`).

## Cost
US$0. Mac checks 1280x720, 20 spp: 3.2 to 4.8 s a frame cool; about 13 s a frame once the fanless Mac throttled (full
run estimate 1 h 45 min there). Runner time for the film: not recorded.

## Sam's verdict
Pending.

## Weak spots (from NOTES)
The T. rex skull lies apart from the neck (reads as broken, toy-like); the amphora reads as an orange blob at crane
distance; pale bands are large plain areas; train passengers are blobs and the train is boxy; the skyline is flat boxes;
people are about 15 px tall; no motion blur, so the train may strobe a little; the builder checked stills only.

## To make a new one like it
Write the layer table first (depth, layer, what is in it, job); keep each layer one idea; light the face with its own
practicals; a crane over the full block needs time (here 11 s). For the house default, hold one view and let the layers
come alive in turn instead of craning.

## Checks before showing Sam
Check frames 40, 150, 200, 252, 320, 368, 440; the check playbook; watch the train pass for strobing.

## Known traps
Tunnel end caps bulged out of the side faces until kept inside the block; face fill above 45 W read flat and toy-like;
limestone read washed white until darkened (NOTES log).

## Sources of truth
`films/cutaway/series/under-the-city/NOTES.md`, `blender.py`, `audio/*`, `films/cutaway/series/SOUND.md`, `docs/LOG.md`,
`docs/STATUS.md` (23 Oct). The code wins if they disagree.
