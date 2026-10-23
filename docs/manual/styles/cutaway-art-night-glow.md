# Cutaway art look: night-glow (bioluminescent night)

The Cutaway block at night, alive with light: a deep night sky with stars, a large pale moon low behind the block with a
halo, a faint green aurora on the horizon; surfaces dark and cool, and the life and the finds give the light (cyan root
veins, glimmering pebbles, glowing bones and gold, a luminous river, fireflies). Board sent to Sam on 23 Oct; his pick is
pending.

## Inputs
A line film or a kit scene with the art hook (`cutaway-art.md`); module `films/styles/cutaway/art/night-glow.py`, helpers
`_jewel.py`.

## What it changes
- Every material: moonlit dark paint (a hard silver terminator) plus emission for what glows. Glow colours: cyan
  (0.30, 1.00, 0.92), sea (0.45, 1.00, 0.70), lime (0.70, 1.00, 0.40), gold (1.00, 0.72, 0.28); `GLOW` maps egg
  materials (`ex_bone`, `ex_tooth`, `ex_nacre`, `ex_trilo`, `ex_gold` and others) to a colour and strength.
- Cut faces: night strata colours (`STRATA_NIGHT`: violet and blue bands), faint blue lines between layers, cyan veins of
  light hanging from the turf, pebbles glimmering like plankton.
- Finds: bones and the ammonite glow sea-green at their edges (facing angle), the gold vein and the chest burn warm.
- River: luminous turquoise from inside with brighter ripple lines; grass tips and moss spots glow green; trees carry
  speckles of light; village windows lit; 70 fireflies (the cinematic extras' own, blinking).
- World: night sky, stars, moon (lowered to 9 degrees so it sits in the hero frame), aurora; the floor.
- Lights: sun turned into a cool moon; fill, rim, edge spills, god rays and cloud shadows off; museum spots dimmed.
- Compositor: wide soft bloom, vignette; AgX view kept so glows roll off softly; words crisp in their own layer (pale
  plates, midnight ink).
- On the seasons loop: season materials keep their colours, dimmed less than the rest; grass tips, snowflakes, the ice
  edge, the frog, the acorns and the fish glow; `sz_haze` hidden; the loop re-poses the sun each frame, so this look
  turns it back into the low cool moon every frame; the title is pale with no plate.

## Exact steps (apply it)
1. Line film: `"look": {"art": "night-glow"}` in `spec.json`, or `KF_ART=night-glow`.
2. Seasons board (exists): `films/cutaway/looks/seasons-night-glow/`; check
   `python3 harness/blender_render.py films/cutaway/looks/seasons-night-glow --w 270 --h 480 --samples 8 --start 260 --end 261`.
3. Meadow board (exists): `films/cutaway/looks/night-glow/`; check frames 440 and 830 at 480x270, 8 spp.
4. Full size on the Mac lane or rc-render `stills.yml` / `films.yml`.

## Cost per frame
About the reference or cheaper (mostly emission, 3 bounces, no glass refraction; fireflies are tiny emitters). Measured
on the shared 2-core box at 480x270, 8 spp: about 60 s (box busy; the reference was 21 s there when quieter). Seasons
loop at 270x480, 8 spp: 13 to 35 s.

## Best uses (from NOTES)
1. Natural history museums, aquariums and science centres: night-life and soil-life explainers, planetarium loops.
2. Fantasy and gaming brands, light festivals, night markets, zoo night openings: teasers and social loops.
3. Wellness, sleep and meditation apps: calm loopable backgrounds (fireflies, glowing water, slow moon). The seasons loop
   grammar suits this best.

## Weak spots
- Bands all sit in the blue to violet range: less distinct than in daylight.
- Fireflies are specks below full size.
- Edge glow uses the facing angle: flat finds seen straight on (the amphora) glow less.
- Root veins are a shader on the flat wall.
- On the seasons loop the camera looks down, so the moon, aurora and stars are out of frame (a dark floor behind); summer
  grass tips glow busily.

## Alternatives
`fable` (same jewel family by day), `stained-glass`.

## Checks before showing Sam
The title must stay readable (round 1 on the loop: a dark title vanished on the dark ground; fixed with a pale title).

## Known traps
Rounds in NOTES: first pass too dark to read, root veins a uniform curtain, moon out of frame (fixed by lifting band
colours, thinner varied veins, moon at 9 degrees). Keep egg openings with `_jewel.under_mask`.

## Sources of truth
`films/styles/cutaway/art/night-glow.py`, `_jewel.py`, `films/cutaway/looks/night-glow/NOTES.md`,
`films/cutaway/looks/seasons-night-glow/NOTES.md`. The code wins if they disagree.
