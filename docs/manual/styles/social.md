# Style: social videos (9:16 templates, the social lane)

The social lane makes short phone-format videos (TikTok, Instagram Reels, YouTube Shorts, Facebook Reels) from code
templates: real photos, the client's words, numbers and logo set in code, rendered frame by frame in Chromium at 1080x1920,
30 fps. It is how Unmissed's Social Autopilot (12 videos a month per client) would be made. Three looks exist as templates
(`social/templates/card-motion`, `bento`, `type-motion`) with a first batch for Smart Mount (`social/batches/smartmount/2026-12`,
12 videos). **Status: stopped by Sam on 16 Oct 2026 (17:32 Toronto)** after he watched the local check videos: the install
photo used showed weak workmanship; he wants imagery with no copyright problem (made in code, licence-free, or AI with the
platform label) and "a clean professional look on everything". Nothing was rendered on GitHub, nothing posted, US$0 spent.
Do not dispatch `social.yml` until Sam restarts the lane.

## Inputs
- A batch file `social/batches/<client>/<batch>/batch.json`: `client`, `batch`, `render` (`w` 1080, `h` 1920, `fps` 30,
  `sub` = motion-blur sub-frames, 2), optional `music` (`enabled`, `prompt`, `cap_usd`, `gain_db`, `offset_s`), and `videos`
  (`id`, `template`, `card` with `eyebrow`, `title` about 34 characters, `body` about 90, `fact` as `[number, words]`,
  `photo`, `platforms`, optional `figure`, `caption_fact`, `hashtags`, `cover_s`, `music_offset_s`).
- A client kit `social/clients/<client>/`: `brand.json` (name, site, area, colours, fonts, logo, mark assembly, hashtags,
  caption lines), the logo, `media/` (photos with `media.json`: each photo's TV or subject box). Only cleared material in the
  public repo; Smart Mount's install photos are now marked do-not-use.
- Fonts: Inter and Inter Tight (`social/fonts/`, SIL OFL), JetBrains Mono (`ads/fonts/`).

## The three looks (style board of 16 Oct, same content: the tip "Your TV is too high.")
| Template | Look | What it is | Length |
| --- | --- | --- | --- |
| `card-motion` | A, Card in motion | the client's own social card brought to life: photo band pushing in, eyebrow, title words rising, body, the fact counting up, the footer, the panel rising into the end card; words in the middle band, the bottom 35 % quiet navy | 12.4 s |
| `bento` | B, Bento | Unmissed's Bento language in the client's colours: opens on the title tile, pulls back to the grid, glides to the real photo, the fact with a measured figure, Book online, collapses into the mark; each close-up's zoom computed so the tile's words fit the safe box | 14.4 s (cover at 1.2 s) |
| `type-motion` | C, Type in Motion | big kinetic type over the full-bleed real photo (TV high, type in the lower half of the safe box), a line through the centre, the fact as one giant number, a brand-blue end card | 13.6 s |
Every end card: the mark assembles itself (ground, wall plate and arm, the screen hooks on), the site, the area. Sam asked
for a mix of the three on 16 Oct (B for v01, v05, v08, v12; A for v02, v04, v06, v10; C for v03, v07, v09, v11).

## Exact steps
1. Batch check (free, seconds, no browser): `node social/lib/check.mjs social/batches/<client>/<batch>` (templates,
   photos, house style, card copy limits, captions per platform). Tests: `node --test social/lib/social.test.mjs`.
2. Stills (free): `node harness/dom-render.cjs social/templates/<t> --w 1080 --h 1920 --stills 0.5,3,7 --stills-only --param brief=/social/batches/<client>/<batch>/batch.json --param id=<video id>`
   (`--param guides=1` shows the platform zones in red). A silent check video: drop `--stills-only`, use `--w 540 --h 960`.
3. Safe zones (free, every frame): `node social/lib/safecheck.mjs social/templates/<t> --brief /social/batches/<client>/<batch>/batch.json --id <video id>`.
   Fails if any word, number, URL or logo mark (tagged `data-safe="mark"`) leaves the box x 0.11 to 0.78, y 0.15 to 0.65
   (rule R-2-08; one constant `SAFE` in `social/lib/brief.mjs` feeds templates, the check and the review mask).
4. Render on GitHub only after Sam approves the look and the batch: workflow `social.yml` (input `batch`, optional `only` =
   comma list of ids). One runner per video: captions in code (`social/lib/captions.mjs`, no AI, the hook first), the
   safe-zone check, the render, the mix (`harness/shots/social.py finish`: -14 LUFS, or a silent track), the cover. Music
   (optional, one Lyria clip per batch, about US$0.04 to 0.08, cap in `batch.json`) is made once by the plan job and committed
   with `ledger.json`. Output in release `social`: `<client>-<batch>-<id>.mp4`, `-cover.jpg`, `-captions.json`.
5. Posting gate: nothing is posted by the lane; nothing before Sam approves the batch; nothing for Smart Mount while
   smartmount.ca is parked (smartmount repo `api/_parked.js`, `PARKED = true` since 13 Oct 2026).

## Template contract
Fixed 1080x1920 stage; `window.KF = { duration, fps: 30, cover, render(i, t) }`; every style a pure function of `t`;
`window.KF_READY = true` when ready; `window.KF_ERROR` on a bad brief; files `index.html`, `template.json` (length, cover
moment), `sample.json`.

## Alternatives
| Route | When |
| --- | --- |
| Imagery made in code or Blender (a Cutaway trade ad, a style made in code) | Sam's 16 Oct verdict: no real photo with weak work or doubtful rights |
| AI stills with the platform's AI label (`board.yml`) | only after Sam's go per job (paid) |
| Business ad pipeline (`business-ads.md`) | 16:9 brand films |

## Checks before showing Sam
- Every frame inside the safe box (`safecheck.mjs` passes); captions per platform within limits; house style.
- The photo shows clean, professional work and has clear rights; nothing a tradesperson would fault.
- Words only from the brief and `brand.json`; no prices, ratings, counts, results or claims on screen; tips are the client's
  own correct advice (three bodies were corrected on 16 Oct: v07 104 inches about 8.7 feet, v10 TruMotion is LG's name only,
  v11 renters usually need the landlord's OK).

## Known traps
- Never use the smartmount repo's `hero-*.webp` (they may be AI images).
- `fitStage()` must not measure the stage before fonts load.
- The safe zone was first written as 10/20/12 % zones; rule R-2-08 replaced them (16 Oct): use the one constant.

## Sources of truth
`social/README.md`, `social/lib/*.mjs`, `social/templates/*/`, `social/batches/smartmount/2026-12/batch.json`,
`.github/workflows/social.yml`, `harness/shots/social.py`, `docs/WORKFLOWS.md` (social), `docs/STATUS.md` (Waiting on Sam),
`docs/SOUL.md` section 3.
