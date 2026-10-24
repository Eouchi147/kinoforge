# Sound of the shooting star film (Little Big Questions)

A SILENT 68.4 s film for children aged 6 to 8: no narration. The music is a real orchestral recording; every event on
screen has a real recorded sound effect. Built by `audio/make_audio.py` (deterministic: numpy, scipy, soundfile, ffmpeg).
`audio/mix.m4a` is committed (the render needs it); `audio/mix.wav` is ignored; `audio/mix.json` (measurements, every
recording and where it is used, the music edit, the event table, the timelines) is kept.

**Music credit (for the description of the video):** Music: Edvard Grieg, Anitra's Dance (Peer Gynt Suite No. 1), performed by the Musopen Symphony (musopen.org), public domain.

## Result (measured on the decoded AAC, `ffmpeg ebur128=peak=true`)
- 68.40 s, 48 kHz stereo AAC 256k, -16.1 LUFS integrated (target -16), true peak -1.90 dBTP (limit -1.5 dBTP), loudness range 9.4 LU.
- The loudest limiter dip is 5.8 dB at 24.2 s; the true-peak loop re-encodes until the decoded AAC is under the limit.
- Every spot is placed from the picture's event table (`szevents.py`, zero offset by construction). On the rendered effects bus alone, 49 of 63 percussive spots
  stand out by 3 dB or more within 30 ms before to 150 ms after their event; the rest are quiet details sitting under the fire or a neighbouring sound (listed in `mix.json`, `landing_check`).
- Nobody has listened to it yet: the build cannot hear. Levels were set by measurement (below) and by rules, then must be
  checked by ear on a phone speaker, a tablet and headphones before anything is published.

## The music edit (as `beats.json` says)
Grieg, Peer Gynt Suite No. 1, III. Anitra's Dance, Musopen Symphony (Musopen), Public domain (Wikimedia Commons record). Source: https://commons.wikimedia.org/wiki/File:Grieg_-_Peer_Gynt_Suite_No._1,_Op._46_-_III._Anitra%27s_Dance_(Musopen_Symphony).flac. Asset: Eouchi147/rc-render release music: grieg-anitra-musopen.flac (+ .licence.json).
Cut on the bar lines (one bar = 1.3065 s) into four pieces, joined by triangular (linear in, linear out) cross-fades:
recording 0:00 to 0:03.6 (the introduction, film 0 to 3.6), 0:05.18 to 0:30.05 (the theme, film 3.6 to 28.47, a 0.5 s fade at 3.6),
1:28.84 to 2:00.19 (the plucked build and its full-orchestra peak, film 27.16 to 58.51, a one-bar fade from 27.16), 3:46.06 to the end
(the dance's own ending, film 57.2 to 68.4, a one-bar fade from 57.2; its bright chord is at film 59.55). The big reveal lands on the loud
hit of the peak (film 41.9). A slow level rider (zero-phase, 1 s Gaussian smoothing, ratio 3.0, gain between +4.0
and +9.0 dB) lifts the whispering parts and eases the peak so the film sits near -16 LUFS; the notes keep their own shape.

## Where the effects come from
The studio's CC0 bank: release `sfx-bank` of `Eouchi147/rc-render` (BigSoundBank, Joseph Sardin, CC0; each sound's page was
checked to say CC0 by the bank workflow). Event times are read from `szevents.py` and `beats.json` at build time: a re-timed picture
re-times the sound. Tonal sounds (chimes, triangle, glockenspiel, bowl, boings, metallophone) are tuned by resampling to the pitch classes the
orchestra is playing at that moment (read from the recording), so they ring with the chord and never against it. Beds (fire, crickets, evening birds,
air) are chosen by low crest factor (no stray knock) and set by RMS against the music; every spot is set by its peak in dB against the music's local RMS.

| Recording | Used as | Source page | Licence |
| --- | --- | --- | --- |
| `boing_6` | the snail lifts its tiny telescope (a little boing) (0.9 s) | https://bigsoundbank.com/s2281.html | CC0 (BigSoundBank / Joseph Sardin) |
| `brush_wood` | dad holds a marshmallow on a stick to the fire (a soft swish) (3.6 s) | https://bigsoundbank.com/s1106.html | CC0 (BigSoundBank / Joseph Sardin) |
| `candle_sparkle_1` | the first stars wink on (3x, 1.0 to 3.2 s); the pebble and the rock glint together (19.6 s); a speck of space dust glints (tiny dust falls every day) (4x, 47.1 to 50.9 s) | https://bigsoundbank.com/s1278.html | CC0 (BigSoundBank / Joseph Sardin) |
| `candle_sparkle_2` | sparkle in its wake (7.7 s); sparks shed from the streak (7x, 42.4 to 44.5 s) | https://bigsoundbank.com/s1279.html | CC0 (BigSoundBank / Joseph Sardin) |
| `carrot_crunch` | the snail munches its wish (a lettuce crunch) (3x, 54.5 to 56.4 s) | https://bigsoundbank.com/s1594.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_1` | the window opens (chimes) (9.7 s); the window opens on the rock (chimes) (18.4 s); the last bright chord (chimes) (59.6 s) | https://bigsoundbank.com/s2087.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_butterfly_3` | she holds the pebble up to the sky (a small chime) (15.8 s); the trail fades away (a long soft chime) (44.0 s) | https://bigsoundbank.com/s2089.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_1` | the little streak sings (chimes tuned to the music) (7.6 s); sparkles drift down and melt (chimes) (4x, 42.8 to 44.8 s); the last streak sings (a soft chime) (66.7 s) | https://bigsoundbank.com/s2079.html | CC0 (BigSoundBank / Joseph Sardin) |
| `chimes_dream_3` | the star is a giant, calm ball of fire (a slow glow of chimes) (13.3 s); the ring appears in the sky (a small chime) (29.0 s); everyone makes a wish (a hushed chime) (49.7 s) | https://bigsoundbank.com/s2081.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cloth` | everyone looks up (cloth rustle) (7.8 s); they cuddle close (cloth) (57.6 s) | https://bigsoundbank.com/s0013.html | CC0 (BigSoundBank / Joseph Sardin) |
| `cluster_chimes` | METEOR! a burst of gold stars (chimes, tuned) (41.9 s) | https://bigsoundbank.com/s2687.html | CC0 (BigSoundBank / Joseph Sardin) |
| `dreamcatcher` | wish stars lift from their heads (a faint shimmer) (50.6 s) | https://bigsoundbank.com/s0040.html | CC0 (BigSoundBank / Joseph Sardin) |
| `evening_birds` | the last evening birds (0.0 s) | https://bigsoundbank.com/s1859.html | CC0 (BigSoundBank / Joseph Sardin) |
| `field_cricket` | crickets as the night comes (louder in the breath of stillness) (3.0 s) | https://bigsoundbank.com/s1020.html | CC0 (BigSoundBank / Joseph Sardin) |
| `fire_branching_1` | a crackle from the fire (11x, 2.2 to 64.2 s) | https://bigsoundbank.com/s0987.html | CC0 (BigSoundBank / Joseph Sardin) |
| `fireplace_1` | the campfire crackles all film (0.0 s) | https://bigsoundbank.com/s0030.html | CC0 (BigSoundBank / Joseph Sardin) |
| `glockenspiel` | METEOR! sparkle (a struck glockenspiel chord, tuned) (42.0 s) | https://bigsoundbank.com/s0920.html | CC0 (BigSoundBank / Joseph Sardin) |
| `metallophone` | she aims the telescope (a tiny ring) (9.3 s); the rock drifts closer (accent 1 of 3 on the bar line) (21.9 s); the rock drifts closer (accent 2 of 3 on the bar line) (23.2 s); the rock drifts closer (accent 3 of 3 on the bar line) (24.5 s) | https://bigsoundbank.com/s3067.html | CC0 (BigSoundBank / Joseph Sardin) |
| `owl_tawny` | the owl turns its head (a soft hoot) (8.0 s); the owl hoots softly goodnight (61.0 s) | https://bigsoundbank.com/s0429.html | CC0 (BigSoundBank / Joseph Sardin) |
| `paper` | a lettuce leaf floats in, rocking (paper-light rustle) (51.7 s) | https://bigsoundbank.com/s0785.html | CC0 (BigSoundBank / Joseph Sardin) |
| `plant_cartoon_1` | the leaf lands beside the snail (53.9 s) | https://bigsoundbank.com/s1950.html | CC0 (BigSoundBank / Joseph Sardin) |
| `rusk_crunch` | the snail munches its wish (a lettuce crunch) (3x, 55.0 to 56.8 s) | https://bigsoundbank.com/s0407.html | CC0 (BigSoundBank / Joseph Sardin) |
| `sigh_nose` | everyone gasps: oh (a soft breath) (41.7 s); a happy sigh (58.1 s) | https://bigsoundbank.com/s1404.html | CC0 (BigSoundBank / Joseph Sardin) |
| `steps_pebbles` | she picks up a pebble (14.4 s); she sets the pebble back (17.6 s); the rock tumbles (a tiny tick) (4x, 19.0 to 20.6 s) | https://bigsoundbank.com/s0839.html | CC0 (BigSoundBank / Joseph Sardin) |
| `tibetan_bowl_2` | METEOR! a singing bowl blooms with the climax (41.9 s) | https://bigsoundbank.com/s1110.html | CC0 (BigSoundBank / Joseph Sardin) |
| `toy_squeal_1` | the little brother squeals with delight (7.9 s); the little brother cheers (42.0 s) | https://bigsoundbank.com/s3331.html | CC0 (BigSoundBank / Joseph Sardin) |
| `triangle_2` | the star glints in the window (a triangle) (10.2 s); the twin glint (a triangle) (19.6 s); the ring in the sky (a triangle) (32.0 s); METEOR! a soft triangle (41.9 s); the dance's last bright chord (a triangle) (59.5 s) | https://bigsoundbank.com/s1688.html | CC0 (BigSoundBank / Joseph Sardin) |
| `water_bubble_2` | the round window opens (a soft bubble) (9.6 s); the window closes (a soft bubble, reversed) (2x, 15.8 to 46.4 s); the round window opens again (a soft bubble) (18.2 s); the window shows the layers of the air (a soft bubble) (26.0 s) | https://bigsoundbank.com/s0183.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_10` | a small streak zips across the sky (7.9 s) | https://bigsoundbank.com/s1798.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_4` | one last small streak (66.9 s) | https://bigsoundbank.com/s1796.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_8` | the rock rushes in (a reversed whoosh crossing the sky) (41.9 s) | https://bigsoundbank.com/s1801.html | CC0 (BigSoundBank / Joseph Sardin) |
| `whoosh_long_2` | it enters the air (a long, rising rush) (28.1 s) | https://bigsoundbank.com/s0573.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_inside_1` | a long breath of air as it nears (22.1 s) | https://bigsoundbank.com/s1714.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_plain` | a soft night breeze (14.0 s) | https://bigsoundbank.com/s0595.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_whistle_1` | the air sings past as it glows hotter (28.4 s) | https://bigsoundbank.com/s0147.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wind_whistle_2` | the air screams past, gently (a reversed whistle) (41.8 s) | https://bigsoundbank.com/s0155.html | CC0 (BigSoundBank / Joseph Sardin) |
| `wine_stopper_3` | words pop in: what is a shooting star? (0.3 s); words pop in: not a star (9.2 s); words pop in: a tiny space rock (18.3 s); words pop in: meteor! (41.9 s); words pop in: will you see one tonight? (61.9 s) | https://bigsoundbank.com/s1719.html | CC0 (BigSoundBank / Joseph Sardin) |

## Stand-ins (honest)
- The streaks are real whooshes (reversed so they build to the bright instant) with real chimes, a triangle and a glockenspiel chord tuned to the music: the bank has no recording of a meteor, and there is none to make (it is silent in space and far away).
- The pebble, the rock tumbling and the marshmallow stick are a pebble-walking recording, a few of its ticks, and a soft wooden brush: stand-ins for small things.
- The sparks from the fire and the streak are tiny recorded sparkles from a candle, faint and short.
- The lettuce crunch is a raw carrot and a rusk crunch, a little higher and small: there is no recording of a snail, and a snail would not be heard.
- The owl is a real tawny owl's hoots (cut to short soft ones, low-passed, a little way off).
- The family's gasp and happy sigh are a soft breath through the nose; the little brother's squeal is a squeaky toy (no recorded children).
- The window opening is a soft water bubble, closing is the same reversed; the shimmer of the wish stars is a dreamcatcher's faint jingle.
- Words pop in with a wine stopper's pop.

## Rebuild
`python3 films/cutaway/kids/shooting-star/audio/make_audio.py` (about a minute; it downloads the recording and the bank once).
`$MUSIC_FLAC` and `$SFX_BANK` point at local copies. Then check by ear and fix levels in the `design()` table of the script.
