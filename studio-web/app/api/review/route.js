// GET  /api/review?id=<film id>  Sam's review of a film: films/reviews/<id>.json on the studio-data branch (verdict and
//      notes pinned to a time and a frame). Never on main: a commit to main redeploys the studio (Vercel Hobby: 100 a day).
// POST /api/review { id, action: "approve" | "changes" | "note", text, t, frame, fps }  appends to that file and commits it
//      to studio-data with the studio's GitHub token (the branch is created from main on first write). Locked when
//      STUDIO_PASSCODE is set and this browser has not unlocked. Without a token: 409 "no-github"; the page keeps the note.
// Agents read reviews at https://raw.githubusercontent.com/Eouchi147/kinoforge/studio-data/films/reviews/<id>.json
import { commitFile, readJSON, readRaw, listDir, DATA_BRANCH } from '@/lib/github';
import { guard } from '@/lib/gate';
export const dynamic = 'force-dynamic';

const ID_OK = /^[A-Za-z0-9][A-Za-z0-9_-]{0,90}$/;
const dashless = (s) => s.replace(/[\u2013\u2014]/g, ',').replace(/\.{3,}|\u2026/g, '.');
const empty = (id) => ({ id, verdict: null, verdict_at: null, notes: [], updated: null });

async function current(id, strict = false) {
  const path = `films/reviews/${id}.json`;
  if (strict) return (await readJSON(path, DATA_BRANCH)) || empty(id);                     // before a write: fresh or fail, never a stale copy
  if (process.env.GITHUB_TOKEN) {
    try { return (await readJSON(path, DATA_BRANCH)) || empty(id); } catch { /* rate limited or down: the public file below */ }   // fresh, through the API
  }
  const t = await readRaw(path, { revalidate: 0, ref: DATA_BRANCH });                            // public, may lag a few minutes
  return t ? JSON.parse(t) : empty(id);
}

// GET /api/review (no id): every saved verdict, { verdicts: { <id>: "approved" | "changes" } }, for the desk.
async function all() {
  const files = (await listDir('films/reviews', { ref: DATA_BRANCH })).filter((f) => f.type === 'file' && f.name.endsWith('.json')).slice(0, 200);
  const out = {};
  await Promise.all(files.map(async (f) => {
    try { const r = JSON.parse(await readRaw(f.path, { revalidate: 30, ref: DATA_BRANCH })); if (r?.verdict) out[f.name.replace(/\.json$/, '')] = r.verdict; } catch { /* skip */ }
  }));
  return out;
}

export async function GET(req) {
  const id = new URL(req.url).searchParams.get('id') || '';
  if (!id) {
    try { return Response.json({ verdicts: await all() }, { headers: { 'Cache-Control': 'public, max-age=15, s-maxage=30' } }); }
    catch (e) { return Response.json({ verdicts: {}, error: e.message }, { headers: { 'Cache-Control': 'no-store' } }); }
  }
  if (!ID_OK.test(id)) return Response.json({ error: 'bad id' }, { status: 400 });
  try { return Response.json({ review: await current(id) }, { headers: { 'Cache-Control': 'no-store' } }); }
  catch (e) { return Response.json({ review: empty(id), error: e.message }, { status: 200, headers: { 'Cache-Control': 'no-store' } }); }
}

export async function POST(req) {
  const locked = guard(req); if (locked) return locked;
  const { id, action, text = '', t = null, frame = null, fps = null } = await req.json().catch(() => ({}));
  if (!ID_OK.test(id || '')) return Response.json({ saved: false, error: 'bad id' }, { status: 400 });
  if (!['approve', 'changes', 'note'].includes(action)) return Response.json({ saved: false, error: 'action must be approve, changes or note' }, { status: 400 });
  const words = dashless(String(text || '').trim().slice(0, 1500));
  if (action !== 'approve' && !words) return Response.json({ saved: false, error: 'Write the note first.' }, { status: 400 });
  const time = Number.isFinite(Number(t)) && t !== null && Number(t) >= 0 ? Math.round(Number(t) * 10) / 10 : null;
  if (!process.env.GITHUB_TOKEN) return Response.json({ saved: false, code: 'no-github', error: 'GitHub is not connected, so the studio cannot save to the repo.' }, { status: 409 });
  try {
    const r = await current(id, true); const at = new Date().toISOString();
    r.notes = Array.isArray(r.notes) ? r.notes : [];
    if (action === 'approve') { r.verdict = 'approved'; r.verdict_at = at; }
    if (action === 'changes') { r.verdict = 'changes'; r.verdict_at = at; }
    const fr = Number.isInteger(frame) && frame >= 0 && frame < 1e7 ? frame : null;
    const rate = Number(fps) > 0 && Number(fps) <= 240 ? Number(fps) : null;
    if (words || action !== 'note') r.notes.push({ t: time, ...(fr != null ? { frame: fr, fps: rate } : {}), text: words || 'Approved.', kind: action, at });
    r.updated = at;
    const url = await commitFile(`films/reviews/${id}.json`, JSON.stringify(r, null, 1) + '\n', `review: ${id} ${action === 'note' ? 'note' : action === 'approve' ? 'approved' : 'changes requested'}`, { branch: DATA_BRANCH });
    return Response.json({ saved: true, url, review: r });
  } catch (e) {
    return Response.json({ saved: false, code: e.code || 'error', error: e.code === 'no-github' ? 'GitHub is not connected.' : e.message }, { status: e.code === 'no-github' ? 409 : 502 });
  }
}
