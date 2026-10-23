// GET /api/manual        the manual's table of contents: docs/GUIDE.md and every docs/manual/**.md on main, with titles
// GET /api/manual?q=...  full-text search over those pages (each fetched from raw GitHub, cached five minutes)
// Read only. When GitHub does not answer, `error` says so and the page falls back to the catalog's recipe paths.
import { treePaths, readRaw } from '@/lib/github';
export const dynamic = 'force-dynamic';
export const maxDuration = 30;

const isDoc = (p) => p === 'docs/GUIDE.md' || (p.startsWith('docs/manual/') && p.endsWith('.md'));
const titleOf = (text, path) => (/^#\s+(.+)$/m.exec(text || '')?.[1] || path.split('/').pop().replace(/\.md$/, '').replace(/[-_]+/g, ' ')).trim();

async function pages() {
  return (await treePaths()).filter(isDoc).sort((a, b) => (a === 'docs/GUIDE.md' ? -1 : b === 'docs/GUIDE.md' ? 1 : a === 'docs/manual/README.md' ? -1 : b === 'docs/manual/README.md' ? 1 : a.localeCompare(b)));
}

async function pool(items, n, fn) {
  const out = new Array(items.length); let i = 0;
  await Promise.all(Array.from({ length: n }, async () => { while (i < items.length) { const k = i++; out[k] = await fn(items[k]).catch(() => null); } }));
  return out;
}

export async function GET(req) {
  const q = (new URL(req.url).searchParams.get('q') || '').trim().toLowerCase().slice(0, 80);
  let paths;
  try { paths = await pages(); }
  catch (e) { return Response.json({ pages: [], hits: [], error: e.message }, { headers: { 'Cache-Control': 'no-store' } }); }
  const texts = await pool(paths, 8, (p) => readRaw(p, { revalidate: 300 }));
  const all = paths.map((path, i) => ({ path, title: titleOf(texts[i], path) }));
  if (!q) return Response.json({ pages: all }, { headers: { 'Cache-Control': 'public, max-age=60, s-maxage=300' } });
  const terms = q.split(/\s+/).filter(Boolean);
  const hits = [];
  paths.forEach((path, i) => {
    const t = texts[i] || ''; const low = t.toLowerCase();
    if (!terms.every((w) => low.includes(w) || path.includes(w))) return;
    const at = Math.max(0, low.indexOf(terms[0]));
    const snippet = t.slice(Math.max(0, at - 70), at + 160).replace(/\s+/g, ' ').replace(/[#*\x60|]/g, '').trim();
    const sc = terms.reduce((s, w) => s + (all[i].title.toLowerCase().includes(w) ? 5 : 0) + (path.includes(w) ? 3 : 0) + Math.min(5, low.split(w).length - 1), 0);
    hits.push({ path, title: all[i].title, snippet, sc });
  });
  hits.sort((a, b) => b.sc - a.sc);
  return Response.json({ pages: all, hits: hits.slice(0, 30).map(({ sc, ...h }) => h) }, { headers: { 'Cache-Control': 'public, max-age=60, s-maxage=300' } });
}
