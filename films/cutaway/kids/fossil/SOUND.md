# Sound of the fossil film (Little Big Questions, film 1)

A SILENT 65 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
Audio never goes into git: `audio/mix.m4a` and `audio/mix.wav` are ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** Music: Edvard Grieg, Morning Mood, performed by the Musopen Symphony (musopen.org), public domain.

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- 65.00 s, 48 kHz stereo AAC 256k, -16.0 LUFS integrated (target -16), true peak -1.60 dBTP (limit -1.5 dBTP), loudness range 6.5 LU.
- The loudest limiter dip is 2.6 dB at 50.3 s (the sunrise climax); the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; the loudest instant of a footfall, bite or splash sits 10 to 35 ms after the event
  frame, a brush stroke on its turn). On the rendered effects bus alone, 97 of 147 percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under the river, rain or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
Grieg, Peer Gynt Suite No. 1, I. Morning Mood, Musopen Symphony (Musopen), Public domain (Wikimedia Commons record). Source: https://commons.wikimedia.org/wiki/File:Grieg_-_Peer_Gynt_Suite_No._1,_Op._46_-_I._Morning_Mood_(Musopen_Symphony).flac. Asset: Eouchi147/rc-render release music: grieg-morning-mood-musopen.flac (+ .licence.json).
Recording 0:00 to 0:54.5, a triangular (linear in, linear out) cross-fade of 1.5 s (film 53.0 to 54.5) into recording
3:37.0 to 3:49.0; 65.0 s. The music leads. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio 2.3,
gain between -4.7 and +7.0 dB) lifts the whispering opening and eases the sunrise climax so the film can sit near
-16 LUFS; the notes keep their own shape. The music is lowered by at most 1.5 dB under the brush strokes, the FOSSIL! sparkle and the stone hit.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). The bank was extended for this film with 64 more BigSoundBank ids from
`docs/research/KIDS_MUSIC_2026-10.md` section 5.1 (soft boings, chimes, bowls, soft steps, crunches, brushes, splashes):
rc-render sfx-bank.yml run 40049538821 (24 Oct 2026). Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowl, chimes, glock, toy squeak, boings) are tuned by resampling to the
pitch classes the orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
| `apple_crunch_1` | chew (3x, 13.7 to 18.5 s); munching the ferns (15.5 s) | https://bigsoundbank.com/s1113.html | CC0 (BigSoundBank / Joseph Sardin) |
| `apple_crunch_2` | chew (3x, 14.1 to 18.9 s); munching the ferns (17.7 s) | https://bigsoundbank.com/s1114.html | CC0 (BigSoundBank / Joseph Sardin) |
| `birds_waking_3` | meadow birds (today) (0.0 s) | https://bigsoundbank.com/s0999.html | CC0 (BigSoundBank / Joseph Sardin) |
| `body_fall_1` | it settles on the bank (23.2 s) | https://bigsoundbank.com/s2452.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_2` | the ball stops with a little bounce (4x, 2.5 to 57.7 s) | https://bigsoundbank.com/s2277.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_4` | the snail waves (60.8 s) | https://bigsoundbank.com/s2279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `brush_concrete` | brush stroke (11x, 47.0 to 49.3 s) | https://bigsoundbank.com/s1107.html | CC0 (BigSoundBank / Joseph Sardin) |
| `bumblebee_2` | a dragonfly hums past (2x, 13.5 to 16.9 s) | https://bigsoundbank.com/s1001.html | CC0 (BigSoundBank / Joseph Sardin) |
| `carrot_crunch` | munching the ferns (13.3 s); chew (3x, 14.5 to 18.1 s) | https://bigsoundbank.com/s1594.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cave_1` | a cave-like hush inside the window (38.0 s) | https://bigsoundbank.com/s2135.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_1` | the fossil glints (3x, 0.8 to 4.0 s); FOSSIL! the bone appears (chimes) (49.5 s) | https://bigsoundbank.com/s2087.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_3` | a rising shimmer as time runs back (reversed chimes) (3x, 7.5 to 9.8 s) | https://bigsoundbank.com/s2089.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_1` | a crystal sparkle where a drop lands (6x, 39.1 to 43.1 s) | https://bigsoundbank.com/s2079.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_3` | the toy reaches the top: a small twinkle (59.5 s) | https://bigsoundbank.com/s2081.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cloth` | she kneels (cloth rustle) (46.9 s); arms up (cloth) (49.6 s); she lifts her arm (cloth) (57.2 s) | https://bigsoundbank.com/s0013.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cluster_chimes` | THE HIT: a burst of gold stars (43.0 s) | https://bigsoundbank.com/s2687.html | CC0 (BigSoundBank / Joseph Sardin) |
| `dogs_breathing` | the dog pants as it runs about (46.0 s) | https://bigsoundbank.com/s1547.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_1` | a drop seeps in (2x, 38.9 to 41.9 s) | https://bigsoundbank.com/s1384.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_2` | a drop seeps in (2x, 39.5 to 42.9 s) | https://bigsoundbank.com/s1385.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_3` | a drop seeps in (41.2 s) | https://bigsoundbank.com/s1386.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_4` | a drop seeps in (40.4 s) | https://bigsoundbank.com/s1387.html | CC0 (BigSoundBank / Joseph Sardin) |
| `fall_of_stone` | a small trickle of grit (4x, 44.5 to 46.2 s) | https://bigsoundbank.com/s1022.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_bird_1` | birds fly up from the big tree (49.6 s) | https://bigsoundbank.com/s2891.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_bird_2` | a pterosaur glides over the hills (14.6 s); birds fly up from the big tree (49.9 s) | https://bigsoundbank.com/s2892.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_pigeon` | birds fly up from the big tree (49.7 s) | https://bigsoundbank.com/s0840.html | CC0 (BigSoundBank / Joseph Sardin) |
| `forest` | a forest era races by (leaves and birds) (2x, 30.6 to 37.0 s) | https://bigsoundbank.com/s0100.html | CC0 (BigSoundBank / Joseph Sardin) |
| `glockenspiel` | FOSSIL! sparkle (a struck glockenspiel chord, raised to B7) (49.6 s) | https://bigsoundbank.com/s0920.html | CC0 (BigSoundBank / Joseph Sardin) |
| `goat_bleat_1` | a far soft call (a slowed goat stands in) (17.2 s) | https://bigsoundbank.com/s0279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `goat_bleat_2` | a far mammoth call (a slowed goat stands in) (34.2 s) | https://bigsoundbank.com/s0280.html | CC0 (BigSoundBank / Joseph Sardin) |
| `hammer_concrete` | THE HIT: a soft stone tok (43.0 s) | https://bigsoundbank.com/s1108.html | CC0 (BigSoundBank / Joseph Sardin) |
| `old_dog_bark_3` | the dog barks happily (3x, 49.8 to 51.5 s) | https://bigsoundbank.com/s2354.html | CC0 (BigSoundBank / Joseph Sardin) |
| `paper` | one leaf lands (24.7 s) | https://bigsoundbank.com/s0785.html | CC0 (BigSoundBank / Joseph Sardin) |
| `rain_concrete` | rain wears the land (44.0 s) | https://bigsoundbank.com/s1289.html | CC0 (BigSoundBank / Joseph Sardin) |
| `rain_puddle` | rain begins (25.0 s) | https://bigsoundbank.com/s1290.html | CC0 (BigSoundBank / Joseph Sardin) |
| `robin_1` | one bird (22.0 s); a bird calls over the last chord (62.6 s) | https://bigsoundbank.com/s1667.html | CC0 (BigSoundBank / Joseph Sardin) |
| `small_cascade` | the flood spreads (25.4 s) | https://bigsoundbank.com/s0507.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_1` | a baby splashes (3x, 9.9 to 19.5 s) | https://bigsoundbank.com/s1529.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_2` | a baby splashes (3x, 9.9 to 19.5 s) | https://bigsoundbank.com/s1530.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_3` | a baby splashes (3x, 11.5 to 21.1 s) | https://bigsoundbank.com/s1531.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_4` | a baby splashes (3x, 11.5 to 21.1 s) | https://bigsoundbank.com/s1532.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_5` | a baby splashes (2x, 13.1 to 17.9 s) | https://bigsoundbank.com/s1533.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_6` | a baby splashes (2x, 13.1 to 17.9 s) | https://bigsoundbank.com/s1534.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_leaves` | ferns unfurl (leaf rustle) (7.2 s) | https://bigsoundbank.com/s0137.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_mud` | the long-neck walks to the ferns (wet leaf and mud) (5x, 10.2 to 12.0 s); the old one walks to the bank (wet leaf and mud) (6x, 19.8 to 22.0 s); a wet squelch as the mud settles (5x, 26.5 to 29.8 s); a layer lands (damp settle) (5x, 30.5 to 36.9 s) | https://bigsoundbank.com/s0495.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_short_grass` | the turtle plods (tiny steps) (8x, 11.2 to 21.6 s); the babies walk off (6x, 21.4 to 23.9 s); she runs in over the grass (5x, 45.8 to 46.7 s); she lands, jumping for joy (2x, 49.9 to 50.5 s) | https://bigsoundbank.com/s0854.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_snow_1` | snow crunch (3x, 32.4 to 33.2 s) | https://bigsoundbank.com/s3363.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_wood_floor` | the long-neck walks to the ferns (5x, 10.2 to 12.0 s); the old one walks to the bank (6x, 19.8 to 22.0 s); the long-neck lies down (23.1 s); a layer lands (soft thud) (5x, 30.5 to 36.9 s); mammoths cross the steppe (far soft footfalls) (3x, 34.0 to 35.1 s) | https://bigsoundbank.com/s0165.html | CC0 (BigSoundBank / Joseph Sardin) |
| `strong_wind_1` | wind gusts (43.8 s) | https://bigsoundbank.com/s0146.html | CC0 (BigSoundBank / Joseph Sardin) |
| `strong_wind_village` | the red ball rolls in on the grass (a soft swish of air stands in) (0.6 s); grassland era races by (grass in the wind) (35.4 s); the red ball rolls back (a soft swish of air stands in) (55.3 s) | https://bigsoundbank.com/s0625.html | CC0 (BigSoundBank / Joseph Sardin) |
| `swirl_water` | a short flood brings a layer (5x, 30.1 to 36.5 s) | https://bigsoundbank.com/s0192.html | CC0 (BigSoundBank / Joseph Sardin) |
| `tibetan_bowl_1` | THE HIT: the stone glows (a singing bowl swells to the hit) (43.0 s) | https://bigsoundbank.com/s1109.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_duck` | the toy dinosaur squeaks as it is lifted (58.5 s) | https://bigsoundbank.com/s0364.html | CC0 (BigSoundBank / Joseph Sardin) |
| `triangle_2` | FOSSIL! a soft triangle (49.5 s) | https://bigsoundbank.com/s1688.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_bubble_2` | the round window opens (a soft bubble) (38.2 s); the window closes (a soft bubble, reversed) (44.0 s) | https://bigsoundbank.com/s0183.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_over_soil` | a wave of mud spreads (5x, 26.2 to 29.5 s) | https://bigsoundbank.com/s0563.html | CC0 (BigSoundBank / Joseph Sardin) |
| `watercourse_1` | the river (8.5 s) | https://bigsoundbank.com/s3132.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_3` | time runs backwards (a reversed whoosh) (6.5 s) | https://bigsoundbank.com/s1795.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_4` | time runs backwards (a reversed whoosh) (8.2 s) | https://bigsoundbank.com/s1796.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_5` | time runs backwards (a reversed whoosh) (8.8 s) | https://bigsoundbank.com/s1797.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_7` | time runs backwards (a reversed whoosh) (7.3 s) | https://bigsoundbank.com/s1800.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_8` | time runs backwards (a reversed whoosh) (5.6 s) | https://bigsoundbank.com/s1801.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_inside_1` | a long soft exhale of wind, the world hushes (23.2 s) | https://bigsoundbank.com/s1714.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_plain` | a soft breeze (today) (0.0 s) | https://bigsoundbank.com/s0595.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_whistle_2` | a wind of passing years (5.1 s); an ice era races by (cold wind) (32.2 s) | https://bigsoundbank.com/s0155.html | CC0 (BigSoundBank / Joseph Sardin) |
| `winder_1` | the clock spins backwards (a music-box winder, reversed) (9.8 s) | https://bigsoundbank.com/s1674.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wine_stopper_3` | words pop in: how do bones turn to stone? (0.3 s); words pop in: long ago (5.3 s); words pop in: mud (25.4 s); words pop in: millions of years (30.4 s); words pop in: bone to stone (38.4 s); words pop in: what is under your feet? (60.0 s) | https://bigsoundbank.com/s1719.html | CC0 (BigSoundBank / Joseph Sardin) |

## Stand-ins (honest)
- The red ball rolls on a soft swish of air (a band-passed village wind): the bank has no rolling ball. Its stop is two soft harp "boings", tuned to the music.
- The long-neck's footfalls are a slowed, low-passed wooden step with a slowed mud step on top: there is no recording of a giant. It will read as a heavy soft footfall, not as a dinosaur.
- Munching is a slowed raw carrot and apple crunch (a plant eater's mouth made large by slowing).
- Lying down is a slowed low-passed wooden step and a slowed body fall; the "exhale" is a swell of real wind inside a hall (no breath, on purpose: nothing to read as a sigh of death).
- The far soft call (17 s) and the far mammoth call (34 s) are slowed goat bleats, low-passed, far away and very quiet: there is no dinosaur or mammoth in any recording.
- Dragonflies are a bumblebee's hum passing; the pterosaur is a small bird's wings, slowed.
- The dog is an old dog's real barks, played a little faster so it sounds younger and happier: the nearest recording the bank has.
- The stone hit is a singing bowl that swells to the hit, a slowed low-passed hammer on concrete and a burst of real chimes: a blend for a magic moment, not a real stone.
- The rewind is real whooshes, chimes and a music-box winder played backwards, with a wind of years.
- The glockenspiel is a struck G7 chord raised a major third to B7 (the dominant of the key, over the climax); it is a real recording shifted, not played on a glockenspiel in B.
- Words pop in with a wine stopper's pop.

## Rebuild
`python3 films/cutaway/kids/fossil/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
