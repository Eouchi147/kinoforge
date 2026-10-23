'use client';
// Library: every film in the catalog (plus anything the pipeline published since), filters and search, and the film
// page: the player (a light preview first, the full file one tap away), facts, the recipe from the manual, and review.
import { useEffect, useMemo, useRef, useState } from 'react';
import { useOS, useFetch } from '../store';
import { Head, Panel, FilmTile, Poster, StatusPill, Empty, Note, Seg } from '../ui';
import { Icon } from '../icons';
import { Markdown } from '../Markdown';
import { clock, tc, facet, byDate, needsVerdict, LINE_NAMES, STATUS_NAMES, titleCase } from '@/lib/catalog.mjs';
import { createRoute, score, norm } from '@/lib/commands.mjs';

const FILTERS = [['series', 'Series'], ['style', 'Style'], ['look', 'Look'], ['format', 'Format'], ['status', 'Status']];

export function Library() {
  const { route, go, catalog, reviews } = useOS();
  const remote = useFetch(route.rest ? null : '/api/review');
  if (route.rest) return <FilmPage id={route.rest} />;
  const q = route.query;
  const set = (k, v) => { const next = { ...q, [k]: v }; if (!v) delete next[k]; const s = new URLSearchParams(next).toString(); go('library' + (s ? '?' + s : ''), { replace: true }); };
  const films = catalog?.films || [];
  const verdicts = { ...(remote.data?.verdicts || {}) };
  for (const [id, r] of Object.entries(reviews)) if (r?.verdict) verdicts[id] = r.verdict;
  const words = norm(q.q || '').split(' ').filter(Boolean);
  const shown = films.filter((f) => FILTERS.every(([k]) => !q[k] || String(f[k]) === q[k])
    && (!words.length || score(words, `${f.title} ${f.id} ${f.series} ${f.style} ${f.look || ''} ${f.summary || ''} ${f.format}`) > 0)
    && (q.view !== 'verdict' || needsVerdict(f, Object.fromEntries(Object.entries(verdicts).map(([k, x]) => [k, { verdict: x }]))))).sort(byDate);
  const any = FILTERS.some(([k]) => q[k]) || q.q || q.view;

  return (
    <div className="app library">
      <Head title="Library" lede={catalog ? `${films.length} films. Tap one to watch it, read how it was made, and give your verdict.` : 'Reading the library'} />
      <div className="filterbar" role="search">
        <label className="field search-field">
          <Icon.search size={16} />
          <input type="search" value={q.q || ''} onChange={(e) => set('q', e.target.value)} placeholder="Search the library" aria-label="Search the library" />
        </label>
        {FILTERS.map(([k, label]) => {
          const opts = facet(films, k);
          if (opts.length < 2 && !q[k]) return null;
          return (
            <label key={k} className="field select-field">
              <span className="sr">{label}</span>
              <select value={q[k] || ''} onChange={(e) => set(k, e.target.value)} aria-label={label}>
                <option value="">{label}: all</option>
                {opts.map(([v, n]) => <option key={v} value={v}>{k === 'style' ? LINE_NAMES[v] || titleCase(v) : k === 'status' ? STATUS_NAMES[v] || v : v} ({n})</option>)}
              </select>
            </label>
          );
        })}
        <button className={'chipbtn' + (q.view === 'verdict' ? ' on' : '')} aria-pressed={q.view === 'verdict'} onClick={() => set('view', q.view === 'verdict' ? '' : 'verdict')}>Needs a verdict</button>
        {any && <button className="linkbtn" onClick={() => go('library', { replace: true })}>Clear</button>}
      </div>
      {catalog && !shown.length && <Empty>No film matches. Clear the filters or search for something else.</Empty>}
      <div className="grid-films">{shown.map((f) => <FilmTile key={f.id} f={f} verdict={verdicts[f.id]} />)}</div>
    </div>
  );
}

// ------------------------------------------------------------------ the film page
function FilmPage({ id }) {
  const { catalog, route, go } = useOS();
  const f = catalog?.films.find((x) => x.id === id);
  const [tab, setTab] = useState(route.query.tab === 'recipe' ? 'recipe' : route.query.tab === 'facts' ? 'facts' : 'review');
  const api = useRef(null);
  const [pos, setPos] = useState({ t: 0, frame: 0 });
  useEffect(() => { setPos({ t: 0, frame: 0 }); }, [id]);
  if (!catalog) return <div className="app"><Empty>Reading the library</Empty></div>;
  if (!f) return <div className="app"><Head title="Not in the library" lede={`No film with the id ${id}.`}><a className="btn" href="#/library">Back to the library</a></Head></div>;
  const fps = Number(f.fps) > 0 ? Number(f.fps) : 24;
  const facts = <Facts f={f} />;
  return (
    <div className="app film">
      <nav className="crumbs" aria-label="Breadcrumb"><a href="#/library"><Icon.back size={16} />Library</a><span aria-current="page">{f.title}</span></nav>
      <div className="film-grid">
        <div className="film-main">
          <FramePlayer key={f.id} f={f} fps={fps} onPos={setPos} api={api} />
          <div className="film-title">
            <div>
              <h1>{f.title}</h1>
              <p className="dim">{[f.series, f.format, f.duration_s ? clock(f.duration_s) : null, f.date].filter(Boolean).join(', ')}</p>
            </div>
            <div className="acts">
              {f.downloadUrl && <a className="btn primary" href={f.downloadUrl} rel="noreferrer"><Icon.download size={16} />Full film</a>}
              <a className="btn" href={'#/' + createRoute({ line: f.style === 'cutaway' || f.style === 'battle-map' || f.style === 'kinetic' ? f.style : undefined, format: f.format, look: f.look || undefined })}>Make one like it</a>
            </div>
          </div>
          {f.downloadUrl && f.previewUrl !== f.videoUrl && <p className="dim small">You are watching a lighter preview. Full film downloads the full-quality file.</p>}
          <div className="tabs" role="tablist" aria-label="Film">
            {[['review', 'Review'], ['recipe', 'Recipe'], ['facts', 'Facts']].map(([k, l]) => (
              <button key={k} role="tab" id={`tab-${k}`} aria-selected={tab === k} aria-controls={`pane-${k}`} className={(tab === k ? 'on' : '') + (k === 'facts' ? ' phone-tab' : '')} onClick={() => { setTab(k); go(`library/${id}?tab=${k}`, { replace: true }); }}>{l}</button>
            ))}
          </div>
          <div role="tabpanel" id={`pane-${tab}`} aria-labelledby={`tab-${tab}`} className="tabpane">
            {tab === 'review' && <Review f={f} pos={pos} fps={fps} seekFrame={(n) => api.current?.seekFrame(n)} seek={(t) => api.current?.seek(t)} />}
            {tab === 'recipe' && <Recipe path={f.recipe} />}
            {tab === 'facts' && <div className="phone-facts">{facts}</div>}
          </div>
        </div>
        <aside className="film-side">{facts}</aside>
      </div>
    </div>
  );
}

/** m:ss:ff (seconds and frames), the review timecode. */
export const tcf = (frame, fps) => {
  if (!Number.isFinite(frame) || frame < 0) return '0:00:00';
  const r = Math.round(fps), s = Math.floor(frame / r), ff = frame - s * r;
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}:${String(ff).padStart(2, '0')}`;
};

// The review player: the frame actually on screen (requestVideoFrameCallback where the browser has it, else the time
// update), frame steps by key and by button, and a seek that lands inside a frame ((frame + 0.5) / fps).
// The browser's video element is not guaranteed frame-accurate, so the readout says "frame shown".
function FramePlayer({ f, fps, onPos, api }) {
  const video = useRef(null);
  const [bad, setBad] = useState(false);
  const [tries, setTries] = useState(0);
  const [pos, setPos] = useState({ t: 0, frame: 0 });
  const [paused, setPaused] = useState(true);
  const report = (t) => { const p = { t, frame: Math.max(0, Math.round(t * fps - 0.001)) }; setPos(p); onPos(p); };
  useEffect(() => {
    const v = video.current; if (!v) return;
    let handle = null, live = true;
    if (typeof v.requestVideoFrameCallback === 'function') {
      const tick = (_now, meta) => { if (!live) return; report(meta.mediaTime); handle = v.requestVideoFrameCallback(tick); };
      handle = v.requestVideoFrameCallback(tick);
    }
    return () => { live = false; if (handle != null && v.cancelVideoFrameCallback) v.cancelVideoFrameCallback(handle); };
  }, [tries, fps]);
  const seekFrame = (n) => { const v = video.current; if (!v) return; v.pause(); const d = v.duration || Infinity; const fr = Math.max(0, Math.min(n, Math.floor(d * fps) - 1)); v.currentTime = (fr + 0.5) / fps; report((fr + 0.5) / fps); };
  const seek = (t) => { const v = video.current; if (!v) return; v.pause(); v.currentTime = Math.max(0, t); report(t); };
  const step = (n) => seekFrame(pos.frame + n);
  const toggle = () => { const v = video.current; if (!v) return; if (v.paused) v.play().catch(() => {}); else v.pause(); };
  api.current = { seekFrame, seek };
  useEffect(() => {
    const k = (e) => {
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(e.target?.tagName) || e.target?.isContentEditable || e.metaKey || e.ctrlKey || e.altKey) return;
      const v = video.current; if (!v || document.querySelector('.pal-scrim')) return;
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); const dir = e.key === 'ArrowLeft' ? -1 : 1; e.shiftKey ? seek(v.currentTime + dir) : seekFrame(Math.round(v.currentTime * fps - 0.5) + dir); }
      else if (e.key === 'k' || e.key === 'K' || (e.key === ' ' && e.target?.tagName !== 'BUTTON' && e.target?.tagName !== 'A' && e.target !== v)) { e.preventDefault(); toggle(); }
      else if (e.key === 'j' || e.key === 'J') { e.preventDefault(); seek(v.currentTime - 1); }
      else if (e.key === 'l' || e.key === 'L') { e.preventDefault(); seek(v.currentTime + 1); }
    };
    addEventListener('keydown', k); return () => removeEventListener('keydown', k);
  });
  return (
    <div className="framer">
      <div className={'player' + (f.format === '9:16' ? ' tall' : '')}>
        {f.previewUrl && !bad ? (
          <video key={tries} ref={video} src={f.previewUrl} poster={f.posterUrl || undefined} controls playsInline preload="metadata"
            onTimeUpdate={(e) => { if (typeof e.currentTarget.requestVideoFrameCallback !== 'function') report(e.currentTarget.currentTime); }}
            onSeeked={(e) => report(e.currentTarget.currentTime)} onPlay={() => setPaused(false)} onPause={() => setPaused(true)}
            onError={() => setBad(true)} aria-label={`${f.title}, preview`} />
        ) : (
          <div className="vfail">
            <Poster src={f.posterUrl} format={f.format} label={f.title} />
            <div className="vfail-msg" role="alert">
              <p>{f.previewUrl ? 'This film would not play just now.' : 'No playable file is listed for this film yet.'}</p>
              {f.previewUrl && <button className="btn" onClick={() => { setBad(false); setTries((n) => n + 1); }}>Try again</button>}
            </div>
          </div>
        )}
      </div>
      <div className="transport" role="group" aria-label="Frame controls">
        <button className="btn icon" onClick={() => seek((video.current?.currentTime || 0) - 1)} aria-label="Back one second">-1 s</button>
        <button className="btn icon" onClick={() => step(-1)} aria-label="Back one frame">-1 f</button>
        <button className="btn icon" onClick={toggle} aria-label={paused ? 'Play' : 'Pause'}>{paused ? 'Play' : 'Pause'}</button>
        <button className="btn icon" onClick={() => step(1)} aria-label="Forward one frame">+1 f</button>
        <button className="btn icon" onClick={() => seek((video.current?.currentTime || 0) + 1)} aria-label="Forward one second">+1 s</button>
        <span className="readout" aria-live="off"><span className="mono">{tcf(pos.frame, fps)}</span><span className="dim small">frame {pos.frame} shown, {fps} fps{Number(f.fps) > 0 ? '' : ' (assumed)'}</span></span>
        <span className="keys dim small">Keys: Left and Right one frame, Shift one second, Space or K play, J and L one second</span>
      </div>
    </div>
  );
}

function Facts({ f }) {
  return (
    <Panel title="Facts" className="facts-panel">
      {f.summary && <p>{f.summary}</p>}
      <dl className="facts">
        <dt>Status</dt><dd><StatusPill status={f.status} /></dd>
        {f.verdict && <><dt>Your verdict</dt><dd>{f.verdict}</dd></>}
        <dt>Series</dt><dd>{f.series || 'not recorded'}</dd>
        <dt>Style</dt><dd>{LINE_NAMES[f.style] || titleCase(f.style) || 'not recorded'}{f.look ? `, look ${f.look}` : ''}</dd>
        <dt>Format</dt><dd>{f.format}{f.duration_s ? `, ${clock(f.duration_s)}` : ''}</dd>
        <dt>Sound</dt><dd>{f.sound || 'not recorded'}</dd>
        <dt>Made with</dt><dd>{f.made_with?.length ? f.made_with.join(', ') : 'not recorded'}</dd>
        <dt>Folder</dt><dd>{f.folder ? <a href={`https://github.com/Eouchi147/kinoforge/tree/main/${f.folder}`} target="_blank" rel="noreferrer" className="mono">{f.folder}</a> : 'not recorded'}</dd>
        <dt>Recipe</dt><dd><a href={`#/manual/${f.recipe}`} className="mono">{f.recipe.replace('docs/manual/', '')}</a></dd>
        <dt>Id</dt><dd className="mono">{f.id}</dd>
      </dl>
    </Panel>
  );
}

export function Recipe({ path }) {
  const d = useFetch(path ? `/api/doc?path=${encodeURIComponent(path)}` : null);
  if (d.loading) return <Empty>Reading the recipe from the repo</Empty>;
  if (!d.data?.text) return (
    <Note tone="warn">{d.data?.error === 'not written yet' ? `The recipe page is not written yet (${path}). It appears here by itself once it is on main.` : `The recipe could not be read just now${d.error ? ` (${d.error})` : ''}. Try again in a minute.`}</Note>
  );
  return (
    <article className="md">
      <p className="md-src"><a href={`#/manual/${path}`}>Open in the manual</a> <a href={d.data.web} target="_blank" rel="noreferrer">On GitHub <Icon.external size={14} /></a></p>
      <Markdown text={d.data.text} from={path} />
    </article>
  );
}

// ------------------------------------------------------------------ review: approve, request changes, timecoded notes
function Review({ f, pos, fps, seek, seekFrame }) {
  const t = pos.t;
  const { reviews, saveLocal, lock, status } = useOS();
  const remote = useFetch(`/api/review?id=${encodeURIComponent(f.id)}`);
  const [server, setServer] = useState(null);
  useEffect(() => { if (remote.data?.review) setServer(remote.data.review); }, [remote.data]);
  const local = reviews[f.id] || null;
  const [text, setText] = useState('');
  const [pin, setPin] = useState(true);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);
  const notes = useMemo(() => [
    ...((server?.notes) || []).map((n) => ({ ...n })),
    ...((local?.notes) || []).map((n) => ({ ...n, local: true })),
  ].sort((a, b) => (a.t ?? 1e9) - (b.t ?? 1e9) || String(a.at).localeCompare(String(b.at))), [server, local]);
  const verdict = local?.verdict || server?.verdict || null;
  const locked = lock?.required && !lock?.unlocked;

  async function send(action, words, time) {
    setBusy(true); setMsg(null);
    const frame = time == null ? null : pos.frame;
    const note = { t: time, ...(frame != null ? { frame, fps } : {}), text: words || (action === 'approve' ? 'Approved.' : ''), kind: action, at: new Date().toISOString() };
    try {
      const r = await fetch('/api/review', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: f.id, action, text: words, t: time, frame, fps }) });
      const j = await r.json().catch(() => ({}));
      if (j.saved) { setServer(j.review); setMsg({ tone: 'ok', text: 'Saved to the repo.', url: j.url }); setText(''); return true; }
      throw Object.assign(new Error(j.error || 'The review could not be saved.'), { code: j.code });
    } catch (e) {
      const why = e.code === 'locked' ? 'The studio is locked, so this is kept on this device. Unlock it in Settings, then send it.'
        : e.code === 'no-github' ? 'GitHub is not connected, so this is kept on this device only. Connect GitHub in Settings to save reviews to the repo.'
        : `The repo did not take it (${String(e.message || 'no answer').replace(/[.\s]+$/, '')}). It is kept on this device.`;
      const next = { verdict: action === 'approve' ? 'approved' : action === 'changes' ? 'changes' : local?.verdict || null, notes: [...(local?.notes || []), note] };
      saveLocal(f.id, next); setMsg({ tone: 'warn', text: why }); setText('');
      return false;
    } finally { setBusy(false); }
  }
  async function flush() {
    const pending = [...(local?.notes || [])]; let left = [];
    setBusy(true);
    for (const n of pending) {
      try {
        const r = await fetch('/api/review', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: f.id, action: n.kind, text: n.kind === 'approve' && n.text === 'Approved.' ? '' : n.text, t: n.t, frame: n.frame ?? null, fps: n.fps ?? null }) });
        const j = await r.json(); if (j.saved) setServer(j.review); else left.push(n);
      } catch { left.push(n); }
    }
    saveLocal(f.id, left.length ? { ...local, notes: left } : null);
    setMsg(left.length ? { tone: 'warn', text: `${left.length} still on this device: the repo did not take them.` } : { tone: 'ok', text: 'Sent to the repo.' });
    setBusy(false);
  }
  const submit = (e) => { e.preventDefault(); if (text.trim()) send('note', text.trim(), pin ? Math.round(t * 10) / 10 : null); };

  return (
    <div className="review">
      <div className="verdict-row">
        <div className="verdict-now" aria-live="polite">
          {verdict === 'approved' ? <><i className="led ok" />Approved</> : verdict === 'changes' ? <><i className="led warn" />Changes requested</> : <><i className="led" />No verdict yet</>}
          {local?.verdict && <span className="pill">on this device</span>}
        </div>
        <div className="acts">
          <button className="btn primary" disabled={busy} onClick={() => send('approve', text.trim(), null)}><Icon.check size={16} />Approve</button>
          <button className="btn" disabled={busy} onClick={() => { if (!text.trim()) { setMsg({ tone: 'warn', text: 'Write what should change in the note field first, then tap Request changes.' }); document.getElementById('note-input')?.focus(); return; } send('changes', text.trim(), pin ? Math.round(t * 10) / 10 : null); }}>Request changes</button>
        </div>
      </div>
      <form className="note-form" onSubmit={submit}>
        <button type="button" className={'pinbtn' + (pin ? ' on' : '')} aria-pressed={pin} onClick={() => setPin(!pin)} title="Pin the note to the current playback time">
          <Icon.pin size={16} /><span className="mono">{pin ? tcf(pos.frame, fps) : 'No time'}</span>
        </button>
        <label className="sr" htmlFor="note-input">Note</label>
        <input id="note-input" value={text} onChange={(e) => setText(e.target.value)} placeholder={pin ? `A note at frame ${pos.frame}` : 'A note on the whole film'} maxLength={1500} autoComplete="off" />
        <button className="btn" disabled={busy || !text.trim()}>Add note</button>
      </form>
      {msg && <Note tone={msg.tone}>{msg.text} {msg.url && <a href={msg.url} target="_blank" rel="noreferrer">See the commit file</a>}</Note>}
      {(locked || (status && !status.github)) && !msg && <p className="dim small">{locked ? 'The studio is locked: notes are kept on this device until you unlock it in Settings.' : 'GitHub is not connected: notes are kept on this device only.'}</p>}
      {local?.notes?.length > 0 && !locked && status?.github && <button className="linkbtn" onClick={flush} disabled={busy}>Send {local.notes.length} note{local.notes.length === 1 ? '' : 's'} from this device to the repo</button>}
      <ol className="notes" aria-label="Notes">
        {notes.map((n, i) => (
          <li key={i} className={n.kind}>
            {n.frame != null && (n.fps || fps) === fps ? <button className="tcbtn mono" onClick={() => seekFrame(n.frame)} aria-label={`Go to frame ${n.frame}`} title={`frame ${n.frame}`}>{tcf(n.frame, fps)}</button>
              : n.t != null ? <button className="tcbtn mono" onClick={() => seek(n.t)} aria-label={`Go to ${tc(n.t)}`}>{tc(n.t)}</button> : <span className="tcbtn none mono">whole</span>}
            <span className="ntext">{n.kind === 'changes' && <b>Change: </b>}{n.kind === 'approve' && <b>Approved. </b>}{n.kind === 'approve' && n.text === 'Approved.' ? '' : n.text}</span>
            <span className="nmeta">{n.local ? 'on this device' : (n.at || '').slice(0, 10)}</span>
          </li>
        ))}
        {!notes.length && !remote.loading && <li className="emptyli">No notes yet. Play the film, pause where something matters (step with the arrow keys), and write it down: the note keeps the frame.</li>}
      </ol>
      {remote.data?.error && <p className="dim small">Saved notes could not be read: {remote.data.error}.</p>}
    </div>
  );
}
