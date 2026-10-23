# KINOFORGE Studio OS (studio-web)

The studio's own software: one page that works like an operating system for the studio. Next.js 15 (App Router),
React 19, no UI framework, no paid service. Deployed on Vercel as `kinoforge-studio`; every push to `main` redeploys.

## How it is organised

```
app/page.jsx                 renders the OS
app/layout.jsx, globals.css  fonts and the whole design system (tokens at the top of globals.css)
components/os/OS.jsx         the shell: rail of apps (bottom dock on phones), command bar, one app on screen
components/os/store.js       shared state: hash routes, catalog loading, fetch hook, local reviews, small helpers
components/os/Palette.jsx    the command bar (Ctrl K or Cmd K, "/" or the search field)
components/os/Markdown.jsx   a safe Markdown renderer (builds React elements, never HTML strings)
components/os/ui.jsx         shared pieces: Head, Panel, Poster, FilmTile, Seg, Note, Led
components/os/icons.jsx      line icons
components/os/apps/*.jsx     the apps: Desk, Library, Create, Styles, Jobs, Sound, Manual, Settings
lib/commands.mjs             the command bar's brain (plain words to actions, search); pure, tested
lib/catalog.mjs              the catalog made ready for the interface; pure, tested
lib/assets.mjs               asset URLs (public paths or release assets streamed through /api/media); pure, tested
lib/catalog.fixture.json     sample data used only when public/data/catalog.json is missing (Settings says so)
lib/github.js                GitHub reads and the one write helper (commitFile)
lib/gate.js                  the write lock (STUDIO_PASSCODE)
tests/flow.mjs               the server flow against a mock OpenRouter (no key, no money, no GitHub writes)
tests/commands.test.mjs      node --test: command bar, catalog, assets
```

The data the OS shows comes from `public/data/catalog.json` (written by `tools/catalog.py`, owned by the manual
writers; never edit it by hand) plus live reads: studio jobs, render runs, reviews, the manual pages (fetched from the
public repo at request time), and the director's status.

## Routes (the address bar)

Hash routes, so every view has a link Sam can keep: `#/desk`, `#/library`, `#/library/<film id>?tab=review|recipe|facts`,
`#/create?what=loop&line=cutaway&format=9:16&look=fable&length=30&cap=2&music=<id>`, `#/styles`, `#/styles/looks`,
`#/styles/<style id>`, `#/styles/compare/<a>/<b>`, `#/jobs`, `#/jobs/<job id>`, `#/sound`, `#/manual/<docs path>`,
`#/manual?q=<words>`, `#/settings`. Old links (`#job/<id>`, `#films`, `#director`, `#setup`) still open the right app.

## API routes

| Route | What | Writes |
| --- | --- | --- |
| `POST /api/director` | one turn of the director chat (OpenRouter) | spends credit: locked |
| `POST /api/build` | commits `films/studio/<id>/brief.json`, which starts `film.yml`; accepts `look` and `music_piece` (kept, not yet read by the pipeline) | locked |
| `GET /api/job?id=` | one build's brief, status and run | |
| `GET /api/jobs` | every studio build, newest first | |
| `GET /api/runs` | Actions runs of `Eouchi147/rc-render` and `Eouchi147/kinoforge` (public, works without a token) | |
| `GET /api/review?id=`, `GET /api/review` | a film's review, or every saved verdict | |
| `POST /api/review` | approve, request changes, or a note pinned to a frame: commits `films/reviews/<id>.json` on the `studio-data` branch | locked |
| `GET /api/doc?path=` | one page of `docs/GUIDE.md` or `docs/manual/**` from GitHub raw | |
| `GET /api/manual[?q=]` | the manual's contents, or a full-text search | |
| `GET /api/media?r=&f=` | streams a release asset with Range (video seeks); `r` is `kino-films`, `films`, `gallery` or `<kinoforge or rc-render>:<tag>` | |
| `GET /api/films`, `/api/status`, `/api/models` | live pipeline films, connections and money, the model market | |
| `POST /api/decision` | a decision record (`studio/decisions/`, on `studio-data`) | locked |
| `GET/POST/DELETE /api/unlock` | the write lock | |

## Where the OS writes (and why not to main)

Every commit to `main` can redeploy the studio, and Vercel Hobby allows 100 deploys a day while `main` gets hundreds of
commits. So the only write that goes to `main` is `/api/build` (the director workflow listens there). Reviews and
decisions go to the branch `studio-data`, created from `main` on the first write (`ensureBranch` in `lib/github.js`);
the OS reads them back from there, and agents read them at
`https://raw.githubusercontent.com/Eouchi147/kinoforge/studio-data/films/reviews/<film id>.json`.
`vercel.json` skips builds for every branch other than `main`, and on `main` for commits that do not touch `studio-web/`.

## The review player

The film page shows the frame actually on screen (`requestVideoFrameCallback` where the browser has it), steps by frame
(Left and Right, or the -1 f and +1 f buttons for phones; Shift steps a second; Space or K plays; J and L jump a second)
and pins each note to a frame: `{ t, frame, fps, text, kind, at }`. Clicking a note seeks to `(frame + 0.5) / fps`, inside
the frame. The frame rate comes from the catalog's `fps` when present, else 24 (the readout says "assumed"). The browser's
video element is not guaranteed frame-accurate, so the readout says "frame shown".

## The write lock

The studio is public, and its write routes act with Sam's GitHub token and spend his OpenRouter credit. When the Vercel
environment variable `STUDIO_PASSCODE` is set, every write route above (build, review, decision, and the director chat)
needs an unlock cookie: Sam types the passcode once per device in Settings; `/api/unlock` answers with an httpOnly,
SameSite=Strict cookie signed with HMAC-SHA256 under a key derived from the passcode (changing the passcode signs every
device out; the cookie lasts 90 days). Reads stay open. Without `STUDIO_PASSCODE`, writes work as before and Settings
and the Desk say plainly that writes are open and how to set the passcode. Sam sets it himself on Vercel; agents never
handle keys.

## How to add an app

1. Write `components/os/apps/<Name>.jsx` exporting a component (read shared state with `useOS()`; data with `useFetch`).
2. Add it to `APPS` in `components/os/OS.jsx` (`phone: true` puts it in the phone dock; at most four do, the rest go
   under More) and its id to `APP_IDS` in `components/os/store.js`.
3. Give it an icon in `components/os/icons.jsx` (line geometry, no pictograms) and a line in `APPS` of
   `lib/commands.mjs` (name, hint, search words) so the command bar finds it.
4. Use the shared pieces (`Head`, `Panel`, `Note`) and the tokens in `globals.css`; logical properties only (inline,
   block), so right-to-left languages mirror.

## How to add a command

Commands are plain words parsed in `lib/commands.mjs`: `interpret()` turns the words into one action (a route), and
`search()` lists matches. Add a verb pattern (like `VERB_OPEN`) and a branch in `interpret()` that returns
`{ type, id, label, hint, route }`, then add a case to `tests/commands.test.mjs`. Today it understands: `new` or `make`
(with what, line, format, look, length like `30 s` or `2 min`, `cap $3`, `no music`), `open`, `play` or `watch`,
`approve` or `review` a film, `show` (looks, styles, films, jobs, music, manual, money), `<words> films`, `compare`
two looks, `use` a look, `manual` or `help` plus words, and any app name.

## House rules in the interface

No em dash, en dash or "..." in any word on screen (text that does not fit fades out instead of showing an ellipsis).
No emoji, no cartoon icons. One motion moment (the house lights come up on load); `prefers-reduced-motion` turns all
motion off. Visible keyboard focus everywhere; works from 360 px wide.

## Check before you push

```
cd studio-web
npm ci
npx next build
node tests/flow.mjs              # starts two servers against a mock OpenRouter
node --test tests/*.test.mjs
```

Headless Chromium (Playwright) has no H.264 decoder, so films show "would not play" in screenshots taken that way;
real browsers play them.
