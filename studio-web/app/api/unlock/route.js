// GET    /api/unlock   { required, unlocked }  is the write lock on (STUDIO_PASSCODE set on Vercel) and is this browser in
// POST   /api/unlock   { passcode }            sets the signed httpOnly cookie when the passcode is right
// DELETE /api/unlock                           signs this browser out
import { gateOn, unlocked, passcodeOk, token, cookie, MAX_AGE } from '@/lib/gate';
export const dynamic = 'force-dynamic';

export async function GET(req) {
  return Response.json({ required: gateOn(), unlocked: gateOn() ? unlocked(req) : true }, { headers: { 'Cache-Control': 'no-store' } });
}

export async function POST(req) {
  if (!gateOn()) return Response.json({ required: false, unlocked: true });
  const { passcode } = await req.json().catch(() => ({}));
  if (!passcodeOk(passcode)) {
    await new Promise((r) => setTimeout(r, 700));   // slows guessing
    return Response.json({ required: true, unlocked: false, error: 'That passcode is not right.' }, { status: 401 });
  }
  return Response.json({ required: true, unlocked: true }, { headers: { 'Set-Cookie': cookie(req, token(), MAX_AGE), 'Cache-Control': 'no-store' } });
}

export async function DELETE(req) {
  return Response.json({ required: gateOn(), unlocked: !gateOn() }, { headers: { 'Set-Cookie': cookie(req, '', 0) } });
}
