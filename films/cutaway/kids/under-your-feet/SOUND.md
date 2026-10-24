# Sound of "Who lives under your feet?" (Little Big Questions)

A SILENT 74 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on screen
has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg). Audio
never goes into git by default (`audio/mix.m4a` is committed here with `git add -f` because the render needs it; `audio/mix.wav`
is ignored); `audio/mix.json` (measurements, every recording and where it is used, the music edit, the event table, the
timelines) is kept.

**Music credit (for the description of the video):** Music: Wolfgang Amadeus Mozart, The Marriage of Figaro Overture, Czech National Symphony Orchestra, recorded by Musopen (CC0 / public domain).

## Music licence (read from the asset's `licence.json`)
CC0 1.0 Universal (Public Domain Dedication) as recorded on the Wikimedia Commons file page, which quotes Musopen's statement that uploaders must represent the content as public domain; no attribution required, credit given anyway. Source page: https://commons.wikimedia.org/wiki/File:Mozart,_The_Marriage_of_Figaro_(overture).ogg. Asset: release music of Eouchi147/rc-render: mozart-figaro-overture.ogg (6,344,097 bytes) with mozart-figaro-overture.licence.json. The Wikimedia Commons file page records the licence as
CC0 1.0 Universal and quotes Musopen's rule that uploaders "represent and warrant that content uploaded to the site is in the
public domain"; attribution is not required and is given anyway. The recording is Czech National Symphony Orchestra via
Musopen; the composition (Mozart, 1786) is long out of copyright.

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- 74.00 s, 48 kHz stereo AAC 256k, -16.1 LUFS integrated (target -16), true peak -1.90 dBTP (limit -1.5 dBTP), loudness range 7.1 LU.
- The loudest limiter dip is 1.2 dB at 68.3 s; the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction). On the rendered effects bus alone, 141 of 206 percussive spots stand out by 3 dB or more
  within 30 ms before to 150 ms after their event; the rest are quiet details sitting under a bed or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement and by rules, and must be checked by ear on a phone
  speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
Recording 0:00 to 0:27.6 (film 0 to 27.6), a triangular (linear in, linear out) cross-fade of 1.5 s (film 26.1 to 27.6) into recording
3:15.0 to 3:59.9 (film 26.1 to 71.0, played straight through the piece's own final cadence at film 68.05 and its decay), then a quiet
tail to 74.0 s. The hushed scurrying opening (pizzicato strings and whispering woodwinds) is the many small feet; the first tutti burst
at film 8.75 is the hidden world revealed; the tutti at 22.15 is the years racing; the finale tutti at film 34.0 (recording 202.9) is the
cicadas coming out; accents at 43.6 and 55.55 carry the climb and the splitting skin; the coda at 59.7 carries the wings opening and the song;
the final chord at 68.05 closes it. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio 2.3, gain between
-5.4 and +7.0 dB) lifts the whispering opening and eases the tuttis so the film can sit near -16 LUFS; the notes keep their own shape.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was checked to say
CC0 by the bank workflow), rc-render sfx-bank.yml run 40049538821 (24 Oct 2026). Event times are read from `blender.py` (its `T(**seconds)` calls) and `beats.json` at build time. Tonal sounds
(chimes, boings, bowl, glock, triangle) are tuned by resampling to the pitch classes the orchestra is playing at that moment (read from the
recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
| `birds_waking_3` | park birds (spring and summer) (0.0 s) | https://bigsoundbank.com/s0999.html | CC0 (BigSoundBank / Joseph Sardin) |
| `body_fall_1` | she settles on the lawn (69.9 s) | https://bigsoundbank.com/s2452.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_2` | the worms pop in (8.9 s); a cicada pops out of the lawn (2x, 34.0 to 34.6 s) | https://bigsoundbank.com/s2277.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_4` | the ants pop in (9.3 s); a cicada pops out of the lawn (34.2 s); the snail waves (69.5 s) | https://bigsoundbank.com/s2279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_6` | a tiny plop as the nymph lands (6.3 s); the grubs pop in (10.0 s); the crumb lands in the pantry (4x, 20.6 to 62.6 s); a cicada pops out of the lawn (34.3 s) | https://bigsoundbank.com/s2281.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_8` | the mole pops in (9.6 s); a cicada pops out of the lawn (34.5 s) | https://bigsoundbank.com/s2283.html | CC0 (BigSoundBank / Joseph Sardin) |
| `brush_wood` | the nymph digs down the shaft (7x, 8.4 to 11.4 s); scritch, they climb the trunk (18x, 42.7 to 53.2 s) | https://bigsoundbank.com/s1106.html | CC0 (BigSoundBank / Joseph Sardin) |
| `candle_sparkle_1` | the egg cracks (a tiny crackle) (5.3 s) | https://bigsoundbank.com/s1278.html | CC0 (BigSoundBank / Joseph Sardin) |
| `candle_sparkle_2` | a crackle of the skin (55.6 s) | https://bigsoundbank.com/s1279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cave_soundscape_1` | the hush of the soil (the hidden world) (8.7 s) | https://bigsoundbank.com/s2135.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_1` | the egg glints (3x, 0.8 to 4.2 s); THE WINGS OPEN: chimes on the coda (59.7 s) | https://bigsoundbank.com/s2087.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_3` | a sparkle on the label (14.7 s); a rising shimmer up the shaft (reversed chimes) (3x, 32.0 to 33.5 s) | https://bigsoundbank.com/s2089.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_1` | the roots wake and drink (a sparkle) (3x, 10.5 to 11.4 s); the wings grow, glowing (56.5 s) | https://bigsoundbank.com/s2079.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_3` | the final chord: a twinkle (68.1 s) | https://bigsoundbank.com/s2081.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cloth` | the wings unfold (soft cloth) (56.0 s); the girl lies down, ear to the grass (cloth) (69.0 s) | https://bigsoundbank.com/s0013.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cluster_chimes` | THE HIDDEN WORLD: tunnels glow open (a burst of chimes on the tutti) (8.8 s); THEY ARE OUT: a burst of chimes on the finale tutti (34.0 s) | https://bigsoundbank.com/s2687.html | CC0 (BigSoundBank / Joseph Sardin) |
| `dig_shovel` | the mole digs (soft) (6x, 11.8 to 29.8 s) | https://bigsoundbank.com/s1305.html | CC0 (BigSoundBank / Joseph Sardin) |
| `dreamcatcher` | a held breath before the song (58.5 s) | https://bigsoundbank.com/s0040.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_1` | the nymph sips root juice (a drop) (3x, 12.6 to 25.8 s) | https://bigsoundbank.com/s1384.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_2` | the nymph sips root juice (a drop) (3x, 14.4 to 27.6 s) | https://bigsoundbank.com/s1385.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_3` | the nymph sips root juice (a drop) (2x, 17.8 to 24.0 s) | https://bigsoundbank.com/s1386.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_4` | the nymph sips root juice (a drop) (2x, 16.0 to 22.7 s) | https://bigsoundbank.com/s1387.html | CC0 (BigSoundBank / Joseph Sardin) |
| `field_cricket` | the cicada song (a field cricket chorus stands in; see SOUND.md) (60.1 s) | https://bigsoundbank.com/s1020.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_bird_1` | birds fly up from the big tree (34.2 s) | https://bigsoundbank.com/s2891.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_bird_2` | birds fly up from the big tree (34.5 s) | https://bigsoundbank.com/s2892.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_bird_3` | birds join the song (2x, 62.5 to 64.9 s) | https://bigsoundbank.com/s2893.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_bird_4` | birds join the song (60.7 s) | https://bigsoundbank.com/s2894.html | CC0 (BigSoundBank / Joseph Sardin) |
| `flight_pigeon` | birds fly up from the big tree (34.3 s) | https://bigsoundbank.com/s0840.html | CC0 (BigSoundBank / Joseph Sardin) |
| `glockenspiel` | THE HIDDEN WORLD: sparkle (8.8 s); THE WINGS OPEN: a bright sparkle (59.8 s) | https://bigsoundbank.com/s0920.html | CC0 (BigSoundBank / Joseph Sardin) |
| `heartbeat_5` | many small hearts wake (28.0 s) | https://bigsoundbank.com/s1930.html | CC0 (BigSoundBank / Joseph Sardin) |
| `ice_crack_2` | the shell splits (5.7 s); the old skin splits (a soft crack on the accent) (55.5 s) | https://bigsoundbank.com/s2206.html | CC0 (BigSoundBank / Joseph Sardin) |
| `metallophone` | a year turns (a soft tick) (6x, 22.3 to 26.6 s) | https://bigsoundbank.com/s3067.html | CC0 (BigSoundBank / Joseph Sardin) |
| `old_dog_bark_3` | the dog barks happily (3x, 34.7 to 37.1 s); the dog barks and dances (4x, 60.5 to 65.7 s) | https://bigsoundbank.com/s2354.html | CC0 (BigSoundBank / Joseph Sardin) |
| `robin_1` | a robin in the tree (47.0 s); a bird calls in the quiet (71.2 s) | https://bigsoundbank.com/s1667.html | CC0 (BigSoundBank / Joseph Sardin) |
| `rusk_crunch` | a grub munches a root (9x, 11.5 to 29.9 s) | https://bigsoundbank.com/s0407.html | CC0 (BigSoundBank / Joseph Sardin) |
| `solitary_bees` | a shimmer around the song (60.6 s) | https://bigsoundbank.com/s0101.html | CC0 (BigSoundBank / Joseph Sardin) |
| `squeaker_toy_2` | the crumb is home (a tiny squeak: the joke) (4x, 20.5 to 62.5 s) | https://bigsoundbank.com/s0879.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_leaves` | leaves of the years (22.6 s) | https://bigsoundbank.com/s0137.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_mud` | a worm slides along its tunnel (6x, 10.9 to 26.4 s) | https://bigsoundbank.com/s0495.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_pebbles` | ants skitter in the tunnels (10x, 10.3 to 30.1 s); the ant hauls its crumb (20x, 12.6 to 60.6 s); little feet crawl to the shaft (10x, 29.2 to 33.2 s) | https://bigsoundbank.com/s0839.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_short_grass` | shoes pass on the lawn above (8x, 0.7 to 4.2 s); the kids dance on the grass (6x, 60.0 to 61.5 s) | https://bigsoundbank.com/s0854.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_twigs` | tiny feet scurry to the hole (9x, 6.4 to 7.8 s); the cicadas march to the tree (22x, 36.5 to 41.5 s) | https://bigsoundbank.com/s1301.html | CC0 (BigSoundBank / Joseph Sardin) |
| `suction_cup_plastic` | a nymph lets go of the root (a tiny pop) (5x, 28.4 to 28.9 s) | https://bigsoundbank.com/s1261.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sun_heat_1` | the soil warms (a warm hush) (27.5 s) | https://bigsoundbank.com/s1779.html | CC0 (BigSoundBank / Joseph Sardin) |
| `tibetan_bowl_1` | the final chord: a singing bowl swells in (68.0 s) | https://bigsoundbank.com/s1109.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_squeal_1` | the kids gasp (a toy squeal stands in) (34.5 s) | https://bigsoundbank.com/s3331.html | CC0 (BigSoundBank / Joseph Sardin) |
| `triangle_2` | THE WINGS OPEN: a soft triangle (59.7 s); the final chord: a soft triangle (68.2 s) | https://bigsoundbank.com/s1688.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_bubble_2` | a dive into the hole (a soft bubble) (8.0 s) | https://bigsoundbank.com/s0183.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_over_soil` | soil trickles in (8.0 s); soil crumbs fall away (34.0 s) | https://bigsoundbank.com/s0563.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_inside_2` | a breath of air up the shaft (32.3 s) | https://bigsoundbank.com/s1715.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_plain` | a soft breeze (autumn and winter swell it) (0.0 s) | https://bigsoundbank.com/s0595.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_tree_squeaks` | the big tree creaks in the breeze (42.4 s) | https://bigsoundbank.com/s1051.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_whistle_2` | a wind of years (21.9 s) | https://bigsoundbank.com/s0155.html | CC0 (BigSoundBank / Joseph Sardin) |
| `winder_1` | the clock winds (a music-box winder) (21.9 s) | https://bigsoundbank.com/s1674.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wine_stopper_3` | the label pops: CICADA! (14.7 s); words pop in: who lives under your feet? (0.3 s); words pop in: a hidden world! (9.1 s); words pop in: cicada! (14.6 s); words pop in: 17 years (22.5 s); words pop in: all together! (29.0 s); words pop in: who is down there right now? (68.0 s) | https://bigsoundbank.com/s1719.html | CC0 (BigSoundBank / Joseph Sardin) |

## Stand-ins (honest)
- The cicada song (60 to 74 s) is a field recording of crickets, filtered and kept soft, with a bee shimmer: the bank has no cicada. It reads as a bright insect chorus, not as a real periodical cicada.
- Tiny feet (the hatchling, the ants, the marching cicadas) are a twig or pebble step, sped up and high-passed: there is no recording of an insect walking.
- Digging and climbing scratches are a wooden brush stroke and a shovel in soil, slowed or sped up and filtered. The mole is a muffled shovel crunch.
- Worms are a slowed, low-passed mud step. Grubs munching is a sped-up rusk crunch.
- The egg crack is a soft ice crack and a candle crackle: there is no recording of an egg.
- The nymph's sips are real water drops. Pops of the neighbours and of the cicadas coming out are soft harp "boings", tuned to the music.
- The dog is an old dog's real barks, played a little faster so it sounds younger and happier: the nearest recording the bank has.
- The kids' gasp is a toy squeal (no children's voices in the bank, on purpose: the film has no voices).
- The wings opening are real chimes, a triangle and a glockenspiel chord raised a major third; the unfolding is soft cloth.
- Words pop in with a wine stopper's pop.

## Rebuild
`python3 films/cutaway/kids/under-your-feet/audio/make_audio.py` (about a minute; it needs the bank and the recording once).
`$MUSIC_FILE` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
