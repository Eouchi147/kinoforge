# The Battle of Thermopylae (480 BC): Battle Map film notes

Engine: `films/lib/battlemap/` (spec: `SPEC.md` there). 16:9, 24 fps, 164.113 s, Terrain style. Persians red (team `rome`), Greeks blue (team `carthage`). All times come from `cues.json` words.
The ASR spelled some words oddly in the cues: "Dianik," (Dienekes), "Effialty's" (Ephialtes), "Thespier", and "past" for "pass" (l10, l17): the spec uses prefixes or neighbouring words.

## Film-side code (no engine change)
- `icons.js`: throne (hops 3x with a counter bubble), calendar (`fill: "start,stepSeconds,HEADER,max"`), sundim, cool (helmet in sunglasses), moon, burn, bag, stone, peak, wave, hourglass, shout.
- `fx.js`: patches `StageOverlay.draw` for `spec.dim` (veil, stars for the night), `spec.regions` (hatched ground area that sweeps west to east, with sea holes: the Persian Empire) and `spec.nums` (the "millions" plate that crashes to "100,000+").

## Structure
- Main stage: the pass (cliff wall west, sea east, road between; sun from the east so the cliff face is lit), x east, z south, Persians come from the north.
- Stage `aeg` (Aegean): hook 0 to 12.95, the squabbling cities 34.3 to 40.95, Athens/Salamis/Plataea 133.7 to 149.9. Stage `emp` (Persian Empire): 17.4 to 34.6.
- Title card 12.95; epitaph card from 154.1 (lines timed on the cue words); end card from 159.913.

## Shot list (seconds)
0 to 12.9 hook on the Aegean (480 BC, army floods across the Hellespont, tiny Greek block at the gap) / 12.95 title / 17.4 empire shading Egypt to India, "millions" plate crashes to 100,000+, "STILL: A LOT." / 34.3 cities squabble (arrows) then team up / 41 pass: steep mountains, sea, narrow road, army squeezes / 53 Greeks (7,000 counter, Leonidas, 300) / 60 Xerxes waits, calendar DAY 1 to 4, Greeks do not run / 66 Herodotus, arrows darken the sky, Dienekes plate, "fight in the shade" / 79 DAY 5, waves, shield wall rotates / 89 Immortals bounce, throne hops 3x / 99 TWO DAYS, DAY 6, THE PASS HELD / 102 Ephialtes, dotted path around the mountain / 110 night climb / 113 surrounded, most Greeks leave, Spartans + 700 Thespians stay / 126 DAY 7, they fought to the end (blocks fade) / 132 Persians win, Athens burns / 139 Salamis ships, Plataea 479 BC / 150 stone, epitaph / 159.9 end card.

## Measured
1280x720 SwiftShader: stills 0.5 to 1.5 s; a 5 s stretch (frames 1976 to 2096, the waves) rendered at 0.56 s/frame.

## Known weak spots
- Persian waves are a few red blocks (stylised); the Aegean/Empire coasts are simplified; the Immortals block bends when the path turns sharply.
- Camera keys on the night climb are hand-placed along the path; check them if the voice is re-cut.
