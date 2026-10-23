# The anthology prototypes (`proto/`): where the house styles came from

On 13 and 14 Oct 2026 the studio was started with a set of short style prototypes, each a 6 to 12 s scene that proves one
look and one piece of film grammar (a lane, a logline, an emotion arc, a shot list equal to the code, a QC log). They were
rendered on GitHub runners by `render.yml` into the release `gallery` (each `<id>.mp4` plus `<id>.contact.jpg`). Four of
them became house styles: p03 Lantern Road, p10 Clay, p11 Kinetic, p12 Terrain (Battle Map). The others stay as a library
of proven techniques. They are frozen reference work: do not edit them; copy what you need into a film folder.

## The prototypes
| Id | Name, length, frame | Engine | What it proves | Became |
| --- | --- | --- | --- | --- |
| p01-static | Static, 10 s, 1280x720 with a 4:3 CRT picture | web (harness kit `vhs` mode) | analog-horror finish; a scare built on a continuity change, glitch timing shared by picture and sound | technique (Dark Corners horror) |
| p02-ink-ember | Ink and Ember, 10 s, 16:9 | web, Canvas 2D motion comic through the kit grade | comic page grammar, 2.5D lens language, one accent colour bound to one object | technique |
| p03-lantern-road | The Lantern Road, 12 s, 16:9 | web, Three.js multiplane | procedural painted 2.5D multiplane with true depths, lanterns that relight the paint, colour script by light, planted walk | **Lantern Road** (`lantern-road.md`) |
| p04-witness | Witness, 6 s, 16:9 | Blender Cycles | path-traced practicals, thin volume, optical rack focus in diopters | technique |
| p05-relic | Relic, 10 s, 2.39:1 | web | trailer phase map in miniature, volumetric light, one accent colour | technique |
| p06-cel | Cel, 10 s, 16:9 | web, Three.js toon | 4-step toon ramp with designed shadow colours, ink outlines, animation on twos with IK-planted feet | technique |
| p07-ash-ascent | Ash Ascent, 6 s, 16:9 | Blender Cycles | displaced procedural terrain, a volumetric cloud sea inside the CI budget, a physical sky whose sun motivates the light | technique |
| p08-two-chairs | Two Chairs, 12 s, 16:9 | web, Canvas 2D rig | dialogue comedy: hierarchical 2D rig driven by Kokoro TTS and Rhubarb visemes, one cue file for picture and sound | technique |
| p09-paper-kingdom | Paper Kingdom, 10 s, 16:9 | web, Canvas 2D | cut-paper shadow theatre with jointed puppets and a physically consistent lightbox | technique (p16) |
| p10-clay | Clay, 6 s, 16:9 | Blender Cycles, on twos | stop-motion grammar: poses on twos, hand jitter, squash and stretch, replacement smear, deadpan timing | **Clay** (`clay.md`) |
| p11-kinetic | Kinetic, 8 s, 9:16 | web, Canvas 2D through the kit | text-only hook directed like film; 9:16 safe zone verified on every frame (`?audit=all`) | **Kinetic** (`kinetic.md`) |
| p12-terrain | Terrain, 10 s, 16:9 | web, Three.js | a relief that reads as a drawn and engraved map: baked hillshade, contour lines, hatching, watercolour washes, an inked route | **Battle Map** (`battle-map.md`) |
| p13-pixel-vigil | Pixel Vigil, 10 s, 1280x720 on a 320x180 art grid | web, kit `pixel` mode | stable pixel grid in a cut scene, small palette, chip-tune score that arrives with the signal | technique |
| p15-moon-lesson | Why the Moon Changes Shape, 62.5 s, 16:9 | Blender Cycles, on twos | a clay classroom demonstration where real light does the physics; timing from a narration file | technique (Clay, explainers) |
| p16-dragon-tale | The Dragon Who Couldn't Fly, 16:9 | web, paper theatre (from p09) | a longer narrated pilot with an owner and agent review log (`REVIEW.md`) | pilot, waited on Sam's approval (14 Oct) |
Also: `proto/smoke` (the regression scene for `smoke.yml`), `films/showcase/` (one 90 s film per style pack, frozen on
15 Oct after the scene agent failed, about US$2.50).

## Exact steps (re-render a prototype)
1. Locally: `node harness/render.cjs proto/<id> --w 1280 --h 720 --mp4 --contact` (web) or
   `python3 harness/blender_render.py proto/<id> --w 1280 --h 720 --samples 32 --mp4` (Blender; p04, p07, p10, p15).
2. On GitHub (free): push a queue file `render/queue/<name>.json` such as `{"scenes": ["p05-relic"], "w": 1280, "h": 720, "fps": 24}`
   (Blender entries may be objects: `{"scene": "p04-witness", "parts": 6, "samples": 32}`), or dispatch `render.yml` with
   `scenes` (comma list or `all`), `w`, `h`. Output: release `gallery`, `<id>.mp4` and `<id>.contact.jpg`.
3. Each prototype's sound is its own `audio.py` (picture and sound share a timing file); run it as its NOTES say.

## How to use them now
- To start a new house style: copy the closest prototype's technique into a film folder, keep the prototype untouched (the
  Kleidion core says "Derived from proto/p03-lantern-road/lib.js; the proto stays untouched").
- To borrow one technique (rack focus, toon ramp, lightbox, pixel grid, viseme rig), read that prototype's `NOTES.md` QC log
  first: each lists the bugs found and how they were fixed.

## Known traps
- Prototype R-rules (R-2-04, R-3-06 and so on) refer to `docs/DIRECTORS_RULEBOOK.md`.
- Several prototypes' NOTES use typographic dashes and arrows (written before the house style gates); do not copy that text
  onto the screen or into narration.
- The 2 core chat box timings in the NOTES are under shared load; runners are the reference.

## Sources of truth
`proto/*/NOTES.md` (p16 `REVIEW.md`), `proto/*/scene.js`, `blender.py`, `audio.py`, `.github/workflows/render.yml`,
`render/queue/README.md`, `docs/SOUL.md` section 4, `docs/LOG.md` (13 to 15 Oct).
