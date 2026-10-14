# P07 — ASH ASCENT (6 s, 16:9, 24 fps, Blender 5.2 Cycles CPU)

**Lane:** epic cinematic / awe (R-8-06). **Logline:** At dawn on a volcanic highland, a lone rider crosses a knife-edge ridge above a sea of cloud as the sun breaks a far volcano.
**Proves:** the KINOFORGE Blender contract end to end — Python-displaced procedural terrain, a volumetric cloud sea that stays inside the CI budget, a physical sky whose animated sun *motivates* the light change (crest → the cloud sea floods with light except the volcano's shadow wedge → rim light runs onto the ridge and the rider), a procedurally animated figure with planted hooves and a reacting beat, a compositor finish (halation on highlights / vignette / grain), and a hard cut to black synced to silence.
**Emotion arc (Plutchik):** anticipation (cold blue drift, horn swelling) → awe (= surprise + fear: the sun breaks, light finds the rider; he stops) → void (black, silent).

## Shot list (= code: `SHOTS`, `camera_pose`, `frame` in blender.py)

| ID | frames / dur | size / lens | move + motivation | light | sound |
|----|------|-------------|-------------------|-------|-------|
| S1 | 0–129 (130 f, 5.417 s) | EWS aerial, 50 mm, behind-right-above (3/4 rear of the rider) | aerial dolly forward + down: 330→205 m behind, 66→41 m right, 53→32 m above the rider (constant ≈8.5° depression), Hermite ease from 34 m/s to ≈3 m/s (a near-hold for the crest), roll 0→3° (smoothstep 0.4–5.2 s). Motivation: a bird's-eye drift that follows the rider and reveals scale as the cloud sea opens; it settles so the key image holds 39 f (91–129) | key = Sun lamp behind the far volcano, elev 2°→5° linear, az 0.37°, 18 W/m², 0.5°, (1, .64, .40). Before f91: blue skylight only, warm aureole behind the cone. f91: the limb breaks the cone's west flank (verified on renders: f90 no sun pixels, f91 first). From ~f94 light reaches the rider, full by ~f116; the volcano's shadow wedge keeps the cloud sea in front of it blue | wind at altitude ×2 (L/R), 30 Hz sub rumble, horn A2 (saw 110, lp 600, 2 s attack) swelling to the crest, 16 faint hoof thumps on the gait's plants (fade over the halt), C5-E5-G5 shimmer pad from f91 |
| BLACK | 130–143 (14 f, 0.583 s) | black | hard cut (no dissolve); world off, meshes/lights hidden, dither 0 → true RGB 0 | none | digital silence (14 f ≥ 12 f, R-3-06 style) |

Reacting beat (R-8-06 "then a reacting beat"; R-5-01 anticipation): the light reaches him ~3.9–4.8 s; at 4.30 s the horse checks its walk and squares up (halted 4.95 s), head up; the rider straightens, looks up and lifts his staff (a 0.15 s dip, then a 0.5 s rise + forward tilt) — the staff is the only element long enough to read at this scale. Hoof plants come from `hoof_local` (lateral-sequence walk, duty 0.62, stride 1.70 m, 1.55 m/s), hooves planted on the true terrain height (2-bone IK).
"Feet planting on 2s" was read as: plants land on a regular beat (4-beat walk, every plant scored); the animation runs on ones (realistic 3D, R-5-02).

## Geometry
- Units: metres, +Y toward the volcano. Ridge crest at z≈0 at the rider, descending gently past him (the spine tapers into the cloud ~1 km on); flanks ~47–50° with gullies/spurs, gendarmes (4–12 m) on/beside the crest for scale; a local jog in the crest turns his path ~28° so the camera sees a 3/4 rear view (39–40° off his axis).
- Terrain: sheared, variable-resolution grid following the crest (0.62 m along / 0.4 m across near the riding line, growing outward), 223k verts; 5 islands (96k); volcano = radial grid (58k), ~46° summit → ~34° at the cloud line, broken crater rim, radial gullies, west parasitic cone, top 1180 m, 11.8 km away.
- Cloud sea: closed shell mesh (96k verts; frustum-shaped heightfield: multi-scale Worley domes 150/58/22 m on a slow swell, Earth-curvature drop, billows flatten 5–12 km out) filled with a homogeneous Principled Volume (density 0.05, anisotropy 0.3, colour .93/.95/1, emission 0.008 sky-blue as a multiple-scattering stand-in); tops ≈176 m below the ridge (−216…−156). Beyond 13.6 km an opaque hazed deck carries it to 150 km; camera rays below the horizon see the horizon haze (the curved deck falls away under it, so the cloud horizon sits ~0.5° below the sky horizon).
- Scale: rider (2.4 m) ≈1/57 of frame height at f0 → ≈1/35 at f129 (13 → 20 px at 720p). Composition: horizon ≈0.56 from bottom, volcano summit on the right third (0.68, 0.80), sun just left of the summit, rider on the left third (0.36, 0.22), ridge diagonal from bottom-left.

## Colour script
- f0–90: deep blue world — ridge near-black, cloud sea blue-grey, volcano a slate silhouette with a hazed base; one warm point = the aureole behind the cone (warm horizon band at f0).
- f91: the limb breaks (white-gold, the only clipped pixels; halation on it only).
- f91–129: gold billow tops flood the left of the sea, the volcano's shadow wedge stays blue and points down toward the ridge; warm rim on the crest, the rider silhouetted against lit cloud.
- f130–143: black.

## Grade (one for the scene)
AgX view, `AgX - Medium High Contrast` (the brief's "Medium Contrast" look does not exist in 5.2), exposure −3.1 (the 5.2 sky is physically scaled). Compositor (`scene.compositing_node_group`): Bloom glare threshold 60 (scene-linear), clamp 250, strength 0.28 → only the sun blooms; vignette smoothstep to ×0.76 in the corners (≈0.4 stop); grain = multiplicative 4-D white noise ±4 % (σ≈2.3 %) on pixel coords, W = frame×1.618 → deterministic, identical on every lit frame; black frames stay RGB 0 (dither off).

## Deviations from the brief (all deliberate, with reasons)
1. **Camera distances ×≈2.8.** At 50 mm (VFOV 22.9°) the brief's path (120→60 m behind, 40→25 m up) puts the rider 18–23° below horizontal: rider and sunrise cannot share the frame, and he would be 1/21→1/11 of frame height (brief ~1/60, R-8-06 ≥1:20). Kept 50 mm, scaled the move (rider 1/57→1/35).
2. **Sky:** 5.2 has no `NISHITA`; it is `SINGLE_SCATTERING` (same model). At a 2–5° sun it turned murky beige; `MULTIPLE_SCATTERING` (new in 5.x) reads as real dawn (blue zenith, peach horizon) → used. The 5.2 sky is physical (sky radiance 2–12, sun disc ~1e6), so world strength 1.0 + exposure +0.2 was ~3.5 stops over → exposure −3.1. Sun lamp 18 W/m² instead of 3–5: at this sky scale 3–5 W/m² is weaker than the skylight and the crest changed nothing; 18 W/m² ≈ 6× the sky's horizontal irradiance (a real low-sun ratio) and makes the crest visible.
3. **Cloud volume:** the brief's cube with noise-driven density costs ~1.1 CPU-s per 480×270 sample (biased marching: the step is 0.1 × mean box size, ~870 m, unless the material step rate is tiny; null scattering + an ~18 s octree build was no cheaper) → ~300 CPU-s per 720p frame. Same medium (Principled Volume, density 0.05, anisotropy 0.3) but homogeneous, bounded by a billowed shell mesh → analytic integration. `volume_biased` + step rate 2.0 are kept as set (they only matter for heterogeneous media).
4. **Volume bounces 0 (brief: 1)** + constant emission 0.008: −37 % on cloud pixels at the same brightness (A/B checked on crops); the only way into the CI budget without shrinking the shot.
5. **Render settings set in build():** adaptive threshold 0.12 + min samples 8 (the harness leaves min at "auto", which on 64 spp means a 48-sample floor; with 8 the floor is Cycles' 16-sample adaptive step: 82 % of pixels stop at 16), OIDN prefilter FAST (ACCURATE cost ~13 CPU-s/frame), diffuse/glossy bounces 0 (basalt albedo ≤0.07), light tree off (2 lights), Embree spatial splits, persistent data.
6. **Lighting sky = node fit:** non-camera rays see a ramp fit (elevation × azimuth × per-frame gain) sampled from equirects of the 5.2 sky at 2/3.5/5°; camera rays see the real sky + disc. Static terrain haze (no per-frame shader recompiles; emission sampling off on haze materials — with it ~1 M terrain triangles became mesh lights).

## Render cost (measured)
- Final check, harness, frame 110, 1280×720, 64 spp, box nearly free (load 1.4–1.7): **25.3 s/frame wall** (`frame 111/111 25.3 s/frame`); whole process 52.7 CPU-s incl. the 3.2 s build → ≈49 CPU-s per frame → **≈12–13 s/frame on a 4-vCPU runner** → 130 lit + 14 black (~1 s) frames ≈ 28 min (< 45). An earlier run of the same frame while other agents loaded the box: 55.1 s/frame wall, 58 CPU-s (wall ≈ CPU = one core available).
- Before the single-scattering change, frames 30 / 100 / 125 measured within ±3 % of each other at full res, so f110 is representative. 640×360/64 spp check frames: ~7 s wall (free box), ~15 CPU-s.
- History (CPU-s per 720p frame): 295 (noise-driven volume) → 98 (homogeneous shell) → 86 (FAST prefilter) → 79 (splits, bounces) → ≈49 (single scattering + emission stand-in).
- Determinism: two separate harness runs of frames 100–101 are pixel-identical (max diff 0).

## Sound (audio.py → out/p07-ash-ascent/audio.wav)
6.000 s, 48 kHz stereo, peak −4.3 dBFS, RMS −23 → −15.5 dBFS into the crest; the 14 black frames are digital silence (max sample 0). Cue sheet printed by audio.py; hoof times imported from `blender.hoof_plants()`; crest cue at `blender.T_CREST`.

## QC log
- v1 (480×270): ridge = a centred glowing yellow pyramid (haze emission sampled the sun-side sky ×50 brighter than basalt; ash band too wide; ridge seen end-on); sky cream/beige (single scattering at 2–5°); 26 s/frame at 480×270 → profiling.
- v1 perf: every terrain/floor triangle was a mesh light (haze emission + AUTO emission sampling) → light tree rebuilt per frame, 2nd frame 2× slower; 7 sky LUTs per frame. Fixed: static analytic haze, emission sampling NONE, hide_render only on change.
- v2: multiple-scattering sky (blue + peach) fixed the palette; ridge relief + steeper flanks; heterogeneous clouds still ~1 s/sample → homogeneous shell. Clouds read better (billows, soft, blue) and 2× cheaper.
- v3: volcano was a pale cardboard massif (warm haze, wide shoulder, ash) → cool haze only (the air in front of a backlit peak is in its shadow), darker rock, narrower cone; bloom clamped (sun disc ~1e6 blew a huge glow).
- v4: crest changed nothing on the ridge (sun 4 W/m², grazing) → 18 W/m²: the volcano's shadow wedge appears on the cloud sea, gold tops on the left, warm rim on the crest. Flat-table far horizon → curvature + hazed far deck + below-horizon haze for camera rays. Volcano base haze overdone (glowing) → toned down.
- v5: rider read as a narrow blob (15° off his axis) → crest jog gives a 3/4 rear view (40°); reaction made legible with a staff lift (dip → rise).
- v6/v7: volcano too perfect → concave profile, irregular flanks, broken rim; analytic crest was 2–3 frames late vs render (mesh silhouette, disc glow) → SUN_ROT re-solved on rendered crops (f90 0 sun pixels, f91 20). Exposure +0.2 EV (pre-dawn ridge was sliding to mud). Black frame had dither noise (max 1) → dither 0 → true 0.
- Motion check: 12 consecutive full-res rider crops (f100–111, `motion_burst.jpg` tiles 6): silhouette stable (no flicker), legs cycle, staff tip rises from ~f107; camera speed curve 34 → 3 m/s (no glide, settles into the hold).
- v7b: reaction pose signs were inverted (horse's head went down, rider looked down) → fixed (head up, rider straightens and looks up); affected keyframes + burst re-rendered.
- Open: the volcano is still a clean cone (a small backlit ash plume would sell "volcanic" and add life); the reacting beat only reads at 1:1 (as briefed, the rider is tiny); upper sky a little pale; clouds are single-scatter + emission rather than true multiple scattering.
