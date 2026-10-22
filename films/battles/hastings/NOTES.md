# The Battle of Hastings (1066): Battle Map film notes

Engine: `films/lib/battlemap/` (spec: `SPEC.md` there). Film spec: `spec.js`; every time is a cue word, so a re-cut of the voice moves the picture.
16:9, 24 fps, 155.401 s. Colours: English royal blue, Normans deep red, Vikings gold. Two maps: the main stage is England and Normandy
(hook, build-up, Christmas coronation, the French words); the `bat` stage (Senlac hill: ridge, gentle south slope, marsh ponds and woods
at the sides, the London road north) is shown full screen from 53.4 s to 134.4 s.

## Shot list against the cues

| time (s) | cue | picture |
| --- | --- | --- |
| 0 to 12 | l00 hook | map of England and the Channel; "1066"; three crowns pop in on "three kings", two get red crosses on "battle" and "decided", a star on "the last one" |
| 12.3 to 17.3 | l01 | title card THE BATTLE OF HASTINGS + 1066 |
| 17.4 to 23.9 | l02 | JANUARY 1066, the old king's crown falls, Harold's blue block appears in London and is crowned |
| 23.9 to 34 | l03 | Normandy, DUKE WILLIAM, crown with a question mark on "excuse me", three ships on "fleet" |
| 34 to 43 | l04 | Viking ships (gold) sail in, Harold marches up the road (blue arrow), Stamford Bridge: Vikings fade, laurel |
| 43 to 53.4 | l05 | the fleet crosses to Pevensey, Harold's dashed march back with a MILES counter 0 to 250, BUSY MONTH |
| 53.4 to 63 | l06 | 14 OCTOBER 1066, Senlac hill, English wall (8 blocks + second line + Harold) appears block by block, shield icons |
| 63 to 73 | l07 | Normans below: archers, foot soldiers, knights, William; UP THE HILL arrow, NOT FUN |
| 73 to 84 | l08 | volleys onto the wall, knights charge and bounce back, the wall holds, HOUR 1 / 2 / 3 ticks |
| 84 to 91 | l09 | A RUMOR, WILLIAM IS DEAD! blocks wobble and run, William fades to a ghost with a cross |
| 91 to 98 | l10 | William's block lifts (banner), helmet icon, I'M ALIVE!, the Normans turn around |
| 98 to 104 | l11 | book icon "the Norman writers say", A TRICK, gold dashed arrows downhill |
| 104 to 111 | l12 | two English blocks chase down the hill, gap in the wall, knights wheel in from three sides, gold loop, chasers fade |
| 111.7 to 117 | l13 | AGAIN / AND AGAIN with the other pair, the remaining wall squeezes: THE WALL GETS THINNER |
| 117 to 130 | l14 | evening light, KING HAROLD, crown falls and his block fades; tapestry strip (plain, then with ?), MAYBE, two books (historians argue), three question marks |
| 130.8 to 134.4 | l15 | the English blocks scatter and fade, THE ENGLISH ARMY BREAKS |
| 134.6 to 141 | l16 | back to the map: CHRISTMAS DAY, William's block marches to London, crown, WILLIAM THE CONQUEROR |
| 141 to 151.2 | l17 | FRENCH / ENGLISH, BEEF JURY JUDGE float across the Channel on dashed arrows, ALL THANKS TO ONE LONG AFTERNOON ON A HILL |
| 151.2 to 155.4 | end | BATTLE MAP + The Battle of Hastings, 1066 |

## Engine additions (backward compatible, Cannae unaffected)
Icons `shield`, `tapestry` (`fill:'plain'`), `cross`; `fallAt`/`fallDur` on icons (a crown that drops). Documented in SPEC.md.

## Known weak spots
- The English map is stylised (not to scale); the Channel is narrow so Normandy is a strip at the bottom of the frame.
- Soldiers are lattice blocks; the chase and the surround are readable by colour and the gold loop, not by individual figures.
- The dusk ridge has strong relief shading; the tapestry strip sits over the sky/wall in 120 to 130 s.
- No numbers on screen except the 250 MILES counter (the narration gives none).
