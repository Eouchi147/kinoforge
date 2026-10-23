# Ad: Unmissed, Manifesto (`unmissed-v1`)

A 16 s, 16:9 kinetic-typography brand ad for Unmissed, music led: the problem in four cold lines ("9:47 PM", "The phone
rings.", "Nobody picks up.", "They call the next place."), a white flash and "Not anymore." on the drop, then the answer fired
one word per beat ("Answered.", "Booked.", "Texted back.", "Followed up.", "Review asked.", "Day and night.", "In your name.")
and the end card. Built music first on 16 Oct 2026 as version 1 of five directions. Sam's verdict: "a little".
Style: `docs/manual/styles/business-ads.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `ads/unmissed-v1/` |
| Length | 16.0 s, 1920x1080, 30 fps; motion blur `render.sub` 4, grain 5 |
| Look | night palette; Instrument Sans 700 at width 75 % for the slams (300 to 420 px, tracking -0.04 em), JetBrains Mono labels, full-frame `#2f7df6` fields, one or two white flash frames on the drop |
| Music | Lyria, 124 bpm brief (tense filtered first 4 s, a hard drop around 4 s, a final hit around 14 s); `music_offset` 13.4 s, gain -4 dB, duck ratio 2 |
| Voice | ElevenLabs `roger` (cast: "deepest, warmest, most naturally confident"): "Unmissed." on the logo slam, then the tagline |
| Render | `codead.yml` render, 16 Oct: 16 s, -13.2 LUFS, 72 Mbps because grain is incompressible (codead then capped the bitrate) |
| Release | kinoforge `ads`: `unmissed-v1.mp4` (145 MB), `-sheet.jpg`, `-listen.json` |
| Cost | US$0.04911 (music US$0.04, voice US$0.00696, listening US$0.00215); cap US$0.60 |
| Verdict | "a little" (16 Oct) |

## Structure
Cue times (`ad.json` `cues`): clock 0.08 s, rings 1.54, nobody 2.99, next 4.44, whip 5.41, drop 5.89, answered 6.37, booked 6.86,
texted 7.34, followed 7.83, review 8.31, day 8.79, night 9.28, name 9.76, ring draw 10.25, logo 10.73, tagline 12.07 and 13.96,
end 16.0. Each answer word has its own composition (black, blue, white fields) and a tiny proof glyph drawn in code. Sound
effects: ticks on the clock, rings, a riser into the drop, a whoosh on the whip, impacts on the drop and the logo.

## Exact steps to re-make it
`node harness/dom-render.cjs ads/unmissed-v1 --stills 2,6,12 --stills-only --out out/unmissed-v1`; render with `codead.yml`
(`inputs[ad]=unmissed-v1`, `inputs[mode]=render`).

## Weak spots
The bitrate of the master; Sam's lukewarm verdict on the direction (keep it as a reference for kinetic type, not a template).

## Sources of truth
`ads/unmissed-v1/TREATMENT.md`, `ad.json`, `index.html`, `ledger.json`, `audio/casting.json`, `docs/LOG.md` (16 Oct).
