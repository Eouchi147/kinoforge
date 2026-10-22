# The Battle of Waterloo (1815): Battle Map film notes

Engine: `films/lib/battlemap/` (spec format: `SPEC.md` there). Film spec: `spec.js` (all times come from `cues.json` words, so a re-cut of the
voice moves the picture with it). 16:9, 24 fps, 158.506 s. Terrain style (engraved relief map). Colours: French blue, Wellington's British-led
army red, Prussians green, Imperial Guard blue with gold trim (elite block). Every word on screen is set in code, no dashes, no ellipsis.
Extra icons (hat, farm, clock, bed, sun, rain, cannon, hedgehog, island, oops) live in `icons.js` and are registered in `index.html` with
`registerIcon` (the engine has no film specific code). No engine file was changed by this film.

## Shot list against the cues

| time (s) | cue | picture |
| --- | --- | --- |
| 0 to 1 | | black card fades out |
| 1.3 to 10.3 | l00 hook | Europe relief map (stage `eur`), JUNE 1815; a bicorne hat pops onto Paris on "Napoleon" (NAPOLEON, then HE IS BACK with a burst on "back"); a stop sign over the hat on "enough" (EUROPE HAD HAD ENOUGH) |
| 10.7 to 15 | l01 | title card THE BATTLE OF WATERLOO, then 1815, map dimmed behind |
| 15.7 to 28.3 | l02 | France is blue; crown on the hat (EMPEROR OF FRANCE) and it falls off on "beaten"; ship on a dashed arrow to ELBA (island icon); escape: ship back to the coast, solid arrow to Paris, hat and crown back (BACK IN CHARGE); on "declared war" six red arrows converge on France; on "all of it" the second bake of the map (`eurW`, land red, France stays blue) fades in over 1.1 s (ALL OF IT) |
| 29 to 42 | l03 | cut to the Belgian field, wide: French blue line on "him" (NAPOLEON + hat), Wellington's six red blocks on "armies" (WELLINGTON'S ARMY, red helmet), Prussian green blocks far east on "Prussian" (BLUCHER, 72 YEARS OLD with a star, NEVER GAVE UP) |
| 42 to 47 | l04 | plan: blue arrows hit the centre and the east, then red and green dashed arrows reach toward each other and are stopped by a no sign (ONE AT A TIME, KEEP THEM APART) |
| 47 to 59 | l05 | 18 JUNE 1815; the red column deploys onto the ridge (THE RIDGE, WATERLOO); on "Most of his soldiers" the blocks slide behind the crest and vanish below the skyline, only their flags show (HIDDEN BEHIND THE CREST); French guns (cannon icons) rise on the French ridge on "guns" (FRENCH GUNS) |
| 59 to 67 | l06 | low push over the valley; farm icons on "farmhouses", red flags and garrisons on "forts"; camera moves to HOUGOUMONT (west) then LA HAYE SAINTE (centre) |
| 67 to 77 | l07 | rain: five rain clouds, dark haze (light track); NAPOLEON waits (hat, clock); "Until almost midday": a gold dashed arc with a sun climbing along it, haze clears; "very expensive lie in": a bed with Z z under the hat |
| 78 to 83.5 | l08 | camera west; two blue blocks hit Hougoumont and bounce back three times (arrows redrawn each time), a clock spins (ALL DAY LONG), then NEVER TAKEN with a check |
| 84 to 93 | l09 | four French blocks march at the centre (FRENCH INFANTRY); two red cavalry blocks charge from behind the ridge, the French are pushed back; the cavalry goes on to the French line (TOO FAR, oops mark, dashed overshoot arrow) and fades by numbers |
| 93 to 105 | l10 | three French cavalry blocks ride up the ridge; Wellington's blocks step up and shrink into squares (SQUARES, hedgehog icons, HEDGEHOGS OF BAYONETS); the cavalry circles the squares twice and rides off (THEY WILL NOT CHARGE, no sign) |
| 105 to 113 | l11 | camera pans far east; four green blocks arrive along a long dashed route from the map edge (FAR TO THE EAST, PRUSSIANS, THROUGH MUD with a rain cloud, LATE with a clock, BUT COMING) |
| 113.7 to 124 | l12 | evening light; the Prussians hit the French right flank at Plancenoit (burst); the Imperial Guard drops in at the French rear (LAST AND BEST, star) and goes up the road to the ridge |
| 124.5 to 134 | l13 | the red blocks step up out of the corn field (TALL CORN), two volleys on "fired" (FIRE), the Guard falls back, the whole French army turns and runs off the map, split left and right (RUN) |
| 134.5 to 139.3 | l14 | low evening sweep behind a dark scrim, red helmet, plate THE DUKE OF WELLINGTON with the quote line by line on the words |
| 139.5 to 142.9 | l15 | FOUR DAYS LATER; hat and crown, the crown drops on "throne" |
| 142.9 to 148.3 | l15 | full screen cut to the South Atlantic (stage `atl`): a tiny island on a big ocean, ship on a dashed arrow, SAINT HELENA, then a door slams (NO ESCAPING) |
| 148.95 to 154 | l16 | dictionary plate: WATERLOO, idiom, "to meet your Waterloo", "to meet the one thing that finally beats you" |
| 154.3 to 158.5 | end | end card BATTLE MAP + "The Battle of Waterloo, 1815" |

## Build notes

- Stages: `world` (the battlefield, 900 x 580 units), `eur` and `eurW` (the same Europe polygons baked twice with different palettes: the
  palette is keyed by height, France is lifted so it paints blue, the other lands are parchment in `eur` and red in `eurW`; the second bake
  fades in as a full screen inset), `atl` (South Atlantic). Insets are full screen so the main stage is skipped while they show.
- Geography is stylised and not to scale: the ridge, the road north to south (Brussels road), the crest lane (a thin road on the ridge), the
  Hougoumont wood, villages left out except named labels, the Dyle on the east edge. Europe and the Atlantic are hand polygons.
- Losses are fading blocks (the cavalry in l09), never wounds. The French rout is a block run, not casualties.
- No numbers on screen other than 1815, 18 JUNE 1815 and 72 YEARS OLD (all in the narration).

## Known weak spots

- The ground is a calm engraved plain; the low evening sun in l12 to l15 makes hard relief shadows.
- Europe is a rough hand map; Italy and the Baltic are crude. Elba is almost touching the coast of the mainland at this scale.
- The Prussians appear at the east map edge (x 440), close to the fog edge; the dashed route stays readable but the blocks are small.
- `registerIcon` and `fallAt` (crown falling) are small additions other builders put in the shared engine files; if they are not in the tree,
  the icons do not draw and the crown does not fall.
