# Sound of the Cutaway showcase series

Sam (22 Oct 2026): "no voice, just nature sounds (try to use the free 2.5gig sound bank we have already)". So: no music,
no voice, no synthesis. Every sound is a real recording from BigSoundBank (Joseph Sardin), all **CC0** (public domain;
each sound page was checked to say "CC0" by the bank workflow), placed only on what we see or feel; silence is used
where the story asks for it (the meadow before the hawk, the bottom under the city).

- **The bank:** release `sfx-bank` of `Eouchi147/rc-render`: `sfx-bank.tar` (197 recordings as 48 kHz stereo 24-bit FLAC:
  the 138 BigSoundBank rows of the Dark Corners bank `dark/assets.csv` plus 59 extras in `sfx/bank_extra.txt`) and
  `sfx-bank.csv` (name, source page, licence, duration, integrated loudness, true peak). Built by the workflow
  `.github/workflows/sfx-bank.yml` (script `sfx/bank.sh`, run by hand) on a GitHub runner, because chat containers
  cannot reach bigsoundbank.com. Audio never goes into git.
- **The mixes:** `<film>/audio/make_audio.py` with the shared kit `audio_kit.py` (numpy, scipy, soundfile, ffmpeg; free,
  deterministic). Each writes `audio/mix.m4a` (20.0 s, 48 kHz stereo AAC 256k, about -18 LUFS integrated, peaks under
  -1.5 dBFS after decoding, fade in 0.8 s and out 1.2 s) and `audio/mix.json` (measurements and every recording used,
  with where). The kit finds the bank in `$SFX_BANK`, else `~/.cache/kinoforge/sfx-bank`, else downloads the archive once.
- **Events:** each script's `EV` table holds the film's event times; update it from the film's NOTES.md event table and
  run the script again (about 10 s).
- **Honest notes:** `cave_1`, `cave_2` (BigSoundBank 2135, 2136) are soundscapes the author assembled from his own real
  recordings (drops, rain, reverb), marked "idealized" on their pages. Some sounds stand in for what has no recording
  in the bank: a slowed boiling pot and slowed thunder for the magma, slowed ice cracks for rock cracking, a pigeon's
  and a small bird's wings for the hawk and the flock (no hawk call: the hawk is a shadow), a wheelbarrow and a steam
  wagon's rumble for the mine cart, mud steps for the ants and the rabbits' dives. The fox and the rabbits are silent.


## The River Through Time (`river-time`)

Beds: stream to river, wind; spots: falling stones, fossil ticks, birds and steps of today. Measured: -18.14 LUFS, peak -2.02 dBFS, 20.0 s.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `evening_birds` | bed 15.4-20.0 s | https://bigsoundbank.com/s1859.html |
| `fall_of_stone` | stones fall at 5.60 s; stones fall at 8.30 s; stones fall at 11.10 s; stones fall at 13.40 s | https://bigsoundbank.com/s1022.html |
| `mountain_stream_1` | bed 3.0-20.0 s | https://bigsoundbank.com/s2754.html |
| `small_stream_4` | bed 0.0-16.5 s | https://bigsoundbank.com/s1354.html |
| `steps_gravel_1` | hiker steps at 16.70 s; hiker steps at 17.25 s; hiker steps at 17.80 s; hiker steps at 18.35 s | https://bigsoundbank.com/s0510.html |
| `steps_stone_stair` | fossil revealed at 9.20 s; fossil revealed at 12.20 s | https://bigsoundbank.com/s0606.html |
| `wind_plain` | bed 4.0-20.0 s | https://bigsoundbank.com/s0595.html |

## Under the City (`under-the-city`)

Street at dusk with a bus and steam, water in pipes and sewer, drips, the rat, the metro, stillness in old stone, the city faintly back with a far train. Measured: -18.18 LUFS, peak -1.97 dBFS, 20.0 s.

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

Birdsong, crickets and a bee above; muffled below with the mole and ants; silence and wings for the hawk. Measured: -18.05 LUFS, peak -2.0 dBFS, 20.0 s.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `birds_waking_3` | bed 0.0-20.0 s; bed 4.5-13.0 s | https://bigsoundbank.com/s0999.html |
| `bumblebee_1` | bumblebee at 2.60 s | https://bigsoundbank.com/s1000.html |
| `dig_shovel` | mole digs at 7.20 s; mole digs at 7.90 s; mole digs at 8.50 s | https://bigsoundbank.com/s1305.html |
| `field_cricket` | bed 0.0-20.0 s | https://bigsoundbank.com/s1020.html |
| `flight_bird_1` | hawk wings pass at 13.00 s | https://bigsoundbank.com/s2891.html |
| `steps_mud` | ants (tiny scratching) at 9.00 s; rabbit dives at 13.90 s; rabbit dives at 14.30 s; rabbit dives at 14.60 s | https://bigsoundbank.com/s0495.html |

## Reef and Wreck (`reef-and-wreck`)

Surf and gulls; underwater hush with the surf through water; reef bubbles; hull creaks; diver splash. Measured: -18.14 LUFS, peak -2.0 dBFS, 20.0 s.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `bubbles_burst` | turtle breath bubbles at 9.50 s; diver bubbles at 17.15 s | https://bigsoundbank.com/s1074.html |
| `creaking_door_2` | the hull creaks at 12.40 s; the hull creaks at 14.60 s | https://bigsoundbank.com/s3205.html |
| `gulls_harbor` | gulls at 0.60 s | https://bigsoundbank.com/s2573.html |
| `small_waves_ocean` | bed 0.0-20.0 s; bed 4.2-20.0 s | https://bigsoundbank.com/s1046.html |
| `splash_big_1` | diver splash (above) at 16.80 s | https://bigsoundbank.com/s1519.html |
| `underwater` | bed 3.9-20.0 s | https://bigsoundbank.com/s3430.html |
| `water_bubbles` | reef bubbles at 6.40 s | https://bigsoundbank.com/s0150.html |

## The Gold Mine (`gold-mine`)

Night wind, crickets, owl and the miner's steps; cave air and lanterns; cart, ladder, far diggers; three blows, the last rings with sparks; bats wake and pour out across the moon. Measured: -18.09 LUFS, peak -1.99 dBFS, 20.0 s.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `anvil_1` | the strike rings: gold at 11.00 s | https://bigsoundbank.com/s3589.html |
| `bats` | bats wake in the cavern at 11.45 s; bats pour out across the moon at 14.15 s | https://bigsoundbank.com/s0458.html |
| `campaign_night_1` | bed 0.0-20.0 s | https://bigsoundbank.com/s0110.html |
| `candle_sparkle_2` | bed 6.0-14.2 s | https://bigsoundbank.com/s1279.html |
| `cave_1` | bed 5.4-14.8 s | https://bigsoundbank.com/s2135.html |
| `fall_of_stone` | chips fall at 8.64 s; chips fall at 9.84 s; chips fall at 11.04 s | https://bigsoundbank.com/s1022.html |
| `fire_foley` | sparks at 11.02 s | https://bigsoundbank.com/s3322.html |
| `flight_bird_1` | wings in the cavern at 11.95 s; wings rush out at 14.60 s | https://bigsoundbank.com/s2891.html |
| `flight_bird_2` | wings rush out at 15.05 s | https://bigsoundbank.com/s2892.html |
| `flight_pigeon` | wings in the cavern at 12.85 s; wings rush out at 14.20 s; wings rush out at 15.75 s | https://bigsoundbank.com/s0840.html |
| `hammer_concrete` | diggers far off at 7.20 s; diggers far off at 8.35 s; diggers far off at 9.50 s; diggers far off at 10.65 s; diggers far off at 11.80 s; diggers far off at 7.85 s; diggers far off at 9.25 s; diggers far off at 10.65 s; diggers far off at 12.05 s; pick strikes rock at 8.60 s; pick strikes rock at 9.80 s; pick strikes rock at 11.00 s | https://bigsoundbank.com/s1108.html |
| `owl_tawny` | an owl on the mountain at 1.20 s | https://bigsoundbank.com/s0429.html |
| `squeaky_barrow_4` | cart wheels squeal at 5.70 s | https://bigsoundbank.com/s2519.html |
| `squeaky_steps_1` | ladder rung creaks at 6.20 s; ladder rung creaks at 7.27 s; ladder rung creaks at 8.33 s; ladder rung creaks at 9.40 s; ladder rung creaks at 10.47 s; ladder rung creaks at 11.53 s | https://bigsoundbank.com/s3440.html |
| `steam_between_wagons` | cart rumble on the rails at 5.70 s | https://bigsoundbank.com/s3020.html |
| `steps_gravel_1` | the miner walks in at 0.60 s; the miner walks in at 1.15 s; the miner walks in at 1.70 s; the miner walks in at 2.25 s; the miner walks in at 2.80 s; the miner walks in at 3.35 s; the miner walks in at 3.90 s; the miner walks in at 4.45 s | https://bigsoundbank.com/s0510.html |
| `wind_plain` | bed 0.0-20.0 s | https://bigsoundbank.com/s0595.html |

## The Sleeping Volcano (`sleeping-volcano`)

Surf and birds; slow boil and rumble below; rock cracks; birds lift; steam; the eruption roar, fire, falling stones. Measured: -18.07 LUFS, peak -1.97 dBFS, 20.0 s.

| Recording | Used as | Source page (CC0) |
| --- | --- | --- |
| `big_broth` | bed 3.5-20.0 s | https://bigsoundbank.com/s0491.html |
| `crows_1` | alarm calls as they lift at 11.20 s | https://bigsoundbank.com/s0754.html |
| `fall_of_stone` | stones fall back at 16.40 s; stones fall back at 17.40 s; stones fall back at 18.20 s | https://bigsoundbank.com/s1022.html |
| `fireplace_2` | bed 15.1-20.0 s | https://bigsoundbank.com/s0031.html |
| `flight_bird_2` | birds lift at 11.05 s | https://bigsoundbank.com/s2892.html |
| `flight_pigeon` | birds lift at 10.80 s | https://bigsoundbank.com/s0840.html |
| `forest` | bed 0.0-11.4 s | https://bigsoundbank.com/s0100.html |
| `ice_crack_1` | rock cracks as magma rises at 7.20 s | https://bigsoundbank.com/s2205.html |
| `ice_crack_2` | rock cracks as magma rises at 8.60 s | https://bigsoundbank.com/s2206.html |
| `ice_crack_3` | rock cracks as magma rises at 9.80 s | https://bigsoundbank.com/s2207.html |
| `small_waves_ocean` | bed 0.0-20.0 s | https://bigsoundbank.com/s1046.html |
| `steam_hiss_1` | steam from the vents at 11.80 s | https://bigsoundbank.com/s0227.html |
| `thunder_2` | the eruption roars at 14.80 s | https://bigsoundbank.com/s3113.html |
| `thunder_3` | bed 4.5-20.0 s | https://bigsoundbank.com/s3114.html |
