# KINOFORGE

**A procedural cinema framework for directed, deterministic, CPU-rendered animation.**
Every clip is code: a shot list with motivations, a camera rig, procedural materials and particles, a film-finishing pass
(grade, halation, grain, letterbox, CRT/pixel/halftone/painterly modes), and a synthesised soundtrack placed from a cue sheet.
No GPU, no stock assets, no generated video: Three.js in headless Chromium (SwiftShader) or Blender (`bpy`, Cycles CPU), then ffmpeg.

The point is control. Models that generate video decide the camera, the timing and the physics for you; this framework
makes those decisions explicit, reviewable and re-renderable — the way a storyboard, a shot list and a colour script do on a film set.

## The anthology (example scenes)

`proto/` holds the project's example scenes — short "style tests" in the spirit of an animated anthology, each one
exercising a different look and a different part of the kit. CI renders them (`.github/workflows/render.yml`) and publishes
the clips to the [gallery release](../../releases/tag/gallery). Each scene ships with `NOTES.md`: logline, shot list
(size / lens / move / motivation), emotion tags, colour script and sound plan.

| id | title | lane | what it exercises |
|----|-------|------|-------------------|
| p05 | Relic | epic / trailer grammar | cold open → crane reveal → push-in turn → silence → title stinger; volumetric shafts, carved emissive runes, ember grade, 2.39 |

More scenes are added as they pass review against `docs/DIRECTORS_RULEBOOK.md`.

## Run it

```bash
cd harness && npm ci && npx playwright install chromium && cd ..
python3 proto/p05-relic/audio.py out/p05-relic/audio.wav            # soundtrack from the cue sheet
node harness/render.cjs proto/p05-relic --mp4 --audio out/p05-relic/audio.wav --contact
```
Blender scenes: `pip install bpy==5.2.2` then `python3 harness/blender_render.py proto/<scene> --mp4`.
See `harness/README.md` for the scene contract, the kit API and the review loop.

## Director's Rulebook

`docs/DIRECTORS_RULEBOOK.md` — 91 testable rules (`R-section-nn | rule | WHY | CHECK`) for story, shot grammar, editing rhythm,
lighting and colour, animation, trailer structure, storyboards, emotion, and an anti-"AI slop" checklist. Scenes are reviewed against it.

## CI usage

Renders are the project's regression set and gallery; they run on pushes to `render/queue/*.json` or by hand, one runner per
scene, 45-minute cap, results to a release. The workflow is deliberately modest (no cron, bounded parallelism, short artifact retention).

## License

MIT. Fonts are bundled from Fontsource (SIL OFL). No third-party media.
