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

**B (14.16 s).** B1, 86.70 to 93.91: low on the -Y cut face, a slow track left to right with the French front file
(France left, England right, the same screen direction as A2). Through the face we see their armoured legs go into the
soft layer; strides shorten, ankle deep on "advanced", knee deep on "knees", where the soldier in the middle of the
frame stops dead and wobbles and the next one bumps up behind him; 1.2 s hold. Cut (0.15 s before "The woods"): change
of scale, from the legs to the army. B2, 93.91 to 100.87: high behind the English stakes, a slow rise; the blue column
comes at us between the two woods, the files close together in the neck ("squeezed", "packed"), and on "swing a weapon"
the poleaxes clatter into each other.

## Layout and look

- Block 4.2 x 3.2 x 0.9 m. March along +X: France enters from -X, England holds the +X end. The -Y face is the cut face the
  French front file walks on (file 0 is placed exactly on it, legs straddling the plane; a boolean against a solid
  outside the face, below the terrain line, cuts their buried parts flush, so they show as sections in the soil).
- Woods: Agincourt wood along +Y; Tramecourt wood bulging in from -Y in the middle: the neck. Autumn leaves (25 October).
- Field: plough furrows across the march (period 8.5 cm), muddy puddles in the low troughs (glass, brown absorption).
  Strata: soft wet mud 6.5 cm (darker, glossy coat), wet loam, clay, chalky marl, deep (Picardy loess over chalk).
- Figures about 0.17 m: French in carthage blue surcoats with a gold hem and gold disc, steel arms and legs (mud caked
  below the knee), bascinets with the pointed visor, poleaxes; two French banners (blue, gold border, gold disc,
  swallowtail, as the film's). English archers in rome red jacks, kettle hats, quivers, longbows, mallets; red
  men-at-arms with two red banners. Colours from `films/lib/battlemap/blocks.js` TEAMS.
- Light: A overcast and dark (rain); B grey after-rain light with drifting cloud shadows and a few crows over the wood.
- Living layers: rain and puddle rings (A), wind in grass and trees, banners waving, figures moving, cloud shadows (B).

## Measured

Local build (no render) on the shared 2-core box: about 5 to 8 s; frame pose and evaluation about 1 to 3 s (the face
legs use the Manifold boolean solver; EXACT was about 40 s per frame for B).

## Known weak spots

- The mud does not deform around the boots (no dents or ruts); the collars of mud at the shins carry it.
- Figures are rigid parts (no knees bending); the walk is a hip swing with a body bob.
