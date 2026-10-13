# P13 — PIXEL VIGIL (10 s, 1280x720 render -> 320x180 art grid, 24 fps)

**Lane:** retro / epic pixel-art cinematic. **Logline (21 words):** On a rain-soaked neon rooftop a watcher waits for a signal; across the street, one amber window lights.
**Proves:** the kit's `pixel` mode can carry a *cut* scene: stable grid (layers move in whole art pixels), a deliberately small palette, animation on 2s with anticipation/overlap, a single warm accent reserved for meaning, and a chip-tune score that only exists once the signal arrives.
**Emotion arc (Plutchik):** S1 vigilance (anticipation, low) -> S2 surprise -> anticipation (rising) -> S3 resolve (anticipation -> trust).

## Shot list (final = code). 24 fps; cuts are whole frames, so the brief's 3.6 s / 7.2 s (86.4 f / 172.8 f) become f87 = 3.625 s and f173 = 7.208 s

| ID | frames / dur | size, lens, camera | move + motivation | light | sound |
|----|--------------|--------------------|-------------------|-------|-------|
| S1 | 0-86 / 3.625 s | EWS->WS, **28 mm**, roof eye-height cam (-1.75, 1.5, 8.0), pitch +4 deg | **Parallax truck + lens-shift pan, screen R->L** (the world slides right-to-left, as an animation "pan R->L"). Both are snapped to whole art px: pan 70 px (all depths) + truck 130 px at roof depth, per-layer parallax for the five depth layers (far 178 m, B3 93, B2 58, B1 32, roof 7.3). Ease: accel 10 % / cruise 60 % / decel 30 % over f0-74, then a 12-f hold (f74-86). Motivation: *searching* — the lens scans the skyline until it finds him; the scan ends where the character begins. He slides in at the right edge at ~f45 (decel phase) and stands at 79-86 % of frame width when the move lands | neon signs (magenta bars, cyan ring, magenta zigzag, cyan/magenta stack) flicker on fixed frames; rain; blimp + antenna beacons blink | rain, city hum, neon buzz with dropouts on the flicker frames, slow 2-note chip pulse |
| S2 | 87-172 / 3.583 s | MS (knee-up), **35 mm**, **low angle**: cam (0.9, 0.5, 4.8), pitch +13 deg, behind-left of him | **Locked-off** (static = dread/authority; the only motion is his). Motivation: let the eye wait on the dark window, then catch it | cyan rim (left, ring sign), magenta rim (right, zigzag/stack); at f130 the window lights, amber appears on his left shoulder/brim | weight shift f120 inside 14 f of near-silence (f116-129), chime on f130, arpeggio enters |
| S3 | 173-239 / 2.79 s | MCU (chest-up), **85 mm** telephoto, cam (2.0, 0.7, 6.7), yaw 11 deg (toward screen-left), pitch +8 deg | **Locked-off.** Motivation: the window sits in the slot between two towers, him big at the right; his step is the only move | amber window pulses (period 1.7 s, gentle), amber rim on his left shoulder + head, cyan/magenta rims continue | two footfalls f186 / f194, arpeggio tops on the glow peaks, wind gust f212->239, tail |

Hold on the key image (lit window + watcher in the slot, S3): f198-239 (42 f). S1 hold 12 f. Shot lengths 3.625 / 3.583 / 2.79 s (the brief fixes ~3.6 / 3.6 / 2.8, so they differ by only a couple of frames).
Screen direction: S1 image travels R->L (searching); his head turn in S2 and the window both sit screen-LEFT, and S3 keeps the window screen-left of him (R-2-05).
**Cut S2->S3 (R-2-06):** size step MS->MCU and lens 35->85 mm (strong perspective compression, new background: wall + window instead of skyline/blimp), but the camera-to-subject angle only changes ~14 deg (S2 bearing 12.5 deg left of his back axis, S3 1.9 deg right). It carries as a punch-in, not a 30-degree cut; what helps is that the composition is matched across the cut (window screen-left, watcher screen-right in both, S2 f172 -> S3 f173). Known weakness (see below).

### Watcher animation (all on 2s: pose time = floor(frame/2)*2)
- Breathing 4 s cycle (+-1.2 % spine scale, ~1 art px at S3), coat hem = 3 panels, each lagging the one above by 3 f (3 / 6 / 9 f behind the body: overlapping action), wind ramps 0.4 -> 1.3 with the gust f212->239.
- f120-131 weight shift: hips slide right 4.5 cm, torso counter-leans 2 deg, ease in/out.
- Reaction to the light (f130): latency 3 f, **anticipation f133-137** (head yaws 6 deg *away*, dips and lifts 1.2 cm), **turn f138-140** (to 42 deg, overshoot), **settle f141-150** (to 34 deg); shoulders follow a beat later (spine yaw +4.6 deg eased over f140-154).
- S3 step: lean-back anticipation f176-180, forward lean, **foot 1 plants f186**, **foot 2 closes f194** (planted-foot solver: leg angle = asin(root offset / leg length), so the planted foot does not slide); body drops 4.6 cm / 4.0 cm on the plants with the head settling 2 f later; at rest by f198, then breathing + wind only.

## Colour script / palette (R-4-05/06)
7 output levels per channel (kit: palette 6 -> k/6). Every colour is authored as a k-triple (0..6), so flat areas land exactly on a level and never speckle; only gradients (sky, clouds, halos, vignette) dither.
Navy/teal night (dominant) -> magenta + cyan neon (rims, signs) -> **amber (6,4,0) reserved for the window + his rim, absent from every frame before f130** (measured: 0 amber px on the pre-light frames checked, f0 / 44 / 86 / 87 / 128; 0.7 % of S2 pixels at f150; ~3.2 % of S3).
Measured at 1280x720 on 10 frames (320x180 block centres): 49-69 unique colours per frame including dither mixes, but only **18-25 colours cover >= 0.3 %** and 9-12 cover >= 1 % (the "visual" palette is ~20-25). 4x4 art-pixel blocks are uniform in 100 % of blocks on every frame measured -> the grid is exact.
Beat colours: S1 cold blue-teal + magenta haze; S2 same until f130, then the amber blooms and warms the left rim; S3 amber pulse is the brightest thing in frame.

## How the pixel grid is kept stable
- All geometry is unlit MeshBasic / vertex-colour in authored hex; tone mapping off, saturation/contrast 1, so authored hex = displayed colour before the quantiser.
- S1 pan = camera lens shift in whole art px (`setViewOffset(W,H,-px*blk,...)`, blk = 4 canvas px); the truck moves each depth layer by `round(px_layer) * depth / F1` world units so every layer moves by whole art px per frame. Rain and puddle reflections are painted in the overlay as whole 4x4 blocks.
- Sky shader time steps every 6 f; neon/halo/beacons flicker on fixed frames; the blimp drifts 1 art px / 7 f.

## Grade
`pixel` mode: pixelate to 320 px, palette [6,6,6], Bayer dither `modeParams.y` 0.08, saturation/contrast 1.0, grain 0, tone mapping off, no bloom (glows are SDF-falloff gradient quads that the quantiser turns into banded, dithered halos; the amber window glow is a normal-blend gradient because additive amber over navy turned beige).
**Vignette:** brief says 0.2, but the kit applies the vignette *after* quantisation (smooth, off-palette shades). `finish.vignette = 0`; the same ~0.25-alpha radial darkening is painted in the overlay (composited before the quantise pass) so it is stepped and dithered. Grain 0 for the same reason (and per brief). No letterbox.

## Sound plan (audio.py prints the cue sheet; frame times locked to picture)
rain 0.7 (two decorrelated stereo layers, wider/softer in S1, closer from f87) | city hum (hum 50 + drone lp 200, +-1.5 dB breathing, sinks into the held breath) | neon buzz (hum 120 + harmonic per sign, each detuned and dropping out on its own flicker frames — the FLICK tables are parsed from world.js; a tiny tick when a tube relights) | slow 2-note square pulse (A2/E3, lowpassed, -28 dB; pre-light notes on a 0.725 s grid whose 5th note is cut 1, the post-light notes re-lock a downbeat on cut 2) | cut accents: soft sub thump + air push on f87, thump on f173 | **held breath: everything -50 dB for f116-129 (14 f)** | **sine chime on f130** (the beds recover over 0.5 s under it) | soft 3-note square arpeggio (A4 C#5 E5, lowpassed + echo) **only after f130**: after the chime, on the S3 cut and again on the final glow peak | footfall thuds (hit sub 60, 0.32 s, -22 dB) + a wet slap on f186 / f194 | wind bed from f130, gust ramping f212->239 and a tail to 10.0 s | bell tail on the last glow peak.
Master: RMS -18 dBFS, soft-limited; verified duration 10.000 s, peak -1.97 dBFS; held-breath RMS -77 dBFS (56 dB under the beds).

## Kit quirks found (worked around in the scene; film.js / render.cjs untouched)
1. `pixel` mode applies **vignette and grain after quantisation** -> smooth, off-palette shades and a non-pixel look. Workaround: finish.vignette 0, grain 0, vignette painted into the overlay (which is composited before the finish pass).
2. The overlay canvas texture is treated as sRGB and decoded, darkening authored colours. Workaround: `post.overlay.tex.colorSpace = THREE.NoColorSpace`.
3. Default tone mapping (ACES) breaks the exact-palette premise; boot option `toneMapping: THREE.NoToneMapping` fixes it (not obvious from the README).
4. Author brief's default grain (0.03..) conflicts with this brief's grain 0 in pixel mode; the pixel brief wins.
5. Not a bug, but worth knowing: shot boundaries must be whole frames (the brief's 3.6 / 7.2 s are 86.4 / 172.8 f) — rounded to f87 / f173; `render()` picks the shot from the frame index so float time can never land a frame in the wrong shot.
6. The 7 output levels are 0 / 42 / 85 / 128 / 170 / 212 / 255 (k/6*255 with the half-levels rounded 42.5 -> 42, 127.5 -> 128, 212.5 -> 212); a palette check against 43 / 213 reports everything as off-grid.

## QC log (render one frame per shot -> look -> critique -> fix)
1. **First 640x360 render of S1/S2/S3.** Halos were huge rounded blobs (box SDF with a big reach) and per-face colours were wrong on tall boxes. Fix: halo rewritten (SDF hugs the sign outline, reach in metres, circle option for rings); `colorBox` classifies vertices by normal and supports world-y gradients.
2. **Amber window** looked beige/muddy (additive amber over cyan/navy) and the glow covered the mullions. Fix: normal-blend `mix` halo in K(6,3,0) placed behind the glass; neighbouring windows within 7x8 m forced dark so W is the only lit window.
3. **S3 framing**: a giant dark alley wall dominated and the watcher merged with a sign plate. Fix: B1 towers 6 m deep, zigzag moved out of S3, lower neighbour roofs, window raised to y 9.5, low cameras so the head sits against hazy wall/sky.
4. **S1 foreground**: a roof tank dominated frame 0 (removed with the vent stack); reflection streaks too faint (denser, 2-px wide for ring/eq); blimp position edits had no effect because scene.js overwrote x every frame (exported `BL_X0` constant).
5. **1280x720 check of the watcher** (crop at 1:1): read as stacked boxes — black side faces + seam strips drew a cage-like rectangle, flat shoulders. Fix: torso is one extruded back-view outline (sloped shoulders, tapered waist) in a single flat navy; sleeves one step lighter; seams removed (belt kept); shoulder rim strips follow the slope; hat gets a thicker brim with a lit underside and a stepped (pinched) crown.
6. **Tangents**: B1b mast beacon touched the hat brim in S2 (x 6.1 -> `avoid` ranges in `roofClutter`); roof-mast beacon touched the blimp at f0 (mast 4.2 -> 3.3 m); a B2 mast pierced the blimp belly (avoid range -22..-6).
7. **Motion bursts** (12 frames @640x360 each): head turn f128-150 — anticipation, turn and settle read (hat brim widens, shadowed side face appears, amber rim travels); shoulders now follow 8 f later. Step f176-198 — the two plants were too quiet at 85 mm (upper body only) -> bob 2.8/2.4 cm -> 4.6/4.0 cm, head lags 2 f. Pan: snapped to whole px by construction; far layer moves 1-2 art px/frame at peak, nearest layer ~3.4 px/frame.
8. **Cut 2 re-timed**: the first build cut at f174 (7.25 s, 1.2 f late vs the brief's 7.2 s = f172.8). Moved to f173 (S2 86 f, S3 67 f); the window pulse phase, the arpeggio/bell on the glow peaks (7.64 / 9.34 s) and the pulse downbeat in audio.py re-locked; f172 -> f173 viewed side by side: window and watcher keep their screen sides.
9. **Measurements** (1280x720 frames f0,44,86,87,128,150,173,174,200,239): grid uniform 100 %, visual palette 18-25 colours, no amber on the pre-light frames. Final `render.cjs --start 0 --end 1` clean; frame 0 identical to the dev render (deterministic).

## Weaknesses / what more time would fix
- S2->S3 is a punch-in with only ~14 deg of angle change (see above): re-layout so S3 is shot from ~30 deg round to his right (the slot would need to move) or add a 3-frame match element across the cut.
- S1 is long on wide geometry but short on a foreground: the roof below the parapet is mostly empty (reflection dashes only). A pipe/vent in the near layer would sell the parallax more. The mast + beacon at the roof depth carries it for now.
- The head turn is read through silhouette changes only (no face): at 320 px it is 3-4 art px of change; a nose/cheek lit by the amber would sell it harder.
- Shot lengths 3.625 / 3.583 / 2.79 s vary only by a few frames (the brief dictates them); a freer cut would lengthen S1 to ~4 s and tighten S3.
- Dither: Bayer 4x4 at 0.08 gives clean bands; the vignette (overlay) steps visibly in the corners — intended, but it could be lighter.
- No lightning (optional in the brief) and no letters on any sign (R-9-07).
