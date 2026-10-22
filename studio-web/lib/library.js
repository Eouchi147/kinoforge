// The film library: the twelve films in rc-render's `kino-films` release (static catalogue, titles and lengths from
// each film's film.json) plus anything the studio's own pipeline publishes to kinoforge's `films` release (read live).
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

const fromCatalogue = (f) => ({
  ...f, source: 'kino-films',
  preview: mediaUrl('kino-films', `${f.id}-preview.mp4`),
  full: downloadUrl('kino-films', `${f.id}.mp4`),
  poster: `/posters/${f.id}.jpg`,
  sheet: mediaUrl('kino-films', `${f.id}-sheet.jpg`),
});

const pretty = (id) => id.replace(/[-_]+/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

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
      const line = brief?.line === 'kinetic' ? 'kinetic' : brief?.line === 'battle-map' ? 'battle-map' : null;
      const file = (a) => a && mediaUrl('films', a.name);
      return {
        id: g.id, title: brief?.title || pretty(g.id), series: line === 'kinetic' ? 'Kinetic' : line === 'battle-map' ? 'Battle Map' : 'Studio',
        line, style: line === 'kinetic' ? 'Kinetic' : line === 'battle-map' ? 'Terrain' : '', format: line === 'kinetic' ? '9:16' : '16:9',
        duration: brief?.target_seconds || null, subject: brief?.subject || null, source: 'films', at: g.at,
        preview: file(g.preview) || file(g.full), full: g.full ? downloadUrl('films', g.full.name) : null,
        poster: file(g.poster), sheet: file(g.sheet), size: g.full?.size || null,
      };
    }));
    return films.sort((a, b) => (b.at || '').localeCompare(a.at || ''));
  } catch { return []; }
}

export async function library() {
  const fresh = await liveFilms();
  return { fresh, films: KINO_FILMS.map(fromCatalogue) };
}
