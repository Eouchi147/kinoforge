# Check a render before showing Sam

Nothing reaches Sam before it passes this. "It rendered" is not a check. Run the numbers, then look with your own eyes.
If you cannot open images, stop and say so: do not claim the visual check.

## Steps
1. **Get the file** (asset id from the release listing; works where `gh release download` does not):
   `gh api -H "Accept: application/octet-stream" repos/Eouchi147/<repo>/releases/assets/<asset id> > film.mp4`
2. **Numbers, first check, always: `tools/qc.py`** (ffmpeg and ffprobe only, free):
   `python3 tools/qc.py film.mp4 --film films/<kind>/<id> --out qc/qc.json`
   It checks length and size against `film.json`, loudness (target from `film.json` `lufs`, else -16 for Cutaway showcase
   and loop films, else -14; within 1 LU), true peak at or below -1 dBTP, dead air, frozen stretches (not for loops),
   black frames, unplanned hard cuts (none allowed when `film.json` says `"cuts": false`, or for a loop, a seasons style or a
   Cutaway showcase), flicker and the loop seam. It writes `qc.json` (pass or fail, numbers, exact commands) and `qc-sheet.jpg`
   beside it and exits 1 on any fail. Fix every fail or name it in the message to Sam. Do not run later steps to excuse a
   failed gate. Manual equivalents, for one number by hand:
   - Length equals `film.json` `duration` (within a frame): `ffprobe -v error -show_entries format=duration -of csv=p=0 film.mp4`
   - Size and frame rate as `film.json` (`w`, `h`, `fps`): `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 film.mp4`
   - Loudness about -14 LUFS (-16 for Cutaway), true peak under -1 dBTP: `ffmpeg -nostdin -i film.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12`
   - No frozen or black stretches that were not meant: `ffmpeg -nostdin -i film.mp4 -vf "freezedetect=n=0.003:d=2,blackdetect=d=0.5" -an -f null - 2>&1 | grep -E "freeze_|black_"`
3. **Contact sheet:** `qc-sheet.jpg` (about 20 tiles) is the first one; for finer, every 2 s, and look at all of it:
   `ffmpeg -nostdin -i film.mp4 -vf "fps=0.5,scale=320:-2,tile=8x10" -frames:v 1 sheet.jpg`
   Reject: text that overlaps, clips the frame or is misspelled; a dash or "..." on screen; emoji or cartoon icons; units
   passing through each other; blank or bare frames; warped shapes; anything that reads as alcohol or pork for a
   halal-friendly client; a person depicted in NOOR where none may be.
4. **Watch moving stretches:** the opening, the turn, the end (at least 5 s each). Look for sped-up moves, jitter, pops,
   cuts with no reason, sound that fights the voice.
5. **Compare against the brief and `NOTES.md` weak spots,** and against Sam's last notes on this film or style.
6. **Write the result** in `docs/LOG.md` (numbers and what you looked at) and in the message to Sam: results first, the
   link or file, then the weak spots in one or two lines.

## Definition of done
- `tools/qc.py` exits 0 (or each fail is named in the message); all numbers in range; the full sheet and three moving stretches looked at; every fault fixed or named in the message.
