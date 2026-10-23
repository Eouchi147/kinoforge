# Sound: `music-fetch.yml` and the public-domain music rule

When a film is built on an existing piece of music (the planned Cutaway "Fable" film on Borodin), the recording must be
clean for a worldwide, possibly monetised film: public domain or CC0, or CC BY with a credit line. rc-render workflow
`music-fetch.yml` fetches such a recording from Wikimedia Commons into the public release `music` of `Eouchi147/rc-render`,
together with its licence record as Commons states it (`<name>.licence.json`). It is free. The rule for choosing a recording
comes from `docs/research/CUTAWAY_USES_AND_MUSIC_2026-10.md` (23 Oct 2026).

## The rule (from the research, part 1)
1. Composer out of copyright AND the recording itself cleared. The composition being old is not enough: a performance has its
   own rights.
2. Usable: CC0 or "public domain" recordings (Musopen's 2012 recordings released into the public domain or CC0), US federal
   government band recordings (public domain in the US; outside the US, a lawyer question), US recordings old enough for the
   Music Modernization Act schedule (1925 recordings entered the US public domain on 1 Jan 2026; 1927 not until 1 Jan 2028),
   and CC BY recordings with a credit line ("Music: <piece>, <orchestra>, via Musopen, CC BY 3.0").
3. Not usable: IMSLP rows marked "Public Domain - Non-PD US" (1950s and 60s recordings still protected in the US); any NC,
   ND or SA licence (ShareAlike would pull the film into SA); unclear licences (the "EFF Open Audio License" youth recording,
   unchecked).
4. Before production: open the file page, copy the exact licence text, source URL and retrieval date into the film's docs;
   fetch the file from a machine with network access (the research sandbox could not reach Commons or Musopen); add the
   credit line when required. Items marked LAWYER in the research (worldwide status of US-government recordings, Canadian
   and EU terms for 1920s recordings, whether a description credit is enough) are open.
5. Shortlist (ranked): Borodin, In the Steppes of Central Asia (Musopen 2012, CC0 or public domain; 7:38) best fit;
   Grieg, Peer Gynt Suite No. 1 (Musopen 2012, CC BY 3.0 on IMSLP: credit Musopen); Saint-Saens, Orient et Occident (US Marine
   Band, public domain in the US); Glazunov, Chant du menestrel (Musopen, public domain). No clean recording was found of
   Scheherazade, Flight of the Bumblebee, Danse Macabre, the Sorcerer's Apprentice, the Nutcracker, Polovtsian Dances or Ravel.

## Inputs
- The Commons file title without `File:` and a short asset name.

## Exact steps
1. Dispatch:
   `gh api -X POST repos/Eouchi147/rc-render/actions/workflows/music-fetch.yml/dispatches -f ref=main -f 'inputs[file]=Borodin_-_In_the_Steppes_of_Central_Asia_(Musopen_Symphony).flac' -f 'inputs[name]=borodin-steppes-musopen'`
2. The job (ubuntu-24.04) queries the Commons API (`prop=imageinfo`, `iiprop=url|size|mime|extmetadata`) with a KINOFORGE
   user agent, writes `<name>.licence.json` (`file`, `url`, `page`, `size`, `mime`, and `licence`: `LicenseShortName`,
   `License`, `LicenseUrl`, `UsageTerms`, `Copyrighted`, `Artist`, `Credit`, `ImageDescription`, `DateTimeOriginal`,
   `AttributionRequired`, `Restrictions`), downloads the file as `<name>.<ext>`, prints its duration and codec with ffprobe,
   creates release `music` if needed and uploads both with `--clobber`. It fails with "no such file on Commons" on a wrong title.
3. Read the licence record before use (download by asset id:
   `gh api repos/Eouchi147/rc-render/releases/tags/music --jq '.assets[] | "\(.id) \(.name)"'` then
   `gh api -H "Accept: application/octet-stream" repos/Eouchi147/rc-render/releases/assets/<id> > <file>`).
4. Copy the licence facts and the credit line into the film's NOTES.md; cut the music on phrase ends (the Fable plan names cuts
   at 1:57 and 3:17, the long cut by default).

## Recorded fetch
Run 40023819924 (23 Oct, success): `borodin-steppes-musopen.flac` (73,785,694 bytes, audio/flac) and
`borodin-steppes-musopen.licence.json`. Commons record: LicenseShortName "Public domain", `Copyrighted` "False",
`AttributionRequired` "false", DateTimeOriginal 2012, page
`https://commons.wikimedia.org/wiki/File:Borodin_-_In_the_Steppes_of_Central_Asia_(Musopen_Symphony).flac`.
Open point from the research: Wikipedia names the Czech Philharmonic, IMSLP the Czech National Symphony Orchestra; credit
"Musopen" and verify the orchestra on the Musopen page before any credits.

## Alternatives
| Route | When | Cost |
| --- | --- | --- |
| The free score engine (`score-engine.md`) | any film that does not need a known piece | free, no licence question |
| Lyria | ads; rejected for battles | about US$0.04 to 0.08 a clip |

## Known traps
- The chat sandbox's proxy blocks Commons, Musopen and archive.org: fetch on a runner.
- Labels on IMSLP can disagree for recordings of the same project (CC0 on one, CC BY 3.0 on another): treat as CC BY and credit.

## Sources of truth
rc-render `.github/workflows/music-fetch.yml`, release `music`, `docs/research/CUTAWAY_USES_AND_MUSIC_2026-10.md` (part 1),
`docs/STATUS.md` (Cutaway art directions), `docs/LOG.md` (23 Oct).
