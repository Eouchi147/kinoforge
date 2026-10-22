// The Battle of Waterloo (18 June 1815): Battle Map v2 spec (see films/lib/battlemap/SPEC.md, the reference film films/battles/cannae/,
// and NOTES.md here for the scene list). Times come from the cue words; the line starts never change (the sound is re-scored around them).
// Map: x east, z south, 1 unit about 8 m. Brussels and Waterloo are north (-z), the French are south (+z). Wellington's ridge runs east to
// west at z -34, the French ridge at z 124, the Brussels road north to south along x 0. French blue (carthage), Wellington's army red
// (rome), Prussians green. Film-side: `artillery` figures and the `tricolore` and `brig` glyphs (units.js, registered in index.html).
const FR = { team: 'carthage' }, BR = { team: 'rome' }, PR = { team: 'green' };

// ------------------------------------------------------------------ the battlefield
const world = {
  seed: 1815, size: [900, 580], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 215, elevation: 34 }, sunEve: { azimuth: 282, elevation: 12 },
  style: { contour: 1.5, pxPerUnit: 4.6, palette: [[-4, [0.66, 0.74, 0.46]], [1, [0.78, 0.80, 0.48]], [6, [0.80, 0.76, 0.46]], [13, [0.78, 0.66, 0.42]], [22, [0.72, 0.58, 0.42]], [40, [0.66, 0.60, 0.55]]], paletteSoft: 5 },
  features: [
    { type: 'undulate', amp: 4, scale: 130 }, { type: 'undulate', amp: 1.4, scale: 38 },
    { type: 'ridge', path: [[-470, -30], [-330, -36], [-190, -38], [-60, -34], [40, -32], [150, -34], [300, -30], [470, -22]], w: 52, h: 26, rough: 0.2, meander: 4 },
    { type: 'ridge', path: [[-470, 128], [-300, 120], [-120, 124], [40, 120], [200, 126], [470, 118]], w: 60, h: 11, rough: 0.2, meander: 6 },
    { type: 'hill', at: [250, 190], r: [34, 26], h: 7, rot: 20 },
    { type: 'river', name: 'Dyle', path: [[432, -300], [438, -100], [426, 100], [434, 300]], w: 9, depth: 2.4, meander: 6, wl: 38 },
    { type: 'woods', at: [-112, 4], r: [12, 18] }, { type: 'woods', at: [0, -262], r: [330, 24] }, { type: 'woods', at: [300, 220], r: [24, 16] }, { type: 'woods', at: [-340, 70], r: [26, 20] }, { type: 'woods', at: [380, -170], r: [30, 22] },
    { type: 'farms', rect: [-250, 50, 210, 60, 3], cell: [18, 12] }, { type: 'farms', rect: [-250, -130, 260, 70, 2], cell: [18, 12] }, { type: 'farms', rect: [240, -130, 240, 70, -2], cell: [18, 12] },
    { type: 'farms', rect: [-40, 196, 300, 50, 1], cell: [18, 12] }, { type: 'farms', rect: [80, -12, 110, 22, 0], cell: [10, 9] },   // the tall corn in front of the centre right
    { type: 'farms', rect: [-90, 16, 22, 18, 0], cell: [7, 6] }, { type: 'farms', rect: [14, 34, 18, 14, 0], cell: [6, 5] },           // Hougoumont and La Haye Sainte yards
    { type: 'road', path: [[2, -295], [8, -190], [5, -100], [3, -36], [-1, 40], [-4, 120], [4, 200], [-2, 295]], w: 3.2, meander: 3 },
    { type: 'road', path: [[-470, -32], [-330, -38], [-190, -40], [-60, -36], [40, -34], [150, -36], [300, -32], [470, -24]], w: 1.5, meander: 2 },
    { type: 'road', path: [[470, -60], [380, -80], [300, -40], [270, 40], [250, 140], [230, 220]], w: 1.6, meander: 4 },               // the Prussians' lane from Wavre
    { type: 'flat', at: [-150, -160], r: 30, amount: 0.7 }, { type: 'flat', at: [60, 226], r: 30, amount: 0.7 },
  ],
};

// ------------------------------------------------------------------ Europe (two bakes of one map: before the war, and "all of it" in red)
const mkEurope = (allied) => ({
  world: {
    seed: 1814, size: [900, 600], res: 1, base: 0, meshStep: 2.5, sun: { azimuth: 235, elevation: 34 }, sunEve: { azimuth: 284, elevation: 10 },
    style: { contour: 4, pxPerUnit: 4.4, paletteSoft: 1.2, palette: [[-4, allied ? [0.86, 0.46, 0.38] : [0.82, 0.79, 0.52]], [1.5, allied ? [0.88, 0.46, 0.38] : [0.82, 0.79, 0.52]], [5.2, allied ? [0.86, 0.50, 0.40] : [0.80, 0.78, 0.50]], [9.6, [0.30, 0.48, 0.88]], [14, [0.24, 0.40, 0.80]], [30, [0.7, 0.7, 0.7]]] },
    features: [
      { type: 'undulate', amp: 1.0, scale: 90 },
      { type: 'sea', poly: [[-470, -310], [470, -310], [470, 310], [-470, 310]], shelf: 30, depth: 8 },
      { type: 'land', wob: 2, shelf: 14, poly: [[-336, 64], [-336, 160], [-287, 176], [-238, 160], [-210, 128], [-182, 88], [-140, 59], [-84, 42], [-66, 56], [-42, 83], [-7, 99], [8, 144], [26, 124], [28, 104], [49, 110], [27, 94], [14, 82], [-21, 54], [-38, 26], [-17, 21], [14, 64], [63, 96], [98, 160], [118, 150], [112, 102], [196, 96], [470, 110], [470, -310], [330, -240], [210, -206], [136, -198], [126, -160], [77, -123], [50, -118], [-10, -112], [-42, -114], [-67, -117], [-70, -152], [-63, -171], [-95, -144], [-112, -104], [-147, -88], [-170, -67], [-185, -64], [-232, -42], [-273, -22], [-227, 13], [-227, 32], [-238, 59]] },
      { type: 'land', wob: 2, shelf: 14, poly: [[-307, -48], [-290, -64], [-252, -72], [-273, -88], [-252, -102], [-255, -120], [-280, -141], [-290, -160], [-252, -186], [-238, -168], [-252, -144], [-232, -128], [-210, -106], [-186, -91], [-190, -67], [-250, -52]] },
      { type: 'land', wob: 2, shelf: 12, poly: [[-300, -84], [-340, -92], [-350, -112], [-330, -128], [-300, -124], [-292, -104]] },
      { type: 'land', wob: 2, shelf: 12, poly: [[-130, -300], [330, -300], [240, -232], [190, -200], [120, -222], [60, -200], [30, -168], [14, -152], [2, -168], [-30, -178], [-70, -186], [-100, -214]] },
      { type: 'land', wob: 2, smooth: 1, shelf: 10, poly: [[-95, 98], [-76, 100], [-73, 134], [-92, 136]] },
      { type: 'land', wob: 2, smooth: 1, shelf: 10, poly: [[-90, 60], [-77, 62], [-78, 86], [-90, 84]] },
      { type: 'land', wob: 2, smooth: 1, shelf: 10, poly: [[-36, 142], [8, 139], [6, 165], [-34, 160]] },
      { type: 'land', wob: 0.5, smooth: 1, shelf: 6, poly: [[-76, 62], [-62, 62], [-62, 74], [-76, 74]] },
      // France, raised so the palette paints it blue
      { type: 'land', wob: 1.5, shelf: 8, beach: 16, lift: 12, poly: [[-273, -22], [-258, -36], [-232, -42], [-196, -52], [-185, -64], [-166, -62], [-140, -48], [-126, -40], [-108, -30], [-102, -20], [-118, 0], [-126, 10], [-112, 38], [-108, 53], [-140, 59], [-168, 70], [-200, 66], [-235, 59], [-230, 32], [-230, 10], [-245, -6], [-262, -8]] },
      { type: 'lake', poly: [[184, 56], [206, 30], [250, 8], [320, 0], [366, 30], [350, 70], [300, 96], [240, 98], [196, 94]], shelf: 8 },
      { type: 'woods', at: [-190, 20], r: [18, 12] }, { type: 'woods', at: [30, -60], r: [20, 12] }, { type: 'woods', at: [250, -100], r: [30, 18] },
      { type: 'mountains', path: [[-120, 40], [-104, 50]], w: 12, h: 10, ridged: 0.7, scale: 20 },
    ],
  },
  ambient: { wind: [1, 0.3], gusts: 0, flow: { dir: [1, 0.2], speed: 0.5, glint: 1.1 }, birds: [{ center: [-150, 110], r: 30, h: 16, n: 5, speed: 5, size: 1.0 }] },
});
const eur = mkEurope(false), eurW = mkEurope(true);
const PARIS = [-177, -30], ELBA = [-69, 68];
Object.assign(eur, {
  arrows: [
    { id: 'exile', at: 'l02.sent', until: 'l02.island.', ease: 'cam', team: 'carthage', style: 'dash', width: 3.0, path: [[-168, -22], [-148, 8], [-114, 40], [-82, 62]], head: true, lift: 5, hide: 'l02.escaped,' },
    { id: 'sail', at: 'l02.escaped,', until: 'l02.France#1', ease: 'cam', team: 'carthage', style: 'dash', width: 3.0, path: [[-72, 66], [-92, 60], [-113, 52]], lift: 5, hide: 'l02.So' },
    { id: 'march', at: 'l02.France#1', until: 'l02.again.', ease: 'out', team: 'carthage', width: 3.6, path: [[-113, 52], [-130, 20], [-152, -8], [-170, -26]], lift: 5, hide: 'l02.So' },
    ...[[[-250, -108], [-200, -44]], [[-270, 110], [-216, 24]], [[20, -24], [-100, -14]], [[-26, -96], [-130, -42]], [[240, -140], [-98, -30]], [[-30, 96], [-110, 34]]].map((p, i) => ({ at: { line: 'l02', word: 'declared', offset: i * 0.14 }, until: { line: 'l02', word: 'him,', offset: 0.2 }, ease: 'out', team: 'rome', width: 5, path: p, lift: 5, hide: 'l03' })),
  ],
  labels: [
    { at: 1.4, until: 6.0, text: 'JUNE 1815', screen: [0.5, 0.15], big: true },
    { at: 'l00.Napoleon,', until: 'l00.And', text: 'NAPOLEON', pos: PARIS, y: 4, team: 'carthage', dx: 0.08, dy: -0.12 },
    { at: 'l02.France.', until: 'l02.He', text: 'FRANCE', pos: [-180, 14], y: 12, leader: false, rule: false },
    { at: 'l02.small', until: 'l02.So', text: 'ELBA', pos: ELBA, y: 2, dx: 0.08, dy: -0.08 },
  ],
  icons: [
    { at: 'l00.Napoleon,', until: 'l02.beaten', icon: 'tricolore', pos: PARIS, y: 4, size: 26, minPx: 0.06, maxPx: 0.075 },
    { follow: 'exile', at: 'l02.sent', until: 'l02.escaped,', icon: 'brig', team: 'carthage', size: 22, minPx: 0.05, maxPx: 0.065 },
    { follow: 'sail', at: 'l02.escaped,', until: 'l02.France#1', icon: 'brig', team: 'carthage', size: 22, minPx: 0.05, maxPx: 0.065, flip: true },
    { at: 'l02.took', until: 'l03', icon: 'tricolore', pos: PARIS, y: 4, size: 26, minPx: 0.06, maxPx: 0.075 },
  ],
  markers: [{ id: 'paris', at: 'l00.Napoleon,', until: 'l03', pos: PARIS, glyph: 'town', team: [0.15, 0.33, 0.74], label: 'PARIS', labelUntil: 'l00.back.', size: 0.055 }],
});
// the red bake fades in on "All of it" (a manual inset over the scene's own); its camera holds the closing frame of S1.3
eurW.camera = [{ at: 0, target: [-86, -18], width: 690, pitch: 60, yaw: 0, mm: 35 }];

// ------------------------------------------------------------------ the South Atlantic (Saint Helena)
const SH = [95, 72];
const atl = {
  world: {
    seed: 1821, size: [900, 600], res: 1, base: 0, meshStep: 2.5, sun: { azimuth: 235, elevation: 34 }, sunEve: { azimuth: 284, elevation: 10 },
    style: { contour: 4, pxPerUnit: 4.4, paletteSoft: 2, palette: [[-4, [0.62, 0.72, 0.46]], [1.5, [0.82, 0.79, 0.52]], [6, [0.78, 0.72, 0.48]], [14, [0.74, 0.60, 0.44]], [30, [0.7, 0.66, 0.6]], [50, [0.9, 0.9, 0.9]]] },
    features: [
      { type: 'undulate', amp: 1.2, scale: 90 },
      { type: 'sea', poly: [[-470, -310], [470, -310], [470, 310], [-470, 310]], shelf: 40, depth: 10 },
      { type: 'land', wob: 3, shelf: 16, poly: [[62, -300], [90, -270], [130, -250], [200, -215], [241, -180], [303, -168], [297, -120], [320, -70], [359, -24], [350, 50], [338, 144], [380, 230], [420, 288], [470, 310], [470, -310], [100, -310]] },
      { type: 'land', wob: 3, shelf: 16, poly: [[-470, -110], [-330, -70], [-310, -54], [-312, -24], [-359, 36], [-380, 90], [-421, 156], [-440, 230], [-470, 310]] },
      { type: 'land', wob: 0.8, smooth: 1, shelf: 6, poly: [[86, 68], [94, 64], [104, 68], [104, 76], [94, 80], [86, 76]] },
      { type: 'hill', at: SH, r: [6, 5], h: 6 },
      { type: 'woods', at: [330, 60], r: [20, 40] }, { type: 'woods', at: [-370, 40], r: [14, 40] },
    ],
  },
  ambient: { wind: [1, 0.3], gusts: 0, flow: { dir: [0.4, 1], speed: 0.6, glint: 1.3 }, birds: [{ center: [100, 60], r: 18, h: 10, n: 5, speed: 4, size: 0.8 }, { path: [[-300, -200], [300, 200]], n: 4, h: 30, speed: 7 }] },
  arrows: [
    { id: 'ocean', at: 'l15.sent', until: 'l15.Atlantic.>', ease: 'cam', team: 'carthage', style: 'dash', width: 3.0, path: [[-90, -292], [-60, -180], [-10, -70], [50, 16], [88, 62]], lift: 5 },
  ],
  labels: [
    { at: 'l15.This', until: 'l16', text: 'AFRICA', pos: [380, 40], dy: -0.06, leader: false, rule: false },
    { at: 'l15.This', until: 'l16', text: 'SOUTH AMERICA', pos: [-380, 20], dy: -0.06, leader: false, rule: false },
    { at: 'l15.island', until: 'l16', text: 'SAINT HELENA', pos: SH, y: 6, team: 'carthage', dx: -0.1, dy: -0.12 },
    { at: 'l15.No', until: 'l16', text: '1,900 KM FROM AFRICA', screen: [0.5, 0.86], big: true },
  ],
  icons: [{ follow: 'ocean', at: 'l15.sent', until: 'l16', icon: 'brig', team: 'carthage', size: 22, minPx: 0.05, maxPx: 0.065 }],
};

// ------------------------------------------------------------------ the armies
const WX = [-200, -125, -50, 50, 125, 200];            // Wellington's six line blocks on the ridge (a 40 unit gap at the road)
const SQ = [1, 2, 3, 4];                               // the four central blocks form squares in the afternoon
const FX = [-210, -150, -90, -30, 30, 90, 150, 210];   // the French line on its own ridge
const wel = WX.map((_, i) => 'wel' + (i + 1)), fr = FX.map((_, i) => 'fr' + (i + 1)), prs = ['pr1', 'pr2', 'pr3', 'pr4'];
const LINE_Z = -58, SQ_Z = -44, FR_Z = 136;
const blocks = {};
WX.forEach((x, i) => { blocks[wel[i]] = { ...BR, kind: 'infantry', x: -60 + (i % 3) * 60, z: -176 + Math.floor(i / 3) * 34, heading: 180, len: 46, dep: 16, hidden: true }; });
// the other three faces of each square (north, east, west), facing outward, raised on "formed"
for (const i of SQ) { const x = WX[i];
  blocks['sqN' + i] = { ...BR, kind: 'infantry', x, z: SQ_Z - 9, heading: 0, len: 22, dep: 4, hidden: true, banner: false };
  blocks['sqE' + i] = { ...BR, kind: 'infantry', x: x + 9, z: SQ_Z, heading: 90, len: 12, dep: 4, hidden: true, banner: false };
  blocks['sqW' + i] = { ...BR, kind: 'infantry', x: x - 9, z: SQ_Z, heading: 270, len: 12, dep: 4, hidden: true, banner: false }; }
FX.forEach((x, i) => { blocks[fr[i]] = { ...FR, kind: 'infantry', x, z: FR_Z, heading: 0, len: 54, dep: 16, hidden: true }; });
Object.assign(blocks, {
  wellington: { ...BR, kind: 'elite', x: 40, z: -92, heading: 180, len: 7, dep: 5, hidden: true, bannerScale: 1.5 },
  napoleon: { ...FR, kind: 'elite', x: 16, z: 164, heading: 0, len: 7, dep: 5, hidden: true, bannerScale: 1.5 },
  blucher: { ...PR, kind: 'cavalry', x: 360, z: -126, heading: 220, len: 8, dep: 5, hidden: true, bannerScale: 1.5 },
  hougA: { ...BR, kind: 'infantry', x: -92, z: 16, heading: 180, len: 16, dep: 10, hidden: true, weight: 2, bannerScale: 1.2 },
  hayeA: { ...BR, kind: 'infantry', x: 16, z: 32, heading: 180, len: 14, dep: 9, hidden: true, weight: 2, bannerScale: 1.2 },
  bCav: { ...BR, kind: 'cavalry', x: 0, z: -84, heading: 180, len: 34, dep: 12, hidden: true },
  fCavA: { ...FR, kind: 'cavalry', x: -88, z: 70, heading: 0, len: 26, dep: 10, hidden: true },
  fCavB: { ...FR, kind: 'cavalry', x: -22, z: 70, heading: 0, len: 30, dep: 10, hidden: true },
  fCavC: { ...FR, kind: 'cavalry', x: 88, z: 70, heading: 0, len: 26, dep: 10, hidden: true },
  guard: { ...FR, kind: 'elite', x: 0, z: 112, heading: 0, len: 40, dep: 16, hidden: true, bannerScale: 1.3 },
  g1: { ...FR, kind: 'marker', figures: 'artillery', x: -76, z: 100, heading: 0, len: 40, dep: 6, hidden: true, banner: false },
  g2: { ...FR, kind: 'marker', figures: 'artillery', x: 76, z: 100, heading: 0, len: 40, dep: 6, hidden: true, banner: false },
  g3: { ...FR, kind: 'marker', figures: 'artillery', x: 150, z: 100, heading: 0, len: 34, dep: 6, hidden: true, banner: false },
});
prs.forEach((id, i) => { blocks[id] = { ...PR, kind: 'infantry', x: 340 + (i % 2) * 40, z: -100 + Math.floor(i / 2) * 30, heading: 220, len: 34, dep: 14, hidden: true }; });

const moves = [
  // S2: the French on their ridge, Wellington's army in column, the Prussians far to the east
  { blocks: [...fr, 'g1', 'g2', 'g3'], at: 'l03.waiting', dur: 0.9, stagger: 0.12, appear: true },
  { block: 'napoleon', at: 'l03.him', dur: 0.8, appear: true },
  { blocks: [...wel, 'wellington'], at: 'l03.British', dur: 0.9, stagger: 0.14, appear: true },
  { blocks: [...prs, 'blucher'], at: 'l03.Prussian', dur: 0.9, stagger: 0.16, appear: true },
  // S3: the army files onto the ridge, then steps back behind the crest; the farms are garrisoned
  ...WX.map((x, i) => ({ block: wel[i], at: { line: 'l05', word: 'lined', offset: i * 0.16 }, dur: 3.0, to: { x, z: -40, len: 60, dep: 16 }, ease: 'inOut' })),
  { blocks: wel, at: 'l05.Most', dur: 2.4, to: { z: LINE_Z }, ease: 'inOut' },
  { blocks: ['hougA', 'hayeA'], at: 'l06.forts.', dur: 0.9, stagger: 0.4, appear: true },
  // S5: Hougoumont, two waves that break on the walls
  { block: 'fr1', at: 'l08.attacked', dur: 1.6, to: { x: -160, z: 40 }, ease: 'inOut' }, { block: 'fr2', at: 'l08.attacked+0.2', dur: 1.6, to: { x: -98, z: 31 }, ease: 'inOut' },
  { blocks: ['fr1', 'fr2'], at: 'l08.all', dur: 1.0, by: { z: 34 }, ease: 'out' }, { blocks: ['fr1', 'fr2'], at: 'l08.all', dur: 1.0, fadeTo: 0.3 },
  { block: 'fr1', at: 'l08.long.', dur: 1.1, to: { z: 40 }, ease: 'inOut' }, { block: 'fr2', at: 'l08.long.+0.15', dur: 1.1, to: { z: 31 }, ease: 'inOut' },
  { block: 'fr1', at: 'l08.never', dur: 1.6, to: { x: -210, z: FR_Z }, ease: 'inOut' }, { block: 'fr2', at: 'l08.never', dur: 1.6, to: { x: -150, z: FR_Z }, ease: 'inOut' },
  { blocks: ['fr1', 'fr2'], at: 'l08.never', dur: 1.4, fadeTo: 0.55 },
  // the centre: two French columns climb, the British cavalry comes through the gap and throws them back, then runs on into the guns
  { block: 'fr4', at: 'l09.marched', dur: 3.0, to: { x: -26, z: 44, len: 48 }, ease: 'inOut' }, { block: 'fr5', at: 'l09.marched', dur: 3.0, to: { x: 26, z: 44, len: 48 }, ease: 'inOut' },
  { block: 'bCav', at: 'l09.British', dur: 0.7, appear: true },
  { block: 'bCav', at: 'l09.charged', dur: 1.8, path: [[0, -84], [0, -40], [-14, 0], [-24, 30]], ease: 'inQuad' },
  { blocks: ['fr4', 'fr5'], at: 'l09.back', dur: 1.5, by: { z: 44 }, ease: 'out' }, { blocks: ['fr4', 'fr5'], at: 'l09.back', dur: 1.5, fadeTo: 0.5 },
  { block: 'bCav', at: 'l09.back', dur: 1.5, to: { z: 70 }, ease: 'out' },
  { blocks: ['fr4', 'fr5'], at: 'l09.and', dur: 1.2, vanish: true },
  { block: 'bCav', at: 'l09.then#1', dur: 1.8, path: [[-24, 70], [10, 84], [42, 90]], ease: 'inOut' },
  { block: 'bCav', at: 'l09.far.', dur: 1.4, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 },
  { block: 'bCav', at: 'l10.thousands', dur: 1.0, vanish: true },
  { blocks: ['fr4', 'fr5'], at: 'l10.thousands', dur: 0.05, to: { z: FR_Z, len: 54 } }, { block: 'fr4', at: 'l10.thousands', dur: 0.05, to: { x: -30 } }, { block: 'fr5', at: 'l10.thousands', dur: 0.05, to: { x: 30 } },
  { blocks: ['fr4', 'fr5'], at: 'l10.Wellington', dur: 1.0, appear: true },
  // S6: the horsemen ride up; the line steps up to the crest and folds into squares; the horses flow round them and go back
  { blocks: ['fCavA', 'fCavB', 'fCavC'], at: 'l10.thousands', dur: 0.9, stagger: 0.2, appear: true },
  { blocks: wel, at: 'l10.rode', dur: 1.8, to: { z: SQ_Z }, ease: 'inOut' },
  ...SQ.map((i) => ({ block: wel[i], at: 'l10.formed', dur: 1.3, to: { z: SQ_Z + 9, len: 22, dep: 4 }, ease: 'inOut' })),
  { blocks: SQ.flatMap((i) => ['sqN' + i, 'sqE' + i, 'sqW' + i]), at: 'l10.formed+0.3', dur: 1.1, stagger: 0.05, appear: true },
  ...[['fCavA', -88], ['fCavB', -22], ['fCavC', 88]].flatMap(([id, x]) => [
    { block: id, at: 'l10.rode', dur: 2.2, to: { z: -6 }, ease: 'inOut' },
    { block: id, at: 'l10.squares', dur: 2.8, path: [[x, -6], [x, -50], [x, -92]], ease: 'inOut' },
    { block: id, at: 'l10.would', dur: 2.6, path: [[x, -92], [x + (x >= 0 ? 16 : -16), -104], [x, -80], [x, -20], [x, 50]], ease: 'inOut' },
  ]),
  { blocks: ['fCavA', 'fCavB', 'fCavC'], at: 'l10.would', dur: 2.0, fadeTo: 0.4 },
  { blocks: ['fCavA', 'fCavB', 'fCavC'], at: 'l11.far', dur: 1.2, vanish: true },
  // S7: the Prussians march through the mud; by evening they hit the French flank, which wheels to face them
  { block: 'pr1', at: 'l11.marching,', dur: 6.0, path: [[340, -100], [318, -40], [288, 30], [256, 88]], ease: 'inOut' },
  { block: 'pr3', at: 'l11.marching,+0.4', dur: 6.0, path: [[340, -70], [322, -10], [296, 70], [256, 142]], ease: 'inOut' },
  { block: 'pr2', at: 'l11.marching,+0.8', dur: 6.0, path: [[380, -100], [360, -30], [330, 40], [300, 96]], ease: 'inOut' },
  { block: 'pr4', at: 'l11.marching,+1.2', dur: 6.0, path: [[380, -70], [364, 0], [338, 80], [300, 152]], ease: 'inOut' },
  { block: 'blucher', at: 'l11.marching,+0.6', dur: 6.0, path: [[360, -126], [346, -50], [316, 20], [320, 124]], ease: 'inOut' },
  { block: 'fr8', at: 'l12.By', dur: 2.4, to: { x: 210, z: 100, heading: 90 }, ease: 'inOut' },
  { block: 'fr7', at: 'l12.By+0.3', dur: 2.4, to: { x: 206, z: 160, heading: 90 }, ease: 'inOut' },
  { blocks: prs, at: 'l12.By', dur: 1.6, to: { heading: 270 }, ease: 'inOut' },
  { blocks: ['pr1', 'pr3'], at: 'l12.smashing', dur: 1.4, to: { x: 228 }, ease: 'inQuad' }, { blocks: ['pr2', 'pr4'], at: 'l12.smashing+0.3', dur: 1.4, to: { x: 268 }, ease: 'inQuad' },
  { blocks: ['fr7', 'fr8'], at: 'l12.side,', dur: 2.0, fadeTo: 0.4 },
  // the squares open back into a line behind the crest; the Guard goes up the road
  { blocks: SQ.flatMap((i) => ['sqN' + i, 'sqE' + i, 'sqW' + i]), at: 'l12.By', dur: 1.2, vanish: true },
  ...SQ.map((i) => ({ block: wel[i], at: 'l12.By+0.4', dur: 2.0, to: { z: LINE_Z, len: 60, dep: 16 }, ease: 'inOut' })),
  { blocks: ['wel1', 'wel6'], at: 'l12.By+0.4', dur: 2.0, to: { z: LINE_Z }, ease: 'inOut' },
  { block: 'guard', at: 'l12.sent', dur: 1.0, appear: true },
  { block: 'guard', at: 'l12.Imperial', dur: 5.0, path: [[0, 112], [-16, 60], [-24, -6]], ease: 'inOut' },
  // S8: the line rises and fires; the Guard falls back; the whole army runs
  { blocks: wel, at: 'l13.rose', dur: 1.0, to: { z: -36 }, ease: 'out' },
  { block: 'guard', at: 'l13.fired.', dur: 1.4, fadeTo: 0.5 },
  { block: 'guard', at: 'l13.guard', dur: 1.6, to: { z: 36 }, ease: 'out' },
  { block: 'guard', at: 'l13.back#1', dur: 1.4, to: { z: 92 }, ease: 'inOut' },
  { block: 'napoleon', at: 'l13.army', dur: 3.0, path: [[16, 164], [40, 230], [44, 300]], ease: 'in' },
  ...[['fr1', -330], ['fr2', -250], ['fr3', -160], ['fr4', -70], ['fr5', 70], ['fr6', 160], ['fr7', 200], ['fr8', 214]].map(([id, x], k) => ({ block: id, at: { line: 'l13', word: 'army', offset: k * 0.1 }, dur: 3.2, to: { x, z: 300, heading: 180 }, ease: 'in' })),
  { block: 'guard', at: 'l13.ran.+0.4', dur: 3.0, to: { z: 300, heading: 180 }, ease: 'in' },
  { blocks: wel, at: 'l13.ran.', dur: 4.0, by: { z: 46 }, ease: 'inOut' },
  { blocks: prs, at: 'l13.army', dur: 4.0, by: { x: -40, z: 30 }, ease: 'inOut' },
];

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.06, grain: 0.03, vignette: 0.30 } },
  world,
  stages: { eur, eurW, atl },
  msaaOn: [['l10.horses', 'l11'], ['l13.guard', 'l13.And#1']],   // anti-aliasing only on the two low close shots
  blocks,
  moves,

  ambient: {
    wind: [1.0, 0.45], gusts: 0.6, flow: { dir: [0.05, 1], speed: 1.0, glint: 1.1 },
    camps: [{ pos: [-150, -160], size: [56, 34], team: 'rome', style: 'scatter', tents: 22, fires: 3, people: 12, palisade: false }, { pos: [60, 226], size: [60, 36], team: 'carthage', style: 'scatter', tents: 26, fires: 3, people: 12, rot: 6, palisade: false }],
    walkers: [{ path: [[2, -295], [8, -190], [5, -110]], n: 6, gap: 5, speed: 1.4, kind: 'light', team: 'neutral' }, { path: [[-470, -36], [-330, -40], [-220, -44]], n: 4, gap: 5, speed: 1.2, kind: 'light', team: 'neutral', offset: 20 }],
    smoke: [
      { pos: [-150, -160], n: 6, alpha: 0.12, height: 7 }, { pos: [60, 226], n: 6, alpha: 0.12, height: 7 },
      { pos: [-76, 92], n: 10, alpha: 0.2, height: 8, at: 'l08' }, { pos: [76, 92], n: 10, alpha: 0.2, height: 8, at: 'l08' }, { pos: [150, 92], n: 8, alpha: 0.18, height: 8, at: 'l08' },
      { pos: [-92, 14], n: 10, alpha: 0.24, height: 12, at: 'l10' },
      { pos: [250, 175], n: 10, alpha: 0.24, height: 12, at: 'l12.smashing' },
      ...[-60, -20, 20, 60, 100].map((x) => ({ pos: [x, -24], n: 6, alpha: 0.32, height: 5, at: 'l13.fired.' })),
    ],
    birds: [{ center: [-260, -90], r: 50, h: 30, n: 7, speed: 7 }, { path: [[-420, 200], [420, -160]], n: 5, h: 40, speed: 9 }, { center: [300, 40], r: 34, h: 26, n: 5, speed: 6, dir: -1 }],
  },

  // ------------------------------------------------------------------ scenes: sets and pre-planned cameras (the edit)
  scenes: [
    { id: 'S1', name: 'The return', at: 0, until: 'l02.all', stage: 'eur', inset: 'full', job: 'Napoleon is back, and this time all of Europe turns on him', set: { time: 0.08, haze: 1.0 },
      shots: [
        { at: 0, why: 'cold open on the map of Europe in June 1815; push to Paris as he is named, pull back to the continent that has had enough, crane up under the title',
          from: { target: [-100, -12], width: 720, pitch: 58, yaw: 0, mm: 35 },
          moves: [{ at: 1.8, until: 'l00.back.>', to: { target: [-160, -22], width: 520 }, ease: 'cam' }, { until: 'l00.enough.>', to: { target: [-104, -14], width: 660 }, ease: 'cam' }, { until: 'l02', to: { pitch: 66, width: 690 }, ease: 'camSoft' }] },
        { at: 'l02', why: 'closer on France: his fall, the exile to Elba and the escape back to Paris, following the routes', from: { target: [-150, 6], width: 400, pitch: 50, yaw: 0, mm: 35 },
          moves: [{ at: 'l02.sent', until: 'l02.island.>', to: { target: [-118, 28] } }, { at: 'l02.escaped,', until: 'l02.again.', to: { target: [-146, 0] } }] },
        { at: 'l02.again.', why: 'pull out to the whole continent: every army converges on France, then all of Europe turns red', from: { target: [-80, -20], width: 720, pitch: 60, yaw: 0, mm: 35 },
          moves: [{ until: 'l02.all', to: { target: [-86, -18], width: 690 } }] },
      ] },
    { id: 'S2', name: 'Two armies', at: 'l03', transition: { type: 'dissolve', dur: 1.0 }, job: 'who waits for him in Belgium, and his plan to beat them one at a time', set: { time: 0.18, haze: 1.2, cloud: 0.35 },
      shots: [
        { at: 'l03', why: 'change of world: the field in Belgium from high in the south, the French line arriving on its ridge', from: { target: [0, 64], width: 560, pitch: 44, yaw: 0, mm: 35 },
          moves: [{ until: 'l03.British', to: { target: [0, 48], width: 530 } }] },
        { at: 'l03.British', why: 'closer on the first enemy: Wellington\'s British-led army in column behind the ridge', from: { target: [-10, -150], width: 330, pitch: 38, yaw: 336, mm: 35 },
          moves: [{ until: 'l03.Wellington,>', to: { width: 300, target: [0, -146] } }] },
        { at: 'l03.and', why: 'change of place, far to the east: the Prussians and their seventy-two year old marshal', from: { target: [356, -94], width: 300, pitch: 30, yaw: 68, mm: 35 },
          moves: [{ until: 'l03.up.>', to: { yaw: 80, width: 272 } }] },
        { at: 'l04', why: 'the plan on the map from above: a wedge between two armies that want to join', from: { target: [70, -40], width: 800, pitch: 86, yaw: 0, mm: 35 },
          moves: [{ until: 'l04.up.>', to: { width: 770, target: [74, -38] } }] },
      ] },
    { id: 'S3', name: 'The ridge', at: 'l05', job: 'Wellington\'s position: a hidden line behind a ridge, and two farms turned into forts', set: { time: 0.12, haze: 1.25, cloud: 0.3 },
      shots: [
        { at: 'l05', why: 'the day of battle: high from the French side as the army files onto the ridge near Waterloo', from: { target: [0, -60], width: 560, pitch: 40, yaw: 8, mm: 35 },
          moves: [{ until: 'l05.Waterloo.>', to: { target: [0, -70], width: 500, yaw: 2 } }] },
        { at: 'l05.Most', why: 'low behind the French guns looking up the slope: the line steps back and drops out of sight', from: { target: [0, 10], dist: 224, pitch: 8, yaw: 0, mm: 35 },
          moves: [{ until: 'l05.guns.>', to: { dist: 204 } }] },
        { at: 'l06', why: 'high over the valley: the two farms in front of the ridge, each with its garrison', from: { target: [-76, 2], width: 320, pitch: 50, yaw: 342, mm: 35 },
          moves: [{ until: 'l06.middle.>', to: { target: [-46, 8], width: 296, yaw: 350 } }] },
      ] },
    { id: 'S4', name: 'The lie in', at: 'l07', job: 'rain all night, and the Emperor waits until almost midday', set: { time: [0.1, 0.0], haze: [2.6, 1.05], cloud: [0.95, 0.25] },
      shots: [
        { at: 'l07', why: 'low from the allied ridge over the wet valley to the French, waiting in the murk', from: { target: [0, 110], dist: 220, pitch: 9, yaw: 184, mm: 35 },
          moves: [{ until: 'l07.attacking.>', to: { dist: 196 } }] },
        { at: 'l07.Until', why: 'the sky clears: push in slowly on the Emperor\'s headquarters and hold on the joke', from: { target: [12, 158], dist: 120, pitch: 22, yaw: 22, mm: 40 },
          moves: [{ until: 'l07.in.>', to: { dist: 98, target: [14, 160] } }] },
      ] },
    { id: 'S5', name: 'Morning attacks', at: 'l08', job: 'the French attack and fail: Hougoumont holds, the centre is thrown back, the British cavalry goes too far', set: { time: 0.0, haze: 1.05, cloud: 0.28 },
      shots: [
        { at: 'l08', why: 'change of place, west to Hougoumont: wave after wave breaks on its walls', from: { target: [-120, 52], width: 290, pitch: 46, yaw: 328, mm: 35 },
          moves: [{ until: 'l08.it.>', to: { target: [-112, 44], width: 260 } }] },
        { at: 'l09', why: 'low behind the French columns as they climb at the centre of the ridge', from: { target: [0, 72], dist: 160, pitch: 12, yaw: 0, mm: 35 },
          moves: [{ until: 'l09.ridge.>', to: { target: [0, 40], dist: 150 } }] },
        { at: 'l09.British', why: 'high from the flank: the British cavalry comes through the gap in its line and throws them back down the slope', from: { target: [-6, 20], width: 300, pitch: 54, yaw: 272, mm: 35 },
          moves: [{ until: 'l09.slope,>', to: { target: [-6, 44] } }] },
        { at: 'l09.and', why: 'cut wide on the punchline: the horsemen run on into the French guns', from: { target: [10, 60], width: 470, pitch: 62, yaw: 306, mm: 35 },
          moves: [{ until: 'l09.far.>', to: { width: 500 } }] },
      ] },
    { id: 'S6', name: 'The squares', at: 'l10', job: 'thousands of French horsemen against squares that will not break', set: { time: 0.18, haze: 1.1, cloud: 0.3 },
      shots: [
        { at: 'l10', why: 'low behind the horsemen as they ride up the slope: the weight of the charge', from: { target: [0, 30], dist: 180, pitch: 11, yaw: 8, mm: 35 },
          moves: [{ until: 'l10.ridge.>', to: { target: [0, 0], dist: 168 } }] },
        { at: 'l10.Wellington', why: 'top-down: the line folds into hollow squares and the horsemen flow through the gaps', from: { target: [4, -46], width: 380, pitch: 82, yaw: 0, mm: 35 },
          moves: [{ until: 'l10.bayonets.>', to: { width: 350 } }] },
        { at: 'l10.horses', why: 'low and close beside one square: the horses will not go in', from: { target: [-50, -42], dist: 72, pitch: 12, yaw: 338, mm: 40 },
          moves: [{ until: 'l11', to: { yaw: 350, dist: 68 } }] },
      ] },
    { id: 'S7', name: 'The Prussians come', at: 'l11', job: 'the Prussians arrive late but they arrive, and Napoleon plays his last card', set: { time: [0.3, 0.6], haze: 1.15, cloud: 0.25 },
      shots: [
        { at: 'l11', why: 'change of place, far off to the east: the Prussians on the long road through the mud', from: { target: [330, -40], width: 430, pitch: 42, yaw: 296, mm: 35 },
          moves: [{ until: 'l11.coming.>', to: { target: [290, 40] } }] },
        { at: 'l12', why: 'evening, closer: they smash into the French flank, which wheels to face them', from: { target: [230, 120], width: 300, pitch: 46, yaw: 246, mm: 35 },
          moves: [{ until: 'l12.side,>', to: { width: 280 } }] },
        { at: 'l12.so', why: 'low behind Napoleon\'s last and best soldiers as they climb the road to the ridge', from: { target: [-6, 72], dist: 124, pitch: 24, yaw: 0, mm: 35 },
          moves: [{ until: 'l13', to: { target: [-14, 34], dist: 118 } }] },
      ] },
    { id: 'S8', name: 'The turn', at: 'l13', climax: true, job: 'the decisive moment, wide then close, the rout, and what it cost', set: { time: [0.75, 0.95], haze: 1.2, cloud: 0.1 },
      shots: [
        { at: 'l13', why: 'the decisive moment, wide and from above: the line rises out of the corn and fires', from: { target: [0, -16], width: 340, pitch: 70, yaw: 0, mm: 35 },
          moves: [{ until: 'l13.fired.>', to: { width: 320 } }] },
        { at: 'l13.guard', why: 'the same moment closer and lower: the Guard reels back under the smoke', from: { target: [-20, 6], dist: 112, pitch: 12, yaw: 330, mm: 40 },
          moves: [{ until: 'l13.And#1', to: { dist: 104 } }] },
        { at: 'l13.And#1', why: 'pull high and wide: when the Guard breaks, the whole French army runs', from: { target: [0, 130], width: 660, pitch: 64, yaw: 0, mm: 35 },
          moves: [{ until: 'l13.ran.>', to: { width: 720 } }] },
        { at: 'l14', why: 'the low evening light over the emptied field, under the Duke\'s words', from: { target: [0, 40], dist: 380, pitch: 13, yaw: 48, mm: 30 },
          moves: [{ until: 'l14>', to: { yaw: 60 }, ease: 'camLong' }] },
        { at: 'l15', why: 'four days later: the abandoned French ridge at dusk', from: { target: [0, 150], dist: 170, pitch: 15, yaw: 200, mm: 35 },
          moves: [{ until: 'l15.throne.>', to: { dist: 184 } }] },
      ] },
    { id: 'S9', name: 'Saint Helena', at: 'l15.This', stage: 'atl', inset: 'full', transition: { type: 'dissolve', dur: 1.0 }, job: 'exile for good, and the word it left behind', set: { time: 0.2, haze: 1.0 },
      shots: [
        { at: 'l15.This', why: 'change of world: the whole South Atlantic, then a slow push to a speck of an island', from: { target: [0, 0], width: 860, pitch: 74, yaw: 0, mm: 35 },
          moves: [{ until: 'l16', to: { target: [70, 50], width: 480 }, ease: 'camLong' }] },
      ] },
  ],

  // ------------------------------------------------------------------ the legend (motion-graphics frame)
  legend: {
    title: { text: 'THE BATTLE OF WATERLOO', sub: '18 June 1815', at: 'l02' },
    show: [['l02', 'l14']],
    sides: [
      { id: 'france', team: 'carthage', name: 'FRANCE', commander: 'Napoleon', banner: 'tricolore', at: 'l02.France.', strength: 73000, strengthAt: 'l03.him', dimAt: 'l13.ran.' },
      { id: 'allies', team: 'rome', name: 'ALLIED ARMY', commander: 'Duke of Wellington', commanderAt: 'l03.Duke', banner: 'banner', at: 'l03.British', strength: 68000, strengthAt: 'l03.Wellington,' },
      { id: 'prussia', team: 'green', name: 'PRUSSIA', commander: 'Marshal Blücher', commanderAt: 'l03.Marshal', banner: 'banner', at: 'l03.Prussian', strength: 50000, strengthAt: 'l03.72' },
    ],
    key: { show: [['l05.ridge', 'l11'], ['l12.Imperial', 'l13>']] },
    units: [
      { id: 'inf', kind: 'infantry', name: 'Infantry', teams: ['carthage', 'rome', 'green'], at: 'l05.army' },
      { id: 'art', kind: 'artillery', name: 'Artillery', team: 'carthage', at: 'l05.guns.' },
      { id: 'cav', kind: 'cavalry', name: 'Cavalry', teams: ['carthage', 'rome'], at: 'l09.cavalry' },
    ],
    places: [
      { id: 'ridge', letter: 'A', glyph: 'hill', name: 'The ridge', at: 'l05.ridge', pos: [-150, -36], y: 4, label: false, markerSize: 0.05 },
      { id: 'waterloo', letter: 'B', glyph: 'town', name: 'Waterloo', at: 'l05.Waterloo.', pos: [6, -232], team: 'rome' },
      { id: 'hougoumont', letter: 'C', glyph: 'fort', name: 'Hougoumont', at: 'l06.Hugo', pos: [-92, 16], y: 4, team: 'rome' },
      { id: 'haye', letter: 'D', glyph: 'fort', name: 'La Haye Sainte', at: 'l06.Laisant', pos: [16, 32], y: 4, team: 'rome' },
    ],
    focus: [
      { entry: 'art', at: 'l05.guns.', until: 'l06' }, { entry: 'hougoumont', at: 'l08.attacked', until: 'l08.it.>' }, { entry: 'cav', at: 'l09.cavalry', until: 'l09.far.>' },
      { entry: 'cav', at: 'l10.horsemen', until: 'l10.ridge.>' }, { entry: 'inf', at: 'l10.squares', until: 'l10.bayonets.>' },
      { entry: 'prussia', at: 'l11.Meanwhile,', until: 'l12.side,>' }, { entry: 'allies', at: 'l13.rose', until: 'l13.fired.>' },
    ],
    scale: { unitM: 8, show: [['l04', 'l11']] },
  },

  labels: [
    { at: 'l03.him', until: 'l03.British', text: 'NAPOLEON', block: 'napoleon', team: 'carthage', dx: 0.04, dy: -0.12 },
    { at: 'l03.Duke', until: 'l03.and', text: 'WELLINGTON', block: 'wellington', team: 'rome', dx: 0.06, dy: -0.14 },
    { at: 'l03.Marshal', until: 'l04', text: 'BLÜCHER', block: 'blucher', team: 'green', dx: -0.06, dy: -0.14 },
    { at: 'l05.18th', until: 'l05.army', text: '18 JUNE 1815', screen: [0.5, 0.86], big: true },
    { at: 'l07.Napoleon', until: 'l07.Until', text: 'NAPOLEON', block: 'napoleon', team: 'carthage', dx: 0.0, dy: -0.12 },
    { at: 'l07.midday,', until: 'l07.expensive', text: '11:30 AM', screen: [0.5, 0.86], big: true },
    { at: 'l10.squares', until: 'l10.horses', text: 'SQUARES', block: 'wel3', team: 'rome', dx: 0.1, dy: -0.12 },
    { at: 'l12.smashing', until: 'l12.so', text: 'PLANCENOIT', pos: [250, 180], y: 4, team: 'green', dx: 0.08, dy: -0.1 },
    { at: 'l12.Imperial', until: 'l13.guard', text: 'IMPERIAL GUARD', block: 'guard', team: 'carthage', dx: 0.1, dy: -0.12 },
    { at: 'l15.Four', until: 'l15.This', text: '22 JUNE 1815', screen: [0.5, 0.86], big: true },
  ],

  counters: [],
  icons: [],

  arrows: [
    // S2.4 the plan: a wedge between two armies that reach for each other
    { at: 'l04.beat', until: 'l04.them>', ease: 'out', team: 'carthage', width: 7, path: [[10, 150], [40, 20], [100, -60]], lift: 6, hide: 'l05' },
    { at: 'l04.one', until: 'l04.time>', ease: 'out', team: 'carthage', width: 5, path: [[100, -60], [190, -70], [300, -84]], lift: 6, hide: 'l05' },
    { at: 'l04.before', until: 'l04.up.>', ease: 'out', team: 'rome', width: 4, style: 'dash', path: [[10, -150], [80, -120], [150, -106]], lift: 6, hide: 'l05' },
    { at: 'l04.before', until: 'l04.up.>', ease: 'out', team: 'green', width: 4, style: 'dash', path: [[340, -120], [260, -112], [200, -108]], lift: 6, hide: 'l05' },
    // S5 Hougoumont: two waves
    ...['attacked', 'long.'].flatMap((w) => [
      { at: `l08.${w}`, dur: 0.9, ease: 'out', team: 'carthage', width: 4, path: [[-200, 110], [-164, 56]], lift: 6, hide: `l08.${w}+1.6` },
      { at: `l08.${w}+0.2`, dur: 0.9, ease: 'out', team: 'carthage', width: 4, path: [[-140, 110], [-104, 48]], lift: 6, hide: `l08.${w}+1.6` },
    ]),
    // the centre and the cavalry
    { at: 'l09.marched', dur: 1.6, ease: 'out', team: 'carthage', width: 6, path: [[0, 120], [0, 50]], lift: 6, hide: 'l09.British' },
    { at: 'l09.charged', dur: 1.2, ease: 'out', team: 'rome', width: 6, path: [[0, -70], [-6, -20], [-20, 26]], lift: 6, hide: 'l09.and' },
    { at: 'l09.then#1', until: 'l09.far.', ease: 'out', team: 'rome', width: 4, style: 'dash', path: [[-24, 72], [10, 86], [44, 92]], lift: 6, hide: 'l10' },
    ...[-88, -22, 88].map((x) => ({ at: 'l10.rode', dur: 1.4, ease: 'out', team: 'carthage', width: 4, path: [[x, 66], [x, 4]], lift: 6, hide: 'l10.Wellington' })),
    // S7 the Prussian road, then the blow on the flank; the Guard goes up the road
    { at: 'l11.marching,', until: 'l11.coming.>', ease: 'cam', team: 'green', style: 'dash', width: 4, path: [[372, -110], [330, -40], [298, 40], [268, 112]], lift: 6, hide: 'l12.smashing' },
    { at: 'l12.smashing', dur: 1.0, ease: 'out', team: 'green', width: 5, path: [[270, 100], [234, 100]], lift: 6, hide: 'l12.so' },
    { at: 'l12.smashing+0.2', dur: 1.0, ease: 'out', team: 'green', width: 5, path: [[270, 156], [232, 158]], lift: 6, hide: 'l12.so' },
    { at: 'l12.straight', until: 'l12.ridge.>', ease: 'out', team: 'carthage', width: 6, path: [[0, 104], [-16, 50], [-24, 6]], lift: 6, hide: 'l13.fired.' },
    // S8 the rout
    ...[[-1, 0], [0, 1], [1, 2]].map(([s, k]) => ({ at: { line: 'l13', word: 'ran.', offset: k * 0.12 }, dur: 1.0, ease: 'out', team: 'carthage', width: 5, path: [[s * 60, 170], [s * 150, 260]], lift: 6, hide: 'l14' })),
  ],

  volleys: [],

  cards: [
    { at: 0, until: 0.9, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 10.7, until: 15.0, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF WATERLOO', size: 0.078, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
      { text: '1815', size: 0.056, y: 0.575, delay: 0.95, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.5 }, { y: 0.65, w: 0.5 }] },
    { at: 134.45, until: 139.3, scrim: 0.8, scrimCenter: 'rgba(20,8,6,0.75)', fadeIn: 0.5, fadeOut: 0.7, lines: [
      { text: 'THE DUKE OF WELLINGTON', size: 0.036, y: 0.40, delay: 0.1, pop: false, weight: 600, track: 0.2, colorTop: '#f3c0a8', colorBottom: '#d9846a' },
      { text: '"THE NEAREST RUN THING', size: 0.058, y: 0.52, delay: 1.7, pop: false, weight: 600, track: 0.08 },
      { text: 'YOU EVER SAW IN YOUR LIFE"', size: 0.058, y: 0.62, delay: 2.9, pop: false, weight: 600, track: 0.08 } ], ornaments: [{ y: 0.34, w: 0.5 }, { y: 0.69, w: 0.5 }] },
    { at: 148.95, until: 154.0, fill: 'rgb(238,226,192)', fillAlpha: 0.97, fadeIn: 0.6, fadeOut: 0.5, lines: [
      { text: 'WATERLOO', size: 0.1, y: 0.29, delay: 0.1, pop: false, stroke: 'rgba(0,0,0,0)', shadow: false, colorTop: '#4a2a14', colorBottom: '#2e180a', track: 0.12, weight: 600 },
      { text: 'idiom', size: 0.05, y: 0.40, delay: 0.5, pop: false, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#6a4a2a', colorBottom: '#6a4a2a' },
      { text: 'to meet your Waterloo', size: 0.07, y: 0.52, delay: 1.2, pop: false, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.03, colorTop: '#3a2412', colorBottom: '#3a2412' },
      { text: 'to meet the one thing', size: 0.062, y: 0.66, delay: 2.85, pop: false, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.03, colorTop: '#3a2412', colorBottom: '#3a2412' },
      { text: 'that finally beats you', size: 0.062, y: 0.76, delay: 3.85, pop: false, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.03, colorTop: '#8a2a1a', colorBottom: '#8a2a1a' } ], ornaments: [{ y: 0.18, w: 0.5 }, { y: 0.88, w: 0.5 }] },
    { at: 154.306, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.88, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Waterloo, 1815', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],

  // "All of it": S1 ends on the word and its Europe inset fades off (the S2 dissolve sets its out to 1 s), revealing the red bake of the
  // same map under it; the red map then dissolves into the battlefield at l03 (a manual inset: insets listed here draw under the scenes')
  insets: [{ why: 'All of it: the same map, every country but France turned red (a change of state, not of place)', stage: 'eurW', at: 'l02.all', until: 'l03', rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.01, out: 1.0, samples: 0 }],
};
