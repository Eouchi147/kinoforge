# Make a Cutaway film

A block of land cut out of the world: a living landscape on top, clean strata on four sides, clear glassy water. Blender
(bpy 5.2), Cycles, everything procedural, free. Decision: `docs/decisions/0004`. Read first: `docs/SOUL.md` (Cutaway),
`films/styles/cutaway/README.md` (the kit API), `films/styles/cutaway/cinematic/NOTES.md` (the cinematic look Sam asked
for), and one finished production: `films/cutaway/venice/NOTES.md` (explainer) or `films/cutaway/loops/seasons/` (loop).
A spec-driven Cutaway line is being built since 23 Oct (`films/lib/cutaway/SPEC.md`, example `films/cutaway/meadow/`,
director line `cutaway`): once Sam has seen its first film, prefer it for new films and rewrite this playbook around it.

## Steps
1. **Brief.** In `films/cutaway/<id>/brief.md`: what the cut reveals that the viewer could not otherwise see, the audience,
   the length, the aspect (16:9 film or 9:16 ad), the easter eggs (lit like museum pieces, by depth), the end.
   Facts with sources in `script.md` if it is an explainer. A trade ad uses an invented business marked Sample.
2. **Sound first** if narrated: `ad.json` prep block, then kinoforge `sound.yml` (see `make-a-battle-map-film.md` step 3;
   `audition=` to compare voices). Pull `cues.json`. The picture follows it.
3. **Scene.** `blender.py` with `DURATION`, `SETTINGS`, `build(bpy, ctx)`, `frame(bpy, ctx, state, i, t)`, importing the kit
   (`cw.Kit(bpy, seed=..., loop=...)`). Deterministic: seeded, every frame a function of `i`. `film.json` `duration`
   equals the audio length. Words on screen as Blender text or an overlay set in code (`overlay.py` in Venice).
4. **Cinematic bar:** golden backlight, cool shade on the cut faces, haze and god rays as light cards (a full volume fogs
   the frame), animated animals and plants, surprises in the strata, a planned camera per shot with a reason.
5. **Look cheaply first:** a few stills at low size locally (`python3 films/styles/cutaway/board.py ...` for looks, or
   `python3 harness/blender_render.py films/cutaway/<id> --w 640 --h 360 --samples 16 --start N --end N+1`), then
   full-quality stills on a runner with rc-render `stills.yml` (at most 8 frames, one run in flight). Open every still.
6. **Write `NOTES.md`:** shot list with reasons, measured seconds per frame, weak spots.
7. **Gates, LOG, STATUS, commit, push.**
8. **Render:** rc-render `films.yml` with 24 parts (Blender films take about 80 min), or the Mac lane when Sam's Mac is
   connected (`render-on-the-mac.md`). Inserts for another film are rendered first; the host film lists them in `film.json`
   `inserts` (frame-exact).
9. **Check and deliver.**

## Definition of done
- Every shot seen as a full-quality still; one moving stretch seen; the loop seam checked for loops.
- `NOTES.md` complete; `bash tools/verify.sh` passes; LOG and STATUS updated; pushed.
- Render checked (`check-before-showing-sam.md`) and delivered with its weak spots named.
