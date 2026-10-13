# P06 — CEL (10 s, 16:9, 24 fps, 240 frames)

**Lane:** epic cinematic, anime-style cel shading.
**Logline (21 words):** During a storm, a lighthouse keeper's daughter climbs the tower to relight the dead lamp; the beam cuts the dark.
**Proves:** 3D that reads as deliberate 2D: 4-step toon ramp with a *designed shadow colour per material* (hue-shifted
shadows), constant-pixel-width inverted-hull ink, cool rim separation; a primitive-built character animated on 2s with
IK-planted feet (measured slide 0.0 m), anticipation, overlap (3-frame-lagged cape on a spring); FX on 1s (rain) and
2-frame lightning; one motivated light change (dead lamp → lit) that flips the palette; sound locked to picture.
**Emotion arc (Plutchik):** apprehension (S1) → anticipation/determination (S2) → anticipation → surprise/joy (S3) → joy/awe (S4).
**Opening vs final image (R-1-06):** S1 low angle, the dead lantern silhouetted in the moon's halo; S4 low angle from the
sea, the same tower lit from within, two beams cutting the storm. Change in ≤10 words: the dark tower gives light again.

## Shot list (final = code)

| ID | frames / dur | size, lens, angle | move + motivation | light (named sources) | sound |
|----|--------------|-------------------|-------------------|-----------------------|-------|
| S1 | f0–71 / 3.0 s (72 f) | WS, 20 mm, low from the waterline 20.5 m out | locked-off: authority/dread (R-2-04) | moon behind the tower = cool rim + halo behind the dead lantern; lightning f21–22 & f55–56 (DirectionalLight spike + sky flash + bolt, 2 frames each); practical: keeper's cottage window (warm) | storm wind/rain/surf; THUNDER hit+rumble at 0.9 s and 2.3 s; wave crashes f30, f58 |
| S2 | f72–139 / 2.83 s (68 f) | MS (full figure), 30 mm, high 3/4-front from over the treads ahead of her | crane up + pan around the helix, leading her (following motion, R-2-03): holds through her look-up/crouch, reacts one drawing after the launch, eases into her pace | moonlight through a slit window behind camera = hard cool bar (she runs through it f100–116, her shadow on the wall); slit windows are the practicals; depth fog drops the well into dark | storm muffled by stone, slit moan; iron footsteps on every contact (f92…f132); breath |
| S3 | f140–191 / 2.17 s (52 f) | CU two-shot (face + hands + lamp), 55 mm, eye level from behind-beside the lamp | locked-off (the action is the hands); 2-drawing impact nudge on the clunk | before: cool moon rim through the lantern glazing; from f168: PointLight in the lamp, warm, below her face; burner sphere + banded Fresnel-lens emissive, bloom 0.9 / thr 0.6 | creak f144, effort f150, CLUNK f154, −30 dB for 12 f (f156–167), IGNITION f168, hum 110 Hz + riser into the cut, choir enters |
| S4 | f192–239 / 2.0 s (48 f) | WS, 30 mm, low from the sea | locked-off on a gentle swell (camera floats: ±0.12 m bob, 0.5° roll) | lamp PointLight (range 4.5 m) + two beams (kit lightShaft, length 60) rotating 70°/s, the near beam passes over the lens at f206 (glare sprite + exposure lift); moon rim | whoosh 1.2 s peaking at f206; choir peak; storm continues; no title |

Shot lengths 72 / 68 / 52 / 48 f (no equal run). Holds ≥24 f: her lit face f168–191 (24 f, eyes open), the lit tower f208–239 (32 f).
Cuts land on frames 72, 140, 192 (S2→S3 is f140 = 5.833 s; 5.8 s is not a frame boundary).

**Character timing (on 2s via `ease.hold2s`):** S2: look up f72–77 → crouch/anticipation f78–83 (decision blink f78–81) →
launch f84 → 7 steps × 8 f (4 drawings/step: contact–down(dip)–push–passing); squash on each contact, head bob, counter-arm
swing, shoulder twist; contacts f92 f100 f108 f116 f124 f132. Feet: planted feet are placed by 2-bone IK on the step and never
move; heel-raise pivots on a fixed toe; the pelvis is lowered if a planted leg would over-reach (never the foot).
S3: hold f140–143 → wind-up 6 f (f144–149, coil back/down, brows furrow) → push 4 f (f150–153) → CLUNK f154 (squeeze blink) →
follow-through 10 f (f154–163) → held breath → IGNITION f168 (eyes widen, brows up, mouth opens) → 24 f hold.
Cape: thick slab, chest-local, driven by a pre-integrated spring of the body's acceleration + drag, sampled 3 frames late (R-5-04).

## Colour script
S1 indigo night, painted cloud banks with silver moon rims, the dead lantern black against the moon halo; one warm window.
S2 blue-violet interior; cool moonlight slab; the girl's yellow oilskin (shadow: burnt orange) is the only warm thing.
S3 dark blue lantern room → f168 ignition flips it: warm gold key from the lamp, violet/mauve designed shadows.
S4 the storm stays blue; the lantern glows gold; two warm-white beams cut the rain.
Accent rule (R-4-06): warm amber belongs to the girl and the lamp (plus the cottage window as the single "home" practical).

## Grade & look
`cel` preset + shadowTint [0.0, 0.02, 0.08], grain 0.03 (all shots), vignette 0.2, halation 0, no letterbox; Neutral tone
mapping (keeps flat hues); bloom strength 0.9 / radius 0.35 / threshold 0.6 — only emissives cross it (lightning, burner,
lens bands, beams, moon).
- **Toon:** MeshToonMaterial + `toonGradient(4)` on every lit surface. Each material carries `[lit albedo, designed shadow]`;
  an onBeforeCompile patch makes the ambient light the shadow colour and direct light add (albedo − shadow) through the ramp.
  This is what makes the yellow cape go burnt orange (not olive), skin go mauve, white go lavender.
- **Ink:** inverted hull (BackSide, MeshBasicMaterial near-black, fogged) with the vertices pushed along welded normals in
  view space by a width proportional to depth = constant ~2.3 px at 720p (scales with resolution). A uniform 1.03 scale was
  rejected: line weight would follow object size (9 cm on the tower, invisible on fingers) and offset meshes not centred on
  their origin. No z-fighting: the hull sits behind the surface except at silhouettes.
- **Sea:** polar grid centred under each camera, 5 Gerstner waves (sines), toon-shaded; foam = emissive bands where the crest
  exceeds a height + a thinner line below + rings around the rocks; small moon glints.
- **Rain:** 4000 instanced streak quads (≤ 4000), world-anchored, on 1s, culled inside the tower wall, lit gold inside the beam
  cones; in S2 concentrated just outside the two slits behind her so it reads through the openings.

## Sound (audio.py, cue sheet printed on run)
Exterior beds (S1, S4): wind 0.8 gusty, rain 0.8, sea surge, L-cut tails into S2. Interior (S2, S3): storm low-passed, slit
moan, tower resonance, rain on the lantern glass. Thunder = hit(sub 45, crunch 0.8) + low rumble at exactly 0.9 / 2.3 s
(picture flashes f21 / f55 contain those instants). Footsteps: square 1200 Hz pings low-passed + thud, stairwell reverb, on the
six contacts (9–16 dB over the bed in 0.8–4 kHz). Lever creak f144, CLUNK f154 (custom, gone in ~3 f). Whole mix ducked −30 dB
f156–167, then IGNITION f168 (whumpf + sub drop + shimmer), hum 110 Hz + riser ending on the S4 cut, choir A3 C#4 E4 from the
S3 cut rising to its peak in S4 (+ octave), beam whoosh 8.0–9.2 s peaking at f206.
Measured: 10.000 s / 480 000 samples, stereo 48 kHz, peak −4.6 dBFS; silence window RMS −53.5 dB vs ignition −14.9 dB (38.6 dB).

## QC log
- **v1** everything one saturated mid-blue, no value structure; a single coloured ambient cannot hue-shift per colour (yellow
  shadow went olive) → per-material designed shadow colours + neutral ambient. S1 tower small, clouds = floating pancakes,
  spray = cotton balls. S3 broken: lever out of reach after the push (arms straight, hands detached), lamp out of frame, glass
  glowing brown, lens edge a sawtooth. S4 beams too fat with visible cone ends; crest foam read as white puddles.
- **v2** palette pairs + toon patch landed; clouds rebuilt as lineless painted banks; foam thinned to lines; S3 restaged
  (lever 0.42 m from the lamp, grip within reach in every key, camera behind-beside the lamp → lens FG, hands MG, 3/4 face).
  Lightning whited out the frame and the bolt was hidden behind the clouds; tower shadow too saturated (read "blue tower");
  shadow acne dots on the grazing rim; S4 PointLight lit the whole tower body pink.
- **v3** moon moved so the dead lantern is silhouetted in its halo (the hook); bolts moved in front of the cloud banks, flash
  softened; tower shade lightened; normalBias 0.045; spray rebuilt as a velocity-stretched plume; lamp light range 4.5 m;
  beam end-fade patched into the kit shaft instance; glare alignment measured on the horizontal (beam passes over the lens).
  S2 camera "ahead across the well" put the next treads between camera and girl.
- **v4** cloud puffs culled by angle from the S1 camera so the moon stays clear; 20 mm with more headroom; the moon disc sat on
  the lantern and read as a lit lamp → moved 9° left / 4.5° up (the opposite of the hook would have been fatal).
- **v5–v6** S2 rethought: camera over the treads she is about to climb, above her, leading crane → her face, her feet on the
  treads and the spiral dropping away all read; interior values lifted (iron/plaster shadow colours, ambient); cape lift cut
  (it read as a flat disc from above). S3: stronger cool rim before ignition.
- **Motion check (R-5-01):** 12-frame bursts at 640×360 via render.cjs (out/p06-cel/burst): f78–89 (stand → crouch with decision
  blink → coil → launch; camera holds until she commits) and f146–157 (wind-up back → push → clunk, cape trails 3 f behind the
  lunge). Frame-diff within a drawing 1.5 vs 4.1 between drawings (on 2s confirmed). Numeric foot probe (`window.KF_P06.feet`):
  planted toe contact moves **0.0 m** over all of S2 (heel-raise pivots on the toe); no IK reach misses in S2/S3 (`?debug=1`).
- **v7–v8** wind-up exaggerated (coil −8 cm, lean 0.06); lens shrunk and made opaque dark glass, camera to 55 mm; lens emissive
  map = one glowing band per prism ring (reads as a Fresnel lens); ignition flare kept on the burner/lens, capped on her key
  light (her face had whited out on f168).
- **v9–v11** spray as teardrops trailing their velocity (splash crown); S2 depth fog, lower camera so the boots read on the
  treads, rain allowed into the window reveals and concentrated outside the two slits; S2 headroom at the cut-in; lever timing
  moved 2 f earlier so the 12-frame silence (f156–167) is clean of the clunk and the lit face still holds 24 f; a late blink
  removed so her eyes stay open through the 24-frame hold (R-8-02).
- **Full 640×360 pass** (out/p06-cel/preview): every in-shot frame-diff spike is a designed event (f21–23, f55–57 lightning;
  f168 ignition; f204–209 beam pass; f104 entering the moon bar); no flicker or pops.
- **Final:** `render.cjs proto/p06-cel --start 0 --end 1` clean (no page errors), 2.54 s cold at 1280×720; warm frames 1.0–2.5 s.

## Still weak / next
- S2 is nearly monochrome flat blue: the plaster wall needs painted value variation (stone courses, a darker skirting band),
  and the cape seen from above reads a little like a shell.
- The girl is honest primitives: capsule joints show at the elbows/knees; no fingers in S2; a hand-sculpted hair/face mesh and
  a shoulder/elbow cap would lift it most.
- Cloud banks are attractive but repetitive; two or three hand-placed hero shapes per shot would compose better.
- The S1 splash crown still reads a little like a sea anemone; a few flat sheet shapes at its base would sell water.

## Deviations from the brief (deliberate)
Near-silence is 12 f (brief says 10; R-3-06 requires ≥12). S3 is a CU two-shot (face, hands and lamp share the frame) because
the same 2.2 s shot must show the push, the lamp igniting and the light on her face. S2's crane leads her from above instead of
tilting up from below (from below the next turns of the helix hide her face). Ink is an inverted hull with constant pixel
width rather than a 1.03 scale (reason above).
