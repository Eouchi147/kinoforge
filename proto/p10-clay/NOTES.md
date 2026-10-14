# P10 — CLAY (6 s, 16:9, 24 fps, animated ON 2s — Blender/Cycles CPU)

**Lane:** characters & comedy / artisanal stop-motion look. **Logline:** A clay snail admires its glossy new shell; a falling apple pancakes it; it re-inflates in three pops and stares us down, dignified.
**Proves:** the Blender path of the KINOFORGE contract (`blender.py`: `build` / `frame` / `SETTINGS`), stop-motion grammar (poses on 2s, per-pose hand jitter, a replacement smear, replacement mouths, pose-seeded grain), squash & stretch with rough volume preservation, rule of three, deadpan comedy timing (locked-off, a beat after the hit), and a physically motivated anticipation cue (the apple's shadow under real gravity).
**Emotion arc (Plutchik):** joy/pride → anticipation → fear → surprise (impact) → (stunned beat) → anticipation (pop, pop…) → pride regained (deadpan dignity).

## Shot list (one shot, locked-off) — final = code

| ID | dur | size / lens | move + motivation | light | sound |
|----|-----|-------------|-------------------|-------|-------|
| S1 | 6.0 s (144 f, 72 poses) | MS, low angle: lens 6.6 cm off the paper, 0.56 m from the snail, looking up at its eyes (≈13 cm); 50 mm; f/4 focused between the eyes and the shell face (shallow tabletop DOF) | **locked-off** — deadpan (R-2-04, R-8-08). Only a 2-pose set jolt on the impact (f52 down 6 mm / roll 0.85°, f54 counter 3 mm / −0.4°): the table is hit, the stand is not. | key = 1×1 m area 300 W 4000 K front-left-high (soft modelling); fill = 1×1 m area 60 W 8000 K front-right-low; rim = 0.4 m area 40 W behind-right-high (edge on shell/eyes vs. the paper sky, R-4-02); "sky" = sun 1.2°, 110 W/m², tilted 3° toward the lens, **light-linked to light only the paper ground** and shadowed only by the apple + the snail's masses: it gives crisp contact shadows and the falling apple's shadow without flattening the puppets' modelling | room tone, uke plucks, falling whistle + wind drop, splat + thump, dead air, squeak, roll foley, three boings, plop, chord, blink click |

## Beat sheet (pose frames are even; every odd frame is the same picture)

| f | t (s) | beat | principle | sound |
|---|-------|------|-----------|-------|
| 0–2 | 0.00 | proud snail, 3/4 to camera, smile, eyes front | establish | room tone |
| 4–6 | 0.17 | eye stalks dip forward | anticipation R-5-01 | pluck C5 (f4) |
| 8–14 | 0.33–0.58 | stalks swing back over the head to the shell: −8/−34/−52 (overshoot)/−44°; lids drop to a contented half | ease + overshoot + settle | pluck E5 (f14) |
| 16–24 | 0.67–1.0 | proud wiggle: body dips 0.95, stretches 1.05, settles; shell rocks −2.5/+6/−4/+2/0° | anticipation / overshoot / settle | pluck G5 (f24) |
| 26–32 | 1.08–1.33 | chest-out puff (body 1.045, shell 1.06, chin up) | rule of three #3 | — |
| 32 | 1.33 | off screen, 3.4 m up, the apple lets go (free fall, real g) | R-9-03 | — |
| 34–38 | 1.42 | **eyes dart UP**: one big in-between, overshoot, settle; lids snap wide; mouth → "o" | dart R-5-05 | varied motif C5 → E♭5 (minor turn) |
| 38–48 | 1.6–2.0 | fear: stalks tremble ±1.6°/pose, eyes swell to 1.2, pupils shrink; the apple's umbra (r = 4.6 cm − h·tan 0.6°) appears as a speck in the foreground and slides in, growing, as h(t) = gTτ − gτ²/2 drops | real gravity | falling whistle + wind drop 1.567 → 2.167 (fades over the last 3 f) |
| 50 | 2.08 | replacement **smear** apple (2.7× stretched) | R-5-03 | — |
| 52 | 2.17 | **IMPACT 1**: apple squash 0.7, snail Z 0.45, set jolt | squash | SPLAT + set thump |
| 54 | 2.25 | **IMPACT 2**: snail flat Z 0.15 / X 1.6 / Y 2.2 (≈0.53 vol), apple rebounds (1.12, +9 mm), eyes pop out sideways (×1.34), counter-jolt | | 8 f of dead air |
| 56–80 | 2.33–3.33 | **HOLD flat (28 f)**: apple settles (0.9 → 1.03 → 1.0); f62 pupils pin; f64 apple rocks back, rolls off right over the flattened tail, drops onto the paper (f76), hops (f78), rolls to rest on its side (f88), rocks, settles | beat before the punchline R-8-08 | squeak f62; soft roll, tok f76, tick f80 |
| 80 / 82 | 3.33 / 3.42 | dip, then **inflate #1** (small) Z 0.37 → 0.32 | rule of three | boing 180→260 Hz |
| 92 / 94 | 3.83 / 3.92 | dip, **inflate #2** (medium) 0.68 → 0.62 — flat shell rides on top like a hat | | boing 220→330 Hz |
| 104 / 106 | 4.33 / 4.42 | dip, **inflate #3** overshoot 1.22 → 0.92 → 1.05 → 1.0 | overshoot / settle | boing 260→420 Hz |
| 110 | 4.58 | shell pops back last 1.25 → 0.90 → 1.05 → 1.0, with a rock | follow-through R-5-04 | soft plop |
| 110–118 | 4.6–4.9 | dazed: lids droop, one quick blink (f114), stalks askew, pupils diverge, head droops | | — |
| 118–122 | 4.92–5.08 | stalks compress 0.90 → snap straight 1.07 → settle | anticipation | — |
| 124 | 5.17 | eyes to the lens, half-lidded, chin up 9°, head turns 18° to us, smile back: **dignified** | turn to lens | resolving pluck chord |
| 132–140 | 5.5–5.83 | one slow blink: lids 4/2/4 f (close/closed/open) + eye Z squash 0.78 | long blink R-5-05 | blink click |
| 140–143 | 5.83–6.0 | hold the look | | chord tail |

Holds: the flattened key image holds 28 frames; the final look holds from f124 to the end (20 frames including the blink).

## Colour script
Pale painted-paper sky (cool, light) with a painted gradient to a deeper blue at the top; sage painted-paper ground (mid, muted) → the snail is the warm mid-value (mustard clay) with a saturated **teal** glossy shell + cream spiral stripe (its pride). **Red is reserved for the apple** (the threat) and appears only from f50; the impact frames are the only time red and teal touch. Ending: opening palette back, the red apple resting at the right third, slightly deeper (softer) than the snail.

**Grade:** one look — AgX "Base Contrast" at −3.4 EV exposure (`'AgX - Medium Contrast'` does not exist in bpy 5.2: Base is the middle step between Medium Low and Medium High, and the harness silently ignores unknown look names). Pose-seeded multiplicative grain in the compositor (±3.5 %), a ≈0.25-stop corner falloff, no halation, no letterbox, no motion blur.

**Set:** tabletop diorama — painted-paper ground (brush streaks, paper tooth), two slightly bowed card sky sheets with a visible vertical seam (tone step + lit card edge) placed between the snail's tail and the apple's resting place, an out-of-focus clay grass tuft in the lower-left foreground (depth + scale).

**Puppets (all procedural):** body = a generalised-cylinder sweep of an elliptic section along a spline (foot sunk 2–3 mm into the paper), head sphere on a neck pivot, coiled-snake shell (log spiral, tube radius ∝ radius so the turns touch) with a cream snake pressed into the groove, eye stalks + eyes + pupil discs + thick clay eyelids, replacement mouths (smile / "o" / flat); apple = dented sphere by vertex push (no booleans), stem, leaf. Every mesh gets small smooth vertex noise (hand-made lumps). Clay shader: Principled, subsurface 0.3, radius (0.02, 0.01, 0.008) m (Burley), roughness 0.55 (shell 0.30 "new and shiny"), bump = noise 40 lumps + stretched-noise dents + fine tooth at strength 0.15.

## Render budget (CI: 144 f in 45 min on 4 vCPU, setup included)
* Profiled at 640×360: cost is path-traced samples, not features — subsurface off saves ~2.5 %, fewer bounces 0 %, light tree off 0 %, DOF ~3 %, adaptive threshold 0.02 → 0.06 saves 16 %. So the brief's "subsurface → 0" fallback would not buy the budget; SSS stays.
* Optimisations kept: bump + SSS evaluated on camera rays only (Light Path branch; bounces use a cheap twin BSDF), low-octave noise, no bump on the defocused sky, persistent data, Burley SSS, OIDN.
* **On-2s pair reuse:** frame 2k+1 is by contract the same picture as 2k, so when it is rendered right after its partner in the same process, `frame()` sets a 2×2-px border and a `render_write` handler copies 2k's PNG over it (byte-identical; verified on 48–59). First frame of any range, single-frame calls and the clip's last frame always render in full. `KF_NO_PAIR_REUSE=1` disables it (pairs are then still pixel-identical: determinism verified, see QC v4).
* **Measured (this 2-vCPU shared box, harness, 1280×720, one frame f126):** 64 spp as briefed = **400 s/frame wall, 297 CPU-s** → ~83 s per path-traced frame even on 4 ideal vCPUs → does not fit 45 min (≈100 min with pair reuse, ≈200 without). Shipped: **16 spp cap** + OIDN balanced + 0.04 threshold = **71 CPU-s (37 s wall on 2 vCPU when the box was quiet)** per path-traced frame; a reused odd frame ≈ 1 CPU-s. 1:1 crops of 64/24/16 spp are indistinguishable (mean abs diff vs 64 spp: 0.51 / 0.56 of 255, under the grain). CI projection: 72 × 71 CPU-s / (4 vCPU × 0.9) ≈ 24 min + setup ≈ **29–31 min for 144 frames** (≈ 10 s/frame average).
* The cap lives in `build()` (`SPP_CAP = 16`, env `KF_P10_SPP_CAP`), because the workflow passes `--samples 96` by default, which would otherwise override `SETTINGS`.

## QC log
- **v0** (first frame): ~1.5 stops hot (frame mean 0.83), pastel colours; eyes too small; profile view stacked both eye stalks; no contact shadow (apple-only shadow linking let the sky light leak under the snail); 37 CPU-s at 640×360/24 spp.
- **v1:** 3/4 turn (25°) so both eyes read; eyes 2.4 cm; head smaller; profiling showed shaders/SSS/DOF/bounces are not the cost → camera-ray-only bump/SSS, low-octave noise, sky without bump; pair reuse designed.
- **v2:** exposure −3.4 + deeper sky card + darker ground (mean 0.83 → ~0.5, colours hold); lower tentacles read as tiny hands → removed, replacement mouths added; apple floated 1.4 cm above the squashed shell (my shell-top constant was wrong: a log spiral is smaller at the top) → raycast contact solver (apple's lower vertices dropped onto the posed snail + paper, 2–6 mm "press" at the impact); Z-squash blink read as white plates from the low lens → body-colour eyelids on top of the squash (and the half-lid gives the deadpan "dignified" read); f20 eyes hid behind the shell rim → admire pose leans 18° less.
- **v3:** apple contact correct; apple shadow invisible: (a) sky light was only ~25 % of the ground's light → receiver-linked to the ground only, 28 → 110 W/m², ground albedo down; (b) a vertical sun puts the umbra where a 6 cm-high lens cannot see it → 3° tilt toward the lens: the tiny umbra lands in the visible foreground and slides in as it grows. Popped eyes cut by the left frame edge, apple half out of frame, seam tangent to the apple → camera pulled back to 0.56 m and centred, apple path 23° further right, seam between tail and apple.
- **v4:** grass tuft was a stray sliver at the frame edge → moved into frame (lower-left, clear of the popped eyes). Determinism bug: the gaze read the camera's jolted position from the previous frame → first render of a pose differed (max 48/255 on the eyes) → eyes aim at the nominal lens; now the same pose renders pixel-identically first or later. Impact jolt ~2 px at 360p → doubled.
- **Timing burst (f48–f59 via the harness, pair reuse on):** f48 shadow under the front → f50 smear → f52 squash → f54 flat + rebound + eyes pop → f56/f58 settle: one-pose fall reads as a hit, no float; all six frame pairs byte-identical.
- **v5 (final check):** 1280×720/64 spp = 400 s wall / 297 CPU-s → 16-spp cap after a 64/24/16 spp 1:1 comparison (no visible difference); all 144 poses dry-run clean (no exceptions, odd = even pose state, eyes/lids never under the paper, apple never sinks > 3 mm); harness frame 0 and ranges run clean; audio 6.000 s, peak −1.8 dBFS, splat 31 dB over the 8 f of dead air after it.
- **Sound vs rulebook:** cues snapped to pose frames (≤ 1 f from the brief's times). R-3-06: the brief runs the whistle into the hit, so the last 12 f before the splat sit 16.5 dB under it (last 4 f: 21 dB, the whistle fades out); the real silence is the 8 f after the hit, as briefed.
- **Kit notes:** `'AgX - Medium Contrast'` is not a bpy 5.2 look and the harness silently ignores bad look names (try/except: pass); the harness log prints the CLI spp even when a scene caps it; `sfx.whoosh(direction=-1)` does not reverse the sweep (it only flips a symmetric envelope) → used lo > hi; `sfx.hit(tail=False)` still has a slow sub decay (~0.45 s) → re-enveloped for the splat.
- **Open:** the shadow cue is soft (umbra partly in the out-of-focus foreground) — reads in motion with the whistle, but a slightly higher lens or a smaller sky angle would sharpen it; fingerprint detail is subtle at 720p.
