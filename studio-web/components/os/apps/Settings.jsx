'use client';
// Settings: the write lock, connections, money caps and the catalog's source. Read only where a change needs a key:
// keys are added by Sam on Vercel or GitHub, never here.
import { useState } from 'react';
import { useOS, usd } from '../store';
import { Head, Panel, Note, Led } from '../ui';
import { Icon } from '../icons';

const VERCEL_ENV = 'https://vercel.com/samkeamy-7230s-projects/kinoforge-studio/settings/environment-variables';

export function Settings() {
  const { status, statusError, lock, reloadLock, catalog } = useOS();
  const [pass, setPass] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);
  const unlock = async (e) => {
    e.preventDefault(); setBusy(true); setMsg(null);
    try {
      const r = await fetch('/api/unlock', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ passcode: pass }) });
      const j = await r.json();
      if (j.unlocked) { setPass(''); setMsg({ tone: 'ok', text: 'Unlocked on this browser for 90 days.' }); } else setMsg({ tone: 'bad', text: j.error || 'That did not work.' });
    } catch { setMsg({ tone: 'bad', text: 'The studio did not answer. Try again.' }); }
    await reloadLock(); setBusy(false);
  };
  const relock = async () => { await fetch('/api/unlock', { method: 'DELETE' }); await reloadLock(); setMsg({ tone: '', text: 'This browser is locked again.' }); };
  const a = status?.account, caps = status?.caps, seats = status?.seats || {};
  const n = (id) => (id || 'none').split('/').pop();

  return (
    <div className="app settings">
      <Head title="Settings" lede="The lock, the connections and what the studio may spend. Keys are added on Vercel or GitHub by you, never on this page." />
      <div className="settings-grid">
        <Panel title="Write lock" id="h-lock">
          {!lock && <p className="dim">Reading</p>}
          {lock && !lock.required && (
            <>
              <Note tone="warn"><b>Writes are open.</b> Anyone with this page's link can start builds (which spend money), talk to the director and save reviews.</Note>
              <ol className="howto">
                <li>Open the <a href={VERCEL_ENV} target="_blank" rel="noreferrer">studio's environment variables on Vercel</a>.</li>
                <li>Add <code>STUDIO_PASSCODE</code> with a passphrase only you know (four or more words). Save.</li>
                <li>Redeploy (or push anything to main). Then type the passphrase here once on each device.</li>
              </ol>
            </>
          )}
          {lock?.required && !lock.unlocked && (
            <form className="unlock" onSubmit={unlock}>
              <p><Led s="warn" /> Locked. Reading is open; building, the director chat and saving reviews need the passcode.</p>
              <label htmlFor="pass">Passcode</label>
              <div className="row">
                <input id="pass" type="password" autoComplete="current-password" value={pass} onChange={(e) => setPass(e.target.value)} />
                <button className="btn primary" disabled={busy || !pass}><Icon.unlock size={16} />Unlock</button>
              </div>
            </form>
          )}
          {lock?.required && lock.unlocked && (
            <div className="row-between"><p><Led s="ok" /> Unlocked on this browser.</p><button className="btn" onClick={relock}><Icon.lock size={16} />Lock this browser</button></div>
          )}
          {msg && <Note tone={msg.tone}>{msg.text}</Note>}
        </Panel>

        <Panel title="Connections" id="h-conn">
          {statusError && <Note tone="warn">The studio's status did not load: {statusError}</Note>}
          <ul className="conn">
            <li><Led s={status?.openrouter ? 'ok' : status ? 'off' : ''} /><div><b>Director (OpenRouter)</b><span className="dim small">{status?.openrouter ? `Online. Head seat: ${n(seats.head?.[0])}.` : 'Not connected: the chat cannot answer.'}</span></div></li>
            <li><Led s={status?.github ? 'ok' : status ? 'off' : ''} /><div><b>GitHub (writes)</b><span className="dim small">{status?.github ? 'Connected: builds start and reviews save to the repo.' : 'Read only: builds cannot start and reviews stay on the device.'}</span></div></li>
            <li><Led s="ok" /><div><b>GitHub (reads)</b><span className="dim small">Public repos: films, runs and the manual are read without a key.</span></div></li>
          </ul>
          <details className="how">
            <summary>How to connect the director</summary>
            <ol className="howto">
              <li>Open <a href="https://openrouter.ai/settings/keys" target="_blank" rel="noreferrer">openrouter.ai/settings/keys</a>, create a key named <code>KINOFORGE</code> with a credit limit, copy it.</li>
              <li>On <a href={VERCEL_ENV} target="_blank" rel="noreferrer">Vercel</a>, add <code>OPENROUTER_API_KEY</code> with the key as its value. Save, then redeploy.</li>
            </ol>
          </details>
          <details className="how">
            <summary>How to connect GitHub writes</summary>
            <ol className="howto">
              <li>Create a <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noreferrer">fine-grained token</a> for <b>Eouchi147/kinoforge</b> only, 90 days, with Contents: Read and write and Actions: Read and write.</li>
              <li>On <a href={VERCEL_ENV} target="_blank" rel="noreferrer">Vercel</a>, add <code>GITHUB_TOKEN</code> with the token as its value. Save, then redeploy.</li>
            </ol>
          </details>
          <details className="how">
            <summary>How builds get their own key</summary>
            <ol className="howto">
              <li>Create a second OpenRouter key named <code>KINOFORGE builds</code> with its own credit limit.</li>
              <li>Add it as the repo secret <code>OPENROUTER_API_KEY</code> on <a href="https://github.com/Eouchi147/kinoforge/settings/secrets/actions/new" target="_blank" rel="noreferrer">GitHub</a>.</li>
            </ol>
          </details>
        </Panel>

        <Panel title="Money" id="h-money2">
          {!status?.openrouter && <p className="dim">The director is not connected, so nothing is spent here.</p>}
          {a?.remaining != null && <p className="bignum">{usd(a.remaining)}<span> left on the studio key{a.limit != null ? ` (limit ${usd(a.limit)})` : ''}</span></p>}
          <dl className="facts">
            {a?.today != null && <><dt>Spent today</dt><dd className="mono">{usd(a.today)}</dd></>}
            <dt>Per message</dt><dd className="mono">{caps ? usd(caps.turn_usd) : 'not read'}</dd>
            <dt>Per day</dt><dd className="mono">{caps ? usd(caps.day_usd) : 'not read'}</dd>
            <dt>Per film</dt><dd>the cap chosen in Create, $0.50 to $5.00, default $2.00</dd>
            {status?.openrouter && <>
              <dt>Head</dt><dd>{n(seats.head?.[0])}</dd>
              <dt>Deputy</dt><dd>{n(seats.deputy?.[0])}</dd>
              <dt>Crew</dt><dd>{(seats.crew || []).slice(0, 3).map(n).join(', ') || 'none'}</dd>
              <dt>Backup</dt><dd>{(seats.free || []).slice(0, 2).map(n).join(', ') || 'none'} (free)</dd>
            </>}
          </dl>
          <p className="dim small">Caps live in studio-web/lib/crew.json and films/director/config.json. Changing them is a code change, on purpose.</p>
          <p><a className="btn" href="#/spend">What every video cost</a></p>
        </Panel>

        <Panel title="Catalog" id="h-cat">
          {!catalog && <p className="dim">Reading</p>}
          {catalog && (
            <>
              {catalog.source === 'fixture'
                ? <Note tone="warn">Showing sample data: public/data/catalog.json is not built yet. Run <code>python3 tools/catalog.py</code> and commit the file.</Note>
                : <p><Led s="ok" /> From public/data/catalog.json, generated {catalog.generated ? catalog.generated.slice(0, 16).replace('T', ' ') + ' UTC' : 'at an unknown time'}.</p>}
              <dl className="facts">
                <dt>Films</dt><dd className="mono">{catalog.films.length}</dd>
                <dt>House styles</dt><dd className="mono">{catalog.house.length}</dd>
                <dt>Cutaway looks</dt><dd className="mono">{catalog.looks.length}</dd>
                <dt>Workflows</dt><dd className="mono">{catalog.workflows.length}</dd>
                <dt>Music</dt><dd className="mono">{catalog.music.length}</dd>
              </dl>
            </>
          )}
        </Panel>
      </div>
    </div>
  );
}
