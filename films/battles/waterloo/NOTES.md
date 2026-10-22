# The Battle of Waterloo (1815): Battle Map film notes (v2)

Engine: `films/lib/battlemap/` v2 (spec format: `SPEC.md` there; reference film `films/battles/cannae/`). Film spec: `spec.js`.
16:9, 24 fps, 158.506 s. Narration timing is locked to `cues.json` (line starts never change; the score is re-done around them).
Look: engraved relief map, armies as painted miniatures on trays. French blue, Wellington's British-led army red, Prussians green.
`node films/lib/battlemap/tools/scenes.mjs films/battles/waterloo` prints the plan below with the checks.

Film-side additions (`units.js`, registered from `index.html`, no engine file changed):
- `artillery` figure kind: a field gun on its carriage (two spoked wheels, trail, bronze barrel) with two gunners, added to the
  engine's exported `FIG_KINDS` before the film starts, so the French grand battery stands on the map as real guns on trays.
  The legend's Artillery row uses the engine's `u-artillery` unit symbol.
- `tricolore` glyph (the French standard: a staff with a gold eagle finial and a vertical blue, white, red flag) for the legend and Paris.
- `brig` glyph (a flat two-masted sailing ship in the team colour) that follows the exile and escape routes and the voyage to Saint Helena.
- Squares are built from blocks, not drawn: at "formed squares" each of the four central line blocks contracts into the south face of a
  hollow square and three thin faces (north, east, west, each facing outward) rise rank by rank. The French horsemen ride through the
  gaps between the squares and back; the spacing solver keeps them out of the squares.

## How the battle is explained (CRAFT.md section 7)
Stakes and people first (S1: Napoleon is back and all Europe turns on him; S2: the two allied armies and their commanders), then each
side's plan on the map (S2.4: drive a wedge between them), the field (S3: the ridge, the hidden line, the farms as forts), the delay (S4),
the attacks (S5, S6), the turn (S7: the Prussians arrive, the Guard goes in), the decisive moment shown twice (S8.1 wide from above: the
line rises and fires; S8.2 low and close: the Guard reels back under the smoke), the result (S8.3 the rout, the legend dims France), then
why it mattered (S8.4 the Duke's words, S9 exile and the idiom). Humour stays in the narration and the timing: the hold on the Emperor's
headquarters through "a very expensive lie in", the cut to the wide shot on "and then charged a bit too far", the slow push on the speck of an
island through "No escaping from that one."

## Scene list (9 scenes, 28 shots)

| scene | cue | job | camera plan |
| --- | --- | --- | --- |
| S1 The return (Europe map) | 0 to l03 | Napoleon is back, and this time all of Europe turns on him | 1.1 Europe wide (caption JUNE 1815), slow push to Paris on "Napoleon" (French standard, NAPOLEON), pull back to the continent on "Europe had had enough", crane up under the title card; 1.2 follow the exile to Elba and the escape back to Paris (the brig rides the dashed routes); 1.3 wide Europe: six red arrows converge on France on "declared war", the whole continent turns red on "All of it" (second bake of the map fades in) |
| S2 Two armies | l03 to l05 | who waits for him in Belgium, and his plan to beat them one at a time | dissolve (change of world). 2.1 high over the field from the south: the French line arrives on its ridge; 2.2 high oblique on Wellington's army in column (WELLINGTON, legend adds the allied army); 2.3 far east, low: the Prussians and their old marshal (BLÜCHER, legend adds Prussia); 2.4 top-down plan: a blue wedge drives between the red and green dashed arrows that reach for each other |
| S3 The ridge | l05 to l07 | Wellington's position: a hidden line behind a ridge, two farms turned into forts | 3.1 high oblique from the French side: the army files onto the ridge (caption 18 JUNE 1815, places A ridge, B Waterloo); 3.2 low behind the French guns looking up the slope: the line steps back behind the crest and drops out of sight (legend adds Artillery); 3.3 high over the valley: Hougoumont (C) on one side, La Haye Sainte (D) in the middle, garrisons in each |
| S4 The lie in | l07 to l08 | rain delays the attack until almost midday | rain haze and heavy cloud clearing through the scene. 4.1 low from the allied ridge over the wet valley to the waiting French; 4.2 the sky clears: slow push on the Emperor's headquarters (caption 11:30 AM), held through "a very expensive lie in" |
| S5 Morning attacks | l08 to l10 | the French attack all day and fail: Hougoumont holds, the centre is thrown back, the British cavalry goes too far | 5.1 west to Hougoumont: two waves break on the walls and fall back thinned; 5.2 low behind the French columns climbing at the centre; 5.3 high from the flank: the British cavalry comes through the gap in its line and throws them back; 5.4 cut wide on the punchline: the horsemen run on into the French guns and thin out |
| S6 The squares | l10 to l11 | the French horsemen against squares that will not break | 6.1 low behind the horsemen riding up the slope (legend highlights Cavalry); 6.2 top-down: the line folds into hollow squares, the horsemen flow through the gaps (the key panel steps aside so it does not cover the left square); 6.3 low and close beside one square: the horses will not go in |
| S7 The Prussians come | l11 to l13 | the Prussians arrive late, and Napoleon plays his last card | 7.1 far east, high: the Prussians on the long dashed road, late but coming (legend highlights Prussia); 7.2 evening light: they smash into the French flank at Plancenoit, two French blocks wheel to face them; 7.3 low behind the Imperial Guard as it climbs the road to the ridge |
| S8 The turn (climax) | l13 to l15.This | the decisive moment, then the cost and the verdict | 8.1 wide and high: the line rises out of the corn and fires (musket smoke), the Guard thins; 8.2 the same moment low and close: the Guard reels back; 8.3 high and wide: the whole French army runs, arrows fan out, France dims in the legend; 8.4 low evening sweep over the emptied field under the Duke's words (card; the routed blocks have left the map); 8.5 the abandoned French ridge at dusk (caption 22 JUNE 1815) |
| S9 Saint Helena | l15.This to end | exile for good, and the word it left behind | dissolve to the South Atlantic: the brig sails the long dashed route, a slow push from the whole ocean to the speck of SAINT HELENA (caption 1,900 KM FROM AFRICA); the dictionary plate and the end card |

Legend: title THE BATTLE OF WATERLOO, 18 June 1815; sides FRANCE (Napoleon, about 73,000, `tricolore`), ALLIED ARMY (Duke of
Wellington, about 68,000), PRUSSIA (Marshal Blücher, about 50,000 reached the field), each on the word that names it; units Infantry
(all three), Cavalry (French and British), Artillery (French); places A the ridge, B Waterloo, C Hougoumont, D La Haye Sainte.
Numbers: commonly cited strengths on the field (French 72,000 to 73,000; Wellington about 68,000; Prussians about 50,000 engaged by evening).

Living world: cloud shadows, grass gusts, the Dyle glinting on the east edge, two bivouacs (tents, fires, people), wagons and walkers on
the Brussels road, two flocks of birds, gun smoke on the French battery from the first attack, Hougoumont burning in the afternoon,
Plancenoit burning in the evening, musket smoke along the ridge on "fired", army dust.

## Removed from v1
Cartoon icons and their `icons.js` (hat, crown, farm, clock, bed, sun, rain clouds, cannon clip art, hedgehogs, island, the "!" mark, stop
signs, bursts, the helmet over the quote) and the labels that only repeated the narration (HE IS BACK, ESCAPED, ALL OF IT, ONE AT A
TIME, KEEP THEM APART, IT RAINED ALL NIGHT, A VERY EXPENSIVE LIE IN, ATTACK, ALL DAY LONG, NEVER TAKEN, TOO FAR, HEDGEHOGS OF BAYONETS,
THEY WILL NOT CHARGE, THROUGH MUD, LATE, BUT COMING, FIRE, RUN, NO ESCAPING and the rest). Kept: names, dates, numbers.

## Checks (22 Oct)
`tools/scenes.mjs`: 9 scenes, 28 shots, average shot 5.6 s, 0 errors, 0 warnings. `films/director/check.cjs`: no hard problems (the
artillery blocks are `kind: 'marker'` with `figures: 'artillery'`, because the director's lint only knows the engine's kinds; the manual
red-Europe inset carries a `why`). Contact sheet: one still per shot with the narration under it.

## Known weak spots
- Europe and the South Atlantic are rough hand maps, not to scale (Elba sits almost on the coast).
- The squares are 22 units (about 180 m) across so they read from above; real squares were far smaller.
- Compressed army moves (the Hougoumont waves, the cavalry charge) are faster than real marching, as in every Battle Map film.
- Labels are placed by hand (`dx`, `dy`); the legend panels cover the left quarter of the frame, so shots keep the action centre right.
