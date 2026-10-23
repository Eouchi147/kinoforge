'use client';
// Desk: what needs Sam, what is running, the latest deliveries, money, and one-tap starts.
import { useEffect, useMemo, useState } from 'react';
import { useOS, useFetch, ago, usd } from '../store';
import { Head, Panel, FilmTile, Led, Empty, Note, Poster } from '../ui';
import { byDate, needsVerdict } from '@/lib/catalog.mjs';
import { createRoute } from '@/lib/commands.mjs';
import { Icon } from '../icons';

const QUICK = [
  { label: 'Cutaway loop', sub: '9:16, one fixed view, 30 s', p: { what: 'loop', line: 'cutaway', format: '9:16', length: 30 }, img: '/looks/seasons-base-100.jpg', tall: true },
  { label: 'Cutaway film', sub: '16:9, what lies under', p: { what: 'film', line: 'cutaway', format: '16:9', length: 60 }, img: '/looks/reference-830.jpg' },
  { label: 'Battle Map', sub: '16:9, about 2.5 min', p: { what: 'explainer', line: 'battle-map', format: '16:9', length: 150 }, img: '/posters/battle-map-cannae.jpg' },
  { label: 'Kinetic story', sub: '9:16, words in motion', p: { what: 'film', line: 'kinetic', format: '9:16', length: 120 }, img: '/posters/dark-corners-bamberg-kinetic.jpg', tall: true },
];

export function runState(r) { return r.status !== 'completed' ? 'run' : r.conclusion === 'success' ? 'ok' : r.conclusion === 'cancelled' || r.conclusion === 'skipped' ? '' : 'bad'; }

export function Desk() {
  const { catalog, status, lock, reviews } = useOS();
  const jobs = useFetch('/api/jobs', { every: 30000 });
  const runs = useFetch('/api/runs', { every: 30000 });
  const remote = useFetch('/api/review', { every: 120000 });
  const [draft, setDraft] = useState(null);
  useEffect(() => { try { setDraft(JSON.parse(localStorage.getItem('kf-create-1') || 'null')); } catch {} }, []);

  const verdicts = useMemo(() => {
    const v = { ...(remote.data?.verdicts || {}) };
    for (const [id, r] of Object.entries(reviews)) if (r?.verdict) v[id] = r.verdict;
    return v;
  }, [remote.data, reviews]);
  const films = catalog?.films || [];
  const waiting = films.filter((f) => needsVerdict(f, Object.fromEntries(Object.entries(verdicts).map(([k, x]) => [k, { verdict: x }])))).sort(byDate);
  const jobList = jobs.data?.jobs || [];
  const fresh = (j) => j.updated && Date.now() - new Date(j.updated) < 2 * 3600e3;
  const runningJobs = jobList.filter((j) => j.state === 'running' || (j.state === 'queued' && fresh(j)));   // a brief with no status for hours is not running
  const failedJobs = jobList.filter((j) => j.state === 'failed' && j.updated && Date.now() - new Date(j.updated) < 3 * 864e5);
  const runList = runs.data?.runs || [];
  const live = runList.filter((r) => r.status !== 'completed');
  const recentRuns = runList.slice(0, 6);
  const latest = [...films].sort(byDate).slice(0, 8);
  const a = status?.account, caps = status?.caps;
  const draftReady = draft?.brief && ['title', 'line', 'subject', 'angle', 'audience', 'tone', 'target_seconds'].every((k) => draft.brief[k]);

  const needs = [];
  if (status && !status.openrouter) needs.push({ key: 'or', href: '#/settings', title: 'Connect the director', sub: 'The director chat needs the OpenRouter key on Vercel.', tone: 'warn' });
  if (lock && !lock.required) needs.push({ key: 'lock', href: '#/settings', title: 'Writes are open to anyone with the link', sub: 'Set a passcode on Vercel to lock builds, reviews and the director chat.', tone: 'warn' });
  if (draftReady) needs.push({ key: 'draft', href: '#/create', title: `Your brief "${draft.brief.title}" is ready to build`, sub: 'Check it once and tap Build.' });
  for (const j of failedJobs) needs.push({ key: 'f' + j.id, href: `#/jobs/${j.id}`, title: `Build stopped: ${j.title}`, sub: (j.message || '').slice(0, 140), tone: 'bad' });
  for (const f of waiting.slice(0, 6)) needs.push({ key: f.id, href: `#/library/${f.id}?tab=review`, title: `Give a verdict: ${f.title}`, sub: [f.series, f.format, 'delivered', f.date].filter(Boolean).join(', '), film: f.posterUrl ? f : null });

  const parts = [];
  if (catalog) parts.push(waiting.length ? `${waiting.length} film${waiting.length === 1 ? '' : 's'} wait for your verdict.` : 'Every delivered film has a verdict.');
  if (jobs.data || runs.data) parts.push(runningJobs.length + live.length ? `${runningJobs.length + live.length} running now.` : 'Nothing is running.');
  if (a?.remaining != null) parts.push(`${usd(a.remaining)} left on the studio key.`);

  return (
    <div className="app desk">
      <Head title="Desk" lede={parts.join(' ') || 'Reading the studio'} />
      <div className="desk-grid">
        <Panel title="Needs you" count={needs.length} className="needs" id="h-needs">
          {!catalog && <Empty>Reading the library</Empty>}
          {catalog && !needs.length && <Empty>Nothing waits for you. Start something below.</Empty>}
          <ul className="needs-list">
            {needs.map((n) => (
              <li key={n.key}>
                <a href={n.href} className={'need ' + (n.tone || '')}>
                  {n.film ? <span className="need-img"><Poster src={n.film.posterUrl} format={n.film.format} label="" /></span> : <span className="need-mark"><Led s={n.tone === 'bad' ? 'bad' : 'warn'} /></span>}
                  <span className="need-txt"><b>{n.title}</b><span>{n.sub}</span></span>
                  <Icon.next />
                </a>
              </li>
            ))}
          </ul>
          {waiting.length > 6 && <a className="more-link" href="#/library?view=verdict">All {waiting.length} films without a verdict</a>}
        </Panel>

        <div className="desk-side">
        <Panel title="Running" count={runningJobs.length + live.length} id="h-run" action={<a className="more-link" href="#/jobs">All jobs</a>}>
          {(jobs.loading || runs.loading) && !jobs.data && !runs.data && <Empty>Asking GitHub</Empty>}
          {runningJobs.map((j) => (
            <a key={j.id} className="runrow" href={`#/jobs/${j.id}`}><Led s="run" /><span><b>{j.title}</b><span className="dim">Studio build, {j.stage || 'starting'}</span></span><span className="mono dim">{usd(j.usd)}{j.cap_usd ? ` of ${usd(j.cap_usd)}` : ''}</span></a>
          ))}
          {(live.length ? live : recentRuns).slice(0, 6).map((r) => (
            <a key={r.repo + r.id} className="runrow" href={r.url} target="_blank" rel="noreferrer"><Led s={runState(r)} /><span><b>{r.title || r.name}</b><span className="dim">{r.repo.split('/')[1]}, {r.name}</span></span><span className="mono dim">{r.status !== 'completed' ? 'running' : ago(r.updated)}</span></a>
          ))}
          {!live.length && !runningJobs.length && runs.data && <p className="dim small">Nothing running. The last runs are shown.</p>}
          {runs.data?.errors?.length > 0 && <Note tone="warn">{runs.data.errors.map((e) => `${e.repo.split('/')[1]}: ${e.error}`).join('. ')}.</Note>}
          {jobs.data?.error && <Note tone="warn">Studio jobs: {jobs.data.error}.</Note>}
        </Panel>

        <Panel title="Money" id="h-money" action={<a className="more-link" href="#/settings">Caps</a>}>
          {!status && <Empty>Reading</Empty>}
          {status && !status.openrouter && <p className="dim">The director is not connected, so nothing is being spent.</p>}
          {a && (
            <>
              <p className="bignum">{usd(a.remaining)}<span> left{a.limit != null ? ` of ${usd(a.limit)}` : ''}</span></p>
              {a.limit ? <div className="meter" aria-hidden="true"><i style={{ inlineSize: `${Math.max(0, Math.min(100, (a.remaining / a.limit) * 100))}%` }} /></div> : null}
              <dl className="facts tight">
                {a.today != null && <><dt>Today</dt><dd className="mono">{usd(a.today)} of {usd(caps?.day_usd)} day cap</dd></>}
                <dt>Per film</dt><dd>hard cap you choose, $0.50 to $5.00, default $2</dd>
                <dt>Per message</dt><dd className="mono">{usd(caps?.turn_usd)}</dd>
              </dl>
            </>
          )}
          {status?.openrouter && !a && <p className="dim">The key's balance could not be read just now.</p>}
        </Panel>

        <Panel title="Start something" className="quick" id="h-quick" action={<a className="more-link" href="#/create">Open Create</a>}>
          <div className="quick-grid">
            {QUICK.map((q) => (
              <a key={q.label} className="quick-card" href={'#/' + createRoute(q.p)}>
                <span className="qimg"><img src={q.img} alt="" loading="lazy" className={q.tall ? 'tall' : ''} /></span>
                <b>{q.label}</b><span>{q.sub}</span>
              </a>
            ))}
          </div>
        </Panel>
        </div>
      </div>

      <Panel title="Latest deliveries" className="latest" id="h-latest" action={<a className="more-link" href="#/library">Library</a>}>
        {!catalog && <Empty>Reading the library</Empty>}
        <div className="strip">{latest.map((f) => <FilmTile key={f.id} f={f} verdict={verdicts[f.id]} compact />)}</div>
      </Panel>
    </div>
  );
}
