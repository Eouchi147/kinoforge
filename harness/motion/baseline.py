"""baseline.py — learn the human motion baseline from licence-safe mocap (100STYLE, CMU, Cologne, own captures).

    python3 harness/motion/baseline.py DATA_DIR OUT_DIR [--source 100STYLE] [--limit N]

For every clip: locomotion (speed, stride length, cadence, double support), joint angular speeds, pelvis sway and bob,
centre of mass against the support feet, and foot-skate during contacts. Aggregated per gait and per style into
baseline.json, which the plausibility checker (check.py) uses to flag motion a human body could not do.
"""
import sys, os, re, json, glob, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bvh import load

UP = 1
GAITS = {'FW': 'forward walk', 'BW': 'backward walk', 'FR': 'forward run', 'BR': 'backward run', 'SW': 'sidestep walk', 'SR': 'sidestep run', 'ID': 'idle',
         'TR1': 'transitions 1', 'TR2': 'transitions 2', 'TR3': 'transitions 3'}
# rough segment mass shares (de Leva 1996, rounded) matched on joint names
MASS = [(('head',), 0.081), (('neck',), 0.02), (('spine', 'chest', 'abdomen'), 0.43), (('hips', 'pelvis'), 0.14), (('upleg', 'thigh', 'hip'), 0.1),
        (('leg', 'knee', 'shin', 'calf'), 0.047), (('foot', 'ankle'), 0.014), (('arm', 'shoulder'), 0.027), (('forearm', 'elbow'), 0.016), (('hand', 'wrist'), 0.006)]

def side_of(n):
    l = n.lower()
    if 'left' in l or re.match(r'^(l_|l[A-Z]|left)', n) or l.startswith('l'): return 'L'
    if 'right' in l or re.match(r'^(r_|r[A-Z]|right)', n) or l.startswith('r'): return 'R'
    return ''

def feet(c):
    """Per side: the ankle/foot joint and (if any) the toe joint."""
    out = {}
    for s in 'LR':
        cand = [j for j, n in enumerate(c.names) if side_of(n) == s and any(k in n.lower() for k in ('ankle', 'foot', 'toe')) and not n.endswith('_end')]
        if not cand:
            cand = [j for j, n in enumerate(c.names) if side_of(n) == s]
            cand = sorted(cand, key=lambda j: c.pos[:, j, UP].mean())[:2]
        cand = sorted(cand, key=lambda j: -c.pos[:, j, UP].mean())    # ankle first (higher), then toe
        out[s] = cand[:2]
    return out

def weights(c):
    w = np.zeros(len(c.names))
    for j, n in enumerate(c.names):
        if n.endswith('_end'): continue
        l = n.lower()
        for keys, m in MASS:
            if any(k in l for k in keys): w[j] = m; break
        else: w[j] = 0.01
    return w / w.sum()

def smooth(x, k=5):
    if len(x) < k: return x
    ker = np.ones(k) / k; pad = np.pad(x, [(k // 2, k // 2)] + [(0, 0)] * (x.ndim - 1), mode='edge')
    return np.apply_along_axis(lambda v: np.convolve(v, ker, mode='valid'), 0, pad)

def runs(b, k):
    """Remove on/off flickers shorter than k frames (contacts are held, not toggled)."""
    b = b.copy(); i = 0
    while i < len(b):
        j = i
        while j < len(b) and b[j] == b[i]: j += 1
        if j - i < k and i > 0: b[i:j] = b[i - 1]
        i = j
    return b

def analyse(c):
    F, fps = len(c.pos), c.fps; dt = 1 / fps
    root = c.pos[:, 0]; hv = smooth(np.gradient(root[:, [0, 2]], dt, axis=0), 9); speed = np.linalg.norm(hv, axis=1)
    ft = feet(c); contact = {}; fpos = {}
    for s, js in ft.items():
        j = js[0]; p = c.pos[:, j]; h = p[:, UP]; v = np.linalg.norm(smooth(np.gradient(p, dt, axis=0), 5), axis=1)
        h0 = np.percentile(h, 5); contact[s] = runs((h < h0 + 0.05) & (v < 0.35), max(2, int(0.05 * fps))); fpos[s] = p
    both = contact['L'] & contact['R']; anyc = contact['L'] | contact['R']
    # steps = contact onsets
    steps = []
    for s in 'LR':
        on = np.where(np.diff(contact[s].astype(int)) == 1)[0] + 1
        steps += [(i, s) for i in on]
    steps.sort()
    stride = []
    for s in 'LR':
        on = [i for i, ss in steps if ss == s]
        for a, b in zip(on, on[1:]): stride.append(np.linalg.norm(fpos[s][b, [0, 2]] - fpos[s][a, [0, 2]]))
    dur = F * dt; cadence = 60 * len(steps) / dur if dur > 0 else 0
    # skate: horizontal foot speed while in contact
    skate = np.concatenate([np.linalg.norm(np.gradient(fpos[s][:, [0, 2]], dt, axis=0), axis=1)[contact[s]] for s in 'LR']) if anyc.any() else np.zeros(1)
    # joint angular speed from local rotations
    R = c.rot; rel = np.einsum('fjik,fjil->fjkl', R[:-1], R[1:])
    ang = np.arccos(np.clip((np.trace(rel, axis1=2, axis2=3) - 1) / 2, -1, 1)) * fps      # rad/s, (F-1, J)
    # pelvis sway (perpendicular to travel) and bob
    head = hv / (np.linalg.norm(hv, axis=1, keepdims=True) + 1e-6); perp = np.stack([-head[:, 1], head[:, 0]], 1)
    lat = np.einsum('fi,fi->f', root[:, [0, 2]] - smooth(root[:, [0, 2]], int(fps) | 1), perp)
    bob = root[:, UP] - smooth(root[:, UP:UP + 1], int(fps) | 1)[:, 0]
    # centre of mass against the support
    w = weights(c); com = np.einsum('j,fji->fi', w, c.pos)[:, [0, 2]]
    dist = np.full(F, np.nan)
    for f in range(F):
        pts = [fpos[s][f, [0, 2]] for s in 'LR' if contact[s][f]]
        if not pts: continue
        if len(pts) == 1: dist[f] = np.linalg.norm(com[f] - pts[0])
        else:
            a, b = pts; ab = b - a; t = np.clip(np.dot(com[f] - a, ab) / (np.dot(ab, ab) + 1e-9), 0, 1); dist[f] = np.linalg.norm(com[f] - (a + t * ab))
    d = dist[~np.isnan(dist)]
    out_frac = float((d > 0.25).mean()) if len(d) else None
    return {'frames': F, 'fps': round(fps, 2), 'speed_mean': float(speed.mean()), 'speed_p95': float(np.percentile(speed, 95)),
            'cadence_spm': float(cadence), 'stride_m': float(np.median(stride)) if stride else None, 'double_support': float(both.mean()),
            'flight': float((~anyc).mean()), 'skate_p50': float(np.median(skate)), 'skate_p95': float(np.percentile(skate, 95)),
            'sway_m': float(np.std(lat)), 'bob_m': float(np.std(bob)), 'com_support_p95_m': float(np.percentile(d, 95)) if len(d) else None,
            'com_outside_frac': out_frac,
            'joint_speed': {c.names[j]: [float(np.percentile(ang[:, j], 50)), float(np.percentile(ang[:, j], 95)), float(np.percentile(ang[:, j], 99.5))]
                            for j in range(len(c.names)) if not c.names[j].endswith('_end')}}

def main():
    data, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    source = sys.argv[sys.argv.index('--source') + 1] if '--source' in sys.argv else os.path.basename(data.rstrip('/'))
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 0
    files = sorted(glob.glob(os.path.join(data, '**', '*.bvh'), recursive=True))
    if limit: files = files[:limit]
    rows = []; t0 = time.time()
    for k, f in enumerate(files):
        base = os.path.splitext(os.path.basename(f))[0]
        m = re.match(r'(.+?)_(FW|BW|FR|BR|SW|SR|ID|TR1|TR2|TR3)$', base)
        style, gait = (m.group(1), m.group(2)) if m else (os.path.basename(os.path.dirname(f)), 'other')
        try:
            c = load(f); r = analyse(c); r.update({'file': os.path.relpath(f, data), 'style': style, 'gait': gait}); rows.append(r)
        except Exception as e:
            print('skip', f, e, flush=True); continue
        if k % 50 == 0: print(f'{k}/{len(files)} {time.time() - t0:.0f}s {base}', flush=True)
    json.dump(rows, open(os.path.join(out, 'clips.json'), 'w'))
    def agg(sel):
        keys = ['speed_mean', 'cadence_spm', 'stride_m', 'double_support', 'flight', 'skate_p95', 'sway_m', 'bob_m', 'com_support_p95_m', 'com_outside_frac']
        res = {'clips': len(sel)}
        for kk in keys:
            v = [r[kk] for r in sel if r.get(kk) is not None]
            if v: res[kk] = [round(float(np.percentile(v, p)), 4) for p in (10, 50, 90)]
        return res
    base = {'source': source, 'clips': len(rows), 'note': 'values are [p10, p50, p90] across clips; metres, seconds, radians',
            'per_gait': {GAITS.get(g, g): agg([r for r in rows if r['gait'] == g]) for g in sorted(set(r['gait'] for r in rows))},
            'per_style': {s: agg([r for r in rows if r['style'] == s]) for s in sorted(set(r['style'] for r in rows))}}
    # human limits per joint: the 99.5th percentile of angular speed across all clips
    js = {}
    for r in rows:
        for n, v in r['joint_speed'].items(): js.setdefault(n, []).append(v[2])
    base['joint_speed_limit_rad_s'] = {n: round(float(np.percentile(v, 99)), 2) for n, v in js.items()}
    # stride length and cadence against speed (walks and runs)
    for g in ('FW', 'FR'):
        sel = [r for r in rows if r['gait'] == g and r['stride_m'] and r['speed_mean'] > 0.2]
        if len(sel) > 5:
            sp = np.array([r['speed_mean'] for r in sel]); st = np.array([r['stride_m'] for r in sel]); ca = np.array([r['cadence_spm'] for r in sel])
            base.setdefault('fits', {})[GAITS[g]] = {'stride_m = a*speed + b': [round(float(x), 4) for x in np.polyfit(sp, st, 1)],
                                                    'cadence_spm = a*speed + b': [round(float(x), 4) for x in np.polyfit(sp, ca, 1)], 'n': len(sel)}
    json.dump(base, open(os.path.join(out, 'baseline.json'), 'w'), indent=1)
    print('wrote', os.path.join(out, 'baseline.json'), len(rows), 'clips', f'{time.time() - t0:.0f}s')

if __name__ == '__main__':
    main()
