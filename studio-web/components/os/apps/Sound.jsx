'use client';
// Sound: the music library (public-domain pieces with their licence), the sound tools from the catalog, the sound
// pages of the manual, and the narrator takes kept from the early films.
import { useEffect } from 'react';
import { useOS, useFetch } from '../store';
import { Head, Panel, Empty } from '../ui';
import { Icon } from '../icons';
import { createRoute } from '@/lib/commands.mjs';

const SOUNDISH = /score|sfx|sound|music|remux|narrat|voice|mix|audio/i;

export function Sound() {
  const { catalog, docs, needDocs } = useOS();
  const voices = useFetch('/data/voices.json');
  useEffect(() => { needDocs(); }, [needDocs]);
  const tools = (catalog?.workflows || []).filter((w) => SOUNDISH.test(`${w.id} ${w.name} ${w.doc}`));
  const pages = (docs || []).filter((d) => d.path.startsWith('docs/manual/sound/'));
  return (
    <div className="app sound">
      <Head title="Sound" lede="Music the studio may use, the tools that make sound for free, and how each one works." />
      <Panel title="Music library" count={catalog?.music.length ?? null} id="h-music">
        {!catalog && <Empty>Reading the catalog</Empty>}
        {catalog && !catalog.music.length && <Empty>No public-domain pieces are in the library yet.</Empty>}
        <ul className="musiclist">
          {(catalog?.music || []).map((m) => (
            <li key={m.id}>
              <div className="mtxt"><b>{m.title}</b><span className="dim small">{m.licence}. {m.source}.</span></div>
              {m.url ? <audio controls preload="none" src={m.url} aria-label={`Listen to ${m.title}`} /> : <span className="dim small">No file listed</span>}
              <div className="acts">
                {m.download && <a className="btn" href={m.download}><Icon.download size={16} />File</a>}
                <a className="btn" href={'#/' + createRoute({ music: m.id })}>Use in a film</a>
              </div>
            </li>
          ))}
        </ul>
        <p className="dim small">The free score engine makes music in code for every film (US$0). A piece from this library is chosen in Create and written into the brief.</p>
      </Panel>
      <div className="two">
        <Panel title="Sound tools" count={tools.length} id="h-tools">
          {!tools.length && <Empty>The catalog lists no sound tools yet.</Empty>}
          <ul className="toollist">
            {tools.map((w) => (
              <li key={w.id}>
                <b>{w.name}</b><span className="dim small">{w.summary}</span>
                <span className="mono small">{w.run}</span>
                {w.doc && <a href={`#/manual/${w.doc}`} className="small">How it works</a>}
              </li>
            ))}
          </ul>
        </Panel>
        <Panel title="Sound in the manual" count={pages.length || null} id="h-sman">
          {docs === null ? <Empty>Reading the manual</Empty> : !pages.length ? <Empty>No sound pages in the manual yet.</Empty> : null}
          <ul className="doclist">{pages.map((d) => <li key={d.path}><a href={`#/manual/${d.path}`}>{d.title}</a></li>)}</ul>
        </Panel>
      </div>
      <Panel title="Narrator takes from the early films" id="h-voices">
        {voices.loading && <Empty>Reading</Empty>}
        {(voices.data?.films || []).map((f) => (
          <div key={f.id} className="voicefilm">
            <h3>{f.title}</h3>
            {f.takes.map((t) => (
              <div key={t.id} className="take">
                <div><b>{t.name}</b><span className="dim small">{t.summary}</span></div>
                <video src={t.src} controls preload="none" playsInline className="takevid" aria-label={`${f.title}, ${t.name}`} />
              </div>
            ))}
          </div>
        ))}
      </Panel>
    </div>
  );
}
