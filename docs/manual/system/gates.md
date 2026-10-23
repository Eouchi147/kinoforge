# The gates: `tools/verify.sh`

Every house rule that code can check is a gate in `tools/verify.py`, run by `bash tools/verify.sh`. A gate fails loudly
with a "how to fix" line. Run it at the start of a session, before every commit, and before you say "done". CI runs the
same gates on every push (`.github/workflows/verify.yml`, about 1 min) and the heavy ones on engine changes
(`verify-engine.yml`, about 10 min).

## Inputs
- Node 22 and Python 3.11 or newer. For `--full`: `cd harness && npm ci && npx playwright install --with-deps chromium`,
  `pip install numpy scipy soundfile librosa pillow`, and ffmpeg.

## Exact steps
1. `bash tools/verify.sh` (fast, about 1 min, no browser, no network, no money). Exit 0 means every gate passed.
2. `bash tools/verify.sh --full` when you touched `films/lib/`, `films/director/`, `harness/` or `tools/` (about 8 to 10 min).
3. Other forms: `--only text,docs` (some gates), `--since <ref>` (judge the commits after `<ref>` for the docs gate),
   `--list` (names).
4. Read every `x` line: `<where>: <what>` then `how to fix: <fix>`. Fix the cause, run again.
5. After you push, check CI: `gh api "repos/Eouchi147/kinoforge/actions/workflows/verify.yml/runs?per_page=3" --jq '.workflow_runs[] | [.head_sha[0:7], .status, .conclusion]'`.

## The gates
| Gate | Checks | Typical fix |
| --- | --- | --- |
| `secrets` | No API keys, tokens or private keys in tracked files (OpenRouter, OpenAI or Anthropic style, GitHub, AWS, Google, Slack, PEM) | Remove the key; Sam rotates it; keys live only in GitHub or Vercel secrets |
| `json` | Every tracked `.json` parses | Fix the syntax |
| `syntax` | Every tracked `.py` compiles; every `.js/.mjs/.cjs` passes `node --check` (studio-web is built by Vercel instead) | Fix the code |
| `workflows` | A workflow that installs Playwright runs on `ubuntu-24.04` (Playwright 1.56 does not install on `ubuntu-latest`) | Pin `runs-on: ubuntu-24.04` |
| `text` | No em dash, en dash, "..." or the ellipsis character in words that reach the screen or the voice: JSON on-screen fields, string literals in film and ad code, Python strings in Blender films | A comma, a colon, "to" for ranges, or a new sentence |
| `prompts` | AI image or video prompts never ask for words, logos or numbers (`prompt`, `image_prompt`, `video_prompt`, `still_prompt`) unless negated ("no text") | Set the words in code; say "no text, no logos" |
| `battlemap` | `films/lib/battlemap/tools/scenes.mjs` on every Battle Map film: scene plan, camera speed, shot count, jump cuts | Fix the spec |
| `social` | `social/lib/check.mjs` on every batch, and the social lane's unit tests | Fix the batch |
| `director` | The director tests that need no browser | Fix the director code |
| `docs` | A change to code, films or workflows comes with a `docs/LOG.md` line (or, for work inside one film folder, that folder's `NOTES.md`); LOG keeps `## <day> <Mon> <year>` headings newest first | Add the dated line (and update STATUS) |
| `director-full` (full) | Every director test, including the spec stage in Chromium | |
| `check` (full) | `films/director/check.cjs` on every Battle Map film (Chromium, stills, craft checks) | |
| `score` (full) | `films/lib/score/selftest.py` | |

Exceptions live in one file, `tools/verify-allow.txt` (`<gate> <path pattern>  # <reason>`), only for frozen legacy
work or files machines write (ledgers, `status.json`, audio outputs, `films/director/LESSONS.md`). Never add one to get a
green run on new work. The gate warns when an exception matches nothing.

## Other checks that are not in verify (run them yourself)
| Check | Command |
| --- | --- |
| Cutaway spec | `python3 films/lib/cutaway/tools/validate.py films/cutaway/<id>` (under 1 s; prints the render cost) |
| Cutaway line library | `python3 films/lib/cutaway/tools/selftest.py` |
| Battle Map film | `node films/lib/battlemap/tools/scenes.mjs films/battles/<id>`; `node films/director/check.cjs films/battles/<id> --line battle-map` |
| Social safe box | `node social/lib/safecheck.mjs social/templates/<t>` |
| Catalog fresh | `python3 tools/catalog.py --check` |
| Web studio | `cd studio-web && npx next build && node tests/flow.mjs` (mock OpenRouter) |

## Alternatives
None: the gates are the floor. A rule that code cannot check goes in `docs/LESSONS.md` and in your own review.

## Checks before showing Sam
Gates passing is necessary, not sufficient: the render still goes through `quality-checks.md`.

## Known traps
- The docs gate judges your unpushed commits plus the working tree against `origin/main`, the upstream or `FETCH_HEAD`;
  in a fresh checkout with no remote ref it may judge nothing. Pull first.
- The docs gate only fails for a missing LOG line; it warns (does not fail) when STATUS is not updated alongside.
- `docs/LOG.md` is append-only: a removed or rewritten line raises a warning; add a correcting line instead.
- Gates do not check whether a sentence is true. Your review does.

## Sources of truth
`tools/verify.py` (the gate code and its docstring), `tools/verify.sh`, `tools/verify-allow.txt`,
`.github/workflows/verify.yml`, `.github/workflows/verify-engine.yml`, `docs/decisions/0010-memory-and-gates.md`.
