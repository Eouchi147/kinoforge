# Films lane: brief for every scene builder (22 Oct 2026)

Sam (the owner) asked on 21 Oct for two things, finished by the morning:
1. **Dark Corners** (his dark-history series, 9:16, about 3 minutes each) re-made in three KINOFORGE styles:
   Bamberg in **Kinetic** (`proto/p11-kinetic`), Zong and Kleidion in **Lantern Road** (`proto/p03-lantern-road`),
   Arabia in **Clay** (`proto/p10-clay`). The sound is DONE: each folder has the original episode's final mix
   (`audio/mix.m4a`: narration, score, sound) and `cues.json` (every narration line with its start, end and word timings on
   the film's timeline, the 3 % strongest music hits `strong_hits`, an energy curve at 0.1 s). **The picture follows the
   sound. Never change its timing.**
2. **Battle Map**, a new series (16:9, about 2.5 minutes each): epic, grandiose, kid-clear reconstructions of famous
   battles in the **Terrain** style (`proto/p12-terrain`), upbeat with a glint of dark humour. `films/battles/<id>/`.

## Your folder is your film
`films/<series>/<id>/` holds `film.json` (id, duration, fps 24, render size, delivery size, audio), `cues.json`, `audio/`,
and your scene. Do not edit other films' folders, `proto/`, or the docs. If you must change shared harness code
(`harness/render.cjs`, `harness/blender_render.py`, `harness/kit/`), keep it backward compatible and say so in your report.

## The scene contract (same as the prototypes)
- Web scene (canvas 2D or Three.js): `index.html` + modules; `window.KF = { width, height, fps: 24, duration, canvas,
  render(i, t) }`, `window.KF_READY = true` when fonts and assets are loaded. Every frame is a pure function of `i`/`t`
  (no clocks, no randomness without a fixed seed, no CSS transitions). Read the size from `?w=&h=`.
  Render: `node harness/render.cjs films/<series>/<id> --w 720 --h 1280 --start A --end B --jpg --out out/<id>`
  (Dark Corners 720x1280; Battle Map 1280x720). Imports are served from the repo root (`/harness/...`, `/proto/...`,
  `/films/...`); copy prototype code into your folder rather than editing `proto/`.
- Blender scene (Clay): `blender.py` with `DURATION`, `SETTINGS`, `build(bpy, ctx)`, `frame(bpy, ctx, state, i, t)`
  (see `harness/blender_render.py`, `proto/p10-clay/blender.py`). Render: `python3 harness/blender_render.py films/... --w 720 --h 1280`.
- `film.json` `duration` must equal `KF.duration` / `DURATION` (the audio length). The render farm (rc-render
  `films.yml`) splits the frames into 12 to 20 parallel parts on 4-core CPU runners with no GPU (SwiftShader WebGL):
  **budget about 1 s per frame for web scenes and about 20 s per frame for Cycles at 720x1280**, measured locally on
  a few frames across the film. Cache expensive work (painted plates, baked terrain) per shot, not per frame.

## Quality bar
- Directed like film: a shot list against the cues, motivated camera moves, cuts on the narration and on the music's
  strong hits, real holds on key images, one colour script, the style's own motion language (the prototype NOTES.md).
- Every narrated idea gets a picture that makes it instantly clear. For Battle Map: a child must be able to follow who is
  where and what moves (two clear colours, simple unit blocks, arrows that draw on, names that pop in at the word).
- On-screen words are set in code: title card after the opening promise, the episode/battle title, place and date
  labels, short captions where the prototype style uses them. **No em or en dashes, no "..." on screen.**
- Dark Corners subjects are real atrocities (witch trials and torture, the Zong massacre, the blinding of prisoners,
  infanticide). Treat them with restraint: no gore, no bodies shown suffering, no drowning or torture shown literally.
  Show it the way the originals did: silhouettes, objects, documents, light, absence, symbols. Respectful, never
  sensational. Battle Map is for kids: armies are blocks, arrows and banners, losses are numbers and fading blocks, never
  wounds.
- History must match the narration exactly (dates, places, numbers). Do not invent extra facts on screen.
- End card: Dark Corners keeps its series card ("DARK CORNERS" + episode title) over the last `end_card_s` seconds;
  Battle Map ends on "BATTLE MAP" + the battle name and year.

## Working rules
- Check your own work: render stills at 8 to 12 key moments and a contact sheet, look at them, fix, repeat. Render one
  short moving stretch (5 s) to check motion. Report the measured seconds per frame.
- Commit often to `main` (only your folder plus any harness fix): `git add <your paths>; git commit -m "..."; git pull --rebase --autostash; git push`.
  Commit messages end with the two trailer lines given in your task. Never commit frames, mp4s or `out/`.
- Never touch API keys. Do not start GitHub workflows; the lead (Claude) dispatches renders.
- Time box: aim to have a complete, renderable film committed within about 3 hours, then polish.
