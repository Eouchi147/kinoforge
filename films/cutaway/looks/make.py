#!/usr/bin/env python3
"""Make (or refresh) a look-board film folder: the Cutaway line's example (films/cutaway/meadow) with an art direction.

    python3 films/cutaway/looks/make.py <art-name> [<art-name> ...]     # 'reference' = no art direction

Each folder films/cutaway/looks/<name>/ holds the meadow's spec.json with "look": {"art": <name>}, its cues.json, a
film.json (id style-cutaway-art-<name>) and the line's generic blender.py, so rc-render stills.yml renders it like any
other film. The art module itself lives in films/styles/cutaway/art/<name>.py.
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, 'films', 'cutaway', 'meadow')


def make(name):
    d = os.path.join(HERE, name); os.makedirs(d, exist_ok=True)
    spec = json.load(open(os.path.join(SRC, 'spec.json')))
    if name != 'reference':
        spec['look'] = dict(spec.get('look') or {}, art=name)
    json.dump(spec, open(os.path.join(d, 'spec.json'), 'w'), indent=1)
    shutil.copy(os.path.join(SRC, 'cues.json'), os.path.join(d, 'cues.json'))
    shutil.copy(os.path.join(ROOT, 'films', 'lib', 'cutaway', 'blender.py'), os.path.join(d, 'blender.py'))
    meta = json.load(open(os.path.join(SRC, 'film.json')))
    meta.update(id=f'style-cutaway-art-{name}', title=f'Cutaway look board: {name}', note=f'Look board frame of the meadow example with art direction {name} (films/styles/cutaway/art/{name}.py).')
    meta.pop('audio', None)
    json.dump(meta, open(os.path.join(d, 'film.json'), 'w'), indent=1)
    print('made', d)


if __name__ == '__main__':
    for n in sys.argv[1:] or ['reference']: make(n)
