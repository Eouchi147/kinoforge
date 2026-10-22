// Documents in candlelight: parchment on a dark desk, ink that writes itself left to right, a candle that relights the paper.
import * as THREE from 'three';
import { clamp, lerp, smoothstep, ease, rng, valueNoise2D } from '/harness/kit/film.js';
import { Setup, setLights, DW, DH } from './lib.js';
import { Canvas, hex, mixc, mul, rgba, underpaint } from './paint.js';
import { WARM, GLOW, coverCams, flick } from './common.js';

const PAPER_DEFAULT = [40, -150, 680, 1450];   // design px on the paper plane (tall: the camera travels down the page)
const INK = '#241609';
const serif = (px, it = true, font = null) => (font ? `500 ${px}px "${font}"` : `${it ? 'italic ' : ''}400 ${px}px "IM Fell English"`);

// content per document: lines {id, text, x, y, px, it, sp, align, col}; extras are drawn into the paper itself
export const DOCS = {
  claim: { lines: [
    { id: 'h', text: 'THE CLAIM', x: 360, y: 330, px: 34, it: false, sp: 10 },
    { id: 'l1', text: 'The owners of the Zong', x: 360, y: 470, px: 56 }, { id: 'l2', text: 'claim the insurance', x: 360, y: 548, px: 56 },
    { id: 'l3', text: 'for the people they drowned.', x: 360, y: 650, px: 46 }, { id: 'l4', text: 'Gregson and others against Gilbert', x: 360, y: 880, px: 30 },
  ] },
  ledger: { ruled: true, paper: [-300, -150, 1020, 1450], lines: [
    { id: 'h', text: 'THE INSURANCE', x: 360, y: 250, px: 36, it: false, sp: 9 }, { id: 'hn', text: 'Name', x: 170, y: 330, px: 34, align: 'left' }, { id: 'hp', text: 'Price', x: 500, y: 330, px: 34, align: 'left' },
    ...Array.from({ length: 10 }, (_, i) => ({ id: 'p' + i, text: '£30', x: 520, y: 420 + i * 62, px: 36, font: 'Cinzel', sp: 3, align: 'left' })),
  ] },
  rule: { lines: [
    { id: 'h', text: 'THE RULE', x: 360, y: 280, px: 34, it: false, sp: 10 },
    { id: 'a1', text: 'Died of sickness', x: 360, y: 440, px: 52 }, { id: 'a2', text: "the owners' loss", x: 360, y: 520, px: 58, col: '#4a1410' },
    { id: 'b1', text: 'Thrown overboard', x: 360, y: 700, px: 52 }, { id: 'b1b', text: 'to save the ship', x: 360, y: 768, px: 46 }, { id: 'b2', text: 'the insurers pay', x: 360, y: 860, px: 58, col: '#4a1410' },
  ] },
  quote: { lines: [
    { id: 'q0', text: '“', x: 112, y: 372, px: 130, align: 'left' },
    { id: 'q1', text: 'It is the case', x: 360, y: 500, px: 78 }, { id: 'q2', text: 'of throwing', x: 360, y: 604, px: 78 }, { id: 'q3', text: 'over goods.”', x: 360, y: 708, px: 78 },
  ] },
  kb: { lines: [
    { id: 'h', text: 'A NEW TRIAL', x: 360, y: 300, px: 34, it: false, sp: 10 },
    { id: 'k1', text: 'after the rain,', x: 360, y: 500, px: 66 }, { id: 'k2', text: 'there seemed to be', x: 360, y: 610, px: 60 }, { id: 'k3', text: 'no need.', x: 360, y: 706, px: 66 },
  ] },
};

function drawInk(C, ln) {
  const g = C.g; g.save(); g.font = serif(ln.px, ln.it !== false, ln.font); g.fillStyle = ln.col || INK; g.textBaseline = 'alphabetic'; if (ln.sp) g.letterSpacing = ln.sp + 'px';
  const w = g.measureText(ln.text).width; const x0 = ln.align === 'left' ? ln.x : ln.x - w / 2; const R = C.R;
  // ink bleed: a faint wide pass, the body, and a few lighter re-strokes
  g.globalAlpha = 0.18; g.shadowColor = ln.col || INK; g.shadowBlur = 3; g.fillText(ln.text, x0, ln.y); g.shadowBlur = 0;
  for (let k = 0; k < 3; k++) { g.globalAlpha = k === 0 ? 0.92 : 0.28; g.fillText(ln.text, x0 + (k ? (R() - 0.5) * 0.9 : 0), ln.y + (k ? (R() - 0.5) * 0.9 : 0)); }
  g.restore(); return { x0, w };
}

export function buildDoc(kind, shots) {
  const S = new Setup('doc-' + kind, { pos: [0, 0, 0], mm: 35 }); const f = S.f; const cams = coverCams(shots, 'doc:' + kind); const cover = (D, m) => S.cover(D, cams, m);
  const spec = DOCS[kind]; const planes = {}; const D = { desk: 15, paper: 12.5, ink: 12.45, quill: 11.6, candle: 6 };
  // desk: dark wood, long grain running across
  { const r = cover(D.desk, 30); const C = new Canvas(r, { seed: 801 }); const n = C.n;
    underpaint(C, (x, y) => mixc(hex('#2a1b14'), hex('#120b0a'), smoothstep(200, 1200, y)), null, 12);
    C.strokes({ n: C.area / 600, color: (x, y) => mixc(hex('#3a2519'), hex('#1b100c'), n.fbm(x * 0.004, y * 0.03, 3)), angle: (x, y) => 0.04 + (n.fbm(x * 0.003, y * 0.01, 2) - 0.5) * 0.12, len: [60, 200], wid: [3, 8], alpha: [0.3, 0.6], jv: 0.12, bend: 0.03 });
    C.mottle({ amt: 0.06 }); planes.desk = S.plane('desk', D.desk, r, C.c); }
  // paper
  const [px0, py0, px1, py1] = spec.paper || PAPER_DEFAULT;
  { const r = [px0 - 30, py0 - 30, px1 + 30, py1 + 30]; const C = new Canvas(r, { seed: 811 }); const n = C.n, R = C.R; const g = C.g;
    const edge = (x, y) => { const dx = Math.min(x - px0, px1 - x), dy = Math.min(y - py0, py1 - y); return Math.min(dx, dy) + (n.fbm(x * 0.05, y * 0.05, 3) - 0.5) * 14; };
    const path = new Path2D(); const pts = []; const N = 120; for (let i = 0; i < N * 4; i++) { const s = i / (N * 4); let x, y; const q = Math.floor(i / N), u = (i % N) / N;
      if (q === 0) { x = lerp(px0, px1, u); y = py0; } else if (q === 1) { x = px1; y = lerp(py0, py1, u); } else if (q === 2) { x = lerp(px1, px0, u); y = py1; } else { x = px0; y = lerp(py1, py0, u); }
      x += (n.fbm(x * 0.06 + 3, y * 0.06, 3) - 0.5) * 8; y += (n.fbm(x * 0.06, y * 0.06 + 9, 3) - 0.5) * 8; i ? path.lineTo(x, y) : path.moveTo(x, y); } path.closePath();
    const col = (x, y) => { const e = clamp(edge(x, y) / 60); let c = mixc(hex('#e2c58c'), hex('#caa96a'), n.fbm(x * 0.006, y * 0.006, 3)); c = mixc(hex('#8d6a38'), c, smoothstep(0, 1, e) * 0.9 + 0.1); return c; };
    underpaint(C, col, path, 6); const m = C.mask((gg) => gg.fill(path));
    C.strokes({ n: C.area / 420, mask: m, color: col, angle: () => (R() - 0.5) * 3.1, len: [10, 40], wid: [3, 7], alpha: [0.25, 0.5], jv: 0.06, bend: 0.2 });
    for (let i = 0; i < 26; i++) { const x = lerp(px0, px1, R()), y = lerp(py0, py1, R()); C.dab(x, y, R() * 3, 60 + R() * 120, 30 + R() * 60, hex('#9a7440'), 0.05 + R() * 0.07, 0.3, 0.9); }
    // fold creases
    for (const yy of [py0 + (py1 - py0) * 0.5]) { for (let x = px0; x < px1; x += 5) C.dab(x, yy + (n.fbm(x * 0.02, 1, 2) - 0.5) * 3, 0, 14, 2.4, hex('#6d4e28'), 0.22, 0.0, 0.5); for (let x = px0; x < px1; x += 6) C.dab(x, yy + 3, 0, 14, 1.8, hex('#f3dcaa'), 0.2, 0, 0.5); }
    if (spec.ruled) { g.strokeStyle = 'rgba(70,45,20,0.35)'; g.lineWidth = 1.6; for (let i = 0; i < 16; i++) { const y = 372 + i * 62; g.beginPath(); g.moveTo(px0 + 60, y); g.lineTo(px1 - 60, y); g.stroke(); }
      g.beginPath(); g.moveTo(450, 290); g.lineTo(450, 1000); g.moveTo(96, 290); g.lineTo(96, 1000); g.moveTo(px1 - 60, 290); g.lineTo(px1 - 60, 1000); g.stroke(); }
    C.mottle({ amt: 0.06, cell: 16 }); planes.paper = S.plane('paper', D.paper, r, C.c); planes.paper.rotation.z = -0.018; planes.paper.userData.rot = -0.018; }
  // ink lines: each its own plane at the same depth so it can write itself (uWipe) and be lit with the paper
  const lines = {};
  for (const ln of spec.lines) { const tmp = document.createElement('canvas').getContext('2d'); tmp.font = serif(ln.px, ln.it !== false, ln.font); if (ln.sp) tmp.letterSpacing = ln.sp + 'px'; const w = tmp.measureText(ln.text).width;
    const x0 = ln.align === 'left' ? ln.x : ln.x - w / 2; const r = [Math.floor(x0 - 20), Math.floor(ln.y - ln.px * 1.1), Math.ceil(x0 + w + 24), Math.ceil(ln.y + ln.px * 0.5)];
    const C = new Canvas(r, { seed: 830 + ln.id.length }); drawInk(C, ln); const pl = S.plane('ink-' + ln.id, D.ink, r, C.c); pl.rotation.z = -0.018; pl.userData.ln = ln; pl.visible = false; lines[ln.id] = pl; }
  // quill + inkwell, lying at the lower right of the paper
  { const r = [300, 980, 740, 1260]; const C = new Canvas(r, { seed: 851 }); const g = C.g; const R = C.R;
    // feather: shaft from nib (330,1230) toward (700,1020), barbs as angled strokes
    const a = [336, 1232], b = [716, 1010]; const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
    for (let i = 0; i < 120; i++) { const u = 0.28 + 0.72 * (i / 120); const x = lerp(a[0], b[0], u), y = lerp(a[1], b[1], u); const len = (46 + 20 * Math.sin(u * 3)) * (1 - 0.4 * u); for (const sd of [-1, 1]) C.dab(x + Math.cos(ang + sd * 1.15) * len * 0.4, y + Math.sin(ang + sd * 1.15) * len * 0.4, ang + sd * 0.6, len, 3.2, mixc(hex('#cdbfa6'), hex('#7a6a58'), R() * 0.8), 0.7, 0.1, 0.8); }
    g.strokeStyle = rgba(hex('#2e241d')); g.lineWidth = 4; g.lineCap = 'round'; g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.stroke(); g.strokeStyle = rgba(hex('#e9d7b2'), 0.5); g.lineWidth = 1.4; g.beginPath(); g.moveTo(a[0] + 1, a[1] - 2); g.lineTo(b[0] + 1, b[1] - 2); g.stroke();
    g.fillStyle = rgba(hex('#16100c')); g.beginPath(); g.moveTo(...a); g.lineTo(a[0] - 10, a[1] + 14); g.lineTo(a[0] + 6, a[1] + 4); g.fill();
    C.blur(0.6); planes.quill = S.plane('quill', D.quill, r, C.c); planes.quill.rotation.z = 0; }
  // the candle itself stays out of frame (upper right); its flame is the light: glow sprites + relight
  { const r = [560, 20, 900, 300]; const C = new Canvas(r, { seed: 861 }); C.g.fillStyle = 'rgba(0,0,0,0.0)'; C.g.fillRect(0, 0, 4, 4); planes.candle = S.plane('candle', D.candle, r, C.c); planes.candle.userData.flame = [722, 216]; }
  const fp = planes.candle.userData.flame; const flame = S.glow(fp[0], fp[1], D.candle, 120, { color: GLOW, core: 22 }, planes.candle); const flameCore = S.glow(fp[0], fp[1] + 6, D.candle, 46, { color: [1, 0.9, 0.62], core: 20 }, planes.candle);
  const halo = S.glow(fp[0] - 40, fp[1] + 120, D.paper - 2, 900, { color: [1.0, 0.55, 0.22], core: 5000 }, planes.candle); // soft warm air around the candle
  const dust = Array.from({ length: 46 }, (_, i) => { const R = rng(900 + i); return { x: R() * DW, y: R() * DH, z: R(), s: 0.6 + R() * 1.4, ph: R() * 6.28, sp: 0.3 + R() * 0.5 }; });
  // tint the paper/desk down so the candle does the lighting
  planes.desk.material.uniforms.uTint.value.set(0.34, 0.3, 0.3); planes.paper.material.uniforms.uTint.value.set(0.27, 0.23, 0.22); for (const k in lines) lines[k].material.uniforms.uTint.value.set(0.27, 0.23, 0.22); planes.quill.material.uniforms.uTint.value.set(0.3, 0.26, 0.24);
  const api = {
    key: 'doc:' + kind, S, planes, lines, cams,
    show(v) { S.group.visible = v; },
    update(t, sh) {
      const ink = sh.ink || {}; const fl = flick(t, 5) * (sh.candle ?? 1);
      for (const [id, pl] of Object.entries(lines)) { const t0 = ink[id]; if (t0 === undefined) { pl.visible = sh.inkAll ? true : false; pl.material.uniforms.uWipe.value.set(2, 0.001); continue; } const d = (pl.userData.ln.dur || 0.9) * (sh.inkSpeed || 1); pl.visible = t >= t0; const k = clamp((t - t0) / d); pl.material.uniforms.uWipe.value.set(ease.outSine(k) * 1.12, 0.12); }
      const wp = new THREE.Vector3(); const fw = S.world(fp[0], fp[1], D.candle, wp); flame.position.copy(fw); flameCore.position.copy(fw).add(new THREE.Vector3(0, -6 * D.candle / f, 0)); flame.material.uniforms.uI.value = 1.5 * fl; flameCore.material.uniforms.uI.value = 1.1 * fl; planes.candle.material.uniforms.uTint.value.set(0.7, 0.62, 0.55);
      halo.material.uniforms.uI.value = 0.04 * fl;
      const lp = fw.clone(); lp.z = -D.paper + 2.2; const L = [{ p: lp, r: 2.0, c: [1.0, 0.6, 0.3], k: 2.6 * fl }]; for (const k of ['desk', 'paper', 'quill']) setLights(planes[k].material, L.map((l) => ({ ...l, k: l.k * (k === 'desk' ? 0.8 : 1) }))); for (const id in lines) setLights(lines[id].material, L);
    },
    draw(g, e) { // dust motes in the candle light
      for (const d of dust) { const x = ((d.x + e.t * 7 * d.sp * (d.z + 0.3)) % (DW + 40)) - 20, y = ((d.y - e.t * 4 * d.sp) % (DH + 40) + DH + 40) % (DH + 40) - 20; const k = Math.exp(-(((x - 690) / 330) ** 2 + ((y - 300) / 520) ** 2)); const a = 0.55 * k * (0.5 + 0.5 * Math.sin(e.t * 1.6 + d.ph)); if (a < 0.02) continue; g.fillStyle = `rgba(255,214,150,${a.toFixed(3)})`; g.beginPath(); g.arc(x, y, d.s * 1.1, 0, 6.3); g.fill(); }
    },
  };
  S.group.visible = false; return api;
}
