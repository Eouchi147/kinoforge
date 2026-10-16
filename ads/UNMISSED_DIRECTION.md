# Unmissed ads: direction notes shared by all five versions (16 Oct 2026)

Sam's brief: "dynamic, modern, premium, genially directed and orchestrated." v4 of `unmissed-01` was rejected as poor
quality: one layout repeated five times, slow drifting moves, nothing cut to the music, small dim visuals, flat voice.

## The craft bar (every version)
- **Music first.** The score exists before the picture (`audio/music.mp3`, beat map in `audio/music.json`). Every cut, word
  entrance, camera move and colour change lands on a beat or a half-beat. Big moments land on downbeats or on the drop
  (`biggest_rise_s`, and the `energy` curve, 0.1 s steps). Nothing idles for more than about 1.5 s.
- **Scale and contrast.** Words that matter are big (120 to 420 px on the 1920x1080 stage), tight tracking (-0.03 to -0.05 em),
  high contrast. Nothing important under 36 px. Safe margin 96 px. One idea per frame.
- **Real motion design moves.** Hard cuts on the beat, masked reveals, scale punches (1.15 to 1.0 in 4 to 6 frames, expo-out),
  whip transitions, zoom-throughs, match cuts, parallax layers, a camera that moves (the whole stage scales and drifts), light
  (glows, blooms, flares done with layered blur), colour flashes on accents. Easing: expo-out entrances, quick exits.
  Avoid slow floaty fades and generic "rise and hold" on everything.
- **Variety.** Every shot is composed differently. No layout repeats more than twice in a row.
- **Rendering.** Motion blur is on (`render.sub` in ad.json, 4 sub-frames), film grain in post (`post.grain`). Design for it:
  fast moves read as blur, so use them.
- **Voice.** Prepared and cast by `prep.py` (`audio/vo.json` or `audio/dialogue.json`). Place each line on a beat in
  ad.json `audio.vo[].start`. Never speed a line up; move the next cue instead.
- **Honesty and brand.** Claims only in the site's words (`harness/shots/policies/unmissed.md`). No em or en dashes, no "...".
  Demos show an invented business and say "Demo with an invented business". End card: ring logo with the node at one o'clock
  (ring #2f7df6, node #79b4ff), "Unmissed", "A premium presence. An AI front desk.", small "Made with AI, checked by a person".

## Files each version owns (`ads/<id>/`)
- `TREATMENT.md`: the director's treatment.
- `ad.json`: `prep` (done), then the builder adds `audio` (music file and offset, gains, voice/dialogue files with start
  times), `sfx` (cue times and kinds: ring, click, pop, whoosh, check, chime, impact, tick, riser) and `cues` (named scene
  times). The scene reads `./ad.json` at load, so picture and sound share one timeline.
- `index.html`: the scene (fixed 1920x1080 stage, `window.KF = { duration, fps: 30, render(i, t) }`, every style set from `t`,
  `KF_READY` after fonts, images and ad.json load). Shared helpers: `/ads/lib/motion.js`. Fonts: `/ads/fonts/`.

## Palette and type
- Night: bg #05070f, glow #0b1530 / #070c1c, ink #f4f6fb, ink2 #c3cad8, ink3 #98a1b5, accent #79b4ff, action blue #2f7df6,
  deep #0b3b8f, violet #8c6eff (logo only), ok #5ad69a, alert #ff6b6b.
- Day (Bento only): bg #f4f6fa, surface #ffffff, ink #0b1020, ink2 #3d4658, accent #2456c9, soft blue #e7eeff.
- Type: Instrument Sans (variable: weight 400 to 700, width 75% to 100%), JetBrains Mono for small labels.
