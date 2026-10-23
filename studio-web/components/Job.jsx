'use client';
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { appear, mins } from './ui';

// The pipeline's stages in order (films/director/status.py): status.stages[key] = { state, usd, started_at, ended_at }.
const STAGES = [
  ['script', 'Script and fact check'], ['sound', 'Narration and music'], ['spec', 'Picture plan'], ['check', 'Checks'],
  ['eyes', 'Review by eye'], ['render', 'Render'], ['reflect', 'Lessons'], ['done', 'Done'],
];
const state = (st) => String(st?.state ?? '').toLowerCase();
const usd = (n) => (Number.isFinite(Number(n)) ? `$${Number(n).toFixed(2)}` : null);
// One row: ok, run, bad or wait, from status.stages with the current stage as a fallback.
function rowState(st, key, idx, curIdx) {
  const s = state(st?.stages?.[key]);
  if (key === 'done') return state(st) === 'done' && st?.stage === 'done' ? 'ok' : 'wait';
  if (/^(done|skipped)$/.test(s)) return 'ok';
  if (s === 'failed') return 'bad';
  if (s === 'running') return 'run';
  if (!st?.stages && idx < curIdx) return 'ok';
  if (idx === curIdx && !/^(queued|)$/.test(state(st)) && !s) return state(st) === 'failed' ? 'bad' : 'run';
  return s === 'queued' ? 'queued' : 'wait';
}

export function Job({ id, onWatch, goDirector }) {
  const [j, setJ] = useState(null);
  const [err, setErr] = useState(null);
  const stop = useRef(false);
  useEffect(() => {
    stop.current = false; setJ(null); setErr(null);
    let t;
    const tick = async () => {
      try {
        const r = await fetch(`/api/job?id=${encodeURIComponent(id)}`, { cache: 'no-store' });
        const d = await r.json();
        if (!r.ok) throw new Error(d.error || 'The job could not be read.');
        setJ(d); setErr(null);
        const s = state(d.status);
        if ((d.status?.stage === 'done' && s === 'done') || s === 'failed' || d.run?.conclusion === 'failure') return;   // finished: stop polling
      } catch (e) { setErr(e.message); }
      if (!stop.current) t = setTimeout(tick, 6000);
    };
    tick();
    return () => { stop.current = true; clearTimeout(t); };
  }, [id]);

  const st = j?.status, s = state(st);
  const failed = s === 'failed' || (!st && j?.run?.conclusion && j.run.conclusion !== 'success');
  const done = st?.stage === 'done' && s === 'done';
  const curIdx = Math.max(0, STAGES.findIndex(([k]) => k === st?.stage));
  const cap = st?.cap_usd ?? j?.brief?.cap_usd;
  const brief = j?.brief;
  const runUrl = st?.run_url || j?.run?.url;
  const fmt = brief?.line === 'kinetic' ? '9:16' : brief?.line === 'cutaway' && brief?.format === '9:16' ? '9:16' : '16:9';
  const series = { kinetic: 'Kinetic', cutaway: 'Cutaway' }[brief?.line] || 'Battle Map';
  const film = j?.film && done ? { id, title: brief?.title || id, series, subject: brief?.subject, format: fmt, duration: brief?.target_seconds, ...j.film } : null;
  const waiting = !st;
  return (
    <>
      <motion.div className="page-head" {...appear(0)}>
        <div>
          <h1>{brief?.title || id}</h1>
          <p className="lede">{done ? 'Your film is ready.' : failed ? 'The build stopped.' : waiting ? 'The build is starting on GitHub’s machines.' : 'Building on GitHub’s machines. You can close this page; it picks up where it was.'}</p>
        </div>
        <button className="btn ghost" onClick={goDirector}>Back to the director</button>
      </motion.div>
      <div className="director">
        <motion.section className="card glass refract" {...appear(1)} aria-label="Build progress" aria-live="polite">
          <ol className="pipeline">
            {STAGES.map(([k, label], i) => {
              const status = rowState(st, k, i, curIdx);
              return <li key={k} className={status}><i className={'dot ' + (status === 'wait' || status === 'queued' ? '' : status)} /><span>{label}</span>{status === 'run' && <em>working</em>}{status === 'queued' && <em>queued</em>}</li>;
            })}
          </ol>
          <p className="msg ai" style={{ marginTop: 18 }} role="status">
            {err && !j ? err : failed ? (st?.message || 'The run failed before the film was finished.') : done ? (st?.message || 'Finished and published to the library.') : st?.message || (j?.run ? 'GitHub has accepted the job and is starting a runner.' : 'Waiting for GitHub to pick up the brief. This usually takes under a minute.')}
          </p>
          {runUrl && <p style={{ margin: '12px 0 0' }}><a href={runUrl} target="_blank" rel="noreferrer">Open the run on GitHub</a></p>}
          {film && (
            <div style={{ marginTop: 18 }}>
              <div className={'jobposter' + (film.format === '9:16' ? ' tall' : '')}>
                <img src={film.poster} alt="" onError={(e) => { e.currentTarget.src = film.sheet; }} />
                <button className="btn lamp" onClick={() => onWatch(film)}>Watch the film</button>
              </div>
            </div>
          )}
        </motion.section>
        <aside className="side">
          <motion.div className="card glass" {...appear(2)}>
            <h2>Money</h2>
            <p className="big">{usd(st?.usd) || '$0.00'}{cap != null && <span className="faint"> of {usd(cap)} cap</span>}</p>
            <div className="meter" aria-hidden="true"><i style={{ width: `${Math.min(100, cap ? (Number(st?.usd || 0) / cap) * 100 : 0)}%` }} /></div>
            <p className="faint" style={{ margin: '10px 0 0' }}>Every paid call is booked against the cap. The build stops before it passes it.</p>
          </motion.div>
          {brief && (
            <motion.div className="card brief glass" {...appear(3)}>
              <h2>The brief</h2>
              <dl>
                {[['Line', `${{ kinetic: 'Kinetic', cutaway: 'Cutaway' }[brief.line] || 'Battle Map'}, ${brief.line === 'kinetic' ? '9:16' : brief.line === 'cutaway' && brief.format === '9:16' ? '9:16' : '16:9'}`], ['Subject', brief.subject], ['Angle', brief.angle], ['Audience', brief.audience], ['Tone', brief.tone], ['Length', brief.target_seconds ? mins(brief.target_seconds) : null]].map(([k, v]) => v && <div key={k} style={{ display: 'contents' }}><dt>{k}</dt><dd>{v}</dd></div>)}
              </dl>
            </motion.div>
          )}
        </aside>
      </div>
    </>
  );
}
