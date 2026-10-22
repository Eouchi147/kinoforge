# The Battle of Thermopylae (480 BC): Battle Map film notes (v2)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there; reference film `films/battles/cannae/`). Film spec: `spec.js`.
16:9, 24 fps, 164.113 s. Narration timing is locked to `cues.json` (line starts never change; the score is re-done around them).
Persians red (team `rome`), Greeks blue (team `carthage`). The ASR spelled some words oddly in the cues: "Dianik," (Dienekes),
"Effialty's" (Ephialtes), "Thespier" (Thespiae), "past" for "pass" (l10, l17); the spec refers to neighbouring words.
`node films/lib/battlemap/tools/scenes.mjs films/battles/thermopylae` prints the plan below with the checks.

Film-side additions (`units.js`, registered from `index.html`; no engine file changed): four flat glyphs in the v2 style (one ink
weight, flat fills, no faces): `pass` (a cliff, a narrow road and the sea: the place glyph of Thermopylae), `trail` (a mountain with a
dashed path over it: the hidden path), `stele` (the stone with the epitaph) and `lambda` (a Spartan shield, the Greek side's banner in the
legend). The terrain needs no new feature: the pass is the engine's `mountains` wall against a `sea`, the coast road a `road`, and the
hidden mountain path a thin `road` drawn over the mountains. The old `icons.js` (throne, calendar, sunglasses helmet, moon, money bag,
hourglass, shout marks) and `fx.js` (an overlay patch for a screen veil with stars, a hatched empire and a bouncing number plate) are
removed; the night is a blue scrim card over a low sun, the empire is shown by its armies rising from Egypt to India, and the numbers are
engine counters.

## How the battle is explained (CRAFT.md section 7)
Stakes first (S1: the biggest army ever seen against a few thousand Greeks at a gap; S2: who Xerxes is, how big his empire and his army),
then the Greeks (S3: rival cities that team up), the place and why it was chosen (S4: a road between a cliff and the sea where a giant army
can only come a little at a time; the defenders and their numbers), the waiting and the arrows (S5), the fighting (S6: waves that break on
a shield wall that takes turns at the front; even the Immortals fail), the turn (S7: the hidden path, the night climb, the Greeks sent away,
the last stand shown twice: wide from above as the ring closes, then low and close as the ranks thin), the result and why it mattered
(S8: Athens burns, then Salamis and Plataea), and the stone (S9). Humour stays in the narration and the timing: the cut to the Greek front
rank on "They did not.", the hold on the close shot through "fight in the shade", the king's standard that jumps three times on the words,
the low shot over the massed armies on "Still, a lot."

## Scene list (9 scenes, 32 shots)

| scene | cue | job | camera plan |
| --- | --- | --- | --- |
| S1 The invasion (Aegean map) | 0 to l02 | the biggest army ever seen marches into Greece; a few thousand Greeks wait at a gap in the mountains | 1.1 the Persian columns cross from Asia into Greece (caption 480 BC), slow follow west; 1.2 push in to the tiny Greek block at the gap, held under the title card |
| S2 King of Kings (empire map) | l02 to l03 | who is coming: Xerxes, an empire from Egypt to India, an army of a million, or a hundred thousand | dissolve. 2.1 the capital, XERXES; 2.2 the whole empire: armies rise from Egypt to India in order as the line names them; 2.3 the numbers: 1,000,000 by the ancient writers counts down to 100,000 by the modern ones; 2.4 cut on "Still, a lot.": low over the massed armies |
| S3 The allies (Aegean map) | l03 to l04 | the Greek cities usually fight each other; this time some team up | dissolve. 3.1 the cities, thin ink arrows between rivals; 3.2 lower and turned: blue routes converge on Thermopylae |
| S4 The pass | l04 to l06 | why here: a road between a cliff and the sea where a giant army can only come a little at a time; who holds it | dissolve. 4.1 high down the pass from the south (legend: A Thermopylae); 4.2 low in the road at the narrowest point, cliff on one side (B), sea on the other (C); 4.3 top-down: the army squeezes into the road; 4.4 low behind the Greek wall: about 7,000 Greeks, LEONIDAS, 300 SPARTANS |
| S5 The wait | l06 to l08 | Xerxes waits four days for them to run; they do not; the arrows story | 5.1 high from the south over the tiny Greek wall to the host filling the plain (XERXES); 5.2 cut on the punchline: low and close on the front rank; 5.3 the archers draw up and the sky fills with arrows (legend highlights Archers, the cloud darkens); 5.4 close on the Spartan front in the shade: DIENEKES |
| S6 Wave after wave | l08 to l11 | the Persians attack for two days and cannot break the wall, not even the Immortals | 6.1 reverse angle behind the Persian waves pouring into the pass; 6.2 high and close over the shield wall: the front rank steps back through its lane and the next takes its place; 6.3 low behind the Immortals as they charge and fail; 6.4 reaction: the king's standard on the slope, jumping three times; 6.5 top-down: two days on, the wall stands where it stood |
| S7 Surrounded (climax) | l11 to l15.They | a traitor shows the Persians a way round; most Greeks leave, the Spartans and the Thespians stay and die | 7.1 EPHIALTES walks into the Persian camp; 7.2 top-down over the mountains: the hidden path (D) drawn round behind the Greeks; 7.3 night (blue scrim, low sun): follow the Immortals along the path; 7.4 dawn, high and wide: they come down behind the pass, most Greeks march away; 7.5 low and close on those who stay (700 THESPIANS); 7.6 the decisive moment wide from above: the ring closes from both ends; 7.7 the same moment closer and lower: the ranks thin to the end, pull back on "So, the Persians won." |
| S8 The war (Aegean map) | l15.They to l17 | why it mattered: they burn Athens, then lose at sea and on land | dissolve. 8.1 the march south, smoke over Athens; 8.2 Salamis: the Greek galleys row in and the Persian galleys capsize; 8.3 Plataea, 479 BC: beaten on land for good (legend highlights the Greeks) |
| S9 The stone | l17 to end | the epitaph at the empty pass | dissolve back to the pass in the evening, quiet: slow push on the stone (marker), then the epitaph card on the words and the end card |

Legend: title THE BATTLE OF THERMOPYLAE, August 480 BC; sides PERSIA (Xerxes, 100,000, the modern estimate the line gives) and GREEK
ALLIES (Leonidas of Sparta, 7,000), each on the word that names it; units Hoplites (Greek), Infantry and Archers (Persian); places A
Thermopylae, B the mountains, C the sea, D the hidden path, each entering on its word.

Living world: cloud shadows, wind and gusts, the sea glinting along the coast, the Persian camp (tents, fires, smoke, people) and the Greek
camp, walkers on the coast road, gulls over the sea and a hawk over the cliffs, dust along every front.

## Removed from v1
Cartoon icons (throne hops with a counter bubble, calendar pages, a helmet in sunglasses, moon, money bag, question marks, stop signs, bursts,
laurels, an hourglass, shout marks, a door), the bouncing number plate, the hatched empire overlay, the screen veil, the bouncing blocks, and
the labels that only repeated the narration (THE BIGGEST ARMY EVER SEEN, STOP THEM!, FIGHTING EACH OTHER, A NARROW ROAD, SQUEEZE THROUGH,
WAITING, THEY DID NOT, SO MANY ARROWS, GOOD., WAVE AFTER WAVE, THEY CANNOT BREAK THROUGH, TWO DAYS, THE PASS HELD, HE SELLS A SECRET, THAT
NIGHT, ABOUT TO BE SURROUNDED, THEY FOUGHT TO THE VERY END, THE END? and the rest). Kept: names, dates, numbers.

## Checks (22 Oct)
`tools/scenes.mjs`: 9 scenes, 32 shots, average shot 5.1 s, 0 errors, 0 warnings. `films/director/check.cjs`: no hard problems (one
soft note: the galley glyphs at Salamis, kept because they carry the sea battle). Contact sheet: one still per shot with the narration.

## Known weak spots
- The Aegean and the empire are rough hand maps, not to scale; their armies are a few large figures on trays.
- The night is a blue scrim over a low sun, not a true night light (the engine's light goes from day to a low red sun only).
- Compressed waves: each Persian wave marches up, presses, thins and melts away in about 6 s, as in every Battle Map film.
- The legend panels cover the left quarter of the frame; shots keep the action centre right.
