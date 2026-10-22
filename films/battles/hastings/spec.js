// The Battle of Hastings (1066): Battle Map spec. Times come from the cue words (see films/lib/battlemap/SPEC.md).
// Colours: the English are royal blue (team 'carthage'), the Normans deep red (team 'rome'), the Vikings gold.
// Two maps: the main stage is England and Normandy (the build-up and the coronation); the 'bat' stage is the battlefield below Senlac hill,
// shown full screen from the start of l06 to the end of l15. Map units: x east, z south, 1 unit about 10 m on the battlefield.
const ENG = { team: 'carthage' }, NOR = { team: 'rome' }, VIK = { team: 'gold' };

// ------------------------------------------------------------------ England and Normandy
const england = {
  seed: 1066, size: [760, 500], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 250, elevation: 32 }, sunEve: { azimuth: 284, elevation: 10 },
  style: { contour: 4, pxPerUnit: 5.4, palette: [[-4, [0.62, 0.72, 0.46]], [3, [0.74, 0.76, 0.48]], [14, [0.80, 0.70, 0.46]], [30, [0.72, 0.58, 0.42]], [48, [0.70, 0.66, 0.62]], [66, [0.95, 0.95, 0.96]]], paletteSoft: 5 },
  features: [
    { type: 'undulate', amp: 4, scale: 90 },
    { type: 'ridge', path: [[-60, -250], [-40, -190], [-70, -130], [-60, -70]], w: 22, h: 14, rough: 0.3 },
    { type: 'sea', poly: [[-420, -300], [420, -300], [420, 300], [-420, 300]], shelf: 34, depth: 8 },
    // England (the north and the east run off the edge), then France
    { type: 'land', wob: 2.4, shelf: 16, poly: [[-420, -300], [190, -300], [190, -260], [210, -215], [196, -170], [230, -150], [250, -130], [300, -98], [312, -62], [276, -46], [302, -20], [296, 14], [262, 28], [215, 40], [160, 48], [100, 54], [40, 62], [-20, 72], [-90, 84], [-160, 82], [-220, 96], [-300, 112], [-340, 96], [-420, 86]] },
    { type: 'land', wob: 2.4, shelf: 16, poly: [[-420, 300], [-420, 190], [-330, 172], [-260, 150], [-200, 168], [-150, 160], [-110, 128], [-70, 120], [-50, 150], [0, 165], [60, 170], [110, 172], [150, 168], [200, 150], [250, 140], [290, 125], [330, 112], [420, 100], [420, 300]] },
    { type: 'river', name: 'Thames', path: [[130, -70], [190, -52], [250, -48], [285, -50]], w: 5, depth: 1.6, meander: 4, wl: 3 },
    { type: 'woods', at: [-120, -150], r: [50, 18], rot: 10 }, { type: 'woods', at: [60, -100], r: [26, 14], rot: -20 }, { type: 'woods', at: [-20, 10], r: [40, 14], rot: 8 }, { type: 'woods', at: [220, -110], r: [20, 18] },
    { type: 'woods', at: [-200, 200], r: [40, 14] }, { type: 'woods', at: [120, 215], r: [60, 18], rot: 4 },
    { type: 'farms', rect: [20, -150, 120, 40, 8], cell: [14, 10] }, { type: 'farms', rect: [-140, -20, 130, 40, -4], cell: [15, 10] }, { type: 'farms', rect: [10, 225, 200, 40, 0], cell: [16, 11] },
    { type: 'road', path: [[190, 34], [172, 4], [150, -30], [138, -58], [128, -92], [112, -128], [92, -160], [70, -196]], w: 2.0, meander: 3 },
  ],
};

// ------------------------------------------------------------------ the battlefield: Senlac hill, the ridge, the gentle south slope
const hill = {
  look: { cloud: 0.1 },
  world: {
    seed: 1014, size: [760, 500], res: 1, base: 0, meshStep: 2.5,
    sun: { azimuth: 232, elevation: 30 }, sunEve: { azimuth: 250, elevation: 5 },
    style: { contour: 1.5, pxPerUnit: 5.4 },
    features: [
      { type: 'undulate', amp: 3, scale: 120 }, { type: 'undulate', amp: 1.0, scale: 38 },
      { type: 'ridge', path: [[-400, -50], [-220, -54], [-80, -58], [60, -56], [220, -50], [400, -54]], w: 100, h: 24, rough: 0.18, meander: 6 },
      { type: 'hill', at: [-260, -120], r: [60, 40], h: 14, rot: 15 }, { type: 'hill', at: [270, -140], r: [70, 36], h: 12, rot: -12 },
      // marshy ground to both sides at the foot of the slope
      { type: 'lake', at: [-215, 58], r: [50, 22] }, { type: 'lake', at: [225, 40], r: [56, 24] }, { type: 'lake', at: [-290, -10], r: [20, 16] },
      { type: 'woods', at: [-285, -50], r: [42, 56], rot: 8 }, { type: 'woods', at: [285, -60], r: [42, 56], rot: -8 }, { type: 'woods', at: [-110, -190], r: [70, 24] }, { type: 'woods', at: [140, -200], r: [70, 24] },
      { type: 'woods', at: [-70, 215], r: [60, 18] }, { type: 'woods', at: [120, 222], r: [50, 16] },
      { type: 'farms', rect: [0, 205, 240, 40, 0], cell: [16, 11] }, { type: 'farms', rect: [-120, 150, 70, 40, 6], cell: [14, 10] },
      { type: 'road', path: [[8, 250], [-4, 160], [4, 60], [-2, -50], [6, -140], [0, -250]], w: 2.2, meander: 3 },
    ],
  },
  blocks: {
    // the English: a wall of eight blocks on the crest, a second line behind, King Harold behind them
    ...Object.fromEntries([0, 1, 2, 3, 4, 5, 6, 7].map((i) => ['w' + i, { ...ENG, kind: 'infantry', x: -63 + 18 * i, z: -46, heading: 180, len: 17.2, dep: 11, height: 4, banner: false, hidden: true }])),
    ...Object.fromEntries([0, 1, 2, 3, 4, 5].map((i) => ['b' + i, { ...ENG, kind: 'infantry', x: -45 + 18 * i, z: -61, heading: 180, len: 17.2, dep: 14, height: 4, banner: false, hidden: true }])),
    harold: { ...ENG, kind: 'elite', x: 0, z: -72, heading: 180, len: 18, dep: 12, height: 5, bannerScale: 2.4, hidden: true },
    // the Normans: archers, foot soldiers, knights, and William at the back
    arch: { ...NOR, kind: 'light', x: 0, z: 108, heading: 0, len: 124, dep: 8, grid: { cols: 3, ranks: 1, gap: 2.4 }, height: 3, banner: false, hidden: true },
    inf: { ...NOR, kind: 'infantry', x: 0, z: 124, heading: 0, len: 126, dep: 18, grid: { cols: 3, ranks: 1, gap: 2.4 }, height: 4, banner: false, hidden: true },
    kL: { ...NOR, kind: 'cavalry', x: -50, z: 146, heading: 0, len: 30, dep: 14, height: 4, banner: false, hidden: true },
    kM: { ...NOR, kind: 'cavalry', x: 0, z: 146, heading: 0, len: 30, dep: 14, height: 4, banner: false, hidden: true },
    kR: { ...NOR, kind: 'cavalry', x: 50, z: 146, heading: 0, len: 30, dep: 14, height: 4, banner: false, hidden: true },
    wm: { ...NOR, kind: 'elite', x: 0, z: 166, heading: 0, len: 18, dep: 12, height: 5, bannerScale: 2.6, hidden: true },
  },
  moves: [],   // filled below (the choreography is easier to read as code)
  arrows: [], labels: [], icons: [], volleys: [], counters: [], light: [], camera: [],
};

// ---- helpers for the battlefield choreography
const M = hill.moves;
const W_ALL = ['w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7'], B_ALL = ['b0', 'b1', 'b2', 'b3', 'b4', 'b5'], KN = ['kL', 'kM', 'kR'];
const mv = (o) => M.push(o);
// English
mv({ blocks: ['harold'], at: "l06.Harold's", dur: 0.9, appear: true, appearFrom: 20 });
mv({ blocks: B_ALL, at: 'l06.stood', dur: 0.7, stagger: 0.12, appear: true, appearFrom: 16 });
mv({ blocks: W_ALL, at: 'l06.shoulder', dur: 0.6, stagger: 0.1, appear: true, appearFrom: 16 });
// Normans arrive on the south
mv({ group: 'arch', at: 'l07.archers', dur: 0.8, stagger: 0.14, appear: true, appearFrom: 18 });
mv({ group: 'inf', at: 'l07.foot', dur: 0.8, stagger: 0.14, appear: true, appearFrom: 18 });
mv({ blocks: KN, at: 'l07.knights', dur: 0.8, stagger: 0.14, appear: true, appearFrom: 18 });
mv({ blocks: ['wm'], at: 'l07.Williams', dur: 0.9, appear: true, appearFrom: 20 });
// l08: the attack. Archers to mid slope, foot soldiers to the wall, knights charge, everyone falls back, then a second push
mv({ group: 'arch', at: 'l08.The', dur: 2.4, to: { z: 34 }, ease: 'out' });
mv({ group: 'inf', at: 'l08.Normans', dur: 3.6, to: { z: -30 }, ease: 'inOut' });
mv({ blocks: KN, at: 'l08.attacked,', dur: 3.0, to: { z: 28 }, ease: 'out' });
mv({ group: 'inf', at: 'l08.knights', dur: 0.9, to: { z: -6 }, ease: 'out' });
mv({ blocks: KN, at: 'l08.knights', dur: 1.2, to: { z: -32 }, ease: 'in' });
mv({ blocks: KN, at: 'l08.axes,', dur: 1.2, to: { z: 6 }, ease: 'out' });
mv({ group: 'inf', at: 'l08.held,', dur: 1.5, to: { z: 22 }, ease: 'inOut' });
mv({ blocks: KN, at: 'l08.held,', dur: 1.5, to: { z: 38 }, ease: 'inOut' });
mv({ group: 'arch', at: 'l08.held,', dur: 1.5, to: { z: 50 }, ease: 'inOut' });
mv({ group: 'inf', at: 'l08.hour', dur: 1.8, to: { z: -30 }, ease: 'inOut' });
mv({ group: 'arch', at: 'l08.hour', dur: 1.4, to: { z: 34 }, ease: 'inOut' });
// l09: the rumour. They wobble, then run
for (const g of ['arch', 'inf']) { mv({ group: g, at: 'l09.William', dur: 0.2, stagger: 0.07, to: { heading: 12 } }); mv({ group: g, at: 'l09.William+0.2', dur: 0.2, stagger: 0.07, to: { heading: -12 } }); mv({ group: g, at: 'l09.William+0.4', dur: 0.2, stagger: 0.07, to: { heading: 0 } }); }
mv({ group: 'inf', at: 'l09.William', dur: 0.9, to: { z: -16 }, ease: 'out' });
mv({ blocks: ['wm'], at: 'l09.dead.', dur: 0.3, to: { alpha: 0.25 } });
mv({ group: 'arch', at: 'l09.soldier', dur: 1.9, to: { z: 132 }, ease: 'inQuad' });
mv({ group: 'inf', at: 'l09.soldier', dur: 1.9, to: { z: 142 }, ease: 'inQuad' });
mv({ blocks: KN, at: 'l09.soldier', dur: 1.9, to: { z: 158 }, ease: 'inQuad' });
for (const g of ['arch', 'inf']) mv({ group: g, at: 'l09.soldier', dur: 0.4, to: { heading: 180 } });
mv({ blocks: KN, at: 'l09.soldier', dur: 0.4, to: { heading: 180 } });
// l10: William lifts his helmet, the banner goes up, they turn around
mv({ blocks: ['wm'], at: 'l10.William', dur: 0.4, to: { alpha: 1 } });
mv({ blocks: ['wm'], at: 'l10.helmet', dur: 0.5, to: { lift: 7, scale: 1.4 }, ease: 'outBack' });
mv({ group: 'arch', at: 'l10.turned', dur: 0.5, to: { heading: 0 } }); mv({ group: 'inf', at: 'l10.turned', dur: 0.5, to: { heading: 0 } }); mv({ blocks: KN, at: 'l10.turned', dur: 0.5, to: { heading: 0 } });
mv({ group: 'arch', at: 'l10.turned', dur: 2.4, to: { z: 62 }, ease: 'out' });
mv({ group: 'inf', at: 'l10.turned', dur: 2.4, to: { z: 46 }, ease: 'out' });
mv({ blocks: KN, at: 'l10.turned', dur: 2.4, to: { z: 40 }, ease: 'out' });
mv({ blocks: ['wm'], at: 'l10.turned', dur: 2.4, to: { z: 110, lift: 0, scale: 1 }, ease: 'out' });
// l11: the trick. Knights slip to the flanks, the rest "run away"
mv({ blocks: ['kL'], at: 'l11.Norman', dur: 1.6, to: { x: -100, z: 64 }, ease: 'inOut' });
mv({ blocks: ['kR'], at: 'l11.Norman', dur: 1.6, to: { x: 100, z: 64 }, ease: 'inOut' });
mv({ group: 'arch', at: 'l11.pretend', dur: 0.4, to: { heading: 180 } }); mv({ group: 'inf', at: 'l11.pretend', dur: 0.4, to: { heading: 180 } }); mv({ blocks: ['kM'], at: 'l11.pretend', dur: 0.4, to: { heading: 180 } });
mv({ group: 'arch', at: 'l11.pretend', dur: 2.2, to: { z: 136 }, ease: 'inOut' });
mv({ group: 'inf', at: 'l11.pretend', dur: 2.2, to: { z: 104 }, ease: 'inOut' });
mv({ blocks: ['kM'], at: 'l11.pretend', dur: 2.2, to: { z: 150 }, ease: 'inOut' });
// l12: the first chase (w1, w2 run down the hill), the knights wheel round them
mv({ blocks: ['w1', 'w2'], at: 'l12.chased', dur: 3.4, to: { z: 70, x: undefined }, ease: 'inQuad' });
mv({ blocks: ['w1'], at: 'l12.chased', dur: 3.4, to: { x: -44 }, ease: 'linear' });
mv({ blocks: ['w2'], at: 'l12.chased', dur: 3.4, to: { x: -29 }, ease: 'linear' });
for (const g of ['arch', 'inf']) mv({ group: g, at: 'l12.Norman', dur: 0.4, to: { heading: 0 } });
mv({ group: 'inf', at: 'l12.Norman', dur: 1.3, to: { z: 92 }, ease: 'out' });
mv({ blocks: ['kL'], at: 'l12.Norman', dur: 1.7, path: [[-82, 70], [-66, 72]], ease: 'inOut' });
mv({ blocks: ['kR'], at: 'l12.Norman', dur: 1.7, path: [[40, 64], [8, 72], [-6, 72]], ease: 'inOut' });
mv({ blocks: ['kM'], at: 'l12.Norman', dur: 1.9, path: [[34, 96], [34, 66], [-6, 56], [-36, 54]], ease: 'inOut' });
mv({ blocks: ['kL', 'kR'], at: 'l12.Norman', dur: 0.4, to: { heading: 90 } });
mv({ blocks: ['w1', 'w2'], at: 'l12.surrounded', dur: 1.5, stagger: 0.2, fadeTo: 1, alphaTo: 0.12, sinkTo: 0.9 });
// l13: again
mv({ blocks: ['kL'], at: 'l13.They', dur: 1.3, to: { x: -100, z: 62, heading: 0 }, ease: 'inOut' });
mv({ blocks: ['kM'], at: 'l13.They', dur: 1.3, to: { x: 0, z: 74, heading: 180 }, ease: 'inOut' });
mv({ blocks: ['kR'], at: 'l13.They', dur: 1.3, to: { x: 100, z: 62, heading: 0 }, ease: 'inOut' });
for (const g of ['arch', 'inf']) mv({ group: g, at: 'l13.more', dur: 0.4, to: { heading: 180 } });
mv({ group: 'arch', at: 'l13.more', dur: 1.8, to: { z: 136 }, ease: 'inOut' });
mv({ group: 'inf', at: 'l13.more', dur: 1.8, to: { z: 104 }, ease: 'inOut' });
mv({ blocks: ['w5'], at: 'l13.once,', dur: 1.9, to: { x: 31, z: 68 }, ease: 'inQuad' });
mv({ blocks: ['w6'], at: 'l13.once,', dur: 1.9, to: { x: 46, z: 68 }, ease: 'inQuad' });
for (const g of ['arch', 'inf']) mv({ group: g, at: 'l13.every', dur: 0.4, to: { heading: 0 } });
mv({ group: 'inf', at: 'l13.every', dur: 1.0, to: { z: 92 }, ease: 'out' });
mv({ blocks: ['kR'], at: 'l13.every', dur: 1.4, path: [[100, 62], [76, 70], [64, 72]], ease: 'inOut' });
mv({ blocks: ['kL'], at: 'l13.every', dur: 1.5, path: [[-60, 52], [-14, 56], [14, 72]], ease: 'inOut' });
mv({ blocks: ['kM'], at: 'l13.every', dur: 1.5, path: [[40, 60], [38, 54]], ease: 'inOut' });
mv({ blocks: ['kL', 'kR'], at: 'l13.every', dur: 0.3, to: { heading: 90 } });
mv({ blocks: ['w5', 'w6'], at: 'l13.the', dur: 1.3, stagger: 0.2, fadeTo: 1, alphaTo: 0.12, sinkTo: 0.9 });
// the wall gets thinner: what is left squeezes together
mv({ blocks: ['w0', 'w3', 'w4', 'w7', ...B_ALL], at: 'l13.thinner.', dur: 1.2, squeeze: { about: [0, -50], kx: 0.62, kz: 1 }, ease: 'inOut' });
mv({ blocks: ['w0', 'w3', 'w4', 'w7'], at: 'l13.thinner.', dur: 1.2, to: { len: 12 }, ease: 'inOut' });
// the Normans regroup at the foot of the slope
mv({ group: 'inf', at: 'l13.thinner.', dur: 1.6, to: { z: 30, heading: 0 }, ease: 'inOut' });
mv({ group: 'arch', at: 'l13.thinner.', dur: 1.6, to: { z: 52, heading: 0 }, ease: 'inOut' });
mv({ blocks: KN, at: 'l13.thinner.', dur: 1.6, to: { z: 40, heading: 0 }, ease: 'inOut' });
mv({ blocks: ['kL'], at: 'l13.thinner.', dur: 1.6, to: { x: -50 }, ease: 'inOut' }); mv({ blocks: ['kM'], at: 'l13.thinner.', dur: 1.6, to: { x: 0 }, ease: 'inOut' }); mv({ blocks: ['kR'], at: 'l13.thinner.', dur: 1.6, to: { x: 50 }, ease: 'inOut' });
// l14: late in the day, the last push; Harold falls (the crown drops, the block fades by numbers)
mv({ group: 'inf', at: 'l14.Late', dur: 2.4, to: { z: -28 }, ease: 'inOut' });
mv({ group: 'arch', at: 'l14.Late', dur: 2.4, to: { z: 30 }, ease: 'inOut' });
mv({ blocks: KN, at: 'l14.King', dur: 1.8, to: { z: -30 }, ease: 'in' });
mv({ blocks: ['harold'], at: 'l14.killed.', dur: 1.3, fadeTo: 1, alphaTo: 0.15, sinkTo: 0.9 });
mv({ blocks: KN, at: 'l14.killed.', dur: 2.0, to: { z: 0 }, ease: 'out' });
// l15: the English army breaks apart (fading blocks, scattering north), the Normans march up
const ENG_LEFT = ['w0', 'w3', 'w4', 'w7', ...B_ALL];
ENG_LEFT.forEach((id, i) => { const dir = i % 2 ? 1 : -1; mv({ blocks: [id], at: 'l15.broke', dur: 2.2, by: { x: dir * (14 + (i % 4) * 9), z: -34 - (i % 3) * 8 }, ease: 'inQuad' }); mv({ blocks: [id], at: { line: 'l15', word: 'broke', offset: 0.1 * (i % 5) }, dur: 1.6, fadeTo: 1, alphaTo: 0.1, sinkTo: 0.9 }); });
mv({ group: 'inf', at: 'l15.Without', dur: 3.4, to: { z: -46 }, ease: 'inOut' });
mv({ group: 'arch', at: 'l15.Without', dur: 3.4, to: { z: 6 }, ease: 'inOut' });
mv({ blocks: KN, at: 'l15.the', dur: 3.0, to: { z: -50 }, ease: 'inOut' });

// ---- camera (battlefield)
hill.camera = [
  { at: 53.0, target: [0, 0], width: 760, pitch: 46, yaw: 0, mm: 35 },
  { at: 'l06.14th', target: [0, -10], width: 560, pitch: 46, yaw: 12, mm: 35, ease: 'inOut' },
  { at: "l06.Harold's", target: [0, -50], width: 330, pitch: 38, yaw: 22, mm: 35, ease: 'inOut' },
  { at: 'l06.shoulder', target: [0, -48], width: 210, pitch: 30, yaw: 8, mm: 35, ease: 'inOut' },
  { at: 'l06.wall.', target: [0, -48], width: 270, pitch: 34, yaw: -14, mm: 35, ease: 'inOut' },
  { at: 'l07.Williams', target: [0, 118], width: 330, pitch: 34, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l07.Their', target: [0, 30], width: 520, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l08.The', target: [0, 18], width: 430, pitch: 44, yaw: 8, mm: 35, ease: 'inOut' },
  { at: 'l08.knights', target: [0, -8], width: 290, pitch: 36, yaw: 18, mm: 35, ease: 'inOut' },
  { at: 'l08.and', target: [0, -26], width: 250, pitch: 32, yaw: -12, mm: 35, ease: 'inOut' },
  { at: 'l08.hour', target: [0, -2], width: 360, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l09.then', target: [0, 22], width: 400, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l09.His', target: [0, 70], width: 460, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l10.William', target: [0, 112], width: 240, pitch: 36, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l10.turned', target: [0, 60], width: 430, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l11.Then,', target: [0, 50], width: 420, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l11.They', target: [0, 62], width: 420, pitch: 55, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l12.Some', target: [-34, 32], width: 360, pitch: 55, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l12.Norman', target: [-34, 68], width: 230, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l12.surrounded.+1.5', target: [-34, 68], width: 230, pitch: 58, yaw: 0, mm: 35, ease: 'linear' },
  { at: 'l13.once,', target: [10, 50], width: 340, pitch: 56, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l13.every', target: [24, 66], width: 240, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l13.chase,', target: [24, 66], width: 240, pitch: 58, yaw: 0, mm: 35, ease: 'linear' },
  { at: 'l13.the', target: [0, -30], width: 300, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l14.Late', target: [0, -44], width: 330, pitch: 24, yaw: 22, mm: 32, ease: 'inOut' },
  { at: 'l14.Historians', target: [0, -44], width: 330, pitch: 22, yaw: -22, mm: 32, ease: 'linear' },
  { at: 'l15.Without', target: [0, -30], width: 380, pitch: 40, yaw: -8, mm: 35, ease: 'inOut' },
  { at: 'l15.broke', target: [0, -40], width: 420, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
  { at: 'l16.On', target: [0, -40], width: 440, pitch: 56, yaw: 0, mm: 35, ease: 'linear' },
];

hill.light = [
  { at: 'l13.They', dur: 5.5, to: { eve: 0.3 }, ease: 'inOut' },
  { at: 'l14.Late', dur: 3.4, to: { eve: 1 }, ease: 'inOut' }, { at: 'l14.Late', dur: 3.4, to: { haze: 1.3 }, ease: 'inOut' },
];

// ---- arrows (battlefield)
hill.arrows = [
  { id: 'up', at: 'l07.Go', until: 'l07.hill.', ease: 'out', team: 'rome', width: 7, path: [[0, 118], [0, -20]], lift: 6, hide: 'l08.The' },
  { at: 'l09.soldier', dur: 1.4, ease: 'out', team: 'rome', style: 'dash', width: 5, path: [[0, -10], [0, 110]], lift: 6, hide: 'l10.William' },
  { at: 'l10.turned', dur: 1.2, ease: 'out', team: 'rome', width: 6, path: [[0, 100], [0, 30]], lift: 6, hide: 'l11.Then,' },
  { at: 'l11.pretend', dur: 1.6, ease: 'out', team: 'gold', style: 'dash', width: 5, path: [[-30, 40], [-30, 110]], lift: 6, hide: 'l12.Some' },
  { at: 'l11.pretend', dur: 1.6, ease: 'out', team: 'gold', style: 'dash', width: 5, path: [[34, 40], [34, 110]], lift: 6, hide: 'l12.Some' },
  { at: 'l12.chased', dur: 1.8, ease: 'out', team: 'carthage', width: 4.5, path: [[-37, -34], [-37, 56]], lift: 6, hide: 'l12.surrounded.' },
  { at: 'l12.surrounded.', dur: 1.2, ease: 'inOut', team: 'gold', width: 2.2, head: false, smooth: true, lift: 6, hide: 'l13.They', path: [[-84, 52], [-36, 44], [8, 52], [10, 86], [-36, 94], [-84, 86], [-84, 52]] },
  { at: 'l13.once,', dur: 1.5, ease: 'out', team: 'carthage', width: 4.5, path: [[38, -34], [38, 56]], lift: 6, hide: 'l13.the' },
  { at: 'l13.every', dur: 1.2, ease: 'inOut', team: 'gold', width: 2.2, head: false, smooth: true, lift: 6, hide: 'l13.the', path: [[-4, 50], [40, 42], [86, 52], [88, 86], [40, 96], [-4, 86], [-4, 50]] },
  { at: 'l15.broke', dur: 1.6, ease: 'out', team: 'rome', width: 7, path: [[0, -30], [0, -100]], lift: 6, hide: 'l16.On' },
];

// ---- labels, icons, counters, volleys (battlefield)
hill.labels = [
  { at: 53.9, until: 'l06.Harold\'s', text: '14 OCTOBER 1066', screen: [0.5, 0.12], big: true },
  { at: 'l06.Harold\'s', until: 'l06.shoulder', text: 'HAROLD', block: 'harold', team: 'carthage', dy: -0.12 },
  { at: 'l06.hill,', until: 'l06.shoulder', text: 'SENLAC HILL', pos: [-100, -58], y: 14, dy: -0.12, big: true },
  { at: 'l06.shoulder', until: 'l06.shields', text: 'SHOULDER TO SHOULDER', block: 'w3', team: 'carthage', dy: -0.2, big: true },
  { at: 'l06.shields', until: 'l06.wall.', text: 'SHIELDS LOCKED TOGETHER', block: 'w3', team: 'carthage', dy: -0.2, big: true },
  { at: 'l06.wall.', until: 'l07.Williams', text: 'THE SHIELD WALL', block: 'w3', team: 'carthage', dy: -0.22, big: true },
  { at: 'l07.Williams', until: 'l07.archers,', text: 'WILLIAM\'S ARMY', block: 'wm', team: 'rome', dy: -0.2, big: true },
  { at: 'l07.archers,', until: 'l07.foot', text: 'ARCHERS', block: 'arch', team: 'rome', dx: -0.3, dy: -0.04 },
  { at: 'l07.foot', until: 'l07.knights', text: 'FOOT SOLDIERS', block: 'inf', team: 'rome', dx: 0.32, dy: 0.0 },
  { at: 'l07.knights', until: 'l07.Their', text: 'KNIGHTS', block: 'kM', team: 'rome', dy: 0.12 },
  { at: 'l07.hill.', until: 'l07.Not', text: 'UP THE HILL', pos: [0, 40], y: 8, dx: 0.15, dy: 0, team: 'rome', big: true },
  { at: 'l07.Not', until: 'l08.The', text: 'NOT FUN', pos: [0, 40], y: 8, dx: 0.15, dy: 0, team: 'rome', big: true },
  { at: 'l08.The', until: 'l08.arrows', text: 'THE NORMANS ATTACK', screen: [0.5, 0.12], big: true },
  { at: 'l08.arrows', until: 'l08.knights', text: 'ARROWS VS SHIELDS', screen: [0.5, 0.12], big: true },
  { at: 'l08.knights', until: 'l08.and', text: 'KNIGHTS VS AXES', screen: [0.5, 0.12], big: true },
  { at: 'l08.wall', until: 'l08.hour', text: 'THE WALL HOLDS', screen: [0.5, 0.12], big: true, team: 'carthage' },
  { at: 'l08.hour', until: 'l08.after', text: 'HOUR 1', screen: [0.5, 0.12], big: true, size: 1.2 },
  { at: 'l08.after', until: 'l08.hour#1', text: 'HOUR 2', screen: [0.5, 0.12], big: true, size: 1.2 },
  { at: 'l08.hour#1', until: 'l09.then', text: 'HOUR 3', screen: [0.5, 0.12], big: true, size: 1.2 },
  { at: 'l09.rumor', until: 'l09.William', text: 'A RUMOR', block: 'inf', team: 'rome', dy: -0.18, big: true },
  { at: 'l09.William', until: 'l09.His', text: 'WILLIAM IS DEAD!', screen: [0.5, 0.14], big: true, team: 'rome', size: 1.15 },
  { at: 'l09.His', until: 'l10.William', text: 'RUN!', block: 'inf', team: 'rome', dy: -0.16, big: true },
  { at: 'l10.William', until: 'l10.I\'m', text: 'WILLIAM', block: 'wm', team: 'rome', dy: -0.2, big: true },
  { at: 'l10.I\'m', until: 'l10.he', text: 'I\'M ALIVE!', screen: [0.5, 0.14], big: true, team: 'rome', size: 1.3 },
  { at: 'l10.turned', until: 'l11.Then,', text: 'TURN AROUND', block: 'inf', team: 'rome', dy: -0.16, big: true },
  { at: 'l11.writers', until: 'l11.try', text: 'THE NORMAN WRITERS SAY', screen: [0.5, 0.13], big: true },
  { at: 'l11.trick.', until: 'l11.They', text: 'A TRICK', screen: [0.5, 0.13], big: true, team: 'rome', size: 1.3 },
  { at: 'l11.pretend', until: 'l12.Some', text: 'PRETENDING TO RUN', block: 'inf', team: 'rome', dy: -0.16, big: true },
  { at: 'l12.chased', until: 'l12.left', text: 'THE ENGLISH CHASE', block: 'w1', team: 'carthage', dy: -0.2, big: true },
  { at: 'l12.left', until: 'l12.Norman', text: 'A GAP IN THE WALL', pos: [-36, -46], y: 6, dy: -0.18, team: 'carthage', big: true },
  { at: 'l12.surrounded.', until: 'l13.They', text: 'SURROUNDED', pos: [-36, 70], y: 4, dy: -0.2, team: 'rome', big: true },
  { at: 'l13.more', until: 'l13.and', text: 'AGAIN', screen: [0.5, 0.13], big: true, size: 1.3 },
  { at: 'l13.and', until: 'l13.the', text: 'AND AGAIN', screen: [0.5, 0.13], big: true, size: 1.3 },
  { at: 'l13.the', until: 'l14.Late', text: 'THE WALL GETS THINNER', screen: [0.5, 0.13], big: true, team: 'carthage' },
  { at: 'l14.Harold', until: 'l14.killed.', text: 'KING HAROLD', block: 'harold', team: 'carthage', dy: -0.2, big: true },
  { at: 'l14.Bayou', until: 'l14.may', text: 'THE BAYEUX TAPESTRY', screen: [0.5, 0.82], big: true },
  { at: 'l14.may', until: 'l14.Historians', text: 'MAYBE', screen: [0.5, 0.82], big: true },
  { at: 'l14.Historians', until: 'l14.It', text: 'HISTORIANS STILL ARGUE', screen: [0.5, 0.86], big: true },
  { at: 'l14.ask', until: 'l15.Without', text: 'TRY ASKING A TAPESTRY', screen: [0.5, 0.86], big: true },
  { at: 'l15.Without', until: 'l15.the', text: 'NO KING', block: 'w3', team: 'carthage', dy: -0.18, big: true },
  { at: 'l15.broke', until: 'l16.On', text: 'THE ENGLISH ARMY BREAKS', screen: [0.5, 0.13], big: true, team: 'carthage' },
];
hill.icons = [
  { at: 'l06.shields', until: 'l07.Williams', icon: 'shield', team: 'carthage', pos: [-40, -46], y: 6, size: 15, anim: 'bounce' },
  { at: 'l06.shields', until: 'l07.Williams', icon: 'shield', team: 'carthage', pos: [0, -46], y: 6, size: 15, anim: 'bounce' },
  { at: 'l06.shields', until: 'l07.Williams', icon: 'shield', team: 'carthage', pos: [40, -46], y: 6, size: 15, anim: 'bounce' },
  { at: 'l07.archers,', until: 'l07.foot', icon: 'bow', block: 'arch', size: 16, anim: 'bounce' },
  { at: 'l07.Not', until: 'l08.The', icon: 'no', pos: [0, 70], y: 4, size: 18 },
  { at: 'l08.swinging', until: 'l08.and', icon: 'burst', pos: [-45, -44], y: 4, size: 16, anim: 'bounce' },
  { at: 'l08.swinging', until: 'l08.and', icon: 'burst', pos: [0, -44], y: 4, size: 16, anim: 'bounce' },
  { at: 'l08.swinging', until: 'l08.and', icon: 'burst', pos: [45, -44], y: 4, size: 16, anim: 'bounce' },
  { at: 'l08.wall', until: 'l08.hour', icon: 'check', pos: [0, -46], y: 4, size: 18 },
  { at: 'l09.rumor', until: 'l09.William', icon: 'question', block: 'inf', size: 16, anim: 'bounce' },
  { at: 'l09.dead.', until: 'l10.William', icon: 'cross', pos: [0, 166], y: 6, size: 14 },
  { at: 'l10.helmet', until: 'l10.turned', icon: 'helmet', team: 'rome', pos: [0, 166], y: 22, size: 18, anim: 'bounce' },
  { at: 'l10.I\'m', until: 'l10.he', icon: 'burst', pos: [0, 166], y: 28, size: 26, anim: 'bounce' },
  { at: 'l11.writers', until: 'l11.try', icon: 'book', screen: [0.5, 0.26], size: 0.14, anim: 'bounce' },
  { at: 'l11.trick.', until: 'l11.They', icon: 'star', screen: [0.5, 0.27], size: 0.12, anim: 'bounce' },
  { at: 'l12.left', until: 'l12.Norman', icon: 'door', pos: [-36, -46], y: 4, size: 14 },
  { at: 'l12.surrounded.', until: 'l13.They', icon: 'burst', pos: [-36, 70], y: 8, size: 18, anim: 'bounce' },
  { at: 'l13.every', until: 'l13.the', icon: 'burst', pos: [38, 70], y: 8, size: 18, anim: 'bounce' },
  { at: 'l14.King', until: 'l14.killed.+1.2', fallAt: 'l14.killed.', fallDur: 0.9, icon: 'crown', block: 'harold', size: 16 },
  { at: 'l14.embroidery,', until: 'l14.may', icon: 'tapestry', fill: 'plain', screen: [0.5, 0.40], size: 0.30 },
  { at: 'l14.may', until: 'l14.Historians', icon: 'tapestry', screen: [0.5, 0.40], size: 0.30, anim: 'bounce' },
  { at: 'l14.Historians', until: 'l14.It', icon: 'book', screen: [0.2, 0.62], size: 0.17, anim: 'sway' },
  { at: 'l14.Historians', until: 'l14.It', icon: 'book', screen: [0.8, 0.62], size: 0.17, anim: 'sway', flip: true },
  { at: 'l14.It', until: 'l14.questions.', icon: 'tapestry', screen: [0.5, 0.40], size: 0.30 },
  { at: 'l14.questions.', until: 'l15.Without', icon: 'question', screen: [0.3, 0.46], size: 0.18, anim: 'bounce' },
  { at: 'l14.questions.+0.15', until: 'l15.Without', icon: 'question', screen: [0.5, 0.3], size: 0.2, anim: 'bounce' },
  { at: 'l14.questions.+0.3', until: 'l15.Without', icon: 'question', screen: [0.7, 0.46], size: 0.18, anim: 'bounce' },
];
hill.volleys = [
  { at: 'l08.arrows', dur: 1.2, from: [0, 34, 56], to: [0, -44, 60], n: 40, flight: 0.95, spread: 0.35, team: 'rome' },
  { at: 'l08.into', dur: 1.2, from: [0, 34, 56], to: [0, -44, 60], n: 40, flight: 0.95, spread: 0.35, team: 'rome' },
  { at: 'l08.hour', dur: 1.2, from: [0, 34, 56], to: [0, -44, 60], n: 40, flight: 0.95, spread: 0.35, team: 'rome' },
  { at: 'l14.Late', dur: 1.2, from: [0, 30, 56], to: [0, -44, 50], n: 36, flight: 0.95, spread: 0.35, team: 'rome' },
];

// ------------------------------------------------------------------ the film (main stage = England and Normandy)
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 }, edgeStart: 1500, edgeEnd: 2600, fogDensity: 0.0009 },
  world: england,
  stages: { bat: hill },
  msaaOn: [[0, 17.5], [134, 160]],

  blocks: {
    harold: { ...ENG, kind: 'infantry', x: 150, z: -50, heading: 0, len: 54, dep: 24, height: 6, bannerScale: 2.2, hidden: true },
    willN: { ...NOR, kind: 'infantry', x: 66, z: 200, heading: 0, len: 54, dep: 24, height: 6, bannerScale: 2.2, hidden: true },
    willE: { ...NOR, kind: 'infantry', x: 150, z: 38, heading: 0, len: 54, dep: 24, height: 6, bannerScale: 2.2, hidden: true },
    vik: { ...VIK, kind: 'infantry', x: 126, z: -192, heading: 270, len: 54, dep: 24, height: 6, bannerScale: 2.2, hidden: true },
  },

  moves: [
    // l02: Harold appears at London
    { block: 'harold', at: 'l02.English', dur: 0.9, appear: true, appearFrom: 26 },
    // l03: William in Normandy
    { block: 'willN', at: 'l03.duke', dur: 0.9, appear: true, appearFrom: 26 },
    // l04: Vikings land, Harold marches north, the Vikings fade by numbers
    { block: 'vik', at: 'l04.invaded', dur: 1.0, appear: true, appearFrom: 26 },
    { block: 'harold', at: 'l04.marched', dur: 1.9, path: [[132, -92], [108, -132], [86, -174]], ease: 'inOut' },
    { block: 'vik', at: 'l04.beat', dur: 1.6, fadeTo: 1, alphaTo: 0.1, sinkTo: 0.9 },
    // l05: William lands (the red block arrives with the ships), Harold marches back down
    { block: 'willN', at: 'l05.William', dur: 0.4, vanish: true },
    { block: 'willE', at: 'l05.south,', dur: 0.9, appear: true, appearFrom: 26 },
    { block: 'harold', at: 'l05.so', dur: 4.2, path: [[104, -140], [132, -84], [150, -42], [176, 0], [188, 32]], ease: 'linear' },
    { block: 'harold', at: 53.0, dur: 0.5, vanish: true },
    // l16: Christmas Day: William marches from Hastings to London
    { block: 'willE', at: 'l16.Christmas', dur: 1.6, path: [[172, 6], [150, -26], [140, -52]], ease: 'inOut' },
  ],

  light: [],

  camera: [
    { at: 0, target: [10, 48], width: 860, pitch: 84, yaw: 0, mm: 35 },
    { at: 'l00.three', target: [80, -60], width: 640, pitch: 66, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 12.3, target: [90, -60], width: 560, pitch: 64, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l02.In', target: [130, -70], width: 400, pitch: 64, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.Across', target: [110, 40], width: 660, pitch: 66, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.Normandy,', target: [80, 165], width: 460, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.fleet', target: [150, 140], width: 480, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.But', target: [120, -80], width: 700, pitch: 66, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.invaded', target: [150, -165], width: 460, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.Harold#1', target: [115, -135], width: 500, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 42.6, target: [115, -135], width: 500, pitch: 62, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l05.Three', target: [160, 95], width: 540, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l05.so', target: [125, -70], width: 700, pitch: 72, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l05.busy', target: [125, -65], width: 680, pitch: 72, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l16.On', target: [150, -10], width: 440, pitch: 60, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l16.William', target: [145, -45], width: 340, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l17.His', target: [145, -45], width: 340, pitch: 58, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l17.Normans', target: [20, 55], width: 860, pitch: 84, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 160, target: [20, 55], width: 840, pitch: 84, yaw: 0, mm: 35, ease: 'linear' },
  ],


  labels: [
    // hook
    { at: 'l00.1066,', until: 'l00.England', text: '1066', screen: [0.5, 0.17], style: 'text', big: true, size: 2.0, track: 0.16, weight: 800 },
    { at: 'l00.England', until: 'l00.kings', text: 'ENGLAND', pos: [60, -110], y: 6, dy: -0.12, team: 'carthage', big: true },
    { at: 'l00.last', until: 'l00.one.', text: 'THE LAST ONE', screen: [0.7, 0.34], big: true },
    // l02
    { at: 'l02.January,', until: 'l02.English', text: 'JANUARY 1066', screen: [0.5, 0.12], big: true },
    { at: 'l02.Old', until: 'l02.died.', text: 'THE OLD KING', pos: [150, -50], y: 10, dy: -0.16, big: true },
    { at: 'l02.English', until: 'l03.Across', text: 'LONDON', pos: [150, -50], y: 4, dy: 0.1, leader: false },
    { at: 'l02.Harold.', until: 'l04.But', text: 'HAROLD', block: 'harold', team: 'carthage', dy: -0.17, big: true },
    // l03
    { at: 'l03.Normandy,', until: 'l04.But', text: 'NORMANDY', pos: [70, 184], dx: -0.2, dy: 0.1, leader: false, big: true },
    { at: 'l03.duke', until: 'l03.excuse', text: 'DUKE WILLIAM', block: 'willN', team: 'rome', dx: 0.22, dy: -0.12, big: true },
    { at: 'l03.fleet', until: 'l04.But', text: 'A FLEET', pos: [190, 152], y: 10, dy: -0.14, team: 'rome', big: true },
    // l04
    { at: 'l04.Viking', until: 'l04.Hardrada,', text: 'A VIKING KING', screen: [0.5, 0.12], big: true },
    { at: 'l04.Hardrada,', until: 'l04.invaded', text: 'HARALD HARDRADA', screen: [0.5, 0.12], big: true, team: 'gold' },
    { at: 'l04.north.', until: 'l04.Harold#1', text: 'THE NORTH', pos: [126, -192], y: 6, dy: -0.18, team: 'gold', big: true },
    { at: 'l04.Harold#1', until: 'l04.beat', text: 'HAROLD MARCHES NORTH', screen: [0.5, 0.12], big: true, team: 'carthage' },
    { at: 'l04.Stamford', until: 'l05.Three', text: 'STAMFORD BRIDGE', pos: [100, -190], y: 4, dy: -0.18, big: true },
    // l05
    { at: 'l05.Three', until: 'l05.William', text: 'THREE DAYS LATER', screen: [0.5, 0.12], big: true },
    { at: 'l05.landed', until: 'l05.so', text: 'PEVENSEY', pos: [150, 40], y: 4, dy: -0.18, team: 'rome', big: true },
    { at: 'l05.south,', until: 'l05.so', text: 'WILLIAM LANDS IN THE SOUTH', screen: [0.5, 0.12], big: true, team: 'rome', size: 0.9 },
    { at: 'l05.tired', until: 'l05.army', text: 'TIRED', block: 'harold', team: 'carthage', dy: -0.17, big: true },
    { at: 'l05.busy', until: 53.4, text: 'BUSY MONTH', screen: [0.5, 0.82], big: true, size: 1.4 },
    // l16
    { at: 'l16.Christmas', until: 'l16.William', text: 'CHRISTMAS DAY', screen: [0.5, 0.12], big: true, size: 1.2 },
    { at: 'l16.William', until: 'l16.King', text: 'WESTMINSTER', pos: [140, -52], y: 8, dy: -0.2, big: true },
    { at: 'l16.King', until: 'l16.We', text: 'KING OF ENGLAND', block: 'willE', team: 'rome', dy: -0.22, big: true },
    { at: 'l16.William#1', until: 'l16>', text: 'WILLIAM THE CONQUEROR', screen: [0.5, 0.88], big: true, team: 'rome' },
    // l17
    { at: 'l17.French,', until: 'l17.All', text: 'FRENCH', pos: [60, 192], dy: 0.08, leader: false, big: true, team: 'rome' },
    { at: 'l17.English', until: 'l17.All', text: 'ENGLISH', pos: [-110, -10], dy: 0.08, leader: false, big: true, team: 'carthage' },
    { follow: 'beef', at: 'l17.beef,', until: 'l17.All+1.2', text: 'BEEF', dy: -0.08, big: true, size: 1.1 },
    { follow: 'jury', at: 'l17.jury,', until: 'l17.All+1.2', text: 'JURY', dy: -0.08, big: true, size: 1.1 },
    { follow: 'judge', at: 'l17.judge.', until: 'l17.All+1.2', text: 'JUDGE', dy: -0.08, big: true, size: 1.1 },
    { at: 'l17.All', until: 'l17>', text: 'ALL THANKS TO ONE LONG AFTERNOON ON A HILL', screen: [0.5, 0.9], big: true, size: 0.85 },
  ],

  counters: [
    { at: 'l05.so', until: 53.3, screen: [0.84, 0.28], team: 'carthage', from: 0, to: 250, countDur: 4.0, step: 5, suffix: 'MILES' },
  ],

  icons: [
    // three crowns, two crossed out in turn
    { id: 'c1', at: 'l00.three', until: 'l00>', icon: 'crown', screen: [0.3, 0.6], size: 0.2, anim: 'none' },
    { id: 'c2', at: 'l00.kings', until: 'l00>', icon: 'crown', screen: [0.5, 0.6], size: 0.2, anim: 'none' },
    { id: 'c3', at: 'l00.single', until: 'l00>', icon: 'crown', screen: [0.7, 0.6], size: 0.2, anim: 'none' },
    { at: 'l00.battle', until: 'l00>', icon: 'cross', screen: [0.3, 0.6], size: 0.2 },
    { at: 'l00.decided', until: 'l00>', icon: 'cross', screen: [0.5, 0.6], size: 0.2 },
    { at: 'l00.last', until: 'l00>', icon: 'star', screen: [0.7, 0.36], size: 0.1, anim: 'bounce' },
    // l02: the old king's crown drops; Harold is crowned
    { at: 'l02.Old', until: 'l02.died.+1.2', fallAt: 'l02.died.', fallDur: 0.9, icon: 'crown', pos: [150, -50], y: 20, size: 35 },
    { at: 'l02.crowned', until: 'l04.But', icon: 'crown', block: 'harold', size: 32, anim: 'bounce' },
    { at: 'l02.English', until: 'l03.Across', icon: 'city', team: 'carthage', pos: [150, -50], y: 0, size: 42, dx: 0.0, dy: 0.02 },
    // l03: William's "excuse me": a crown with a question mark; the fleet
    { at: 'l03.duke', until: 'l04.But', icon: 'city', team: 'rome', pos: [70, 184], y: 0, size: 38, dy: 0.0 },
    { at: 'l03.excuse', until: 'l03.and', icon: 'crown', pos: [70, 196], y: 30, size: 32, anim: 'bounce' },
    { at: 'l03.excuse', until: 'l03.and', icon: 'question', pos: [70, 196], y: 54, size: 35, anim: 'bounce' },
    { at: 'l03.built', until: 'l05.William+0.3', icon: 'ship', team: 'rome', pos: [150, 160], y: 0, size: 38 },
    { at: 'l03.fleet', until: 'l05.William+0.3', icon: 'ship', team: 'rome', pos: [190, 154], y: 0, size: 38 },
    { at: 'l03.fleet+0.2', until: 'l05.William+0.3', icon: 'ship', team: 'rome', pos: [230, 148], y: 0, size: 38 },
    // l04: Viking ships, then Stamford Bridge
    { follow: 'vA', at: 'l04.Viking', until: 'l04.Harold#1', icon: 'ship', team: 'gold', size: 38 },
    { follow: 'vB', at: 'l04.Viking+0.15', until: 'l04.Harold#1', icon: 'ship', team: 'gold', size: 38 },
    { follow: 'vC', at: 'l04.Viking+0.3', until: 'l04.Harold#1', icon: 'ship', team: 'gold', size: 38 },
    { at: 'l04.Bridge.', until: 'l05.Three', icon: 'laurel', team: 'carthage', pos: [100, -190], y: 6, size: 32, anim: 'bounce' },
    { at: 'l04.beat', until: 'l04.Bridge.', icon: 'burst', pos: [104, -190], y: 6, size: 35, anim: 'bounce' },
    // l05: William's fleet crosses, Harold marches back
    { follow: 'xA', at: 'l05.William', until: 'l05.so+0.6', icon: 'ship', team: 'rome', size: 38 },
    { follow: 'xB', at: 'l05.William', until: 'l05.so+0.6', icon: 'ship', team: 'rome', size: 38 },
    { follow: 'xC', at: 'l05.William', until: 'l05.so+0.6', icon: 'ship', team: 'rome', size: 38 },
    { at: 'l05.busy', until: 53.4, icon: 'burst', screen: [0.2, 0.8], size: 0.14, anim: 'bounce' },
    { at: 'l05.busy', until: 53.4, icon: 'burst', screen: [0.8, 0.8], size: 0.14, anim: 'bounce' },
    // l16: the coronation
    { at: 'l16.crowned', until: 'l17.His', icon: 'crown', block: 'willE', size: 35, anim: 'bounce' },
    { at: 'l16.Conqueror.', until: 'l17.His', icon: 'laurel', screen: [0.5, 0.68], size: 0.2, anim: 'bounce' },
    // l17
    { at: 'l17.French,', until: 'l17.All', icon: 'flag', team: 'rome', pos: [60, 192], y: 0, size: 38 },
    { at: 'l17.English', until: 'l17.All', icon: 'flag', team: 'carthage', pos: [-110, -10], y: 0, size: 38 },
    { at: 'l17.hill.', until: 'l17>', icon: 'swords', pos: [190, 36], y: 6, size: 48, anim: 'bounce' },
  ],

  arrows: [
    // l04: the Vikings sail in from the north east; Harold marches up the road
    { id: 'vA', at: 'l04.Viking', until: 'l04.north.', ease: 'inOut', team: 'gold', width: 3.2, path: [[340, -236], [140, -196]], lift: 4, hide: 'l05.Three', head: false },
    { id: 'vB', at: 'l04.Viking+0.15', until: 'l04.north.', ease: 'inOut', team: 'gold', width: 3.2, path: [[340, -210], [134, -190]], lift: 4, hide: 'l05.Three', head: false },
    { id: 'vC', at: 'l04.Viking+0.3', until: 'l04.north.', ease: 'inOut', team: 'gold', width: 3.2, path: [[340, -184], [128, -184]], lift: 4, hide: 'l05.Three', head: true },
    { at: 'l04.marched', dur: 1.9, ease: 'inOut', team: 'carthage', width: 7, path: [[132, -92], [108, -132], [86, -174]], lift: 5, hide: 'l05.Three' },
    // l05: the fleet crosses; Harold's long march back
    { id: 'xA', at: 'l05.William', until: 'l05.south,+0.5', ease: 'inOut', team: 'rome', width: 3.2, path: [[150, 158], [146, 52]], lift: 4, hide: 'l05.so', head: false },
    { id: 'xB', at: 'l05.William', until: 'l05.south,+0.5', ease: 'inOut', team: 'rome', width: 3.2, path: [[190, 152], [160, 50]], lift: 4, hide: 'l05.so', head: false },
    { id: 'xC', at: 'l05.William', until: 'l05.south,+0.5', ease: 'inOut', team: 'rome', width: 3.2, path: [[230, 146], [176, 48]], lift: 4, hide: 'l05.so', head: true },
    { at: 'l05.so', until: 'l05.miles,', ease: 'linear', team: 'carthage', width: 7, style: 'dash', path: [[86, -176], [104, -140], [132, -84], [150, -42], [176, 0], [188, 32]], lift: 5, hide: 53.2 },
    // l16: William to London
    { at: 'l16.Christmas', dur: 1.6, ease: 'inOut', team: 'rome', width: 7, path: [[172, 6], [150, -26], [140, -52]], lift: 5, hide: 'l17.His' },
    // l17: words float from Normandy to England
    { id: 'beef', at: 'l17.beef,', dur: 1.9, ease: 'inOut', team: 'ink', style: 'dash', width: 4, path: [[30, 188], [30, 90], [10, 20], [4, -20]], lift: 8, hide: 'l17.All+1.4' },
    { id: 'jury', at: 'l17.jury,', dur: 1.9, ease: 'inOut', team: 'ink', style: 'dash', width: 4, path: [[70, 190], [90, 90], [110, 10], [112, -40]], lift: 8, hide: 'l17.All+1.4' },
    { id: 'judge', at: 'l17.judge.', dur: 1.9, ease: 'inOut', team: 'ink', style: 'dash', width: 4, path: [[110, 186], [150, 90], [200, 20], [214, -20]], lift: 8, hide: 'l17.All+1.4' },
  ],

  volleys: [],

  cards: [
    { at: 0, until: 1.0, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 12.3, until: 16.6, scrim: 0.9, scrimCenter: 'rgba(20,10,4,0.85)', fadeIn: 0.25, fadeOut: 0.7, lines: [
      { text: 'THE BATTLE OF HASTINGS', size: 0.078, y: 0.44, delay: 0 },
      { text: '1066', size: 0.07, y: 0.585, delay: 1.0, colorTop: '#ffd9a0', colorBottom: '#e2873a' } ], ornaments: [{ y: 0.35, w: 0.62 }, { y: 0.68, w: 0.62 }] },
    { at: 151.2, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.13, y: 0.43, delay: 0.1, track: 0.14 },
      { text: 'The Battle of Hastings, 1066', size: 0.062, y: 0.6, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.5 }, { y: 0.69, w: 0.5 }] },
  ],

  insets: [
    { stage: 'bat', at: 53.4, until: 134.4, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.6, out: 0.5, samples: 0 },
  ],
};
