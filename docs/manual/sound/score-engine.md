# Sound: the free score engine (`films/lib/score/`)

The score engine writes original film music from a short JSON plan, for any length, with no paid service, no key and
nothing downloaded at run time (the CC0 samples are optional and cached). The feel is the one Sam asked for on 22 Oct:
ambient, warm, living strategy-game music in the manner of Age of Empires and Anno (CRAFT.md section 8): long evolving
string chords, a plucked voice (harp, lute, oud, lyre), one solo instrument for the place and era, soft hand drums that enter
with tension, **one swell into the turn**, a settling after it, a resolve on the tonic. It is deterministic: the same plan,
seed and engine give the same audio sample for sample. It scores all eight Battle Map films, the NOOR samples, Venice and
the director's films, and its instruments play the Cutaway series scores (`music_kit.py`, see `sfx-bank.md`). Decision:
`docs/decisions/0006-free-score-engine.md`.

## Inputs
- For a narrated film: the film folder with `cues.json` (lines with starts, ends, word times), `audio/vo/line*.mp3` and
  `ad.json` (era and place words; optional `prep.score` steering), or a hand-written plan.
- Python 3 with numpy, scipy, soundfile (librosa for the analysis and cues), ffmpeg for the mix and the AAC file.
- Optional samples: VSCO-2 CE (CC0) at `$SCORE_SAMPLES` (the folder that holds `Strings/` and `Woodwinds/`); otherwise the
  engine looks in `films/lib/score/samples/vsco`, `.cache/vsco` at the repo root and `~/vsco`, and falls back to synthesis.

## Sound sources (licence-safe only)
| Source | What | Licence |
| --- | --- | --- |
| VSCO-2 CE samples (`github.com/sgossner/VSCO-2-CE`) | string sections (cello, viola, violin sustain with vibrato), violin pizzicato, harp, solo violin, flute, clarinet, bassoon | CC0 |
| Own synthesis (`dsp.py`, `voices.py`) | wavetable strings, Karplus-Strong lute, oud and lyre, breathy flute, reed, fiddle, hand drums, reverb | ours |
Hand drums and the oud are always synthesised (no CC0 recordings of them).

## Palettes (`palettes.py`)
| Palette | Default key and mode | Solo | Plucked | Hand drum | Used for |
| --- | --- | --- | --- | --- | --- |
| `ancient_med` | D dorian | flute | harp, lyre | frame drum | Cannae (D dorian, 62 bpm), Thermopylae (E phrygian, 58) |
| `medieval_europe` | G dorian | solo violin, flute | lute, harp | tabor | Hastings (G dorian, 76), Agincourt (E aeolian, 70) |
| `middle_east_central_asia` | D hijaz | flute (ney-like, scooped) | oud | darbuka | Gaugamela (D hijaz, 72), Hattin (A hijaz, 66), Ain Jalut (E minor pentatonic, 84, solo violin, steppe drum), NOOR Iqra (D hijaz), NOOR Juz Amma (D dorian) |
| `early_modern_europe` | D aeolian | clarinet, bassoon | harp, pizzicato | muted march drum | Waterloo (D aeolian, 84, a lift into D major), Venice (D dorian) |
Moods (story stages): `calm`, `curious`, `tension`, `turn`, `triumph`, `aftermath`.

## The plan (`audio/score_plan.json`)
`palette`, `key`, `mode`, `tempo` (hand-drum pulse in bpm), `duration`, `seed`, `sections` (`[{t, mood, intensity?}]`),
`hits` (`[{t, kind: low|drum|swell|chime, level}]`), `voice` (narration spans: solo phrases prefer the gaps), `solo`
(`flute`, `clarinet`, `bassoon`, `solo_violin`), `drums`, `swell_len` (default 8 s), `settle` (10 s), `end_fade` (3.5 s).
Per-film steering for `plan_from_cues.py` lives in `films/lib/score/hints/<film>.json` or `ad.json` `prep.score`: `palette`,
`key`, `mode`, `tempo`, `solo`, `drums`, `battle_line`, `turn_line`, `result_line`, `result_mood`, `epilogue_line`, and a
`_` line saying the intent (Cannae: "calm hook, the plan drawn on the map, drums with the Roman charge, the one swell when
his best soldiers step in from both ends, sober after").

## Exact steps
1. One film, end to end (keeps `cues.json` and `audio/vo/line*.mp3` exactly; writes `audio/score_plan.json`,
   `audio/score.json`, `audio/score.wav` (git-ignored), `audio/mix.m4a`; keeps the previous mix once as `audio/mix_lyria.m4a`):
   `SCORE_SAMPLES=<vsco folder> python3 films/lib/score/remix.py films/battles/<id>`
2. Steer by hand: edit `audio/score_plan.json`, then `python3 films/lib/score/remix.py films/battles/<id> --keep-plan`.
   No samples: `--engine synth`.
3. Plan only, or score only:
   `python3 films/lib/score/plan_from_cues.py films/battles/<id> -o plan.json` and
   `python3 films/lib/score/score.py plan.json -o score.wav [--engine synth] [--seed 7] [--excerpt 80 30]`.
   `plan_from_cues.py` finds hook, title, setup, plan, battle, turn, result and epilogue from the narration and the subject;
   sections start where lines start; hits sit just before the title line and the turn line. For a film whose `cues.json`
   does not have the Battle Map line structure, write the plan by hand (sections and hits are all `score.py` needs).
4. Make `cues.json` describe the new score (music fields only: `bpm`, `beats`, `downbeats`, `strong_hits`, `energy_hop_s`,
   `energy`, `note`; narration fields verified unchanged, else it refuses):
   `python3 films/lib/score/cues_from_score.py films/battles/<id>` (`--dry` to preview).
5. Listen by numbers: `python3 films/lib/score/analyse.py films/battles/<id>/audio/mix.m4a --info films/battles/<id>/audio/score.json --png out.png`
   (integrated and short-term loudness, peak, clipping, energy share per band, loudness per section, a spectrogram).
6. Commit `audio/mix.m4a`, `audio/score.json`, `audio/score_plan.json` (and `mix_lyria.m4a` once); never `score.wav`.
7. If the film was already rendered: rc-render `remux.yml` (`remux.md`).
8. On a runner: kinoforge `sound.yml` (narration plus score, `narration.md`), `noor-sound.yml` (NOOR), or the cached sparse
   checkout of VSCO-2 CE shown in `films/lib/score/README.md` (about 30 s and 450 MB of WAV on a cache miss).

## The mix that `remix.py` makes
Narration at its own timeline positions; score made at -23 LUFS and ducked under the voice (about 18 dB below it while it
speaks, about 11 dB below in the pauses, eased in 0.10 s and out 0.65 s); loud-normalised to -14 LUFS integrated (BS.1770),
sample peak held under -2 dBFS, 2.4 s end fade, AAC 256 kbit/s. Measured on the battles: mix -14.09 to -14.12 LUFS, voice
16.8 to 17.3 dB over the score while speaking, 0 clipped samples (`audio/score.json` `mix`). Air: about 3 to 4 % of the
score's energy sits in 3.5 to 8 kHz (the `AIR` table at the top of `score.py`; it was 0.2 % before 22 Oct).

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Lyria (`"music": "lyria"` in a director brief; `codead.yml` prep for ads) | a full produced track (ads); rejected for battles (Sam wanted ambient) | about US$0.04 to 0.08 a clip |
| Cutaway `music_kit.py` (notes written by hand on the engine's instruments) | short films with no voice, a quiet score under nature sounds | free |
| A public-domain recording (`music-fetch.md`) | a film built on a classical piece (the Cutaway Fable film plan) | free, licence record required |

## Checks
- `python3 films/lib/score/selftest.py` (about 40 s, synthesis only; in `bash tools/verify.sh --full`): every palette
  renders, determinism, stereo 48 kHz length, peak under -3 dBFS, no clipping, no NaN, loudness on target, the swell is
  real, no em or en dashes in the package.
- `analyse.py` numbers in range; listen once to the opening, the turn and the end before showing Sam.

## Known traps
- Judged by analysis and spectrograms, not by ear: a person should listen once and say which palette needs warming. Sam's
  verdict on the feel (three 30 s excerpts sent 22 Oct) is not recorded yet.
- The score has its own beat grid; `cues.json` keeps the old music's beats until `cues_from_score.py` runs. The v2 battle
  pictures do not snap to music.
- Encode the mix to a temp file, verify it with ffprobe and swap it in atomically: a checkpointing git process once
  snapshotted a half-written `mix.m4a`.
- Memory: about 2 to 3 GB and 1 to 1.5 minutes per film on 2 cores; run films as a matrix if a job must be faster.

## Sources of truth
`films/lib/score/README.md`, `score.py`, `palettes.py`, `voices.py`, `dsp.py`, `plan_from_cues.py`, `remix.py`,
`cues_from_score.py`, `analyse.py`, `selftest.py`, `hints/*.json`, `films/*/*/audio/score.json`,
`docs/decisions/0006-free-score-engine.md`, `films/director/CRAFT.md` section 8.
