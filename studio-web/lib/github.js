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
