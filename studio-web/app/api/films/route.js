import { library } from '@/lib/library';
export const dynamic = 'force-dynamic';
export async function GET() {
  const l = await library();
  return Response.json(l, { headers: { 'Cache-Control': 'public, max-age=30, s-maxage=60' } });
}
