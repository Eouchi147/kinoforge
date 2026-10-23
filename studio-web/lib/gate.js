// The write lock. The studio is public (kinoforge-studio.vercel.app) and its write routes act with Sam's GitHub token
// and spend his OpenRouter credit. When the Vercel env var STUDIO_PASSCODE is set, those routes need an unlock cookie:
// Sam types the passcode once in Settings; /api/unlock answers with an httpOnly cookie signed (HMAC-SHA256) with a key
// derived from the passcode, so changing the passcode signs everyone out. Reads stay open. Without STUDIO_PASSCODE,
// writes work as before and Settings says plainly that they are open.
import crypto from 'node:crypto';

export const COOKIE = 'kf_unlock';
const DAYS = 90;
export const gateOn = () => Boolean(process.env.STUDIO_PASSCODE);
const key = () => crypto.createHash('sha256').update('kinoforge-studio-unlock-v1:' + (process.env.STUDIO_PASSCODE || '')).digest();
const mac = (ts) => crypto.createHmac('sha256', key()).update('unlocked:' + ts).digest('base64url');
const same = (a, b) => { const x = Buffer.from(String(a)), y = Buffer.from(String(b)); return x.length === y.length && crypto.timingSafeEqual(x, y); };

export function token() { const ts = String(Date.now()); return `${ts}.${mac(ts)}`; }

export function passcodeOk(p) {
  if (!gateOn() || typeof p !== 'string') return false;
  const h = (v) => crypto.createHash('sha256').update(v).digest('hex');
  return same(h(p), h(process.env.STUDIO_PASSCODE));
}

function cookieValue(req) {
  const raw = req.headers.get('cookie') || '';
  for (const part of raw.split(';')) { const [k, ...v] = part.trim().split('='); if (k === COOKIE) return v.join('='); }
  return null;
}

export function unlocked(req) {
  if (!gateOn()) return true;
  const v = cookieValue(req); if (!v) return false;
  const [ts, sig] = v.split('.');
  if (!/^\d{12,14}$/.test(ts || '') || !sig) return false;
  if (Date.now() - Number(ts) > DAYS * 864e5) return false;
  return same(sig, mac(ts));
}

/** null when the request may write; else the 401 to return. */
export function guard(req) {
  if (unlocked(req)) return null;
  return Response.json({ saved: false, code: 'locked', error: 'The studio is locked. Unlock it in Settings to make changes.' }, { status: 401 });
}

export function cookie(req, value, maxAgeS) {
  const https = new URL(req.url).protocol === 'https:' || req.headers.get('x-forwarded-proto') === 'https';
  return `${COOKIE}=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAgeS}${https ? '; Secure' : ''}`;
}
export const MAX_AGE = DAYS * 86400;
