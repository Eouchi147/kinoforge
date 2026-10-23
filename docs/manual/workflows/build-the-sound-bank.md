# Build the sound bank (rc-render `sfx-bank.yml`)

Builds the studio's library of real recordings as one release: every BigSoundBank (CC0, Joseph Sardin) row of rc-render
`dark/assets.csv` (the Dark Corners sounds) plus the extras in rc-render `sfx/bank_extra.txt`, each checked "CC0" on its
own page, converted to 48 kHz stereo 24-bit FLAC, measured (EBU R128 integrated loudness and true peak), published to
rc-render release `sfx-bank` as `sfx-bank.tar` (folder `sfx-bank/<name>.flac`) and `sfx-bank.csv`
(`name,source,licence,duration_s,lufs_i,true_peak_dbtp,channels_in,rate_in,file`). Free. Run 39890165805 (22 to 23 Oct)
made 197 recordings (138 Dark Corners rows plus 59 extras: birdsong, insects, streams, sea, underwater, gulls, city,
metro, sewer, cave, steam, boiling, splashes). How films use it: `docs/manual/sound/sfx-bank.md`.

## Inputs
None. To add sounds, add lines `<name> bsb:<4-digit id>` to rc-render `sfx/bank_extra.txt` (comments with `#`).

## Exact steps
1. Find the sound on bigsoundbank.com; note its id (page `https://bigsoundbank.com/s<id>.html`).
2. Add `<name> bsb:<id>` to `sfx/bank_extra.txt` in rc-render; commit that file only; pull with rebase; push.
3. Dispatch: `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/sfx-bank.yml/dispatches -f ref=main`.
4. Watch the run (up to 90 min); the log prints `SKIP <name>` for any page without "CC0".
5. Download `sfx-bank.csv` (small) to see what is in; `sfx-bank.tar` is about 1.2 GB: download it once per machine.
6. Commit the refreshed `sfx/sfx-bank.csv` copy in rc-render if you keep one (the 23 Oct one is committed), and log it.

## Alternatives
| Source | When | Cost |
| --- | --- | --- |
| rc-render release `sfx` (the original Dark Corners WAVs) | the exact Dark Corners files | free |
| Synthesised sounds in code (the ads' interface sounds, `harness/shots/codead.py`) | clicks, chimes, whooshes | free |
| Other CC0 libraries | not wired; check each licence page and add a fetch step | free |

## Checks before showing Sam
Every recording used in a film is listed with its source and licence in the film's sound notes
(`films/cutaway/series/SOUND.md` is the model).

## Known traps
- The workflow runs on `ubuntu-latest` (no Playwright, so the gate allows it).
- A Dark Corners row whose page check fails keeps the licence recorded in `dark/assets.csv` and says so in the CSV.
- Stand-ins (a close recording used for a sound the bank lacks) must be named as such in the sound notes.

## Sources of truth
rc-render `.github/workflows/sfx-bank.yml`, rc-render `sfx/bank.sh`, `sfx/bank_extra.txt`, `sfx/sfx-bank.csv`,
`docs/LOG.md` (23 Oct).
