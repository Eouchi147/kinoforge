'use client';
// Manual: an in-app reader for docs/GUIDE.md (the short human guide) and docs/manual/** (the AI manual), read from the
// public repo at request time. A tree, a search (titles at once, full text from the server), rendered Markdown.
import { useEffect, useMemo, useState } from 'react';
import { useOS, useFetch } from '../store';
import { Empty, Note } from '../ui';
import { Icon } from '../icons';
import { Markdown, outline } from '../Markdown';
import { fallbackDocs } from '../Palette';
import { score, norm } from '@/lib/commands.mjs';

const GROUPS = { '': 'Start here', system: 'System', workflows: 'Workflows', styles: 'Styles and looks', films: 'Film recipes', sound: 'Sound' };
const groupOf = (p) => (p === 'docs/GUIDE.md' || p === 'docs/manual/README.md' ? '' : p.replace(/^docs\/manual\//, '').split('/').slice(0, -1).join('/'));
const groupName = (g) => GROUPS[g] || g.replace(/[-_/]+/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

export function Manual() {
  const { route, go, catalog, docs, needDocs } = useOS();
  useEffect(() => { needDocs(); }, [needDocs]);
  const pages = docs?.length ? docs : fallbackDocs(catalog);
  const offline = docs && !docs.length;
  const [q, setQ] = useState(route.query.q || '');
  useEffect(() => { setQ(route.query.q || ''); }, [route.query.q]);
  const [debounced, setDebounced] = useState(q);
  useEffect(() => { const t = setTimeout(() => setDebounced(q.trim()), 400); return () => clearTimeout(t); }, [q]);
  const full = useFetch(debounced.length > 2 ? `/api/manual?q=${encodeURIComponent(debounced)}` : null);
  const path = route.rest || null;
  const words = norm(q).split(' ').filter(Boolean);
  const shown = words.length ? pages.filter((d) => score(words, `${d.title} ${d.path.replace(/[/._-]+/g, ' ')}`) > 0) : pages;
  const groups = useMemo(() => {
    const m = new Map();
    for (const d of shown) { const g = groupOf(d.path); if (!m.has(g)) m.set(g, []); m.get(g).push(d); }
    return [...m.entries()].sort((a, b) => (a[0] === '' ? -1 : b[0] === '' ? 1 : Object.keys(GROUPS).indexOf(a[0]) - Object.keys(GROUPS).indexOf(b[0]) || a[0].localeCompare(b[0])));
  }, [shown]);
  const open = path || 'docs/GUIDE.md';

  return (
    <div className={'app manual' + (path ? ' reading' : '')}>
      <div className="man-grid">
        <nav className="man-nav" aria-label="Manual contents">
          <h1 className="man-h1">Manual</h1>
          <label className="field search-field">
            <Icon.search size={16} />
            <input type="search" value={q} placeholder="Search the manual" aria-label="Search the manual"
              onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') go(`manual${path ? '/' + path : ''}?q=${encodeURIComponent(q)}`, { replace: true }); }} />
          </label>
          {offline && <Note tone="warn">GitHub did not list the manual just now: showing the pages the catalog knows.</Note>}
          {debounced.length > 2 && (
            <div className="man-hits" aria-live="polite">
              <h2>In the text</h2>
              {full.loading && <Empty>Searching</Empty>}
              {full.data?.hits && !full.data.hits.length && <Empty>No page mentions that.</Empty>}
              {full.data?.error && <Note tone="warn">{full.data.error}</Note>}
              <ul>{(full.data?.hits || []).map((h) => <li key={h.path}><a href={`#/manual/${h.path}`} aria-current={h.path === open ? 'page' : undefined}><b>{h.title}</b><span className="small dim">{h.snippet}</span></a></li>)}</ul>
            </div>
          )}
          {groups.map(([g, list]) => (
            <div key={g || 'start'} className="man-group">
              <h2>{groupName(g)}<span className="count">{list.length}</span></h2>
              <ul>{list.map((d) => <li key={d.path}><a href={`#/manual/${d.path}`} aria-current={d.path === open ? 'page' : undefined}>{d.title}</a></li>)}</ul>
            </div>
          ))}
          {!shown.length && <Empty>No title matches.</Empty>}
        </nav>
        <Reader path={open} anchor={route.anchor} />
      </div>
    </div>
  );
}

function Reader({ path, anchor }) {
  const d = useFetch(`/api/doc?path=${encodeURIComponent(path)}`);
  const heads = outline(d.data?.text);
  useEffect(() => { if (anchor && d.data?.text) setTimeout(() => document.getElementById(anchor)?.scrollIntoView(), 50); }, [anchor, d.data]);
  useEffect(() => { document.querySelector('.man-read')?.scrollTo?.({ top: 0 }); }, [path]);
  return (
    <article className="man-read" aria-label="Page">
      <div className="man-top">
        <a className="man-back" href="#/manual"><Icon.back size={16} />Contents</a>
        <span className="mono dim small">{path.replace(/^docs\//, '')}</span>
        {d.data?.web && <a className="small" href={d.data.web} target="_blank" rel="noreferrer">On GitHub <Icon.external size={14} /></a>}
      </div>
      {d.loading && <Empty>Reading the page from the repo</Empty>}
      {!d.loading && !d.data?.text && (
        <Note tone="warn">{d.data?.error === 'not written yet' ? `This page is not written yet (${path}). It appears here by itself once it is on main.` : `The page could not be read just now${d.error ? ` (${d.error})` : ''}.`}</Note>
      )}
      {heads.length > 3 && (
        <details className="man-outline"><summary>On this page ({heads.length})</summary>
          <ul>{heads.map((h, i) => <li key={i} className={'l' + h.level}><a href={`#/manual/${path}~${h.id}`}>{h.text}</a></li>)}</ul>
        </details>
      )}
      {d.data?.text && <div className="md"><Markdown text={d.data.text} from={path} /></div>}
    </article>
  );
}
