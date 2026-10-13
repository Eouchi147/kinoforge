// P13 overlay: rain streaks drawn as whole art pixels (blocks of W/320 canvas px) + a dithered-by-the-pass vignette.
// The overlay is composited BEFORE the kit's pixelate/quantise pass, so everything here lands exactly on the 320x180 grid and palette.
import { rng } from '/harness/kit/film.js';
import { P, K } from './palette.js';

const AW = 320, AH = 180;
const hexCss = (h) => '#' + h.toString(16).padStart(6, '0');
const RAIN_MID = K(2, 4, 5);

function makeStreaks() {
  const R = rng(2024); const fg = [], bg = [];
  for (let i = 0; i < 118; i++) fg.push({ x0: R.int(0, AW - 1), y0: R.int(0, 260), sp: 9 + R.int(0, 3), len: 6 + R.int(0, 2) });
  for (let i = 0; i < 150; i++) bg.push({ x0: R.int(0, AW - 1), y0: R.int(0, 260), sp: 5 + R.int(0, 1), len: 3 + R.int(0, 1) });
  return { fg, bg };
}
const STREAKS = makeStreaks();

export function paintOverlay(ctx, W, H, frame, { rain = 1, vignette = 0.2, refl = [] } = {}) {
  const b = W / AW; ctx.clearRect(0, 0, W, H);
  if (vignette > 0) { // stepped + dithered later by the finish pass
    const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.42, W / 2, H / 2, W * 0.62); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${vignette * 1.25})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  const px = (x, y, hex) => { if (y < 0 || y >= AH) return; ctx.fillStyle = hexCss(hex); ctx.fillRect(Math.floor(((x % AW) + AW) % AW) * b, y * b, b, b); };
  // puddle reflections: broken vertical dashes of each lit sign colour just below the parapet line, jittering on 2s (R-5-02)
  const hs = (a, b, c) => { const v = Math.sin(a * 12.9898 + b * 78.233 + c * 37.719) * 43758.5453; return v - Math.floor(v); };
  const n2 = frame >> 1;
  refl.forEach((q, qi) => { if (q.level <= 0) return; const nseg = Math.max(4, Math.min(14, Math.round(q.len / 2)));
    for (let k = 0; k < nseg; k++) { if (hs(qi, k, n2) < 0.2) continue; const y = Math.round(q.y0 + 2 + k * (q.len / nseg) + hs(qi, k, n2 + 7) * 1.5); const dx = Math.round((hs(qi, k, n2 + 3) - 0.5) * 4); const L = 1 + (hs(qi, k, n2 + 5) < 0.5 ? 1 : 0);
      const hex = (k % 2 && q.hex2) ? q.hex2 : q.hex; for (let j = 0; j < L; j++) { px(Math.round(q.x) + dx, y + j, q.level < 1 ? q.dim : hex); if (q.wide) px(Math.round(q.x) + dx + 1, y + j, q.level < 1 ? q.dim : hex); } } });
  if (!rain) return;
  const draw = (arr, headHex, tailHex, span) => {
    for (const s of arr) {
      const head = (s.y0 + s.sp * frame) % (AH + span) - 2; // wrap with a margin so streaks enter/leave smoothly
      for (let r = 0; r < s.len; r++) { const y = head - r; if (y < 0 || y >= AH) continue; px(s.x0 - Math.floor(y / 3), y, r < 2 ? headHex : tailHex); }
    }
  };
  draw(STREAKS.bg, P.rainBg, K(1, 2, 3), 40); draw(STREAKS.fg, P.rainFg, RAIN_MID, 60);
}
