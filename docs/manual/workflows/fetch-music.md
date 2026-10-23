# Fetch music (rc-render `music-fetch.yml`)

Fetches one public domain, CC0 or CC BY recording from Wikimedia Commons into rc-render release `music`, with its licence
record (Commons `extmetadata`: licence, artist, credit, description URL) saved beside it as `<name>.licence.json`. Free.
First use (23 Oct 2026): Borodin, In the Steppes of Central Asia (Musopen Symphony, public domain) for the Fable music
film, asset `borodin-steppes-musopen.flac`. More on choosing and cutting music: `docs/manual/sound/music-fetch.md`.

## Inputs
| Input | Meaning |
| --- | --- |
| `file` | Commons file title without `File:`, e.g. `Borodin_-_In_the_Steppes_of_Central_Asia_(Musopen_Symphony).flac` |
| `name` | short asset name, e.g. `borodin-steppes-musopen` |

## Exact steps
1. Find the recording on commons.wikimedia.org; read its licence on the page (public domain, CC0 or CC BY; for CC BY the
   credit must appear in the film's credits or description). Prefer recordings whose performance is also free (Musopen).
2. Dispatch:
   ```bash
   gh api -X POST repos/Eouchi147/rc-render/actions/workflows/music-fetch.yml/dispatches -f ref=main \
     -f 'inputs[file]=<Commons title>' -f 'inputs[name]=<short-name>'
   ```
3. The log prints the licence record and `ffprobe` (duration, codec, rate, channels). It fails with
   `no such file on Commons` for a wrong title.
4. Download: `gh api repos/Eouchi147/rc-render/releases/tags/music --jq '.assets[] | "\(.id) \(.name)"'`, then by id.
5. Read `<name>.licence.json` yourself (`LicenseShortName`, `UsageTerms`, `Artist`, `Credit`) and write the licence in
   the film's `NOTES.md` and `docs/LICENCES.md`. Add a row to `MUSIC` in `tools/catalog.py`.

## Alternatives
| Source | When | Cost |
| --- | --- | --- |
| The free score engine (`films/lib/score`, VSCO-2 CE CC0 samples plus synthesis) | narrated films, quiet beds under nature sound | free, deterministic |
| Lyria (OpenRouter, streamed) | ads (`codead.yml` prep), a director film with `"music": "lyria"` | about US$0.05 to 0.08 a clip, inside the cap |
| Musopen or archive.org directly | not wired; use Commons copies | free |

## Checks before showing Sam
The licence record says public domain or CC0 (or CC BY with the credit placed). The Musopen credit block on Commons notes
that Musopen's own site materials are copyrighted; the recordings uploaded there are declared public domain.

## Known traps
- Commons asks for a descriptive User-Agent; the workflow sends one.
- A FLAC of a full work is large (Borodin: about 74 MB); cut and encode in the film folder, never commit the source.

## Sources of truth
rc-render `.github/workflows/music-fetch.yml`, release `music`, `docs/STATUS.md` (Fable music film), `docs/LOG.md` (23 Oct).
