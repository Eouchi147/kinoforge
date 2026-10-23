'use client';
// Spend: what the studio has spent, video by video (public/data/spend.json, built by tools/spend.py from the ledgers,
// the log, the GitHub runs and the Mac lane job logs). The studio view (#/spend), one record (#/spend/<id>) for work that
// is not a video in the library, and the film page's Spend tab (FilmSpend, used by Library).
import { useMemo } from 'react';
import { useOS, useFetch } from '../store';
import { Head, Panel, Empty, Note } from '../ui';
import { Icon } from '../icons';
import { normalizeSpend, usdText, usdExact, minutesText, secondsText, groupPaid, plainWords, spendRoute, BASIS, KIND_NAMES, LOG_ROLE } from '@/lib/spend.mjs';

const MANUAL = '#/manual/docs/manual/system/money-and-keys.md';

export function useSpend() {
  const d = useFetch('/data/spend.json');
  const spend = useMemo(() => (d.data && !d.error ? normalizeSpend(d.data) : null), [d.data, d.error]);
  return { spend, loading: d.loading, error: d.error };
}

function Missing({ error }) {
  return <Note tone="warn">The spend record could not be read{error ? ` (${error})` : ''}. It is built by <code>python3 tools/spend.py</code> into public/data/spend.json.</Note>;
}

const Basis = ({ b }) => <span className={'pill b-' + b} title={BASIS[b]?.hint}>{BASIS[b]?.label || b}</span>;
const Bar = ({ v, max }) => <span className="sbar" aria-hidden="true"><i style={{ inlineSize: `${max > 0 ? Math.max(1.5, (v / max) * 100) : 0}%` }} /></span>;
const dayText = (d) => (d ? new Date(d + (d.length === 10 ? 'T12:00:00Z' : '')).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }) : 'not dated');
const monthText = (m) => (/^\d{4}-\d{2}$/.test(m) ? new Date(m + '-15T12:00:00Z').toLocaleDateString('en-GB', { month: 'long', year: 'numeric', timeZone: 'UTC' }) : m);

// ------------------------------------------------------------------ one record (a film's Spend tab, or #/spend/<id>)
export function FilmSpend({ id, compact = false }) {
  const { spend, loading, error } = useSpend();
  if (loading && !spend) return <Empty>Reading the spend record</Empty>;
  if (!spend) return <Missing error={error} />;
  const e = spend.byId[id];
  if (!e) return <Note tone="warn">This video has no entry in the spend record yet. Run <code>python3 tools/spend.py</code> after the catalog lists it.</Note>;
  return <SpendDetail e={e} rates={spend.rates} compact={compact} />;
}

function SpendDetail({ e, rates }) {
  const t = e.total;
  const groups = groupPaid(e.paid);
  const capShare = t.cap_usd ? Math.min(100, (t.paid_usd / t.cap_usd) * 100) : null;
  const runnerRate = rates?.runner_usd_per_min?.value;
  return (
    <div className="spend-detail">
      <div className="spend-top">
        <div className="spend-big">
          <p className="bignum">{usdText(t.paid_usd)}<span> paid{t.cap_usd != null ? ` of a ${usdText(t.cap_usd)} cap` : ''}</span></p>
          {capShare != null && <div className="meter" role="img" aria-label={`${Math.round(capShare)} percent of the cap`}><i style={{ inlineSize: `${capShare}%` }} /></div>}
          <p className="dim small">{t.paid_usd ? `Exact: ${usdExact(t.paid_usd)}` : ''}{t.paid_usd && t.calls ? ', ' : ''}{t.calls ? `${t.calls} paid call${t.calls === 1 ? '' : 's'}${t.failed_calls ? `, ${t.failed_calls} failed` : ''}` : ''}</p>
        </div>
        <dl className="facts spend-split">
          <dt>Measured</dt><dd className="mono">{usdText(t.measured_usd)}</dd>
          <dt>Estimated</dt><dd className="mono">{usdText(t.estimated_usd)}</dd>
          {t.unflagged_usd > 0 && <><dt>Not flagged</dt><dd className="mono">{usdText(t.unflagged_usd)}</dd></>}
          {t.log_usd > 0 && <><dt>From the log</dt><dd className="mono">{usdText(t.log_usd)}</dd></>}
          {t.failed_charged_usd > 0 && <><dt>Failed, still charged</dt><dd className="mono">{usdText(t.failed_charged_usd)}</dd></>}
          <dt>GitHub runners</dt><dd>{t.runner_minutes ? <><span className="mono">{minutesText(t.runner_minutes)}</span> free, worth <span className="mono">{usdText(t.runner_worth_usd)}</span></> : 'not recorded'}</dd>
          <dt>Mac lane</dt><dd>{t.mac_seconds ? <><span className="mono">{secondsText(t.mac_seconds)}</span>, about <span className="mono">{usdText(t.electricity_cad, { cad: true })}</span> power</> : 'none in the Mac lane job logs'}</dd>
        </dl>
      </div>
      <p className="spend-words">{plainWords(e)}</p>

      <section className="spend-sec" aria-labelledby={`sp-paid-${e.id}`}>
        <h3 id={`sp-paid-${e.id}`}>Paid calls</h3>
        {!groups.length && <p className="dim">{e.notRecorded.find((x) => x.startsWith('paid calls')) ? 'No ledger: no paid call is recorded for this video.' : 'None.'}</p>}
        {groups.map((g) => (
          <details key={g.key} className="sgroup">
            <summary>
              <span className="sg-chev"><Icon.next size={14} /></span>
              <span className="sg-name"><b>{g.seat}</b><span className="dim">{g.model}</span></span>
              <span className="sg-n dim">{g.calls} call{g.calls === 1 ? '' : 's'}{g.failed ? `, ${g.failed} failed` : ''}</span>
              <span className="sg-b">{Object.keys(g.bases).map((b) => <Basis key={b} b={b} />)}</span>
              <span className="sg-usd mono">{usdText(g.usd)}</span>
            </summary>
            <div className="stable-wrap">
              <table className="stable">
                <thead><tr><th scope="col">Task</th><th scope="col" className="num">Amount</th><th scope="col">Basis</th><th scope="col" className="opt">Time</th><th scope="col" className="opt">Day</th></tr></thead>
                <tbody>
                  {g.lines.map((l, i) => (
                    <tr key={i} className={l.ok ? '' : 'failed'}>
                      <td>{l.task}{l.part ? <span className="dim small"> ({l.part})</span> : null}{l.flags.length > 0 && <span className="sflags">{l.flags.map((f) => <span key={f} className={'pill ' + (/charged|unreadable|no cost/.test(f) ? 'warnline' : '')}>{f}</span>)}</span>}</td>
                      <td className="mono num">{usdExact(l.usd)}</td>
                      <td><Basis b={l.basis} /></td>
                      <td className="mono dim opt">{l.seconds != null ? `${Math.round(l.seconds)} s` : ''}</td>
                      <td className="dim opt">{l.date ? dayText(l.date) : 'not committed'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="dim small">{[...new Set(g.lines.map((l) => l.basis_why || BASIS[l.basis]?.hint).filter(Boolean))].map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join('. ')}. Source <code>{g.lines[0].source}</code>.</p>
          </details>
        ))}
      </section>

      {e.director && (
        <section className="spend-sec" aria-labelledby={`sp-dir-${e.id}`}>
          <h3 id={`sp-dir-${e.id}`}>Director stages</h3>
          <div className="stable-wrap">
            <table className="stable">
              <thead><tr><th scope="col">Stage</th><th scope="col">State</th><th scope="col" className="num">Spent</th><th scope="col" className="num">Running total</th></tr></thead>
              <tbody>{e.director.stages.map((s) => <tr key={s.stage}><td>{s.stage}</td><td className="dim">{s.state}</td><td className="mono num">{usdText(s.spent_usd)}</td><td className="mono num dim">{usdText(s.running_usd)}</td></tr>)}</tbody>
            </table>
          </div>
          {e.director.message && <p className="dim small">Last message: {e.director.message}</p>}
          <p className="dim small">From <code>{e.director.source}</code>; a stage's spend is the difference of the running totals where the file has no per-stage figure.</p>
        </section>
      )}

      <section className="spend-sec" aria-labelledby={`sp-cmp-${e.id}`}>
        <h3 id={`sp-cmp-${e.id}`}>Rendering and compute</h3>
        {!e.runs.length && !e.mac.length && <p className="dim">No render time is recorded for this video.</p>}
        {e.runs.length > 0 && (
          <div className="stable-wrap">
            <table className="stable">
              <thead><tr><th scope="col">GitHub run</th><th scope="col" className="num">Jobs</th><th scope="col" className="num">Minutes</th><th scope="col" className="num">Worth</th><th scope="col">Result</th></tr></thead>
              <tbody>
                {e.runs.map((r) => (
                  <tr key={r.run_id}>
                    <td><a href={r.url} target="_blank" rel="noreferrer">{r.what}</a><span className="dim small"> {r.repo?.split('/')[1]}, {dayText(r.date)}</span></td>
                    <td className="mono num">{r.jobs}</td>
                    <td className="mono num">{r.minutes_billable}</td>
                    <td className="mono num">{usdText(r.worth_usd)}</td>
                    <td className="dim">{r.conclusion || 'not recorded'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {e.runs.length > 0 && <p className="dim small">Free: public repos. Minutes are rounded up per job, as GitHub bills; worth is {runnerRate ? `${usdText(runnerRate)} a minute, ` : ''}GitHub&apos;s list price for the same jobs in a private repo.</p>}
        {e.mac.length > 0 && (
          <div className="stable-wrap">
            <table className="stable">
              <thead><tr><th scope="col">Mac lane</th><th scope="col" className="num">Jobs</th><th scope="col" className="num">Frames</th><th scope="col" className="num">Time</th><th scope="col" className="num">Power</th></tr></thead>
              <tbody>
                {e.mac.map((m, i) => (
                  <tr key={i}>
                    <td>{m.what}<span className="dim small"> {m.size.join('; ')}</span></td>
                    <td className="mono num">{m.jobs}</td>
                    <td className="mono num">{m.frames}</td>
                    <td className="mono num">{secondsText(m.seconds)}</td>
                    <td className="mono num">{usdText(m.electricity_cad, { cad: true })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {e.mac.length > 0 && <p className="dim small">Render time from the job logs on the drive. Power is an estimate: {rates?.mac_watts?.value} W and CA${rates?.kwh_cad?.value} a kWh, both assumed and not yet checked (see How it is measured).</p>}
      </section>

      {(e.log.length > 0 || e.logZero.length > 0) && (
        <section className="spend-sec" aria-labelledby={`sp-log-${e.id}`}>
          <h3 id={`sp-log-${e.id}`}>From the log</h3>
          <ul className="slog">
            {e.log.map((l, i) => (
              <li key={i}><span className="pill">{LOG_ROLE[l.role] || l.role}</span><span><q>{l.text}</q><span className="dim small"> docs/LOG.md, {dayText(l.date)}, line {l.line}: {l.why}.</span></span></li>
            ))}
            {e.logZero.length > 0 && <li><span className="pill">US$0</span><span className="dim">The log marks this video&apos;s changes as US$0 on {e.logZero.map(dayText).join(', ')}.</span></li>}
          </ul>
        </section>
      )}

      {e.cross.length > 0 && (
        <section className="spend-sec">
          <h3>Account cross-check</h3>
          {e.cross.map((c) => <p key={c.source} className="dim small">OpenRouter key usage moved by <span className="mono">{usdText(c.account_usd)}</span> while the ledger says <span className="mono">{usdText(c.ledger_usd)}</span>: {c.note}.</p>)}
        </section>
      )}

      <section className="spend-sec" aria-labelledby={`sp-nr-${e.id}`}>
        <h3 id={`sp-nr-${e.id}`}>Not recorded</h3>
        {e.notRecorded.length ? <ul className="snr">{e.notRecorded.map((x) => <li key={x}>{x}</li>)}</ul> : <p className="dim">Nothing missing that the studio knows of.</p>}
        <p className="dim small"><a href={MANUAL}>How spend is measured</a></p>
      </section>
    </div>
  );
}

// ------------------------------------------------------------------ the studio view
export function Spend() {
  const { route, catalog } = useOS();
  const { spend, loading, error } = useSpend();
  if (route.rest) return <SpendOne id={route.rest} spend={spend} loading={loading} error={error} />;
  const t = spend?.totals;
  const maxV = Math.max(0, ...(t?.by_vendor || []).map((v) => v.usd));
  const maxS = Math.max(0, ...(t?.by_seat || []).map((v) => v.usd));
  const title = (id) => catalog?.films.find((f) => f.id === id)?.title || spend?.byId[id]?.title || id;
  return (
    <div className="app spend">
      <Head title="Spend" lede="What the studio has spent, video by video. Paid calls say whether the cost was measured by the provider or estimated by our code; rendering is free and shown with what it would be worth." />
      {loading && !spend && <Empty>Reading the spend record</Empty>}
      {!loading && !spend && <Missing error={error} />}
      {spend && (
        <>
          <div className="spend-cards">
            <Panel title="Paid, all time" id="h-sp-paid">
              <p className="bignum">{usdText(t.paid_usd)}<span> in {t.calls} paid calls</span></p>
              <dl className="facts">
                <dt>Measured</dt><dd className="mono">{usdText(t.measured_usd)}</dd>
                <dt>Estimated</dt><dd className="mono">{usdText(t.estimated_usd)}</dd>
                {t.unflagged_usd > 0 && <><dt>Not flagged</dt><dd className="mono">{usdText(t.unflagged_usd)}</dd></>}
                {t.failed_charged_usd > 0 && <><dt>Failed, still charged</dt><dd className="mono">{usdText(t.failed_charged_usd)}</dd></>}
              </dl>
              <p className="dim small">Videos in the library {usdText(t.films_paid_usd)}; other paid work (style boards, AI-footage pieces, the showcase agent) {usdText(t.other_paid_usd)}.</p>
            </Panel>
            <Panel title="GitHub runners" id="h-sp-run">
              <p className="bignum">{minutesText(t.runner_minutes)}<span> free</span></p>
              <p className="dim small">{t.runner_runs} recorded runs. Worth {usdText(t.runner_worth_usd)} at GitHub&apos;s list price; many older runs have no run id written down, so this is a floor.</p>
            </Panel>
            <Panel title="Mac lane" id="h-sp-mac">
              <p className="bignum">{secondsText(t.mac_seconds)}<span> of rendering</span></p>
              <p className="dim small">{t.mac_jobs} jobs. About {usdText(t.electricity_cad, { cad: true })} of electricity ({t.mac_kwh.toFixed(2)} kWh), an estimate from assumed figures.</p>
            </Panel>
          </div>

          <div className="two">
            <Panel title="Most expensive videos" id="h-sp-top">
              {!t.top_films.length && <Empty>No video has a paid record yet.</Empty>}
              <ol className="srank">
                {t.top_films.map((f) => (
                  <li key={f.id}><a href={`#/${spendRoute(f.id, spend)}`}><span className="sr-t">{title(f.id)}</span><span className="mono">{usdText(f.paid_usd)}</span></a>
                    <span className="dim small">{f.runner_minutes ? `${minutesText(f.runner_minutes)} on runners` : 'runner time not recorded'}{f.mac_seconds ? `, ${secondsText(f.mac_seconds)} on the Mac` : ''}</span></li>
                ))}
              </ol>
            </Panel>
            <Panel title="By month" id="h-sp-month">
              <div className="stable-wrap">
                <table className="stable">
                  <thead><tr><th scope="col">Month</th><th scope="col" className="num">Paid</th><th scope="col" className="num">Runner minutes</th><th scope="col" className="num">Mac time</th></tr></thead>
                  <tbody>{t.by_month.map((m) => <tr key={m.month}><td>{monthText(m.month)}</td><td className="mono num">{usdText(m.paid_usd)}</td><td className="mono num">{m.runner_minutes}</td><td className="mono num">{secondsText(m.mac_seconds)}</td></tr>)}</tbody>
                </table>
              </div>
              <p className="dim small">A paid call is dated by the commit that first recorded it (new ledgers stamp the minute).</p>
            </Panel>
          </div>

          <div className="two">
            <Panel title="By vendor" id="h-sp-vendor">
              <ul className="sbars">
                {t.by_vendor.map((v) => (
                  <li key={v.vendor}><span className="sb-l">{v.vendor}<span className="dim small"> {v.calls} calls{v.estimated_usd > 0 ? `, ${usdText(v.estimated_usd)} estimated` : ''}{v.unflagged_usd > 0 ? `, ${usdText(v.unflagged_usd)} not flagged` : ''}</span></span><span className="mono">{usdText(v.usd)}</span><Bar v={v.usd} max={maxV} /></li>
                ))}
              </ul>
              <p className="dim small">Every paid call went through OpenRouter; the vendor is who made the model.</p>
            </Panel>
            <Panel title="By seat" id="h-sp-seat">
              <ul className="sbars">
                {t.by_seat.map((v) => <li key={v.seat}><span className="sb-l">{v.seat}<span className="dim small"> {v.calls} calls</span></span><span className="mono">{usdText(v.usd)}</span><Bar v={v.usd} max={maxS} /></li>)}
              </ul>
              <p className="dim small">A seat is the job a model did: head writes, deputy checks, voice speaks, image and video make footage, eyes and ears review.</p>
            </Panel>
          </div>

          <Panel title="Other paid work" count={t.other.length} id="h-sp-other">
            <p className="dim small">Spend that is not a video in the library: style boards, the 15 Oct AI-footage pieces and showcase agent, shared tools, and Mac lane look boards.</p>
            <ul className="srank">
              {t.other.map((o) => (
                <li key={o.id}><a href={`#/spend/${o.id}`}><span className="sr-t">{o.title}</span><span className="mono">{o.paid_usd ? usdText(o.paid_usd) : 'free'}</span></a>
                  <span className="dim small">{KIND_NAMES[o.kind] || o.kind}{o.runner_minutes ? `, ${minutesText(o.runner_minutes)} on runners` : ''}{o.mac_seconds ? `, ${secondsText(o.mac_seconds)} on the Mac` : ''}</span></li>
              ))}
            </ul>
          </Panel>

          <div className="two">
            <Panel title="Videos with no cost record" count={t.no_record.length} id="h-sp-none">
              <p className="dim small">Nothing at all is written down for these: no ledger, no money in the log, no run id, no Mac job.</p>
              <ul className="slist">{t.no_record.map((f) => <li key={f.id}><a href={`#/library/${f.id}?tab=spend`}>{title(f.id)}</a></li>)}</ul>
            </Panel>
            <Panel title="How it is measured" id="h-sp-how">
              <ul className="howto">{spend.how.map((h) => <li key={h}>{h}</li>)}</ul>
              <dl className="facts tight">
                {Object.entries(spend.rates).map(([k, r]) => (
                  <div key={k} className="rate"><dt>{r.unit}</dt><dd><span className="mono">{r.value}</span> {r.verified ? <span className="pill">cited</span> : <span className="pill warnline">assumed, to check</span>}<span className="dim small"> {r.what} Source: {r.source}</span></dd></div>
                ))}
              </dl>
              <p className="dim small">Built {spend.generated ? spend.generated.slice(0, 16).replace('T', ' ') + ' UTC' : 'at an unknown time'} by tools/spend.py. <a href={MANUAL}>The full method in the manual</a>.</p>
            </Panel>
          </div>
        </>
      )}
    </div>
  );
}

function SpendOne({ id, spend, loading, error }) {
  const e = spend?.byId[id];
  return (
    <div className="app spend">
      <nav className="crumbs" aria-label="Breadcrumb"><a href="#/spend"><Icon.back size={16} />Spend</a><span aria-current="page">{e?.title || id}</span></nav>
      {loading && !spend && <Empty>Reading the spend record</Empty>}
      {!loading && !spend && <Missing error={error} />}
      {spend && !e && <Note tone="warn">No spend entry with the id {id}.</Note>}
      {e && (
        <>
          <Head title={e.title} lede={[KIND_NAMES[e.kind], e.folder].filter(Boolean).join(', ')}>
            {e.isVideo && <a className="btn" href={`#/library/${e.id}?tab=spend`}>Open the video</a>}
          </Head>
          <Panel><SpendDetail e={e} rates={spend.rates} /></Panel>
        </>
      )}
    </div>
  );
}
