// Studio content: films, style packs, build gates. The director writes new films to the repo (films/<slug>/).
export const REPO = 'Eouchi147/kinoforge';

export const STAGES = ['Idea', 'Story', 'Style', 'Animatic', 'Review', 'Render', 'Deliver'];

export const FILMS = [
  {
    id: 'dragon-tale', title: 'The Dragon Who Couldn’t Fly', style: 'Paper theatre', length: '2:06', format: '16:9',
    stage: 4, media: 'dragon-tale-v1', status: 'Prototype v1 · new narrator ready to approve',
    next: 'Watch it with the new narrator on the Voices page, then tap “Use this narrator” (Gate A).',
    logline: 'A dragon crashes into a tiny paper kingdom. Everyone sees a monster; one small girl sees a broken wing.',
  },
  {
    id: 'moon-lesson', title: 'Why the Moon Changes Shape', style: 'Clay', length: '1:02', format: '16:9',
    stage: 4, media: 'moon-lesson-v2', status: 'v2 picture approved in principle · clean narration ready to approve',
    next: 'Watch it with the clean narration on the Voices page, then tap “Use this narrator”.',
    logline: 'A thumb-sized clay kid stands on Earth while a desk lamp plays the Sun, and the Moon’s phases explain themselves.',
  },
  {
    id: 'shadow-pass', title: 'The Shadow at the Pass', style: 'Paper theatre', length: '0:50', format: '9:16',
    stage: 4, media: 'shadow-pass-v1', status: 'Shelved · the story didn’t match the style', next: null, shelved: true,
    logline: 'A child flees a giant shadow, until she turns to face the sun.',
  },
];

// The house styles (the Styles page): what the studio makes films in. `line` = a live production line of the director
// (films/director/lines.json): it builds a whole film from a conversation. `ref` = a finished film to watch (rc-render
// release kino-films, or a local clip).
export const HOUSE_STYLES = [
  { id: 'cutaway', name: 'Cutaway', line: 'cutaway', formats: ['16:9', '9:16'], engine: 'Blender', poster: '/posters/style-cutaway.jpg',
    what: 'A block of land cut out of the world: a living landscape on top, the layers underneath cut clean like a diagram, with surprises buried at their depth. Golden light, fog, animals, easter eggs.',
    best: 'what lies under the surface: cities, digs, geology, nature, how things work underground; ads for trades',
    ref: { id: 'cutaway-loop-seasons', title: 'Four Seasons Over One Block', format: '9:16' } },
  { id: 'battle-map', name: 'Battle Map', line: 'battle-map', formats: ['16:9'], engine: 'Web 3D relief', poster: '/posters/battle-map-cannae.jpg',
    what: 'A 3D relief map with armies as refined unit blocks, arrows that draw on, a legend panel, labels set in code. Upbeat, kid-clear history.',
    best: 'battles, campaigns, journeys, expeditions: anything about places and movement',
    ref: { id: 'battle-map-cannae', title: 'The Battle of Cannae', format: '16:9' } },
  { id: 'kinetic', name: 'Kinetic', line: 'kinetic', formats: ['9:16'], vertical: true, engine: 'Web canvas', poster: '/posters/dark-corners-bamberg-kinetic.jpg',
    what: 'Words, dates, numbers and documents in motion, restrained and adult. Facts carry the weight.',
    best: 'true stories told through words and documents: history, science, ideas',
    ref: { id: 'dark-corners-bamberg-kinetic', title: 'A Hundred Thousand Good Nights', format: '9:16' } },
  { id: 'lantern-road', name: 'Lantern Road', line: null, formats: ['9:16'], engine: 'Web 2.5D', poster: '/posters/dark-corners-zong-lantern-road.jpg',
    what: 'Painterly storybook sets with lantern light and slow moves.', best: 'dark history told as a fable', why: 'Hand-built for now: ask in chat for a film in it.',
    ref: { id: 'dark-corners-zong-lantern-road', title: 'The Ship Called Care', format: '9:16' } },
  { id: 'clay', name: 'Clay', line: null, formats: ['9:16'], engine: 'Blender', poster: '/posters/dark-corners-arabia-clay.jpg',
    what: 'Thumb-sized clay figures and handmade sets, stepped motion.', best: 'intimate human stories', why: 'Hand-built for now: ask in chat for a film in it.',
    ref: { id: 'dark-corners-arabia-clay', title: 'I Am Buying Her Life', format: '9:16' } },
];

// The 12 style packs. `motion` = the style's own motion language (blueprint, "Style motion").
export const STYLES = [
  { id: 'clay', name: 'Clay', media: 'p10-clay', motion: 'Stepped on 2s, clay boil, face-replacement pops', renderer: 'Blender', phase: 'Phase 2 · first' },
  { id: 'paper', name: 'Paper theatre', media: 'p16-paper-dragon', motion: 'Pins and rods only, pendulum swing, lamp-lit', renderer: 'Web canvas', phase: 'Phase 2 · first' },
  { id: 'cel', name: 'Cel', media: 'p06-cel', motion: 'Long holds, smears, impact frames', renderer: 'Web 3D toon', phase: 'Phase 3' },
  { id: 'ink-ember', name: 'Ink Ember', media: 'p02-ink-ember', motion: 'Strokes that draw on, ink bleed, rising embers', renderer: 'Web canvas', phase: 'Phase 3' },
  { id: 'lantern-road', name: 'Lantern Road', media: 'p03-lantern-road', motion: 'Slow storybook moves, painterly boil', renderer: 'Web 2.5D', phase: 'Phase 3' },
  { id: 'pixel-vigil', name: 'Pixel Vigil', media: 'p13-pixel-vigil', motion: 'Whole-pixel moves, hit-stop, 8 to 12 fps cycles', renderer: 'Web pixel', phase: 'Phase 3' },
  { id: 'static', name: 'Static', media: 'p01-static', motion: 'Missed frames, abrupt steps, tape faults', renderer: 'Web VHS', phase: 'Phase 3' },
  { id: 'kinetic', name: 'Kinetic', media: 'p11-kinetic', motion: 'Eased type, overshoot, per-letter stagger', renderer: 'Web canvas', phase: 'Phase 3', vertical: true, line: 'kinetic' },
  { id: 'relic', name: 'Relic', media: 'p05-relic', motion: 'Hero holds, speed ramps, impact flashes', renderer: 'Web 3D', phase: 'Phase 3' },
  { id: 'witness', name: 'Witness', media: 'p04-witness', motion: 'Real motion, handheld camera that lags', renderer: 'Blender', phase: 'Phase 3' },
  { id: 'ash-ascent', name: 'Ash Ascent', media: 'p07-ash-ascent', motion: 'Heavy footfalls, ash and dust on contact', renderer: 'Blender', phase: 'Phase 3' },
  { id: 'terrain', name: 'Terrain', media: 'p12-terrain', motion: 'Camera glides and banks, never clips the land', renderer: 'Web 3D relief', phase: 'Phase 3', line: 'battle-map' },
];

export const BUILD_GATES = [
  { id: 'A', name: 'Gate A', what: 'Pick the narrator', state: 'now' },
  { id: 'B', name: 'Gate B', what: 'Approve the Clay and Paper packs', state: 'later' },
  { id: 'C', name: 'Gate C', what: 'Approve each new style pack', state: 'later' },
  { id: 'D', name: 'Gate D', what: 'Approve episode 0', state: 'later' },
];
