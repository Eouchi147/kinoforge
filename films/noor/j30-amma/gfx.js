// Teaching graphics for NOOR Juz 30, drawn crisp on the overlay after the grade: refined, flat, gold hairlines, no emoji, no icons.
// Each item: { type, at, out, ... } in film seconds. Arabic only from cues.arabic (the King Fahd Complex Uthmani text), set in Amiri Quran.
import { drawText, ease, clamp, lerp, smoothstep } from '/harness/kit/film.js';
import { drawArabic } from './lib.js';

const GOLD = '#e3c26a', GOLD2 = '#c9a227', CREAM = '#efe6d3', SHADOW = 'rgba(3,3,12,0.92)';
const fadeA = (t, at, out, fi = 0.6, fo = 0.6) => smoothstep(at, at + fi, t) * (1 - smoothstep(out - fo, out, t));

export function drawGfx(og, F, items) {
  const t = F.t; const A = F.CUES.arabic; let any = false;
  for (const it of items) {
    const out = it.out ?? F.shot.t1 + 99; if (t < it.at - 0.01) continue; const a = fadeA(t, it.at, out, it.fi ?? 0.6, 0.5); if (a <= 0.003 && t > it.at + 1) continue; any = true;
    switch (it.type) {
      case 'label': {
        const y = it.y ?? 96; const s = it.small ? 0.8 : 1;
        drawText(og, it.text, { x: 640, y, font: `500 ${Math.round(26 * s)}px "Cinzel"`, color: '#ead9b4', alpha: a, spacing: 7 * s, shadow: 12, shadowColor: SHADOW });
        if (it.sub) drawText(og, it.sub, { x: 640, y: y + 34 * s, font: `italic 400 ${Math.round(24 * s)}px "Cormorant Garamond"`, color: '#d8cdb8', alpha: a * 0.92 * smoothstep(it.at + 0.3, it.at + 1.0, t), spacing: 1, shadow: 10, shadowColor: SHADOW });
        break; }
      case 'arabic': {
        const r = ease.inOutSine(clamp((t - it.at) / (it.dur ?? 1.6)));
        drawArabic(og, A[it.key], it.x ?? 640, it.y ?? 300, it.size ?? 64, { alpha: a, reveal: r, glow: it.glow ?? 0, shadow: 14 });
        if (it.meaning) { const ma = a * smoothstep(it.meaningAt ?? it.at + 1, (it.meaningAt ?? it.at + 1) + 0.8, t);
          drawText(og, it.meaning, { x: it.x ?? 640, y: (it.y ?? 300) + (it.size ?? 64) * 0.95 + 18, font: 'italic 400 32px "Cormorant Garamond"', color: CREAM, alpha: ma, spacing: 0.4, shadow: 12, shadowColor: SHADOW, maxWidth: 900 });
          if (it.ref) drawText(og, it.ref, { x: it.x ?? 640, y: (it.y ?? 300) + (it.size ?? 64) * 0.95 + 62, font: '500 15px "Cinzel"', color: GOLD2, alpha: ma * 0.9, spacing: 5, shadow: 8, shadowColor: SHADOW }); }
        break; }
      case 'cartouche': { // a gilded band with the surah's name in Arabic, a small caps line above, the English name below
        const y = it.y ?? 330; const w = 420 * ease.outCubic(clamp((t - it.at) / 0.9)), h = 96;
        og.save(); og.globalAlpha = a; og.strokeStyle = GOLD; og.lineWidth = 1.4; og.shadowColor = SHADOW; og.shadowBlur = 8;
        const x0 = 640 - w / 2, x1 = 640 + w / 2; og.beginPath(); og.moveTo(x0 + 24, y - h / 2); og.lineTo(x1 - 24, y - h / 2); og.quadraticCurveTo(x1 + 8, y, x1 - 24, y + h / 2); og.lineTo(x0 + 24, y + h / 2); og.quadraticCurveTo(x0 - 8, y, x0 + 24, y - h / 2); og.stroke();
        og.lineWidth = 0.8; og.globalAlpha = a * 0.7; og.beginPath(); og.moveTo(x0 + 34, y - h / 2 + 7); og.lineTo(x1 - 34, y - h / 2 + 7); og.moveTo(x0 + 34, y + h / 2 - 7); og.lineTo(x1 - 34, y + h / 2 - 7); og.stroke();
        for (const sx of [-1, 1]) { const cx = 640 + sx * (w / 2 + 26); og.globalAlpha = a; og.beginPath(); for (let k = 0; k < 8; k++) { const ang = k * Math.PI / 4; og.moveTo(cx, y); og.lineTo(cx + Math.cos(ang) * 9, y + Math.sin(ang) * 9); } og.stroke(); og.beginPath(); og.arc(cx, y, 4, 0, 7); og.fillStyle = GOLD; og.fill(); }
        og.restore();
        drawArabic(og, A[it.key], 640, y + 4, 58, { alpha: a * smoothstep(it.at + 0.4, it.at + 1.2, t), glow: 0.3 });
        drawText(og, it.num, { x: 640, y: y - h / 2 - 28, font: '500 17px "Cinzel"', color: GOLD2, alpha: a, spacing: 6, shadow: 8, shadowColor: SHADOW });
        drawText(og, it.name, { x: 640, y: y + h / 2 + 34, font: '500 26px "Cinzel"', color: '#ead9b4', alpha: a * smoothstep(it.at + 0.5, it.at + 1.3, t), spacing: 6, shadow: 10, shadowColor: SHADOW });
        break; }
      case 'pair': { // two surah names side by side
        const y = it.y ?? 140; for (const [s, x] of [[it.a, 420], [it.b, 860]]) { if (t < s.at) continue; const b = a * smoothstep(s.at, s.at + 0.8, t);
          drawArabic(og, A[s.key], x, y, 56, { alpha: b, reveal: ease.inOutSine(clamp((t - s.at) / 1.0)), glow: 0.3 });
          drawText(og, s.name, { x, y: y + 58, font: '500 20px "Cinzel"', color: '#ead9b4', alpha: b, spacing: 5, shadow: 10, shadowColor: SHADOW }); }
        break; }
      case 'arches': { // a row of thirty small arches: the thirty parts; each fills with gold when its lantern lights
        const n = it.n || 30, y = it.y ?? 92, gap = 30, w = 22, x0 = 640 - (n - 1) * gap / 2; const draw = ease.outCubic(clamp((t - it.at) / 2.2));
        og.save(); og.shadowColor = SHADOW; og.shadowBlur = 6;
        for (let i = 0; i < n; i++) { if (i / n > draw) break; const x = x0 + i * gap; const lt = it.lit ? it.lit[i] : null; const on = lt != null ? smoothstep(lt, lt + 0.4, t) : 0;
          const p = new Path2D(); p.moveTo(x - w / 2, y + 16); p.lineTo(x - w / 2, y - 2); p.quadraticCurveTo(x - w / 2, y - 14, x, y - 20); p.quadraticCurveTo(x + w / 2, y - 14, x + w / 2, y - 2); p.lineTo(x + w / 2, y + 16); p.closePath();
          og.globalAlpha = a * (0.55 + 0.45 * on); if (on > 0) { og.fillStyle = `rgba(242,196,96,${0.85 * on})`; og.fill(p); } og.strokeStyle = i === n - 1 ? '#ffe39a' : GOLD; og.lineWidth = i === n - 1 ? 1.6 : 1.1; og.stroke(p); }
        og.restore();
        // numbers under the first and the last arch
        drawText(og, '1', { x: x0, y: y + 34, font: '500 14px "Cinzel"', color: GOLD2, alpha: a * draw, shadow: 6, shadowColor: SHADOW });
        drawText(og, String(n), { x: x0 + (n - 1) * gap, y: y + 34, font: '500 14px "Cinzel"', color: GOLD2, alpha: a * smoothstep(0.95, 1, draw), shadow: 6, shadowColor: SHADOW });
        break; }
      case 'count': {
        const u = ease.outCubic(clamp((t - it.at) / Math.max(0.3, it.settle - it.at))); let v = Math.round(lerp(it.from || 0, it.to, u)); let s = it.commas ? v.toLocaleString('en-US') : String(v);
        const thenA = it.then ? smoothstep(it.then.at, it.then.at + 0.6, t) : 0;
        drawText(og, s, { x: it.x, y: it.y - 10 * thenA, font: '500 92px "Cinzel"', color: GOLD, alpha: a, spacing: 4, shadow: 18, shadowColor: SHADOW });
        drawText(og, it.label, { x: it.x, y: it.y + 66 - 10 * thenA, font: '500 22px "Cinzel"', color: '#ead9b4', alpha: a * smoothstep(it.at + 0.2, it.at + 0.8, t), spacing: 9, shadow: 10, shadowColor: SHADOW });
        if (it.then) drawText(og, it.then.text, { x: it.x, y: it.y + 116, font: '500 30px "Cinzel"', color: '#ffe39a', alpha: a * thenA, spacing: 5, shadow: 14, shadowColor: SHADOW });
        break; }
      case 'grid37': { // thirty-seven rosettes in rows, filling in order as the number counts
        const n = 37, cols = 13, gx = 52, gy = 56, y0 = 300; const u = clamp((t - it.at) / Math.max(0.3, it.settle - it.at)); const shown = u * n;
        og.save(); og.shadowColor = SHADOW; og.shadowBlur = 6;
        for (let i = 0; i < n; i++) { const row = Math.floor(i / cols), col = i % cols; const inRow = Math.min(cols, n - row * cols); const x = 640 + (col - (inRow - 1) / 2) * gx, y = y0 + row * gy; const on = clamp(shown - i);
          if (on <= 0) continue; og.globalAlpha = a * on; og.strokeStyle = GOLD; og.lineWidth = 1; og.beginPath(); og.arc(x, y, 15, 0, 7); og.stroke();
          og.beginPath(); for (let k = 0; k < 8; k++) { const ang = k * Math.PI / 4 + Math.PI / 8; og.moveTo(x, y); og.lineTo(x + Math.cos(ang) * 10, y + Math.sin(ang) * 10); } og.stroke(); og.fillStyle = GOLD; og.beginPath(); og.arc(x, y, 3, 0, 7); og.fill(); }
        og.restore(); break; }
      case 'bracket': { // the end and the beginning, side by side
        const y = it.y ?? 470; const d = ease.outCubic(clamp((t - it.at) / 1.2)); og.save(); og.globalAlpha = a; og.strokeStyle = GOLD; og.lineWidth = 1.2; og.shadowColor = SHADOW; og.shadowBlur = 6;
        og.beginPath(); og.moveTo(640, y - 10); og.lineTo(640, y + 26); og.moveTo(640 - 260 * d, y + 8); og.lineTo(640 - 30, y + 8); og.moveTo(640 + 30, y + 8); og.lineTo(640 + 260 * d, y + 8); og.stroke(); og.restore();
        drawText(og, it.left, { x: 640 - 150, y: y - 16, font: '500 18px "Cinzel"', color: '#ead9b4', alpha: a * smoothstep(it.at + 0.3, it.at + 1.0, t), spacing: 5, shadow: 10, shadowColor: SHADOW });
        drawText(og, it.right, { x: 640 + 150, y: y - 16, font: '500 18px "Cinzel"', color: '#ffe39a', alpha: a * smoothstep(it.at + 0.9, it.at + 1.6, t), spacing: 5, shadow: 10, shadowColor: SHADOW });
        break; }
      case 'ikhlas': { // four verses, one under the other, each with its meaning
        const n = it.lines.length; const y0 = 140, step = 112;
        it.lines.forEach((L, i) => { if (t < L.at) return; const b = a * smoothstep(L.at, L.at + 0.5, t); const y = y0 + i * step;
          drawArabic(og, A[L.key], 640, y, 50, { alpha: b, reveal: ease.inOutSine(clamp((t - L.at) / 1.1)), glow: 0.25 });
          drawText(og, L.meaning, { x: 640, y: y + 44, font: 'italic 400 25px "Cormorant Garamond"', color: CREAM, alpha: b * smoothstep(L.at + 0.4, L.at + 1.0, t), spacing: 0.3, shadow: 10, shadowColor: SHADOW }); });
        break; }
      case 'third': { // a circle, one third filling with gold
        const u = ease.inOutSine(clamp((t - it.at) / Math.max(0.4, it.settle - it.at))); const { x, y, r } = it;
        og.save(); og.globalAlpha = a; og.shadowColor = SHADOW; og.shadowBlur = 8; og.strokeStyle = GOLD; og.lineWidth = 1.4; og.beginPath(); og.arc(x, y, r, 0, Math.PI * 2); og.stroke();
        for (let k = 0; k < 3; k++) { const ang = -Math.PI / 2 + k * Math.PI * 2 / 3; og.beginPath(); og.moveTo(x, y); og.lineTo(x + Math.cos(ang) * r, y + Math.sin(ang) * r); og.lineWidth = 0.9; og.stroke(); }
        if (u > 0) { og.shadowBlur = 0; og.fillStyle = 'rgba(236,190,90,0.78)'; og.beginPath(); og.moveTo(x, y); og.arc(x, y, r - 3, -Math.PI / 2, -Math.PI / 2 + u * Math.PI * 2 / 3); og.closePath(); og.fill(); }
        og.restore();
        drawText(og, it.label, { x, y: y + r + 48, font: '500 22px "Cinzel"', color: '#ffe39a', alpha: a * smoothstep(it.settle - 0.3, it.settle + 0.4, t), spacing: 6, shadow: 12, shadowColor: SHADOW });
        break; }
    }
  }
  return any;
}
