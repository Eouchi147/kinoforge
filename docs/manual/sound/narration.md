# Sound: narration (voices, paid and free, with recognition checks)

Narration is recorded line by line, each line heard back by speech recognition (faster-whisper) and retaken if it was
misheard, and saved with word timings so the picture can land on words. Two routes exist. Paid: ElevenLabs voices through
OpenRouter (`harness/shots/factory.speech`), cast by an audio model; this voiced the eight battles (`brian`) and the
business ads, and is the director's default in paid mode (decision 0013, cap per film). Free: Kokoro-82M (Apache 2.0) or
Chatterbox (MIT) on a GitHub runner (`films/director/voice_free.py`); this voiced the NOOR samples (Chatterbox) and Venice
(Kokoro `bm_george`). Sam's bar (16 Oct): "the voices should sound the most natural possible, not AI at all"; a voice that
sounds synthetic loses an ad he otherwise loved (The Call). How to get truly natural voices is still an open question for
him (`docs/STATUS.md`).

## Inputs
- `ad.json` with a `prep` block in the film folder: `vo` (lines: `text`, optional `id`), `voice` (`engine|option` or an
  ElevenLabs name), and for paid casting `voice_cast` (candidates), `cast_lines`, `voice_brief`, `voice_instructions`
  (delivery direction, sent to models that accept it), `vo_words: true` (word timings). Spoken spellings go in the spoken
  text only (NOOR `say`, Venice "Sa-lootay"); the screen keeps the display text.
- Words checked by the house style: no em dash, en dash or "..." (gate `text`).

## Voices used so far
| Film(s) | Voice | Route | How it was chosen |
| --- | --- | --- | --- |
| The eight Battle Map films | ElevenLabs `eleven-v4` `brian` | `codead.yml` prep (paid) | an audio model scored reels of 5 candidates (`openai/gpt-4o-mini-tts` ash and coral, `google/gemini-3.8-flash-tts` Puck and Charon, ElevenLabs brian); `audio/casting.json` `best` |
| `unmissed-v1` Manifesto | ElevenLabs `roger` | `codead.yml` prep | casting by `xiaomi/mimo-v2.6-pro` ("deepest, warmest") |
| `unmissed-v2` The Catch | ElevenLabs `river` | same | "a person speaking softly and closely into the microphone" |
| `unmissed-v3` The Call | ElevenLabs `matilda` (AI) and `chris` (caller), v3 tags like `[casual]` | `prep.dialogue` | Sam: loved the ad, the voice "too fake" |
| `unmissed-v4` Night Shift | ElevenLabs `eric` | `codead.yml` prep | "low, slow, close and warm" |
| `unmissed-v5` Bento | ElevenLabs `jessica` | `codead.yml` prep | "warm and bright, upbeat" |
| `unmissed-01` | ElevenLabs `sarah` | single-step `codead.py` | given in ad.json |
| NOOR Iqra, Juz Amma (and the short) | Chatterbox, `exaggeration` 0.5, `cfg` 0.35, `temperature` 0.7 | `noor-sound.yml` (free) | default; Sam's verdict pending |
| Venice (Cutaway) | Kokoro `bm_george`, en-gb, speed 1.0 | `sound.yml` audition then sound (free) | audition of three free voices: George 2.98 words a second, 9.8 semitones, word error 0.04; Chatterbox livelier but 3.85 words a second with pitch drift; Kokoro `bf_emma` flatter with an artefact |
| Salamis (director, free day) | Chatterbox, 15 lines in 15.5 min | `film.yml` free mode | free mode default |

## Exact steps
Free (no money):
1. Audition first (optional): `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main -f 'inputs[folder]=<folder>' -f 'inputs[audition]=kokoro|bm_george,kokoro|bf_emma,chatterbox'`
   (or `audition=ad` for `prep.audition.voices`). It voices `prep.audition.lines` (default the first two) with each voice
   into `<folder>/audition/<voice>/` plus `report.json` (rate, pitch range, pauses, recognition) and makes nothing else.
2. Voice and sound: the same dispatch with `-f 'inputs[voice]=kokoro|bm_george'` (blank = `ad.json` `prep.voice`;
   `inputs[redo]=true` deletes `audio/vo*` and re-voices). Kokoro runs in its own Python 3.11 env (`kokoro-onnx`, model files
   `kokoro-v1.0.onnx` and `voices-v1.0.bin` from the kokoro-onnx releases); British voices (`bf_*`, `bm_*`) are phonemised
   en-gb. Chatterbox runs in its own Python 3.11 env with CPU torch 2.6.0 and `setuptools<81`. Every line is checked by
   faster-whisper base.en: a take with word error over 0.15 is redone with another seed, at most 3 takes, the best kept;
   silence trimmed. Output `audio/vo/line<k>.mp3`, `audio/vo.json` (`voice`, `lines` with `text`, `file`, `dur`, `words`,
   `wer`, `takes`), then placement, score and mix (`battle-mix.md`, `score-engine.md`). Committed by the workflow.
3. NOOR: `noor-sound.yml` does the same with Chatterbox and its own placement (`docs/manual/styles/noor.md`).

Paid (decision 0013: inside a cap per film; ads and boards still need Sam's go per job):
1. `ad.json` prep with `voice_cast`, `voice_brief`, `voice_instructions`, `cast_lines`, `vo_words: true`.
2. `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/codead.yml/dispatches -f ref=main -f 'inputs[ad]=<id or folder path>' -f 'inputs[mode]=prep'`
   (`harness/shots/prep.py`): every candidate reads `cast_lines` lines, an audio model scores the reels and writes
   `audio/casting.json` (`best`, `why`, `model`), the best voice reads every line, Whisper base.en gives word times. Also makes
   the Lyria score and its beat map. Cost recorded in `ledger.json` (battles: voice US$0.14 to 0.17, music US$0.08).
3. The director in paid mode (`films/director/README.md`): ElevenLabs `eleven-v4|brian` by default (brief `voice`), every
   line heard back by Whisper, a word error over 0.25 retaken once (booked like any call); about US$0.10 to 0.15 for about
   330 words.

## Alternatives
| Route | When | Note |
| --- | --- | --- |
| A human voice recording | when Sam wants a fully natural voice | an open option in `docs/STATUS.md`; nothing recorded yet |
| `chatterbox|path/to/ref.wav` | a reference voice we have the right to use, stored in this repo | voice cloning only with rights |
| OmniVoice and other engines in the old `voice.yml` lane (14 Oct pilots) | history only | OmniVoice weights are non-commercial: those pilot narrations cannot be published or monetised |
| ElevenLabs premade voices for dialogue | rejected | "too fake" (SOUL section 5) |

## Checks
- `audio/vo.json` has one entry per script line; word error per line low (free: at most 0.15 after retakes).
- Listen to the hook, the title line and the end: natural pace and pauses, no artefacts, names pronounced right.
- Picture text shows the script's words, not the recogniser's.

## Known traps
- Chatterbox fails to load without `setuptools<81` (resemble-perth imports `pkg_resources`).
- faster-whisper on new PyAV fails to decode: decode with ffmpeg (`voice_free.py` `pcm16k`) or librosa first.
- Whisper spells names its own way ("Tiberius", "Hatton", "Angelut"): the spec refers to neighbouring words.
- Hard-to-say names need a spoken spelling in the spoken text, never on screen.
- A voice must never be sped up to fit; move the next cue.

## Sources of truth
`films/director/voice_free.py`, `harness/shots/prep.py`, `harness/shots/factory.py` (`speech`), `.github/workflows/sound.yml`,
`noor-sound.yml`, `codead.yml`, `films/director/README.md`, `films/*/*/audio/casting.json` and `vo.json`, `ads/*/audio/casting.json`,
`films/cutaway/venice/NOTES.md`, `docs/decisions/0013-capped-paid-films.md`, `docs/SOUL.md` sections 2 and 5.
