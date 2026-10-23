# Sound: the CC0 sound bank and the nature-sound kits (`audio_kit.py`, `music_kit.py`)

The studio's sound effects and ambiences are real recordings from BigSoundBank (Joseph Sardin), every one CC0 (public
domain), checked as "CC0" on its own page by the workflow that builds the bank. The bank is one archive in the public
release `sfx-bank` of `Eouchi147/rc-render` (197 recordings, 48 kHz stereo 24-bit FLAC, about 1.2 GB) with a CSV of names,
source pages, licences, durations and loudness. Two small Python kits use it: `audio_kit.py` (beds and spot sounds placed on
the picture's events, a master to a loudness target) and `music_kit.py` (a quiet score written note by note, played by the
score engine's instruments). They made the six Cutaway showcase films and the meadow example; any film can use them
(set `KF_SOUND_DUR` for a length other than 20 s). Audio never goes into git.

## Inputs
- The film's event times (an `EV` table in its `make_audio.py`, taken from the film's NOTES.md event table or its build's
  shot list and time constants).
- Python 3 with numpy, scipy, soundfile; ffmpeg. The bank: `$SFX_BANK` (a folder of `<name>.flac`), else
  `~/.cache/kinoforge/sfx-bank`; if neither holds it, the kit downloads `sfx-bank.tar` once from
  `https://github.com/Eouchi147/rc-render/releases/download/sfx-bank/sfx-bank.tar` (public, no key) and unpacks it.
- For the music: VSCO-2 CE samples at `$SCORE_SAMPLES` (see `score-engine.md`), else synthesis.

## The bank (how it is built)
- Workflow rc-render `.github/workflows/sfx-bank.yml`, run by hand (workflow_dispatch), script `sfx/bank.sh`. It takes the
  138 BigSoundBank rows of the Dark Corners bank `dark/assets.csv` (fetched from rc-render release `sfx`) plus the extras in
  `sfx/bank_extra.txt` (lines `name bsb:<id>`, 59 on 23 Oct: birdsong, insects, streams, sea, underwater, gulls, city,
  metro, sewer, cave, steam, boiling, splashes), reads each sound's page `https://bigsoundbank.com/s<id>.html`, keeps it only
  if the page says CC0, converts to 48 kHz stereo 24-bit FLAC, measures EBU R128 loudness and true peak, and publishes
  `sfx-bank.tar` (folder `sfx-bank/<name>.flac`) and `sfx-bank.csv` (`name,source,licence,duration_s,lufs_i,true_peak_dbtp,channels_in,rate_in,file`).
- It runs on a GitHub runner because chat containers cannot reach bigsoundbank.com. Run 39890165805 (23 Oct, success)
  built the current release.
- To add sounds: append `name bsb:<id>` lines to `sfx/bank_extra.txt` in rc-render, push, dispatch:
  `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/sfx-bank.yml/dispatches -f ref=main`.

## Exact steps (a film's sound with the kits)
1. In the film folder, `audio/make_audio.py`:
   ```python
   import os, sys; sys.path.insert(0, '<repo>/films/cutaway/series')
   import audio_kit as K, music_kit as MK
   m = K.Mix()
   m.bed('forest', start=12, gain=-6, hp=120)            # the place, looped with cross-fades over the film
   m.spot('splash_small_1', t=7.4, gain=-12, p=0.3, label='the splash we see')   # onset on t, p = pan
   s = MK.Score(seed=3)
   s.pad(0.0, 6.0, [50, 57, 62, 66])                     # a chord (MIDI notes): strings by register plus a synth cushion
   s.note('harp', 69, 2.4, ring=3.0, vel=0.45)           # a pluck or a solo note
   m.music(s.render(env=[(0, -6), (12, 0), (20, -4)]), under=10.0)   # its loudest 3 s sit 10 dB under the nature's
   m.master(HERE)                                        # audio/mix.m4a + audio/mix.json
   ```
   Kit calls: `bed(name, start, gain, env, hp, lp, speed, width, p, t0, t1, fi, fo, xf, send)`, `spot(name, t, gain, p,
   start, length, hp, lp, speed, fi, fo, trim, width, label, sweep=(p0, p1), send)` (`p` is the pan, -1 left to 1 right;
   `label` is written into `mix.json`), `room(rt60, wet, seed, predelay)` (a synthetic cave or tunnel for the
   sends), `music(y, under)`, `master(out_dir, lufs=-16.0, ceiling=-2.0, fi=0.8, fo=1.5)`. Music instruments (`music_kit`):
   `cello`, `viola`, `violin`, `bass`, `harp`, `pizz`, `cello_pizz`, `flute`, `clarinet`, `bassoon`, `solo_violin`, `glock`,
   and a synthesised `dulcimer`; `render(env, rt60=3.6, lead_db=-3.0, lp=9000, warm=True)`.
2. Run it (about 10 s): `SFX_BANK=<bank folder> SCORE_SAMPLES=<vsco folder> KF_SOUND_DUR=<seconds> python3 audio/make_audio.py`.
3. Output: `audio/mix.m4a` (the film's length, 48 kHz stereo AAC 256k, about -16 LUFS integrated, sample peak under the
   -2 dBFS ceiling, peaks under -1.5 dBFS after decoding, fade in 0.8 s, out 1.5 s) and `audio/mix.json` (measurements and
   every recording used, with where). Write the sources table (recording, use, source page) into the series or film's
   SOUND notes, as `films/cutaway/series/SOUND.md` does.

## Alternatives
| Route | When |
| --- | --- |
| The score engine with narration (`score-engine.md`) | narrated films |
| rc-render `sfx.yml` and release `sfx` | the older Dark Corners bank (the `.wav` files the bank was built from) |
| Synthesised interface sounds in `harness/shots/codead.py` (ring, click, pop, whoosh, check, chime, impact, tick, riser) | business ads (no files, no licences) |

## Checks
- Every recording placed on something we see or feel (CRAFT.md section 8: nothing decorative); silence used on purpose.
- `mix.json`: integrated loudness near -16 LUFS, the music's loudest 3 s about 10 dB under the nature's, no clipping.
- The licence of every recording used is CC0 in `sfx-bank.csv`; stand-ins are named honestly in the notes.

## Known traps
- `cave_1` and `cave_2` (BigSoundBank 2135, 2136) are soundscapes the author assembled from his own recordings, marked
  "idealized" on their pages. Some sounds stand in for what has no recording (a slowed boiling pot and slowed thunder for
  magma, slowed ice cracks for rock, a pigeon's wings for a hawk); say so.
- The kits default to 20.0 s (`DUR` from `KF_SOUND_DUR`): a longer film without the variable is cut at 20 s.
- Slowing a spot (`speed`) used to change its heard length; the kit now keeps the set `length` after slowing.

## Sources of truth
`films/cutaway/series/audio_kit.py`, `films/cutaway/series/music_kit.py`, `films/cutaway/series/SOUND.md`, rc-render
`sfx/bank.sh`, `sfx/bank_extra.txt`, `.github/workflows/sfx-bank.yml`, release `sfx-bank` (`sfx-bank.csv`), `docs/LOG.md` (23 Oct).
