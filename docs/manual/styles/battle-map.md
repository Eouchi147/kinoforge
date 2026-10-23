# Style: Battle Map (Terrain), engine v2

Battle Map is KINOFORGE's history explainer line: a 16:9 film of about 2.5 minutes in which a narrator explains a battle
over a living relief map that reads as drawn and engraved (parchment, watercolour washes by height, engraved contours,
45 degree hatching), with armies shown as many small soldier figures on wargame trays, ink arrows that draw on with a
tapered head, a motion-graphics legend, and pre-planned cameras. It is spec-driven: one `spec.js` (data) drives the
engine `films/lib/battlemap/` (Three.js r0.186 in headless Chromium, SwiftShader on CPU). Audience: kids 8 to 14 and
curious adults; tone: epic, kid-clear, upbeat, a glint of dark humour in the words and the timing, never in clip art.
Eight films exist on v2 (Cannae is the reference); see `docs/manual/films/battle-map-*.md`.

## Inputs
- A battle (or any story about places and movement) with facts checkable in two sources.
- A script of 15 to 18 narration lines, about 330 words (hook, title line "This is the Battle of X.", stakes and people,
  each side's plan, the turn, the result in plain numbers, why it mattered, a closing line with a smile).
- The sound: narration lines with word timings, a score, a mix, and `cues.json` (made before the picture; the picture
  follows it and never changes its timing). See `docs/manual/sound/battle-mix.md` and `docs/manual/sound/score-engine.md`.
- Tools: Node 22, `cd harness && npm ci && npx playwright install chromium` (once), Python 3 with numpy, scipy,
  soundfile, librosa, and ffmpeg for the sound.

## The look (what makes it this style)
| Element | Exact setting or rule | Where in code |
| --- | --- | --- |
| Frame | 16:9, rendered 1280x720 at 24 fps, delivered 1920x1080 (`film.json` `render_w/h`, `w/h`) | `film.json`, rc-render `films.yml` |
| Map sheet | baked once per stage on the GPU: paper, watercolour washes by height, engraved contours (`style.contour`), 45 degree hatching on shaded faces, hex-lattice trees, patchwork fields, water ripples, roads, grass tufts; `style.pxPerUnit` about 5.4 (sheet capped near 4096 px) | `terrainShaders.js`, `bake.js`, `worldgen.js` |
| Light | low sun from `world.sun` (azimuth, elevation), evening sun `world.sunEve`; scene `set.time` 0 = golden day, 1 = low red sun; haze and cloud per scene | `stage.js`, `scenes.js` |
| Armies | instanced figures (about 30 triangles each, 3,000 to 4,000 in a big battle) on trays; kinds `infantry`, `elite`, `cavalry`, `light`, `archers`, `elephant`, `marker`; a spacing solver keeps blocks apart at a front; casualties thin the ranks (`fadeTo`, figures shrink and sink, never fall) | `figures.js`, `blocks.js` |
| Team colours | `rome` deep red, `carthage` royal blue, `neutral`, `green`, `gold` (a team is a colour, not a nation: each film maps its sides onto them) | `icons.js` `TEAM_RGB` |
| Arrows | tapered ink strokes drawn on by an unseen pen, swept head drawn last, paper halo; `style: 'dash'` for journeys | `arrows.js` |
| Glyphs | flat, one ink weight, paper halo, no faces: heraldry (`banner`, `vexillum`, `shield`), unit symbols (`u-infantry` to `u-commander`), places (`town`, `river`, `hill`), rare annotations | `icons.js` |
| Labels | cartographic tags (small caps, paper halo, hairline leader to a ringed dot, team rule); `screen` labels are documentary captions (dark band with gold rules); counters are large tabular numbers in the team colour | `overlay.js` |
| Legend | sides panel (banner, name, commander, strength counter), key panel (unit kinds, lettered places linked to map markers), scale bar, compass; each row grows in on the word that first names it | `legend.js` |
| Type | Cinzel 600/700/800 (display), Cormorant Garamond 500i/600/600i (text), loaded by the engine | `index.js` |
| Living world | camps (tents, palisade, fires with smoke, people), walkers on roads, smoke columns, birds, wind gusts over grass, flowing water glints, drifting cloud shadows, army dust | `ambient.js` |
| Grade | `look.grade` (saturation about 0.98, contrast 1.07, grain 0.03, vignette 0.32 on Cannae); fog, sky, sun colours in `DEFAULT_LOOK` | `stage.js` |
| Edit | 5 to 9 scenes, 18 to 35 shots per 150 s (hard error over 40 per 180 s), average shot 5 to 8 s, a written `why` for every cut, camera speed limits | `scenes.js` |

## Exact steps (a new film by hand)
Playbook: `docs/PLAYBOOKS/make-a-battle-map-film.md`. Reference film: `films/battles/cannae/` (`NOTES.md`, `spec.js`).
1. Folder `films/battles/<id>/` (lowercase, dashes). Copy `film.json` and `index.html` from Cannae; change `id`
   (form `battle-map-<id>`) and `title`. `index.html` is only the importmap and
   `startBattleMap({ specUrl: './spec.js', cuesUrl: './cues.json' })`.
2. Script and facts: write `ad.json` with a `prep` block (`vo` lines, `voice`, optional `score` hints with the keys of
   `films/lib/score/hints/<film>.json`: `palette`, `key`, `mode`, `tempo`, `battle_line`, `turn_line`, `result_line`,
   `result_mood`, `epilogue_line`). Facts and two sources per fact go in `NOTES.md`. No em dash, en dash or "..." (gate `text`).
3. Sound, free route (current default):
   `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/sound.yml/dispatches -f ref=main -f 'inputs[folder]=films/battles/<id>' -f 'inputs[voice]=kokoro|bm_george'`
   (or `-f 'inputs[audition]=kokoro|bm_george,chatterbox'` first to compare voices). It commits `audio/vo/*.mp3`,
   `audio/vo.json`, `audio/score_plan.json`, `audio/score.json`, `audio/mix.m4a`, `cues.json`, `film.json`. Then `git pull`.
   Paid route (how the eight films were voiced): see `docs/manual/sound/narration.md` (ElevenLabs `brian`).
4. Plan before code, in `NOTES.md`: the scene table (scene, time, job, shots and camera plan) and the reason for every cut
   (CRAFT.md sections 2 to 4).
5. `spec.js`: `world` (terrain features), `stages` (extra maps), `blocks` hidden until the word that names them
   (`appear`), `moves`, `arrows` on the words, `labels` only for names, numbers and dates, `legend` (sides with
   `strengthAt`, 2 to 3 unit kinds, 2 to 4 lettered places with `pos`), `ambient` (camps or walkers, birds, wind, river
   flow: three layers in every wide shot), `scenes` (each with `id`, `name`, `at`, `job`, `set`, `shots` with `at`, `why`,
   `from`, `moves`), `cards` (title card on the title line, end card), `msaaOn` only on low close shots. Times are cue
   references (`"l08.charged"`), never typed seconds where a word exists. Full format: `films/lib/battlemap/SPEC.md`.
6. Film-side code only when the engine lacks something (never edit the engine for one film): a figure kind added to the
   exported `FIG_KINDS` (Waterloo `units.js` artillery, Gaugamela `kinds.js` scythed chariot, Hattin `kinds.js` flame and
   pavilion), a glyph with `registerIcon` (Thermopylae `pass`, `trail`, `stele`, `lambda`), an overlay effect in `fx.js`
   (Agincourt rain, Hattin fire and heat, territories on maps). Import them in `index.html` before `startBattleMap`.
7. Plan check, no browser: `node films/lib/battlemap/tools/scenes.mjs films/battles/<id>` until 0 errors; read every
   warning (exit 1 on errors).
8. Stills in one browser session (the sheet bakes once): `node films/lib/battlemap/tools/stills.cjs films/battles/<id> --t <one time per shot> --out out/<id>`.
   Look at every image. Debug params: `--param prof=1` (timings), `nb=1` (hide blocks), `cam=x,z,width,pitch,yaw`, `dbg=1`.
9. Director check: `node films/director/check.cjs films/battles/<id> --line battle-map` (writes `check/<spec>/report.json`
   and `sheet.jpg`, not committed). Needs `ok: true`, no overlapping labels. Look at the sheet.
10. `bash tools/verify.sh` (`--full` runs `check.cjs` on every battle), commit only your files, pull with rebase, push.
11. Render on free runners (about 12 to 20 parts):
    `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/films.yml/dispatches -f ref=main -f 'inputs[film]=films/battles/<id>' -f 'inputs[parts]=16' -f "inputs[ref]=$(git rev-parse HEAD)"`.
    Output in rc-render release `kino-films`: `battle-map-<id>.mp4` (1920x1080), `-preview.mp4` (960 wide), `-sheet.jpg`,
    `-poster.jpg`. Expected wall time 10 to 25 minutes.
12. If the sound changes after the render (re-score, re-mix), never re-render the picture: rc-render `remux.yml`
    (`docs/manual/sound/remux.md`).
13. Check (`docs/PLAYBOOKS/check-before-showing-sam.md`) and deliver (Sam's Mac `Video Production/kino-films/` with a
    `-v2` suffix for re-made films; the drive archive `KINOFORGE/films/`).

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| The director (`films/studio/<id>/brief.json`, line `battle-map`, `film.yml` then `films-render.yml`, release `films`) | Sam wants a film without hand coding; `docs/PLAYBOOKS/run-the-free-director.md`, `films/director/README.md` | usual US$0.90 to 1.50 per 2.5 min film in paid mode (cap default US$2.00); free mode spends nothing but the picture spec stage is weak |
| v1 look of a part (`armies: 'blocks'`, `overlayStyle: 'v1'`) | only to compare with old work; v1 icons are rejected by Sam | free |
| Insert a Blender Cutaway clip (`film.json` `inserts: [{film, first, last}]`) | a close-up the map cannot show (Agincourt mud) | free on runners, inserts render first |
| Local full render `node harness/render.cjs films/battles/<id> --w 1280 --h 720 --jpg --mp4 --audio films/battles/<id>/audio/mix.m4a` | a short local check only; the 2 core chat box is too slow for a film (decision 0002) | free |

## Checks before showing Sam
- `scenes.mjs` 0 errors; `check.cjs` `ok: true`; the full contact sheet looked at (one still per shot) and at least three
  5 s moving stretches (the opening, the turn, the end).
- Length equals `film.json` `duration` within a frame; 1920x1080, 24 fps; about -14 LUFS (battles measured -14.1 to -14.2),
  true peak under -1 dBTP; no frozen or black stretches (`freezedetect`, `blackdetect`).
- No emoji or cartoon icons; no units passing through each other; no label clipped, overlapping or misspelled; no dash or
  "..." on screen; the decisive moment shown twice (wide, then closer or slower); numbers from the narration only.

## Known traps
- Cue words come from speech recognition and are sometimes misspelled ("Agincourt" wrong in Agincourt l01, "Dianik,"
  for Dienekes, "Hatton" for Hattin): refer to a neighbouring word in the spec; screen text is spelled correctly.
- A wrong cue word is a hard error on purpose: the spec cannot drift from the audio.
- `inOut` (cubic) easing peaks at 3 x the average speed: use `cam`, `camSoft` or `camLong` for cameras.
- A camera move faster than a real operator could make is an ERROR (pan 0.26 frame widths a second, zoom 0.16 a second,
  yaw 16, pitch 12 degrees a second); start earlier, move less, or hold longer; `fast: 'reason'` only at a climax.
- `fadeTo` with `alphaTo` under 0.5 makes trays unreadable; the thinning does the telling.
- MSAA costs about 0.4 s a frame: keep `msaaOn` to the low close shots.
- Labels are placed by hand (`dx`, `dy`); there is no collision avoidance with the legend panels, which cover the left
  quarter of the frame: keep the action centre right.
- The engine light goes from day to a low red sun only: night is a scrim card (Thermopylae) or a film-side veil (Hattin).
- Continent and region maps are hand-drawn and not to scale; say so in the weak spots.
- The director's lint only knows the engine's kinds: a film-side figure kind goes on `kind: 'marker'` with
  `figures: '<kind>'` (Waterloo artillery).
- `cues.json` music fields describe the score: after a re-score run `films/lib/score/cues_from_score.py`; the v2 pictures
  do not snap to music.

## Cost
Free to render on GitHub runners. Measured on Cannae (shared 2 core sandbox, SwiftShader, 1280x720): 2.6 to 8.4 s wall a
frame; estimate on a quiet 4 core runner about 1.2 to 2 s a frame, about 80 min for 3,783 frames in one runner, so
12 to 20 parts finish in 10 to 25 minutes. The sheet bake is a one-off 4 to 10 s per stage. Sound: free (`sound.yml`) or
about US$0.22 to 0.25 for the eight films' paid prep (ElevenLabs voice and a Lyria score, per `ledger.json`).

## Sources of truth (the code wins if they disagree)
`films/lib/battlemap/SPEC.md`, `films/lib/battlemap/*.js`, `films/lib/battlemap/tools/scenes.mjs` and `stills.cjs`,
`films/director/check.cjs` and `films/director/lint/battle-map.js`, `films/director/CRAFT.md`, `docs/SOUL.md` section 4,
`docs/decisions/0003-battle-map-v2.md`, `docs/PLAYBOOKS/make-a-battle-map-film.md`, `films/battles/cannae/NOTES.md`,
rc-render `.github/workflows/films.yml`.
