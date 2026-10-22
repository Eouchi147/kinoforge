// Movements 7 and 8 (123.4 to 163.3 s): THE LETTER (written in a failing hand, folded, hidden; "I am innocent"; "Good night") and THE ARCHIVE
// (August 1628; the letter that probably never arrived; the file; the drawer opens and the light finds it; the end card).
// Scenes: letter3 (the page slides back onto the desk, as in the opening), desk5 (the fold, then everything on the dark desk), end card (a dissolve).
import { clamp, ease, lerp, rgba, mk, smoothstep, noise1, rng, measure, FONTS } from './lib.js';
import { makeKit } from './kit.js';
import { drawSheet } from './fold.js';

export function buildEnd(E) {
  const { C, W, H, U, AX, MEAS, PAD } = E, tw = E.tw, cream = C.cream, ink = C.ink, red = C.red, kit = makeKit(E), B = kit.block;
  const S = [];
  const DURATION = E.duration;

  // ================================================================ letter3: "He wrote all of this to his daughter, Veronica, over several days, with hands that barely worked."
  const em1 = E.emFit('C', 'to his daughter,', 0.80), emV = E.emFit('C', 'Veronica,', 0.82);
  const trem1 = (tk) => 0.30 + 1.5 * smoothstep(128.7, 131.4, tk);              // the hand gives out: tremor and sag grow with the page
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
    const tb = tw('e1', 'worked.') + 0.30;                                      // the pen gives out: a blot spreads where "worked." ends
    if (t >= tb) { const p = ease.outCubic(clamp((t - tb) / 0.38)), x = AX + MEAS * 0.52 + 0.10 * W, y = 0.560 * H + 0.006 * H, I = E.ink; I.save(); I.fillStyle = rgba(ink, 0.9); I.beginPath(); I.ellipse(x, y, 5 * U * p, 4 * U * p, 0.3, 0, 6.2832); I.fill(); I.fillRect(x - 1.1 * U, y, 2.2 * U, 18 * U * p); I.restore(); }
  }
  S.push({
    name: 'M7 letter 3: to Veronica, a failing hand', t0: 123.40, bg: 'cream', trans: { kind: 'slideIn', dir: 'bottom', dur: 0.62, ease: 'outCubic' },
    draw(E) { drawLetterPage(E, E.t); },                                        // job of the echo with the opening: the letter that began the film comes back to end it
  });

  // ---- the page as an image (front), its back, and the folded strip (used by the fold and by the archive)
  let SHEET = null, BACK = null, STRIP = null;
  const snapshot = () => {
    if (SHEET) return SHEET;
    const c = mk(W, H), sg = c.getContext('2d'), tmp = mk(W, H), tg = tmp.getContext('2d'); tg.textRendering = 'geometricPrecision'; tg.fontKerning = 'normal';
    const save = { g: E.g, ink: E.ink, t: E.t, f: E.f }; E.g = sg; E.ink = tg; E.t = 131.95; E.f = Math.round(131.95 * 24);
    sg.drawImage(E.PAPER.cream, -PAD, -PAD); drawLetterPage(E, 131.95);
    tg.globalCompositeOperation = 'destination-out'; tg.drawImage(E.INKNOISE, 0, 0); tg.globalCompositeOperation = 'source-over';
    sg.save(); sg.filter = `blur(${0.7 * U}px)`; sg.globalAlpha = 0.4; sg.drawImage(tmp, 0, 0); sg.restore(); sg.drawImage(tmp, 0, 0);
    E.g = save.g; E.ink = save.ink; E.t = save.t; E.f = save.f; SHEET = c;
    const bc = mk(W, H), bg = bc.getContext('2d'); bg.drawImage(E.PAPER.cream, -PAD, -PAD); bg.fillStyle = 'rgba(128,96,56,0.14)'; bg.fillRect(0, 0, W, H);   // the back: same fibre, a shade older
    const rr = rng(9); bg.lineCap = 'round'; for (let k = 0; k < 160; k++) { bg.strokeStyle = `rgba(120,90,50,${0.03 + 0.05 * rr()})`; bg.lineWidth = (0.6 + 0.8 * rr()) * U; const x = rr() * W, y = rr() * H; bg.beginPath(); bg.moveTo(x, y); bg.lineTo(x + (rr() - 0.5) * 30 * U, y + (rr() - 0.5) * 20 * U); bg.stroke(); }
    BACK = bc; return c;
  };
  const addrFn = (g, a, h3) => {                                                  // the outside of a folded letter carries the name it is for
    g.save(); g.globalAlpha = a; g.translate(W * 0.5, 1.5 * h3 + 0.008 * H); g.rotate(-0.018); g.fillStyle = 'rgba(26,22,18,0.88)'; g.font = FONTS.C(0.062 * H); g.letterSpacing = '0px'; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.fillText('Veronica', 0, 0); g.restore();
  };
  const strip = () => {
    if (STRIP) return STRIP; snapshot(); const c = mk(W, H), sg = c.getContext('2d');
    drawSheet(sg, { front: SHEET, back: BACK, sheetW: W, sheetH: H, thetaT: Math.PI, thetaB: Math.PI, U, shadow: 0, addr: 1, addrFn });
    const pad = 10 * U, y0 = H / 3 - pad, sc = mk(W, H / 3 + 2 * pad); sc.getContext('2d').drawImage(c, 0, y0, W, H / 3 + 2 * pad, 0, 0, W, H / 3 + 2 * pad); STRIP = sc; return sc;
  };
  function drawStrip(g, cx, cy, w, rot, alpha = 1) {                                // the folded letter, lying on something, with its own shadow
    const SC = strip(), s = w / W, h = SC.height * s, pad = 10 * U * s;
    g.save(); g.translate(cx, cy); g.rotate(rot); g.globalAlpha = alpha; g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = 20 * U; g.shadowOffsetY = 7 * U; g.drawImage(SC, -w / 2, -h / 2, w, h); g.restore(); return h - 2 * pad;
  }

  // ---- the fold (131.88 to 134.42): shrink on the desk, fold the top third down, fold the bottom third up, slide the strip behind a slit of light
  const SLOT = 0.745 * H, SC0 = 0.60, CY1 = 0.58 * H;
  const tShr = [131.90, 132.50], tA = [132.55, 133.02], tC = [133.08, 133.55], tS = [133.66, 134.42];
  function drawFold(E, t) {
    const g = E.g, SH = snapshot(), pS = ease.inOutCubic(clamp((t - tShr[0]) / (tShr[1] - tShr[0])));
    const thT = Math.PI * ease.inOutSine(clamp((t - tA[0]) / (tA[1] - tA[0]))), thB = Math.PI * ease.inOutSine(clamp((t - tC[0]) / (tC[1] - tC[0])));
    const pSlide = ease.inCubic(clamp((t - tS[0]) / (tS[1] - tS[0]))), s = lerp(1, SC0, pS), cy = lerp(0.5 * H, CY1, pS) + pSlide * 0.34 * H;
    // the slit of light the letter will slip behind (it appears as the fold completes)
    const la = smoothstep(133.3, 133.8, t);
    if (la > 0) { const gr = g.createLinearGradient(0, SLOT - 22 * U, 0, SLOT + 22 * U); gr.addColorStop(0, 'rgba(239,214,170,0)'); gr.addColorStop(0.5, `rgba(239,214,170,${0.16 * la})`); gr.addColorStop(1, 'rgba(239,214,170,0)'); g.fillStyle = gr; g.fillRect(0, SLOT - 22 * U, W, 44 * U); g.fillStyle = 'rgba(4,3,3,0.9)'; g.fillRect(0.06 * W, SLOT - 2.5 * U, 0.88 * W, 5 * U); g.fillStyle = `rgba(239,214,170,${0.55 * la})`; g.fillRect(0.06 * W, SLOT - 0.8 * U, 0.88 * W, 1.6 * U); }
    g.save(); if (t >= tS[0]) { g.beginPath(); g.rect(0, 0, W, SLOT - 2.5 * U); g.clip(); }
    g.translate(W / 2, cy); g.scale(s, s); g.translate(-W / 2, -H / 2);
    drawSheet(g, { front: SH, back: BACK, sheetW: W, sheetH: H, thetaT: thT, thetaB: thB, U: U / s, shadow: smoothstep(0, 1, pS), addr: smoothstep(133.45, 133.75, t), addrFn });
    g.restore();
    E.slotLine(la * (1 - smoothstep(134.45, 135.2, t)));
  }
  E.slotLine = (a) => { if (a <= 0.001) return; const g = E.g; g.fillStyle = `rgba(239,214,170,${0.6 * a})`; g.fillRect(0.06 * W, SLOT - 0.8 * U, 0.88 * W, 1.6 * U); };

  // ---- the archive drawer (a drawer of case files seen from above), used from "The court kept it in his file."
  const DR = { x0: 0.07 * W, x1: 0.93 * W, y0: 0.44 * H, y1: 0.82 * H }, FO = { x0: 0.13 * W, x1: 0.87 * W, y0: 0.485 * H, y1: 0.775 * H };
  const motes = (() => { const r = rng(606), a = []; for (let k = 0; k < 46; k++) a.push({ x: r(), y: r(), s: 0.004 + 0.01 * r(), z: 0.6 + 1.8 * r(), p: r() * 6.28 }); return a; })();
  function drawDrawer(E, t, st) {                                                  // st: { open 0..1, strip: {y (absolute), a}|null, glow, dust, push, dy (slide in from below, px) }
    const g = E.g, cx = W / 2, cyy = 0.63 * H, push = st.push || 0, dy = st.dy || 0;
    g.save(); g.translate(cx, cyy + dy); g.scale(1 + push, 1 + push); g.translate(-cx, -cyy);
    const rim = 15 * U;
    g.save(); g.shadowColor = 'rgba(0,0,0,0.8)'; g.shadowBlur = 40 * U; g.shadowOffsetY = 14 * U; g.fillStyle = '#17181a'; g.fillRect(DR.x0 - rim, DR.y0 - rim, DR.x1 - DR.x0 + 2 * rim, DR.y1 - DR.y0 + 2 * rim + 0.10 * H); g.restore();
    let gr = g.createLinearGradient(0, DR.y0 - rim, 0, DR.y1 + rim); gr.addColorStop(0, '#3a3d40'); gr.addColorStop(1, '#17181a'); g.fillStyle = gr; g.fillRect(DR.x0 - rim, DR.y0 - rim, DR.x1 - DR.x0 + 2 * rim, DR.y1 - DR.y0 + 2 * rim);
    g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(DR.x0 - rim, DR.y0 - rim, DR.x1 - DR.x0 + 2 * rim, 2 * U);
    g.fillStyle = '#080707'; g.fillRect(DR.x0, DR.y0, DR.x1 - DR.x0, DR.y1 - DR.y0);
    gr = g.createLinearGradient(0, DR.y0, 0, DR.y0 + 46 * U); gr.addColorStop(0, 'rgba(0,0,0,0.85)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(DR.x0, DR.y0, DR.x1 - DR.x0, 46 * U);
    const ly0 = DR.y1 + rim, ly1 = ly0 + 0.10 * H;
    gr = g.createLinearGradient(0, ly0, 0, ly1); gr.addColorStop(0, '#2e3033'); gr.addColorStop(1, '#141516'); g.fillStyle = gr; g.fillRect(DR.x0 - rim, ly0, DR.x1 - DR.x0 + 2 * rim, ly1 - ly0);
    g.fillStyle = 'rgba(255,255,255,0.09)'; g.fillRect(DR.x0 - rim, ly0, DR.x1 - DR.x0 + 2 * rim, 2 * U);
    const pw = 0.30 * W, ph = 0.034 * H; g.fillStyle = '#c9ced0'; g.fillRect(cx - pw / 2, ly0 + 0.022 * H, pw, ph); g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(cx - pw / 2, ly0 + 0.022 * H + ph - 1.5 * U, pw, 1.5 * U);
    g.fillStyle = '#14171a'; g.font = `400 ${0.0145 * H}px "Special Elite"`; g.letterSpacing = (0.12 * 0.0145 * H) + 'px'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('JUNIUS, 1628', cx, ly0 + 0.022 * H + ph / 2 + 1 * U); g.textAlign = 'left'; g.letterSpacing = '0px';
    g.fillStyle = '#0c0d0e'; g.fillRect(cx - 0.10 * W, ly0 + 0.066 * H, 0.20 * W, 0.012 * H); g.fillStyle = 'rgba(255,255,255,0.14)'; g.fillRect(cx - 0.10 * W, ly0 + 0.066 * H, 0.20 * W, 1.5 * U);
    g.save(); g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 16 * U; g.shadowOffsetY = 5 * U; g.fillStyle = '#b9bfc1'; g.fillRect(FO.x0, FO.y0, FO.x1 - FO.x0, FO.y1 - FO.y0); g.restore();
    g.fillStyle = '#bcc2c4'; g.fillRect(FO.x0 - 1 * U, FO.y0 - 0.014 * H, 0.22 * W, 0.016 * H);
    if (st.strip) drawStrip(g, (FO.x0 + FO.x1) / 2, st.strip.y - dy, 0.64 * W, st.strip.rot ?? -0.012, st.strip.a ?? 1);
    if (st.glow > 0) { const gg = g.createRadialGradient(cx, (FO.y0 + FO.y1) / 2, 10, cx, (FO.y0 + FO.y1) / 2, 0.55 * W); gg.addColorStop(0, `rgba(255,214,150,${0.28 * st.glow})`); gg.addColorStop(1, 'rgba(255,214,150,0)'); g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = gg; g.fillRect(DR.x0, DR.y0 - 60 * U, DR.x1 - DR.x0, DR.y1 - DR.y0 + 120 * U); g.restore(); }
    const th = Math.PI * clamp(st.open), c = Math.cos(th), cw = FO.x1 - FO.x0;                       // the cover: hinge on the left edge; open 0 = shut over the folder, 1 = lying open to the left
    {
      g.save(); g.translate(FO.x0, 0); g.scale(Math.abs(c) < 1e-3 ? 1e-3 : c, 1);
      g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 14 * U; g.fillStyle = c >= 0 ? '#cdd2d3' : '#a9b0b2'; g.fillRect(0, FO.y0, cw, FO.y1 - FO.y0); g.shadowColor = 'rgba(0,0,0,0)';
      g.fillStyle = `rgba(0,0,0,${0.35 * (1 - Math.abs(c))})`; g.fillRect(0, FO.y0, cw, FO.y1 - FO.y0);
      if (c > 0) { g.fillStyle = '#2a2f33'; g.font = `400 ${0.0175 * H}px "Special Elite"`; g.letterSpacing = (0.12 * 0.0175 * H) + 'px'; g.textBaseline = 'alphabetic'; g.fillText('JOHANNES JUNIUS', 0.05 * cw, FO.y0 + 0.04 * H); g.fillRect(0.05 * cw, FO.y0 + 0.05 * H, 0.5 * cw, 2 * U); g.letterSpacing = '0px'; }
      g.restore();
    }
    if (st.dust > 0) { g.save(); for (const m of motes) { const yy = DR.y0 + ((m.y + t * m.s) % 1) * (DR.y1 - DR.y0), xx = DR.x0 + m.x * (DR.x1 - DR.x0) + 14 * U * Math.sin(t * 0.5 + m.p); g.fillStyle = `rgba(255,236,200,${0.30 * st.dust * (0.5 + 0.5 * Math.sin(t * 1.3 + m.p))})`; g.beginPath(); g.arc(xx, yy, m.z * U, 0, 6.2832); g.fill(); } g.restore(); }
    g.restore();
  }

  // ================================================================ desk5: fold, "I am innocent", "Good night", August 1628, the letter that never arrived, the file, the drawer
  const FILE_T = [152.95, 153.65], COVER_T = [153.95, 154.48];
  S.push({
    name: 'M7/M8 desk: the fold, innocent, good night, August, the file, the drawer', t0: 131.88, bg: 'dark',
    // jobs: the cover of the file closes with a thump (154.5); nothing else shakes
    hits: [[154.52, 7, 6]],
    draw(E) {
      const t = E.t, g = E.g, I = E.ink;
      // ---- "He asked her to hide the letter." the page shrinks, folds in thirds along its creases, and slips behind a slit of light
      if (t < 134.9) {
        B([
          { txt: 'HE ASKED HER', font: 'B', fit: 1.0, maxCap: 0.04, ls: 0.14, times: [tw('e2', 'he'), tw('e2', 'asked'), tw('e2', 'her')] },
          { txt: 'TO HIDE THE LETTER.', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, times: [tw('e2', 'to'), tw('e2', 'hide'), tw('e2', 'the'), tw('e2', 'letter.')], curves: [null, E.HEAVY, null, E.PAYOFF] },
        ], 0.15, { out: 134.5, outDur: 0.25, k: 0.5, alpha: smoothstep(132.3, 132.6, t) });
        E.ink.save(); drawFold(E, t); E.ink.restore();
      }
      // ---- "He wrote: I am innocent."  the one red mark of the film
      if (t >= 134.6 && t < 138.15) {
        const al = 1 - clamp((t - 137.85) / 0.25);
        E.slotLine(0.5 * (1 - clamp((t - 134.47) / 0.7)));
        E.line({ color: cream, txt: 'HE WROTE:', font: 'B', cap: 0.04, ls: 0.2, base: 0.20, times: [tw('e3', 'he'), tw('e3', 'wrote:')], alpha: al });
        const emA = E.emFit('C', 'innocent.', 0.98), tg = tw('e3', 'innocent.') + 0.3;
        if (t > tg) { const k = smoothstep(tg, tg + 1.2, t), gr = g.createRadialGradient(W * 0.5, 0.42 * H, 10, W * 0.5, 0.42 * H, 0.45 * W); gr.addColorStop(0, `rgba(207,59,46,${0.10 * k * al})`); gr.addColorStop(1, 'rgba(207,59,46,0)'); g.fillStyle = gr; g.fillRect(0, 0.2 * H, W, 0.5 * H); }
        E.hand({ txt: 'I am', em: 0.092, base: 0.325, times: [tw('e3', 'I'), tw('e3', 'am')], color: red, trem: () => 0.55, seed: 21, alpha: al });
        E.hand({ txt: 'innocent.', em: emA, base: 0.455, times: [tw('e3', 'innocent.')], color: red, trem: () => 0.5, seed: 22, lastDur: 0.75, maxWord: 0.75, alpha: al });
      }
      // ---- "And he ended with: Good night. Your father will never see you again."  the writing weakens and fades
      if (t >= 138.1 && t < 145.0) {
        const fade = 1 - 0.92 * smoothstep(143.6, 144.85, t);
        E.hand({ txt: 'I am innocent.', em: E.emFit('C', 'I am innocent.', 0.62), base: 0.195, times: [0, 0, 0], color: red, trem: () => 0.45, seed: 23, alpha: 0.5 * fade * clamp((t - 138.1) / 0.2), glyph: 0.0001, dry: 0.01 });   // his claim stays on the page while he says goodbye
        E.line({ color: cream, txt: 'AND HE ENDED WITH:', font: 'B', fit: 1.0, maxCap: 0.035, ls: 0.12, base: 0.285, times: [tw('e4', 'and'), tw('e4', 'he'), tw('e4', 'ended'), tw('e4', 'with:')], alpha: fade });
        E.hand({ txt: 'Good night.', em: E.emFit('C', 'Good night.', 0.98), base: 0.415, times: [tw('e4', 'Good'), tw('e4', 'night.')], color: cream, trem: () => 0.5, seed: 31, alpha: fade });
        E.hand({ txt: 'Your father', em: 0.048, base: 0.50, times: [tw('e4', 'Your'), tw('e4', 'father')], color: cream, trem: () => 0.7, seed: 32, alpha: 0.92 * fade });
        E.hand({ txt: 'will never see', em: 0.048, base: 0.56, times: [tw('e4', 'will'), tw('e4', 'never'), tw('e4', 'see')], color: cream, trem: () => 0.8, seed: 33, alpha: 0.8 * fade });
        E.hand({ txt: 'you again.', em: 0.048, base: 0.62, times: [tw('e4', 'you'), tw('e4', 'again.')], color: cream, trem: () => 1.0, seed: 34, alpha: 0.65 * fade, lastDur: 0.9, maxWord: 0.9 });
      }
      // ---- "That August, Johannes Junius was executed."
      if (t >= 144.8 && t < 149.25) {
        const al = 1 - clamp((t - 149.05) / 0.15);
        E.line({ color: cream, txt: 'THAT', font: 'B', cap: 0.035, ls: 0.3, base: 0.185, times: tw('f1', 'that'), alpha: al });
        E.line({ color: cream, txt: 'AUGUST', font: 'B', fit: 1.0, maxCap: 0.135, ls: 0.03, base: 0.335, times: tw('f1', 'August,'), mode: 'stamp', smear: true, alpha: al });
        E.line({ color: cream, txt: '1628', font: 'C', em: 0.036, base: 0.385, times: tw('f1', 'August,') + 0.5, mode: 'pop', alpha: 0.85 * al });
        const nm = E.line({ color: cream, txt: 'JOHANNES JUNIUS', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, base: 0.46, times: [tw('f1', 'Johannes'), tw('f1', 'Junius')], curves: [null, E.HEAVY], alpha: al });
        E.line({ color: cream, txt: 'WAS EXECUTED.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.04, base: 0.56, times: [tw('f1', 'was'), tw('f1', 'executed.')], curves: [null, E.PAYOFF], alpha: al });
        const ts = tw('f1', 'executed.') + 0.3;                                  // the name is struck through
        if (t >= ts) { const p = ease.outCubic(clamp((t - ts) / 0.35)), y = nm.base - nm.cap * 0.5; I.fillStyle = rgba(cream, 0.9 * al); I.fillRect(nm.inkL - 6 * U, y, (nm.inkW + 12 * U) * p, Math.max(2, 0.0026 * H)); }
      }
      // ---- "His letter probably never reached his daughter." the folded letter comes up from below (the lower half of the desk)
      if (t >= 148.9 && t < 152.2) {
        const p = ease.outBack(clamp((t - 148.97) / 0.5));
        if (t < 152.95) drawStrip(g, W * 0.5, lerp(1.02 * H, 0.745 * H, p), 0.56 * W, -0.035 + 0.02 * ease.outCubic(clamp((t - 149.0) / 1.2)), clamp((t - 148.97) / 0.1));
        B([
          { txt: 'HIS LETTER', font: 'B', cap: 0.04, ls: 0.2, times: [149.30, 149.36] },
          { txt: 'PROBABLY', font: 'B', fit: 0.6, maxCap: 0.04, ls: 0.12, times: tw('f2', 'probably') },
          { txt: 'NEVER', font: 'B', fit: 0.8, maxCap: 0.13, ls: 0.03, times: tw('f2', 'never'), curve: E.PAYOFF },
          { txt: 'REACHED', font: 'B', fit: 0.8, maxCap: 0.07, ls: 0.04, times: tw('f2', 'reached'), curve: E.HEAVY },
          { txt: 'HIS DAUGHTER.', font: 'B', fit: 1.0, maxCap: 0.045, ls: 0.06, times: [tw('f2', 'his', 1), tw('f2', 'daughter.')] },
        ], 0.15, { out: 151.95, outDur: 0.15, k: 0.3 });
      }
      // ---- the drawer rises under the letter; "The court kept it in his file."  the letter goes into the folder and the cover closes
      if (t >= 151.9 && t < 154.8) {
        const pr = ease.outCubic(clamp((t - 151.95) / 0.65)), pD = ease.inOutCubic(clamp((t - FILE_T[0]) / (FILE_T[1] - FILE_T[0]))), cyS = (FO.y0 + FO.y1) / 2, open = 1 - ease.inQuad(clamp((t - COVER_T[0]) / (COVER_T[1] - COVER_T[0])));
        drawDrawer(E, t, { open, strip: { y: lerp(0.745 * H, cyS, pD), a: 1, rot: lerp(-0.015, -0.012, pD) }, glow: 0.35 * open, dust: 0, dy: (1 - pr) * 0.42 * H });
        B([
          { txt: 'THE COURT', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.1, times: [tw('f2', 'The'), tw('f2', 'court')] },
          { txt: 'KEPT IT', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.06, times: [tw('f2', 'kept'), tw('f2', 'it')] },
          { txt: 'IN HIS FILE.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.04, times: [tw('f2', 'in'), tw('f2', 'his', 2), tw('f2', 'file.')], curves: [null, null, E.PAYOFF] },
        ], 0.15, { out: 154.50, outDur: 0.12, k: 0.3 });
      }
      // ---- "And that is why, almost four hundred years later, we can still read it."  the drawer, shut, then opened on the letter in a pool of warm light
      if (t >= 154.7) {
        const k = clamp((t - 154.72) / 4.1), tO = [158.86, 159.34], open = ease.outCubic(clamp((t - tO[0]) / (tO[1] - tO[0]))), glow = smoothstep(158.95, 159.8, t) * (0.9 + 0.1 * Math.sin(t * 2.1));
        drawDrawer(E, t, { open, strip: t >= tO[0] ? { y: (FO.y0 + FO.y1) / 2, a: 1 } : null, glow, dust: 1, push: t < 158.8 ? 0.05 * k : 0.05 + 0.012 * clamp((t - 158.8) / 1.9) });
        if (t < 158.8) B([
          { txt: 'AND THAT IS WHY,', font: 'B', fit: 1.0, maxCap: 0.034, ls: 0.14, times: [tw('f3', 'And'), tw('f3', 'that'), tw('f3', 'is'), tw('f3', 'why,')] },
          { txt: 'ALMOST FOUR HUNDRED', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.04, times: [tw('f3', 'almost'), tw('f3', 'four'), tw('f3', 'hundred')], curves: [null, E.HEAVY, E.HEAVY] },
          { txt: 'YEARS LATER,', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.04, times: [tw('f3', 'years'), tw('f3', 'later,')], curves: [null, E.PAYOFF] },
        ], 0.15, { out: 158.62, outDur: 0.15, k: 0.3 });
        if (t >= 158.7) B([
          { txt: 'WE CAN STILL', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.06, times: [tw('f3', 'we'), tw('f3', 'can'), tw('f3', 'still')] },
          { txt: 'READ IT.', font: 'B', fit: 1.0, maxCap: 0.115, ls: 0.04, times: [tw('f3', 'read'), tw('f3', 'it.')], curves: [E.HEAVY, E.PAYOFF] },
        ], 0.15, { k: 0.3 });
      }
    },
  });

  // ---- end card: a dissolve (the story is over and the series card takes the screen)
  const tEnd = 160.715;
  S.push({
    name: 'end card', t0: tEnd, bg: 'dark', trans: { kind: 'fade', dur: 0.5 },
    hits: [[tEnd + 0.62, 3, 5]],
    draw(E) { E.titleCard(tEnd + 0.62, null, 0.2); },
  });
  return S;
}
