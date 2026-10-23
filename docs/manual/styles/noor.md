# Series style: NOOR (Ramadan samples, Lantern Road)

NOOR is a planned Ramadan 2027 series for Muslim families (series bible: the Claude doc "NOOR · Thirty Nights of Light",
kept outside this repo). Three free look samples exist, built in the Lantern Road style (painted 2.5D multiplane, lanterns
that relight the paint): The Descent, Night Five, Iqra (16:9), Tonight's Juz, Night 30, Juz Amma (16:9), and a 9:16 short
cut from Iqra. Feel: reverent and warm. The depiction rules below are strict and non-negotiable; they come from
`docs/SOUL.md` section 1 and the films' `NOTES.md`. The samples were delivered on 23 Oct (UTC) and wait on Sam's verdict
(voice, look).

## The rules (non-negotiable)
1. **No depiction** of any prophet, angel, Companion or named person, in any form: no figure, no face, no silhouette.
   Nothing depicts Allah. The Prophet's presence is shown only by objects and light: a hand lantern alone on the mountain
   path, the empty cave, the mat where he sat, the lantern set down at his door. The angel is light only (the sky behind the
   mountain and the mouth of the cave fill with white-gold light). Juz Amma shows no person at all (the bedroom is empty).
2. **Qur'anic Arabic is set in code, never generated, never retyped**: copied from `script.json` `arabic`, which holds the
   King Fahd Complex Uthmani text (via quranenc, npm `quran-json`), and drawn in Amiri Quran (`films/noor/fonts/`, SIL OFL).
   That text writes open (staggered) tanween with U+065E and U+0656; Amiri draws them at U+08F1 and U+08F2, so `forAmiri()`
   maps them for display only. Every Arabic line is looked at rendered.
3. **No recitation until licensed**: the narration is in English; no Qur'an audio is used.
4. **No AI imagery**: every picture is painted procedurally in code.
5. Words set in code; no em dash, en dash or "..." on screen; captions are the display text (the voice may read a
   spelled-out form from `say`); meanings under the Arabic replace the caption for those lines so no line of type is on screen
   twice.
6. Facts and sources listed in `script.json` `sources` (Iqra: Qur'an 96:1-5, Qur'an 2:185, Sahih al-Bukhari 3).

## Inputs
- `films/noor/<film>/script.json`: `id`, `series` "NOOR", `strand`, `night`, `title`, `title_sub`, `lead_in` (s), `tail`
  (s), `score` (`palette`, `key`, `mode`, `seed`, `solo`), `sources`, `arabic` (verse key to Uthmani text), and `lines`
  (`id`, `sec` = score mood, `text` = display, optional `say` = spoken form, `gap` = silence after, optional
  `after: "title"` leaves the gap for the title card, optional `hit` adds a score hit before it).

## Exact steps
1. Write `script.json` (above). Copy the Arabic from the King Fahd Complex text exactly (byte for byte).
2. Sound (free), one workflow for one or more films:
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/noor-sound.yml/dispatches -f ref=main -f 'inputs[films]=films/noor/<film>'`.
   It runs `films/noor/lib/place.py <film> --prep` (writes `ad.json` with `voice` "chatterbox" and `voice_settings`
   `exaggeration` 0.5, `cfg` 0.35, `temperature` 0.7), `films/director/voice_free.py <film>` (Chatterbox on CPU, every line
   checked by Whisper base.en, a take with word error over 0.15 redone, at most 3 takes), `place.py <film>` (lines placed on
   the film's own timeline with their gaps: `cues.json`, `film.json`, `audio/score_plan.json`), then
   `films/lib/score/remix.py <film> --keep-plan` (the free score from VSCO-2 CE strings and flute, mixed at -14 LUFS). It
   commits the outputs. Re-run safe: delete `audio/vo.json` to re-voice.
3. Picture: Lantern Road, 16:9 core `kf.js` (1280x720 design frame) from Kleidion, `paint.js`, `ambient.js`; sets in `sets/`;
   `shots.js` with every cut as a cue reference (a line or a word), so the picture re-fits any new take; `type.js` or `gfx.js`
   for type, Arabic panels and teaching graphics; `scene.js` boot. See `lantern-road.md`.
4. Stills: `node films/noor/n05-iqra/tools/stills.cjs films/noor/<film> --shots --out out/<film>` (two per shot). Check every
   Arabic line rendered, and that no person appears anywhere.
5. Render free: kinoforge `films-render.yml` (dispatchable; `film`, `parts` 0 = auto, `ref`) to release `films`:
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/films-render.yml/dispatches -f ref=main -f 'inputs[film]=films/noor/<film>'`.
   Outputs `<id>.mp4`, `-preview.mp4`, `-sheet.jpg`, `-poster.jpg`.
6. A 9:16 short: cut from the film's own mix with a script like `films/noor/s05-iqra-short/make_short.py` (pieces of the mix
   joined with 0.3 s fades; `cues.json` lines shifted to the short's timeline), same sets reframed.
7. Check (`check-before-showing-sam.md`: "a person depicted in NOOR where none may be" is a reject) and deliver.

## Alternatives
| Route | When |
| --- | --- |
| A licensed recitation | only after a licence exists; until then English narration only |
| Kokoro voice (`kokoro|bf_emma` and others) through `sound.yml` | a voice audition; Chatterbox was used for the samples |
| The paid ElevenLabs voice (decision 0013) | if Sam finds the free voice not natural enough; cost about US$0.15 a film |

## Checks before showing Sam
- No figure, face or silhouette in any frame (look at the full contact sheet and every shot).
- Arabic shapes correct (kasra and tanween not touching the English under it; open tanween drawn); the single word Iqra
  drawn as a clean filled glyph run.
- Captions are the display text; no line on screen twice; 16:9 captions inside the frame, 9:16 inside the phone safe zone.

## Known traps
- Amiri does not draw U+065E and U+0656 as open tanween: map with `forAmiri()` for display only.
- Arabic lines and the English under them need space between them (Juz Amma 96:1, 97:1, 97:3 re-spaced on 22 Oct).
- An outlined Arabic glyph run looked broken: the word Iqra is a clean filled run (dark ink over a warm glow on light, gold
  over a dark halo at night) written on by a wipe.
- Iqra's render hung on one part for 4.5 h (run 39822483930, part 11): cancel and re-run only the failed part.
- Chatterbox needs `setuptools<81` in its env (the workflow pins it).

## Sources of truth
`films/noor/*/NOTES.md`, `films/noor/*/script.json`, `films/noor/lib/place.py`, `films/noor/s05-iqra-short/make_short.py`,
`.github/workflows/noor-sound.yml`, `films/director/voice_free.py`, `docs/SOUL.md` sections 1 and 3, `docs/LOG.md` (22 Oct).
