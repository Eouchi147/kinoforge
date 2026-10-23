# Engine demo: The Ship Called Care, re-told by the Kinetic engine (`kinetic-demo`), draft (not rendered)

The demonstration film of the spec-driven Kinetic engine (`films/lib/kinetic/`): the Dark Corners Zong episode ("The Ship
Called Care", 179.4 s, 9:16) re-told from a `spec.js` alone, with no hand-written scenes, on the original episode's mix and cue
sheet. It uses every card type except `drawer` and is the example the director's `kinetic` line and `films/lib/kinetic/SPEC.md`
point to. Words and objects only: no bodies, no water, no ship drawn. No render of it is recorded. Style:
`docs/manual/styles/kinetic.md`.

## At a glance
| Field | Value |
| --- | --- |
| Folder | `films/studio/kinetic-demo/` |
| Files | `index.html` (`startKinetic`), `spec.js` (the cards), `cues.json` and `audio/mix.m4a` (the Zong episode's original), `film.json` |
| Length | 179.4 s, 720x1280 render, 1080x1920 delivery, 24 fps |
| Colour script | dark card and cream type for the narration; cold paper for records, the insurance and the court; one warm parchment page (the price) |
| Accent | ONE accent mark: "CARE." in the last line (`#cf3b2e`) |
| Render | not recorded |
| Cost | US$0 |

## Exact steps
1. Stills and checks: `node films/lib/kinetic/tools/stills.cjs films/studio/kinetic-demo --cards --out out/kinetic-demo`
   (`--sheet` for a contact sheet); it prints the spec's errors and warnings.
2. Render if wanted: rc-render `films.yml` (`inputs[film]=films/studio/kinetic-demo`, 12 parts) or kinoforge `films-render.yml`.

## To make a new one like it
Copy `index.html` and `film.json`, write `spec.js` card by card against the new `cues.json` (`docs/manual/styles/kinetic.md`).

## Sources of truth
`films/studio/kinetic-demo/spec.js`, `film.json`, `films/lib/kinetic/SPEC.md`, `films/director/lines.json`, git commit 782e86c.
