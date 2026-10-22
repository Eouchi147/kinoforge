# Dark Corners: I Am Buying Her Life (Arabia, c. 600), Clay (re-direction, 22 Oct 2026)

Blender 5.2 / Cycles CPU, KINOFORGE Clay style, 9:16, 720x1280, 24 fps, 175.84 s (`DURATION` equals `film.json`). The picture
follows the final mix (`audio/mix.m4a`, `cues.json`); the sound and its timing are untouched. Only the picture was re-directed after
Sam's verdict ("the stars are not rendered properly, the cuts do not feel natural, the screen feels too bare") and the rules in
`films/director/CRAFT.md`.

## What changed

1. **Stars.** The old card was 5 m away and rendered through a lens focused at 0.4 m, so every star became a 30 px bokeh blob. The sky
   is now its own Cycles scene (painted card, stars, Milky Way, moon, wisps, dawn sun, far ridge with caravan lamps) with no depth of
   field, composited under the table scene (`film_transparent`). Stars are about 11,000 emissive pin-hole discs in four classes
   (160 bright with a four-point glint, 2,300 mid, 6,400 small, 3,600 dust along a faint Milky Way band), 0.35 to 1.7 px, five warm and
   cool tints, a slow twinkle. Two side wings (the same card turned 90 degrees, 24 m tall) keep the sky there when the camera looks along
   the table. Checked at 720x1280, 24 spp (`t=94` frame, see QC log).
2. **Cuts.** 49 shots became 31 shots in 9 scenes (average 5.7 s). Every shot has a written reason below. Cuts happen on the end of a
   sentence or on a strong hit; the held shots follow key lines; there is no dissolve (time and scale changes are hidden behind low
   walls or carried by a camera move); camera moves are trapezoid eases (`ease(x, y, "t")`) with real-camera speeds.
3. **A fuller world** (`dress.py`). Scatter of rocks, wind-blown dry tufts and thorn scrub over the whole table (about 1,200 tufts,
   170 rocks, 55 scrub plants, more at Mecca), a second far dune crest, oasis pools with palms at both ends of the camp and in Mecca,
   rugs, jars, saddles, sacks, three small fires with clay smoke puffs, goats, saltating clay sand grains, tent cloth that breathes,
   banners on the Mecca roofs, a stall with an awning, eight caravan lamps on the far ridge, and four foreground clusters (grass and
   stones) that `fg_place` puts at the bottom corners of low shots, out of focus, so the frame has a near, a middle and a far layer.
4. **Paper-and-clay graphics**, not digital overlays: a dated place card (ARABIA, AROUND 600) taped to the sky, a name card (SASAA, tribe
   and rank), the MECCA card, the number tiles (30, 96, 360, 400) set into the sand, the poet's verse on a scroll, the end card. Cut paper
   with a tape strip, ink rule and clay letters, in their own scene without depth of field.
5. **Restraint kept.** No burial and no infant on screen (a lone lamp, a glowing tent, a silhouette in the cloth), modest wardrobe,
   no em or en dashes and no ellipsis anywhere.

## Files

| File | Holds |
|---|---|
| `blender.py` | Harness contract, materials, sky scene, compositor groups (sky, HUD), pair reuse |
| `kit.py` | Clay, card, sand, striped and emissive materials; geometry helpers; easing; text meshes |
| `world.py` | Height-field dunes with camel prints, sky card, pin-hole stars, Milky Way, moon, dawn sun, far ridge and caravan lamps, lights |
| `actors.py` | Figures, camels, lamps, ropes, goat-hair tents (they breathe), silhouette cutouts |
| `props.py` | Clay lettering (cached glyph advances), lamp field, houses of Mecca, thorn bush, stamps |
| `dress.py` | Scatter, palms and oases, fires and smoke, goats, drifting sand, rugs, pots, saddles, sacks, flags, foreground clusters |
| `director.py` | Scenes and shots with reasons (`SCENES`, `WHY`), camera keys, paper-card HUD, per-pose state, music-hit pulse |

## Look and mechanics

- Animated on 2s: every channel is a function of the pose frame `pf = (i // 2) * 2` with a small per-pose hand jitter (crc32 seeded).
- Pair reuse: the odd frame of each pair renders a 2x2 border and a `render_write` handler copies the even frame's PNG, so pairs are
  byte-identical. `KF_NO_PAIR_REUSE=1` turns it off. No harness change.
- The workflow passes `--samples 96`; `build()` caps it at 20 (`KF_ARABIA_SPP_CAP=0` lifts the cap).
- Compositor: sky scene under the table render, HUD over it where shown, pose-seeded grain and a corner falloff. Two to four node groups are
  switched per frame (muting the Render Layers node gives a grey frame, do not).
- Colour script: deep blue night, orange lamp and tent glow, Mecca warmer, dawn lilac to peach over the last shots, sun behind the dune for the end card.
- The music-hit pulse (`hit_env`, from `strong_hits`) drives lamp flicker, flame emission and tent glow.

## Scenes, shots and the reason for every cut

The scene list is in `director.SCENES` and the reasons in `director.WHY`; this table is generated from them.

### Scene 1: The night search (0.00 to 11.66 s, 2 shots)

- **Place:** Sasaa's ridge above the camps, then the camel tracks (night, stars)
- **Dramatic question:** Who is out there at night, and what does he find?
- **Beginning:** The sky: moon, stars, the dated card; a man shades his eyes on the ridge.
- **Middle:** He scans the valley of lamps; the camera follows his gaze down to the camel tracks.
- **End:** The tracks lead to a far glow and a column of smoke: two tents.
- **Camera plan:** Tilt down from the stars with a slow dolly to Sasaa (one move); then a slider pan along the tracks to the glow.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| A1_stars_to_ridge | 0.00 to 6.58 | 6.6 s | Opening: the sky and the date first (hook, place), then the man; one continuous tilt-and-dolly so the eye is led from the stars to Sasaa. Cut at 6.6 when the narration turns to "what he found". |
| A2_tracks_to_glow | 6.58 to 11.67 | 5.1 s | New information at the turn of the narration ("what he found that night"): the tracks he follows lead to a glow. The slider pan carries the eye from the prints to the far tents and their smoke. |

### Scene 2: The old records (11.66 to 18.94 s, 2 shots)

- **Place:** A scribe's scroll in the dunes (lamp, ink pot)
- **Dramatic question:** Can this be believed?
- **Beginning:** A dark scroll, a lamp.
- **Middle:** Rows of script are written in, line by line.
- **End:** The title is raised in clay letters on a plinth.
- **Camera plan:** Slow push-in on the scroll; then a slow push to the title plinth.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| A3_the_scroll | 11.67 to 16.58 | 4.9 s | A change of place and register: the "old Arabic records" become an object we can read. Rows of script are set in step with the narration; the push-in is the viewer leaning in to read. |
| A4_title | 16.58 to 18.92 | 2.3 s | The promise of the film is paid here: the title is raised in clay on a plinth right after the records line ends (hold on silence), before the first name. |

### Scene 3: The hard years (18.94 to 41.52 s, 3 shots)

- **Place:** Sasaa's ridge and the families' camp at the oasis
- **Dramatic question:** What was this world like for a newborn girl?
- **Beginning:** Sasaa is named; his tribe and rank are on a paper name card.
- **Middle:** Hunger: dry thorn, empty bowls; one lamp alone in the sand.
- **End:** A row of lit tents with figures in the cloth; one tent goes dark. "But it happened."
- **Camera plan:** A slow arc round Sasaa; a low slider past the thorn to the bowls; the camera slides from the lone lamp along the tents to the dark one.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| B1_sasaa_named | 18.92 to 25.42 | 6.5 s | A man needs a name: Sasaa is named ("His name was Sasaa") and ranked ("a nobleman of the Tamim tribe") on a paper card. One slow arc round him lets the camp and the oasis show behind; no cut inside the sentence. |
| C1_hunger | 25.42 to 33.67 | 8.2 s | Change of place and scale: from the man to what hunger looks like. A low slider passes dry thorn (foreground), empty bowls (middle) and the lit tents (far) so the scene explains "one more mouth" with objects, not words. A bowl is filled on "mouth" (33.4). |
| C2_lamp_to_tents | 33.67 to 41.50 | 7.8 s | "Some buried her alive" is not shown: one lamp alone in the sand (held on the line), then at "Not every family" the camera slides off it along the lit tents. Silhouettes in the cloth are the families; one tent goes dark on "But it happened" (the hit at 39.68). |

### Scene 4: The two tents (41.52 to 74.02 s, 6 shots)

- **Place:** The two tents on the sand: the old man's and the woman's, a fire, camels and goats between
- **Dramatic question:** Boy or girl?
- **Beginning:** Sasaa follows the tracks and finds two lit tents.
- **Middle:** The old man: your camels are safe, their milk kept us alive. A woman calls: she has given birth. The old man asks: boy or girl?
- **End:** "It was a girl." The tent glows, held in silence.
- **Camera plan:** An orbit round the rider from the side to behind; a slow dolly and a push to the milk; a dolly toward the woman's tent; a push-in on the old man; static holds on the answers.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| E_follow_to_tents | 41.50 to 49.08 | 7.6 s | Arrival as one move: a lateral track beside the rider on the tracks (41.5), the camera swings behind him as he crests (46.2, on the hit "Late at night"), he stops and points at the two tents (47.7); the fire and its smoke tell us people are there. |
| F_old_man_milk | 49.08 to 57.92 | 8.8 s | The old man gives two facts, the camels are safe and their milk kept the family alive. A slow dolly shows both men and the camels behind (they are the proof); from 54.6 the camera lowers and pushes to the milk bowl at his feet (a change of scale to the detail the line names). |
| G_woman_calls | 57.92 to 63.33 | 5.4 s | A voice from elsewhere, so the camera turns with the men toward it and moves to the woman's tent; the birth is a silhouette appearing in the cloth at 61.9 ("She had just given birth") and the camera is allowed to settle on it. |
| H_boy_or_girl | 63.33 to 71.00 | 7.7 s | The question is the whole film, so it gets one long uninterrupted face: the old man asks, the camera creeps in (4 % a second). The fire at his side and a lamp light his eyes; nothing else moves. |
| H4_reaction | 71.00 to 72.25 | 1.2 s | Reaction: cut to Sasaa on "bury her" so we see the words land on him (a reaction needs more than 24 frames; held to the hit at 72.214). |
| I_it_was_a_girl | 72.25 to 74.00 | 1.8 s | The answer is given to the tent, not to a face: the camera holds on the woman's tent, glowing, with a slow breath in the silhouette. The hold after the key line is the scene's end. |

### Scene 5: The price (74.02 to 98.85 s, 5 shots)

- **Place:** The old man's rug, the fire, the camels
- **Dramatic question:** Will he sell her, and for what?
- **Beginning:** Sasaa asks to buy her.
- **Middle:** The old man is insulted (a free man does not sell his children). Sasaa answers: I am buying her life.
- **End:** Five camels, one by one, are handed over on ropes, the last the one he rode.
- **Camera plan:** Two-shot; slow pushes on each speaker; a wide dolly on the herd; a low angle on the last camel.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| J1_asked_to_buy | 74.00 to 77.17 | 3.2 s | Two people, one question: a two-shot so we see both faces and the distance between them while Sasaa asks to buy her; the old man turns away at the end of the sentence. |
| J2_free_man | 77.17 to 83.75 | 6.6 s | The old man's insult and his principle are one thought ("A free man does not sell his children"), so one shot: the camera arcs from his right to his left while his face hardens. Cut only after "children". |
| K_buying_her_life | 83.75 to 91.92 | 8.2 s | The title line. Sasaa answers; the camera has been moving in on his face since the old man's refusal and now pushes to its closest. The long pause before "I am buying her life" is held, not covered. |
| L1_herd_handed_over | 91.92 to 96.50 | 4.6 s | The price is a list, so the picture is a list: two pregnant camels, then their calves, each roped and handed over on its word. One wide slow dolly lets the herd gather in frame. |
| L3_the_riding_camel | 96.50 to 98.83 | 2.3 s | The last camel is the one he rode: a change of angle and scale (low, close) on the hit at 96.502 because this is the cost to him. Held to the end of the line. |

### Scene 6: The promise (98.85 to 122.20 s, 4 shots)

- **Place:** The dunes at night, then the field of lamps
- **Dramatic question:** What does he do with what he has lost?
- **Beginning:** He walks home without a camel; his footprints behind him.
- **Middle:** He stops under the stars and promises; a lamp is lit for each girl, the numbers arrive on tiles.
- **End:** "Every number was a girl": the camera moves through a field of lamps.
- **Camera plan:** Tracking walk, then a tilt up to the stars; a long crane down into the field; a dolly through the lamps.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| M1_walk_home_promise | 98.83 to 105.08 | 6.2 s | One take for "walked home without them" and "that night he made a promise": a tracking shot beside him (footprints behind), he stops at the end of the walk (101.4), and the camera lowers and tilts up past him to the stars as the promise is made. The tilt is the vow. |
| M3_a_lamp_for_each | 105.08 to 108.92 | 3.8 s | "Every girl he heard of, he would save": the promise becomes a lamp, then another, then the first of a field. The camera drifts round him slowly so each lamp lights in a new part of the frame. |
| N_records_cannot_agree | 108.92 to 119.42 | 10.5 s | Scale change on the hit at 108.878: from one man to a whole field. One long crane down (high and wide = understanding the count) lands low beside the tiles as each number arrives (30, 96, 360, 400) and the field grows with it. |
| N3_every_number_a_girl | 119.42 to 122.17 | 2.8 s | The sentence changes the numbers into people: the camera leaves the tiles and moves into the lamps at lamp height; focus pulls from the tiles to the field. Held in silence to the end of the scene. |

### Scene 7: Mecca (122.20 to 144.90 s, 4 shots)

- **Place:** Mecca at night: clay houses, palms, a stall, a fire
- **Dramatic question:** Is he the only one?
- **Beginning:** A lamp is lit in the dark; Zayd walks in; MECCA card.
- **Middle:** A father at his door; Zayd stands between him and his daughter: do not kill her, I will pay for her keep.
- **End:** He raises her (she grows up behind three walls); "if you want her back, take her."
- **Camera plan:** A crane back to reveal the town; a slow push toward the two men; a lateral track behind low walls; a push to the three of them.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| O_not_alone_mecca | 122.17 to 128.67 | 6.5 s | A change of place the story needs us to feel: one lamp is lit (the same gesture as Sasaa's) and the camera cranes back and up to reveal a whole town; Zayd walks in and turns to us as the MECCA card lands. A crane because the information is scale. |
| P_zayd_and_the_father | 128.67 to 137.42 | 8.8 s | One push toward what matters: from the wide (a father at his door, Zayd coming) to the two men and the pouch of payment. The father turns on "Zayd told him"; the pouch passes on "I will pay"; the camera keeps moving in, never cutting inside the exchange. |
| Q_raised_and_grown | 137.42 to 143.08 | 5.7 s | Years pass in one walk: Zayd and the girl cross the street behind two low walls that sweep through the frame; she is smaller before each wall and taller after it, so time passes without a dissolve or a visible jump. The camera tracks with them at their pace. |
| Q3_take_her | 143.08 to 144.92 | 1.8 s | On the hit at 143.058 we are at the door: the three of them in one frame (Zayd, the grown girl, the father) as the line "take her" is said; the choice is the father's, so he is in frame. Held to the end of the line. |

### Scene 8: The poet (144.90 to 160.42 s, 3 shots)

- **Place:** A poet's lamp-lit corner of the camp, listeners around him
- **Dramatic question:** What did the grandson say about his grandfather?
- **Beginning:** A poet writes alone.
- **Middle:** The camera pulls back: he is famous, a crowd listens. One line is about his grandfather.
- **End:** The verse is set in clay letters on a scroll.
- **Camera plan:** A pull-back slider with a small crane; a push on the poet's face; a slow crane up the scroll.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| R_years_later_famous | 144.92 to 152.00 | 7.1 s | Years later and famous are one sentence, told as a pull-back: we start close on a man writing alone and the camera slides back and up to reveal the circle of listeners; the reveal lands on "most famous" (149.3). |
| R3_one_line | 152.00 to 154.75 | 2.8 s | "One line was about his grandfather": the camera returns to his face, close, because the next thing we see is what he wrote. Short because it is a breath, not a scene. |
| S_the_verse | 154.75 to 160.42 | 5.7 s | The line itself, set in clay letters word by word on the beat of the voice (no text is read before it is spoken). A slow crane up the scroll lets the last line "not buried" stand alone at the top of the frame; held for the pause after. |

### Scene 9: Dawn (160.42 to 175.84 s, 2 shots)

- **Place:** The same desert at dawn, the field of lamps burning down
- **Dramatic question:** Who grew up?
- **Beginning:** Dawn over the lamps: nobody knows how many.
- **Middle:** One girl walks up the dune.
- **End:** The sun clears the ridge; end card.
- **Camera plan:** A slow crane over the lamps; a low tracking shot, then a crane up and away.

| Shot | Time (s) | Len | Reason for the cut / the move |
|---|---|---|---|
| T1_nobody_knows | 160.42 to 164.42 | 4.0 s | The count is unknowable, so we see all of it at once: a slow crane over the field of lamps as the night turns to dawn. A hold on the wide, because the next shot picks one. |
| T2_girl_grew_up | 164.42 to 175.92 | 11.5 s | "Somewhere in that desert, a girl grew up": one girl, walking, grown, her own footprints behind her, and the sun clearing the ridge behind. A low tracking move (steady pace), then the crane up and away on "camels" gives the film its last image and room for the end card. |

Shots: 31, scenes: 9, average shot 5.7 s, shortest 1.2 s, longest 11.5 s.

Number tiles arrive at 113.0, 113.8, 115.05 and 117.38 s; the verse is set word by word in S; the end card is in the last 2.6 s.

## Render budget (720x1280, 24 spp, OIDN, measured with `time.process_time`)

- CPU time per frame: about 65 to 95 CPU-s (night sky shots with the Milky Way and many tents at the top: 80 to 93; tents and faces 67).
  On a 4 vCPU runner that is about 17 to 24 s wall per frame. Pair reuse halves the path-traced count to about 2,110 poses
  (4,220 frames in all): about 45 CPU-hours, so about 11 hours of 4 vCPU time, in roughly 22 parts of 30 minutes.
- Scene build takes 60 to 100 s once per part (the dev box here has 2 cores and a load of 8 to 11, so wall times in the logs are inflated).
- Slightly over the 20 s per frame target on the busiest shots; the cheap lever if a runner is slow is `KF_ARABIA_SPP_CAP=18`.

## QC log

- 36 stills at 360x640 (8 to 12 spp) over three passes at times through all nine scenes, a full-resolution check of the star sky
  (720x1280, 24 spp, t=94: stars crisp and varied, Milky Way band, moon with painted halo, no bokeh) and of the number tiles, the cards and the foreground clusters.
- Fixed in QC: sky showing the world gradient past the card ends and above the card (wings and a 24 m card), a V gap between the card and a
  wing (wings extended past the corner), the camera inside the terrain (ground clamp), rule line crossing the letters on cards, caravan lamps
  reading as a string of fairy lights (fewer, dimmer, irregular), far dunes near black (lighter paper colours), number tiles blurred in N3
  (camera stops short of the tiles, f/8 first, focus pulled to the field after 120.2 s), bare bottom third of low shots (denser scatter and foreground clusters).
- A no-render dry run over every pose and a pair-reuse run through the real harness were done (see the report).

## Known weak spots

- The lowest wide shots still show a lot of smooth sand in the bottom third (it is a table seen at lamp height); the foreground clusters and the
  scatter soften it, they do not remove it.
- The Milky Way band is painted and slightly diagonal at the left end of the table, which reads as a brush stroke, not a photograph.
- The sky above about 25 degrees on the side wings has no stars (stars stop at 7.5 m on the card), seen only when the camera looks along the table.
- Dawn streaks on the sky card can shimmer a little at 24 spp (grain hides most of it).
- Figures are small in the wide shots (O, N); E shows the rider's back with the tents far off (a deliberate reveal).
- 31 shots is one over the "about 20 to 30" guide; the cuts H4 (1.2 s, on the climax) and Q3/I are short by design.
