// The repo is the studio's memory: briefs, decisions and film folders are committed there.
import { REPO } from './data';

/** The branch where the OS keeps Sam's reviews and other studio writes, so they never land on main (a commit to main
 *  redeploys the studio on Vercel, and Hobby allows 100 deploys a day). Agents read it through raw GitHub. */
export const DATA_BRANCH = 'studio-data';

/** Make sure a branch exists (created from main on first use). */
export async function ensureBranch(branch) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw Object.assign(new Error('no-github'), { code: 'no-github' });
  const h = { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'User-Agent': 'kinoforge-studio' };
  const base = `https://api.github.com/repos/${REPO}/git`;
  const have = await fetch(`${base}/ref/heads/${branch}`, { headers: h, cache: 'no-store' });
  if (have.ok) return;
  if (have.status !== 404) throw Object.assign(new Error(`GitHub ${have.status} reading branch ${branch}`), { code: 'github' });
  const main = await fetch(`${base}/ref/heads/main`, { headers: h, cache: 'no-store' });
  if (!main.ok) throw Object.assign(new Error(`GitHub ${main.status} reading main`), { code: 'github' });
  const sha = (await main.json()).object?.sha;
  const r = await fetch(`${base}/refs`, { method: 'POST', headers: h, body: JSON.stringify({ ref: `refs/heads/${branch}`, sha }) });
  if (!r.ok && r.status !== 422) throw Object.assign(new Error(`GitHub ${r.status} creating branch ${branch}`), { code: 'github' });   // 422: created meanwhile
}

/** Create or update one file with one commit. branch: "main" (default; /api/build, the director listens there) or
 *  DATA_BRANCH for everything else the OS writes. */
export async function commitFile(path, content, message, { branch = 'main' } = {}) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw Object.assign(new Error('no-github'), { code: 'no-github' });
  if (branch !== 'main') await ensureBranch(branch);
  const url = `https://api.github.com/repos/${REPO}/contents/${path}`;
  const h = { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'User-Agent': 'kinoforge-studio' };
  let sha;
  const cur = await fetch(`${url}?ref=${encodeURIComponent(branch)}`, { headers: h, cache: 'no-store' });
  if (cur.ok) sha = (await cur.json()).sha;
  const r = await fetch(url, {
    method: 'PUT', headers: h,
    body: JSON.stringify({ message, content: Buffer.from(content).toString('base64'), sha, branch, committer: { name: 'KINOFORGE Studio', email: 'Eouchi147@users.noreply.github.com' } }),
  });
  if (!r.ok) throw Object.assign(new Error(`GitHub ${r.status}: ${(await r.text()).slice(0, 200)}`), { code: 'github' });
  return (await r.json()).content?.html_url;
}

const headers = (token) => ({ Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'User-Agent': 'kinoforge-studio' });

/** Read a JSON file from the repo, never cached. Returns null if it does not exist. */
export async function readJSON(path, ref = 'main') {
  const token = process.env.GITHUB_TOKEN;
  const url = `https://api.github.com/repos/${REPO}/contents/${path}?ref=${ref}&_=${Date.now()}`;
  let r = await fetch(url, { headers: { ...(token ? headers(token) : { 'User-Agent': 'kinoforge-studio' }), Accept: 'application/vnd.github.raw+json' }, cache: 'no-store', signal: AbortSignal.timeout(9000) });
  if (r.status === 401 && token) r = await fetch(url, { headers: { 'User-Agent': 'kinoforge-studio', Accept: 'application/vnd.github.raw+json' }, cache: 'no-store', signal: AbortSignal.timeout(9000) });   // a rejected token: the repo is public
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

// ------------------------------------------------------------------ read-only helpers for the studio OS
const anyHeaders = (extra = {}, anon = false) => { const t = anon ? null : process.env.GITHUB_TOKEN; return { ...(t ? headers(t) : { 'User-Agent': 'kinoforge-studio', Accept: 'application/vnd.github+json' }), ...extra }; };
/** A read of the public API: with the token when there is one, and again without it if GitHub rejects the token. */
async function apiGet(url, opts) {
  const r = await fetch(url, { headers: anyHeaders(), ...opts, signal: AbortSignal.timeout(12000) });
  if (r.status !== 401 || !process.env.GITHUB_TOKEN) return r;
  return fetch(url, { headers: anyHeaders({}, true), ...opts, signal: AbortSignal.timeout(12000) });
}

/** A text file from main through raw.githubusercontent.com (public repo, no API quota). null when missing. */
export async function readRaw(path, { revalidate = 60, repo = REPO, ref = 'main' } = {}) {
  const r = await fetch(`https://raw.githubusercontent.com/${repo}/${ref}/${path.split('/').map(encodeURIComponent).join('/')}`, { headers: { 'User-Agent': 'kinoforge-studio' }, next: { revalidate }, signal: AbortSignal.timeout(9000) });
  if (r.status === 404) return null;
  if (!r.ok) throw Object.assign(new Error(`GitHub ${r.status}`), { code: 'github' });
  return r.text();
}

/** The newest Actions runs of a repo (public repos read without a token). Throws on failure so callers can say so. */
export async function repoRuns(repo, perPage = 15) {
  const r = await apiGet(`https://api.github.com/repos/${repo}/actions/runs?per_page=${perPage}`, { next: { revalidate: 20 } });
  if (!r.ok) throw Object.assign(new Error(r.status === 403 ? 'GitHub rate limit reached' : `GitHub ${r.status}`), { code: 'github' });
  return (await r.json()).workflow_runs || [];
}

/** Folder listing on main (contents API): [{name, type, path}]. */
export async function listDir(path, { revalidate = 30, ref = 'main' } = {}) {
  const r = await apiGet(`https://api.github.com/repos/${REPO}/contents/${path}?ref=${encodeURIComponent(ref)}`, { next: { revalidate } });
  if (r.status === 404) return [];
  if (!r.ok) throw Object.assign(new Error(r.status === 403 ? 'GitHub rate limit reached' : `GitHub ${r.status}`), { code: 'github' });
  const j = await r.json();
  return Array.isArray(j) ? j.map(({ name, type, path: p }) => ({ name, type, path: p })) : [];
}

/** Every file path on main (one call, cached five minutes). */
export async function treePaths({ revalidate = 300 } = {}) {
  const r = await apiGet(`https://api.github.com/repos/${REPO}/git/trees/main?recursive=1`, { next: { revalidate } });
  if (!r.ok) throw Object.assign(new Error(r.status === 403 ? 'GitHub rate limit reached' : `GitHub ${r.status}`), { code: 'github' });
  return ((await r.json()).tree || []).filter((t) => t.type === 'blob').map((t) => t.path);
}
