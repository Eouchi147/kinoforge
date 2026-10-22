// Beats 16 to 19: the turn (the executioner's plea), the lie, and the walk through his own town, naming people (86.4 to 123.8 s).
import { clamp, ease, lerp, rgba, keys } from './lib.js';

export function buildTurn(E) {
  const { C, W, H, U, AX, MEAS } = E, tw = E.tw, cream = C.cream, M = E.M;
  const S = [];
  const L = (s, extra = {}) => E.line({ color: cream, ...s, ...extra });
  const stack = (specs, top, gap, extra = {}) => { for (const s of E.stack(specs, top, gap).lines) L(s, extra); return null; };
  const dim = (to = 0.45, a0 = 0.8) => { const g = E.g, gr = g.createLinearGradient(0, 0, 0, to * H); gr.addColorStop(0, `rgba(14,13,11,${a0})`); gr.addColorStop(0.8, `rgba(14,13,11,${a0 * 0.8})`); gr.addColorStop(1, 'rgba(14,13,11,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, to * H); };
  const PALE = '#d6cdb8';

  // ---------------------------------------------------------------- the silence after "Eight times."
  S.push({
    name: 'silence after eight', t0: 86.40, bg: 'dark',
    draw(E) {
      const a = 0.55 * (1 - clamp((E.t - 86.5) / 1.1)), I = E.ink, y0 = 0.40 * H, hh = 0.07 * H, sp = 0.05 * W, x0 = W / 2 - 3.5 * sp;
      I.save(); I.strokeStyle = rgba(cream, a); I.lineCap = 'round'; I.lineWidth = 4 * U;
      for (let j = 0; j < 8; j++) { I.beginPath(); I.moveTo(x0 + j * sp, y0); I.lineTo(x0 + j * sp, y0 + hh); I.stroke(); }
      I.restore();
    },
  });

  // ---------------------------------------------------------------- k1, k2: something strange. The executioner begged him.
  S.push({
    name: 'k1 something strange', t0: 87.78, bg: 'dark',
    hits: [[tw('k1', 'strange'), 7, 6, 0.06]],
    draw(E) {
      stack([
        { txt: 'THEN SOMETHING', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, times: [tw('k1', 'then'), tw('k1', 'something')] },
        { txt: 'STRANGE', font: 'B', fit: 1.0, maxCap: 0.12, ls: 0.03, times: tw('k1', 'strange'), curve: E.PAYOFF },
        { txt: 'HAPPENED.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: tw('k1', 'happened.'), curve: E.HEAVY },
      ], 0.24, 0.026);
    },
  });
  S.push({
    name: 'k2 the executioner begged', t0: 90.16, bg: 'dark',
    hits: [[tw('k2', 'executioner,'), 6, 5, 0.05], [tw('k2', 'begged'), 3, 4, 0.02]],
    draw(E) {
      const b = E.stack([
        { txt: 'THE', font: 'B', cap: 0.038, ls: 0.22, times: tw('k2', 'the') },
        { txt: 'EXECUTIONER', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.02, times: tw('k2', 'executioner,'), curve: E.PAYOFF },
      ], 0.18, 0.022);
      for (const s of b.lines) L(s);
      const em = 0.034;
      L({ txt: 'the man who had', font: 'C5', em, base: 0.375, times: [tw('k2', 'the', 1), tw('k2', 'man'), tw('k2', 'who'), tw('k2', 'had')], mode: 'pop', alpha: 0.9 });
      L({ txt: 'just tortured him,', font: 'C5', em, base: 0.418, times: [tw('k2', 'just'), tw('k2', 'tortured'), tw('k2', 'him,')], mode: 'pop', alpha: 0.9 });
      const bg = E.stack([{ txt: 'BEGGED HIM:', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, times: [tw('k2', 'begged'), tw('k2', 'him:')], mode: 'pop', popDur: 0.5 }], 0.49, 0.02);
      for (const s of bg.lines) L(s);
    },
  });

  // ---------------------------------------------------------------- k3: the plea, in another hand (IM Fell, sloppy double strike, tilted)
  {
    const lines = [
      { txt: 'Confess to something.', base: 0.215, words: ['Confess', 'to', 'something.'], nth: [0, 0, 0] },
      { txt: 'True or not.', base: 0.325, words: ['True', 'or', 'not.'], nth: [0, 0, 0] },
      { txt: "If you don't,", base: 0.435, words: ['If', 'you', "don't,"], nth: [0, 0, 0] },
      { txt: 'they will never stop.', base: 0.545, words: ['they', 'will', 'never', 'stop.'], nth: [0, 0, 0, 0] },
    ];
    const em = E.emFit('F', 'they will never stop.', 0.97);
    const tEcho = tw('k3', 'stop.') + 0.12;
    S.push({
      name: 'k3 confess to something', t0: 95.10, bg: 'dark',
      hits: [[tw('k3', 'something.'), 4, 4, 0.03], [tw('k3', 'not.'), 4, 4, 0.03], [tw('k3', 'stop.'), 5, 5, 0.04]],
      draw(E) {
        const I = E.ink;
        I.save(); I.translate(AX, 0.4 * H); I.rotate(-0.018); I.translate(-AX, -0.4 * H);
        for (const l of lines) {
          const times = l.words.map((w, i) => tw('k3', w));
          const spec = { txt: l.txt, font: 'F', em, base: l.base, times, mode: 'pop', popDur: 0.45, color: PALE };
          E.line(spec); E.line({ ...spec, x: AX + 1.3 * U, base: l.base + 0.0012, alpha: 0.38 });
        }
        // "they will never stop": the line repeats down the page
        if (E.t >= tEcho) for (let n = 1; n <= 6; n++) { const tn = tEcho + n * 0.14; if (E.t < tn) break; const a = 0.5 * Math.pow(0.72, n - 1) * (1 - clamp((E.t - 102.2) / 0.4)); E.line({ txt: 'they will never stop.', font: 'F', em, base: 0.545 + n * 0.093, times: tn, mode: 'pop', popDur: 0.2, color: PALE, alpha: a }); }
        I.restore();
      },
    });
  }

  // ---------------------------------------------------------------- l1, l2: the lie, then they wanted names
  S.push({
    name: 'l1 so Junius lied', t0: 102.60, bg: 'dark',
    hits: [[tw('l1', 'So'), 5, 4, 0.04], [tw('l1', 'lied.'), 7, 6, 0.06], [tw('l1', 'devil.'), 7, 6, 0.06]],
    draw(E) {
      const t = E.t;
      if (t < 104.62) stack([
        { txt: 'SO JUNIUS', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: [tw('l1', 'So'), tw('l1', 'Junius')] },
        { txt: 'LIED.', font: 'B', fit: 0.62, maxCap: 0.14, ls: 0.04, times: tw('l1', 'lied.'), curve: E.PAYOFF },
      ], 0.22, 0.026);
      else {
        const COLD = '#d5d9da';
        E.line({ txt: 'HE MADE UP A STORY', font: 'T', cap: 0.0235, ls: 0.02, base: 0.245, times: ['he', 'made', 'up', 'a', 'story'].map((w) => tw('l1', w)), mode: 'type', color: COLD, perChar: 0.045 });
        E.line({ txt: 'ABOUT MEETING', font: 'T', cap: 0.0235, ls: 0.02, base: 0.295, times: [tw('l1', 'about'), tw('l1', 'meeting')], mode: 'type', color: COLD, perChar: 0.045 });
        for (const s of E.stack([
          { txt: 'THE', font: 'B', cap: 0.04, ls: 0.22, times: tw('l1', 'the') },
          { txt: 'DEVIL.', font: 'B', fit: 1.0, maxCap: 0.14, ls: 0.04, times: tw('l1', 'devil.'), curve: E.PAYOFF },
        ], 0.37, 0.024).lines) {
          L(s);
          // a lie is a double image: two cold ghosts slide off the word and settle
          if (s.txt === 'DEVIL.') { const k = (t - tw('l1', 'devil.')); if (k > 0) { const d = 9 * U * Math.exp(-k * 3.2); E.line({ ...s, color: '#9fa6a8', alpha: 0.55 * Math.exp(-k * 2.5), x: E.AX + d }); E.line({ ...s, color: '#9fa6a8', alpha: 0.45 * Math.exp(-k * 2.5), x: E.AX - d }); } }
        }
      }
    },
  });
  S.push({
    name: 'l2 then they wanted names', t0: 109.20, bg: 'dark',
    hits: [[tw('l2', 'names.'), 8, 6, 0.07]],
    draw(E) {
      stack([
        { txt: 'THEN THEY', font: 'B', fit: 1.0, maxCap: 0.045, ls: 0.08, times: [tw('l2', 'then'), tw('l2', 'they')] },
        { txt: 'WANTED', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: tw('l2', 'wanted'), curve: E.HEAVY },
        { txt: 'NAMES.', font: 'B', fit: 1.0, maxCap: 0.15, ls: 0.04, times: tw('l2', 'names.'), curve: E.PAYOFF },
      ], 0.22, 0.026);
    },
  });

  // ---------------------------------------------------------------- l3, l4: the walk through his town, street by street; the names multiply
  S.push({
    name: 'l3 walk his town street by street', t0: 111.07, bg: 'dark',
    hits: [[tw('l3', 'street'), 3, 3, 0.02], [tw('l3', 'by'), 3, 3, 0.02], [tw('l3', 'street,'), 4, 4, 0.03], [tw('l3', 'people.'), 5, 5, 0.04]],
    draw(E) {
      const t = E.t, c = M.cam(t); M.drawStreets(t, 111.1, 1.8, 0.95, c); M.drawWalk(t, c); dim(0.45, 0.85);
      if (t < 112.45) L({ txt: 'THEY MADE HIM WALK', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.04, base: 0.22, times: [tw('l3', 'they'), tw('l3', 'made'), tw('l3', 'him'), tw('l3', 'walk')], curves: [null, null, null, E.HEAVY] });
      else if (t < 114.07) L({ txt: 'THROUGH HIS OWN TOWN', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.04, base: 0.22, times: [tw('l3', 'through'), tw('l3', 'his'), tw('l3', 'own'), tw('l3', 'town')], curves: [null, null, null, E.HEAVY] });
      else if (t < 115.0) L({ txt: 'in his mind,', font: 'C', fit: 0.9, ls: 0, base: 0.23, times: [tw('l3', 'in'), tw('l3', 'his', 1), tw('l3', 'mind,')], mode: 'pop', popDur: 0.35 });
      else {
        L({ txt: 'STREET BY STREET,', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.04, base: 0.225, times: [tw('l3', 'street'), tw('l3', 'by'), tw('l3', 'street,')], curve: E.PAYOFF });
        L({ txt: 'AND NAME PEOPLE.', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, base: 0.31, times: [tw('l3', 'and'), tw('l3', 'name'), tw('l3', 'people.')], curves: [null, E.HEAVY, E.PAYOFF] });
      }
    },
  });
  S.push({
    name: 'l4 they gave him a name; he repeated it', t0: 117.50, bg: 'dark',
    hits: [[tw('l4', 'name.'), 9, 7, 0.07], [tw('l4', 'repeated'), 4, 4, 0.03], [tw('l4', 'it.'), 6, 6, 0.05]],
    draw(E) {
      const t = E.t, c = M.cam(t); M.drawStreets(t, 111.1, 1.8, 0.95, c); M.drawWalk(t, c); dim(0.46, 0.86);
      if (t < 119.50) stack([
        { txt: "WHEN HE COULDN'T", font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.05, times: [tw('l4', 'when'), tw('l4', 'he'), tw('l4', "couldn't")] },
        { txt: 'THINK OF ANYONE,', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.05, times: [tw('l4', 'think'), tw('l4', 'of'), tw('l4', 'anyone,')], curves: [null, null, E.HEAVY] },
      ], 0.20, 0.024);
      else if (t < 121.52) stack([
        { txt: 'THEY GAVE', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.06, times: [tw('l4', 'they'), tw('l4', 'gave')] },
        { txt: 'HIM A NAME.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, times: [tw('l4', 'him'), tw('l4', 'a'), tw('l4', 'name.')], curves: [null, null, E.PAYOFF] },
      ], 0.20, 0.024);
      else stack([
        { txt: 'AND HE', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.1, times: [tw('l4', 'and'), tw('l4', 'he', 1)] },
        { txt: 'REPEATED IT.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, times: [tw('l4', 'repeated'), tw('l4', 'it.')], curves: [E.HEAVY, E.PAYOFF] },
      ], 0.20, 0.024);
    },
  });
  return S;
}
