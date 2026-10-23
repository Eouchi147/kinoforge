# Playbooks: one recurring job each, step by step

Pick the playbook for your job, follow it in order, and finish with its **definition of done**. Every playbook assumes
the start of every session in `AGENTS.md` (pull, `bash tools/verify.sh`, read `docs/STATUS.md`). If a step does not
work as written, fix the playbook in the same commit as your fix (and log it).

| Job | Playbook |
| --- | --- |
| Make a Battle Map film by hand | [make-a-battle-map-film.md](make-a-battle-map-film.md) |
| Re-direct a film from Sam's notes | [redirect-from-sams-notes.md](redirect-from-sams-notes.md) |
| Make a Cutaway film | [make-a-cutaway-film.md](make-a-cutaway-film.md) |
| Run the free director (a film from a brief, no hand coding) | [run-the-free-director.md](run-the-free-director.md) |
| Render on GitHub (rc-render films, stills, remux, chain) | [render-on-github.md](render-on-github.md) |
| Render on Sam's Mac (the Mac lane) | [render-on-the-mac.md](render-on-the-mac.md) |
| Check a render before showing Sam | [check-before-showing-sam.md](check-before-showing-sam.md) |
| Deliver to Sam's Mac | [deliver-to-sams-mac.md](deliver-to-sams-mac.md) |
| Make a business ad or social video (paused lane) | [make-a-business-ad.md](make-a-business-ad.md) |

Shared rules for every playbook: free tools only (`docs/decisions/0001`); words set in code; one stills run in flight per
builder on the shared runner queue; dispatch through the REST API (`gh api -X POST ...`), because `gh workflow run` and
`gh release download` use GraphQL, which some sessions block; give `ref` as a branch or a FULL commit hash.
