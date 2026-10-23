// GET /api/doc?path=docs/manual/<...>.md  one page of the manual (or docs/GUIDE.md), fetched from the public repo at
// request time (raw.githubusercontent.com, cached a minute). Only the guide and the manual are served.
import { readRaw } from '@/lib/github';
export const dynamic = 'force-dynamic';

const DOC_OK = /^docs\/(GUIDE\.md|manual\/[A-Za-z0-9][A-Za-z0-9_\/-]*\.md)$/;

export async function GET(req) {
  const path = new URL(req.url).searchParams.get('path') || '';
  if (!DOC_OK.test(path) || path.includes('//')) return Response.json({ error: 'Only docs/GUIDE.md and pages under docs/manual/ can be read here.' }, { status: 400 });
  const web = `https://github.com/Eouchi147/kinoforge/blob/main/${path}`;
  try {
    const text = await readRaw(path, { revalidate: 60 });
    if (text == null) return Response.json({ path, text: null, web, error: 'not written yet' }, { status: 404 });
    return Response.json({ path, text, web }, { headers: { 'Cache-Control': 'public, max-age=30, s-maxage=60' } });
  } catch (e) {
    return Response.json({ path, text: null, web, error: e.message }, { status: 502 });
  }
}
