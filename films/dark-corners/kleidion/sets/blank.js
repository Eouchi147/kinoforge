// placeholder set (a dark plane) used while a set is not built yet
import { Canvas, hex } from './common.js';
export default function blank(S, cams) {
  const r = S.cover(500, cams); const C = new Canvas(r, { seed: 1 }); C.g.fillStyle = '#141830'; C.g.fillRect(r[0], r[1], r[2] - r[0], r[3] - r[1]); S.plane('bg', 500, r, C.c);
  return { update(F) {} };
}
