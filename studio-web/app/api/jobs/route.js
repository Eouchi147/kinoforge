// GET /api/jobs  every studio job (films/studio/<id>/, the director pipeline): brief and status, newest first. Read only.
// One folder listing (contents API) plus raw file reads (no API quota). Folders starting with "_" are test jobs.
import { listDir, readRaw } from '@/lib/github';
export const dynamic = 'force-dynamic';

const json = (t) => { try { return t ? JSON.parse(t) : null; } catch { return null; } };

export async function GET() {
  let dirs;
  try { dirs = (await listDir('films/studio')).filter((d) => d.type === 'dir' && !d.name.startsWith('_')); }
  catch (e) { return Response.json({ jobs: [], error: e.message }, { status: 200, headers: { 'Cache-Control': 'no-store' } }); }
  const jobs = await Promise.all(dirs.slice(0, 40).map(async (d) => {
    const [status, brief] = await Promise.all([
      readRaw(`films/studio/${d.name}/status.json`, { revalidate: 15 }).then(json).catch(() => null),
      readRaw(`films/studio/${d.name}/brief.json`, { revalidate: 300 }).then(json).catch(() => null),
    ]);
    const stages = Object.fromEntries(Object.entries(status?.stages || {}).map(([k, v]) => [k, { state: v?.state || null, usd: v?.usd ?? null, spent: v?.spent ?? null }]));
    return {
      id: d.name, title: brief?.title || status?.title || d.name, line: brief?.line || status?.line || null, format: brief?.format || null, look: brief?.look || null,
      stage: status?.stage || null, state: status?.state || (brief ? 'queued' : null), message: status?.message || null,
      usd: status?.usd ?? 0, cap_usd: status?.cap_usd ?? brief?.cap_usd ?? null, stages, run_url: status?.run_url || null,
      approved_at: brief?.approved_at || status?.approved_at || null, updated: status?.updated_at || brief?.approved_at || null,
    };
  }));
  jobs.sort((a, b) => String(b.updated || '').localeCompare(String(a.updated || '')));
  return Response.json({ jobs }, { headers: { 'Cache-Control': 'public, max-age=10, s-maxage=15' } });
}
