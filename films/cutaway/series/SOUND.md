# Sound of the Cutaway showcase series

Sam (22 Oct 2026): "no voice, just nature sounds (try to use the free 2.5gig sound bank we have already)", then (22:54
Toronto) "I said no music but actually I would like ambient, peaceful subtle music. I need artistic, cinema direction,
self contained." So: no voice; every effect and ambience is a real recording from BigSoundBank (Joseph Sardin), all
**CC0** (public domain; each sound page was checked to say "CC0" by the bank workflow), placed only on what we see or
feel; and under it a quiet score per film (long warm pads, one sparse solo voice for the place), its loudest moment
10 dB under the nature's loudest, swelling only at the film's turn and resolving at the end. Silence is still a tool
(the meadow falls quiet, music too, when the hawk's shadow comes).

- **The score:** `music_kit.py`, written note by note in each film's `make_audio.py` (`score()`), played by the free score
  engine's instruments (`films/lib/score/voices.py`): VSCO-2 CE samples (CC0) when the sample folder is found
  (`$SCORE_SAMPLES`, see `films/lib/score/README.md`; this build found it), else the engine's own synthesis. The gold
  mine's dulcimer is a synthesised Karplus-Strong pluck. No paid service.

- **The bank:** release `sfx-bank` of `Eouchi147/rc-render`: `sfx-bank.tar` (197 recordings as 48 kHz stereo 24-bit FLAC:
  the 138 BigSoundBank rows of the Dark Corners bank `dark/assets.csv` plus 59 extras in `sfx/bank_extra.txt`) and
  `sfx-bank.csv` (name, source page, licence, duration, integrated loudness, true peak). Built by the workflow
  `.github/workflows/sfx-bank.yml` (script `sfx/bank.sh`, run by hand) on a GitHub runner, because chat containers
  cannot reach bigsoundbank.com. Audio never goes into git.
- **The mixes:** `<film>/audio/make_audio.py` with the shared kit `audio_kit.py` (numpy, scipy, soundfile, ffmpeg; free,
  deterministic). Each writes `audio/mix.m4a` (20.0 s, 48 kHz stereo AAC 256k, about -16 LUFS integrated, peaks under
  -1.5 dBFS after decoding, fade in 0.8 s and out 1.5 s) and `audio/mix.json` (measurements and every recording used,
  with where). The kit finds the bank in `$SFX_BANK`, else `~/.cache/kinoforge/sfx-bank`, else downloads the archive once.
- **Events:** each script's `EV` table holds the film's event times; update it from the film's NOTES.md event table and
  run the script again (about 10 s).
- **Honest notes:** `cave_1`, `cave_2` (BigSoundBank 2135, 2136) are soundscapes the author assembled from his own real
  recordings (drops, rain, reverb), marked "idealized" on their pages. Some sounds stand in for what has no recording
  in the bank: a slowed boiling pot and slowed thunder for the magma, slowed ice cracks for rock cracking, a pigeon's
  and a small bird's wings for the hawk and the flock (no hawk call: the hawk is a shadow), a wheelbarrow and a steam
  wagon's rumble for the mine cart, mud steps for the ants and the rabbits' dives. The fox and the rabbits are silent.


## The River Through Time (`river-time`)

Brook, wind and songbirds; time races: wind rising, the brook becomes a river, a rockfall, grit as each fossil is bared; today: rim wind, the river far below, a raven, the hiker's steps. Measured: -16.1 LUFS, peak -2.28 dBFS, 20.0 s. Score: key D, cello, harp, viola, violin; turn: time slows, 12.2 to 14.4 s; its loudest 3 s sit 10.0 dB under the nature's.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `crows_1` | a raven over the canyon at 15.60 s | https://bigsoundbank.com/s0754.html |
| `evening_birds` | bed 13.7-20.0 s | https://bigsoundbank.com/s1859.html |
| `fall_of_stone` | a small rockfall at 9.50 s; grit trickles as a fossil is bared at 7.99 s; grit trickles as a fossil is bared at 11.31 s; grit trickles as a fossil is bared at 12.11 s | https://bigsoundbank.com/s1022.html |
| `forest` | bed 0.0-6.3 s | https://bigsoundbank.com/s0100.html |
| `mountain_stream_1` | bed 3.2-20.0 s; bed 5.8-14.4 s; bed 13.7-20.0 s | https://bigsoundbank.com/s2754.html |
| `small_stream_4` | bed 0.0-6.4 s | https://bigsoundbank.com/s1354.html |
| `steps_gravel_1` | hiker steps at 14.91 s; hiker steps at 15.22 s; hiker steps at 15.54 s; hiker steps at 15.85 s; hiker steps at 16.16 s; hiker steps at 16.48 s; hiker steps at 16.79 s; hiker steps at 17.10 s; hiker steps at 17.41 s; hiker steps at 17.73 s; hiker steps at 18.04 s | https://bigsoundbank.com/s0510.html |
| `wind_plain` | bed 0.0-20.0 s | https://bigsoundbank.com/s0595.html |

## Under the City (`under-the-city`)

Street at dusk with a bus and steam, water in pipes and sewer, drips, the rat, the metro, stillness in old stone, the city faintly back with a far train. Measured: -16.18 LUFS, peak -1.88 dBFS, 20.0 s. Score: key A minor to C, cello, harp, viola, violin; turn: the metro, 10.74 s; its loudest 3 s sit 10.0 dB under the nature's.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `cave_2` | bed 11.3-20.0 s | https://bigsoundbank.com/s2136.html |
| `drops_3` | slow drip on the Roman floor at 13.90 s | https://bigsoundbank.com/s1386.html |
| `drops_4` | drip into the sewer at 6.70 s; drip into the sewer at 8.40 s; drip into the sewer at 10.10 s | https://bigsoundbank.com/s1387.html |
| `evening_birds` | bed 0.0-5.0 s | https://bigsoundbank.com/s1859.html |
| `fall_of_stone` | a trickle of grit at 12.40 s | https://bigsoundbank.com/s1022.html |
| `london_bus` | bus passes left to right at 0.20 s; faint bus on top at 15.50 s | https://bigsoundbank.com/s0644.html |
| `mouse_screams` | rat squeaks at 8.40 s | https://bigsoundbank.com/s0459.html |
| `paris_by_night` | bed 0.0-6.0 s; bed 3.5-7.5 s; bed 15.3-20.0 s | https://bigsoundbank.com/s0680.html |
| `pencil_2` | rat claws at 6.90 s; rat claws at 7.02 s; rat claws at 7.14 s; rat claws at 7.26 s; rat claws at 7.38 s; rat claws at 7.50 s; rat claws at 7.62 s; rat claws at 7.74 s; rat bolts at 10.00 s; rat bolts at 10.08 s; rat bolts at 10.16 s; rat bolts at 10.24 s; rat bolts at 10.32 s; rat bolts at 10.40 s | https://bigsoundbank.com/s3233.html |
| `sewer_1` | bed 4.5-10.9 s | https://bigsoundbank.com/s0607.html |
| `steam_hiss_1` | manhole steam at 0.30 s | https://bigsoundbank.com/s0227.html |
| `train_passage_1` | metro roars past at 8.74 s; rumble before the train at 9.60 s; second train far below at 16.10 s | https://bigsoundbank.com/s0900.html |

## The Hidden Meadow (`hidden-meadow`)

Birdsong, crickets and bees above; below, muffled, the mole, the fox cubs and the ants; a hush, two slow wing beats, the rabbits run and land; the meadow breathes again; flute and pizzicato that fall silent for the hawk. Measured: -16.1 LUFS, peak -1.99 dBFS, 20.0 s. Score: key G, cello, flute, pizz, viola, violin; turn: the hawk, 12.7 to 16.4 s (the music falls away); its loudest 3 s sit 10.0 dB under the nature's.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `birds_waking_3` | bed 0.0-20.0 s; bed 5.8-12.7 s | https://bigsoundbank.com/s0999.html |
| `bumblebee_1` | a bee crosses close at 1.50 s | https://bigsoundbank.com/s1000.html |
| `bumblebee_2` | a bee crosses close at 4.00 s | https://bigsoundbank.com/s1001.html |
| `cloth` | straw rustles at 6.71 s; straw rustles at 9.31 s; straw rustles at 11.91 s | https://bigsoundbank.com/s0013.html |
| `countryside` | bed 5.8-12.7 s | https://bigsoundbank.com/s0097.html |
| `dig_shovel` | a dirt trickle at 7.30 s; a dirt trickle at 9.60 s; into the burrow at 13.86 s; into the burrow at 14.07 s | https://bigsoundbank.com/s1305.html |
| `field_cricket` | bed 0.0-20.0 s | https://bigsoundbank.com/s1020.html |
| `flight_bird_1` | slow wing beat overhead at 13.70 s | https://bigsoundbank.com/s2891.html |
| `flight_pigeon` | slow wing beat overhead at 13.08 s | https://bigsoundbank.com/s0840.html |
| `steps_mud` | the mole digs (paw strokes) at 6.20 s; the mole digs (paw strokes) at 6.65 s; the mole digs (paw strokes) at 7.11 s; the mole digs (paw strokes) at 7.56 s; the mole digs (paw strokes) at 8.02 s; the mole digs (paw strokes) at 8.47 s; the mole digs (paw strokes) at 8.93 s; the mole digs (paw strokes) at 9.38 s; the mole digs (paw strokes) at 9.84 s; the mole digs (paw strokes) at 10.29 s; the mole digs (paw strokes) at 10.75 s; a fox cub lands on straw at 6.68 s; a fox cub lands on straw at 9.28 s; a fox cub lands on straw at 11.88 s; ants scratching at 7.50 s; a rabbit bolts at 13.45 s; a rabbit bolts at 13.63 s; safe in the warren at 15.10 s; safe in the warren at 15.38 s | https://bigsoundbank.com/s0495.html |
| `wind_plain` | bed 0.0-20.0 s; a gust as the shadow passes at 13.70 s | https://bigsoundbank.com/s0595.html |

## Reef and Wreck (`reef-and-wreck`)

Surf, terns, the boat and the splash; underwater hush, reef crackle and her breath every 1.6 s; the school turns; the hull creaks; a quiet oceanic score with a soft bell for the gold. Measured: -16.16 LUFS, peak -1.98 dBFS, 20.0 s. Score: key E, cello, glock, harp, viola, violin; turn: the school turns, 10.2 s; the gold, 17 s; its loudest 3 s sit 10.0 dB under the nature's.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `bubbles_burst` | first bubbles at 5.80 s; her regulator exhales at 6.95 s; her regulator exhales at 8.55 s; her regulator exhales at 10.15 s; her regulator exhales at 11.75 s; her regulator exhales at 13.35 s; her regulator exhales at 14.95 s; her regulator exhales at 16.55 s; her regulator exhales at 18.15 s; her regulator exhales at 19.75 s | https://bigsoundbank.com/s1074.html |
| `cloth` | a rustle of gear at 4.90 s | https://bigsoundbank.com/s0013.html |
| `creaking_door_2` | the boat creaks as she tips back at 4.80 s; the hull creaks at 13.80 s; the hull creaks at 16.90 s | https://bigsoundbank.com/s3205.html |
| `sea_tern` | bed 0.0-6.0 s | https://bigsoundbank.com/s0267.html |
| `small_waves_ocean` | bed 0.0-20.0 s; bed 5.5-20.0 s | https://bigsoundbank.com/s1046.html |
| `splash_big_1` | the diver splashes in at 5.35 s | https://bigsoundbank.com/s1519.html |
| `splash_small_1` | water laps the hull at 2.00 s; water laps the hull at 2.90 s; water laps the hull at 3.80 s; water laps the hull at 4.70 s | https://bigsoundbank.com/s1529.html |
| `underwater` | bed 5.5-20.0 s | https://bigsoundbank.com/s3430.html |
| `water_bubbles` | bed 7.0-20.0 s | https://bigsoundbank.com/s0150.html |
| `whoosh_3` | the school turns (a rush of water) at 10.05 s | https://bigsoundbank.com/s1795.html |
| `whoosh_5` | a slow stroke through water at 10.50 s; a slow stroke through water at 13.10 s; a slow stroke through water at 15.90 s; a slow stroke through water at 17.30 s | https://bigsoundbank.com/s1797.html |

## The Gold Mine (`gold-mine`)

Night wind, crickets, owl and the miner's steps; cave air, drips, lanterns; cart, ladder, diggers; three blows, the last rings with sparks; bats shiver, burst past the lens and pour out toward the moon. Measured: -16.11 LUFS, peak -1.62 dBFS, 20.0 s. Score: key D minor, cello, viola, violin, dulcimer (synthesised pluck); turn: the gold, 11.0 s; its loudest 3 s sit 10.0 dB under the nature's.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `anvil_1` | bright click at 8.61 s; bright click at 9.81 s; the strike rings: gold at 11.01 s | https://bigsoundbank.com/s3589.html |
| `bats` | bats squeak as they drop at 11.45 s; bats pour out toward the moon at 14.15 s | https://bigsoundbank.com/s0458.html |
| `campaign_night_1` | bed 0.0-20.0 s | https://bigsoundbank.com/s0110.html |
| `candle_sparkle_2` | bed 6.0-14.0 s | https://bigsoundbank.com/s1279.html |
| `cave_1` | bed 5.8-14.5 s | https://bigsoundbank.com/s2135.html |
| `cloth` | bats shiver at 11.00 s | https://bigsoundbank.com/s0013.html |
| `drops_1` | a drip at 6.70 s; a drip at 8.10 s; a drip at 9.30 s; a drip at 10.90 s; a drip at 12.40 s; a drip at 13.60 s | https://bigsoundbank.com/s1384.html |
| `fall_of_stone` | a scatter of chips at 11.06 s | https://bigsoundbank.com/s1022.html |
| `fire_foley` | sparks at 11.02 s | https://bigsoundbank.com/s3322.html |
| `flight_bird_1` | wings burst at 11.85 s; dense wing flutter, thinning at 14.62 s; dense wing flutter, thinning at 15.88 s; dense wing flutter, thinning at 17.14 s | https://bigsoundbank.com/s2891.html |
| `flight_bird_2` | wings burst at 12.25 s; dense wing flutter, thinning at 15.04 s; dense wing flutter, thinning at 16.30 s; dense wing flutter, thinning at 17.56 s | https://bigsoundbank.com/s2892.html |
| `flight_pigeon` | wings burst at 11.50 s; wings burst at 12.75 s; dense wing flutter, thinning at 14.20 s; dense wing flutter, thinning at 15.46 s; dense wing flutter, thinning at 16.72 s | https://bigsoundbank.com/s0840.html |
| `hammer_concrete` | diggers' picks at 6.05 s; diggers' picks at 7.20 s; diggers' picks at 8.35 s; diggers' picks at 9.50 s; diggers' picks at 10.65 s; diggers' picks at 11.80 s; diggers' picks at 12.95 s; diggers' picks at 6.45 s; diggers' picks at 7.85 s; diggers' picks at 9.25 s; diggers' picks at 10.65 s; diggers' picks at 12.05 s; diggers' picks at 13.45 s; pick strikes quartz at 8.60 s; pick strikes quartz at 9.80 s; pick strikes quartz at 11.00 s | https://bigsoundbank.com/s1108.html |
| `iron_bar_fall_2` | the cart stops: a clunk at 10.48 s | https://bigsoundbank.com/s0235.html |
| `owl_tawny` | an owl on the mountain at 2.00 s | https://bigsoundbank.com/s0429.html |
| `squeaky_barrow_4` | cart wheels on the rails at 1.50 s | https://bigsoundbank.com/s2519.html |
| `squeaky_steps_1` | the lantern handle creaks at 2.30 s; ladder creaks at 5.60 s; ladder creaks at 6.38 s; ladder creaks at 7.16 s; ladder creaks at 7.94 s; ladder creaks at 8.72 s; ladder creaks at 9.50 s; ladder creaks at 10.28 s; ladder creaks at 11.06 s; ladder creaks at 11.84 s | https://bigsoundbank.com/s3440.html |
| `steam_between_wagons` | cart rumble at 1.50 s | https://bigsoundbank.com/s3020.html |
| `steps_gravel_1` | the miner walks in at 0.60 s; the miner walks in at 1.15 s; the miner walks in at 1.70 s; the miner walks in at 2.25 s; the miner walks in at 2.80 s; the miner walks in at 3.35 s; the miner walks in at 3.90 s; the miner walks in at 4.45 s | https://bigsoundbank.com/s0510.html |
| `whoosh_4` | bats pass the lens at 12.60 s | https://bigsoundbank.com/s1796.html |
| `wind_plain` | bed 0.0-20.0 s | https://bigsoundbank.com/s0595.html |

## The Sleeping Volcano (`sleeping-volcano`)

Waves, gulls and a far fumarole; the chamber: mud-pot boil and a felt rumble growing, rock cracks, the hiss thickening, a flock lifting; a beat of quiet at dusk, then the boom, fire, bombs and the sea hissing under the lava; deep string drones that swell at the eruption and settle. Measured: -16.34 LUFS, peak -1.79 dBFS, 20.0 s. Score: key C, cello, harp, viola, violin; turn: the eruption, 14.2 s; its loudest 3 s sit 10.0 dB under the nature's.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `big_broth` | bed 4.0-20.0 s | https://bigsoundbank.com/s0491.html |
| `crows_1` | alarm calls at 11.20 s | https://bigsoundbank.com/s0754.html |
| `fall_of_stone` | a short rock tumble at 14.35 s; a bomb thuds down at 15.40 s; a bomb thuds down at 16.50 s; a bomb thuds down at 18.30 s | https://bigsoundbank.com/s1022.html |
| `fire_branching_1` | bed 14.7-18.2 s | https://bigsoundbank.com/s0987.html |
| `fireplace_2` | bed 14.4-20.0 s | https://bigsoundbank.com/s0031.html |
| `flight_bird_1` | a flock takes off at 11.25 s | https://bigsoundbank.com/s2891.html |
| `flight_bird_2` | a flock takes off at 11.10 s | https://bigsoundbank.com/s2892.html |
| `flight_pigeon` | a flock takes off at 10.90 s | https://bigsoundbank.com/s0840.html |
| `forest` | bed 0.0-6.8 s | https://bigsoundbank.com/s0100.html |
| `gulls_harbor` | gulls circling at 0.30 s | https://bigsoundbank.com/s2573.html |
| `ice_crack_1` | rock cracks as magma climbs at 7.80 s; rock cracks as magma climbs at 12.70 s | https://bigsoundbank.com/s2205.html |
| `ice_crack_2` | rock cracks as magma climbs at 9.40 s | https://bigsoundbank.com/s2206.html |
| `ice_crack_3` | rock cracks as magma climbs at 11.30 s | https://bigsoundbank.com/s2207.html |
| `small_waves_ocean` | bed 0.0-20.0 s | https://bigsoundbank.com/s1046.html |
| `steam_hiss_1` | the hiss thickens at 10.00 s; bed 18.3-20.0 s | https://bigsoundbank.com/s0227.html |
| `steam_hiss_3` | far fumarole hiss at 0.50 s; steam roars up at 17.75 s | https://bigsoundbank.com/s3011.html |
| `thunder_2` | the eruption booms at 14.20 s | https://bigsoundbank.com/s3113.html |
| `thunder_3` | bed 4.0-20.0 s | https://bigsoundbank.com/s3114.html |
| `water_that_burns` | lava meets the sea at 17.70 s | https://bigsoundbank.com/s0202.html |
| `wind_plain` | bed 13.3-20.0 s | https://bigsoundbank.com/s0595.html |
