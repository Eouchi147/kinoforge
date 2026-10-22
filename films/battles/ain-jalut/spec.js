// The Battle of Ain Jalut (1260): Battle Map v2 spec (engine: films/lib/battlemap/SPEC.md; scene list and reasons: NOTES.md).
// Two maps. Stage `emp`: a stylised map of Asia, the Middle East and Eastern Europe (1 degree of longitude = 6 units, 1 degree of latitude = 8 units;
// not to scale for the Levant). It carries the opening, the empire, the letters, the march and the epilogue. The main stage is the battlefield:
// a valley floor running west to east between two lines of hills, Goliath's Spring in the west. Mamluks red ('rome'), Mongols blue ('carthage').
// Film-side: kinds.js (the horse-archer unit symbol), fx.js (the empire as ink spreading over the map).
const MAM = { team: 'rome' }, MON = { team: 'carthage' };
const P = (lon, lat) => [Math.round((lon - 70) * 6 * 10) / 10, Math.round((38 - lat) * 8 * 10) / 10];
const PP = (a) => a.map(([lo, la]) => P(lo, la));
const RED = [0.74, 0.12, 0.12], BLUE = [0.15, 0.33, 0.74];

// ------------------------------------------------------------------ the empire map
const eurasia = PP([[-15, 75], [150, 75], [150, 60], [142, 52], [135, 44], [130, 42.5], [129.5, 40], [128, 38], [129, 35.2], [126.5, 34.5], [126, 37.5], [124.5, 39.8], [121.5, 40.3], [118, 39], [119, 37], [122.5, 37.2], [120, 35], [121, 32], [122, 30], [120, 27], [118, 24.5], [114, 22.3], [110, 21], [108, 21.5], [106.5, 19], [108, 15], [109, 11.5], [105, 8.5], [100, 8], [98.5, 10], [98, 13], [97.5, 16.5], [94.5, 16], [94, 19], [92, 21.5], [89.5, 21.7], [86.5, 20.5], [84.5, 18.5], [82, 16], [80.2, 13], [79.8, 10.2], [78, 8.2], [77, 8.1], [76.2, 9.8], [75, 13], [73.5, 17], [72.8, 19.5], [72.8, 21.2], [70.5, 20.8], [69, 22.5], [68, 23.5], [66.5, 25], [62, 25.2], [58, 25.5], [57, 27], [54, 26.7], [51.5, 27.8], [50, 29.5], [48.5, 30], [47.8, 29.4], [48.5, 28.2], [50, 26.4], [51.4, 25], [51.6, 24.3], [54, 24.1], [55.5, 25.5], [56.5, 26.2], [56.4, 24.5], [58.5, 23.5], [59.8, 22.4], [58, 20], [56, 17.8], [52.5, 16.3], [49, 14.6], [45, 12.8], [43.4, 12.7], [42.8, 14.5], [41.5, 17], [39.5, 21.5], [37.5, 24.5], [35.2, 27.8], [34.9, 29.5], [32.8, 29.9], [32.6, 28.5], [33.7, 27], [35.5, 24], [37, 21], [38.5, 18], [39.5, 15.5], [41.5, 13], [43.2, 11.8], [44.5, 10.5], [47, 11.2], [51.2, 11.8], [51, 10], [49.5, 6], [46, 2], [46, -5], [-15, -5]]);
const med = PP([[-1, 36.3], [3, 36.8], [8, 37], [10.2, 37.2], [11, 36.8], [10.3, 34.5], [11.2, 33.2], [15, 32.3], [19, 30.3], [20, 32.3], [25, 31.6], [30, 31], [32.5, 31.1], [34.3, 31.3], [34.9, 32.8], [35.6, 34.4], [35.9, 35.8], [36.2, 36.7], [34, 36.6], [30.5, 36.3], [28, 36.7], [26, 36.2], [23.2, 36.4], [21.5, 38], [19.8, 40.2], [18.6, 40.1], [16.5, 38.8], [15.6, 38], [15.8, 40], [14, 41.2], [12, 42], [10.2, 43.8], [8.5, 44.2], [6, 43.2], [3.3, 43], [0.5, 40.2], [-1, 38], [-1.5, 36.8]]);
const adriatic = PP([[19.4, 41.6], [18.4, 42.4], [16.2, 43.5], [14.2, 44.8], [13.3, 45.6], [12.3, 44.8], [14.2, 42.5], [16.2, 41.7], [18.2, 40.4]]);
const black = PP([[28.2, 43.5], [28.8, 41.3], [32, 41.2], [36, 41.7], [40, 41], [41.6, 41.6], [41.2, 43], [37.6, 44.8], [36.4, 45.4], [34, 44.6], [33, 45.5], [31, 46.6], [30, 45.4], [29, 44.5]]);
const caspian = PP([[47, 45], [50, 46.6], [53, 46.8], [53.6, 44], [51.6, 43], [52.6, 41], [53, 39.5], [54, 37.5], [51, 36.7], [49, 38], [49, 40.5], [48.5, 42], [47.5, 43.6]]);
const balkash = PP([[74, 46.5], [77, 46.8], [79, 45.8], [77, 45.2], [74.6, 45.6]]);
const CAIRO = P(31.3, 30.1), DAMASCUS = P(36.3, 33.5), BAGHDAD = P(44.4, 33.3), KARAKORUM = P(102.8, 47.2), AINJ = P(35.4, 32.55);
const emp = {
  world: {
    seed: 1260, size: [880, 520], res: 1, base: 0, meshStep: 3,
    sun: { azimuth: 240, elevation: 33 }, sunEve: { azimuth: 270, elevation: 8 },
    style: { contour: 4, pxPerUnit: 4.6, palette: [[-4, [0.70, 0.74, 0.46]], [1.5, [0.74, 0.75, 0.46]], [4, [0.82, 0.72, 0.46]], [8, [0.78, 0.63, 0.43]], [12, [0.68, 0.58, 0.48]], [16, [0.80, 0.78, 0.76]], [22, [0.96, 0.96, 0.97]]], paletteSoft: 5, fields: 0.15 },
    features: [
      { type: 'undulate', amp: 3, scale: 110 }, { type: 'undulate', amp: 1.0, scale: 34 },
      { type: 'mountains', path: PP([[72, 35], [82, 31], [92, 30], [102, 29.5]]), w: 52, h: 15, scale: 70, ridged: 0.8, edge: 30 },
      { type: 'mountains', path: PP([[76, 42.5], [86, 44], [97, 49]]), w: 42, h: 12, scale: 60, ridged: 0.8, edge: 25 },
      { type: 'mountains', path: PP([[64, 35.5], [72, 36.5]]), w: 26, h: 10, scale: 50, ridged: 0.8, edge: 20 },
      { type: 'mountains', path: PP([[39.5, 43.2], [48, 41.2]]), w: 15, h: 9, scale: 40, ridged: 0.8, edge: 12 },
      { type: 'mountains', path: PP([[45.5, 35], [53, 28.5]]), w: 22, h: 8, scale: 45, ridged: 0.7, edge: 14 },
      { type: 'mountains', path: PP([[30, 37], [40, 38.2]]), w: 14, h: 7, scale: 40, ridged: 0.7, edge: 10 },
      { type: 'mountains', path: PP([[6, 46.2], [14, 47]]), w: 16, h: 8, scale: 40, ridged: 0.8, edge: 10 },
      { type: 'sea', poly: [[-500, -300], [500, -300], [500, 300], [-500, 300]], shelf: 30, depth: 8 },
      { type: 'land', poly: eurasia, shelf: 12, beach: 5, wob: 1.2 },
      { type: 'lake', poly: med, shelf: 10, beach: 5, smooth: 2 },
      { type: 'lake', poly: adriatic, shelf: 6, beach: 3, smooth: 1 },
      { type: 'lake', poly: black, shelf: 8, beach: 4 }, { type: 'lake', poly: caspian, shelf: 8, beach: 4 }, { type: 'lake', poly: balkash, shelf: 6, beach: 3 },
      { type: 'river', name: 'Nile', path: PP([[31.6, 23.5], [32.4, 26], [31.2, 28.5], [31.2, 30], [31.4, 31.4]]), w: 3.2, depth: 1.2, meander: 2, bank: 1.5 },
      { type: 'river', name: 'Euphrates', path: PP([[38.5, 37], [40, 35.5], [43, 33.6], [46, 31.5], [48, 30.3]]), w: 2.6, depth: 1.0, meander: 3, bank: 1.5 },
      { type: 'river', name: 'Yellow', path: PP([[100, 35.5], [106, 40.5], [111, 39], [112, 35], [118, 37.4]]), w: 2.8, depth: 1.0, meander: 3, bank: 1.5 },
      { type: 'river', name: 'Volga', path: PP([[41, 57], [45, 55], [47, 50], [47.6, 46]]), w: 2.4, depth: 1.0, meander: 3, bank: 1.5 },
      { type: 'river', name: 'Danube', path: PP([[9, 48.2], [17, 48], [20, 46.5], [26, 44], [29, 45]]), w: 2.2, depth: 1.0, meander: 3, bank: 1.5 },
    ],
  },
  look: { fogDensity: 0.00025, edgeStart: 2000, edgeEnd: 3000, worldEdge: 40 },
  ambient: { wind: [1, 0.2], gusts: 0.3, flow: { dir: [1, 0.1], speed: 0.5, glint: 1.1 },
    birds: [{ center: P(36, 31.5), r: 16, h: 12, n: 5, speed: 4 }, { center: P(60, 44), r: 40, h: 20, n: 6, speed: 6, dir: -1 }] },
  blocks: {
    hul: { ...MON, kind: 'cavalry', x: P(52, 34.5)[0], z: P(52, 34.5)[1], heading: 270, len: 10, dep: 5, hidden: true, bannerScale: 1.0, figScale: 1.4 },
    kit: { ...MON, kind: 'cavalry', x: P(52, 33)[0], z: P(52, 33)[1], heading: 270, len: 6, dep: 4, hidden: true, bannerScale: 0.8, figScale: 1.4 },
    qut: { ...MAM, kind: 'elite', x: P(34.4, 31.9)[0], z: P(34.4, 31.9)[1], heading: 90, len: 6, dep: 4, hidden: true, bannerScale: 0.8, figScale: 1.4 },
    bay: { ...MAM, kind: 'cavalry', x: P(31.2, 30.2)[0], z: P(31.2, 30.2)[1], heading: 45, len: 5, dep: 3, hidden: true, bannerScale: 0.7, figScale: 1.4 },
  },
  moves: [
    // the hook: the horde rides out of Persia into Palestine; there an army is waiting
    { blocks: ['hul', 'kit'], at: 'l00.armies', dur: 0.8, stagger: 0.2, appear: true },
    { block: 'hul', at: 'l00.rode', until: 'l00.met', path: PP([[50, 34.3], [45, 34.6], [40.5, 34.2], [37.4, 34.2]]), ease: 'cam' },
    { block: 'kit', at: 'l00.rode+0.2', until: 'l00.met+0.2', path: PP([[50, 33], [45, 33.4], [40.5, 33.2], [36.8, 33.2]]), ease: 'cam' },
    { block: 'qut', at: 'l00.army', dur: 0.8, appear: true },
    { block: 'qut', at: 13.6, dur: 0.6, vanish: true },
    { block: 'qut', at: 16.5, dur: 0.1, to: { x: CAIRO[0] + 2, z: CAIRO[1] - 2, heading: 60 }, ease: 'linear' },
    { block: 'qut', at: 'l03.Mamluks,', dur: 0.8, appear: true },
    // the Great Khan dies far away: Hulagu takes most of the army back east; a smaller army stays under Kitbuqa
    { block: 'hul', at: 'l04.took', until: 'l04.east.>', path: PP([[40, 35.5], [50, 38.5], [64, 42], [80, 44.5], [96, 46.5]]), ease: 'cam' },
    { block: 'hul', at: 'l04.He', dur: 1.0, vanish: true },
    // Qutuz and Baybars march out of Egypt
    { block: 'bay', at: 'l05.toughest', dur: 0.8, appear: true },
    { block: 'qut', at: 'l05.marched', dur: 3.6, path: PP([[31.6, 30.6], [32.6, 31.2], [34.2, 32.0], [35.0, 32.3]]), ease: 'cam' },
    { block: 'bay', at: 'l05.marched+0.4', dur: 3.6, path: PP([[31.6, 30.4], [32.8, 31.3], [34.4, 32.2], [35.2, 32.6]]), ease: 'cam' },
    { block: 'kit', at: 'l05.marched', dur: 2.4, path: PP([[36, 33.0], [35.6, 32.8]]), ease: 'cam' },
    // the epilogue: Kitbuqa's army is gone; the Mamluks ride home; on the way Baybars gets rid of Qutuz
    { block: 'kit', at: 'l14', dur: 0.1, vanish: true },
    { blocks: ['qut', 'bay'], at: 'l14', dur: 0.1, to: { heading: 250 }, ease: 'linear' },
    { block: 'qut', at: 'l15.home', until: 'l15.rid', path: PP([[34.2, 32.0], [33.2, 31.4]]), ease: 'cam' },
    { block: 'bay', at: 'l15.home', until: 'l15.rid', path: PP([[34.4, 32.2], [33.4, 31.7]]), ease: 'cam' },
    { block: 'qut', at: 'l15.rid', dur: 1.2, vanish: true },
    { block: 'bay', at: 'l15.made', dur: 3.4, path: PP([[32.4, 31.0], [31.6, 30.5]]), ease: 'cam' },
  ],
  arrows: [
    { at: 'l00.rode', until: 'l00.Palestine', ease: 'cam', team: 'carthage', width: 4, path: PP([[50, 34.3], [45, 34.6], [40.5, 34.2], [36.4, 33.4]]), lift: 6, hide: 'l00.army' },
    { at: 'l02.stretched', until: 'l02.Europe.>', ease: 'cam', team: 'carthage', width: 6, path: PP([[119, 42], [100, 43.5], [76, 43], [52, 46], [32, 48], [19, 47.5]]), lift: 8, hide: 'l02.Two' },
    { id: 'msg', at: 'l03.sent', until: 'l03.Egypt,>', ease: 'cam', team: 'carthage', style: 'dash', width: 2, path: PP([[36.2, 33.4], [35, 32.6], [33.4, 31.4], [31.8, 30.4]]), lift: 5, hide: 'l03.The' },
    { id: 'rep', at: 'l03.sent#1', until: 'l03.answer.>', ease: 'cam', team: 'rome', style: 'dash', width: 2, path: PP([[31.8, 30.4], [33.4, 31.4], [35, 32.6], [36.2, 33.4]]), lift: 5, hide: 'l04' },
    { at: 'l04.took', until: 'l04.east.>', ease: 'cam', team: 'carthage', width: 6, path: PP([[40, 35.5], [50, 38.5], [64, 42], [80, 44.5], [96, 46.5]]), lift: 8, hide: 'l04.He' },
    { at: 'l05.marched', until: 'l05.Beybars.>', ease: 'cam', team: 'rome', width: 2.4, path: PP([[31.6, 30.5], [32.6, 31.2], [34.2, 32.0], [35.1, 32.4]]), lift: 5, hide: 'l06' },
    { at: 'l14.could', until: 'l14.revenge.>', ease: 'cam', team: 'carthage', style: 'dash', width: 5, path: PP([[100, 46.5], [84, 44.5], [66, 41.5], [52, 38.5], [44, 36]]), lift: 8, hide: 'l14.They#1' },
    { at: 'l14.They#1', until: 'l14.conquered', ease: 'cam', team: 'carthage', width: 3, head: false, path: PP([[35.5, 32.3], [34.4, 31.4], [33.6, 30.8]]), lift: 5, hide: 'l15' },
    { at: 'l14.conquered', dur: 0.9, ease: 'out', team: 'gold', style: 'dash', width: 2.2, head: false, taper: 1, path: PP([[32.4, 31.6], [33.4, 30.6], [34.4, 29.6]]), lift: 6, hide: 'l15' },
  ],
  icons: [
    { follow: 'msg', at: 'l03.message', until: 'l03.Egypt,>', icon: 'scroll', team: 'carthage', size: 18, minPx: 0.045, maxPx: 0.06 },
    { follow: 'rep', at: 'l03.sent#1', until: 'l03.answer.>', icon: 'scroll', team: 'rome', size: 18, minPx: 0.045, maxPx: 0.06 },
  ],
  ink: [
    { at: 2.4, spread: 4.2, grow: 1.0, origin: P(100, 47), color: [0.22, 0.40, 0.86], dark: [0.08, 0.14, 0.40], alpha: 0.38,
      blobs: [[100, 47, 10], [118, 43, 8], [112, 34, 8], [124, 48, 5], [88, 42, 9], [73, 40, 9], [62, 36, 8], [53, 33, 8], [46, 36, 6], [44, 32.5, 5], [38, 35.8, 5], [37, 33.8, 3.4], [34, 38, 4.5], [95, 57, 9], [75, 56, 9], [110, 53, 7], [60, 50, 10], [48, 47, 8], [40, 55, 9], [33, 50, 8], [25, 50, 6.5], [19, 47, 4.5], [22, 54, 5], [85, 33, 7]].map(([lo, la, r]) => [...P(lo, la), r * 6.3]) },
    { at: 'l16.rule', spread: 1.6, grow: 1.0, origin: P(31.3, 30.2), color: [0.82, 0.16, 0.14], dark: [0.34, 0.05, 0.04], alpha: 0.5,
      blobs: [[31.3, 30.2, 3.2], [30.4, 27.6, 3.0], [32, 25, 2.6], [29.5, 30.4, 3.0], [33.2, 29.6, 2.2], [26.5, 30.2, 3.0], [30.5, 25, 3.2], [35.2, 32.2, 1.6], [36.4, 33.6, 2.0], [37.2, 35, 1.8]].map(([lo, la, r]) => [...P(lo, la), r * 9.5]) },
  ],
  markers: [
    { id: 'kar', at: 1.2, until: 'l00.Their', pos: KARAKORUM, glyph: 'town', team: BLUE, label: 'MONGOLIA', labelUntil: 'l00.Their', size: 0.06, ldy: 0.05 },
    { id: 'pal', at: 'l00.Palestine', until: 'l02', pos: AINJ, glyph: 'plain', label: 'PALESTINE', labelUntil: 13.3, size: 0.05, ldy: 0.05 },
    { id: 'bag', at: 'l02.destroyed', until: 'l04', pos: BAGHDAD, glyph: 'town', team: BLUE, label: 'BAGHDAD, 1258', labelUntil: 'l03', size: 0.05, ldy: 0.05 },
    { id: 'dam', at: 'l02.Damascus.', until: 'l06', pos: DAMASCUS, glyph: 'town', team: BLUE, label: 'DAMASCUS', labelUntil: 'l03.sent', size: 0.05, ldx: 0.05, align: 'left', ldy: -0.01 },
    { id: 'cai', at: 'l03.Egypt,', until: 'l06', pos: CAIRO, glyph: 'town', team: RED, label: 'CAIRO', labelUntil: 'l03.rulers', size: 0.05, ldx: -0.05, align: 'right', ldy: -0.01 },
    { id: 'kar2', at: 'l04.Mongolia,', until: 'l04.He', pos: KARAKORUM, glyph: 'town', team: BLUE, label: 'KARAKORUM', labelUntil: 'l04.took', size: 0.06, ldy: 0.05 },
    { id: 'aj', at: 'l14', until: 170, pos: AINJ, glyph: 'clash', label: 'AIN JALUT', labelUntil: 'l14.In', size: 0.045, ldx: 0.05, align: 'left', ldy: -0.01 },
    { id: 'cai2', at: 'l14', until: 170, pos: CAIRO, glyph: 'town', team: RED, label: 'CAIRO', labelUntil: 'l15', size: 0.05, ldx: -0.05, align: 'right', ldy: -0.01 },
  ],
  labels: [
    { at: 'l02.China', until: 'l02.Two', text: 'CHINA', pos: P(112, 37), leader: false, rule: false },
    { at: 'l02.Eastern', until: 'l02.Two', text: 'EASTERN EUROPE', pos: P(26, 50), leader: false, rule: false },
    { at: 'l03.Hulagu,', until: 'l03.Egypt,', text: 'HULAGU', block: 'hul', team: 'carthage', dx: 0.04, dy: -0.12 },
    { at: 'l04.died,', until: 'l04.took', text: 'AUGUST 1259', screen: [0.5, 0.86], big: true },
    { at: 'l04.Kit', until: 'l05', text: 'KITBUQA', block: 'kit', team: 'carthage', dx: 0.05, dy: -0.12 },
    { at: 'l05.Qutuz', until: 'l05.Beybars.', text: 'SULTAN QUTUZ', block: 'qut', team: 'rome', dx: -0.05, dy: -0.11 },
    { at: 'l05.Beybars.', until: 'l06', text: 'BAYBARS', block: 'bay', team: 'rome', dx: 0.05, dy: 0.1 },
    { at: 'l15.Baybar', until: 'l16', text: 'SULTAN BAYBARS', block: 'bay', team: 'rome', dx: 0.05, dy: -0.12 },
    { at: 'l16.250', until: 140, text: '1260 TO 1517', screen: [0.5, 0.86], big: true },
  ],
};

// ------------------------------------------------------------------ the valley (main stage)
// x east, z south. Valley floor |z| < 45 running west to east; ridges at z = -80 and z = +84; Goliath's Spring in the west.
const SPRING = [-96, 6];
const world = {
  seed: 1260, size: [620, 340], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 232, elevation: 36 }, sunEve: { azimuth: 262, elevation: 8 },
  style: { contour: 1.5, pxPerUnit: 5.2, palette: [[-4, [0.62, 0.66, 0.40]], [1, [0.66, 0.68, 0.40]], [6, [0.76, 0.68, 0.42]], [16, [0.80, 0.66, 0.42]], [30, [0.72, 0.60, 0.44]], [50, [0.68, 0.60, 0.52]], [80, [0.74, 0.70, 0.66]]], paletteSoft: 5, fields: 0.4 },
  features: [
    { type: 'undulate', amp: 3, scale: 120 }, { type: 'undulate', amp: 1.2, scale: 34 },
    { type: 'ridge', path: [[-330, -74], [-200, -82], [-60, -78], [70, -80], [200, -84], [330, -76]], w: 54, h: 38, rough: 0.3, crest: 1.2, meander: 5 },
    { type: 'ridge', path: [[-330, 78], [-200, 86], [-60, 82], [70, 84], [200, 88], [330, 80]], w: 54, h: 36, rough: 0.3, crest: 1.2, meander: 5 },
    { type: 'hill', at: [-140, -150], r: [100, 40], h: 50, rough: 0.2, crag: 0.2 }, { type: 'hill', at: [110, -156], r: [120, 44], h: 56, rough: 0.2, crag: 0.2 },
    { type: 'hill', at: [-120, 154], r: [110, 40], h: 46, rough: 0.2, crag: 0.2 }, { type: 'hill', at: [130, 158], r: [120, 42], h: 52, rough: 0.2, crag: 0.2 },
    ...[-200, -140, -80, -20, 40, 100, 160, 220].map((x) => ({ type: 'flat', at: [x, 0], r: 22, level: 2, soft: 14, amount: 0.9 })),
    { type: 'lake', at: SPRING, r: [14, 9], shelf: 5, beach: 4, depth: 3 },
    { type: 'river', name: 'stream', path: [[-84, 8], [-30, 14], [50, 10], [150, 16], [320, 12]], w: 3.4, depth: 1.2, meander: 3 },
    { type: 'farms', rect: [-215, 8, 110, 56, 0], cell: [26, 16], skip: 0.1, kinds: 3 },
    { type: 'woods', at: [60, -60], r: [60, 12], rot: 0, wob: 0.2 }, { type: 'woods', at: [112, -66], r: [44, 12], rot: 8, wob: 0.2 },
    { type: 'woods', at: [60, 64], r: [60, 12], rot: 0, wob: 0.2 }, { type: 'woods', at: [112, 68], r: [44, 12], rot: -8, wob: 0.2 },
    { type: 'woods', at: [-30, -52], r: [36, 9], wob: 0.2 }, { type: 'woods', at: [-40, 56], r: [36, 9], wob: 0.2 },
    { type: 'road', path: [[-320, -8], [-100, -2], [100, 4], [320, 0]], w: 1.6, meander: 3 },
  ],
};

const MN1 = 'mamN1', MN2 = 'mamN2', MS1 = 'mamS1', MS2 = 'mamS2';
const AM = [MN1, MN2, MS1, MS2];
const blocks = {
  monK: { ...MON, kind: 'cavalry', x: -150, z: 0, heading: 90, len: 26, dep: 12, hidden: true, bannerScale: 1.6 },
  monA: { ...MON, kind: 'light', figures: 'cavalry', x: -150, z: -30, heading: 90, len: 30, dep: 12, hidden: true, bannerScale: 1.0 },
  monB: { ...MON, kind: 'light', figures: 'cavalry', x: -150, z: 30, heading: 90, len: 30, dep: 12, hidden: true, bannerScale: 1.0 },
  bay: { ...MAM, kind: 'cavalry', x: 14, z: 2, heading: 270, len: 22, dep: 10, hidden: true, bannerScale: 1.3 },
  [MN1]: { ...MAM, kind: 'infantry', x: 56, z: -82, heading: 180, len: 40, dep: 14, hidden: true, bannerScale: 1.0 },
  [MN2]: { ...MAM, kind: 'cavalry', x: 108, z: -86, heading: 180, len: 32, dep: 12, hidden: true, bannerScale: 1.0 },
  [MS1]: { ...MAM, kind: 'infantry', x: 56, z: 84, heading: 0, len: 40, dep: 14, hidden: true, bannerScale: 1.0 },
  [MS2]: { ...MAM, kind: 'cavalry', x: 108, z: 88, heading: 0, len: 32, dep: 12, hidden: true, bannerScale: 1.0 },
  qutB: { ...MAM, kind: 'elite', x: 70, z: -66, heading: 180, len: 10, dep: 7, hidden: true, bannerScale: 1.8 },
};
const moves = [
  // 3 September 1260: the Mongols by the spring, Baybars's small force up the valley
  { blocks: ['monK', 'monA', 'monB'], at: 'l06.met', dur: 0.9, stagger: 0.2, appear: true },
  { block: 'bay', at: 'l06.met+0.4', dur: 0.9, appear: true },
  // the trick: Baybars rides out, fights a while, then pretends to run, up the valley; the Mongols charge after him
  { block: 'bay', at: 'l08.rode', dur: 2.0, to: { x: -92, z: 0 }, ease: 'cam' },
  { blocks: ['monA', 'monB'], at: 'l08.rode', dur: 2.0, by: { x: 26 }, ease: 'cam' }, { block: 'monK', at: 'l08.rode', dur: 2.0, by: { x: 16 }, ease: 'cam' },
  { block: 'bay', at: 'l08.pretended', dur: 0.7, to: { heading: 90 }, ease: 'inOut' },
  { block: 'bay', at: 'l08.run', until: 'l09.him.', to: { x: 128, z: 0 }, ease: 'inOut' },
  { blocks: ['monA', 'monB'], at: 'l09.charge', until: 'l10.hills,', by: { x: 158 }, ease: 'in' },
  { block: 'monK', at: 'l09.charge', until: 'l10.hills,', by: { x: 110 }, ease: 'in' },
  // the main army, hidden in the hills, rises; the ambush hits from both sides
  { blocks: AM, at: 'l10.main', dur: 0.9, stagger: 0.2, appear: true }, { block: 'qutB', at: 'l10.army', dur: 0.9, appear: true },
  { block: MN1, at: 'l11.ambush.', dur: 1.9, to: { z: -26, x: 50 }, ease: 'in' },
  { block: MS1, at: 'l11.ambush.', dur: 1.9, to: { z: 28, x: 50 }, ease: 'in' },
  { block: MN2, at: 'l11.ambush.+0.4', dur: 1.9, to: { z: -36, x: 98 }, ease: 'in' },
  { block: MS2, at: 'l11.ambush.+0.4', dur: 1.9, to: { z: 36, x: 98 }, ease: 'in' },
  { block: 'bay', at: 'l11.ambush.', dur: 0.6, to: { heading: 270 }, ease: 'out' }, { block: 'bay', at: 'l11.ambush.+0.4', dur: 2.0, to: { x: 104 }, ease: 'in' },
  // the Mongols fight back and the Mamluk line bends; Qutuz rides into it and the men rally
  { block: 'monA', at: 'l12.fought', dur: 1.2, by: { z: -8, x: 4 }, ease: 'out' }, { block: 'monB', at: 'l12.fought', dur: 1.2, by: { z: 8, x: 4 }, ease: 'out' },
  { block: MN1, at: 'l12.line', dur: 1.6, to: { bulge: -0.3, z: -38 }, ease: 'inOut' },
  { block: MS1, at: 'l12.line+0.2', dur: 1.6, to: { bulge: -0.22, z: 38 }, ease: 'inOut' },
  { block: 'qutB', at: 'l12.Khutuz', dur: 1.6, to: { x: 56, z: -52 }, ease: 'cam' },
  { blocks: [MN1, MS1], at: 'l12.Islam!', dur: 1.4, to: { bulge: 0.1 }, ease: 'out' },
  { block: MN1, at: 'l12.rallied.', dur: 1.0, to: { z: -30 }, ease: 'out' }, { block: MS1, at: 'l12.rallied.', dur: 1.0, to: { z: 30 }, ease: 'out' },
  // the second charge: Kitbuqa is killed, the Mongol army breaks and drains away west
  { block: MN1, at: 'l13.charged', dur: 2.8, to: { x: 0, z: -22, heading: 270, bulge: 0 }, ease: 'cam' },
  { block: MS1, at: 'l13.charged', dur: 2.8, to: { x: 0, z: 22, heading: 270, bulge: 0 }, ease: 'cam' },
  { block: MN2, at: 'l13.charged', dur: 2.8, to: { x: 30, z: -46, heading: 270 }, ease: 'cam' },
  { block: MS2, at: 'l13.charged', dur: 2.8, to: { x: 30, z: 46, heading: 270 }, ease: 'cam' },
  { block: 'bay', at: 'l13.charged', dur: 2.8, to: { x: 34, z: 0 }, ease: 'cam' },
  { block: 'qutB', at: 'l13.charged', dur: 2.8, to: { x: 40, z: -30, heading: 270 }, ease: 'cam' },
  { blocks: ['monA', 'monB', 'monK'], at: 'l13.charged', dur: 2.8, by: { x: -36 }, ease: 'cam' },
  { block: 'monK', at: 'l13.killed', dur: 1.6, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 },
  { blocks: ['monA', 'monB'], at: 'l13.broken.', dur: 2.6, stagger: 0.2, by: { x: -110 }, ease: 'in' },
  { blocks: ['monA', 'monB'], at: 'l13.broken.', dur: 2.0, stagger: 0.2, fadeTo: 1, alphaTo: 0.5, sinkTo: 0.9 },
];

// ------------------------------------------------------------------ the edit: scenes, sets, shots (reasons in NOTES.md)
const scenes = [
  { id: 'S1', name: 'Almost never lost', at: 0, stage: 'emp', inset: 'full', job: 'the Mongols have conquered more than anyone; they ride into Palestine and meet an army that knows a trick', set: { time: [0.1, 0.05], haze: 1.1 },
    shots: [
      { at: 0, why: 'cold open low over Mongolia as the empire spreads like ink across the map', from: { target: P(100, 47), dist: 190, pitch: 18, yaw: 285, mm: 30 },
        moves: [{ until: 'l00.history.>', to: { target: P(84, 45), dist: 250, pitch: 26, yaw: 290 } }] },
      { at: 'l00.Then', why: 'follow the horsemen west into Palestine, then rise under the title', from: { target: P(44, 34.5), width: 420, pitch: 50, yaw: 350, mm: 35 },
        moves: [{ until: 'l00.two.>', to: { target: P(37.8, 33.3), width: 350 } }, { at: 13.6, until: 'l02', to: { pitch: 62, width: 380 }, ease: 'camSoft' }] },
    ] },
  { id: 'S2', name: 'The empire', at: 'l02', stage: 'emp', inset: 'full', job: 'how big the Mongol Empire is, and how close it has come', set: { time: 0.05, haze: 1.0 },
    shots: [
      { at: 'l02', why: 'the whole empire from China to Eastern Europe, top-down', from: { target: P(70, 45), width: 820, pitch: 76, yaw: 0, mm: 35 },
        moves: [{ until: 'l02.Europe.>', to: { width: 790 } }] },
      { at: 'l02.Two', why: 'lower and closer: Baghdad destroyed, Damascus taken', from: { target: P(41, 34), width: 300, pitch: 46, yaw: 340, mm: 35 },
        moves: [{ until: 'l02.Damascus.>', to: { target: P(38.5, 33.8), width: 280 } }] },
    ] },
  { id: 'S3', name: 'Surrender or else', at: 'l03', stage: 'emp', inset: 'full', job: 'Hulagu threatens Egypt; the Mamluks answer, rudely', set: { time: 0.06, haze: 1.0 },
    shots: [
      { at: 'l03', why: 'from above Damascus: Hulagu\'s message rides to Egypt', from: { target: P(34.2, 32.2), width: 210, pitch: 56, yaw: 24, mm: 35 },
        moves: [{ until: 'l03.else.>', to: { width: 196 } }] },
      { at: 'l03.The', why: 'reverse, low from the Egyptian side: the Mamluks send their answer back, then hold on it', from: { target: P(33.4, 31.6), width: 170, pitch: 30, yaw: 62, mm: 35 },
        moves: [{ until: 'l03.answer.>', to: { width: 160 } }] },
    ] },
  { id: 'S4', name: 'Luck changes', at: 'l04', stage: 'emp', inset: 'full', job: 'the Great Khan dies, most of the Mongols ride home, and Egypt marches out', set: { time: [0.06, 0.12], haze: 1.0 },
    shots: [
      { at: 'l04', why: 'wide to Mongolia: the Great Khan dies, Hulagu rides most of his army back east', from: { target: P(70, 42), width: 820, pitch: 62, yaw: 0, mm: 35 },
        moves: [{ until: 'l04.east.>', to: { target: P(72, 42), width: 800 } }] },
      { at: 'l04.He', why: 'back to Syria, closer: the smaller army left under Kitbuqa', from: { target: P(36.2, 33.4), width: 150, pitch: 44, yaw: 350, mm: 35 },
        moves: [{ until: 'l04.Bukka.>', to: { width: 140 } }] },
      { at: 'l05', why: 'Egypt: Sultan Qutuz marches out with Baybars', from: { target: P(33, 31), width: 200, pitch: 40, yaw: 40, mm: 35 },
        moves: [{ until: 'l06', to: { target: P(34.2, 31.8) } }] },
    ] },
  { id: 'S5', name: 'The valley', at: 'l06', transition: { type: 'dissolve', dur: 1.0 }, job: 'where they meet: a spring, a valley, hills on both sides', set: { time: 0.04, haze: 1.15, cloud: 0.3 },
    shots: [
      { at: 'l06', why: 'change of world: low along the valley from the east to the Mongols at the spring', from: { target: [-60, 0], dist: 220, pitch: 14, yaw: 270, mm: 30 },
        moves: [{ until: 'l06.Spring,>', to: { target: [-86, 4], dist: 196 } }] },
      { at: 'l06.in', why: 'high over the valley: the hills of Galilee on both sides', from: { target: [0, 0], width: 520, pitch: 62, yaw: 0, mm: 35 },
        moves: [{ until: 'l06.Galilee.>', to: { width: 500 } }] },
      { at: 'l07', why: 'low on the Mongol horsemen: their own favourite trick is about to be used on them', from: { target: [-140, 0], dist: 100, pitch: 12, yaw: 70, mm: 40 },
        moves: [{ until: 'l07.them.>', to: { dist: 92 } }] },
    ] },
  { id: 'S6', name: 'The feigned retreat', at: 'l08', job: 'Baybars fights, pretends to run, and the Mongols chase him up the valley', set: { time: [0.04, 0.1], haze: 1.12 },
    shots: [
      { at: 'l08', why: 'behind Baybars\'s small force as it rides out at the Mongols, closing in as they fight', from: { target: [-60, 0], dist: 130, pitch: 14, yaw: 270, mm: 35 },
        moves: [{ until: 'l08.while,>', to: { target: [-88, 0], dist: 112 } }] },
      { at: 'l08.pretended', why: 'high angle: he turns and runs, up the valley', from: { target: [-30, 0], width: 380, pitch: 64, yaw: 350, mm: 35 },
        moves: [{ until: 'l08.valley.>', to: { target: [0, 0] } }] },
      { at: 'l09', why: 'low behind the Mongol horsemen as they charge after him', from: { target: [-10, 0], dist: 170, pitch: 12, yaw: 90, mm: 35 },
        moves: [{ until: 'l09.him.>', to: { target: [24, 0], dist: 160 } }] },
    ] },
  { id: 'S7', name: 'Ambush', at: 'l10', climax: true, job: 'the hidden army strikes from both sides; the line bends, Qutuz rallies it, the Mongols break', set: { time: [0.1, 0.3], haze: 1.15 },
    shots: [
      { at: 'l10', why: 'tilt up to the hills: the main Mamluk army, hidden, waiting', from: { target: [80, -60], dist: 170, pitch: 16, yaw: 0, mm: 35 },
        moves: [{ until: 'l10.waiting.>', to: { pitch: 21, target: [80, -70] } }] },
      { at: 'l11', why: 'the decisive moment, wide from above: hit from both sides at once', from: { target: [60, 0], width: 340, pitch: 86, yaw: 0, mm: 35 },
        moves: [{ until: 'l11.sides.>', to: { width: 320 } }] },
      { at: 'l12', why: 'closer and lower, the same fight: the Mongols push back and the Mamluk line bends', from: { target: [52, -24], dist: 120, pitch: 18, yaw: 300, mm: 35 },
        moves: [{ until: 'l12.bend.>', to: { dist: 108 } }] },
      { at: 'l12.Khutuz', why: 'low on Qutuz as he rides into the bending line: the men rally', from: { target: [56, -50], dist: 72, pitch: 12, yaw: 20, mm: 45 },
        moves: [{ until: 'l12.rallied.>', to: { dist: 64 } }] },
      { at: 'l13', why: 'high and wide: the second charge, Kitbuqa falls, the Mongol army breaks', from: { target: [-10, 0], width: 420, pitch: 58, yaw: 10, mm: 35 },
        moves: [{ until: 'l14', to: { target: [-40, 0], width: 470 }, ease: 'camLong' }] },
    ] },
  { id: 'S8', name: 'Never conquered', at: 'l14', stage: 'emp', inset: 'full', transition: { type: 'dissolve', dur: 1.0 }, job: 'the result: beaten, the Mongols never come back and never take Egypt; Baybars takes the throne', set: { time: [0.1, 0.4], haze: 1.05 },
    shots: [
      { at: 'l14', why: 'change of world: the map again, from the empire down to the Nile', from: { target: P(55, 40), width: 620, pitch: 58, yaw: 0, mm: 35 },
        moves: [{ until: 'l14.Egypt.>', to: { target: P(37, 32.5), width: 270 }, ease: 'camLong' }] },
      { at: 'l15', why: 'closer and lower on the road home: Baybars gets rid of Qutuz and makes himself Sultan', from: { target: P(33, 31.2), width: 130, pitch: 36, yaw: 30, mm: 35 },
        moves: [{ until: 'l15.Teamwork.>', to: { width: 122 } }] },
    ] },
  { id: 'S9', name: 'Two and a half centuries', at: 'l16', stage: 'emp', inset: 'full', job: 'why it mattered: the Mamluks rule Egypt for more than 250 years', set: { time: 0.4, haze: 1.05 },
    shots: [
      { at: 'l16', why: 'high over Egypt as the Mamluk realm spreads', from: { target: P(32, 29), width: 340, pitch: 64, yaw: 0, mm: 35 },
        moves: [{ until: 135.4, to: { width: 360 } }] },
    ] },
];

// ------------------------------------------------------------------ the legend (motion-graphics frame)
const legend = {
  title: { text: 'BATTLE OF AIN JALUT', sub: '3 September 1260', at: 'l02.Mongol' },
  show: [['l02.Mongol', 'l16.years.>']],
  sides: [
    { id: 'mongols', team: 'carthage', name: 'MONGOL EMPIRE', commander: 'Kitbuqa', commanderAt: 'l04.Kit', banner: 'banner', at: 'l02.Mongol', dimAt: 'l13.broken.' },
    { id: 'mamluks', team: 'rome', name: 'MAMLUKS OF EGYPT', commander: 'Qutuz and Baybars', commanderAt: 'l05.Qutuz', banner: 'vexillum', at: 'l03.Mamluks,' },
  ],
  key: { show: [['l06.Ainjalut,', 'l08.pretended'], ['l10.main', 'l13.broken.>']] },
  units: [
    { id: 'ha', kind: 'cavalry', glyph: 'u-horse-archers', name: 'Horse archers', team: 'carthage', at: 'l06.Mongols' },
    { id: 'cav', kind: 'cavalry', name: 'Cavalry', team: 'rome', at: 'l06.met+0.4' },
    { id: 'inf', kind: 'infantry', name: 'Infantry', team: 'rome', at: 'l10.army' },
  ],
  places: [
    { id: 'spring', letter: 'A', glyph: 'river', name: 'Ain Jalut, Goliath\'s Spring', at: 'l06.Ainjalut,', pos: SPRING, label: 'AIN JALUT', ldy: 0.05 },
    { id: 'valley', letter: 'B', glyph: 'plain', name: 'The valley', at: 'l06.valley', pos: [20, 26], label: false, markerSize: 0.05 },
    { id: 'hills', letter: 'C', glyph: 'hill', name: 'Hills of Galilee', at: 'l06.hills', pos: [-10, -80], y: 6, label: false },
  ],
  focus: [
    { entry: 'ha', at: 'l07.favorite', until: 'l07.them.>' }, { entry: 'hills', at: 'l10.Hidden', until: 'l10.waiting.>' },
    { entry: 'mamluks', at: 'l14.beaten.', until: 'l14.In' }, { entry: 'mamluks', at: 'l16.rule', until: 'l16.years.>' },
  ],
  scale: { unitM: 20, show: [['l06', 'l13.broken.>']] },
};

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { fogDensity: 0.0007, edgeStart: 900, edgeEnd: 1500, grade: { saturation: 0.98, contrast: 1.06, grain: 0.03, vignette: 0.3 } },
  world, stages: { emp }, blocks, moves, scenes, legend,
  msaaOn: [['l07', 'l07.them.>'], ['l12.Khutuz', 'l13']],
  ambient: {
    wind: [1.0, 0.25], gusts: 0.55, flow: { dir: [1, 0.05], speed: 0.8, glint: 1.1 },
    camps: [{ pos: [-250, 0], size: [56, 44], team: 'carthage', style: 'scatter', tents: 22, fires: 3, people: 12 }, { pos: [250, 0], size: [50, 40], team: 'rome', style: 'grid', fires: 3, people: 10 }],
    walkers: [{ path: [[-320, -8], [-100, -2], [100, 4], [320, 0]], n: 4, gap: 6, speed: 1.3, kind: 'light', team: 'neutral', until: 'l08' }],
    smoke: [{ pos: [50, 0], n: 12, alpha: 0.2, height: 10, at: 'l11.ambush.' }, { pos: [-20, 0], n: 12, alpha: 0.2, height: 10, at: 'l13.charged' }],
    birds: [{ center: [-60, -110], r: 50, h: 34, n: 6, speed: 6 }, { path: [[-300, 120], [300, -120]], n: 5, h: 40, speed: 9 }, { center: [100, 90], r: 34, h: 30, n: 5, speed: 5, dir: -1 }],
  },
  arrows: [
    { at: 'l08.run', until: 'l08.valley.>', ease: 'cam', team: 'rome', style: 'dash', width: 5, path: [[-84, 0], [-30, 4], [30, 0], [96, 2]], lift: 6, hide: 'l09.charge' },
    { at: 'l09.charge', until: 'l09.him.>', ease: 'cam', team: 'carthage', width: 6, path: [[-112, -30], [-50, -24], [10, -24], [44, -24]], lift: 6, hide: 'l11.ambush.' },
    { at: 'l09.charge', until: 'l09.him.>', ease: 'cam', team: 'carthage', width: 6, path: [[-112, 30], [-50, 24], [10, 24], [44, 24]], lift: 6, hide: 'l11.ambush.' },
    { at: 'l11.ambush.', dur: 1.2, ease: 'out', team: 'rome', width: 5, path: [[56, -72], [52, -32]], lift: 8, hide: 'l12' },
    { at: 'l11.ambush.', dur: 1.2, ease: 'out', team: 'rome', width: 5, path: [[56, 74], [52, 34]], lift: 8, hide: 'l12' },
    { at: 'l11.ambush.+0.4', dur: 1.2, ease: 'out', team: 'rome', width: 5, path: [[108, -76], [100, -42]], lift: 8, hide: 'l12' },
    { at: 'l11.ambush.+0.4', dur: 1.2, ease: 'out', team: 'rome', width: 5, path: [[108, 78], [100, 42]], lift: 8, hide: 'l12' },
    { at: 'l13.charged', until: 'l13.again,>', ease: 'cam', team: 'rome', width: 7, path: [[54, -26], [20, -20], [-30, -14]], lift: 8, hide: 'l13.killed' },
    { at: 'l13.charged', until: 'l13.again,>', ease: 'cam', team: 'rome', width: 7, path: [[54, 26], [20, 20], [-30, 14]], lift: 8, hide: 'l13.killed' },
  ],
  labels: [
    { at: 'l06.3rd', until: 'l06.they', text: '3 SEPTEMBER 1260', screen: [0.5, 0.86], big: true },
    { at: 'l06.met', until: 'l06.spring', text: 'KITBUQA', block: 'monK', team: 'carthage', dx: 0.04, dy: -0.12 },
    { at: 'l08.Babers', until: 'l08.fought', text: 'BAYBARS', block: 'bay', team: 'rome', dx: 0.04, dy: -0.12 },
    { at: 'l12.Khutuz', until: 'l12.rallied.>', text: 'QUTUZ', block: 'qutB', team: 'rome', dx: 0.1, dy: 0.08 },
    { at: 'l13.Kitbuka', until: 'l13.Mongol', text: 'KITBUQA', block: 'monK', team: 'carthage', dx: -0.05, dy: -0.12 },
  ],
  cards: [
    { at: 0, until: 0.9, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 0.9, lines: [] },
    { at: 13.4, until: 17.4, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
      { text: 'THE BATTLE OF AIN JALUT', size: 0.078, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
      { text: '1260', size: 0.056, y: 0.575, delay: 1.0, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.56 }, { y: 0.65, w: 0.56 }] },
    { at: 135.428, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.8, lines: [
      { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
      { text: 'The Battle of Ain Jalut, 1260', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
  ],
};
