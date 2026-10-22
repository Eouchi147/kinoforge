// All type for the film, drawn crisp on the overlay after the paint pass: captions, place labels, the title and end cards,
// the word Iqra writing itself, the illuminated verse panel. Arabic is set ONLY in Amiri Quran from cues.arabic (copied from
// the King Fahd Complex Uthmani text in script.json), right to left. House rule: no em or en dashes, no "..." on screen.
import { drawText, ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { DW, DH } from './kf.js';

const GOLD = '#e2c06a', BONE = '#efe6d3', INK_SH = 'rgba(3,3,12,0.92)';
const capFont = 'italic 400 30px "Cormorant Garamond"';

function wrap(g, text, maxW, font) { g.save(); g.font = font; const words = text.split(' '); const lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } if (cur) lines.push(cur); g.restore(); return lines; }

export function capDraw(og, text, a, { y = 650, maxW = 980, size = 30, shade = 0.5 } = {}) {
  const font = `italic 400 ${size}px "Cormorant Garamond"`; const lines = wrap(og, text, maxW, font); const lh = size * 1.25; const y0 = y - (lines.length - 1) * lh;
  og.save(); const gr = og.createLinearGradient(0, y0 - 70, 0, DH); gr.addColorStop(0, 'rgba(4,4,14,0)'); gr.addColorStop(1, `rgba(4,4,14,${shade * a})`); og.fillStyle = gr; og.fillRect(0, y0 - 70, DW, DH - y0 + 70); og.restore();
  lines.forEach((l, i) => drawText(og, l, { x: DW / 2, y: y0 + i * lh, font, color: BONE, alpha: a, spacing: 0.4, shadow: 12, shadowColor: INK_SH }));
}

// Arabic, right to left, centred at (x, y); reveal u (0..1) wipes in from the right like a pen writing
export function arabic(og, text, x, y, size, { a = 1, color = GOLD, reveal = 1, glow = 0.6, halo = 0 } = {}) {
  if (a <= 0.003 || reveal <= 0) return;
  og.save(); og.font = `400 ${size}px "Amiri Quran"`; og.direction = 'rtl'; og.textAlign = 'center'; og.textBaseline = 'middle';
  const w = og.measureText(text).width + size * 0.6;
  if (reveal < 1) { og.beginPath(); og.rect(x + w / 2 - w * reveal - size * 0.2, y - size * 1.4, w * reveal + size * 0.4, size * 2.8); og.clip(); }
  og.globalAlpha = a; og.shadowColor = `rgba(255,190,90,${0.55 * glow})`; og.shadowBlur = size * 0.45; og.fillStyle = color; og.fillText(text, x, y);
  og.shadowColor = INK_SH; og.shadowBlur = 6; og.fillText(text, x, y);
  if (halo) { og.shadowBlur = 0; og.lineWidth = size * 0.02; og.strokeStyle = 'rgba(255,236,190,0.9)'; og.strokeText(text, x, y); }
  og.restore();
}

function label(og, L, a, F) {
  const x = L.x ?? 250, y = L.y ?? 120;
  drawText(og, L.text, { x, y, font: '500 26px "Cinzel"', color: '#ead9b4', alpha: a, spacing: 6, shadow: 10, shadowColor: INK_SH, align: 'left' });
  if (L.sub) drawText(og, L.sub, { x, y: y + 34, font: 'italic 400 24px "Cormorant Garamond"', color: '#d8cdb8', alpha: a * 0.92, spacing: 0.8, shadow: 10, shadowColor: INK_SH, align: 'left' });
  if (L.at && F.S && F.shot.set === 'mountain') { // a hairline leader to the place it names
    const D = F.S.planes.find((p) => p.userData.name === L.at[0])?.userData.D; if (!D) return; const p = F.P(D, L.at[1], L.at[2]);
    const sx = x + 6, sy = y + (L.sub ? 52 : 22); og.save(); og.globalAlpha = a * 0.8; og.strokeStyle = '#d9c38c'; og.lineWidth = 1; og.beginPath(); og.moveTo(sx, sy); og.lineTo(lerp(sx, p[0], 0.5), sy); og.lineTo(p[0] - 8, p[1] - 8); og.stroke();
    og.beginPath(); og.arc(p[0], p[1], 9, 0, 7); og.stroke(); og.restore();
  }
}

function titleCard(og, F, sh) {
  const T = F.CUES.marks.title; const lt = F.t - T[0]; if (lt < 0) return false; const out = 1 - smoothstep(sh.t1 - 0.8, sh.t1 - 0.1, F.t);
  const a1 = ease.outCubic(clamp((lt - 0.3) / 1.2)) * out, a2 = ease.outCubic(clamp((lt - 1.1) / 1.2)) * out, a3 = ease.outCubic(clamp((lt - 1.9) / 1.2)) * out;
  drawText(og, 'NOOR', { x: DW / 2, y: 170, font: '500 74px "Cinzel"', color: '#ead9b4', alpha: a1, spacing: 22, shadow: 18, shadowColor: INK_SH });
  const wl = 300 * a2; og.save(); og.globalAlpha = 0.75 * a2; og.fillStyle = '#c9a227'; og.fillRect(DW / 2 - wl / 2, 220, wl, 1.5); og.restore();
  drawText(og, 'The Descent', { x: DW / 2, y: 262, font: 'italic 400 42px "Cormorant Garamond"', color: BONE, alpha: a2, spacing: 1.2, shadow: 14, shadowColor: INK_SH });
  drawText(og, 'NIGHT FIVE  ·  IQRA', { x: DW / 2, y: 316, font: '500 22px "Cinzel"', color: '#d8c79c', alpha: a3, spacing: 7, shadow: 10, shadowColor: INK_SH });
  arabic(og, F.CUES.arabic.iqra, DW / 2, 392, 64, { a: a3, reveal: ease.inOutSine(clamp((lt - 1.9) / 1.3)) });
  return true;
}

function endCard(og, F, sh) {
  const t0 = sh.endAt ?? F.CUES.marks.end[0]; const lt = F.t - t0; if (lt < 0) return false;
  const a1 = ease.outCubic(clamp((lt) / 1.2)), a2 = ease.outCubic(clamp((lt - 0.8) / 1.2));
  drawText(og, 'NOOR', { x: DW / 2, y: 520, font: '500 46px "Cinzel"', color: '#ead9b4', alpha: a1, spacing: 16, shadow: 16, shadowColor: INK_SH });
  drawText(og, 'Thirty Nights of Light', { x: DW / 2, y: 568, font: 'italic 400 32px "Cormorant Garamond"', color: BONE, alpha: a1, spacing: 1, shadow: 12, shadowColor: INK_SH });
  drawText(og, 'TOMORROW  ·  NIGHT SIX', { x: DW / 2, y: 618, font: '500 18px "Cinzel"', color: '#d8c79c', alpha: a2, spacing: 6, shadow: 10, shadowColor: INK_SH });
  return true;
}

// the illuminated panel: a gold double frame that draws itself, then the five verses, each Arabic line with its meaning
function versePanel(og, F, sh) {
  const C = F.CUES; const vs = C.lines.filter((l) => l.verse); const keys = ['96:1', '96:2', '96:3', '96:4', '96:5'];
  const lt = F.t - sh.t0; const fa = ease.inOutSine(clamp(lt / 1.6)) * (1 - smoothstep(sh.t1 - 0.9, sh.t1 - 0.05, F.t));
  const x0 = 210, x1 = 1070, y0 = 46, y1 = 676; const draw = ease.inOutSine(clamp(lt / 2.6));
  og.save(); og.globalAlpha = fa;
  const bg = og.createRadialGradient(640, 360, 60, 640, 360, 620); bg.addColorStop(0, 'rgba(18,14,30,0.55)'); bg.addColorStop(1, 'rgba(6,6,18,0.78)'); og.fillStyle = bg; og.fillRect(x0, y0, x1 - x0, y1 - y0);
  og.strokeStyle = '#c9a227'; og.lineWidth = 1.6; const per = 2 * (x1 - x0 + y1 - y0); og.setLineDash([per * draw, per]); og.strokeRect(x0, y0, x1 - x0, y1 - y0); og.lineWidth = 0.8; og.strokeRect(x0 + 9, y0 + 9, x1 - x0 - 18, y1 - y0 - 18); og.setLineDash([]);
  // corner rosettes: eight-point stars
  for (const [cx, cy] of [[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) { og.save(); og.translate(cx, cy); og.globalAlpha = fa * draw; og.fillStyle = '#c9a227'; for (let r = 0; r < 2; r++) { og.rotate(Math.PI / 4); og.fillRect(-8, -8, 16, 16); } og.fillStyle = '#1a1424'; og.beginPath(); og.arc(0, 0, 4, 0, 7); og.fill(); og.restore(); }
  og.restore();
  drawText(og, 'SURAH AL-ALAQ  ·  THE FIRST FIVE VERSES', { x: 640, y: 84, font: '500 17px "Cinzel"', color: '#d8c79c', alpha: fa * draw, spacing: 5, shadow: 8, shadowColor: INK_SH });
  vs.forEach((l, k) => {
    const a = ease.outCubic(clamp((F.t - l.start + 0.25) / 1.1)) * fa; if (a <= 0.003) return; const y = 146 + k * 106;
    arabic(og, C.arabic[keys[k]], 640, y, 40, { a, reveal: ease.inOutSine(clamp((F.t - l.start + 0.25) / 1.6)), glow: 0.5 });
    drawText(og, l.text, { x: 640, y: y + 50, font: 'italic 400 25px "Cormorant Garamond"', color: BONE, alpha: a * 0.95, spacing: 0.4, shadow: 10, shadowColor: INK_SH });
  });
  return true;
}

// the word, large: Arabic writing itself, then its meaning
function wordCard(og, F, sh) {
  const w = sh.word; const u = ease.inOutSine(clamp((F.t - sh.t0 - (w.at - sh.t0)) / (w.dur ?? 1.4)));
  const out = 1 - smoothstep(sh.t1 - 0.5, sh.t1, F.t);
  arabic(og, F.CUES.arabic[w.ar], 640, 320, 150, { a: out, reveal: u, glow: 0.3, color: '#7a4e12', halo: 1 });
  if (w.en) { const a = ease.outCubic(clamp((F.t - w.enAt + 0.1) / 1.0)) * out; drawText(og, w.en, { x: 640, y: 470, font: '500 40px "Cinzel"', color: '#3a2208', alpha: a, spacing: 18, shadow: 16, shadowColor: INK_SH }); }
  return true;
}

// "Read" stays with us while the meaning is told
function readCard(og, F, sh) {
  const lt = F.t - sh.t0; const a = ease.outCubic(clamp((lt - 0.6) / 1.6)) * (1 - smoothstep(sh.t1 - 1.0, sh.t1 - 0.1, F.t));
  arabic(og, F.CUES.arabic.iqra, 640, 150, 80, { a: a * 0.95, glow: 0.7 });
  drawText(og, 'READ', { x: 640, y: 236, font: '500 26px "Cinzel"', color: '#ead9b4', alpha: a * 0.9, spacing: 14, shadow: 12, shadowColor: INK_SH });
  return true;
}

export function drawOverlays(og, F, { CAPS, CUES }) {
  const sh = F.shot; let ov = false; const t = F.t;
  if (sh.card === 'title') ov = titleCard(og, F, sh) || ov;
  if (sh.card === 'verse') ov = versePanel(og, F, sh) || ov;
  if (sh.card === 'read') ov = readCard(og, F, sh) || ov;
  if (sh.word && sh.mode === 'word') ov = wordCard(og, F, sh) || ov;
  if (sh.mode === 'lantern' && sh.word && F.lanternPos) { const [x, y, s] = F.lanternPos; const a = ease.outCubic(clamp((F.t - sh.t0 - sh.word.at) / 1.4)) * (1 - smoothstep(sh.endAt - 0.6, sh.endAt + 0.4, F.t));
    if (a > 0.003) { ov = true; arabic(og, CUES.arabic.iqra, x, y + s * 1.05, 46, { a, reveal: ease.inOutSine(clamp((F.t - sh.t0 - sh.word.at) / 1.4)) }); drawText(og, 'READ', { x, y: y + s * 1.05 + 46, font: '500 18px "Cinzel"', color: '#ead9b4', alpha: a, spacing: 10, shadow: 10, shadowColor: INK_SH }); } }
  if (sh.card === 'end') ov = endCard(og, F, sh) || ov;
  for (const L of sh.labels || []) { const a = smoothstep(L.in, L.in + 0.5, t) * (1 - smoothstep(L.out - 0.5, L.out, t)); if (a > 0.003) { ov = true; label(og, L, a, F); } }
  for (const c of CAPS) { const a = smoothstep(c.in, c.in + 0.25, t) * (1 - smoothstep(c.out - 0.3, c.out, t)); if (a > 0.003) { ov = true; capDraw(og, c.text, a); } }
  return ov;
}
