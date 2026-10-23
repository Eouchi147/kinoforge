#!/usr/bin/env python3
"""Make (or refresh) look-board folders for the seasons loop with an art direction.

    python3 films/cutaway/looks/make_seasons.py <art-name> [<art-name> ...]

Each folder films/cutaway/looks/seasons-<name>/ holds a tiny blender.py that names the art direction (KF_ART_NAME, a
module global, so nothing leaks into the environment of a render process that runs several films) and then runs the
seasons loop's own blender.py (films/cutaway/loops/seasons/), plus a film.json copied from the seasons film (no audio).
harness/blender_render.py and rc-render render it like any film folder. The art module lives in
films/styles/cutaway/art/<name>.py and reaches the kit scene through films/styles/cutaway/art/_adapter.py.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, 'films', 'cutaway', 'loops', 'seasons')

BLENDER = '''"""Look board: the seasons loop (films/cutaway/loops/seasons) dressed with the art direction `{name}`
(films/styles/cutaway/art/{name}.py, through art/_adapter.py). Made by films/cutaway/looks/make_seasons.py; do not edit.
Runs the seasons loop's own blender.py in this module, so DURATION, SETTINGS, build and frame are the loop's."""
import os

KF_ART_NAME = '{name}'
_SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'loops', 'seasons', 'blender.py'))
__file__ = _SRC
exec(compile(open(_SRC).read(), _SRC, 'exec'))
'''


def make(name):
    d = os.path.join(HERE, 'seasons-' + name); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'blender.py'), 'w').write(BLENDER.format(name=name))
    meta = json.load(open(os.path.join(SRC, 'film.json')))
    meta.update(id=f'cutaway-loop-seasons-art-{name}', title=f'Seasons loop look board: {name}',
                note=f'Look board of the seasons loop (films/cutaway/loops/seasons) with art direction {name} (films/styles/cutaway/art/{name}.py). Board frames: 40 (spring), 100 (summer), 230 (winter).')
    meta.pop('audio', None)
    json.dump(meta, open(os.path.join(d, 'film.json'), 'w'), indent=1)
    print('made', d)


if __name__ == '__main__':
    for n in sys.argv[1:]: make(n)
