// The Battle of Salamis (480 BC): Battle Map v2 spec (engine: films/lib/battlemap/SPEC.md; scene list and reasons: NOTES.md).
// Colours: Persian deep red (team 'rome'), Greek royal blue (team 'carthage').
// Two maps: the main stage is the Saronic Gulf region (Athens, Salamis, Aegaleos, Hellespont); the 'strait' stage is the narrow channel,
// shown full-screen in S1 and S4–S7. Map units: x east, z south; on the strait 1 unit ≈ 15 m.
// Times come from the cue words; the line starts never change (the sound is re-scored around them).
const PER = { team: 'rome' }, GRE = { team: 'carthage' };

// ------------------------------------------------------------------ Saronic Gulf region (Athens, Salamis, Aegaleos, Hellespont)
const region = {
  seed: 480, size: [760, 500], res: 1, base: 0, meshStep: 2.5,
  sun: { azimuth: 245, elevation: 35 }, sunEve: { azimuth: 280, elevation: 8 },
  style: { contour: 3, pxPerUnit: 5.4, palette: [[-2, [0.55, 0.68, 0.78]], [2, [0.68, 0.72, 0.58]], [12, [0.78, 0.70, 0.52]], [28, [0.70, 0.58, 0.44]], [50, [0.68, 0.64, 0.60]], [70, [0.96, 0.96, 0.97]]], paletteSoft: 6 },
  features: [
    { type: 'undulate', amp: 5, scale: 110 }, { type: 'undulate', amp: 1.5, scale: 35 },
    // Sea
    { type: 'sea', poly: [[-420, -300], [420, -300], [420, 300], [-420, 300]], shelf: 28, depth: 6 },
    // Attica mainland (west)
    { type: 'land', wob: 2.0, shelf: 14, poly: [[-420, -300], [-420, 300], [-60, 300], [-40, 220], [-20, 160], [0, 100], [20, 40], [40, -20], [20, -80], [0, -140], [-20, -200], [-40, -260], [-80, -300]] },
    // Salamis island (east of mainland, separated by the strait)
    { type: 'land', wob: 1.2, shelf: 8, poly: [[60, -280], [140, -260], [180, -200], [200, -120], [180, -40], [140, 40], [80, 100], [20, 140], [-20, 160], [-40, 120], [-20, 60], [20, 0], [40, -60], [20, -120], [0, -180], [20, -240]] },
    // Aegina island (south)
    { type: 'land', wob: 1.5, shelf: 10, poly: [[180, 180], [260, 160], [300, 200], [280, 260], [220, 280], [160, 240]] },
    // Mount Aegaleos (on mainland, overlooking strait)
    { type: 'hill', at: [-80, 20], r: [30, 22], h: 18, rot: 10 },
    // Athens plain
    { type: 'flat', at: [-20, -100], r: 40, amount: 0.9 },
    { type: 'woods', at: [-120, -180], r: [50, 20], rot: 5 }, { type: 'woods', at: [-200, 100], r: [60, 24] },
    { type: 'farms', rect: [-60, -140, 80, 40, 0], cell: [14, 10] },
    { type: 'road', path: [[-420, -200], [-300, -150], [-180, -100], [-80, -60], [-40, -20]], w: 2.2, meander: 4 },
  ],
};

// ------------------------------------------------------------------ the strait: narrow channel between Salamis (east) and mainland (west)
const W_PERS = [...Array(14)].map((_, i) => `p${i}`);   // 14 Persian blocks (700 ships / 50 per block)
const W_GREK = [...Array(6)].map((_, i) => `g${i}`);     // 6 Greek blocks (300 ships / 50 per block)
const strait = {
  look: { cloud: 0.08 },
  world: {
    seed: 4800, size: [760, 500], res: 1, base: 0, meshStep: 2.0,
    sun: { azimuth: 235, elevation: 32 }, sunEve: { azimuth: 265, elevation: 6 },
    style: { contour: 1.2, pxPerUnit: 5.4 },
    features: [
      { type: 'undulate', amp: 1.5, scale: 80 },
      // Mainland shore (west)
      { type: 'land', wob: 0.6, shelf: 6, poly: [[-400, -300], [-120, -300], [-120, -200], [-140, -140], [-150, -60], [-155, 20], [-150, 100], [-140, 180], [-120, 240], [-120, 300], [-400, 300]] },
      // Salamis shore (east)
      { type: 'land', wob: 0.6, shelf: 6, poly: [[120, -300], [400, -300], [400, 300], [120, 300], [120, 240], [140, 180], [150, 100], [155, 20], [150, -60], [140, -140], [120, -200]] },
      // Narrowest point ~1 km (≈66 units) near the centre
      { type: 'flat', at: [0, -40], r: [80, 120], amount: 0.7 }, // water flattening
      { type: 'woods', at: [-200, -200], r: [30, 14] }, { type: 'woods', at: [200, -200], r: [30, 14] },
      { type: 'woods', at: [-200, 180], r: [30, 14] }, { type: 'woods', at: [200, 180], r: [30, 14] },
    ],
  },
  ambient: {
    wind: [1.3, 0.45], gusts: 0.7,
    flow: { dir: [0.2, 1], speed: 0.8, glint: 1.3 },
    camps: [],
    walkers: [],
    smoke: [
      { pos: [0, -20], n: 18, alpha: 0.22, height: 14, at: 'l05.ramming', until: 'l09' },
      { pos: [-20, 60], n: 14, alpha: 0.18, height: 10, at: 'l07.jamming', until: 'l09' },
    ],
    birds: [
      { center: [-180, -180], r: 40, h: 18, n: 6, speed: 5 },
      { center: [180, 180], r: 40, h: 18, n: 5, speed: 5, dir: -1 },
      { path: [[-300, 0], [300, 0]], n: 7, h: 28, speed: 10 },
    ],
  },
  blocks: {
    // Persian fleet: 14 blocks in tight columns filling the strait (north to south)
    ...Object.fromEntries(W_PERS.map((id, i) => [id, {
      ...PER, kind: 'infantry', figures: false, banner: i % 3 === 0,
      x: -30 + (i % 7) * 12, z: -220 + Math.floor(i / 7) * 180,
      heading: 180, len: 22, dep: 10, grid: { cols: 1, ranks: 1, gap: 0 },
      count: 50, hidden: true, bannerScale: 1.2, trayAlpha: 0.85, tray: [0.55, 0.15, 0.1],
    }])),
    // Greek fleet: 6 blocks in the wider bay behind Salamis (south-east)
    ...Object.fromEntries(W_GREK.map((id, i) => [id, {
      ...GRE, kind: 'infantry', figures: false, banner: i % 2 === 0,
      x: 160 + (i % 3) * 14, z: 80 + Math.floor(i / 3) * 30,
      heading: 270, len: 20, dep: 12, grid: { cols: 1, ranks: 1, gap: 0 },
      count: 50, hidden: true, bannerScale: 1.2, trayAlpha: 0.85, tray: [0.15, 0.25, 0.55],
    }])),
    // Commanders
    xerxes: { ...PER, kind: 'marker', x: -155, z: 20, heading: 90, len: 6, dep: 4, hidden: true, bannerScale: 2.0, banner: false, trayAlpha: 0 },
    themis: { ...GRE, kind: 'marker', x: 165, z: 85, heading: 270, len: 6, dep: 4, hidden: true, bannerScale: 2.0, banner: false, trayAlpha: 0 },
    euryb:  { ...GRE, kind: 'marker', x: 175, z: 85, heading: 270, len: 6, dep: 4, hidden: true, bannerScale: 1.6, banner: false, trayAlpha: 0 },
  },
  moves: [],
  arrows: [], labels: [], icons: [], volleys: [], counters: [], markers: [],
};
const mv = (o) => strait.moves.push(o);

// S1: Cold open – Persian fleet appears in strait, Greek fleet in bay
W_PERS.forEach((id, i) => mv({ block: id, at: 'l00.Persian', dur: 0.6, stagger: 0.08 * i, appear: true }));
W_GREK.forEach((id, i) => mv({ block: id, at: 'l00.Greek', dur: 0.6, stagger: 0.1 * i, appear: true }));
mv({ block: 'xerxes', at: 'l00.Persian', dur: 0.8, appear: true });

// S2: Xerxes on throne (already there)

// S3: Themistocles and Eurybiades appear in Greek bay
mv({ blocks: ['themis', 'euryb'], at: 'l03.Themistocles,', dur: 0.7, stagger: 0.2, appear: true });

// S4: Night – messenger darts (icon), Persian fleet advances into strait
mv({ blocks: W_PERS, at: 'l04.Xerxes', dur: 4.0, by: { z: 140 }, ease: 'cam' });

// S5: Dawn – Greek charge from bay into strait flank
mv({ blocks: W_GREK, at: 'l05.first', dur: 3.5, path: [
  [160, 80], [140, 60], [110, 40], [80, 20], [40, 0], [0, -20], [-30, -40]
], ease: 'inOut' });
// Persian flank blocks (p0..p6 west side) get pushed / tangled
[0,1,2,3,4,5,6].forEach(i => mv({ block: `p${i}`, at: 'l05.ramming', dur: 1.8, by: { x: 18, z: 12 }, ease: 'out' }));

// S6: ~200 Persian ships lost (4 blocks fade)
['p0','p1','p7','p8'].forEach((id, i) => mv({ block: id, at: 'l06.smashed', dur: 1.2, stagger: 0.3 * i, fadeTo: 1, alphaTo: 0.2, sinkTo: 0.85 }));

// S7: Centre jam – rear Persian ranks press forward, channel narrows visually
mv({ blocks: W_PERS.filter((_,i)=>i>=2 && i<=5).concat(W_PERS.filter((_,i)=>i>=9 && i<=12)), at: 'l07.pressed', dur: 2.5, by: { z: -30 }, ease: 'inQuad' });
mv({ blocks: ['p6','p13'], at: 'l07.jamming', dur: 2.0, by: { z: -20 }, ease: 'inQuad' });

// S8: Xerxes leaps, fleet dissolves
mv({ block: 'xerxes', at: 'l08.leapt', dur: 0.5, to: { y: 8 }, ease: 'out' });
mv({ block: 'xerxes', at: 'l08.tearing', dur: 0.8, to: { y: 0 }, ease: 'outBack' });
W_PERS.forEach((id, i) => mv({ block: id, at: 'l08.dissolve', dur: 2.0, stagger: 0.1 * i, fadeTo: 1, alphaTo: 0.15, sinkTo: 0.9 }));

// S9: Counters handled in counters array

// S10: Persian remnants retreat north to Hellespont; Xerxes walks inland with army block
mv({ blocks: W_PERS.filter((_,i)=>i>=2 && i<=5).concat(W_PERS.filter((_,i)=>i>=9 && i<=12)), at: 'l10.fled', dur: 4.0, path: [
  [0, -20], [0, -80], [0, -140], [-20, -200], [-60, -260]
], ease: 'cam' });
mv({ block: 'xerxes', at: 'l10.leaving', dur: 3.5, path: [[-155, 20], [-160, 60], [-180, 120], [-220, 180]], ease: 'cam' });

// S11: Athens safe, Persian million-man army fades (icon only)

// S12: Temple at Athens (icon)

// S13-14: Modern overlay handled by icons/arrows on main stage

strait.arrows = [
  // S1: width label on strait (arrow with head=false, taper=1)
  { at: 'l00.channel', until: 'l01', ease: 'out', team: 'ink', width: 1.2, head: false, taper: 1, path: [[-130, -40], [130, -40]], lift: 4, hide: 'l02' },
  // S3: Trap arrow from strait narrowing point
  { id: 'trap', at: 'l03.trap,', until: 'l04', ease: 'cam', team: 'gold', width: 2.5, style: 'dash', path: [[-10, -60], [-10, -20], [30, 0], [-10, 20], [-10, 60]], lift: 5, hide: 'l05' },
  // S4: Persian advance at night
  { at: 'l04.moved', until: 'l05', ease: 'cam', team: 'rome', width: 4, style: 'dash', path: [[-30, -220], [-30, -80]], lift: 6, hide: 'l05.first' },
  // S5: Greek charge arrow
  { at: 'l05.Greek', until: 'l05.ramming', ease: 'out', team: 'carthage', width: 5, path: [[160, 80], [40, 0], [-40, -40]], lift: 6, hide: 'l06' },
  // S7: Channel width shrinks label
  { at: 'l07.narrow', until: 'l08', ease: 'out', team: 'ink', width: 1.0, head: false, taper: 1, path: [[-125, 0], [125, 0]], lift: 4, hide: 'l09' },
  // S10: Retreat to Hellespont
  { at: 'l10.Hellespont', until: 'l11', ease: 'cam', team: 'rome', width: 3.5, style: 'dash', path: [[-60, -260], [-120, -320], [-200, -380]], lift: 6, hide: 'l11' },
  // S10: Xerxes walks inland
  { at: 'l10.march', until: 'l11', ease: 'cam', team: 'rome', width: 2.5, style: 'dash', path: [[-155, 20], [-160, 60], [-180, 120], [-220, 180]], lift: 5, hide: 'l11' },
];

strait.volleys = [
  { at: 'l05.ramming', dur: 1.4, from: [40, 0, 30], to: [-30, -40, 40], n: 30, flight: 0.8, spread: 0.25, team: 'carthage' },
];

strait.labels = [
  { at: 'l00.700', until: 'l01', text: '700 PERSIAN SHIPS', block: 'p7', team: 'rome', dx: 0.15, dy: -0.12 },
  { at: 'l00.300', until: 'l01', text: '300 GREEK TRIREMES', block: 'g3', team: 'carthage', dx: -0.15, dy: -0.12 },
  { at: 'l00.channel', until: 'l01', text: '1 KM', screen: [0.5, 0.42], big: true },
  { at: 'l02.Xerxes', until: 'l03', text: 'XERXES', block: 'xerxes', team: 'rome', dx: 0.0, dy: -0.18 },
  { at: 'l03.Themistocles,', until: 'l04', text: 'THEMISTOCLES', block: 'themis', team: 'carthage', dx: 0.05, dy: -0.14 },
  { at: 'l03.Euribides', until: 'l04', text: 'EURYBIADES', block: 'euryb', team: 'carthage', dx: 0.12, dy: -0.14 },
  { at: 'l04.night,', until: 'l05', text: 'NIGHT MOVE', screen: [0.5, 0.12], big: true },
  { at: 'l04.unproven.', until: 'l05', text: 'UNCONFIRMED', screen: [0.5, 0.88], big: true },
  { at: 'l05.ramming', until: 'l06', text: 'OARS TANGLE', pos: [-20, -30], y: 4, team: 'rome', dx: -0.1, dy: -0.1 },
  { at: 'l07.jamming', until: 'l08', text: 'CENTRE JAMMED', pos: [0, 0], y: 4, team: 'rome', dx: 0.0, dy: -0.12, big: true },
  { at: 'l07.500', until: 'l08', text: '500 M', screen: [0.5, 0.42], big: true },
  { at: 'l08.leapt', until: 'l09', text: 'XERXES REACTS', block: 'xerxes', team: 'rome', dx: 0.0, dy: -0.22, big: true },
];

strait.counters = [
  { at: 'l06.200', until: 'l07', block: 'p0', team: 'rome', from: 0, to: 200, countDur: 2.0, step: 10, suffix: 'PERSIAN LOST', dx: 0.15, dy: -0.1 },
  { at: 'l09.200', until: 'l10', block: 'p0', team: 'rome', from: 200, to: 200, countDur: 0.5, step: 1, suffix: 'PERSIAN LOST', dx: 0.15, dy: -0.1 },
  { at: 'l09.40', until: 'l10', block: 'g0', team: 'carthage', from: 0, to: 40, countDur: 1.5, step: 2, suffix: 'GREEK LOST', dx: -0.15, dy: -0.1 },
  { at: 'l09.ratio', until: 'l10', text: '5 TO 1', screen: [0.5, 0.5], big: true },
];

strait.icons = [
  // S2: Xerxes throne (gold)
  { at: 'l02.throne', until: 'l10', icon: 'crown', team: 'gold', block: 'xerxes', size: 24, minPx: 0.05, maxPx: 0.08, anim: 'sway' },
  // S3: Commander icons
  { at: 'l03.Themistocles,', until: 'l05', icon: 'helmet', team: 'carthage', block: 'themis', size: 20, minPx: 0.045, maxPx: 0.07 },
  { at: 'l03.Euribides', until: 'l05', icon: 'helmet', team: 'carthage', block: 'euryb', size: 18, minPx: 0.04, maxPx: 0.065 },
  // S4: Messenger with question (annotation 'question')
  { at: 'l04.messenger', until: 'l04.lie', icon: 'question', team: 'gold', pos: [160, 80], y: 10, size: 18, minPx: 0.04, maxPx: 0.06, anim: 'walk' },
  // S5: Tangled oar icons (annotation 'swords' for crossed oars)
  { at: 'l05.tangled', until: 'l06', icon: 'swords', team: 'rome', pos: [-20, -30], y: 6, size: 16, minPx: 0.035, maxPx: 0.05 },
  { at: 'l05.tangled', until: 'l06', icon: 'swords', team: 'rome', pos: [10, -35], y: 6, size: 16, minPx: 0.035, maxPx: 0.05 },
  // S6: Debris (annotation 'clash')
  { at: 'l06.smashed', until: 'l08', icon: 'clash', team: 'rome', pos: [-30, -40], y: 4, size: 20, minPx: 0.04, maxPx: 0.06 },
  // S8: Robe tear (animation on crown icon handled by label)
  // S10: Ego -100 (humorous label, not icon)
  // S12: Temple, gold coins
  { at: 'l12.temple', until: 'l13', icon: 'temple', team: 'gold', pos: [-20, -100], y: 8, size: 22, minPx: 0.05, maxPx: 0.07 },
  { at: 'l12.money', until: 'l13', icon: 'crown', team: 'gold', pos: [-10, -100], y: 6, size: 14, minPx: 0.03, maxPx: 0.05, anim: 'float' },
  // S13: Ferry, replica triremes
  { at: 'l13.ferry', until: 'l14', icon: 'galley', team: 'neutral', pos: [0, -40], size: 18, minPx: 0.04, maxPx: 0.06, anim: 'walk' },
  { at: 'l13.replicas', until: 'l14', icon: 'galley', team: 'neutral', pos: [30, -20], size: 16, minPx: 0.035, maxPx: 0.055, anim: 'walk' },
  { at: 'l13.replicas', until: 'l14', icon: 'galley', team: 'neutral', pos: [-30, -10], size: 16, minPx: 0.035, maxPx: 0.055, anim: 'walk' },
];

strait.markers = [
  { id: 'strait', at: 'l00.channel', until: 'l09', pos: [0, -40], glyph: 'sea', letter: 'A', label: 'SALAMIS STRAIT', labelDur: 4, size: 0.06, team: 'ink' },
  { id: 'aegaleos', at: 'l02.Egeleos', until: 'l08', pos: [-155, 20], glyph: 'hill', letter: 'B', label: 'MOUNT AEGALEOS', labelDur: 4, size: 0.06, team: 'rome', y: 12 },
  { id: 'athens', at: 'l11.Athens', until: 'l14', pos: [-20, -100], glyph: 'town', letter: 'C', label: 'ATHENS', labelDur: 4, size: 0.06, team: 'carthage' },
];

// ------------------------------------------------------------------ Main stage blocks (region map)
const mvR = (o) => regionMoves.push(o);
const regionMoves = [];

// S1: Title line – region map establishes geography
// S2: Xerxes on Aegaleos
mvR({ block: 'xerxesR', at: 'l02.Xerxes', dur: 0.8, appear: true });
// S3: Themistocles/Eurybiades in bay
mvR({ blocks: ['themisR', 'eurybR'], at: 'l03.Themistocles,', dur: 0.7, stagger: 0.2, appear: true });
// S4: Messenger darts from Greek bay to Xerxes
mvR({ block: 'messenger', at: 'l04.messenger', dur: 2.5, path: [[160, 80], [80, 40], [-80, 20]], ease: 'cam' });
// S4: Persian fleet moves into strait (represented by icons on region map)
mvR({ block: 'persianFleetR', at: 'l04.Xerxes', dur: 4.0, by: { z: 80 }, ease: 'cam' });
// S10: Retreat to Hellespont
mvR({ block: 'persianFleetR', at: 'l10.fled', dur: 5.0, path: [[0, -40], [-60, -120], [-140, -200], [-240, -280]], ease: 'cam' });
mvR({ block: 'xerxesR', at: 'l10.leaving', dur: 4.0, path: [[-80, 20], [-100, 60], [-140, 120], [-200, 180]], ease: 'cam' });
mvR({ block: 'armyR', at: 'l10.army', dur: 4.0, path: [[-80, 40], [-100, 80], [-140, 140], [-200, 200]], ease: 'cam' });
// S11: Persian army fades
mvR({ block: 'armyR', at: 'l11.million', dur: 2.0, fadeTo: 1, alphaTo: 0.2, sinkTo: 0.9 });

// Region blocks
const regionBlocks = {
  xerxesR: { ...PER, kind: 'marker', x: -80, z: 20, heading: 90, len: 8, dep: 5, hidden: true, bannerScale: 2.0, banner: false, trayAlpha: 0, figScale: 1.5 },
  themisR: { ...GRE, kind: 'marker', x: 160, z: 80, heading: 270, len: 8, dep: 5, hidden: true, bannerScale: 1.8, banner: false, trayAlpha: 0, figScale: 1.5 },
  eurybR:  { ...GRE, kind: 'marker', x: 170, z: 80, heading: 270, len: 8, dep: 5, hidden: true, bannerScale: 1.5, banner: false, trayAlpha: 0, figScale: 1.5 },
  persianFleetR: { ...PER, kind: 'infantry', figures: false, banner: true, x: 20, z: -160, heading: 180, len: 60, dep: 20, count: 700, hidden: true, bannerScale: 1.3, trayAlpha: 0.8, tray: [0.55, 0.15, 0.1] },
  armyR: { ...PER, kind: 'infantry', figures: false, banner: true, x: -80, z: 40, heading: 90, len: 40, dep: 30, count: 1000, hidden: true, bannerScale: 1.2, trayAlpha: 0.7, tray: [0.5, 0.2, 0.1] },
  messenger: { ...GRE, kind: 'light', figures: false, banner: false, x: 160, z: 80, heading: 270, len: 6, dep: 4, hidden: true, trayAlpha: 0, figScale: 1.2 },
};

// Region arrows
const regionArrows = [
  { id: 'msg', at: 'l04.messenger', until: 'l04.lie', ease: 'cam', team: 'gold', width: 2, style: 'dash', path: [[160, 80], [80, 40], [-80, 20]], lift: 4, hide: 'l05' },
  { at: 'l10.Hellespont', until: 'l11', ease: 'cam', team: 'rome', width: 3, style: 'dash', path: [[-60, -120], [-140, -200], [-240, -280]], lift: 5, hide: 'l11' },
];

// Region icons
const regionIcons = [
  { at: 'l02.throne', until: 'l10', icon: 'crown', team: 'gold', block: 'xerxesR', size: 28, minPx: 0.05, maxPx: 0.08, anim: 'sway' },
  { at: 'l03.Themistocles,', until: 'l05', icon: 'helmet', team: 'carthage', block: 'themisR', size: 22, minPx: 0.045, maxPx: 0.07 },
  { at: 'l03.Euribides', until: 'l05', icon: 'helmet', team: 'carthage', block: 'eurybR', size: 20, minPx: 0.04, maxPx: 0.065 },
  { at: 'l04.messenger', until: 'l04.lie', icon: 'question', team: 'gold', block: 'messenger', size: 20, minPx: 0.04, maxPx: 0.06, anim: 'walk' },
  { at: 'l10.ego', until: 'l11', text: 'EGO -100', block: 'xerxesR', team: 'rome', dx: 0.15, dy: -0.1, leader: false }, // handled as label below
  { at: 'l12.temple', until: 'l13', icon: 'temple', team: 'gold', pos: [-20, -100], y: 10, size: 24, minPx: 0.05, maxPx: 0.07 },
  { at: 'l13.ferry', until: 'l14', icon: 'galley', team: 'neutral', pos: [40, -20], size: 20, minPx: 0.04, maxPx: 0.06, anim: 'walk' },
  { at: 'l13.replicas', until: 'l14', icon: 'galley', team: 'neutral', pos: [60, 0], size: 18, minPx: 0.035, maxPx: 0.055, anim: 'walk' },
];

// Region labels
const regionLabels = [
  { at: 'l00.Salamis', until: 'l01', text: 'SALAMIS', pos: [100, -40], y: 4, team: 'carthage', dx: -0.1, dy: -0.08 },
  { at: 'l00.Persian', until: 'l01', text: 'PERSIAN FLEET', pos: [20, -160], y: 2, team: 'rome', dx: 0.1, dy: -0.1 },
  { at: 'l02.Egeleos', until: 'l03', text: 'MOUNT AEGALEOS', pos: [-80, 20], y: 12, team: 'rome', dx: -0.12, dy: -0.1 },
  { at: 'l04.unproven.', until: 'l05', text: 'UNCONFIRMED', screen: [0.5, 0.88], big: true },
  { at: 'l10.ego', until: 'l11', text: 'EGO -100', block: 'xerxesR', team: 'rome', dx: 0.15, dy: -0.1, leader: false },
  { at: 'l11.saved', until: 'l12', text: 'ATHENS SAVED', pos: [-20, -100], y: 4, team: 'carthage', dx: 0.12, dy: -0.12, big: true },
  { at: 'l12.temple', until: 'l13', text: 'ARTEMIS TEMPLE', pos: [-20, -100], y: 12, team: 'gold', dx: 0.1, dy: 0.08 },
  { at: 'l12.not', until: 'l13', text: 'NOT CONFIRMED', screen: [0.5, 0.88], big: true },
  { at: 'l13.ferry', until: 'l14', text: 'FERRY LANE', pos: [40, -20], y: 2, dx: -0.1, dy: -0.08 },
  { at: 'l13.timing', until: 'l14', text: 'STROKE! STROKE!', screen: [0.5, 0.88], big: true },
];

// Region markers
const regionMarkers = [
  { id: 'salamis', at: 'l00.Salamis', until: 'l14', pos: [100, -40], glyph: 'town', letter: 'A', label: 'SALAMIS', labelDur: 4, size: 0.06, team: 'carthage' },
  { id: 'athens', at: 'l11.Athens', until: 'l14', pos: [-20, -100], glyph: 'town', letter: 'C', label: 'ATHENS', labelDur: 4, size: 0.06, team: 'carthage' },
  { id: 'hellespont', at: 'l10.Hellespont', until: 'l11', pos: [-280, -320], glyph: 'bridge', letter: 'D', label: 'HELLESPONT', labelDur: 3, size: 0.05, team: 'rome' },
];

// ------------------------------------------------------------------ Scenes (the edit)
const scenes = [
  { id: 'S1', name: 'The Strait', at: 0, job: 'the trap: 700 Persian ships crowd a 1 km channel, 300 Greek triremes wait in the bay', set: { time: [0.15, 0.1], haze: 1.2, cloud: 0.25 },
    shots: [
      { at: 0, why: 'cold open top-down: the strait from above, the numbers and the geography', from: { target: [0, -20], width: 600, pitch: 89, yaw: 0, mm: 35 },
        moves: [{ until: 'l00.wide.', to: { width: 520, target: [0, -10] } }] },
      { at: 'l00.Persian', why: 'push in on the red fleet jamming the channel', from: { target: [-20, -40], width: 280, pitch: 55, yaw: 350, mm: 35 },
        moves: [{ until: 'l00.Greek', to: { target: [-10, -20], width: 240, pitch: 48 } }] },
      { at: 'l00.Greek', why: 'reverse to the blue fleet in the wide bay behind Salamis', from: { target: [140, 60], width: 320, pitch: 50, yaw: 170, mm: 35 },
        moves: [{ until: 10.0, to: { target: [150, 70], width: 280 } }] },
    ] },
  { id: 'S2', name: 'Xerxes', at: 'l02', stage: 'region', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'Xerxes on his golden throne, convinced his numbers will crush the Greeks', set: { time: 0.1, haze: 1.0, cloud: 0.2 },
    shots: [
      { at: 'l02', why: 'change of world: the region map, Mount Aegaleos above the strait', from: { target: [-80, 20], width: 300, pitch: 52, yaw: 0, mm: 35 },
        moves: [{ until: 'l02.throne', to: { target: [-85, 22], width: 240 } }] },
      { at: 'l02.throne', why: 'low on the slope: the throne, the man, the fleet far below', from: { target: [-140, 20], dist: 90, pitch: 14, yaw: 80, mm: 40 },
        moves: [{ until: 'l02.noon.>', to: { dist: 78, pitch: 16 } }] },
    ] },
  { id: 'S3', name: 'The Plan', at: 'l03', stage: 'region', inset: 'full', job: 'Themistocles knows the narrows turn size into a trap; Eurybiades holds command', set: { time: 0.1, haze: 1.0, cloud: 0.2 },
    shots: [
      { at: 'l03', why: 'shift to the Greek bay: the two commanders on the flagship', from: { target: [160, 80], dist: 110, pitch: 18, yaw: 190, mm: 35 },
        moves: [{ until: 'l03.trap,', to: { target: [155, 85], dist: 96 } }] },
      { at: 'l03.trap,', why: 'draw the trap on the map: the narrowing point', from: { target: [20, -20], width: 260, pitch: 70, yaw: 10, mm: 35 },
        moves: [{ until: 'l04', to: { width: 240, target: [10, -10] } }] },
    ] },
  { id: 'S4', name: 'The Night Move', at: 'l04', stage: 'strait', inset: 'full', transition: { type: 'dissolve', dur: 0.8 }, job: 'a messenger, a lie, the Persian fleet enters the strait at night', set: { time: 0.8, haze: 1.4, cloud: 0.5 },
    shots: [
      { at: 'l04', why: 'back in the strait at night: the messenger darts from bay to throne', from: { target: [80, 40], width: 340, pitch: 48, yaw: 340, mm: 35 },
        moves: [{ until: 'l04.Xerxes', to: { target: [20, 10], width: 300 } }] },
      { at: 'l04.Xerxes', why: 'Persian columns advance into the narrows', from: { target: [-20, -160], width: 380, pitch: 55, yaw: 350, mm: 35 },
        moves: [{ until: 'l05', to: { target: [-10, -60], width: 340, pitch: 62 } }] },
    ] },
  { id: 'S5', name: 'The Charge', at: 'l05', stage: 'strait', inset: 'full', job: 'at first light the Greek line surges, ramming the Persian flank where oars tangle', set: { time: 0.2, haze: 1.1, cloud: 0.2 },
    shots: [
      { at: 'l05', why: 'low behind the Greek line: the charge into the strait', from: { target: [100, 40], dist: 140, pitch: 12, yaw: 280, mm: 35 },
        moves: [{ until: 'l05.ramming', to: { target: [40, 0], dist: 110 } }] },
      { at: 'l05.ramming', why: 'close on the impact: oars tangle, ships cannot turn', from: { target: [-10, -30], dist: 70, pitch: 10, yaw: 350, mm: 45 },
        moves: [{ until: 'l05.turn.', to: { dist: 60 } }] },
    ] },
  { id: 'S6', name: 'The Jam', at: 'l06', stage: 'strait', inset: 'full', job: '200 Persian ships lost; the centre jams against a wall of Greek bronze', set: { time: [0.25, 0.4], haze: 1.2 },
    shots: [
      { at: 'l06', why: 'high and wide: debris fields where 200 ships were smashed', from: { target: [0, -20], width: 400, pitch: 82, yaw: 0, mm: 35 },
        moves: [{ until: 'l06.not', to: { width: 360 } }] },
      { at: 'l07', why: 'the disorder: rear ranks press forward, jamming the centre', from: { target: [-10, 20], width: 320, pitch: 68, yaw: 355, mm: 35 },
        moves: [{ until: 'l07.bronze.', to: { target: [0, 30], width: 290 } }] },
    ] },
  { id: 'S7', name: 'The Reaction', at: 'l08', stage: 'strait', inset: 'full', climax: true, job: 'Xerxes leaps tearing his robes as his fleet dissolves into splinters', set: { time: [0.55, 0.8], haze: 1.3 },
    shots: [
      { at: 'l08', why: 'close on the throne: the leap, the torn robe', from: { target: [-155, 20], dist: 48, pitch: 16, yaw: 90, mm: 50 },
        moves: [{ until: 'l08.robes', to: { dist: 42 } }] },
      { at: 'l08.robes', why: 'wide behind him: the fleet dissolving into a debris field', from: { target: [-20, 0], width: 440, pitch: 78, yaw: 280, mm: 35 },
        moves: [{ until: 'l09', to: { width: 480, pitch: 84 }, ease: 'camLong' }] },
    ] },
  { id: 'S8', name: 'The Cost', at: 'l09', stage: 'strait', inset: 'full', job: 'the final tally: 200 Persian, 40 Greek, a 5 to 1 ratio that still stuns admirals', set: { time: 0.8, haze: 1.1 },
    shots: [
      { at: 'l09', why: 'top-down the strait: the debris, the intact Greek line, the counters', from: { target: [0, 0], width: 420, pitch: 88, yaw: 0, mm: 35 },
        moves: [{ until: 'l10', to: { width: 460 }, ease: 'camLong' }] },
    ] },
  { id: 'S9', name: 'The Aftermath', at: 'l10', stage: 'region', inset: 'full', transition: { type: 'dissolve', dur: 1.0 }, job: 'the Persian fleet flees to the Hellespont; Xerxes marches home with a bruised ego', set: { time: [0.2, 0.35], haze: 1.05 },
    shots: [
      { at: 'l10', why: 'region map: the retreat north along the coast', from: { target: [-60, -120], width: 480, pitch: 60, yaw: 0, mm: 35 },
        moves: [{ until: 'l10.Hellespont', to: { target: [-100, -160], width: 420 } }] },
      { at: 'l10.leaving', why: 'Xerxes and his army turn inland', from: { target: [-140, 60], dist: 180, pitch: 22, yaw: 80, mm: 35 },
        moves: [{ until: 'l10.ego.', to: { target: [-180, 120], dist: 160 } }] },
      { at: 'l11', why: 'Athens safe, the Greek cities free', from: { target: [-20, -100], width: 320, pitch: 58, yaw: 0, mm: 35 },
        moves: [{ until: 'l11.men.', to: { width: 280 } }] },
    ] },
  { id: 'S10', name: 'The Offering', at: 'l12', stage: 'region', inset: 'full', job: 'Themistocles dedicates spoils; a temple to Artemis, not confirmed', set: { time: 0.3, haze: 1.0, cloud: 0.15 },
    shots: [
      { at: 'l12', why: 'Athens: the temple, gold flowing from debris', from: { target: [-20, -100], width: 240, pitch: 48, yaw: 20, mm: 35 },
        moves: [{ until: 'l12.documented.', to: { width: 210 } }] },
    ] },
  { id: 'S11', name: 'The Lesson', at: 'l13', stage: 'region', inset: 'full', job: 'today a ferry lane, replica triremes, tourists arguing about oar timing', set: { time: 0.15, haze: 0.9, cloud: 0.1 },
    shots: [
      { at: 'l13', why: 'modern overlay: ferries cross the ancient trap', from: { target: [0, -20], width: 400, pitch: 70, yaw: 0, mm: 35 },
        moves: [{ until: 'l13.timing.', to: { width: 360 } }] },
      { at: 'l14', why: 'child squeezes a tight door; inset the strait: big fleet stuck, small fleet wins', from: { target: [0, -20], width: 420, pitch: 84, yaw: 0, mm: 35 },
        moves: [{ until: 119.16, to: { width: 500 }, ease: 'camLong' }] },
    ] },
];

// ------------------------------------------------------------------ Legend (motion-graphics frame)
const legend = {
  title: { text: 'THE BATTLE OF SALAMIS', sub: 'September 480 BC', at: 'l01' },
  show: [['l01', 'l14.won.>']],
  corner: 'tl',
  sides: [
    { id: 'persia', team: 'rome', name: 'PERSIA', commander: 'Xerxes', commanderAt: 'l02.Xerxes', banner: 'banner', at: 'l00.Persian', strength: 700, strengthAt: 'l00.700', strengthLabel: 'SHIPS' },
    { id: 'greece', team: 'carthage', name: 'GREECE', commander: 'Themistocles / Eurybiades', commanderAt: 'l03.Themistocles,', banner: 'banner', at: 'l00.Greek', strength: 300, strengthAt: 'l00.300', strengthLabel: 'TRIREMES' },
  ],
  key: { show: [['l03', 'l07'], ['l09', 'l11']] },
  units: [
    { id: 'trireme', kind: 'infantry', name: 'Trireme', teams: ['rome', 'carthage'], at: 'l00.triremes' },
  ],
  places: [
    { id: 'strait', letter: 'A', glyph: 'sea', name: 'Salamis Strait', at: 'l00.channel', pos: [0, -40], stage: 'strait', label: 'SALAMIS STRAIT', ldy: -0.05, markerSize: 0.06 },
    { id: 'aegaleos', letter: 'B', glyph: 'hill', name: 'Mount Aegaleos', at: 'l02.Egeleos', pos: [-80, 20], stage: 'region', label: 'MOUNT AEGALEOS', y: 10, markerSize: 0.06 },
    { id: 'athens', letter: 'C', glyph: 'town', name: 'Athens', at: 'l11.Athens', pos: [-20, -100], stage: 'region', label: 'ATHENS', markerSize: 0.06 },
    { id: 'hellespont', letter: 'D', glyph: 'bridge', name: 'Hellespont', at: 'l10.Hellespont', pos: [-280, -320], stage: 'region', label: 'HELLESPONT', markerSize: 0.05 },
  ],
  focus: [
    { entry: 'persia', at: 'l02.Xerxes', until: 'l02.noon.' },
    { entry: 'greece', at: 'l03.Themistocles,', until: 'l03.command.' },
    { entry: 'trireme', at: 'l05.ramming', until: 'l07.bronze.' },
    { entry: 'persia', at: 'l08.leapt', until: 'l09' },
    { entry: 'greece', at: 'l11.saved', until: 'l12' },
  ],
  scale: { unitM: 15, show: [['l00', 'l09']] },
  compass: true,
  scaleUI: 1.05,
};

// ------------------------------------------------------------------ Light (evening fall on S7)
const light = [
  { at: 'l08.leapt', dur: 3.0, to: { eve: 0.6, haze: 1.4 }, ease: 'inOut' },
];

// ------------------------------------------------------------------ Look (grade)
const look = { grade: { saturation: 1.02, contrast: 1.05, grain: 0.025, vignette: 0.28 } };

// ------------------------------------------------------------------ Cards (title and end)
const cards = [
  { at: 0, until: 0.8, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
  { at: 10.03, until: 13.5, scrim: 0.82, scrimCenter: 'rgba(20,10,4,0.7)', fadeIn: 0.4, fadeOut: 0.8, lines: [
    { text: 'THE BATTLE OF SALAMIS', size: 0.084, y: 0.45, delay: 0, pop: false, weight: 600, track: 0.14 },
    { text: '480 BC', size: 0.056, y: 0.575, delay: 1.0, pop: false, weight: 600, track: 0.3, colorTop: '#f3d9a0', colorBottom: '#d9a441' } ], ornaments: [{ y: 0.36, w: 0.5 }, { y: 0.65, w: 0.5 }] },
  { at: 114.96, until: 130, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.8, lines: [
    { text: 'BATTLE MAP', size: 0.11, y: 0.43, delay: 0.1, track: 0.16, pop: false, weight: 600 },
    { text: 'The Battle of Salamis, 480 BC', size: 0.058, y: 0.58, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 600, track: 0.04, pop: false, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.44 }, { y: 0.67, w: 0.44 }] },
];

// ------------------------------------------------------------------ MSAA on close shots (S2 throne, S5 impact, S7 throne, S8 debris)
const msaaOn = [['l02.throne', 'l02.noon.>'], ['l05.ramming', 'l05.turn.>'], ['l08.leapt', 'l08.robes'], ['l08.dissolve', 'l09']];

// ------------------------------------------------------------------ Main ambient (region)
const ambient = {
  wind: [1.0, 0.35], gusts: 0.5,
  flow: { dir: [0.3, 1], speed: 0.7, glint: 1.2 },
  camps: [{ pos: [-20, -100], size: [50, 30], team: 'carthage', style: 'grid', fires: 2, people: 10, palisade: false }],
  walkers: [
    { path: [[-420, -200], [-300, -150], [-180, -100]], n: 4, gap: 6, speed: 1.4, kind: 'light', team: 'neutral' },
    { path: [[-80, -60], [-40, -20]], n: 3, gap: 5, speed: 1.0, kind: 'light', team: 'neutral', until: 'l05' },
  ],
  smoke: [{ pos: [-80, 20], n: 6, alpha: 0.12, height: 6 }],
  birds: [
    { center: [-200, -150], r: 50, h: 22, n: 6, speed: 6 },
    { center: [200, 150], r: 40, h: 20, n: 5, speed: 5, dir: -1 },
    { path: [[-300, 100], [300, -50]], n: 6, h: 30, speed: 9 },
  ],
};

// ------------------------------------------------------------------ Assemble
export default {
  marks: {},
  look,
  world: region,
  stages: { strait },
  msaaOn,
  ambient,
  blocks: regionBlocks,
  moves: regionMoves,
  arrows: regionArrows,
  labels: regionLabels,
  icons: regionIcons,
  markers: regionMarkers,
  volleys: [],
  scenes,
  legend,
  light,
  cards,
};
