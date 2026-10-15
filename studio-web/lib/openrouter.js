// OpenRouter: always the best available model, chosen from the live model list (blueprint: "How it always picks the best model").
const FALLBACK = ['anthropic/claude-opus-5.5', 'openai/gpt-6.1-sol', 'google/gemini-4-argon'];
let cache = { at: 0, models: FALLBACK };

export async function bestModels({ needImages = false, maxPromptPerM = 6 } = {}) {
  if (Date.now() - cache.at < 3600e3) return cache.models;
  try {
    const r = await fetch('https://openrouter.ai/api/v1/models', { next: { revalidate: 3600 } });
    const { data } = await r.json();
    const ok = data.filter((m) => {
      const ins = m.architecture?.input_modalities || [];
      const params = m.supported_parameters || [];
      const price = Number(m.pricing?.prompt || 0) * 1e6;
      return ins.includes('text') && (!needImages || ins.includes('image')) && (params.includes('structured_outputs') || params.includes('response_format'))
        && !m.expiration_date && !m.id.endsWith(':free') && price > 0 && price <= maxPromptPerM;
    });
    const score = (m) => m.benchmarks?.artificial_analysis?.intelligence_index ?? -1;
    const ranked = ok.filter((m) => score(m) >= 0 && !m.id.includes(':')).sort((a, b) => score(b) - score(a)).map((m) => m.id);
    // fallbacks from different providers, so one provider's outage never stops the director
    const pick = [], seen = new Set();
    for (const id of ranked) { const p = id.split('/')[0]; if (!seen.has(p)) { pick.push(id); seen.add(p); } if (pick.length === 3) break; }
    cache = { at: Date.now(), models: pick.length ? pick : FALLBACK };
  } catch { cache = { at: Date.now(), models: FALLBACK }; }
  return cache.models;
}

export async function chat({ messages, schema, name = 'reply', maxTokens = 1800 }) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw Object.assign(new Error('no-key'), { code: 'no-key' });
  const models = await bestModels({ needImages: true });
  const r = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json', 'HTTP-Referer': 'https://kinoforge.studio', 'X-Title': 'KINOFORGE Studio' },
    body: JSON.stringify({
      models, messages, max_tokens: maxTokens,
      response_format: { type: 'json_schema', json_schema: { name, strict: true, schema } },
      provider: { require_parameters: true },
    }),
  });
  const j = await r.json();
  if (!r.ok) throw Object.assign(new Error(j?.error?.message || `OpenRouter ${r.status}`), { code: r.status === 402 ? 'credits' : 'upstream' });
  const text = j.choices?.[0]?.message?.content || '{}';
  return { data: JSON.parse(text), model: j.model };
}
