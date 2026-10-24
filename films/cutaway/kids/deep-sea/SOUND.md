# Sound of the deep-sea film (Little Big Questions)

A SILENT 70.5 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
Audio never goes into git: `audio/mix.m4a` and `audio/mix.wav` are ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** Music: Felix Mendelssohn, The Hebrides (Fingal's Cave) Overture, performed by the Musopen Symphony (musopen.org), public domain.

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- 70.50 s, 48 kHz stereo AAC 256k, -16.1 LUFS integrated (target -16), true peak -1.90 dBTP (limit -1.5 dBTP), loudness range 4.9 LU.
- The loudest limiter dip is 5.7 dB at 63.1 s (the climax of the Hebrides, where every light comes on); the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (zero offset by construction; the loudest instant of a splash or a thump sits 10 to 35 ms after the event
  frame). On the rendered effects bus alone, 57 of 79 percussive spots stand out by 3 dB or more within 30 ms before to 150 ms
  after their event; the rest are quiet details sitting under the river, rain or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
Mendelssohn, The Hebrides (Fingal's Cave), Overture, Op. 26, Musopen Symphony (Musopen), Public domain (Wikimedia Commons licence record: Public domain; Musopen requires uploaders to warrant public domain content). The research notes list CC BY 3.0 on IMSLP for the performance; credited either way.. Source: https://commons.wikimedia.org/wiki/File:Mendelssohn_-_Hebrides_Overture,_Op._26_(Musopen_Symphony).flac. Asset: Eouchi147/rc-render release music: mendelssohn-hebrides-musopen.flac (+ .licence.json).
Recording 0:00.5 to 0:26.0, a triangular (linear in, linear out) cross-fade of 2.0 s (film 23.5 to 25.5) into recording 1:05.0 to 1:42.0,
then a 2.0 s cross-fade (film 58.5 to 60.5) into recording 11:07.5 to 11:20.0; 70.5 s. The music leads. A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio 3.2,
gain between -4.8 and +10.0 dB) lifts the whispering opening and the hush of the midnight zone and eases the climax so the film can sit near
-16 LUFS; the notes keep their own shape. The music is lowered by at most 1.5 dB under the climax cascade of chimes.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). The bank is the one extended on 24 Oct 2026 with the BigSoundBank ids of
`docs/research/KIDS_MUSIC_2026-10.md` section 5.1 (soft boings, chimes, bowls, soft steps, splashes):
rc-render sfx-bank.yml run 40049538821 (24 Oct 2026). Event times are read from `blender.py` (EVENTS) and `beats.json` at build time: a re-timed picture re-times
the sound. Tonal sounds (bowls, chimes, glock, toy squeaks, boings) are tuned by resampling to the
pitch classes the orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
| `bell_1oclock` | the boat rings a far soft bell (3.7 s) | https://bigsoundbank.com/s3446.html | CC0 (BigSoundBank / Joseph Sardin) |
| `blow_1` | the whale blows a far soft spout (5x, 1.4 to 69.2 s) | https://bigsoundbank.com/s1602.html | CC0 (BigSoundBank / Joseph Sardin) |
| `body_fall_1` | a soft settle (52.5 s) | https://bigsoundbank.com/s2452.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boiling_water` | the hot vent bubbles (47.5 s) | https://bigsoundbank.com/s0149.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_2` | the snail waves (2x, 37.9 to 45.4 s) | https://bigsoundbank.com/s2277.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_4` | the snail waves (2x, 35.7 to 43.6 s); the snail waves goodbye (2x, 67.1 to 70.3 s) | https://bigsoundbank.com/s2279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `boing_6` | a cheerful boing: the friendly anglerfish swims out (40.5 s) | https://bigsoundbank.com/s2281.html | CC0 (BigSoundBank / Joseph Sardin) |
| `candle_sparkle_1` | tiny sparkles twinkle round the jellyfish (3x, 27.9 to 32.6 s) | https://bigsoundbank.com/s1278.html | CC0 (BigSoundBank / Joseph Sardin) |
| `candle_sparkle_2` | tiny sparkles twinkle round the jellyfish (2x, 29.0 to 31.9 s) | https://bigsoundbank.com/s1279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cave_soundscape_1` | the deep quiet of the midnight zone (20.4 s) | https://bigsoundbank.com/s2135.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_1` | the lantern fish switch on (tiny chimes) (17.2 s); a jellyfish lights up (a glass chime) (26.7 s); the treasure chest sparkles (52.2 s); ALL THE LIGHTS: the chime that starts the cascade (55.0 s) | https://bigsoundbank.com/s2087.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_3` | the lantern fish switch on (tiny chimes) (17.9 s); a jellyfish lights up (a glass chime) (30.0 s); another light twinkles on (3x, 55.9 to 58.4 s); the surface: a warm chime on the last chord (65.8 s) | https://bigsoundbank.com/s2089.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_1` | the lantern fish switch on (tiny chimes) (16.9 s); the lamp's soft glow (21.1 s); a jellyfish lights up (a glass chime) (28.3 s); another light twinkles on (3x, 55.5 to 58.0 s) | https://bigsoundbank.com/s2079.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_3` | the lantern fish switch on (tiny chimes) (17.5 s); a pale jellyfish lights up in the twilight (17.3 s); the torch lights the submarine (a chime) (42.6 s); another light twinkles on (3x, 56.3 to 58.8 s); a light goes out (a falling chime) (4x, 59.8 to 61.9 s) | https://bigsoundbank.com/s2081.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cluster_chimes` | ALL THE LIGHTS: a burst of gold stars (55.0 s) | https://bigsoundbank.com/s2687.html | CC0 (BigSoundBank / Joseph Sardin) |
| `creaking_door_1` | a toy chest lid creaks (52.1 s) | https://bigsoundbank.com/s0302.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_1` | the fish school flutters past (9.1 s) | https://bigsoundbank.com/s1384.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_2` | the fish school flutters past (12.3 s) | https://bigsoundbank.com/s1385.html | CC0 (BigSoundBank / Joseph Sardin) |
| `drops_3` | the bottle bobs by (2x, 35.1 to 42.1 s) | https://bigsoundbank.com/s1386.html | CC0 (BigSoundBank / Joseph Sardin) |
| `glockenspiel` | ALL THE LIGHTS: sparkle (a struck glockenspiel chord, tuned) (55.1 s) | https://bigsoundbank.com/s0920.html | CC0 (BigSoundBank / Joseph Sardin) |
| `gulls_harbor` | gulls over the sea (0.0 s) | https://bigsoundbank.com/s2573.html | CC0 (BigSoundBank / Joseph Sardin) |
| `lock` | the submarine's headlamp clicks on (21.0 s); the headlamp blinks off (41.3 s); the headlamp clicks back on (45.7 s) | https://bigsoundbank.com/s0191.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sea_tern` | a tern calls (4.0 s); a gull calls at sunset (66.5 s) | https://bigsoundbank.com/s0267.html | CC0 (BigSoundBank / Joseph Sardin) |
| `small_waves_ocean` | gentle waves on the sunny sea (0.0 s) | https://bigsoundbank.com/s1046.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sparkling_water` | a shimmer of tiny lights (16.9 s) | https://bigsoundbank.com/s0230.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_big_1` | the submarine dives in: a splash (5.7 s) | https://bigsoundbank.com/s1519.html | CC0 (BigSoundBank / Joseph Sardin) |
| `splash_big_2` | the submarine pops out of the sea (65.9 s) | https://bigsoundbank.com/s1520.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steam_hiss_1` | warm steam (47.9 s) | https://bigsoundbank.com/s0227.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_mud` | the submarine settles on the sand (soft thump) (52.4 s) | https://bigsoundbank.com/s0495.html | CC0 (BigSoundBank / Joseph Sardin) |
| `swirl_water` | the turtle paddles by (a slow swirl) (8.2 s) | https://bigsoundbank.com/s0192.html | CC0 (BigSoundBank / Joseph Sardin) |
| `thunder_8` | a low warm rumble from the vent (47.1 s) | https://bigsoundbank.com/s3181.html | CC0 (BigSoundBank / Joseph Sardin) |
| `tibetan_bowl_1` | ALL THE LIGHTS: a singing bowl swells (55.0 s) | https://bigsoundbank.com/s1109.html | CC0 (BigSoundBank / Joseph Sardin) |
| `tibetan_bowl_2` | the lure lights up (a warm bowl) (42.3 s) | https://bigsoundbank.com/s1110.html | CC0 (BigSoundBank / Joseph Sardin) |
| `tibetan_bowl_3` | the first closing chord: the torch shows only a little (63.0 s) | https://bigsoundbank.com/s2553.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_duck` | the rubber duck squeaks as it hops (2x, 2.6 to 3.1 s); the rubber duck greets the submarine (2x, 66.1 to 66.6 s) | https://bigsoundbank.com/s0364.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_squeal_1` | the squid squeaks (34.2 s) | https://bigsoundbank.com/s3331.html | CC0 (BigSoundBank / Joseph Sardin) |
| `underwater` | under the water (a soft hum) (6.4 s) | https://bigsoundbank.com/s3430.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_bubble_2` | the fish school flutters past (2x, 7.4 to 11.0 s); one slow bubble (24.0 s); a bubble pop as it blinks its spots (35.5 s); the lure dims with a bubble pop (45.9 s); a questioning bubble (62.9 s) | https://bigsoundbank.com/s0183.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_bubbles` | a ring of bubbles (5.8 s); a burble as it glows (3x, 26.8 to 30.1 s); a bubble giggle (43.4 s) | https://bigsoundbank.com/s0150.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_10` | it glides out of the dark (39.8 s) | https://bigsoundbank.com/s1798.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_4` | the squid zips away (39.4 s) | https://bigsoundbank.com/s1796.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_5` | the squid zips in (33.6 s) | https://bigsoundbank.com/s1797.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_long_1` | the water hums lower as the sun fades (13.3 s) | https://bigsoundbank.com/s0572.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_long_2` | the submarine rises (63.8 s) | https://bigsoundbank.com/s0573.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wine_stopper_3` | the bottle's cork bobs (2x, 33.9 to 40.9 s); words pop in: what lives in the deep sea? (0.3 s); words pop in: sunlight zone (5.8 s); words pop in: twilight zone (13.8 s); words pop in: midnight zone (20.9 s); words pop in: glow! (26.9 s); words pop in: hot vents (47.4 s); words pop in: most is unseen (59.9 s); words pop in: what else is down there? (66.0 s) | https://bigsoundbank.com/s1719.html | CC0 (BigSoundBank / Joseph Sardin) |

## Stand-ins (honest)
- The submarine's headlamp click is the click of a real lock, shortened: there is no recording of a little submarine.
- The whale's spout is a real soft blow (an exhale), slowed and low-passed, far away: there is no recording of a whale.
- The squid's squeak is a small toy squeal; its zip is a real whoosh. No recording of a squid exists in the bank.
- The anglerfish's cheerful boing is a real soft boing, tuned to the music; the lure's glow is a singing bowl swell with real chimes.
- The hot vent is boiling water, low-passed, a very low rolling thunder and a breath of steam: there is no recording of a hydrothermal vent.
- The sub settling on the sand is a slowed soft mud step and a slowed body fall (no recording of a small submarine landing).
- The turtle's paddle is a slow swirl of real water; the fish school is real water drops and bubbles; the bottle's cork is a wine stopper slowed.
- The boat's far bell is a real church bell striking once, low-passed and far away; gulls and the tern are real recordings.
- The glockenspiel is a real struck chord tuned to the orchestra's pitch classes at the climax (a recording shifted, not played in the key).
- Words pop in with a wine stopper's pop.

## Rebuild
`python3 films/cutaway/kids/deep-sea/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
