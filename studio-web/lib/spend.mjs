// Spend per video: public/data/spend.json (written by tools/spend.py, never by hand) made ready for the interface.
// Pure: no fetch, no React, so tests can import it (tests/spend.test.mjs).
//   normalizeSpend(raw)  every number checked, every list present; entries indexed by id
//   usdText(n)           money to the cent; under a cent shows the fraction ("$0.0016") so nothing reads as free
//   plainWords(e, rates) one or two sentences for Sam about one video's cost
//   checkTotals(s)       the studio totals recomputed from the entries (the test uses it: they must agree)

const num = (v) => (Number.isFinite(Number(v)) && v !== null && v !== '' ? Number(v) : 0);
const arr = (v) => (Array.isArray(v) ? v : []);
const str = (v) => (typeof v === 'string' ? v : v == null ? '' : String(v));

export const BASIS = {
  measured: { label: 'Measured', hint: 'the provider reported this cost' },
  estimated: { label: 'Estimated', hint: 'our code priced it (for example speech by the characters sent)' },
  unflagged: { label: 'Not flagged', hint: 'old code booked a list price when no cost came back and did not say which' },
};
export const KIND_NAMES = { film: 'Video', 'director-job': 'Director job', board: 'Style board', piece: 'AI-footage piece', showcase: 'Showcase agent', shared: 'Shared work', mac: 'Mac lane', other: 'Other' };
export const LOG_ROLE = { 'cross-check': 'Cross-check', shared: 'Shared figure', counted: 'Counted', mention: 'Mention' };

/** $0.24, $1,204.50, $0.0016 (under a cent: up to four decimals, so a small cost never reads as $0.00). */
export function usdText(n, { cad = false } = {}) {
  const v = num(n); const sign = cad ? 'CA$' : '$';
  if (v === 0) return `${sign}0.00`;
  if (Math.abs(v) < 0.01) return `${sign}${v.toFixed(4).replace(/0+$/, '')}`;
  return `${sign}${v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
/** Every recorded digit (up to six decimals), for the exact line under a rounded total. */
export const usdExact = (n) => `$${num(n).toFixed(6).replace(/\.?0+$/, '') || '0'}`;
/** 215 min, 3 h 35 min; seconds under a minute as "42 s". */
export function minutesText(min) {
  const m = Math.round(num(min));
  if (m < 60) return `${m} min`;
  return `${Math.floor(m / 60)} h${m % 60 ? ` ${m % 60} min` : ''}`;
}
export function secondsText(s) {
  const v = num(s);
  if (v < 60) return `${Math.round(v)} s`;
  return minutesText(v / 60);
}

function normEntry(e) {
  const t = e.total || {};
  const total = {};
  for (const k of ['paid_usd', 'measured_usd', 'estimated_usd', 'unflagged_usd', 'log_usd', 'failed_charged_usd', 'calls', 'failed_calls',
    'runner_minutes', 'runner_seconds', 'runner_worth_usd', 'mac_seconds', 'mac_kwh', 'electricity_cad']) total[k] = num(t[k]);
  total.cap_usd = t.cap_usd == null ? null : num(t.cap_usd);
  const comp = e.compute || {};
  return {
    id: str(e.id), title: str(e.title) || str(e.id), kind: KIND_NAMES[e.kind] ? e.kind : 'other', folder: e.folder || null,
    series: e.series || null, status: e.status || null, total,
    record: { paid: Boolean(e.record?.paid), log: Boolean(e.record?.log), runner: Boolean(e.record?.runner), mac: Boolean(e.record?.mac) },
    paid: arr(e.paid).map((l) => ({ ...l, usd: num(l.usd), basis: BASIS[l.basis] ? l.basis : 'measured', flags: arr(l.flags), ok: l.ok !== false })),
    director: e.director ? { ...e.director, stages: arr(e.director.stages).map((s) => ({ ...s, spent_usd: num(s.spent_usd) })) } : null,
    cross: arr(e.cross_checks), log: arr(e.log).map((l) => ({ ...l, amounts: arr(l.amounts) })), logZero: arr(e.log_zero),
    runs: arr(comp.runner?.runs).map((r) => ({ ...r, minutes_billable: num(r.minutes_billable), worth_usd: num(r.worth_usd), seconds: num(r.seconds) })),
    mac: arr(comp.mac?.lines).map((m) => ({ ...m, seconds: num(m.seconds), kwh: num(m.kwh), electricity_cad: num(m.electricity_cad), size: arr(m.size) })),
    notRecorded: arr(e.not_recorded).map(str),
    isVideo: e.kind === 'film' || e.kind === 'director-job',
  };
}

export function normalizeSpend(raw) {
  const s = raw && typeof raw === 'object' ? raw : {};
  const entries = arr(s.entries).filter((e) => e && e.id).map(normEntry);
  const byId = Object.fromEntries(entries.map((e) => [e.id, e]));
  const t = s.totals || {};
  const totals = {
    ...Object.fromEntries(['paid_usd', 'measured_usd', 'estimated_usd', 'unflagged_usd', 'log_usd', 'failed_charged_usd', 'films_paid_usd', 'other_paid_usd',
      'calls', 'failed_calls', 'runner_minutes', 'runner_seconds', 'runner_worth_usd', 'runner_runs', 'mac_seconds', 'mac_jobs', 'mac_kwh', 'electricity_cad'].map((k) => [k, num(t[k])])),
    by_month: arr(t.by_month).map((m) => ({ month: str(m.month), paid_usd: num(m.paid_usd), runner_minutes: num(m.runner_minutes), mac_seconds: num(m.mac_seconds) })),
    by_vendor: arr(t.by_vendor).map((v) => ({ ...v, usd: num(v.usd), calls: num(v.calls), measured_usd: num(v.measured_usd), estimated_usd: num(v.estimated_usd), unflagged_usd: num(v.unflagged_usd) })),
    by_seat: arr(t.by_seat).map((v) => ({ ...v, usd: num(v.usd), calls: num(v.calls) })),
    top_films: arr(t.top_films), no_record: arr(t.no_record), no_paid_record: arr(t.no_paid_record), other: arr(t.other),
  };
  return {
    generated: str(s.generated), rates: s.rates || {}, how: arr(s.how).map(str), entries, byId, totals,
    videos: entries.filter((e) => e.isVideo), other: entries.filter((e) => !e.isVideo),
  };
}

export const spendRoute = (id, spend) => (spend?.byId?.[id] && !spend.byId[id].isVideo ? `spend/${id}` : `library/${id}?tab=spend`);

/** Paid lines grouped by seat and model, biggest first: [{key, seat, model, vendor, usd, calls, bases: {measured, ...}, lines}] */
export function groupPaid(lines) {
  const m = new Map();
  for (const l of lines) {
    const key = `${l.seat}|${l.model}`;
    const g = m.get(key) || { key, seat: l.seat, model: l.model, vendor: l.vendor, usd: 0, calls: 0, failed: 0, bases: {}, lines: [] };
    g.usd += l.usd; g.calls += 1; g.failed += l.ok ? 0 : 1; g.bases[l.basis] = (g.bases[l.basis] || 0) + l.usd; g.lines.push(l);
    m.set(key, g);
  }
  return [...m.values()].sort((a, b) => b.usd - a.usd || a.key.localeCompare(b.key));
}

/** One or two plain sentences: what was paid, against what cap, and what the free compute was worth. */
export function plainWords(e) {
  if (!e) return 'No spend record for this video.';
  const t = e.total; const out = [];
  if (e.paid.length || t.log_usd) {
    const parts = [t.measured_usd && `${usdText(t.measured_usd)} measured`, t.estimated_usd && `${usdText(t.estimated_usd)} estimated`,
      t.unflagged_usd && `${usdText(t.unflagged_usd)} not flagged`, t.log_usd && `${usdText(t.log_usd)} from the log`].filter(Boolean);
    out.push(`Paid ${usdText(t.paid_usd)}${parts.length > 1 ? ` (${parts.join(', ')})` : parts.length ? ` (${parts[0].replace(/^\$[\d.,]+ /, '')})` : ''}${t.cap_usd != null ? ` against a cap of ${usdText(t.cap_usd)}` : ''}.`);
  } else out.push(e.logZero.length ? 'No paid calls recorded; the log marks its changes as US$0.' : 'No paid calls recorded.');
  const free = [];
  if (t.runner_minutes) free.push(`${minutesText(t.runner_minutes)} on GitHub runners (free, worth ${usdText(t.runner_worth_usd)} at list price)`);
  if (t.mac_seconds) free.push(`${secondsText(t.mac_seconds)} on the Mac lane (about ${usdText(t.electricity_cad, { cad: true })} of electricity)`);
  if (free.length) out.push(`Rendering: ${free.join('; ')}.`);
  else if (e.isVideo) out.push('Rendering time is not recorded.');
  return out.join(' ');
}

/** The studio totals recomputed from the entries; any difference over half a cent is reported. */
export function checkTotals(s) {
  const sum = (k) => s.entries.reduce((a, e) => a + e.total[k], 0);
  const out = [];
  for (const k of ['paid_usd', 'measured_usd', 'estimated_usd', 'unflagged_usd', 'runner_worth_usd']) {
    if (Math.abs(sum(k) - s.totals[k]) > 0.005) out.push(`${k}: entries ${sum(k).toFixed(4)}, total ${s.totals[k].toFixed(4)}`);
  }
  if (Math.round(sum('runner_minutes')) !== Math.round(s.totals.runner_minutes)) out.push('runner_minutes differ');
  for (const e of s.entries) {
    const lines = e.paid.reduce((a, l) => a + l.usd, 0) + e.total.log_usd;
    if (Math.abs(lines - e.total.paid_usd) > 0.005) out.push(`${e.id}: lines ${lines.toFixed(4)}, total ${e.total.paid_usd.toFixed(4)}`);
  }
  return out;
}
