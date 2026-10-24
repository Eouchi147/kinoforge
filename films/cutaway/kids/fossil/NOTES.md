# Fossil pilot (Little Big Questions): the picture

23 Oct 2026. A silent 65 s story (Sam 20:09: no narration; real orchestral music and real sound effects carry it; a few
big words set in code), choreographed to Grieg, Morning Mood (Musopen Symphony, public domain; Sam's pick 21:00, the edit
is described in `beats.json`). Source of truth: `beats.json` (10 beats: picture, words, sound, music). `ad.json` voice
lines are obsolete for this film. Fable Cutaway look on the seasons grammar: one fixed view, a 2 degree sway on one sine
over the whole film, no cuts. 16:9, rendered 1280x720, delivered 1920x1080, 24 fps, 1560 frames.

## Timing: one table, re-timed by beats.json
`szworld.py` reads `beats.json` (beat ranges, words, the duration: 65.0 s, so the harness renders 1560 frames). Every event
of the picture is in ONE table at the top of `blender.py` (`EVENTS`: event, beat, fraction of the way through that beat);
`szworld.set_events()` turns it into seconds (`W.B.<event>`). The music's hits are entries of that table:
- the bone turns to stone on the hit at 43.0 s (`hit`, 5/6 of bone to stone);
- brush strokes 47.0 to 49.4 s; the bone appears and FOSSIL! pops on the climax at 49.5 s (`pit1`, `label0`, 1/3 of the find);
- she lifts her toy dinosaur on the final swell, 57 to 60 s (`hold0`, `hold1`);
- WHAT IS UNDER YOUR FEET? waits for the last quiet chord, 60 to 65 s (`words_send`, through `W.WORD_IN`).

If the beats are re-timed again, edit `beats.json` (and these fractions only if a hit moves inside its beat). Captions come
from each beat's `words`: in 0.35 s after the beat starts (or at `WORD_IN`), out 0.25 s before it ends, never under 2.5 s.
The key word is the label on the bone, timed by `label0` and `label1` (2.75 s).

## Beats (current beats.json times)
| Beat | Time (s) | What the picture does (event times) | Words |
| --- | --- | --- | --- |
| hook | 0 to 5 | Today: the slice floats over its hole in a sunny meadow that carries on all round (brook, trees, a village with chimney smoke, a train, sheep, kites); the stone skeleton in the front cut face, a glint sliding over it; the snail mascot on the front right corner leans over to look; the red ball rolls in (0.6 to 2.5) | HOW DO BONES TURN TO STONE? (0.35 to 4.75) |
| rewind | 5 to 10 | Today's plants fold (5.0 to 5.6); the ground above the old one peels away upward and fades (5.75 to 8.75); the sky runs back through days and seasons (soft blends, no flashing); the clock spins backwards; the land all round turns into the fern era; ferns grow (7.25 to 10.9); the dinosaur appears (8.5 to 10.3) | LONG AGO (5.35 to 9.75) |
| the living world | 10 to 21 | The long-neck walks to the ferns (10.0 to 12.2) and munches (12.2 to 19.5; the clump shrinks); two babies splash in the river; a turtle plods along the front with the snail riding it; dragonflies, lizards, birds; the duck-shaped yellow flower floats down the river (the visual joke); a volcano smokes far off, a herd walks the hills, pterosaurs circle | none |
| the old dinosaur rests | 21 to 25 | The babies grow (18.8 to 21.6) and walk off (21.2 to 24.6); the old one walks to the bank (19.5 to 22.4), lies down (22.4 to 23.6), its eyes close and it stays still (23.4 to 24.7; no breathing, never shown as sleep); evening gold (19.9 to 24.4); one leaf drifts down (23.0 to 24.9) | none |
| mud covers the bones | 25 to 30 | Rain; a gentle brown flood over the whole plain (25.4 to 29.75); the body fades and the skeleton remains (25.75 to 27.0); mud rises over it like a blanket with a soft hump (27.1 to 29.1); cream bones show in the new band of the cut face (28.6 to 29.75) | MUD (25.35 to 29.75) |
| layer on layer | 30 to 38 | Five layers, each brought by a short flood (rises at 30.1, 31.7, 33.3, 34.9, 36.5), each a new colour band with gold lines; the whole land rises with them; on each new top an era, on the block and all round: forest with saplings, ice, mammoths crossing a steppe, grassland, forest; the clock races; the hills behind rise | MILLIONS OF YEARS (30.35 to 37.75) |
| bone to stone | 38 to 44 | The magnifier window opens (38.1 to 38.6) above the fossil, tied to it by a small ring and two gold lines: drops fall into the pores of a big bone, each leaves a crystal sparkle, the bone turns ivory to stone grey with gold flecks from one end to the other (39.2 to 43.0); the face skeleton turns too, with blue drops seeping down the bands and a burst of gold stars on the hit (43.0); the window closes (43.7 to 44.4) | BONE TO STONE (38.35 to 43.75) |
| the land wears away | 44 to 47 | Wind and rain (44.0 to 46.6); the top and the land all round wear down band by band (44.1 to 46.4); the hills shrink; today's meadow, trees, village, train, sheep, kites return (45.65 to 47.4) | none |
| the find | 47 to 54.5 | The girl (hat, little brush, toy dinosaur in her hand) runs out from behind the big tree and hops the brook (45.7 to 46.9), kneels at the little rock face in a hollow, brushes (47.0 to 49.4); the bone appears out of the rock on the climax (49.5); she jumps for joy (49.6 to 51.65); birds fly up from the big tree; the dog drops its stick, dashes to the bone and sits by it, wagging hard | FOSSIL! label up and to the right of the bone, its leader clear of the girl (49.5 to 52.25) |
| the send-off | 54.5 to 65 | The red ball rolls back into view (55.3 to 57.4); she turns to us and lifts her toy dinosaur up next to the real fossil on the final swell (57.0 to 60.0); the snail waves its eye stalks (60.8); the meadow keeps living | WHAT IS UNDER YOUR FEET? (60.0 to 64.75) |

## The lifted slice in a living world (Sam 23 Oct: v3 framing; the v2 trench read as a swimming pool)
The Cutaway block is the hero again: a slice of land lifted out of the living world. It floats `-ZB + GAP` above its
origin (`szworld.lift`: its own depth plus a 0.32 m gap, about 0.3 of its height today), bobbing 2.5 cm on a 7.5 s sine.
All four cut faces show their strata with the gold lines (the walls mesh is rewritten each frame in the slice's own frame,
then lifted). Its top is the same era ground as the land around (one driven material).
- **Directly beneath it is the hole it came from** (`build_hole`): as deep as the slice and 0.10 m wider on every side. Dark
  earthy walls, darker towards the floor, with pebbles in the earth. Seventy roots and twenty-two pebbles hang off the
  slice's underside and sway a little, and a grain of soil trickles into the hole every few seconds (`underside_pose`).
- **The living world carries on around it at its natural level** (`fs_world`, 24 x 23 m, `szworld.land_h`), following
  every era in the same ground paint as in v2: today's meadow, the fern era, mud, ice, steppe, grassland, worn rock. It
  has the river, plants swaying, trees of both eras, floods over the plain, and the far curve-away horizon with the hills,
  their life and the sky beyond.
- **The river visibly continues into the slice's top and out again** (`fs_river`, one free quad per segment). It runs at
  the land's level outside the hole and at the slice's level on top, and the segments over the gap are left out. So it
  ends at the hole's rim and starts again on the slice: the slice reads as cut from this exact spot.
- **Everything on the slice rides it.** `top_h` adds `lift(t)` inside the slice's footprint (edges included). Absolute
  heights add it too: the face fossil, sparkles and drops (object offset), the 3D skeleton, the peel slab, the leaf, the
  bone in the rock face, the toy car, the kite, the birds, the magnifier target, the rain stop.
- **The girl** now runs out from behind the big tree at the back of the slice and hops the brook; the land around is
  1.4 m below her.
- **Camera:** fixed with the 2 degree sway. It is fitted on the slice plus its gap and the hole's rim, aimed 0.12 m higher
  (`CAM_DZ`). The block is the hero again, and the haze and light step on the land keep it so.

## Series rules (Sam 23 Oct 19:43 and 20:09, research 4.1; keep them in every film)
1. **Easter eggs kids know from their own lives**, several per film, some obvious, one or two hidden, animated where
   possible; only generic everyday objects, never a brand, a logo, a character or anything that looks like one. Here:
   the red ball rolling in and back (obvious), the toy car nose out of the right cut face's soil (hidden), the rubber
   duck bobbing down the brook, the kite stuck in the big tree and tugging, the teddy bear on the meadow, the toy
   dinosaur the girl lifts beside the real fossil, her dog with a stick.
2. **A living world, not a flat card**: the land the slice was lifted from carries on all round at its natural level, then
   three hill layers in depth (3.8, 5.8, 7.8 m behind the block, crests placed by screen height), the same era as the block, life far away (long ago: a smoking volcano, a herd of small long-necks,
   pterosaurs, tree ferns and conifers; today: a village with chimney smoke, a train on a viaduct, a red tractor, sheep,
   kites, round trees and poplars), drifting clouds, colours and light following the story; pieces rise out of or sink
   into their hills, staggered, when time passes. Fable's painted card remains only as the far sky.
3. **The mascot**: a small silent snail (coral and gold shell) in the corner of every block, who reacts and never
   speaks: peeks at the fossil, rides a turtle long ago, hides in its shell in the rewind, floods and rain, stretches up
   at the cheer, waves at the end.
4. **One small visual joke per film**, never sarcasm: here the duck-shaped flower floating in the dinosaur's river, and
   the dog sitting by the fossil as if it were its bone.
5. **Silent films**: the picture explains everything; words are few, big, in with a soft pop, at least 2.5 s on screen;
   the picture's events sit on the music's phrases and hits through the one event table.

## Files and jobs
| File | Job |
| --- | --- |
| `blender.py` | The event table (`EVENTS`), build and frame; camera (az -62, el 21, 50 mm, 2 degree sway); sun per mood; ground colour per era; the land around (`build_world`), the hole and the slice's underside (`build_hole`, `underside_pose`); water (river ribbon cut at the gap, flood box over the slice, flood sheet over the land); rain |
| `szworld.py` | `beats.json`, `set_events`, layer slots, word windows; heights in time (`base`, `slice_h`, `land_h`, `top_h`, `lift`: relief, river bed, blanket hump, today's hollow with the rock face, the curve away); strata (`STACK`, `BELOW`); the masks (`in_slice`, `in_hole`, `far`); `weights` (moods for Fable's sky, the hills, the sun) |
| `szmats.py` | `Drive` (per-frame colours and amounts); top (with rock face, haze and the light step), bones, water, words materials |
| `szgeo.py` | `Parts` (many rigid pieces in one mesh, posed with numpy), primitives, the dinosaur (one swept tube on a spine blending stand, munch and lie poses) |
| `szlife.py` | Plants on the block and the land around, trees of both eras, birds, butterflies and dragonflies, rabbit, dog, lizards, the girl, the bone in the rock face, the easter eggs, the snail |
| `szstory.py` | Set pieces of single beats: peel, babies, turtle, leaf, 3D skeleton, mammoths, saplings, the magnifier window (logic; its gold frame, handle, small ring and connector lines are in `_build_frame`, drawn in the crisp words layer through `lens.crisp`) |
| `szfossil.py` | The skeleton in the front cut face (thicker neck and tail beads, a cranium and a snout, eye socket), ink outline, seeping drops, gold sparkles, the hook's glint |
| `szback.py` | The hills behind (crest trees, volcano, herd, pterosaurs, village, train, tractor, sheep, kites, smoke, clouds) |
| `szwords.py` | Captions (Fredoka Bold, plum with a warm gold-orange under-shadow, on storybook cards), the FOSSIL! label with its gold ribbon pointer and ring round the bone, the pocket-watch clock |
| `szui.py` | The storybook graphics kit (Sam 24 Oct: "improve text, box, frame"): hand-cut rounded outlines, gold tube bands shaded from the upper left, parchment, soft warm shadows, sparkles; materials are emission fed by a colour node so Fable's word recolour (ink and paper) cannot repaint them |
| `fonts/` | `Fredoka-Bold.ttf` (SIL OFL 1.1, `OFL.txt` beside it): Google Fonts' variable Fredoka instanced at weight 700, width 100 with fontTools `instancer` (no Reserved Font Name is declared) |

Every motion is a pure function of t: every piece is set or hidden on every frame, the camera is read from this frame's
pose (`matrix_basis`, not the lagging `matrix_world`), and text sizes are measured once. Checked: frames 1330, 1020 and 814
render pixel-identical alone and after earlier frames (max difference 0).

## The graphics (Sam 24 Oct: "improve the graphical elements: text, box, frame"; the picture is untouched)
Painted storybook set in code, all in the crisp words layer over the brushwork: Fredoka Bold in deep plum with a warm
gold-orange under-shadow; parchment cards with a hand-cut edge, a toned border, a lit gold rim, a thin inner gold line,
gold sparkles and a soft warm shadow; a card pops in with a small overshoot, unfolds from slightly flat and settles from a
3 degree tilt (pure functions of t). Two-line captions are held 0.05 inside the top of the frame. FOSSIL! has a tapered gold
ribbon that draws itself (0.6 s) from under the card down to a gold ring round the bone, bowed to the right so it never crosses
the girl. The clock is a pocket watch (gold bezel and crown, cream face, plum spade hands; the hour hand turns at one twelfth).
The magnifier is a gold lens ring with a bevel and studs, a glass glint, a short plum grip, a small gold ring at the bone
and two fine gold connector lines. Words, positions, timings and the `Words` API are unchanged.

## Checks and cost
Check stills (480x270, 8 samples, Fable, this shared 2-core box; each one looked at): beat middles 60, 180, 372, 552, 660,
816, 984, 1092, 1218, 1434 and key moments 156 (peel), 588 (lying still), 636 (skeleton), 785 (ice), 823 (mammoths),
1032 (the hit), 1190 (FOSSIL! popping), 1416 (toy lifted), 1488 (last words). Full size: frame 1188 (49.5 s, the find, the
bone just out of the rock; FOSSIL! starts its pop on that frame, so it is still at zero opacity) at 1280x720, 32 samples,
opened and checked.
Measured: build 4 s; 480x270 at 8 samples 8 to 17 s a frame; 1280x720 at 32 samples 153 s (frame 1188, 158 s wall with
the build). The 1560 frames are about 66 hours on this box: a job for the Mac lane or the runners. Cost: none (CPU). No
audio in the folder yet (`film.json` has no `audio` key).
Frame independence: frames 1330, 1020, 814 (v2) and 1188 (v3) render pixel-identical alone and after earlier frames.

## Weak spots (honest)
- The slice's lowest band (rock) is a large dark teal-navy area; the bottom of the slice reads heavy.
- The roots and pebbles under the slice are small at full size and barely show on a phone; the soil trickle is a few
  grains a second.
- The land around stays at today's level in every era while the slice's top rises and falls with the story (the slice
  grows taller during the layers: its top reaches about 1.8 m, near the captions).
- The river's two ends (land and slice) line up in plan, not in height (by design: it is cut and lifted).
- The surrounding plants and trees are sparser than the slice's; the haze hides the difference only in part.
- The peel slab in the rewind is a plain block, and the land all round changes era without its own peel.
- The girl runs about 1.7 m in 1.1 s at the end of the short erosion beat (excited running, but quick).
- The face skeleton is a flat painted shape (thicker now); the magnifier's stone grey is clear only near the hit.
- The five layer floods are short, so each era shows for about 1 s ("racing" by design).
- The rewind sky blends four moods six times in 5 s: soft, but the final render still needs a photosensitivity check.
- The dinosaur's legs paint lighter than its body.
- Only stills were checked; brush shimmer and the slice's bob in motion are untested.
