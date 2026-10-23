# Ad: Unmissed, Night Shift (`unmissed-v4`), rejected

A 22.9 s, 16:9 brand ad built on AI footage: an invented neighbourhood restaurant after closing, rain on the windows, a phone
lights up on the counter ("You closed at nine. Your customers didn't."), the AI front desk answers and books, morning light,
the logo. Built on 16 Oct 2026 as version 4 of five directions. Sam's verdict: **"a big NO"** (`docs/SOUL.md` sections 3
and 5 list Night Shift, AI footage, among the rejected directions). Kept only as a record. Style: `docs/manual/styles/business-ads.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `ads/unmissed-v4/` (`media/ns-1` to `ns-4` as `.webm` clips and `.jpg` stills, `ns-5.jpg`) |
| Length | 22.9 s, 1920x1080, 30 fps; motion blur `render.sub` 4, grain 5 |
| Footage | AI, photoreal, no people: board `boards/unmissed-night` (5 stills, US$0.45) and `boards/unmissed-night-clips` (4 clips, US$1.60) |
| Build | the footage is drawn on a canvas, clips loaded as Blobs (the dev server has no Range requests, so plain video seeking snapped to 0); 2.39:1 letterbox, teal-amber grade, UI overlays as dark glass cards drawn in code |
| Music | Lyria, 72 bpm brief (felt piano, warm pads, a swell as morning comes); `music_offset` 5.55 s, gain -8 dB, duck ratio 3; every cut on a transient of the score |
| Voice | ElevenLabs `eric` (cast: "low, slow, close and warm") |
| Render | `codead.yml` render, 16 Oct |
| Release | kinoforge `ads`: `unmissed-v4.mp4` (29.3 MB), `-sheet.jpg`, `-listen.json` |
| Cost | ad US$0.06669 (music US$0.04, voice US$0.02436, listening US$0.00233) plus the boards US$2.05 |
| Verdict | "a big NO" (16 Oct) |

## Structure
Cuts: rain 2.55 s, phone 5.06 (card "Incoming call, 21:47" at 5.42), flip to "Answered by your AI front desk" 8.2, kitchen pass
10.06 ("Booked: catering for 40, Saturday 12:00" at 11.7), dawn dissolve 13.05 and the warm hit 13.39, the logo from 16.76,
tagline 19.2 and 20.98, AI label 20.3.

## Do not reuse
The direction is rejected. The technique of drawing clips on a canvas for deterministic seeking is the only reusable part.

## Sources of truth
`ads/unmissed-v4/TREATMENT.md`, `ad.json`, `index.html`, `ledger.json`, `boards/unmissed-night*/ledger.json`, `docs/LOG.md`
(16 Oct), `docs/SOUL.md` sections 3 and 5.
