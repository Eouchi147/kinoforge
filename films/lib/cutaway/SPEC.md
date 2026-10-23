# Cutaway line: the spec (`spec.json`)

The Cutaway line makes films in the Cutaway style (a block of land cut out of the world: a living landscape on top, the
layers underneath cut clean like a diagram, surprises buried at their depth) from **data**. A spec names presets; the
engine (`films/lib/cutaway/engine.py`, Blender 5.2, Cycles, free) builds them with the kit (`films/styles/cutaway/`)
and the cinematic extras (golden light, fog, god rays, animals, easter eggs). Nobody writes Blender code for a film.

A film folder of the line holds: `spec.json` (this file's format), `cues.json` (the narration's line and word times),
`film.json` (id, sizes, fps, samples, audio), `blender.py` (a copy of `films/lib/cutaway/blender.py`, unchanged), and the
sound (`audio/mix.m4a`). Example: `films/cutaway/meadow/`.

Check a spec in a second, with no Blender: `python3 films/lib/cutaway/tools/validate.py <film dir> [--spec cand/a.json]`.
Look at it: `python3 films/lib/cutaway/tools/stills.py <film dir> --w 480 --samples 8` (contact sheet), or runner stills
with rc-render `stills.yml` (playbook: `docs/PLAYBOOKS/cutaway-film.md`).

## 1. Time references

Everywhere a time is accepted (`until`, `at`, `done`, `lift_at`...) you can write (same forms as the Battle Map engine):

| form | meaning |
| --- | --- |
| `12.5` | seconds |
| `"l08"` / `"l08>"` | start / end of cue line `l08` |
| `"l08.mole"` | start of the word "mole" in line `l08` (case and punctuation ignored; exact match first, then prefix) |
| `"l08.mole>"` | end of that word |
| `"l08.step#1"` | the second "step" in the line (0-based) |
| `"l05.chest+0.4"`, `"l05>-0.6"` | an offset in seconds (a trailing `+n` or `-n` is always an offset) |
| `"start"`, `"end"`, `"outro"` | 0, the film's end, the start of the end card (`duration - cues.outro_s`) |
| `"myMark"` | an entry of `marks` (`{"myMark": "l03.giant"}`) |

A word that is not in the line is an error that names the line's words, so a spec cannot drift from the narration.

## 2. The top level

```json
{
 "format": "16:9",
 "look": {"samples": 20, "quality": "fast", "exposure": 0.1},
 "title": {"text": "What Lies Under a Meadow", "kicker": "CUTAWAY", "at": "l01", "until": "l01>+2.6"},
 "end": {"text": "CUTAWAY", "sub": "What Lies Under a Meadow"},
 "marks": {},
 "sets": {"meadow": {}},
 "scenes": []
}
```

| key | meaning |
| --- | --- |
| `format` | `"16:9"` (render 1280x720, delivered 1920x1080) or `"9:16"` (720x1280, delivered 1080x1920) |
| `look.samples` | Cycles samples (20 is the house value; denoised); `quality: "full"` = full bounces (slower) |
| `look.art` | optional art direction on top of the line: the name of a module in `films/styles/cutaway/art/` (`apply(bpy, film, ctx)` once after the build, optional `frame(bpy, film, ctx, t, shot)` each frame); `$KF_ART` overrides it |
| `title` | the title card (set in code, on a paper plate): `text`, optional `kicker` (small caps above), `at`/`until` (default: the title line and 2 s after it) |
| `end` | the end card over the outro: `text` (series or brand, capitals) and `sub` (the film title) |

## 3. Sets (the worlds)

A set is one block of land, built at the origin. Usually one set per film; a second set only for a change of place or
time. `"like": "meadow"` copies another set and changes only what you write (for example the same place at dusk).

| key | values (default) | what |
| --- | --- | --- |
| `size` | `small` (3 x 3 m, 1.3 deep), `standard` (4 x 4 m, 1.6 deep), `deep` (4 x 4 m, 2.1 deep) | the block |
| `strata` | `time` (recent soil, sand, clay, a Roman loam, gravel, ochre, fossil limestone, bedrock), `meadow`, `red`, `limestone`, `lagoon`, `mud` | the layers on the cut faces |
| `terrain` | `flat`, `rolling`, `hills` | the top |
| `water` | `river` (an S-bend out through the -Y face), `stream`, `pond` (against the -Y face), `lagoon` (the front corner), `none` | water is glass you can see into on the cut |
| `season` | `summer`, `spring`, `autumn`, `winter` | grass, leaves, snow |
| `time` | `day` (sky, cheap), `golden` (low warm sun behind the block, rim light, cloud gaps, god rays), `dusk` (lit windows and lamps), `overcast`, `studio` (white seamless, for ads) | light |
| `trees`, `flowers`, `reeds`, `lilies`, `boulders`, `grass`, `corals` | counts and amounts (12, 0.5, 0.5, 10, 10, 1.0, 0) | vegetation, all moving in the wind |
| `fog` | 0 to 1 (0) | ground fog in the valleys and mist on the water; **costs about 2.5 times the render time of a wide shot**: only when the story needs it |
| `shafts` | 0 to 1 (1 at golden and dusk) | god rays (cheap cards) |
| `seed` | integer (4) | the random layout (houses, animals, trees) |
| `props` | `{"village": 5, "mill": true, "bridge": true, "lamps": 3, "houses": [[x, y, yaw]], "pipes": [[[x, y, z], ...]], "piles": [[x, y, length]]}` | from the kit; houses and lamps are placed on dry land by the seed; mill and bridge need a river or stream |
| `eggs` | list, below | easter eggs in the cut faces |
| `animals` | list, below | life |

Coordinates: metres, the block centred on the origin, the turf near z = 0, the bottom at z = -depth. The two cut faces
the camera sees are **-Y** (the long front face; cranes and macros look at it) and **+X** (the right face, seen in hero
shots). `u` is the position along a face, from -size/2 to +size/2 (left to right as seen from outside).

### Eggs (by depth: recent near the top, deep time at the bottom)

`{"kind": "dino", "face": "-Y", "u": -0.78, "depth": 0.98, "id": "rex"}`. `face` default `-Y`; `u` default: spread along
the face; `depth` (metres below the turf) default per kind; `id` default the kind (labels and cameras name eggs by id).

| kind | default depth | what |
| --- | --- | --- |
| `mole` | 0.115 | a mole digging its tunnel under the turf, its nest at the end (the tunnel runs about 0.6 m to the right of `u`) |
| `hedgehog` | 0.17 | asleep in a leaf-lined burrow, breathing |
| `chest` | 0.31 | a pirate chest ajar, coins spilling |
| `amphora` | 0.46 | a Roman amphora with shards and bronze coins |
| `well` | 0.78 (its bottom) | an ancient well cut in half, a bucket swaying (runs from the turf down) |
| `ammonite` | 0.84 | a spiral fossil with a nacre sheen |
| `dino` | 0.98 | a T. rex skeleton (about 1 m long; macro and labels aim at its skull); `scale` 0.6 to 1.2 |
| `geode` | 1.10 | cracked open, glowing amethyst points (two per set allowed) |
| `trilobite` | 1.235 | at the base of the limestone |
| `gold` | 1.42 | a quartz vein with gold nuggets across the bedrock; `span` (3.0 m) is its length |

Rules (the validator): one of each kind per set (two geodes), at most 12 per set (each has its own light), inside the
block, not overlapping on a face, recent above old above deep (soft). Depths deeper than the block are moved up.

### Animals

`{"kind": "deer"}`, with optional `at` `[x, y]`, `path` `[[x, y], ...]`, `n`, `yaw`, and times `lift_at` (deer),
`strike_at` (heron). Without them the seed places each one where it belongs (dry land, the shallows, the water near the
cut face). Kinds: `deer`, `fawn`, `rabbit`, `fox`, `heron`, `ducks` (n), `fish` (n, behind the glass of the cut face),
`birds` (n), `fireflies` (n, best at dusk), `butterflies` (n), `petals` (n). Heron, ducks and fish need water.

## 4. Scenes and shots

Write the scene list first (CRAFT.md 2): each scene is one place and one dramatic question.

```json
{"name": "The young layers", "set": "meadow", "job": "What is just under the turf?",
 "begin": "the treetops and the river glass", "middle": "the finds appear as they are named", "end": "the Roman layer",
 "shots": [
  {"camera": "crane", "face": "-Y", "u": -0.7, "to": "amphora", "until": "l02>-0.6",
   "why": "the reveal: the cut face read from the top down, each find on the word that names it",
   "labels": [{"text": "MOLE TUNNEL", "at": "l02.mole", "until": "l02.chest-0.2", "point": "mole", "slot": "upper-left"}]}
 ]}
```

Shots run in order with no gaps: each starts where the previous ended and ends at its `until` (a time reference); the
last shot of the film has no `until` (it runs to the end). Every shot needs a `why` (new information, place, time,
reaction or scale). `set` on a shot overrides the scene's set. `transition: "dip"` dips through pale mist into the shot
(only for a change of time); the default is a hard cut.

### Camera presets (every move eased in and out, in real time)

| camera | what | parameters |
| --- | --- | --- |
| `map` | straight down on the whole block, a slow drift and turn: where we are | `turn` (6 degrees), `roll` (22), `dir` |
| `orbit` | high three-quarter on the whole block, a slow orbit: the world, wide | `deg` (8), `dir` (1 or -1), `el` (30; 27 in 9:16), `az` (-50) |
| `push` | three-quarter, a slow push toward a `target` | `target` (egg id, `"water"`, `"mill"`, `"house"` or `[x, y, z]`), `amount` (0.22), `aim` (0.6), `el`, `az`, `deg` |
| `pull` | the reverse of push: from close to wide, the consequence | as push |
| `ground` | low at the corner of the cut, eye on the grass, along the -Y face into the light; shallow focus | none |
| `crane` | a vertical crane down a cut face from the treetops: the reveal, layers read as time | `face` (`-Y`/`+X`), `u` (the column; default the target egg), `from` (z, 0.32 = treetops), `to` (an egg id, or a depth in metres) |
| `macro` | close on one egg, a slow push, shallow focus: the payoff | `target` (an egg id; required), `amount` (0.10) |
| `hero` | low three-quarter, the sun behind the block, a slow arc (rays burst round the tree in front of the sun): the closing image | `deg` (8), `dir`, `az` (-46), `el` (3) |

Speed limits (CRAFT.md 4, measured on screen by the validator): a pan or crane at most 0.25 frames per second, a push at
most 10 % of the frame per second at the peak of the ease; twice that is an error. A crane over the full height of the
block needs about 6 s or more. Depth of field is on in `ground` and `macro` only.

### Words on screen (set in code)

| key | where | meaning |
| --- | --- | --- |
| `labels` | on a shot | `[{"text", "at", "until", "point", "slot"}]`: a small-caps label on a paper pill; `point` (an egg id, `"water"`, `"mill"`, `"house"`, `[x, y, z]`) draws a hairline leader to it that follows the camera. `slot`: `upper-left`, `upper-right`, `lower-left`, `lower-right`, `left`, `right`, `top`, `bottom`, or `[x, y]` pixels from the centre of a 1920x1080 (1080x1920) frame |
| `counter` | on a shot | `{"from", "to", "at", "done", "until", "caption", "suffix", "slot"}`: a number rolling up to `to` by `done` (`66000000` shows as 66,000,000) |
| `caption` | on a shot | `{"text", "at", "until"}`: a date or place in the top-left corner |

Rules: capitals (the engine upper-cases labels), at most about 4 words, no em or en dashes, no "...", no emoji; at most
two labels at once; two labels in the same place at the same time is an error; in a `ground` shot labels go in the upper
slots (the grass in front would hide low ones); nothing in the title card's place while it shows. Labels are clipped to
their shot.

## 5. Render cost (free) and what the validator estimates

Everything is free: Blender Cycles on the CPU of GitHub's runners for the public repo (rc-render `films.yml`, or the
director's `films-render.yml`, release `films`). The validator prints the estimate: seconds per frame for each shot from
the set's light, fog, water, eggs and the camera (close shots are cheaper), runner-hours, and minutes per part on the
parallel runners (a part may run 300 minutes; the validator refuses a plan over about 280).

Measured (free 4-core runners, 1280x720, 20 samples): see `docs/PLAYBOOKS/cutaway-film.md` (cost table, updated with
each run). Levers, in order: `fog: 0`, fewer samples (16 holds up with the denoiser), `time: "day"` instead of golden,
fewer houses lit at dusk, a shorter film.

## 6. Weak spots (honest)

- Sets are presets: a place the presets cannot say (a castle, a city like Venice, a mine with galleries) still needs a
  hand-built film on the kit (see `films/cutaway/venice/`). New presets are added here, in `presets.py` and `layout.py`.
- Animals and eggs are storybook-sized and made of primitives; they read at phone size, not as museum casts.
- One egg of each kind per set; eggs are not placed by meaning (a T. rex skull is not a real fossil site).
- Labels are pinned at their slot; the validator checks slots and the title card, not the picture behind them (the
  eyes stage does).
- Cost: golden light and especially fog are slow; a 90 s film is about 2,160 frames.
