# Little Big Questions (working title): Fable explainers for kids aged 6 to 8

Sam, 23 Oct 2026 19:34: several 1-minute videos that explain big concepts to kids aged 6 to 8, very simply, in the
Fable Cutaway look. A wise and playful voice, likeable by kids, minimal, inspired by the gentle wonder of the great
nature documentaries (the writing and the pace, never an imitation of any real person's voice). Music plays a central
role. Each film is a self-contained concept that stands on its own and explains perfectly and simply how something works
or an amazing fact. The world on screen is alive, bustling and happy; the films are entertaining, hooking, clear and
never confusing.

## Grammar (from Sam's verdicts, docs/SOUL.md and films/director/CRAFT.md)
- One fixed view of one Cutaway block (the seasons-loop grammar): no cuts, barely any camera movement (a slow sway of a
  few degrees at most). The world changes in front of the camera: that is the story.
- Fable look (`films/styles/cutaway/art/fable.py`): painted sky and hills, storybook trees, gold lines between layers.
- 16:9 masters at 1920x1080 (YouTube, tablets and TV, where most 6 to 8 year olds watch); about 60 s each.
- Words on screen set in code, very few: the question as the title, one or two labels when a new word is taught
  (FOSSIL, MAGMA, LAVA), large and readable on a phone.
- Narration: short sentences, everyday words, one idea per line, a question at the start (the hook in the first three
  seconds) and a wonder at the end that sends the child back to their own world ("under your feet", "in your glass").
- Music: an original playful orchestral theme for the series (pizzicato, glockenspiel, flute, clarinet, harp, light
  percussion), a variation per film, hits on the reveals (the bone turns to stone, the volcano bursts), the voice always
  on top. Free score engine (`films/lib/score/`, VSCO-2 CE CC0 samples), a new "playful" palette.
- Facts checked with sources before anything is voiced (`docs/research/KIDS_FACTS_2026-10.md`).
- YouTube: these are "Made for Kids" (COPPA): no personalised ads, comments off. Money comes from the brand, books and
  prints more than ads (see the Cutaway guide doc).

## Films (first batch)
| id | Question | Theme | Status |
| --- | --- | --- | --- |
| fossil | How does a dinosaur turn into stone? | Dinosaurs | pilot: script, voice, music, picture |
| volcano | How is a volcano born? | Planet Earth | script; picture after the pilot verdict |
| under-your-feet | Who lives under your feet? | Animals | script draft |
| rain | Where does rain come from? | Planet Earth, weather | script draft |
| deep-sea | What lives in the deep sea? | Oceans | script draft |
| shooting-star | What is a shooting star? | Space | script draft |
