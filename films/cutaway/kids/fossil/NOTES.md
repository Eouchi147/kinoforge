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
| hook | 0 to 5 | Today: the dig section in a sunny meadow that carries on all round (path, brook, trees, a village with chimney smoke, a train, sheep, kites); the stone skeleton in the front cut face, a glint sliding over it; the snail mascot on the front right corner leans over to look; the red ball rolls in (0.6 to 2.5) | HOW DO BONES TURN TO STONE? (0.35 to 4.75) |
| rewind | 5 to 10 | Today's plants fold (5.0 to 5.6); the ground above the old one peels away upward and fades (5.75 to 8.75); the sky runs back through days and seasons (soft blends, no flashing); the clock spins backwards; the land all round turns into the fern era; ferns grow (7.25 to 10.9); the dinosaur appears (8.5 to 10.3) | LONG AGO (5.35 to 9.75) |
| the living world | 10 to 21 | The long-neck walks to the ferns (10.0 to 12.2) and munches (12.2 to 19.5; the clump shrinks); two babies splash in the river; a turtle plods along the front with the snail riding it; dragonflies, lizards, birds; the duck-shaped yellow flower floats down the river (the visual joke); a volcano smokes far off, a herd walks the hills, pterosaurs circle | none |
| the old dinosaur rests | 21 to 25 | The babies grow (18.8 to 21.6) and walk off (21.2 to 24.6); the old one walks to the bank (19.5 to 22.4), lies down (22.4 to 23.6), its eyes close and it stays still (23.4 to 24.7; no breathing, never shown as sleep); evening gold (19.9 to 24.4); one leaf drifts down (23.0 to 24.9) | none |
| mud covers the bones | 25 to 30 | Rain; a gentle brown flood over the whole plain (25.4 to 29.75); the body fades and the skeleton remains (25.75 to 27.0); mud rises over it like a blanket with a soft hump (27.1 to 29.1); cream bones show in the new band of the cut face (28.6 to 29.75) | MUD (25.35 to 29.75) |
| layer on layer | 30 to 38 | Five layers, each brought by a short flood (rises at 30.1, 31.7, 33.3, 34.9, 36.5), each a new colour band with gold lines; the whole land rises with them; on each new top an era, on the block and all round: forest with saplings, ice, mammoths crossing a steppe, grassland, forest; the clock races; the hills behind rise | MILLIONS OF YEARS (30.35 to 37.75) |
| bone to stone | 38 to 44 | The magnifier window opens (38.1 to 38.6) above the fossil, tied to it by a small ring and two gold lines: drops fall into the pores of a big bone, each leaves a crystal sparkle, the bone turns ivory to stone grey with gold flecks from one end to the other (39.2 to 43.0); the face skeleton turns too, with blue drops seeping down the bands and a burst of gold stars on the hit (43.0); the window closes (43.7 to 44.4) | BONE TO STONE (38.35 to 43.75) |
| the land wears away | 44 to 47 | Wind and rain (44.0 to 46.6); the top and the land all round wear down band by band (44.1 to 46.4); the hills shrink; today's meadow, trees, village, train, sheep, kites return (45.65 to 47.4) | none |
| the find | 47 to 54.5 | The girl (hat, little brush, toy dinosaur in her hand) runs in from the meadow beside the dig (45.7 to 46.9), kneels at the little rock face in a hollow, brushes (47.0 to 49.4); the bone appears out of the rock on the climax (49.5); she jumps for joy (49.6 to 51.65); birds fly up from the big tree; the dog drops its stick, dashes to the bone and sits by it, wagging hard | FOSSIL! label up and to the right of the bone, its leader clear of the girl (49.5 to 52.25) |
| the send-off | 54.5 to 65 | The red ball rolls back into view (55.3 to 57.4); she turns to us and lifts her toy dinosaur up next to the real fossil on the final swell (57.0 to 60.0); the snail waves its eye stalks (60.8); the meadow keeps living | WHAT IS UNDER YOUR FEET? (60.0 to 64.75) |

## The world around the block (coordinator, 23 Oct: no flat empty ground)
The block is a dig section cut out of a continuous land. One terrain (`fs_world`, 24 x 23 m) carries on all round at the
same heights (`szworld.top_h`) in the same ground paint (`sz_top`), so it follows every era: today's meadow, the fern
forest and river, the mud, the ice, the steppe, the grassland, the rain-worn rock. The river crosses it (it comes from far
behind on the left, loops past the front of the block where the dinosaur rests, and leaves through the back); floods
spread over the whole plain (`fs_floodworld`). Ferns, grass, flowers, layer sprouts and trees of both eras grow on it
(sparser with distance), sway in the kit's wind, and fold or grow with time like the block's own.
- A narrow viewing trench in front of the -Y face (1.3 m) and beside the +X face (0.6 m) is cut away so both faces stay
  in view. Its two visible walls (`add_trench_walls`) are part of the block's walls mesh, so Fable paints them in the same
  strata with gold lines. Its earthen floor sits at -0.8 m and is mostly hidden by the land beyond.
- The land in front of the trench stays at the old ground's level (`szworld.near`, eased over 0.7 m). It sits at the
  bottom edge of the frame, so its level never reads, and it never hides the fossil band however high the layers stack.
- Beyond the block's far corner the land curves gently down (`szworld.drop`, radius 6 m). This gives a storybook horizon,
  so the hills, their life and the sky stay in view. The camera aim is 0.5 m above the kit's fit, so the block sits low.
- The block stays the hero: a small step of light just outside it, then haze with distance (attribute `far`, colour
  `haze` per mood). Its two cut faces are the only full cross-sections.

## Series rules (Sam 23 Oct 19:43 and 20:09, research 4.1; keep them in every film)
1. **Easter eggs kids know from their own lives**, several per film, some obvious, one or two hidden, animated where
   possible; only generic everyday objects, never a brand, a logo, a character or anything that looks like one. Here:
   the red ball rolling in and back (obvious), the toy car nose out of the right cut face's soil (hidden), the rubber
   duck bobbing down the brook, the kite stuck in the big tree and tugging, the teddy bear on the meadow, the toy
   dinosaur the girl lifts beside the real fossil, her dog with a stick.
2. **A living world, not a flat card**: the land the block was cut from carries on all round at the same level, then
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
| `blender.py` | The event table (`EVENTS`), build and frame; camera (az -62, el 21, 50 mm, 2 degree sway); sun per mood; ground colour per era; the land around (`build_world`), the trench walls; water (river ribbon, flood box over the block, flood sheet over the land); rain |
| `szworld.py` | `beats.json`, `set_events`, layer slots, word windows; heights in time (`base`, `top_h`: relief, river bed, blanket hump, today's hollow with the rock face, the near land, the curve away); strata (`STACK`, `BELOW`); the world masks (`in_block`, `in_trench`, `far`); `weights` (moods for Fable's sky, the hills, the sun) |
| `szmats.py` | `Drive` (per-frame colours and amounts); top (with rock face, haze and the light step), bones, water, words materials |
| `szgeo.py` | `Parts` (many rigid pieces in one mesh, posed with numpy), primitives, the dinosaur (one swept tube on a spine blending stand, munch and lie poses) |
| `szlife.py` | Plants on the block and the land around, trees of both eras, birds, butterflies and dragonflies, rabbit, dog, lizards, the girl, the bone in the rock face, the easter eggs, the snail |
| `szstory.py` | Set pieces of single beats: peel, babies, turtle, leaf, 3D skeleton, mammoths, saplings, the magnifier window |
| `szfossil.py` | The skeleton in the front cut face (thicker neck and tail beads, a cranium and a snout, eye socket), ink outline, seeping drops, gold sparkles, the hook's glint |
| `szback.py` | The hills behind (crest trees, volcano, herd, pterosaurs, village, train, tractor, sheep, kites, smoke, clouds) |
| `szwords.py` | Captions, the FOSSIL! label and leader, the clock |

Every motion is a pure function of t: every piece is set or hidden on every frame, the camera is read from this frame's
pose (`matrix_basis`, not the lagging `matrix_world`), and text sizes are measured once. Checked: frames 1330, 1020 and 814
render pixel-identical alone and after earlier frames (max difference 0).

## Checks and cost
Check stills (480x270, 8 samples, Fable, this shared 2-core box; each one looked at): beat middles 60, 180, 372, 552, 660,
816, 984, 1092, 1218, 1434 and key moments 156 (peel), 588 (lying still), 636 (skeleton), 785 (ice), 823 (mammoths),
1032 (the hit), 1190 (bone and FOSSIL! on the climax), 1416 (toy lifted), 1488 (last words). Full size checked on frame
1330 (1280x720, 32 samples), before the Grieg re-timing; the geometry is the same.
Measured: build 3 to 4 s; 480x270 at 8 samples 7 to 12 s a frame (the land around costs about 3 s); 1280x720 at 32
samples 146 s (frame 1330, 151 s wall with the build), up from 97 s without the land around. The 1560 frames are about 63
hours on this box: a job for the Mac lane or the runners. Cost: none (CPU). No audio in the folder yet (`film.json` has
no `audio` key).

## Weak spots (honest)
- The world is a dig in a landscape now: the block reads by its cut faces, the trench and the light step, not as a free
  block on a floor. Sam has not seen this framing yet.
- The land in front of the dig stays at the old ground's level in every era (a cheat; it sits at the frame's bottom edge).
- The land beyond the block's far corner curves down (a little-world horizon); the strip of visible land behind is narrow.
- The surrounding plants and trees are far sparser than the block's; the haze hides the difference only in part.
- The peel slab in the rewind is a plain block, and the land all round changes era without its own peel.
- The girl has to run in during a short beat (2.6 m in about 1.1 s): reads as excited running, but quick.
- The face skeleton is a flat painted shape (thicker now); the magnifier's stone grey is clear only near the hit.
- The five layer floods are short, so each era shows for about 1 s ("racing" by design).
- The rewind sky blends four moods six times in 5 s: soft, but the final render still needs a photosensitivity check.
- The dinosaur's legs paint lighter than its body.
- Only stills were checked; brush shimmer in motion (Fable's known weak spot) is untested.
