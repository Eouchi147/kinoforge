// node --test studio-web/tests/*.test.mjs : the spend data loader (lib/spend.mjs) and the "spend" commands.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { normalizeSpend, usdText, usdExact, minutesText, secondsText, groupPaid, plainWords, checkTotals, spendRoute } from '../lib/spend.mjs';
import { interpret, search } from '../lib/commands.mjs';
import { normalize } from '../lib/catalog.mjs';

const SAMPLE = {
  generated: '2026-10-23T00:00:00Z', rates: { runner_usd_per_min: { value: 0.006 } }, how: ['x'],
  entries: [
    { id: 'battle-map-cannae', title: 'The Battle of Cannae', kind: 'film', record: { paid: true, log: true, runner: true, mac: false },
      total: { paid_usd: 0.2384, measured_usd: 0.08, estimated_usd: 0.1584, unflagged_usd: 0, log_usd: 0, failed_charged_usd: 0, calls: 3, failed_calls: 0, cap_usd: 0.9,
        runner_minutes: 215, runner_seconds: 12079, runner_worth_usd: 1.29, mac_seconds: 0, mac_kwh: 0, electricity_cad: 0 },
      paid: [
        { seat: 'music', model: 'google/lyria-3-pro-preview', vendor: 'Google Lyria music', task: 'music', usd: 0.08, basis: 'measured', ok: true, flags: [] },
        { seat: 'voice', model: 'elevenlabs/eleven-v4', vendor: 'ElevenLabs voice', task: 'vo 0', usd: 0.1, basis: 'estimated', ok: true, flags: [] },
        { seat: 'voice', model: 'elevenlabs/eleven-v4', vendor: 'ElevenLabs voice', task: 'vo 1', usd: '0.0584', basis: 'estimated', ok: true, flags: [] },
      ],
      compute: { runner: { runs: [{ run_id: 1, minutes_billable: 215, worth_usd: 1.29, seconds: 12079 }] }, mac: { lines: [] } }, log_zero: ['2026-10-23'] },
    { id: 'boards-x', title: 'Board x', kind: 'board', record: { paid: true },
      total: { paid_usd: 1.0, measured_usd: 1.0, calls: 1, cap_usd: null }, paid: [{ seat: 'image', model: 'm', usd: 1, basis: 'weird', ok: false, flags: ['failed but charged'] }] },
    { id: 'p01-static', title: 'Static', kind: 'film', total: {}, compute: {} },
    { title: 'no id: dropped' },
  ],
  totals: { paid_usd: 1.2384, measured_usd: 1.08, estimated_usd: 0.1584, unflagged_usd: 0, runner_minutes: 215, runner_worth_usd: 1.29, calls: 4,
    by_vendor: [{ vendor: 'ElevenLabs voice', usd: 0.1584, calls: 2 }], by_month: [{ month: '2026-10', paid_usd: 1.2384 }], no_record: [{ id: 'p01-static' }] },
};

test('normalizeSpend: ids indexed, numbers checked, unknown bases and kinds made safe', () => {
  const s = normalizeSpend(SAMPLE);
  assert.equal(s.entries.length, 3);
  assert.equal(s.byId['battle-map-cannae'].paid[2].usd, 0.0584);
  assert.equal(s.byId['boards-x'].paid[0].basis, 'measured');
  assert.equal(s.byId['boards-x'].paid[0].ok, false);
  assert.equal(s.byId['p01-static'].total.paid_usd, 0);
  assert.equal(s.byId['p01-static'].total.cap_usd, null);
  assert.deepEqual(s.byId['p01-static'].runs, []);
  assert.equal(s.videos.length, 2); assert.equal(s.other.length, 1);
  assert.deepEqual(checkTotals(s), []);
});
test('normalizeSpend: nothing in, nothing breaks', () => {
  for (const raw of [null, undefined, 'x', {}, { entries: 'no' }]) {
    const s = normalizeSpend(raw);
    assert.deepEqual(s.entries, []); assert.equal(s.totals.paid_usd, 0); assert.deepEqual(s.totals.by_month, []);
  }
});
test('checkTotals reports a total that does not add up', () => {
  const bad = normalizeSpend({ ...SAMPLE, totals: { ...SAMPLE.totals, paid_usd: 5 } });
  assert.ok(checkTotals(bad).some((x) => x.startsWith('paid_usd')));
});
test('money and time read well and never hide a small cost', () => {
  assert.equal(usdText(0.2384), '$0.24');
  assert.equal(usdText(0.0016), '$0.0016');
  assert.equal(usdText(0), '$0.00');
  assert.equal(usdText(1204.5), '$1,204.50');
  assert.equal(usdText('nope'), '$0.00');
  assert.equal(usdText(0.03, { cad: true }), 'CA$0.03');
  assert.equal(usdExact(0.2384), '$0.2384');
  assert.equal(minutesText(215), '3 h 35 min');
  assert.equal(minutesText(42), '42 min');
  assert.equal(secondsText(42.4), '42 s');
});
test('groupPaid and plainWords', () => {
  const e = normalizeSpend(SAMPLE).byId['battle-map-cannae'];
  const g = groupPaid(e.paid);
  assert.equal(g[0].seat, 'voice'); assert.equal(g[0].calls, 2); assert.ok(Math.abs(g[0].usd - 0.1584) < 1e-9);
  const w = plainWords(e);
  assert.match(w, /^Paid \$0\.24 \(\$0\.08 measured, \$0\.16 estimated\) against a cap of \$0\.90\./);
  assert.match(w, /3 h 35 min on GitHub runners \(free, worth \$1\.29/);
  assert.match(plainWords(normalizeSpend(SAMPLE).byId['p01-static']), /No paid calls recorded\. Rendering time is not recorded\./);
  assert.ok(!/[–—]|\.\.\./.test(w));
});
test('spendRoute: videos open their Spend tab, other work its own page', () => {
  const s = normalizeSpend(SAMPLE);
  assert.equal(spendRoute('battle-map-cannae', s), 'library/battle-map-cannae?tab=spend');
  assert.equal(spendRoute('boards-x', s), 'spend/boards-x');
});

const cat = normalize(JSON.parse(fs.readFileSync(new URL('../lib/catalog.fixture.json', import.meta.url))));
const ctx = { films: cat.films, styles: cat.styles, music: cat.music, docs: [] };
test('command bar: "spend" and "spend <film>"', () => {
  assert.equal(interpret('spend', ctx).route, 'spend');
  assert.equal(interpret('spend cannae', ctx).route, 'library/battle-map-cannae?tab=spend');
  assert.equal(interpret('cost of agincourt', ctx).route, 'library/battle-map-agincourt?tab=spend');
  assert.equal(interpret('spend zzqx', ctx).route, 'spend');
  assert.equal(interpret('show spend', ctx).route, 'spend');
  assert.ok(search('spend', ctx).some((r) => r.type === 'app' && r.id === 'spend'));
});

test('the real spend.json (when built) parses, adds up and covers every catalog film', () => {
  const p = new URL('../public/data/spend.json', import.meta.url);
  if (!fs.existsSync(p)) return;
  const raw = JSON.parse(fs.readFileSync(p));
  const s = normalizeSpend(raw);
  assert.ok(s.entries.length > 0);
  assert.deepEqual(checkTotals(s), []);
  const cp = new URL('../public/data/catalog.json', import.meta.url);
  if (fs.existsSync(cp)) for (const f of JSON.parse(fs.readFileSync(cp)).films) assert.ok(s.byId[f.id], `no spend entry for ${f.id}`);
  for (const e of s.entries) for (const l of e.paid) assert.ok(['measured', 'estimated', 'unflagged'].includes(l.basis));
  assert.ok(!/[–—…]|\.\.\./.test(JSON.stringify(raw)));
});
