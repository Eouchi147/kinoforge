# Film recipe: Why Venice Sinks (`under-the-surface-venice`)

Under the Surface, film 1: a narrated Cutaway explainer, 16:9, 157 s (2 min 37 s), 23 shots in 8 scenes, average shot
6.8 s. Free tools only. Why a city of palaces stands on wooden poles in mud, why the wood lasts, why the city sinks, and
the MOSE gates that hold the sea back. Built and rendered on 22 Oct on GitHub runners, delivered to Sam's Mac on 23 Oct.
Verdict pending (`docs/SOUL.md`: waiting on his verdict).

Note for new work: a cut-based explainer (23 shots); since 23 Oct 17:32 Sam prefers one fixed view with no cuts
(`docs/manual/styles/cutaway-seasons-loop.md`). Ask him before another explainer in this grammar.

## Folder and every file
`films/cutaway/venice/`:
| File | What |
| --- | --- |
| `script.md` | 17 narration lines (l00 to l16, about 330 words), one picture idea each; facts checked 22 Oct with sources |
| `ad.json` | `prep` block for `sound.yml`: voice `kokoro|bm_george`, speed 1.0, `pad_bpm` 60, audition record, the `vo` lines (two spoken spellings: "Sa-lootay" for Salute, "October twenty twenty"), score steering in `prep.score`; `cap_usd` 0 |
| `audition/` | `report.json` and the three auditioned voices (`kokoro_bf_emma`, `kokoro_bm_george`, `chatterbox`) |
| `audio/` | `vo.json`, `music.json`, `score.json`, `score_plan.json`, `mix.m4a` (written by `sound.yml`) |
| `cues.json` | every line and word time (the picture follows it) |
| `film.json` | id, series "Under the Surface", 24 fps, render 1280x720, delivery 1920x1080, `duration` 156.965, `audio/mix.m4a`; no `samples` key, so runners use 24 |
| `blender.py` | the scene contract; `PLAN` (shots on `cues.json` times); builds only the sets its `--start/--end` range needs |
| `sets.py` | the six worlds: city, lagoon, site, pole, sink, inlet |
| `arch.py` | Venetian architecture, boats, people, gates, pole sections |
| `life.py` | mist sheets, god rays (camera-only cones), animals |
| `overlay.py` | labels, counter, title, arrows set in code (Instrument Sans) |
| `NOTES.md` | the director's notes: sets, scenes, every shot and cut, graphics, render, limits |

## Sets and scenes
Sets (all at the origin, one visible per shot): **city** (Grand Canal cut open on both front faces, about 90 palazzi, a
campo, campanile, Santa Maria della Salute at the front corner, a bridge; the city on poles under boards and white stone
on the faces), **lagoon** (1,500 years ago: mud flats, reeds, a sand strip; settlers' boats; the stone house that sinks),
**site** (441 poles driven by pile drivers, tree trunks, workers; boards, stone and walls built up), **pole** (one pole in
the mud; bubbles stop deeper down; minerals soak in), **sink** (a diagram block, section drawn in code so it can be
squeezed: mud, pale clay, water-bearing sand, deep clay; factory, pump, tide gauge, valve), **inlet** (a lagoon opening
with a caisson and about ten yellow MOSE gates in section, dunes, a lighthouse).
Scenes: 1 A city in the sea (l00 to l01); 2 The lagoon, 1,500 years ago (l02 to l03; a dip through mist); 3 A forest
upside down (l04 to l07); 4 Why the wood lasts (l08 to l09); 5 Why Venice sinks (l10 to l12); 6 High water (l13);
7 The wall under the sea (l14 to l15); 8 Dusk (l16; a dip through mist).

## Every shot (from `PLAN`; times in seconds on `cues.json`)
| Shot | In | Out | Set | Camera (eased) | Why this cut |
| --- | --- | --- | --- | --- | --- |
| 1a | 0.0 | 7.0 | city | el 30, orbit +8, push 9 % | arrive on Venice in morning haze |
| 1b | 7.0 | 12.8 | city | el 3, orbit -8, push 15 %, tilt down | change of scale: low along the water at the cut, down into the mud (fish, crab, amphora, coin) |
| 1c | 12.8 | 16.8 | city | el 38, orbit +4, push 3 % | the title card over the city |
| 2a | 16.8 | 29.2 | lagoon | el 34, orbit -10, push 6 % | 1,500 years earlier (dip); boats arrive |
| 2b | 29.2 | 37.1 | lagoon | el 16, orbit +4, push 10 %, tilt down | the stone house sinks like a spoon in pudding |
| 3a | 37.1 | 42.3 | site | el 14, orbit +2, push 7 %, tilt down | one pole hammered down |
| 3b | 42.3 | 47.0 | site | el 30, orbit +6, push 7 % | "Millions of them": many poles, three drivers |
| 3c | 47.0 | 55.2 | site | el 12, orbit -2, push 4 %, tilt down | packed poles reach the harder clay |
| 3d | 55.2 | 63.2 | site | el 26, orbit -6, push 7 %, tilt up | boards, white stone, walls build up |
| 3e | 63.2 | 70.2 | city | el 10, orbit -6, push 6 %, tilt down | the Salute in golden light; crane down to the clay; counter 1,000,000+ |
| 4a | 70.2 | 80.0 | pole | el 17, orbit -4, push 9 %, tilt down | one pole; NO AIR |
| 4b | 80.0 | 88.2 | pole | el 10, orbit -2, push 6 %, tilt down | the wood turns stony grey; MINERALS |
| 5a | 88.2 | 98.1 | sink | el 16, orbit +2, push 6 %, tilt down | mud squeezed (two drawn arrows) |
| 5b | 98.1 | 104.2 | sink | el 13, orbit -2, push 6 % | the sea wall and gauge; SEA LEVEL |
| 5c | 104.2 | 113.0 | sink | el 15, orbit +4, push 7 %, tilt down | factories pump water up; WATER PUMPED UP |
| 5d | 113.0 | 115.7 | sink | el 18, push 6 % | the valve turns; PUMPING STOPPED |
| 6a | 115.7 | 119.8 | city | el 12, orbit +4, push 8 % | high tide pours over the street; a cat asleep in the cellar |
| 6b | 119.8 | 123.8 | city | el 10, orbit +4, push 4 % | people on the raised walkways |
| 7a | 123.8 | 132.2 | inlet | el 32, orbit -6, push 6 % | 78 GATES ON THE SEABED |
| 7b | 132.2 | 138.2 | inlet | el 16, orbit +4, push 9 %, tilt up | air in, gates swing up to about 45 degrees (the score's one swell) |
| 7c | 138.2 | 141.4 | inlet | el 22, orbit -4, push 5 % | sea high outside, lagoon calm (OCTOBER 2020, SEA, LAGOON) |
| 7d | 141.4 | 145.1 | city | el 22, orbit -4, push 5 % | "The squares stayed dry" |
| 8a | 145.1 | 157.0 | city | el 31, orbit -6, pull back 44 %, tilt down | dusk (dip): the city lights up; the end |
Cuts hold at least 0.8 s after a line and never run more than 0.25 s into the next (short J-cuts). Pushes under 5 % of
frame per second, orbits under 1.5 degrees per second. Two dips through mist (0.45 s out, 0.55 s in) for the two changes
of time; otherwise hard cuts.

## Exact steps that made it
1. Script with checked facts (`script.md`), then `ad.json` (prep block).
2. Sound on GitHub (kinoforge `sound.yml`, free): audition first, then the sound (the exact dispatches are not
   recorded; `audition=ad` uses `prep.audition.voices` and `prep.audition.lines`, here l00, l01, l07):
   ```bash
   gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main \
     -f 'inputs[folder]=films/cutaway/venice' -f 'inputs[audition]=ad'
   gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main \
     -f 'inputs[folder]=films/cutaway/venice' -f 'inputs[voice]=kokoro|bm_george'
   ```
   It voices the lines (Kokoro-82M, Apache 2.0, phonemised en-gb), checks words (Whisper), places them with
   `films/lib/battle_mix.py` on the beat grid of a quiet 60 bpm pad (0.4 to 1.3 s between lines, a 3.6 s hold after the
   title line), scores with the free engine, mixes, and commits `audio/`, `cues.json`, `film.json`. Run ids: not recorded.
3. Picture on the cue times (`blender.py` `PLAN`); check stills with rc-render `stills.yml` (tags `venice-r*`).
4. Render on GitHub runners, 24 parts (LOG 22 Oct: "full render dispatched (24 parts, about 50 runner-hours)"):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/venice' -f 'inputs[parts]=24' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   Run id not recorded. Output `under-the-surface-venice.mp4` (98,221,172 bytes, seen 23 Oct), `-preview.mp4`, `-sheet.jpg`.
5. Checked on a contact sheet (2:37, -14.1 LUFS) and copied to Sam's Mac as `kino-films/under-the-surface-venice.mp4`
   (LOG and STATUS 23 Oct).

## The sound
Voice Kokoro `bm_george` (won the audition: 2.98 words/s, pitch range 9.8 semitones, steady 141 to 154 Hz, word error
0.04; Chatterbox read 3.85 words/s and its pitch drifted 163 to 111 Hz; `bf_emma` flatter with a title artefact). Score:
the free procedural engine, early modern Europe palette in D dorian, harp and pizzicato strings, a solo flute, soft pads,
a light frame drum only from the pumping (l12) to the gates, the one swell on "air is pumped in" (l14, 134.0 s), a chime
and lift on "They rose for real" (l15), the dusk resolve (l16). Mix -14.1 LUFS, peak -2 dBFS, voice 17.5 dB over the score.

## Graphics (set in code, `overlay.py`)
Instrument Sans (OFL, `ads/fonts`); small-caps labels on a paper pill with a hairline leader drawn on to a dot pinned to
the world point (projected through the moving camera each frame); title "Why Venice Sinks" with kicker UNDER THE SURFACE
and a rule; a counter (1,000,000+); two drawn-on arrows. Every word on screen is from the script.

## Cost
US$0. Runner (r4, 22 Oct): about 70 s a still including the build, so about 45 to 60 s a frame chunked; 3,767 frames,
roughly 50 runner-hours. Build about 3 s per set, the city 15 to 35 s. Mac lane test (Venice frames 1000 to 1019,
1280x720, 24 spp): about 7.5 s a frame on the M4 GPU.

## Sam's verdict
Pending.

## Weak spots and limits (from NOTES)
Vertical scale exaggerated (poles and mud drawn deeper and thicker than true); the sink section is drawn in code over the
kit's walls; MOSE shows one opening with about ten gates (the label gives the real 78 in three openings). A 9:16 cut was
planned in `films/cutaway/README.md`; none is recorded as made.

## To make a new one like it
1. Script first (one picture idea per line, facts with sources), `ad.json`, `sound.yml` (audition, then voice).
2. Sets as functions in `sets.py`, built only when the frame range needs them; a `PLAN` table of shots on cue times with
   a reason per cut; overlays in code.
3. Prefer the spec line (`docs/manual/styles/cutaway-line.md`) when its presets can say the place; Venice needed six
   hand-built worlds.

## Checks before showing Sam
Length 156.965 s; -14 LUFS; labels from the script only; no dash or three-dot ellipsis on screen; the two dips; a full contact sheet.

## Known traps
A one-frame still must build only one set (it reads `--start/--end` from the harness command line). The free voice needs
spoken spellings for foreign names (keep the screen text unchanged).

## Sources of truth
`films/cutaway/venice/NOTES.md`, `script.md`, `ad.json`, `blender.py`, `sets.py`, `arch.py`, `life.py`, `overlay.py`,
`.github/workflows/sound.yml`, rc-render `films.yml`, `docs/LOG.md` (22 and 23 Oct), `docs/STATUS.md`. The code wins if
they disagree.
