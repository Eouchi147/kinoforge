# Series style: Dark Corners (the hand-built films)

Dark Corners is a series of true dark-history episodes for adults, 9:16, about 3 minutes each, told with restraint: no
gore, no suffering bodies, silence as a tool. The episodes were first made by the older rc-render pipeline (`dark/` and
`dark.yml`, release `dark-films`). On the night of 21 to 22 Oct 2026 Sam asked for every episode in the KINOFORGE styles, so
each picture was re-made by hand in one house style while keeping the original narration, score and sound mix untouched:
Bamberg in Kinetic, Zong and Kleidion in Lantern Road, Arabia in Clay. After Sam's verdicts of 22 Oct, Kleidion, Arabia and
Bamberg were re-directed again (v2); Zong was not in his notes and stays on its first KINOFORGE version. This page is the
series contract; the style pages hold the techniques and `docs/manual/films/dark-corners-*.md` the recipe of each film.

## Inputs (every episode)
- `audio/mix.m4a`: the final episode mix copied from rc-render release `dark-films` (narration, score and sound; never
  changed). `cues.json`: `episode`, `title`, `duration`, `end_card_s` (2.6 s), `style`, `aspect`, `w`, `h`, `fps`, `audio`,
  `audio_note`, `strong_hits`, `energy` (0.1 s hop) and `lines` with word times, rebuilt from the original timeline code
  (LOG 21 Oct). The picture follows these times.
- `film.json`: `id` `dark-corners-<episode>-<style>`, `series` "Dark Corners", `title`, `style`, `duration`, `fps` 24,
  `render_w` 720, `render_h` 1280, `w` 1080, `h` 1920, `audio`, `samples` 24, and the note "Picture re-made in the KINOFORGE
  style; the narration, score and sound are the original episode mix."

## The four episodes
| Episode | Title | Style | Folder | Length | Release asset (rc-render `kino-films`) |
| --- | --- | --- | --- | --- | --- |
| Bamberg, 1628 | A Hundred Thousand Good Nights | Kinetic (hand-built Canvas 2D) | `films/dark-corners/bamberg/` | 163.315 s | `dark-corners-bamberg-kinetic.mp4` |
| The Zong, 1781 | The Ship Called Care | Lantern Road | `films/dark-corners/zong/` | 179.4 s | `dark-corners-zong-lantern-road.mp4` |
| Kleidion, 1014 | As They Say | Lantern Road (re-directed 22 Oct) | `films/dark-corners/kleidion/` | 169.049 s | `dark-corners-kleidion-lantern-road.mp4` |
| Arabia, about 600 | I Am Buying Her Life | Clay (re-directed 22 Oct) | `films/dark-corners/arabia/` | 175.84 s | `dark-corners-arabia-clay.mp4` |
Each also has `-preview.mp4` (540 wide) and `-sheet.jpg` in the release. On Sam's Mac: `Video Production/kino-films/`, the
re-made ones with a `-v2` suffix.

## Rules of the series
- Restraint: atrocity is told by words, objects, numbers, absence and light. Zong: no drowning, no bodies; 29 November shown
  only by an empty deck, a swinging lantern and the sea; scale by numerals and amber dots. Kleidion: the blinding is never
  shown. Arabia: no burial and no infant on screen (a lone lamp, a glowing tent, a silhouette in the cloth). Bamberg: torture
  is words and objects only (thumbscrew plates, rope, eight falls as a tally).
- Faceless silhouettes for real people (Equiano and Sharp in Zong); no invented people named.
- Craft (CRAFT.md, Sam 22 Oct): every cut has a reason (18 to 35 shots for 2.5 to 3 min), real-time moves, full living
  worlds, every effect has a written job.
- Words set in code; no em dash, en dash or "..." on screen; type inside the phone safe zone (x 0.11 to 0.78, y 0.15 to 0.65).
- Series cards: title card early (Zong 14.9 to 17.4 s), end card in the last 2.6 s.

## Exact steps (a new episode, or a re-make)
1. Sound first. A new episode needs its narration, score and mix made and placed before any picture (`docs/manual/sound/`);
   a re-make copies `audio/mix.m4a` and `cues.json` from the existing episode.
2. Pick the style by the story: documents and a single voice (Kinetic), light and journeys (Lantern Road), people and a full
   world (Clay). Read that style page and the closest film's recipe page.
3. Build in `films/dark-corners/<episode>/` (keep an old version in `<episode>_old/` only if Sam may compare; the Kleidion
   one is no longer in the tree).
4. Write `NOTES.md` with the scene list, the reason for every cut, what lives in every wide, measured cost and weak spots.
5. Render on rc-render `films.yml` (web films 12 to 20 parts, Blender 24 parts), check, deliver with `-v2` for re-makes.

## Alternatives
The spec-driven Kinetic engine (`films/lib/kinetic/`) re-told Zong from a spec alone (`films/studio/kinetic-demo/`): use it
for a new Kinetic episode unless it needs objects the engine lacks.

## Checks before showing Sam
`docs/PLAYBOOKS/check-before-showing-sam.md`, plus: nothing shown that the series' restraint forbids; the mix is the
original (duration matches `film.json` within a frame); about -14 LUFS (Bamberg measured -14 LUFS, no freezes).

## Known traps
See each style page; series-specific: the original mixes are final, so a picture problem is fixed in the picture, never by
re-timing the sound; text overprinting at card changes (Bamberg, 148 s) is found only by auditing every change.

## Sam's verdicts
22 Oct (09:20 Toronto), on the first KINOFORGE versions: Kleidion too many cuts, a sped-up opening, it does not flow;
Arabia stars not rendered properly, cuts not natural, the screen too bare; Bamberg good but not polished, effects with no
intent. The re-made versions (22 Oct) wait on his verdict (`docs/SOUL.md` section 3).

## Sources of truth
`films/dark-corners/*/NOTES.md`, `films/dark-corners/*/cues.json` and `film.json`, `docs/LOG.md` (21 and 22 Oct),
`docs/SOUL.md`, `films/director/CRAFT.md`, rc-render `dark/` (the original pipeline) and `.github/workflows/films.yml`.
