# Why this repository uses GitHub-hosted runners

KINOFORGE is a procedural cinema framework. Its example scenes under `proto/` are the project's regression set and its
documentation: each one exercises a part of the kit (camera rig, finish pass, particles, materials, sound synthesis,
lip-sync) and is rendered by CI so that a change to the kit can be checked against a known result and so that the
README's gallery stays current.

What the workflows do:

- `smoke.yml` — on pushes that touch the harness, renders 6 frames of a tiny scene to prove the renderer still works on a clean runner.
- `render.yml` — on pushes to `render/queue/*.json` or by hand, renders the listed example scenes (one runner per scene, or a few frame-range parts for the Blender examples) and publishes the clips and contact sheets to the `gallery` release.

Self-imposed limits, so the footprint stays that of an ordinary open-source project: no scheduled runs, 45 minutes
per job, bounded parallelism, artifacts kept 3–7 days, release assets for the finals, roughly 1,500 runner-minutes a month
and never more than 3,000 in any 30 days. Finished productions built with the framework are rendered elsewhere.
