# The Battle of Gaugamela (331 BC): Battle Map film notes (v2)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there; reference film: `films/battles/cannae`). Film spec: `spec.js`.
16:9, 24 fps, 151.252 s. Narration timing is locked to `cues.json` (line starts never change; the sound is re-scored around them).
Look: engraved relief map of a dry plain, armies as painted miniatures on trays, Macedon deep red (`rome` team), Persia royal blue
(`carthage` team), dawn haze to a bright day to a low red sun as Darius runs. `node films/lib/battlemap/tools/scenes.mjs films/battles/gaugamela`
prints the plan below with the checks (0 errors, 0 warnings).

Film-side code (no engine change):
- `kinds.js`: the scythed chariot, the one army kind the engine lacks. A miniature figure (two horses, a car with a team breastwork, two
  spoked wheels each with a blade out of the hub, a driver) added to the engine's `FIG_KINDS` table, used with `figures: 'chariot'`; and the
  flat unit symbol `u-chariot` (registerIcon) for the legend key. The v1 `icons.js` (cartoon chariots, spinning wheels, bulb, sweat, roller,
  struck-through tags, calendar, puffs) is gone.
- `fx.js`: only the empire as a territory on the `asia` map (fine hatching, inked edge), growing on "master of the Persian Empire" and again
  on "stretched from Greece to India". The v1 sheen and pulsing glow are gone: the levelled ground is now a dashed ink ring and a lettered
  place, the gap a gold dashed ring with one tag.

## How the battle is explained (CRAFT.md section 7)
Stakes and people first (S1, S2: a young king, an empire, two earlier wins), then the field and Darius's plan drawn on the map (S3: the
levelled ground, the chariots, their planned charge), then the numbers and Alexander's plan (S4: march sideways, Darius must follow), then the
first turn (S5: the chariots fail), the decisive turn shown wide (S6.4, from above: the wedge into the gap) and then closer and lower (S7.1:
the wedge at the guard, Darius's chariot turns and runs), then the result (S8: the army breaks; 330 BC), then why it mattered (S9: the empire
changes hands and grows to India). Humour stays in the narration and the timing: the cut to the low line on "Nobody knows exactly", the caption
ONE ANCIENT WRITER SAYS 1,000,000 landing on "truly ridiculous", the cut to the spent chariots on "So much for the secret weapon".

## Scene list (9 scenes, 27 shots, average shot 5.6 s)

| scene | time (s) | job | shots and camera plan |
| --- | --- | --- | --- |
| S1 A young king | 0 to 19.6 | a young king faces the most powerful empire on Earth, outnumbered | dawn. 1.1 low behind Alexander's horsemen (ALEXANDER tag) as his army walks into line, the plain ahead; across it the Persian host rises rank by rank on "the most powerful empire", slow push; caption 1 OCTOBER 331 BC; 1.2 reverse angle high over the Persian host toward the small army beyond ("outnumbered"), slow orbit; 1.3 crane up into the plan view under the title card |
| S2 The road east | 19.6 to 32.1 | who the king is and who waits for him | dissolve to the map of Asia. 2.1 Macedon (marker), the dashed march to GRANICUS, 334 BC and ISSUS, 333 BC (battle marks), slow pan east; legend opens with MACEDON / Alexander; 2.2 lower and east: PERSIA / Darius III joins the legend, his army appears at GAUGAMELA, push in on "his biggest army yet" |
| S3 The trap on the plain | 32.1 to 52.1 | Darius's plan: a flat plain, levelled, for the chariots | dissolve back to the plain. 3.1 the whole field from the south-west, place A River Tigris; 3.2 top-down over the levelled ground, a dashed ink ring draws round it on "smoothed", place B; the chariots roll out on "secret weapon"; 3.3 low and close (45 mm) on a chariot and its blades, key row Scythed chariots; 3.4 high angle: the planned charge drawn as five dashed blue arrows across the smooth ground |
| S4 Sideways | 52.1 to 79.6 | the numbers, then Alexander's answer | 4.1 top-down plan, 47,000 counter on the map and in the legend; 4.2 cut low along the endless Persian front on "Nobody knows exactly", caption ONE ANCIENT WRITER SAYS 1,000,000 on "truly ridiculous"; 4.3 top-down: a dashed ink arrow straight ahead (fades: "instead of"), then the red arrow to the right as the whole army slides east off the levelled ground (camera follows); 4.4 from behind the Persian line: the blue arrow, the line stretches to follow |
| S5 The chariots charge | 79.6 to 92.1 | the secret weapon fails | 5.1 low behind the chariots as they charge; 5.2 high angle: the columns step apart into five lanes; 5.3 low behind the Macedonian rear: the chariots come through the lanes at the camera and are stopped at the back (ranks thin); 5.4 cut on "So much for the secret weapon" to the plan view, the spent chariots greyed; legend highlights Scythed chariots |
| S6 The gap | 92.1 to 112.6 | Darius stretches too far, Alexander charges | 6.1 wide and high: Persian horsemen ride round the right, the line stretches; 6.2 top-down on the centre: the gap opens, gold dashed ring, THE GAP; 6.3 low behind Alexander's horsemen looking at the gap ("exactly what he had been waiting for"), slow push; 6.4 the decisive moment wide from above: the wedge (COMPANION CAVALRY) grows and drives into the gap on the red arrow, straight at Darius (DARIUS tag); legend highlights Cavalry |
| S7 The king runs (climax) | 112.6 to 124.6 | how it worked, closer; the price on the other wing | 7.1 closer and lower (40 mm): the wedge reaches the guard, Darius's chariot turns and runs east on the dashed arrow, the guard thins; 7.2 meanwhile on the left: Persian horsemen fall on PARMENION, dust; 7.3 high and wide: Alexander turns back on the red arrow |
| S8 The army falls apart | 124.6 to 136.1 | the result | the light turns to a low red sun. 8.1 pull back over the field: the Persian blocks turn, drift north and thin out (numbers, never wounds), PERSIA dims in the legend; 8.2 low into the red sun: Darius's lone chariot runs east over the Tigris and fades; caption 330 BC |
| S9 Master of Asia | 136.1 to 151.3 | why it mattered | dissolve to the map of Asia: Alexander at Gaugamela, the Persian Empire appears as a hatched red territory, then a long pull out as it stretches from GREECE to INDIA on the red arrow; legend highlights Macedon; end card at 147.05 |

Living world in every wide shot: drifting cloud shadows, wind gusts over the grass, glints moving down the Tigris, two camps (the Persian camp
behind its army, the Macedonian camp on the southern hill: tents, fires and smoke, people walking), travellers on two roads, three flocks of
birds, banners in the wind, army dust; dust columns at the gap, at Parmenion's fight and over the broken army.

## Measured
Stills on free GitHub runners (rc-render `stills.yml`, 1280x720); the local box is shared by several builders, so no timing is measured here.
A local 640x360 smoke test rendered in about 3.5 s per frame after a 27 s start.

## Known weak spots
- The army sizes are symbolic: five small chariot blocks stand for about 200 chariots, four elephants for fifteen; figures are miniatures.
- The asia map is schematic and not to scale.
- The Persian strength is left blank in the legend on purpose (the narration says nobody knows).
- Labels are placed by hand; no automatic collision avoidance with the legend panels.
