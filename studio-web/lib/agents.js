// The director's agent core: seats filled live from OpenRouter, a fallback chain per seat, a timeout per call,
// and a ledger that counts every cent against the caps in crew.json. Mirrored in harness/director/agents.py.
import CREW from './crew.json';

const API = 'https://openrouter.ai/api/v1';
const KEY = () => process.env.OPENROUTER_API_KEY;
const now = () => Date.now();
let MARKET = { at: 0, byId: null };

// ---------------------------------------------------------------- the market: what exists, what it costs, what it can do
export async function market() {
  if (MARKET.byId && now() - MARKET.at < 3600e3) return MARKET.byId;
  try {
    const { data } = await fetch(`${API}/models`, { signal: AbortSignal.timeout(8000) }).then((r) => r.json());
    const byId = {};
    for (const m of data) {
      if (m.expiration_date || m.id.startsWith('openrouter/')) continue;
      const p = m.supported_parameters || [];
      byId[m.id] = {
        id: m.id, iq: m.benchmarks?.artificial_analysis?.intelligence_index ?? null,
        in: Number(m.pricing?.prompt || 0) * 1e6, out: Number(m.pricing?.completion || 0) * 1e6,
        mods: m.architecture?.input_modalities || [], json: p.includes('structured_outputs'), created: m.created,
      };
    }
    MARKET = { at: now(), byId };
  } catch { /* keep the last market, or none: seats then use their `prefer` lists */ }
  return MARKET.byId;
}

// A seat's chain: the smartest models inside its price ceiling and abilities, one per provider, best first.
export async function seat(name) {
  const s = CREW.seats[name]; const byId = await market();
  if (!byId) return s.prefer;
  const fits = (m) => s.needs.every((n) => m.mods.includes(n)) && (s.free ? m.id.endsWith(':free') : !m.id.includes(':') && m.in > 0 && m.in <= s.max_in && m.out <= s.max_out);
  const ranked = Object.values(byId).filter(fits).filter((m) => m.iq != null).sort((a, b) => b.iq - a.iq || b.created - a.created);
  const out = [], seen = new Set();
  for (const m of ranked) { const p = m.id.split('/')[0]; if (!seen.has(p)) { out.push(m.id); seen.add(p); } if (out.length === s.n) break; }
  for (const id of s.prefer) if (byId[id] && !out.includes(id) && out.length < s.n + 1) out.push(id);   // known-good backups
  return out.length ? out : s.prefer;
}

// ---------------------------------------------------------------- money
export function ledger(capUsd = CREW.caps.turn_usd) { return { cap: capUsd, total: 0, calls: [] }; }
export async function account() {
  try {
    const { data } = await fetch(`${API}/key`, { headers: { Authorization: `Bearer ${KEY()}` }, signal: AbortSignal.timeout(6000) }).then((r) => r.json());
    return { usage: data.usage, today: data.usage_daily ?? null, remaining: data.limit_remaining ?? null, limit: data.limit ?? null };
  } catch { return null; }
}
const estimate = (m, inTok, outTok) => m ? (inTok * m.in + outTok * m.out) / 1e6 : 0;

// ---------------------------------------------------------------- one call, with fallbacks
export function parseJSON(text) {
  const t = String(text || '');
  for (let a = t.indexOf('{'); a !== -1; a = t.indexOf('{', a + 1)) {
    let depth = 0, inStr = false, esc = false;
    for (let i = a; i < t.length; i++) {
      const c = t[i];
      if (inStr) { if (esc) esc = false; else if (c === '\\') esc = true; else if (c === '"') inStr = false; continue; }
      if (c === '"') inStr = true; else if (c === '{') depth++; else if (c === '}' && --depth === 0) { try { return JSON.parse(t.slice(a, i + 1)); } catch { break; } }
    }
  }
  throw new Error('no JSON object in the reply');
}

const cached = (messages, model) => (model.startsWith('anthropic/') || model.startsWith('google/'))
  ? messages.map((m, i) => i === 0 && m.role === 'system' ? { role: 'system', content: [{ type: 'text', text: m.content, cache_control: { type: 'ephemeral' } }] } : m)
  : messages;

/** Ask a seat. Tries each model of the seat in turn (then the free seat, if allowed) until one returns valid JSON.
 *  deadline: epoch ms by which we must be done (keeps the web request under its time limit). */
export async function ask(seatName, { messages, schema, name = 'reply', maxTokens = 1500, deadline = now() + 55e3, book = ledger(), allowFree = true, validate, only }) {
  const byId = (await market()) || {};
  const s = CREW.seats[seatName];
  const chain = only ? [[seatName, only]] : (await seat(seatName)).map((id) => [seatName, id]);
  if (allowFree && !only && seatName !== 'free') for (const id of await seat('free')) chain.push(['free', id]);
  const inTok = Math.ceil(JSON.stringify(messages).length / 3.5);
  const errors = [];
  for (let k = 0; k < chain.length; k++) {
    const [seatUsed, model, loose] = chain[k];
    const left = deadline - now();
    if (left < 8e3) { errors.push('out of time'); break; }
    const m = byId[model];
    if (book.total + estimate(m, inTok, maxTokens) > book.cap) { errors.push(`${model}: over the cap`); continue; }
    const strict = m?.json !== false && !loose;
    const body = {
      model, max_tokens: maxTokens, usage: { include: true },
      messages: strict ? cached(messages, model) : [...cached(messages, model), { role: 'system', content: 'Reply with ONE JSON object only (no prose, no code fences) matching this JSON schema:\n' + JSON.stringify(schema) }],
      ...(strict ? { response_format: { type: 'json_schema', json_schema: { name, strict: true, schema } } } : {}),
    };
    const t0 = now();
    try {
      const r = await fetch(`${API}/chat/completions`, {
        method: 'POST', body: JSON.stringify(body), signal: AbortSignal.timeout(Math.min((CREW.seats[seatUsed].timeout_s || s.timeout_s) * 1e3, left - 4e3)),
        headers: { Authorization: `Bearer ${KEY()}`, 'Content-Type': 'application/json', 'HTTP-Referer': 'https://kinoforge-studio.vercel.app', 'X-Title': 'KINOFORGE director' },
      });
      const j = await r.json();
      const cost = Number(j.usage?.cost ?? estimate(m, j.usage?.prompt_tokens || inTok, j.usage?.completion_tokens || maxTokens));
      book.total += r.ok ? cost : 0;
      if (!r.ok) {
        errors.push(`${model}: ${r.status} ${j.error?.message || ''}`.slice(0, 160)); if (r.status === 402) break;
        if (r.status === 400 && strict) chain.splice(k + 1, 0, [seatUsed, model, true]);   // schema refused: same model, schema as instructions
        continue;
      }
      const data = parseJSON(j.choices?.[0]?.message?.content);
      const problem = validate?.(data);
      book.calls.push({ seat: seatUsed, model: j.model || model, usd: +cost.toFixed(5), ms: now() - t0, ok: !problem });
      if (problem) { errors.push(`${model}: ${problem}`); continue; }
      return { data, model: j.model || model, seat: seatUsed, cost };
    } catch (e) {
      book.calls.push({ seat: seatUsed, model, usd: 0, ms: now() - t0, ok: false });
      errors.push(`${model}: ${e.name === 'TimeoutError' ? 'too slow' : e.message}`.slice(0, 160));
    }
  }
  throw Object.assign(new Error('every model in the chain failed: ' + errors.join(' | ')), { code: errors.some((e) => / 402 /.test(e)) ? 'credits' : 'upstream', errors });
}

/** Ask several crew models the same thing in parallel; returns every draft that came back. */
export async function fanOut(seatName, n, args) {
  const chain = (await seat(seatName)).slice(0, n);
  const runs = chain.map((id) => ask(seatName, { ...args, allowFree: false, only: id }).catch(() => null));
  return (await Promise.all(runs)).filter(Boolean);
}
