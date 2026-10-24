# Fossil pilot (Little Big Questions): the picture

23 Oct 2026. A silent 60 s story (Sam 20:09: no narration; real orchestral music and real sound effects carry it; a few big
words set in code). Source of truth: `beats.json` (10 beats: picture, words, sound, music). `ad.json` voice lines are
obsolete for this film. Fable Cutaway look on the seasons grammar: one fixed view of one block, a 2 degree sway on one
sine over the whole film, no cuts. 16:9, rendered 1280x720, delivered 1920x1080, 24 fps, 1440 frames.

## Timing: one table, re-timed by beats.json
Every event of the picture is in ONE table at the top of `blender.py` (`EVENTS`: event name, beat, fraction of the way
through that beat). `szworld.set_events()` turns it into seconds (`W.B.<event>`). When the beats are re-timed to the
phrases of the chosen recording, edit `beats.json` only: the whole picture follows. Captions come from each beat's
`words` (in 0.35 s after the beat starts, out 0.25 s before it ends, never under 2.5 s); the key word (`FOSSIL!`) is the
label on the bone, timed by `label0`/`label1` in the table.

## Beats (current beats.json times)
| Beat | Time (s) | What the picture does (event times) | Words |
| --- | --- | --- | --- |
| hook | 0 to 5 | Today: sunny meadow, birds, butterflies, rabbit, village and train behind; stone skeleton in the front cut face with a glint sliding over it; the snail mascot on the front right corner leans over the edge to look at it; the red ball rolls in and stops (0.6 to 2.5) | HOW DO BONES TURN TO STONE? (0.35 to 4.75) |
| rewind | 5 to 8 | Today's plants fold (5.0 to 5.4); the ground above the old one peels away upward and fades (5.54 to 7.4); the sky runs back through days and seasons (soft blends, about 2 a second, no flashing); the clock spins backwards; the background sinks to the old era and the fern era rises (volcano, herd, pterosaurs); ferns and tree ferns grow (6.35 to 9.0); the dinosaur appears (7.1 to 8.4) | LONG AGO (5.35 to 7.85) |
| the living world | 8 to 18 | The long-neck walks to the ferns (8.0 to 10.2) and munches (10.2 to 18.1; the clump it eats shrinks); two babies splash in the river; a turtle plods along the front with the snail riding it (8.5 to 20.4); dragonflies, lizards, birds; the duck-shaped yellow flower floats down the river (the visual joke) | none |
| the old dinosaur rests | 18 to 24 | The babies grow (18.0 to 19.8) and walk off (19.5 to 23.1); the old one walks to the bank (18.3 to 20.7), lies down (20.7 to 22.3), its eyes close and it stays still (22.0 to 23.5; no breathing, never shown as sleep); evening gold (18.6 to 23.1); one leaf drifts down (21.3 to 23.9) | none |
| mud covers the bones | 24 to 30 | Rain; a gentle brown flood (24.5 to 29.7); the body fades and the skeleton remains (24.9 to 26.4); mud rises over it like a blanket with a soft hump (26.5 to 28.9); cream bones show in the new band of the cut face (28.3 to 29.7) | MUD (24.35 to 29.75) |
| layer on layer | 30 to 38 | Five layers, each brought by a short flood (rises at 30.1, 31.7, 33.3, 34.9, 36.5), each a new colour band with gold lines; on each new top an era: forest with saplings, ice, mammoths crossing a steppe, grassland, forest; the clock races; the hills behind rise | MILLIONS OF YEARS (30.35 to 37.75) |
| bone to stone | 38 to 46 | The magnifier window opens (38.2 to 38.8) above the fossil, tied to it by a small ring and two gold lines: drops fall into the pores of a big bone, each leaves a crystal sparkle, the bone turns ivory to stone grey with gold flecks from one end to the other (39.8 to 44.9, the hit); the face skeleton turns too, with blue drops seeping down the bands and a burst of gold stars on the hit; the window closes (45.6 to 46.25) | BONE TO STONE (38.35 to 45.75) |
| the land wears away | 46 to 51 | Wind and rain (46.0 to 50.1); the top wears down band by band (46.25 to 50.3); the hills shrink; today's meadow, trees, village, train, sheep, kites return (49.5 to 51.5) | none |
| the find | 51 to 56 | The girl (hat, little brush, toy dinosaur in her hand) walks in from the left meadow (49.9 to 52.1), kneels at the little rock face in a hollow (52.0 to 52.5), brushes (52.5 to 54.7); the face clears and the bone appears out of the rock (52.6 to 54.6); she jumps for joy (54.8); birds fly up from the big tree; the dog drops its stick, dashes to the bone and sits by it, wagging hard | FOSSIL! label with a leader to the bone (54.3 to 56.88) |
| the send-off | 56 to 60 | She turns to us and holds her toy dinosaur up next to the real fossil (56.2 to 57.2); the snail waves its eye stalks (57.0); the red ball rolls back into view (57.2 to 59.0); the meadow keeps living | WHAT IS UNDER YOUR FEET? (56.35 to 59.75) |

Check stills (480x270, 8 samples, Fable, this 2-core box), each looked at: beat middles at frames 60, 156, 312, 504, 648,
816, 1008, 1164, 1284, 1392 and key moments 142 (peel), 556 (lying still), 622 (skeleton), 785 (ice), 823 (mammoths),
1078 (the hit), 1330 (FOSSIL!); one full-size frame 1330 at 1280x720, 32 samples.

## Series rules (Sam 23 Oct 19:43, research 4.1; keep them in every film)
1. **Easter eggs kids know from their own lives**, several per film, some obvious, one or two hidden, animated where
   possible; only generic everyday objects, never a brand, a logo, a character or anything that looks like one. Here:
   the red ball rolling in and back (obvious), the toy car nose out of the right cut face's soil (hidden), the rubber
   duck bobbing down the brook, the kite stuck in the big tree and tugging, the teddy bear on the meadow, the toy
   dinosaur the girl holds up beside the real fossil, her dog with a stick.
2. **A living 3D background, not a flat card**: three hill layers in depth (2.6, 5.0, 7.8 m behind the block; crests
   placed by screen height so the sky keeps the top of the frame), the same era as the block, life far away (long ago: a
   smoking volcano, a herd of small long-necks, pterosaurs, tree ferns and conifers; today: a village with chimney
   smoke, a train on a viaduct, a red tractor, sheep, kites, round trees and poplars), drifting clouds, colours and
   light following the story; pieces rise out of or sink into their hills, staggered, when time passes. Fable's painted
   card remains only as the far sky.
3. **The mascot**: a small silent snail (coral and gold shell) in the corner of every block, who reacts and never
   speaks: peeks at the fossil, rides a turtle long ago, hides in its shell in the rewind, floods and rain, stretches up
   at the cheer, waves at the end.
4. **One small visual joke per film**, never sarcasm: here the duck-shaped flower floating in the dinosaur's river, and
   the dog sitting by the fossil as if it were its bone.
5. Silent films: the picture explains everything; words are few, big, in with a soft pop, at least 2.5 s on screen.

## Files and jobs
| File | Job |
| --- | --- |
| `blender.py` | The event table (`EVENTS`), build and frame; camera (az -62, el 21, 50 mm, 2 degree sway), sun per mood, ground colour per era, water (river ribbon and flood box), rain |
| `szworld.py` | Heights in time (`base`, `top_h`: relief, river bed, blanket hump, today's hollow with the rock face), strata (`STACK`, `BELOW`), `weights` (moods for Fable's sky, the hills, the sun), `set_events`, layer slots, word windows |
| `szmats.py` | `Drive` (per-frame colours and amounts), top, bones, water, words materials |
| `szgeo.py` | `Parts` (many rigid pieces in one mesh, posed with numpy), primitives, the dinosaur (one swept tube on a spine blending stand, munch and lie poses) |
| `szlife.py` | Plants (ferns, grass, flowers, layer sprouts), block trees, birds, butterflies and dragonflies, rabbit, dog, lizards, the girl, the bone in the rock face, the easter eggs, the snail |
| `szstory.py` | Set pieces of single beats: peel, babies, turtle, leaf, 3D skeleton, mammoths, saplings, the magnifier window |
| `szfossil.py` | The skeleton in the front cut face: bones, ink outline, seeping drops, gold sparkles, the hook's glint |
| `szback.py` | The world behind (hills, crest trees, volcano, herd, pterosaurs, village, train, tractor, sheep, kites, smoke, clouds) |
| `szwords.py` | Captions, the FOSSIL! label and leader, the clock |

Every motion is a pure function of t: every piece is set or hidden on every frame, the camera is read from this frame's
pose (`matrix_basis`, not the lagging `matrix_world`), text sizes are measured once. Checked: frames 1330 and 1020 render
pixel-identical alone and after earlier frames (max difference 0).

## Render
Local check: `python3 harness/blender_render.py films/cutaway/kids/fossil --w 480 --h 270 --samples 8 --start N --end N+1`.
Full size (coordinator, Mac lane): `film.json` render 1280x720, 32 samples, delivery 1920x1080, 60 s, 1440 frames.
Measured on this shared 2-core box: build 2 to 3 s; 480x270 at 8 samples 6.4 to 8.2 s a frame (Fable compositing
included); 960x540 at 8 samples 26.6 s; 1280x720 at 32 samples 96.8 s (frame 1330, 100 s wall with the build).
The full film at that rate is about 39 hours on this box, so it belongs on the Mac or the runners. Cost: none (CPU).
No audio yet (music and sound effects are the next stage; `film.json` has no `audio` key).

## Weak spots (honest)
- The face skeleton is a flat painted shape: the neck and tail beads are thin, the skull reads as a rounded disc; fine at
  full size, small on a phone.
- The flood and layer water is a flat painted sheet; the five layer floods are short (about a third of each 1.6 s slot),
  so each era shows for about 1 s: "racing" by design, but fast.
- The mammoths take long steps over a short distance while their era lasts; the saplings pop up (scale) rather than grow.
- The peel slab in the rewind is a plain block (green top, banded sides): it reads as the ground lifting away but does
  not carry the grass and trees with it (they fold away just before).
- The babies walk off and fade at the back edge (the herd is only in the background).
- The girl, dog and rabbit are at storybook scale (girl about 54 cm on a 3.6 m block) so they read; the dog and rabbit
  are still small on a phone. The girl has no face detail (as asked); seen at the send-off her front is plain.
- The magnifier window's rock is pale and its bone colour change is gentle; the stone grey is clear only from about
  frame 1060 on.
- The sky's rewind blends four moods six times in 3 s; soft, but a photosensitivity check of the final render is
  still to do.
- The dinosaur's legs paint lighter than its body (the belly colour catches their undersides).
- Only stills were checked; no moving check yet (Kuwahara brush shimmer in motion, Fable's known weak spot, is untested).
- `beats.json` sound and music columns are not used by the picture yet beyond the timing; the music hit is the `hit`
  event (bone to stone, u 0.86), to be moved onto the recording's real hit when the music is chosen.
