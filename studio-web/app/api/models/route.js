// GET /api/models — the live model market, compacted: top models by published intelligence, with prices and abilities.
// Used to choose the director's head and workers, and by the budget ledger. Calls OpenRouter's free endpoints only.
export const dynamic = 'force-dynamic';

export async function GET() {
  const key = process.env.OPENROUTER_API_KEY;
  const [{ data }, keyInfo] = await Promise.all([
    fetch('https://openrouter.ai/api/v1/models').then((r) => r.json()),
    key ? fetch('https://openrouter.ai/api/v1/key', { headers: { Authorization: `Bearer ${key}` } }).then((r) => r.json()).catch(() => null) : null,
  ]);
  const row = (m) => ({
    id: m.id,
    iq: m.benchmarks?.artificial_analysis?.intelligence_index ?? null,
    in: +(Number(m.pricing?.prompt || 0) * 1e6).toFixed(3),
    out: +(Number(m.pricing?.completion || 0) * 1e6).toFixed(3),
    ctx: m.context_length,
    mods: (m.architecture?.input_modalities || []).join(','),
    tools: (m.supported_parameters || []).includes('tools'),
    json: (m.supported_parameters || []).includes('structured_outputs'),
    created: m.created,
  });
  const live = data.filter((m) => !m.expiration_date && !m.id.startsWith('openrouter/'));
  const byIq = (l) => l.map(row).sort((a, b) => (b.iq ?? -1) - (a.iq ?? -1) || b.created - a.created);
  return Response.json({
    account: keyInfo?.data ? { usage: keyInfo.data.usage, limit: keyInfo.data.limit, limit_remaining: keyInfo.data.limit_remaining, is_free_tier: keyInfo.data.is_free_tier } : null,
    paid: byIq(live.filter((m) => !m.id.includes(':'))).slice(0, 30),
    free: byIq(live.filter((m) => m.id.endsWith(':free'))).slice(0, 25),
  });
}
