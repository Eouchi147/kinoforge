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
- A start line that stops an earlier run must match that run's own path (`pkill -f "<pack>/mac/run.sh"`), never a shared script name: a test with `pkill -f blender_render.py` killed an unrelated render in the same session. Test such a line through `bash -s`: inside `bash -c '...'` the pattern also matches the test shell and kills it silently (24 Nov).
- Other agents push to `main` all the time: `git pull --rebase --autostash origin main` before every commit and push; commit only your own files (never `git add -A` in a shared checkout).
- Free original sound effects need no licence: a heartbeat (two low decaying thumps with a falling pitch and a few harmonics) and a released balloon (a buzzy, falling, wobbling tone) synthesized in numpy both read on a tablet speaker (24 Nov).
- Birdsong, wingbeats and a soft far-off boom also synthesize well: a tweet is two quick up-and-down sine sweeps around 4 kHz with a fast trill; wings are band-limited noise in bursts at the wingbeat rate; a boom needs harmonics above 100 Hz or a tablet speaker plays nothing (24 Nov).

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
- A session cannot grant itself access to a folder on the Mac (the folder request is refused from the session side): as soon as the Mac shows up, ask the owner in one line to add the drive in the Claude desktop app (+, Add folder) (24 Nov).
- The Mac's `device_bash` is a Linux VM, not macOS: it cannot run Blender with Metal. Start Mac renders from Blender's Python console (`go.py`) or the macOS Terminal; a Terminal line can wait for its files first: `until [ -f <file> ]; do sleep 15; done; <command>` (24 Nov).
- ffmpeg: in a chain of `overlay` filters, `enable='between(n,a,b)'` on the second overlay does not see the main frame numbers (Agincourt insert B never showed). Enable by time (`between(t,(a-0.5)/fps,(b+0.5)/fps)`) and test with two inserts, not one.
- Every frame is a pure function of the frame index: no clocks, no unseeded randomness, no CSS transitions.
- Never measure a stage before its fonts load: an early `offsetWidth` read shifts glyph rasterization.
- Masked word reveals need at least 135 % travel or descenders peek out of the mask.
- A full haze volume in Blender fogs the whole frame: make god rays as light cards (22 Oct, Cutaway).
- Stars need their own pass with no depth of field, or they blur into blobs (22 Oct, Arabia).
- Constant screen speed over a big perspective change reads as sped up: plan moves in metres per second (22 Oct, Kleidion).
- Grain is incompressible: cap the bitrate (crf 20, max 14 Mbps) or masters reach 70 Mbps.
- Square stills fed to a 16:9 video model get pillarboxed: crop to the target aspect first.
- A jump scan cut with a tiny camera move (about 0.005 to 0.02 units) and a small turn (under about 20 degrees) is a jump cut: the same subject from nearly the same place. Make it one smooth move from where the last shot ended, or a real change of size or angle (24 Nov).
- Contact sheets at 384x216 can turn a small open mouth into what looks like a moustache: look at the face at 960x540 before changing anything (24 Nov).

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
- Cycles: anything inside a refractive glass tube renders black (shadow rays do not pass refraction without caustics). For clear tubes mix a Transparent BSDF with a Glossy BSDF by Fresnel (24 Nov).
- A parked object must also be shrunk or hidden: a unit-sphere mesh parked at z = -1 still filled the room and swallowed the camera, and every frame came out black (24 Nov).
- Never let a render depend on Python `hash()`: it is randomised per process, so chunked renders disagree with each other; use a fixed checksum such as `sum(map(ord, name))` (24 Nov).
- A Workbench animatic of a whole 3 min film renders in well under an hour on two CPU cores and catches camera drift and framing errors before a multi-hour Cycles render; review it as contact sheets every 1.5 s (24 Nov).
- Blender: `hide_render` on a parent does not hide its children; hide each one (`children_recursive`), or lashes and wheels stay floating in the shot (24 Nov).
- A Solidify shell with offset 0 grows outward by half its thickness: discs or decals placed on the original surface (an iris, a pupil) end up under the shell; push them out by half the thickness plus a margin (24 Nov).
- A cutaway part that slides toward the camera blocks the very view it should open: lift parts up and away, and check the opened shot from the camera's own position (24 Nov).
- A pinhole (camera obscura) picture is far too dim to render at 16 samples: fake it with an emissive picture on the wall that fades in, and show the light path with glowing beads that cross at the hole (24 Nov).
- A jug tipped past 90 degrees points its mouth into the ground; a pour reads at about 75 degrees with the drops falling forward (24 Nov).
- A two-axis shoulder can twist without changing old poses: set the shoulder empty to ZXY Euler and put the twist in Z; with zero twist the matrix equals the old XYZ one (24 Nov).
- Amiri Quran draws Uthmani stop marks (small high jeem, ligatures) about a line above their word: give two-row verse cards about 1.3 lines of spacing, or use one row when it fits, or the mark lands on the line above (24 Nov).
- Under the AgX view transform an emissive gold or orange at strength 2 to 3 renders cream white: keep emission under about 1 and the base colour deep (gold 1.0, 0.48, 0.02) when the colour must read (24 Nov).
- A thin marker traced along a limb hides inside the limb's own tube: offset it toward the camera by more than the limb's radius (24 Nov).
- Walk cycles of the form sin(t x frequency) jump when the frequency changes mid-shot (the phase leaps): keep the frequency fixed and fade the swing amplitude in and out instead (24 Nov).
- Keep a clear circle around every camera path, not only a cone in front of it: a slow 3 cm drift took a camera into a scattered tree and every frame rendered black (24 Nov).
- Two shots in a row with nearly the same framing read as a jump cut: glide between them; a jump scan that lists a cut with a camera move of a few cm and a small turn has found one (24 Nov).
- A low, flat band of white clouds along a far shore reads as snow, not mist: leave haze to the sky colours (24 Nov).
- Before dispatching a board, read the key's balance in the last `account.json` (`after.remaining`): OpenRouter refuses image output with error 402 below US$1.00 of balance, so frames stop mid-board with nothing to show for them. Size the board to the balance, or ask the owner to raise the limit first (25 Nov).
- A board's charge is its `ledger.json` total, checked against the meter at the start of the next run. "board spent" in `board.log` is the account meter after minus before, read while charges are still posting: it under-reported every website-library run from v8 to v20 (26 Nov).
