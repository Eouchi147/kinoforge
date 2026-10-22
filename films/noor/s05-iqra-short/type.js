// Type for the 9:16 short. Every word stays inside the platform safe box (x 0.11 to 0.78, y 0.15 to 0.65 of the frame:
// x 79 to 562, y 192 to 832 in the 720x1280 frame), so the centre of the text column is x = 320, not the frame centre.
// Arabic is set only in Amiri Quran from cues.arabic; no em or en dashes, no "..." on screen.
import { drawText, ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { arabic } from '../n05-iqra/type.js';
const CX = 320, BONE = '#efe6d3', SH = 'rgba(3,3,12,0.94)', SAFE = [79, 192, 562, 832];
function wrap(g, text, maxW, font) { g.save(); g.font = font; const words = text.split(' '); const lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } if (cur) lines.push(cur); g.restore(); return lines; }
function cap(og, text, a) {
  const font = 'italic 500 34px "Cormorant Garamond"'; const lines = wrap(og, text, SAFE[2] - SAFE[0] - 10, font); const lh = 40; const y0 = 800 - (lines.length - 1) * lh;
  og.save(); const gr = og.createLinearGradient(0, y0 - 90, 0, 900); gr.addColorStop(0, 'rgba(4,4,14,0)'); gr.addColorStop(0.5, `rgba(4,4,14,${0.5 * a})`); gr.addColorStop(1, 'rgba(4,4,14,0)'); og.fillStyle = gr; og.fillRect(0, y0 - 90, 720, 990 - y0); og.restore();
  lines.forEach((l, i) => drawText(og, l, { x: CX, y: y0 + i * lh, font, color: BONE, alpha: a, spacing: 0.3, shadow: 12, shadowColor: SH }));
}
function hook(og, F, sh) {
  const [h0, h1] = sh.hook; const a = ease.outCubic(clamp((F.t - h0 - 0.1) / 0.5)) * (1 - smoothstep(h1 - 0.6, h1, F.t)); if (a <= 0.003) return false;
  drawText(og, 'THE FIRST WORD', { x: CX, y: 240, font: '500 40px "Cinzel"', color: '#ead9b4', alpha: a, spacing: 6, shadow: 14, shadowColor: SH });
  drawText(og, 'EVER REVEALED', { x: CX, y: 292, font: '500 40px "Cinzel"', color: '#ead9b4', alpha: a, spacing: 6, shadow: 14, shadowColor: SH });
  return true;
}
function word(og, F, sh) {
  const w = sh.word; const u = ease.inOutSine(clamp((F.t - w.at) / w.dur)); const out = 1 - smoothstep(sh.t1 - 0.5, sh.t1, F.t);
  arabic(og, F.CUES.arabic.iqra, CX, 470, 128, { a: out, reveal: u, bright: true });
  const a = ease.outCubic(clamp((F.t - w.enAt + 0.1) / 1.0)) * out; drawText(og, 'READ', { x: CX, y: 600, font: '500 40px "Cinzel"', color: '#2C2416', alpha: a, spacing: 14, shadow: 10, shadowColor: 'rgba(255,236,190,0.7)' });
  return true;
}
function verses(og, F, sh) {
  const C = F.CUES; const vs = C.lines.filter((l) => l.verse); const keys = ['96:1', '96:2', '96:3', '96:4', '96:5'];
  const lt = F.t - sh.t0; const fa = ease.inOutSine(clamp(lt / 1.2)) * (1 - smoothstep(sh.t1 - 0.6, sh.t1, F.t)); const draw = ease.inOutSine(clamp(lt / 2.2));
  const x0 = 72, x1 = 568, y0 = 186, y1 = 840;
  og.save(); og.globalAlpha = fa; og.fillStyle = 'rgba(8,7,20,0.72)'; og.fillRect(x0, y0, x1 - x0, y1 - y0);
  og.strokeStyle = '#c9a227'; og.lineWidth = 1.6; const per = 2 * (x1 - x0 + y1 - y0); og.setLineDash([per * draw, per]); og.strokeRect(x0, y0, x1 - x0, y1 - y0); og.lineWidth = 0.8; og.strokeRect(x0 + 8, y0 + 8, x1 - x0 - 16, y1 - y0 - 16); og.setLineDash([]); og.restore();
  drawText(og, 'SURAH AL-ALAQ  ·  96:1 TO 5', { x: CX, y: 222, font: '500 16px "Cinzel"', color: '#d8c79c', alpha: fa * draw, spacing: 4, shadow: 8, shadowColor: SH });
  vs.forEach((l, k) => { const a = ease.outCubic(clamp((F.t - l.start + 0.25) / 1.0)) * fa; if (a <= 0.003) return; const y = 284 + k * 112;
    arabic(og, C.arabic[keys[k]], CX, y, 34, { a, reveal: ease.inOutSine(clamp((F.t - l.start + 0.25) / 1.4)), glow: 0.5 });
    const ls = wrap(og, l.text, 440, 'italic 400 23px "Cormorant Garamond"'); ls.forEach((s, i) => drawText(og, s, { x: CX, y: y + 44 + i * 26, font: 'italic 400 23px "Cormorant Garamond"', color: BONE, alpha: a * 0.95, shadow: 8, shadowColor: SH })); });
  return true;
}
function read(og, F, sh) {
  const a = ease.outCubic(clamp((F.t - sh.t0 - 0.6) / 1.4)) * (1 - smoothstep(sh.endAt - 0.6, sh.endAt, F.t));
  arabic(og, F.CUES.arabic.iqra, CX, 300, 96, { a: a * 0.95, glow: 0.7 }); drawText(og, 'READ', { x: CX, y: 392, font: '500 28px "Cinzel"', color: '#ead9b4', alpha: a * 0.9, spacing: 12, shadow: 12, shadowColor: SH });
  const e = ease.outCubic(clamp((F.t - sh.endAt) / 1.0));
  if (e > 0.003) { drawText(og, 'NOOR', { x: CX, y: 520, font: '500 48px "Cinzel"', color: '#ead9b4', alpha: e, spacing: 14, shadow: 14, shadowColor: SH }); drawText(og, 'Thirty Nights of Light', { x: CX, y: 572, font: 'italic 400 30px "Cormorant Garamond"', color: BONE, alpha: e, shadow: 10, shadowColor: SH }); drawText(og, 'THE FULL FILM ON YOUTUBE', { x: CX, y: 622, font: '500 15px "Cinzel"', color: '#d8c79c', alpha: e, spacing: 4, shadow: 8, shadowColor: SH }); }
  return true;
}
export function drawOverlays(og, F, { CAPS }) {
  const sh = F.shot; let ov = false;
  if (sh.hook) ov = hook(og, F, sh) || ov;
  if (sh.word) ov = word(og, F, sh) || ov;
  if (sh.card === 'verse') ov = verses(og, F, sh) || ov;
  if (sh.card === 'read') ov = read(og, F, sh) || ov;
  const endAt = sh.endAt ?? 1e9;
  for (const c of CAPS) { if (F.t > endAt) break; const a = smoothstep(c.in, c.in + 0.2, F.t) * (1 - smoothstep(c.out - 0.25, c.out, F.t)); if (a > 0.003) { ov = true; cap(og, c.text, a); } }
  return ov;
}
