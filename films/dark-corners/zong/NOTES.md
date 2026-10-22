# The Ship Called Care (Dark Corners ep. 2): build notes

Lantern Road style: procedural painted 2.5D multiplane, motivated light, the lantern as the motif.
9:16, 179.4 s, 24 fps, rendered at 720x1280 (deliver 1080x1920). Picture follows `audio/mix.m4a` and `cues.json`; every cut sits on a `strong_hits` time or a narration start (the cut list is `SEQ` in `shots.js`).

Run: `node harness/render.cjs films/dark-corners/zong --w 720 --h 1280 --audio films/dark-corners/zong/audio/mix.m4a --mp4` (add `--start/--end` for chunks, `--param kr=3` for a stronger Kuwahara, `--param prof=1` for set build timings).

## Sets (one file each, built lazily, LRU of 3 live sets)
- `sea.js` + `seaextra.js`: sea at dusk / moon / dawn (swell bands, ship, glows), Jamaica ridge, Black River harbour, captain with spyglass, Zong/Zorg name board, hull seen from the water with one rope and the climber, rain, rings.
- `deck.js`: night deck, swinging lantern, casks (water level, drips, rain), chain (coil, hang).
- `court.js`: London court, candle groups that go out one by one, jury, judge, lawyer, dock.
- `docs.js`: documents (claim, ledger, rule, the quoted line, King's Bench record) with ink that writes in.
- `section.js`: ship in section, 17 crew and 440 amber dots counting down to 208.
- `street.js`: London lane at night, Equiano with a hand lamp, Sharp, the letter, the lit study window.
- `road.js`: hill road, lamps taking their light one by one, dawn rising (1807).
- `lantern.js`: the ship's lantern close up (night / dusk / dawn), flame goes out at 176.05 to 176.6, smoke.

## Shot list against the cues (start s)
0 o1a/o1b sea dusk, promise | 6.9 o2a court | 9.9 o2b claim doc | 11.6 o3 lantern night | 14.6 title card | 17.5 x1a Zong, name board | 20.5 x1b | 24.8 x1c lantern dusk (care) | 28.3 x2a-x2c ship section, 17 crew, 440 captives | 38.2 x4 ledger | 42.4 m1a/m1b Jamaica passing unseen, captain's glass | 50.9 m2a moon sea | 54.2 m2b casks low | 58.4 m3a-c the rule | 70.5 d1 deck, 29 Nov by absence (empty deck, swinging lantern) | 75.1 d2a/d2b | 81.1 d3 | 84.2 r1a/r1b rain fills casks | 90.4 r3a chain coil | 95.0 r3b rings on the water | 98.2 r3c hanging chain | 101.0 p1a/p1b moon sea | 103.9 | 106.4 a1a dawn ship | 109.1 a1b Black River | 111.7 a1c 440 to 208 | 115.6 c1 claim | 120.6 c2 jury | 125.0 c3a lawyer | 127.6 c3b quoted line as a document | 131.3 e1a-e1c Equiano and Sharp, the letter | 143.0 e2 Sharp writing | 146.6 j1a/j1b King's Bench, record | 155.4 j2a candles out | 158.6 j2b | 162.1 f1a/f1b ledger, price only | 167.1 f2a lamps ignite up the road | 172.3 f2b 1807 | 174.0 f3 lantern dawn, goes out | 176.8 end card (black) | 179.4 end.
Title card 14.9 to 17.4, end card 176.8 to 179.4.

## Restraint
No drowning, no bodies shown. Scale is shown by numerals and amber dots. 29 November is shown only by an empty deck, a swinging lantern and the sea. The one figure in the water scenes is a man holding a rope against the hull, as a dark silhouette. Equiano and Sharp are faceless silhouettes.

## Measured (local 2-core box, software GL, no GPU), 720x1280
- Kuwahara radius 3: about 4.2 s/frame. Radius 2 (the default now): about 2.1 to 2.3 s/frame steady (120-frame road stretch 2.15 s/frame, 0.8 min per 24 frames). Radius 1: 2.0.
- Set build costs: street about 3.1 s, others 1.5 to 4 s each (once per set per chunk).
- The Kuwahara pass is about half the frame time. A GPU runner would be far faster; whole film is 4306 frames, so about 2.5 h single-threaded on this box, split into chunks on the farm.

## Weak spots
- Figures (Equiano, Sharp, the climber) are blocky silhouettes, readable but crude close up (e1b).
- Hull side wall is flat; the Zong stern cabin reads as a box in close shots; palms on the Jamaica ridge are scraggly.
- The street ground edge meets the building bases in a straight line.
- Label BLACK RIVER overlaps the mast in a1c; captions on pale paper rely on a dark scrim.
- `tools/check.mjs` does not exist in this repo (kinoforge); `node --test tests/*.test.mjs` found no tests.
