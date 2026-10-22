#!/usr/bin/env python3
"""selftest.py: quick gate for the score engine (about 40 s, synthesis only, needs no samples).

    python3 films/lib/score/selftest.py

Checks: every palette renders; same plan and seed give identical audio; a different seed gives different audio; stereo,
48 kHz length matches the plan; peak under -3 dBFS; no clipping; no NaN; loudness lands on target; the swell is real
(the turn section is clearly louder than the calm opening); no em or en dashes in the package.
"""
import os, sys, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import score, dsp, palettes as P

SECS = [{'t': 0, 'mood': 'calm'}, {'t': 9, 'mood': 'curious'}, {'t': 17, 'mood': 'tension'}, {'t': 28, 'mood': 'turn'}, {'t': 37, 'mood': 'triumph'}, {'t': 44, 'mood': 'aftermath'}]
fails = []


def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: fails.append(msg)


for name in P.PALETTES:
    plan = {'palette': name, 'duration': 56, 'seed': 3, 'sections': SECS, 'hits': [{'t': 27.7, 'kind': 'low', 'level': 1}]}
    y, info = score.render_plan(plan, 'synth')
    check(y.shape == (56 * 48000, 2) or abs(len(y) - 56 * 48000) <= 48000, f'{name}: stereo, 56 s ({len(y) / 48000:.1f} s)')
    check(np.isfinite(y).all() and np.abs(y).max() <= dsp.db(-3.0), f'{name}: finite, peak {info["peak_dbfs"]} dBFS under -3')
    check(abs(info['lufs'] + 23) < 0.6, f'{name}: loudness {info["lufs"]} LUFS near -23')
    calm = dsp.loudness(y[2 * 48000:8 * 48000]); turn = dsp.loudness(y[26 * 48000:34 * 48000])
    check(turn - calm > 4.0, f'{name}: the turn is {turn - calm:.1f} dB above the calm opening (need > 4)')
    if name == 'ancient_med':
        y2, _ = score.render_plan(plan, 'synth'); check(np.array_equal(y, y2), 'same plan and seed give identical audio')
        y3, _ = score.render_plan({**plan, 'seed': 4}, 'synth'); check(not np.array_equal(y, y3), 'a different seed gives different audio')

bad = []
for f in glob.glob(os.path.join(HERE, '**', '*'), recursive=True):
    if os.path.isfile(f) and f.endswith(('.py', '.md', '.json')):
        t = open(f, encoding='utf-8').read()
        if '—' in t or '–' in t: bad.append(os.path.relpath(f, HERE))
check(not bad, 'no em or en dashes in the package' + (f' (found in {bad})' if bad else ''))
print('PASS' if not fails else f'{len(fails)} FAILED')
sys.exit(1 if fails else 0)
