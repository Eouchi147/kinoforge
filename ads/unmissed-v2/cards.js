// Notification cards for "The Catch": dark-glass rounded planes with a canvas texture (icon, bold title, one line).
// Text is drawn at 1024 x 384 so it stays crisp when a card sweeps close to the camera.
import * as THREE from 'three';

export const CARD_W = 3.2, CARD_H = 1.2;
export const KINDS = {
  call:    { title: 'Incoming call', line: '21:47', icon: 'phone', tone: '#79b4ff', tag: 'now' },
  message: { title: 'New message', line: 'table for 6 tonight?', icon: 'chat', tone: '#79b4ff', tag: 'now' },
  lead:    { title: 'New lead', line: 'catering for 40', icon: 'user', tone: '#79b4ff', tag: 'now' },
  missed:  { title: 'Missed call', line: '18:32', icon: 'missed', tone: '#ff6b6b', tag: '18:32' },
  enquiry: { title: 'New enquiry', line: 'from your website', icon: 'globe', tone: '#79b4ff', tag: 'now' },
};
export const KIND_LIST = Object.keys(KINDS);

const PHONE = 'M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z';
const ICONS = {
  phone: [PHONE],
  missed: [PHONE, 'M23 1l-6 6', 'M17 1l6 6'],
  chat: ['M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z'],
  user: ['M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2', 'M12.5 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0z', 'M20 8v6', 'M23 11h-6'],
  globe: ['M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0z', 'M2 12h20', 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z'],
};

function rr(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

export function cardTexture(kind, renderer) {
  const K = KINDS[kind], W = 1024, H = 384, c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  g.clearRect(0, 0, W, H);
  // glass body: #0b1122 at about 90%, a faint diagonal sheen, a 1 px #79b4ff edge (3 px in texture space)
  rr(g, 6, 6, W - 12, H - 12, 56);
  const body = g.createLinearGradient(0, 0, W, H); body.addColorStop(0, 'rgba(18,28,52,.93)'); body.addColorStop(0.55, 'rgba(11,17,34,.92)'); body.addColorStop(1, 'rgba(8,13,28,.92)');
  g.fillStyle = body; g.fill();
  g.save(); g.clip();
  const sh = g.createLinearGradient(0, 0, W * 0.9, H * 1.4); sh.addColorStop(0, 'rgba(255,255,255,0)'); sh.addColorStop(0.18, 'rgba(160,200,255,.10)'); sh.addColorStop(0.34, 'rgba(255,255,255,0)');
  g.fillStyle = sh; g.fillRect(0, 0, W, H);
  const glowL = g.createRadialGradient(150, 192, 10, 150, 192, 330); glowL.addColorStop(0, K.tone === '#ff6b6b' ? 'rgba(255,107,107,.16)' : 'rgba(47,125,246,.20)'); glowL.addColorStop(1, 'rgba(47,125,246,0)');
  g.fillStyle = glowL; g.fillRect(0, 0, W, H);
  g.restore();
  rr(g, 6, 6, W - 12, H - 12, 56); g.lineWidth = 3.5; g.strokeStyle = 'rgba(121,180,255,.78)'; g.stroke();
  rr(g, 11, 11, W - 22, H - 22, 52); g.lineWidth = 1.5; g.strokeStyle = 'rgba(255,255,255,.07)'; g.stroke();
  // icon tile
  const ix = 56, iy = 72, is = 240;
  rr(g, ix, iy, is, is, 62); g.fillStyle = K.tone === '#ff6b6b' ? 'rgba(255,107,107,.14)' : 'rgba(47,125,246,.20)'; g.fill();
  g.lineWidth = 3; g.strokeStyle = K.tone === '#ff6b6b' ? 'rgba(255,107,107,.55)' : 'rgba(121,180,255,.45)'; g.stroke();
  g.save(); g.translate(ix + is / 2 - 12 * 6.6, iy + is / 2 - 12 * 6.6); g.scale(6.6, 6.6);
  g.lineWidth = 2.1; g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = K.tone;
  for (const d of ICONS[K.icon]) g.stroke(new Path2D(d));
  g.restore();
  // words
  const tx = ix + is + 54;
  g.textBaseline = 'alphabetic'; g.fillStyle = '#f4f6fb'; g.font = '700 74px Inst, sans-serif';
  g.fillText(K.title, tx, 168);
  g.fillStyle = '#c3cad8'; g.font = '500 52px Inst, sans-serif';
  g.fillText(K.line, tx, 250);
  g.fillStyle = K.tone === '#ff6b6b' ? '#ff9a9a' : '#98a1b5'; g.font = '500 30px Mono, monospace';
  g.textAlign = 'right'; g.fillText(K.tag, W - 64, 82); g.textAlign = 'left';
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.generateMipmaps = true;
  tex.minFilter = THREE.LinearMipmapLinearFilter; return tex;
}

export function glowTexture() {
  const W = 512, H = 256, c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  g.shadowColor = 'rgba(80,150,255,1)'; g.shadowBlur = 70; g.fillStyle = 'rgba(60,130,255,.9)';
  rr(g, 120, 78, W - 240, H - 156, 30); g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function radialTexture(stops) {
  const S = 256, c = document.createElement('canvas'); c.width = c.height = S; const g = c.getContext('2d');
  const gr = g.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2); for (const [o, col] of stops) gr.addColorStop(o, col);
  g.fillStyle = gr; g.fillRect(0, 0, S, S); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

// One card: a mesh (its own material, so opacity is per card) and a soft glow plane behind it.
export function makeCard(kind, tex, glowTex, geo, glowGeo) {
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, fog: true, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false;
  const gm = new THREE.MeshBasicMaterial({ map: glowTex, transparent: true, depthWrite: false, fog: true, blending: THREE.AdditiveBlending, opacity: 0.22 });
  const glow = new THREE.Mesh(glowGeo, gm); glow.position.z = -0.03; glow.frustumCulled = false; mesh.add(glow);
  mesh.userData = { kind, mat, gm };
  return mesh;
}
