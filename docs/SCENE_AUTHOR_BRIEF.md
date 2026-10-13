# Scene author brief (read fully before touching code)

You are building ONE example scene for KINOFORGE, a procedural cinema framework. You are the director, DP, animator and
sound designer of a 6–12 second clip that must look deliberately crafted: composed, lit, cut and scored on purpose.
Judge your own frames like a picky film editor would. "It renders" is not the bar; "a stranger would believe a person framed this" is.

## Where things are
- Repo: `/home/claude/kinoforge` (git; do NOT commit or push — the lead does). Your scene lives in `proto/<scene-id>/`.
- Harness API & contract: `harness/README.md` (read it). Kit source: `harness/kit/film.js` (read it; it is the API you call).
- Reference scene to imitate structurally: `proto/p05-relic/scene.js`, `proto/p05-relic/audio.py`, `proto/p05-relic/NOTES.md`.
- Rulebook: `docs/DIRECTORS_RULEBOOK.md` — your shot list must satisfy §2 (motivated moves, lens per shot), §3 (cut rhythm, silence before the hit), §4 (motivated light, separation, one grade), §5 (anticipation/holds/eases), §9 (anti-slop blockers).
- Sound kit: `harness/audio/sfx.py` (procedural: drones, risers, hits, rain, wind, crackle, pluck, piano, choir, tick, heartbeat, Mix with ducking). Speech: `harness/audio/tts.py` (Kokoro voices + Rhubarb visemes) — only if your brief uses voice.
- Fonts (link the CSS in index.html, then list them in `boot({fonts})`): Bebas Neue, Inter, Playfair Display, Special Elite (typewriter), VT323 (terminal), Cinzel, Bangers (comic), Cormorant Garamond, Oswald, Press Start 2P (pixel), Permanent Marker, IM Fell English. Path: `/harness/node_modules/@fontsource/<kebab-name>/index.css`.

## How to work (the loop)
1. Write `NOTES.md` FIRST: logline (≤25 words), the shot list table (ID, duration, size/lens, move + motivation, light, sound), emotion tag per shot, colour script, grade, what the scene proves. Durations must sum to the brief's length.
2. Build `index.html` + `scene.js` (+ `blender.py` for Blender scenes). Deterministic: seeded `rng()`, animate by `t`. No network, no external assets, no Math.random/Date.
3. Render ONE frame per shot (pick a representative frame index per shot):
   `cd /home/claude/kinoforge && PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node harness/render.cjs proto/<scene-id> --start N --end N+1`
   Frames land in `out/<scene-id>/frames/NNNNN.png`. Tile them into `out/<scene-id>/keyframes.jpg` (PIL) and LOOK at the image with the Read tool.
   Blender scenes: `python3 harness/blender_render.py proto/<scene-id> --w 640 --h 360 --samples 24 --start N --end N+1` for checks (keep them small; CPU is shared).
4. Critique each frame honestly: exposure (no blown whites unless intended, no mud), subject separation from background, lens/size matching the shot's purpose, composition in depth (foreground/mid/background), scale cues, readable silhouettes, nothing that reads as "default 3D" (grey plastic, centred eye-level medium shot, flat light). Fix and re-render. Do at least 3 iterations; write each finding in the NOTES.md QC log.
5. Motion check: render a short low-res burst of one shot (e.g. 12 frames at 640x360 via `--w 640 --h 360 --start a --end a+12`) and tile 6 of them to confirm the move eases and the animation has anticipation/holds (R-5-01). Do NOT run a full 1280x720 render here (CI does that); at most one 640x360 full-length pass if you need to see cut rhythm.
6. Write `audio.py` from the FINAL shot timings (import pattern as in p05). Every hit on a cut, risers end on the cut they motivate, ≥12 frames of real silence before the biggest hit, tails, beds with slow movement, no loop repeats. Run it: `python3 proto/<scene-id>/audio.py out/<scene-id>/audio.wav` and verify duration == clip length and peak < -1 dBFS (soundfile + numpy).
7. Final: ensure `node harness/render.cjs proto/<scene-id> --start 0 --end 1` works clean (no page errors), update NOTES.md (final shot list = code), and report.

## Hard rules
- Original content only: no existing characters, brands, logos, lyrics, titles, or living artists' names. Fictional names and places.
- No generated/garbled text in-world (R-9-07): signs are abstract shapes, real type is drawn with the bundled fonts.
- Moves: every camera move names its motivation in NOTES.md; locked-off shots are good. No dissolves; cuts only (an ink wipe/whip is allowed only if the brief says so).
- One grade per scene; grain on every shot (`grain` 0.02–0.08); vignette ≤ 0.45; halation only on highlights; letterbox only if the brief says.
- Shot lengths vary (never 4 equal in a row); a hold ≥24 frames on the key image; sound has a cue sheet printed by audio.py.
- Keep per-frame cost sane: SwiftShader is software GL. Avoid `bokeh` unless the brief asks; keep particle counts ≤ 4000; `painterly` mode (Kuwahara) costs ~2–3 s/frame — fine. Target ≤ 4 s/frame at 1280x720.
- Do not edit `harness/kit/film.js` or `harness/render.cjs`. If you need a helper, put it in `proto/<scene-id>/` (or `harness/kit/<scene-id>-extras.js`). If you find a kit bug, work around it and REPORT it.
- Do not commit, push, or touch other scenes' folders.

## What to return
≤ 200 words: the clip's final shot list in one line each, what reads well, what is still weak and how you'd fix it with more time, measured render speed (s/frame at 1280x720 for one frame), the path of `out/<scene-id>/keyframes.jpg`, and any kit bugs found.
