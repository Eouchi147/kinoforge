# What is a shooting star? (Little Big Questions, film 5)

A silent story for children aged 6 to 8, 68.4 s, 24 fps, 1280x720 render (1920x1080 mastered). No narration: the picture
explains everything, a few big words are set in code. Cutaway kit, Fable look (`art/fable.py` through `art/_adapter.py`), one
fixed view of one lifted slice with a 2 degree sway, no cuts.

## The facts (binding: `docs/research/KIDS_FACTS_2026-10.md` section 2.4)
A tiny bit of space rock or dust, usually no bigger than a pebble (a meteoroid), rushes into the air so fast that it glows hot and
makes a streak of light, and burns up high above the clouds. It is NOT a star. Tiny space dust falls every day. No dinosaur impact in
this film. The "make a wish" idea is folklore and is only the joke at the end (nobody says it works).

## Beats (beats.json is the source; times in film seconds)
| Beat | Time | Picture | Words | Music (recording time) |
| --- | --- | --- | --- | --- |
| hook | 0 to 4.91 | Dusk on a hilltop slice: a family camps (tent, fire, telescope), the snail looks up through its tiny telescope, first stars wink on, dad toasts a marshmallow | WHAT IS A SHOOTING STAR? | introduction, light strings and triangle (0:00 to 0:03.6) |
| look | 4.91 to 8.82 | A small streak zips across on the bar line (7.52); everyone looks up and points, the owl turns its head | none | the theme enters (5.18) |
| notstar | 8.82 to 12.74 | A magnifier window opens on one bright star, a ring and two gold lines tie it to the sky | NOT A STAR | the theme (10.40 to 14.32) |
| far | 12.74 to 17.97 | The star is a giant calm ball of fire, far away; the window closes; the girl picks up a pebble and holds it to the sky | none | the theme (14.32 to 19.55) |
| rock | 17.97 to 21.88 | The window opens on a small brown rock tumbling in space, a matching pebble glints beside it | A TINY SPACE ROCK | the theme gathers (19.55 to 23.46) |
| drift | 21.88 to 27.16 | The rock drifts closer; accents on the bar lines 21.88, 23.19, 24.50; the window turns to the layers of the air | none | accents, then a one-bar cross-fade into the plucked build (88.84) |
| air | 27.16 to 40.23 | The rock enters the layers of the air and glows orange, yellow, white; a ring in the sky marks the place | none | quiet plucked strings that build bar by bar (88.84 to 101.91) |
| streak | 40.23 to 44.14 | The rock rushes in: the long streak crosses the sky on the full orchestra, the big reveal lands on the loud hit (41.9) | METEOR! (at 41.9) | the full orchestra (101.91 to 105.82, the hit at 103.58) |
| gone | 44.14 to 49.37 | The trail fades, sparkles drift down and melt, the window closes, specks of dust glint (tiny dust falls every day) | none | the glow of the last tutti bars |
| wish | 49.37 to 57.2 | Everyone closes their eyes and makes a wish; the snail's wish, a lettuce leaf, floats in, lands, and the snail munches it (the joke) | none | the lilting second theme (111.05 to 118.88) |
| send | 57.2 to 68.4 | They cuddle; the dance's last bright chord (59.55); a breath of stillness (61.88 to 63.57) with crickets; one last small streak (66.6) | WILL YOU SEE ONE TONIGHT? (from 61.88) | the dance's own ending (228.41 chord, hush, plucked coda) |

Each word is on screen at least 2.5 s (`szworld.word_windows`).

## The one events table
`szevents.py` holds every timed event, anchored to a beat ("beat name + seconds after the beat starts"). `blender.py` hands it to
`szworld.set_events` (`W.B.<event>` in seconds); `audio/make_audio.py` imports the same module (no bpy needed). Re-time `beats.json`
and the picture and the sound both follow. The music-to-film mapping (bar lines) is in the module docstring.

## Music
Grieg, Anitra's Dance (Peer Gynt Suite No. 1), Musopen Symphony, public domain (Wikimedia Commons), asset
`grieg-anitra-musopen.flac` in release `music` of `Eouchi147/rc-render` (with its licence json). Four pieces cut on the bar lines (one bar
1.3065 s), joined by triangular cross-fades: recording 0:00 to 0:03.6 | 5.18 to 30.05 | 1:28.84 to 2:00.19 | 3:46.06 to the end. The streak
and METEOR! land on the loud hit of the full-orchestra peak (film 41.9); the last bright chord is film 59.55.
Credit line for the video description: "Music: Edvard Grieg, Anitra's Dance (Peer Gynt Suite No. 1), performed by the Musopen Symphony (musopen.org), public domain."

## Sound
Real CC0 recordings (the studio bank, BigSoundBank) on every event: the campfire all film, crickets as the night comes, owl, chimes and
a triangle tuned to the music for the star and window, a whoosh, chimes, a glockenspiel and a bowl on the streak, pebble ticks, the lettuce
crunch. See `SOUND.md` (every recording, where it is used, stand-ins, the measurements) and `audio/mix.json`. `audio/mix.m4a` is committed.
Nobody has listened to it yet.

## Easter eggs (generic, no brands, no characters)
A teddy bear by the tent (hug-sized, with a red bow); marshmallows on a stick that dad holds to the fire (they brown); a flashlight with
its beam on the grass; a paper star hanging from the tent's pole (it swings); the little brother's toy rocket (he raises it to the streak); a
sleeping cat curled on a blanket (it breathes); the girl's pebble; fireflies; the owl in the tree (its head follows the streak, it blinks, its
eyes go wide); the village with warm windows, a church clock, a windmill and chimney smoke far away; a lake with the stars on it; the Moon.
The series mascot: **the snail** sits at the front right corner with a tiny telescope and follows the streak.
**The visual joke:** at the wish everyone shuts their eyes and wishes (wish stars lift from their heads); the snail's wish is a lettuce
leaf that floats in, rocking, lands in front of it, and it munches it.

## Files
`beats.json` (beats, words, rules, music) | `szevents.py` (events) | `blender.py` (scene contract, light, camera) | `szworld.py` (land, moods, clock) |
`szmats.py` (driven materials) | `szgeo.py` (rigid parts) | `szlife.py` (camp, family, animals, easter eggs, snail) | `szstory.py` (night sky, Moon,
stars, streaks, the magnifier window) | `szback.py` (hills, village, clouds) | `szwords.py`, `szui.py`, `fonts/` (the storybook captions, from the fossil film) |
`audio/make_audio.py` (sound) | `film.json`.

## Rules kept
No narration; words set in code only; no emoji or cartoon icons; no brands; no dash or three-dot punctuation in any text; nothing scary (the
meteor is a gentle glow and sparkles, no flash, no sound over the music); AI-made, disclosed by the series.

## Changes after the first push (23 Oct night)
- The paper star now hangs on the tent's guy rope and glows (it was hidden behind dad), the flashlight is bigger, the reveal's flare is brighter and wider (US$0).

## Open
Needs Sam's eyes and ears before it is published (looks and levels were set by measurement and stills). See the builder's report for weak spots.
