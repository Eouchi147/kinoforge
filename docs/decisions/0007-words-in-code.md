# 0007 Words, logos and numbers are set in code, never generated

- **Date:** 15 Oct 2026. **Decided by:** Sam and Claude after the first AI tests.
- **Context:** Image and video models garble text, invent logos and get numbers wrong; a wrong word on screen is a lie.
- **Decision:** Every word, number, URL and logo on screen is drawn by code (HTML/CSS, canvas, Three.js text, Blender text
  objects) with licensed fonts (OFL, in `ads/fonts/`, `social/fonts/`, `harness/node_modules/@fontsource`). AI pictures
  carry no text: prompts say so. House style for words on screen and in narration: no em or en dashes, no "...".
- **Enforced in code:** `tools/verify.sh` gates `text` (dashes and "..." in on-screen and spoken strings) and `prompts`
  (an AI prompt that mentions text, logos or captions without forbidding them); `films/lib/kinetic/compile.js` and the
  director's code guards refuse the same characters; `social/lib/safecheck.mjs` keeps words inside the phone safe zone.
- **Status:** Active.
