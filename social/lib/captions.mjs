#!/usr/bin/env node
// social/lib/captions.mjs: each platform's caption for one video, built from the brief and brand.json in code (no AI).
//
//   node social/lib/captions.mjs social/batches/smartmount/2026-12 v01-tip-height [--out file.json]
//   node social/lib/captions.mjs social/templates/card-motion/sample.json            (a single brief)
//   import { captions } from './captions.mjs'; captions(brief, brand, { music })     (library)
//
// Words come only from the card (title, body, fact) and the brand (cta line, sign-off, hashtags): no claims are added,
// no prices, ratings, counts or results. House style is checked on every caption: no em or en dash, no "..." or ellipsis.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolveVideo, styleProblems } from './brief.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

// Platform limits (the one place to update them; checked by the coordinator on 16 Oct 2026). Characters count whole
// captions, hashtags included.
//  TikTok: the Content Posting API caps video captions at 2,200 characters
//    (socialk.it/de/tools/social-media-character-limits, verified June 2026).
//  Instagram: 2,200 characters and 5 hashtags per post or Reel, phased in since December 2025 (socialsamosa.com, 19 Dec 2025).
//  YouTube: title 100, description 5,000; the first 3 hashtags of the description show with the title.
//  Facebook: about 125 characters show on mobile before "See more"; kept to 2,200 and 3 hashtags like the others.
// Every caption opens with the hook (the card's title) alone on its first line. TikTok's first line stays under about
// 100 characters so its caption overlay stays short, inside the bottom 35% of the frame (rule R-2-08 keeps our words out of it).
export const LIMITS = {
  tiktok: { caption: 2200, hashtags: 5, firstLine: 100 },
  instagram: { caption: 2200, hashtags: 5 },
  youtube: { title: 100, description: 5000, hashtags: 3 },
  facebook: { caption: 2200, hashtags: 3, preview: 125 },
};
export const PLATFORMS = Object.keys(LIMITS);
const TAG = /^#[A-Za-z0-9_]{2,40}$/;

// "42\"" + "to the centre, seated" -> '42" to the centre, seated.'; a brief may give caption_fact to word it differently.
export function factLine(brief) {
  if (brief.caption_fact) return brief.caption_fact;
  const f = (brief.card || {}).fact; if (!f) return '';
  const s = `${f[0]} ${f[1]}`.trim(); return /[.!?]$/.test(s) ? s : s + '.';
}
function tags(brief, brand, n) {
  const all = [...(brief.hashtags || []), ...(brand.hashtags || [])], out = [];
  for (const t of all) if (TAG.test(t) && !out.some((x) => x.toLowerCase() === t.toLowerCase())) out.push(t);
  return out.slice(0, n);
}
const clip = (s, n) => (s.length <= n ? s : s.slice(0, n).replace(/\s+\S*$/, ''));   // never cut a word, never add "..."

export function captions(brief, brand, { music = 'none' } = {}) {
  const c = brief.card || {}, cap = brand.captions || {};
  const cta = cap.cta || `${brand.cta} at ${brand.site}`, sign = cap.sign || `${brand.name}, ${brand.area}.`;
  const hook = c.title || '', rest = [c.body, factLine(brief)].filter(Boolean).join(' ');
  const want = new Set(brief.platforms || PLATFORMS), out = {}, problems = [];
  const text = (parts) => parts.filter(Boolean).join('\n\n');   // never truncated: too long is reported below and fails the build
  // the hook alone on the first line, the tip under it, then the call to action and the hashtags
  if (want.has('tiktok')) { const L = LIMITS.tiktok; out.tiktok = { caption: text([`${hook}\n${rest}`, cta, tags(brief, brand, L.hashtags).join(' ')]) }; }
  if (want.has('instagram')) { const L = LIMITS.instagram; out.instagram = { caption: text([[hook, c.body, factLine(brief)].filter(Boolean).join('\n'), `${cta}\n${sign}`, tags(brief, brand, L.hashtags).join(' ')]) }; }
  if (want.has('youtube')) {
    const L = LIMITS.youtube, suffix = cap.youtube_suffix ?? ` | ${brand.name}`;
    const title = hook.length + suffix.length <= L.title ? hook + suffix : clip(hook, L.title);   // the title is the hook
    out.youtube = { title, description: text([rest, `${cta}\n${sign}`, tags(brief, brand, L.hashtags).join(' ')]) };
  }
  if (want.has('facebook')) { const L = LIMITS.facebook; out.facebook = { caption: text([`${hook}\n${rest}`, `${cta}\n${sign}`, tags(brief, brand, L.hashtags).join(' ')]) }; }
  // checks: house style, limits, hashtag counts, the hook first
  for (const [p, o] of Object.entries(out)) for (const [k, v] of Object.entries(o)) {
    problems.push(...styleProblems(v, `${p} ${k}`));
    const lim = LIMITS[p][k === 'caption' ? 'caption' : k]; if (lim && v.length > lim) problems.push(`${p} ${k} is ${v.length} characters (limit ${lim})`);
    const n = (v.match(/#[A-Za-z0-9_]+/g) || []).length; if (n > LIMITS[p].hashtags) problems.push(`${p} ${k} has ${n} hashtags (limit ${LIMITS[p].hashtags})`);
    if (k === 'caption' && v.split('\n')[0] !== hook) problems.push(`${p} caption does not open with the hook`);
  }
  if (out.tiktok && out.tiktok.caption.split('\n')[0].length > LIMITS.tiktok.firstLine) problems.push(`tiktok first line is over ${LIMITS.tiktok.firstLine} characters`);
  if (out.facebook && hook.length > LIMITS.facebook.preview) problems.push(`the hook is longer than Facebook's ${LIMITS.facebook.preview} character preview`);
  return {
    id: brief.id, client: brief.client, batch: brief.batch || null, template: brief.template, card: c.name || null, ...out,
    disclosure: {
      ai_label: false,
      why: 'Real install photos and words set in code; no AI images, faces or voices. ' + (music === 'ai' ? 'The music is instrumental, generated with AI (Lyria).' : 'No music generated.'),
    },
    checks: { ok: problems.length === 0, problems, limits: LIMITS },
  };
}

// ---------- CLI
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2), oi = args.indexOf('--out'), out = oi >= 0 ? args.splice(oi, 2)[1] : null;
  const [src, id] = args;
  if (!src) { console.error('usage: captions.mjs <batch dir | brief.json> [video id] [--out file]'); process.exit(2); }
  const file = fs.statSync(src).isDirectory() ? path.join(src, 'batch.json') : src;
  const doc = JSON.parse(fs.readFileSync(file, 'utf8'));
  const brief = resolveVideo(doc, id);
  const brand = JSON.parse(fs.readFileSync(path.join(ROOT, 'social', 'clients', brief.client, 'brand.json'), 'utf8'));
  const music = doc.music && doc.music.enabled !== false && doc.music.prompt ? 'ai' : 'none';
  const res = captions(brief, brand, { music });
  const json = JSON.stringify(res, null, 1);
  if (out) { fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true }); fs.writeFileSync(out, json + '\n'); console.log('wrote', out); } else console.log(json);
  if (!res.checks.ok) { console.error('caption problems:\n  ' + res.checks.problems.join('\n  ')); process.exit(1); }
}
