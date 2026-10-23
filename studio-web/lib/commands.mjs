// The command bar's brain. Pure functions, tested in tests/commands.test.mjs.
//   interpret(text, ctx)  plain words to ONE action ("new cutaway film 9:16 fable", "open agincourt", "show looks",
//                         "manual seasons loop", "compare fable and pixel"), or null
//   search(text, ctx)     everything that matches: apps, actions, films, styles, looks, manual pages
// ctx = { films: [{id,title,series,style,look}], styles: [{id,name,family}], docs: [{path,title}], music: [{id,title}] }
// A result is { type, id, label, hint, route }; route is the hash route the shell opens (see components/os/routes.js).

export const APPS = [
  { id: 'desk', name: 'Desk', hint: 'What needs you, what is running', words: 'desk home today start overview' },
  { id: 'library', name: 'Library', hint: 'Every film, watch and review', words: 'library films videos watch review catalogue catalog' },
  { id: 'create', name: 'Create', hint: 'Build a new film', words: 'create new make build brief director film' },
  { id: 'styles', name: 'Styles', hint: 'House styles and Cutaway looks', words: 'styles looks art directions boards compare' },
  { id: 'jobs', name: 'Jobs', hint: 'Builds and render runs', words: 'jobs builds runs renders running queue actions' },
  { id: 'sound', name: 'Sound', hint: 'Music library and sound tools', words: 'sound music score audio voice narration' },
  { id: 'spend', name: 'Spend', hint: 'What every video cost, line by line', words: 'spend spent spending cost costs paid money budget ledger receipts price' },
  { id: 'manual', name: 'Manual', hint: 'The guide and the AI manual', words: 'manual guide docs help instructions recipes how' },
  { id: 'settings', name: 'Settings', hint: 'Connections, money caps, lock', words: 'settings setup connections money caps keys lock passcode' },
];

const WHAT = [['film', /^(film|films|movie|video)$/], ['ad', /^(ad|ads|advert|advertisement|commercial|promo)$/], ['loop', /^(loop|loops|social|reel|reels|short|shorts|tiktok)$/], ['explainer', /^(explainer|explain|lesson|educational)$/]];
const LINES = [['cutaway', /^(cutaway|cut-away|cross-section)$/], ['battle-map', /^(battle-map|battlemap|battle|map|battles)$/], ['kinetic', /^(kinetic|type|typography|words)$/]];
const VERB_NEW = /^(new|make|create|start|build|begin)$/;
const VERB_OPEN = /^(open|play|watch|view|see)$/;
const VERB_SHOW = /^(show|list|go|goto|browse|all)$/;
const VERB_MANUAL = /^(manual|help|how|docs|doc|guide|recipe|instructions)$/;
const VERB_SPEND = /^(spend|spent|spending|cost|costs)$/;

export const norm = (s) => String(s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9:$.\s-]+/g, ' ').replace(/\s+/g, ' ').trim();
const words = (s) => norm(s).split(' ').filter(Boolean);
const slugify = (s) => norm(s).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const STOP = new Set(['a', 'an', 'the', 'of', 'to', 'for', 'me', 'my', 'please', 'in', 'on', 'with', 'and', 'film', 'films', 'page', 'pages', 'up', 'about']);

/** Score an item's text against query words: every word must prefix a word of the item (or appear in it). */
export function score(qWords, text) {
  const hay = words(text);
  if (!qWords.length || !hay.length) return 0;
  let s = 0;
  for (const q of qWords) {
    let best = 0;
    for (const h of hay) {
      if (h === q) { best = 4; break; }
      if (h.startsWith(q)) best = Math.max(best, 3);
      else if (q.length > 2 && h.includes(q)) best = Math.max(best, 1);
    }
    if (!best) return 0;
    s += best;
  }
  return s;
}

function bestMatch(qWords, items, text) {
  let top = null, topScore = 0;
  for (const it of items) { const sc = score(qWords, text(it)); if (sc > topScore) { top = it; topScore = sc; } }
  return top;
}

const looksOf = (ctx) => (ctx.styles || []).filter((s) => s.family === 'cutaway-look');

/** Find a look named anywhere in the words (multiword names like "night glow" too). Returns [look, rest words]. */
function takeLook(ws, ctx) {
  const looks = looksOf(ctx);
  for (let i = 0; i < ws.length; i++) {
    for (let n = Math.min(3, ws.length - i); n >= 1; n--) {
      const phrase = ws.slice(i, i + n).join('-');
      const l = looks.find((x) => x.id === phrase || x.key === phrase || slugify(x.name) === phrase);
      if (l) return [l, [...ws.slice(0, i), ...ws.slice(i + n)]];
    }
  }
  return [null, ws];
}

/** The create preset in plain words: what, line, format, look, length, cap, music. */
export function parseCreate(rest, ctx = {}) {
  let ws = [...rest];
  const p = {};
  const [look, ws2] = takeLook(ws, ctx); ws = ws2;
  if (look) p.look = look.key || look.id;
  for (let i = 0; i < ws.length; i++) {
    const w = ws[i], next = ws[i + 1] || '';
    if (/^(9:16|916|vertical|portrait|upright|phone)$/.test(w)) { p.format = '9:16'; continue; }
    if (/^(16:9|169|wide|landscape|horizontal|youtube)$/.test(w)) { p.format = '16:9'; continue; }
    const len = /^(\d{1,3})(s|sec|secs|seconds|m|min|mins|minutes)?$/.exec(w);
    if (len && (len[2] || /^(s|sec|secs|seconds|m|min|mins|minutes)$/.test(next))) {
      const unit = len[2] || next; const n = Number(len[1]);
      p.length = /^m/.test(unit) ? n * 60 : n; if (!len[2]) i++; continue;
    }
    const cap = /^\$(\d+(?:\.\d+)?)$/.exec(w) || (w === 'cap' && /^\$?\d+(\.\d+)?$/.test(next) ? [0, next.replace('$', '')] : null);
    if (cap) { p.cap = Number(cap[1]); if (w === 'cap') i++; continue; }
    if (w === 'no' && /^(music|score)$/.test(next)) { p.music = 'none'; i++; continue; }
    if (w === 'battle' && next === 'map') { p.line = 'battle-map'; i++; continue; }
    const wh = WHAT.find(([, re]) => re.test(w)); if (wh && !p.what) { p.what = wh[0]; continue; }
    const ln = LINES.find(([, re]) => re.test(w)); if (ln && !p.line) { p.line = ln[0]; continue; }
    const m = (ctx.music || []).find((x) => score([w], x.title) >= 3 && w.length > 3);
    if (m) { p.music = m.id; continue; }
  }
  if (p.look && !p.line) p.line = 'cutaway';
  if (p.what === 'loop' && !p.line) p.line = 'cutaway';
  if (p.what === 'loop' && !p.format) p.format = '9:16';
  if (p.line === 'kinetic') p.format = '9:16';
  if (p.line === 'battle-map') p.format = '16:9';
  return p;
}

export function createRoute(p) {
  const q = Object.entries(p).filter(([, v]) => v != null && v !== '').map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
  return q ? `create?${q}` : 'create';
}

function describeCreate(p, ctx) {
  const look = looksOf(ctx).find((l) => (l.key || l.id) === p.look);
  const what = { film: 'film', ad: 'ad', loop: 'social loop', explainer: 'explainer' }[p.what] || 'film';
  const line = { cutaway: 'Cutaway', 'battle-map': 'Battle Map', kinetic: 'Kinetic' }[p.line];
  return ['New', line, what, p.format, look ? `in ${look.name}` : null, p.length ? `${p.length} s` : null, p.cap ? `cap $${p.cap}` : null].filter(Boolean).join(' ');
}

const SHOW = [
  [/^(looks?|art|arts|directions?)$/, 'styles/looks', 'Show the Cutaway looks'],
  [/^(styles?|house)$/, 'styles', 'Show the house styles'],
  [/^(prototypes?|tests?|early)$/, 'styles/early', 'Show the early prototypes'],
  [/^(films?|library|videos?|movies?)$/, 'library', 'Show the library'],
  [/^(jobs?|builds?|runs?|renders?|running|queue)$/, 'jobs', 'Show jobs and render runs'],
  [/^(music|sound|sounds|score|audio)$/, 'sound', 'Show the sound room'],
  [/^(manual|guide|docs)$/, 'manual', 'Open the manual'],
  [/^(spend|spending|costs?)$/, 'spend', 'Show the spend'],
  [/^(money|settings|caps?|connections?|setup|lock)$/, 'settings', 'Open settings'],
  [/^(desk|home|today)$/, 'desk', 'Go to the desk'],
];

/** Plain words to one action, or null when the words are only a search. */
export function interpret(text, ctx = {}) {
  const ws = words(text);
  if (!ws.length) return null;
  const [v, ...rest] = ws;
  const films = ctx.films || [], styles = ctx.styles || [];

  if (VERB_NEW.test(v)) {
    const p = parseCreate(rest, ctx);
    return { type: 'action', id: 'create', label: describeCreate(p, ctx), hint: 'Opens Create with these choices', route: createRoute(p) };
  }
  if (v === 'use' || (v === 'try' && rest.length)) {
    const [look] = takeLook(rest, ctx);
    const st = look || bestMatch(rest.filter((w) => !STOP.has(w) && w !== 'look' && w !== 'style'), styles, (s) => `${s.name} ${s.id}`);
    if (st) return { type: 'action', id: 'use', label: `Start a film in ${st.name}`, hint: 'Opens Create preset', route: createRoute(st.start ? { line: st.start.line, format: st.start.format, look: st.start.look } : { look: st.key || st.id }) };
  }
  if (v === 'compare') {
    const looks = [...looksOf(ctx), ...styles.filter((s) => s.family !== 'cutaway-look')];
    let ws2 = rest.filter((w) => w !== 'and' && w !== 'with' && w !== 'vs' && w !== 'to');
    const [a, r1] = takeLook(ws2, ctx); const [b] = takeLook(r1, ctx);
    if (a && b) return { type: 'action', id: 'compare', label: `Compare ${a.name} and ${b.name}`, hint: 'Side by side', route: `styles/compare/${a.id}/${b.id}` };
    if (a) return { type: 'action', id: 'compare', label: `Compare ${a.name} with the reference`, hint: 'Side by side', route: `styles/compare/${a.id}/${looks.find((l) => l.id === 'reference') ? 'reference' : (looks.find((l) => l.id !== a.id) || a).id}` };
    return { type: 'action', id: 'compare', label: 'Compare two looks', hint: 'Pick two on the Styles app', route: 'styles/looks' };
  }
  if (VERB_MANUAL.test(v)) {
    const q = rest.filter((w) => !STOP.has(w) && !/^(to|do|i|we|make|does|is)$/.test(w)).join(' ');
    if (!q) return { type: 'app', id: 'manual', label: 'Open the manual', hint: 'The guide and the AI manual', route: 'manual' };
    const doc = bestMatch(words(q), ctx.docs || [], (d) => `${d.title} ${d.path.replace(/[/._-]+/g, ' ')}`);
    return doc
      ? { type: 'doc', id: doc.path, label: `Manual: ${doc.title}`, hint: doc.path, route: `manual/${doc.path}` }
      : { type: 'action', id: 'manual-search', label: `Search the manual for "${q}"`, hint: 'Full text', route: `manual?q=${encodeURIComponent(q)}` };
  }
  if (VERB_SPEND.test(v)) {
    const q = rest.filter((w) => !STOP.has(w) && !/^(on|for|of|per|what|did|was|much|how)$/.test(w));
    const f = q.length ? bestMatch(q, films, (x) => `${x.title} ${x.id} ${x.series || ''}`) : null;
    if (f) return { type: 'film', id: f.id, label: `Spend on ${f.title}`, hint: 'Every paid line and the render time', route: `library/${f.id}?tab=spend` };
    return { type: 'app', id: 'spend', label: 'Show the spend', hint: 'Totals, by month, by vendor, every video', route: 'spend' };
  }
  if (VERB_OPEN.test(v) || v === 'approve' || v === 'review') {
    const q = rest.filter((w) => !STOP.has(w));
    if (!q.length) return null;
    const f = bestMatch(q, films, (x) => `${x.title} ${x.id} ${x.series || ''}`);
    if (f) return { type: 'film', id: f.id, label: `${v === 'approve' || v === 'review' ? 'Review' : 'Open'} ${f.title}`, hint: f.series, route: `library/${f.id}${v === 'approve' || v === 'review' ? '?tab=review' : ''}` };
    const app = APPS.find((a) => score(q, `${a.name} ${a.words}`) > 0);
    if (app) return { type: 'app', id: app.id, label: `Open ${app.name}`, hint: app.hint, route: app.id };
    const st = bestMatch(q, styles, (s) => `${s.name} ${s.id}`);
    if (st) return { type: st.family === 'cutaway-look' ? 'look' : 'style', id: st.id, label: `Open ${st.name}`, hint: 'Styles', route: `styles/${st.id}` };
    return null;
  }
  if (VERB_SHOW.test(v)) {
    const q = rest.filter((w) => !STOP.has(w) && w !== 'me' && w !== 'the');
    if (!q.length) return null;
    const hit = SHOW.find(([re]) => re.test(q[q.length - 1]) && q.length === 1);
    if (hit) return { type: 'app', id: hit[1], label: hit[2], hint: '', route: hit[1] };
    const last = SHOW.find(([re]) => re.test(q[q.length - 1]));
    const filt = q.slice(0, last ? -1 : undefined).join(' ');
    if (last && last[1] === 'library' && filt) return { type: 'action', id: 'filter', label: `Show ${filt} films`, hint: 'Library, filtered', route: `library?q=${encodeURIComponent(filt)}` };
    if (last) return { type: 'app', id: last[1], label: last[2], hint: '', route: last[1] };
  }
  const app = APPS.find((a) => ws.length === 1 && (a.id === ws[0] || norm(a.name) === ws[0]));
  if (app) return { type: 'app', id: app.id, label: `Open ${app.name}`, hint: app.hint, route: app.id };
  return null;
}

/** Everything that matches the words, best first, at most `limit`. */
export function search(text, ctx = {}, limit = 12) {
  const q = words(text).filter((w) => !STOP.has(w) || words(text).length === 1);
  const out = [];
  const add = (base, bonus, r) => { if (base > 0) out.push({ ...r, sc: base + bonus }); };
  if (!q.length) {
    return [...APPS.map((a) => ({ type: 'app', id: a.id, label: a.name, hint: a.hint, route: a.id })), ...EXAMPLES].slice(0, limit + EXAMPLES.length);
  }
  for (const a of APPS) add(score(q, `${a.name} ${a.words}`), 1, { type: 'app', id: a.id, label: a.name, hint: a.hint, route: a.id });
  for (const f of ctx.films || []) add(score(q, `${f.title} ${f.id} ${f.series || ''} ${f.style || ''} ${f.look || ''}`), 2, { type: 'film', id: f.id, label: f.title, hint: [f.series, f.format].filter(Boolean).join(', '), route: `library/${f.id}` });
  for (const s of ctx.styles || []) add(score(q, `${s.name} ${s.id} ${s.family === 'cutaway-look' ? 'look cutaway' : 'style house'}`), 2, { type: s.family === 'cutaway-look' ? 'look' : 'style', id: s.id, label: s.name, hint: s.family === 'cutaway-look' ? 'Cutaway look' : 'House style', route: `styles/${s.id}` });
  for (const d of ctx.docs || []) add(score(q, `${d.title} ${d.path.replace(/[/._-]+/g, ' ')}`), 0, { type: 'doc', id: d.path, label: d.title, hint: d.path.replace(/^docs\//, ''), route: `manual/${d.path}` });
  for (const m of ctx.music || []) add(score(q, `${m.title} music`), 0, { type: 'music', id: m.id, label: m.title, hint: 'Music library', route: 'sound' });
  out.sort((a, b) => b.sc - a.sc);
  return out.slice(0, limit).map(({ sc, ...r }) => r);
}

export const EXAMPLES = [
  { type: 'example', id: 'ex1', label: 'new cutaway loop 9:16 fable', hint: 'Try it', fill: 'new cutaway loop 9:16 fable' },
  { type: 'example', id: 'ex2', label: 'open agincourt', hint: 'Try it', fill: 'open agincourt' },
  { type: 'example', id: 'ex3', label: 'compare fable and night glow', hint: 'Try it', fill: 'compare fable and night glow' },
  { type: 'example', id: 'ex4', label: 'manual seasons loop', hint: 'Try it', fill: 'manual seasons loop' },
];
