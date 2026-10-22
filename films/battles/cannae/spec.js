// The Battle of Cannae (216 BC): Battle Map spec. Times come from the cue words (see films/lib/battlemap/SPEC.md).
// Map: x east, z south, 1 unit about 20 m. Rome (red) starts in the west facing east; Carthage (blue) in the east facing west; the river Aufidus runs along the south.
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
    { type: 'sea', poly: [[335, -300], [327, -160], [343, -40], [331, 70], [349, 180], [361, 300], [460, 300], [460, -300]], shelf: 24 },
    { type: 'river', name: 'Aufidus', path: [[-400, 142], [-300, 166], [-200, 176], [-100, 158], [0, 168], [110, 182], [220, 174], [335, 190]], w: 9, depth: 2.4, meander: 9, wl: 38 },
    { type: 'woods', at: [-170, -170], r: [40, 16], rot: 5 }, { type: 'woods', at: [100, -176], r: [58, 14], rot: -8 }, { type: 'woods', at: [-300, 30], r: [20, 34], rot: 30 }, { type: 'woods', at: [255, 40], r: [18, 30] }, { type: 'woods', at: [-60, 214], r: [50, 14] },
    { type: 'farms', rect: [-235, -150, 150, 46, 4], cell: [16, 11] }, { type: 'farms', rect: [215, -120, 110, 46, -6], cell: [15, 10] }, { type: 'farms', rect: [-30, 225, 260, 50, 2], cell: [18, 12] },
    { type: 'farms', rect: [-322, -40, 40, 80, 0], cell: [14, 12] }, { type: 'farms', rect: [262, 120, 40, 70, 0], cell: [14, 12] },
    { type: 'road', path: [[-400, -150], [-260, -145], [-120, -158], [40, -150], [180, -160], [335, -145]], w: 2.2, meander: 6 },
  ],
};

// ------------------------------------------------------------------ the second map (Alps inset, then the epilogue)
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
      // Gaul and the north shore, Iberia, Italy, the Balkans, Africa, then the islands
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
  blocks: {
    hanIT: { team: 'carthage', kind: 'infantry', x: 192, z: 40, heading: 300, len: 22, dep: 12, height: 5, hidden: true, bannerScale: 1.6 },
    newRome: { team: 'rome', kind: 'infantry', x: 106, z: -4, heading: 90, len: 60, dep: 24, grid: { cols: 3, ranks: 2, gap: 3 }, height: 5, hidden: true, bannerScale: 1.2 },
    scipio: { team: 'rome', kind: 'infantry', x: 34, z: 142, heading: 90, len: 26, dep: 14, height: 5, hidden: true, bannerScale: 1.8 },
    hanAF: { team: 'carthage', kind: 'infantry', x: 104, z: 150, heading: 270, len: 22, dep: 12, height: 5, hidden: true, bannerScale: 1.6 },
  },
  moves: [
    { block: 'hanIT', at: 'l15.Hannibal', dur: 0.9, appear: true, appearFrom: 30 },
    { group: 'newRome', at: 'l15.raised', dur: 0.8, stagger: 0.16, appear: true, appearFrom: 40 },
    { block: 'scipio', at: 'l16.Scipio', dur: 0.4, to: { alpha: 1 } },
    { block: 'hanAF', at: 'l16.beat', dur: 0.8, appear: true, appearFrom: 30 },
    { block: 'hanAF', at: 'l16.Africa', dur: 1.8, to: { x: 126, z: 158 }, ease: 'inOut' },
    { block: 'hanAF', at: 'l16.Africa', dur: 1.8, fadeTo: 1, alphaTo: 0.0, sinkTo: 0.6 },
  ],
  arrows: [
    { id: 'alps', at: 'l02.marched', until: 'l02.point.', ease: 'linear', team: 'ink', style: 'dash', width: 2.6, path: [[-204, -6], [-204, -52], [-170, -78], [-120, -94], [-70, -106], [-20, -116], [30, -112], [54, -98], [62, -74]], head: true, lift: 6, hide: 'l03.and' },
    { id: 'sea', at: 'l16.Scipio', until: 'l16.Africa', ease: 'inOut', team: 'rome', style: 'dash', width: 2.4, path: [[100, -2], [76, 34], [56, 80], [40, 116]], lift: 6 },
    { id: 'march', at: 'l15.raised', until: 'l15.going.', ease: 'out', team: 'rome', width: 3, path: [[106, -4], [74, -36]], lift: 6 },
    { id: 'march2', at: 'l15.kept', until: 'l15.going.', ease: 'out', team: 'rome', width: 3, path: [[106, -4], [150, -34]], lift: 6 },
  ],
  labels: [
    { at: 'l02.Hannibal,', until: 'l02.Carthage,', text: 'HANNIBAL', pos: [72, 128], y: 4, team: 'carthage', dy: -0.2, big: true },
    { at: 'l02.Carthage,', until: 'l02.Africa.', text: 'CARTHAGE', pos: [72, 134], y: 4, team: 'carthage', dy: -0.2, dx: -0.12 },
    { at: 'l02.North', until: 'l03.and', text: 'NORTH AFRICA', pos: [-100, 170], y: 0, dy: -0.12, leader: false },
    { at: 'l02.Alps,', until: 'l02.point.', text: 'THE ALPS', pos: [30, -112], y: 20, dy: -0.12 },
    { at: 'l02.Two', until: 'l02.marched', text: 'TWO YEARS EARLIER', screen: [0.5, 0.88], big: true },
    { at: 'l15.Hannibal', until: 'l15.Nope.', text: 'HANNIBAL', pos: [192, 40], y: 8, team: 'carthage', dy: -0.16 },
    { at: 'l15.right?', until: 'l15.Nope.', text: 'WON THE WAR?', screen: [0.5, 0.2], big: true },
    { at: 'l15.Nope.', until: 'l15.refused', text: 'NOPE', screen: [0.5, 0.2], big: true, team: 'rome' },
    { at: 'l15.Rome', until: 'l16.Fourteen', text: 'ROME', pos: [106, -10], y: 6, team: 'rome', dy: -0.12, dx: -0.1 },
    { at: 'l15.raised', until: 'l16.Fourteen', text: 'NEW ARMIES', pos: [106, -4], y: 12, team: 'rome', dy: -0.2, dx: 0.14 },
    { at: 'l16.Fourteen', until: 'l16.a', text: '14 YEARS LATER', screen: [0.5, 0.14], big: true },
    { at: 'l16.a', until: 'l16.He', text: '202 BC', screen: [0.5, 0.14], big: true, team: 'rome' },
    { at: 'l16.Scipio', until: 'l16.studied', text: 'SCIPIO', pos: [106, -4], y: 12, team: 'rome', dy: -0.2, dx: -0.1 },
    { at: 'l16.Africa', until: 'l16.He', text: 'AFRICA', pos: [-100, 172], dy: -0.12, leader: false },
    { at: 'l16.studied', until: 'l17.Hannibal', text: 'HE STUDIED HIS TRICKS', pos: [34, 142], y: 10, team: 'rome', dy: -0.24 },
    { at: 'l17.Hannibal', until: 'l17.Rome', text: 'HANNIBAL WON THE BATTLE', screen: [0.5, 0.16], big: true, team: 'carthage' },
    { at: 'l17.Rome', until: 'l17.and', text: 'ROME WON THE WAR', screen: [0.5, 0.16], big: true, team: 'rome' },
  ],
  icons: [
    { at: 'l02.Hannibal,', until: 'l02.Carthage,', icon: 'helmet', team: 'carthage', pos: [72, 128], size: 24, anim: 'bounce' },
    { at: 'l02.Carthage,', until: 'l03.and', icon: 'city', team: 'carthage', pos: [72, 134], size: 30 },
    { follow: 'alps', at: 'l02.elephants,', until: 'l03.and', icon: 'elephant', team: 'carthage', size: 26, anim: 'walk' },
    { at: 'l02.point.', until: 'l03.and', icon: 'burst', pos: [62, -74], y: 6, size: 30, anim: 'bounce' },
    { at: 'l15.Hannibal', until: 'l15.Nope.', icon: 'crown', pos: [192, 40], y: 24, size: 20, anim: 'bounce' },
    { at: 'l15.Nope.', until: 'l15.refused', icon: 'no', pos: [192, 40], y: 24, size: 26 },
    { at: 'l15.Rome', until: 'l16.Fourteen', icon: 'city', team: 'rome', pos: [106, -10], size: 30 },
    { at: 'l16.Scipio', until: 'l16.studied', icon: 'helmet', team: 'rome', pos: [106, -4], y: 6, size: 22, anim: 'bounce' },
    { follow: 'sea', at: 'l16.Scipio', until: 'l16.Africa', icon: 'ship', team: 'rome', size: 26 },
    { at: 'l16.studied', until: 'l17.Hannibal', icon: 'book', pos: [34, 142], y: 10, size: 26, anim: 'bounce' },
    { at: 'l17.Hannibal', until: 'l17.Rome', icon: 'crown', screen: [0.5, 0.30], size: 0.14, anim: 'bounce' },
    { at: 'l17.Rome', until: 'l17.and', icon: 'laurel', screen: [0.5, 0.31], size: 0.14, anim: 'bounce' },
    // the final graphic: the double envelopment, copied again and again
    { at: 'l17.copying', until: 'l17.since.', icon: 'hug', team: 'carthage', inner: [0.8, 0.12, 0.12], screen: [0.5, 0.58], size: 0.30 },
    { at: 'l17.copying', until: 'l17.since.', icon: 'hug', team: 'green', inner: [0.86, 0.80, 0.64], screen: [0.24, 0.62], size: 0.15 },
    { at: 'l17.his', until: 'l17.since.', icon: 'hug', team: 'gold', inner: [0.16, 0.38, 0.88], screen: [0.77, 0.62], size: 0.15 },
    { at: 'l17.giant', until: 'l17.since.', icon: 'hug', team: 'rome', inner: [0.16, 0.38, 0.88], screen: [0.12, 0.45], size: 0.1 },
    { at: 'l17.hug', until: 'l17.since.', icon: 'hug', team: 'neutral', inner: [0.8, 0.12, 0.12], screen: [0.88, 0.46], size: 0.1 },
    { at: 'l17.ever', until: 'l17.since.', icon: 'hug', team: 'carthage', inner: [0.86, 0.80, 0.64], screen: [0.32, 0.46], size: 0.08 },
    { at: 'l17.since.', until: 'l17.since.+1.2', icon: 'hug', team: 'rome', inner: [0.96, 0.84, 0.46], screen: [0.68, 0.46], size: 0.08 },
  ],
  camera: [
    { at: 'l02.Hannibal,', target: [0, 20], width: 560, pitch: 62, yaw: 0, mm: 35 },
    { at: 'l02.Alps,', target: [10, -8], width: 330, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.marched', target: [-20, -56], width: 300, pitch: 40, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.elephants,', target: [-18, -70], width: 260, pitch: 38, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l03.and', target: [-10, -70], width: 250, pitch: 40, yaw: 14, mm: 35 },
    { at: 'l15.So', target: [92, 36], width: 470, pitch: 72, yaw: 0, mm: 35 },
    { at: 'l15.refused', target: [110, 24], width: 400, pitch: 66, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.Fourteen', target: [96, 44], width: 420, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.Africa', target: [76, 96], width: 330, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l17.Hannibal', target: [80, 34], width: 540, pitch: 80, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 160, target: [80, 34], width: 520, pitch: 80, yaw: 0, mm: 35, ease: 'inOut' },
  ],
};

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 } },
  world,
  stages: { med },
  msaaOn: [[0, 14], [118, 127]],

  blocks: {
    rome: { ...ROM, kind: 'infantry', x: -100, z: 0, heading: 90, len: 92, dep: 54, grid: { cols: 4, ranks: 3, gap: 2.4 }, count: 80000, hidden: true },
    hannibal: { ...CAR, kind: 'infantry', x: 115, z: -5, heading: 270, len: 14, dep: 9, hidden: true, bannerScale: 1.3 },
    carC: { ...CAR, kind: 'infantry', x: 6, z: 0, heading: 270, len: 112, dep: 14, bulge: 0, hidden: true, count: 50000 },
    carEN: { ...CAR, kind: 'elite', x: 6, z: -74, heading: 270, len: 26, dep: 20, hidden: true },
    carES: { ...CAR, kind: 'elite', x: 6, z: 74, heading: 270, len: 26, dep: 20, hidden: true },
    carCavN: { ...CAR, kind: 'cavalry', x: -4, z: -104, heading: 270, len: 32, dep: 14, hidden: true },
    carCavS: { ...CAR, kind: 'cavalry', x: -18, z: 104, heading: 270, len: 32, dep: 14, hidden: true },
    romeCavN: { ...ROM, kind: 'cavalry', x: -96, z: -104, heading: 90, len: 32, dep: 14, hidden: true },
    romeCavS: { ...ROM, kind: 'cavalry', x: -96, z: 104, heading: 90, len: 32, dep: 14, hidden: true },
  },

  moves: [
    // the hook: Rome's host assembles block by block, then one lone man appears
    { group: 'rome', at: 'l00.Rome', dur: 0.8, stagger: 0.17, appear: true },
    { block: 'hannibal', at: 'l00.one', dur: 0.8, appear: true, appearFrom: 20 },
    { block: 'hannibal', at: 21.6, dur: 0.4, vanish: true },
    // Rome's two cavalry wings and Carthage's whole army (as a straight line) appear for the two numbers
    { blocks: ['romeCavN', 'romeCavS'], at: 'l04.armies', dur: 0.8, stagger: 0.2, appear: true },
    { blocks: ['carEN', 'carC', 'carES', 'carCavN', 'carCavS'], at: 'l05.Hannibal', dur: 0.8, stagger: 0.14, appear: true },
    { group: 'rome', at: 'l05.bigger', dur: 0.25, to: { scale: 1.06 }, ease: 'out' }, { group: 'rome', at: 'l05.bigger+0.25', dur: 0.4, to: { scale: 1 }, ease: 'inOut' },
    // Hannibal's plan: the middle bows toward Rome
    { block: 'carC', at: 'l06.put', dur: 3.2, to: { bulge: 0.22, x: -17 }, ease: 'inOut' },
    { blocks: ['carEN', 'carES'], at: 'l07.best', dur: 0.25, to: { scale: 1.2 }, ease: 'out' }, { blocks: ['carEN', 'carES'], at: 'l07.best+0.25', dur: 0.4, to: { scale: 1 } },
    { blocks: ['carCavN', 'carCavS'], at: 'l07.horsemen', dur: 0.25, to: { scale: 1.2 }, ease: 'out' }, { blocks: ['carCavN', 'carCavS'], at: 'l07.horsemen+0.25', dur: 0.4, to: { scale: 1 } },
    // the charge: Rome pushes east, the middle gives way step by step
    { group: 'rome', at: 'l08.charged', dur: 7.0, by: { x: 82 }, ease: 'inQuad' },
    { block: 'carC', at: 'l08.gave', dur: 0.9, to: { bulge: 0.15, x: -9 }, ease: 'out' },
    { block: 'carC', at: 'l08.slowly,', dur: 1.2, to: { bulge: 0.08, x: -1 }, ease: 'out' },
    { block: 'carC', at: 'l08.step', dur: 0.4, to: { bulge: 0.02, x: 4 }, ease: 'out' },
    { block: 'carC', at: 'l08.step#1', dur: 0.4, to: { bulge: -0.03, x: 11 }, ease: 'out' },
    { block: 'carC', at: 'l08.exactly', dur: 0.9, to: { bulge: -0.06, x: 24 }, ease: 'out' },
    // deeper into the gap
    { group: 'rome', at: 'l09.pushed', dur: 4.6, by: { x: 30 }, ease: 'out' },
    { block: 'carC', at: 'l09.pushed', dur: 3.6, to: { bulge: -0.2, x: 63 }, ease: 'out' },
    // the wings: Carthage's horse beats Rome's, then swings round behind
    { block: 'carCavS', at: 'l10.out', dur: 2.0, to: { x: -66, z: 106 }, ease: 'inQuad' },
    { block: 'carCavN', at: 'l10.out', dur: 2.2, to: { x: -66, z: -106 }, ease: 'inQuad' },
    { blocks: ['romeCavS', 'romeCavN'], at: 'l10.chased', dur: 1.5, by: { x: -60 }, ease: 'out' },
    { blocks: ['romeCavS', 'romeCavN'], at: 'l10.chased+0.2', dur: 1.2, vanish: true },
    { block: 'carCavS', at: 'l10.then', dur: 3.0, path: [[-100, 96], [-132, 60], [-108, 14], [-40, 22]], ease: 'inOut' },
    { block: 'carCavN', at: 'l10.swung', dur: 2.6, path: [[-100, -96], [-130, -58], [-104, -14], [-40, -22]], ease: 'inOut' },
    // the envelopment: both ends step in, the horsemen close the back door
    { block: 'carEN', at: 'l11.stepped', dur: 2.2, to: { x: 22, z: -60, heading: 180 }, ease: 'inOut' },
    { block: 'carES', at: 'l11.stepped', dur: 2.2, to: { x: 22, z: 60, heading: 360 }, ease: 'inOut' },
    { blocks: ['carCavN', 'carCavS'], at: 'l11.shut', dur: 0.9, by: { x: 14 }, ease: 'out' },
    // surrounded, packed so tightly
    { group: 'rome', at: 'l13.packed', dur: 3.6, squeeze: { about: [28, 0], kx: 0.8, kz: 0.8, lenK: 0.8, depK: 0.8 }, ease: 'inOut' },
    { block: 'carC', at: 'l13.packed', dur: 3.6, to: { x: 58 }, ease: 'inOut' },
    { block: 'carEN', at: 'l13.packed', dur: 3.6, by: { z: 11 }, ease: 'inOut' },
    { block: 'carES', at: 'l13.packed', dur: 3.6, by: { z: -11 }, ease: 'inOut' },
    // by evening Rome's blocks fade away (numbers, never wounds)
    { group: 'rome', at: 'l14.lost', dur: 2.4, stagger: 0.22, fadeTo: 1, alphaTo: 0.1, sinkTo: 0.9 },
  ],

  light: [
    { at: 'l14.evening,', dur: 3.4, to: { eve: 1 }, ease: 'inOut' },
    { at: 'l14.evening,', dur: 3.4, to: { haze: 1.3 }, ease: 'inOut' },
  ],

  camera: [
    // hook: a low sweep over the plain while Rome's host assembles, then the swing to the lone man
    { at: 0, target: [-170, 30], dist: 150, pitch: 13, yaw: 70, mm: 30 },
    { at: 'l00.together', target: [-108, 6], dist: 125, pitch: 15, yaw: 82, mm: 30, ease: 'spline' },
    { at: 'l00.And', target: [-30, -5], dist: 250, pitch: 12, yaw: 90, mm: 40, ease: 'spline' },
    { at: 'l00.today.', target: [-20, -5], dist: 255, pitch: 12, yaw: 91, mm: 40, ease: 'linear' },
    { at: 15.8, target: [-60, 0], dist: 480, pitch: 56, yaw: 90, mm: 35, ease: 'spline' },
    { at: 17.4, target: [-45, 0], width: 470, pitch: 89.9, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 22.4, target: [-45, 0], width: 440, pitch: 89.9, yaw: 0, mm: 35, ease: 'linear' },
    // Rome and the plain
    { at: 'l03.and', target: [-100, 0], dist: 200, pitch: 32, yaw: 58, mm: 35 },
    { at: 'l03.wrong?', target: [-100, 0], dist: 150, pitch: 36, yaw: 64, mm: 35, ease: 'linear' },
    { at: 'l04.On', target: [-100, 10], dist: 160, pitch: 38, yaw: 66, mm: 35 },
    { at: 'l04.river.', target: [-40, 60], width: 560, pitch: 58, yaw: 96, mm: 35, ease: 'inOut' },
    { at: 'l05.Rome', target: [-45, 0], width: 470, pitch: 86, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l06.Hannibal\'s', target: [-45, 0], width: 440, pitch: 86, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l06.curve', target: [-20, 0], width: 300, pitch: 78, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l07.His', target: [-20, 0], width: 270, pitch: 78, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l07.horsemen', target: [-35, 0], width: 400, pitch: 80, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l08.The', target: [-45, 0], width: 380, pitch: 74, yaw: 14, mm: 35, ease: 'inOut' },
    { at: 'l08.exactly', target: [-20, 0], width: 300, pitch: 62, yaw: 40, mm: 35, ease: 'inOut' },
    { at: 'l09.pushed', target: [8, 0], width: 250, pitch: 48, yaw: 62, mm: 35, ease: 'inOut' },
    { at: 'l10.Meanwhile,', target: [-40, 60], width: 340, pitch: 60, yaw: 36, mm: 35, ease: 'inOut' },
    { at: 'l10.swung', target: [-80, 40], width: 360, pitch: 64, yaw: 28, mm: 35, ease: 'inOut' },
    { at: 'l11.Now', target: [-4, 0], width: 380, pitch: 80, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l12.The', target: [4, 0], width: 340, pitch: 84, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l12.hug.', target: [8, 0], width: 300, pitch: 84, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l13.They', target: [10, 0], width: 240, pitch: 60, yaw: 20, mm: 35, ease: 'inOut' },
    { at: 'l14.By', target: [10, 0], width: 240, pitch: 44, yaw: 50, mm: 35, ease: 'inOut' },
    { at: 'l14.Rome', target: [10, 0], dist: 230, pitch: 18, yaw: 80, mm: 30, ease: 'spline' },
    { at: 'l14.history.', target: [30, 0], dist: 250, pitch: 14, yaw: 100, mm: 30, ease: 'spline' },
  ],

  labels: [
    // hook
    { at: 1.3, until: 3.9, text: '2,200 YEARS AGO', screen: [0.5, 0.17], style: 'text', big: true, size: 1.9, track: 0.16, weight: 800 },
    { at: 'l00.Rome', until: 'l00.battle.>', text: 'ROME', block: 'rome', team: 'rome', dy: -0.16, dx: -0.34, big: true },
    { at: 'l00.one', until: 12.2, text: 'ONE MAN', block: 'hannibal', team: 'carthage', dy: -0.14, dx: 0.1, big: true },
    { at: 'l00.today.', until: 15.0, text: 'STILL STUDIED TODAY', screen: [0.5, 0.84], big: true },
    // Rome and its two commanders
    { at: 'l03.Rome.', until: 'l03.commanders', text: 'ROME', block: 'rome', team: 'rome', dy: -0.12, big: true },
    { at: 'l03.commanders', until: 'l03.and', text: 'TWO COMMANDERS', block: 'rome', team: 'rome', dy: -0.3, dx: 0 },
    { at: 'l03.day', until: 'l03.What', text: 'DAY 1', pos: [-122, -22], y: 30, dy: -0.08, dx: -0.01, leader: false },
    { at: 'l03.each.', until: 'l03.What', text: 'DAY 2', pos: [-122, 22], y: 30, dy: -0.08, dx: 0.01, leader: false },
    // the plain
    { at: 'l04.August,', until: 'l04.river.', text: '2 AUGUST 216 BC', screen: [0.5, 0.12], big: true },
    { at: 'l04.flat,', until: 'l04.in', text: 'A FLAT, DUSTY PLAIN', pos: [-45, 30], dy: -0.08, leader: false },
    { at: 'l04.southern', until: 'l04.next', text: 'SOUTHERN ITALY', screen: [0.5, 0.86], big: true },
    { at: 'l04.river.', until: 'l05.Rome', text: 'RIVER AUFIDUS', pos: [-40, 166], dy: -0.1, leader: false },
    // the numbers
    { at: 'l05.bigger,', until: 'l05.push', text: 'BE BIGGER', block: 'rome', team: 'rome', dy: -0.14, big: true },
    { at: 'l05.push', until: 'l05.win.', text: 'PUSH HARD', block: 'rome', team: 'rome', dy: -0.14, big: true },
    { at: 'l05.win.', until: 'l06.Hannibal\'s', text: 'WIN', block: 'rome', team: 'rome', dy: -0.14, big: true },
    // Hannibal's plan
    { at: 'l06.weakest', until: 'l06.like', text: 'HIS WEAKEST TROOPS', block: 'carC', team: 'carthage', dx: 0.17, dy: -0.04 },
    { at: 'l06.like', until: 'l07.His', text: 'LIKE A BOW', pos: [-17, 0], dx: -0.2, dy: 0.0, team: 'carthage', big: true },
    { at: 'l07.best', until: 'l07.horsemen', text: 'HIS BEST SOLDIERS', block: 'carEN', team: 'carthage', dx: 0.18, dy: -0.02 },
    { at: 'l07.best', until: 'l07.horsemen', text: 'HIS BEST SOLDIERS', block: 'carES', team: 'carthage', dx: 0.18, dy: 0.02 },
    { at: 'l07.horsemen', until: 'l08.The', text: 'HIS HORSEMEN', block: 'carCavN', team: 'carthage', dx: 0.17, dy: -0.01 },
    { at: 'l07.horsemen', until: 'l08.The', text: 'HIS HORSEMEN', block: 'carCavS', team: 'carthage', dx: 0.17, dy: 0.01 },
    // the charge
    { at: 'l08.charged', until: 'l08.straight', text: 'THE ROMANS CHARGE', block: 'rome', team: 'rome', dy: -0.2, big: true },
    { at: 'l08.gave', until: 'l08.slowly,', text: 'THE MIDDLE GIVES WAY', block: 'carC', team: 'carthage', dx: 0.2, dy: -0.12 },
    { at: 'l08.slowly,', until: 'l08.exactly', text: 'SLOWLY, STEP BY STEP', block: 'carC', team: 'carthage', dx: 0.2, dy: 0.12 },
    { at: 'l08.exactly', until: 'l09.The', text: 'EXACTLY AS PLANNED', block: 'carC', team: 'carthage', dx: 0.2, dy: -0.12 },
    { at: 'l09.winning.', until: 'l09.They', text: 'THEY THINK THEY ARE WINNING', block: 'rome', team: 'rome', dy: -0.22, big: true },
    { at: 'l09.deeper', until: 'l10.Meanwhile,', text: 'DEEPER AND DEEPER', block: 'rome', team: 'rome', dy: -0.2, big: true },
    // the wings
    { at: 'l10.chased', until: 'l10.then', text: 'CHASED OFF', pos: [-84, 106], dy: -0.14, team: 'carthage' },
    { at: 'l10.behind', until: 'l11.Now', text: 'BEHIND THE ROMANS', pos: [-90, 0], dy: -0.16, team: 'carthage', big: true },
    { at: 'l11.left,', until: 'l12.The', text: 'LEFT', block: 'carES', team: 'carthage', dx: 0.12, dy: 0.04, big: true },
    { at: 'l11.right,', until: 'l12.The', text: 'RIGHT', block: 'carEN', team: 'carthage', dx: 0.12, dy: -0.04, big: true },
    { at: 'l11.back', until: 'l12.The', text: 'THE BACK DOOR', pos: [-70, 0], y: 18, dx: -0.14, dy: -0.12, team: 'carthage' },
    { at: 'l12.surrounded.', until: 'l12.History\'s', text: 'SURROUNDED', block: 'rome', team: 'carthage', dy: -0.24, big: true },
    { at: 'l12.least', until: 'l13.They', text: 'HISTORY\'S LEAST FUN GROUP HUG', screen: [0.5, 0.88], big: true },
    { at: 'l13.packed', until: 'l13.lift', text: 'PACKED SO TIGHTLY', block: 'rome', team: 'rome', dy: -0.2, big: true },
    { at: 'l13.lift', until: 'l14.By', text: 'NO ROOM TO LIFT A SWORD', block: 'rome', team: 'rome', dy: -0.2, big: true },
    // evening
    { at: 'l14.tens', until: 'l14.and', text: 'TENS OF THOUSANDS LOST', block: 'rome', team: 'rome', dy: -0.18, big: true },
    { at: 'l14.one', until: 'l14.It', text: 'ONE OF ITS TWO COMMANDERS', screen: [0.5, 0.86], big: true },
    { at: 'l14.worst', until: 'l15.So', text: 'ONE OF THE WORST DAYS IN ROMAN HISTORY', screen: [0.5, 0.86], big: true, size: 0.9 },
  ],

  counters: [
    { at: 'l05.80', until: 'l05.Rome\'s', block: 'rome', team: 'rome', from: 0, to: 80000, countDur: 1.1, dy: -0.16, step: 1000 },
    { at: 'l05.50', until: 'l05.Rome\'s', block: 'carC', team: 'carthage', from: 0, to: 50000, countDur: 1.1, dx: 0.14, dy: -0.14, step: 1000 },
  ],

  icons: [
    { at: 'l00.study', until: 15.0, icon: 'book', screen: [0.5, 0.64], size: 0.17, anim: 'bounce' },
    { id: 'hA', at: 'l03.commanders', until: 'l04.On', icon: 'helmet', team: 'rome', pos: [-122, -22], y: 20, size: 22, anim: 'sway' },
    { id: 'hB', at: 'l03.commanders', until: 'l04.On', icon: 'helmet', team: 'rome', pos: [-122, 22], y: 20, size: 22, anim: 'sway' },
    { at: 'l03.took', until: 'l04.On', icon: 'crown', pos: [-122, -22], y: 20, size: 14, hop: { between: ['hA', 'hB'], swaps: ['l03.each.', 'l03.What', 'l03.possibly', 'l03.go', 'l03.wrong?'], dur: 0.26, start: 0 } },
    { at: 'l03.wrong?', until: 'l04.On', icon: 'question', pos: [-122, 0], y: 36, size: 30, anim: 'bounce' },
    { at: 'l06.like', until: 'l07.His', icon: 'bow', pos: [-30, 0], y: 8, size: 40, anim: 'bounce' },
    { at: 'l07.best', until: 'l07.horsemen', icon: 'star', block: 'carEN', size: 14, anim: 'bounce' },
    { at: 'l07.best', until: 'l07.horsemen', icon: 'star', block: 'carES', size: 14, anim: 'bounce' },
    { at: 'l08.exactly', until: 'l09.The', icon: 'check', block: 'carC', size: 18, dx: 0.0, dy: -0.04 },
    { at: 'l09.winning.', until: 'l09.They', icon: 'laurel', block: 'rome', size: 18, dy: -0.08 },
    { at: 'l10.chased', until: 'l10.then', icon: 'burst', pos: [-72, 106], y: 6, size: 18 },
    { at: 'l10.chased', until: 'l10.then', icon: 'burst', pos: [-72, -106], y: 6, size: 18 },
    { at: 'l11.shut', until: 'l12.The', icon: 'door', pos: [-50, 0], y: 4, size: 22, anim: 'slam' },
    { at: 'l12.hug.', until: 'l13.They', icon: 'heart', block: 'rome', size: 34, anim: 'bounce', dy: -0.02 },
    { at: 'l13.swords.', until: 'l14.By', icon: 'sword', block: 'rome', size: 28, dy: 0.0 },
    { at: 'l13.swords.', until: 'l14.By', icon: 'no', block: 'rome', size: 34, dy: 0.0 },
    { id: 'cA', at: 'l14.one', until: 'l14.It', icon: 'helmet', team: 'rome', screen: [0.42, 0.62], size: 0.16, anim: 'sway' },
    { id: 'cB', at: 'l14.one', until: 'l14.commanders.', icon: 'helmet', team: 'rome', screen: [0.58, 0.62], size: 0.16, anim: 'sway' },
  ],

  arrows: [
    { at: 'l05.push', until: 'l05.win.', ease: 'out', team: 'rome', width: 6, path: [[-60, 0], [-12, 0]], lift: 6, hide: 'l06.Hannibal\'s' },
    { at: 'l06.bulging', until: 'l06.toward', ease: 'out', team: 'carthage', width: 4, path: [[-17, 0], [-62, 0]], lift: 6, hide: 'l07.His' },
    { at: 'l06.bow.', dur: 0.8, ease: 'out', team: 'ink', width: 1.1, head: false, path: [[6, -56], [6, 56]], lift: 6, hide: 'l07.His' },
    { at: 'l08.charged', dur: 1.2, ease: 'out', team: 'rome', width: 6, path: [[-70, 0], [-20, 0]], lift: 6, hide: 'l08.straight' },
    { at: 'l08.slowly,', dur: 0.6, ease: 'out', team: 'carthage', width: 3.4, path: [[-6, -24], [12, -24]], lift: 6, hide: 'l08.exactly' },
    { at: 'l08.slowly,', dur: 0.6, ease: 'out', team: 'carthage', width: 3.4, path: [[-6, 24], [12, 24]], lift: 6, hide: 'l08.exactly' },
    { at: 'l09.pushed', until: 'l09.gap.', ease: 'out', team: 'rome', width: 6, path: [[-10, 0], [52, 0]], lift: 6, hide: 'l10.Meanwhile,' },
    { at: 'l10.chased', dur: 0.6, ease: 'out', team: 'carthage', width: 4, path: [[-20, 104], [-70, 106]], lift: 6, hide: 'l10.then' },
    { at: 'l10.chased', dur: 0.6, ease: 'out', team: 'carthage', width: 4, path: [[-4, -104], [-70, -106]], lift: 6, hide: 'l10.then' },
    { at: 'l10.swung', until: 'l10.Romans.', ease: 'inOut', team: 'carthage', width: 3.6, style: 'dash', path: [[-100, 96], [-132, 60], [-108, 14], [-50, 22]], lift: 6, hide: 'l11.Now' },
    { at: 'l10.swung', until: 'l10.Romans.', ease: 'inOut', team: 'carthage', width: 3.6, style: 'dash', path: [[-100, -96], [-130, -58], [-104, -14], [-50, -22]], lift: 6, hide: 'l11.Now' },
    { at: 'l11.stepped', until: 'l11.ends,', ease: 'out', team: 'carthage', width: 5, path: [[22, -84], [22, -58]], lift: 6, hide: 'l12.The' },
    { at: 'l11.stepped', until: 'l11.ends,', ease: 'out', team: 'carthage', width: 5, path: [[22, 84], [22, 58]], lift: 6, hide: 'l12.The' },
    { at: 'l11.shut', dur: 0.8, ease: 'out', team: 'carthage', width: 5, path: [[-62, 0], [-38, 0]], lift: 6, hide: 'l12.The' },
    { at: 'l12.surrounded.', dur: 1.2, ease: 'inOut', team: 'gold', width: 2.2, head: false, path: [[-50, -66], [70, -66], [80, 0], [70, 66], [-50, 66], [-58, 0], [-50, -66]], smooth: true, lift: 6, hide: 'l13.They' },
  ],

  volleys: [],

  cards: [
    { at: 0, until: 1.0, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 17.4, until: 21.7, scrim: 0.9, scrimCenter: 'rgba(20,10,4,0.85)', fadeIn: 0.25, fadeOut: 0.7, lines: [
      { text: 'THE BATTLE OF CANNAE', size: 0.088, y: 0.44, delay: 0 },
      { text: '216 BC', size: 0.07, y: 0.585, delay: 1.3, colorTop: '#ffd9a0', colorBottom: '#e2873a' } ], ornaments: [{ y: 0.35, w: 0.62 }, { y: 0.68, w: 0.62 }] },
    { at: 153.43, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.13, y: 0.43, delay: 0.1, track: 0.14 },
      { text: 'The Battle of Cannae, 216 BC', size: 0.062, y: 0.6, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.5 }, { y: 0.69, w: 0.5 }] },
  ],

  insets: [
    { stage: 'med', at: 22.4, until: 33.5, rect: [0.1, 0.1, 0.8, 0.8], tilt: -1.2, in: 0.55, out: 0.45, scrim: 0.55 },
    { stage: 'med', at: 127.6, until: 170, rect: [0, 0, 1, 1], frame: false, pop: false, in: 1.2, out: 0.01 },
  ],
};
