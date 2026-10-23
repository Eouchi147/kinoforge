# Render on Sam's Mac (the Mac lane)

Only for agents with Sam's Claude desktop connection (device tools and computer use). Other agents cannot reach the Mac:
render on GitHub instead. Measured 22 Oct: Venice at 1280x720, 24 samples, about 7.5 s per frame on the M4 GPU, about 7
GitHub runners' worth. Reference: `docs/WORKFLOWS.md` ("Render on Sam's Mac").

## Steps
1. **Ask before using the Mac** if Sam has not asked for it today. Keep it plugged in and awake; it has no fan, long runs slow down.
2. **Code copy:** the Mac renders from its own copy on Sam's external drive, `Samsung X5/KINOFORGE/render/` (harness,
   films/lib, films/styles, films/cutaway, ads/fonts); fallback `Video Production/kinoforge-render/` if the drive is
   unplugged. Refresh it from GitHub's tarball when the film or the kit changed.
3. **Start the lane** once per Blender launch: in Blender's Python console (computer use, Blender only), run the `exec(...)`
   line from `docs/WORKFLOWS.md`. It writes `mac-jobs/heartbeat.txt` every 10 s: check it is fresh.
4. **Queue a job:** write `{film, out, w, h, samples, start, end, device: "METAL"}` as a JSON file into
   the lane home's `mac-jobs/` (device file tools; committing a staged file works even when the Mac's shell is down).
   Split long films into frame ranges. Since 23 Oct, point `out` at Sam's external drive (absolute path,
   `/Volumes/Samsung X5/KINOFORGE/frames/<film-id>`; 816 GB free, the Mac's own disk had 13 GB): the session reaches it
   as the connected folder `Samsung X5`. Keep the iCloud folder for the code copy and the job files only.
5. **Watch:** the job's `.log`, then `mac-jobs/done/`. Frames land in `<out>/frames`. If the heartbeat is stale, Blender
   was restarted: start the lane again (step 3). Computer use cannot reach Blender while Sam is in a full-screen app.
6. **Encode and add sound** (ffmpeg on the Mac or in the container), then `check-before-showing-sam.md`. Deliver to
   `Video Production/kino-films/` and keep an archive copy in `Samsung X5/KINOFORGE/films/`.
7. **Log** the job, the time per frame and anything odd in `docs/LOG.md`.

## Definition of done
- The frame range is complete (count the frames), the log shows exit 0, the encoded film passed the checks, and the
  measurement is logged.
