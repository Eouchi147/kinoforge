# Ad: Unmissed, The Catch (`unmissed-v2`)

An 18.2 s, 16:9 brand ad in Three.js: notifications (calls, messages, leads) stream through dark space toward the camera, some
slip past into the gaps, then a glass ring forms and catches every one; they orbit and are absorbed, and the ring becomes the
logo. Apple-keynote calm. Built music first on 16 Oct 2026 as version 2 of five directions. Sam's verdict: the visuals "a little".
Style: `docs/manual/styles/business-ads.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `ads/unmissed-v2/` (`index.html`, `scene.js`, `cards.js`, `ring.js`, `choreo.js`) |
| Length | 18.2 s, 1920x1080, 30 fps; motion blur `render.sub` 3, grain 5 |
| Build | Three.js from `/harness/node_modules/three` through an importmap; `preserveDrawingBuffer: true`, exponential fog `#05070f`, ACES tone mapping, one UnrealBloomPass (about 0.8); cards are rounded planes with canvas textures; the ring a torus with a glow shader rim-lit `#2f7df6` to `#79b4ff`; final text is HTML over the canvas; MSAA off on SwiftShader for speed |
| Music | Lyria, 90 bpm brief (warm analog pads, slow heartbeat pulse, glassy plucks, a swell resolving around 11 s); gain -7 dB, duck ratio 3 |
| Voice | ElevenLabs `river` (cast: "a person speaking softly and closely into the microphone") |
| Render | `codead.yml` render, 16 Oct: 18.2 s, listening check no problems |
| Release | kinoforge `ads`: `unmissed-v2.mp4` (21.6 MB), `-sheet.jpg`, `-listen.json` |
| Cost | US$0.05999 (music US$0.04, voice US$0.01608, listening US$0.00392); cap US$0.60 |
| Verdict | "a little" (16 Oct) |

## Structure
Cues: calls 0.58 s, messages 1.90, leads 3.25 (each card type surges on its word), the gaps 4.57 (cards veer off; "the gaps."
in thin type), ring draws 6.25, ring forms 7.90 (chime), orbit 8.5 (quiet pops as cards are absorbed), ignite 10.57, logo 11.24,
tagline 13.24 and 14.65, end 18.2.

## Exact steps to re-make it
`node harness/dom-render.cjs ads/unmissed-v2 --stills 2,8,12 --stills-only --out out/unmissed-v2`; render with `codead.yml`
(`inputs[ad]=unmissed-v2`, `inputs[mode]=render`). Keep the WebGL scene light for SwiftShader (low polygon counts, one bloom).

## Sources of truth
`ads/unmissed-v2/TREATMENT.md`, `ad.json`, the scene files, `ledger.json`, `audio/casting.json`, `docs/LOG.md` (16 Oct).
