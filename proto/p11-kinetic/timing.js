// P11 KINETIC — TIMING. Single source of truth for picture (scene.js imports it) and sound (audio.py parses the object below as JSON).
// Frames are integers @ 24 fps (seconds = frame / 24). Keep the exported object strict JSON: no comments inside, no trailing commas.
export default {
  "fps": 24,
  "total": 192,
  "beats": [
    { "id": "B1", "name": "B1 year slam", "f0": 0, "f1": 34 },
    { "id": "B2", "name": "B2 verdict on the beat", "f0": 34, "f1": 72 },
    { "id": "B3", "name": "B3+B4 interrupt, letter, written line", "f0": 72, "f1": 130 },
    { "id": "B5", "name": "B5 secret, broken hand", "f0": 130, "f1": 168 },
    { "id": "B6", "name": "B6 silence, part marker, open loop", "f0": 168, "f1": 192 }
  ],
  "b1": { "slam": 0, "rule": 4, "dateline": 6 },
  "b2": { "words": { "A": 34, "MAYOR": 40, "WAS": 46, "EXECUTED": 52 }, "witch": 58, "ulStart": 60, "ulEnd": 65 },
  "b3": { "cut": 72, "dipFrames": 3, "launch": 75, "rest": 86 },
  "b4": { "typeStart": 78, "glyphMs": 40, "wipeMs": 70, "dryMs": 220 },
  "b5": { "t2": 130, "t2Wipe": 5, "t3": { "With": 144, "a": 148, "broken": 152, "hand.": 156 }, "ulStart": 158, "ulEnd": 164, "heartbeats": [132, 156] },
  "b6": { "silenceFrom": 168, "label": 180, "arrowStart": 182, "arrowShaftEnd": 186, "arrowEnd": 188 }
};
