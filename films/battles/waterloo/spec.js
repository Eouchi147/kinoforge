// The Battle of Waterloo (1815): Battle Map spec. Times come from the cue words (see films/lib/battlemap/SPEC.md).
// Colours: French = blue (carthage), Wellington's British-led army = red (rome), Prussians = green, Imperial Guard = blue with gold trim.
// Battlefield map: x east, z south; Brussels is north (-z), the French are south (+z). The ridge is Wellington's, the Brussels road runs north to south.
const FR = { team: 'carthage' }, BR = { team: 'rome' }, PR = { team: 'green' };
const GREEN = [0.20, 0.60, 0.30];
const range = (n) => Array.from({ length: n }, (_, i) => i);
const circle = (cx, cz, r, a0, a1, n) => range(n + 1).map((i) => { const a = (a0 + (a1 - a0) * i / n) * Math.PI / 180; return [Math.round(cx + Math.sin(a) * r), Math.round(cz - Math.cos(a) * r)]; });

// ------------------------------------------------------------------ the battlefield
const world = {
  seed: 1815, size: [900, 580], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 215, elevation: 34 }, sunEve: { azimuth: 282, elevation: 15 },
  style: { contour: 1.5, pxPerUnit: 4.6, fields: 0.55, trees: 0.8, palette: [[-4, [0.66, 0.74, 0.46]], [1, [0.78, 0.80, 0.48]], [6, [0.80, 0.76, 0.46]], [13, [0.78, 0.66, 0.42]], [22, [0.72, 0.58, 0.42]], [40, [0.66, 0.60, 0.55]]], paletteSoft: 5 },
  features: [
    { type: 'undulate', amp: 4, scale: 130 }, { type: 'undulate', amp: 1.4, scale: 38 },
    { type: 'ridge', path: [[-470, -30], [-330, -36], [-190, -38], [-60, -34], [40, -32], [150, -34], [300, -30], [470, -22]], w: 52, h: 26, rough: 0.2, meander: 4 },
    { type: 'ridge', path: [[-470, 128], [-300, 120], [-120, 124], [40, 120], [200, 126], [470, 118]], w: 60, h: 11, rough: 0.2, meander: 6 },
    { type: 'hill', at: [200, 100], r: [34, 26], h: 7, rot: 20 },
    { type: 'river', name: 'Dyle', path: [[392, -300], [398, -100], [386, 100], [394, 300]], w: 9, depth: 2.4, meander: 6, wl: 38 },
    { type: 'woods', at: [-100, 6], r: [13, 20] }, { type: 'woods', at: [-122, 30], r: [10, 8] },
    { type: 'woods', at: [225, 80], r: [20, 15] }, { type: 'woods', at: [0, -262], r: [330, 24] }, { type: 'woods', at: [330, -70], r: [14, 38] }, { type: 'woods', at: [-340, 70], r: [26, 20] },
    { type: 'farms', rect: [-240, 40, 230, 64, 3], cell: [18, 12] }, { type: 'farms', rect: [250, 30, 230, 70, -2], cell: [18, 12] },
    { type: 'farms', rect: [-250, -130, 260, 70, 2], cell: [18, 12] }, { type: 'farms', rect: [250, -130, 260, 70, -2], cell: [18, 12] },
    { type: 'farms', rect: [26, -22, 112, 22, 0], cell: [10, 9] }, { type: 'farms', rect: [-30, 190, 300, 50, 1], cell: [18, 12] },
    { type: 'road', path: [[2, -295], [8, -190], [5, -100], [3, -36], [-1, 40], [-4, 120], [4, 200], [-2, 295]], w: 3.2, meander: 3 },
    { type: 'road', path: [[-470, -32], [-330, -38], [-190, -40], [-60, -36], [40, -34], [150, -36], [300, -32], [470, -24]], w: 1.5, meander: 2 },
  ],
};

// ------------------------------------------------------------------ Europe (two bakes of one map: before the war and after "all of it")
const mkEurope = (allied) => ({
  world: {
    seed: 1814, size: [900, 600], res: 1, base: 0, meshStep: 2.5, sun: { azimuth: 235, elevation: 34 }, sunEve: { azimuth: 284, elevation: 10 },
    style: { contour: 4, pxPerUnit: 4.4, paletteSoft: 1.2, palette: [[-4, allied ? [0.86, 0.46, 0.38] : [0.82, 0.79, 0.52]], [1.5, allied ? [0.88, 0.46, 0.38] : [0.82, 0.79, 0.52]], [5.2, allied ? [0.86, 0.50, 0.40] : [0.80, 0.78, 0.50]], [9.6, [0.30, 0.48, 0.88]], [14, [0.24, 0.40, 0.80]], [30, [0.7, 0.7, 0.7]]] },
    features: [
      { type: 'undulate', amp: 1.0, scale: 90 },
      { type: 'sea', poly: [[-470, -310], [470, -310], [470, 310], [-470, 310]], shelf: 30, depth: 8 },
      // the mainland: Iberia, France, Italy, the Balkans, Germany, Poland and Russia
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
  camera: [
    { at: 0, target: [-110, -10], width: 900, pitch: 60, yaw: 0, mm: 35 },
    { at: 'l00.Napoleon,', target: [-160, -22], width: 520, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.back.', target: [-170, -28], width: 360, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.And', target: [-100, -10], width: 760, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l01', target: [-100, -10], width: 740, pitch: 58, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l02', target: [-165, -24], width: 460, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.beaten', target: [-140, 14], width: 480, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.escaped,', target: [-135, 12], width: 400, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.So', target: [-60, -20], width: 880, pitch: 60, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03', target: [-60, -20], width: 860, pitch: 60, yaw: 0, mm: 35, ease: 'linear' },
  ],
});
const eurA = mkEurope(false), eurB = mkEurope(true);

const PARIS = [-177, -30], ELBA = [-69, 68];
Object.assign(eurA, {
  arrows: [
    { id: 'exile', at: 'l02.sent', until: 'l02.island.', ease: 'inOut', team: 'carthage', style: 'dash', width: 3.4, path: [[-168, -22], [-148, 8], [-114, 40], [-82, 62]], head: true, lift: 5, hide: 'l02.escaped,' },
    { id: 'sail', at: 'l02.escaped,', until: 'l02.France#1', ease: 'inOut', team: 'carthage', style: 'dash', width: 3.4, path: [[-72, 66], [-92, 60], [-113, 52]], lift: 5, hide: 'l02.So' },
    { id: 'march', at: 'l02.France#1', until: 'l02.again.', ease: 'out', team: 'carthage', width: 4.2, path: [[-113, 52], [-130, 20], [-152, -8], [-170, -26]], lift: 5, hide: 'l02.So' },
    ...[[[-250, -108], [-200, -44]], [[-270, 110], [-216, 24]], [[20, -24], [-112, -14]], [[-26, -96], [-136, -42]], [[240, -140], [-104, -30]], [[-30, 96], [-118, 30]]].map((p, i) => ({ at: { line: 'l02', word: 'declared', offset: i * 0.12 }, until: { line: 'l02', word: 'him,', offset: 0.1 }, ease: 'out', team: 'rome', width: 6, path: p, lift: 5, hide: 'l03' })),
  ],
  labels: [
    { at: 1.4, until: 6.2, text: 'JUNE 1815', screen: [0.5, 0.13], style: 'text', big: true, size: 1.5, track: 0.16, weight: 800 },
    { at: 'l00.Napoleon,', until: 'l00.back.', text: 'NAPOLEON', pos: PARIS, y: 6, team: 'carthage', dy: -0.2, big: true },
    { at: 'l00.back.', until: 'l00.And', text: 'HE IS BACK', pos: PARIS, y: 6, team: 'carthage', dy: -0.2, big: true },
    { at: 'l00.Europe', until: 'l01', text: 'EUROPE HAD HAD ENOUGH', screen: [0.5, 0.86], big: true },
    { at: 'l02.Emperor', until: 'l02.He', text: 'EMPEROR OF FRANCE', pos: PARIS, y: 6, team: 'carthage', dy: -0.2, big: true },
    { at: 'l02.small', until: 'l02.He#1', text: 'ELBA', pos: ELBA, y: 8, dy: -0.12, dx: 0.1, big: true },
    { at: 'l02.escaped,', until: 'l02.sailed', text: 'ESCAPED', screen: [0.5, 0.14], big: true, team: 'carthage' },
    { at: 'l02.took', until: 'l02.So', text: 'BACK IN CHARGE', pos: PARIS, y: 6, team: 'carthage', dy: -0.2, big: true },
    { at: 'l02.So', until: 'l02.all', text: 'EUROPE DECLARES WAR', screen: [0.5, 0.13], big: true, team: 'rome' },
    { at: 'l02.all', until: 'l03', text: 'ALL OF IT', screen: [0.5, 0.13], style: 'text', big: true, size: 1.9, track: 0.16, weight: 800 },
  ],
  icons: [
    { at: 'l00.Napoleon,', until: 'l02.beaten', icon: 'hat', pos: PARIS, y: 4, size: 38, anim: 'bounce' },
    { at: 'l00.enough.', until: 'l01', icon: 'no', pos: PARIS, y: 4, size: 44 },
    { at: 'l00.back.', until: 'l00.And', icon: 'burst', pos: PARIS, y: 30, size: 30, anim: 'bounce' },
    { at: 'l02.Emperor', until: 'l02.beaten', icon: 'crown', pos: PARIS, y: 30, size: 22, anim: 'bounce', fallAt: 'l02.beaten', fallDur: 0.7 },
    { follow: 'exile', at: 'l02.sent', until: 'l02.escaped,', icon: 'ship', team: 'carthage', size: 24 },
    { at: 'l02.small', until: 'l02.escaped,', icon: 'island', pos: ELBA, y: 2, size: 26 },
    { follow: 'sail', at: 'l02.sailed', until: 'l02.France#1', icon: 'ship', team: 'carthage', size: 22, flip: true },
    { at: 'l02.took', until: 'l02.So', icon: 'hat', pos: PARIS, y: 4, size: 38, anim: 'bounce' },
    { at: 'l02.took', until: 'l02.So', icon: 'crown', pos: PARIS, y: 34, size: 22, anim: 'bounce' },
    { at: 'l02.So', until: 'l03', icon: 'swords', pos: [-130, -90], y: 6, size: 34, anim: 'bounce' },
  ],
});
eurB.arrows = eurA.arrows; // the same stage with the countries turned red; its own overlay stays empty (the labels above are drawn once)
eurB.arrows = [];

// ------------------------------------------------------------------ the South Atlantic (Saint Helena)
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
      { type: 'hill', at: [95, 72], r: [6, 5], h: 6 },
      { type: 'woods', at: [330, 60], r: [20, 40] }, { type: 'woods', at: [-370, 40], r: [14, 40] },
    ],
  },
  arrows: [
    { id: 'ocean', at: 'l15.sent', until: 'l15.South', ease: 'inOut', team: 'carthage', style: 'dash', width: 3.6, path: [[-90, -292], [-60, -180], [-10, -70], [60, 20], [92, 64]], lift: 5, hide: 'l16' },
  ],
  labels: [
    { at: 'l15.This', until: 'l15.island', text: 'ALL ALONE', screen: [0.5, 0.14], big: true },
    { at: 'l15.island', until: 'l15.No', text: 'SAINT HELENA', pos: [95, 72], y: 6, team: 'carthage', dy: -0.18, big: true },
    { at: 'l15.South', until: 'l15.No', text: 'SOUTH ATLANTIC OCEAN', screen: [0.5, 0.86], big: true },
    { at: 'l15.This', until: 'l15.No', text: 'AFRICA', pos: [380, 40], dy: -0.06, leader: false },
    { at: 'l15.This', until: 'l15.No', text: 'SOUTH AMERICA', pos: [-380, 20], dy: -0.06, leader: false },
    { at: 'l15.No', until: 'l16', text: 'NO ESCAPING', screen: [0.5, 0.14], big: true, team: 'carthage' },
  ],
  icons: [
    { follow: 'ocean', at: 'l15.sent', until: 'l15.No', icon: 'ship', team: 'carthage', size: 22 },
    { at: 'l15.island', until: 'l15.No', icon: 'hat', pos: [95, 72], y: 14, size: 18, anim: 'bounce' },
    { at: 'l15.No', until: 'l16', icon: 'door', pos: [95, 72], y: 6, size: 24, anim: 'slam' },
  ],
  camera: [
    { at: 'l15.This', target: [0, 0], width: 900, pitch: 80, yaw: 0, mm: 35 },
    { at: 'l15.island', target: [60, 40], width: 560, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l15.in', target: [92, 66], width: 300, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l15.No', target: [92, 66], width: 200, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l16.today,', target: [90, 60], width: 900, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
  ],
};

// ------------------------------------------------------------------ the film
const WX = [-190, -112, -34, 44, 122, 200];   // Wellington's six blocks along the ridge
const FX = [-210, -150, -90, -30, 30, 90, 150, 210]; // the French line
const wel = WX.map((_, i) => 'wel' + (i + 1)), fr = FX.map((_, i) => 'fr' + (i + 1));
const blocks = {};
WX.forEach((x, i) => { blocks['wel' + (i + 1)] = { ...BR, kind: 'infantry', x: -60 + (i % 3) * 60, z: -170 + Math.floor(i / 3) * 34, heading: 180, len: 46, dep: 16, hidden: true, height: 3.4 }; });
FX.forEach((x, i) => { blocks['fr' + (i + 1)] = { ...FR, kind: 'infantry', x, z: 112, heading: 0, len: 54, dep: 16, hidden: true, height: 3.4 }; });
for (let i = 0; i < 4; i++) blocks['pr' + (i + 1)] = { ...PR, kind: 'infantry', x: 322 + (i % 2) * 36, z: -6 + Math.floor(i / 2) * 30, heading: 270, len: 34, dep: 14, hidden: true, height: 3.4 };
Object.assign(blocks, {
  hougA: { ...BR, kind: 'infantry', x: -96, z: 14, heading: 180, len: 16, dep: 12, hidden: true, bannerScale: 1.2 },
  hayeA: { ...BR, kind: 'infantry', x: 2, z: 24, heading: 180, len: 16, dep: 12, hidden: true, bannerScale: 1.2 },
  bCav1: { ...BR, kind: 'cavalry', x: -30, z: -66, heading: 180, len: 40, dep: 12, hidden: true },
  bCav2: { ...BR, kind: 'cavalry', x: 40, z: -66, heading: 180, len: 40, dep: 12, hidden: true },
  fCav1: { ...FR, kind: 'cavalry', x: -40, z: 150, heading: 0, len: 48, dep: 14, hidden: true },
  fCav2: { ...FR, kind: 'cavalry', x: 40, z: 150, heading: 0, len: 48, dep: 14, hidden: true },
  fCav3: { ...FR, kind: 'cavalry', x: -110, z: 150, heading: 0, len: 48, dep: 14, hidden: true },
  guard: { ...FR, kind: 'elite', x: 0, z: 176, heading: 0, len: 46, dep: 18, hidden: true, height: 3.8 },
});

const spec = {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 } },
  world,
  stages: { eur: eurA, eurW: eurB, atl },
  msaaOn: [[29, 47], [134.4, 139.5]],

  blocks,

  moves: [
    // l03 two armies in Belgium
    { blocks: ['fr1', 'fr2', 'fr3', 'fr4', 'fr5', 'fr6', 'fr7', 'fr8'], at: 'l03.him', dur: 0.7, stagger: 0.12, appear: true, appearFrom: 20 },
    { blocks: wel, at: 'l03.armies', dur: 0.7, stagger: 0.14, appear: true, appearFrom: 20 },
    { blocks: ['pr1', 'pr2', 'pr3', 'pr4'], at: 'l03.Prussian', dur: 0.7, stagger: 0.14, appear: true, appearFrom: 20 },
    { blocks: ['pr1', 'pr2', 'pr3', 'pr4'], at: 46.7, dur: 0.5, vanish: true },
    // l05 Wellington lines up on the ridge, then waits behind the crest
    // l06 farms become forts
    { blocks: ['hougA', 'hayeA'], at: 'l06.forts.', dur: 0.7, stagger: 0.3, appear: true, appearFrom: 18 },
    // l08 Hougoumont: the French attack it again and again
    ...[['fr1', -210, -130, 40], ['fr2', -150, -70, 46]].flatMap(([id, x0, x1, z1], k) => [
      { block: id, at: { line: 'l08', word: 'attacked', offset: k * 0.3 }, dur: 0.9, to: { x: x1, z: z1 }, ease: 'inOut' },
      { block: id, at: { line: 'l08', word: 'attacked', offset: 1.5 + k * 0.2 }, dur: 0.8, to: { x: x0, z: 112 }, ease: 'inOut' },
      { block: id, at: { line: 'l08', word: 'day', offset: k * 0.2 }, dur: 0.8, to: { x: x1, z: z1 }, ease: 'inOut' },
      { block: id, at: { line: 'l08', word: 'day', offset: 0.95 + k * 0.2 }, dur: 0.8, to: { x: x0, z: 112 }, ease: 'inOut' },
      { block: id, at: { line: 'l08', word: 'They', offset: k * 0.2 }, dur: 0.8, to: { x: x1, z: z1 }, ease: 'inOut' },
      { block: id, at: { line: 'l08', word: 'They', offset: 0.95 + k * 0.2 }, dur: 0.8, to: { x: x0, z: 112 }, ease: 'inOut' },
    ]),
    // l09 the centre: French march up, British cavalry throws them back and then goes too far
    { blocks: ['fr3', 'fr4', 'fr5', 'fr6'], at: 'l09.marched', dur: 2.6, to: { z: 22 }, ease: 'inOut' },
    { blocks: ['bCav1', 'bCav2'], at: 'l09.cavalry', dur: 0.8, stagger: 0.12, appear: true, appearFrom: 10 },
    { blocks: ['bCav1', 'bCav2'], at: 'l09.charged', dur: 1.5, to: { z: 20 }, ease: 'inQuad' },
    { blocks: ['fr3', 'fr4', 'fr5', 'fr6'], at: 'l09.back', dur: 1.5, to: { z: 100 }, ease: 'out' },
    { blocks: ['bCav1', 'bCav2'], at: 'l09.charged#1', dur: 1.9, to: { z: 130 }, ease: 'inOut' },
    { blocks: ['bCav1', 'bCav2'], at: 'l09.far.', dur: 0.8, fadeTo: 1, alphaTo: 0.0, sinkTo: 0.9 },
    // l10 French cavalry up the ridge; Wellington's soldiers form squares; the horses will not charge
    { blocks: ['fCav3', 'fCav1', 'fCav2'], at: 'l10.thousands', dur: 0.8, stagger: 0.15, appear: true, appearFrom: 14 },
    { blocks: wel, at: 'l10.afternoon,', dur: 1.8, to: { z: -44 }, ease: 'inOut' },
    { blocks: wel, at: 'l10.formed', dur: 1.0, to: { len: 26, dep: 26 }, ease: 'inOut' },
    { block: 'fCav3', at: 'l10.rode', dur: 2.6, path: [[-110, 150], [-100, 60], [-80, -4]], ease: 'inOut' },
    { block: 'fCav1', at: 'l10.rode', dur: 2.6, path: [[-40, 150], [-36, 60], [-30, -4]], ease: 'inOut' },
    { block: 'fCav2', at: 'l10.rode', dur: 2.6, path: [[40, 150], [44, 60], [50, -4]], ease: 'inOut' },
    { block: 'fCav3', at: 'l10.Wellington', dur: 4.6, path: [...circle(-112, -44, 34, 160, 520, 12)], ease: 'linear' },
    { block: 'fCav1', at: 'l10.Wellington', dur: 4.6, path: [...circle(-34, -44, 34, 160, 520, 12)], ease: 'linear' },
    { block: 'fCav2', at: 'l10.Wellington', dur: 4.6, path: [...circle(44, -44, 34, 160, 520, 12)], ease: 'linear' },
    { blocks: ['fCav3', 'fCav1', 'fCav2'], at: 'l10.would', dur: 1.8, by: { z: 40 }, ease: 'out' },
    { blocks: ['fCav3', 'fCav1', 'fCav2'], at: 'l11.far', dur: 1.2, vanish: true },
    // l11 the Prussians march in from the east
    { blocks: ['pr1', 'pr2', 'pr3', 'pr4'], at: 'l11.Meanwhile,', dur: 0.1, to: { x: 442, z: -70 }, ease: 'linear' },
    { blocks: ['pr1', 'pr2', 'pr3', 'pr4'], at: 'l11.far', dur: 0.7, stagger: 0.14, appear: true, appearFrom: 14 },
    { block: 'pr1', at: 'l11.marching,', dur: 6.2, path: [[400, -62], [330, -34], [260, 22], [214, 70], [190, 92]], ease: 'inOut' },
    { block: 'pr2', at: 'l11.marching,+0.5', dur: 6.2, path: [[400, -62], [330, -34], [260, 22], [226, 80], [208, 100]], ease: 'inOut' },
    { block: 'pr3', at: 'l11.marching,+1.0', dur: 6.2, path: [[400, -62], [330, -34], [270, 8], [236, 60], [216, 84]], ease: 'inOut' },
    { block: 'pr4', at: 'l11.marching,+1.5', dur: 6.2, path: [[400, -62], [330, -34], [276, 4], [250, 40], [230, 70]], ease: 'inOut' },
    // l12 evening: the Prussians hit the French right; Napoleon sends in the Guard
    { blocks: ['fr7', 'fr8'], at: 'l12.smashing', dur: 1.4, to: { heading: 90, x: 196 }, ease: 'inOut' },
    { blocks: wel, at: 'l12.By', dur: 2.0, to: { z: -58, len: 66, dep: 16 }, ease: 'inOut' },
    { block: 'guard', at: 'l12.sent', dur: 0.8, appear: true, appearFrom: 24 },
    { block: 'guard', at: 'l12.straight', dur: 4.0, path: [[0, 140], [2, 60], [2, -12]], ease: 'inOut' },
    // l13 the allies rise out of the corn and fire; the Guard falls back; the army runs
    { blocks: wel, at: 'l13.rose', dur: 0.9, to: { z: -36 }, ease: 'out' },
    { block: 'guard', at: 'l13.guard', dur: 1.6, to: { z: 70 }, ease: 'out' },
    { block: 'guard', at: 'l13.back,', dur: 1.6, to: { z: 110 }, ease: 'inOut' },
    { blocks: fr, at: 'l13.army', dur: 2.6, stagger: 0.11, to: { z: 290, heading: 180 }, ease: 'inQuad' },
    { block: 'guard', at: 'l13.army', dur: 2.4, to: { z: 300, heading: 180 }, ease: 'inQuad' },
    { blocks: ['fr1', 'fr3', 'fr5', 'fr7'], at: 'l13.ran.', dur: 1.6, by: { x: -90 }, ease: 'in' },
    { blocks: ['fr2', 'fr4', 'fr6', 'fr8'], at: 'l13.ran.', dur: 1.6, by: { x: 90 }, ease: 'in' },
  ],

  light: [
    { at: 'l07.It', dur: 1.2, to: { cloud: 0.95 }, ease: 'inOut' }, { at: 'l07.It', dur: 1.2, to: { haze: 2.6 }, ease: 'inOut' },
    { at: 'l07.Until', dur: 1.2, to: { cloud: 0.28 }, ease: 'inOut' }, { at: 'l07.Until', dur: 1.2, to: { haze: 1.0 }, ease: 'inOut' },
    { at: 'l12.evening,', dur: 3.4, to: { eve: 1 }, ease: 'inOut' }, { at: 'l12.evening,', dur: 3.4, to: { haze: 1.3 }, ease: 'inOut' }, { at: 'l12.evening,', dur: 3.0, to: { cloud: 0.03 }, ease: 'inOut' },
  ],

  camera: [
    // l03 Belgium: two armies waiting, a wide view
    { at: 0, target: [10, -50], width: 860, pitch: 58, yaw: 0, mm: 35 },
    { at: 'l03.Two', target: [20, -50], width: 860, pitch: 58, yaw: 0, mm: 35 },
    { at: 'l03.Prussian', target: [190, 0], width: 700, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.Napoleon\'s', target: [60, 20], width: 880, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    // l05 the ridge
    { at: 'l05.On', target: [0, -50], width: 600, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l05.Most', target: [0, 0], width: 480, pitch: 26, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l05.out', target: [0, 30], width: 460, pitch: 24, yaw: 6, mm: 35, ease: 'inOut' },
    // l06 the farms
    { at: 'l06.In', target: [-40, 8], width: 380, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l06.Hugo', target: [-96, 12], width: 200, pitch: 40, yaw: -10, mm: 35, ease: 'inOut' },
    { at: 'l06.Laisant', target: [2, 22], width: 190, pitch: 40, yaw: 8, mm: 35, ease: 'inOut' },
    // l07 rain and the lie in
    { at: 'l07.It', target: [0, 40], width: 520, pitch: 44, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l07.Napoleon', target: [0, 118], width: 300, pitch: 36, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l07.expensive', target: [0, 124], width: 240, pitch: 34, yaw: 0, mm: 35, ease: 'inOut' },
    // l08 Hougoumont
    { at: 'l08.First,', target: [-104, 56], width: 300, pitch: 46, yaw: -14, mm: 35, ease: 'inOut' },
    { at: 'l08.never', target: [-100, 44], width: 280, pitch: 40, yaw: -8, mm: 35, ease: 'inOut' },
    // l09 the centre
    { at: 'l09.Then', target: [0, 40], width: 440, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l09.British', target: [0, 20], width: 340, pitch: 40, yaw: 18, mm: 35, ease: 'inOut' },
    { at: 'l09.and', target: [0, 80], width: 380, pitch: 40, yaw: 20, mm: 35, ease: 'inOut' },
    // l10 the squares
    { at: 'l10.In', target: [0, 50], width: 440, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l10.Wellington', target: [-20, -40], width: 300, pitch: 46, yaw: 14, mm: 35, ease: 'inOut' },
    { at: 'l10.horses', target: [-10, -40], width: 270, pitch: 56, yaw: 10, mm: 35, ease: 'inOut' },
    // l11 far to the east
    { at: 'l11.Meanwhile,', target: [220, 10], width: 640, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l11.marching,', target: [270, 10], width: 560, pitch: 50, yaw: -14, mm: 35, ease: 'inOut' },
    { at: 'l11.but', target: [240, 40], width: 440, pitch: 46, yaw: -10, mm: 35, ease: 'inOut' },
    // l12 evening
    { at: 'l12.By', target: [200, 80], width: 340, pitch: 42, yaw: -8, mm: 35, ease: 'inOut' },
    { at: 'l12.so', target: [0, 140], width: 330, pitch: 34, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l12.the#1', target: [0, 50], width: 400, pitch: 30, yaw: 0, mm: 35, ease: 'inOut' },
    // l13 the volley, the rout
    { at: 'l13.Wellington', target: [10, -10], width: 300, pitch: 26, yaw: 6, mm: 35, ease: 'inOut' },
    { at: 'l13.guard-0.4', target: [0, 50], width: 420, pitch: 36, yaw: -6, mm: 35, ease: 'inOut' },
    { at: 'l13.And#1', target: [0, 100], width: 640, pitch: 60, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l13.ran.+0.9', target: [0, 100], width: 640, pitch: 60, yaw: 0, mm: 35, ease: 'linear' },
    // l14 the quote (low evening sweep), l15 four days later
    { at: 'l14.Wellington', target: [0, 20], dist: 560, pitch: 16, yaw: 50, mm: 30, ease: 'inOut' },
    { at: 'l15.Four', target: [0, 116], dist: 300, pitch: 20, yaw: 120, mm: 30, ease: 'inOut' },
    { at: 143.5, target: [0, 116], dist: 280, pitch: 20, yaw: 130, mm: 30, ease: 'linear' },
  ],

  labels: [
    // l03 Belgium
    { at: 'l03.Belgium,', until: 'l03.British', text: 'BELGIUM', screen: [0.5, 0.13], big: true },
    { at: 'l03.him', until: 'l04.Napoleon\'s', text: 'NAPOLEON', pos: [0, 128], y: 22, team: 'carthage', dy: -0.17, big: true },
    { at: 'l03.British', until: 'l03.and', text: 'WELLINGTON\'S ARMY', block: 'wel2', team: 'rome', dy: -0.17, dx: 0.1, big: true },
    { at: 'l03.Prussian', until: 'l03.who', text: 'PRUSSIANS', block: 'pr1', team: 'green', dy: -0.17, dx: -0.12, big: true },
    { at: 'l03.Blücher,', until: 'l03.a', text: 'BLÜCHER', block: 'pr3', team: 'green', dy: -0.12, dx: 0.0 },
    { at: 'l03.72', until: 'l04.Napoleon\'s', text: '72 YEARS OLD', block: 'pr3', team: 'green', dy: -0.24, dx: 0.02, big: true },
    { at: 'l03.never,', until: 'l04.Napoleon\'s', text: 'NEVER GAVE UP', block: 'pr1', team: 'green', dy: -0.1, dx: -0.3 },
    // l04 the plan
    { at: 'l04.one', until: 'l05.On', text: 'ONE AT A TIME', screen: [0.5, 0.14], big: true, team: 'carthage' },
    { at: 'l04.join', until: 'l05.On', text: 'KEEP THEM APART', screen: [0.5, 0.86], big: true },
    // l05 the ridge
    { at: 'l05.18th', until: 'l05.Wellington', text: '18 JUNE 1815', screen: [0.5, 0.13], big: true },
    { at: 'l05.low', until: 'l05.Most', text: 'THE RIDGE', pos: [0, -36], y: 14, team: 'rome', dy: -0.14, big: true },
    { at: 'l05.Waterloo.', until: 'l05.Most', text: 'WATERLOO', pos: [8, -200], dy: -0.06, leader: false },
    { at: 'l05.behind', until: 'l06.In', text: 'HIDDEN BEHIND THE CREST', pos: [0, -58], y: 10, team: 'rome', dy: -0.2, big: true },
    { at: 'l05.guns.', until: 'l06.In', text: 'FRENCH GUNS', pos: [0, 120], y: 12, team: 'carthage', dy: -0.12, big: true },
    // l06 the farms
    { at: 'l06.Hugo', until: 'l06.Laisant', text: 'HOUGOUMONT', pos: [-96, 14], y: 14, team: 'rome', dy: -0.16, big: true },
    { at: 'l06.on', until: 'l06.Laisant', text: 'WEST', pos: [-96, 14], y: 14, dy: 0.21, dx: 0, leader: false },
    { at: 'l06.Laisant', until: 'l07.It', text: 'LA HAYE SAINTE', pos: [2, 24], y: 14, team: 'rome', dy: -0.16, big: true },
    { at: 'l06.in#1', until: 'l07.It', text: 'CENTRE', pos: [2, 24], y: 14, dy: 0.21, leader: false },
    // l07 rain and the lie in
    { at: 'l07.rained', until: 'l07.Napoleon', text: 'IT RAINED ALL NIGHT', screen: [0.5, 0.86], big: true },
    { at: 'l07.waited', until: 'l07.Until', text: 'WAITING FOR THE GROUND TO DRY', screen: [0.5, 0.86], big: true, size: 0.9 },
    { at: 'l07.Until', until: 'l07.it#1', text: 'ALMOST MIDDAY', screen: [0.5, 0.86], big: true },
    { at: 'l07.expensive', until: 'l08.First,', text: 'A VERY EXPENSIVE LIE IN', screen: [0.5, 0.86], big: true },
    // l08 Hougoumont
    { at: 'l08.attacked', until: 'l08.all', text: 'ATTACK', pos: [-100, 50], team: 'carthage', dy: -0.17, big: true },
    { at: 'l08.all', until: 'l08.They', text: 'ALL DAY LONG', screen: [0.5, 0.86], big: true },
    { at: 'l08.never', until: 'l09.Then', text: 'NEVER TAKEN', pos: [-96, 14], y: 14, team: 'rome', dy: -0.2, dx: 0.12, big: true },
    // l09 the centre and the cavalry
    { at: 'l09.marched', until: 'l09.British', text: 'FRENCH INFANTRY', block: 'fr4', team: 'carthage', dy: -0.17, big: true },
    { at: 'l09.charged', until: 'l09.and', text: 'BRITISH CAVALRY CHARGES', block: 'bCav1', team: 'rome', dy: -0.12, dx: 0.28, big: true },
    { at: 'l09.too', until: 'l10.In', text: 'TOO FAR', block: 'bCav2', team: 'rome', dy: -0.2, big: true },
    // l10 the squares
    { at: 'l10.thousands', until: 'l10.Wellington', text: 'FRENCH HORSEMEN', block: 'fCav1', team: 'carthage', dy: -0.16, big: true },
    { at: 'l10.squares', until: 'l10.like', text: 'SQUARES', block: 'wel3', team: 'rome', dy: -0.2, big: true },
    { at: 'l10.hedgehogs', until: 'l10.horses', text: 'HEDGEHOGS OF BAYONETS', block: 'wel4', team: 'rome', dy: -0.24, big: true, size: 0.9 },
    { at: 'l10.not', until: 'l11.Meanwhile,', text: 'THEY WILL NOT CHARGE', screen: [0.5, 0.86], big: true },
    // l11 the Prussians
    { at: 'l11.east,', until: 'l11.through', text: 'FAR TO THE EAST', screen: [0.5, 0.13], big: true },
    { at: 'l11.bluecares\'', until: 'l11.through', text: 'PRUSSIANS', block: 'pr1', team: 'green', dy: -0.16, big: true },
    { at: 'l11.through', until: 'l11.late,', text: 'THROUGH MUD', pos: [330, -34], team: 'green', dy: -0.17, big: true },
    { at: 'l11.late,', until: 'l11.but', text: 'LATE', pos: [260, 22], team: 'green', dy: -0.17, big: true },
    { at: 'l11.coming.', until: 'l12.By', text: 'BUT COMING', pos: [214, 70], team: 'green', dy: -0.17, big: true },
    // l12 evening
    { at: 'l12.evening,', until: 'l12.so', text: 'EVENING', screen: [0.5, 0.13], big: true },
    { at: 'l12.smashing', until: 'l12.so', text: 'PLANCENOIT', pos: [205, 100], y: 8, team: 'green', dy: -0.17, big: true },
    { at: 'l12.smashing', until: 'l12.so', text: 'NAPOLEON\'S SIDE', pos: [205, 100], y: 8, dy: 0.1, dx: -0.2, leader: false },
    { at: 'l12.Imperial', until: 'l13.Wellington', text: 'IMPERIAL GUARD', block: 'guard', team: 'carthage', dy: -0.18, big: true },
    { at: 'l12.last', until: 'l12.the#1', text: 'LAST AND BEST', block: 'guard', team: 'carthage', dy: -0.17, dx: 0.1 },
    // l13 the volley
    { at: 'l13.tall', until: 'l13.guard', text: 'TALL CORN', pos: [80, -26], y: 2, team: 'rome', dy: 0.14, dx: 0.14, big: true },
    { at: 'l13.fired.', until: 'l13.guard', text: 'FIRE', screen: [0.5, 0.86], team: 'rome', big: true, size: 1.3 },
    { at: 'l13.back.', until: 'l13.whole', text: 'THE GUARD FALLS BACK', block: 'guard', team: 'carthage', dy: -0.17, big: true },
    { at: 'l13.ran.', until: 'l13.ran.+1.3', text: 'RUN', screen: [0.5, 0.86], big: true, team: 'carthage', size: 1.3 },
    // l15 four days later
    { at: 'l15.Four', until: 'l15.This', text: 'FOUR DAYS LATER', screen: [0.5, 0.13], big: true },
    { at: 'l15.Napoleon', until: 'l15.This', text: 'NAPOLEON GIVES UP THE THRONE', screen: [0.5, 0.86], big: true, size: 0.9 },
  ],

  counters: [],

  icons: [
    // l03 Napoleon, the commanders
    { at: 'l03.him', until: 'l07.expensive', icon: 'hat', pos: [0, 128], y: 6, size: 24, anim: 'bounce' },
    { at: 'l03.Duke', until: 'l03.and', icon: 'helmet', team: 'rome', block: 'wel2', size: 22, anim: 'sway', dy: -0.02 },
    { at: 'l03.Marshal', until: 'l04.Napoleon\'s', icon: 'helmet', team: GREEN, block: 'pr3', size: 22, anim: 'sway', dy: -0.02 },
    { at: 'l03.72', until: 'l04.Napoleon\'s', icon: 'star', team: GREEN, block: 'pr4', size: 14, anim: 'bounce', dy: -0.04 },
    { at: 'l04.join', until: 'l05.On', icon: 'no', pos: [140, -80], y: 8, size: 30 },
    // l05 French guns
    ...[-200, -140, -80, -20, 40, 100, 160].map((x, i) => ({ at: { line: 'l05', word: 'guns.', offset: -0.45 + i * 0.07 }, until: 'l06.In', icon: 'cannon', pos: [x, 120], y: 4, size: 15, flip: true })),
    // l06 forts
    { at: 'l06.farmhouses,', until: 'l07.It', icon: 'farm', pos: [-96, 14], y: 3, size: 24, anim: 'bounce' },
    { at: 'l06.farmhouses,+0.35', until: 'l07.It', icon: 'farm', pos: [2, 24], y: 3, size: 24, anim: 'bounce' },
    { at: 'l06.forts.', until: 'l07.It', icon: 'flag', team: 'rome', pos: [-96, 14], y: 28, size: 18 },
    { at: 'l06.forts.+0.3', until: 'l07.It', icon: 'flag', team: 'rome', pos: [2, 24], y: 28, size: 18 },
    // l07 rain, clock, sun, bed
    ...[0.14, 0.32, 0.5, 0.68, 0.86].map((x, i) => ({ at: { line: 'l07', word: 'rained', offset: i * 0.12 }, until: 'l07.Napoleon', icon: 'rain', screen: [x, 0.3 + (i % 2) * 0.06], size: 0.2, anim: 'none' })),
    { at: 'l07.waited', until: 'l07.it#1', icon: 'clock', pos: [-36, 128], y: 22, size: 34, anim: 'bounce' },
    { follow: 'sun', at: 'l07.Until', until: 'l07.it#1', icon: 'sun', size: 30, y: 26, anim: 'none' },
    { at: 'l07.lie', until: 'l08.First,', icon: 'bed', pos: [0, 128], y: 6, size: 34 },
    { at: 'l07.lie', until: 'l08.First,', icon: 'hat', pos: [-6, 128], y: 22, size: 14, anim: 'bounce' },
    // l08
    { at: 'l08.never', until: 'l09.Then', icon: 'check', pos: [-96, 14], y: 30, size: 22, dx: -0.08 },
    { at: 'l08.all', until: 'l08.They', icon: 'clock', pos: [-60, 60], y: 20, size: 28 },
    // l09
    { at: 'l09.too', until: 'l10.In', icon: 'oops', block: 'bCav2', size: 20, anim: 'bounce', dx: 0.04, dy: -0.07 },
    // l10 hedgehogs
    { at: 'l10.hedgehogs', until: 'l10.horses', icon: 'hedgehog', team: 'rome', block: 'wel3', size: 34, anim: 'bounce' },
    { at: 'l10.hedgehogs', until: 'l10.horses', icon: 'hedgehog', team: 'rome', block: 'wel4', size: 34, anim: 'bounce' },
    { at: 'l10.not', until: 'l11.Meanwhile,', icon: 'no', pos: [4, -44], y: 18, size: 26 },
    // l11 mud, clock
    { at: 'l11.through', until: 'l11.late,', icon: 'rain', team: GREEN, pos: [330, -34], y: 14, size: 28 },
    { at: 'l11.late,', until: 'l12.By', icon: 'clock', pos: [260, 22], y: 18, size: 28, anim: 'bounce' },
    // l12 evening
    { at: 'l12.smashing', until: 'l12.so', icon: 'burst', pos: [200, 98], y: 6, size: 34, anim: 'bounce' },
    { at: 'l12.best', until: 'l12.the#1', icon: 'star', block: 'guard', size: 14, anim: 'bounce', dy: -0.02 },
    // l13 the rout
    { at: 'l13.fired.', until: 'l13.guard', icon: 'burst', pos: [4, 30], y: 12, size: 24 },
    // l14 quote helper (the Duke, on the dark plate)
    { at: 'l14.Wellington', until: 'l15.Four', icon: 'helmet', team: 'rome', screen: [0.5, 0.2], size: 0.14, anim: 'sway' },
    // l15
    { at: 'l15.Napoleon', until: 'l15.This', icon: 'hat', pos: [0, 128], y: 6, size: 30, anim: 'bounce' },
    { at: 'l15.gave', until: 'l15.This', icon: 'crown', pos: [0, 128], y: 28, size: 22, fallAt: 'l15.throne.', fallDur: 0.8 },
  ],

  arrows: [
    // l04 the plan: beat them one at a time
    { id: 'p1', at: 'l04.beat', until: 'l04.them', ease: 'out', team: 'carthage', width: 7, path: [[0, 112], [-6, 20]], lift: 6, hide: 'l05.On' },
    { id: 'p2', at: 'l04.one', until: 'l04.time', ease: 'out', team: 'carthage', width: 6, path: [[120, 120], [250, 40], [300, 12]], lift: 6, hide: 'l05.On' },
    { at: 'l04.before', until: 'l04.up.', ease: 'out', team: 'rome', width: 5, style: 'dash', path: [[40, -100], [160, -60], [260, -10]], lift: 6, hide: 'l05.On' },
    { at: 'l04.before', until: 'l04.up.', ease: 'out', team: 'green', width: 5, style: 'dash', path: [[320, -40], [200, -76], [80, -92]], lift: 6, hide: 'l05.On' },
    // l07 the sun climbs
    { id: 'sun', at: 'l07.Until', until: 'l07.midday,', ease: 'linear', team: 'gold', style: 'dash', width: 2.4, path: [[-120, 150], [-70, 128], [0, 112], [70, 128], [120, 150]], lift: 40, hide: 'l08.First,' },
    // l08 Hougoumont attacks
    ...[['attacked', 0], ['day', 0], ['They', 0]].flatMap(([w]) => [
      { at: { line: 'l08', word: w }, dur: 0.8, ease: 'out', team: 'carthage', width: 4.4, path: [[-170, 100], [-130, 52]], lift: 6, hide: { line: 'l08', word: w, offset: 1.6 } },
      { at: { line: 'l08', word: w, offset: 0.2 }, dur: 0.8, ease: 'out', team: 'carthage', width: 4.4, path: [[-110, 104], [-72, 58]], lift: 6, hide: { line: 'l08', word: w, offset: 1.6 } },
    ]),
    // l09 the centre
    { at: 'l09.marched', dur: 1.6, ease: 'out', team: 'carthage', width: 6, path: [[-10, 100], [-10, 30]], lift: 6, hide: 'l09.British' },
    { at: 'l09.charged', dur: 1.2, ease: 'out', team: 'rome', width: 6, path: [[0, -50], [0, 24]], lift: 6, hide: 'l09.and' },
    { at: 'l09.back', dur: 0.9, ease: 'out', team: 'rome', width: 5, path: [[0, 24], [0, 80]], lift: 6, hide: 'l09.and' },
    { at: 'l09.too', until: 'l09.far.', ease: 'inOut', team: 'rome', width: 5, style: 'dash', path: [[0, 80], [-6, 116], [-4, 138]], lift: 6, hide: 'l10.In' },
    // l11 the Prussian route from the east (late but coming)
    { id: 'route', at: 'l11.marching,', until: 'l11.coming.', ease: 'inOut', team: 'green', style: 'dash', width: 4, path: [[440, -66], [400, -62], [330, -34], [260, 22], [214, 70], [190, 92]], lift: 6, hide: 'l12.By' },
    // l12 the Guard climbs the ridge
    { at: 'l12.straight', until: 'l12.ridge.', ease: 'inOut', team: 'carthage', width: 6, path: [[0, 140], [2, 60], [2, -10]], lift: 6, hide: 'l13.Wellington' },
    { at: 'l12.smashing', until: 'l12.smashing+1.2', ease: 'out', team: 'green', width: 5, path: [[230, 70], [200, 100]], lift: 6, hide: 'l12.so' },
    // l13 the rout
    ...[-1, 1].map((s) => ({ at: 'l13.ran.', until: 'l13.ran.+1.1', ease: 'out', team: 'carthage', width: 5, path: [[s * 30, 150], [s * 120, 240]], lift: 6, hide: 'l14.Wellington' })),
  ],
  // squares and hedgehogs are bayonet red; arrows off the squares show the points
  volleys: [
    { at: 'l13.fired.', dur: 1.2, from: { block: 'wel3' }, to: { block: 'guard' }, n: 34, flight: 0.8, spread: 0.35, team: 'rome' },
    { at: 'l13.fired.+0.2', dur: 1.2, from: { block: 'wel4' }, to: { block: 'guard' }, n: 34, flight: 0.8, spread: 0.35, team: 'rome' },
  ],

  cards: [
    { at: 0, until: 1.0, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    // title on l01
    { at: 10.7, until: 15.0, scrim: 0.88, scrimCenter: 'rgba(20,10,4,0.82)', fadeIn: 0.25, fadeOut: 0.7, lines: [
      { text: 'THE BATTLE OF WATERLOO', size: 0.078, y: 0.44, delay: 0 },
      { text: '1815', size: 0.07, y: 0.585, delay: 0.95, colorTop: '#ffd9a0', colorBottom: '#e2873a' } ], ornaments: [{ y: 0.35, w: 0.7 }, { y: 0.68, w: 0.7 }] },
    // Wellington's words
    { at: 134.45, until: 139.3, scrim: 0.82, scrimCenter: 'rgba(20,8,6,0.8)', fadeIn: 0.4, fadeOut: 0.7, lines: [
      { text: 'THE DUKE OF WELLINGTON', size: 0.04, y: 0.40, delay: 0.1, colorTop: '#ffb8a0', colorBottom: '#e0644a', weight: 600 },
      { text: '"THE NEAREST RUN THING', size: 0.06, y: 0.52, delay: 1.7 },
      { text: 'YOU EVER SAW IN YOUR LIFE"', size: 0.06, y: 0.63, delay: 2.9 } ], ornaments: [{ y: 0.34, w: 0.7 }, { y: 0.7, w: 0.7 }] },
    // the dictionary plate
    { at: 148.95, until: 154.0, fill: 'rgb(238,226,192)', fillAlpha: 0.97, fadeIn: 0.5, fadeOut: 0.5, lines: [
      { text: 'WATERLOO', size: 0.105, y: 0.29, delay: 0.1, stroke: 'rgba(0,0,0,0)', shadow: false, colorTop: '#4a2a14', colorBottom: '#2e180a', track: 0.12 },
      { text: 'idiom', size: 0.05, y: 0.40, delay: 0.5, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#6a4a2a', colorBottom: '#6a4a2a' },
      { text: 'to meet your Waterloo', size: 0.07, y: 0.52, delay: 1.2, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.03, colorTop: '#3a2412', colorBottom: '#3a2412' },
      { text: 'to meet the one thing', size: 0.062, y: 0.66, delay: 2.85, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.03, colorTop: '#3a2412', colorBottom: '#3a2412' },
      { text: 'that finally beats you', size: 0.062, y: 0.76, delay: 3.85, stroke: 'rgba(0,0,0,0)', shadow: false, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.03, colorTop: '#8a2a1a', colorBottom: '#8a2a1a' } ], ornaments: [{ y: 0.18, w: 0.5 }, { y: 0.88, w: 0.5 }] },
    // end card
    { at: 154.306, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.88, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.13, y: 0.43, delay: 0.1, track: 0.14 },
      { text: 'The Battle of Waterloo, 1815', size: 0.062, y: 0.6, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.5 }, { y: 0.69, w: 0.5 }] },
  ],

  insets: [
    { stage: 'eur', at: 0, until: 28.95, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.01, out: 0.01 },
    { stage: 'eurW', at: 'l02.all', until: 28.95, rect: [0, 0, 1, 1], frame: false, pop: false, in: 1.1, out: 0.01 },
    { stage: 'atl', at: 'l15.This', until: 170, rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.01, out: 0.01 },
  ],
};

// Wellington's blocks line up on the crest, then wait behind it until the afternoon
WX.forEach((x, i) => {
  const id = 'wel' + (i + 1);
  spec.moves.push({ block: id, at: { line: 'l05', word: 'lined', offset: i * 0.14 }, dur: 2.6, to: { x, z: -40, len: 66, dep: 16 }, ease: 'inOut' });
  spec.moves.push({ block: id, at: 'l05.Most', dur: 2.2, to: { z: -58 }, ease: 'inOut' });
});

export default spec;
