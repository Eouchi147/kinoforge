# Lessons (studio-wide traps; one line each, phrased as a rule)

Technical and process lessons for everyone. The director's own lessons (written by `reflect.py`) are in
`films/director/LESSONS.md`; craft rules from Sam's verdicts are in `films/director/CRAFT.md` and `docs/SOUL.md`.
Add a line the day you hit a trap; if a lesson can be checked by code, add the check to `tools/verify.py` and say so here.

## Process
- Show a style board first; one look file for every piece made everything look the same (15 Oct).
- Fix the look, not the clip: an automatic "score and redo" loop doubled the cost when the look was the problem (15 Oct).
- Save every output to disk and upload it the moment it exists: a script crash once lost paid stills (15 Oct).
- Never claim a render, a fix or a delivery without evidence: the run id and conclusion, the asset in the release, the numbers from ffprobe.
- The chat container restarts and loses background watchers: anything that must happen later lives on GitHub (rc-render `chain.yml`), not in a session (22 Oct).
- Free models allow about 1,000 requests a day per key and few capable ones are live: run one director job at a time; keep repair prompts small (22 Oct).
- The picture spec is the weak stage of the free director; script and sound are fine on free models (22 Oct).
- Other agents push to `main` all the time: `git pull --rebase --autostash origin main` before every commit and push; commit only your own files (never `git add -A` in a shared checkout).

## GitHub and runners
- `gh workflow run` and `gh release download` use GraphQL, which some sessions block: dispatch and download through `gh api` (REST).
- `ref` for a cross-repo dispatch must be a branch or a FULL commit hash; a short hash fails the checkout.
- A new workflow file is registered only after a push that touches it; dispatching before gives 404.
- Playwright 1.56 does not install on `ubuntu-latest` (now 26.04): pin `runs-on: ubuntu-24.04` (gate `workflows` checks it; 22 Oct).
- Chatterbox needs `setuptools<81` in its env (resemble-perth imports `pkg_resources`) (22 Oct).
- Runner commits to `main` collide when jobs finish together: pull, rebase, push, with retries.
- One render part can hang for hours: watch the jobs, cancel and re-run only the failed jobs (22 Oct, Iqra part 11).
- The runner queue is shared: one stills run in flight per builder, at most 8 frames (22 Oct).

## Rendering
- ffmpeg `-movflags +faststart` writing straight to the Samsung X5 (exFAT) through the Mac's Linux mount wrote a broken mp4 (NAL errors). Encode to `$HOME` on that shell, then copy to the drive; check with ffprobe after copying.
- Cutaway art modules: `Eggs.finish` cuts the egg openings into the wall and water materials, so an art look that replaces them must keep the mask (`films/styles/cutaway/art/_jewel.py` `under_mask`). Overlay text is measured in the active view layer: keep the words indirect-only in the picture layer, not removed.
- Mac lane on the Samsung X5 (exFAT): macOS writes a `._name` file beside every file. Count frames with `ls frames/[0-9]*.png`, never `ls | wc -l`; a job's `end` frame is exclusive.
- ffmpeg: in a chain of `overlay` filters, `enable='between(n,a,b)'` on the second overlay does not see the main frame numbers (Agincourt insert B never showed). Enable by time (`between(t,(a-0.5)/fps,(b+0.5)/fps)`) and test with two inserts, not one.
- Every frame is a pure function of the frame index: no clocks, no unseeded randomness, no CSS transitions.
- Never measure a stage before its fonts load: an early `offsetWidth` read shifts glyph rasterization.
- Masked word reveals need at least 135 % travel or descenders peek out of the mask.
- A full haze volume in Blender fogs the whole frame: make god rays as light cards (22 Oct, Cutaway).
- Stars need their own pass with no depth of field, or they blur into blobs (22 Oct, Arabia).
- Constant screen speed over a big perspective change reads as sped up: plan moves in metres per second (22 Oct, Kleidion).
- Grain is incompressible: cap the bitrate (crf 20, max 14 Mbps) or masters reach 70 Mbps.
- Square stills fed to a 16:9 video model get pillarboxed: crop to the target aspect first.

## Sound
- ffmpeg: `xfade` shorter than about 0.22 s drops segments; trim on the input (`-ss`/`-t` before `-i`); always `-nostdin`.
- Beat trackers halve or double the tempo: check the grid (librosa with `start_bpm`) before timing cuts.
- Whisper words differ from the script: show the script's words, timed by alignment.
- Encode a mix to a temp file and verify it before replacing the old one: checkpoint commits once caught half-written mixes (22 Oct).
- Finished films get new sound with rc-render `remux.yml`; never re-render the picture for a sound change.

## AI models (paid models allowed inside a cap per film since 22 Oct 20:50, `docs/decisions/0013`)
- OpenRouter key `usage` lags by hours; per-call `usage.cost` is the reliable figure.
- Lyria returns audio only when streamed (`stream: true`); Seedream needs `modalities: ["image"]`.
- Video models warp crowds of small particles and people's hands; they hold one solid object well.
- 23 Oct 2026: VSCO-2 CE names most notes an octave below the sounding pitch; the score engine's YIN check copes for the instruments it uses but misreads Cello Section pizzT by 4 octaves. If cello pizz is ever used, pin its octave (+12) instead of trusting the check.
- 24 Oct 2026: a single 1560-frame Mac lane job (kids fossil) was killed with exit -9 after about 2 h at frame 734 (likely memory growth in one Blender process). Queue Mac lane renders as chunks of about 200 frames (one job file each); a fresh process also ran faster (7.2 s against 10 s a frame).
