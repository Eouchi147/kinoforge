// GET /api/job?id=<id>  the live state of a film job: films/studio/<id>/status.json (never cached), plus the newest
// film.yml run so the page can show a failure even if the pipeline died before writing a status.
import { readJSON, readRaw, workflowRuns } from '@/lib/github';
import { mediaUrl, downloadUrl } from '@/lib/media';
export const dynamic = 'force-dynamic';
const raw = (p) => readRaw(p, { revalidate: 0 }).then((t) => (t ? JSON.parse(t) : null)).catch(() => null);

export async function GET(req) {
  const id = new URL(req.url).searchParams.get('id') || '';
  if (!/^[a-z0-9][a-z0-9-]{0,60}$/.test(id)) return Response.json({ error: 'bad id' }, { status: 400 });
  try {
    const [status, brief, runs] = await Promise.all([
      readJSON(`films/studio/${id}/status.json`).catch(() => raw(`films/studio/${id}/status.json`)),   // the API can be rate limited: the
      readJSON(`films/studio/${id}/brief.json`).catch(() => raw(`films/studio/${id}/brief.json`)),     // public raw file (a few minutes old) then
      workflowRuns('film.yml', 10).catch(() => []),
    ]);
    const run = runs.find((r) => (r.display_title || '').includes(id) || (r.head_commit?.message || '').includes(id)) || null;
    const done = status?.stage === 'done' && status?.state === 'done';
    const film = done ? {
      preview: mediaUrl('films', `${id}-preview.mp4`), full: downloadUrl('films', `${id}.mp4`), poster: mediaUrl('films', `${id}-poster.jpg`), sheet: mediaUrl('films', `${id}-sheet.jpg`),
    } : null;
    return Response.json({
      id, brief, status, film,
      run: run ? { url: run.html_url, state: run.status, conclusion: run.conclusion, at: run.updated_at } : null,
    }, { headers: { 'Cache-Control': 'no-store' } });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 502 });
  }
}
