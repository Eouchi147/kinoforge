# P03 — THE LANTERN ROAD (12 s, 16:9, 1280x720, 24 fps)

**Lane:** dark history / living-painting documentary (narrated 2.5D painted history).
**Logline (22 w):** At dusk a lone traveler climbs a mountain road; lanterns light one by one as he passes, until the village gate's great lantern answers him.
**Proves:** a fully procedural 2.5D painted multiplane — brush-stroke canvases placed at true depths so a dolly and a crane produce
correct parallax; practical lanterns that *relight the paint* (cause → effect); a warm/cool colour script carried by light,
not by grade; a fine-brush detail layer so a 1/40-frame figure survives the Kuwahara painterly pass with a planted walk cycle.
**Emotion arc (Plutchik):** anticipation (interest) → surprise → awe → trust/serenity at the gate.
**Files:** `scene.js` (boot, timeline, camera, per-frame figure/detail drawing, captions) · `sets.js` (the three painted setups) ·
`paint.js` (brush engine) · `walker.js` (gait + figure painter) · `lib.js` (multiplane placement, relight material, glows, detail pass) ·
`timing.json` (single source of truth for picture *and* sound) · `audio.py`.

## Shot list (final = code; frame ranges at 24 fps)

| ID | time / frames | size · lens | move + motivation | light (all motivated) | sound |
|----|---------------|-------------|-------------------|-----------------------|-------|
| S1 | 0.00–4.60 s · f0–110 (111 f) | EWS, 32 mm, eye level across a gorge; traveler 18 px ≈ 1/40 H | lateral dolly L→R, eases in from rest over 2.4 s then tracks at 1.25× his pace — *following his motion*, lead room ahead (R-2-07). 10 planes, D = 12 m … 6 km; foreground boulders slide 324 px, road 41 px, peaks 2 px | key: dusk sky (cool, afterglow low at the left); practicals: his hand lantern + a rope line of 3 paper lanterns that ignite as he passes beneath them (1.0 / 2.5 / 4.0 s) | wind bed + high gust whistle, D2 drone fades in, gravel steps on every drawn plant (+ staff tap), motif D4 0.5 s, distant bell 1.8 s, chime A5/C6/D6 per ignition, motif F4 3.2 s |
| S2 | 4.60–8.80 s · f111–211 (101 f) | low-angle EWS, 26 mm; traveler 14 px | crane up 17 m + tilt 0→12°, ease in/out 4.6→8.2 s then holds 0.6 s — *reveal/scale* (R-8-06); the eye follows the chain of lights climbing the terraces; boulders fall away, terraces separate by parallax, peaks enter from the top, fog halves drift apart | cool dusk; practicals: lantern chain ignites upward every ~0.4 s from the post he passes (5.40 s) to the summit shrine (8.45 s); windows follow their lantern; fog wisps relit warm by nearby lanterns; gate lantern stays dark (set-up for S3) | motif A4 on the cut, A2 fifth joins the drone, choir swell D3-A3-D4, 9 ascending pentatonic chimes (D5→A6) panned by screen x, distant steps |
| S3 | 8.80–12.00 s · f212–287 (76 f) | MWS, 35 mm, low camera; traveler ≈ 265 px | locked-off — arrival/authority. Walks in (cut on action) → brakes from 8.80 s, short braking step 9.025 s with lean-back (anticipation) → quick closing step plants 9.40 s, body at rest 9.46 s → sink-and-settle, cloak/lantern follow-through → hood lifts to the lantern 9.85–10.12 s → holds (breathing) | cool dusk + his lantern + village windows/stair lanterns; **f245 (10.21 s) the gate's great lantern ignites**: warm key from upper right, warm pool on ground/posts, warm rim on hood/cloak/staff, long soft shadow thrown down-left | motif G4 on the cut, village bell 9.0 s, braking + closing steps (9.083 / 9.417), **silence 9.62–10.20 s (f230–244, 15 f, 50 dB under the hit)**, gentle low hit + D5/A5 chime on f245, flame bed, warm pad, motif C5 at the title (10.625 s), D4 resolve 11.25 s |

Title "THE LANTERN ROAD" (Cinzel 500, bone, bottom-left over the dark foreground rock) fades in at 10.625 s and holds to the end.
Captions (Cormorant Garamond italic, lower third y=616): "He had walked for eleven days." 0.55–4.25 s; "The village had been waiting." 5.25–8.45 s.
Hold on the key image: S3 settled from 9.46 s and still from 9.85 s to 12.0 s = 52 f (≥ 36 f). Shot lengths 111 / 101 / 76 f (all different).
Cuts: S1→S2 keeps the traveler near the same screen position (eye-trace, R-3-03) and continues the gait phase — a plant lands
on the cut (cut on action); S2→S3 is a size jump (EWS → MWS) and an ellipsis in space, same screen direction (L→R, R-2-05).
Head: 6-frame soft open from black (frame 0 is black by design); the first ignition at 1.0 s is the hook (R-1-01).

## Look
- **Planes:** sky (gradient + painted cloud bands), far peaks (ridged-noise crests, snow in diagonal gullies), mid mountains,
  distant village spur, valley fog bands (fbm-alpha, drifting with the wind toward −x), pine ridges (fbm-broken silhouettes),
  the road on a ridge crest, near brush, out-of-focus foreground boulders. Each plane is a canvas painted with thousands of
  tapered brush dabs (blunt start, tapered tail) over a smooth underpainting; colour comes from a value/temperature field with
  jitter, direction from a flow field (horizontal sky, along the crest then diagonally down each facet, along the road), plus
  coarse paper mottling. Planes sit at depth D and are scaled by D/f so they paint at screen density; coverage is computed from
  the camera path. S1/S2/S3 are three setups (as in a real multiplane production), sharing one painting vocabulary.
- **Relighting:** plane shader = paint × ambient + (paint luminance toward the light's hue) × Σ lantern lights with soft falloff —
  a lantern that catches warms the wall/road/fog around it; glow sprites (additive, HDR) feed bloom (thr 0.8, str 0.5, radius 0.42)
  and the kit's highlight-only halation.
- **Grade (one):** kit `painterly` (Kuwahara mode 4, radius 4), saturation 1.1, contrast 1.04, shadowTint [−0.008, 0, 0.035] (blue),
  highlightTint [0.05, 0.022, −0.02] (amber), halation 0.25, grain 0.035, vignette 0.35. No letterbox. Tone mapping off so the painted
  values are exactly what renders.
- **Fine-brush detail layer:** traveler + rope line (S1), traveler + road posts + gate (S2) are drawn per frame in screen space and
  composited after the finish pass with the *same* grade, vignette and grain formula (uniforms copied each frame) and a radius-1
  Kuwahara. A static canvas weave (3%) is applied there too. In S3 the figure is large enough to go through the kit Kuwahara.
- **Type:** Cormorant Garamond italic narration captions; Cinzel title. Drawn after the finish pass (crisp, never Kuwahara'd).

## Colour script (measured: warm = r>b+4%, r≥g, sat>0.22, value>0.18)
S1 f100: cool blue-violet, warm **0.2%** (his lantern + 3 rope lanterns) → S2 f205: warm **4.1%** as the chain climbs the village and
the mist around the terraces warms → S3 f270: warm **6.7%** — the great lantern, gate posts, ground pool, his rim; sky stays cool.
Mean luma ~15–16% in all three (blue-hour key held constant; only the warm share changes).

## The traveler
Hooded cloak, staff in the far hand, hand lantern in the near hand. Walk on 2s (pose sampled every 2 frames; camera/light on 1s),
step 0.30 H, 0.55 s/step, plants at 0.225 + k·0.55 s. Feet are world-space plants: heel-strike rotates about the heel, heel-off
about the toe, so the contact point never moves (R-5-07); the staff tip plants with every far-foot step. Bob lowest at contact.
Lantern = damped pendulum driven by the hand's acceleration; cloak hem = damped spring (lags, settles). Wind from the right: hood
tip and hem trail back. Measured planted-contact drift vs the ground: S1 ≤ 0.02 px at 1280 (through the moving dolly), S3 0.00 px.

## Sound (audio.py prints the cue sheet; all times read from timing.json)
Mountain wind (gusty) + high gust whistle; D2 drone (73.4 Hz, sine, lp 700), A2 fifth from S2; plucked D-minor-pentatonic motif
(D4 F4 A4 G4 C5 D4 — two on the cuts); distant bell (low pluck, long reverb) 1.8 s and 9.0 s; gravel steps on every drawn plant
(−27 dB S1, −31 dB S2 distant, −22/−23 dB S3 close) + staff taps; soft sine chime per ignition (−24/−25 dB, ascending in S2);
choir swell across S2; silence 9.62–10.20 s; gentle low hit (−16 dB) + D5/A5 chime on f245; flame bed + warm pad under the title.
Verified: 12.000 s (576 000 samples @ 48 kHz, stereo), peak −1.46 dBFS, 15 frames ≥ 20 dB (actually 50 dB) under the hit.

## QC log
- **v1** (f66/f190/f262) — BUG: traveler drawn as a 170-px pole: hip height was absolute while feet followed `ground(x)` (≈ −9 H in S1) → body now rides on `ground(bx)`. Peaks read as glowing white "table mountains" with vertical slats (per-column gradient underpainting + vertical gully strokes, amplified by Kuwahara). Road too pale (reads as snow/river). S2 houses in barracks rows, walls too pale. S3 great lantern a blown white sun; warm rim turned the thin staff into an orange neon line; figure grey (no separation). Layer-cake composition in S1.
- **v2** — smooth per-pixel underpainting (coarse colour grid upscaled) replaces column gradients; ridged-noise crests; facet-following diagonal strokes; dusk values corrected so peaks sit *below* the horizon glow in value (were above). S1 recomposed on a diagonal: massif upper-left stepping down to the village spur (right), lead room toward it. Gable/eave house variants, irregular clusters on cone-shaped terraces. Staff excluded from the rim pass.
- **v3** — slats persisted. Root cause found by elimination: the value gradient and the crest-slope lighting were keyed to `ridge(x)`/`slope(x)`, so every crest notch printed a full-height column. Fix: gradient keyed to a 130-px box-filtered ridge; slope lighting fades out 70 px below the crest. Fog invisible in S2: strokes were stratified over the whole (huge) plane, ~5% landed in the band → now sampled inside the band's bounding box.
- **v4** — measured pixels instead of guessing: S2 walls were actually dark (≈40–50); they *read* pale because gable-front houses were identical pentagons with no roof mass and window pairs looked like faces → deeper rake overhang, single larger windows. S2 out-of-focus grass blurred into a row of blobs that read as a crowd of figures → boulders + a few tufts. S1 bough read as a cloud smear → removed.
- **v5** — S3 measured: cloak (28,27,54) vs mist behind (46,45,85) — under 1 stop, no silhouette → brighter, thicker mist behind him, darker cloak (now ≈3 stops). Lantern paper clipped to 255 even without bloom: the sprite's core was the size of the lantern body → halo-only sprite; the ribbed paper is now the source. Relight model: lit share of the paint takes the light's hue (painted light), so warm pools read on cool paint. Rope line raised: lanterns hang above his head.
- **v6** — S1 foreground sat in the vignetted shadow and vanished → boulders tall enough to silhouette against the lit upper slope (one exits left, one enters right during the dolly). Long shadow missing: Canvas2D `filter` + `setTransform` on one draw dropped it → shear into a scratch canvas, blacken, then blur. Standing leg bent 27° (thigh+shin > hip height) → 0.236 + 0.236. S2 payoff too small → lanterns relight the fog wisps; soft scatter over each terrace ramps with its lanterns (first pass read as a lightbulb → cut to a faint mist).
- **v7** — boulder highlights painted as long dabs read as claw marks → soft top-edge gradient + short low-contrast dabs. Performance: S3 spent ~2 s/frame in full-frame Canvas2D blurs + a full-frame texture upload → figure card and scratch canvases cut to the 520×450 region he occupies, CPU-raster contexts; fast sRGB decode; no anisotropic filtering; detail-pass early-out. 4.7 → 2.8 s/frame (S3) under shared load.
- **v8** — motion burst (640x360, f0–29 and f212–287) + numeric foot log: planted contacts drift ≤ 0.02 px (S1, road-relative) and 0.00 px (S3); dolly step per frame rises smoothly from 0 (ease-in from rest). Closing footstep (9.583 s) fell inside the duck ramp of the silence → stop retimed to a quicker, shorter closing shuffle (plant 9.40 s, body at rest 9.46 s), silence 9.62–10.20 s; stance re-solved so the hip ends over both feet (feet mean −0.001 H). Look-up made legible (hood tilt 0.62 rad); far leg darkened.
- **v9** — REGRESSION caught on the arrival sheet: a scripted edit put a `//` comment in front of `c3.push(...)`, deleting the braking/closing plants (feet froze at the 7.9/8.5 s plants → a leg stretched 0.5 H behind him). Fixed and audited every inline comment. Orphan warm disc in S2: "halo-only" sprites still had a 13-px core (exp(0)=1 at the centre) → core term disabled when `uCore ≥ 3000`. Head fade shortened to 6 frames.

## Verification (final)
- `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node harness/render.cjs proto/p03-lantern-road --start 0 --end 1` → exit 0, no page errors,
  ready 21 s (one-time: painting ~0.5 M dabs into 51 Mpx of canvases + texture upload, now done in init), **3.2–3.5 s/frame** at 1280x720
  on the shared 2-vCPU box (load ≈ 1–2); steady-state frames measured 2.8–3.6 s across all shots. Deterministic (seeded rng, time-driven).
- Keyframes: `out/p03-lantern-road/keyframes.jpg` (S1 f100, S2 f205, S3 f270).

## Still weak / next
- S2's terraces still read as stylised contour bands with rows of houses; more irregular massing (stepped retaining walls, trees
  breaking the rows, a visible zig-zag stair) would make the village feel built rather than placed.
- The S1 traveler is legible but tiny (by brief); at 1/40 H his gait reads mostly as bob + lantern sway at viewing size.
- S3's left half (where he came from) is intentionally dark negative space but is a little flat; a faint second ridge or road
  continuing into the mist would give it depth without stealing focus.
