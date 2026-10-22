// The Battle of Gaugamela (331 BC): Battle Map v2 spec (engine: films/lib/battlemap/SPEC.md; scene list and reasons: NOTES.md).
// Battlefield: x east, z south, 1 unit about 12 m. Macedonians (red) in the south facing north, Persians (blue) in the north facing south.
// Alexander's right is east (screen right on the plan views). Darius's levelled ground lies in front of the Macedonian left and centre.
// Stage `asia` is the map from Macedon to India (the road to Gaugamela, then the empire). Times are cue words; line starts never change.
// Film-side: kinds.js (the scythed chariot figure and its unit symbol), fx.js (the empire as a territory on the `asia` map).
const MAC = { team: 'rome' }, PER = { team: 'carthage' };

// ------------------------------------------------------------------ the battlefield: a dry plain, the levelled ground, the Tigris on the east
const SMOOTH = { c: [-120, 0], r: 118 };
const world = {
  seed: 331, size: [960, 520], res: 1, base: 6, meshStep: 2.5,
  sun: { azimuth: 236, elevation: 34 }, sunEve: { azimuth: 268, elevation: 8 },
  style: { contour: 1.5, pxPerUnit: 5.2, palette: [[-2, [0.60, 0.50, 0.32]], [3, [0.74, 0.62, 0.40]], [7, [0.80, 0.67, 0.43]], [10, [0.82, 0.70, 0.46]], [11.4, [0.90, 0.82, 0.62]], [14, [0.92, 0.86, 0.68]], [24, [0.72, 0.62, 0.50]]], paletteSoft: 3, fields: 0.0 },
  features: [
    { type: 'undulate', amp: 3.4, scale: 90 }, { type: 'undulate', amp: 1.0, scale: 30 },
    { type: 'hill', at: [-300, -220], r: [90, 34], h: 22, rot: 8 }, { type: 'hill', at: [130, -235], r: [100, 30], h: 18, rot: -6 }, { type: 'hill', at: [-60, 245], r: [120, 28], h: 16 },
    { type: 'flat', at: SMOOTH.c, r: SMOOTH.r, level: 11.6, soft: 22, amount: 0.985 },
    { type: 'river', name: 'Tigris', path: [[340, -270], [326, -140], [344, -30], [330, 90], [346, 270]], w: 15, depth: 2.6, meander: 7, wl: 5.4 },
    { type: 'woods', at: [380, -190], r: [30, 18] }, { type: 'woods', at: [372, 150], r: [26, 20] }, { type: 'woods', at: [300, 200], r: [14, 22], rot: 20 },
    { type: 'farms', rect: [372, 0, 40, 120, 0], cell: [14, 12], skip: 0.15 }, { type: 'farms', rect: [-330, 205, 120, 40, 4], cell: [16, 11], skip: 0.2 },
    { type: 'road', path: [[-40, -228], [120, -236], [250, -230], [336, -226], [480, -232]], w: 1.8, meander: 5 },
    { type: 'road', path: [[-200, 205], [-330, 236], [-480, 244]], w: 1.8, meander: 5 },
  ],
};

// ------------------------------------------------------------------ the map of Macedon to India (the road to Gaugamela, then the empire)
const POS = { macedon: [-330, -40], granicus: [-236, -56], issus: [-118, -22], gauga: [18, -34], greece: [-336, 6], india: [278, 40] };
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
  ambient: { wind: [1, 0.3], gusts: 0.4, flow: { dir: [1, 0.15], speed: 0.6, glint: 1.2 },
    birds: [{ center: [-200, -60], r: 30, h: 20, n: 6, speed: 5 }, { center: [60, -60], r: 34, h: 22, n: 5, speed: 6, dir: -1 }, { center: [200, 30], r: 30, h: 22, n: 5, speed: 5 }] },
  blocks: {
    mk: { ...MAC, kind: 'infantry', x: POS.macedon[0], z: POS.macedon[1], heading: 90, len: 20, dep: 10, hidden: true, bannerScale: 1.5, figScale: 1.4 },
    dk: { ...PER, kind: 'infantry', x: POS.gauga[0] + 16, z: POS.gauga[1] - 12, heading: 270, len: 20, dep: 10, hidden: true, bannerScale: 1.5, figScale: 1.4 },
    dk2: { ...PER, kind: 'infantry', x: POS.gauga[0] + 16, z: POS.gauga[1] + 12, heading: 270, len: 20, dep: 10, hidden: true, figScale: 1.4 },
    dk3: { ...PER, kind: 'cavalry', x: POS.gauga[0] + 38, z: POS.gauga[1], heading: 270, len: 18, dep: 10, hidden: true, banner: false, figScale: 1.4 },
    alex: { ...MAC, kind: 'cavalry', x: POS.gauga[0] - 6, z: POS.gauga[1], heading: 90, len: 16, dep: 8, hidden: true, bannerScale: 1.6, figScale: 1.4 },
  },
  zones: [{ y: 3, p: 3, alpha: 0.26, keys: [
    { t: 'l16.master', c: [70, 0], rx: 0, rz: 0 }, { t: 'l16.master+1.6', c: [70, 0], rx: 150, rz: 78 },
    { t: 'l16.stretched', c: [70, 0], rx: 150, rz: 78 }, { t: 'l16.India.+0.6', c: [-4, 4], rx: 340, rz: 92 } ] }],
  moves: [
    { block: 'mk', at: 'l02.Alexander', dur: 0.9, appear: true },
    { block: 'mk', at: 'l02.He', dur: 1.4, path: [[-290, -52], [-236, -56]], ease: 'inOut' },
    { block: 'mk', at: 'l02.Persians', dur: 1.6, path: [[-190, -50], [-150, -34], [-124, -22]], ease: 'inOut' },
    { blocks: ['dk', 'dk2', 'dk3'], at: 'l02.Darius', dur: 0.9, stagger: 0.35, appear: true },
    { block: 'mk', at: 'l02.waiting', dur: 2.6, path: [[-70, -26], [-24, -32]], ease: 'inOut' },
    { blocks: ['mk', 'dk', 'dk2', 'dk3'], at: 'l16', dur: 0.2, vanish: true },
    { block: 'alex', at: 'l16.Alexander', dur: 0.9, appear: true },
  ],
  arrows: [
    { at: 'l02.He', until: 'l02.Persians', ease: 'inOut', team: 'rome', style: 'dash', width: 3, path: [[-322, -42], [-290, -52], [-242, -56]], lift: 4, hide: 'l02.Now,' },
    { at: 'l02.Persians', until: 'l02.twice.>', ease: 'inOut', team: 'rome', style: 'dash', width: 3, path: [[-230, -56], [-190, -50], [-150, -34], [-126, -22]], lift: 4, hide: 'l02.Now,' },
    { at: 'l02.waiting', until: 'l02.yet.', ease: 'cam', team: 'rome', style: 'dash', width: 3, path: [[-112, -22], [-70, -26], [-32, -32]], lift: 4, hide: 'l03' },
    { at: 'l16.stretched', until: 'l16.India.>', ease: 'cam', team: 'rome', width: 5, path: [[-336, 4], [-200, 0], [-60, 12], [90, 40], [262, 38]], lift: 8 },
  ],
  markers: [
    { id: 'macedon', at: 'l02.Macedon.', until: 'l03', pos: POS.macedon, glyph: 'town', team: [0.74, 0.12, 0.12], label: 'MACEDON', labelDur: 3, size: 0.065, dx: 0.0, dy: -0.04 },
    { id: 'granicus', at: 'l02.beaten', until: 'l03', pos: POS.granicus, glyph: 'clash', label: 'GRANICUS, 334 BC', labelUntil: 'l02.Now,', size: 0.05, ldy: 0.05 },
    { id: 'issus', at: 'l02.twice.', until: 'l03', pos: POS.issus, glyph: 'clash', label: 'ISSUS, 333 BC', labelUntil: 'l02.Now,', size: 0.05, ldy: 0.05 },
    { id: 'gauga', at: 'l02.waiting', until: 'l03', pos: [POS.gauga[0] + 16, POS.gauga[1] + 28], glyph: 'plain', label: 'GAUGAMELA', labelUntil: 'l03', size: 0.05, ldy: 0.05 },
    { id: 'greece', at: 'l16.Greece', until: 170, pos: POS.greece, glyph: 'town', team: [0.74, 0.12, 0.12], label: 'GREECE', labelUntil: 170, size: 0.06 },
    { id: 'india', at: 'l16.India.', until: 170, pos: POS.india, glyph: 'river', label: 'INDIA', labelUntil: 170, size: 0.06 },
  ],
  labels: [
    { at: 'l16.master', until: 'l16.By', text: 'THE PERSIAN EMPIRE', pos: [70, 30], y: 4, team: 'rome', leader: false },
  ],
};

// ------------------------------------------------------------------ the armies on the plain
const ROW1 = -92, ROW2 = -114, ROW3 = -136, PITCH = 50;
const blocks = {}; const PL = [], PB = [], PC = [];
for (let k = 0; k < 8; k++) {
  blocks['pl' + k] = { ...PER, kind: 'infantry', x: (k - 3.5) * PITCH, z: ROW1, heading: 180, len: 44, dep: 20, hidden: true, bannerScale: 0.9 }; PL.push('pl' + k);
  blocks['pb' + k] = { ...PER, kind: k % 3 === 1 ? 'archers' : 'infantry', x: (k - 3.5) * PITCH, z: ROW2, heading: 180, len: 44, dep: 16, hidden: true, banner: k % 2 === 0 }; PB.push('pb' + k);
  blocks['pc' + k] = { ...PER, kind: 'infantry', x: (k - 3.5) * PITCH, z: ROW3, heading: 180, len: 44, dep: 16, hidden: true, banner: false }; PC.push('pc' + k);
}
const PERSIANS = [...PL, ...PB, ...PC];
const S_LANE = 10;                                                         // each Macedonian column steps aside by this much per place from the centre
const laneX = [0, 1, 2, 3, 4].map((i) => 45 + (i - 2) * (140 / 6 + S_LANE)); // the five lanes after the march east (x)
const CH = laneX.map((_, i) => 'ch' + i);
Object.assign(blocks, {
  guard: { ...PER, kind: 'elite', x: 0, z: -160, heading: 180, len: 34, dep: 14, hidden: true, bannerScale: 1.2 },
  darius: { ...PER, kind: 'cavalry', figures: 'chariot', x: 0, z: -177, heading: 180, len: 4.4, dep: 5, hidden: true, bannerScale: 1.8, figScale: 1.3 },
  eleph: { ...PER, kind: 'elephant', x: 4, z: -76, heading: 180, len: 16, dep: 5, hidden: true, figScale: 0.26, spacing: 5, banner: false },
  pcavE1: { ...PER, kind: 'cavalry', x: 225, z: -96, heading: 180, len: 36, dep: 14, hidden: true, bannerScale: 0.9 },
  pcavE2: { ...PER, kind: 'cavalry', x: 225, z: -122, heading: 180, len: 36, dep: 14, hidden: true, banner: false },
  pcavW: { ...PER, kind: 'cavalry', x: -225, z: -98, heading: 180, len: 36, dep: 14, hidden: true, bannerScale: 0.9 },
  mac: { ...MAC, kind: 'infantry', x: -75, z: 114, heading: 0, len: 140, dep: 32, grid: { cols: 6, ranks: 2, gap: 3 }, count: 47000, bannerScale: 1.0 },
  parm: { ...MAC, kind: 'elite', x: -175, z: 110, heading: 0, len: 50, dep: 22, bannerScale: 1.1 },
  comp: { ...MAC, kind: 'cavalry', x: 40, z: 110, heading: 0, len: 36, dep: 14, bannerScale: 1.5 },
  rear: { ...MAC, kind: 'infantry', x: -75, z: 148, heading: 0, len: 130, dep: 10, bannerScale: 0.8 },
});
laneX.forEach((x, i) => { blocks['ch' + i] = { ...PER, kind: 'cavalry', figures: 'chariot', x: x - 60, z: -70, heading: 180, len: 8.4, dep: 5, hidden: true, banner: false, figScale: 1.3 }; });
const MACS = ['mac', 'parm', 'comp', 'rear'];

const moves = [
  // S1: Alexander's army walks into line at dawn; across the plain the Persian host forms up, rank by rank
  { blocks: MACS, at: 0, dur: 10, by: { z: -18 }, ease: 'cam' },
  { blocks: PL, at: 'l00.most', dur: 0.9, stagger: 0.12, appear: true },
  { blocks: PB, at: 'l00.most+0.7', dur: 0.9, stagger: 0.12, appear: true },
  { blocks: PC, at: 'l00.most+1.3', dur: 0.9, stagger: 0.12, appear: true },
  { blocks: ['pcavW', 'pcavE1', 'pcavE2', 'guard', 'darius', 'eleph'], at: 'l00.Earth.', dur: 0.9, stagger: 0.2, appear: true },
  // S3: the secret weapon rolls out in front of the line
  { blocks: CH, at: 'l03.secret', dur: 0.8, stagger: 0.15, appear: true },
  { blocks: CH, at: 'l03.secret', dur: 2.4, stagger: 0.15, by: { z: 6 }, ease: 'cam' },
  // S4: the march to the right, off the levelled ground; Darius follows and his line stretches
  { group: 'mac', at: 'l06.marched', dur: 6.6, by: { x: 120 }, ease: 'cam' }, { blocks: ['comp', 'rear'], at: 'l06.marched', dur: 6.6, by: { x: 120 }, ease: 'cam' },
  { block: 'parm', at: 'l06.marched', dur: 6.6, by: { x: 50 }, ease: 'cam' },
  ...PERSIANS.map((id, n) => ({ block: id, at: 'l07.follow,', dur: 2.8, by: { x: 10 * (n % 8) }, ease: 'cam' })),
  { blocks: ['pcavE1', 'pcavE2'], at: 'l07.follow,', dur: 2.8, by: { x: 70 }, ease: 'cam' },
  { blocks: ['guard', 'darius'], at: 'l07.follow,', dur: 2.8, by: { x: 35 }, ease: 'cam' }, { block: 'eleph', at: 'l07.follow,', dur: 2.8, by: { x: 30 }, ease: 'cam' },
  { blocks: CH, at: 'l07.follow,', dur: 3.0, by: { x: 60, z: 34 }, ease: 'cam' },
  // S5: the chariots charge; the columns step aside into five lanes; the chariots run through and are stopped at the back
  ...[0, 1, 2, 3, 4, 5].flatMap((i) => [0, 1].map((r) => ({ block: `mac.${i}.${r}`, at: 'l08.soldiers', dur: 1.5, by: { x: (i - 2.5) * S_LANE }, ease: 'inOut' }))),
  { block: 'comp', at: 'l08.soldiers', dur: 1.5, by: { x: 2.5 * S_LANE }, ease: 'inOut' },
  ...CH.map((id, i) => ({ block: id, at: 'l08.chariots', until: 'l08.stopped', path: [[laneX[i], 40], [laneX[i], 119]], ease: 'inQuad' })),
  { blocks: CH, at: 'l08.stopped', dur: 1.4, stagger: 0.1, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.6 },
  ...[0, 1, 2, 3, 4, 5].flatMap((i) => [0, 1].map((r) => ({ block: `mac.${i}.${r}`, at: 'l08.So', dur: 1.2, by: { x: -(i - 2.5) * S_LANE }, ease: 'inOut' }))),
  { block: 'comp', at: 'l08.So', dur: 1.2, by: { x: -2.5 * S_LANE }, ease: 'inOut' },
  { blocks: CH, at: 'l10', dur: 1.0, vanish: true },
  // S6: the Persian horsemen ride round the right; the line stretches and the gap opens; the wedge forms and charges
  { block: 'pcavE1', at: 'l09.horsemen', dur: 4.4, path: [[295, -60], [290, -10], [262, 50], [212, 112], [168, 140]], ease: 'cam' },
  { block: 'pcavE2', at: 'l09.horsemen+0.5', dur: 4.4, path: [[300, -60], [302, -10], [276, 56], [228, 118], [190, 150]], ease: 'cam' },
  ...PERSIANS.map((id, n) => ({ block: id, at: 'l09.stretched', dur: 2.6, by: { x: (n % 8) >= 4 ? 20 : -20 }, ease: 'cam' })),
  { block: 'eleph', at: 'l09.stretched', dur: 2.6, by: { x: -20 }, ease: 'cam' },
  { block: 'comp', at: 'l11.formed', dur: 1.6, to: { scale: 1.25 }, ease: 'inOut' },
  { block: 'comp', at: 'l11.charged', until: 'l12', path: [[140, 40], [95, -30], [48, -90], [36, -136]], ease: 'inOut' },
  // S7: Darius turns his chariot and runs; his guard gives way; on the left, Parmenion is struck; Alexander turns back
  { block: 'darius', at: 'l12.turned', dur: 3.4, path: [[60, -184], [120, -195], [200, -200]], ease: 'in' },
  { block: 'comp', at: 'l12.turned', dur: 2.4, by: { z: -6 }, ease: 'out' },
  { block: 'guard', at: 'l12.fled.', dur: 2.4, fadeTo: 0.6, alphaTo: 0.6, ease: 'inOut' },
  { block: 'pcavW', at: 'l13.Meanwhile,', dur: 3.6, path: [[-225, -40], [-205, 20], [-170, 56], [-150, 66]], ease: 'cam' },
  { block: 'parm', at: 'l13.serious', dur: 2.0, fadeTo: 0.35, alphaTo: 0.85, ease: 'inOut' },
  { block: 'comp', at: 'l13.turn', dur: 1.4, to: { scale: 1.0 }, ease: 'inOut' },
  { block: 'comp', at: 'l13.turn', until: 'l14.fled,', path: [[36, -100], [20, -30], [-40, 30], [-92, 52]], ease: 'cam' },
  // S8: the army falls apart (turns, drifts away, thins by numbers); Darius runs east over the Tigris
  { blocks: PERSIANS, at: 'l14.fell', dur: 1.4, stagger: 0.04, to: { heading: 0 }, ease: 'inOut' },
  { blocks: PERSIANS, at: 'l14.fell', dur: 4.0, stagger: 0.04, by: { z: -26 }, ease: 'in' },
  { blocks: PERSIANS, at: 'l14.fell', dur: 3.2, stagger: 0.05, fadeTo: 1, alphaTo: 0.55, sinkTo: 0.9 },
  { blocks: ['pcavE1', 'pcavE2'], at: 'l14.realized', dur: 3.6, by: { x: 70, z: 30 }, ease: 'in' }, { blocks: ['pcavE1', 'pcavE2'], at: 'l14.fell', dur: 2.4, fadeTo: 1, alphaTo: 0.5 },
  { block: 'pcavW', at: 'l14.realized', dur: 3.6, path: [[-200, 40], [-250, 0]], ease: 'in' }, { block: 'pcavW', at: 'l14.fell', dur: 2.4, fadeTo: 1, alphaTo: 0.5 },
  { blocks: ['guard', 'eleph'], at: 'l14.fell', dur: 2.6, fadeTo: 1, alphaTo: 0.5 },
  { block: 'darius', at: 'l15.ran', dur: 5.0, path: [[300, -203], [384, -208]], ease: 'cam' },
  { block: 'darius', at: 'l15.dead,', dur: 1.4, vanish: true },
];

// ------------------------------------------------------------------ the edit: scenes, sets, shots (reasons in NOTES.md)
const scenes = [
  { id: 'S1', name: 'A young king', at: 0, job: 'a young king faces the most powerful empire on Earth, outnumbered', set: { time: [0.34, 0.22], haze: 1.4, cloud: 0.3 },
    shots: [
      { at: 0, why: 'cold open at dawn, low behind the young king\'s horsemen: the empty plain ahead, and what is on it', from: { target: [36, 30], dist: 157, pitch: 17, yaw: 354, mm: 30 },
        moves: [{ until: 'l00.Earth.>', to: { target: [36, 12], dist: 150 } }] },
      { at: 'l00.He', why: 'reverse angle over the Persian host: how outnumbered he is', from: { target: [0, -60], width: 560, pitch: 34, yaw: 180, mm: 35 },
        moves: [{ until: 13.4, to: { yaw: 192, width: 520 } }] },
      { at: 13.4, why: 'crane up to the map: the lesson is the plan, seen from above (under the title)', from: { target: [-10, 0], width: 640, pitch: 52, yaw: 0, mm: 35 },
        moves: [{ until: 19.5, to: { pitch: 84, width: 660 }, ease: 'camSoft' }] },
    ] },
  { id: 'S2', name: 'The road east', at: 'l02', stage: 'asia', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'who the king is: Alexander, two victories already, and Darius waiting with his biggest army', set: { time: 0.05, haze: 1.0 },
    shots: [
      { at: 'l02', why: 'change of world: the map from Macedon across Asia Minor, the march and the two victories', from: { target: [-262, -36], width: 400, pitch: 58, yaw: 0, mm: 35 },
        moves: [{ at: 'l02.Macedon.', until: 'l02.twice.>', to: { target: [-176, -34], width: 420 } }] },
      { at: 'l02.Now,', why: 'lower and east: Darius waits at Gaugamela, push in on his army', from: { target: [-40, -22], width: 440, pitch: 40, yaw: 12, mm: 35 },
        moves: [{ until: 'l02.yet.>', to: { target: [-14, -28], width: 370 } }] },
    ] },
  { id: 'S3', name: 'The trap on the plain', at: 'l03', transition: { type: 'dissolve', dur: 0.8 }, job: 'Darius\'s plan: a flat plain, levelled further, so his scythed chariots can charge at full speed', set: { time: 0.08, haze: 1.15, cloud: 0.3 },
    shots: [
      { at: 'l03', why: 'back on the plain: establish the field, the Persian line and the Tigris', from: { target: [60, -10], width: 720, pitch: 38, yaw: 20, mm: 35 },
        moves: [{ until: 'l03.Iraq.>', to: { target: [80, -10], yaw: 26, width: 690 } }] },
      { at: 'l03.He', why: 'high over the levelled ground: the field smoothed flat, for a reason', from: { target: [-110, 0], width: 420, pitch: 80, yaw: 0, mm: 35 },
        moves: [{ until: 'l03.weapon.>', to: { width: 390 } }] },
      { at: 'l04', why: 'low and close on the secret weapon: blades out of the wheels', from: { target: [-15, -60], dist: 40, pitch: 11, yaw: 345, mm: 45 },
        moves: [{ until: 'l04.wheels.>', to: { dist: 34 } }] },
      { at: 'l04.On', why: 'high angle: the charge Darius planned, straight across the smooth ground', from: { target: [-70, 0], width: 480, pitch: 64, yaw: 340, mm: 35 },
        moves: [{ until: 'l04.speed.>', to: { width: 460 } }] },
    ] },
  { id: 'S4', name: 'Sideways', at: 'l05', job: 'the numbers, then Alexander\'s answer: march sideways, off the smooth ground, and make Darius follow', set: { time: [0.0, 0.04], haze: 1.05, cloud: 0.28 },
    shots: [
      { at: 'l05', why: 'the plan view: both armies, and the numbers', from: { target: [-30, -10], width: 560, pitch: 86, yaw: 0, mm: 35 },
        moves: [{ until: 'l05.more.>', to: { target: [-20, -10], width: 530 } }] },
      { at: 'l05.Nobody', why: 'low along the Persian front, end to end: nobody knows how many', from: { target: [30, -76], dist: 130, pitch: 8, yaw: 262, mm: 35 },
        moves: [{ until: 'l05.numbers.>', by: { target: [-24, 0] } }] },
      { at: 'l06', why: 'top-down: the plan drawn on the map, the whole army slides right', from: { target: [-30, 30], width: 600, pitch: 84, yaw: 0, mm: 35 },
        moves: [{ at: 'l06.marched', until: 'l06.ground.>', to: { target: [40, 20] } }] },
      { at: 'l07', why: 'from behind the Persian line: Darius has to follow, his line stretches', from: { target: [70, -60], dist: 220, pitch: 28, yaw: 160, mm: 35 },
        moves: [{ until: 'l07.up.>', by: { target: [30, 0], yaw: -8 } }] },
    ] },
  { id: 'S5', name: 'The chariots charge', at: 'l08', job: 'the secret weapon charges; the soldiers open lanes; the chariots run through and are stopped', set: { time: 0.05, haze: 1.12 },
    shots: [
      { at: 'l08', why: 'low behind the chariots as they charge at the Macedonian line', from: { target: [45, 20], dist: 100, pitch: 14, yaw: 180, mm: 35 },
        moves: [{ until: 'l08.soldiers', to: { target: [45, 40], dist: 96 } }] },
      { at: 'l08.soldiers', why: 'high angle: the soldiers simply step aside and open lanes', from: { target: [45, 78], width: 300, pitch: 64, yaw: 30, mm: 35 },
        moves: [{ until: 'l08.lanes.>', to: { target: [45, 88], width: 280 } }] },
      { at: 'l08.The#1', why: 'low behind the Macedonian rear: the chariots come through the lanes and are stopped at the back', from: { target: [45, 100], dist: 90, pitch: 13, yaw: 0, mm: 35 },
        moves: [{ until: 'l08.back.>', to: { dist: 84 } }] },
      { at: 'l08.So', why: 'cut on the punchline to the plan: the secret weapon, spent', from: { target: [45, 70], width: 360, pitch: 74, yaw: 350, mm: 35 },
        moves: [{ until: 'l08.weapon.>', to: { width: 350 } }] },
    ] },
  { id: 'S6', name: 'The gap', at: 'l09', job: 'Darius stretches too far, a gap opens, and Alexander charges into it', set: { time: [0.06, 0.14], haze: 1.1 },
    shots: [
      { at: 'l09', why: 'wide and high: the Persian horsemen ride round Alexander\'s right, pulling the line further', from: { target: [150, 0], width: 640, pitch: 56, yaw: 20, mm: 35 },
        moves: [{ until: 'l09.side,>', to: { target: [170, 10] } }] },
      { at: 'l09.gap', why: 'top-down on the Persian centre: a gap opens', from: { target: [35, -110], width: 300, pitch: 86, yaw: 0, mm: 35 },
        moves: [{ until: 'l09.line.>', to: { width: 280 } }] },
      { at: 'l10', why: 'low behind Alexander and his horsemen: the gap, seen from where he waited', from: { target: [110, -20], dist: 180, pitch: 12, yaw: 328, mm: 35 },
        moves: [{ until: 'l10.for.>', to: { dist: 166 } }] },
      { at: 'l11', why: 'the decisive moment, wide from above: the wedge drives into the gap, straight at Darius', from: { target: [90, -40], width: 460, pitch: 74, yaw: 340, mm: 35 },
        moves: [{ until: 'l11.Darius.>', to: { target: [60, -80], width: 420 } }] },
    ] },
  { id: 'S7', name: 'The king runs', at: 'l12', climax: true, job: 'how it worked, closer: the wedge reaches the guard, Darius flees; and the cost on the other wing', set: { time: [0.14, 0.3], haze: 1.15 },
    shots: [
      { at: 'l12', why: 'closer and lower, the same moment: the wedge at the guard, Darius turns his chariot and runs', from: { target: [56, -168], dist: 120, pitch: 18, yaw: 70, mm: 40 },
        moves: [{ until: 'l12.fled.>', to: { target: [76, -174], dist: 128 } }] },
      { at: 'l13', why: 'meanwhile, the other wing: Persian horsemen fall on Parmenion', from: { target: [-140, 70], dist: 150, pitch: 24, yaw: 30, mm: 35 },
        moves: [{ until: 'l13.trouble.>', to: { dist: 138 } }] },
      { at: 'l13.Alexander', why: 'high and wide: Alexander gives up the chase and turns back to help', from: { target: [-30, -20], width: 520, pitch: 66, yaw: 0, mm: 35 },
        moves: [{ until: 'l13.him.>', to: { target: [-40, 0], width: 500 } }] },
    ] },
  { id: 'S8', name: 'The army falls apart', at: 'l14', job: 'the result: with their king gone the Persians break, and Darius runs east to his end', set: { time: [0.45, 0.95], haze: 1.25 },
    shots: [
      { at: 'l14', why: 'pull back over the field: the Persian army breaks and drifts away', from: { target: [40, -100], dist: 260, pitch: 28, yaw: 196, mm: 35 },
        moves: [{ until: 'l14.apart.>', to: { dist: 320, pitch: 32 }, ease: 'camLong' }] },
      { at: 'l15', why: 'low into the red sun: Darius alone, running east over the Tigris', from: { target: [290, -200], dist: 140, pitch: 13, yaw: 90, mm: 35 },
        moves: [{ until: 'l15.officers.>', to: { target: [340, -205], dist: 130 } }] },
    ] },
  { id: 'S9', name: 'Master of Asia', at: 'l16', stage: 'asia', inset: 'full', transition: { type: 'dissolve', dur: 1.0 }, job: 'why it mattered: the empire changes hands, and grows from Greece to India', set: { time: 0.2, haze: 1.05 },
    shots: [
      { at: 'l16', why: 'change of world: the Persian Empire on the map passes to Alexander, then the pull out to India', from: { target: [40, -4], width: 520, pitch: 62, yaw: 0, mm: 35 },
        moves: [{ until: 'l16.25.>', to: { width: 500 } }, { at: 'l16.By', until: 146.8, to: { target: [-4, 6], width: 880 }, ease: 'camLong' }] },
    ] },
];

// ------------------------------------------------------------------ the legend (motion-graphics frame)
const legend = {
  title: { text: 'BATTLE OF GAUGAMELA', sub: '1 October 331 BC', at: 'l02.Alexander' },
  show: [['l02.Alexander', 'l16.battle.>']],
  sides: [
    { id: 'macedon', team: 'rome', name: 'MACEDON', commander: 'Alexander', banner: 'banner', at: 'l02.Alexander', strength: 47000, strengthAt: 'l05.47', strengthLabel: 'MEN' },
    { id: 'persia', team: 'carthage', name: 'PERSIA', commander: 'Darius III', banner: 'vexillum', at: 'l02.Darius', dimAt: 'l14.fell' },
  ],
  key: { show: [['l03.Tigris', 'l06.Alexander\'s'], ['l08', 'l08.weapon.>'], ['l09.horsemen', 'l11.Darius.>']] },
  units: [
    { id: 'chariot', kind: 'chariot', glyph: 'u-chariot', name: 'Scythed chariots', team: 'carthage', at: 'l04.Scythe' },
    { id: 'inf', kind: 'infantry', name: 'Infantry', teams: ['rome', 'carthage'], at: 'l05.men.' },
    { id: 'cav', kind: 'cavalry', name: 'Cavalry', teams: ['rome', 'carthage'], at: 'l09.horsemen' },
  ],
  places: [
    { id: 'tigris', letter: 'A', glyph: 'river', name: 'River Tigris', at: 'l03.Tigris', pos: [334, 52], ldy: 0.05 },
    { id: 'level', letter: 'B', glyph: 'plain', name: 'The levelled ground', at: 'l03.smooths', pos: [-150, -40], y: 2, label: 'LEVELLED GROUND' },
  ],
  focus: [
    { entry: 'chariot', at: 'l08.chariots', until: 'l08.weapon.>' }, { entry: 'cav', at: 'l11.best', until: 'l11.Darius.>' },
    { entry: 'macedon', at: 'l16.Alexander', until: 'l16.battle.>' },
  ],
  scale: { unitM: 12, show: [['l03', 'l13.him.>']] },
};

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.06, grain: 0.03, vignette: 0.30 } },
  world, stages: { asia }, blocks, moves, scenes, legend,
  msaaOn: [[0, 'l00.He'], ['l04', 'l04.On'], ['l08.The#1', 'l08.So']],   // anti-aliasing only on the three low, close shots
  ambient: {
    wind: [1.0, 0.3], gusts: 0.5, flow: { dir: [0.05, 1], speed: 0.9, glint: 1.1 },
    camps: [{ pos: [-40, -230], size: [110, 34], team: 'carthage', style: 'scatter', tents: 40, fires: 5, people: 14 }, { pos: [-200, 196], size: [56, 34], team: 'rome', style: 'grid', fires: 3, people: 12, rot: -4 }],
    walkers: [{ path: [[-40, -228], [120, -236], [250, -230], [336, -226], [480, -232]], n: 6, gap: 5, speed: 1.4, kind: 'light', team: 'neutral' }, { path: [[-200, 205], [-330, 236], [-480, 244]], n: 4, gap: 5, speed: 1.2, kind: 'light', team: 'neutral', offset: 20 }],
    smoke: [{ pos: [36, -128], n: 12, alpha: 0.2, height: 11, at: 'l11.charged' }, { pos: [-140, 80], n: 10, alpha: 0.18, height: 9, at: 'l13.Meanwhile,' }, { pos: [60, -150], n: 14, alpha: 0.22, height: 12, at: 'l14' }],
    birds: [{ center: [-200, 120], r: 50, h: 30, n: 7, speed: 7 }, { path: [[-420, -40], [420, 60]], n: 5, h: 40, speed: 9 }, { center: [330, -60], r: 30, h: 24, n: 6, speed: 6, dir: -1 }],
  },
  arrows: [
    { at: 'l03.smooths', dur: 1.6, ease: 'cam', team: 'ink', width: 1.4, style: 'dash', head: false, taper: 1, smooth: true, lift: 4, hide: 'l05',
      path: [...Array(17)].map((_, i) => [SMOOTH.c[0] + Math.cos(i / 16 * Math.PI * 2) * (SMOOTH.r - 8), SMOOTH.c[1] + Math.sin(i / 16 * Math.PI * 2) * (SMOOTH.r - 8)]) },
    ...laneX.map((x) => ({ at: 'l04.charge', dur: 1.2, ease: 'out', team: 'carthage', width: 3, style: 'dash', path: [[x - 60, -56], [x - 60, 66]], lift: 5, hide: 'l05' })),
    { at: 'l06.straight', dur: 0.9, ease: 'out', team: 'ink', width: 3, style: 'dash', path: [[-75, 72], [-75, -10]], lift: 5, hide: 'l06.he' },
    { at: 'l06.sideways', until: 'l06.further#1>', ease: 'cam', team: 'rome', width: 6, path: [[-75, 62], [-10, 62], [50, 62]], lift: 6, hide: 'l07' },
    { at: 'l07.follow,', until: 'l07.up.', ease: 'cam', team: 'carthage', width: 5, path: [[-20, -72], [80, -72], [200, -72]], lift: 6, hide: 'l08' },
    ...laneX.map((x) => ({ at: 'l08.chariots', until: 'l08.through', ease: 'out', team: 'carthage', width: 2.2, style: 'dash', path: [[x, -22], [x, 112]], lift: 4, hide: 'l08.So' })),
    { at: 'l09.horsemen', until: 'l09.side,>', ease: 'cam', team: 'carthage', width: 5, path: [[295, -60], [290, -10], [262, 50], [212, 112], [168, 140]], lift: 6, hide: 'l10' },
    { at: 'l09.gap', dur: 1.4, ease: 'cam', team: 'gold', width: 1.6, style: 'dash', head: false, taper: 1, smooth: true, lift: 5, hide: 'l11.charged',
      path: [...Array(13)].map((_, i) => [35 + Math.cos(i / 12 * Math.PI * 2) * 26, -114 + Math.sin(i / 12 * Math.PI * 2) * 34]) },
    { at: 'l11.charged', until: 'l11.Darius.', ease: 'out', team: 'rome', width: 7, path: [[160, 82], [140, 40], [95, -30], [48, -90], [36, -134]], lift: 7, hide: 'l12.fled.' },
    { at: 'l12.turned', until: 'l12.fled.>', ease: 'cam', team: 'carthage', width: 4, style: 'dash', path: [[40, -186], [60, -186], [120, -196], [200, -200]], lift: 6, hide: 'l13' },
    { at: 'l13.Meanwhile,', until: 'l13.side,>', ease: 'cam', team: 'carthage', width: 5, path: [[-225, -80], [-225, -40], [-205, 20], [-164, 60]], lift: 6, hide: 'l14' },
    { at: 'l13.turn', until: 'l13.him.', ease: 'cam', team: 'rome', width: 6, path: [[36, -132], [36, -100], [20, -30], [-40, 30], [-86, 50]], lift: 7, hide: 'l14' },
    { at: 'l15.ran', until: 'l15.east.>', ease: 'cam', team: 'carthage', width: 4, style: 'dash', path: [[204, -200], [300, -203], [384, -208]], lift: 6, hide: 'l16' },
  ],
  labels: [
    { at: 'l00.331', until: 'l00.young', text: '1 OCTOBER 331 BC', screen: [0.5, 0.86], big: true },
    { at: 'l00.young', until: 'l00.He', text: 'ALEXANDER', block: 'comp', team: 'rome', dy: -0.12 },
    { at: 'l05.truly', until: 'l06', text: 'ONE ANCIENT WRITER SAYS 1,000,000', screen: [0.5, 0.86], big: true },
    { at: 'l09.gap', until: 'l11.charged', text: 'THE GAP', pos: [35, -114], y: 3, dx: 0.1, dy: -0.14 },
    { at: 'l11.best', until: 'l11.charged', text: 'COMPANION CAVALRY', block: 'comp', team: 'rome', dx: 0.08, dy: -0.1 },
    { at: 'l11.Darius.', until: 'l12.fled.>', text: 'DARIUS', block: 'darius', team: 'carthage', dx: 0.06, dy: -0.12 },
    { at: 'l13.general', until: 'l13.Alexander', text: 'PARMENION', block: 'parm', team: 'rome', dx: -0.06, dy: -0.12 },
    { at: 'l15.Within', until: 'l16', text: '330 BC', screen: [0.5, 0.86], big: true },
  ],
  counters: [
    { at: 'l05.47', until: 'l05.Nobody', block: 'mac', team: 'rome', from: 0, to: 47000, countDur: 1.1, step: 1000, suffix: 'MEN', dy: -0.12 },
  ],
  cards: [
    { at: 0, until: 0.8, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 14.35, until: 19.3, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF GAUGAMELA', size: 0.078, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
      { text: '331 BC', size: 0.056, y: 0.575, delay: 1.0, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.56 }, { y: 0.65, w: 0.56 }] },
    { at: 147.052, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.8, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Gaugamela, 331 BC', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],
};
