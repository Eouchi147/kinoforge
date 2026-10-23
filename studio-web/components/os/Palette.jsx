'use client';
// The command bar: type to search everything, or say what to do in plain words. Enter runs the first line.
import { useEffect, useMemo, useRef, useState } from 'react';
import { interpret, search } from '@/lib/commands.mjs';
import { useOS } from './store';
import { Icon } from './icons';

const KIND = { app: 'App', action: 'Do', film: 'Film', style: 'Style', look: 'Look', doc: 'Manual', music: 'Music', example: 'Example' };

/** Manual pages known without the network: the guide, the manual's front door, and every recipe in the catalog. */
export function fallbackDocs(catalog) {
  const seen = new Set(); const out = [];
  const add = (path, title) => { if (path && !seen.has(path)) { seen.add(path); out.push({ path, title }); } };
  add('docs/GUIDE.md', 'Guide: the studio in short'); add('docs/manual/README.md', 'Manual: start here');
  for (const s of catalog?.styles || []) add(s.recipe, `Recipe: ${s.name}`);
  for (const f of catalog?.films || []) add(f.recipe, `Recipe: ${f.title}`);
  for (const w of catalog?.workflows || []) add(w.doc, `Workflow: ${w.name}`);
  return out;
}

export function Palette({ initial = '', close }) {
  const { catalog, docs, needDocs, go } = useOS();
  const [text, setText] = useState(initial);
  const [active, setActive] = useState(0);
  const input = useRef(null);
  useEffect(() => { needDocs(); const prev = document.activeElement; input.current?.focus(); document.body.classList.add('noscroll'); return () => { document.body.classList.remove('noscroll'); prev?.focus?.(); }; }, []);
  const ctx = useMemo(() => ({ films: catalog?.films || [], styles: catalog?.styles || [], music: catalog?.music || [], docs: docs?.length ? docs : fallbackDocs(catalog) }), [catalog, docs]);
  const items = useMemo(() => {
    const cmd = interpret(text, ctx);
    const rest = cmd ? text.trim().replace(/^\S+\s*/, '') : text;            // after a command word, search the rest
    const found = (cmd && !rest ? [] : search(rest, ctx, 12)).filter((r) => !cmd || r.route !== cmd.route);
    return cmd ? [cmd, ...found] : found;
  }, [text, ctx]);
  useEffect(() => { setActive(0); }, [text]);

  const run = (it) => {
    if (!it) return;
    if (it.fill) { setText(it.fill); input.current?.focus(); return; }
    close(); go(it.route);
  };
  const onKey = (e) => {
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); setActive((a) => Math.min(items.length - 1, a + 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive((a) => Math.max(0, a - 1)); }
    else if (e.key === 'Enter') { e.preventDefault(); run(items[active]); }
    else if (e.key === 'Tab') { e.preventDefault(); }   // focus stays in the bar while it is open
  };
  useEffect(() => { document.getElementById(`pal-${active}`)?.scrollIntoView({ block: 'nearest' }); }, [active]);

  return (
    <div className="pal-scrim" onMouseDown={close}>
      <div className="palette" role="dialog" aria-modal="true" aria-label="Command bar" onMouseDown={(e) => e.stopPropagation()}>
        <div className="pal-input">
          <Icon.search />
          <input ref={input} value={text} onChange={(e) => setText(e.target.value)} onKeyDown={onKey} role="combobox" aria-expanded="true" aria-controls="pal-list"
            aria-activedescendant={items[active] ? `pal-${active}` : undefined} aria-autocomplete="list" placeholder="Try: new cutaway loop 9:16 fable" spellCheck={false} autoComplete="off" />
          <button className="iconbtn" onClick={close} aria-label="Close the command bar"><Icon.close /></button>
        </div>
        <ul id="pal-list" role="listbox" aria-label="Results">
          {items.map((it, i) => (
            <li key={`${it.type}-${it.id}-${i}`} id={`pal-${i}`} role="option" aria-selected={i === active} className={i === active ? 'on' : ''} onMouseEnter={() => setActive(i)} onClick={() => run(it)}>
              <span className={'kind k-' + it.type}>{KIND[it.type] || it.type}</span>
              <span className="lbl">{it.label}</span>
              {it.hint && <span className="hint">{it.hint}</span>}
            </li>
          ))}
          {!items.length && <li className="none" role="option" aria-selected="false" aria-disabled="true">Nothing matches. Try a film name, a look, or words like "new", "open", "show", "manual", "compare".</li>}
        </ul>
        <p className="pal-foot"><kbd>Enter</kbd> run <kbd>Up</kbd><kbd>Down</kbd> move <kbd>Esc</kbd> close</p>
      </div>
    </div>
  );
}
