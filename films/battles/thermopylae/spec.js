// The Battle of Thermopylae (480 BC): Battle Map spec. Times come from the cue words (see films/lib/battlemap/SPEC.md).
// Teams: the Persians are red (team 'rome'), the Greeks are blue (team 'carthage').
// Stages: main = the pass (x east, z south; the Persians come from the north, the sea is on the east, the cliff wall on the west);
//         aeg  = the Aegean (hook, the squabbling cities, Athens, Salamis, Plataea);  emp = the Persian Empire, Egypt to India.
// The ASR spelled some words oddly in cues.json: "Dianik," (Dienekes), "Effialty's" (Ephialtes), "Thespier", and "past" for "pass" (l10, l17): use prefixes.
const PER = { team: 'rome' }, GRE = { team: 'carthage' };
const cues = await (await fetch(new URL('./cues.json', import.meta.url))).json();
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
const wordT = (line, word) => cues.lines.find((l) => l.id === line).words.find((w) => norm(w[0]).startsWith(norm(word)))[1];
const L = (at, until, text, o = {}) => ({ at, until, text, ...o });
const I = (at, until, icon, o = {}) => ({ at, until, icon, ...o });
const ell = (cx, cz, rx, rz, rot = 0, n = 16) => Array.from({ length: n }, (_, i) => { const a = i / n * Math.PI * 2, c = Math.cos(rot), s = Math.sin(rot); const x = Math.cos(a) * rx * (1 + 0.1 * Math.sin(a * 3 + cx)), z = Math.sin(a) * rz * (1 + 0.1 * Math.cos(a * 2 + cz)); return [cx + x * c - z * s, cz + x * s + z * c]; });

// ====================================================================================== the pass (main stage)
const ZS = [-280, -200, -140, -90, -50, -20, 0, 25, 55, 100, 160, 280];
const FOOT = [-250, -200, -158, -108, -66, -36, -18, -18, -30, -76, -136, -230];   // where the cliff wall meets the road
const COAST = [170, 108, 74, 52, 34, 22, 14, 14, 20, 44, 84, 150];                  // where the sea begins
const at = (tab, z) => { let i = 0; while (i < ZS.length - 2 && z > ZS[i + 1]) i++; const u = (z - ZS[i]) / (ZS[i + 1] - ZS[i]); return tab[i] + (tab[i + 1] - tab[i]) * Math.max(0, Math.min(1, u)); };
const flats = [-210, -160, -110, -60, -20, 20, 60, 110, 170].map((z) => { const f = at(FOOT, z), c = at(COAST, z); return { type: 'flat', at: [(f + c) / 2, z], r: Math.max(8, (c - f) / 2 - 7), level: 1.6, soft: 10, amount: 0.96 }; });
const CX = -4; // the road's centre line at the gate

const passWorld = {
  seed: 480, size: [640, 560], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 112, elevation: 32 }, sunEve: { azimuth: 70, elevation: 7 },
  style: { contour: 2, pxPerUnit: 5.4, palette: [[-4, [0.70, 0.76, 0.62]], [1.5, [0.84, 0.77, 0.52]], [8, [0.77, 0.69, 0.45]], [26, [0.72, 0.57, 0.40]], [52, [0.68, 0.61, 0.55]], [86, [0.90, 0.88, 0.84]]], paletteSoft: 6 },
  features: [
    { type: 'undulate', amp: 3, scale: 100 }, { type: 'undulate', amp: 1, scale: 30 },
    { type: 'mountains', poly: [[-460, -300], ...ZS.map((z, i) => [FOOT[i] - 4, z]), [-460, 300]], h: 86, scale: 64, ridged: 0.5, edge: 13 },
    { type: 'hill', at: [-84, -66], r: [20, 22], h: 9, rot: 20 },
    { type: 'sea', poly: [...ZS.map((z, i) => [COAST[i] + 3, z]), [470, 300], [470, -300]], shelf: 26, depth: 7, beach: 5 },
    { type: 'woods', at: [-70, 196], r: [26, 12], rot: 10 }, { type: 'woods', at: [30, -240], r: [20, 10] },
    { type: 'road', path: [[-60, -280], [-34, -150], [CX, -30], [CX, 40], [-20, 130], [-70, 280]], w: 4, meander: 2 },
    ...flats,
  ],
};

// ====================================================================================== the Aegean (stage aeg)
const EUR = [[-270, -210], [270, -210], [270, -160], [175, -150], [120, -140], [82, -122], [70, -100], [66, -92], [60, -100], [56, -130], [30, -134], [-4, -134], [-30, -128], [-28, -112], [-10, -100], [-22, -90], [-40, -105], [-55, -118], [-62, -122],
  [-72, -105], [-70, -80], [-62, -59], [-70, -46], [-72, -38], [-66, -26], [-58, -14], [-52, -4], [-44, 2], [-34, 6], [-22, 10], [-18, 26], [-26, 30], [-34, 22], [-40, 16], [-52, 10], [-62, 6], [-66, 14], [-58, 32], [-50, 40], [-46, 62], [-52, 88],
  [-70, 92], [-90, 92], [-108, 70], [-120, 50], [-135, 38], [-140, 22], [-150, 2], [-160, -25], [-190, -60], [-210, -110], [-270, -120]];
const ASIA = [[270, -135], [170, -128], [126, -118], [96, -104], [82, -88], [74, -78], [70, -68], [80, -56], [90, -40], [100, -18], [104, -6], [112, 14], [110, 40], [116, 60], [134, 64], [152, 70], [190, 84], [220, 86], [270, 100]];
const AEG_CITIES = { athens: [-16, 14], corinth: [-56, 30], tegea: [-98, 46], sparta: [-80, 74] };
const THERMO = [-80, -34];
const aegWorld = {
  seed: 479, size: [540, 420], res: 1, base: 0, meshStep: 2.2,
  sun: { azimuth: 250, elevation: 32 }, sunEve: { azimuth: 284, elevation: 10 },
  style: { contour: 4, pxPerUnit: 7, palette: [[-4, [0.62, 0.74, 0.50]], [3, [0.76, 0.76, 0.48]], [12, [0.80, 0.70, 0.46]], [26, [0.72, 0.58, 0.42]], [40, [0.70, 0.64, 0.58]], [58, [0.95, 0.94, 0.92]]], paletteSoft: 5 },
  features: [
    { type: 'undulate', amp: 3, scale: 70 },
    { type: 'mountains', path: [[-180, -100], [-135, -70], [-110, -34], [-100, 10], [-106, 50]], w: 20, h: 34, ridged: 0.8, scale: 28, edge: 12 },
    { type: 'mountains', at: [-98, -36], r: [15, 24], h: 28, ridged: 0.85, scale: 20, edge: 8 },
    { type: 'mountains', at: [-120, -90], r: [22, 22], h: 28, ridged: 0.8, scale: 24, edge: 10 },
    { type: 'mountains', at: [-20, -128], r: [34, 10], h: 22, ridged: 0.7, scale: 24, edge: 8 },
    { type: 'sea', poly: [[-420, -300], [420, -300], [420, 300], [-420, 300]], shelf: 30, depth: 8 },
    { type: 'land', wob: 1.4, shelf: 14, poly: EUR }, { type: 'land', wob: 1.4, shelf: 14, poly: ASIA },
    { type: 'land', wob: 1, shelf: 10, poly: [[-52, -48], [-44, -50], [-30, -30], [-14, -10], [2, 6], [0, 14], [-10, 12], [-26, -4], [-42, -24], [-52, -40]] },   // Euboea
    { type: 'land', wob: 1, shelf: 10, poly: [[-70, 140], [-20, 134], [30, 138], [62, 146], [52, 158], [-30, 162], [-72, 154]] },   // Crete
    { type: 'land', wob: 1, shelf: 8, poly: ell(88, -52, 12, 7, 0.5) }, { type: 'land', wob: 1, shelf: 8, poly: ell(92, -8, 6, 9, 0.2) }, { type: 'land', wob: 1, shelf: 8, poly: ell(34, -86, 8, 6) },
    { type: 'land', wob: 1, shelf: 8, poly: ell(8, 24, 6, 8) }, { type: 'land', wob: 1, shelf: 8, poly: ell(26, 50, 7, 6) }, { type: 'land', wob: 1, shelf: 8, poly: ell(46, 76, 8, 6) }, { type: 'land', wob: 1, shelf: 8, poly: ell(-8, -6, 5, 7) },
    { type: 'land', wob: 0.6, shelf: 6, poly: ell(-38, 16, 3.4, 2.4) },   // Salamis
    { type: 'woods', at: [-130, -20], r: [14, 22] }, { type: 'woods', at: [-30, -150], r: [26, 8] }, { type: 'woods', at: [140, 30], r: [22, 18] },
    { type: 'farms', rect: [-30, -80, 70, 40, 10], cell: [10, 8] }, { type: 'farms', rect: [140, -60, 90, 70, 0], cell: [12, 9] },
  ],
};

// ====================================================================================== the Persian Empire (stage emp), 1 unit about 6 km
const EMP_REGION = [[-335, 38], [-300, 34], [-250, 46], [-215, 46], [-188, 44], [-172, 2], [-178, -46], [-226, -40], [-258, -42], [-300, -60], [-318, -108], [-322, -135], [-290, -140], [-240, -136], [-190, -132], [-150, -134], [-110, -140], [-80, -150],
  [-30, -125], [10, -82], [30, -62], [80, -72], [112, -100], [118, -150], [130, -215], [260, -218], [390, -205], [405, -120], [425, -40], [415, 60], [380, 150], [330, 180], [318, 170], [209, 158], [150, 138], [110, 124], [78, 106], [50, 85], [28, 70],
  [-10, 75], [-90, 70], [-150, 70], [-185, 100], [-205, 120], [-190, 170], [-190, 218], [-260, 218], [-300, 160], [-335, 100]];
const empWorld = {
  seed: 486, size: [900, 460], res: 1, base: 0, meshStep: 3,
  sun: { azimuth: 250, elevation: 32 }, sunEve: { azimuth: 284, elevation: 10 },
  style: { contour: 5, pxPerUnit: 4.5, palette: [[-4, [0.62, 0.74, 0.50]], [3, [0.86, 0.80, 0.56]], [12, [0.88, 0.76, 0.50]], [26, [0.80, 0.64, 0.44]], [44, [0.72, 0.62, 0.55]], [62, [0.95, 0.94, 0.92]]], paletteSoft: 6 },
  features: [
    { type: 'undulate', amp: 5, scale: 110 },
    { type: 'mountains', path: [[-200, -40], [-110, -30], [-30, 6], [50, 38], [130, 60]], w: 30, h: 36, ridged: 0.8, scale: 40, edge: 16 },
    { type: 'mountains', path: [[270, -70], [340, -78], [420, -104]], w: 34, h: 62, ridged: 0.85, scale: 44, edge: 18 },
    { type: 'mountains', path: [[-250, -150], [-160, -150], [-80, -158]], w: 22, h: 30, ridged: 0.7, scale: 34, edge: 14 },
    { type: 'sea', poly: [[-460, 55], [-380, 48], [-330, 34], [-290, 38], [-257, 50], [-240, 46], [-188, 44], [-172, 2], [-178, -48], [-225, -41], [-256, -43], [-300, -62], [-315, -100], [-322, -112], [-345, -118], [-362, -112], [-374, -98], [-380, -84], [-376, -66], [-372, -56], [-384, -60], [-394, -76], [-404, -92], [-420, -106], [-460, -118]], shelf: 20, depth: 8, beach: 6 },
    { type: 'sea', poly: [[-280, -150], [-240, -135], [-200, -130], [-150, -130], [-110, -140], [-70, -160], [-70, -205], [-120, -228], [-290, -228], [-300, -170]], shelf: 20, depth: 8 },
    { type: 'sea', poly: [[10, -62], [40, -60], [80, -70], [112, -100], [118, -140], [112, -190], [100, -232], [50, -232], [40, -175], [20, -120], [8, -85]], shelf: 14, depth: 6 },
    { type: 'sea', poly: [[-216, 98], [-200, 100], [-170, 185], [-150, 232], [-190, 232], [-218, 140]], shelf: 10, depth: 5 },
    { type: 'sea', poly: [[28, 70], [50, 85], [78, 106], [110, 124], [150, 138], [209, 158], [318, 170], [345, 200], [364, 232], [215, 232], [206, 212], [165, 170], [148, 160], [125, 150], [100, 128], [75, 114], [55, 98], [30, 88]], shelf: 20, depth: 8 },
    { type: 'river', name: 'Nile', path: [[-232, 232], [-236, 150], [-234, 90], [-240, 52]], w: 4, depth: 1.5, meander: 4 },
    { type: 'river', name: 'Tigris', path: [[-120, -30], [-70, 6], [-20, 40], [28, 72]], w: 3, depth: 1.2, meander: 5 },
    { type: 'river', name: 'Indus', path: [[330, 178], [346, 120], [366, 52], [392, -10]], w: 4, depth: 1.5, meander: 5 },
    { type: 'woods', at: [-130, -60], r: [24, 14] }, { type: 'woods', at: [300, 10], r: [30, 18] }, { type: 'woods', at: [30, -110], r: [24, 12] },
    { type: 'farms', rect: [-236, 100, 30, 110, 0], cell: [10, 8] }, { type: 'farms', rect: [-80, 20, 120, 40, 10], cell: [12, 9] },
  ],
};
const PERSEPOLIS = [99, 76];

// ====================================================================================== shared look of the plates
const nightVeil = [0.035, 0.05, 0.16];

// ---------------------------------------------------------------------------------- stage emp
const E_POS = [[-60, -60], [-140, -20], [-200, 70], [-236, 110], [-20, -20], [30, 20], [60, 100], [140, 40], [190, -40], [250, 10], [330, -30], [360, 80], [40, -100], [200, -140]];
const emp = {
  world: empWorld,
  blocks: Object.fromEntries(E_POS.map((p, k) => [`E${k}`, { ...PER, kind: 'infantry', x: p[0], z: p[1], heading: 90, len: 26, dep: 11, height: 5, hidden: true, bannerScale: 1.8 }])),
  moves: [{ blocks: E_POS.map((_, k) => `E${k}`), at: 'l02.Still,', dur: 0.6, stagger: 0.14, appear: true, appearFrom: 30 }],
  regions: [{ at: 'l02.Xerxes,', until: 'l02>', poly: EMP_REGION, color: [0.80, 0.12, 0.12], alpha: 0.30, step: 16, fadeIn: 0.5, fadeOut: 0.7, sweep: { at: 'l02.empire', until: 'l02.India.>' } }],
  arrows: [],
  labels: [
    L('l02.Xerxes,', 'l02.King', 'XERXES', { pos: PERSEPOLIS, y: 14, team: 'rome', dy: -0.22, dx: -0.12, big: true }),
    L('l02.King', 'l02.His', 'KING OF KINGS OF PERSIA', { pos: PERSEPOLIS, y: 14, team: 'rome', dy: -0.22, dx: -0.12 }),
    L('l02.Egypt', 'l02.Ancient', 'EGYPT', { pos: [-236, 90], y: 6, dy: -0.2, dx: 0.0, big: true, team: 'rome' }),
    L('l02.India.', 'l02.Ancient', 'INDIA', { pos: [388, 40], y: 6, dy: -0.2, dx: 0.0, big: true, team: 'rome' }),
    L('l02.Ancient', 'l02.Modern', 'THE PERSIAN EMPIRE', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l02.Still,', 'l02>', 'STILL: A LOT.', { screen: [0.5, 0.1], big: true, size: 1.5, team: 'rome' }),
  ],
  icons: [
    I('l02.Xerxes,', 'l02.His', 'crown', { pos: PERSEPOLIS, y: 4, size: 38, anim: 'bounce' }),
    I('l02.Kings', 'l02.His', 'crown', { pos: [PERSEPOLIS[0] - 30, PERSEPOLIS[1] + 10], y: 4, size: 30, anim: 'bounce' }),
    I('l02.Persia.', 'l02.His', 'crown', { pos: [PERSEPOLIS[0] + 30, PERSEPOLIS[1] + 10], y: 4, size: 30, anim: 'bounce' }),
    I('l02.Modern', 'l02.Still,', 'book', { screen: [0.17, 0.62], size: 0.17, anim: 'bounce' }),
    I('l02.Ancient', 'l02.Modern', 'book', { screen: [0.17, 0.62], size: 0.17, anim: 'sway' }),
  ],
  nums: [
    { at: 'l02.million', until: 'l02.Modern', screen: [0.5, 0.95], keys: [['l02.million', 0], ['l02.strong.', 2000000]], plusAt: 'l02.strong.', tag: 'ANCIENT WRITERS SAID', suffix: 'SOLDIERS', col: [0.40, 0.05, 0.06], step: 100000 },
    { at: 'l02.Modern', until: 'l02>', screen: [0.5, 0.95], keys: [['l02.Modern', 2000000], ['l02.100', 100000]], plusAt: 'l02.or', tag: 'MODERN HISTORIANS THINK', suffix: 'SOLDIERS', col: [0.06, 0.15, 0.42], step: 100000 },
  ],
  camera: [
    { at: 17.4, target: [20, -10], width: 980, pitch: 58, yaw: 0, mm: 35 },
    { at: 'l02.Xerxes,', target: [60, 20], width: 560, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.His', target: [80, 30], width: 760, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.Egypt', target: [30, 40], width: 900, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.Ancient', target: [40, 10], width: 940, pitch: 60, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.Still,', target: [40, 10], width: 800, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 34.4, target: [40, 10], width: 740, pitch: 52, yaw: 0, mm: 35, ease: 'linear' },
  ],
};

// ---------------------------------------------------------------------------------- stage aeg
const A_N = 16;
const A_ID = Array.from({ length: A_N }, (_, k) => `A${k}`);
const aStart = (k) => [100 + (k % 4) * 15, -92 + Math.floor(k / 4) * 14];
const aEnd = (k) => [-88 + ((k % 2) * 2 - 1) * 7, -62 - Math.floor(k / 2) * 9];
const aMove = (k, t0, dur, pts) => ({ block: `A${k}`, at: t0, dur, path: pts(k), smooth: true });
const aegBlocks = {
  ...Object.fromEntries(A_ID.map((id, k) => [id, { ...PER, kind: 'infantry', x: aStart(k)[0], z: aStart(k)[1], heading: 270, len: 14, dep: 7, height: 4, hidden: true, bannerScale: 1.2 }])),
  G: { ...GRE, kind: 'infantry', x: THERMO[0], z: THERMO[1], heading: 0, len: 9, dep: 5, height: 4, hidden: true, bannerScale: 1.2 },
  plR: { ...PER, kind: 'infantry', x: -46, z: -22, heading: 180, len: 22, dep: 9, height: 4, hidden: true, bannerScale: 1.4 },
  plG: { ...GRE, kind: 'infantry', x: -50, z: 28, heading: 0, len: 22, dep: 9, height: 4, hidden: true, bannerScale: 1.4 },
};
const cityLine = (a, b, bend = 5) => { const [x0, z0] = a, [x1, z1] = b; const mx = (x0 + x1) / 2, mz = (z0 + z1) / 2; const dx = x1 - x0, dz = z1 - z0; const l = Math.hypot(dx, dz) || 1; return [a, [mx - dz / l * bend, mz + dx / l * bend], b]; };
const shrink = (a, b, k = 0.2) => [[a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k], [b[0] - (b[0] - a[0]) * k, b[1] - (b[1] - a[1]) * k]];
const PAIRS = [['athens', 'sparta'], ['corinth', 'tegea'], ['athens', 'corinth'], ['sparta', 'tegea']];
const squab = [];
PAIRS.forEach(([a, b], i) => { const [p, q] = shrink(AEG_CITIES[a], AEG_CITIES[b], 0.16);
  squab.push({ at: `l03.fighting+${0.0 + i * 0.12}`, dur: 0.5, ease: 'out', team: 'ink', width: 1.5, path: cityLine(p, q, 4), lift: 3, hide: 'l03.This', head: true });
  squab.push({ at: `l03.fighting+${0.2 + i * 0.12}`, dur: 0.5, ease: 'out', team: 'ink', width: 1.5, path: cityLine(q, p, 4), lift: 3, hide: 'l03.This', head: true }); });
const teamUp = Object.entries(AEG_CITIES).map(([name, p], i) => ({ at: `l03.teamed+${i * 0.1}`, dur: 0.9, ease: 'inOut', team: 'carthage', width: 2.2, path: [p, [(p[0] + THERMO[0]) / 2 + (i % 2 ? 6 : -6), (p[1] + THERMO[1]) / 2], THERMO], lift: 4, hide: 'l04' }));

const aeg = {
  world: aegWorld,
  blocks: aegBlocks,
  moves: [
    // hook: the huge Persian army floods across the Hellespont into Greece; a tiny Greek block waits at the pass
    { blocks: A_ID, at: 'l00.biggest', dur: 0.6, stagger: 0.13, appear: true, appearFrom: 26 },
    ...A_ID.map((_, k) => aMove(k, `l00.marched+${k * 0.11}`, 3.4, () => [[76, -104], [40, -126], [-10, -122], [-56, -104], [-76, -82], aEnd(k)])),
    { block: 'G', at: 'l00.few', dur: 0.7, appear: true, appearFrom: 20 },
    { block: 'G', at: 'l00.stop', dur: 0.5, to: { scale: 1.3 }, ease: 'out' }, { block: 'G', at: 'l00.stop+0.5', dur: 0.5, to: { scale: 1 }, ease: 'inOut' },
    { blocks: A_ID, at: 12.4, dur: 0.5, vanish: true },
    // the army comes back to march south to Athens (l15)
    { blocks: A_ID, at: 'l15.marched-0.6', dur: 0.5, stagger: 0.04, appear: true, appearFrom: 14 },
    ...A_ID.map((_, k) => aMove(k, `l15.marched+${k * 0.06}`, 2.6, () => { const e = aEnd(k); return [e, [-72, -40], [-58, -14], [-40, 2], [-26 + (k % 4) * 3, 8 + Math.floor(k / 4) * 2]]; })),
    // Plataea, the next year
    { block: 'plR', at: 'l16.In', dur: 0.7, appear: true, appearFrom: 18 }, { block: 'plG', at: 'l16.In', dur: 0.7, appear: true, appearFrom: 18 },
    { block: 'plG', at: 'l16.beaten', dur: 1.0, to: { z: -2 }, ease: 'inOut' },
    { block: 'plR', at: 'l16.beaten', dur: 1.4, to: { z: -70 }, ease: 'in' }, { block: 'plR', at: 'l16.beaten', dur: 1.4, to: { alpha: 0.12 }, ease: 'in' },
  ],
  arrows: [
    { at: 'l00.marched', until: 'l00.and', ease: 'inOut', team: 'rome', style: 'dash', width: 3.0, path: [[76, -104], [40, -126], [-10, -122], [-56, -104], [-76, -82], [-86, -58]], lift: 4, head: true, hide: 'l00.few' },
    ...squab, ...teamUp,
    { at: 'l15.marched', until: 'l15.Athens', ease: 'inOut', team: 'rome', style: 'dash', width: 2.8, path: [[-84, -58], [-72, -40], [-58, -14], [-40, 2], [-22, 12]], lift: 4, head: true, hide: 'l15.Which' },
    { id: 'blueship1', at: 'l16.smashed', dur: 1.2, ease: 'out', team: 'carthage', width: 1.6, path: [[-52, 26], [-40, 20], [-28, 14]], lift: 3, hide: 'l16.the' },
    { id: 'blueship2', at: 'l16.smashed+0.15', dur: 1.2, ease: 'out', team: 'carthage', width: 1.6, path: [[-50, 14], [-38, 12], [-26, 8]], lift: 3, hide: 'l16.the' },
    { id: 'blueship3', at: 'l16.smashed+0.3', dur: 1.2, ease: 'out', team: 'carthage', width: 1.6, path: [[-50, 34], [-38, 28], [-24, 22]], lift: 3, hide: 'l16.the' },
    { at: 'l16.beaten', dur: 1.2, ease: 'out', team: 'rome', style: 'dash', width: 2.2, path: [[-46, -16], [-46, -40], [-44, -64]], lift: 4, head: true, hide: 'l17' },
    { at: 'l16.beaten', dur: 1.0, ease: 'out', team: 'carthage', width: 2.4, path: [[-50, 20], [-50, 4]], lift: 4, head: true, hide: 'l17' },
  ],
  labels: [
    // ---- hook
    { at: 'l00.480', until: 'l00.the', text: '480 BC', screen: [0.5, 0.16], style: 'text', big: true, size: 1.9, track: 0.16, weight: 800 },
    L('l00.biggest', 'l00.marched', 'THE BIGGEST ARMY EVER SEEN', { block: 'A5', team: 'rome', dy: -0.17, big: true }),
    L('l00.marched', 'l00.and', 'MARCHING INTO GREECE', { pos: [-20, -118], y: 4, team: 'rome', dy: -0.12, big: true }),
    L('l00.few', 'l00.stop', 'A FEW THOUSAND GREEKS', { block: 'G', team: 'carthage', dy: -0.2, big: true }),
    L('l00.stop', 'l00.at', 'STOP THEM!', { block: 'G', team: 'carthage', dy: -0.2, big: true }),
    L('l00.gap', 12.9, 'A GAP IN THE MOUNTAINS', { block: 'G', team: 'carthage', dy: -0.22, big: true }),
    L('l00.marched', 'l00.and', 'GREECE', { pos: [-110, -10], y: 4, leader: false, size: 1.2 }),
    L('l00.biggest', 'l00.marched', 'PERSIA', { pos: [150, -40], y: 4, leader: false, size: 1.2, team: 'rome' }),
    // ---- the cities
    L('l03.Greek', 'l03.were', 'THE GREEK CITIES', { screen: [0.5, 0.1], big: true, team: 'carthage' }),
    L('l03.fighting', 'l03.This', 'FIGHTING EACH OTHER', { screen: [0.5, 0.1], big: true, team: 'ink' }),
    L('l03.teamed', 'l04', 'SOME TEAMED UP', { screen: [0.5, 0.1], big: true, team: 'carthage' }),
    L('l03.Greek', 'l04', 'ATHENS', { pos: AEG_CITIES.athens, y: 10, dy: -0.12, dx: 0.1, size: 0.85 }),
    L('l03.Greek+0.1', 'l04', 'CORINTH', { pos: AEG_CITIES.corinth, y: 10, dy: -0.12, dx: 0.12, size: 0.85 }),
    L('l03.Greek+0.2', 'l04', 'SPARTA', { pos: AEG_CITIES.sparta, y: 10, dy: -0.1, dx: 0.1, size: 0.85 }),
    L('l03.Greek+0.3', 'l04', 'TEGEA', { pos: AEG_CITIES.tegea, y: 10, dy: -0.1, dx: -0.1, size: 0.85 }),
    L('l03.teamed', 'l04', 'THERMOPYLAE', { pos: THERMO, y: 6, dy: -0.15, dx: -0.12, size: 0.85, team: 'carthage' }),
    // ---- Athens burns, Salamis, Plataea
    L('l15.Persians', 'l15.They', 'THE PERSIANS WIN', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l15.marched', 'l15.burned', 'MARCHING SOUTH', { pos: [-50, -6], y: 4, team: 'rome', dy: -0.14, dx: -0.2, big: true }),
    L('l15.burned', 'l15.Which', 'ATHENS BURNS', { pos: AEG_CITIES.athens, y: 10, team: 'rome', dy: -0.2, dx: 0.12, big: true }),
    L('l15.end', 'l16', 'THE END?', { screen: [0.5, 0.1], big: true, size: 1.4 }),
    L('l16.those', 'l16.A', 'THOSE DAYS BOUGHT TIME', { screen: [0.5, 0.1], big: true, team: 'carthage' }),
    L('l16.A', 'l16.the#1', 'A FEW WEEKS LATER', { screen: [0.5, 0.1], big: true }),
    L('l16.Greek', 'l16.smashed', 'GREEK NAVY', { pos: [-46, 26], y: 8, team: 'carthage', dy: -0.18, dx: -0.14, big: true }),
    L('l16.smashed', 'l16.In', 'SALAMIS: THE PERSIAN FLEET IS SMASHED', { screen: [0.5, 0.1], big: true, size: 0.85, team: 'carthage' }),
    L('l16.In', 'l16.the#4', 'THE NEXT YEAR', { screen: [0.5, 0.1], big: true }),
    L('l16.the#4', 'l17', 'PLATAEA, 479 BC', { pos: [-48, 4], y: 8, dy: -0.2, dx: 0.14, big: true }),
    L('l16.beaten', 'l16.for', 'PERSIANS BEATEN ON LAND', { screen: [0.5, 0.1], big: true, team: 'carthage' }),
    L('l16.for', 'l17', 'FOR GOOD', { screen: [0.5, 0.1], big: true, size: 1.5, team: 'carthage' }),
  ],
  icons: [
    I('l00.few', 'l00.at', 'helmet', { block: 'G', team: 'carthage', size: 14, dy: -0.03, anim: 'bounce' }),
    I('l00.gap', 12.9, 'peak', { pos: [-98, -34], y: 6, size: 16, anim: 'none' }),
    I('l00.gap+0.2', 12.9, 'wave', { pos: [-60, -36], y: 3, size: 10, anim: 'none' }),
    I('l00.480', 'l00.the', 'laurel', { screen: [0.5, 0.33], size: 0.14, anim: 'bounce' }),
    ...Object.entries(AEG_CITIES).map(([name, p], i) => I(`l03.Greek+${0.1 * i}`, 'l03.teamed', 'city', { pos: p, y: 2, size: 20, anim: 'bounce', team: 'neutral' })),
    ...Object.entries(AEG_CITIES).map(([name, p], i) => I(`l03.teamed+${0.1 * i}`, 'l04', 'city', { pos: p, y: 2, size: 20, anim: 'bounce', team: 'carthage' })),
    I('l03.fighting', 'l03.This', 'swords', { pos: [(AEG_CITIES.athens[0] + AEG_CITIES.sparta[0]) / 2, (AEG_CITIES.athens[1] + AEG_CITIES.sparta[1]) / 2], y: 6, size: 12 }),
    I('l03.fighting+0.2', 'l03.This', 'swords', { pos: [(AEG_CITIES.corinth[0] + AEG_CITIES.tegea[0]) / 2, (AEG_CITIES.corinth[1] + AEG_CITIES.tegea[1]) / 2], y: 6, size: 12 }),
    I('l03.teamed', 'l04', 'flag', { pos: THERMO, y: 6, size: 14, team: 'carthage' }),
    I('l15.burned', 'l16.But', 'burn', { pos: [AEG_CITIES.athens[0] - 6, AEG_CITIES.athens[1]], y: 6, size: 24 }),
    I('l15.burned+0.2', 'l16.But', 'burn', { pos: [AEG_CITIES.athens[0] + 6, AEG_CITIES.athens[1] + 2], y: 6, size: 20 }),
    I('l15.burned+0.4', 'l16.But', 'burn', { pos: [AEG_CITIES.athens[0], AEG_CITIES.athens[1] - 4], y: 6, size: 18 }),
    I('l15.end', 'l16', 'question', { screen: [0.5, 0.6], size: 0.3, anim: 'bounce' }),
    I('l16.those', 'l16.A', 'hourglass', { screen: [0.5, 0.58], size: 0.3, anim: 'bounce' }),
    ...[[-44, 18], [-38, 26], [-50, 30], [-56, 22]].map((p, i) => I(`l16.Greek+${0.08 * i}`, 'l16.In', 'ship', { pos: p, y: 2, size: 14, team: 'carthage', anim: 'bounce' })),
    ...[[-24, 10], [-18, 18], [-26, 26], [-14, 28], [-30, 4], [-12, 8]].map((p, i) => I(`l16.weeks+${0.1 * i}`, 'l16.In', 'ship', { pos: p, y: 2, size: 14, team: 'rome', anim: 'none', fallAt: `l16.smashed+${0.25 + 0.2 * i}`, fallDur: 0.8 })),
    ...[[-30, 14], [-22, 22], [-20, 6], [-28, 24]].map((p, i) => I(`l16.smashed+${0.3 + 0.15 * i}`, 'l16.In', 'burst', { pos: p, y: 8, size: 18, anim: 'bounce' })),
    I('l16.beaten', 'l17', 'laurel', { pos: [-50, 12], y: 8, size: 20, anim: 'bounce' }),
  ],
  camera: [
    { at: 0, target: [70, -64], width: 400, pitch: 52, yaw: 6, mm: 35 },
    { at: 'l00.biggest', target: [100, -70], width: 250, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.marched', target: [14, -84], width: 360, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.and', target: [-50, -62], width: 260, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.stop', target: [-80, -46], width: 160, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.gap', target: [-82, -36], width: 100, pitch: 44, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 12.9, target: [-82, -36], width: 90, pitch: 42, yaw: 14, mm: 35, ease: 'linear' },
    { at: 34.0, target: [-60, 8], width: 330, pitch: 60, yaw: 0, mm: 35, cut: true },
    { at: 'l03.Greek', target: [-58, 10], width: 270, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.teamed', target: [-62, -2], width: 250, pitch: 56, yaw: 4, mm: 35, ease: 'inOut' },
    { at: 'l04', target: [-70, -12], width: 230, pitch: 54, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 133.7, target: [-70, -22], width: 230, pitch: 52, yaw: 6, mm: 35, cut: true },
    { at: 'l15.marched', target: [-56, -12], width: 210, pitch: 52, yaw: 4, mm: 35, ease: 'inOut' },
    { at: 'l15.burned', target: [-34, 10], width: 150, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l15.Which', target: [-40, 4], width: 200, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.A', target: [-40, 14], width: 150, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.Greek', target: [-34, 18], width: 120, pitch: 40, yaw: -10, mm: 35, ease: 'inOut' },
    { at: 'l16.smashed', target: [-34, 16], width: 100, pitch: 36, yaw: 12, mm: 35, ease: 'inOut' },
    { at: 'l16.In', target: [-46, 4], width: 150, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.beaten', target: [-48, -18], width: 140, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 150.2, target: [-48, -20], width: 150, pitch: 48, yaw: 0, mm: 35, ease: 'linear' },
  ],
};

// ====================================================================================== the pass: blocks and choreography
const PX = [-75, -45, -15, 15, 45, 75];
const P_ID = [...PX.map((_, i) => `P${i}`), ...PX.map((_, i) => `P${6 + i}`)];
const pBlocks = Object.fromEntries(P_ID.map((id, k) => [id, { ...PER, kind: 'infantry', x: PX[k % 6], z: k < 6 ? -216 : -198, heading: 180, len: 22, dep: 9, height: 4, hidden: true, bannerScale: 1.0 }]));
const Q_ID = ['Q0', 'Q1', 'Q2', 'Q3'];
const SLOT = [24, 35, 46]; // the shield wall: three blocks take turns at the front
const HIT = 14.6;          // z where a Persian block meets the front of the wall
const wave = (id, t, jit = 0) => [
  { block: id, at: t, dur: 3.3, to: { z: HIT }, ease: 'inQuad' }, { block: id, at: t, dur: 3.3, to: { x: CX + jit }, ease: 'inOut' },
  { block: id, at: t + 3.3, dur: 0.5, to: { z: -34 }, ease: 'out' }, { block: id, at: t + 3.3, dur: 0.18, to: { lift: 2 }, ease: 'out' }, { block: id, at: t + 3.48, dur: 0.3, to: { lift: 0 }, ease: 'in' },
  { block: id, at: t + 3.8, dur: 0.7, vanish: true },
];
const waveAt = (id, line, word, add, jit) => wave(id, wordT(line, word) + add, jit);
const WAVE_JIT = [-6, 6, -2, 4, -5, 2, -4, 5, 0, 6, -6, 3];
// the shield wall rotates: front -> back, the others step forward
const rot = (t, who) => { const [a, b, c] = who; // a is at the front now, b second, c third
  return [
    { block: a, at: t, dur: 0.35, to: { x: CX + 10 }, ease: 'inOut' }, { block: a, at: t + 0.3, dur: 0.7, to: { z: SLOT[2] }, ease: 'inOut' }, { block: a, at: t + 0.95, dur: 0.35, to: { x: CX }, ease: 'inOut' },
    { block: b, at: t + 0.25, dur: 0.8, to: { z: SLOT[0] }, ease: 'inOut' }, { block: c, at: t + 0.25, dur: 0.8, to: { z: SLOT[1] }, ease: 'inOut' }];
};
const T_ROT1 = wordT('l08', 'took') + 0.05;

const main = {
  world: passWorld,
  blocks: {
    ...pBlocks,
    horde: { ...PER, kind: 'infantry', x: CX, z: -250, heading: 180, len: 220, dep: 30, grid: { cols: 9, ranks: 2, gap: 3 }, hidden: true, height: 4, bannerScale: 1.0 },
    imm: { ...PER, kind: 'elite', x: CX, z: -80, heading: 180, len: 24, dep: 10, height: 4.4, hidden: true, bannerScale: 1.3 },
    imm2: { ...PER, kind: 'elite', x: -52, z: -196, heading: 200, len: 24, dep: 10, height: 4.4, hidden: true, bannerScale: 1.3 },
    ...Object.fromEntries(Q_ID.map((id, k) => [id, { ...PER, kind: 'infantry', x: CX + (k % 2 ? 3 : -3), z: k < 2 ? -50 - k * 12 : 150 + (k - 2) * 12, heading: k < 2 ? 180 : 0, len: 22, dep: 9, height: 4, hidden: true, bannerScale: 1.0 }])),
    D0: { ...PER, kind: 'infantry', x: -60, z: -150, heading: 180, len: 36, dep: 12, hidden: true, height: 4 }, D1: { ...PER, kind: 'infantry', x: -20, z: -150, heading: 180, len: 36, dep: 12, hidden: true, height: 4 },
    D2: { ...PER, kind: 'infantry', x: 20, z: -150, heading: 180, len: 36, dep: 12, hidden: true, height: 4 }, D3: { ...PER, kind: 'infantry', x: 60, z: -150, heading: 180, len: 36, dep: 12, hidden: true, height: 4 },
    camp: { ...GRE, kind: 'infantry', x: CX - 2, z: 96, heading: 0, len: 44, dep: 22, count: 7000, hidden: true, height: 4, bannerScale: 1.5 },
    w1: { ...GRE, kind: 'elite', x: CX, z: SLOT[0], heading: 0, len: 22, dep: 9, count: 300, hidden: true, height: 4.4, bannerScale: 1.3 },
    w2: { ...GRE, kind: 'infantry', x: CX, z: SLOT[1], heading: 0, len: 22, dep: 9, hidden: true, height: 4, bannerScale: 1.0 },
    w3: { ...GRE, kind: 'infantry', x: CX, z: SLOT[2], heading: 0, len: 22, dep: 9, hidden: true, height: 4, bannerScale: 1.0 },
    thesp: { ...GRE, kind: 'infantry', x: CX + 1, z: 58, heading: 0, len: 22, dep: 9, count: 700, hidden: true, height: 4, bannerScale: 1.0 },
  },

  moves: [
    // ---- l04: a giant army squeezed through a narrow road (four big blocks queue up and pass one at a time)
    { blocks: ['D0', 'D1', 'D2', 'D3'], at: 'l04.giant', dur: 0.6, stagger: 0.14, appear: true, appearFrom: 24 },
    ...['D0', 'D1', 'D2', 'D3'].flatMap((id, k) => [
      { block: id, at: 'l04.squeeze', dur: 1.5, to: { z: -52 - k * 15 }, ease: 'inOut' }, { block: id, at: 'l04.squeeze', dur: 1.5, to: { x: CX, len: 24 }, ease: 'inOut' }]),
    { block: 'D0', at: 'l04.through', dur: 1.0, to: { z: 6 }, ease: 'inOut' }, { block: 'D1', at: 'l04.little', dur: 0.8, to: { z: -52 }, ease: 'inOut' },
    { blocks: ['D0', 'D1', 'D2', 'D3'], at: 'l04.time.>', dur: 0.4, vanish: true },
    // ---- l05: the Greeks take the pass
    { blocks: ['camp', 'w2', 'w3'], at: 'l05.Holding', dur: 0.7, stagger: 0.15, appear: true, appearFrom: 22 },
    { block: 'w1', at: 'l05.Leonidas', dur: 0.7, appear: true, appearFrom: 22 },
    { block: 'w1', at: 'l05.300', dur: 0.25, to: { scale: 1.25 }, ease: 'out' }, { block: 'w1', at: 'l05.300+0.25', dur: 0.5, to: { scale: 1 }, ease: 'inOut' },
    // ---- l06: Xerxes waits; the Greeks do not run
    { group: 'horde', at: 'l06.Xerxes', dur: 0.7, stagger: 0.07, appear: true, appearFrom: 20 },
    { blocks: P_ID, at: 'l06.Xerxes+0.5', dur: 0.6, stagger: 0.09, appear: true, appearFrom: 20 },
    { block: 'w1', at: 'l06.not', dur: 0.25, to: { scale: 1.2 }, ease: 'out' }, { block: 'w1', at: 'l06.not+0.25', dur: 0.5, to: { scale: 1 }, ease: 'inOut' },
    // ---- l08: wave after wave into the funnel; the wall rotates
    ...[0, 1, 2, 3, 4, 5].flatMap((k) => waveAt(`P${k}`, 'l08', 'wave', k * 0.6, WAVE_JIT[k])),
    ...rot(T_ROT1, ['w1', 'w2', 'w3']), ...rot(T_ROT1 + 1.6, ['w2', 'w3', 'w1']),
    // ---- l09: the Immortals charge and bounce off
    ...waveAt('P6', 'l09', 'Even', 0, WAVE_JIT[6]), ...waveAt('P7', 'l09', 'Even', 0.9, WAVE_JIT[7]),
    { block: 'imm', at: 'l09.elite', dur: 0.6, appear: true, appearFrom: 22 },
    { block: 'imm', at: 'l09.could', dur: 0.75, to: { z: HIT }, ease: 'inQuad' }, { block: 'imm', at: 'l09.could', dur: 0.75, to: { x: CX }, ease: 'inOut' },
    { block: 'imm', at: 'l09.through', dur: 0.5, to: { z: -50 }, ease: 'out' }, { block: 'imm', at: 'l09.through', dur: 0.2, to: { lift: 2.4 }, ease: 'out' }, { block: 'imm', at: 'l09.through+0.2', dur: 0.4, to: { lift: 0 }, ease: 'in' },
    { block: 'imm', at: 'l09.Herodotus', dur: 0.8, vanish: true },
    // ---- l10: two days, the pass held
    ...waveAt('P8', 'l10', 'Two', 0, WAVE_JIT[8]), ...waveAt('P9', 'l10', 'Two', 0.35, WAVE_JIT[9]), ...waveAt('P10', 'l10', 'Two', 0.7, WAVE_JIT[10]), ...waveAt('P11', 'l10', 'Two', 1.05, WAVE_JIT[11]),
    // ---- l12: the Immortals climb the hidden path by night (they arrive behind the Greeks as Leonidas learns it)
    { block: 'imm2', at: 'l12.That', dur: 0.4, appear: true, appearFrom: 12 },
    { block: 'imm2', at: 'l12.That+0.45', dur: 5.1, path: [[-52, -196], [-118, -176], [-182, -124], [-206, -50], [-196, 30], [-150, 100], [-86, 142], [-30, 140], [-8, 128]] },
    // ---- l13: surrounded; most Greeks leave
    { blocks: ['camp', 'w2'], at: 'l13.sent', dur: 3.2, to: { z: 270 }, ease: 'in' }, { blocks: ['camp', 'w2'], at: 'l13.sent+2.4', dur: 0.8, vanish: true },
    { block: 'thesp', at: 'l13.700', dur: 0.7, appear: true, appearFrom: 20 },
    { block: 'w1', at: 'l13.stayed', dur: 0.25, to: { scale: 1.2 }, ease: 'out' }, { block: 'w1', at: 'l13.stayed+0.25', dur: 0.5, to: { scale: 1 }, ease: 'inOut' },
    { block: 'w3', at: 'l13.others', dur: 0.25, to: { scale: 1.18 }, ease: 'out' }, { block: 'w3', at: 'l13.others+0.25', dur: 0.5, to: { scale: 1 }, ease: 'inOut' },
    // ---- l14: the third day, surrounded on all sides, they fight to the end
    { blocks: Q_ID, at: 'l14.third', dur: 0.6, stagger: 0.12, appear: true, appearFrom: 18 },
    { block: 'Q0', at: 'l14.surrounded', dur: 1.8, to: { z: -2 }, ease: 'inOut' }, { block: 'Q1', at: 'l14.surrounded', dur: 1.8, to: { z: -14 }, ease: 'inOut' },
    { block: 'Q2', at: 'l14.surrounded', dur: 1.8, to: { z: 78 }, ease: 'inOut' }, { block: 'Q3', at: 'l14.surrounded', dur: 1.8, to: { z: 92 }, ease: 'inOut' },
    { block: 'imm2', at: 'l14.surrounded', dur: 1.6, to: { x: CX, z: 100, heading: 0 }, ease: 'inOut' },
    { blocks: ['w1', 'w3', 'thesp'], at: 'l14.fought', dur: 2.6, stagger: 0.3, fadeTo: 1, alphaTo: 0.06, sinkTo: 0.95 },
    // ---- the Persians stay; the pass falls quiet
    { blocks: [...Q_ID, 'imm2', 'horde'], at: 'l15.So', dur: 1.2, vanish: true },
  ],

  arrows: [
    // l04: the road is narrow
    { at: 'l04.narrow', dur: 0.7, ease: 'out', team: 'cream', width: 2.2, path: [[-56, 0], [-24, 0]], lift: 5, hide: 'l04.giant', head: true },
    { at: 'l04.narrow', dur: 0.7, ease: 'out', team: 'cream', width: 2.2, path: [[50, 0], [16, 0]], lift: 5, hide: 'l04.giant', head: true },
    // l06: expecting the Greeks to run away (they do not)
    { id: 'runaway', at: 'l06.run', dur: 0.9, ease: 'out', team: 'carthage', width: 3, style: 'dash', path: [[CX, 28], [CX - 6, 70], [CX - 16, 130]], lift: 5, hide: 'l06.did', head: true },
    // l08: the wall rotates
    { at: 'l08.took', dur: 0.8, ease: 'out', team: 'gold', width: 2.2, path: [[12, 20], [18, 34], [14, 50], [-6, 56], [-24, 44], [-22, 28], [-12, 18]], lift: 4, hide: 'l09.Even', head: true },
    // l09: the Immortals charge
    { at: 'l09.could', dur: 0.75, ease: 'in', team: 'gold', width: 4, path: [[CX, -70], [CX, HIT - 6]], lift: 5, hide: 'l09.through+0.6', head: true },
    // l11: Ephialtes sells the hidden mountain path (dotted, drawn around behind the Greeks), then the Immortals follow it by night
    { id: 'hidden', at: 'l11.hidden', until: 'l11.Greeks.>', ease: 'inOut', team: 'rome', style: 'dash', width: 2.8, path: [[-52, -196], [-118, -176], [-182, -124], [-206, -50], [-196, 30], [-150, 100], [-86, 142], [-30, 140], [-8, 128]], lift: 7, hide: 'l13.sent' },
    // l13: surrounded
    { at: 'l13.surrounded', dur: 0.7, ease: 'out', team: 'rome', width: 4, path: [[CX, 130], [CX, 70]], lift: 5, hide: 'l14.On', head: true },
    { at: 'l13.surrounded+0.1', dur: 0.7, ease: 'out', team: 'rome', width: 4, path: [[CX, -60], [CX, -2]], lift: 5, hide: 'l14.On', head: true },
    { at: 'l13.sent', dur: 1.2, ease: 'out', team: 'carthage', width: 5, path: [[CX, 92], [CX - 6, 150], [CX - 20, 220]], lift: 5, hide: 'l13.He#2', head: true },
    // l14: closing in
    { at: 'l14.surrounded', dur: 0.8, ease: 'out', team: 'rome', width: 3.6, path: [[CX, -40], [CX, 6]], lift: 5, hide: 'l14.fought', head: true },
    { at: 'l14.surrounded', dur: 0.8, ease: 'out', team: 'rome', width: 3.6, path: [[CX, 130], [CX, 74]], lift: 5, hide: 'l14.fought', head: true },
    { at: 'l14.sides', dur: 0.8, ease: 'out', team: 'rome', width: 3.0, path: [[-36, 40], [-12, 40]], lift: 5, hide: 'l14.fought', head: true },
    { at: 'l14.sides', dur: 0.8, ease: 'out', team: 'rome', width: 3.0, path: [[26, 40], [6, 40]], lift: 5, hide: 'l14.fought', head: true },
  ],

  volleys: [
    ...[0, 1, 2, 3, 4, 5, 6, 7].map((k) => ({ at: `l07.arrows+${k * 0.4}`, dur: 1.0, from: [CX, -90, 38], to: [CX, 28, 12], n: 90, flight: 1.5, arc: 70, team: 'rome' })),
  ],

  labels: [
    // ---- l04 the place
    L('l04.Thermopylae,', 'l04.steep', 'THERMOPYLAE', { pos: [CX, 14], y: 4, dy: -0.2, big: true }),
    L('l04.steep', 'l04.the', 'STEEP MOUNTAINS', { pos: [-58, -10], y: 52, dy: -0.12, dx: 0.0, big: true }),
    L('l04.the', 'l04.A#1', 'THE SEA', { pos: [38, 10], y: 2, dy: -0.15, dx: 0.1, big: true }),
    L('l04.A#1', 'l04.so', 'A NARROW ROAD', { pos: [CX, 4], y: 2, dy: -0.18, big: true }),
    L('l04.giant', 'l04.could', 'A GIANT ARMY', { pos: [CX, -130], y: 2, dy: -0.12, big: true, team: 'rome' }),
    L('l04.squeeze', 'l04.little', 'SQUEEZE THROUGH', { pos: [CX, -60], y: 2, dy: -0.12, big: true, team: 'rome' }),
    L('l04.little', 'l05', 'A LITTLE AT A TIME', { screen: [0.5, 0.1], big: true }),
    // ---- l05 the Greeks
    L('l05.led', 'l05.and', 'KING LEONIDAS OF SPARTA', { block: 'w1', team: 'carthage', dy: -0.2, dx: -0.14 }),
    L('l05.300', 'l06', '300 SPARTANS', { block: 'w1', team: 'carthage', dy: -0.2, dx: 0.12, big: true }),
    // ---- l06 the wait
    L('l06.Xerxes', 'l06.waited', 'XERXES AND HIS ARMY', { block: 'horde', team: 'rome', dy: -0.14, big: true }),
    L('l06.waited', 'l06.expecting', 'WAITING', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l06.expecting', 'l06.They', 'WAITING FOR THE GREEKS TO RUN', { screen: [0.5, 0.1], big: true, team: 'rome', size: 0.85 }),
    L('l06.They', 'l07', 'THEY DID NOT', { block: 'w1', team: 'carthage', dy: -0.21, dx: -0.12, big: true }),
    // ---- l07 the shade
    L('l07.Herodotus', 'l07.Someone', 'HERODOTUS TELLS A STORY', { screen: [0.5, 0.1], big: true }),
    L('l07.arrows', 'l07.block', 'SO MANY ARROWS', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l07.block', 'l07.Spartan', 'THEY BLOCK OUT THE SUN', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l07.Spartan', 'l07.good', 'DIENEKES, A SPARTAN', { block: 'w1', team: 'carthage', dy: -0.21, dx: -0.14 }),
    { at: 'l07.good', until: 'l07>', text: 'GOOD.', screen: [0.5, 0.33], style: 'text', big: true, size: 2.2, track: 0.14, weight: 800 },
    L('l07.then', 'l07>', 'THEN WE WILL FIGHT IN THE SHADE.', { screen: [0.5, 0.5], big: true, size: 1.3, team: 'carthage' }),
    // ---- l08 the attack
    L('l08.fifth', 'l08.the#1', 'DAY FIVE: THE ATTACK', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l08.wave', 'l08.poured', 'WAVE AFTER WAVE', { pos: [CX, -110], y: 2, dy: -0.12, big: true, team: 'rome' }),
    L('l08.poured', 'l08.The#3', 'INTO THE PASS', { pos: [CX, -60], y: 2, dy: -0.12, big: true, team: 'rome' }),
    L('l08.wall', 'l08.took', 'A WALL OF SHIELDS', { block: 'w1', team: 'carthage', dy: -0.2, dx: -0.15, big: true }),
    L('l08.took', 'l09', 'TAKING TURNS AT THE FRONT', { screen: [0.5, 0.1], big: true, team: 'carthage', size: 0.9 }),
    // ---- l09 the Immortals and the throne
    L('l09.elite', 'l09.could', 'XERXES\' ELITE GUARD: THE IMMORTALS', { block: 'imm', team: 'rome', dy: -0.2, size: 0.9 }),
    L('l09.break', 'l09.Herodotus', 'THEY CANNOT BREAK THROUGH', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l09.Herodotus', 'l09.jumped', 'XERXES WATCHES', { pos: [-62, -62], y: 10, dy: -0.2, dx: 0.14, big: true, team: 'rome' }),
    L('l09.jumped', 'l09.afraid', 'HE JUMPS UP, THREE TIMES', { screen: [0.5, 0.1], big: true, team: 'rome', size: 0.95 }),
    L('l09.afraid', 'l10', 'AFRAID FOR HIS ARMY', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    // ---- l10
    { at: 'l10.Two', until: 'l10.the', text: 'TWO DAYS', screen: [0.5, 0.5], style: 'text', big: true, size: 2.2, track: 0.14, weight: 800 },
    L('l10.the', 'l11', 'THE PASS HELD', { screen: [0.5, 0.1], big: true, size: 1.5, team: 'carthage' }),
    // ---- l11 the secret path
    L('l11.Eff', 'l11.sold', 'EPHIALTES, A LOCAL MAN', { pos: [-76, -112], y: 6, dy: -0.18, dx: 0.0, big: true }),
    L('l11.sold', 'l11.hidden', 'HE SELLS A SECRET', { pos: [-76, -112], y: 6, dy: -0.18, dx: 0.0, big: true, team: 'rome' }),
    L('l11.hidden', 'l11.behind', 'A HIDDEN MOUNTAIN PATH', { pos: [-206, -50], y: 60, dy: -0.12, dx: 0.0, big: true, team: 'rome' }),
    L('l11.behind', 'l12', 'BEHIND THE GREEKS', { pos: [-8, 128], y: 6, dy: -0.2, dx: 0.14, big: true, team: 'rome' }),
    // ---- l12 the night climb
    L('l12.That', 'l12.the', 'THAT NIGHT', { screen: [0.5, 0.1], big: true, size: 1.4 }),
    L('l12.Immortals', 'l13', 'THE IMMORTALS CLIMB THE PATH', { block: 'imm2', team: 'rome', dy: -0.16, big: true }),
    // ---- l13 leaving
    L('l13.surrounded', 'l13.He#1', 'ABOUT TO BE SURROUNDED', { screen: [0.5, 0.1], big: true, team: 'carthage' }),
    L('l13.sent', 'l13.He#2', 'MOST OF THE GREEKS SENT AWAY', { block: 'camp', team: 'carthage', dy: -0.2, big: true, size: 0.9 }),
    L('l13.stayed', 'l13.with', 'LEONIDAS STAYS', { block: 'w1', team: 'carthage', dy: -0.2, dx: -0.14, big: true }),
    L('l13.Spartans', 'l13.and', '300 SPARTANS', { block: 'w1', team: 'carthage', dy: -0.2, dx: -0.14 }),
    L('l13.others', 'l13.like', 'A FEW OTHERS REFUSE TO LEAVE', { block: 'w3', team: 'carthage', dy: -0.2, dx: 0.17, size: 0.9 }),
    L('l13.Thespier', 'l14', 'THE TOWN OF THESPIAE', { block: 'thesp', team: 'carthage', dy: -0.2, dx: 0.17 }),
    // ---- l14 the end
    L('l14.third', 'l14.surrounded', 'THE THIRD DAY', { screen: [0.5, 0.1], big: true }),
    L('l14.surrounded', 'l14.they', 'SURROUNDED ON ALL SIDES', { screen: [0.5, 0.1], big: true, team: 'rome' }),
    L('l14.they', 'l15', 'THEY FOUGHT TO THE VERY END', { screen: [0.5, 0.1], big: true, team: 'carthage' }),
    // ---- l17 the stone
    L('l17.stone', 'l17.Go', 'A STONE AT THE PASS', { pos: [CX, 6], y: 8, dy: -0.26, big: true }),
  ],

  counters: [
    { at: 'l05.7', until: 'l06', block: 'camp', team: 'carthage', from: 0, to: 7000, countDur: 1.2, step: 100, suffix: 'GREEKS', dy: -0.2, dx: 0.0 },
    { at: 'l13.700', until: 'l14', block: 'thesp', team: 'carthage', from: 0, to: 700, countDur: 0.9, step: 10, suffix: 'THESPIANS', dy: -0.3, dx: 0.2 },
  ],

  icons: [
    // ---- l04 the place
    I('l04.steep', 'l04.the', 'peak', { pos: [-62, -10], y: 40, size: 30, anim: 'bounce' }),
    I('l04.the', 'l04.A#1', 'wave', { pos: [40, 12], y: 2, size: 16, anim: 'none' }),
    I('l04.giant', 'l04.could', 'helmet', { block: 'D1', team: 'rome', size: 16, anim: 'sway' }),
    // ---- l05
    I('l05.Holding', 'l05.led', 'shield', { block: 'camp', team: 'carthage', size: 16, dy: -0.04, anim: 'bounce' }),
    I('l05.Leonidas', 'l05.300', 'crown', { block: 'w1', size: 15, dx: 0.0, dy: -0.045, anim: 'bounce' }),
    I('l05.300', 'l06', 'helmet', { block: 'w1', team: 'carthage', size: 17, dx: 0.0, dy: -0.045, anim: 'sway' }),
    // ---- l06
    I('l06.waited', 'l06.They', 'calendar', { screen: [0.9, 0.3], size: 0.24, fill: '1,0.65,DAY,4', anim: 'none' }),
    I('l06.Xerxes', 'l06.They', 'tent', { pos: [-100, -246], y: 2, size: 22, team: 'rome' }), I('l06.Xerxes+0.2', 'l06.They', 'tent', { pos: [80, -246], y: 2, size: 22, team: 'rome' }),
    I('l06.expecting', 'l06.run', 'question', { block: 'w1', size: 18, dy: -0.06, anim: 'bounce' }),
    I('l06.run', 'l06.did', 'question', { block: 'w1', size: 18, dy: -0.06, anim: 'bounce' }),
    I('l06.did', 'l07', 'no', { pos: [CX - 8, 70], y: 8, size: 22, anim: 'bounce' }),
    I('l06.did', 'l07', 'check', { block: 'w1', size: 17, dx: 0.0, dy: -0.06, anim: 'bounce' }),
    // ---- l07
    I('l07.Herodotus', 'l07.Someone', 'book', { screen: [0.5, 0.45], size: 0.25, anim: 'bounce' }),
    I('l07.block', 'l07.Spartan', 'sundim', { screen: [0.12, 0.3], size: 0.26, anim: 'none' }),
    I('l07.Spartan', 'l07.good', 'helmet', { block: 'w1', team: 'carthage', size: 16, dy: -0.04, anim: 'sway' }),
    I('l07.shade.', 'l07>', 'cool', { block: 'w1', team: 'carthage', size: 20, dy: -0.04, anim: 'bounce' }),
    // ---- l08
    I('l08.fifth', 'l10.Two', 'calendar', { screen: [0.9, 0.3], size: 0.24, fill: '5,0,DAY', anim: 'none' }),
    I('l08.wall', 'l09', 'shield', { block: 'w1', team: 'carthage', size: 16, dx: -0.1, dy: 0.0, anim: 'bounce' }),
    I('l08.wall+0.15', 'l09', 'shield', { block: 'w2', team: 'carthage', size: 14, dx: 0.1, dy: 0.0, anim: 'bounce' }),
    ...[0, 1, 2, 3, 4, 5].map((k) => I(`l08.wave+${k * 0.6 + 3.3}`, `l08.wave+${k * 0.6 + 3.9}`, 'burst', { pos: [CX + WAVE_JIT[k] * 0.5, HIT + 4], y: 5, size: 16, anim: 'none' })),
    // ---- l09
    I('l09.through', 'l09.Herodotus', 'burst', { pos: [CX, HIT + 4], y: 5, size: 20, anim: 'none' }),
    I('l09.through+0.1', 'l09.Herodotus', 'no', { pos: [CX, HIT - 12], y: 12, size: 20, anim: 'bounce' }),
    I('l09.elite', 'l09.could', 'crown', { block: 'imm', size: 14, dy: -0.04, anim: 'bounce' }),
    I('l09.jumped', 'l10', 'throne', { pos: [-62, -62], y: 2, size: 34, anim: 'none' }),
    I('l09.afraid', 'l10', 'shout', { pos: [-62, -62], y: 26, size: 20, anim: 'bounce' }),
    // ---- l10
    I('l10.Two', 'l11', 'calendar', { screen: [0.9, 0.3], size: 0.24, fill: '5,0.95,DAY,6', anim: 'none' }),
    I('l10.the', 'l11', 'shield', { screen: [0.38, 0.62], size: 0.2, team: 'carthage', anim: 'bounce' }),
    I('l10.the', 'l11', 'check', { screen: [0.58, 0.62], size: 0.16, anim: 'bounce' }),
    // ---- l11
    I('l11.Eff', 'l12', 'bag', { pos: [-76, -112], y: 2, size: 22, anim: 'bounce' }),
    I('l11.sold', 'l11.hidden', 'question', { pos: [-60, -112], y: 8, size: 14, anim: 'bounce' }),
    I('l11.behind', 'l12', 'swords', { pos: [-8, 128], y: 12, size: 22, anim: 'bounce' }),
    // ---- l12 night
    I('l12.That', 'l13.He#1', 'moon', { screen: [0.88, 0.2], size: 0.2, anim: 'sway' }),
    // ---- l13
    I('l13.surrounded', 'l13.He#1', 'shout', { block: 'w1', size: 20, dy: -0.07, anim: 'bounce' }),
    I('l13.sent', 'l13.He#2', 'door', { block: 'camp', size: 16, dy: -0.04, anim: 'bounce' }),
    I('l13.stayed', 'l14', 'helmet', { block: 'w1', team: 'carthage', size: 18, dy: -0.04, anim: 'sway' }),
    I('l13.stayed', 'l14', 'heart', { block: 'w1', size: 12, dx: 0.04, dy: -0.04, anim: 'bounce' }),
    I('l13.refused', 'l14', 'no', { block: 'w3', size: 16, dx: 0.05, dy: -0.04, anim: 'bounce' }),
    I('l13.Thespier', 'l14', 'city', { block: 'thesp', team: 'carthage', size: 16, dx: 0.0, dy: -0.04, anim: 'bounce' }),
    // ---- l14
    I('l14.third', 'l15', 'calendar', { screen: [0.9, 0.3], size: 0.24, fill: '7,0,DAY', anim: 'none' }),
    I('l14.fought', 'l15', 'burst', { pos: [CX, 30], y: 8, size: 24, anim: 'bounce' }),
    I('l14.fought+0.4', 'l15', 'burst', { pos: [CX - 8, 48], y: 8, size: 20, anim: 'bounce' }),
    I('l14.very', 'l15', 'laurel', { pos: [CX, 34], y: 8, size: 28, anim: 'bounce' }),
    // ---- l17
    I('l17.stone', 'l17.Go', 'stone', { pos: [CX, 6], y: 0, size: 44, anim: 'none' }),
  ],

  dim: [
    { at: 'l07.block', until: 'l07.shade.>', alpha: 0.5, fadeIn: 1.0, fadeOut: 0.7 },
    { at: 'l12.That', until: 'l13.He#1', alpha: 0.6, color: nightVeil, stars: true, fadeIn: 0.9, fadeOut: 1.4 },
  ],
  light: [
    { at: 'l07.arrows', dur: 2.5, to: { cloud: 0.9 }, ease: 'inOut' }, { at: 'l08.On', dur: 1.4, to: { cloud: 0.28 }, ease: 'inOut' },
    { at: 'l12.That', dur: 1.2, to: { eve: 0.7, haze: 1.2 }, ease: 'inOut' },
    { at: 'l13.He#1', dur: 1.8, to: { eve: 0, haze: 1 }, ease: 'inOut' },
    { at: 'l15.So', dur: 4, to: { eve: 1, haze: 1.3 }, ease: 'inOut' },
    { at: 'l17.Today,', dur: 3, to: { eve: 0.8 }, ease: 'inOut' },
  ],

  camera: [
    // l04: the place (the cliff wall on the west, the sea on the east, the road squeezing between)
    { at: 12.9, target: [-10, -10], dist: 360, pitch: 26, yaw: 6, mm: 30 },
    { at: 17.2, target: [-10, -10], dist: 340, pitch: 26, yaw: -4, mm: 30, ease: 'linear' },
    { at: 'l04.They', target: [CX, -40], dist: 330, pitch: 30, yaw: 4, mm: 30, cut: true },
    { at: 'l04.Thermopylae,', target: [CX, -10], dist: 270, pitch: 28, yaw: 0, mm: 30, ease: 'inOut' },
    { at: 'l04.steep', target: [-52, -4], dist: 210, pitch: 17, yaw: 292, mm: 28, ease: 'inOut' },
    { at: 'l04.the', target: [30, 0], dist: 200, pitch: 22, yaw: 38, mm: 28, ease: 'inOut' },
    { at: 'l04.A#1', target: [CX, 0], dist: 220, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.giant', target: [CX, -70], dist: 340, pitch: 32, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.squeeze', target: [CX, -50], dist: 260, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.little', target: [CX, -14], dist: 200, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    // l05: the Greeks
    { at: 'l05.Holding', target: [CX, 50], dist: 200, pitch: 34, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 'l05.led', target: [CX, 28], dist: 120, pitch: 26, yaw: -8, mm: 35, ease: 'inOut' },
    { at: 'l05.300', target: [CX, 30], dist: 100, pitch: 30, yaw: 6, mm: 35, ease: 'inOut' },
    // l06: the wait
    { at: 'l06.Xerxes', target: [CX, -130], dist: 340, pitch: 22, yaw: 0, mm: 30, ease: 'inOut' },
    { at: 'l06.waited', target: [CX, -150], dist: 300, pitch: 28, yaw: 10, mm: 30, ease: 'inOut' },
    { at: 'l06.expecting', target: [CX, 20], dist: 190, pitch: 26, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l06.They', target: [CX, 40], dist: 150, pitch: 22, yaw: -6, mm: 35, ease: 'inOut' },
    // l07: the arrows block out the sun
    { at: 'l07.Herodotus', target: [CX, 30], dist: 200, pitch: 30, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l07.arrows', target: [CX, -20], dist: 230, pitch: 18, yaw: 0, mm: 30, ease: 'inOut' },
    { at: 'l07.Spartan', target: [CX, 28], dist: 110, pitch: 22, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l07.good', target: [CX, 30], dist: 90, pitch: 22, yaw: 0, mm: 35, ease: 'inOut' },
    // l08: wave after wave
    { at: 'l08.On', target: [CX, 20], dist: 240, pitch: 36, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l08.wave', target: [CX, -50], dist: 270, pitch: 36, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l08.wave+2.6', target: [CX, -20], dist: 230, pitch: 38, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 'l08.wall', target: [CX, 10], dist: 160, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l08.took', target: [CX, 26], dist: 130, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    // l09: the Immortals and the throne
    { at: 'l09.Even', target: [CX, -20], dist: 190, pitch: 26, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l09.elite', target: [CX, -28], dist: 160, pitch: 20, yaw: -6, mm: 32, ease: 'inOut' },
    { at: 'l09.through', target: [CX, 0], dist: 100, pitch: 28, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l09.Herodotus', target: [-50, -56], dist: 170, pitch: 26, yaw: 300, mm: 35, ease: 'inOut' },
    { at: 'l09.afraid', target: [-56, -58], dist: 130, pitch: 24, yaw: 308, mm: 35, ease: 'inOut' },
    // l10
    { at: 'l10.Two', target: [CX, 0], dist: 220, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    // l11: Ephialtes and the path
    { at: 'l11.Then', target: [-60, -90], dist: 190, pitch: 34, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l11.sold', target: [-70, -100], dist: 140, pitch: 30, yaw: 18, mm: 35, ease: 'inOut' },
    { at: 'l11.hidden', target: [-110, -10], width: 560, pitch: 56, yaw: 328, mm: 35, ease: 'inOut' },
    { at: 'l11.behind', target: [-80, 30], width: 600, pitch: 58, yaw: 340, mm: 35, ease: 'inOut' },
    // l12: the night climb (the camera follows the Immortals around the mountain)
    { at: 'l12.That', target: [-70, -170], dist: 210, pitch: 38, yaw: 330, mm: 35, ease: 'inOut' },
    { at: 'l12.climbed', target: [-170, -110], dist: 190, pitch: 34, yaw: 340, mm: 35, ease: 'inOut' },
    { at: 'l13.Leonidas', target: [-200, -10], dist: 200, pitch: 32, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l13.learned', target: [-180, 80], dist: 210, pitch: 34, yaw: 40, mm: 35, ease: 'inOut' },
    { at: 'l13.surrounded', target: [-30, 110], dist: 190, pitch: 40, yaw: 20, mm: 35, ease: 'inOut' },
    // l13: leaving and staying
    { at: 'l13.He#1', target: [CX, 80], dist: 260, pitch: 44, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l13.stayed', target: [CX, 34], dist: 130, pitch: 34, yaw: -8, mm: 35, ease: 'inOut' },
    { at: 'l13.700', target: [CX, 44], dist: 120, pitch: 40, yaw: 10, mm: 35, ease: 'inOut' },
    // l14: the end
    { at: 'l14.On', target: [CX, 34], dist: 170, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l14.fought', target: [CX, 38], dist: 120, pitch: 48, yaw: 12, mm: 35, ease: 'inOut' },
    { at: 'l15.So', target: [CX, 36], dist: 150, pitch: 30, yaw: 20, mm: 35, ease: 'inOut' },
    // l17: the stone
    { at: 150.4, target: [CX, 40], dist: 220, pitch: 28, yaw: 16, mm: 30, cut: true },
    { at: 'l17.stone', target: [CX, 8], dist: 90, pitch: 22, yaw: 6, mm: 35, ease: 'inOut' },
    { at: 'l17.Go', target: [CX, 8], dist: 80, pitch: 20, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 160, target: [CX, 8], dist: 74, pitch: 20, yaw: 0, mm: 35, ease: 'linear' },
  ],
};

// ====================================================================================== the film
const T_END = cues.duration - cues.outro_s;
const epi = wordT('l17', 'Go'); const eD = (w) => wordT('l17', w) - epi;
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 } },
  ...main,
  stages: { emp, aeg },
  msaaOn: [[41, 52]],
  insets: [
    { stage: 'aeg', at: 0, until: 12.95, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.05, out: 0.35, samples: 2 },
    { stage: 'emp', at: 17.4, until: 34.6, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.9, out: 0.01, samples: 2 },
    { stage: 'aeg', at: 34.3, until: 40.95, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.5, out: 0.5, samples: 2 },
    { stage: 'aeg', at: 133.7, until: 149.9, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.7, out: 0.5, samples: 2 },
  ],
  cards: [
    { at: 0, until: 1.0, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 12.95, until: 17.3, scrim: 0.9, scrimCenter: 'rgba(20,10,4,0.85)', fadeIn: 0.3, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF THERMOPYLAE', size: 0.07, y: 0.44, delay: 0.1 },
      { text: '480 BC', size: 0.07, y: 0.585, delay: 1.1, colorTop: '#ffd9a0', colorBottom: '#e2873a' } ], ornaments: [{ y: 0.35, w: 0.8 }, { y: 0.68, w: 0.8 }] },
    { at: epi - 0.1, until: T_END - 0.2, scrim: 0.9, scrimCenter: 'rgba(16,8,4,0.8)', fadeIn: 0.8, fadeOut: 0.5, lines: [
      { text: 'GO TELL THE SPARTANS,', size: 0.062, y: 0.34, delay: 0.1 },
      { text: 'PASSER BY,', size: 0.062, y: 0.46, delay: eD('passerby') + 0.1, colorTop: '#ffd9a0', colorBottom: '#e2873a' },
      { text: 'THAT HERE, OBEYING THEIR ORDERS,', size: 0.05, y: 0.58, delay: eD('that') + 0.1 },
      { text: 'WE LIE.', size: 0.09, y: 0.72, delay: eD('we') + 0.1, colorTop: '#fff0c4', colorBottom: '#e8b94f' } ], ornaments: [{ y: 0.26, w: 0.7 }, { y: 0.82, w: 0.7 }] },
    { at: T_END, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.13, y: 0.43, delay: 0.1, track: 0.14 },
      { text: 'The Battle of Thermopylae, 480 BC', size: 0.062, y: 0.6, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.5 }, { y: 0.69, w: 0.5 }] },
  ],
};
