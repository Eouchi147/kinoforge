'use client';
// A small Markdown renderer that builds React elements (no HTML strings, so nothing in a page can inject markup).
// Enough for the manual: headings, paragraphs, lists (nested by indent), tables, code fences, quotes, rules, inline
// code, bold, italic, links. Links between manual pages open inside the studio; links to repo files open on GitHub.
import { Fragment } from 'react';
import { smooth } from './store';

const BLOB = 'https://github.com/Eouchi147/kinoforge/blob/main/';

/** Resolve a link found in docs/<...>/page.md against the page's folder. */
export function resolveLink(href, from) {
  if (/^(https?:|mailto:)/.test(href)) return { href, external: true };
  if (href.startsWith('#')) return { href: null, anchor: href.slice(1) };
  const [p, hash] = href.split('#');
  const base = from.split('/').slice(0, -1);
  const parts = p.startsWith('/') ? p.slice(1).split('/') : [...base, ...p.split('/')];
  const out = [];
  for (const s of parts) { if (s === '..') out.pop(); else if (s && s !== '.') out.push(s); }
  const path = out.join('/');
  if (/^docs\/(GUIDE\.md|manual\/.+\.md)$/.test(path)) return { href: `#/manual/${path}${hash ? '~' + hash : ''}`, internal: path };
  return { href: BLOB + path + (hash ? '#' + hash : ''), external: true };
}

export const slug = (s) => String(s).toLowerCase().replace(/[`*_]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function inline(text, from, key = 'i') {
  const out = []; let rest = text; let n = 0;
  const re = /(`[^`]+`)|(\*\*[^*]+\*\*|__[^_]+__)|(\*[^*\s][^*]*\*|_[^_\s][^_]*_)|(\[[^\]]+\]\([^)\s]+\))|(<https?:\/\/[^>]+>)/;
  while (rest) {
    const m = re.exec(rest);
    if (!m) { out.push(rest); break; }
    if (m.index) out.push(rest.slice(0, m.index));
    const t = m[0]; const k = `${key}-${n++}`;
    if (m[1]) out.push(<code key={k}>{t.slice(1, -1)}</code>);
    else if (m[2]) out.push(<strong key={k}>{inline(t.slice(2, -2), from, k)}</strong>);
    else if (m[3]) out.push(<em key={k}>{inline(t.slice(1, -1), from, k)}</em>);
    else if (m[4]) {
      const lm = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(t); const L = resolveLink(lm[2], from);
      out.push(L.external
        ? <a key={k} href={L.href} target="_blank" rel="noreferrer">{inline(lm[1], from, k)}</a>
        : <a key={k} href={L.href || `#${L.anchor}`} onClick={L.anchor ? (e) => { e.preventDefault(); document.getElementById(L.anchor)?.scrollIntoView({ behavior: smooth() }); } : undefined}>{inline(lm[1], from, k)}</a>);
    } else if (m[5]) out.push(<a key={k} href={t.slice(1, -1)} target="_blank" rel="noreferrer">{t.slice(1, -1)}</a>);
    rest = rest.slice(m.index + t.length);
  }
  return out;
}

const cells = (line) => line.trim().replace(/^\|/, '').replace(/\|$/, '').split(/(?<!\\)\|/).map((c) => c.trim().replace(/\\\|/g, '|'));

function list(lines, from, k) {
  // lines: [{indent, ordered, text}] -> nested lists
  const root = { children: [] }; const stack = [{ indent: -1, node: root }];
  for (const l of lines) {
    while (stack.length > 1 && l.indent <= stack[stack.length - 1].indent) stack.pop();
    const parent = stack[stack.length - 1].node;
    const item = { text: l.text, ordered: l.ordered, children: [] };
    parent.children.push(item); stack.push({ indent: l.indent, node: item });
  }
  const render = (items, kk) => {
    const Tag = items[0]?.ordered ? 'ol' : 'ul';
    return <Tag key={kk}>{items.map((it, i) => <li key={i}>{inline(it.text, from, `${kk}-${i}`)}{it.children.length ? render(it.children, `${kk}-${i}c`) : null}</li>)}</Tag>;
  };
  return render(root.children, k);
}

export function Markdown({ text, from = 'docs/manual/README.md' }) {
  const L = String(text || '').replace(/\r/g, '').split('\n');
  const out = []; let i = 0; let k = 0;
  while (i < L.length) {
    const line = L[i];
    if (!line.trim()) { i++; continue; }
    const fence = /^\s*(```|~~~)(.*)$/.exec(line);
    if (fence) {
      const body = []; i++;
      while (i < L.length && !L[i].trim().startsWith(fence[1])) body.push(L[i++]);
      i++; out.push(<pre key={k++} tabIndex={0}><code>{body.join('\n')}</code></pre>); continue;
    }
    const h = /^(#{1,6})\s+(.*?)\s*#*$/.exec(line);
    if (h) { const Tag = `h${Math.min(6, h[1].length + 1)}`; out.push(<Tag key={k++} id={slug(h[2])}>{inline(h[2], from, `h${k}`)}</Tag>); i++; continue; }
    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) { out.push(<hr key={k++} />); i++; continue; }
    if (/^\s*\|.*\|\s*$/.test(line) && i + 1 < L.length && /^\s*\|?\s*:?-{2,}/.test(L[i + 1])) {
      const head = cells(line); i += 2; const rows = [];
      while (i < L.length && /^\s*\|.*\|\s*$/.test(L[i])) rows.push(cells(L[i++]));
      const kk = k++;
      out.push(<div className="md-table" key={kk} tabIndex={0} role="region" aria-label="Table"><table><thead><tr>{head.map((c, j) => <th key={j}>{inline(c, from, `t${kk}h${j}`)}</th>)}</tr></thead><tbody>{rows.map((r, ri) => <tr key={ri}>{r.map((c, j) => <td key={j}>{inline(c, from, `t${kk}r${ri}c${j}`)}</td>)}</tr>)}</tbody></table></div>);
      continue;
    }
    if (/^\s*>/.test(line)) {
      const body = []; while (i < L.length && /^\s*>/.test(L[i])) body.push(L[i++].replace(/^\s*>\s?/, ''));
      out.push(<blockquote key={k++}><Markdown text={body.join('\n')} from={from} /></blockquote>); continue;
    }
    if (/^\s*([-*+]|\d+[.)])\s+/.test(line)) {
      const items = [];
      while (i < L.length) {
        const m = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/.exec(L[i]);
        if (m) { items.push({ indent: m[1].replace(/\t/g, '    ').length, ordered: /\d/.test(m[2]), text: m[3] }); i++; continue; }
        if (L[i].trim() && /^\s{2,}\S/.test(L[i]) && items.length) { items[items.length - 1].text += ' ' + L[i].trim(); i++; continue; }
        break;
      }
      out.push(list(items, from, `l${k++}`)); continue;
    }
    const para = [];
    while (i < L.length && L[i].trim() && !/^(#{1,6}\s|\s*```|\s*~~~|\s*>|\s*([-*+]|\d+[.)])\s+|\s*\|.*\|\s*$)/.test(L[i])) para.push(L[i++].trim());
    if (!para.length) { para.push(L[i++].trim()); }
    out.push(<p key={k++}>{inline(para.join(' '), from, `p${k}`)}</p>);
  }
  return <Fragment>{out}</Fragment>;
}

/** Headings of a page, for the in-page outline. */
export function outline(text) {
  return String(text || '').split('\n').map((l) => /^(#{2,3})\s+(.*?)\s*#*$/.exec(l)).filter(Boolean).map((m) => ({ level: m[1].length, text: m[2].replace(/[`*_]/g, ''), id: slug(m[2]) }));
}
