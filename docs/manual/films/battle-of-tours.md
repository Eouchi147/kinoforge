# Director job: The Battle of Tours (`battle-of-tours`), Battle Map, cancelled (not rendered)

The first real test job of the paid director pipeline (22 Oct 2026, 13:10 UTC): the Battle of Tours (Poitiers), October 732,
Charles Martel's Frankish infantry against the Umayyad army of Abd al-Rahman al-Ghafiqi, "the infantry that stood like a wall
of ice against cavalry charges all day, and the army that was gone by morning". Script and sound were done; it was cancelled
during the spec stage by Sam's no-spend order of 22 Oct 09:20 Toronto, after US$0.36. Not rendered. Tours stays on the slate
(`films/director/SLATE.md`, Battle Map number 6).

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/studio/battle-of-tours/` |
| Brief | line `battle-map`, kids 8 to 14, target 90 s, cap US$0.90, voice `elevenlabs/eleven-v4|brian`, approved 22 Oct 13:15 UTC |
| Run | kinoforge `film.yml` run 39784277702 |
| Stages | script done (US$0.18), sound done (Lyria score and ElevenLabs voice; duration 100.386 s), spec cancelled |
| Spent | US$0.36178 (head US$0.15089, deputy US$0.03017, music US$0.08, voice US$0.10072) |
| Status | cancelled; a draft for a later paid run |

## Files
`brief.json`, `script.json`, `ad.json`, `audio/` (`casting.json`, `music.mp3`, `music.json`, vo, `vo.json`, `mix.m4a`),
`cues.json`, `film.json`, `index.html`, `ledger.json`, `status.json`.

## Exact steps (to finish it)
Under decision 0013 (capped paid films): raise `cap_usd` to 2.00 if needed, then resume:
`gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/film.yml/dispatches -f ref=main -f 'inputs[job]=battle-of-tours' -f 'inputs[from]=spec'`
(`from=resume` skips stages whose outputs exist, so nothing is paid twice). Note: its sound uses a Lyria score from before the
free score engine; re-score with `python3 films/lib/score/remix.py films/studio/battle-of-tours` if the director's sound stage
is not re-run.

## Sources of truth
`films/studio/battle-of-tours/brief.json`, `status.json`, `ledger.json`, `films/director/README.md`, `docs/LOG.md` (22 Oct).
