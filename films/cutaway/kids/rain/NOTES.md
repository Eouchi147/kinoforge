# Rain (Little Big Questions, film 3): the picture

23 to 24 Oct 2026. A silent 73 s story for ages 6 to 8: WHERE DOES RAIN COME FROM? No narration; a real orchestral recording
(Smetana, Vltava, The Moldau; Musopen Symphony, public domain) and real recorded sound effects carry it; a few big words
set in code. Built on the fossil pilot's kit (same Fable Cutaway look, same lifted slice, same camera: one fixed view, a
2 degree sway, no cuts). 16:9, rendered 1280x720, delivered 1920x1080, 24 fps, 1752 frames. Source of truth: `beats.json`
(10 beats: picture, words, sound, music). Facts: `docs/research/KIDS_FACTS_2026-10.md` 2.2 (sun warms water, it rises as
invisible vapour, cools into tiny droplets that make a cloud, about a million droplets join into one raindrop, it falls,
soaks in, runs to streams, rivers and the sea, and around again). The dinosaur-water claim is not used.

## The slice and the world
The slice is a hillside with a brook, a little lake, soil and a water table: its cut faces show the soil darkening blue
from the top down while rain soaks in, and the sandy layer's blue band rising. All round: meadow with flowers and trees,
hills in three layers, a village with chimney smoke, a river winding to a sea at the horizon, drifting clouds, kites.
Weather is part of the picture: sunny, then a soft grey cloud and rain, then sun and a rainbow. No thunder, nothing scary.

## Timing: one table, re-timed by beats.json
`szworld.py` reads `beats.json`; every event of the picture is in ONE table at the top of `blender.py` (`EVENTS`: event,
beat, fraction of the way through that beat); `szworld.set_events()` turns it into seconds (`W.B.<event>`). Some entries
are dummies kept so `szwords.py` (the coordinator's drop-in caption code, API unchanged) finds the events it reads
(rw0, rw1, stack0, stack1, rain0, erode1, label0, label1, hold0, hold1).

## Beats
| Beat | Time (s) | Picture | Words | Music |
| --- | --- | --- | --- | --- |
| hook | 0 to 6.5 | Sunny slice, brook into a lake, village, river to the sea; the snail looks up | WHERE DOES RAIN COME FROM? | first flute line alone (recording 0:00) |
| the sun warms | 6.5 to 12.5 | The sun climbs; lake and sea glitter; the air shimmers | none | the second flute joins (two springs) |
| invisible water | 12.5 to 19.0 | Pale wavy vapour ribbons rise from the lake and the sea, thinner as they climb | INVISIBLE WATER | rippling lines climb; edit joint at 16.2 |
| tiny drops | 19.0 to 25.5 | The ribbon tips become tiny white dots that gather above the slice; a cloud grows | TINY DROPS | springs swell together |
| a million | 25.5 to 33.86 | A magnifier opens on the cloud: tiny drops bump and join, pairs join again, one fat drop falls out; the cloud turns grey | ABOUT A MILLION | swell to the river theme; entry at 33.86 |
| first drops | 33.86 to 40.5 | First raindrops; a child in a yellow raincoat runs in and the umbrella pops open; the snail wiggles | none | river theme enters |
| soaking in | 40.5 to 48.8 | Rain soaks into the hill; drops sink to the sand; water table rises; brook swells; paper boat; puddle splashes | none | first statement of the theme |
| the sun again | 48.8 to 57.0 | Cloud thins, sun breaks out, rainbow draws itself | none | joint at 48.8: the broad theme in major |
| around and around | 57.0 to 64.4 | River to the sea; new shimmer rises; a small new cloud begins | AROUND AND AROUND | the great chord at 60.3 |
| your rain | 64.4 to 73.0 | Rainbow glows, snail waves, child jumps in the puddle | WHERE HAS YOUR RAIN BEEN? | the piece's own two final chords at 68.0 and 70.0 |

## Easter eggs and the joke
Obvious: the child in a yellow raincoat and red boots, the yellow umbrella, the puddle splash, the paper boat, a rubber
duck on the lake, a watering can that fills, a kite. Hidden: a lost red ball and a toy car in the soil. The mascot snail sits
on the front corner and LOVES the rain (the visual joke: it stretches up, rocks its shell and wiggles its eyes while
everyone else runs for cover) and waves at the end.

## Files and jobs
| File | Job |
| --- | --- |
| `blender.py` | The event table, build and frame; camera (2 degree sway); sun and sky by mood; ground colour by weather; the brook ribbon and the rain streaks; the magnifier and words attached |
| `szworld.py` | `beats.json`, `set_events`, word windows; heights in time (relief, brook and lake cut, lift and bob), weather curves (`sunny`, `rain_k`), lake level |
| `szmats.py` | `Drive` (per-frame colours and amounts); top, water, soil water (emission over the strata), vapour, rainbow, words materials |
| `szgeo.py` | `Parts` (many rigid pieces in one mesh), primitives |
| `szlife.py` | Plants, trees, birds, butterflies, rabbit, the child with umbrella, eggs, the snail |
| `szstory.py` | Cloud, vapour ribbons, soil overlay with sinking drops, lake, ripples, puddle splashes, paper boat, the magnifier (`Lens`, gold frame) and its droplet merge tree |
| `szback.py` | Hills, village, sea, glitter, rainbow, kites, sky clouds |
| `szwords.py`, `szui.py`, `fonts/` | Captions and the storybook frames (the fossil's, unchanged; Fredoka Bold, SIL OFL) |
| `audio/make_audio.py` | The music edit, level rider and the sound design; writes `mix.m4a`, `mix.json`, `SOUND.md` |

## Checks and cost
Time purity: frame 960 rendered alone and after frames 957 to 959 is pixel-identical (max difference 0). Local contact
frames at 640x360, 4 samples, each looked at: 72, 360, 528, 720, 960, 1104, 1272, 1344, 1488, 1704. Real 1280x720 stills run on
GitHub (`stills.yml`) after the push; see the report. Cost: none (CPU, free runners). Audio: -16.1 LUFS, true peak
-2.0 dBTP, 73.0 s (`SOUND.md`).

## Weak spots (honest)
- Nobody has watched the film in motion or listened to the sound; everything was checked from stills and measurements.
- The closing card sits in front of the rainbow's arch; only the two sides of the arch show at the end.
- The slice is small in the frame (the fossil's framing, widened for sky room); the cloud and rain read best at full size.
- Rain streaks are thin and faint at phone size; the soaking-in beat depends on the cut face's blue, which reads well.
- The cut-face water and vapour are emission overlays (painted, not simulated).
- The drop-merge sounds are soft bubbles and a boing: the bank has no cloud droplets (see the stand-ins in `SOUND.md`).
- 36 of 109 sound spots sit quietly under the river or rain bed (listed in `mix.json`).
