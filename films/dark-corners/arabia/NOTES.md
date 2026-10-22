# Dark Corners: I Am Buying Her Life (Arabia, c. 600), Clay

Blender 5.2 / Cycles CPU, KINOFORGE Clay style, 9:16, 720x1280, 24 fps, 175.84 s (`DURATION` equals `film.json`). The picture
follows the final mix (`audio/mix.m4a`, `cues.json`); nothing here changes its timing.

## Files

| File | Holds |
|---|---|
| `blender.py` | Harness contract (`DURATION`, `SETTINGS`, `build`, `frame`), materials, compositor, HUD scene, pair reuse |
| `kit.py` | Clay, card, sand, striped and emissive materials; geometry helpers; text meshes |
| `world.py` | Height-field dunes with camel prints, painted-card sky, pin-hole stars, moon and dawn sun, lights |
| `actors.py` | Figures, camels, lamps, ropes, goat-hair tents with silhouette cutouts |
| `props.py` | Clay lettering, lamp field, houses of Mecca, thorn bush, stamps |
| `director.py` | The shot list (one function per shot), music-hit pulse, per-pose state |

## Look and design

- Animated on 2s: every channel is a function of the pose frame `pf = (i // 2) * 2`, with a small per-pose hand jitter (crc32 seeded), so
  re-renders are deterministic.
- Pair reuse: the odd frame of each pair renders only a 2x2 border and a `render_write` handler copies the even frame's PNG, so the
  pair is byte-identical (checked through the real harness). `KF_NO_PAIR_REUSE=1` turns it off. No harness change was needed.
- The workflow passes `--samples 96`; `build()` caps it at 24 (`KF_ARABIA_SPP_CAP=0` lifts the cap).
- On-screen text (labels, title, end card) is clay lettering in a separate Cycles scene with no depth of field, composited with AlphaOver.
  Two compositor node groups (with and without the HUD) are switched per frame; muting the Render Layers node gives a grey frame, do not.
- Compositor: pose-seeded grain and a corner falloff.
- Colour script: deep blue night with orange lamp and tent glow; Mecca warmer; dawn lilac to peach over the last shots, sun rising
  behind the dune for the end card.
- Restrictions kept: no burial and no infant on screen, only light, shadow, a tent glow and empty sand; modest wardrobe throughout;
  no em or en dashes in any file and no ellipsis on screen.
- Music-hit pulse (`hit_env`, from `strong_hits`) drives lamp flicker, flame emission and tent glow. 13 cuts were snapped to the nearest strong hit within 0.2 s.

## Shot list against the cues

| Shot | Time (s) | Lines | Cut on |
|---|---|---|---|
| A1_sky_to_dune | 0.00 to 6.60 | o1 |  |
| A2_tracks | 6.60 to 11.66 | o2 |  |
| A3_records | 11.66 to 16.60 | o3 | hit 11.656 |
| A4_title | 16.60 to 18.94 | cont. |  |
| B1_sasaa | 18.94 to 22.00 | x1 |  |
| B2_nobleman | 22.00 to 25.40 | cont. |  |
| C1_hard | 25.42 to 27.92 | x2 |  |
| C2_hunger | 27.92 to 33.70 | cont. |  |
| C3_lone_lamp | 33.70 to 37.22 | cont. |  |
| D1_families | 37.22 to 39.68 | x3 |  |
| D2_dark_tent | 39.68 to 41.52 | cont. | hit 39.683 |
| E1_follow_tracks | 41.52 to 46.00 | s1 | hit 41.54 |
| E2_two_tents | 46.00 to 49.11 | cont. | hit 46.161 |
| F1_old_man | 49.11 to 52.00 | s2 | hit 49.11 |
| F2_found_camels | 52.00 to 54.58 | cont. |  |
| F3_milk | 54.58 to 57.95 | cont. |  |
| G1_woman_calls | 57.95 to 60.70 | s3 |  |
| G2_given_birth | 60.70 to 63.37 | cont. |  |
| H1_boy_or_girl | 63.37 to 66.00 | s4 | hit 63.367 |
| H2_one_of_us | 66.00 to 69.41 | cont. |  |
| H3_bury_her | 69.41 to 71.00 | cont. |  |
| H4_reaction | 71.00 to 72.21 | cont. |  |
| I_it_was_a_girl | 72.21 to 74.02 | s5 | hit 72.214 |
| J1_asked_to_buy | 74.02 to 77.16 | b1 |  |
| J2_insulted | 77.16 to 80.40 | cont. | hit 77.16 |
| J3_free_man | 80.40 to 83.75 | cont. |  |
| K1_answered | 83.75 to 88.20 | b2 |  |
| K2_buying_her_life | 88.20 to 91.95 | cont. |  |
| L1_two_pregnant | 91.95 to 94.95 | b3 |  |
| L2_calves | 94.95 to 96.50 | cont. |  |
| L3_riding_camel | 96.50 to 98.85 | cont. | hit 96.502 |
| M1_walked_home | 98.85 to 101.80 | v1 |  |
| M2_promise | 101.80 to 105.09 | cont. |  |
| M3_every_girl | 105.09 to 108.88 | cont. | hit 105.094 |
| N1_records_cannot_agree | 108.88 to 113.00 | v2 | hit 108.762 |
| N2_numbers | 113.00 to 119.40 | cont. |  |
| N3_every_number_a_girl | 119.40 to 122.20 | cont. | hit 119.397 |
| O1_not_alone | 122.20 to 124.00 | z1 |  |
| O2_mecca_zayd | 124.00 to 128.70 | cont. |  |
| P1_father_door | 128.70 to 131.31 | z2 |  |
| P2_do_not_kill | 131.31 to 134.95 | cont. | hit 131.309 |
| P3_pay_keep | 134.95 to 137.39 | cont. |  |
| Q1_raised | 137.39 to 139.50 | z3 | hit 137.392 |
| Q2_grown | 139.50 to 143.06 | cont. |  |
| Q3_take_her | 143.06 to 144.90 | cont. | hit 143.058 |
| R1_years_later | 144.90 to 148.45 | g1 |  |
| R2_famous_poet | 148.45 to 152.00 | cont. |  |
| R3_one_line | 152.00 to 154.72 | cont. |  |
| S_verse | 154.72 to 160.42 | g2 |  |
| T1_nobody_knows | 160.42 to 164.40 | f1 |  |
| T2_girl_grew_up | 164.40 to 175.90 | cont. |  |

Title card (DARK CORNERS / I Am Buying Her Life) shows in A4 before x1 at 19.1 s; labels ARABIA, AROUND 600 (A1) and MECCA (O2);
number tiles 30, 96, 360, 400 at 113.0, 113.8, 115.05, 117.38 s; the scroll line is set in S_verse; end card in the last 2.6 s.

## Render budget (measured on this box, 720x1280, 24 spp, OIDN)

- About 55 to 80 CPU-s per frame; on a 4 vCPU runner that is roughly 14 to 20 s per frame. Pair reuse halves the path-traced
  frame count to about 2110 poses (4220 frames in all). Expected total about 38 CPU-hours, about 9.5 hours of 4 vCPU time, so about 20 parts of roughly 30 minutes each.
- Wall times on the dev box are inflated by other jobs (load about 8); use CPU time.
- Frames in this QC were rendered at 360x640, 8 to 12 spp; some at 720x1280.

## QC log

Contact sheets of all 51 shots checked at 360x640 and the problem shots fixed: angry brows (`brow_bias`), faces too dark in dialogue
(warm fill, higher f-stop), ropes crossing the frame in the price scene, the riding path leading away from the tents, the poet hidden
behind the scroll, Zayd's back in P2, title overflow on the end card, sky card edge, beards hiding mouths, domes covering eyes, blurred
HUD text. Final pass: A1 (Sasaa and camel visible at 3.5 s and 5.5 s), D1, D2, E2, F1, N1, N2, O2, R1 to R3, T1, T2, end card.
A full dry run of all 4220 poses (no rendering) was run to catch exceptions.

## Known weak spots

- Pin-hole stars read as soft bokeh dots at depth of field; close to the camera they are noisy.
- The thumbprint texture on the sand is subtle at 720x1280.
- Figures are small in the wide shots (E2, N2, O1); E2 shows the rider's back with the tents far off.
- The far dune layers are near black in the dawn shots.
- The cuts at 41.52, 46.0 and 113.0 are not snapped to a hit (the first two share constants with the follow-track path).
- 24 spp with OIDN may show a little temporal shimmer on the stars and the lamp field; grain hides most of it.
