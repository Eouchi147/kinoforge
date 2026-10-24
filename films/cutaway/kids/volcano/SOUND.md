# Sound of the volcano film (Little Big Questions: how is a volcano born?)

A SILENT 72.3 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
`audio/mix.m4a` is committed (force-added); `audio/mix.wav` is ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** Music: Edvard Grieg, In the Hall of the Mountain King, performed by the Musopen Symphony (musopen.org), public domain.

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- 72.30 s, 48 kHz stereo AAC 256k, -16.2 LUFS integrated (target -16), true peak -1.80 dBTP (limit -1.5 dBTP), loudness range 8.8 LU.
- The loudest limiter dip is 4.3 dB at 38.7 s; the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; a thud's or a bubble's loudest instant sits 10 to 35 ms after the event
  frame). On the rendered effects bus alone, 99 of 152 percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under a bed or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
Grieg, Peer Gynt Suite No. 1, IV. In the Hall of the Mountain King, Musopen Symphony (Musopen), Public domain (Wikimedia Commons record). Source: https://commons.wikimedia.org/wiki/File:Grieg_-_Peer_Gynt_Suite_No._1,_Op._46_-_IV._In_the_Hall_of_the_Mountain_King_(Musopen_Symphony).flac. Asset: Eouchi147/rc-render release music: grieg-mountain-king-musopen.flac (+ .licence.json).
four cuts, each on a rest of the music, 72.3 s: recording 0:00 to 0:09.0 (the whisper); cross-fade 0.5 s into 1:17.2 to 1:52.0 (the accelerando up to the big entrance at 1:40.09 = the eruption at film 31.39, then the full orchestra); cross-fade 1.0 s into 2:14.1 to 2:31.9 (the eight orchestral hits at 2:15.15, 2:16.11, 2:19.08, 2:20.02, 2:22.95, 2:23.89, 2:24.84 and the piece's own final crash at 2:28.62 = eight more eruptions, the last the biggest); cross-fade 1.0 s into 0:17.8 to 0:31.0 (the quiet theme again for the calm); loudnorm -16 LUFS, true peak -1.5 dBTP
Every cut sits on a rest of the music; the cross-fades are triangular (linear in, linear out). The music leads. A slow level rider
(zero-phase, 1 s Gaussian smoothing, ratio 2.6, gain between -6.3 and +14.0 dB) lifts the whispering opening
and eases the tutti so the film can sit near -16 LUFS; the notes keep their own shape.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow): rc-render sfx-bank.yml run 40049538821 (24 Oct 2026). Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowl, chimes, boings, bubbles, plant pops, squeaks) are tuned by resampling to the pitch classes the orchestra is playing at that moment
(read from the recording, mostly B minor), so they ring with the chord and never against it. Steady beds (sea, rumble, fizz, crackle, birds) follow the music's own
smoothed level, a fixed number of dB under it, so they are felt more than heard.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
| `big_broth` | thick magma bubbles slowly (5.2 s) | https://bigsoundbank.com/s0491.html | CC0 (BigSoundBank / Joseph Sardin) |
| `birds_waking_3` | small birds find the green island (59.4 s) | https://bigsoundbank.com/s0999.html | CC0 (BigSoundBank / Joseph Sardin) |
| `body_fall_1` | a new layer settles (soft thud) (8x, 43.4 to 56.8 s) | https://bigsoundbank.com/s2452.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_2` | the beach ball stops with a little bounce (2x, 2.4 to 2.7 s) | https://bigsoundbank.com/s2277.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_4` | the cap lands on the sandcastle (32.5 s); the snail waves (69.6 s) | https://bigsoundbank.com/s2279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_6` | the beach ball lands after its hop (9x, 32.1 to 57.5 s) | https://bigsoundbank.com/s2281.html | CC0 (BigSoundBank / Joseph Sardin) |
| `bubbles_burst` | a gas bubble pops in the magma (42x, 21.4 to 30.9 s) | https://bigsoundbank.com/s1074.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_1` | a chime for each old island (66.4 s) | https://bigsoundbank.com/s2087.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_3` | a chime for each old island (66.9 s) | https://bigsoundbank.com/s2089.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_1` | a chime for each old island (67.4 s) | https://bigsoundbank.com/s2079.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_3` | a chime for our new island (67.9 s); a last twinkle for the question (70.5 s) | https://bigsoundbank.com/s2081.html | CC0 (BigSoundBank / Joseph Sardin) |
| `creak_barn_door` | the rock creaks open (a slowed door stands in) (12.4 s) | https://bigsoundbank.com/s0539.html | CC0 (BigSoundBank / Joseph Sardin) |
| `fire_branching_1` | the lava crackles as it flows (32.0 s) | https://bigsoundbank.com/s0987.html | CC0 (BigSoundBank / Joseph Sardin) |
| `glockenspiel` | sparkles on the final crash (56.9 s) | https://bigsoundbank.com/s0920.html | CC0 (BigSoundBank / Joseph Sardin) |
| `gulls_harbor` | gulls over the beach (the hook) (0.0 s); gulls over the calm (59.0 s); the gulls cheer from a safe distance (32.3 s); the gulls cheer again (58.0 s) | https://bigsoundbank.com/s2573.html | CC0 (BigSoundBank / Joseph Sardin) |
| `ice_crack_1` | the cooling rock ticks (2x, 34.1 to 50.9 s); the first lava cools into new rock (ticks) (2x, 37.4 to 41.5 s) | https://bigsoundbank.com/s2205.html | CC0 (BigSoundBank / Joseph Sardin) |
| `ice_crack_2` | the cooling rock ticks (2x, 46.0 to 53.9 s); the first lava cools into new rock (ticks) (2x, 39.0 to 40.6 s) | https://bigsoundbank.com/s2206.html | CC0 (BigSoundBank / Joseph Sardin) |
| `ice_crack_3` | the cooling rock ticks (2x, 47.0 to 54.8 s) | https://bigsoundbank.com/s2207.html | CC0 (BigSoundBank / Joseph Sardin) |
| `ice_crack_4` | the cooling rock ticks (2x, 50.0 to 55.7 s) | https://bigsoundbank.com/s2208.html | CC0 (BigSoundBank / Joseph Sardin) |
| `plant_cartoon_1` | a plant finds a home on the new rock (3x, 59.3 to 64.9 s) | https://bigsoundbank.com/s1950.html | CC0 (BigSoundBank / Joseph Sardin) |
| `plant_cartoon_4` | the snail peeks out again (33.6 s); a plant finds a home on the new rock (2x, 60.8 to 63.6 s) | https://bigsoundbank.com/s1953.html | CC0 (BigSoundBank / Joseph Sardin) |
| `robin_1` | a bird sings in the new green (62.6 s) | https://bigsoundbank.com/s1667.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sea_tern` | a tern calls over the sea (1.1 s) | https://bigsoundbank.com/s0267.html | CC0 (BigSoundBank / Joseph Sardin) |
| `small_waves_ocean` | the sea laps the beach (0.0 s) | https://bigsoundbank.com/s1046.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sparkling_water` | the shaken bottle fizzes (23.0 s); fizz and foam burst from the bottle (31.4 s); a short fizz of the small fountain (8x, 43.4 to 56.8 s) | https://bigsoundbank.com/s0230.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_big_3` | a big happy splash as the lava slides into the sea (58.3 s) | https://bigsoundbank.com/s1521.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_1` | a dolphin leaps from the sea (2x, 2.4 to 60.2 s); the dolphin dives back in (33.0 s) | https://bigsoundbank.com/s1529.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_2` | a dolphin leaps from the sea (2x, 12.6 to 63.4 s); the dolphin dives back in (41.5 s) | https://bigsoundbank.com/s1530.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_3` | a dolphin leaps from the sea (2x, 24.6 to 68.2 s); the dolphin dives back in (52.0 s) | https://bigsoundbank.com/s1531.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_4` | the dolphin dives back in (2x, 3.9 to 61.7 s); a dolphin leaps from the sea (31.6 s) | https://bigsoundbank.com/s1532.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_5` | the dolphin dives back in (2x, 14.1 to 64.9 s); a dolphin leaps from the sea (40.0 s) | https://bigsoundbank.com/s1533.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_6` | the dolphin dives back in (2x, 26.1 to 69.7 s); a dolphin leaps from the sea (50.5 s) | https://bigsoundbank.com/s1534.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steam_hiss_1` | a puff of steam (31.9 s); lava hisses where it meets the sea (8x, 45.2 to 58.7 s) | https://bigsoundbank.com/s0227.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steam_hiss_3` | steam where the lava meets the sea (33.8 s); a puff of steam (8x, 43.9 to 57.3 s) | https://bigsoundbank.com/s3011.html | CC0 (BigSoundBank / Joseph Sardin) |
| `strong_wind_village` | the beach ball rolls in on the sand (a soft swish of air stands in) (0.4 s) | https://bigsoundbank.com/s0625.html | CC0 (BigSoundBank / Joseph Sardin) |
| `suction_cup_plastic` | the snail pops into its shell (31.0 s) | https://bigsoundbank.com/s1261.html | CC0 (BigSoundBank / Joseph Sardin) |
| `swirl_water` | the drink sloshes as it is shaken (23.0 s) | https://bigsoundbank.com/s0192.html | CC0 (BigSoundBank / Joseph Sardin) |
| `thunder_2` | the biggest rumble on the final crash (56.8 s) | https://bigsoundbank.com/s3113.html | CC0 (BigSoundBank / Joseph Sardin) |
| `thunder_3` | the big happy rumble of the eruption (31.3 s) | https://bigsoundbank.com/s3114.html | CC0 (BigSoundBank / Joseph Sardin) |
| `thunder_8` | the deep rumble of the magma far below (4.9 s) | https://bigsoundbank.com/s3181.html | CC0 (BigSoundBank / Joseph Sardin) |
| `tibetan_bowl_1` | the chamber begins to glow (a warm bowl) (5.0 s) | https://bigsoundbank.com/s1109.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_squeal_1` | a happy squeak from the snail (70.0 s) | https://bigsoundbank.com/s3331.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_squeal_3` | a happy squeak (a toy squeal stands in for a dolphin) (4x, 3.0 to 60.8 s) | https://bigsoundbank.com/s3333.html | CC0 (BigSoundBank / Joseph Sardin) |
| `triangle_2` | a ping on our own island (68.0 s) | https://bigsoundbank.com/s1688.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_bubble_2` | a blob of magma lifts off the chamber (8x, 9.1 to 19.2 s); the gas fizzes in the crack (21.0 s) | https://bigsoundbank.com/s0183.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_over_soil` | the soil forms (60.0 s) | https://bigsoundbank.com/s0563.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_9` | the cap whooshes over to the sandcastle (31.5 s); a little jet leaps from the top (8x, 43.2 to 56.7 s) | https://bigsoundbank.com/s1802.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_long_1` | WHOOSH: lava leaps out of the top (31.3 s) | https://bigsoundbank.com/s0572.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_plain` | a soft breeze in the new leaves (58.8 s) | https://bigsoundbank.com/s0595.html | CC0 (BigSoundBank / Joseph Sardin) |
| `winder_1` | the clock spins (a music-box winder) (43.0 s) | https://bigsoundbank.com/s1674.html | CC0 (BigSoundBank / Joseph Sardin) |
| `winder_2` | the clock spins on (a music-box winder) (52.9 s) | https://bigsoundbank.com/s1675.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wine_stopper_3` | the bottle pops its cap (31.4 s); words pop in: how is a volcano born? (0.3 s); words pop in: magma (5.2 s); words pop in: lava (31.7 s); words pop in: new rock (35.4 s); words pop in: layer by layer (42.6 s); words pop in: hawaii (66.3 s); words pop in: is the ground under your feet really still? (69.3 s) | https://bigsoundbank.com/s1719.html | CC0 (BigSoundBank / Joseph Sardin) |

## Stand-ins (honest)
- The beach ball rolls on a soft swish of air (a band-passed village wind): the bank has no rolling ball. Its stop and every hop are soft harp "boings", tuned to the music.
- Dolphins are real splashes with a toy squeal tuned to the music for a happy squeak: there is no dolphin in the bank.
- The deep rumble of the magma is real thunder, low-passed to the floor of hearing; thick bubbling magma is a real pot of broth, slowed and low-passed; the cracking rock is a slowed barn door.
- Gas bubbles popping in the magma are real bubbles bursting in water, slowed and lowered as they grow; the glowing chamber is a singing bowl.
- The shaken bottle is real sparkling water (fizz) and a swirl of water; the cap pop is a wine-stopper pop slowed a little; the cap flying is a short whoosh.
- The lava fountain is a long real whoosh plus a thunder rumble and real fizz; lava crackle is a real fire in branches; steam is a real steam hiss; cooling rock ticks are real ice cracks sped up and filtered. There is no lava in any recording.
- The gulls cheer is a real gull recording from a harbour, placed on the eruption.
- The snail popping into its shell is a suction-cup pop; peeking out and waving are a plant-pop and a boing; its happy squeak is a toy squeal.
- Plants finding a home are cartoon plant pops tuned to the music; the soil forming is water over soil, soft.
- The clock spinning is a music-box winder.
- Words pop in with a wine stopper's pop, sped up.

## Rebuild
`python3 films/cutaway/kids/volcano/audio/make_audio.py` (a few minutes; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
