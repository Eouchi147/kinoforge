# How to deliver to Sam

Sam sees work in three ways: a GitHub release link, a file on his Mac (`Video Production/kino-films/`, with an archive copy
on his Samsung X5 drive in `KINOFORGE/films/`), and the web studio's Films page. He reads on his phone, wants results and
numbers first, very few and very small decisions, and every weak spot named. Nothing is published, posted or sent to
anyone else without his explicit approval.

## Inputs
- A render that passed `quality-checks.md`.
- For the Mac: a session with Sam's Claude desktop connection (device file tools). Every other agent delivers the link.

## Exact steps
1. **Check first** (`quality-checks.md`). No exceptions.
2. **Name the file** `<series>-<id>[-<style>]-vN.mp4` for the Mac; a re-made film keeps the old file beside it and takes
   the next suffix (`-v2`, `-v3`). Examples in the record: `battle-map-agincourt-v2.mp4`,
   `dark-corners-kleidion-lantern-road-v2.mp4`, `under-the-surface-venice.mp4`, series films in `kino-films/series/`.
3. **Mac (desktop connection only):** download the asset into the container, then copy it with the device commit tool to
   `Video Production/kino-films/` (and `Samsung X5/KINOFORGE/films/` as the archive); list the folder on the device and
   compare the size with the release asset. Mac-lane films are encoded on the Mac and land there directly.
4. **Mac disconnected:** say so in one line, give the release link, and note the pending copy in `docs/STATUS.md`
   ("Waiting").
5. **Web studio:** a film in rc-render `kino-films` shows on the Films page when its id is in `KINO_FILMS` or
   `CUTAWAY_FILMS` (`studio-web/lib/library.js`); a film in kinoforge `films` shows by itself. Add the row to the
   catalog (`tools/catalog.py` tables: status `delivered`, the date), run `python3 tools/catalog.py`, commit the JSON.
6. **The message** (short, phone-first):
   - first line: what it is and that it is done, with the link or "on your Mac as `kino-films/<file>`";
   - the numbers: length, format, loudness, cost against the cap (or US$0);
   - weak spots in one or two lines, and what you would fix next;
   - at most one question, with your recommendation first.
7. **Log it:** `docs/LOG.md` ("on Sam's Mac as `kino-films/<file>`", run ids, numbers), `docs/STATUS.md`.

## Alternatives
- A private Claude page (artifact) for boards and comparisons (the look board, "Unmissed Ad Directions", "Restaurant Ad
  Looks" were pages). Use it when Sam must compare several items side by side.
- A Claude doc for long guides (the Cutaway guide "Cutaway: where to take it and how it earns").
- The release link alone, for any agent without the desktop connection.

## Checks before showing Sam
Every claim in the message is backed by evidence from this session (run id, asset listed with its size, ffprobe numbers,
a sheet you looked at). Never write "delivered" for a file you did not see land.

## Known traps
- The Mac has had about 13 to 14 GB free on its own disk: frames and archives go to the Samsung X5 drive, never the Mac's disk.
- The superseded v1 films stay in `Video Production/kino-films/` until Sam says otherwise (iCloud-only copies).
- Computer use cannot reach Blender (or start the lane) while Sam is in a full-screen app.
- Do not mark a film delivered in the catalog until the copy or the link has reached Sam.

## Sources of truth
`docs/PLAYBOOKS/deliver-to-sams-mac.md`, `docs/SOUL.md` section 6, `AGENTS.md` (how to work), `docs/STATUS.md` (drive
and Mac notes), `studio-web/lib/library.js`, `tools/catalog.py`.
