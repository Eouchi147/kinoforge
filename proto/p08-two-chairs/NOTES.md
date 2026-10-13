# P08 — TWO CHAIRS (12 s, 16:9, 24 fps, 1280x720)

**Lane:** characters & comedy. **Logline:** Rémi rehearsed a speech for three weeks; Bo asks what happened.
**Proves:** a hierarchical 2D rig drawn in Canvas 2D (body → head → eyes/lids/brows/mouth, IK arms with five-digit hands)
driven by real TTS dialogue (Kokoro) and Rhubarb visemes (9 distinct mouth shapes, ≥2-frame holds, lips closed on p/b/m);
deadpan comedy grammar: locked-off cameras, no sting, an 18-frame beat before the punchline, a 12-frame reaction hold,
then a cut to the face. Picture and sound share ONE cue file (`lines/cues.json`), so sync is by construction.
**Emotion arc (Plutchik):** anticipation (Rémi's nervous pride) → trust/flat (Bo) → anticipation rising (the build) →
(beat) → surprise (punchline) → sadness, low intensity (pensiveness: the deflation).

## Final shot list (= code: `lines/cues.json` shots + `CAM` in scene.js)

| ID | frames | time | size / "lens" | move + motivation | light | sound | emotion |
|----|--------|------|---------------|-------------------|-------|-------|---------|
| S1 | 0–73 (74 f) | 0.000–3.083 | WS two-shot, z 1.1 (≈38 mm eq.) | locked-off: deadpan authority (R-2-04, R-8-08) | overhead warm stage spot: pool between the chairs, soft haze cone, spill on the curtain | room tone, pad fades in, L1 at f14 | anticipation |
| S2 | 74–99 (26 f) | 3.083–4.167 | MCU Bo, z 3.0 (≈105 mm eq.), eye-line on the right third, lead room left | locked-off | same spot, key from his front-left (stage centre) | L2 "Mm-hm." on the cut | trust (flat) |
| S3 | 100–177 (78 f) | 4.167–7.417 | MCU Rémi, z 2.55 (≈90 mm eq.), left third, lead room right for the gesture | locked-off; the motion is the performance (weight shift + gesture) | same | creak 1 at 4.267 (his visible shift), L3 on the cut | anticipation ↑ |
| S4 | 178–210 (33 f) | 7.417–8.792 | MCU-tight Bo, z 4.1 — one size step in from S2 | locked-off; Bo's only move: 3° (≈2 px) head tilt on "And?", then the 18-f beat on his stare | same | L4 "And?", then the beat (room tone + pad −6 dB) | anticipation (setup) |
| S5 | 211–245 (35 f) | 8.792–10.250 | MS two-shot, z 1.42 (≈50 mm eq.) — a size step in from S1 | locked-off | same | creak 2 on the cut (his lean-in), L5 punchline on the cut | surprise |
| S6 | 246–257 (12 f) | 10.250–10.750 | MCU-tight Bo (= S4 framing, not consecutive) | locked-off; one slow blink 3/2/4 (f247–255) | same | pad CUT on the cut: room tone only | flat |
| S7 | 258–287 (30 f) | 10.750–12.000 | CU Rémi, z 3.25 — tightest size on Rémi = emotional peak (R-2-01) | locked-off; deflation: shoulders −4 px (f259–268), brows up/in, head sinks, glasses slip, slow blink f262–270, eyes reopen lower; hold to the end | same | room tone only | sadness (low) |

"Lens" in a 2D stage = a pure crop of one locked camera position (equivalent focal length ≈ 35 mm × zoom). Singles are
framed on the character's computed eye-line at the shot's first frame, then locked (the camera never follows).
Screen direction (R-2-05): Rémi always screen-left looking right, Bo always screen-right looking left; eyelines converge.
Shot lengths 74/26/78/33/35/12/30 f (CV 0.54; no 4 equal in a row). Locked-off 7/7, pushes 0.

## Dialogue — measured durations and final cue times (written by build_lines.py → lines/cues.json)

Kokoro TTS (Rémi `am_michael` 1.08, Bo `bm_george` 0.92), trimmed to speech (20 ms pre-roll, 80 ms decay tail), Rhubarb
1.14 (PocketSphinx + dialog text for word times; phonetic recogniser for the non-word hum). Kokoro's G2P spells "Mm-hm" out
as letter names, so L2 is fed as phonemes `əm hˈəm.` (a PocketSphinx ASR check hears "hum hum"). L3's two full stops were
opened to 0.26 s each (Kokoro ran them at 60 / 240 ms) for the comic list rhythm.

| line | text | speech dur | file dur | nominal (brief) | **cue (start)** | speech on → off |
|------|------|-----------:|---------:|----------------:|----------------:|-----------------|
| L1 Rémi | "I rehearsed this speech for three weeks." | 1.905 s | 2.005 s | 0.6 | **0.583 s (f14)** | 0.603 → 2.508 |
| L2 Bo | "Mm-hm." | 0.935 s | 1.030 s | 3.1 | **3.083 s (f74)** | 3.098 → 4.033 |
| L3 Rémi | "Three weeks. In the mirror. With hand gestures." | 2.860 s | 2.960 s | 4.0 | **4.167 s (f100)** (+0.167: L2 runs to 4.033) | 4.187 → 7.047 |
| L4 Bo | "And?" | 0.605 s | 0.689 s | 7.4 | **7.417 s (f178)** | 7.437 → 8.042 |
| L5 Rémi | "The mirror said no." | 1.095 s | 1.195 s | 8.6 | **8.792 s (f211)** (+0.19: keeps the beat) | 8.812 → 9.907 |

Rules applied: nominal time rounded to a frame, pushed later only if the previous line's last sound + 120 ms would be
overlapped; L5 = first frame whose speech onset is ≥ 18 frames (0.75 s) after the last sound of "And?" → **beat 0.770 s
= 18.5 frames of nothing** between the last and first audible sound (f195–f210 hold no dialogue samples at all, including
the stem's decay tail). No file overlaps anywhere. Shots cut on the first frame of the next
speaker's line; S6 = last syllable of the punchline + 8 f; S7 = S6 + 12 f; total 288 f.
Word times (for acting): "speech" 1.293, "for" 1.683, "weeks" 2.063, "mirror" 5.207, "hand" 6.047, "gestures" 6.427,
"mirror" 8.882, "no" 9.512 s.

**Lip-sync (R-9-14):** per-frame mouth tracks sample Rhubarb at t + 35 ms (mouth leads by 0–35 ms), then every viseme is
held ≥ 2 frames (a 1-frame shape steals a frame from a long neighbour, preferring the earlier side; 1-frame B/X merge;
A closures are never dropped). Measured on all 42 onsets: offset −50…+5 ms (sound never more than 5 ms early); 40/42 inside
the ATSC window; the two outliers show the shape 48–50 ms before the sound. Closures (A): L1 "speech" f30–31 (−13 ms),
L2 "mm" f76–78 (−17 ms) and f87–92 (−8 ms), L3 "mirror" f125–126 (+2 ms), L5 "mirror" f213–214 (−7 ms) — all rendered and
confirmed closed (`out/p08-two-chairs/lipsync_L1.jpg`, `lipsync_bo.jpg`, `lipsync_mirror.jpg`; "for" f39–40 = G, "weeks"
f50–51 = F). Min hold: 2 frames on both tracks. All 9 shapes are drawn (`mouth_chart.jpg`); this dialogue's Rhubarb tracks
use 7 of them (Rémi A B C E F G X, Bo A B C F X — no D/H occur).
**Prosody (R-9-13):** F0 contours differ line to line — L1 rise-fall statement; L2 "mm-HM" 192 → 123 → 210 → 89 Hz; L3
three falling fragments; L4 high-onset fall 210 → 70 Hz (a flat, unimpressed "And?" — in character for Bo, though not a
rising question); L5 low-onset rise-fall with a second accent on "no".

## Rig & acting
- World = the stage in stage px (1 unit = 1 px of the wide). Outlines held at 2–3 screen px at every zoom (width / zoom),
  each ~40% darker and cooler than its fill. Cel shading per part: shadow crescent away from the overhead key (shape minus
  itself shifted toward the light), thin warm rim on the lit edge. Bent limbs are single seamless outlines (custom limb
  path), arms are 2-bone IK to pose targets, hands are five digits (ink underlay + fill).
- RÉMI: hip → torso (breath 3.5 s, lean, deflation) → neck → head (nods on stressed syllables, tilt) → hair + cowlick
  (lags the head by 3 frames: overlap R-5-04) / ear / eyes (lids, darts) / long nose / mouth / round glasses / big brows
  (up/in = anxious); shoulders → IK arms → hands. Weight shifts with counter-moves at f62, f102 (creak 1), f140–159
  (gesture), f211 (creak 2), f259 (deflation). Blinks: f8, f101 (head move), f171 (pride beat), f240 (fast, after "no."),
  f262 slow 3/2/4 (thought change). Darts (3–4 f): f64, f116 (recalling, after "weeks."), f137 (after "mirror."),
  f220 (eyes drop on "said").
- GESTURE on "hand gestures": anticipation f140–145 (hands gather to the belly, body hunches +1.4°), action f145–151
  (outBack to a two-handed presenting pose, near hand high, far hand low, palms open), overshoot + settle f151–159,
  moving hold to the cut; hands return to the knees off-screen during S4.
- BO: hip → round body (breath) → hood → sleeve into the kangaroo pocket; head (beanie, half-lids, flat brows, button nose,
  tiny mouth). Moves only: breath, lips, the 3° head tilt (f178–184, held), one slow blink (f247–255, mapped onto his
  half-lid range so every frame reads). No other blinks: the stare is the joke.

## Colour script & grade
- One palette: dark slate-violet curtain (the faint back wall) warmed by the spot's spill, dark umber boards with a warm
  perspective pool, soft haze cone + a few drifting motes = the visible source (R-4-01). Rémi warm mustard/ochre,
  Bo cool teal/slate. Faces always on the lit inner side; spot falloff darkens the outer sides of both figures.
- Grade (every shot): kit `cel` base, sat 1.06, contrast 1.05, grain 0.035, vignette 0.30, halation 0.06 (threshold 0.82,
  highlights only), cool shadow tint / warm highlight tint. No letterbox.

## Sound (audio.py reads lines/cues.json; output 12.000 s = 576000 samples, peak −1.57 dBFS)
```
  0.000s  f  0.0  12.00s  -40.0 dB  room tone (L/R decorrelated low-passed pink noise, slow drift)
  0.000s  f  0.0  10.25s  -34.8 dB  warm pad Cmaj7 (fades in; −6 dB through the beat; CUT on S6 frame 1, 12 ms declick)
  0.583s  f 14.0   2.00s  -17.8 dB  L1 REMI (gated RMS −16 dB, limiter −3.5 dB peak GR)
  3.083s  f 74.0   1.03s  -16.5 dB  L2 BO
  4.167s  f100.0   2.96s  -17.0 dB  L3 REMI (limiter −1.0 dB)
  4.267s  f102.4   0.55s  -32.0 dB  chair creak 1 (low K-S plucks + stick-slip rasp, panned to Rémi)
  7.417s  f178.0   0.69s  -16.7 dB  L4 BO
  8.792s  f211.0   1.20s  -16.7 dB  L5 REMI (limiter −2.1 dB)
  8.792s  f211.0   0.55s  -32.0 dB  chair creak 2 (his lean-in on the punchline cut)
```
Checks: every line correlates with the mix at lag 0 samples at its cue frame (sample = frame × 2000). Beat (8.06–8.80 s)
−37.2 dB RMS vs punchline −16.3 dB → 20.9 dB under (R-3-06). S6/S7 −43.5 dB (room tone only). No music sting.
(Levels in the sheet are plain RMS over each placed element; dialogue is normalised on gated RMS.)

## Waivers (written reasons)
- R-3-07 split edits: none. Deadpan grammar — every cut lands on the first frame of the next speaker's line, so the edit
  itself is the comic timing (R-8-08); J/L overlaps would soften it.
- R-3-08 reaction ≥ 24 f: S6 is 12 f by design (R-8-08: hold 6–12 f, then cut to the face); the face hold S7 is 30 f.
- R-2-07 foreground plane: only the wide has one (stage lip, thin); singles stage in three planes (figure / chair / curtain).

## QC log
- v1 (one frame per shot): thigh drawn over the cardigan from behind; far legs hidden; brows lost under the hairline and
  the glasses; S7 frown inverted (X-mouth curve sign bug → read as a smile); Bo's mouth half outside his face contour and
  his nose on the contour (stuck-on ball); Bo's arm read as a hug, not hands-in-pockets; far arm tangled in the gesture.
  Kit bug found (overlay colour space, below).
- v2: near leg under the hem, far legs offset; hairline raised, brows thicker and above the frames; true 3/4 face layout
  (far eye inside the contour, nose from the bridge); Bo's features re-centred; frown fixed; sleeve + pocket mouth.
  Found: singles framed on guessed eye positions drifted (CU off-centre right) because accumulated lean moved the head.
- v3: singles framed on the computed eye-line at each shot's first frame; leans reduced; two-handed presenting pose
  (asymmetric heights, clear of the face); Bo nose softened (outline only on its outer edge + nostril).
- v4: viseme chart rendered — G too close to B → G now shows upper teeth over a tucked lower lip. Lip-sync frames rendered
  and inspected (all closures closed). Far knee read as a stick behind the hands → less dark, wider; pocket rounded;
  haze cone + motes added for a visible source.
- v5: cone had hard geometric edges → six nested low-alpha cones (soft volume). Bo's slow blink started inside his
  half-lid (first frames invisible) → remapped onto his lid range. Rémi gets a pride blink at f171 (closes a 5.8 s gap).
- Motion bursts (640x360): gesture f138–162 (`burst_gesture.jpg`: gather → snap → overshoot → settle by f156, holds),
  S7 f258–273 (`burst_s7_blink.jpg`: deflation + 3/2/4 blink), Bo f246–257 (`burst_bo_blink.jpg`).
- One full 640x360 pass with audio for cut rhythm: `out/p08-two-chairs/preview/p08-two-chairs.mp4` (+ contact sheet),
  no page errors.

## Known weaknesses / next steps
- Bo's singles leave the left half as empty curtain and the warm backrest is the brightest object at the right edge.
- Rémi's resting hands read as mitts at wide-shot scale; hands could use dedicated rest/grip drawings.
- Chairs are flat 3/4 cut-outs (no seat perspective); hair has no secondary motion except the cowlick.
- "And?" falls rather than rises (Kokoro); a rising read would need a different phoneme/intonation input.

## Kit notes
- BUG: `makeComposer` overlay CanvasTexture is tagged `SRGBColorSpace`, so the overlay is linearised on sampling and never
  re-encoded: canvas rgb(128,128,128) lands as 55, (30,27,38) as (3,3,5). Workaround in scene.js:
  `post.overlay.tex.colorSpace = THREE.NoColorSpace` (verified exact pass-through). Affects every overlay title too (p05).
- `tts.say()` cannot take phoneme input; `tts.visemes()` uses only the phonetic recogniser (no word times). build_lines.py
  calls Kokoro with `is_phonemes=True` and Rhubarb PocketSphinx + dialog text directly.
- Repo hygiene: `.gitignore` excludes `*.wav`, so `lines/*.wav` (the dialogue stems audio.py needs) are not committed by
  default — force-add them or re-run build_lines.py (needs Kokoro + Rhubarb). cues.json + analysis.json are committed text.

## Files
`index.html`, `scene.js` (rig, shots; QC-only params `?chart=1` viseme chart, `?cu=remi|bo` tracking close-up),
`build_lines.py` (TTS → stems → Rhubarb → cues), `lines/` (L1–L5 wavs, `cues.json`, `analysis.json`), `audio.py`.
