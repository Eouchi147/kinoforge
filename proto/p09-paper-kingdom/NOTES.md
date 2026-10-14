# P09 — PAPER KINGDOM (10 s, 16:9 1280x720, 24 fps, 240 f)

**Lane:** characters / fable (all-ages, artisanal) — cut-paper shadow theatre.
**Logline (25 words):** A paper king sends his army against a paper dragon, until a child's hands fold the dragon into a bird that flies into the light.
**Proves:** a pure Canvas-2D multiplane cut-paper theatre through `boot()` + overlay + ONE finish grade; jointed puppets (shoulder
pivot, a 5-link hinged chain + head + hinged jaw, two-part wings with overlap/lag, two-joint fingers); on-2s character animation
with anticipation, holds and settles; a shape-swap transformation (dragon → half-folded → half-folded → bird) on 2s with 6-frame
holds; a physically consistent lightbox: ONE lamp up-right behind the screen → hotspot up-right, translucent scenery multiplies the
light, every layer's drop shadow falls down-left, every opaque cut edge facing the lamp carries a thin fibrous rim, cut-out holes
(eyes, shield bosses, ermine spots, castle windows) glow.
**Files:** `scene.js` (timing, cameras, animation, compositing), `paper.js` (path parser, fixed hand-cut/torn edges, textures,
lit-edge rims, layer compositor), `puppets.js` (king, soldier, dragon rig, fire, hands, bird, fold stages), `stage.js` (scenery),
`audio.py`. Multiplane camera: card depth d, camera k (zoom), cx/cy (truck), cz (dolly), tx/ty (tilt): m = k·d/(d−cz).
Depths: screen 2.2, far ridge 1.9, lair mountains 1.65, castle 1.4, dragon 1.15, army 1.0, king/rock/hillock 0.9, grass 0.75.

## Final shot list (= scene.js; integer frames — every cut and audio cue shares exact times)

| ID | frames | dur | size / lens | move + motivation | light (source) | action (on 2s) | sound | emotion |
|----|--------|-----|-------------|-------------------|----------------|----------------|-------|---------|
| S1 | 0–71 | 72 f / 3.000 s | WS, 35 mm-eq. (k=1.0): castle cut by the left edge, king on his rock front-left, army mid, hotspot upper-right third | **locked-off** (the proscenium presents the kingdom; authority) | lamp behind the screen, up-right: cream → amber → deep orange → brown; scenery multiplies it; shadows down-left | king: dip back f6–12 (anticipation), raise f12–20 with overshoot, settle f20–28, slow breath; army: crouch f14–18, steps off on beat 1 (0.778 s), 4 steps, two-pose cycle (contact/passing) + bob, ripple phase 0/2/4 f | rustles f6 / f12 / f14; toy march 108 bpm (wood tick every beat, low drum on 1 & 3, step rustles); the 5th beat (drum) lands ON the S2 cut | pride → anticipation |
| S2 | 72–143 | 72 f / 3.000 s | EWS low angle, 28 mm-eq. (k=0.8; camera 300 px right, 70 px lower, tilted up 150 px: horizon drops, sky opens) | **slow dolly-in 2 %/s** on 1s (army plane +5.5 %; near cards grow faster = real parallax) — the dragon's threat growing | the dragon eclipses the lamp: screen −12 % f76–108; fire glow (additive) + lamp +12 % flare at f120 | march halts; head breaks the hillock ~f90 (vertical surfacing), neck arches over the army by f108; spears level f86–104 (staggered, outBack), tremble on 2s, harder after the fire; wings unfold f96–122 (outer +4 f, far wing +3 f, overshoot, settle); head rears back f108–118, snaps forward + jaw opens ON f120 = FIRE (12 tissue tongues, additive α 0.6), recedes by f138 | the march stops dead ON the cut; quiet low riser 3.000 → ends ON the S3 cut; low drone; rumbling paper flutter f86; spear / wing / rear rustles; FIRE whoosh + crackle f120; tremble rustle | awe → fear |
| S3 | 144–201 | 58 f / 2.417 s | CU, 85 mm-eq.: the dragon puppet as a paper object (1.7× stage size), background defocused (far ridge blur 7 px, washi magnified 1.7×) | **locked-off** (the hands do the moving; intimacy) | same lamp, hotspot behind the dragon's head (silhouette on the brightest paper); the cream back of the paper = the accent | dragon alone f144; hands rise from the bottom corners f144–155 (outCubic); fingers close f156–160; fold 1: press f162–163 → flip sliver f164–165 → **crease f166** (wings show cream backs, jaw shuts) held 6 f; fold 2: press f172 → flip f174 → **crease f176** (dark-bodied half bird, cream neck & wings) held 6 f; fold 3: press f182 → half-flipped f184 → **crease f186** = cream bird; hands open f192–196 | sleeve rustle ON the cut, grasp rustle, presses, **SNAPS f166 / f176 / f186** (−10 dB); **12 f silence f190–201** (−97 dBFS) | surprise → wonder |
| S4 | 202–239 | 38 f / 1.583 s | WS, 40 mm-eq. (k=0.84, camera right, horizon lowered: big sky for the bird) | **locked-off tableau**; army and king still from f216 (24 f), only the bird glides | lamp +20 % f202–226 as the bird reaches it | bird lifts ON the cut, flaps up into the hotspot (12-f cycle up/mid/down/down/mid/up) f202–224, then glides; spears lower f203–215 (1-f ripple, inOutCubic); king's arm falls f203–211, bounce, settled f216 | soft gong + wooden flute G4 B4 D5 G5 ON the cut, warm pad, lamp hum swells, wing flutters on the downstrokes f206 / f218, spear & arm rustles | relief → joy |

Sum 72+72+58+38 = 240 f = 10.000 s (brief timings; S4 starts at f202 = round(8.4 × 24)). Moves: one dolly (S2) = 25 %, locked-off 75 %.
Shot-length CV 0.23 (S1/S2 equal by brief; no 3+ equal run). Holds: S4 tableau 38 f locked, 24 f still; S3 bird held f186–201.
Screen direction: army L→R (progress), dragon faces R→L (opposition); the bird faces right — the fold reverses the dragon's facing.
Eye-trace: S1 end on the marching line (centre) → S2 army centre-left, dragon head on the hotspot ≈(690,330) → S3 opens on the
head ≈(380,270) (310 px, < 1/3 frame) → S3 ends on the bird at centre ≈(640,344) → S4 bird lifts from ≈(700,500).
Size steps at every cut: WS → EWS low → CU → WS (R-2-06).

## Colour script & grade (measured on the final frames, after the grade)
S1 amber (sky hue 28°, sat 0.53, mean L 0.30) → S2 darker and redder as the dragon eclipses the lamp (hue 23.5°, sat 0.65, mean L
0.24 at f142), the only yellow is the fire burst (p95 L 0.81 at f124) → S3 intimate, brightest mid-tones (mean L 0.40, cream paper
accent) → S4 the release: brightest highlights (p95 L 0.84), cream bird in the 20 %-brighter hotspot. Accent = cream paper,
reserved for the revealed back of the dragon's paper and the bird.
Grade: kit `sepia` tuned warm — saturation 0.5, grain 0.04, vignette 0.35, contrast 1.06, halation 0.2 above 0.8 only,
shadowTint [0.035, 0.006, −0.03], highlightTint [0.09, 0.04, −0.04]. The lamp gradient is drawn pre-saturated so it survives
saturation 0.5. Overlay colours are true (kit overlay is NoColorSpace).

## Sound (audio.py prints the cue sheet; verified with soundfile + numpy)
Duration 10.000000 s (480000 samples, 48 kHz, 24-bit stereo); peak −1.15 dBFS; RMS −19.5 dBFS. Snaps peak −1.4…−1.8 dBFS (the
loudest events); gong onset on f202 (first sample > −40 dBFS at 8.437 s, cut 8.417 s). Silence f190–201: peak −97.4 dBFS, 90 dB
under the gong. Riser and drone end exactly at 6.000 (S3 cut); the last march drum at 3.000 (S2 cut); FIRE whoosh at f120 with
the first fire drawing. Every rustle/tick/drum is generated fresh (no loop repeats); room tone (lamp hum + air) under S1–S3.

## Motion check (R-5-01) — 640x360 bursts (out/p09-paper-kingdom/burst_*) + one 640x360 full pass (out/…/lowres, with audio)
- `burst_march.jpg` (f12–23): king's raise passes horizontal at f16, overshoots f20–21, settles f22–23; soldiers crouch f18–19
  then stride. `burst_march2.jpg` (f30–41, zoom): contact/passing alternation with the 0/2/4-frame ripple, each drawing held 2 f.
- `burst_fold.jpg` (f160–171): grasp hold f160–161, 2-frame press f162–163, 2-frame flip sliver f164–165, crease f166 held 6 f.
- `folds_v1.jpg`, `cuts_v1.jpg`: every fold in-between and the frames either side of each cut.
- Full-pass frame-difference scan (160x90): held drawing pairs median 0.7 (grain only) in every shot → no boiling (edges are
  cut once, textures live in each piece's own space); new drawings land on even frames; the only spikes are the cuts (32–59),
  the fire burst (f119→120: 11.2) and the fold snaps (f163→164: 15.3, f175→176: 14.0). S4 army/king band is still from f216.

## QC log
- v1 (first frame): **31 s/frame** — the kit overlay canvas is GPU-accelerated; on SwiftShader the clip/blur/pattern work runs at
  flush. All drawing moved to CPU-raster canvases (`willReadFrequently`), one copy into the overlay per frame, rim clips bounded to
  each piece's bbox → 2–3 s/frame at load 8. Look: king an egg-shaped blob against the dark castle (no separation); screen fibres
  read as hairs; beige sky (the grade halves saturation); S2 tilt exposed the paper texture's top edge; wing ran out of frame;
  CU hands were mittens on thick slabs; cream folded wings read as a pile of strips.
- v2: king rebuilt (cape, robe with belt slit + hem diamonds, ermine collar with cut-out spots, long pointed beard, 4-point crown,
  scepter) and moved onto a rock right of the castle so crown and raised arm silhouette against the sky; castle shifted left;
  washi texture rebuilt (two scales of cloudy density, fibres α 0.025–0.075); lamp gradient tighter and pre-saturated; texture
  extended for S2's tilt.
- v3: wing membranes opaque (α 0.97), far wing smaller, lighter umber, peeking left; folded wings as flat cream membranes; fire
  rebuilt as pointed tissue tongues aimed down at the army; tree behind the lead soldier removed; S4 reframed wider with a low
  horizon; CU background = lighter defocused far ridge.
- v4: fire shortened to end over the army (not on the king); CU hotspot moved behind the dragon's head.
- v5: the rise read as a slither at ground level → vertical surfacing coil (head first, neck arches over), wings unfold only after
  the shoulders clear the hillock; CU hands raised so fingertips overlap the paper (grip contact); ground strip lightened so the
  soldiers' legs read.
- v6: neck-fold in-between swung the neck up like a stalk → foreshortened cream flap on its hinge; fire was first visible 2 frames
  after the whoosh → bursts ON f120; cut-paper fern and daisy break up the hillock; S4 settle tightened (24 f still tableau).

## Still weak / next with more time
- The fold D1 → D2 is a magical swap (rig layout → bird layout); per-facet hinge foreshortening would make the paper logic literal.
- The king's face is a profile only (nose + beard) at 190 px; a larger eye hole/crown would read better on a phone.
- The spread far wing is a flat umber slab; a sheared second scallop set would separate it from the near wing.
- The hands are pure silhouettes; knuckle-crease rims and pad deformation at the pinch would sell the grip.
- The bottom fifth of the wides is dark (ground strip + rock + hillock); a lighter mid-ground strip would open it up.
- Shot-length CV 0.23 because S1 = S2 = 72 f by the brief; 68/76 would reach the house CV ≥ 0.4 target.

## Render
1280x720 single frames: 1.7–2.6 s/frame on the shared 2-vCPU box at load 4–8 (scene 2D ≈ 0.45 s + finish ≈ 0.18 s; the rest is
readback/PNG; heaviest = S2 fire f124 at 2.5 s/frame, load 7.9). 640x360 full pass 0.58 s/frame (3.2 min). No particles (≤12 fire
tongues), no bokeh. `node harness/render.cjs proto/p09-paper-kingdom --start 0 --end 1`: clean, no page errors.
Preview with sound: out/p09-paper-kingdom/lowres/p09-paper-kingdom.mp4. Per-layer timing: add `--param prof=1`.

## Kit notes (not edited; please consider)
1. Perf trap: `makeComposer`'s overlay is a GPU 2D canvas; on SwiftShader clip/blur-heavy 2D work costs ~30 s/frame. Drawing into
   `getContext('2d', { willReadFrequently: true })` (CPU raster) and copying once into the overlay gives ~10x. An `overlay: { cpu: true }`
   option would make this the default for 2D scenes.
2. `sfx.Mix.duck` ramps back up *after* `end`, so a hit placed at `end` before calling `duck()` loses its attack; place post-silence
   cues after the `duck()` call (done here).
3. `sfx.Mix.write`'s limiter is a whole-signal tanh waveshaper once any sample exceeds −1 dBFS (−0.9 dB and soft-clip on everything).
