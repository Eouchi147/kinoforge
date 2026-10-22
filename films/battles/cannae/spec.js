// The Battle of Cannae (216 BC): Battle Map v2 spec (the reference film for engine v2; see films/lib/battlemap/SPEC.md and NOTES.md).
// Map: x east, z south, 1 unit about 20 m. Rome (red) starts in the west facing east; Carthage (blue) in the east facing west; the river Aufidus
// runs along the south. Times come from the cue words; the line starts never change (the sound is re-scored around them).
const CAR = { team: 'carthage' }, ROM = { team: 'rome' };

// ------------------------------------------------------------------ the world of the battle
const world = {
  seed: 216, size: [760, 500], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 248, elevation: 31 }, sunEve: { azimuth: 284, elevation: 6 },
  style: { contour: 1.5, pxPerUnit: 5.4 },
  features: [
    { type: 'undulate', amp: 7, scale: 130 }, { type: 'undulate', amp: 2.2, scale: 42 },
    { type: 'ridge', path: [[-400, -215], [-250, -205], [-90, -225], [70, -210], [230, -222], [400, -205]], w: 50, h: 26, rough: 0.25, meander: 10 },
    { type: 'hill', at: [-250, -90], r: [38, 30], h: 12, rot: 20 }, { type: 'hill', at: [170, -150], r: [52, 28], h: 10, rot: -10 }, { type: 'hill', at: [-310, 90], r: [40, 36], h: 9 },
    { type: 'hill', at: [228, 118], r: [30, 22], h: 11, rot: 15 },   // the hill town of Cannae, above the river
    { type: 'sea', poly: [[335, -300], [327, -160], [343, -40], [331, 70], [349, 180], [361, 300], [460, 300], [460, -300]], shelf: 24 },
    { type: 'river', name: 'Aufidus', path: [[-400, 142], [-300, 166], [-200, 176], [-100, 158], [0, 168], [110, 182], [220, 174], [335, 190]], w: 9, depth: 2.4, meander: 9, wl: 38 },
    { type: 'woods', at: [-170, -170], r: [40, 16], rot: 5 }, { type: 'woods', at: [100, -176], r: [58, 14], rot: -8 }, { type: 'woods', at: [-320, 20], r: [18, 30], rot: 30 }, { type: 'woods', at: [280, 40], r: [16, 28] }, { type: 'woods', at: [-60, 214], r: [50, 14] },
    { type: 'farms', rect: [-235, -150, 150, 46, 4], cell: [16, 11] }, { type: 'farms', rect: [215, -120, 110, 46, -6], cell: [15, 10] }, { type: 'farms', rect: [-30, 225, 260, 50, 2], cell: [18, 12] },
    { type: 'farms', rect: [262, 150, 40, 50, 0], cell: [14, 12] },
    { type: 'road', path: [[-400, -150], [-260, -145], [-120, -158], [40, -150], [180, -160], [335, -145]], w: 2.2, meander: 6 },
    { type: 'road', path: [[180, -160], [205, -40], [222, 104]], w: 1.8, meander: 4 },
    { type: 'flat', at: [-235, 80], r: 30, amount: 0.8 }, { type: 'flat', at: [235, -70], r: 30, amount: 0.8 },
  ],
};

// ------------------------------------------------------------------ the second map: the Mediterranean (Hannibal's march, then the epilogue)
const med = {
  world: {
    seed: 202, size: [540, 360], res: 1, base: 0, meshStep: 2.0, sun: { azimuth: 250, elevation: 32 }, sunEve: { azimuth: 284, elevation: 10 },
    style: { contour: 4, pxPerUnit: 7, palette: [[-4, [0.62, 0.72, 0.46]], [3, [0.74, 0.76, 0.48]], [14, [0.80, 0.70, 0.46]], [30, [0.72, 0.58, 0.42]], [48, [0.70, 0.66, 0.62]], [66, [0.95, 0.95, 0.96]]], paletteSoft: 5 },
    features: [
      { type: 'undulate', amp: 4, scale: 90 },
      { type: 'mountains', path: [[-40, -92], [0, -106], [40, -114], [84, -104], [112, -86]], w: 34, h: 66, ridged: 0.8, scale: 46, edge: 20 },
      { type: 'mountains', path: [[-196, -72], [-150, -78]], w: 18, h: 30, ridged: 0.7, scale: 30 },
      { type: 'ridge', path: [[40, -66], [88, -28], [132, 10], [168, 42], [196, 72]], w: 14, h: 14, rough: 0.3 },
      { type: 'sea', poly: [[-400, -300], [400, -300], [400, 300], [-400, 300]], shelf: 34, depth: 8 },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-290, -210], [290, -210], [290, -124], [200, -118], [140, -108], [110, -118], [70, -120], [20, -118], [-30, -102], [-80, -84], [-120, -72], [-160, -60], [-190, -66], [-230, -82], [-290, -90]] },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-290, -90], [-230, -82], [-190, -66], [-176, -30], [-184, 10], [-204, 50], [-236, 76], [-290, 82]] },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[10, -112], [70, -114], [120, -100], [140, -72], [156, -42], [176, -12], [196, 20], [218, 52], [238, 80], [236, 100], [220, 100], [204, 88], [188, 76], [180, 58], [160, 34], [134, 12], [110, -8], [86, -24], [56, -40], [30, -60], [0, -82]] },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[290, -126], [226, -112], [244, -72], [262, -30], [290, 14]] },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-290, 152], [-200, 146], [-120, 150], [-40, 142], [10, 134], [44, 122], [72, 116], [100, 124], [128, 138], [170, 144], [290, 146], [290, 230], [-290, 230]] },
      { type: 'land', wob: 3, smooth: 1, shelf: 12, poly: [[148, 104], [176, 98], [206, 112], [200, 130], [170, 134], [150, 122]] },
      { type: 'land', wob: 3.2, smooth: 1, shelf: 12, poly: [[-60, 20], [-36, 12], [-26, 38], [-32, 76], [-58, 82], [-68, 52]] },
      { type: 'land', wob: 2.4, smooth: 1, shelf: 12, poly: [[-52, -34], [-40, -40], [-34, -12], [-46, -4]] },
      { type: 'woods', at: [-110, -120], r: [44, 14] }, { type: 'woods', at: [-60, -100], r: [26, 8] }, { type: 'woods', at: [150, 20], r: [10, 18], rot: 30 },
      { type: 'farms', rect: [78, -72, 50, 22, 28], cell: [12, 9] },
    ],
  },
  ambient: { wind: [1, 0.3], gusts: 0.4, flow: { dir: [1, 0.2], speed: 0.6, glint: 1.2 },
    birds: [{ center: [60, 150], r: 26, h: 18, n: 6, speed: 5, size: 1.0 }, { center: [120, -30], r: 30, h: 22, n: 5, speed: 6, dir: -1, size: 1.0 }],
    smoke: [{ pos: [100, -6], n: 8, alpha: 0.16, height: 7, at: 'l15.Rome' }] },
  blocks: {
    hanIT: { team: 'carthage', kind: 'cavalry', x: 196, z: 42, heading: 300, len: 14, dep: 8, hidden: true, bannerScale: 1.5, figScale: 1.4 },
    newRome: { team: 'rome', kind: 'infantry', x: 106, z: -4, heading: 90, len: 44, dep: 18, grid: { cols: 3, ranks: 2, gap: 3 }, hidden: true, bannerScale: 1.1, figScale: 1.4 },
    scipio: { team: 'rome', kind: 'infantry', x: 40, z: 143, heading: 90, len: 26, dep: 10, hidden: true, bannerScale: 1.4, figScale: 1.4 },
    scipCavN: { team: 'rome', kind: 'cavalry', x: 44, z: 128, heading: 90, len: 10, dep: 5, hidden: true, banner: false, figScale: 1.4 },
    scipCavS: { team: 'rome', kind: 'cavalry', x: 44, z: 158, heading: 90, len: 10, dep: 5, hidden: true, banner: false, figScale: 1.4 },
    hanAF: { team: 'carthage', kind: 'infantry', x: 92, z: 143, heading: 270, len: 26, dep: 10, hidden: true, bannerScale: 1.4, figScale: 1.4 },
  },
  moves: [
    { block: 'hanIT', at: 'l15.So', dur: 0.8, appear: true },
    { group: 'newRome', at: 'l15.raised', dur: 0.9, stagger: 0.25, appear: true },
    { group: 'newRome', at: 'l15.kept', dur: 4, by: { x: 16, z: 6 }, ease: 'inOut' },
    { blocks: ['scipio', 'hanAF', 'scipCavN', 'scipCavS'], at: 'l16.beat', dur: 0.8, stagger: 0.15, appear: true },
    { blocks: ['scipio', 'hanAF'], at: 'l16.He', dur: 1.6, by: { x: 0 } },
    { block: 'scipio', at: 'l16.He', dur: 2.0, to: { x: 52 }, ease: 'inOut' },
    { block: 'scipCavN', at: 'l16.studied', dur: 2.6, path: [[70, 122], [108, 126], [118, 140]], ease: 'inOut' },
    { block: 'scipCavS', at: 'l16.studied', dur: 2.6, path: [[70, 164], [108, 162], [118, 148]], ease: 'inOut' },
    { block: 'hanAF', at: 'l16.carefully.', dur: 1.6, fadeTo: 1, alphaTo: 0.1, sinkTo: 0.9 },
  ],
  arrows: [
    { id: 'alps', at: 'l02.marched', until: 'l02.point.', ease: 'cam', team: 'ink', style: 'dash', width: 2.4, path: [[-204, -6], [-204, -52], [-170, -78], [-120, -94], [-70, -106], [-20, -116], [30, -112], [54, -98], [62, -74]], head: true, lift: 6 },
    { id: 'sea', at: 'l16.Scipio', until: 'l16.Africa.', ease: 'cam', team: 'rome', style: 'dash', width: 2.2, path: [[100, -2], [76, 34], [56, 80], [44, 118]], lift: 6, hide: 'l16.carefully.' },
    { at: 'l15.raised', until: 'l15.going.', ease: 'out', team: 'rome', width: 3, path: [[106, -4], [76, -34]], lift: 6 },
    { at: 'l15.kept', until: 'l15.going.', ease: 'out', team: 'rome', width: 3, path: [[110, -4], [150, -34]], lift: 6 },
  ],
  labels: [
    { at: 'l02.Africa.', until: 'l02.Two', text: 'NORTH AFRICA', pos: [-60, 172], dy: -0.02, leader: false, rule: false },
    { at: 'l02.Two', until: 'l02.marched', text: 'SPAIN', pos: [-206, -6], y: 2, dy: -0.06 },
    { at: 'l02.Alps,', until: 'l03.and', text: 'THE ALPS', pos: [30, -112], y: 22, dy: -0.07 },
    { at: 'l02.point.', until: 'l03.and', text: 'ITALY', pos: [80, -60], y: 4, dy: -0.06, team: 'rome' },
    { at: 'l15.Hannibal', until: 'l15.Nope.', text: 'HANNIBAL', block: 'hanIT', team: 'carthage', dy: -0.09 },
    { at: 'l15.Nope.', until: 'l16.Fourteen', text: 'ROME', pos: [106, -12], y: 6, team: 'rome', dx: -0.12, dy: -0.11 },
    { at: 'l15.raised', until: 'l16.Fourteen', text: 'NEW ARMIES', block: 'newRome', team: 'rome', dx: 0.12, dy: 0.10 },
    { at: 'l16.Fourteen', until: 'l16.He', text: '202 BC', screen: [0.5, 0.86], big: true },
    { at: 'l16.Scipio', until: 'l16.Africa.', text: 'SCIPIO', pos: [100, -2], y: 4, team: 'rome', dx: 0.1, dy: -0.08 },
    { at: 'l16.He', until: 'l17.Hannibal', text: 'ZAMA', pos: [72, 146], y: 2, dx: 0.0, dy: 0.16, rule: false },
  ],
  icons: [
    { follow: 'alps', at: 'l02.elephants,', until: 'l03.and', icon: 'elephant', team: 'carthage', size: 22, minPx: 0.05, maxPx: 0.07, anim: 'walk' },
    { follow: 'sea', at: 'l16.Scipio', until: 'l16.carefully.', icon: 'galley', team: 'rome', size: 22, minPx: 0.05, maxPx: 0.07 },
  ],
  markers: [{ id: 'carthage', at: 'l02.Carthage,', until: 'l03.and', pos: [72, 134], glyph: 'town', team: [0.15, 0.33, 0.74], label: 'CARTHAGE', labelUntil: 'l02.Two', size: 0.07 }],
};

// ------------------------------------------------------------------ the film
const Y0 = 'l00.ago,';
export default {
  marks: {},
  look: { grade: { saturation: 1.0, contrast: 1.06, grain: 0.03, vignette: 0.30 } },
  world,
  stages: { med },
  msaaOn: [[0, 17.4], [106.4, 127.7]],
  ambient: {
    wind: [1.2, 0.35], gusts: 0.6, flow: { dir: [1, 0.08], speed: 1.2, glint: 1.2 },
    camps: [{ pos: [-235, 80], size: [50, 34], team: 'rome', style: 'grid', fires: 3, people: 14 }, { pos: [235, -70], size: [52, 38], team: 'carthage', style: 'scatter', tents: 28, fires: 3, people: 12, rot: 8 }],
    walkers: [{ path: [[-400, -150], [-260, -145], [-120, -158], [40, -150]], n: 6, gap: 4, speed: 1.6, kind: 'light', team: 'neutral' }, { path: [[180, -160], [205, -40], [222, 104]], n: 4, gap: 5, speed: 1.2, kind: 'light', team: 'neutral', offset: 30 }],
    smoke: [{ pos: [228, 112], n: 8, alpha: 0.14, height: 8 }, { pos: [10, -10], n: 14, alpha: 0.22, height: 12, at: 'l14.By' }, { pos: [40, 30], n: 10, alpha: 0.18, height: 10, at: 'l14.Rome' }],
    birds: [{ center: [-60, -120], r: 50, h: 30, n: 7, speed: 7 }, { path: [[-320, 60], [320, -60]], n: 5, h: 40, speed: 9 }, { center: [220, 90], r: 30, h: 24, n: 5, speed: 6, dir: -1 }],
  },

  blocks: {
    rome: { ...ROM, kind: 'infantry', x: -118, z: 0, heading: 90, len: 92, dep: 54, grid: { cols: 4, ranks: 3, gap: 2.4 }, count: 80000, hidden: true },
    varro: { ...ROM, kind: 'elite', x: -151, z: -14, heading: 90, len: 7, dep: 5, hidden: true, bannerScale: 1.5 },
    paullus: { ...ROM, kind: 'elite', x: -151, z: 14, heading: 90, len: 7, dep: 5, hidden: true, bannerScale: 1.5 },
    hannibal: { ...CAR, kind: 'cavalry', x: 120, z: -6, heading: 270, len: 8, dep: 5, hidden: true, bannerScale: 1.6 },
    carC: { ...CAR, kind: 'infantry', x: 6, z: 0, heading: 270, len: 112, dep: 14, bulge: 0, hidden: true, count: 50000 },
    carEN: { ...CAR, kind: 'elite', x: 6, z: -74, heading: 270, len: 26, dep: 20, hidden: true },
    carES: { ...CAR, kind: 'elite', x: 6, z: 74, heading: 270, len: 26, dep: 20, hidden: true },
    carCavN: { ...CAR, kind: 'cavalry', x: -4, z: -104, heading: 270, len: 32, dep: 14, hidden: true },
    carCavS: { ...CAR, kind: 'cavalry', x: -18, z: 104, heading: 270, len: 32, dep: 14, hidden: true },
    romeCavN: { ...ROM, kind: 'cavalry', x: -114, z: -104, heading: 90, len: 32, dep: 14, hidden: true },
    romeCavS: { ...ROM, kind: 'cavalry', x: -114, z: 104, heading: 90, len: 32, dep: 14, hidden: true },
  },

  moves: [
    // S1: Rome's host forms up rank by rank and marches into line; far away, one man
    { group: 'rome', at: Y0, dur: 0.9, stagger: 0.38, appear: true },
    { blocks: ['romeCavN', 'romeCavS', 'varro', 'paullus'], at: 'l00.armies', dur: 0.9, stagger: 0.3, appear: true },
    { group: 'rome', at: Y0, dur: 9.5, by: { x: 18 }, ease: 'cam' }, { blocks: ['romeCavN', 'romeCavS', 'varro', 'paullus'], at: Y0, dur: 9.5, by: { x: 18 }, ease: 'cam' },
    { block: 'hannibal', at: 'l00.one', dur: 0.8, appear: true },
    // S4: Carthage arrives on the field ("the two armies met"); Hannibal takes his place behind the centre
    { blocks: ['carCavN', 'carEN', 'carC', 'carES', 'carCavS'], at: 'l04.two', dur: 1.0, stagger: 0.3, appear: true },
    { blocks: ['carCavN', 'carEN', 'carC', 'carES', 'carCavS'], at: 'l04.two', dur: 4.5, by: { x: -12 }, ease: 'cam' },
    { block: 'hannibal', at: 'l04.two', dur: 5.5, path: [[95, -5], [64, -4]], ease: 'cam' },
    // S5: Hannibal's plan: the middle bows toward Rome
    { block: 'carC', at: 'l06.put', dur: 3.2, to: { bulge: 0.22, x: -29 }, ease: 'inOut' },
    // S6: the charge; the middle gives way step by step
    { group: 'rome', at: 'l08.charged', dur: 7.0, by: { x: 82 }, ease: 'inQuad' }, { blocks: ['varro', 'paullus'], at: 'l08.charged', dur: 7.0, by: { x: 82 }, ease: 'inQuad' },
    { block: 'carC', at: 'l08.gave', dur: 0.9, to: { bulge: 0.15, x: -9 }, ease: 'out' },
    { block: 'carC', at: 'l08.slowly,', dur: 1.2, to: { bulge: 0.08, x: -1 }, ease: 'out' },
    { block: 'carC', at: 'l08.step', dur: 0.5, to: { bulge: 0.02, x: 4 }, ease: 'out' },
    { block: 'carC', at: 'l08.step#1', dur: 0.5, to: { bulge: -0.03, x: 11 }, ease: 'out' },
    { block: 'carC', at: 'l08.exactly', dur: 0.9, to: { bulge: -0.06, x: 24 }, ease: 'out' },
    { group: 'rome', at: 'l09.pushed', dur: 4.6, by: { x: 30 }, ease: 'out' }, { blocks: ['varro', 'paullus'], at: 'l09.pushed', dur: 4.6, by: { x: 30 }, ease: 'out' },
    { block: 'carC', at: 'l09.pushed', dur: 3.6, to: { bulge: -0.2, x: 63 }, ease: 'out' },
    { block: 'hannibal', at: 'l09.pushed', dur: 3.6, to: { x: 96 }, ease: 'out' },
    // the wings: Carthage's horse beats Rome's, then swings round behind
    { block: 'carCavS', at: 'l10.out', dur: 2.0, to: { x: -66, z: 106 }, ease: 'inQuad' },
    { block: 'carCavN', at: 'l10.out', dur: 2.2, to: { x: -66, z: -106 }, ease: 'inQuad' },
    { blocks: ['romeCavS', 'romeCavN'], at: 'l10.chased', dur: 1.6, by: { x: -60 }, ease: 'out' },
    { blocks: ['romeCavS', 'romeCavN'], at: 'l10.chased+0.3', dur: 1.4, vanish: true },
    { block: 'carCavS', at: 'l10.then', dur: 3.0, path: [[-100, 96], [-132, 60], [-108, 14], [-40, 22]], ease: 'inOut' },
    { block: 'carCavN', at: 'l10.swung', dur: 2.6, path: [[-100, -96], [-130, -58], [-104, -14], [-40, -22]], ease: 'inOut' },
    // the envelopment: left, right, and the horsemen shut the back door
    { block: 'carES', at: 'l11.stepped', dur: 2.2, to: { x: 22, z: 60, heading: 360 }, ease: 'inOut' },
    { block: 'carEN', at: 'l11.stepped+0.5', dur: 2.2, to: { x: 22, z: -60, heading: 180 }, ease: 'inOut' },
    { blocks: ['carCavN', 'carCavS'], at: 'l11.shut', dur: 0.9, by: { x: 14 }, ease: 'out' },
    // S7: packed so tightly
    { group: 'rome', at: 'l13.packed', dur: 3.6, squeeze: { about: [28, 0], kx: 0.8, kz: 0.8, lenK: 0.8, depK: 0.8 }, ease: 'inOut' },
    { blocks: ['varro', 'paullus'], at: 'l13.packed', dur: 3.6, squeeze: { about: [28, 0], kx: 0.8, kz: 0.8 }, ease: 'inOut' },
    { block: 'carC', at: 'l13.packed', dur: 3.6, to: { x: 58 }, ease: 'inOut' },
    { block: 'carEN', at: 'l13.packed', dur: 3.6, by: { z: 11 }, ease: 'inOut' },
    { block: 'carES', at: 'l13.packed', dur: 3.6, by: { z: -11 }, ease: 'inOut' },
    // by evening the ranks thin (numbers, never wounds); one of the two consuls falls
    { group: 'rome', at: 'l14.lost', dur: 3.0, stagger: 0.22, fadeTo: 1, alphaTo: 0.55, sinkTo: 0.9 },
    { block: 'paullus', at: 'l14.commanders.', dur: 1.6, fadeTo: 1, alphaTo: 0.0, sinkTo: 1 },
  ],

  // ------------------------------------------------------------------ scenes: sets and pre-planned cameras (the edit)
  scenes: [
    { id: 'S1', name: 'The host', at: 0, job: 'Rome sends a gigantic army; one man is about to beat it', set: { time: [0.22, 0.12], haze: 1.35, cloud: 0.32 },
      shots: [
        { at: 0, why: 'cold open low over the plain as the host forms up: scale and stakes', from: { target: [-112, 6], dist: 124, pitch: 11, yaw: 66, mm: 30 },
          moves: [{ until: 'l00.battle.', to: { target: [-98, 2], dist: 112, pitch: 13, yaw: 80 } }] },
        { at: 'l00.And', why: 'reverse angle from behind the lone standard: one man against the host', from: { target: [96, -5], dist: 74, pitch: 9, yaw: 268, mm: 35 },
          moves: [{ until: 'l00.today.>', to: { dist: 64, pitch: 9.5 } }] },
        { at: 13.4, why: 'crane up to the map: the lesson is the plan, seen from above (under the title)', from: { target: [-30, 0], width: 600, pitch: 52, yaw: 80, mm: 35 },
          moves: [{ until: 22.4, to: { pitch: 84, yaw: 90, width: 640 }, ease: 'camSoft' }] },
      ] },
    { id: 'S2', name: 'Hannibal', at: 'l02', stage: 'med', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'who Hannibal is, and how audacious: over the Alps with elephants', set: { time: 0.05, haze: 1.0 },
      shots: [
        { at: 'l02', why: 'change of world: the Mediterranean, Carthage in Africa', from: { target: [70, 104], width: 300, pitch: 58, yaw: 0, mm: 35 },
          moves: [{ until: 'l02.Africa.>', to: { target: [40, 80], width: 360 } }] },
        { at: 'l02.Two', why: 'two years earlier: follow the march from Spain over the Alps', from: { target: [-150, -30], width: 330, pitch: 46, yaw: 10, mm: 35 },
          moves: [{ until: 'l02.point.', to: { target: [14, -80], width: 320, yaw: 4 }, ease: 'cam' }] },
      ] },
    { id: 'S3', name: 'Rome', at: 'l03', transition: { type: 'dissolve', dur: 0.8 }, job: 'meet Rome: a huge army with two commanders who take turns', set: { time: 0.12, haze: 1.15, cloud: 0.3 },
      shots: [
        { at: 'l03', why: 'back on the plain: the Roman camp and the army in front of it', from: { target: [-170, 40], dist: 210, pitch: 22, yaw: 252, mm: 35 },
          moves: [{ until: 'l03.they', to: { yaw: 240, dist: 196 } }] },
        { at: 'l03.they', why: 'closer on the two consuls: command passes day by day', from: { target: [-140, -4], dist: 78, pitch: 30, yaw: 62, mm: 40 },
          moves: [{ until: 'l03.wrong?>', to: { dist: 68, target: [-138, -3] } }] },
      ] },
    { id: 'S4', name: 'The field', at: 'l04', job: 'where and how many: a flat plain by a river, 80,000 against 50,000, and Rome\'s simple plan', set: { time: [0.06, 0.0], haze: 1.05, cloud: 0.28 },
      shots: [
        { at: 'l04', why: 'establish the whole field: the river, the plain, the town; Carthage marches in', from: { target: [-10, 70], width: 660, pitch: 44, yaw: 12, mm: 35 },
          moves: [{ until: 'l04.river.>', to: { target: [-10, 40], width: 580, pitch: 54 } }] },
        { at: 'l05', why: 'the numbers on the plan view: both armies side by side', from: { target: [-40, 0], width: 480, pitch: 86, yaw: 0, mm: 35 },
          moves: [{ at: 'l05.Hannibal', until: 'l05.Rome\'s', to: { width: 450, target: [-30, 0] } }] },
        { at: 'l05.Rome\'s', why: 'Rome\'s plan from behind its own ranks: simple and heavy', from: { target: [-52, 0], dist: 156, pitch: 19, yaw: 90, mm: 35 },
          moves: [{ until: 'l05.win.>', to: { dist: 126, target: [-44, 0] } }] },
      ] },
    { id: 'S5', name: 'The trap is set', at: 'l06', job: 'Hannibal\'s plan: a weak centre bowed toward Rome, strong ends, horsemen on the sides', set: { time: 0.0, haze: 1.0 },
      shots: [
        { at: 'l06', why: 'the plan from above: the centre bends into a bow', from: { target: [-12, 0], width: 330, pitch: 84, yaw: 0, mm: 35 },
          moves: [{ at: 'l06.put', until: 'l06.bow.>', to: { width: 290, target: [-8, 0] } }] },
        { at: 'l07', why: 'low along Carthage\'s line: the veterans and the horsemen waiting at the ends', from: { target: [4, -36], dist: 170, pitch: 22, yaw: 196, mm: 35 },
          moves: [{ until: 'l07.sides.>', to: { yaw: 184, target: [2, -24] } }] },
      ] },
    { id: 'S6', name: 'The jaws', at: 'l08', job: 'the Romans walk into the bow, the horsemen ride round, and the trap closes', set: { time: [0.05, 0.2], haze: 1.1 },
      shots: [
        { at: 'l08', why: 'behind the Roman ranks as they charge: the weight of the push', from: { target: [-56, 0], dist: 112, pitch: 15, yaw: 90, mm: 35 },
          moves: [{ until: 'l08.and', to: { target: [-28, 0], dist: 104 } }] },
        { at: 'l08.and', why: 'high angle: the middle gives way, step by step, as planned', from: { target: [-12, 0], width: 300, pitch: 64, yaw: 40, mm: 35 },
          moves: [{ until: 'l08.planned.>', to: { target: [4, 0], width: 280, yaw: 48 } }] },
        { at: 'l09', why: 'low from the river side: the Romans push deeper, sure they are winning', from: { target: [6, 12], dist: 136, pitch: 15, yaw: 0, mm: 35 },
          moves: [{ until: 'l09.gap.>', to: { target: [22, 6], dist: 118 } }] },
        { at: 'l10', why: 'meanwhile, out on the sides: the cavalry by the river', from: { target: [-58, 102], width: 250, pitch: 46, yaw: 0, mm: 35 },
          moves: [{ until: 'l10.then', to: { target: [-88, 98] } }] },
        { at: 'l10.then', why: 'high and wide: the horsemen swing round behind the Roman army', from: { target: [-56, 0], width: 430, pitch: 70, yaw: 20, mm: 35 },
          moves: [{ until: 'l10.Romans.>', to: { yaw: 12, width: 410 } }] },
        { at: 'l11', why: 'the decisive moment, wide and from above: left, right, and the back door', from: { target: [-12, 0], width: 380, pitch: 88, yaw: 0, mm: 35 },
          moves: [{ at: 'l11.left,', until: 'l11.door.>', to: { width: 350, target: [-6, 0] } }] },
      ] },
    { id: 'S7', name: 'Surrounded', at: 'l12', climax: true, job: 'how it worked up close: packed and helpless; the cost by evening', set: { time: [0.25, 0.25], haze: 1.15 },
      shots: [
        { at: 'l12', why: 'closer and slower: circle the ring the way it closed', from: { target: [24, 0], dist: 150, pitch: 30, yaw: 118, mm: 35 },
          moves: [{ until: 'l12.hug.>', to: { yaw: 160, dist: 132 }, ease: 'camLong' }] },
        { at: 'l13', why: 'low and close inside the press: no room to lift a sword', from: { target: [30, 2], dist: 64, pitch: 13, yaw: 200, mm: 45 },
          moves: [{ until: 'l13.swords.>', to: { dist: 56 } }] },
        { at: 'l14', why: 'pull back as the sun goes down: the cost', from: { target: [24, 0], dist: 150, pitch: 22, yaw: 240, mm: 35 },
          moves: [{ until: 'l14.history.>', to: { dist: 236, pitch: 30, yaw: 252 }, ease: 'camLong' }] },
      ] },
    { id: 'S8', name: 'Rome refuses', at: 'l15', stage: 'med', inset: 'full', transition: { type: 'dissolve', dur: 1.0 }, job: 'the twist: winning a battle is not winning a war', set: { time: [0.1, 0.25], haze: 1.0 },
      shots: [
        { at: 'l15', why: 'the map of Italy: Hannibal in the south, and the question', from: { target: [150, 14], width: 330, pitch: 60, yaw: 0, mm: 35 },
          moves: [{ until: 'l15.right?>', to: { target: [154, 18], width: 316 } }] },
        { at: 'l15.Nope.', why: 'cut on the punchline: Rome refuses and raises new armies', from: { target: [110, -8], width: 210, pitch: 50, yaw: 326, mm: 35 },
          moves: [{ until: 'l15.going.>', to: { width: 244 } }] },
        { at: 'l16', why: 'fourteen years later: Scipio sails for Africa', from: { target: [74, 60], width: 320, pitch: 56, yaw: 0, mm: 35 },
          moves: [{ until: 'l16.Africa.>', to: { target: [66, 100] } }] },
        { at: 'l16.He', why: 'Zama: Scipio uses Hannibal\'s own trick on him', from: { target: [74, 146], width: 170, pitch: 58, yaw: 18, mm: 35 },
          moves: [{ until: 'l16.carefully.>', to: { width: 156 } }] },
      ] },
    { id: 'S9', name: 'The lesson', at: 'l17', transition: { type: 'dissolve', dur: 1.0 }, job: 'the result in one image: the double envelopment, copied ever since', set: { time: 0.35, haze: 1.1 },
      shots: [
        { at: 'l17', why: 'back over Cannae from above: the giant hug as the textbook diagram', from: { target: [-4, 0], width: 380, pitch: 89, yaw: 0, mm: 35 },
          moves: [{ until: 157.6, to: { width: 450 }, ease: 'camLong' }] },
      ] },
  ],

  // ------------------------------------------------------------------ the legend (motion-graphics frame)
  legend: {
    title: { text: 'THE BATTLE OF CANNAE', sub: '2 August 216 BC', at: 'l02.Hannibal,' },
    show: [['l02.Hannibal,', 'l17.since.>']],
    sides: [
      { id: 'carthage', team: 'carthage', name: 'CARTHAGE', commander: 'Hannibal', banner: 'banner', at: 'l02.Hannibal,', strength: 50000, strengthAt: 'l05.50' },
      { id: 'rome', team: 'rome', name: 'ROME', commander: 'Varro and Paullus', commanderAt: 'l03.commanders', banner: 'vexillum', at: 'l03.Rome.', strength: 80000, strengthAt: 'l05.80', dimAt: 'l14.lost' },
    ],
    key: { show: [['l04.armies', 'l12'], ['l17', 'l17.since.>']] },
    units: [
      { id: 'inf', kind: 'infantry', name: 'Infantry', teams: ['rome', 'carthage'], at: 'l05.soldiers.' },
      { id: 'vets', kind: 'elite', name: 'Veteran infantry', team: 'carthage', at: 'l07.best' },
      { id: 'cav', kind: 'cavalry', name: 'Cavalry', teams: ['rome', 'carthage'], at: 'l07.horsemen' },
    ],
    places: [
      { id: 'plain', letter: 'A', glyph: 'plain', name: 'The plain', at: 'l04.plain', pos: [-60, 128], label: false, markerSize: 0.05 },
      { id: 'aufidus', letter: 'B', glyph: 'river', name: 'River Aufidus', at: 'l04.river.', pos: [-150, 168], ldy: 0.05 },
      { id: 'cannae', letter: 'C', glyph: 'town', name: 'Cannae', at: 'l04.river.+1.0', pos: [228, 112], y: 10, team: 'rome' },
    ],
    focus: [
      { entry: 'inf', at: 'l06.weakest', until: 'l06.like' }, { entry: 'vets', at: 'l11.best', until: 'l11.left,' }, { entry: 'cav', at: 'l11.horsemen', until: 'l11.door.>' },
      { entry: 'carthage', at: 'l17.Hannibal', until: 'l17.Rome' }, { entry: 'rome', at: 'l17.Rome', until: 'l17.and' },
    ],
    scale: { unitM: 20, show: [['l04', 'l12']] },
  },

  light: [{ at: 'l14.evening,', dur: 4.0, to: { eve: 1, haze: 1.3 }, ease: 'inOut' }],

  labels: [
    { at: 1.3, until: 4.6, text: '2,200 YEARS AGO', screen: [0.5, 0.16], big: true },
    { at: 'l00.Rome', until: 'l00.battle.>', text: 'ROME', block: 'rome', team: 'rome', dx: 0.0, dy: -0.16, big: true },
    { at: 'l00.one', until: 'l00.today.>', text: 'ONE MAN', block: 'hannibal', team: 'carthage', dx: 0.02, dy: -0.12, big: true },
    { at: 'l03.they', until: 'l04', text: 'VARRO', block: 'varro', team: 'rome', dx: 0.02, dy: -0.22 },
    { at: 'l03.they', until: 'l04', text: 'PAULLUS', block: 'paullus', team: 'rome', dx: 0.10, dy: -0.22 },
    { at: 'l04.August,', until: 'l04.the', text: '2 AUGUST 216 BC', screen: [0.5, 0.86], big: true },
    { at: 'l06.weakest', until: 'l06.like', text: 'WEAKEST TROOPS', block: 'carC', team: 'carthage', dx: 0.10, dy: -0.10 },
    { at: 'l07.best', until: 'l07.horsemen', text: 'VETERANS', block: 'carEN', team: 'carthage', dx: -0.06, dy: -0.10 },
    { at: 'l07.horsemen', until: 'l08', text: 'HORSEMEN', block: 'carCavN', team: 'carthage', dx: -0.06, dy: -0.10 },
    { at: 'l08.gave', until: 'l08.exactly', text: 'THE MIDDLE GIVES WAY', block: 'carC', team: 'carthage', dx: 0.14, dy: -0.12 },
    { at: 'l08.exactly', until: 'l09', text: 'AS PLANNED', block: 'carC', team: 'carthage', dx: 0.14, dy: -0.12 },
    { at: 'l10.Roman', until: 'l10.then', text: 'ROMAN CAVALRY', block: 'romeCavS', team: 'rome', dx: -0.08, dy: -0.12 },
    { at: 'l10.behind', until: 'l11', text: 'BEHIND THE ROMANS', pos: [-82, 0], y: 4, team: 'carthage', dx: -0.10, dy: -0.10, big: true },
    { at: 'l12.surrounded.', until: 'l12.History\'s', text: 'SURROUNDED', block: 'rome', team: 'carthage', dy: -0.16, big: true },
    { at: 'l14.tens', until: 'l14.one', text: 'ABOUT 50,000 ROMANS LOST', screen: [0.5, 0.86], big: true },
    { at: 'l14.one', until: 'l14.It', text: 'CONSUL PAULLUS', block: 'paullus', team: 'rome', dx: -0.1, dy: -0.12 },
  ],

  counters: [
    { at: 'l05.80', until: 'l05.Rome\'s', block: 'rome', team: 'rome', from: 0, to: 80000, countDur: 1.1, dy: -0.12, step: 1000 },
    { at: 'l05.50', until: 'l05.Rome\'s', block: 'carC', team: 'carthage', from: 0, to: 50000, countDur: 1.1, dx: 0.10, dy: -0.12, step: 1000 },
  ],

  icons: [
    // one day each: the command (a gold star) passes between the two consuls on the words
    { id: 'cV', at: 'l03.they', until: 'l04', icon: 'star', block: 'varro', hidden: true }, { id: 'cP', at: 'l03.they', until: 'l04', icon: 'star', block: 'paullus', hidden: true },
    { at: 'l03.took', until: 'l04', icon: 'star', block: 'varro', size: 0.05, screen: null, hop: { between: ['cV', 'cP'], swaps: ['l03.One', 'l03.day', 'l03.each.', 'l03.What', 'l03.possibly', 'l03.wrong?'], dur: 0.34, start: 0, up: 0.2 }, minPx: 0.06, maxPx: 0.06 },
  ],

  arrows: [
    { at: 'l05.push', dur: 1.0, ease: 'out', team: 'rome', width: 7, path: [[-72, 0], [-16, 0]], lift: 6, hide: 'l06' },
    { at: 'l06.bulging', dur: 1.2, ease: 'out', team: 'carthage', width: 4, path: [[-22, 0], [-58, 0]], lift: 6, hide: 'l07' },
    { at: 'l06.bow.', dur: 0.8, ease: 'out', team: 'ink', width: 1.0, head: false, taper: 1, path: [[-6, -56], [-6, 56]], lift: 6, hide: 'l07' },
    { at: 'l08.charged', dur: 1.4, ease: 'out', team: 'rome', width: 7, path: [[-64, 0], [-14, 0]], lift: 6, hide: 'l08.slowly,' },
    { at: 'l08.slowly,', dur: 0.6, ease: 'out', team: 'carthage', width: 3.4, path: [[-6, -24], [12, -24]], lift: 6, hide: 'l08.exactly' },
    { at: 'l08.slowly,', dur: 0.6, ease: 'out', team: 'carthage', width: 3.4, path: [[-6, 24], [12, 24]], lift: 6, hide: 'l08.exactly' },
    { at: 'l09.pushed', until: 'l09.gap.', ease: 'out', team: 'rome', width: 7, path: [[-10, 0], [50, 0]], lift: 6, hide: 'l10' },
    { at: 'l10.chased', dur: 0.8, ease: 'out', team: 'carthage', width: 4, path: [[-24, 104], [-78, 106]], lift: 6, hide: 'l10.then' },
    { at: 'l10.chased', dur: 0.8, ease: 'out', team: 'carthage', width: 4, path: [[-8, -104], [-78, -106]], lift: 6, hide: 'l10.then' },
    { at: 'l10.swung', until: 'l10.Romans.', ease: 'inOut', team: 'carthage', width: 3.6, style: 'dash', path: [[-100, 96], [-132, 60], [-108, 14], [-50, 22]], lift: 6, hide: 'l11.left,' },
    { at: 'l10.swung', until: 'l10.Romans.', ease: 'inOut', team: 'carthage', width: 3.6, style: 'dash', path: [[-100, -96], [-130, -58], [-104, -14], [-50, -22]], lift: 6, hide: 'l11.left,' },
    { at: 'l11.left,', dur: 0.7, ease: 'out', team: 'carthage', width: 5, path: [[22, 88], [22, 58]], lift: 6, hide: 'l12' },
    { at: 'l11.right,', dur: 0.7, ease: 'out', team: 'carthage', width: 5, path: [[22, -88], [22, -58]], lift: 6, hide: 'l12' },
    { at: 'l11.shut', dur: 0.8, ease: 'out', team: 'carthage', width: 5, path: [[-64, 0], [-38, 0]], lift: 6, hide: 'l12' },
    { at: 'l12.surrounded.', dur: 1.4, ease: 'inOut', team: 'gold', width: 1.6, style: 'dash', head: false, taper: 1, path: [[-50, -70], [70, -70], [84, 0], [70, 70], [-50, 70], [-60, 0], [-50, -70]], smooth: true, lift: 6, hide: 'l13' },
    // S9: the giant hug, drawn as the textbook diagram
    { at: 'l17.generals', dur: 1.8, ease: 'cam', team: 'carthage', width: 6, path: [[60, -62], [10, -96], [-60, -86], [-92, -36], [-70, -8]], lift: 7 },
    { at: 'l17.generals', dur: 1.8, ease: 'cam', team: 'carthage', width: 6, path: [[60, 62], [10, 96], [-60, 86], [-92, 36], [-70, 8]], lift: 7 },
  ],

  volleys: [],

  cards: [
    { at: 0, until: 0.8, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 17.4, until: 21.7, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF CANNAE', size: 0.084, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
      { text: '216 BC', size: 0.056, y: 0.575, delay: 1.0, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.5 }, { y: 0.65, w: 0.5 }] },
    { at: 153.43, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.8, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Cannae, 216 BC', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],
};
