# Follow-up chains (rc-render `chain.yml`)

A render that must wait for other renders, run by GitHub itself so no chat session has to stay alive. Every 15 minutes
(cron `*/15 * * * *`, also dispatchable by hand) the workflow reads the asset names in `kino-films` and the markers in
`film-logs`; for each rule whose needed assets all exist and whose marker is missing, it dispatches `films.yml` for the
rule's film and writes the marker `chain-<name>.done`. Used for Agincourt v2, which waited for its two Cutaway mud inserts.

## Inputs
A rule line in rc-render `.github/workflows/chain.yml`, inside the `rules` step:
`rule <name> <film folder> <parts> <needed asset> [<more needed assets>]`, for example
`rule agincourt-v2 films/battles/agincourt 16 cutaway-agincourt-mud-A.mp4 cutaway-agincourt-mud-B.mp4`.

## Exact steps
1. Render the dependencies first (each with its own `films.yml` dispatch).
2. Clone rc-render, add your rule line under the existing ones, commit only that file, pull with rebase, push.
3. Wait (up to 15 min plus queue), or dispatch the check by hand:
   `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/chain.yml/dispatches -f ref=main`.
4. The chain run's log says `<marker> waiting for <asset>`, `already done` or `dispatched <film>`:
   `gh api "repos/Eouchi147/rc-render/actions/workflows/chain.yml/runs?per_page=3" --jq '.workflow_runs[] | [.id,.conclusion]'`.
5. Follow the dispatched `films.yml` run as usual (`render-film-on-runners.md`).
6. To repeat a rule, delete its marker asset in `film-logs`; to stop it, remove the line.

## Alternatives
- A scheduled task that wakes a session (`send_later` or a scheduled task) when a session must act on the result
  (checking, delivering). The render itself still belongs on GitHub.
- Dispatch by hand once the inputs exist, if a session is alive anyway.

## Checks before showing Sam
The dispatched film is checked like any other; for inserts, look at the first and last frame of each insert span.

## Known traps
- The cron had not fired for Agincourt on 23 Oct: the chain was dispatched by hand at 04:21 UTC. GitHub's scheduled runs
  can be late or skipped; check, and dispatch by hand if needed.
- Inside the runner the rule uses `gh workflow run` with the workflow's own token (allowed there); the dispatched films
  render `ref=main`, so push the film before the dependencies finish.
- Rules accumulate: old rules stay harmless once their marker exists.

## Sources of truth
rc-render `.github/workflows/chain.yml`, `docs/LESSONS.md` (Process: the container restarts), `docs/LOG.md` (22 to 23 Oct).
