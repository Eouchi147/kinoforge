# Director job: The Great Emu War (`great-emu-war`), Kinetic, failed at the script stage (not rendered)

The first Kinetic film of the slate (`films/director/SLATE.md`, Kinetic number 1): Western Australia, November to December
1932, soldiers of the Royal Australian Artillery under Major Meredith with two Lewis guns sent to cull about 20,000 emus
damaging wheat farms in the Campion district, and the emus mostly win; told through the official reports, the numbers and the
newspapers. A director job on the `kinetic` line (`films/lib/kinetic/`), started on the free director on 22 Oct. It stopped
at the script stage when the free models' daily limit of the OpenRouter key (1,000 requests) was reached; it is held until
Salamis is done (`docs/LOG.md` 23 Oct). Nothing spent, nothing rendered. Style: `docs/manual/styles/kinetic.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/studio/great-emu-war/` |
| Brief | line `kinetic`, audience general (teens and adults), target 120 s, cap US$0.50, voice `chatterbox`, approved 22 Oct 15:00 UTC; notes: dry, true, a little absurd; the documents and numbers carry the humour; no graphic harm to animals, numbers only |
| Run | kinoforge `film.yml` run 39817396473; script stage failed (OverBudget: free-model daily limit, resets 00:00 UTC) |
| Spent | US$0 |
| Status | draft; next after Salamis |

## Files
`brief.json`, `seats.json`, `ledger.json`, `status.json` (no script yet).

## Exact steps (to make it)
Under decision 0013, set `cap_usd` (default 2.00) and the voice in `brief.json`, then
`gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/film.yml/dispatches -f ref=main -f 'inputs[job]=great-emu-war' -f 'inputs[from]=script'`.
The `kinetic` line renders 720x1280 and delivers 1080x1920 (`films/director/lines.json`); placement by `films/lib/battle_mix.py`.

## Sources of truth
`films/studio/great-emu-war/brief.json`, `status.json`, `films/director/README.md`, `films/director/lines.json`,
`films/director/SLATE.md`, `docs/LOG.md` (22 and 23 Oct).
