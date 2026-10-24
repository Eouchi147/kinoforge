# Film recipe: Little Big Questions, the Fable kids explainers (`kids-*`)

Six silent 65 to 74 s films for kids aged 6 to 8, each explaining one big idea with no narration: the picture explains,
a real public-domain orchestral recording carries the story, real CC0 sound effects sit on every event, and a few big words
are set in code. Made 23 to 24 Oct 2026 from Sam's verdicts (23 Oct 19:34 to 22:21 Toronto): Fable look, silent stories
("drop the voices"), "top notch audio, not crappy midi sound", recognisable everyday easter eggs, a lively world around the
block, the "lifted slice" framing, upgraded storybook graphics. Series rules: `films/cutaway/kids/README.md`.

## The six films
| id | Question | Music (recording, licence) | Length | Rendered on |
| --- | --- | --- | --- | --- |
| `kids-fossil` | How do bones turn to stone? | Grieg, Morning Mood (Musopen, public domain) | 65.0 s | Mac lane (and rc-render films.yml) |
| `kids-volcano` | How is a volcano born? | Grieg, In the Hall of the Mountain King (Musopen, public domain) | 72.3 s | rc-render films.yml, run 40059001981 |
| `kids-deep-sea` | What lives in the deep sea? | Mendelssohn, The Hebrides (Musopen, public domain) | 70.5 s | run 40060566034 |
| `kids-shooting-star` | What is a shooting star? | Grieg, Anitra's Dance (Musopen, public domain) | 68.4 s | run 40062232772 |
| `kids-under-your-feet` | Who lives under your feet? | Mozart, Figaro Overture (Musopen, CC0) | 74.0 s | run 40062248447 |
| `kids-rain` | Where does rain come from? | Smetana, Vltava (Musopen, public domain) | 73.0 s | run 40062314304 |
Delivered to Samsung X5 `KINOFORGE/films/kids/` and rc-render release `kino-films`. Facts: `docs/research/KIDS_FACTS_2026-10.md`;
music and effects research: `docs/research/KIDS_MUSIC_2026-10.md`.

## Folder and every file (each film is `films/cutaway/kids/<id>/`; the fossil is the template)
| File | What |
| --- | --- |
| `beats.json` | Source of truth: beats (t, name, picture, words, sound, music) plus the music block (piece, recording, licence, source page, asset, edit segments and cross-fades, credit) |
| `blender.py` | Scene contract (`build`, `frame`); ONE event table at the top (`EVENTS`, beat plus fraction, read from beats.json, so a re-timed beat sheet re-times the picture and the sound); `KF_ART_NAME = 'fable'`; a fixed camera with a 2 degree sway |
| `szworld.py` | The lifted slice (block floats about 0.3 of its height above its hole, 2.5 cm bob on a 7.5 s sine), the land around it at natural level following every era, the far horizon |
| `szmats.py`, `szgeo.py`, `szlife.py`, `szstory.py`, `szback.py` (+ film-specific modules) | Materials, geometry helpers, life and easter eggs, the story events, the background hills and life |
| `szui.py`, `szwords.py`, `fonts/Fredoka-Bold.ttf`, `fonts/OFL.txt` | Storybook graphics: Fredoka Bold in plum with a gold-orange shadow on parchment cards with gold rims, pop with overshoot, gold ribbon pointer, pocket-watch clock, gold lens magnifier (Lens class in szstory.py, `words=words.obs + lens.crisp`) |
| `audio/make_audio.py`, `audio/mix.json`, `audio/mix.m4a`, `SOUND.md` | The soundtrack: music edit, level rider, effects placed from the event table (levels relative to the music's local RMS, tonal effects tuned to the orchestra's pitch classes, beds chosen by low crest factor), master -16 LUFS, true peak under -1.5 dBTP; mix.m4a committed with `git add -f` so the runners can lay it |
| `film.json` | id, 24 fps, render 1280x720, delivery 1920x1080, samples 20 to 32, `audio: audio/mix.m4a` |
| `NOTES.md` | Beat table with times, easter eggs, weak spots, cost |

## Exact steps for a new film in the series
1. Pick the question and check the facts (researcher; every line with a source and confidence) into the facts doc.
2. Pick a real recording: Commons search with rc-render `music-search.yml` (results as notices: `gh api repos/Eouchi147/rc-render/check-runs/<job id>/annotations`), fetch with `music-fetch.yml` into release `music` (licence json beside it). Only public domain, CC0 or CC BY; never share-alike.
3. Copy `films/cutaway/kids/fossil/` code, write `beats.json` (8 to 11 beats, each understandable without words), analyse the recording (librosa RMS timeline, onsets, chroma), cut it on phrase boundaries to 60 to 75 s with 1 to 2 s cross-fades ending on its own cadence, and time every beat and hit to it.
4. Build the world and story; check stills locally at low resolution and with rc-render `stills.yml` (1280x720); the picture must be a pure function of time.
5. Build the soundtrack with `audio/make_audio.py`; measure; commit the mix with `git add -f`.
6. Render: rc-render `films.yml` with 24 parts and the full commit hash (about 45 minutes a part at 20 samples; 20 runners at a time), or the Mac lane in chunks of about 200 frames (7 to 10 s a frame; a single long job was killed after 2 h).
7. Check: contact sheet, `tools/qc.py` (loudness -16 LUFS is the series design; flicker under 3 flashes a second), deliver to the drive (curl the public release URL on the Mac shell), send Sam.

## Weak spots known on 24 Oct
- Nobody had listened by ear before delivery; levels are measured only.
- `kids-under-your-feet`: the fast seasons at 22 to 27 s brighten and dim about 2.5 times a second (qc flicker flag); slow it. The cut face washes pale cream at about 30 to 33 s.
- `kids-deep-sea`: the ocean column fills only about 28 percent of the frame width; a wider slice would read better.
- Stand-in sounds (no real recording exists): dinosaur steps, lava, meteor, cicada song; listed in each `SOUND.md`.
