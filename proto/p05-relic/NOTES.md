# P05 — RELIC (10 s, 2.39:1, 24 fps)

**Lane:** epic cinematic / game-trailer grammar. **Logline:** In a cavern cathedral, a pilgrim reaches a buried monolith as it wakes.
**Proves:** trailer phase map in miniature (cold open → quiet build → turn → silence → title stinger → tag), volumetric light, carved emissive materials, a scale figure, one accent colour reserved for meaning (ember red = the waking).
**Emotion arc (Plutchik):** anticipation → awe → fear/anticipation (apprehension→fear) → (void) → dread/wonder at the title.

## Shot list

| ID | dur | size / lens | move + motivation | light | sound |
|----|-----|-------------|-------------------|-------|-------|
| S1 | 2.2 s | ECU, 90 mm | locked-off (dread; R-2-04) + dust drift | raking god light from above, grooves in shadow (8:1+) | cavern air, drip, drone enters (hook: what is this?) |
| S2 | 3.0 s | EWS→WS, 24 mm | crane up from floor behind rubble = reveal/scale (R-8-06: figure ≈1:20 of the cavern) | god light + 3 shafts, cool rim on the pilgrim, walls faint | drone swells, choir pad, Shepard dread, whoosh on the cut |
| S3 | 2.4 s | OTS MCU, 40 mm | push-in past the pilgrim = realization (R-2-04); hand-held amplitude grows with the wake | runes ignite bottom-up, relic point light, embers | riser ends exactly on the cut, pulse, crackle, hum |
| S4 | 0.5 s | black | — | — | SILENCE ≥12 f (R-3-06) |
| S5 | 1.9 s | title | "RELIC" forms from ember glow; tag "It was never buried." at +0.75 s | — | hit + sub drop + one braam (R-6-07) + tail pad |

Colour script: slate/bone cavern → warm god light → ember red accent (≤3% of frame until S3) → black → ember title on black.
Grade: `ember` preset, halation 0.4, grain 0.055, vignette 0.42, aberration 0.12 (edges only). Letterbox 2.39.

## QC log
- v1: S1 glyphs read raised, not carved → inverted height map (grooves dark) and softened normal strength.
- v1: shafts invisible → shader falloff was alpha-squared; now additive rgb falloff with view-angle edge fade.
- v1: OTS framing missed the pilgrim (camera 30° off his axis) → camera placed 0.9 m behind his head, 0.2 m right, 40 mm.
- Open: stone surface still reads smooth under the ECU; candidate fix = triplanar grain normal + roughness breakup.
