// The Battle of Hattin (1187): Battle Map v2 spec (engine: films/lib/battlemap/SPEC.md; scene list and reasons: NOTES.md).
// Teams are colours only, no religious badges: the crusaders are red ('rome'), Saladin's army is blue ('carthage').
// Main stage: the hills of Galilee, 1 unit about 100 m (x east, z south): Saffuriya far west, the dry plateau, the Horns of Hattin (two hills
// and a saddle), the springs north of them, Tiberias and the Sea of Galilee in the east. Stage `lev`: the Levant, 1 unit about 1.5 km.
// Film-side: kinds.js (flame, pavilion, horse-archer symbol), fx.js (the brush fire, the falling tent, heat veil, drifting smoke, night, regions).
const CRU = { team: 'rome' }, SAL = { team: 'carthage' };

const SAFF = [-200, 45], TIB = [256, 34], CAMP = [95, 35];
const HORN_A = [158, 28], HORN_B = [194, 28], SADDLE = [176, 28], SPRING = [182, -34];

// ------------------------------------------------------------------ Galilee
const world = {
  seed: 1187, size: [900, 560], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 232, elevation: 36 }, sunEve: { azimuth: 262, elevation: 6 },
  style: { contour: 2, pxPerUnit: 4.4, palette: [[-8, [0.70, 0.62, 0.40]], [0, [0.82, 0.72, 0.46]], [6, [0.86, 0.72, 0.44]], [14, [0.82, 0.66, 0.42]], [26, [0.74, 0.60, 0.42]], [40, [0.68, 0.59, 0.52]]], paletteSoft: 5 },
  features: [
    { type: 'undulate', amp: 5, scale: 110 }, { type: 'undulate', amp: 1.4, scale: 34 },
    { type: 'hill', at: [-330, -120], r: [190, 140], h: 30, rough: 0.2, crag: 0.1 }, { type: 'hill', at: [-300, 180], r: [210, 120], h: 26, rough: 0.2 },
    { type: 'hill', at: [60, -200], r: [200, 90], h: 26, rough: 0.2 }, { type: 'hill', at: [40, 200], r: [170, 80], h: 22, rough: 0.2 },
    { type: 'hill', at: [400, -200], r: [160, 100], h: 22 }, { type: 'hill', at: [-120, 110], r: [60, 34], h: 10, rot: 20 }, { type: 'hill', at: [-30, -70], r: [50, 26], h: 9, rot: -15 },
    // the Horns of Hattin: two steep peaks (an old volcano) with a saddle between them
    { type: 'hill', at: HORN_A, r: [24, 20], h: 11, rough: 0.12, crag: 0.05, power: 0.6 }, { type: 'hill', at: HORN_B, r: [24, 20], h: 10, rough: 0.12, crag: 0.05, power: 0.6 },
    { type: 'ridge', path: [HORN_A, HORN_B], w: 16, h: 4, rough: 0.1 },
    { type: 'flat', at: CAMP, r: 46, level: 5, soft: 34, amount: 0.92 },
    { type: 'lake', poly: [[268, -60], [290, -85], [335, -95], [380, -75], [405, -30], [412, 25], [400, 80], [372, 125], [335, 145], [298, 135], [272, 108], [262, 70], [259, 34], [262, -5], [264, -35]], shelf: 30, beach: 6, depth: 7 },
    { type: 'river', name: 'springs', path: [[168, -60], [178, -44], [190, -30], [204, -24]], w: 3.2, depth: 0.8, bank: 3, meander: 1 },
    { type: 'woods', at: [182, -48], r: [10, 6] }, { type: 'woods', at: [-250, 0], r: [30, 16] }, { type: 'woods', at: [330, -150], r: [30, 18] },
    { type: 'farms', rect: [-245, 90, 60, 40, 6], cell: [14, 10], skip: 0.2 }, { type: 'farms', rect: [240, 0, 18, 50, 0], cell: [10, 10], skip: 0.2 },
    { type: 'road', path: [[-260, 50], [-200, 46], [-100, 38], [0, 34], [95, 33], [205, 36], [256, 36]], w: 2.0, meander: 3 },
  ],
};

// ------------------------------------------------------------------ the Levant (second stage)
const JER = [45, 109], DAM = [112, -18];
const EGYPT = [[-380, 160], [-286, 152], [-250, 142], [-215, 132], [-185, 128], [-167, 137], [-150, 134], [-137, 148], [-80, 148], [-30, 142], [-2, 130], [10, 150], [60, 150], [100, 160], [150, 170], [150, 320], [-380, 320]];
const SYRIA = [[130, -292], [380, -292], [380, 170], [150, 170], [100, 160], [60, 150], [70, 110], [76, 60], [80, 10], [85, 0], [95, -40], [112, -100], [130, -180]];
const CRU_N = [[60, -292], [130, -292], [130, -180], [112, -100], [95, -40], [85, 0], [43, -1], [50, -20], [62, -48], [84, -87], [84, -110], [80, -168], [84, -190], [88, -215], [70, -250]];
const CRU_S = [[85, 0], [80, 10], [76, 60], [70, 110], [60, 150], [10, 150], [-2, 130], [6, 112], [16, 89], [26, 56], [35, 24], [43, -1]];
const lev = {
  world: {
    seed: 1099, size: [760, 640], res: 1, base: 0, meshStep: 2.5, sun: { azimuth: 245, elevation: 34 }, sunEve: { azimuth: 284, elevation: 10 },
    style: { contour: 4, pxPerUnit: 5.6, palette: [[-6, [0.80, 0.70, 0.46]], [1, [0.90, 0.80, 0.54]], [6, [0.86, 0.74, 0.48]], [14, [0.76, 0.68, 0.44]], [26, [0.72, 0.60, 0.42]], [44, [0.70, 0.64, 0.58]]], paletteSoft: 5 },
    features: [
      { type: 'undulate', amp: 5, scale: 100 },
      { type: 'mountains', path: [[92, -112], [80, -72], [72, -32]], w: 13, h: 22, ridged: 0.7, scale: 30, edge: 9 },
      { type: 'mountains', path: [[108, -90], [100, -48], [98, -18]], w: 9, h: 18, ridged: 0.7, scale: 30, edge: 7 },
      { type: 'hill', at: [48, 100], r: [16, 40], h: 8 }, { type: 'hill', at: [150, 120], r: [60, 80], h: 10 }, { type: 'hill', at: [100, -200], r: [60, 40], h: 14 },
      { type: 'sea', poly: [[-352, -292], [60, -292], [70, -250], [88, -215], [84, -190], [80, -168], [84, -110], [84, -87], [62, -48], [50, -20], [43, -1], [35, 24], [26, 56], [16, 89], [6, 112], [-2, 130], [-30, 142], [-80, 148], [-137, 148], [-150, 134], [-167, 137], [-185, 128], [-215, 132], [-250, 142], [-286, 152], [-352, 170]], shelf: 24, depth: 8 },
      { type: 'river', name: 'Nile', path: [[-205, 300], [-205, 255], [-200, 215]], w: 5, depth: 1.5, meander: 4 },
      { type: 'river', name: 'Damietta', path: [[-200, 215], [-178, 178], [-167, 140]], w: 4, depth: 1.2, meander: 3 },
      { type: 'river', name: 'Rosetta', path: [[-200, 215], [-232, 182], [-262, 156]], w: 4, depth: 1.2, meander: 3 },
      { type: 'river', name: 'Jordan', path: [[75, -10], [68, 12], [68, 46], [63, 92], [58, 122]], w: 2.2, depth: 0.8, meander: 2 },
      { type: 'lake', at: [67, 34], r: [6, 8], shelf: 5, beach: 2, depth: 2 }, { type: 'lake', at: [57, 142], r: [6, 18], shelf: 5, beach: 2, depth: 2 },
      { type: 'woods', at: [64, -70], r: [10, 24], rot: 10 },
    ],
  },
  ambient: { wind: [-1, 0.2], gusts: 0.4, flow: { dir: [0.3, 1], speed: 0.6, glint: 1.2 },
    birds: [{ center: [-120, 40], r: 40, h: 22, n: 6, speed: 6 }, { center: [150, 60], r: 30, h: 22, n: 5, speed: 5, dir: -1 }] },
  regions: [
    { at: 'l02.Egypt', until: 'l03', poly: EGYPT, team: 'carthage' }, { at: 'l02.Syria.', until: 'l03', poly: SYRIA, team: 'carthage' },
    { at: 'l02.crusaders', until: 'l03', poly: [...CRU_N.slice(0, 6), ...CRU_S.slice(1), ...CRU_N.slice(6)], team: 'rome' },
    { at: 'l13', until: 170, poly: EGYPT, team: 'carthage', fadeIn: 0.01 }, { at: 'l13', until: 170, poly: SYRIA, team: 'carthage', fadeIn: 0.01 },
    { at: 'l13', until: 170, poly: CRU_N, team: 'rome', fadeIn: 0.01 }, { at: 'l13', until: 'l13.Jerusalem.', poly: CRU_S, team: 'rome', fadeIn: 0.01, fadeOut: 0.6 },
    { at: 'l13.Jerusalem.', until: 170, poly: CRU_S, team: 'carthage', fadeIn: 0.8 },
  ],
  blocks: {
    salL: { ...SAL, kind: 'cavalry', x: DAM[0], z: DAM[1], heading: 220, len: 14, dep: 8, hidden: true, bannerScale: 1.8, figScale: 1.4 },
    ricL: { ...CRU, kind: 'cavalry', x: -150, z: -160, heading: 120, len: 14, dep: 8, hidden: true, bannerScale: 1.8, figScale: 1.4 },
  },
  moves: [
    { block: 'salL', at: 'l02.Sultan', dur: 0.8, appear: true },
    { block: 'salL', at: 'l13.Saladin', until: 'l13.Jerusalem.>', path: [[100, 20], [74, 66], [56, 100]], ease: 'cam' },
    { block: 'ricL', at: 'l14.new', dur: 0.8, appear: true },
    { block: 'ricL', at: 'l14.crusade', until: 'l14.Lionheart,>', path: [[-90, -100], [-30, -40], [20, 16]], ease: 'cam' },
  ],
  arrows: [
    { at: 'l02.Europe', until: 'l02.Jerusalem', ease: 'cam', team: 'rome', style: 'dash', width: 2.6, path: [[-320, -270], [-210, -150], [-100, -60], [12, 16]], lift: 4, hide: 'l02.string' },
    { at: 'l13.Saladin', until: 'l13.Jerusalem.', ease: 'cam', team: 'carthage', width: 3.4, path: [[112, -10], [100, 20], [74, 66], [56, 96]], lift: 4, hide: 'l14' },
    { id: 'eu2', at: 'l14.Europe', until: 'l14.Richard', ease: 'cam', team: 'rome', style: 'dash', width: 2.6, path: [[-320, -270], [-210, -170], [-120, -110], [-40, -40], [16, 14]], lift: 4, hide: 'l15' },
    { at: 'l14.but', until: 'l14.stayed', ease: 'out', team: 'rome', style: 'dash', width: 2.4, head: false, path: [[36, 30], [40, 60], [44, 80]], lift: 4, hide: 'l15' },
  ],
  icons: [
    { follow: 'eu2', at: 'l14.Europe', until: 'l14.Richard', icon: 'galley', team: 'rome', size: 22, minPx: 0.05, maxPx: 0.07 },
  ],
  markers: [
    { id: 'dam', at: 'l02.Saladin,', until: 'l03', pos: DAM, glyph: 'town', team: [0.15, 0.33, 0.74], label: 'DAMASCUS', labelDur: 3, size: 0.055, ldy: 0.05 },
    { id: 'cairo', at: 'l02.Egypt', until: 'l03', pos: [-202, 237], glyph: 'town', team: [0.15, 0.33, 0.74], label: 'CAIRO', labelDur: 3, size: 0.055, ldy: 0.05 },
    { id: 'jer', at: 'l02.Jerusalem', until: 'l03', pos: JER, glyph: 'town', team: [0.74, 0.12, 0.12], label: 'JERUSALEM', labelUntil: 'l03', size: 0.06, ldx: 0.07, align: 'left', ldy: 0.0 },
    ...[['ANTIOCH', 103, -218], ['TRIPOLI', 84, -88], ['TYRE', 43, -1], ['ACRE', 35, 24]].map(([n, x, z], k) => ({ id: 'c' + k, at: `l02.string+${k * 0.3}`, until: 'l03', pos: [x, z], glyph: 'fort', team: [0.74, 0.12, 0.12], label: n, labelUntil: 'l03', size: 0.04, ldx: -0.05, align: 'right', ldy: 0.0 })),
    { id: 'jer2', at: 'l13', until: 'l13.Jerusalem.', pos: JER, glyph: 'town', team: [0.74, 0.12, 0.12], size: 0.06 },
    { id: 'jer3', at: 'l13.Jerusalem.', until: 170, pos: JER, glyph: 'town', team: [0.15, 0.33, 0.74], label: 'JERUSALEM', labelUntil: 170, size: 0.06, ldx: 0.07, align: 'left', ldy: 0.0 },
    { id: 'acre2', at: 'l14', until: 170, pos: [35, 24], glyph: 'fort', team: [0.74, 0.12, 0.12], label: 'ACRE', labelUntil: 170, size: 0.045, ldx: -0.05, align: 'right', ldy: 0.0 },
    { id: 'hattin', at: 'l13', until: 170, pos: [70, 30], glyph: 'clash', label: 'HATTIN', labelUntil: 'l13.Jerusalem.', size: 0.04, ldy: 0.045 },
  ],
  labels: [
    { at: 'l02.Egypt', until: 'l03', text: 'EGYPT', pos: [-200, 250], leader: false, rule: false, team: 'carthage' },
    { at: 'l02.Syria.', until: 'l03', text: 'SYRIA', pos: [240, -120], leader: false, rule: false, team: 'carthage' },
    { at: 'l02.crusaders', until: 'l03', text: 'CRUSADER STATES', pos: [104, -150], dx: -0.16, dy: 0, leader: false, team: 'rome' },
    { at: 'l13.took', until: 'l13.And', text: '2 OCTOBER 1187', screen: [0.5, 0.86], big: true },
    { at: 'l14.Richard', until: 'l14.but', text: 'RICHARD THE LIONHEART', block: 'ricL', team: 'rome', dx: -0.04, dy: -0.12 },
    { at: 'l14.crusade', until: 'l14.Richard', text: '1191', screen: [0.5, 0.86], big: true },
  ],
};

// ------------------------------------------------------------------ the armies in Galilee
const S1X = 140;   // during the cold open the army is shown on its march (140 units east of Saffuriya); it is back in camp before S3
const ARMY = ['crus', 'kn', 'guy', 'raymond'];
const HA_C = [40, 36], HA_R = 58;
const near = (h, ref) => h + 360 * Math.round((ref - h) / 360);
const haStart = (k) => { const a = (k / 6) * Math.PI * 2; return { x: HA_C[0] + Math.cos(a) * HA_R, z: HA_C[1] + Math.sin(a) * HA_R, heading: (a * 180 / Math.PI + 180) % 360 }; };
const haH1 = (k) => near(270, haStart(k).heading + 340);
const ha = {}; for (let k = 0; k < 6; k++) ha['ha' + k] = { ...SAL, kind: 'light', figures: 'cavalry', ...haStart(k), len: 12, dep: 5, hidden: true, bannerScale: 1.0, banner: k % 2 === 0 };
const RING = ['salA.0.0', 'salA.1.0', 'salA.2.0', 'salA.3.0', 'salA.4.0', 'salA.0.1', 'salA.1.1', 'salA.2.1', 'salA.3.1', 'salA.4.1', 'ha0', 'ha1', 'ha2', 'ha3', 'ha4', 'ha5'];
const ringAng = (k) => (k / RING.length) * Math.PI * 2 + 0.3;
const ringPt = (a, R) => [SADDLE[0] + Math.cos(a) * R * 1.12, SADDLE[1] + Math.sin(a) * R];
// where each ring member stands when the ring starts to form (after the l09 moves): salA grid members and the horse-archer line
const salAPos = (id) => { const [, i, j] = id.split('.').map(Number); return [218 + (j === 0 ? 5.3 : -5.3), 33 - (i - 2) * 22.24]; };
const startPos = (id) => id.startsWith('ha') ? [150 + 14 * Number(id.slice(2)), -24] : salAPos(id);
// the path round the outside (radius 80) from where a member stands to its place in the ring, so no one walks through the crusaders
const ringPath = (id, k) => { const [sx, sz] = startPos(id); let a0 = Math.atan2(sz - SADDLE[1], (sx - SADDLE[0]) / 1.12), a1 = ringAng(k); while (a1 - a0 > Math.PI) a1 -= Math.PI * 2; while (a1 - a0 < -Math.PI) a1 += Math.PI * 2;
  const n = Math.max(1, Math.ceil(Math.abs(a1 - a0) / 0.45)); const P = []; for (let q = 0; q <= n; q++) P.push(ringPt(a0 + (a1 - a0) * q / n, 80)); P.push(ringPt(a1, 46)); return P; };

const blocks = {
  crus: { ...CRU, kind: 'infantry', x: SAFF[0] + S1X, z: SAFF[1], heading: 90, len: 40, dep: 20, grid: { cols: 4, ranks: 2, gap: 0.9 }, count: 20000, bannerScale: 0.95 },
  kn: { ...CRU, kind: 'cavalry', x: SAFF[0] + 22 + S1X, z: SAFF[1], heading: 90, len: 24, dep: 8, bannerScale: 0.9 },
  raymond: { ...CRU, kind: 'elite', x: SAFF[0] + 32 + S1X, z: SAFF[1] - 8, heading: 90, len: 6, dep: 5, bannerScale: 1.4 },
  guy: { ...CRU, kind: 'elite', x: SAFF[0] - 18 + S1X, z: SAFF[1], heading: 90, len: 8, dep: 6, bannerScale: 1.7 },
  salT: { ...SAL, kind: 'cavalry', x: 440, z: 150, heading: 270, len: 26, dep: 12, hidden: true, bannerScale: 1.4 },
  ...ha,
  salA: { ...SAL, kind: 'infantry', x: 218, z: 33, heading: 270, len: 110, dep: 20, grid: { cols: 5, ranks: 2, gap: 1.2 }, hidden: true, bannerScale: 1.0 },
  saladin: { ...SAL, kind: 'elite', x: 100, z: -6, heading: 270, len: 8, dep: 6, hidden: true, bannerScale: 2.0 },
};
const moves = [
  // S1: the army on its march into the hills (the cold open); far ahead, the Sultan's standard. Back to camp under the Levant map.
  { blocks: ARMY, at: 0, dur: 10.4, by: { x: 30 }, ease: 'linear' },
  { block: 'saladin', at: 'l00.Sultan', dur: 0.9, appear: true },
  { block: 'saladin', at: 10.8, dur: 0.5, vanish: true },
  { blocks: ARMY, at: 17, dur: 0.2, by: { x: -S1X - 30 }, ease: 'linear' },
  { block: 'saladin', at: 17, dur: 0.2, to: { x: 236, z: 30 }, ease: 'linear' },
  // S3: Saladin's horsemen ride round the south of the lake and fall on Tiberias
  { block: 'salT', at: 'l03.Saladin', dur: 0.8, appear: true },
  { block: 'salT', at: 'l03.attacked', until: 'l03.Galilee.>', path: [[400, 180], [340, 190], [292, 150], [266, 104], [250, 66]], ease: 'cam' },
  // S3 to S5: King Guy marches anyway; across the dry hills; the horse archers ride round them; stuck on the dry plateau
  { blocks: ARMY, at: 'l04.marched', until: 'l05>', by: { x: 230, z: -10 }, ease: 'inOut' },
  { blocks: ARMY, at: 'l06', until: 'l06>', by: { x: 20 }, ease: 'linear' },
  { blocks: ARMY, at: 'l07.By', until: 'l07.dry', by: { x: 45 }, ease: 'out' },
  ...Object.keys(ha).map((id) => ({ block: id, at: 'l06.Saladin\'s', dur: 0.5, stagger: 0.12, appear: true })),
  ...Object.keys(ha).map((id) => ({ block: id, at: 'l06.Saladin\'s+0.8', until: 'l06.blocking', wheel: { about: HA_C, deg: 340 }, ease: 'linear' })),
  ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l06.blocking', dur: 1.3, to: { x: 150, z: -2 + k * 15, heading: haH1(k) }, ease: 'inOut' })),
  { group: 'salA', at: 'l07.army', dur: 0.9, stagger: 0.08, appear: true }, { block: 'saladin', at: 'l07.army', dur: 0.9, appear: true },
  ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l07.army', dur: 1.4, to: { x: 196, z: 6 + k * 15 }, ease: 'inOut' })),
  // the night: the horse archers ride back along the line and set the grass alight; the smoke thins the crusader ranks
  ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l08.men', dur: 1.8, to: { x: 152, z: -2 + k * 15 }, ease: 'inOut' })),
  { blocks: ARMY, at: 'l08.coughing', dur: 2.0, fadeTo: 0.25, alphaTo: 0.95 },
  // S6: morning: the break-out toward the springs; the horse archers bar the way north
  { blocks: ARMY, at: 'l09.break', until: 'l09.springs,', by: { x: 42, z: -24 }, ease: 'inOut' },
  ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l09.break', dur: 1.6, to: { x: 150 + 14 * k, z: -24, heading: near(180, haH1(k)) }, ease: 'inOut' })),
  // the army breaks into pieces: some charge (and are lost), some flee up the hills with the king's tent
  ...[0, 1, 2, 3].flatMap((i) => [0, 1].map((j) => ({ block: `crus.${i}.${j}`, at: 'l10.pieces', dur: 1.0, by: { z: (i - 1.5) * 6, x: j ? 4 : -4 }, ease: 'out' }))),
  { blocks: ['crus.0.0', 'crus.1.0', 'crus.0.1', 'crus.1.1', 'kn', 'raymond'], at: 'l10.charged', dur: 1.6, stagger: 0.06, by: { x: 26, z: -22 }, ease: 'in' },
  { block: 'crus.2.0', at: 'l10.fled', dur: 2.0, to: { x: 160, z: 20, heading: 0 }, ease: 'inOut' }, { block: 'crus.2.1', at: 'l10.fled', dur: 2.0, to: { x: 162, z: 37, heading: 0 }, ease: 'inOut' },
  { block: 'crus.3.0', at: 'l10.fled', dur: 2.2, to: { x: 191, z: 20, heading: 0 }, ease: 'inOut' }, { block: 'crus.3.1', at: 'l10.fled', dur: 2.2, to: { x: 192, z: 37, heading: 0 }, ease: 'inOut' },
  { block: 'guy', at: 'l10.fled', dur: 2.2, to: { x: 176, z: 41, heading: 0 }, ease: 'inOut' },
  // the blue ring closes round the horns (round the outside, never through the crusaders), then tightens when the tent falls
  ...RING.map((id, k) => ({ block: id, at: 'l10.fled', until: 'l10.surrounded+0.3', path: ringPath(id, k), ease: 'inOut' })),
  ...RING.map((id) => ({ block: id, at: 'l10.surrounded', dur: 0.8, to: { scale: 0.8 }, ease: 'inOut' })),
  { blocks: ['crus.0.0', 'crus.1.0', 'crus.0.1', 'crus.1.1', 'kn', 'raymond'], at: 'l10.surrounded', dur: 1.6, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 },
  ...RING.map((id, k) => { const [x, z] = ringPt(ringAng(k), 38); return { block: id, at: 'l11.fell,', dur: 1.5, to: { x, z }, ease: 'inOut' }; }),
  { blocks: ['crus.2.0', 'crus.2.1', 'crus.3.0', 'crus.3.1'], at: 'l11.over.', dur: 1.8, stagger: 0.15, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 },
  { block: 'guy', at: 'l11.captured.', dur: 1.2, fadeTo: 0.5, alphaTo: 0.8 },
  // S7: the ring parts on the east and Saladin walks up to the king
  { block: 'ha5', at: 'l12.offered', dur: 1.2, by: { z: -8 }, ease: 'inOut' }, { block: 'salA.0.0', at: 'l12.offered', dur: 1.2, by: { z: 8 }, ease: 'inOut' },
  { block: 'saladin', at: 'l12.offered', until: 'l12.ice,', path: [[214, 32], [198, 34], [190, 38]], ease: 'cam' },
];

// ------------------------------------------------------------------ the edit: scenes, sets, shots (reasons in NOTES.md)
const scenes = [
  { id: 'S1', name: 'Lured', at: 0, job: 'a Sultan lures a whole army into the hills in summer, and waits for it to get thirsty', set: { time: [0.06, 0.1], haze: 1.45, cloud: 0.15 },
    shots: [
      { at: 0, why: 'cold open low over the dry hills at midday: an army marching into the heat', from: { target: [-20, 40], dist: 150, pitch: 12, yaw: 76, mm: 30 },
        moves: [{ until: 'l00.summer,>', to: { target: [0, 38], dist: 142 } }] },
      { at: 'l00.and', why: 'reverse angle from behind the Sultan\'s standard: he waits for the army to come to him', from: { target: [26, 4], dist: 122, pitch: 9, yaw: 262, mm: 35 },
        moves: [{ until: 10.4, to: { dist: 114 } }] },
      { at: 10.4, why: 'crane up to the map of the hills under the title', from: { target: [30, 30], width: 600, pitch: 50, yaw: 0, mm: 35 },
        moves: [{ until: 'l02', to: { pitch: 80, width: 640 }, ease: 'camSoft' }] },
    ] },
  { id: 'S2', name: 'Saladin', at: 'l02', stage: 'lev', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'who the Sultan is, and who holds Jerusalem', set: { time: 0.05, haze: 1.0 },
    shots: [
      { at: 'l02', why: 'change of world: the Levant; Saladin rules Egypt and Syria', from: { target: [-40, 30], width: 640, pitch: 56, yaw: 0, mm: 35 },
        moves: [{ until: 'l02.Syria.>', to: { target: [-20, 20], width: 610 } }] },
      { at: 'l02.For', why: 'lower along the coast: the crusader states, Jerusalem and the string of castles', from: { target: [40, 20], width: 360, pitch: 40, yaw: 345, mm: 35 },
        moves: [{ until: 'l02.coast.>', to: { target: [50, -30], width: 380 } }] },
    ] },
  { id: 'S3', name: 'The bait', at: 'l03', transition: { type: 'dissolve', dur: 0.8 }, job: 'Saladin attacks Tiberias as bait; the lords say do not go; King Guy marches anyway', set: { time: [0.04, 0.0], haze: 1.2, cloud: 0.25 },
    shots: [
      { at: 'l03', why: 'back in Galilee: Saladin swings round the lake and attacks Tiberias', from: { target: [270, 70], width: 380, pitch: 50, yaw: 350, mm: 35 },
        moves: [{ until: 'l03.Galilee.>', to: { target: [266, 56], width: 350 } }] },
      { at: 'l03.It', why: 'wide to the whole map: the bait, and the army at Saffuriya it is meant for', from: { target: [20, 40], width: 720, pitch: 58, yaw: 0, mm: 35 },
        moves: [{ until: 'l03>', to: { width: 690 } }] },
      { at: 'l04', why: 'low in the crusader camp at Saffuriya: the lords say do not go', from: { target: [-196, 42], dist: 80, pitch: 16, yaw: 120, mm: 40 },
        moves: [{ until: 'l04.go.>', to: { dist: 72 } }] },
      { at: 'l04.It\'s', why: 'high along the road east: July, and no water between here and the lake', from: { target: [20, 40], width: 560, pitch: 30, yaw: 88, mm: 35 },
        moves: [{ until: 'l04.way.>', by: { target: [30, 0] } }] },
      { at: 'l04.Even', why: 'Tiberias: the lord\'s wife trapped inside', from: { target: [252, 40], dist: 100, pitch: 26, yaw: 300, mm: 35 },
        moves: [{ until: 'l04.go.#1>', to: { dist: 90 } }] },
      { at: 'l04.King', why: 'back in camp: King Guy gives the order anyway', from: { target: [-186, 44], dist: 120, pitch: 22, yaw: 60, mm: 35 },
        moves: [{ until: 'l05', to: { target: [-170, 44] } }] },
    ] },
  { id: 'S4', name: 'Across the dry hills', at: 'l05', job: '20,000 men in armour march into the heat, harried all day and cut off from water', set: { time: [0.0, 0.18], haze: 1.35, cloud: 0.12 },
    shots: [
      { at: 'l05', why: 'low beside the road: the column marches past, into the heat', from: { target: [-60, 40], dist: 210, pitch: 15, yaw: 12, mm: 35 },
        moves: [{ until: 'l05.July.>', by: { target: [40, 0] } }] },
      { at: 'l06', why: 'high over the column: Saladin\'s horse archers ride round it, shooting', from: { target: [44, 36], width: 260, pitch: 58, yaw: 0, mm: 35 },
        moves: [{ until: 'l06.and', to: { yaw: 30, target: [56, 36] }, ease: 'camLong' }] },
      { at: 'l06.and', why: 'low from the east, behind the horse archers: the way to water is blocked', from: { target: [118, 30], dist: 150, pitch: 16, yaw: 270, mm: 35 },
        moves: [{ until: 'l06.water.>', to: { dist: 144 } }] },
    ] },
  { id: 'S5', name: 'The dry plateau', at: 'l07', job: 'stuck on a dry plateau in sight of the lake; at night the grass burns and the smoke blows into the camp', set: { time: [0.55, 1.0], haze: 1.3 },
    shots: [
      { at: 'l07', why: 'high over the plateau at evening: stuck, and Saladin\'s army arrives between them and the lake', from: { target: [168, 34], width: 400, pitch: 60, yaw: 10, mm: 35 },
        moves: [{ until: 'l07.lake.>', to: { target: [176, 34], width: 420 } }] },
      { at: 'l07.They', why: 'low over the crusaders\' shoulders: the water they can see and cannot reach', from: { target: [230, 34], dist: 165, pitch: 8, yaw: 90, mm: 35 },
        moves: [{ until: 'l07.it.>', to: { dist: 155 } }] },
      { at: 'l08', why: 'night: low along the dry grass as Saladin\'s men set it alight', from: { target: [140, 30], dist: 120, pitch: 14, yaw: 350, mm: 35 },
        moves: [{ until: 'l08.grass.>', to: { dist: 112 } }] },
      { at: 'l08.smoke', why: 'high and wide: the smoke blows straight into the crusader camp', from: { target: [118, 36], width: 240, pitch: 56, yaw: 290, mm: 35 },
        moves: [{ until: 'l08.coughing.>', to: { yaw: 278 }, ease: 'camLong' }] },
    ] },
  { id: 'S6', name: 'The Horns of Hattin', at: 'l09', climax: true, job: 'the break-out fails: the army breaks, the king\'s tent is surrounded on the Horns and falls', set: { time: [0.12, 0.3], haze: 1.15, cloud: 0.3 },
    shots: [
      { at: 'l09', why: 'morning, wide and high: the break-out toward the springs by the two hills', from: { target: [150, 8], width: 380, pitch: 50, yaw: 20, mm: 35 },
        moves: [{ until: 'l09.Hatim.>', to: { target: [162, 8], width: 350 } }] },
      { at: 'l10', why: 'the decisive moment from above: the army breaks into pieces and the ring closes on the horns', from: { target: [166, 18], width: 270, pitch: 86, yaw: 0, mm: 35 },
        moves: [{ until: 'l10.King', to: { width: 250, target: [172, 22] } }] },
      { at: 'l10.King', why: 'closer and lower, circling the saddle: King Guy\'s red tent, surrounded, and it falls', from: { target: [176, 32], dist: 100, pitch: 22, yaw: 150, mm: 40 },
        moves: [{ until: 'l11.over.>', to: { yaw: 186, dist: 92 }, ease: 'camLong' }] },
      { at: 'l11.King', why: 'low on the king as he is taken', from: { target: [176, 42], dist: 56, pitch: 16, yaw: 340, mm: 45 },
        moves: [{ until: 'l12', to: { dist: 52 } }] },
    ] },
  { id: 'S7', name: 'A cup of water', at: 'l12', job: 'Saladin offers the king iced water: his life will be spared', set: { time: [0.7, 0.85], haze: 1.2 },
    shots: [
      { at: 'l12', why: 'low at dusk: Saladin walks up through the ring to the exhausted king', from: { target: [186, 36], dist: 80, pitch: 12, yaw: 330, mm: 40 },
        moves: [{ until: 'l12.ice,>', to: { dist: 70 } }] },
      { at: 'l12.a#1', why: 'pull back over the Horns: a life spared, the battle over', from: { target: [180, 32], dist: 140, pitch: 30, yaw: 300, mm: 35 },
        moves: [{ until: 'l13', to: { dist: 156 } }] },
    ] },
  { id: 'S8', name: 'Jerusalem', at: 'l13', stage: 'lev', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'why it mattered: Jerusalem falls to Saladin without a massacre and stays his', set: { time: 0.15, haze: 1.05 },
    shots: [
      { at: 'l13', why: 'change of world: three months later, Saladin marches on Jerusalem', from: { target: [80, 40], width: 330, pitch: 52, yaw: 0, mm: 35 },
        moves: [{ until: 'l13.And', to: { target: [64, 76], width: 300 } }] },
      { at: 'l13.And', why: 'closer and lower on the city: taken without a massacre, unlike 1099', from: { target: [44, 106], width: 150, pitch: 32, yaw: 330, mm: 35 },
        moves: [{ until: 'l13.massacre.>', to: { width: 140 } }] },
      { at: 'l14', why: 'wide over the sea: a new crusade from Europe under Richard the Lionheart, and Jerusalem stays', from: { target: [-120, -90], width: 560, pitch: 50, yaw: 10, mm: 35 },
        moves: [{ until: 'l14.hands.>', to: { target: [-30, 0], width: 600 } }] },
    ] },
  { id: 'S9', name: 'The lesson', at: 'l15', transition: { type: 'dissolve', dur: 1.0 }, job: 'the lesson, on the hills where it happened', set: { time: 0.08, haze: 1.4 },
    shots: [
      { at: 'l15', why: 'back over the dry hills and the Horns, empty now: the lesson', from: { target: [60, 34], width: 560, pitch: 40, yaw: 80, mm: 35 },
        moves: [{ until: 137.3, to: { target: [100, 32], pitch: 50, width: 600 }, ease: 'camLong' }] },
    ] },
];

// ------------------------------------------------------------------ the legend (motion-graphics frame)
const legend = {
  title: { text: 'BATTLE OF HATTIN', sub: '4 July 1187', at: 'l02.Saladin,' },
  show: [['l02.Saladin,', 'l15.suit.>']],
  sides: [
    { id: 'saladin', team: 'carthage', name: 'EGYPT AND SYRIA', commander: 'Saladin', banner: 'banner', at: 'l02.Saladin,' },
    { id: 'crusaders', team: 'rome', name: 'CRUSADERS', commander: 'King Guy of Jerusalem', commanderAt: 'l04.King', banner: 'vexillum', at: 'l02.crusaders', strength: 20000, strengthAt: 'l05.20', dimAt: 'l11.over.' },
  ],
  key: { show: [['l03.Tiberius', 'l04.King'], ['l05.20', 'l07.They'], ['l09.springs,', 'l11.over.>']] },
  units: [
    { id: 'inf', kind: 'infantry', name: 'Infantry', teams: ['rome', 'carthage'], at: 'l05.crusaders' },
    { id: 'kn', kind: 'cavalry', name: 'Knights in heavy armour', team: 'rome', at: 'l05.heavy' },
    { id: 'ha', kind: 'cavalry', glyph: 'u-horse-archers', name: 'Horse archers', team: 'carthage', at: 'l06.horse' },
  ],
  places: [
    { id: 'tib', letter: 'A', glyph: 'town', name: 'Tiberias', at: 'l03.Tiberius', pos: TIB, team: 'rome', ldx: -0.06, align: 'right', ldy: 0.0 },
    { id: 'sea', letter: 'B', glyph: 'sea', name: 'Sea of Galilee', at: 'l03.Sea', pos: [330, 20], ldy: 0.05 },
    { id: 'spring', letter: 'C', glyph: 'river', name: 'The springs', at: 'l09.springs,', pos: SPRING, ldy: 0.05 },
    { id: 'horns', letter: 'D', glyph: 'hill', name: 'Horns of Hattin', at: 'l09.Horns', pos: [176, 6], y: 6, label: 'HORNS OF HATTIN', labelDur: 3.5 },
  ],
  focus: [
    { entry: 'ha', at: 'l06.horse', until: 'l06.blocking' }, { entry: 'sea', at: 'l07.lake.', until: 'l07.it.>' },
    { entry: 'saladin', at: 'l14.but', until: 'l14.hands.>' },
  ],
  scale: { unitM: 100, show: [['l03', 'l11.captured.>']] },
};

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.06, grain: 0.03, vignette: 0.30 } },
  world, stages: { lev }, blocks, moves, scenes, legend,
  msaaOn: [[0, 'l00.and'], ['l11.King', 'l12'], ['l12', 'l12.a#1']],
  ambient: {
    wind: [-1.2, 0.25], gusts: 0.7, flow: { dir: [0.3, 1], speed: 0.5, glint: 1.2 },
    camps: [{ pos: [-250, 46], size: [40, 52], team: 'rome', style: 'grid', fires: 3, people: 12 }, { pos: [330, 200], size: [60, 36], team: 'carthage', style: 'scatter', tents: 26, fires: 4, people: 10, rot: 10 }],
    walkers: [{ path: [[-260, 50], [-200, 46], [-100, 38], [0, 34], [95, 33], [205, 36], [256, 36]], n: 5, gap: 6, speed: 1.4, kind: 'light', team: 'neutral', until: 'l04.marched' }, { path: [[256, 36], [205, 36], [95, 33]], n: 3, gap: 6, speed: 1.2, kind: 'light', team: 'neutral', until: 'l03.attacked' }],
    smoke: [{ pos: TIB, n: 12, alpha: 0.24, height: 12, at: 'l03.attacked', until: 'l05' }, { pos: [176, 30], n: 10, alpha: 0.18, height: 10, at: 'l10.surrounded', until: 'l13' }],
    birds: [{ center: [-120, 0], r: 60, h: 34, n: 6, speed: 6 }, { center: CAMP, r: 34, h: 30, n: 5, speed: 4, dir: -1, at: 'l07', until: 'l08' }, { path: [[400, 160], [-200, -40]], n: 5, h: 40, speed: 9 }, { center: SADDLE, r: 40, h: 34, n: 5, speed: 4, at: 'l11', until: 'l13' }],
    fires: [{ path: [[136, -8], [143, 12], [140, 32], [146, 52], [141, 72], [147, 92]], at: 'l08.fire', spread: 3.2, until: 'l09.In+1.5', n: 34, sc: 2.6, width: 6, smoke: 0.34, smokeH: 14 }],
    pavilions: [{ pos: [176, 30], team: 'rome', sc: 6.5, at: 'l10.red', fallAt: 'l11.fell,', fallDur: 0.9 }],
  },
  heat: [{ at: 0, until: 'l00.thirsty.>', strength: 0.9, fadeIn: 0.01 }, { at: 'l05', until: 'l07.By', strength: 1.0 }, { at: 'l15', until: 140, strength: 0.8 }],
  smoke: [{ at: 'l08.smoke', until: 'l09.In', from: [136, -6, 146, 92], wind: [-52, 6], n: 60, size: 7.5, rise: 12, speed: 0.12, alpha: 0.5, fadeIn: 1.4, fadeOut: 1.0 }],
  dim: [{ at: 'l08', until: 'l09.In', alpha: 0.48, color: 'rgb(10,14,40)', fadeIn: 1.2, fadeOut: 1.4 }],
  arrows: [
    { at: 'l03.attacked', until: 'l03.Galilee.', ease: 'cam', team: 'carthage', width: 4, path: [[400, 180], [340, 190], [292, 150], [266, 104], [252, 70]], lift: 5, hide: 'l03.It' },
    { at: 'l03.rescue', until: 'l03.it.>', ease: 'cam', team: 'rome', style: 'dash', width: 3, path: [[-186, 44], [-100, 38], [0, 34], [95, 33], [205, 36], [240, 36]], lift: 5, hide: 'l04.Even' },
    { at: 'l04.marched', until: 'l05.dry', ease: 'cam', team: 'rome', width: 5, path: [[-180, 44], [-110, 40], [-20, 36], [50, 35]], lift: 5, hide: 'l06' },
    { at: 'l06.long,', until: 'l06.rode', ease: 'cam', team: 'carthage', width: 3, style: 'dash', path: Array.from({ length: 14 }, (_, i) => { const a = (i / 13) * Math.PI * 1.9 - 0.2; return [HA_C[0] + Math.cos(a) * HA_R, HA_C[1] + Math.sin(a) * HA_R]; }), lift: 4, hide: 'l06.blocking' },
    { at: 'l07.see', until: 'l07.water,', ease: 'out', team: 'ink', style: 'dash', width: 1.8, path: [[112, 34], [190, 34], [262, 36]], lift: 6, hide: 'l08' },
    { at: 'l09.break', until: 'l09.springs,', ease: 'cam', team: 'rome', width: 5, path: [[110, 30], [132, 10], [158, -12], [176, -22]], lift: 5, hide: 'l10' },
    { at: 'l10.surrounded', dur: 1.4, ease: 'cam', team: 'gold', width: 1.6, style: 'dash', head: false, taper: 1, smooth: true, lift: 8, hide: 'l12',
      path: Array.from({ length: 17 }, (_, i) => ringPt(i / 16 * Math.PI * 2, 30)) },
  ],
  volleys: [
    ...Array.from({ length: 4 }, (_, k) => ({ at: `l06.shooting+${k * 0.45}`, dur: 0.7, from: { block: 'ha' + (k + 1) }, to: [60, 36, 16], n: 20, flight: 0.9, arc: 22, team: 'carthage' })),
    { at: 'l06.arrows', dur: 0.8, from: { block: 'ha3' }, to: [58, 36, 18], n: 22, flight: 0.9, arc: 22, team: 'carthage' },
  ],
  labels: [
    { at: 1.2, until: 'l00.Sultan', text: 'GALILEE, 1187', screen: [0.5, 0.86], big: true },
    { at: 'l00.Sultan', until: 'l00.and', text: 'SALADIN', block: 'saladin', team: 'carthage', dx: 0.04, dy: -0.12 },
    { at: 'l03.crusader', until: 'l04.It\'s', text: 'SAFFURIYA', pos: [-232, 70], leader: false, rule: false },
    { at: 'l04.lords', until: 'l04.It\'s', text: 'RAYMOND OF TRIPOLI', block: 'raymond', team: 'rome', dx: 0.06, dy: -0.12 },
    { at: 'l04.July.', until: 'l04.Even', text: '3 JULY 1187', screen: [0.5, 0.86], big: true },
    { at: 'l04.wife', until: 'l04.King', text: 'COUNTESS ESCHIVA', pos: TIB, y: 6, team: 'rome', dx: -0.1, dy: -0.12 },
    { at: 'l04.King', until: 'l05', text: 'KING GUY', block: 'guy', team: 'rome', dx: 0.04, dy: -0.12 },
    { at: 'l10.King', until: 'l11.King', text: 'KING GUY\'S TENT', pos: [176, 30], y: 8, team: 'rome', dx: 0.08, dy: -0.12 },
    { at: 'l11.over.', until: 'l12', text: '4 JULY 1187', screen: [0.5, 0.86], big: true },
    { at: 'l12.Saladin', until: 'l12.cup', text: 'SALADIN', block: 'saladin', team: 'carthage', dx: 0.06, dy: -0.12 },
  ],
  counters: [{ at: 'l05.20', until: 'l05.July.', block: 'crus', team: 'rome', from: 0, to: 20000, countDur: 1.1, step: 500, suffix: 'CRUSADERS', dy: -0.14 }],
  cards: [
    { at: 0, until: 0.8, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 'l01', until: 15.7, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF HATTIN', size: 0.08, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
      { text: '1187', size: 0.056, y: 0.575, delay: 1.0, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.5 }, { y: 0.65, w: 0.5 }] },
    { at: 137.35, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.8, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Hattin, 1187', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],
};
