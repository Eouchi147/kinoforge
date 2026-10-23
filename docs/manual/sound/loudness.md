# Sound: loudness targets and how each is measured

Every KINOFORGE mix is normalised to a target integrated loudness (EBU R128 / BS.1770) with a peak ceiling. Narrated films,
ads and social videos sit at -14 LUFS (the common target of social and video platforms); the Cutaway showcase films with no
voice sit at -16 LUFS so the nature sounds stay soft; the score alone is made at -23 LUFS before it is mixed under a voice.
This page lists every target the code uses and the measured results on record.

## Targets in code
| What | Target | Peak ceiling | Where |
| --- | --- | --- | --- |
| Narrated film mix (score engine) | -14 LUFS integrated | sample peak under -2 dBFS; 2.4 s end fade | `films/lib/score/remix.py` |
| Score alone, before mixing | -23 LUFS | peak under -3 dBFS (selftest) | `films/lib/score/score.py`, `audio/score.json` `lufs` |
| Voice over the score | about 18 dB over while speaking, about 11 dB in the pauses (measured 16.6 to 17.5 dB while speaking) | | `remix.py`, `audio/score.json` `mix` |
| First battle mix over a Lyria score | `loudnorm=I=-14:TP=-1.5:LRA=11` | true peak -1.5 dBTP | `films/lib/battle_mix.py` |
| Business ads | `loudnorm=I=-14:TP=-1.5:LRA=11` | -1.5 dBTP | `harness/shots/codead.py` |
| Social videos | `loudnorm=I=-14:TP=-1.5:LRA=11`, or a silent track | -1.5 dBTP | `harness/shots/social.py` |
| AI-footage pieces | -14 LUFS | | `harness/shots/factory.py` |
| Cutaway nature mixes (`audio_kit`) | -16 LUFS (`master(lufs=-16.0, ceiling=-2.0)`), the music's loudest 3 s 10 dB under the nature's | -2 dBFS limiter; peaks under -1.5 dBFS after AAC decoding | `films/cutaway/series/audio_kit.py` |
| First Cutaway series ambiences (before the music) | -18 LUFS | under -1.5 dBFS decoded | `docs/LOG.md` 23 Oct (superseded by -16) |
| Check before showing Sam | about -14 LUFS, true peak under -1 dBTP | | `docs/PLAYBOOKS/check-before-showing-sam.md` |

## Measured (on record)
| Film | Integrated | Source |
| --- | --- | --- |
| Battle Map Cannae, Hastings, Gaugamela, Hattin, Thermopylae, Waterloo, Ain Jalut, Agincourt | mix -14.09 to -14.12 LUFS (`score.json`), -14.2 LUFS on the finished films | `films/battles/*/audio/score.json`, `docs/LOG.md` 22 to 23 Oct |
| NOOR Iqra, Juz Amma | -14.06, -14.07 LUFS | `films/noor/*/audio/score.json` |
| Venice (Cutaway, narrated) | -14.07 LUFS (`score.json`), -14.1 on the film | `films/cutaway/venice/audio/score.json` |
| Arabia (Dark Corners, original mix) | -14.0 LUFS on the film | `docs/LOG.md` 22 Oct |
| Bamberg (Dark Corners, original mix) | -14 LUFS on the film | `docs/LOG.md` 22 Oct |
| `unmissed-v1` | -13.2 LUFS | `docs/LOG.md` 16 Oct |
| Cutaway series (six films) and the meadow example | -16.0 to -16.3 LUFS (decoded -16.1 to -16.3) | `films/cutaway/*/audio/mix.json`, `films/cutaway/series/*/audio/mix.json` |
| Cutaway seasons loop | -18.0 LUFS | `films/cutaway/loops/seasons/audio/mix.json` |

## Exact steps (measure a file)
- Integrated loudness and true peak: `ffmpeg -nostdin -i film.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12`
- Per section, band balance and a spectrogram: `python3 films/lib/score/analyse.py <file> --info <film>/audio/score.json --png out.png`
- Duration: `ffprobe -v error -show_entries format=duration -of csv=p=0 film.mp4`

## Known traps
- A limiter after loudness normalisation moves the loudness a little: `audio_kit.master` normalises, limits, fades, then
  normalises and limits again; AAC encoding moves peaks again (measure the decoded file).
- Loudness targets are integrated: a quiet film with one loud moment can pass the number and still fight the voice; check the
  voice-over-score figures per section in `score.json`.

## Sources of truth
`films/lib/score/remix.py`, `score.py`, `analyse.py`, `selftest.py`; `films/lib/battle_mix.py`; `harness/shots/codead.py`,
`social.py`, `factory.py`; `films/cutaway/series/audio_kit.py`; the `audio/score.json` and `audio/mix.json` files;
`docs/PLAYBOOKS/check-before-showing-sam.md`.
