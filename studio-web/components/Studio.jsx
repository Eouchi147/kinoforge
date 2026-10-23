'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion, LayoutGroup } from 'framer-motion';
import { STYLES, HOUSE_STYLES, BUILD_GATES, REPO } from '@/lib/data';
import { mediaUrl } from '@/lib/media';
import { Films, Player } from './Films';
import { Job } from './Job';
import { appear, ease } from './ui';

// ------------------------------------------------------------------ icons (2px strokes, round)
const I = {
  director: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H11l-4.5 4v-4H6.5A2.5 2.5 0 0 1 4 13.5z"/><path d="M8.5 9.5h7M8.5 12.5h4"/></svg>,
  films: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m10 9.5 4.5 2.5-4.5 2.5z"/></svg>,
  styles: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="8" cy="8" r="3.5"/><circle cx="16" cy="8" r="3.5"/><circle cx="8" cy="16" r="3.5"/><circle cx="16" cy="16" r="3.5"/></svg>,
  voices: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 10v4M8 7v10M12 4v16M16 8v8M20 11v2"/></svg>,
  renders: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="3"/></svg>,
  setup: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="8" cy="15" r="4"/><path d="m11 12 8-8M16 7l2 2M14 9l2 2"/></svg>,
  send: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>,
};
const TABS = [['director', 'Director'], ['films', 'Films'], ['renders', 'Renders'], ['styles', 'Styles'], ['setup', 'Setup']];

// The lamp: a warm studio light that follows the pointer and catches every glass edge.
function useLamp() {
  useEffect(() => {
    const root = document.documentElement;
    let raf = 0, tx = innerWidth * 0.7, ty = innerHeight * 0.2, x = tx, y = ty;
    const move = (e) => { const p = e.touches ? e.touches[0] : e; tx = p.clientX; ty = p.clientY; if (!raf) raf = requestAnimationFrame(step); };
    const step = () => { x += (tx - x) * 0.14; y += (ty - y) * 0.14; root.style.setProperty('--mx', x + 'px'); root.style.setProperty('--my', y + 'px'); raf = Math.abs(tx - x) + Math.abs(ty - y) > 0.5 ? requestAnimationFrame(step) : 0; };
    addEventListener('pointermove', move, { passive: true }); addEventListener('touchmove', move, { passive: true });
    if (/Chrome\//.test(navigator.userAgent) && !/Edg\//.test(navigator.userAgent)) root.classList.add('liquid');
    requestAnimationFrame(() => root.style.setProperty('--lit', '1'));        // the lamp comes up (the one orchestrated moment)
    return () => { removeEventListener('pointermove', move); removeEventListener('touchmove', move); };
  }, []);
}

export default function Studio() {
  useLamp();
  const [tab, setTab] = useState('director');
  const [status, setStatus] = useState(null);
  const [player, setPlayer] = useState(null);
  const [job, setJob] = useState(null);                 // id of the film job being watched (#job/<id>)
  const [seed, setSeed] = useState(null);               // a house style picked on the Styles page: {line, format, say}
  useEffect(() => { fetch('/api/status').then((r) => r.json()).then(setStatus).catch(() => setStatus({ openrouter: false, github: false })); }, []);
  useEffect(() => {
    const sync = () => {
      const h = location.hash.slice(1);
      if (h.startsWith('job/') && /^[a-z0-9-]+$/.test(h.slice(4))) { setJob(h.slice(4)); setTab('job'); }
      else if (TABS.some(([k]) => k === h)) setTab(h);
    };
    sync(); addEventListener('hashchange', sync); return () => removeEventListener('hashchange', sync);
  }, []);
  const go = (k) => { setTab(k); history.replaceState(null, '', '#' + k); window.scrollTo({ top: 0, behavior: 'smooth' }); };
  const openJob = (id) => { try { localStorage.setItem('kf-job', id); } catch {} setJob(id); setTab('job'); history.replaceState(null, '', '#job/' + id); window.scrollTo({ top: 0 }); };

  return (
    <>
      <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
        <filter id="liquid" x="-10%" y="-10%" width="120%" height="120%">
          <feTurbulence type="fractalNoise" baseFrequency="0.006 0.009" numOctaves="2" seed="7" result="n" />
          <feGaussianBlur in="n" stdDeviation="2" result="s" />
          <feDisplacementMap in="SourceGraphic" in2="s" scale="24" xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </svg>
      <div className="field" aria-hidden="true"><div className="orb lamp" /><div className="orb moon" /><div className="orb dusk" /><div className="pointer" /><div className="grain" /></div>
      <div className="shell">
        <motion.nav className="dock glass refract" aria-label="Studio" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 1, delay: 0.15, ease }}>
          <Mark />
          <LayoutGroup>
            {TABS.map(([k, label]) => (
              <button key={k} className="navbtn" aria-current={tab === k || (tab === 'job' && k === 'director') ? 'page' : undefined} onClick={() => go(k)}>
                {(tab === k || (tab === 'job' && k === 'director')) && <motion.i layoutId="pill" className="navpill" transition={{ type: 'spring', stiffness: 420, damping: 34 }} />}
                {I[k]}<span>{label}</span>
              </button>
            ))}
          </LayoutGroup>
          <div className="spacer" />
        </motion.nav>
        <main className="main">
          <AnimatePresence mode="wait">
            <motion.div key={tab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.45, ease }}>
              {tab === 'director' && <Director status={status} go={go} openJob={openJob} seed={seed} clearSeed={() => setSeed(null)} />}
              {tab === 'job' && job && <Job id={job} onWatch={setPlayer} goDirector={() => go('director')} />}
              {tab === 'films' && <Films open={setPlayer} />}
              {tab === 'styles' && <Styles open={setPlayer} pick={(x) => { setSeed({ ...x, at: Date.now() }); go('director'); }} />}
              {tab === 'renders' && <Renders />}
              {tab === 'setup' && <Setup status={status} />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
      <AnimatePresence>{player && <Player item={player} close={() => setPlayer(null)} />}</AnimatePresence>
    </>
  );
}

function Mark() {
  return (
    <svg className="mark" viewBox="0 0 40 40" aria-label="KINOFORGE">
      <defs><radialGradient id="mk" cx="50%" cy="38%" r="60%"><stop offset="0" stopColor="#ffe2b0" /><stop offset=".55" stopColor="#ffc46b" /><stop offset="1" stopColor="#f29b4b" /></radialGradient></defs>
      <path d="M20 5c6 0 10 3.4 10 8.6 0 3.4-1.8 5.4-3.6 7.2H13.6C11.8 19 10 17 10 13.6 10 8.4 14 5 20 5Z" fill="url(#mk)" />
      <path d="M13 23.5h14l3.6 11.5H9.4z" fill="rgba(255,196,107,.28)" />
      <rect x="15" y="20.8" width="10" height="2.4" rx="1.2" fill="#f5efe4" opacity=".85" />
    </svg>
  );
}

// ------------------------------------------------------------------ Director: the conversation
const LINE_NAME = { 'battle-map': 'Battle Map, 16:9', kinetic: 'Kinetic, 9:16', cutaway: 'Cutaway' };
const lineName = (b) => b?.line === 'cutaway' ? `Cutaway, ${b.format === '9:16' ? '9:16' : '16:9'}` : LINE_NAME[b?.line];
const complete = (b) => ['title', 'line', 'subject', 'angle', 'audience', 'tone', 'target_seconds'].every((k) => b?.[k]);
const lengthOf = (s) => (s ? `${Math.floor(s / 60)} min ${String(Math.round(s % 60)).padStart(2, '0')} s` : null);

function Director({ status, go, openJob, seed, clearSeed }) {
  const [msgs, setMsgs] = useState([]);
  const [brief, setBrief] = useState(null);
  const [options, setOptions] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const [text, setText] = useState('');
  const [fallback, setFallback] = useState(null);       // one line when a free model is answering
  const [building, setBuilding] = useState(false);
  const [buildErr, setBuildErr] = useState(null);
  const [lastJob, setLastJob] = useState(null);
  const thread = useRef(null);
  const connected = status?.openrouter;
  const started = useRef(false);

  useEffect(() => {
    try {
      const s = JSON.parse(localStorage.getItem('kf-director-2') || 'null');
      if (s) { setMsgs(s.msgs || []); setBrief(s.brief || null); setOptions(s.options || []); setFallback(s.fallback || null); started.current = Boolean(s.msgs?.length); }
      setLastJob(localStorage.getItem('kf-job'));
    } catch {}
  }, []);
  useEffect(() => { try { localStorage.setItem('kf-director-2', JSON.stringify({ msgs, brief, options, fallback })); } catch {} }, [msgs, brief, options, fallback]);
  useEffect(() => { thread.current?.scrollTo({ top: 1e6, behavior: 'smooth' }); }, [msgs, busy]);
  useEffect(() => { if (connected && !started.current && !busy && !seed) { started.current = true; send(null); } }, [connected]);   // the director opens the conversation
  // A house style picked on the Styles page: the line goes into the brief and the director hears the choice.
  useEffect(() => {
    if (!seed || !connected || busy) return;
    started.current = true; clearSeed();
    const b = { ...(brief || {}), line: seed.line, ...(seed.format ? { format: seed.format } : {}) };
    setBrief(b); send(seed.say, b);
  }, [seed, connected]);

  async function send(content, briefNow = brief) {
    const next = content ? [...msgs, { role: 'user', content }] : msgs;
    if (content) setMsgs(next);
    setText(''); setOptions([]); setBusy(true); setErr(null);
    try {
      const r = await fetch('/api/director', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: next.map(({ role, content }) => ({ role, content })), brief: briefNow }) });
      const j = await r.json().catch(() => ({ error: 'The reply could not be read.' }));
      if (!r.ok) throw Object.assign(new Error(j.error), { code: j.code });
      setMsgs([...next, { role: 'assistant', content: j.say, by: j.director }]); setOptions(j.options || []); setBrief(j.brief || briefNow);
      setFallback(j.director?.fallback ? j.director.note : null);
    } catch (e) {
      setErr(e.code === 'credits' ? 'The studio key is out of credit and no free model could answer. Try again in a minute, or add credit on openrouter.ai.' : e.code === 'no-key' ? null : 'No model answered just now. Send your message again in a minute.');
      if (!content) started.current = false;
    }
    setBusy(false);
  }
  async function build() {
    setBuilding(true); setBuildErr(null);
    try {
      const r = await fetch('/api/build', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ brief }) });
      const j = await r.json();
      if (!j.saved) throw new Error(j.code === 'no-github' ? 'Connect GitHub on the Setup page so the studio can start builds.' : j.error || 'The build could not be started.');
      openJob(j.id);
    } catch (e) { setBuildErr(e.message); }
    setBuilding(false);
  }
  const reset = () => { setMsgs([]); setBrief(null); setOptions([]); setErr(null); setFallback(null); setBuildErr(null); started.current = false; try { localStorage.removeItem('kf-director-2'); } catch {} if (connected) setTimeout(() => { started.current = true; send(null); }, 0); };
  const ok = complete(brief);
  const credit = status?.account?.remaining;
  const lowLine = fallback || (credit != null && credit < 0.05 ? 'The studio key is out of credit, so free models answer.' : null);
  const nextForSam = !status ? 'Checking the studio' : !status.openrouter ? 'Connect the director’s brain: add your OpenRouter key (Setup).' : ok ? 'The brief is complete. Tap “Build this film” when you are happy with it.' : 'Tell the director a subject, any subject, or tap an answer.';

  return (
    <>
      <motion.div className="page-head" {...appear(0)}>
        <div><h1>What are we making?</h1><p className="lede">Name a subject. The director picks the line, the angle and the length with you, then the studio builds the film and hands it back.</p></div>
        {lastJob && <button className="btn ghost" onClick={() => openJob(lastJob)}>Open the last build</button>}
      </motion.div>
      <div className="director">
        <motion.section className="convo glass refract" {...appear(1)} aria-label="Conversation with the director">
          <div className="thread" ref={thread} aria-live="polite">
            {!connected && status && (
              <div className="msg ai">I’m the studio’s director. I need my brain connected before we talk: it takes a few steps on the Setup page, and I’ll be ready the moment you finish.</div>
            )}
            {msgs.map((m, i) => (
              <motion.div key={i} className={'msg ' + (m.role === 'user' ? 'me' : 'ai')} initial={{ opacity: 0, y: 8, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.4, ease }}>{m.content}</motion.div>
            ))}
            {busy && <div className="msg ai thinking" aria-label="The director is thinking"><i /><i /><i /></div>}
            {err && <div className="msg ai" role="alert">{err} <button className="opt" style={{ marginInlineStart: 6 }} onClick={() => send(msgs.length ? msgs[msgs.length - 1].role === 'user' ? msgs[msgs.length - 1].content : 'Please go on.' : null)}>Try again</button></div>}
            {!!options.length && !busy && (
              <div className="options">{options.map((o) => <button key={o} className="opt" onClick={() => send(o)}>{o}</button>)}</div>
            )}
          </div>
          {ok && !busy && <div className="inlinebuild"><button className="btn lamp" disabled={building} onClick={build}>{building ? 'Starting' : 'Build this film'}</button>{buildErr && <p role="alert" style={{ margin: '8px 0 0', color: '#ffb4b4' }}>{buildErr}</p>}</div>}
          {lowLine && <p className="notice" role="status"><i className="dot run" />{lowLine}</p>}
          <form className="composer" onSubmit={(e) => { e.preventDefault(); if (text.trim()) send(text.trim()); }}>
            <textarea rows={1} value={text} placeholder={connected ? 'Name a subject, or reply' : 'Connect the director on the Setup page first'} disabled={!connected || busy}
              onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (text.trim()) send(text.trim()); } }} aria-label="Message" />
            <button className="btn lamp" disabled={!connected || busy || !text.trim()} aria-label="Send">{I.send}</button>
          </form>
        </motion.section>
        <aside className="side">
          <motion.div className="next glass" {...appear(2)}>
            <div className="label">Your next step</div>
            <p>{nextForSam}</p>
            {status && !status.openrouter && <button className="btn lamp" onClick={() => go('setup')}>Open Setup</button>}
            {ok && <button className="btn lamp" disabled={building} onClick={build}>{building ? 'Starting' : 'Build this film'}</button>}
            {ok && <p className="faint" style={{ margin: '10px 0 0' }}>{brief?.line === 'cutaway' ? 'Free models and free render machines: $0. A Cutaway film renders for a few hours on GitHub. Nothing is published without you.' : 'About $1 to $1.50 of model time, capped at $1.50. Nothing is published without you.'}</p>}
            {buildErr && <p role="alert" style={{ margin: '10px 0 0', color: '#ffb4b4' }}>{buildErr}</p>}
          </motion.div>
          <motion.div className="card brief glass" {...appear(3)}>
            <h2>The film so far</h2>
            <dl>
              {[['Title', brief?.title], ['Line', lineName(brief)], ['Subject', brief?.subject], ['Angle', brief?.angle], ['Audience', brief?.audience], ['Tone', brief?.tone], ['Length', lengthOf(brief?.target_seconds)], ['Extras', brief?.notes], ['Narrator', 'the series narrator']].map(([k, v]) => (
                <div key={k} style={{ display: 'contents' }}><dt>{k}</dt><dd className={v ? '' : 'empty'}>{v || 'not decided yet'}</dd></div>
              ))}
            </dl>
            {!!msgs.length && <button className="btn ghost" style={{ marginTop: 16 }} onClick={reset}>Start a new film</button>}
          </motion.div>
          {(() => { const by = [...msgs].reverse().find((m) => m.by)?.by;
            return status?.openrouter && (
              <p className="faint" style={{ margin: '0 6px' }}>
                {by ? <>Last answer: {by.head}{by.crew?.length ? <>, with {by.crew.length} crew drafts</> : null}, {(by.ms / 1000).toFixed(0)} s, ${by.usd.toFixed(3)}.</> : <>Director: {(status.seats?.head?.[0] || '').split('/').pop()}.</>}
                {credit != null && <> ${credit.toFixed(2)} left on the studio key.</>}
              </p>); })()}
        </aside>
      </div>
    </>
  );
}

// ------------------------------------------------------------------ Styles: the house styles, then the early test looks
function Styles({ open, pick }) {
  const play = (h) => open({ title: h.name, series: 'House style', subject: h.ref.title, format: h.ref.format, poster: h.poster,
    preview: h.ref.local ? h.ref.local : mediaUrl('kino-films', `${h.ref.id}-preview.mp4`), full: null });
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>House styles</h1><p className="lede">The looks the studio makes films in. Pick one to start a film with the director; the live lines build a whole film from a conversation.</p></div></motion.div>
      <div className="styles">
        {HOUSE_STYLES.map((h, i) => (
          <motion.article key={h.id} className="tile glass style-card" {...appear(1 + i * 0.4)} aria-labelledby={`st-${h.id}`}>
            <button className="thumb" onClick={() => play(h)} aria-label={`Play a ${h.name} film`} style={{ border: 0, padding: 0, width: '100%', cursor: 'pointer', display: 'block' }}>
              {h.vertical && <img className="backdrop" src={h.poster} alt="" aria-hidden="true" loading="lazy" />}
              <img className={h.vertical ? 'portrait' : ''} src={h.poster} alt="" loading="lazy" />
              <span className="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m9 6.5 9 5.5-9 5.5z" fill="currentColor" /></svg></span>
              <span className="fmt">{h.formats.join(' or ')}</span>
            </button>
            <div className="body">
              <b id={`st-${h.id}`} style={{ fontSize: 18, fontWeight: 640 }}>{h.name}</b>
              <p>{h.what}</p>
              <div className="tags">
                <span className={'chip' + (h.line ? ' on' : '')}>{h.line ? 'live line' : 'hand-built'}</span>
                <span className="chip">{h.engine}</span>
              </div>
              <p className="faint" style={{ fontSize: 13 }}>Best for: {h.best}</p>
              <div className="acts">
                {h.line && h.formats.map((f) => (
                  <button key={f} className="btn lamp" onClick={() => pick({ line: h.line, format: h.line === 'cutaway' ? f : null, say: `Let's make a ${h.name} film${h.formats.length > 1 ? `, ${f === '9:16' ? 'vertical 9:16' : 'wide 16:9'}` : ''}.` })}>
                    {h.formats.length > 1 ? `Start a film, ${f}` : 'Start a film'}
                  </button>
                ))}
                {!h.line && <span className="faint" style={{ fontSize: 13 }}>{h.why}</span>}
              </div>
            </div>
          </motion.article>
        ))}
      </div>
      <h2 className="sect">Early test looks <span className="faint">short clips from the first style prototypes</span></h2>
      <div className="row">
        {STYLES.map((s, i) => (
          <motion.button key={s.id} className="tile glass" onClick={() => open({ title: s.name, series: 'Style test', format: s.vertical ? '9:16' : '16:9', poster: `/media/${s.media}.jpg`, preview: `/media/${s.media}.mp4` })} {...appear(3 + i * 0.3)} aria-label={`Play the ${s.name} test clip`}>
            <div className="thumb">
              {s.vertical && <img className="backdrop" src={`/media/${s.media}.jpg`} alt="" aria-hidden="true" loading="lazy" />}
              <img className={s.vertical ? 'portrait' : ''} src={`/media/${s.media}.jpg`} alt="" loading="lazy" />
              <span className="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m9 6.5 9 5.5-9 5.5z" fill="currentColor" /></svg></span>
            </div>
            <div className="meta"><b>{s.name}</b><span style={{ display: 'block' }}>{s.motion}</span></div>
          </motion.button>
        ))}
      </div>
    </>
  );
}

// ------------------------------------------------------------------ Renders (live from GitHub)
function Renders() {
  const [runs, setRuns] = useState(null);
  const [err, setErr] = useState(false);
  useEffect(() => {
    const load = () => fetch(`https://api.github.com/repos/${REPO}/actions/runs?per_page=15`).then((r) => r.json()).then((j) => { if (Array.isArray(j.workflow_runs)) { setRuns(j.workflow_runs); setErr(false); } else throw new Error('x'); }).catch(() => { setErr(true); setRuns((r) => r || []); });
    load(); const t = setInterval(load, 30000); return () => clearInterval(t);
  }, []);
  const label = { render: 'Picture render', voice: 'Narration takes', motion: 'Motion learning', smoke: 'Health check', film: 'Studio film build', 'films-render': 'Film render', codead: 'Code-built ad', board: 'Style board', piece: 'Shot factory' };
  const ago = (d) => { const m = Math.max(0, Math.round((Date.now() - new Date(d)) / 60000)); return m < 60 ? `${m} min ago` : m < 1440 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} d ago`; };
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Renders</h1><p className="lede">The studio’s machines at work. This list refreshes on its own.</p></div></motion.div>
      {err && <p className="notice" role="status"><i className="dot bad" />GitHub did not answer just now, so this list may be out of date.</p>}
      <motion.div className="list glass" {...appear(1)}>
        {!runs && <div className="li"><i className="dot run" /><span>Loading</span><span /></div>}
        {runs && !runs.length && <div className="li"><i className="dot" /><span>No runs to show.</span><span /></div>}
        {runs?.map((r) => (
          <a key={r.id} className="li" href={r.html_url} target="_blank" rel="noreferrer">
            <i className={'dot ' + (r.status !== 'completed' ? 'run' : r.conclusion === 'success' ? 'ok' : r.conclusion === 'cancelled' ? '' : 'bad')} />
            <span><b style={{ fontWeight: 600 }}>{label[r.name] || r.name}</b> <span className="faint">· {r.display_title?.slice(0, 70)}</span></span>
            <span className="faint">{r.status !== 'completed' ? 'running' : r.conclusion === 'success' ? 'done' : r.conclusion === 'cancelled' ? 'cancelled' : 'failed'} · {ago(r.updated_at)}</span>
          </a>
        ))}
      </motion.div>
    </>
  );
}

// ------------------------------------------------------------------ Setup: one key at a time
function BuildKey() {
  return (
    <motion.section className="card glass" style={{ marginTop: 18 }} {...appear(3)}>
      <h2>3. The build director (GitHub)</h2>
      <p className="quiet" style={{ margin: '6px 0 0' }}>When you tap “Build this film”, the director plans and writes the film on GitHub’s machines. It needs its own OpenRouter key, with its own spending limit, so builds can never spend more than you allow.</p>
      <ol className="steps">
        <li><div>Open <a href="https://openrouter.ai/settings/keys" target="_blank" rel="noreferrer">openrouter.ai/settings/keys</a>, tap <b>Create key</b>. Name: <code className="copy">KINOFORGE builds</code>. Credit limit: <b>3</b>. Create, then copy the key.</div></li>
        <li><div>Open <a href="https://github.com/Eouchi147/kinoforge/settings/secrets/actions/new" target="_blank" rel="noreferrer">the repo’s new secret page</a>. Name: <code className="copy">OPENROUTER_API_KEY</code>. Secret: paste the key. Tap <b>Add secret</b>.</div></li>
        <li><div>Tell me “builds linked”.</div></li>
      </ol>
    </motion.section>
  );
}

function Spend({ status }) {
  const a = status?.account, c = status?.caps, seats = status?.seats || {}; const n = (id) => (id || 'none').split('/').pop();
  if (!status?.openrouter) return null;
  return (
    <motion.section className="card glass refract" style={{ marginBottom: 18 }} {...appear(1)}>
      <h2>Money</h2>
      {a?.remaining != null && <p className="big" style={{ margin: '4px 0 2px' }}>${a.remaining.toFixed(2)} <span className="faint">left on the studio key (limit ${(a.limit ?? 0).toFixed(2)})</span></p>}
      {a?.remaining != null && a.remaining < 0.5 && <p className="notice" role="status" style={{ margin: '8px 0' }}><i className="dot run" />{a.remaining < 0.05 ? 'The key is out of credit. The director still answers on free models, which are slower and less sharp. Raise the key’s limit on openrouter.ai to get the best models back.' : 'Credit is low. When it runs out the director switches to free models automatically.'}</p>}
      <dl>
        {a?.today != null && <div style={{ display: 'contents' }}><dt>Spent today</dt><dd>${a.today.toFixed(3)} (stops at ${c?.day_usd})</dd></div>}
        <div style={{ display: 'contents' }}><dt>Caps</dt><dd>${c?.turn_usd} per message, ${c?.day_usd} per day; a film build is capped at $1.50 by default</dd></div>
        <div style={{ display: 'contents' }}><dt>Head</dt><dd>{n(seats.head?.[0])}: plans, talks with you, final review</dd></div>
        <div style={{ display: 'contents' }}><dt>Deputy</dt><dd>{n(seats.deputy?.[0])}: reviews every step</dd></div>
        <div style={{ display: 'contents' }}><dt>Crew</dt><dd>{(seats.crew || []).slice(0, 3).map(n).join(', ')}: drafts in parallel</dd></div>
        <div style={{ display: 'contents' }}><dt>Backup</dt><dd>{(seats.free || []).slice(0, 2).map(n).join(', ')} (free)</dd></div>
      </dl>
    </motion.section>
  );
}

function Setup({ status }) {
  const vercelEnv = 'https://vercel.com/samkeamy-7230s-projects/kinoforge-studio/settings/environment-variables';
  const S = ({ ok }) => <span className={'chip' + (ok ? ' on' : '')}><i className={'dot ' + (ok ? 'ok' : '')} />{ok ? 'Connected' : 'Not connected yet'}</span>;
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Setup</h1><p className="lede">The director’s brain, its hands, and what it may spend.</p></div></motion.div>
      <Spend status={status} />
      <motion.section className="card glass refract" style={{ marginBottom: 18 }} {...appear(1)}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}><h2>1. The director’s brain (OpenRouter)</h2><S ok={status?.openrouter} /></div>
        <ol className="steps">
          <li><div>Open <a href="https://openrouter.ai/settings/keys" target="_blank" rel="noreferrer">openrouter.ai/settings/keys</a> and sign in.</div></li>
          <li><div>Tap <b>Create key</b>, name it <code className="copy">KINOFORGE</code>, and copy the key.</div></li>
          <li><div>Open the <a href={vercelEnv} target="_blank" rel="noreferrer">studio’s settings on Vercel</a>, tap <b>Add</b>. Name: <code className="copy">OPENROUTER_API_KEY</code>. Value: paste the key. Tap <b>Save</b>.</div></li>
          <li><div>Tell me “key added” in our chat. I redeploy the studio and the director wakes up.</div></li>
        </ol>
      </motion.section>
      <motion.section className="card glass" {...appear(2)}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}><h2>2. The director’s hands (GitHub)</h2><S ok={status?.github} /></div>
        <p className="quiet" style={{ margin: '6px 0 0' }}>Lets the studio save films and your choices, and start renders.</p>
        <ol className="steps">
          <li><div>Open <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noreferrer">github.com → new token</a>. Name: <code className="copy">KINOFORGE studio</code>. Expiration: <b>90 days</b>.</div></li>
          <li><div>Repository access: <b>Only select repositories</b> → <b>Eouchi147/kinoforge</b>.</div></li>
          <li><div>Permissions → Repository: <b>Contents: Read and write</b> and <b>Actions: Read and write</b>. Tap <b>Generate token</b> and copy it.</div></li>
          <li><div>In the <a href={vercelEnv} target="_blank" rel="noreferrer">studio’s settings on Vercel</a>, add <code className="copy">GITHUB_TOKEN</code> with the token as its value. Save.</div></li>
          <li><div>Tell me “GitHub added”.</div></li>
        </ol>
      </motion.section>
      <BuildKey />
    </>
  );
}
