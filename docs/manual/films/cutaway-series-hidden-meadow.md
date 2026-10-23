# Film recipe: The Hidden Meadow (`cutaway-series-hidden-meadow`)

Cutaway showcase series, film 3. 20 s, 9:16. Use it shows: wildlife documentary, kids, nature brands. A spring meadow in
soft morning light; below, in one column of the cut face, a rabbit warren (a doe and two kits), a mole digging, a fox den
with two cubs, an ant nest; a hawk's shadow sweeps the meadow, the two rabbits on top bolt into the burrow and arrive
underground; calm returns and the camera breathes out to the whole block. Rendered on GitHub runners, delivered 23 Oct.
Verdict pending.

Note for new work: three shots; the house default since 23 Oct 17:32 is one fixed view (`cutaway-seasons-loop.md`).

## Folder and every file
`films/cutaway/series/hidden-meadow/`: `film.json` (20 s, 24 fps, 480 frames, render 720x1280, delivery 1080x1920,
20 spp), `blender.py` (the whole scene; the extras' rabbit model copied in so its motion is the film's own), `NOTES.md`,
`audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a`.

## How the picture is built
- Block 1.6 x 1.6 m, 1.4 m deep, cut open on two faces. One column of homes on the -Y face (made for 9:16): warren mouth at
  u -0.30 (a notch in the cut edge, the top transparent there), chamber A (u -0.12, z -0.23, empty until the runners
  arrive), chamber B (u -0.34, z -0.37: doe and two kits on straw, breathing, ears twitching); mole tunnel u 0.07 to 0.37
  just under the turf with a molehill (extras `Eggs.mole`); fox den at u 0.12, z -0.57 (one cub asleep, one playing: play
  bow, pounce, back every 2.6 s, a bone), its run to a notch at u 0.60; ant nest entrance u -0.56, one gallery through four
  chambers (z -0.74 to -1.0), 24 ants with leaf bits, the queen, eggs, a leaf store, nine ants on the top trail.
- Burrows are hollows, not booleans: the wall material is transparent over each opening (extras `Eggs` masks) and a
  half-tube or bowl closes it from inside; a cavity material darkens with depth. Each home has a warm museum spot.
- Eggs: -Y face ammonite (u 0.30, z -1.11), trilobite (u -0.36, z -1.19), geode at the bottom (u 0.02, z -1.29); +X face
  hedgehog asleep under the turf (breathing), a lost amphora (z -0.62), a second geode (z -1.18).
- Top life: grass and flowers in the kit wind, 7 bees (wings at 23 Hz, figure-eight flights), 3 butterflies, 24 petals,
  46 pollen motes in the sun (camera only), the two grazing rabbits, 3 far birds, `ex.Shafts` god rays; three haze cards
  behind the block; no volumes anywhere.
- Light: morning sun from the side-back (az 158, el 27, warm (1.0, 0.82, 0.62), strength 7), weak cool fill (0.42), sky
  ambient 0.17 so the hawk's shadow reads; extras golden sky dome (bluer zenith for spring); `ex.finish` bloom and
  vignette; AgX Medium High Contrast, exposure +0.25.
- The hawk is never seen: a flat silhouette (0.75 m span) 0.85 m above the meadow toward the sun, seen by shadow rays
  only, plus the same silhouette laid over the grass tips as two soft dark veils exactly where the sun would throw it
  (dense backlit grass hid a real shadow); it crosses right to left (heading -0.77, -0.64; 1.1 m/s), over the grazing spot
  at 14.0 s.
- Title "The Hidden Meadow", Archivo (`ads/fonts/Archivo.ttf`), emission text parented to the camera at the focus
  distance, upper third, in 0.25 to 0.85 s, out 1.85 to 2.5 s. Nothing else written.
- Render settings: 20 spp, adaptive 0.04, OIDN, 4 bounces, no volumes, no motion blur.

## Shots (and why each cut)
| # | Shot | Time (frames) | Camera | Job |
| --- | --- | --- | --- | --- |
| 1 | meadow | 0 to 6 s (0 to 143) | low three-quarter (az -62 to -57, el 8 to 12, 42 mm, f/6.3) into the side-back sun; slow push settling on the burrow mouth | the world above; title |
| 2 | below | 6 to 12.5 s (144 to 299) | frontal on the -Y face (az -82 to -77, el 7 to 5, 40 mm, f/7.1); slow crane down the column, warren to ants | the reveal, motivated by shot 1 ending on the burrow mouth |
| 3 | hawk | 12.5 to 20 s (300 to 479) | three-quarter (az -50, el 20, 35 mm, f/8); holds while the shadow passes and the rabbits dive, from 16.4 s eases out to the whole block (el 23) | threat above and shelter below in one frame; resolution |
Events: rabbits look up 13.25 s, bolt 13.45 and 13.63, drop into the mouth 13.86 and 14.07, arrive in chamber A 15.10 and
15.38 s; doe and kits look up 13.05 s and relax 16.4 s; cub pounces 6.11, 8.71, 11.31 (lands 6.68, 9.28, 11.88 s).

## Exact render route that made it
1. Mac lane checks, five rounds (NOTES "Render cost"); best stills `out/hidden-meadow-check4/frames/00200.png` (the hidden
   world) and `check3/frames/00130.png` (the meadow) in the Mac's `kinoforge-render` folder.
2. Full film on GitHub runners, `films.yml`, 20 parts:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/series/hidden-meadow' -f 'inputs[parts]=20' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   Run 39896254752 (LOG 23 Oct; success 05:27 UTC).
3. Checked: 9:16, 20.0 s, -16.2 LUFS, no frozen frames; on Sam's Mac `Video Production/kino-films/series/`; sent.

Expected assets (seen 23 Oct): `cutaway-series-hidden-meadow.mp4` 24,984,016 bytes, with preview (540 wide), sheet, poster.

## The sound (`audio/make_audio.py`; sources in `films/cutaway/series/SOUND.md`)
Birdsong (`birds_waking_3`), crickets (`field_cricket`) and wind all through; bees crossing at 1.5 and 4.0 s
(`bumblebee_1`, `bumblebee_2`); below, muffled: the mole's paw strokes about 2.2 a second from 6.2 s (`steps_mud`), dirt
trickles (`dig_shovel`), straw rustles and cub landings at 6.68, 9.28, 11.88 s, ants; at 12.5 s a hush, two slow wing
beats overhead at 13.08 and 13.70 s (`flight_pigeon`, `flight_bird_1`; the bank has no hawk), a gust at 13.70 s, the rabbits'
bolts and dives, safe in the warren at 15.10 and 15.38 s; the meadow breathes again. Score: key G, cello, flute, pizz,
viola, violin; the music falls away for the hawk, 12.7 to 16.4 s; loudest 3 s 10.0 dB under the nature. Measured:
-16.1 LUFS, peak -1.99 dBFS, 20.0 s. The fox and rabbits themselves are silent (no recording).

## Cost
US$0. Mac checks 720x1280, 20 spp: 5 to 7 s a frame idle (about 45 to 55 min for 480 frames), 12 to 21 s when the Mac was
shared. Runner time for the film: not recorded.

## Sam's verdict
Pending.

## Weak spots (from NOTES)
The hawk shadow is half real, half art-directed (soft in a still); storybook scale (rabbits 2.35 x the extras model, ants
about 2 cm, dots with leaf bits at 1080 px); rabbits are rigid models that hop and pitch, the dive a head-first slide;
a thin highlight where tunnel tubes meet the face; kit trees read as a diorama; a plain sand band in the crane.

## To make a new one like it
Lay out one column of homes on the face for 9:16 first (a table of u and z); make hollows with masks and inner meshes, not
booleans; art-direct shadows that dense grass would hide. In the house default, keep the camera on one framing that holds
both the top and the column, and let the event happen in it.

## Checks before showing Sam
The shadow must never hang in the air (veils fade near the cut edges); the rabbits must read arriving below.

## Known traps
Dense backlit grass hides real shadows (only about a quarter of its brightness is direct sun); the burrows read as pipes
unless the cavity darkens with depth.

## Sources of truth
`films/cutaway/series/hidden-meadow/NOTES.md`, `blender.py`, `audio/*`, `films/cutaway/series/SOUND.md`, `docs/LOG.md`
(23 Oct). The code wins if they disagree.
