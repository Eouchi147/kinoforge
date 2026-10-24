# Sound of the rain film (Little Big Questions, film 3)

A SILENT 73 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
`audio/mix.wav` is ignored; `audio/mix.m4a` is committed with `git add -f` (the runners need it) together with `audio/mix.json`
(measurements, every recording and where it is used, the music edit, the event table, the timelines).

**Music credit (for the description of the video):** Music: Bedřich Smetana, Vltava (The Moldau), performed by the Musopen Symphony (musopen.org), public domain.

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- 73.00 s, 48 kHz stereo AAC 256k, -16.1 LUFS integrated (target -16), true peak -2.00 dBTP (limit -1.5 dBTP), loudness range 8.1 LU.
- The loudest limiter dip is 1.8 dB at 68.2 s (the loud river theme); the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; the loudest instant of a footstep or splash sits 10 to 35 ms after the event
  frame, a pop on its frame). On the rendered effects bus alone, 69 of 109 percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under the river, rain or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
Smetana, Má Vlast, no. 2, Vltava (The Moldau), Musopen Symphony (Musopen), Public domain (Wikimedia Commons record; Musopen requires uploaders to warrant public domain). Source: https://commons.wikimedia.org/wiki/File:Smetana_-_M%C3%A1_Vlast_-_Vltava_(Musopen_Symphony).flac. Asset: Eouchi147/rc-render release music: smetana-vltava-musopen.flac (+ .licence.json).
recording 0:00.0 to 0:16.95, 1.5 s cross-fade (joint 0:16.2 = 0:44.4: flutes in the same key, 0.95 chroma match) into 0:43.65 to 1:17.5 (the springs swell, the river theme enters at 1:02.1 = film 33.86), 1.0 s cross-fade (joint 1:17.0 = 11:52.2, V to I) into 11:51.7 to 12:09.0 (the broad river theme in major, big phrase at 11:56.0, final chord 12:03.8), 2.0 s cross-fade into 12:40.8 to 12:50.2 (the piece's own two final chords at 12:45.2 and 12:47.2) with a 0.6 s fade-out; level rider; loudnorm -16 LUFS, true peak -1.5 dBTP; 73.0 s
The music leads. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio 3.4,
gain between -9.0 and +17.0 dB) lifts the whispering opening and eases the sunrise climax so the film can sit near
-16 LUFS; the notes keep their own shape. The music is lowered by at most 1.5 dB under the rain and the rainbow.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). The bank is the one extended on 24 Oct 2026 for the kids series: rc-render sfx-bank.yml run 40049538821 (24 Oct 2026). Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowl, chimes, glock, toy squeak, boings) are tuned by resampling to the
pitch classes the orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
| `birds_waking_3` | morning birds (and again when the sun is back) (0.0 s) | https://bigsoundbank.com/s0999.html | CC0 (BigSoundBank / Joseph Sardin) |
| `blackbird_30` | a bird sings again (51.2 s) | https://bigsoundbank.com/s3503.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_2` | the last two join: one plump drop (32.8 s); a hop (a soft boing) (5x, 42.2 to 69.2 s) | https://bigsoundbank.com/s2277.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_4` | the umbrella bounces open (a soft boing) (36.9 s); the snail wiggles happily in the rain (2x, 36.5 to 39.8 s); the snail waves (67.8 s) | https://bigsoundbank.com/s2279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `bubbles_burst` | two drops bump and stick (a soft blip) (2x, 29.1 to 29.4 s) | https://bigsoundbank.com/s1074.html | CC0 (BigSoundBank / Joseph Sardin) |
| `candle_sparkle_1` | a tiny drop joins the cloud (14x, 18.9 to 24.8 s) | https://bigsoundbank.com/s1278.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_1` | a glint on the lake (4x, 7.7 to 11.8 s) | https://bigsoundbank.com/s2087.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_3` | a last twinkle (68.0 s) | https://bigsoundbank.com/s2089.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_1` | the water rises as an invisible shimmer (reversed chimes) (4x, 13.0 to 18.0 s); new shimmer rises again (reversed chimes) (3x, 58.7 to 62.1 s) | https://bigsoundbank.com/s2079.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_3` | the rainbow paints itself across the sky (chimes) (4x, 52.5 to 55.0 s) | https://bigsoundbank.com/s2081.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cloth` | the umbrella unfurls (cloth) (36.0 s); the umbrella is shut (cloth) (50.1 s) | https://bigsoundbank.com/s0013.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cluster_chimes` | the cloud puffs up (a soft shimmer) (3x, 20.3 to 26.0 s) | https://bigsoundbank.com/s2687.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_1` | the first raindrops fall (33.9 s); a raindrop (2x, 36.2 to 37.2 s); a drop sinks down to the water in the sand (4x, 39.1 to 47.3 s) | https://bigsoundbank.com/s1384.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_2` | a raindrop (3x, 34.7 to 37.4 s); a drop sinks down to the water in the sand (5x, 38.0 to 49.1 s) | https://bigsoundbank.com/s1385.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_3` | two drops bump and stick (a soft blip) (2x, 31.6 to 31.9 s); a raindrop (2x, 35.8 to 37.0 s) | https://bigsoundbank.com/s1386.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_4` | a raindrop (2x, 35.4 to 36.8 s); a drop sinks down to the water in the sand (4x, 39.9 to 48.0 s) | https://bigsoundbank.com/s1387.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_metal_pan` | a raindrop plinks in the watering can (11x, 36.5 to 48.5 s) | https://bigsoundbank.com/s1382.html | CC0 (BigSoundBank / Joseph Sardin) |
| `forest_stream_1` | the brook (it swells in the rain) (0.0 s) | https://bigsoundbank.com/s2713.html | CC0 (BigSoundBank / Joseph Sardin) |
| `glockenspiel` | the rainbow arrives (a struck glockenspiel chord, tuned) (52.6 s) | https://bigsoundbank.com/s0920.html | CC0 (BigSoundBank / Joseph Sardin) |
| `night_after_rain` | drip, drip: after the rain (49.3 s) | https://bigsoundbank.com/s0621.html | CC0 (BigSoundBank / Joseph Sardin) |
| `paper` | paper rustle (the boat) (40.7 s) | https://bigsoundbank.com/s0785.html | CC0 (BigSoundBank / Joseph Sardin) |
| `rain_concrete` | rain on leaves (36.9 s) | https://bigsoundbank.com/s1289.html | CC0 (BigSoundBank / Joseph Sardin) |
| `rain_puddle` | the cloud grows heavy (a far hush of rain) (29.0 s); soft rain (35.9 s); rain drums on the umbrella (37.1 s) | https://bigsoundbank.com/s1290.html | CC0 (BigSoundBank / Joseph Sardin) |
| `robin_1` | a bird sings again (2x, 50.3 to 52.3 s); a bird calls over the last chord (71.0 s) | https://bigsoundbank.com/s1667.html | CC0 (BigSoundBank / Joseph Sardin) |
| `small_cascade` | the brook swells (43.5 s) | https://bigsoundbank.com/s0507.html | CC0 (BigSoundBank / Joseph Sardin) |
| `small_waves_ocean` | the far sea (56.2 s) | https://bigsoundbank.com/s1046.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sparkling_water` | the water glitters in the warm sun (7.5 s) | https://bigsoundbank.com/s0230.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_big_1` | she lands in the puddle: SPLASH (70.0 s) | https://bigsoundbank.com/s1519.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_2` | she lands in the puddle: SPLASH (43.0 s) | https://bigsoundbank.com/s1530.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_3` | two drops bump and stick (a soft blip) (32.7 s) | https://bigsoundbank.com/s1531.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_4` | she lands in the puddle: SPLASH (44.6 s) | https://bigsoundbank.com/s1532.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_5` | she lands in the puddle: SPLASH (46.2 s) | https://bigsoundbank.com/s1533.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_small_6` | she lands in the puddle: SPLASH (47.8 s) | https://bigsoundbank.com/s1534.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_short_grass` | she runs in over the wet grass (8x, 35.2 to 36.7 s) | https://bigsoundbank.com/s0854.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sun_heat_1` | the sun warms (a warm hum) (6.0 s) | https://bigsoundbank.com/s1779.html | CC0 (BigSoundBank / Joseph Sardin) |
| `swirl_water` | the water table rises in the sand (46.0 s) | https://bigsoundbank.com/s0192.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_duck` | the rubber duck squeaks on the lake (59.7 s); the rubber duck squeaks again (60.0 s) | https://bigsoundbank.com/s0364.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_squeal_1` | the snail wiggles happily in the rain (34.9 s) | https://bigsoundbank.com/s3331.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_squeal_3` | the snail wiggles happily in the rain (38.0 s) | https://bigsoundbank.com/s3333.html | CC0 (BigSoundBank / Joseph Sardin) |
| `triangle_2` | a soft triangle on the rainbow (52.7 s) | https://bigsoundbank.com/s1688.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_bubble_2` | the round window opens (a soft bubble) (25.8 s); two drops bump and stick (a soft blip) (5x, 27.8 to 30.7 s); the paper boat is set on the brook (41.0 s) | https://bigsoundbank.com/s0183.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_over_soil` | the water sinks into the soil (37.0 s) | https://bigsoundbank.com/s0563.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_3` | the fat drop falls out of the window (33.3 s) | https://bigsoundbank.com/s1795.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_inside_1` | high up the air is cold and still (a soft wind) (13.0 s) | https://bigsoundbank.com/s1714.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_plain` | a soft breeze (0.0 s) | https://bigsoundbank.com/s0595.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wine_stopper_3` | POP: the yellow umbrella opens (36.8 s); words pop in: where does rain come from? (0.3 s); words pop in: invisible water (12.8 s); words pop in: tiny drops (19.4 s); words pop in: about a million (25.9 s); words pop in: around and around (57.4 s); words pop in: where has your rain been? (64.8 s) | https://bigsoundbank.com/s1719.html | CC0 (BigSoundBank / Joseph Sardin) |

## Stand-ins (honest)
- The umbrella pop is a wine stopper's pop plus a soft harp boing tuned to the music: the bank has no umbrella.
- The child's running is a real soft footstep on short grass (the bank has no wet grass or rubber boots); the puddle splashes are real small splashes.
- The snail's happy wiggle is a toy squeal and soft boings, panned right: there is no recording of a snail.
- The drops that bump and stick in the magnifier are soft water bubbles and bubble bursts (the bank has no cloud droplets); the last join is a soft boing.
- The invisible water rising is reversed chimes tuned to the music (a shimmer, not a real sound of vapour).
- The tiny drops gathering are a candle sparkle (tiny tinks).
- The paper boat is a rustle of paper and a bubble where it touches the water.
- The rainbow is a struck glockenspiel, chimes and a triangle, tuned to the orchestra; a rainbow has no sound.
- No thunder anywhere (it would frighten the very young); the rain is a soft puddle-rain bed and rain on leaves.
- Words pop in with a wine stopper's pop.

## Rebuild
`python3 films/cutaway/kids/rain/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
