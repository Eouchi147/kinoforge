// Where finished media lives. The web studio never serves big files itself from disk: it streams them from public
// GitHub releases through /api/media (so <video> can seek), from an allow-list, with no token involved.
export const RELEASES = {
  'kino-films': { repo: 'Eouchi147/rc-render', tag: 'kino-films' },
  films: { repo: 'Eouchi147/kinoforge', tag: 'films' },
  gallery: { repo: 'Eouchi147/kinoforge', tag: 'gallery' },
};
export const NAME_OK = /^[A-Za-z0-9][A-Za-z0-9._-]{0,120}\.(mp4|jpg|jpeg|png|webp)$/;
export const TYPES = { mp4: 'video/mp4', jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp' };

/** Same-origin URL that streams a release asset (supports Range). */
export const mediaUrl = (release, name) => `/api/media?r=${encodeURIComponent(release)}&f=${encodeURIComponent(name)}`;
/** Direct GitHub download URL (public repos): used for "Download the full file" so big files never pass through us. */
export const downloadUrl = (release, name) => { const r = RELEASES[release]; return r ? `https://github.com/${r.repo}/releases/download/${r.tag}/${encodeURIComponent(name)}` : null; };
