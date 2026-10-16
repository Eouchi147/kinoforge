# Review pages (sources of the Claude artifacts shown to Sam)

Saved 16 Oct 2026 at the handover, so the pages can be rebuilt or republished. The HTML is the published page as it
stood, kept as published (older wording, including some dashes, left unchanged). The media files they point to are not in
the repo: they are hosted inside each artifact on claude.ai, and most also exist in the GitHub releases.

| File | Artifact | Media it expects | Where the media also live |
| --- | --- | --- | --- |
| `anthology-prototypes.html` | KINOFORGE Anthology Prototypes, https://claude.ai/artifact/RNYD6WL3Pu5ZCof76s2x5K | clips stored inside the artifact (`/_blob/<hash>` in the `SRC` map); its "full quality" links point to release `gallery` (the `p14-finishing` link there is a 404: p14 is not in the release) | release `gallery` (p01 to p13, p15, p16); Sam's Mac `/Users/sam/Desktop/Projects/AI tools/Video Production/kinoforge-prototypes/` (p01 to p14) |
| `restaurant-ad-looks.html` | Restaurant Ad Looks, https://claude.ai/artifact/PCjsE4tLDSUg7A6JjDsw5P | `media/hero-*.jpg`, `flash-*.jpg`, `freeze-*-move.mp4` and posters, `type-motion-v2.mp4`, `screen-story.mp4`, `*-type.jpg` | stills and clips in release `boards`; `type-motion-v2.mp4` and `screen-story.mp4` are renders of `ads/board/type-motion` and `ads/board/screen-story` (re-render with `harness/dom-render.cjs`) |
| `unmissed-ad-directions.html` | Unmissed Ad Directions, https://claude.ai/artifact/6zvTkrN7mpTTCQZc3i99bN | `media/v1.mp4` to `v5.mp4` (720p previews) and posters | 1080p masters in release `ads` (`unmissed-v1.mp4` to `unmissed-v5.mp4`) |
