// The Battle of Agincourt (1415): Battle Map v2 spec (engine: films/lib/battlemap/SPEC.md; scene list and reasons: NOTES.md).
// Battlefield: x east, z south, about 1 unit = 5 m. England (red) in the south facing north; France (blue) in the north facing south.
// The two woods squeeze the field in the middle (Agincourt wood west, Tramecourt wood east). The Channel map is a second stage; the same
// battlefield is baked twice (dry, then wet and brown) so the mud arrives with the night's rain. fx.js adds `rain`.
// Times come from the cue words (never l01: the ASR misspelled it); the line starts never change.
const ENG = { team: 'rome' }, FRA = { team: 'carthage' };

// ------------------------------------------------------------------ the battlefield
const hw = [[-260, 168], [-200, 140], [-150, 118], [-100, 98], [-60, 88], [20, 86], [80, 96], [140, 132], [200, 172], [270, 200]]; // half width of the open field by z
const woodPoly = (side) => { const edge = hw.map(([z, w]) => [side * w, z]); const far = side * 400; return [[far, -270], ...edge, [far, 270]]; };
const fieldWorld = (wet) => ({
  seed: 1415, size: [760, 560], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 232, elevation: 34 }, sunEve: { azimuth: 262, elevation: 6 },
  style: wet
    ? { contour: 1.5, pxPerUnit: 5.2, palette: [[-4, [0.42, 0.33, 0.21]], [1, [0.45, 0.34, 0.21]], [5, [0.48, 0.36, 0.22]], [11, [0.50, 0.40, 0.27]], [22, [0.52, 0.44, 0.35]], [40, [0.58, 0.53, 0.48]]], paletteSoft: 5, fields: 0.3, wash: 1.1 }
    : { contour: 1.5, pxPerUnit: 5.2, palette: [[-4, [0.74, 0.64, 0.42]], [1, [0.78, 0.66, 0.42]], [5, [0.80, 0.66, 0.42]], [11, [0.78, 0.64, 0.44]], [22, [0.72, 0.58, 0.42]], [40, [0.66, 0.60, 0.55]]], paletteSoft: 5, fields: 0.55 },
  features: [
    { type: 'undulate', amp: 3.2, scale: 120 }, { type: 'undulate', amp: 1.0, scale: 36 },
    { type: 'flat', at: [0, 0], r: 150, level: 1.5, soft: 60, amount: 0.95 },
    { type: 'farms', rect: [0, 0, 320, 560, 0], cell: [34, 18], skip: 0.02, kinds: 4 },
    { type: 'woods', poly: woodPoly(-1) }, { type: 'woods', poly: woodPoly(1) },
    { type: 'road', path: [[-30, 270], [-8, 160], [10, 40], [-6, -90], [8, -270]], w: 1.6, meander: 3 },
  ],
});
const fieldAmbient = (wet) => ({
  wind: wet ? [1.4, 0.5] : [1.1, 0.35], gusts: wet ? 0.3 : 0.6,
  camps: [{ pos: [30, 205], size: [56, 30], team: 'rome', style: 'scatter', tents: 18, fires: 3, people: 12, palisade: false },
    { pos: [-10, -232], size: [90, 34], team: 'carthage', style: 'grid', fires: 4, people: 16 }],
  walkers: [{ path: [[-30, 270], [-8, 160], [-2, 130]], n: 3, gap: 5, speed: 1.1, kind: 'light', team: 'neutral', until: 'l07' },
    { path: [[8, -270], [2, -200]], n: 3, gap: 5, speed: 1.0, kind: 'light', team: 'neutral', offset: 12 }],
  smoke: [{ pos: [30, 205], n: 8, alpha: 0.14, height: 8 }, { pos: [-10, -232], n: 10, alpha: 0.16, height: 9 },
    ...(wet ? [{ pos: [0, -48], n: 14, alpha: 0.2, height: 10, at: 'l12' }, { pos: [-40, -60], n: 8, alpha: 0.16, height: 8, at: 'l13' }] : [])],
  birds: [{ center: [-170, -60], r: 40, h: 26, n: 7, speed: 6 }, { center: [180, 30], r: 36, h: 24, n: 6, speed: 5, dir: -1 }, { path: [[-300, 120], [300, -100]], n: 4, h: 36, speed: 8 }],
});

// ------------------------------------------------------------------ the Channel map (England, the sea, northern France), 1 unit about 1.2 km
const channel = {
  world: {
    seed: 1415, size: [640, 460], res: 1, base: 0, meshStep: 2.0, sun: { azimuth: 250, elevation: 32 }, sunEve: { azimuth: 284, elevation: 10 },
    style: { contour: 4, pxPerUnit: 7, palette: [[-4, [0.62, 0.72, 0.46]], [3, [0.74, 0.76, 0.48]], [14, [0.80, 0.70, 0.46]], [30, [0.72, 0.58, 0.42]], [48, [0.70, 0.66, 0.62]], [66, [0.95, 0.95, 0.96]]], paletteSoft: 5 },
    features: [
      { type: 'undulate', amp: 4, scale: 90 },
      { type: 'sea', poly: [[-400, -300], [400, -300], [400, 300], [-400, 300]], shelf: 34, depth: 8 },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-330, -5], [-290, -8], [-261, -9], [-232, -20], [-200, -32], [-170, -38], [-140, -52], [-122, -58], [-95, -58], [-66, -60], [-44, -52], [-15, -60], [10, -75], [18, -86], [26, -109], [40, -118], [70, -128], [95, -150], [140, -240], [-330, -240]] },
      { type: 'land', wob: 2.2, shelf: 16, poly: [[-330, 60], [-285, 52], [-255, 38], [-220, 44], [-185, 60], [-160, 48], [-140, 38], [-133, 46], [-125, 62], [-110, 76], [-92, 84], [-74, 86], [-60, 80], [-50, 72], [-46, 66], [-40, 48], [-25, 34], [5, 25], [21, 13], [34, 2], [36, -25], [35, -49], [49, -69], [79, -77], [100, -86], [133, -102], [330, -110], [330, 240], [-330, 240]] },
      { type: 'river', name: 'Seine', path: [[-48, 76], [-20, 110], [30, 150], [70, 240]], w: 4, depth: 1.5, meander: 6 },
      { type: 'river', name: 'Somme', path: [[34, 4], [60, 24], [110, 40], [170, 62], [260, 70]], w: 3, depth: 1.2, meander: 5 },
      { type: 'hill', at: [-200, -90], r: [50, 26], h: 14, rot: 10 }, { type: 'hill', at: [120, 120], r: [60, 40], h: 12 },
      { type: 'woods', at: [-110, 120], r: [40, 16] }, { type: 'woods', at: [80, 90], r: [34, 14], rot: 20 }, { type: 'woods', at: [-70, -150], r: [50, 16], rot: -8 },
      { type: 'farms', rect: [30, 80, 110, 60, 8], cell: [14, 10] }, { type: 'farms', rect: [-190, -130, 100, 50, -6], cell: [14, 10] },
      { type: 'road', path: [[-48, 70], [-20, 30], [10, 8], [38, -20], [49, -66]], w: 1.4, meander: 4 },
    ],
  },
  ambient: { wind: [1, 0.3], gusts: 0.4, flow: { dir: [1, 0.15], speed: 0.6, glint: 1.2 },
    birds: [{ center: [-90, 0], r: 30, h: 20, n: 6, speed: 5 }, { center: [80, -90], r: 26, h: 20, n: 5, speed: 5, dir: -1 }],
    smoke: [{ pos: [-52, 74], n: 8, alpha: 0.18, height: 7, at: 'l02.captured' }],
    walkers: [{ path: [[-48, 70], [-20, 30], [10, 8], [38, -20], [49, -66]], n: 4, gap: 5, speed: 1.0, kind: 'light', team: 'neutral' }] },
  blocks: {
    hen: { ...ENG, kind: 'infantry', x: -128, z: -62, heading: 150, len: 20, dep: 9, hidden: true, bannerScale: 1.4, figScale: 1.4 },
    frBlock: { ...FRA, kind: 'infantry', x: 60, z: -38, heading: 200, len: 36, dep: 12, hidden: true, bannerScale: 1.4, figScale: 1.4 },
    henT: { ...ENG, kind: 'elite', x: 52, z: 196, heading: 0, len: 14, dep: 8, hidden: true, bannerScale: 1.6, figScale: 1.4 },
  },
  moves: [
    { block: 'hen', at: 'l02.Henry', dur: 0.9, appear: true },
    { block: 'hen', at: 'l02.invaded', dur: 2.4, path: [[-110, -30], [-84, 6], [-60, 40], [-38, 58]], ease: 'cam' },
    { block: 'hen', at: 'l02.sick.', dur: 1.2, fadeTo: 0.45, alphaTo: 0.9 },
    { block: 'hen', at: 'l02.Very,', dur: 1.4, fadeTo: 0.75, alphaTo: 0.85 },
    { block: 'hen', at: 'l03.march', dur: 4.6, path: [[-30, 42], [4, 14], [26, -2], [40, -14]], ease: 'cam' },
    { block: 'frBlock', at: 'l03.French#1', dur: 0.9, appear: true },
    { blocks: ['hen', 'frBlock'], at: 'l04', dur: 0.5, vanish: true },
    { block: 'henT', at: 'l16.marry', dur: 0.9, appear: true },
  ],
  arrows: [
    { id: 'cross', at: 'l02.invaded', until: 'l02.crown.>', ease: 'cam', team: 'rome', style: 'dash', width: 2.2, path: [[-128, -58], [-110, -30], [-84, 6], [-60, 40], [-48, 62]], lift: 4, hide: 'l02.He' },
    { at: 'l03.march', until: 'l03.home.>', ease: 'cam', team: 'rome', style: 'dash', width: 2.2, path: [[-40, 60], [-30, 42], [4, 14], [28, -4], [44, -24], [52, -56]], lift: 4, hide: 'l04' },
  ],
  labels: [
    { at: 'l02.England', until: 'l02.He', text: 'ENGLAND', pos: [-170, -70], leader: false, rule: false, team: 'rome' },
    { at: 'l02.France', until: 'l02.He', text: 'FRANCE', pos: [0, 92], leader: false, rule: false, team: 'carthage' },
    { at: 'l02.King', until: 'l02.invaded', text: 'KING HENRY V', block: 'hen', team: 'rome', dx: -0.06, dy: -0.12 },
    { at: 'l15.Shakespeare', until: 'l16', text: 'HENRY V, BY WILLIAM SHAKESPEARE, ABOUT 1599', screen: [0.5, 0.86], big: true },
    { at: 'l15.Almost', until: 'l16', text: 'LONDON', pos: [-30, -128], y: 2, team: 'rome', dx: 0.08, dy: -0.08 },
    { at: 'l16.marry', until: 'l16.And#1', text: 'TROYES, 1420', block: 'henT', team: 'rome', dx: 0.1, dy: -0.1 },
  ],
  icons: [
    { follow: 'cross', at: 'l02.invaded', until: 'l02.captured', icon: 'galley', team: 'rome', size: 18, minPx: 0.045, maxPx: 0.065 },
  ],
  rain: [{ at: 'l16.always', until: 160, density: 1.0, fadeIn: 1.2 }],
  light: [{ at: 'l16.And#1', dur: 2.4, to: { cloud: 0.85 }, ease: 'inOut' }],
};

// ------------------------------------------------------------------ the battle (shared by the dry and the wet stage)
const FR = ['fr.0.0', 'fr.1.0', 'fr.2.0', 'fr.3.0', 'fr.4.0'];     // the rear rank (France faces south, so rank 2 is the front)
const ENGL = ['engW', 'engC', 'engE'];
const ZZ = (z) => Array.from({ length: 43 }, (_, i) => [-84 + i * 4, z + (i % 2 ? 1.6 : -1.6)]); // a row of stakes across the English front
const battle = {
  blocks: {
    engW: { ...ENG, kind: 'archers', x: -56, z: 96, heading: 0, len: 46, dep: 12, hidden: true, banner: false },
    engC: { ...ENG, kind: 'elite', x: 0, z: 104, heading: 0, len: 52, dep: 14, hidden: true, bannerScale: 1.6, count: 8000 },
    engE: { ...ENG, kind: 'archers', x: 56, z: 96, heading: 0, len: 46, dep: 12, hidden: true, banner: false },
    fr: { ...FRA, kind: 'infantry', x: 0, z: -140, heading: 180, len: 190, dep: 66, grid: { cols: 5, ranks: 3, gap: 3 }, hidden: true, bannerScale: 0.9 },
    frCavW: { ...FRA, kind: 'cavalry', x: -62, z: -94, heading: 180, len: 44, dep: 16, hidden: true },
    frCavE: { ...FRA, kind: 'cavalry', x: 62, z: -94, heading: 180, len: 44, dep: 16, hidden: true },
  },

  moves: [
    // S1: England's small army, then France's huge host rises block by block; both leave under the title card
    { block: 'engC', at: 'l00.small,', dur: 0.9, appear: true },
    { group: 'fr', at: 'l00.biggest', dur: 0.8, stagger: 0.12, appear: true },
    { blocks: ['engC', 'fr'], at: 13.3, dur: 0.5, vanish: true },
    // S3: both armies take their places; the knights on France's wings
    { blocks: ENGL, at: 'l04.armies', dur: 0.8, stagger: 0.15, appear: true },
    { group: 'fr', at: 'l04.faced', dur: 0.8, stagger: 0.08, appear: true },
    { blocks: ['frCavW', 'frCavE'], at: 'l05.knights', dur: 0.8, stagger: 0.2, appear: true },
    // S4: the whole line walks forward to bowshot (the stakes are the zigzag ink lines in `arrows`)
    { blocks: ENGL, at: 'l07.moved', dur: 3.2, by: { z: -120 }, ease: 'cam' },
    // S5: the cavalry charge: fast, slowed and sinking in the mud, stopped short of the stakes, turned back into their own lines
    { block: 'frCavW', at: 'l09.horseback', dur: 1.9, to: { z: -72 }, ease: 'inQuad' },
    { block: 'frCavE', at: 'l09.horseback+0.12', dur: 1.9, to: { z: -72 }, ease: 'inQuad' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.mud', dur: 1.8, to: { z: -54 }, ease: 'out' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.mud', dur: 1.6, to: { sink: 0.6 }, ease: 'out' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.stopped', dur: 0.4, fadeTo: 0.3, alphaTo: 0.9 },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.turned', dur: 0.8, to: { heading: 0 }, ease: 'cam' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.galloped', dur: 1.6, to: { z: -112, sink: 0 }, ease: 'inQuad' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.side.', dur: 0.9, vanish: true },
    // S6: France on foot: steady at first, slower in the mud, sinking to the knees; the woods squeeze them, they pack tight
    { group: 'fr', at: 'l10.Then', dur: 3.0, by: { z: 24 }, ease: 'cam' },
    { group: 'fr', at: 'l10.through', dur: 3.6, by: { z: 18 }, ease: 'out' },
    { group: 'fr', at: 'l10.through', dur: 1.2, to: { sink: 0.5 }, ease: 'out' },
    { group: 'fr', at: 'l10.up', dur: 1.4, to: { sink: 0.85 }, ease: 'out' },
    { group: 'fr', at: 'l11.squeezed', dur: 2.6, squeeze: { about: [0, -98], kx: 0.72, kz: 1, lenK: 0.72, depK: 1.1 }, ease: 'inOut' },
    { group: 'fr', at: 'l11.squeezed', dur: 2.6, by: { z: 4 }, ease: 'inOut' },
    { group: 'fr', at: 'l11.packed', dur: 2.0, squeeze: { about: [0, -92], kx: 0.82, kz: 1, lenK: 0.9, depK: 1.05 }, ease: 'inOut' },
    // S7: they reach the line exhausted; the archers wheel in on both flanks; the back pushes the front
    { group: 'fr', at: 'l12.reached', dur: 1.8, by: { z: 22 }, ease: 'cam' },
    { block: 'engW', at: 'l12.joined', dur: 1.4, to: { x: -66, z: -52, heading: 40 }, ease: 'cam' },
    { block: 'engE', at: 'l12.joined', dur: 1.4, to: { x: 66, z: -52, heading: 320 }, ease: 'cam' },
    { blocks: FR, at: 'l13.pushing', dur: 1.6, by: { z: 16 }, ease: 'cam' },
    { group: 'fr', at: 'l13.chaos.', dur: 1.2, squeeze: { about: [0, -60], kx: 0.94, kz: 0.9, lenK: 0.96, depK: 0.9 }, ease: 'inOut' },
    // S8: within a few hours: France thins by numbers (never wounds), England loses a few hundred
    { group: 'fr', at: 'l14.Thousands', dur: 3.4, stagger: 0.16, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.95 },
    { blocks: ENGL, at: 'l14.lost', dur: 1.0, fadeTo: 0.12, alphaTo: 0.95 },
  ],

  arrows: [
    // the stakes: a zigzag ink line (the map symbol for a row of stakes), hammered in from west to east, then planted again at bowshot
    { at: 'l07.hammered', until: 'l07.them.>', ease: 'linear', team: 'ink', width: 1.6, taper: 1, head: false, smooth: false, path: ZZ(86), lift: 3, hide: 'l07.moved' },
    { at: 'l07.shoot.', dur: 0.9, ease: 'out', team: 'ink', width: 1.6, taper: 1, head: false, smooth: false, path: ZZ(-36), lift: 3, hide: 'l15' },
    { at: 'l07.moved', until: 'l07.close', ease: 'cam', team: 'rome', width: 4, path: [[0, 76], [0, 4]], lift: 5, hide: 'l07.shoot.' },
    { at: 'l07.moved', until: 'l07.close', ease: 'cam', team: 'rome', width: 4, path: [[-56, 70], [-56, -2]], lift: 5, hide: 'l07.shoot.' },
    { at: 'l07.moved', until: 'l07.close', ease: 'cam', team: 'rome', width: 4, path: [[56, 70], [56, -2]], lift: 5, hide: 'l07.shoot.' },
    { at: 'l09.horseback', until: 'l09.mud', ease: 'out', team: 'carthage', width: 4, path: [[-62, -98], [-62, -60]], lift: 5, hide: 'l09.stopped' },
    { at: 'l09.horseback+0.12', until: 'l09.mud', ease: 'out', team: 'carthage', width: 4, path: [[62, -98], [62, -60]], lift: 5, hide: 'l09.stopped' },
    { at: 'l09.galloped', dur: 0.9, ease: 'out', team: 'carthage', width: 3.4, style: 'dash', path: [[-62, -56], [-66, -100]], lift: 5, hide: 'l10' },
    { at: 'l09.galloped', dur: 0.9, ease: 'out', team: 'carthage', width: 3.4, style: 'dash', path: [[62, -56], [66, -100]], lift: 5, hide: 'l10' },
    { at: 'l10.Then', until: 'l10.foot.', ease: 'cam', team: 'carthage', width: 5, path: [[0, -100], [0, -66]], lift: 6, hide: 'l10.through' },
    { at: 'l11.squeezed', dur: 1.2, ease: 'out', team: 'ink', width: 2.4, path: [[-120, -100], [-90, -98]], lift: 8, hide: 'l11.They' },
    { at: 'l11.squeezed', dur: 1.2, ease: 'out', team: 'ink', width: 2.4, path: [[120, -100], [90, -98]], lift: 8, hide: 'l11.They' },
    { at: 'l12.joined', dur: 1.0, ease: 'out', team: 'rome', width: 4, path: [[-58, -28], [-66, -48]], lift: 6, hide: 'l13' },
    { at: 'l12.joined', dur: 1.0, ease: 'out', team: 'rome', width: 4, path: [[58, -28], [66, -48]], lift: 6, hide: 'l13' },
    { at: 'l13.pushing', until: 'l13.front,', ease: 'out', team: 'carthage', width: 4, path: [[0, -118], [0, -86]], lift: 7, hide: 'l14' },
  ],

  volleys: [
    { at: 'l08.Thousands', dur: 1.0, from: { block: 'engW' }, to: [-30, -120, 40], n: 48, flight: 1.5, arc: 44, team: 'rome' },
    { at: 'l08.Thousands+0.15', dur: 1.0, from: { block: 'engE' }, to: [30, -120, 40], n: 48, flight: 1.5, arc: 44, team: 'rome' },
    { at: 'l08.went', dur: 1.2, from: { block: 'engW' }, to: [-40, -126, 46], n: 56, flight: 1.5, arc: 48, team: 'rome' },
    { at: 'l08.went+0.15', dur: 1.2, from: { block: 'engE' }, to: [40, -126, 46], n: 56, flight: 1.5, arc: 48, team: 'rome' },
    { at: 'l08.came', dur: 1.3, from: { block: 'engW' }, to: [-20, -128, 52], n: 56, flight: 1.4, arc: 44, team: 'rome' },
    { at: 'l08.came', dur: 1.3, from: { block: 'engE' }, to: [20, -128, 52], n: 56, flight: 1.4, arc: 44, team: 'rome' },
  ],

  labels: [
    { at: 1.39, until: 3.6, text: '1415', screen: [0.5, 0.16], big: true },
    { at: 'l04.On', until: 'l04.faced', text: '25 OCTOBER 1415', screen: [0.5, 0.86], big: true },
    { at: 'l05.Henry', until: 'l05.Most', text: 'KING HENRY V', block: 'engC', team: 'rome', dx: 0.12, dy: -0.12 },
    { at: 'l09.stakes', until: 'l09.Their', text: 'STAKES', pos: [-40, -36], y: 1, dx: 0.1, dy: -0.1 },
  ],

  counters: [
    { at: 'l05.8', until: 'l05.Most', block: 'engC', team: 'rome', from: 0, to: 8000, countDur: 1.0, step: 100, suffix: 'MEN', dx: -0.12, dy: -0.12 },
  ],

  icons: [],

  rain: [
    { at: 'l00.soaking', until: 'l00.Spoiler,', density: 0.9 },
    { at: 'l06.rained', until: 'l07.The', density: 1.3 },
  ],
};
const wetMarkers = [
  { id: 'aginW', at: 'l11.woods', until: 'l12', pos: [-130, -100], glyph: 'woods', letter: 'C', label: 'AGINCOURT WOOD', labelDur: 2.6, size: 0.05 },
  { id: 'tramW', at: 'l11.woods', until: 'l12', pos: [130, -100], glyph: 'woods', letter: 'D', label: 'TRAMECOURT WOOD', labelDur: 2.6, size: 0.05 },
];

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.30 } },
  world: fieldWorld(false),
  ...battle,
  ambient: fieldAmbient(false),
  stages: { chan: channel, wet: { world: fieldWorld(true), ...battle, ambient: fieldAmbient(true), markers: wetMarkers } },

  // ------------------------------------------------------------------ scenes: sets and pre-planned cameras (the edit)
  scenes: [
    { id: 'S1', name: 'The odds', at: 0, job: 'a small, sick, soaked army against one of France\'s biggest; spoiler: the mud', set: { time: 0.15, haze: 1.35, cloud: 0.8 },
      shots: [
        { at: 0, why: 'cold open low behind the small English army in the rain: who we follow, and how small', from: { target: [0, 94], dist: 150, pitch: 14, yaw: -4, mm: 30 },
          moves: [{ until: 'l00.face', to: { dist: 128, pitch: 15, yaw: 2 } }] },
        { at: 'l00.one', why: 'change of scale: high and wide, France\'s host rises across the field', from: { target: [0, -30], width: 460, pitch: 36, yaw: 0, mm: 35 },
          moves: [{ until: 'l00.France.>', to: { target: [0, -46], width: 480 } }] },
        { at: 'l00.Spoiler,', why: 'crane up to the field from above: the place that will decide it (under the title)', from: { target: [0, 10], width: 340, pitch: 30, yaw: 40, mm: 35 },
          moves: [{ until: 17.6, to: { width: 600, pitch: 82, yaw: 0 }, ease: 'camLong' }] },
      ] },
    { id: 'S2', name: 'The road to Calais', at: 'l02', stage: 'chan', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'why Henry is in France, and why his army is small, sick and trapped', set: { time: 0.08, haze: 1.0, cloud: 0.3 },
      shots: [
        { at: 'l02', why: 'change of world: the Channel map, Henry crosses from England to claim the crown', from: { target: [-92, -14], width: 380, pitch: 56, yaw: 0, mm: 35 },
          moves: [{ until: 'l02.crown.>', to: { target: [-70, 18], width: 360 } }] },
        { at: 'l02.He', why: 'closer on the port he takes; hold on the sickness and the bushes', from: { target: [-46, 60], width: 230, pitch: 50, yaw: 10, mm: 35 },
          moves: [{ until: 'l02.sick.#1>', to: { target: [-42, 58], width: 206 } }] },
        { at: 'l03', why: 'wider: follow the march north toward Calais and home', from: { target: [-12, 30], width: 380, pitch: 58, yaw: 0, mm: 35 },
          moves: [{ until: 'l03.home.>', to: { target: [18, -8], width: 360 } }] },
        { at: 'l03.The#1', why: 'closer on the road ahead: the French army blocks it', from: { target: [44, -34], width: 230, pitch: 46, yaw: 20, mm: 35 },
          moves: [{ until: 'l04', to: { width: 212 } }] },
      ] },
    { id: 'S3', name: 'The field', at: 'l04', transition: { type: 'dissolve', dur: 0.8 }, job: 'where and how many: a ploughed field between two woods; 8,000 mostly archers against far more, many knights', set: { time: 0.05, haze: 1.1, cloud: 0.35 },
      shots: [
        { at: 'l04', why: 'change of world, back on the field: establish it from the English side as both armies take their places', from: { target: [0, -10], width: 540, pitch: 40, yaw: 0, mm: 35 },
          moves: [{ until: 'l04.other>', to: { target: [0, -20], width: 500 } }] },
        { at: 'l04.freshly', why: 'top down: the ploughed field and the two woods that pinch it', from: { target: [0, -10], width: 480, pitch: 86, yaw: 0, mm: 35 },
          moves: [{ until: 'l04.sides.>', to: { width: 520 } }] },
        { at: 'l05', why: 'low behind the English: Henry, his 8,000, archers on both wings', from: { target: [0, 80], dist: 180, pitch: 22, yaw: -10, mm: 35 },
          moves: [{ until: 'l05.bows.>', to: { dist: 162, yaw: 2 } }] },
        { at: 'l05.The', why: 'reverse, high behind the French looking south: far more, knights on the wings; the field the rain will soak', from: { target: [0, -60], dist: 300, pitch: 32, yaw: 180, mm: 35 },
          moves: [{ until: 'l05.armor.>', to: { dist: 282 } }] },
      ] },
    { id: 'S4', name: 'Rain and stakes', at: 'l06', stage: 'wet', inset: 'full', transition: { type: 'dissolve', dur: 1.8 }, job: 'overnight the field turns to mud; the English stake their line and walk to bowshot', set: { time: 0.1, haze: 1.45, cloud: 0.8 },
      shots: [
        { at: 'l06', why: 'change of time, the same view from the French side: the night\'s rain turns the field to mud', from: { target: [0, 0], width: 520, pitch: 46, yaw: 180, mm: 35 },
          moves: [{ until: 'l06.mud.>', to: { width: 470, pitch: 52 } }] },
        { at: 'l07', why: 'low along the English line: the stakes go in, a wave from west to east', from: { target: [-30, 86], dist: 96, pitch: 12, yaw: 80, mm: 40 },
          moves: [{ until: 'l07.them.>', to: { target: [-6, 86], dist: 90 } }] },
        { at: 'l07.Then', why: 'high from the west: the whole line and its stakes walk forward to bowshot', from: { target: [0, 46], dist: 270, pitch: 34, yaw: 90, mm: 35 },
          moves: [{ until: 'l07>', to: { target: [0, 6] } }] },
      ] },
    { id: 'S5', name: 'Arrows and horses', at: 'l07>', stage: 'wet', inset: 'full', job: 'the arrows fall; the knights charge, the mud slows them, the stakes stop them, they flee into their own lines', set: { time: [0.1, 0.18], haze: 1.3, cloud: 0.6 },
      shots: [
        { at: 'l07>', why: 'out of the mud insert, top down: the consequence, the line now forward behind its stakes; the first volley rises', from: { target: [0, -40], width: 420, pitch: 82, yaw: 0, mm: 35 },
          moves: [{ until: 'l08.came', to: { target: [0, -56], width: 400 } }] },
        { at: 'l08.came', why: 'low from the French side under the falling arrows', from: { target: [0, -100], dist: 124, pitch: 14, yaw: 186, mm: 35 },
          moves: [{ until: 'l09', to: { dist: 112 } }] },
        { at: 'l09', why: 'high from the east: both wings of knights charge', from: { target: [0, -72], dist: 280, pitch: 36, yaw: 270, mm: 35 },
          moves: [{ until: 'l09.charged,>', to: { target: [0, -64], dist: 268 } }] },
        { at: 'l09.but', why: 'closer and low behind the west wing: the mud slows them, the stakes stop them', from: { target: [-60, -48], dist: 104, pitch: 16, yaw: 162, mm: 35 },
          moves: [{ until: 'l09.them.#1>', to: { dist: 94 } }] },
        { at: 'l09.Their', why: 'high and wide: the horses gallop back into their own lines; the ground the rest must now cross', from: { target: [0, -90], width: 400, pitch: 64, yaw: 0, mm: 35 },
          moves: [{ until: 'l09.side.>', to: { width: 380 } }] },
      ] },
    { id: 'S6', name: 'The funnel', at: 'l10', stage: 'wet', inset: 'full', job: 'the French on foot in mud to the knees; the woods squeeze them', set: { time: 0.18, haze: 1.25 },
      shots: [
        { at: 'l10', why: 'low beside the French front, France left, England right: they slow and sink as they come', from: { target: [-30, -84], dist: 112, pitch: 13, yaw: 90, mm: 40 },
          moves: [{ until: 'l10.knees.>', to: { target: [-30, -66], dist: 106 } }] },
        { at: 'l11', why: 'high behind the English stakes, a slow rise: the woods squeeze the column into the neck', from: { target: [0, -84], dist: 220, pitch: 32, yaw: 0, mm: 35 },
          moves: [{ until: 'l11>', to: { pitch: 44, dist: 232 }, ease: 'camLong' }] },
      ] },
    { id: 'S7', name: 'The crush', at: 'l11>', stage: 'wet', inset: 'full', climax: true, job: 'exhausted, they reach the line; the archers join in; the rear pushes the front: chaos', set: { time: [0.2, 0.3], haze: 1.25 },
      shots: [
        { at: 'l11>', why: 'out of the funnel insert, the decisive moment wide and from above: the packed mass reaches the stakes', from: { target: [0, -58], width: 360, pitch: 86, yaw: 0, mm: 35 },
          moves: [{ until: 'l12.and', to: { width: 336 } }] },
        { at: 'l12.and', why: 'closer and low on the west flank: how it worked, the archers drop their bows and wheel in', from: { target: [-56, -50], dist: 112, pitch: 18, yaw: 58, mm: 35 },
          moves: [{ until: 'l12.in.>', to: { yaw: 72, dist: 102 }, ease: 'camSoft' }] },
        { at: 'l13', why: 'behind the French rear over the press: the back ranks push into the front', from: { target: [0, -78], dist: 144, pitch: 22, yaw: 180, mm: 35 },
          moves: [{ until: 'l13.chaos.>', to: { dist: 128 } }] },
      ] },
    { id: 'S8', name: 'The cost', at: 'l14', stage: 'wet', inset: 'full', job: 'over in a few hours: thousands of French killed or captured, a few hundred English', set: { time: [0.4, 1.0], haze: [1.2, 1.35] },
      shots: [
        { at: 'l14', why: 'a long pull back as the sun goes down: the French ranks thin', from: { target: [0, -60], dist: 160, pitch: 18, yaw: 30, mm: 35 },
          moves: [{ until: 'l14.France.>', to: { dist: 250, pitch: 30, yaw: 46 }, ease: 'camLong' }] },
        { at: 'l14.The#1', why: 'cut on the line: low on the English standard, nearly whole', from: { target: [0, -18], dist: 84, pitch: 12, yaw: 196, mm: 40 },
          moves: [{ until: 'l14>', to: { dist: 78 } }] },
      ] },
    { id: 'S9', name: 'After', at: 'l15', stage: 'chan', inset: 'full', transition: { type: 'dissolve', dur: 1.0 }, job: 'a famous play, a marriage, an heir to France, and a lesson', set: { time: [0.2, 0.3], haze: 1.0, cloud: 0.35 },
      shots: [
        { at: 'l15', why: 'change of time and world: two centuries on, toward England and the play', from: { target: [-60, -76], width: 420, pitch: 58, yaw: 0, mm: 35 },
          moves: [{ until: 'l15.play.>', to: { target: [-46, -96], width: 380 } }] },
        { at: 'l16', why: 'across to France: Henry at Troyes, married and named heir', from: { target: [40, 160], width: 380, pitch: 56, yaw: 0, mm: 35 },
          moves: [{ until: 'l16.France.>', to: { target: [46, 172], width: 350 } }] },
        { at: 'l16.And#1', why: 'pull back over northern France as the cloud rolls in: the lesson arrives as rain', from: { target: [0, 40], width: 520, pitch: 62, yaw: 0, mm: 35 },
          moves: [{ until: 146.8, to: { width: 600, pitch: 72 }, ease: 'camLong' }] },
      ] },
  ],

  // ------------------------------------------------------------------ the legend (motion-graphics frame)
  legend: {
    title: { text: 'BATTLE OF AGINCOURT', sub: '25 October 1415', at: 'l02' },
    show: [['l02', 'l16.weather.>']],
    sides: [
      { id: 'england', team: 'rome', name: 'ENGLAND', commander: 'King Henry V', commanderAt: 'l02.England', banner: 'banner', at: 'l02.England', strength: 8000, strengthAt: 'l05.8', strengthLabel: 'MEN, ABOUT' },
      { id: 'france', team: 'carthage', name: 'FRANCE', commander: 'Constable d\'Albret', commanderAt: 'l03.French#1', banner: 'banner', at: 'l02.France', dimAt: 'l14.Thousands' },
    ],
    key: { show: [['l02.port', 'l03>'], ['l04', 'l14']] },
    units: [
      { id: 'arch', kind: 'archers', name: 'Archers', team: 'rome', at: 'l05.archers' },
      { id: 'kn', kind: 'cavalry', name: 'Knights', team: 'carthage', at: 'l05.knights' },
      { id: 'foot', kind: 'infantry', name: 'Foot soldiers', teams: ['rome', 'carthage'], at: 'l10.soldiers' },
    ],
    places: [
      { id: 'harfleur', letter: 'A', glyph: 'town', name: 'Harfleur', at: 'l02.port', pos: [-52, 74], y: 2, stage: 'chan', label: 'HARFLEUR', team: 'carthage' },
      { id: 'calais', letter: 'B', glyph: 'town', name: 'Calais', at: 'l03.Calais,', pos: [54, -64], y: 2, stage: 'chan', label: 'CALAIS', team: 'rome' },
      { id: 'agin', letter: 'C', glyph: 'woods', name: 'Agincourt wood', at: 'l04.woods', pos: [-132, -40], label: 'AGINCOURT WOOD' },
      { id: 'tram', letter: 'D', glyph: 'woods', name: 'Tramecourt wood', at: 'l04.both', pos: [132, -40], label: 'TRAMECOURT WOOD' },
    ],
    focus: [
      { entry: 'arch', at: 'l05.archers', until: 'l05.The' }, { entry: 'kn', at: 'l05.knights', until: 'l06' },
      { entry: 'kn', at: 'l09.knights', until: 'l09.but' }, { entry: 'arch', at: 'l12.archers', until: 'l13' },
      { entry: 'england', at: 'l14.English', until: 'l15' }, { entry: 'england', at: 'l16.heir', until: 'l16.And#1' },
    ],
    scale: { unitM: 5, show: [['l04', 'l05>']] },
  },

  cards: [
    { at: 0, until: 0.8, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 12.95, until: 16.3, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF AGINCOURT', size: 0.074, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
      { text: '1415', size: 0.056, y: 0.575, delay: 1.0, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.5 }, { y: 0.65, w: 0.5 }] },
    { at: 143.078, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.8, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Agincourt, 1415', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],
};
