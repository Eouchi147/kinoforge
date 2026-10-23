# Ad: Unmissed, first code-built ad (`unmissed-01`), rejected

A 27.6 s, 16:9 brand ad for Unmissed built in code on 16 Oct 2026, following the offer of 15 Oct (a premium presence and an
AI front desk; phone answering live) in the site's night theme, with voice, music and interface sounds generated during the
render (the older single-step `codead.py` mode, no `audio` block). It went through four runs (v1 to v4) with an automatic
listening check after each. Sam's verdict on v4: **"really bad quality"**, the voice "not the greatest": one layout repeated
five times, slow drifting moves, nothing cut to the music, small dim visuals, a flat voice (`ads/UNMISSED_DIRECTION.md`).
That verdict produced the music-first pipeline and the five directions (`unmissed-v1` to `-v5`). Kept as a record.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `ads/unmissed-01/` (`index.html`, `ad.json`, `ledger.json`, `media/bread-oven.jpg`) |
| Length | 27.6 s (v4), 1920x1080, 30 fps, -14 LUFS |
| Voice | ElevenLabs `sarah` (v3 through OpenRouter), lines with start times in `ad.json` `vo`; v4 spaced the sign-off lines 1.5 to 2 s apart and spelled "A.I." for the voice |
| Music | Lyria, a 27 s sleek minimal electronic score at 100 bpm with a lift at 21 s; gain -10 dB |
| Sounds | synthesised in `codead.py` (ring, click, pop, whoosh, check, chime) |
| Runs | v1 US$0.054 (score buried, whoosh like hiss, last line sped up); v2 US$0.109 (guitar-led score off brief, bright pops, rushed sign-off); v3 US$0.056 ("An AI front desk" blurred into "and AI"); v4 delivered |
| Release | kinoforge `ads`: `unmissed-01.mp4` (4.5 MB), `-sheet.jpg`, `-listen.json` |
| Cost | US$0.22275 for the four runs (ledger) |
| Verdict | "really bad quality" (16 Oct) |

## Exact steps (single-step mode)
`gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/codead.yml/dispatches -f ref=main -f 'inputs[ad]=unmissed-01' -f 'inputs[mode]=render'`
(paid: voice and music are generated in the run). Do not reuse the direction; use the music-first route (`business-ads.md`).

## Lessons it left
Music first; several versions to choose from; never speed up a line; an automatic listening check (an audio model transcribes
and critiques the mix, `<id>-listen.json`) catches blurred words and buried scores; Lyria returns audio only when streamed.

## Sources of truth
`ads/unmissed-01/ad.json`, `index.html`, `ledger.json`, `harness/shots/codead.py`, `ads/UNMISSED_DIRECTION.md`, `docs/LOG.md` (16 Oct).
