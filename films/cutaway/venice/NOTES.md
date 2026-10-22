# Why Venice Sinks: director's notes (Under the Surface, film 1)

Cutaway style, 16:9, 157 s (2 min 37 s), 23 shots in 8 scenes, average shot 6.8 s. Free tools only, nothing paid.
Picture: `blender.py` (scene contract of `harness/blender_render.py`) on the kit `films/styles/cutaway/cutaway.py`
(imported, never edited), plus this folder's `sets.py` (six worlds), `arch.py` (Venetian architecture, boats, people,
gates, pole sections), `overlay.py` (labels, counter, title, arrows set in code). Sound: `.github/workflows/sound.yml`.

## Sound (done, free, on GitHub runners)
- **Voice:** Kokoro-82M (Apache 2.0) `bm_george`, British, phonemised en-gb, speed 1.0. Chosen by an audition of three
  free voices on lines l00, l01, l07 (`audition/report.json`): George 2.98 words/s, pitch range 9.8 semitones, steady
  pitch across lines (141 to 154 Hz), word error 0.04. Chatterbox (MIT) was livelier but read 3.85 words/s and its pitch
  drifted from 163 to 111 Hz between lines; Kokoro `bf_emma` was flatter (7 semitones) with an artefact on the title.
- Words exactly as `script.md`. Two spoken spellings only (the text on screen is unchanged): "Sa-lootay" so the voice
  says Salute the Italian way, and "October twenty twenty" (not "two thousand and twenty").
- **Placement:** `films/lib/battle_mix.py` on the exact beat grid of a quiet 60 bpm pad (`ad.json prep.pad_bpm`): about
  0.4 to 1.3 s between lines, a 3.6 s hold after the title line. `cues.json` holds every line and word time.
- **Score:** the free procedural engine (`films/lib/score/`), palette early modern Europe in D dorian, harp and
  pizzicato strings, a solo flute, soft string pads; a light frame drum only from the pumping (l12) to the gates;
  the one swell lands on "air is pumped in" (l14, 134.0 s) as the gates rise; a chime and a lift on "They rose for
  real" (l15); the dusk resolve (l16). Steering in `ad.json prep.score`. Mix -14.1 LUFS, peak -2 dBFS, voice 17.5 dB
  over the score while speaking. `audio/mix.m4a`.

## The six sets (all at the origin; one visible per shot)
| Set | What | Life in it |
| --- | --- | --- |
| city | Venice: a Grand Canal cut open on both front faces, two rios, open lagoon behind, about 90 palazzi with arched windows and funnel chimneys, a campo with a church, a campanile and a well, Santa Maria della Salute at the front corner, a stone bridge over the canal; on the cut faces the whole city stands on wooden poles under a band of boards and white stone, densest under the Salute | gondolas rowing both ways, moored boats, people crossing the campo, gulls, water ripples, cloud shadows; lamps and windows light at dusk; the flood and the walkways |
| lagoon | 1,500 years ago: mud flats with marsh grass and reeds, a long strip of sand with the sea beyond, deep turquoise water | boats of settlers rowing in from the left and slowing, reeds and grass in the wind, gulls; the stone house that sinks at the cut |
| site | a building site on a mud island: a pit at the front corner, 441 poles driven by pile drivers (tripod, weight hauled and dropped), a stack of tree trunks, workers; then boards, white stone and brick walls built up | hammers, workers, grass and trees in the wind, gulls |
| pole | one pole deep in the mud, close, with neighbours, the lagoon above | bubbles rising in the water, a few in the top of the mud that slow and stop; mineral specks drifting into the wood |
| sink | a diagram block: palazzi and a campanile on an island, the sea on the right, a factory with a smoking chimney and a pump house; the section on both front faces is drawn in code (mud, pale clay, water-bearing sand, deep clay) so it can be squeezed | the ground lowers, the sea rises on a tide gauge, water flows up the pipe, the sand dries, a valve turns, smoke, a gondola, gulls |
| inlet | an opening of the lagoon between a strip of dunes (with a lighthouse on a jetty) and the -Y face: a row of yellow MOSE gates hinged on the seabed | gates fill with air and swing up, bubbles; the sea outside rises and leans on the gates while the lagoon stays low; weed, a boat, gulls, dune grass in the wind |

## Scenes (beginning, middle, end) and camera plans
1. **A city in the sea** (l00 to l01, city, misty). Begins wide on Venice floating in the mist (slow 8 degree orbit);
   middle: on the end of "standing in the middle of the sea" a cut to the cut face at the mouth of the Grand Canal, a
   slow push and tilt down from the water into the mud ("almost no solid ground"); ends on the title card over the
   whole city, held 3.6 s.
2. **The lagoon, 1,500 years ago** (l02 to l03, lagoon). A dip through the mist marks the jump back in time. Begins on
   the empty lagoon (labels LAGOON, STRIP OF SAND), boats arrive; middle: wide to close at the cut, the stone house;
   ends with the house half sunk and tilted, "like a spoon in pudding".
3. **A forest upside down** (l04 to l07, site then city). Begins close and low on one pole hammered down, seen above
   ground and through the cut; middle: wide, later the same day, many poles in and three drivers working ("Millions of
   them"), then close on the cut, tilting down the packed poles to the pale harder clay (OAK, ALDER, PINE / HARDER
   CLAY); boards, white stone and walls build up in time with the words; ends on Santa Maria della Salute, low, the cut
   faces packed with poles, the counter rolling to 1,000,000+.
4. **Why the wood lasts** (l08 to l09, pole). Begins on one pole in dark mud, bubbles only near the water (NO AIR);
   middle: closer; ends with the pole turned stony grey as minerals soak in (MINERALS).
5. **Why Venice sinks** (l10 to l12, sink). Begins on the whole section: the mud squeezed, the city lowers a hair
   (two drawn-on arrows, MUD SQUEEZED); middle: the sea wall and gauge, the water line creeps up (SEA LEVEL); then the
   factory and pipe, water pumped up from the deep sand, the ground drops faster (WATER PUMPED UP); ends close on the
   valve turning, the flow stopping (PUMPING STOPPED).
6. **High water** (l13, city, overcast). Begins high on the campo as the sea pours in; ends low and close among the
   people on the raised walkways.
7. **The wall under the sea** (l14 to l15, inlet then city). Begins wide on the inlet, gates on the seabed (78 GATES ON
   THE SEABED); middle: side on through the cut, the gates fill with air and swing up (AIR PUMPED IN, the score's one
   swell), the sea rises outside; wide again: sea high, lagoon calm (OCTOBER 2020, SEA, LAGOON); ends on the campo,
   dry, people walking.
8. **Dusk** (l16, city). A dip through the mist to dusk; the lamps and windows come on; a slow pull back to the whole
   city ends the film under the score's resolve.

## Every shot and every cut
Generated from `PLAN` in `blender.py` (times in seconds on `cues.json`). Moves are eased in and out, real time,
never sped up; pushes stay under 5 % of frame per second, orbits under 1.5 degrees per second.

| Shot | In | Out | Len | Set | Camera (eased) | Why this cut |
| --- | --- | --- | --- | --- | --- | --- |
| 1a | 0.0 | 7.0 | 7.0 | city | el 30, orbit +8 deg, push in 9 % | open: arrive on Venice floating in the mist; the narration names it |
| 1b | 7.0 | 12.8 | 5.8 | city | el 13, orbit +2 deg, push in 20 %, tilt down | end of the sentence "standing in the middle of the sea"; change of scale: push to the cut face to see what is under it (water, then mud) |
| 1c | 12.8 | 16.8 | 4.0 | city | el 38, orbit +4 deg, push in 3 % | the title card: the question of the film over the whole city |
| 2a | 16.8 | 29.2 | 12.5 | lagoon | el 34, orbit -10 deg, push in 6 % | change of time (1,500 years earlier), shown by a dip through the mist; the empty lagoon, boats arrive |
| 2b | 29.2 | 37.1 | 7.8 | lagoon | el 16, orbit +4 deg, push in 10 %, tilt down | end of line; wide to close: the stone house on the mud, at the cut, sinks like a spoon in pudding |
| 3a | 37.1 | 42.3 | 5.2 | site | el 14, orbit +2 deg, push in 7 %, tilt down | change of place: the clever trick; one pole hammered down, seen above and through the cut |
| 3b | 42.3 | 47.0 | 4.8 | site | el 30, orbit +6 deg, push in 7 % | "Millions of them": close to wide, later the same day; many poles in, three drivers, the stack of tree trunks |
| 3c | 47.0 | 55.2 | 8.2 | site | el 4, tilt down | wide to close on the cut: the poles packed side by side reach the pale, harder clay; the camera tilts down them |
| 3d | 55.2 | 63.2 | 8.0 | site | el 26, orbit -6 deg, push in 7 %, tilt up | new information: what goes on top of the poles, in order; the camera holds on the corner while it builds |
| 3e | 63.2 | 70.2 | 7.0 | city | el 21, orbit -6 deg, push in 7 %, tilt down | change of place: the real church built this way; low angle for its scale, the cut face packed with poles |
| 4a | 70.2 | 80.0 | 9.7 | pole | el 8, push in 9 %, tilt down | change of scale: one pole deep in the mud; bubbles near the water stop deeper down |
| 4b | 80.0 | 88.2 | 8.3 | pole | el 4, push in 9 %, tilt down | closer: the change happens in the wood itself; it turns stony grey as minerals soak in |
| 5a | 88.2 | 98.1 | 9.9 | sink | el 16, orbit +2 deg, push in 6 %, tilt down | change of place and question: why it sinks; reason one, the mud squeezed under the city |
| 5b | 98.1 | 104.2 | 6.1 | sink | el 13, orbit -2 deg, push in 6 % | reason two: cut to the sea wall and its gauge; the water line creeps up |
| 5c | 104.2 | 113.0 | 8.8 | sink | el 15, orbit +4 deg, push in 7 %, tilt down | new information: the factories; the pipe pulls water from the deep sand, the ground drops |
| 5d | 113.0 | 115.7 | 2.6 | sink | el 18, push in 6 % | closer, the detail that answers the line: the valve turns, the flow stops |
| 6a | 115.7 | 119.8 | 4.1 | city | el 34, orbit +4 deg, push in 6 % | change of place and time: today, a high tide; the sea pours into the campo |
| 6b | 119.8 | 123.8 | 4.0 | city | el 10, orbit +4 deg, push in 4 % | low and close for people: walking to work on the raised walkways |
| 7a | 123.8 | 132.2 | 8.4 | inlet | el 32, orbit -6 deg, push in 6 % | change of place: an opening of the lagoon; the gates lie on the seabed |
| 7b | 132.2 | 138.2 | 6.0 | inlet | el 5, push in 4 %, tilt up | close, side on through the cut: the gates fill with air and swing up (the score swells here) |
| 7c | 138.2 | 141.4 | 3.2 | inlet | el 22, orbit -4 deg, push in 5 % | wide again for the result: the sea high outside, the lagoon calm behind the gates |
| 7d | 141.4 | 145.1 | 3.7 | city | el 22, orbit -4 deg, push in 5 % | cut on "The squares stayed dry": the campo, dry, people walking |
| 8a | 145.1 | 157.0 | 11.8 | city | el 31, orbit -6 deg, pull back 44 %, tilt down | passing time to dusk (a dip through the mist): the city lights up; the slow pull back ends the film |

Cuts after a line hold at least 0.8 s on the picture the line explained, but never run more than 0.25 s into the
next line (the next sentence then leads across the cut, a short J-cut). Transitions: hard cuts, except two dips
through the mist (0.45 s out, 0.55 s in) for the two changes of time (1,500 years back; to dusk).

## Graphics (set in code, `overlay.py`)
One text face, Instrument Sans (OFL, `ads/fonts`). Labels are small caps on a paper pill with a hairline leader that
draws on to a dot pinned to the world point (projected through the moving camera each frame). Title "Why Venice
Sinks" with the kicker UNDER THE SURFACE and a rule. A counter (1,000,000+, "more than a million" in the script). Two
thin drawn-on arrows (mud squeezed). No emoji, no icons, no dashes, no "...". Every word on screen is from the script.

## Render (the lead dispatches it; nothing here renders the film)
- `blender.py` builds only the sets its frame range needs (it reads `--start/--end` from the harness command line), so a
  one-frame still builds one set. Build: about 3 s per set, the city about 15 to 35 s.
- SETTINGS: Cycles 40 samples, adaptive, OIDN denoise, AgX Base Contrast, exposure 0.2. Render 1280 x 720 at 24 fps
  (3,767 frames), delivery 1920 x 1080 (`film.json`). Check stills: rc-render `stills.yml`, tags `venice-r*`.

## Known limits
- Vertical scale is exaggerated (as in any cutaway diagram): the poles and the mud layers are drawn deeper than true
  scale so the foundation reads; poles are drawn thicker than true scale for the same reason.
- The "sink" section is drawn in code over the kit's walls so it can compress; its top follows the kit's terrain.
- MOSE: one opening is shown with about ten gates; the label gives the real total (78 gates, three openings).
