# Score engine: free procedural music for KINOFORGE films

Ambient, warm, living strategy-game music (the feel of Age of Empires and Anno, CRAFT.md section 8), made from a short
plan, for any length. No paid service, no API key, nothing downloaded at run time. Deterministic: the same plan, seed
and engine give the same audio, sample for sample.

## What it makes
Long evolving string chords (voice-led, modal), a plucked voice (harp, lute, oud, lyre), a solo wind or bowed
instrument for the place and era (one motif, stated, varied, resolved), soft hand drums that enter with tension, **one
swell into the turn of the battle**, a settling after it, and a resolve on the tonic. Humanised timing and velocity,
synthesised room reverb, gentle EQ with a scoop where the voice lives, soft attacks (no clicks), master peak under -3 dBFS.

## Sound sources and licences (licence-safe only)
| Source | What | Licence |
|---|---|---|
| VSCO-2 CE samples | string sections, harp, violin pizzicato, flute, clarinet, bassoon, solo violin | CC0 (public domain) |
| Own synthesis (`dsp.py`, `voices.py`) | wavetable strings, Karplus-Strong lute/oud/lyre, breathy flute, reed, fiddle, hand drums, reverb | ours |

`--engine auto` (default) uses the samples when a sample folder is found and always adds a quiet synthetic cushion under
the strings; any missing sample falls back to synthesis. `--engine synth` needs no files at all (it sounds simpler,
more synthetic). Pure Python: numpy, scipy, soundfile (ffmpeg only for the mix and the AAC file).

## Palettes (era and place)
| Palette | Key and mode (default) | Solo | Plucked | Hand drum | Used for |
|---|---|---|---|---|---|
| `ancient_med` | D dorian | flute | harp, lyre | frame drum | Cannae (D dorian), Thermopylae (E phrygian) |
| `medieval_europe` | G dorian | solo violin, flute | lute, harp | tabor | Hastings (G dorian), Agincourt (E aeolian) |
| `middle_east_central_asia` | D hijaz | flute (ney-like, scooped) | oud | darbuka | Gaugamela (D hijaz), Hattin (A hijaz), Ain Jalut (E minor pentatonic, bowed solo, steppe drum) |
| `early_modern_europe` | D aeolian | clarinet, bassoon | harp, pizzicato | muted march drum | Waterloo (D minor, a lift into D major) |

Moods (stages of the story): `calm`, `curious`, `tension`, `turn`, `triumph`, `aftermath` (`palettes.py`).

## Use
```bash
# one film: keeps cues.json and audio/vo/line*.mp3 exactly; writes audio/score.wav, audio/mix.m4a, audio/score.json,
# audio/score_plan.json, and keeps the old mix once as audio/mix_lyria.m4a
python3 films/lib/score/remix.py films/battles/cannae
python3 films/lib/score/remix.py films/battles/cannae --keep-plan     # re-render from an edited audio/score_plan.json
python3 films/lib/score/remix.py films/battles/cannae --engine synth  # no samples needed

# only the plan (palette, key, sections found in the story), or only a score from a plan
python3 films/lib/score/plan_from_cues.py films/battles/cannae -o plan.json
python3 films/lib/score/score.py plan.json -o score.wav [--engine synth] [--seed 7] [--excerpt 80 30]

# make cues.json describe the new score (music fields only: bpm, beats, downbeats, strong_hits, energy, note;
# narration fields are verified unchanged and the script refuses to write otherwise)
python3 films/lib/score/cues_from_score.py films/battles/cannae

# listen-check by numbers and pictures: loudness, peaks, band balance, per-section level, spectrogram
python3 films/lib/score/analyse.py films/battles/cannae/audio/mix.m4a --info films/battles/cannae/audio/score.json --png out.png
```
`plan_from_cues.py` finds hook, title, setup, plan, battle, turn, result and epilogue from the narration text and the
subject (era and place words in `ad.json` and the lines). Per-film steering lives in `hints/<film>.json` (line ids, key,
mode, tempo, solo, drums, result mood); everything it does is also a plain JSON plan you can edit. Narration timing is
never changed: sections start where lines start, hits sit just before the title line and the turn line.

Score plan (JSON): `palette`, `key`, `mode`, `tempo`, `duration`, `seed`, `sections[{t, mood, intensity?}]`,
`hits[{t, kind: low|drum|swell|chime, level}]`, `voice[[start,end],...]` (solo phrases prefer the gaps), `solo`, `drums`,
`swell_len` (default 8 s), `settle` (10 s), `end_fade` (3.5 s). See the top of `score.py`.

## Air and presence
The `AIR` table at the top of `score.py` sets it: a shimmer of high chord tones, a little band-limited breath on the swell,
a gentle high shelf, brighter plucks, a livelier room. The score keeps about 3 to 4 % of its energy in 3.5 to 8 kHz (it was
0.2 %), without harsh transients (the ducking under the voice is unchanged).

## The mix (remix.py)
Narration at its own timeline positions; score ducked under it (sits about 18 dB below the voice while it speaks, about
11 dB below in the pauses, eased in 0.10 s and out 0.65 s so it breathes); loud-normalised to -14 LUFS integrated
(BS.1770), sample peak held under -2 dBFS, 2.4 s end fade, AAC 256 kbit/s. The numbers are in `audio/score.json`.
`*.wav` is git-ignored: `score.wav` is rebuilt by the same command; `mix.m4a` and `score.json` are committed. The mix is
encoded in the system temp folder, copied beside its final name, swapped in atomically and checked with ffprobe, because a
checkpointing git process once snapshotted a half-written `mix.m4a`.

## Runner setup (film.yml)
The runner already has ffmpeg, numpy, librosa (which brings scipy) and soundfile. Only the samples are new, and they are
optional (without them the engine falls back to synthesis and still works). Cache them so the download happens once:

```yaml
      - name: score samples (VSCO-2 CE, CC0), cached
        id: vsco
        uses: actions/cache@v4
        with:
          path: ${{ runner.temp }}/vsco
          key: vsco-2-ce-score-v1            # bump the suffix if the folder list below changes
      - name: score samples: fetch on a cache miss (about 30 s, 450 MB of WAV)
        if: steps.vsco.outputs.cache-hit != 'true'
        run: |
          git clone -q --depth 1 --filter=blob:none --sparse https://github.com/sgossner/VSCO-2-CE.git "$RUNNER_TEMP/vsco-src"
          git -C "$RUNNER_TEMP/vsco-src" sparse-checkout set --no-cone \
            '/Strings/Cello Section/susvib/' '/Strings/Viola Section/susvib/' '/Strings/Violin Section/susVib/' \
            '/Strings/Violin Section/Pizz/' '/Strings/Harp/' '/Strings/Solo Violin/Arco Vib/' \
            '/Woodwinds/Flute/susvib/' '/Woodwinds/Flute/expvib/' '/Woodwinds/Clarinet/susLong/' '/Woodwinds/Bassoon/sus/' \
            '/LICENSE'
          mkdir -p "$RUNNER_TEMP/vsco"; cp -r "$RUNNER_TEMP/vsco-src/Strings" "$RUNNER_TEMP/vsco-src/Woodwinds" "$RUNNER_TEMP/vsco-src/LICENSE" "$RUNNER_TEMP/vsco/"
          rm -rf "$RUNNER_TEMP/vsco-src"
      - name: re-score the battle films
        env: { SCORE_SAMPLES: '${{ runner.temp }}/vsco' }
        run: for d in films/battles/*/; do python3 films/lib/score/remix.py "$d"; done
```
- `SCORE_SAMPLES` points at the folder that contains `Strings/` and `Woodwinds/`; without it the engine also looks next to
  the package (`films/lib/score/samples/vsco`), in `.cache/vsco` at the repo root, and in `~/vsco`.
- pip: nothing new (`numpy librosa soundfile` are already installed; `scipy` comes with librosa).
- Cost and time: no API, no spend. About 1 to 1.5 minutes and 2 to 3 GB of memory per film on 2 cores; films are
  independent, so run them as a matrix if a job must be faster.
- For a film in `films/studio/<id>` (not Battle Map) call `plan_from_cues.py` only if its `cues.json` has the same line
  structure; otherwise write a plan by hand (sections and hits are all `score.py` needs) and call `score.py`.
- Git: commit `audio/mix.m4a`, `audio/score.json`, `audio/score_plan.json` (and `mix_lyria.m4a` once); never `score.wav`.

## Files
`score.py` engine and CLI | `palettes.py` modes, moods, palettes, patterns | `voices.py` samplers and synth voices |
`dsp.py` reverb, filters, loudness meter, limiter, oscillators | `plan_from_cues.py` story to plan | `hints/` per-film steering |
`remix.py` narration + score to mix.m4a | `analyse.py` numbers and spectrograms.

## Known limits
- Judged by analysis and spectrograms, not by ear: a person should listen once and say which palette needs warming.
- Hand drums and the oud are synthesised (no CC0 recordings of them); everything else is real samples when available.
- The score has its own beat grid (`audio/score.json` `beats`); `cues.json` still carries the old music's beats and
  strong hits. Picture cues that snap to `strong_hits` now snap to times that no longer line up with the music.
