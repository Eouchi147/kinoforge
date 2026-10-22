// The repo is the studio's memory: briefs, decisions and film folders are committed there.
import { REPO } from './data';

export async function commitFile(path, content, message) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw Object.assign(new Error('no-github'), { code: 'no-github' });
  const url = `https://api.github.com/repos/${REPO}/contents/${path}`;
  const h = { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'User-Agent': 'kinoforge-studio' };
  let sha;
  const cur = await fetch(url, { headers: h, cache: 'no-store' });
  if (cur.ok) sha = (await cur.json()).sha;
  const r = await fetch(url, {
    method: 'PUT', headers: h,
    body: JSON.stringify({ message, content: Buffer.from(content).toString('base64'), sha, committer: { name: 'KINOFORGE Studio', email: 'Eouchi147@users.noreply.github.com' } }),
  });
  if (!r.ok) throw Object.assign(new Error(`GitHub ${r.status}: ${(await r.text()).slice(0, 200)}`), { code: 'github' });
  return (await r.json()).content?.html_url;
}

const headers = (token) => ({ Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'User-Agent': 'kinoforge-studio' });

/** Read a JSON file from the repo, never cached. Returns null if it does not exist. */
export async function readJSON(path, ref = 'main') {
  const token = process.env.GITHUB_TOKEN;
  const url = `https://api.github.com/repos/${REPO}/contents/${path}?ref=${ref}&_=${Date.now()}`;
  const r = await fetch(url, { headers: { ...(token ? headers(token) : { 'User-Agent': 'kinoforge-studio' }), Accept: 'application/vnd.github.raw+json' }, cache: 'no-store', signal: AbortSignal.timeout(9000) });
  if (r.status === 404) return null;
  if (!r.ok) throw Object.assign(new Error(`GitHub ${r.status}`), { code: 'github' });
  return JSON.parse(await r.text());
}

/** The latest runs of a workflow file (for a link and a failure signal when status.json has not appeared). */
export async function workflowRuns(file, perPage = 8) {
  const token = process.env.GITHUB_TOKEN;
  const r = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${file}/runs?per_page=${perPage}`, { headers: token ? headers(token) : { 'User-Agent': 'kinoforge-studio' }, cache: 'no-store', signal: AbortSignal.timeout(9000) });
  if (!r.ok) return [];
  return (await r.json()).workflow_runs || [];
}

/** Does a path exist on main? (HEAD-style check through the contents API.) */
export async function exists(path) {
  const token = process.env.GITHUB_TOKEN;
  const r = await fetch(`https://api.github.com/repos/${REPO}/contents/${path}?ref=main`, { headers: token ? headers(token) : { 'User-Agent': 'kinoforge-studio' }, cache: 'no-store', signal: AbortSignal.timeout(9000) });
  return r.ok;
}
