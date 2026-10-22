// The Battle of Agincourt (1415): Battle Map spec. Times come from the cue words (see films/lib/battlemap/SPEC.md).
// Battlefield: x east, z south, about 1 unit = 5 m. England (red) starts in the south facing north; France (blue) in the north facing south.
// The two woods squeeze the field in the middle (Agincourt wood west, Tramecourt wood east). The Channel map is a second stage shown full screen
// for the invasion; the same battlefield is baked twice (dry, then wet and brown) so the mud really arrives with the rain.
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
  blocks: {
    hen: { ...ENG, kind: 'infantry', x: -128, z: -62, heading: 150, len: 22, dep: 10, height: 4, hidden: true, bannerScale: 1.5 },
    frBlock: { ...FRA, kind: 'infantry', x: 62, z: -36, heading: 200, len: 40, dep: 14, height: 4, hidden: true, bannerScale: 1.5 },
  },
  moves: [
    { block: 'hen', at: 'l02.Henry', dur: 0.9, appear: true, appearFrom: 30 },
    { block: 'hen', at: 'l02.invaded', dur: 2.1, path: [[-110, -30], [-84, 6], [-60, 40], [-38, 58]], ease: 'inOut' },
    { block: 'hen', at: 'l02.lot', dur: 1.5, to: { scale: 0.58 }, ease: 'inOut' },
    { block: 'hen', at: 'l02.very', dur: 1.4, to: { scale: 0.38 }, ease: 'inOut' },
    { block: 'hen', at: 'l03.march', dur: 4.6, path: [[-30, 42], [4, 14], [26, -2], [42, -12]], ease: 'inOut' },
    { block: 'frBlock', at: 'l03.French#1', dur: 0.9, appear: true, appearFrom: 30 },
  ],
  arrows: [
    { id: 'cross', at: 'l02.invaded', until: 'l02.crown.+0.7', ease: 'inOut', team: 'rome', style: 'dash', width: 2.4, path: [[-128, -58], [-110, -30], [-84, 6], [-60, 40], [-48, 66]], head: true, lift: 4, hide: 'l02.He' },
    { id: 'march', at: 'l03.march', until: 'l03.home.', ease: 'inOut', team: 'rome', style: 'dash', width: 2.4, path: [[-48, 66], [-30, 42], [4, 14], [28, -4], [50, -24], [58, -52]], head: true, lift: 4, hide: 'l03.The' },
  ],
  labels: [
    { at: 'l02.King', until: 'l02.had', text: 'KING HENRY V', pos: [-128, -62], y: 8, team: 'rome', dy: -0.2, dx: -0.04, big: true },
    { at: 'l02.England', until: 'l02.invaded', text: 'ENGLAND', pos: [-170, -105], leader: false, big: true, team: 'rome' },
    { at: 'l02.invaded', until: 'l02.to', text: 'THE CHANNEL', pos: [-90, 0], leader: false },
    { at: 'l02.France', until: 'l02.He', text: 'FRANCE', pos: [34, 110], leader: false, big: true, team: 'carthage' },
    { at: 'l02.captured', until: 'l02.And', text: 'HARFLEUR', pos: [-52, 74], y: 4, team: 'rome', dy: -0.2, dx: 0.17 },
    { at: 'l02.port', until: 'l02.And', text: 'PORT CAPTURED', pos: [-52, 74], y: 4, team: 'rome', dy: -0.32, dx: 0.17 },
    { at: 'l02.sick.', until: 'l02.Very,', text: 'THE ARMY GETS SICK', pos: [-38, 58], y: 6, team: 'rome', dy: -0.22, dx: -0.2 },
    { at: 'l02.very', until: 'l02.Let\'s', text: 'VERY, VERY SICK', pos: [-38, 58], y: 6, team: 'rome', dy: -0.22, dx: -0.2, big: true },
    { at: 'l02.bushes', until: 'l03.So', text: 'BUSHES WERE BUSY', pos: [-62, 80], y: 4, dy: -0.3, dx: 0.3, big: true },
    { at: 'l03.Calais,', until: 'l03.an', text: 'CALAIS', pos: [54, -64], y: 6, team: 'rome', dy: -0.18, dx: 0.12, big: true },
    { at: 'l03.English', until: 'l03.and', text: 'AN ENGLISH TOWN', pos: [54, -64], y: 6, team: 'rome', dy: -0.3, dx: 0.14 },
    { at: 'l03.go', until: 'l03.The', text: 'GO HOME', screen: [0.5, 0.87], big: true },
    { at: 'l03.French#1', until: 'l04.On', text: 'THE FRENCH ARMY', pos: [62, -36], y: 8, team: 'carthage', dy: -0.2, dx: 0.16, big: true },
    { at: 'l03.blocked', until: 'l04.On', text: 'ROAD BLOCKED', screen: [0.5, 0.87], big: true, team: 'carthage' },
  ],
  icons: [
    { at: 'l02.King', until: 'l02.had', icon: 'helmet', team: 'rome', pos: [-128, -62], y: 6, size: 22, anim: 'bounce' },
    { follow: 'cross', at: 'l02.invaded', until: 'l02.captured', icon: 'ship', team: 'rome', size: 28 },
    { at: 'l02.crown.', until: 'l02.He', icon: 'crown', pos: [60, 96], y: 10, size: 30, anim: 'bounce' },
    { at: 'l02.captured', until: 'l03.So', icon: 'city', team: 'rome', pos: [-52, 74], y: 6, size: 24 },
    { at: 'l02.captured', until: 'l03.So', icon: 'flag', team: 'rome', pos: [-62, 74], y: 12, size: 14 },
    { at: 'l02.sick.', until: 'l03.So', icon: 'sick', pos: [-38, 58], y: 8, size: 18, anim: 'bounce', dx: -0.06 },
    { at: 'l02.very#1', until: 'l03.So', icon: 'thermo', pos: [-38, 58], y: 8, size: 18, anim: 'bounce', dx: 0.06 },
    { at: 'l02.bushes', until: 'l03.So', icon: 'bush', pos: [-64, 80], y: 2, size: 16, anim: 'bounce' },
    { at: 'l02.bushes+0.18', until: 'l03.So', icon: 'bush', pos: [-34, 90], y: 2, size: 14, anim: 'bounce' },
    { at: 'l02.bushes+0.34', until: 'l03.So', icon: 'bush', pos: [-82, 62], y: 2, size: 15, anim: 'bounce' },
    { at: 'l02.were', until: 'l03.So', icon: 'bush', pos: [-22, 64], y: 2, size: 14, anim: 'bounce' },
    { at: 'l02.busy.', until: 'l03.So', icon: 'bush', pos: [-52, 98], y: 2, size: 15, anim: 'bounce' },
    { at: 'l03.Calais,', until: 'l04.On', icon: 'city', team: 'rome', pos: [54, -64], y: 6, size: 28 },
    { at: 'l03.Calais,', until: 'l04.On', icon: 'flag', team: 'rome', pos: [63, -64], y: 12, size: 16 },
    { at: 'l03.blocked', until: 'l04.On', icon: 'no', pos: [62, -36], y: 12, size: 24 },
  ],
  camera: [
    { at: 16.3, target: [-20, 0], width: 660, pitch: 62, yaw: 0, mm: 35 },
    { at: 'l02.Henry', target: [-90, -20], width: 340, pitch: 55, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.invaded', target: [-92, -6], width: 300, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.France', target: [-70, 20], width: 290, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.claim', target: [-12, 50], width: 470, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.captured', target: [-46, 50], width: 250, pitch: 50, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.very', target: [-48, 66], width: 190, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l02.bushes', target: [-50, 72], width: 205, pitch: 44, yaw: 6, mm: 35, ease: 'inOut' },
    { at: 'l03.So', target: [-10, 20], width: 400, pitch: 58, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.march', target: [-6, 12], width: 330, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.English', target: [26, -28], width: 270, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l03.French#1', target: [38, -30], width: 220, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.On', target: [40, -30], width: 195, pitch: 44, yaw: 8, mm: 35, ease: 'linear' },
  ],
};

// ------------------------------------------------------------------ the battle (shared by the dry and the wet stage)
const L = (at, until, text, o = {}) => ({ at, until, text, ...o });
const I = (at, until, icon, o = {}) => ({ at, until, icon, ...o });
const FR = ['fr.0.0', 'fr.1.0', 'fr.2.0', 'fr.3.0', 'fr.4.0'];     // the rear rank (France faces south, so rank 2 is the front)
const FRONT = ['fr.0.2', 'fr.1.2', 'fr.2.2', 'fr.3.2', 'fr.4.2'];

const battle = {
  blocks: {
    engW: { ...ENG, kind: 'elite', x: -56, z: 96, heading: 0, len: 46, dep: 12, hidden: true, bannerScale: 1.0 },
    engC: { ...ENG, kind: 'infantry', x: 0, z: 104, heading: 0, len: 56, dep: 14, hidden: true, bannerScale: 1.8, count: 8000 },
    engE: { ...ENG, kind: 'elite', x: 56, z: 96, heading: 0, len: 46, dep: 12, hidden: true, bannerScale: 1.0 },
    stakes: { team: 'wood', kind: 'cavalry', x: 0, z: 85, heading: 0, len: 168, dep: 7, grid: { cols: 26, ranks: 2, gap: 1.0 }, hidden: true, height: 4.4, banner: false },
    fr: { ...FRA, kind: 'infantry', x: 0, z: -140, heading: 180, len: 190, dep: 66, grid: { cols: 5, ranks: 3, gap: 3 }, hidden: true, bannerScale: 0.9 },
    frCavW: { ...FRA, kind: 'cavalry', x: -62, z: -98, heading: 180, len: 44, dep: 16, hidden: true, bannerScale: 1.0 },
    frCavE: { ...FRA, kind: 'cavalry', x: 62, z: -98, heading: 180, len: 44, dep: 16, hidden: true, bannerScale: 1.0 },
  },

  moves: [
    // hook: England's small block, then France's huge host drops in block by block
    { block: 'engC', at: 'l00.small,', dur: 0.7, appear: true, appearFrom: 16 },
    { group: 'fr', at: 'l00.biggest', dur: 0.7, stagger: 0.15, appear: true, appearFrom: 26 },
    { blocks: ['engC', 'fr'], at: 13.3, dur: 0.5, vanish: true },
    // the field: both armies take their places
    { blocks: ['engW', 'engC', 'engE'], at: 'l04.armies', dur: 0.7, stagger: 0.12, appear: true, appearFrom: 18 },
    { group: 'fr', at: 'l04.faced', dur: 0.7, stagger: 0.1, appear: true, appearFrom: 20 },
    // numbers: Henry's archers on the flanks, then France's size and its knights
    { blocks: ['engW', 'engE'], at: 'l05.archers', dur: 0.25, to: { scale: 1.22 }, ease: 'out' }, { blocks: ['engW', 'engE'], at: 'l05.archers+0.25', dur: 0.5, to: { scale: 1 }, ease: 'inOut' },
    { group: 'fr', at: 'l05.far', dur: 0.25, to: { scale: 1.07 }, ease: 'out' }, { group: 'fr', at: 'l05.far+0.25', dur: 0.5, to: { scale: 1 }, ease: 'inOut' },
    { blocks: ['frCavW', 'frCavE'], at: 'l05.knights', dur: 0.7, stagger: 0.2, appear: true, appearFrom: 20 },
    // stakes go in, then the army walks forward to bowshot
    { group: 'stakes', at: 'l07.hammered', dur: 0.4, stagger: 0.045, appear: true, appearFrom: 12 },
    { blocks: ['engW', 'engC', 'engE'], at: 'l07.moved', dur: 2.9, by: { z: -120 }, ease: 'inOut' },
    { group: 'stakes', at: 'l07.moved', dur: 2.9, by: { z: -120 }, ease: 'inOut' },
    // arrows fall on the French: a ripple of little hops
    { group: 'fr', at: 'l08.came+0.5', dur: 0.15, stagger: 0.05, to: { lift: 1.4 }, ease: 'out' },
    { group: 'fr', at: 'l08.came+0.65', dur: 0.3, stagger: 0.05, to: { lift: 0 }, ease: 'in' },
    // the cavalry charge: fast, slowed by the mud, stopped by the stakes, turned back into their own lines
    { block: 'frCavW', at: 'l09.horseback', dur: 1.9, to: { z: -72 }, ease: 'in' },
    { block: 'frCavE', at: 'l09.horseback+0.12', dur: 1.9, to: { z: -72 }, ease: 'in' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.mud', dur: 1.6, to: { z: -52 }, ease: 'out' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.mud', dur: 1.6, to: { sink: 0.75 }, ease: 'out' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.stopped', dur: 0.3, to: { z: -50 }, ease: 'out' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.turned', dur: 0.5, to: { heading: 0 }, ease: 'out' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.galloped', dur: 1.3, to: { z: -122 }, ease: 'in' },
    { blocks: ['frCavW', 'frCavE'], at: 'l09.own', dur: 0.5, vanish: true },
    { blocks: FRONT, at: 'l09.own', dur: 0.25, by: { z: -3 }, ease: 'out' }, { blocks: FRONT, at: 'l09.own+0.25', dur: 0.5, by: { z: 3 }, ease: 'inOut' },
    // France on foot: quick at first, slower in the mud, sinking to the knees
    { group: 'fr', at: 'l10.Then', dur: 2.6, by: { z: 24 }, ease: 'inOut' },
    { group: 'fr', at: 'l10.through', dur: 3.9, by: { z: 20 }, ease: 'out' },
    { group: 'fr', at: 'l10.through', dur: 1.2, to: { sink: 0.5 }, ease: 'out' },
    { group: 'fr', at: 'l10.up', dur: 1.4, to: { sink: 0.85 }, ease: 'out' },
    // the woods squeeze them, then they are packed
    { group: 'fr', at: 'l11.squeezed', dur: 2.6, squeeze: { about: [0, -96], kx: 0.72, kz: 1, lenK: 0.72, depK: 1.1 }, ease: 'inOut' },
    { group: 'fr', at: 'l11.squeezed', dur: 2.6, by: { z: 4 }, ease: 'inOut' },
    { group: 'fr', at: 'l11.packed', dur: 2.0, squeeze: { about: [0, -90], kx: 0.82, kz: 1, lenK: 0.9, depK: 1.05 }, ease: 'inOut' },
    // contact, the archers drop their bows and swing in on the flanks
    { group: 'fr', at: 'l12.reached', dur: 1.4, by: { z: 14 }, ease: 'inOut' },
    { block: 'engW', at: 'l12.joined', dur: 1.0, to: { x: -64, z: -50, heading: 28 }, ease: 'inOut' },
    { block: 'engE', at: 'l12.joined', dur: 1.0, to: { x: 64, z: -50, heading: 332 }, ease: 'inOut' },
    // the back pushes the front: chaos
    { blocks: FR, at: 'l13.pushing', dur: 1.1, by: { z: 20 }, ease: 'inOut' },
    { blocks: FR, at: 'l13.pushing', dur: 0.3, to: { lift: 1.6 }, ease: 'out' },
    { group: 'fr', at: 'l13.chaos', dur: 0.2, to: { heading: 168 }, ease: 'out' },
    { group: 'fr', at: 'l13.chaos+0.3', dur: 0.2, to: { heading: 192 }, ease: 'out' },
    { group: 'fr', at: 'l13.chaos+0.6', dur: 0.2, to: { heading: 170 }, ease: 'out' },
    { group: 'fr', at: 'l13.chaos+0.9', dur: 0.2, to: { heading: 180 }, ease: 'out' },
    // by evening: France fades by numbers, England loses far fewer
    { group: 'fr', at: 'l14.soldiers', dur: 3.2, stagger: 0.18, fadeTo: 1, alphaTo: 0.12, sinkTo: 0.95 },
    { blocks: ['engW', 'engC', 'engE'], at: 'l14.lost', dur: 1.0, to: { scale: 0.88 }, ease: 'inOut' },
  ],

  arrows: [
    { at: 'l07.moved', until: 'l07.close', ease: 'inOut', team: 'rome', width: 5, path: [[0, 84], [0, 6]], lift: 5, hide: 'l07.enough' },
    { at: 'l07.moved', until: 'l07.close', ease: 'inOut', team: 'rome', width: 5, path: [[-56, 78], [-56, -4]], lift: 5, hide: 'l07.enough' },
    { at: 'l07.moved', until: 'l07.close', ease: 'inOut', team: 'rome', width: 5, path: [[56, 78], [56, -4]], lift: 5, hide: 'l07.enough' },
    { at: 'l09.horseback', until: 'l09.mud', ease: 'in', team: 'carthage', width: 4, path: [[-62, -96], [-62, -66]], lift: 5, hide: 'l09.slowed' },
    { at: 'l09.horseback+0.12', until: 'l09.mud', ease: 'in', team: 'carthage', width: 4, path: [[62, -96], [62, -66]], lift: 5, hide: 'l09.slowed' },
    { at: 'l09.turned', dur: 0.5, ease: 'out', team: 'carthage', width: 4, style: 'dash', path: [[-62, -52], [-72, -86]], lift: 5, hide: 'l10.Then' },
    { at: 'l09.turned', dur: 0.5, ease: 'out', team: 'carthage', width: 4, style: 'dash', path: [[62, -52], [72, -86]], lift: 5, hide: 'l10.Then' },
    { at: 'l10.Then', until: 'l10.advanced', ease: 'inOut', team: 'carthage', width: 6, path: [[0, -150], [0, -118]], lift: 6, hide: 'l10.wearing' },
    { at: 'l11.squeezed', dur: 1.1, ease: 'out', team: 'green', width: 5, path: [[-142, -102], [-100, -96]], lift: 8, hide: 'l11.They' },
    { at: 'l11.squeezed', dur: 1.1, ease: 'out', team: 'green', width: 5, path: [[142, -102], [100, -96]], lift: 8, hide: 'l11.They' },
    { at: 'l12.joined', dur: 0.9, ease: 'out', team: 'rome', width: 5, path: [[-56, -26], [-62, -48]], lift: 6, hide: 'l13.The' },
    { at: 'l12.joined', dur: 0.9, ease: 'out', team: 'rome', width: 5, path: [[56, -26], [62, -48]], lift: 6, hide: 'l13.The' },
    { at: 'l13.pushing', until: 'l13.front,', ease: 'out', team: 'carthage', width: 5, path: [[0, -112], [0, -76]], lift: 7, hide: 'l14.Within' },
  ],

  volleys: [
    { at: 'l08.Thousands', dur: 0.9, from: { block: 'engW' }, to: [-30, -128, 42], n: 56, flight: 1.5, arc: 44, team: 'rome' },
    { at: 'l08.Thousands+0.1', dur: 0.9, from: { block: 'engE' }, to: [30, -128, 42], n: 56, flight: 1.5, arc: 44, team: 'rome' },
    { at: 'l08.Thousands+0.3', dur: 1.0, from: { block: 'engC' }, to: [0, -124, 50], n: 56, flight: 1.5, arc: 44, team: 'rome' },
    { at: 'l08.went', dur: 1.2, from: { block: 'engW' }, to: [-40, -132, 48], n: 70, flight: 1.5, arc: 50, team: 'rome' },
    { at: 'l08.went', dur: 1.2, from: { block: 'engE' }, to: [40, -132, 48], n: 70, flight: 1.5, arc: 50, team: 'rome' },
    { at: 'l08.and', dur: 1.2, from: { block: 'engC' }, to: [0, -128, 60], n: 70, flight: 1.5, arc: 50, team: 'rome' },
    { at: 'l08.came', dur: 1.4, from: { block: 'engW' }, to: [-20, -134, 56], n: 70, flight: 1.4, arc: 44, team: 'rome' },
    { at: 'l08.came', dur: 1.4, from: { block: 'engE' }, to: [20, -134, 56], n: 70, flight: 1.4, arc: 44, team: 'rome' },
  ],

  labels: [
    // ---- hook
    { at: 1.39, until: 3.2, text: '1415', screen: [0.5, 0.17], style: 'text', big: true, size: 1.9, track: 0.16, weight: 800 },
    L('l00.small,', 'l00.sick,', 'SMALL', { block: 'engC', team: 'rome', dy: 0.12, big: true }),
    L('l00.sick,', 'l00.soaking', 'SICK', { block: 'engC', team: 'rome', dy: 0.12, big: true }),
    L('l00.soaking', 'l00.English', 'SOAKING WET', { block: 'engC', team: 'rome', dy: 0.12, big: true }),
    L('l00.English', 'l00.about', 'ENGLAND', { block: 'engC', team: 'rome', dy: 0.12, big: true }),
    L('l00.biggest', 'l00.Spoiler,', 'ONE OF FRANCE\'S BIGGEST ARMIES', { block: 'fr', team: 'carthage', dy: 0.0, big: true }),
    L('l00.mud', 'l00>', 'MUD PICKS ENGLAND', { block: 'engC', team: 'rome', dy: -0.2, big: true }),
    // ---- the field
    L('l04.On', 'l04.faced', '25 OCTOBER 1415', { screen: [0.5, 0.11], big: true }),
    L('l04.armies', 'l04.freshly', 'ENGLAND', { block: 'engC', team: 'rome', dy: -0.14 }),
    L('l04.faced', 'l04.freshly', 'FRANCE', { block: 'fr', team: 'carthage', dy: -0.04 }),
    L('l04.freshly', 'l04.thick', 'FRESHLY PLOUGHED FIELD', { pos: [0, 30], dy: -0.1, leader: false, big: true }),
    L('l04.thick', 'l05.Henry', 'AGINCOURT WOOD', { pos: [-122, 0], y: 14, dy: -0.04, leader: false, big: true }),
    L('l04.thick', 'l05.Henry', 'TRAMECOURT WOOD', { pos: [122, 0], y: 14, dy: -0.04, leader: false, big: true }),
    // ---- numbers
    L('l05.Henry', 'l05.maybe', 'KING HENRY V', { block: 'engC', team: 'rome', dy: -0.2 }),
    L('l05.Most', 'l05.The', 'LONGBOW ARCHERS', { block: 'engW', team: 'rome', dy: -0.17, dx: -0.05 }),
    L('l05.Most', 'l05.The', 'LONGBOW ARCHERS', { block: 'engE', team: 'rome', dy: -0.17, dx: 0.05 }),
    L('l05.far', 'l05.many', 'FAR MORE', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    L('l05.knights', 'l06.It', 'KNIGHTS IN HEAVY ARMOUR', { block: 'frCavW', team: 'carthage', dy: -0.17, dx: 0.1 }),
    // ---- rain and mud
    L('l06.rained', 'l06.The', 'IT RAINED ALL NIGHT', { screen: [0.5, 0.11], big: true }),
    L('l06.deep', 'l07.The', 'DEEP, STICKY MUD', { screen: [0.5, 0.11], big: true }),
    // ---- stakes and the advance
    L('l07.sharp', 'l07.Then', 'SHARP WOODEN STAKES', { block: 'stakes', team: 'wood', dy: -0.17, big: true }),
    L('l07.Henry', 'l07.close', 'HENRY MOVES FORWARD', { block: 'engC', team: 'rome', dy: -0.2, big: true }),
    L('l07.close', 'l08.Thousands', 'CLOSE ENOUGH TO SHOOT', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    // ---- arrows
    L('l08.Thousands', 'l08.came', 'THOUSANDS OF ARROWS', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l08.came', 'l09.French', 'DOWN ON THE FRENCH', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    // ---- the cavalry
    L('l09.knights', 'l09.but', 'FRENCH KNIGHTS CHARGE', { block: 'frCavW', team: 'carthage', dy: -0.17, dx: 0.12, big: true }),
    L('l09.but', 'l09.and', 'THE MUD SLOWS THEM', { block: 'frCavE', team: 'carthage', dy: -0.17, dx: -0.1 }),
    L('l09.stakes', 'l09.Their', 'THE STAKES STOP THEM', { pos: [0, -40], y: 4, dy: -0.2, big: true }),
    L('l09.Their', 'l09.into', 'THEY TURN BACK', { block: 'frCavW', team: 'carthage', dy: -0.15, dx: 0.1 }),
    L('l09.into', 'l10.Then', 'INTO THEIR OWN LINES', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    // ---- on foot
    L('l10.Then', 'l10.wearing', 'FRENCH SOLDIERS ON FOOT', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    L('l10.wearing', 'l10.through', 'HEAVY ARMOUR', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    L('l10.through', 'l10.up', 'THROUGH THE MUD', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    L('l10.up', 'l11.The', 'UP TO THEIR KNEES', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    // ---- the funnel
    L('l11.The', 'l11.into', 'THE WOODS SQUEEZE THEM', { screen: [0.5, 0.11], big: true, team: 'green' }),
    L('l11.narrow', 'l11.They', 'A NARROW SPACE', { pos: [0, -90], y: 6, dy: -0.25, big: true }),
    L('l11.packed', 'l11.could', 'PACKED SO TIGHTLY', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    L('l11.could', 'l12.By', 'NO ROOM TO SWING A WEAPON', { screen: [0.5, 0.11], big: true }),
    // ---- the melee
    L('l12.reached', 'l12.exhausted,', 'THE ENGLISH LINE', { block: 'engC', team: 'rome', dy: -0.2 }),
    L('l12.exhausted,', 'l12.dropped', 'EXHAUSTED', { block: 'fr', team: 'carthage', dy: -0.04, big: true }),
    L('l12.dropped', 'l12.grabbed', 'ARCHERS DROP THEIR BOWS', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l12.grabbed', 'l12.joined', 'HAMMERS AND AXES', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l12.joined', 'l13.The', 'ARCHERS JOIN IN', { screen: [0.5, 0.11], big: true, team: 'rome' }),
    L('l13.lines', 'l13.chaos,', 'THE BACK PUSHES THE FRONT', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    L('l13.chaos,', 'l14.Within', 'CHAOS', { block: 'fr', team: 'carthage', dy: -0.04, big: true, size: 1.5 }),
    // ---- evening
    L('l14.Within', 'l14.Thousands', 'OVER IN A FEW HOURS', { screen: [0.5, 0.11], big: true }),
    L('l14.Thousands', 'l14.including', 'THOUSANDS OF FRENCH KILLED OR CAPTURED', { block: 'fr', team: 'carthage', dy: -0.04, big: true, size: 0.8 }),
    L('l14.including', 'l14.The', 'MANY OF FRANCE\'S GREATEST LORDS', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    L('l14.The', 'l15.Almost', 'THE ENGLISH LOST A FEW HUNDRED', { block: 'engC', team: 'rome', dy: -0.2, big: true }),
    // ---- Shakespeare and the aftermath
    L('l15.Almost', 'l15.Shakespeare', 'ALMOST 200 YEARS LATER', { screen: [0.5, 0.11], big: true }),
    L('l15.Shakespeare', 'l16.Henry', 'HENRY V\nA PLAY BY SHAKESPEARE', { screen: [0.5, 0.34], big: true, size: 1.1 }),
    { at: 'l15.We', until: 'l16.Henry', text: 'WE FEW.', screen: [0.5, 0.6], style: 'text', big: true, size: 1.5, track: 0.14, weight: 800 },
    { at: 'l15.happy', until: 'l16.Henry', text: 'WE HAPPY FEW.', screen: [0.5, 0.74], style: 'text', big: true, size: 1.5, track: 0.14, weight: 800 },
    L('l16.marry', 'l16.was', 'HENRY MARRIES\nTHE FRENCH KING\'S DAUGHTER', { screen: [0.5, 0.24], big: true, size: 0.9 }),
    L('l16.was', 'l16.And', 'HEIR TO FRANCE', { screen: [0.5, 0.11], big: true }),
    L('l16.And', 'l16.always', 'A LESSON FOR FRENCH KNIGHTS', { screen: [0.5, 0.11], big: true, team: 'carthage' }),
    L('l16.always', 143.05, 'ALWAYS CHECK THE WEATHER', { screen: [0.5, 0.11], big: true }),
  ],

  counters: [
    { at: 'l05.8', until: 'l05.The', block: 'engC', team: 'rome', from: 0, to: 8000, countDur: 1.0, step: 100, suffix: 'ENGLISH', dy: -0.19 },
  ],

  icons: [
    // ---- hook
    I('l00.sick,', 'l00.English', 'sick', { block: 'engC', size: 18, dx: -0.05, dy: -0.05, anim: 'bounce' }),
    I('l00.sick,', 'l00.English', 'thermo', { block: 'engC', size: 18, dx: 0.0, dy: -0.05, anim: 'bounce' }),
    I('l00.soaking', 'l00.about', 'rain', { block: 'engC', size: 26, dx: 0.06, dy: -0.04, anim: 'sway' }),
    I('l00.mud', 'l00>', 'mud', { block: 'engC', size: 28, dx: -0.11, dy: -0.04, anim: 'bounce' }),
    I('l00.aside.', 'l00>', 'check', { block: 'engC', size: 20, dx: 0.11, dy: -0.03, anim: 'bounce' }),
    // ---- the field
    I('l05.Henry', 'l05.maybe', 'crown', { block: 'engC', size: 16, dx: 0.0, dy: -0.04, anim: 'bounce' }),
    I('l05.Most', 'l05.The', 'bow', { block: 'engW', size: 24, dy: -0.05, anim: 'bounce' }),
    I('l05.Most', 'l05.The', 'bow', { block: 'engE', size: 24, dy: -0.05, anim: 'bounce' }),
    I('l05.knights', 'l06.It', 'helmet', { block: 'frCavW', team: 'carthage', size: 20, dy: -0.02, anim: 'sway' }),
    I('l05.knights', 'l06.It', 'helmet', { block: 'frCavE', team: 'carthage', size: 20, dy: -0.02, anim: 'sway' }),
    // ---- rain and mud
    I('l06.rained', 'l06.The', 'rain', { screen: [0.5, 0.58], size: 0.26, anim: 'sway' }),
    I('l06.deep', 'l07.The', 'mud', { screen: [0.5, 0.64], size: 0.2, anim: 'bounce' }),
    I('l06.sticky', 'l07.The', 'mud', { pos: [-40, 40], size: 38, anim: 'bounce' }),
    I('l06.mud.', 'l07.The', 'mud', { pos: [45, 6], size: 34, anim: 'bounce' }),
    I('l06.deep+0.1', 'l07.The', 'mud', { pos: [0, -60], size: 36, anim: 'bounce' }),
    // ---- stakes
    I('l07.hammered', 'l07.Then', 'hammer', { block: 'engW', size: 26, dy: -0.04, anim: 'none' }),
    I('l07.hammered+0.15', 'l07.Then', 'hammer', { block: 'engE', size: 26, dy: -0.04, anim: 'none' }),
    I('l07.close', 'l08.Thousands', 'bow', { screen: [0.5, 0.3], size: 0.15, anim: 'bounce' }),
    // ---- the arrows
    I('l08.arrows', 'l08.came', 'bow', { block: 'engW', size: 24, dy: -0.04, anim: 'bounce' }),
    I('l08.arrows', 'l08.came', 'bow', { block: 'engE', size: 24, dy: -0.04, anim: 'bounce' }),
    I('l08.French.', 'l09.French', 'burst', { block: 'fr', size: 28, dy: -0.02 }),
    // ---- the cavalry
    I('l09.stopped', 'l09.Their', 'burst', { pos: [-40, -40], y: 6, size: 24 }),
    I('l09.stopped', 'l09.Their', 'burst', { pos: [40, -40], y: 6, size: 24 }),
    I('l09.stopped', 'l09.Their', 'no', { pos: [0, -44], y: 8, size: 30 }),
    I('l09.mud', 'l09.and', 'mud', { block: 'frCavW', size: 22, dy: -0.04, anim: 'bounce' }),
    I('l09.mud', 'l09.and', 'mud', { block: 'frCavE', size: 22, dy: -0.04, anim: 'bounce' }),
    I('l09.own', 'l10.Then', 'burst', { block: 'fr', size: 28, dy: -0.01 }),
    // ---- on foot
    I('l10.wearing', 'l10.through', 'helmet', { block: 'fr', team: 'carthage', size: 20, dy: -0.12, anim: 'sway' }),
    I('l10.mud', 'l11.The', 'mud', { pos: [-60, -150], size: 24, anim: 'bounce' }),
    I('l10.mud+0.2', 'l11.The', 'mud', { pos: [-10, -156], size: 24, anim: 'bounce' }),
    I('l10.mud+0.4', 'l11.The', 'mud', { pos: [40, -150], size: 24, anim: 'bounce' }),
    I('l10.mud+0.6', 'l11.The', 'mud', { pos: [80, -144], size: 22, anim: 'bounce' }),
    I('l10.up', 'l11.The', 'mud', { block: 'fr', size: 30, dy: -0.12, anim: 'bounce' }),
    // ---- the funnel
    I('l11.packed', 'l11.could', 'heart', { block: 'fr', size: 30, dy: -0.14, anim: 'bounce' }),
    I('l11.swing', 'l12.By', 'sword', { block: 'fr', size: 30, dy: -0.12 }),
    I('l11.swing', 'l12.By', 'no', { block: 'fr', size: 34, dy: -0.12 }),
    // ---- the melee
    I('l12.exhausted,', 'l12.dropped', 'sweat', { block: 'fr', size: 28, dy: -0.12, anim: 'bounce' }),
    I('l12.dropped', 'l12.grabbed', 'fall', { block: 'engW', size: 26, dy: -0.07, anim: 'none' }),
    I('l12.dropped', 'l12.grabbed', 'fall', { block: 'engE', size: 26, dy: -0.07, anim: 'none' }),
    I('l12.hammers', 'l12.joined', 'hammer', { block: 'engW', size: 24, dy: -0.06, dx: -0.02, anim: 'none' }),
    I('l12.axes,', 'l12.joined', 'axe', { block: 'engW', size: 22, dy: -0.06, dx: 0.03 }),
    I('l12.hammers', 'l12.joined', 'hammer', { block: 'engE', size: 24, dy: -0.06, dx: 0.02, anim: 'none' }),
    I('l12.axes,', 'l12.joined', 'axe', { block: 'engE', size: 22, dy: -0.06, dx: -0.03 }),
    I('l12.joined', 'l13.The', 'swords', { pos: [-62, -62], y: 8, size: 30 }),
    I('l12.joined', 'l13.The', 'swords', { pos: [62, -62], y: 8, size: 30 }),
    I('l13.chaos,', 'l14.Within', 'burst', { pos: [-50, -80], y: 8, size: 30, anim: 'bounce' }),
    I('l13.chaos,+0.15', 'l14.Within', 'burst', { pos: [10, -92], y: 8, size: 34, anim: 'bounce' }),
    I('l13.chaos,+0.3', 'l14.Within', 'burst', { pos: [52, -76], y: 8, size: 28, anim: 'bounce' }),
    // ---- evening
    I('l14.Within', 'l14.Thousands', 'clock', { screen: [0.5, 0.64], size: 0.2, anim: 'bounce' }),
    I('l14.including', 'l14.The', 'crown', { screen: [0.38, 0.64], size: 0.12, anim: 'bounce' }),
    I('l14.including+0.15', 'l14.The', 'crown', { screen: [0.5, 0.64], size: 0.15, anim: 'bounce' }),
    I('l14.including+0.3', 'l14.The', 'crown', { screen: [0.62, 0.64], size: 0.12, anim: 'bounce' }),
    I('l14.The', 'l15.Almost', 'laurel', { block: 'engC', size: 18, dy: -0.04 }),
    // ---- Shakespeare and after
    I('l15.Shakespeare', 'l16.Henry', 'quill', { screen: [0.2, 0.55], size: 0.24, anim: 'sway' }),
    I('l15.Shakespeare', 'l16.Henry', 'crown', { screen: [0.8, 0.5], size: 0.17, anim: 'bounce' }),
    I('l16.marry', 'l16.was', 'helmet', { team: 'rome', screen: [0.38, 0.72], size: 0.2, anim: 'sway' }),
    I('l16.marry', 'l16.was', 'heart', { screen: [0.5, 0.64], size: 0.14, anim: 'bounce' }),
    I('l16.marry', 'l16.was', 'crown', { screen: [0.62, 0.72], size: 0.2, anim: 'bounce' }),
    I('l16.was', 'l16.And', 'crown', { screen: [0.5, 0.74], size: 0.3, anim: 'bounce' }),
    I('l16.And', 'l16.always', 'helmet', { team: 'carthage', screen: [0.5, 0.74], size: 0.26, anim: 'sway' }),
    I('l16.always', 143.05, 'weather', { screen: [0.5, 0.76], size: 0.34, anim: 'bounce' }),
  ],

  rain: [
    { at: 'l00.soaking', until: 'l00.Spoiler,', density: 1.0 },
    { at: 'l06.rained', until: 'l07.The', density: 1.4 },
  ],
  dim: [
    { at: 'l15.Shakespeare', until: 'l16.Henry', alpha: 0.5, curtains: true },
    { at: 'l16.Henry', until: 143.1, alpha: 0.32, fadeIn: 0.6 },
  ],

  light: [
    { at: 'l00.soaking', dur: 1.2, to: { cloud: 0.85 }, ease: 'inOut' },
    { at: 'l00.Spoiler,', dur: 1.6, to: { cloud: 0.3 }, ease: 'inOut' },
    { at: 'l06.rained', dur: 1.4, to: { cloud: 0.8, haze: 1.5 }, ease: 'inOut' },
    { at: 'l07.Then', dur: 2.0, to: { cloud: 0.55 }, ease: 'inOut' },
    { at: 'l14.over', dur: 3.4, to: { eve: 1, haze: 1.3 }, ease: 'inOut' },
  ],

  camera: [
    // hook: low on England's small block, then pull back to show the huge French host
    { at: 0, target: [0, 98], dist: 170, pitch: 17, yaw: -8, mm: 30 },
    { at: 'l00.sick,', target: [0, 100], dist: 125, pitch: 13, yaw: 6, mm: 30, ease: 'inOut' },
    { at: 'l00.army', target: [0, 96], dist: 150, pitch: 17, yaw: 0, mm: 30, ease: 'inOut' },
    { at: 'l00.face', target: [0, 96], dist: 152, pitch: 17, yaw: 0, mm: 30, ease: 'linear' },
    { at: 'l00.armies+0.5', target: [0, 5], width: 430, pitch: 38, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l00.Spoiler,', target: [0, 10], width: 420, pitch: 39, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l00.mud', target: [0, 40], width: 340, pitch: 38, yaw: 4, mm: 35, ease: 'inOut' },
    { at: 12.9, target: [0, 10], width: 620, pitch: 80, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 16.3, target: [0, 10], width: 620, pitch: 80, yaw: 0, mm: 35, ease: 'linear' },
    // the field
    { at: 'l04.On', target: [0, -5], width: 560, pitch: 58, yaw: 0, mm: 35, ease: 'linear' },
    { at: 'l04.armies', target: [0, 0], width: 540, pitch: 42, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.freshly', target: [0, 10], width: 500, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l04.woods', target: [0, -5], width: 600, pitch: 62, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l05.Henry', target: [0, 82], dist: 190, pitch: 32, yaw: -8, mm: 35, ease: 'inOut' },
    { at: 'l05.archers', target: [0, 86], dist: 175, pitch: 30, yaw: 10, mm: 35, ease: 'inOut' },
    { at: 'l05.The', target: [0, -60], dist: 330, pitch: 30, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l05.knights', target: [0, -100], dist: 250, pitch: 28, yaw: 6, mm: 35, ease: 'inOut' },
    { at: 'l06.It', target: [0, -10], width: 560, pitch: 70, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l06.deep', target: [0, 20], dist: 210, pitch: 24, yaw: 8, mm: 32, ease: 'inOut' },
    { at: 'l07.The', target: [0, 95], dist: 150, pitch: 32, yaw: 14, mm: 35, ease: 'inOut' },
    { at: 'l07.Then', target: [0, 80], width: 340, pitch: 48, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l07.shoot.', target: [0, -30], dist: 270, pitch: 30, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l08.Thousands', target: [0, -45], dist: 210, pitch: 20, yaw: 0, mm: 30, ease: 'inOut' },
    { at: 'l08.came', target: [0, -100], dist: 200, pitch: 26, yaw: 0, mm: 30, ease: 'inOut' },
    { at: 'l09.French', target: [0, -75], width: 340, pitch: 52, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l09.mud', target: [0, -70], width: 260, pitch: 46, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l09.turned', target: [0, -85], width: 300, pitch: 54, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l10.Then', target: [0, -105], width: 340, pitch: 52, yaw: 14, mm: 35, ease: 'inOut' },
    { at: 'l10.mud', target: [0, -100], dist: 170, pitch: 24, yaw: 16, mm: 32, ease: 'inOut' },
    { at: 'l11.The', target: [0, -80], width: 420, pitch: 82, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l11.packed', target: [0, -78], width: 270, pitch: 70, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 'l12.By', target: [0, -62], width: 250, pitch: 55, yaw: 12, mm: 35, ease: 'inOut' },
    { at: 'l12.dropped', target: [0, -48], width: 210, pitch: 52, yaw: -10, mm: 35, ease: 'inOut' },
    { at: 'l13.The', target: [0, -66], dist: 170, pitch: 40, yaw: 20, mm: 35, ease: 'inOut' },
    { at: 'l13.chaos,', target: [0, -72], dist: 150, pitch: 36, yaw: -15, mm: 35, ease: 'inOut' },
    { at: 'l14.Within', target: [0, -45], dist: 210, pitch: 24, yaw: 20, mm: 30, ease: 'inOut' },
    { at: 'l14.Thousands', target: [0, -65], dist: 230, pitch: 22, yaw: 34, mm: 30, ease: 'linear' },
    { at: 'l15.Almost', target: [0, -60], width: 560, pitch: 62, yaw: 30, mm: 35, ease: 'inOut' },
    { at: 'l16.Henry', target: [0, -60], width: 620, pitch: 70, yaw: 0, mm: 35, ease: 'inOut' },
    { at: 146, target: [0, -60], width: 600, pitch: 72, yaw: 0, mm: 35, ease: 'linear' },
  ],
};

// ------------------------------------------------------------------ the film
export default {
  marks: {},
  look: { grade: { saturation: 0.98, contrast: 1.07, grain: 0.03, vignette: 0.32 } },
  world: fieldWorld(false),
  ...battle,
  stages: { chan: channel, wet: { world: fieldWorld(true), ...battle } },
  msaaOn: [[0, 13]],
  insets: [
    { stage: 'chan', at: 16.3, until: 'l04.On', rect: [0, 0, 1, 1], frame: false, pop: false, in: 0.8, out: 0.01, samples: 0 },
    { stage: 'wet', at: 'l06.It', until: 160, rect: [0, 0, 1, 1], frame: false, pop: false, in: 1.8, out: 0.01, samples: 0 },
  ],
  cards: [
    { at: 0, until: 1.0, fill: 'rgb(8,4,2)', fadeIn: 0.01, fadeOut: 1.0, lines: [] },
    { at: 12.95, until: 16.3, scrim: 0.9, scrimCenter: 'rgba(20,10,4,0.85)', fadeIn: 0.3, fadeOut: 0.7, lines: [
      { text: 'THE BATTLE OF AGINCOURT', size: 0.074, y: 0.44, delay: 0.1 },
      { text: '1415', size: 0.07, y: 0.585, delay: 1.1, colorTop: '#ffd9a0', colorBottom: '#e2873a' } ], ornaments: [{ y: 0.35, w: 0.7 }, { y: 0.68, w: 0.7 }] },
    { at: 143.078, until: 170, fill: 'rgb(14,7,3)', fillAlpha: 0.84, fadeIn: 0.6, lines: [
      { text: 'BATTLE MAP', size: 0.13, y: 0.43, delay: 0.1, track: 0.14 },
      { text: 'The Battle of Agincourt, 1415', size: 0.062, y: 0.6, delay: 0.7, font: 'Cormorant Garamond', italic: true, weight: 500, track: 0.04, colorTop: '#f6ecd0', colorBottom: '#e4c98c' } ], ornaments: [{ y: 0.33, w: 0.5 }, { y: 0.69, w: 0.5 }] },
  ],
};
