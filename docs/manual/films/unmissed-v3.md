# Ad: Unmissed, The Call (`unmissed-v3`)

A 26.8 s, 16:9 brand ad with no narrator: you hear a real-sounding late-night call between a caller and the AI front desk of
an invented restaurant (Saffron Hearth Kitchen), read as huge kinetic captions word by word exactly on time; a booking card
slams in on "Done."; after the hang-up the music opens up and three supers land on the beat ("Answered at 9:47 PM.", "Booked
on the call.", "In your business's name."). It proves the product instead of describing it. Built on 16 Oct 2026 as version 3
of five directions. Sam's verdict: loved, but the voice "sounds too fake". Style: `docs/manual/styles/business-ads.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `ads/unmissed-v3/` |
| Length | 26.8 s, 1920x1080, 30 fps; motion blur `render.sub` 2, grain 5 |
| Dialogue | ElevenLabs v3: AI `matilda`, caller `chris` (tags `[casual]`, `[relieved]`); 5 lines in `ad.json` `prep.dialogue`; word times from Whisper aligned on the real audio envelope; per-line voice level at 60 fps (`levels`) drives the speaker orb |
| Music | Lyria, 100 bpm brief (very sparse for the first 15 s, then it opens up); `audio/music_late.mp3` = the score delayed 7.2 s (3 bars) so it opens on the hang-up; gain -6 dB, duck ratio 6 |
| Render | `codead.yml` render, 16 Oct; listening check: no problems |
| Release | kinoforge `ads`: `unmissed-v3.mp4` (235 MB), `-sheet.jpg`, `-listen.json` |
| Cost | US$0.06058 (music US$0.04, voice US$0.0168, listening US$0.00378); cap US$0.60 |
| Verdict | loved the ad; the voice too fake (16 Oct). Open question for Sam: must the AI receptionist sound like Unmissed's live phone agent? |

## Structure
Two rings (0.43, 1.03 s), the answer click (1.33), five lines from 1.63 s; "Done." 17.81 s with the booking card (calendar
tick: "Saturday 12:00, catering for 40, booked") and a check at 18.05; hang-up 21.43 s = the music drop; supers at 21.43, 22.01,
23.22; ring draws 24.1, logo 24.40, tagline 25.01, "Made with AI" 25.61. Captions: Instrument Sans 650, 110 to 140 px, the
spoken word full white, spoken words ink2, AI words tinted `#79b4ff`; the speaker indicator is the ring orb (AI) or a soft white
circle with initials (caller); top-left chip "Saffron Hearth Kitchen", "AI front desk" and a live timer; bottom-left "Demo with
an invented business".

## Exact steps to re-make it
`node harness/dom-render.cjs ads/unmissed-v3 --stills 3,12,22 --stills-only --out out/unmissed-v3`; render with `codead.yml`
(`inputs[ad]=unmissed-v3`, `inputs[mode]=render`). A new voice means a new `prep` (paid; Sam's go).

## Known trap (this ad)
Dialogue recognition first failed (faster-whisper against a new PyAV); fixed by decoding with librosa.

## Weak spots
The synthetic voices (the reason the ad cannot be used yet); the uncapped master bitrate (235 MB for 26.8 s).

## Sources of truth
`ads/unmissed-v3/TREATMENT.md`, `ad.json` (captions, cues, audio, sfx, levels), `index.html`, `ledger.json`,
`audio/dialogue.json`, `docs/LOG.md` (16 Oct), `docs/STATUS.md` (Waiting on Sam).
