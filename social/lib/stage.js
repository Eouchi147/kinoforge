// social/lib/stage.js: the 9:16 stage every social template shares (browser only; rendered by harness/dom-render.cjs).
//
//   const S = await boot(document.querySelector('#stage'));   // brief, brand, photo, logo, fonts, theme
//   ...build the scene from S.brief.card, then window.KF = { duration, fps: 30, cover, render(i, t) }; window.KF_READY = true
//
// The brief comes from the URL: ?brief=/social/batches/<client>/<batch>/batch.json&id=<video id> (one entry of a batch),
// or ?brief=<path to one brief>, or nothing (the template's own ./sample.json). dom-render passes them with --param.
// Everything a template draws is a pure function of t, so any frame renders on its own and identically every run.
import { fitStage, clamp } from '/ads/lib/motion.js';
import { FRAME, resolveVideo, safeBox, briefProblems } from '/social/lib/brief.mjs';

export const SAFE = safeBox();
const json = async (u) => { const r = await fetch(u); if (!r.ok) throw new Error(`${u}: ${r.status}`); return r.json(); };
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export async function boot(stage) {
  const q = fitStage(stage, FRAME);
  const doc = await json(q.get('brief') || './sample.json');
  const brief = resolveVideo(doc, q.get('id'));
  const base = `/social/clients/${brief.client}`;
  const [brand, media, tpl] = await Promise.all([json(`${base}/brand.json`), json(`${base}/media/media.json`), json('./template.json')]);
  const bad = briefProblems(brief, brand, { photos: media.photos.map((p) => p.file) });
  if (bad.length) throw new Error('brief: ' + bad.join('; '));
  const photo = { ...media.photos.find((p) => p.file === brief.photo) }; photo.url = `${base}/media/${photo.file}`;
  // theme: the brand's colours and fonts as CSS variables (--navy, --blue, ... and --display, --text, --mono)
  const root = document.documentElement.style;
  for (const [k, v] of Object.entries(brand.colors)) root.setProperty('--' + k, v);
  const faces = [];
  for (const [role, f] of Object.entries(brand.fonts)) {
    root.setProperty('--' + role, `'${f.family}', sans-serif`);
    const ff = new FontFace(f.family, `url(${f.file})`, { weight: f.weight || '100 900' }); document.fonts.add(ff); faces.push(ff.load());
  }
  const [logo] = await Promise.all([fetch(`${base}/${brand.logo}`).then((r) => r.text()), ...faces, loadImage(photo.url)]);
  await document.fonts.ready;
  if (q.get('guides')) guides(stage);
  window.KF_TEXT = () => visibleText(stage);
  return { q, brief, brand, photo, logo, tpl, card: brief.card };
}

export function loadImage(src) {
  return new Promise((res, rej) => { const im = new Image(); im.onload = () => (im.decode ? im.decode().then(() => res(im), () => res(im)) : res(im)); im.onerror = () => rej(new Error('image ' + src)); im.src = src; });
}

// The brand mark, inlined (an <img> of this SVG loses its gradient), with its ids made unique per copy.
let markN = 0;
export function markSVG(svgText) {
  const k = 'mk' + (++markN);
  return svgText.replace(/<\?xml[^>]*\?>/, '').replace(/<!--[\s\S]*?-->/g, '').replace(/id="([^"]+)"/g, `id="$1-${k}"`).replace(/url\(#([^)]+)\)/g, `url(#$1-${k})`)
    .replace('<svg ', '<svg width="100%" height="100%" ');
}

// The mark assembles itself, ending exactly on the original drawing (only translate and scale on its own parts; nothing is
// redrawn). brand.mark_build names the SVG's drawable children by index: { ground: [0], mount: [1, 2], screen: [3, 4, 5],
// centre: [256, 256] }. Without it the whole mark scales in. p runs 0 to 1 (about a second).
export function markBuilder(holder, build) {
  const svg = holder.querySelector('svg'), parts = [...svg.querySelectorAll('circle, rect, path, ellipse, polygon')];
  const pick = (k) => ((build && build[k]) || []).map((i) => parts[i]).filter(Boolean);
  const G = { ground: pick('ground'), mount: pick('mount'), screen: pick('screen') }, [cx, cy] = (build && build.centre) || [256, 256];
  const setT = (els, tr) => els.forEach((e) => (tr ? e.setAttribute('transform', tr) : e.removeAttribute('transform')));
  const outBack = (p, s = 1.6) => 1 + (s + 1) * Math.pow(p - 1, 3) + s * Math.pow(p - 1, 2), outExpo = (p) => (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p));
  const sg = (p, a, b) => clamp((p - a) / (b - a));
  return (p) => {
    if (!build) { holder.style.opacity = clamp(p * 4); holder.style.transform = `scale(${0.7 + 0.3 * outBack(clamp(p), 1.4)})`; return; }
    holder.style.opacity = p > 0 ? 1 : 0;
    const g = outBack(sg(p, 0, 0.42), 1.5), m = outExpo(sg(p, 0.22, 0.58)), s = outBack(sg(p, 0.42, 0.86), 1.25);
    setT(G.ground, g >= 1 && p >= 0.42 ? null : `translate(${cx} ${cy}) scale(${Math.max(0, g)}) translate(${-cx} ${-cy})`);
    G.mount.forEach((e) => e.setAttribute('opacity', clamp(m * 1.5))); setT(G.mount, m >= 1 ? null : `translate(${-70 * (1 - m)} 0)`);
    G.screen.forEach((e) => e.setAttribute('opacity', clamp(sg(p, 0.42, 0.52)))); setT(G.screen, s >= 1 && p >= 0.86 ? null : `translate(${110 * (1 - s)} ${-26 * (1 - s)})`);
  };
}

// Frame a photo in a box so its television (photo.tv, fractions) sits at (ax, ay) of the box, at the smallest scale that
// both covers the box and allows that placement (capped, so a room never turns into a texture), times `zoom`.
// Returns the image size and offset in box px, and where the TV lands.
export function framePhoto(ph, boxW, boxH, { ax = 0.5, ay = 0.45, zoom = 1, cap = 1.5 } = {}) {
  const cover = Math.max(boxW / ph.w, boxH / ph.h);
  const [x0, y0, x1, y1] = ph.tv, mx = (x0 + x1) / 2, my = (y0 + y1) / 2, wx = ax * boxW, wy = ay * boxH;
  const need = Math.max(cover, wy / (my * ph.h), (boxH - wy) / ((1 - my) * ph.h), wx / (mx * ph.w), (boxW - wx) / ((1 - mx) * ph.w));
  const s = Math.min(need, cover * cap) * zoom, w = ph.w * s, h = ph.h * s;
  const x = clamp(wx - mx * w, boxW - w, 0), y = clamp(wy - my * h, boxH - h, 0);
  return { s, w, h, x, y, tv: { x0: x + x0 * w, y0: y + y0 * h, x1: x + x1 * w, y1: y + y1 * h, cx: x + mx * w, cy: y + my * h } };
}
// Apply a frame to an <img> (absolute inside its box).
export function placeImg(img, f) { Object.assign(img.style, { position: 'absolute', left: f.x + 'px', top: f.y + 'px', width: f.w + 'px', height: f.h + 'px', maxWidth: 'none' }); }

// Masked words: <span class=m><span class=w>word</span></span>; returns the inner spans (move them with motion.js rise()).
export function maskWords(el, text = el.textContent) {
  el.innerHTML = String(text).trim().split(/\s+/).map((w) => `<span class="m"><span class="w">${esc(w)}</span></span>`).join(' ');
  return [...el.querySelectorAll('.w')];
}
// Masked lines: the text as the browser wraps it (fonts must be loaded), one mask per line; returns the inner spans.
export function maskLines(el, text = el.textContent) {
  const ws = String(text).trim().split(/\s+/);
  el.innerHTML = ws.map((w) => `<span class="lw">${esc(w)}</span>`).join(' ');
  const rows = [];
  for (const s of el.querySelectorAll('.lw')) { let r = rows.find((x) => Math.abs(x.top - s.offsetTop) < 6); if (!r) rows.push(r = { top: s.offsetTop, w: [] }); r.w.push(s.textContent); }
  el.innerHTML = rows.map((r) => `<span class="ln"><span>${r.w.map(esc).join(' ')}</span></span>`).join('');
  return [...el.querySelectorAll('.ln > span')];
}
// Largest font size (px, integer) in [min, max] at which `fits()` holds; the element keeps it. Throws if even min fails.
export function fitFont(el, min, max, fits, what = 'text') {
  let lo = min, hi = max, ok = null;
  while (lo <= hi) { const mid = (lo + hi) >> 1; el.style.fontSize = mid + 'px'; if (fits()) { ok = mid; lo = mid + 1; } else hi = mid - 1; }
  if (ok == null) throw new Error(`${what} does not fit even at ${min}px: shorten the words rather than shrinking the type`);
  el.style.fontSize = ok + 'px'; return ok;
}
// How far below an element's top its text really reaches (glyph boxes, not the line box: with tight line-height the
// descenders hang below the box), in stage px. Use it to anchor text to the bottom of the safe box.
export function textBottom(el) {
  const k = stageScale(el), top = el.getBoundingClientRect().top, rg = document.createRange(); rg.selectNodeContents(el);
  let b = 0; for (const r of rg.getClientRects()) b = Math.max(b, r.bottom); return (b - top) / k;
}
export const lineCount = (el) => { const lh = parseFloat(getComputedStyle(el).lineHeight) || parseFloat(getComputedStyle(el).fontSize) * 1.2; return Math.round(el.getBoundingClientRect().height / lh / stageScale(el)); };
export const stageScale = (el) => { const st = el.closest('#stage'); return st ? st.getBoundingClientRect().width / 1080 : 1; };

// Review overlay: the platform zones in red, the word-safe box dashed.
export function guides(stage) {
  const g = document.createElement('div'); g.id = 'guides';
  const z = [[0, 0, FRAME.w, SAFE.y0], [0, SAFE.y1, FRAME.w, FRAME.h - SAFE.y1], [0, SAFE.y0, SAFE.x0, SAFE.y1 - SAFE.y0], [SAFE.x1, SAFE.y0, FRAME.w - SAFE.x1, SAFE.y1 - SAFE.y0]];
  g.innerHTML = z.map(([x, y, w, h]) => `<i style="left:${x}px;top:${y}px;width:${w}px;height:${h}px"></i>`).join('') +
    `<b style="left:${SAFE.x0}px;top:${SAFE.y0}px;width:${SAFE.x1 - SAFE.x0}px;height:${SAFE.y1 - SAFE.y0}px"></b>`;
  stage.appendChild(g);
}

// How visible an element is right now: the product of its ancestors' opacity and the box their overflow masks leave
// (clip-path is ignored, so the answer errs on the side of "visible"). null when it is not displayed at all.
function seen(el, stage, sr) {
  let op = 1, clip = { l: sr.left, t: sr.top, r: sr.right, b: sr.bottom };
  for (let e = el; e && e !== document.body; e = e.parentElement) {
    const cs = getComputedStyle(e);
    if (cs.display === 'none') return null;
    op *= parseFloat(cs.opacity);
    if (cs.overflow !== 'visible' || cs.overflowX !== 'visible' || cs.overflowY !== 'visible') {
      const r = e.getBoundingClientRect(); clip = { l: Math.max(clip.l, r.left), t: Math.max(clip.t, r.top), r: Math.min(clip.r, r.right), b: Math.min(clip.b, r.bottom) };
    }
    if (e === stage) break;
  }
  return getComputedStyle(el).visibility === 'hidden' || op < 0.04 ? null : { op, clip };
}
// Everything that must stay in the safe zone and is visible right now, in stage px: every piece of text (words, numbers,
// URLs) and every element tagged data-safe (logo marks; faces would be tagged the same way; our photos have none).
// social/lib/safecheck.mjs steps through a video frame by frame and flags anything outside SAFE.
export function visibleText(stage) {
  const sr = stage.getBoundingClientRect(), k = sr.width / FRAME.w, out = [];
  const push = (text, kind, op, r, clip) => {
    const l = Math.max(r.left, clip.l), t = Math.max(r.top, clip.t), rr = Math.min(r.right, clip.r), b = Math.min(r.bottom, clip.b);
    if (rr - l > 1 && b - t > 1) out.push({ text, kind, op: +op.toFixed(2), x0: (l - sr.left) / k, y0: (t - sr.top) / k, x1: (rr - sr.left) / k, y1: (b - sr.top) / k });
  };
  const tw = document.createTreeWalker(stage, NodeFilter.SHOW_TEXT);
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    if (!n.textContent.trim() || n.parentElement.closest('#guides,svg,style,script')) continue;
    const v = seen(n.parentElement, stage, sr); if (!v) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    for (const r of rg.getClientRects()) push(n.textContent.trim().slice(0, 48), 'text', v.op, r, v.clip);
  }
  for (const el of stage.querySelectorAll('[data-safe]')) {
    const v = seen(el, stage, sr); if (v) push(`[${el.dataset.safe} ${el.id || el.className}]`, el.dataset.safe, v.op, el.getBoundingClientRect(), v.clip);
  }
  return out;
}
