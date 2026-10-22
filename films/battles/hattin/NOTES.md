# The Battle of Hattin (1187): Battle Map film notes (v2)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there; reference film: `films/battles/cannae`). Film spec: `spec.js`.
16:9, 24 fps, 141.55 s. Narration timing is locked to `cues.json` (line starts never change; the sound is re-scored around them).
Teams are colours only, no religious badges: crusaders red (`rome`), Saladin's army blue (`carthage`). Look: engraved relief map of the
Galilee hills in July heat (a warm haze veil), evening, a blue night lit by the brush fire, a clear morning, dusk at the Horns.
`node films/lib/battlemap/tools/scenes.mjs films/battles/hattin` prints the plan below with the checks (0 errors, 0 warnings).
Cue spellings: the ASR writes "Tiberius" (l03), "Hatton" (l01), "Hatim" (l09), "Hateen" (l15); `l04.go.#1` is the second "don't go".

Film-side code (no engine change):
- `kinds.js`: three kinds the engine lacks. `flame` (a burning tuft of dry grass: flame tongues on a charred patch) and `pavilion` (King
  Guy's red tent) added to the engine's `FIG_KINDS` table; the unit symbol `u-horse-archers` (registerIcon) for the legend key.
- `fx.js`: the brush fire (`ambient.fires`: flames light one after another along the line, flicker, send up dark smoke; their glow is
  added over the night veil), the red tent that collapses (`ambient.pavilions`), the July heat (`heat`: a warm veil only, no moving
  graphics), the smoke drifting into the crusader camp (`smoke`), the night (`dim`, no stars), and the territories on the Levant map
  (`regions`: Egypt and Syria blue, the crusader states red; the south turns blue when Jerusalem falls).
- The v1 `icons.js` (sun with sunglasses, sad flask, hook and worm, thermometer, coughing faces, iced cup, hourglass) is gone, and so are
  the moving heat bands and the stars.
- Thirst is told by the map, not by a prop: the water is always on screen as lettered places (B Sea of Galilee, C the springs), the horse
  archers bar the way to it, an ink sightline runs from the camp to the lake on "they could see the water", the ranks thin in the smoke.

## How the battle is explained (CRAFT.md section 7)
Stakes and people first (S1 the lure, S2 Saladin and the crusader states), then the bait and the decision (S3: Tiberias, the lords' advice,
King Guy marches anyway), then the march and the thirst (S4, S5), then the turn (S6: the break-out fails, the army breaks), shown wide (S6.2,
top-down: the pieces and the ring) and then closer and lower (S6.3: circling the saddle as the tent is surrounded and falls), then the result
(S6.4 the king taken, S7 the cup of water), then why it mattered (S8: Jerusalem). The humour stays in the narration and the timing: the hold
on the lords' camp for "don't go", the cut back to King Guy on "marched anyway", the empty hills under "especially in a metal suit".

## Scene list (9 scenes, 28 shots, average shot 5.1 s)

| scene | time (s) | job | shots and camera plan |
| --- | --- | --- | --- |
| S1 Lured | 0 to 16.0 | a Sultan lures an army into the hills and waits for thirst | midday heat. 1.1 low over the dry hills, the crusader column marching east (caption GALILEE, 1187), far ahead the Sultan's standard rises (SALADIN tag), slow push; 1.2 reverse angle from behind his standard toward the column, "and then he waited"; 1.3 crane up into the map under the title |
| S2 Saladin | 16.0 to 27.4 | who the Sultan is, who holds Jerusalem | dissolve to the Levant. 2.1 Saladin at Damascus; Egypt and Syria appear as blue hatched territories (CAIRO, DAMASCUS); legend opens; 2.2 lower along the coast: the crusader states in red, the dashed route from Europe, JERUSALEM, then ANTIOCH, TRIPOLI, TYRE, ACRE pinned one after another on "a string of castles" |
| S3 The bait | 27.4 to 51.0 | the bait, the advice, the decision | dissolve to Galilee. 3.1 Saladin's horsemen ride round the lake (blue arrow) and Tiberias burns, places A Tiberias and B Sea of Galilee; 3.2 wide over the whole map: the red dashed rescue route from SAFFURIYA; 3.3 low in the camp: RAYMOND OF TRIPOLI, "don't go"; 3.4 high along the road east, caption 3 JULY 1187: no water on the way; 3.5 Tiberias: COUNTESS ESCHIVA trapped; 3.6 cut back to camp on "King Guy": KING GUY, the march begins |
| S4 Across the dry hills | 51.0 to 64.9 | the march into the heat, cut off from water | heat veil. 4.1 low beside the road as the column passes, 20,000 counts up in the legend, key rows Infantry and Knights; 4.2 high over the column: horse archers ride round it, volleys of arrows, key row Horse archers highlighted; 4.3 low from the east behind the archers' line: the way to water blocked |
| S5 The dry plateau | 64.9 to 85.3 | in sight of the lake; then fire and smoke | evening to night. 5.1 high over the plateau: Saladin's army forms between the crusaders and the lake, vultures circle; 5.2 low over the crusaders' shoulders toward the glinting lake, ink sightline, legend highlights Sea of Galilee; 5.3 night: low along the grass as the fire runs down the line; 5.4 high and wide: the smoke drifts into the camp, the ranks thin |
| S6 The Horns of Hattin (climax) | 85.3 to 106.7 | the break-out fails; the king is taken | morning. 6.1 wide and high: the break-out arrow toward C the springs and D the Horns of Hattin; 6.2 the decisive moment top-down: the army breaks into pieces, some charge into the archers' line and are lost, some flee up the hills, the blue ring forms round the outside; 6.3 closer and lower, circling the saddle: KING GUY'S TENT surrounded, gold dashed ring, the tent falls, the ring tightens, caption 4 JULY 1187; 6.4 low on the king as he is taken |
| S7 A cup of water | 106.7 to 114.4 | a life spared | dusk. 7.1 low: the ring parts and Saladin's standard walks up to the king (SALADIN); 7.2 pull back over the Horns |
| S8 Jerusalem | 114.4 to 131.0 | why it mattered | dissolve to the Levant. 8.1 Saladin's arrow to Jerusalem, HATTIN marked; the south of the crusader states turns blue; 8.2 closer on JERUSALEM, caption 2 OCTOBER 1187 ("without a massacre"); 8.3 wide over the sea: the galley of the new crusade (caption 1191, RICHARD THE LIONHEART) reaches ACRE and stops short of Jerusalem; legend highlights Saladin |
| S9 The lesson | 131.0 to 141.6 | the lesson, where it happened | dissolve back over the empty, hazy hills and the Horns; end card at 137.35 |

Living world in every wide shot: drifting cloud shadows, wind gusts over the dry grass, glints on the Sea of Galilee, two camps (Saffuriya,
Saladin's camp across the lake: tents, fires, smoke, people), travellers on the road until the war reaches it, birds (vultures over the
plateau at evening and over the Horns after the battle), Tiberias burning, banners in the wind, army dust.

## Measured
Local 640x360 smoke test on the shared 2 core box: 0.8 to 1.7 s per still after a 15 s start. Full-quality stills on free GitHub runners.

## Known weak spots
- The Levant is stylised (territories are simplified shapes); the Galilee map is not to scale (Saffuriya to Tiberias is stretched).
- The ring of Saladin's army forms by riding round the outside of the horns at map speed; it is fast on the map by design.
- The fire's smoke columns are engine puffs and the drifting smoke is a 2D overlay; they are tuned to read at night, not to be physical.
