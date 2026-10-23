# Quality checks before Sam sees anything

Nothing reaches Sam before it passes these checks. "It rendered" is not a check: run the numbers, then look with your
own eyes. If you cannot open images, stop and say so; never claim a visual check you did not do. The playbook is
`docs/PLAYBOOKS/check-before-showing-sam.md`; this page adds the per-kind targets the record shows.

## Inputs
- The finished file (release asset or Mac-lane encode), the film folder (`film.json`, `NOTES.md`, the brief), Sam's last
  notes on the film or its style (`docs/SOUL.md` section 3, `films/director/CRAFT.md`).

## Exact steps
1. Get the file by asset id:
   `gh api repos/Eouchi147/<repo>/releases/tags/<release> --jq '.assets[] | "\(.id) \(.name)"'` then
   `gh api -H "Accept: application/octet-stream" repos/Eouchi147/<repo>/releases/assets/<id> > film.mp4`.
2. Numbers:
   - length equals `film.json` `duration` within a frame: `ffprobe -v error -show_entries format=duration -of csv=p=0 film.mp4`
   - size and rate as `film.json` (`w`, `h`, `fps`): `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 film.mp4`
   - loudness and peak: `ffmpeg -nostdin -i film.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12`
   - frozen or black stretches: `ffmpeg -nostdin -i film.mp4 -vf "freezedetect=n=0.003:d=2,blackdetect=d=0.5" -an -f null - 2>&1 | grep -E "freeze_|black_"`
3. Contact sheet every 2 s, and look at all of it:
   `ffmpeg -nostdin -i film.mp4 -vf "fps=0.5,scale=320:-2,tile=8x10" -frames:v 1 sheet.jpg` (for 20 s films use `fps=1`).
4. Watch at least three moving stretches of 5 s: the opening, the turn, the end. For a loop, the seam.
5. Compare with the brief, the `NOTES.md` weak spots and Sam's last notes.
6. Write the result in `docs/LOG.md` (numbers, what you looked at) and in the message: results first, then the weak spots.

## Targets from the record
| Kind | Loudness | Other |
| --- | --- | --- |
| Narrated films (Battle Map, Venice, Dark Corners, NOOR) | about -14 LUFS (battles -14.2, Venice -14.1), true peak under -1 dBTP | voice about 16 to 17.5 dB over the score |
| Cutaway showcase and nature films (no voice) | about -16 LUFS (series -16.2 to -16.4, meadow -16) | score's loudest 3 s about 10 dB under the nature recordings |
| Ads and social | -14 LUFS | every word inside the safe box (social: x 0.11 to 0.78, y 0.15 to 0.65, rule R-2-08) |
| Loops | as the film | seam smaller than a normal frame step |
| Films with inserts | as the film | look at the first and last frame of each insert span |

## What to reject on the sheet and in motion
Text that overlaps, clips or is misspelled; a dash or "..." on screen; emoji or cartoon icons; units passing through
each other; blank or bare frames; warped shapes; sped-up moves; cuts with no reason; jitter or pops; sound that fights
the voice; anything that reads as alcohol or pork for a halal-friendly client; any depicted person in NOOR where none
may be (no prophets, angels or Companions); claims outside the client's own written words.

## Alternatives
- Before a full render: check stills (`../workflows/check-stills.md`) and, for the Cutaway line, the validator and a
  400 px contact sheet (`films/lib/cutaway/tools/stills.py`).
- Director films: `films/director/check.cjs` and the eyes gate already ran; still do steps 2 to 5 yourself.

## Known traps
- A render that "succeeded" can still have a hung part re-run with a gap, a missing insert (Agincourt insert B on 22 Oct)
  or text overprinting at card changes (Bamberg, 148 s): look at boundaries.
- Fanless Mac renders can differ in speed, never in pixels; frames on the exFAT drive have `._` twins: count with
  `ls frames/[0-9]*.png`.
- Weak spots are part of the delivery: name them (for example "River's water reads as a pale grey trench").

## Sources of truth
`docs/PLAYBOOKS/check-before-showing-sam.md`, `docs/WORKFLOWS.md` ("Checking a result"), `docs/LOG.md` (measured
loudness), `films/director/CRAFT.md`, `docs/SOUL.md`.
