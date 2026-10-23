# Sound: the battle mix (`films/lib/battle_mix.py`): narration placed on a beat grid

`battle_mix.py` takes recorded narration lines with word timings and a piece of music with its beat map, and places every
line on the music's beat grid to make the film's timeline: it writes `cues.json` (every line with start, end and word times
on the film timeline, beats, downbeats, strong hits, energy), `film.json` (duration and render sizes) and a first
`audio/mix.m4a` (narration over the ducked music, -14 LUFS). Everything in the picture follows `cues.json` from then on. It
made the timelines of the eight Battle Map films (21 Oct, over a Lyria score), and it is the placement step of kinoforge
`sound.yml`, the director's sound stage (over a quiet pad made in code, `films/director/pad.py`), and the Venice Cutaway film
(a 60 bpm pad).

## Inputs (in the film folder)
- `audio/vo.json`: `{voice, lines: [{text, file, dur, words: [[word, start, end]]}]}` (from `harness/shots/prep.py` or
  `films/director/voice_free.py`), and the line files `audio/vo/line<k>.mp3`.
- `audio/music.mp3` and `audio/music.json` (`bpm`, `beats`, `downbeats`, `biggest_rise_s`, `duration`).
- `ad.json` (`id`, and `_` whose text after ": " up to " (" becomes the title).

## Exact steps
1. `python3 films/lib/battle_mix.py films/battles/<id> [--title-line 1]`
2. What it does, in order (constants `GAP` 0.32 s, `LEAD` 1.2 s, `OUTRO` 4.2 s, `TITLE_HOLD` 2.6 s):
   - If the music is shorter than the narration needs, it repeats whole bars from about 40 % in (cut on downbeats, 40 ms
     triangular cross-fades) into `audio/music_ext.wav` and shifts the beat grid (Waterloo needed it).
   - Line 0 starts on the first beat after 1.2 s. The title line (index 1, "This is the Battle of X.") lands on the music's
     biggest rise when that is reachable (0.3 to 4.5 s after the previous line ends); the line after it waits an extra 2.6 s
     for the title card. Every other line starts on the first beat at least 0.32 s after the previous line ends.
   - Duration = last line end + 4.2 s (room for the end card while the score resolves).
   - Strong hits = onset-strength peaks above the 96th percentile (librosa); energy = RMS every 0.1 s, scaled to 1.
   - `cues.json`: `id`, `title`, `duration`, `outro_s`, `title_line`, `bpm`, `beats`, `downbeats`, `strong_hits`,
     `energy_hop_s`, `energy`, `lines`, `audio`, `note`.
   - `film.json`: `series` "Battle Map", `style` "terrain", `fps` 24, `render_w` 1280, `render_h` 720, `w` 1920, `h` 1080,
     `audio` (an existing `film.json` keeps its fields; only `duration` is updated).
   - The mix (ffmpeg): each line delayed to its start, amixed; music at -7 dB with a 0.4 s fade in and a 2.6 s fade out,
     `sidechaincompress` under the voice (threshold 0.04, ratio 3.5, attack 25 ms, release 420 ms), then
     `loudnorm=I=-14:TP=-1.5:LRA=11`, AAC 256k.
3. Then replace the music with the free score and keep the timeline: `python3 films/lib/score/remix.py <film>` (the
   previous mix is kept once as `audio/mix_lyria.m4a`) and `python3 films/lib/score/cues_from_score.py <film>`
   (`score-engine.md`). Never move a line after the picture exists.

## Alternatives
| Route | When |
| --- | --- |
| `sound.yml` (kinoforge): free voice, then `battle_mix.py` on a pad, then the score | any narrated film folder with an `ad.json` prep block (`narration.md`) |
| `films/noor/lib/place.py` | NOOR: lines placed with written gaps and a lead-in instead of a beat grid |
| `films/noor/s05-iqra-short/make_short.py` | a short cut from an existing film's mix |

## Checks
- `cues.json` line count equals the script's; the title line sits where the title card is planned; `duration` equals the
  mix length.
- Listen to the joins; the end card has its 4.2 s.

## Known traps
- Beat trackers halve or double the tempo: check the grid (librosa with `start_bpm`) before trusting it.
- Whisper words differ from the script (spellings like "Hatton", "Dianik,"): the picture refers to neighbouring words or
  shows the script's words timed by alignment.
- `ffmpeg` needs `-nostdin`; `xfade` shorter than about 0.22 s drops segments.

## Sources of truth
`films/lib/battle_mix.py`, `.github/workflows/sound.yml`, `films/director/sound.py`, `films/director/README.md` (sound
stage), `docs/LESSONS.md` (Sound).
