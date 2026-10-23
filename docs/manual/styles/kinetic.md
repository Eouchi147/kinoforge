# Style: Kinetic (typography as cinema, 9:16)

Kinetic tells a true story with words, dates, documents and numbers directed like film, in 9:16 for phones: type that
lands on the narrator's words, stamps, typed court records, handwritten letters, counters, an abstract map, a strike-through,
an archive drawer. It exists in two forms: (1) the hand-built Dark Corners film Bamberg ("A Hundred Thousand Good Nights",
`films/dark-corners/bamberg/`, Canvas 2D, one candle-lit desk), and (2) the spec-driven engine `films/lib/kinetic/`
generalised from Bamberg (a `spec.js` of cards; demo `films/studio/kinetic-demo/`, the Zong episode re-told from a spec).
The director's `kinetic` line uses the engine. Origin: prototype `proto/p11-kinetic` (an 8 s Bamberg hook). Audience:
short-form adults; tone plain and restrained, facts carry the weight.

## Inputs
- A true story with checked facts, and its narration already recorded and placed: `cues.json` (lines with word times,
  strong hits), `audio/mix.m4a`. The picture follows the sound; never change cue times.
- Tools: Node 22 and the harness (`cd harness && npm ci && npx playwright install chromium`).

## The look (what makes it this style)
| Element | Rule |
| --- | --- |
| Frame | 9:16, rendered 720x1280 at 24 fps, delivered 1080x1920; every size is relative to the frame height |
| Safe zone | every word inside x 0.11 to 0.78, y 0.15 to 0.65 of the frame (rule R-2-08 of `docs/DIRECTORS_RULEBOOK.md`); `?safe=1` draws the platform mask |
| Surfaces (colour script) | dark ink-black card with cream type for the narration; cold grey paper with black print for records and the court (no candle); warm parchment with brown-black ink for letters and the human hand |
| Accent | ONE accent colour (default `#cf3b2e`), used on one card per film (Bamberg: "I am innocent.") |
| Type | Bebas Neue (display, slams), Cormorant Garamond italic 500/600 (the human hand), Special Elite (typed court print), IM Fell English (a third hand, double struck) (`films/lib/kinetic/lib.js` `FONTS`) |
| Motion | words LAND on their cue word with a short vertical stretch that snaps back; payoff lines shake the frame and flash on the beat; typed lines type letter by letter; handwriting writes glyph by glyph with wet ink and tremor |
| Finish | baked paper grain, ink dropout, a 0.7 px ink spread, vignette and grain tiles in Canvas 2D (no WebGL in the render path) |
| Restraint | no bodies, no pictures of violence: words and objects only (documents, stamps, rope, drawer, numbers) |
| Edit | hard cuts on the narration by default; every effect has a written job (Sam, 22 Oct: "effects with no intent" was the fault of Bamberg v1) |

## Exact steps (spec-driven film)
1. Folder `films/studio/<name>/` (or the series folder): `index.html` (below), `spec.js`, `cues.json`, `film.json`,
   `audio/mix.m4a`.
   ```html
   <body style="margin:0;background:#000"><script type="module">
     import { startKinetic } from '/films/lib/kinetic/index.js';
     startKinetic({ specUrl: './spec.js', cuesUrl: './cues.json' });
   </script></body>
   ```
2. Sound: same tools as Battle Map (`docs/manual/sound/narration.md`, `battle-mix.md`, `score-engine.md`); the director's
   `kinetic` line uses `films/lib/battle_mix.py` (title line index 1) and the free score. Dark Corners films keep their
   original episode mix.
3. Write `spec.js`: `series`, `title`, `accent`, `look` (`vignette`, `grain`, `shake`, `snap`), `marks`, and `cards` in time
   order. Card types: `statement`, `slam`, `record`, `letter`, `quote`, `stamp`, `count`, `list`, `map` (abstract grids only,
   never geography), `strike`, `drawer`, `title`, `end`. A card starts at `at` or `line` and runs until the next card (a hard
   cut). Words land automatically on matching cue words; override with `on`. Text mini-language prefixes: `^` kicker,
   `+` heavy, `!` payoff, `!!` huge payoff, `#` stamp, `~` typed, `==` rule, `_` gap. Full format: `films/lib/kinetic/SPEC.md`.
4. Stills and checks in one browser session:
   `node films/lib/kinetic/tools/stills.cjs films/studio/<name> --cards --out out/<name>` (one still per card at its first
   landing; `--sheet` for a contact sheet; `--t 3,17.6` or `--range a,b,step`). It prints the spec's errors (exit 2) and
   warnings. Look at every still with `?safe=1` once.
5. Render: on free runners with rc-render `films.yml` (`inputs[film]=<folder>`, `parts` 12 to 20, full `ref`), release
   `kino-films`; or through the director (`films-render.yml`, release `films`). Local:
   `node harness/render.cjs films/studio/<name> --w 720 --h 1280 --jpg --out out/<name>`.
6. Check (`docs/PLAYBOOKS/check-before-showing-sam.md`) and deliver.

## Exact steps (hand-built, as Bamberg)
Bamberg was polished by hand rather than rebuilt on the engine because the engine has no town plan, paper fold,
transitions or rope (NOTES.md). Its build: `scene.js` composer (scene layers, transitions, finish), `engine.js`
(words land on word times, handwriting writer), `kit.js` (text blocks), `map.js` (the schematic plan), `fold.js`
(the paper fold: each flap cut into 18 slices bent about its hinge), `textures.js` (desk, parchment, cold paper),
`scenes_open.js`, `scenes_record.js`, `scenes_plea.js`, `scenes_end.js`; landing times looked up with
`E.tw(line, word, nth)`. Use this route only when a film needs objects the engine lacks; otherwise extend the engine
(a new card type in `films/lib/kinetic/cards/`) so the next film gets it.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| Director line `kinetic` (brief `line: "kinetic"`) | a new true story without hand coding; Great Emu War was the first (stopped at the script stage by the free-model daily limit on 22 Oct) | usual paid director cost, capped |
| Battle Map | the story is about places and movement | see `battle-map.md` |
| Social `type-motion` template | a client's tip in brand colours over a real photo | `social.md` |

## Checks before showing Sam
- Every word inside the safe zone on every frame; no text on screen twice; no overprinting at card changes (Bamberg's first
  render overprinted at 148 s; all 38 changes were audited after).
- The accent used once; a heavy word on strong hits only where the story wants it; a real silence before the open loop.
- Each effect has a one-line job written in `NOTES.md` (Bamberg's audit table is the model).
- Length equal to `film.json`; 1080x1920; about -14 LUFS.

## Known traps
- No em dash, en dash or "..." anywhere in a spec: the engine throws (`compile.js`).
- A text block taller than the safe zone gives a warning: split the card.
- Masked word reveals need at least 135 % travel or descenders peek out of the mask (`docs/LESSONS.md`).
- Never measure text before the fonts load.
- A `map` card is an abstract grid (`streets`, `graticule`, `sea`), never real geography: keep claims honest.
- Number words: digits match number words under 100 only ("54" finds "fifty-four"); bigger numbers are placed between
  their neighbours.

## Cost
Free. Engine: about 0.05 s a frame in headless Chromium for stills plus 0.15 to 0.4 s encode at 720x1280. Bamberg measured
0.05 to 0.4 s a frame (heaviest: the ink bleed, the street walk, the fold). Renders deterministic, byte-identical.

## Sources of truth
`films/lib/kinetic/SPEC.md` and `*.js`, `films/lib/kinetic/tools/stills.cjs`, `films/dark-corners/bamberg/NOTES.md`,
`films/studio/kinetic-demo/spec.js`, `proto/p11-kinetic/NOTES.md`, `films/director/lines.json` (`kinetic`),
`docs/SOUL.md` section 4, `films/director/CRAFT.md`.
