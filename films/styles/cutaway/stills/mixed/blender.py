"""One stills run that mixes looks and aspects: frame -> (look, width, height). Frames 24 A 9:16, 25 B 16:9, 27 D 9:16
(26 C 16:9). The harness --w/--h are overridden per frame."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scene import make  # noqa: E402
PLAN = {0: ('A', (1080, 1920)), 1: ('B', (1920, 1080)), 2: ('C', (1920, 1080)), 3: ('D', (1080, 1920))}

def _start():
    a = sys.argv
    return int(a[a.index('--start') + 1]) if '--start' in a else 0

_look, _size = PLAN[_start() % 4]
DURATION, SETTINGS, build, frame = make(_look, duration=8.0, move='none', samples=128, size=_size)
