#!/usr/bin/env python3
"""Self-test of the Cutaway line (no Blender, about 15 s): the example spec passes the validator, and broken specs fail
with the error a coder seat needs to fix them.

    python3 films/lib/cutaway/tools/selftest.py
"""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
from validate import validate  # noqa: E402

EX = os.path.join(ROOT, 'films', 'cutaway', 'meadow')


def run(spec, cues=None):
    d = tempfile.mkdtemp(prefix='cl-')
    try:
        json.dump(spec, open(os.path.join(d, 'spec.json'), 'w')); shutil.copy(os.path.join(EX, 'film.json'), d)
        json.dump(cues or json.load(open(os.path.join(EX, 'cues.json'))), open(os.path.join(d, 'cues.json'), 'w'))
        return validate(d)
    finally: shutil.rmtree(d, ignore_errors=True)


def main():
    base = json.load(open(os.path.join(EX, 'spec.json'))); fails = []
    rep = validate(EX)
    if not rep['ok']: fails.append(f'the example fails: {rep["hard"][:3]}')
    if rep['cost']['usd'] != 0: fails.append('the example costs money')

    def expect(name, mutate, needle):
        s = copy.deepcopy(base); mutate(s); r = run(s)
        hit = any(needle in h for h in r['hard'])
        if r['ok'] or not hit: fails.append(f'{name}: expected a hard error with "{needle}", got ok={r["ok"]} {r["hard"][:3]}')
        else: print(f'ok  {name}')

    expect('wrong cue word', lambda s: s['scenes'][1]['shots'][0].update(until='l02.dragon'), 'is not in l02')
    expect('no why', lambda s: s['scenes'][0]['shots'][0].pop('why'), 'needs "why"')
    expect('camera too fast', lambda s: s['scenes'][2]['shots'][0].update(**{'from': 0.3, 'to': 1.45, 'until': 'l03.years'}), 'faster than a real camera')
    expect('eggs overlap', lambda s: s['sets']['meadow']['eggs'].append({'kind': 'geode', 'face': '-Y', 'u': -0.9, 'depth': 0.95}), 'overlap')
    expect('two of a kind', lambda s: s['sets']['meadow']['eggs'].append({'kind': 'chest', 'face': '+X', 'u': 1.4}), 'one of each')
    expect('unknown egg', lambda s: s['sets']['meadow']['eggs'].append({'kind': 'dragon'}), 'is not one of')
    expect('macro without egg', lambda s: s['scenes'][2]['shots'][1].update(target='unicorn'), 'macro needs')
    expect('labels collide', lambda s: s['scenes'][1]['shots'][0]['labels'][1].update(slot='upper-left', at='l02.mole'), 'same place')
    expect('dash on screen', lambda s: s['scenes'][1]['shots'][0]['labels'][0].update(text='MOLE — TUNNEL'), 'dashes')
    expect('shots out of order', lambda s: s['scenes'][0]['shots'][1].update(until='l00.secret'), 'is not after the shot start')
    expect('ducks without water', lambda s: s['sets']['meadow'].update(water='none', props={'village': 3}), 'need water')
    expect('low label in a ground shot', lambda s: s['scenes'][0]['shots'][1].update(labels=[{'text': 'GRASS', 'at': 'l01>', 'slot': 'lower-left'}]), 'sits low')
    expect('too costly', lambda s: (s['look'].update(samples=400), s['sets']['meadow'].update(fog=1.0)), 'job limit')
    if fails:
        print('\n'.join('FAIL ' + f for f in fails)); sys.exit(1)
    print(f'selftest: all passed (example: {rep["cost"]["frames"]} frames, {rep["cost"]["runner_hours"]} runner-hours, US$0)')


if __name__ == '__main__':
    main()
