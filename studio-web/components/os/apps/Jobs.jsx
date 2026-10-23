'use client';
// Jobs: studio builds (films/studio/<id>/, the director pipeline) with their stages and spend, and the render runs on
// GitHub Actions (Eouchi147/rc-render and Eouchi147/kinoforge). A job page follows one build live (GET /api/job).
import { useEffect, useRef, useState } from 'react';
import { useOS, useFetch, ago, usd } from '../store';
import { Head, Panel, Empty, Note, Led, Seg } from '../ui';
import { Icon } from '../icons';
import { runState } from './Desk';
import { clock } from '@/lib/catalog.mjs';

export const STAGES = [
  ['script', 'Script and fact check'], ['sound', 'Narration and music'], ['spec', 'Picture plan'], ['check', 'Checks'],
  ['eyes', 'Review by eye'], ['render', 'Render'], ['reflect', 'Lessons'], ['done', 'Done'],
];
const st = (x) => String(x?.state ?? x ?? '').toLowerCase();
function rowState(s, key, idx, curIdx) {
  const v = st(s?.stages?.[key]);
  if (key === 'done') return st(s) === 'done' && s?.stage === 'done' ? 'ok' : '';
  if (/^(done|skipped)$/.test(v)) return 'ok';
  if (v === 'failed') return 'bad';
  if (v === 'running') return 'run';
  if (!s?.stages && idx < curIdx) return 'ok';
  if (idx === curIdx && !/^(queued|)$/.test(st(s)) && !v) return st(s) === 'failed' ? 'bad' : 'run';
  return '';
}
const LINE = { cutaway: 'Cutaway', 'battle-map': 'Battle Map', kinetic: 'Kinetic' };
const stale = (j) => !j.updated || Date.now() - new Date(j.updated) > 2 * 3600e3;
const jobLed = (j) => (j.state === 'failed' ? 'bad' : j.state === 'done' ? 'ok' : j.state === 'running' || (j.state === 'queued' && !stale(j)) ? 'run' : '');
const jobWord = (j) => (j.state === 'failed' ? `stopped at ${j.stage || 'start'}` : j.state === 'done' && j.stage === 'done' ? 'finished' : j.state === 'queued' ? (stale(j) ? 'brief only, never started' : 'queued') : j.stage ? `${j.stage}, ${j.state || ''}` : 'waiting');

export function Jobs() {
  const { route } = useOS();
  if (route.rest) return <Job id={route.rest} />;
  return <JobList />;
}

function JobList() {
  const jobs = useFetch('/api/jobs', { every: 30000 });
  const runs = useFetch('/api/runs', { every: 30000 });
  const [repo, setRepo] = useState('all');
  const list = jobs.data?.jobs || [];
  const rl = (runs.data?.runs || []).filter((r) => repo === 'all' || r.repo.endsWith(repo));
  return (
    <div className="app jobs">
      <Head title="Jobs" lede="Studio builds with their stages and spend, then every render run on GitHub. Refreshes on its own." />
      <Panel title="Studio builds" count={list.length} id="h-builds">
        {jobs.loading && !jobs.data && <Empty>Asking GitHub</Empty>}
        {jobs.data?.error && <Note tone="warn">GitHub did not list the builds: {jobs.data.error}.</Note>}
        {jobs.data && !list.length && !jobs.data.error && <Empty>No studio builds yet. Start one in Create.</Empty>}
        <ul className="joblist">
          {list.map((j) => {
            const cur = Math.max(0, STAGES.findIndex(([k]) => k === j.stage));
            return (
              <li key={j.id}>
                <a href={`#/jobs/${j.id}`} className="jobrow">
                  <span className="jr-title"><Led s={jobLed(j)} /><b>{j.title}</b><span className="dim">{[LINE[j.line] || j.line, j.format, j.look && `look ${j.look}`].filter(Boolean).join(', ')}</span></span>
                  <span className="jr-stages" aria-label={`Stage: ${jobWord(j)}`}>{STAGES.map(([k, l], i) => <i key={k} title={l} className={rowState({ ...j, stages: j.stages }, k, i, cur)} />)}</span>
                  <span className="jr-word dim">{jobWord(j)}</span>
                  <span className="jr-money mono">{usd(j.usd) || '$0.00'}{j.cap_usd != null ? <span className="dim"> of {usd(j.cap_usd)}</span> : null}</span>
                  <span className="jr-when dim">{ago(j.updated)}</span>
                </a>
              </li>
            );
          })}
        </ul>
      </Panel>
      <Panel title="Render runs" count={rl.length} id="h-runs" action={<Seg label="Repository" value={repo} onChange={setRepo} options={[['all', 'All'], ['rc-render', 'Render farm'], ['kinoforge', 'Studio repo']]} />}>
        {runs.loading && !runs.data && <Empty>Asking GitHub</Empty>}
        {runs.data?.errors?.map((e) => <Note key={e.repo} tone="warn">{e.repo}: {e.error}. The list may be out of date.</Note>)}
        <ul className="runlist">
          {rl.map((r) => (
            <li key={r.repo + r.id}>
              <a className="runrow" href={r.url} target="_blank" rel="noreferrer">
                <Led s={runState(r)} />
                <span><b>{r.title || r.name}</b><span className="dim">{r.repo.split('/')[1]}, {r.workflow || r.name}{r.event ? `, ${r.event}` : ''}</span></span>
                <span className="mono dim">{r.status !== 'completed' ? r.status : r.conclusion}, {ago(r.updated)}</span>
              </a>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

// ------------------------------------------------------------------ one build, live
export function Job({ id }) {
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
        const s = st(d.status);
        if ((d.status?.stage === 'done' && s === 'done') || s === 'failed' || d.run?.conclusion === 'failure') return;
      } catch (e) { setErr(e.message); }
      if (!stop.current) t = setTimeout(tick, 6000);
    };
    tick();
    return () => { stop.current = true; clearTimeout(t); };
  }, [id]);

  const s = j?.status, state = st(s);
  const failed = state === 'failed' || (!s && j?.run?.conclusion && j.run.conclusion !== 'success');
  const done = s?.stage === 'done' && state === 'done';
  const curIdx = Math.max(0, STAGES.findIndex(([k]) => k === s?.stage));
  const cap = s?.cap_usd ?? j?.brief?.cap_usd;
  const brief = j?.brief;
  const runUrl = s?.run_url || j?.run?.url;
  const tall = brief?.line === 'kinetic' || (brief?.line === 'cutaway' && brief?.format === '9:16');
  return (
    <div className="app job">
      <nav className="crumbs" aria-label="Breadcrumb"><a href="#/jobs"><Icon.back size={16} />Jobs</a><span aria-current="page">{brief?.title || id}</span></nav>
      <Head title={brief?.title || id} lede={done ? 'Your film is ready.' : failed ? 'The build stopped.' : !s ? 'The build is starting on GitHub’s machines.' : 'Building on GitHub’s machines. You can close this page; it picks up where it was.'} />
      <div className="job-grid">
        <Panel title="Stages" id="h-stages">
          <ol className="pipeline" aria-live="polite">
            {STAGES.map(([k, label], i) => {
              const rs = rowState(s, k, i, curIdx); const spent = Number(s?.stages?.[k]?.spent || 0);
              return <li key={k} className={rs}><Led s={rs} /><span>{label}</span>{rs === 'run' && <em>working</em>}{spent > 0.0005 && <em className="mono">{usd(spent)}</em>}</li>;
            })}
          </ol>
          <Note tone={failed ? 'bad' : ''}>{err && !j ? err : failed ? (s?.message || 'The run failed before the film was finished.') : done ? (s?.message || 'Finished and published to the library.') : s?.message || (j?.run ? 'GitHub has accepted the job and is starting a runner.' : 'Waiting for GitHub to pick up the brief. This usually takes under a minute.')}</Note>
          {runUrl && <p><a href={runUrl} target="_blank" rel="noreferrer">Open the run on GitHub <Icon.external size={14} /></a></p>}
          {done && j?.film && (
            <div className={'player' + (tall ? ' tall' : '')}>
              <video src={j.film.preview} poster={j.film.poster} controls playsInline preload="metadata" />
            </div>
          )}
          {done && <div className="acts">{j?.film?.full && <a className="btn primary" href={j.film.full}><Icon.download size={16} />Full film</a>}<a className="btn" href={`#/library/${id}?tab=review`}>Review it in the library</a></div>}
        </Panel>
        <div className="job-side">
          <Panel title="Money" id="h-jm">
            <p className="bignum">{usd(s?.usd) || '$0.00'}{cap != null && <span> of {usd(cap)} cap</span>}</p>
            <div className="meter" aria-hidden="true"><i style={{ inlineSize: `${Math.min(100, cap ? (Number(s?.usd || 0) / cap) * 100 : 0)}%` }} /></div>
            <p className="dim small">Every paid call is booked against the cap before it is made. A film that cannot pass the checks inside the cap stops, and is not rendered.</p>
          </Panel>
          {brief && (
            <Panel title="The brief" id="h-jb">
              <dl className="facts">
                {[['Line', `${LINE[brief.line] || brief.line}${brief.format ? `, ${brief.format}` : ''}`], ['Look', brief.look], ['Subject', brief.subject], ['Angle', brief.angle], ['Audience', brief.audience], ['Tone', brief.tone], ['Length', brief.target_seconds ? clock(brief.target_seconds) : null], ['Music', brief.music_piece], ['Voice', brief.voice], ['Approved', brief.approved_at?.slice(0, 16).replace('T', ' ')]]
                  .filter(([, v]) => v).map(([k, v]) => <div key={k} style={{ display: 'contents' }}><dt>{k}</dt><dd>{v}</dd></div>)}
              </dl>
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}
