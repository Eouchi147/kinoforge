# Director job: The Battle of Salamis (`salamis`), Battle Map, in progress (not rendered)

The first film of the slate (`films/director/SLATE.md`, Battle Map number 1): September 480 BC, Themistocles lures Xerxes's
much larger fleet into the narrow strait between Salamis and the mainland, where the Persian ships jam and cannot turn. It
is a director job (`films/director/`, no hand coding), started on the free director on 22 Oct under the then no-spend rule.
Script and sound are done; the picture spec stage failed (free models too weak, then the daily free limit, then the old
US$0.50 cap with no credit). Nothing is rendered. Next: re-run as the first paid film once Sam adds credit, with the brief
raised to a cap of US$2.00 and the ElevenLabs voice, `from=script` (`docs/LOG.md` 23 Oct). Process: `docs/PLAYBOOKS/run-the-free-director.md`,
`films/director/README.md`; style `docs/manual/styles/battle-map.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/studio/salamis/` |
| Brief | `brief.json`: line `battle-map`, audience kids 8 to 14, target 150 s, cap US$0.50, voice `chatterbox`, approved 22 Oct 15:00 UTC; angle "a trick and a narrow strait: the giant fleet that could not turn"; notes: show twice the moment the Persian ships jam; Xerxes watching from his throne is the glint of dark humour; kid-safe, losses as numbers and fading ships, no drowning |
| Script | done 22 Oct (free Nemotron 3 Ultra, about 24 min): `script.json` |
| Sound | done 22 Oct: Chatterbox, 15 lines in 15.5 min; the free score (`ancient_med`, D dorian; mix -14.28 LUFS, voice 16.7 dB over); duration 119.16 s |
| Spec | failed: the first draft had 19 check errors and repairs could not run (the free key hit 1,000 requests a day); resumed 23 Oct 00:21 UTC (run 39877596998) and stopped at the spec stage before any call by its US$0.50 cap with no credit |
| Spent | US$0 |
| Status | in progress; waits on credit (`docs/STATUS.md`) |

## Files
`brief.json`, `script.json`, `ad.json`, `audio/` (vo, `vo.json`, `music.mp3` and `music.json` (the code pad), `mix_lyria.m4a`,
`score_plan.json`, `score.json`, `mix.m4a`), `cues.json`, `film.json`, `index.html`, `seats.json`, `ledger.json`, `status.json`.

## Exact steps (to finish it)
1. Sam adds credit (`films/director/README.md`, "Credit"); agents never touch keys.
2. Edit `brief.json`: `cap_usd` 2.00, `voice` `elevenlabs/eleven-v4|brian`, a new `approved_at` only if a fresh start is wanted.
3. Resume from the script (the money rule wants the paid writer and checker):
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/film.yml/dispatches -f ref=main -f 'inputs[job]=salamis' -f 'inputs[from]=script'`.
4. Watch `films/studio/salamis/status.json`; gates stop it before any render if it cannot pass; the film lands in kinoforge
   release `films` (`films-render.yml`).

## Known traps
Free models allow about 1,000 requests a day per key and few capable ones are live: one director job at a time; the picture
spec is the weak stage of the free director (`docs/LESSONS.md`).

## Sources of truth
`films/studio/salamis/brief.json`, `status.json`, `ledger.json`, `audio/score.json`, `films/director/README.md`, `films/director/SLATE.md`,
`docs/LOG.md` (22 and 23 Oct), `docs/STATUS.md`.
