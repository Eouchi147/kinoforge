// GET /api/media?r=<release>&f=<file>  streams a public GitHub release asset, forwarding Range requests so that
// <video> plays and seeks. Allow-list only (lib/media.js); no token is sent or exposed (the repos are public).
// &dl=1 redirects to the GitHub download URL instead (big files should not pass through a function).
// r is an old short key ("kino-films") or "<repo>:<tag>" for a release of Eouchi147/kinoforge or Eouchi147/rc-render.
import { resolveRelease, NAME_OK, TYPES, downloadUrl } from '@/lib/media';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const PASS = ['content-length', 'content-range', 'etag', 'last-modified'];

export async function GET(req) {
  const u = new URL(req.url);
  const rel = resolveRelease(u.searchParams.get('r') || ''), name = u.searchParams.get('f') || '';
  if (!rel || !NAME_OK.test(name)) return new Response('Not found', { status: 404 });
  const src = `https://github.com/${rel.repo}/releases/download/${rel.tag}/${encodeURIComponent(name)}`;
  if (u.searchParams.get('dl')) return Response.redirect(downloadUrl(u.searchParams.get('r'), name), 302);

  const headers = { 'User-Agent': 'kinoforge-studio' };
  const range = req.headers.get('range');
  if (range && /^bytes=\d*-\d*$/.test(range)) headers.Range = range;
  let up;
  try { up = await fetch(src, { headers, redirect: 'follow', cache: 'no-store', signal: AbortSignal.timeout(25000) }); }
  catch { return new Response('The file host did not answer. Try again.', { status: 502 }); }
  if (up.status === 404) return new Response('Not found', { status: 404 });
  if (up.status === 416) return new Response(null, { status: 416, headers: { 'Content-Range': up.headers.get('content-range') || 'bytes */*' } });
  if (!up.ok && up.status !== 206) return new Response('The file host refused.', { status: 502 });

  const out = new Headers({
    'Content-Type': TYPES[name.split('.').pop().toLowerCase()] || 'application/octet-stream',
    'Accept-Ranges': 'bytes',
    'Cache-Control': 'public, max-age=3600',
    'X-Content-Type-Options': 'nosniff',
    'Content-Disposition': 'inline',
  });
  for (const h of PASS) if (up.headers.get(h)) out.set(h, up.headers.get(h));
  return new Response(up.body, { status: up.status === 206 ? 206 : 200, headers: out });
}
