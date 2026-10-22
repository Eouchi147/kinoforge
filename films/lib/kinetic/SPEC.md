# Kinetic engine: the spec

One JSON-like object (a `spec.js` that `export default`s it, or a plain JSON file) drives a whole 9:16 film made of type, documents
and objects (the Dark Corners "Kinetic" look, generalised from the hand-built Bamberg film). The engine is `films/lib/kinetic/`
(Canvas 2D only, no three.js, about 0.05 to 0.5 s per frame). A film is just:

```html
<!-- films/studio/<name>/index.html -->
<body style="margin:0;background:#000"><script type="module">
  import { startKinetic } from '/films/lib/kinetic/index.js';
  startKinetic({ specUrl: './spec.js', cuesUrl: './cues.json' });
</script></body>
```

Folder = `index.html`, `spec.js`, `cues.json`, `film.json`, `audio/mix.m4a` (same contract as every film: `window.KF`, `KF_READY`, size from `?w=&h=`, default 720x1280).
Render: `node harness/render.cjs films/studio/<name> --w 720 --h 1280 --jpg --out out/<name>`.
Fast stills in one browser session: `node films/lib/kinetic/tools/stills.cjs films/studio/<name> --t 3,17.6,40 --out /tmp/x`
(`--cards` = one still per card at its first landing, `--sheet` = contact sheet, `--range a,b,step` = frames). It prints the spec's
errors and warnings. Query params: `?safe=1` draws the platform-UI safe mask, `?captions=1` burns captions from the cues.

The picture follows the sound: **never change cue times**. Every frame is a pure function of its index (no clocks, seeded randomness only).

## 1. Time references (`at`, `until`, `on`, `settle`, `strikeOn`...)

Same forms as the Battle Map engine. A wrong line or word is a hard error, so the spec cannot silently drift from the audio.

| form | meaning |
| --- | --- |
| `12.5` | seconds |
| `"x1"` / `"x1>"` | a pure line ref in `at`/`line` = that line's start (cut a little early, see below); `>` = the line's end |
| `"x1.Zong"` / `"x1.Zong>"` | start / end of the word "Zong" in line `x1` (case and punctuation ignored, prefix match: `witch` finds "witches") |
| `"x1.the#2"` | the third "the" in the line (0-based) |
| `"x1.Zong+0.3"` | offset in seconds, `+` or `-` |
| `"d1.twenty-ninth,"` | words with hyphens and commas work as written in the cues; digits match number words under 100 ("54" finds "fifty-four") |
| `"myMark"` | an entry of `spec.marks` (`{ myMark: "x1.Zong" }`) |
| `{ line, word, nth, edge, offset, snap }` | object form; `snap: true` (or seconds) snaps to the nearest music strong hit |
| `{ hit: n }`, `{ beat: n }`, `{ downbeat: n }` | music grid from `cues.json` |

Line ids are whatever `cues.json` calls them (`o1`, `x4`, `l08`...); they must match `^[A-Za-z_][A-Za-z0-9_]*$`.

## 2. The spec

```js
export default {
  series: 'DARK CORNERS',            // used by title / end cards
  title: ['The Ship', 'Called Care'], // string or array of lines
  accent: '#cf3b2e',                  // the ONE accent colour (default #cf3b2e); use it once per film
  look: { vignette: 0.30, grain: 0.045, shake: 1, snap: true },   // finish pass: vignette, grain, warm tint baked into the paper; snap = landings snap to strong hits within 0.12 s
  captions: false,                    // true or { size, y } burns the narration under the picture (optional)
  marks: {},                          // named times
  cards: [ ... ],                     // in time order
}
```

### Cards are cuts on the timeline

`cards` is a list of cards. Each needs a start: `at` (a time ref) or `line` (a cue line id; the cut is placed about 0.12 s before the line's first word, never into the previous line).
A card runs until the next card starts (cards are hard cuts, like Bamberg), or until `until`. Gaps are allowed (they show the dark card; use them for silence on purpose), but the engine warns about gaps over 1 s.
The `end` card defaults to the last `end_card_s` seconds (cues) of the film.

Options on every card:

| key | meaning |
| --- | --- |
| `type` | one of the types below |
| `at` / `line` / `until` | start, start-by-line, end |
| `bg` | `'dark'` (ink-black card, cream type), `'paper'` (cold grey court paper, black type), `'parchment'` (warm cream, brown-black ink). Defaults: `record` paper, `letter` parchment, everything else dark |
| `pos` | where the text block sits in the 9:16 safe zone (x 0.11 to 0.78, y 0.15 to 0.65 of the frame): `'top'`, `'upper'` (default for most), `'middle'`, `'lower'`, or a number (top edge as a fraction of the height) |
| `align` | `'left'` (default), `'center'`, `'right'` |
| `accent` | `true` = the card's last text line is drawn in the accent colour (`'first'`, or a line index). Use on ONE card per film; the engine warns otherwise |
| `hold` | seconds to keep the card after its last word lands (shorter than "until the next card"; leaves a dark gap) |
| `exit` / `enter` | `'cut'` (default) or `'fade'` (to / from black, `exitDur`, `enterDur` default 0.3 s) |
| `over: true` | the card is drawn on top of the card running under it (no background of its own, does not end the previous card); use for a stamp or caption laid over something. Needs `at`, and `until` or `dur` |
| `from` | start of the word search for automatic timing (default: the card's start) |
| `name` | label shown in tools |

### Automatic timing (the default)

Give text and no timing and **each word lands on the matching cue word**: the engine scans the cue words forward from the card's
start (up to 9 words ahead per word) and matches by letters; words with no match (a number like "1781" for "seventeen eighty one",
a label that is not in the narration) are placed between their neighbours. If nothing matches, the lines spread over the card.
So `{ type: 'statement', line: 'x1', text: [...] }` just works if the card's text paraphrases the narration in the same order.
Override any line with `on: ref` (all its words land together on that time) or `on: [ref, ref, ...]` (per word) in the object form.

## 3. Text mini-language (statement, slam lines, record lines, map steps...)

Wherever a card takes `text` / `lines`: a string, an array of strings, or objects. Parts of one string are separated by ` / ` or a newline.

| prefix | line style |
| --- | --- |
| (none) | body: caps, fitted to the measure (max cap height 6.5 % of the frame) |
| `^` | kicker: small, widely tracked caps |
| `+` | heavy: bigger, heavier landing |
| `!` | payoff: big, hard slam |
| `!!` | huge payoff (use for the one word the line is about) |
| `#` | stamp: big smeared stamp (dates, numbers) |
| `~` | typed: Special Elite typewriter line, wraps by itself |
| `==` | a rule that draws across under the previous line |
| `_` | extra gap |

- A single plain string with no ` / ` is wrapped into balanced lines. If no prefix is used anywhere, a lone short line becomes a payoff and the last short line of a block becomes the payoff (`emph: 'none'` turns this off).
- Object form: `{ kind: 'big'|'heavy'|'huge'|'kicker'|'body'|'stamp'|'typed', txt, on, after, accent, maxCap, cap, ls, color, align, mode }`; `{ rule: true }`, `{ gap: 0.03 }`.
- Words **land** with a vertical stretch that snaps back (the Bamberg "slam"); payoff lines also shake the frame and flash on the beat. Typed lines type letter by letter.
- A block taller than the safe zone gets a warning: split the card.
- Write the words of the narration, in capitals for display lines. Names, numbers and dates come from the narration. **No em dashes, en dashes or "..." anywhere in the spec** (the engine throws), no invented facts.

## 4. Card types

### `statement`
Lines landing word by word on the cue words. `text` or `lines` (mini-language above). Optional `deco`: `{ kind: 'rope', on, x, len }` (a twisted rope drawing down from the top edge) or `{ kind: 'bars', on }` (cell-bar hairlines).
```js
{ type: 'statement', line: 'x1', text: ['^THE SHIP WAS CALLED', '!!THE ZONG.'] }
{ type: 'statement', at: 'o1.ran', text: 'RAN SHORT OF WATER IN THE CARIBBEAN.' }
```

### `slam`
A big date or number that slams on a word, with a kicker above and a typed dateline under a rule. `text` (the big thing; or an array of `{ text, on }` for **ticks**: "28 JUNE" then "29 JUNE" replace each other), `on` (the slam time), `kicker`, `dateline` (typed on the words), `lines` (statement lines below), `rule: false`, `cap` (max cap height).
```js
{ type: 'slam', at: 0, kicker: 'IN', text: '1781', on: 'o1.1781,', dateline: 'A BRITISH SLAVE SHIP' }
```

### `record`
Cold typed document on paper. `header` (typed, tracked, with a rule), `date` (big stamp), `lines` (typed by default; use prefixes for big words). `bg` defaults to `paper`.
```js
{ type: 'record', line: 'c1', header: 'INSURANCE CLAIM', lines: ['THE OWNERS CLAIMED THE INSURANCE', '!!HAD DROWNED.'] }
```

### `letter`
Warm parchment, handwriting that writes itself glyph by glyph on the cue words (wet ink, tremor). `text` (wrapped by itself) or `lines: [...]`, `kicker` (small printed caps above), `size: 'small'|'normal'|'big'`, `fail: true` (the hand weakens: tremor and sag grow through the card), `tremble`, `underline: true`, `blot: true`, `sign` (a last, indented line), `accent: true` (signature in the accent). `bg` defaults to `parchment`.
```js
{ type: 'letter', at: 'f1.Only', text: 'Only their price.', size: 'big' }
```

### `quote`
A third hand: serif (IM Fell English), double-struck (a ghost copy a hair off register), tilted a little, with a large opening mark. `text`, `by` (attribution, small caps after the last word), `size: 'big'`, `tilt` (radians), `mark: false`, `italic: true`.
```js
{ type: 'quote', at: 'c3.It', text: 'It is the case of throwing over goods.', size: 'big' }
```

### `stamp`
A stamped word over a document sheet. `word`, `on` (default: the cue word if it matches, else 0.9 s in), `doc: { header, date, lines }` (typed onto the sheet; omit `doc` for grey placeholder rules), `angle` (degrees, default -6), `place: [fx, fy]` (stamp centre as frame fractions), `accent: true` (accent-coloured stamp), `sheet: false` (no sheet: the doc is set straight on the card background, use with `bg: 'paper'`), `frame: false`, `fit` (width as a fraction of the measure, default 0.8). Heavy shake on the hit.
```js
{ type: 'stamp', line: 'x4', doc: { header: 'INSURANCE', lines: ['EVERY CAPTIVE'] }, word: 'INSURED', on: 'x4.insured' }
```

### `count`
A number counting up with a label (digits in fixed cells, ends with a slam). `to` (number), `from` (default 0), `on` (when counting starts), `settle` (when it must arrive; or `dur`), `kicker` (above), `label` (below, mini-language, matched to the cues), `prefix`, `suffix`, `decimals`, `commas: false`, `cap`, `align`.
```js
{ type: 'count', at: 'x2.and', kicker: 'AND ABOUT', to: 440, on: 'x2.about', settle: 'x2.forty+0.4', label: ['AFRICAN', 'CAPTIVES.'] }
```

### `list`
Items appearing in turn, each with a marker. `title` (kicker above), `items: [string | { txt, mark, on, accent }]`, `marker`: `'num'` (01, 02), `'dot'`, `'tick'`, `'cross'`, `'none'` (per item `mark` overrides). Long items wrap by themselves. Items land on their cue words (or `on: [ref, ...]` at card level).
```js
{ type: 'list', at: 'm3.Captives', bg: 'paper', title: 'THE RULE', items: [{ txt: "DIED OF SICKNESS: THE OWNERS' LOSS", mark: 'cross' }, { txt: 'THROWN OVERBOARD: THE INSURERS PAID', mark: 'tick' }] }
```

### `map`
An **abstract** grid (never geography) that draws itself, with nodes, edges and a pen route appearing on words. Coordinates are frame fractions `[0..1, 0..1]`; keep nodes inside y 0.2 to 0.64.
- `grid`: `'streets'` (wobbly city grid with a river), `'graticule'` (curved meridians and parallels), `'sea'` (long wave lines), `'none'`; `seed`, `gridOn` (when it starts drawing; earlier than the card start = already drawn, so consecutive map cards look like one), `gridDur`, `gridAlpha`.
- `nodes: { id: { x, y, label, on, kind: 'ring'|'dot'|'square'|'none', big, side: 'right'|'left'|'above'|'below', accent, xOn } }`: a ring lands on `on` (default: the label's cue word), `xOn` strikes a cross over it. `kind: 'none'` is a label only.
- `edges: [{ from, to, on, dur, dash, accent }]` or `['a', 'b', { on }]`; drawn between two nodes.
- `routes: [{ points: [[x, y], ...] | via: ['a', 'b'], on, until, dash, ease: 'linear', pen: false }]`: a pen walks the path.
- `zoom`: a number (slow push-in over the card) or `[[ref, z], ...]` keyframes; `focus: [fx, fy]`.
- Text: `text` (one block) or `steps: [{ at, text }]` that replace each other on the cue words (each step's words are matched from its own start).
```js
{ type: 'map', line: 'm1', until: 'm2.And', grid: 'sea', seed: 4,
  nodes: { jam: { x: 0.56, y: 0.54, label: 'JAMAICA', on: 'm1.Jamaica.', big: true } },
  routes: [{ points: [[0.06, 0.74], [0.47, 0.6]], on: 'm1.In', until: 'm1.Jamaica.>', ease: 'linear' }],
  steps: [{ at: 'm1', text: ['^IN LATE NOVEMBER,', '!!JAMAICA.'] }, { at: 'm1.The', text: ['^THE CAPTAIN THOUGHT', '!ANOTHER ISLAND.'] }] }
```

### `strike`
Text that is struck through and then contradicted. `text` (lines, mini-language; kicker lines are not struck), `strikeOn` (when the bars draw; default 0.9 s after the last word), `then` (lines that land after the strike), `bar: 'accent'` (default: ink; a thin line on dark, a thick bar on paper).
```js
{ type: 'strike', at: 'j2.No', text: ['^NO ONE WAS EVER', 'CHARGED WITH', '!MURDER.'], strikeOn: 'j2.murder.>+0.15' }
```

### `drawer`
Archive drawer and file reveal: a drawer with a label plate, a folder, warm light and dust. `label` (plate), `folder` (folder cover label), `strip: [typed lines]` (the paper in the file; `false` = none), `text` (statement above), `start: 'closed'|'open'`, `openAt` (cover opens), `dropAt` (the strip slips into the file), `closeAt` (cover closes with a thump), `push` (slow push-in, default 0.05), `dust`.
```js
{ type: 'drawer', at: 'f2.kept', label: 'CASE FILE', folder: 'THE FILE', strip: ['A LETTER'], dropAt: 'f2.kept', closeAt: 'f2.file.', text: ['^KEPT IN', '!!HIS FILE.'] }
```

### `title`
The series card: `series` (big stamped caps, default `spec.series`), a rule, then `title` (serif, word by word; default `spec.title`). `on` (slam time, default 0.2 s after the start), `fadeOut`.
```js
{ type: 'title', at: 14.85, on: 15.1 }
```

### `end`
Same card for the end; default start = `duration - end_card_s`; fades to black over the last 0.4 s. Optional `line` (a statement above). `{ type: 'end' }`.

## 5. Checks the engine does for you

Errors (the page sets `window.KF_ERROR`, stills.cjs prints it and exits 2): unknown cue line or word, unknown card type, em / en dash or "..." in any text, an edge to an unknown node, a card that ends before it starts.
Warnings (`window.KF_WARNINGS`): accent used on more than one card, a card under 0.5 s, dark gaps over 1 s, nothing on screen at the end, a text block taller than the safe zone.

## 6. Look and cost

- Colour script: dark card + cream type for narration, cold paper for records and the court, parchment for letters and the human hand; ONE accent colour, once. Cut backgrounds with the story, not to decorate.
- One idea per card, one payoff word per card. Hard cuts on the narration, a heavy word on every strong hit.
- Restraint on atrocity: words and objects only (documents, stamps, rope, drawer, numbers). No bodies, no pictures of violence.
- Cost: about 0.05 s/frame in headless Chromium for stills (the finish pass is baked tiles, no shaders); the renderer adds PNG/JPEG encode (about 0.15 to 0.4 s/frame at 720x1280).
- Determinism: baked paper uses seeded noise, grain is a tile at a per-frame deterministic offset, so two renders are byte-identical.

## 7. Worked example: a short film (facts are placeholders; the words come from your narration)

```js
export default {
  series: 'TRUE STORIES', title: 'The Long Night',
  cards: [
    { type: 'slam', at: 0, kicker: 'IN', text: '1901', on: 'l01.1901', dateline: 'A HARBOUR TOWN' },
    { type: 'statement', line: 'l02', text: 'THE BELLS WERE RUNG ALL NIGHT.' },
    { type: 'count', line: 'l03', kicker: 'MORE THAN', to: 300, on: 'l03.three', settle: 'l03.hundred+0.2', label: 'BOATS WAITED.' },
    { type: 'record', line: 'l04', header: 'LOG BOOK', lines: ['THE LAMP WENT OUT.', '!!NO ONE KNEW WHY.'] },
    { type: 'strike', line: 'l05', text: ['^THE REPORT SAID', 'NO FAULT.'], strikeOn: 'l05.fault', then: ['!!SOMEONE', 'LIED.'] },
    { type: 'title', at: 'l06', on: 'l06' },
  ],
};
```
The full 179 s demo (every card type except drawer) is `films/studio/kinetic-demo/spec.js`, with the Zong episode's `cues.json`.
