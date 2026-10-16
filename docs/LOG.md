# Log

Newest first. One line per change or decision, with the date (UTC). Whoever changes the project adds a line here.

## 16 Oct 2026
- Sam: Unmissed ad v4 "really bad quality", voice not great; wants dynamic, modern, premium, directed and orchestrated, and at least 5 different versions. Response: music-first pipeline (`prep.py`: Lyria score + beat map, voice casting by an audio model, Whisper word timings), motion blur (`dom-render --sub`), film grain, WebGL in the renderer, `codead.yml` modes prep/render with several ads per run. Five versions specced: `ads/unmissed-v1` Manifesto, `v2` The Catch (3D), `v3` The Call (dialogue + kinetic captions), `v4` Night Shift (AI footage, board `unmissed-night`), `v5` Bento (day theme).
- `unmissed-01` v4 delivered to Sam (27.6 s, 16:9, -14 LUFS). Listening check (Gemini 3.7 Flash): no problems. Total for the four runs: $0.223.
- `unmissed-01` v3 ($0.056): the listening check now finds the score on-brief, sounds pleasant, mix excellent; one problem: "An AI front desk" blurred into "and AI". v4: sign-off lines spaced 1.5 to 2 s apart (no speed-up), "A.I." spelled out for the voice, ad 27.6 s.
- `unmissed-01` v2 ($0.109 incl. the listening check): the check (MiMo v2.6 Pro) heard a clear voice, a good balance, but a guitar-led score off-brief, bright pops and chimes, and a rushed sign-off. v3: score re-briefed (no guitar, synth keynote), softer interface sounds, the sign-off split into three timed lines.
- `unmissed-01` first full run ($0.054): picture, voice and Lyria music all worked; loudness -14 LUFS. Fixes for v2: score was buried (gain -15 to -10 dB, gentler ducking), whoosh sounded like hiss (darker, quieter), last line no longer sped up (end card 1 s longer). New automatic listening check: an audio model transcribes and critiques the mix (`<id>-listen.json`).
- `codead.yml` was not registered by GitHub until a push touched the file itself; noted in WORKFLOWS. First real run of `unmissed-01` started.
- Handover docs added: `AGENTS.md` (read first), `CLAUDE.md`, `docs/WORKFLOWS.md`, `docs/STATUS.md`, this log. Rule from Sam: every change updates STATUS and LOG.
- Unmissed ad v1 built in code (`ads/unmissed-01`), following the new Unmissed offer of 15 Oct (Presence, AI Front Desk, Complete; phone answering live) and the site's night theme. New pipeline `codead.yml` / `harness/shots/codead.py`: render, ElevenLabs voice, Lyria score, synthesised interface sounds, sidechain ducking, -14 LUFS.
- `factory.music()` rewritten: OpenRouter returns audio output only when streamed; earlier music calls had always failed.
- Decision (Claude, at Sam's request "you decide"): Hero Close-ups kept as short food inserts. Documentary dropped (Sam).

## 15 Oct 2026
- Style board round 2 ($1.47): photo cut-outs (bread, tea glass) for Type in Motion v2; two 6 s Freeze Frame clips (torn bread good, spice burst warps).
- Sam's verdicts on round 1: Screen Story "amazing", Type in Motion "great" but the drawn bread looked fake, Freeze Frame wanted in motion, Flash Editorial "good", Documentary no.
- Style board round 1 (about $1.65; half lost to a script crash, fixed by saving every still at once): six looks for one invented restaurant.
- Sam rejected the five ad tests (Smart Mount, Unmissed stills, restaurant, detailing, barber) as "AI slop": every piece used one stylised cartoon-3D direction. All spending stopped. New rule: style board first, Sam picks, then video. Six business directions written; Voltage retired for business ads.
- Unmissed answers applied (`harness/shots/policies/unmissed.md`): claims, industries (restaurants, auto detailing, barbers; no clinics), modest wardrobe, no dashes, AI label. Smart Mount cleared for public use. Private storage for client material parked.
- Focus changed to ads for money (Sam approved the four-step path). Shot factory (`piece.yml`) built: treatment, keyframes, Veo clips, voice, edit, end card in code.
- Showcase scene agent failed (replies truncated, about $2.50); showcase frozen.

## 14 Oct 2026
- Multi-agent director built (head, deputy, crew seats filled live from OpenRouter; capped loops and spend); web studio on Vercel.
- Narration lane on OmniVoice with take checker and placement; pilots "The Dragon Who Couldn't Fly" and "Why the Moon Changes Shape" narrated, waiting for Sam's approval.

## 13 Oct 2026
- Repo created by Sam. Fourteen anthology style prototypes (`proto/`) rendered on GitHub runners (`render.yml`, `gallery` release).
