// The studio flow against a mock OpenRouter (tests only; no key, no money, no GitHub writes).
//   cd studio-web && npx next build && node tests/flow.mjs
// Starts a mock OpenRouter on a local port, then `next start` with OPENROUTER_BASE pointing at it, and walks the flow:
// status (key and credit), the director's opening turn, a turn with the key out of credit (402), the build route's checks,
// the job route's input check, the OS's read routes (doc, review, runs, unlock) and, on a second server with
// STUDIO_PASSCODE set, the write lock (refused without the cookie, wrong passcode refused, right one unlocks).
// Exits 1 when any check failed.
import http from 'node:http';
import { spawn } from 'node:child_process';

let mode = 'ok'; const seen = [];
const TURN = { say: 'Hello Sam. Pick a subject.', options: ['The Battle of Salamis', 'The Great Emu War'], ready: false, crew: { need: 'none', task: null },
  brief: { title: null, line: null, format: null, subject: null, angle: null, audience: null, tone: null, target_seconds: null, notes: null } };
const IDEAS = { ideas: [{ title: 'Salamis', pitch: 'A fleet lured into a strait, 480 BC.', why: 'places and movement' }] };
const mock = http.createServer((req, res) => {
  let body = ''; req.on('data', (c) => (body += c)); req.on('end', () => {
    const send = (code, obj) => { res.writeHead(code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(obj)); };
    if (req.url.endsWith('/models')) return send(200, { data: [
      { id: 'anthropic/claude-opus-5.5', pricing: { prompt: '0.000005', completion: '0.000025' }, architecture: { input_modalities: ['text', 'image'] }, supported_parameters: ['structured_outputs'], benchmarks: { artificial_analysis: { intelligence_index: 80 } }, created: 2 },
      { id: 'xiaomi/mimo-v2.6-pro', pricing: { prompt: '0.0000004', completion: '0.000001' }, architecture: { input_modalities: ['text', 'image'] }, supported_parameters: ['structured_outputs'], benchmarks: { artificial_analysis: { intelligence_index: 60 } }, created: 1 },
      { id: 'nvidia/nemotron-3-ultra-550b-a55b:free', pricing: { prompt: '0', completion: '0' }, architecture: { input_modalities: ['text'] }, supported_parameters: [], created: 1 }] });
    if (req.url.endsWith('/key')) return send(200, { data: mode === 'broke' ? { usage: 5, limit: 5, limit_remaining: 0 } : { usage: 1, limit: 10, limit_remaining: 9 } });
    if (req.url.endsWith('/chat/completions')) {
      const b = JSON.parse(body || '{}'); seen.push(b.model);
      if (mode === 'broke') return send(402, { error: { message: 'Insufficient credits' } });
      const name = b.response_format?.json_schema?.name || (JSON.stringify(b.messages).includes('crew') ? 'crew_ideas' : 'director_turn');
      return send(200, { model: b.model, usage: { cost: 0.001, prompt_tokens: 100, completion_tokens: 50 }, choices: [{ message: { content: JSON.stringify(name === 'crew_ideas' ? IDEAS : TURN) } }] });
    }
    send(404, {});
  });
});
await new Promise((r) => mock.listen(0, '127.0.0.1', r));
const MOCK = `http://127.0.0.1:${mock.address().port}`;
const PORT = 3000 + Math.floor(Math.random() * 2000);
const env = { ...process.env, OPENROUTER_BASE: MOCK, OPENROUTER_API_KEY: 'test-only', PORT: String(PORT) }; delete env.GITHUB_TOKEN;
const app = spawn('npx', ['next', 'start', '-p', String(PORT)], { env, stdio: ['ignore', 'pipe', 'pipe'], detached: true });
const stop = (p) => { try { process.kill(-p.pid, 'SIGTERM'); } catch { p.kill('SIGTERM'); } };   // the whole group: npx and the next server it starts
const base = `http://127.0.0.1:${PORT}`;
for (let i = 0; i < 60; i++) { try { await fetch(base + '/api/status'); break; } catch { await new Promise((r) => setTimeout(r, 500)); } }
let failed = 0; const check = (ok, what, extra = '') => { console.log((ok ? 'ok   ' : 'FAIL ') + what + (ok ? '' : '  ' + extra)); if (!ok) failed++; };
const post = (p, body) => fetch(base + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
try {
  let r = await fetch(base + '/api/status'); let j = await r.json();
  check(j.openrouter === true && j.github === false, 'status: key present, GitHub not connected', JSON.stringify(j).slice(0, 200));
  check(j.account?.remaining === 9, 'status: credit left on the studio key is read', JSON.stringify(j.account));
  r = await post('/api/director', { messages: [] }); j = await r.json();
  check(r.ok && j.say === TURN.say && j.options.length === 2, 'director: opening turn answers', JSON.stringify(j).slice(0, 300));
  check(j.director?.seat === 'head' && j.director?.head === 'claude-opus-5.5', 'director: the paid head seat leads (Opus)', JSON.stringify(j.director));
  r = await post('/api/director', { messages: [{ role: 'user', content: 'The Battle of Salamis' }], brief: { line: 'battle-map' } }); j = await r.json();
  check(r.ok && j.brief?.line === 'battle-map', 'director: the brief is carried forward', JSON.stringify(j.brief));
  mode = 'broke';
  r = await post('/api/director', { messages: [{ role: 'user', content: 'hello' }] }); j = await r.json();
  check(r.status === 502 && j.code === 'credits', 'director: out of credit gives the credits code (the page shows the add-credit message)', `${r.status} ${JSON.stringify(j).slice(0, 200)}`);
  mode = 'ok';
  r = await post('/api/build', { brief: { title: 'X', line: 'battle-map' } }); j = await r.json();
  check(r.status === 400 && /still needs/.test(j.error), 'build: an incomplete brief is refused', JSON.stringify(j));
  const full = { title: 'The Battle of Salamis', line: 'battle-map', subject: 'Salamis, 480 BC', angle: 'a strait', audience: 'kids', tone: 'upbeat', target_seconds: 150, cap_usd: 2 };
  r = await post('/api/build', { brief: full }); j = await r.json();
  check(r.status === 409 && j.code === 'no-github', 'build: without GitHub it says so (no write)', `${r.status} ${JSON.stringify(j)}`);
  r = await fetch(base + '/api/job?id=Bad%20id'); check(r.status === 400, 'job: a bad id is refused');
  r = await fetch(base + '/api/doc?path=../../etc/passwd'); check(r.status === 400, 'doc: only the guide and the manual can be read');
  r = await fetch(base + '/api/doc?path=docs/AGENTS.md'); check(r.status === 400, 'doc: other docs are refused');
  r = await fetch(base + '/api/review?id=bad%20id'); check(r.status === 400, 'review: a bad id is refused');
  r = await post('/api/review', { id: 'battle-map-cannae', action: 'note', text: 'Hold the title longer', t: 12.34 }); j = await r.json();
  check(r.status === 409 && j.code === 'no-github', 'review: without GitHub it says so (the page keeps the note on the device)', `${r.status} ${JSON.stringify(j)}`);
  r = await post('/api/review', { id: 'battle-map-cannae', action: 'shout', text: 'x' }); check(r.status === 400, 'review: an unknown action is refused');
  r = await fetch(base + '/api/runs'); j = await r.json();
  check(r.ok && Array.isArray(j.runs) && Array.isArray(j.errors), 'runs: answers with runs and errors (GitHub may be unreachable here)', JSON.stringify(j).slice(0, 200));
  r = await fetch(base + '/api/unlock'); j = await r.json();
  check(j.required === false && j.unlocked === true, 'unlock: without STUDIO_PASSCODE writes are open (Settings warns)', JSON.stringify(j));
  r = await fetch(base + '/api/media?r=evil:x&f=a.mp4'); check(r.status === 404, 'media: releases outside the two studio repos are refused');
} finally { stop(app); }

// ---- the write lock, on a second server with STUDIO_PASSCODE set
const PORT2 = PORT + 1;
const app2 = spawn('npx', ['next', 'start', '-p', String(PORT2)], { env: { ...env, PORT: String(PORT2), STUDIO_PASSCODE: 'four quiet test words' }, stdio: ['ignore', 'pipe', 'pipe'], detached: true });
const base2 = `http://127.0.0.1:${PORT2}`;
for (let i = 0; i < 60; i++) { try { await fetch(base2 + '/api/unlock'); break; } catch { await new Promise((r) => setTimeout(r, 500)); } }
const post2 = (p, body, cookie) => fetch(base2 + p, { method: 'POST', headers: { 'Content-Type': 'application/json', ...(cookie ? { Cookie: cookie } : {}) }, body: JSON.stringify(body) });
try {
  const full = { title: 'The Battle of Salamis', line: 'battle-map', subject: 'Salamis, 480 BC', angle: 'a strait', audience: 'kids', tone: 'upbeat', target_seconds: 150, cap_usd: 2 };
  let r = await fetch(base2 + '/api/unlock'); let j = await r.json();
  check(j.required === true && j.unlocked === false, 'lock: on when STUDIO_PASSCODE is set', JSON.stringify(j));
  r = await post2('/api/build', { brief: full }); j = await r.json();
  check(r.status === 401 && j.code === 'locked', 'lock: build refused without the cookie', `${r.status} ${JSON.stringify(j)}`);
  r = await post2('/api/director', { messages: [] }); check(r.status === 401, 'lock: the director chat (it spends credit) is refused without the cookie');
  r = await post2('/api/review', { id: 'battle-map-cannae', action: 'approve' }); check(r.status === 401, 'lock: review refused without the cookie');
  r = await post2('/api/decision', { topic: 't', choice: 'c' }); check(r.status === 401, 'lock: decision refused without the cookie');
  r = await post2('/api/build', { brief: full }, 'kf_unlock=1761000000000.forged'); check(r.status === 401, 'lock: a forged cookie is refused');
  r = await post2('/api/unlock', { passcode: 'wrong words' }); check(r.status === 401 && !r.headers.get('set-cookie'), 'lock: a wrong passcode is refused');
  r = await post2('/api/unlock', { passcode: 'four quiet test words' }); j = await r.json();
  const setc = r.headers.get('set-cookie') || '';
  check(j.unlocked === true && /kf_unlock=\d+\.[\w-]+;/.test(setc) && /HttpOnly/i.test(setc) && /SameSite=Strict/i.test(setc), 'lock: the right passcode sets a signed httpOnly cookie', setc);
  const cookie = setc.split(';')[0];
  r = await fetch(base2 + '/api/unlock', { headers: { Cookie: cookie } }); j = await r.json(); check(j.unlocked === true, 'lock: the cookie unlocks this browser');
  r = await post2('/api/build', { brief: full }, cookie); j = await r.json();
  check(r.status === 409 && j.code === 'no-github', 'lock: with the cookie the build passes the lock (then says GitHub is not connected)', `${r.status} ${JSON.stringify(j)}`);
  r = await fetch(base2 + '/api/films'); check(r.ok, 'lock: reads stay open');
} finally { stop(app2); mock.close(); }
console.log(failed ? `${failed} failed` : 'studio flow: all ok'); process.exit(failed ? 1 : 0);
