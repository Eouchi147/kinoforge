# Film recipe: Agincourt mud insert A (`cutaway-agincourt-mud-A`)

A 14.698 s Cutaway insert (16:9, no sound of its own) laid frame-exactly into the Battle Map film "The Battle of
Agincourt" (`films/battles/agincourt/`, id `battle-map-agincourt`) over film frames 1375 to 1727 (cue l06 to l07, film
57.284 to 71.982 s): the ploughed field in rain is a trap before anyone moves, and the English archers hammer sharpened
stakes in at an angle. Kid-safe (no wounds; the humour is in the mud and the timing). Rendered on GitHub runners; laid
into Agincourt v2 (rc-render run 39908562175), delivered to Sam's Mac as `battle-map-agincourt-v2.mp4` (23 Oct). Verdict
pending.

## Folder and every file
`films/cutaway/agincourt-mud/`:
| File | What |
| --- | --- |
| `brief.md` | both inserts, cue spans, picture and job |
| `NOTES.md` | the join spans, shot plans, layout and look, measured times, check stills, weak spots |
| `agin_mud.py` | the shared world: cue words (`W(line, word)` from `films/battles/agincourt/cues.json`), spans, block, furrows, holes, puddles, strata, woods, figures (English, French), crows, worms, rain, haze, mist, eggs, `settings()`, `set_dof()` |
| `A/blender.py` | insert A's shots |
| `A/film.json` | id, 14.698 s, 24 fps, render 1280x720, delivery 1920x1080, 64 spp, `audio: ""` |

## How it is built
- Every beat is read from the Agincourt narration words, every pose is a pure function of the film time `T = (F0 + i) / 24`
  (`F0` = 1375), so a re-timed voice moves the picture with it (a re-render is needed).
- Block 4.2 x 3.2 x 0.66 m, the march along +X (France at -X, England at +X); woods: Agincourt along +Y, Tramecourt
  bulging in from -Y (the neck); autumn leaves (25 October); plough furrows across the march (about 9 cm period), clods,
  about 320 boot and hoof holes, muddy puddles (glass, brown absorption, rain rings); strata: soft wet mud 7.8 cm (dark,
  glossy), wet loam, clay, chalky marl, deep (Picardy loess over chalk); kit roots off.
- English archers in rome red jacks with kettle hats, quivers, longbows and mallets; red men-at-arms with two banners;
  colours from `films/lib/battlemap/blocks.js` TEAMS. Figures about 0.17 m.
- Light (`am.light(kit, land, 'rain')`): grey rain light, mist in both woods (`am.mist(kit, 0.55)`), a soft fill from -Y.
- Life: rain (`am.Rain`), three crows pecking on the field edge, three earthworms in the wet layers of the face; an easter
  egg: a Roman bronze coin in the clay under the English stakes (`am.easter_eggs(coin=(1.355, -0.150))`).
- `SETTINGS = am.settings(64, 0.45)`: 64 spp, OIDN ACCURATE, AgX Base Contrast, exposure 0.45, max bounces 8, clamp 6.

## Shots
- **A1** (57.28 s to the end of "mud." + 0.55 s): high and wide from the French side (az -151 to -147, el 44 to 39,
  50 mm), the block as a map, rain, rings in the furrow puddles, the soaked layers in the faces, the small red line of
  archers on the far edge; one slow push down. Cut: change of scale, from the trap to the people.
- **A2** (to 71.98 s): low on the -Y face at the English line (45 mm, f/11 to f/15), looking along the zigzag row of
  stakes; three mallet blows per stake in a wave from the near face outward between "hammered" and "them."; the nearest
  stake sits on the face, so its point goes into the soft layer in section. On "Then Henry moved his whole army forward"
  (0.5 s before "Then") the men-at-arms come up and the camera eases up and back; on "shoot" the archers lift their bows.
In and out are hard cuts on line starts (CRAFT 3).

## Exact steps that made it
1. Check stills on runners (rc-render `stills.yml`, release `stills`): the last approved round for A is `agin-r5A-f*`
   (commit 90a37e1). Runner time: about 3 to 4 min a frame for A2, 2 to 3 min for the wide (64 spp, 1280x720).
2. Render on GitHub runners (LOG 22 Oct: "Agincourt insert A rendered"; parts and run id not recorded; 24 is the
   playbook value for Blender films):
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main \
     -f 'inputs[film]=films/cutaway/agincourt-mud/A' -f 'inputs[parts]=24' -f "inputs[ref]=$(git rev-parse HEAD)"
   ```
   With `audio: ""` the join makes a silent `cutaway-agincourt-mud-A.mp4` (17,451,665 bytes, seen 23 Oct) at 1920x1080.
3. The host film lays it: `films/battles/agincourt/film.json` has
   `"inserts": [{"film": "cutaway-agincourt-mud-A", "first": 1375, "last": 1727}, {"film": "cutaway-agincourt-mud-B", "first": 2081, "last": 2420}]`.
   rc-render `films.yml` downloads each insert from `kino-films`, scales it to the render size, trims it to
   `last - first + 1` frames, shifts it to `first / fps`, and overlays it enabled by time
   (`between(t, (first - 0.5)/fps, (last + 0.5)/fps)`). The Agincourt film's own `audio/mix.m4a` runs unchanged under it.
4. The follow-up render waited on GitHub: rc-render `chain.yml` (every 15 min) rule
   `rule agincourt-v2 films/battles/agincourt 16 cutaway-agincourt-mud-A.mp4 cutaway-agincourt-mud-B.mp4`; it was
   dispatched by hand at 04:21 UTC on 23 Oct when the cron had not fired. Run 39900294683 laid A but not B (overlay bug,
   see B); after the fix (rc-render 54c1bb4) run 39908562175 succeeded: 147.3 s, -14.2 LUFS, both inserts checked on
   their boundary frames.

## Sound
None of its own: the Agincourt film's mix plays over it.

## Cost
US$0. Local build on the 2-core box 5 to 8 s; frame pose and evaluation 1 to 3 s.

## Sam's verdict
Pending (the Agincourt film and its inserts are on his list).

## Weak spots (from NOTES)
Furrow crests close up (A2) catch the grey sky and read slightly plastic (they do read wet); figures are rigid parts (no
bending knees); the mud surface does not deform around boots.

## To make a new insert like it
1. Read the host film's `cues.json`; span = start of the first line to the start of the line after the last; frames
   `first = round(t0 * 24)` to `last`.
2. Put every beat on a word (`W(line, word)`), every pose a function of the film time; `film.json` `duration` = the span.
3. Render it first; then add it to the host's `film.json` `inserts` and render the host.

## Checks before showing Sam
Check the boundary frames of the host film (1374, 1375, 1727, 1728) after the join.

## Known traps
Chained ffmpeg overlays: enable by time, not by `n` (`docs/LESSONS.md`). Boolean cuts: the Manifold solver (EXACT was
about 40 s a frame).

## Sources of truth
`films/cutaway/agincourt-mud/brief.md`, `NOTES.md`, `agin_mud.py`, `A/*`, `films/battles/agincourt/film.json`, rc-render
`films.yml` and `chain.yml`, `docs/LOG.md` (22 and 23 Oct), `docs/LESSONS.md`. The code wins if they disagree.
