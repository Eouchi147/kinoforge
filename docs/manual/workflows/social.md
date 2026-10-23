# Social videos (kinoforge `social.yml`) (lane paused)

Renders a batch of 9:16 phone videos (TikTok, Reels, Shorts, Facebook Reels) from code templates, one runner per video:
captions built in code, a safe-zone check on every frame, the render (`harness/dom-render.cjs`, 1080x1920, 30 fps), the
mix (-14 LUFS, or a silent track) and the cover; uploads `<client>-<batch>-<id>.mp4`, `-cover.jpg`, `-captions.json` to
kinoforge release `social`. Nothing is posted by the lane. **Paused:** Sam stopped Smart Mount's videos on 16 Oct 17:32
Toronto ("not good, especially because the photo you used is a bad job photo"); do not dispatch until he restarts it.
Nothing has been rendered on GitHub. Templates: `card-motion` (A), `bento` (B), `type-motion` (C). Everything:
`social/README.md`.

## Inputs
| Input | Meaning |
| --- | --- |
| `batch` | folder under `social/batches/`, e.g. `smartmount/2026-12`, holding `batch.json` (`client`, `batch`, `render.sub`, optional `music` with `enabled, prompt, cap_usd, gain_db, offset_s`, `videos` with `id, template, card {eyebrow, title, body, fact, photo}, platforms`, optional `figure`) |
| `only` | optional comma list of video ids |

## Exact steps (when Sam restarts the lane)
1. New look first: a style board of free stills, Sam picks (0008). Imagery with no rights doubt: made in code, licence-free
   stock, or AI with each platform's AI label. The photos in `social/clients/smartmount/media/` are do-not-use.
2. Check locally: `node social/lib/check.mjs social/batches/<client>/<batch>`; stills
   `node harness/dom-render.cjs social/templates/<t> --w 1080 --h 1920 --stills 0.5,3,7 --stills-only --param brief=/social/batches/<client>/<batch>/batch.json --param id=<video id>`
   (`--param guides=1` shows the platform zones); `node social/lib/safecheck.mjs social/templates/<t>`.
3. Sam approves the look and the batch.
4. Dispatch: `gh api -X POST repos/Eouchi147/kinoforge/actions/workflows/social.yml/dispatches -f ref=main -f 'inputs[batch]=<client>/<batch>'`.
5. Download from release `social`; check every video; Sam approves before anything is posted.

## Cost
Pictures free; optional music once per batch (Lyria, about US$0.04 to 0.08, capped in `batch.json`); runner time about
3 to 5 min per video (40 to 60 job-minutes for 12).

## Alternatives
Cutaway in 9:16 (the drainage ad `v916`, the seasons loop) for trade businesses; code ads (`ads.md`).

## Checks before showing Sam
Every word, number, URL and logo mark inside rule R-2-08's box (x 0.11 to 0.78, y 0.15 to 0.65; one constant `SAFE` in
`social/lib/brief.mjs`); claims only in the client's own words; captions with the AI disclosure where needed.

## Known traps
- Nothing for Smart Mount while smartmount.ca is parked (smartmount `api/_parked.js`).
- Never measure the stage before fonts load (glyph shifts); `fitStage()` scales uniformly and letterboxes.

## Sources of truth
`.github/workflows/social.yml`, `social/README.md`, `social/lib/`, `docs/WORKFLOWS.md` ("social.yml"), `docs/STATUS.md` (Waiting on Sam).
