'use client';
// Small pieces every app uses.
import { clock, STATUS_NAMES } from '@/lib/catalog.mjs';
import { Icon } from './icons';

export function Head({ title, lede, children }) {
  return (
    <header className="head">
      <div><h1>{title}</h1>{lede && <p className="lede">{lede}</p>}</div>
      {children && <div className="head-acts">{children}</div>}
    </header>
  );
}

export function Panel({ title, count, action, children, className = '', id }) {
  return (
    <section className={'panel ' + className} aria-labelledby={title ? id || undefined : undefined}>
      {(title || action) && <div className="panel-head">{title && <h2 id={id}>{title}{count != null && <span className="count">{count}</span>}</h2>}{action}</div>}
      {children}
    </section>
  );
}

const isSheet = (src) => /-sheet\.jpg|\.contact\.jpg/.test(decodeURIComponent(src || ''));

/** Contact sheets often fill only part of their canvas (the rest is black): find the frames and crop to them, like
 *  object-fit: cover on the part that has picture. Same-origin images only (/api/media), so the canvas can read them. */
function cropToPicture(img) {
  try {
    const W = img.naturalWidth, H = img.naturalHeight; if (!W || !H) return;
    const w = 160, h = Math.max(1, Math.round((H / W) * w));
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(img, 0, 0, w, h);
    const d = g.getImageData(0, 0, w, h).data;
    let x0 = w, y0 = h, x1 = -1, y1 = -1;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const i = (y * w + x) * 4; if (d[i] + d[i + 1] + d[i + 2] > 45) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; } }
    if (x1 < 0) return;
    const bx = x0 / w, by = y0 / h, bw = (x1 - x0 + 1) / w, bh = (y1 - y0 + 1) / h;
    if (bw * bh > 0.85) return;                                        // already full: leave it
    const box = img.parentElement.getBoundingClientRect(); const tw = box.width, th = box.height; if (!tw || !th) return;
    const s = (bw * W) / (bh * H) > tw / th ? th / (bh * H) : tw / (bw * W);   // cover the tile with the picture part
    const iw = W * s, ih = H * s;
    Object.assign(img.style, { inset: 'auto', objectFit: 'fill', inlineSize: `${(iw / tw) * 100}%`, blockSize: `${(ih / th) * 100}%`, maxInlineSize: 'none',
      left: `${((-bx * iw + (tw - bw * iw) / 2) / tw) * 100}%`, top: `${((-by * ih + (th - bh * ih) / 2) / th) * 100}%` });
  } catch { /* a cross-origin or broken image: show it as it is */ }
}

/** A frame for any poster: 16:9 fills, 9:16 sits in the middle over a soft blur of itself. */
export function Poster({ src, format = '16:9', alt = '', label, children, ratio = '16 / 9' }) {
  const sheet = isSheet(src);
  const tall = format === '9:16' && !sheet;
  return (
    <div className="poster" style={{ aspectRatio: ratio }}>
      {src ? (
        <>
          {tall && <img className="bd" src={src} alt="" aria-hidden="true" loading="lazy" />}
          <img className={tall ? 'tall' : ''} src={src} alt={alt} loading="lazy" onLoad={sheet ? (e) => cropToPicture(e.currentTarget) : undefined} onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }} />
        </>
      ) : <div className="noposter">{label}</div>}
      {children}
    </div>
  );
}

export function FilmTile({ f, verdict, compact }) {
  const v = verdict || (f.verdict ? 'noted' : null);
  return (
    <a className={'tile' + (compact ? ' compact' : '')} href={`#/library/${f.id}`}>
      <Poster src={f.posterUrl} format={f.format} label={f.title}>
        <span className="tc">{f.format}{f.duration_s ? `  ${clock(f.duration_s)}` : ''}</span>
        <span className="playmark" aria-hidden="true"><Icon.play size={16} /></span>
      </Poster>
      <span className="tile-meta">
        <b>{f.title}</b>
        <span>{[f.series, f.look && `look ${f.look}`].filter(Boolean).join(', ')}</span>
        <span className="tile-state">
          <StatusPill status={f.status} />
          {v === 'approved' && <span className="pill ok">Approved</span>}
          {v === 'changes' && <span className="pill warn">Changes asked</span>}
          {f.live && <span className="pill">From the pipeline</span>}
        </span>
      </span>
    </a>
  );
}

export function StatusPill({ status }) {
  return <span className={'pill s-' + status}>{STATUS_NAMES[status] || status}</span>;
}

export function Led({ s }) { return <i className={'led ' + (s || '')} aria-hidden="true" />; }

export function Seg({ value, options, onChange, label }) {
  return (
    <div className="seg" role="radiogroup" aria-label={label}>
      {options.map(([v, l, n]) => (
        <button key={v} role="radio" aria-checked={value === v} className={value === v ? 'on' : ''} onClick={() => onChange(v)}>
          {l}{n != null && <span className="n">{n}</span>}
        </button>
      ))}
    </div>
  );
}

export function Empty({ children }) { return <p className="empty">{children}</p>; }
export function Note({ tone = '', children, role = 'status' }) { return <p className={'note ' + tone} role={role}>{children}</p>; }
