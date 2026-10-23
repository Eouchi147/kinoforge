'use client';
// Styles: the house styles and the Cutaway looks with their board images, a style page, side-by-side compare of two,
// and "Use this look", which opens Create preset. Early prototypes (the first style tests) are kept at the end.
import { useEffect, useRef, useState } from 'react';
import { useOS } from '../store';
import { Head, Panel, Empty, Seg } from '../ui';
import { Icon } from '../icons';
import { Recipe } from './Library';
import { createRoute } from '@/lib/commands.mjs';
import { STYLES as PROTOTYPES } from '@/lib/data';

const startHref = (s) => '#/' + createRoute(s.start ? { line: s.start.line || undefined, format: s.start.format || undefined, look: s.start.look || undefined } : { look: s.id });
const FRAMES = [['hero', 'Hero', /-830\.jpg$|-768\.jpg$/], ['layers', 'Layers', /-470\.jpg$|-440\.jpg$/], ['seasons', 'Seasons 9:16', /seasons-[a-z-]+-\d+\.jpg$/]];
const frameOf = (s, kind) => { const re = FRAMES.find(([k]) => k === kind)?.[2]; return (re && s.board.find((b) => re.test(b))) || null; };

export function Styles() {
  const { route, catalog } = useOS();
  const [pick, setPick] = useState([]);
  const p = route.parts;
  if (!catalog) return <div className="app"><Head title="Styles" /><Empty>Reading the catalog</Empty></div>;
  if (p[0] === 'compare') return <Compare a={p[1]} b={p[2]} />;
  const view = p[0] === 'looks' ? 'looks' : p[0] === 'early' ? 'early' : p[0] && p[0] !== 'house' ? 'one' : 'house';
  if (view === 'one') return <StylePage id={p[0]} />;
  const toggle = (id) => setPick((x) => (x.includes(id) ? x.filter((y) => y !== id) : [...x, id].slice(-2)));
  const list = view === 'looks' ? catalog.looks : catalog.house;
  return (
    <div className="app styles">
      <Head title="Styles" lede={view === 'looks' ? 'Twelve art directions for the same Cutaway world. Tick two to compare them side by side, or use one to start a film.' : view === 'early' ? 'The first style prototypes, kept for reference.' : 'The looks the studio makes films in. Use one to start a film preset.'} />
      <div className="tabs" role="tablist" aria-label="Styles">
        {[['house', 'House styles', catalog.house.length], ['looks', 'Cutaway looks', catalog.looks.length], ['early', 'Early prototypes', PROTOTYPES.length]].map(([k, l, n]) => (
          <a key={k} role="tab" aria-selected={view === k} className={view === k ? 'on' : ''} href={`#/styles/${k === 'house' ? '' : k}`}>{l}<span className="n">{n}</span></a>
        ))}
      </div>
      {view === 'early' ? <Early /> : (
        <div className="grid-styles">
          {list.map((s) => (
            <article key={s.id} className={'style-card' + (pick.includes(s.id) ? ' picked' : '')} aria-labelledby={`st-${s.id}`}>
              <a className="sc-img" href={`#/styles/${s.id}`} aria-label={`Open ${s.name}`}>
                {s.cover ? <img src={s.cover} alt="" loading="lazy" /> : <span className="noposter">{s.name}</span>}
              </a>
              <div className="sc-body">
                <h3 id={`st-${s.id}`}><a href={`#/styles/${s.id}`}>{s.name}</a></h3>
                <p>{s.summary}</p>
                {s.best_for && s.best_for !== 'not recorded' && <p className="dim small">Best for: {s.best_for}</p>}
                <div className="acts">
                  {s.start?.line ? <a className="btn primary" href={startHref(s)}>{s.family === 'cutaway-look' ? 'Use this look' : 'Start a film'}</a> : <span className="dim small">Made by an agent: ask for it in chat</span>}
                  <label className="check"><input type="checkbox" checked={pick.includes(s.id)} onChange={() => toggle(s.id)} /> Compare</label>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
      {pick.length > 0 && view !== 'early' && (
        <div className="comparebar" role="region" aria-label="Compare">
          <span>{pick.map((id) => catalog.styles.find((s) => s.id === id)?.name).join(' and ')}</span>
          {pick.length === 2 ? <a className="btn primary" href={`#/styles/compare/${pick[0]}/${pick[1]}`}>Compare side by side</a> : <span className="dim small">Tick one more</span>}
          <button className="linkbtn" onClick={() => setPick([])}>Clear</button>
        </div>
      )}
    </div>
  );
}

function StylePage({ id }) {
  const { catalog } = useOS();
  const s = catalog.styles.find((x) => x.id === id);
  const [big, setBig] = useState(0);
  if (!s) return <div className="app"><Head title="Not found" lede={`No style with the id ${id}.`}><a className="btn" href="#/styles">All styles</a></Head></div>;
  const other = s.family === 'cutaway-look' ? catalog.looks.find((l) => l.id !== s.id) : null;
  return (
    <div className="app style-page">
      <nav className="crumbs" aria-label="Breadcrumb"><a href={s.family === 'cutaway-look' ? '#/styles/looks' : '#/styles'}><Icon.back size={16} />{s.family === 'cutaway-look' ? 'Cutaway looks' : 'House styles'}</a><span aria-current="page">{s.name}</span></nav>
      <div className="sp-grid">
        <div>
          <div className="board-main">{s.board[big] ? <img src={s.board[big]} alt={`${s.name}, board frame ${big + 1}`} /> : <span className="noposter">No board image yet</span>}</div>
          {s.board.length > 1 && (
            <div className="board-thumbs" role="group" aria-label="Board frames">
              {s.board.map((b, i) => <button key={b + i} className={i === big ? 'on' : ''} aria-pressed={i === big} onClick={() => setBig(i)}><img src={b} alt={`Frame ${i + 1}`} loading="lazy" /></button>)}
            </div>
          )}
        </div>
        <Panel title={s.name}>
          <p>{s.summary}</p>
          <dl className="facts">
            <dt>Family</dt><dd>{s.family === 'cutaway-look' ? 'Cutaway look (art direction)' : 'House style'}</dd>
            {s.best_for && <><dt>Best for</dt><dd>{s.best_for}</dd></>}
            {s.engine && <><dt>Engine</dt><dd><a className="mono" href={`https://github.com/Eouchi147/kinoforge/tree/main/${s.engine}`} target="_blank" rel="noreferrer">{s.engine}</a></dd></>}
            {s.recipe && <><dt>Recipe</dt><dd><a className="mono" href={`#/manual/${s.recipe}`}>{s.recipe.replace('docs/manual/', '')}</a></dd></>}
          </dl>
          <div className="acts">
            {s.start?.line ? <a className="btn primary" href={startHref(s)}>{s.family === 'cutaway-look' ? 'Use this look' : 'Start a film'}</a> : <span className="dim small">Not in the builder yet: made by an agent, ask for it in chat.</span>}
            {other && <a className="btn" href={`#/styles/compare/${s.id}/${other.id}`}>Compare</a>}
          </div>
        </Panel>
      </div>
      {s.recipe && <Panel title="Recipe" className="recipe-panel"><Recipe path={s.recipe} /></Panel>}
    </div>
  );
}

function Compare({ a, b }) {
  const { catalog, go } = useOS();
  const all = catalog.styles;
  const A = all.find((s) => s.id === a) || catalog.looks[0], B = all.find((s) => s.id === b) || catalog.looks[1] || A;
  const kinds = FRAMES.filter(([k]) => frameOf(A, k) || frameOf(B, k));
  const [kind, setKind] = useState(kinds[0]?.[0] || 'hero');
  const img = (s) => frameOf(s, kind) || s.cover;
  const side = (s, which) => (
    <figure className="cmp-side">
      <div className="cmp-img">{img(s) ? <img src={img(s)} alt={`${s.name}, ${kind}`} /> : <span className="noposter">{s.name}</span>}</div>
      <figcaption>
        <label className="field select-field">
          <span className="sr">{which === 'a' ? 'Left' : 'Right'} style</span>
          <select value={s.id} onChange={(e) => go(`styles/compare/${which === 'a' ? e.target.value : A.id}/${which === 'b' ? e.target.value : B.id}`, { replace: true })}>
            <optgroup label="Cutaway looks">{catalog.looks.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}</optgroup>
            <optgroup label="House styles">{catalog.house.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}</optgroup>
          </select>
        </label>
        <p className="small dim">{s.summary}</p>
        {s.start?.line ? <a className="btn primary" href={startHref(s)}>{s.family === 'cutaway-look' ? 'Use this look' : 'Start a film'}</a> : <span className="dim small">Made by an agent: ask for it in chat</span>}
      </figcaption>
    </figure>
  );
  return (
    <div className="app compare">
      <nav className="crumbs" aria-label="Breadcrumb"><a href="#/styles/looks"><Icon.back size={16} />Cutaway looks</a><span aria-current="page">Compare</span></nav>
      <Head title={`${A.name} and ${B.name}`}>
        {kinds.length > 1 && <Seg label="Frame" value={kind} onChange={setKind} options={kinds.map(([k, l]) => [k, l])} />}
      </Head>
      <div className="cmp">{side(A, 'a')}{side(B, 'b')}</div>
    </div>
  );
}

function Early() {
  const [open, setOpen] = useState(null);
  return (
    <>
      <div className="grid-films">
        {PROTOTYPES.map((s) => (
          <button key={s.id} className="tile" onClick={() => setOpen(s)}>
            <span className="poster" style={{ aspectRatio: '16 / 9' }}>
              {s.vertical && <img className="bd" src={`/media/${s.media}.jpg`} alt="" aria-hidden="true" loading="lazy" />}
              <img className={s.vertical ? 'tall' : ''} src={`/media/${s.media}.jpg`} alt="" loading="lazy" />
              <span className="playmark" aria-hidden="true"><Icon.play size={16} /></span>
            </span>
            <span className="tile-meta"><b>{s.name}</b><span>{s.motion}</span></span>
          </button>
        ))}
      </div>
      {open && <Clip s={open} close={() => setOpen(null)} />}
    </>
  );
}

function Clip({ s, close }) {
  const btn = useRef(null);
  useEffect(() => {
    const prev = document.activeElement; btn.current?.focus();
    const k = (e) => e.key === 'Escape' && close(); addEventListener('keydown', k);
    return () => { removeEventListener('keydown', k); prev?.focus?.(); };
  }, [close]);
  return (
    <div className="pal-scrim" onMouseDown={close}>
      <div className="clip" role="dialog" aria-modal="true" aria-label={`${s.name} test clip`} onMouseDown={(e) => e.stopPropagation()}>
        <video src={`/media/${s.media}.mp4`} poster={`/media/${s.media}.jpg`} controls autoPlay playsInline />
        <div className="clip-bar"><div><b>{s.name}</b><p className="dim small">{s.motion}. {s.renderer}.</p></div><button ref={btn} className="btn" onClick={close}>Close</button></div>
      </div>
    </div>
  );
}
