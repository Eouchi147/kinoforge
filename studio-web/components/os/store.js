'use client';
// The OS's shared state: the route (hash), the catalog, the studio status, the write lock, local reviews.
import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { normalize, mergeFresh } from '@/lib/catalog.mjs';

export const OSContext = createContext(null);
export const useOS = () => useContext(OSContext);

// ------------------------------------------------------------------ routes: #/<app>/<rest>?<query>
const LEGACY = { director: 'create', films: 'library', renders: 'jobs', setup: 'settings', styles: 'styles' };
export const APP_IDS = ['desk', 'library', 'create', 'styles', 'jobs', 'sound', 'manual', 'settings'];

export function parseHash(hash) {
  const raw = String(hash || '');
  if (raw && raw !== '#' && !raw.startsWith('#/') && !/^#(job\/|director$|films$|renders$|setup$|styles$)/.test(raw)) return null;   // an in-page anchor (#main), not a route
  let h = decodeURIComponent(raw.replace(/^#\/?/, ''));
  if (/^job\/[a-z0-9-]+$/.test(h)) h = 'jobs/' + h.slice(4);                 // links from the old studio
  if (LEGACY[h]) h = LEGACY[h];
  const [path, qs = ''] = h.split('?');
  const parts = path.split('/').filter(Boolean);
  const app = APP_IDS.includes(parts[0]) ? parts[0] : 'desk';
  let rest = parts.slice(1).join('/'), anchor = null;
  if (rest.includes('~')) [rest, anchor] = rest.split('~');
  return { app, rest, parts: parts.slice(1), query: Object.fromEntries(new URLSearchParams(qs)), anchor };
}

export function useRoute() {
  const [route, setRoute] = useState({ app: 'desk', rest: '', parts: [], query: {} });
  useEffect(() => {
    const sync = () => { const r = parseHash(location.hash); if (r) setRoute(r); };
    sync(); addEventListener('hashchange', sync); return () => removeEventListener('hashchange', sync);
  }, []);
  const go = useCallback((r, { replace = false } = {}) => {
    const next = '#/' + String(r || 'desk').replace(/^#?\/?/, '');
    const prevApp = parseHash(location.hash)?.app;
    if (replace) { history.replaceState(null, '', next); setRoute(parseHash(next)); }
    else if (location.hash !== next) location.hash = next;
    if (parseHash(next).app !== prevApp) window.scrollTo({ top: 0 });
  }, []);
  return [route, go];
}

// ------------------------------------------------------------------ fetching
export function useFetch(url, { every = 0, init = null } = {}) {
  const [state, setState] = useState({ data: init, error: null, loading: Boolean(url) });
  const live = useRef(true);
  const load = useCallback(async () => {
    if (!url) return;
    try {
      const r = await fetch(url, { cache: 'no-store' });
      const j = await r.json().catch(() => null);
      if (!live.current) return;
      if (!r.ok && !j) throw new Error(`The studio answered ${r.status}.`);
      setState({ data: j, error: r.ok ? null : j?.error || `The studio answered ${r.status}.`, loading: false });
    } catch (e) { if (live.current) setState((s) => ({ ...s, error: e.message || 'No answer.', loading: false })); }
  }, [url]);
  useEffect(() => {
    live.current = true; load();
    const t = every ? setInterval(() => { if (document.visibilityState === 'visible') load(); }, every) : null;
    return () => { live.current = false; if (t) clearInterval(t); };
  }, [load, every]);
  return { ...state, reload: load };
}

/** The catalog: public/data/catalog.json when it exists, else the bundled fixture (said plainly in Settings). */
export function useCatalog() {
  const [cat, setCat] = useState(null);
  useEffect(() => {
    let live = true;
    (async () => {
      let raw = null, source = 'catalog';
      try { const r = await fetch('/data/catalog.json', { cache: 'no-store' }); if (r.ok) raw = await r.json(); } catch { /* fall back */ }
      if (!raw) { raw = (await import('@/lib/catalog.fixture.json')).default; source = 'fixture'; }
      let c = { ...normalize(raw), source };
      if (live) setCat(c);
      try {
        const f = await fetch('/api/films').then((r) => r.json());
        c = { ...mergeFresh(c, f.fresh), source };
        if (live) setCat(c);
      } catch { /* the catalog alone is enough */ }
    })();
    return () => { live = false; };
  }, []);
  return cat;
}

// ------------------------------------------------------------------ local reviews (kept on this device until saved)
const RKEY = 'kf-reviews-1';
export function readLocalReviews() { try { return JSON.parse(localStorage.getItem(RKEY) || '{}'); } catch { return {}; } }
export function writeLocalReviews(v) { try { localStorage.setItem(RKEY, JSON.stringify(v)); } catch { /* private mode */ } }

export const ago = (d) => {
  if (!d) return '';
  const m = Math.max(0, Math.round((Date.now() - new Date(d)) / 60000));
  return m < 1 ? 'just now' : m < 60 ? `${m} min ago` : m < 1440 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} d ago`;
};
export const usd = (n) => (Number.isFinite(Number(n)) && n !== null ? `$${Number(n).toFixed(2)}` : '');
/** Scroll behaviour that respects reduced motion. */
export const smooth = () => (typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth');
