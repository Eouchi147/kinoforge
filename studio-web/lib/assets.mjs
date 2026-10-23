// Where a catalog asset is served from. Pure functions (no Next, no Node APIs) so tests can import them.
// An asset is either a plain path in public/ ("/looks/fable-830.jpg", "/posters/x.jpg") or a release asset
// { repo: "Eouchi147/rc-render" | "Eouchi147/kinoforge", release: "<tag>", name: "<file>" }.

export const REPOS = { kinoforge: 'Eouchi147/kinoforge', 'rc-render': 'Eouchi147/rc-render' };
// Old short keys kept for links already in use (lib/library.js, /api/job).
export const RELEASES = {
  'kino-films': { repo: 'Eouchi147/rc-render', tag: 'kino-films' },
  films: { repo: 'Eouchi147/kinoforge', tag: 'films' },
  gallery: { repo: 'Eouchi147/kinoforge', tag: 'gallery' },
};
export const NAME_OK = /^[A-Za-z0-9][A-Za-z0-9._-]{0,140}\.(mp4|jpg|jpeg|png|webp|mp3|m4a|ogg|oga|opus|wav|flac)$/;
export const TYPES = {
  mp4: 'video/mp4', jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp',
  mp3: 'audio/mpeg', m4a: 'audio/mp4', ogg: 'audio/ogg', oga: 'audio/ogg', opus: 'audio/ogg', wav: 'audio/wav', flac: 'audio/flac',
};

/** A release key ("kino-films", or "<repo short>:<tag>" for any release of the two public studio repos) to {repo, tag}. */
export function resolveRelease(key) {
  if (RELEASES[key]) return RELEASES[key];
  const m = /^(kinoforge|rc-render):([a-z0-9][a-z0-9._-]{0,40})$/.exec(String(key || ''));
  return m ? { repo: REPOS[m[1]], tag: m[2] } : null;
}

/** Same-origin URL that streams a release asset (supports Range, so video and audio can seek). */
export const mediaUrl = (release, name) => `/api/media?r=${encodeURIComponent(release)}&f=${encodeURIComponent(name)}`;
/** Direct GitHub download URL (public repos): big files never pass through the studio. */
export const downloadUrl = (release, name) => {
  const r = resolveRelease(release);
  return r ? `https://github.com/${r.repo}/releases/download/${r.tag}/${encodeURIComponent(name)}` : null;
};

const short = (repo) => Object.keys(REPOS).find((k) => REPOS[k] === repo);
const isLocal = (a) => typeof a === 'string' && /^\/[A-Za-z0-9._\/-]+$/.test(a) && !a.includes('..');

/** Streaming URL for an asset in either shape, or null. */
export function assetUrl(a) {
  if (!a) return null;
  if (typeof a === 'string') return isLocal(a) ? a : null;
  const s = short(a.repo);
  if (!s || !a.release || !NAME_OK.test(a.name || '')) return null;
  return mediaUrl(`${s}:${a.release}`, a.name);
}
/** Download URL for an asset in either shape (local files download from the site itself). */
export function assetDownload(a) {
  if (!a) return null;
  if (typeof a === 'string') return isLocal(a) ? a : null;
  const s = short(a.repo);
  return s && a.release && a.name ? downloadUrl(`${s}:${a.release}`, a.name) : null;
}
