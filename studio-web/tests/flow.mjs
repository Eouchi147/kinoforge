// The studio flow against a mock OpenRouter (tests only; no key, no money, no GitHub writes).
//   cd studio-web && npx next build && node tests/flow.mjs
// Starts a mock OpenRouter on a local port, then `next start` with OPENROUTER_BASE pointing at it, and walks the flow:
// status (key and credit), the director's opening turn, a turn with the key out of credit (402), the build route's checks,
// and the job route's input check. Exits 1 on the first failure.
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
const app = spawn('npx', ['next', 'start', '-p', String(PORT)], { env, stdio: ['ignore', 'pipe', 'pipe'] });
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
} finally { app.kill('SIGTERM'); mock.close(); }
console.log(failed ? `${failed} failed` : 'studio flow: all ok'); process.exit(failed ? 1 : 0);
