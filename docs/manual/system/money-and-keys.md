# Money and keys (decision 0013)

The money rule since 22 Oct 2026, 20:50 Toronto (Sam: "cap the budget per film but I need good results every time I
pay"): paid models are allowed inside a hard cap per film, booked before every call; the best tool per stage, free tools
wherever they are as good; quality gates before each paid stage; a film that cannot pass inside its cap stops and is
never rendered. Paid image or video generation (style boards, AI footage) still needs Sam's go per job. Agents never
handle API keys. Decision record: `docs/decisions/0013-capped-paid-films.md` (supersedes 0001, amends 0005).

## Inputs
- The film's brief with `cap_usd` (director films) or the folder's own cap (`ad.json` `cap_usd`, `batch.json`
  `music.cap_usd`, `board.json` `cap_usd`, `pieces/<id>/brief.json` cap).
- Credit on the OpenRouter keys (Sam adds it; see below).

## What costs money and what does not
| Item | Cost | Where the cap lives |
| --- | --- | --- |
| Rendering on GitHub runners (rc-render, kinoforge) | US$0 | none needed (runner minutes are the limit, see `architecture.md`) |
| Rendering on the Mac lane | US$0 | none |
| Free procedural score (`films/lib/score`), Kokoro and Chatterbox narration on runners, the sound bank, Commons music | US$0 | none |
| Director film, paid mode (writer Opus, checker Gemini, coder Opus, repairs Sonnet, eyes Gemini, lessons Haiku, ElevenLabs narration) | usual US$0.90 to 1.50 per 2.5 min film | `brief.cap_usd`, default 2.00, 0.50 to 5.00 (`films/director/config.json`) |
| Director chat in the web studio | about US$0.02 to 0.05 a turn on Opus; falls back to free models when the studio key is dry | studio key limit |
| Code ad prep (Lyria score, voice casting, dialogue) | about US$0.05 to 0.07 per ad; render about US$0.01 | `ad.json` `cap_usd` |
| Social batch music (Lyria, optional) | about US$0.04 to 0.08 per batch | `batch.json` `music.cap_usd` |
| Style board stills (`board.yml`) | about US$0.09 per Seedream still, US$0.14 per Gemini still, US$0.60 per 6 s Veo 3.1 Fast clip | `board.json` `cap_usd`; Sam's go per job |
| AI-footage piece (`piece.yml`) | tiers: draft cap US$4, standard US$10, premium US$12 | brief cap; Sam's go per job |

## Exact steps (before anything that costs money)
1. Is it free? Rendering, the score engine, free narration, the sound bank: go ahead.
2. Director film: set `cap_usd` in the brief (default 2.00). The pipeline books every call's worst case against it and
   stops before passing it. Nothing else to do.
3. Paid image or video generation (board, piece): ask Sam first, one short question with the cost and your
   recommendation. Never loop paid renders automatically (0008: fix the look, not the clip).
4. After the run, read the cost from the ledger (`films/studio/<id>/ledger.json`, `ads/<id>/ledger.json`,
   `boards/<id>/ledger.json`, `social/batches/<client>/<batch>/ledger.json`) and write it in `docs/LOG.md` ("US$0.42").
5. Out of credit (HTTP 402 in `status.json` or a log): tell Sam in one line; he adds credit; resume the job
   (`film.yml` with `from=resume`). Never ask for a key, never paste one anywhere.

## Keys (Sam owns them; agents never see them)
| Key | Where it lives | Used by |
| --- | --- | --- |
| OpenRouter build key | GitHub secret `OPENROUTER_API_KEY` on `Eouchi147/kinoforge` | `film.yml`, `codead.yml`, `social.yml` music, `board.yml`, `piece.yml` |
| OpenRouter studio key | Vercel env `OPENROUTER_API_KEY` (project `kinoforge-studio`) | The director chat in the web studio |
| GitHub token for the studio | Vercel env `GITHUB_TOKEN` | `/api/build` commits the brief; library reads |
The `secrets` gate fails on any key in a tracked file.

## What Sam must do for credit (from `films/director/README.md`, "Credit")
On openrouter.ai, Settings, Credits and Keys: add about US$25 account credit; raise the build key's limit to US$20; raise
the studio key's limit by US$5. As of 23 Oct 2026 no paid director job has been dispatched (STATUS "Waiting on Sam").

## Money so far (from the record)
Sum of all committed ledgers on 16 Oct: US$36.29 (handover). Since then: boards site-samples v1 (US$0.81), v2 (US$2.34),
v3 food and industries (dispatched 17 Oct, caps US$3.00 each; spend not recorded in the log), battle narration and
scores about US$0.96 and about US$0.93 (21 to 22 Oct), the cancelled battle-of-tours job US$0.36. Everything from 22 Oct
09:20 onwards logged US$0. Read the ledgers for exact figures.

## Alternatives
- Free mode for the director (`free_only: true` in `films/director/config.json` or `KF_FREE_ONLY=1`): US$0, fine for
  script and sound, weak for the picture spec (22 Oct). Use for tests.
- Lyria music for a director film only when the brief says `"music": "lyria"` (about US$0.08); default is the free score.

## Checks before showing Sam
The delivery message states the cost against the cap ("US$1.12 of US$2.00") or "US$0".

## Known traps
- OpenRouter key `usage` lags by hours; the per-call `usage.cost` in the ledgers is the reliable figure.
- An automatic "score and redo" loop doubled paid video cost on 15 Oct.
- Save every paid output to disk and upload it the moment it exists (a crash once lost paid stills).
- Free models allow about 1,000 requests a day per key (reset 00:00 UTC): one free director job at a time.

## Sources of truth
`docs/decisions/0013-capped-paid-films.md`, `0008-style-board-first.md`, `films/director/config.json`,
`films/director/README.md` (Money, Credit), `docs/WORKFLOWS.md` (costs per workflow), `docs/STATUS.md` (Money).
