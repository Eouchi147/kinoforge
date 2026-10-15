'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion, LayoutGroup } from 'framer-motion';
import { FILMS, STYLES, STAGES, BUILD_GATES, REPO } from '@/lib/data';

const ease = [0.22, 1, 0.36, 1];

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
const TABS = [['director', 'Director'], ['films', 'Films'], ['styles', 'Styles'], ['voices', 'Voices'], ['renders', 'Renders'], ['setup', 'Setup']];

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

const appear = (i = 0) => ({ initial: { opacity: 0, y: 14, filter: 'blur(8px)' }, animate: { opacity: 1, y: 0, filter: 'blur(0px)' }, transition: { duration: 0.9, delay: 0.25 + i * 0.08, ease } });

export default function Studio() {
  useLamp();
  const [tab, setTab] = useState('director');
  const [status, setStatus] = useState(null);
  const [player, setPlayer] = useState(null);
  useEffect(() => { fetch('/api/status').then((r) => r.json()).then(setStatus).catch(() => setStatus({ openrouter: false, github: false })); }, []);
  useEffect(() => { const sync = () => { const h = location.hash.slice(1); if (TABS.some(([k]) => k === h)) setTab(h); }; sync(); addEventListener('hashchange', sync); return () => removeEventListener('hashchange', sync); }, []);
  const go = (k) => { setTab(k); history.replaceState(null, '', '#' + k); window.scrollTo({ top: 0, behavior: 'smooth' }); };

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
              <button key={k} className="navbtn" aria-current={tab === k ? 'page' : undefined} onClick={() => go(k)}>
                {tab === k && <motion.i layoutId="pill" className="navpill" transition={{ type: 'spring', stiffness: 420, damping: 34 }} />}
                {I[k]}<span>{label}</span>
              </button>
            ))}
          </LayoutGroup>
          <div className="spacer" />
        </motion.nav>
        <main className="main">
          <AnimatePresence mode="wait">
            <motion.div key={tab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.45, ease }}>
              {tab === 'director' && <Director status={status} go={go} />}
              {tab === 'films' && <Films open={setPlayer} />}
              {tab === 'styles' && <Styles open={setPlayer} />}
              {tab === 'voices' && <Voices status={status} />}
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
function Director({ status, go }) {
  const [msgs, setMsgs] = useState([]);
  const [brief, setBrief] = useState(null);
  const [options, setOptions] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const [text, setText] = useState('');
  const [ready, setReady] = useState(false);
  const [saved, setSaved] = useState(null);
  const thread = useRef(null);
  const connected = status?.openrouter;

  useEffect(() => { try { const s = JSON.parse(localStorage.getItem('kf-director') || 'null'); if (s) { setMsgs(s.msgs || []); setBrief(s.brief || null); setOptions(s.options || []); } } catch {} }, []);
  useEffect(() => { try { localStorage.setItem('kf-director', JSON.stringify({ msgs, brief, options })); } catch {} }, [msgs, brief, options]);
  useEffect(() => { thread.current?.scrollTo({ top: 1e6, behavior: 'smooth' }); }, [msgs, busy]);
  useEffect(() => { if (connected && !msgs.length && !busy) send(null); }, [connected]);   // the director opens the conversation

  async function send(content) {
    const next = content ? [...msgs, { role: 'user', content }] : msgs;
    if (content) setMsgs(next);
    setText(''); setOptions([]); setBusy(true); setErr(null);
    try {
      const r = await fetch('/api/director', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: next, brief }) });
      const j = await r.json();
      if (!r.ok) throw Object.assign(new Error(j.error), { code: j.code });
      setMsgs([...next, { role: 'assistant', content: j.say, step: j.step_for_sam, by: j.director }]); setOptions(j.options || []); setBrief(j.brief); setReady(Boolean(j.ready));
    } catch (e) { setErr(e.code === 'credits' ? 'Your OpenRouter key has reached its spending limit. Raise it on openrouter.ai under Settings, Keys.' : e.code === 'no-key' ? null : 'Every model in the director’s chain failed just now. Send your message again in a minute.'); }
    setBusy(false);
  }
  async function build() {
    const r = await fetch('/api/film', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ brief, transcript: msgs }) });
    const j = await r.json(); setSaved(j.saved ? `Saved as films/${j.id}. The build agent picks it up from here.` : j.code === 'no-github' ? 'Connect GitHub on the Setup page so the studio can save and build films.' : j.error);
  }
  const lastStep = [...msgs].reverse().find((m) => m.step && / /.test(m.step) && m.step.length > 15)?.step;   // only real sentences, never internal tokens
  const nextForSam = !status ? 'Checking the studio…' : !status.openrouter ? 'Connect the director’s brain: add your OpenRouter key (Setup, 4 short steps).' : saved ? saved : ready ? 'The story is ready. Tap “Build this film”.' : lastStep || 'Talk with the director. Tap an answer or type your own.';

  return (
    <>
      <motion.div className="page-head" {...appear(0)}>
        <div><h1>What are we making?</h1><p className="lede">Talk it through with the director. When the story is right, it builds the film and tells you exactly what it needs from you.</p></div>
      </motion.div>
      <div className="director">
        <motion.section className="convo glass refract" {...appear(1)} aria-label="Conversation with the director">
          <div className="thread" ref={thread} aria-live="polite">
            {!connected && status && (
              <div className="msg ai">I’m the studio’s director. I need my brain connected before we talk: it takes four short steps on the Setup page, and I’ll be ready the moment you finish.</div>
            )}
            {msgs.map((m, i) => (
              <motion.div key={i} className={'msg ' + (m.role === 'user' ? 'me' : 'ai')} initial={{ opacity: 0, y: 8, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.4, ease }}>{m.content}</motion.div>
            ))}
            {busy && <div className="msg ai thinking" aria-label="The director is thinking"><i /><i /><i /></div>}
            {err && <div className="msg ai" role="alert">{err}</div>}
            {!!options.length && !busy && (
              <div className="options">{options.map((o) => <button key={o} className="opt" onClick={() => send(o)}>{o}</button>)}</div>
            )}
          </div>
          <form className="composer" onSubmit={(e) => { e.preventDefault(); if (text.trim()) send(text.trim()); }}>
            <textarea rows={1} value={text} placeholder={connected ? 'Describe the film, or answer the director…' : 'Connect the director on the Setup page first'} disabled={!connected || busy}
              onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (text.trim()) send(text.trim()); } }} aria-label="Message" />
            <button className="btn lamp" disabled={!connected || busy || !text.trim()} aria-label="Send">{I.send}</button>
          </form>
        </motion.section>
        <aside className="side">
          <motion.div className="next glass" {...appear(2)}>
            <div className="label">Your next step</div>
            <p>{nextForSam}</p>
            {status && !status.openrouter && <button className="btn lamp" onClick={() => go('setup')}>Open Setup</button>}
            {ready && !saved && <button className="btn lamp" onClick={build}>Build this film</button>}
          </motion.div>
          <motion.div className="card brief glass" {...appear(3)}>
            <h2>The film so far</h2>
            <dl>
              {[['Title', brief?.title], ['Channel', brief?.channel === 'dark-corners' ? 'Dark Corners' : brief?.channel === 'family' ? 'Family' : null], ['Style', brief?.style],
                ['Length', brief?.length_seconds ? `${Math.round(brief.length_seconds)} s, ${brief.format || '16:9'}` : null], ['Story', brief?.logline], ['Narrator', brief?.narrator], ['Ending', brief?.moral]].map(([k, v]) => (
                <div key={k} style={{ display: 'contents' }}><dt>{k}</dt><dd className={v ? '' : 'empty'}>{v || 'not decided yet'}</dd></div>
              ))}
            </dl>
            {!!msgs.length && <button className="btn ghost" style={{ marginTop: 16 }} onClick={() => { setMsgs([]); setBrief(null); setOptions([]); setReady(false); setSaved(null); }}>Start a new film</button>}
          </motion.div>
          {(() => { const by = [...msgs].reverse().find((m) => m.by)?.by; const a = status?.account;
            return status?.openrouter && (
              <p className="faint" style={{ margin: '0 6px' }}>
                {by ? <>Last answer: {by.head}{by.crew?.length ? <>, with {by.crew.length} crew drafts</> : null}, {(by.ms / 1000).toFixed(0)} s, ${by.usd.toFixed(3)}.{by.note ? <> {by.note}</> : null}</> : <>Director: {(status.seats?.head?.[0] || '').split('/').pop()}. Crew: {(status.seats?.crew || []).slice(0, 3).map((m) => m.split('/').pop()).join(', ')}.</>}
                {a?.remaining != null && <> ${a.remaining.toFixed(2)} left on your key.</>}
              </p>); })()}
        </aside>
      </div>
    </>
  );
}

// ------------------------------------------------------------------ Films
function Stages({ stage }) {
  return <div className="stages" aria-label={`Stage: ${STAGES[stage]}`}>{STAGES.map((s, i) => <i key={s} className={i < stage ? 'done' : i === stage ? 'now' : ''} title={s} />)}</div>;
}
function Films({ open }) {
  const [lead, ...rest] = FILMS;
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Films</h1><p className="lede">Every film the studio has made, where it stands, and what it is waiting for.</p></div></motion.div>
      <motion.article className="hero glass" {...appear(1)}>
        <div className="screen"><video src={`/media/${lead.media}.mp4`} poster={`/media/${lead.media}.jpg`} muted loop playsInline autoPlay preload="metadata" /></div>
        <div className="info">
          <h2 style={{ fontSize: 28, lineHeight: 1.1 }}>{lead.title}</h2>
          <p className="quiet" style={{ margin: 0 }}>{lead.logline}</p>
          <Stages stage={lead.stage} />
          <p className="faint" style={{ margin: 0 }}>{lead.style} · {lead.length} · {lead.status}</p>
          {lead.next && <p style={{ margin: 0 }}><b style={{ color: 'var(--lamp)' }}>Next:</b> {lead.next}</p>}
          <div><button className="btn lamp" onClick={() => open({ title: lead.title, media: lead.media })}>Watch with sound</button></div>
        </div>
      </motion.article>
      <div className="row">
        {rest.map((f, i) => (
          <motion.button key={f.id} className="tile glass" onClick={() => open({ title: f.title, media: f.media })} {...appear(2 + i)}>
            <div className="thumb" style={f.format === '9:16' ? { aspectRatio: '16 / 9' } : null}><img src={`/media/${f.media}.jpg`} alt="" style={f.format === '9:16' ? { objectFit: 'contain', background: '#050814' } : null} /></div>
            <div className="meta"><b>{f.title}</b><span>{f.status}</span><Stages stage={f.stage} /></div>
          </motion.button>
        ))}
      </div>
    </>
  );
}

// ------------------------------------------------------------------ Styles
function Styles({ open }) {
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Twelve styles, each with its own way of moving</h1><p className="lede">Tap a style to see its test clip. Clay and Paper are being upgraded first; the rest follow.</p></div></motion.div>
      <div className="row">
        {STYLES.map((s, i) => (
          <motion.button key={s.id} className="tile glass" onClick={() => open({ title: s.name, media: s.media })} {...appear(1 + i * 0.5)}>
            <div className="thumb"><img src={`/media/${s.media}.jpg`} alt="" style={s.vertical ? { objectFit: 'contain' } : null} /></div>
            <div className="meta"><b>{s.name}</b><span>{s.motion}</span><div className="faint" style={{ marginTop: 6 }}>{s.renderer} · {s.phase}</div></div>
          </motion.button>
        ))}
      </div>
    </>
  );
}

// ------------------------------------------------------------------ Voices (Gate A)
function Voices({ status }) {
  const [data, setData] = useState(null);
  const [saved, setSaved] = useState({});
  useEffect(() => { fetch('/data/voices.json').then((r) => r.json()).then(setData).catch(() => setData({ films: [] })); }, []);
  async function choose(film, take) {
    const r = await fetch('/api/decision', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic: `narrator-${film}`, choice: take }) });
    const j = await r.json(); setSaved({ ...saved, [film]: j.saved ? `Saved: ${take}` : 'Connect GitHub on the Setup page so your choice is saved.' });
  }
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Narrators</h1><p className="lede">Each line was generated several times and checked: no repeated or missing words, no odd pauses, steady pace. Listen, then choose the one that fits.</p></div></motion.div>
      {!data?.films?.length && <motion.div className="card glass" {...appear(1)}><h2>The new takes are being recorded</h2><p className="quiet">The studio is directing the narrator line by line on GitHub’s machines. The finished versions appear here, ready to compare.</p></motion.div>}
      {data?.films?.map((f, fi) => (
        <motion.section key={f.id} className="card glass" style={{ marginBottom: 18 }} {...appear(1 + fi)}>
          <h2>{f.title}</h2><p className="faint" style={{ margin: '0 0 12px' }}>{f.note}</p>
          <div className="row" style={{ marginTop: 0 }}>
            {f.takes.map((t) => (
              <div key={t.id} className="card" style={{ background: 'rgba(255,255,255,.05)', border: '1px solid var(--edge)' }}>
                <b>{t.name}</b><p className="faint" style={{ margin: '4px 0 10px' }}>{t.summary}</p>
                <audio controls preload="none" src={t.src} />
                <button className="btn ghost" style={{ marginTop: 10 }} onClick={() => choose(f.id, t.id)}>Use this narrator</button>
              </div>
            ))}
          </div>
          {saved[f.id] && <p className="faint" role="status">{saved[f.id]}</p>}
        </motion.section>
      ))}
    </>
  );
}

// ------------------------------------------------------------------ Renders (live from GitHub)
function Renders() {
  const [runs, setRuns] = useState(null);
  useEffect(() => {
    const load = () => fetch(`https://api.github.com/repos/${REPO}/actions/runs?per_page=15`).then((r) => r.json()).then((j) => setRuns(j.workflow_runs || [])).catch(() => setRuns([]));
    load(); const t = setInterval(load, 30000); return () => clearInterval(t);
  }, []);
  const label = { render: 'Picture render', voice: 'Narration takes', motion: 'Motion learning', smoke: 'Health check' };
  const ago = (d) => { const m = Math.round((Date.now() - new Date(d)) / 60000); return m < 60 ? `${m} min ago` : `${Math.round(m / 60)} h ago`; };
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Renders</h1><p className="lede">The studio’s machines at work. This list refreshes on its own.</p></div></motion.div>
      <motion.div className="list glass" {...appear(1)}>
        {!runs && <div className="li"><i className="dot run" /><span>Loading…</span><span /></div>}
        {runs?.map((r) => (
          <a key={r.id} className="li" href={r.html_url} target="_blank" rel="noreferrer">
            <i className={'dot ' + (r.status !== 'completed' ? 'run' : r.conclusion === 'success' ? 'ok' : 'bad')} />
            <span><b style={{ fontWeight: 600 }}>{label[r.name] || r.name}</b> <span className="faint">· {r.display_title?.slice(0, 70)}</span></span>
            <span className="faint">{r.status !== 'completed' ? 'running' : r.conclusion === 'success' ? 'done' : 'failed'} · {ago(r.updated_at)}</span>
          </a>
        ))}
      </motion.div>
      <motion.div className="card glass" style={{ marginTop: 18 }} {...appear(2)}>
        <h2>Building the studio</h2>
        <div className="options" style={{ marginTop: 10 }}>{BUILD_GATES.map((g) => <span key={g.id} className={'chip' + (g.state === 'now' ? ' on' : '')}>{g.name}: {g.what}</span>)}</div>
      </motion.div>
    </>
  );
}

// ------------------------------------------------------------------ Setup: one key at a time
function Setup({ status }) {
  const vercelEnv = 'https://vercel.com/samkeamy-7230s-projects/kinoforge-studio/settings/environment-variables';
  const S = ({ ok }) => <span className={'chip' + (ok ? ' on' : '')}><i className={'dot ' + (ok ? 'ok' : '')} />{ok ? 'Connected' : 'Not connected yet'}</span>;
  return (
    <>
      <motion.div className="page-head" {...appear(0)}><div><h1>Setup</h1><p className="lede">Two keys give the director its brain and its hands. Do the first one now; the second when it asks.</p></div></motion.div>
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
    </>
  );
}

// ------------------------------------------------------------------ player sheet
function Player({ item, close }) {
  useEffect(() => { const k = (e) => e.key === 'Escape' && close(); addEventListener('keydown', k); return () => removeEventListener('keydown', k); }, [close]);
  return (
    <motion.div className="scrim" onClick={close} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div className="sheet glass" role="dialog" aria-label={item.title} onClick={(e) => e.stopPropagation()} initial={{ scale: 0.94, y: 24, opacity: 0 }} animate={{ scale: 1, y: 0, opacity: 1 }} exit={{ scale: 0.97, y: 12, opacity: 0 }} transition={{ duration: 0.5, ease }}>
        <div className="screen"><video src={`/media/${item.media}.mp4`} poster={`/media/${item.media}.jpg`} controls autoPlay playsInline /></div>
        <div className="bar"><h2 style={{ margin: 0 }}>{item.title}</h2><button className="btn ghost" onClick={close}>Close</button></div>
      </motion.div>
    </motion.div>
  );
}
