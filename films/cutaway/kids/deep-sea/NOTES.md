# Deep sea (Little Big Questions): the picture

24 Oct 2026. A silent 70.5 s story for ages 6 to 8: no narration; real orchestral music and real sound effects carry it;
a few big words set in code. Question: WHAT LIVES IN THE DEEP SEA? Choreographed to Mendelssohn, The Hebrides (Fingal's
Cave) Overture, Musopen Symphony (public domain on Commons; the research lists CC BY 3.0 on IMSLP, credited either way).
Source of truth: `beats.json` (11 beats: picture, words, sound, music, the music edit and its credit). Facts and cautions:
`docs/research/KIDS_FACTS_2026-10.md` section 2.3 (zones by NOAA depths, sunlight fades with depth, many animals the
cameras see make their own light, only SOME anglerfish have a lure and its glow comes from bacteria, vents found in 1977
with life around them, very little of the deep seafloor has been seen; never "5% explored"; the word "bioluminescence"
is not used). Fable Cutaway look on the lifted slice: one fixed view, a 2 degree sway, no cuts. 16:9, rendered
1280x720, delivered 1920x1080, 24 fps, 1692 frames.

## The picture
One tall slice of ocean (2.4 x 1.3 m, 2.9 m of water over a real Cutaway block of seafloor strata) floats 0.34 m above
the hole it was lifted from, bobbing 2.5 cm on a 7.5 s sine. It is open on its two near faces (front and right); the back
and left walls and the sea surface on top are painted water: sunny turquoise at the top (with slanted sun shafts), dusk
violet in the twilight zone, deep blue in the midnight zone, gold hairlines at the zone changes (200 m and 1,000 m in
the story; the slice is a model, not to scale). The sea round it carries on to the horizon (a far card held by the
camera hides the edge of Fable's painted sky card): an island with a palm, a bucket and a sandcastle, a sailboat sailing
home, a beach ball, gulls, a friendly whale with its far spout, a drifting sky.
The thread is a little round generic submarine (red, with a porthole and a snail in it, a headlamp and a propeller).

## Timing: one table, re-timed by beats.json
`szworld.py` reads `beats.json`. Every event of the picture is in ONE table at the top of `blender.py` (`EVENTS`:
event, beat, seconds into that beat); `szworld.set_events()` turns it into seconds (`W.B.<event>`). The audio script reads
the same table, so a re-timed picture re-times the sound.

| Beat | Time (s) | Picture (event times) | Words | Music |
| --- | --- | --- | --- | --- |
| hook | 0 to 5.5 | Sunny sea, island, boat, gulls; the whale blows (1.2); the duck hops twice (2.6, 3.1); the submarine waits on the top with the snail in its porthole | WHAT LIVES IN THE DEEP SEA? | the rolling wave motif, low strings |
| sunlight zone | 5.5 to 13.5 | The submarine tips in and dives (5.6) with a ring of bubbles; yellow fish and a turtle | SUNLIGHT ZONE | the wave motif rises and falls |
| twilight zone | 13.5 to 20.5 | Sun shafts run out; lantern fish and a pale jellyfish switch on at the swell (16.9 to 17.3) | TWILIGHT ZONE | the first swell (17.0) |
| midnight zone | 20.5 to 26.5 | Darkness; the headlamp clicks on (21.0); marine snow; one slow bubble | MIDNIGHT ZONE | a hush, the splice lands in it |
| they glow | 26.5 to 33.5 | Jellyfish light up one after another (26.7, 28.3, 30.0), sparkles; a far spout (27.9) | GLOW! (the label on the first jelly) | the warm cello theme begins (26.6) |
| glowing squid | 33.5 to 40.0 | Spotted squid zips past (33.7 to 39.7); a message in a bottle drifts by (33.5 to 40.5); the snail waves (35.7, 37.9) | none | the theme goes on |
| the lantern | 40.0 to 47.0 | A friendly anglerfish slides in (40.0); the headlamp blinks off (41.3); the lure lights up and the sub glows like in a torch beam (42.4 to 45.8); the lamp clicks on (45.7) | none | the theme answers itself |
| hot vents | 47.0 to 55.5 | The sub settles by a hot vent; red tube worms sway round it; a toy boat, a lost sandal and a treasure chest (sparkle 52.2) | HOT VENTS | the build to the tutti |
| all the lights | 55.5 to 59.5 | At 55.0 every light in the slice twinkles on at once | none | the climax (55.0) |
| only a tiny piece | 59.5 to 64.5 | The lights go out one by one; the torch shows a small round patch of a wide dark seafloor; the sub rises (59.4 on) | MOST IS UNSEEN | cross-fade into the closing section; the first chord (63.0) |
| back to the surface | 64.5 to 70.5 | The sub pops out of the sea (65.9) at golden sunset; the snail waves (67.1, 70.3); the duck squeaks; gull; the whale blows (69.0) | WHAT ELSE IS DOWN THERE? (from 66.0) | the final chord (65.8) and the hush |

## Easter eggs and the joke
Obvious: the rubber duck on the top of the slice (it hops at 2.6, 3.1 and again on the return), a beach ball, a message in
a bottle, a toy sailboat on the seafloor, a lost sandal, a treasure chest toy (sparkles once), a sandcastle and a bucket
on the island. Hidden: the SNAIL mascot waves from the submarine's porthole window (35.7, 37.9, 43.6, 45.4, 67.1, 70.3).
Visual joke: the anglerfish's lure lights the submarine up like a torch (the headlamp blinks off, the lure's glow warms the
hull, the snail waves up at it). Only some anglerfish have a lure; this is one friendly fish.

## Files and jobs
| File | Job |
| --- | --- |
| `blender.py` | The event table, build and frame; camera (az -62, el 13, 50 mm, 2 degree sway); the sun; the GLOW! label pointed at jelly 0 |
| `szworld.py` | `beats.json`, `set_events`, word windows, the slice's measures and bob, the submarine's path, `weights` (day to golden evening for Fable's sky card) |
| `szmats.py` | `Drive`; the sea shader (depth ramp, fog, driven lamps for the headlamp, the lure and the vent), glow materials, wall, surface, haze, sun rays, far card |
| `szsea.py` | The seafloor block (Cutaway strata), the walls, surface and gold rails, sun shafts, the hole, the sea sheet, the far card |
| `szlife.py` | The submarine (and snail), fish, turtle, duck, lantern fish, big-eyed fish, jellyfish, squid, anglerfish, the vent, worms and toys, marine snow, bubbles, ripples and splashes, sparkles, the bottle, the island, boat, ball, gulls and whale |
| `szgeo.py` | `Parts` (many rigid pieces in one mesh posed with numpy) and primitives |
| `szwords.py`, `szui.py`, `fonts/` | The storybook captions and label (the coordinator's upgraded graphics, same API as the fossil film) |
| `audio/make_audio.py` | The soundtrack (see `SOUND.md`); `audio/mix.m4a` is committed with `git add -f` for the runners |

## Checks and cost
Looked at (this shared box, small size, Fable): t = 1.2, 2.2, 8, 18, 22 (640x360 to 960x540) and 36, 43 (1280x720). Real
full-size stills: see the run ids in `docs/LOG.md`. Cost: US$0 (CPU, free runners).
Frame independence: see the line in the report of the film (a frame rendered alone and after another).

## Weak spots (honest)
- The deep creatures are lit by an ambient floor (they glow brighter than a real deep sea would show them) so a child can see them.
- The whale is a simple painted shape far away; its spout is a fan of drops.
- The slice's lower strata read dark navy; the column is about a third of the picture width (the world around is the point).
- The anglerfish lure's light on the submarine is a painted warm tint, not real light transport.
- The limiter takes about 5.6 dB off the first closing chord (63.0 s) because the music jumps 20 dB in 0.1 s there.
- Only stills were checked; the motion of the dive, the bob and the brush shimmer are untested in video.
