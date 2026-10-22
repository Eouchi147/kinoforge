# The Battle of Cannae (216 BC): Battle Map film notes (v2, the reference film)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there). Film spec: `spec.js`. 16:9, 24 fps, 157.629 s. Narration timing is
locked to `cues.json` (line starts never change; the score is being redone around them). Look: engraved relief map, armies as painted
miniatures on trays, Rome deep red, Carthage royal blue, morning haze to golden day to a low red sun in the evening.
`node films/lib/battlemap/tools/scenes.mjs films/battles/cannae` prints the plan below with the checks (0 errors, 0 warnings).

## How the battle is explained (CRAFT.md section 7)
Stakes and people first (S1, S2, S3), then the field and the numbers (S4), then each side's plan drawn on the map (S4.3, S5), then the
turn (S6), shown wide (S6.6, top-down) and then closer and slower (S7.1 orbit, S7.2 inside the press), then the result in plain numbers
(S7.3: about 50,000 Romans lost, Livy's figure is 48,200; the narration says "tens of thousands"), then why it mattered (S8, S9).
Humour stays in the narration and the timing: the command star hops between the two consuls on "One. Day. Each.", the cut lands on "Nope.".

## Scene list (9 scenes, 26 shots, average shot 6.1 s)

| scene | time (s) | job | shots and camera plan |
| --- | --- | --- | --- |
| S1 The host | 0 to 22.5 | Rome sends a gigantic army; one man is about to beat it | 1.1 low sweep (11 deg, 30 mm) as the 12 legions rise rank by rank and march into line, ROME tag, caption 2,200 YEARS AGO; 1.2 reverse angle from behind Hannibal's standard toward the distant host (ONE MAN), slow push; 1.3 crane up from 52 to 84 deg into the plan view under the title card |
| S2 Hannibal | 22.5 to 33.9 | who Hannibal is, how audacious | dissolve to the Mediterranean map. 2.1 Carthage in Africa (marker), slow pull out, legend opens with CARTHAGE / Hannibal; 2.2 follow the dashed route from Spain over the Alps (elephant glyph walks the pen tip), hold on ITALY for "just to make a point" |
| S3 Rome | 33.9 to 42.7 | meet Rome and its odd two-headed command | dissolve back to the plain. 3.1 the army in front of its camp, slow orbit, legend adds ROME; 3.2 closer on the consuls' standards, VARRO and PAULLUS, the gold command star hops on each word, slow push into "what could possibly go wrong?" |
| S4 The field | 42.7 to 61.7 | where and how many, and Rome's simple plan | 4.1 the whole field from the river side, Carthage marches in, caption 2 AUGUST 216 BC, key opens (plain, River Aufidus, Cannae); 4.2 top-down plan, 80,000 and 50,000 counters on the map and in the legend; 4.3 low behind the Roman ranks, the heavy red arrow on "push" |
| S5 The trap is set | 61.7 to 75.4 | Hannibal's plan | 5.1 top-down: the centre bends into a bow toward Rome (bowstring hairline), WEAKEST TROOPS, legend highlights Infantry; 5.2 low along Carthage's line toward the river: VETERANS at the ends, HORSEMEN on the sides |
| S6 The jaws | 75.4 to 106.5 | the Romans walk in, the horsemen ride round, the trap closes | 6.1 behind the Romans as they charge (follow); 6.2 high angle: THE MIDDLE GIVES WAY step by step, AS PLANNED; 6.3 low from the river side, the push deeper (screen direction left to right kept); 6.4 meanwhile by the river: ROMAN CAVALRY chased off; 6.5 high and wide: the dashed swing behind the Romans; 6.6 the decisive moment top-down: left and right arrows on the words, the back door, legend highlights veterans then cavalry |
| S7 Surrounded (climax) | 106.5 to 127.8 | how it worked, up close; the cost | 7.1 closer and slower orbit around the ring (gold dashed ring, SURROUNDED), dust along every front; 7.2 low and close (45 mm) inside the press, ranks compressed; 7.3 long pull back as the sun turns red, ranks thin out, Paullus's standard sinks (CONSUL PAULLUS), caption ABOUT 50,000 ROMANS LOST, Rome dims in the legend |
| S8 Rome refuses | 127.8 to 146.3 | the twist: a battle is not a war | dissolve to the Mediterranean. 8.1 Italy, HANNIBAL in the south, hold on "right?"; 8.2 cut on "Nope.": Rome raises NEW ARMIES; 8.3 caption 202 BC, Scipio's galley sails to Africa; 8.4 Zama: Scipio's horsemen swing round behind Hannibal's line (the trick, copied), it thins |
| S9 The lesson | 146.3 to 157.6 | the result in one image | dissolve back over Cannae from above: the legend highlights Carthage ("won the battle") then Rome ("won the war"); the two great pincer arrows of the double envelopment draw on "generals have been copying his giant hug"; end card at 153.43 |

Living world in every wide shot: drifting cloud shadows, wind gusts sweeping the grass, river glints moving downstream, two camps
(tents, palisade, fires with smoke, people walking), travellers on the roads, three flocks of birds, banners in the wind, army dust.

## Measured
See the bottom of this file (filled after each measurement run).

## Known weak spots
- The sandbox is shared (load 6 to 10 on 2 cores), so wall time per frame is noisy; the engine's own work is profiled separately.
- The Mediterranean map is stylised and not to scale; its armies are small groups of large figures (`figScale` 1.4).
- Figures are simple boxes at map scale (no faces, by design); in the 45 mm close shot (S7.2) they read as miniatures, which is the look.
- Labels are placed by hand (`dx`, `dy`); no automatic collision avoidance with the legend panels yet.
