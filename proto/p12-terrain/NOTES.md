# P12 — TERRAIN (10 s, 16:9, 1280x720, 24 fps)

**Lane:** edutainment / cinematic map explainer.
**Logline (24 words):** A lost 1840s expedition's last known route is inked across a relief map; the camera descends until the trail ends at a black tarn.
**What it proves:** a 3D relief that reads as a *drawn / engraved* map, not CG terrain — baked low-sun hillshade with cast shadows, shader-analytic contour lines (wobbly, Tanaka-weighted so they thicken and multiply in the shade), engraver's 45-degree hatching, vegetation stipple, watercolour hypsometric washes on foxed parchment, a dashed ink route drawn progressively by an unseen pen (bleed halo, wet head, ink running dry), 3D-projected micro-labels, and ONE continuous motivated tilt-and-descend move that follows the pen. Everything (terrain, erosion, route, lighting, textures, sound) is procedural and original; the only third-party assets are the two OFL typefaces the harness already ships (@fontsource Cinzel 600, Cormorant Garamond 500 italic).
**Emotion tags (Plutchik):** S1 anticipation (interest) -> S2 anticipation rising to apprehension -> S3 sadness (pensiveness) under awe.

## Shot list (FINAL — equals the code: `timing.js` + `camera.js` + `scene.js`)

| ID | frames / time | dur | size / lens | move + motivation | light | sound |
|----|---------------|-----|-------------|-------------------|-------|-------|
| S1 top-down, the pen starts at Camp II | f0–86 · 0–3.625 s | 3.625 s | EWS top-down 89.9 deg (map-reading authority), 35 mm, camera 197 high | **locked-off.** The only motion is ink: CAMP II pops f8, pen touches down 0.60 s, caption 1 fades in 0.85 s | low warm sun, az 315 / el 30 (from the NW), cool sky fill, baked cast shadows | wind, drone, paper hit f8, quill from 0.60 s |
| S2 tilt + descend following the pen | f87–182 · 3.625–7.625 s | 4.0 s | WS -> MWS, 35 mm; pitch **89.9 -> 34.0 deg**, camera 197 -> 131 high, 36 units east | **ONE eased move** (smootherstep rest -> rest, 2 % pre-settle for anticipation), starting from the *identical* S1 frame; the look target rides ahead of the pen so the tilt is motivated by "following the route"; peak rate 1.2 deg/frame at the middle, no drift. THE BLACK TARN pops f142, THE SADDLE f171 as their anchors come into view | same sun, dim 1.0 -> 0.84 and haze 0.15 -> 1.3 as we drop into the valley | choir swell, tick 90 bpm (S2 only), paper hits on TARN / SADDLE |
| S3 low oblique, the trail ends at the tarn | f183–239 · 7.625–10.0 s | 2.375 s | WS, low oblique 10.2 deg below the horizon, **28 mm**, camera 72 high, peaks against the sky | **locked-off** (dread / deadpan). Hard cut from S2: view direction changes 34.5 deg, camera moves 87 units (64 W, 59 lower), pitch 34 -> 10 deg, lens 35 -> 28 mm. Route completes f201 (8.375 s), pen lifts, marker rings appear; caption 2 at 8.72 s. **Hold on the key image f201–239 = 39 frames** (the shot itself holds 57 frames) | sun thinned to 84 %, haze at its thickest, pale warm sky | quill dies, 12 frames of near-silence f189–200, low hit + 880 Hz ring on f201, drone to the end |

Cuts only (no dissolves): the S1 -> S2 boundary is a continuous camera move from rest (no picture cut); the only hard cut is S2 -> S3 on f183. Shot lengths 3.625 / 4.0 / 2.375 s.

Overlay: three labels (Cinzel 600, 13 px at 720p, tracking 0.2 em, cream fill + dark outline, hairline leader for the two "above" labels) projected from 3D anchors on the heightfield — CAMP II (f8), THE BLACK TARN (f142), THE SADDLE (f171) — pop = alpha 0.22 s + scale 0.82 -> 1 with a small overshoot, fade at the frame edge, and fade when the terrain hides the anchor (heightfield ray march). Pop times were taken from `tools/scan.mjs` (first frame the anchor is inside the safe frame and unoccluded). Captions (Cormorant Garamond italic 500, 40 px, left at 7 % margin, soft lower scrim, 0.5 s fades): "They left Camp II on the ninth of October." 0.85–3.75 s; "The trail ends here." 8.72–10.0 s.

## Colour script
Warm parchment + sage / ochre washes (S1) -> cooler greys and deeper shadow as the camera climbs into the cirque (S2) -> slate peaks against a pale warm sky with a darker, hazier valley (S3). Values in code: sun (1.40, 1.07, 0.72) x dim, sky fill (0.20, 0.25, 0.36), ground bounce (0.15, 0.105, 0.065), engraving ink (0.085, 0.052, 0.034), fog / horizon (0.86, 0.76, 0.62), zenith (0.60, 0.68, 0.80); the tarn is black ink with engraved ripple lines. The red-brown route / ring (#7a1f1f after the grade; the linear ink is pre-compensated for the sepia desaturation) is the only saturated hue and covers well under 3 % of any frame.
**Grade:** kit `sepia`, tuned — saturation 0.55, contrast 1.12, warm highlight tint [0.04, 0.026, 0], slightly blue shadow tint [-0.012, 0, 0.03], grain 0.04 (size 1.4), vignette 0.4, letterbox 0, halation 0 (see performance). One grade for the whole clip. Tone mapping: `THREE.NeutralToneMapping` (the kit's default ACES bleached the parchment).

## Sound (audio.py -> out/p12-terrain/audio.wav, 48 kHz 24-bit stereo, 10.000 s)
Timings come from `timing.json` (generated by `tools/timing.mjs` from `timing.js`, the same module the picture uses; the quill follows the same pen-speed curve that inks the route).

| time | frame | cue | dB |
|------|-------|-----|----|
| 0.000 | 0 | drone A1 55 Hz, lp 400, to the end (fade-in 1.6 s, tail 0.5 s) | -24 |
| 0.000 | 0 | wind 0.4, decorrelated L/R pair, opens up in S3 | -30 each |
| 0.333 | 8 | paper hit: CAMP II | -14 |
| 0.600 | 14 | quill = crackle highpassed, gated by the pen-speed curve, runs exactly 0.60 -> 8.375 s (while the route draws) | -22 |
| 3.625 | 87 | choir swell (A2 E3 A3), across the tilt-down, quadratic rise, tail to 7.75 s | -26 |
| 3.625 | 87 | tick 90 bpm, S2 only (the beat that would fall on the cut never comes) | -30 |
| 5.917 | 142 | paper hit: THE BLACK TARN | -14 |
| 7.125 | 171 | paper hit: THE SADDLE | -14 |
| 7.875–8.375 | 189–200 | **12 frames of near-silence**: whole mix ducked -30 dB (the thinning quill rides +10 dB first so the dying pen is the last thing heard) | -30 |
| 8.375 | 201 | LOW HIT (sub 38 Hz) on the frame the pen lifts and the marker appears | -12 |
| 8.375 | 201 | marker ring: sine 880 Hz, slow exponential decay, re-excited softly on the two ink ripples (+0.35 s, +0.80 s) | -22 |

Verified with soundfile + numpy: duration **10.000000 s**, peak **-2.79 dBFS** (< -1), no clipped samples. Silence window RMS -55 dBFS, peak 37 dB under the hit (rulebook R-3-06: >= 12 frames at >= 20 dB under the next hit); frames 189–200 peak between -39 and -48 dBFS, frame 201 -4 dBFS. `out/p12-terrain/audio_view.png` = waveform / RMS / spectrogram. (Not auditioned by ear — there is no audio device here; checked by numbers and spectrogram.)

## QC log (render one frame per shot -> Read -> critique -> fix)
Questions asked every time: does it look like a drawn / engraved relief map lit by a low warm sun? are the labels tiny and precise? does the route read as ink?

**Iteration 1 — first real render (one frame per shot).**
- F1 no contour lines or hatching anywhere, just a smooth hillshade (it read as CG terrain): the water mask in the shader was inverted (lake value is 9 on land) -> fixed; contours, tone contours and hatch appeared.
- F2 haze ~30 % at S1 and the "black" tarn lifted to grey: fog far too dense -> low base density, haze ramps 0.15 -> 1.3 over 3.4–8.0 s, edge fade moved out to 185–275 units, fog on water cut by 80 %.
- F3 the cross-hatch read as a chain-link / wire mesh at oblique angles -> single 45-degree stroke family, faded by view angle (it exists only when the sheet is seen from above).
- F4 route nearly invisible in S2 / S3 (thin, same value as the hatching, red washed out by the sepia saturation) -> half-width 0.90 growing with distance^0.30, longer dashes (4.2 / 1.9), ink authored in display space and pre-compensated so the graded line lands near #7a1f1f, wider darker bleed halo, wet head.
- F5 dash ends flickered at the pen head: screen derivatives were taken after `discard` -> fwidth hoisted above the discard.

**Iteration 2 — composition of S2-end / S3 (renders plus `tools/view.mjs` previews).**
- F6 THE SADDLE anchor sat in a pit behind the headwall and the skyline had no V-notch (nothing to label): replaced the rim notch by a carved pass trench (V on the skyline) and added priority-flood pit filling to the erosion so no closed "potholes" remain.
- F7 the S3 camera from the west hid the route behind a foreground spur and the cut from S2 was too weak: S3 moved to the valley axis (-34, 72, -52, 28 mm) and S2's last frame to the east bank -> the cut now changes the view direction by 34.5 deg (rulebook R-2-06: >= 30 deg and/or a size step), with a different lens and a 24 deg lower pitch.
- F8 route head sat at the very bottom edge of the frame at the S2 end: accepted — only the last ~40 units of route are in shot there by design (the camera looks ahead of the pen at the tarn); the marker image is S3.

**Iteration 3 — labels, captions, tarn (S1 / S2 frames, crops of the labels).**
- F9 labels popped before their anchors were in frame or while occluded: pop times retimed from measured visibility (`tools/scan.mjs`): TARN 5.917 s, SADDLE 7.125 s; labels now fade at the frame edge and when the terrain hides the anchor.
- F10 caption lost against the busy hatch in the lower left: soft lower scrim (rgba 24,14,8 at 0.42), dark shadow, left-aligned at 7 %, 40 px Cormorant italic -> legible without a title card.
- F11 tarn read navy-grey after the fog change and its shoreline slightly blue: water colour darkened to near-black, ripple lines kept at 0.30 weight, fog on water reduced.
- Motion burst: 12 frames of the S2 tilt (f128–139, 640x360, 6 columns, `out/p12-terrain/burst_s2_tile.png`) -> one continuous move, no stalls, reversals or drift; the tarn slides in from the top edge at f137.

**Iteration 4 — final pass (frames 0, 70, 130, 182, 228 at 1280x720, `out/p12-terrain/keyframes.jpg`).**
- F12 render cost (see below): halation off (<= 3/255 change), paper anisotropy 8 -> 1 (< 0.2/255 change), MSAA only once there is a skyline (S2 u >= 0.34); checked MSAA 4 vs 0 at the switch frame f120 (0.01 % of pixels differ by > 10/255, so the switch is invisible) and on the S3 skyline (it staircases without MSAA, so S3 keeps it); a sequential 640x360 render across f118–122 shows no discontinuity.
- F13 paper hit was almost as loud as the final hit (raw peak 1.0 at -14 dB): scaled to 0.6 peak before the cue gain so the label taps stay subordinate to the low hit.
- Final clean render `--start 0 --end 1`: no page errors, no warnings.

## Render speed (1280x720, SwiftShader, 2 shared cores at load average 5–9)
Single-frame `render.cjs` invocations: 5.7–10.8 s (including about 4 s page init and the ~3 s first-frame shader compile). Steady state inside one session, measured as Chromium CPU seconds / wall: S1 and the first third of S2 **2.3 CPU-s (4.2 s wall at load 8)**, late S2 / S3 **3.4–3.9 CPU-s (4.3–6.9 s wall at load 8)**; about 3.0 CPU-s per frame averaged over the clip, which is roughly 1.5 s per frame on an idle 2-core box (estimate). Where it went before the fixes: MSAA x4 +1.4 s on the heavy terrain shader, halation 0.4 s, paper anisotropy 0.4 s, ~25 noise fetches 0.5 s, the 1.25-unit mesh (247 k triangles) shading duplicates ~0.8 s. A coarser mesh (2.0–2.5) saves 0.7–0.8 s but facets the silhouettes and makes contour lines saw-tooth at the ridges, so it was rejected.

## Known weak points and how to fix them
- The east massif in S1 is plain ochre — add scree stipple / hachuring on the steep, sunlit faces.
- Contours on large smooth S3 hills are very regular (layer-cake); vary the interval with a slow noise or draw only every 5th line near the ridge.
- 13 px labels are as small as the brief wants but are at the legibility floor on phones; 15 px would still read as "tiny".
- The shoreline ripple lines of the tarn are still slightly blue at the edge.
- Baking the ~7 low-frequency noise fields (`cloud`, `fox`, `wd`, wobbles) into one RGBA8 aux texture would save another ~0.4 s/frame.
- Sound was checked numerically only.

## Kit bugs / limitations found
- `loadFonts()` cannot request an italic face (workaround: `document.fonts.load('italic 500 20px "Cormorant Garamond"')` in `init`).
- `makeComposer` render targets have no MSAA (skyline and ridge edges alias); workaround `composer.renderTarget1/2.samples`, and both are needed because the ping-pong swaps every frame; changing it needs `dispose()`.
- `boot()` defaults to ACES, which bleaches parchment; `toneMapping: THREE.NeutralToneMapping` works.
- `valueNoise2D` is exported by the kit but missing from the README import list.
- The finish pass's 12-tap halation costs ~0.4 s/frame at 720p in SwiftShader (about 10 % of this scene) and at the 0.12 used here it changed <= 3/255: worth a half-res option or an early-out.
- `render.cjs` prints s/frame only every 24 frames or at the end, so single-frame runs include the first-frame shader compile.

## Files and how to run
`scene.js` (boot, per-shot camera, colour script, overlay, labels), `index.html`, `terrain.js` (height model, erosion, pass, tarn, camp, A* route, river), `bake.js` (low-sun cast shadows + sky visibility), `world.js` (builds the shader textures), `materials.js` (terrain / route / river / sky shaders, paper + noise textures, relief mesh), `camera.js` (poses + `kS2`), `timing.js` + `timing.json` (single source of truth for picture and sound), `tools/` (`view.mjs` ray-marched camera preview, `scan.mjs` anchor visibility + S2 path rates, `preview.mjs`, `routeinfo.mjs`, `timing.mjs`), `audio.py`.
```
node proto/p12-terrain/tools/timing.mjs        # after editing timing.js
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node harness/render.cjs proto/p12-terrain --start 0 --end 1
python3 proto/p12-terrain/audio.py out/p12-terrain/audio.wav
```
Debug URL params (`--param k=v`): `dbg=1` init timings, `cam=x,y,z,lx,ly,lz,mm`, `dbgmode=1..6` (height, bake, contour phase, albedo, light, lines+hatch), `lift=`, `msaa=0|4` (force; default gated by shot).
