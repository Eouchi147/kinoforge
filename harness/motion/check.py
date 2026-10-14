"""check.py — the motion plausibility checker (rule §0 applied to movement).

    python3 harness/motion/check.py MOTION.bvh BASELINE.json [--profile realistic|clay|cel|paper|...]

Flags, with times: feet sliding while planted, joints turning faster than a human can, the body hanging outside its
support for too long, gliding (the body travels while both feet stay planted), and steps that don't match the speed.
Stylised profiles relax what their style allows (a cel smear may break joint-speed limits on purpose; paper theatre has
no feet to plant), so the same checker serves every style.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bvh import load
from baseline import analyse, feet, weights, smooth, runs, UP

PROFILES = {   # multipliers on the human limits, per style (see the blueprint's style-motion table)
    'realistic': dict(skate=1.0, joint=1.0, support=1.0), 'witness': dict(skate=1.0, joint=1.0, support=1.0),
    'clay': dict(skate=1.5, joint=1.5, support=1.2), 'lantern': dict(skate=1.5, joint=1.3, support=1.2),
    'cel': dict(skate=2.0, joint=3.0, support=1.5), 'pixel': dict(skate=2.0, joint=3.0, support=1.5),
    'paper': None, 'kinetic': None, 'terrain': None}

def main():
    c = load(sys.argv[1]); base = json.load(open(sys.argv[2]))
    prof = sys.argv[sys.argv.index('--profile') + 1] if '--profile' in sys.argv else 'realistic'
    k = PROFILES.get(prof, PROFILES['realistic'])
    if k is None: print(json.dumps({'profile': prof, 'findings': [], 'note': 'no ground contact in this style: hinge and timing rules apply instead'})); return
    fps = c.fps; dt = 1 / fps; F = len(c.pos); findings = []
    lim = base.get('joint_speed_limit_rad_s', {})
    R = c.rot; rel = np.einsum('fjik,fjil->fjkl', R[:-1], R[1:]); ang = np.arccos(np.clip((np.trace(rel, axis1=2, axis2=3) - 1) / 2, -1, 1)) * fps
    for j, n in enumerate(c.names):
        if n in lim and lim[n] > 0:
            bad = np.where(ang[:, j] > lim[n] * 1.25 * k['joint'])[0]
            if len(bad): findings.append({'kind': 'joint too fast', 'joint': n, 'at_s': round(bad[0] * dt, 2), 'frames': int(len(bad)), 'peak_rad_s': round(float(ang[bad, j].max()), 1), 'limit': lim[n]})
    walk = base['per_gait'].get('forward walk', {})
    skate_lim = (walk.get('skate_p95', [0, 0.15, 0.3])[2]) * 1.5 * k['skate']
    ft = feet(c)
    for s, js in ft.items():
        p = c.pos[:, js[0]]; h = p[:, UP]; v = np.linalg.norm(smooth(np.gradient(p, dt, axis=0), 5), axis=1); hv = np.linalg.norm(np.gradient(p[:, [0, 2]], dt, axis=0), axis=1)
        cont = runs((h < np.percentile(h, 5) + 0.05) & (v < 0.6), max(2, int(0.05 * fps)))
        bad = np.where(cont & (hv > max(0.12, skate_lim)))[0]
        if len(bad) > fps * 0.1: findings.append({'kind': 'foot sliding while planted', 'foot': s, 'at_s': round(bad[0] * dt, 2), 'seconds': round(len(bad) * dt, 2)})
    a = analyse(c)
    sup_lim = (walk.get('com_support_p95_m', [0, 0.2, 0.3])[2]) * 1.3 * k['support']
    if a['com_support_p95_m'] and a['com_support_p95_m'] > sup_lim:
        findings.append({'kind': 'body outside its support', 'p95_m': round(a['com_support_p95_m'], 3), 'limit_m': round(sup_lim, 3)})
    fit = base.get('fits', {}).get('forward walk')
    if fit and a['stride_m'] and a['speed_mean'] > 0.3:
        exp = fit['stride_m = a*speed + b'][0] * a['speed_mean'] + fit['stride_m = a*speed + b'][1]
        if abs(a['stride_m'] - exp) / exp > 0.35: findings.append({'kind': 'steps do not match the speed', 'stride_m': round(a['stride_m'], 2), 'expected_m': round(exp, 2)})
    print(json.dumps({'profile': prof, 'findings': findings, 'summary': {kk: a[kk] for kk in ('speed_mean', 'cadence_spm', 'stride_m', 'skate_p95', 'com_support_p95_m')}}, indent=1))

if __name__ == '__main__':
    main()
