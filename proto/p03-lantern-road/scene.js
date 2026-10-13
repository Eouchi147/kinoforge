// P03 "THE LANTERN ROAD" — 2.5D painted multiplane, narrated-history look. 12 s, 3 shots (see NOTES.md).
// A lone traveler climbs a mountain road at dusk; lanterns light one by one as he passes; the gate's great lantern answers.
import * as THREE from 'three';
import { boot, makeComposer, drawText, ease, clamp, lerp, smoothstep, noise1 } from '/harness/kit/film.js';
import { makeDetailPass } from './lib.js';
import { buildS1, buildS2, buildS3, igniteEnv, fovV, WARM } from './sets.js';
import { continuousPlan, makePlan, pose, drawTraveler, PAL } from './walker.js';
import { rgba, mixc, hex } from './paint.js';

const TM = await (await fetch('./timing.json')).json();          // shared with audio.py
const FPS = TM.fps, HM = TM.walk.heightM, T = TM.walk.T, STEP = TM.walk.step, V = STEP / T;
const SHOTS = TM.shots.map((s) => ({ name: s.name, dur: s.dur }));
let scene, camera, post, detail, A, B, Cc, W, H, SC; const plans = {}; const tv = new THREE.Vector3();
let figOnly, figOnlyG, rimC, rimG;

const px = (x, y, z) => { tv.set(x, y, z).project(camera); return [(tv.x * 0.5 + 0.5) * W, (-tv.y * 0.5 + 0.5) * H]; };
// local affine map for walk coordinates (H units) on the plane z, around world (xw, yw)
function affineAt(xw, yw, z) { const p0 = px(xw, yw, z), p1 = px(xw + HM, yw, z), p2 = px(xw, yw + HM, z); const s = ((p1[0] - p0[0]) + (p0[1] - p2[1])) / 2; return { ox: p0[0] - (xw / HM) * s, oy: p0[1] + (yw / HM) * s, s }; }
const sway = (t, k) => 0.05 * Math.sin(t * 2.1 + k * 1.7) + 0.02 * Math.sin(t * 3.7 + k);

// paper lantern on a cord: c = centre (screen), w,h size (px), on 0..1+, ang sway
function paperLantern(g, cx, cy, w, h, on, ang = 0) {
  g.save(); g.translate(cx, cy); g.rotate(ang);
  g.fillStyle = rgba(mixc(PAL.paperOff, PAL.paperLit, clamp(on, 0, 1))); g.beginPath(); g.ellipse(0, 0, w / 2, h / 2, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = rgba(PAL.frame); g.fillRect(-w * 0.38, -h / 2 - Math.max(0.8, h * 0.08), w * 0.76, Math.max(1, h * 0.14)); g.fillRect(-w * 0.36, h / 2 - Math.max(0.6, h * 0.06), w * 0.72, Math.max(1, h * 0.12));
  g.restore();
}
function line(g, a, b, w, col) { g.strokeStyle = rgba(col); g.lineWidth = w; g.lineCap = 'round'; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }

await boot({
  fps: FPS, shots: SHOTS, toneMapping: THREE.NoToneMapping,
  fonts: [['Cormorant Garamond', 'italic 400'], ['Cormorant Garamond', 400], ['Cinzel', 500]],
  init: async (ctx) => {
    W = ctx.W; H = ctx.H; SC = H / 720;
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x0b0d1e);
    camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 30000);
    const prof = ctx.q.get('prof'); const t0 = performance.now();
    A = buildS1(TM); const t1 = performance.now(); B = buildS2(TM); const t2 = performance.now(); Cc = buildS3(TM); const t3 = performance.now();
    scene.add(A.setup.group, B.setup.group, Cc.setup.group);
    // pay the one-time costs here (not in frame 0): flush the recorded brushwork, upload every painted texture + mips
    let px = 0; const tr = performance.now(); for (const S of [A, B, Cc]) for (const p of S.setup.planes) { const tx = p.material.uniforms.map.value, c = tx.image; px += c.width * c.height; c.getContext('2d').getImageData(0, 0, 1, 1); ctx.renderer.initTexture(tx); }
    if (prof) console.log(`build S1 ${(t1 - t0).toFixed(0)}ms S2 ${(t2 - t1).toFixed(0)}ms S3 ${(t3 - t2).toFixed(0)}ms | raster+upload ${(performance.now() - tr).toFixed(0)}ms for ${(px / 1e6).toFixed(1)} Mpx, planes ${[A, B, Cc].map((s) => s.setup.planes.length)}, glows ${[A, B, Cc].map((s) => s.setup.glows.length)}`);
    post = makeComposer(ctx.renderer, scene, camera, {
      bloom: { strength: 0.5, radius: 0.42, threshold: 0.8 }, grade: 'painterly', overlayAfterFinish: true,
      finish: { saturation: 1.1, contrast: 1.04, shadowTint: [-0.008, 0.0, 0.035], highlightTint: [0.05, 0.022, -0.02], halation: 0.25, grain: 0.035, vignette: 0.35 },
    });
    detail = makeDetailPass(post, W, H);
    { const off = (ctx.q.get('off') || '').split(','); // profiling only: ?off=kuw,bloom,detail,finish,scene
      if (off.includes('kuw')) post.finish.mode.value = 0; if (off.includes('bloom') && post.bloom) post.bloom.enabled = false; if (off.includes('detail')) detail.pass.enabled = false;
      if (off.includes('finish')) for (const p of post.composer.passes) if (p.uniforms && p.uniforms.kuwaharaRadius) p.enabled = false;
      if (off.includes('scene')) window.__noScene = true; }
    // ---- gait plans (walk coordinate X in H units; world x = X * HM)
    const g1 = (X) => -(A.yWalk(640 + X * HM * A.setup.f / A.D.road) - 360) * A.D.road / A.setup.f / HM;
    plans.s1 = continuousPlan({ T, L: STEP, x0: (425 - 640) * A.D.road / A.setup.f / HM, v: V, phase0: TM.walk.phase0, t0: -3, t1: 5, ground: g1 });
    const g2 = (X) => -(B.yWalk(640 + X * HM * B.setup.f / B.D.road) - 360) * B.D.road / B.setup.f / HM;
    plans.s2 = continuousPlan({ T, L: STEP, x0: (360 - 640) * B.D.road / B.setup.f / HM - V * 4.6, v: V, phase0: TM.walk.phase0, t0: 2, t1: 9.2, ground: g2 });
    // S3 arrival: constant pace, brake from s3.brake to 9.62 (smoothstep velocity), small forward overshoot, X_stop = 0
    const tb = TM.s3.brake, ts = TM.s3.plantStop + 0.06, I = (u) => u - u ** 3 + u ** 4 / 2; // body comes to rest just after the closing step
    const rem = (t) => (t >= ts ? 0 : t <= tb ? V * (tb - t) + V * (ts - tb) * 0.5 : V * (ts - tb) * (I(1) - I((t - tb) / (ts - tb))));
    const body3 = (t) => -rem(t) + (t > ts - 0.1 ? 0.012 * Math.sin(Math.PI * clamp((t - ts + 0.1) / 0.45)) : 0); // upper body carries on a little, then settles back
    const c3 = []; for (let k = 8; k <= 15; k++) { const tc = TM.walk.phase0 + k * T; c3.push({ t: tc, foot: k % 2, x: body3(tc) + 0.5 * STEP }); }
    // braking step lands short; the closing foot comes alongside so the hip ends over both feet
    const xB = body3(TM.s3.plantBrake) + 0.085; c3.push({ t: TM.s3.plantBrake, foot: 0, x: xB }, { t: TM.s3.plantStop, foot: 1, x: xB - 0.034 });
    plans.s3 = makePlan({ T, L: STEP, body: body3, contacts: c3, ground: () => 0, stopT: TM.s3.plantStop, brake: tb, lookUp: TM.s3.lookUp, ignite: TM.s3.ignite });
    const FW = Cc.figCanvas.width, FH = Cc.figCanvas.height; // scratch canvases match the S3 figure card region
    figOnly = document.createElement('canvas'); figOnly.width = FW; figOnly.height = FH; figOnlyG = figOnly.getContext('2d', { willReadFrequently: true });
    rimC = document.createElement('canvas'); rimC.width = FW; rimC.height = FH; rimG = rimC.getContext('2d', { willReadFrequently: true });
    window.__p03 = { plans, TM };
  },
  render: async (ctx, i, t) => {
    const sh = ctx.timeline.at(t), n = sh.i; const tq = Math.floor(i / 2) * 2 / FPS; // characters on 2s, camera/light on 1s
    A.setup.group.visible = n === 0; B.setup.group.visible = n === 1; Cc.setup.group.visible = n === 2;
    detail.clear(); const g = detail.g; const { ctx: oc, clear } = post.overlay; clear();
    if (n === 0) {
      camera.fov = fovV(32); camera.updateProjectionMatrix(); A.camera(camera, t); camera.updateMatrixWorld();
      const z = -A.D.road, P = pose(plans.s1, tq, -2.0); const M = affineAt(P.bx * HM, plans.s1.ground(P.bx) * HM, z);
      // rope line: two posts, a sagging rope, three paper lanterns that ignite as he passes beneath
      const pl = plans.s1, X = TM.s1.ropeLanterns.map((tt) => pl.body(tt)), P0 = pl.body(TM.s1.posts[0]), P1 = pl.body(TM.s1.posts[1]);
      const S = (x, y) => [M.ox + x * M.s, M.oy - y * M.s]; const rope = (x) => { const u = (x - P0) / (P1 - P0); return pl.ground(x) + 1.86 - 0.2 * 4 * u * (1 - u); };
      for (const p of [P0, P1]) line(g, S(p, pl.ground(p) - 0.02), S(p, pl.ground(p) + 1.93), Math.max(1.6, 0.07 * M.s), hex('#17141f'));
      g.strokeStyle = rgba(hex('#1e1a27'), 0.95); g.lineWidth = Math.max(0.9, 0.014 * M.s); g.beginPath(); for (let k = 0; k <= 40; k++) { const x = lerp(P0, P1, k / 40); const q = S(x, rope(x)); k ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); } g.stroke();
      const ropeOn = [], ropeWorld = [];
      X.forEach((x, k) => { const on = igniteEnv(t, TM.s1.ropeLanterns[k], k + 1); const a = sway(t, k); const top = S(x, rope(x)); const len = 0.12 * M.s, hh = 0.27 * M.s, ww = 0.21 * M.s;
        const c = [top[0] + Math.sin(a) * (len + hh / 2), top[1] + Math.cos(a) * (len + hh / 2)]; line(g, top, [top[0] + Math.sin(a) * len, top[1] + Math.cos(a) * len], Math.max(0.7, 0.01 * M.s), hex('#1e1a27'));
        paperLantern(g, c[0], c[1], Math.max(2.6, ww), Math.max(3.4, hh), on, -a); ropeOn.push(on);
        const wx = (c[0] - M.ox) / M.s * HM, wy = (M.oy - c[1]) / M.s * HM; ropeWorld.push(new THREE.Vector3(wx, wy, z)); });
      // contact shadow + the traveler (fine brush)
      for (const f of P.feet) { const q = S((f.heel[0] + f.toe[0]) / 2, pl.ground(f.heel[0]) - 0.01); g.fillStyle = 'rgba(8,8,18,0.35)'; g.beginPath(); g.ellipse(q[0], q[1], 0.09 * M.s, Math.max(0.8, 0.02 * M.s), 0, 0, Math.PI * 2); g.fill(); }
      const d = drawTraveler(g, P, M, { tiny: true, lantern: 1 });
      if (ctx.q.get('feet')) { const ref = px(-20, -15, z); console.log('FEET ' + JSON.stringify({ i, s: 1, cam: +camera.position.x.toFixed(4), ref: ref.map((v) => +v.toFixed(2)), f: P.feet.map((f) => [f.heel[0], f.toe[0], f.heel[1], f.toe[1]].map((v, k) => +((k < 2 ? M.ox + v * M.s : M.oy - v * M.s)).toFixed(2))), body: +(M.ox + P.bx * M.s).toFixed(2) })); }
      A.update(t, { lanternWorld: new THREE.Vector3(d.lantern[0] * HM, d.lantern[1] * HM, z), ropeWorld, ropeOn });
    } else if (n === 1) {
      camera.fov = fovV(26); camera.updateProjectionMatrix(); B.camera(camera, t); camera.updateMatrixWorld();
      const z = -B.D.road, pl = plans.s2, P = pose(pl, tq, 2.6); const M = affineAt(P.bx * HM, pl.ground(P.bx) * HM, z);
      // road lantern posts R1..R3 (R1 is the one he passes) and the gate with its dark great lantern (set-up for S3)
      const rx = [pl.body(TM.s2.chain[0]) + 0.05, (560 - 640) * B.D.road / B.setup.f / HM, (760 - 640) * B.D.road / B.setup.f / HM];
      const roadPosts = rx.map((X, k) => { const Mk = affineAt(X * HM, pl.ground(X) * HM, z); const S = (x, y) => [Mk.ox + x * Mk.s, Mk.oy - y * Mk.s]; const gy = pl.ground(X) - 0.15;
        line(g, S(X, gy), S(X, gy + 1.3), Math.max(1.5, 0.07 * Mk.s), hex('#17141f')); const on = igniteEnv(t, TM.s2.chain[k], k + 1);
        const c = S(X, gy + 1.3 + 0.14); paperLantern(g, c[0], c[1], Math.max(2.4, 0.2 * Mk.s), Math.max(3, 0.26 * Mk.s), on, 0);
        return { world: new THREE.Vector3(X * HM, (gy + 1.44) * HM, z) }; });
      { const X = (880 - 640) * B.D.road / B.setup.f / HM; const gy = pl.ground(X) - 0.12; const Mk = affineAt(X * HM, gy * HM, z); const S = (x, y) => [Mk.ox + x * Mk.s, Mk.oy - y * Mk.s]; const col = hex('#1a1622');
        for (const dx of [-1.1, 1.1]) line(g, S(X + dx, gy), S(X + dx * 0.98, gy + 2.45), Math.max(1.8, 0.15 * Mk.s), col);
        line(g, S(X - 1.32, gy + 2.42), S(X + 1.32, gy + 2.42), Math.max(1.6, 0.12 * Mk.s), col);
        g.fillStyle = rgba(hex('#15131f')); const r0 = S(X - 1.55, gy + 2.5), r1 = S(X - 1.1, gy + 2.85), r2 = S(X + 1.1, gy + 2.85), r3 = S(X + 1.55, gy + 2.5); g.beginPath(); g.moveTo(...r0); g.lineTo(...r1); g.lineTo(...r2); g.lineTo(...r3); g.closePath(); g.fill();
        line(g, S(X, gy + 2.42), S(X, gy + 2.2), Math.max(0.7, 0.02 * Mk.s), col); const lc = S(X, gy + 1.98); paperLantern(g, lc[0], lc[1], Math.max(3, 0.32 * Mk.s), Math.max(4, 0.44 * Mk.s), 0, 0); }
      for (const f of P.feet) { const q = [M.ox + (f.heel[0] + f.toe[0]) / 2 * M.s, M.oy - (pl.ground(f.heel[0]) - 0.01) * M.s]; g.fillStyle = 'rgba(8,8,18,0.35)'; g.beginPath(); g.ellipse(q[0], q[1], 0.09 * M.s, Math.max(0.8, 0.02 * M.s), 0, 0, Math.PI * 2); g.fill(); }
      const d = drawTraveler(g, P, M, { tiny: true, lantern: 1 });
      B.update(t, { lanternWorld: new THREE.Vector3(d.lantern[0] * HM, d.lantern[1] * HM, z), roadPosts });
    } else {
      camera.fov = fovV(35); camera.updateProjectionMatrix(); Cc.camera(camera); camera.updateMatrixWorld();
      const P = pose(plans.s3, tq, 7.0); const M = { ox: 600, oy: Cc.groundY, s: 262.5 }; const ign = igniteEnv(t, TM.s3.ignite, 5, 1.55, 0.06);
      // everything for the figure happens in a local card region FIG (design px) — small canvases keep per-frame 2D work cheap
      const [X0, Y0] = Cc.FIG, CW = Cc.figCanvas.width, CH = Cc.figCanvas.height; const fg = Cc.figG; const ID = () => fg.setTransform(1, 0, 0, 1, 0, 0); const DS = () => fg.setTransform(1, 0, 0, 1, -X0, -Y0);
      ID(); fg.clearRect(0, 0, CW, CH);
      // body alone first (for shadows + rims); the staff is painted separately behind it so it never gets a rim band
      figOnlyG.setTransform(1, 0, 0, 1, 0, 0); figOnlyG.clearRect(0, 0, CW, CH); figOnlyG.setTransform(1, 0, 0, 1, -X0, -Y0); const d = drawTraveler(figOnlyG, P, M, { tiny: false, lantern: 1, parts: 'body' });
      const fx = M.ox + P.bx * M.s, fy = M.oy, fxL = fx - X0, fyL = fy - Y0;
      // contact shadows (always) + the long shadow thrown by the great lantern (after ignition), cast down-left away from it
      DS(); fg.save(); fg.filter = 'blur(6px)'; fg.fillStyle = 'rgba(6,6,16,0.55)'; fg.beginPath(); fg.ellipse(fx, fy + 2, 0.24 * M.s, 0.035 * M.s, 0, 0, Math.PI * 2); fg.fill(); fg.restore();
      for (const f of P.feet) { const q = [M.ox + (f.heel[0] + f.toe[0]) / 2 * M.s, M.oy + 1]; fg.save(); fg.filter = 'blur(3px)'; fg.fillStyle = 'rgba(4,4,12,0.6)'; fg.beginPath(); fg.ellipse(q[0], q[1], 0.08 * M.s, 0.016 * M.s, 0, 0, Math.PI * 2); fg.fill(); fg.restore(); }
      if (ign > 0) { rimG.setTransform(1, 0, 0, 1, 0, 0); rimG.globalCompositeOperation = 'source-over'; rimG.clearRect(0, 0, CW, CH);
        rimG.setTransform(0.9, 0.05, 0.85, -0.2, fxL - (0.9 * fxL + 0.85 * fyL), fyL - (0.05 * fxL - 0.2 * fyL)); rimG.drawImage(figOnly, 0, 0); rimG.setTransform(1, 0, 0, 1, 0, 0);
        rimG.globalCompositeOperation = 'source-in'; rimG.fillStyle = '#05050c'; rimG.fillRect(0, 0, CW, CH); rimG.globalCompositeOperation = 'source-over';
        ID(); fg.save(); fg.globalAlpha = 0.55 * clamp(ign, 0, 1); fg.filter = 'blur(6px)'; fg.drawImage(rimC, 0, 0); fg.restore(); }
      DS(); const st = drawTraveler(fg, P, M, { parts: 'staff' }); ID(); fg.drawImage(figOnly, 0, 0);
      // rims (body only): cool sky edge (upper left) always; warm edge facing the great lantern once lit; a soft warm wash on that side
      const rim = (dx, dy, w, col, a) => { rimG.setTransform(1, 0, 0, 1, 0, 0); rimG.globalCompositeOperation = 'source-over'; rimG.clearRect(0, 0, CW, CH); rimG.drawImage(figOnly, 0, 0);
        rimG.globalCompositeOperation = 'source-in'; rimG.fillStyle = rgba(col); rimG.fillRect(0, 0, CW, CH); rimG.globalCompositeOperation = 'destination-out'; rimG.drawImage(figOnly, -dx * w, -dy * w);
        ID(); fg.save(); fg.globalCompositeOperation = 'source-atop'; fg.globalAlpha = a; fg.filter = 'blur(1.5px)'; fg.drawImage(rimC, 0, 0); fg.restore(); };
      rim(-0.55, -0.83, 5, PAL.rimCool, 0.4);
      if (ign > 0) { const lx = Cc.LAN.x, ly = (Cc.LAN.y0 + Cc.LAN.y1) / 2; const hx = fx + 0.03 * M.s, hy = fy - 0.9 * M.s; const dl = Math.hypot(lx - hx, ly - hy); const k = clamp(ign, 0, 1.2);
        rim((lx - hx) / dl, (ly - hy) / dl, 6, PAL.rimWarm, 0.6 * k);
        DS(); fg.save(); fg.globalCompositeOperation = 'source-atop'; const rg = fg.createRadialGradient(lx, ly, 60, lx, ly, 470); rg.addColorStop(0, rgba([255, 165, 85], 0.24 * clamp(ign, 0, 1))); rg.addColorStop(1, rgba([255, 150, 80], 0)); fg.fillStyle = rg; fg.fillRect(X0, Y0, CW, CH); fg.restore();
        // a thin warm highlight down the lantern side of the staff
        const [a0, a1] = st.staff; fg.save(); fg.globalAlpha = 0.5 * clamp(ign, 0, 1); fg.strokeStyle = rgba(PAL.rimWarm); fg.lineWidth = 2.2; fg.beginPath(); fg.moveTo(a0[0] + 3, a0[1]); fg.lineTo(a1[0] + 3, a1[1]); fg.stroke(); fg.restore(); }
      ID();
      if (ctx.q.get('feet')) console.log('FEET ' + JSON.stringify({ i, s: 3, f: P.feet.map((f) => [f.heel[0], f.toe[0], f.heel[1], f.toe[1]].map((v, k) => +((k < 2 ? M.ox + v * M.s : M.oy - v * M.s)).toFixed(2))), body: +(M.ox + P.bx * M.s).toFixed(2), hip: +(M.oy - P.hipY * M.s).toFixed(2), head: +P.head.toFixed(3), phi: +P.phi.toFixed(3), hem: +P.hem.toFixed(3) }));
      Cc.update(t, { lanternPx: [M.ox + d.lantern[0] * M.s, M.oy - d.lantern[1] * M.s], ign });
    }
    // ---- narration captions (lower third) and the small title (bottom-left, S3)
    for (const c of TM.captions) { const a = smoothstep(c.in, c.in + 0.45, t) * (1 - smoothstep(c.out - 0.45, c.out, t)); if (a > 0.002) drawText(oc, c.text, { x: W / 2, y: 616 * SC, font: `italic 400 ${Math.round(35 * SC)}px "Cormorant Garamond"`, color: '#efe6d3', alpha: a, spacing: 0.6 * SC, shadow: 14 * SC, shadowColor: 'rgba(3,3,12,0.92)' }); }
    if (t >= TM.s3.title) { const a = ease.outCubic(clamp((t - TM.s3.title) / 0.7)); drawText(oc, 'THE LANTERN ROAD', { x: 64 * SC, y: 666 * SC, align: 'left', font: `500 ${Math.round(23 * SC)}px "Cinzel"`, color: '#e8dcc3', alpha: a, spacing: 6 * SC, shadow: 10 * SC, shadowColor: 'rgba(3,3,12,0.85)' }); }
    post.finish.fade.value = ease.inOutSine(clamp(t / 0.25)); // 6-frame soft open from black
    detail.pass.uniforms.useDetail.value = n < 2 ? 1 : 0; detail.sync(t);
    post.render(t);
  },
});
