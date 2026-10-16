# Social lane: phone-format (9:16) videos from code templates

Short videos for TikTok, Instagram Reels, YouTube Shorts and Facebook Reels, built in code: real photos, words, numbers
and logos set in code, rendered frame by frame in Chromium (`harness/dom-render.cjs`). No AI pictures, no AI words, no
fees except an optional music clip. This is how Unmissed's Social Autopilot (12 videos a month per client) gets made.

## How a video is made
1. **Brief**: one entry of a batch, `social/batches/<client>/<batch>/batch.json`: `id`, `template`, `card` (eyebrow,
   title, body, fact as `[number, words]`), `photo` (a file in the client's `media/`), `platforms`; optional `figure`
   (`"height"` draws the measured eye-level figure), `caption_fact`, `hashtags`, `cover_s`, `music_offset_s`.
2. **Check** (free, seconds): `node social/lib/check.mjs social/batches/<client>/<batch>`: templates, photos, house style
   (no em or en dash, no "..."), the card copy limits (title about 34 characters, body about 90), captions per platform.
3. **Look at it** locally (free): `node harness/dom-render.cjs social/templates/<template> --w 1080 --h 1920 --stills 0.5,3,7
   --stills-only --param brief=/social/batches/<client>/<batch>/batch.json --param id=<video id>`; add `--param guides=1`
   to see the platform zones in red. A silent check video: drop `--stills-only`, use `--w 540 --h 960`.
4. **Safe zones** (free): `node social/lib/safecheck.mjs social/templates/<template> --brief /social/batches/<client>/<batch>/batch.json --id <video id>`
   steps through the video and fails if any visible word enters the top 10%, the bottom 20% or the right 12% of the frame.
5. **Render the batch** on GitHub: workflow `social.yml` (input `batch`, optional `only`). Outputs in the release `social`:
   `<client>-<batch>-<id>.mp4` (1080x1920, 30 fps, -14 LUFS), `-cover.jpg`, `-captions.json`. Nothing is posted:
   Sam approves every video first.

## The three looks (style board of 16 Oct 2026, same content: card tip-height)
| Template | Look | What it is | Length |
| --- | --- | --- | --- |
| `card-motion` | A, Card in motion | The client's own social card brought to life: photo band pushing in, eyebrow, title words rising, body, the fact counting up, the card's footer, the panel rising into the end card | 12.4 s |
| `bento` | B, Bento | Unmissed's Bento language in the client's colours: a camera gliding across tiles (title, real photo, fact with a measured figure, Book online), collapsing into the mark | 14.0 s |
| `type-motion` | C, Type in Motion | Big kinetic type over the full-bleed real photo, a line through the centre of the screen, the fact as one giant number, a brand-blue end card | 13.6 s |
Every end card: the mark assembles itself (ground, wall plate and arm, the screen hooks on), the site, the area.

## Files
| Path | What it is |
| --- | --- |
| `lib/brief.mjs` | Pure rules shared by pages and tools: safe zone, house style, brief resolution, the counting fact |
| `lib/stage.js`, `lib/stage.css` | The 9:16 stage: loads brief, brand, fonts, photo; photo framing on the TV; masked words and lines; fitting; the mark assembly; the visible-text probe |
| `lib/captions.mjs` | Captions per platform from the brief, in code, with the limits table |
| `lib/check.mjs`, `lib/safecheck.mjs` | Batch check (no browser) and safe-zone check (browser, no screenshots) |
| `lib/social.test.mjs` | Tests of the pure rules: `node --test social/lib/social.test.mjs` |
| `templates/<t>/` | `index.html` (the scene), `template.json` (length, cover moment), `sample.json` (tip-height) |
| `clients/<client>/` | `brand.json` (name, site, area, colours, fonts, logo, mark assembly, hashtags, caption lines), the logo, `media/` (real photos and `media.json` with each TV's box) |
| `batches/<client>/<batch>/` | `batch.json`; after a run: `audio/music.mp3`, `ledger.json` (paid calls and render records) |
| `fonts/` | Inter and Inter Tight (SIL OFL, licences included); JetBrains Mono is in `ads/fonts/` |
| `../harness/shots/social.py` | Music once per batch (cap), mix to -14 LUFS, cover, ledger |

## Rules (from AGENTS.md and Sam)
- Real photos only (never `hero-*.webp` from the smartmount repo: they may be AI images). Words only from the brief and
  brand.json. No prices, ratings, counts, results or claims on screen. Tips must be the client's own, correct advice.
- A new client needs `clients/<client>/brand.json`, its logo and photos with TV (or subject) boxes. The public repo holds
  only cleared material (Smart Mount is cleared); other clients wait for private storage.
- Template contract: fixed 1080x1920 stage, `window.KF = { duration, fps: 30, cover, render(i, t) }`, every style a pure
  function of `t`, `window.KF_READY = true` when ready, `window.KF_ERROR` on a bad brief. Words never leave the safe box.
