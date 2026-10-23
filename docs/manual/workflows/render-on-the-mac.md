# Render on Sam's Mac (the Mac lane)

Blender films rendered on Sam's MacBook Air (M4, 10-core GPU through Metal) by a job watcher that runs inside the Blender
5.2 app. The lane's home is Sam's external drive `Samsung X5` (1.9 TB, about 815 GB free on 23 Oct): code copy and job
folder in `KINOFORGE/render/`, frames in `KINOFORGE/frames/`, an archive of every finished film in `KINOFORGE/films/`.
Free and about 7 times one GitHub runner. Only a session with Sam's Claude desktop connection (device file tools and
computer use) can use it. Made this way: Reef and Wreck, The Gold Mine, the meadow film, the 12-look board.

## Inputs
- The film folder pushed to GitHub (the lane renders from its own code copy, refreshed from GitHub's tarball).
- Sam's agreement to use the Mac today (ask once if he has not asked for it), the Mac plugged in and awake.

## Exact steps
1. **Ask before using the Mac** if Sam has not asked for it today.
2. **Is the lane alive?** Read `KINOFORGE/render/mac-jobs/heartbeat.txt` on the drive (device tools; the session sees
   the drive as the connected folder `Samsung X5`). It is rewritten every 10 s with the time and `gen N`. Stale means
   Blender was restarted: go to step 3; fresh: go to step 4.
3. **Start the lane** (computer use, Blender only): in Blender's Python console type
   `exec(open('/Volumes/Samsung X5/KINOFORGE/render/harness/mac/go.py').read())` and press Return. It prints
   `KINOFORGE Mac lane (gen N) started`. Running it again stops the older thread (generation counter). Fallback when the
   drive is unplugged: `exec(open('/Users/sam/Desktop/Projects/AI tools/Video Production/kinoforge-render/harness/mac/go.py').read())`
   (iCloud folder, file locks, little disk). Computer use cannot reach Blender while Sam is in a full-screen app.
4. **Refresh the code copy** when the film or the kit changed: drop a sync job, named to run first:
   `0-sync.json` = `{"kind": "sync", "ref": "main", "paths": ["harness", "films/lib", "films/styles", "films/cutaway", "ads/fonts"]}`
   (curl and tar of `codeload.github.com/Eouchi147/kinoforge/tar.gz/<ref>`; public, no credentials). Add other paths
   (for example `films/battles`) if your film lives elsewhere.
5. **Queue render jobs:** one JSON file per frame range in `KINOFORGE/render/mac-jobs/`, written with the device file
   tools (committing a staged file works even when the Mac's shell is down):
   ```json
   {"film": "films/cutaway/meadow", "out": "/Volumes/Samsung X5/KINOFORGE/frames/cutaway-line-meadow",
    "w": 1280, "h": 720, "samples": 20, "start": 0, "end": 96, "device": "METAL"}
   ```
   `end` is exclusive. Jobs run one at a time in file-name order: name checks `0-<name>.json` and film chunks `5-<film>-c00.json`,
   `5-<film>-c01.json` (the meadow was 10 jobs `5-meadow-c00` to `c09` for 959 frames). Each runs under `caffeinate -i`.
6. **Watch:** the job's `.log` beside it while it runs (the command line, then `exit 0 after N s`); finished jobs and
   logs move to `mac-jobs/done/`; errors of the watcher itself go to `mac-jobs/lane-error.txt`. Frames land in
   `<out>/frames/NNNNN.png`. Count them with `ls <out>/frames/[0-9]*.png | wc -l` (never `ls | wc -l`: macOS writes `._`
   twins on the exFAT drive).
7. **Encode and add the sound** on the Mac or in the container, with the same settings as rc-render's join
   (`render-film-on-runners.md`, "What the join does"): frames to `libx264 -crf 17 -preset slow -pix_fmt yuv420p`, scale
   to `w x h`, the folder's `audio/mix.m4a` as AAC 256k, `-shortest -movflags +faststart`; a preview and a sheet. (The
   exact commands used for the Mac-lane series films are not recorded; these are the runner's.)
8. **Check** (`../system/quality-checks.md`), **deliver** to `Video Production/kino-films/` and archive in
   `Samsung X5/KINOFORGE/films/`. Log the job names, seconds per frame and anything odd in `docs/LOG.md`.

## Measured
| Film | Size, samples | Seconds a frame |
| --- | --- | --- |
| Venice frames 1000 to 1019 (22 Oct) | 1280x720, 24 | about 7.5 |
| Meadow, 959 frames (23 Oct) | 1280x720, 20 | about 6.5 (about 1 h 45 min) |
| Gold Mine, 480 frames | 720x1280, 20 | about 5 |
| River Through Time | 1280x720, 20 | 3 to 5 on an idle Mac |
| Look board frames (12 looks) | full size | about 10 to 60 per frame by look; reference about 15 |
| Drive test frame (Sleeping Volcano) | | 4.7 |
The fanless Mac heat-throttles from about 5 to 13 s a frame after an hour of rendering.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| rc-render `films.yml` | Mac not connected, Sam in a full-screen app, or to spread load (River went to runners) | free, about 7 times slower per frame |
| Split: Mac for some films, runners for others | overnight batches (the series) | free |

## Checks before showing Sam
Frame count equals `end - start` for every job; every log ends `exit 0`; the encoded film passes `quality-checks.md`.

## Known traps
- `end` is exclusive.
- `._` files on the exFAT drive: count frames by pattern.
- The Mac's own disk had about 13 GB free: frames go to the drive (absolute `out` path), never to the Mac's disk or iCloud.
- The lane reads its own code copy: a change pushed to GitHub is not seen until a sync job runs.
- An older lane thread from the same Blender session watched `mac-queue/`; the current lane watches `mac-jobs/`.
- A request for folders outside the connected ones can be refused by the safety check (22 Oct, `~/Movies`).

## Sources of truth
`harness/mac/go.py` (the code wins), `harness/blender_render.py` (`--device METAL`), `docs/PLAYBOOKS/render-on-the-mac.md`,
`docs/WORKFLOWS.md` ("Render on Sam's Mac"), `docs/STATUS.md` (drive), `docs/LESSONS.md` (Rendering).
