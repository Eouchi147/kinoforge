# Director lessons (newest first, at most 40)

Written by `films/director/reflect.py` after every job and read by `films/director/spec.py` before every draft.
One line each: what the checks or the eyes caught, phrased as a rule for the next spec. Seed lessons come from building
the eight hand-made Battle Map films (21 to 22 Oct 2026).

- 2026-10-22 Sam: Spend nothing. Free OpenRouter models (":free") and free tools only; narration with a free open voice on the runner, score with the free procedural engine.
- 2026-10-22 Sam: Every cut, move and effect needs a written job (CRAFT.md section 1). A spec with more than 40 shots in 3 minutes, or cuts placed only on music hits, is rejected.
- 2026-10-22 Sam: Never speed up a camera move or an animation to fit a line; plan earlier, move less, hold longer.
- 2026-10-22 Sam: Battle Map: no emoji or cartoon icons; a motion-graphics legend frames the battlefield; units never overlap or pass through each other; each set has a planned camera.
- 2026-10-22 Sam: Worlds must feel alive and full: at least three layers of ambient motion in every wide shot; bare frames read as unfinished.
- 2026-10-22 seed: Word refs must copy a word that is in that line's word list; prefer distinctive words (names, numbers, verbs) over "the", "and", "a", which repeat and need #n.
- 2026-10-22 seed: An `until` past the end of the film is fine for things that hold to the end; an entry that ends before it starts is never shown.
- 2026-10-22 seed: Labels anchored to blocks move with the block; when two blocks are close, give their labels opposite `dx` or `dy`, or the plates cover each other.
- 2026-10-22 seed: Hide blocks (`hidden: true`) and drop them in with `appear` on the word that introduces them; a map full of blocks before the narration names them confuses a child.
- 2026-10-22 seed: A full-screen inset (`rect: [0, 0, 1, 1]`, `frame: false`) for the battlefield stage reads as a cut; give it `in: 1.0` or more so the cut is a soft dissolve.
- 2026-10-22 seed: Top-down camera keys use `width` (ground width in view) and `pitch: 89.9`; oblique keys use `dist` and a pitch of 12 to 40. Keep the action inside the width you ask for.
