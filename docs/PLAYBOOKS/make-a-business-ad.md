# Make a business ad or a social video (lane paused)

Paused: Smart Mount's social videos were stopped by Sam on 16 Oct; Bento polish and natural voices wait on him; the paid
parts (AI stills and clips, Lyria, ElevenLabs) need Sam's go per job (`docs/decisions/0008`, `0013`). Use this only when Sam restarts the lane.
Read first: `harness/shots/policies/unmissed.md` (claims, brand), `docs/decisions/0007`, `0008`, `0012`, `docs/SOUL.md`
(business looks), `docs/WORKFLOWS.md` (codead, social), `social/README.md`.

## Steps
1. **Brief:** business (invented and marked Sample, or Sam's own cleared brand), audience, the one idea, the end-card line,
   policy, length (15 to 30 s), aspect.
2. **Style board first** (free stills made in code or Blender), two or three per look; Sam picks. No video before his pick.
3. **Build in code:** `ads/<id>/index.html` + `ad.json` (fixed 1920x1080 stage, `window.KF`, `ads/lib/motion.js`), or a social
   template batch (`social/batches/<client>/<batch>/batch.json`; every word inside the safe box `SAFE` in `social/lib/brief.mjs`).
   Music first: the scene is timed to the audio.
4. **Check locally:** `node harness/dom-render.cjs ads/<id> --stills 1.5,6,12 --stills-only --out out/<id>`;
   social: `node social/lib/check.mjs <batch>` and `node social/lib/safecheck.mjs social/templates/<t>`.
5. **Render** with `codead.yml` or `social.yml` only when Sam approved the look; check every frame; deliver to Sam. Nothing
   is published or sent without him.

## Definition of done
- Claims match the policy word for word; words, logos and numbers set in code; `bash tools/verify.sh` passes; the render
  passed `check-before-showing-sam.md`; Sam approved before anything left the studio.
