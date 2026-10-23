// The film library: the twelve films in rc-render's `kino-films` release (static catalogue, titles and lengths from
// each film's film.json), the Cutaway films (listed as soon as their files land in `kino-films`: read live), plus
// anything the studio's own pipeline publishes to kinoforge's `films` release (read live).
import { mediaUrl, downloadUrl } from './media';
import { REPO } from './data';

const dc = (id, title, style, duration, subject) => ({ id: `dark-corners-${id}`, title, series: 'Dark Corners', line: null, style, format: '9:16', duration, subject });
const bm = (id, title, duration, subject) => ({ id: `battle-map-${id}`, title, series: 'Battle Map', line: 'battle-map', style: 'Terrain', format: '16:9', duration, subject });
export const KINO_FILMS = [
  bm('cannae', 'The Battle of Cannae', 157.6, '216 BC'),
  bm('hastings', 'The Battle of Hastings', 155.4, '1066'),
  bm('agincourt', 'The Battle of Agincourt', 147.3, '1415'),
  bm('waterloo', 'The Battle of Waterloo', 158.5, '1815'),
  bm('thermopylae', 'The Battle of Thermopylae', 164.1, '480 BC'),
  bm('gaugamela', 'The Battle of Gaugamela', 151.3, '331 BC'),
  bm('hattin', 'The Battle of Hattin', 141.6, '1187'),
  bm('ain-jalut', 'The Battle of Ain Jalut', 139.6, '1260'),
  dc('bamberg-kinetic', 'A Hundred Thousand Good Nights', 'Kinetic', 163.3, 'The Bamberg witch trials'),
  dc('zong-lantern-road', 'The Ship Called Care', 'Lantern Road', 179.4, 'The Zong, 1781'),
  dc('kleidion-lantern-road', 'As They Say', 'Lantern Road', 169.0, 'Kleidion, 1014'),
  dc('arabia-clay', 'I Am Buying Her Life', 'Clay', 175.8, null),
];

// Cutaway (Blender cross-section worlds, films/cutaway/ and films/styles/cutaway/). Each shows up by itself once
// `<id>.mp4` or `<id>-preview.mp4` is in rc-render's `kino-films` release (ids are the film.json ids).
const cw = (id, title, format, duration, subject, series = 'Cutaway') => ({ id, title, series, line: null, style: 'Cutaway', format, duration, subject });
export const CUTAWAY_FILMS = [
  cw('under-the-surface-venice', 'Why Venice Sinks', '16:9', 157.0, 'Under the Surface, film 1', 'Under the Surface'),
  cw('cutaway-loop-seasons', 'Four Seasons Over One Block', '9:16', 12, 'Social loop'),
  cw('cutaway-ad-drainage-v169', 'Drainage and Landscaping (sample ad)', '16:9', 15, 'Sample trade ad, invented business'),
  cw('cutaway-ad-drainage-v916', 'Drainage and Landscaping (sample ad)', '9:16', 15, 'Sample trade ad, vertical'),
  cw('style-cutaway-cinematic', 'Cutaway, the cinematic test', '16:9', 12, 'Golden light, fog, animals, easter eggs'),
  cw('cutaway-line-meadow', 'What Lies Under a Meadow', '16:9', 39.9, 'The Cutaway line example'),
];

const fromCatalogue = (f) => ({
  ...f, source: 'kino-films',
  preview: mediaUrl('kino-films', `${f.id}-preview.mp4`),
  full: downloadUrl('kino-films', `${f.id}.mp4`),
  poster: `/posters/${f.id}.jpg`,
  sheet: mediaUrl('kino-films', `${f.id}-sheet.jpg`),
});

const pretty = (id) => id.replace(/[-_]+/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

/** Asset names in rc-render's `kino-films` release (cached for a minute), or null when GitHub does not answer. */
async function kinoAssets() {
  try {
    const r = await gh('repos/Eouchi147/rc-render/releases/tags/kino-films', { next: { revalidate: 60 } });
    if (!r.ok) return null;
    return new Set(((await r.json()).assets || []).map((a) => a.name));
  } catch { return null; }
}

/** The Cutaway films whose files exist; poster: a committed one in public/posters, else the release poster, else the sheet. */
async function cutawayFilms(posters) {
  const have = await kinoAssets();
  if (!have) return [];
  return CUTAWAY_FILMS.filter((f) => have.has(`${f.id}.mp4`) || have.has(`${f.id}-preview.mp4`)).map((f) => ({
    ...f, source: 'kino-films',
    preview: mediaUrl('kino-films', have.has(`${f.id}-preview.mp4`) ? `${f.id}-preview.mp4` : `${f.id}.mp4`),
    full: have.has(`${f.id}.mp4`) ? downloadUrl('kino-films', `${f.id}.mp4`) : null,
    poster: posters.has(f.id) ? `/posters/${f.id}.jpg` : have.has(`${f.id}-poster.jpg`) ? mediaUrl('kino-films', `${f.id}-poster.jpg`) : have.has(`${f.id}-sheet.jpg`) ? mediaUrl('kino-films', `${f.id}-sheet.jpg`) : null,
    sheet: have.has(`${f.id}-sheet.jpg`) ? mediaUrl('kino-films', `${f.id}-sheet.jpg`) : null,
  }));
}

// Posters committed in public/posters (a frame chosen by hand), by film id.
const POSTERS = new Set(['cutaway-loop-seasons']);

async function gh(path, opts = {}) {
  const token = process.env.GITHUB_TOKEN;
  return fetch(`https://api.github.com/${path}`, {
    headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'kinoforge-studio', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    signal: AbortSignal.timeout(9000), ...opts,
  });
}

/** Films the studio pipeline published to kinoforge's `films` release, read live (cached for a minute). */
async function liveFilms() {
  try {
    const r = await gh(`repos/${REPO}/releases/tags/films`, { next: { revalidate: 60 } });
    if (!r.ok) return [];
    const assets = (await r.json()).assets || [];
    const by = {};
    for (const a of assets) {
      const m = /^(.+?)(-preview|-poster|-sheet)?\.(mp4|jpg)$/.exec(a.name);
      if (!m) continue;
      const slot = m[2] ? m[2].slice(1) : m[3] === 'mp4' ? 'full' : null;
      if (!slot) continue;
      (by[m[1]] ||= { id: m[1], at: a.updated_at })[slot] = a;
      if (a.updated_at > by[m[1]].at) by[m[1]].at = a.updated_at;
    }
    const films = await Promise.all(Object.values(by).filter((g) => g.full || g.preview).map(async (g) => {
      let brief = null;
      try {
        const b = await gh(`repos/${REPO}/contents/films/studio/${encodeURIComponent(g.id)}/brief.json`, { headers: { Accept: 'application/vnd.github.raw+json', 'User-Agent': 'kinoforge-studio', ...(process.env.GITHUB_TOKEN ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {}) }, next: { revalidate: 300 } });
        if (b.ok) brief = await b.json();
      } catch { /* the title falls back to the id */ }
      const line = ['kinetic', 'battle-map', 'cutaway'].includes(brief?.line) ? brief.line : null;
      const file = (a) => a && mediaUrl('films', a.name);
      return {
        id: g.id, title: brief?.title || pretty(g.id), series: { kinetic: 'Kinetic', 'battle-map': 'Battle Map', cutaway: 'Cutaway' }[line] || 'Studio',
        line, style: { kinetic: 'Kinetic', 'battle-map': 'Terrain', cutaway: 'Cutaway' }[line] || '',
        format: line === 'kinetic' ? '9:16' : line === 'cutaway' ? (brief?.format === '9:16' ? '9:16' : '16:9') : '16:9',
        duration: brief?.target_seconds || null, subject: brief?.subject || null, source: 'films', at: g.at,
        preview: file(g.preview) || file(g.full), full: g.full ? downloadUrl('films', g.full.name) : null,
        poster: file(g.poster), sheet: file(g.sheet), size: g.full?.size || null,
      };
    }));
    return films.sort((a, b) => (b.at || '').localeCompare(a.at || ''));
  } catch { return []; }
}

export async function library() {
  const [fresh, cutaway] = await Promise.all([liveFilms(), cutawayFilms(POSTERS)]);
  return { fresh, films: [...KINO_FILMS.map(fromCatalogue), ...cutaway] };
}
