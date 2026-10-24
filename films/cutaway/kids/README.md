# Little Big Questions (working title): Fable explainers for kids aged 6 to 8

Sam, 23 Oct 2026 19:34: several 1-minute videos that explain big concepts to kids aged 6 to 8, very simply, in the
Fable Cutaway look. A wise and playful voice, likeable by kids, minimal, inspired by the gentle wonder of the great
nature documentaries (the writing and the pace, never an imitation of any real person's voice). Music plays a central
role. Each film is a self-contained concept that stands on its own and explains perfectly and simply how something works
or an amazing fact. The world on screen is alive, bustling and happy; the films are entertaining, hooking, clear and
never confusing.

## Grammar (from Sam's verdicts, docs/SOUL.md and films/director/CRAFT.md)
- SILENT STORIES (Sam, 23 Oct 20:09 and 20:10): no narration. The picture explains everything on its own; the music and
  the sound design carry the story; a few big words set in code where needed (the question, the new word: FOSSIL). The
  music is a REAL orchestral recording (public domain or CC0, never sample-based or MIDI-sounding: "top notch audio"), and
  the picture is choreographed to its phrases (Fantasia style); every event has a real recorded sound. Each film's
  `beats.json` (picture, words, sound, music per beat) is its source of truth; the beats are re-timed to the recording.
- One fixed view of one Cutaway block (the seasons-loop grammar): no cuts, barely any camera movement (a slow sway of a
  few degrees at most). The world changes in front of the camera: that is the story.
- Fable look (`films/styles/cutaway/art/fable.py`): painted sky and hills, storybook trees, gold lines between layers.
- 16:9 masters at 1920x1080 (YouTube, tablets and TV, where most 6 to 8 year olds watch); about 60 s each.
- Words on screen set in code, very few: the question as the title, one or two labels when a new word is taught
  (FOSSIL, MAGMA, LAVA), large and readable on a phone.
- Music research and picks: `docs/research/KIDS_MUSIC_2026-10.md`. Nothing harsh or scary: soft attacks, no loud stingers.
- Easter eggs (Sam, 23 Oct 19:43): very recognisable things from a child's own life in every film, several per film,
  some obvious and one or two hidden, animated where possible (a red ball or toy car in a soil layer, a rubber duck on
  the river, a teddy bear, a kite in a tree, a dropped ice-cream cone, a bucket and spade, a dog chasing a stick, a toy
  dinosaur beside the real fossil). Generic objects only: no brands, logos or characters from any film, show or game.
- The background is a lively extension of the world (Sam, 23 Oct 19:43), never a flat static card: 3D layers with depth
  behind the block, distant life of the same era (herds on the horizon, a smoking volcano, a village with chimney smoke,
  a train on a bridge, kites, sheep), drifting clouds, light that changes with the story and with time passing.
- Voice: dropped (20:09) after two auditions; the free voice lab (`voice-lab.yml`, Chatterbox and Parler-TTS) stays
  available but untested.
- Scripts at 125 words or fewer, one key word repeated on screen, no sleep words for death ("died", said softly).
- Facts checked with sources before anything is voiced (`docs/research/KIDS_FACTS_2026-10.md`).
- YouTube: these are "Made for Kids" (COPPA): no personalised ads, comments off. Money comes from the brand, books and
  prints more than ads (see the Cutaway guide doc).

## Films (first batch)
| id | Question | Theme | Status |
| --- | --- | --- | --- |
| fossil | How does a dinosaur turn into stone? | Dinosaurs | delivered 24 Oct (silent, real orchestra) |
| volcano | How is a volcano born? | Planet Earth | delivered 24 Oct (silent, real orchestra) |
| under-your-feet | Who lives under your feet? | Animals | delivered 24 Oct (silent, real orchestra) |
| rain | Where does rain come from? | Planet Earth, weather | delivered 24 Oct (silent, real orchestra) |
| deep-sea | What lives in the deep sea? | Oceans | delivered 24 Oct (silent, real orchestra) |
| shooting-star | What is a shooting star? | Space | delivered 24 Oct (silent, real orchestra) |
