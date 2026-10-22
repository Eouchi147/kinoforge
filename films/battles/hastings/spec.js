// The Battle of Hastings (1066): Battle Map v2 spec (engine: films/lib/battlemap/SPEC.md; scene list and reasons: NOTES.md).
// Colours: the English royal blue (team 'carthage'), the Normans deep red (team 'rome'), the Norwegians gold.
// Two maps: the main stage is England, the Channel and Normandy (the build-up and the coronation); the 'bat' stage is the field below the
// English ridge (Senlac hill), shown full screen in S1 and S4 to S7. Map units: x east, z south; on the field 1 unit is about 10 m.
// Times come from the cue words; the line starts never change (the sound is re-scored around them).
const ENG = { team: 'carthage' }, NOR = { team: 'rome' }, VIK = { team: 'gold' };

// ------------------------------------------------------------------ England, the Channel and Normandy
const england = {
  seed: 1066, size: [760, 500], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 250, elevation: 32 }, sunEve: { azimuth: 284, elevation: 10 },
  style: { contour: 4, pxPerUnit: 5.4, palette: [[-4, [0.62, 0.72, 0.46]], [3, [0.74, 0.76, 0.48]], [14, [0.80, 0.70, 0.46]], [30, [0.72, 0.58, 0.42]], [48, [0.70, 0.66, 0.62]], [66, [0.95, 0.95, 0.96]]], paletteSoft: 5 },
  features: [
    { type: 'undulate', amp: 4, scale: 90 },
    { type: 'ridge', path: [[-60, -250], [-40, -190], [-70, -130], [-60, -70]], w: 22, h: 14, rough: 0.3 },
    { type: 'sea', poly: [[-420, -300], [420, -300], [420, 300], [-420, 300]], shelf: 34, depth: 8 },
    // England (the north and the west run off the edge), then France
    { type: 'land', wob: 2.4, shelf: 16, poly: [[-420, -300], [190, -300], [190, -260], [210, -215], [196, -170], [230, -150], [250, -130], [300, -98], [312, -62], [276, -46], [302, -20], [296, 14], [262, 28], [215, 40], [160, 48], [100, 54], [40, 62], [-20, 72], [-90, 84], [-160, 82], [-220, 96], [-300, 112], [-340, 96], [-420, 86]] },
    { type: 'land', wob: 2.4, shelf: 16, poly: [[-420, 300], [-420, 190], [-330, 172], [-260, 150], [-200, 168], [-150, 160], [-110, 128], [-70, 120], [-50, 150], [0, 165], [60, 170], [110, 172], [150, 168], [200, 150], [250, 140], [290, 125], [330, 112], [420, 100], [420, 300]] },
    { type: 'river', name: 'Thames', path: [[130, -70], [190, -52], [250, -48], [285, -50]], w: 5, depth: 1.6, meander: 4, wl: 3 },
    { type: 'woods', at: [-120, -150], r: [50, 18], rot: 10 }, { type: 'woods', at: [60, -100], r: [26, 14], rot: -20 }, { type: 'woods', at: [-20, 10], r: [40, 14], rot: 8 }, { type: 'woods', at: [220, -110], r: [20, 18] },
    { type: 'woods', at: [-200, 200], r: [40, 14] }, { type: 'woods', at: [120, 215], r: [60, 18], rot: 4 }, { type: 'woods', at: [196, 6], r: [20, 12], rot: 20 },
    { type: 'farms', rect: [20, -150, 120, 40, 8], cell: [14, 10] }, { type: 'farms', rect: [-140, -20, 130, 40, -4], cell: [15, 10] }, { type: 'farms', rect: [10, 225, 200, 40, 0], cell: [16, 11] },
    { type: 'road', path: [[178, 20], [172, 4], [150, -30], [138, -58], [128, -92], [112, -128], [92, -160], [70, -196]], w: 2.0, meander: 3 },
  ],
};

// ------------------------------------------------------------------ the battlefield: Senlac hill, the ridge, the gentle south slope
const W_ALL = ['w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7'], B_ALL = ['b0', 'b1', 'b2', 'b3', 'b4', 'b5'];
const FOOT = ['f0', 'f1', 'f2'], KN = ['kL', 'kR'], NORM = [...FOOT, ...KN];
const bat = {
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
      { type: 'woods', at: [-70, 215], r: [60, 18] }, { type: 'woods', at: [150, 222], r: [50, 16] },
      { type: 'farms', rect: [-40, 205, 160, 40, 0], cell: [16, 11] }, { type: 'farms', rect: [-140, 150, 70, 40, 6], cell: [14, 10] },
      { type: 'road', path: [[8, 250], [-4, 160], [4, 60], [-2, -50], [6, -140], [0, -250]], w: 2.2, meander: 3 },
      { type: 'flat', at: [110, 196], r: 34, amount: 0.8 }, { type: 'flat', at: [50, -150], r: 22, amount: 0.7 },
    ],
  },
  ambient: {
    wind: [1.1, 0.4], gusts: 0.6, flow: { dir: [1, 0.1], speed: 0.5, glint: 1.0 },
    camps: [{ pos: [110, 196], size: [56, 34], team: 'rome', style: 'grid', fires: 3, people: 14, rot: -4 },
      { pos: [50, -150], size: [34, 24], team: 'carthage', style: 'scatter', tents: 14, fires: 2, people: 8, palisade: false, rot: 10 }],
    walkers: [{ path: [[0, -250], [6, -140], [2, -100]], n: 4, gap: 5, speed: 1.2, kind: 'light', team: 'neutral' },
      { path: [[8, 250], [-4, 160], [0, 150]], n: 3, gap: 5, speed: 1.0, kind: 'light', team: 'neutral', offset: 20, until: 'l07' }],
    smoke: [{ pos: [0, -40], n: 12, alpha: 0.18, height: 10, at: 'l08.arrows', until: 'l15' }, { pos: [-40, 60], n: 8, alpha: 0.14, height: 8, at: 'l12.chased' },
      { pos: [-10, -60], n: 12, alpha: 0.2, height: 12, at: 'l14' }],
    birds: [{ center: [-110, -190], r: 44, h: 26, n: 7, speed: 6 }, { path: [[-320, 80], [320, -40]], n: 5, h: 38, speed: 8 }, { center: [150, -200], r: 36, h: 24, n: 5, speed: 5, dir: -1 }],
  },
  blocks: {
    // the English: a wall of eight blocks along the crest, a second line behind, King Harold behind them (there from the cold open)
    ...Object.fromEntries([0, 1, 2, 3, 4, 5, 6, 7].map((i) => ['w' + i, { ...ENG, kind: 'infantry', x: -63 + 18 * i, z: -46, heading: 180, len: 17.0, dep: 11, banner: i % 2 === 1 }])),
    ...Object.fromEntries([0, 1, 2, 3, 4, 5].map((i) => ['b' + i, { ...ENG, kind: 'infantry', x: -45 + 18 * i, z: -61, heading: 180, len: 17.0, dep: 13, banner: false }])),
    harold: { ...ENG, kind: 'elite', x: 0, z: -80, heading: 180, len: 14, dep: 10, bannerScale: 2.0 },
    // the Normans: archers in front (skirmishers: they walk through their own lines), foot soldiers in the centre, knights on the wings, William behind
    arch: { ...NOR, kind: 'archers', x: 0, z: 96, heading: 0, len: 120, dep: 7, grid: { cols: 3, ranks: 1, gap: 4 }, hidden: true, banner: false, solid: false },
    f0: { ...NOR, kind: 'infantry', x: -32, z: 114, heading: 0, len: 28, dep: 16, hidden: true },
    f1: { ...NOR, kind: 'infantry', x: 0, z: 114, heading: 0, len: 28, dep: 16, hidden: true, banner: false },
    f2: { ...NOR, kind: 'infantry', x: 32, z: 114, heading: 0, len: 28, dep: 16, hidden: true },
    kL: { ...NOR, kind: 'cavalry', x: -70, z: 114, heading: 0, len: 28, dep: 14, hidden: true },
    kR: { ...NOR, kind: 'cavalry', x: 70, z: 114, heading: 0, len: 28, dep: 14, hidden: true },
    wm: { ...NOR, kind: 'elite', x: 0, z: 142, heading: 0, len: 12, dep: 8, bannerScale: 2.0, hidden: true, solid: false },
  },
  moves: [],
  arrows: [], labels: [], icons: [], volleys: [], counters: [],
  markers: [],
};
const mv = (o) => bat.moves.push(o);
// S4: the shields lock (the files close the gaps); William's army forms at the bottom, each arm on its word
mv({ blocks: W_ALL, at: 'l06.locked', dur: 1.2, to: { len: 18 }, ease: 'inOut' });
mv({ block: 'wm', at: 'l07.Williams', dur: 0.9, appear: true });
mv({ group: 'arch', at: 'l07.archers,', dur: 0.8, stagger: 0.2, appear: true });
mv({ blocks: FOOT, at: 'l07.foot', dur: 0.8, stagger: 0.2, appear: true });
mv({ blocks: KN, at: 'l07.knights', dur: 0.8, stagger: 0.25, appear: true });
// S5: the attack. Archers walk up and shoot; the foot climb into the wall; the knights ride uphill into the axes; all fall back; again
mv({ group: 'arch', at: 'l08.Normans', dur: 2.6, to: { z: 30 }, ease: 'cam' });
mv({ blocks: FOOT, at: 'l08.attacked,', dur: 4.2, to: { z: -26 }, ease: 'cam' });
mv({ blocks: KN, at: 'l08.attacked,', dur: 3.2, to: { z: 56 }, ease: 'cam' });
mv({ block: 'wm', at: 'l08.attacked,', dur: 3.6, to: { z: 112 }, ease: 'cam' });
mv({ blocks: KN, at: 'l08.knights', dur: 2.0, to: { z: -30 }, ease: 'inQuad' });
mv({ blocks: FOOT, at: 'l08.held,', dur: 1.8, to: { z: 18 }, ease: 'out' });
mv({ blocks: KN, at: 'l08.held,', dur: 1.8, to: { z: 30 }, ease: 'out' });
mv({ group: 'arch', at: 'l08.held,', dur: 1.8, to: { z: 46 }, ease: 'out' });
mv({ blocks: FOOT, at: 'l08.hour', dur: 2.2, to: { z: -26 }, ease: 'cam' });
mv({ blocks: KN, at: 'l08.hour', dur: 2.2, to: { z: 4 }, ease: 'cam' });
// S5: the rumour. The lines stop; then they turn and run (past William, who stays)
mv({ blocks: [...NORM], at: 'l09.soldier', dur: 0.5, to: { heading: 180 } }); mv({ group: 'arch', at: 'l09.soldier', dur: 0.5, to: { heading: 180 } });
mv({ blocks: FOOT, at: 'l09.soldier+0.3', dur: 2.4, to: { z: 146 }, ease: 'inQuad' });
mv({ blocks: KN, at: 'l09.soldier+0.3', dur: 2.2, to: { z: 150 }, ease: 'inQuad' });
mv({ group: 'arch', at: 'l09.soldier+0.3', dur: 2.4, to: { z: 160 }, ease: 'inQuad' });
// S5: William turns to face his runners, then they all turn and climb again
mv({ block: 'wm', at: 'l10.William', dur: 1.2, to: { heading: 180, z: 124 }, ease: 'cam' });
mv({ blocks: [...NORM, 'wm'], at: 'l10.turned', dur: 0.6, to: { heading: 0 } }); mv({ group: 'arch', at: 'l10.turned', dur: 0.6, to: { heading: 0 } });
mv({ blocks: FOOT, at: 'l10.turned+0.4', dur: 3.2, to: { z: 70 }, ease: 'cam' });
mv({ blocks: KN, at: 'l10.turned+0.4', dur: 3.2, to: { z: 80 }, ease: 'cam' });
mv({ group: 'arch', at: 'l10.turned+0.4', dur: 3.2, to: { z: 96 }, ease: 'cam' });
mv({ block: 'wm', at: 'l10.turned+0.4', dur: 3.2, to: { z: 118 }, ease: 'cam' });
// S6: the trick. They pretend to run away (foot and knights turn and go back down)
mv({ blocks: NORM, at: 'l11.pretend', dur: 0.5, to: { heading: 180 } });
mv({ blocks: FOOT, at: 'l11.pretend+0.2', dur: 2.6, to: { z: 120 }, ease: 'cam' });
mv({ blocks: KN, at: 'l11.pretend+0.2', dur: 2.6, to: { z: 112 }, ease: 'cam' });
// the first chase: w1 and w2 run down the hill and leave a gap in the wall
mv({ blocks: ['w1', 'w2'], at: 'l12.chased', dur: 3.0, by: { z: 108 }, ease: 'cam' });
// the knights wheel in from both sides; the foot turn and close the south side
mv({ block: 'kL', at: 'l12.the#4', dur: 2.2, path: [[-74, 96], [-74, 74], [-64, 62]], ease: 'cam' });
mv({ block: 'kR', at: 'l12.the#4', dur: 2.2, path: [[50, 100], [20, 80], [-8, 62]], ease: 'cam' });
mv({ blocks: ['kL'], at: 'l12.the#4+2.2', dur: 0.5, to: { heading: 90 } }); mv({ blocks: ['kR'], at: 'l12.the#4+2.2', dur: 0.5, to: { heading: 270 } });
mv({ blocks: FOOT, at: 'l12.Knights', dur: 0.5, to: { heading: 0 } });
mv({ block: 'f0', at: 'l12.Knights+0.3', dur: 1.8, to: { z: 78 }, ease: 'cam' });
mv({ blocks: ['w1', 'w2'], at: 'l12.surrounded', dur: 1.6, stagger: 0.2, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 });
// S6: again on the other side (w5 and w6); then the cut-off chasers are gone and the wall closes up, thinner
mv({ blocks: ['w1', 'w2'], at: 'l13.They', dur: 1.0, vanish: true });
mv({ block: 'kL', at: 'l13.They', dur: 1.6, path: [[-50, 80], [-10, 92], [8, 96]], ease: 'cam' });
mv({ block: 'kR', at: 'l13.They', dur: 1.6, path: [[20, 84], [60, 94], [76, 96]], ease: 'cam' });
mv({ block: 'f0', at: 'l13.They', dur: 1.6, to: { z: 120 }, ease: 'cam' });
mv({ blocks: ['w5', 'w6'], at: 'l13.once,', dur: 2.2, by: { z: 108 }, ease: 'cam' });
mv({ block: 'kL', at: 'l13.every', dur: 1.4, path: [[10, 80], [8, 62]], ease: 'cam' }); mv({ block: 'kL', at: 'l13.every+1.4', dur: 0.4, to: { heading: 90 } });
mv({ block: 'kR', at: 'l13.every', dur: 1.4, path: [[74, 80], [64, 62]], ease: 'cam' }); mv({ block: 'kR', at: 'l13.every+1.4', dur: 0.4, to: { heading: 270 } });
mv({ block: 'f2', at: 'l13.every', dur: 1.6, to: { z: 78 }, ease: 'cam' });
mv({ blocks: ['w5', 'w6'], at: 'l13.chase,+0.6', dur: 1.4, stagger: 0.2, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 });
mv({ blocks: ['w0', 'w3', 'w4', 'w7', ...B_ALL], at: 'l13.the', dur: 1.6, squeeze: { about: [0, -50], kx: 0.62, kz: 1 }, ease: 'inOut' });
mv({ blocks: ['w0', 'w3', 'w4', 'w7', ...B_ALL], at: 'l13.the', dur: 1.6, fadeTo: 0.35, alphaTo: 0.9 });
// S7: late in the day the last push; Harold falls (his standard sinks; numbers, never wounds)
mv({ blocks: ['w5', 'w6'], at: 'l14', dur: 0.8, vanish: true });
mv({ block: 'kL', at: 'l14+0.2', dur: 3.2, path: [[-40, 40], [-36, -24]], ease: 'cam' });
mv({ block: 'kR', at: 'l14+0.2', dur: 3.2, path: [[40, 40], [36, -24]], ease: 'cam' });
mv({ blocks: FOOT, at: 'l14', dur: 3.0, to: { z: -22 }, ease: 'cam' });
mv({ group: 'arch', at: 'l14', dur: 2.4, to: { z: 30 }, ease: 'cam' });
mv({ block: 'wm', at: 'l14', dur: 3.0, to: { z: 70 }, ease: 'cam' });
mv({ block: 'harold', at: 'l14.killed.', dur: 1.6, fadeTo: 1, alphaTo: 0.5, sinkTo: 1 });
// S7: without their king, the English break and scatter north; the Normans take the crest
[...['w0', 'w3', 'w4', 'w7'], ...B_ALL].forEach((id, i) => { const dir = i % 2 ? 1 : -1;
  mv({ block: id, at: { line: 'l15', word: 'broke', offset: 0.08 * (i % 5) }, dur: 2.4, by: { x: dir * (10 + (i % 4) * 7), z: -40 - (i % 3) * 10 }, ease: 'inQuad' });
  mv({ block: id, at: { line: 'l15', word: 'broke', offset: 0.4 + 0.08 * (i % 5) }, dur: 2.0, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 }); });
mv({ blocks: ['harold'], at: 'l15.broke', dur: 1.0, vanish: true });
mv({ blocks: FOOT, at: 'l15.broke+0.5', dur: 3.0, to: { z: -50 }, ease: 'cam' });
mv({ blocks: KN, at: 'l15.broke+0.5', dur: 3.0, by: { z: -26 }, ease: 'cam' });

bat.arrows = [
  { at: 'l07.Go', until: 'l07.hill.>', ease: 'out', team: 'rome', width: 6, path: [[0, 92], [0, 0], [0, -30]], lift: 6, hide: 'l08.attacked,' },
  { at: 'l08.knights', dur: 1.0, ease: 'out', team: 'rome', width: 4.5, path: [[-70, 60], [-70, -26]], lift: 6, hide: 'l08.held,' },
  { at: 'l08.knights', dur: 1.0, ease: 'out', team: 'rome', width: 4.5, path: [[70, 60], [70, -26]], lift: 6, hide: 'l08.held,' },
  { at: 'l09.soldier+0.3', dur: 1.2, ease: 'out', team: 'rome', style: 'dash', width: 4.5, path: [[0, -6], [0, 112]], lift: 6, hide: 'l10.William' },
  { at: 'l10.turned', dur: 1.2, ease: 'out', team: 'rome', width: 5, path: [[0, 140], [0, 84]], lift: 6, hide: 'l11' },
  { at: 'l11.pretend', dur: 1.4, ease: 'out', team: 'rome', style: 'dash', width: 4, path: [[-32, 70], [-32, 118]], lift: 6, hide: 'l12.chased' },
  { at: 'l11.pretend', dur: 1.4, ease: 'out', team: 'rome', style: 'dash', width: 4, path: [[32, 70], [32, 118]], lift: 6, hide: 'l12.chased' },
  { at: 'l12.chased', dur: 1.6, ease: 'out', team: 'carthage', width: 4.5, path: [[-36, -32], [-36, 52]], lift: 6, hide: 'l12.Knights' },
  { at: 'l12.the#4', dur: 1.6, ease: 'cam', team: 'rome', width: 3.6, path: [[-74, 100], [-74, 74], [-66, 62]], lift: 6, hide: 'l13' },
  { at: 'l12.the#4', dur: 1.6, ease: 'cam', team: 'rome', width: 3.6, path: [[50, 100], [20, 80], [-6, 62]], lift: 6, hide: 'l13' },
  { at: 'l12.surrounded', dur: 1.2, ease: 'inOut', team: 'gold', width: 1.4, style: 'dash', head: false, taper: 1, smooth: true, lift: 6, hide: 'l13',
    path: [[-80, 44], [-36, 38], [8, 44], [12, 66], [-6, 90], [-36, 94], [-70, 88], [-84, 66], [-80, 44]] },
  { at: 'l13.once,', dur: 1.4, ease: 'out', team: 'carthage', width: 4.5, path: [[36, -32], [36, 52]], lift: 6, hide: 'l13.the' },
  { at: 'l13.every', dur: 1.0, ease: 'inOut', team: 'gold', width: 1.4, style: 'dash', head: false, taper: 1, smooth: true, lift: 6, hide: 'l14',
    path: [[-4, 44], [36, 38], [80, 44], [84, 66], [70, 88], [36, 94], [6, 90], [-8, 66], [-4, 44]] },
  { at: 'l15.broke+0.5', dur: 1.6, ease: 'out', team: 'rome', width: 6, path: [[0, 10], [0, -90]], lift: 6, hide: 'l16' },
];
bat.volleys = [
  { at: 'l08.arrows', dur: 1.2, from: [0, 30, 50], to: [0, -46, 60], n: 40, flight: 0.95, spread: 0.35, team: 'rome' },
  { at: 'l08.shields,', dur: 1.2, from: [0, 30, 50], to: [0, -46, 60], n: 34, flight: 0.95, spread: 0.35, team: 'rome' },
  { at: 'l14.Late', dur: 1.4, from: [0, 30, 50], to: [0, -60, 50], n: 40, flight: 1.1, spread: 0.4, team: 'rome' },
];
bat.labels = [
  { at: 5.0, until: 8.6, text: '1066', screen: [0.5, 0.16], big: true },
  { at: 'l06.14th', until: "l06.Harold's", text: '14 OCTOBER 1066', screen: [0.5, 0.86], big: true },
  { at: "l06.Harold's", until: 'l06.shoulder', text: 'HAROLD', block: 'harold', team: 'carthage', dx: 0.08, dy: -0.12 },
  { at: 'l06.wall.', until: 'l07', text: 'THE SHIELD WALL', block: 'w4', team: 'carthage', dx: 0.04, dy: -0.16 },
  { at: 'l07.Williams', until: 'l07.archers,', text: 'WILLIAM', block: 'wm', team: 'rome', dx: 0.06, dy: -0.1 },
  { at: 'l10.William', until: 'l10.and', text: 'WILLIAM', block: 'wm', team: 'rome', dx: 0.1, dy: -0.14 },
  { at: 'l11.pretend', until: 'l12', text: 'FEIGNED FLIGHT', block: 'f1', team: 'rome', dx: 0.1, dy: -0.12 },
  { at: 'l14.King', until: 'l14.A', text: 'KING HAROLD', block: 'harold', team: 'carthage', dx: 0.1, dy: -0.14 },
  { at: 'l14.Bayou', until: 'l14.Historians', text: 'BAYEUX TAPESTRY, 1070s', screen: [0.5, 0.86], big: true },
];

// ------------------------------------------------------------------ the film (main stage = England, the Channel and Normandy)
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.30 }, edgeStart: 1500, edgeEnd: 2600, fogDensity: 0.0009 },
  world: england,
  stages: { bat },
  ambient: {
    wind: [1, 0.3], gusts: 0.4, flow: { dir: [1, 0.15], speed: 0.6, glint: 1.2 },
    camps: [{ pos: [112, 186], size: [40, 22], team: 'rome', style: 'scatter', tents: 16, fires: 2, people: 10, palisade: false }],
    walkers: [{ path: [[150, -30], [138, -58], [128, -92], [112, -128], [92, -160], [70, -196]], n: 5, gap: 6, speed: 1.6, kind: 'light', team: 'neutral' }],
    smoke: [{ pos: [152, -52], n: 8, alpha: 0.14, height: 7 }],
    birds: [{ center: [60, 115], r: 40, h: 22, n: 6, speed: 6 }, { center: [260, -200], r: 36, h: 22, n: 5, speed: 5, dir: -1 }, { path: [[-200, 130], [300, 90]], n: 5, h: 30, speed: 8 }],
  },

  blocks: {
    harold: { ...ENG, kind: 'infantry', x: 150, z: -48, heading: 0, len: 30, dep: 14, figScale: 1.4, bannerScale: 1.6, hidden: true },
    willN: { ...NOR, kind: 'infantry', x: 66, z: 196, heading: 0, len: 30, dep: 14, figScale: 1.4, bannerScale: 1.6, hidden: true },
    willE: { ...NOR, kind: 'infantry', x: 154, z: 32, heading: 0, len: 30, dep: 14, figScale: 1.4, bannerScale: 1.6, hidden: true },
    vik: { ...VIK, kind: 'infantry', x: 142, z: -196, heading: 270, len: 30, dep: 14, figScale: 1.4, bannerScale: 1.6, hidden: true },
  },

  moves: [
    // S2: Harold is crowned in London; William rises in Normandy
    { block: 'harold', at: 'l02.crowned', dur: 0.9, appear: true },
    { block: 'willN', at: 'l03.duke', dur: 0.9, appear: true },
    // S3: the Norwegians land in the north; Harold marches up the road and beats them; the ranks thin
    { block: 'vik', at: 'l04.invaded', dur: 1.0, appear: true },
    { block: 'harold', at: 'l04.marched', dur: 2.4, path: [[132, -84], [112, -128], [100, -168]], ease: 'cam' },
    { block: 'vik', at: 'l04.beat', dur: 1.6, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 },
    { block: 'vik', at: 'l05', dur: 0.6, vanish: true },
    // S3: William crosses and lands; Harold's long march back down
    { block: 'willN', at: 'l05.William', dur: 0.6, vanish: true },
    { block: 'willE', at: 'l05.landed', dur: 0.9, appear: true },
    { block: 'harold', at: 'l05.marched', dur: 4.6, path: [[112, -128], [132, -84], [150, -40], [172, -10], [178, -4]], ease: 'camLong' },
    { block: 'harold', at: 'l06', dur: 0.5, vanish: true },
    // S8: Christmas Day: William marches to London
    { block: 'willE', at: 'l16.Christmas', dur: 2.6, path: [[170, 4], [158, -26], [150, -44]], ease: 'cam' },
  ],

  // ------------------------------------------------------------------ scenes: sets and pre-planned cameras (the edit)
  scenes: [
    { id: 'S1', name: 'The hill at dawn', at: 0, stage: 'bat', inset: 'full', job: '1066: three kings in one year; the last one is decided here, on this hill', set: { time: [0.4, 0.3], haze: 1.6, cloud: 0.3 },
      shots: [
        { at: 0, why: 'cold open low over the slope at dawn: an army waits on the crest; the stakes before the story', from: { target: [0, -36], dist: 150, pitch: 11, yaw: 4, mm: 30 },
          moves: [{ until: 'l00.year.>', to: { target: [0, -44], dist: 124, pitch: 12, yaw: 10 } }] },
        { at: 'l00.This', why: 'crane up from the slope to the whole field: this is the battle, seen as the map we will read (under the title)', from: { target: [0, -10], width: 420, pitch: 30, yaw: 346, mm: 35 },
          moves: [{ until: 17.2, to: { target: [0, 0], width: 520, pitch: 74, yaw: 360 }, ease: 'camLong' }] },
      ] },
    { id: 'S2', name: 'The crown', at: 'l02', transition: { type: 'dissolve', dur: 0.8 }, job: 'who claims the crown: Harold in England, William across the sea', set: { time: 0.1, haze: 1.0, cloud: 0.3 },
      shots: [
        { at: 'l02', why: 'change of world: the map of England, London, where the old king dies and Harold is crowned', from: { target: [150, -58], width: 330, pitch: 56, yaw: 0, mm: 35 },
          moves: [{ until: 'l02.Harold.>', to: { target: [152, -54], width: 290 } }] },
        { at: 'l03', why: 'across the sea, change of place: Normandy and its duke; hold for his "excuse me"', from: { target: [96, 150], width: 430, pitch: 52, yaw: 0, mm: 35 },
          moves: [{ until: 'l03.William>', to: { target: [80, 168], width: 370 } }] },
        { at: 'l03.built', why: 'low on the Normandy shore looking north: the fleet, and the England it is built for', from: { target: [180, 120], dist: 170, pitch: 16, yaw: 352, mm: 35 },
          moves: [{ until: 'l04', to: { dist: 156 } }] },
      ] },
    { id: 'S3', name: 'Two invasions', at: 'l04', job: 'Harold beats the Norwegians in the north, then William lands in the south; the long march back', set: { time: 0.08, haze: 1.0, cloud: 0.3 },
      shots: [
        { at: 'l04', why: 'change of place: the north, where the Norwegian galleys sail in', from: { target: [190, -176], width: 430, pitch: 56, yaw: 0, mm: 35 },
          moves: [{ until: 'l04.north.>', to: { target: [168, -182], width: 390 } }] },
        { at: 'l04.Harold#1', why: 'wider and higher: follow Harold up the road to Stamford Bridge', from: { target: [146, -112], width: 480, pitch: 78, yaw: 6, mm: 35 },
          moves: [{ until: 'l04.Bridge.>', to: { target: [128, -140], width: 470 } }] },
        { at: 'l05', why: 'three days later, change of place: the south coast, William crosses and lands', from: { target: [166, 92], width: 400, pitch: 56, yaw: 0, mm: 35 },
          moves: [{ until: 'l05.south,>', to: { target: [162, 70], width: 380 } }] },
        { at: 'l05.so', why: 'pull out to the whole length of England: the march back, in miles; hold on "Busy month."', from: { target: [134, -72], width: 600, pitch: 74, yaw: 0, mm: 35 },
          moves: [{ until: 'l05.miles,>', to: { target: [136, -66], width: 620 } }] },
      ] },
    { id: 'S4', name: 'The hill', at: 'l06', stage: 'bat', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'the field: the English on top in a shield wall, the Normans below with a hard job', set: { time: 0.1, haze: 1.15, cloud: 0.25 },
      shots: [
        { at: 'l06', why: 'back on the field, establish it: the ridge, the marsh, the English on the crest', from: { target: [0, -6], width: 520, pitch: 36, yaw: 330, mm: 35 },
          moves: [{ until: 'l06.hill,>', to: { target: [0, -30], width: 440, yaw: 338 } }] },
        { at: 'l06.shoulder', why: 'low along the wall from its west end: shoulder to shoulder, the shields lock', from: { target: [-40, -44], dist: 80, pitch: 13, yaw: 66, mm: 40 },
          moves: [{ until: 'l06.wall.>', to: { target: [-18, -46], dist: 75 } }] },
        { at: 'l07', why: 'reverse angle from behind the English, above: William\'s army forms at the bottom', from: { target: [0, 70], dist: 236, pitch: 30, yaw: 180, mm: 35 },
          moves: [{ until: 'l07.horseback.>', to: { target: [0, 84], dist: 206 } }] },
        { at: 'l07.Their', why: 'low behind the Normans looking up the slope: their job; hold on "Not fun."', from: { target: [0, -14], dist: 176, pitch: 14, yaw: 6, mm: 35 },
          moves: [{ until: 'l07.hill.>', to: { dist: 164 } }] },
      ] },
    { id: 'S5', name: 'The wall holds', at: 'l08', job: 'the attack fails against the wall; a rumour, a panic, a rally', set: { time: [0.1, 0.25], haze: 1.15 },
      shots: [
        { at: 'l08', why: 'high from the west flank: arrows and foot soldiers against the wall', from: { target: [0, 14], dist: 262, pitch: 38, yaw: 74, mm: 35 },
          moves: [{ until: 'l08.shields,>', to: { target: [0, -4], dist: 236 } }] },
        { at: 'l08.knights', why: 'low behind the knights: riding uphill into swinging axes', from: { target: [-68, -10], dist: 104, pitch: 14, yaw: 10, mm: 35 },
          moves: [{ until: 'l08.axes,>', to: { dist: 94 } }] },
        { at: 'l08.and', why: 'high, near top down: the Normans fall back, the blue line has not moved; hour after hour', from: { target: [0, 6], width: 380, pitch: 80, yaw: 0, mm: 35 },
          moves: [{ until: 'l09', to: { width: 410 }, ease: 'camLong' }] },
        { at: 'l09', why: 'oblique on the Norman lines: the rumour, then the run (pull back with them)', from: { target: [10, 30], dist: 196, pitch: 28, yaw: 322, mm: 35 },
          moves: [{ at: 'l09.soldier', until: 'l10', to: { target: [10, 76], dist: 222 } }] },
        { at: 'l10', why: 'low and close on William: he turns to face the runners', from: { target: [0, 126], dist: 62, pitch: 12, yaw: 178, mm: 40 },
          moves: [{ until: 'l10.alive,>', to: { dist: 54 } }] },
        { at: 'l10.and', why: 'wide: the whole army turns and climbs again', from: { target: [0, 70], width: 430, pitch: 56, yaw: 20, mm: 35 },
          moves: [{ until: 'l11', to: { width: 410 } }] },
      ] },
    { id: 'S6', name: 'The trick', at: 'l11', job: 'the feigned flight pulls the English off the hill; again; the wall thins', set: { time: [0.25, 0.4], haze: 1.15 },
      shots: [
        { at: 'l11', why: 'from behind the English wall: what the English see, the Normans running away', from: { target: [0, 52], dist: 214, pitch: 34, yaw: 194, mm: 35 },
          moves: [{ at: 'l11.pretend', until: 'l12', to: { target: [0, 66], dist: 230 } }] },
        { at: 'l12', why: 'the decisive moment wide, from above: the chase, and the gap it leaves in the wall', from: { target: [-12, 26], width: 400, pitch: 84, yaw: 0, mm: 35 },
          moves: [{ until: 'l12.wall,>', to: { target: [-20, 32], width: 380 } }] },
        { at: 'l12.the#4', why: 'closer and lower on the same place: how it worked, the knights close the ring', from: { target: [-36, 64], dist: 118, pitch: 24, yaw: 312, mm: 35 },
          moves: [{ until: 'l12.them.>', to: { yaw: 326, dist: 106 }, ease: 'camSoft' }] },
        { at: 'l13', why: 'wide again from the east: it happens more than once, on the other side', from: { target: [24, 12], width: 450, pitch: 56, yaw: 282, mm: 35 },
          moves: [{ until: 'l13.chase,>', to: { target: [30, 28], width: 430 } }] },
        { at: 'l13.chase,>', why: 'low along the crest: what is left of the wall closes up, thinner', from: { target: [16, -48], dist: 92, pitch: 14, yaw: 262, mm: 35 },
          moves: [{ until: 'l14', to: { dist: 86 } }] },
      ] },
    { id: 'S7', name: 'The king falls', at: 'l14', climax: true, job: 'Harold falls and the English army breaks', set: { time: [0.6, 1.0], haze: [1.2, 1.35] },
      shots: [
        { at: 'l14', why: 'low behind the last Norman push toward Harold\'s standard in the evening light', from: { target: [0, -60], dist: 124, pitch: 12, yaw: 352, mm: 35 },
          moves: [{ until: 'l14.A', to: { target: [0, -68], dist: 110 } }] },
        { at: 'l14.A', why: 'slow orbit over the fallen standard: the hold carries the tapestry and the historians', from: { target: [0, -72], dist: 112, pitch: 26, yaw: 36, mm: 35 },
          moves: [{ until: 'l14.eye.>', to: { yaw: 76, dist: 122 }, ease: 'camLong' }, { at: 'l14.Historians', until: 'l14.questions.>', by: { yaw: 14, zoom: 1.05 }, ease: 'camLong' }] },
        { at: 'l15', why: 'cut on "Without": high from the north, the English scatter and the Normans take the crest', from: { target: [0, -60], width: 440, pitch: 50, yaw: 180, mm: 35 },
          moves: [{ until: 'l15.apart.>', to: { target: [0, -70], width: 470 } }] },
      ] },
    { id: 'S8', name: 'The Conqueror', at: 'l16', transition: { type: 'dissolve', dur: 1.0 }, job: 'William is king; a French-speaking king changed English', set: { time: [0.2, 0.35], haze: 1.05 },
      shots: [
        { at: 'l16', why: 'change of world, back to the map: William marches to London and is crowned', from: { target: [160, -16], width: 330, pitch: 52, yaw: 0, mm: 35 },
          moves: [{ until: 'l16.England.>', to: { target: [154, -38], width: 296 } }] },
        { at: 'l17', why: 'wide over the Channel: the French words cross with the Normans', from: { target: [100, 90], width: 520, pitch: 46, yaw: 0, mm: 35 },
          moves: [{ until: 'l17.judge.>', to: { target: [100, 70], width: 500 } }] },
        { at: 'l17.All', why: 'pull back and up to the whole map: one afternoon on a hill, and where it was', from: { target: [130, 0], width: 600, pitch: 64, yaw: 0, mm: 35 },
          moves: [{ until: 155.0, to: { width: 700, pitch: 78 }, ease: 'camLong' }] },
      ] },
  ],

  // ------------------------------------------------------------------ the legend (motion-graphics frame)
  legend: {
    title: { text: 'THE BATTLE OF HASTINGS', sub: '14 October 1066', at: 'l02' },
    show: [['l02', 'l17.hill.>']],
    sides: [
      { id: 'england', team: 'carthage', name: 'ENGLAND', commander: 'King Harold', commanderAt: 'l02.Harold.', banner: 'banner', at: 'l02.English', strength: 7000, strengthAt: "l06.Harold's", strengthLabel: 'MEN, ESTIMATED', dimAt: 'l15.broke' },
      { id: 'normandy', team: 'rome', name: 'NORMANDY', commander: 'Duke William', commanderAt: 'l03.William', banner: 'banner', at: 'l03.Normandy,', strength: 7000, strengthAt: 'l07.Williams', strengthLabel: 'MEN, ESTIMATED' },
      { id: 'norway', team: 'gold', name: 'NORWAY', commander: 'Harald Hardrada', commanderAt: 'l04.Harold', banner: 'banner', at: 'l04.Viking', dimAt: 'l04.beat' },
    ],
    key: { show: [['l03.sea', 'l05>'], ['l06', 'l14'], ['l16', 'l17.hill.>']] },
    units: [
      { id: 'foot', kind: 'infantry', name: 'Foot soldiers', teams: ['carthage', 'rome'], at: 'l07.foot' },
      { id: 'arch', kind: 'archers', name: 'Archers', team: 'rome', at: 'l07.archers,' },
      { id: 'kn', kind: 'cavalry', name: 'Knights', team: 'rome', at: 'l07.knights' },
    ],
    places: [
      { id: 'channel', letter: 'A', glyph: 'sea', name: 'The Channel', at: 'l03.sea', pos: [40, 114], label: false, markerSize: 0.05 },
      { id: 'stamford', letter: 'B', glyph: 'bridge', name: 'Stamford Bridge', at: 'l04.Stamford', pos: [112, -176], label: 'STAMFORD BRIDGE', team: 'carthage', ldy: -0.05 },
      { id: 'senlac', letter: 'C', glyph: 'hill', name: 'Senlac Hill', at: 'l06.hill,', pos: [-120, -60], y: 8, stage: 'bat', label: 'SENLAC HILL', ldy: -0.05 },
    ],
    focus: [
      { entry: 'arch', at: 'l08.arrows', until: 'l08.knights' }, { entry: 'kn', at: 'l08.knights', until: 'l08.and' },
      { entry: 'kn', at: 'l12.Knights', until: 'l13' }, { entry: 'england', at: 'l14.King', until: 'l14.A' },
      { entry: 'normandy', at: 'l16.William#1', until: 'l17' },
    ],
    scale: { unitM: 2000, show: [['l04', 'l05>']] },
  },

  labels: [
    { at: 'l02.Old', until: 'l02.The#1', text: 'EDWARD THE CONFESSOR', pos: [152, -54], y: 4, dx: -0.1, dy: -0.12 },
    { at: 'l02.crowned', until: 'l03', text: 'LONDON', pos: [152, -54], y: 2, dx: 0.12, dy: 0.08 },
    { at: 'l05.landed', until: 'l05.so', text: 'PEVENSEY', pos: [150, 46], y: 2, team: 'rome', dx: -0.12, dy: -0.08 },
    { at: 'l16.Christmas', until: 'l16.William', text: 'CHRISTMAS DAY 1066', screen: [0.5, 0.86], big: true },
    { at: 'l16.crowned', until: 'l16>', text: 'WESTMINSTER ABBEY', pos: [146, -52], y: 4, team: 'rome', dx: -0.12, dy: -0.12 },
    { follow: 'beef', at: 'l17.beef,', until: 'l17.All', text: 'BUEF', dy: -0.06, team: 'rome', leader: false },
    { follow: 'jury', at: 'l17.jury,', until: 'l17.All', text: 'JUREE', dy: -0.06, team: 'rome', leader: false },
    { follow: 'judge', at: 'l17.judge.', until: 'l17.All', text: 'JUGE', dy: -0.06, team: 'rome', leader: false },
  ],

  counters: [
    { at: 'l05.marched', until: 'l05.busy', block: 'harold', team: 'carthage', from: 0, to: 250, countDur: 4.0, step: 5, suffix: 'MILES', dx: 0.1, dy: -0.12 },
  ],

  icons: [
    // the fleet gathers on the Normandy shore (who crosses the sea, and when)
    { at: 'l03.fleet', until: 'l05.William', icon: 'galley', team: 'rome', pos: [150, 156], size: 18, minPx: 0.045, maxPx: 0.065 },
    { at: 'l03.fleet+0.2', until: 'l05.William', icon: 'galley', team: 'rome', pos: [190, 146], size: 18, minPx: 0.045, maxPx: 0.065 },
    { at: 'l03.fleet+0.4', until: 'l05.William', icon: 'galley', team: 'rome', pos: [228, 134], size: 18, minPx: 0.045, maxPx: 0.065 },
    // the Norwegian galleys sail in; William's galleys cross
    { follow: 'vA', at: 'l04.Viking', until: 'l04.Harold#1', icon: 'galley', team: 'gold', size: 18, minPx: 0.045, maxPx: 0.065 },
    { follow: 'vC', at: 'l04.Viking+0.3', until: 'l04.Harold#1', icon: 'galley', team: 'gold', size: 18, minPx: 0.045, maxPx: 0.065 },
    { follow: 'xA', at: 'l05.William', until: 'l05.so', icon: 'galley', team: 'rome', size: 18, minPx: 0.045, maxPx: 0.065 },
    { follow: 'xC', at: 'l05.William+0.2', until: 'l05.so', icon: 'galley', team: 'rome', size: 18, minPx: 0.045, maxPx: 0.065 },
  ],

  markers: [{ id: 'senlacMain', at: 'l17.All', pos: [174, 10], glyph: 'hill', letter: 'C', label: 'SENLAC HILL', labelDur: 3, size: 0.06 }],

  arrows: [
    // S3: the Norwegian galleys sail in from the North Sea; Harold marches up the road
    { id: 'vA', at: 'l04.Viking', until: 'l04.north.>', ease: 'cam', team: 'gold', width: 2.6, style: 'dash', path: [[340, -236], [240, -214], [150, -200]], lift: 4, hide: 'l04.Harold#1', head: false },
    { id: 'vC', at: 'l04.Viking+0.3', until: 'l04.north.>', ease: 'cam', team: 'gold', width: 2.6, style: 'dash', path: [[340, -180], [240, -186], [150, -192]], lift: 4, hide: 'l04.Harold#1' },
    { at: 'l04.marched', dur: 2.4, ease: 'cam', team: 'carthage', width: 5, path: [[146, -64], [132, -84], [112, -128], [104, -160]], lift: 5, hide: 'l05' },
    // S3: William's galleys cross; Harold's long march back, dashed
    { id: 'xA', at: 'l05.William', until: 'l05.south,>', ease: 'cam', team: 'rome', width: 2.6, style: 'dash', path: [[150, 156], [150, 100], [150, 52]], lift: 4, hide: 'l05.so', head: false },
    { id: 'xC', at: 'l05.William+0.2', until: 'l05.south,>', ease: 'cam', team: 'rome', width: 2.6, style: 'dash', path: [[228, 134], [190, 90], [162, 50]], lift: 4, hide: 'l05.so' },
    { at: 'l05.marched', dur: 4.6, ease: 'camLong', team: 'carthage', width: 5, style: 'dash', path: [[100, -168], [112, -128], [132, -84], [150, -40], [172, -10]], lift: 5, hide: 'l06' },
    // S8: William to London
    { at: 'l16.Christmas', dur: 2.6, ease: 'cam', team: 'rome', width: 5, path: [[170, 4], [158, -26], [152, -40]], lift: 5, hide: 'l17' },
    // S8: three Old French words ride across the Channel into English
    { id: 'beef', at: 'l17.beef,', dur: 1.8, ease: 'cam', team: 'ink', style: 'dash', width: 2.4, path: [[40, 176], [36, 120], [30, 40], [26, -10]], lift: 6, hide: 'l17.All+1.0' },
    { id: 'jury', at: 'l17.jury,', dur: 1.8, ease: 'cam', team: 'ink', style: 'dash', width: 2.4, path: [[100, 178], [104, 120], [112, 40], [114, -10]], lift: 6, hide: 'l17.All+1.0' },
    { id: 'judge', at: 'l17.judge.', dur: 1.8, ease: 'cam', team: 'ink', style: 'dash', width: 2.4, path: [[160, 170], [176, 110], [196, 40], [206, -10]], lift: 6, hide: 'l17.All+1.0' },
  ],

  volleys: [],

  cards: [
    { at: 0, until: 0.8, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 12.3, until: 16.6, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF HASTINGS', size: 0.078, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
      { text: '1066', size: 0.056, y: 0.575, delay: 1.0, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.5 }, { y: 0.65, w: 0.5 }] },
    { at: 151.2, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.8, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Hastings, 1066', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],
};
