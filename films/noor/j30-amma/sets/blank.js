// placeholder set while building (not used in the final film)
import { Canvas, hex, nightSky } from '../lib.js';
export default function blank(S, cams) { const r = S.cover(300, cams, 60); const C = new Canvas(r, { seed: 9 }); nightSky(C); S.plane('sky', 300, r, C.c); return { update(F) {} }; }
