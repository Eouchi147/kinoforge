'use client';
// Create: every choice is a card you click; the brief (a production slate) fills as you click; the director chat shapes
// the story; Build commits the brief (POST /api/build, unchanged contract plus look and music_piece, which the
// pipeline keeps and ignores for now). The draft lives on this device (localStorage kf-create-1) until it is built.
import { useEffect, useMemo, useRef, useState } from 'react';
import { useOS, smooth } from '../store';
import { Head, Note } from '../ui';
import { Icon } from '../icons';

const KIND = [
  { id: 'film', name: 'Film', sub: 'A story told start to end', img: '/posters/battle-map-agincourt.jpg' },
  { id: 'ad', name: 'Ad', sub: 'A short ad for a business', img: '/looks/reference-470.jpg', note: 'Ad: a short ad for a business; the business name and offer only in its own written words.' },
  { id: 'loop', name: 'Social loop', sub: 'One fixed view, no cuts, seamless', img: '/looks/seasons-base-40.jpg', tall: true, note: 'Social loop: one fixed view, no cuts, a living world, seamless loop (the seasons loop is the base).' },
  { id: 'explainer', name: 'Explainer', sub: 'How or why something works', img: '/looks/reference-830.jpg', note: 'Explainer: one clear question answered, kid-clear.' },
];
const LINES = [
  { id: 'cutaway', name: 'Cutaway', sub: 'A block of land cut open: life on top, layers and finds below', img: '/looks/reference-830.jpg', formats: ['16:9', '9:16'], range: [30, 90], lengths: [30, 45, 60, 90], def: 60 },
  { id: 'battle-map', name: 'Battle Map', sub: 'A 3D relief map, armies, arrows, labels', img: '/posters/battle-map-cannae.jpg', formats: ['16:9'], range: [120, 180], lengths: [120, 150, 180], def: 150 },
  { id: 'kinetic', name: 'Kinetic', sub: 'Words, dates and documents in motion', img: '/posters/dark-corners-bamberg-kinetic.jpg', tall: true, formats: ['9:16'], range: [60, 180], lengths: [60, 90, 120, 180], def: 120 },
];
const VOICES = [
  { id: '', name: 'Series narrator', sub: 'The pipeline default (paid ElevenLabs voice in paid mode, a free open voice in free mode)' },
  { id: 'elevenlabs/eleven-v4|brian', name: 'ElevenLabs Brian', sub: 'Warm, paid voice, checked line by line' },
  { id: 'kokoro|bm_george', name: 'Kokoro George', sub: 'Free open voice on the runner, British' },
];
const CAPS = [1, 2, 3, 5];
const DEF = { what: 'film', line: 'cutaway', format: '9:16', look: '', length: 60, music: 'score', voice: '', cap: 2 };
const STORY = [['title', 'Title'], ['subject', 'Subject'], ['angle', 'Angle'], ['audience', 'Audience'], ['tone', 'Tone']];
const KEY = 'kf-create-1';

const lineOf = (id) => LINES.find((l) => l.id === id) || LINES[0];
function fit(c) {
  const L = lineOf(c.line); const out = { ...c };
  if (!L.formats.includes(out.format)) out.format = L.formats[0];
  const n = Number(out.length);
  out.length = Number.isFinite(n) && n ? Math.min(L.range[1], Math.max(L.range[0], Math.round(n))) : L.def;
  if (out.line !== 'cutaway') out.look = '';
  out.cap = CAPS.includes(Number(out.cap)) ? Number(out.cap) : Math.min(5, Math.max(0.5, Number(out.cap) || 2));
  return out;
}

function Card({ on, onClick, img, tall, name, sub, disabled, children, wide }) {
  return (
    <button type="button" className={'opt-card' + (on ? ' on' : '') + (wide ? ' wide' : '')} aria-pressed={on} onClick={onClick} disabled={disabled}>
      {img !== undefined && <span className="oc-img">{img ? <img src={img} alt="" loading="lazy" className={tall ? 'tall' : ''} /> : children}</span>}
      <span className="oc-txt"><b>{name}</b>{sub && <span>{sub}</span>}</span>
      <span className="oc-tick" aria-hidden="true"><Icon.check size={14} /></span>
    </button>
  );
}

function Step({ n, title, note, children, id }) {
  return (
    <section className="step" aria-labelledby={id}>
      <h2 id={id}><span className="stepn mono">{n}</span>{title}</h2>
      {note && <p className="dim small step-note">{note}</p>}
      {children}
    </section>
  );
}

export function Create() {
  const { route, catalog, status, lock, go } = useOS();
  const [c, setC] = useState(DEF);
  const [brief, setBrief] = useState({});
  const [msgs, setMsgs] = useState([]);
  const [options, setOptions] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const [text, setText] = useState('');
  const [fallback, setFallback] = useState(null);
  const [building, setBuilding] = useState(false);
  const [buildErr, setBuildErr] = useState(null);
  const [loaded, setLoaded] = useState(false);
  const [playing, setPlaying] = useState(null);
  const thread = useRef(null);
  const audio = useRef(null);

  // the draft on this device, then any preset in the route (#/create?line=cutaway&look=fable)
  useEffect(() => {
    try { const s = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s) { setC(fit({ ...DEF, ...s.c })); setBrief(s.brief || {}); setMsgs(s.msgs || []); setOptions(s.options || []); setFallback(s.fallback || null); } } catch {}
    setLoaded(true);
  }, []);
  const qs = JSON.stringify(route.query);
  useEffect(() => {
    if (!loaded) return;
    const q = route.query; if (!Object.keys(q).length) return;
    setC((prev) => fit({ ...prev, ...(q.what ? { what: q.what } : {}), ...(q.line ? { line: q.line } : q.look ? { line: 'cutaway' } : {}), ...(q.format ? { format: q.format } : {}),
      ...(q.look ? { look: q.look === 'reference' ? '' : ((catalog?.looks || []).find((l) => l.id === q.look || l.key === q.look)?.key || q.look) } : {}), ...(q.length ? { length: Number(q.length) } : {}), ...(q.cap ? { cap: Number(q.cap) } : {}), ...(q.music ? { music: q.music } : {}) }));
    go('create', { replace: true });
  }, [qs, loaded]);
  useEffect(() => { if (loaded) try { localStorage.setItem(KEY, JSON.stringify({ c, brief: { ...brief, line: c.line, format: c.format, target_seconds: c.length }, msgs, options, fallback })); } catch {} }, [c, brief, msgs, options, fallback, loaded]);
  useEffect(() => { thread.current?.scrollTo({ top: 1e6, behavior: smooth() }); }, [msgs, busy]);

  const set = (k, v) => setC((p) => fit({ ...p, [k]: v }));
  const L = lineOf(c.line);
  const looks = (catalog?.looks || []).filter((l) => !l.start || l.start.line === 'cutaway');   // looks the Blender line can render
  const music = catalog?.music || [];
  const look = looks.find((l) => l.key === c.look);
  const piece = music.find((m) => m.id === c.music);
  const kind = KIND.find((k) => k.id === c.what) || KIND[0];
  const connected = status?.openrouter;
  const locked = lock?.required && !lock?.unlocked;
  const missing = STORY.filter(([k]) => !String(brief[k] || '').trim()).map(([, l]) => l.toLowerCase());
  const ready = !missing.length;

  const choiceWords = () => [
    `Let's make a ${L.name} ${kind.name.toLowerCase()}, ${c.format}, about ${c.length} seconds`,
    look ? `, in the ${look.name} look` : '',
    c.music === 'none' ? ', no music' : piece ? `, music: ${piece.title}` : '',
    '. Propose a subject and an angle.',
  ].join('');

  async function send(content) {
    const next = content ? [...msgs, { role: 'user', content }] : msgs;
    if (content) setMsgs(next);
    setText(''); setOptions([]); setBusy(true); setErr(null);
    const prior = { title: null, subject: null, angle: null, audience: null, tone: null, notes: null, ...brief, line: c.line, format: c.line === 'cutaway' ? c.format : null, target_seconds: c.length };
    try {
      const r = await fetch('/api/director', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: next.map(({ role, content: x }) => ({ role, content: x })), brief: prior }) });
      const j = await r.json().catch(() => ({ error: 'The reply could not be read.' }));
      if (!r.ok) throw Object.assign(new Error(j.error), { code: j.code });
      setMsgs([...next, { role: 'assistant', content: j.say, by: j.director }]); setOptions(j.options || []);
      const b = j.brief || {};
      setBrief((p) => ({ ...p, ...Object.fromEntries(['title', 'subject', 'angle', 'audience', 'tone', 'notes'].filter((k) => b[k]).map((k) => [k, b[k]])) }));
      if (b.line && b.line !== c.line) setC((p) => fit({ ...p, line: b.line, format: b.format || p.format }));
      else if (b.target_seconds && b.target_seconds !== c.length) setC((p) => fit({ ...p, length: b.target_seconds }));
      setFallback(j.director?.fallback ? j.director.note : null);
    } catch (e) {
      setErr(e.code === 'locked' ? 'The studio is locked. Unlock it in Settings to talk to the director.' : e.code === 'credits' ? 'The studio key is out of credit and no free model could answer. Try again in a minute, or add credit on openrouter.ai.' : e.code === 'no-key' ? 'The director is not connected (Settings).' : 'No model answered just now. Send your message again in a minute.');
    }
    setBusy(false);
  }

  async function build() {
    setBuilding(true); setBuildErr(null);
    const notes = [kind.note, brief.notes].filter(Boolean).join(' ');
    const out = {
      title: brief.title, subject: brief.subject, angle: brief.angle, audience: brief.audience, tone: brief.tone, notes: notes || undefined,
      line: c.line, format: c.format, target_seconds: c.length, cap_usd: c.cap, voice: c.voice || undefined,
      look: c.line === 'cutaway' && c.look ? c.look : undefined, music_piece: c.music === 'score' ? undefined : c.music,
    };
    try {
      const r = await fetch('/api/build', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ brief: out }) });
      const j = await r.json();
      if (!j.saved) throw new Error(j.code === 'no-github' ? 'GitHub is not connected, so the studio cannot start builds. Connect it in Settings.' : j.code === 'locked' ? 'The studio is locked. Unlock it in Settings, then tap Build again.' : j.error || 'The build could not be started.');
      try { localStorage.setItem('kf-job', j.id); localStorage.removeItem(KEY); } catch {}
      go(`jobs/${j.id}`);
    } catch (e) { setBuildErr(e.message); }
    setBuilding(false);
  }

  const reset = () => { setC(DEF); setBrief({}); setMsgs([]); setOptions([]); setErr(null); setFallback(null); setBuildErr(null); try { localStorage.removeItem(KEY); } catch {} };
  const listen = (m) => {
    const a = audio.current; if (!a) return;
    if (playing === m.id) { a.pause(); setPlaying(null); return; }
    a.src = m.url; a.play().then(() => setPlaying(m.id)).catch(() => setPlaying(null));
  };

  const slate = [
    ['What', kind.name], ['Line', L.name], ['Look', c.line === 'cutaway' ? (look ? look.name : 'Reference') : 'not used'], ['Format', c.format], ['Length', `${c.length} s`],
    ['Music', c.music === 'none' ? 'None' : piece ? piece.title : 'Free score'], ['Voice', (VOICES.find((v) => v.id === c.voice) || VOICES[0]).name], ['Money cap', `$${c.cap.toFixed(2)}`],
  ];
  const filled = slate.length + STORY.filter(([k]) => brief[k]).length, total = slate.length + STORY.length;

  return (
    <div className="app create">
      <Head title="Create" lede="Click your choices and the brief fills as you go. Then shape the story with the director, and build.">
        <button className="btn" onClick={reset}>Start over</button>
      </Head>
      <div className="create-grid">
        <div className="steps-col">
          <Step n="1" title="What are we making" id="s-what">
            <div className="cards c4">{KIND.map((k) => <Card key={k.id} on={c.what === k.id} onClick={() => setC((p) => fit({ ...p, what: k.id, ...(k.id === 'loop' ? { line: 'cutaway', format: '9:16', length: 30 } : {}) }))} img={k.img} tall={k.tall} name={k.name} sub={k.sub} />)}</div>
          </Step>
          <Step n="2" title="Production line" id="s-line" note="Hand-built styles (Lantern Road, Clay, NOOR) are made by an agent, not by this builder: ask for one in chat.">
            <div className="cards c3">{LINES.map((l) => <Card key={l.id} on={c.line === l.id} onClick={() => set('line', l.id)} img={l.img} tall={l.tall} name={l.name} sub={l.sub} />)}</div>
          </Step>
          {c.line === 'cutaway' && (
            <Step n="3" title="Cutaway look" id="s-look" note="The look is written into the brief. The automatic build still renders the reference look until the pipeline reads it; an agent can render the chosen look from the brief.">
              <div className="cards looks">
                <Card on={!c.look} onClick={() => set('look', '')} img="/looks/reference-470.jpg" name="Reference" sub="Golden light, fog, the kit as built" />
                {looks.map((l) => <Card key={l.id} on={c.look === l.key} onClick={() => set('look', l.key)} img={l.cover || null} name={l.name} sub={l.summary}>{l.name}</Card>)}
              </div>
              <p className="small"><a href={look ? `#/styles/${look.id}` : '#/styles/looks'}>{look ? `See the ${look.name} board` : 'See every look board'}</a></p>
            </Step>
          )}
          <Step n={c.line === 'cutaway' ? '4' : '3'} title="Format" id="s-format">
            <div className="cards c2">
              {['16:9', '9:16'].map((f) => (
                <Card key={f} on={c.format === f} onClick={() => set('format', f)} disabled={!L.formats.includes(f)} img={null} name={f === '16:9' ? '16:9 wide' : '9:16 vertical'} sub={f === '16:9' ? 'YouTube, screens' : 'Shorts, Reels, TikTok'}>
                  <span className={'frame ' + (f === '9:16' ? 'v' : 'h')} aria-hidden="true" />
                </Card>
              ))}
            </div>
            {L.formats.length === 1 && <p className="dim small">{L.name} is made in {L.formats[0]} only.</p>}
          </Step>
          <Step n={c.line === 'cutaway' ? '5' : '4'} title="Length" id="s-length" note={c.line === 'cutaway' ? 'Cutaway renders for hours on free machines: shorter is faster.' : null}>
            <div className="cards c4 small-cards">{L.lengths.map((s) => <Card key={s} on={c.length === s} onClick={() => set('length', s)} name={s < 60 ? `${s} s` : `${Math.floor(s / 60)} min${s % 60 ? ` ${s % 60} s` : ''}`} sub={s === L.def ? 'usual' : null} />)}</div>
          </Step>
          <Step n={c.line === 'cutaway' ? '6' : '5'} title="Music" id="s-music" note="The automatic build scores every film with the free score engine. A chosen public-domain piece or no music is written into the brief for the finishing step.">
            <div className="cards c3">
              <Card on={c.music === 'score'} onClick={() => set('music', 'score')} name="Free score" sub="Made in code for this film, US$0" />
              {music.map((m) => (
                <div key={m.id} className="card-with-action">
                  <Card on={c.music === m.id} onClick={() => set('music', m.id)} name={m.title} sub={m.licence} />
                  {m.url && <button type="button" className="linkbtn small" onClick={() => listen(m)} aria-pressed={playing === m.id}>{playing === m.id ? 'Stop' : 'Listen'}</button>}
                </div>
              ))}
              <Card on={c.music === 'none'} onClick={() => set('music', 'none')} name="No music" sub="Voice and sound only" />
            </div>
            <audio ref={audio} onEnded={() => setPlaying(null)} preload="none" />
          </Step>
          <Step n={c.line === 'cutaway' ? '7' : '6'} title="Voice" id="s-voice">
            <div className="cards c3">{VOICES.map((v) => <Card key={v.id || 'def'} on={c.voice === v.id} onClick={() => set('voice', v.id)} name={v.name} sub={v.sub} />)}</div>
          </Step>
          <Step n={c.line === 'cutaway' ? '8' : '7'} title="Money cap for this film" id="s-cap" note="Every paid call is booked against the cap before it is made. A film that cannot pass the fact check and the picture checks inside the cap stops, and nothing is rendered.">
            <div className="cards c4 small-cards">{CAPS.map((n) => <Card key={n} on={c.cap === n} onClick={() => set('cap', n)} name={`$${n}`} sub={n === 2 ? 'usual' : n === 1 ? 'tight' : null} />)}</div>
          </Step>

          <section className="step story" aria-labelledby="s-story">
            <h2 id="s-story"><span className="stepn mono">{c.line === 'cutaway' ? '9' : '8'}</span>The story, with the director</h2>
            <div className="convo">
              <div className="thread" ref={thread} aria-live="polite">
                {!msgs.length && (
                  <div className="msg ai">{connected ? 'Tell me the subject, or let me propose one from your choices.' : status ? 'The director is not connected (Settings). You can still write the story fields in the brief yourself.' : 'Checking the director'}</div>
                )}
                {msgs.map((m, i) => <div key={i} className={'msg ' + (m.role === 'user' ? 'me' : 'ai')}>{m.content}</div>)}
                {busy && <div className="msg ai thinking" role="status" aria-label="The director is thinking"><i /><i /><i /></div>}
                {err && <div className="msg ai" role="alert">{err}</div>}
                {!busy && !!options.length && <div className="options">{options.map((o) => <button key={o} className="optchip" onClick={() => send(o)}>{o}</button>)}</div>}
                {!busy && !msgs.length && connected && <div className="options"><button className="optchip strong" onClick={() => send(choiceWords())}>Propose a subject from my choices</button></div>}
              </div>
              {fallback && <Note tone="warn">{fallback}</Note>}
              <form className="composer" onSubmit={(e) => { e.preventDefault(); if (text.trim()) send(text.trim()); }}>
                <label className="sr" htmlFor="say">Message to the director</label>
                <textarea id="say" rows={1} value={text} placeholder={connected ? (locked ? 'Unlock the studio in Settings to talk' : 'Name a subject, or reply') : 'The director is not connected'} disabled={!connected || busy || locked}
                  onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (text.trim()) send(text.trim()); } }} />
                <button className="btn primary icon" disabled={!connected || busy || !text.trim() || locked} aria-label="Send"><Icon.send size={18} /></button>
              </form>
            </div>
          </section>
        </div>

        <aside className="slate-col" id="brief">
          <div className="slate">
            <div className="slate-stripes" aria-hidden="true" />
            <div className="slate-head"><h2>The brief</h2><span className="mono dim">{filled} of {total}</span></div>
            <dl className="slate-rows">
              {slate.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}
            </dl>
            <div className="slate-story">
              {STORY.map(([k, l]) => (
                <label key={k} className="sfield">
                  <span>{l}</span>
                  {k === 'title' ? <input value={brief[k] || ''} onChange={(e) => setBrief((p) => ({ ...p, [k]: e.target.value }))} placeholder="not decided yet" maxLength={90} />
                    : <textarea rows={k === 'subject' || k === 'angle' ? 2 : 1} value={brief[k] || ''} onChange={(e) => setBrief((p) => ({ ...p, [k]: e.target.value }))} placeholder="not decided yet" maxLength={600} />}
                </label>
              ))}
              {brief.notes && <p className="small dim">Notes from the chat: {brief.notes}</p>}
            </div>
            <div className="slate-build">
              <button className="btn primary block" disabled={!ready || building || locked} onClick={build}>{building ? 'Starting the build' : 'Build this film'}</button>
              <p className="small dim">{locked ? 'The studio is locked: unlock it in Settings to build.' : ready ? `Runs on GitHub's machines inside the $${c.cap.toFixed(2)} cap. Nothing is published without you.` : `Still needed: ${missing.join(', ')}.`}</p>
              {buildErr && <Note tone="bad" role="alert">{buildErr}</Note>}
            </div>
          </div>
        </aside>
      </div>
      <button type="button" className="brief-peek" onClick={() => { const b = document.getElementById('brief'); b?.scrollIntoView({ behavior: smooth() }); b?.querySelector('input, textarea, button')?.focus({ preventScroll: true }); }}>
        <span>Brief</span><span className="mono">{filled} of {total}</span><span>{ready ? 'Ready to build' : 'See it'}</span>
      </button>
    </div>
  );
}
