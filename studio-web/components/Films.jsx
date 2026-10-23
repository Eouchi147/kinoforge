'use client';
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { appear, ease, mins } from './ui';
import { FILMS } from '@/lib/data';

// A poster that fits any film: 16:9 fills the tile, 9:16 sits in the middle over a soft blur of itself.
function Thumb({ film }) {
  const v = film.format === '9:16';
  return (
    <div className="thumb">
      {film.poster ? (
        <>
          {v && <img className="backdrop" src={film.poster} alt="" aria-hidden="true" loading="lazy" />}
          <img className={v ? 'portrait' : ''} src={film.poster} alt="" loading="lazy" />
        </>
      ) : <div className="noposter">{film.title}</div>}
      <span className="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m9 6.5 9 5.5-9 5.5z" fill="currentColor" /></svg></span>
      <span className="fmt">{film.format}{film.duration ? ` · ${mins(film.duration)}` : ''}</span>
    </div>
  );
}

function Tile({ film, open, i }) {
  return (
    <motion.button className="tile glass" onClick={() => open(film)} {...appear(Math.min(i, 8) * 0.5)} aria-label={`Play ${film.title}`}>
      <Thumb film={film} />
      <div className="meta"><b>{film.title}</b><span>{[film.series, film.subject].filter(Boolean).join(' · ')}</span></div>
    </motion.button>
  );
}

const FILTERS = [['all', 'All'], ['cutaway', 'Cutaway'], ['battle', 'Battle Map'], ['dark', 'Dark Corners'], ['new', 'Made in this studio']];

export function Films({ open, initial = 'all' }) {
  const [lib, setLib] = useState(null);
  const [err, setErr] = useState(false);
  const [show, setShow] = useState(initial);
  useEffect(() => {
    let live = true;
    const load = () => fetch('/api/films').then((r) => r.json()).then((j) => live && setLib(j)).catch(() => live && setErr(true));
    load(); const t = setInterval(load, 60000);
    return () => { live = false; clearInterval(t); };
  }, []);
  const battles = lib?.films.filter((f) => f.series === 'Battle Map') || [];
  const dark = lib?.films.filter((f) => f.series === 'Dark Corners') || [];
  const cutaway = [...(lib?.fresh || []).filter((f) => f.style === 'Cutaway'), ...(lib?.films.filter((f) => f.style === 'Cutaway') || [])];
  const fresh = (lib?.fresh || []).filter((f) => f.style !== 'Cutaway');
  const pilots = FILMS.map((f) => ({ id: f.id, title: f.title, series: 'Early test', subject: f.style, format: f.format, poster: `/media/${f.media}.jpg`, preview: `/media/${f.media}.mp4`, full: null }));
  const on = (k) => show === 'all' || show === k;
  let n = 0;
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Films</h1><p className="lede">Every film the studio has made. Tap one to watch it; the full-quality file is one tap away.</p></div></motion.div>
      <div className="filters" role="group" aria-label="Show">
        {FILTERS.map(([k, label]) => <button key={k} className={'chip' + (show === k ? ' on' : '')} aria-pressed={show === k} onClick={() => setShow(k)}>{label}</button>)}
      </div>
      {err && <div className="card glass" role="alert">The library could not load. Check your connection and reload.</div>}
      {!lib && !err && <div className="card glass" role="status">Loading the library</div>}
      {on('new') && !!fresh.length && (
        <section aria-labelledby="h-new">
          <h2 className="sect" id="h-new">Made in this studio</h2>
          <div className="row">{fresh.map((f) => <Tile key={f.id} film={f} open={open} i={n++} />)}</div>
        </section>
      )}
      {on('cutaway') && lib && (
        <section aria-labelledby="h-cw">
          <h2 className="sect" id="h-cw">Cutaway <span className="faint">worlds cut open: life on top, layers and surprises underneath</span></h2>
          {cutaway.length
            ? <div className="row">{cutaway.map((f) => <Tile key={f.id} film={f} open={open} i={n++} />)}</div>
            : <p className="faint" style={{ margin: '12px 0 0' }}>The first Cutaway films are rendering. They appear here on their own when they are ready.</p>}
        </section>
      )}
      {on('battle') && !!battles.length && (
        <section aria-labelledby="h-bm">
          <h2 className="sect" id="h-bm">Battle Map <span className="faint">16:9, upbeat history on a relief map</span></h2>
          <div className="row">{battles.map((f) => <Tile key={f.id} film={f} open={open} i={n++} />)}</div>
        </section>
      )}
      {on('dark') && !!dark.length && (
        <section aria-labelledby="h-dc">
          <h2 className="sect" id="h-dc">Dark Corners <span className="faint">9:16, adult, restrained</span></h2>
          <div className="row">{dark.map((f) => <Tile key={f.id} film={f} open={open} i={n++} />)}</div>
        </section>
      )}
      {show === 'all' && (
        <section aria-labelledby="h-old">
          <h2 className="sect" id="h-old">Early tests <span className="faint">the first animation pilots, kept for reference</span></h2>
          <div className="row">{pilots.map((f) => <Tile key={f.id} film={f} open={open} i={n++} />)}</div>
        </section>
      )}
    </>
  );
}

// The player: any release or local file, 16:9 or 9:16, with a real error state and the full-quality download.
export function Player({ item, close }) {
  const [bad, setBad] = useState(false);
  const [tries, setTries] = useState(0);
  const closeBtn = useRef(null);
  useEffect(() => {
    const prev = document.activeElement; closeBtn.current?.focus();
    const k = (e) => e.key === 'Escape' && close();
    addEventListener('keydown', k); document.body.style.overflow = 'hidden';
    return () => { removeEventListener('keydown', k); document.body.style.overflow = ''; prev?.focus?.(); };
  }, [close]);
  const v = item.format === '9:16';
  return (
    <motion.div className="scrim" onClick={close} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div className="sheet glass" role="dialog" aria-modal="true" aria-label={item.title} onClick={(e) => e.stopPropagation()} initial={{ scale: 0.94, y: 24, opacity: 0 }} animate={{ scale: 1, y: 0, opacity: 1 }} exit={{ scale: 0.97, y: 12, opacity: 0 }} transition={{ duration: 0.5, ease }}>
        <div className={'screen' + (v ? ' tall' : '')}>
          {bad ? (
            <div className="vfail" role="alert"><p>This clip would not play right now.</p><button className="btn lamp" onClick={() => { setBad(false); setTries(tries + 1); }}>Try again</button></div>
          ) : (
            <video key={tries} src={item.preview} poster={item.poster || undefined} controls autoPlay playsInline preload="auto" onError={() => setBad(true)} />
          )}
        </div>
        <div className="bar">
          <div><h2 style={{ margin: 0 }}>{item.title}</h2><div className="faint">{[item.series, item.subject, item.format, item.duration ? mins(item.duration) : null].filter(Boolean).join(' · ')}</div></div>
          <div className="actions">
            {item.full && <a className="btn lamp" href={item.full} rel="noreferrer">Download full film</a>}
            {item.sheet && <a className="btn ghost" href={item.sheet} target="_blank" rel="noreferrer">Contact sheet</a>}
            <button ref={closeBtn} className="btn ghost" onClick={close}>Close</button>
          </div>
        </div>
        {item.full && <p className="faint foot">You are watching a lighter preview. The download is the full-quality film.</p>}
      </motion.div>
    </motion.div>
  );
}
