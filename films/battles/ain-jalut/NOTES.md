# The Battle of Ain Jalut (1260): Battle Map film notes (v2)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there; reference film: `films/battles/cannae`). Film spec: `spec.js`.
16:9, 24 fps, 139.628 s. Narration timing is locked to `cues.json` (line starts never change; the sound is re-scored around them).
Mamluks deep red (`rome`), Mongols royal blue (`carthage`). Two maps: `emp` (a stylised map of Asia, the Middle East and Eastern Europe;
1 degree of longitude = 6 units, of latitude = 8; not to scale in the Levant) for the opening and the epilogue, and the valley of Ain Jalut
(main stage: a valley floor running west to east between two wooded lines of hills, Goliath's Spring in the west).
`node films/lib/battlemap/tools/scenes.mjs films/battles/ain-jalut` prints the plan below with the checks (0 errors, 0 warnings).
Cue spellings: the ASR writes "Angelut" (l01), "Ainjalut," (l06), "Babers" (l08), "mondles" (l11), "Khutuz" (l12), "Kitbuka" (l13),
"Katoos" (l15); screen text is spelled correctly.

Film-side code (no engine change):
- `kinds.js`: the unit symbol `u-horse-archers` (registerIcon) for the legend key.
- `fx.js`: only the territory ink (the Mongol Empire spreading from Mongolia in the first seconds; the Mamluk realm spreading from Cairo
  at the end), with a thinner edge than v1. The v1 timeline bar is gone (the 250 years are now a caption, 1260 TO 1517).
- The v1 `icons.js` (censored scroll, hat, mirror, copy, smirk, puff, horn, bush) is gone, and so are the bouncing crowns, bursts and
  question marks. The letters stay as the engine's flat scroll glyph riding the dashed message routes (a message really travelled).
- The feigned retreat is told by the choreography and the ink: a red arrow out, a short fight, Baybars turns, a dashed red arrow "up the
  valley", the blue arrows of the chase drawn behind him; the hidden army only appears on "the main Mamluk army was waiting" (lettered
  place C, the Hills of Galilee, is highlighted on "Hidden in the hills").

## How the battle is explained (CRAFT.md section 7)
Stakes and people first (S1 the Mongols, S2 the empire, S3 the threat and the rude answer), then the turn of luck and the two armies on
the march (S4), then the field (S5: a spring, a valley, hills on both sides), then the plan in action (S6: the feigned retreat), the turn
shown wide (S7.2, top-down: hit from both sides at once) and then closer and lower (S7.3: the line bends; S7.4: Qutuz rallies it), the
result (S7.5 Kitbuqa falls, S8 the Mongols never come back), and why it mattered (S9: 250 years of Mamluk Egypt). Humour stays in the
narration and the timing: the hold on the Egyptian side for "It was not polite. Let's leave it at that.", the low shot on the Mongol
horsemen for "their own favourite trick", the cut-free hold on Baybars for "Teamwork."

## Scene list (9 scenes, 23 shots, average shot 6.1 s)

| scene | time (s) | job | shots and camera plan |
| --- | --- | --- | --- |
| S1 Almost never lost | 0 to 18.6 | the Mongols conquered more than anyone; they meet an army that knows a trick | 1.1 low over Mongolia (MONGOLIA marker) as the empire spreads like ink across Asia, slow rise; 1.2 follow the horsemen's arrow west into PALESTINE, a red army waits; one move continues under the title card |
| S2 The empire | 18.6 to 28.4 | how big, how close | 2.1 top-down, the whole map: the arrow from CHINA to EASTERN EUROPE; legend opens with MONGOL EMPIRE; 2.2 lower over Mesopotamia: BAGHDAD, 1258 then DAMASCUS pinned |
| S3 Surrender or else | 28.4 to 42.1 | the threat and the answer | 3.1 above Damascus: HULAGU, his message (a scroll on a dashed blue route) rides to CAIRO; 3.2 reverse, low from the Egyptian side: MAMLUKS OF EGYPT join the legend, the answer rides back (red), hold on "Let's leave it at that" |
| S4 Luck changes | 42.1 to 60.1 | the Khan dies, most Mongols go home, Egypt marches | 4.1 wide to KARAKORUM: caption AUGUST 1259, Hulagu rides most of the army back east on a long blue arrow; 4.2 back to Syria, closer: KITBUQA and the smaller army; 4.3 Egypt: SULTAN QUTUZ and BAYBARS march out on the red route |
| S5 The valley | 60.1 to 74.7 | where they meet | dissolve to the valley. 5.1 low along the valley from the east, Baybars's small force in the foreground, the Mongols (KITBUQA) by the spring; caption 3 SEPTEMBER 1260; places A Ain Jalut, B the valley; 5.2 high over the valley: C the Hills of Galilee on both sides; 5.3 low on the Mongol horsemen, legend highlights Horse archers |
| S6 The feigned retreat | 74.7 to 87.4 | the trick | 6.1 behind BAYBARS as he rides out (red arrow) and closes with the Mongols; 6.2 high angle: he turns and runs up the valley (red dashed arrow); 6.3 low behind the Mongol horsemen as they charge after him (blue arrows) |
| S7 Ambush (climax) | 87.4 to 113.7 | the hidden army strikes; the line bends, holds, and the Mongols break | 7.1 tilt up to the wooded hills: the main Mamluk army rises rank by rank; 7.2 the decisive moment top-down: four red arrows, hit from both sides; 7.3 closer and lower: the Mongols push back, the Mamluk line bows; 7.4 low on QUTUZ riding into the line (45 mm), the line straightens; 7.5 high and wide: the second charge, KITBUQA's block thins, the Mongol army drains west, MONGOL EMPIRE dims in the legend |
| S8 Never conquered | 113.7 to 130.9 | the result | dissolve to the map: AIN JALUT marked, the long dashed blue arrow back from Mongolia stops short, the Mongol arrow toward Egypt stops at a gold dashed line; closer on the road home: Qutuz's standard fades, SULTAN BAYBARS |
| S9 Two and a half centuries | 130.9 to 139.6 | why it mattered | high over Egypt as the red Mamluk realm spreads from Cairo to Syria; caption 1260 TO 1517; legend highlights the Mamluks; end card at 135.43 |

Living world in every wide shot of the valley: drifting cloud shadows, wind gusts over the grass and the woods, glints running down the
stream from the spring, two camps (the Mongol camp by the spring, the Mamluk camp up the valley: tents, fires and smoke, people), travellers
on the road until the fighting starts, three flocks of birds, banners, army dust, and battle smoke from the ambush on.
On the map: cloud shadows, sea glints, birds over the Levant and the steppe, the spreading ink.

## Measured
Local 640x360 smoke test on the shared 2 core box: 0.9 to 4.2 s per still after a 20 s start. Full-quality stills on free GitHub runners.

## Known weak spots
- The Mediterranean on the `emp` map is drawn as an inland sea and reads like a lake at close zoom (unchanged from v1).
- Kitbuqa's death is told by his block thinning out and the legend dimming (no wounds, by design).
- The map blocks are symbols (`figScale` 1.4), not armies to scale.
