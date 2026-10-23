// Decision records go to the studio-data branch, never main (a commit to main redeploys the studio).
import { commitFile, DATA_BRANCH } from '@/lib/github';
import { guard } from '@/lib/gate';
export async function POST(req) {
  const locked = guard(req); if (locked) return locked;
  const { topic, choice, note = '' } = await req.json();
  if (!topic || !choice) return Response.json({ error: 'topic and choice are required' }, { status: 400 });
  const at = new Date().toISOString();
  try {
    const url = await commitFile(`studio/decisions/${at.slice(0, 10)}-${topic}.json`, JSON.stringify({ topic, choice, note, at }, null, 1), `decision: ${topic}: ${choice}`, { branch: DATA_BRANCH });
    return Response.json({ saved: true, url });
  } catch (e) {
    return Response.json({ saved: false, code: e.code || 'error', error: e.message }, { status: e.code === 'no-github' ? 409 : 500 });
  }
}
