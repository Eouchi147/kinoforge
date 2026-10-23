# Make a Battle Map film by hand

For a battle (or any story about places and movement) in the Terrain style, 16:9, about 2.5 minutes. The free director
can make one without hand coding (`run-the-free-director.md`); use this playbook when Sam wants a hand-made film or the
director's spec is not good enough.

Read first: `docs/SOUL.md` sections 2 to 4, `films/director/CRAFT.md` (all of it), `films/lib/battlemap/SPEC.md`,
and the reference film `films/battles/cannae/` (`NOTES.md`, `spec.js`). Decision: `docs/decisions/0003`.

## Steps
1. **Folder.** `films/battles/<id>/` (lowercase, dashes). Copy `film.json` and `index.html` from Cannae and change `id`,
   `title`. Nothing else in another film's folder.
2. **Script.** 15 to 18 narration lines, about 330 words: a hook, the title line, stakes and people first, each side's plan,
   the turn, the result in plain numbers, why it mattered, a closing line with a smile. Kid-clear, upbeat, a glint of
   dark humour in the words and the timing, never in clip art. Check every fact against two sources and list them in
   `NOTES.md`. No em or en dashes, no "..." (the `text` gate fails on them).
3. **Sound (free).** Write `ad.json` with a `prep` block like Cannae's (`vo` lines, `voice`, score hints in `prep.score`),
   commit, push, then dispatch kinoforge `sound.yml`:
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main -f 'inputs[folder]=films/battles/<id>' -f 'inputs[voice]=kokoro|bm_george'`
   (or `audition=` first to compare voices). It commits `audio/`, `cues.json`, `film.json`. Pull. The picture now follows
   this sound: never change its timing.
4. **Plan before code.** In `NOTES.md`: the scene list (5 to 9 scenes, each one place and one dramatic question with its
   job), then the shots (18 to 35, average 5 to 8 s) with a reason for every cut and a camera plan per scene.
5. **Spec.** `spec.js`: `scenes` (each with `job`, `set`, `shots` with `at`, `why`, `from`, `moves`), maps (`stages`),
   `blocks` hidden until the word that names them (`appear`), `legend` (sides, unit kinds, 2 to 4 lettered places),
   `ambient` (camps or walkers, birds, wind, river flow), arrows that draw on the words, labels only for names, numbers
   and dates. No emoji, no cartoon icons, no `Math.random` or clocks.
6. **Plan check (no browser):** `node films/lib/battlemap/tools/scenes.mjs films/battles/<id>` until 0 errors; read
   every warning and fix or justify it in `NOTES.md`.
7. **Look at it.** Stills in one browser session:
   `node films/lib/battlemap/tools/stills.cjs films/battles/<id> --t <one time per shot> --out out/<id>` (needs
   `cd harness && npm ci && npx playwright install chromium` once). Open the images. Fix what a picky editor would.
   For full-quality stills on a runner: `render-on-github.md`, stills.
8. **Director check:** `node films/director/check.cjs films/battles/<id> --line battle-map` (report and `sheet.jpg` in
   `films/battles/<id>/check/`, not committed). `ok: true` and no overlapping labels; look at the sheet.
9. **Write it down.** `NOTES.md` final (scene table equal to the code, measured cost, weak spots); a line in
   `docs/LOG.md`; `docs/STATUS.md`.
10. **Gates, commit, push:** `bash tools/verify.sh`, then commit only your files, `git pull --rebase --autostash origin main`, push.
11. **Render** (`render-on-github.md`, about 16 parts), **check** (`check-before-showing-sam.md`), **deliver**.

## Definition of done
- `scenes.mjs` 0 errors; `check.cjs` `ok: true`; `bash tools/verify.sh` all pass.
- You looked at one still per shot and at least three 5 s moving stretches (the opening, the turn, the end).
- `NOTES.md` has the scene table, the facts with sources, the weak spots; LOG and STATUS updated; pushed.
- The render passed `check-before-showing-sam.md`, and Sam has the link or the file, with the weak spots named.
