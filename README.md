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
| p01 | Static | analog horror | CCTV corridor, VHS pass (curvature, chroma bleed, tracking band), a continuity-change scare, timestamp overlay |
| p02 | Ink & Ember | motion comic noir | comic-page grammar, parallax inside panels, halftone shadows, ink-blot wipe, one accent colour |
| p03 | The Lantern Road | 2.5D living painting | ten painted layers, multiplane parallax, Kuwahara painterly pass, lanterns lighting on cause→effect, a walk cycle on 2s |
| p04 | Witness | Blender Cycles interior | candlelight, f/2 rack focus, volumetric haze, torches through leaded glass, a head turn with anticipation |
| p05 | Relic | epic / trailer grammar | cold open → crane reveal → push-in turn → silence → title stinger; volumetric shafts, carved emissive runes, ember grade, 2.39 |
| p06 | Cel | cel-shaded anime | toon gradients, inverted-hull outlines, hue-shifted shadows, lightning on the thunder frame, a lamp that floods the frame |
| p07 | Ash Ascent | Blender Cycles aerial | physically based sky, a mesh-bounded cloud volume, a 1:60 rider, sunrise timed to a frame, hard cut to silence |
| p08 | Two Chairs | 2D dialogue comedy | Canvas 2D rig, Kokoro voices, Rhubarb visemes, blinks and breathing per the rulebook, rule of three with an 18-frame beat |
| p09 | Paper Kingdom | cut-paper shadow theatre | fibre-edged silhouettes, layered shadows from one backlight, puppets on 2s, three folds held six frames each |
| p10 | Clay | Blender claymation | subsurface clay with thumb-print bump, animation on 2s with per-pose jitter, volume-preserving squash |
| p11 | Kinetic | 9:16 typographic hook | safe zones verified per frame, snappy type with holds, a pattern interrupt, sound on every text beat |
| p12 | Terrain | relief-map explainer | heightmap terrain with engraved contours and hatching, a route that inks itself, projected labels, one motivated tilt |
| p13 | Pixel Vigil | pixel-art cinematic | true 320-px grid, palette quantisation and ordered dither, moves snapped to art pixels |
| p14 | Finishing | craft | `tools/finishing_compare.py`: the same shot raw vs finished with a moving wipe |

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
