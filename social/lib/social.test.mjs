// node --test social/lib/social.test.mjs   : the social lane's pure rules (no browser, no network, no fees)
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseFact, factAt, styleProblems, resolveVideo, briefProblems, safeBox } from './brief.mjs';
import { captions, LIMITS } from './captions.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const brand = read('social/clients/smartmount/brand.json');
const batch = read('social/batches/smartmount/2026-12/batch.json');

test('the fact counts up only when counting means something', () => {
  assert.equal(factAt(parseFact('42"'), 0.5), '21"');
  assert.equal(factAt(parseFact('42"'), 1), '42"');
  assert.equal(factAt(parseFact('1.6x'), 0.5), '0.8x');
  assert.equal(factAt(parseFact('10 min'), 1), '10 min');
  assert.equal(factAt(parseFact('1,6'), 1), '1,6');
  for (const s of ['400x300', '0', '1', '0mm', '1 day']) assert.equal(parseFact(s).count, false, s);
});

test('house style: no em dash, no en dash, no "..." or ellipsis', () => {
  assert.equal(styleProblems('Your TV is too high.').length, 0);
  assert.equal(styleProblems('In wall power - rated kit').length, 0);   // a hyphen is allowed
  for (const bad of ['a \u2014 b', 'a \u2013 b', 'wait...', 'wait\u2026']) assert.equal(styleProblems(bad).length, 1, bad);
});

test('safe box is rule R-2-08: x 0.11 to 0.78, y 0.15 to 0.65 of 1080x1920', () => {
  assert.deepEqual(safeBox(), { x0: 119, x1: 842, y0: 288, y1: 1248 });
});

test('a batch entry resolves to a full brief; an unknown id is refused', () => {
  const b = resolveVideo(batch, 'v01-tip-height');
  assert.equal(b.client, 'smartmount'); assert.equal(b.batch, '2026-12'); assert.equal(b.card.title, 'Your TV is too high.');
  assert.throws(() => resolveVideo(batch, 'nope'));
});

test('every video in the first batch passes the brief rules and fits every platform', () => {
  const photos = read('social/clients/smartmount/media/media.json').photos.map((p) => p.file);
  assert.equal(batch.videos.length, 12);
  for (const v of batch.videos) {
    const b = resolveVideo(batch, v.id);
    assert.deepEqual(briefProblems(b, brand, { templates: ['card-motion', 'bento', 'type-motion'], photos }), [], v.id);
    const c = captions(b, brand, { music: 'ai' });
    assert.ok(c.checks.ok, v.id + ': ' + c.checks.problems.join('; '));
    assert.ok(c.youtube.title.length <= LIMITS.youtube.title);
    assert.ok((c.instagram.caption.match(/#\w+/g) || []).length <= LIMITS.instagram.hashtags);
  }
});

test('captions open with the hook on its own line and use only the card and the brand', () => {
  for (const v of batch.videos) {
    const c = captions(resolveVideo(batch, v.id), brand, { music: 'ai' });
    for (const p of ['tiktok', 'instagram', 'facebook']) assert.equal(c[p].caption.split('\n')[0], v.card.title, `${v.id} ${p}`);
    assert.ok(c.tiktok.caption.split('\n')[0].length <= LIMITS.tiktok.firstLine);
  }
  const c = captions(resolveVideo(batch, 'v01-tip-height'), brand, { music: 'none' });
  assert.match(c.tiktok.caption, /^Your TV is too high\.\nEye level means the centre of the screen, sitting down\. 42" to the centre, seated\./);
  assert.match(c.instagram.caption, /Book online at smartmount\.ca/);
  assert.equal(c.youtube.title, 'Your TV is too high. | Smart Mount');
  assert.equal(c.disclosure.ai_label, false);
  assert.doesNotMatch(JSON.stringify(c), /\$|\d+ ?%|stars?\b|rated \d/i);   // no prices, discounts or ratings slipped in
});
