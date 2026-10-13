# KINOFORGE harness — how a scene is built, rendered and scored

Deterministic, headless, CPU-only. A scene is a web page that draws exact frames on demand; the renderer steps it
frame by frame in headless Chromium (SwiftShader), writes PNGs, and ffmpeg assembles the MP4 with the scene's
procedurally synthesised soundtrack. Blender scenes use the same contract through `bpy` (see "Blender scenes").

```
harness/
  render.cjs        node render.cjs proto/<scene> [--w 1280 --h 720 --fps 24] [--start a --end b] [--mp4] [--audio f.wav] [--contact] [--jpg]
  server.cjs        static server (so ES modules load over http)
  kit/film.js       the film kit: timeline, camera rig, textures, particles, light shafts, post (grade/grain/halation/letterbox/CRT/pixel/halftone/painterly), titles
  audio/sfx.py      procedural sound: drone, pad, riser, shepard, hit, braam, sub_drop, whoosh, wind, rain, hum, tape_hiss, crackle, fire, heartbeat, tick, tone, pluck, piano, choir + Mix (cue sheet, ducking, write)
  blender_render.py python3 harness/blender_render.py proto/<scene> --out out/<scene> [--w --h --fps --samples --start --end]
proto/<scene>/
  index.html        importmap + font links + <script type=module src=scene.js>
  scene.js          the scene (see contract)
  audio.py          cue sheet -> wav  (python3 proto/<scene>/audio.py out.wav)
  NOTES.md          direction: logline, shot list (size/lens/move/motivation), emotion tags, colour script, sound plan, what it proves
```

## Scene contract (Three.js / canvas)

```js
import * as THREE from 'three';
import { boot, CameraRig, makeComposer, Timeline, dustPoints, lightShaft, drawText, env, ease, rng, fbmCanvas, canvasTexture,
         heightToNormal, blurCanvas, toonGradient, smoothstep, clamp, lerp, noise1 } from '/harness/kit/film.js';

const SHOTS = [ { name: 'S1 ...', dur: 2.2 }, { name: 'S2 ...', dur: 3.0 }, ... ];   // seconds; total = clip length
await boot({
  fps: 24, shots: SHOTS, fonts: [['Cinzel', 700]],          // fonts come from /harness/node_modules/@fontsource/<name>/index.css (link it in index.html)
  init: async (ctx) => { /* build scene, camera, rig = new CameraRig(camera), post = makeComposer(renderer, scene, camera, {...}) */ },
  render: async (ctx, i, t) => {                             // MUST be deterministic in (i, t): no Date.now(), no Math.random() (use rng(seed))
    const sh = ctx.timeline.at(t);                           // { i: shot index, shot, t: local seconds, u: 0..1, name }
    /* animate by t, set camera per shot with rig.move(a, b, sh.u, ease.x).apply(), draw titles on post.overlay.ctx, then: */
    post.render(t);
  },
});
```

`makeComposer(renderer, scene, camera, { bloom: {strength, radius, threshold}, bokeh: {focus, aperture, maxblur}, grade: 'noir'|'tealOrange'|'bleach'|'painterly'|'cel'|'sepia'|'ember'|'vhs'|'pixel'|'halftone'|'none', finish: { letterbox: 2.39, halation, grain, vignette, aberration, fade, weave, exposure, contrast, saturation, lift:[r,g,b], gain:[..], shadowTint:[..], highlightTint:[..], mode, modeAmount, modeParams:[..], palette:[..] }, overlay: true, overlayAfterFinish: false })`
returns `{ composer, finish (live uniforms: post.finish.fade.value = 0 for black), overlay: { ctx, clear }, render(t) }`.
Set `overlayAfterFinish: true` when titles must stay visible over a faded-to-black frame.

Pure-2D scenes (motion comics, cut-outs, typography) can skip Three.js: create a canvas, draw with 2D context, and set
`window.KF = { width, height, fps, duration, canvas, shots, render: async (i, t) => {...} }; window.KF_READY = true;` yourself —
or keep `boot()` and draw into `post.overlay.ctx` with a black scene behind it to get the finish pass (grain, grade, letterbox) for free.

Units: 1 unit = 1 metre. Lights are physical (candela/lux): a dramatic key SpotLight is ~1500–5000 cd at 10–25 m; a candle PointLight ~20–60 cd.
Lenses: `rig.lens(mm)` (full-frame equivalent). Dust: `dustPoints({size: 0.03 /* metres */})` then `dust.update(t, camera, H)`.

## Render & review loop (what to actually do)

1. Build the scene, then render ONE frame per shot: `node harness/render.cjs proto/<scene> --start 20 --end 21` (frames land in `out/<scene>/frames/`).
   Tile them and LOOK at them (convert to jpg, Read the image). Fix composition, exposure (nothing blown out, blacks with detail where intended), separation (R-4-02), lens, continuity. Iterate until every shot reads.
2. Write `audio.py` from the shot timings: beds, details, a riser that ends exactly on the cut it motivates, real silence before the biggest hit (R-3-06), a hit on frame 1 of the title/reveal, tails.
3. Full render runs on GitHub Actions (push to `render/queue/*.json`), or locally: `node harness/render.cjs proto/<scene> --mp4 --audio out/<scene>/audio.wav --contact`.
   Local speed ≈ 1–4 s/frame at 1280x720 depending on post passes (painterly mode and bokeh are the slow ones).
4. QC against `docs/DIRECTORS_RULEBOOK.md` §9 blockers and the shot's own intent; log the pass in NOTES.md.

## Blender scenes

`proto/<scene>/blender.py` exposes `build(bpy, ctx) -> dict` (creates the scene, returns {camera, objects...}) and `frame(bpy, ctx, state, i, t)`
(poses everything for frame i). `harness/blender_render.py` sets Cycles (CPU, adaptive sampling, OIDN denoise, motion blur optional), renders
the range and writes PNGs with the same naming, so `render.cjs`'s ffmpeg step (or `ffmpeg -framerate 24 -i out/<scene>/frames/%05d.png`) assembles it.
Budget: 4-vCPU runner ≈ 20–60 s per 1280x720 frame at 64–128 samples with denoise; keep Blender clips ≤ 6 s or split with --start/--end across jobs.

## Rules that are not optional

- Deterministic frames (seeded RNG, time-driven animation). A re-render must be pixel-identical.
- Every camera move has a motivation written in NOTES.md (R-2-03). Locked-off shots are allowed and good.
- Cuts, not dissolves; vary shot lengths (R-3-04, R-9-12); hold faces/key images ≥ 24 f; silence before the big hit.
- One grade per scene, grain on every shot, vignette ≤ 0.5 stop, halation on highlights only (R-4-08).
- No generated/garbled text; titles are real type from the bundled fonts (R-9-07).
- No copyrighted characters, logos, lyrics, or living artists' names anywhere.
