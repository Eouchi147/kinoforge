// The Battle of Gaugamela (331 BC): Battle Map spec. Times come from the cue words (see films/lib/battlemap/SPEC.md).
// Battlefield: x east, z south, 1 unit about 12 m. Macedonians (red) start in the south facing north, Persians (blue) in the north facing south.
// "Right" for Alexander is east (screen right). Darius's left wing is east too, so the Persian line stretches east to follow.
// Stage `asia` is the map of Macedon to India (shown full screen for the setup and for the ending).
const MAC = { team: 'rome' }, PER = { team: 'carthage' };
const L = (at, until, text, o = {}) => ({ at, until, text, ...o });
const I = (at, until, icon, o = {}) => ({ at, until, icon, ...o });

// ------------------------------------------------------------------ the battlefield: a dry plain with a smoothed patch, the Tigris on the east side
const SMOOTH = { c: [-120, 0], r: 118 }; // the ground Darius had levelled
const fieldWorld = {
  seed: 331, size: [960, 520], res: 1, base: 6, meshStep: 2.5,
  sun: { azimuth: 236, elevation: 34 }, sunEve: { azimuth: 268, elevation: 8 },
  style: { contour: 1.5, pxPerUnit: 5.2, palette: [[-2, [0.60, 0.50, 0.32]], [3, [0.74, 0.62, 0.40]], [7, [0.80, 0.67, 0.43]], [10, [0.82, 0.70, 0.46]], [11.4, [0.95, 0.90, 0.72]], [14, [0.97, 0.94, 0.80]], [24, [0.72, 0.62, 0.50]]], paletteSoft: 3, fields: 0.0 },
  features: [
    { type: 'undulate', amp: 3.4, scale: 90 }, { type: 'undulate', amp: 1.0, scale: 30 },
    { type: 'hill', at: [-300, -220], r: [90, 34], h: 22, rot: 8 }, { type: 'hill', at: [130, -235], r: [100, 30], h: 18, rot: -6 }, { type: 'hill', at: [-60, 245], r: [120, 28], h: 16 },
    { type: 'flat', at: SMOOTH.c, r: SMOOTH.r, level: 11.6, soft: 22, amount: 0.985 },
    { type: 'river', name: 'Tigris', path: [[340, -270], [326, -140], [344, -30], [330, 90], [346, 270]], w: 15, depth: 2.6, meander: 7, wl: 5.4 },
    { type: 'woods', at: [380, -190], r: [30, 18] }, { type: 'woods', at: [372, 150], r: [26, 20] },
    { type: 'farms', rect: [372, 0, 40, 120, 0], cell: [14, 12], skip: 0.15 },
  ],
};

// ------------------------------------------------------------------ the map of Macedon to India (full screen for the setup and the ending)
const POS = { macedon: [-330, -40], granicus: [-236, -56], issus: [-118, -22], gauga: [18, -34], babylon: [36, 16], persepolis: [112, 52], greece: [-336, 6], india: [278, 40] };
const asia = {
  world: {
    seed: 331, size: [920, 460], res: 1, base: 0, meshStep: 2.2, sun: { azimuth: 250, elevation: 34 }, sunEve: { azimuth: 284, elevation: 10 },
    style: { contour: 4, pxPerUnit: 6, palette: [[-4, [0.60, 0.72, 0.46]], [3, [0.76, 0.76, 0.46]], [14, [0.82, 0.70, 0.45]], [30, [0.72, 0.58, 0.42]], [48, [0.70, 0.66, 0.62]], [66, [0.95, 0.95, 0.96]]], paletteSoft: 5 },
    features: [
      { type: 'undulate', amp: 4, scale: 90 },
      { type: 'sea', poly: [[-560, -330], [560, -330], [560, 330], [-560, 330]], shelf: 34, depth: 8 },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-520, -300], [520, -300], [520, 10], [420, 12], [385, 30], [350, 68], [322, 125], [300, 160], [282, 125], [262, 72], [236, 50], [206, 52], [178, 58], [150, 66], [128, 60], [110, 40], [86, 16], [62, 2], [36, -2], [8, 2], [-22, -2], [-58, -10], [-90, -6], [-102, -24], [-130, -42], [-170, -50], [-210, -52], [-245, -58], [-268, -48], [-290, -30], [-306, -6], [-322, 12], [-334, 38], [-350, 22], [-362, -12], [-384, -34], [-420, -40], [-520, -42]] },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-100, -2], [-60, 12], [-22, 10], [8, 12], [36, 10], [62, 12], [82, 30], [100, 56], [122, 84], [98, 122], [56, 160], [0, 168], [-50, 150], [-80, 100], [-94, 50]] },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-520, 96], [-300, 96], [-200, 98], [-130, 88], [-100, 104], [-80, 150], [-60, 300], [-520, 300]] },
      { type: 'lake', at: [-150, -170], r: [80, 26] }, { type: 'lake', at: [70, -168], r: [24, 52] },
      { type: 'mountains', path: [[70, -52], [110, -22], [150, 10], [186, 40]], w: 14, h: 40, ridged: 0.8, scale: 40, edge: 14 },
      { type: 'mountains', path: [[190, -120], [250, -76], [306, -30]], w: 14, h: 52, ridged: 0.8, scale: 40, edge: 14 },
      { type: 'river', name: 'Tigris', path: [[24, -120], [26, -60], [40, -6], [62, 6]], w: 3, depth: 1.2, meander: 4 },
      { type: 'river', name: 'Indus', path: [[262, -80], [276, -10], [270, 60], [290, 150]], w: 3, depth: 1.2, meander: 5 },
      { type: 'woods', at: [-300, -130], r: [50, 20] }, { type: 'woods', at: [-60, -120], r: [40, 16] },
      { type: 'farms', rect: [38, 12, 70, 28, 10], cell: [12, 9] },
    ],
  },
  blocks: {
    mk: { ...MAC, kind: 'infantry', x: POS.macedon[0], z: POS.macedon[1], heading: 90, len: 20, dep: 10, height: 4, hidden: true, bannerScale: 1.5 },
    dk: { ...PER, kind: 'infantry', x: POS.gauga[0], z: POS.gauga[1], heading: 270, len: 20, dep: 10, height: 4, hidden: true, bannerScale: 1.5 },
    dk2: { ...PER, kind: 'infantry', x: POS.gauga[0] + 18, z: POS.gauga[1] - 14, heading: 270, len: 18, dep: 10, height: 4, hidden: true },
    dk3: { ...PER, kind: 'infantry', x: POS.gauga[0] + 20, z: POS.gauga[1] + 14, heading: 270, len: 18, dep: 10, height: 4, hidden: true },
    dk4: { ...PER, kind: 'infantry', x: POS.gauga[0] + 38, z: POS.gauga[1], heading: 270, len: 18, dep: 10, height: 4, hidden: true },
    alex: { ...MAC, kind: 'cavalry', x: POS.gauga[0], z: POS.gauga[1], heading: 90, len: 26, dep: 12, height: 4, hidden: true, bannerScale: 1.4 },
  },
  zones: [{ y: 3, p: 3, alpha: 0.42, keys: [
    { t: 'l16.master', c: [70, 0], rx: 0, rz: 0 }, { t: 'l16.master+1.1', c: [70, 0], rx: 150, rz: 78 },
    { t: 'l16.By', c: [70, 0], rx: 150, rz: 78 }, { t: 'l16.By+5', c: [-4, 4], rx: 340, rz: 92 } ] }],
  moves: [
    { block: 'mk', at: 'l02.Alexander', dur: 0.9, appear: true, appearFrom: 30 },
    { block: 'mk', at: 'l02.He', dur: 1.1, path: [[-330, -40], [-290, -52], [-236, -56]], ease: 'inOut' },
    { block: 'mk', at: 'l02.Persians', dur: 1.2, path: [[-236, -56], [-190, -50], [-150, -34], [-118, -22]], ease: 'inOut' },
    { block: 'dk', at: 'l02.Darius', dur: 0.9, appear: true, appearFrom: 30 },
    { blocks: ['dk2', 'dk3', 'dk4'], at: 'l02.biggest', dur: 0.7, stagger: 0.18, appear: true, appearFrom: 24 },
    { block: 'mk', at: 'l02.waiting', dur: 2.6, path: [[-118, -22], [-70, -26], [-24, -30]], ease: 'inOut' },
    // the ending: Alexander's blocks vanish, the empire grows from Persia to Greece and India
    { blocks: ['mk', 'dk', 'dk2', 'dk3', 'dk4'], at: 'l16.Alexander-0.4', dur: 0.2, vanish: true },
    { block: 'alex', at: 'l16.Alexander', dur: 0.9, appear: true, appearFrom: 30 },
  ],
  arrows: [
    { id: 'toGr', at: 'l02.He', until: 'l02.Persians', ease: 'inOut', team: 'rome', style: 'dash', width: 3.2, path: [[-330, -40], [-290, -52], [-236, -56]], head: true, lift: 4, hide: 'l02.Now,' },
    { id: 'toIs', at: 'l02.Persians', until: 'l02.twice.+0.5', ease: 'inOut', team: 'rome', style: 'dash', width: 3.2, path: [[-236, -56], [-190, -50], [-150, -34], [-118, -22]], head: true, lift: 4, hide: 'l02.Now,' },
    { id: 'toDa', at: 'l02.waiting', until: 'l02.yet.', ease: 'inOut', team: 'rome', style: 'dash', width: 3.2, path: [[-118, -22], [-70, -26], [-24, -30]], head: true, lift: 4, hide: 'l03.Darius' },
    { id: 'spread', at: 'l16.stretched', until: 'l16.India.', ease: 'inOut', team: 'gold', width: 5, path: [[-336, 4], [-200, 0], [-60, 12], [90, 40], [270, 38]], head: true, lift: 8, hide: 'l16.never' },
  ],
  labels: [
    L('l02.Macedon.', 'l02.He', 'MACEDON', { pos: POS.macedon, y: 4, team: 'rome', dy: -0.2, big: true }),
    L('l02.Alexander', 'l02.Macedon.', 'ALEXANDER', { pos: POS.macedon, y: 6, team: 'rome', dy: -0.2, big: true }),
    L('l02.beaten', 'l02.Persians', 'WIN ONE: GRANICUS', { pos: POS.granicus, y: 4, team: 'rome', dy: -0.2, dx: 0.04 }),
    L('l02.twice.', 'l02.Now,', 'WIN TWO: ISSUS', { pos: POS.issus, y: 4, team: 'rome', dy: -0.2, dx: 0.02 }),
    L('l02.Darius', 'l02.great', 'DARIUS THE THIRD', { pos: POS.gauga, y: 8, team: 'carthage', dy: -0.2, dx: 0.0, big: true }),
    L('l02.great', 'l02.waiting', 'GREAT KING OF PERSIA', { pos: POS.gauga, y: 8, team: 'carthage', dy: -0.2, dx: 0.0 }),
    L('l02.waiting', 'l02.biggest', 'WAITING', { pos: POS.gauga, y: 8, team: 'carthage', dy: -0.2, big: true }),
    L('l02.biggest', 'l03.Darius', 'HIS BIGGEST ARMY YET', { pos: POS.gauga, y: 8, team: 'carthage', dy: -0.32, big: true }),
    L('l02.Persians', 'l02.twice.', 'PERSIAN EMPIRE', { pos: [100, -40], leader: false, team: 'carthage' }),
    L('l16.master', 'l16.He', 'THE PERSIAN EMPIRE', { pos: [40, 10], y: 6, dy: -0.1, leader: false, big: true, team: 'rome' }),
    L('l16.Greece', 'l16.never', 'GREECE', { pos: POS.greece, y: 8, dy: -0.12, leader: false, big: true }),
    L('l16.India.', 'l16.never', 'INDIA', { pos: POS.india, y: 8, dy: -0.12, leader: false, big: true }),
    L('l16.He', 'l16.By', 'AGE 25', { screen: [0.5, 0.12], big: true, size: 1.7, team: 'rome' }),
    L('l16.By', 'l16.never', 'AGE 30', { screen: [0.5, 0.12], big: true, size: 1.7, team: 'rome' }),
    L('l16.never', 147.05, 'NEVER LOST A BATTLE', { screen: [0.5, 0.12], big: true, size: 1.3, team: 'rome' }),
  ],
  icons: [
    I('l02.Alexander', 'l02.He', 'crown', { block: 'mk', size: 18, dy: -0.03, anim: 'bounce' }),
    I('l02.beaten+0.7', 'l02.Now,', 'swords', { pos: POS.granicus, y: 2, size: 20 }),
    I('l02.twice.', 'l02.Now,', 'swords', { pos: POS.issus, y: 2, size: 20 }),
    I('l02.Darius', 'l03.Darius', 'crown', { block: 'dk', team: 'carthage', size: 18, dy: -0.03, anim: 'bounce' }),
    I('l02.waiting', 'l02.biggest', 'clock', { pos: [60, -50], y: 6, size: 22, anim: 'bounce' }),
    I('l16.Alexander', 'l16.master', 'crown', { block: 'alex', size: 20, dy: -0.04, anim: 'bounce' }),
    I('l16.master', 'l16.He', 'crown', { pos: [40, 6], y: 10, size: 26, anim: 'bounce' }),
    I('l16.Greece', 'l16.never', 'city', { pos: POS.greece, y: 4, size: 22 }),
    I('l16.India.', 'l16.never', 'city', { pos: POS.india, y: 4, size: 22 }),
    I('l16.never', 147.05, 'laurel', { screen: [0.5, 0.73], size: 0.3, anim: 'bounce' }),
    I('l16.never+0.2', 147.05, 'star', { screen: [0.36, 0.7], size: 0.12, anim: 'bounce' }),
    I('l16.never+0.35', 147.05, 'star', { screen: [0.64, 0.7], size: 0.12, anim: 'bounce' }),
  ],
  camera: [
    { at: 18.3, target: [-250, -30], width: 460, pitch: 64, yaw: 0, mm: 35 },
    { at: 'l02.Alexander', target: [-262, -30], width: 400, pitch: 63, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.He', target: [-225, -34], width: 420, pitch: 63, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.Persians', target: [-185, -32], width: 400, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.Now,', target: [-90, -28], width: 560, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.Darius', target: [-40, -26], width: 470, pitch: 60, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.biggest', target: [-20, -30], width: 360, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.yet.', target: [-18, -30], width: 340, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 135.8, target: [40, -4], width: 520, pitch: 64, yaw: 0, mm: 35 },
    { at: 'l16.master', target: [40, -4], width: 500, pitch: 64, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.By', target: [-4, 6], width: 860, pitch: 64, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.never', target: [-4, 6], width: 900, pitch: 66, yaw: 0, mm: 35, ease: 'inOut' },
  ],
};

// ------------------------------------------------------------------ the armies on the plain
const PITCH = 50, ROW1 = -92, ROW2 = -114;
const PL = [], PB = [], PC = [], blocks = {}, moves = [], arrows = [], labels = [], icons = [], counters = [], volleys = [];
for (let k = 0; k < 8; k++) {
  blocks['pl' + k] = { ...PER, kind: 'infantry', x: (k - 3.5) * PITCH, z: ROW1, heading: 180, len: 44, dep: 20, hidden: true, bannerScale: 0.9 }; PL.push('pl' + k);
  blocks['pb' + k] = { ...PER, kind: 'infantry', x: (k - 3.5) * PITCH, z: ROW2, heading: 180, len: 44, dep: 16, hidden: true, bannerScale: 0.8 }; PB.push('pb' + k);
  blocks['pc' + k] = { ...PER, kind: 'infantry', x: (k - 3.5) * PITCH, z: ROW2 - 22, heading: 180, len: 44, dep: 16, hidden: true, bannerScale: 0.8 }; PC.push('pc' + k);
}
Object.assign(blocks, {
  dar: { ...PER, kind: 'elite', x: 0, z: -160, heading: 180, len: 34, dep: 16, hidden: true, bannerScale: 1.4 },
  pcavE1: { ...PER, kind: 'cavalry', x: 225, z: -96, heading: 180, len: 36, dep: 14, hidden: true, bannerScale: 0.9 },
  pcavE2: { ...PER, kind: 'cavalry', x: 225, z: -122, heading: 180, len: 36, dep: 14, hidden: true, bannerScale: 0.9 },
  pcavW: { ...PER, kind: 'cavalry', x: -225, z: -98, heading: 180, len: 36, dep: 14, hidden: true, bannerScale: 0.9 },
  mac: { ...MAC, kind: 'infantry', x: -75, z: 96, heading: 0, len: 140, dep: 32, grid: { cols: 6, ranks: 2, gap: 3 }, count: 47000, hidden: true, bannerScale: 1.2 },
  parm: { ...MAC, kind: 'elite', x: -150, z: 92, heading: 0, len: 50, dep: 22, hidden: true, bannerScale: 1.1 },
  comp: { ...MAC, kind: 'cavalry', x: 22, z: 92, heading: 0, len: 36, dep: 14, hidden: true, bannerScale: 1.3 },
  rear: { ...MAC, kind: 'infantry', x: -75, z: 130, heading: 0, len: 130, dep: 10, hidden: true, bannerScale: 0.8 },
  // hook: a young king's small block against a vast host
  king: { ...MAC, kind: 'infantry', x: -190, z: 20, heading: 90, len: 28, dep: 14, height: 4, hidden: true, bannerScale: 1.8 },
  emp: { ...PER, kind: 'infantry', x: 40, z: 10, heading: 270, len: 250, dep: 150, grid: { cols: 4, ranks: 5, gap: 4 }, hidden: true, bannerScale: 0.9 },
});
const PERSIANS = [...PL, ...PB, ...PC];
const MARCH = 120, PARM_MARCH = 50, S_LANE = 16;
const laneX = [...Array(5)].map((_, i) => -75 + MARCH + (i - 2) * (140 / 6 - 2.5 + 3 + S_LANE));  // x of the five lanes between the six Macedonian columns
const colBlocks = (i) => [`mac.${i}.0`, `mac.${i}.1`];

// ---- moves
moves.push(
  // hook
  { block: 'king', at: 'l00.young', dur: 0.8, appear: true, appearFrom: 26 },
  { group: 'emp', at: 'l00.most', dur: 0.7, stagger: 0.14, appear: true, appearFrom: 30 },
  { block: 'king', at: 'l00.outnumbered,', dur: 0.5, to: { scale: 0.84 }, ease: 'out' },
  { block: 'king', at: 'l00.plan', dur: 0.4, to: { scale: 1.0 }, ease: 'out' },
  { blocks: ['king', 'emp'], at: 14.1, dur: 0.4, vanish: true },
  // Darius's army takes the plain
  { blocks: PL, at: 'l03.chose', dur: 0.7, stagger: 0.09, appear: true, appearFrom: 20 },
  { blocks: PB, at: 'l03.chose+0.5', dur: 0.7, stagger: 0.09, appear: true, appearFrom: 20 },
  { blocks: PC, at: 'l03.chose+0.9', dur: 0.7, stagger: 0.09, appear: true, appearFrom: 20 },
  { blocks: ['pcavW', 'pcavE1', 'pcavE2'], at: 'l03.chose+1.3', dur: 0.7, stagger: 0.12, appear: true, appearFrom: 20 },
  { block: 'dar', at: 'l03.chose+1.9', dur: 0.7, appear: true, appearFrom: 22 },
  // Alexander's army and the numbers
  { group: 'mac', at: 'l05.Alexander', dur: 0.7, stagger: 0.07, appear: true, appearFrom: 22 },
  { blocks: ['parm', 'comp', 'rear'], at: 'l05.Alexander+0.75', dur: 0.7, stagger: 0.15, appear: true, appearFrom: 22 },
  { blocks: PERSIANS, at: 'l05.far', dur: 0.25, to: { scale: 1.12 }, ease: 'out' }, { blocks: PERSIANS, at: 'l05.far+0.25', dur: 0.6, to: { scale: 1 }, ease: 'inOut' },
  // the sideways march
  { group: 'mac', at: 'l06.marched', dur: 6.6, by: { x: MARCH }, ease: 'inOut' },
  { blocks: ['comp', 'rear'], at: 'l06.marched', dur: 6.6, by: { x: MARCH }, ease: 'inOut' },
  { block: 'parm', at: 'l06.marched', dur: 6.6, by: { x: PARM_MARCH }, ease: 'inOut' },
);
// Darius follows: the line stretches east (block k slides east by 10 k); his guard keeps the middle
PERSIANS.forEach((id, n) => { const k = n % 8; moves.push({ block: id, at: 'l07.follow,', dur: 2.7, by: { x: 10 * k }, ease: 'inOut' }); });
moves.push(
  { blocks: ['pcavE1', 'pcavE2'], at: 'l07.follow,', dur: 2.7, by: { x: 70 }, ease: 'inOut' },
  { block: 'dar', at: 'l07.follow,', dur: 2.7, by: { x: 35 }, ease: 'inOut' },
  // the chariot charge: the Macedonian columns step apart into lanes, the chariots pass, the lanes close
);
for (let i = 0; i < 6; i++) for (const id of colBlocks(i)) moves.push({ block: id, at: 'l08.soldiers', dur: 1.5, by: { x: (i - 2.5) * S_LANE }, ease: 'inOut' });
for (let i = 0; i < 6; i++) for (const id of colBlocks(i)) moves.push({ block: id, at: 'l08.So', dur: 1.1, by: { x: -(i - 2.5) * S_LANE }, ease: 'inOut' });
// the horsemen ride around Alexander's right; a gap opens in the Persian centre
PERSIANS.forEach((id, n) => { const k = n % 8; moves.push({ block: id, at: 'l09.gap', dur: 1.8, by: { x: k >= 4 ? 14 : -14 }, ease: 'inOut' }); });
moves.push(
  { block: 'pcavE1', at: 'l09.horsemen', dur: 4.2, path: [[295, -96], [292, -30], [262, 50], [212, 112], [160, 144]], ease: 'inOut' },
  { block: 'pcavE2', at: 'l09.horsemen+0.5', dur: 4.2, path: [[295, -122], [300, -40], [272, 50], [224, 118], [176, 150]], ease: 'inOut' },
  // the Companion cavalry: gather into a giant wedge and charge into the gap
  { block: 'comp', at: 'l11.formed', dur: 1.6, to: { scale: 1.9 }, ease: 'inOut' },
  { block: 'comp', at: 'l11.charged', dur: 2.6, path: [[142, 92], [118, 40], [80, -30], [46, -108], [36, -150]], ease: 'inQuad' },
  // Darius turns and flees east
  { block: 'dar', at: 'l12.turned', dur: 0.5, to: { heading: 90 }, ease: 'out' },
  { block: 'dar', at: 'l12.turned+0.3', dur: 3.4, path: [[35, -160], [110, -182], [200, -192]], ease: 'in' },
  // Parmenion's wing is attacked; Alexander turns back
  { block: 'pcavW', at: 'l13.Meanwhile,', dur: 3.6, path: [[-225, -98], [-214, -30], [-170, 44], [-118, 80]], ease: 'inOut' },
  { block: 'parm', at: 'l13.trouble.', dur: 0.4, to: { lift: 1.4 }, ease: 'out' }, { block: 'parm', at: 'l13.trouble.+0.4', dur: 0.4, to: { lift: 0 }, ease: 'in' },
  { block: 'parm', at: 'l13.serious', dur: 1.8, to: { scale: 0.84 }, ease: 'inOut' },
  { block: 'comp', at: 'l13.turn', dur: 3.4, path: [[36, -150], [-6, -96], [-50, -22], [-88, 56]], ease: 'inOut' },
  { block: 'comp', at: 'l13.turn', dur: 1.2, to: { scale: 1.2 }, ease: 'inOut' },
  { block: 'pcavW', at: 'l14.Persians', dur: 0.6, vanish: true },
  // the Persian army falls apart: blocks wobble, drift away and fade by numbers
  { blocks: PERSIANS, at: 'l14.fell', dur: 0.22, stagger: 0.03, to: { heading: 200 }, ease: 'out' },
  { blocks: PERSIANS, at: 'l14.fell+0.35', dur: 0.22, stagger: 0.03, to: { heading: 160 }, ease: 'out' },
  { blocks: PERSIANS, at: 'l14.fell+0.7', dur: 0.22, stagger: 0.03, to: { heading: 190 }, ease: 'out' },
  { blocks: PERSIANS, at: 'l14.fell', dur: 2.6, stagger: 0.06, fadeTo: 1, alphaTo: 0.1, sinkTo: 0.9 },
  { blocks: ['pcavE1', 'pcavE2'], at: 'l14.fell', dur: 1.6, stagger: 0.2, fadeTo: 1, alphaTo: 0.1, sinkTo: 0.9 },
  // Darius runs on to the east, over the Tigris
  { block: 'dar', at: 'l15.ran', dur: 3.8, path: [[200, -192], [300, -196], [384, -200]], ease: 'inOut' },
);

// ---- arrows
// every arrow carries an id when an icon follows it
arrows.push(
  // hook: the plan that looks completely mad (a squiggle)
  { id: 'mad', at: 'l00.plan', until: 'l00.mad.', ease: 'inOut', team: 'rome', width: 5, path: [[-170, 20], [-140, -22], [-112, 46], [-84, -40], [-56, 52], [-28, -30], [0, 38], [24, -12], [48, 18]], lift: 6, hide: 14.0, head: true },
  // the smoothing roller goes up and down the plain
  { id: 'roll', at: 'l03.ground', until: 'l03.flat#1+0.3', ease: 'linear', team: 'cream', width: 6, style: 'dash', path: [[-205, -70], [-40, -70], [-40, -36], [-205, -36], [-205, -2], [-40, -2], [-40, 32], [-205, 32], [-205, 66], [-40, 66]], smooth: false, lift: 4, hide: 'l03.Why?' },
  // chariots show off on the smooth ground (full speed)
  ...[-150, -90, -30, 30, 90, 150].map((x, i) => ({ id: 'dem' + i, at: 'l04.charge', until: 'l04.speed.', ease: 'in', team: 'carthage', width: 4, path: [[x, -72], [x + (i % 2 ? 6 : -6), 24]], lift: 5, hide: 'l05.Alexander' })),
  // straight ahead would be the usual plan; the sideways march
  { id: 'ahead', at: 'l06.straight', until: 'l06.ahead,', ease: 'out', team: 'rome', width: 6, path: [[-75, 70], [-75, -50]], lift: 6, hide: 'l06.he' },
  { id: 'side', at: 'l06.sideways', until: 'l06.right,', ease: 'out', team: 'rome', width: 7, path: [[-75, 60], [-20, 60], [45, 60]], lift: 6, hide: 'l06.further' },
  { id: 'side2', at: 'l06.further', until: 'l06.further#1+0.7', ease: 'out', team: 'rome', width: 7, path: [[45, 60], [90, 60], [150, 60]], lift: 6, hide: 'l07.Darius' },
  // Darius's line follows
  { id: 'dfollow', at: 'l07.follow,', until: 'l07.keep', ease: 'inOut', team: 'carthage', width: 11, path: [[30, -66], [100, -66], [190, -66]], lift: 6, hide: 'l08.Then', head: true },
  // chariot charge: five lanes between the Macedonian columns
  ...laneX.map((x, i) => ({ id: 'ch' + i, at: 'l08.chariots', until: 'l08.stopped+0.7', ease: 'linear', team: 'carthage', width: 3.4, style: 'dash', path: [[x, -72], [x, 120]], lift: 4, hide: 'l08.So' })),
  // horsemen go around Alexander's right
  { id: 'around', at: 'l09.horsemen', until: 'l09.stretched+0.6', ease: 'inOut', team: 'carthage', width: 6, path: [[295, -96], [292, -30], [262, 50], [212, 112], [160, 144]], lift: 6, hide: 'l10.That', head: true },
  // the wedge charge (gold) and Darius's flight
  { id: 'wedge', at: 'l11.charged', until: 'l11.Darius.', ease: 'inQuad', team: 'gold', width: 8, path: [[142, 92], [118, 40], [80, -30], [46, -108], [36, -150]], lift: 8, hide: 'l12.Darius', head: true },
  { id: 'flee', at: 'l12.turned+0.3', until: 'l12.fled.+0.7', ease: 'in', team: 'carthage', width: 5, style: 'dash', path: [[35, -160], [110, -182], [200, -192]], lift: 6, hide: 'l13.Meanwhile,', head: true },
  { id: 'wing', at: 'l13.Meanwhile,', until: 'l13.side,', ease: 'out', team: 'carthage', width: 6, path: [[-225, -98], [-214, -30], [-170, 44], [-122, 76]], lift: 6, hide: 'l14.When', head: true },
  { id: 'back', at: 'l13.turn', until: 'l13.help', ease: 'inOut', team: 'gold', width: 8, path: [[36, -150], [-6, -96], [-50, -22], [-88, 56]], lift: 8, hide: 'l14.When', head: true },
  { id: 'east', at: 'l15.ran', until: 'l15.east.+0.9', ease: 'inOut', team: 'carthage', width: 5, style: 'dash', path: [[200, -192], [300, -196], [384, -200]], lift: 6, hide: 'l16.Alexander', head: true },
);

// ---- labels
labels.push(
  // hook
  { at: 1.4, until: 'l00.young', text: '331 BC', screen: [0.5, 0.17], style: 'text', big: true, size: 1.9, track: 0.16, weight: 800 },
  L('l00.young', 'l00.most', 'A YOUNG KING', { block: 'king', team: 'rome', dy: 0.13, big: true }),
  L('l00.most', 'l00.outnumbered,', 'THE MOST POWERFUL EMPIRE ON EARTH', { block: 'emp', team: 'carthage', dy: -0.1, dx: -0.16, big: true, size: 0.8 }),
  L('l00.outnumbered,', 'l00.plan', 'OUTNUMBERED', { block: 'king', team: 'rome', dy: 0.13, big: true }),
  L('l00.plan', 'l00>', 'A PLAN THAT LOOKS COMPLETELY MAD', { screen: [0.5, 0.88], big: true, size: 0.95 }),
  // the plain
  L('l03.Darius', 'l03.chose', 'DARIUS', { block: 'dar', team: 'carthage', dy: -0.12, big: true }),
  L('l03.wide', 'l03.near', 'A WIDE, FLAT PLAIN', { screen: [0.5, 0.11], big: true }),
  L('l03.Tigris', 'l03.in', 'THE TIGRIS RIVER', { pos: [340, 0], y: 8, dy: -0.12, dx: -0.06, big: true }),
  L('l03.northern', 'l03.He', 'NORTHERN IRAQ TODAY', { screen: [0.5, 0.11], big: true }),
  L('l03.smooths', 'l03.Why?', 'SMOOTHED FLAT', { pos: SMOOTH.c, y: 12, dy: -0.12, leader: false, big: true }),
  L('l03.Why?', 'l03.secret', 'WHY?', { screen: [0.5, 0.11], big: true }),
  L('l03.secret', 'l04.Scythe', 'THE SECRET WEAPON', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  // chariots
  L('l04.Chariots.', 'l04.War', 'SCYTHED CHARIOTS', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l04.blades', 'l04.On', 'BLADES ON THE WHEELS', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l04.smooth', 'l04.they', 'SMOOTH GROUND, NO BUMPS', { screen: [0.5, 0.11], big: true }),
  L('l04.charge', 'l05.Alexander', 'FULL SPEED', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  // numbers
  L('l05.Alexander', 'l05.47', 'ALEXANDER\'S ARMY', { block: 'mac', team: 'rome', dy: -0.28, big: true }),
  L('l05.far', 'l05.Nobody', 'FAR MORE', { block: 'pb3', team: 'carthage', dy: -0.2, big: true, size: 1.4 }),
  L('l05.Nobody', 'l05.Ancient', 'NOBODY KNOWS EXACTLY', { screen: [0.5, 0.11], big: true }),
  L('l05.Ancient', 'l05.truly', 'ANCIENT WRITERS MADE UP NUMBERS', { screen: [0.5, 0.11], big: true, size: 0.9 }),
  L('l05.truly', 'l06.Alexander', 'TRULY RIDICULOUS', { screen: [0.5, 0.11], big: true, team: 'rome' }),
  // the sideways march
  L('l06.Alexander', 'l06.Instead', 'ALEXANDER\'S PLAN', { block: 'comp', team: 'rome', dy: -0.2, big: true }),
  L('l06.straight', 'l06.he', 'NOT STRAIGHT AHEAD', { screen: [0.5, 0.11], big: true }),
  L('l06.sideways', 'l06.further', 'SIDEWAYS, TO THE RIGHT', { screen: [0.5, 0.11], big: true, team: 'rome' }),
  L('l06.further', 'l06.off', 'FURTHER AND FURTHER', { screen: [0.5, 0.11], big: true, team: 'rome' }),
  L('l06.off', 'l07.Darius', 'OFF THE SMOOTH GROUND', { screen: [0.5, 0.11], big: true }),
  // Darius follows
  L('l07.Darius', 'l07.stretching', 'DARIUS HAS TO FOLLOW', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l07.stretching', 'l08.Then', 'STRETCHING HIS LONG LINE', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  // the charge
  L('l08.chariots', 'l08.Alexander', 'THE CHARIOTS CHARGE', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l08.Alexander', 'l08.The#1', 'SOLDIERS STEP ASIDE', { screen: [0.5, 0.11], big: true, team: 'rome' }),
  L('l08.The#1', 'l08.stopped', 'RATTLING STRAIGHT THROUGH', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l08.stopped', 'l08.So', 'STOPPED AT THE BACK', { screen: [0.5, 0.11], big: true, team: 'rome' }),
  L('l08.So', 'l09.Darius', 'SO MUCH FOR THE SECRET WEAPON', { screen: [0.5, 0.11], big: true }),
  // horsemen and the gap
  L('l09.Darius', 'l09.as', 'PERSIAN HORSEMEN RIDE AROUND', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l09.stretched', 'l09.gap', 'STRETCHING FURTHER AND FURTHER', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l09.gap', 'l10.That', 'A GAP OPENS', { pos: [35, -108], y: 8, dy: -0.2, big: true }),
  L('l10.That', 'l10.Alexander', 'EXACTLY WHAT ALEXANDER WAITED FOR', { screen: [0.5, 0.11], big: true, team: 'rome', size: 0.9 }),
  // the wedge
  L('l11.formed', 'l11.charged', 'THE BEST CAVALRY, A GIANT WEDGE', { screen: [0.5, 0.11], big: true, team: 'rome', size: 0.9 }),
  L('l11.charged', 'l11.straight#1', 'CHARGE INTO THE GAP', { screen: [0.5, 0.11], big: true, team: 'rome' }),
  L('l11.straight#1', 'l12.Darius', 'STRAIGHT AT DARIUS', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l12.Darius', 'l12.fled.', 'DARIUS TURNS AROUND', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l12.fled.', 'l13.Meanwhile,', 'AND FLEES', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  // Parmenion
  L('l13.Meanwhile,', 'l13.Alexander', 'MEANWHILE, ON THE OTHER SIDE', { screen: [0.5, 0.11], big: true, size: 0.9 }),
  L('l13.Parmen', 'l13.serious', 'PARMENION', { block: 'parm', team: 'rome', dy: -0.16, big: true }),
  L('l13.serious', 'l13.Alexander', 'IN SERIOUS TROUBLE', { block: 'parm', team: 'rome', dy: -0.16, big: true }),
  L('l13.Alexander', 'l14.When', 'ALEXANDER TURNS BACK TO HELP', { screen: [0.5, 0.11], big: true, team: 'rome', size: 0.9 }),
  // the army falls apart
  L('l14.When', 'l14.their#1', 'THE KING HAS FLED', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l14.army', 'l15.Darius', 'THE ARMY FALLS APART', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  // Darius's end
  L('l15.Darius', 'l15.Within', 'DARIUS RUNS EAST', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
  L('l15.Within', 'l15.killed', 'WITHIN A YEAR', { screen: [0.5, 0.11], big: true }),
  L('l15.killed', 'l16.Alexander', 'KILLED BY HIS OWN OFFICERS', { screen: [0.5, 0.11], big: true, team: 'carthage', size: 0.9 }),
);
// ---- counters (the only number given in the film)
counters.push({ at: 'l05.47', until: 'l05.Darius', block: 'mac', team: 'rome', from: 0, to: 47000, countDur: 1.1, step: 1000, suffix: 'MEN, ABOUT', dy: -0.18 });

// ---- icons
icons.push(
  // hook
  I('l00.king', 'l00.most', 'crown', { block: 'king', size: 20, dy: -0.04, anim: 'bounce' }),
  I('l00.outnumbered,', 'l00.plan', 'question', { block: 'king', size: 24, dy: -0.04, dx: 0.06, anim: 'bounce' }),
  I('l00.completely', 14.0, 'spiral', { screen: [0.5, 0.68], size: 0.2, anim: 'sway' }),
  // the plain: roller gag, sparkles, a mystery
  I('l03.ground', 'l03.Why?', 'roller', { follow: 'roll', size: 46 }),
  I('l03.flat#1', 'l03.secret', 'star', { pos: [-170, -40], y: 12, size: 18, anim: 'bounce' }),
  I('l03.flat#1+0.15', 'l03.secret', 'star', { pos: [-100, 30], y: 12, size: 16, anim: 'bounce' }),
  I('l03.flat#1+0.3', 'l03.secret', 'star', { pos: [-150, 50], y: 12, size: 20, anim: 'bounce' }),
  I('l03.flat#1+0.45', 'l03.secret', 'star', { pos: [-80, -50], y: 12, size: 15, anim: 'bounce' }),
  I('l03.Why?', 'l03.secret', 'question', { screen: [0.5, 0.58], size: 0.3, anim: 'bounce' }),
  // scythed chariots
  I('l04.Chariots.', 'l04.War', 'chariot', { screen: [0.5, 0.88], size: 0.5, anim: 'bounce' }),
  I('l04.Chariots#1', 'l04.sharp', 'chariot', { screen: [0.5, 0.88], size: 0.5, anim: 'bounce' }),
  I('l04.sharp', 'l04.On', 'wheel', { screen: [0.5, 0.86], size: 0.62, anim: 'bounce' }),
  ...[-150, -90, -30, 30, 90, 150].map((x, i) => I('l04.Chariots.', 'l04.charge', 'chariot', { pos: [x, -72], y: 3, size: 30, anim: 'bounce' })),
  ...[0, 1, 2, 3, 4, 5].map((i) => I('l04.charge', 'l05.Alexander', 'chariot', { follow: 'dem' + i, fill: 'fast', size: 32 })),
  // numbers and the silly numbers
  I('l05.Nobody', 'l05.Ancient', 'question', { screen: [0.5, 0.6], size: 0.26, anim: 'bounce' }),
  I('l05.Ancient', 'l05.truly', 'book', { screen: [0.5, 0.64], size: 0.24, anim: 'sway' }),
  I('l05.truly', 'l06.Alexander', 'strike', { screen: [0.5, 0.5], size: 0.19, fill: '1,000,000?' }),
  I('l05.ridiculous', 'l06.Alexander', 'strike', { screen: [0.5, 0.68], size: 0.19, fill: '800,000?' }),
  I('l05.Alexander', 'l06.Alexander', 'crown', { block: 'comp', size: 16, dy: -0.04, anim: 'bounce' }),
  // sideways
  I('l06.Alexander', 'l06.Instead', 'crown', { block: 'comp', size: 18, dy: -0.04, anim: 'bounce' }),
  I('l06.he', 'l06.sideways', 'no', { pos: [-75, -20], y: 8, size: 30 }),
  I('l06.marched', 'l07.Darius', 'crown', { block: 'comp', size: 18, dy: -0.04, anim: 'bounce' }),
  I('l06.off', 'l07.Darius', 'exclaim', { pos: [-30, 20], y: 12, size: 34, anim: 'bounce' }),
  I('l07.stretching', 'l08.Then', 'sweat', { block: 'pl7', size: 24, dy: -0.04, anim: 'bounce' }),
  // the chariot charge in five lanes
  ...laneX.map((_, i) => I('l08.chariots', 'l08.So', 'chariot', { follow: 'ch' + i, fill: 'fast', size: 24, fallAt: 'l08.stopped+0.7', fallDur: 0.8 })),
  I('l08.soldiers', 'l08.The#1', 'helmet', { block: 'mac', team: 'rome', size: 15, dy: -0.06, anim: 'sway' }),
  ...laneX.map((x, i) => I('l08.stopped+0.65', 'l08.So', 'burst', { pos: [x, 118], y: 6, size: 20 })),
  I('l08.stopped+0.7', 'l09.Darius', 'no', { pos: [45, 128], y: 6, size: 34 }),
  I('l08.So', 'l09.Darius', 'sweat', { block: 'dar', size: 28, dy: -0.04, anim: 'bounce' }),
  // horsemen and the gap
  I('l09.horsemen', 'l09.as', 'helmet', { block: 'pcavE1', team: 'carthage', size: 20, dy: -0.04, anim: 'sway' }),
  I('l10.That', 'l11.He', 'bulb', { block: 'comp', size: 26, dy: -0.06, dx: 0.02, anim: 'bounce' }),
  I('l10.Alexander', 'l11.He', 'crown', { block: 'comp', size: 18, dy: -0.04, anim: 'bounce' }),
  // the wedge
  I('l11.formed', 'l11.charged', 'crown', { block: 'comp', size: 20, dy: -0.04, anim: 'bounce' }),
  I('l11.charged', 'l12.Darius', 'crown', { follow: 'wedge', size: 24 }),
  I('l11.Darius.', 'l12.turned', 'chariot', { pos: [35, -164], y: 2, size: 44, fill: 'royal', flip: true, anim: 'bounce' }),
  I('l11.Darius.', 'l12.turned', 'exclaim', { pos: [35, -164], y: 40, size: 34, dx: 0.0, anim: 'bounce' }),
  I('l12.turned', 'l13.Meanwhile,', 'chariot', { follow: 'flee', fill: 'royalfast', size: 44 }),
  I('l12.turned+0.1', 'l12.fled.', 'puff', { pos: [38, -164], y: 2, size: 50 }),
  I('l12.around', 'l13.Meanwhile,', 'sweat', { follow: 'flee', size: 16, dx: -0.04, dy: -0.12, anim: 'bounce' }),
  // Parmenion
  I('l13.Parmen', 'l13.Alexander', 'sweat', { block: 'parm', size: 26, dy: -0.07, dx: 0.03, anim: 'bounce' }),
  I('l13.serious', 'l13.Alexander', 'exclaim', { block: 'parm', size: 28, dy: -0.07, dx: -0.04, anim: 'bounce' }),
  I('l13.Alexander', 'l14.When', 'crown', { follow: 'back', size: 24 }),
  I('l13.help', 'l14.When', 'helmet', { block: 'parm', team: 'rome', size: 22, dy: -0.06, anim: 'sway' }),
  // the end of the army
  I('l14.king', 'l14.fled,', 'crown', { screen: [0.5, 0.62], size: 0.22, anim: 'bounce' }),
  ...[['pl2', 0], ['pl4', 0.15], ['pl6', 0.3], ['pb1', 0.45], ['pb5', 0.6]].map(([b, d]) => I('l14.realized+' + d, 'l15.Darius', 'question', { block: b, size: 22, dy: -0.04, anim: 'bounce' })),
  // Darius's end: a crown falls, no more
  I('l15.east.', 'l15.dead,', 'chariot', { follow: 'east', fill: 'royalfast', size: 40 }),
  I('l15.Within', 'l15.dead,', 'calendar', { screen: [0.5, 0.62], size: 0.26, anim: 'bounce' }),
  I('l15.dead,', 'l16.Alexander', 'crown', { pos: [384, -200], y: 22, size: 34, fallAt: 'l15.dead,+0.6', fallDur: 1.0 }),
  I('l15.killed', 'l16.Alexander', 'helmet', { pos: [372, -200], y: 4, size: 22, team: 'carthage', anim: 'sway' }),
  I('l15.killed+0.2', 'l16.Alexander', 'helmet', { pos: [398, -196], y: 4, size: 22, team: 'carthage', anim: 'sway' }),
  I('l15.officers.', 'l16.Alexander', 'helmet', { pos: [385, -180], y: 4, size: 22, team: 'carthage', anim: 'sway' }),
);

// ---- camera
const cam = [
  // hook: low and soaring over the young king, then a pull back to show the vast host
  { at: 0, target: [-185, 20], dist: 110, pitch: 15, yaw: 24, mm: 30 },
  { at: 'l00.young', target: [-185, 20], dist: 90, pitch: 14, yaw: 16, mm: 30, ease: 'inOut' },
  { at: 'l00.most', target: [-80, 10], dist: 400, pitch: 30, yaw: 0, mm: 30, ease: 'inOut' },
  { at: 'l00.outnumbered,', target: [-70, 10], dist: 430, pitch: 34, yaw: 0, mm: 30, ease: 'linear' },
  { at: 'l00.plan', target: [-60, 8], width: 400, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 13.6, target: [-60, 8], width: 410, pitch: 64, yaw: 0, mm: 35, ease: 'linear' },
  // the plain (main stage, after the asia inset)
  { at: 31.8, target: [30, 0], width: 760, pitch: 52, yaw: 0, mm: 35, cut: true },
  { at: 'l03.wide', target: [-60, 0], width: 600, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l03.Tigris', target: [100, 0], width: 700, pitch: 50, yaw: 14, mm: 35, ease: 'inOut' },
  { at: 'l03.He', target: [-100, 0], width: 520, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l03.ground', target: [-120, 0], width: 330, pitch: 60, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l03.Why?', target: [-60, -20], width: 520, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l04.Scythe', target: [0, -70], dist: 190, pitch: 28, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l04.blades', target: [0, -72], dist: 150, pitch: 24, yaw: 6, mm: 35, ease: 'inOut' },
  { at: 'l04.smooth', target: [-20, -30], width: 520, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l05.Alexander', target: [-70, 0], width: 560, pitch: 44, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l05.Darius', target: [-30, -20], width: 600, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l05.Nobody', target: [-20, -20], width: 640, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l06.Alexander', target: [-60, 10], width: 540, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l06.marched', target: [-20, 20], width: 600, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l06.further', target: [30, 20], width: 600, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l07.Darius', target: [50, -10], width: 700, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l08.Then', target: [50, 10], width: 520, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l08.Alexander', target: [50, 30], width: 400, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l08.The#1', target: [50, 70], width: 300, pitch: 36, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l08.stopped', target: [50, 100], width: 280, pitch: 34, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l08.So', target: [60, 20], width: 620, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l09.Darius', target: [120, -10], width: 640, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l09.as', target: [90, -10], width: 580, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l09.gap', target: [40, -90], width: 360, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l10.That', target: [60, -30], width: 460, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l11.formed', target: [90, 10], width: 420, pitch: 40, yaw: 8, mm: 35, ease: 'inOut' },
  { at: 'l11.charged', target: [80, -30], width: 430, pitch: 38, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l11.Darius.', target: [45, -135], width: 270, pitch: 36, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l12.turned', target: [62, -148], width: 250, pitch: 34, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l12.fled.', target: [130, -172], width: 330, pitch: 38, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l13.Meanwhile,', target: [-120, 0], width: 400, pitch: 46, yaw: 0, mm: 35, cut: true },
  { at: 'l13.Alexander', target: [-40, 10], width: 540, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l14.When', target: [40, -50], width: 700, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l14.army', target: [40, -60], width: 640, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l15.Darius', target: [200, -150], width: 560, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l15.Within', target: [320, -180], width: 380, pitch: 46, yaw: -8, mm: 35, ease: 'inOut' },
  { at: 'l15.killed', target: [380, -190], width: 260, pitch: 42, yaw: -10, mm: 35, ease: 'inOut' },
  { at: 135.8, target: [380, -190], width: 280, pitch: 42, yaw: -10, mm: 35, ease: 'linear' },
];

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 } },
  world: fieldWorld,
  blocks, moves, arrows, labels, counters, icons, volleys, camera: cam,
  sheen: [
    { at: 'l03.smooths', until: 'l03.secret', center: SMOOTH.c, rx: SMOOTH.r, rz: SMOOTH.r, y: 11.8 },
    { at: 'l04.smooth', until: 'l04.they', center: SMOOTH.c, rx: SMOOTH.r, rz: SMOOTH.r, y: 11.8, alpha: 0.9 },
    { at: 'l06.off', until: 'l07.Darius', center: SMOOTH.c, rx: SMOOTH.r, rz: SMOOTH.r, y: 11.8, alpha: 0.9 },
  ],
  glows: [
    { at: 'l09.gap', until: 'l11.charged', pos: [35, -108], y: 3, r: 62, rgb: [255, 214, 80] },
  ],
  light: [
    { at: 'l14.When', dur: 5.0, to: { eve: 0.55, haze: 1.1 }, ease: 'inOut' },
    { at: 'l15.Darius', dur: 4.0, to: { eve: 1, haze: 1.3 }, ease: 'inOut' },
  ],
  stages: { asia },
  msaaOn: [[0, 14.5]],
  insets: [
    { stage: 'asia', at: 18.3, until: 31.9, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.8, out: 0.01, samples: 0 },
    { stage: 'asia', at: 135.8, until: 170, rect: [0, 0, 1, 1], frame: false, pop: false, in: 1.0, out: 0.01, samples: 0 },
  ],
  cards: [
    { at: 0, until: 1.0, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 14.35, until: 19.3, scrim: 0.9, scrimCenter: 'rgba(20,10,4,0.85)', fadeIn: 0.3, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF GAUGAMELA', size: 0.074, y: 0.44, delay: 0.1 },
      { text: '331 BC', size: 0.07, y: 0.585, delay: 1.1, colorTop: '#ffd9a0', colorBottom: '#e2873a' } ], ornaments: [{ y: 0.35, w: 0.7 }, { y: 0.68, w: 0.7 }] },
    { at: 147.052, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.13, y: 0.43, delay: 0.1, track: 0.14 },
      { text: 'The Battle of Gaugamela, 331 BC', size: 0.062, y: 0.6, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.5 }, { y: 0.69, w: 0.5 }] },
  ],
};
