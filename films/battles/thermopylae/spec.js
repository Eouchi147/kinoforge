// The Battle of Thermopylae (August 480 BC): Battle Map v2 spec (see films/lib/battlemap/SPEC.md, the reference film films/battles/cannae/,
// and NOTES.md here for the scene list). Times come from the cue words; the line starts never change (the sound is re-scored around them).
// Teams: the Persians are red (team 'rome'), the Greeks are blue (team 'carthage').
// Stages: main = the pass (x east, z south; the Persians come from the north, the sea is east, the cliff wall west; 1 unit about 4 m);
//         aeg  = the Aegean (the invasion, the Greek cities, Athens, Salamis, Plataea);  emp = the Persian Empire, Egypt to India.
// The ASR spelled some words oddly in cues.json: "Dianik," (Dienekes), "Effialty's" (Ephialtes), "Thespier", and "past" for "pass" (l10, l17).
// Film-side glyphs `pass`, `trail`, `stele` and `lambda` live in units.js (registered in index.html).
const PER = { team: 'rome' }, GRE = { team: 'carthage' };
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
    { type: 'road', path: [[-52, -196], [-118, -176], [-182, -124], [-206, -50], [-196, 30], [-150, 100], [-86, 142], [-30, 140], [-8, 128]], w: 1.2, meander: 3 },   // the hidden mountain path
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
const EMP_SEAS = empWorld.features.filter((f) => f.type === 'sea').map((f) => f.poly);
const PERSEPOLIS = [99, 76];

const HIDDEN = [[-52, -196], [-118, -176], [-182, -124], [-206, -50], [-196, 30], [-150, 100], [-86, 142]];   // the hidden mountain path (Anopaea)

// ====================================================================================== the Persian Empire (stage emp)
const E_POS = [[-60, -60], [-140, -20], [-200, 70], [-236, 110], [-20, -20], [30, 20], [60, 100], [140, 40], [190, -40], [250, 10], [330, -30], [360, 80], [40, -100], [200, -140]];
const E_ORDER = E_POS.map((p, k) => [p[0], k]).sort((a, b) => a[0] - b[0]).map((q) => q[1]);   // west to east: Egypt first, India last
const emp = {
  world: empWorld,
  ambient: { wind: [1, 0.3], gusts: 0, flow: { dir: [1, 0.2], speed: 0.5, glint: 1.1 }, birds: [{ center: [-280, 0], r: 30, h: 18, n: 5, speed: 5, size: 1.0 }] },
  blocks: Object.fromEntries(E_POS.map((p, k) => [`E${k}`, { ...PER, kind: 'infantry', x: p[0], z: p[1], heading: 270, len: 36, dep: 15, hidden: true, bannerScale: 2.0, figScale: 1.5 }])),
  moves: E_ORDER.map((k, i) => ({ block: `E${k}`, at: `l02.empire+${(i * 0.13).toFixed(2)}`, dur: 0.8, appear: true })),
  labels: [
    { at: 'l02', until: 'l02.Egypt', text: 'GREECE', pos: [-392, -72], y: 4, leader: false, rule: false, team: 'carthage' },
    { at: 'l02', until: 'l02.Egypt', text: 'MEDITERRANEAN SEA', pos: [-330, 10], y: 2, leader: false, rule: false },
    { at: 'l02.Xerxes,', until: 'l02.His', text: 'XERXES', pos: PERSEPOLIS, y: 6, team: 'rome', dx: -0.1, dy: -0.14 },
    { at: 'l02.Egypt', until: 'l02.Ancient', text: 'EGYPT', pos: [-236, 90], y: 6, team: 'rome', dx: 0.04, dy: -0.12 },
    { at: 'l02.India.', until: 'l02.Ancient', text: 'INDIA', pos: [388, 40], y: 6, team: 'rome', dx: -0.06, dy: -0.12 },
  ],
  counters: [
    { at: 'l02.million', until: 'l02.Modern', screen: [0.6, 0.84], team: 'rome', from: 0, to: 1000000, countDur: 0.9, step: 10000, suffix: 'ANCIENT WRITERS' },
    { at: 'l02.Modern', until: 'l03', screen: [0.6, 0.84], team: 'rome', from: 1000000, to: 100000, countDur: 1.8, step: 10000, suffix: 'MODERN ESTIMATE, OR MORE' },
  ],
  markers: [{ id: 'persepolis', at: 'l02.Xerxes,', until: 'l03', pos: PERSEPOLIS, glyph: 'town', team: [0.74, 0.12, 0.12], label: false, size: 0.055 }],
};

// ====================================================================================== the Aegean (stage aeg)
const A_N = 16;
const A_ID = Array.from({ length: A_N }, (_, k) => `A${k}`);
const aStart = (k) => [100 + (k % 4) * 15, -92 + Math.floor(k / 4) * 14];
const aEnd = (k) => [-88 + ((k % 2) * 2 - 1) * 7, -62 - Math.floor(k / 2) * 9];
const aMove = (k, t0, dur, pts) => ({ block: `A${k}`, at: t0, dur, path: pts(k), ease: 'inOut' });
const cityLine = (a, b, bend = 5) => { const [x0, z0] = a, [x1, z1] = b; const mx = (x0 + x1) / 2, mz = (z0 + z1) / 2; const dx = x1 - x0, dz = z1 - z0; const l = Math.hypot(dx, dz) || 1; return [a, [mx - dz / l * bend, mz + dx / l * bend], b]; };
const shrink = (a, b, k = 0.2) => [[a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k], [b[0] - (b[0] - a[0]) * k, b[1] - (b[1] - a[1]) * k]];
const PAIRS = [['athens', 'sparta'], ['corinth', 'tegea'], ['athens', 'corinth'], ['sparta', 'tegea']];
const squab = [];   // rivals: thin ink arrows both ways between the cities
PAIRS.forEach(([a, b], i) => { const [p, q] = shrink(AEG_CITIES[a], AEG_CITIES[b], 0.18);
  squab.push({ at: `l03.fighting+${(i * 0.15).toFixed(2)}`, dur: 0.7, ease: 'out', team: 'ink', width: 1.3, path: cityLine(p, q, 4), lift: 3, hide: 'l03.This', head: true });
  squab.push({ at: `l03.fighting+${(0.3 + i * 0.15).toFixed(2)}`, dur: 0.7, ease: 'out', team: 'ink', width: 1.3, path: cityLine(q, p, 4), lift: 3, hide: 'l03.This', head: true }); });
const teamUp = Object.entries(AEG_CITIES).map(([name, p], i) => ({ at: `l03.teamed+${(i * 0.12).toFixed(2)}`, dur: 1.2, ease: 'cam', team: 'carthage', width: 2.2, path: [p, [(p[0] + THERMO[0]) / 2 + (i % 2 ? 6 : -6), (p[1] + THERMO[1]) / 2], THERMO], lift: 4, hide: 'l04' }));
const SAL_P = [[-26, 8], [-18, 16], [-28, 26], [-12, 26], [-32, 0], [-10, 6]];   // the Persian galleys in the straits

const aeg = {
  world: aegWorld,
  ambient: { wind: [1, 0.3], gusts: 0.2, flow: { dir: [0.6, 0.6], speed: 0.6, glint: 1.2 },
    birds: [{ center: [-40, 40], r: 24, h: 14, n: 5, speed: 5, size: 0.9 }, { center: [60, -60], r: 30, h: 18, n: 5, speed: 6, dir: -1, size: 0.9 }],
    smoke: [{ pos: AEG_CITIES.athens, n: 8, alpha: 0.28, height: 9, at: 'l15.burned' }, { pos: [AEG_CITIES.athens[0] + 4, AEG_CITIES.athens[1] + 3], n: 6, alpha: 0.22, height: 7, at: 'l15.burned+0.4' }] },
  blocks: {
    ...Object.fromEntries(A_ID.map((id, k) => [id, { ...PER, kind: 'infantry', x: aStart(k)[0], z: aStart(k)[1], heading: 270, len: 14, dep: 7, hidden: true, bannerScale: 1.2, figScale: 1.4 }])),
    G: { ...GRE, kind: 'elite', x: THERMO[0], z: THERMO[1], heading: 0, len: 9, dep: 5, hidden: true, bannerScale: 1.3, figScale: 1.4 },
    plR: { ...PER, kind: 'infantry', x: -46, z: -22, heading: 180, len: 22, dep: 9, hidden: true, bannerScale: 1.4, figScale: 1.4 },
    plG: { ...GRE, kind: 'elite', x: -50, z: 28, heading: 0, len: 22, dep: 9, hidden: true, bannerScale: 1.4, figScale: 1.4 },
  },
  moves: [
    // S1: the army crosses from Asia and floods into Greece; a few thousand Greeks wait at the gap
    { blocks: A_ID, at: 'l00.biggest', dur: 0.8, stagger: 0.12, appear: true },
    ...A_ID.map((_, k) => aMove(k, `l00.marched+${(k * 0.11).toFixed(2)}`, 4.0, () => [aStart(k), [76, -104], [40, -126], [-10, -122], [-56, -104], [-76, -82], aEnd(k)])),
    { block: 'G', at: 'l00.few', dur: 0.8, appear: true },
    // S8: the army marches south to Athens; Salamis; Plataea
    { blocks: A_ID, at: 'l02', dur: 0.3, vanish: true }, { block: 'G', at: 'l04', dur: 0.3, vanish: true },   // offscreen between the scenes on this map
    { blocks: A_ID, at: 'l15.They+0.1', dur: 0.8, stagger: 0.04, appear: true },
    ...A_ID.map((_, k) => aMove(k, `l15.marched+${(k * 0.06).toFixed(2)}`, 2.8, () => { const e = aEnd(k); return [e, [-72, -40], [-58, -14], [-40, 2], [-26 + (k % 4) * 3, 8 + Math.floor(k / 4) * 2]]; })),
    { blocks: A_ID, at: 'l16', dur: 0.8, vanish: true },
    { blocks: ['plR', 'plG'], at: 'l16.In', dur: 0.8, appear: true },
    { block: 'plG', at: 'l16.beaten', dur: 1.2, to: { z: -2 }, ease: 'inOut' },
    { block: 'plR', at: 'l16.beaten', dur: 1.6, to: { z: -60 }, ease: 'in' }, { block: 'plR', at: 'l16.beaten', dur: 1.6, fadeTo: 1, alphaTo: 0.5 },
  ],
  arrows: [
    { at: 'l00.marched', until: 'l00.and', ease: 'cam', team: 'rome', style: 'dash', width: 2.6, path: [[76, -104], [40, -126], [-10, -122], [-56, -104], [-76, -82], [-86, -58]], lift: 4, head: true, hide: 'l00.few' },
    ...squab, ...teamUp,
    { at: 'l15.marched', until: 'l15.Athens.', ease: 'cam', team: 'rome', style: 'dash', width: 2.4, path: [[-84, -58], [-72, -40], [-58, -14], [-40, 2], [-22, 12]], lift: 4, head: true, hide: 'l16' },
    { id: 'gship1', at: 'l16.Navy', dur: 1.6, ease: 'cam', team: 'carthage', width: 1.4, path: [[-52, 26], [-40, 20], [-30, 14]], lift: 3, hide: 'l16.In' },
    { id: 'gship2', at: 'l16.Navy+0.15', dur: 1.6, ease: 'cam', team: 'carthage', width: 1.4, path: [[-50, 14], [-38, 12], [-28, 8]], lift: 3, hide: 'l16.In' },
    { id: 'gship3', at: 'l16.Navy+0.3', dur: 1.6, ease: 'cam', team: 'carthage', width: 1.4, path: [[-50, 36], [-38, 30], [-26, 24]], lift: 3, hide: 'l16.In' },
    { at: 'l16.beaten', dur: 1.2, ease: 'out', team: 'carthage', width: 2.4, path: [[-50, 20], [-50, 4]], lift: 4, head: true, hide: 'l17' },
  ],
  labels: [
    { at: 'l00.480', until: 'l00.the', text: '480 BC', screen: [0.5, 0.86], big: true },
    { at: 'l00.biggest', until: 'l00.and', text: 'PERSIA', pos: [150, -40], y: 4, leader: false, rule: false, team: 'rome' },
    { at: 'l00.marched', until: 'l00.few', text: 'GREECE', pos: [-110, -10], y: 4, leader: false, rule: false, team: 'carthage' },
    { at: 'l00.gap', until: 12.9, text: 'THERMOPYLAE', pos: THERMO, y: 4, team: 'carthage', dx: -0.1, dy: -0.12 },
    { at: 'l03.Greek', until: 'l04', text: 'ATHENS', pos: AEG_CITIES.athens, y: 6, dx: 0.08, dy: -0.1 },
    { at: 'l03.Greek+0.1', until: 'l04', text: 'CORINTH', pos: AEG_CITIES.corinth, y: 6, dx: 0.1, dy: -0.1 },
    { at: 'l03.Greek+0.2', until: 'l04', text: 'SPARTA', pos: AEG_CITIES.sparta, y: 6, dx: 0.08, dy: 0.1 },
    { at: 'l03.Greek+0.3', until: 'l04', text: 'TEGEA', pos: AEG_CITIES.tegea, y: 6, dx: -0.1, dy: -0.1 },
    { at: 'l03.teamed', until: 'l04', text: 'THERMOPYLAE', pos: THERMO, y: 6, team: 'carthage', dx: 0.1, dy: -0.1 },
    { at: 'l15.burned', until: 'l16', text: 'ATHENS', pos: AEG_CITIES.athens, y: 6, team: 'rome', dx: 0.1, dy: -0.12 },
    { at: 'l16.Salamis.', until: 'l16.In', text: 'SALAMIS', pos: [-38, 16], y: 2, team: 'carthage', dx: -0.12, dy: -0.12 },
    { at: 'l16.In', until: 'l17', text: 'PLATAEA, 479 BC', pos: [-48, 4], y: 6, team: 'carthage', dx: 0.12, dy: -0.14 },
  ],
  icons: [
    ...['gship1', 'gship2', 'gship3'].map((id) => ({ follow: id, at: 'l16.Navy', until: 'l16.In', icon: 'galley', team: 'carthage', size: 8, minPx: 0.06, maxPx: 0.075 })),
    ...SAL_P.map((p, i) => ({ at: 'l16.A', until: 'l16.In', icon: 'galley', team: 'rome', pos: p, y: 1, size: 8, minPx: 0.06, maxPx: 0.075, flip: true, fallAt: `l16.smashed+${(0.2 + 0.22 * i).toFixed(2)}`, fallDur: 0.9 })),
  ],
  markers: Object.entries(AEG_CITIES).map(([id, p], i) => ({ id, at: `l03.Greek+${(0.1 * i).toFixed(1)}`, until: 'l04', pos: p, glyph: 'town', team: [0.15, 0.33, 0.74], label: false, size: 0.045 })),
};

// ====================================================================================== the pass: the armies
const SLOT = [24, 35, 46];   // the shield wall, three blocks deep, at the narrowest point
const HIT = 14;              // where a Persian block's centre stops when its front meets the wall
const D_ID = ['D0', 'D1', 'D2', 'D3'], D_X = [-66, -22, 22, 66];
// one wave: it forms up in the road, marches into the wall, presses, thins, and melts away as the next one arrives
const wave = (id, arrive, jit) => [
  { block: id, at: arrive - 3.6, dur: 0.6, appear: true },
  { block: id, at: arrive - 3.0, dur: 3.0, to: { z: HIT, x: CX + jit }, ease: 'inQuad' },
  { block: id, at: arrive, dur: 1.4, fadeTo: 1, alphaTo: 0.5 },
  { block: id, at: arrive + 1.4, dur: 0.8, vanish: true },
];
// the shield wall takes turns at the front: the front block steps into the west lane and back, the others come up the east lane
const rot = (t, [front, mid, back]) => [
  { block: front, at: t, dur: 0.5, to: { x: CX - 6.5, len: 10 }, ease: 'inOut' }, { blocks: [mid, back], at: t, dur: 0.5, to: { x: CX + 5.5, len: 10 }, ease: 'inOut' },
  { block: front, at: t + 0.55, dur: 1.0, to: { z: SLOT[2] }, ease: 'inOut' }, { block: mid, at: t + 0.55, dur: 1.0, to: { z: SLOT[0] }, ease: 'inOut' }, { block: back, at: t + 0.55, dur: 1.0, to: { z: SLOT[1] }, ease: 'inOut' },
  { blocks: [front, mid, back], at: t + 1.6, dur: 0.5, to: { x: CX, len: 22 }, ease: 'inOut' },
];

const blocks = {
  // the Persians
  ...Object.fromEntries(D_ID.map((id, k) => [id, { ...PER, kind: 'infantry', x: -60 + k * 40, z: -150, heading: 180, len: 36, dep: 12, hidden: true }])),
  horde: { ...PER, kind: 'infantry', x: CX, z: -250, heading: 180, len: 220, dep: 30, grid: { cols: 9, ranks: 2, gap: 3 }, hidden: true },
  xerxes: { ...PER, kind: 'elite', x: -60, z: -112, heading: 160, len: 6, dep: 4, hidden: true, bannerScale: 1.4 },
  arch: { ...PER, kind: 'archers', x: CX, z: -70, heading: 180, len: 34, dep: 10, hidden: true },
  ...Object.fromEntries(['P0', 'P1', 'P2', 'P3', 'P4'].map((id) => [id, { ...PER, kind: 'infantry', x: CX, z: -116, heading: 180, len: 22, dep: 9, hidden: true }])),
  imm: { ...PER, kind: 'elite', x: CX, z: -100, heading: 180, len: 22, dep: 10, hidden: true, bannerScale: 1.3 },
  imm2: { ...PER, kind: 'elite', x: HIDDEN[1][0], z: HIDDEN[1][1], heading: 240, len: 18, dep: 8, hidden: true, bannerScale: 1.3 },
  Q0: { ...PER, kind: 'infantry', x: CX, z: -60, heading: 180, len: 22, dep: 9, hidden: true },
  Q1: { ...PER, kind: 'infantry', x: CX, z: -76, heading: 180, len: 22, dep: 9, hidden: true },
  Q2: { ...PER, kind: 'infantry', x: CX, z: 150, heading: 0, len: 22, dep: 9, hidden: true },
  eph: { team: 'neutral', kind: 'light', x: -150, z: -150, heading: 110, len: 3, dep: 2, hidden: true, banner: false },
  // the Greeks
  camp: { ...GRE, kind: 'elite', x: CX - 2, z: 96, heading: 0, len: 44, dep: 22, hidden: true, bannerScale: 0.8 },
  w1: { ...GRE, kind: 'elite', x: CX, z: SLOT[0], heading: 0, len: 22, dep: 9, count: 300, hidden: true, bannerScale: 1.0 },
  w2: { ...GRE, kind: 'elite', x: CX, z: SLOT[1], heading: 0, len: 22, dep: 9, hidden: true },
  w3: { ...GRE, kind: 'elite', x: CX, z: SLOT[2], heading: 0, len: 22, dep: 9, hidden: true },
  thesp: { ...GRE, kind: 'elite', x: CX + 1, z: 58, heading: 0, len: 22, dep: 9, count: 700, hidden: true },
};

const moves = [
  // S4: a giant army squeezes into the road a little at a time, then falls back to wait
  { blocks: D_ID, at: 'l04.giant', dur: 0.8, stagger: 0.14, appear: true },
  ...D_ID.map((id, k) => ({ block: id, at: 'l04.squeeze', dur: 1.6, to: { x: CX, z: -40 - k * 15, len: 24 }, ease: 'inOut' })),
  ...D_ID.map((id, k) => ({ block: id, at: 'l05.Leonidas', dur: 3.0, to: { x: D_X[k], z: -190, len: 36 }, ease: 'inOut' })),
  { blocks: ['camp', 'w2', 'w3'], at: 'l05.Holding', dur: 0.9, stagger: 0.2, appear: true },
  { block: 'w1', at: 'l05.Leonidas', dur: 0.9, appear: true },
  // S5: Xerxes and his host wait; the archers draw up and loose
  { group: 'horde', at: 'l06.Xerxes', dur: 0.9, stagger: 0.06, appear: true },
  { block: 'xerxes', at: 'l06.Xerxes', dur: 0.8, appear: true },
  { block: 'arch', at: 'l07.Herodotus', dur: 0.9, appear: true },
  { block: 'arch', at: 'l08', dur: 0.8, vanish: true },
  // S6: wave after wave; the wall takes turns; the Immortals fail; the king jumps up three times
  ...wave('P0', 83.3, -3), ...wave('P1', 85.5, 3),
  ...rot(87.29, ['w1', 'w2', 'w3']),
  ...wave('P2', 89.6, -2),
  { block: 'imm', at: 'l09.elite-0.4', dur: 0.6, appear: true },
  { block: 'imm', at: 'l09.elite', dur: 2.4, to: { z: HIT }, ease: 'inQuad' },
  { block: 'imm', at: 'l09.through.', dur: 1.0, fadeTo: 0.6, alphaTo: 0.7 },
  { block: 'imm', at: 'l09.Herodotus', dur: 2.0, to: { z: -110 }, ease: 'out' },
  { block: 'imm', at: 'l09.afraid', dur: 1.0, vanish: true },
  ...['jumped', 'three', 'times,'].flatMap((w) => [{ block: 'xerxes', at: `l09.${w}`, dur: 0.18, to: { lift: 1.6 }, ease: 'out' }, { block: 'xerxes', at: `l09.${w}+0.2`, dur: 0.25, to: { lift: 0 }, ease: 'in' }]),
  ...rot(95.0, ['w2', 'w3', 'w1']),
  ...wave('P3', 99.6, 2), ...wave('P4', 101.8, -3),
  // S7: Ephialtes; the night climb; most Greeks leave; the ring closes; the end
  { block: 'eph', at: 'l11.local', dur: 0.6, appear: true },
  { block: 'eph', at: 'l11.man', dur: 2.6, path: [[-150, -150], [-110, -136], [-68, -118]], ease: 'inOut' },
  { block: 'eph', at: 'l12', dur: 0.6, vanish: true },
  { block: 'imm2', at: 'l12.That', dur: 0.6, appear: true },
  { block: 'imm2', at: 'l12.That+0.3', dur: 5.4, path: HIDDEN.slice(1), ease: 'inOut' },
  { block: 'camp', at: 'l13.sent', dur: 4.5, path: [[CX - 2, 96], [20, 150], [40, 220], [44, 290]], ease: 'in' }, { block: 'camp', at: 'l13.sent+3.8', dur: 0.8, vanish: true },
  { block: 'w2', at: 'l13.sent+0.6', dur: 5.0, path: [[CX, SLOT[2]], [0, 96], [22, 150], [40, 220], [44, 290]], ease: 'in' }, { block: 'w2', at: 'l13.sent+4.8', dur: 0.8, vanish: true },
  { block: 'thesp', at: 'l13.700', dur: 0.9, appear: true },
  { blocks: ['Q0', 'Q1', 'Q2'], at: 'l14.third', dur: 0.8, stagger: 0.15, appear: true },
  { block: 'thesp', at: 'l14.On', dur: 1.0, to: { heading: 180 }, ease: 'inOut' },
  { block: 'Q0', at: 'l14.surrounded', dur: 1.8, to: { z: HIT }, ease: 'inOut' }, { block: 'Q1', at: 'l14.surrounded', dur: 1.8, to: { z: HIT - 12 }, ease: 'inOut' },
  { block: 'imm2', at: 'l14.surrounded', dur: 1.8, to: { x: CX, z: 69, heading: 0 }, ease: 'inOut' }, { block: 'Q2', at: 'l14.surrounded', dur: 1.8, to: { z: 82 }, ease: 'inOut' },
  { blocks: ['w3', 'w1', 'thesp'], at: 'l14.fought', dur: 2.6, stagger: 0.3, fadeTo: 1, alphaTo: 0.5 },
  { blocks: ['w3', 'w1', 'thesp'], at: 'l15.So,', dur: 1.6, stagger: 0.2, vanish: true },
  { blocks: ['Q0', 'Q1', 'Q2', 'imm2', 'xerxes', 'horde', ...D_ID], at: 'l16', dur: 0.5, vanish: true },   // offscreen: the pass is empty when we come back
];

// ====================================================================================== the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.06, grain: 0.03, vignette: 0.30 } },
  world: passWorld,
  stages: { emp, aeg },
  msaaOn: [['l06.away.', 'l07'], ['l07.Spartan', 'l08'], ['l13.He#2', 'l14']],   // anti-aliasing only on the three low close shots
  blocks,
  moves,

  ambient: {
    wind: [-0.6, 1.0], gusts: 0.5, flow: { dir: [1, 0.1], speed: 0.8, glint: 1.2 },
    camps: [{ pos: [40, -258], size: [150, 30], team: 'rome', style: 'grid', tents: 40, fires: 4, people: 16, palisade: false }],
    walkers: [{ path: [[-20, 130], [-46, 200], [-70, 280]], n: 5, gap: 5, speed: 1.2, kind: 'light', team: 'neutral', until: 'l13' }],
    smoke: [{ pos: [0, -258], n: 6, alpha: 0.14, height: 8 }, { pos: [80, -256], n: 6, alpha: 0.14, height: 8 }, { pos: [CX, 18], n: 8, alpha: 0.16, height: 6, at: 'l08.wave', until: 'l11' }],
    birds: [{ center: [80, -30], r: 40, h: 22, n: 6, speed: 6 }, { center: [-30, 60], r: 26, h: 30, n: 2, speed: 4, dir: -1 }, { path: [[320, -200], [-200, 200]], n: 5, h: 36, speed: 8 }],
  },

  light: [
    { at: 'l07.block', dur: 1.2, to: { cloud: 0.9 }, ease: 'inOut' }, { at: 'l08', dur: 1.4, to: { cloud: 0.3 }, ease: 'inOut' },
    { at: 'l12', dur: 1.0, to: { eve: 0.9, haze: 1.5 }, ease: 'inOut' }, { at: 'l13', dur: 1.6, to: { eve: 0.15, haze: 1.1 }, ease: 'inOut' },
  ],

  // ------------------------------------------------------------------ scenes: sets and pre-planned cameras (the edit)
  scenes: [
    { id: 'S1', name: 'The invasion', at: 0, stage: 'aeg', inset: 'full', job: 'the biggest army ever seen marches into Greece; a few thousand Greeks wait at a gap in the mountains', set: { time: 0.1, haze: 1.0 },
      shots: [
        { at: 0, why: 'cold open on the Aegean: the Persian columns cross from Asia into Greece', from: { target: [64, -84], width: 330, pitch: 52, yaw: 0, mm: 35 },
          moves: [{ at: 'l00.marched', until: 'l00.Greece,>', to: { target: [0, -92], width: 350 }, ease: 'cam' }] },
        { at: 'l00.and', why: 'closer: a few thousand Greeks at the gap, held under the title', from: { target: [-70, -52], width: 210, pitch: 48, yaw: 6, mm: 35 },
          moves: [{ until: 12.9, to: { target: [-82, -40], width: 140 }, ease: 'cam' }] },
      ] },
    { id: 'S2', name: 'King of Kings', at: 'l02', stage: 'emp', inset: 'full', transition: { type: 'dissolve', dur: 0.9 }, job: 'who is coming: Xerxes, an empire from Egypt to India, and how big his army really was', set: { time: 0.08, haze: 1.0 },
      shots: [
        { at: 'l02', why: 'change of world: the king of kings in his capital', from: { target: [86, 64], width: 360, pitch: 54, yaw: 0, mm: 35 },
          moves: [{ until: 'l02.His', to: { width: 334 }, ease: 'cam' }] },
        { at: 'l02.His', why: 'pull out to the whole empire as its armies rise from Egypt to India', from: { target: [50, 20], width: 860, pitch: 62, yaw: 0, mm: 35 },
          moves: [{ until: 'l02.Ancient', to: { width: 830 }, ease: 'cam' }] },
        { at: 'l02.Ancient', why: 'the numbers over the western armies: the ancient figure, then the modern one', from: { target: [-80, 24], width: 520, pitch: 44, yaw: 340, mm: 35 },
          moves: [{ until: 'l02.more#1>', to: { yaw: 350, width: 500 }, ease: 'cam' }] },
        { at: 'l02.Still,', why: 'cut on the punchline: low over the massed armies, still a lot', from: { target: [-40, 10], dist: 200, pitch: 12, yaw: 290, mm: 35 },
          moves: [{ until: 'l03', to: { dist: 188 }, ease: 'cam' }] },
      ] },
    { id: 'S3', name: 'The allies', at: 'l03', stage: 'aeg', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'the Greek cities usually fight each other; this time some team up', set: { time: 0.08, haze: 1.0 },
      shots: [
        { at: 'l03', why: 'change of world, back to Greece: the rival cities', from: { target: [-58, 34], width: 240, pitch: 58, yaw: 0, mm: 35 },
          moves: [{ until: 'l03.This', to: { width: 226 }, ease: 'cam' }] },
        { at: 'l03.This', why: 'lower and turned toward the north: their routes converge on the pass', from: { target: [-86, -12], width: 250, pitch: 36, yaw: 24, mm: 35 },
          moves: [{ until: 'l04', to: { target: [-88, -20], yaw: 16 }, ease: 'cam' }] },
      ] },
    { id: 'S4', name: 'The pass', at: 'l04', transition: { type: 'dissolve', dur: 0.9 }, job: 'why here: a road between a cliff and the sea where a giant army can only come a little at a time; who holds it', set: { time: 0.06, haze: 1.05, cloud: 0.3 },
      shots: [
        { at: 'l04', why: 'change of world: the pass from high in the south, the cliff wall and the sea', from: { target: [CX, -36], width: 440, pitch: 42, yaw: 4, mm: 35 },
          moves: [{ until: 'l04.Thermopylae,>', to: { target: [CX, -16], width: 410 }, ease: 'cam' }] },
        { at: 'l04.steep', why: 'low in the road at the narrowest point: mountains on one side, the sea on the other', from: { target: [CX, 4], dist: 150, pitch: 9, yaw: 0, mm: 30 },
          moves: [{ until: 'l04.other.>', to: { dist: 138 }, ease: 'cam' }] },
        { at: 'l04.A#1', why: 'top-down: the giant army squeezes into the road a little at a time', from: { target: [CX, -104], width: 300, pitch: 82, yaw: 0, mm: 35 },
          moves: [{ at: 'l04.squeeze', until: 'l04.time.>', to: { target: [CX, -70], width: 280 }, ease: 'cam' }] },
        { at: 'l05', why: 'the defenders: low behind the Greek wall at the narrowest point', from: { target: [CX, 14], dist: 140, pitch: 17, yaw: 352, mm: 35 },
          moves: [{ until: 'l05.Spartans.>', to: { dist: 108 }, ease: 'cam' }] },
      ] },
    { id: 'S5', name: 'The wait', at: 'l06', job: 'Xerxes waits four days for them to run; they do not; then the arrows', set: { time: [0.45, 0.05], haze: 1.15, cloud: 0.3 },
      shots: [
        { at: 'l06', why: 'the other side: from high behind the tiny Greek wall to the host that fills the plain', from: { target: [CX, -150], width: 500, pitch: 30, yaw: 0, mm: 35 },
          moves: [{ until: 'l06.away.', to: { width: 470 }, ease: 'cam' }] },
        { at: 'l06.away.', why: 'cut on the punchline: low and close on the front rank, which does not move', from: { target: [CX, 22], dist: 64, pitch: 9, yaw: 336, mm: 40 },
          moves: [{ until: 'l07', to: { dist: 60 }, ease: 'cam' }] },
        { at: 'l07', why: 'Herodotus\' story: high over the archers drawn up in the pass as the sky fills with arrows', from: { target: [CX, -36], width: 300, pitch: 40, yaw: 12, mm: 35 },
          moves: [{ until: 'l07.sun.>', to: { target: [CX, -14], width: 280, yaw: 8 }, ease: 'cam' }] },
        { at: 'l07.Spartan', why: 'close on the Spartan front in the shadow, held for the answer', from: { target: [CX, 24], dist: 70, pitch: 13, yaw: 24, mm: 40 },
          moves: [{ until: 'l08', to: { dist: 64, yaw: 18 }, ease: 'cam' }] },
      ] },
    { id: 'S6', name: 'Wave after wave', at: 'l08', job: 'the Persians attack for two days and cannot break the wall, not even the Immortals', set: { time: 0.04, haze: 1.05, cloud: 0.3 },
      shots: [
        { at: 'l08', why: 'reverse angle, the attackers\' side: behind the Persian waves pouring into the pass', from: { target: [CX, -20], dist: 200, pitch: 24, yaw: 176, mm: 35 },
          moves: [{ until: 'l08.pass.>', to: { target: [CX, 0], dist: 184 }, ease: 'cam' }] },
        { at: 'l08.Greeks', why: 'high and close over the shield wall: the front rank steps back and the next takes its place', from: { target: [CX, 30], width: 120, pitch: 60, yaw: 18, mm: 35 },
          moves: [{ until: 'l09', to: { width: 112 }, ease: 'cam' }] },
        { at: 'l09', why: 'low behind the Immortals as they charge the wall', from: { target: [CX, -40], dist: 120, pitch: 12, yaw: 184, mm: 35 },
          moves: [{ until: 'l09.through.>', to: { target: [CX, -10], dist: 112 }, ease: 'cam' }] },
        { at: 'l09.Herodotus', why: 'reaction: the king\'s standard on the slope above the pass', from: { target: [-50, -96], dist: 76, pitch: 16, yaw: 150, mm: 40 },
          moves: [{ until: 'l10', to: { dist: 70 }, ease: 'cam' }] },
        { at: 'l10', why: 'top-down, two days on: the wall stands where it stood', from: { target: [CX, 4], width: 260, pitch: 84, yaw: 0, mm: 35 },
          moves: [{ until: 'l11', to: { width: 250 }, ease: 'cam' }] },
      ] },
    { id: 'S7', name: 'Surrounded', at: 'l11', climax: true, job: 'a traitor shows the Persians a way round; most Greeks leave; the Spartans and the Thespians stay and die', set: { time: 0.08, haze: 1.1, cloud: 0.3 },
      shots: [
        { at: 'l11', why: 'a new character: a local man walks into the Persian camp with a secret', from: { target: [-100, -128], dist: 130, pitch: 20, yaw: 116, mm: 35 },
          moves: [{ until: 'l11.secret,>', to: { target: [-80, -122] }, ease: 'cam' }] },
        { at: 'l11.hidden', why: 'top-down over the mountains: the hidden path, around and behind the Greeks', from: { target: [-110, -20], width: 500, pitch: 80, yaw: 0, mm: 35 },
          moves: [{ until: 'l11.Greeks.>', to: { width: 480 }, ease: 'cam' }] },
        { at: 'l12', why: 'change of time, night: follow the Immortals along the mountain path', from: { target: [-150, -150], width: 270, pitch: 50, yaw: 344, mm: 35 },
          moves: [{ until: 'l13', to: { target: [-196, -30] }, ease: 'cam' }] },
        { at: 'l13', why: 'dawn, high and wide: they come down behind the pass and most of the Greeks march away', from: { target: [-30, 66], width: 430, pitch: 56, yaw: 0, mm: 35 },
          moves: [{ until: 'l13.He#2', to: { target: [-20, 76], width: 410 }, ease: 'cam' }] },
        { at: 'l13.He#2', why: 'low and close on the ones who stay', from: { target: [CX, 44], dist: 92, pitch: 13, yaw: 340, mm: 40 },
          moves: [{ until: 'l14', to: { dist: 84, yaw: 348 }, ease: 'cam' }] },
        { at: 'l14', why: 'the decisive moment, wide and from above: the ring closes from both ends', from: { target: [CX, 36], width: 300, pitch: 86, yaw: 0, mm: 35 },
          moves: [{ until: 'l14.they', to: { width: 284 }, ease: 'cam' }] },
        { at: 'l14.they', why: 'the same moment closer and lower: the ranks thin to the end; pull back on the result', from: { target: [CX, 40], dist: 96, pitch: 18, yaw: 40, mm: 40 },
          moves: [{ until: 'l15.They', to: { dist: 136, pitch: 24 }, ease: 'camLong' }] },
      ] },
    { id: 'S8', name: 'The war', at: 'l15.They', stage: 'aeg', inset: 'full', transition: { type: 'dissolve', dur: 0.9 }, job: 'why it mattered: they burn Athens, then lose at sea and on land', set: { time: 0.3, haze: 1.05 },
      shots: [
        { at: 'l15.They', why: 'change of world: the Persian march south and the smoke over Athens', from: { target: [-52, -20], width: 220, pitch: 52, yaw: 0, mm: 35 },
          moves: [{ until: 'l15.story.>', to: { target: [-40, -4], width: 200 }, ease: 'cam' }] },
        { at: 'l16', why: 'the time it bought: lower over the straits of Salamis', from: { target: [-34, 16], width: 130, pitch: 40, yaw: 340, mm: 35 },
          moves: [{ until: 'l16.Salamis.>', to: { width: 122 }, ease: 'cam' }] },
        { at: 'l16.In', why: 'the next year, on land: Plataea, beaten for good', from: { target: [-48, -4], width: 160, pitch: 54, yaw: 12, mm: 35 },
          moves: [{ until: 'l17', to: { width: 150 }, ease: 'cam' }] },
      ] },
    { id: 'S9', name: 'The stone', at: 'l17', transition: { type: 'dissolve', dur: 1.0 }, job: 'the epitaph at the empty pass', set: { time: 0.7, haze: 1.2, cloud: 0.25 },
      shots: [
        { at: 'l17', why: 'change of time, today: the empty pass in the evening, a slow push on the stone', from: { target: [CX, 40], dist: 160, pitch: 16, yaw: 196, mm: 35 },
          moves: [{ until: 'l17.Go', to: { target: [0, 46], dist: 120 }, ease: 'camLong' }] },
      ] },
  ],

  // ------------------------------------------------------------------ the legend (motion-graphics frame)
  legend: {
    title: { text: 'THERMOPYLAE', sub: 'The battle, August 480 BC', at: 'l02' },
    show: [['l02', 'l17']],
    sides: [
      { id: 'persia', team: 'rome', name: 'PERSIA', commander: 'Xerxes', commanderAt: 'l02.Xerxes,', banner: 'banner', at: 'l02.Persia.', strength: 100000, strengthAt: 'l02.100' },
      { id: 'greeks', team: 'carthage', name: 'GREEK ALLIES', commander: 'Leonidas of Sparta', commanderAt: 'l05.Leonidas', banner: 'lambda', at: 'l03.Greek', strength: 7000, strengthAt: 'l05.7' },
    ],
    key: { show: [['l04.Thermopylae,', 'l06'], ['l07.arrows', 'l08.front.>']] },
    units: [
      { id: 'inf', kind: 'infantry', name: 'Infantry', team: 'rome', at: 'l04.army' },
      { id: 'hop', kind: 'elite', name: 'Hoplites', team: 'carthage', at: 'l05.Greeks,' },
      { id: 'arch', kind: 'archers', name: 'Archers', team: 'rome', at: 'l07.arrows' },
    ],
    places: [
      { id: 'pass', letter: 'A', glyph: 'pass', name: 'Thermopylae', at: 'l04.Thermopylae,', pos: [CX + 22, 24], y: 2, ldy: 0.05 },
      { id: 'mountains', letter: 'B', glyph: 'mountain', name: 'The mountains', at: 'l04.mountains', pos: [-80, -20], y: 4, label: false },
      { id: 'sea', letter: 'C', glyph: 'sea', name: 'The sea', at: 'l04.sea', pos: [70, 0], y: 1, label: false },
      { id: 'path', letter: 'D', glyph: 'trail', name: 'The hidden path', at: 'l11.path', pos: HIDDEN[3], y: 4 },
    ],
    focus: [
      { entry: 'arch', at: 'l07.arrows', until: 'l07.sun.>' }, { entry: 'hop', at: 'l08.wall', until: 'l08.front.>' },
      { entry: 'persia', at: 'l15.Persians', until: 'l15.won.>' }, { entry: 'greeks', at: 'l16.Greek', until: 'l16.good.>' },
    ],
    scale: { unitM: 4, show: [['l04.A#1', 'l05']] },
  },

  labels: [
    { at: 'l05.Leonidas', until: 'l05.300', text: 'LEONIDAS', block: 'w1', team: 'carthage', dx: -0.1, dy: -0.12 },
    { at: 'l06.Xerxes', until: 'l06.expecting', text: 'XERXES', block: 'xerxes', team: 'rome', dx: 0.08, dy: -0.1 },
    { at: 'l07.Spartan', until: 'l08', text: 'DIENEKES', block: 'w1', team: 'carthage', dx: 0.08, dy: -0.14 },
    { at: 'l09.Immortals,', until: 'l09.Herodotus', text: 'THE IMMORTALS', block: 'imm', team: 'rome', dx: 0.08, dy: -0.12 },
    { at: 'l09.king', until: 'l10', text: 'XERXES', block: 'xerxes', team: 'rome', dx: 0.08, dy: -0.14 },
    { at: 'l11.named', until: 'l11.hidden', text: 'EPHIALTES', block: 'eph', dx: 0.06, dy: -0.12 },
    { at: 'l17.stone', until: 'l17.Go', text: 'EPITAPH OF SIMONIDES', pos: [6, 48], y: 4, dx: 0.12, dy: -0.12 },
    { at: 'l13.stayed', until: 'l13.700', text: 'LEONIDAS', block: 'w1', team: 'carthage', dx: -0.1, dy: -0.12 },
  ],

  counters: [
    { at: 'l05.300', until: 'l06', block: 'w1', team: 'carthage', from: 0, to: 300, countDur: 0.9, step: 10, suffix: 'SPARTANS', dx: 0.1, dy: -0.14 },
    { at: 'l13.700', until: 'l14', block: 'thesp', team: 'carthage', from: 0, to: 700, countDur: 0.9, step: 10, suffix: 'THESPIANS', dx: 0.12, dy: -0.14 },
  ],

  icons: [],
  markers: [{ id: 'stele', at: 'l17.stone', until: 170, pos: [6, 48], y: 1, glyph: 'stele', team: [0.15, 0.33, 0.74], label: false, size: 0.07 }],

  arrows: [
    { at: 'l04.narrow#1', dur: 0.8, ease: 'out', team: 'ink', width: 1.6, path: [[-50, 8], [-24, 8]], lift: 5, hide: 'l04.giant', head: true },
    { at: 'l04.narrow#1', dur: 0.8, ease: 'out', team: 'ink', width: 1.6, path: [[42, 8], [18, 8]], lift: 5, hide: 'l04.giant', head: true },
    { at: 'l06.run', dur: 0.9, ease: 'out', team: 'carthage', width: 3, style: 'dash', path: [[CX, 60], [CX - 6, 100], [CX - 16, 140]], lift: 5, hide: 'l06.not.', head: true },
    { at: 'l09.elite', dur: 1.6, ease: 'out', team: 'rome', width: 2.6, path: [[CX, -80], [CX, 4]], lift: 5, hide: 'l09.through.>', head: true },
    { id: 'hidden', at: 'l11.hidden', until: 'l11.Greeks.>', ease: 'cam', team: 'rome', style: 'dash', width: 2.8, path: HIDDEN, lift: 7, hide: 'l13.sent' },
    { at: 'l13.surrounded.', dur: 0.8, ease: 'out', team: 'rome', width: 3, path: [[-60, 150], [CX - 6, 80]], lift: 5, hide: 'l13.He#2', head: true },
    { at: 'l13.surrounded.+0.1', dur: 0.8, ease: 'out', team: 'rome', width: 3, path: [[CX, -70], [CX, -6]], lift: 5, hide: 'l13.He#2', head: true },
    { at: 'l13.sent', dur: 1.2, ease: 'out', team: 'carthage', width: 4, path: [[CX, 104], [20, 160], [40, 230]], lift: 5, hide: 'l13.He#2', head: true },
    { at: 'l14.surrounded', dur: 0.9, ease: 'out', team: 'rome', width: 3.6, path: [[CX, -50], [CX, 6]], lift: 5, hide: 'l14.fought', head: true },
    { at: 'l14.surrounded', dur: 0.9, ease: 'out', team: 'rome', width: 3.6, path: [[CX, 130], [CX, 74]], lift: 5, hide: 'l14.fought', head: true },
  ],

  volleys: [0, 1, 2, 3, 4].map((k) => ({ at: `l07.arrows+${(k * 0.5).toFixed(1)}`, dur: 1.0, from: { block: 'arch' }, to: [CX, 30, 12], n: 70, flight: 1.5, arc: 70, spread: 0.35, team: 'rome' })),

  cards: [
    { at: 0, until: 0.9, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 12.95, until: 17.3, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF THERMOPYLAE', size: 0.072, y: 0.45, delay: 0.1, pop: false, weight: 600, track: 0.12 },
      { text: '480 BC', size: 0.056, y: 0.575, delay: 1.1, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.56 }, { y: 0.65, w: 0.56 }] },
    // night: a blue scrim over the low sun while the Immortals climb (a change of time, no stars, no clip art)
    { at: 'l12', until: 'l13', scrim: 0.5, scrimCenter: 'rgba(12,20,48,0.6)', fadeIn: 0.8, fadeOut: 1.4, lines: [] },
    // the epitaph, line by line on the words (154.21 Go, 155.61 passerby, 156.47 that, 158.97 we)
    { at: 'l17.Go-0.1', until: 159.71, scrim: 0.86, scrimCenter: 'rgba(16,8,4,0.75)', fadeIn: 0.8, fadeOut: 0.5, lines: [
      { text: 'GO TELL THE SPARTANS,', size: 0.058, y: 0.34, delay: 0.1, pop: false, weight: 600, track: 0.1 },
      { text: 'PASSER BY,', size: 0.058, y: 0.46, delay: 1.5, pop: false, weight: 600, track: 0.1, colorTop: '#f3d9a0', colorBottom: '#d9a441' },
      { text: 'THAT HERE, OBEYING THEIR ORDERS,', size: 0.048, y: 0.58, delay: 2.36, pop: false, weight: 600, track: 0.08 },
      { text: 'WE LIE.', size: 0.08, y: 0.72, delay: 4.86, pop: false, weight: 600, track: 0.14, colorTop: '#fff0c4', colorBottom: '#e8b94f' } ], ornaments: [{ y: 0.26, w: 0.56 }, { y: 0.82, w: 0.56 }] },
    { at: 159.913, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.88, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Thermopylae, 480 BC', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],
};
