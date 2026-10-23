// POST /api/build  { brief }  commits films/studio/<id>/brief.json; that push starts .github/workflows/film.yml.
import { commitFile, readJSON, exists } from '@/lib/github';
export const dynamic = 'force-dynamic';

const LINES = ['battle-map', 'kinetic', 'cutaway'];
const ENGINE_SPEC = { 'battle-map': 'films/lib/battlemap/SPEC.md', kinetic: 'films/lib/kinetic/SPEC.md', cutaway: 'films/lib/cutaway/SPEC.md' };   // a line is available when its SPEC.md is on main
const RANGE = { 'battle-map': [120, 180], kinetic: [60, 180], cutaway: [30, 90] };   // the pipeline checks the line's own range (films/director/lines.json)
const slug = (s) => (s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40);
const str = (v, max = 600) => (typeof v === 'string' ? v.trim().slice(0, max) : '');
const dashless = (s) => s.replace(/[\u2013\u2014]/g, ',').replace(/\.{3,}|\u2026/g, '');

export async function POST(req) {
  const { brief: b } = await req.json().catch(() => ({}));
  const missing = ['title', 'line', 'subject', 'angle', 'audience', 'tone'].filter((k) => !str(b?.[k]));
  if (missing.length) return Response.json({ error: `The brief still needs: ${missing.join(', ')}.` }, { status: 400 });
  if (!LINES.includes(b.line)) return Response.json({ error: 'The line must be battle-map, kinetic or cutaway.' }, { status: 400 });
  const range = RANGE[b.line];
  const target = Math.min(range[1], Math.max(range[0], Math.round(Number(b.target_seconds) || { kinetic: 120, 'battle-map': 150, cutaway: 60 }[b.line])));
  const cap = Math.min(3, Math.max(0.5, Number(b.cap_usd) || 1.5));
  if (!(await exists(ENGINE_SPEC[b.line]).catch(() => true))) return Response.json({ error: `The ${b.line} line is not available on the build side yet. Choose the other line, or try again later.` }, { status: 409 });
  let id = slug(b.title) || 'film'; const base = id;
  try {
    for (let n = 2; await readJSON(`films/studio/${id}/brief.json`); n++) id = `${base}-${n}`;
    const out = {
      id, title: dashless(str(b.title, 90)), line: b.line, subject: dashless(str(b.subject)), angle: dashless(str(b.angle)),
      audience: dashless(str(b.audience, 200)), tone: dashless(str(b.tone, 200)), target_seconds: target, cap_usd: +cap.toFixed(2),
      approved_at: new Date().toISOString(),   // the pipeline starts a fresh job whenever this changes
    };
    if (str(b.notes, 800)) out.notes = dashless(str(b.notes, 800));
    if (b.line === 'cutaway') out.format = b.format === '9:16' ? '9:16' : '16:9';
    // voice is a "model|voice" id for the narration lane (e.g. elevenlabs/eleven-v4|brian); left out, the pipeline's default narrator is used
    if (/^[A-Za-z0-9._\/-]+\|[A-Za-z0-9_-]+$/.test(str(b.voice, 120))) out.voice = str(b.voice, 120);
    const url = await commitFile(`films/studio/${id}/brief.json`, JSON.stringify(out, null, 1) + '\n', `studio: brief for ${id} (${b.line})`);
    return Response.json({ saved: true, id, url, brief: out });
  } catch (e) {
    return Response.json({ saved: false, code: e.code || 'error', error: e.code === 'no-github' ? 'GitHub is not connected yet.' : e.message }, { status: e.code === 'no-github' ? 409 : 500 });
  }
}
