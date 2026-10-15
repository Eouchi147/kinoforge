import { commitFile } from '@/lib/github';
const slug = (s) => (s || 'untitled').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48);
export async function POST(req) {
  const { brief, transcript = [] } = await req.json();
  if (!brief?.title) return Response.json({ error: 'The brief needs a title first.' }, { status: 400 });
  const id = slug(brief.title), at = new Date().toISOString();
  try {
    await commitFile(`films/${id}/transcript.json`, JSON.stringify(transcript, null, 1), `film ${id}: director conversation`);
    const url = await commitFile(`films/${id}/brief.json`, JSON.stringify({ ...brief, id, stage: 'story', approved_at: at }, null, 1), `film ${id}: brief approved (Gate 1)`);
    return Response.json({ saved: true, id, url });
  } catch (e) {
    return Response.json({ saved: false, code: e.code || 'error', error: e.message }, { status: e.code === 'no-github' ? 409 : 500 });
  }
}
