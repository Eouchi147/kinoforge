# Style: AI-footage pieces (the shot factory), paused

The shot factory (`harness/shots/factory.py`, workflow `piece.yml`) turns a brief into an ad made of AI-generated video:
a head director model writes a treatment, reference images and keyframes are generated and scored, a video model animates
each keyframe, then voice, music, the edit and an end card set in code are added. Five pieces were made on 15 Oct 2026
(`pieces/`), all in one stylised cartoon-3D direction ("voltage") except the Unmissed brand piece (classic, keyframes only).
Sam rejected them the same day as "AI slop": one look for everything made everything the same. All spending stopped; the
rule "style board first, Sam picks, then video" (`docs/decisions/0008`) came from it. The lane is **paused**; any paid image
or video generation still needs Sam's go per job (`docs/decisions/0013`). This page records the recipe so it can be judged
or reused for inserts, not as a default.

## Inputs
- `pieces/<id>/brief.json`: `type` (ad), `tier` (draft, standard, premium, kling), `policy` (unmissed), `aspect` (16:9),
  `direction` (a file in `harness/shots/directions/`), `duration` (20 or 30 s), `brand`, `idea`, `end_card`, `end_card_s`,
  `notes` (what must not appear: real people, alcohol or pork for a halal-friendly client, text), `cap`, labels
  (`corner_label`, `concept_label`: "Concept by Unmissed, AI-assisted"), controls `stop_after` (e.g. `"keyframes"`),
  `redo_keyframes`, `redo_clips`, `accept_keyframes`, `clip_audio`.
- `pieces/BUDGET.json`: the whole test budget (US$50); every call checks it and the piece's cap first.
- `OPENROUTER_API_KEY` as a GitHub secret (Sam's; agents never see it).

## Tiers (`factory.py` `TIERS`)
| Tier | Video model | Resolution | Keyframe model | Cap |
| --- | --- | --- | --- | --- |
| draft | google/veo-3.1-lite | 720p | bytedance-seed/seedream-5-0-pro | US$4 |
| standard | google/veo-3.1-fast | 1080p | bytedance-seed/seedream-5-0-pro | US$10 |
| premium | google/veo-3.1 | 1080p | google/gemini-3-pro-image | US$12 |
| kling | kwaivgi/kling-v3.0-pro | 720p | bytedance-seed/seedream-5-0-pro | US$9 |

## Exact steps (as built)
1. Write `pieces/<id>/brief.json`; always start with `"stop_after": "keyframes"` so stills are judged before any video money.
2. Dispatch `piece.yml` (input `piece` = the folder name):
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/piece.yml/dispatches -f ref=main -f 'inputs[piece]=<id>'`.
3. Stages: 1 treatment (look, reference sheet, shots each a keyframe and a motion, voice-over, music, end card); 2 one
   reference image per product, character or location; 3 one keyframe per shot, scored by an eyes model, a weak one redone
   once; 4 clips from the keyframes as first frames, 3 frames of each checked, a broken clip redone once; 5 ElevenLabs voice,
   Lyria score, the clips' ambience under it, ducked, -14 LUFS; 6 edit with one grade and an end card typeset in code; 7 the
   head director reviews the contact sheet.
4. Output in release `pieces`: `<id>.mp4`, `<id>-9x16.mp4`, `-keyframes.jpg`, `-contact.jpg`, `-work.tgz`, logs;
   `pieces/<id>/*.json` (treatment, ledger, report) committed.

## The five pieces (15 Oct 2026)
| Piece | Tier, direction | Outputs in release `pieces` | Spent (ledger) |
| --- | --- | --- | --- |
| `smartmount-01` | draft, voltage | keyframes, work archive, logs (no final mp4) | US$5.74 |
| `unmissed-brand-01` | standard, classic, `stop_after: keyframes` | keyframes only | US$2.35 |
| `concept-barber-01` | standard, voltage | keyframes, work archive (no final mp4) | US$4.98 |
| `concept-detailing-01` | standard, voltage | `concept-detailing-01.mp4`, `-9x16.mp4`, contact, keyframes | US$7.61 |
| `concept-restaurant-01` | standard, voltage | `concept-restaurant-01.mp4`, `-9x16.mp4`, contact, keyframes | US$8.26 |
Verdict (Sam, 15 Oct): "AI slop" for all five. Voltage is retired for business ads.

## Alternatives (use these first)
- Ads built in code (`business-ads.md`), the Cutaway trade ad, social templates: exact words, no AI glitches, free pictures.
- AI only as inserts where it is strong: Hero Close-ups (materials: crust, char, steam, liquid, chrome), Flash Editorial
  stills, Freeze Frame (one solid subject only), after a style board (`board.yml`: about US$0.09 a Seedream still,
  US$0.14 a Gemini still, US$0.60 a 6 s Veo 3.1 Fast clip).

## Checks before showing Sam
Reject warping, melting, extra fingers, unreadable or wrong text, claims outside the policy, anything that could read as
alcohol or pork for a halal-friendly client; AI label on screen and in the captions.

## Known traps
- The automatic "score and redo" loop doubled the cost when the look itself was the problem: fix the look, not the clip;
  prefer `stop_after` and a human look over loops.
- Video models warp crowds of small particles and people's hands; they hold one solid object well.
- Square stills fed to a 16:9 video model get pillarboxed: crop to the target aspect first.
- Save every paid output to disk the moment it exists (a crash once lost paid stills).
- Text, logos and numbers are never drawn by an image or video model; prompts say "no text, no logos" (gate `prompts`).

## Sources of truth
`harness/shots/factory.py`, `.github/workflows/piece.yml`, `pieces/*/brief.json`, `ledger.json`, `report.json`,
`harness/shots/directions/`, `docs/WORKFLOWS.md` (piece.yml, board.yml), `docs/SOUL.md` sections 3 and 5,
`docs/decisions/0008-style-board-first.md`, `docs/LOG.md` (15 Oct).
