// Movements 5 and 6 (85.95 to 123.4 s): THE PLEA (the executioner, in another hand) and THE NAMES (the lie, then the walk through his own town).
// One scene: the desk after the ink has bled in from the tally. The map comes back for the walk.
import { clamp, ease, lerp, rgba, noise1 } from './lib.js';
import { makeKit } from './kit.js';

export function buildPlea(E) {
  const { C, W, H, U, AX, MEAS } = E, tw = E.tw, cream = C.cream, kit = makeKit(E), B = kit.block, M = E.M;
  const PALE = '#d6cdb8', COLD = '#d5d9da';
  const T8 = [83.56, 83.87, 84.22, 84.50, 84.80, 85.08, 85.40, 85.72];
  const S = [];
  const tally = (I, a) => {                                  // the same eight strokes as on the page, now in cream: the one thing the ink did not take
    const { y0, hh, sp } = E.tally; I.save(); I.strokeStyle = rgba(cream, a); I.lineCap = 'round'; I.lineWidth = 3.4 * U;
    T8.forEach((T, j) => { const x = AX + (j < 5 ? Math.min(j, 3) : 4 + (j - 5)) * sp + 0.005 * W * noise1(j, 4); I.beginPath();
      if (j === 4) { I.moveTo(AX - 4 * U, y0 + hh * 0.85); I.lineTo(AX - 4 * U + (3 * sp + 14 * U), y0 + hh * 0.85 - hh * 0.7); } else { I.moveTo(x, y0); I.lineTo(x + 2 * U * noise1(j, 7), y0 + hh); } I.stroke(); });
    I.restore();
  };
  const plea = [
    { txt: 'Confess to something.', base: 0.215, words: ['Confess', 'to', 'something.'] }, { txt: 'True or not.', base: 0.325, words: ['True', 'or', 'not.'] },
    { txt: "If you don't,", base: 0.435, words: ['If', 'you', "don't,"] }, { txt: 'they will never stop.', base: 0.545, words: ['they', 'will', 'never', 'stop.'] },
  ];
  const emP = E.emFit('F', 'they will never stop.', 0.97);
  S.push({
    name: 'M5/M6 desk: silence, plea, lie, names, the walk', t0: 85.95, bg: 'dark', trans: { kind: 'bleed', dur: 1.55, ease: 'inOutSine', at: [E.tally.x0 + 2.2 * E.tally.sp, E.tally.y0 + 0.5 * E.tally.hh] },
    // job: none. The type lands; the only physical event here is the slip of paper at the end (drawn, not shaken)
    draw(E) {
      const t = E.t, I = E.ink;
      // ---- the silence after "Eight times": the tally stays a moment on the dark and then goes
      const ta = 0.8 * (1 - clamp((t - 87.6) / 1.2)); if (ta > 0) tally(I, ta);
      // ---- "Then something strange happened."
      if (t < 90.35) B([
        { txt: 'THEN SOMETHING', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.06, times: [tw('k1', 'then'), tw('k1', 'something')] },
        { txt: 'STRANGE', font: 'B', fit: 1.0, maxCap: 0.12, ls: 0.03, times: tw('k1', 'strange'), curve: E.PAYOFF },
        { txt: 'HAPPENED.', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.03, times: tw('k1', 'happened.'), curve: E.HEAVY },
      ], 0.24, { out: 90.12, outDur: 0.22 });
      // ---- "The executioner, the man who had just tortured him, begged him:"
      if (t >= 90.15 && t < 95.4) {
        const o = { out: 95.0, outDur: 0.22 };
        B([{ txt: 'THE', font: 'B', cap: 0.038, ls: 0.22, times: tw('k2', 'the') }, { txt: 'EXECUTIONER', font: 'B', fit: 1.0, maxCap: 0.075, ls: 0.02, times: tw('k2', 'executioner,'), curve: E.PAYOFF }], 0.18, o);
        const em = 0.034, al = 0.9 * (1 - clamp((t - 95.0) / 0.22));
        E.line({ color: cream, txt: 'the man who had', font: 'C5', em, base: 0.375, times: [tw('k2', 'the', 1), tw('k2', 'man'), tw('k2', 'who'), tw('k2', 'had')], mode: 'pop', alpha: al });
        E.line({ color: cream, txt: 'just tortured him,', font: 'C5', em, base: 0.418, times: [tw('k2', 'just'), tw('k2', 'tortured'), tw('k2', 'him,')], mode: 'pop', alpha: al });
        B([{ txt: 'BEGGED HIM:', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, times: [tw('k2', 'begged'), tw('k2', 'him:')], mode: 'pop', popDur: 0.5 }], 0.49, o);
      }
      // ---- the plea: another hand (IM Fell English, struck twice a hair off register, tilted). It holds after "stop." and is not echoed.
      if (t >= 95.1 && t < 102.9) {
        const al = 1 - clamp((t - 102.45) / 0.25);
        I.save(); I.translate(AX, 0.4 * H); I.rotate(-0.018); I.translate(-AX, -0.4 * H);
        for (const l of plea) { const spec = { txt: l.txt, font: 'F', em: emP, base: l.base, times: l.words.map((w) => tw('k3', w)), mode: 'pop', popDur: 0.45, color: PALE, alpha: al }; E.line(spec); E.line({ ...spec, x: AX + 1.3 * U, base: l.base + 0.0012, alpha: 0.38 * al }); }
        I.restore();
      }
      // ---- "So Junius lied. He made up a story about meeting the devil."  The lie is a double image.
      if (t >= 102.5 && t < 104.75) B([
        { txt: 'SO JUNIUS', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: [tw('l1', 'So'), tw('l1', 'Junius')] },
        { txt: 'LIED.', font: 'B', fit: 0.62, maxCap: 0.14, ls: 0.04, times: tw('l1', 'lied.'), curve: E.PAYOFF },
      ], 0.22, { out: 104.62, outDur: 0.2 });
      if (t >= 104.6 && t < 109.35) {
        const out = 109.1, al = 1 - clamp((t - out) / 0.25);
        E.line({ txt: 'HE MADE UP A STORY', font: 'T', cap: 0.0235, ls: 0.02, base: 0.245, times: ['he', 'made', 'up', 'a', 'story'].map((w) => tw('l1', w)), mode: 'type', color: COLD, perChar: 0.045, alpha: al });
        E.line({ txt: 'ABOUT MEETING', font: 'T', cap: 0.0235, ls: 0.02, base: 0.295, times: [tw('l1', 'about'), tw('l1', 'meeting')], mode: 'type', color: COLD, perChar: 0.045, alpha: al });
        for (const s of E.stk([{ txt: 'THE', font: 'B', cap: 0.04, ls: 0.22, times: tw('l1', 'the') }, { txt: 'DEVIL.', font: 'B', fit: 1.0, maxCap: 0.14, ls: 0.04, times: tw('l1', 'devil.'), curve: E.PAYOFF }], 0.37, 0.3).lines) {
          E.line({ color: cream, ...s, alpha: al });
          if (s.txt === 'DEVIL.') { const k = t - tw('l1', 'devil.'); if (k > 0) { const d = 8 * U * Math.exp(-k * 3.0); for (const [dx, a] of [[d, 0.5], [-d, 0.4]]) E.line({ ...s, color: '#9fa6a8', alpha: a * Math.exp(-k * 2.4) * al, x: AX + dx }); } }   // a lie is a double image
        }
      }
      // ---- "Then they wanted names."
      if (t >= 109.1 && t < 111.2) B([
        { txt: 'THEN THEY', font: 'B', fit: 1.0, maxCap: 0.045, ls: 0.08, times: [tw('l2', 'then'), tw('l2', 'they')] },
        { txt: 'WANTED', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.03, times: tw('l2', 'wanted'), curve: E.HEAVY },
        { txt: 'NAMES.', font: 'B', fit: 1.0, maxCap: 0.15, ls: 0.04, times: tw('l2', 'names.'), curve: E.PAYOFF },
      ], 0.22, { out: 110.95, outDur: 0.22 });
      // ---- the walk: the plan comes back, the camera goes down to street level, the pen follows three streets, then the town fills with names
      if (t >= 110.9) {
        const c = M.cam(t); M.drawPlan(t, 111.0, 2.4, 0.95, c); M.drawWalk(t, c); kit.dim(0.47, 0.86);
        if (t < 112.5) B([{ txt: 'THEY MADE HIM WALK', font: 'B', fit: 1.0, maxCap: 0.06, ls: 0.04, times: [tw('l3', 'they'), tw('l3', 'made'), tw('l3', 'him'), tw('l3', 'walk')], curves: [null, null, null, E.HEAVY] }], 0.20, { out: 112.42, outDur: 0.2 });
        else if (t < 115.0) {
          const al = 1 - clamp((t - 114.9) / 0.2);
          B([{ txt: 'THROUGH HIS OWN TOWN', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.04, times: [tw('l3', 'through'), tw('l3', 'his'), tw('l3', 'own'), tw('l3', 'town')], curves: [null, null, null, E.HEAVY] }], 0.20, { alpha: al });
          E.line({ color: cream, txt: 'in his mind,', font: 'C', fit: 0.9, ls: 0, base: 0.30, times: [tw('l3', 'in'), tw('l3', 'his', 1), tw('l3', 'mind,')], mode: 'pop', popDur: 0.35, alpha: al });
        } else if (t < 117.5) B([
          { txt: 'STREET BY STREET,', font: 'B', fit: 1.0, maxCap: 0.07, ls: 0.04, times: [tw('l3', 'street'), tw('l3', 'by'), tw('l3', 'street,')], curve: E.PAYOFF },
          { txt: 'AND NAME PEOPLE.', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.04, times: [tw('l3', 'and'), tw('l3', 'name'), tw('l3', 'people.')], curves: [null, E.HEAVY, E.PAYOFF] },
        ], 0.205, { out: 117.45, outDur: 0.18 });
        if (t >= 117.4 && t < 119.55) B([
          { txt: "WHEN HE COULDN'T", font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.05, times: [tw('l4', 'when'), tw('l4', 'he'), tw('l4', "couldn't")] },
          { txt: 'THINK OF ANYONE,', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.05, times: [tw('l4', 'think'), tw('l4', 'of'), tw('l4', 'anyone,')], curves: [null, null, E.HEAVY] },
        ], 0.20, { out: 119.45, outDur: 0.18 });
        if (t >= 119.4 && t < 121.55) B([
          { txt: 'THEY GAVE', font: 'B', fit: 1.0, maxCap: 0.055, ls: 0.06, times: [tw('l4', 'they'), tw('l4', 'gave')] },
          { txt: 'HIM A NAME.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, times: [tw('l4', 'him'), tw('l4', 'a'), tw('l4', 'name.')], curves: [null, null, E.PAYOFF] },
        ], 0.20, { out: 121.45, outDur: 0.18 });
        if (t >= 121.45) B([
          { txt: 'AND HE', font: 'B', fit: 1.0, maxCap: 0.05, ls: 0.1, times: [tw('l4', 'and'), tw('l4', 'he', 1)] },
          { txt: 'REPEATED IT.', font: 'B', fit: 1.0, maxCap: 0.085, ls: 0.04, times: [tw('l4', 'repeated'), tw('l4', 'it.')], curves: [E.HEAVY, E.PAYOFF] },
        ], 0.20);
      }
    },
  });
  return S;
}
