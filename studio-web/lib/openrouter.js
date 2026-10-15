// OpenRouter: the best model the budget allows, chosen from the live model list.
// KF_BUDGET = "free" (default: only :free models), "low" (free first, then models under $0.50 per million tokens), "best".
const FALLBACK = { free: ['deepseek/deepseek-chat-v3.1:free', 'meta-llama/llama-4-maverick:free', 'google/gemini-2.0-flash-exp:free'], low: ['deepseek/deepseek-chat-v3.1:free'], best: ['anthropic/claude-opus-5.5', 'openai/gpt-6.1-sol', 'google/gemini-4-argon'] };
const budget = () => (process.env.KF_BUDGET || 'free').toLowerCase();
let cache = { at: 0, key: '', models: null };

export async function bestModels({ needImages = false } = {}) {
  const b = budget(), key = b + needImages;
  if (cache.models && cache.key === key && Date.now() - cache.at < 3600e3) return cache.models;
  let models = FALLBACK[b] || FALLBACK.free;
  try {
    const r = await fetch('https://openrouter.ai/api/v1/models', { next: { revalidate: 3600 } });
    const { data } = await r.json();
    const price = (m) => Number(m.pricing?.prompt || 0) * 1e6 + Number(m.pricing?.completion || 0) * 1e6 / 4;
    const score = (m) => m.benchmarks?.artificial_analysis?.intelligence_index ?? (m.context_length > 100000 ? 10 : 0);
    const usable = data.filter((m) => {
      const ins = m.architecture?.input_modalities || [];
      return ins.includes('text') && (!needImages || ins.includes('image')) && !m.expiration_date && !m.id.includes('openrouter/');
    });
    const free = usable.filter((m) => m.id.endsWith(':free') || price(m) === 0);
    const cheap = usable.filter((m) => !m.id.includes(':') && price(m) > 0 && price(m) < 0.5);
    const top = usable.filter((m) => !m.id.includes(':') && Number(m.pricing?.prompt || 0) * 1e6 <= 6);
    const rank = (list) => list.sort((a, b) => score(b) - score(a)).map((m) => m.id);
    const diverse = (ids, n) => { const out = [], seen = new Set(); for (const id of ids) { const p = id.split('/')[0]; if (!seen.has(p)) { out.push(id); seen.add(p); } if (out.length === n) break; } return out; };
    const pick = b === 'best' ? diverse(rank(top), 3) : b === 'low' ? [...diverse(rank(free), 2), ...diverse(rank(cheap), 1)] : diverse(rank(free), 3);
    if (pick.length) models = pick;
  } catch {}
  cache = { at: Date.now(), key, models };
  return models;
}

function parseJSON(text) {
  try { return JSON.parse(text); } catch {}
  const a = text.indexOf('{'), b = text.lastIndexOf('}');
  if (a >= 0 && b > a) return JSON.parse(text.slice(a, b + 1));
  throw new Error('The model did not return JSON');
}

export async function chat({ messages, schema, name = 'reply', maxTokens = 1800 }) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw Object.assign(new Error('no-key'), { code: 'no-key' });
  const models = await bestModels({ needImages: false });
  const headers = { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json', 'HTTP-Referer': 'https://kinoforge-studio.vercel.app', 'X-Title': 'KINOFORGE Studio' };
  const call = (body) => fetch('https://openrouter.ai/api/v1/chat/completions', { method: 'POST', headers, body: JSON.stringify(body) });
  // 1) strict JSON schema where the model supports it; 2) otherwise the schema as instructions and JSON parsed from the text
  let r = await call({ models, messages, max_tokens: maxTokens, response_format: { type: 'json_schema', json_schema: { name, strict: true, schema } } });
  let j = await r.json();
  if (!r.ok || !j.choices?.[0]?.message?.content) {
    const hint = { role: 'system', content: 'Reply with ONE JSON object only (no prose, no code fences) matching this JSON schema:\n' + JSON.stringify(schema) };
    r = await call({ models, messages: [...messages, hint], max_tokens: maxTokens });
    j = await r.json();
  }
  if (!r.ok) throw Object.assign(new Error(j?.error?.message || `OpenRouter ${r.status}`), { code: r.status === 402 ? 'credits' : r.status === 429 ? 'limit' : 'upstream' });
  return { data: parseJSON(j.choices?.[0]?.message?.content || '{}'), model: j.model };
}
