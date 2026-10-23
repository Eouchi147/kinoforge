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

## Spend per video
Sam (23 Oct, 19:05): "I need a way to accurately see what was spent in detail per video." The studio's Spend app
(`#/spend`, also from Settings, Money) and every film's Spend tab (`#/library/<id>?tab=spend`; command bar `spend` and
`spend <film>`) show it. The data is `studio-web/public/data/spend.json`, built by `tools/spend.py` (deterministic like
`tools/catalog.py`: sorted, only `generated` varies; `--check` compares).

How each kind of cost is measured:
| Kind | Source | Basis |
| --- | --- | --- |
| Paid calls | every tracked `ledger.json` (films, ads, boards, pieces): seat, model, task, usd, seconds, ok, note | **measured** when the provider reported `usage.cost`; **estimated** when our code priced it (speech by the characters sent, a fallback price, note "estimated"); **not flagged** for 15 Oct piece and board lines whose code booked a list price when no cost came back and did not record which |
| Failed calls | the same ledgers (`ok: false`) | kept; flagged "failed but charged" when they cost money, "reply unreadable, booked at US$0" when a reply came back but could not be parsed (the provider may have charged a little: `harness/director/agents.py` books those at 0) |
| Director stages | `films/studio/<id>/status.json` | spend per stage (`spent`, or the difference of the running totals in older files), cap, last message |
| Footage boards of a film | `BOARDS_OF` in `tools/spend.py` (today: `unmissed-v4` uses boards `unmissed-night` and `unmissed-night-clips`) | as paid calls; `account.json` shown as a cross-check only (key usage lags by hours, and boards run in parallel share it) |
| The log | sentences of `docs/LOG.md` with US$ and the film's name (`ALIASES` in the tool) | never added when a ledger exists (cross-check); a figure shared by several films is shown, not split; counted only for a film with no ledger, named alone |
| GitHub runners | job times of every run id written down (`RUNS` in the tool, director `run_url`, `renders` lines in ledgers, and `<id>-run.json` records in release `kino-films`), stored in `data/spend/runs.json` | free (public repos); minutes rounded up per job as GitHub bills; **worth** at US$0.006 a minute (Linux 2-core x64 list price, GitHub Docs "Actions runner pricing", read 23 Oct 2026 from the docs source; Linux 4-core is US$0.012) |
| Mac lane | `data/spend/mac-lane-jobs.csv` (every job log on the drive), plus `renders` lines with `where: mac` | render time measured; film check stills on their own line; look boards and drive tests in their own entries, not on a film; electricity **estimated** at an assumed 30 W and an assumed CA$0.20 per kWh (both not verified: the Apple and OEB pages were not reachable when this was built; measure and update `RATES` in the tool) |
Work that is not a video in the library (style boards, the 15 Oct AI-footage pieces and showcase agent, the shared sound
bank run, Mac look boards) has its own entries and is in the studio total. Anything with no record says "not recorded".

**The rule from now on: every paid call or render writes one line into the film's own `ledger.json`.** Use
`films/lib/spend_log.py`: `call(folder, seat, model, task, usd, basis, seconds, ok, note)` for a paid call (`basis`
"measured" or "estimated"; `cost_from_usage(usage, price_in, price_out)` gives both from an OpenRouter reply) and
`render(folder, where='github', run_id=...)` or `render(folder, where='mac', seconds=..., job=...)` for a render. Lines
are stamped with the UTC minute (`at`); writes are locked and atomic. From the shell:
`python3 films/lib/spend_log.py call|render ...`. rc-render `films.yml` and `remux.yml` write `<film id>-run.json`
(every run of that film: run id, jobs, seconds, billable minutes, runner, start, end) to release `kino-films` at the end.
A failed render skips the join, so its run id must still be written in the log by hand.

How to update: `python3 tools/spend.py --fetch-runs` (asks GitHub, read only, for new run ids and release records, then
builds), or `python3 tools/spend.py` offline; add a new run id to `RUNS` when a render is logged without a record; add a
Mac lane export to the CSV when jobs ran on the drive; commit `spend.json` and `data/spend/runs.json`.

Traps: the director's `Ledger` (`harness/director/agents.py`) rewrites `ledger.json` with only cap, total, by_seat and
calls, so a `renders` list written before its last save is lost: write renders after the job's paid calls are done.
Speech has never returned a cost: every ElevenLabs line is an estimate from the characters sent.

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
