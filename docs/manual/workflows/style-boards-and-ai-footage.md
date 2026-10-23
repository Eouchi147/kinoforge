# Style boards and AI footage (kinoforge `board.yml`, `piece.yml`) (paid, Sam's go per job)

Two paid lanes that generate images or video with AI models through OpenRouter. `board.yml` makes stills per look (and
optional cut-outs and short image-to-video tests) so Sam picks a look before any video money is spent; used for the
Unmissed site sample photos (`site-samples-v1`, `-v2`, `-v3-food`, `-v3-industries`). `piece.yml` is the shot factory: a
treatment, keyframes, clips, voice, music, edit, end card set in code, a 9:16 cut. Both need Sam's explicit go per job
(decisions 0008 and 0013). Free style boards (code or Blender stills, like the Cutaway look board) are preferred.

## Inputs
- `board.yml`: `board` = folder under `boards/` with `board.json`: `cap_usd`, `aspect`, `frames` (id, model, prompt,
  optional aspect and `cutout`), optional `clips` (id, from, prompt, seconds, model).
- `piece.yml`: `piece` = folder under `pieces/` with `brief.json` (type, tier, policy, aspect, direction, duration, brand,
  idea, end_card, notes, cap; controls `stop_after`, `redo_keyframes`, `redo_clips`, `accept_keyframes`, `clip_audio`).

## Exact steps
1. Ask Sam: what, how many, the cap, the expected cost. Wait for his go.
2. Write the folder; every prompt says "no text, no logos" (gate `prompts`); no people for business samples where the
   record says so; commit, push.
3. Dispatch: `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/board.yml/dispatches -f ref=main -f 'inputs[board]=<id>'`
   (or `piece.yml` with `inputs[piece]=<id>`; use `stop_after: "keyframes"` to look before paying for video).
4. Download from release `boards` (`<board>-<frame>.jpg`, `.cut.png`, `.mp4`) or `pieces`; `ledger.json` and
   `account.json` are committed. Review every still; discard any that shows poor workmanship.
5. Log the spend (the account figure and the ledger) in `docs/LOG.md`.

## Cost
About US$0.09 per Seedream still, US$0.14 per Gemini still, US$0.60 per 6 s Veo 3.1 Fast clip. Pieces: draft (Veo 3.1
Lite 720p, cap US$4), standard (Veo 3.1 Fast 1080p, cap US$10), premium (Veo 3.1, cap US$12).

## Alternatives
Free boards: Blender or code stills (`check-stills.md`, the Cutaway look board, the social style board rendered locally).

## Checks before showing Sam
Samples are marked Sample and AI-generated where shown; never presented as a client's work.

## Known traps
- 15 Oct: five AI-footage ads were "AI slop"; the automatic clip re-render loop doubled costs; `piece.yml` had 5 failed
  and 7 cancelled runs of 19. Prefer `stop_after` and a human look over loops.
- Video models warp crowds, small particles and hands; they hold one solid object well.
- Square stills fed to a 16:9 video model get pillarboxed: crop first. Seedream needs `modalities: ["image"]`.
- Save every paid output the moment it exists.

## Sources of truth
`.github/workflows/board.yml`, `piece.yml`, `harness/shots/board.py`, `harness/shots/factory.py`, `docs/WORKFLOWS.md`,
`docs/decisions/0008-style-board-first.md`, `docs/SOUL.md` section 5 (rejected).
