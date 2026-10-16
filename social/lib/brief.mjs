// social/lib/brief.mjs: pure helpers shared by the social templates (browser) and the social tools (Node).
// No DOM, no file system: the same rules run on screen, in the captions and in the batch check.

export const FRAME = { w: 1080, h: 1920 };

// Phone safe zone for words. TikTok, Reels, Shorts and Facebook Reels draw their tabs across the top, the caption and
// account line across the bottom, and the like, comment and share column down the right. Pictures may run under them;
// words may not. Fractions of the frame, plus a left margin so nothing kisses the edge.
export const SAFE = { top: 0.10, bottom: 0.20, right: 0.12, left: 72 / 1080 };
export const safeBox = (w = FRAME.w, h = FRAME.h) => ({
  x0: Math.round(SAFE.left * w), x1: Math.round(w * (1 - SAFE.right)), y0: Math.round(h * SAFE.top), y1: Math.round(h * (1 - SAFE.bottom)),
});

// House style (Sam): no em dash, no en dash, no "..." and no ellipsis character, on screen or in captions.
const BANNED = [[/\u2014/, 'an em dash'], [/\u2013/, 'an en dash'], [/\.\.\./, '"..."'], [/\u2026/, 'an ellipsis']];
export function styleProblems(text, where = 'text') {
  const out = [];
  for (const [re, what] of BANNED) if (re.test(String(text ?? ''))) out.push(`${where} has ${what}: ${JSON.stringify(text)}`);
  return out;
}

// A batch (it has "videos") or a single brief, to the brief of one video. Batch defaults fill what an entry leaves out.
export function resolveVideo(doc, id) {
  if (!doc || !Array.isArray(doc.videos)) return { ...doc };
  const v = id ? doc.videos.find((x) => x.id === id) : doc.videos[0];
  if (!v) throw new Error(`video "${id}" is not in batch ${doc.client}/${doc.batch}`);
  return { client: doc.client, batch: doc.batch, ...(doc.defaults || {}), ...v };
}

// Every word a video puts on screen, with where it comes from (for the style check).
export function screenWords(brief, brand) {
  const c = brief.card || {};
  return [['eyebrow', c.eyebrow], ['title', c.title], ['body', c.body], ['fact', (c.fact || [])[0]], ['fact label', (c.fact || [])[1]],
    ['site', brand.site], ['area', brand.area], ['cta', brief.cta || brand.cta]].filter(([, v]) => v != null && v !== '');
}

// Problems with a brief before anything is rendered: missing fields, house style, the card copy limits from
// smartmount tools/cards.data.js (title about 34 characters, body about 90).
export function briefProblems(brief, brand, { templates = null, photos = null } = {}) {
  const out = [], c = brief.card || {};
  if (!brief.client) out.push('no client');
  if (!brief.template) out.push('no template');
  else if (templates && !templates.includes(brief.template)) out.push(`unknown template "${brief.template}"`);
  if (!c.title) out.push('no card.title');
  if (!brief.photo) out.push('no photo');
  else if (photos && !photos.includes(brief.photo)) out.push(`photo "${brief.photo}" is not in the client's media.json`);
  if (c.title && c.title.length > 36) out.push(`title is ${c.title.length} characters (the card limit is about 34): shorten the words`);
  if (c.body && c.body.length > 92) out.push(`body is ${c.body.length} characters (the card limit is about 90): shorten the words`);
  if (c.fact && (!Array.isArray(c.fact) || c.fact.length !== 2)) out.push('card.fact must be [number, words]');
  for (const [where, text] of screenWords(brief, brand)) out.push(...styleProblems(text, where));
  return out;
}

// The fact number. A plain number with a unit ("42\"", "10 min", "1.6x", "3 ft") counts up; anything else
// ("400x300", "0mm", "1 day") is revealed whole, because counting to 0 or 1 says nothing.
export function parseFact(s) {
  const text = String(s ?? '').trim();
  const m = /^(\d+(?:[.,]\d+)?)(.*)$/.exec(text);
  if (!m || /\d/.test(m[2])) return { text, count: false };
  const sep = m[1].includes(',') ? ',' : '.';
  const value = parseFloat(m[1].replace(',', '.'));
  const decimals = (m[1].split(/[.,]/)[1] || '').length;
  return { text, count: value >= 2 || decimals > 0, value, decimals, sep, num: m[1], suffix: m[2] };
}
// The fact's text at progress p (0 to 1) of its count.
export function factAt(f, p) {
  if (!f.count) return f.text;
  let s = (f.value * Math.max(0, Math.min(1, p))).toFixed(f.decimals);
  if (f.sep === ',') s = s.replace('.', ',');
  return s + f.suffix;
}
