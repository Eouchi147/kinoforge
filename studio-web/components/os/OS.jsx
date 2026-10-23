'use client';
// KINOFORGE Studio OS: the shell. A rail of apps (a bottom bar on phones), a command bar (Ctrl K or Cmd K, and the
// visible search field), and one app on screen at a time, chosen by the hash route (#/<app>/<rest>?<query>).
// To add an app: write components/os/apps/<Name>.jsx, add it to APPS below and to APP_IDS in store.js, give it an
// icon in icons.jsx and a line in lib/commands.mjs APPS (so the command bar finds it).
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { OSContext, useRoute, useCatalog, useFetch, readLocalReviews, writeLocalReviews } from './store';
import { APP_ICON, Icon } from './icons';
import { Palette } from './Palette';
import { Desk } from './apps/Desk';
import { Library } from './apps/Library';
import { Create } from './apps/Create';
import { Styles } from './apps/Styles';
import { Jobs } from './apps/Jobs';
import { Sound } from './apps/Sound';
import { Manual } from './apps/Manual';
import { Settings } from './apps/Settings';
import { Spend } from './apps/Spend';

export const APPS = [
  { id: 'desk', name: 'Desk', C: Desk, phone: true },
  { id: 'library', name: 'Library', C: Library, phone: true },
  { id: 'create', name: 'Create', C: Create, phone: true },
  { id: 'styles', name: 'Styles', C: Styles },
  { id: 'jobs', name: 'Jobs', C: Jobs, phone: true },
  { id: 'sound', name: 'Sound', C: Sound },
  { id: 'spend', name: 'Spend', C: Spend },
  { id: 'manual', name: 'Manual', C: Manual },
  { id: 'settings', name: 'Settings', C: Settings },
];

function Wordmark() {
  return (
    <a className="wordmark" href="#/desk" aria-label="KINOFORGE Studio, go to the desk">
      <svg viewBox="0 0 28 28" width="26" height="26" aria-hidden="true"><rect x="1" y="1" width="26" height="26" rx="5" fill="none" stroke="currentColor" strokeOpacity=".35" /><path d="M8 7v14M8 14l8-7M11 11.5 18 21" stroke="var(--lamp)" strokeWidth="2.2" fill="none" strokeLinecap="round" strokeLinejoin="round" /><circle cx="20.5" cy="7.5" r="1.6" fill="var(--lamp)" /></svg>
      <span><b>KINOFORGE</b><small>Studio</small></span>
    </a>
  );
}

export default function OS() {
  const [route, go] = useRoute();
  const catalog = useCatalog();
  const status = useFetch('/api/status');
  const lock = useFetch('/api/unlock');
  const [palette, setPalette] = useState(null);         // null | '' | initial text
  const [more, setMore] = useState(false);
  const [reviews, setReviews] = useState({});
  const [docs, setDocs] = useState(null);
  useEffect(() => { setReviews(readLocalReviews()); }, []);
  const saveLocal = useCallback((id, r) => setReviews((all) => { const next = { ...all, [id]: r }; if (!r) delete next[id]; writeLocalReviews(next); return next; }), []);

  // Ctrl K / Cmd K, and "/" when not typing, open the command bar.
  useEffect(() => {
    const k = (e) => {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target?.tagName) || e.target?.isContentEditable;
      if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); setPalette((p) => (p == null ? '' : null)); }
      else if (e.key === '/' && !typing && palette == null) { e.preventDefault(); setPalette(''); }
    };
    addEventListener('keydown', k); return () => removeEventListener('keydown', k);
  }, [palette]);
  useEffect(() => { setMore(false); }, [route.app]);

  // Manual pages for the command bar: fetched once, on first need.
  const asked = useRef(false);
  const needDocs = useCallback(() => {
    if (asked.current) return;
    asked.current = true;
    fetch('/api/manual').then((r) => r.json()).then((j) => setDocs(j.pages?.length ? j.pages : [])).catch(() => setDocs([]));
  }, []);

  const ctx = useMemo(() => ({
    route, go, catalog, status: status.data, statusError: status.error, reloadStatus: status.reload, lock: lock.data, reloadLock: lock.reload,
    reviews, saveLocal, docs, needDocs, openPalette: (t = '') => setPalette(t),
  }), [route, go, catalog, status.data, status.error, status.reload, lock.data, lock.reload, reviews, saveLocal, docs, needDocs]);

  const App = (APPS.find((a) => a.id === route.app) || APPS[0]).C;
  const here = APPS.find((a) => a.id === route.app) || APPS[0];
  useEffect(() => { document.title = `${here.name}, KINOFORGE Studio`; }, [here.name]);
  const connected = status.data?.openrouter, github = status.data?.github, locked = lock.data?.required && !lock.data?.unlocked;

  return (
    <OSContext.Provider value={ctx}>
      <a className="skip" href="#main">Skip to content</a>
      <div className="house-lights" aria-hidden="true" />
      <div className="os">
        <aside className="rail" aria-label="Studio apps">
          <Wordmark />
          <button className="cmd" onClick={() => setPalette('')} aria-label="Search or type a command (Control K)">
            <Icon.search size={16} /><span>Search</span><kbd>Ctrl K</kbd>
          </button>
          <nav>
            <ul>
              {APPS.map((a) => { const I = APP_ICON[a.id]; return (
                <li key={a.id}><a href={`#/${a.id}`} aria-current={route.app === a.id ? 'page' : undefined}><I /><span>{a.name}</span></a></li>
              ); })}
            </ul>
          </nav>
          <div className="rail-foot" aria-label="Connections">
            <a href="#/settings"><i className={'led ' + (connected ? 'ok' : status.data ? 'off' : '')} />Director {connected ? 'online' : status.data ? 'offline' : ''}</a>
            <a href="#/settings"><i className={'led ' + (github ? 'ok' : status.data ? 'off' : '')} />GitHub {github ? 'connected' : status.data ? 'read only' : ''}</a>
            <a href="#/settings"><i className={'led ' + (lock.data ? (lock.data.required ? (locked ? 'warn' : 'ok') : 'warn') : '')} />{lock.data ? (lock.data.required ? (locked ? 'Locked' : 'Unlocked') : 'Writes open') : 'Lock'}</a>
          </div>
        </aside>

        <header className="topbar">
          <a className="wordmark small" href="#/desk" aria-label="KINOFORGE Studio, go to the desk"><b>KINOFORGE</b></a>
          <button className="cmd wide" onClick={() => setPalette('')} aria-label="Search or type a command (Control K)">
            <Icon.search size={16} /><span>Search films, looks, the manual, or type a command</span><kbd>Ctrl K</kbd>
          </button>
          <button className="iconbtn phone-only" onClick={() => setPalette('')} aria-label="Search or type a command"><Icon.search /></button>
        </header>

        <main id="main" className="stage" tabIndex={-1}>
          <App />
        </main>

        <nav className="dock" aria-label="Studio apps">
          {APPS.filter((a) => a.phone).map((a) => { const I = APP_ICON[a.id]; return (
            <a key={a.id} href={`#/${a.id}`} aria-current={route.app === a.id ? 'page' : undefined}><I /><span>{a.name}</span></a>
          ); })}
          <button aria-expanded={more} aria-controls="more-sheet" className={APPS.some((a) => !a.phone && a.id === route.app) ? 'on' : ''} onClick={() => setMore((m) => !m)}><Icon.more /><span>More</span></button>
        </nav>
        {more && (
          <div className="more-scrim" onClick={() => setMore(false)}>
            <div id="more-sheet" className="more-sheet" role="dialog" aria-label="More apps" onClick={(e) => e.stopPropagation()}>
              {APPS.filter((a) => !a.phone).map((a) => { const I = APP_ICON[a.id]; return (
                <a key={a.id} href={`#/${a.id}`} aria-current={route.app === a.id ? 'page' : undefined} onClick={() => setMore(false)}><I /><span>{a.name}</span></a>
              ); })}
            </div>
          </div>
        )}
      </div>
      {palette != null && <Palette initial={palette} close={() => setPalette(null)} />}
    </OSContext.Provider>
  );
}
