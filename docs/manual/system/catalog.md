# The catalog: `studio-web/public/data/catalog.json`

One JSON file lists everything KINOFORGE has made (films), every style and Cutaway look, every workflow and the music
on hand. It is the contract between this manual and the studio OS (the web studio reads it). It is built by
`tools/catalog.py` from the repo plus a few static tables in that script, and never edited by hand.

## Inputs
- Tracked `film.json` files under `films/` (except `films/director/tests/`, the look boards `films/cutaway/looks/`, the
  board stills `films/styles/cutaway/stills/`, and folders starting with `_`).
- Director jobs `films/studio/<id>/brief.json` without a `film.json`; code ads `ads/<id>/ad.json`; prototypes `proto/<id>/`.
- Board images in `studio-web/public/looks/` (`<look>-470.jpg`, `<look>-830.jpg`, `seasons-<look>-<frame>.jpg`,
  `board-meadow-830.jpg`) and posters in `studio-web/public/posters/<id>.jpg`.
- Static tables in `tools/catalog.py`: release assets known to exist (`KINO_FILMS`, `KF_FILMS`, `KF_ADS`, `GALLERY`),
  per-film facts (`FILMS`: status, date, sound, made_with, summary; `VERDICTS`), styles (`HOUSE`, `LOOKS`), `WORKFLOWS`, `MUSIC`.

## Exact steps
1. A film was rendered, delivered or judged: edit its row in `FILMS` (status, date) and `VERDICTS` (Sam's words, dated),
   add its assets to `KINO_FILMS` or `KF_FILMS` (letters: `v` mp4, `p` preview, `o` poster, `s` sheet).
2. A new film folder: nothing to add for it to appear (it is found by its `film.json`); add a `FILMS` row for the
   summary, sound and status.
3. A new look board image: drop it in `studio-web/public/looks/` with the naming above; it is picked up.
4. `python3 tools/catalog.py` (prints the counts), then `python3 tools/catalog.py --check` (exit 0 when fresh).
5. Commit `tools/catalog.py` and `studio-web/public/data/catalog.json` with a LOG line.

## Schema (one line per field)
- `generated`: ISO time of the build (the only clock in the file; `SOURCE_DATE_EPOCH` is honoured).
- `films[]`: `id` (film.json id), `title`, `series`, `style` (`battle-map`, `kinetic`, `lantern-road`, `clay`, `cutaway`,
  `business`, or a prototype's name), `look` (null or a Cutaway look), `format` (`16:9` or `9:16`), `duration_s`,
  `folder`, `status` (`delivered`, `rendered`, `in-progress`, `draft`), `video` and `preview` (`{repo, release, name}` or
  null), `poster` (`/posters/<id>.jpg`, or a release asset, or null), `sound` (one line), `made_with` (list), `recipe`
  (`docs/manual/films/<id>.md`), `summary`, `verdict` (Sam's words or null), `date` (`YYYY-MM-DD`, UTC).
- `styles[]`: `id`, `name`, `family` (`house` or `cutaway-look`), `summary`, `best_for`, `engine` (path), `recipe`
  (`docs/manual/styles/<id>.md`), `board` (list of `/looks/<name>.jpg`, `/posters/<id>.jpg` or release assets), `start`
  (`{line, format, look}`: what "Start a film" passes to the director).
- `workflows[]`: `id`, `name`, `summary`, `doc` (`docs/manual/workflows/<page>.md`), `run` (how it is started).
- `music[]`: `id`, `title`, `source` (URL), `licence`, `asset`.

## Alternatives
`studio-web/lib/library.js` still has its own film lists (`KINO_FILMS`, `CUTAWAY_FILMS`) for the current Films page;
the studio OS rework moves to the catalog.

## Checks before showing Sam
`--check` passes; the counts printed match what you expect; every `video` you added exists in the release listing.

## Known traps
- The asset tables are static: a film rendered after the last edit is not shown as playable until its row is updated.
- The two Mac-lane series films (Reef and Wreck, The Gold Mine) are delivered to Sam's Mac but not in any release:
  their `video` is null.
- Recipe paths fall back to the expected name when the page is not yet written.

## Sources of truth
`tools/catalog.py` (the code wins), the release listings (`gh api repos/Eouchi147/<repo>/releases/tags/<tag>`).
