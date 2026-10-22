# The Battle of Hastings (1066): Battle Map film notes (v2)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there; reference film: `films/battles/cannae/`). Film spec: `spec.js`.
16:9, 24 fps, 155.401 s. Narration timing is locked to `cues.json` (line starts never change; the sound is re-scored around them).
Colours: the English royal blue (team `carthage`), the Normans deep red (team `rome`), the Norwegians gold. Two maps: the main stage
is England, the Channel and Normandy (the build-up and the coronation); the `bat` stage is the field below the English ridge (Senlac
hill: the ridge, the gentle south slope, marshy ponds and woods at the sides, the London road north), shown full screen in S1 and S4 to S7.
`node films/lib/battlemap/tools/scenes.mjs films/battles/hastings` prints the plan below with the checks.

## How the battle is explained (CRAFT.md section 7)
Stakes first (S1: an army waiting on a hill at dawn, three kings in one year), then the people and the claims (S2: Harold crowned in
London, William across the sea), then the two invasions and the long march that tires the English (S3), then the field and each side's
job (S4), the attack that fails (S5), the turn (S6, the feigned flight: shown wide from above, then closer and lower as the knights close
the ring, then wide again for "more than once"), the result (S7: Harold falls, the army breaks) and why it mattered (S8: a French-speaking
king; the Old French words BUEF, JUREE, JUGE ride across the Channel on "beef, jury and judge"). Humour stays in the narration and the
timing: the hold on Normandy through "excuse me, that crown was promised to me", the hold on "Busy month.", the hold on "Not fun.", the
long slow orbit over Harold's fallen standard through "It is very hard to ask a tapestry questions" with the cut on "Without".
No cartoon icons: the v1 crowns, crosses, bursts, question marks, books, helmet, tapestry and laurel are gone. Glyphs kept only where
they carry information: the galleys (who crosses the sea, and when).

## Scene list (8 scenes, 30 shots, average shot 5.2 s)

| scene | time (s) | job | shots and camera plan |
| --- | --- | --- | --- |
| S1 The hill at dawn | 0 to 17.4 (bat) | 1066: three kings in one year; the last one is decided here | 1.1 cold open low over the slope at dawn mist toward the English wall on the crest, slow push (caption 1066); 1.2 on "This is the battle": crane up from the slope to the field seen from above, under the title card |
| S2 The crown | 17.4 to 34.3 (main) | who claims the crown: Harold in England, William across the sea | dissolve (change of world) to the map. 2.1 London from above, EDWARD THE CONFESSOR on "old king", Harold's army rises on "crowned", legend opens with ENGLAND / King Harold; 2.2 cut across the sea to Normandy, William's army rises, then a hold through "excuse me, that crown was promised to me" (the joke lives in the hold); 2.3 low over the Normandy shore looking north across the Channel: the galleys gather on "fleet" (what the fleet is for: England on the horizon) |
| S3 Two invasions | 34.3 to 53.9 (main) | Harold beats the Norwegians in the north, then William lands in the south; the long march back | 3.1 the north: the Norwegian galleys sail in, gold army lands, legend adds NORWAY / Harald Hardrada; 3.2 high and wide, following Harold's march up the road; the Norwegians thin and dim at "beat"; key adds B Stamford Bridge; 3.3 three days later, the south coast: William's galleys cross, he lands at PEVENSEY; 3.4 the whole length of England from above: the dashed blue march back down, the 250 MILES counter rides on Harold's army, hold on "Busy month." |
| S4 The hill | 53.9 to 73.0 (bat) | the field: the English on top in a shield wall, the Normans below with a hard job | dissolve back to the field. 4.1 establishing high oblique from the south-east: ridge, marsh, the wall on the crest (caption 14 OCTOBER 1066, key adds C Senlac Hill); 4.2 low along the wall from its west end as the shields lock (the files close on "locked", THE SHIELD WALL); 4.3 reverse, from behind the English and above: William's army forms at the bottom (archers, foot, knights, each on its word, in the legend too); 4.4 low behind the Normans looking up the slope: the red arrow draws up the hill, hold on "Not fun." |
| S5 The wall holds | 73.0 to 98.1 (bat) | the attack fails against the wall; a rumour, a panic, a rally | 5.1 high from the west flank: archers walk up, two volleys arc into the shields, the foot climb into the wall; 5.2 low behind the knights as they ride uphill into the axes; 5.3 high, near top down: the Normans fall back, the blue line has not moved, "hour after hour" (the sun moves through the set); 5.4 oblique on the Norman lines: the rumour, then they turn and run (pull back with them); 5.5 low and close on William's standard as he turns to face the runners; 5.6 wide: the army turns and climbs again |
| S6 The trick | 98.1 to 117.2 (bat) | the feigned flight pulls the English off the hill; again; the wall thins | 6.1 from behind the English wall, high: the Normans "run away" (FEIGNED FLIGHT); 6.2 the decisive moment wide, from above: two blocks chase down the slope and leave a gap in the wall; 6.3 closer and lower on the same place: the knights wheel in from both sides and the foot turn, the chasers are cut off (gold ring), they thin; 6.4 high from the east: it happens again on the other side; 6.5 low along the crest: what is left of the wall closes up, thinner |
| S7 The king falls (climax) | 117.2 to 134.7 (bat) | Harold falls and the English army breaks | 7.1 low from behind the last Norman push toward Harold's standard in the red evening; a volley; his standard sinks on "killed"; 7.2 slow orbit over the fallen standard (caption BAYEUX TAPESTRY, 1070s), the hold carries "Historians still argue... ask a tapestry questions"; 7.3 cut on "Without": high from the west, the English scatter north and the Normans take the crest, ENGLAND dims in the legend |
| S8 The Conqueror | 134.7 to 155.4 (main) | William is king; a French-speaking king changed English | dissolve back to the map. 8.1 William marches to London, WESTMINSTER ABBEY on "crowned", legend highlights NORMANDY on "Conqueror"; 8.2 wide over the Channel: three ink routes from Normandy carry BUEF, JUREE, JUGE into England on "beef, jury, judge"; 8.3 pull back and up to the whole map, marker C (Senlac hill) on "All thanks to one very long afternoon on a hill", end card at 151.2 |

The decisive moment (the feigned flight and the cut-off chasers) is shown wide from above (S6.2), then closer and lower (S6.3), then
wide again for the repeat (S6.4).

## Legend
Sides: ENGLAND (blue banner, King Harold, about 7,000 men estimated, dims on "broke"), NORMANDY (red banner, Duke William, about 7,000
estimated), NORWAY (gold banner, Harald Hardrada, dims on "beat"). Strengths are the common modern estimates (the sources vary from about
5,000 to 13,000 a side), labelled MEN, ESTIMATED. Units: Foot soldiers (both sides), Archers, Knights, each on its word in l07. Places:
A The Channel ("sea"), B Stamford Bridge ("Stamford"), C Senlac Hill ("hill", on the battlefield map). The scale bar shows only in S3
(the map is stylised: 1 unit is about 2 km there); compass on the high map views.

## Living world
Main map: cloud shadows, sea glints, gulls over the Channel and the North Sea, travellers on the London to York road, smoke over London,
William's camp on the Normandy shore. Battlefield: cloud shadows, grass gusts, glints on the marsh ponds, the Norman camp in the south and
the English baggage camp in the north (tents, fires, people), travellers on the London road, birds over the woods, smoke and dust from
the fighting from l08, the army dust along every front.

## Known weak spots
- The England map is stylised and not to scale; the Channel is narrow.
- The battlefield shows a single English line of 8 blocks; the real wall was longer and deeper.
- The arrow in Harold's eye is not drawn (the narration says historians argue; the picture does not take sides).
