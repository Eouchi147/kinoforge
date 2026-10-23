// node --test studio-web/tests/*.test.mjs : the command bar and the catalog helpers (no server, no network).
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { interpret, search, parseCreate } from '../lib/commands.mjs';
import { normalize, tc } from '../lib/catalog.mjs';
import { assetUrl, resolveRelease, assetDownload } from '../lib/assets.mjs';

const raw = JSON.parse(fs.readFileSync(new URL('../lib/catalog.fixture.json', import.meta.url)));
const cat = normalize(raw);
const ctx = { films: cat.films, styles: cat.styles, music: cat.music, docs: [{ path: 'docs/manual/styles/cutaway-seasons-loop.md', title: 'Cutaway seasons loop' }, { path: 'docs/GUIDE.md', title: 'Guide' }] };

test('new cutaway film 9:16 fable opens Create preset', () => {
  const r = interpret('new cutaway film 9:16 fable', ctx);
  assert.equal(r.route, 'create?look=fable&line=cutaway&what=film&format=9%3A16');
});
test('a look alone implies the Cutaway line; multiword looks are found', () => {
  assert.deepEqual(parseCreate(['night', 'glow', 'loop'], ctx), { look: 'night-glow', what: 'loop', line: 'cutaway', format: '9:16' });
});
test('length, cap and no music', () => {
  const p = parseCreate(['battle', 'map', '150', 's', 'cap', '$3', 'no', 'music'], ctx);
  assert.deepEqual(p, { line: 'battle-map', length: 150, cap: 3, music: 'none', format: '16:9' });
});
test('open agincourt finds the film', () => {
  assert.equal(interpret('open agincourt', ctx).route, 'library/battle-map-agincourt');
});
test('show looks, show jobs', () => {
  assert.equal(interpret('show looks', ctx).route, 'styles/looks');
  assert.equal(interpret('show me the jobs', ctx).route, 'jobs');
});
test('manual seasons loop opens the page', () => {
  assert.equal(interpret('manual seasons loop', ctx).route, 'manual/docs/manual/styles/cutaway-seasons-loop.md');
  assert.match(interpret('manual something unknown', ctx).route, /^manual\?q=/);
});
test('compare two looks', () => {
  assert.equal(interpret('compare fable and stained glass', ctx).route, 'styles/compare/cutaway-fable/cutaway-stained-glass');
});
test('search finds films, looks and docs', () => {
  const r = search('fable', ctx);
  assert.ok(r.some((x) => x.type === 'look' && x.id === 'cutaway-fable'));
  assert.ok(search('cannae', ctx)[0].id === 'battle-map-cannae');
});
test('assets: both shapes', () => {
  assert.equal(assetUrl('/looks/fable-830.jpg'), '/looks/fable-830.jpg');
  assert.equal(assetUrl('/../etc'), null);
  assert.equal(assetUrl({ repo: 'Eouchi147/rc-render', release: 'stills', name: 'a.jpg' }), '/api/media?r=rc-render%3Astills&f=a.jpg');
  assert.equal(assetUrl({ repo: 'someone/else', release: 'x', name: 'a.jpg' }), null);
  assert.deepEqual(resolveRelease('kino-films'), { repo: 'Eouchi147/rc-render', tag: 'kino-films' });
  assert.equal(resolveRelease('evil:x'), null);
  assert.match(assetDownload({ repo: 'Eouchi147/rc-render', release: 'music', name: 'b.flac' }), /^https:\/\/github\.com\/Eouchi147\/rc-render\/releases\/download\/music\/b\.flac$/);
});
test('catalog normalizes and timecodes read well', () => {
  assert.ok(cat.looks.length >= 12 && cat.house.length >= 3);
  assert.equal(tc(72.34), '1:12.3');
});
test('the real catalog (when built) parses and its looks resolve to engine keys', () => {
  const p = new URL('../public/data/catalog.json', import.meta.url);
  if (!fs.existsSync(p)) return;
  const real = normalize(JSON.parse(fs.readFileSync(p)));
  assert.ok(real.films.length > 0);
  const c2 = { films: real.films, styles: real.styles, music: real.music, docs: [] };
  assert.match(interpret('new cutaway film fable', c2).route, /look=fable/);
  for (const f of real.films) assert.ok(f.id && f.title && ['16:9', '9:16'].includes(f.format));
});
test('search returns nothing for words nothing has (no bonus for a miss)', () => {
  assert.deepEqual(search('zzqx', ctx), []);
  assert.ok(!search('cutaway loop 9:16 fable', ctx).some((r) => r.type === 'film' && !/loop|cutaway/i.test(r.label + r.hint)));
});
