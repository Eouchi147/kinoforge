# Engines the director can use (pick per film, per scene or per shot)

| Engine | What it makes best | Cost | Where |
| --- | --- | --- | --- |
| Shot factory (`harness/shots/factory.py`) | Cinema-level footage: people, acting, real light, products, stylised 3D/anime looks, ads | $0.03–0.40 per generated second (live list: OpenRouter `/api/v1/videos/models`) | GitHub runner calling OpenRouter |
| Code styles (12 packs in `proto/`, scene agent) | Exact, repeatable, free: paper theatre, clay, cel, ink, pixel, VHS, kinetic type, terrain flyovers, data/maps | ~$0.10–0.60 per film for the code writer; rendering free | GitHub runners / Mac |
| Hybrid | Generated footage + code-made titles, logos, captions, lower thirds, end cards, transitions, grade | factory cost only | factory `edit()` + kit |
| Voice | ElevenLabs Eleven v3 (premium, ads) or OmniVoice / VoiceStudio (free, long narration) | $0.04 / 1k chars (50% off to Oct 19) or free | OpenRouter / voice lane |
| Music | Google Lyria 3 (scores) or VSCO-2 orchestral sampler | $0.04 per 30 s clip or free | OpenRouter / sampler |

Rules of thumb
- Text, logos and numbers on screen: always the code engine, never generated.
- Brand products: one reference image, reused in every keyframe; never let the video model invent the product.
- Draft at the cheap tier (Veo 3.1 Lite 720p), final at standard (Veo 3.1 Fast 1080p) or premium (Veo 3.1).
- Directions (`harness/shots/directions/*.md`): `voltage` (kinetic, stylised, beat-cut), `classic` (premium photoreal). Add more as files.
