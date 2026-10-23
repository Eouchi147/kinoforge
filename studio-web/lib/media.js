// Where finished media lives. The web studio never serves big files itself from disk: it streams them from public
// GitHub releases through /api/media (so <video> can seek), from an allow-list, with no token involved.
// The functions live in assets.mjs (pure, tested); this file keeps the old import path working.
export { RELEASES, NAME_OK, TYPES, resolveRelease, mediaUrl, downloadUrl, assetUrl, assetDownload } from './assets.mjs';
