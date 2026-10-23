# Re-direct a film from Sam's notes

When Sam judges a finished film ("too many cuts", "the stars are wrong", "effects with no intent").

## Steps
1. **Record his words, verbatim and dated,** before touching code: in `docs/SOUL.md` section 3 (verdict and lesson), in
   `films/director/CRAFT.md` "Sam's verdicts" if it is a craft rule for every film, and a line in `docs/LOG.md`.
2. **Turn each note into a checkable item** in the film's `NOTES.md`, as a table: note, what will change, how you will
   check it (a number, a still, a gate). Example: "too many cuts" means 64 shots become 18 to 35, checked by `scenes.mjs` or
   the shot list count.
3. **If the note is a rule for every film, make it a check,** not only prose: a craft check in `films/director/check.cjs`
   or `films/director/lint/`, a check in the engine (`films/lib/battlemap/scenes.js`), or a gate in `tools/verify.py`.
   If it cannot be checked by code, say so in `docs/MEMORY.md` style: a line in `docs/LESSONS.md`.
4. **Keep the old version reachable:** write the last commit hash of the old version in `NOTES.md` (git keeps it). The
   finished old render stays in its release; the new one is delivered with a suffix (`-v2`, `-v3`).
5. **Keep the sound** unless the note is about sound: the picture follows `cues.json`. A sound note goes to the score
   engine (`films/lib/score/`) and the finished picture gets new sound with rc-render `remux.yml` (no re-render).
6. **Re-direct** with the playbook of the film's style (Battle Map, Cutaway; Lantern Road, Clay and Kinetic films are
   hand-built: the film's `NOTES.md` explains its code).
7. **Compare** old and new contact sheets side by side; every note must be visibly answered.
8. **Render, check, deliver** (`render-on-github.md`, `check-before-showing-sam.md`, `deliver-to-sams-mac.md`). In the
   message to Sam: one line per note, what changed, and anything you could not fix.

## Definition of done
- Every note in the `NOTES.md` table is marked done with how it was verified, or marked not done with the reason.
- Rule-level notes have a check in code (or a written reason why not).
- SOUL, CRAFT (if craft), LOG and STATUS updated; `bash tools/verify.sh` passes; pushed.
- The new render passed the checks and reached Sam with a version suffix.
