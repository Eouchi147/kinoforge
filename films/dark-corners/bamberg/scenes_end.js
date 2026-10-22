// Beats 20 to 25: the letter (written in a failing hand, folded, hidden), "I am innocent", "Good night", the end, the archive drawer, the end card. 123.8 to 163.3 s.
import { clamp, ease, lerp, rgba, keys, mk, withScale, smoothstep, noise1, rng, measure, FONTS } from './lib.js';

export function buildEnd(E) {
  const { C, W, H, U, AX, MEAS, PAD } = E, tw = E.tw, cream = C.cream, ink = C.ink, red = C.red;
  const S = [];
  const L = (s, extra = {}) => E.line({ color: cream, ...s, ...extra });
  const stack = (specs, top, gap, extra = {}) => { for (const s of E.stack(specs, top, gap).lines) L(s, extra); };
  const DURATION = E.duration;

  // ================================================================ e1: the letter, written in a failing hand
  const em1 = E.emFit('C', 'to his daughter,', 0.80), emV = E.emFit('C', 'Veronica,', 0.82);
  const trem1 = (tk) => 0.30 + 1.5 * smoothstep(128.7, 131.4, tk);
  const E1 = [
    { txt: 'He wrote all of this', em: em1, base: 0.19, times: ['He', 'wrote', 'all', 'of', 'this'].map((w) => tw('e1', w)), seed: 11 },
    { txt: 'to his daughter,', em: em1, base: 0.255, times: [tw('e1', 'to'), tw('e1', 'his'), tw('e1', 'daughter,')], seed: 12 },
    { txt: 'Veronica,', em: emV, base: 0.355, times: [tw('e1', 'Veronica,')], seed: 13, maxWord: 0.9 },
    { txt: 'over several days,', em: em1, base: 0.43, times: [tw('e1', 'over'), tw('e1', 'several'), tw('e1', 'days,')], seed: 14 },
    { txt: 'with hands that', em: em1, base: 0.495, times: [tw('e1', 'with'), tw('e1', 'hands'), tw('e1', 'that')], seed: 15, sag: (u) => 0.9 * u },
    { txt: 'barely worked.', em: em1, base: 0.560, times: [tw('e1', 'barely'), tw('e1', 'worked.')], seed: 16, sag: (u) => 3 + 6 * u, lastDur: 0.8, maxWord: 0.8 },
  ];
  function drawLetterPage(E, t) {
    E1.forEach((l) => E.hand({ ...l, color: ink, trem: trem1 }, E.f, t));
    // the pen gives out: a blot spreads where "worked." ends
    const tb = tw('e1', 'worked.') + 0.55;
    if (t >= tb) { const p = ease.outCubic(clamp((t - tb) / 0.5)), x = AX + MEAS * 0.52 + 0.10 * W, y = 0.560 * H + 0.006 * H, I = E.ink; I.save(); I.fillStyle = rgba(ink, 0.9); I.beginPath(); I.ellipse(x, y, 5 * U * p, 4 * U * p, 0.3, 0, 6.2832); I.fill(); I.fillRect(x - 1.1 * U, y, 2.2 * U, 18 * U * p); I.restore(); }
  }
  S.push({
    name: 'e1 to Veronica, a failing hand', t0: 123.80, bg: 'cream',
    hits: [[123.80, 9, 6, 0], [tw('e1', 'Veronica,'), 3, 3, 0]],
    draw(E) { drawLetterPage(E, E.t); },
  });

  // ================================================================ e2: he asked her to hide the letter (fold in thirds, slip into a gap)
  let SHEET = null;
  const sheet = () => {
    if (SHEET) return SHEET;
    const c = mk(W, H), sg = c.getContext('2d'), si = E.INK.getContext('2d'); const save = { g: E.g, ink: E.ink, t: E.t, f: E.f };
    const tmp = mk(W, H), tg = tmp.getContext('2d'); tg.textRendering = 'geometricPrecision'; tg.fontKerning = 'normal';
    E.g = sg; E.ink = tg; E.t = 131.7; E.f = Math.round(131.7 * 24);
    sg.drawImage(E.PAPER.cream, -PAD, -PAD); drawLetterPage(E, 131.7);
    tg.globalCompositeOperation = 'destination-out'; tg.drawImage(E.INKNOISE, 0, 0); tg.globalCompositeOperation = 'source-over'; sg.drawImage(tmp, 0, 0);
    E.g = save.g; E.ink = save.ink; E.t = save.t; E.f = save.f; SHEET = c; return c;
  };
  const SLOT = 0.665 * H;
  function drawFold(E, t) {
    const g = E.g, SH = sheet(), h3 = H / 3;
    const tShr = [131.90, 132.50], tA = [132.55, 133.00], tC = [133.05, 133.50], tS = [133.62, 134.42];
    const pS = ease.inOutCubic(clamp((t - tShr[0]) / (tShr[1] - tShr[0]))), thA = Math.PI * ease.inOutQuad(clamp((t - tA[0]) / (tA[1] - tA[0]))), thC = Math.PI * ease.inOutQuad(clamp((t - tC[0]) / (tC[1] - tC[0])));
    const pSlide = ease.inCubic(clamp((t - tS[0]) / (tS[1] - tS[0]))), s = lerp(1, 0.62, pS), cy = lerp(0.5 * H, 0.62 * H, pS) + pSlide * 0.55 * H;
    g.save(); g.beginPath(); g.rect(0, 0, W, SLOT); g.clip();
    g.translate(W / 2, cy); g.scale(s, s); g.translate(-W / 2, -H / 2);
    g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 30 * U * pS; g.shadowOffsetY = 10 * U * pS; g.fillStyle = '#d9cdb0';
    g.fillRect(0, h3, W, h3); g.shadowColor = 'rgba(0,0,0,0)';
    g.drawImage(SH, 0, h3, W, h3, 0, h3, W, h3);                                         // middle panel, static
    const back = 'rgba(190,168,122,0.55)';
    // top panel folds down over the middle
    g.save(); g.translate(0, h3); const cA = Math.cos(thA); g.scale(1, cA === 0 ? 1e-4 : cA);
    g.drawImage(SH, 0, 0, W, h3, 0, -h3, W, h3); if (thA > Math.PI / 2) { g.drawImage(E.PAPER.cream, PAD, PAD + 0, W, h3, 0, -h3, W, h3); g.fillStyle = back; g.fillRect(0, -h3, W, h3); }
    g.fillStyle = `rgba(0,0,0,${0.30 * Math.sin(thA)})`; g.fillRect(0, -h3, W, h3); g.restore();
    // bottom panel folds up over it
    g.save(); g.translate(0, 2 * h3); const cC = Math.cos(thC); g.scale(1, cC === 0 ? 1e-4 : cC);
    g.drawImage(SH, 0, 2 * h3, W, h3, 0, 0, W, h3); if (thC > Math.PI / 2) { g.drawImage(E.PAPER.cream, PAD, PAD, W, h3, 0, 0, W, h3); g.fillStyle = back; g.fillRect(0, 0, W, h3); }
    g.fillStyle = `rgba(0,0,0,${0.30 * Math.sin(thC)})`; g.fillRect(0, 0, W, h3); g.restore();
    if (thC > 2.4) { g.fillStyle = 'rgba(80,56,30,0.30)'; g.fillRect(0, h3, W, 2 * U); g.fillRect(0, 2 * h3 - 2 * U, W, 2 * U); }   // the folded edges
    g.restore();
  }
  S.push({
    name: 'e2 fold and hide the letter', t0: 131.80, bg: 'none',
    hits: [[tw('e2', 'letter.') + 0.5, 8, 5, 0]],
    draw(E) {
      const t = E.t, g = E.g;
      if (t < 131.9) { g.drawImage(E.PAPER.cream, -PAD, -PAD); drawLetterPage(E, t); return; }
      g.drawImage(E.PAPER.dark, -PAD, -PAD);
      drawFold(E, t);
      // the gap: a hairline of light the letter slips behind
      const a = 0.55 * smoothstep(133.3, 133.8, t); const gr = g.createLinearGradient(0, SLOT - 18 * U, 0, SLOT + 18 * U); gr.addColorStop(0, 'rgba(239,230,210,0)'); gr.addColorStop(0.5, `rgba(239,230,210,${0.18 * a})`); gr.addColorStop(1, 'rgba(239,230,210,0)'); g.fillStyle = gr; g.fillRect(0, SLOT - 18 * U, W, 36 * U);
      g.fillStyle = `rgba(239,230,210,${a})`; g.fillRect(0.06 * W, SLOT - U, 0.88 * W, 2 * U);
      L({ txt: 'HE ASKED HER', font: 'B', fit: 1.0, maxCap: 0.04, ls: 0.14, base: 0.185, times: [tw('e2', 'he'), tw('e2', 'asked'), tw('e2', 'her')] });
      L({ txt: 'TO HIDE THE LETTER.', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, base: 0.245, times: [tw('e2', 'to'), tw('e2', 'hide'), tw('e2', 'the'), tw('e2', 'letter.')], curves: [null, E.HEAVY, null, E.PAYOFF] });
    },
  });
  E.slotLine = (a) => { const g = E.g; g.fillStyle = `rgba(239,230,210,${a})`; g.fillRect(0.06 * W, SLOT - U, 0.88 * W, 2 * U); };

  // ================================================================ e3: "He wrote: I am innocent." The one red mark.
  S.push({
    name: 'e3 I am innocent', t0: 134.47, bg: 'dark',
    hits: [[134.47, 6, 5, 0.04], [tw('e3', 'innocent.'), 3, 3, 0]],
    draw(E) {
      const t = E.t, g = E.g;
      E.slotLine(0.5 * (1 - clamp((t - 134.47) / 0.7)));
      L({ txt: 'HE WROTE:', font: 'B', cap: 0.04, ls: 0.2, base: 0.20, times: [tw('e3', 'he'), tw('e3', 'wrote:')] });
      const emA = E.emFit('C', 'innocent.', 0.98), emI = 0.092;
      // a faint red glow behind the mark as it dries
      const tg = tw('e3', 'innocent.') + 0.3;
      if (t > tg) { const k = smoothstep(tg, tg + 1.2, t), gr = g.createRadialGradient(W * 0.5, 0.42 * H, 10, W * 0.5, 0.42 * H, 0.45 * W); gr.addColorStop(0, `rgba(207,59,46,${0.10 * k})`); gr.addColorStop(1, 'rgba(207,59,46,0)'); g.fillStyle = gr; g.fillRect(0, 0.2 * H, W, 0.5 * H); }
      E.hand({ txt: 'I am', em: emI, base: 0.325, times: [tw('e3', 'I'), tw('e3', 'am')], color: red, trem: () => 0.55, seed: 21 });
      E.hand({ txt: 'innocent.', em: emA, base: 0.455, times: [tw('e3', 'innocent.')], color: red, trem: () => 0.5, seed: 22, lastDur: 0.75, maxWord: 0.75 });
    },
  });

  // ================================================================ e4: "Good night. Your father will never see you again."
  S.push({
    name: 'e4 good night', t0: 138.20, bg: 'dark',
    hits: [[138.252, 4, 4, 0.03], [tw('e4', 'night.'), 4, 4, 0.03]],
    draw(E) {
      const t = E.t, fade = 1 - 0.92 * smoothstep(143.6, 144.85, t);
      E.hand({ txt: 'I am innocent.', em: E.emFit('C', 'I am innocent.', 0.62), base: 0.195, times: [0, 0, 0], color: red, trem: () => 0.45, seed: 23, alpha: 0.5 * fade, glyph: 0.0001, dry: 0.01 });
      L({ txt: 'AND HE ENDED WITH:', font: 'B', fit: 1.0, maxCap: 0.035, ls: 0.12, base: 0.285, times: [tw('e4', 'and'), tw('e4', 'he'), tw('e4', 'ended'), tw('e4', 'with:')], alpha: fade });
      E.hand({ txt: 'Good night.', em: E.emFit('C', 'Good night.', 0.98), base: 0.415, times: [tw('e4', 'Good'), tw('e4', 'night.')], color: cream, trem: () => 0.5, seed: 31, alpha: fade });
      const em = 0.048;
      E.hand({ txt: 'Your father', em, base: 0.50, times: [tw('e4', 'Your'), tw('e4', 'father')], color: cream, trem: () => 0.7, seed: 32, alpha: 0.92 * fade });
      E.hand({ txt: 'will never see', em, base: 0.56, times: [tw('e4', 'will'), tw('e4', 'never'), tw('e4', 'see')], color: cream, trem: () => 0.8, seed: 33, alpha: 0.8 * fade });
      E.hand({ txt: 'you again.', em, base: 0.62, times: [tw('e4', 'you'), tw('e4', 'again.')], color: cream, trem: () => 1.0, seed: 34, alpha: 0.65 * fade, lastDur: 0.9, maxWord: 0.9 });
    },
  });

  // ================================================================ f1: That August, Johannes Junius was executed.
  S.push({
    name: 'f1 August, executed', t0: 144.85, bg: 'dark',
    hits: [[144.985, 5, 4, 0.04], [tw('f1', 'August,'), 6, 5, 0.05], [tw('f1', 'executed.'), 9, 7, 0.08]],
    draw(E) {
      const t = E.t;
      L({ txt: 'THAT', font: 'B', cap: 0.035, ls: 0.3, base: 0.185, times: tw('f1', 'that') });
      const A = E.line({ txt: 'AUGUST', font: 'B', fit: 1.0, maxCap: 0.135, ls: 0.03, base: 0.335, times: tw('f1', 'August,'), mode: 'stamp', smear: true, color: cream });
      L({ txt: '1628', font: 'C', em: 0.036, base: 0.385, times: tw('f1', 'August,') + 0.5, mode: 'pop', alpha: 0.85 });
      const nm = L({ txt: 'JOHANNES JUNIUS', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, base: 0.46, times: [tw('f1', 'Johannes'), tw('f1', 'Junius')], curves: [null, E.HEAVY] });
      L({ txt: 'WAS EXECUTED.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.04, base: 0.56, times: [tw('f1', 'was'), tw('f1', 'executed.')], curves: [null, E.PAYOFF] });
      const ts = tw('f1', 'executed.') + 0.3;
      if (t >= ts) { const p = ease.outCubic(clamp((t - ts) / 0.35)), y = nm.base - nm.cap * 0.5; E.ink.fillStyle = rgba(cream, 0.9); E.ink.fillRect(nm.inkL - 6 * U, y, (nm.inkW + 12 * U) * p, Math.max(2, 0.0026 * H)); }
    },
  });

  // ================================================================ the strip (the folded letter) and the archive drawer
  function drawStrip(g, cx, cy, w, rot, alpha = 1) {
    const SH = sheet(), h = w * (H / 3) / W;
    g.save(); g.translate(cx, cy); g.rotate(rot); g.globalAlpha = alpha; g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = 20 * U; g.shadowOffsetY = 7 * U; g.fillStyle = '#e6dcc2'; g.fillRect(-w / 2, -h / 2, w, h);
    g.shadowColor = 'rgba(0,0,0,0)'; g.drawImage(SH, 0, H / 3, W, H / 3, -w / 2, -h / 2, w, h);
    g.fillStyle = 'rgba(70,48,24,0.22)'; g.fillRect(-w / 2, -h / 2, w, 2 * U); g.fillRect(-w / 2, h / 2 - 2 * U, w, 2 * U); g.fillRect(-w / 2, -h / 2, 2 * U, h); g.fillRect(w / 2 - 2 * U, -h / 2, 2 * U, h);
    g.restore(); return h;
  }
  const DR = { x0: 0.07 * W, x1: 0.93 * W, y0: 0.44 * H, y1: 0.82 * H };
  const FO = { x0: 0.13 * W, x1: 0.87 * W, y0: 0.485 * H, y1: 0.775 * H };
  const motes = (() => { const r = rng(606), a = []; for (let k = 0; k < 46; k++) a.push({ x: r(), y: r(), s: 0.004 + 0.01 * r(), z: 0.6 + 1.8 * r(), p: r() * 6.28 }); return a; })();
  // st: { open: 0..1 (1 = cover lies open on the left), strip: {y, a} | null, glow: 0..1, push: scale add, dust: 0..1 }
  function drawDrawer(E, t, st) {
    const g = E.g, cx = W / 2, cyy = 0.63 * H, push = st.push || 0;
    g.save(); g.translate(cx, cyy); g.scale(1 + push, 1 + push); g.translate(-cx, -cyy);
    const rim = 15 * U;
    // rim + cavity
    let gr = g.createLinearGradient(0, DR.y0 - rim, 0, DR.y1 + rim); gr.addColorStop(0, '#34373a'); gr.addColorStop(1, '#17181a'); g.fillStyle = gr; g.fillRect(DR.x0 - rim, DR.y0 - rim, DR.x1 - DR.x0 + 2 * rim, DR.y1 - DR.y0 + 2 * rim);
    g.fillStyle = 'rgba(255,255,255,0.10)'; g.fillRect(DR.x0 - rim, DR.y0 - rim, DR.x1 - DR.x0 + 2 * rim, 2 * U);
    g.fillStyle = '#080707'; g.fillRect(DR.x0, DR.y0, DR.x1 - DR.x0, DR.y1 - DR.y0);
    gr = g.createLinearGradient(0, DR.y0, 0, DR.y0 + 40 * U); gr.addColorStop(0, 'rgba(0,0,0,0.8)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(DR.x0, DR.y0, DR.x1 - DR.x0, 40 * U);
    // front lip: label plate and handle
    const ly0 = DR.y1 + rim, ly1 = ly0 + 0.10 * H;
    gr = g.createLinearGradient(0, ly0, 0, ly1); gr.addColorStop(0, '#2b2d30'); gr.addColorStop(1, '#141516'); g.fillStyle = gr; g.fillRect(DR.x0 - rim, ly0, DR.x1 - DR.x0 + 2 * rim, ly1 - ly0);
    g.fillStyle = 'rgba(255,255,255,0.08)'; g.fillRect(DR.x0 - rim, ly0, DR.x1 - DR.x0 + 2 * rim, 2 * U);
    const pw = 0.30 * W, ph = 0.034 * H; g.fillStyle = '#c9ced0'; g.fillRect(cx - pw / 2, ly0 + 0.022 * H, pw, ph);
    g.fillStyle = '#14171a'; g.font = `400 ${0.0145 * H}px "Special Elite"`; g.letterSpacing = (0.12 * 0.0145 * H) + 'px'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('JUNIUS, 1628', cx, ly0 + 0.022 * H + ph / 2 + 1 * U); g.textAlign = 'left'; g.letterSpacing = '0px';
    g.fillStyle = '#0c0d0e'; g.fillRect(cx - 0.10 * W, ly0 + 0.066 * H, 0.20 * W, 0.012 * H); g.fillStyle = 'rgba(255,255,255,0.14)'; g.fillRect(cx - 0.10 * W, ly0 + 0.066 * H, 0.20 * W, 1.5 * U);
    // folder: body, tab, inner face
    g.save(); g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 16 * U; g.shadowOffsetY = 5 * U; g.fillStyle = '#b9bfc1'; g.fillRect(FO.x0, FO.y0, FO.x1 - FO.x0, FO.y1 - FO.y0); g.restore();
    g.fillStyle = '#bcc2c4'; g.fillRect(FO.x0 - 1 * U, FO.y0 - 0.014 * H, 0.22 * W, 0.016 * H);
    if (st.strip) drawStrip(g, (FO.x0 + FO.x1) / 2, st.strip.y, 0.64 * W, -0.012, st.strip.a ?? 1);
    // warm light on the letter
    if (st.glow > 0) { const gg = g.createRadialGradient(cx, (FO.y0 + FO.y1) / 2, 10, cx, (FO.y0 + FO.y1) / 2, 0.55 * W); gg.addColorStop(0, `rgba(255,214,150,${0.28 * st.glow})`); gg.addColorStop(1, 'rgba(255,214,150,0)'); g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = gg; g.fillRect(DR.x0, DR.y0 - 60 * U, DR.x1 - DR.x0, DR.y1 - DR.y0 + 120 * U); g.restore(); }
    // the cover: hinge on the left edge; angle 0 = closed, pi = lying open to the left
    const th = Math.PI * (1 - clamp(st.open)), c = Math.cos(th), cw = FO.x1 - FO.x0;
    if (st.open < 0.999) {
      g.save(); g.translate(FO.x0, 0); g.scale(Math.abs(c) < 1e-3 ? 1e-3 : c, 1);
      g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 14 * U; g.fillStyle = c >= 0 ? '#cdd2d3' : '#a9b0b2'; g.fillRect(0, FO.y0, cw, FO.y1 - FO.y0); g.shadowColor = 'rgba(0,0,0,0)';
      g.fillStyle = `rgba(0,0,0,${0.35 * (1 - Math.abs(c))})`; g.fillRect(0, FO.y0, cw, FO.y1 - FO.y0);
      g.fillStyle = 'rgba(20,23,26,0.35)'; g.fillRect(0.04 * cw, FO.y0 + 0.02 * H, 0.35 * cw, 2 * U); g.fillRect(0.04 * cw, FO.y0 + 0.032 * H, 0.22 * cw, 2 * U);
      g.restore();
    }
    // dust in the lamp light
    if (st.dust > 0) { g.save(); for (const m of motes) { const yy = DR.y0 + ((m.y + t * m.s) % 1) * (DR.y1 - DR.y0), xx = DR.x0 + m.x * (DR.x1 - DR.x0) + 14 * U * Math.sin(t * 0.5 + m.p); g.fillStyle = `rgba(255,236,200,${0.30 * st.dust * (0.5 + 0.5 * Math.sin(t * 1.3 + m.p))})`; g.beginPath(); g.arc(xx, yy, m.z * U, 0, 6.2832); g.fill(); } g.restore(); }
    g.restore();
  }

  // ---- f2a: his letter probably never reached his daughter
  S.push({
    name: 'f2a letter never reached', t0: 148.95, bg: 'dark',
    hits: [[149.03, 5, 4, 0.03], [tw('f2', 'never'), 7, 6, 0.05]],
    draw(E) {
      const t = E.t, g = E.g, tin = 148.97, p = ease.outBack(clamp((t - tin) / 0.35));
      drawStrip(g, W * 0.5, lerp(1.0 * H, 0.745 * H, p), 0.56 * W, -0.035, clamp((t - tin) / 0.1));
      stack([
        { txt: 'HIS LETTER', font: 'B', cap: 0.04, ls: 0.2, times: [tw('f2', 'His'), tw('f2', 'letter')] },
        { txt: 'PROBABLY', font: 'B', fit: 0.6, maxCap: 0.04, ls: 0.12, times: tw('f2', 'probably') },
        { txt: 'NEVER', font: 'B', fit: 0.8, maxCap: 0.13, ls: 0.03, times: tw('f2', 'never'), curve: E.PAYOFF },
        { txt: 'REACHED', font: 'B', fit: 0.8, maxCap: 0.07, ls: 0.04, times: tw('f2', 'reached'), curve: E.HEAVY },
        { txt: 'HIS DAUGHTER.', font: 'B', fit: 1.0, maxCap: 0.045, ls: 0.06, times: [tw('f2', 'his', 1), tw('f2', 'daughter.')] },
      ], 0.165, 0.02);
    },
  });

  // ---- f2b: the court kept it in his file (the strip drops into the folder, the cover closes)
  const FILE_T = [152.95, 153.65], COVER_T = [153.95, 154.48];
  S.push({
    name: 'f2b kept in his file', t0: 152.20, bg: 'dark',
    hits: [[154.52, 10, 7, 0.06]],
    draw(E) {
      const t = E.t, pD = ease.inOutCubic(clamp((t - FILE_T[0]) / (FILE_T[1] - FILE_T[0]))), cyS = (FO.y0 + FO.y1) / 2;
      const open = 1 - ease.inQuad(clamp((t - COVER_T[0]) / (COVER_T[1] - COVER_T[0])));
      drawDrawer(E, t, { open, strip: { y: lerp(0.745 * H, cyS, pD), a: 1 }, glow: 0.35 * (1 - (1 - open)), dust: 0 });
      stack([
        { txt: 'THE COURT', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.1, times: [tw('f2', 'The'), tw('f2', 'court')] },
        { txt: 'KEPT IT', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.06, times: [tw('f2', 'kept'), tw('f2', 'it')] },
        { txt: 'IN HIS FILE.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.04, times: [tw('f2', 'in'), tw('f2', 'his', 2), tw('f2', 'file.')], curves: [null, null, E.PAYOFF] },
      ], 0.165, 0.016);
    },
  });

  // ---- f3a/f3b: almost four hundred years later, we can still read it (the drawer opens on the letter)
  S.push({
    name: 'f3a four hundred years', t0: 154.72, bg: 'dark',
    draw(E) {
      const t = E.t, k = clamp((t - 154.72) / 4.1);
      drawDrawer(E, t, { open: 0, strip: null, glow: 0, dust: 1, push: 0.05 * k });
      stack([
        { txt: 'AND THAT IS WHY,', font: 'B', fit: 1.0, maxCap: 0.034, ls: 0.14, times: [tw('f3', 'And'), tw('f3', 'that'), tw('f3', 'is'), tw('f3', 'why,')] },
        { txt: 'ALMOST FOUR HUNDRED', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.04, times: [tw('f3', 'almost'), tw('f3', 'four'), tw('f3', 'hundred')], curves: [null, E.HEAVY, E.HEAVY] },
        { txt: 'YEARS LATER,', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.04, times: [tw('f3', 'years'), tw('f3', 'later,')], curves: [null, E.PAYOFF] },
      ], 0.165, 0.016);
    },
  });
  S.push({
    name: 'f3b we can still read it', t0: 158.80, bg: 'dark',
    hits: [[tw('f3', 'still') - 0.16, 8, 6, 0.05]],
    draw(E) {
      const t = E.t, tO = [158.86, 159.34], open = ease.outCubic(clamp((t - tO[0]) / (tO[1] - tO[0]))), glow = smoothstep(158.95, 159.8, t) * (0.9 + 0.1 * Math.sin(t * 2.1));
      drawDrawer(E, t, { open, strip: { y: (FO.y0 + FO.y1) / 2, a: 1 }, glow, dust: 1, push: 0.05 + 0.012 * clamp((t - 158.8) / 1.9) });
      stack([
        { txt: 'WE CAN STILL', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.06, times: [tw('f3', 'we'), tw('f3', 'can'), tw('f3', 'still')] },
        { txt: 'READ IT.', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.04, times: [tw('f3', 'read'), tw('f3', 'it.')], curves: [E.HEAVY, E.PAYOFF] },
      ], 0.165, 0.016);
    },
  });

  // ---- end card (the series card over the last 2.6 s)
  const tEnd = DURATION - 2.6;
  S.push({
    name: 'end card', t0: tEnd, bg: 'dark',
    hits: [[tEnd + 0.12, 6, 5, 0.05]],
    draw(E) { E.titleCard(tEnd + 0.12, null, 0.2); },
  });
  return { S, SHEET: sheet };
}
