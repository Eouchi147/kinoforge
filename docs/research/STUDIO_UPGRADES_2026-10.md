# Studio upgrades: the studio OS and production quality (research, 23 Oct 2026)

Question (Sam, 23 Oct 2026, via the coordinator's brief `os.md`): which tools and ways of working would upgrade KINOFORGE
greatly, in two parts: (1) the studio OS web app, (2) production (render, motion, sound, quality control, ways of working).
Everything is for a one-person studio run by AI agents, free or nearly free, within the public-repo rules (`docs/decisions/0009`).

**How to read this.** Confidence: high = read on the primary page or measured here; medium = one good secondary page, or reasoned
from a primary page; low = search summary, memory, or a guess (labelled "assumption"). Each source says what was done: OPENED
(page fetched and read), RAW (file read from raw.githubusercontent.com), MEASURED (run in this session), SEARCH-ONLY (search
snippet, page not read), BLOCKED (could not fetch). Effort is my estimate in agent-hours, not a measurement. Items that need a
lawyer or accountant are collected in section C.

## 0. Findings that change decisions (read these first)

1. **The Vercel Hobby plan can lock Sam out of deploying his own OS.** The repo had 317 commits on 22 Oct 2026 and 36 so far on
   23 Oct (`git log`, MEASURED). Hobby allows 100 deployments per day and 100 builds per hour, and says "you will need to wait
   another day before you can deploy again" ([Vercel limits](https://vercel.com/docs/limits), OPENED, high). AGENTS.md says Vercel
   "redeploys on every push to main". No `vercel.json` or `ignoreCommand` exists in the repo (MEASURED); whether the dashboard has an
   "Ignored Build Step" is unknown. The OS's own review route also commits to `main` for every note
   (`studio-web/app/api/review/route.js`), which adds deploys. Fix first: U1.
2. **Hobby is for non-commercial personal use only**, and "commercial" covers any deployment used for the financial gain of anyone
   involved in any part of production ([Fair use guidelines](https://vercel.com/docs/limits/fair-use-guidelines), OPENED, high).
   Unmissed is a marketing agency and the OS runs its content engine. It likely needs Pro once money flows. Flag: section C.
3. **EEVEE on the free runners is not an upgrade.** Measured here (no GPU, 2 vCPU, bpy 5.2.2): EEVEE falls back to software GL, works,
   and is not faster than Cycles CPU (P1). Keep Cycles. Also: the engine id `BLENDER_EEVEE_NEXT` in the usage text of
   `harness/blender_render.py` is **rejected by Blender 5.2.2** (MEASURED); the id is `BLENDER_EEVEE`.
4. **Most sound and QC primitives already exist in the repo** (sidechain ducking in `films/lib/battle_mix.py`, own ducking and
   -14 LUFS in `films/lib/score/remix.py`, ebur128, freezedetect and blackdetect in `docs/PLAYBOOKS/check-before-showing-sam.md`,
   librosa in `harness/shots/prep.py`). The gap is that QC is a manual playbook, not a gate that writes a report, and two checks that
   match Sam's verdicts (no unplanned cuts, loop seam) do not exist.
5. **The OS builder already shipped a first version** (working tree 23 Oct): a command bar that reads plain words
   (`lib/commands.mjs`, `components/os/Palette.jsx`), Desk, Library with timecoded notes, Create, Styles with side-by-side compare,
   Jobs with stages, Sound, Manual, Settings, passcode gate. So Part 1 is a gap analysis against the best tools, not a blank sheet.
6. **Licence traps found:** madmom's trained models are CC BY-NC-SA 4.0 (non-commercial); tldraw's licence forbids production use
   without a licence key; Kitsu is AGPL-3.0; Theatre.js Studio is AGPL-3.0 (its core is Apache-2.0); Vidstack is in security-only
   maintenance. Details below.
7. **VMAF got new "v1" models in June 2026** ([Netflix/vmaf README](https://raw.githubusercontent.com/Netflix/vmaf/master/README.md),
   RAW, high). The Ubuntu ffmpeg 6.1.1 on this box has **no libvmaf** (MEASURED), so VMAF needs another ffmpeg build.

---

## Part 1. The studio OS

### 1.1 What the best tools do, and what fits a one-person, AI-run studio

| Tool and pattern | What it does (source) | Fit here | Take |
| --- | --- | --- | --- |
| **Frame.io**: comments pinned to a frame, version compare, approval stages, review links | "Click directly on frames to add time-stamped feedback"; split-view compare of two versions; custom approval stages; watermarked password-protected review links; free plan 2 users and 2 GB; paid from $15/user/month billed annually ([third-party review](https://thedigitalprojectmanager.com/tools/frame-io-review/), OPENED, medium: not Frame.io's own page) | High for frame notes and compare. Skip stages and links (one reviewer) | Frame-pinned notes, A/B compare, a verdict per version |
| **Kitsu (CGWire)**: status-driven review | Artist sets status WFA; reviewer opens it, draws on the frame (pencil, text), comments with `@frame` that jump to that frame, compares two versions side by side, then sets Retake (request changes) or Done (approve); playlists of latest versions with frame-by-frame, loop, waveforms; export zip, CSV, MP4 ([Kitsu review docs](https://kitsu.cg-wire.com/review/), OPENED, high) | Best model for approve / request changes. Our agents are the "artists": a finished render sets WFA by itself | Copy the status words. Do not self-host Kitsu: AGPL-3.0 ([LICENSE](https://raw.githubusercontent.com/cgwire/kitsu/master/LICENSE), RAW, high) and a server stack (assumption) |
| **Flow Production Tracking (ShotGrid), ftrack**: entity model | Project contains Sequence, Asset, Shot; Task belongs to a Shot or Asset; Version = submitted work; Note = feedback on a parent; Seasons contain Episodes ([Autodesk entity unit](https://www.autodesk.com/learn/ondemand/module/working-with-entities-and-entity-pages-in-flow-production-tracking/unit/7CskJ6bNNkZEmiJWofju5P), OPENED, high). ftrack: no page opened (SEARCH-ONLY, low) | The nouns map cleanly: Series -> Film -> Scene (spec) -> Job -> Render version -> Note | Reuse the nouns; `catalog.json` and `films/reviews/*.json` already hold them |
| **Linear**: command menu, keyboard-first | Cmd/Ctrl+K opens the command menu to open pages or run actions; `/` searches; G then a letter jumps (G I = Inbox); `?` lists shortcuts ([Linear guide](https://linear.app/enablement/guide/navigating-linear), OPENED, high) | High: Sam works from a phone and a Mac; the bar already reads plain words | Add G-then-letter jumps, `?` help, contextual verbs (U6) |
| **Runway Workflows, Pika-style flows** | Node graph with input nodes, media-model nodes and LLM nodes; links pass data; run all or one node; reusable templates ([AlternativeTo news](https://alternativeto.net/news/2025/10/runway-launches-node-based-workflows-for-building-custom-ai-creative-pipelines), OPENED, medium: no date on page; limited to Creative Partners and Enterprise) | A node canvas is too much for a fixed pipeline run by one person. A linear recipe stepper with a cost line fits | Keep Create a stepper; show looks in motion and the cap before "Build" (U9) |
| **Notion-like docs** | Blocks, slash menu | Sam wants to "write, click and see options in the page", not a block editor; the Manual app already renders markdown | A plain "Note to the studio" box that commits a file agents read (U8) |

### 1.2 Open-source building blocks (Next.js on the Vercel free tier)

| Block | Licence | What for | Notes | Source |
| --- | --- | --- | --- | --- |
| Native `<video>` + `requestVideoFrameCallback` | Web standard | Frame readout: the callback gets `mediaTime` (the frame's presentation timestamp), `presentedFrames`, `expectedDisplayTime`. Chrome 83, Safari 15.4, Firefox 132. The video element does not guarantee frame-accurate seeking; WebCodecs is the exact route | zero dependencies | [web.dev rVFC](https://web.dev/articles/requestvideoframecallback-rvfc), OPENED, high (MDN page BLOCKED by the egress proxy) |
| Video.js v10 (Media Chrome, Plyr and Vidstack teams merged in) | Apache-2.0 | Player chrome with React components, only if the native element is not enough | "Video.js v10 is stable". **Vidstack is in security-only maintenance until Jan 2028.** Media Chrome is MIT | [Video.js](https://raw.githubusercontent.com/videojs/video.js/main/README.md), [LICENSE](https://raw.githubusercontent.com/videojs/video.js/main/LICENSE), [Vidstack](https://raw.githubusercontent.com/vidstack/player/main/README.md), RAW, high |
| cmdk | MIT | Accessible command-menu primitive (Command, Input, List, Group, Item; custom `filter`, `keywords`, `shouldFilter={false}`) | The repo's palette is hand-rolled (no cmdk in `package.json`); keep unless accessibility gaps appear | [cmdk README](https://raw.githubusercontent.com/pacocoursey/cmdk/main/README.md), [LICENSE](https://raw.githubusercontent.com/pacocoursey/cmdk/main/LICENSE.md), RAW, high |
| kbar | not checked (licence file not opened) | Palette with nested actions and keystroke shortcuts | not needed | [kbar](https://raw.githubusercontent.com/timc1/kbar/main/README.md), RAW, medium |
| Fuse.js | Apache-2.0 | Fuzzy search for small and medium data sets; token search; Web Worker mode | zero dependency | [Fuse](https://raw.githubusercontent.com/krisk/Fuse/main/README.md), [LICENSE](https://raw.githubusercontent.com/krisk/Fuse/main/LICENSE), RAW, high |
| MiniSearch | MIT | In-memory full text (prefix, fuzzy, boosting) for data that fits in memory; better than Fuse for document bodies | tiny | [MiniSearch](https://raw.githubusercontent.com/lucaong/minisearch/master/README.md), [LICENSE](https://raw.githubusercontent.com/lucaong/minisearch/master/LICENSE.txt), RAW, high |
| Pagefind | MIT | Static search over built HTML, no server | Needs static HTML to index; our pages are rendered at runtime from raw GitHub, so it does not fit | [Pagefind](https://raw.githubusercontent.com/Pagefind/pagefind/main/README.md), [LICENSE](https://raw.githubusercontent.com/Pagefind/pagefind/main/LICENSE), RAW, high |
| Orama | Apache-2.0 | Full text, vector and facets in process | more than needed | [Orama](https://raw.githubusercontent.com/oramasearch/orama/main/README.md), [LICENSE](https://raw.githubusercontent.com/oramasearch/orama/main/LICENSE.md), RAW, high |
| Fumadocs | MIT | Docs framework for Next.js | The OS already has its own Manual app; skip | [Fumadocs](https://raw.githubusercontent.com/fuma-nama/fumadocs/main/README.md), [LICENSE](https://raw.githubusercontent.com/fuma-nama/fumadocs/main/LICENSE), RAW, high |
| react-konva | MIT | Canvas drawing for draw-over annotations | optional (U4); a plain SVG overlay also works | [LICENSE](https://raw.githubusercontent.com/konvajs/react-konva/master/LICENSE), RAW (licence only), medium |
| **tldraw** | **Not usable**: licence forbids use "in Production Environments" without a licence key | Whiteboard, annotation | Do not use | [tldraw LICENSE](https://raw.githubusercontent.com/tldraw/tldraw/main/LICENSE.md), RAW, high |
| wavesurfer.js | BSD-3-Clause | Waveform plus Regions plugin for notes on the score | | [README](https://raw.githubusercontent.com/katspaugh/wavesurfer.js/main/README.md), [LICENSE](https://raw.githubusercontent.com/katspaugh/wavesurfer.js/main/LICENSE), RAW, high |
| dnd-kit | MIT | Drag and drop for a manual board | only if cards must be dragged; a derived board needs none | [LICENSE](https://raw.githubusercontent.com/clauderic/dnd-kit/master/LICENSE), RAW, high |
| react-markdown | MIT | Markdown to React | The repo has its own `components/os/Markdown.jsx` (112 lines); no need | [LICENSE](https://raw.githubusercontent.com/remarkjs/react-markdown/main/license), RAW, high |

### 1.3 Vercel free tier: what needs storage or auth, and the cheapest safe option

| Need | Cheapest safe option | Limits and caveats | Source |
| --- | --- | --- | --- |
| Source of truth for briefs, decisions, notes that agents must read | The repo (already the pattern: `commitFile` in `lib/github.js`) | GitHub REST: 5,000 requests/hour with a user token; `GITHUB_TOKEN` inside Actions 1,000/hour/repo; about 80 content-creating requests/minute and 500/hour (secondary limit). **Public repo: no client material, nothing personal.** A commit to `main` redeploys the OS (U1) | [GitHub rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), OPENED, high |
| Notes and verdicts on **client** work (must not be public) | Vercel Blob in a **private** store | Hobby: 1 GB storage, first 10,000 simple operations, first 2,000 advanced operations (uploads, lists), first 10 GB transfer per month; past a limit Blob stops working until 30 days have passed, and you are not billed. Hobby rate limit 1,200 simple and 900 advanced operations per minute. `@vercel/blob` is already a dependency | [Blob pricing](https://vercel.com/docs/storage/vercel-blob/usage-and-pricing), OPENED, high |
| Large finished media | GitHub Releases (already; public; streamed through `/api/media`) | Public only: client or pre-approval material must not go there | `docs/WORKFLOWS.md` (repo) |
| Large private media | Cloudflare R2 | Free tier 10 GB-month, 1M Class A and 10M Class B operations, no egress fee ([third-party summary](https://filebase.com/blog/cloudflare-r2-pricing-costs-savings-and-alternatives-in-2026/), OPENED, medium); whether a card is required: unknown | |
| Key-value or SQL | Marketplace databases (Neon, Upstash, Supabase) via `vercel install`; Global Config for read-mostly flags | Free-tier numbers per provider: not verified. Not needed yet: git files plus Blob cover everything planned here | [Vercel storage overview](https://vercel.com/docs/storage), OPENED, high |
| Who may use the OS | Two layers: (1) **Vercel Authentication** (included on Hobby), (2) the existing signed-cookie passcode gate (`lib/gate.js`) | Password Protection is **not available on Hobby** ($20/month per project on Pro). Shareable links: one per account on Hobby. So a client cannot be given a review link on Hobby beyond that single link | [Deployment protection pricing](https://vercel.com/docs/deployment-protection/usage-and-pricing), OPENED, high |
| Long jobs | Never in Vercel Functions; start GitHub workflows (already) | Hobby function max 300 s, 2 GB and 1 vCPU; included per month: 1M invocations, 4 hours Active CPU, 100 GB fast data transfer; Hobby static upload 100 MB; 100 deployments/day | [Vercel limits](https://vercel.com/docs/limits), [Fair use](https://vercel.com/docs/limits/fair-use-guidelines), OPENED, high |

### 1.4 Recommendations: the OS

**U1. Deploy hygiene: stop `main` pushes from burning the Hobby deploy quota, and move note writes off `main`.**
- What: set an Ignored Build Step so a build runs only when `studio-web/` changed (a command that exits 0 skips the build and 1 builds; the guide's example
  is `git diff HEAD^ HEAD --quiet -- ./path/`; Vercel clones with depth 10). Write review notes and the inbox (U8) to a separate branch (`studio-data`, using the `branch`
  field of the GitHub contents API: assumption, standard API, page not opened) and skip builds for every ref other than `main` (the guide says scripts can read `VERCEL_GIT_COMMIT_REF`).
  Agents read that branch through raw.githubusercontent.com.
- Why: 317 commits in one day against 100 deployments per day. A locked deploy means Sam cannot ship an OS fix. Docs, films and manual pages are fetched at run time from raw GitHub,
  so most commits do not need a rebuild.
- Cost and licence: free. Effort 1.5 to 2 h (plus reading the dashboard setting). Risk: low. Unknown: whether skipped builds still count toward the daily limit (the guide does not say;
  a changelog says skipped *monorepo* deployments no longer count). Test with a docs-only commit and read the deployment list.
- Source: [Ignored Build Step guide](https://vercel.com/guides/how-do-i-use-the-ignored-build-step-field-on-vercel) (OPENED, high); [limits](https://vercel.com/docs/limits) (OPENED, high);
  [changelog](https://vercel.com/changelog/skipped-monorepo-deployments-no-longer-count-against-limits) (OPENED, high).

**U2. Frame-accurate review player (notes pinned to a frame, keyboard stepping).**
- What: `Library.jsx` seeks with `currentTime` and shows seconds. Add `requestVideoFrameCallback` to show the frame actually on screen (`frame = round(mediaTime * fps)`, fps from `film.json`);
  keys Left/Right = 1 frame, Shift = 1 s, J/K/L shuttle, Space; notes stored as `{t, frame, text}`; clicking a note seeks to `(frame + 0.5) / fps` (the half-frame offset is my
  assumption to land inside the frame; test in Chrome and Safari). Timecode as `00:12:07` (seconds:frames). A wavesurfer.js strip under the video for notes on sound.
- Why: Sam's verdicts are about moments (no cuts, pops, jitter); "frame 299" beats "around 12 s". Matches Frame.io and Kitsu behaviour.
- Cost and licence: free (browser API; wavesurfer BSD-3-Clause). Effort 6 to 8 h. Risk: the element is not guaranteed frame-accurate and callback timing is best effort (web.dev), so label the
  readout "frame shown"; phones scrub coarsely, so add +1 and -1 frame buttons.
- Source: [web.dev rVFC](https://web.dev/articles/requestvideoframecallback-rvfc) (OPENED, high); [Kitsu review](https://kitsu.cg-wire.com/review/) (OPENED, high).

**U3. Versions and A/B compare.**
- What: name each render `v001, v002`, with its contact sheet, `qc.json` (P9) and a render-settings hash beside it; a review attaches to a version; a compare view plays two versions on one
  clock (side by side, or a draggable wipe) with the same frame stepping. A verdict per version: "Approve" or "Request changes" (Kitsu: Done or Retake).
- Why: Sam's "fix the look, not the clip" way of working needs "is v3 better than v2" answered at a glance. The Styles app already compares stills; this does the same for moving pictures.
  Today a re-render replaces the old file under the same id in `kino-films`.
- Cost: free. Effort 5 to 7 h. Risk: two `<video>` elements drift; drive both from one `requestAnimationFrame` loop and re-sync when the gap exceeds half a frame.
- Source: [Kitsu review](https://kitsu.cg-wire.com/review/) (compare, Retake and Done; OPENED, high); [Frame.io review](https://thedigitalprojectmanager.com/tools/frame-io-review/) (version compare; OPENED, medium).

**U4. Draw-over annotations (optional).**
- What: an SVG or react-konva overlay for pencil and text on the paused frame; save as normalised coordinates (0 to 1) inside the note so it replays at any size; attach a PNG snapshot. Not tldraw (licence).
- Why: "this branch is wrong" is faster drawn than described. Effort 6 to 8 h. Risk: drawing by touch on a phone; keep optional.
- Source: [Kitsu annotations](https://kitsu.cg-wire.com/review/) (OPENED, high); [tldraw LICENSE](https://raw.githubusercontent.com/tldraw/tldraw/main/LICENSE.md) (RAW, high).

**U5. Pipeline board, derived from files (no dragging).**
- What: one row per film, columns Brief, Look approved, Spec valid, Stills checked, Rendering, QC passed, Sam review, Delivered. Every cell is computed from facts that exist or will:
  `films/studio/<id>/status.json`, the validator result, `qc.json`, `films/reviews/<id>.json`, the release asset. Cards that need Sam are pinned on the Desk ("what needs you").
- Why: Kitsu and ShotGrid exist because status is the product; here status can be read from the repo, so it cannot go stale and agents cannot forget to move a card.
  Effort 6 to 8 h (`Jobs.jsx` already derives stage chips; reuse). Risk low. Add dnd-kit only if Sam wants to re-order by hand.
- Source: [Autodesk entities](https://www.autodesk.com/learn/ondemand/module/working-with-entities-and-entity-pages-in-flow-production-tracking/unit/7CskJ6bNNkZEmiJWofju5P) (OPENED, high); [Kitsu](https://kitsu.cg-wire.com/review/) (OPENED, high).

**U6. Command bar polish (the bar exists).**
- What: add Linear's G-then-letter jumps (G D = Desk, G L = Library, G J = Jobs), `/` to focus the bar, a `?` shortcut sheet, recent items, and verbs that change with the page (on a film:
  "Approve", "Request changes", "Make a 9:16 version", "Open recipe"). Fuse.js (Apache-2.0) or MiniSearch (MIT) behind `search()` only if typo tolerance is missing. Keep the hand-rolled
  component; adopt cmdk only if screen-reader or focus bugs appear.
- Why: matches the best keyboard-first tool for little cost. Effort 3 to 4 h. Risk: shortcut clashes with browser keys on iOS; keep every shortcut optional.
- Source: [Linear](https://linear.app/enablement/guide/navigating-linear) (OPENED, high); [Fuse](https://raw.githubusercontent.com/krisk/Fuse/main/README.md), [cmdk](https://raw.githubusercontent.com/pacocoursey/cmdk/main/README.md) (RAW, high).

**U7. One search over everything (catalog, manual, LOG).**
- What: `tools/catalog.py` also writes `studio-web/public/data/search.json` (title, heading, first 300 characters, route for each manual section, film, style, LOG day). MiniSearch loads it
  on first use, client side, no server. The palette's `search()` queries it.
- Why: Sam's brief: "findable by search". Pagefind cannot index pages built at run time; an index file can. Effort 3 to 4 h. Risk: index size; split by section and cache with the catalog's revalidate.
- Source: [MiniSearch](https://raw.githubusercontent.com/lucaong/minisearch/master/README.md) (RAW, high); [Pagefind](https://raw.githubusercontent.com/Pagefind/pagefind/main/README.md) (RAW, high).

**U8. "Note to the studio" inbox (Notion-like writing without a block editor).**
- What: a text box on the Desk. Sam types or dictates; the OS commits `docs/inbox/YYYY-MM-DD-HHMM.md` through the existing `commitFile`, on the `studio-data` branch (U1); the playbook
  `docs/PLAYBOOKS/redirect-from-sams-notes.md` tells agents to read the inbox first. A note can carry a film id and a frame (from U2).
- Why: one place to write and click; it is how a two-line verdict reaches agents without a chat session. Effort 2 to 3 h. Risk: house style (the review route already strips dashes and dots)
  and privacy: the repo is public, so show a banner "this is public" on the box.
- Source: `studio-web/app/api/review/route.js` (repo, read this session).

**U9. Look picker with live previews.**
- What: in Styles and Create, each look's card plays a muted 3 to 4 s loop of the real render (the `-preview.mp4` assets in `kino-films`) when in view, with the still as poster; choosing a look
  pins it into the brief and shows the estimated cost and render minutes (from history, P12).
- Why: Sam chooses by eye (SOUL: show a style board before any money); motion previews make "alive" visible. Effort 3 h. Risk: phone bandwidth; load only the card in view, `preload="none"`.
- Source: Runway reusable templates and one-node test runs ([AlternativeTo](https://alternativeto.net/news/2025/10/runway-launches-node-based-workflows-for-building-custom-ai-creative-pipelines), OPENED, medium).

**U10. Job queue with real render progress.**
- What: for a matrix render (`films-render.yml`, rc-render `films.yml`) read the run's jobs and show "parts 14 of 24 done", elapsed time and an ETA from the median of the last runs; poll about
  every 20 s only while the tab is visible and the run is active.
- Why: the Jobs app shows stages, but a 24-part, 80-minute Blender render looks frozen. Effort 4 h. Risk: API budget (unauthenticated 60/hour, token 5,000/hour; `repoRuns` already caches 20 s);
  the jobs-per-run endpoint is standard GitHub REST but I did not open its page (assumption).
- Source: [GitHub rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) (OPENED, high).

---

## Part 2. Production upgrades

### P1. Render: Cycles CPU stays; EEVEE only maybe on the Mac

Measured in this session (bpy 5.2.2 LTS, the version `film.yml` installs; ffmpeg 6.1.1; a 2 vCPU container shared with other work, so timings are noisy; default cube scene at 1280x720, so the
numbers say something about relative cost only, not about Cutaway scenes):

| Engine | Seconds per frame (three frames) | Note |
| --- | --- | --- |
| EEVEE (`BLENDER_EEVEE`), 16 samples, software GL | 28.5, 35.0, 25.2 | Printed "EGL Error 0x3009 EGL_BAD_MATCH" and still rendered. A first frame at 640x360 took 48 s |
| Cycles CPU, 20 samples + OpenImageDenoise | 12.6, 25.0, 23.4 | |
| Cycles CPU, same, plus `use_persistent_data` | 11.9, 10.9, 20.4 | Inconclusive: the noise is larger than the effect |
| Workbench, 1280x720 | 1.22, 0.51, 0.50 | Fast enough for animatics (P11) |

- Reading: the runners have no GPU ([TOOL_LANDSCAPE_2026-10.md](TOOL_LANDSCAPE_2026-10.md), S47); EEVEE falls back to software GL and is not faster. One vendor page claims EEVEE (4.2+) "demands" a display
  context and GPU swapchain when headless ([iRender](https://irendering.net/eevee-next-headless-dilemma-cloud-render-farm-guide/), OPENED, low: it sells GPU farms); my run shows it works in software but gains nothing.
  **Decision: keep Cycles on the runners (high).**
- On the Mac M4: Cycles Metal uses hardware ray tracing by default on M3 and later ([PR 114296](https://projects.blender.org/blender/blender/pulls/114296), OPENED, high; no numbers in the PR);
  Open Image Denoise supports Apple silicon CPUs and Apple GPUs from M1 ([OIDN README v2.5.1](https://raw.githubusercontent.com/RenderKit/oidn/master/README.md), RAW, high); Blender 4.2 let CPU renders use
  GPU-accelerated denoising ([4.2 Cycles notes](https://developer.blender.org/docs/release_notes/4.2/cycles/), OPENED, high). The existing Mac lane measure is about 7.5 s per frame, about 7 times one runner (WORKFLOWS.md).
  EEVEE on the Mac for look-development is plausible (native Metal) but I found no primary source and did not test it: assumption, low.
- Blender 5.2 LTS (released 14 Jul 2026, fixes until July 2028) adds a Texture Cache for scenes with many image textures and an EEVEE ray-tracing rework
  ([DigitalProduction](https://digitalproduction.com/2026/07/21/blender-5-2-lts-lands-with-node-physics/), OPENED, medium). The repo already runs 5.2.2.
- Licence: Blender GPL (your output is yours); OIDN Apache-2.0 (OIDN README, RAW, high).
- Action for the harness owner: change the usage text of `harness/blender_render.py` to `BLENDER_EEVEE` (MEASURED: `BLENDER_EEVEE_NEXT` is rejected in 5.2.2). Effort 0.2 h.

### P2. Render speed and noise knobs (all free; prove each with the A/B harness, P10)

- What: (a) `scene.render.use_persistent_data = True` for the many-frames-per-part runs: it keeps evaluated data and BVH between frames ([Blender commit](https://developer.blender.org/rB50782df4258), OPENED, high;
  caveats there: more memory, reported bugs with hair and particles, animated collection instances and image-sequence textures). (b) Denoise inputs: Blender 5.2.2 offers `RGB`, `RGB_ALBEDO`, `RGB_ALBEDO_NORMAL`,
  prefilter `NONE/FAST/ACCURATE`, quality `HIGH/BALANCED/FAST` (MEASURED). The engine sets prefilter `FAST` (`films/lib/cutaway/engine.py`, line 60): try `ACCURATE` with `RGB_ALBEDO_NORMAL` at the same samples and
  compare. (c) **Constant seed for the fixed camera**: Blender Studio found a constant seed keeps denoised noise stable only while the camera is static ([Sprite Fright](https://studio.blender.org/blog/denoising-sprite-fright), OPENED, high).
  The Cutaway seasons loop is exactly that case: keep `use_animated_seed` off. (d) Blue-noise sampling is the default for new files since 4.2 ([4.2 notes](https://developer.blender.org/docs/release_notes/4.2/cycles/), OPENED, high);
  check any older `.blend` the kit loads. (e) Open Image Denoise 3 will add **temporal denoising** for animation ([CG Channel, 30 Jan 2026](https://www.cgchannel.com/tag/oidn-3/), OPENED, medium: headline only, no release date
  and no word on Blender adoption).
- Why: each is a few lines; together they may cut samples or flicker. No speedup is claimed: my persistent-data test was inconclusive.
- Effort 3 to 4 h including the A/B. Risk: persistent-data bugs; put it behind a `film.json` flag. Cost: free.

### P3. Upscale 720p to 1080p: test Real-ESRGAN against Lanczos (an experiment, not a rollout)

- What: Cutaway renders 1280x720 and delivers 1920x1080 with `scale=<w>:<h>:flags=lanczos` (`.github/workflows/films-render.yml` line 133; SPEC.md "render 1280x720, delivered 1920x1080").
  Real-ESRGAN is BSD-3-Clause ([LICENSE](https://raw.githubusercontent.com/xinntao/Real-ESRGAN/master/LICENSE), RAW, high), offers a portable `realesrgan-ncnn-vulkan` binary for Windows, Linux and macOS, an
  AnimeVideo-v3 model, scales 2, 3 or 4 and `--outscale` for arbitrary ratios (resized with Lanczos afterwards) ([README](https://raw.githubusercontent.com/xinntao/Real-ESRGAN/master/README.md), RAW, high).
  Experiment: render 10 frames at 1080p with 4 times the samples as the reference; compare Lanczos 720->1080, Real-ESRGAN 720->1080 (x2 then `--outscale 1.5`) and a direct 1080p render at 20 samples,
  by SSIM or VMAF (P10) and by eye.
- Why: if 720p plus AI beats a direct 1080p render for less CPU it is a speed and sharpness win; if it invents texture on flat looks (flat-vector, clay, risograph) it stays off. The Sprite Fright team tried
  super-resolution rendering and found it unstable over time in transparency and volume areas (same article, high); our fog and god rays are volumes.
- Cost: free; compute unknown (the ncnn build needs a Vulkan device, GitHub runners have none; PyTorch CPU speed not measured; assumption: minutes per second of video per runner). Effort 5 to 6 h.
  Risk medium-high (shimmer; terms of the model weights not read: check before publishing).

### P4. Frame interpolation (RIFE, FILM, ffmpeg minterpolate): mostly no, with two narrow uses

- Facts: Practical-RIFE is MIT, its models are "under the same MIT license", 4.25 is recommended and 4.24+ is "quite suitable" for diffusion-generated video ([README](https://raw.githubusercontent.com/hzwer/Practical-RIFE/main/README.md),
  [LICENSE](https://raw.githubusercontent.com/hzwer/Practical-RIFE/main/LICENSE), RAW, high). rife-ncnn-vulkan is MIT, runs on CPU with `-g -1`, doubles the frame count by default ([README](https://raw.githubusercontent.com/nihui/rife-ncnn-vulkan/master/README.md), RAW, high).
  FILM (Google Research) is Apache-2.0 ([LICENSE](https://raw.githubusercontent.com/google-research/frame-interpolation/main/LICENSE), RAW, high), TensorFlow 2, built for large motion ([README](https://raw.githubusercontent.com/google-research/frame-interpolation/main/README.md), RAW, high).
  ffmpeg `minterpolate` is built in, modes `dup`, `blend`, motion-compensated `mci` ([filters.texi](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/filters.texi), RAW, high).
- Conflict with house rules: `docs/DIRECTORS_RULEBOOK.md` R-5-08 says "never interpolate to smooth" and R-5-02 says frame rate is language (stylised work on twos). Interpolating painted or clay looks would erase the look.
- The two uses that fit:
  1. **Looks on twos: render only the unique frames and hold the rest.** A film that declares twos needs half the Cycles frames. I did not find this in `harness/blender_render.py` or the Cutaway engine (a search for
     "twos" only hits docs): verify, then add a `hold` field to `film.json` and duplicate frames in the join step. Saves 50% on such films with the exact look and no AI. Effort 2 to 3 h. Risk low.
  2. **Smooth living-world loops (Cutaway seasons): render at 12 fps, interpolate to 24 with RIFE**, only if the A/B (P10) shows no ghosting around thin stalks, water glints or particles. Effort 6 h as an experiment.
     Risk medium-high (assumption: ghosting on thin, high-contrast detail).
- Cost: free; models MIT or Apache-2.0.

### P5. Procedural animation: Blender Geometry Nodes (low priority now)

- Blender 5.0 brought closures and bundles to shader nodes (Cycles repeat zones run a fixed number of iterations) ([5.0 rendering notes](https://developer.blender.org/docs/release_notes/5.0/rendering/), OPENED, high).
  5.2 adds Mesh Bevel, bundle get and set across modifiers, and **experimental** XPBD hair and cloth ([DigitalProduction](https://digitalproduction.com/2026/07/21/blender-5-2-lts-lands-with-node-physics/), OPENED, medium).
- The Cutaway engine already animates sway in Python (`engine.py`, `sway=1.35`). Moving wind and scatter into a Geometry Nodes group (noise-driven Set Position over time, a random phase per instance) could make flora
  cheaper to evaluate and richer, but I have no measurement. Effort 10 to 20 h, risk medium. Do not put the experimental physics in a delivered film.

### P6. Motion design stack: evaluated, none to adopt now

| Tool | Licence (source) | Verdict |
| --- | --- | --- |
| Remotion | Free for individuals, for-profit organisations with up to 3 employees, and non-profits; a company licence above that; **the licence changes in 5.0** ([LICENSE](https://raw.githubusercontent.com/remotion-dev/remotion/main/LICENSE.md), RAW, high) | Redundant: `dom-render.cjs` with `window.KF.render(i,t)` is the same frame-pure model. Revisit if Unmissed passes 3 employees (section C) |
| Motion Canvas, Revideo | MIT ([Motion Canvas](https://raw.githubusercontent.com/motion-canvas/motion-canvas/main/LICENSE), [Revideo](https://raw.githubusercontent.com/redotvideo/revideo/main/LICENSE), RAW, high). Revideo: headless `renderVideo()`, React player, "runs anywhere Node and a headless browser run" ([README](https://raw.githubusercontent.com/redotvideo/revideo/main/README.md), RAW, high) | Good for explainer vector motion synced to a voice-over. No current film needs it. Trial only for a Kinetic explainer |
| Theatre.js | Core `@theatre/core` Apache-2.0; Studio `@theatre/studio` **AGPL-3.0**; development "temporarily moved to a private repo" ([README](https://raw.githubusercontent.com/theatre-js/theatre/main/README.md), RAW, high) | Visual keyframe editor for Three.js and DOM; maintenance uncertain. Skip |
| Rive | Web runtime MIT ([LICENSE](https://raw.githubusercontent.com/rive-app/rive-wasm/master/LICENSE), RAW, high); editor: Free has "a limited number of files with export limits", Pro $24/month annual ([2023 post](https://rive.app/blog/new-pricing), OPENED, low: old) | Interactive UI motion, not a film tool. Skip |
| Lottie (lottie-web) | MIT ([LICENSE](https://raw.githubusercontent.com/airbnb/lottie-web/master/LICENSE.md), RAW, high) | Licences of third-party Lottie files vary; house rule bans cartoon icons. Skip |

### P7. Sound: music to picture

- State: the score engine writes `audio/score_plan.json` (the beats are known by construction); `harness/shots/prep.py` already makes a beat map for ads with librosa. Beat *detection* is only needed for fetched music (`music-fetch.yml`).
- Tools:
  - librosa, ISC ([LICENSE](https://raw.githubusercontent.com/librosa/librosa/main/LICENSE.md), RAW, high). `beat_track` returns `tempo` and `beats`; `start_bpm` defaults to 120 and `tightness` to 100; the page does not mention tempo octave errors
    ([beat_track](https://librosa.org/doc/main/generated/librosa.beat.beat_track.html), OPENED, high). WORKFLOWS.md already warns that trackers halve or double the tempo, so keep the `start_bpm` check.
  - **Beat This!** (ISMIR 2024): code and published weights MIT; CLI `beat_this file -o out.beats`; falls back to CPU; needs PyTorch; some training data has limited licences, "up to the user to assess"
    ([README](https://raw.githubusercontent.com/CPJKU/beat_this/main/README.md), [LICENSE](https://raw.githubusercontent.com/CPJKU/beat_this/main/LICENSE), RAW, high).
  - **madmom: do not use for Unmissed or client work.** Code is BSD-2-Clause, but "all model and data files" are CC BY-NC-SA 4.0 ([LICENSE](https://raw.githubusercontent.com/CPJKU/madmom/main/LICENSE), RAW, high). Its PyPI release supports only old Python
    and numpy per the Beat This README (RAW, high).
  - Sonic Visualiser: GPL-2.0-or-later desktop application with Vamp plugins, for a human to inspect tracks ([README](https://raw.githubusercontent.com/sonic-visualiser/sonic-visualiser/master/README.md), RAW, high); it cannot run in CI.
  - Demucs (stem separation, MIT, [LICENSE](https://raw.githubusercontent.com/adefossez/demucs/main/LICENSE), RAW, high): only if a track must be split; no current need.
- Recommended: a small `films/lib/score/beatmap.py` that writes `audio/beats.json` (beats, downbeats, onsets): from `score_plan.json` when the score is ours, from Beat This (fallback librosa with `start_bpm`) otherwise. The Cutaway spec's time
  references gain `"beat12"` marks, so a bird takes off *on* a beat. Effort 3 to 4 h. Risk low. Payoff moderate: Cutaway is narration-led; music-to-picture matters most for loops and ads.

### P8. Loudness and mix: two-pass linear loudnorm; platform targets

- Targets (sources conflict): YouTube -14 LUFS, true peak -1 dBTP, "turns down only; never boosts" ([Fora Soft table, 2026-06-05](https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026), OPENED, medium);
  the Frame.io workflow guide says YouTube "tends to shoot for -12 to -14 LUFS" and does not confirm turn-down-only ([Frame.io](https://workflow.frame.io/guide/loudness-for-youtube), OPENED, medium);
  a post dated 2015 with an update note says YouTube has used exactly -14 LUFS since 2019 and that "louder songs are turned down" ([Production Advice](https://productionadvice.co.uk/youtube-loudness/), OPENED, low: old).
  TikTok, Instagram Reels, Facebook: **no published target**; observed about -14 LUFS; Meta uses adaptive loudness (Fora Soft, medium). EBU R128 broadcast: -23 LUFS (same table).
  **Keep -14 LUFS with true peak at or below -1 dBTP for everything**; the repo's `-14 / -1.5` is safe under every reading above.
- Upgrade: `films/lib/battle_mix.py` line 76 runs a single-pass `loudnorm=I=-14:TP=-1.5:LRA=11`. ffmpeg documents dynamic and linear modes and single or double pass; for files, a double pass (measure, then apply the `measured_*` values with
  `linear=true`) reaches the target without dynamic gain riding ([loudnorm](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/filters.texi), RAW, high). Add LRA and the short-term maximum to the report, plus `silencedetect=n=-50dB:d=1` for dead air.
  pyloudnorm (MIT, ITU-R BS.1770-4, [README](https://raw.githubusercontent.com/csteinmetz1/pyloudnorm/master/README.md), [LICENSE](https://raw.githubusercontent.com/csteinmetz1/pyloudnorm/master/LICENSE), RAW, high) is an independent cross-check of the number.
- Ducking: `sidechaincompress` (threshold, ratio, attack, release) is already used; no change.
- Effort 1.5 to 2 h. Risk low.
- YouTube upload spec for the final encode: MP4 with moov at the front, H.264 High, closed GOP of half the frame rate, 2 consecutive B-frames, 4:2:0, BT.709, AAC-LC at 48 kHz; SDR 1080p at 8 Mbps for 24 to 30 fps and 12 Mbps for 48 to 60 fps;
  384 kbps stereo audio ([YouTube Help](https://support.google.com/youtube/answer/1722171?hl=en), OPENED, high). The current join uses CRF 17 with a 16 Mbps maxrate: above the spec, fine.

### P9. Automatic quality gate: one `tools/qc.py` that writes `qc.json` (the biggest gap)

Today the checks live in a playbook (`docs/PLAYBOOKS/check-before-showing-sam.md`) as commands someone must remember. Make them one script, run by the join job and by hand, writing a machine-readable report that the OS shows (U3, U5).
All filters below are documented in [filters.texi](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/filters.texi) (RAW, high); rows marked MEASURED were run here on a synthetic 6 s clip with ffmpeg 6.1.1.

| Check | Filter or method | Verified here |
| --- | --- | --- |
| Unplanned cuts (Sam's 23 Oct verdict: one fixed view, no cuts) | `scdet=t=10:s=1`; fail on any score above the threshold in a Cutaway film (the documented good range is 8 to 14) | MEASURED: scores 18.3 at 2 s and 11.5 at 4 s for two hard cuts |
| Frozen stretches | `freezedetect=n=0.003:d=1` (defaults: noise -60 dB, duration 2 s) | MEASURED: found the freeze from 2 s to 4 s. Limit: it averages the whole frame, so it misses a *local* freeze (a frozen river under a moving sky); add a per-tile difference check (assumption, 3 h) |
| Black frames | `blackdetect=d=0.5` | already in the playbook |
| Flicker (denoise shimmer, pulsing fog) | `signalstats` prints per-frame `YAVG`; metric = high-frequency energy of the YAVG series (second difference) on static-camera shots; repair option `deflicker=size=5:mode=pm` | MEASURED: `signalstats` prints YAVG per frame and `deflicker` runs. The threshold is not calibrated: calibrate on two accepted films (assumption) |
| Loop seam (seasons loop) | `ssim` or `psnr` of the last frame against the first; clean when the score matches a typical frame-to-frame score | MEASURED: `ssim` on first vs last PNG ran (0.87 on my non-looping clip) |
| Loudness | `ebur128=peak=true` (I, LRA, true peak); two-pass loudnorm (P8) | MEASURED: reports I, LRA and peak |
| Dead air | `silencedetect` | filter present (MEASURED) |
| Banding in fog and gradients | VMAF's CAMBI banding detector (open-sourced 2021, `full_ref` option) ([vmaf README](https://raw.githubusercontent.com/Netflix/vmaf/master/README.md), RAW, high) | **Not runnable with Ubuntu ffmpeg 6.1.1 here: no libvmaf** (MEASURED). Needs an ffmpeg build with libvmaf (a source for one was not opened) |
| Text-safe areas | 9:16 exists: `social/lib/safecheck.mjs` (box x 0.11 to 0.78, y 0.15 to 0.65). Add the same for 16:9 titles: keep text inside the central 90% (assumption: the broadcast "title safe" convention, not sourced here) | repo |
| Contact sheet | existing `tile` sheet; print the QC verdict beside it | repo |

- Effort 8 to 10 h (script, thresholds, unit tests on synthetic clips, wiring into `films-render.yml` join, an OS badge). Cost free.
- Risk: false positives on deliberate holds (rulebook R-9-05 asks for at least one hold of 24 frames per minute): let the spec list its `holds`.
- Licence: ffmpeg LGPL or GPL by build. PySceneDetect (BSD-3-Clause, v0.7.2 of 11 Oct 2026, [LICENSE](https://raw.githubusercontent.com/Breakthrough/PySceneDetect/main/LICENSE), [README](https://raw.githubusercontent.com/Breakthrough/PySceneDetect/main/README.md), RAW, high) is an alternative for cut lists; not needed because `scdet` is built in.

### P10. A/B reference harness (VMAF and SSIM): every render change proven, not argued

- What: `tools/ab.py` takes a 10-frame still set rendered at high samples as the reference, renders the candidate (new samples, prefilter, upscaler, interpolation) and reports SSIM and PSNR (built in), and VMAF where libvmaf exists.
  VMAF is BSD-2-Clause-Patent ([LICENSE](https://raw.githubusercontent.com/Netflix/vmaf/master/LICENSE), RAW, high). The ffmpeg `libvmaf` filter takes the distorted video first and the reference second, writes `log_fmt=json`, and the library also computes PSNR,
  SSIM, MS-SSIM and CIEDE2000 ([vmaf README](https://raw.githubusercontent.com/Netflix/vmaf/master/README.md), [filters.texi](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/filters.texi), RAW, high). New v1 models: June 2026.
- Why: gives P2, P3 and P4 a yes or no. Caveat (assumption): VMAF was built for compression artefacts on natural video; use it only as a *relative* score between two candidates of the same scene, never as a verdict on stylised looks. Eyes still decide.
- Effort 3 to 4 h plus getting an ffmpeg with libvmaf onto the runner. Risk low.

### P11. Ways of working: animatic first, look-development matrix, versioned reviews

- **Animatic from the spec in a minute:** the harness already accepts `--engine BLENDER_WORKBENCH` (`harness/blender_render.py`). MEASURED: Workbench renders 1280x720 at 0.5 s per frame (default scene, same shared box).
  Render the spec's blocking (placeholder shapes for presets, the real camera, the real narration and title cards) and review *timing* (does the deer rise on "step"?) before the 80-minute Cycles run. Effort 4 to 6 h.
  Risk: the Cutaway engine builds Cycles-only shaders; Workbench shows geometry and flat colour only (enough for timing).
- **Look-development matrix:** one `stills.yml` dispatch renders the same hero frame across the 12 art looks and 4 seasons as a labelled sheet (24 to 48 stills at 480 px, 8 samples). The Styles app already shows boards; this makes the board cheap to refresh
  after any kit change. Effort 3 h, cost free (runner minutes).
- **Versioned reviews:** see U3. A version is `v00N` plus spec hash, Blender version, QC report, contact sheet and verdict. Nothing is overwritten.
- Why: SOUL.md's rule "show a style board before any money" extended to time: show timing before compute.

### P12. Render cache and render history by input hash

- What: hash each part's inputs (spec.json, cues.json, kit and engine file hashes, Blender version, samples, frame range). If a part with the same hash exists in a release asset (for example `kino-parts`) download it instead of rendering.
  After a change that touches only the end card or the last sentence, 20 of 24 parts are reused. The Actions cache offers 10 GB per repository with 7-day retention by default and least-recently-used eviction; more than 10 GB needs a paid plan
  ([GitHub changelog](https://github.blog/changelog/2025-11-20-github-actions-cache-size-can-now-exceed-10-gb-per-repository/), OPENED, high), so parts older than a week belong in a release, not the cache.
- Why: the usual edit is small; 80 minutes of runner time for a one-word change is the biggest avoidable cost and delay. Also record seconds per part in `render-history.json` to feed the OS ETA (U10) and the cost line (U9).
- Effort 8 to 12 h. Risk: keys must hash *inputs*; do not rely on bit-identical output across runners (determinism of CPU floats and the denoiser across machines is not verified: assumption).

---

## A. What I did not recommend, and why

| Item | Reason |
| --- | --- |
| EEVEE on GitHub runners | Measured no faster than Cycles in software GL; a vendor page warns of headless failures (P1) |
| tldraw | Licence forbids production use without a key |
| madmom models | CC BY-NC-SA 4.0 (non-commercial) |
| Kitsu, ShotGrid, ftrack as the OS | Heavy server stacks (Kitsu is AGPL-3.0); we only need the patterns, and status can be derived from files |
| Frame.io itself | Paid beyond a 2-user, 2 GB free plan; there is one reviewer |
| Vidstack | Security-only maintenance; use the native element or Video.js 10 |
| Remotion, Motion Canvas, Theatre.js, Rive, Lottie | Redundant with the in-house frame-pure renderer, or licence and maintenance caveats (P6) |
| RIFE on looks on twos | Erases the look; rulebook R-5-08 (P4) |
| Pagefind | Needs prebuilt static HTML; our pages render at run time (U7) |
| OpenTimelineIO (Apache-2.0), Storyboarder | No current need; Storyboarder's licence file was not found at the usual path (404) and its README links to a notes page, so unverified |

## B. Sources that could not be opened, and what is unverified

- developer.mozilla.org (egress proxy policy denial, 403): web.dev used instead.
- github.com pages and `gh api` for third-party repos (not enabled for this session): raw.githubusercontent.com used for READMEs and LICENSE files.
- docs.blender.org manual pages (Sampling, Performance): the body was not returned; Blender Studio, a commit page and release notes used instead.
- developer.blender.org/docs/release_notes/5.2 (not in the fetch allow-list): Phoronix and DigitalProduction summaries used; the Phoronix page gave only EEVEE items.
- Frame.io's own pages and ftrack: not read (Frame.io via a third-party review).
- Not verified at all: Vercel Pro price, Global Config limits, Marketplace database free tiers, Real-ESRGAN and RIFE speed on CPU, model-weight terms, EEVEE on macOS, whether the Vercel dashboard already has an Ignored Build Step.

## C. Needs a lawyer, an accountant, or Sam

1. **Vercel Hobby is non-commercial.** Confirm with Vercel support, or move the OS to Pro, before Unmissed bills a client. (Pro price not read this session; accountant for the expense.)
2. **Remotion** is free only up to 3 employees and its licence changes in 5.0: relevant only if the studio adopts it.
3. **Model weights** (Real-ESRGAN, RIFE): terms for commercial output were not read beyond the code licences. Check before using them in a delivered film.
4. **Public repo:** review notes, inbox notes and verdicts are public if committed to this repo. Client material needs Blob (private) or the private `sovereign-studio` repo.

## D. Ranked top 10 to implement now

Ranking = value for Sam's stated goals (a self-sufficient studio, results first, cinema-grade, no surprises) divided by effort and risk.

| # | Item | Effort | Why now |
| --- | --- | --- | --- |
| 1 | **U1** Ignored Build Step, and note writes off `main` | 1.5 to 2 h | 317 commits a day against 100 deployments a day; stops the OS going dark |
| 2 | **P9** `tools/qc.py` and a `qc.json` gate (unplanned cuts via `scdet`, freeze, flicker, loop seam, loudness, black) | 8 to 10 h | Turns Sam's verdicts into automatic checks before he sees a film; the filters are verified |
| 3 | **U2** Frame-accurate review player (frame readout, frame stepping, notes by frame) | 6 to 8 h | Sam's feedback is about moments; notes become exact |
| 4 | **P10 + P2** A/B harness and the free render knobs (denoise inputs, constant seed, persistent data) | 6 to 8 h | Proves every later render change; may cut samples or flicker |
| 5 | **P8** Two-pass linear loudnorm, with LRA and dead air in the report | 1.5 to 2 h | Cheap, exact -14 LUFS without dynamic gain riding |
| 6 | **P11** Workbench animatic from the spec | 4 to 6 h | Review timing in a minute before an 80-minute render |
| 7 | **U3** Versions, synced A/B compare, verdict per version | 5 to 7 h | "Is v3 better than v2" in one view; nothing overwritten |
| 8 | **U5** Pipeline board derived from files | 6 to 8 h | Status that cannot go stale; the Desk shows only what needs Sam |
| 9 | **P12** Part-level render cache by input hash | 8 to 12 h | Small edits stop costing 80 minutes |
| 10 | **U10** Per-part render progress and ETA | 4 h | A long render stops looking frozen; uses P12 history |

Next five, after those: P3 Real-ESRGAN against Lanczos (experiment); P4 use 1, render only the unique frames for looks on twos (after verifying it is not already done); U7 one search index; U8 note-to-studio inbox; P7 `beatmap.py` with Beat This.
