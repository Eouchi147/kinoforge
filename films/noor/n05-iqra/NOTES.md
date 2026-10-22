# NOOR · The Descent · Night Five · Iqra (Lantern Road, 16:9)

A look sample for the NOOR Ramadan 2027 series (bible: Claude doc "NOOR · Thirty Nights of Light"). About 3.5 minutes,
1280x720 render, 1920x1080 delivery, 24 fps. The picture follows `audio/mix.m4a` through `cues.json` (written by
`films/noor/lib/place.py` from the Chatterbox narration); no time is typed into the shot list, every cut is a cue reference.

## Rules kept (non-negotiable for NOOR)
- No prophet, angel, Companion or named person is ever drawn: no figure, face or silhouette. The Prophet's presence is a
  hand lantern alone on the mountain path, the empty cave, the mat where he sat, the lantern set down at his door.
  The angel is light only: the sky behind the mountain and the mouth of the cave fill with white-gold light. Nothing depicts Allah.
- Qur'anic Arabic is set in code in Amiri Quran (`films/noor/fonts/`, OFL), copied from `script.json` (King Fahd Complex
  Uthmani text via quranenc); never generated, never retyped. No AI imagery: every image is painted procedurally.
- No em or en dashes, no "..." on screen. Captions are the display text (the voice reads spelled-out names).

## Files
- `scene.js` boot, camera, per-frame context, dissolves. `shots.js` the shot plan and captions. `type.js` all type (captions,
  labels, title and end cards, the word, the verse panel). `kf.js` multiplane core and post chain (from Kleidion, 16:9).
- `paint.js`, `ambient.js` (from Kleidion), `fx.js` (glows, hand lantern, fanous, twinkling stars).
- `sets/`: `mountain` (Jabal an-Nur, the path, the cave notch, Makkah's lamps; modes night, dusk, light, dawn), `cave` (inside
  Hira looking out: mat, water skin, dates, clay lamp; modes dusk, night, light, pulses), `valley` (Makkah at dusk: the Kaaba,
  small idols in a ring, houses, cook fires, specks of people), `house` (a lit doorway, folded cloak, the lantern on the step),
  `sky` (title lantern, the word in gold light, the calm night behind the verses, the end lantern).
- `tools/stills.cjs` stills in one browser session (`--shots` = two per shot; `--param dbg=1`, `noglows=1`, `glowoff=i`, `hide=plane`).

## Shot list (scene: shot, set, cue span, reason for the cut)
1. Cold open: `o1` mountain night, c1 to c2: a dark peak, one lamp burning high in the rock. Slow push.
2. Title: `title` sky, the title gap: a lantern rises; NOOR, The Descent, Night Five · Iqra, the word in Arabic. (new world: the series)
3. Where: `a1` mountain dusk, w1 (place) / `a2` cave dusk, w2 (inside: what it is) / `a3` mountain closer, w3 (names: JABAL AN-NUR, HIRA with a leader). Changes of scale.
4. The valley: `b1` valley dusk, w4 to w5: loud life, the idols round the Kaaba (new place).
5. One man: `c1` mountain night, w6 to w7: the hand lantern climbs the path / `c2` closer, w8: label AL-AMIN, the lantern reaches the cave / `d1` cave night, w9: water, dates, the lamp.
6. The night: `e1` cave, e1: the mouth fills with light / `e2` mountain, e2: the sky behind the peak is light / `e3` sky, e3: the word writes itself, READ / `e4` cave, e4 to e5: light breathes on each ask / `e6` cave close on the mat, e6: the third ask.
7. The first words: `v` sky, e7 to v5: the illuminated panel draws itself; each verse lands with its meaning (captions off: the panel carries them).
8. What it means: `f1` mountain night, m1 to m2 (the word stays) / `f2` mountain, m3: the lantern hurries down / `f3` house, m4: the doorway, the cloak, the lantern on the step.
9. Time: `f4` mountain dawn, m5 (dissolve: time passes; stars wheel, dawn).
10. The lantern sky: `l` sky, l1 to the end (dissolve): one lantern rises with the word; end card "NOOR · Thirty Nights of Light · Tomorrow · Night Six".

## Known weak spots
- Wide sets are painted at screen density; the closest lenses (a3, c2 at 64 to 74 mm) soften the peak (painted at q 2 to help).
- The valley houses are simple boxes; the Kaaba and idols are tiny by design (wide only).
- Dusk and dawn warmth comes from tinting the painted sky; a big glow mesh on the sky plane leaked over the peak and was removed.
