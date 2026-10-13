# P02 — INK & EMBER (10 s, 16:9 1280x720, 24 fps, 240 f)

**Lane:** dark storytelling / illustrated history — motion-comic noir. Style sheet: DIRECTORS_RULEBOOK §10 "Ink & Ember".
**Logline (17 words):** A courier crosses a rain-soaked city at night to deliver a sealed letter she must not read.
**Proves:** a pure Canvas-2D motion comic finished by the kit's ONE grade (halftone-in-shadows mode 3, grain, vignette,
halation on highlights only); comic page grammar (the panel border inks itself onto the page, the page re-flows to two
panels with the previous one dimmed, captions in boxes); 2.5D lens language (24 / 85 / 40 mm as layer parallax, dolly
scale and pre-blur); noise-modulated brush-ink ribbons; cel light bands from one hard key per shot; one accent colour bound
to one story object (the Ember Red seal); readable eyes with a dart + 2/1/3 blink; lightning sound and picture on one frame;
the single allowed ink-blot wipe into 12 frames of true silence, then the chapter-card hit.

## Final shot list (= scene.js; integer frames, so every cut and every audio cue share exact times)

| ID | frames | dur | size / lens | move + motivation | light (source) | sound | emotion (Plutchik) |
|----|--------|-----|-------------|-------------------|----------------|-------|--------------------|
| S1 | 0–61 | 62 f / 2.583 s | EWS roofscape, 24 mm (F≈853 px), 5 layers: sky ∞, far skyline 800 m, mid roofs 90 m, street 30 m, near roofs 18 m + rain 40/12/4 m | page rises from black f0–5, border inks itself clockwise f1–10, image develops out of the paper f8–20; **truck right 1.6 m** (inOutSine) = following the wind-driven rain, and it reveals the courier from behind a near chimney (near layer moves 76 px, street 46 px) | teal city-glow on the cloud base, sodium windows, dormer window, street lantern (practicals); **lightning main stroke f26**, restrike f28, decay to f33 = hard key from the sky, rooftops snap to silhouette with bone rims | rain bed + gusting wind, cello drone enters, brush-on-paper swish under the border, **thunder crack 1.100 s (inside f26)** + restrike + rolling rumble | apprehension → surprise |
| S2 | 62–129 | 68 f / 2.833 s | MCU hooded near-profile, 85 mm (background compressed, pre-blurred 10 px, darker); page: P1 city strip dimmed left, P2 right, slanted gutter | **locked-off** (stillness; she waits) | wall lantern upper right = the one hard key (sodium amber, cel bands, ≈10:1), sea-teal rim from the wet street behind; lantern swings ±2.9° (extremes 2.9 s / 4.1 s) | piano A3 on the cut, lantern creak ×2 at the swing extremes, breath swells 3.0 / 4.583 s (puffs f72 / f110), rain closer | anticipation → surprise/guilt: caption f67–69, eyes dart to camera f101–103 (1-frame counter-move f100), blink 2/1/3 f108–113, holds the look to the cut (26 f) |
| S3 | 130–186 | 57 f / 2.375 s | ECU gloved hand + letter (her POV), 40 mm, 4 layers: wet cobbles 1.6 m, rain 1.0 m, hand/letter 0.5 m, near rain 0.3 m; page: her face strip (dimmed AND desaturated) left = eyeline, P3 right, skewed | **slow dolly push-in** toward the seal (subject ×1.12, near rain ×1.22, ground ×1.03; u^1.6, accelerating into the cut) = temptation. Thumb acting (on 2s): rest 8 f → pull-back 6 px over 6 f (anticipation) → reach 32 px over 22 f → hesitate 7 f at the seal's edge → drop → flinch −16 px in 3 f (on 1s) → settle over 10 f | same lantern from above, rendered drained (bone/slate/ink) so the **Ember Red seal is the only hue in the frame** (verified: all saturated pixels lie inside the seal); its blurred reflection in a puddle is the practical | piano E4 on the cut, F4 at 6.8 s (minor second), quiet riser 6.6→7.792 s, **drip on the seal 7.000 s = f168** (crown splash on that frame, ink ripple rings from f169) | anticipation → fear (temptation) |
| S4 | 187–198 | 12 f / 0.5 s | ink-blot wipe (the one allowed): splat on the seal, ragged periodic-noise edge, 11 tendrils, 46 spatter drops with 1-frame streaks; full black by ≈f195 | — (blot on 1s) | — | **SILENCE 12 f at −141 dBFS** (R-3-06); the riser ends exactly on f187 | — (void) |
| S5 | 199–239 | 41 f / 1.708 s | chapter card on the same ink paper: "CHAPTER ONE" (Oswald 400, bone 80 %, wide tracking) over "THE SEAL" (Oswald 600, 158 px, bone), brush rule, small red seal mark as the full stop; left-aligned block, off-centre | locked-off hold | — | **low card hit −8 dB on f199** + sub drop + A2-E3-A3 tail pad, distant rain returning as room tone | anticipation (open question: what is in the letter?) |

Sum 62+68+57+12+41 = 240 f = 10.000 s. All lengths differ (CV ≈ 0.5). Holds ≥24 f on the key images: S2 face 68 f, S5 card 41 f.
Moves: 1 truck (S1) + 1 push (S3) = 20 % pushes; locked-off S2/S4/S5 = 60 % (style sheet: locked ≥60 %, pushes ≤20 %).
Eye-trace across cuts: S1 ends on the lantern-lit courier (≈x780 y600) → S2 eyes (≈x900 y275) → S3 seal (≈x898 y354; her
desaturated face in the left strip looks down-right at it = eyeline match) → S4 blot starts on the seal → S5 type block left.
Screen direction: the courier faces right (L→R progress) in S1, S2 and the S3 strip.

## Colour script (measured, nearest-swatch share in CIELAB, after the grade)
S1 cold navy/teal glow + small amber practicals (Ink 60 %, Navy 34, Slate 5, Bone 1, Amber 0.4) → f26/f28 bone-white flash
(Bone 28 % for those 2 frames — intended) → S2 warm sodium key on ink, teal rim (Ink 63 %, Navy 27, Slate 7, Bone 2, Amber 1.0)
→ S3 drained bone/slate/ink + Ember Red seal only (Ink 58–61 %, Navy 17–18, Slate 8, Bone 12.9 → 13.9 → 15.6 % over the push
— just over the cap only in its last frames, Ember 0.5) → S4 ink → S5 ink page, bone type, one red mark (Ink 85 %, Bone 4,
Ember 0.1). Ember Red appears ONLY on the seal (S3) and its mark (S5).

## Grade (one for the scene) — kit `halftone` preset, tuned
mode 3 halftone in shadows, modeAmount 0.6, cell 5 px, angle 0.6; **gamma 1.3** (see QC v3: pre-compensates the halftone's
shadow darkening so drawn swatches survive on average), contrast 1.04, saturation 1.0, no shadow/highlight tints (teal–orange
split-toning is forbidden), halation 0.35 above luminance 0.86 only (lightning, lantern core, puddle reflection), grain 0.05
(size 1.5) on every shot, vignette 0.3, no letterbox. All drawing uses the seven style-sheet swatches (+ derived bands).

## Sound (audio.py prints the cue sheet; verified with soundfile + numpy)
Duration 10.000000 s (480000 samples, 48 kHz, 24-bit stereo); peak −2.86 dBFS; RMS −19.6 dBFS. Thunder onset 1.1000 s (inside
f26), restrike visible in the envelope at 1.18 s (f28); drip onset 7.0000 s (f168); card onset 8.2919 s (f199 = 8.2917).
Silence f187–198 at −141 dBFS, i.e. 132 dB under the card hit; the card hit is the loudest event (peak −2.86 vs thunder −3.88,
RMS −9.6 vs −13.6). Everything before S4 (including reverb tails) is removed for good at the cut, so nothing leaks under the card.
Beds move slowly (gusting wind, drifting drone filter), every instance is generated fresh (no loop repeats), every hit has a tail.

## Motion check (R-5-01) — 640x360 bursts via render.cjs (out/p02-ink-ember/burst) + one 640x360 full pass (out/…/lowres)
- Thumb displacement (px along its axis) by S3 frame: 0 ×8 → −1.5, −4.5, −6 (anticipation) → −5.4 … +26 (eased reach on 2s)
  → hold 26 ×7 → 14.7, 10.6, 10.0 (flinch on 1s) → 10.6 … 16.0 (settle over 10 f). Burst A (f134–145) and B (f164–175) tiled:
  pull-back reads, the falling drop streak is visible f165–167, crown splash f168, rings f169–175, droplets fall under gravity.
- Eye beats checked frame by frame at 3x crops: counter-move f100, dart f101–103 (≈8 px), blink 2/1/3 with a faint slate lid
  line while closed, glints on the lantern side.
- Full-pass frame-difference scan (160x90): the only spikes are the flash (f26–31), the cuts (f62, f130, f199), the blot
  (f187–198) and the opening rise (f4–6); inside shots the difference is flat (median 1.4–1.9) → no flicker/boiling (R-9-01).
- Re-render of f118/f165 in a fresh session, different order: sha1 identical (deterministic).

## QC log
- v1 KIT BUG: the overlay CanvasTexture is tagged sRGB, so the GPU linearises it on sampling and no pass re-encodes it — every
  2D colour came out ~2.2-gamma too dark (probe: mid-grey 128 → 55, bone 217,207,188 → 177,159,128). Workaround in scene.js:
  `post.overlay.tex.colorSpace = THREE.NoColorSpace` (exact 1:1 after the fix). Kit not edited — please fix in film.js.
- v1 (first look): lightning frame and the seal ECU already strong. Problems: page and panels the same value, so the comic
  grammar didn't read; S1/S2 92–93 % Ink (mud, not noir); hood read as a helmet/bowl; face too small for an MCU; collar like a
  cat ear; hard teal "column" in the S2 background; thumb a black stick, hand an amorphous mass; envelope oversized (Bone 24 %).
- v2: charcoal paper page (borders now read), lifted S1 sky + darker far skyline so it silhouettes before the flash, street
  layer closer (courier 1.25x, stronger rim); S2 rebuilt — cowl with a drooping back peak, seam/drape folds, figure scaled 1.3x,
  lantern moved; S3 rebuilt — glove in slate leather with three stitch lines, index finger wrapping the edge, thicker thumb with
  joint crease, envelope 13 % smaller with heavier shadow-side line weight, hatching and flap shadow; lighter wet cobbles.
- v3: measured cause of the remaining darkness: mode-3 halftone darkens ~90 % of each cell to 55 % in deep shadows, pushing
  every navy into Ink. Simulated the shader per swatch and set gamma 1.3 (navy 20,26,38 → 18,23,32 after halftone; slate exact).
  Ink fell to 56 % (S1) / 54 % (S3). Removed S2 background slabs; dimmed strips lightened (0.38/0.42).
- v4: hood inner boundary was exposed under the jaw and caught the key (amber sliver) → routed under the flap, neck filled.
  Border draw-on was invisible (black ink over a black interior) → the interior is bare paper until it develops, so the stroke
  visibly inks onto the page. Impact frame had all splash droplets at t=0 (a dark blot) → crown splash on f168, droplets sampled
  mid-shutter, rings from f169. Captions pop over 2 frames instead of fading.
- v5: hood front reshaped (no cap-visor beak, lower crown); cloak front falls from the chin with a lit edge; dart widened, closed
  lid shown as a faint slate line; thumb acting given anticipation + hesitation (R-5-01); splash crown randomised.
- v6: f0 showed paper inside the panel (fade ignored the develop overlay) → whole-frame rise from black; teal catch-light on
  the drape fold; envelope shadow falloff + 8 % dimmer paper + push trimmed to ×1.12 (Bone ≤15 % except the last push frames).
- v7: brief audit — "the seal is the only colour" was violated by the amber in the dimmed S2 strip next to it → the strip is
  desaturated in S3 (verified: only seal pixels are saturated). Grade tints zeroed (they were a tiny teal–orange split-tone,
  forbidden by §10). S2 strip dim 0.30, background lifted (Ink 66 → 63 %). Plain ink patch hides the last under-jaw sliver.

## Still weak / next with more time
- S2 hood is one large flat ink mass with rim/folds only; a second, softer teal bounce plane on the far shoulder and a slightly
  closer framing would give the glance more weight on a phone (glints are ~4 px at 720p).
- The key bands on her face are static shapes while the lantern swings; driving the band offsets with the lantern angle and
  flame flicker would make the light breathe with the practical.
- S1 rooftops are procedural blocks with repetitive window grids; hand-drawn landmark silhouettes and wet-roof glints would
  sell the city more.
- The thumb doesn't deform the paper; a pressure crease/bend under the thumb would make the grip physical.
- S2 sits at 63 % Ink (band 45–60 %) because the subject is a black cowl; S4/S5 are ink-heavy by design.

## Render
1280x720 (2-vCPU shared box, SwiftShader): ≈1.3–2.5 s/frame steady at load ≈1.8 (S5 card fastest, S1/S2 heaviest), 3.1 s/frame
for an 8-frame render.cjs run of S2 at load 2.4–4.3; first frame of a session +3–6 s for shader warm-up. 640x360 full pass: 0.54
s/frame. Particles: rain ≤1016 streaks/frame (S1). `node harness/render.cjs proto/p02-ink-ember --start 0 --end 1`: clean, no page
errors, frame 0 black. Low-res preview with sound: out/p02-ink-ember/lowres/p02-ink-ember.mp4.
