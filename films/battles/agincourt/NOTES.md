# The Battle of Agincourt (1415): Battle Map film notes (v2)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there; reference film: `films/battles/cannae/`). Film spec: `spec.js`.
16:9, 24 fps, 147.278 s. Narration timing is locked to `cues.json` (line starts never change; the sound is re-scored around them).
England deep red (team `rome`), France royal blue (team `carthage`); the stakes are drawn as the map symbol for a row of stakes (a zigzag ink line).
The ASR spelled "Agincourt" wrongly in cue line l01 (do not use words of l01); "plowed" and "armor" are US spellings in the cues, the
screen text is UK. `node films/lib/battlemap/tools/scenes.mjs films/battles/agincourt` prints the plan below with the checks.

## Maps
- Main stage: the battlefield, dry (hook, title, the field and the numbers). Agincourt wood west, Tramecourt wood east, narrowing to a
  neck (the funnel). England in the south facing north, France in the north facing south. About 1 unit = 5 m.
- Stage `chan`: the Channel map (England, the Seine, the Somme, northern France), for the invasion and the epilogue.
- Stage `wet`: the same battlefield baked again with a dark brown palette; it dissolves in over "It had rained all night" (a change of
  time: overnight) and carries the battle. Blocks, moves, labels and arrows are one shared object for the dry and the wet field.

## Film-side code
- `fx.js`: `spec.rain` (slanted rain streaks between two cue times: it rains on the march in the hook, all night in l06, and over northern
  France on "always check the weather"). The v1 theatre curtains, veil and `wood` team are gone.
- `icons.js` (v1 cartoon icons: rain cloud, thermometer, sick face, mud splat, bush, quill, axe, hammer, clock, sweat) is deleted; nothing
  in the film draws clip art now. The only glyph left is one galley on Henry's crossing (who crosses the sea, and when).

## Cutaway inserts (films/cutaway/agincourt-mud/, Blender, by another builder)
Insert A replaces about 57.3 to 71.2/72.0 s (l06 and l07: rain, mud, the stakes, the advance); insert B about 86.7 to 100.3/100.9 s (l10
and l11: the French on foot in the mud, the woods squeeze them). The map shots under them (S4, S6) are complete fallbacks. The cuts are
planned around them:
- Into A: S3.4 is a high shot from behind the French looking south over the whole dry field (the field the insert's A1 shows from the same
  French side, now soaked). Out of A: S5.1 (cut on the end of "close enough to shoot.", 71.25 s) is top down: the consequence from
  above, the English line now forward behind its row of stakes on the brown field, the first volley rising.
- Into B: S5.5 is high and wide over the French host after the horses fled into it: the ground they must now cross. Out of B: S7.1 (cut
  on the end of "swing a weapon.", 100.3 s) is top down: the consequence from above, the packed French mass in the neck, at the stakes.
If the inserts run to the next line start (72.0 and 100.9 s) instead, the first 0.7 s of S5.1 and 0.6 s of S7.1 are covered and the cuts
still work (a hard cut on a line start).

## How the battle is explained (CRAFT.md section 7)
Stakes first (S1: a small, sick, soaked army against a huge one; spoiler: the mud), then the people and the road (S2: Henry crosses, takes
Harfleur, the army falls sick, he marches for Calais and the French block the road), then the field and the numbers (S3), then the
night of rain and the plan (S4: stakes and the walk to bowshot), then the turn in two parts (S5: arrows, the charge that fails; S6: the
French on foot in the mud and the funnel), the decisive moment wide from above (S7.1) and then closer (S7.2 the archers join in on the
flank, S7.3 the rear pushing the front), the cost (S8) and the legacy (S9). Humour stays in the narration and the timing: the hold on
Harfleur through "Very, very sick. Let's just say the bushes were busy.", the cut to the English standard on "The English lost a few
hundred.", the rain arriving over France on "always check the weather".

## Scene list (9 scenes, 29 shots, average shot 5.1 s)

| scene | time (s) | job | shots and camera plan |
| --- | --- | --- | --- |
| S1 The odds | 0 to 17.9 (main, dry) | a small, sick, soaked army against one of France's biggest; spoiler: the mud | 1.1 cold open low behind the small red block in the rain (caption 1415), slow push; 1.2 change of scale on "one of the biggest armies": high and wide from behind England, France's host rises block by block across the field; 1.3 on "Spoiler": crane up from a quarter angle to top down over the field, under the title card |
| S2 The road to Calais | 17.9 to 40.0 (chan) | why Henry is in France, and why his army is small, sick and trapped | dissolve (change of world) to the Channel map. 2.1 Henry crosses from England (galley on the dashed route), legend opens with ENGLAND / King Henry V; 2.2 closer on Harfleur (A), taken; the red ranks thin on "sick", and the camera holds through "Very, very sick. Let's just say the bushes were busy."; 2.3 follow the dashed march north toward Calais (B); 2.4 closer on the road: the French army rises across it |
| S3 The field | 40.0 to 57.3 (main, dry) | where and how many: a ploughed field between two woods; 8,000 mostly archers against far more, many knights | dissolve back to the field. 3.1 establish from the south: both armies take their places (caption 25 OCTOBER 1415); 3.2 top down: the ploughed field and the two woods (C Agincourt wood, D Tramecourt wood, on "woods"); 3.3 low behind the English: King Henry V, the 8,000 counter, archers on both wings (legend highlights Archers); 3.4 reverse, high behind the French looking south: far more, and the knights on the wings (into insert A) |
| S4 Rain and stakes | 57.3 to 71.2 (wet; insert A) | overnight the field turns to mud; the English stake their line and walk to bowshot | dissolve 1.8 s (change of time) to the wet field in the rain. 4.1 high and wide from the French side, slow push down; 4.2 low along the English line as the stakes go in, a wave from west to east; 4.3 high from the west: the whole English line and its stakes walk forward |
| S5 Arrows and horses | 71.2 to 86.7 (wet) | the arrows fall; the French knights charge, the mud slows them, the stakes stop them, they flee into their own lines | 5.1 out of insert A, top down: the consequence, the line forward behind its stakes, volleys rise; 5.2 low from the French side under the falling arrows; 5.3 high from the east: both wings charge; 5.4 closer and low behind the west wing: they slow and sink in the mud and stop at the stakes (STAKES); 5.5 high and wide: the horses turn and gallop back into their own lines (into insert B) |
| S6 The funnel | 86.7 to 100.3 (wet; insert B) | the French on foot in mud to the knees; the woods squeeze them | 6.1 low from the west beside the French front (France left, England right, as in insert B), tracking with it as it slows and sinks; 6.2 high behind the English stakes, a slow rise: the column narrows between the woods (C and D marked again on "woods") |
| S7 The crush (climax) | 100.3 to 115.0 (wet) | exhausted, they reach the line; the archers join in; the rear pushes the front: chaos | 7.1 the decisive moment wide, top down: the packed mass in the neck reaches the stakes; 7.2 closer and low on the west flank: the archers wheel in on the flank (legend highlights Archers); 7.3 behind the French rear over the press: the back ranks push into the front, the ranks compress |
| S8 The cost | 115.0 to 126.1 (wet) | over in a few hours: thousands of French killed or captured, a few hundred English | 8.1 long pull back as the sun goes down, the French ranks thin and FRANCE dims in the legend; 8.2 cut on "The English lost a few hundred.": low on the English standard, nearly whole |
| S9 After | 126.1 to 147.3 (chan) | a famous play, a marriage, an heir to France, and a lesson | dissolve (change of time) to the map. 9.1 toward England and London (caption HENRY V, BY WILLIAM SHAKESPEARE, ABOUT 1599), a hold through "We few. We happy few."; 9.2 France: Henry at Troyes (TROYES, 1420), legend highlights ENGLAND on "heir"; 9.3 pull back over northern France: cloud rolls in and the rain starts on "always check the weather"; end card at 143.08 |

## Legend
Sides: ENGLAND (red banner, King Henry V, about 8,000 men on "8,000"), FRANCE (blue banner, Constable d'Albret, no number: the
narration says "far more" and the modern estimates range from about 12,000 to 36,000; dims on "Thousands of French"). Units: Archers (on
"archers"), Knights (on "knights"), Foot soldiers (both sides, on "soldiers" in l10). Places: A Harfleur (on "port"), B Calais (on
"Calais"), both on the Channel map; C Agincourt wood and D Tramecourt wood (on "woods"), on the field, marked again on the wet field in
l11. Scale bar on the field views of S3 (about 5 m a unit), compass on the high views.

## Living world
Field: cloud shadows, grass gusts (dry), the English camp in the south and the French camp in the north (tents, fires, people), walkers on
the road, crows over both woods, rain in the hook and in l06, smoke over the camps and over the fighting from l12, army dust at every front.
Channel map: cloud shadows, sea glints, gulls, smoke over Harfleur after it falls, rain over France at the end.

## Known weak spots
- The Channel map is stylised and not to scale; Troyes and London are placed by eye.
- The mud is a darker brown palette and rain streaks, not a true mud texture (insert A and B carry the close-up mud).
- Losses are thinning ranks; no counters for the French (the narration gives no number).
