import { commitFile } from '@/lib/github';
export async function POST(req) {
  const { topic, choice, note = '' } = await req.json();
  if (!topic || !choice) return Response.json({ error: 'topic and choice are required' }, { status: 400 });
  const at = new Date().toISOString();
  try {
    const url = await commitFile(`studio/decisions/${at.slice(0, 10)}-${topic}.json`, JSON.stringify({ topic, choice, note, at }, null, 1), `decision: ${topic} → ${choice}`);
    return Response.json({ saved: true, url });
  } catch (e) {
    return Response.json({ saved: false, code: e.code || 'error', error: e.message }, { status: e.code === 'no-github' ? 409 : 500 });
  }
}
