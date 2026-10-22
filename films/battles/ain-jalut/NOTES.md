# The Battle of Ain Jalut (1260): Battle Map film notes

Engine: `films/lib/battlemap/` (spec format: `SPEC.md` there). Film spec: `spec.js` (all times come from `cues.json` words). 16:9, 24 fps, 139.628 s.
Terrain style, Mamluks deep red, Mongols royal blue. The ASR in the cues misspells names (l01 "Angelut", l06 "Ainjalut", l11 "mondles", l12 "Khutuz", l15 "Katoos"):
the spec uses the cue spellings (`l06.Ainjalut,`, `l12.Khutuz`), screen text is spelled correctly. No engine change.

## Film-side code
- `icons.js`: scroll (fill `censor` = the black-barred reply), spring, hat (a trick), mirror, copy, smirk, puff, horn, bush via `registerIcon`.
- `fx.js`: patches `Stage.update` and `StageOverlay.draw`. `spec.ink` = territory that spreads over the ground like ink (blobs baked into a canvas, draped on
  the terrain as one mesh under the blocks); `spec.bar` = the growing timeline bar (1260, 250+ YEARS).

## Structure
- Stage `emp` (stylised Asia, Middle East, Eastern Europe; 1 deg longitude = 6 units, 1 deg latitude = 8; not to scale in the Levant) shown full screen 0 to 60 s
  and again 113.2 s to the end. Main stage = the valley (valley floor west to east, ridges north and south, Goliath's Spring in the west), 60 to 113.3 s.
- Shot list: hook (ink spreads from Mongolia, ALMOST NEVER LOST, horde rides into Palestine, red block + hat "a trick or two") / title card 13.3 / empire,
  China to Eastern Europe arrow, Baghdad 1258, Damascus / letters (scroll icons travel on arrows, SURRENDER OR ELSE, censored reply NOT POLITE) / luck changes
  (crown tips over in Mongolia, big arrow back east, smaller army under Kitbuqa) / Qutuz and Baybars march from Egypt / valley: date, spring, hills / the trick
  (hat, copy, Baybars fights, smirk, dashed retreat arrow, mirror, Mongols charge) / HIDDEN IN THE HILLS (bushes, red blocks appear on both ridges) / AMBUSH,
  line bends, helmet drops, OH ISLAM burst + horn, second charge, Kitbuqa's banner falls, Mongol blocks fade away / map again: BEATEN, NO REVENGE, stop line
  and no sign at Egypt / Qutuz's crown and helmet, puff, crown on Baybars, TEAMWORK. + smirk / red ink over Egypt + timeline bar 250+ YEARS / end card 135.43.

## Known weak spots
- The Mediterranean reads as a very large lake at close zoom; the empire ink is a flat wash (blocks under it have less contrast).
- The ambush scrum overlaps blocks; it reads as a melee, not as individual units. Kitbuqa's death is only a falling banner and a fading block.
- Egypt's red ink is small; Mamluk rule after 1517 is not shown (narration gives only 250+ years).
