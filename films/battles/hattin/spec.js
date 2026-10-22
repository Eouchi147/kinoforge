// The Battle of Hattin (1187): Battle Map spec. Times come from the cue words (see films/lib/battlemap/SPEC.md).
// Teams are colours only, no religious badges: the crusaders are red ('rome'), Saladin's army is blue ('carthage').
// Main stage: the hills of Galilee, 1 unit about 100 m. x east, z south. Saffuriya (crusader camp) far west, the Sea of Galilee and Tiberias in the east,
// between them the dry plateau (camp), the Horns of Hattin (two hills) and the springs just north of them.
// Stage `lev`: the Levant, 1 unit about 1.5 km (Egypt and Syria, the crusader states and their castles along the coast), full screen insets.
const CRU = { team: 'rome' }, SAL = { team: 'carthage' };
const L = (at, until, text, o = {}) => ({ at, until, text, ...o });
const I = (at, until, icon, o = {}) => ({ at, until, icon, ...o });

// key places on the Galilee map
const SAFF = [-200, 45];          // crusader camp at Saffuriya (start of the march)
const TIB = [256, 34];            // Tiberias, on the west shore of the lake
const CAMP = [95, 35];            // the dry plateau where the crusaders get stuck
const HORN_A = [158, 28], HORN_B = [194, 28], SADDLE = [176, 28];
const SPRING = [182, -30];

// ------------------------------------------------------------------ the world of the battle
const galilee = {
  seed: 1187, size: [900, 560], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 232, elevation: 36 }, sunEve: { azimuth: 262, elevation: 6 },
  style: { contour: 2, pxPerUnit: 4.4, palette: [[-8, [0.70, 0.62, 0.40]], [0, [0.82, 0.72, 0.46]], [6, [0.86, 0.72, 0.44]], [14, [0.82, 0.66, 0.42]], [26, [0.74, 0.60, 0.42]], [40, [0.68, 0.59, 0.52]]], paletteSoft: 5 },
  features: [
    { type: 'undulate', amp: 5, scale: 110 }, { type: 'undulate', amp: 1.4, scale: 34 },
    { type: 'hill', at: [-330, -120], r: [190, 140], h: 30, rough: 0.2, crag: 0.1 }, { type: 'hill', at: [-300, 180], r: [210, 120], h: 26, rough: 0.2 },
    { type: 'hill', at: [60, -200], r: [200, 90], h: 26, rough: 0.2 }, { type: 'hill', at: [40, 200], r: [170, 80], h: 22, rough: 0.2 },
    { type: 'hill', at: [400, -200], r: [160, 100], h: 22 }, { type: 'hill', at: [-120, 110], r: [60, 34], h: 10, rot: 20 }, { type: 'hill', at: [-30, -70], r: [50, 26], h: 9, rot: -15 },
    // the Horns of Hattin: two distinct hills with a saddle between them
    { type: 'hill', at: HORN_A, r: [21, 18], h: 17, rough: 0.1, crag: 0.1, power: 0.75 }, { type: 'hill', at: HORN_B, r: [21, 18], h: 17, rough: 0.1, crag: 0.1, power: 0.75 },
    { type: 'ridge', path: [HORN_A, HORN_B], w: 11, h: 8, rough: 0.1 },
    { type: 'flat', at: CAMP, r: 46, level: 5, soft: 34, amount: 0.92 },
    { type: 'lake', poly: [[268, -60], [290, -85], [335, -95], [380, -75], [405, -30], [412, 25], [400, 80], [372, 125], [335, 145], [298, 135], [272, 108], [262, 70], [259, 34], [262, -5], [264, -35]], shelf: 30, beach: 6, depth: 7 },
    { type: 'river', name: 'springs', path: [[168, -56], [178, -40], [190, -26], [204, -20]], w: 3.2, depth: 0.8, bank: 3, meander: 1 },
    { type: 'road', path: [[-260, 50], [-200, 46], [-100, 38], [0, 34], [95, 33], [205, 36], [256, 36]], w: 2.0, meander: 3 },
  ],
};

// ------------------------------------------------------------------ the Levant (second stage), 1 unit about 1.5 km
const JER = [45, 109], DAM = [112, -18], CAIRO = [-202, 237], ACRE = [35, 24];
const COAST_CASTLES = [['ANTIOCH', 103, -218], ['TRIPOLI', 84, -88], ['BEIRUT', 62, -48], ['TYRE', 43, -1], ['ACRE', 35, 24], ['JAFFA', 16, 89]];
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
  blocks: {
    egy: { ...SAL, kind: 'infantry', x: -195, z: 212, heading: 0, len: 270, dep: 135, height: 1.4, spacing: 7, hidden: true, banner: false },
    syr: { ...SAL, kind: 'infantry', x: 172, z: -98, heading: 0, len: 170, dep: 250, height: 1.4, spacing: 7, hidden: true, banner: false },
    kjer: { ...CRU, kind: 'infantry', x: 48, z: 64, heading: 18, len: 46, dep: 150, height: 1.4, spacing: 6, hidden: true, banner: false },
    ktri: { ...CRU, kind: 'infantry', x: 90, z: -92, heading: 18, len: 28, dep: 56, height: 1.4, spacing: 6, hidden: true, banner: false },
    kant: { ...CRU, kind: 'infantry', x: 110, z: -214, heading: 0, len: 50, dep: 62, height: 1.4, spacing: 6, hidden: true, banner: false },
    salL: { ...SAL, kind: 'elite', x: DAM[0], z: DAM[1], heading: 200, len: 26, dep: 14, height: 3, hidden: true, bannerScale: 2.2 },
    ricL: { ...CRU, kind: 'elite', x: -260, z: -230, heading: 120, len: 22, dep: 12, height: 3, hidden: true, bannerScale: 2.0 },
  },
  moves: [
    { block: 'salL', at: 'l02.Sultan', dur: 0.8, appear: true, appearFrom: 40 },
    { block: 'egy', at: 'l02.Egypt', dur: 0.8, appear: true, appearFrom: 30 }, { block: 'egy', at: 'l02.Egypt+0.8', dur: 0.6, to: { alpha: 0.62 } },
    { block: 'syr', at: 'l02.Syria', dur: 0.8, appear: true, appearFrom: 30 }, { block: 'syr', at: 'l02.Syria+0.8', dur: 0.6, to: { alpha: 0.62 } },
    { blocks: ['kjer', 'ktri', 'kant'], at: 'l02.crusaders', dur: 0.8, stagger: 0.18, appear: true, appearFrom: 30 }, { blocks: ['kjer', 'ktri', 'kant'], at: 'l02.crusaders+1.4', dur: 0.6, to: { alpha: 0.62 } },
    { block: 'salL', at: 'l02.Syria+1.4', dur: 0.5, to: { x: 140, z: -14 } },
    // three months later: Saladin walks to Jerusalem
    { block: 'salL', at: 'l13.Three', dur: 0.4, to: { x: 112, z: -18 }, ease: 'linear' },
    { block: 'salL', at: 'l13.Saladin', dur: 2.4, path: [[100, 20], [74, 66], [56, 98]], ease: 'inOut' },
    // the new crusade under Richard
    { block: 'ricL', at: 'l14.new', dur: 0.8, appear: true, appearFrom: 30 },
    { block: 'ricL', at: 'l14.crusade', dur: 3.6, path: [[-200, -160], [-110, -90], [-30, -20], [14, 14]], ease: 'inOut' },
  ],
  arrows: [
    { id: 'eu', at: 'l02.Europe', until: 'l02.Jerusalem', ease: 'inOut', team: 'rome', style: 'dash', width: 3.0, path: [[-300, -250], [-210, -140], [-100, -50], [8, 14]], head: true, lift: 4, hide: 'l02.string' },
    { id: 'eu2', at: 'l14.new', until: 'l14.Richard', ease: 'inOut', team: 'rome', style: 'dash', width: 3.0, path: [[-300, -250], [-200, -160], [-110, -90], [-30, -20], [14, 14]], head: true, lift: 4, hide: 'l15' },
    { id: 'sal', at: 'l13.Saladin', until: 'l13.Jerusalem', ease: 'inOut', team: 'carthage', width: 3.4, path: [[112, -18], [100, 20], [74, 66], [56, 98]], head: true, lift: 4, hide: 'l14.Europe' },
    { id: 'stop', at: 'l14.but', until: 'l14.Jerusalem', ease: 'out', team: 'rome', style: 'dash', width: 2.6, path: [[34, 20], [38, 52], [42, 84]], head: true, lift: 4, hide: 'l15' },
  ],
  labels: [
    L('l02.Saladin,', 'l02.ruler', 'SALADIN', { block: 'salL', team: 'carthage', dy: 0.16, dx: 0.1, big: true }),
    L('l02.Egypt', 'l02.For', 'EGYPT', { pos: [-195, 212], team: 'carthage', leader: false, big: true }),
    L('l02.Syria', 'l02.For', 'SYRIA', { pos: [172, -98], team: 'carthage', leader: false, big: true }),
    L('l02.almost', 'l02.crusaders', 'ALMOST 90 YEARS', { screen: [0.5, 0.92], big: true }),
    L('l02.Europe', 'l02.had', 'EUROPE', { pos: [-300, -250], team: 'rome', dy: -0.04, dx: 0.04, big: true }),
    L('l02.crusaders', 'l02.had', 'CRUSADER STATES', { pos: [60, -20], team: 'rome', dy: 0.0, dx: -0.2, big: true, leader: false }),
    L('l02.Jerusalem', 'l02.in', 'JERUSALEM', { pos: JER, y: 6, team: 'rome', dy: -0.12, dx: -0.14, big: true }),
    L('l02.string', 'l03.That', 'A STRING OF CASTLES ALONG THE COAST', { screen: [0.5, 0.92], big: true, size: 0.9, team: 'rome' }),
    ...COAST_CASTLES.map(([n, x, z], k) => L(`l02.string+${k * 0.34}`, 'l03.That', n, { pos: [x, z], y: 6, team: 'rome', dy: -0.09, dx: -0.12, size: 0.75 })),
    L('l13.Three', 'l13.Saladin', 'THREE MONTHS LATER', { screen: [0.5, 0.11], big: true }),
    L('l13.Saladin', 'l13.took', 'SALADIN', { block: 'salL', team: 'carthage', dy: -0.18, dx: 0.12, big: true }),
    L('l13.Jerusalem', 'l13.And', 'JERUSALEM TAKEN', { pos: JER, y: 6, team: 'carthage', dy: -0.13, dx: -0.16, big: true }),
    L('l13.1099', 'l13.he', '1099', { screen: [0.75, 0.2], big: true, size: 1.4 }),
    L('l13.he', 'l14.Europe', 'WITHOUT A MASSACRE', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    L('l14.Europe', 'l14.led', 'A NEW CRUSADE', { block: 'ricL', team: 'rome', dy: -0.12, dx: 0.1, big: true }),
    L('l14.Richard', 'l14.but', 'RICHARD THE LIONHEART', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l14.Jerusalem', 'l15', 'JERUSALEM STAYS WITH SALADIN', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  ],
  icons: [
    I('l02.Sultan', 'l02.ruler', 'helmet', { block: 'salL', team: 'carthage', size: 24, dy: -0.04, anim: 'sway' }),
    I('l02.Egypt', 'l02.For', 'city', { pos: CAIRO, y: 6, team: 'carthage', size: 40, anim: 'bounce' }),
    I('l02.Syria', 'l02.For', 'city', { pos: DAM, y: 6, team: 'carthage', size: 40, anim: 'bounce' }),
    I('l02.Europe', 'l02.crusaders', 'ship', { follow: 'eu', team: 'rome', size: 34 }),
    I('l02.held', 'l03.That', 'crown', { pos: [JER[0], JER[1]], y: 22, size: 26, anim: 'bounce' }),
    I('l02.Jerusalem', 'l13.Three', 'city', { pos: JER, y: 6, team: 'rome', size: 40, anim: 'bounce' }),
    ...COAST_CASTLES.map(([n, x, z], k) => I(`l02.string+${k * 0.34}`, 'l03.That', 'castle', { pos: [x, z], y: 4, team: 'rome', size: 22, anim: 'bounce' })),
    I('l13.Jerusalem', 'l15', 'city', { pos: JER, y: 6, team: 'carthage', size: 44, anim: 'bounce' }),
    I('l13.Jerusalem+0.2', 'l15', 'flag', { pos: [JER[0] - 8, JER[1]], y: 20, team: 'carthage', size: 20 }),
    I('l13.Crusaders', 'l13.he', 'city', { screen: [0.75, 0.82], team: 'rome', size: 0.4, anim: 'sway' }),
    I('l13.without', 'l14.Europe', 'laurel', { pos: [JER[0] + 26, JER[1] - 4], y: 10, size: 34, anim: 'bounce' }),
    I('l14.Europe', 'l14.led', 'ship', { follow: 'eu2', team: 'rome', size: 34 }),
    I('l14.Richard', 'l14.but', 'crown', { block: 'ricL', size: 26, dy: -0.04, anim: 'bounce' }),
    I('l14.stayed', 'l15', 'no', { pos: [42, 84], y: 14, size: 34 }),
  ],
  dim: [{ at: 'l13.Crusaders', until: 'l13.he', alpha: 0.55, color: 'rgb(14,7,3)', fadeIn: 0.4, fadeOut: 0.4 }],
  camera: [
    { at: 15.4, target: [60, 20], width: 820, pitch: 56, yaw: 0, mm: 35 },
    { at: 'l02.Sultan', target: [150, -40], width: 420, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.ruler', target: [10, 80], width: 800, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.Syria', target: [10, 80], width: 810, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.almost', target: [120, 10], width: 520, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.crusaders', target: [90, -20], width: 500, pitch: 54, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 'l02.held', target: [75, 70], width: 330, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.string', target: [120, -150], width: 300, pitch: 54, yaw: 6, mm: 35, ease: 'inOut' },
    { at: 'l02.along', target: [85, -30], width: 320, pitch: 54, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 'l02>', target: [60, 60], width: 330, pitch: 54, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 'l13.Three', target: [110, 20], width: 520, pitch: 54, yaw: 0, mm: 35, ease: 'cut', cut: true },
    { at: 'l13.Saladin', target: [100, 40], width: 360, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l13.Jerusalem', target: [70, 100], width: 210, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l13.without+0.6', target: [66, 96], width: 190, pitch: 48, yaw: 6, mm: 35, ease: 'inOut' },
    { at: 'l14.Europe', target: [-20, -40], width: 560, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l14.Richard', target: [10, -20], width: 420, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l14.but', target: [60, 50], width: 260, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l14>', target: [64, 54], width: 240, pitch: 50, yaw: 4, mm: 35, ease: 'linear' },
  ],
};

// ------------------------------------------------------------------ the battle on the Galilee map
// the blue ring around the red tent: k-th of n blocks on a circle of radius R around the saddle (heading = tangent, clockwise)
const RING = ['salA.0.0', 'salA.1.0', 'salA.2.0', 'salA.3.0', 'salA.4.0', 'salA.0.1', 'salA.1.1', 'salA.2.1', 'salA.3.1', 'salA.4.1', 'ha0', 'ha1', 'ha2', 'ha3', 'ha4', 'ha5'];
const ringPos = (k, R, n = RING.length) => { const a = (k / n) * Math.PI * 2 + 0.3; return { x: SADDLE[0] + Math.cos(a) * R * 1.12, z: SADDLE[1] + Math.sin(a) * R, heading: (a * 180 / Math.PI + 180) % 360 }; };
const ringTo = (k, R) => { const p = ringPos(k, R); return { ...p, heading: near(p.heading, k >= 10 ? haH1(k - 10) : 270) }; };
const HA_C = [40, 36], HA_R = 58;          // the horse archers circle the crusaders around this point
const haStart = (k) => { const a = (k / 6) * Math.PI * 2; return { x: HA_C[0] + Math.cos(a) * HA_R, z: HA_C[1] + Math.sin(a) * HA_R, heading: (a * 180 / Math.PI + 180) % 360 }; };
const ha = {}; for (let k = 0; k < 6; k++) ha['ha' + k] = { ...SAL, kind: 'cavalry', ...haStart(k), len: 12, dep: 5, height: 2.4, hidden: true, bannerScale: 1.1 };
const near = (h, ref) => h + 360 * Math.round((ref - h) / 360);
const haH1 = (k) => near(270, haStart(k).heading + 340);      // heading after the circle, unwrapped, facing west
const lord = (k) => [-238 + k * 14, 10];
const NOS = ['NO', 'NO', 'NO', 'NO', 'NO', 'NO'];
const FIRE = [[138, -4], [143, 12], [140, 28], [146, 44], [141, 60], [147, 76], [137, 90]];

const battle = {
  blocks: {
    hkC: { ...CRU, kind: 'infantry', x: -270, z: 45, heading: 90, len: 36, dep: 20, height: 3.5, hidden: true, bannerScale: 1.5 },
    hkS: { ...SAL, kind: 'elite', x: 122, z: -6, heading: 270, len: 22, dep: 12, height: 3.5, hidden: true, bannerScale: 1.8 },
    crus: { ...CRU, kind: 'infantry', x: SAFF[0], z: SAFF[1], heading: 90, len: 40, dep: 20, grid: { cols: 4, ranks: 2, gap: 0.9 }, count: 20000, hidden: true, height: 3.5, bannerScale: 0.95 },
    salT: { ...SAL, kind: 'infantry', x: 440, z: 150, heading: 270, len: 26, dep: 14, height: 3.5, hidden: true, bannerScale: 1.5 },
    ...ha,
    salA: { ...SAL, kind: 'infantry', x: 218, z: 33, heading: 270, len: 110, dep: 20, grid: { cols: 5, ranks: 2, gap: 1.2 }, hidden: true, height: 3.5, bannerScale: 1.0 },
    saladin: { ...SAL, kind: 'elite', x: 236, z: 28, heading: 270, len: 12, dep: 7, height: 3.5, hidden: true, bannerScale: 2.0 },
  },

  moves: [
    // ---- hook: the sultan waits on the far hills; the army is lured out into the heat
    { block: 'hkS', at: 'l00.Sultan', dur: 0.8, appear: true, appearFrom: 30 },
    { block: 'hkC', at: 'l00.entire', dur: 0.8, appear: true, appearFrom: 30 },
    { block: 'hkC', at: 'l00.out', until: 'l00.waited', by: { x: 330, z: -8 }, ease: 'inOut' },
    { blocks: ['hkC', 'hkS'], at: 11.4, dur: 0.5, vanish: true },
    // ---- the crusader army at Saffuriya
    { group: 'crus', at: 'l03.crusader', dur: 0.7, stagger: 0.08, appear: true, appearFrom: 20 },
    // Saladin's army arrives at Tiberias (round the south of the lake)
    { block: 'salT', at: 'l03.Saladin', dur: 0.8, appear: true, appearFrom: 20 },
    { block: 'salT', at: 'l03.attacked', dur: 2.6, path: [[400, 180], [340, 190], [292, 150], [262, 104], [246, 58]], ease: 'inOut' },
    // ---- the march: Guy marches anyway; across the dry hills; the horse archers circle; the plateau
    { group: 'crus', at: 'l04.marched', until: 'l05>', by: { x: 230, z: -10 }, ease: 'inOut' },
    { group: 'crus', at: 'l06', until: 'l06>', by: { x: 20 }, ease: 'linear' },
    { group: 'crus', at: 'l07.By', until: 'l07.dry', by: { x: 45 }, ease: 'out' },
    ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l06.Saladin\'s', dur: 0.5, stagger: 0.12, appear: true, appearFrom: 16 })),
    ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l06.Saladin\'s+0.8', until: 'l06.blocking', wheel: { about: HA_C, deg: 340 }, ease: 'linear' })),
    // blocking the way to water: they line up east of the camp, between the crusaders and the springs
    ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l06.blocking', dur: 1.3, to: { x: 150, z: -2 + k * 15, heading: haH1(k) }, ease: 'inOut' })),
    // evening: Saladin's whole army stands between the crusaders and the lake
    { group: 'salA', at: 'l07.army', dur: 0.7, stagger: 0.07, appear: true, appearFrom: 20 },
    ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l07.army', dur: 1.2, to: { x: 205, z: 6 + k * 15, heading: 270 }, ease: 'inOut' })),
    // night: the horse archers ride the line and set the grass alight
    ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l08.men', dur: 1.6, to: { x: 150, z: -2 + k * 15 }, ease: 'inOut' })),
    // morning: the crusaders try to break through toward the springs
    { group: 'crus', at: 'l09.break', until: 'l09.springs', by: { x: 42, z: -24 }, ease: 'inOut' },
    ...Object.keys(ha).map((id, k) => ({ block: id, at: 'l09.break', dur: 1.4, to: { x: 176, z: -6 + k * 16 }, ease: 'inOut' })),
    // the army breaks into pieces
    ...[0, 1, 2, 3].flatMap((i) => [0, 1].map((j) => ({ block: `crus.${i}.${j}`, at: 'l10.pieces', dur: 1.0, by: { z: (i - 1.5) * 7, x: j ? 5 : -5 }, ease: 'out' }))),
    ...['crus.0.0', 'crus.1.0', 'crus.0.1', 'crus.1.1'].map((id, k) => ({ block: id, at: 'l10.charged', dur: 1.6, stagger: 0.08, by: { x: 54, z: -8 }, ease: 'in' })),
    { block: 'crus.2.0', at: 'l10.fled', dur: 1.9, to: { x: 150, z: 18, heading: 0 }, ease: 'inOut' }, { block: 'crus.2.1', at: 'l10.fled', dur: 1.9, to: { x: 156, z: 38, heading: 0 }, ease: 'inOut' },
    { block: 'crus.3.0', at: 'l10.fled', dur: 2.1, to: { x: 192, z: 16, heading: 0 }, ease: 'inOut' }, { block: 'crus.3.1', at: 'l10.fled', dur: 2.1, to: { x: 198, z: 40, heading: 0 }, ease: 'inOut' },
    // the blue ring closes round the red tent, then tightens
    ...RING.map((id, k) => ({ block: id, at: 'l10.surrounded', dur: 1.3, stagger: 0.04, to: { ...ringTo(k, 46), scale: 0.8 }, ease: 'inOut' })),
    ...RING.map((id, k) => ({ block: id, at: 'l11.fell,', dur: 1.5, stagger: 0.02, to: ringTo(k, 38), ease: 'inOut' })),
    { blocks: ['crus.0.0', 'crus.1.0', 'crus.0.1', 'crus.1.1'], at: 'l10.surrounded', dur: 1.0, fadeTo: 1, alphaTo: 0.12, sinkTo: 0.9 },
    { blocks: ['crus.2.0', 'crus.2.1', 'crus.3.0', 'crus.3.1'], at: 'l11.over', dur: 1.8, stagger: 0.15, fadeTo: 1, alphaTo: 0.12, sinkTo: 0.9 },
    // Saladin walks up to the king
    { block: 'saladin', at: 'l12.Saladin', dur: 0.8, appear: true, appearFrom: 30 },
    { block: 'saladin', at: 'l12.offered', dur: 2.6, path: [[210, 28], [190, 28], [182, 28]], ease: 'inOut' },
    { blocks: [...RING, 'saladin', 'crus.2.0', 'crus.2.1', 'crus.3.0', 'crus.3.1'], at: 113.4, dur: 0.6, vanish: true },
  ],

  arrows: [
    { id: 'hookArrow', at: 'l00.lured', until: 'l00.army', ease: 'inOut', team: 'carthage', style: 'dash', width: 2.6, path: [[110, -4], [10, 20], [-120, 42], [-250, 44]], lift: 4, head: true, hide: 'l00.out' },
    { id: 'hookMarch', at: 'l00.out', until: 'l00.waited', ease: 'inOut', team: 'rome', style: 'dash', width: 2.6, path: [[-262, 44], [-170, 40], [-60, 34], [60, 28]], lift: 4, head: true, hide: 11.2 },
    { id: 'rescue', at: 'l03.rescue', until: 'l03>', ease: 'inOut', team: 'rome', style: 'dash', width: 3, path: [[-190, 45], [-60, 40], [90, 36], [220, 36]], lift: 4, head: true, hide: 'l04.King' },
    { id: 'march', at: 'l04.marched', until: 'l05.dry', ease: 'inOut', team: 'rome', style: 'dash', width: 3.2, path: [[-190, 45], [-110, 40], [-20, 36], [55, 36]], lift: 4, head: true, hide: 'l06.All' },
    { id: 'ring', at: 'l06.long,', until: 'l06.rode', ease: 'inOut', team: 'carthage', style: 'dash', width: 3, path: Array.from({ length: 14 }, (_, i) => { const a = (i / 13) * Math.PI * 1.9 - 0.2; return [HA_C[0] + Math.cos(a) * HA_R, HA_C[1] + Math.sin(a) * HA_R]; }), lift: 4, head: true, hide: 'l06.blocking' },
    { id: 'see', at: 'l07.see', until: 'l07.water,', ease: 'out', team: 'cream', style: 'dash', width: 2.4, path: [[CAMP[0] + 14, CAMP[1]], [190, 34], [262, 36]], lift: 5, head: true, hide: 'l08' },
    { id: 'breakout', at: 'l09.break', until: 'l09.springs', ease: 'inOut', team: 'rome', width: 4, path: [[CAMP[0] + 12, CAMP[1] - 2], [130, 12], [160, -14], [SPRING[0] - 4, SPRING[1] + 4]], lift: 4, head: true, hide: 'l10.Their' },
  ],

  volleys: [
    ...Array.from({ length: 4 }, (_, k) => ({ at: `l06.shooting+${k * 0.45}`, dur: 0.7, from: { block: 'ha' + (k % 6) }, to: [58, 36, 18], n: 20, flight: 0.9, arc: 26, team: 'carthage' })),
    { at: 'l06.arrows', dur: 0.8, from: { block: 'ha3' }, to: [56, 36, 20], n: 24, flight: 0.9, arc: 26, team: 'carthage' },
    { at: 'l06.arrows+0.3', dur: 0.8, from: { block: 'ha5' }, to: [60, 38, 20], n: 24, flight: 0.9, arc: 26, team: 'carthage' },
  ],

  labels: [
    // ---- hook
    { at: 1.51, until: 3.2, text: '1187', screen: [0.5, 0.17], style: 'text', big: true, size: 1.9, track: 0.16, weight: 800 },
    L('l00.Sultan', 'l00.lured', 'THE SULTAN', { block: 'hkS', team: 'carthage', dy: -0.2, dx: 0.1, big: true }),
    L('l00.lured', 'l00.entire', 'LURED', { pos: [-60, 34], y: 4, team: 'carthage', leader: false, big: true }),
    L('l00.entire', 'l00.out', 'AN ENTIRE ARMY', { block: 'hkC', team: 'rome', dy: -0.18, dx: 0.0, big: true }),
    L('l00.middle', 'l00.waited', 'THE MIDDLE OF SUMMER', { screen: [0.5, 0.88], big: true }),
    L('l00.waited', 'l00.thirsty', 'WAITING', { block: 'hkS', team: 'carthage', dy: -0.2, dx: 0.1, big: true }),
    L('l00.thirsty', 'l01', 'THIRSTY', { screen: [0.5, 0.2], big: true, size: 1.4, team: 'rome' }),
    // ---- Tiberias
    L('l03.That', 'l03.Saladin', 'SUMMER 1187', { screen: [0.5, 0.11], big: true }),
    L('l03.Saladin', 'l03.Tiberius', 'SALADIN ATTACKS', { block: 'salT', team: 'carthage', dy: -0.16, dx: 0.1, big: true }),
    L('l03.Tiberius', 'l03.Sea', 'TIBERIAS', { pos: TIB, y: 4, team: 'rome', dy: -0.17, dx: -0.1, big: true }),
    L('l03.Sea', 'l03.It', 'SEA OF GALILEE', { pos: [315, 40], leader: false, big: true, size: 1.2 }),
    L('l03.bait.', 'l03.crusader', 'IT WAS BAIT', { screen: [0.3, 0.11], big: true, size: 1.2 }),
    L('l03.crusader', 'l03.army', 'CRUSADER ARMY', { block: 'crus', team: 'rome', dy: -0.16, big: true }),
    L('l03.rescue', 'l04.Some', 'COME OUT AND RESCUE IT', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    // ---- the lords say no
    L('l04.lords', 'l04.King', 'THE LORDS', { pos: lord(2.5), y: 2, team: 'rome', dy: 0.07, leader: false, size: 0.8 }),
    ...[0, 1, 2].map((k) => L(`l04.don't#0+${k * 0.16}`, 'l04.It\'s', 'NO', { pos: lord(k), y: 8, team: 'rome', dy: -0.1, size: 0.8, big: true })),
    L('l04.July', 'l04.There\'s', 'JULY', { screen: [0.5, 0.11], big: true, size: 1.5, team: 'rome' }),
    ...[3, 4, 5].map((k) => L(`l04.no+${(k - 3) * 0.3}`, 'l04.Even', 'NO', { pos: lord(k), y: 8, team: 'rome', dy: -0.1, size: 0.8, big: true })),
    L('l04.water', 'l04.Even', 'NO WATER ON THE WAY', { screen: [0.5, 0.11], big: true }),
    L('l04.wife', 'l04.said#1', 'HIS WIFE IS IN TIBERIAS', { pos: TIB, y: 4, team: 'rome', dy: -0.17, dx: -0.16, big: true }),
    L('l04.don\'t#1', 'l04.King', 'DON\'T GO', { pos: lord(2.5), y: 8, team: 'rome', dy: -0.1, big: true, size: 1.3 }),
    L('l04.King', 'l04.marched', 'KING GUY OF JERUSALEM', { block: 'crus', team: 'rome', dy: -0.16, big: true }),
    L('l04.marched', 'l05.About', 'HE MARCHES ANYWAY', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    // ---- the march
    L('l05.across', 'l05.heavy', 'ACROSS THE DRY HILLS', { screen: [0.5, 0.11], big: true }),
    L('l05.heavy', 'l05.in#1', 'HEAVY ARMOUR', { block: 'crus', team: 'rome', dy: -0.16, big: true }),
    L('l05.July.', 'l06.All', 'IN JULY', { screen: [0.5, 0.11], big: true, size: 1.5 }),
    // ---- horse archers
    L('l06.Saladin\'s', 'l06.shooting', 'HORSE ARCHERS', { block: 'ha1', team: 'carthage', dy: -0.2, dx: 0.12, big: true }),
    L('l06.rode', 'l06.shooting', 'CIRCLING ALL DAY', { screen: [0.5, 0.11], big: true }),
    L('l06.shooting', 'l06.blocking', 'SHOOTING ARROWS', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    L('l06.blocking', 'l07.By', 'THE WAY TO WATER IS BLOCKED', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    // ---- the dry plateau
    L('l07.By', 'l07.crusaders', 'EVENING', { screen: [0.5, 0.11], big: true }),
    L('l07.stuck', 'l07.Saladin\'s', 'STUCK ON A DRY PLATEAU', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l07.army', 'l07.lake', 'SALADIN\'S ARMY', { block: 'salA', team: 'carthage', dy: -0.17, big: true }),
    L('l07.lake', 'l07.They', 'THE LAKE', { pos: [338, 25], leader: false, big: true, size: 1.2 }),
    L('l07.They', 'l07.they#1', 'THEY COULD SEE THE WATER', { screen: [0.5, 0.11], big: true }),
    L('l07.they#1', 'l07>', 'BUT COULD NOT REACH IT', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    // ---- the night of smoke
    L('l08.That', 'l08.set', 'THAT NIGHT', { screen: [0.5, 0.11], big: true }),
    L('l08.set', 'l08.smoke', 'GRASS ON FIRE', { pos: [143, 40], y: 6, dy: -0.2, big: true }),
    L('l08.smoke', 'l08.thirsty', 'SMOKE INTO THE CAMP', { screen: [0.5, 0.11], big: true }),
    L('l08.thirsty', 'l08.coughing', 'THIRSTY', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l08.coughing', 'l09.In', 'AND NOW COUGHING', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    // ---- morning: the break-out
    L('l09.In', 'l09.break', 'MORNING', { screen: [0.5, 0.11], big: true }),
    L('l09.break', 'l09.springs,', 'BREAK THROUGH', { block: 'crus', team: 'rome', dy: -0.17, big: true }),
    L('l09.springs,', 'l09.near', 'THE SPRINGS', { pos: SPRING, y: 2, dy: -0.1, dx: -0.12, big: true }),
    L('l09.near', 'l09.Horns', 'TWO HILLS', { screen: [0.5, 0.11], big: true }),
    L('l09.Horns', 'l10.Their', 'THE HORNS OF HATTIN', { screen: [0.5, 0.11], big: true, size: 1.1 }),
    // ---- the army breaks
    L('l10.broke', 'l10.charged', 'THE ARMY BREAKS INTO PIECES', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l10.charged', 'l10.some#1', 'SOME CHARGE', { block: 'crus.0.0', team: 'rome', dy: -0.12, big: true }),
    L('l10.fled', 'l10.King', 'SOME FLEE UP THE HILLS', { pos: SADDLE, y: 20, dy: -0.2, leader: false, big: true, team: 'rome' }),
    L('l10.red', 'l10.was', 'KING GUY\'S RED TENT', { pos: SADDLE, y: 4, dy: -0.23, team: 'rome', big: true }),
    L('l10.surrounded', 'l11.When', 'SURROUNDED', { pos: SADDLE, y: 4, dy: -0.23, team: 'carthage', big: true }),
    // ---- the tent falls
    L('l11.fell,', 'l11.King', 'THE RED TENT FALLS', { pos: SADDLE, y: 4, dy: -0.23, team: 'rome', big: true }),
    L('l11.over.', 'l11.King', 'THE BATTLE IS OVER', { screen: [0.5, 0.11], big: true }),
    L('l11.King', 'l12.Saladin', 'KING GUY CAPTURED', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    // ---- the cup
    L('l12.Saladin', 'l12.cup', 'SALADIN', { block: 'saladin', team: 'carthage', dy: -0.18, dx: 0.1, big: true }),
    L('l12.Exhausted', 'l12.cup', 'THE EXHAUSTED KING', { pos: SADDLE, y: 4, team: 'rome', dy: -0.2, dx: -0.12, big: true }),
    L('l12.cup', 'l12.cooled', 'A CUP OF WATER', { screen: [0.5, 0.11], big: true }),
    L('l12.cooled', 'l12.a#1', 'COOLED WITH ICE', { screen: [0.5, 0.11], big: true }),
    L('l12.a#1', 113.7, 'A SIGN HIS LIFE WOULD BE SPARED', { screen: [0.5, 0.11], big: true, size: 0.95 }),
    // ---- the lesson
    L('l15.lesson', 'l15.never', 'THE LESSON OF HATTIN', { screen: [0.5, 0.11], big: true }),
    L('l15.never', 'l15.especially', 'NEVER CROSS DRY HILLS IN JULY', { screen: [0.5, 0.11], big: true, size: 1.1 }),
    L('l15.especially', 137.3, 'ESPECIALLY IN A METAL SUIT', { screen: [0.5, 0.11], big: true, size: 1.1, team: 'rome' }),
  ],

  counters: [
    { at: 'l05.20', until: 'l05.July.', block: 'crus', team: 'rome', from: 0, to: 20000, countDur: 1.1, step: 500, suffix: 'CRUSADERS', dy: -0.19 },
  ],

  icons: [
    // ---- hook
    I('l00.middle', 'l00.waited', 'sun', { screen: [0.84, 0.3], size: 0.3, anim: 'sway' }),
    I('l00.Sultan', 'l00.lured', 'helmet', { block: 'hkS', team: 'carthage', size: 20, dy: -0.04, anim: 'sway' }),
    I('l00.entire', 'l00.waited', 'helmet', { block: 'hkC', team: 'rome', size: 20, dy: -0.04, anim: 'sway' }),
    I('l00.waited', 'l00.thirsty', 'hourglass', { block: 'hkS', size: 22, dy: -0.04, anim: 'sway' }),
    I('l00.thirsty', 'l01', 'flask', { screen: [0.5, 0.74], size: 0.4, anim: 'sway' }),
    // ---- Tiberias and the bait
    I('l03.That', 'l03.Saladin', 'sun', { screen: [0.88, 0.32], size: 0.24, anim: 'sway' }),
    I('l03.Tiberius', 'l04.King', 'city', { pos: TIB, y: 4, team: 'rome', size: 36, anim: 'bounce' }),
    I('l03.attacked', 'l03.It', 'burst', { pos: [244, 54], y: 8, size: 20 }),
    I('l03.bait.', 'l03.crusader', 'hook', { pos: TIB, y: 14, size: 60, anim: 'sway' }),
    I('l03.crusader', 'l03.army', 'helmet', { block: 'crus', team: 'rome', size: 18, dy: -0.04, anim: 'sway' }),
    // ---- the lords
    ...[0, 1, 2, 3, 4, 5].map((k) => I(`l04.lords+${k * 0.08}`, 'l04.King', 'helmet', { pos: lord(k), y: 3, team: 'rome', size: 12, anim: 'sway' })),
    I('l04.July', 'l04.There\'s', 'thermo', { screen: [0.83, 0.52], size: 0.34 }),
    I('l04.water', 'l04.Even', 'flask', { screen: [0.5, 0.7], size: 0.3, anim: 'sway' }),
    I('l04.water', 'l04.Even', 'no', { screen: [0.62, 0.68], size: 0.2 }),
    I('l04.wife', 'l04.said#1', 'heart', { pos: TIB, y: 20, size: 22, anim: 'bounce' }),
    I('l04.King', 'l04.marched', 'crown', { block: 'crus', size: 16, dy: -0.04, anim: 'bounce' }),
    // ---- the march
    I('l05.dry', 'l05.in', 'sun', { screen: [0.86, 0.3], size: 0.26, anim: 'sway' }),
    I('l05.heavy', 'l05.in#1', 'hothelmet', { screen: [0.5, 0.62], size: 0.34, team: 'rome', anim: 'sway' }),
    I('l05.July.', 'l06.All', 'thermo', { screen: [0.84, 0.52], size: 0.36 }),
    // ---- horse archers
    I('l06.Saladin\'s', 'l06.shooting', 'bow', { block: 'ha1', size: 16, dy: -0.04, anim: 'bounce' }),
    I('l06.shooting', 'l06.blocking', 'bow', { block: 'ha3', size: 16, dy: -0.04, anim: 'bounce' }),
    I('l06.blocking', 'l07.By', 'drop', { pos: [172, 36], y: 6, size: 18, anim: 'bounce' }),
    I('l06.blocking', 'l07.By', 'no', { pos: [172, 36], y: 6, size: 26 }),
    // ---- evening: the plateau
    I('l07.stuck', 'l07.Saladin\'s', 'sweat', { block: 'crus', size: 16, dy: -0.04, anim: 'bounce' }),
    I('l07.lake', 'l07.They', 'drop', { pos: [320, 25], y: 6, size: 26, anim: 'bounce' }),
    I('l07.see', 'l07.they#1', 'eye', { block: 'crus', size: 22, dy: -0.05, anim: 'sway' }),
    I('l07.couldn\'t', 'l08.That', 'no', { pos: [222, 34], y: 8, size: 30 }),
    // ---- the night
    ...FIRE.map(([x, z], k) => I(`l08.fire+${k * 0.15}`, 'l09.In', 'flame', { pos: [x, z], y: 1, size: 8 + (k % 3) })),
    I('l08.smoke', 'l08.thirsty', 'cough', { screen: [0.5, 0.62], size: 0.3, anim: 'none' }),
    I('l08.thirsty', 'l09.In', 'flask', { screen: [0.34, 0.66], size: 0.3, anim: 'sway' }),
    I('l08.coughing', 'l09.In', 'cough', { screen: [0.66, 0.66], size: 0.32, anim: 'none' }),
    // ---- the break-out and the Horns
    I('l09.springs,', 'l10.Their', 'drop', { pos: SPRING, y: 4, size: 18, anim: 'bounce' }),
    I('l09.hills', 'l10.Their', 'twinpeaks', { screen: [0.86, 0.4], size: 0.2, anim: 'bounce' }),
    // ---- the army breaks
    I('l10.charged', 'l10.some#1', 'burst', { pos: [200, 6], y: 8, size: 20 }),
    I('l10.red', 'l11.When', 'tent2', { pos: SADDLE, y: 6, team: 'rome', size: 15, anim: 'none' }),
    I('l10.surrounded', 'l11.When', 'burst', { pos: [SADDLE[0] + 30, SADDLE[1] + 10], y: 8, size: 16 }),
    // ---- the tent falls
    { at: 'l11.red', until: 'l11.King', icon: 'tent2', pos: SADDLE, y: 6, team: 'rome', size: 15, anim: 'none', fallAt: 'l11.fell,', fallDur: 0.9 },
    I('l11.King', 'l12.Saladin', 'crown', { pos: SADDLE, y: 12, size: 18, anim: 'bounce' }),
    I('l11.captured', 'l12.Saladin', 'hug', { pos: SADDLE, y: 4, team: 'carthage', inner: [0.86, 0.80, 0.64], size: 20 }),
    // ---- the cup
    I('l12.Saladin', 'l12.cup', 'helmet', { block: 'saladin', team: 'carthage', size: 14, dy: -0.04, anim: 'sway' }),
    I('l12.Exhausted', 'l12.cup', 'sweat', { pos: SADDLE, y: 12, size: 20, anim: 'bounce' }),
    I('l12.cup', 'l12>', 'cup', { screen: [0.5, 0.95], size: 0.62, anim: 'bounce' }),
    I('l12.a#1', 'l12>', 'check', { screen: [0.74, 0.7], size: 0.22, anim: 'bounce' }),
    // ---- the lesson
    I('l15.lesson', 'l15.never', 'book', { screen: [0.5, 0.6], size: 0.34, anim: 'bounce' }),
    I('l15.never', 'l15.especially', 'sun', { screen: [0.5, 0.64], size: 0.4, anim: 'sway' }),
    I('l15.especially', 137.4, 'hothelmet', { screen: [0.5, 0.74], size: 0.52, team: 'rome', anim: 'sway' }),
  ],

  shimmer: [
    { at: 'l00.middle', until: 'l00.thirsty', strength: 0.9 },
    { at: 'l04.July', until: 'l04.King', strength: 0.55 },
    { at: 'l05.across', until: 'l07.By', strength: 1.0 },
    { at: 'l15.never', until: 137.4, strength: 0.9 },
  ],
  smoke: [
    { at: 'l08.set', until: 'l09.In', from: [136, -6, 142, 92], wind: [-52, 8], n: 70, size: 11, rise: 12, speed: 0.12, alpha: 0.85, fadeIn: 1.0, fadeOut: 0.8 },
  ],
  dim: [
    { at: 'l08.That', until: 'l09.In', alpha: 0.5, color: 'rgb(8,12,48)', stars: true, fadeIn: 0.8, fadeOut: 0.9 },
    { at: 'l12.cup', until: 'l12>', alpha: 0.5, color: 'rgb(14,7,3)', fadeIn: 0.6, fadeOut: 0.4 },
    { at: 'l15.lesson', until: 137.4, alpha: 0.38, color: 'rgb(14,7,3)', fadeIn: 0.6, fadeOut: 0.3 },
  ],

  light: [
    { at: 'l07.By', dur: 3.0, to: { eve: 1, haze: 1.3 }, ease: 'inOut' },
    { at: 'l09.In', dur: 2.0, to: { eve: 0, haze: 1.0, cloud: 0.35 }, ease: 'inOut' },
    { at: 'l11.When', dur: 4.0, to: { eve: 0.8, haze: 1.2 }, ease: 'inOut' },
  ],

  camera: [
    // hook: low sweep over the dry hills, then the whole corridor from Saffuriya to the Horns
    { at: 0, target: [-300, 45], dist: 170, pitch: 15, yaw: 78, mm: 30 },
    { at: 'l00.Sultan', target: [-30, 25], width: 600, pitch: 36, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.entire', target: [-50, 25], width: 560, pitch: 34, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.out', target: [-150, 40], width: 360, pitch: 30, yaw: 40, mm: 35, ease: 'inOut' },
    { at: 'l00.middle', target: [-20, 35], dist: 260, pitch: 20, yaw: 78, mm: 30, ease: 'inOut' },
    { at: 'l00.and', target: [60, 28], dist: 230, pitch: 22, yaw: 80, mm: 30, ease: 'inOut' },
    { at: 'l00.waited', target: [80, 10], width: 380, pitch: 40, yaw: 20, mm: 35, ease: 'inOut' },
    { at: 11.0, target: [80, 10], width: 400, pitch: 42, yaw: 20, mm: 35, ease: 'linear' },
    // Tiberias
    { at: 'l03.That', target: [210, 40], width: 400, pitch: 54, yaw: 0, mm: 35, ease: 'cut', cut: true },
    { at: 'l03.Saladin', target: [290, 70], width: 300, pitch: 46, yaw: -10, mm: 35, ease: 'inOut' },
    { at: 'l03.Tiberius', target: [264, 40], width: 190, pitch: 44, yaw: -20, mm: 35, ease: 'inOut' },
    { at: 'l03.It', target: [262, 36], width: 150, pitch: 40, yaw: -10, mm: 35, ease: 'inOut' },
    { at: 'l03.crusader', target: [30, 40], width: 620, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.army', target: [-120, 40], width: 360, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.rescue', target: [30, 40], width: 640, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
    // the lords say no
    { at: 'l04.Some', target: [-205, 30], width: 170, pitch: 42, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l04.July', target: [-205, 30], width: 150, pitch: 38, yaw: -10, mm: 35, ease: 'inOut' },
    { at: 'l04.Even', target: [250, 40], width: 200, pitch: 44, yaw: -14, mm: 35, ease: 'inOut' },
    { at: 'l04.said#1', target: [236, 40], width: 190, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.don\'t#1', target: [-205, 30], width: 160, pitch: 40, yaw: 8, mm: 35, ease: 'inOut' },
    { at: 'l04.King', target: [-190, 40], width: 190, pitch: 38, yaw: 20, mm: 35, ease: 'inOut' },
    // the march across the dry hills
    { at: 'l04.marched', target: [-160, 40], width: 200, pitch: 34, yaw: 55, mm: 35, ease: 'inOut' },
    { at: 'l05.About', target: [-110, 40], width: 230, pitch: 30, yaw: 70, mm: 35, ease: 'inOut' },
    { at: 'l05.dry', target: [-30, 36], width: 250, pitch: 28, yaw: 78, mm: 35, ease: 'inOut' },
    { at: 'l05.heavy', target: [14, 36], width: 220, pitch: 34, yaw: 80, mm: 35, ease: 'inOut' },
    // horse archers circle
    { at: 'l06.All', target: [40, 36], width: 250, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l06.rode', target: [40, 36], width: 215, pitch: 46, yaw: 30, mm: 35, ease: 'linear' },
    { at: 'l06.blocking', target: [110, 28], width: 300, pitch: 44, yaw: 70, mm: 35, ease: 'inOut' },
    // evening on the plateau, looking east to the lake
    { at: 'l07.By', target: [150, 32], dist: 250, pitch: 24, yaw: 82, mm: 32, ease: 'inOut' },
    { at: 'l07.stuck', target: [140, 32], dist: 240, pitch: 22, yaw: 86, mm: 30, ease: 'inOut' },
    { at: 'l07.army', target: [210, 30], dist: 230, pitch: 24, yaw: 90, mm: 30, ease: 'inOut' },
    { at: 'l07.They', target: [250, 30], dist: 250, pitch: 20, yaw: 92, mm: 30, ease: 'inOut' },
    { at: 'l07>', target: [250, 30], dist: 240, pitch: 20, yaw: 94, mm: 30, ease: 'linear' },
    // night
    { at: 'l08.That', target: [110, 36], dist: 150, pitch: 28, yaw: 262, mm: 32, ease: 'inOut' },
    { at: 'l08.smoke', target: [105, 36], dist: 140, pitch: 26, yaw: 250, mm: 32, ease: 'inOut' },
    { at: 'l08.thirsty', target: [92, 36], dist: 100, pitch: 30, yaw: 240, mm: 32, ease: 'inOut' },
    // morning, the Horns
    { at: 'l09.In', target: [120, 20], width: 300, pitch: 46, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l09.break', target: [130, 10], width: 240, pitch: 46, yaw: 25, mm: 35, ease: 'inOut' },
    { at: 'l09.near', target: [172, 16], width: 190, pitch: 40, yaw: 50, mm: 35, ease: 'inOut' },
    { at: 'l09.Horns', target: [176, 22], width: 160, pitch: 36, yaw: 90, mm: 35, ease: 'inOut' },
    { at: 'l10.Their', target: [160, 20], width: 220, pitch: 46, yaw: 60, mm: 35, ease: 'inOut' },
    { at: 'l10.charged', target: [178, 22], width: 190, pitch: 50, yaw: 30, mm: 35, ease: 'inOut' },
    { at: 'l10.King', target: [176, 28], width: 190, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l10.surrounded', target: [176, 28], width: 190, pitch: 52, yaw: -20, mm: 35, ease: 'inOut' },
    { at: 'l11.When', target: [176, 28], width: 170, pitch: 50, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l11.King', target: [176, 28], width: 150, pitch: 46, yaw: 40, mm: 35, ease: 'inOut' },
    { at: 'l12.Saladin', target: [186, 28], width: 170, pitch: 44, yaw: 90, mm: 35, ease: 'inOut' },
    { at: 'l13', target: [186, 28], width: 170, pitch: 44, yaw: 100, mm: 35, ease: 'linear' },
    // the lesson
    { at: 'l15', target: [20, 30], width: 600, pitch: 50, yaw: 0, mm: 35, ease: 'cut', cut: true },
    { at: 141.55, target: [20, 30], width: 560, pitch: 52, yaw: 6, mm: 35, ease: 'linear' },
  ],
};

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 } },
  world: galilee,
  ...battle,
  stages: { lev },
  msaaOn: [[0, 11]],
  insets: [
    { stage: 'lev', at: 15.4, until: 'l03', rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.8, out: 0.01, samples: 0 },
    { stage: 'lev', at: 'l13', until: 'l15', rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.5, out: 0.01, samples: 0 },
  ],
  cards: [
    { at: 0, until: 1.0, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 'l01', until: 15.7, scrim: 0.9, scrimCenter: 'rgba(20,10,4,0.85)', fadeIn: 0.3, fadeOut: 0.7, lines: [
      { text: 'THE BATTLE OF HATTIN', size: 0.074, y: 0.44, delay: 0.1 },
      { text: '1187', size: 0.07, y: 0.585, delay: 1.1, colorTop: '#ffd9a0', colorBottom: '#e2873a' } ], ornaments: [{ y: 0.35, w: 0.7 }, { y: 0.68, w: 0.7 }] },
    { at: 137.35, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.13, y: 0.43, delay: 0.1, track: 0.14 },
      { text: 'The Battle of Hattin, 1187', size: 0.062, y: 0.6, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.5 }, { y: 0.69, w: 0.5 }] },
  ],
};
