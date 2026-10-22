# Cutaway productions (Sam, 22 Oct 2026: "build 1,2,3,4")

The Cutaway style (`films/styles/cutaway/`, Blender kit) is a floating block of land cut out of the world: a living
landscape on top, clean strata on the cut faces, water as a clear volume you can see into. Its power is showing what is
hidden under the surface. Four productions, all with free tools only, all following `films/director/CRAFT.md`.
Sam's three reference pictures are stock images: they are references only, never used in any output.

| # | Production | Folder | Format | Sound |
| --- | --- | --- | --- | --- |
| 1 | Trade ad: drainage and landscaping (sample business, marked Sample) | `ads/drainage/` | 15 s, 9:16 and 16:9 | music only (free score engine), words on screen |
| 2 | Explainer series "Under the Surface", film 1: Why Venice Sinks | `venice/` | about 2.5 min, 16:9 (and a 9:16 cut) | free narration (director's `voice_free.py`), free score |
| 3 | Battle set piece: the mud at Agincourt (insert for the Battle Map film) | `agincourt-mud/` | two inserts, 16:9, on the film's own cue times | the Agincourt film's own mix |
| 4 | Social loop: four seasons over one block | `loops/seasons/` | 12 s seamless loop, 9:16 | soft ambience and a short loopable score |

## Rules for all four
- Words, logos and numbers are set in code (never painted by a model). No em or en dashes, no "..." on screen.
- The ad is for an invented sample business, marked "Sample" on screen; no real client, no claims about Unmissed.
- Every cut and every move has a written job (CRAFT.md sections 1 to 4); real time, eased moves, living worlds.
- Renders on GitHub runners (rc-render `films.yml`; check stills with rc-render `stills.yml`, release `stills`).
- Nothing is published or sent anywhere before Sam has watched it.
