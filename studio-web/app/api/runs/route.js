// GET /api/runs  the newest GitHub Actions runs of the render farm (Eouchi147/rc-render) and the studio repo
// (Eouchi147/kinoforge), merged, newest first. Read only. Both repos are public, so this works without a token (with a
// lower rate limit); a repo that does not answer is listed in `errors` and the other one still shows.
import { repoRuns } from '@/lib/github';
export const dynamic = 'force-dynamic';

const REPOS = ['Eouchi147/rc-render', 'Eouchi147/kinoforge'];

export async function GET() {
  const results = await Promise.allSettled(REPOS.map((r) => repoRuns(r, 20)));
  const runs = [], errors = [];
  results.forEach((res, i) => {
    if (res.status === 'rejected') { errors.push({ repo: REPOS[i], error: res.reason?.message || 'no answer' }); return; }
    for (const r of res.value) runs.push({
      repo: REPOS[i], id: r.id, name: r.name, workflow: (r.path || '').split('/').pop(), title: r.display_title || '', status: r.status, conclusion: r.conclusion,
      url: r.html_url, event: r.event, started: r.run_started_at || r.created_at, updated: r.updated_at,
    });
  });
  runs.sort((a, b) => String(b.updated).localeCompare(String(a.updated)));
  return Response.json({ runs, errors, at: new Date().toISOString() }, { headers: { 'Cache-Control': 'public, max-age=15, s-maxage=20' } });
}
