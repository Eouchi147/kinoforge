# Agincourt mud: the two Cutaway inserts for "The Battle of Agincourt" (Battle Map)

Brief: `brief.md`. Scene code: `agin_mud.py` (shared world, figures, timing), `A/blender.py`, `B/blender.py` (the shots).
Free: Blender bpy 5.2.2, Cycles CPU, the Cutaway kit (`films/styles/cutaway/cutaway.py`, imported, not edited).
Every beat is read from `films/battles/agincourt/cues.json` words (`W(line, word)`), every pose is a function of the film
time T, so a re-timed voice moves the picture with it (re-render needed).

## For the join (lead): where the inserts go

Spans are the cue rule: start of the first line to the start of the line after the last. 24 fps, film frame f shows
t = f / 24. Insert frame i (0-based, `out/frames/00000.png` ...) replaces film frame `first + i`.

| Insert | Cues | Film seconds | Film frames (inclusive) | Count | Insert duration |
| --- | --- | --- | --- | --- | --- |
| A | l06 to l07 (l08 starts at the end) | 57.284 to 71.982 | **1375 to 1727** | 353 | 14.698 s (353 frames) |
| B | l10 to l11 (l12 starts at the end) | 86.703 to 100.867 | **2081 to 2420** | 340 | 14.164 s (340 frames) |

- ffmpeg: take the film's frames `[0, 1375)`, then A's 353 frames, then film `[1728, 2081)`, then B's 340, then film
  `[2421, end)`; the film's own `audio/mix.m4a` runs unchanged under all of it (the inserts have no sound).
- In and out are hard cuts on line starts (the voice begins a new line on each cut), which is a cut "on the end of a
  sentence" (CRAFT 3). A does not need a dissolve: the film's wet stage and rain begin on the same word (57.28).
- Render 1280x720, deliver 1920x1080 (scale up in the join, like the film itself).

## Shot plan (camera per insert, every cut with a reason)

**A (14.70 s).** A1, 57.28 to 62.00 (end of "mud." plus 0.55 s): high and wide from the French side, the block as a
map, rain streaks, rings spreading in the furrow puddles, the soaked layers in the cut faces, the small red line of
archers on the far edge; one slow push down. Cut: change of scale, from the trap to the people who use it. A2, 62.00 to
71.98: low on the -Y cut face at the English line, looking along the zigzag row of stakes. Three mallet blows per stake
in a wave from the near face outward, the first on "hammered", the last before "them."; the nearest stake sits on the
cut face, so we see its point go into the soft wet layer in section. On "Then Henry moved his whole army forward" the
red men-at-arms come up behind the archers and the camera eases up and back to show the line facing the long wet field;
on "close enough to shoot" the archers lift their longbows.

**B (14.16 s).** B1, 86.70 to 93.91: very low at the -Y cut face (24 mm lens at soil level, the legs in the foreground),
a slow track with the French front file walking away to the right (France left, England right, the same screen
direction as A2). On "advanced" the crows on the field edge ahead of them lift and fly off. Through the face we see their armoured legs go into the
soft layer; strides shorten, ankle deep on "advanced", knee deep on "knees", where the soldier in the middle of the
frame stops dead and wobbles and the next one bumps up behind him; 1.2 s hold. Cut (0.15 s before "The woods"): change
of scale, from the legs to the army. B2, 93.91 to 100.87: high behind the English stakes, a slow rise; the blue column
comes at us between the two woods, the files close together in the neck ("squeezed", "packed"), and on "swing a weapon"
the poleaxes clatter into each other.

## Layout and look

- Block 4.2 x 3.2 x 0.66 m. March along +X: France enters from -X, England holds the +X end. The -Y face is the cut face the
  French front file walks on (file 0 is placed exactly on it, legs straddling the plane; a boolean against a solid
  outside the face, below the terrain line, cuts their buried parts flush, so they show as sections in the soil).
- Woods: Agincourt wood along +Y; Tramecourt wood bulging in from -Y in the middle: the neck. Autumn leaves (25 October).
- Field: plough furrows across the march (period about 9 cm, wandering, rounded crests, uneven height), clods, about 320
  boot and hoof holes, muddy puddles in the low troughs and holes (glass, brown absorption, rain rings in A).
  Strata: soft wet mud 7.8 cm (dark, glossy), wet loam, clay, chalky marl, deep (Picardy loess over chalk); the kit's
  root lines are switched off (a ploughed field). The French sink to the knee inside the soft band.
- Figures about 0.17 m: French in carthage blue surcoats with a gold hem and gold disc, steel arms and legs (mud caked
  below the knee), bascinets with the pointed visor, poleaxes; two French banners (blue, gold border, gold disc,
  swallowtail, as the film's). English archers in rome red jacks, kettle hats, quivers, longbows, mallets; red
  men-at-arms with two red banners. Colours from `films/lib/battlemap/blocks.js` TEAMS.
- Light: A grey rain light, mist lying and drifting in both woods; B a low warm sun breaking through behind the
  Agincourt wood into a thin ground haze (god rays through the trees), grey sky. A soft fill from the -Y side lifts the
  cut face in both.
- Life (Sam, 22 Oct: fauna and flora animated, easter eggs in the soil): crows pecking on the field edge (they lift
  in B as the French come), earthworms wriggling in the wet layers of the cut face, wind in grass and trees, banners
  waving, rain and puddle rings in A. Easter eggs, small and deep in the face: a Roman bronze coin in the clay under the
  English stakes (A2), an ammonite in the marl under the French (B1).
- Built locally in `agin_mud.py` (Crows, Worms, easter_eggs, haze, mist); swap for the shared
  `films/styles/cutaway/cinematic/` pieces when they land.

## Measured

Local build (no render) on the shared 2-core box: about 5 to 8 s; frame pose and evaluation about 1 to 3 s (the face
legs use the Manifold boolean solver; EXACT was about 40 s per frame for B).

## Check stills (rc-render stills.yml, release "stills")

Last approved-by-eye rounds: A `agin-r5A-f*` (commit 90a37e1), B `agin-r7B-f*` (commit 0ee3b60). Local copies:
`/tmp/claude-0/-home-claude/b576bd3d-71d2-5bea-b286-3ba8d53b8c9d/scratchpad/agincourt-board/`. Runner time: about 3 to 4 min
per frame for A2 and B1 close shots, about 2 to 3 min for the wides (64 spp, 1280x720).

## Known weak spots
- God rays in B are subtle (thin haze, low sun 13 degrees behind the Agincourt wood): the light is warm and raking with
  long shadows, but there are no strong shafts. More haze makes B1 milky; a separate shafts pass would be the next step.
- Furrow crests close up (A2) still catch the grey sky and read slightly plastic; they do read wet.
- The crows are small in B1 (they lift on "advanced" ahead of the file, top right of frame).

- B1 sinking in the section (coordinator, 22 Oct): file 0 straddles the cut plane until the Tramecourt wood; shin deep from
  the start, knee deep on "knees"; each boot is pulled up to the surface as it swings forward (slow strides), a fat mud lip
  rings each leg at the face, and every pulled-out boot leaves a dark hole in the section that closes up behind it.
- The mud surface itself does not deform around the boots (no ruts on top); the lips and the section holes carry it.
- Figures are rigid parts (no knees bending); the walk is a hip swing with a body bob.
