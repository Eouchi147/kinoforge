// The catalog (public/data/catalog.json, written by tools/catalog.py) made ready for the interface. Pure: no fetch,
// no React, so tests can import it. Every field the schema allows to be null is treated as optional.
import { assetUrl, assetDownload } from './assets.mjs';

export const LINE_NAMES = { cutaway: 'Cutaway', 'battle-map': 'Battle Map', kinetic: 'Kinetic' };
export const STATUS_NAMES = { delivered: 'Delivered', rendered: 'Rendered', 'in-progress': 'In progress', draft: 'Draft' };

const arr = (v) => (Array.isArray(v) ? v : []);
const s = (v) => (typeof v === 'string' ? v : v == null ? '' : String(v));
export const titleCase = (id) => s(id).replace(/[-_]+/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

export function normalizeFilm(f) {
  const id = s(f.id);
  const poster = assetUrl(f.poster);
  return {
    ...f, id, title: s(f.title) || titleCase(id), series: s(f.series), style: s(f.style), look: f.look || null,
    format: f.format === '9:16' ? '9:16' : '16:9', duration_s: Number(f.duration_s) || null,
    status: STATUS_NAMES[f.status] ? f.status : 'draft', made_with: arr(f.made_with), date: s(f.date),
    posterUrl: poster, previewUrl: assetUrl(f.preview) || assetUrl(f.video), videoUrl: assetUrl(f.video),
    downloadUrl: assetDownload(f.video), verdict: f.verdict || null, recipe: s(f.recipe) || `docs/manual/films/${id}.md`,
  };
}

export function normalizeStyle(st) {
  const board = arr(st.board).map(assetUrl).filter(Boolean);
  const start = st.start && typeof st.start === 'object' ? st.start : null;
  // key: the name the build and the engine use for a look (films/styles/cutaway/art/<key>.py), e.g. "fable" for "cutaway-fable"
  return { ...st, id: s(st.id), name: s(st.name) || titleCase(st.id), family: st.family === 'cutaway-look' ? 'cutaway-look' : 'house', board, cover: board.find((b) => /-830\.jpg$/.test(b)) || board[0] || null, start, key: start?.look || s(st.id) };
}

export function normalize(raw) {
  const c = raw && typeof raw === 'object' ? raw : {};
  const films = arr(c.films).filter((f) => f && f.id).map(normalizeFilm);
  const styles = arr(c.styles).filter((x) => x && x.id).map(normalizeStyle);
  return {
    generated: s(c.generated), films, styles,
    house: styles.filter((x) => x.family === 'house'), looks: styles.filter((x) => x.family === 'cutaway-look'),
    workflows: arr(c.workflows).filter((w) => w && w.id),
    music: arr(c.music).filter((m) => m && m.id).map((m) => ({ ...m, url: assetUrl(m.asset), download: assetDownload(m.asset) })),
  };
}

/** Films the live pipeline published (GET /api/films "fresh") that the catalog does not know yet. */
export function mergeFresh(cat, fresh) {
  const have = new Set(cat.films.map((f) => f.id));
  const extra = arr(fresh).filter((f) => f && f.id && !have.has(f.id)).map((f) => ({
    id: f.id, title: f.title || titleCase(f.id), series: f.series || 'Studio', style: f.style || '', look: null, format: f.format === '9:16' ? '9:16' : '16:9',
    duration_s: f.duration || null, folder: `films/studio/${f.id}`, status: 'delivered', made_with: ['director pipeline'], date: s(f.at).slice(0, 10),
    summary: f.subject || '', sound: '', verdict: null, recipe: `docs/manual/films/${f.id}.md`,
    posterUrl: f.poster || null, previewUrl: f.preview || null, videoUrl: f.preview || null, downloadUrl: f.full || null, live: true,
  }));
  return { ...cat, films: [...extra, ...cat.films] };
}

/** Values for a filter, in a stable order, with counts. */
export function facet(films, key) {
  const m = new Map();
  for (const f of films) { const v = f[key]; if (v) m.set(v, (m.get(v) || 0) + 1); }
  return [...m.entries()].sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0])));
}

export const byDate = (a, b) => s(b.date).localeCompare(s(a.date));
export const needsVerdict = (f, reviews = {}) => f.status === 'delivered' && !f.verdict && !reviews[f.id]?.verdict;

export const clock = (sec) => {
  if (!Number.isFinite(sec) || sec < 0) return '0:00';
  const m = Math.floor(sec / 60), r = sec - m * 60;
  return `${m}:${String(Math.floor(r)).padStart(2, '0')}`;
};
/** Timecode for notes: m:ss.t */
export const tc = (sec) => {
  if (!Number.isFinite(sec) || sec < 0) return '0:00.0';
  const m = Math.floor(sec / 60), r = sec - m * 60;
  return `${m}:${r.toFixed(1).padStart(4, '0')}`;
};
